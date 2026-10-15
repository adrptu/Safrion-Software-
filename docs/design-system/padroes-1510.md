# Padrões do proprietário de 15/10/2026

Pedido do proprietário em 15/10/2026: "padronize no design system essas melhorias que definimos hoje".

Os padrões abaixo completam os de 09/10/2026 (BOT, SEL, ETP e VIS, em `docs/design-system/README.md` da `main`) sem contrariá-los. Valem para o protótipo e para o software real (`packages/ui`), como manda o AGENTS §4:
- tela nova já nasce assim;
- tela existente é corrigida pelo componente comum ou na varredura de conformidade.

A coluna "Situação" diz onde o padrão já está aplicado. O detalhe de AVI-01, TAB-05, TAB-06 e BOT-10 está em [aviso-e-menu-da-linha.md](aviso-e-menu-da-linha.md); o de ETP-02, em [fluxo-de-etapas.md](fluxo-de-etapas.md).

## Tabelas e visões

| ID | Regra | Por quê | Situação |
|---|---|---|---|
| TAB-01 | **Barra da visão em ordem fixa.** <ul><li>À esquerda: busca, filtros rápidos, filtros de coluna ativos e "Limpar filtros".</li><li>À direita: ferramentas da tela, "Agrupar por" e "Colunas", nesta ordem.</li><li>Filtro rápido é o estado da lista (Fase, Rotina, Prazo, Situação) e fica nessa barra, dentro da área da visão.</li><li>A faixa de filtros do topo da tela fica só com o contexto: Fazenda, Safra, Cultura e Talhão.</li></ul> Revê a FIL-02 da manhã de 15/10, que levava Fase, Rotina e Prazo para a faixa do topo. | Quem filtra a lista olha a lista. O contexto vale para a tela inteira | Toda tabela (`engine.grid`). O.S. e Manutenção com Fase, Rotina e Prazo na área da visão |
| TAB-02 | **Sem "x de y" quando há filtro rápido.** Cada filtro rápido já mostra a sua quantidade. Sem filtro rápido, a contagem fica, porque ajuda na busca. | Número repetido é ruído | Toda tabela (`engine.grid`) |
| TAB-03 | **Funil no cabeçalho da coluna.** <ul><li>O ícone é um funil vazado; com filtro ativo, fica cheio na cor de ação.</li><li>O nome acessível é fixo: "Filtrar &lt;coluna&gt;".</li><li>A dica acrescenta "· filtro ativo".</li></ul> | O ícone de filtro é reconhecido de imediato | Toda tabela (`engine.grid`, `g2lib`) |
| TAB-04 | **Seta de abrir e recolher (drill-down) sem dica.** O nome acessível continua para o leitor de tela ("Abrir …", "Recolher …"). | A seta é óbvia, e a dica cobria a linha de baixo | Toda tabela em árvore, Planos agronômicos e Manutenção |
| TAB-05 | **Ações da linha no ⋯.** <ul><li>Os botões de ação saem da célula e vão para o ⋯ da linha, cada um com um ícone do verbo.</li><li>"Excluir" vem por último, em vermelho, com a mesma confirmação.</li><li>O link que abre o registro (›) continua na célula: é o alvo único da BOT-07.</li></ul> | A tabela fica limpa. A ação continua a um toque | `engine.grid(..., menu_linha=True)`. Planejar safra › Talhões e cultivos. Demais tabelas na varredura |
| TAB-06 | **Alerta só dentro da tabela.** <ul><li>Na linha, o recurso em falta aparece como ⚠, com o detalhe na dica.</li><li>Nenhuma frase de alerta nem atalho fora da tabela.</li><li>O veredito continua para o leitor de tela.</li></ul> | O alerta aparece junto do que precisa ser corrigido | `engine.grid(..., sico_so_icone=True)`. Planejar safra › Operações e recursos |
| TAB-07 | **Sem cartões de resumo sobre a tela de trabalho** (lista, Kanban, Carga). As contagens ficam nos filtros rápidos e os totais na linha de total. Indicador em cartão é do Painel. | Cartão que repete a tabela empurra o trabalho para baixo | O.S. › Carga. Demais telas na varredura |
| VIS-05 | **Modos de visão em toda lista.** <ul><li>Toda lista tem Tabela e Cartões.</li><li>Kanban quando o registro anda por fases. Matriz, Mapa e Calendário quando o dado pede.</li><li>"Agrupar por" vale em toda visão que lista registros (Tabela, Cartões e Kanban), com o mesmo controle e o mesmo estado.</li></ul> | Cada pessoa vê do jeito que decide melhor, sem perder o agrupamento | Agrupar no Kanban: O.S. Tabela e Cartões nas demais listas: em aplicação |

## Escolha e seleção

| ID | Regra | Por quê | Situação |
|---|---|---|---|
| SEL-03 | **Lista suspensa do DS.** <ul><li>No computador, toda lista de escolha (`select`) abre a lista do design system: ✓ na opção escolhida, hover verde e teclado (↑ ↓ Home End Enter Esc).</li><li>No toque, fica a lista do próprio aparelho, que é melhor no celular.</li></ul> | Mesma aparência em todas as telas, inclusive Agrofit, Agrupar por e filtros | Toda página (`g2lib`, `g2dsel`) |
| SEL-04 | **Seleção em mais de uma fazenda.** Ao planejar a safra, a pessoa escolhe fazendas e talhões de várias fazendas de uma vez, de forma rápida e visual. Um talhão pode ficar sem plantio. | A safra real cruza fazendas. Talhão em pousio é decisão do produtor | Em aplicação. A regra final entra com a entrega |

## Ações, avisos e etapas

| ID | Regra | Por quê | Situação |
|---|---|---|---|
| AVI-01 | **Aviso de retorno pequeno e com tom.** <ul><li>A caixa tem até 420 px e pouco texto.</li><li>Feito: verde-claro com ✓.</li><li>Impedido ou a corrigir: âmbar-claro com ⚠.</li><li>O resto: branco com ⓘ.</li><li>O tom sai do próprio texto (`G2_TOAST_TOM`). A tela não escolhe cor.</li></ul> | A pessoa sabe na hora se deu certo, sem ler um parágrafo | Toda página (`engine.G2_TOAST`) |
| BOT-10 | **"Incluir" da linha de inclusão é verde.** A linha de inclusão (insumo na atividade, item no pedido) é um contexto da BOT-01, e o verde dela é o "Incluir". | É a ação que a pessoa veio fazer naquela linha | Planos agronômicos e Planejar safra |
| ETP-02 | **Fluxo de etapas em cartões clicáveis.** <ul><li>Cada etapa é um cartão com seta, e o cartão leva à etapa.</li><li>A etapa travada mostra o motivo e não navega.</li><li>Revoga o "a faixa só informa" de 03/10.</li></ul> | Ir direto à etapa sem voltar passo a passo | Planejar safra e Compras |
| VIS-01 (revisão) | **Separador só onde organiza.** <ul><li>Vale abaixo do cabeçalho da página, abaixo do título do bloco e entre blocos de assunto diferente.</li><li>Sem linha entre itens que o espaço já separa, sem linha dupla e sem moldura em volta de tudo.</li></ul> | Linha demais vira grade e cansa a leitura | Em aplicação |

## Verificação

| Comando | O que confere |
|---|---|
| `python3 ds_1510_test.py` (sem navegador, depois do build) | TAB-01 a TAB-04, AVI-01 e SEL-03 em todas as páginas geradas. Componente e uso de TAB-05 e TAB-06 |
| `ds_padrao_test.py` F | TAB-01: Fase, Rotina e Prazo da O.S. e da Manutenção na área da visão, e a faixa do topo só com o contexto |
| `saf_tab_test.py`, `saf_operacoes_test.py`, `ocupacao_test.py` | TAB-05 e TAB-06 no Planejar safra |
| `pa_lista_test.py` | BOT-10 e AVI-01 nos Planos |
| `acao_unica_test.py` 1, `componentes_test.py` 14 e 17, `etapas_celular_test.py` | ETP-02 |
| `tabelas_os_test.py`, `os_cenario_test.py` | Agrupar por no Kanban e Carga sem cartões |
