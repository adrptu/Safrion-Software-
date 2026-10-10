# Visões das listagens · descoberta, lente INVENTÁRIO

- **Pedido:** seletor de visões por ícone (ViewSwitcher), proprietário, 10/10/2026. Regra: "a visão nasce do atributo dominante".
- **Base lida (somente leitura):** `/home/user/sp-proto` = `claude/prototipo-v44` @ `0139898`. Também lidos, sem editar: `sp-ds` (`claude/v44-ds` @ `943433c`), `sp-tabr` (`claude/v44-tabelas-r` @ `8f19e0d`), `sp-nav` (`claude/v44-nav` @ `a7023ca`) e `apps/web`.
- **O que foi executado:** leitura de código e um levantamento por AST de `areas/*.py`, que acha cada `grid()/table()`, cada tela `shell37/_shell` e cada `tabs/seg/abas`.
  - Script: `scratchpad/visoes/inv_grids.py`. Saída: `inv_grids.json`. Apêndice: `apendice.py` → `apendice.md`.
  - Resultado: 106 funções, 260 grades, 133 chamadas de tela e 16 seletores.
  - **Não executado:** build, testes e navegador. Nenhum arquivo do protótipo foi alterado.
- **Linha das grades:** "arquivo:linha" aponta a chamada `grid(` (AST). O `gid=` pode estar 1–8 linhas abaixo.

---

## 1. Mecanismos de "visão" que já existem: seis implementações diferentes, todas só com texto

| # | Mecanismo | Onde está definido | Onde é usado | Observação |
|---|---|---|---|---|
| 1 | `ui37.tabs()` (grupo `role=group` com botões `aria-pressed`) | ui37.py:476-488 | O.S. `Lista · Kanban · Recursos` (processo_os.py:1232); CA-01 `Lista · Kanban · Mapa` (campo.py:198, oculto); SU-05 `Por carga · Por item · Por depósito · Por mês` (suprimentos.py:590, oculto) | É o mais próximo do ViewSwitcher. Sem ícone, sem setas, sem URL e sem preferência. |
| 2 | `cadastros.seg()` (`.cadx-seg`) | areas/cadastros.py:166-169 | CD-01 `Lista · Mapa` (cad_fazendas.py:259 e :263) e `Santa Rita · Lagoa Grande` (:263) | O 2º seletor é **recorte** (fazenda), não visão. |
| 3 | `.pr-vis` da Produção | areas/producao.py:36-38 | BEN `Lista · Kanban` (processo_beneficiamento.py:23-24); COLH `Por talhão · Por semana` (producao.py:502-503) | Abaixo de 480 px a lista vira cartões (producao.py:8-9). Cartões são forma de desenhar a Lista, não uma visão. |
| 4 | `engine.seg()` (aria-label fixo "Visão") | engine.py:176-178 | VE-01 `Semana · Dia` (comercial.py:170); VE-02 `Físico · Futuros · Câmbio` (:213); PL-04 `Hoje · 7 · 14 dias` (planejamento.py:429) | Todos ocultos. Na PL-04 é horizonte (filtro), não visão. |
| 5 | Agrupar (Tabela agrupada) | AG-01 `<select>` Nenhum/Talhão/Alvo/Situação/Fazenda (agronomia.py:827-829); O.S. botão "Agrupar por talhão" (processo_os.py:559, :767-769) | AG-01, O.S. | Na O.S. o grupo conta O.S. distintas e soma a área. No AG-01 não há subtotal. |
| 6 | Abas por entidade (`role=tab`) | cadastros.py:128 `abas()` | CD-01 Talhões/Fazendas/Ambiental/Água (:288); CD-02/03/04/05/06 | **Não é visão** (troca de entidade). O ViewSwitcher não deve absorver. |

O que nenhum deles tem hoje:
- **Ícone:** o protótipo usa `engine.icon()` com caminhos SVG próprios (engine.py:12-29, 60-63), não Lucide. `apps/web/package.json` não tem `lucide-react`.
- **Navegação com setas.**
- **Atalhos 1…9:** a busca por `key==='1'`, `Digit1`, `accesskey` e `aria-keyshortcuts` não achou nada. Pela regra do pedido ("1…9 se o projeto já tiver atalhos"), não implementar.
- **Visão na URL.**
- **Preferência por usuário e entidade.**

Estado e endereço que já existem:
- **Filtros na sessão:** `g2keep` (g2lib.js:16-19) guarda filtro, busca e ordenação no `sessionStorage` por tela e grade. **Só a `g_os` usa** (processo_os.py:535).
- **Endereço por hash, não por query:**
  - `OS.dc.html#OS-0420`, `#OS-0430:ajustar`, `#tal=Santa Rita|T1` (processo_os.py:751-753);
  - `IR-03det #OS-xxxx[:acao]` (irrigacao.py:4);
  - `CD-01det #talhao=ID` (cad_fazendas.py:10);
  - `AG-01 #VIS-xxx`;
  - `PA #plano=<id>` (NAV1, sp-nav docs/navegacao/ESPECIFICACAO.md §1).
  - `?view=` precisará conviver com o hash no protótipo.
- **Contexto do Mapa:** guardado em `sessionStorage 'mapa-ctx'` (inicio.py:976).
- **Software real:** já usa query para o estado da tabela, `estadoDaUrl`/`urlDoEstado` (apps/web/src/tabela/logica.ts:235, :284). A tabela soma no grupo só com a mesma unidade, `somavel` (logica.ts:16-17, :172-177). Hoje há duas listagens: `/estoque` (lotes) e `/cadastros/produtos` (apps/web/src/estoque/lista.ts:13-21, :46-50).

Dica (tooltip): a frente DS (sp-ds, não integrada) cria o componente único `g2dica`, que abre no hover (300 ms) e no foco de teclado, fecha com Esc e usa `aria-describedby` (sp-ds g2lib.js:526-545). Em botão só com ícone, a dica mostra o `aria-label`. Esse é o comportamento pedido para o ViewSwitcher: reaproveitar, não criar outro.

---

## 2. Inventário por entidade: listagens, visões atuais, atributos com fonte e veredito

Legenda: ✔ o dado sustenta · ⚠ sustenta só depois de um ajuste no dado · ✘ o dado não sustenta · **(existe)** já existe na tela.

### 2.1 Talhão
- **Listagens:**
  - CD-01 (Cadastros › Fazendas, áreas e talhões): `g_tal` cad_fazendas.py:256, árvore fazenda › talhão, subtotal por fazenda, seletor `Lista · Mapa` (:259/:263); `g_faz` :252 (em cartões).
  - CD-01det: `g_parc` :507, árvore safra › parcela, abas Parcelas por safra · Geometria (:531).
  - Mapa IN-04 (inicio.py:1300; camadas inicio.py:99-101): o talhão é a unidade do mapa.
- **Atributos:**
  - **Geometria:**
    - Santa Rita é desenho esquemático em pixels, com **duas fontes divergentes**: `GEO` inicio.py:93-96 (Mapa) e `GEO_MAPA` cad_fazendas.py:206 (CD-01). As coordenadas são diferentes.
    - Polígono validado só do T1: dados.py:126 `GEO_TAL` e dados_cad.py:25 `GEO_VERS`. Parcelas: dados.py:127 `GEO_PARC`.
    - Centros lat/lon sintéticos da Santa Rita: dados_mip.py:99-100 `_SR_LL`.
    - Lagoa Grande: círculo do KML (centro e raio). Fontes: `LG_PIVOS` (dados_cad.py:192 → dados_lagoa_fonte; sintético em dados_lagoa_sintetico/kml.py:31) e `lagoa_pivos.geojson` (inicio.py:431).
    - Desenhado ou importado: `localStorage 'talhao-os-cd01-v1'` (talmapa.js:3-4).
  - **Pai/filho:**
    - fazenda › talhão: dados_cad.py:13-19; árvore montada em cad_fazendas.py:250.
    - talhão › parcela por safra: dados2.py:65-86, `local` 'T1-A'.
    - **"Setor" não é nível da hierarquia.** É a bomba ou o sistema de irrigação do talhão irrigado: dados_cad.py:21-22 `SISTEMA`/`SETORES`.
  - **Categoria + valor:** sistema (Sequeiro/Pivô/Gotejo) + área cultivável (cad_fazendas.py:56-66).
  - **Status:** só Ativo/Inativo, sem fluxo. **Datas do próprio talhão:** nenhuma. **Foto:** nenhuma.
- **Veredito:** Lista **(existe)** ✔ · Mapa **(existe)** ✔ · Árvore **(existe)** ✔, mas **fazenda › talhão › parcela**, não "fazenda › setor › talhão" · Tabela agrupada ✔ opcional (sistema, soma em ha).
  - A Timeline é do cultivo (2.2), não do talhão.
  - **Pré-requisito do Mapa como visão comum:** unificar a geometria da Santa Rita.

### 2.2 Safra (e cultivo)
- **Listagens:**
  - SAF etapa 1 (Agrícola › Planejar safra): `g_saf` processo_safra.py:27.
  - Cultivos por safra: `g_cult_{k}` :83, em árvore, com as colunas Livre a partir de / Ocupa até / Fim por (:63-66).
  - CMP etapa 1: `g_saf` processo_compras.py:73.
  - PL-01 `g_saf` planejamento.py:151 (oculto).
- **Atributos:**
  - Início e fim da safra (ISO): dados2.py:14-19; Lagoa Grande dados_lagoa_safra.py:11.
  - Estado: Rascunho, Em planejamento, Encerrada (dados2.py:15-17; chip em safra.js:1190). São 3 estados sem transição de fluxo definida, em 4 safras.
  - Cultivo: plantio (dados2.py:65-86), colheita prevista ou "ocupa até" (serviço ocupacao.js / ocupacao_cen), área e talhão.
- **Veredito:** Lista **(existe)** ✔ · Timeline ✔.
  - A Timeline que decide alguma coisa é a dos **cultivos por talhão no tempo** (ocupação, SAF-C01/C02). A de 4 safras quase não informa.
  - Kanban ✘: não há fluxo e o volume é pequeno.

### 2.3 O.S.
- **Listagens:**
  - O.S. (Agrícola › Ordem de Serviço): `g_os` processo_os.py:1220 (18 colunas).
    - Seletor `Lista · Kanban · Recursos` (:1232). Agrupar por talhão (:767-769).
    - Filtros: Talhão (`_talsel` :961), Fase (`_chips` :979), Fazenda e Safra no topo. `g2keep` (:535).
  - CA-01 `g_os` campo.py:187 (oculto), com `Lista · Kanban · Mapa` esquemático (:138, :198).
  - Mapa IN-04: camada O.S./prazos com filtro Fase (inicio.py:107; `_ORD_MAPA` :119).
  - O Kanban `_kanban()` (processo_os.py:942) é reaproveitado pelo BEN.
- **Atributos:**
  - **Fase:** 5 fases fixas (processo_os.py:66 `FASES`; dados.py:88-112). Canceladas fica fora do quadro (processo_os.py:20-21).
  - **Datas:** início e fim ISO (dados.py:116-121 `_JAN`; colunas Início e Fim t='date', :1221).
  - **Responsável:** pessoa (dados.py ORDENS `resp`).
  - **Recursos por dia e hora:** alocacao.py:10-33 (`RECURSOS`, `ALOC`), **só a semana de 22 a 27/09**.
  - **Talhão:** dados.py:114 `_TAL` → geometria do talhão.
  - **Área, realizado e saldo:** valores numéricos.
- **Veredito:**
  - Lista **(existe)**, Kanban **(existe)**, Carga por recurso **(existe: "Recursos", :1158)** e Tabela agrupada **(existe)** ✔.
  - Calendário ✔ (início e fim).
  - Mapa ✔: o dado existe e está no IN-04, falta na tela O.S.
  - Timeline: sustentada, mas sobrepõe a Carga por recurso. Não acrescentar.
  - **Filtro na visão Recursos:** aplica o filtro aos blocos, mas conflitos, manutenção e uso continuam da semana inteira, como diz a nota (processo_os.py:806). Isso fere em parte "mesmo estado de filtro". Manter a nota ou decidir.

### 2.4 Atividade / Aplicação / Apontamento
- **Não há listagem própria no menu.**
  - Planejada: SAF `g_op` processo_safra.py:180 (árvore operação › atividade › talhão, com Data, Conjunto e Horas). PL-02 `g_op`/`g_tal` planejamento.py:227/:291 (oculto).
  - Realizada: apontamentos da O.S. (cenario.py:58, `ap=[d,dia,ha,st]`; campo.py:221 `TURNOS`; `g_ap` campo.py:251/:326; CA-02 `g_fila` :396, oculto; app MB-03).
- **Atributos:**
  - Gatilho relativo DAP/DATA (dados2.py:24-61). A data só existe calculada contra o cultivo: `data_atividade` dados2.py:125 e `demanda_datada` :903.
  - Talhão ou parcela (CULTIVOS.local); dose e área.
  - Conjunto: dados2.py:89-103 `CONJ`. Horas de recurso por mês: `g_cap_{k}` processo_safra.py:194, matriz recurso × mês que **já existe**.
- **Veredito:**
  - Lista ✔. Calendário ✔ com a data calculada.
  - Matriz talhão × semana ✔: chaves talhão e semana ISO, valor ha ou número de aplicações. Plano vem de CULTIVOS × PLANOS e realizado de `ap`.
  - Mapa: só por talhão, que já é a camada Lavoura e O.S. do IN-04. Não duplicar.
  - **Decisão pendente:** em que tela a "Atividade" mora (SAF etapa 3 ou nova listagem).

### 2.5 Insumo / Estoque
- **Listagens:**
  - EST (Suprimentos › Estoque), 6 seções (processo_estoque.py): `g_rec` :81, `g_ent` :98, `g_dev` :106, `g_lot` :116 (árvore item › lote, chips Local), `g_cnt` :122, `g_mov` :130.
  - CD-06 `g_itm` cad_produtos_estrutura.py:87 (árvore grupo › item).
  - SU-03 `g_sal` suprimentos.py:388 (oculto).
  - Software real: `/estoque`.
- **Atributos:**
  - Grupo: dados2.py:821 `GRUPOS`; dados_cad.py:146 `GRUPO_NAT`.
  - Quantidades: dados2.py:861-869 `LOTES` (físico, quarentena, reservado), **em kg ou L**.
  - Local: dados_cad.py:167 `LOCAIS`. Validade: LOTES.validade 'MM/AAAA'.
  - Preço: dados2 PLANOS `preco`; dados_cad.py:159 `PRECO_DATA`.
  - Situação do lote (quarentena, bloqueado, apto) não é fluxo.
- **Veredito:** Lista **(existe, item › lote)** ✔ · Tabela agrupada ✔ por grupo ou local.
  - **Subtotal só dentro da mesma unidade, ou em R$.** É a regra que o software real já aplica (logica.ts:16-17).
  - Calendário de validade fraco: só 4 lotes têm validade.

### 2.6 Compras (solicitação, cotação, pedido)
- **Listagens:**
  - CMP (Suprimentos › Compra de insumos), em processo_compras.py: `g_saf` :73, `g_dem` :76 (árvore grupo › insumo, soma Valor), `g_conv` :82, `g_cmp` :90, `g_apr` :99, `g_ent` :103 (pedidos, Previsão t='date').
  - Ocultos: SU-01 `g_nec` :269, SU-04 `g_cot` :501, SU-05 `g_ped`/`g_car`/`g_itm`/`g_dep`/`g_mes` :554-586, com abas pivô (:590).
- **Atributos:**
  - Estado do pedido: Aguarda confirmação → Confirmado → Parcial → Entregue · conciliado (processo_compras.py:297-308; dados2.py:846-850).
  - Previsão de entrega: dados2.py:847 'previsao'.
  - Grupo e valor em R$; fornecedor (dados2.py:822).
- **Veredito:** Lista **(existe)** ✔ · Tabela agrupada **(existe em árvore com soma)** ✔ · Calendário de entregas ✔ opcional.
  - Kanban ⚠: o fluxo é curto (4 estados) e há poucos pedidos.

### 2.7 Máquina / ativo
- **Listagens:**
  - CD-03 `g_atv` cad_ativos_pessoas.py:136, abas Máquinas · Conjuntos (:156); Conjuntos em cartões.
  - MA-01 `g_at` maquinas.py:136 (Agenda, Próxima manutenção, Uso 30 d) e `g_ut` :155 (utilização por grupo).
  - MA-03 `g_vc`/`g_mi` :311-312. MA-05 `g_ab` :669 e `g_co` :686. GE-06 `g_atv` gestao.py:480 (oculto).
- **Atributos:**
  - Classe e custo/h: dados_cad.py:63-80. Condição Apto/Restrito/Bloqueado: maquinas.py:137; dados_cad.py:81.
  - **Local é só texto** ('Santa Rita · T4', 'Galpão 1'), sem coordenada, GPS ou telemetria.
  - Ocupação por dia e hora: alocacao.py:10-33. Janelas de OM: dados_manutencao.py:174-206. Vencimentos: dados_manutencao.py:212.
- **Veredito:** Lista **(existe)** ✔ · Carga por recurso ✔ (reaproveitar O.S. › Recursos) · Tabela agrupada por classe ✔ opcional (o `g_ut` já agrega).
  - **Mapa ✘**: não há coordenada.

### 2.8 Colaborador (CD-04)
- **Listagem:** `g_pes` cad_ativos_pessoas.py:301, abas Pessoas · Equipes (:314), filtro Função. Equipes em cartões.
- **Atributos:**
  - Equipe e custo/h: dados_cad.py:95, :100-117. Habilidades.
  - Validades NR/CREA: datas `v31`, `v10`, `vcrea`.
  - Alocação por dia: alocacao.py (MAR, CAR, PAU, JOA).
- **Veredito:** Lista **(existe)** ✔ · Tabela agrupada por equipe ✔ (contagem; **soma do custo/h não faz sentido**) · Carga por recurso ✔, no PCP e não no cadastro.
  - Calendário de vencimento de habilitação: fraco.

### 2.9 Vistoria / Ocorrência (MIP)
- **Listagens:**
  - AG-01 (Agrícola › Pragas e doenças): `g_vis` agronomia.py:831. Agrupar por Talhão/Alvo/Situação/Fazenda **(existe)** e chips de situação.
  - AG-01det: `g_pts` :899 (ponto, GPS, hora, fotos).
  - Camada MIP/MID do IN-04 (inicio.py:99, :108).
  - Ocorrências: CA-03 `g_oc` campo.py:467 (oculto); app MB-04.
- **Atributos:**
  - Estado: programada → coleta → concluída, e a decisão monitorar/controlar (dados_mip.py:178-213).
  - Data: VIS.data; programada no futuro, `prox` nas decisões.
  - Talhão: centro lat/lon dados_mip.py:99-104. GPS por ponto só na VIS-011 (:242-247).
  - **Foto:**
    - A vistoria só tem contagem ("N fotos", agronomia.py:865) e cartões com texto (:885, :912).
    - Na ocorrência, "Foto" é uma opção de select (campo.py:475).
    - No app a foto é **simulada** (mobile.py:599-624).
    - **Nenhum arquivo de imagem.**
- **Veredito:** Lista **(existe)** ✔ · Tabela agrupada **(existe)** ✔ · Mapa ✔ (a camada existe; falta na listagem) · Calendário ✔ (programação de vistorias).
  - **Galeria ✘** até haver imagem real.
  - Ocorrência: o local é texto livre ('T4 · OS-0420'). Mapa ⚠ só com talhão estruturado.

### 2.10 Lançamento de custo / Orçamento
- **Listagens:**
  - GE-03 `g_lan` gestao.py:291 (oculto). Componente + valor em R$: gestao.py:272-281.
  - Estrutura gerencial CD-07 `g_dim` cad_produtos_estrutura.py:259 (árvore).
  - Orçamento: GE-02 `g_ver`/`g_cx`/`g_cmp` gestao.py:179-220 (oculto); SAF `g_dem` Valor (R$) processo_safra.py:221.
- **Atributos:**
  - No lançamento, "Dimensões" é **texto livre** ('Feijão · P1 · OS-…'). Não há natureza ou centro codificado.
  - Hierarquia só na estrutura: dados_cad.py:177-190 `ESTR`, campo `superior`. Natureza 3.1 › 3.1.01…06. Centro de resultado e centro de responsabilidade não têm superior (são planos).
- **Veredito:** Lista ✔ · Tabela agrupada ✔ (componente, valor) · **Árvore de centro de custo ⚠** até o lançamento gravar a dimensão codificada.
  - No CD-07 a árvore **(existe)**.

### 2.11 Irrigação (IR-01 a IR-04)
- **Listagens** (irrigacao.py):
  - IR-01 `g_set` :151 (setor, déficit em mm, situação).
  - IR-02 `g_ag` :213 (árvore captação › ordem; agenda por captação).
  - IR-03 `g_os` :295 (ordens só de água, etapa).
  - IR-03det `g_pas` :337. IR-04 `g_src`/`g_cap`/`g_des` :538-555.
  - Camada Irrigação do IN-04 (inicio.py:99, :111).
- **Atributos:**
  - Setor = pivô ou talhão, com geometria.
  - Passadas com início e duração: dados_irrigacao.py:133-170. FERT início e fim: :173. **Paradas por bomba:** :177.
  - Etapas: as 5 da O.S. (irrigacao.py:299). Captação: dados_irrigacao.py:39.
- **Veredito:**
  - IR-01: Lista ✔, Mapa ✔ (está no IN-04).
  - IR-03: Lista ✔, Kanban ✔ (5 fases), Timeline / Carga por recurso ✔ (bomba × hora).
  - IR-02: Árvore **(existe)**.

### 2.12 Colheita, Produção e Comercial
- **Listagens** (producao.py):
  - COLH `g_tal` :493 (árvore cultura › talhão) e `g_sem` :497, com seletor `Por talhão · Por semana` **(existe)**.
  - CARGA `g_cg` :363. PROD `g_lot` :241 (árvore produto › lote) e `g_ped` :246.
  - Ocultos: CO-01…07 (colheita.py), VE-01…06 (comercial.py), LO-01…04 (logistica.py; `g_sl` doca × horário :186).
- **Atributos:**
  - Previsão por cultivo × semana ISO: dados_producao.py:111-115. Hoje só 2 pivôs × 1 semana; a soja tem só o total da safra.
  - Carga: data de colheita, data de recebimento e hora; origem talhão/O.S.; estado A pesar → Recebida (dados_producao.py:71-90).
  - Qualidade do lote: Em inspeção, Liberado, Bloqueado, Destinado (producao.js:193-204). É decisão, não fluxo.
  - Pedido: janela e semana (dados_producao.py:96-107).
- **Veredito:**
  - COLH: Lista **(existe)**. Matriz talhão × semana ⚠: o dado é ralo; o "Por semana" atual é por produto.
  - CARGA: Lista ✔. Calendário opcional.
  - PROD: Lista e Árvore **(existem)**. Kanban ✘.
  - LO-01 (oculto): Carga por recurso ✔ (doca × horário).

### 2.13 Beneficiamento (BEN)
- **Listagem:** `g_ob` processo_beneficiamento.py:18, `Lista · Kanban` **(existe)**, 5 fases (ben.js:21), cartões no estreito.
- **Veredito:** Lista e Kanban ✔ (existem). Migrar para o ViewSwitcher.

### 2.14 Manutenção (OM, planos)
- **Listagens:**
  - MA-04 `g_om` maquinas.py:544, com chips de fase.
  - PM `g_pv` :1121. Planos: dados_manutencao.py:89.
  - MA-03 `g_vc`/`g_mi`.
- **Atributos:**
  - 5 fases: dados_manutencao.py:268 `MAN_FASES`.
  - **Janela em texto** ('hoje 14:00', '28/09'), tempo em h, ativo e especialidade (dados_manutencao.py:174-206). Vencimento calculado: :212.
- **Veredito:** Lista ✔ · Kanban ✔ (as 5 fases da O.S.) · **Calendário ⚠** (a janela precisa virar data ISO) · Carga por recurso ✔ (ativo ou especialidade × dia) · Árvore plano › serviço opcional.

### 2.15 Requisições
- **Listagens:**
  - EST `g_ent` processo_estoque.py:98 e `g_dev` :106. Fontes: dados2.py:855-860 `REQUISICOES` e cenario.py:34-40.
  - Ocultos: CA-04 `g_req` campo.py:553, SU-07 `g_req` suprimentos.py:818.
- **Atributos:** o estado acompanha a fase da O.S.; não é fluxo próprio. Pai O.S. › item. Quantidade com unidade.
- **Veredito:** Lista ✔. Tabela agrupada por O.S. ✔. Mais nada.

---

## 3. Correções à sugestão de partida

| Entidade | Sugestão | Confirmado com o código | Corrigido |
|---|---|---|---|
| Talhão | Lista, Mapa, Árvore (fazenda › setor › talhão) | Lista e Mapa (existem no CD-01) e Árvore (existe fazenda › talhão) | Árvore = **fazenda › talhão › parcela por safra**. Setor é bomba de irrigação (dados_cad.py:21-22). Unificar antes a geometria da Santa Rita (inicio.py:93 × cad_fazendas.py:206). |
| Safra | Lista, Timeline | Sim | A Timeline útil é a da **ocupação dos cultivos por talhão**. A de 3–4 safras quase não informa. |
| O.S. | Lista, Kanban, Calendário, Carga por recurso, Mapa | Sim. Lista, Kanban e Recursos já existem; Mapa existe no IN-04 | Acrescentar a **Tabela agrupada, que já existe** (Agrupar por talhão). A Carga por recurso só tem dado da semana de 22 a 27/09. |
| Atividade/Aplicação | Lista, Calendário, Matriz (talhão × semana), Mapa | Calendário e Matriz, com data calculada (dados2.py:125, :903) | Mapa sai: já é o IN-04. A entidade não tem tela própria: decidir onde mora. |
| Insumo/Estoque | Lista, Tabela agrupada | Sim | Subtotal só na mesma unidade ou em R$. A Lista atual já é árvore item › lote. |
| Máquina | Lista, Carga por recurso, Mapa | Lista e Carga | **Mapa sai**: não há coordenada (dados_cad.py:63-80 `local` é texto). |
| Vistoria/Ocorrência | Lista, Mapa, Galeria | Lista, Mapa e Tabela agrupada (existe) | **Galeria sai**: não há imagem (foto simulada). Entra o **Calendário** (programação). O Mapa da ocorrência depende de talhão estruturado. |
| Lançamento de custo | Lista, Tabela agrupada, Árvore (centro de custo) | Lista e Tabela agrupada | **Árvore ⚠**: a dimensão do lançamento é texto (gestao.py:272-281). Só a estrutura do CD-07 é árvore. |
| *(fora da sugestão)* OM (MA-04) | — | Lista, Kanban de 5 fases e Carga por recurso | Calendário depois que a janela virar ISO. |
| *(fora)* Irrigação IR-03 | — | Lista, Kanban de 5 fases e Timeline por bomba | — |
| *(fora)* BEN | — | Lista e Kanban (existem) | Só migrar. |
| *(fora)* Compras (pedidos) | — | Lista, Tabela agrupada (existe) e Calendário de entregas | Kanban fraco. |
| *(fora)* Colaborador | — | Lista e Tabela agrupada por equipe (contagem) | Carga por recurso fica no PCP. |
| *(fora)* Requisições | — | Lista e Tabela agrupada por O.S. | — |

---

## 4. Contradições e riscos que a especificação precisa resolver

1. **Arrastar no Kanban da O.S., BEN, OM e irrigação:** não existe hoje. O código não tem `draggable` em areas/*.py.
   - A fase só muda por evento (rodapé da O.S., processo_os.py:1251). Liberar exige aprovação agronômica (AGENTS §4; CMD-42/CMD-06).
   - **Arrastar entre fases: ✘.**
   - Único arraste defensável: no Calendário, mudar a janela de ordem A liberar ou Liberadas, pela mesma validação do formulário. O CA-01 já permite editar a janela sem trocar produto nem área (campo.py:189-192). Precisa de desfazer.
2. **Kanban da O.S. sem coluna nova:** as 5 fases são fixas. Canceladas fica fora do quadro (processo_os.py:20-21). Pausa e impedimento são selos.
3. **Fonte única da geometria:** a Santa Rita tem duas geometrias (inicio.py:93 e cad_fazendas.py:206). Só a Lagoa Grande tem coordenadas reais (círculos).
4. **Filtro comum:** o Recursos da O.S. filtra os blocos, mas conflitos e uso continuam da semana inteira (processo_os.py:806). O IN-04 tem filtros por camada (inicio.py:103-112), não os da lista.
5. **Estado preservado:** só a `g_os` guarda filtro, busca e ordem (`g2keep`). As outras perdem tudo ao abrir o detalhe e voltar. A visão não é guardada em nenhuma.
6. **Mobile:** a Lista vira cartões (producao.py:8-9, BEN). O app (MB-*) usa `mcard` e fica fora do escopo do ViewSwitcher.
7. **Ícones Lucide:** nem o protótipo nem o software real usam Lucide. Adotar exige decisão de dependência (versões em docs/architecture/versions.md). No protótipo, desenhar os caminhos no `engine.ICONS`.
8. **Frentes não integradas no mesmo terreno:**
   - DS (sp-ds) mexe em processo_os.py: selos com dica (`osEncSelo`/`osSeloDica`) e g2lib.js (`g2dica`).
   - TABR (sp-tabr) mexe em cad_*.py e irrigacao.py.
   - NAV1 (sp-nav) reescreve processo_planos.py (PA lista → detalhe com hash).
   - Integrar essas frentes antes de mexer nas mesmas grades.

## 5. Sugestão de entidade para a fatia 1 (ViewSwitcher, estado, URL, preferência, Lista + Tabela agrupada)
- **Software real:** `/estoque` (lotes). Já tem Agrupar por produto ou estado, soma na mesma unidade e estado na query (apps/web/src/estoque/lista.ts:13-21; tabela/logica.ts:235, :284).
- **Protótipo:** EST › Confira saldos (`g_lot` processo_estoque.py:116), agrupado por grupo ou local com subtotal na mesma unidade. Alternativa: AG-01, que já tem o select Agrupar.
- **Fatia 2:** migrar o seletor de texto da O.S. (processo_os.py:1232) e do BEN (processo_beneficiamento.py:23) para o ViewSwitcher e acrescentar o Calendário.

---

## Apêndice A · Todas as grades com id (gerado por `apendice.py`, AST)

Tabela abaixo (cópia de `apendice.md`) no formato tela · menu/oculto · gid · arquivo:linha · forma · colunas.

- Telas no menu (ui37.py:36-44): IN-04, CD-01…07, AG-07, PA, SAF, OS, AG-01, IR-01 (e as irmãs IR-02…04), COLH, CARGA (e BEN), PROD, PM, MA-01…05, CMP, EST, CF-05.
- As demais são ocultas: AG-02…06, CA-*, CO-*, VE-*, LO-*, GE-*, PL-*, SU-*, PT-*, CF-01…04, ON, BO, IN-01…03 e o app MB-*.
- `cadastros.py:303-809` é substituído por `cad_*.py` (cadastros.py:289-295 `CAD_MODS`).

| Tela (fid) | Menu | Grade | Arquivo:linha | Forma | Colunas |
|---|---|---|---|---|---|
| AG-02/AG-03/AG-04/AG-05/AG-06 | oculto | `g_lau` | areas/agronomia.py:164 |  | Laudo · amostra; Local · área representada; Profund.; Data; Laboratório; Método · extrator; Validação; Próxima ação |
| AG-02/AG-03/AG-04/AG-05/AG-06 | oculto | `g_ext` | areas/agronomia.py:173 |  | Atributo; Valor; Unidade; LD |
| AG-02/AG-03/AG-04/AG-05/AG-06 | oculto | `g_dia` | areas/agronomia.py:206 |  | Diagnóstico; Talhão · cultura; Evidências; Hipótese · causa; Risco; Situação · decisão; Próximo passo |
| AG-02/AG-03/AG-04/AG-05/AG-06 | oculto | `g_ev` | areas/agronomia.py:251 |  | Evidência; Tipo; Data; O que mostra; Fonte |
| AG-02/AG-03/AG-04/AG-05/AG-06 | oculto | `g_rec` | areas/agronomia.py:291 |  | Recomendação; Origem; Operação · talhão; Produto · dose · janela; Situação; Próximo passo |
| AG-02/AG-03/AG-04/AG-05/AG-06 | oculto | `g_ver` | areas/agronomia.py:326 |  | Versão; O que muda; Alcance; Situação; Quando |
| AG-02/AG-03/AG-04/AG-05/AG-06 | oculto | `g_it` | areas/agronomia.py:332 |  | Produto; Unidade; Dose sugerida; Dose informada; Registro Agrofit |
| AG-02/AG-03/AG-04/AG-05/AG-06 | oculto | `g_zon` | areas/agronomia.py:341 |  | Zona; Área; K trocável; KCl 60 % (v2); Saldo na v3 |
| AG-02/AG-03/AG-04/AG-05/AG-06 | oculto | `g_exe` | areas/agronomia.py:348 |  | Registro; O que é; Situação |
| AG-02/AG-03/AG-04/AG-05/AG-06 | oculto | `g_cus` | areas/agronomia.py:358 |  | Recurso; Origem; Quantidade × preço; Custo; Situação |
| AG-02/AG-03/AG-04/AG-05/AG-06 | oculto | `g_bib` | areas/agronomia.py:412 |  | Item · tipo; Escopo (cultura · região · fase); Referência; Unidade · gatilhos; Validade · revisão; Aprovador técnico; Situação; Ação |
| AG-02/AG-03/AG-04/AG-05/AG-06 | oculto | `g_ef` | areas/agronomia.py:459 |  | Avaliação; Recomendação → execução; Método pré/pós; Datas; Resultado; Confiança; Custo; Ação |
| AG-02/AG-03/AG-04/AG-05/AG-06 | oculto | `g_eco` | areas/agronomia.py:465 |  | Economia; Valor; O que entra; Situação |
| AG-01 | Agrícola › Pragas e doenças | `g_vis` | areas/agronomia.py:831 | árvore | Vistoria; Talhão · cultura; Alvo; Contagem × NC; Data; Situação; Próximo passo |
| AG-01 | Agrícola › Pragas e doenças | `g_pts` | areas/agronomia.py:899 |  | Ponto; GPS; Hora; Contagem; × NC; Fotos; Qualidade |
| CF-05 | Configurações › Assinatura e cobrança | `g_uso` | areas/assinatura.py:221 |  | Fazenda; Talhão; Área cultivável (ha); Situação |
| CF-05 | Configurações › Assinatura e cobrança | `g_fat` | areas/assinatura.py:224 |  | Competência; Área cobrada (ha); Regra; Valor (R$); Vencimento; Estado |
| CF-05 | Configurações › Assinatura e cobrança | `g_pl` | areas/assinatura.py:228 |  | Plano; Módulos; Limite de área; Usuários; Franquias; Preço R$/ha·mês; Mínimo R$/mês; Valor para a sua área; Situação |
| CD-03 | Cadastros › Máquinas, instalações e setores | `g_atv` | areas/cad_ativos_pessoas.py:136 |  | Máquina ou instalação; Classe; Capacidade; Custo por hora; Conjuntos; Situação |
| CD-03 | Cadastros › Máquinas, instalações e setores | `g_cj` | areas/cad_ativos_pessoas.py:144 |  | Conjunto; Operações; Largura; Condição; Operadores alocáveis; Rendimento |
| CD-04 | Cadastros › Pessoas e equipes | `g_pes` | areas/cad_ativos_pessoas.py:301 |  | Pessoa · equipe; Habilidades; Vínculo; Custo-hora; Situação |
| CD-04 | Cadastros › Pessoas e equipes | `g_eq` | areas/cad_ativos_pessoas.py:307 |  | Equipe; Líder; Pessoas ativas; Calendário |
| CD-02 | Cadastros › Culturas, cultivares e operações | `g_cv` | areas/cad_culturas.py:64 | árvore | Cultura · cultivar; Ciclo; Item de semente; Cultivos; Situação |
| CD-02 | Cadastros › Culturas, cultivares e operações | `g_cult` | areas/cad_culturas.py:81 |  | Cultura |
| CD-02 | Cadastros › Culturas, cultivares e operações | `g_rend` | areas/cad_culturas.py:103 | árvore | Operação · conjunto; Cultura; Rendimento; Custo por hora; Custo por hectare; Fonte |
| CD-02 | Cadastros › Culturas, cultivares e operações | `g_op` | areas/cad_culturas.py:118 |  | Operação |
| CD-01 | Cadastros › Fazendas, áreas e talhões | `g_faz` | areas/cad_fazendas.py:252 |  | Fazenda; Área total |
| CD-01 | Cadastros › Fazendas, áreas e talhões | `g_tal` | areas/cad_fazendas.py:256 | árvore | Talhão; Área cultivável; Polígono; Diferença; Situação |
| CD-01 | Cadastros › Fazendas, áreas e talhões | `g_amb` | areas/cad_fazendas.py:273 |  | Área ambiental; Fazenda; Tipo; Área |
| CD-01 | Cadastros › Fazendas, áreas e talhões | `g_agua` | areas/cad_fazendas.py:281 |  | Ponto de água; Fazenda; Uso; Vazão; Situação |
| CD-01 | Cadastros › Fazendas, áreas e talhões | `g_idt` | areas/cad_fazendas.py:502 |  | Fazenda; Sistema; Área cultivável; Polígono; Diferença; Situação |
| CD-01 | Cadastros › Fazendas, áreas e talhões | `g_parc` | areas/cad_fazendas.py:507 | árvore | Safra · parcela; Cultura · variedade; Área; Livre; Plantio; Polígono |
| CD-05 | Cadastros › Parceiros e fornecedores | `g_forn` | areas/cad_parceiros.py:166 |  | Parceiro · CPF/CNPJ; Papéis; Contato; Situação do papel |
| CD-05 | Cadastros › Parceiros e fornecedores | `g_cob` | areas/cad_parceiros.py:170 |  | Grupo de insumo; Fornecedores que recebem cotação; Situação |
| CD-06 | Cadastros › Produtos, unidades e locais | `g_itm` | areas/cad_produtos_estrutura.py:87 | árvore | Grupo · item; Unidade · embalagem; Controle; Preço de referência; Situação |
| CD-06 | Cadastros › Produtos, unidades e locais | `g_grp` | areas/cad_produtos_estrutura.py:107 |  | Grupo |
| CD-06 | Cadastros › Produtos, unidades e locais | `g_loc` | areas/cad_produtos_estrutura.py:118 |  | Local; Fazenda; Tipo; Capacidade; Itens com este local padrão |
| CD-07 | Cadastros › Estrutura gerencial | `g_dim` | areas/cad_produtos_estrutura.py:259 | árvore | Dimensão · código; Vigência; Vínculos; Tradução no ERP (Sankhya); Situação |
| CA-01 | oculto | `g_os` | areas/campo.py:187 |  | O.S.; Atividade · local; Janela; Fase; Condição · próxima ação; Realizado · saldo; Equipe · conjunto |
| CA-01 | oculto | `g_ap` | areas/campo.py:251 |  | Data; Turno; Área do dia; Acumulado; Conferência; Origem · sincronização |
| CA-01 | oculto | `g_mat` | areas/campo.py:260 |  | Item · lote; Solicitado; Entregue; Consumido; Em custódia; A entregar; Custódia de |
| CA-01 | oculto | `g_ins` | areas/campo.py:313 |  | Produto; Dose da v2; Quantidade para 100 ha; Saldo de 70 ha na v3; Fonte |
| CA-01 | oculto | `g_ap0420` | areas/campo.py:326 |  | Data; Turno; Área do dia; Acumulado; Conferência; Origem · sincronização |
| CA-01 | oculto | `g_req0420` | areas/campo.py:331 |  | Requisição; Item; Solicitado; Entregue; Consumido; Em custódia; Custo apontado |
| CA-02 | oculto | `g_fila` | areas/campo.py:396 |  | Apontamento; Equipe · conjunto; Realizado · acumulado; Horas; Consumos e sobras; Origem · sincronização; Conferência · ação |
| CA-02 | oculto | `g_proj` | areas/campo.py:411 |  | Quando; Evento; Efeito; Quem |
| CA-03 | oculto | `g_oc` | areas/campo.py:467 |  | Ocorrência; Local · instante; Relato; Gravidade; Evidência; Destino · responsável; Próxima ação |
| CA-03 | oculto | `g_vinc` | areas/campo.py:494 |  | Registro; Tipo; Estado; Efeito |
| CA-03 | oculto | `g_trilha` | areas/campo.py:505 |  | Instante; Evento; Quem; Efeito |
| CA-04 | oculto | `g_req` | areas/campo.py:553 |  | Requisição · ordem; Item · lote; Solicitado; Entregue; Consumido; Devolvido decl. · receb.; Em custódia; Próxima ação |
| CO-01 | oculto | `g_of` | areas/colheita.py:160 |  | C('parc', l='Parcela · cultura · área', ; C('ciclo', l='Ciclo / estádio', w=100); C('plantas', l='Plantas vivas', w=100); C('peso', l='Peso · curva',  |
| CO-01 | oculto | `g_ped` | areas/colheita.py:176 |  | C('ped', l='Pedido'); C('pede', l='Cliente pede'); C('fut', l='Futuras em classe A'); C('falta', l='Falta'); C('sem', l='Semana'); C('sit', l='Situaçã |
| CO-01 | oculto | `g_wape` | areas/colheita.py:183 |  | C('ciclo', l='Ciclo'); C('ver', l='Versão congelada'); C('ant', l='Antecedência'); C('wape', l='WAPE'); C('vies', l='Viés'); C('am', l='Amostra'); C(' |
| CO-02 | oculto | `g_oc` | areas/colheita.py:229 |  | C('id', l='Ordem · origem', w=140); C('janela', l='Janela', w=90); C('etapa', l='Etapa · selo'); C('prev', l='Previsto', w=80); C('real', l='Realizado |
| CO-02 | oculto | `g_ap` | areas/colheita.py:257 |  | C('dia', l='Dia'); C('q', l='Quantidade', t='num', a='r', u; C('horas', l='Horas de equipe'); C('cargas', l='Cargas do dia', w=240); C('sit', l='Situa |
| CO-02 | oculto | `g_cv` | areas/colheita.py:266 |  | C('carga', l='Carga'); C('liq', l='Líquido', t='num', a='r', u=; C('qual', l='Qualidade inicial', w=240); C('dest', l='Destino'); C('vinc', l='Vínculo |
| CO-03 | oculto | `g_cg` | areas/colheita.py:318 |  | C('carga', l='Carga · hora · veículo', w; C('os', l='Ordem · origem', w=100); C('bt', l='Bruto − tara (kg)', a='r'); C('liq', l='Líquido', t='num', a= |
| CO-04 | oculto | `g_rc` | areas/colheita.py:372 |  | C('ent', l='Entrada · origem', w=140); C('peso', l='Peso recebido', w=90); C('local', l='Local', w=120); C('cond', l='Condição', chips=COND); C('am',  |
| CO-05 | oculto | `g_ob` | areas/colheita.py:403 |  | C('id', l='Ordem · produto · rota', w=17; C('janela', l='Janela', w=90); C('etapa', l='Etapa', chips=ETAPA_CH); C('ent', l='Lotes de entrada · origem' |
| CO-05 | oculto | `g_bal` | areas/colheita.py:439 |  | C('fluxo', l='Fluxo'); C('q', l='Quantidade', t='num', a='r', u; C('classe', l='Classe / destino', w=260); C('lote', l='Lote'); C('sit', l='Situação', |
| CO-06 | oculto | `g_in` | areas/colheita.py:528 |  | C('insp', l='Inspeção · lote', w=130); C('prod', l='Produto', w=90); C('pad', l='Padrão · amostra', w=120); C('res', l='Resultado'); C('dec', l='Decis |
| CO-06 | oculto | `g_pd` | areas/colheita.py:558 |  | C('pend', l='Pendência'); C('lote', l='Lote'); C('q', l='Quantidade', a='r'); C('resp', l='Responsável'); C('przo', l='Prazo'); C('cond', l='Condição  |
| CO-06 | oculto | `g_am` | areas/colheita.py:563 |  | C('crit', l='Critério'); C('pad', l='Padrão do tipo 6'); C('med', l='Medido', a='r'); C('sit', l='Situação') |
| CO-06 | oculto | `g_ef` | areas/colheita.py:569 |  | C('tent', l='Tentativa', w=260); C('orig', l='Origem'); C('res', l='Resultado') |
| CO-07 | oculto | `g_es` | areas/colheita.py:620 |  | C('lote', l='Lote · local · proprietário; C('prod', l='Produto · classe · validade; C('fis', l='Físico', a='r', w=100); C('qual', l='Qualidade'); C('r |
| VE-01/VE-02/VE-03/VE-04/VE-05/VE-06 | oculto | `g_bal` | areas/comercial.py:142 |  | C('prod', 'Produto · classe', w=160); C('janela', 'Janela'); C('dem', 'Demanda', w=220); C('ofe', 'Oferta', w=220); C('saldo', 'Falta ou excesso', w=2 |
| VE-01/VE-02/VE-03/VE-04/VE-05/VE-06 | oculto | `g_res` | areas/comercial.py:153 |  | C('res', 'Reserva', w=170); C('tipo', 'Tipo'); C('qt', 'Quantidade', a='r'); C('venc', 'Vencimento'); C('estado', 'Estado'); C('efeito', 'Efeito no sa |
| VE-01/VE-02/VE-03/VE-04/VE-05/VE-06 | oculto | `g_pr` | areas/comercial.py:197 |  | C('inst', 'Instrumento', w=200); C('fonte', 'Fonte · licença'); C('praca', 'Praça'); C('un', 'Unidade'); C('moeda', 'Moeda'); C('venc', 'Vencimento/da |
| VE-01/VE-02/VE-03/VE-04/VE-05/VE-06 | oculto | `g_al` | areas/comercial.py:201 |  | C('inst', 'Instrumento', w=180); C('cond', 'Condição'); C('lim', 'Limite', t='num', a='r', pre='; C('canal', 'Avisar por'); C('val', 'Validade', t='da |
| VE-01/VE-02/VE-03/VE-04/VE-05/VE-06 | oculto | `g_of` | areas/comercial.py:248 |  | C('of', 'Oferta', w=150); C('vol', 'Volume', a='r'); C('janela', 'Janela'); C('dest', 'Destino · clientes', w=170); C('pr', 'Preço · condição'); C('es |
| VE-01/VE-02/VE-03/VE-04/VE-05/VE-06 | oculto | `g_cmp` | areas/comercial.py:259 |  | C('prop', 'Proposta', w=220); C('cli', 'Cliente'); C('preco', 'Preço', a='r'); C('frete', 'Frete por conta'); C('prazo', 'Prazo'); C('liq', 'Líquido/k |
| VE-01/VE-02/VE-03/VE-04/VE-05/VE-06 | oculto | `g_cart` | areas/comercial.py:321 |  | C('ped', 'Pedido', w=90); C('cli', 'Cliente'); C('item', 'Item · classe'); C('qt', 'Quantidade · janela', a='r', w=; C('pr', 'Preço · condição', w=160 |
| VE-01/VE-02/VE-03/VE-04/VE-05/VE-06 | oculto | `g_rsv` | areas/comercial.py:335 |  | C('ped', 'Pedido · cliente', w=200); C('prod', 'Produto', w=190); C('tipo', 'Tipo · janela', w=160); Quantidade; Reservado; Falta; C('sit', 'Situação  |
| VE-01/VE-02/VE-03/VE-04/VE-05/VE-06 | oculto | `g_ver` | areas/comercial.py:381 |  | C('ver', 'Versão', w=70); C('qt', 'Quantidade', a='r'); C('pr', 'Preço · medição'); C('janela', 'Janela'); C('frete', 'Frete'); C('venc', 'Vencimento' |
| VE-01/VE-02/VE-03/VE-04/VE-05/VE-06 | oculto | `g_at` | areas/comercial.py:392 |  | C('orig', 'Origem', w=230); C('tipo', 'Tipo de alocação'); C('qt', 'Quantidade', a='r'); C('estado', 'Estado', w=210); C('obs', 'Rastreio', w=300) |
| VE-01/VE-02/VE-03/VE-04/VE-05/VE-06 | oculto | `g_fin` | areas/comercial.py:406 |  | C('ev', 'Evento', w=200); C('base', 'Base'); C('val', 'Valor previsto', a='r'); C('venc', 'Vencimento'); C('estado', 'Estado') |
| VE-01/VE-02/VE-03/VE-04/VE-05/VE-06 | oculto | `g_ob` | areas/comercial.py:462 |  | C('ob', 'Obrigação · contraparte', w=180; C('prod', 'Produto · janela', w=190); C('vol', 'Volume', t='num', a='r', u='sc; C('cond', 'Condições · víncu |
| VE-01/VE-02/VE-03/VE-04/VE-05/VE-06 | oculto | `g_dim` | areas/comercial.py:471 |  | C('dim', 'Dimensão', w=200); C('vol', 'Volume', t='num', a='r', u='sc; C('pct', '% da previsão V2', a='r'); C('comp', 'Composição', w=380) |
| VE-01/VE-02/VE-03/VE-04/VE-05/VE-06 | oculto | `g_rc` | areas/comercial.py:518 |  | C('rc', 'Caso', w=70); C('ped', 'Pedido · entrega', w=200); C('motivo', 'Motivo · evidências', w=190; C('lq', 'Lote · quantidade', w=140); C('dec', 'D |
| CF-01/CF-02/CF-03/CF-04 | oculto | `g_usr` | areas/configuracoes.py:103 |  | C('ident', 'Identidade', w=200); C('papel', 'Papel', w=170); C('escopo', 'Escopo', w=150); C('vig', 'Vigência', w=130); C('auth', 'Autenticação', w=13 |
| CF-01/CF-02/CF-03/CF-04 | oculto | `g_dev` | areas/configuracoes.py:122 |  | C('disp', 'Dispositivo · usuário', w=200; C('ult', 'Último sincronismo'); C('pacote', 'Pacote offline', w=300); C('acao', 'Ação') |
| CF-01/CF-02/CF-03/CF-04 | oculto | `g_alc` | areas/configuracoes.py:180 |  | C('cmd', 'Comando · alçada · fonte', w=2; C('dono', 'Dono (quem decide)', w=200); C('lim', 'Valor / limite', w=210); C('classe', 'Classe de bloqueio', |
| CF-01/CF-02/CF-03/CF-04 | oculto | `g_pol` | areas/configuracoes.py:196 |  | C('regra', 'Regra/ID · proprietário', w=; C('escopo', 'Escopo', w=150); C('lim', 'Limites', w=210); C('aprov', 'Aprovadores', w=150); C('vig', 'Vigênc |
| CF-01/CF-02/CF-03/CF-04 | oculto | `g_def` | areas/configuracoes.py:234 |  | C('campo', 'Campo', w=170); C('vig', 'Valor vigente (v2)', w=330); C('prop', 'Proposta (v3 · em revisão)',  |
| CF-01/CF-02/CF-03/CF-04 | oculto | `g_tst` | areas/configuracoes.py:243 |  | C('caso', 'Caso', w=180); C('ent', 'Entrada', w=280); C('esp', 'Resultado esperado', w=280); C('sit', 'Situação') |
| CF-01/CF-02/CF-03/CF-04 | oculto | `g_obj` | areas/configuracoes.py:251 |  | C('obj', 'Objeto', w=300); C('cond', 'Condição', w=420); C('abrir', 'Abrir') |
| CF-01/CF-02/CF-03/CF-04 | oculto | `g_v3` | areas/configuracoes.py:255 |  | C('ver', 'Versão'); C('mud', 'Mudança proposta', w=300); C('por', 'Proposta por'); C('sit', 'Situação', w=240) |
| CF-01/CF-02/CF-03/CF-04 | oculto | `g_con` | areas/configuracoes.py:292 |  | C('con', 'Conector / escopo', w=180); C('fonte', 'Fonte oficial (escritor)', w; C('est', 'Estado · erros', w=200); C('ult', 'Atualização · evento', w= |
| CF-01/CF-02/CF-03/CF-04 | oculto | `g_err` | areas/configuracoes.py:303 |  | C('item', 'Item · direção', w=220); C('erro', 'Erro / estado', w=250); C('ct', 'Correlação · tentativas', w=180; C('resp', 'Responsável', w=130); C('a |
| CF-01/CF-02/CF-03/CF-04 | oculto | `g_off` | areas/configuracoes.py:315 |  | C('disp', 'Dispositivo', w=170); C('pend', 'Registro', w=210); C('idr', 'Identidade · recibo', w=150); C('comp', 'Comportamento verificado', w=; C('si |
| CF-01/CF-02/CF-03/CF-04 | oculto | `g_rec` | areas/configuracoes.py:354 |  | C('doc', 'Documento / linha', w=200); C('corr', 'Correlação'); C('plat', 'Plataforma', w=180); C('erp', 'ERP (Sankhya)', w=160); C('dif', 'Diferença', |
| CF-01/CF-02/CF-03/CF-04 | oculto | `g_syn` | areas/configuracoes.py:364 |  | C('rel', 'Relato · dispositivo', w=200); C('idl', 'Identidade local', w=120); C('rec', 'Recibo', w=160); C('area', 'Área', t='num', a='r', u='ha'; C(' |
| CF-01/CF-02/CF-03/CF-04 | oculto | `g_tr` | areas/configuracoes.py:426 |  | C('inst', 'Instante (BRT)', w=100); C('obj', 'Objeto / versão', w=190); C('aut', 'Autor / origem', w=150); C('ad', 'Antes → depois · motivo', w=290; C |
| CF-01/CF-02/CF-03/CF-04 | oculto | `g_par` | areas/configuracoes.py:431 |  | C('par', 'Parâmetro', w=200); C('val', 'Valor', w=300); C('fonte', 'Fonte'); C('sit', 'Situação') |
| CF-01/CF-02/CF-03/CF-04 | oculto | `g_doc` | areas/configuracoes.py:438 |  | C('tipo', 'Tipo'); C('proc', 'Processo', w=180); C('gar', 'O que garante', w=320); C('ex', 'Exemplo', w=220); C('abrir', 'Abrir') |
| GE-01 | oculto | `g_res` | areas/gestao.py:140 |  | C('cult', 'Cultura', w=190); C('ha', 'Área', t='num', a='r', u='ha', ; C('rec', 'Receita', t='num', a='r', d=2,; C('mar', 'Margem', t='num', a='r', d= |
| GE-01 | oculto | `g_cau` | areas/gestao.py:145 |  | C('desvio', 'Desvio', w=240); C('onde', 'Onde', w=200); C('efeito', 'Efeito', w=210); C('orig', 'Origem do dado'); C('prox', 'Próxima ação') |
| GE-02 | oculto | `g_ver` | areas/gestao.py:179 |  | C('ver', 'Versão', w=190); C('prem', 'Premissas', w=210); C('vol', 'Volume soja', t='num', a='r', ; C('preco', 'Preço soja (R$/sc)', t='num'; C('custo |
| GE-02 | oculto | `g_cx` | areas/gestao.py:189 |  | C('tri', 'Trimestre'); C('v1', 'Desembolso V1', t='num', a='r',; C('v2', 'Desembolso V2', t='num', a='r',; C('dif', 'Diferença', t='num', a='r', d=; C |
| GE-02 | oculto | `g_cmp` | areas/gestao.py:220 |  | C('g', 'Grandeza', w=170); C('v1', 'Orçado V1'); C('v2', 'Previsão V2'); C('real', 'Real (encerrada)'); C('dif', 'Diferença V1→real'); C('fonte', 'Fon |
| GE-03 | oculto | `g_lan` | areas/gestao.py:291 |  | C('doc', 'Origem (documento)', w=190); C('comp', 'Componente', w=170); C('dim', 'Dimensões', w=185); C('qp', 'Qtd × preço', a='r'); C('val', 'Valor',  |
| GE-04 | oculto | `g_tit` | areas/gestao.py:356 |  | C('cred', 'Credor · documento', w=180); C('orig', 'Origem', w=185); C('venc', 'Vencimento', t='date', w=130); C('princ', 'Principal · pago / saldo', t |
| GE-05 | oculto | `g_rec` | areas/gestao.py:418 | árvore | C('tit', 'Cliente · título', w=190); C('orig', 'Pedido · entrega', w=205); C('venc', 'Vencimento', t='date', w=130); C('val', 'Valor', t='num', a='r', |
| GE-06 | oculto | `g_ind` | areas/gestao.py:475 |  | C('ind', 'Indicador', w=170); C('proc', 'Processo'); C('form', 'Fórmula · fonte', w=190); C('meta', 'Meta · período', a='r'); C('real', 'Realizado · t |
| GE-06 | oculto | `g_atv` | areas/gestao.py:480 |  | C('at', 'Ativo · classe', w=210); C('disp', 'Disponibilidade'); C('ut', 'Utilização', a='r'); C('mtbf', 'MTBF', a='r'); C('mttr', 'MTTR', a='r'); C('c |
| GE-06 | oculto | `g_cau` | areas/gestao.py:503 |  | C('causa', 'Causa', w=220); C('ef', 'Efeito', a='r'); C('ev', 'Evidência'); C('hip', 'Hipótese a validar', w=300) |
| GE-06 | oculto | `g_doc` | areas/gestao.py:508 |  | C('doc', 'Documento', w=220); C('sust', 'O que sustenta', w=300); C('dt', 'Data'); C('ab', 'Abrir') |
| GE-07 | oculto | `g_ac` | areas/gestao.py:551 |  | C('caso', 'Caso', w=150); C('orig', 'Origem · indicador', w=155); C('hip', 'Hipótese · ação definida', w=2; C('dono', 'Dono', w=110); C('prazo', 'Praz |
| GE-08 | oculto | `g_cre` | areas/gestao.py:596 |  | C('sol', 'Solicitação'); C('fin', 'Finalidade', w=135); C('cred', 'Credor'); C('val', 'Valor', t='num', a='r', pre='R; C('gar', 'Garantia', w=135); C( |
| GE-08 | oculto | `g_dos` | areas/gestao.py:606 |  | C('blk', 'Bloco do dossiê', w=190); C('cont', 'Conteúdo', w=260); C('aut', 'Autorizado para', w=200); C('prz', 'Prazo de acesso', t='date'); C('st', ' |
| IN-02 | oculto | `g_ap` | areas/inicio.py:1339 |  | Objeto e decisão; Solicitante · alçada; Vencimento; Efeito · valor; Conflito; Situação |
| IN-01 | oculto | `g_dia` | areas/inicio.py:1379 |  | Objeto · local; Tarefa; Prazo; Responsável; Impedimento; Próxima ação |
| IN-03 | oculto | `g_ag` | areas/inicio.py:1415 |  | Data; Compromisso; Responsável; Prioridade; Condição · bloqueio; Prazo limite; Abrir |
| IR-01 | Agrícola › Irrigação | `g_set` | areas/irrigacao.py:151 |  | Setor; Déficit hoje; Necessidade; Situação; Próximo passo |
| IR-02 | Agrícola › Irrigação (tela irmã) | `g_ag` | areas/irrigacao.py:213 | árvore | Captação · ordem; Setor · bomba; Janela; Lâmina; Etapa · pendência |
| IR-03 | Agrícola › Irrigação (tela irmã) | `g_os` | areas/irrigacao.py:295 |  | Ordem; Setor; Janela; Lâmina; Etapa; Próximo passo |
| IR-03 | Agrícola › Irrigação (tela irmã) | `g_pas` | areas/irrigacao.py:337 |  | Passada; Janela; Lâmina; Duração; Estado; Área coberta |
| IR-03 | Agrícola › Irrigação (tela irmã) | `g_trl` | areas/irrigacao.py:339 |  | Quando; Recibo; Evento; Quem |
| IR-04 | Agrícola › Irrigação (tela irmã) | `g_src` | areas/irrigacao.py:538 |  | Fonte; Atualização; Calibração; Cobertura; Estado; Efeito no balanço |
| IR-04 | Agrícola › Irrigação (tela irmã) | `g_cap` | areas/irrigacao.py:546 |  | Captação; Vazão outorgada; Vencimento; Situação; Uso hoje; Setores ligados |
| IR-04 | Agrícola › Irrigação (tela irmã) | `g_des` | areas/irrigacao.py:555 |  | Setor; Volume; Energia; Lâmina aplicada; Eficiência; Indicador |
| LO-01/LO-02/LO-03/LO-04 | oculto | `g_ag` | areas/logistica.py:161 |  | C('carga', 'Carga · tipo', w=130); C('prod', 'Produto · rota', w=195); C('jan', 'Janela', w=160); C('veic', 'Veículo · compatibilidade', w; C('custo', |
| LO-01/LO-02/LO-03/LO-04 | oculto | `g_cp` | areas/logistica.py:166 |  | C('cand', 'Candidata a agrupar com a Car; C('cons', 'Produto · conservação'); C('rota', 'Rota'); C('jan', 'Janela'); C('comp', 'Compatibilidade', w=26 |
| LO-01/LO-02/LO-03/LO-04 | oculto | `g_sl` | areas/logistica.py:186 |  | C('slot', 'Slot'); C('doca', 'Doca'); C('carga', 'Carga · transportador', w=19; C('dur', 'Duração', w=170); C('resp', 'Responsabilidade', w=210); C('e |
| LO-01/LO-02/LO-03/LO-04 | oculto | `g_fi` | areas/logistica.py:246 |  | C('veic', 'Veículo', w=130); C('pos', 'Pos.', t='num', a='r'); C('jan', 'Janela original'); C('cheg', 'Chegada real · espera', w=150; C('sit', 'Situaç |
| LO-01/LO-02/LO-03/LO-04 | oculto | `g_ex` | areas/logistica.py:269 |  | C('ped', 'Pedido · destino', w=170); C('lote', 'Lote · quantidade', w=190); C('veic', 'Veículo · doca', w=120); C('doc', 'Documento', w=190); C('etapa |
| LO-01/LO-02/LO-03/LO-04 | oculto | `g_po` | areas/logistica.py:273 |  | C('veic', 'Veículo'); C('jan', 'Janela original'); C('cheg', 'Chegada real', w=220); C('pont', 'Pontualidade (vs. janela orig; C('esp', 'Espera desde  |
| LO-01/LO-02/LO-03/LO-04 | oculto | `g_cf` | areas/logistica.py:376 |  | C('item', 'Item', w=170); C('lote', 'Lote'); C('ped', 'Pedido (parcela)', a='r'); C('sep', 'Separado', a='r'); C('car', 'Carregado', a='r'); C('saldo' |
| LO-01/LO-02/LO-03/LO-04 | oculto | `g_ps` | areas/logistica.py:380 |  | C('tk', 'Ticket'); C('tara', 'Tara', a='r'); C('bruto', 'Bruto', a='r'); C('liq', 'Líquido', a='r'); C('base', 'Umidade · base'); C('orig', 'Origem da |
| LO-01/LO-02/LO-03/LO-04 | oculto | `g_ck` | areas/logistica.py:384 |  | C('item', 'Verificação', w=300); C('estado', 'Estado', w=250); C('resp', 'Responsável', w=200) |
| LO-01/LO-02/LO-03/LO-04 | oculto | `g_sa` | areas/logistica.py:395 |  | C('ev', 'Evento', w=220); C('estado', 'Estado', w=280); C('quem', 'Quem · quando', w=220) |
| LO-01/LO-02/LO-03/LO-04 | oculto | `g_vg` | areas/logistica.py:463 |  | C('vg', 'Viagem'); C('carga', 'Carga → destinatário', w=220; C('ev', 'Eventos · evidência', w=200); C('rec', 'Recebido · ocorrência', w=200); C('estad |
| LO-01/LO-02/LO-03/LO-04 | oculto | `g_tar` | areas/logistica.py:467 |  | C('reg', 'Registro', w=240); C('val', 'Valor', w=520) |
| LO-01/LO-02/LO-03/LO-04 | oculto | `g_rt` | areas/logistica.py:474 |  | C('vg', 'Viagem'); C('dir', 'Direcionador · versão'); C('base', 'Base', a='r'); C('comp', 'Componentes', w=300); C('tot', 'Total', t='num', a='r', pre |
| LO-01/LO-02/LO-03/LO-04 | oculto | `g_ct` | areas/logistica.py:512 |  | C('prest', 'Prestador', w=190); C('base', 'Base'); C('total', 'Custo total', t='num', a='r'; C('prazo', 'Prazo'); C('cons', 'Conservação'); C('inc', ' |
| LO-01/LO-02/LO-03/LO-04 | oculto | `g_pr` | areas/logistica.py:527 |  | C('prest', 'Prestador · rota', w=200); C('preco', 'Preço', a='r'); C('cond', 'Condição', w=170); C('docs', 'Documentos', w=210); C('desemp', 'Desempen |
| LO-01/LO-02/LO-03/LO-04 | oculto | `g_sv` | areas/logistica.py:532 |  | C('vg', 'Viagem'); C('prest', 'Prestador', w=150); C('med', 'Medição', w=200); C('rat', 'Rateio aplicado', w=150); C('val', 'Valor do serviço', t='num |
| LO-01/LO-02/LO-03/LO-04 | oculto | `g_ra` | areas/logistica.py:539 |  | C('dir', 'Direcionador', w=170); C('ver', 'Versão'); C('quando', 'Quando usar', w=230); C('salv', 'Salvaguardas', w=420) |
| MA-01 | Manutenção › Ativos e disponibilidade | `g_at` | areas/maquinas.py:136 |  | Ativo · local · contador; Condição; Agenda; Elegível; Próxima manutenção; Uso 30 d |
| MA-01 | Manutenção › Ativos e disponibilidade | `g_ut` | areas/maquinas.py:155 |  | Grupo/classe; Ativos; Horas trabalhadas 30 d; Horas disponíveis 30 d; Utilização |
| MA-02 | Manutenção › Solicitações e inspeções | `g_cs` | areas/maquinas.py:239 |  | Caso; Ativo; Sintoma · contador · evidência; Criticidade; Condição recomendada · responsável; Ação |
| MA-02 | Manutenção › Solicitações e inspeções | `g_pa` | areas/maquinas.py:256 |  | Item/sistema; Achados; Ativos afetados; Horas paradas; % das horas paradas; Acumulado |
| MA-02 | Manutenção › Solicitações e inspeções | `g_ct` | areas/maquinas.py:261 |  | Ordem de campo; Efeito; Tratamento; Abrir |
| MA-03 | Manutenção › Vencimentos e paradas | `g_vc` | areas/maquinas.py:311 |  | Ativo; Serviço; Leitura · última; Próximo vencimento; Situação; Ordem |
| MA-03 | Manutenção › Vencimentos e paradas | `g_mi` | areas/maquinas.py:312 |  | Manutenção; Janela; Produção afetada; Situação; Abrir |
| MA-04 | Manutenção › Ordens de manutenção | `g_om` | areas/maquinas.py:544 |  | Ordem · ativo; Serviço · tipo; Janela; Fase · selos; Checklist · peças; Ação |
| MA-04 | Manutenção › Ordens de manutenção | `g_ib` | areas/maquinas.py:561 |  | Objeto afetado; Efeito; Tratamento; Situação; Abrir |
| MA-04 | Manutenção › Ordens de manutenção | `g_tk` | areas/maquinas.py:565 |  | Tarefa; Situação; Horas; Peças aplicadas |
| MA-04 | Manutenção › Ordens de manutenção | `g_te` | areas/maquinas.py:572 |  | Teste; Quando; Resultado; Efeito |
| MA-04 | Manutenção › Ordens de manutenção | `g_sb` | areas/maquinas.py:574 |  | Item; Destinação; Responsável |
| MA-05 | Manutenção › Abastecimentos e desempenho | `g_ab` | areas/maquinas.py:669 |  | Lançamento · operador; Ativo; Tanque/lote · nível após; Volume; Data · contador; Método / taxa; Ação |
| MA-05 | Manutenção › Abastecimentos e desempenho | `g_co` | areas/maquinas.py:686 |  | Ativo; Litros no período; Horas trabalhadas; Taxa; Método; Desvio vs. referência |
| PM | Manutenção › Planos de manutenção | `g_pv` | areas/maquinas.py:1121 |  | Ativo; Serviço; Leitura · última; Próximo vencimento; Situação; Ordem |
| ON-01 | oculto | `g_passos` | areas/onboarding_backoffice.py:83 |  | Passo; Estado; Dado pedido no momento do uso; Próxima ação |
| ON-01 | oculto | `g_trial` | areas/onboarding_backoffice.py:93 |  | Recurso; Habilitação; Franquia; Unidade; Ao esgotar ou expirar |
| ON-01 | oculto | `g_imp` | areas/onboarding_backoffice.py:168 |  | Objeto; Linhas; Mapeamento; Sistema de coordenadas; Erro; Estado |
| PT-01 | oculto | `g_op` | areas/parceiros.py:130 |  | C('op', 'Oportunidade', w=260); C('acesso', 'Convite e acesso', w=240); C('prazo', 'Prazo'); C('sit', 'Situação', w=230); C('acao', 'Abrir') |
| PT-01 | oculto | `g_av` | areas/parceiros.py:144 |  | C('aviso', 'Aviso', w=460); C('reg', 'Registro'); C('abrir', 'Abrir') |
| PT-02 | oculto | `g_cot` | areas/parceiros.py:164 |  | C('cot', 'Cotação', w=240); C('item', 'Itens e volume', w=200); C('prazo', 'Responder até'); C('sit', 'Proposta e situação', w=230); C('acao', 'Abrir' |
| PT-02 | oculto | `g_dos` | areas/parceiros.py:185 |  | C('campo', 'Campo', w=180); C('valor', 'Valor', w=420); C('fonte', 'Fonte', w=260) |
| PT-02 | oculto | `g_it` | areas/parceiros.py:191 |  | C('item', 'Item', w=220); C('qtd', 'Quantidade', t='num', a='r', u; C('preco', 'Preço (R$/kg)', t='num', a='; C('tot', 'Total', t='num', a='r', pre='R |
| PT-02 | oculto | `g_cd` | areas/parceiros.py:198 |  | C('frete', 'Frete', w=200); C('pag', 'Pagamento'); C('prazo', 'Prazo de entrega', t='num', ; C('val', 'Validade', t='date'); C('obs', 'Observações', w |
| PT-02 | oculto | `g_esc` | areas/parceiros.py:205 |  | C('perg', 'Pergunta', w=360); C('de', 'De · quando'); C('resp', 'Resposta', w=300); C('sit', 'Situação') |
| PT-03 | oculto | `g_of` | areas/parceiros.py:237 |  | C('of', 'Oferta', w=120); C('prod', 'Produto e padrão', w=200); C('vol', 'Volume e janela'); C('preco', 'Preço, condição e local', w=; C('val', 'Valid |
| PT-03 | oculto | `g_rv` | areas/parceiros.py:247 |  | C('res', 'Reserva'); C('tipo', 'Tipo'); C('qtd', 'Quantidade', t='num', a='r', u; C('venc', 'Vencimento'); C('est', 'Estado'); C('efe', 'Efeito', w=42 |
| PT-03 | oculto | `g_pp` | areas/parceiros.py:251 |  | C('vol', 'Volume', t='num', a='r', u='kg; C('jan', 'Janela de entrega'); C('preco', 'Preço proposto', t='num', a=; C('local', 'Local de entrega'); C(' |
| PT-04 | oculto | `g_ds` | areas/parceiros.py:280 |  | C('dos', 'Dossiê', w=260); C('fin', 'Finalidade e blocos concedidos; C('vig', 'Vigência do acesso'); C('sit', 'Situação', w=220); C('acao', 'Abrir') |
| PT-04 | oculto | `g_hist` | areas/parceiros.py:287 |  | C('q', 'Quando', w=120); C('u', 'Usuário', w=220); C('b', 'Bloco acessado'); C('f', 'Finalidade') |
| PT-04 | oculto | `g_con` | areas/parceiros.py:303 |  | C('campo', 'Campo', w=180); C('valor', 'Valor', w=560) |
| PT-04 | oculto | `g_blk` | areas/parceiros.py:309 |  | C('b', 'Bloco', w=180); C('c', 'Conteúdo', w=300); C('f', 'Fonte', w=220); C('val', 'Validade'); C('s', 'Situação', w=220) |
| PT-05 | oculto | `g_ng` | areas/parceiros.py:341 |  | C('neg', 'Negócio', w=240); C('res', 'Resultado'); C('cond', 'Condição aceita', w=190); C('doc', 'Pedido e documento', w=220); C('ent', 'Entrega', w=2 |
| PT-05 | oculto | `g_msg` | areas/parceiros.py:351 |  | C('neg', 'Negócio'); C('de', 'De · quando'); C('m', 'Mensagem', w=520) |
| PT-05 | oculto | `g_cond` | areas/parceiros.py:367 |  | C('campo', 'Campo', w=180); C('valor', 'Valor', w=520) |
| PT-05 | oculto | `g_cg` | areas/parceiros.py:373 |  | C('c', 'Carga', w=140); C('q', 'Quantidade', t='num', a='r', u='; C('d', 'Data prevista', t='date'); C('placa', 'Placa'); C('doc', 'Documento', w=220) |
| PT-05 | oculto | `g_dc` | areas/parceiros.py:383 |  | C('doc', 'Documento', w=200); C('carga', 'Carga'); C('prazo', 'Prazo'); C('s', 'Situação', w=200) |
| PT-06 | oculto | `g_fu` | areas/parceiros.py:410 |  | C('e', 'Etapa', w=220); C('q', 'Quantidade', t='num', a='r'); C('val', 'Valor', t='num', a='r', pre='R; C('conv', 'Conversão da etapa', w=220) |
| PT-06 | oculto | `g_co` | areas/parceiros.py:422 |  | C('reg', 'Categoria · região', w=300); C('conv', 'Convites', t='num', a='r'); C('gan', 'Ganhos', t='num', a='r'); C('rec', 'Receita própria', t='num', |
| PT-06 | oculto | `g_ag` | areas/parceiros.py:427 |  | C('i', 'Indicador agregado', w=380); C('p', 'Sua posição'); C('n', 'Amostra'); C('s', 'Situação') |
| PT-07 | oculto | `g_emp` | areas/parceiros.py:449 |  | C('emp', 'Empresa · CNPJ', w=220); C('cat', 'Categorias', w=180); C('reg', 'Regiões', w=170); C('cult', 'Culturas atendidas', w=180); C('mail', 'E-mai |
| PT-07 | oculto | `g_pref` | areas/parceiros.py:456 |  | C('tipo', 'Aviso', w=260); C('canal', 'Canal', w=220) |
| PT-07 | oculto | `g_us` | areas/parceiros.py:462 |  | C('nome', 'Usuário', w=180); C('mail', 'E-mail', w=220); C('papel', 'Papel'); C('sit', 'Situação'); C('acao', 'Ação') |
| PT-07 | oculto | `g_pl` | areas/parceiros.py:472 |  | C('item', 'Item', w=300); C('cond', 'Condição', w=280); C('vig', 'Vigência'); C('sit', 'Situação', w=220) |
| PL-01/PL-02/PL-03/PL-04/PL-05/PL-06 | oculto | `g_saf` | areas/planejamento.py:151 |  | Safra; Período; Fazenda; Cultivos · área; Situação; Abrir |
| PL-01/PL-02/PL-03/PL-04/PL-05/PL-06 | oculto | `g_cult` | areas/planejamento.py:166 |  | Talhão/parcela; Cultura; Variedade; Área; Plantio previsto; Meta (hipótese); Plano |
| PL-01/PL-02/PL-03/PL-04/PL-05/PL-06 | oculto | `g_op` | areas/planejamento.py:227 |  | Parcela · cultivo; Atividade · necessidade; Dose/quantidade; Gatilho por extenso → data; Situação; Abrir |
| PL-01/PL-02/PL-03/PL-04/PL-05/PL-06 | oculto | `g_tal` | areas/planejamento.py:291 |  | Atividade; Gatilho por extenso; Data resultante; Estado; Dose local; Dose padrão |
| PL-01/PL-02/PL-03/PL-04/PL-05/PL-06 | oculto | `g_cap` | areas/planejamento.py:337 |  | Recurso/classe; Operação dominante; Carga out/26; Capacidade líquida; Ocupado; Livre; Sem alocação; Indisponível; Déficit |
| PL-01/PL-02/PL-03/PL-04/PL-05/PL-06 | oculto | `g_cen` | areas/planejamento.py:346 |  | Cenário; Cobre; Custo estimado (hipótese); Restrição; Comparação |
| PL-01/PL-02/PL-03/PL-04/PL-05/PL-06 | oculto | `g_ord` | areas/planejamento.py:409 |  | Ordem; Janela · duração; Conjunto · operador; Impedimento · selo; Etapa · material; Abrir |
| PL-01/PL-02/PL-03/PL-04/PL-05/PL-06 | oculto | `g_maq` | areas/planejamento.py:415 |  | Máquina; Condição; Ocupação no período; Elegibilidade |
| PL-01/PL-02/PL-03/PL-04/PL-05/PL-06 | oculto | `g_pen` | areas/planejamento.py:421 |  | Ordem; Etapa; Selo; Pendência; Ação |
| PL-01/PL-02/PL-03/PL-04/PL-05/PL-06 | oculto | `g_imp` | areas/planejamento.py:485 |  | Causa · origem; Afetados · impacto; Responsável; Prazo; Alternativa · aprovação; Ação |
| PL-01/PL-02/PL-03/PL-04/PL-05/PL-06 | oculto | `g_par` | areas/planejamento.py:577 |  | Parcela · geometria; Área; Ciclo e ocupação; Variedade; Plantio próprio; Janela de colheita; Preparo/limpeza; Situação |
| PL-01/PL-02/PL-03/PL-04/PL-05/PL-06 | oculto | `g_sem` | areas/planejamento.py:591 |  | Semana; Oferta; Entregas contratadas; Saldo; Capacidade colheita/secagem |
| BO-02 | oculto | `g_org` | areas/plataforma.py:111 |  | Organização; Plano; Estado; Área medida (ha); Área contratada (ha); Mensalidade (R$); Fatura aberta; Próximo evento |
| BO-02 | oculto | `g_fila` | areas/plataforma.py:115 |  | Evento; Organização; Fatura; Valor (R$); Resultado; Situação |
| BO-01 | oculto | `g_par` | areas/plataforma.py:164 |  | Plano; Módulos; Limite de área; Usuários; Franquias; Preço R$/ha·mês; Mínimo R$/mês; Equivalente R$/ha·ano; Decisão pendente |
| BO-01 | oculto | `g_sim` | areas/plataforma.py:170 |  | Área (ha); <[dict(k=P['id'], l=P['nome'] + ' (R$)', t='num', a='r', d=2)> |
| BEN | Produção › Recebimento e beneficiamento (Beneficiamento) | `g_ob` | areas/processo_beneficiamento.py:18 |  | Ordem; Produto; Fase; Condição; Em processo; Próximo passo; Quem resolve |
| CMP | Suprimentos › Compra de insumos | `g_saf` | areas/processo_compras.py:73 |  | Safra; Solicitação de compra; Origem; Compra; Ação |
| CMP | Suprimentos › Compra de insumos | `g_dem` | areas/processo_compras.py:76 | árvore | Grupo · insumo; Bruta; Estoque apto; A receber; Necessidade; Un.; Falta a partir de; Preço ref.; Valor (R$); Na compra |
| CMP | Suprimentos › Compra de insumos | `g_conv` | areas/processo_compras.py:82 | árvore | Grupo · fornecedor; Homologação; Convite; Canal e contato; Responder até; Resposta |
| CMP | Suprimentos › Compra de insumos | `g_cmp` | areas/processo_compras.py:90 | árvore | Grupo · insumo · proposta; A pedir; Preço (R$); Entrega; Frete; Pagamento; Validade; Custo (R$); Escolha |
| CMP | Suprimentos › Compra de insumos | `g_apr` | areas/processo_compras.py:99 | árvore | Pedido · fornecedor · insumo; Quantidade; Preço (R$/un); Entrega (dias); Frete; Pagamento; Valor (R$) |
| CMP | Suprimentos › Compra de insumos | `g_ent` | areas/processo_compras.py:103 | árvore | Pedido · fornecedor · insumo; Pedido; Recebido; A entregar; Valor (R$); Previsão; Situação; Ação |
| EST | Suprimentos › Estoque | `g_rec` | areas/processo_estoque.py:81 |  | Nota fiscal; Data da nota; Conferida em; Pedido; Fornecedor; Item; Lote; Na nota; Conferida; Apta; Quarentena; Situação; Divergência; Validade |
| EST | Suprimentos › Estoque | `g_ent` | areas/processo_estoque.py:98 |  | Requisição; O.S.; Fase da O.S.; Item; Lote; Embalagem; Solicitado; Entregue; A entregar; A entregar em embalagens; Situação; Detalhe |
| EST | Suprimentos › Estoque | `g_dev` | areas/processo_estoque.py:106 |  | Requisição; O.S.; Item; Lote; Entregue; Consumido; Devolvido; Em custódia; Com quem; Encerramento da O.S.; Detalhe |
| EST | Suprimentos › Estoque | `g_lot` | areas/processo_estoque.py:116 | árvore | Item › lote; Item; Local; Físico; Reservado; Bloqueado; Disponível; Em conferência; Em custódia (fora do depósito); O.S. com custódia; Situação do lot |
| EST | Suprimentos › Estoque | `g_cnt` | areas/processo_estoque.py:122 |  | Contagem; Ajuste; Item; Lote; Local; Sistema na data de corte; Contado; Diferença; Situação; Ação |
| EST | Suprimentos › Estoque | `g_mov` | areas/processo_estoque.py:130 |  | Hora; Registro; Movimento; Condição; Documento; O.S.; Item; Lote; Quantidade; Quem; Origem; Sinal do app |
| OS | Agrícola › Ordem de Serviço | `g_os` | areas/processo_os.py:1220 | árvore | O.S.; Atividade; Talhão; Local; Área (ha); Início; Fim; Fase; Situação; Observação; Quem resolve; Próxima ação; Prazo; Realizado (ha); Saldo (ha); Dis |
| PA | Agrícola › Planos agronômicos | `g_cv` | areas/processo_planos.py:511 |  | Safra; Talhão ou parcela; Cultura e variedade; Área; Versão aplicada; Situação |
| SAF | Agrícola › Planejar safra | `g_saf` | areas/processo_safra.py:27 |  | Safra; Fazenda; Cultivos; Área; Estado; Próximo passo |
| SAF | Agrícola › Planejar safra | `g_op` | areas/processo_safra.py:180 | árvore | Operação › atividade › talhão; Situação; Data; Conjunto; Rendimento; Área trabalhada; Horas-conjunto (h); Custo R$/ha |
| SAF | Agrícola › Planejar safra | `g_dem` | areas/processo_safra.py:221 | árvore | Grupo; Insumo; 1º uso; Necessidade líquida; Falta em; Valor (R$); Situação; Solicitação; A complementar; Demanda bruta; Já realizado; Estoque apto; Us |
| SAF | Agrícola › Planejar safra | `g_cult_{k}` | areas/processo_safra.py:83 | árvore | Talhão ou parcela; Situação; Área livre (ha); Livre a partir de; Área (ha); Cultura; Ocupa até; Fim por; Safra; Variedade; Plano agronômico; Versão; P |
| SAF | Agrícola › Planejar safra | `g_rend_{k}` | areas/processo_safra.py:176 | árvore | Operação; Atividade; Conjunto; Rendimento (ha/h); Custo (R$/h); Custo (R$/ha); Custo R$/kg; Modo; Largura (m); Velocidade (km/h); Eficiência (%); Part |
| SAF | Agrícola › Planejar safra | `g_cap_{k}` | areas/processo_safra.py:194 |  | <cap_cols(CAP_MIS.get(k, list(range(len(meses)))))> |
| PROD | Produção › Estoque de produto | `g_lot` | areas/producao.py:241 | árvore | Lote · produto; Produto; Local · validade; Físico; Bloqueado; Em processo; Apto; Reservado; Disponível; Qualidade · próximo passo |
| PROD | Produção › Estoque de produto | `g_ped` | areas/producao.py:246 |  | Pedido · cliente; Produto; Tipo · janela; Quantidade; Reservado; Falta; Situação · próximo passo |
| CARGA | Produção › Recebimento e beneficiamento | `g_cg` | areas/producao.py:363 |  | Carga · ticket; Cultura; Origem; Colheita · recebimento; Líquido; Comercial; Lote · local; Situação · próximo passo |
| COLH | Produção › Previsão e colheita | `g_tal` | areas/producao.py:493 | árvore | Talhão · variedade; Cultura; Área; Previsão; Colhido; Produtividade; Referência · desvio; Situação · próximo passo |
| COLH | Produção › Previsão e colheita | `g_sem` | areas/producao.py:497 |  | Semana; Produto; Previsão publicada; Colhido; Vendas futuras; Oferta livre; Desvio |
| SU-01 | oculto | `g_nec` | areas/suprimentos.py:269 | árvore | Item · origem; Falta firme; Pedir até · necessária; Demanda; Disponível; Receb. firmes; Próxima ação |
| SU-02 | oculto | `g_pol` | areas/suprimentos.py:310 |  | Item/grupo · depósito; ABC · criticidade; Método; Segurança · prazo; Lote/múltiplo; Validade; Limite econômico; Versão · estado |
| SU-03 | oculto | `g_sal` | areas/suprimentos.py:388 |  | Item · lote; Local; Físico; Retido; Utilizável; Reservado; Disponível; Custódia; Valor |
| SU-03 | oculto | `g_lot` | areas/suprimentos.py:429 |  | Medida; Quantidade; Situação |
| SU-04 | oculto | `g_cot` | areas/suprimentos.py:501 |  | Cotação · origem; Itens; Fornecedores; Respostas; Melhor custo equalizado; Estado |
| SU-04 | oculto | `g_cmp` | areas/suprimentos.py:512 |  | Fornecedor; Mercadoria; Frete; Prazo de entrega; Condição; Custo comparável; Situação |
| SU-05 | oculto | `g_ctr` | areas/suprimentos.py:554 |  | Contraparte · contrato; Item · unidade; Contratado; Tolerância (versão aceita); Preço · condição; Exposição · limite; Estado |
| SU-05 | oculto | `g_ped` | areas/suprimentos.py:565 |  | Pedido · fornecedor; Item; Quantidade; Recebido; A entregar; Chegada prevista; Uso previsto; Depósito; Estado |
| SU-05 | oculto | `g_car` | areas/suprimentos.py:575 |  | Carga · contrato/pedido; Item; Quantidade; Chegada; Uso previsto (cobertura); Depósito; Exposição projetada; Estado |
| SU-05 | oculto | `g_itm` | areas/suprimentos.py:578 |  | Item; Contratado; Recebido; Liberado pendente; Proposto; Estado |
| SU-05 | oculto | `g_dep` | areas/suprimentos.py:582 |  | Depósito; Capacidade; Ocupação na chegada; Exposição projetada; Limite; Estado |
| SU-05 | oculto | `g_mes` | areas/suprimentos.py:586 |  | Mês; Cargas; Quantidade; Exposição de pico; Estado |
| SU-05 | oculto | `g_sal` | areas/suprimentos.py:636 |  | Medida; Valor; Fonte |
| SU-05 | oculto | `g_lib` | areas/suprimentos.py:640 |  | Liberação · carga; Quantidade; Chegada prevista; Cobertura atendida; Exposição projetada; Estado |
| SU-06 | oculto | `g_rec` | areas/suprimentos.py:705 |  | Documento · pedido; Item · lote; Conferido; Apto · retido; Inspeção · divergência; Físico · título · ação |
| SU-07 | oculto | `g_req` | areas/suprimentos.py:818 |  | Requisição · O.S.; Item · lote; Solicitado; Entregue; Consumido; Em custódia; Estado · próxima ação |
| SU-07 | oculto | `g_bal` | areas/suprimentos.py:892 |  | Medida; Quantidade; Situação |
| SU-08 | oculto | `g_mov` | areas/suprimentos.py:974 |  | Documento · data; Movimento · motivo; Origem → destino; Item · lote; Quantidade; Estado |
| SU-09 | oculto | `g_inv` | areas/suprimentos.py:1053 |  | Inventário · escopo; Corte · contador; Observado × sistema · recontagem; Diferença · causa; Estado · ação |

_243 grades com id (AST de areas/*.py; cadastros.py:303–809 não entram porque cad_*.py os substitui)._
