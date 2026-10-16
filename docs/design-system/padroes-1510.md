# Padrões do proprietário de 15/10/2026

Pedido do proprietário em 15/10/2026: "padronize no design system essas melhorias que definimos hoje".

Os padrões abaixo completam os de 09/10/2026 (BOT, SEL, ETP e VIS, em `docs/design-system/README.md` da `main`) sem contrariá-los. Valem para o protótipo e para o software real (`packages/ui`), como manda o AGENTS §4:
- tela nova já nasce assim;
- tela existente é corrigida pelo componente comum ou na varredura de conformidade.

A coluna "Situação" diz onde o padrão já está aplicado. O detalhe de AVI-01, TAB-05, TAB-06 e BOT-10 está em [aviso-e-menu-da-linha.md](aviso-e-menu-da-linha.md); o de ETP-02, em [fluxo-de-etapas.md](fluxo-de-etapas.md).

## Tabelas e visões

| ID | Regra | Por quê | Situação |
|---|---|---|---|
| TAB-01 | **Barra da visão em ordem fixa.** <ul><li>À esquerda: busca, filtros rápidos, filtros de coluna ativos e "Limpar filtros".</li><li>À direita: ferramentas da tela, "Expandir tudo" (só em árvore ou grupos), "Agrupar por", "Colunas" e o seletor Tabela | Cartões, nesta ordem. O modo de visão fica sempre na ponta (16/10).</li><li>Filtro rápido é o estado da lista (Fase, Rotina, Prazo, Situação) e fica nessa barra, dentro da área da visão.</li><li>A faixa de filtros do topo da tela fica só com o contexto: Fazenda, Safra, Cultura e Talhão.</li></ul> Revê a FIL-02 da manhã de 15/10, que levava Fase, Rotina e Prazo para a faixa do topo. | Quem filtra a lista olha a lista. O contexto vale para a tela inteira | Toda tabela (`engine.grid`). O.S. e Manutenção com Fase, Rotina e Prazo na área da visão |
| TAB-02 | **Sem "x de y" quando há filtro rápido.** Cada filtro rápido já mostra a sua quantidade. Sem filtro rápido, a contagem fica, porque ajuda na busca. | Número repetido é ruído | Toda tabela (`engine.grid`) |
| TAB-03 | **Funil no cabeçalho da coluna.** <ul><li>O ícone é um funil vazado; com filtro ativo, fica cheio na cor de ação.</li><li>O nome acessível é fixo: "Filtrar &lt;coluna&gt;".</li><li>A dica acrescenta "· filtro ativo".</li></ul> | O ícone de filtro é reconhecido de imediato | Toda tabela (`engine.grid`, `g2lib`) |
| TAB-04 | **Seta de abrir e recolher (drill-down) em toda linha que abre detalhe, sem dica.** ▸ fechada, ▾ aberta, no começo da linha; › quando abre noutro lugar. O nome acessível continua para o leitor de tela ("Abrir …", "Recolher …"). | A seta é óbvia, e a dica cobria a linha de baixo | Toda tabela em árvore, Planos agronômicos e Manutenção |
| TAB-05 | **Ações da linha no ⋯.** <ul><li>Os botões de ação saem da célula e vão para o ⋯ da linha, cada um com um ícone do verbo.</li><li>"Excluir" vem por último, em vermelho, com a mesma confirmação.</li><li>O link que abre o registro (›) continua na célula: é o alvo único da BOT-07.</li></ul> | A tabela fica limpa. A ação continua a um toque | `engine.grid(..., menu_linha=True)`. Planejar safra › Talhões e cultivos. Demais tabelas na varredura |
| TAB-06 | **Alerta só dentro da tabela.** <ul><li>Na linha, o recurso em falta aparece como ⚠, com o detalhe na dica.</li><li>Nenhuma frase de alerta nem atalho fora da tabela.</li><li>O veredito continua para o leitor de tela.</li></ul> | O alerta aparece junto do que precisa ser corrigido | `engine.grid(..., sico_so_icone=True)`. Planejar safra › Operações e recursos |
| TAB-07 | **Sem cartões de resumo sobre a tela de trabalho** (lista, Kanban, Carga). As contagens ficam nos filtros rápidos e os totais na linha de total. Indicador em cartão é do Painel. | Cartão que repete a tabela empurra o trabalho para baixo | O.S. › Carga. Demais telas na varredura |
| VIS-05 | **Modos de visão em toda lista.** <ul><li>Toda lista tem Tabela e Cartões.</li><li>Kanban quando o registro anda por fases. Matriz, Mapa e Calendário quando o dado pede.</li><li>"Agrupar por" vale em toda visão que lista registros (Tabela, Cartões e Kanban), com o mesmo controle e o mesmo estado. O controle é o mesmo em toda tela: ícone, "Agrupar por" apagado, o valor e ▾. O Agrofit foi alinhado em 16/10.</li><li>Cartão enxuto (16/10, "deixe mais clean, minimalista e mais organizado"): <ul><li>título forte e uma linha de apoio apagada;</li><li>até 4 campos em duas colunas, com rótulo curto em cima e valor numa linha com reticências;</li><li>o texto secundário da célula fica na Tabela e no detalhe.</li></ul></li></ul> | Cada pessoa vê do jeito que decide melhor, sem perder o agrupamento | 94 listas em 43 telas com Tabela e Cartões (seletor no fim da barra, depois de Colunas); O.S. com Cartões no seletor e Agrupar por no Kanban; Manutenção › Ordens e Beneficiamento com Lista, Cartões e Kanban. Faltam: Fazendas, Equipes e Conjuntos, que só têm cartões e ainda não têm o modo Tabela |

## Escolha e seleção

| ID | Regra | Por quê | Situação |
|---|---|---|---|
| SEL-03 | **Lista suspensa do DS.** <ul><li>No computador, toda lista de escolha (`select`) abre a lista do design system: ✓ na opção escolhida e hover verde. Teclado como na lista nativa: Espaço, F4 ou Alt+↓ abrem; na lista, ↑ ↓ Home End e letra andam, Enter escolhe e Esc fecha. Enter no campo fechado não faz nada.</li><li>No toque, fica a lista do próprio aparelho, que é melhor no celular.</li></ul> | Mesma aparência em todas as telas, inclusive Agrofit, Agrupar por e filtros | Toda página (`g2lib`, `g2dsel`) |
| SEL-04 | **Escolha de vários contextos e ação em lote.** <ul><li>Os contextos escolhidos (ex.: fazendas da safra) ficam à vista em chips ✓ na faixa "Trabalhando em". "+ Fazenda" abre a lista do DS com caixas, nome e resumo. Marcar grava na hora, e a recusa aparece no próprio item.</li><li>A tabela mostra os escolhidos juntos, com uma faixa de cabeçalho por item (nome, área, "x de y") e o filtro do item logo depois da busca. Com um item só, não há grupo.</li><li>Agir em várias linhas é no painel lateral, nunca com caixas na tabela: lista já marcada, campos comuns uma vez e uma primária "Planejar N …". A conferência é item a item, a recusa é atômica e repetir não duplica.</li><li>Talhão sem plantio: "Não plantar nesta safra" no ⋯ do talhão livre. Não é pendência nem entra na demanda; "Voltar a planejar" desfaz.</li></ul> | A safra real cruza fazendas, e planejar um por um custa cliques. Talhão em pousio é decisão do produtor | Planejar safra › etapa 2 (`saf_multi_fazenda_test.py` 23/23) |

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
