# Padrões de 16/10/2026

Pedidos do proprietário em 16/10, transformados em padrão pelo método da skill `padrao-safrion` (`.claude/skills/padrao-safrion/SKILL.md`).

- **Valem para todas as telas do mesmo tipo**, no protótipo e no software real.
- **Teste:** `tools/prototipo/v37/gen37/ds_1610_test.py`; TAB-09 e TAB-10 em `tab_drill_cab_test.py`; TAB-11 em `seta_padrao_test.py`; paridade dos módulos em `ds_modulos.py`.
- **Contraprova:** a versão publicada antes (a156f83) reprova; para TAB-09 e TAB-10, a 519ed7b; para TAB-11, a c9ffa08.

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
- Na 1ª célula, a **seta de abrir** (TAB-04), com o desenho único da TAB-11:
  - a seta que gira abre os itens ali mesmo;
  - a mesma seta, parada, abre o detalhe.

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

**Referência:** Atividades do plano, modo Tabela: a seta abre a 1ª coluna, antes do DAP.

**Regra:**
- A seta de abrir (TAB-04; desenho e alvo da TAB-11: gira e abre ali, ou leva ao detalhe) é a primeira coisa da linha, à esquerda de qualquer outra coluna: número, caixa de seleção, ícone ou texto.
- Árvore e grupos: o recuo do nível continua; a seta do subnível fica no recuo, sempre antes do nome.
- Com seleção, a seta vem antes da caixa. A linha sem seta guarda o lugar (a largura do alvo da TAB-11), para as caixas ficarem alinhadas. Nos cartões, a coluna da seta vem antes da seleção.
- Seta de seção ou de item que abre ali (lotes da Qualidade, raia do Kanban da O.S., "Capacidade por mês") vem antes do nome.
- Lista suspensa ("Agrupar por ▾", escolha de alvos) não é seta de abrir: o ▾ continua no fim.

**Peça única:**
- motor: célula `c.carT` no `engine.grid`; o `g2lib` põe a seta na 1ª célula da linha;
- cartões: `_cartoes_html` e `_cdgtc` (seta, seleção, título);
- Atividades do plano: a seta na célula do gatilho (`pa-tb-gat`).

**Inventário na base (519ed7b):**
- a varredura achou 7 telas ou estados fora: Ordens de campo (CA-01), Ocorrências (CA-03) e Aprovações (IN-02), com a caixa antes da seta; Qualidade (CO-06), com a seta no fim do lote; Atividades do plano em Tabela (2 estados), com o DAP antes; Planejar safra › operações, com "Capacidade por mês ▾";
- pelo código, mais 1: a raia do Kanban da O.S. com Agrupar por, com a seta no fim.

**Dano evitado:** a pessoa procura a seta num lugar diferente em cada tela, e a linha que abre fica sem o sinal no lugar de sempre.

**Teste:** `tab_drill_cab_test.py` parte A (148 telas e 4 estados por endereço, a 1440 e 390 px, no estado inicial, com "Expandir tudo" e no outro modo de Tabela | Cartões). O render da 519ed7b reprova.

**Oráculo mudado:** o B2 do `ds_1610_test.py` procurava a seta na célula do nome (`.g2c0`); agora procura na 1ª célula da linha, que é onde a TAB-09 a põe quando há seleção.

## TAB-10 · Cabeçalho de tabela com 40 px em todas as telas

> "padronize a altura das colunas cabeçalho das tabelas, em diferentes telas temos diferentes alturas."

**Regra:**
- Toda linha de cabeçalho de tabela tem 40 px: motor, tabelas próprias (Atividades do plano, Agrofit) e a ficha impressa da O.S.
- 40 px é a altura de duas linhas de rótulo no cabeçalho do motor, a mais comum na base (39,2 px em 86 telas a 1440 px).
- O rótulo ocupa até 2 linhas.
- Rótulo cuja melhor quebra em 2 linhas não cabe em 104 px ganha a largura dessa quebra, medida no texto como desenhado, até 200 px.
- Se ainda assim não couber (coluna estreita no celular), termina em reticências. O nome inteiro continua no nome acessível ("Ordenar por …").

**Peça única** (`engine.TABELA_CSS`):
- `.g2th` na célula: `cab_colunas_html`, seleção e ação;
- `.g2thr` na linha das tabelas próprias: Agrofit, ficha da O.S. e tabela de adubação;
- `.g2hl` no rótulo;
- `--g2hbw` vem do `g2cabVals`.

**Inventário na base (519ed7b):**
- 1440 px: 7 alturas diferentes (de 22 a 64,4 px), com 70 telas fora de 40 px;
- 390 px: 9 alturas diferentes, com 68 telas fora.

Causas:
- rótulo quebrando em 3 ou 4 linhas (largura máxima de 104 px);
- motor com mínimo de 36 px, sem altura fixa;
- tabelas próprias sem mínimo: Atividades com 26,6 px, Agrofit com 22 px, ficha com 26,5 px;
- Cadastros com fonte de 12 px e linha de 13,5 px (CADX_CSS da frente Cadastros).

No celular, o cabeçalho das Atividades agora esconde Insumos e Custo/ha junto com as colunas. Antes ele quebrava em 2 linhas (53 px).

**Dano evitado:** a tabela muda de cara de uma tela para outra, e o rótulo em 3 ou 4 linhas empurra os dados para baixo.

**Teste:** `tab_drill_cab_test.py` parte B, que também conta os rótulos que terminam em reticências: nenhum a 1440 px e 30 a 390 px, em coluna estreita. O render da 519ed7b reprova.

## TAB-11 · Seta única de abrir e de ir

> "mude o estilo do drill down daquele preto para a setinha mais intuitiva e amigável dos debaixo, melhore ela e implemente como nosso padrão em tudo" (captura do CD-01: o grupo "Santa Rita" com o triângulo preto ▾ e os talhões com a seta fina cinza ›)

**Referência:** a seta fina das linhas filhas do CD-01 (talhões), agora a única.

**Regra:**
- **Um só desenho em todas as telas:** chevron fino em SVG (16 px, traço de 1,75 px, pontas arredondadas), na cor do texto secundário (#65736A). Nunca o triângulo cheio de texto (▸ ▾ ▶) nem preto.
- **Abrir e recolher ali mesmo** (a linha tem filhos, a seção tem conteúdo):
  - fechada aponta para a direita; aberta gira 90° para baixo;
  - o giro leva 120 ms e não anima com `prefers-reduced-motion`;
  - o controle é um botão nativo com `aria-expanded` e o nome "Abrir …" / "Recolher …"; ou o botão inteiro com o nome à vista (seção da Manutenção e da O.S., lote da Qualidade, "Capacidade por mês", `summary`), com a seta antes do nome.
- **Ir para o detalhe** (TAB-08): a mesma seta para a direita, sem girar; quem navega é a linha ou o link.
- **"Expandir tudo" / "Recolher tudo":** a mesma seta, no estado das linhas (direita com linhas recolhidas; baixo com tudo aberto).
- **Alvo:** 24 × 24 px no mouse, 44 × 44 px no toque, sem cobrir o controle vizinho. A seta de ir e a linha sem seta guardam a mesma largura, para os nomes alinharem.
- **Interação:** hover verde (VIS-02: fundo #E4F3E9 e seta #1E7A4C); anel de foco verde de 2 px; Enter e Espaço alternam sem abrir o painel da linha. Alinhada ao centro da linha, na 1ª coluna, antes do nome (TAB-09).
- **Sem dica**, como a TAB-04 (15/10: "a seta é óbvia, e a dica cobria a linha de baixo"); o nome fica para o leitor de tela.
- **Fora:** a lista suspensa (o ▾ continua no fim de "Agrupar por", TAB-09), a ordenação do cabeçalho (⇅ ▲ ▼), o › de trilha e de texto corrido e o › no fim de atalho de texto ("Planejar ›", BOT-08).

**Peça única:**
- HTML: `engine.seta`, `engine.seta_abrir`, `engine.seta_ir`, `engine.SETA_VAZIO` e `engine.SETA_CSS`;
- JS: `g2seta(aberta, nome)` no `g2lib` (estado e nome acessível); o desenho é sempre o do HTML, e nenhum estado da tela carrega glifo.

**Aplicado em:** motor (Tabela, árvore, Agrupar por, Cartões, "Expandir tudo"), Atividades do plano (Tabela e Cartões), Planejar safra ("Capacidade por mês" e ajuste local do plano), Manutenção (blocos do ativo e da ordem, serviços do plano e Versões), Qualidade (lotes do CO-06), painel da O.S. (seções) e laudo de solo (`summary` "Ver original").

**Inventário na base (c9ffa08):**
- 35 triângulos de abrir no código de produto (19 ▸ e 16 ▾), em 6 arquivos: motor (`g2lib`), Atividades do plano, Planejar safra, Manutenção e Qualidade; os 9 ▾ de lista suspensa ficam;
- 5 desenhos para o mesmo gesto: o triângulo de texto preto (13 px), a seta cinza da linha de ir (14 px, #9AA59E), as duas setas do painel da O.S., as setas de "Expandir tudo" e o marcador nativo do `summary`;
- detalhe, números depois e pendências em `docs/integracao/V73/SETA-PADRAO.md`.

**Dano evitado:** dois desenhos para o mesmo gesto (o triângulo preto chama mais atenção que o conteúdo e parece outra função), alvo pequeno no celular e tela nova voltando ao glifo solto.

**Teste:** `seta_padrao_test.py` (148 telas e 9 estados por endereço, a 1440 e 390 px, no estado inicial, com "Expandir tudo" e no outro modo): A sem triângulo de texto; B todo controle de abrir com o componente; C uma seta só (cor, tamanho e traço computados); D giro coerente com o `aria-expanded`; E Enter e Espaço com foco visível; F alvo. O render da c9ffa08 reprova.

## PAR-01 · Paridade dos módulos com o Agrícola

> "os demais módulos estão com design system diferente do nosso padrão de excelencia do módulo agrícola. Faça seu melhor e mantenha sempre o padrão para mim não ter que ficar cobrando toda vez."

**Regra:**
- Toda tela de todo módulo segue as regras que a tela de referência do Agrícola cumpre: cabeçalho, FIL-01, TAB-01 a TAB-10, VIS-05, VIS-06 e BOT-01.
- O módulo não ganha estilo próprio.

**Aplicado em 16/10 na peça comum:**
- **VIS-05 em toda lista do motor:** a lista com ordenar e filtrar ganha Tabela | Cartões. Antes eram só as do quadro `MODO_LISTAS` e as com colunas essenciais ou Agrupar por (82 de 247 grades); agora são 240 de 250. A matriz sem ordenar (capacidade por mês) fica só em Tabela.
- **VIS-06 nos cartões:**
  - o texto de apoio apagado da célula fica só na Tabela (a regra existia, mas não pegava, porque o desenho grava a cor em rgb);
  - as partes do valor ganham espaço entre si.

**Inventário e o que falta:** `docs/integracao/V72/DS-MODULOS.md`, com tela, regra, evidência e a mudança exata, inclusive nos arquivos da frente Cadastros.

**Teste e catraca:** `ds_modulos.py` mede 9 regras em 148 telas; `--catraca` reprova se a contagem de alguma regra subir em algum módulo (base em `ds_modulos_base.json`).

**Dano evitado:**
- módulo com cara diferente do Agrícola;
- desvio corrigido que volta na tela seguinte sem ninguém ver.

## Cadastros (frente CADASTROS-PADRAO)

- **Teste:** `tools/prototipo/v37/gen37/cadastros_padrao_test.py`.
- **Contraprova:** com `CONTRAPROVA=1` e `RENDER_DIR` apontando para o `_render` da base 6a23a88, a base reprova P1 a P4 e P6.

### CAD-01 · Cadastro no componente comum

> "todas telas de cadastro estao fora do nosso padrão"

**Regra:**
- **Nenhum CSS de área sobre classe do motor.** Valem tabela, barra, cartões, abas e bloco do motor (`engine.grid`, seletor segmentado `engine.SEG_ON` e `SEG_OFF`, bloco igual ao da O.S. e do Estoque).
- **A primária fica no cabeçalho da tela, à direita do título** (BOT-01).
  - Leva o verbo **Criar** e o "+" (BOT-03 e BOT-05), o mesmo desenho do "Criar plano".
  - Com abas, o rótulo segue a aba ativa.
  - A aba que não cria (Cobertura de cotação, Ambiental, Água) fica sem verde.
  - O que só leva a outra tela é link secundário (BOT-08).
- **Barra da tabela na ordem da TAB-01, numa linha a 1440 px:**
  - à esquerda, a busca, os filtros (Função, papel) e o filtro rápido no lugar do motor;
  - à direita, nesta ordem: ferramentas da tela (Importar do ERP, Comparar com o realizado, Lista | Mapa), Expandir tudo, Agrupar por, Colunas e Tabela | Cartões.
  - Sem "x de y" quando há filtro rápido (TAB-02).
- **O que pede atenção fica na linha** (TAB-06):
  - um selo com o próximo passo;
  - o motivo na dica (máquina bloqueada, documento da água a renovar);
  - o filtro rápido "A resolver" com a contagem.
  - Sem faixa de cartões sobre a lista (TAB-07).
- **Entidade que só tinha cartões próprios passa à grade do motor** com Tabela | Cartões (VIS-05): Equipes e Conjuntos. As Fazendas entram na árvore da CAD-03.

**Verbo:** a fala da reserva dizia "Cadastrar …". O padrão escrito (BOT-03, 09/10) manda **Criar** para registro novo e independente, com o talhão como exemplo, e foi seguido. O título do painel continua o nome ("Cadastrar talhão"), como "Nova ordem" na O.S.

**Dano evitado:** a camada de estilo de 01/10 (`CADX_CSS`, 15 regras sobre o motor) anulava toda melhoria do motor nos Cadastros. O proprietário tinha de pedir de novo, tela a tela.

**Referência visual:** Ordem de Serviço (cabeçalho com "Criar ordem") e Estoque › Recebimentos (bloco, barra e tabela do motor).

**Teste:** `cadastros_padrao_test.py`, P1 a P4. O `ds_inventario.py` mostra os Cadastros com css 0 e cartão 0, com catraca.

### CAD-02 · Formulário de cadastro só com o essencial

> "elimine campos dos formularios de cadastro que não sejam essenciais à gestão. documentos para credito podemos deixar tudo separado em outro lugar para nao perder foco e produtividade"

**Regra:**
- **Um campo fica no formulário de cadastro quando:**
  - alimenta cálculo, regra, trava ou outro módulo;
  - é exigido por lei ou documento fiscal;
  - ou identifica o registro (inclui coluna, filtro e busca).
- **Sai quando** não muda decisão e ninguém lê.
- **Campo calculável é calculado** (ex.: o fuso vem da UF).
- **Documentos para crédito vivem no Crédito** › Documentos para crédito: CAR, matrícula, módulos fiscais, contrato de arrendamento, certidões e o que o credor pedir. No cadastro sobra, no máximo, o vínculo "Documentos para crédito ›".
- **Documento que trava operação agrícola fica onde a regra o usa:** a outorga de água, no CD-01 › Água, que a Irrigação lê.
- **O documento movido segue a entidade pelo id estável dela, nunca pelo nome** (revisão do Codex 6220145128). Fonte única: `credito_docs.js`.
  - O Crédito mostra o nome, a posse e as fazendas do cadastro atual: fazenda criada no CD-01 já tem CAR e matrícula a informar e entra no seletor.
  - O que foi preenchido no formulário antigo migra uma vez, sem sobrescrever o que já foi editado no Crédito, e sai do cadastro.
  - A edição no Crédito é gravada por id do documento: recarregar não reverte nem duplica.
  - Documento automático (CAR, matrícula e contrato da fazenda) tem o tipo e a fazenda fixos: só leitura com o motivo no formulário, e o comando recusa a mudança. Documento incluído pela pessoa continua editável (revisão do Codex 6221423767).
  - Só vale como salvo o que o navegador gravou. Se a gravação falha, nada é confirmado e o formulário volta com o rascunho e o motivo (ponto transacional do motor, como no `cad_gravacao_falha`).

**Prova:** tabela campo a campo em `docs/integracao/V71/cadastros-campos.md`.

**Dano evitado:** formulário longo, com campos que nenhuma tela usa, custa tempo e tira o foco de quem cadastra. Documento de banco misturado ao cadastro operacional aparece como pendência onde não trava nada.

**Teste:** `cadastros_padrao_test.py`, P6a a P6e; `cadastros_rev1_test.py`, R1a a R1f, R3a, R3b e R4a a R4c.

### CAD-03 · Mãe e filhas numa lista só (fazendas e talhões)

> "fazendas e talhoes na mesma tela, conectados e intuitivos"

**Regra:** quando uma entidade contém a outra (fazenda e talhões), a lista é uma árvore só, na grade do motor.

- **Linha-pai: a mãe.**
  - Nome e, nas linhas apagadas de baixo, a empresa e o município (cada um na sua linha, sem quebra no meio do nome).
  - Área total, área cultivável (soma das filhas ativas) e "Talhões" (só os ativos, dito na ajuda do cabeçalho).
  - Posse (com o fim do contrato na linha apagada) e situação.
  - O clique abre o painel da mãe.
- **Com todas as colunas, a árvore cabe na caixa a 1440 px** (TABELAS-FOCO A1): a situação, a posse e o nome quebram linha; o selo é curto ("Incompleto") e o que falta vai na dica.
- **Filhas nas linhas de baixo,** com a seta de abrir (TAB-04, desenho da TAB-11). O clique abre a filha.
- **A primária do cabeçalho cria a mãe** ("Criar fazenda").
- **A filha se inclui de dentro da mãe:** "Incluir talhão" no painel da fazenda, ou na própria linha quando a fazenda está vazia (BOT-03).
- **As outras entidades da tela continuam em abas** (Ambiental, Água).
- **A mãe também é registro no filtro rápido** (revisão do Codex 6220145128):
  - "A resolver" e "Inativos" alcançam a mãe pela situação dela, sem somar área e sem inventar filha;
  - a mãe que passa sozinha aparece recolhida, e as filhas em dia ficam fora da lista filtrada;
  - a filha que passa traz a mãe como contexto;
  - "Todos", a contagem e a aba contam mães e filhas; voltar a "Todos" devolve a abertura de antes.

**Dano evitado:** com a fazenda numa aba de cartões e os talhões em outra, a pessoa perdia a ligação entre a área da fazenda e a soma dos talhões e cadastrava talhão sem ver a fazenda.

**Teste:** `cadastros_padrao_test.py`, P5a a P5f:
- a árvore abre e fecha;
- a área cultivável da fazenda é a soma dos talhões;
- Criar fazenda e Incluir talhão funcionam.

E `cadastros_rev1_test.py`, R2a a R2e: "A resolver" com fazenda incompleta sem e com talhões, o contexto do talhão pendente, "Todos", teclado e 390 px.

### Fica para o motor (não é desta frente)

- **Linha de grupo das árvores:** a faixa clara e o hover #E8F3EC que a VIS-02 cita existiam só no `CADX_CSS`. Agora as árvores dos Cadastros ficam iguais às das outras telas (hover #F2F8F4 do motor). Se valer para todas as árvores, entra no `engine.py`.
- **"Próximo passo" do detalhe (BOT-02):** o motor não tem o bloco comum. No detalhe do talhão (CD-01det), a ação pendente ("Definir polígono da T1-B") ficou como primária do cabeçalho até o bloco existir.

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

## Entrada rápida (frente SAF-LOTE)

> "coloque um botao para poder editar de uma vez todos talhoes de uma fazenda numa tela só. como no outro anexo. todos inputs do usuário no sistema devem ser mais rápido e fácil."

O "outro anexo" é o painel "Dividir T1 em parcelas" (grade editável com a soma conferida). Detalhe, números e testes: `docs/integracao/V73/SAF-LOTE.md`; próximas telas: `docs/integracao/V73/ENTRADA-RAPIDA.md`.

### EDL-01 · Editar em lote numa grade

**Regra:** quando a tela lista N itens do mesmo tipo com os mesmos campos, ela oferece a edição em grade, num painel largo do mesmo desenho do Dividir.
- **Onde fica a ação:** secundária, verbo "Editar <itens>…", no título do bloco (com um contexto só) ou na faixa de cada contexto (uma fazenda por faixa, também no modo Cartões). Nunca uma segunda primária.
- **Grade:** uma linha por item; os filhos (parcelas) recuados embaixo do pai; as colunas do formulário do item; uma coluna Situação curta com o motivo na dica e o link do que trava.
- **Navegação de planilha:** Tab e Shift+Tab nas colunas; Enter ou ↓ desce e Shift+Enter ou ↑ sobe na mesma coluna; Esc fecha e, com alteração, pergunta antes.
- **Aplicar aos marcados:** caixa em cada linha e "todas"; uma faixa com os mesmos campos da linha, preenchidos uma vez, vale para as linhas marcadas. Preenche só onde pode e diz quantas recusou e por quê.
- **Colar do Excel/Planilhas:** bloco (tabulação e quebra de linha) a partir da célula focada, com conversão (vírgula decimal, datas dd/mm/aaaa e dd/mm) e o resumo "Colados 3 × 2: 6 células; 2 recusados (motivo)". Célula vazia do bloco não apaga.
- **Nada é salvo antes do "Salvar alterações (N)":** o contador diz quantas células mudaram, as alteradas ficam destacadas (borda âmbar), e o selo do resumo diz "N alterações não salvas".
- **Mesmas regras e mesmo caminho de gravação do formulário do item** (uma fonte só, ENG-011). A gravação é atômica por contexto (fazenda), com a chave do comando gerada ao abrir: o duplo clique não duplica. Falha ou conflito (outra aba mudou o que a grade mostra) não grava nada e mantém o rascunho.
- **Celular:** cada linha vira um bloco com os mesmos campos em duas colunas e o rótulo em cima; alvos de 44 px; barra de salvar fixa; sem rolagem de lado. A faixa "Aplicar" mostra os campos quando há linha marcada.
- **Peça própria sem tabela:** é uma grade de edição, como o Dividir (sem ordenar nem filtrar, sem `role=table`, sem CSS sobre classe do motor). A lista continua sendo a do motor.

**Dano evitado:** abrir, preencher e salvar um painel por item quando os itens são muitos e os campos são os mesmos (no cenário medido, 29 cliques e 64 teclas viram 11 cliques e 30 teclas, ou 3 cliques e 2 teclas colando o bloco da planilha; ver SAF-LOTE.md).

**Referência e teste:** Planejar safra › Cultivos e planos › "Editar talhões…" (`safra_lote.js`, `areas/saf_lote.py`). `saf_lote_test.py` (1440 e 390 px) e `saf_lote_unit_test.py` (colar, datas, número e recusas no node). A base c9ffa08 reprova (sem o botão).

### INP · Entrada rápida (todo campo do sistema)

| ID | Regra | Onde já vale | Prova |
|---|---|---|---|
| INP-01 | **Contexto herdado e visível.** A tela já sabe a organização, a fazenda, a safra, o talhão e a ordem: o painel diz o contexto no título e não pede de novo. Corrigível onde faz sentido. | Planejar safra (título "Editar talhões da Santa Rita", "Safra 2026/27 · Santa Rita") | `saf_lote_test.py` A2 |
| INP-02 | **Campo calculável não se digita.** Área do talhão inteiro (cadastro CD-01), área livre (ocupação), primeiro plantio possível, totais e selos vêm calculados; a célula fica só leitura com o motivo. | Editar talhões (área do talhão inteiro e da área livre) | `saf_lote_test.py` G8, `saf_lote_unit_test.py` slPode |
| INP-03 | **Teclado numérico com a unidade à vista.** Quantidade, área, dose e meta abrem o teclado decimal (`inputmode=decimal`), aceitam "1.234,5" e mostram a unidade ao lado (ha, sc/ha, t/ha/ano). | Formulário do motor (já tinha), Dividir, Editar talhões | `saf_lote_test.py` B4 |
| INP-04 | **Número selecionado ao receber o foco** pelo toque ou pela navegação da tela: o número digitado substitui o anterior. O clique do mouse põe o cursor onde a pessoa clicou; o Tab já seleciona no navegador. | Toda página (`g2lib.js`, `g2inp`) | `saf_lote_test.py` B1 e I1 |
| INP-05 | **Datas com atalho.** dd/mm sem ano assume o ano que cai dentro da safra; aceita ddmm, ddmmaaaa e dd/mm/aa; data que não existe é recusada com o formato. | Colar e aplicar no Editar talhões | `saf_lote_unit_test.py` slData |
| INP-06 | **Lista curta em um toque; catálogo com busca.** Cultura em lista (a letra inicial escolhe), variedade com sugestão do cadastro e da safra, plano só da cultura da linha. | Editar talhões | `saf_lote_test.py` C1, D3 |
| INP-07 | **Número, data e código sem corretor ortográfico nem maiúscula automática** (placa, lote, nota, CPF, CNPJ, chassi, série, matrícula, CAR). | Toda página (`g2lib.js`, `g2inp`) | `saf_lote_test.py` B4 e I1 |
| INP-08 | **Enter avança só em grade de edição.** Na grade, Enter desce na coluna, como na planilha. Em formulário, o Enter não muda: não envia nem salva sem querer. | Editar talhões | `saf_lote_test.py` B1 e B2 |
| INP-09 | **Colar em bloco** da planilha, com conversão e resumo do que entrou e do que foi recusado (EDL-01). | Editar talhões | `saf_lote_test.py` D1 a D4 |
| INP-10 | **Nunca o último valor** para lote, dose, quantidade e autorização (AGENTS §3.3). Sugestão só de contexto (variedade e plano mais usados na safra, primeiro plantio possível), sempre destacada como alteração. A meta nunca é sugerida. | Editar talhões, Planejar ›, Planejar talhões livres | `saf_lote_unit_test.py` slTrocaCult |
| INP-11 | **Erro junto ao campo.** A célula com problema fica destacada, a mensagem fica na linha, e a recusa é atômica: o que foi digitado continua. | Formulário do motor (já tinha), Dividir, Editar talhões | `saf_lote_test.py` C3 e E1 |

**Dano evitado:** digitar de novo o que a tela já sabe, apagar dígito a dígito, corretor trocando código ou número, data digitada em formato que a tela não aceita e Enter que envia sem querer.
