# Padrões de 17/10/2026

Pedidos do proprietário em 17/10, transformados em padrão pelo método da skill `padrao-safrion`.

- **Valem para todas as telas do mesmo tipo**, no protótipo e no software real.
- **Medição e catraca:** `tools/prototipo/v37/gen37/ds_modulos.py` (148 telas, 10 regras); `--catraca` reprova se a contagem de alguma regra subir em algum módulo.
- **Relatório da frente:** `docs/integracao/V73/ds-modulos-2/DS-MODULOS-2.md`.

## MAIS-02 · Ações do cabeçalho da tela: a primária e o ⋯

> "os 3 pontinhos no topo da tela a direita em criar plano.... é uma boa, toda tela que tiver mais ações pode ter esses 3 pontinhos nesses botões dessa região da tela."

**Referência:** Manutenção › Planos ("Criar plano" + ⋯).

**Regra:** à direita do título fica à vista no máximo uma primária verde; as outras ações do contexto vão para o "⋯ Mais ações", à direita dela. Detalhe, exceções e peça única em [barra-limpa-mais-acoes.md](barra-limpa-mais-acoes.md) §3. Substitui, só no cabeçalho da tela, o "primária e uma secundária à vista" da MAIS-01.

**Dano evitado:** fileira de botões no topo, que esconde o comando da vez.

**Teste:** `ds_modulos.py` regra MAIS-02 (148 telas) e `cadc_cd07_test.py` (Estrutura gerencial). Contraprova: o render anterior tem 1 desvio (CD-07) e reprova.

## VIS-07 · Cartões compactos em grade (revê a VIS-06 no motor)

> "os cartoes em ordem de serviço estao fora do padrao design system" (print da O.S. em Cartões, agrupada por talhão)

**O que estava errado:** dentro de cada grupo o cartão saía como uma linha larga de tabela dentro de uma caixa, com cabeçalho de colunas acima dos grupos e os valores espalhados na largura toda.

**Regra (modo Cartões do motor, em toda tela, inclusive agrupado):**
- Grade de cartões compactos: vários por fileira no computador (mínimo de 300 px cada), um por fileira no celular.
- Dentro de cada grupo, a mesma grade; o título do grupo e as somas ficam acima dela.
- Cada cartão:
  1. seta à esquerda quando há itens dentro (abre no próprio cartão), seleção quando a lista tem. A coluna da seta só existe quando algum cartão tem itens dentro; o título do grupo tem a sua;
  2. título com o identificador e, ao lado, o **selo de estado** (a 1ª coluna em que todo valor começa por um selo: Fase, Situação);
  3. até 4 campos, cada um com o seu rótulo, em duas colunas;
  4. ⋯ da linha no fim da 1ª linha.
- Sem cabeçalho de colunas.
- No celular, o cartão traz o mesmo selo e os mesmos campos do computador. Em Cartões, a grade usa o título e até 4 colunas do padrão; a Tabela segue com as 3 primeiras.
- Total numa faixa acima dos cartões, com rótulos.

**Peça única:** `CARTOES_CSS` e `_cartoes_html` no `engine.py`; `g2cdVals` no `g2lib.js` (selo e campos). A lista própria das Atividades do plano não muda.

**Dano evitado:** cartão que parece linha de tabela, valores longe do nome e rótulo distante do valor.

**Teste:** `ds_1610_test.py` parte C (C1 reescrito: O.S., O.S. agrupada por talhão, Planejar safra, Parceiros e Produtos) e `cartoes_test.py`. Contraprova: o render anterior (cartão em linha com cabeçalho de colunas) reprova C1.

## TAB-05 · ⋯ da linha por padrão no motor

Aplicação da TAB-05 de 15/10 ("em vez desses botões soltos na tabela, coloque os 3 pontinhos") em toda grade do motor, sem depender de cada tela pedir. Detalhe em [barra-limpa-mais-acoes.md](barra-limpa-mais-acoes.md) §4.

## CAB-1 e CAB-2 nas telas fora do menu

Aplicação da PAR-01 de 16/10 ("os demais módulos estão com design system diferente do nosso padrão de excelencia do módulo agrícola") ao cabeçalho das 86 telas fora do menu, na casca comum (`ui37.shell37`):
- **CAB-1:** "‹ Módulo" (`ui37.volta_pilula`) pelo prefixo da tela, para o módulo do menu onde o assunto mora hoje (`ui37.VOLTA_PREF`): Campo, Planejamento, Irrigação e Gestão em Agrícola; Colheita, Vendas e Logística em Comercial; Suprimentos; Mapa; Portal do parceiro; Outros acessos (Onboarding e Backoffice). O caminho diz o mesmo módulo. O detalhe continua voltando à sua lista pela seta.
- **CAB-2:** fazenda, safra e parceiro saem do topo e vão para a faixa "Trabalhando em" (FIL-01), o mesmo desenho das telas do menu (`ui37.CTX_LAB`).
- A ficha impressa da OS-0424 ganha o mesmo "‹ Ficha do app" (fora da impressão).

## TAB-07 · Sem cartões de resumo: como cada tela ficou

Aplicação tela a tela da TAB-07 de 15/10. Regra de bolso usada em todas:
- contagem que a lista já mostra: sai (fica no filtro rápido ou na linha);
- o que pede atenção: vai ao selo do cabeçalho;
- soma de uma coluna: vira a linha de total;
- dado do próprio registro (assinatura, vistoria): vira pares rótulo × valor (SEP-20261015 e), sem número grande;
- tela de indicadores (Painel do módulo, Indicadores do portal): os cartões são o conteúdo e ficam.

A tabela tela a tela está no relatório da frente.

## Mapa da fazenda (MAPA-UX): padrões de 17/10/2026

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

### MUX-P1 · Cartão do talhão no hover e no foco

| Item | Conteúdo |
|---|---|
| **Regra** | <ul><li>O hover e o foco de teclado mostram o mesmo cartão claro: número e área, cultura e estádio, valor da camada com unidade, estado em texto, data do dado, comparação curta quando houver, O.S. em andamento e "Clique para detalhar".</li><li>Abre sem espera programada.</li><li>Nunca é cortado pela janela nem cobre o talhão; não tem ação dentro.</li><li>Some ao sair do talhão e do cartão (120 ms para o ponteiro chegar até ele); Esc dispensa (WCAG 1.4.13).</li><li>No toque não abre: tocar escolhe o talhão.</li></ul> |
| **Dano evitado** | Clicar talhão por talhão para descobrir qual merece atenção; texto essencial só no clique. |
| **Teste** | `mapa_mux_f2_test.py` C1–C5 e M1 |

### MUX-P2 · Talhão é botão num grupo com nome

| Item | Conteúdo |
|---|---|
| **Regra** | <ul><li>O mapa é um grupo com nome ("Talhões da Fazenda X · N talhões") e uma parada de Tab (tabindex móvel).</li><li>As setas vão ao vizinho na direção; Home e End vão ao primeiro e ao último pelo nome.</li><li>Enter abre o painel com o foco no título; Esc fecha e devolve o foco ao talhão.</li><li>"/" (com o foco no bloco do mapa) abre a busca "Ir para talhão".</li><li>Cada talhão tem `aria-pressed` e o nome completo do pedido ("P5, 71 ha, cultura e estádio, valor, estado, data"); instruções visíveis e no `aria-describedby`.</li><li>O mapa não muda de zoom nem de centro sozinho; só a busca e "Localizar no mapa" enquadram.</li></ul> |
| **Dano evitado** | Pivôs inalcançáveis sem mouse (0 de 23); oito paradas de Tab num desenho só; painel que abre sem o leitor de tela saber. |
| **Teste** | `mapa_mux_f1_test.py` F1-1 a F1-4 e F1-7 |

### MUX-P3 · Cor honesta

| Item | Conteúdo |
|---|---|
| **Regra** | <ul><li>Sem leitura (nuvem, sem dado) em hachura; sem cultura em neutro; nunca a cor de um valor.</li><li>"Estimado" é a origem do valor: fica com a cor da classe e a etiqueta "≈ … estimado", nunca na hachura (NC10).</li><li>"Não se aplica" tem contorno tracejado `#6B776F`, nunca só a cor do fundo (D14).</li></ul> |
| **Dano evitado** | Ler falta de dado como condição; ler valor estimado como falta de leitura. |
| **Teste** | `mapa_mux_f2_test.py` K1 |

### MUX-P4 · Rótulo sobre placa e anéis em duas cores

| Item | Conteúdo |
|---|---|
| **Regra** | <ul><li>Dentro do talhão, no máximo 3 linhas (número / valor com unidade / estado curto); em escala pequena, só o número.</li><li>O valor e o estado ficam numa placa branca a 90 %, com texto opaco `#15201A`: ≥ 13,4:1 sobre qualquer fundo, e nenhum `opacity` no caminho do texto.</li><li>Seleção, foco, hover e realce da legenda em duas cores (escuro e branco: ≥ 3:1 sobre qualquer preenchimento); a seleção é contínua e forte, e o foco tracejado.</li></ul> |
| **Dano evitado** | Rótulo ilegível sobre a imagem; seleção que some sobre a cor da classe (NC11). |
| **Teste** | `mapa_mux_f2_test.py` K2 e S1 |

### MUX-P5 · Legenda que trabalha

| Item | Conteúdo |
|---|---|
| **Regra** | <ul><li>Cada classe é um botão com a contagem e a área ("foco · 2 · 137 ha").</li><li>Passar o mouse ou focar realça os talhões dela.</li><li>Clicar filtra o mapa e a lista: os outros esmaecem e a Lista mostra "N de M". Clicar de novo limpa.</li><li>O contêiner da legenda não pega o clique fora dos itens.</li><li>Escala relativa (Satélite no contraste Talhão; Solo fora do Absoluto) não conta nem filtra talhões: a cor do talhão não é uma classe dela. Sem cultura, sem laudo e nuvem contam.</li><li>No mapa estreito (≤ 700 px), a legenda é uma linha que rola de lado.</li></ul> |
| **Dano evitado** | Legenda decorativa; contar talhões de uma condição à mão; contagem que diz "Médio 20" quando os rótulos dizem fraco e bom; legenda que cobre metade do mapa no celular. |
| **Teste** | `mapa_mux_f2_test.py` L1 |

### MUX-P6 · Ver dados: Lista | Mapa no mesmo bloco

| Item | Conteúdo |
|---|---|
| **Regra** | <ul><li>A Lista tem os mesmos filtros, a mesma seleção e o mesmo painel do mapa.</li><li>Uma linha por talhão, com valor, estado em texto e data, do mais grave ao melhor, e "N de M".</li><li>A linha abre o painel (SEL-02, seta de ir da TAB-11); "Localizar no mapa" volta ao mapa com o talhão escolhido.</li><li>Em "Todas", a Lista traz as três fazendas.</li><li>Sem o MapLibre (CDN), a Lista continua e o aviso oferece "Tentar de novo".</li></ul> |
| **Dano evitado** | Mapa como único caminho, inalcançável para quem não enxerga ou não usa mouse (MAPUX-06, RF-WRK-004). |
| **Teste** | `mapa_mux_f1_test.py` F1-5, F1-6 e F1-10 |
| **Exceção registrada** | A Lista é peça própria: o motor de grade é estático e as linhas aqui mudam a cada camada. Ela migra para o componente comum no SAF-MAPA. |

### MUX-P7 · Endereço é estado

| Item | Conteúdo |
|---|---|
| **Regra** | <ul><li>`#faz=&lay=&t=&dt=` guarda fazenda, camada, talhão e data da cena; recarregar, voltar e o link compartilhado abrem o mesmo mapa.</li><li>Na Lagoa Grande, a câmera é guardada na sessão (voltar sem reenquadrar).</li><li>`#talhao=ID` troca a fazenda; ID inexistente avisa e não escolhe outro talhão.</li></ul> |
| **Dano evitado** | Voltar de outra tela e perder camada, data, seleção e zoom. |
| **Teste** | `mapa_mux_f1_test.py` F1-8, `mapa_mux_f0_test.py` F0-2 e `mapa_mux_unit.js` H |
