-- F0-b: base transacional multiempresa (PRD 11.2, 73.3, 73.6; ENG-021, ENG-022, ENG-025, ENG-026).
-- Aplicada pelo papel migrator, dono das tabelas. A aplicação usa app_runtime: LOGIN, sem BYPASSRLS, sem CREATEROLE,
-- sem CREATEDB e sem posse de tabela. Os nomes de coluna seguem o PRD: organization_id é o tenant_id de 11.2 (IDEM-12).
-- Toda tabela de organização tem RLS habilitado e FORCE: nem o dono passa sem a organização da sessão.

CREATE SCHEMA app;
REVOKE ALL ON SCHEMA app FROM PUBLIC;
GRANT USAGE ON SCHEMA app TO app_runtime;

-- Organização da sessão, fixada por transação com set_config('app.organization_id', id, true).
-- Sem ela o resultado é NULL e nenhuma linha passa nas políticas: falha fechada.
CREATE FUNCTION app.organizacao_atual() RETURNS uuid
  LANGUAGE sql STABLE
  AS $$ SELECT nullif(current_setting('app.organization_id', true), '')::uuid $$;
REVOKE ALL ON FUNCTION app.organizacao_atual() FROM PUBLIC;
GRANT EXECUTE ON FUNCTION app.organizacao_atual() TO app_runtime;

-- Fatos e registros imutáveis (ENG-026; IDEM-17): correção é registro novo vinculado, nunca edição.
CREATE FUNCTION app.impedir_alteracao() RETURNS trigger
  LANGUAGE plpgsql
  AS $$ BEGIN RAISE EXCEPTION 'registro imutável em %: corrija com novo registro vinculado', TG_TABLE_NAME
          USING ERRCODE = 'P0001'; END $$;

-- Organizações e pessoas -----------------------------------------------------------------------------------------------

CREATE TABLE app.organization (
  id uuid PRIMARY KEY,
  name text NOT NULL CHECK (btrim(name) <> ''),
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE app.app_user (
  id uuid NOT NULL,
  organization_id uuid NOT NULL REFERENCES app.organization (id),
  name text NOT NULL CHECK (btrim(name) <> ''),
  email text NOT NULL CHECK (email LIKE '%_@_%'),
  active boolean NOT NULL DEFAULT true,
  created_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (id),
  UNIQUE (organization_id, id)
);
CREATE UNIQUE INDEX app_user_email_por_organizacao ON app.app_user (organization_id, lower(email));

-- Catálogo de papéis da plataforma (sem organização); o que cada papel pode fazer é regra da aplicação (F0-c).
CREATE TABLE app.role (
  code text PRIMARY KEY CHECK (code ~ '^[a-z][a-z_]*$'),
  description text NOT NULL
);

CREATE TABLE app.user_role (
  organization_id uuid NOT NULL,
  user_id uuid NOT NULL,
  role_code text NOT NULL REFERENCES app.role (code),
  PRIMARY KEY (organization_id, user_id, role_code),
  FOREIGN KEY (organization_id, user_id) REFERENCES app.app_user (organization_id, id)
);

-- Fazenda, locais e produtos. Chaves estrangeiras compostas com organization_id impedem referência entre organizações.

CREATE TABLE app.farm (
  id uuid PRIMARY KEY,
  organization_id uuid NOT NULL REFERENCES app.organization (id),
  name text NOT NULL CHECK (btrim(name) <> ''),
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (organization_id, id)
);

CREATE TABLE app.stock_location (
  id uuid PRIMARY KEY,
  organization_id uuid NOT NULL,
  farm_id uuid NOT NULL,
  name text NOT NULL CHECK (btrim(name) <> ''),
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (organization_id, id),
  FOREIGN KEY (organization_id, farm_id) REFERENCES app.farm (organization_id, id)
);

-- Unidade-base por dimensão, igual ao domínio (packages/domain: UNIDADE_BASE): L, kg e un.
CREATE TABLE app.product (
  id uuid PRIMARY KEY,
  organization_id uuid NOT NULL REFERENCES app.organization (id),
  name text NOT NULL CHECK (btrim(name) <> ''),
  base_unit text NOT NULL CHECK (base_unit IN ('L', 'kg', 'un')),
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (organization_id, id),
  UNIQUE (organization_id, id, base_unit)
);

-- Conversão de embalagem versionada (CD-06): nova versão é nova linha; a antiga continua explicando o passado.
CREATE TABLE app.packaging_conversion (
  id uuid PRIMARY KEY,
  organization_id uuid NOT NULL,
  product_id uuid NOT NULL,
  packaging text NOT NULL CHECK (btrim(packaging) <> ''),
  factor numeric NOT NULL CHECK (factor > 0),
  version integer NOT NULL CHECK (version >= 1),
  valid_from timestamptz NOT NULL DEFAULT now(),
  UNIQUE (organization_id, id),
  UNIQUE (organization_id, product_id, packaging, version),
  FOREIGN KEY (organization_id, product_id) REFERENCES app.product (organization_id, id)
);

-- Lote: a versão serve à concorrência otimista (ENG-021: versão esperada em todo comando).
CREATE TABLE app.lot (
  id uuid PRIMARY KEY,
  organization_id uuid NOT NULL,
  product_id uuid NOT NULL,
  code text NOT NULL CHECK (btrim(code) <> ''),
  expiry_date date NOT NULL,
  base_unit text NOT NULL,
  version bigint NOT NULL DEFAULT 0 CHECK (version >= 0),
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (organization_id, id),
  UNIQUE (organization_id, id, base_unit),
  UNIQUE (organization_id, product_id, code),
  FOREIGN KEY (organization_id, product_id, base_unit) REFERENCES app.product (organization_id, id, base_unit)
);

-- Movimento de estoque imutável (ENG-026): quantidade e unidade originais, quantidade na unidade-base e versão da
-- conversão quando veio em embalagem (11.2; PRD 11). A situação usa os valores do domínio (packages/domain SITUACOES).
CREATE TABLE app.stock_movement (
  id uuid PRIMARY KEY,
  organization_id uuid NOT NULL,
  lot_id uuid NOT NULL,
  location_id uuid NOT NULL,
  kind text NOT NULL CHECK (kind IN ('entrada', 'mudanca', 'estorno')),
  situation text CHECK (situation IN ('quarentena_livre', 'quarentena_bloqueado', 'liberado_livre', 'liberado_bloqueado')),
  from_situation text CHECK (from_situation IN ('quarentena_livre', 'quarentena_bloqueado', 'liberado_livre', 'liberado_bloqueado')),
  to_situation text CHECK (to_situation IN ('quarentena_livre', 'quarentena_bloqueado', 'liberado_livre', 'liberado_bloqueado')),
  reverses_id uuid,
  original_quantity numeric,
  original_unit text,
  base_quantity numeric,
  base_unit text,
  conversion_id uuid,
  conversion_version integer,
  lot_version bigint NOT NULL,
  -- Chave de negócio do efeito (INTEG-08): o mesmo item de uma intenção nunca gera dois movimentos.
  intent_command_type text NOT NULL,
  intent_key text NOT NULL,
  intent_item integer NOT NULL DEFAULT 1 CHECK (intent_item >= 1),
  actor_id uuid NOT NULL,
  recorded_at timestamptz NOT NULL DEFAULT clock_timestamp(),
  UNIQUE (organization_id, id),
  UNIQUE (organization_id, intent_command_type, intent_key, intent_item),
  -- Ordem do extrato: cada comando sobe a versão do lote uma vez; itens da mesma intenção se ordenam pelo número.
  UNIQUE (organization_id, lot_id, lot_version, intent_item),
  FOREIGN KEY (organization_id, lot_id) REFERENCES app.lot (organization_id, id),
  -- A unidade-base do movimento é a do lote (MATCH SIMPLE: estorno, sem quantidade, não é conferido aqui).
  FOREIGN KEY (organization_id, lot_id, base_unit) REFERENCES app.lot (organization_id, id, base_unit),
  FOREIGN KEY (organization_id, location_id) REFERENCES app.stock_location (organization_id, id),
  FOREIGN KEY (organization_id, reverses_id) REFERENCES app.stock_movement (organization_id, id),
  FOREIGN KEY (organization_id, conversion_id) REFERENCES app.packaging_conversion (organization_id, id),
  CHECK (
    (kind = 'entrada' AND situation IS NOT NULL AND from_situation IS NULL AND to_situation IS NULL
      AND reverses_id IS NULL AND base_quantity > 0 AND original_quantity > 0)
    OR (kind = 'mudanca' AND situation IS NULL AND from_situation IS NOT NULL AND to_situation IS NOT NULL
      AND from_situation <> to_situation AND reverses_id IS NULL AND base_quantity > 0 AND original_quantity > 0)
    OR (kind = 'estorno' AND situation IS NULL AND from_situation IS NULL AND to_situation IS NULL
      AND reverses_id IS NOT NULL AND base_quantity IS NULL AND original_quantity IS NULL)
  ),
  CHECK ((conversion_id IS NULL) = (conversion_version IS NULL))
);
-- Chave estrangeira não passa pelo RLS: as chaves compostas com organization_id é que impedem referência cruzada.
CREATE TRIGGER stock_movement_imutavel BEFORE UPDATE OR DELETE ON app.stock_movement
  FOR EACH ROW EXECUTE FUNCTION app.impedir_alteracao();

-- Registro da intenção processada (modelo mínimo de 73.3.5; IDEM-12 a IDEM-17). "processing" só existe dentro da
-- transação que o insere; depois do commit o registro não muda.
CREATE TABLE app.intent_record (
  organization_id uuid NOT NULL REFERENCES app.organization (id),
  command_type text NOT NULL CHECK (btrim(command_type) <> '' AND length(command_type) <= 64),
  idempotency_key text NOT NULL CHECK (btrim(idempotency_key) <> '' AND length(idempotency_key) <= 128),
  payload_hash char(64) NOT NULL CHECK (payload_hash ~ '^[0-9a-f]{64}$'),
  canonical_version text NOT NULL,
  initiator_kind text NOT NULL CHECK (initiator_kind IN ('app', 'web', 'integracao', 'ia', 'job')),
  actor_id uuid NOT NULL,
  transport_actor_id uuid,
  device_id text,
  target_type text NOT NULL,
  target_id uuid NOT NULL,
  expected_version bigint,
  resulting_version bigint,
  outcome text NOT NULL CHECK (outcome IN
    ('processing', 'confirmed', 'partial', 'received', 'rejected', 'version_conflict', 'refused', 'key_expired')),
  reason_code text,
  receipt_id uuid NOT NULL,
  effects jsonb NOT NULL DEFAULT '{}'::jsonb,
  pending jsonb NOT NULL DEFAULT '[]'::jsonb,
  next_action text,
  confirmed_at timestamptz,
  received_at timestamptz NOT NULL DEFAULT clock_timestamp(),
  processed_at timestamptz,
  correlation_id text NOT NULL CHECK (btrim(correlation_id) <> ''),
  retain_until timestamptz,
  PRIMARY KEY (organization_id, command_type, idempotency_key)
);
CREATE INDEX intent_record_retencao ON app.intent_record (retain_until) WHERE retain_until IS NOT NULL;

CREATE FUNCTION app.intent_record_imutavel() RETURNS trigger
  LANGUAGE plpgsql
  AS $$
BEGIN
  IF TG_OP = 'DELETE' THEN
    RAISE EXCEPTION 'registro da intenção não é apagado fora da purga por retain_until' USING ERRCODE = 'P0001';
  END IF;
  IF OLD.outcome <> 'processing' OR NEW.outcome = 'processing'
     OR (NEW.organization_id, NEW.command_type, NEW.idempotency_key, NEW.payload_hash, NEW.canonical_version,
         NEW.initiator_kind, NEW.actor_id, NEW.target_type, NEW.target_id, NEW.receipt_id, NEW.received_at,
         NEW.correlation_id)
        IS DISTINCT FROM
        (OLD.organization_id, OLD.command_type, OLD.idempotency_key, OLD.payload_hash, OLD.canonical_version,
         OLD.initiator_kind, OLD.actor_id, OLD.target_type, OLD.target_id, OLD.receipt_id, OLD.received_at,
         OLD.correlation_id) THEN
    RAISE EXCEPTION 'registro da intenção concluído é imutável (IDEM-17)' USING ERRCODE = 'P0001';
  END IF;
  RETURN NEW;
END $$;
CREATE TRIGGER intent_record_imutavel BEFORE UPDATE OR DELETE ON app.intent_record
  FOR EACH ROW EXECUTE FUNCTION app.intent_record_imutavel();

-- Auditoria dos comandos críticos (NFR-04): autor, antes/depois, versão, motivo e correlação. Imutável.
CREATE TABLE app.audit_log (
  id uuid PRIMARY KEY,
  organization_id uuid NOT NULL REFERENCES app.organization (id),
  occurred_at timestamptz NOT NULL DEFAULT clock_timestamp(),
  actor_id uuid NOT NULL,
  command_type text NOT NULL,
  idempotency_key text NOT NULL,
  outcome text NOT NULL,
  target_type text NOT NULL,
  target_id uuid NOT NULL,
  before_state jsonb,
  after_state jsonb,
  resulting_version bigint,
  reason text,
  correlation_id text NOT NULL CHECK (btrim(correlation_id) <> '')
);
CREATE INDEX audit_log_por_objeto ON app.audit_log (organization_id, target_type, target_id, occurred_at);
CREATE TRIGGER audit_log_imutavel BEFORE UPDATE OR DELETE ON app.audit_log
  FOR EACH ROW EXECUTE FUNCTION app.impedir_alteracao();

-- Outbox (73.6.2; INTEG-04): campos de evento de 11.2, agregado com versão e versão anterior, e a intenção de origem.
-- Gravada na mesma transação do efeito (ENG-022). O publicador (futuro) só marca publicação e tentativas.
CREATE TABLE app.outbox (
  event_id uuid PRIMARY KEY,
  organization_id uuid NOT NULL REFERENCES app.organization (id),
  type text NOT NULL CHECK (btrim(type) <> ''),
  schema_version integer NOT NULL CHECK (schema_version >= 1),
  entity_type text NOT NULL,
  entity_id uuid NOT NULL,
  entity_version bigint NOT NULL,
  previous_version bigint,
  causation_command_type text NOT NULL,
  causation_id text NOT NULL,
  actor_id uuid NOT NULL,
  occurred_at timestamptz NOT NULL,
  payload jsonb NOT NULL,
  created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
  published_at timestamptz,
  attempts integer NOT NULL DEFAULT 0 CHECK (attempts >= 0),
  last_error text,
  UNIQUE (organization_id, entity_type, entity_id, entity_version, type)
);
CREATE INDEX outbox_pendente ON app.outbox (created_at) WHERE published_at IS NULL;

-- RLS com FORCE em todas as tabelas de organização (ENG-025) ------------------------------------------------------------

ALTER TABLE app.organization ENABLE ROW LEVEL SECURITY;
ALTER TABLE app.organization FORCE ROW LEVEL SECURITY;
CREATE POLICY isolamento ON app.organization
  USING (id = app.organizacao_atual()) WITH CHECK (id = app.organizacao_atual());

DO $$
DECLARE t text;
BEGIN
  FOREACH t IN ARRAY ARRAY['app_user', 'user_role', 'farm', 'stock_location', 'product', 'packaging_conversion', 'lot',
                           'stock_movement', 'intent_record', 'audit_log', 'outbox'] LOOP
    EXECUTE format('ALTER TABLE app.%I ENABLE ROW LEVEL SECURITY', t);
    EXECUTE format('ALTER TABLE app.%I FORCE ROW LEVEL SECURITY', t);
    EXECUTE format('CREATE POLICY isolamento ON app.%I USING (organization_id = app.organizacao_atual()) '
                   'WITH CHECK (organization_id = app.organizacao_atual())', t);
  END LOOP;
END $$;

-- Permissões mínimas de app_runtime: ler e inserir; nada de DELETE. UPDATE só nas colunas que o envelope e o
-- publicador precisam. Cadastros ganham UPDATE quando os comandos de cadastro existirem (F1/etapa 03).

GRANT SELECT ON ALL TABLES IN SCHEMA app TO app_runtime;
GRANT INSERT ON app.organization, app.app_user, app.user_role, app.farm, app.stock_location, app.product,
  app.packaging_conversion, app.lot, app.stock_movement, app.intent_record, app.audit_log, app.outbox TO app_runtime;
GRANT UPDATE (version) ON app.lot TO app_runtime;
GRANT UPDATE (outcome, reason_code, resulting_version, effects, pending, next_action, processed_at, retain_until)
  ON app.intent_record TO app_runtime;
GRANT UPDATE (published_at, attempts, last_error) ON app.outbox TO app_runtime;
