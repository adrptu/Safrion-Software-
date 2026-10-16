# Padrões de 16/10/2026

Pedidos do proprietário em 16/10, transformados em padrão pelo método da skill `padrao-safrion` (`.claude/skills/padrao-safrion/SKILL.md`).

- **Valem para todas as telas do mesmo tipo**, no protótipo e no software real.
- **Teste:** `tools/prototipo/v37/gen37/ds_1610_test.py`; TAB-09 e TAB-10 em `tab_drill_cab_test.py`; paridade dos módulos em `ds_modulos.py`.
- **Contraprova:** a versão publicada antes (a156f83) reprova; para TAB-09 e TAB-10, a 519ed7b.

## MET-01 · Método: pedido vira padrão

> "crie uma skill e metodologia de trabalho melhor, porque toda hora eu preciso ficar te corrigindo, sobre padrões e outros"

| Item | Conteúdo |
|---|---|
| **Regra** | Todo pedido visual ou de UX segue a skill `padrao-safrion`: inventário de todas as ocorrências, correção na peça comum, ID no catálogo, varredura com contraprova e fotos conferidas antes de publicar. |
| **Ferramentas** | <ul><li>`ds_inventario.py`: CSS de área sobre classe do motor, tabelas e cartões próprios, com catraca;</li><li>`galeria.py`: fotos por família de tela em 1440 e 390 px.</li></ul> |
| **Dano evitado** | Tela corrigida sozinha enquanto as do mesmo tipo seguem erradas; o proprietário volta a corrigir o mesmo desvio. |

## TAB-08 · Tabela padrão (substitui o visual anterior das tabelas)

> "padronize o visual desse modo de visao tabela em todos, mas adicionando nessa e nas demais o drill down e os icones em cada coluna de ordenação e filtro"

**Referência:** Planos agronômicos › Atividades do plano, modo Tabela.

**Regra:**
- A tabela tem moldura própria (borda de 1 px e raio de 12 px), alinhada à barra, e acaba na última linha.
- Cabeçalho em maiúsculas pequenas sobre o fundo da DS.
- Sem linha vertical.
- Linhas de 44 px.
- Toda coluna tem **⇅** (ordenar) e **funil** (filtrar por valores).
- Na 1ª célula, a **seta de abrir** (TAB-04):
  - **▸/▾** abre os itens ali mesmo;
  - **›** abre o detalhe.

**Celular (até 480 px):** "Agrupar por" e "Colunas" aparecem só com o ícone e o valor; o nome fica no `aria-label`. Assim a barra cabe numa linha com Tabela | Cartões, e a lista mostra pelo menos 5 linhas acima da dobra (AC-PCM-22).

**Peça única:**
- `E.cab_colunas_html` e `E.filtro_coluna_html`;
- `g2cabVals` e `g2cabAplica` no `g2lib`.

A tabela própria das Atividades do plano usa a mesma peça; não há cópia de estilo.

**Dano evitado:**
- tabela sem ordenar nem filtrar onde o usuário precisa achar a linha;
- linha que abre algo sem nenhum sinal;
- visual diferente entre telas iguais.

## VIS-06 · Cartões em linha

> "Nesses tipos de tela com finalidades similares, deixe o modo de visão do cartão igual de planos agronomicos, ficou muito mais bonito, organizado e produtivo ao usuário"

**Referência:** Atividades do plano, modo Cartões.

**Regra:**
- Um cartão por linha, com borda e raio de 12 px.
- Ordem dentro do cartão:
  1. seta à esquerda, quando há itens dentro (abre no próprio cartão);
  2. título;
  3. até 4 colunas, as mesmas e **alinhadas** em todos os cartões da lista;
  4. ⋯ no fim.
- Rótulos das colunas uma vez, no alto.
- Total alinhado às colunas.
- Agrupar por: título do grupo com as somas alinhadas.
- No estreito (até 640 px) os campos descem para baixo do título, com o rótulo.
- Vale nas 94 listas com Tabela | Cartões.

**Peça única:** `_cartoes_html` e `CARTOES_CSS` no motor; `g2cdVals` no `g2lib`.

**Dano evitado:** cartão em grade com rótulo repetido em cada caixa, que polui a tela e não deixa comparar valores lado a lado.

## AGR-02 · Agrupar sem trilha

> "tire esse todas => santa rita por talhão em todas telas. essa funcao ja esta nos filtros e no agrupamento"

**Regra:**
- O Agrupar por agrupa e a seta do grupo recolhe.
- O nome do grupo não "desce" e não há trilha ("Todas › Santa Rita por talhão").
- Quando o recorte tem um valor só no 1º nível (uma fazenda), o agrupamento já mostra o nível seguinte.
- O recorte é dos filtros.

**Dano evitado:**
- duas formas de recortar a mesma coisa (filtro e trilha), uma escondendo linhas sem aparecer nos filtros;
- texto a mais na barra.

## TAB-09 · Seta de abrir sempre na 1ª coluna

> "colone os icones de drill down sempre na esquerda, fica mais intuitivo em todas telas" (print: Planos agronômicos › Atividades do plano, a coluna DAP vinha antes da seta)

**Referência:** Atividades do plano, modo Tabela: a seta ▸/▾ abre a 1ª coluna, antes do DAP.

**Regra:**
- A seta de abrir (TAB-04: ▸/▾ abre ali; › abre o detalhe) é a primeira coisa da linha, à esquerda de qualquer outra coluna: número, caixa de seleção, ícone ou texto.
- Árvore e grupos: o recuo do nível continua; a seta do subnível fica no recuo, sempre antes do nome.
- Com seleção, a seta vem antes da caixa. A linha sem seta guarda o lugar (22 px), para as caixas ficarem alinhadas. Nos cartões, a coluna da seta vem antes da seleção.
- Seta de seção ou de item que abre ali (lotes da Qualidade, raia do Kanban da O.S., "Capacidade por mês") vem antes do nome.
- Lista suspensa ("Agrupar por ▾", escolha de alvos) não é seta de abrir: o ▾ continua no fim.

**Peça única:**
- motor: célula `c.carT` no `engine.grid`; o `g2lib` põe a seta na 1ª célula da linha;
- cartões: `_cartoes_html` e `_cdgtc` (seta, seleção, título);
- Atividades do plano: a seta na célula do gatilho (`pa-tb-gat`).

**Inventário na base (519ed7b):**
- a varredura achou 6 telas ou estados fora: Ordens de campo (CA-01), Ocorrências (CA-03) e Aprovações (IN-02), com a caixa antes da seta; Qualidade (CO-06), com a seta no fim do lote; Atividades do plano em Tabela, com o DAP antes;
- pelo código, mais 2: raia do Kanban da O.S. com Agrupar por e "Capacidade por mês" no Planejar safra, ambas com a seta no fim.

**Dano evitado:** a pessoa procura a seta num lugar diferente em cada tela, e a linha que abre fica sem o sinal no lugar de sempre.

**Teste:** `tab_drill_cab_test.py` parte A (148 telas e 4 estados por endereço, a 1440 e 390 px, no estado inicial, com "Expandir tudo" e no outro modo de Tabela | Cartões). O render da 519ed7b reprova.

**Oráculo mudado:** o B2 do `ds_1610_test.py` procurava a seta na célula do nome (`.g2c0`); agora procura na 1ª célula da linha, que é onde a TAB-09 a põe quando há seleção.

## TAB-10 · Cabeçalho de tabela com 40 px em todas as telas

> "padronize a altura das colunas cabeçalho das tabelas, em diferentes telas temos diferentes alturas."

**Regra:**
- Toda linha de cabeçalho de tabela tem 40 px: motor, tabelas próprias (Atividades do plano, Agrofit) e a ficha impressa da O.S.
- 40 px é a altura de duas linhas de rótulo no cabeçalho do motor, a mais comum na base (39,2 px em 86 telas a 1440 px).
- O rótulo ocupa até 2 linhas.
- Rótulo com mais de 26 letras ganha largura, até 180 px, para caber em 2 linhas.
- Se ainda assim não couber (coluna estreita no celular), termina em reticências. O nome inteiro continua no nome acessível ("Ordenar por …").

**Peça única** (`engine.TABELA_CSS`):
- `.g2th` na célula: `cab_colunas_html`, seleção e ação;
- `.g2thr` na linha das tabelas próprias: Agrofit, ficha da O.S. e tabela de adubação;
- `.g2hl` no rótulo;
- `--g2hbw` vem do `g2cabVals`.

**Inventário na base (519ed7b):**
- 1440 px: 7 alturas diferentes (de 22 a 64,4 px), com 69 telas fora de 40 px;
- 390 px: 9 alturas diferentes, com 65 telas fora.

Causas:
- rótulo quebrando em 3 ou 4 linhas (largura máxima de 104 px);
- motor com mínimo de 36 px, sem altura fixa;
- tabelas próprias sem mínimo: Atividades com 26,6 px, Agrofit com 22 px, ficha com 26,5 px;
- Cadastros com fonte de 12 px e linha de 13,5 px (CADX_CSS da frente Cadastros).

No celular, o cabeçalho das Atividades agora esconde Insumos e Custo/ha junto com as colunas. Antes ele quebrava em 2 linhas (53 px).

**Dano evitado:** a tabela muda de cara de uma tela para outra, e o rótulo em 3 ou 4 linhas empurra os dados para baixo.

**Teste:** `tab_drill_cab_test.py` parte B, que também conta os rótulos que terminam em reticências. O render da 519ed7b reprova.

## PAR-01 · Paridade dos módulos com o Agrícola

> "os demais módulos estão com design system diferente do nosso padrão de excelencia do módulo agrícola. Faça seu melhor e mantenha sempre o padrão para mim não ter que ficar cobrando toda vez."

**Regra:**
- Toda tela de todo módulo segue as regras que a tela de referência do Agrícola cumpre: cabeçalho, FIL-01, TAB-01 a TAB-10, VIS-05, VIS-06 e BOT-01.
- O módulo não ganha estilo próprio.

**Aplicado em 16/10 na peça comum:**
- **VIS-05 em toda lista do motor:** a lista com ordenar e filtrar ganha Tabela | Cartões. Antes eram só as do quadro `MODO_LISTAS` e as com colunas essenciais ou Agrupar por; agora são 237 das 247 grades. A matriz sem ordenar (capacidade por mês) fica só em Tabela.
- **VIS-06 nos cartões:**
  - o texto de apoio apagado da célula fica só na Tabela (a regra existia, mas não pegava, porque o desenho grava a cor em rgb);
  - as partes do valor ganham espaço entre si.

**Inventário e o que falta:** `docs/integracao/V72/DS-MODULOS.md`, com tela, regra, evidência e a mudança exata, inclusive nos arquivos da frente Cadastros.

**Teste e catraca:** `ds_modulos.py` mede 9 regras em 148 telas; `--catraca` reprova se a contagem de alguma regra subir em algum módulo (base em `ds_modulos_base.json`).

**Dano evitado:**
- módulo com cara diferente do Agrícola;
- desvio corrigido que volta na tela seguinte sem ninguém ver.

## Em curso na frente CADASTROS-PADRAO

> "todas telas de cadastro estao fora do nosso padrão"; "elimine campos dos formularios de cadastro que não sejam essenciais à gestão. documentos para credito podemos deixar tudo separado em outro lugar"; "fazendas e talhoes na mesma tela, conectados e intuitivos"

**CAD-01:**
- Cadastros sem camada de estilo própria (o `CADX_CSS` de 01/10 sai).
- "Cadastrar …" verde no cabeçalho da tela (BOT-01).
- Barra na ordem da TAB-01.

**CAD-02:**
- Formulário só com o essencial, com prova de uso de cada campo.
- Documentos para crédito vão para o módulo Crédito.

**CAD-03:** Fazendas e talhões numa lista só, em árvore: a fazenda com os talhões dentro.

## Mapa (frente MAPA-9, juntada em f27811b)

> "no mapa em analise de solo, coloque icone para importar novo laudo. (no topo do mapa, a direita na parte branca onde ja ficam demais botoes acima do mapa)"; "a barra de icones do mapa por estar do lado da barra lateral de icones dos modulos, nao fica legal, melhore esses icones do mapa de lugar"

**MAP-02 · Importar laudo no mapa:**
- Com a função Solo, o ícone "Importar laudo de análise de solo" é o último das ferramentas no topo do mapa, à direita.
- Tem 32 px no mouse e 44 px no toque, com dica e `aria-label`.
- Abre o mesmo "Registrar laudo" do AG-02, com a fazenda e o talhão do mapa já escolhidos (`#registrar=<fazenda>`).

**MAP-03 · Funções do mapa numa barra horizontal com nome (VISOES-ROT):**
- As 9 funções (DEC-1610-09) ficam no alto do bloco do mapa, com ícone e nome; a coluna ao lado do menu de módulos saiu.
- Usa o seletor de visões da DS na variante com nome (`engine.VISOES_CSS`), em abas com `aria-selected`.
- A 390 px a barra rola dentro dela, com a função ativa à vista.
- O bloco do mapa ocupa a altura que sobra da janela: a fazenda inteira cabe em 1440 × 900.
- Inventário: o IN-04 era a única tela com coluna de ícones ao lado do menu.

**Teste:** `mapa9_test.py` (13/13; a base reprova 8 e para no ícone que não existe).

**MAP-04 · Faixa branca da função com a mesma altura em todas** (16/10: "deixe a espessura da parte branca da opção solo igual aos demais, manter um padrão visual"):
- No computador, uma linha só (52 px) em todas as funções e larguras: filtros inteiros à esquerda; números, atalho e ações à direita, no espaço que sobra.
- Número que não cabe rola dentro da própria faixa; nunca desce para uma 2ª linha. Seletor da faixa com até 150 px.
- No celular (≤ 760 px), sempre duas linhas: filtros e números, cada uma com rolagem própria.
- Causa: a faixa quebrava linha quando os números não cabiam (Solo a 1440; Pragas e O.S. a 1280).

**FIL-01 · Faixa de filtros só pela peça comum** (16/10: "não falta o símbolo do filtro que é nosso padrão?"): toda faixa que filtra dados usa `ui37.faixa_filtros` (funil, rótulo e controles). A faixa das fazendas do Planejar safra era desenho próprio, sem funil; agora usa a peça comum. Inventário: era a única faixa de filtros montada à mão.

**Teste:** `mapa_faixa_test.py` (25/25: 2 fazendas × 9 funções × 1440, 1280, 1024 e 390; mais a faixa do Planejar safra). O render de ff3903d reprova 15 (Solo 78 px contra 47; sem funil).

**Dano evitado:**
- duas colunas de ícones lado a lado, que se confundem;
- importar laudo exigir sair do mapa e achar o talhão de novo.
