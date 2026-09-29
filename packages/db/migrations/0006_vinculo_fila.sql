-- F1: fila de pedidos de vínculo em HML (R-006, GCP-0017, §3c). Aplicada pelo migrator.
-- - Cada pedido (uma versão do segredo hml-vinculo-pedido) tem um recibo durável e único, gravado na mesma transação do
--   efeito. Repetir o pedido devolve o recibo e nunca reaplica: uma revogação repetida e atrasada não apaga uma concessão
--   posterior. Ordem, trava e prazo são proteções auxiliares, não a garantia.
-- - O conteudo_hash (vinculo-fila.ts) só separa repetição de reutilização do pedido_id. O código nunca chega aqui.
-- - Só o migrator (caminho do administrador) chama a função, só em banco hml. O app_runtime não lê, não grava e não executa
--   nada daqui.

CREATE TABLE app.vinculo_pedido_recibo (
  pedido_id uuid PRIMARY KEY,
  conteudo_hash bytea NOT NULL CHECK (octet_length(conteudo_hash) = 32),
  acao text NOT NULL CHECK (acao IN ('conceder', 'revogar')),
  -- Sem chave estrangeira: a recusa de negócio também tem recibo, inclusive para usuário que não existe.
  organization_id uuid NOT NULL,
  user_id uuid NOT NULL,
  -- Resultado desconhecido não entra: a gravação falha, a transação é desfeita e a fila para sem recibo.
  resultado text NOT NULL CHECK (resultado IN ('concedido', 'mantido', 'revogado', 'sem_vinculo', 'PEDIDO_ATRASADO',
                                              'OPCAO_INVALIDA', 'PEDIDO_INEXISTENTE', 'PEDIDO_VENCIDO',
                                              'PEDIDO_CONSUMIDO', 'VINCULO_CONFLITANTE', 'USUARIO_INVALIDO')),
  revogados integer CHECK (revogados >= 0),
  -- Versão do segredo da 1ª aplicação; a repetição por outra versão não muda o recibo.
  versao_segredo bigint NOT NULL CHECK (versao_segredo >= 1),
  processado_em timestamptz NOT NULL DEFAULT now(),
  -- Quem estava conectado ao banco (session_user), não o dono da função.
  database_user text NOT NULL DEFAULT session_user
);
CREATE TRIGGER vinculo_pedido_recibo_imutavel BEFORE UPDATE OR DELETE ON app.vinculo_pedido_recibo
  FOR EACH ROW EXECUTE FUNCTION app.impedir_alteracao();
-- TRUNCATE não passa por RLS nem por gatilho de linha: sem este, o dono apagaria todos os recibos, e uma versão que
-- ficou ENABLED seria reaplicada. Barra o engano, não o dono, que ainda pode desativar o gatilho.
CREATE TRIGGER vinculo_pedido_recibo_sem_truncate BEFORE TRUNCATE ON app.vinculo_pedido_recibo
  FOR EACH STATEMENT EXECUTE FUNCTION app.impedir_alteracao();

ALTER TABLE app.vinculo_pedido_recibo ENABLE ROW LEVEL SECURITY;
ALTER TABLE app.vinculo_pedido_recibo FORCE ROW LEVEL SECURITY;
CREATE POLICY recibo_sessao_select ON app.vinculo_pedido_recibo FOR SELECT TO app_sessao USING (true);
CREATE POLICY recibo_sessao_insert ON app.vinculo_pedido_recibo FOR INSERT TO app_sessao WITH CHECK (true);
-- O administrador, como migrator, lê os recibos; ninguém os altera.
CREATE POLICY leitura_auditoria ON app.vinculo_pedido_recibo FOR SELECT TO migrator USING (true);

GRANT SELECT, INSERT ON app.vinculo_pedido_recibo TO app_sessao;
GRANT SELECT ON app.vinculo_pedido_recibo TO migrator;

-- Um pedido da fila, numa transação só: trava do pedido, recibo primeiro, prazo, efeito e recibo novo. Recusa de negócio
-- grava recibo e é final. Chamada fora do contrato é defeito de quem chama: erro, nada gravado, e repetir é seguro.
CREATE FUNCTION app.processar_pedido_vinculo(p_pedido_id uuid, p_conteudo_hash bytea, p_versao_segredo bigint,
                                             p_acao text, p_codigo_hash bytea, p_organizacao uuid, p_usuario uuid,
                                             p_responsavel text, p_motivo text, p_criado_em timestamptz)
  RETURNS TABLE (resultado text, revogados integer, repetido boolean)
  LANGUAGE plpgsql SECURITY DEFINER SET search_path = pg_catalog, pg_temp
  AS $$
DECLARE
  v_recibo app.vinculo_pedido_recibo;
  v_resultado text;
  v_revogados integer;
BEGIN
  -- Fora de hml, como as funções da 0005: nada é gravado, nem recibo.
  IF NOT EXISTS (SELECT 1 FROM app.environment_identity e WHERE e.name = 'hml') THEN
    RETURN QUERY SELECT 'AMBIENTE_PROIBIDO'::text, NULL::integer, false;
    RETURN;
  END IF;
  IF p_pedido_id IS NULL OR p_conteudo_hash IS NULL OR octet_length(p_conteudo_hash) <> 32
     OR p_versao_segredo IS NULL OR p_versao_segredo < 1 OR p_acao IS NULL OR p_acao NOT IN ('conceder', 'revogar')
     OR (p_acao = 'conceder') <> (p_codigo_hash IS NOT NULL) OR octet_length(p_codigo_hash) <> 32
     OR p_organizacao IS NULL OR p_usuario IS NULL OR p_criado_em IS NULL THEN
    RAISE EXCEPTION 'pedido de vínculo fora do contrato' USING ERRCODE = '22023';
  END IF;
  -- Duas execuções com o mesmo pedido: a segunda espera a primeira terminar e lê o recibo dela (cada comando da função
  -- tem instantâneo próprio em READ COMMITTED; em outro nível, a chave primária recusa a segunda e nada fica gravado).
  PERFORM pg_advisory_xact_lock(hashtext('safrion.vinculo_pedido'), hashtext(p_pedido_id::text));
  SELECT * INTO v_recibo FROM app.vinculo_pedido_recibo r WHERE r.pedido_id = p_pedido_id;
  IF FOUND THEN
    IF v_recibo.conteudo_hash = p_conteudo_hash THEN
      RETURN QUERY SELECT v_recibo.resultado, v_recibo.revogados, true;
    ELSE
      RETURN QUERY SELECT 'PEDIDO_ID_REUTILIZADO'::text, NULL::integer, false;
    END IF;
    RETURN;
  END IF;
  -- Prazo fixo de 60 min, contado do início da transação; 60:00 exatos ainda vale.
  IF now() - p_criado_em > interval '60 minutes' THEN
    v_resultado := 'PEDIDO_ATRASADO';
  ELSIF p_acao = 'conceder' THEN
    v_resultado := app.conceder_vinculo(p_codigo_hash, p_organizacao, p_usuario, p_responsavel, p_motivo);
  ELSE
    SELECT r.resultado, r.revogados INTO v_resultado, v_revogados
      FROM app.revogar_vinculos(p_organizacao, p_usuario, p_responsavel, p_motivo) r;
  END IF;
  INSERT INTO app.vinculo_pedido_recibo (pedido_id, conteudo_hash, acao, organization_id, user_id, resultado,
                                         revogados, versao_segredo)
    VALUES (p_pedido_id, p_conteudo_hash, p_acao, p_organizacao, p_usuario, v_resultado, v_revogados,
            p_versao_segredo);
  RETURN QUERY SELECT v_resultado, v_revogados, false;
END $$;

-- Padrão da 0005: o dono atual (migrator) revoga antes de entregar a posse; o EXECUTE do migrator vem depois, pelo novo
-- dono. Como dono de conceder_vinculo e revogar_vinculos, o app_sessao as executa daqui.
REVOKE ALL ON FUNCTION app.processar_pedido_vinculo(uuid, bytea, bigint, text, bytea, uuid, uuid, text, text,
                                                    timestamptz) FROM PUBLIC;
ALTER FUNCTION app.processar_pedido_vinculo(uuid, bytea, bigint, text, bytea, uuid, uuid, text, text, timestamptz)
  OWNER TO app_sessao;
SET LOCAL ROLE app_sessao;
GRANT EXECUTE ON FUNCTION app.processar_pedido_vinculo(uuid, bytea, bigint, text, bytea, uuid, uuid, text, text,
                                                       timestamptz) TO migrator;
RESET ROLE;
