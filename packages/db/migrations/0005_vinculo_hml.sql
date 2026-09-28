-- F1: vínculo de identidade real em HML (ADR 0004 §11). Aplicada pelo migrator.
-- - Pedido de acesso: nasce de um login OIDC validado sem vínculo, pela casca (app_runtime), e não concede nada. O banco
--   guarda só o SHA-256 do código de referência. Um pedido vivo por identidade, 24 h; até 100 vivos e 1000 retidos.
-- - Concessão e revogação: funções só para o migrator (caminho do administrador), só em banco identificado como hml,
--   com responsável e motivo. O app_runtime não concede nem revoga.
-- - Auditoria imutável em identity_link_event. O audit_log exige um usuário da aplicação como autor; o operador não é.
-- - Concessão, revogação, conclusão de login e troca de papel usam a mesma trava por organização e usuário: uma sessão
--   criada durante a revogação nunca sobra para voltar a valer numa concessão posterior.

CREATE TABLE app.access_request (
  code_hash bytea PRIMARY KEY CHECK (octet_length(code_hash) = 32),
  issuer text NOT NULL CHECK (length(issuer) BETWEEN 1 AND 255),
  subject text NOT NULL CHECK (length(subject) BETWEEN 1 AND 255),
  created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
  expires_at timestamptz NOT NULL,
  -- Preenchidos juntos no consumo: o destino fica para a idempotência da concessão.
  consumed_at timestamptz,
  organization_id uuid,
  user_id uuid,
  CHECK ((consumed_at IS NULL) = (organization_id IS NULL) AND (organization_id IS NULL) = (user_id IS NULL))
);
CREATE UNIQUE INDEX access_request_um_vivo ON app.access_request (issuer, subject) WHERE consumed_at IS NULL;

CREATE TABLE app.identity_link_event (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  occurred_at timestamptz NOT NULL DEFAULT clock_timestamp(),
  action text NOT NULL CHECK (action IN ('concedido', 'revogado')),
  organization_id uuid NOT NULL,
  user_id uuid NOT NULL,
  issuer text NOT NULL,
  subject text NOT NULL,
  -- Quem estava conectado ao banco (session_user), não o dono da função.
  database_user text NOT NULL DEFAULT session_user,
  responsible text NOT NULL CHECK (length(btrim(responsible)) BETWEEN 1 AND 120),
  reason text NOT NULL CHECK (length(btrim(reason)) BETWEEN 1 AND 200)
);
CREATE INDEX identity_link_event_por_usuario ON app.identity_link_event (organization_id, user_id, occurred_at);
CREATE TRIGGER identity_link_event_imutavel BEFORE UPDATE OR DELETE ON app.identity_link_event
  FOR EACH ROW EXECUTE FUNCTION app.impedir_alteracao();

ALTER TABLE app.access_request ENABLE ROW LEVEL SECURITY;
ALTER TABLE app.access_request FORCE ROW LEVEL SECURITY;
CREATE POLICY servico_sessao ON app.access_request TO app_sessao USING (true) WITH CHECK (true);

ALTER TABLE app.identity_link_event ENABLE ROW LEVEL SECURITY;
ALTER TABLE app.identity_link_event FORCE ROW LEVEL SECURITY;
CREATE POLICY servico_sessao ON app.identity_link_event FOR SELECT TO app_sessao USING (true);
CREATE POLICY servico_sessao_registrar ON app.identity_link_event FOR INSERT TO app_sessao WITH CHECK (true);
-- O administrador, como migrator, lê a auditoria; ninguém da aplicação a altera.
CREATE POLICY leitura_auditoria ON app.identity_link_event FOR SELECT TO migrator USING (true);

-- O papel das funções grava e apaga também vínculo de issuer real; só as funções abaixo fazem isso.
CREATE POLICY vinculo_real_inserir ON app.identity_link FOR INSERT TO app_sessao
  WITH CHECK (issuer <> 'urn:safrion:desenvolvimento');
CREATE POLICY vinculo_real_apagar ON app.identity_link FOR DELETE TO app_sessao
  USING (issuer <> 'urn:safrion:desenvolvimento');

GRANT SELECT, INSERT, UPDATE, DELETE ON app.access_request TO app_sessao;
GRANT SELECT, INSERT ON app.identity_link_event TO app_sessao;

-- Funções -------------------------------------------------------------------------------------------------------------

-- Trava por organização e usuário, comum a concessão, revogação, conclusão de login e troca de papel.
CREATE FUNCTION app.travar_vinculo(p_organizacao uuid, p_usuario uuid)
  RETURNS void
  LANGUAGE sql SET search_path = pg_catalog, pg_temp
  AS $$ SELECT pg_advisory_xact_lock(hashtext('safrion.vinculo'), hashtext(p_organizacao::text || '/' || p_usuario::text)) $$;

-- Pedido de acesso da casca, depois de um login OIDC validado sem vínculo. Não concede nada. Fora de hml, não grava.
CREATE FUNCTION app.registrar_pedido_acesso(p_issuer text, p_subject text, p_codigo_hash bytea)
  RETURNS text
  LANGUAGE plpgsql SECURITY DEFINER SET search_path = pg_catalog, pg_temp
  AS $$
DECLARE
  v_vivos bigint;
  v_retidos bigint;
BEGIN
  IF NOT EXISTS (SELECT 1 FROM app.environment_identity e WHERE e.name = 'hml') THEN
    RETURN 'fora_de_hml';
  END IF;
  IF p_issuer IS NULL OR p_subject IS NULL OR p_codigo_hash IS NULL OR octet_length(p_codigo_hash) <> 32
     OR length(p_issuer) NOT BETWEEN 1 AND 255 OR length(p_subject) NOT BETWEEN 1 AND 255
     OR p_issuer = 'urn:safrion:desenvolvimento' THEN
    RETURN 'recusado';
  END IF;
  -- Um registro por vez: a cota é conferida sem corrida, e a limpeza acontece aqui mesmo, sem serviço à parte.
  PERFORM pg_advisory_xact_lock(hashtext('safrion.pedido_acesso'));
  DELETE FROM app.access_request r WHERE r.consumed_at IS NULL AND r.expires_at <= clock_timestamp();
  DELETE FROM app.access_request r WHERE r.consumed_at <= clock_timestamp() - interval '30 days';
  IF NOT EXISTS (SELECT 1 FROM app.access_request r
                  WHERE r.issuer = p_issuer AND r.subject = p_subject AND r.consumed_at IS NULL) THEN
    SELECT count(*) FILTER (WHERE r.consumed_at IS NULL), count(*) INTO v_vivos, v_retidos FROM app.access_request r;
    IF v_vivos >= 100 OR v_retidos >= 1000 THEN
      RETURN 'cota_esgotada';
    END IF;
  END IF;
  INSERT INTO app.access_request (code_hash, issuer, subject, expires_at)
    VALUES (p_codigo_hash, p_issuer, p_subject, clock_timestamp() + interval '24 hours')
    ON CONFLICT (issuer, subject) WHERE consumed_at IS NULL
    DO UPDATE SET code_hash = EXCLUDED.code_hash, created_at = clock_timestamp(), expires_at = EXCLUDED.expires_at;
  RETURN 'registrado';
END $$;

-- Concessão pelo administrador. Nada muda se qualquer conferência falhar. Repetir o mesmo pedido para o mesmo destino,
-- com a concessão vigente, devolve 'mantido' sem evento; depois de revogada, o código antigo não reabre o acesso.
CREATE FUNCTION app.conceder_vinculo(p_codigo_hash bytea, p_organizacao uuid, p_usuario uuid, p_responsavel text,
                                     p_motivo text)
  RETURNS text
  LANGUAGE plpgsql SECURITY DEFINER SET search_path = pg_catalog, pg_temp
  AS $$
DECLARE
  v_pedido app.access_request;
  v_atual uuid;
BEGIN
  IF NOT EXISTS (SELECT 1 FROM app.environment_identity e WHERE e.name = 'hml') THEN
    RETURN 'AMBIENTE_PROIBIDO';
  END IF;
  IF p_codigo_hash IS NULL OR p_organizacao IS NULL OR p_usuario IS NULL
     OR p_responsavel IS NULL OR length(btrim(p_responsavel)) NOT BETWEEN 1 AND 120 OR p_responsavel ~ '[[:cntrl:]]'
     OR p_motivo IS NULL OR length(btrim(p_motivo)) NOT BETWEEN 1 AND 200 OR p_motivo ~ '[[:cntrl:]]' THEN
    RETURN 'OPCAO_INVALIDA';
  END IF;
  PERFORM app.travar_vinculo(p_organizacao, p_usuario);
  SELECT * INTO v_pedido FROM app.access_request r WHERE r.code_hash = p_codigo_hash FOR UPDATE;
  IF NOT FOUND OR v_pedido.issuer = 'urn:safrion:desenvolvimento' THEN
    RETURN 'PEDIDO_INEXISTENTE';
  END IF;
  IF v_pedido.consumed_at IS NOT NULL THEN
    IF v_pedido.organization_id <> p_organizacao OR v_pedido.user_id <> p_usuario THEN
      RETURN 'VINCULO_CONFLITANTE';
    END IF;
    IF EXISTS (SELECT 1 FROM app.identity_link l
                WHERE l.issuer = v_pedido.issuer AND l.subject = v_pedido.subject
                  AND l.organization_id = p_organizacao AND l.user_id = p_usuario) THEN
      RETURN 'mantido';
    END IF;
    RETURN 'PEDIDO_CONSUMIDO';
  END IF;
  IF v_pedido.expires_at <= clock_timestamp() THEN
    RETURN 'PEDIDO_VENCIDO';
  END IF;
  IF NOT EXISTS (SELECT 1 FROM app.app_user u
                   JOIN app.user_role ur ON ur.organization_id = u.organization_id AND ur.user_id = u.id
                  WHERE u.organization_id = p_organizacao AND u.id = p_usuario AND u.active) THEN
    RETURN 'USUARIO_INVALIDO';
  END IF;
  SELECT l.user_id INTO v_atual FROM app.identity_link l
   WHERE l.issuer = v_pedido.issuer AND l.subject = v_pedido.subject AND l.organization_id = p_organizacao;
  IF v_atual IS NOT NULL AND v_atual <> p_usuario THEN
    RETURN 'VINCULO_CONFLITANTE';
  END IF;
  UPDATE app.access_request r
     SET consumed_at = clock_timestamp(), organization_id = p_organizacao, user_id = p_usuario
   WHERE r.code_hash = p_codigo_hash;
  IF v_atual IS NOT NULL THEN
    RETURN 'mantido';
  END IF;
  -- Sessão que sobrou de um vínculo anterior desta identidade nesta organização nunca volta a valer.
  UPDATE app.session s SET revoked_at = clock_timestamp()
   WHERE s.issuer = v_pedido.issuer AND s.subject = v_pedido.subject AND s.organization_id = p_organizacao
     AND s.revoked_at IS NULL;
  INSERT INTO app.identity_link (issuer, subject, organization_id, user_id)
    VALUES (v_pedido.issuer, v_pedido.subject, p_organizacao, p_usuario);
  INSERT INTO app.identity_link_event (action, organization_id, user_id, issuer, subject, responsible, reason)
    VALUES ('concedido', p_organizacao, p_usuario, v_pedido.issuer, v_pedido.subject, btrim(p_responsavel),
            btrim(p_motivo));
  RETURN 'concedido';
END $$;

-- Revogação pelo administrador: todos os vínculos do usuário nesta organização, com um evento por vínculo, e as
-- sessões dele nesta organização. Outras organizações não mudam. Repetir não muda nada.
CREATE FUNCTION app.revogar_vinculos(p_organizacao uuid, p_usuario uuid, p_responsavel text, p_motivo text)
  RETURNS TABLE (resultado text, revogados integer)
  LANGUAGE plpgsql SECURITY DEFINER SET search_path = pg_catalog, pg_temp
  AS $$
DECLARE
  v_n integer;
BEGIN
  IF NOT EXISTS (SELECT 1 FROM app.environment_identity e WHERE e.name = 'hml') THEN
    RETURN QUERY SELECT 'AMBIENTE_PROIBIDO'::text, 0;
    RETURN;
  END IF;
  IF p_organizacao IS NULL OR p_usuario IS NULL
     OR p_responsavel IS NULL OR length(btrim(p_responsavel)) NOT BETWEEN 1 AND 120 OR p_responsavel ~ '[[:cntrl:]]'
     OR p_motivo IS NULL OR length(btrim(p_motivo)) NOT BETWEEN 1 AND 200 OR p_motivo ~ '[[:cntrl:]]' THEN
    RETURN QUERY SELECT 'OPCAO_INVALIDA'::text, 0;
    RETURN;
  END IF;
  PERFORM app.travar_vinculo(p_organizacao, p_usuario);
  WITH apagados AS (
    DELETE FROM app.identity_link l WHERE l.organization_id = p_organizacao AND l.user_id = p_usuario
    RETURNING l.issuer, l.subject
  )
  INSERT INTO app.identity_link_event (action, organization_id, user_id, issuer, subject, responsible, reason)
    SELECT 'revogado', p_organizacao, p_usuario, a.issuer, a.subject, btrim(p_responsavel), btrim(p_motivo)
      FROM apagados a;
  GET DIAGNOSTICS v_n = ROW_COUNT;
  UPDATE app.session s SET revoked_at = clock_timestamp()
   WHERE s.organization_id = p_organizacao AND s.user_id = p_usuario AND s.revoked_at IS NULL;
  RETURN QUERY SELECT CASE WHEN v_n > 0 THEN 'revogado' ELSE 'sem_vinculo' END, v_n;
END $$;

-- demo:reset em hml: vínculos reais que apontam para gerações anteriores da demonstração saem, com evento e sessões
-- revogadas, na mesma transação do reset. Nada passa para a geração nova. Fora de hml, não faz nada (DEV segue só com o
-- vínculo sintético da 0004).
CREATE FUNCTION app.revogar_vinculos_demonstracao(p_organizacao_atual uuid)
  RETURNS integer
  LANGUAGE plpgsql SECURITY DEFINER SET search_path = pg_catalog, pg_temp
  AS $$
DECLARE
  v record;
  v_k integer;
  v_n integer := 0;
BEGIN
  IF NOT EXISTS (SELECT 1 FROM app.environment_identity e WHERE e.name = 'hml') THEN
    RETURN 0;
  END IF;
  FOR v IN
    SELECT DISTINCT l.organization_id, l.user_id
      FROM app.identity_link l JOIN app.organization o ON o.id = l.organization_id AND o.fictitious
     WHERE l.organization_id <> p_organizacao_atual AND l.issuer <> 'urn:safrion:desenvolvimento'
     ORDER BY l.organization_id, l.user_id
  LOOP
    PERFORM app.travar_vinculo(v.organization_id, v.user_id);
    WITH apagados AS (
      DELETE FROM app.identity_link l
       WHERE l.organization_id = v.organization_id AND l.user_id = v.user_id
         AND l.issuer <> 'urn:safrion:desenvolvimento'
      RETURNING l.issuer, l.subject
    )
    INSERT INTO app.identity_link_event (action, organization_id, user_id, issuer, subject, responsible, reason)
      SELECT 'revogado', v.organization_id, v.user_id, a.issuer, a.subject, 'demo:reset', 'demo_reset' FROM apagados a;
    GET DIAGNOSTICS v_k = ROW_COUNT;
    v_n := v_n + v_k;
    UPDATE app.session s SET revoked_at = clock_timestamp()
     WHERE s.organization_id = v.organization_id AND s.user_id = v.user_id
       AND s.issuer <> 'urn:safrion:desenvolvimento' AND s.revoked_at IS NULL;
  END LOOP;
  RETURN v_n;
END $$;

-- Conclusão de login e troca de papel da 0003, agora com a trava do vínculo: se a revogação chega no meio, ou ela espera a
-- sessão existir para revogá-la, ou a conclusão espera a revogação e não acha mais o vínculo. As duas são do app_sessao,
-- e o migrator só assume esse papel (sem herdar): a substituição roda como ele, e dono e EXECUTE continuam os mesmos.
SET LOCAL ROLE app_sessao;

CREATE OR REPLACE FUNCTION app.concluir_continuacao(p_ticket_hash bytea, p_organizacao uuid, p_papel text,
                                                    p_sessao_hash bytea, p_validade_segundos integer DEFAULT 43200)
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
  SELECT l.user_id INTO v_usuario FROM app.identity_link l
   WHERE l.issuer = v_cont.issuer AND l.subject = v_cont.subject AND l.organization_id = p_organizacao;
  IF v_usuario IS NOT NULL THEN
    PERFORM app.travar_vinculo(p_organizacao, v_usuario);
    -- Depois da trava, o vínculo é lido de novo: uma revogação concluída enquanto esperava já aparece aqui.
    SELECT l.user_id INTO v_usuario
      FROM app.identity_link l
      JOIN app.app_user u ON u.organization_id = l.organization_id AND u.id = l.user_id AND u.active
      JOIN app.user_role ur ON ur.organization_id = l.organization_id AND ur.user_id = l.user_id
                           AND ur.role_code = p_papel
     WHERE l.issuer = v_cont.issuer AND l.subject = v_cont.subject AND l.organization_id = p_organizacao
       AND l.user_id = v_usuario;
  END IF;
  IF v_usuario IS NULL THEN
    RETURN QUERY SELECT 'VINCULO_AUSENTE'::text, NULL::uuid, NULL::text, NULL::timestamptz;
    RETURN;
  END IF;
  v_expira := clock_timestamp() + make_interval(secs => p_validade_segundos);
  INSERT INTO app.session (token_hash, organization_id, user_id, role_code, issuer, subject, expires_at)
    VALUES (p_sessao_hash, p_organizacao, v_usuario, p_papel, v_cont.issuer, v_cont.subject, v_expira);
  RETURN QUERY SELECT 'SESSAO_CRIADA'::text, v_usuario, v_cont.destination, v_expira;
END $$;

CREATE OR REPLACE FUNCTION app.trocar_papel(p_sessao_hash bytea, p_papel text, p_nova_hash bytea)
  RETURNS TABLE (resultado text, expira_em timestamptz)
  LANGUAGE plpgsql SECURITY DEFINER SET search_path = pg_catalog, pg_temp
  AS $$
DECLARE
  v_atual record;
BEGIN
  SELECT r.user_id, r.organization_id, r.expira_em INTO v_atual FROM app.resolver_sessao(p_sessao_hash) r;
  IF FOUND THEN
    PERFORM app.travar_vinculo(v_atual.organization_id, v_atual.user_id);
    SELECT r.user_id, r.organization_id, r.expira_em INTO v_atual FROM app.resolver_sessao(p_sessao_hash) r;
  END IF;
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

RESET ROLE;

-- Mesma ordem da 0003: o dono atual (migrator) revoga e concede antes de entregar a posse. A trava não é SECURITY
-- DEFINER e só trava; as funções que a usam são do app_sessao.
REVOKE ALL ON FUNCTION app.travar_vinculo(uuid, uuid) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION app.travar_vinculo(uuid, uuid) TO app_sessao;
ALTER FUNCTION app.travar_vinculo(uuid, uuid) OWNER TO app_sessao;

REVOKE ALL ON FUNCTION app.registrar_pedido_acesso(text, text, bytea) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION app.registrar_pedido_acesso(text, text, bytea) TO app_runtime;
ALTER FUNCTION app.registrar_pedido_acesso(text, text, bytea) OWNER TO app_sessao;

REVOKE ALL ON FUNCTION app.revogar_vinculos_demonstracao(uuid) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION app.revogar_vinculos_demonstracao(uuid) TO app_runtime;
ALTER FUNCTION app.revogar_vinculos_demonstracao(uuid) OWNER TO app_sessao;

-- Caminho do administrador: só o migrator executa. O app_runtime não concede nem revoga. O EXECUTE do migrator é
-- concedido depois da troca de dono, pelo novo dono: concedido antes, a troca o transferiria para o app_sessao.
REVOKE ALL ON FUNCTION app.conceder_vinculo(bytea, uuid, uuid, text, text) FROM PUBLIC;
ALTER FUNCTION app.conceder_vinculo(bytea, uuid, uuid, text, text) OWNER TO app_sessao;
REVOKE ALL ON FUNCTION app.revogar_vinculos(uuid, uuid, text, text) FROM PUBLIC;
ALTER FUNCTION app.revogar_vinculos(uuid, uuid, text, text) OWNER TO app_sessao;
SET LOCAL ROLE app_sessao;
GRANT EXECUTE ON FUNCTION app.conceder_vinculo(bytea, uuid, uuid, text, text) TO migrator;
GRANT EXECUTE ON FUNCTION app.revogar_vinculos(uuid, uuid, text, text) TO migrator;
RESET ROLE;
