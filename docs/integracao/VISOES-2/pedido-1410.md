# VISOES-2 · Foco (o quê, quem e como, quando, onde, quanto), agrupar e descer, colunas essenciais, Tabela, Cartões e padrão visual

Arquivo único para o Claude Code: a Parte 1 é a ordem de execução; a Parte 2 é a especificação que ela cita. Fonte: documento "Modos de visão por tela · Do Talhão à O.S.", versão de 14/10/2026.

---

## Parte 1 · Ordem de execução

Contexto: o protótipo "Do Talhão à O.S." tem 155 arquivos .dc.html, 8 itens de menu e 41 telas no menu. Só g_os (OS.dc.html) declara G2_VISOES: lista, agrupada, kanban, calendario, carga. A especificação completa está na Parte 2 deste arquivo (seções Foco: cinco perguntas; Agrupar e descer; Visões; Tabela, Cartões e o Agrupar por; Padrão visual das visões; Telas e focos; Colunas: só o essencial). Siga-a sem acrescentar visões.

1. Marcas: cada coluna de GRIDS ganha foco (oque, quem, quando, onde, quanto, situacao) e tipo (data, intervalo, dap, geometria, numero); hierarquias ganham níveis (Fazenda > talhão > parcela; Grupo > insumo > lote; Safra > mês > semana > dia; Total > componente > natureza > documento). O motor deduz focos e visões dessas marcas; G2_VISOES deixa de ser escrito tela a tela.
2. Barra única em toda Tabela e Cartões: busca, filtros, foco com ícone e rótulo (só os que a listagem tem, sempre na ordem O quê, Quem e como, Quando, Onde, Quanto), "Ver como" com até 4 formas válidas para o foco, ordenação. O menu do foco escolhe o nível de partida e um segundo foco opcional.
3. Colunas: cada listagem abre só com as colunas de "Abre com" da seção Colunas: só o essencial da Parte 2, na ordem dela (a primeira é a identidade e fica travada); as demais vão para "Mais colunas". Seletor de colunas (view_column) na barra, com o número de ocultas ("+6"): painel agrupado por foco, marcar mostra, desmarcar oculta, arrastar reordena, busca acima de 12 colunas, "Restaurar padrão"; o menu ⋯ do cabeçalho tem "Ocultar coluna". A escolha fica por usuário × listagem. Ocultas seguem valendo para busca, filtros e foco; exportar leva as visíveis, com opção "Todas as colunas". Situação, Estado e Condição viram ícone com cor antes do nome; unidade vai junto do número; coluna do grupo ou com o mesmo valor em todo o recorte sai da linha. Celular mostra as 3 primeiras. Listagens com até 5 colunas ficam inteiras; o app de campo não ganha seletor.
4. Cruzamento: quem × quando = carga; oque ou onde × quando com intervalo = linha_tempo; quanto × quando = grafico; dois focos com número = matriz, com quanto na cor.
5. Descer em toda visão que agrupa: clique no nome do grupo, barra, célula, polígono, raia ou mês desce um nível e filtra; a forma se mantém; na matriz desce nos dois focos; a seta da Tabela e dos Cartões só expande no lugar. Trilha no topo volta a qualquer nível; Esc sobe um. Totais fecham em cada nível. Feed, galeria e comparar não descem. O último nível abre a ficha com a origem (Por quê).
6. Quando alterna DAP, DAE e data (conversão pela data de plantio de cada talhão, como PL-02det); Quanto alterna R$, R$/ha e quantidade.
7. Situação: chips com contagem e cor com ícone em todo foco; kanban com colunas por fase e raias pelo foco.
8. Preferência por perfil × listagem guarda foco, trilha, visão e grupos recolhidos; o foco segue para a próxima tela que o tenha. Início: PCP em Quem e como, agrônomo em O quê, encarregado em Onde, gestor em Quanto; sem perfil, a coluna "Abre em" da Parte 2. Endereço: ?foco=onde&trilha=LG/T4&view=mapa.
9. Tabela única: funda lista e agrupada (k=tabela, rótulo "Tabela"); ?view=lista e ?view=agrupada redirecionam; árvores viram Tabela agrupada pelo pai. Cartões: promova as Atividades do plano (PA) a componente compartilhado (k=cartoes).
10. Motor: acrescente mapa, matriz, linha_tempo, grafico, galeria, feed e comparar como componentes compartilhados e reaproveite o calendario e a carga da O.S. O mapa reaproveita o IN-04; a matriz usa escala de cor única, com legenda e valor no foco; a linha do tempo aceita eixo de datas ou DAP/DAE.
11. Telas: marque as colunas de cada listagem conforme a seção Telas e focos da Parte 2 (colunas de GRIDS em 14/10/2026; se alguma mudou, use a equivalente e registre no PRD).
12. Seletores próprios: COLH (Por talhão/Por semana) e AG-01 (Agrupar vistorias por) viram foco; CD-01 (Lista/Mapa), BEN (Lista/Kanban) e CA-01 (Lista/Kanban/Mapa) vão para o Ver como; o seletor "Visão" da MA vira abas (Sem ordem, Ordens, Ativos, Planos); o "Agrupar por" sem opções do AG-07 sai. "Hoje/Esta semana" da EXPED continua filtro.
13. Padrão visual em todas as visões, conforme a seção Padrão visual das visões da Parte 2: ícones Material Symbols Rounded conferidos no catálogo; texto só onde muda decisão; cor de estado sempre com ícone; números à direita em fonte tabular; menu ⋯ com desfazer de 5 s; esqueleto no carregamento; transições de 150 a 200 ms; alvo de 44 px; contraste AA; tema claro e escuro. Comece pelas Atividades do plano, seguindo o exemplo hoje × passa a ser.
14. Regras de toda visão: Tabela sempre no Ver como e retorno de erro; mesmo recorte e mesmos totais; nenhuma visão grava dado; o clique abre a mesma ficha; estados do §2.8 em toda visão; teclado e leitor de tela com equivalente em Tabela. Celular (<= 640 px): 1 nível por vez com trilha; mapa e matriz com rolagem própria e legenda fixa; linha do tempo, calendário e carga viram Cartões por dia ou por recurso.
15. Fora do menu (AG-03 a AG-06, CA, CO, GE fora do menu, IN, LO, PL, SU, VE, PT-02 a PT-07, MB-02 a MB-10): só barra e padrão visual, sem focos novos; as consolidadas redirecionam como MA-01 a MA-05.
16. Corrija as telas sem link de chegada: GE-01, IN-03, PL-03, PT-06, MB-05det, MB-08 e MB-08x-recibo; prioridade MB-08.
17. Nenhum seletor exibe "Lista" ou "Tabela agrupada"; o crawler falha se encontrar algum.

Aceite, por listagem: (a) cada foco marcado agrupa, e a soma dos grupos e a contagem dos chips batem com o total da Tabela; (b) descer e voltar pela trilha preserva os totais em cada nível, e o link com a trilha abre no mesmo ponto; (c) cada forma do Ver como abre sem erro para cada foco válido e o clique abre o registro certo; (d) trocar foco, visão ou tela e voltar preserva foco, trilha, filtros, grupos recolhidos e rolagem; (e) ?view=lista e ?view=agrupada abrem a Tabela; (f) cada tela passa na rubrica do padrão visual; (g) o crawler por papel percorre todos os focos, níveis e formas; (h) cada listagem abre com exatamente as colunas de "Abre com", na ordem da Parte 2, e o seletor mostra, oculta, reordena e restaura, com a escolha de volta no próximo acesso. Registre a matriz de aceite no PRD e entregue antes/depois com capturas de cada tela alterada.

---

## Parte 2 · Especificação

### Resumo

Toda listagem passa a responder a cinco perguntas, os focos: o quê, quem e como, quando, onde e quanto. O usuário escolhe o foco; o sistema escolhe a forma que melhor responde e leva o foco junto para a próxima tela.

O protótipo tem hoje 8 itens de menu, 41 telas no menu e 155 arquivos de tela; só a O.S. declara visões no motor (Lista, Tabela agrupada, Kanban, Calendário e Carga por recurso). Em vez de declarar visões tela a tela, cada coluna ganha a marca do seu foco e o motor deduz as visões válidas: o trabalho por tela vira marcar colunas.

### Foco: cinco perguntas

O foco é a pergunta que o usuário quer responder: ele agrupa a listagem e escolhe a forma de mostrar. É o Agrupar por levado ao nível da tela.

| Foco | Pergunta | Colunas que respondem | Ver como |
| --- | --- | --- | --- |
| O quê | Que atividade, operação, insumo ou produto? | Atividade, operação, serviço, alvo, item, produto, plano | Cartões · Tabela · Comparar |
| Quem e como | Quem faz e com que recurso? | Equipe, pessoa, executante, máquina, conjunto, captação, fornecedor, cliente | Carga por recurso · Tabela · Cartões |
| Quando | Em que DAP ou data? | DAP, DAE, data, início e fim, prazo, semana, mês, safra | Linha do tempo · Calendário · Feed · Tabela |
| Onde | Em que fazenda, talhão, setor ou local? | Fazenda, talhão, parcela, setor, ponto, depósito | Mapa · Cartões · Galeria · Tabela |
| Quanto | Quanto custa, rende ou falta? | R$, R$/ha, área, quantidade, saldo, produtividade | Gráfico · Matriz · Tabela |

- **Dois focos cruzados dão a forma.** Quem × Quando é a Carga por recurso; O quê ou Onde × Quando, com início e fim, é a Linha do tempo; Quanto × Quando é o Gráfico; dois focos com um número são a Matriz, com Quanto na cor (talhão × alvo, insumo × mês).
- **Quando fala DAP e data.** O mesmo controle alterna DAP, DAE e data; a conversão usa o plantio de cada talhão, como o Plano do talhão (PL-02det) já faz.
- **Quanto troca a unidade.** R$, R$/ha ou quantidade (ha, L, kg, sc); totais e subtotais seguem a unidade escolhida.
- **Situação não é foco: está sempre à vista.** Chips com contagem e cor com ícone em qualquer foco. O Kanban põe as fases em colunas e usa o foco nas raias (uma raia por talhão, por exemplo).
- **Por quê fica a um clique.** A ficha de cada item mostra a origem: plano, recomendação, ocorrência ou alvo.
- **O foco é do usuário, não da tela.** Fica no perfil e segue para a próxima tela: quem olha Ordens por Onde abre Pragas por Onde. Início por perfil: PCP em Quem e como, agrônomo em O quê, encarregado em Onde, gestor em Quanto.
- **O motor deduz, a tela só marca.** Cada coluna recebe o foco e o tipo (data, início e fim, DAP, geometria, número); as visões válidas saem daí. Foco sem coluna não aparece; os demais ficam sempre na mesma ordem.

#### Agrupar e descer

Cada foco tem níveis, do geral ao detalhe: o foco agrupa no primeiro nível e o clique desce um nível, filtrando pelo que foi clicado.

| Foco | Níveis | O último nível abre |
| --- | --- | --- |
| O quê | Processo › operação › atividade; Grupo › insumo › lote; Produto › classe › lote | a ficha do item, com o Por quê |
| Quem e como | Equipe › pessoa; Classe › máquina › conjunto; Captação › setor; Fornecedor ou cliente › contrato | a agenda do recurso |
| Quando | Safra › mês › semana › dia; Fase do ciclo › faixa de DAP › DAP | o dia, em Tabela |
| Onde | Fazenda › talhão › parcela; Depósito › local | a ficha do talhão ou do local |
| Quanto | Total › componente › natureza › documento | o documento de origem |

- **Desce em toda visão que agrupa.** Clicar no nome de um grupo (Tabela, Cartões), numa barra (Gráfico), numa célula (Matriz), num polígono (Mapa), numa raia (Kanban, Linha do tempo, Carga) ou num mês (Calendário) desce um nível; a forma continua a mesma.
- **Abrir no lugar é outra coisa.** Na Tabela e nos Cartões, a seta só expande o grupo ali mesmo, sem trocar de nível.
- **Na Matriz, desce nos dois focos.** A célula T4 × ácaro abre as vistorias daquele talhão para aquele alvo.
- **A trilha mostra onde se está.** "Todas as fazendas › Lagoa Grande › T4" no topo volta a qualquer nível; Esc sobe um. A trilha vai no endereço, então o link compartilhado abre no mesmo ponto.
- **Os números fecham em cada nível.** O total do nível de baixo é o valor do grupo clicado em cima.
- **Feed, Galeria e Comparar não descem:** já mostram o detalhe.

### Visões

Cada visão responde a um foco ou a um cruzamento de dois; a coluna da direita impede a visão errada.

| Visão | Responde a | Como fica | Não usar quando |
| --- | --- | --- | --- |
| Tabela | qualquer foco | Cabeçalho fixo; grupo do foco com contagem e subtotal; seleção em massa | — (sempre disponível) |
| Cartões | O quê, Onde, Quem e como | Fechado, uma linha: ícone do tipo, título e até 2 números; aberto, os filhos em mini-Tabela | o item não tem filhos a conferir |
| Kanban | Situação | Colunas por fase com contagem e soma; raias pelo foco; atraso com ícone | o fluxo tem 1 ou 2 fases |
| Carga por recurso | Quem e como × Quando | Grade recurso × tempo; excesso em vermelho com ícone; tarifa como faixa de fundo | não há disputa de recurso |
| Linha do tempo | O quê ou Onde × Quando | Barras no eixo de datas ou DAP; linha de hoje; sobreposição destacada | as durações não se sobrepõem |
| Calendário | Quando, data única | Mês ou semana; ponto com a cor do tipo; dia cheio mostra "+3" | ordenar por data já resolve |
| Mapa | Onde | Polígonos pela escala única; legenda fixa; clique abre painel lateral | há menos de 3 locais com geometria |
| Matriz | dois focos + Quanto | Células pela escala única; cabeçalhos fixos; totais na borda | um eixo tem 1 ou 2 valores |
| Gráfico | Quanto × Quando | Até 3 séries; rótulo na ponta da linha; meta tracejada; título com a conclusão | menos de 5 pontos |
| Galeria | Onde, com foto | Miniaturas com data e talhão sobre a foto; tela cheia com setas | a foto é anexo eventual |
| Feed | Quando, para eventos | Eventos por dia; hora à esquerda; ícone do tipo e quem fez | o evento muda depois |
| Comparar | O quê × O quê | Lado a lado; só as linhas que diferem; melhor valor marcado | só há uma alternativa |

Quatro regras valem em toda tela:

- Tabela está sempre no Ver como e é o retorno de qualquer erro.
- No máximo 4 formas por foco; no celular aparecem 3 e o resto em "Mais visões".
- Toda visão lê o mesmo recorte (Fazenda, Safra, filtros, busca) e mostra os mesmos totais da Tabela.
- Visão não cria dado: o clique abre a mesma ficha ou painel da Tabela.

#### Tabela, Cartões e o Agrupar por

Lista e Tabela agrupada são uma visão só, a Tabela. Cartões é outra visão, para ler item a item e abrir o que há dentro de cada um. O Agrupar por virou o foco.

| Visão | Como é | Serve para | Exemplo |
| --- | --- | --- | --- |
| Tabela | Grade com cabeçalho de colunas. Sem grupo é a antiga Lista; a antiga árvore é a Tabela agrupada pelo pai. | Comparar, ordenar e somar colunas; editar e exportar | Talhões por fazenda |
| Cartões | Um cartão por item com ícone do tipo, título e até 2 números; a seta abre os filhos; "Expandir tudo"; chips de filtro rápido com ícone e contagem. | Ler em sequência e conferir a composição de cada item | Atividades do plano por DAP, cada uma com seus insumos e o custo por ha |

- Barra única em Tabela e Cartões: busca, filtros, foco (que agrupa e desce), ordenação e colunas.
- O menu de cada foco escolhe o nível de partida (Onde: Fazenda ou Talhão) e um segundo foco opcional. No celular, 1 nível por vez, com a trilha no topo.
- Cada grupo mostra contagem e subtotais e ordena por nome ou subtotal; a soma dos grupos fecha com o total.
- Chips de filtro rápido filtram, não agrupam: "Pulverização 4" mostra quantos itens há daquele tipo no recorte.
- Foco, trilha, visão e grupos recolhidos ficam na preferência e no endereço (?foco=onde&trilha=LG/T4&view=mapa).

### Padrão visual das visões

Toda visão segue o mesmo padrão: ícone com rótulo no seletor, texto só onde muda decisão, cor só com significado e números alinhados para leitura rápida. Base: a casca Material 3 do sistema e os ícones Material Symbols Rounded.

- **Texto essencial.** Fica só o que muda uma decisão. Instrução fixa sai da tela e vai para o "?" ou para o estado vazio; nada repete o que a seção, o chip ou o ícone já dizem.
- **Ícone com função.** Tipo e estado ganham ícone antes do título; o seletor mostra ícone e rótulo. Ícone sozinho só em ação óbvia (busca, menu ⋯).
- **Cor com significado.** Verde da marca só na ação principal e na seleção. Vermelho, âmbar e verde só para estado, sempre com ícone junto, para quem não distingue cor.
- **Números legíveis.** Alinhados à direita, em fonte tabular, com unidade curta (R$/ha, ha, mm, d); totais e subtotais sempre visíveis.
- **Menos moldura.** Divisória ou sombra, nunca as duas; espaçamento em múltiplos de 8 px; título sem sublinhado, e a linha ou o cartão inteiro abre o registro.
- **Ações no lugar certo.** Uma ação principal por tela, no topo à direita. Editar e excluir ficam no menu ⋯, que aparece no foco; excluir oferece desfazer por 5 s em vez de janela de confirmação.
- **Resposta imediata.** Esqueleto no carregamento; transição de 150 a 200 ms ao abrir, agrupar e trocar de visão; respeita "reduzir movimento".
- **Celular e acessibilidade.** Alvo de toque de 44 px, foco visível, contraste AA, tema claro e escuro pelos tokens.

#### Ícones de domínio

O mesmo ícone aparece no chip, no cartão, na linha da Tabela, no Calendário e no Feed. Os nomes são do catálogo Material Symbols; se algum faltar, usar o mais próximo e registrar.

| Grupo | Ícones |
| --- | --- |
| Foco | O quê `category` · Quem e como `engineering` · Quando `event` · Onde `location_on` · Quanto `payments` |
| Visão | Tabela `table_rows` · Cartões `view_agenda` · Kanban `view_kanban` · Carga `view_week` · Linha do tempo `view_timeline` · Calendário `calendar_month` · Mapa `map` · Matriz `grid_on` · Gráfico `show_chart` · Galeria `photo_library` · Feed `dynamic_feed` · Comparar `compare_arrows` |
| Tipo de operação | Pulverização `sprinkler` · Plantio `psychiatry` · Adubação `compost` · Tratamento de sementes `grain` · Colheita `agriculture` · Irrigação `water_drop` · Manutenção `build` · Transporte `local_shipping` |
| Estado | Planejada `schedule` · Liberada `play_circle` · Em execução `pending` · Concluída `check_circle` · Atrasada `error` · Bloqueada `block` |
| Barra e ações | Busca `search` · Filtros `filter_list` · Ordenar `swap_vert` · Colunas `view_column` · Expandir `expand_more` · Trilha `chevron_right` · Mais ações `more_vert` · Incluir `add` |

#### Exemplo: Atividades do plano

A tela atual já é Cartões; aplicar o padrão tira texto repetido e põe o custo do plano à vista.

| Hoje | Passa a ser |
| --- | --- |
| "DAP −20" e, abaixo, "20 dias antes do plantio" | Só "−20" em coluna fixa; a seção já diz DAP |
| Frase "Confira as atividades pela distância do plantio…" | Sai; vai para o "?" da seção |
| Título verde sublinhado em toda linha | Título em preto, sem sublinhado; o cartão inteiro abre |
| Tipo escrito sob o título ("Pulverização") | Ícone do tipo antes do título, o mesmo do chip |
| Chips só com texto | Chips com ícone e contagem |
| Lixeira em toda linha | Menu ⋯ no foco; excluir com desfazer |
| "8 gatilhos · 8 atividades" | "8 atividades · R$ 2.099,90/ha"; gatilhos só quando o número diferir |
| Sem total | Total da seção à direita, alinhado aos custos |

### Telas e focos

Cada linha é uma listagem que existe hoje no protótipo, com as colunas reais que respondem a cada foco; "—" é foco que a listagem não tem e, por isso, não aparece. Abre em é o foco e a forma de entrada quando o perfil ainda não tem preferência. Situação (fase, estado) existe em quase todas e fica fora da tabela, porque vale em qualquer foco.

#### Mapa e Cadastros

| Tela · listagem | Abre em | O quê | Quem e como | Quando | Onde | Quanto |
| --- | --- | --- | --- | --- | --- | --- |
| IN-04 Mapa · talhões nas 11 camadas | Onde · Mapa | Camada | — | Data da imagem | Fazenda › talhão | Valor da camada |
| CD-01 Talhões | Onde · Tabela | Sistema | — | — | Fazenda › talhão | Área cultivável, Polígono, Diferença |
| CD-01 Fazendas | Onde · Tabela | — | — | — | Fazenda | Área total |
| CD-01 Ambiental | Onde · Mapa | Tipo | — | — | Área ambiental, Fazenda | Área |
| CD-01 Água | Onde · Mapa | Uso | — | Vencimento | Ponto de água, Fazenda | Vazão |
| CD-01det Talhão · parcelas | Quando · Linha do tempo | Cultura, Cultivar | — | Safra › parcela, Plantio | Talhão | Área, Livre |
| CD-02 Culturas e cultivares | O quê · Tabela | Cultura › cultivar, Tipo de ciclo | — | Ciclo | — | Cultivos |
| CD-03 Máquinas e instalações | Quem e como · Tabela | Classe | Máquina ou instalação | Próxima calibração | — | Custo R$/h |
| CD-03 Conjuntos | Quem e como · Tabela | Operações | Conjunto, Operadores alocáveis | — | — | Largura, Rendimento |
| CD-04 Pessoas | Quem e como · Tabela | Habilidades, Habilitação | Pessoa, Equipe, Vínculo | Disponível até, Validade da habilitação | — | Custo R$/h |
| CD-04 Equipes | Quem e como · Cartões | — | Equipe, Líder | Calendário | — | Pessoas ativas |
| CD-05 Parceiros | Quem e como · Tabela | Papéis | Parceiro, Contato | — | — | — |
| CD-05 Cobertura de cotação | O quê · Matriz grupo × fornecedor | Grupo de insumo | Fornecedor | — | — | Fornecedores que recebem cotação |
| CD-06 Itens | O quê · Tabela | Grupo › item, Natureza de custo | — | Data do preço | — | Preço de referência |
| CD-06 Locais de estoque | Onde · Tabela | Tipo | — | — | Local, Fazenda | Itens com este local padrão |
| CD-07 Estrutura gerencial | O quê · Tabela | Dimensão › código, Conta no ERP | — | Início e fim da vigência | — | — |
| CD-08 Operações e rendimentos | O quê · Tabela | Operação › conjunto, Processo, Cultura | Conjunto, Fonte | — | — | Rendimento, Custo R$/h, Custo R$/ha |

#### Agrícola

| Tela · listagem | Abre em | O quê | Quem e como | Quando | Onde | Quanto |
| --- | --- | --- | --- | --- | --- | --- |
| PAGR Painel · colheita prevista e recebida | Quanto × Quando · Gráfico | Cultivo | — | Período | Fazenda | Previsão publicada, Recebido |
| AG-07 Agrofit · produtos | O quê · Tabela | Produto, Ingrediente ativo, Classe · modo de ação | — | — | — | Culturas, Alvos, Na fazenda |
| PA Biblioteca de planos | O quê · Cartões | Plano, Cultura | — | Gatilhos | — | Atividades, Insumos/ha |
| PA Atividades do plano | Quando · Cartões | Atividade, Operação, Insumos | — | Gatilho (DAP ou data) | — | Dose/ha, Custo/ha |
| PA Cultivos que usam o plano | Onde · Tabela | Cultura e variedade, Versão aplicada | — | Safra | Talhão ou parcela | Área |
| PA Versões | O quê · Comparar | Versão | — | — | — | — |
| AG-02 Laudos | Onde · Mapa | Laudo, Profundidade | — | Coleta | Fazenda · talhão | V %, K |
| AG-02 Água no solo | Onde · Tabela | Método, Profundidade | Fonte · responsável | Data | Talhão · zona | Capacidade de campo, Ponto de murcha, CAD |
| SAF Safras | Quando · Tabela | — | — | Safra | Fazenda | Cultivos, Área |
| SAF Talhões e cultivos | Onde × Quando · Linha do tempo | Cultura, Variedade, Plano agronômico | — | Plantio, Ocupa até, Livre a partir de | Talhão ou parcela | Área, Área livre, Meta |
| SAF Operações | O quê × Quando · Linha do tempo | Operação › atividade | Conjunto | Data | Talhão | Área trabalhada, Horas-conjunto, Custo R$/ha, Custo total |
| SAF Rendimentos | O quê · Tabela | Operação, Atividade | Conjunto, Modo | Janela por talhão | — | Rendimento, Custo R$/h, Custo R$/ha |
| SAF Capacidade | Quem e como × Quando · Matriz | — | Recurso | Mês | — | Maior uso, uso por mês |
| SAF Recursos no pico | Quem e como · Tabela | — | Recurso (máquinas, pessoas) | Mês do pico | — | Disponíveis, Necessárias no pico |
| SAF Demanda de insumos | O quê × Quando · Matriz | Grupo, Insumo | — | 1º uso, Falta em, Coberta em | — | Demanda bruta, Necessidade líquida, Valor |
| SAF Sugestões do laudo | Onde · Tabela | Atividade · produto, Tipo | — | — | Talhão | Diferença no talhão |
| GE-02 Orçamento · versões | O quê · Comparar | Versão, Premissas | — | — | — | Volume, Preço, Custo total, Pico de caixa |
| GE-02 Cronograma de caixa | Quanto × Quando · Gráfico | Maior componente | — | Trimestre | — | Desembolso V1 e V2, Diferença |
| OS Ordens de serviço | pelo perfil; já tem Tabela, Kanban, Calendário e Carga | Atividade, O.S. | Responsável, Quem resolve | Início e fim, Prazo | Talhão, Local | Área, Realizado, Saldo |
| AG-01 Pragas · vistorias | Onde × O quê · Matriz | Alvo | — | Data | Talhão · cultura | Contagem × NC |
| AG-01det Rota e evidências | Onde · Mapa | — | — | Hora | Ponto, GPS | Contagem, Fotos |
| IR-01 Irrigação · setores | Onde · Mapa | Pendência | — | Próxima passada | Setor, Fazenda | Déficit hoje, Necessidade bruta, Cobertura |
| IR-02 Programação | Quem e como × Quando · Carga | Etapa | Captação › ordem | Início e fim | Setor | Lâmina |
| IR-03 Ordens de irrigação | Quando · Tabela | Tipo, Etapa | Responsável | Início e fim | Setor, Fazenda | Lâmina |
| IR-04 Fontes de clima | Quando · Gráfico | Grandeza | Fonte | Atualização, Validade da calibração | Fazenda | Cobertura |
| IR-04 Captações | Onde · Tabela | Outorga | Captação | Vencimento | Fazenda | Vazão outorgada, Volume hoje, Uso do dia |
| IR-04 Desempenho por setor | Quanto · Gráfico | Cultura | — | — | Setor | Volume, Energia, Lâmina aplicada, Eficiência |
| COLH Previsão por talhão | Onde × Quando · Matriz | Cultura, Variedade | — | Semana | Talhão | Previsão, Colhido, Produtividade |
| COLH Previsão por semana | Quando · Gráfico | Produto | — | Semana | — | Previsão publicada, Colhido, Desvio |
| CARGA Cargas e recebimento | Situação · Kanban | Cultura | — | Colheita, Recebimento | Origem, Lote · local | Líquido, Comercial |
| BEN Ordens de beneficiamento | Situação · Kanban | Ordem, Produto | Quem resolve | — | — | Em processo |
| PROD Lotes de produto | Quanto · Tabela | Produto, Lote | — | Validade | Local | Físico, Bloqueado, Em processo, Reservado, Disponível |
| GE-03 Custos · composição | Quanto · Gráfico | Componente, Origem (documento) | — | Competência | Dimensões | Qtd × preço, Valor |

#### Manutenção

| Tela · listagem | Abre em | O quê | Quem e como | Quando | Onde | Quanto |
| --- | --- | --- | --- | --- | --- | --- |
| PMAN Painel · ordens por estado | Situação · Kanban | — | — | — | — | Pendências sem ordem, Ordens abertas, Em execução, Ativos bloqueados |
| MA Sem ordem | Quando · Calendário | Item, O que | Ativo · leitura | Prazo | — | Peças |
| MA Ordens | Quem e como × Quando · Carga | Serviço · tipo | Ordem · ativo, Executante | Janela | — | Tempo, Custo |
| MA Ativos | Situação · Kanban por condição | — | Ativo · local | Próxima manutenção | — | Leitura, Custo no mês, Consumo |
| MA Abastecimentos | Quanto × Quando · Gráfico | — | Ativo, Operador, Método | Data · leitura | Tanque/lote | Volume, Consumo |
| MA Planos | O quê · Cartões | Plano, Serviços | Aplica-se a, Ativos | — | — | — |

#### Suprimentos

| Tela · listagem | Abre em | O quê | Quem e como | Quando | Onde | Quanto |
| --- | --- | --- | --- | --- | --- | --- |
| PSUP Painel · lotes com saldo | Quanto · Gráfico | — | — | — | — | Lotes com saldo, com reserva, em quarentena; Requisições a entregar |
| CMP Safras e solicitações | Quando · Tabela | Solicitação de compra | — | Safra | — | — |
| CMP Demanda por grupo | O quê × Quando · Matriz | Grupo · insumo | — | Falta a partir de | — | Bruta, Estoque apto, A receber, Necessidade, Valor |
| CMP Fornecedores homologados | Quem e como · Tabela | Grupo | Fornecedor, Canal e contato | Responder até | — | — |
| CMP Propostas | O quê · Comparar | Grupo · insumo | Proposta, Frete, Pagamento | Entrega, Validade | — | A pedir, Preço, Custo |
| CMP Alçada de aprovação | Quanto · Tabela | Insumo | Pedido · fornecedor | Entrega | — | Quantidade, Preço, Valor |
| CMP Pedidos e entregas | Quando · Calendário | Insumo | Pedido · fornecedor | Previsão | — | Pedido, Recebido, A entregar, Valor |
| EST Recebimentos | Quando · Tabela | Item, Lote | Fornecedor, Pedido | Data da nota, Conferida em, Validade | — | Na nota, Conferida, Apta, Quarentena |
| EST Entregas por O.S. | O quê · Cartões por O.S. | Item, Lote | Requisição, O.S. | Fase da O.S. | — | Solicitado, Entregue, A entregar |
| EST Custódia e devoluções | Quem e como · Tabela | Item, Lote | Com quem | Encerramento da O.S. | — | Entregue, Consumido, Devolvido, Em custódia |
| EST Saldos por lote e local | Onde · Tabela | Item › lote | — | Validade | Local | Físico, Reservado, Bloqueado, Disponível |
| EST Contagens | Onde · Tabela | Item, Lote | — | — | Local | Sistema, Contado, Diferença |
| EST Movimentos | Quando · Feed | Movimento, Item | Quem, Origem | Hora | — | Quantidade |
| IC Preço e melhor mês | O quê × Quando · Matriz | Insumo | — | Mês mais barato, Próxima necessidade | — | Preço agora, 12 meses, Economia estimada |
| IC Preço por insumo | Quanto · Tabela | Insumo, Grupo | — | — | — | Último pago, Referência, Melhor cotação |
| IC Fornecedores | Quem e como · Gráfico de dispersão | — | Fornecedor | Prazo de entrega | — | Preço vs referência, Pontualidade |
| IC Custo por hectare | Quanto · Gráfico | Grupo | — | — | — | Total orçado, Custo R$/ha |

#### Comercial

| Tela · listagem | Abre em | O quê | Quem e como | Quando | Onde | Quanto |
| --- | --- | --- | --- | --- | --- | --- |
| PCOM Oferta e compromissos | O quê × Quando · Matriz | Produto | — | Período | — | Oferta, Compromissos, Livre para vender |
| PCOM Preço e recebimento | Quanto · Gráfico | Produto | — | — | — | Preço contratado e realizado, A receber, Vencido |
| VEN Contratos e pedidos | Situação · Kanban | Produto | Venda · cliente | Tipo · janela | — | Quantidade, Preço, Entregue, Falta |
| EXPED Cargas de saída | Quem e como × Quando · Carga | Produto · lotes | Venda · cliente, Modalidade · veículo | Data | — | Previsto, Saída |
| IV Preço e melhor mês | O quê × Quando · Matriz | Produto | — | Melhor mês para vender | — | Preço agora, 1 mês, 12 meses |
| IV Preço × mercado | Quanto · Gráfico | Produto | — | — | — | Preço contratado, Referência, Diferença |
| IV Safra comercializada | Quanto · Gráfico | Produto | — | — | — | Oferta, Vendido, Livre para vender |
| IV Recebimento líquido | Quanto · Tabela | Produto, Venda | Cliente | Prazo | — | Preço, Frete, Custo do prazo, Líquido |

#### Configurações

| Tela · listagem | Abre em | O quê | Quem e como | Quando | Onde | Quanto |
| --- | --- | --- | --- | --- | --- | --- |
| CF-01 Pessoas | Quem e como · Matriz pessoa × papel | Decide (alçadas) | Pessoa, Papéis | — | — | — |
| CF-01 Alçadas | O quê · Tabela | Alçada | Quem decide | — | — | Valor ou limite |
| CF-04 Auditoria · trilha | Quando · Feed | O quê, Objeto | Quem, Origem | Quando | — | — |
| CF-03 Integrações | O quê · Tabela | Conexão, Traz e leva | Credencial | Última sincronização | — | Pendências |
| CF-05 Uso por talhão | Onde · Tabela | — | — | — | Fazenda, Talhão | Área cultivável |
| CF-05 Faturas | Quando · Tabela | Regra | — | Competência, Vencimento | — | Área cobrada, Valor |
| CF-05 Planos | O quê · Comparar | Plano, Módulos | Usuários | — | — | Preço R$/ha·mês, Valor para a sua área |

#### Outros acessos

| Tela · listagem | Abre em | O quê | Quem e como | Quando | Onde | Quanto |
| --- | --- | --- | --- | --- | --- | --- |
| MB-01 App de campo · minha fila | Quando · Cartões, sem seletor | Tipo de trabalho | Eu | Hoje | Mapa só com deslocamento: MB-02det, MB-06, MB-07 | — |
| PT-01 Portal · oportunidades | Quando · Tabela | Oportunidade | Convite e acesso | Prazo | — | — |
| ON-01 Onboarding · passos | Assistente por etapas, sem seletor | Passo | — | — | — | — |
| BO-02 Backoffice · organizações | Quem e como · Tabela | Plano | Organização | Próximo evento | — | Área medida, Área contratada, Mensalidade |
| BO-02 Fila de cobrança | Quando · Feed | Evento, Fatura | Organização | — | — | Valor |

### Colunas: só o essencial

Toda Tabela abre só com as colunas que decidem; o resto fica a um clique, no seletor de colunas. Nas 86 listagens do menu, 380 de 658 colunas abrem visíveis e 278 vão para Mais colunas.

- **Essencial é o que decide.** Fica a coluna que identifica o item, a do foco de entrada, até 3 números que mudam a decisão e o próximo passo. No máximo 6 colunas no computador; no celular, as 3 primeiras.
- **Situação vira ícone.** As colunas Situação, Estado e Condição saem do padrão: o estado aparece como ícone com cor antes do nome. Fica escrita só quando traz o próximo passo ("Situação · próximo passo").
- **O grupo já diz, a linha não repete.** A coluna usada pelo foco ou pela árvore sai das linhas e vai para o cabeçalho do grupo; coluna com o mesmo valor em todo o recorte (uma só fazenda filtrada) vai para o título.
- **Unidade vai junto do número:** "120 L", não uma coluna Un.
- **Saem do padrão:** contatos e documentos (WhatsApp, e-mail, CPF/CNPJ), datas de cadastro e de vigência, versões, parâmetros técnicos e colunas que se calculam das que ficaram (Polígono, quando Área e Diferença estão).
- **Listagem com até 5 colunas fica inteira.** O app de campo não ganha seletor: cada tarefa já mostra só o essencial.

#### Seletor de colunas

- **Um ícone na barra:** `view_column`, com o número de colunas ocultas ("+6"). Abre um painel com as colunas agrupadas por foco (O quê, Quem e como, Quando, Onde, Quanto, Situação), com os mesmos ícones.
- **Marcar mostra, desmarcar oculta, arrastar reordena.** A primeira coluna (identidade) fica travada; "Restaurar padrão" volta ao essencial; busca no painel quando houver mais de 12 colunas.
- **Atalho no cabeçalho:** o menu ⋯ de cada coluna tem "Ocultar coluna".
- **A escolha é de cada usuário.** Fica por usuário × listagem e volta igual no próximo acesso.
- **Oculta não é apagada.** Colunas ocultas seguem valendo para busca, filtros e foco; exportar leva as visíveis, com a opção "Todas as colunas".
- **Cartões usam o mesmo seletor:** ele escolhe os até 2 números do cartão fechado; os demais aparecem ao abrir.

#### Colunas · Mapa e Cadastros

| Tela · listagem | Abre com | Em Mais colunas |
| --- | --- | --- |
| CD-01 Talhões | Fazenda › talhão, Área cultivável, Diferença, Parcelas na safra 2026/27 | Situação, Sistema, Polígono |
| CD-01 Água | Ponto de água, Vencimento, Vazão, Uso | Situação, Fazenda, Documento, Curso d’água |
| CD-01det Parcelas | Safra › parcela, Cultura, Área, Plantio | Situação, Tipo, Cultivar, Livre |
| CD-02 Culturas e cultivares | Cultura › cultivar, Ciclo, Cultivos | Situação, Tipo de ciclo, Unidade de produtividade, Item de semente |
| CD-03 Máquinas e instalações | Máquina ou instalação, Custo R$/h, Próxima calibração | Situação, Classe, Conjuntos |
| CD-03 Conjuntos | Conjunto, Operações, Rendimento | Largura, Condição, Operadores alocáveis |
| CD-04 Pessoas | Pessoa, Equipe, Validade da habilitação, Habilidades | Situação, Vínculo, Disponível até, Custo R$/h, Habilitação |
| CD-05 Parceiros | Parceiro, Papéis, Contato | Situação do papel, CPF/CNPJ, WhatsApp, E-mail, Canais autorizados |
| CD-06 Itens | Grupo › item, Unidade, Preço de referência | Situação, Natureza de custo, Embalagem, Data do preço |
| CD-07 Estrutura gerencial | Dimensão › código, Nome, Conta no ERP (Sankhya) | Situação, Início da vigência, Fim da vigência, No rascunho |
| CD-08 Operações e rendimentos | Operação › conjunto, Cultura, Rendimento, Custo R$/ha | Fonte, Processo, Custo R$/h |

#### Colunas · Agrícola

| Tela · listagem | Abre com | Em Mais colunas |
| --- | --- | --- |
| AG-07 Produtos | Produto · registro, Ingrediente ativo · grupo químico, Classe · modo de ação, Na fazenda | Culturas, Alvos, Tox · amb |
| PA Atividades do plano (Cartões) | Gatilho, Atividade, Insumos, Custo/ha; ao abrir: Produto, Dose/ha, Custo/ha | Grupo e Preço unitário do insumo |
| PA Cultivos que usam o plano | Talhão ou parcela, Área, Versão aplicada | Safra, Cultura e variedade, Situação |
| AG-02 Laudos | Laudo, Fazenda · talhão, V %, K, Coleta | Profundidade, Situação, No plano |
| AG-02 Água no solo | Medição, Talhão · zona, Data, CAD | Profundidade, Método, Capacidade de campo, Ponto de murcha, Fonte · responsável |
| SAF Safras | Safra, Fazenda, Próximo passo, Área | Cultivos, Estado |
| SAF Talhões e cultivos | Talhão ou parcela, Cultura, Plantio, Plano agronômico, Área, Ocupa até | Situação, Área livre, Livre a partir de, Fim por, Safra, Variedade, Versão, Meta, Ajustes locais, Tipo |
| SAF Operações | Operação › atividade › talhão, Data, Conjunto, Horas-conjunto, Custo total | Situação, Rendimento, Área trabalhada, Custo R$/ha |
| SAF Rendimentos | Operação, Conjunto, Rendimento, Custo R$/ha, Janela por talhão | Atividade, Custo R$/h, Custo R$/kg, Modo, Largura, Velocidade, Eficiência, Parte da área, Trabalha, Planos |
| SAF Recursos no pico · máquinas | Recurso, Unidades, Necessárias no pico, Mês do pico | Jornada, Turnos, Disponibilidade |
| SAF Recursos no pico · pessoas | Recurso, Pessoas, Necessárias no pico, Mês do pico | Jornada, Absenteísmo |
| SAF Demanda de insumos | Grupo, Insumo, Falta em, Necessidade líquida, Valor | 1º uso, Situação, Solicitação, A complementar, Demanda bruta, Antes de hoje sem O.S., Estoque apto, Usado antes da compra, Reservado, Recebimentos previstos, Recebido após a falta, Coberta em, Preço |
| SAF Sugestões do laudo | Talhão, Atividade · produto, Padrão, Sugestão | Diferença no talhão, Laudo, Tipo, Resultado |
| GE-02 Orçamento · versões | Versão, Custo total, Pico de caixa, Estado · aprovação | Premissas, Volume soja, Preço soja |
| OS Ordens de serviço | O.S., Atividade, Talhão, Prazo, Fase, Progresso | Local, Área, Início, Fim, Situação, Observação, Quem resolve, Próxima ação, Realizado, Saldo, Dispensado, Responsável |
| AG-01 Vistorias | Vistoria, Alvo, Contagem × NC, Talhão · cultura, Próximo passo | Data, Situação |
| AG-01det Pontos da rota | Ponto, Contagem, × NC, Fotos | GPS, Hora, Qualidade |
| IR-01 Setores | Setor, Déficit hoje, Próximo passo, Próxima passada | Fazenda, Situação, Pendência, Necessidade bruta, Ordem, Cobertura |
| IR-02 Programação | Captação › ordem, Início, Lâmina, Setor, Fim, Próximo passo | Etapa, Pendência, Avisos |
| IR-03 Ordens de irrigação | Ordem, Setor, Próximo passo, Início, Lâmina, Etapa | Fazenda, Pendência, Responsável, Tipo, Fim |
| IR-04 Fontes de clima | Fonte, Grandeza, Atualização, Efeito no balanço | Fazenda, Estado, Unidade, Calibração, Validade da calibração, Cobertura |
| IR-04 Captações | Captação, Vazão outorgada, Uso do dia, Vencimento | Fazenda, Situação, Outorga, Regime, Volume hoje, Setores ligados |
| IR-04 Desempenho por setor | Setor, Lâmina aplicada, Eficiência, Variação da eficiência | Cultura, Volume, Energia |
| COLH Previsão por talhão | Talhão · variedade, Situação · próximo passo, Previsão, Colhido, Referência · desvio | Cultura, Área, Produtividade |
| CARGA Cargas | Carga · ticket, Situação · próximo passo, Líquido, Origem | Cultura, Colheita · recebimento, Comercial, Lote · local |
| BEN Ordens de beneficiamento | Ordem, Produto, Próximo passo, Fase, Em processo | Condição, Quem resolve |
| PROD Lotes de produto | Lote · produto, Disponível, Qualidade · próximo passo, Físico, Local · validade | Produto, Bloqueado, Em processo, Apto, Reservado |
| GE-03 Composição de custos | Origem (documento), Componente, Dimensões, Valor | Qtd × preço, Rateio, Estado |

#### Colunas · Manutenção

| Tela · listagem | Abre com | Em Mais colunas |
| --- | --- | --- |
| MA Sem ordem | Item, Ativo · leitura, O que, Prazo, Próximo passo | Peças |
| MA Ordens | Ordem · ativo, Serviço · tipo, Janela, Executante, Fase | Pendência, Tempo, Custo |
| MA Ativos | Ativo · local, Em aberto, Próxima manutenção, Leitura | Condição, Custo no mês, Consumo |
| MA Abastecimentos | Lançamento · operador, Ativo, Data · leitura, Volume, Consumo | Tanque/lote, Método, Qualidade |
| MA Planos | Plano, Aplica-se a, Serviços, Ativos | Estado, Situação |

#### Colunas · Suprimentos

| Tela · listagem | Abre com | Em Mais colunas |
| --- | --- | --- |
| CMP Demanda por grupo | Grupo · insumo, Falta a partir de, Necessidade (com a unidade), Valor, Na compra | Bruta, Estoque apto, A receber, Preço ref. |
| CMP Fornecedores homologados | Grupo · fornecedor, Convite, Responder até, Resposta | Homologação, Canal e contato |
| CMP Propostas | Grupo · insumo · proposta, Custo, Escolha, Preço, A pedir, Entrega | Frete, Pagamento, Validade |
| CMP Alçada de aprovação | Pedido · fornecedor · insumo, Quantidade, Preço, Entrega, Valor | Frete, Pagamento |
| CMP Pedidos e entregas | Pedido · fornecedor · insumo, A entregar, Previsão, Ação | Pedido, Recebido, Valor, Situação |
| EST Recebimentos | Nota fiscal, Item, Divergência, Fornecedor, Na nota, Conferida | Data da nota, Conferida em, Pedido, Lote, Apta, Quarentena, Situação, Validade |
| EST Entregas por O.S. | Requisição, Item, A entregar em embalagens, O.S., Lote, A entregar | Fase da O.S., Embalagem, Solicitado, Entregue, Situação, Detalhe |
| EST Custódia e devoluções | Requisição, O.S., Item, Em custódia, Com quem | Lote, Entregue, Consumido, Devolvido, Encerramento da O.S., Detalhe |
| EST Saldos por lote e local | Item › lote, Local, Físico, Disponível, Validade | Item, Reservado, Bloqueado, Em conferência, Em custódia (fora do depósito), O.S. com custódia, Situação do lote |
| EST Contagens | Contagem, Item, Local, Diferença, Ação | Ajuste, Lote, Sistema na data de corte, Contado, Situação |
| EST Movimentos | Hora, Movimento, Item, Quantidade, Quem | Registro, Condição, Documento, O.S., Lote, Origem, Sinal do app |
| IC Preço e melhor mês | Insumo, O que fazer, Economia estimada, Preço agora, Mês mais barato | 12 meses, Tendência, Próxima necessidade |
| IC Preço por insumo | Insumo, Último pago, Melhor cotação, vs último, Sinal | Grupo, Referência, vs referência |

#### Colunas · Comercial

| Tela · listagem | Abre com | Em Mais colunas |
| --- | --- | --- |
| PCOM Oferta e compromissos | Produto › período, Oferta, Compromissos, Livre para vender | Coberto por lote, Situação |
| PCOM Preço e recebimento | Produto, Preço médio realizado, A receber, Preço médio contratado, Referência de mercado, Vencido | Vendido, Entregue |
| VEN Vendas | Venda · cliente, Situação · próximo passo, Falta, Produto, Quantidade, Preço | Tipo · janela, Entregue, Reservado |
| EXPED Cargas de saída | Carga · romaneio, Data, Situação · próximo passo, Venda · cliente, Previsto | Produto · lotes, Saída, Modalidade · veículo |
| IV Preço e melhor mês | Produto, O que fazer, Preço agora, Agora vs normal do mês, Melhor mês para vender | 1 mês, 12 meses, Tendência |
| IV Safra comercializada | Produto, Oferta da safra, Comercializado, Livre para vender | Vendido, Situação |
| IV Recebimento líquido | Venda, Cliente, Preço, Líquido | Produto, Frete, Prazo, Custo do prazo |

#### Colunas · Configurações

| Tela · listagem | Abre com | Em Mais colunas |
| --- | --- | --- |
| CF-04 Trilha | Quando, Quem, O quê, Objeto, Antes → depois / efeito | Origem |
| CF-03 Conexões | Conexão, Última sincronização, Pendências | Traz / leva, Estado, Credencial |
| CF-05 Faturas | Competência, Área cobrada, Valor, Vencimento | Regra, Estado |
| CF-05 Planos | Plano, Módulos, Preço R$/ha·mês, Valor para a sua área | Limite de área, Usuários, Franquias, Mínimo R$/mês, Situação |

#### Colunas · Outros acessos

| Tela · listagem | Abre com | Em Mais colunas |
| --- | --- | --- |
| BO-02 Organizações | Organização, Plano, Mensalidade, Fatura aberta, Próximo evento | Estado, Área medida, Área contratada |
| BO-02 Fila de cobrança | Evento, Organização, Valor, Resultado | Fatura, Situação |

Ficam inteiras, por terem até 5 colunas: CD-01 Fazendas; CD-01 Ambiental; CD-04 Equipes; CD-05 Cobertura de cotação; CD-06 Locais de estoque; PAGR Colheita prevista e recebida; GE-02 Cronograma de caixa; COLH Previsão por semana; CMP Safras e solicitações; IC Fornecedores; IC Custo por hectare; IV Preço × mercado; CF-01 Pessoas; CF-01 Alçadas; CF-05 Uso por talhão; PT-01 Oportunidades; PT-01 Avisos.

### Telas fora do menu

Dos 155 arquivos, 41 estão no menu, 7 são índices (Cadastros e os 6 módulos), 8 redirecionam (MA-01 a MA-05, MA-04det, PM e Main) e os demais se abrem por link. As famílias abaixo repetem telas do menu; não vale investir foco nelas, exceto Finanças, que é única.

| Família | Telas | Repete | Se a tela ficar |
| --- | --- | --- | --- |
| Finanças e gestão | GE-01 Visão gerencial, GE-04 Contas a pagar e caixa, GE-05 Contas a receber, GE-06 Indicadores, GE-07 Planos de ação, GE-08 Crédito e garantias | nada; GE-02 e GE-03 já estão no Agrícola | Menu próprio; GE-04 e GE-05 em Quando · Calendário de vencimentos, GE-08 em Quando · Linha do tempo |
| Diagnóstico agrícola | AG-03 Diagnósticos, AG-04 Recomendações, AG-05 Biblioteca e planos técnicos, AG-06 Eficácia e histórico | abertas por Pragas, Análises de solo e Mapa | AG-03 em Situação · Kanban (hipótese, confirmado, decisão); AG-06 em Quanto × Quando · Gráfico |
| Planejamento | PL-01 a PL-06 | SAF, OS | PL-02det já converte gatilho em data: base do Quando |
| Campo | CA-01 a CA-04 | OS, EST, app | CA-01 tem seletor próprio Lista, Kanban, Mapa |
| Colheita | CO-01 a CO-07 | COLH, CARGA, BEN, PROD, EXPED | redirecionar |
| Vendas | VE-01 a VE-06 | VEN, PCOM, IV | redirecionar |
| Logística | LO-01 a LO-04 | EXPED | LO-01 em Quem e como × Quando · Carga (doca × hora) |
| Suprimentos | SU-01 a SU-09 | CMP, EST | redirecionar |
| Início | IN-01 Meu dia, IN-02 Aprovações, IN-03 Agenda e pendências | app, alçadas | IN-03 em Quando · Calendário |
| Portal | PT-02 a PT-07 | abertas pelo PT-01 | Tabela |
| App de campo | MB-02 a MB-10 | abertas pelo MB-01 | Cartões, sem seletor |

### Achados

O inventário de 14/10/2026 leu os 155 arquivos: o menu mudou, há seletores próprios em 7 telas e sete telas seguem sem caminho de chegada.

- **O menu mudou.** São 8 itens: Mapa, Cadastros, Agrícola, Manutenção, Suprimentos, Comercial, Configurações e Outros acessos. Produção entrou no Agrícola, que ganhou Painel, Beneficiamento, Orçamento (GE-02) e Custos (GE-03); Manutenção e Suprimentos ganharam Painel. O Mapa tem 11 camadas.
- **Seletores próprios viram foco ou Ver como.** COLH "Por talhão / Por semana" é o foco Onde ou Quando; AG-01 "Agrupar vistorias por" (Talhão, Alvo, Situação, Fazenda) é o foco. CD-01 "Lista / Mapa", BEN "Lista / Kanban" e CA-01 "Lista / Kanban / Mapa" vão para o Ver como. A O.S. já usa o motor com 5 visões; o "Agrupar por" do AG-07 não tem opções.
- **"Visão" da Manutenção não é visão.** Troca entre 4 listagens (Sem ordem, Ordens, Ativos, Planos) que o menu já mostra; vira abas, para não confundir com o Ver como.
- **Telas sem link de chegada:** GE-01, IN-03, PL-03, PT-06, MB-05det, MB-08 e o recibo dela. A busca leu também o código das telas; um link montado por partes ainda pode escapar. MB-08 pesa mais: o irrigante não chega à tarefa dele pelo app.
- **Finanças ainda sem menu:** GE-01 e GE-04 a GE-08.
- **Duplicação:** CO, VE, SU, PL, CA e LO repetem telas do menu; o caminho é redirecionar, como MA-01 a MA-05 e PM já fazem.

### Ordem de implementação

Começar pelo motor e pela O.S., que já tem 5 visões, e seguir pelas listagens que mudam decisões de maior valor.

1. Motor: marcas de foco, tipo e níveis nas colunas; barra única com seletor de colunas e padrão essencial; descer com trilha; Tabela e Cartões; padrão visual.
2. O.S. como piloto: as 5 visões passam a sair do foco, e a O.S. abre pelo foco do perfil.
3. Planejar safra e Planos agronômicos: ocupação (Onde × Quando), capacidade (Quem e como × Quando), demanda (O quê × Quando) e as Atividades do plano em Cartões por DAP.
4. Pragas (Onde × O quê) e Colheita (Onde × Quando): decisões semanais de maior custo.
5. Painel comercial e Compras: oferta livre (O quê × Quando) e Comparar propostas.
6. Manutenção, Irrigação e Beneficiamento: operação do dia em Carga e Kanban.
7. Cadastros, Configurações e demais: Tabela com foco e descida.
