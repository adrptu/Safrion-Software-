# Contrato F1/CAD-01: fazenda, talhão, limite e culturas (mínimo)

**Versão 3 (30/09), autor Claude.** Não é implementação e não reserva arquivo do repositório.

- **Histórico:** a v1 (be4ac1e4…, preservada ao lado) passou por crítica adversarial em 3 lentes (fidelidade, viabilidade, UX/escopo), com um cético por lente. Saíram 42 achados confirmados, nenhum bloqueante, e 8 refutados (`critica-v1-achados.json`). A v2 aplicou todos.
- A **v3** aplica o retorno consolidado do Codex de 20:11:42Z, com o Gemini `Mmy9arPgI6uZn_APqO6e2Ag`, em três ajustes: conduta executável para os nomes legados (§3), UX do 409 (§2 e §4) e limite vazio ou de área zero (§5). A v2 (0593350a…) está preservada ao lado.
- **Base:** o commit imutável `02c92a51c67d9e01f807709598b2c4a3e6cf3014`, que é o head do PR #32 com a main `0dac3be` incorporada. É a fonte dos caminhos e contratos reaproveitados, e não o HEAD de outro checkout. O PR #32 traz o despacho por `commandType` (`PREPARO`), o limite de corpo por comando (`LIMITES_CORPO`) e a criação com alvo novo na versão 0. Este contrato reaproveita os três e depende do merge dele.
- **Fontes:**
  - V9 é o PRD v3.9 da main, canônico.
  - A v3.11 não tem diferença material nestes cadastros (CD-01, CD-02, FO-01, FO-21, RF-DAT-001/002 e DEC-2609-14 são idênticos).
  - "Plano" é `outputs/plano-execucao-safrion.md` (72b8eccc…).
- "**Decisão técnica**" marca o que não vem de fonte e precisa de revisão (§10).

## 0. Por que agora e o que destrava
- **Etapa 03 do plano:** "Cadastros e mapa da fazenda" (plano:237).
  - A etapa 01 pede o contrato de CRS/SRID e área **antes** das geometrias (plano:235).
  - O aceite da etapa 03 é "Criar/importar uma fazenda, abrir talhão no mapa e na lista, editar sem perder histórico ou contexto" (plano:262).
- **Quem consome depois:**
  - a safra e a ocupação leem fazenda, talhão e área: "ao selecionar talhões, o sistema preenche fazenda e área" (V9:6656);
  - a O.S. e o apontamento leem talhão e fazenda, e o **fuso da fazenda** para a data civil (V9:4507, 6677);
  - o custo em R$/ha lê a área do talhão (V9:8143);
  - os índices (C4) recortam pelo **limite** do talhão.
- **Na main hoje** só existe `app.farm(id, organization_id, name, created_at)` (0001:60-66). Não há talhão, geometria, cultura nem PostGIS nas migrações.

## 1. Entidades
| Entidade | Situação | Campos deste contrato | Fonte |
|---|---|---|---|
| **Fazenda** (`app.farm`) | existe; ganha colunas | `name`; `timezone` (IANA); `status`; `version`; `updated_at` | V9:1670, 2311, 12228; 0001:60-66 |
| **Talhão** (`app.field`, novo) | Inc 1 | `id` uuid gerado pelo cliente; `farm_id` (FK composta); `name`; **`declared_area_ha`**; `status`; `version`; `created_at/by`; `updated_at` | V9:1670, 2480, 4186 |
| **Limite do talhão** (`app.field_boundary`, novo, **imutável**) | Inc 2 | `field_id`; `version`, com `UNIQUE (organization_id, field_id, version)`; `source_text` (GeoJSON recebido); `source_sha256`; `geom geometry(MultiPolygon, 4674)`; `area_calc_ha` numeric(14,6); `transform`; `overlap_note`; `created_at/by` | V9:2481, 6381 |
| **Cultura** (`app.crop`, novo) | Inc 3 | `name`; `status`; `version`; `updated_at` | V9:1683-1691, 12228 |
| **Cultivar** (`app.cultivar`, novo; "Variedade" na tela) | Inc 3 | `crop_id` (FK composta); `name`; `code` (identificador, opcional); `status`; `version`; `updated_at` | V9:2339, 6652, 6657 |

- **Área.** `declared_area_ha` é a **área física declarada** do talhão. Com limite, a **área física de referência** passa a ser a calculada (V9:2416). A "área útil/cultivável" do CD-01 (V9:1670; PARC-02, V9:7135) não entra aqui (§7).
- **Convenções da main em toda tabela nova:**
  - `organization_id` NOT NULL e `UNIQUE (organization_id, id)`;
  - FK sempre composta com a organização;
  - RLS com ENABLE, FORCE e a política `isolamento`;
  - GRANT explícito ao `app_runtime` de SELECT e INSERT, **sem DELETE** (0001:58-76, 283-304).
  - **UPDATE só nestas colunas** (**decisão técnica**):
    - `farm`: `name`, `timezone`, `version`, `updated_at` (a `name_key` é gerada, §3);
    - `field`: `farm_id`, `name`, `declared_area_ha`, `status`, `version`, `updated_at`;
    - `crop`: `name`, `status`, `version`, `updated_at`;
    - `cultivar`: `name`, `code`, `status`, `version`, `updated_at`;
    - `field_boundary`: nenhuma, com o trigger `app.impedir_alteracao` (0001:18-22).
  - O teste que conta as tabelas com `organization_id` (papeis-rls.int.test.ts:37-49) sobe em cada incremento.
- **Fazendas existentes.** A migração do Inc 1 dá **DEFAULT** às colunas novas da fazenda (`timezone` = `America/Sao_Paulo`, `status` = `ativa`, `version` = 1). Assim, a fazenda da demonstração, os INSERTs atuais (ambiente.ts:184-189; helpers de teste) e a HML seguem válidos. Um teste de migração com fazenda anterior, no molde do teste da 0007, confere isso.
- **Não vira entidade neste contrato:**
  - **Parcela:** o plano a põe na etapa 03 (plano:237). Fica para a **fatia seguinte da etapa 03**, a CAD-02.
  - **Ocupação e ciclo:** também estão listados na etapa 03 (plano:237), mas **decisão técnica**: vão **com a safra** (etapa 04). Safra sem ocupação não serve (V9:6650), a ocupação liga cultura e ciclo à parcela (V9:7116, 9956), e a O.S. tem item por parcela (V9:4490). É divergência do plano:237, a decidir pelo Codex, dono do plano. O contrato da etapa 04 herda a ocupação.

## 2. Níveis, estados e ação primária
**Menu (V9:270):** "Cadastros" vira grupo com **Produtos, Fazendas e talhões** (`/cadastros/areas`, V9:1666) e, no Inc 3, **Culturas e cultivares** (`/cadastros/operacoes`, a rota do CD-02, V9:1683-1687, que depois recebe as operações). "Fazendas e talhões" fica ativo também em `/cadastros/fazendas/*`. Cadastros não têm seletor de fazenda no topo (DEC-2609-11, V9:12225).

| Nível | Estado | Ação primária | O que a tela mostra |
|---|---|---|---|
| Listagem `/cadastros/areas` | — | **Novo talhão** | Grupos por fazenda (DEC-2609-14), **inclusive fazenda ativa sem talhão**, como grupo vazio com "Novo talhão nesta fazenda". O cabeçalho do grupo abre o detalhe da fazenda e mostra a contagem e a soma da **área de referência** dos talhões **ativos**. Colunas: Talhão · Área (ha, com a origem: "declarada" ou "calculada") · Limite ("Sem limite" ou "Versão N · data") · Situação. Os filtros de situação e de fazenda ficam na URL. Estado vazio: "Nenhum talhão · Novo talhão". |
| Detalhe da fazenda `/cadastros/fazendas/[id]` | Ativa | **Novo talhão nesta fazenda** | Nome e fuso, editáveis na própria linha. Seção Talhões com a tabela da listagem filtrada. |
| Detalhe do talhão `/cadastros/areas/[id]` | Ativo · Sem limite | Inc 1: **Editar talhão**; a partir do Inc 2: **Importar limite** | Seções Identificação (fazenda, nome, área declarada) e Limite, com a pendência "Sem limite no mapa" explícita, sem coordenada inventada (V9:7130; plano:93). |
| Detalhe do talhão | Ativo · Delimitado | **Editar talhão** | Limite: área calculada (a de referência), área declarada ao lado com a diferença em ha e em %, origem, versão e data. "Nova versão do limite" fica como secundária na seção. Histórico de versões. |
| Detalhe do talhão | Inativo | **Reativar talhão** | Tudo em consulta. "Inativar talhão" fica no menu ⋯ enquanto está ativo. |
| Subnível Importar limite (painel) | Prévia válida | **Gravar limite** | Área calculada, diferença para a declarada, "sem sobreposição" |
| Importar limite | Prévia com sobreposição | **Gravar com justificativa** | Talhões sobrepostos com a área, e o campo Justificativa |
| Importar limite | Prévia inválida | **Escolher outro arquivo** | O motivo em pt-BR e onde corrigir |
| Culturas `/cadastros/operacoes` (Inc 3) | — | **Nova cultura** | Culturas com a contagem de variedades e a situação |
| Detalhe da cultura | Ativa | **Nova variedade** | Tabela de variedades (nome, identificador, situação) |
| Detalhe da cultura | Inativa | **Reativar cultura** | Tudo em consulta |

- **Próximo passo na etapa 04.** Nos dois estados ativos, com ou sem limite, "Editar talhão" dá lugar a "**Planejar safra**", porque planejar não exige limite (V9:7130; plano:86). Até lá, "Editar" é a ação disponível: não existe próximo processo.
- **Conflito de versão (409)** (padrão do CMD-15 e do AGENTS.md). A tela **preserva** os campos digitados e o contexto (painel, filtros, URL) e mostra "Outra pessoa alterou este registro" com a **versão atual** ao lado. A ação primária vira **Reaplicar minhas alterações**, que reenvia com a versão atual só por clique explícito, com chave nova. Nada recarrega apagando o que foi digitado, e nada é reexecutado sozinho.
- **Criação rápida.** "Novo talhão" abre um painel lateral com **3 campos**: Fazenda, Nome e Área (ha).
  - O campo Fazenda tem "**Cadastrar fazenda**", com Nome e Fuso (padrão pré-selecionado), e o painel volta com a fazenda selecionada (AC-72-12, V9:12251).
  - O botão se chama **Criar talhão**. Criar leva ao detalhe **substituindo** a entrada do painel no histórico: o Voltar volta à listagem com os filtros.
- **Papéis.** O PRD põe o CD-01 com o "Gestor de dados e agronomia" (V9:1666), papel que não existe no banco nem na matriz (0002:48-50; matriz.ts:12-17).
  - **Decisão técnica:** o `gerente` executa os `cadastros.*` até existir o papel de agronomia.
  - A leitura `cadastros` continua dos dois papéis.
  - Quem não pode executar vê "**Somente consulta · quem cadastra: Gerente**", sem os botões de ação.

## 3. Regras de valor
- **Nome.** O mecanismo é **decisão técnica**; a conduta com os legados é **decisão do Codex** (20:11Z).
  - **Normalização única no banco:** a função `app.normalizar_nome(text)`, `IMMUTABLE`, aplica `normalize(t, NFC)`. Depois troca toda sequência da classe explícita de espaços por um espaço só e apara as pontas da mesma classe. A classe é `[\t\n\v\f\r \u00a0\u1680\u2000-\u200a\u2028\u2029\u202f\u205f\u3000]`, enumerada para não depender do locale.
  - **Chave de unicidade:** coluna gerada `name_key text GENERATED ALWAYS AS (lower(app.normalizar_nome(name))) STORED` em `farm`, `field`, `crop` e `cultivar`. O índice é único parcial sobre (organização[, fazenda ou cultura], `name_key`) `WHERE status = 'ativo'` (na fazenda, `'ativa'`). A chave vale para **todos** os nomes ativos, legados inclusive.
  - **Tamanho:** `CHECK (char_length(app.normalizar_nome(name)) BETWEEN 1 AND 80)`, **validado** e não `NOT VALID`.
  - **Gravação nova:** o esquema da aplicação normaliza do mesmo jeito antes do hash, mas **quem decide é o banco**. A violação vira 422 `NOME_EM_USO` pelo nome da constraint, e a concorrência nunca gera 500 (CMD-15 §3). Acento diferencia, porque não há `unaccent`.
  - **Fazendas legadas (a única tabela com dados anteriores):**
    - A migração do Inc 1 faz um **preflight** antes de criar o índice e o CHECK. Na mesma transação, procura (a) nome normalizado vazio ou com mais de 80 caracteres e (b) colisão de `name_key` entre fazendas ativas da mesma organização.
    - Se achar algo, **aborta a migração** com `RAISE EXCEPTION`, SQLSTATE próprio e a lista de IDs, **sem nomes**. Nada muda, porque a migração é uma transação só (migrar.ts:21-23). Não se renomeia, mescla nem exclui nenhum legado da regra.
    - Se não achar, cria o índice e o CHECK validados. **A migração nunca termina sem a proteção.**
    - O nome gravado não é reescrito; só a chave é derivada.
    - A correção de um conflito real, que hoje não existe (a demonstração tem uma fazenda só, ambiente.ts:184-189), é uma decisão de dados fora da migração.
  - **Ensaiado** num PostgreSQL 17.10 local descartável (`prova-nome-pg17/`), sobre o mecanismo e não sobre a migração real:
    - colisão legada "Boa Vista" × " boa\u00a0 vista" → abortou com SF001, os dois IDs e nenhuma coluna nova;
    - 81 caracteres → abortou;
    - legados limpos migraram. Depois, "BOA VISTA", "Café" em NFD e "\u2003Boa\u3000Vista\u00a0" deram 23505 no índice, e 81 caracteres novos deram 23514 no CHECK.
- **Área declarada:**
  - hectare decimal **maior que zero**, com **até 8 dígitos inteiros e até 6 decimais** depois da forma canônica (V9:4186, 6 casas no cálculo e 2 na tela);
  - fora disso, 400 no campo, sem gravar;
  - no `data`, vai como **texto** canônico ("204.5"), porque o hash canônico recusa número decimal (canonico.ts:21-27);
  - a tela aceita pt-BR ("204,5"; "1.204,50");
  - **decisão técnica:** "1.204" é **recusado como ambíguo** (mil e duzentos ha ou 1,204 ha digitado com ponto), com a instrução "Use vírgula nos decimais: 1204 ou 1,204". A regra é a mesma do painel do protótipo (parseDecimal), porque errar a área por mil vezes é o dano.
- **Fuso** (**decisão técnica**): nome IANA válido no runtime; padrão `America/Sao_Paulo`, com as zonas do Brasil no topo. Mudar o fuso não reescreve instantes gravados (V9:4507, 6677).
- **Editar talhão** (`nome`, `área`, **`fazenda`**):
  - permitido enquanto nada o consome, até a etapa 04;
  - trocar a fazenda confere de novo a unicidade do nome e a sobreposição, se houver limite;
  - a auditoria guarda o antes e o depois;
  - **restrição declarada para a etapa 04:** quando existirem ocupação ou O.S., mudar a área ou a fazenda passa a criar versão e preserva o valor usado antes (RN-005, V9:207; RF-DAT-002, V9:2481).
- **Situação:**
  - inativar bloqueia novos usos e conserva a consulta (RF-DAT-001, V9:2480);
  - **não há exclusão** (**decisão técnica**, apoiada no grant sem DELETE, 0001:295-304, e em DEC-2609-14, V9:12228). Talhão criado errado se corrige editando ou inativando.
  - **Recusas por alvo inativo:**
    - `editar-talhao` e `importar-limite-talhao` em talhão inativo → 422 `TALHAO_INATIVO`;
    - `criar-cultivar` em cultura inativa, ou reativar variedade de cultura inativa → 422 `CULTURA_INATIVA`;
    - reativar com o nome já tomado → 422 `NOME_EM_USO`;
    - reativar talhão com limite repete a conferência de sobreposição (§5).
  - As **listas de seleção** omitem os inativos (§6). As listagens de cadastro mostram os inativos pelo filtro.
- **Criação com id do cliente:** qualquer 23505 fora do índice de nome (id já usado, inclusive por outra organização, porque a PK não passa pelo RLS) e qualquer 23503 de FK composta viram 422 `ALVO_INVALIDO`, com a mesma resposta de inexistente (CMD-15 §3).

## 4. Comandos e envelope
| commandType | Origem | Alvo | `data` | Inc |
|---|---|---|---|---|
| `cadastros.criar-fazenda` | CD-01 "Cadastrar" (V9:1672); AC-72-12 | `farm` novo, versão 0 | `{nome, fuso}` | 1 |
| `cadastros.editar-fazenda` | CD-01 | `farm`, versão N | `{nome?, fuso?}`, com ao menos um | 1 |
| `cadastros.criar-talhao` | CD-01; FO-01 (V9:2311) | `field` novo, versão 0 | `{fazenda, nome, areaDeclaradaHa}` | 1 |
| `cadastros.editar-talhao` | CD-01 | `field`, versão N | `{fazenda?, nome?, areaDeclaradaHa?}`, com ao menos um | 1 |
| `cadastros.alterar-situacao-talhao` | RF-DAT-001 | `field`, versão N | `{situacao, justificativaSobreposicao?}` | 1 |
| `cadastros.importar-limite-talhao` | CD-01 "Importar geometrias" (V9:1672); FO-40 (V9:2358); M-10 (V9:10196) | `field`, versão N | `{geojson, nomeArquivo?, justificativaSobreposicao?}` | 2 |
| `cadastros.criar-cultura` / `editar-cultura` / `alterar-situacao-cultura` | CD-02 (V9:1683-1691) | `crop` | `{nome}` / `{nome}` / `{situacao}` | 3 |
| `cadastros.criar-cultivar` / `editar-cultivar` / `alterar-situacao-cultivar` | V9:2339, 6657 | `cultivar` | `{cultura, nome, codigo?}` / `{nome?, codigo?}` / `{situacao}` | 3 |

- **Envelope:** `executarComando` sem mudança. Organização e ator vêm da sessão.
  - **Criação:** `target.id` uuid gerado pelo cliente e `expectedVersion = 0`; o efeito devolve a versão 1.
  - **Edição, situação e limite:** exigem a versão atual, ou dão 409 (tratado na tela como na §2), e **sobem a versão da entidade** de N para N+1 na mesma transação. **Importar limite também sobe `field.version`.** Recibo e outbox saem em N+1, o que respeita o UNIQUE da outbox (0001:261, 272), e a versão do limite é `max+1` sob a trava da linha do talhão.
  - Cada mudança emite outbox com `entity_version` (`farm.created`, `field.updated`, `field.boundary_imported`…) e auditoria com antes e depois.
- **Na rota:**
  - tipo de alvo errado, versão diferente de 0 na criação ou `data` fora do esquema → 400, sem gravar (padrão de `prepararRecebimento`);
  - regra de negócio → 422 registrado dentro do efeito. O **recibo da rejeição** leva o `reasonCode` e, no `nextAction`, o motivo em pt-BR. Detalhe estruturado, como a lista de talhões sobrepostos, só na prévia (§5).
  - **`LIMITES_CORPO`:** 16 KiB para todos, menos `importar-limite-talhao`, que tem **512 KiB**.
- **Idempotência:** mesma chave e mesmo conteúdo devolvem o recibo com `alreadyReceived`. Mesma chave com outro conteúdo dá `IDEMPOTENCY_KEY_REUSED` (comando.ts:328-343).
- **Autorização:** matriz com os `cadastros.*` para o `gerente` (§2). O RLS é a segunda barreira.

## 5. Limite do talhão: CRS, área e validação (Inc 2; exigido antes das geometrias, plano:235)
Tudo nesta seção é **decisão técnica** sobre a regra do PRD: guardar CRS/SRID e a transformação, usar método geodésico, nunca tratar graus como metros e preservar original e derivada (V9:6381).

**Entrada.** GeoJSON (RFC 7946, lon/lat WGS 84) como **texto** em `data.geojson`.
- **Tipo:** só **objeto geometria** Polygon ou MultiPolygon.
  - Feature ou FeatureCollection com **um único** polígono é extraído **pela tela** antes de enviar.
  - Mais de um polígono na coleção é recusado na tela com "Um arquivo por talhão".
- **Membro `crs`:** só CRS84 ou EPSG:4326, e é removido antes do parse. Outro CRS dá 400 "Converta para WGS 84 (EPSG:4326)".
- **Esquema da rota (400, sem gravar):**
  - tipo;
  - anéis fechados, com pelo menos 4 posições;
  - números finitos;
  - lon entre ±180 e lat entre ±90;
  - no máximo **20.000 vértices** — acima disso, **422 `LIMITE_GRANDE_DEMAIS`** com a instrução de simplificar. Corpo acima de 512 KiB dá **413**.
- **Altitude:** descartada.
- **Outros formatos:** KML, Shapefile, GeoPackage e CSV ficam fora (V9:6379, "quando implementados").

**Armazenamento.**
- O original como recebido fica em `source_text`. O **servidor** calcula `source_sha256` sobre os bytes UTF-8 desse texto, e o hash do navegador não entra.
- O derivado é `ST_Transform(ST_SetSRID(ST_Multi(ST_Force2D(ST_GeomFromGeoJSON(texto))), 4326), 4674)`, em **SIRGAS 2000**, o referencial oficial do Brasil.
- `transform` registra "EPSG:4326→EPSG:4674" e as versões do PostGIS e do PROJ.
- **Mesmo `source_sha256` do limite vigente:** 422 `LIMITE_SEM_MUDANCA`, sem criar versão (RF-DAT-007, V9:2486).

**Erro de geometria no SQL.** Falha de parse, transformação ou INSERT da geometria vira **422 `LIMITE_INVALIDO`** no efeito e na prévia, **nunca 5xx nem "repita"**.

**Área.**
- `ST_Area(geom::geography)` em m², dividido por 10.000, em `numeric(14,6)`. Nunca área planar em graus.
- Com limite, a calculada vira a área física de referência (V9:2416), e a declarada fica visível ao lado com a diferença, **sem tolerância inventada**.

**Vazio ou área zero** (retorno do Codex, 20:11Z). `ST_IsEmpty(geom)`, ou `area_calc_ha` = 0 depois do arredondamento para 6 casas, dá **422 `LIMITE_INVALIDO`**, na prévia e no efeito, antes de gravar.

**Validade.** `ST_IsValid` é obrigatório. Limite inválido dá 422 `LIMITE_INVALIDO`, com o motivo em pt-BR a partir de `ST_IsValidReason`. Sem `ST_MakeValid` automático.

**Sobreposição** ("sobreposições justificadas", FO-01, V9:2311).
- **Conta:** a interseção de área positiva entre o limite novo e o **limite vigente** de outro talhão **ativo** da organização. Borda encostada não conta, e não há tolerância inventada.
- **Sem justificativa:** 422 `SOBREPOSICAO_SEM_JUSTIFICATIVA`.
- **Concorrência:** as importações e reativações da organização são **serializadas** com `pg_advisory_xact_lock`, para que duas importações de vizinhos não gravem sobreposição sem se enxergar.
- **Reativação** de talhão com limite repete a conferência.

**Prévia antes de gravar (M-10, V9:10196).**
- **Rota:** `POST /api/v1/cadastros/limites/previa`, **sem efeito**.
- **Entrada:** o mesmo esquema de `importar-limite-talhao`, com o id do talhão.
- **Recusas da rota de comandos:** origem, JSON, sessão e permissão de executar `importar-limite-talhao`.
- **Limite próprio:** 512 KiB, lido antes do parse.
- **Leitura:** em `emOrganizacao`, sem gravar, com `Cache-Control: no-store`.
- **Devolve:** área calculada, diferença, validade e a **lista estruturada** de sobreposições.
- **A tela sempre mostra a prévia** antes de "Gravar limite", e o comando **valida de novo**.

**Extensão PostGIS.**
- O `migrator` não é superusuário (papeis.ts:51), então `CREATE EXTENSION postgis` fica fora dele.
- **HML e produção:** o **preparo**, com a credencial de administração (`preparo.ts`; no Cloud SQL, `cloudsqlsuperuser`, que não é superusuário), cria a extensão no banco da aplicação **antes** das migrações.
- **Testes:** o `global-setup` cria a extensão no **template1**. Assim, todo banco de teste criado por `criarBanco` (test/ambiente.ts:27) já nasce com ela.
- **Migração do Inc 2:** só confere que a extensão existe e para com uma mensagem clara se faltar.
- **Limite conhecido:** a partir dessa migração, sem PostGIS **nenhum** teste de integração roda no PostgreSQL local sem Docker, só na CI.
- **Antes de o Inc 2 ir para a HML (pendência registrada, porque a CI usa superusuário real e não prova isso):** executar o preparo na HML, com admin sem superusuário e banco com dono `migrator`, criar a extensão e registrar `postgis_full_version()`.

**Leitura para o mapa.** `listarLimites(fazenda)` devolve o GeoJSON em **4326**, o que os mapas web esperam, e simplificado para exibição. A geometria gravada não é simplificada. A meta de p95 do mapa (V9:5656) é da fatia do mapa (§7).

## 6. Leituras (dentro de `emOrganizacao`; outra organização recebe a mesma resposta de inexistente)
- **`listarTalhoes({fazenda?, situacao?})`:**
  - id, nome, fazenda {id, nome};
  - **área de referência** e a **origem** dela (calculada se houver limite; senão declarada);
  - área declarada;
  - limite {versão, data} ou "sem";
  - situação e versão.
- **`obterTalhao(id)`:** os mesmos campos, mais o histórico de limites (Inc 2).
- **`listarFazendas()` e `obterFazenda(id)`:** id, nome, fuso, situação, versão, contagem de talhões ativos e soma da área de referência deles. A soma não é a "área da fazenda", campo da DEC-2609-14 que fica para depois (§7).
- **Listas de seleção** (sem inativos):
  - `opcoesFazenda()`;
  - `opcoesCultura()`;
  - **`opcoesVariedade(cultura)`**, filtrada pela cultura e com nome e identificador (V9:6657). Omite variedade inativa e as de cultura inativa. É a leitura que a etapa 04 vai consumir.
- **`listarCulturas()` e `obterCultura(id)`** (Inc 3): a cultura com as variedades.

## 7. Fica fora deste contrato, com motivo e destino
| Item | Motivo | Destino |
|---|---|---|
| **Parcela** | Divisão com linhagem e soma contra a área útil (PARC-01/02) é uma fatia própria | **Etapa 03, fatia CAD-02** (plano:237) |
| Ocupação e ciclo | Ligam cultura e ciclo à parcela e à safra | Com a safra, na etapa 04 (**decisão técnica**, §1) |
| Área útil/cultivável do talhão | É a base da PARC-02 | CAD-02, com as parcelas |
| **Aceite no mapa: selecionar o talhão, abrir o detalhe e voltar com o contexto** (plano:93 (1)-(2), plano:262) | Exige a tela do mapa (IN-04) | **Fatia do mapa da etapa 03, logo depois do Inc 2**, com autoria a definir pelo Codex. O aceite de mapa do plano:31 para o talhão fecha nela, com a meta de p95 ≤ 3 s e 500 geometrias (V9:5656) |
| Desenhar, dividir e unir no mapa | Exigem o mapa e as parcelas | Fatia do mapa e CAD-02 |
| Importação em lote (FO-40 completo), KML, Shapefile e CSV | O GeoJSON único cobre a primeira jornada | Etapa 03, depois deste contrato |
| Biblioteca global de culturas e RNC | Licença e mecanismo por homologar (V9:8926) | Etapa 03, depois deste contrato |
| Fazenda: área, município/UF, posse, CAR/matrícula, documento; empresa | Cadastro progressivo: documento pendente só bloqueia o processo que o exige (V9:1674). O esquema não tem empresa | Com o processo que os exigir |
| Inativar fazenda | Depende dos locais de estoque (0001:68-76) | Com a regra dos locais |
| Papel de agronomia ou gestor de dados | Não existe no banco nem na matriz | Etapa 04 |
| Pessoas, equipes, ativos e parceiros | Outros itens da etapa 03, com contrato próprio | Etapa 03 |

## 8. Incrementos e arquivos (proposta; a reserva e o número das migrações ficam para a reserva, pela ordem real de merge)
Cada incremento é um PR a partir da main, depois do PR #32.
- **Inc 1 (fazenda e talhão).** Dois autores, em arquivos distintos. O ponto de encontro são as assinaturas da §6 exportadas por `web.ts` e os `commandType` da §4.
  - **Claude — dados, comandos e integração:**
    - a migração nova (com `app.normalizar_nome`, as colunas geradas e o preflight);
    - `packages/db/src/cadastros-agricolas.ts` (efeitos e leituras) e a exportação em `packages/db/src/web.ts`;
    - `packages/contracts/src/cadastros.ts` (esquemas estritos);
    - em `apps/web/src`, só os aditivos de `rotas/comandos.ts` (`PREPARO` e `LIMITES_CORPO`) e de `autorizacao/matriz.ts`;
    - testes: `packages/db/test` (integração, migração com os legados e contagem do RLS) e `apps/web/test` (matriz e rota).
  - **Codex — UI, quando apta:**
    - as telas `(app)/cadastros/areas`, `areas/[talhao]` e `fazendas/[fazenda]`, o grupo Cadastros no `layout.tsx` e a UX do 409;
    - o E2E da jornada.
  - **Reaproveita de `02c92a51`:** `executarComando` (packages/db/src/comando.ts), o padrão `PREPARO` e `LIMITES_CORPO` e a criação na versão 0 (`prepararRecebimento`, apps/web/src/rotas/comandos.ts), `emOrganizacao` (packages/db/src/sessao.ts) e o teste de migração da 0007 como molde.
- **Inc 2 (limite):**
  - migração nova, o efeito de importação e a rota de prévia;
  - a seção e o painel do limite;
  - `preparo.ts` (extensão) e `packages/db/test/global-setup.ts` (template1).
- **Inc 3 (culturas):** migração nova, efeitos e leituras, e as telas em `/cadastros/operacoes`.
- **Ordem:** o **Inc 3 depende só do Inc 1** e pode ir antes do Inc 2, se a extensão atrasar.

## 9. Aceite
**Primeira jornada (Inc 1; AC-72-12):**
1. O gerente abre `/cadastros/areas?situacao=ativo` e clica em **Novo talhão**.
2. No campo Fazenda, escolhe **Cadastrar fazenda**, preenche "Fazenda Boa Vista" e mantém o fuso padrão.
3. O painel volta com a fazenda selecionada. Ele preenche "T1" e "204".
4. **Criar talhão** abre o detalhe: "T1 · Fazenda Boa Vista · 204,00 ha (declarada) · Ativo · Sem limite no mapa".
5. **Voltar** leva de novo a `/cadastros/areas?situacao=ativo`, sem reabrir o painel, com o grupo "Fazenda Boa Vista · 1 talhão · 204,00 ha".
6. O almoxarife abre as mesmas telas e vê "Somente consulta · quem cadastra: Gerente", sem "Novo talhão".

**Domínio:**
- parse da área pt-BR: "204", "204,5" e "1.204,50" viram a forma canônica; "1.204" é recusado com a instrução; mais de 6 decimais ou mais de 8 dígitos inteiros dá 400;
- normalização do nome (NFC, espaço Unicode, espaços colapsados);
- fuso válido.

**Integração com PostgreSQL real, `app_runtime` sem BYPASSRLS:**
- **Criação e idempotência:**
  - criar fazenda e talhão → confirmado, versão 1, outbox e auditoria;
  - repetir a chave → `alreadyReceived`, sem duplicar;
  - mesma chave com outro conteúdo → `IDEMPOTENCY_KEY_REUSED`.
- **Recusas:**
  - nome ativo repetido na mesma fazenda → 422 `NOME_EM_USO`, inclusive com duas criações concorrentes (uma confirma, a outra 422, nunca 500);
  - id já usado por outra organização → 422 `ALVO_INVALIDO`, com a resposta de inexistente;
  - versão velha → 409;
  - editar talhão inativo → 422 `TALHAO_INATIVO`;
  - reativar com o nome tomado → 422 `NOME_EM_USO`.
- **Aceitos:**
  - o mesmo nome em outra fazenda;
  - editar a fazenda do talhão, com o nome conferido de novo.
- **Migração com legados** (teste mínimo da conduta; sai de um banco na migração anterior):
  - (i) duas fazendas ativas na mesma organização, "Boa Vista" e " boa  vista" → a migração **aborta** com o SQLSTATE próprio e os **dois IDs**, e o esquema continua na migração anterior, sem tabela, coluna ou índice novo;
  - (ii) uma fazenda com o nome normalizado de 81 caracteres → aborta com o ID;
  - (iii) só legados limpos, inclusive o mesmo nome em **outra** organização → migra, ficam fuso padrão, ativa e versão 1, e a `name_key` é gerada; em seguida, criar uma fazenda "BOA VISTA" na mesma organização → 422 `NOME_EM_USO`.
- **Permissões:** sem DELETE; UPDATE só nas colunas da §1; a contagem de tabelas do RLS atualizada.

**Web:**
- matriz: o gerente executa `cadastros.*` e o almoxarife não, e os dois leem;
- alvo de tipo errado, criação com versão diferente de 0 ou área fora do esquema → 400, sem gravar;
- corpo acima do limite → 413;
- **menu:** grupo Cadastros com Produtos e Fazendas e talhões, e o item ativo em `/cadastros/fazendas/*`.

**E2E no desktop e no celular:** a jornada acima, recarregar com a URL preservada, estado vazio, a fazenda sem talhão como grupo vazio e o **409**: editar com uma versão velha preserva os campos, mostra a versão atual, e só "Reaplicar minhas alterações" reenvia.

**Desempenho** (orçamentos do PRD §29.3, V9:5644-5652):
- `criar-talhao` com p95 ≤ 600 ms e `listarTalhoes` com p95 ≤ 300 ms;
- medidos pelo **ensaio local delimitado** do CMD-15 §9.1 (gerador, regras de veredito e limites), com um perfil de dados declarado: 5 fazendas e 200 talhões;
- a medição **em HML** fica como pendência registrada, sem travar o merge;
- WCAG 2.2 AA nas telas novas.

**Inc 2:**
- **Área calculada:** fixture com área geodésica calculada **fora** do PostGIS, por uma biblioteca independente, com a tolerância declarada no teste.
- **Recusas:**
  - GeoJSON quebrado → 400 no esquema, ou 422 `LIMITE_INVALIDO` quando o erro vem do SQL, nunca 5xx;
  - geometria vazia ou com área calculada 0 depois do arredondamento → 422 `LIMITE_INVALIDO`, na prévia e no comando;
  - autointerseção → 422 `LIMITE_INVALIDO` com o motivo;
  - mais de 20.000 vértices → 422 `LIMITE_GRANDE_DEMAIS`;
  - acima de 512 KiB → 413;
  - sobreposição sem justificativa → 422, e com justificativa grava;
  - mesmo arquivo com outra chave → 422 `LIMITE_SEM_MUDANCA`.
- **Versões:**
  - mesma chave → `alreadyReceived`;
  - a importação sobe `field.version`;
  - duas importações concorrentes na mesma versão → uma confirma e a outra dá 409;
  - a nova versão preserva a anterior;
  - o limite é imutável (UPDATE recusado pelo trigger).
- **Prévia:** não grava nada, conferido pelo estado persistido antes e depois.
- **Leitura:** devolve 4326.
- **E2E:** arquivo → prévia → Gravar limite → o detalhe mostra a área calculada, a diferença e a versão 1.

**Inc 3:**
- criar cultura e variedade (com identificador opcional);
- nome duplicado → 422;
- `opcoesVariedade(cultura)` filtra pela cultura e omite as inativas;
- criar variedade em cultura inativa → 422 `CULTURA_INATIVA`.

## 10. Decisões técnicas para revisão
1. O gerente executa os cadastros até existir o papel de agronomia.
2. Nome: `app.normalizar_nome` (NFC e classe de espaços enumerada), `name_key` gerada, índice parcial entre ativos, CHECK de 1 a 80 validado, acento diferenciando. **Legados: o preflight aborta sem renomear** (conduta decidida pelo Codex).
3. Fuso IANA, com padrão `America/Sao_Paulo`; DEFAULTs na fazenda existente.
4. "1.204" é recusado como ambíguo.
5. Sem exclusão; editar a fazenda do talhão é permitido enquanto nada o consome.
6. SIRGAS 2000 (4674) no armazenamento, área geodésica, original preservado e leitura em 4326.
7. Só GeoJSON, como objeto geometria, até 512 KiB e 20.000 vértices; Feature com um polígono é extraído pela tela.
8. Sobreposição de área positiva exige justificativa; importações serializadas por organização.
9. Com limite, a área física de referência passa a ser a calculada.
10. A extensão é criada pelo preparo e pelo template1 dos testes, nunca pelo `migrator`.
11. Ocupação e ciclo vão com a safra (etapa 04), divergindo do plano:237, que é decisão do Codex. A parcela fica na etapa 03 (CAD-02).
12. As culturas ficam em `/cadastros/operacoes`, a rota do CD-02. Na tela, "Variedade"; no código, `cultivar`.
13. Três incrementos; o Inc 3 depende só do Inc 1; o número das migrações sai na reserva.

## 11. Adendos da implementação (Inc 1, 30/09)
Fonte: a v3 aceita (SHA-256 `be5614c022aaf821af252c80f01286c730e8ce97d0fa43e22851c877003ea281`, preservada fora do repositório em `work/fontes-claude/cadastros-agricolas/`). Os itens abaixo não mudam as seções anteriores; registram o que a implementação acrescentou e foi aceito pelo Codex.
- **`SITUACAO_INALTERADA` (422):** pedir a situação que o talhão já tem é recusado sem mudar a versão (aceito pelo Codex às 20:38Z).
- **Nome com U+0000:** o esquema recusa (`NOME_COM_NUL`, 400 antes do envelope, sem recibo nem efeito). O PostgreSQL não aceita NUL em texto (achado P2 do Codex às 20:53Z).
- **Motivo da recusa:** o recibo de toda recusa leva o texto em pt-BR no `nextAction`, que é o que a tela mostra (§4).
- **Preflight dos nomes legados:** o FORCE do RLS vale também para o dono. A migração retira o FORCE da fazenda só durante a conferência e o recoloca na mesma transação.
- **Reaplicar depois do 409:** a tela envia só os campos que diferem dos valores da abertura (achado P1 do Claude na revisão da UI, corrigido pelo Codex no PR #33).
- **Pendências registradas fora deste incremento:** NUL na `idempotencyKey` do envelope comum; erros de classe 22 do PostgreSQL devolvidos como falha transitória; roteiro de upgrade para conferir `name_key` e os índices de nome quando a versão do Unicode ou da collation mudar.

