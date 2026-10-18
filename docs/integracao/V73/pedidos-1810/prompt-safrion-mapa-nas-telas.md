PROJETO: Safrion (Do Talhão à O.S.) · EX-55 · Visão Mapa dentro das telas do Agrícola

PEDIDO DO PROPRIETÁRIO (18/10/2026)
"Em todos esses submenus agrícolas que o modo de visão mapa agregar valor, coloque... exemplo... planejar safra, ordem de serviço, irrigação, etc. dentro do próprio submenu/tela sem ir para o menu principal do mapa."
O hub Agrícola mostra hoje: Planejamento (Agrofit, Análises de solo, Planos agronômicos, Planejar safra, Orçamento), Execução (Pragas e doenças, Ordens de serviço, Irrigação, Colheita) e Resultados (Recebimento, Beneficiamento, Estoque de produto, Custos, Painel).

COMO TRABALHAR (protocolo da equipe, sem exceção)
1. Leia AGENTS.md, docs/STATUS.md, o cabeçalho do checkpoint da issue #1 e o protocolo canônico. Este prompt não substitui o PRD nem as decisões NAV/DS.
2. Antes de qualquer código, Claude e Codex melhoram este desenho de forma independente: cada um confere, tela por tela, se o mapa ajuda uma decisão e decide Adotar, Adaptar ou Rejeitar. Divergência se resolve por fonte; o Codex registra no checkpoint (só ele edita o checkpoint).
3. Gemini real só se houver divergência material de domínio (candidatos: interpolação de solo e leitura de produtividade por talhão). Não simule nenhum modelo.
4. Só depois implante, por fatias, com revisão cruzada: quem revisa integra o PR do outro.

O QUE EXISTE HOJE
- Nenhuma tela do Agrícola tem mapa próprio: a única entrada é o Mapa da barra principal (IN-04). O cadastro de talhões (CD-01) tem uma visão Mapa esquemática.
- O Mapa já tem as camadas de cada área: Integrado, Satélite, Solo, Pragas e doenças, Ordens de serviço, Irrigação, Estádio, Colheita e produtividade, Custos (anexo-mapa-analise.md, EX-44), e cada camada tem um link de volta para a sua tela. O caminho tela → mapa é que não existe: a pessoa sai da tela, perde filtros e registro aberto e precisa achar a camada.
- Ordem de Serviço já tem visões (Tabela, Cartões, Kanban, Calendário, Carga por recurso); as outras telas do Agrícola só têm tabela e cartões.
- Achados do EX-44 que valem aqui: o polígono não mostra dica ao passar o mouse; o mapa da Lagoa Grande (MapLibre) não é operável pelo teclado; Santa Rita tem talhões esquemáticos; "sem dado" usa a mesma cor do fundo; os destinos perdem o contexto.

REGRAS DA VISÃO MAPA NAS TELAS
R1 Um componente só. A visão Mapa de cada tela usa o mesmo motor e a mesma camada do Mapa da fazenda (cores, classes, legenda, regras de "sem dado"). Nada de mapa novo por tela nem cálculo duplicado (EX-51 R8).
R2 É uma visão da tela. Entra no seletor de visões (Tabela | Cartões | Mapa…), com os filtros, a busca e o escopo da tela (Fazenda, Safra, cultura; EX-51 R5). Lista e mapa mostram o mesmo recorte; o contador diz "N no mapa · M sem geometria" e lista os que não têm polígono.
R3 Clique abre o detalhe da própria tela. Clicar no talhão abre o painel de detalhe da tela (EX-49), não o Mapa principal; com vários registros no talhão, abre uma lista curta. Passar o mouse mostra 3 ou 4 valores-chave (EX-44). Teclado: Tab percorre os talhões na ordem da lista, Enter abre, Esc fecha; o leitor de tela recebe o mesmo conteúdo em texto.
R4 Selecionar no mapa alimenta as ações da tela. Clique, Shift+clique e laço selecionam talhões para as ações em vários talhões que a tela já permite (planejar cultivo, programar vistoria, criar O.S., montar frente, programar colheita). Nunca aprovação em lote (decisão fixa).
R5 Legenda com os valores reais. "Sem dado" em hachura neutra, nunca com cor de condição; contraste Talhão, Fazenda ou Absoluto onde houver índice ou interpolação (skill de indicadores de satélite).
R6 "Abrir no Mapa da fazenda" fica como ação secundária, levando o escopo e a camada, para a visão cruzada entre áreas. O Mapa principal continua sendo a visão integrada.
R7 O endereço guarda a visão (?view=mapa) e o talhão aberto; Voltar e recarregar reabrem (EX-51 R4). A última visão escolhida por pessoa e tela fica salva (preferência que o motor já tem).
R8 Celular: mapa na largura toda e a lista como folha que sobe; alvos de 44 px; o mapa só carrega quando a visão é escolhida.
R9 Geometria real. Onde o talhão é esquemático (Santa Rita), o mapa avisa "posição esquemática" até a importação do contorno no cadastro de talhões.

TELA POR TELA
Valor: alto quando a decisão depende de onde as coisas estão; médio quando ajuda a ver o padrão; sem mapa quando não há decisão espacial.

| Tela | Valor | O mapa mostra | Alternar "Mostrar" | Clique abre | Ações com seleção no mapa | Camada que reaproveita |
|---|---|---|---|---|---|---|
| Planejar safra | alto | cada talhão pela cultura e cultivar planejadas na safra; hachura em "sem cultivo" | Cultura · Situação do planejamento (sem cultivo, planejado, publicado, adotado) · Janela de plantio | o cultivo do talhão | Planejar cultivo nos selecionados, com área somada e talhões preenchidos | Estádio |
| Análises de solo | alto | pontos de coleta e mapa de calor do indicador escolhido no laudo; talhão sem laudo vigente em hachura | Indicador (V %, P, K, argila…) · Camada 0–20 ou 20–40 cm · Contraste | o laudo e a dose sugerida do talhão | Planejar amostragem nos talhões sem laudo vigente | Solo |
| Planos agronômicos | médio | talhões pelo plano e versão adotados; destaque para versão nova publicada e não adotada | Plano · Versão | o talhão dentro do plano | Adotar a versão vigente nos selecionados (cada adoção com o seu registro) | Estádio |
| Orçamento | médio | orçado em R$/ha por talhão na versão escolhida | Orçado · Orçado × realizado | o talhão no orçamento | — | Custos |
| Pragas e doenças | alto | pior situação do talhão no período (acima do NC, foco, perto, em controle, sem vistoria), com filtro de alvos; aproximando, os pontos e a rota da vistoria | Situação · Vistoria atrasada · Tendência | a vistoria e a decisão do talhão | Programar vistoria nos selecionados, com a rota | Pragas e doenças |
| Ordens de serviço | alto | O.S. por talhão | Fases · Avanço (fração feita pintada, EX-52 J2) · Atrasos · Impedimentos · Insumos · Frentes (rota numerada, EX-54) | a O.S. do talhão | Criar O.S. da atividade do plano nos selecionados · Montar frente | Ordens de serviço |
| Irrigação | alto | setores e pivôs com a situação de hoje; posição do pivô e lâmina | Hoje · Balanço hídrico (déficit em mm) · Outorga e energia | a ordem de irrigação ou o setor | Programar irrigação nos setores em déficit | Irrigação |
| Colheita | alto | situação da colheita por talhão | Situação · Produtividade × meta (t/ha, sc/ha) · Semana de colheita · Carência (talhão bloqueado) | a previsão e as cargas do talhão | Programar colheita nos selecionados (O.S. de colheita e, depois, frente) | Colheita e produtividade |
| Recebimento | médio | origem das cargas do período por talhão: toneladas recebidas, cargas a pesar, umidade e impureza médias | Recebido · A pesar · Qualidade na recepção | as cargas do talhão | — | Colheita e produtividade |
| Custos | alto | custo realizado em R$/ha × previsto por talhão; custo por saca quando houver produtividade | Realizado × previsto · R$/ha · R$/sc | a composição do custo do talhão | — | Custos (corrigir o "todo talhão com previsto fica azul" do EX-44) |
| Agrofit | sem mapa | consulta de produto, sem decisão por lugar | — | — | No detalhe do produto: "onde está planejado ou foi aplicado", em lista com link ao talhão | — |
| Beneficiamento | sem mapa | processo no packing | — | — | Origem do lote como link ao talhão | — |
| Estoque de produto | sem mapa | lotes e saldo | — | — | Origem por talhão no lote, com rastreabilidade (EX-51) | — |
| Painel | sem mapa | indicadores | — | — | Indicador por talhão abre a tela da área já na visão Mapa | — |

FATIAS (ordem sugerida; Claude e Codex podem reordenar com motivo)
F1 Extrair do Mapa da fazenda o componente embutível (camada, legenda, dica, clique, seleção, teclado) e ligar em Ordens de serviço, Pragas e doenças e Irrigação, que já têm camada pronta.
F2 Planejar safra (com seleção para planejar cultivo) e Colheita.
F3 Análises de solo, Custos e Orçamento.
F4 Planos agronômicos e Recebimento; links de origem por talhão em Agrofit, Beneficiamento e Estoque de produto.
Cada fatia: desenho independente de Claude e Codex → aceite medido antes do código → implantação → revisão cruzada → robôs de passagens (EX-51) e de listas (EX-49) de novo → publicação no artefato existente com versão e mudança concreta.

ACEITE
- Nas 10 telas com valor, a visão Mapa abre dentro da tela, com os mesmos filtros e os mesmos números da lista; nenhuma tarefa da tela exige ir ao Mapa principal.
- Clique no talhão abre o detalhe da própria tela; dica ao passar o mouse; teclado e leitor de tela percorrem os talhões; celular com mapa e lista em folha.
- Seleção no mapa dispara as ações permitidas da tela e nunca aprova em lote.
- "Sem dado" e "sem geometria" visíveis e contados; Santa Rita marcada como esquemática até a importação.
- O Mapa da fazenda continua igual e recebe o escopo quando aberto pela ação secundária.

NÃO FAZER
- Criar mapa ou camada nova por tela, ou nome novo na barra de camadas do Mapa (continua com 9 camadas).
- Criar item novo na barra principal.
- Pôr visão Mapa onde não há decisão espacial (Agrofit, Beneficiamento, Estoque de produto, Painel).
- Mostrar interpolação ou índice sem legenda de valores e sem a qualidade do dado.

ENTREGA (no canal registrado)
- Para cada tela: validação (o que existe, com arquivo e trecho), decisão de Claude, decisão do Codex, decisão final e fatia.
- Desenho do componente embutível no motor e dos pontos de mudança.
- Três listas curtas, com motivo: aplicado, deixado de fora, cortado. Suposições e pendências com gatilho de retomada.
