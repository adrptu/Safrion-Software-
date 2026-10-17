# Padrões de 17/10/2026 · Mapa da fazenda (MAPA-UX)

Pedido do proprietário de 16/10/2026, cobrado em 17/10, transformado em padrão pelo método da skill `padrao-safrion`:

> "Mapa da fazenda com UX e UI de excelência — passar o mouse e entender, clicar e detalhar, sem perder o contexto"
>
> "as melhorias de design, ux e ui, hover, etc dentro do mapa também nao mudaram nada. ja foi pedido."

- **Vale para todas as telas com mapa ou forma de talhão.**
  - Implantado no IN-04 (Mapa).
  - CD-01 (visão Mapa), CD-01det, PL-06, CA-01 e AG-01det entram na MUX-F4, junto com o SAF-MAPA, que extrai a peça comum.
  - O motivo da espera é que essas telas ficam em arquivos de outras frentes (`cad_fazendas.py`, `campo.py`, `agronomia.py`).
- **Fonte do desenho:** `docs/integracao/V73/MAPA-UX/` (pedido, confronto §7 e §8.2). Implantação e medidas: `implantacao/LEIAME.md`.
- **Testes:** `tools/prototipo/v37/gen37/mapa_mux_f0_test.py`, `mapa_mux_f1_test.py`, `mapa_mux_f2_test.py` e `mapa_mux_unit.js`.
- **Contraprova:** o render da base 0b3d0d4 reprova.
- **Peça:** `areas/inicio.py`, bloco MUX (API em `<mux-puro>` e funções `mux*`), para o SAF-MAPA extrair.

## MUX-P1 · Cartão do talhão no hover e no foco

| Item | Conteúdo |
|---|---|
| **Regra** | <ul><li>O hover e o foco de teclado mostram o mesmo cartão claro: número e área, cultura e estádio, valor da camada com unidade, estado em texto, data do dado, comparação curta quando houver, O.S. em andamento e "Clique para detalhar".</li><li>Abre sem espera programada.</li><li>Nunca é cortado pela janela nem cobre o talhão; não tem ação dentro.</li><li>Some ao sair do talhão e do cartão (120 ms para o ponteiro chegar até ele); Esc dispensa (WCAG 1.4.13).</li><li>No toque não abre: tocar escolhe o talhão.</li></ul> |
| **Dano evitado** | Clicar talhão por talhão para descobrir qual merece atenção; texto essencial só no clique. |
| **Teste** | `mapa_mux_f2_test.py` C1–C5 e M1 |

## MUX-P2 · Talhão é botão num grupo com nome

| Item | Conteúdo |
|---|---|
| **Regra** | <ul><li>O mapa é um grupo com nome ("Talhões da Fazenda X · N talhões") e uma parada de Tab (tabindex móvel).</li><li>As setas vão ao vizinho na direção; Home e End vão ao primeiro e ao último pelo nome.</li><li>Enter abre o painel com o foco no título; Esc fecha e devolve o foco ao talhão.</li><li>"/" (com o foco no bloco do mapa) abre a busca "Ir para talhão".</li><li>Cada talhão tem `aria-pressed` e o nome completo do pedido ("P5, 71 ha, cultura e estádio, valor, estado, data"); instruções visíveis e no `aria-describedby`.</li><li>O mapa não muda de zoom nem de centro sozinho; só a busca e "Localizar no mapa" enquadram.</li></ul> |
| **Dano evitado** | Pivôs inalcançáveis sem mouse (0 de 23); oito paradas de Tab num desenho só; painel que abre sem o leitor de tela saber. |
| **Teste** | `mapa_mux_f1_test.py` F1-1 a F1-4 e F1-7 |

## MUX-P3 · Cor honesta

| Item | Conteúdo |
|---|---|
| **Regra** | <ul><li>Sem leitura (nuvem, sem dado) em hachura; sem cultura em neutro; nunca a cor de um valor.</li><li>"Estimado" é a origem do valor: fica com a cor da classe e a etiqueta "≈ … estimado", nunca na hachura (NC10).</li><li>"Não se aplica" tem contorno tracejado `#6B776F`, nunca só a cor do fundo (D14).</li></ul> |
| **Dano evitado** | Ler falta de dado como condição; ler valor estimado como falta de leitura. |
| **Teste** | `mapa_mux_f2_test.py` K1 |

## MUX-P4 · Rótulo sobre placa e anéis em duas cores

| Item | Conteúdo |
|---|---|
| **Regra** | <ul><li>Dentro do talhão, no máximo 3 linhas (número / valor com unidade / estado curto); em escala pequena, só o número.</li><li>O valor e o estado ficam numa placa branca a 90 %, com texto opaco `#15201A`: ≥ 13,4:1 sobre qualquer fundo, e nenhum `opacity` no caminho do texto.</li><li>Seleção, foco, hover e realce da legenda em duas cores (escuro e branco: ≥ 3:1 sobre qualquer preenchimento); a seleção é contínua e forte, e o foco tracejado.</li></ul> |
| **Dano evitado** | Rótulo ilegível sobre a imagem; seleção que some sobre a cor da classe (NC11). |
| **Teste** | `mapa_mux_f2_test.py` K2 e S1 |

## MUX-P5 · Legenda que trabalha

| Item | Conteúdo |
|---|---|
| **Regra** | <ul><li>Cada classe é um botão com a contagem e a área ("foco · 2 · 137 ha").</li><li>Passar o mouse ou focar realça os talhões dela.</li><li>Clicar filtra o mapa e a lista: os outros esmaecem e a Lista mostra "N de M". Clicar de novo limpa.</li><li>O contêiner da legenda não pega o clique fora dos itens.</li></ul> |
| **Dano evitado** | Legenda decorativa; contar talhões de uma condição à mão. |
| **Teste** | `mapa_mux_f2_test.py` L1 |

## MUX-P6 · Ver dados: Lista | Mapa no mesmo bloco

| Item | Conteúdo |
|---|---|
| **Regra** | <ul><li>A Lista tem os mesmos filtros, a mesma seleção e o mesmo painel do mapa.</li><li>Uma linha por talhão, com valor, estado em texto e data, do mais grave ao melhor, e "N de M".</li><li>A linha abre o painel (SEL-02, seta de ir da TAB-11); "Localizar no mapa" volta ao mapa com o talhão escolhido.</li><li>Em "Todas", a Lista traz as três fazendas.</li><li>Sem o MapLibre (CDN), a Lista continua e o aviso oferece "Tentar de novo".</li></ul> |
| **Dano evitado** | Mapa como único caminho, inalcançável para quem não enxerga ou não usa mouse (MAPUX-06, RF-WRK-004). |
| **Teste** | `mapa_mux_f1_test.py` F1-5, F1-6 e F1-10 |
| **Exceção registrada** | A Lista é peça própria: o motor de grade é estático e as linhas aqui mudam a cada camada. Ela migra para o componente comum no SAF-MAPA. |

## MUX-P7 · Endereço é estado

| Item | Conteúdo |
|---|---|
| **Regra** | <ul><li>`#faz=&lay=&t=&dt=` guarda fazenda, camada, talhão e data da cena; recarregar, voltar e o link compartilhado abrem o mesmo mapa.</li><li>Na Lagoa Grande, a câmera é guardada na sessão (voltar sem reenquadrar).</li><li>`#talhao=ID` troca a fazenda; ID inexistente avisa e não escolhe outro talhão.</li></ul> |
| **Dano evitado** | Voltar de outra tela e perder camada, data, seleção e zoom. |
| **Teste** | `mapa_mux_f1_test.py` F1-8, `mapa_mux_f0_test.py` F0-2 e `mapa_mux_unit.js` H |
