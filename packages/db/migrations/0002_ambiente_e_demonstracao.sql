-- F0-c: identidade do ambiente, saúde e demonstração com dados fictícios (PRD 23.4; plano R-006, passo 8; ADR 0004).

-- Identidade do ambiente: uma linha só, gravada no provisionamento pelo papel dono e nunca alterada pela aplicação.
-- Trocar a identidade de um banco é recriá-lo: um banco de HML não "vira" produção nem o contrário.
CREATE TABLE app.environment_identity (
  singleton boolean PRIMARY KEY DEFAULT true CHECK (singleton),
  name text NOT NULL CHECK (name IN ('dev', 'hml', 'prod')),
  defined_at timestamptz NOT NULL DEFAULT now()
);
CREATE TRIGGER environment_identity_imutavel BEFORE UPDATE OR DELETE ON app.environment_identity
  FOR EACH ROW EXECUTE FUNCTION app.impedir_alteracao();
GRANT SELECT ON app.environment_identity TO app_runtime;

-- Organização fictícia: só ela entra na demonstração. A marca é definida na criação; a aplicação não tem UPDATE em
-- organization, então uma organização real não vira fictícia depois.
ALTER TABLE app.organization ADD COLUMN fictitious boolean NOT NULL DEFAULT false;

-- Demonstração vigente: aponta a geração atual de dados fictícios. Restaurar cria uma geração nova e troca o ponteiro;
-- movimentos e auditoria das gerações anteriores continuam imutáveis (ENG-026), nada é apagado.
CREATE TABLE app.demo_state (
  singleton boolean PRIMARY KEY DEFAULT true CHECK (singleton),
  -- Não se chama organization_id: por convenção, essa coluna marca organização dona, sempre com RLS forçado.
  current_organization uuid NOT NULL,
  generation integer NOT NULL CHECK (generation >= 1),
  generated_at timestamptz NOT NULL DEFAULT clock_timestamp()
);
GRANT SELECT, INSERT ON app.demo_state TO app_runtime;
GRANT UPDATE (current_organization, generation, generated_at) ON app.demo_state TO app_runtime;
-- demo_state não pertence a uma organização: é um ponteiro global de ambiente de teste. Só ambiente dev/hml o usa,
-- e a função da aplicação confere a identidade antes de escrever.
CREATE FUNCTION app.demo_state_so_fora_de_producao() RETURNS trigger
  LANGUAGE plpgsql
  AS $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM app.environment_identity WHERE name IN ('dev', 'hml')) THEN
    RAISE EXCEPTION 'demonstração só em ambiente dev ou hml identificado' USING ERRCODE = 'P0001';
  END IF;
  RETURN NEW;
END $$;
CREATE TRIGGER demo_state_so_fora_de_producao BEFORE INSERT OR UPDATE ON app.demo_state
  FOR EACH ROW EXECUTE FUNCTION app.demo_state_so_fora_de_producao();

-- Saúde (/saude): a aplicação lê qual foi a última migração aplicada, sem ler o conteúdo das migrações.
GRANT USAGE ON SCHEMA migracao TO app_runtime;
GRANT SELECT (versao, aplicada_em) ON migracao.registro TO app_runtime;

-- Papéis usados pela casca da F0-c e pela demonstração; o que cada um pode fazer é a matriz da aplicação (ADR 0004).
INSERT INTO app.role (code, description) VALUES
  ('almoxarife', 'Almoxarife'),
  ('gerente', 'Gerente da fazenda');
