-- F0-c: vínculo das identidades fictícias de desenvolvimento aos usuários da demonstração (ADR 0004 §5; PRD 23.4).
-- Só o demo:reset chama, pelo app_runtime. A função é do app_sessao e só aceita banco identificado como dev ou hml,
-- organização fictícia e o issuer de desenvolvimento, que nenhum provedor real emite (o provedor de DEV só existe com a
-- trava dupla). O vínculo desse subject com gerações anteriores da demonstração sai: só a geração atual entra.

GRANT SELECT ON app.environment_identity TO app_sessao;
-- A política de isolamento de identity_link (0003) chama app.organizacao_atual(); ao inserir ou apagar, o PostgreSQL a
-- avalia também para o app_sessao. A função só lê a organização da transação.
GRANT EXECUTE ON FUNCTION app.organizacao_atual() TO app_sessao;
GRANT INSERT, DELETE ON app.identity_link TO app_sessao;
-- O papel das funções só escreve ou apaga vínculo do issuer de desenvolvimento; vínculo real não passa por aqui.
CREATE POLICY vinculo_demonstracao_inserir ON app.identity_link FOR INSERT TO app_sessao
  WITH CHECK (issuer = 'urn:safrion:desenvolvimento');
CREATE POLICY vinculo_demonstracao_apagar ON app.identity_link FOR DELETE TO app_sessao
  USING (issuer = 'urn:safrion:desenvolvimento');

CREATE FUNCTION app.vincular_demonstracao(p_organizacao uuid, p_usuario uuid, p_subject text)
  RETURNS void
  LANGUAGE plpgsql SECURITY DEFINER SET search_path = pg_catalog, pg_temp
  AS $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM app.environment_identity e WHERE e.name IN ('dev', 'hml')) THEN
    RAISE EXCEPTION 'vínculo de demonstração só em banco dev ou hml identificado' USING ERRCODE = 'P0001';
  END IF;
  IF NOT EXISTS (SELECT 1 FROM app.organization o WHERE o.id = p_organizacao AND o.fictitious) THEN
    RAISE EXCEPTION 'vínculo de demonstração só em organização fictícia' USING ERRCODE = 'P0001';
  END IF;
  IF p_subject IS NULL OR p_subject !~ '^demo-[a-z]+$' THEN
    RAISE EXCEPTION 'subject de demonstração fora do formato' USING ERRCODE = '22023';
  END IF;
  DELETE FROM app.identity_link l
   WHERE l.issuer = 'urn:safrion:desenvolvimento' AND l.subject = p_subject AND l.organization_id <> p_organizacao;
  INSERT INTO app.identity_link (issuer, subject, organization_id, user_id)
    VALUES ('urn:safrion:desenvolvimento', p_subject, p_organizacao, p_usuario);
END $$;

-- Mesma ordem da 0003: o dono atual (migrator) revoga e concede antes de entregar a posse.
REVOKE ALL ON FUNCTION app.vincular_demonstracao(uuid, uuid, text) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION app.vincular_demonstracao(uuid, uuid, text) TO app_runtime;
ALTER FUNCTION app.vincular_demonstracao(uuid, uuid, text) OWNER TO app_sessao;
