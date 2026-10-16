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
- **Filhas nas linhas de baixo,** com a seta ▸/▾ (TAB-04). O clique abre a filha.
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

**Dano evitado:**
- duas colunas de ícones lado a lado, que se confundem;
- importar laudo exigir sair do mapa e achar o talhão de novo.
