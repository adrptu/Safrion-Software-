# Planejar safra · etapa única "Dimensione operações e recursos" (v2): numa tela só, saber se a safra cabe no que a fazenda tem, onde aperta e ajustar ali mesmo

**Pedido do proprietário (chat, 05/10/2026):** «Integre a etapa 3, 4 e 5 numa só fazendo um UX e UI mais inteligente, simples e intuitivo possível. Elimine duplicidades dados menos relevantes e foque no mais essencial que gera valor real na gestão operacional da safra.»

**v2.** Aplica os 33 achados confirmados da revisão. O que mudou e por quê está em [DECISOES.md](DECISOES.md); o que fica de fora, em [FORA-DE-ESCOPO.md](FORA-DE-ESCOPO.md).

**Em uma linha:** o topo diz se cabe e o que ficou fora da conta; a capacidade por mês fica recolhida num atalho; a árvore de operações é a lista; o formulário é o sub-detalhe.

**Rótulos:**
- **Executado (v2calc):** saiu de comando nesta revisão, sobre `884620c`. Os scripts estão em `scratchpad/v2calc/`: `cap2.js` (o `capSaf` proposto sobre o motor real, `saf_body.js` = `safra.js` linha a linha), `base.js`, `cen.js`, `filtro.js`, `janela.js`, `o9.js`, `mn04.js`, `misc.js`. Também rodaram de novo `rend_multiconjuntos_unit.py` (106/106), `quantidade_test.py` (14/14) e `cadc_cd0102_b.py` (falha na linha 27).
- **Simulação de layout (v2calc):** DOM real do `_render` com o topo da v2 injetado (`layout_c.py`, `layout_m_d.py`, `largura_v2.py`). Não é a tela implementada.
- **Executado pelo revisor:** medida que não refiz; o script vem citado.
- **Especificado:** proposta, sem execução.
- **LG2627:** os dados são sintéticos.

---

## 0. Como executar

### 0.1 Base, reserva e impedimentos
- **Base:** `884620c`, ponta do PR #44 em rascunho. Branch nova: `claude/v44-saf-unica-01`.
- **Reserva antes de editar.** Commit só de reserva em `tools/prototipo/v37/RETOMADA-NUVEM.md`, no padrão do `1fbb354`, com base, arquivos (§0.3) e o acordo (§0.2). O mesmo acordo vai para um arquivo novo em `docs/parceria/rodadas/`.
- **Impedimento 1 · cadeia de rascunhos.** #36→#37→#39→#40→#41→#42→#43→#44 estão todos em rascunho, e o #45 está empilhado sobre o #44. Executado (`gh api …/pulls`): o `884620c` não é ancestral de `origin/main`. Sete desses PRs tocam os arquivos desta fatia.
  - Antes da integração da cadeia: o PR 1 pode ser integrado; o PR 2a só abre como rascunho.
  - Depois da integração: rebase da branch, nova linha de base da bateria (a `un-20261005` vale só para `884620c`) e os PRs seguintes comparados com ela.
- **Impedimento 2 · registro (AGENTS §2).** O Codex registra a DEC-0510 reduzida antes do PR 4 (texto em DECISOES.md). Ela tem só a frase literal do proprietário e as consequências mecânicas: 4 etapas e o nome da etapa 3. As escolhas dos agentes ficam como proposta. P1 e P2 vão para "Decisões pendentes do proprietário" (`docs/DECISIONS.md:27-29`).
- **Impedimento 3 · respostas de P1 e P2.** Os commits do PR 4 que tiram `g_mat` (P1) e `g_rend_*` (P2) do corpo esperam a resposta. As perguntas vão já, junto com o pedido de registro.
- **Montar e testar** (RETOMADA, "Como montar e testar na nuvem"): `python3 build.py`, `python3 montar_render.py`, `CHROME_BIN=… python3 varredura.py`, depois cada teste.

### 0.2 Acordo curto (AGENTS §3.4)
```text
ID / resultado útil / persona: SAF-ETAPA-UNICA-20261005 / ver se a safra cabe nas máquinas e pessoas, onde aperta e ajustar conjunto, rendimento e recursos no mesmo lugar / gestor e planejador da fazenda
Requisitos do PRD e fora do escopo: UX-01, 71.6, 52.1, 44.1, 44.3, 44.4, 53.2, 4.2, 4.3; fora: FORA-DE-ESCOPO.md
Autor / revisor / integrador: Claude / Codex / Codex
Base / arquivos: 884620c / gen37/safra.js (por função; ver §0.3), gen37/areas/processo_safra.py, gen37/dados2.py (só blocos novos), gen37/areas/processo_compras.py e areas/suprimentos.py (links e textos), gen37/g2lib.js e gen37/engine.py (parte 'act' com aria-label e célula g2nr), testes do §9
Aceite e verificação: §11; capacidade_unit + 106/106 + 14/14 + saf_operacoes_test + bateria sem vermelho novo contra a linha de base pós-cadeia
Estado / impedimento / próximo passo: especificado / cadeia #36–#44, DEC-0510 reduzida, P1 e P2 / PR 1 (capacidade pura)
```

### 0.3 Mapa do que existe

**Coordenação com a etapa 2 em redesenho** (`scratchpad/saf2/especificacao.md:592-599`). Vale a ordem de lá: o PR-A entra em paralelo; esta fatia entra antes do PR-B; se o PR-B ficar pronto antes, ele entra e esta refaz a base. A reserva desta fatia é **por função**. Ficam fora dela: o ramo `step===2` de `safAcoes` (exceto o rótulo do avanço), `openApply`/`apVals`/`doApply`, `leaves`, `cult*`, `dv*`, `syncLivres`, `k2` e, em `dados2.py`, o bloco `CULTIVOS['S2526']`.

**Fica sem mudar a lógica:**

| O quê | Onde |
|---|---|
| Motor REPARTIR (D-01, várias configurações, partes, sequência, troca, pools, causas, `nec = atendido + saldo`) | safra.js:29-280; espelho dados2.py:209-661; oráculo `rend_multiconjuntos_unit.py` |
| Ponte `cfgLeaves`, `cfgsOf`, `ativosDe`, `cfgIn`, `poolsOf` | safra.js:282-289 |
| `ocorr` (fonte única, `dose*area` em :330) e `demanda` | safra.js:322-337 e :338 |
| `prodColheita`, `compRend`, `rendLive`, `conjOpts`, `normRend`, `rendNova`, `rendRemover`, `rendActs` | safra.js:358-494 |
| Campos e limites dos formulários de recurso | processo_safra.py:170-186 |
| `g_rend_<safra>`, `g_recp_maq`, `g_recp_pes` como fonte e formulário (saem só do corpo; o formulário já vai para `EXTRA`, engine.py:1243) | processo_safra.py:149-154, 180-186 |
| Área de ações única | engine.py:1085-1100; g2lib.js:360; safra.js:874 |
| Etapas 1, 2 e a demanda (hoje etapa 6) | processo_safra.py:193, 250; safra.js:789-820 |

**Muda:**

| O quê | Onde | Para |
|---|---|---|
| `NOMES`, blocos `s3`–`s5` e `corpo` | processo_safra.py:12, 223-252 | 4 etapas; um bloco `s3` (§2) |
| `g_op` | processo_safra.py:158-162 | 8 colunas (§3.4) |
| Ganchos `g2pick`, `g2live`, `g2after` | processo_safra.py:204-212 | `g_op` → `abrirRend`; `g_cap` → `abrirRec`; `g2live`/`g2after` também em `g_recp_*` |
| `PREVALS` das etapas 4 e 5 | safra.js:665-788 | `g_op`, `g_cap`, veredito, linha de capacidade, `state.cap`, `state.capAberta` |
| `mlab` e `mes` de `linhaOc` | safra.js:676, :710 | faixa real de meses (§3.4) |
| Custo por hectare | safra.js:388, :462 | `custoHa(custo_h, rend)` (ENG-011) |
| `rendAfter`: alcance do "Todas" e aviso | safra.js:439-474 | só atividades em uso (`atvEmUso`); aviso antes → depois |
| Campo `jan` e ajuda do "Aplicar em" | processo_safra.py:131, :145 | duas entradas com conds exclusivas + `jan_op` só leitura (§4.1) |
| `rendCheck` | safra.js:421 | guarda da janela digitada em "Todas" |
| `proxSaf`, laço `s1..s6`, `whys`, `g2steps(…,6,…)`, `abrirHash`, `SAF_CURTO`, `safAcoes`, `pickat` | safra.js:647-651, 824-827, 845, 852-855, 863, 874-901 | §5 |
| Origem da solicitação e textos com "etapa 6" | safra.js:1011, :1018; dados2.py:692; processo_compras.py:166, 175, 278, 322, 476, 487, 490, 496, 505, 576; suprimentos.py:489 | `passo=demanda` e "Planejar safra · demanda de insumos" |
| Parte `act` e célula de mês | g2lib.js:91, 96, 179, 191; molde da célula em engine.py | `al` → `aria-label`; opção `full`; campo `nr` → classe `g2nr` fora do clique da linha (retrocompatível) |

**Sai do corpo:** `g_mat`, alternância "Por operação / Por mês", faixa "Mostrando só" (processo_safra.py:164-165, 225-231; safra.js:724-735; espera P1). Frase `k4` (safra.js:736-744). `g_res`, `g_resd`, `rec_ctl`/`seg2`, "Dias úteis por mês", `k5` (processo_safra.py:186-189, 233-249; safra.js:745-788). "Necessárias no pico", "Mês do pico" e `if(n>pico)` (safra.js:765-771). Estados `atv`, `opv`, `rec`, `rcl`, `rv`. `sc-if rend_<safra>` (processo_safra.py:149-154; espera P2).

**Novo:**

| O quê | Onde |
|---|---|
| Bloco puro `// >>> CAPACIDADE … // <<< CAPACIDADE`: `capRec`, `cargaRec`, `outrasSafras`, `capSaf`, `fmtOcup`, `classeOc`, `atvEmUso` | safra.js |
| `origemCfg(d)` ao lado de `cfgBase` (safra.js:433); `resumoCultura(self, saf, oc)` | safra.js |
| Espelhos `plano_op(safra, planos=None, cfg_override=None)`, `capacidade(safra, recursos=None, planos=None, cfg_override=None)` e `resumo_cultura(safra, ajustes=None, planos_extra=None)` | dados2.py |
| Grade `g_cap`, campos `jan_op` e `origem`, seção "Neste talhão", painel "Resumo da safra" | processo_safra.py (EXTRA) e safra.js |
| `capacidade_unit.py` (node + Python) e `saf_operacoes_test.py` (navegador) | gen37/ |

---

## 1. Perguntas que a etapa responde, em ordem de valor

1. **A safra cabe no que a fazenda tem? Em que mês e recurso aperta, e quanto falta?** Veredito e linha de capacidade; detalhe na `g_cap`.
2. **O que ficou fora da conta e por quê?** Cláusula "Fora da conta" do veredito: cultivos sem plano, ocorrências antes do início, fora do calendário ou sem horas calculáveis.
3. **De onde vem a carga daquele mês?** Toque no atalho ou na célula recurso × mês: a `g_op` filtra e mostra as horas do recurso.
4. **Que conjunto, rendimento e custo por hectare estou assumindo, e vale usar recurso próprio ou prestador?** `g_op` e formulário Rendimento.
5. **Cada operação termina dentro da janela?** Coluna Situação: "Cabe na janela", "Janela não informada" ou "Com pendência". O veredito conta quantas atividades estão sem janela.
6. **Quanto custa operar e quanto custa cada cultura por hectare?** Custo de operação na linha do título; "Resumo da safra" por cultura.

---

## 2. Layout

Um bloco (`section`). Ordem no DOM, igual em qualquer largura:
1. título, com "Custo de operação" e o link "Resumo da safra" à direita (no estreito, numa linha logo abaixo do título);
2. veredito (`<span role="status">`) e, fora dele, a linha de capacidade;
3. `g_cap`, **recolhida por padrão**;
4. linha de filtro (só com `state.cap`);
5. `g_op`, último filho direto.

Assim vale o CSS de 01/10 (engine.py:1112-1131): a última `.g2caixa` estica e só a área de dados rola, com cabeçalho fixo.

### 2.1 Computador, 1440 × 1040 (S2627)
```text
Fazenda Santa Rita · Safra 2026/27 · Trocar safra                                                Agrícola › Planejar safra
✓ 1 Escolha a safra   ✓ 2 Defina cultivos e planos   ● 3 Dimensione operações e recursos   ○ 4 Confira a demanda de insumos
┌ Operações e recursos              Custo de operação R$ 264.617,07 · máquinas e pessoas, sem insumos · Resumo da safra ┐
│ ● Na estimativa mensal, cabe nos 690 ha com plano. Fora da conta: T4, T3, P1 e P2 (475 ha), sem plano. Prazo por        │
│   talhão não verificado: 17 de 17 atividades sem janela.  Maior uso: Colhedoras 81 % · fev/27   Capacidade por mês ▾    │
│ [Buscar operação ou talhão]  8 de 8                                                                     Expandir tudo │
│ OPERAÇÃO › ATIVIDADE › TALHÃO │ SITUAÇÃO             │ DATA            │ CONJUNTO                                      │ RENDIMENTO │ ÁREA TRABALHADA │ HORAS-CONJUNTO │ CUSTO R$/HA      │
│ ▸ Pulverização · 6 atividades │ Janela não informada │ set/26 – jan/27 │ Trator 02 MF 7719 + Pulverizador PJ-3030 36 m │ 21,60 ha/h │   2.520 ha-op   │       116,7 h  │ R$ 14,49/ha-op   │
│ ▸ Fertirrigação · 2 atividades│ Janela não informada │ out/26 – nov/26 │ Sistema de gotejo T7 · 1 irrigante            │ 10,00 ha/h │      84 ha-op   │         8,4 h  │ R$ 5,70/ha-op    │
│ ▸ Tratamento de sementes      │ Janela não informada │ out/26          │ Máquina TSI na sede · equipe de 2             │ 40,00 ha/h │     610 ha-op   │        15,3 h  │ R$ 3,40/ha-op    │
│ ▸ Plantio · 1 atividade       │ Janela não informada │ out/26          │ 2 conjuntos                                   │            │     610 ha-op   │       125,4 h  │ R$ 73,59/ha-op   │
│ ▸ Adubação a lanço            │ Janela não informada │ out/26 – jun/27 │ Trator 03 + Distribuidor 3 t                  │ 18,00 ha/h │     724 ha-op   │        40,2 h  │ R$ 12,94/ha-op   │
│ ▸ Colheita de grãos           │ Janela não informada │ fev/27          │ Colhedora Axial-Flow 7250 + trator com graneleiro │  5,00 ha/h │     610 ha-op   │       122,0 h  │ R$ 229,20/ha-op  │
│ ▸ Colheita de café            │ Janela não informada │ mai/27          │ Derriçadeiras portáteis · equipe de 6         │  0,35 ha/h │      38 ha-op   │       108,6 h  │ R$ 662,86/ha-op  │
│ ▸ Poda                        │ Janela não informada │ jul/27          │ Trator 04 + esqueletadeira                    │  1,50 ha/h │      38 ha-op   │        25,3 h  │ R$ 165,33/ha-op  │
│ Total                         │                      │                 │                                               │            │                 │       561,8 h  │                  │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
Aplicar plano em 4 cultivos
[‹ Cultivos e planos]                                                                       [Conferir demanda de insumos ›]
```
Linhas da `g_op` executadas (v2calc, `ocorr` por operação). Sem chips de filtro rápido: as 8 linhas têm a mesma Situação (g2lib.js:50).

**`g_cap` aberta** ("Capacidade por mês ▴"; enquanto aberta, a linha de capacidade não mostra o atalho de maior uso). Executado (v2calc, `base.js`). Entre parênteses e em cinza: só a demanda de outra safra aberta da fazenda (aqui, a Safrinha 2027), sem toque.
```text
│ RECURSO             │ MAIOR USO │ MÊS    │ set/26 │ out/26 │ nov/26 │ dez/26 │ jan/27 │ fev/27 │ mar/27 │ abr/27 │ mai/27 │ jun/27 │ jul/27 │ ago/27 │
│ Tratores            │   27 %    │ fev/27 │   2 %  │   9 %  │   8 %  │   7 %  │  <1 %  │  27 %  │  (6 %) │  (4 %) │ (<1 %) │  <1 %  │  15 %  │   —    │
│ Pulverizadores      │   26 %    │ dez/26 │  10 %  │   5 %  │  17 %  │  26 %  │  <1 %  │   —    │ (11 %) │ (10 %) │  (2 %) │   —    │  (2 %) │   —    │
│ Plantadeiras        │   32 %    │ out/26 │   —    │  32 %  │   —    │   —    │   —    │ (39 %) │   —    │  (7 %) │   —    │   —    │   —    │   —    │
│ Distribuidores      │   16 %    │ nov/26 │   —    │   1 %  │  16 %  │   1 %  │   —    │   —    │ (12 %) │   —    │   —    │  <1 %  │   —    │   —    │
│ Colhedoras          │   81 %    │ fev/27 │   —    │   —    │   —    │   —    │   —    │  81 %  │   —    │   —    │   —    │   —    │ (56 %) │   —    │
│ Operadores e equipe │   42 %    │ mai/27 │   1 %  │  12 %  │   5 %  │   4 %  │  <1 %  │  31 %  │  (3 %) │  (3 %) │  42 %  │  <1 %  │  15 %  │   —    │
```
LG2627, recorte da `g_cap` aberta: Operadores e equipe tem Maior uso **1.584 %** (vermelho), Mês nov/26, e as células out/26 a jan/27 mostram "precisa 105", "precisa 127", "precisa 100" e "precisa 108", em vermelho com texto.

**Medidas (simulação de layout, v2calc `layout_c.py`):** linhas da `g_op` visíveis acima da área de ações, com a `g_cap` recolhida.

| Tela | S2627 (8 operações + Total) | LG2627 (6 operações + Total) |
|---|---|---|
| 1440 × 1040 | 9/9 | 7/7 |
| 1366 × 768 | 8/9 | 7/7 |
| 1280 × 800 | 8/9 | 7/7 |
| 1280 × 689 e 1366 × 657 (área útil de navegador) | 5/9 | 5/7 |

Com a `g_cap` aberta a 1280 × 800, sobra 1 linha: por isso ela vem recolhida e nunca abre sozinha. A página não rola em nenhum caso; a área de dados rola por dentro.

### 2.2 Celular, 390 × 844 e 360 × 800
```text
┌──┬─────────────────────────────────────┐
│≡ │ Fazenda Santa Rita · Safra 2026/27  │
│  │ Planejar safra                      │
│  │ [Etapa 3 de 4 · Dimensione operações│
│  │  e recursos ▾]                      │
│  │ Operações e recursos                │
│  │ Custo de operação R$ 264.617,07 ·   │
│  │ máquinas e pessoas, sem insumos ·   │
│  │ Resumo da safra                     │
│  │ ● Na estimativa mensal, cabe nos 690│
│  │ ha com plano. Fora da conta: T4, T3,│
│  │ P1 e P2 (475 ha), sem plano. Prazo  │
│  │ por talhão não verificado: 17 de 17 │
│  │ atividades sem janela.              │
│  │ Maior uso: Colhedoras 81 % · fev/27 │
│  │ Capacidade por mês ▾                │
│  │ [Buscar…] 8 de 8      Expandir tudo │
│  │ OPERAÇÃO › …        │ SITUAÇÃO   │ →│
│  ├─────────────────────────────────────┤ ← área de ações presa (engine.py:1049)
│  │ Aplicar plano em 4 cultivos         │
│  │ [‹ Cultivos e planos][Conferir      │
│  │  demanda de insumos ›]              │
└──┴─────────────────────────────────────┘
```
- **Sem rolagem horizontal da página.** As grades rolam por dentro, com a 1ª coluna presa e limitada a 45 % (g2lib.js:274-277).
- **Sem rolar** (simulação, `layout_m_d.py`): veredito, atalhos e primária aparecem nos 4 casos (S2627 e LG2627, a 390 e a 360). O cabeçalho da `g_op` também aparece nos 4; a 1ª operação, em 3.
- **Ao abrir a `g_cap`,** ela entra na vista (`scrollIntoView`, `block:'nearest'`). Sem isso, a 360 apareceriam 5/6 linhas (S2627) e 3/6 (LG2627); a 390, 6/6.
- **Colunas da `g_cap` no estreito.** Cabeçalho da 1ª coluna só "Recurso". Simulação (`largura_v2.py`): sem o limite de 45 %, a coluna Mês fica cortada em 15 px a 390. Com o limite, Recurso, Maior uso e Mês cabem inteiros (especificado; L2 mede).
- **Situação** é a 2ª coluna da `g_op`: nome e situação aparecem sem rolar de lado.

---

## 3. Topo e grades

### 3.1 Veredito
Uma função `veredito` dá o texto e a cor do `<span role="status">`, com cor e texto (PRD 4.2). Vale a primeira regra que se aplica. O veredito é **o único lugar** destes fatos: a decisão, quanto falta e o que ficou fora da conta.

| # | Condição | Cor | Texto (executado, v2calc `base.js`, `cen.js`, `janela.js`) |
|---|---|---|---|
| R0 | nenhum cultivo com plano | — | o bloco não aparece; nota e "Aplicar plano em N cultivos" (safra.js:892, como hoje) |
| R1 | nenhuma ocorrência desta safra no calendário | cinza | S2526: "Capacidade não calculada: as 21 ocorrências desta safra ficam fora do calendário do protótipo (set/26 – ago/27)." |
| R2 | alguma célula com demanda desta safra tem necessárias > unidades (§3.3) | vermelho | LG2627: "Falta recurso: Operadores e equipe precisam de 127 em nov/26 e você tem 8 (9 meses); Tratores, 10 em out/26 e você tem 4 (4 meses). Inclui 56 ocorrências ainda sem alocação. Fora da conta: 75 ocorrências antes do início da safra (01/09/2026)." |
| R3 | pendência sem falta de recurso: sem conjunto, sem rendimento, janela, sequência ou tarifa desconhecida | âmbar | S2627 com janela de 50 h na Colheita: "Cálculo incompleto: Colheita de grãos com 48 ha sem conjunto (as janelas não comportam toda a área). Fora da conta: T4, T3, P1 e P2 (475 ha), sem plano." |
| R4 | algo fora da conta | âmbar | S2627: "Na estimativa mensal, cabe nos 690 ha com plano. Fora da conta: T4, T3, P1 e P2 (475 ha), sem plano. Prazo por talhão não verificado: 17 de 17 atividades sem janela." |
| R5 | nenhuma das anteriores | verde | S27SF: "Na estimativa mensal, cabe com o que você tem. Prazo por talhão não verificado: 7 de 7 atividades sem janela." Com todas as janelas: "Na estimativa mensal, cabe com o que você tem." |

**Regras do texto:**
- **R2.** Um trecho por recurso em falta, do mais apertado para o menos (necessárias ÷ unidades), no mês de maior necessidade (empate: o 1º). Entre parênteses, o número de meses quando a falta se repete.
  - Quando a falta só aparece somando outra safra: ", somando a Safrinha 2027 (67,3 h)".
  - "Inclui N ocorrências ainda sem alocação." vem quando há pendente: elas estão na demanda (§3.3). Singular com 1.
  - Com área sem horas calculáveis: "N ha sem horas calculáveis ficam fora: a falta pode ser maior."
- **"Fora da conta: …"** entra em R2, R3 e R4, uma vez, com os motivos separados por ";": cultivos sem plano (nomes de `safLocs`, safra.js:866, e a área), ocorrências antes do início, fora do calendário ou depois do fim (§3.4).
- **"Na estimativa mensal, "** abre todo veredito que diz "cabe" (R4 e R5). Pelo PRD 44.4 (PRD.md:7184), a conta mensal não prova viabilidade.
- **Prazo.** "Prazo por talhão não verificado: J de M atividades sem janela." entra só em R4 e R5, quando J > 0.
  - M = atividades (operação + atividade) com ocorrência no calendário.
  - J = as que têm alguma configuração com área necessária e janela vazia (`H = Infinity`, safra.js:60).
  - A conta é por atividade porque a janela é de cada atividade (§4.1). A cor não muda: a janela é opcional (processo_safra.py:145).
- **Sem controle dentro do `role=status`.** Os atalhos ficam fora dele (§3.2).
- **R1 em safra encerrada.** `outrasSafras` devolve vazio quando a própria safra é encerrada.

### 3.2 Linha de capacidade e custo
- **Atalhos de capacidade** (botões, fora do `role=status`). Fazem o mesmo que a célula: gravam `state.cap` e filtram a `g_op`.
  - Sem falta: um atalho, "Maior uso: Colhedoras 81 % · fev/27" (maior ocupação entre as células com demanda desta safra).
  - Em R2: um atalho por recurso em falta, no mês de maior uso: "Operadores e equipe 1.584 % · nov/26", "Tratores 234 % · out/26". Com mais de 3, "e mais N".
  - Enquanto a `g_cap` está aberta, os atalhos saem (a grade mostra o mesmo).
- **"Capacidade por mês ▾"** abre e recolhe a `g_cap` no lugar (`aria-expanded`). O estado fica em `state.capAberta` enquanto a página estiver aberta. **Nunca abre sozinha**, nem no vermelho (§2.1).
- **Custo de operação**, na linha do título: valor com 2 casas (PRD 10.0, PRD.md:4185), mais um qualificador.
  - Sem ocorrência antes do início: "máquinas e pessoas, sem insumos".
  - LG2627: "inclui R$ 919.906,51 de antes de 01/09/2026; não inclui as ocorrências pendentes".
  - O qualificador aparece em qualquer largura.
- **"Resumo da safra"**: link de texto (`.acoes-lnk`, altura mínima de 24 px) ao lado do custo. Ao fechar o painel, o foco volta a ele.
- **Não há faixa de indicadores.** Área com plano e pendências estão no veredito; maior uso, nos atalhos e na `g_cap`.

### 3.3 Grade `g_cap`: capacidade por mês
- **Tipo.** G2 só de leitura, `edit=dict(m='pick')`, sem busca, sem ferramentas de cabeçalho, sem total e sem árvore. Ocupação não se soma (PRD 4.3).
- **Linhas:** os 6 grupos de `RECURSOS` (dados2.py:100-107), na ordem de lá.
- **Base declarada.** É a matriz mensal por recurso do PRD 44.4 e 44.6 (PRD.md:7180, :7196). Os meses são uma variável só, a ocupação, ao longo do tempo. O limite de sete colunas úteis (PRD.md:287) vale para colunas de atributo, como no AG-02 (PRD.md:6627).

| Coluna | Célula | Regra |
|---|---|---|
| Recurso | "Colhedoras" | presa; no estreito, até 45 % |
| Maior uso | "81 %"; "1.584 %" em vermelho | maior ocupação entre as células com demanda desta safra; vermelho com texto se a linha tem falta; "não calculável" se toda célula com demanda tem capacidade 0; "—" sem demanda |
| Mês | "fev/27" | mês do maior uso, como data tipada; empate: o 1º |
| meses do período da safra | "27 %", "<1 %", "(6 %)", "precisa 127", "—" | meses do calendário dentro do período (dados2.py:15-17), mais mês com demanda desta safra fora dele. Sem interseção (S2526), o calendário inteiro. S2627 e LG2627: 12 meses; S27SF: fev/27 a jul/27 |

**Conta (bloco CAPACIDADE, uma fonte para tela, filtro, chips, prévia e espelho):**
- **Capacidade** do grupo k no mês = unidades × horas de uma unidade. Horas de uma unidade = dias úteis × jornada × turnos × disponibilidade; para pessoas, × (1 − absenteísmo) e turnos = 1. É a mesma aritmética de safra.js:755-760.
- **`cargaRec(i, k)`** = Σ por configuração j da ocorrência de `x.nh × rc_j[k]`. `x.nh = x.h + x.fh` é o necessário (safra.js:273): atendido mais o que falta, inclusive o de "sem recurso na fazenda".
  - Área sem horas calculáveis (sem rendimento, sem conjunto, partes abaixo de 100 %) não entra. Marca a célula com "≥", e o `aria-label` diz "mais N ha sem horas calculáveis".
  - Base: PRD 53.2, "inclui demanda atribuída ao recurso ainda sem alocação factível… não truncar déficit" (PRD.md:8308).
- **Demanda da célula** = Σ `cargaRec` das ocorrências desta safra no mês + as de `outrasSafras(self, saf)`.
  - `outrasSafras` usa o predicado de safra.js:344: outra safra, não encerrada (`!r.ro`), da mesma fazenda. É a mesma regra do estoque; espelho em dados2.py:806-809.
  - A LG2627 (outra fazenda) e a S2526 (encerrada) não entram na S2627.
  - **Elegibilidade pela safra de origem (SAF-C02, 09/10/2026):** a etiqueta de cada ocorrência (antes do início, depois do fim, fora), desta e das outras safras, sai do período da safra dela, qualquer que seja a aberta; a carga das outras que fica fora vai ao "Fora da conta" do veredito (número, motivo e horas, nos meses com demanda desta safra), à linha do filtro e ao `aria-label`. Dano evitado: o mesmo mês dar falta de recurso numa safra e folga na outra só pela navegação.
- **Ocupação** = demanda ÷ capacidade. Capacidade 0 com demanda: "não calculável" (53.2); nunca divide por zero.
- **Necessárias** = max(teto(demanda ÷ horas de uma unidade), maior `rc[k]` de uma configuração com área necessária no mês). É o "postos simultâneos" do PRD 44.4 e a mesma regra do motivo de safra.js:65.
- **Falta** quando necessárias > unidades.

**Célula de mês** (`fmtOcup`, função única para célula, `aria-label`, linha de filtro, atalhos, chips e espelho):
- **Com demanda desta safra:** "<1 %" quando 0 < ocupação < 1 %; senão o inteiro arredondado.
- **Com falta:** vermelho com o texto "precisa N". O % vai no `aria-label`.
- **Só de outra safra:** % entre parênteses, em cinza, sem toque. `aria-label` "só Safrinha 2027". Não entra no maior uso nem no veredito.
- **Sem demanda:** "—". Nunca "—" em mês com pendente sem recurso: a demanda dela está na célula.
- **Sem negrito.** A coluna Maior uso já diz o pico.

**Toques** (uma célula, um comportamento):
- **Recurso, Maior uso, Mês, ou Enter na linha:** `abrirRec` abre o formulário existente de `g_recp_*` via `g2open` (§4.2).
- **As 12 células de mês ficam fora do clique da linha.** Campo `nr:true` na coluna; g2lib.js:179 acrescenta `g2nr`; o `closest` de g2lib.js:96 e :191 passa a incluir `.g2nr`. Vai como classe, porque nenhum molde emite `data-noedit` e um atributo com valor "false" também casaria com o seletor.
- **Célula com demanda desta safra:** a parte `act` ocupa a célula inteira (opção `full`: `width:100%`, `min-height:44px`; docs/design-system/README.md:16).
  - `aria-label`: "Colhedoras, fev/27: 81 %, 122 h de 150,5 h, precisa de 1, tem 1".
  - O toque grava `state.cap={rec,mi}`. Tocar de novo limpa.
- **"—" e células cinza:** inertes, sem parada de Tab.

### 3.4 Grade `g_op`: operações
São 8 colunas: o identificador e 7 úteis (PRD 4.3). Uma variável por coluna e a unidade na célula.

| # | Coluna | Operação | Atividade | Talhão (ocorrência) | Configuração (só quando a atividade divide) |
|---|---|---|---|---|---|
| 1 | Operação › atividade › talhão | **nome** + "6 atividades" (de `atvEmUso`) | nome | "T2 · Soja 62 X" | nome do conjunto |
| 2 | Situação | ver abaixo | idem | idem | só "sem rendimento" e "em sequência" |
| 3 | Data | faixa real de meses (menor a maior `dt`, em qualquer ano): "set/26 – jan/27" | idem | "18/10/2026" (`dcol`) | vazio |
| 4 | Conjunto | o nome, se comum às atividades em uso; senão "varia" em cinza; "2 conjuntos" quando a única atividade divide | vazio quando a operação mostra; senão o próprio | vazio | vazio |
| 5 | Rendimento | "21,60 ha/h" pela mesma regra; senão "varia" | idem | vazio | "6,80 ha/h", "2,93 ha/h" |
| 6 | Área trabalhada | Σ, **"2.520 ha-op"** | Σ, "610 ha" | área do cultivo | área atendida, "208,41 ha" |
| 7 | Horas-conjunto | Σ, "116,7 h"; vazia se tudo está pendente, nunca 0 h | idem | idem | h da configuração |
| 8 | Custo R$/ha | custo de operação ÷ área atendida, nunca somado: **"R$ 14,49/ha-op"** | "R$ 14,49/ha" | idem | "R$ 58,20/ha" e "R$ 109,40/ha" |

- **Unidade ha-op.**
  - Na linha da operação, a área e o custo usam "ha-op", porque a operação soma passadas (PRD.md:7150, :8143).
  - Atividade, talhão e configuração usam "ha", porque são uma passada por cultivo. Guarda: atividade que repete cultivo (duas atividades com o mesmo `nome|op` num plano, safra.js:670) também usa "ha-op".
  - `r.s.area` e `r.s.rha` já levam a unidade; `g2unf` não a duplica (g2lib.js:9-10) e a ordem lê `r.v`.
  - Os cabeçalhos ficam "Área trabalhada" e "Custo R$/ha" (escolha do proprietário, RETOMADA-NUVEM.md:202).
  - O cabeçalho da coluna 6 ganha ajuda (`title`): "ha-op = hectares-operação: cada passada conta; 3 passadas em 10 ha = 30 ha-op (PRD 44.1)". As células "ha-op" ganham `aria-label` com "hectares-operação".
- **Situação** (`s.sit` = "Com pendência" | "Janela não informada" | "Cabe na janela"):
  - **Com pendência:** os chips de `avisos` (safra.js:681-686) e o chip de capacidade "Colhedoras 121 % · fev/27" (vermelho), quando um recurso que a linha usa falta no mês dela (sai de `cargaRec` e `capSaf`). O chip de pendente sem recurso diz o tamanho: "sem recurso na fazenda · precisa de 10, tem 8".
  - **Janela não informada:** texto cinza, sem chip, quando alguma configuração com área necessária tem a janela vazia.
  - **Cabe na janela:** verde, quando todas têm janela e não há pendência. Na operação e na atividade, vale se todas as filhas cabem.
  - **Etiqueta do calendário** (chip cinza, uma por linha, de `classeOc` com `ini`/`fim` de `g_saf`): "antes do início da safra · N" (dt < início), "fora do calendário · N" (dentro da safra e `mi < 0`), "depois do fim da safra · N". Conta no custo, na área e nas horas; não conta na capacidade.
  - **Sem números além do chip.** Trio, motivos, decorrido e "precisa de … faltam …" vão para o formulário (§4.1, "Neste talhão"). Fundamento: PRD 4.3 (PRD.md:287, :295).
  - **Sem repetir o pai.** Uma linha filha só mostra "Janela não informada" ou "Cabe na janela" quando difere do pai. Chips de problema aparecem sempre onde ocorrem.
- **Árvore.** Operação › atividade › talhão › configuração (safra.js:709-723). Vem recolhida; só as operações com pendência abrem. A ordem é a da 1ª data. Mostra só as atividades em uso (a `g_op` sai de `ocorr`).
- **Total:** só Horas-conjunto. Não há total de área nem de R$/ha.
- **Ferramentas:** busca (acha o talhão pelo nome); contador "N de M"; filtro rápido `qf` sobre `s.sit`, que só aparece com 2 categorias ou mais (g2lib.js:50); filtro e ordem por coluna (G2); "Expandir tudo".
- **Toques** (`edit m='pick'`; a seta só expande; t07 continua):
  - **Operação**, com Conjunto e Rendimento comuns: `abrirRend` abre a folha da 1ª atividade em uso com "Aplicar em: Todas as atividades da operação". Senão o toque expande.
  - **Atividade de uma configuração:** a folha dela, com "Só esta atividade".
  - **Atividade dividida:** expande.
  - **Talhão:** a folha da atividade, com "Só esta atividade" e a seção "Neste talhão".
  - **Configuração:** a folha (índice `j` de `rp.itens` = ordem de `cfgsOf`). "Aplicar em" não aparece (cond `UMA`); a seção "Nesta configuração" aparece.

### 3.5 Linha de filtro (entre `g_cap` e `g_op`)
- **Quando aparece:** com `state.cap`.
- **Texto, igual para máquinas e pessoas:** "Mostrando **Tratores · fev/27**: 189,3 h de 699,2 h (27 %) · desta safra 122,0 h · Safrinha 2027 67,3 h · precisa de 2, tem 4 · [Ver todas]". A parte das outras safras só aparece quando existe.
- **Efeito na `g_op`:**
  - Mostra só as ocorrências desta safra daquele mês com `cargaRec > 0`, inclusive as pendentes sem recurso, com a árvore aberta até o talhão.
  - A 7ª coluna passa a "Horas de <recurso>" (o `PREVALS` grava `GR('g_op').cols[6].l`; o cabeçalho lê `c.l` depois do `PREVALS`, engine.py:1436-1437).
  - Valores: ocorrência `cargaRec(i,k)`; configuração `x.nh × rc_j[k]`; atividade e operação Σ. Configuração que não usa o recurso mostra "não usa" em cinza.
  - O Total fecha com "desta safra" por construção.
  - Área trabalhada e Custo R$/ha continuam da ocorrência inteira.
- **Estado:** ao gravar ou limpar `state.cap`, sai `f.horas` e a ordem em 'horas' da `g_op`. Quem limpa: "Ver todas", `pick`, `pickat` e a troca de safra.
- **Foco:** vai para a linha (`role=status`), que entra na vista.

---

## 4. Detalhe e edição

### 4.1 Formulário Rendimento (`REND_EDIT`)
- **Abertura.** `abrirRend(self, linha)` acha a folha em `g_rend_<safra>` (`cfgsOf`) e chama `g2open`. Depois grava `esc` em `draft` e `orig`: operação "Todas as atividades da operação"; atividade e talhão "Só esta atividade"; configuração `''`.
- **"Aplicar em" sempre visível** (cond `UMA`). Esconder recriaria a cópia silenciosa (g2lib.js:111 + safra.js:465).
  - Ajuda (processo_safra.py:131): "Todas: conjunto, rendimento, custos e diesel vão para as outras atividades desta operação em uso nesta safra. As divididas entre conjuntos e as de planos ainda não aplicados ficam como estão. A janela é de cada atividade."
- **"Todas" só alcança atividades em uso.** Em `rendAfter` (safra.js:465-468), o laço pula `!uso.has(k.v.atv)`, com `uso = atvEmUso(self, saf, op)`, a mesma fonte do "N atividades" da `g_op`.
  - `n` e `nd` do aviso contam só essas.
  - As de planos ainda não aplicados mantêm o valor; quando um plano as traz, a operação mostra "varia".
- **Janela.**
  - Duas entradas `jan` com conds que se excluem, como os dois `nome` (processo_safra.py:133-134): uma com cond `MULTI` (configuração e "Nova configuração"), outra com cond `esc = 'Só esta atividade'`.
  - Em "Todas", aparece só o campo de leitura `jan_op`: "Janela por talhão: é de cada atividade · 1 de 6 com janela (Dessecação pré-plantio 8 h) · para mudar, toque na atividade." Conta só as atividades em uso.
  - **Guarda em `rendCheck`** (safra.js:421): com `multi = 'não'`, `esc` diferente de "Só esta atividade" e `jan` diferente do salvo, dá erro em `esc`: "A janela é de cada atividade. Para gravar 8 h, escolha 'Só esta atividade'." O que foi digitado fica.
- **Campos, validações e ações de hoje, na mesma ordem.**
  - Conjunto; Descrição ou Prestador; Como obter o rendimento; Largura 0,5–60 m, Velocidade 0,5–30 km/h, Eficiência 10–100 %.
  - Rendimento ao vivo ou Informado ≥ 0,01 ha/h.
  - Máquina, Implemento, Pessoas, Custo por pessoa; Custo por hora ao vivo, com a composição (DEC-2609-03); Diesel 0–200 L/h.
  - Parte, Trabalha e Troca (só com várias configurações).
  - `rendCheck` (pessoas inteiras; partes fixas ≤ 100 %); "+ Outra configuração" e "Remover".
- **Novos campos só de leitura, ao vivo, sem fórmula nova:**
  - **Custo R$/ha:** `custoHa(custo_h, rend)`, a mesma função de `compRend` e `rendAfter`.
  - **Custo R$/kg:** só na colheita, via `prodColheita`, por cultura e sem média, ou "não calculável". Aparece por uma marca `colh` com cond.
  - **Origem:** calculada por `origemCfg`, sem ler `v.aj`.
    - É "Padrão do cadastro (CD-02)" só quando a configuração é igual ao conjunto padrão da operação: `D2.conj` com id = `cfgBase` e `D2.conj_opts[base].atual`.
    - Compara conj_id, modo, largura/velocidade/eficiência (ou rendimento no Informado), maq, impl, pess, pess_rs e diesel. O rendimento calculado fica fora.
    - Nos outros casos, "Ajustado nesta safra". Vem de `rendLive(k='origem')`, então muda ao digitar.
- **Seção só de leitura "Neste talhão"** (aberto pela linha do talhão): motivo (`rp.motivos`) e o trio Necessário / Atendido / Saldo em ha e horas-conjunto; com 2 ou mais configurações, o decorrido. **"Nesta configuração"** (aberto pela configuração): "precisa de N ha = H h · faltam F ha = W h". Mesma conta de `repartir`.
- **Safra encerrada (S2526):** só consulta (`m='ro'`).

### 4.2 Formulário Recurso (`g_recp_maq` / `g_recp_pes`)
- **Abertura:** `abrirRec(self, rid)` → `g2open`.
- **Campos e limites de hoje:** Unidades ou Pessoas 0–50; Jornada 1–24 h/dia; Turnos 1–3 (só máquinas); Disponibilidade 1–100 % ou Absenteísmo 0–90 %.
- **Subtítulo:** "Conta as safras abertas desta fazenda. Cadastro único no protótipo: mudar aqui muda também a outra fazenda." Na S2526, mais: "Para ajustar, abra uma safra aberta."
- **Campos só de leitura, ao vivo** (`g2live` atende `g_recp_*`):
  - "Horas de uma unidade em fev/27: 174,8 h" (Tratores: 19 × 10 × 1 × 0,92);
  - "Horas na safra no calendário (set/26 – ago/27): 366,9 h": Σ `cargaRec` desta safra;
  - **Prévia:** "Maior uso: 27 % → 22 % (fev/27)". Com falta: "· precisa de 6, tem 5", em vermelho. Quando muda quem trabalha: "· Colheita de café · Derriçadeiras portáteis · equipe de 6 deixa de trabalhar em 1 ocorrência" ou "… volta a trabalhar em 56 ocorrências". O nome sai do motivo de safra.js:65.
- **Como a prévia calcula.** Recalcula a demanda com os pools do rascunho.
  - Guarda do último `ocorr` desta safra e das `outrasSafras`: área, `mi` e `cfs.map(cfgIn)`.
  - Roda `repartir` de novo só nas ocorrências em que alguma configuração tem `rec[rid] > 0`. É exato: as outras não mudam (0 de 16.354 verificações, executado pelo revisor, `mn02/sweep.py`).
  - Chama `capSaf(self, oc, pools)`, sem fórmula nova.
  - Custo: `ocorr` da LG2627 leva 9,8 ms no node (executado, v2calc). O critério é até 100 ms por tecla no navegador; acima disso, recalcula ao sair do campo.
- **Nota fixa:** "Prévia desta safra, somando as safras abertas desta fazenda. Ao salvar, todas as safras são recalculadas."
- **Safra encerrada:** o `PREVALS` marca `r.ro` nas linhas de `g_recp_*` (como `rendRo`, safra.js:365).
  - Fundamento: PRD 52.1, "safra encerrada fica em consulta" (PRD.md:8241).
  - Dano evitado: a S2526 não tem demanda no calendário, então a prévia mostraria 0 % enquanto salvar muda a capacidade das safras abertas. Quem edita ali decidiria sem ver o efeito.

### 4.3 Painel "Resumo da safra"
- **Formato:** `aside` em EXTRA, no padrão do painel "Aplicar plano", com Fechar e Esc. O foco volta ao link. Lista simples, não G2. Dinheiro com 2 casas.
- **Custo por cultura** (`resumoCultura`, espelho `dados2.resumo_cultura`). Executado (v2calc), S2627:

  | Cultura | Área com plano | Custo de operação | Insumos do plano | Custo total R$/ha (ha físico com plano) |
  |---|---|---|---|---|
  | Soja | 610 ha | R$ 230.032,11 | R$ 1.283.143,00 | R$ 2.480,61/ha |
  | Café | 38 ha | R$ 33.497,55 | R$ 94.848,00 | R$ 3.377,51/ha |
  | Mamão Formosa | 42 ha | R$ 1.087,41 | R$ 20.559,00 | R$ 515,39/ha |
  | Total | 690 ha | R$ 264.617,07 | R$ 1.398.550,00 | — |

  - Agrupa a saída de `ocorr` por `c.v.cult` e herda dela a regra de cultura (safra.js:323) e dos ajustes '-' e '+' (safra.js:327-329). A área de cada cultivo com plano válido entra uma vez.
  - R$/ha só quando não há pendente nem tarifa desconhecida. Senão "parcial · N ocorrências pendentes". LG2627, Mamão Formosa: "parcial · 56 ocorrências pendentes".
  - Com ocorrências antes do início, a linha da cultura diz quanto: LG2627 "inclui R$ 919.906,51 de operação e R$ 1.789.941,59 de insumos antes de 01/09/2026".
- **Nota do quadro:** "Insumos do plano: dose × área × preço de todas as datas, antes do estoque. Deles, R$ Y são de antes de hoje (23/09/2026, já realizados) e R$ Z de hoje em diante (a 'Demanda bruta' da etapa 4). A necessidade líquida está na etapa 4."
  - Z = Σ `bruta × preço` de `demanda`; Y = total − Z, para a soma exibida fechar (mesma regra do `nm`).
  - Executado: LG2627 Y = R$ 1.853.460,49 e Z = R$ 1.846.704,17. Na S2627, Y = 0 e o texto diz "Todos de hoje em diante".
- **Trabalho da safra:** "5.234 ha-op (hectares-operação) · 561,84 horas-conjunto · 1.241,95 horas-homem · 6.876,08 L de diesel estimado (9 ocorrências sem L/h)".
  - LG2627, mais: "das quais antes do início: 4.061,60 ha-op · 2.654,23 horas-conjunto · 18.758,32 horas-homem · 17.097,99 L"; "horas-homem no calendário: 15.351,14".
- **Como a conta é feita:**
  - capacidade = unidades × dias úteis × jornada × turnos × disponibilidade; para pessoas, × (1 − absenteísmo) e turnos = 1;
  - ocupação = demanda ÷ capacidade; a demanda inclui o que ainda não tem alocação (PRD 53.2);
  - necessárias = o maior entre teto(horas ÷ horas de uma unidade) e a maior equipe que trabalha ao mesmo tempo;
  - soma as safras abertas desta fazenda;
  - dias úteis: set/26 24 · out/26 22 · nov/26 23 · dez/26 21 · jan/27 21 · fev/27 19 · mar/27 22 · abr/27 23 · mai/27 24 · jun/27 24 · jul/27 25 · ago/27 25;
  - "estimativa mensal: a ocorrência entra inteira no mês da data e não prova viabilidade; o conflito por semana e turno fica em Ordem de Serviço › Recursos" (PRD 44.4; DEC-2609-09);
  - "a capacidade usa o plano inteiro, pela data do plano, sem descontar o realizado das O.S." (§7);
  - "sem janela, o prazo por talhão não é verificado";
  - "ha-op: cada passada conta; Custo R$/ha-op = custo da operação ÷ ha-op; custo total R$/ha da cultura = (operação + insumos) ÷ área com plano (PRD 44.1, 51.4)";
  - "ocorrências antes do início, fora do calendário ou depois do fim contam no custo e não na capacidade".

### 4.4 Ao salvar (os dois formulários)
- O `PREVALS` recalcula `ocorr`, `g_op`, `g_cap`, veredito e linha de capacidade no lugar (safra.js:652). A linha de origem pisca (`fl`) e recebe o foco.
- **Aviso antes → depois.** O "antes" é guardado no `g2check`; o "depois" sai de `ocorr` + `capSaf` num `setTimeout(0)` após o `g2set`. O aviso substitui "Plano operacional e recursos recalculados".
- **Exemplo executado** (v2calc `o9.js`), Adubação de cobertura de 24 para 12 m, só esta atividade: "Adubação de cobertura · Trator 03 + Distribuidor 3 t: 9,00 ha/h · R$ 25,89/ha. Adubação a lanço: 40,2 → 74,1 h · Distribuidores nov/26: 16 % → 31 %."

---

## 5. Ações, numeração, endereços e retomada

### 5.1 Faixa de etapas (6 → 4)

| Nº | Faixa (verbo) | `SAF_CURTO` (retorno) | Antes |
|---|---|---|---|
| 1 | Escolha a safra | Escolha da safra | 1 |
| 2 | Defina cultivos e planos | Cultivos e planos | 2 |
| **3** | **Dimensione operações e recursos** | **Operações e recursos** | 3 + 4 + 5 |
| 4 | Confira a demanda de insumos | Demanda de insumos | 6 |

`g2steps(self,v,'stp',4,…)`, laço `s1..s4`. `whys`: "Aplique um plano" vale para i ≥ 3. No celular: "Etapa 3 de 4 · Dimensione operações e recursos".

### 5.2 Área de ações (`safAcoes`)

| Estado | Nota e atalho | Retorno | Primária |
|---|---|---|---|
| Etapa 2 | do PR-B (saf2 §5.1); esta fatia muda só o rótulo do avanço | — | "Dimensionar operações ›" (consulta: "Ver operações e recursos ›") |
| Etapa 3 | — | ‹ Cultivos e planos | **Conferir demanda de insumos ›** |
| Etapa 3 com cultivo sem plano | só o atalho "Aplicar plano em N cultivos" → `openApply(self, apIds)`, sem texto (o veredito já diz) | ‹ Cultivos e planos | Conferir demanda de insumos › |
| Etapa 3 sem nenhum plano | "Nenhum cultivo tem plano agronômico: operações, recursos e demanda dependem dele." | ‹ Cultivos e planos | Aplicar plano em N cultivos (safra.js:892, `step<4`) |
| Etapa 3, safra encerrada | — | ‹ Cultivos e planos | Ver demanda de insumos › |
| Etapa 4 | igual à etapa 6 de hoje; "Corrigir cultivos" → 2; "Voltar à revisão ›" → 4 | ‹ Operações e recursos | Enviar para cotação / Abrir Compra de insumos › |

- **Falta de recurso é aviso, não trava.** Planejar não reserva, não contrata e não compra, então travar não evitaria dano concreto (AGENTS §4). Avançar não envia nada.
- **Um comando, uma instância**, com um rótulo. Comandos de conteúdo dentro do bloco: "Resumo da safra", atalhos de capacidade, "Capacidade por mês", célula da `g_cap`, busca, filtro rápido, "Expandir tudo", "Ver todas". Nada no topo duplica "Aplicar plano" nem "Com pendência". A meta de duplicatas continua 0.

### 5.3 Endereços
- **Novo formato, por nome:** `#saf=<id>&passo=safra|cultivos|operacoes|demanda`. Não quebra numa renumeração futura.
- **Formato antigo:** `etapa=N` é sempre lido na numeração de 6. O código novo nunca grava `etapa=`.

| Endereço | Abre |
|---|---|
| `etapa=1` / `etapa=2` | 1 / 2 |
| `etapa=3`, `4`, `5` | **3** |
| `etapa=6` (links antigos: favoritos, histórico, textos) | **4** |
| só `saf=`, ou `etapa` fora de 1–6 | 4 |
| `passo=operacoes` / `passo=demanda` | 3 / 4 |

- `abrirHash` (safra.js:852-856): sai o `Math.min(6,…)` e entra a tabela. Vale na carga e no `hashchange`.
- **A origem gravada não é lida.** A Compra recalcula `x.origem` por `safHref` (processo_compras.py:166, 175). `safHref` e `origem.h` (safra.js:1011) passam a gerar `passo=demanda`.
- **Avisos sem número de etapa:** `pickat` (safra.js:845) e `abrirHash` (:855) passam a "Safra aberta: Safrinha 2027 · Demanda de insumos".
- **Textos** "Planejar safra · etapa 6", "Ver origem · etapa 6 ›" e "(etapa 6)" passam a "Planejar safra · demanda de insumos" e "Ver origem · demanda de insumos ›". Arquivos: processo_compras.py:175, 278, 322, 476, 487, 490, 496, 505, 576; safra.js:1018; dados2.py:692; suprimentos.py:489. A "etapa 3/6" da própria Compra não muda.
- **Guardas estáticos** (executado, v2calc; hoje acham 2 e 14 linhas):
  - `grep -nE "['\"][^'\"]*[#&?]etapa=" safra.js areas/processo_compras.py` = 0;
  - `grep -rnE "Planejar safra[^'\"]{0,40}etapa [0-9]|Safra aberta: '[^;]*etapa " safra.js dados2.py areas/*.py` = 0, ignorando comentários.
- **Gravar o passo** no endereço com `history.replaceState` ("sair e retomar", UX-01) fica no PR 6.

### 5.4 Retomada da etapa 1 (`proxSaf`, safra.js:647-651)
Esta fatia muda só os números (6 → 4, 4 → 3) e o rótulo final. O texto do caso sem cultivo é do PR-B ("Continuar: planejar talhões", saf2/especificacao.md:69).
- Encerrada → "Consultar safra" (2).
- Com cultivo sem plano → "Continuar: aplicar plano em N cultivos" (2).
- Sem solicitação → "Continuar: enviar demanda para cotação" (**4**).
- Senão → **"Continuar: dimensionar operações e recursos" (3)**.

---

## 6. Cortes e fusões

| Dado (onde está hoje) | Decisão | Motivo | Onde continua |
|---|---|---|---|
| Grade de rendimentos com 42 atividades de todos os planos (3) | sai da tela (espera P2) | 25 das 42 não são da S2627 | `g_rend_*` como fonte; formulário; CD-02 |
| Coluna Operação repetida; 31 linhas iguais à operação (3) | funde | duplicado | linha-pai; a atividade só mostra a exceção |
| Coluna Planos (3) | corta | duplicado da etapa 2 | etapa 2 |
| Modo, Largura, Velocidade, Eficiência, Custo R$/h, R$/kg (3) | passam ao formulário (proposta P2) | entradas de um resultado que já aparece | formulário, com a composição |
| Parte, Trabalha e Janela (3 e 4) | passam ao formulário | Janela vazia em 100 % das linhas; Parte e Trabalha só no Plantio | formulário; o efeito aparece na Área e na Situação |
| Selo "ajustado nesta safra" (3) | troca | `v.aj` mente depois do "Todas" e no prestador | campo Origem calculado |
| Frase k4 com 6 números (4) | funde | repetia o Total | custo na linha do título; Resumo |
| "R$ 1.427,61/ha da safra" (4) | **corta** | divide o custo de 690 ha por 1.165 ha | Resumo por cultura, com a base declarada |
| Gatilho, Mês, Talhão e Decorrido em coluna (4) | cortam ou fundem | regra do plano; derivado da data; repete o nome; só decide quando passa da janela | Planos agronômicos; Data; nome e busca; formulário "Neste talhão" |
| Custos de operação, insumos e total por linha; R$/ha com insumos (4) | corta | o mesmo dinheiro 5 vezes; mesmo rótulo com outro sentido | custo de operação; Resumo; etapa 4 |
| Diesel em coluna, Total e matriz (4) | corta | não decide capacidade | L/h no formulário; total no Resumo |
| `g_mat` "Por mês" e "Mostrando só" (4) | corta (espera P1) | 6 indicadores para uma pergunta secundária | custo por mês: P1 |
| Alternâncias Máquinas/Pessoas e Parâmetros/Por mês (5) | funde | 4 combinações para uma pergunta | `g_cap` única |
| Grade de parâmetros; coluna Unidades (5) | passam ao formulário | premissa que muda pouco | formulário; "tem M" no filtro, no `aria-label` e no veredito |
| "Necessárias no pico" e "Mês do pico" (5) | troca | mostra 1 em tudo e esconde 81 % contra 26 %; pegava Tratores em set/26 | colunas Maior uso e Mês |
| Filhas Demanda, Capacidade, Necessárias e "Você tem" × 12, e saldo em h (5) | corta | deriváveis e repetidas | linha de filtro e formulário |
| "Dias úteis por mês" e fórmula no subtítulo (5) | passa ao Resumo | premissa no topo | "Como a conta é feita" |
| Origem `g_resd` (5) | funde | outra grade para a mesma pergunta | filtro com "Horas de <recurso>" |
| Horas-homem (k4), demanda de Operadores (5) e "Horas na safra" | funde | a mesma conta com dois nomes (`rec.oper = pess`, safra.js:460) | formulário do recurso; Resumo |
| Faixa de 4 indicadores (proposta da v1) | corta | repetia veredito e `g_cap`; "Pendências: Nenhuma" ao lado de veredito âmbar | veredito, linha de capacidade |
| "defina rendimento e janela na etapa 3" (k5) | corta | etapa que deixa de existir | toque na linha |
| Três avanços 3→4→5→6 | funde | editar e ver o efeito no lugar | uma primária |

---

## 7. Regras, invariantes e totais

**Expressões novas:**
1. ocupação = demanda ÷ capacidade (PRD 53.2, `capSaf`);
2. custo por ha físico da cultura = (operação + insumos do plano) ÷ ha físico com plano (`resumoCultura`). É o KPI-CUS-01 com o denominador do GE-03 (PRD.md:8143).

A regra de necessárias usa o motivo que o motor já tem (safra.js:65). Não há outra fórmula nova.

| Invariante | Função | Prova |
|---|---|---|
| D-01; necessário = atendido + saldo; pendente com causa | `repartir` (safra.js:29-280) | 106/106 (executado, v2calc) |
| Capacidade, necessárias, "não calculável" com capacidade 0 | `capRec`, `capSaf` | C1–C7, C11 |
| Demanda inclui o necessário ainda sem alocação; só sai quando outra configuração assume a área | `cargaRec` | C5, C6, C12, C16 |
| Soma as safras abertas da mesma fazenda; a própria encerrada não soma | `outrasSafras` (predicado de safra.js:344) | C2, C7, C8, C17–C19 |
| No filtro, Σ "Horas de <recurso>" = demanda desta safra na célula | `cargaRec` | C21, V4–V7 |
| Rendimento = L × V ÷ 10 × E; custo/h = máquina + implemento + pessoas × R$/pessoa; prestador = só Máquina | `rendCalc`, `rendLive`, `rendAfter` | TF03, AC-72-03, B6b |
| R$/ha = R$/h ÷ ha/h; na ocorrência, custo ÷ área atendida | `custoHa`; `repartir` | 07a/08 |
| "Todas" só nas atividades em uso; não copia janela; atividade dividida não muda | `rendAfter`, `atvEmUso` | O8–O11 |
| Origem calculada contra o CD-02 | `origemCfg` | O13 |
| Insumos = dose × área, sem mudar com a divisão | `ocorr` :330 | `quantidade_test` 14/14 (executado, v2calc); REND 5c |
| Pessoas inteiras; partes fixas ≤ 100 % | `rendCheck` | REND 7; O14 |
| Pendente nunca vira 0 h nem R$ 0; R$/ha da cultura parcial com pendente | `soma`, `avisos`, `resumoCultura` | B1b; P5 |
| Uma etiqueta de calendário por ocorrência; antes + fora + depois + no calendário = total | `classeOc` | C24 |
| Safra encerrada só em consulta | `rendRo`, `m='ro'`, `r.ro` em `g_recp_*` | REND 11, V11 |
| Capacidade, horas e custo são do plano: todas as ocorrências pela data do plano, sem descontar o realizado. Exemplo: dos 49,07 h de Pulverizadores em dez/26, 20,84 h são do Fungicida 1ª aplicação em T1-B e T2, que a OS-0421 já executa (dados.py:94). A projeção = realizado + saldo (PRD 44.1, PRD.md:7150) fica para o CONTROLE-01 | `ocorr`, `capSaf` | registrada nas limitações da homologação |
| A demanda de insumos é igual a `dados2.demanda` na base do PR e não muda com nenhuma ação da etapa 3. Exemplo na `884620c`: S2627 R$ 379.580,00 · 15 itens | `demanda` | paridade (§9.3) |

**Totais por safra** (executado, v2calc `base.js`; espelho `dados2.plano_op` e `dados2.capacidade`). Nenhuma célula fica "—".

| Safra | Ocorrências: antes + fora + depois + no calendário | ha-op | Horas-conjunto | Custo de operação | Horas-homem atendidas (todas as datas) | Horas de Operadores no calendário (demanda) | Diesel estimado (ocorrências sem L/h) |
|---|---|---|---|---|---|---|---|
| S2627 | 33 = 0 + 0 + 0 + 33 (3 divididas) | 5.234,00 | 561,84 | R$ 264.617,07 | 1.241,95 | 1.241,95 | 6.876,08 L (9) |
| S27SF | 14 = 0 + 0 + 0 + 14 | 2.670,00 | 268,52 | R$ 180.888,10 | 460,40 | 460,40 | 5.589,71 L (0) |
| LG2627 | 276 = 75 + 0 + 0 + 201 | 15.422,76 | 5.442,52 | R$ 1.533.499,13 | 34.109,45 | 86.839,80 | 24.091,28 L (104) |
| S2526 | 21 = 0 + 21 + 0 + 0 | 5.360,00 | 421,29 | R$ 252.257,55 | 681,50 | 0,00 (R1) | 7.994,35 L (2) |

- **Horas-homem atendidas** = `plano_op.hh`. **Horas de Operadores no calendário** = Σ `cargaRec(·,'oper')` desta safra (inclui o necessário sem alocação). As duas só coincidem sem pendente e sem ocorrência fora do calendário.
- **LG2627, à parte:**
  - 56 pendentes, 3.216,99 ha e 7.148,87 horas-conjunto sem alocação, todas por "sem recurso na fazenda";
  - Tratores no calendário: 7.914,27 h de demanda, contra 765,40 h atendidas;
  - insumos do plano R$ 3.700.164,66;
  - Plantio de mudas: R$ 1.041.487,44, dos quais R$ 801.492,72 de 9 ocorrências antes do início.
- **Insumos do plano:** S2627 R$ 1.398.550,00 · S27SF R$ 1.098.502,50 · S2526 R$ 1.475.579,00.

---

## 8. Orçamento de atrito

**Especificado: contei pelo código; falta medir no mesmo cenário (M1, AGENTS §3.3).** Antes: a partir da etapa 4, onde o "Continuar" leva hoje. Depois: a partir da etapa 3.

| Tarefa (S2627) | Antes | Depois |
|---|---|---|
| A. Trocar o conjunto **só** da Adubação de cobertura e ver horas e capacidade | 11 toques + busca · 2 seletores · 3 trocas de etapa | expandir 1 · atividade 1 · Conjunto 2 · Salvar 1 = **5 toques · 1 seletor · 0 trocas**; efeito no aviso antes → depois |
| B. Trocar o conjunto da operação inteira | 8 toques · 1 seletor · 3 trocas | operação 1 · Conjunto 2 · Salvar 1 = **4 toques · 1 seletor · 0 trocas** |
| C. Ver por que fev/27 aperta | 6 toques · 2 trocas | **0 toques** para ver o maior uso; atalho = **1 toque** até os 3 talhões |
| D. Passar tratores de 4 para 5 e ver o efeito | 6 toques + 1 dígito · 2 trocas | "Capacidade por mês" 1 · Tratores 1 · Unidades 1 + "5" (prévia) · Salvar 1 = **4 toques + 1 dígito · 0 trocas** |
| E. Pôr no plano os cultivos que ficaram fora | nada avisa nas etapas 3–5; 6 toques · 4 trocas | atalho 1 · Aplicar 1 = **2 toques · 0 trocas** |

Menos toques não tira pendência de vista: o veredito fica no topo e a Situação é a 2ª coluna.

---

## 9. Testes

### 9.1 `capacidade_unit.py` (novo, sem navegador; PR 1)
Roda o bloco CAPACIDADE no node e o espelho `dados2.capacidade` em Python. Todo oráculo abaixo foi executado nesta revisão (v2calc), com o motor real.

| # | Caso | Esperado |
|---|---|---|
| C1 | S2627 Colhedoras fev/27 | 122,00 h ÷ 150,48 h (1 × 19 × 9 × 0,88) = 81,07 %; precisa de 1 |
| C2 | S2627 Tratores fev/27 | (122,00 + 67,31 da Safrinha) ÷ 699,20 = 27,08 %; precisa de 2; maior uso da linha em fev/27, não em set/26 |
| C3 | S2627 maiores usos | Pulverizadores dez/26 25,97 % (49,07 ÷ 189,00); Plantadeiras out/26 31,67 % (62,70 ÷ 198,00); Distribuidores nov/26 15,51 % (33,89 ÷ 218,50); Operadores mai/27 42,17 % ((651,43 + 4,40) ÷ 1.555,20), precisa de 6 (equipe do café); Operadores out/26 precisa de 2 |
| C4 | Horas de Operadores desta safra | coluna do §7, nas 4 safras |
| C5 | LG2627 | Operadores nov/26 1.584,40 % (23.613,86 ÷ 1.490,40), precisa de 127; out/26 1.305,79 % (18.615,30 ÷ 1.425,60), precisa de 105; mai/27 173,95 %, precisa de 14; ago/27 66,49 % e precisa de 10 (equipe simultânea). Falta em 9 meses: out/26, nov/26, dez/26, jan/27, fev/27, abr/27, mai/27, jul/27, ago/27. Tratores out/26 233,51 % (1.890,49 ÷ 809,60), precisa de 10; falta de out/26 a jan/27 |
| C6 | S2627 com Colhedoras = 0 | fev/27: 122,00 h, capacidade 0, "não calculável", precisa de 1 (falta); 3 pendentes; Tratores e Operadores de fev/27 iguais à base. O −1 só como guarda, em teste de unidade com horas de uma unidade = 0 |
| C7 | S27SF | maior uso Colhedoras jul/27 55,86 % (110,60 ÷ 198,00); Colhedoras fev/27 é só da S2627 e não conta |
| C8 | S2526 | 21 ocorrências fora do calendário; nenhuma demanda; não soma outras safras |
| C9 | S2627 com SOJA-AT nos cultivos de soja sem plano | Colhedoras fev/27 182,00 ÷ 150,48 = 120,95 %; precisa de 2 |
| C10 | Prévia = depois de salvar, Tratores 4 → 5 | fev/27 27,08 % → 21,66 % (189,31 ÷ 874,00) |
| C11 | Paridade | JS = Python (número e texto de `fmtOcup`) em 200 combinações de unidades (incluindo 0, 1 e valores em volta de cada `rec`: oper 5–10, colh 1–2), jornada, turnos, disponibilidade e absenteísmo, com a demanda recalculada nos dois lados; também sorteia `cfg_override` em larg/vel/efic/pess/maq |
| C12 | Invariância da demanda | Colhedoras 1 → 0 e Operadores 8 → 5 mantêm as horas por recurso da base (366,92 / 116,67 / 62,70 / 40,22 / 122,00 / 1.241,95). Operadores 0: o Plantio passa todo ao prestador e Operadores cai para 1.116,55 |
| C13 | S2627, Operadores 8 → 5 | mai/27 67,47 % ((651,43 + 4,40) ÷ 972,00), precisa de 6 (falta); 1 pendente "C1 · Colheita · sem recurso na fazenda" |
| C14 | LG2627, Operadores 8 → 10 e 8 → 5 | 10: nov/26 1.267,52 % (23.613,86 ÷ 1.863,00), pendentes 56 → 0, falta em 7 meses. 5: pendentes 56 → 91 |
| C15 | Serialização, 300 ha, 2 colhedoras (5 e 4 ha/h, janela 40 h) | colh 1: 40,00 h e 120,00 ha sem conjunto; colh 2: 66,67 h e saldo 0 |
| C16 | S2627, Operadores 0 | 30 pendentes; toda célula de Operadores com demanda desta safra fica "não calculável" e em falta; nenhum "—" nesses meses |
| C17 | S2627, Tratores = 1 | fev/27 108,30 % ((122,00 + 67,31) ÷ 174,80), precisa de 2, tem 1; sozinha daria 69,79 %; R2 "somando a Safrinha 2027 (67,3 h)" |
| C18 | S27SF encerrada | S2627 Tratores fev/27 17,45 %; Operadores fev/27 19,82 % |
| C19 | Negativo de escopo | S2627 Operadores nov/26 4,95 %: LG2627 e S2526 não entram |
| C20 | `fmtOcup` | Pulverizadores jan/27 0,931 % → "<1 %"; Distribuidores out/26 1,010 % → "1 %"; Tratores jan/27 0,228 % → "<1 %"; sem demanda → "—"; capacidade 0 → "não calculável" |
| C21 | `cargaRec` | nas 4 safras, em cada recurso e mês, \|Σ `cargaRec` das ocorrências desta safra − demanda desta safra\| < 1e-9. Negativo: Plantadeiras out/26 Σ horas-conjunto = 125,40, não 62,70 |
| C22 | `cfg_override` | `{('Adubação a lanço','Adubação de cobertura','r3'):{'larg':12}}` → 595,73 horas-conjunto · R$ 272.513,18 · 1.275,84 horas-homem · Adubação a lanço 74,11 h · Distribuidores nov/26 31,02 %. `{('Plantio','Plantio e adubação de base','r2'):{'pess':3}}` → Operadores 1.304,65 h · out/26 16,41 % · R$ 266.999,64. Negativo: sobrescrever só `pess` sem derivar `rec.oper` dá 1.241,95 e falha. `'*'` não muda atividade dividida nem atividade fora de uso |
| C23 | `resumo_cultura` | Σ cop por cultura = `plano_op.cop`; Σ insumos = Σ `plano × preço`; S2627 = tabela do §4.3; LG2627 Mamão `rha = None` (56 pendentes) |
| C24 | Partição do calendário | coluna "Ocorrências" do §7 nas 4 safras |

### 9.2 `saf_operacoes_test.py` (novo, navegador; cresce do PR 2a ao PR 5)
Número comparado com o espelho Python ou com o oráculo do §9.1, não com texto solto.

**Endereços e faixa**

| # | Caso | Esperado |
|---|---|---|
| N1 | `#saf=S27SF&etapa=6` | etapa 4 "Confira a demanda de insumos" |
| N2 | `etapa=3`, `4`, `5` | etapa 3 nos três |
| N3 | `passo=operacoes`, `passo=demanda`, só `saf=` | 3, 4, 4 (no PR 2a, `passo=demanda` abre a 6) |
| N4a | etapa 2 aberta; `location.hash='#saf=S2627&etapa=6'`, depois `etapa=4` | 4 e 3 (`hashchange`) |
| N4b | registro com `origem.h` terminado em `&etapa=6` | "Ver origem" da Compra com `passo=demanda` e sem `etapa=` |
| N5 | faixa a 390 px | "Etapa 3 de 4 · Dimensione operações e recursos"; 4 etapas; só informa |
| N6 | retomada | textos do §5.4; aviso do "Continuar" na S27SF: "Safra aberta: Safrinha 2027 · Demanda de insumos" |
| N7 | guardas estáticos | §5.3 = 0 |

**Operações (PR 3)**

| # | Caso | Esperado |
|---|---|---|
| O1 | `g_op` S2627 | 8 colunas na ordem do §3.4; linhas do §2.1; sem Gatilho, Talhão, Mês, Decorrido, Diesel ou Custo de insumos |
| O2 | Pulverização | valores do §2.1; atividades com Conjunto vazio; Dessecação pré-plantio "610 ha" e "R$ 14,49/ha". Negativo: nenhuma linha de operação com "ha" puro |
| O3 | Plantio, T2 (âncora do fluxo REND 2) | "2 conjuntos"; configurações 208,41 ha e 89,59 ha, R$ 58,20/ha e R$ 109,40/ha; 61,3 h; prestador sem recurso. Situação sem número; "Neste talhão" com decorrido 30,6 h e o trio |
| O4 | Situação sem janela | S2627: 8 operações "Janela não informada" em cinza; nenhum verde na coluna; sem chips do filtro rápido. Negativo: nenhum "Atende" nem "Cabe na janela" |
| O5 | Janela 60 h na atividade Colheita (Colheita de grãos), "Só esta" | só ela "Cabe na janela" (verde); T1-A 32,00 h, T1-B 30,40 h, T2 59,60 h; veredito com "16 de 17"; o filtro rápido passa a mostrar 2 categorias |
| O6 | Janela 50 h | T2 com "48 ha sem conjunto"; operação "Com pendência"; veredito R3 do §3.1; Colhedoras fev/27 continua com o valor de C1. Negativo: T2 nunca "Cabe na janela" |
| O7 | S27SF | janela 60 h nas 7 atividades: veredito verde sem a frase do prazo. Janela 40 h só na Colheita: T2 "98 ha sem conjunto", R3, 248,92 horas-conjunto |
| O8 | Operação Pulverização | "Aplicar em" visível = "Todas as atividades da operação"; sem Janela editável; `jan_op` "nenhuma das 6 com janela" |
| O9 | "Todas" nas atividades em uso | velocidade 12, Salvar: aviso "(6 atividades)"; as 6 com 32,40 ha/h e Origem "Ajustado nesta safra"; totais 522,95 h e R$ 252.444,85. Negativo: Controle de mosca-branca e as outras 7 fora de uso seguem 21,60 ha/h e "Padrão do cadastro (CD-02)". Adubação a lanço muda 4 (Calagem e Gessagem não); Fertirrigação 2 de 9 |
| O10 | Plano novo traz atividade escondida | depois de trocar o plano do T7 para MAMAO-PROD na etapa 2, a Pulverização mostra "varia" e as atividades novas vêm com 21,60 ha/h |
| O11 | Janela digitada em "Só esta" e troca para "Todas" | erro no "Aplicar em"; nada gravado. Configuração do Plantio e "+ Outra configuração" mostram Janela; REND 6b e B2 verdes |
| O12 | Escopo "Só esta" | Adubação de cobertura 24 → 12 m: a linha mostra 9,00 ha/h e R$ 25,89/ha; as demais atividades da operação ficam com 18,00 ha/h; a operação mostra "varia"; números de C22 |
| O13 | Origem | Plantio S2627: própria "Padrão do cadastro (CD-02)", prestador "Ajustado nesta safra"; dividida com velocidade 7 → 9: "Ajustado". Negativos: salvar sem mudar mantém 42 de 43 padrão na S2627 e 42 de 42 nas outras safras (executado, v2calc `mn04.js`). Ao vivo: 12 mostra "Ajustado", voltar a 8 mostra "Padrão" |
| O14 | Pessoas inteiras | "2,5" → "Use um número inteiro de pessoas."; o digitado fica |
| O15 | R$/kg | Colheita de grãos S2627: Soja R$ 0,0606/kg; S27SF "Milho 0,0216 · Feijão 0,0764"; café sem cultivo na S27SF: "não calculável" |
| O16 | Edição só na safra aberta | mudar o Plantio na S2627 não muda a S27SF |
| O17 | Paridade CD-02 (PRD 52.1) | Pulverização S2627: os rótulos de `REND_CAMPOS` (cadastros.py:416-427) visíveis no modo Largura × velocidade são subsequência ordenada do formulário; 3 ajudas AJ idênticas; `rend_c` 21,60 e `custo_c` 313,00 |
| O18 | Negativo | "R$ 1.427,61" e "/ha da safra" não aparecem em nenhuma etapa |
| O19 | Calendário (MN-03) | LG2627: chip "antes do início da safra" nas 75, nenhum "fora do calendário"; Data do Plantio de mudas "mar/26 – nov/26". S2526: "fora do calendário · 21"; Pulverização "set/25 – dez/25". S2627 e S27SF sem chip |

**Capacidade, veredito e layout (PR 4)**

| # | Caso | Esperado |
|---|---|---|
| V1 | S2627 topo | veredito R4 do §3.1 (âmbar); atalho "Maior uso: Colhedoras 81 % · fev/27"; custo com "máquinas e pessoas, sem insumos" |
| V2 | Um fato, um lugar (S2627, 1440 e 390, grade recolhida) | texto do bloco + área de ações: "475 ha", "690", "T4, T3, P1 e P2" e "81 %" uma vez cada; nenhum "Área com plano", "Maior uso no mês" ou "Nenhuma"; a área de ações tem só "Aplicar plano em 4 cultivos". Negativo: veredito âmbar nunca ao lado de "Nenhuma" |
| V3 | `g_cap` aberta, S2627 | 6 linhas e 15 colunas com os valores do §2.1; células cinza sem toque; sem negrito; a 1280 × 800, `.g2rola` sem rolagem lateral (simulação: 956 = 956 px) |
| V4 | Atalho/célula Colhedoras · fev/27 | linha "122,0 h de 150,5 h (81 %) · precisa de 1, tem 1"; cabeçalho "Horas de Colhedoras"; T1-A 32,0, T1-B 30,4, T2 59,6; Total 122,0 h; "Ver todas" volta a "Horas-conjunto" e 561,8 h |
| V5 | Plantadeiras · out/26 | "62,7 h de 198,0 h (32 %) · precisa de 1, tem 1"; só Plantio, com T1-A 16,45, T1-B 15,62 e T2 30,63 h; prestador "não usa". Negativo: "125,4" não aparece |
| V6 | Tratores · fev/27 | texto do §3.5; `g_op` só com Colheita de grãos; Total 122,0 h |
| V7 | Operadores | out/26: "171,2 h de 1.425,6 h (12 %) · precisa de 2, tem 8"; Tratamento de sementes 30,5 h; Total 171,2 h. mai/27: "655,8 h de 1.555,2 h (42 %) · desta safra 651,4 h · Safrinha 2027 4,4 h · precisa de 6, tem 8" |
| V8 | LG2627 | veredito R2 do §3.1; atalhos "Operadores e equipe 1.584 % · nov/26" e "Tratores 234 % · out/26"; grade aberta: nov/26 "precisa 127", mai/27 "precisa 14", Tratores out/26 "precisa 10"; Colheita de frutas com "sem recurso na fazenda · precisa de 10, tem 8"; qualificador do custo visível a 1440 e a 360. Negativo: nenhum "—" em mês com pendente sem recurso |
| V9 | LG2627, filtro "Com pendência" | só as operações com pendência; contador coerente |
| V10 | S2627, "Aplicar plano" com SOJA-AT | Colhedoras fev/27 em falta (C9); veredito R2 começa com "Falta recurso: Colhedoras precisam de 2 em fev/27 e você tem 1."; chip "Colhedoras 121 % · fev/27" na Colheita de grãos; continua na etapa 3. Não fixa quantos cultivos o lote aplica (PR-B, R-16) |
| V11 | S2526 | veredito R1; formulários de rendimento e de recurso só para consulta; subtítulo "Para ajustar, abra uma safra aberta."; `g_cap` toda "—"; sem atalho; primária "Ver demanda de insumos ›" |
| V12 | S27SF | veredito R5 do §3.1 (verde); atalho "Maior uso: Colhedoras 56 % · jul/27"; Colhedoras fev/27 em cinza |
| V13 | S2627, Colhedoras = 0 | veredito "Falta recurso: Colhedoras precisam de 1 em fev/27 e você tem 0. Inclui 3 ocorrências ainda sem alocação. Fora da conta: …"; fev/27 "precisa 1"; Maior uso "não calculável" |
| V14 | Toques na `g_cap`, 390 × 844 | "—" de Tratores: nada abre e `state.cap` não muda; toque a 4 px da borda de Colhedoras · fev/27 filtra; "Tratores" e "fev/27" (Mês) abrem o formulário; Enter abre; o Tab não para em "—". Proteção: na `g_cult` (sem `nr`), o toque na célula continua abrindo |
| L1 | Computador | S2627 1440 × 1040: 8 operações e Total; 1366 × 768 e 1280 × 800: as 8 operações; LG2627 1280 × 800: as 6 operações e Total. `main.scrollHeight ≤ clientHeight + 1` só como segunda asserção. Negativo: com a `g_cap` aberta por padrão, o teste fica vermelho |
| L2 | Celular, 390 × 844 e 360 × 800, S2627 e LG2627 | sem rolagem horizontal; sem rolar: veredito, atalhos e primária; ao abrir a `g_cap`, 6/6 linhas acima de `.acoes`, com Recurso, Maior uso e Mês inteiros |
| L3 | Teclado | Tab chega aos atalhos e às células com demanda (`aria-label` completo); Enter filtra e põe o foco na linha de filtro; Esc fecha formulário e Resumo, e o foco volta a quem abriu |
| L4 | — | sem erro de JS em S2627, S27SF, LG2627, S2526 e NOVA |

**Recurso, Resumo e aviso (PR 5)**

| # | Caso | Esperado |
|---|---|---|
| P1 | Tratores | "174,8 h"; "366,9 h"; digitar 5 → prévia "27 % → 22 % (fev/27)"; Salvar → fev/27 "22 %" (C10) |
| P2 | S2627, Operadores 8 → 5 | prévia "Maior uso: 42 % → 67 % (mai/27) · precisa de 6, tem 5 · Colheita de café · Derriçadeiras portáteis · equipe de 6 deixa de trabalhar em 1 ocorrência", em vermelho; depois de salvar, igual (C13), com veredito R2 "Operadores e equipe precisam de 6 em mai/27 e você tem 5" |
| P3 | LG2627, Operadores 8 → 10 | prévia "1.584 % → 1.268 % (nov/26) · precisa de 127, tem 10 · Colheita de frutas · Equipe de colheita (10 pessoas) + trator com carreta volta a trabalhar em 56 ocorrências" (C14) |
| P4 | Resumo S2627 | quadro do §4.3 com Total; nota com "Todos de hoje em diante"; trabalho da safra; Esc fecha e o foco volta ao link |
| P5 | Resumo LG2627 | Mamão "parcial · 56 ocorrências pendentes", nunca "R$ 4.072,16"; linha com a parcela antes do início; nota com Y e Z do §4.3 |
| P6 | Ajustes na Soja | um '-' num produto e um '+' noutro mudam JS e espelho igualmente |
| P7 | Aviso antes → depois | texto do §4.4, números de C22 |
| P8 | +1 pessoa na configuração própria do Plantio | Operadores sobe 62,70 h no formulário do recurso e nas horas-homem do Resumo (C22) |
| M1 | Medida | toques e digitação das tarefas A–E do §8, antes (`884620c`) e depois, no mesmo roteiro |

### 9.3 Testes existentes

| Teste | O que muda | O que **não pode mudar** |
|---|---|---|
| `rend_multiconjuntos_unit.py` | nada | 106/106 |
| `quantidade_test.py` | nada | 14/14; `dose*area` só em safra.js:330 e dados2 |
| `cal01_test.py` | nada | 43/45 com as 2 falhas antigas da LG2627 |
| `rend_multiconjuntos_test.py` fluxo 1–8 | `IR_ETAPA` 3/4/6 → 3/4 no PR 4; LEG lê os cabeçalhos novos; k4 vira comparação com `plano_op`; B2b, B2c, B2d e B5a leem "Neste talhão" e "Nesta configuração", com as mesmas strings (`trio_txt`/`cfg_txt`, :34-37) | T2 208,407 + 89,593 ha · 61,3 h · R$ 21.931 · 490 L; 30 % → 89,4 + 208,6 ha; 5c demanda antes = depois (:149); sequência; 30 % + 80 % recusado; remover e desfazer |
| idem, telas 9–11 | 9 vira etapa 3 a 390 e 360 px; 10b passa a "Σ horas do mês (`aria-label`) = campo do formulário = Σ `capSaf`" | 10 isolamento por safra; 11 S2526 consulta |
| idem, bordas B1–B7 | B1c lê veredito; B2e e B6a deixam de cruzar etapas; B3: Enter abre o formulário | B1a, B1b, B5, B6b |
| `tabelas_saf_test.py` | COLS = 8 do §3.4; filtros de Modo, Largura e Planos viram Situação e Conjunto; Situação ∈ valores de `s.sit` e só chips; unidade por nível (ha-op/ha); ordem numérica do Custo R$/ha (R$ 3,40/ha-op primeiro, R$ 662,86/ha-op por último); TF03 vai para a Adubação de cobertura da S2627 (C22); filtro Talhão = T2 vira busca "T2"; `passo=` | uma variável por coluna; unidade na célula; sem rolagem horizontal a 390 |
| `acao_unica_test.py` saf, responsivo e v3 | muda uma vez, no PR 4: n == 4; "Dimensionar operações ›" (2), "Conferir demanda de insumos ›" (3), "Enviar para cotação" / "Abrir Compra de insumos ›" (4); 7: Corrigir 4 → 2 → 4; 22: "sem percorrer a etapa 3"; 26 e 27 com o alvo 4; 29b com o alvo da etapa 3 nova | ≤ 1 primária; faixa só informa; avançar não envia; corrigir e voltar na mesma rolagem (±4 px) |
| `saf_cmp_continuidade_test.py`, `cmptest.py:45-46` | `passo=demanda` e textos sem número (PR 2a); `cur().startswith('4 ')` (PR 4) | 27: paridade com `dados2.demanda`; ida e volta; registro único |
| `etapas_celular_test.py` | `ATUAL 'SAF':(1,4)` (:106) e "Etapa 1 de 4 · Escolha a safra", no PR 4 | 390 px, zoom de 200 %, tela baixa |
| `partest.py` | navegação 4/6 → 3/4; k4 → Total e custo | dividir em parcelas não muda horas, custo nem demanda |
| `testes_pedido.py` | t01 `range(2,7)` → `range(2,5)`; t05 compara Total e custo | t05; t07 (seta só expande) |
| `saftest.py` | só a navegação | — |
| `saf38test.py`, `psfix38test.py` | continuam vermelhos pelo motivo antigo; regras recriadas em O14, O15 e P8 | — |
| `cadc_cd0102_b.py` | fora da bateria (00-bateria.sh:16) e **já vermelho** na base: falha na linha 27 (executado, v2calc). Fica como está; a regra do PRD 52.1 vira O17 | — |
| `cal01_test.py:93`, `cmptest.py:56`, `saf_cmp_continuidade_test.py:94-95` | têm o literal da demanda; são do CAL-01 e esta fatia não os altera | — |
| `verif_saf*.py`, `pltest.py`, `verif_cad*.py` | não mexer | — |

### 9.4 Bateria
`00-bateria.sh` completa a cada PR, contra a linha de base pós-cadeia (§0.1): os mesmos vermelhos antigos, `02-duplicadas` = 0, `varredura` completa e `03-acao_*` verdes. Falha nova bloqueia o PR. Corrigido um classificador, aproveitar os logs válidos (AGENTS §3.4).

---

## 10. Ordem de execução em PRs pequenos

Autor Claude; revisor e integrador Codex. Cada PR sai verde em `capacidade_unit` (a partir do 1), 106/106, 14/14 e na bateria sem vermelho novo.

1. **PR 1 · Capacidade pura.** Bloco CAPACIDADE; `origemCfg`; espelhos `dados2.capacidade` e `plano_op(…, planos, cfg_override)`, com `cfg_override` aplicado dentro de `cfgs_rend` pelas regras do `rendAfter`: rendimento por `rend_efetivo`; prestador sem implemento, pessoas e `rec`; `rec.oper = pess`. `capacidade_unit` C1–C22 e C24.
   - Sem efeito visível: o código antigo (safra.js:746-772) continua desenhando a etapa 5 até o PR 4.
   - Pode ser integrado antes da cadeia.
2. **PR 2a · Endereços por nome.** Leitura de `passo=`, com `passo=demanda` → 6 enquanto houver 6 etapas. Compra e Planejar safra geram `passo=demanda`; textos sem número; guardas N7. Testes N3 (parcial), N4b, N7, `cmptest`, `saf_cmp_continuidade`.
   - Não depende do registro. Abre como rascunho antes da cadeia e integra depois.
3. **PR 3 · Operações, ainda com 6 etapas (na etapa 4 de hoje).** `g_op` de 8 colunas, Situação, ha-op, `custoHa`, `abrirRend` (escopo e janela), `atvEmUso` no `rendAfter`, "Neste talhão", `classeOc` e a Data real.
   - `g_rend_*` continua na etapa 3; `g_mat`, a alternância e o k4 continuam na etapa 4.
   - Não altera a DEC-2609-03. Depende da cadeia.
   - Testes O1–O19 + REND fluxo e bordas + `tabelas_saf` + `partest` + t05/t07.
4. **PR 4 · Etapa única (com a renumeração 6 → 4).** `g_cap`, veredito, linha de capacidade, filtro, `abrirRec`, `nr` e `full` no G2; s3, s4 e s5 viram s3. Saem `g_res`, `g_resd`, k4 e k5.
   - `acao_unica`, `etapas_celular` e `IR_ETAPA` mudam uma única vez; os dois seletores "Por mês" nunca convivem.
   - Depende do registro da DEC-0510 reduzida.
   - Commits separados e reversíveis: (i) `g_rend_*` fora do corpo, só com P2 = "Sim"; (ii) `g_mat` e alternância fora, só com resposta de P1. Resposta diferente do padrão vira caso rastreável e desenho próprio antes do merge.
   - Testes N1–N6, V1–V14, L1–L4.
5. **PR 5 · Recurso, Resumo e aviso.** Prévia com recálculo, campos ao vivo do recurso, `resumoCultura` + `dados2.resumo_cultura` (C23), Custo R$/ha, R$/kg e Origem no formulário Rendimento, aviso antes → depois. Testes P1–P8, M1.
6. **PR 6 · Endereço gravado.** `history.replaceState` com `passo=`. Caso novo: recarregar volta à mesma etapa.

**CONTROLE-01** (realizado das O.S. na demanda e na projeção) não entra no meio dos PRs 2 a 5, porque mexe nos mesmos arquivos. Por padrão entra depois do PR 5. Se o Codex classificar o item 10 de `pce/verificada.md:202` como S2, entra antes da homologação e os testes do PR 5 rodam de novo sobre a nova base.

**Homologação** (depois do PR 5 ou 6, com o parecer dos dois agentes). O proprietário recebe link, versão, a tarefa curta E do §8, as limitações (FORA-DE-ESCOPO.md, com "a capacidade não desconta o realizado") e, se ainda não respondeu, a pergunta de P2, com a captura antes (`saf3-1440.png`) e a depois.

---

## 11. Matriz de aceite

| # | Critério | Verificação | PR |
|---|---|---|---|
| 1 | A faixa tem 4 etapas, e a 3 se chama "Dimensione operações e recursos". Não existe "Definir rendimentos", "Conferir plano operacional" nem "Dimensionar recursos" em nenhum estado | N5, `acao_unica` | 4 |
| 2 | Endereços antigos: `etapa=3/4/5` → 3; `etapa=6` → 4; `passo=` por nome; a origem da Compra gera `passo=demanda`. **Negativo:** `etapa=4` nunca abre a demanda | N1–N4b, N7 | 2a, 4 |
| 3 | Uma primária e um retorno; nenhum comando com segunda instância; `acoes_duplicadas` = 0 | `acao_unica`, V2, bateria | 4 |
| 4 | O veredito é o texto do §3.1 nas 4 safras e é o único lugar de "cabe", do que falta e do que ficou fora. **Negativos:** nenhum "cabe" sem "Na estimativa mensal"; com algo fora, nunca R5; veredito âmbar nunca ao lado de "Nenhuma" | V1, V2, V8, V11, V12, V13, O6, O7 | 4 |
| 5 | Falta de recurso nunca fica escondida: a demanda inclui o necessário sem alocação; nunca "—" em mês com pendente sem recurso; capacidade 0 mostra "não calculável" e "precisa N" | C5, C6, C12, C16, V8, V13 | 1, 4 |
| 6 | A capacidade soma as safras abertas da mesma fazenda e diz quanto vem de cada uma; outra fazenda e safra encerrada não entram | C2, C7, C17–C19, V6, V12 | 1, 4 |
| 7 | `g_cap`: recolhida por padrão; Recurso, Maior uso, Mês e meses; "<1 %" abaixo de 1 %; sem rolagem lateral a 1280 | V3, C20, L1 | 4 |
| 8 | `g_op` tem as 8 colunas do §3.4; ha-op na operação e ha nos demais níveis | O1, O2, `tabelas_saf` | 3 |
| 9 | Situação honesta: sem janela, nunca verde; "Cabe na janela" só com janela atendida; Situação só com chips e sem números do trio | O3–O7 | 3 |
| 10 | Os totais do §7, todas as colunas e as 4 safras, saem idênticos ao espelho; nenhuma célula "—" | C4, C23, C24 | 1, 5 |
| 11 | Tocar um atalho ou célula filtra as ocorrências daquele mês e recurso; a coluna "Horas de <recurso>" e o Total fecham com a linha de filtro, que diz "precisa de N, tem M" | V4–V7, C21 | 4 |
| 12 | "Todas" alcança só as atividades em uso e não copia janela; a janela só se edita onde vale; a Origem diz a verdade | O8–O13 | 3, 5 |
| 13 | O formulário Rendimento mantém campos, limites e validações; ganha Custo R$/ha, R$/kg e Origem; "2,5" pessoas é recusado; paridade com o CD-02 | O14, O15, O17, REND | 3, 5 |
| 14 | A prévia do recurso é igual ao resultado depois de salvar e diz quem deixa ou volta a trabalhar | C10, C13, C14, P1–P3 | 5 |
| 15 | Depois de salvar, o aviso traz antes → depois, igual ao espelho | P7, P8, C22 | 5 |
| 16 | "Aplicar plano" funciona dentro da etapa 3 e o veredito reage | V10 | 4 |
| 17 | S2526: tudo em consulta, inclusive recursos; o veredito diz que a capacidade não foi calculada | V11 | 4 |
| 18 | Pendente nunca mostra 0 h nem R$ 0; R$/ha da cultura com pendente é "parcial" | O3, P5, B1b | 3, 5 |
| 19 | **Negativo:** "R$ 1.427,61" e "/ha da safra" não aparecem | O18 | 3 |
| 20 | Layout: a página não rola; as operações aparecem nas telas do L1; no celular, sem rolagem lateral e com o essencial sem rolar | L1, L2 | 4 |
| 21 | Teclado e foco: atalhos e células alcançáveis com `aria-label`; "—" inerte; fechar devolve o foco | L3, V14 | 4 |
| 22 | Bateria sem vermelho novo contra a linha de base pós-cadeia; `capacidade_unit`, 106/106 e 14/14 verdes | §9.4 | todos |
| 23 | M1 registrada antes e depois; as tarefas A–E não pioram em toques nem em campos | M1 | 5 |

---

## 12. Fora de escopo
Em [FORA-DE-ESCOPO.md](FORA-DE-ESCOPO.md), cada item com a condição de retorno.

## 13. Decisões
Em [DECISOES.md](DECISOES.md): o que assumi, o que cortei, os parâmetros do dono com padrão, o que está pendente e a revisão aplicada, achado por achado.

## 14. Referências do setor
Pesquisa feita no mapa "referências" em 05/10/2026, só em fontes oficiais. Estar no mercado não prova que a regra está correta (AGENTS §3.3).

| Referência (fonte oficial, data) | Prática | Decisão | Onde entrou |
|---|---|---|---|
| Aegro, "Como realizar o custo orçado" (05/08/2026) | custo orçado nasce do planejamento; máquinas lançadas à mão | **adaptar** | custo de operação calculado (horas × R$/h) |
| Aegro, "Como planejar atividades no Aegro" (21/09/2026) | horas de máquina digitadas; vistas por status | **descartar** | horas = área ÷ rendimento (PRD 44.3); status é da O.S. |
| John Deere Operations Center, página Brasil (acesso em 05/10/2026) | tempo estimado de conclusão por campo | **adaptar** | Situação "Cabe na janela"; progresso real **adiado** |
| Cropwise Operations / Syngenta, newsroom Agritechnica (nov/2025); cropwise.com/operations | lacunas de equipamento; plano diário; Machine Pool | **adaptar sem IA** / **adiar** | "precisa de N, tem M"; o diário é da O.S./PCP |
| Farmbox, "Garanta uma semeadura de sucesso…" (21/07/2023) | rendimento contra a janela de plantio | **adotar** a pergunta | Situação e veredito; janela em datas **adiada** |
| TOTVS Agro Multicultivo, ficha técnica (19/12/2025) e página (03/06/2026) | custo a partir do plano, por hectare | **adotar** | Resumo por cultura com a base declarada |

As 5 referências entram num arquivo do módulo por PR (R-004 §3.1); hoje não existem no repositório.
