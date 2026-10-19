PROJETO: Safrion (Do Talhão à O.S.) · EX-52 · Ideias dos jogos e simuladores de fazenda

PEDIDO DO PROPRIETÁRIO (18/10/2026)
Perguntou quais são os jogos e simuladores de gestão de fazenda mais completos, interativos e intuitivos do mundo. Depois da resposta, pediu: "transforme as ideias dos jogos e simuladores em um EX-52, com prompt próprio e entrada no prompt unificado."

COMO TRABALHAR (protocolo da equipe, sem exceção)
1. Leia AGENTS.md, docs/STATUS.md, o cabeçalho do checkpoint da issue #1 e o protocolo canônico. Este prompt não substitui o PRD nem as decisões NAV/DS.
2. Antes de qualquer código, Claude e Codex melhoram este desenho de forma independente: cada um confere no protótipo o que já existe, aponta o que está errado ou faltando e decide, para cada ideia, Adotar, Adaptar (com o como) ou Rejeitar (com o motivo). Divergência se resolve por fonte ou reprodução. O Codex registra a decisão no checkpoint (só ele edita o checkpoint).
3. Gemini real só se houver divergência material de domínio (candidatos: J1, o ciclo do talhão, e J8, o "e se?" com modelo de cultura). Pacote mínimo, sem dados reais. Não simule nenhum modelo.
4. Só depois implante, por fatias, com revisão cruzada: quem revisa integra o PR do outro.

ESPÍRITO DO ITEM
Os jogos de fazenda resolvem bem uma coisa que sistemas de gestão costumam resolver mal: a pessoa vê o estado do trabalho de relance, sabe o que fazer agora e entende a consequência antes de agir. O EX-52 traz esses padrões de interação para o Safrion. Não traz o jogo: nada de pontos, medalhas, ranking entre pessoas, tempo acelerado ou 3D decorativo. Cada ideia precisa passar pelo critério de entrada da seção 7 do prompt unificado (ganho medido, decisões fixas preservadas, custo proporcional).

REFERÊNCIAS (o padrão a observar; ninguém precisa jogar para implantar)
- Farming Simulator 25 (GIANTS, 2024) com o Precision Farming 3.0 gratuito: amostra de solo, mapa de produtividade, dose variável, sensores e relatório econômico e ambiental por talhão; GPS que traça e dirige a rota no talhão e ajudantes que executam a tarefa. https://farmingsimulator.wiki.gg/wiki/Precision_Farming/Farming_Simulator_25 · https://g-portal.com/en/blog/farming-simulator-25-GPS-and-AI-helpers
- Farming Simulator 26 (2026, Switch e celular): desafios semanais e por estação ao longo das cadeias de produção, tutoriais para quem começa. https://press.giants-software.com/category/farming%20simulator%2026
- Professional Farmer: Cattle and Crops (1.0 em 2020): mais de 50 tutoriais e cenários, modo carreira ou livre, funcionários com tarefas. https://www.toplitz-productions.com/news-2388/professional-farmer-cattle-and-crops-1-0-release-on-october-15-2020.html
- Farm Manager World (2025): equipe por habilidade, várias regiões, cadeias de processamento; a logística é criticada por ser lenta e mal explicada (lição do que não fazer). https://www.gamedeveloper.com/press-release/farm-manager-world-full-release · https://vaporlens.app/app/2206350/farm_manager_world
- Hay Day: quadro de pedidos que mostra o que falta para entregar; cada prédio mostra a sua fila e o tempo restante.
- Stardew Valley: calendário de estações e maturação visível na própria lavoura.
- FARMPILOT (Universidade de Gießen): planejar um ano inteiro da fazenda com produção, insumos, pessoal e finanças, num modelo de simulação. https://dl.gi.de/items/54a5f927-03ef-4fff-9824-e3f94593abe1/full
- APSIM, DSSAT e AquaCrop (FAO): modelos de cultura usados como apoio à decisão, com clima, solo, água e nitrogênio. https://www.mdpi.com/2077-0472/11/11/1166

O QUE JÁ EXISTE NO PROTÓTIPO (1792184197-5a81; conferir de novo na versão vigente)
- Mapa (IN-04): 9 camadas, entre elas Ordens de serviço (Mostrar Fases, Avanço, Atrasos, Impedimentos ou Insumos), Solo (mapa de calor IDW do laudo), Colheita e produtividade, e Custos (previsto R$/ha ou realizado × previsto). Detalhe no anexo-mapa-analise.md (EX-44).
- Análises de solo (AG-02): o laudo validado sugere a dose no plano ("Ver no plano"); o laudo por zona não sugere dose, com o texto "taxa variável fora do escopo".
- Satélite no Mapa: "o índice não aciona compra nem prescrição".
- Ordem de Serviço: é a única tela com visões além da tabela: Tabela, Cartões, Kanban, Calendário e Carga por recurso (G2_VISOES g_os). Manutenção, Beneficiamento, Estoque, Colheita, Cargas e Planejar safra não têm calendário nem carga por recurso.
- Orçamento (GE-02 e GE-02det): versões V1 × V2 × real, base natural para comparar cenários.
- Onboarding (ON-01) com passos; perfil de demonstração ("não é segurança de acesso") e "Restaurar demonstração" sobre um cenário único. Não existe modo treino isolado.
- App de campo (MB-01): simulação "com sinal / sem sinal", só para demonstração.

AS OITO IDEIAS
Para cada uma: referência · o que fazer no Safrion · onde · cuidado · aceite.

J1 Ciclo do talhão (Precision Farming)
- Fazer: no painel do talhão (Mapa e cadastro do talhão), uma seção "Ciclo desta safra" que liga o que hoje está em camadas separadas: laudo de solo → dose do plano e O.S. de correção e adubação → aplicações realizadas → produtividade colhida → custo realizado → resultado por hectare. Cada elo é link (EX-51) e mostra o que falta ("sem laudo", "colheita prevista", "custo parcial: falta preço").
- Onde: painel do talhão do IN-04 e CD-01det; dados das camadas Solo, Ordens de serviço, Colheita e produtividade e Custos, e de COLH e GE-03.
- Cuidado: número parcial diz que é parcial; custo por hectare não se soma entre talhões; resultado só com preço de venda real ou de referência declarado. Dose variável por zona continua fora do escopo vigente (texto do AG-02): Claude e Codex avaliam custo × ganho e só levam ao proprietário se recomendarem incluir, com o RT validando a regra agronômica.
- Aceite: para um talhão colhido do cenário, a seção mostra os seis elos com origem e unidade, os mesmos números das camadas e do GE-03 (EX-51 R8), e cada elo abre o seu registro.

J2 Trabalho andando no mapa (GPS do Farming Simulator)
- Fazer: na camada Ordens de serviço (Mostrar Avanço), pintar dentro do polígono a fração realizada da O.S. em execução, com rótulo "48 de 96 ha · ritmo 24 ha/dia · termina 12/09" e a hora do último apontamento. O apontamento enviado pelo app atualiza o mapa (evento do EX-51).
- Onde: IN-04, camada Ordens de serviço; cálculo do ritmo pelos apontamentos conferidos e provisórios, separados.
- Cuidado: sem telemetria ou as-applied, a área pintada é proporção, não posição: a legenda diz isso e o desenho não sugere a faixa exata feita. Provisório e conferido têm estilos diferentes. Não criar camada nova (a barra continua com 9 nomes).
- Aceite: OS-0420 e OS-0421 em execução mostram fração, ritmo e previsão de término coerentes com os apontamentos; enviar um apontamento no app muda o mapa sem recarregar a tela.

J3 Fila por recurso com tempo restante (Hay Day; lição da logística do Farm Manager World)
- Fazer: levar a visão "Carga por recurso" da O.S. ao motor e usá-la onde há recurso com fila: oficina e mecânicos (Manutenção), linhas de packing e beneficiamento (Beneficiamento), separação do almoxarifado (Estoque), balança (Cargas). Cada recurso mostra em execução, na fila, tempo restante estimado e o gargalo do dia; clicar no item abre o detalhe (EX-49) e a fila nunca esconde o motivo da espera.
- Onde: motor de grades (uma visão nova reaproveitada, não telas novas) e as quatro telas acima.
- Cuidado: tempo restante é estimativa com a base declarada (rendimento do CD-08, média dos apontamentos); recurso único sem dupla alocação (Onda 0); a peça continua reservada para a ordem que pediu.
- Aceite: nas quatro telas, a visão abre com dados do cenário, o gargalo aparece em texto e cor, e os totais batem com a lista.

J4 Pedido mostra o que falta (quadro de pedidos do Hay Day)
- Fazer: um componente único de cobertura "tem · chega · falta", com data de chegada × data de necessidade, usado na O.S. (insumos, já pedido no EX-45), na ordem de manutenção (peças) e no pedido de venda (lotes aptos × quantidade; ex.: PV-031 "Falta 10.000 kg"). Cada "falta" traz a ação de 1 clique para quem resolve (EX-45) e cria a pendência (EX-51).
- Onde: componente do motor, usado em OS, MA e VEN.
- Cuidado: o servidor decide saldo e reserva; o componente só mostra o recibo.
- Aceite: OS-0502, uma OM com peça sem saldo e a PV-031 mostram a mesma barra, com os mesmos números do Estoque e do Estoque de produto.

J5 Calendário da safra (Stardew Valley)
- Fazer: uma visão Calendário por talhão × semana com janela de cada operação, estádio, maturação prevista, colheita e carência, reaproveitando o calendário que a O.S. já tem. Clicar na faixa abre a O.S., a previsão ou o talhão.
- Onde: como visão do Planejar safra (SAF) e de Previsão e colheita (COLH); não é item de menu.
- Cuidado: datas previstas e realizadas com estilos diferentes; carência sempre visível quando corta a colheita.
- Aceite: para a safra 2026/27, o calendário mostra todos os talhões com janela e colheita, e a OS-0502 aparece com a janela 25–27/09 (ou a reprogramada).

J6 Modo treino com cenários guiados (Cattle and Crops; FARMPILOT)
- Fazer: uma organização de treino isolada, com o cenário de exemplo ou uma cópia anonimizada da fazenda, marca visual permanente "Treino" e cenários guiados por persona: Ana aprova uma O.S. e decide uma falta; Rui recebe e separa; Caio reprograma; Paula confere apontamentos; Otávio e Zé abrem e fecham uma OM. "Recomeçar" volta o cenário ao início. Serve ao onboarding (ON-01) e a quem entra na equipe.
- Onde: entrada pelo ON-01 e pelo menu do avatar; fora da barra principal.
- Cuidado: isolamento real (outra organização, nunca dados misturados), sem efeito externo (integração com ERP, e-mail, pedido ao fornecedor, banco), o perfil de demonstração atual não é segurança e não serve de base. A forma técnica fica com Claude e Codex.
- Aceite: completar cada cenário em minutos sem ajuda externa, com o passo atual e o próximo sempre visíveis; nenhuma ação do treino aparece na organização real.

J7 Progresso da semana por pessoa (desafios do FS26, com moderação)
- Fazer: no Meu dia, uma linha de progresso real da semana da pessoa: "6 de 9 O.S. na janela · 2 impedidas · 1 atrasada", com link para cada grupo.
- Onde: Meu dia (EX-50 e EX-51).
- Cuidado: sem pontos, medalhas, sequência de dias ou ranking entre pessoas. Nunca medir velocidade de aprovação agronômica nem premiar volume de liberações (decisão fixa: aprovação individual). O número vem da mesma fonte das listas.
- Aceite: os números batem com as listas filtradas; nada no indicador incentiva aprovar mais rápido.

J8 "E se?" no planejamento (APSIM, DSSAT, AquaCrop)
- Fazer, em duas etapas: (a) já: comparar cenários com os dados que existem, como versões do orçamento (data de plantio × janela, preço, produtividade histórica do talhão), reaproveitando o V1 × V2 × real do GE-02; (b) estudo: quais dados o Safrion já tem (clima, solo, cultivar, data de plantio, irrigação) e quais faltam para um modelo de cultura, com custo, licença e validação. O modelo só entra com o RT validando os parâmetros por cultura e região.
- Onde: Planejar safra e Orçamento.
- Cuidado: não é IA generativa, mas tem custo de cálculo e risco de virar recomendação; nenhum número simulado vira dose, compra ou previsão oficial sem decisão humana. Tratar como o motor estatístico do EX-43.
- Aceite (a): duas versões de cenário lado a lado para a safra, com premissas visíveis e diferença em R$ e em t/ha. Aceite (b): relatório do estudo com recomendação registrada no checkpoint.

O QUE NÃO COPIAR DOS JOGOS
- Pontos, medalhas, sequências, ranking entre pessoas e recompensas.
- Tempo acelerado, eventos aleatórios e "contratos" de jogo.
- 3D e animação decorativos; movimento só quando informa o estado e respeitando a redução de movimento.
- Regra escondida: a logística opaca do Farm Manager World é o exemplo do que frustra; toda espera mostra o motivo e quem resolve.

DECISÕES
- Dose variável por zona (J1): fora do escopo vigente. Claude e Codex recomendam; vai ao proprietário só se recomendarem incluir.
- Modo treino (J6): a forma técnica do isolamento é de Claude e Codex.
- Modelo de cultura (J8): estudo primeiro; entrada só com validação do RT.

FATIAS (ordem sugerida; Claude e Codex podem reordenar com motivo)
F1 J4 (componente de cobertura) junto com o EX-45, e J2 (trabalho andando) junto com o EX-44.
F2 J3 (carga por recurso no motor) e J5 (calendário da safra).
F3 J1 (ciclo do talhão), depois que o EX-51 ligar as referências e o GE-03 ler o cenário.
F4 J7 (progresso da semana), depois do Meu dia visível (EX-50) e das pendências (EX-51).
F5 J6 (modo treino) e J8 (a), com o estudo J8 (b) em paralelo.
Cada fatia: desenho independente de Claude e Codex → aceite medido antes do código → implantação → revisão cruzada → robô de passagens (EX-51) e de listas (EX-49) de novo → publicação no artefato existente com versão e mudança concreta.

NÃO FAZER
- Criar item novo na barra principal (desde 18/10 ela tem 10, com o Painel) ou nome novo na barra de camadas do Mapa (continua com 9 camadas).
- Gamificar aprovação, liberação ou qualquer controle de risco.
- Mostrar estimativa como fato: ritmo, tempo restante e cenário sempre com a base declarada.
- Ligar automação de IA sem a estimativa de custo.

ENTREGA (no canal registrado)
- Para cada ideia J1–J8: validação (o que já existe, com arquivo e trecho), decisão de Claude, decisão do Codex, decisão final, fatia e aceite.
- Recomendação sobre dose variável por zona e sobre o modelo de cultura, com custo e ganho.
- Três listas curtas, com motivo: aplicado, deixado de fora, cortado. Suposições e pendências com gatilho de retomada.
