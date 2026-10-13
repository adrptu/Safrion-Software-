# CADUX-0 · Inventário dos Cadastros como estão hoje

Pedido do proprietário (Adrianus, 09/10/2026): "os cadastros ainda não estão intuitivos com melhor UX e UI. faça algo mais prático e intuitivo. E use seleção para abrir detalhes... como clicar na fazenda e abrir talhões cadastrados nela na tela."

Esta etapa só observa e mede. Nenhum código foi alterado. Tudo o que está marcado **executado** foi rodado no Chrome headless nesta worktree, com dados sintéticos. O que está marcado **especificado** é o texto do PRD.

```text
ID / resultado útil / persona: CADUX-0 · retrato medido das 7 telas de Cadastros, base do redesenho · Ana (gestora e RT), gestor de dados, Rui (almoxarife)
Requisitos do PRD e fora do escopo: PRD v3.9 4.2, 4.3, cap. 5 (CD-01 a CD-07), cap. 19; v3.10/3.11 em revisão: 74 (DS-40, 41, 57, 58, 88) e 75.4 (UXP-01 a 03). Fora: código, benchmark (UXP-01, fica no desenho), regras de domínio
Autor / revisor / integrador: Claude / Codex / Claude (o commit sai junto com o desenho)
Base: claude/v44-cadux @ 8356a07. Os arquivos de Cadastros (areas/cad_*.py, cadastros.py, engine.py, g2lib.js, ui37.py) estão iguais aos de claude/v44-tabelas-r @ 300835d (git diff vazio) · arquivo: docs/cadastros-ux/INVENTARIO.md
Aceite e comando de verificação: seção 1 (build, render, probe1 a probe6)
Estado / impedimento / próximo passo: executado · sem impedimento · próximo passo: o desenho, nesta pasta, sobre a TABELAS-FOCO e a DS
```

**Abreviações.** `gen37/` = `/home/user/sp-cadux/tools/prototipo/v37/gen37/`. `cap/` = `/tmp/claude-0/-home-user-Safrion-Software-/65558514-68d9-57f5-9da3-513cd6735cdc/scratchpad/cadux/antes/` (capturas). PRD v3.9 = `/home/user/Safrion-Software-/docs/PRD.md` (vigente). PRD v3.11 = `scratchpad/parecer/PRD-v3.11.md` (em revisão). PADRÃO = `tools/prototipo/v37/specs/padrao-comandos-v3-prompt.md`. Severidade: PRD 22.1 (S1 a S4). Prioridade: P0 a P3 (AGENTS §3).

---

## 0. Resumo

1. **Selecionar não abre o que está dentro.** O cartão da fazenda abre o formulário de edição da fazenda (12 campos), não os talhões dela. A linha da fazenda na árvore de talhões não faz nada. A busca "Santa Rita" devolve **0 de 32**: aparece o cabeçalho "Santa Rita · 8 talhões ativos" e nenhum talhão (I01, I02, I24). O mesmo acontece com equipe → pessoas, grupo → itens, grupo → fornecedores e máquina → implementos (I04 a I07).
2. **Ver é editar.** Toda linha e todo cartão abrem um formulário editável de 460 px, com "Salvar" verde já ativo (`gen37/g2lib.js:111`). O detalhe, quando existe (só o do talhão), fica atrás de um botão dentro do formulário. A ordem é Lista → Formulário → Detalhe, o contrário do master-detail (I09, I10).
3. **O próximo passo some.** A 1440 × 1000, a coluna Situação, que leva o verbo, fica fora da caixa em 5 das 7 telas. A 390, só 2 colunas aparecem e a Situação nunca aparece sem rolar de lado. O menu lateral ocupa 68 px fixos (I29, I35).
4. **A mesma pendência aparece até 4 vezes na tela:** cabeçalho, ponto na aba, cartão da faixa e chip com verbo na linha. O mesmo comando aparece 2 vezes para o mesmo registro (I14 a I16).
5. Medidas das 7 tarefas comuns (seção 4): 2 a 5 cliques pelo caminho mais curto, que nem sempre é o que a pessoa tenta. O caminho intuitivo falha em 4 tarefas: fazenda → talhões, equipe → pessoas, produto → registro e máquina → implementos.

Há também o que funciona e precisa ficar (seção 6): validações no lugar, inativar em vez de excluir, unidade na célula, faixa com verbo, "Cadastrar fazenda…" sem perder o talhão em preenchimento e o detalhe do talhão com parcelas e versões.

---

## 1. Como medi (executado)

```bash
cd /home/user/sp-cadux/tools/prototipo/v37/gen37
SAFRION_DADOS=sintetico python3 build.py          # 140 artboards · menu vigente: 45 · ocultos: 95
SAFRION_DADOS=sintetico python3 montar_render.py  # _render montado: 140 páginas + 20 arquivos (Lagoa Grande = camada sintética)
cd <scratchpad>/cadux
CHROME_BIN=/tmp/cloudchrome/chrome flock /tmp/cdpH.lock env CDP_GL=1 SAFRION_DADOS=sintetico timeout 900 python3 probe1.py   # capturas e estrutura (info.json)
… probe2.py   # as 7 tarefas, cliques e digitação (tarefas.json)
… probe3.py … probe6.py   # filtro de coluna, linhas na 1ª tela, colunas fora da caixa, busca, voltar, contraste
```

- Janela: 1440 × 1000 (escala 1, ponteiro fino) e 390 × 844 (escala 2, toque, sem hover), pela emulação do `comp_lib.Chrome.aparelho`. É emulação. Não substitui aparelho físico.
- `localStorage` limpo antes de cada tarefa. Nenhum erro de script registrado em `window.__errs` (probe1 e probe2: `[]`).
- **Contagem.** Clique = clique ou toque, incluindo o do menu lateral para entrar na tela. Escolher numa lista nativa (`select`) conta 1; no celular são 2 toques (abrir e escolher). Rolagem conta à parte. O script clica pelo DOM (`element.click()`), o que mede o caminho, não o alcance do dedo.
- **Quem gera cada página.** `build.py` importa `areas/cadastros.py`. O `build()` dele (`cadastros.py:298-304`, `CAD_MODS`) chama `cd01`/`cd01det` de `cad_fazendas.py`, `cd02` de `cad_culturas.py`, `cd03`/`cd04` de `cad_ativos_pessoas.py`, `cd05` de `cad_parceiros.py` e `cd06`/`cd07` de `cad_produtos_estrutura.py`. As funções `cd01`…`cd07` de `cadastros.py` são legado e não geram página (todos os módulos existem). Os auxiliares de layout (`abas`, `faixa`, `cartoes`, `bloco_cad`, `CADXJS`) estão em `cadastros.py:83-296`.

---

## 2. Estrutura comum (padrão `cadx`, redesenho de 01/10/2026)

Cada tela é **um bloco** (`bloco_cad`, `cadastros.py:192`) com:
- abas por entidade, com contagem e ponto de pendência (`abas`, `cadastros.py:127`);
- a faixa "precisa de atenção", com até 3 cartões de número, registro e verbo (`faixa`, `cadastros.py:137`; `cadFaixa`, `:268`);
- a barra da grade: busca, "N de M", filtro rápido Todos · A resolver e a primária por último;
- os dados: grade G2 em lista ou árvore, ou cartões (`cartoes`, `:172`) para fazendas, conjuntos e equipes;
- o estado da tela no cabeçalho, numa linha (`estado_cab`, `:196`).

Abrir um registro, por linha ou por cartão, sempre chama `g2open` (`g2lib.js:104`, e `cadastros.py:277` para os cartões). Ele abre o **painel lateral de formulário** de 460 px (`engine.py:1264`), editável sempre que a grade é `m='form'` (`g2lib.js:111`: `ro` só quando o modo não é formulário). As ações do registro (Abrir talhão, conjuntos da máquina, Excluir, Ver saldo) ficam **depois de todos os campos** (`engine.py:1282`; `acoes_form`, `cadastros.py:214`).

---

## 3. Tela por tela

| Tela · código | O que mostra | Estrutura | Como se chega ao detalhe | 1440 × 1000 | 390 × 844 | Capturas |
|---|---|---|---|---|---|---|
| **CD-01** Fazendas, áreas e talhões · `cad_fazendas.py:252-465` | 32 talhões (Santa Rita 8, Boa Vista 1, Lagoa Grande 23), 3 fazendas, 18 áreas ambientais, 16 pontos de água | 4 abas. **Talhões**: árvore Fazenda › talhão, 7 colunas, Lista \| Mapa. **Fazendas**: 3 cartões. **Ambiental**: lista de 4 colunas. **Água**: lista de 8 colunas. Faixa por aba | Linha do talhão → formulário (6 campos, 5 editáveis) → "Abrir talhão ›" → CD-01det. Cartão da fazenda → formulário (12 campos). A linha da fazenda na árvore não abre nada. Ambiental e Água abrem consulta | Árvore com 1.609 px de dados para 696 px visíveis (2,3 janelas); as 32 linhas abrem expandidas. Água: Situação fora da caixa | Mostra Fazenda › talhão e Sistema. Abas cortadas ("Am…"; Água invisível). 1ª linha em y=512; 6 linhas na 1ª tela | `CD-01_1440_aba0..3`, `CD-01_390_aba0..3`, `CD-01_1440_mapa` |
| **CD-01det** Talhão · `cad_fazendas.py:512-708` | Ficha do talhão, parcelas por safra (safra › parcela, área livre), geometria e versões do polígono | Seletor no cabeçalho (`select` de 32 opções sem grupo por fazenda, `:709`). A ficha é uma **tabela de 1 linha × 9 colunas** (`:518-522`). 2 abas: Parcelas por safra (árvore de 8 colunas, consulta) e Geometria | É o detalhe. Clicar na ficha abre o mesmo formulário do talhão (`t1_det_ficha_abre_form_1440`) | Cabe | A ficha mostra só Fazenda e Sistema. Área, polígono e situação ficam fora. 1ª linha da árvore em y=534 | `CD-01det_*`, `t1a_detalhe_*` |
| **CD-02** Culturas, cultivares e operações · `cad_culturas.py:50-252` | 5 culturas e 7 cultivares; 11 operações › conjuntos com rendimento e custo | 2 abas: árvore Cultura › cultivar (7 colunas) e árvore Operação › conjunto (11 colunas). Secundária "Comparar com o realizado" (simulada) | Linha da cultivar → formulário (6 campos). Linha do conjunto → formulário de rendimento (12 campos). Linha da cultura ou da operação → outro formulário | Operações: Custo R$/h, Custo R$/ha e Fonte fora da caixa (1.523 px em 1.142) | 2 colunas; 1ª linha em y=479 | `CD-02_*`, `t7_*` |
| **CD-03** Máquinas, instalações e setores · `cad_ativos_pessoas.py:133-292` | 15 ativos (tratores, implementos, bombas, packing, silo) e 7 conjuntos | 2 abas: lista de 9 colunas e 7 cartões de conjunto | Linha → formulário (11 campos); os conjuntos da máquina aparecem como botões depois dos campos (`:214-216`). Cartão → formulário do conjunto | Próxima calibração e Situação fora da caixa (1.405 px em 1.142) | 2 colunas; 1ª linha em y=581; 5 linhas | `CD-03_*`, `t3_*` |
| **CD-04** Pessoas e equipes · `cad_ativos_pessoas.py:296-423` | 10 pessoas e 6 equipes | 2 abas: lista de **11 colunas** com filtro Função (`select`, `:315`) e 6 cartões de equipe | Linha → formulário (11 campos). Cartão da equipe → formulário (nome, líder, calendário), **sem os membros** (`:319`, `:365`) | Acesso ao app e Situação fora da caixa (1.427 px em 1.142) | 2 colunas; 7 linhas | `CD-04_*`, `t4_*` |
| **CD-05** Parceiros e fornecedores · `cad_parceiros.py:176-324` | 20 parceiros com papéis; cobertura de cotação de 9 grupos | 2 abas: lista de 8 colunas com chips por papel, que trocam as colunas (`COLS_P`, `:148`), e lista de 3 colunas | Linha → formulário com seções por papel (painel de 1.102 px). Grupo → consulta só com o número (`:183-184`) | Situação do papel fora da caixa (1.327 px em 1.142) | 2 colunas; 7 linhas; grupos homologados abaixo da dobra no painel (y=833) | `CD-05_*`, `t6_*` |
| **CD-06** Produtos, unidades e locais · `cad_produtos_estrutura.py:32-226` | 38 itens em 13 grupos; 11 locais de estoque | 2 abas: árvore Grupo › item (8 colunas) e lista de 5 colunas com chips por tipo | Linha → formulário (11 campos); "Ver saldo no Estoque ›" depois dos campos | Situação fora da caixa. Árvore com 2.284 px em 697 (3,3 janelas) | 2 colunas; a "Natureza de custo" quebra em 3 linhas por item | `CD-06_*`, `t5_*` |
| **CD-07** Estrutura gerencial · `cad_produtos_estrutura.py:247-390` | 23 códigos em 6 dimensões; rascunho v6 com 3 alterações; tradução ERP | Sem abas. Árvore Dimensão › código com **10 colunas**. Faixa com "Publicar estrutura" e "Traduzir no ERP"; "Importar do ERP" simulado | Linha → formulário (até 11 campos) | Conta no ERP, TOP no ERP, Situação e No rascunho fora da caixa (1.679 px em 1.142); "Centro de responsabilidad" cortado | 2 colunas; 1ª linha em y=593; 5 linhas | `CD-07_1440`, `CD-07_390` |

---

## 4. As 7 tarefas comuns (executado, `tarefas.json`, probe2 e probe3)

Os cliques contam o do menu. Os números valem para 1440 e 390, salvo indicação.

| # | Tarefa | Caminho mais curto hoje | Cliques | Campos (caracteres) | Rolagens | Caminho que a pessoa tenta e onde falha |
|---|---|---|---|---|---|---|
| 1 | Ver os talhões da Santa Rita e abrir um (T2) | Menu → a aba Talhões já abre com a árvore expandida → linha T2 (abre o **formulário**) → "Abrir talhão ›" → CD-01det#talhao=T2 | **3** | 0 | 1440: 0 · 390: 1 (C1, o último da Santa Rita, em y=893 > 844) | Fazendas → cartão Santa Rita abre o formulário da fazenda, sem talhões (`t1a_cartao_fazenda_1440`). Até o talhão: fechar, aba Talhões, linha, Abrir talhão = **7 cliques**. Clicar no nome "Santa Rita" na árvore não faz nada. Buscar "Santa Rita" → **0 de 32** (`CD-01_1440_busca_santa_rita`) |
| 2 | Cadastrar o talhão B2 (80 ha) na Boa Vista | Menu → Cadastrar talhão → Identificação, Fazenda (vem **Santa Rita**; trocar), Área cultivável → Salvar | **4** (no celular, 5 toques) | 2 (4) | 0 | Pelo cartão da Boa Vista, a fazenda é herdada: **5 cliques** e 1 rolagem do painel, porque "Cadastrar talhão nesta fazenda" fica em y=1.115 numa janela de 1.000. Depois de salvar, o talhão fica "Sem polígono" e o próximo passo é em outra tela (aviso: "definir o polígono no detalhe do talhão") |
| 3 | Achar o Trator 02 e ver implementos e horímetro | Menu → linha Trator 02 → formulário: Horímetro atual 2.988 h (campo editável, y=740) e, depois de 11 campos, "Pulverizador PJ-3030 · Pulverização ›" (y=1.086) | **2** (+1 para abrir o conjunto) | 0 | 1 no painel (1440 e 390) | Na linha só aparece "Conjuntos: 1". A aba Conjuntos não filtra por máquina, e o cartão abre outro formulário. O horímetro é só o valor atual, editável, sem data da leitura nem histórico |
| 4 | Ver a equipe e o papel de Marcos e quem mais está na equipe | A linha mostra "Campo 1" e "Operar trator, Operar pulverizador". Membros: ▾ da coluna Equipe → Limpar → Campo 1 → OK → Marcos, Carlos, Paula, Beto | **1** para ver · **5** para os membros | 0 | 0 | Equipes → cartão Campo 1 abre o formulário (nome, líder, calendário) **sem membros** (`t4_painel_equipe_1440`). O caminho explorado custou 11 cliques. O "papel" (Operador, Caldeiro…) existe só como opção do filtro Função, não na linha |
| 5 | Achar um fungicida e ver registro, unidade, embalagem e locais | Menu → busca "fungicida" → linha Fungicida A → formulário: L (unidade travada, com o motivo), galão de 5 L, lote e validade, Almox. defensivos (local padrão) | **2** | 1 (9) | 0 (1440) | **O registro não existe no cadastro do item** (o painel não tem "registro", "MAPA" nem "Agrofit"). Locais com saldo: "Ver saldo no Estoque ›" abre `EST.dc.html` sem o item (+1 clique e nova busca). A busca "fungicida" traz 3 dos 4 itens do grupo: Tebuconazol 200 EC fica de fora, e o grupo continua dizendo "4 itens" |
| 6 | Achar a Agro Norte e ver o que ela fornece | Menu → chip Fornecedores → coluna Grupos homologados: Herbicidas, Fungicidas, Inseticidas, Adjuvantes | **2** | 0 | 0 | Pela linha, os grupos aparecem num formulário de 9 campos editáveis: y=768 a 1440 e y=833 a 390 (abaixo da dobra). Buscar "Fungicidas" → **0 de 20**. "O que fornece" é só o grupo: nenhum item, preço, cotação ou pedido |
| 7 | Ver a cultivar 58 W e o rendimento da pulverização | Ciclo de 118 dias e semente na linha (menu); aba Operações → 21,60 ha/h na linha do conjunto | **2** para ver · **5** para abrir os dois painéis | 0 | 0 | Cultivar e rendimento não se ligam: o rendimento vale para "Cultura: Todas", e o painel da cultivar não leva a ele. A 1440, custo por hora, custo por hectare e fonte ficam fora da caixa |

Estas medidas são a linha de base para comparar antes e depois (AGENTS §3.3; UXP-02, v3.10/3.11 em revisão).

---

## 5. Problemas de UX, com evidência

Severidade pelo PRD 22.1: S3 = problema limitado com alternativa segura; S4 = cosmético. Nenhum achado é S1 ou S2: nenhum bloqueia o fluxo nem grava dado errado. Prioridade para o redesenho: **P0** é o que o proprietário pediu, P1 é o que mais custa no uso, P2 e P3 vêm depois.

### 5.1 Hierarquia escondida: a seleção não abre o que está dentro

| ID | Problema | Evidência (executado) | Regra (especificado) | Sev. · Prior. |
|---|---|---|---|---|
| I01 | O cartão da fazenda abre o **formulário de edição** da fazenda (12 campos), não os talhões. O único elo com os talhões é "Cadastrar talhão nesta fazenda", abaixo da dobra (y=1.115 de 1.000), e ele só cadastra | `cadastros.py:277` (`open:()=>g2open`); `cad_fazendas.py:403` (cartões) e `:339-340`; `t1a_cartao_fazenda_1440`; probe4 | PRD v3.9:1668 (CD-01: "Hierarquia e mapa com versões, parcelas, ocupação"); v3.9:4891 (#16 "Lista geográfica com hierarquia e ocupações"); pedido de 09/10 | S3 · **P0** |
| I02 | A linha da fazenda na árvore é inerte: `x.open=()=>{}`. Clicar em "Santa Rita" não abre nem recolhe nada (35 linhas visíveis antes e depois) | `cad_fazendas.py:427`; probe5 | v3.9:293 (4.3: "Linha abre detalhe canônico por clique/teclado") | S3 · **P0** |
| I03 | Ambiental e Água são abas irmãs de Fazendas, mas pertencem a uma fazenda. A coluna Fazenda repete "Lagoa Grande" em 18 de 18 e 16 de 16 linhas. Santa Rita e Boa Vista não têm linha nem aviso | `cad_fazendas.py:276-295`; `CD-01_1440_aba2`, `_aba3` | v3.9:1668 ("restrições" dentro da hierarquia da área) | S3 · P1 |
| I04 | O cartão da equipe abre um formulário sem os membros. Para ver quem está na equipe: filtro de coluna em 4 cliques na outra aba | `cad_ativos_pessoas.py:319`, `:365`; `t4_painel_equipe_1440`, `t4_menu_coluna_equipe_1440`, `t4_membros_filtro_1440` | v3.9:1731 (CD-04: "Vincular equipe"); v3.9:4896 (#21 "Cadastros por entidade") | S3 · **P0** |
| I05 | Da máquina aos implementos: a linha mostra só o número de conjuntos. Os nomes ficam depois de 11 campos do formulário (y=1.086). A aba Conjuntos é outra lista, sem filtro pela máquina | `cad_ativos_pessoas.py:214-216`, `:237`; `t3_painel_maquina_1440` | v3.9:1716 (CD-03: "Conjuntos elegíveis máquina/implemento"); v3.9:4897 (#22 "Ficha operacional do ativo") | S3 · **P0** |
| I06 | Do grupo aos fornecedores: "Cobertura de cotação" mostra só o número. A consulta do grupo repete grupo e número, sem a lista | `cad_parceiros.py:183-184`; `CD-05_1440_aba1` | v3.9:1748 (CD-05: "grupos de insumo homologados") | S3 · P1 |
| I07 | Cultivar e operação não se ligam: o rendimento vale para "Cultura: Todas", e nada no painel da cultivar leva aos rendimentos ou às operações da cultura | `cad_culturas.py:66-112`; `t7_painel_cultivar_1440` | v3.9:8279 (REND-01: "acessar a mesma ficha… painel contextual mantém operação/parcela selecionada") | S3 · P2 |
| I08 | O detalhe do talhão não tem ficha. A identificação é uma tabela de 1 linha × 9 colunas, e clicar nela abre o formulário. O seletor tem 32 opções sem grupo por fazenda e sem busca | `cad_fazendas.py:518-522`, `:709`; `t1_det_ficha_abre_form_1440`; probe4 | v3.11:14546 (DS-58, v3.10 em revisão: cabeçalho "O que é · Onde · Estado · Quem resolve · Prazo") | S3 · P1 |

### 5.2 Formulário sempre aberto: ver é editar

| ID | Problema | Evidência | Regra | Sev. · Prior. |
|---|---|---|---|---|
| I09 | Toda linha e todo cartão abrem o formulário editável, com "Salvar" verde já ativo. Para ler, a pessoa percorre campos editáveis: 5 no talhão, 12 na fazenda, 11 na máquina, na pessoa e no item, 9 no parceiro. Um toque errado muda o dado (o aviso de não salvo existe, mas ver e editar continuam sendo a mesma coisa) | `g2lib.js:111`; `t1a_painel_talhao_1440`, `t3_*`, `t4_*`, `t5_*`, `t6_*` | v3.9:295 (4.3: "lista é para localizar e decidir; detalhe é para compreender e agir; formulário curto abre painel"); v3.11:14537-14544 (DS-57: "Detalhe: painel de 820 px ou página") e v3.11:14351-14362 (DS-41: painel de consulta de 820 px), v3.10 em revisão | S3 · **P0** |
| I10 | O caminho é invertido: Lista → Formulário → "Abrir talhão ›" → Detalhe. Só o talhão tem detalhe. Fazenda, máquina, pessoa, item, parceiro e cultivar terminam no formulário | `cad_fazendas.py:336-338` (Abrir talhão é ação do formulário) | AGENTS §4 (Menu → Listagem → Detalhe → Sub-detalhe); v3.9:4892 (#17 "Detalhe do mesmo talhão; ciclos, histórico e mapa vinculados") | S3 · **P0** |
| I11 | As ações do registro ficam depois de todos os campos, abaixo da dobra: fazenda (y=1.115), máquina (y=1.086) | `engine.py:1282`; `cadastros.py:214`; probe2 e probe4 | v3.9:281 (4.2: "Um botão primário por contexto ativo; até duas ações secundárias frequentes") | S3 · P1 |

### 5.3 Rolagem longa

| ID | Problema | Evidência | Regra | Sev. · Prior. |
|---|---|---|---|---|
| I12 | As árvores abrem com tudo expandido (`x0` = todos `True`). A pessoa rola tudo para chegar a uma fazenda ou a um grupo: CD-01 tem 2,3 janelas (os 23 pivôs da Lagoa Grande depois da Santa Rita), CD-06 tem 3,3, CD-07 tem 1,9 e CD-02 Operações tem 1,5 | `cad_fazendas.py:265`; `cad_culturas.py:68`, `:110`; `cad_produtos_estrutura.py:90`, `:268`; probe1 (`rolaV`) | v3.9:289 (4.3: agrupamento e "N de M") | S3 · P1 |
| I13 | Painéis longos: parceiro com 1.102 px (1440) e 1.167 px (390); fazenda com a ação em y=1.115 | probe2 (`alturaConteudo`) | v3.11:14351 (DS-41: rolagem própria; v3.10 em revisão) | S4 · P2 |

### 5.4 Ações e estados duplicados

| ID | Problema | Evidência | Regra | Sev. · Prior. |
|---|---|---|---|---|
| I14 | O mesmo comando aparece 2 vezes para o mesmo registro na mesma tela: "Definir polígono ›" na faixa e na linha do B1 (CD-01); "Vincular semente" no 64 Z (CD-02); "Informar preço" no Calcário (CD-06); "Renovar ›" do Marcos (CD-04) | `CD-01_1440_aba0`, `CD-02_1440_aba0`, `CD-06_1440_aba0`, `CD-04_1440_aba0`; `cadastros.py:229` (`sitX`) e `:268` (`cadFaixa`) | PADRÃO:12-16 ("Uma instância por efeito… contando… faixa, cartão") e :69-71 ("a mesma ação duas vezes para o mesmo alvo é duplicata") | S4 · P2 |
| I15 | Há comando dentro da linha nas 7 telas: o verbo vem na coluna Situação (Renovar ›, Informar motivo, Registrar calibração…). Isso diverge do padrão já adotado em Suprimentos, "a linha identifica, o painel resolve" | `cadastros.py:229`; `docs/suprimentos-simplificado/ESPECIFICACAO.md:128-131` | Brief desta frente: reaproveitar esse padrão | S4 · P2 |
| I16 | A mesma pendência aparece 4 vezes: cabeçalho ("B1 sem polígono"), ponto na aba, cartão da faixa e chip na linha | `CD-01_1440_aba0`; `cadastros.py:196` (`estado_cab`), `:127` (`abas`), `:137` (`faixa`) | AGENTS §3.4 (corte do supérfluo) | S4 · P3 |
| I17 | "Cadastrar talhão" existe em 4 lugares, com comportamentos diferentes. Só o do painel da fazenda herda a fazenda: barra da aba (`cad_fazendas.py:266`), barra do Mapa (`:270`), link na linha da fazenda sem talhão (`:347`) e "Cadastrar talhão nesta fazenda" (`:339-340`) | código citado; probe2 (2a × 2b) | PADRÃO:12 (uma instância por efeito) | S4 · P2 |

### 5.5 Rótulos técnicos e repetição

| ID | Problema | Evidência | Regra | Sev. · Prior. |
|---|---|---|---|---|
| I18 | CD-06 mostra o código da controladoria em cada item: "3.1.02 · Defensivos" (coluna Natureza de custo), repetido em cinza em todas as linhas filhas. A 390, quebra em 3 linhas por item | `cad_produtos_estrutura.py:155`; `CD-06_1440_aba0`, `CD-06_390_aba0` | v3.9:4893 (#18 "Cadastro do produto separado dos saldos"); 4.3 (até sete colunas úteis) | S4 · P2 |
| I19 | CD-07 usa "TOP no ERP", "Conta no ERP (Sankhya)" e "Dimensão › código", e a coluna Origem repete "Estrutura gerencial" em quase todas as linhas | `cad_produtos_estrutura.py:265`; `CD-07_1440` | v3.11:14725 (74.8 Conteúdo, v3.10 em revisão) | S4 · P3 |
| I20 | CD-01 usa o jargão da fonte como estado: "Círculo do KML" em 23 talhões; "Polígono", "Diferença %", "Geometria v3" | `cad_fazendas.py:316-321` (`talSit`); `CD-01_1440_aba0` | AGENTS §0 (simples, objetivo) | S4 · P3 |
| I21 | Valores do pai repetidos em cinza em cada filho: "Tipo de ciclo" e "Unidade" em cada cultivar, "Processo" em cada conjunto, natureza em cada item | `cad_culturas.py:158`, `:173`; `cad_produtos_estrutura.py:155` | AGENTS §3.3 (não pedir nem mostrar o mesmo dado duas vezes) | S4 · P3 |
| I22 | CD-03 "Capacidade" põe na mesma coluna 155 cv, 3.000 L, 24 linhas, 3.000 kg e 300 m³/h. Ordenar compara grandezas diferentes. Isto é assunto da TABELAS-FOCO, registrado aqui só como insumo | `CD-03_1440_aba0`; `cad_ativos_pessoas.py:176` (`c3capn`) | Regra da TABELAS-FOCO: uma variável por coluna | S4 · P3 |

### 5.6 Contexto que não é herdado

| ID | Problema | Evidência | Regra | Sev. · Prior. |
|---|---|---|---|---|
| I23 | "Cadastrar talhão" na barra sempre pré-escolhe a 1ª fazenda (Santa Rita), mesmo quando a pessoa está olhando outra | `cad_fazendas.py:101` (`'def':fazs[0]`); probe2 ("fazenda pré-escolhida: Santa Rita") | AGENTS §3.3 (herdar fazenda, visível e corrigível); UXP-02 (v3.10/3.11 em revisão) | S3 · P1 |
| I24 | Links que saem sem o registro: "Planejar T1 na safra" vai para `SAF.dc.html`; "Ver saldo no Estoque ›" vai para `EST.dc.html`; "Ver ordens afetadas" vai para `OS.dc.html`; "Cadastrar rendimento ›" vai para `CD-02#aba=operacoes` sem o conjunto | `cad_fazendas.py:523`; `cad_produtos_estrutura.py:147`; `cad_ativos_pessoas.py:207`, `:217`, `:254` | v3.9:1676 (CD-01: "A ação seguinte abre o registro de destino preservando contexto") | S3 · P1 |
| I25 | "Voltar" do detalhe do talhão leva a `CD-01.dc.html`, sem aba, busca nem posição | probe4 (`href`) | v3.9:278 (4.2: "retorno conserva filtros, seleção e posição da lista") | S3 · P2 |
| I26 | O Mapa da aba Talhões só alterna Santa Rita e Lagoa Grande. A Boa Vista não aparece e o mapa não segue a fazenda escolhida | `cad_fazendas.py:270`; `CD-01_1440_mapa`; probe5 | v3.9:1668 ("Hierarquia e mapa") | S4 · P2 |

### 5.7 Busca que não acha e onde falta busca

| ID | Problema | Evidência | Regra | Sev. · Prior. |
|---|---|---|---|---|
| I27 | A busca não encontra pelo nível de cima. "Santa Rita" → 0 de 32 (o cabeçalho do grupo aparece vazio). "Herbicidas" → 0 de 38. "Fungicidas" no CD-05 → 0 de 20. "Soja" → 2 de 7: acha 58 W e 62 X pelo nome da semente e perde a 64 Z. "fungicida" → 3 de 4 no grupo (perde Tebuconazol). "Natureza" → 1 de 23 | probe5, probe6; `CD-01_1440_busca_santa_rita` | v3.9:279 (4.2: busca por talhão, ativo, pessoa, parceiro); v3.11:14520-14531 (DS-88, v3.10 em revisão: busca por nome, código e sinônimo) | S3 · **P0** |
| I28 | Falta busca nas abas de cartões (Fazendas, Conjuntos, Equipes), nas parcelas do detalhe do talhão e no seletor de talhão (32 opções). As 8 páginas têm `search=False` na casca | `cad_fazendas.py:464`, `:708`; `cad_culturas.py:251`; `cad_ativos_pessoas.py:291`, `:422`; `cad_parceiros.py:323`; `cad_produtos_estrutura.py:225`, `:389` | v3.9:279 (busca global) | S3 · P2 |

### 5.8 Estados vazios

| ID | Problema | Evidência | Regra | Sev. · Prior. |
|---|---|---|---|---|
| I29 | Busca sem resultado responde "Nenhuma linha corresponde aos filtros · Limpar filtros". Fala de "linha" e "filtros" quando foi uma busca e não oferece "Cadastrar {entidade}" | `CD-01_1440_busca_vazia`; probe5 (CD-01, CD-02) | v3.11:14394 (DS-45) e :14527 (DS-88: "Nenhum {item} encontrado" e "+ Novo"), v3.10 em revisão; v3.9:297 (4.3: "vazio com próximo passo") | S4 · P2 |
| I30 | Ausência silenciosa: Santa Rita e Boa Vista sem nenhuma área ambiental nem ponto de água, e nenhuma frase diz se falta cadastrar ou se não há | `CD-01_1440_aba2`, `_aba3` | v3.9:297 ("vazio com próximo passo") | S3 · P2 |

### 5.9 Celular (390 × 844)

| ID | Problema | Evidência | Regra | Sev. · Prior. |
|---|---|---|---|---|
| I31 | O menu lateral fica em 68 px fixos e sobram 292 px para a grade. Nas 8 telas aparecem 2 colunas inteiras, e a Situação (estado e próximo passo) nunca aparece sem rolar de lado | `ui37.py:154`, `:324`; probe1 (`rolaH` 292) e probe3 (`colunas_inteiras_visiveis`) | v3.9:293 (4.3: "em celular, oferecer controles equivalentes sobre a lista de cartões"); v3.11:14544 (DS-57: "No celular, lista de cartões", v3.10 em revisão) | S3 · **P0** |
| I32 | Cabeçalho, estado, abas, faixa, busca, chips e botões ocupam metade da tela antes do 1º dado: a 1ª linha fica em y=424 a 593 de 844. Cabem 5 a 7 linhas | probe3 | v3.9:305 (4.4: "Página móvel mostra primeiro trabalho…") | S3 · P1 |
| I33 | Abas cortadas: o CD-01 mostra "Talhões", "Fazendas", "Am…", e Água fica invisível (rolagem lateral oculta) | `cadastros.py:87` (`.cadx-abas{… overflow-x:auto}`); `CD-01_390_aba0` | DS-07 (contexto visível; v3.10 em revisão) | S3 · P1 |
| I34 | A ficha do talhão a 390 mostra Fazenda e Sistema. Área, polígono, diferença e situação ficam fora | `CD-01det_390_aba0` | DS-58 (v3.10 em revisão) | S3 · P1 |

### 5.10 Desktop: colunas fora da caixa, seleção rápida e contraste

| ID | Problema | Evidência | Regra | Sev. · Prior. |
|---|---|---|---|---|
| I35 | A 1440 × 1000, a última coluna (Situação, com o verbo) fica fora da caixa em CD-03, CD-04, CD-05, CD-06, CD-07 e CD-01 Água. CD-02 Operações perde 3 colunas. Contagem de colunas: CD-04 11, CD-02 Operações 11, CD-07 10, CD-03 9, ficha do CD-01det 9, CD-05 8, CD-06 8, CD-01 Água 8 | probe3 e probe4 (`fora_da_caixa_a_direita`); `CD-04_1440_aba0`, `CD-05_1440_aba0`, `CD-07_1440` | v3.9:287 (4.3: "Tabelas começam com até sete colunas úteis; outras… ficam no detalhe") | S3 · P1 |
| I36 | Listas curtas viram `select` nativo (2 toques): Sistema (3 opções), Situação (2), Exige calibração (Sim/Não), Homologado (Sim/Não), Vínculo (4), Controle (3). Catálogos médios não têm busca: Local padrão (11), Líder (10), Item de semente. As datas não têm atalho | `cad_fazendas.py:102`, `:109`; `cad_ativos_pessoas.py:115`, `:118`, `:302`, `:304`, `:307`; `cad_produtos_estrutura.py:98-105`; `cad_parceiros.py:116` | AGENTS §3.3 (lista curta: um toque; catálogo: busca com sugestões; data: atalhos); UXP-03 e DS-88 (v3.10/3.11 em revisão) | S4 · P2 |
| I37 | No CD-05, o número do chip "Todos" selecionado sai em branco (opacidade 0,8) sobre #E4F3E9, cerca de 1,1:1. Fica ilegível | `cad_parceiros.py:250` (`nst`); probe4 (cores calculadas); `CD-05_1440_aba0` | v3.9:299 (4.3: contraste faz parte do aceite [S3]); DS-09 (v3.10 em revisão) | S3 · P2 |

### 5.11 Lacunas de contrato achadas no caminho (não são UX; ficam registradas)

- **Registro do produto (CD-06).** O PRD pede "Vincular registro → AG-07" (v3.9:1769). O item não tem campo, link nem consulta de registro. Não verifiquei se alguma trava da O.S. depende disso: a O.S. consulta o AGROFIT (`areas/agronomia.py:936`). (I-L1)
- **Contador (CD-03).** O PRD pede "Configurar contador" (v3.9:1712) e "Troca de medidor mantém continuidade do histórico". Hoje há só o valor atual editável, sem data da leitura nem histórico. (I-L2)
- **Parceiro (CD-05).** O PRD lista "culturas; condição; avaliação; documentos" (v3.9:1748). Esses campos não aparecem em `CAMPOS` (`cad_parceiros.py:107-137`). (I-L3)

---

## 6. O que funciona e precisa ficar

- **Validações no lugar, com causa e saída.** Soma dos talhões ≤ área da fazenda; parcelas impedem reduzir área, mudar de fazenda ou inativar (`cad_fazendas.py:162-183`, `talErros`); CPF/CNPJ duplicado com "Abrir e ativar papel" (`cad_parceiros.py:164`, `:264`); horímetro não regride (`cad_ativos_pessoas.py:272`); unidade-base travada com o motivo (`cad_produtos_estrutura.py:191`, `t5_painel_item_1440`).
- **"Cadastrar fazenda…" dentro do talhão** volta ao talhão sem perder o que foi preenchido (`cad_fazendas.py:409`, `:439`).
- **Inativar em vez de excluir.** Exclusão com confirmação, e o motivo aparece quando ela é bloqueada (`cadastros.py:290`, `cadExcluir`).
- **Faixa "precisa de atenção"** com número, registro e verbo, e o estado da tela numa linha. A informação fica; o que sai é a repetição (I14 a I16).
- **Grade G2.** "N de M", filtro e ordenação por coluna com valores reais e contagem (`t4_menu_coluna_equipe_1440`), unidade na célula, uma variável por coluna (TABELAS-FOCO).
- **Detalhe do talhão.** Parcelas por safra com a área livre e versões do polígono com origem (`CD-01det_1440_aba0`, `_aba1`).
- **Painel.** A 390 ele ocupa a tela inteira (`t1a_painel_talhao_390`). Ao fechar, avisa de alteração não salva.

---

## 7. Dependências e limites

- **TABELAS-FOCO** (`claude/v44-tabelas-r`, `/home/user/sp-tabr`) continua nas grades (uma variável por coluna, unidade na célula, filtro e ordenação). O redesenho entra por cima dela. I22 e parte de I35 são insumo para aquela frente, não para esta.
- **DS** (`/home/user/sp-ds`): separadores, hover verde, retorno visual e `g2dica` (commits `0654b2a`, `e4843e0`, `a1bb4d5`, `f36cdd0`). O desenho conta com eles e não os refaz.
- **Ainda não feito:** benchmark (UXP-01, cinco referências do módulo com fonte e data), validação do proprietário, teste em aparelho físico e teclado ou leitor de tela nas telas de Cadastros.
- As capturas estão no scratchpad (`cap/`), que não persiste. Ao fazer o commit, o desenho deve copiar para esta pasta as capturas citadas.
- O datepicker mostra "09/15/2026" porque o Chrome headless roda em en-US. Não é defeito do protótipo e não foi contado.

---

## 8. Insumos para o desenho (hipóteses, não decididas)

1. **A seleção abre o conteúdo**, sem formulário no meio. Fazenda → talhões dela na mesma tela; equipe → pessoas; máquina → conjuntos e implementos; grupo → itens ou fornecedores; cultura → cultivares e rendimentos. A 1440, lista e detalhe lado a lado. A 390, navegação empilhada com "‹ voltar" que preserva a posição. (I01 a I07)
2. **Consultar antes de editar.** O painel ou a página de consulta mostra a ficha (O que é · Onde · Estado · Próximo passo) e só "Editar" abre o formulário (DS-41 de 820 px e DS-58, v3.10 em revisão). (I08 a I11)
3. **"A linha identifica, o painel resolve"**, reaproveitado de Suprimentos: o verbo sai da linha e fica uma vez no painel; a faixa só filtra. (I14 a I17)
4. **Até 7 colunas na lista.** O resto vai para o detalhe, e no celular a lista vira cartões com os mesmos filtros. (I31 a I35)
5. **Busca que encontra pelo pai e por sinônimo**, com o pai visível no resultado e "Nenhum {item} encontrado · Cadastrar". (I27 a I29)
6. **Contexto herdado em todo "Cadastrar" e em todo link de saída**, visível e corrigível. (I23 a I25)
7. **Medir de novo as 7 tarefas da seção 4** com os mesmos scripts, antes e depois (AGENTS §3.3).
