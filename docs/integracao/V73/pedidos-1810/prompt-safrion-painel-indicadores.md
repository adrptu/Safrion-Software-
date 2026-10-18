PROJETO: Safrion (Do Talhão à O.S.) · EX-53 · Indicadores-chave do Painel

PEDIDO DO PROPRIETÁRIO (18/10/2026)
"No novo menu de painel, liste para cada tela os indicadores chave de performance que tem que ter para uma gestão eficaz no que realmente afeta o resultado e produtividade e custo e qualidade."

COMO TRABALHAR (protocolo da equipe, sem exceção)
1. Leia AGENTS.md, docs/STATUS.md, o cabeçalho do checkpoint da issue #1 e o protocolo canônico. Este prompt não substitui o PRD nem as decisões NAV/DS.
2. Antes de qualquer código, Claude e Codex melhoram este catálogo de forma independente: cada um confere fórmula, unidade, fonte e disponibilidade do dado no protótipo, aponta o que falta ou sobra e decide Adotar, Adaptar ou Rejeitar cada indicador. Divergência se resolve por fonte; o Codex registra no checkpoint (só ele edita o checkpoint).
3. Gemini real só se houver divergência material de domínio (candidatos: margem projetada, ponto de equilíbrio, perdas de colheita e aproveitamento do packing). Pacote mínimo, sem dados reais. Não simule nenhum modelo.
4. Fórmulas e referências vêm da base agro do projeto (custo COE/COT/CT pela metodologia CONAB/Embrapa, produtividade corrigida por umidade e impureza, MTBF, MTTR e disponibilidade, cobertura e acurácia de estoque). Metas são parâmetros configuráveis com fonte, nunca valores fixos no código.
5. Só depois implante, por fatias, com revisão cruzada: quem revisa integra o PR do outro.

O QUE EXISTE HOJE (versão publicada 1792342402-4b90, perfil Proprietário)
- O Painel (PG) entrou na barra principal entre Mapa e Cadastros; a barra passou a ter 10 itens e os painéis antigos de Agrícola, Manutenção e Suprimentos (PAGR, PMAN, PSUP) saíram. O PCOM continua como destino do Comercial.
- Abas: Prioridades · Agrícola (10) · Manutenção (7) · Suprimentos (5) · Comercial (2) · Crédito. Cada número tem selo HOJE, PLANO ou RESULTADO e um ⓘ "Como calcular". Isso fica: é a base do padrão abaixo.
- Prioridades: tabela "Alavancas do resultado" por cultivo e fazenda com Custo da execução (ex.: Soja Santa Rita "Parcial · 4 % do orçado") e Preço médio vendido (ex.: Mamão R$ 3,05/kg × ref. R$ 3,10/kg); listas "Atacar agora · 20" (O.S. impedidas com ha e quem resolve, vistorias atrasadas) e "Decidir · 4" (quarentena, vistorias acima do NC).
- Agrícola: O.S. por fase (A liberar 15, Liberadas 4, Em execução 5, Em conferência 2, Atrasadas 0, Impedidas 5); Execução em andamento 59 % (490,4 de 828,4 ha); Pragas e doenças (acima do NC 3, vistorias atrasadas 2, coleta pendente 1); tabela de previsão e colheita (previsão publicada e recebido, em sacas totais).
- Manutenção: pendências sem ordem 6; ordens abertas 4, em execução 1, a liberar 1, liberadas 1; ativos bloqueados 1; ativos liberados 94 % (15 de 16).
- Suprimentos: lotes com saldo físico 28, com reserva 4, em quarentena 1; requisições a entregar 5; ajustes a aprovar 0.
- Comercial: preço médio por produto × referência; períodos em déficit 2 e suspensos 2; a receber R$ 91.470, vencido R$ 0, entregue em 30 dias R$ 91.470.
- Crédito: bens na ficha 0, valor pendente 0, declarações com mais de 1 ano 0.
- Leitura: quase tudo é contagem de fila (HOJE). Resultado aparece só no preço médio e no custo parcial. Faltam produtividade por hectare × meta, custo por hectare e por saca, margem, ponto de equilíbrio, cumprimento de janela, rendimento operacional, disponibilidade em horas, MTBF e MTTR, cobertura de insumo da janela, entrega de fornecedores, qualidade do produto, perdas e irrigação.
- Dados que já existem e não chegam ao Painel: previsão e recebido por talhão (COLH, CARGA), custo previsto e realizado por talhão (camada Custos do Mapa, GE-03), orçado (GE-02), consumo conferido de insumo (O.S.), cobertura e falta de insumo (O.S., Compras), balanço hídrico e trava de outorga (Irrigação), resultado de inspeção por lote (INSP), descarte das cargas (Beneficiamento), limite liberado do crédito (GE-08), clima horário da estação (integração simulada em Configurações).
- Dados que faltam capturar: horas de máquina no apontamento (o apontamento grava data, dia e hectares) ou horímetro pela integração de telemetria; horas paradas e falhas por ativo (a Manutenção mostra "Disponibilidade 30 d: não calculável" e "MTBF · MTTR: não estimável"); horário da aplicação para cruzar com o clima; medição de perdas na colheita. A seção DADOS A REGISTRAR diz como capturar cada um, e mais os dados que hoje existem só em parte.

REGRAS DE TODO INDICADOR DO PAINEL
1. Existe para uma decisão: cada indicador nomeia quem decide e qual ação muda. Contagem que não muda decisão sai do Painel e fica na tela da área.
2. Uma definição, uma fonte (EX-51 R8): o mesmo número no Painel, no Mapa, na lista e no detalhe. O ⓘ "Como calcular" traz fórmula, unidade, período, fonte e o que fica de fora.
3. Selo de tempo mantido: HOJE (fila do dia), PLANO (avanço contra o plano), RESULTADO (efeito físico ou econômico).
4. Sempre com base de comparação: meta configurável, orçado (GE-02), histórico do talhão ou referência de mercado com fonte. Sem benchmark inventado.
5. Estado em texto e cor (em dia, atenção, crítico) com limites configuráveis. Sem dado mostra "sem dado"; dado incompleto mostra "parcial: falta <x>"; nunca zero no lugar de ausente.
6. Agregação correta: produtividade e custo por hectare ponderados pela área; percentuais por razão de totais; R$/ha não se soma entre talhões; unidade por cultura (sc de 60 kg, t, kg, caixa).
7. Clique leva ao recorte da lista com o filtro e, quando há um só registro, ao registro aberto (EX-51 R2 e R4). "Atacar agora" e "Decidir" são as mesmas pendências do Meu dia e de Aprovações (EX-51 R7), não uma lista paralela; "Decidir" nunca aprova em lote (decisão fixa).
8. Escopo global Fazenda e Safra (EX-51 R5); comparação com o período anterior quando houver.
9. Até 6 indicadores por seção na primeira vista; o resto em "Ver mais". O Painel abre na aba da área da pessoa (Rui em Suprimentos, Otávio em Manutenção, Dora em Comercial) e em Prioridades para gestor e proprietário.
10. Acessível: número com texto, tendência com seta e palavra, nunca só cor; gráfico com uma escala só, sem eixo duplo.

CATÁLOGO POR ABA
Colunas: indicador · cálculo e unidade · comparar com · quem decide e o quê · o clique abre · hoje.
Em "hoje": "no Painel" (já existe), "parcial", "dado existe em <tela>" (falta só levar ao Painel) ou "falta capturar <dado>".

PRIORIDADES (visão do gestor e do proprietário; uma linha por cultivo e fazenda em "Alavancas do resultado")
| Indicador | Cálculo e unidade | Comparar com | Decide | Abre | Hoje |
|---|---|---|---|---|---|
| Margem projetada | produtividade esperada × preço esperado − custo por hectare projetado (R$/ha); preço esperado = média ponderada do vendido (preço médio) e do não vendido (referência com fonte) | orçado da versão vigente | gestor: onde cortar custo, quando vender | Custos e fechamento do cultivo | dado existe em COLH, GE-03, VEN |
| Produtividade esperada × meta | previsão publicada ou colhido ÷ área (sc/ha, t/ha) | meta do plano e histórico do talhão | agrônoma: rever manejo; gestor: rever venda | Previsão e colheita, filtrada | parcial (sacas totais, sem /ha nem meta) |
| Custo por hectare × orçado | realizado e comprometido ÷ área (R$/ha) e % do orçado consumido × % do ciclo decorrido | orçado (GE-02) | gestor: conter desvio | Custos e fechamento | parcial (custo da execução em % do orçado) |
| Custo por unidade produzida | custo por hectare projetado ÷ produtividade esperada (R$/sc, R$/t) | preço de referência | gestor: travar preço, rever custo | Custos e fechamento | dado existe |
| Ponto de equilíbrio e margem de segurança | custo/ha ÷ preço esperado (sc/ha); (produtividade esperada − ponto de equilíbrio) ÷ produtividade esperada (%) | meta de margem de segurança (ex.: ≥ 20 %, configurável) | gestor: risco da safra | Custos e fechamento | dado existe |
| Comercialização | % da produção esperada vendida; preço médio × referência; exposição não vendida (sc × preço, R$) | plano de comercialização | comercial e gestor: vender ou esperar | Contratos e pedidos | parcial (preço médio) |
| Área em risco na janela | ha de O.S. impedidas ou atrasadas cuja janela fecha em até 7 dias, por causa (máquina, insumo, clima, decisão) | zero | PCP, compras, manutenção, agrônoma | "Atacar agora" filtrado | parcial (lista com ha, sem total nem prazo da janela) |
Listas: "Atacar agora" ordenada por impacto (ha × dias até fechar a janela, depois R$ em risco), com quem resolve e a ação; "Decidir" igual a Aprovações.

AGRÍCOLA
Operações (prazo, produtividade e custo)
| Indicador | Cálculo e unidade | Comparar com | Decide | Abre | Hoje |
|---|---|---|---|---|---|
| Execução do plano | ha executados ÷ ha previstos pelo plano até hoje (%) | 100 % do previsto até a data | PCP: acelerar ou reprogramar | O.S. por fase | parcial (59 % contra o total, não contra o previsto até hoje) |
| Operações na janela | ha executados dentro da janela ÷ ha com janela encerrada (%) | meta configurável (ex.: ≥ 90 %) | PCP e agrônoma: causa dos atrasos | O.S. atrasadas | dado existe em O.S. (janela e apontamentos) |
| Rendimento real × padrão | ha apontados ÷ horas de máquina (ha/h), por operação | padrão do CD-08 | PCP: dimensionar, treinar, terceirizar | Operações e rendimentos | falta capturar horas no apontamento ou horímetro |
| Custo da operação × orçado | custo realizado da operação ÷ ha (R$/ha), por operação e talhão | orçado | gestor | Custos e fechamento | parcial (camada Custos do Mapa) |
| Dose aplicada × dose da O.S. | consumo conferido ÷ (dose × área realizada) − 1 (%) | faixa configurável (ex.: ± 5 %) | agrônoma: calibração ou perda | O.S. com desvio | dado existe em O.S. (consumo conferido) |
Conformidade e qualidade da aplicação
| Indicador | Cálculo e unidade | Comparar com | Decide | Abre | Hoje |
|---|---|---|---|---|---|
| Aplicações com receituário válido e dentro da carência | aplicações conformes ÷ aplicações com produto (%) | 100 % | RT | aplicações não conformes | dado existe (travas na O.S. e receituário) |
| Aplicações fora da condição de clima | aplicações com temperatura, umidade ou vento fora do limite (nº) | zero | RT e PCP | aplicações fora | falta capturar o horário da aplicação; clima vem da estação (EX-08) |
Pragas e doenças
| Indicador | Cálculo e unidade | Comparar com | Decide | Abre | Hoje |
|---|---|---|---|---|---|
| Focos acima do nível de controle sem decisão | nº e idade em dias | zero acima de 2 dias (configurável) | agrônoma | Pragas e doenças filtrado | parcial (contagem, sem idade) |
| Tempo até o controle | dias da detecção acima do NC até a O.S. liberada | meta configurável | agrônoma e PCP | vistorias decididas | dado existe (VIS, O.S.) |
| Vistorias em dia | vistorias feitas no prazo ÷ programadas (%) | 100 % | monitor de campo | vistorias atrasadas | parcial (contagem de atrasadas) |
| Eficácia do controle | redução do alvo entre a leitura anterior e a posterior à aplicação (%), por produto e alvo | histórico (Raio-X do alvo, EX-43) | agrônoma: trocar produto ou mecanismo | eficácia por produto | parcial (redução observada no AG-01) |
Irrigação
| Indicador | Cálculo e unidade | Comparar com | Decide | Abre | Hoje |
|---|---|---|---|---|---|
| Lâmina aplicada ÷ necessária | mm aplicados ÷ mm demandados (índice), por setor; setores em déficit acima de 10 mm | faixa 0,9 a 1,1 | irrigante e agrônoma | Irrigação, balanço hídrico | parcial (balanço hídrico na Irrigação) |
| Uso da outorga e energia | volume usado ÷ outorgado (%); kWh por mm aplicado | 100 % da outorga; histórico | irrigante e gestor | Irrigação | parcial (trava de outorga existe) |
Colheita e pós-colheita
| Indicador | Cálculo e unidade | Comparar com | Decide | Abre | Hoje |
|---|---|---|---|---|---|
| Produtividade realizada × prevista × meta | peso líquido corrigido ÷ área colhida (sc/ha, t/ha), por talhão | previsão publicada e meta | agrônoma e gestor | Previsão e colheita | parcial (totais em sacas) |
| Perdas na colheita | medição em área conhecida (sc/ha) | meta configurável (ex.: soja ≤ 1 sc/ha) | PCP e operador | colheitas medidas | falta capturar a medição |
| Umidade e impureza na recepção | média ponderada pelo peso (%) e desconto em kg | padrão contratado | recebimento e comercial | Cargas e recebimento | dado existe em CARGA |

MANUTENÇÃO
| Indicador | Cálculo e unidade | Comparar com | Decide | Abre | Hoje |
|---|---|---|---|---|---|
| Disponibilidade mecânica das máquinas críticas | (horas disponíveis − horas paradas) ÷ horas disponíveis (%), na janela | meta configurável (ex.: ≥ 90 %) | PCM e PCP | ativos parados | parcial ("ativos liberados 94 %" conta ativos, não horas); falta capturar horas paradas |
| Área parada por máquina | ha de O.S. impedidas por ativo bloqueado e dias | zero | PCM e PCP | O.S. impedidas por máquina | dado existe (O.S. impedidas) |
| MTBF e MTTR | horas de operação ÷ nº de falhas; horas de reparo ÷ nº de falhas (h), por máquina crítica | histórico da máquina | PCM: preventiva, reforma ou troca | histórico do ativo | falta capturar falhas e horas (MA: "não estimável") |
| Preventiva × corretiva | horas de preventiva ÷ horas de manutenção (%) | meta configurável (ex.: ≥ 70 %) | PCM | ordens por tipo | dado existe parcialmente (tipo da OM; faltam horas) |
| Cumprimento do plano preventivo | preventivas feitas até o vencimento ÷ vencidas no período (%) | 100 % | PCM | pendências sem ordem | parcial (contagem de pendências; o detalhe do ativo já mostra "cumprimento de preventiva") |
| Custo de manutenção | R$ por hora trabalhada da máquina; custo anual ÷ valor de reposição (%) | meta configurável (ex.: 2 a 5 % ao ano) | PCM e gestor: reformar ou trocar | custo por máquina | dado existe parcialmente (custo da OM; faltam horas trabalhadas) |
| Fila e retrabalho | horas estimadas em fila e idade; OM reabertas em 30 dias (%) | meta configurável | PCM | ordens de manutenção | parcial (contagens por estado) |
Sai da primeira vista: as quatro contagens de ordens por estado (vão para a lista da Manutenção); fica "fila em horas".

SUPRIMENTOS
| Indicador | Cálculo e unidade | Comparar com | Decide | Abre | Hoje |
|---|---|---|---|---|---|
| Cobertura das O.S. dos próximos 14 dias | O.S. com todos os insumos cobertos (saldo livre + pedido que chega antes do início) ÷ O.S. que começam em 14 dias (%) | 100 % | compras e agrônoma | O.S. sem cobertura | dado existe (cobertura calculada na O.S. e em Compras) |
| Ruptura | O.S. impedidas por insumo: nº, ha e dias parados | zero | compras | O.S. impedidas por insumo | no Painel em parte (2 por insumo) |
| Pedidos que chegam depois da necessidade | nº e R$ | zero | compras: antecipar ou trocar fornecedor | Compras filtrado | dado existe em Compras ("chega depois da falta") |
| Entrega no prazo e completa (fornecedor) | pedidos entregues na data e na quantidade ÷ pedidos entregues (%) | meta configurável | compras | fornecedores | dado existe parcialmente (datas do pedido e do recebimento) |
| Prazo de compra | dias da solicitação ao recebimento, por classe de item | histórico | compras: antecipar pedido | Compras | dado existe parcialmente |
| Preço pago × referência | R$ por unidade de nutriente ou de ingrediente ativo (%) | referência de mercado com fonte | compras e gestor | Inteligência de compras | parcial (IC) |
| Acurácia do inventário | itens corretos ÷ itens contados (%) | meta configurável (ex.: ≥ 98 %) | almoxarife | contagens | dado existe em tela que vai para o visível (EX-50) |
| Estoque a vencer e parado | R$ com validade em até 90 dias; R$ sem saída há mais de 180 dias | zero a vencer sem destino | almoxarife e compras | lotes filtrados | dado existe (validade por lote) |
| Quarentena pendente | lotes, kg e dias | zero acima do prazo | almoxarife e RT | lotes em quarentena | no Painel |
Sai da primeira vista: "lotes com saldo físico" e "lotes com reserva" (contagens sem decisão; ficam no Estoque). "Requisições a entregar" segue como item de "Atacar agora".

COMERCIAL (inclui qualidade do produto)
| Indicador | Cálculo e unidade | Comparar com | Decide | Abre | Hoje |
|---|---|---|---|---|---|
| Preço médio vendido × referência | média ponderada pelo volume (R$/sc, R$/kg) e diferença (%) | referência com fonte e data | comercial | Contratos e pedidos | no Painel |
| Produção vendida e exposição | % da produção esperada contratada; não contratado × preço de referência (R$) | plano de comercialização | comercial e gestor | Oferta e compromissos | falta levar (dado em VEN e COLH) |
| Custo coberto | receita contratada ÷ custo total da safra (%) | meta do plano de comercialização | gestor | Custos e fechamento | falta levar |
| Oferta × compromissos | períodos e kg em déficit | zero | comercial | Oferta e compromissos | no Painel |
| Entrega no prazo e completa (cliente) | entregas na data e na quantidade ÷ entregas (%) | meta configurável | comercial e expedição | Expedição | dado existe parcialmente (EXPED) |
| Recebíveis | a receber, vencido, prazo médio de recebimento (dias), inadimplência (%) | limite de crédito do cliente | comercial | Recebíveis | parcial (a receber e vencido); a baixa depende da decisão delegada do financeiro |
| Aproveitamento do beneficiamento | kg em classe comercial ÷ kg recebidos (%); descarte (%) | histórico da rota | produção e qualidade | Beneficiamento | dado existe parcialmente (descarte das cargas) |
| Lotes aprovados na primeira inspeção | lotes conformes na 1ª inspeção ÷ inspecionados (%); kg bloqueados e pedidos afetados | meta configurável | qualidade e comercial | Estoque de produto filtrado | dado existe (INSP) |
| Reclamações e devoluções | kg devolvidos ou reclamados ÷ kg entregues (%) | meta configurável | qualidade e comercial | reclamações | dado existe em tela legada (levar antes, EX-50) |

CRÉDITO
| Indicador | Cálculo e unidade | Comparar com | Decide | Abre | Hoje |
|---|---|---|---|---|---|
| Limite × utilizado | R$ e % por linha (ex.: liberado R$ 300 mil de R$ 850 mil) | limite contratado | gestor | Crédito e garantias | dado existe em GE-08 |
| Vencimentos | R$ em 30, 60 e 90 dias por linha | receita esperada no período | gestor | Crédito e garantias | dado existe parcialmente |
| Cobertura de garantias | valor das garantias ÷ saldo devedor (%), com o penhor ligado ao estoque de produto | exigência do credor | gestor | garantias | parcial (penhor não aparece no estoque, E-12 do EX-51) |
| Endividamento da safra e custo | dívida da safra ÷ receita esperada (%); custo efetivo médio (% a.a.) | política do proprietário | gestor | Crédito e garantias | falta levar |
| Ficha cadastral em dia | pendências e declarações vencidas | zero | gestor | Ficha do grupo | no Painel (vai para "Ver mais") |
Financeiro: se a decisão delegada (EX-51) puser o financeiro operacional no Safrion, entram aqui caixa projetado em 30, 60 e 90 dias e contas a pagar em 7 dias, sem aba nova até essa decisão.

DADOS A REGISTRAR (obrigatório: sem eles os indicadores marcados "falta capturar" não existem)
A captura começa na primeira fatia, porque vários indicadores precisam de semanas de histórico (rendimento, disponibilidade, MTBF, MTTR, perdas, eficácia). Cada dado segue a ordem de entrada do EX-46: calculado → herdado do contexto → capturado pelo aparelho ou pela integração → escolhido em lista → digitado só no fim. Tudo funciona no app sem sinal e sincroniza com idempotência; o servidor valida e guarda quem registrou, quando e de onde.
| Dado | Onde e quem registra | Como, do mais automático ao digitado | Validação | Alimenta |
|---|---|---|---|---|
| D1 Horas de máquina por apontamento | App do operador (Apontamento do turno) e apontamento na web; operador e conferência | Botões Iniciar, Pausar com motivo e Encerrar gravam a hora e o GPS sozinhos; horímetro inicial e final vêm da telemetria quando a integração existir; sem ela, horímetro digitado com teclado numérico; máquina e implemento herdados do conjunto da O.S. | horímetro crescente; horas ≤ duração do turno; ha/h fora da faixa do CD-08 gera alerta, não bloqueio | rendimento real × padrão, custo da operação, disponibilidade, custo de manutenção por hora |
| D2 Paradas no turno | Mesmo apontamento; operador | "Pausar" pede o motivo em 1 toque: chuva, quebra, espera de insumo, espera de máquina, abastecimento, deslocamento, outro; início e fim pela hora do aparelho | soma das paradas ≤ turno; "quebra" abre o relato para a Manutenção (EX-51) | disponibilidade, área em risco, causas de atraso |
| D3 Falhas e reparos por ativo | Ordem de manutenção (web e app do mecânico) e relato do operador; PCM e mecânico | Início e fim da indisponibilidade da máquina gravados ao bloquear e liberar o ativo; tipo (falha, preventiva, espera de peça, espera de mecânico), sistema ou componente e causa escolhidos em lista; horas de mão de obra por mecânico com Iniciar e Encerrar | fim ≥ início; OM corretiva exige sistema e causa ao encerrar; reabertura em 30 dias marca retrabalho | disponibilidade, MTBF, MTTR, preventiva × corretiva, retrabalho, custo de manutenção |
| D4 Horário e condição da aplicação | Ficha de campo da O.S. de pulverização no app; operador | Início e fim por carga do tanque pela hora do aparelho; clima da estação cruzado pelo horário e pela fazenda; sem estação, temperatura, umidade e vento digitados no início | hora dentro da janela da O.S.; condição fora do limite configurado exige motivo e avisa o RT | aplicações fora da condição (EX-08), conformidade |
| D5 Perdas na colheita | App da equipe de colheita, nova coleta na O.S. de colheita; operador da colhedora ou monitor | Método da armação de área conhecida: pontos sugeridos no talhão, peso ou contagem por ponto, conversão para kg/ha e sc/ha calculada; foto opcional | número mínimo de pontos por talhão (configurável); unidade da cultura | perdas na colheita, produtividade |
| D6 Entrega de fornecedor | Pedido de compra e recebimento; compras e almoxarife | Data e quantidade prometidas gravadas no pedido; data e quantidade recebidas pela conferência do recebimento, por linha | recebimento ligado à linha do pedido (EX-51 C-3) | entrega no prazo e completa, prazo de compra, pedidos atrasados |
| D7 Entrega ao cliente | Pedido de venda e expedição; comercial e expedição | Data e quantidade prometidas no pedido; data e quantidade entregues pela saída da expedição | entrega ligada ao pedido e ao lote | entrega no prazo ao cliente, recebíveis |
| D8 Beneficiamento por classe | Ordem de beneficiamento; responsável de produção | Peso de entrada herdado da carga; kg por classe e descarte com motivo ao encerrar a ordem; horas da linha por Iniciar e Encerrar | entrada = soma das classes + descarte + perda declarada | aproveitamento, produtividade do packing |
| D9 Inspeção de lote | Inspeção de qualidade; qualidade | Marca automática de primeira inspeção ou reinspeção pelo histórico do lote | resultado obrigatório antes de liberar o lote | lotes aprovados na primeira inspeção |
| D10 Reclamações e devoluções | Venda e expedição, levando a função da tela legada (EX-50); comercial e qualidade | Pedido, lote e quantidade herdados da entrega; motivo em lista; foto opcional | quantidade ≤ entregue | reclamações e devoluções |
| D11 Metas, referências e parâmetros | Configurações e cadastros; gestor e RT | Meta de produtividade por cultivo e talhão; preço de referência com fonte e data; plano de comercialização (% a vender por período); valor de reposição por máquina (CD-03); horas disponíveis por máquina na janela; limites de cada indicador | toda meta com fonte, data e quem definiu; versionada | margem, ponto de equilíbrio, exposição, custo de manutenção, disponibilidade, estados dos indicadores |
| D12 Contagem de inventário | Estoque, levando a função da tela legada (EX-50); almoxarife | Lista de itens a contar gerada pelo sistema; quantidade contada digitada ou lida por código; divergência calculada | ajuste acima da alçada vai para Aprovações | acurácia do inventário |
| D13 Água e energia da irrigação | Irrigação; irrigante | Volume e energia vindos de hidrômetro e medidor quando houver integração; sem ela, leitura no início e no fim do turno de irrigação | leitura crescente; volume acima da outorga avisa antes de iniciar | uso da outorga, kWh por mm |
Enquanto o histórico é curto, o indicador mostra "parcial: N dias de dado" e não esconde a falta. Dado registrado só na web, sem o app, não basta para D1, D2, D4 e D5: a captura precisa estar onde o trabalho acontece.

FATIAS (ordem sugerida; Claude e Codex podem reordenar com motivo)
F1 Padrão e início da captura: aplicar as 10 regras aos números que já existem (definição única, ⓘ completo, base de comparação, estado, clique para o recorte), tirar da primeira vista as contagens sem decisão e já colocar no ar D1, D2, D3, D4 e D11, para o histórico começar a contar.
F2 Prioridades: margem projetada, produtividade × meta, custo por hectare e por unidade, ponto de equilíbrio, comercialização e área em risco na janela, todos com dados que já existem.
F3 Agrícola e Suprimentos: execução contra o previsto até hoje, operações na janela, dose aplicada × dose da O.S., cobertura dos próximos 14 dias, pedidos atrasados, estoque a vencer.
F4 Comercial e Crédito: exposição, custo coberto, aproveitamento, primeira inspeção, limite e vencimentos.
F5 Restante da captura (D5 a D10, D12 e D13) e os indicadores que dependem de histórico (rendimento, disponibilidade, MTBF, MTTR, perdas, eficácia), que aparecem como "parcial: N dias de dado" até o histórico bastar.
Cada fatia: desenho independente de Claude e Codex → aceite medido antes do código → implantação → revisão cruzada → robô de passagens (EX-51) para os cliques do Painel → publicação no artefato existente com versão e mudança concreta.

ACEITE
- Cada indicador tem ⓘ com fórmula, unidade, período, fonte e exclusões; o número do Painel é igual ao da tela de origem (teste automático por indicador).
- Nenhum indicador sem dado mostra zero; parcial diz o que falta.
- Cada clique abre o recorte certo, com volta ao Painel (EX-51 R4).
- No cenário: para Mamão Formosa da Lagoa Grande e Soja de Santa Rita, Prioridades mostra margem projetada, produtividade × meta, custo por hectare e por unidade e ponto de equilíbrio com as fontes visíveis; Área em risco soma as O.S. impedidas com janela em até 7 dias (OS-0502, janela 25 a 27/09, entra).
- Primeira vista com até 6 indicadores por seção; a pessoa encontra o indicador da sua área em até 2 cliques a partir do Painel.
- Cada captura D1–D13 funciona no app sem sinal, sincroniza sem duplicar e registra quem, quando e de onde; o operador registra início, pausa com motivo e fim com no máximo 2 toques por evento, sem digitar hora nem GPS.
- Uma semana de apontamentos no cenário já gera rendimento real × padrão e disponibilidade em horas para as máquinas da OS-0420 e da OS-0421.

BARRA PRINCIPAL
A versão 1792342402-4b90 pôs o Painel na barra principal, que passou a ter 10 itens. Os prompts anteriores (EX-50 a EX-52) diziam 9; vale o registro NAV vigente: confirmar no checkpoint e não criar outro item.

NÃO FAZER
- Indicador sem decisão por trás, ou meta e benchmark fixos no código.
- Média simples de taxas ou soma de R$/ha entre talhões.
- Aba nova para Qualidade ou Financeiro: qualidade entra nas abas da área; financeiro depende da decisão delegada.
- Gamificar indicadores (EX-52) ou medir velocidade de aprovação agronômica.
- Pedir para digitar o que o aparelho, o cadastro ou uma integração já sabem (hora, GPS, horímetro, máquina do conjunto, peso da carga).
- Tratar a captura como opcional: sem ela, o indicador não sai.

ENTREGA (no canal registrado)
- Para cada indicador: validação (fórmula, fonte e dado, com arquivo e trecho), decisão de Claude, decisão do Codex, decisão final e fatia.
- Desenho de cada captura D1–D13: campo, tela, persona, o que é automático e o que é digitado, validação, sincronização e o indicador que alimenta.
- Três listas curtas, com motivo: aplicado, deixado de fora, cortado. Suposições e pendências com gatilho de retomada.
