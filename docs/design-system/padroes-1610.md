# Padrões de 16/10/2026

Pedidos do proprietário em 16/10, transformados em padrão pelo método da skill `padrao-safrion` (`.claude/skills/padrao-safrion/SKILL.md`).

- **Valem para todas as telas do mesmo tipo**, no protótipo e no software real.
- **Teste:** `tools/prototipo/v37/gen37/ds_1610_test.py`.
- **Contraprova:** a versão publicada antes (a156f83) reprova.

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

## Mapa (frente MAPA-9)

> "no mapa em analise de solo, coloque icone para importar novo laudo"

**MAP-02:** com a camada Análises de solo, o ícone "Importar laudo" fica na faixa branca acima do mapa, à direita, junto dos outros botões.
