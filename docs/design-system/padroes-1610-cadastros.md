# Padrões de 16/10/2026 · Cadastros (frente CADASTROS-PADRAO)

- **O que é:** complemento de `padroes-1610.md`, seção "Em curso na frente CADASTROS-PADRAO", que reservou os IDs CAD-01 a CAD-03. Na integração, este texto entra lá.
- **Método:** skill `padrao-safrion` (inventário, peça comum, ID, teste com contraprova e fotos conferidas).
- **Alcance:** protótipo e software real (`packages/ui`).
- **Teste:** `tools/prototipo/v37/gen37/cadastros_padrao_test.py`.
- **Contraprova:** com `CONTRAPROVA=1` e `RENDER_DIR` apontando para o `_render` da base 6a23a88, a base reprova P1 a P4 e P6.

## CAD-01 · Cadastro no componente comum

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

## CAD-02 · Formulário de cadastro só com o essencial

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

**Prova:** tabela campo a campo em `docs/integracao/V71/cadastros-campos.md`.

**Dano evitado:** formulário longo, com campos que nenhuma tela usa, custa tempo e tira o foco de quem cadastra. Documento de banco misturado ao cadastro operacional aparece como pendência onde não trava nada.

**Teste:** `cadastros_padrao_test.py`, P6a a P6e.

## CAD-03 · Mãe e filhas numa lista só (fazendas e talhões)

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

**Dano evitado:** com a fazenda numa aba de cartões e os talhões em outra, a pessoa perdia a ligação entre a área da fazenda e a soma dos talhões e cadastrava talhão sem ver a fazenda.

**Teste:** `cadastros_padrao_test.py`, P5a a P5f:
- a árvore abre e fecha;
- a área cultivável da fazenda é a soma dos talhões;
- Criar fazenda e Incluir talhão funcionam.

## Fica para o motor (não é desta frente)

- **Linha de grupo das árvores:** a faixa clara e o hover #E8F3EC que a VIS-02 cita existiam só no `CADX_CSS`. Agora as árvores dos Cadastros ficam iguais às das outras telas (hover #F2F8F4 do motor). Se valer para todas as árvores, entra no `engine.py`.
- **"Próximo passo" do detalhe (BOT-02):** o motor não tem o bloco comum. No detalhe do talhão (CD-01det), a ação pendente ("Definir polígono da T1-B") ficou como primária do cabeçalho até o bloco existir.
