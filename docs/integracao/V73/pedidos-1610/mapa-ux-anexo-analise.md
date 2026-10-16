# Safrion · Inventário de UX dos mapas e talhões (protótipo v3)

Análise estática do código em `scratchpad/v3/` (somente leitura, sem navegador). Linhas citadas são linhas físicas do arquivo. Os templates são linhas únicas enormes:

- `IN-04.dc.html:20`: CSS global, com hover, foco e alvos de toque.
- `IN-04.dc.html:48`: template principal do Mapa (barra de camadas, SVG, ferramentas, zoom, legenda e painel).
- `IN-04.dc.html:52`: CSS por container (responsivo) e diálogo "Tela cheia".
- `IN-04.dc.html:53`: aviso (toast).
- `IN-04.dc.html` a partir de 7212: lógica do mapa.

`support.js` é React mais o runtime e não tem lógica de mapa.

O que só se confirma no navegador está marcado como **[confirmar no navegador]**.

---

## 0. Telas que desenham mapa ou forma de talhão

| Tela | Título | O que desenha | Técnica | Interação |
|---|---|---|---|---|
| **IN-04** | Mapa da fazenda | Santa Rita: talhões esquemáticos. Lagoa Grande: 23 pivôs com imagem e pixels. Boa Vista: estado vazio | SVG (Santa Rita) e MapLibre GL 5.9.0 com canvas (Lagoa Grande) | Clique, seleção, painel e 9 camadas |
| **CD-01** | Fazendas, áreas e talhões | Visão "Mapa" na aba Talhões: Santa Rita esquemática; Lagoa Grande com círculos projetados dos centros do KML | SVG estático (`viewBox 0 0 1000 460` e `1000 681`, l.48) | Clique abre o **formulário de edição** do talhão. Sem teclado |
| **CD-01det** | Talhão | "Polígono do talhão" ou "Divisão da safra" com faixas de parcela proporcionais à área | `div` com `clip-path` fixo (l.48; `geoVals` 2660-2670) | Nenhuma. Links "Ver no mapa ›", "Desenhar no mapa ›" e "Importar" para o IN-04 (2723-2724) |
| **PL-06** | Parcelas e escalonamento | T1 dividido em T1-A e T1-B, proposta | SVG estático `700×300` (l.48) | Nenhuma |
| **CA-01** | Ordens de campo | Visão "Mapa" (Lista, Kanban ou Mapa): retângulos e círculos por talhão com a O.S. | SVG estático `1180×190`, textos fixos no HTML (l.48) | Nenhuma |
| **AG-01det** | Rota e evidências | "Rota em W" dos pontos da vistoria sobre um retângulo | SVG mais `span` posicionados (l.48; 5422-5425) | `title` por ponto (dica no hover). Sem foco |
| **MB-\*** | App de campo | **Nenhum mapa.** MB-06 (Vistoria por pontos) mostra GPS só como texto e uma caixa "GPS fora da tolerância" (l.26; dados l.2329) | Não se aplica | Não se aplica |

**Links que entram no mapa:**

- `#car:<talhão>` ("Ver restrição/pendência no mapa"): OS, CO-06, COLH, BEN, CARGA, EXPED, IC, IV, PAGR, PCOM, PROD, VE-04, VEN e MB-01..10.
- `#talhao=`, `#desenhar=` e `#importar`: CD-01det.
- `IN-04.dc.html` sem parâmetro: ON-01.

**Contexto compartilhado:** a fazenda escolhida circula por `sessionStorage['mapa-ctx']` entre IN-04, AG-01, AG-01det, AG-03, AG-04, IR-01..04 e IR-03det (ex.: `AG-01:5398-5401`, `IR-01:5885-5892`).

---

## 1. IN-04 · Mapa da fazenda

### 1.1 Renderização

**Fazenda ativa.** O filtro do topo "Fazenda" (Todas, Lagoa Grande, Santa Rita, Boa Vista; l.48) define a fazenda. O padrão é Lagoa Grande (`7797`). A regra é `FAZ = (mf_faz==='Lagoa Grande') ? 'Lagoa Grande' : 'Santa Rita'` (`7797`):

- **Todas** mostra só a Santa Rita, mais o aviso "Boa Vista sem geometria" (`7884`, l.48).
- **Boa Vista** mostra o estado vazio "Nenhum talhão desenhado" com "Cadastrar talhões" (CD-01).

**Santa Rita: esquemático em SVG** (l.48, `<svg viewBox="0 0 1000 620" preserveAspectRatio="xMidYMid meet" role="img">`)

- **Geometria:** 6 quadriláteros desenhados à mão (T1, T2, T4, T3, T7, C1) e 2 círculos (P1 e P2), em coordenadas fixas (`M.geoc`). Não é geometria real. A legenda diz "Demonstrativo" (`leg_nota`, 7890).
- **Fundo:** sem imagem. Usa o padrão `#grade` (40 un), dois traços brancos como estradas e a cor `#E3EADB` (l.48).
- **Preenchimento:** `fill={{fl_T}}` com `fill-opacity` 0,88 (classe) ou 1 (sem dado, nuvem, satélite) (`7835`).
- **Contorno:** branco, 4 un. Quando selecionado, `#15201A` com 6 un (`7836`).
- **Pixels:** em Satélite e Solo, um grupo `clip-path` com quadrados de 16 un (`M.cs=16`) desenha os "pixels" por cima do polígono (`pxo_T`, `px_T_i`; l.48; `7845-7852`). Os pontos de solo são círculos de r=3,4 un (`solo_pts`).
- **Pivôs:** desenham um "braço" (linha do centro à borda) na cor do contorno (l.48).
- **Mancha:** só T7 tem um círculo tracejado e um chip "mancha X ha", em posição fixa `cx=650 cy=556` (l.48; `7833`, `7837`).
- **Rótulos (três, todos `pointer-events:none`):**
  - Nome: `<text>` com `font-size=40`, Sora 700, halo branco de 6 un.
  - Sub: `foreignObject` de 20 un de altura, 13 px, opacidade 0,85. Mostra "Cultura · ha" (`sub_T`).
  - Rótulo da camada: `foreignObject` de 46 un de altura, 15 px, peso 800, com `text-shadow` branco (`lab_T = c.l`).
  - Todos escalam junto com o SVG (ver D12).

**Lagoa Grande: MapLibre GL com dados sintéticos** (`7311-7333`)

- **Carregamento:** a biblioteca vem em tempo de execução do CDN `cdn.jsdelivr.net/npm/maplibre-gl@5.9.0` (`7264`), sem a folha de estilo oficial: só um CSS mínimo próprio (`7257-7262`).
- **Imagem de fundo:** fonte `image` com `lagoa_rgb_YYYYMMDD.png`, trocada conforme a cena (`7320`; `lgSync` 7334-7336).
- **Pixels do índice e do solo:** fonte `canvas` de 820×560 px, cerca de 10 m por pixel, com `raster-resampling: nearest` (`7321`). Os dados vêm de `lagoa_s2.json` (2,5 MB), baixado só ao abrir Satélite ou Solo (`7266`, `7347-7350`).
- **Pivôs:** GeoJSON `M.lg.geo`, círculos pelo centro do KML e pela área declarada (`M.geo` "círculo pelo centro do KML…").
  - `pv-fill`: preenchimento por camada, com opacidade 0,55 na classe, 0,35 em nuvem e 0 em "none" ou nos pixels (`7338-7342`).
  - `pv-line`: branco, 1,8 px.
  - `pv-sel`: `#15201A`, 4 px (`7323-7325`).
- **Rótulos:** HTML `maplibregl.Marker` com `.lg-rot` (`7329-7331`, CSS `7260`). Mostram `<b>` com "P1" a 15 px/800 e `<span>` com o rótulo da camada a 11 px/700 e `max-width:120px`, em branco com sombra preta. O `<span>` some em pivôs com menos de 20 ha (`.peq`), mas o menor tem 29,92 ha, então isso nunca ocorre. Não há regra de colisão nem dependente de zoom.
- **Limites:** sem `attributionControl`, rotação desligada, `maxZoom` 17,5. `lgLimites` prende o arrasto e o afastamento à área da imagem (`7307-7310`).
- **Erro e carga:** se o CDN falhar, aparece "Mapa real indisponível… Recarregue a página." (`7886`, l.48). Não há indicador de carregamento do mapa nem do JSON de pixels.

### 1.2 Hover e foco

| | Santa Rita (SVG) | Lagoa Grande (MapLibre) |
|---|---|---|
| Hover | Só `cursor:pointer` (l.48) e `svg [role=button]:hover{filter:brightness(.92)}` em `@media (hover:hover)` (l.20). Nas camadas Satélite e Solo o grupo de pixels fica **por cima** do polígono, então o realce praticamente some | Só cursor: `m.on('mouseenter','pv-fill',()=>{ m.getCanvas().style.cursor='pointer'; })` (`7328`). Sem destaque e sem popup |
| Dica (tooltip) | **Nenhuma, por decisão:** `g2dicaTexto` exclui SVG (`comando: … &&!(el instanceof SVGElement)}); } // polígono do mapa não vira dica`, `1231`). O componente `g2dica` (atraso de 300 ms, `1282`) não age no mapa | Nenhuma |
| Foco de teclado | `tabIndex="0" role="button"` em cada forma (l.48); `svg [role=button]:focus-visible{stroke:#15201A;stroke-width:4px;stroke-dasharray:7 4}` (l.20). Enter e Espaço selecionam (`7843`). Sem dica no foco | Pivôs **não focáveis**. Os marcadores recebem `role="img"` e `aria-label="P5: …"` (`7341`) sem `tabindex` |

O valor de um pixel ou de um ponto **só aparece com clique** (Satélite) e nunca no hover.

### 1.3 Clique e seleção

**Santa Rita** (`v['tk_'+t]`, `7838-7843`), em ordem de prioridade:

1. Modo Medir: aviso com a área e o perímetro do cadastro.
2. Modo Programar vistoria (`cvis`): cria a vistoria.
3. Camada Satélite com pixel válido: seleciona o pixel e o talhão (`px:{t,i}`).
4. Modo Selecionar área (`selm`): soma o talhão à seleção ou o retira.
5. Caso normal: seleciona; clicar de novo no mesmo talhão **desmarca**.

**Lagoa Grande** (`lgClick`, `7300-7305`): mesma lógica, com o pixel achado pela lat/long (`lgPixelAt`, `7296`).

**Como a seleção aparece**

- Contorno escuro: 6 un no SVG, 4 px no MapLibre.
- Pixel: quadrado com contorno de 3 un (SVG) ou linha de 2,5 px (`pxs`, `7326`).
- O painel lateral `aside` (384 px) abre ao lado; no estreito vai **abaixo** do mapa (l.52: `.mapa-linha{flex-direction:column}`).

**Conteúdo do painel** (`panelTal`, `7680-7787`)

- Cabeçalho "T1 · 312 ha" ou "Pivô 5 · 47 ha", com o resumo do cultivo e da fazenda e um chip de estado.
- O corpo **depende da camada ativa** (ver 1.4).
- Com vários talhões, `panelArea` (`7788-7792`) mostra soma de área, lista, "Ordens na área" (camada O.S.), "Programar vistoria nas áreas" (Satélite e Pragas) e "Limpar seleção".

**Como desmarcar e voltar**

- "×" no painel (`pan_close`, `7854`) ou novo clique no talhão.
- Trocar de fazenda limpa a seleção (`7872`).
- Trocar de camada **mantém** a seleção (`7832`).
- **Clique no fundo não desmarca:** o retângulo de fundo do SVG não tem handler, e no MapLibre `tmClique` só age em modo de desenho (`8240`).
- **Esc não fecha** painel, modos nem tela cheia. Só há Esc no menu Alvos (`7879`).

**Endereço (URL)**

- A seleção **não** vai para a URL.
- O contexto (fazenda, safra, cultura, camada, seleção, filtros, zoom do SVG, O.S. escolhida, pixel) é salvo em `sessionStorage['mapa-ctx']` a cada desenho (`7806`) e restaurado ao voltar (`7801-7803`).
- A câmera do MapLibre **não** é salva: o mapa nasce em `bounds:M.lg.bbox` (`7315`).
- Entradas por hash: `#car[:T]` (`7951-7955`) e `#talhao=ID`, `#desenhar=ID`, `#importar` (`8337-8342`). `#talhao` enquadra o pivô com `tmEnquadra` (`8231`).

**Seleção múltipla:** botão "Selecionar área" (title "Selecionar vários talhões"; `7862`), um clique por talhão. **Não há laço nem retângulo.**

### 1.4 As 9 camadas

Nomes internos em `M.lays`: `Integrado, Satélite, Análises de solo, MIP/MID, O.S./prazos, Irrigação, Lavoura, Colheita, Custos`; os rótulos de tela vêm de `M.nome`.

Comum a todas:

- Cor por classe pela paleta `M.lcop`: ok `#7FAE68`, good `#5F8F55`, lime `#A9C06A`, yellow `#D4B25A`, orange `#D98A4E`, red `#C8553D`, gray `#C9CFCB`, blue `#6E9FC6`, navy `#44739A`, purple `#9B8BC4`, none `#E4E9DF`, cloud em hachura. A classe sai de `cls0` (`7522-7547`) e a legenda de `legend` (`7551-7566`).
- O rótulo da camada aparece **sempre** sobre o talhão.
- O filtro Cultura deixa os talhões de fora como `none` "fora do filtro" (`7521`).
- A faixa da camada traz título, ⓘ com fonte e regra (`fonte`, `7568`), filtros, KPIs (`strip`, `7581`) e um link de módulo (`FL`, `7822`).
- Hover é igual em todas (só cursor).

| Camada (interna) | O que codifica, filtros e unidades | Legenda | Sem dado | Ação na faixa | Clique / painel (primária) |
|---|---|---|---|---|---|
| **Integrado** (`Integrado`) | Pior situação operacional (`M.integ`, mais O.S. a liberar e conflito de irrigação; `integ` 7409-7415). Rótulo, ex.: "OS-0420 impedida", "mancha 1,2 ha · satélite". Filtro Mostrar: Todas as condições ou Só pendências | em dia · atenção ou a liberar · impedida ou conflito · encerrada · sem pendência | `none` "sem pendência" | "Abrir ordens ›" para `OS.dc.html` (sem filtro) | Painel "Neste talhão": uma linha por camada, com chip e botão "Ver …" que troca a camada mantendo a seleção (`7780-7786`). **Sem primária** |
| **Satélite** | Pixels do índice NDVI, NDRE, EVI, SAVI ou NDMI; Cena (Santa Rita 21/09, 16/09, 06/09; Lagoa Grande 25/09, 10/09); Contraste **Talhão (padrão)**, Fazenda ou Absoluto. Rótulo "NDVI 0,66". Paletas v1..v6 e m1..m6 (`M.satpal`) | 6 classes (Falha…Vigor alto, ou Muito seco…Muito úmido) com faixas numéricas. No contraste Talhão sem talhão escolhido, **só nomes, sem valores** (`7559`). Mais "sem cultura" e "nuvem" | `gray` com o motivo (`M.semcult`, ex.: "solo exposto · pré-plantio"); `cloud` em hachura no SVG ("nuvem · sem leitura"). No MapLibre, pixel sem dado (255) fica transparente | "Ver histórico ›" para `AG-06.dc.html`, **que é "Eficácia e histórico" (pragas)**, sem talhão | Clique seleciona **pixel e talhão**. Painel: cena, % de nuvem no talhão e na cena, estado Normal/Atenção/Crítico (`satEstado` 7453), os 5 índices com variação, pixel selecionado, mancha ou queda com "Programar vistoria" (primária só se Crítico). **Sem primária** de nível superior |
| **Solo** (`Análises de solo`) | Mapa de calor por interpolação IDW (inverso do quadrado da distância) dos pontos do laudo (`soloGrade` 7991). Filtros Laudo, Camada (0–20 ou 20–40 cm), Indicador (V % etc.) e Contraste. Pontos desenhados, não clicáveis | Absoluto: classes da tabela com valores. Relativo: "menor (pior) … maior (melhor)" com **4 rótulos vazios** no meio (`8011-8015`) | `gray` "Sem laudo" ou "não calculável"; `none` "fora do laudo escolhido"; "· sem pontos" | **Nenhum link** (FL não tem Solo). Ícone "Importar laudo" na barra de ferramentas para `AG-02#registrar=` | Primária: Registrar, Validar, Corrigir ou Abrir laudo, levando ao AG-02 (`soloAc` 8048). Painel lista os 6 piores pontos com coordenada |
| **Pragas e doenças** (`MIP/MID`) | Pior situação das vistorias do período (7 ou 30 dias), com menu **Alvos** de escolha múltipla. Rótulo "alvo · situação · +n" | 8 itens: acima do NC, foco, perto do NC ou coleta pendente, em controle, programada, abaixo do NC, atrasada ou sem vistoria, sem cultura | `none` "sem cultura" ou "sem X no protocolo"; `gray` "sem vistoria em N dias" ou "vistoria atrasada N dias" | "Abrir Pragas e doenças ›" (AG-01) e o botão "Programar vistoria" (modo clique) | Primária: próximo passo da pior vistoria. Quando é comando, roda no próprio mapa (`mapMipRun`); senão abre `AG-01#VIS-xxx`. Ou "Programar vistoria" (`7746-7760`) |
| **Ordens de serviço** (`O.S./prazos`) | Mostrar Fases, Avanço, Atrasos, Impedimentos ou Insumos; filtro Fase; Período (só em Insumos). Rótulo conta as ordens por fase (`osCls` 7485-7498) | Por visão (`osLegend` 7499-7503). Fases: cinza = "a liberar · encerradas" (**duas fases, uma cor**) | `none` "sem ordem" ou "sem ordem aberta" | "Abrir ordens ›" (`OS.dc.html`; em Insumos, "Abrir compras ›") | Cartões das O.S. (`radiogroup`) e "Próximo passo" com **comando no lugar** e confirmação: Liberar, Aprovar, Iniciar, Apontar (data e ha), Enviar conferência, Encerrar (`nxOf` 7637-7668). Mais "Nova O.S. neste talhão", que leva a `OS.dc.html` **sem talhão** (`7769`) |
| **Irrigação** | Mostrar Hoje (situação do setor) ou Balanço hídrico (déficit em mm, mais lâmina e percentímetro no rótulo) | Hoje: irrigando, programada, pendente, impedida, sem necessidade, ≈ estimado, sequeiro. Balanço: menos de 5 / 5–10 / 10–15 / 15 mm ou mais, ≈ estimado, sequeiro | `gray` sequeiro ou "preparo · sem rega"; `cloud` "≈ estimado" | "Abrir irrigação ›" para `IR-01#faz=` | Primária: ação do setor (`xi.ac`, ex.: programar), que leva ao módulo de irrigação. A seção tem o link `IR-01#<talhão>` |
| **Estádio** (`Lavoura`) | Fase da cultura: pré-plantio, vegetativo, reprodutivo, produção contínua, granação ou maturação, colhido. Rótulo, ex.: "Milho · DAP 44 · V10" | 6 itens. `none` = "colhido **ou** fora do filtro" | `gray` pré-plantio; `none` colhido | "Abrir safra ›" (SAF) | Seção Estádio com "Abrir no Planejar safra" (sem talhão). **Sem primária** |
| **Colheita e produtividade** (`Colheita`) | Mostrar Situação (em colheita, programada, prevista, colhida, sem previsão) ou Carência e destino (mais "Consultar em" Hoje, 7 ou 14 dias). Produtividade e previsão **só no texto do rótulo**: não há escala de cor de sc/ha | Situação: 5 mais "sem colheita". Carência: 4 mais "sem lavoura" | `none` "sem colheita"; `yellow` "sem previsão" | Situação: **nenhum link**. Carência: "Abrir qualidade dos lotes ›" (CO-06) | Primária: ação da Previsão e colheita (`colhAc` 8085). Na carência, Ver restrição, Ver pendência ou Rever programação, levando a O.S. ou CO-06 (`carAc` 7942) |
| **Custos** | Mostrar Previsto R$/ha (**todo talhão com previsto fica azul**; o valor só aparece no rótulo) ou Realizado × previsto (ok / até +10 % / acima de +10 %) | 2 ou 4 itens | `gray` "sem previsto"; `none` "sem execução" | "Abrir safra ›" | Seção com previsto, realizado e conferido e "Abrir origem…". **Sem primária** |

### 1.5 Controles do mapa

- **Zoom e pan**
  - Santa Rita: botões + e − (36×36; l.48) aplicam `transform:scale(z)` de 1 a 2, em passos de 0,25, com `transform-origin:50% 50%` (`7821`) dentro de `.mapa-area{overflow:hidden}`. **Sem pan, roda nem pinça.**
  - Lagoa Grande: os mesmos botões chamam `map.zoomIn()` e `zoomOut()`. Roda, arrasto e pinça são os padrões do MapLibre; não há gesto cooperativo (`7314-7315`).
- **Enquadrar:** não há botão. Só o hash `#talhao=` enquadra (`8231`). A seleção não aproxima o mapa do talhão.
- **Busca de talhão:** **inexistente** (não há `type="search"` no template, l.48).
- **Filtros**
  - Topo: Fazenda, Safra e Cultura (l.48; `7872-7874`).
  - Por camada: segmentados ou listas na faixa (`v.flt`, `7815-7819`).
  - Alvos: menu de escolha múltipla com Esc (`7876-7882`).
- **Tempo:** só "Cena" (Satélite), "Período" (Pragas e Insumos) e "Consultar em" (Carência). Não há linha do tempo nem comparação de duas datas.
- **Escala** Talhão, Fazenda ou Absoluto: em Satélite e Solo, com padrão **Talhão** (ordem em `M.filt`).
- **Fazenda:** um `select` no topo, compartilhado por `mapa-ctx`.
- **Tela cheia:** só Santa Rita (`v.has_full=!v.map_lg`, `7886`). É um `role="dialog"` sem `aria-modal`, sem Esc e sem gestão de foco (l.52).
- **Barra de ferramentas** (l.48; `rst()` 7860): Selecionar área, Medir, Desenhar e Importar (só Lagoa Grande, `tm_ok`), Tela cheia e o ícone Importar laudo (Solo).
  - "Medir" **não mede**: só mostra no aviso a área e o perímetro do cadastro (`7838`, `7301`).
  - O aviso dura 4,5 s (`8532`) e tem `aria-live="off"` (l.53).
- **Celular e estreito** (IN-04 por container query, l.52)
  - Abaixo de 919 px: o painel vai para baixo do mapa, que tem altura mínima `max(62vh,280px)`.
  - Abaixo de 760 px: a faixa quebra.
  - Abaixo de 700 px: a barra de ferramentas vira uma linha com rolagem horizontal em `top:52px`, e a legenda fica com `max-height:30%` e rolagem.
  - A barra de camadas rola na horizontal e centraliza a camada ativa (`7830-7831`).
  - **Nenhuma tela MB-\* tem mapa.**
- **Alvos de toque**
  - Abas de camada: 44 px em ponteiro grosso (l.20, `.g2visoes>button`).
  - Botões da barra de ferramentas: cerca de 29 px (padding 6/10, fonte 12, sem `min-height`; `rst` 7860). A regra de 44 px só cobre botões `aria-pressed` com `border-radius: 999px` (l.20).
  - Zoom: 36 px. Fechar o painel: 30×30. Segmentados da faixa: 7 px de raio, fora da regra.

### 1.6 Acessibilidade

- **Santa Rita:** o SVG pai tem `role="img"` (l.48) e contém `polygon` e `circle` com `role="button"`. Pela especificação ARIA, filhos de `img` são apresentacionais, então leitores de tela **podem não expor os botões**. `aria-label` = "T1: <rótulo da camada>", sem área nem cultura (`7836`).
- **Lagoa Grande (padrão):** pivôs **inacessíveis por teclado e leitor de tela**. Ficam no canvas; marcadores com `role="img"` e sem foco (`7341`); `#mapa-real` tem `aria-label` em um `div` sem papel (l.48). Sem lista alternativa, o painel do pivô é inalcançável sem ponteiro. A navegação do canvas pelo MapLibre (setas e +/−) existe por padrão, mas sem `locale` em pt-BR **[confirmar no navegador]**.
- **Barra de camadas:** `role="tablist"` e `role="tab"` com `aria-selected`, mas **sem** `aria-controls`, `tabpanel` nem setas. O handler `g2visaoTeclaBarra` exige `[data-visao]` (`1413`), que não existe nesses botões.
- **Foco visível:** contorno verde de 2 px nos controles (l.20). No SVG, contorno tracejado escuro (l.20), muito parecido com o contorno de seleção (escuro, 6 un).
- **Cor como único código:** atenuado porque o rótulo de texto está sempre visível, no SVG e no MapLibre. Ainda assim:
  - `none #E4E9DF` contra o fundo do SVG `#E3EADB` tem contraste **1,0:1**. "Sem pendência", "sem ordem", "fora do filtro" e "colhido" se confundem com o fundo e entre si; `gray` contra `none` dá 1,28:1.
  - Nos marcadores da legenda, a borda branca sobre o fundo branco da legenda dá 1,23:1 em `none` (`Lc`, 7549).
  - Na simulação de deuteranopia (Machado 2009), red `#C8553D` vira `#90823A`, good `#5F8F55` vira `#8B8158` e ok vira `#ACA06C`: a paleta de estado vira tons de oliva. Na paleta de vigor, v1 e v6 também ficam próximos.
- **Contraste dos rótulos:** escuro com halo branco no SVG e branco com sombra preta no MapLibre, adequado. O problema é o tamanho (D12, D28), não a cor.
- **Avisos:** a medição e as confirmações aparecem só no aviso (`aria-live="off"`, 4,5 s).
- **Foco após selecionar:** não vai para o painel nem anuncia nada. No estreito, o painel nasce fora da tela (não há `scrollIntoView` nem `focus`; só `scrollTop` interno, `7857`).

### 1.7 Defeitos e inconsistências concretos

| # | Defeito | Evidência |
|---|---|---|
| D1 | Lagoa Grande (fazenda padrão) não é operável por teclado nem por leitor de tela | `7327-7331`, `7341`; l.48 `#mapa-real` |
| D2 | `role="img"` envolvendo botões no SVG | l.48 |
| D3 | Nenhum hover informativo; o realce fica oculto sob os pixels; o valor do pixel só aparece com clique | `1231`, `7328`, l.20, l.48 |
| D4 | Zoom da Santa Rita sem pan: em 2× as bordas (T1, C1) ficam inalcançáveis | `7821`, l.48 `overflow:hidden` |
| D5 | Sem tela cheia na Lagoa Grande; o template da tela cheia nem tem o ramo `map_lg` | `7886`, l.52 |
| D6 | "Todas" mostra só a Santa Rita (Lagoa Grande some) | `7797`, `7884` |
| D7 | "Ver histórico" e "Ver histórico do talhão" (Satélite) levam ao AG-06 "Eficácia e histórico", que é de pragas, sem talhão | `7822`, `7711`; AG-06 `<title>` |
| D8 | "Nova O.S. neste talhão" e "Abrir ordens" sem talhão, embora a O.S. aceite `#tal=Faz\|T` | `7769`, `7822`; `OS.dc.html:6189` |
| D9 | Contraste padrão "Talhão" (sextis, faixas com a mesma quantidade de pixels) com nomes de classe absolutos ("Falha"…). Todo talhão mostra cerca de 1/6 "Falha" vermelho, e a legenda fica sem valores. O chip do painel e o "Pixel selecionado" usam a classe **absoluta** (`ka`, `kOf(val,M.idx.lim)`): a mesma área pode estar vermelha no mapa e "Bom" no painel | `7275`, `7557-7560`, `7682`, `7702`, `7706` |
| D10 | Pixel da Santa Rita anunciado como "10 m", mas a célula tem 16 un, cerca de 1,13 ha (T1: 312 ha em 276 células, cerca de 106 m de lado) | `7706`; `M.cs`, `M.px` |
| D11 | Mancha só existe para T7 (círculo fixo e `pxVals` presos em T7). O chip "mancha" (x 692–782, y 524–546) se sobrepõe ao rótulo do T7 (x 606–780, y 502–548) | l.48; `7440` |
| D12 | Rótulos do SVG em `foreignObject` de altura fixa (20 e 46 un, cerca de 2 linhas) cortam textos longos (ex.: carência "carência até 30/09 em T1-A, T1-B · dados pendentes" em P2, largura 160 un) e encolhem com o SVG: em cerca de 343 px de largura, escala 0,34×, o rótulo de 15 un fica com cerca de 5 px **[confirmar no navegador]** | l.48; `carRot` 6974 |
| D13 | Lagoa Grande: cores a 55 % sobre a imagem diferem dos marcadores a 100 % da legenda; `cloud` vira cinza liso a 35 % (a legenda mostra hachura); `gray` e `cloud` têm a mesma cor | `7338-7340`, `7549` |
| D14 | `none` igual ao fundo; vários estados distintos ("sem pendência", "fora do filtro", "colhido") com a mesma cor | `M.lcop`; legenda Estádio `7561` |
| D15 | Mesma cor com significados diferentes entre camadas: amarelo e laranja são alerta em Integrado, O.S., Irrigação e Custos, mas "produção contínua" e "granação" no Estádio (12 pivôs amarelos na Lagoa Grande, `M.lav`); azul é "liberadas", "irrigando", "em controle", "com previsto" e "programada". Paleta não segura para daltonismo | `7480`, `7561-7565`, `8057` |
| D16 | Clique no fundo e Esc não desmarcam. No Satélite, um novo clique escolhe outro pixel em vez de desmarcar (toggle diferente das outras camadas) | `7838-7842`, `7304`, `8240` |
| D17 | Seleção e câmera fora da URL; câmera da Lagoa Grande não persiste | `7806`, `7315` |
| D18 | `#talhao=ID` (CD-01det "Ver no mapa") não troca a fazenda. Se o contexto salvo for Santa Rita, a seleção é filtrada e nada acontece (o `tmEnquadra` tenta 20 vezes e desiste) | `8339-8342`, `7805` |
| D19 | "Medir" não mede; resultado em aviso mudo e efêmero | `7838`, `7301`, `8532`, l.53 |
| D20 | Painel, modos e tela cheia sem Esc nem gestão de foco; no estreito, o painel aparece abaixo de 62vh de mapa, sem rolagem | l.52; `7856` |
| D21 | Abas sem o padrão ARIA completo (setas, `aria-controls`) | l.48; `1413` |
| D22 | Alvos de toque abaixo de 44 px (ferramentas, fechar, zoom 36 px) | `7860`, l.48, l.20 |
| D23 | Legenda (e a faixa no estreito) sobre o mapa sem `pointer-events:none`: bloqueia cliques nos talhões de baixo e no estreito ocupa até 30 % | l.48, l.52 |
| D24 | Solo e Colheita (Situação) sem link de módulo na faixa, ao contrário das outras 7 | `7822-7823` |
| D25 | Ícone `Colheita` não existe em `ICN`: botões de colheita sem ícone | `7606`, `7775`, `8085` |
| D26 | Mapa da fazenda padrão depende do CDN em tempo de execução, sem modo offline e sem indicador de carga (inclusive do JSON de 2,5 MB) | `7264`, `7266` |
| D27 | Mesmo pivô com três nomes: "P1" (marcador), "Pivô 1" (painel, `7682`) e "PV01" (CD-01). A Santa Rita também tem um "P1" e um "P2" | `7341`, `7682`; CD-01 l.48 |
| D28 | Rótulos da Lagoa Grande em px fixos, sem colisão nem regra por zoom; o espaçamento entre pivôs é cerca de 1,2 km. No celular (cerca de 16 m/px) ficam cerca de 73 px entre centros contra rótulos de até 120 px, provável sobreposição **[confirmar no navegador]** | `7260`, `7329-7331` |
| D29 | Arrasto de um dedo no MapLibre dentro de uma página com rolagem: risco de prender a rolagem no celular (sem `cooperativeGestures`) **[confirmar no navegador]** | `7314-7315` |
| D30 | "Selecionar área" sugere laço, mas é clique por talhão (o title diz "Selecionar vários talhões") | l.48; `7862` |

---

## 2. Outras telas

**CD-01 · visão Mapa da aba Talhões** (l.48; JS `2686-2722`, `2736`, `2761`)

- **Geometria:** a Santa Rita usa outras coordenadas que o IN-04 (T1 `30,30 290,22 300,205 40,215` contra `30,30 300,22 312,282 40,292`). A Lagoa Grande usa círculos **projetados** dos centros do KML (ajuste linear com resíduo de 0,1 un), com rótulos "PV01"…
- **Cor:** situação do polígono no cadastro. Validado `#8FD67F` com contorno `#1E7A4C`; diferença sem motivo `#FFD500` com `#8A5A00`; inativo `#C9CFCB`; sem polígono `#E9EEE6`.
- **Legenda em texto:** "■ polígono validado · ■ diferença sem motivo · ■ inativo · **talhão sem polígono não aparece no mapa**". Os quadradinhos têm a cor do **contorno**, não do preenchimento. Como as formas são fixas, o talhão sem polígono **aparece**, em cinza.
- **Clique:** `g2open(self,GR('g_tal'),id)` abre o **formulário de edição** ("Talhão", `edit.m='form'`), não o detalhe CD-01det (que existe: `irDet`, 2649).
- **Hover e teclado:** sem `tabindex` nem `role`; só `cursor:pointer`. Sem zoom; altura fixa de 430 ou 520 px.

**CD-01det** (l.48; `geoVals` 2660-2670)

- O "polígono" é a mesma forma `clip-path` para qualquer talhão, **inclusive pivô**, com faixas de parcela proporcionais.
- "Livre" usa o mesmo verde do "validado".
- Só a Lagoa Grande tem "Ver no mapa ›" e "Desenhar/Redesenhar no mapa ›" (`2721-2724`). A Santa Rita não tem caminho para o mapa.

**PL-06:** SVG estático da proposta de divisão de T1; outra forma para T1. Sem interação nem link para o mapa.

**CA-01 · visão Mapa:**

- Desenho estático com **valores escritos no HTML** (ex.: "OS-0421 · 190/350 ha", "dia 4 de 7"), que podem divergir do cenário vivo.
- Paleta própria (contornos `#1E7A4C`, `#8A5A00`, `#B42318`; tracejado = impedida) diferente das cores de fase do IN-04 (`FASEC`: azul = liberadas, ok = em execução).
- Sem clique nem link para a camada O.S. do IN-04.

**AG-01det · Rota em W:**

- Pontos posicionados pelo índice (`x=60+i·880/(n−1)`, `y` alternando 70 e 230), **não pelo GPS**, sobre um retângulo genérico, não sobre o talhão.
- Os pontos são `span` com `title`: a dica aparece no hover, mas os pontos não recebem foco nem toque.
- Cores por NC coerentes com o `lcop` do mapa.

**MB-\*:** nenhum mapa. O app de campo (MB-06) não mostra a posição do ponto nem a rota sobre o talhão; o GPS é texto e um checkbox de simulação.

**Consistência entre telas**

- Quatro desenhos diferentes da Santa Rita (IN-04, CD-01, PL-06, CA-01).
- Três nomes por pivô.
- Duas paletas de status de O.S. (IN-04 e CA-01).
- Clique abrindo o formulário (CD-01) ou o painel de detalhe (IN-04).

---

## 3. As 15 oportunidades de maior valor

1. **Acesso sem ponteiro (D1, D2, D21).** Criar uma lista ou campo "Ir para talhão" sincronizado com o mapa, com foco e Enter abrindo o painel. Tirar o `role="img"` do SVG (usar `role="group"`) e completar o padrão de abas.
2. **Hover e foco com cartão rápido (D3).** Mostrar nome, área, cultura, estado da camada e valor, após cerca de 300 ms e também no foco, reutilizando o `g2dica`. Em Satélite e Solo, hover sobre pixel ou ponto mostra valor, classe e coordenada. O clique continua abrindo o detalhe.
3. **Um só motor de mapa (D4, D5, D26).** Levar a Santa Rita para o MapLibre, ou ao menos dar pan, roda, pinça e "Enquadrar fazenda/talhão". Dar tela cheia à Lagoa Grande. Empacotar o MapLibre (offline) com indicador de carga.
4. **Contraste honesto no Satélite e no Solo (D9).** Padrão Fazenda ou Absoluto na visão da fazenda; Talhão só com um talhão escolhido. Nomes relativos no modo Talhão ("mais baixo do talhão" em vez de "Falha"). Legenda sempre com valores. Chip e pixel do painel na **mesma** escala do mapa.
5. **Destinos que preservam contexto (D7, D8, D24).** "Ver histórico" leva à série temporal do índice do talhão, ou sai. "Nova O.S. neste talhão" e "Abrir ordens" levam `#tal=Faz|T`. Dar link de módulo também a Solo e Colheita.
6. **Fazenda coerente (D6, D18).** "Todas" com as fazendas que têm geometria, ou removida. `#talhao=ID` troca a fazenda e enquadra.
7. **Paleta semântica única e segura para daltonismo (D14, D15).** Um token por significado em todas as camadas, sem amarelo para fase fenológica. Sem dado e fora do filtro com hachura ou contorno tracejado distintos do fundo. Segunda codificação (padrão ou ícone) para crítico e impedido.
8. **Legenda fiel e útil (D13, D23).** Na Lagoa Grande, a opacidade e a hachura (`fill-pattern`) iguais às da legenda. Legenda recolhível e sem bloquear cliques; clicar numa classe realça os talhões dela.
9. **Camadas quantitativas com escala de cor (Custos e Colheita).** R$/ha e sc/ha em gradiente com valores na legenda, não "todo azul" com o número só no rótulo.
10. **Regras de rótulo (D12, D28).** Tamanho mínimo em px independente da escala do SVG; reticências com o texto completo no hover; colisão e ocultação por zoom na Lagoa Grande (só o nome em zoom baixo).
11. **Manchas por dados (D11).** Qualquer talhão, lista no painel com "Ir para" e "Criar vistoria", sem sobrepor o rótulo.
12. **Seleção previsível (D16, D20, D30).** Clique no fundo e Esc desmarcam; toggle igual em todas as camadas (pixel só em modo "Inspecionar"); enquadrar o selecionado; no celular, o painel vira bottom sheet com foco e anúncio; laço ou retângulo de verdade, ou renomear para "Selecionar vários".
13. **URL como estado (D17).** Ex.: `#faz=LG&lay=sat&t=PV05&cena=25/09`, para compartilhar, voltar e abrir de outras telas sem `sessionStorage`. Persistir a câmera da Lagoa Grande.
14. **Ferramentas e retorno (D19, D22, D29).** "Medir" real (distância e área desenhadas) ou renomeada para "Área e perímetro", com o resultado no painel e não num aviso mudo. Alvos de 44 px no toque. Gesto cooperativo no celular.
15. **Um componente de mapa em todas as telas (D27, seção 2).** Mesma geometria, nomes (P1 / Pivô 1) e cores em CD-01 (clique abre o **detalhe**), CA-01 (gerado por dados ou link para a camada O.S.), PL-06 e AG-01det (pontos pelo GPS dentro do polígono). O MB-06 pode ganhar um minimapa da rota.

---

## 4. Não determinável só pelo código

- Sobreposição real dos rótulos e marcadores em cada viewport, e o corte efetivo dos `foreignObject` em cada navegador.
- Rótulos e `aria-label` padrão do canvas do MapLibre 5.9 (idioma e papel) e o comportamento real de rolagem por toque.
- Desempenho (carga de 2,5 MB de pixels, texturas canvas e `play`/`pause`).
- Se o CA-01 "Mapa" está ligado a algum fluxo real: o conteúdo é estático, mas a visão está acessível pelo segmentado.

**Suposições:**

- O runtime `x-dc` repassa `onClick` e `onKeyDown` para elementos SVG como o React (o código do mapa supõe isso).
- A ordem de renderização do template segue a ordem do DOM: pixels por cima do polígono e legenda por cima do mapa.
