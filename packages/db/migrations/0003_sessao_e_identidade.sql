-- F0-c: sessão no servidor, vínculo de identidade e login em duas etapas (ADR 0004 rev. 2, §3 e §5).
-- Aplicada pelo migrator. O app_runtime não tem privilégio algum nas quatro tabelas daqui: tudo passa por funções
-- SECURITY DEFINER do papel app_sessao (NOLOGIN, criado no provisionamento, sem atributo privilegiado), com search_path
-- fixo e EXECUTE só para o app_runtime. Tokens nunca chegam ao banco: a aplicação gera 256 bits aleatórios, põe o token
-- no cookie e envia só o SHA-256 (32 bytes). Validades: transação de login e continuação até 10 min; sessão até 12 h.

-- Ser dono de função no esquema exige CREATE nele; o app_sessao não faz login, só o migrator assume esse papel.
GRANT USAGE, CREATE ON SCHEMA app TO app_sessao;

-- Vínculo explícito entre a identidade externa (issuer + subject) e o usuário de uma organização. O e-mail nunca vincula.
CREATE TABLE app.identity_link (
  issuer text NOT NULL CHECK (length(issuer) BETWEEN 1 AND 255),
  subject text NOT NULL CHECK (length(subject) BETWEEN 1 AND 255),
  organization_id uuid NOT NULL,
  user_id uuid NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (issuer, subject, organization_id),
  FOREIGN KEY (organization_id, user_id) REFERENCES app.app_user (organization_id, id)
);

CREATE TABLE app.session (
  token_hash bytea PRIMARY KEY CHECK (octet_length(token_hash) = 32),
  organization_id uuid NOT NULL,
  user_id uuid NOT NULL,
  role_code text NOT NULL REFERENCES app.role (code),
  issuer text NOT NULL,
  subject text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
  expires_at timestamptz NOT NULL,
  revoked_at timestamptz,
  -- Troca de papel: a sessão nova aponta a que ela substituiu, que fica revogada.
  origin_token_hash bytea REFERENCES app.session (token_hash),
  FOREIGN KEY (organization_id, user_id) REFERENCES app.app_user (organization_id, id),
  CHECK (expires_at > created_at)
);

-- Antes do callback: o que o adaptador OIDC guarda (state, nonce, verificador PKCE da RFC 7636) e o destino interno.
CREATE TABLE app.login_transaction (
  ticket_hash bytea PRIMARY KEY CHECK (octet_length(ticket_hash) = 32),
  state text NOT NULL CHECK (length(state) BETWEEN 16 AND 512),
  nonce text NOT NULL CHECK (length(nonce) BETWEEN 16 AND 512),
  pkce_verifier text NOT NULL CHECK (pkce_verifier ~ '^[A-Za-z0-9._~-]{43,128}$'),
  destination text NOT NULL CHECK (
    length(destination) BETWEEN 1 AND 512 AND left(destination, 1) = '/' AND left(destination, 2) <> '//'
    AND strpos(destination, chr(92)) = 0 AND destination !~ '[[:space:][:cntrl:]]'),
  expires_at timestamptz NOT NULL
);

-- Depois do callback: a identidade validada espera a escolha de organização e papel, sem voltar ao navegador.
CREATE TABLE app.login_continuation (
  ticket_hash bytea PRIMARY KEY CHECK (octet_length(ticket_hash) = 32),
  issuer text NOT NULL CHECK (length(issuer) BETWEEN 1 AND 255),
  subject text NOT NULL CHECK (length(subject) BETWEEN 1 AND 255),
  destination text NOT NULL CHECK (
    length(destination) BETWEEN 1 AND 512 AND left(destination, 1) = '/' AND left(destination, 2) <> '//'
    AND strpos(destination, chr(92)) = 0 AND destination !~ '[[:space:][:cntrl:]]'),
  expires_at timestamptz NOT NULL
);

-- RLS com FORCE também aqui. Quem tem organização segue a regra de isolamento de sempre; o papel das funções vê as
-- linhas de que precisa sem organização prévia (a sessão é resolvida antes de existir organização na transação).
ALTER TABLE app.identity_link ENABLE ROW LEVEL SECURITY;
ALTER TABLE app.identity_link FORCE ROW LEVEL SECURITY;
CREATE POLICY isolamento ON app.identity_link
  USING (organization_id = app.organizacao_atual()) WITH CHECK (organization_id = app.organizacao_atual());
CREATE POLICY servico_sessao ON app.identity_link FOR SELECT TO app_sessao USING (true);

ALTER TABLE app.session ENABLE ROW LEVEL SECURITY;
ALTER TABLE app.session FORCE ROW LEVEL SECURITY;
CREATE POLICY isolamento ON app.session
  USING (organization_id = app.organizacao_atual()) WITH CHECK (organization_id = app.organizacao_atual());
CREATE POLICY servico_sessao ON app.session TO app_sessao USING (true) WITH CHECK (true);

ALTER TABLE app.login_transaction ENABLE ROW LEVEL SECURITY;
ALTER TABLE app.login_transaction FORCE ROW LEVEL SECURITY;
CREATE POLICY servico_sessao ON app.login_transaction TO app_sessao USING (true) WITH CHECK (true);

ALTER TABLE app.login_continuation ENABLE ROW LEVEL SECURITY;
ALTER TABLE app.login_continuation FORCE ROW LEVEL SECURITY;
CREATE POLICY servico_sessao ON app.login_continuation TO app_sessao USING (true) WITH CHECK (true);

CREATE POLICY leitura_sessao ON app.organization FOR SELECT TO app_sessao USING (true);
CREATE POLICY leitura_sessao ON app.app_user FOR SELECT TO app_sessao USING (true);
CREATE POLICY leitura_sessao ON app.user_role FOR SELECT TO app_sessao USING (true);

GRANT SELECT ON app.organization, app.app_user, app.user_role, app.identity_link TO app_sessao;
GRANT SELECT, INSERT, UPDATE (revoked_at) ON app.session TO app_sessao;
GRANT SELECT, INSERT, DELETE ON app.login_transaction, app.login_continuation TO app_sessao;

-- Funções -------------------------------------------------------------------------------------------------------------

CREATE FUNCTION app.abrir_transacao_login(p_ticket_hash bytea, p_state text, p_nonce text, p_verificador text,
                                          p_destino text, p_validade_segundos integer DEFAULT 600)
  RETURNS timestamptz
  LANGUAGE plpgsql SECURITY DEFINER SET search_path = pg_catalog, pg_temp
  AS $$
DECLARE
  v_expira timestamptz;
BEGIN
  IF p_validade_segundos IS NULL OR p_validade_segundos NOT BETWEEN 1 AND 600 THEN
    RAISE EXCEPTION 'validade da transação de login fora do limite' USING ERRCODE = '22023';
  END IF;
  DELETE FROM app.login_transaction t WHERE t.expires_at < clock_timestamp();
  v_expira := clock_timestamp() + make_interval(secs => p_validade_segundos);
  INSERT INTO app.login_transaction (ticket_hash, state, nonce, pkce_verifier, destination, expires_at)
    VALUES (p_ticket_hash, p_state, p_nonce, p_verificador, p_destino, v_expira);
  RETURN v_expira;
END $$;

-- Uso único: o ticket é apagado ao ser lido, vencido ou não; só volta dado se ainda estava válido.
CREATE FUNCTION app.consumir_transacao_login(p_ticket_hash bytea)
  RETURNS TABLE (state text, nonce text, verificador text, destino text)
  LANGUAGE sql SECURITY DEFINER SET search_path = pg_catalog, pg_temp
  AS $$
  WITH consumida AS (
    DELETE FROM app.login_transaction t WHERE t.ticket_hash = p_ticket_hash
    RETURNING t.state, t.nonce, t.pkce_verifier, t.destination, t.expires_at
  )
  SELECT c.state, c.nonce, c.pkce_verifier, c.destination FROM consumida c WHERE c.expires_at > clock_timestamp()
$$;

CREATE FUNCTION app.abrir_continuacao(p_ticket_hash bytea, p_issuer text, p_subject text, p_destino text,
                                      p_validade_segundos integer DEFAULT 600)
  RETURNS timestamptz
  LANGUAGE plpgsql SECURITY DEFINER SET search_path = pg_catalog, pg_temp
  AS $$
DECLARE
  v_expira timestamptz;
BEGIN
  IF p_validade_segundos IS NULL OR p_validade_segundos NOT BETWEEN 1 AND 600 THEN
    RAISE EXCEPTION 'validade da continuação fora do limite' USING ERRCODE = '22023';
  END IF;
  DELETE FROM app.login_continuation c WHERE c.expires_at < clock_timestamp();
  v_expira := clock_timestamp() + make_interval(secs => p_validade_segundos);
  INSERT INTO app.login_continuation (ticket_hash, issuer, subject, destination, expires_at)
    VALUES (p_ticket_hash, p_issuer, p_subject, p_destino, v_expira);
  RETURN v_expira;
END $$;

-- Organizações e papéis vivos da identidade guardada na continuação, sem consumi-la: monta a tela de escolha.
CREATE FUNCTION app.vinculos_da_continuacao(p_ticket_hash bytea)
  RETURNS TABLE (organization_id uuid, organization_name text, role_code text)
  LANGUAGE sql SECURITY DEFINER SET search_path = pg_catalog, pg_temp
  AS $$
  SELECT o.id, o.name, ur.role_code
    FROM app.login_continuation c
    JOIN app.identity_link l ON l.issuer = c.issuer AND l.subject = c.subject
    JOIN app.app_user u ON u.organization_id = l.organization_id AND u.id = l.user_id AND u.active
    JOIN app.user_role ur ON ur.organization_id = l.organization_id AND ur.user_id = l.user_id
    JOIN app.organization o ON o.id = l.organization_id
   WHERE c.ticket_hash = p_ticket_hash AND c.expires_at > clock_timestamp()
   ORDER BY o.name, o.id, ur.role_code
$$;

-- Único caminho que cria sessão: consome a continuação (uso único, mesmo quando a escolha é recusada), revalida o
-- vínculo vivo naquele instante e grava a sessão, tudo na mesma transação. Resultado só por código.
CREATE FUNCTION app.concluir_continuacao(p_ticket_hash bytea, p_organizacao uuid, p_papel text, p_sessao_hash bytea,
                                         p_validade_segundos integer DEFAULT 43200)
  RETURNS TABLE (resultado text, user_id uuid, destino text, expira_em timestamptz)
  LANGUAGE plpgsql SECURITY DEFINER SET search_path = pg_catalog, pg_temp
  AS $$
DECLARE
  v_cont app.login_continuation;
  v_usuario uuid;
  v_expira timestamptz;
BEGIN
  IF p_validade_segundos IS NULL OR p_validade_segundos NOT BETWEEN 1 AND 43200 THEN
    RAISE EXCEPTION 'validade da sessão fora do limite' USING ERRCODE = '22023';
  END IF;
  DELETE FROM app.login_continuation c WHERE c.ticket_hash = p_ticket_hash RETURNING c.* INTO v_cont;
  IF NOT FOUND OR v_cont.expires_at <= clock_timestamp() THEN
    RETURN QUERY SELECT 'CONTINUACAO_INVALIDA'::text, NULL::uuid, NULL::text, NULL::timestamptz;
    RETURN;
  END IF;
  SELECT l.user_id INTO v_usuario
    FROM app.identity_link l
    JOIN app.app_user u ON u.organization_id = l.organization_id AND u.id = l.user_id AND u.active
    JOIN app.user_role ur ON ur.organization_id = l.organization_id AND ur.user_id = l.user_id
                         AND ur.role_code = p_papel
   WHERE l.issuer = v_cont.issuer AND l.subject = v_cont.subject AND l.organization_id = p_organizacao;
  IF v_usuario IS NULL THEN
    RETURN QUERY SELECT 'VINCULO_AUSENTE'::text, NULL::uuid, NULL::text, NULL::timestamptz;
    RETURN;
  END IF;
  v_expira := clock_timestamp() + make_interval(secs => p_validade_segundos);
  INSERT INTO app.session (token_hash, organization_id, user_id, role_code, issuer, subject, expires_at)
    VALUES (p_sessao_hash, p_organizacao, v_usuario, p_papel, v_cont.issuer, v_cont.subject, v_expira);
  RETURN QUERY SELECT 'SESSAO_CRIADA'::text, v_usuario, v_cont.destination, v_expira;
END $$;

-- Sessão válida com vínculo vivo: não revogada, não vencida, identidade ainda ligada ao usuário na organização,
-- usuário ativo e papel ainda atribuído. Qualquer falha: nenhuma linha. Não fixa organização na transação.
CREATE FUNCTION app.resolver_sessao(p_sessao_hash bytea)
  RETURNS TABLE (user_id uuid, organization_id uuid, role_code text, expira_em timestamptz)
  LANGUAGE sql SECURITY DEFINER SET search_path = pg_catalog, pg_temp
  AS $$
  SELECT s.user_id, s.organization_id, s.role_code, s.expires_at
    FROM app.session s
    JOIN app.identity_link l ON l.issuer = s.issuer AND l.subject = s.subject
                            AND l.organization_id = s.organization_id AND l.user_id = s.user_id
    JOIN app.app_user u ON u.organization_id = s.organization_id AND u.id = s.user_id AND u.active
    JOIN app.user_role ur ON ur.organization_id = s.organization_id AND ur.user_id = s.user_id
                         AND ur.role_code = s.role_code
   WHERE s.token_hash = p_sessao_hash AND s.revoked_at IS NULL AND s.expires_at > clock_timestamp()
$$;

CREATE FUNCTION app.revogar_sessao(p_sessao_hash bytea)
  RETURNS boolean
  LANGUAGE sql SECURITY DEFINER SET search_path = pg_catalog, pg_temp
  AS $$
  WITH revogada AS (
    UPDATE app.session s SET revoked_at = clock_timestamp()
     WHERE s.token_hash = p_sessao_hash AND s.revoked_at IS NULL
    RETURNING 1
  )
  SELECT EXISTS (SELECT 1 FROM revogada)
$$;

-- Troca de papel: só para papel atribuído ao usuário na mesma organização; revoga a sessão atual e cria outra com a
-- mesma expiração (trocar de papel não estende a sessão).
CREATE FUNCTION app.trocar_papel(p_sessao_hash bytea, p_papel text, p_nova_hash bytea)
  RETURNS TABLE (resultado text, expira_em timestamptz)
  LANGUAGE plpgsql SECURITY DEFINER SET search_path = pg_catalog, pg_temp
  AS $$
DECLARE
  v_atual record;
BEGIN
  SELECT r.user_id, r.organization_id, r.expira_em INTO v_atual FROM app.resolver_sessao(p_sessao_hash) r;
  IF NOT FOUND THEN
    RETURN QUERY SELECT 'SESSAO_INVALIDA'::text, NULL::timestamptz;
    RETURN;
  END IF;
  IF NOT EXISTS (SELECT 1 FROM app.user_role ur
                  WHERE ur.organization_id = v_atual.organization_id AND ur.user_id = v_atual.user_id
                    AND ur.role_code = p_papel) THEN
    RETURN QUERY SELECT 'PAPEL_NAO_VINCULADO'::text, NULL::timestamptz;
    RETURN;
  END IF;
  UPDATE app.session s SET revoked_at = clock_timestamp()
   WHERE s.token_hash = p_sessao_hash AND s.revoked_at IS NULL;
  IF NOT FOUND THEN
    RETURN QUERY SELECT 'SESSAO_INVALIDA'::text, NULL::timestamptz;
    RETURN;
  END IF;
  INSERT INTO app.session (token_hash, organization_id, user_id, role_code, issuer, subject, expires_at,
                           origin_token_hash)
    SELECT p_nova_hash, s.organization_id, s.user_id, p_papel, s.issuer, s.subject, s.expires_at, s.token_hash
      FROM app.session s WHERE s.token_hash = p_sessao_hash;
  RETURN QUERY SELECT 'SESSAO_CRIADA'::text, v_atual.expira_em;
END $$;

DO $$
DECLARE
  f text;
BEGIN
  FOREACH f IN ARRAY ARRAY[
    'abrir_transacao_login(bytea, text, text, text, text, integer)',
    'consumir_transacao_login(bytea)',
    'abrir_continuacao(bytea, text, text, text, integer)',
    'vinculos_da_continuacao(bytea)',
    'concluir_continuacao(bytea, uuid, text, bytea, integer)',
    'resolver_sessao(bytea)',
    'revogar_sessao(bytea)',
    'trocar_papel(bytea, text, bytea)'] LOOP
    -- Nesta ordem: só o dono revoga o EXECUTE padrão de PUBLIC. Depois de trocar o dono, o REVOKE do migrator não
    -- teria efeito e qualquer papel executaria as funções. A troca de dono leva junto as permissões já ajustadas.
    EXECUTE format('REVOKE ALL ON FUNCTION app.%s FROM PUBLIC', f);
    EXECUTE format('GRANT EXECUTE ON FUNCTION app.%s TO app_runtime', f);
    EXECUTE format('ALTER FUNCTION app.%s OWNER TO app_sessao', f);
  END LOOP;
END $$;
