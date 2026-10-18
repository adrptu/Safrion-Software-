PROJETO: Safrion (Do Talhão à O.S.) · EX-56 · Varredura final, melhoria final e encerramento do protótipo

PEDIDO DO PROPRIETÁRIO (18/10/2026)
"Quando o Claude terminar de implantar tudo que está em andamento atualmente no Safrion, faça uma varredura completa em todos módulos, funcionalidades e telas e sugira melhorias para sermos imbatíveis e os melhores na gestão do agro. E faça como se fosse o conjunto dos melhores agrônomos, engenheiros de manutenção, engenheiro agrícola, engenheiro de processos, engenheiro de produção, gerentes e diretores de suprimentos, compras, estoque e comercial, especialistas em design system, UX, UI, regras de negócio, etc. de toda a história humana e das melhores referências mundiais de software em cada funcionalidade. Mantendo sempre o essencialismo, minimalismo e intuitividade, praticidade, rapidez e beleza máximos; também o mínimo de cliques e digitações possível, menos etapas e menos idas e vindas em telas e botões para a gestão no sistema. E faça a melhoria final; aí vamos encerrar a fase de protótipo e começar a fazer o software real."

QUANDO COMEÇAR (portão)
Este item é o último do protótipo. Só começa quando o checkpoint (issue #1) mostrar, ao mesmo tempo:
- todos os outros itens EX (EX-01 a EX-55, EX-57 e qualquer item criado antes do portão) com decisão final registrada (Adotar, Adaptar ou Rejeitar, com motivo);
- todos os adotados implantados no protótipo, revisados pelo outro agente e com aceite e evidência;
- uma candidata completa e operável identificada por versão, URL, fontes, diff e provas.
Se faltar algo, não comece: registre o que falta, quem resolve e o gatilho de retomada. Não ande em paralelo com implantação ainda aberta.

COMO TRABALHAR (protocolo canônico, sem exceção)
1. Leia AGENTS.md, docs/STATUS.md, o cabeçalho do checkpoint e o protocolo. Esta é a auditoria integral prevista no protocolo: Codex, Claude e Gemini reais auditam a mesma candidata, com o mesmo inventário e análise dos brutos. Ferramenta indisponível fica bloqueada; não simule nenhum modelo.
2. Cada agente faz a sua varredura sozinho; depois cruzam. Divergência se resolve por fonte ou reprodução, não por voto. O Codex registra no checkpoint (só ele edita o checkpoint).
3. As "lentes de especialista" abaixo são listas de verificação que cada agente aplica. Não são pessoas simuladas: nenhum achado é atribuído a especialista inventado; cada achado traz evidência verificável.

ETAPA 1 · INVENTÁRIO COMUM (medido, não estimado)
Rode de novo, na candidata, os robôs que já existem e um novo:
- robô de inventário e cliques (anexo-robo-varredura.html, EX-46 a EX-48): telas, campos, origem de cada valor, ações, lotes, primárias;
- robô de listas (anexo-robo-v4.html, EX-49): linha, pai, filho, ⋯, botões, tabela e cartões;
- robô de passagens (anexo-robo-v5.html, EX-51): IDs clicáveis, chegada no registro, volta à origem, Voltar que reabre, escopo;
- robô de jornadas (novo, v6): executa as tarefas da tabela "ORÇAMENTO DE ESFORÇO" como cada persona e mede cliques, toques, campos digitados, telas visitadas, idas e vindas, tempo de resposta e erros;
- acessibilidade automática (WCAG 2.2 AA) em todas as telas, teclado e leitor de tela nas jornadas;
- desempenho (LCP, INP, CLS no percentil 75) no desktop e num celular de entrada, com rede lenta e sem sinal no app;
- celular: cada tela a 375 px, sem rolagem lateral, alvos de 44 px.
Guarde os brutos com versão e data. Os números de antes (EX-46, EX-49, EX-51, EX-53) são a linha de base.

ETAPA 2 · LENTES DE ESPECIALISTA (cada achado diz qual lente, tela, persona e evidência)
1. Agronomia: planejamento da safra e dos cultivos, plano agronômico, receituário, MIP (amostragem, nível de controle, decisão, eficácia, Raio-X do alvo), nutrição e solo, irrigação, estádio, colheita e produtividade. Pergunta: o agrônomo decide certo, rápido e com rastro, sem procurar informação em outra tela?
2. Engenharia agrícola: conjuntos, capacidade de campo e rendimento, frentes de trabalho e rota (EX-54), pulverização (calda, volume, clima, deriva, lavagem), perdas, telemetria. Pergunta: a máquina passa o máximo de tempo produzindo na janela certa?
3. Manutenção (PCM): preventiva por horímetro e tempo, preditiva, ordem de manutenção, peça reservada para a ordem, disponibilidade, MTBF, MTTR, custo por hora, impacto na produção. Pergunta: a máquina crítica está disponível na janela e a quebra para o mínimo de área?
4. Processos e produção: fluxo de ponta a ponta (EX-51), gargalos, filas e esperas, padronização, Lean (desperdício de espera, deslocamento, retrabalho, superprocessamento), OEE do packing e da colheita, qualidade na fonte. Pergunta: o trabalho flui sem parada, sem retrabalho e sem dado redigitado?
5. Suprimentos, compras e estoque: necessidade e cobertura da janela, compra do plano e urgente, cotação, pedido, recebimento com conferência em três vias, reserva pelo servidor, separação e entrega, devolução, inventário, validade, classe ABC, preço por unidade de nutriente ou de ingrediente ativo. Pergunta: nunca falta o insumo certo na hora certa, e nada sobra parado?
6. Comercial: oferta × compromisso, contrato e pedido, alocação de lote, qualidade e bloqueio, expedição, recebíveis, risco de preço e comercialização. Pergunta: vende-se o que existe, entrega-se no prazo e o preço defende a margem?
7. Gestão e controladoria: custo (COE, COT e CT), orçado × realizado, custo por hectare e por saca, margem, ponto de equilíbrio, Painel (EX-53), crédito e garantias, financeiro (decisão delegada no EX-51). Pergunta: o dono sabe em 1 minuto onde está ganhando e perdendo dinheiro, por talhão e cultura?
8. Regras de negócio e conformidade: aprovação agronômica individual, receituário, carência, registro, rastreabilidade, idempotência, alçadas, auditoria, permissões por papel, isolamento por organização, dados pessoais. Pergunta: é impossível errar sem perceber e tudo é rastreável?
9. Design system, UX e UI: Menu → Listagem → Detalhe → Sub-detalhe, uma ação primária por contexto, ⋯ com ícones do dicionário (EX-49), estados em texto e cor, vocabulário, tipografia, cor, espaço, densidade, movimento, beleza. Pergunta: a pessoa entende a tela em 1 segundo e age sem medo?
10. Campo e mobilidade: app sem sinal, sol forte, luva e poeira, uma mão, toques mínimos, GPS e foto automáticos, sincronização segura. Pergunta: o operador registra o turno sem parar o trabalho?
11. Dados e integrações: uma fonte por número, eventos entre módulos, integração com ERP, telemetria, estação meteorológica, Agrofit, satélite. Pergunta: cada número tem origem, data e dono, e nada é digitado duas vezes?

ETAPA 3 · REFERÊNCIAS MUNDIAIS POR FUNCIONALIDADE (comparar padrão de interação e regra, sem copiar)
| Funcionalidade | Referências para comparar | O que conferir |
|---|---|---|
| Mapa, talhões e imagens | John Deere Operations Center, Climate FieldView, xarvio FIELD MANAGER, Trimble Ag Software | camadas, contraste, mancha → vistoria, mapa dentro da tarefa (EX-55) |
| Planejamento de safra e plano | Aegro, Granular, Agrivi, FARMPILOT | do plano à O.S. sem redigitar, versões, orçamento ligado |
| Ordem de serviço e frentes | John Deere Work Planner, Solinftec, CNH FieldOps | frente, rota, capacidade, clima, roteiro no app (EX-54) |
| MIP e receituário | xarvio, FieldView, Agrivi, Embrapa (níveis de controle) | amostragem por ponto, decisão, eficácia, trava legal |
| Irrigação | Valley (BaseStation), Lindsay FieldNET, Netafim | balanço hídrico, pivô em tempo real, outorga e energia |
| Manutenção | SAP PM, IBM Maximo, Fiix, UpKeep | OM pelo celular, peça reservada, MTBF, MTTR, preventiva |
| Compras e suprimentos | SAP Ariba, Coupa, Oracle Procurement | necessidade → pedido em 1 clique, três vias, fornecedor |
| Estoque e almoxarifado | Odoo Inventory, NetSuite WMS, SAP EWM | reserva por origem, leitura de código, inventário cíclico |
| Pós-colheita e qualidade | sistemas de packing e de qualidade do setor, GlobalG.A.P. | lote, inspeção, recolhimento, rastreabilidade de ponta a ponta |
| Comercial e recebíveis | Salesforce, plataformas de originação de grãos, Odoo Sales | oferta × compromisso, alocação de lote, crédito do cliente |
| Painel e indicadores | Power BI e Looker (boas práticas), SAP Fiori Overview Page | indicador → decisão → clique para o recorte |
| Pendências e aprovações | SAP Fiori My Inbox, Linear, GitHub | uma caixa por pessoa, ação no próprio item, aprovação uma a uma |
| Design system | Material 3, IBM Carbon, Shopify Polaris, Microsoft Fluent 2, GOV.UK | componentes, tabela, menu ⋯, painel, estados, acessibilidade |
| Campo e offline | apps de campo das máquinas e de inspeção, padrões offline-first | fila local, recibo, conflito, toques mínimos |

ORÇAMENTO DE ESFORÇO (meta por tarefa frequente, medida pelo robô de jornadas; quem decide os números finais são Claude e Codex com a medida)
| Persona | Tarefa | Meta |
|---|---|---|
| Agrônoma | aprovar uma O.S. com produto a partir de Aprovações | ≤ 2 cliques, 0 digitação, próxima abre sozinha |
| Agrônoma | da vistoria acima do NC à O.S. de controle com receituário | ≤ 4 cliques, 0 redigitação |
| Agrônoma | decidir a falta de insumo de uma O.S. (EX-45, EX-51) | ≤ 2 cliques |
| Agrônoma | validar um laudo de solo e levar a dose ao plano | ≤ 3 cliques |
| PCP | emitir as O.S. do período a partir do plano | ≤ 3 cliques |
| PCP | programar uma frente sugerida (EX-54) | ≤ 2 cliques |
| PCP | reprogramar uma O.S. impedida | ≤ 3 cliques |
| Operador (app) | iniciar, pausar com motivo e encerrar o turno | ≤ 2 toques por evento, 0 digitação de hora ou GPS |
| Operador (app) | relatar ocorrência com foto | ≤ 4 toques |
| Monitor (app) | registrar uma vistoria por pontos | ≤ 1 toque por ponto além da contagem |
| Almoxarife | separar e entregar uma requisição | ≤ 3 cliques, leitura de código |
| Almoxarife | receber uma nota com conferência | ≤ 4 cliques, leitura do XML |
| Compras | pedir compra urgente vinda da O.S. ou da OM | ≤ 2 cliques, tudo preenchido |
| Compras | antecipar uma entrega | ≤ 3 cliques |
| PCM e mecânico | transformar o relato em OM e reservar a peça | ≤ 3 cliques |
| Mecânico (app) | encerrar a OM com causa e horas | ≤ 4 toques |
| Conferência | conferir os apontamentos dentro da tolerância | ≤ 2 cliques por lote de apontamentos, com decisão por item |
| Comercial | alocar um lote a um pedido | ≤ 3 cliques |
| Expedição | registrar uma saída com nota e lacre | ≤ 4 cliques |
| Qualidade | liberar ou bloquear um lote | ≤ 2 cliques e motivo |
| Gestor | ver a margem de um talhão a partir do Painel | ≤ 2 cliques |
| Gestor | aprovar pagamento ou crédito dentro da alçada | ≤ 2 cliques |
| Todos | voltar ao ponto de onde saíram | 1 clique, com o registro reaberto |
| Todos | achar qualquer registro pelo número | 1 busca |
Metas gerais: nenhuma tela sem saída; nenhum valor digitado que o sistema, o cadastro, o aparelho ou uma integração já sabem; no máximo dois níveis de painel empilhado; nenhuma cadeia de modais; uma ação primária por contexto.

ESSENCIALISMO EM CADA ACHADO
Cada elemento passa pelos 5 testes do minimalismo-essencial (qual tarefa depende dele; acrescenta algo; dá para calcular ou herdar; a tarefa continua clara sem ele; há evidência de uso considerando safra e sazonalidade). Saída de cada achado: Automatizar, Mover para sob demanda ou Remover, com motivo. Não cortar aprovação, rastro, unidade, acessibilidade nem recuperação para ganhar clique. Beleza conta: hierarquia clara, respiro, alinhamento, tipografia e cor do design system, sem decoração.

ETAPA 4 · PLACAR E PRIORIDADE
- Placar por módulo em cinco critérios (completude para a decisão, rapidez medida, clareza, confiabilidade e rastro, acessibilidade e beleza), de 1 a 5, cada nota com a evidência e a referência mundial que a supera ou é superada.
- Cada achado: lente, tela, persona, hoje (medido), proposta, ganho (cliques, digitação, telas, tempo, erro), risco, esforço, severidade S1 a S4 (PRD 22.1) e prioridade separada.
- "Imbatível" quer dizer: em cada funcionalidade crítica, o Safrion empata ou supera a melhor referência no que a persona faz com mais frequência, medido.

ETAPA 5 · MELHORIA FINAL
- Implantar, por fatias pequenas e com revisão cruzada, as correções S1 e S2 e as lacunas que deixam o Safrion abaixo da referência numa tarefa frequente, dentro do escopo vigente. Mudança de escopo só com decisão registrada.
- Rodar de novo todos os robôs e jornadas na nova candidata e mostrar antes × depois.
- Publicar a candidata final no artefato existente com versão, URL e lista de mudanças.

CRITÉRIOS PARA ENCERRAR O PROTÓTIPO
1. Todos os itens EX, inclusive este, com decisão final e os adotados implantados, revisados e aceitos.
2. Metas do orçamento de esforço atingidas, ou cada desvio com motivo aceito.
3. Metas medidas dos itens anteriores atingidas: passagens (EX-51), listas (EX-49), entrada de dados (EX-46), indicadores com fonte (EX-53).
4. Zero S1 e S2 abertos; acessibilidade sem erro novo; desempenho dentro das metas.
5. Teste moderado com 3 a 5 pessoas por persona nas jornadas principais, com sucesso, tempo e erros registrados.
6. Auditoria integral de Codex, Claude e Gemini reais na mesma candidata, com divergências resolvidas.
7. PRD confrontado com o que foi implantado (sem ampliar escopo, sem perder IDs, pendências ou histórico), referenciando o design system.
8. Aceite explícito do proprietário (Adrianus) sobre a candidata final.
Cumprido isso, o protótipo congela como especificação visual e de comportamento.

DEPOIS: SOFTWARE REAL
Seguir o protocolo vigente: transferir à aplicação Next existente por fatias tela → domínio → banco, provando fidelidade ao protótipo e passando por HML; registrar cada ID como protótipo → implementado no real → testado → HML; preservar trabalhos reais anteriores; não iniciar nova evolução paralela do protótipo. Produção só com aceite explícito do proprietário.

NÃO FAZER
- Começar antes do portão, ou misturar a varredura com implantação ainda aberta.
- Atribuir achado a especialista inventado ou simular Codex e Gemini.
- Ampliar escopo sem decisão; criar item novo na barra principal; gamificar; ligar automação de IA sem a estimativa de custo.
- Mexer nas decisões fixas: aprovação agronômica individual, servidor como autoridade de saldo e reserva, idempotência e rastreabilidade, travas de receituário, carência e registro, sem modo escuro, peça reservada para a ordem que pediu.

ENTREGA (no canal registrado)
- Inventário comum com os brutos; placar por módulo; achados priorizados por lente.
- Lista da melhoria final com antes × depois medido e a candidata final publicada.
- Situação de cada critério de encerramento e o plano das fatias do software real.
- Três listas curtas, com motivo: aplicado, deixado de fora, cortado. Suposições e pendências com gatilho de retomada.
