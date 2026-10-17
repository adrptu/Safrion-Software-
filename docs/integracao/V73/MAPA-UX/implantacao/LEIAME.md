# MAPA-UX · Implantação MUX-F0, MUX-F1 e MUX-F2 no protótipo (17/10/2026)

Pedido do proprietário de 16/10/2026: "Mapa da fazenda com UX e UI de excelência — passar o mouse e entender, clicar e detalhar, sem perder o contexto" (`651f047:docs/integracao/V73/MAPA-UX/pedido.md`). Em 17/10 ele cobrou: "as melhorias de design, ux e ui, hover, etc dentro do mapa também nao mudaram nada. ja foi pedido."

As decisões técnicas são dos agentes. O Claude implantou sem esperar a MAPA-FROTA F1, o SHA do Codex e o G2 do Gemini, que o confronto punha como portão. O Codex revisa depois. Estado: **executado** no protótipo (`tools/prototipo/v37/gen37`, aqui `G`), com os testes da §4.

```text
ID / resultado útil / persona: MUX-F0+F1+F2 · no IN-04, passar o mouse (ou focar) mostra o essencial do talhão; clicar abre o detalhe ao lado sem perder o lugar; teclado, busca e lista acham qualquer talhão; a cor não mente; a legenda filtra / gestor e agrônomo no computador (mouse, teclado, leitor de tela); operador que chega pelo aviso de carência a 390 px
Requisitos do PRD e fora do escopo: pedido §1, §4 e §5; confronto §7 (MUX-F2) e §8.2 (MUX-F0 e MUX-F1, com Δ2); D1, D2, D3, D6, D7, D8, D13 (hachura), D14, D16, D17, D18, D20 (foco e Esc), D23 (parte), D24, D25, D27 (no IN-04), NC1, NC2, NC4, NC8, NC10, NC11; 74.5.24–26, MAPUX-06, RF-WRK-004, SEL-02, BOT-01/08, VIS-01..04. Fora: MUX-F3, MUX-F4, motor único e embalagem (D26), paleta G1, D9/D10, N2 nas ações antigas (§6 e §7)
Autor / revisor / integrador: Claude / Codex / Codex (regime leve, AGENTS §3.5)
Base / arquivos sob responsabilidade: 0b3d0d4 (composição de 17/10), branch claude/v44-v73-mapa-ux-f1 / G/areas/inicio.py (IN-04); G/talmapa.js (só o #talhao=); testes novos G/mapa_mux_*.py, G/mapa_mux_unit.js e G/mapa_insfaz_unit.js; o jeito de achar o talhão em 10 testes do mapa; G/links_ocultos_test.py (par IN-04 → AG-06); docs/design-system/padroes-1710.md; esta pasta
Aceite e comando de verificação: §4 (comandos e resultados exatos); contraprova no render da base 0b3d0d4
Estado / impedimento / próximo passo: entregue para a revisão do Codex; portões abertos na §6; próximas fatias na §7
```

## 1. O que o proprietário vê e testa (IN-04, Lagoa Grande, a fazenda padrão)

1. Passe o mouse num pivô.
   - O contorno realça, o cursor vira mão e aparece o cartão: número e área, cultura e estádio, valor da camada, estado em texto, data do dado, comparação curta, O.S. em andamento e "Clique para detalhar".
   - O cartão abre na hora, sem cobrir o pivô, e some ao sair.
2. Clique no pivô. O painel abre ao lado, com "Abrir talhão ›". Clique de novo, no × ou no fundo do mapa, ou aperte Esc, para fechar.
3. Teclado:
   - Tab entra no mapa, e as setas andam entre pivôs vizinhos, com o mesmo cartão.
   - Enter abre o painel com o foco no título; Esc fecha e volta ao pivô.
   - "/" abre "Ir para talhão": digite "P5" e aperte Enter.
4. "Lista" (ao lado da busca) mostra os talhões do mais grave ao melhor, com o mesmo painel; "Localizar no mapa" volta ao mapa.
5. Clique numa classe da legenda (ex.: "foco · 2 · 137 ha"): só ela fica no mapa e na Lista; clique de novo para limpar.
6. Recarregue a página: o endereço (`#faz=LG&lay=…&t=…`) devolve a camada, a data e o pivô escolhido.
7. No celular, toque num pivô: o painel abre embaixo e a tela rola até o título.

## 2. O que foi implantado, por item

Peça: bloco MUX em `G/areas/inicio.py`. As funções puras ficam entre `// <mux-puro>` e `// </mux-puro>` (`muxVizinho`, `muxRank`, `muxOrdem`, `muxHashLer`, `muxHashEscrever`, `muxAcha`). O resto são funções `mux*`: cartão, realce, teclado, lista e endereço. Tudo opera sobre os botões `[data-talhao]` dentro de `[data-mux-grupo]`, para o SAF-MAPA extrair depois. Nada mudou em `engine.py`, `g2lib.js`, `alocacao.py`, `frota.js`, `cad_fazendas.py`, `processo_os.py`, no cabeçalho ou em `ds_modulos.py`.

### 2.1 MUX-F0 · destinos, nomes e ícone (§8.2)

| # | Aceite | Implantado |
|---|---|---|
| 1 | "Nova O.S. neste talhão" e "Abrir ordens" com talhão escolhido levam `#tal=Fazenda\|Talhão` | `muxOsTal`; a O.S. abre com "Filtrar por talhão = Santa Rita\|T4" (D8) |
| 2 | `#talhao=PV05` troca a fazenda; `#talhao=PV99` avisa e não escolhe | `talmapa.js` (tmVals): fazenda do talhão, aviso `role=status` no mapa e no aviso do rodapé (D18) |
| 3 | Satélite sem AG-06 | Saíram o "Ver histórico" da faixa e o "Ver histórico do talhão" do painel (D7). O par sai do `links_ocultos_test.py` (regra L2b) |
| 4 | Solo e Colheita › Situação com link de módulo | "Abrir Previsão e colheita ›" (COLH) na faixa (D24). **Solo, ajustado:** na faixa, o link cortava os números a 1440, contra o pedido do proprietário de 16/10 (MAP-04, `mapa_faixa_test` F3). O AG-02 fica no painel do talhão ("Abrir <laudo>") e no ícone de registrar laudo |
| 5 | Ações de Colheita com o ícone da barra | `'Colheita'` no `ICN` (cliente) e no `ICS` (Python), o mesmo desenho do `engine.ICONS` (D25) |
| 6 | Um nome só por pivô no IN-04 | "P5" no marcador, no título do painel, no nome acessível, nas linhas do Estádio, na área selecionada e no Medir. "PV05" e "Pivô 5" ficam como apelidos na busca (D27) |

### 2.2 MUX-F1 · achar e abrir o talhão (§8.2)

| # | Aceite | Implantado |
|---|---|---|
| 1 | Grupo com nome; uma parada de Tab; setas; Home/End; Enter com foco no título; Esc devolve o foco; o Tab seguinte sai | Santa Rita: SVG `role=group`. Lagoa Grande: o contêiner do MapLibre vira o grupo; cada pivô é um `<button>` (o canvas sai do Tab e do leitor, N3). Tabindex móvel; vizinho pela direção (`muxVizinho`); Home/End pelo nome |
| 2 | Instruções visíveis e no `aria-describedby` | `#mux-instr` na legenda ("Setas: vizinho · Enter: abrir · Esc: fechar · /: buscar"); some só em tela de toque |
| 3 | `role=button`, `aria-pressed`, nome completo | `aria-pressed` nos 31 talhões; nome "P5, 71 ha, cultura e estádio, valor, estado, data" (NC8). O rótulo da camada continua em `data-rotulo` |
| 4 | "/" e busca; enquadra só na busca | Busca "Ir para talhão" com sugestões (datalist) e `aria-keyshortcuts="/"`. O "/" só vale com o foco no bloco do mapa (WCAG 2.1.4). Enter escolhe, abre e põe o foco no título; na Lagoa Grande, enquadra o pivô. A câmera só se move por pedido: busca, "Localizar no mapa" e o foco num pivô fora da vista (2.4.11) |
| 5 | "Ver dados" Lista \| Mapa | Visão Lista no mesmo bloco: mapa montado e oculto; mesmos filtros, seleção e painel; ordem SEV; "N de M"; "Localizar no mapa" |
| 6 | "Todas" | Lista com as três fazendas (Santa Rita, Lagoa Grande, Boa Vista sem geometria); o mapa mostra a Santa Rita e avisa onde estão as outras |
| 7 | Esc por nível; rascunho; clique no fundo | Esc fecha o cartão, depois o modo (Medir, Programar vistoria, Selecionar), depois a seleção, devolvendo o foco. Não age em campo, menu de alvos, desenho ou importação. Clique ou toque no fundo desmarca (D16) |
| 8 | Endereço e volta sem reenquadrar | `#faz=&lay=&t=&dt=` por `replaceState`; lido na carga e no `hashchange`; manda sobre o contexto da sessão. A câmera da Lagoa Grande fica na sessão (`mapa-cam`) e volta sem reenquadrar |
| 9 | Leitor de tela real | **Portão aberto** (§6) |
| 10 | Sem o CDN | O aviso diz que a Lista continua e oferece "Tentar de novo", sem recarregar. Antes, a página tentava de novo a cada desenho |

### 2.3 MUX-F2 · ler o talhão

- **Cartão (MUX-P1):** `#mux-cartao` (`role=tooltip`), claro como o do Raio-X.
  - Mostra número e área, cultura e estádio, valor da camada, estado em texto, data do dado (cena, vistoria, coleta, balanço ou "hoje"), comparação curta (variação do índice desde a cena anterior; "1,2× o NC"), O.S. em andamento e "Clique para detalhar".
  - Abre sem espera programada, no hover e no foco de teclado (`:focus-visible`), com o mesmo conteúdo.
  - Posição: ao lado, abaixo ou acima, nunca sobre o talhão, dentro da área do mapa e da janela.
  - Some 120 ms depois de sair do talhão e do cartão; Esc dispensa (1.4.13). Sem ação dentro; não abre no toque.
- **Realce:** anel em duas cores por cima dos pixels (D3): contínuo no hover, tracejado no foco. Na Lagoa Grande, as camadas `pv-hov`/`pv-hov2`; cursor de mão.
- **Cor honesta (MUX-P3):**
  - nuvem e sem leitura em hachura, também no mapa real (`pv-hach`, D13);
  - "estimado" na cor do valor, com "≈ … estimado" (NC10), também na legenda da Irrigação;
  - "não se aplica" com contorno tracejado (D14).
- **Rótulos (MUX-P4):**
  - número / valor / estado curto (sem repetir o que o valor já diz), sobre placa branca a 90 % com texto `#15201A`;
  - Lagoa Grande: só o número abaixo de 64 px de diâmetro na tela, e número e valor abaixo de 110 px;
  - Santa Rita: só o número com o SVG abaixo de 600 px;
  - seleção forte (7 px escuro + linha branca) e número em destaque (invertido);
  - o mapa não muda de zoom no clique.
- **Legenda que trabalha (MUX-P5):** cada classe é um botão com contagem e área; o hover e o foco realçam; o clique filtra o mapa (os outros esmaecem) e a Lista; o segundo clique, ou "Limpar filtro", limpa. O contêiner não pega o clique entre os itens (parte do D23).
  - Escala relativa não conta talhões: no Satélite com contraste Talhão e no Solo fora do Absoluto, a escala é dos pixels de cada talhão (ou da fazenda), e a cor do talhão não é uma classe dela. Antes da correção, a Lagoa Grande mostrava "Médio 20 · 1.137 ha" com rótulos fraco, atenção e bom. Sem cultura, sem laudo e nuvem continuam contando (L1e e L1f).
- **Celular:** o toque no pivô da Lagoa Grande escolhe e abre o painel embaixo, e a tela rola até o título. O MapLibre não gerava "click" do toque no canvas, e o clique de compatibilidade é suprimido. Sem cartão no toque.
- **Design system:** nenhuma primária nova (Mapa \| Lista e a busca mudam a visão; "Abrir talhão ›" e "Localizar no mapa" são navegação, BOT-08); hover verde do motor nos botões novos (VIS-02); seta de ir da TAB-11 na linha da Lista (SEL-02); dica do motor no "Localizar no mapa" (VIS-04). Padrões registrados em `docs/design-system/padroes-1710.md` (MUX-P1 a P7).

### 2.4 CTL-4 S3: Mapa › Insumos ignora a dose atual (achado do Codex 6232261452)

- **Corrigido:** a chave do cache `insFaz._k` passa a levar `X.occ` (ocorrências do plano: dose, área e produtos). Uma dose nova, com as mesmas O.S. e o mesmo estoque, refaz a conta.
- **Teste:** `G/mapa_insfaz_unit.js` (4 casos; contraprova na base: o C2 reprova, §4).
- **Conferido e ainda aberto (S3, não corrigido aqui):**
  - a dose que o Mapa usa vem de `M.dem.faz`, fixado no build (`dados2.dem_fixas`), e não de uma fonte viva;
  - os aceites da análise de solo (`c.solo.aceites`, a única dose viva no cenário) e os ajustes do Planejar safra não entram;
  - a Compra, o SU-03det e o MB-05 usam a mesma parte fixa (`dados2.dem_fixas`, `DEMV.x`); o Planejar safra aplica os aceites (`soloAtividades`).
  - Corrigir exige uma função comum de "ocorrências vivas" (`soloAtividades` + plano) usada pelas três telas e pela Compra. Gatilho: a próxima fatia do CTL-4 ou do SOLO.

## 3. Medidas antes → depois (executado)

Mesmos testes no render da base 0b3d0d4 (montado do checkout limpo, antes de qualquer mudança) e no render desta entrega. Chrome headless com SwiftShader; os tempos são indicativos.

| Medida | Antes (0b3d0d4) | Depois | Fonte |
|---|---|---|---|
| "Nova O.S. neste talhão" e "Abrir ordens" com o T4 escolhido | `OS.dc.html`, sem o talhão (4 de 4, a 1440 e a 390) | `OS.dc.html#tal=Santa%20Rita%7CT4` (0 de 4 sem contexto) | F0 `MEDIDAS` |
| Links do Satélite para o AG-06 | 2 | 0 | F0 |
| Ações de Colheita sem ícone | 8 de 8 | 0 de 8 | F0 |
| Nomes do mesmo pivô | "Pivô 5" no painel e "P5" no marcador | "P5" | F0 |
| Paradas de Tab no mapa da Santa Rita | 8 | 1 | F1 `MEDIDAS` |
| Talhões alcançados só com as setas | 0 de 8 (SR) e 0 de 23 (LG) | 8 de 8 e 23 de 23 | F1 |
| Pivôs da Lagoa Grande alcançáveis sem mouse | 0 de 23 (o canvas era 1 parada, sem pivô) | 23 de 23 | F1 |
| `aria-pressed` nos talhões | 0 | 31 (8 + 23) | F1 |
| Endereço depois de escolher o P5 no Satélite, cena 25/09 | vazio | `#faz=LG&lay=sat&t=PV05&dt=25-09` | F1-8a |
| Lista dos talhões | não existia | 8 (SR) e 23 (LG) linhas, da pior para a melhor | F1-5 |
| Cartão no hover e no foco | 0 de 9 camadas | 9 de 9 | F2 C1–C5 |
| Tempo do evento ao cartão (hover entre vizinhos) | — | do evento ao quadro: p50 52,4 ms · p95 292,7 ms; trabalho do cartão (JS): p50 14,8 ms · p95 34 ms (24 hovers em f37d71ce; SwiftShader, máquina dividida com outros agentes). O quadro inclui a pintura do mapa e pesa com a carga; não prova a meta de p95 < 100 ms | F2 C2b |
| Contraste mínimo do texto do rótulo | texto direto sobre a cor do talhão, sem placa (K2 reprova) | 13,36:1 (Santa Rita e Lagoa Grande) | F2 K2 |
| Legenda a 390 px (altura sobre o mapa) | — | 34 px numa linha que rola (com a contagem e quebrando em linhas, eram 157 px) | sonda de leiaute |

## 4. Testes (executado em 17/10/2026)

Comandos de `G`, com `env CHROME_BIN=… CDP_GL=1 SAFRION_DADOS=sintetico RENDER_DIR=<render>`, um navegador por vez. Versão composta: **f37d71ce** = composição ac5cd1d7 (v125) + esta frente, sem conflito. Render montado desse commit (`python3 -W error::SyntaxWarning -B build.py && python3 -B montar_render.py`, 156 páginas, 0 FALHA no build). Brutos em `brutos/`.

### 4.1 Novos

| Teste | Esta entrega | Contraprova (render ou fonte da base 0b3d0d4) |
|---|---|---|
| `mapa_mux_f0_test.py` | 17 ok · 0 falhas | 3 ok · 14 falhas. Passam F0-1b (a O.S. já lia o `#tal=`) e F0-7 (sem erro de JavaScript, nas duas larguras) |
| `mapa_mux_f1_test.py` (1440 e 390) | 48 ok · 0 falhas | 6 ok · 42 falhas. Passam os itens de não regressão: o Tab seguinte sai do mapa (F1-1g, duas fazendas), Enter e Esc não mexem na câmera (F1-4d), Esc não apaga o rascunho (F1-7c) e nenhum erro de JavaScript (F1-12a/b) |
| `mapa_mux_f2_test.py` | 29 ok · 0 falhas | 4 ok · 25 falhas. Passam C4c (sem cartão, nada fica aberto), K1a (a hachura da nuvem na Santa Rita já existia) e E1a/b (sem erro de JavaScript); L1e e L1f reprovam |
| `node mapa_mux_unit.js` (funções puras: vizinho, ordem, endereço, busca) | 28 ok · 0 falhas | 0 ok · 1 falha: o bloco `<mux-puro>` não existe |
| `node mapa_insfaz_unit.js` (CTL-4 S3) | 4 ok · 0 falhas | 3 ok · 1 falha: C2 dá 10 em vez de 20 (o cache segura a dose antiga) |

### 4.2 Existentes

Todos no render de f37d71ce (`brutos/bateria_f37d71ce.txt`), na ordem em que rodaram. O job parou no limite de 2 h durante o `seta_padrao_test`; ele, o `credito_menu_test` e o `dose_divergente nav` rodaram de novo na segunda parte do mesmo arquivo.

| Teste | Resultado | Classificação do vermelho |
|---|---|---|
| `mapa_filtros_test` | 7/7 | |
| `solo_mapa_calor_test` | 9/9 | |
| `colheita_mapa_test` | 7 ok · 0 falhas | |
| `map_trilha_icones_test` | 9 ok · 0 falhas | |
| `mapa_solo_texto_test` | 9 ok · 0 falhas | |
| `mapa9_test` | 13 ok · 0 falhas | |
| `mapa_faixa_test` | 25/25 | |
| `mapa_cancel_test` | 6/6 | |
| `map_aprov_test` | 4 ok · 1 falha (2: OS-0418 na tela O.S.) | Pré-existente: reprova igual no render da base 0b3d0d4 (`brutos/classificacao_base.txt`) |
| `map_decisoes_test` | 18 ok · 0 falhas | |
| `map_irrig_filtro_test` | 14 ok · 1 falha (15: contagens da tela O.S.) | Pré-existente: reprova igual na base 0b3d0d4 |
| `mip_correcoes_test` | 14/14 | |
| `carencia_test` | 90/90 | |
| `talmapa_test` | 8/8 | |
| `filtros_cultura_test` | 10 ok · 0 falhas | |
| `componentes_test` | 3 ok · 0 falhas | |
| `acao_unica_test` | 10 ok · 0 falhas | |
| `assinatura_test` | 45 ok · 0 falhas | |
| `credito_menu_test` | 26/26 | Falha da ferramenta, corrigida: "Inspected target navigated or closed" ao avaliar durante a troca de página (três vezes sob carga; 26/26 nas repetições, inclusive na base 0b3d0d4). A espera passou a tolerar a navegação (ba3f51f0), sem mudar limite nem asserção |
| `demanda_estado_nav_test` | 14 ok · 0 falhas | |
| `demanda_unica_nav_test` | 19 ok · 10 falhas (totais da demanda) | Pré-existente na composição: reprova igual, os mesmos 10 itens, na base ac5cd1d7 (teste e render da base). A SU-01 pôs a necessidade da OM na demanda (R$ 428.483,50 · 15 insumos, em vez de R$ 428.305,00 · 14), e o oráculo guarda os números antigos. O Mapa › Insumos acompanha a mesma conta. Antes do merge, a frente passava 29/29 |
| `ds_test` | 72/72 | |
| `est_laudo_lote_nav_test` | 7 ok · 0 falhas | |
| `irr_fluxo_test` | 34 ok · 0 falhas | |
| `mip_fluxo_test` | 15/15 | |
| `producao_fluxo_test` | 92/93 (AC-h Mapa) | Pré-existente e de propósito: o teste reprova sempre que a camada Colheita e produtividade está na barra ("falta ligar ao conversor (P5)"), o que vale desde a DEC-0910-36, antes da base |
| `regras_toque_test` | 5 ok · 0 falhas | |
| `solo_rev_test` | 22/22 | |
| `ma_atrito_test` | 13/13 | |
| `saf_capacidade_simetrica_test` | 38 ok · 0 falhas | |
| `nav_modulos_test` | 14 ok · 1 falha (N2: cartões do Crédito) | Pré-existente: reprova igual na base 0b3d0d4 (Crédito, CRE F2) |
| `paginas_scan_test` | 5 ok · 0 falhas (148 páginas) | |
| `seta_padrao_test` | 14 ok · 0 falhas | Numa rodada anterior (14074537, antes do merge) o D1440 reprovou no CD-01det, tela de outra frente; não se repetiu na composição |
| `dose_divergente_test.py nav` | 7/16 · 9 falhas (lista e painel da O.S.) | Pré-existente: reprova igual, item a item, na base ac5cd1d7 (teste e render da base). O modo `unit`, que cobre o Início (IN-04), passa: 35/35 e 2/2 |

Sem navegador (`brutos/sem_navegador_f37d71ce.txt`): `links_ocultos_test.py` 16 · falhas 0; `ds_inventario.py --catraca` "catraca ok"; `node mapa_os_unit.js` 7 · OK 7; `dose_divergente_test.py unit` 35/35 e Início 2/2.

### 4.3 Oráculos mudados, e por quê

- **Quinze testes** acham o talhão por `data-talhao` e `data-rotulo`, e não mais pelo texto do desenho antigo: `mapa9_test`, `mapa_filtros_test`, `solo_mapa_calor_test`, `colheita_mapa_test`, `map_decisoes_test`, `map_aprov_test`, `mapa_cancel_test`, `map_irrig_filtro_test`, `mip_correcoes_test` e `mapa_solo_texto_test`; na bateria final, também `demanda_estado_nav_test`, `demanda_unica_nav_test`, `est_laudo_lote_nav_test`, `irr_fluxo_test` e `mip_fluxo_test` (eles procuravam o aria-label "T4: …", que agora é o nome completo "T4, 204 ha, …").
  - Cada mudança tem o comentário "MUX-F1 (17/10/2026): … oráculo obsoleto na forma de achar; a asserção não muda".
  - Nenhuma asserção ficou mais fraca.
- **`links_ocultos_test.py`:** sai o par IN-04 → AG-06 da lista RESIDUAL. O link saiu de propósito (D7), e a regra L2b pede que a lista só tenha links que existem.
- **Vermelhos da bateria final, classificados:**
  - **Defeito do produto, corrigido:** `mapa_faixa_test` F3 (Lagoa Grande e Santa Rita, 1440). O link "Abrir Análises de solo ›" que esta entrega pôs na faixa do Solo cortava os números. O link saiu da faixa (§2.1, item 4), e o F0-4 passou a conferir os números inteiros.
  - **Oráculo obsoleto pelo D27 (um nome só por pivô):** `mapa9_test` N5 e `carencia_test` ("link #car:PV23…") procuravam "Pivô 23" no painel, que agora abre com "P23 · 64 ha". Passam a exigir que o painel comece por "P23 · ".
  - **Defeito do produto, corrigido:** `map_irrig_filtro_test` 10. O aviso novo de "Todas" tinha perdido a frase "Boa Vista sem geometria", que o teste trava. Texto atual: "Santa Rita no mapa · Lagoa Grande na Lista · Boa Vista sem geometria".
  - **Oráculo obsoleto pelo D8:** `map_decisoes_test` 4 esperava "Nova O.S. neste talhão" → `OS.dc.html`; agora exige `OS.dc.html#tal=Santa%20Rita%7CT1` (mais estrito).
  - **Oráculo obsoleto pela MUX-F1, item 8 (endereço é estado):** `carencia_test` ("Ver carência abre a camada…" e "link #car vindo da CO-06…") exigia `location.hash` vazio, ou seja, o comando `#car` consumido. Agora o endereço guarda o estado. A asserção passa a exigir que nenhum comando `#car` sobre e que o estado traga a camada e o talhão (`lay=colheita&t=PV23`; `faz=SR&t=T7`). Não ficou mais fraca.
  - **Falha da ferramenta, corrigida:** `credito_menu_test` (ver §4.2).
  - **Pré-existentes, fora do Mapa, não bloqueiam:** `map_aprov_test` 2 e `map_irrig_filtro_test` 15 (tela O.S.), `nav_modulos_test` N2 (Crédito), `producao_fluxo_test` AC-h (de propósito), `dose_divergente_test.py nav` (O.S.) e `demanda_unica_nav_test` (§4.2). Cada um reprova igual na base indicada; os brutos estão em `brutos/classificacao_base.txt`.

## 5. Decisões de implantação (técnicas, dos agentes)

- **Cartão imperativo, fora do React:** o `setState` do protótipo custa de 79 a 295 ms por desenho, o que estoura o limite de 100 ms.
  - O cartão é um elemento único, atualizado direto no DOM.
  - O estado da página só muda no clique.
- **O MapLibre não gera clique a partir do toque no canvas:** o toque é tratado à parte (`touchstart`/`touchend`, `queryRenderedFeatures`), e o clique de compatibilidade é suprimido por 800 ms.
- **Sem o CDN, nenhuma nova tentativa automática:** antes, cada desenho da página criava outro `<script>` do MapLibre. Agora só o botão "Tentar de novo" tenta de novo.
- **A Lista é peça própria**, registrada como exceção no MUX-P6: o motor de grade é estático, e as linhas mudam a cada camada. Migra no SAF-MAPA.
- **Nada mudou no `engine.py` nem no `g2lib.js`.** Os ícones de Colheita entraram nos mapas locais `ICN` e `ICS` do `inicio.py`.

## 6. Portões abertos

- **F1 item 9, leitor de tela real (NVDA ou VoiceOver):** não executado.
  - Os testes conferem papel, nome, `aria-pressed`, `aria-describedby` e foco, mas não o que o leitor anuncia.
  - Precisa de uma pessoa com o leitor.
- **Tempo do cartão no aparelho de referência:** só medido no Chrome headless com SwiftShader. Nas rodadas de 17/10, com a máquina dividida com outros agentes, o p95 do evento ao quadro variou de 114,5 a 292,7 ms, acima da meta de 100 ms. O trabalho do próprio cartão ficou em p95 de 20,8 a 34 ms; o resto é a pintura. Medir num computador comum, sem carga, antes de dar a meta por cumprida.
- **Gemini G1 (paleta) e G2 (teclado e leitor de tela):** não consultados. A paleta das classes não mudou; quando o G1 vier, mudam os tokens.
- **Revisão do Codex:** pendente, pela branch e pelo artefato, no regime leve (AGENTS §3.5).
- **Ordem do confronto:** a MAPA-FROTA F1, o SHA do Codex e o G2 eram portões antes desta fatia. A implantação veio antes por causa da cobrança do proprietário de 17/10. Se a MAPA-FROTA mexer no `inicio.py`, a composição confere o delta.

## 7. Fora desta entrega, e por quê

- **Itens da MUX-F2 do confronto que não entraram:**
  - **D9:** no Satélite, Absoluto ou Fazenda como padrão e Talhão só com talhão escolhido. Muda o padrão e os nomes das classes que os testes do Satélite usam; ficou para a fatia com o G1. Parte entrou: no contraste Talhão, a legenda não conta mais talhões pela escala relativa (L1e).
  - **D10:** tirar "10 m" do pixel.
  - **D15:** cores por significado (depende do G1).
  - **Painel na escala do mapa.**
  - **N2 e BOT-08 nas ações antigas das camadas:** o `map_decisoes_test` (CTL-1) exige "Acompanhar OM-0233" como primário. Mudar exige acordo sobre esse oráculo.
  - **N5:** prioridade e motivo estáveis no Integrado.
  - **Escalas comparáveis em Custos e Colheita.**
  - **forced-colors (NC6).**
- **MUX-F3 (mexer no mapa sem perder o lugar):** painel por cima do mapa, folha inferior, controles de 48 px a 390, pan no SVG, "Ajustar à fazenda", tela cheia, gestos, Medir e seleção múltipla. Hoje, a 1440, a primeira fileira de pivôs fica sob a barra de ferramentas. Isso já acontecia na base: o zoom mínimo é o que cobre a imagem.
- **MUX-F4:** o mesmo mapa no CD-01, CD-01det, PL-06, CA-01 e AG-01det, com o SAF-MAPA. Esses arquivos são de outras frentes.
- **Motor único e embalagem do MapLibre (D26):** decisão posterior, com gatilho.
- **CTL-4, dose viva no Mapa › Insumos:** §2.4.
- **`docs/STATUS.md`:** não atualizado aqui; fica para quem integra a versão.

## 8. Capturas

Em `capturas/`, geradas por `capturas.py` (de `G`: `python3 -B <caminho>/capturas.py <render> antes|depois <pasta>`). Lagoa Grande, a fazenda padrão.

| Largura | Antes (0b3d0d4) | Depois |
|---|---|---|
| 1440 | `antes_1440_integrado`, `_satelite`, `_pragas`, `_hover_pragas` (sem cartão), `_painel_pragas` | as mesmas, mais `depois_1440_lista_pragas` (Lista) e `depois_1440_foco_teclado` (cartão no foco, anel tracejado) |
| 390 | `antes_390_integrado`, `_satelite`, `_pragas`, `_toque_painel` | as mesmas; no toque, o painel abre embaixo, com o título à vista |
