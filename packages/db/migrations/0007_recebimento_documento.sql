-- F1/CMD-15, incremento 1: recebimento de insumos por documento e inspeção (SU-06, CMD-15, AC-14; contrato CMD-15
-- v3.1). Só estrutura: o efeito receberDocumento, a rota e a tela vêm depois, no mesmo incremento. A entrada atual por
-- lote (estoque.registrar-entrada) continua como está. Aplicada pelo migrator; app_runtime só lê e insere.

-- Validade e lote por produto ------------------------------------------------------------------------------------------
-- A política vale para o lote NOVO. O lote congela a sua (expiry_applies) na criação: mudar a política do produto não
-- invalida lote antigo nem o histórico. "Não se aplica" é NULL com expiry_applies falso, nunca data fictícia (RN-032).
ALTER TABLE app.product
  ADD COLUMN expiry_policy text NOT NULL DEFAULT 'controla' CHECK (expiry_policy IN ('controla', 'nao_se_aplica')),
  ADD COLUMN lot_policy text NOT NULL DEFAULT 'informado' CHECK (lot_policy IN ('informado', 'por_documento'));

-- Lote de fabricante ou agrupamento interno por documento (granel): o interno tem código DOC:<id do documento> e nunca é
-- apresentado como lote do fabricante.
ALTER TABLE app.lot
  ALTER COLUMN expiry_date DROP NOT NULL,
  ADD COLUMN expiry_applies boolean NOT NULL DEFAULT true,
  ADD COLUMN kind text NOT NULL DEFAULT 'fabricante' CHECK (kind IN ('fabricante', 'agrupamento_interno')),
  ADD CONSTRAINT lot_validade_coerente CHECK (expiry_applies = (expiry_date IS NOT NULL)),
  ADD CONSTRAINT lot_interno_por_documento CHECK (
    (kind = 'agrupamento_interno') = (code ~ '^DOC:[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')),
  -- A linha do documento garante que o lote é do produto dela.
  ADD CONSTRAINT lot_org_id_produto UNIQUE (organization_id, id, product_id);

-- A linha garante que o local é da fazenda do documento, e que a conversão é do produto dela, na versão usada.
ALTER TABLE app.stock_location ADD CONSTRAINT stock_location_org_fazenda_id UNIQUE (organization_id, farm_id, id);
ALTER TABLE app.packaging_conversion
  ADD CONSTRAINT packaging_conversion_org_id_produto_versao UNIQUE (organization_id, id, product_id, version);

-- Contraparte mínima (CD-05): emitente do documento, sem duplicar identidade na organização --------------------------
CREATE TABLE app.counterparty (
  id uuid PRIMARY KEY,
  organization_id uuid NOT NULL REFERENCES app.organization (id),
  name text NOT NULL CHECK (btrim(name) <> '' AND length(name) <= 160),
  -- Identificação normalizada pela aplicação (CNPJ ou CPF só com dígitos, ou outra identificação cadastral).
  identification text NOT NULL CHECK (identification = btrim(identification) AND identification <> ''
                                      AND length(identification) <= 64),
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (organization_id, id),
  UNIQUE (organization_id, identification)
);

-- Documento de entrada ---------------------------------------------------------------------------------------------------
-- Nasce confirmado, na versão 1 (incremento 3: estornado). A origem (emitente, tipo, série, número) é única entre os
-- confirmados: a mesma NF não entra duas vezes, nem com chaves de intenção diferentes; depois do estorno, a corrigida
-- pode entrar. Série e número chegam normalizados (sem espaços nas pontas, sem zeros à esquerda quando numéricos).
CREATE TABLE app.receipt_document (
  id uuid PRIMARY KEY,
  organization_id uuid NOT NULL REFERENCES app.organization (id),
  issuer_id uuid NOT NULL,
  doc_type text NOT NULL CHECK (doc_type IN ('nfe', 'outro')),
  series text NOT NULL CHECK (series = btrim(series) AND length(series) <= 8 AND series !~ '^0[0-9]+$'),
  number text NOT NULL CHECK (number = btrim(number) AND number <> '' AND length(number) <= 20
                              AND number !~ '^0[0-9]+$'),
  issued_on date NOT NULL,
  received_on date NOT NULL,
  farm_id uuid NOT NULL,
  -- Pedido do sistema de origem, quando houver: referência registrada, não identidade (entrega parcial é legítima).
  external_system text CHECK (external_system IS NULL OR (btrim(external_system) <> '' AND length(external_system) <= 40)),
  external_order_ref text CHECK (external_order_ref IS NULL
                                 OR (btrim(external_order_ref) <> '' AND length(external_order_ref) <= 64)),
  status text NOT NULL DEFAULT 'confirmado' CHECK (status IN ('confirmado', 'estornado')),
  version bigint NOT NULL DEFAULT 1 CHECK (version >= 1),
  actor_id uuid NOT NULL,
  intent_command_type text NOT NULL,
  intent_key text NOT NULL,
  recorded_at timestamptz NOT NULL DEFAULT clock_timestamp(),
  UNIQUE (organization_id, id),
  UNIQUE (organization_id, id, farm_id),
  UNIQUE (organization_id, intent_command_type, intent_key),
  CHECK (external_order_ref IS NOT NULL OR external_system IS NULL),
  FOREIGN KEY (organization_id, issuer_id) REFERENCES app.counterparty (organization_id, id),
  FOREIGN KEY (organization_id, farm_id) REFERENCES app.farm (organization_id, id)
);
CREATE UNIQUE INDEX receipt_document_origem ON app.receipt_document (organization_id, issuer_id, doc_type, series, number)
  WHERE status = 'confirmado';

-- Só status e versão mudam (estorno, incremento 3); o resto do documento é fato.
CREATE FUNCTION app.receipt_document_so_status() RETURNS trigger
  LANGUAGE plpgsql
  AS $$
BEGIN
  IF TG_OP = 'DELETE' OR (NEW.id, NEW.organization_id, NEW.issuer_id, NEW.doc_type, NEW.series, NEW.number,
      NEW.issued_on, NEW.received_on, NEW.farm_id, NEW.external_system, NEW.external_order_ref, NEW.actor_id,
      NEW.intent_command_type, NEW.intent_key, NEW.recorded_at)
     IS DISTINCT FROM (OLD.id, OLD.organization_id, OLD.issuer_id, OLD.doc_type, OLD.series, OLD.number,
      OLD.issued_on, OLD.received_on, OLD.farm_id, OLD.external_system, OLD.external_order_ref, OLD.actor_id,
      OLD.intent_command_type, OLD.intent_key, OLD.recorded_at) THEN
    RAISE EXCEPTION 'documento de entrada: só status e versão mudam; corrija com estorno e novo documento'
      USING ERRCODE = 'P0001';
  END IF;
  RETURN NEW;
END $$;
CREATE TRIGGER receipt_document_so_status BEFORE UPDATE OR DELETE ON app.receipt_document
  FOR EACH ROW EXECUTE FUNCTION app.receipt_document_so_status();

-- Linha do documento: o que o documento diz e o que foi conferido, em parcelas na unidade da linha -----------------------
-- Conferido = apto + quarentena + bloqueado + recusado; físico = apto + quarentena + bloqueado (o recusado não entra).
-- Quarentena tem responsável e prazo da decisão enquanto aberta (SU-06); motivo "outro" exige texto.
CREATE TABLE app.receipt_line (
  id uuid PRIMARY KEY,
  organization_id uuid NOT NULL,
  document_id uuid NOT NULL,
  farm_id uuid NOT NULL,
  line_number integer NOT NULL CHECK (line_number BETWEEN 1 AND 50),
  product_id uuid NOT NULL,
  lot_id uuid NOT NULL,
  location_id uuid NOT NULL,
  document_quantity numeric NOT NULL CHECK (document_quantity > 0),
  unit text NOT NULL CHECK (btrim(unit) <> '' AND length(unit) <= 40),
  conversion_id uuid,
  conversion_version integer,
  qty_apto numeric NOT NULL CHECK (qty_apto >= 0),
  qty_quarentena numeric NOT NULL CHECK (qty_quarentena >= 0),
  qty_bloqueado numeric NOT NULL CHECK (qty_bloqueado >= 0),
  qty_recusado numeric NOT NULL CHECK (qty_recusado >= 0),
  divergence_reason text CHECK (divergence_reason IN ('avaria', 'validade', 'produto_diferente', 'falta', 'sobra',
                                                      'outro')),
  divergence_note text CHECK (divergence_note IS NULL OR (btrim(divergence_note) <> '' AND length(divergence_note) <= 200)),
  inspection_owner_id uuid,
  inspection_due_on date,
  external_order_line_ref text CHECK (external_order_line_ref IS NULL
                                      OR (btrim(external_order_line_ref) <> '' AND length(external_order_line_ref) <= 64)),
  -- Valor unitário na unidade do documento, em BRL, escala 8 (PRD 10.0); ausente é NULL, não zero (RN-032).
  unit_price numeric CHECK (unit_price IS NULL OR (unit_price >= 0 AND scale(unit_price) <= 8)),
  UNIQUE (organization_id, id),
  UNIQUE (organization_id, id, document_id),
  UNIQUE (organization_id, document_id, line_number),
  CHECK ((conversion_id IS NULL) = (conversion_version IS NULL)),
  CHECK ((inspection_owner_id IS NULL) = (inspection_due_on IS NULL)),
  CHECK ((qty_quarentena > 0) = (inspection_owner_id IS NOT NULL)),
  CHECK (divergence_reason IS DISTINCT FROM 'outro' OR divergence_note IS NOT NULL),
  FOREIGN KEY (organization_id, document_id, farm_id) REFERENCES app.receipt_document (organization_id, id, farm_id),
  FOREIGN KEY (organization_id, lot_id, product_id) REFERENCES app.lot (organization_id, id, product_id),
  FOREIGN KEY (organization_id, farm_id, location_id) REFERENCES app.stock_location (organization_id, farm_id, id),
  FOREIGN KEY (organization_id, conversion_id, product_id, conversion_version)
    REFERENCES app.packaging_conversion (organization_id, id, product_id, version)
);
CREATE TRIGGER receipt_line_imutavel BEFORE UPDATE OR DELETE ON app.receipt_line
  FOR EACH ROW EXECUTE FUNCTION app.impedir_alteracao();

-- Ocorrência de chegada: produto diferente do documento. Não é estoque e não gera movimento; o produto real nunca é
-- convertido pelo cadastro do produto do documento. Retido para decisão fica aberto, com responsável e prazo; devolvido
-- na entrega fica só registrado. A decisão (Resolver diferença) é registro novo, fora deste incremento.
CREATE TABLE app.receipt_occurrence (
  id uuid PRIMARY KEY,
  organization_id uuid NOT NULL,
  document_id uuid NOT NULL,
  line_id uuid NOT NULL,
  real_product_id uuid,
  real_product_description text CHECK (real_product_description IS NULL
                                       OR (btrim(real_product_description) <> '' AND length(real_product_description) <= 160)),
  counted_quantity numeric NOT NULL CHECK (counted_quantity > 0),
  counted_unit text NOT NULL CHECK (btrim(counted_unit) <> '' AND length(counted_unit) <= 40),
  destination text NOT NULL CHECK (destination IN ('retido_para_decisao', 'devolvido_na_entrega')),
  owner_id uuid NOT NULL,
  due_on date,
  status text NOT NULL CHECK (status IN ('aberta', 'registrada')),
  recorded_at timestamptz NOT NULL DEFAULT clock_timestamp(),
  UNIQUE (organization_id, id),
  CHECK (real_product_id IS NOT NULL OR real_product_description IS NOT NULL),
  CHECK ((destination = 'retido_para_decisao') = (status = 'aberta')),
  CHECK (destination <> 'retido_para_decisao' OR due_on IS NOT NULL),
  FOREIGN KEY (organization_id, line_id, document_id) REFERENCES app.receipt_line (organization_id, id, document_id),
  FOREIGN KEY (organization_id, real_product_id) REFERENCES app.product (organization_id, id)
);
CREATE TRIGGER receipt_occurrence_imutavel BEFORE UPDATE OR DELETE ON app.receipt_occurrence
  FOR EACH ROW EXECUTE FUNCTION app.impedir_alteracao();

-- O movimento aponta para a linha que o gerou (trilha lote → linha → documento; estorno no incremento 3).
ALTER TABLE app.stock_movement
  ADD COLUMN receipt_line_id uuid,
  ADD CONSTRAINT stock_movement_linha FOREIGN KEY (organization_id, receipt_line_id)
    REFERENCES app.receipt_line (organization_id, id);

-- RLS com FORCE nas quatro tabelas novas (ENG-025), como na 0001 ------------------------------------------------------
DO $$
DECLARE t text;
BEGIN
  FOREACH t IN ARRAY ARRAY['counterparty', 'receipt_document', 'receipt_line', 'receipt_occurrence'] LOOP
    EXECUTE format('ALTER TABLE app.%I ENABLE ROW LEVEL SECURITY', t);
    EXECUTE format('ALTER TABLE app.%I FORCE ROW LEVEL SECURITY', t);
    EXECUTE format('CREATE POLICY isolamento ON app.%I USING (organization_id = app.organizacao_atual()) '
                   'WITH CHECK (organization_id = app.organizacao_atual())', t);
  END LOOP;
END $$;

-- app_runtime lê e insere; nada de UPDATE nem DELETE (o estorno do incremento 3 terá o seu GRANT de status e versão).
GRANT SELECT, INSERT ON app.counterparty, app.receipt_document, app.receipt_line, app.receipt_occurrence TO app_runtime;
