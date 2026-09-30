-- F1/CAD-01, incremento 1: fazenda com fuso, situação e versão; talhão com área física declarada (contrato CAD-01 v3,
-- §1, §3 e §4). Aplicada pelo migrator; app_runtime lê, insere e atualiza só as colunas dos comandos de cadastro.
-- Sem geometria (incremento 2) e sem cultura (incremento 3).

-- Nome ------------------------------------------------------------------------------------------------------------
-- Uma normalização só, no banco: NFC e a classe de espaços enumerada (não depende do locale) colapsada em um espaço e
-- aparada nas pontas. É a mesma de normalizarNome em @safrion/contracts; quem decide a unicidade é o índice abaixo.
CREATE FUNCTION app.normalizar_nome(t text) RETURNS text
  LANGUAGE sql IMMUTABLE STRICT PARALLEL SAFE SET search_path = pg_catalog, pg_temp
  AS $$
    SELECT regexp_replace(
             regexp_replace(normalize(t, NFC),
                            '[\t\n\v\f\r \u00a0\u1680\u2000-\u200a\u2028\u2029\u202f\u205f\u3000]+', ' ', 'g'),
             '^ | $', '', 'g')
  $$;
-- A coluna gerada e o CHECK rodam a função com os privilégios de quem grava.
REVOKE ALL ON FUNCTION app.normalizar_nome(text) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION app.normalizar_nome(text) TO app_runtime;

-- Fazenda -----------------------------------------------------------------------------------------------------------
-- As fazendas existentes (a da demonstração e as da HML) ficam ativas, na versão 1 e com o fuso padrão; os INSERTs
-- atuais seguem válidos pelos DEFAULTs.
ALTER TABLE app.farm
  ADD COLUMN timezone text NOT NULL DEFAULT 'America/Sao_Paulo' CHECK (btrim(timezone) <> ''),
  ADD COLUMN status text NOT NULL DEFAULT 'ativa' CHECK (status IN ('ativa')),
  ADD COLUMN version bigint NOT NULL DEFAULT 1 CHECK (version >= 1),
  ADD COLUMN updated_at timestamptz;

-- Preflight dos nomes legados (decisão do Codex, 30/09 20:11Z): com nome fora do tamanho ou colisão entre fazendas
-- ativas da mesma organização, a migração para inteira, com os IDs e sem os nomes. Nada é renomeado, mesclado ou
-- excluído da regra, e a migração nunca termina sem a proteção.
DO $$
DECLARE
  fora text;
  colisoes text;
BEGIN
  SELECT string_agg(id::text, ',' ORDER BY id) INTO fora
    FROM app.farm
   WHERE char_length(app.normalizar_nome(name)) NOT BETWEEN 1 AND 80;
  SELECT string_agg(ids, '; ') INTO colisoes
    FROM (SELECT string_agg(id::text, ',' ORDER BY id) AS ids
            FROM app.farm
           WHERE status = 'ativa'
           GROUP BY organization_id, lower(app.normalizar_nome(name))
          HAVING count(*) > 1) g;
  IF fora IS NOT NULL OR colisoes IS NOT NULL THEN
    RAISE EXCEPTION 'nomes de fazenda existentes fora da regra de cadastro'
      USING ERRCODE = 'SF001',
            DETAIL = format('fora do tamanho: %s; colisões: %s', coalesce(fora, '-'), coalesce(colisoes, '-')),
            HINT = 'Corrija os nomes pela operação de dados antes de aplicar a 0008; a migração não altera legados.';
  END IF;
END $$;

ALTER TABLE app.farm
  ADD COLUMN name_key text GENERATED ALWAYS AS (lower(app.normalizar_nome(name))) STORED,
  ADD CONSTRAINT farm_nome_tamanho CHECK (char_length(app.normalizar_nome(name)) BETWEEN 1 AND 80);
CREATE UNIQUE INDEX farm_nome_ativo ON app.farm (organization_id, name_key) WHERE status = 'ativa';

-- Talhão --------------------------------------------------------------------------------------------------------------
-- Área física declarada em ha, com 6 casas (PRD 4186); o limite do incremento 2 passa a dar a área de referência.
-- O id vem do cliente (alvo novo na versão 0); a PK é global, então id repetido de outra organização é recusado pelo
-- efeito com a resposta de inexistente.
CREATE TABLE app.field (
  id uuid PRIMARY KEY,
  organization_id uuid NOT NULL,
  farm_id uuid NOT NULL,
  name text NOT NULL,
  name_key text GENERATED ALWAYS AS (lower(app.normalizar_nome(name))) STORED,
  declared_area_ha numeric(14, 6) NOT NULL CHECK (declared_area_ha > 0),
  status text NOT NULL DEFAULT 'ativo' CHECK (status IN ('ativo', 'inativo')),
  version bigint NOT NULL DEFAULT 1 CHECK (version >= 1),
  created_at timestamptz NOT NULL DEFAULT now(),
  created_by uuid NOT NULL,
  updated_at timestamptz,
  UNIQUE (organization_id, id),
  CONSTRAINT field_nome_tamanho CHECK (char_length(app.normalizar_nome(name)) BETWEEN 1 AND 80),
  FOREIGN KEY (organization_id, farm_id) REFERENCES app.farm (organization_id, id),
  FOREIGN KEY (organization_id, created_by) REFERENCES app.app_user (organization_id, id)
);
CREATE UNIQUE INDEX field_nome_ativo ON app.field (organization_id, farm_id, name_key) WHERE status = 'ativo';
CREATE INDEX field_fazenda ON app.field (organization_id, farm_id);

ALTER TABLE app.field ENABLE ROW LEVEL SECURITY;
ALTER TABLE app.field FORCE ROW LEVEL SECURITY;
CREATE POLICY isolamento ON app.field
  USING (organization_id = app.organizacao_atual()) WITH CHECK (organization_id = app.organizacao_atual());

-- app_runtime: ler e inserir; UPDATE só nas colunas dos comandos (contrato CAD-01 §1); nada de DELETE.
GRANT SELECT, INSERT ON app.field TO app_runtime;
GRANT UPDATE (farm_id, name, declared_area_ha, status, version, updated_at) ON app.field TO app_runtime;
GRANT UPDATE (name, timezone, version, updated_at) ON app.farm TO app_runtime;
