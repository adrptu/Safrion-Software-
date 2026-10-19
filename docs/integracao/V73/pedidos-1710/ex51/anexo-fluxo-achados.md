# Anexo do EX-51 · Fluxo conectado entre módulos

Protótipo 1792184197-5a81, perfil Proprietário. Especificação viva: https://claude.ai/artifact/QpXT8VwcQuFT4CqEASq7W7

## Números do robô v5

- Telas que ficam, medidas: 94; detalhes abertos: 180; passagens clicadas: 209 (152 levam a outra tela, 43 abrem no lugar, 14 não fazem nada).
- IDs de outros registros citados nos detalhes: 55; clicáveis: 17 (31 %).
- Campos que apontam para outro cadastro (talhão, máquina, conjunto, responsável, produto, origem): 71; clicáveis: 6 (8 %).
- Passagens para outra tela que chegam com o registro aberto ou destacado: 44 de 152 (29 %).
- Destinos que mostram volta para a tela ou o registro de origem: 16 de 152 (11 %). O "Voltar para <módulo>" do cabeçalho não conta.
- Passagens que saem de um detalhe aberto e voltam com o detalhe reaberto pelo Voltar do navegador: 0 de 59.
- Escopo: das 28 telas principais, 9 têm filtro de Fazenda e 5 têm Safra; nenhuma herda a escolha de outra tela (estado próprio de cada tela; o Mapa guarda o seu só para si, em mapa-ctx).
- Detalhes com "Próximo passo": 29 de 180; dos que têm, 9 dizem quem age.

## Leitura dos números

1. Referências que não levam a lugar nenhum (robô v5). Dos 55 IDs de outros registros citados nos detalhes, 17 são link (31 %). Dos 71 campos que apontam para outro cadastro (talhão, conjunto, responsável, produto, origem), 6 abrem o cadastro (8 %). Exemplo: a OS-0424 cita REQ-039 quatro vezes e OS-0421 três vezes, só em texto; a Origem da O.S. criada em Pragas e doenças é texto, sem VIS-, DIA- ou receituário (B-2).
2. Passagens que perdem o registro (robô v5 e segunda passada). Das 88 passagens que levam um registro a outra tela, 44 chegam com ele aberto (50 %). Em 23 o link nem leva o registro: "Entregar no Estoque ›", "Ver saldos no Estoque ›" e "Receber devolução no Estoque ›" abrem o Estoque na etapa de recebimentos (A-8, C-6). Em 21 o link leva, mas o destino ignora: a Manutenção (vinda de Cadastros e de Ocorrências) e o app do mecânico ignoram #ativo=, e a Consulta Agrofit ignora o produto no endereço.
3. Sem caminho de volta. Só 16 das 88 (18 %) mostram volta para a tela ou o registro de origem; as outras só têm "Voltar para <módulo>". Em nenhuma das 59 passagens que saem de um detalhe aberto o Voltar do navegador reabre o detalhe: a lista volta com o foco na linha (o G2_VOLTA cobre só a lista) e a pessoa reabre o registro e procura a seção. Reproduzido à mão na OS-0424 → Estoque → Voltar.
4. Escopo que não viaja (código). Das 28 telas principais, 9 têm filtro de Fazenda e 5 têm Safra, cada uma com o seu padrão (Santa Rita, Lagoa Grande ou Todas) e o seu estado; nenhuma herda a escolha de outra. O Mapa guarda o seu escopo só para si.
5. Silêncio entre áreas (15 das 96 quebras são "sem aviso ao próximo", 10 delas de prioridade alta; outras 14 são "estado não propaga"). Aprovações (IN-02) não lista nenhuma das 5 O.S. com produto em A liberar (A-4). Compra recebida não avisa a Ana nem o Caio e não guarda o saldo para a O.S. que esperava (C-5). Bloquear uma máquina não impede as O.S. que a usam, salvo as duas já marcadas no cenário (OS-0420, OS-0431), e nada chega ao PCP (D-1, D-2). Lote bloqueado pela qualidade trava a saída mas não avisa o Comercial (E-2). O.S. de controle encerrada não programa a leitura de eficácia (B-4). Não há fila de apontamentos a conferir para a Paula (A-15). Nas telas de processo, 18 de 35 detalhes abertos mostram "Próximo passo" e só 7 dizem quem age; "Quem resolve: Suprimentos" aponta para um papel que não existe (A-5, C-1).
6. Estado que não propaga. Pedidos aprovados em Compras (PC-101 em diante) não chegam ao recebimento do Estoque, e o recebido não volta à etapa 6 de Compras (C-3, C-4). Ajustar a O.S. não atualiza o receituário (B-3, risco legal). A devolução no app (MB-05det) não grava (C-12). O "não operar" do operador não aparece para o próximo operador até o PCM agir (D-16).
7. Números que divergem. Custo do plantio da OS-0420: R$ 2.376 em Custos e fechamento (GE-03, grade fixa fora do cenário) × R$ 1.747,20 no Painel e no Mapa (A-11). OM-0233: R$ 18.400 no GE-03 × R$ 6.180 mais R$ 1.843 do PC-201 na Manutenção (D-18). Frutas Real: R$ 91.470 a receber no Comercial × R$ 28.200 no GE-05, com pedidos que não existem em Contratos e pedidos (E-6). O pedido de calcário da OS-0502 não existe em Compras.
8. Becos sem saída. O Planejar safra nunca chega a "Emitir O.S." (A-1). A O.S. encerrada não mostra custo (A-10). A ocorrência de praga no app não vira vistoria (B-1). Não existe compra urgente de insumo fora do plano (C-10, ver EX-45). Não existe registro de recebimento do cliente na cadeia visível, então a exposição de crédito nunca diminui (E-8, depende da decisão do financeiro no EX-50).
9. Caminhos que passam por telas que serão excluídas (EX-50): o impedimento da OS-0420 leva ao CA-01x; o Meu dia manda "Reprogramar saldo" para o PL-05; Custos e fechamento leva a SU-06, SU-07 e CA-02; Estoque de produto e Mapa levam ao CO-06; GE-05 e GE-08 levam a VE-04, VE-05, VE-06 e LO-04.

## Catálogo de eventos (ponto de partida)

| Evento | Muda | Pendência para | Onde aparece |
|---|---|---|---|
| O.S. com produto emitida | Entra na fila de aprovação; Mapa, Painel e O.S. mostram o mesmo número A liberar | Agrônomo: Aprovar (uma por vez) | Aprovações; O.S.; Mapa |
| Falta de insumo na janela | Selo na O.S. com cobertura (tem, chega, falta) e data de chegada × janela | Agrônomo: decidir (trocar produto, dividir, pedir compra, pedir reprogramação) | Meu dia; O.S.; Painel de suprimentos |
| Compra pedida de uma origem | Pedido nasce com origem (O.S., OM, beneficiamento), quantidade e data de necessidade | Compras: cotar, pedir ou antecipar | Compras; fio da origem |
| Data de entrega muda | Pedido e todas as origens recalculam a cobertura | Dono da origem, só se a nova data passa da janela | Origem; Meu dia |
| Recebimento registrado | Estoque sobe; quantidade fica reservada para a origem que pediu; divergência abre tratativa | Dono da origem: liberar ou iniciar; Compras: divergência | Estoque; origem; Meu dia |
| O.S. liberada | Servidor confirma a reserva; ficha vai para o app do responsável | Almoxarife: separar; responsável: executar | Meu dia; app de campo |
| Apontamento enviado | Saldo da O.S., Painel e Mapa; consumo de insumo e horas de máquina | Conferência: conferir | O.S.; Painel; Mapa |
| O.S. encerrada | Custo realizado do talhão e da safra; planejado × realizado | Gestor, só se o desvio passa do limite | Custos e fechamento; fio da O.S. |
| Máquina parada ou bloqueada | O.S. que usam o conjunto ficam impedidas; janela em risco | PCP: trocar conjunto ou reprogramar | O.S.; Painel de manutenção; Mapa |
| Ordem de manutenção encerrada | Máquina liberada; O.S. impedidas voltam; custo da manutenção na máquina | PCP e quem relatou a quebra (aviso) | O.S.; Manutenção; app do mecânico |
| Peça sem saldo para a OM | Pedido de compra com a OM de origem; peça fica reservada para ela ao chegar | Compras: pedir; PCM: replanejar se atrasar | Manutenção; Compras |
| Vistoria acima do nível de controle | Alvo e talhão em alerta no Mapa e em Pragas e doenças | Agrônomo: decidir (recomendação e O.S. de controle) | Pragas e doenças; Mapa; Meu dia |
| Laudo de solo validado | Dose sugerida no plano e nas O.S. ainda não liberadas da mesma atividade (ex.: calagem do Pivô 12) | Agrônomo: aceitar ou manter a dose do plano | Análises de solo; Planejar safra; O.S. |
| Ocorrência relatada no app | Praga ou doença vira vistoria do alvo; falha de máquina vira achado na Manutenção, com a O.S. do turno | Agrônomo ou PCM: decidir; quem relatou acompanha o andamento | Pragas e doenças; Manutenção; app de campo |
| Aplicação de controle encerrada | Próxima vistoria do talhão agendada para medir eficácia | Monitor de campo: vistoriar | App de campo; Pragas e doenças |
| Carga pesada na balança | Peso líquido entra no lote de produto e no estoque de produto, sem redigitar | Produção: beneficiar | Cargas; Beneficiamento; Estoque de produto |
| Lote bloqueado pela qualidade | Pedidos e expedições com o lote ficam impedidos | Comercial: trocar lote; Qualidade: tratar | Contratos e pedidos; Expedição |
| Expedição entregue | Pedido de venda avança; saldo do contrato e do estoque de produto | Comercial: faturar ou cobrar | Contratos e pedidos; Painel comercial |
| Pagamento do cliente registrado | Saldo a receber e exposição de crédito do cliente diminuem; pedidos retidos por limite são revistos | Comercial: liberar a saída retida | Contratos e pedidos; Expedição (depende da decisão do financeiro no EX-50) |

## Cadeia A · Da safra planejada à operação encerrada e custeada

Personas: Ana · Gestora e RT (agrônoma), Caio · PCP, Rui · Almoxarife, Paula · Conferência, Marcos · operador (app de campo), Suprimentos (compras), Proprietário

### Etapas

| # | Etapa | Tela | Persona | Entidade | Estado | Como passa | Evidência |
|---|---|---|---|---|---|---|---|
| 1 | Planejar a safra e aplicar plano aos cultivos | SAF | Ana | Safra / cultivo | Rascunho → Em planejamento · cultivos com plano | botão | v3out/SAF.json: linha 'Continuar: aplicar plano em 4 cultivos'; SAF L7218-7222 proxSaf |
| 2 | Publicar plano agronômico e atividades | PA | Ana | Plano agronômico | rascunho v1 → versão publicada | nada | v3out/PA.json 'publique a versão para aplicar em Planejar safra'; SAF L5043/L7653 pq_hasPA=false, sg_hasPA=false (sem link ao PA) |
| 3 | Conferir demanda de insumos e enviar à cotação | SAF › CMP | Ana → Suprimentos | Solicitação de compra | demanda calculada → A cotar | link | SAF L7213 solHref → CMP.dc.html#sol=…&saf=…; v3out/SAF.json 'Continuar: enviar demanda para cotação' |
| 4 | Emitir a O.S. | OS | Ana / Caio | O.S. | atividade do plano sem O.S. → A liberar | botão | v3out/OS.json 'Criar ordem' → diálogo 'Nova ordem' com Safra, Cultivo, Atividade e Início vazios; OS L6418 nv_open |
| 5 | Aprovar e liberar a O.S. com produto (individual) | OS (painel) | Ana | O.S. | A liberar → Liberadas | botão | v3out/OS.json OS-0501 'Liberar para execução' (primária), sem seleção em lote (selectAll false) |
| 6 | Reservar insumos da O.S. | EST | sistema | Requisição (REQ-) | Aguardando liberação da O.S. → Reservada | automático | OS L187 dica 'Liberadas: os insumos da ordem ficam reservados no Estoque'; trilha 'A liberar → Liberadas · requisição reservada no Estoque' |
| 7 | Separar e entregar insumos a quem executa | EST (Entregue por O.S.) · MB-05 | Rui → Marcos | Requisição | Reservada → Entregue · custódia confirmada no app | botão | EST L5338-5345 etapa 2 lida de c.reqs; MB-05 L26 'Confirmar recebimento' (Minhas retiradas); MB-01 'Retirar no almoxarifado' → MB-05.dc.html#OS-0424 |
| 8 | Executar e apontar o turno no campo | MB-01 › MB-03 | Marcos | Apontamento | Liberadas → Em execução · dia Provisório | automático | MB-03 L3076-3082 cenFecharTurno → cenApontar(origem 'app'); OS, PAGR, IN-04, MB-03 e EST usam CEN_LS (chave local do cenário) |
| 9 | Enviar a O.S. para conferência | OS | responsável / Paula | O.S. | Em execução · saldo 0 → Em conferência | botão | OS L5394-5395 osc_conferencia (CMD-08) recusa com saldo > 0 |
| 10 | Conferir dias e receber sobras | OS (painel) · EST (Receba devoluções) | Paula · Rui | Apontamento / custódia | Provisório · sobra em custódia → Conferido · custódia zero | link | os/os_lista.json OS-0417: 'Encerrar bloqueado: sobra em custódia… Quem resolve: Rui… Receber devolução no Estoque ›'; EST L5184 '· encerramento liberado.' |
| 11 | Encerrar a O.S. | OS | Paula / Ana | O.S. | Em conferência → Encerradas | botão | OS L5398-5400 osc_encerrar (CMD-10): exige nada em custódia; marca Provisório como Conferido |
| 12 | Apurar custo realizado da operação e do talhão | IN-04 (camada Custos) · PAGR · GE-03 | Proprietário / Ana | Custo | apontamentos aceitos → realizado provisório/conferido | automático | IN-04 L7723-7731 custo por talhão e por O.S.; PAGR L7024 agrCustoRef; GE-03 L58 grade estática (não lê o cenário) |
| 13 | Comparar planejado × real | GE-02 › GE-02det · PAGR | Proprietário | Orçamento | V1 aprovada / V2 publicada → desvio explicado | nada | v3out/GE-02.json único link 'Comparar base × previsão × real' → GE-02det fixo na OS-0409; PAGR card 'Custos · orçado e realizado' |
| 14 | Refletir no Painel e no Mapa | PAGR · IN-04 | Ana / Caio / Proprietário | O.S. / talhão | estado da O.S. → contagens, impedimentos e custo | automático | PAGR 'Abrir 2 O.S. por causa: Insumo no Estoque' → OS.dc.html#painel=OS-0418,OS-0502; IN-04 inv2 'Ordens abertas 9 · Impedidas 1 · A liberar 3' |

### Quebras

**A-1 · alta · beco sem saída** · SAF/PA · plano aplicado → OS · emitir
- Hoje: O Planejar safra nunca nomeia 'Emitir O.S.'; depois da demanda o próximo passo volta a 'dimensionar operações'. A O.S. nasce só por 'Criar ordem', uma por vez, com Safra, Cultivo, Atividade e Início vazios, mesmo com a lista filtrada.
- Impacto: Ana e Caio redigitam do plano cada operação da semana; operação planejada fica sem O.S. sem ninguém perceber.
- Proposta: Ação 'Emitir O.S. do período' (hoje, 7 ou 14 dias) no cabeçalho da OS e na etapa 3 do SAF, com prévia do PL-04 (já emitidas, elegíveis, aguardando dados); emite em lote, todas nascendo A liberar, sem 'Liberar prontas'. 'Criar ordem' herda Safra e Talhão do filtro. (esforço G)
- Evidência: SAF L7218-7222 proxSaf; SAF L5124 'se ainda vai acontecer, emita a O.S.' (texto, sem link); OS L6418 nv_open zera saf/cult/atv/jan; v3out/OS.json diálogo 'Nova ordem'

**A-4 · alta · sem aviso ao próximo** · OS · A liberar → Ana · aprovação
- Hoje: Há 5 O.S. A liberar com produto (OS-0418, 0430, 0431, 0501, 0502). Aprovações (IN-02) lista 4 itens e nenhuma O.S.; Meu dia (IN-01) é fixo e mostra só OS-0418 e OS-0430; o card 'A liberar' do Painel e o 'A liberar 3' do Mapa não são clicáveis.
- Impacto: Ana precisa abrir a OS e filtrar por fase para descobrir o que espera por ela; a O.S. vence a janela parada.
- Proposta: IN-02 lê o cenário e lista cada O.S. A liberar com produto, uma por vez, 'Aprovar e liberar' abre a próxima, sem caixa de seleção para O.S.; atalho 'Aprovações · N' no cabeçalho do Mapa; card A liberar do PAGR leva a OS filtrada por A liberar. (esforço M)
- Evidência: v3out/IN-02.json 4 linhas sem O.S.; v3out/IN-01.json; IN-01 e IN-02 sem CEN_KEY (não leem o cenário); PAGR L61 'A liberar {{pn_v0}}' sem <a>; IN-04 inv2 'A liberar 3' sem ação, 'Abrir ordens ›' → OS.dc.html; navegacao.json IN-02 entram: GE-04

**A-5 · alta · ação fora do lugar** · OS · Falta insumo → CMP · compra
- Hoje: OS-0418 diz 'Quem resolve: Suprimentos' e oferece só 'Ver saldos no Estoque ›' (EST sem item). A OS não tem nenhum link para Compras. O Painel manda Suprimentos para o recorte na OS, que não tem ação de compra. O CMP cita a OS-0418 na demanda só como texto.
- Impacto: Suprimentos não sabe se já há pedido; Ana não vê previsão de chegada; os dois saem da tela e procuram.
- Proposta: No impedimento 'Falta insumo', mostrar solicitação/pedido e data prevista com link CMP.dc.html#sol=…&item=Ureia 45%, e ação 'Pedir compra do item' para Suprimentos no próprio painel; no CMP, a linha da demanda abre OS.dc.html#OS-0418. (esforço M)
- Evidência: OS L5481 h:'EST.dc.html', hl:'Ver saldos no Estoque'; OS sem 'CMP.dc.html' fora do código comum; PAGR 'Abrir 2 O.S. por quem resolve: Suprimentos' → OS.dc.html#painel=OS-0418,OS-0502; CMP L5851 evento 'P1 · OS-0418 · Fertirrigação de nitrogênio' (texto)

**A-7 · alta · estado não propaga** · PAGR/OS · impedimento por máquina → OS · reprogramar (Caio)
- Hoje: OS-0431: 'Quem resolve: PCP confirma a máquina substituta', mas o link é 'Acompanhar OM-0233 ›' (Manutenção). 'Trocar' no painel só grava a troca e muda o texto do conjunto; o bloqueio vem do Trator T1 e só sai quando a Manutenção libera o T1.
- Impacto: Caio troca a máquina e a O.S. continua 'Liberar bloqueado'; Ana não libera; o plantio do T2 atrasa.
- Proposta: Primária do impedimento por máquina = 'Trocar máquina' (abre o Trocar do recurso); troca por ativo apto tira o impedimento, grava na trilha e devolve a O.S. para Ana liberar; 'Acompanhar OM-0233' vira link secundário. (esforço M)
- Evidência: os/os_lista.json OS-0431; OS L5021 bloq aid 'a01'; OS L5012-5019 alTrocar não toca bloq/selos; OS L5100 rec só troca o nome no conjunto; OS L5160-5163 osManCond limpa só com ativo apto

**A-8 · alta · contexto perdido** · OS · painel → EST · entregar, devolver, saldo
- Hoje: 'Entregar no Estoque ›', 'Receber devolução no Estoque ›' e 'Ver saldos no Estoque ›' abrem EST.dc.html sem destino; o EST abre em 'Confira recebimentos' (NF 4533). Na volta o painel da O.S. não reabre e a fazenda do filtro muda.
- Impacto: Rui procura a REQ certa em outra etapa; Paula perde a O.S. que estava conferindo.
- Proposta: EST aceita #ent=REQ-039 (etapa Entregue por O.S. com a linha aberta), #dev=REQ-031 para qualquer item e #saldo=Ureia 45%; o Voltar do EST devolve OS.dc.html#OS-…. (esforço M)
- Evidência: OS L5220, L5360, L5481, L5484 h:'EST.dc.html'; v3out/EST.json primária 'Conferir NF 4533'; v5out/OS.v5.json 'Entregar no Estoque ›' abriu:false, detalheReaberto:false, escopo 'Filtrar por fazenda=Santa Rita'; EST L5477 #dev= só para a caixa do BEN

**A-10 · alta · beco sem saída** · OS · Encerradas → Custo da operação
- Hoje: A dica da fase diz 'realizado, consumo e custo gravados', mas o painel da O.S. encerrada mostra só insumos, apontamentos e 'Ordem encerrada: somente consulta'. Encerrar não grava custo. O custo por O.S. só aparece no Mapa, dentro do talhão.
- Impacto: Ana e o proprietário não sabem quanto custou a operação que acabaram de encerrar.
- Proposta: Seção 'Custo realizado' no painel da O.S. (insumos + operação, provisório/conferido, R$/ha × previsto do plano) com a mesma regra do Mapa, e link 'Ver lançamentos ›' para GE-03 filtrado pela O.S. (esforço M)
- Evidência: OS L190 dica 'Encerradas'; OS L5474; os/os_lista.json OS-0415 sem R$; OS L5398-5400 osc_encerrar; IN-04 L7723-7731 custo por O.S. (cusOrdem)

**A-11 · alta · número diverge** · OS/apontamentos → GE-03 · Custos e fechamento
- Hoje: GE-03 é uma grade fixa, fora do cenário. Plantio da OS-0420: R$ 2.376 (6,0 h × R$ 396) no GE-03 e R$ 1.747,20 (R$ 58,24/ha × 30 ha) no Painel e no Mapa. Insumo da OS-0421: R$ 13.775 só de Fungicida A no GE-03 e R$ 14.820 no cenário (inclui Adjuvante). REQ-037 (KCl, OS-0420) e OS-0409 só existem no GE-03; OS-0415, 0509 e 0510 encerradas não aparecem.
- Impacto: Controladoria fecha a competência com valores que não batem com o Painel; o proprietário vê dois custos para a mesma operação.
- Proposta: GE-03 gera os lançamentos das requisições e apontamentos do cenário, com uma só regra de operação (R$/h do CD-08 × horas apontadas, ou R$/ha × ha, a mesma no Mapa e no Painel); retirar REQ-037 e OS-0409. (esforço G)
- Evidência: dumps/GE-03.txt (ap20, req35, req37, nf8842); PAGR L6996 CUSD cop Plantio 58,24, preço Fungicida A 145 e Adjuvante 22; OS L2351 OS-0421 ins 0,5 + 0,25 L/ha, 190 ha apontados; REQ-037: 0 ocorrências em OS e EST

**A-15 · alta · sem aviso ao próximo** · MB-03 · turno enviado → Paula · conferência
- Hoje: Não há fila de apontamentos a conferir. Na OS, cada dia é conferido no painel da sua O.S.; dias provisórios de O.S. em execução (OS-0420 dia 2, OS-0421 dia 4) não aparecem em filtro. Meu dia manda para CA-02 (legada). Encerrar marca todo Provisório como Conferido.
- Impacto: Paula procura O.S. por O.S.; dia não conferido vira conferido no encerramento sem ninguém olhar.
- Proposta: Filtro 'A conferir' na OS com os apontamentos provisórios de todas as O.S., 'Conferir N dentro da tolerância' e 'Devolver para esclarecimento' (do CA-02); encerrar exige todo dia conferido ou decidido. (esforço M)
- Evidência: OS L52 'Conferir dia' / 'Registrar divergência' por dia; v3out/IN-01.json 'Conferir apontamentos' → CA-02.dc.html; OS L5400 Provisório → Conferido; ocultas.json CA-02 'Levar para o visível'

**A-2 · média · beco sem saída** · SAF · cultivo sem plano → PA · plano
- Hoje: SAF diz 'Não há plano publicado para esta cultura. Crie um em Planos agronômicos.' sem link; os atalhos ao PA estão sempre desligados. PA só volta ao SAF quando o cultivo tem versão antiga.
- Impacto: Ana sai do SAF, procura o PA no menu, perde a safra e o cultivo abertos.
- Proposta: Link 'Abrir plano ›' (PA.dc.html#plano=ID) na célula Plano do cultivo e 'Criar plano de Feijão ›' na mensagem; ao publicar no PA, nota 'Aplicar em N cultivos no Planejar safra ›' com #saf=&passo=cultivos. (esforço P)
- Evidência: SAF L52 texto sem <a>; SAF L5043 e L7653 pq_hasPA=false, pq_ph='#', sg_hasPA=false; PA L2751 link só se c.ver<p.versao; navegacao.json PA entram: AG-07, MOD-AGR

**A-3 · média · sem aviso ao próximo** · SAF · plano e demanda → GE-02 · orçamento aprovado
- Hoje: SAF não liga ao Orçamento nem registra aprovação; a revisão do plano só escreve 'Orçamento a revisar'. Em Aprovações, 'Decidir' do 'Orçamento revisado · safra 26/27' abre GE-02det (comparação da OS-0409), não a versão a aprovar.
- Impacto: Execução começa sem orçamento aprovado à vista; a Direção decide olhando o registro errado.
- Proposta: Na safra, selo 'Orçamento V2 aguarda Direção ›' (GE-02.dc.html#versao=V2) e passo 'Autorizar execução' (do PL-01) que só libera emissão com plano publicado e orçamento aprovado; 'Decidir' do IN-02 abre a versão no GE-02. (esforço M)
- Evidência: SAF L6591 'o protótipo não registra aprovação de plano e de orçamento por safra nova'; SAF L7922 'Orçamento a revisar' (texto); navegacao.json GE-02 entram: GE-01, GE-02det, MOD-AGR, VE-02; v3out/IN-02.json 'Decidir' → GE-02det.dc.html

**A-6 · média · sem aviso ao próximo** · EST · recebimento do insumo → OS · liberar (Ana)
- Hoje: O selo 'Falta insumo' sai sozinho quando o saldo chega, mas a mensagem do recebimento só diz 'X kg de … recebidos no lote …' e nenhuma fila de Ana muda.
- Impacto: A OS-0418 fica destravada sem ninguém saber; a fertirrigação perde a janela de 24/09 21:00.
- Proposta: Ao receber item que destrava O.S. A liberar, a mensagem cita 'OS-0418 já pode ser liberada · Ana' e a O.S. entra em Aprovações de Ana com o motivo. (esforço P)
- Evidência: OS L5144-5147 selo recalculado de libErr; cenReceber OS/EST L2737 msg sem O.S.; IN-01/IN-02 estáticos

**A-9 · média · contexto perdido** · EST · Entregue por O.S. e devoluções → OS · registro
- Hoje: O ID da O.S. nas grades do Estoque é link para OS.dc.html, sem o ID: abre a lista, não a ordem.
- Impacto: Rui e Paula buscam a O.S. de novo para ver fase e quem executa.
- Proposta: h:'OS.dc.html#'+x.os em todas as grades (a OS já abre o painel por #OS-…, L6195). (esforço P)
- Evidência: EST L5345, L5370, L5386, L5441 {k:'link',t:x.os,h:'OS.dc.html'}

**A-12 · média · passa por tela que será excluída** · GE-03 · lançamento → documento de origem
- Hoje: A origem dos lançamentos leva a SU-06, SU-07, CA-02, CA-01 e LO-04; a dimensão 'OS-0421' é texto.
- Impacto: Quem audita o custo cai em telas que vão sumir e não chega à O.S.
- Proposta: REQ-… → EST.dc.html#ent=REQ-…; Apontamento → OS.dc.html#OS-…; NF → EST (Confira recebimentos); romaneio → EXPED; dimensão O.S. vira link. (esforço P)
- Evidência: v4out/GE-03.v4.json linksNaLinha (SU-06, SU-07, CA-02); dumps/GE-03.txt o: CA-01.dc.html, LO-04.dc.html; ocultas.json SU-07/CA-02/LO-04 'Excluir' ou levar ao EST/OS

**A-13 · média · número diverge** · Custo realizado → GE-02/GE-02det · planejado × real
- Hoje: O único caminho de comparação é GE-02 → GE-02det, fixo na OS-0409 (fungicida feijão P1), que não existe na OS; dali a origem e a ação vão para CA-02, SU-07, GE-06det e GE-07. O Painel já calcula orçado × realizado por cultura, mas leva só a GE-03; a camada Custos do Mapa leva a 'Abrir safra'.
- Impacto: O proprietário não compara o plano com o real de uma O.S. ou talhão de verdade.
- Proposta: GE-02det abre por recorte (#os=, #tal=, #cult=) com V1 do plano × real do cenário; links de entrada no card de Custos do PAGR, na seção Custo da O.S. e na camada Custos do Mapa. (esforço G)
- Evidência: v3out/GE-02det.json; GE-02det L34 'OS-0409', L58 o → CA-02/SU-07; navegacao.json; PAGR L61 único link GE-03; IN-04 L7822 'Custos':['Abrir safra','SAF.dc.html']

**A-14 · média · número diverge** · OS-0417 (P1) → Custo por cultura
- Hoje: OS-0417 tem origem 'Safra 2026/27 · Feijão P1', mas o registro marca a cultura Soja. No SAF o P1 tem Feijão BRS Estilo em campo (colheita 10/10/2026) e Soja a plantar em 10/11/2026. O Painel soma o P1 na Soja; o GE-03 diz 'Feijão · P1'.
- Impacto: A cobertura do feijão infla o R$/ha da soja 2026/27 antes do plantio.
- Proposta: A O.S. herda o cultivo ocupante na data da janela (feijão em campo) e o custo vai para esse cultivo. (esforço M)
- Evidência: OS L5021 OS-0417 'culturas': ['Soja'] e orig 'Feijão P1'; SAF L58 P1 Feijão plantio 2026-07-05 e Soja plantio 2026-11-10; PAGR L6996 CUSD tal P1 cultura Soja

**A-16 · média · passa por tela que será excluída** · OS/IN-04/IN-01 → O.S. em execução
- Hoje: OS-0420 'Abrir a ordem completa' → CA-01x-os0420; OS-0421 → CA-01det, na própria OS e no Mapa. Meu dia leva a PL-05 (Reprogramar saldo) e CA-02.
- Impacto: Caio e Paula saem da O.S. para uma cópia legada com outras regras.
- Proposta: Trocar por OS.dc.html#OS-0420 / #OS-0421; 'Reprogramar saldo' vira item do ⋯ da O.S. impedida. (esforço P)
- Evidência: OS L5021 link/bloq.h CA-01x-os0420 e CA-01det; IN-04 L6346 e L7211; v3out/IN-01.json links PL-05, CA-02

**A-17 · média · estado não propaga** · OS · Liberadas → MB-05 · almoxarife no app
- Hoje: A aba Almoxarife do MB-05 é texto fixo (REQ-031 '10 sc a receber', REQ-038 bloqueado) e não lista as reservas REQ-039 (OS-0424), REQ-040 (OS-0425) e REQ-021 (OS-0503).
- Impacto: Rui no campo não vê o que separar; a devolução continua 'a receber' depois de recebida no EST.
- Proposta: Aba Almoxarife lê c.reqs como a etapa 'Entregue por O.S.' do EST: filas 'A separar' (Reservada) e 'A receber' (custódia de O.S. em conferência), com Entregar e Receber no item. (esforço M)
- Evidência: MB-05 L26 texto literal 'Receber devolução · REQ-031 · OS-0417 … 10 sc a receber'; MB-05 sem 'REQ-039'/'REQ-040'; ocultas.json MB-05 'Fila "A separar" do almoxarife (OS-06)'

**A-19 · média · sem volta à origem** · OS · painel (Origem) → SAF/PA/EST · registro de origem
- Hoje: A seção Origem é só texto ('Safra 2026/27 · plantio Soja 58 W no T2', 'Recomendação REC-014 v2'); REQ-039 e OS-0421 citados no painel não são clicáveis.
- Impacto: Ana não confere o plano ou a requisição sem sair e procurar.
- Proposta: Origem com links: cultivo → SAF.dc.html#saf=…&passo=cultivos&cult=…; plano → PA.dc.html#plano=…; REQ → EST.dc.html#ent=REQ-…; REC → AG-04det. (esforço P)
- Evidência: OS L6411 pan_orig=o.orig.map(t=>({t})); v5out/OS.v5.json OS-0424 refs REQ-039 clic 0, OS-0421 clic 0

**A-18 · baixa · contexto perdido** · OS/MB-02det → Ficha de calda
- Hoje: Ficha de campo e impressa só existem para a OS-0424. OS-0421, OS-0430, OS-0501, OS-0504 e OS-0508 (com calda) não têm. 'Voltar para Ordem de Serviço' abre a lista, sem reabrir a OS-0424.
- Impacto: Operador sem ficha de carga nas demais pulverizações; volta perde o painel.
- Proposta: Ficha gerada para toda O.S. de pulverização com calda, versão de impressão na mesma tela; Voltar → OS.dc.html#OS-…. (esforço M)
- Evidência: OS L6009 pan_fichas=o.id==='OS-0424'; MB-02det L6278 d_424; v5out/OS.v5.json OS-0424-app voltar detalheReaberto:false; v3out/OS-0424-app.json Voltar → OS.dc.html

### Já funciona

- Painel agrupa O.S. impedidas por causa e por quem resolve e abre o recorte certo na OS (OS.dc.html#painel=OS-0418,OS-0502), com nota 'Do Painel Agrícola: N O.S.' e 'Ver todas as O.S.' (v3out/PAGR.json; OS L6255).
- OS abre o painel pelo endereço #OS-… e ajusta fazenda e safra com aviso; PAGR usa em 'Conferir OS-0417' e 'Acompanhar OS-0421' (OS L6195-6198).
- Apontamento do app atualiza O.S., Painel e Mapa: cenFecharTurno chama o mesmo cenApontar da web e todas gravam/leem 'talhao-os-cenario-v1' (MB-03 L3076-3082).
- MB-03 sugere o consumo de cada insumo pela dose × hectares e avisa quanto está com o operador; não há redigitação do que a O.S. já sabe (MB-03 L6298).
- Liberar reserva automaticamente; a requisição aparece na etapa 'Entregue por O.S.' do EST, lida do cenário (OS L187; EST L5338-5345).
- Fila do operador nasce das O.S. Liberadas/Em execução dele: liberou, aparece no app (MB-01 L5851 mbFila).
- Aprovação individual respeitada na OS: sem seleção em lote, 'Liberar para execução' por O.S. (v3out/OS.json, selectAll false).
- Selo 'Falta insumo' é recalculado do saldo: o insumo chegou, o impedimento sai sozinho (OS L5144-5147).
- Encerrar bloqueado por sobra em custódia diz quem resolve e como; a devolução no EST avisa '· encerramento liberado' (os/os_lista.json OS-0417; EST L5184).
- Camada Custos do Mapa mostra por talhão cada O.S. com insumos, operação e conferido, e 'Abrir ordem' → OS.dc.html#OS-… (IN-04 L7723-7731).
- Card de custos do Painel compara orçado × realizado R$/ha por cultura, separando provisório e conferido, do cenário (PAGR L7024 agrCustoRef).
- CD-08 'Comparar com o realizado' usa a OS-0421 (19,8 ha/h × padrão 21,6 ha/h) e só sugere revisão (v3out/CD-08.json).

### Ideias das telas que saem

- PL-04: prévia de emissão do período e 'Programar' janela, conjunto e operador sem liberar; tabela de máquinas com condição, ocupação e elegibilidade. Não levar 'Liberar prontas'.
- CA-02: fila única do conferente com 'Conferir N apontamentos' por exceção e 'Devolver para esclarecimento' com pergunta registrada; linha do tempo da O.S. (liberação, entrega, turnos, devolução).
- PL-05: impedimento com dono, prazo e alternativa; 'Propor substituição' para máquina; 'Falta de insumo' ligada ao pedido (PC-088, 'Ver pedido').
- PL-01: 'Autorizar execução' só com plano e orçamento aprovados, dizendo o que falta; 'Abrir fechamento' da safra encerrada → GE-03.
- GE-06det: 'Hipótese a validar' e 'Documentos de origem' do desvio, para dentro do GE-02det (ocultas.json GE-06det).

## Cadeia B · Do sinal de campo à decisão, à O.S. de controle e à eficácia

Personas: Ana · Gestora e RT (agrônoma), Operador de campo (no dado: Marcos e João em Santa Rita; Lúcia e Wesley em Lagoa Grande), Paula · Conferência (no dado, OS-0508 está com Lúcia para conferir e encerrar), Proprietário

### Etapas

| # | Etapa | Tela | Persona | Entidade | Estado | Como passa | Evidência |
|---|---|---|---|---|---|---|---|
| 1 | Detectar mancha no satélite e programar inspeção | IN-04 | Ana | Vistoria (inspeção de mancha) | Mancha · indício, não diagnóstico → Programada | botão | IN-04 L7709 Mancha · ha · NDVI · centroide com A('Programar vistoria',{fn:()=>criarVis(self,[t])}); L7618-7627 criarVis grava no estado compartilhado (aparece no AG-01 e no app) |
| 2 | Ler clima e sensores | IR-04 / IR-01 | Ana | Sensor / setor | Sonda Pivô 10 sem dado desde 21/09 06:00 → sem mudança | nada | v4out/IR-04 g_src: painel lateral só consulta, botões Fechar/Fechar; IR-01 e IR-04: 0 ocorrências de 'AG-01.dc.html', 'vistoria' e 'doença' |
| 3 | Registrar praga vista em campo | MB-04 | Operador de campo | Ocorrência OC- | — → Registrada na O.S. | nada | MB-04 L6269 tipo 'Praga ou doença'; L6300-6302 exige O.S. na fila e grava cenOcorrencia; c.ocorr só é lido em MB-02det e MB-04 |
| 4 | Programar vistoria por pontos | AG-01 | Ana | Vistoria VIS- | — → Programada | automático | AG-01 L5199-5209 mipNovaVis: '… aparece no app.'; não entra na fila do MB-01 nem no Meu dia (sem mipGet) |
| 5 | Coletar pontos no app | MB-06 | Operador de campo | Vistoria VIS- | Programada → Concluída (Acima do NC, Foco ou Abaixo) | automático | MB-06 L2735-2739 mipColetar/mipConcluir; L2727 'O agrônomo decide no escritório (Pragas e doenças).' |
| 6 | Ver resultado e abrir a decisão | PAGR › AG-01 | Ana | Vistoria VIS- | Acima do NC → Formulário de decisão aberto | link | PAGR L5912 grupo decidir = acima, foco, cancelada; L6136 'Conferir vistoria' → AG-01.dc.html#VIS-…; AG-01 L5171 próximo passo 'Decidir controle' |
| 7 | Emitir receituário e gerar O.S. de controle | AG-01 | Ana (RT) | DIA + REC/RA + O.S. | Acima do NC / Foco → O.S. em A liberar; vistoria Em controle | botão | AG-01 L5487-5491 pré-preenche produto conferido, dose mínima da bula, área do talhão e data de amanhã; L5522 'Emitir receituário e gerar O.S.'; L5324-5352 grava O.S. no cenário e DIA/REC/RA no MIP numa ação |
| 8 | Validar laudo de solo | AG-02 | Ana | Laudo LAU- | Aguardando validação → Validado | botão | AG-02 L5117-5118 'Validar laudo' só para agrônomo; v3out/AG-02 LAU-2050 |
| 9 | Levar dose sugerida ao plano | AG-02 › SAF | Ana | Sugestão de dose (CAL-10) | Validado com sugestão → Plano ajustado (aceita) ou ignorada | link | AG-02 L5121 'Ver no plano' → SAF.dc.html#saf=…&passo=cultivos&sug=1; SAF L7352 abre Sugestões pelas análises; SAF L7529 volta ao AG-02#LAU-… |
| 10 | Emitir O.S. de calagem ou adubação pelo plano | OS | Ana | O.S. | Atividade no plano → A liberar | botão | v3out/OS 'Criar ordem': Safra, Cultivo, Atividade, Início da janela escolhidos de novo; OS L5502-5507 plano mudado → 'Ajustar antes de liberar' |
| 11 | Consultar Agrofit e usar produto na O.S. | AG-07 › OS | Ana | O.S. | A liberar → A liberar (ajuste com produto) | botão | AG-07 L5509-5516 exige cultura, alvo e O.S. de pulverização A liberar; OS L6195-6201 recebe #OS-…:usar= |
| 12 | Aprovar e liberar a O.S. com produto (uma por vez) | OS | Ana (RT e gestora) | O.S. | A liberar → Liberadas (reserva no Estoque) | botão | OS L5466-5501 Liberar/Aprovar vN por papel; L6130 confirmação 'Liberar … ao confirmar' |
| 13 | Aplicar e apontar | app (MB-03) › OS | Operador de campo | O.S. | Liberadas → Em execução › Em conferência | automático | OS L5021 OS-0508 ap 19/09 e 20/09 'Conferido', etapa Em conferência |
| 14 | Conferir e encerrar a O.S. | OS | Paula (conferência) | O.S. | Em conferência → Encerradas | botão | OS L5021 OS-0508 cond 'Próximo passo: conferir e encerrar.'; PAGR 'Conferir OS-0508' |
| 15 | Programar leitura pós | AG-01 | Ana | Vistoria pós | Avaliar controle (O.S. encerrada) → Leitura pós programada | nada | AG-01 L5134-5135 estado 'pos' calculado ao abrir; L5178 botão 'Programar leitura pós'; PAGR L5912-5916 não lista 'pos'; OS: 0 ocorrências de 'vistoria' e 'leitura pós' |
| 16 | Coletar leitura pós e ver redução | MB-06 › AG-01 / AG-01det | Operador de campo › Ana | Vistoria pós | Programada → Encerrada · redução observada % | automático | AG-01 L5122 redução = 1 − pós/pré; L5136 sub 'redução observada N %'; AG-01det L5435 série do alvo no talhão |
| 17 | Aprender com o histórico do alvo | Raio-X do alvo | Ana | Alvo × talhão | Encerrada → — | nada | Especificado à parte (fora desta varredura) |

### Quebras

**B-1 · alta · beco sem saída** · MB-04 Ocorrência 'Praga ou doença' → AG-01 vistoria
- Hoje: A ocorrência de praga fica presa à O.S. da fila e não vira inspeção. Nenhuma tela web lê c.ocorr. Sem O.S. na fila, o app recusa.
- Impacto: O operador vê a praga e avisa; Ana nunca fica sabendo. O sinal mais barato da cadeia se perde.
- Proposta: Tipo 'Praga ou doença' cria inspeção (mipNovaVis prot 'inspecao', orig 'app · OC-…', foto e GPS do aparelho) sem exigir O.S.; aparece no AG-01 e no Painel em 'Coleta a resolver'; toast 'Ana recebe em Pragas e doenças'. (esforço M)
- Evidência: MB-04 L6269 TIPOS inclui 'Praga ou doença'; L6300 'Nenhuma ordem liberada na sua fila.'; L6302 cenOcorrencia; c.ocorr.filter só em MB-02det e MB-04 (OS, AG-01, PAGR, IN-04: nenhum uso)

**B-2 · alta · sem volta à origem** · OS painel da O.S. de controle → AG-01 vistoria e receituário de origem
- Hoje: A O.S. nascida no AG-01 grava link '' e a Origem como texto puro. Em A liberar a seção Origem vem fechada ('2 registros'). Nenhum link para VIS-, DIA- ou RA-.
- Impacto: Ana aprova a O.S. sem ver contagem × NC e receituário com um clique; para voltar à vistoria precisa lembrar o ID e buscar no AG-01.
- Proposta: orig vira lista {t,h}: 'VIS-… › AG-01.dc.html#VIS-…', 'RA-… (Ana · RT)'; link do cabeçalho 'Abrir VIS-…'; em O.S. com receituário, Origem aberta por padrão em A liberar. (esforço P)
- Evidência: AG-01 L5321 orig:[…v.id…, …RA…], link:''; OS L6411 pan_orig=o.orig.map(t=>({t})); L6412 pan_hasLink=!!o.link; L5957 DEF 'A liberar':['ins','rec']; OS: 0 ocorrências de 'AG-01.dc.html'

**B-3 · alta · estado não propaga** · OS ajuste da O.S. de controle → AG-01 receituário (REC/RA)
- Hoje: Ajustar dose ou área na O.S. gera v2, mas o receituário no MIP fica com a dose da v1. O insumo da O.S. nasce sem alvo; a trava de dose na O.S. usa a bula da cultura e só confere alvo quando o item tem alvo.
- Impacto: Receituário e O.S. divergem na dose; a trava por alvo do AG-01 pode ser contornada no ajuste (ex. do próprio dado: Ciantraniliprole 100 OD em Café tem 0,5–0,7 L/ha para bicho-mineiro e 1,0–1,5 L/ha para broca). Risco legal para a RT.
- Proposta: mipNo grava alvo (p.alvo) em cada insumo; ajuste na O.S. com produto reemite o receituário (nova RA, a anterior 'Substituído') e atualiza s.rec; trava de dose pelo alvo do receituário. (esforço M)
- Evidência: AG-01 L5314 ins=[{g,p,dose,un,tot,sit}] sem alvo; L5581 painel mostra r.dose de s.rec; OS L5342-5351 osUsoItem confere alvo só 'if(x.alvo…)'; OS: 0 ocorrências de mipGet; OS L5620 CARD.prod Ciantraniliprole fx Café

**B-4 · alta · sem aviso ao próximo** · OS encerrada → AG-01 leitura pós
- Hoje: Ao encerrar a O.S., nada avisa Ana. A vistoria passa a 'Avaliar controle' só quando alguém abre o AG-01, e a leitura pós depende de clicar 'Programar leitura pós'. O Painel e o selo do AG-01 não contam esse estado.
- Impacto: A eficácia não é medida ou é medida tarde; o ciclo não fecha e o histórico do alvo fica sem pós.
- Proposta: Ao encerrar a O.S. com origem VIS, programar a leitura pós automaticamente (mesmo método, última aplicação + 7 dias, responsável da vistoria) e listar 'Avaliar controle' no Painel e em Aprovações; aviso no toast de encerramento: 'VIS-… programada para dd/mm'. (esforço M)
- Evidência: AG-01 L5134-5135 k='pos'; L5178 fn 'pos' (botão); L5623-5624 selo conta só acima, foco e coleta; PAGR L5912-5916 grupos decidir/atrasadas/coleta, 'pos' só em n.em_controle; OS: 0 ocorrências de 'vistoria'

**B-5 · média · número diverge** · OS apontamentos da aplicação → AG-01 histórico e data da leitura pós
- Hoje: A leitura pós usa a data prevista no receituário ou a da decisão, não a última aplicação real. O histórico marca 'aplicada' só porque a data passou, mesmo com a O.S. sem execução.
- Impacto: VIS-052: decisão 18/09 sem data → pós em 25/09; a OS-0508 aplicou até 20/09 → 7 DAA seria 27/09. Leitura cedo distorce a redução; rotação e nº máximo contam aplicação que pode não ter ocorrido.
- Proposta: mipPos e mipHist leem a O.S. do cenário: data da última aplicação conferida e etapa (Encerradas = aplicada; Liberadas/Em execução = programada; Canceladas = cancelada). (esforço M)
- Evidência: AG-01 L5370 data=mipAdd(d.data||d.em,7); L5381 ch: x.data>hoje?'programada':'aplicada'; AG-01 L5022 VIS-052 dec {em:'2026-09-18', os:'OS-0508'} sem data; OS L5021 OS-0508 ap 19/09 e 20/09

**B-6 · média · contexto perdido** · AG-01 leitura pós → AG-01 vistoria de origem (antes × depois)
- Hoje: O painel da leitura pós mostra só 'Redução observada N %'. A vistoria pré aparece como texto 'leitura pós da VIS-…' sem link; média pré, O.S., produto e data não ficam lado a lado.
- Impacto: Ana não confere o antes × depois numa tela; precisa abrir duas vistorias e a O.S. para julgar o controle.
- Proposta: Bloco 'Antes × depois' no painel da pós: pré (VIS-…, data, média) › aplicação (OS-…, produto, dose, data) › pós (média) › redução, com links; na série do AG-01det, marcador da aplicação. (esforço P)
- Evidência: AG-01 L5539 pan_res '… · leitura pós da '+vv.pos_de (texto); L5562 pan_kv acrescenta só 'Redução observada'; AG-01det L5435 série do alvo sem marca da aplicação

**B-7 · média · ação fora do lugar** · PAGR MIP 'A decidir' e IN-02 Aprovações → AG-01 decisão
- Hoje: O Painel chama de 'Conferir vistoria' o que é 'Decidir controle' e abre o painel, não o formulário (o Mapa já usa #VIS:decidir). Aprovações, futura página inicial do agrônomo, não lista vistoria a decidir nem O.S. A liberar.
- Impacto: Um clique a mais e verbo diferente do próximo passo; a fila de decisões da RT fica espalhada.
- Proposta: Painel usa o rótulo do próximo passo ('Decidir controle VIS-…') e href '#VIS-…:decidir'; Aprovações inclui VIS acima do NC/foco e cada O.S. com produto A liberar, uma por vez. (esforço P)
- Evidência: PAGR L6136 href:x.origem (AG-01.dc.html#VIS-…), abrir:'Conferir vistoria '; IN-04 L7751 'AG-01.dc.html#'+id+':decidir'; v3out/IN-02 4 itens (inventário, política, orçamento, acesso), 0 VIS e 0 O.S.

**B-8 · média · sem aviso ao próximo** · AG-01 programar vistoria → MB-01 / Meu dia do coletor
- Hoje: A vistoria programada não entra na fila do app nem no Meu dia. O MB-06 abre a primeira de Marcos; o app não tem usuário Lúcia nem Wesley, responsáveis de Lagoa Grande.
- Impacto: O coletor só descobre a vistoria se abrir o atalho Vistoria; atraso de coleta vira 'Vistoria atrasada' no Painel.
- Proposta: Fila do MB-01 e Meu dia listam 'Coletar VIS-… · talhão × alvo · data' do usuário; MB-06 abre a do usuário do app; incluir Lúcia e Wesley em MB_US. (esforço M)
- Evidência: MB-01 e IN-01: 0 ocorrências de mipGet e VIS-; MB-06 L2712 ab.find(x=>x.resp==='Marcos'); MB-01 L6209 MB_US=[Marcos, Zé, João]; AG-01 L5021 MIPD.resp Lagoa Grande ['Lúcia','Wesley']

**B-9 · média · contexto perdido** · IN-04 mancha no satélite → MB-06 inspeção no campo
- Hoje: A inspeção nasce em 1 clique, mas sem a mancha: área, NDVI, cena e centroide não vão para a vistoria. O app mostra só 'caminhamento até o centroide · 5 pontos'.
- Impacto: O coletor não sabe onde fica a mancha; Ana não vê no AG-01 por que a inspeção existe.
- Proposta: criarVis passa extra {mancha:{ha,ndvi,cena,coord}}; AG-01 mostra 'Origem: satélite · cena …' com link ao Mapa; MB-06 mostra o centroide e abre o mapa do ponto. (esforço P)
- Evidência: IN-04 L7708-7709 mancha com ha, NDVI, centroide m.coord; L7625 mipNovaVis(s0,t,prot,mipAmanha(),undefined,'mapa · satélite') sem extra; MB-06 L2721 mb_proto mostra p.met; MB-06 e AG-01: 0 ocorrências de 'coord'

**B-10 · média · redigitação** · AG-01 inspeção com sintoma → AG-01 vistoria do alvo
- Hoje: Na inspeção, a única decisão é 'Registrar a causa' (texto livre) e o sistema programa outra inspeção. Para chegar ao controle, Ana abre 'Programar vistoria' do cabeçalho, que começa no primeiro talhão da fazenda, e escolhe talhão e alvo de novo.
- Impacto: Talhão e alvo redigitados; a causa escrita não vira alvo; risco de programar no talhão errado.
- Proposta: Na decisão da inspeção, escolher o alvo do protocolo e 'Programar vistoria de <alvo>' com o talhão herdado (agPvOpen(self,v.tal,alvo)); o botão do cabeçalho usa o talhão do filtro. (esforço P)
- Evidência: AG-01 L5482 inspecao → [['monitorar','Registrar a causa']]; L5364 nova vistoria com v.prot ('inspecao'); L5517 'programe a vistoria do alvo'; L5594 t0=tal||tals[0]; L5619 pv_new=()=>agPvOpen(self)

**B-11 · média · beco sem saída** · IR-04 / IR-01 clima e sensores → AG-01 vistoria
- Hoje: Não há sinal de clima ligado a pragas e doenças nem link para o AG-01. O sensor sem dado (Sonda Pivô 10, 21/09) abre painel só de consulta, sem 'Pedir manutenção da sonda' nem 'Registrar leitura manual'.
- Impacto: Chuva e umidade que favorecem antracnose não viram vistoria; o balanço passa a estimar por ET sem ninguém responsável por religar a sonda.
- Proposta: No IR-04, linha de risco por pivô (chuva/umidade × alvo do protocolo) com 'Programar vistoria de <alvo>' (mipNovaVis orig 'clima'); no sensor sem dado, primária 'Pedir manutenção da sonda' (achado para a Manutenção) e secundária 'Registrar leitura manual'. (esforço M)
- Evidência: IR-01 e IR-04: 0 ocorrências de 'AG-01.dc.html', 'vistoria', 'doença'; v4out/IR-04 g_src painel consulta, botões Fechar/Fechar; padrao/ocultas.json IR-04 o_que_aproveitar 'Pedir manutenção da sonda' e 'Registrar leitura manual'

**B-12 · média · contexto perdido** · AG-02 laudo validado → OS de calagem A liberar
- Hoje: OS-0502 Calagem do Pivô 12 segue com 'dose do plano 2 t/ha' e não cita laudo, embora LAU-2071 e LAU-2072 do Pivô 12 estejam validados desde 15/09. A O.S. só muda se a sugestão for aceita no Planejar safra.
- Impacto: A RT libera a calagem sem ver o laudo. Pela regra CAL-10 da própria tela (V recalculado 50 % com SB 4,05 e T 8,10; V2 do mamão 70 %; PRNT 90) a dose fica perto de 1,8 t/ha, não 2 t/ha.
- Proposta: Na O.S. de calagem/adubação, seção Insumos mostra 'Laudo LAU-… validado sugere X t/ha · Ver no plano' com link; a O.S. guarda o laudo na Origem. (esforço P)
- Evidência: OS L5021 OS-0502 orig ['… plano MAMAO-IMP','Calagem · dose do plano 2 t/ha'], etapa A liberar; AG-02 L5021 SOLO0 LAU-2071 Pivô 12 Validado (Ca 2,90, Mg 0,95, K 78,2 mg/dm³, H+Al 4,05); regra v2 Mamão Formosa 70; gar filler prnt 90; AG-02 L4576-4583 a regra usa o V recalculado; L4588 soloCalagem; OS: 0 ocorrências de 'LAU-' fora dos dados

**B-13 · média · redigitação** · SAF plano ajustado pelo laudo → OS nova de calagem/adubação
- Hoje: Depois de aceitar a dose no plano, a O.S. é criada em 'Criar ordem', escolhendo de novo safra, cultivo, atividade e janela. O SAF não tem 'Emitir O.S.' por atividade (só a colheita tem o atalho #nova).
- Impacto: Três escolhas repetidas e risco de emitir para o cultivo errado.
- Proposta: Na sugestão aceita do SAF e no laudo do AG-02, link 'Emitir O.S. de calagem' para OS.dc.html#nova:<cultivo>:<atividade>:<data> (Ana só confirma). (esforço P)
- Evidência: v3out/OS 'Criar ordem' campos Safra, Cultivo, Atividade, Início da janela; SAF: 'OS.dc.html#nova' só em L3811/L3816 (colheita); OS L6193 já aceita #nova:cultivo:atividade:data

**B-14 · média · beco sem saída** · AG-07 'Usar na O.S.' → OS ajuste com produto
- Hoje: Só funciona se já houver O.S. de pulverização A liberar na cultura; senão diz 'Nenhuma ordem…' e para. Quando funciona, inclui o produto sem receituário (RA) nem vistoria de origem, ao contrário do AG-01.
- Impacto: Dois caminhos para pôr produto na O.S. com registros legais diferentes; quem parte do Agrofit não tem como seguir.
- Proposta: Sem O.S. candidata, 'Usar na O.S.' leva à decisão do AG-01 (vistoria do talhão × alvo) ou ao 'Criar ordem'; com O.S., o ajuste emite receituário igual ao do AG-01. (esforço M)
- Evidência: AG-07 L5509-5512 cand=agOsCand… 'Nenhuma ordem de pulverização A liberar em '; L5516 location.href='OS.dc.html#'+ord+':usar=…'; OS: 0 ocorrências de 'RA-0'

**B-15 · média · passa por tela que será excluída** · AG-01, AG-01det, AG-02, IN-04, AG-07 → AG-03, AG-03det, AG-04det, AG-06, PL-02, CA-01x-os0420
- Hoje: Os links da cadeia levam a telas que serão excluídas ou levadas para a O.S.: diagnóstico, recomendação REC-014, eficácia, necessidade NEC-028 e ficha antiga da OS-0420.
- Impacto: Ao apagar as telas, a cadeia vira link quebrado; hoje leva o usuário para fora do caminho visível.
- Proposta: Trocar como em padrao/ocultas.json: DIA e REC → AG-01.dc.html#VIS-011 e OS.dc.html#OS-0420; 'Ver histórico' → CD-01det do talhão; NEC-028 → SAF passo operações. (esforço P)
- Evidência: AG-01 L5578 h:'AG-03det.dc.html'/'AG-03.dc.html'; L5579 h:'AG-04det.dc.html'; AG-01det L48 cadeia → AG-03det, AG-04det, PL-02, AG-06; AG-02 L5128 → AG-03det; IN-04 L7711 e L7822 'Ver histórico' → AG-06; AG-07 L5045 → AG-04det e CA-01x-os0420

**B-16 · média · passa por tela que será excluída** · AG-01 receituário emitido → OS lista do RT
- Hoje: O RT não tem lista dos receituários que assinou nas telas visíveis. O número RA só aparece no painel da vistoria e no texto da Origem da O.S.
- Impacto: Ana não acha o que assinou para auditoria, cancelamento ou fiscalização.
- Proposta: Na OS, filtro 'Receituários' e coluna 'Receituário · RT' (RA, versão, produto · dose · janela, situação), vindo do AG-04. (esforço M)
- Evidência: OS: 0 ocorrências de 'Receituário' (maiúscula) e 'RA-01'; padrao/ocultas.json AG-04 'Receituário é exigência legal e só aparece listado aqui'

**B-17 · baixa · número diverge** · OS-0504 e OS-0508 (dado inicial) → AG-01 VIS-051 e VIS-052
- Hoje: No AG-01 as O.S. nasceram das vistorias com receituário RA-0141 e RA-0140. Na O.S., a Origem diz 'plano MAMAO-PROD' e requisição, sem vistoria nem receituário.
- Impacto: Quem parte da O.S. conclui que a aplicação veio do plano; a trilha legal fica contraditória na demonstração.
- Proposta: Alinhar o dado: Origem de OS-0504 e OS-0508 com 'Pragas e doenças · VIS-05x · Pivô … · receituário RA-014x (Ana · RT)' e link, no mesmo formato do mipNo. (esforço P)
- Evidência: AG-01 L5022 VIS-051 dec {os:'OS-0504', ra:'RA-0141'}, VIS-052 dec {os:'OS-0508', ra:'RA-0140'}; OS L5021 OS-0504 orig ['Safra Mamão 2026/27 · Pivô 6 · plano MAMAO-PROD','Requisição REQ-022…'], OS-0508 orig ['… plano MAMAO-PROD','Requisição REQ-025']

**B-18 · baixa · número diverge** · MB-06 coleta → AG-01det evidências
- Hoje: AG-01det mostra 'N fotos · 2 por ponto coletado' e 2 fotos por linha, mas o app de vistoria não tem campo de foto.
- Impacto: Evidência mostrada não existe; o receituário se apoia em prova que ninguém coletou.
- Proposta: MB-06 com 'Foto do ponto' opcional (obrigatória acima do NC ou com sintoma); AG-01det conta as fotos reais. (esforço P)
- Evidência: AG-01det L5420 {l:'Evidências',v:(R.col*2)+' fotos',s:'2 por ponto coletado'}; L5430 fotos:col?2:0; MB-06: 0 ocorrências de 'foto'

### Já funciona

- Vistoria → O.S. sem redigitação: 'Decidir controle' abre o formulário com produto conferido, dose mínima da bula, área do talhão e data de amanhã; 'Emitir receituário e gerar O.S.' grava DIA, REC/RA e a O.S. em A liberar numa ação e o foco vai para 'Abrir OS-…' (AG-01 L5487-5491, L5324-5352, L5530).
- Regra legal única no receituário e na O.S.: registro, dose da bula, nº máximo, rotação, carência × colheita e estoque, com o botão desligado e a trava em role=alert (OS L2495-2513; AG-01 L5251-5284, L52 dc_ok disabled).
- Mapa abre a decisão direto: talhão com VIS acima do NC leva a AG-01.dc.html#VIS-…:decidir (IN-04 L7751; AG-01 L5449-5452).
- Satélite vira inspeção em 1 clique e não duplica: 'Programar vistoria' na mancha ou queda de índice; se já houver, vira 'Abrir VIS-…' (IN-04 L7704, L7709, L7614).
- O.S. cancelada devolve a vistoria para 'Decidir controle' e o Painel a lista em 'A decidir'; receituário antigo fica 'Cancelado' (AG-01 L5133, L5180, L5303; PAGR L5912).
- Seguir monitorando programa a próxima vistoria sozinho; vistoria atrasada oferece 'Programar vistoria' com talhão e alvo herdados (AG-01 L5354-5366, L5181, L5478).
- Contexto herdado na chegada: #VIS-… abre o painel e troca a fazenda; #OS-… abre o painel e troca fazenda e safra com aviso (AG-01 L5445-5448; OS L6195-6198).
- Laudo validado leva a dose CAL-10 ao plano por 'Ver no plano' (Sugestões pelas análises) com volta ao laudo, e a O.S. passa a 'Ajustar antes de liberar' quando o plano muda (AG-02 L5121; SAF L7352, L7529; OS L5502-5507).
- Série do alvo no talhão (mesmo método e unidade) no AG-01det dá a leitura antes × depois em barras (AG-01det L5435).
- Ficha do produto abre em nova aba sem perder o formulário de decisão (AG-01 L52 dc_prods target=_blank).
- Teclado e foco no painel da vistoria: foco no fechar ao chegar, Tab preso no diálogo, Esc fecha, foco volta à linha de origem (AG-01 L5456-5466).
- Idempotência: não emite segunda O.S. para a mesma VIS × alvo nem abre segunda vistoria do mesmo talhão × alvo (AG-01 L5307-5308, L5204).

### Ideias das telas que saem

- AG-03/AG-03det: hipótese · causa e evidências vinculadas (vistoria + laudo, por seleção) na seção Decisão da vistoria do AG-01, com risco.
- AG-04: lista do RT com o que assinou (recomendação, versão, produto · dose · janela, situação '1 uso sem registro') como filtro 'Receituários' na OS.
- AG-04det: trava 'sem registro Agrofit para cultura × alvo' com troca por produto registrado; versões com alcance (realizado na v2, saldo na v3); memória de cálculo por zona (laudo → dose) na seção Receituário da O.S.
- AG-06: tabela pré/pós com método, datas (ex.: pré 19/09 · pós 27/09, 7 DAA), confiança e custo, e o cartão 'Economia do MIP' (aplicações evitadas, R$ 41 mil) no Painel › MIP.
- AG-05: NC por alvo e tabela de adubação versionados com fonte, validade e aprovador RT, alimentando MIPD.prot (AG-01) e a regra 'tabela regional a decidir' (AG-02).
- GE-07: 'Evidência esperada · como verificar no indicador' vira a meta de redução escolhida na decisão e conferida na leitura pós.
- AG-01det: a faixa 'Cadeia da demonstração' (VIS → DIA → REC → O.S. → avaliação) existe só para VIS-011; generalizar para toda vistoria como VIS → decisão/RA → O.S. → leitura pós, só com telas visíveis.

## Cadeia C · Da necessidade ao insumo entregue na O.S. e pago

Personas: Ana · Gestora e RT (agrônoma; hoje também compra e aprova), Caio · PCP, Rui · Almoxarife, Paula · Conferência (almoxarife), Marcos · operador de campo, Fornecedor (portal do parceiro), Proprietário/Direção (alçada e pagamento), Compras: não existe como papel nem pessoa (G2_PAPEIS)

### Etapas

| # | Etapa | Tela | Persona | Entidade | Estado | Como passa | Evidência |
|---|---|---|---|---|---|---|---|
| 1 | Detectar falta de insumo na O.S. | OS | Ana | O.S. | A liberar → A liberar · Falta insumo (dono Suprimentos) | automático | OS.dc.html:5145-5147 e 5481; os/os_lista.json OS-0418 "Liberar bloqueado: sem lote de Ureia 45%" |
| 2 | Somar necessidade do plano e das O.S. e enviar a SOL | SAF (Planejar safra) → CMP etapa 2 | Ana | Demanda / SOL | Plano + O.S. abertas → SOL enviada · a cotar (ou complemento -Cn) | botão | CMP.dc.html:5851 Ureia evs "P1 · OS-0418" falta 2026-09-24; CMP.dc.html:6098 "quem atualiza a SOL é o Planejar safra"; SAF.dc.html:7717 |
| 3 | Priorizar compra e conferir preço | PSUP, IC | Ana | Painel / item | — → — | link | PSUP.dc.html:5966 (só lotes e REQ); IC.dc.html:6069 prim "Abrir Compra de insumos" h:'CMP.dc.html' |
| 4 | Cotar com fornecedores homologados | CMP etapas 3-4; PT-01, PT-02, PT-02det | Ana; fornecedor | SOL / proposta | A cotar → Propostas recebidas (simulado) | botão | CMP.dc.html:6290 (sem homologado → CD-05); v3out/PT-02det "Submeter proposta v2" (tela estática) |
| 5 | Aprovar compra e emitir pedidos | CMP etapa 5 | Ana (alçada Gerente) ou Direção | PC | Aguardando alçada → Pedidos emitidos · PC-1xx | botão | CMP.dc.html:6199 id 'PC-'+(SX.pcIni+ix); CMP.dc.html:6210 estadoCompra |
| 6 | Acompanhar entrega do pedido | CMP etapa 6 | Ana | PC | Aguarda confirmação → Confirmado pelo fornecedor | botão | CMP.dc.html:6257-6258 "Confirmar fornecedor" → "Conferir no Estoque" |
| 7 | Receber NF e conferir contra o pedido | EST etapa Recebimentos | Rui | Recebimento / lote | A conferir → Conferida · apta ou em quarentena | botão | EST.dc.html:5161-5172 estReceber; v3out/EST diálogo "Recebimento · NF 4533" |
| 8 | Liberar quarentena com laudo | EST | Ana (AL-11) | Lote | Em quarentena → Disponível | botão | EST.dc.html:2745-2752 cenLiberarQuarentena (exige laudo) |
| 9 | Liberar a O.S. e reservar o lote | OS | Ana | O.S. / REQ | A liberar (sem falta) → Liberadas · REQ reservada | botão | OS.dc.html:2670-2689 cenLiberar (reserva e cria REQ) |
| 10 | Separar e entregar ao campo | EST (Entregue por O.S.); MB-05 aba Almoxarife | Rui | REQ | Reservada → Entregue · aguarda confirmação no app | aviso | os/os_lista.json OS-0424 "Iniciar bloqueado: REQ-039 sem entrega · Quem resolve: Rui"; EST.dc.html:5177 |
| 11 | Confirmar retirada no app | MB-05 (Minhas retiradas) | Marcos | REQ | Entregue → Confirmado no app · O.S. pode iniciar | botão | EST.dc.html:2827 cenConfirmarRecebimento; OS.dc.html:5360 'Ver no app' → MB-05 |
| 12 | Apontar consumo e devolver sobra | OS, MB-05det, EST (Receba devoluções) | Paula/operador → Rui | REQ | Em custódia → Devolvido · O.S. pode encerrar | link | os/os_lista.json OS-0417 "Encerrar bloqueado: sobra em custódia"; OS.dc.html:5220 h:'EST.dc.html' |
| 13 | Apropriar custo do consumo | GE-03 | Ana / controladoria | Lançamento de custo | Consumo conferido → Custo na competência | nada | v3/GE-03.dc.html sem motor (sem cenGet); v3out/GE-03 links REQ-035 → SU-07 |
| 14 | Programar e pagar o título do fornecedor | GE-04 (oculta, decisão do proprietário) | Ana / proprietário | Título | NF conferida → Programado · aguardando banco | nada | v3out/GE-04 "Abrir pedido" → SU-05.dc.html; navegacao.json GE-04 "só por link" |

### Quebras

**C-1 · alta · sem aviso ao próximo** · OS/Falta insumo → CMP/solicitação
- Hoje: O selo põe dono "Suprimentos" e só oferece "Ver saldos no Estoque". Não há botão de compra. Suprimentos não é papel nem perfil. A O.S. de origem aparece na Compra só como texto da memória.
- Impacto: OS-0418 vence hoje e ninguém de compras é chamado. Ana precisa lembrar de ir ao Planejar safra.
- Proposta: Na linha em falta, primária "Pedir compra urgente" no padrão manSolicitar/cmmDaOm (MA.dc.html:5254-5258): idempotente, quantidade = falta, precisa até = início da janela, origem OS-0418 clicável. Criar o papel Compras e mostrar a SC no selo. (esforço M)
- Evidência: OS.dc.html:5146 o.dono='Suprimentos'; OS.dc.html:5481 só h:'EST.dc.html'; OS.dc.html:768-779 sem perfil/papel de compras; CMP.dc.html:6282 cal01Memo(...).map(t=>({t})) sem link

**C-2 · alta · estado não propaga** · CMP/proposta e pedido → OS/Falta insumo
- Hoje: A Compra sabe que a Ureia falta em 24/09 e marca "Chega depois da falta". A O.S. continua dizendo "aguarda Ureia no Estoque", sem SOL, PC nem data. Na OS-0502 o texto cita "pedido de 50.000 kg em 30/09" que não existe na Compra (Safra Mamão sem solicitação).
- Impacto: Ana não sabe que precisa trocar produto ou ajustar área antes da janela. Decide com dado inventado.
- Proposta: Na linha do insumo da O.S., mostrar "Na SOL-2026-07 · PC-x · chega DD/MM" lido da Compra, em vermelho se chega depois da janela, com ação "Ajustar ou trocar produto". Tirar o texto semeado da OS-0502. (esforço M)
- Evidência: CMP.dc.html:5851 Ureia falta 2026-09-24, viavel 2026-09-30, Fertilizantes prazo 8-15 d; CMP.dc.html:6250/6330 "Chega depois da falta"; v3out/PT-02det Ureia 1.140 kg "entrega até 10/10"; OS.dc.html:5021 OS-0502 "pedido de 50.000 kg chega em 30/09"; v3out/CMP Safra Mamão "Sem solicitação"

**C-3 · alta · estado não propaga** · CMP/pedido emitido → EST/recebimento
- Hoje: O Estoque só oferece PC-088, 090, 091 e 096 fixos. Os pedidos aprovados na Compra (PC-101 em diante) ficam no armazenamento da Compra, que o Estoque não lê.
- Impacto: Rui não consegue receber contra o pedido aprovado. A nota entra sem vínculo e a conta pedido × nota se perde.
- Proposta: Pedido emitido vira registro do cenário (servidor) e alimenta a lista "Pedido" do recebimento e a fila "A conferir" com data prevista. (esforço M)
- Evidência: EST.dc.html:5021 E2.pedidos fixo; EST.dc.html:5096 epeds lê só E2.pedidos; CMP.dc.html:6080 SOL_LS (chave local das compras); CMP.dc.html:6094/6199 pcIni 101; EST não contém 'talhao-os-compras-v1'

**C-4 · alta · número diverge** · EST/recebimento → CMP/Acompanhe a entrega
- Hoje: A etapa 6 da Compra mostra recebido "—" (rec 0) nos pedidos novos e números fixos no PC-088. O que o Estoque confere não volta.
- Impacto: Ana vê pedido "a entregar" já recebido e pode cobrar o fornecedor ou pedir de novo.
- Proposta: Recebido, apto e quarentena da etapa 6 calculados dos movimentos recebimento-nf com o PC, como o motor de demanda já faz (CMP.dc.html:2579). (esforço P)
- Evidência: CMP.dc.html:6254-6255 rec:0,quar:0; CMP.dc.html:6260-6264 usa p.rec de CD.pedidos (fixo); EST grava estRec no movimento (EST.dc.html:5171)

**C-5 · alta · sem aviso ao próximo** · EST/recebimento → OS/A liberar com falta
- Hoje: Receber só soma físico e mostra "Disponível X → Y". O selo da O.S. some no próximo render, mas ninguém avisa Ana ou Caio e o saldo não fica guardado para a O.S. que esperava.
- Impacto: Outra O.S. liberada antes leva o insumo. A O.S. de origem perde a janela sem saber que o insumo chegou.
- Proposta: Ao receber item com O.S. aguardando, mostrar "Chegou para OS-0418" e pré-reservar para ela até a liberação (padrão D5). Aviso na fila de Ana em Aprovações/Meu dia: "Pronta para liberar". (esforço M)
- Evidência: EST.dc.html:2729-2737 cenReceber0 sem O.S.; EST.dc.html:5172 mensagem; OS.dc.html:5208 osLibErro recalcula; contraste MA.dc.html:5261-5262 (D5: o que chega para a OM fica reservado para ela)

**C-6 · alta · contexto perdido** · OS ↔ EST → registro aberto
- Hoje: "Entregar no Estoque", "Ver saldos" e "Receber devolução" abrem EST sem registro, na etapa Recebimentos. No Estoque, o número da O.S. é link para OS.dc.html sem #OS. A volta leva a Suprimentos e o detalhe não reabre.
- Impacto: Rui e Ana procuram a REQ ou a O.S. de novo a cada passagem.
- Proposta: Usar EST.dc.html#ent=REQ-039, #lote=Ureia 45%, #dev=REQ-031&para=OS-0417 e OS.dc.html#OS-0424 nos dois sentidos, com "Voltar à OS-0424". (esforço P)
- Evidência: OS.dc.html:5220, 5360, 5481 h:'EST.dc.html'; EST.dc.html:5345, 5370, 5441 h:'OS.dc.html'; v5out/OS.v5.json passagem "Entregar no Estoque": abriu false, volta "Voltar para Suprimentos", detalheReaberto false; EST já aceita #dev= (EST.dc.html:5477)

**C-8 · alta · beco sem saída** · PSUP/Painel → fila de trabalho
- Hoje: O painel só conta lotes com saldo, reserva, quarentena e REQ a entregar. Os cartões não abrem nada. Não mostra O.S. aguardando insumo, pedido atrasado nem "pedir até".
- Impacto: Quem cuida de suprimentos não vê a falta que trava a O.S.
- Proposta: Cartões clicáveis "O.S. aguardando insumo" (osLibErro), "Pedidos que chegam depois da falta" e "Itens a pedir até hoje" (SU-01), cada um abrindo a lista filtrada. (esforço M)
- Evidência: PSUP.dc.html:5966 vals só de lotes e reqs; v3out/PSUP cards só "Como calcular"

**C-10 · alta · beco sem saída** · Ocorrência ou vistoria → CMP/compra avulsa de insumo
- Hoje: A requisição avulsa da Compra exclui insumo ("Nunca safra ou cultura"). O único caminho é emitir O.S., enviar complemento da SOL e refazer 6 etapas, sem urgência. AG-01 avisa "a liberação aguarda a compra" sem ação.
- Impacto: Problema inesperado (praga, reposição) fica dias sem compra rastreável.
- Proposta: "Compra urgente de insumo" na Compra e na decisão MIP: item do catálogo, fazenda, motivo com vínculo (O.S., vistoria), precisa até; defensivo exige receituário do agrônomo; entra na demanda como recebimento firme para não duplicar. (esforço G)
- Evidência: CMP.dc.html:5774; CMP.dc.html:5851 viavel fixa 2026-09-30; AG-01.dc.html:5281; SAF.dc.html:7717

**C-11 · alta · beco sem saída** · MB-05/aba Almoxarife → EST, CMP, MB-05det
- Hoje: A aba tem 3 blocos fixos. "Conferir e entregar · bloqueado" só mostra texto fixo. Não há fila "A separar" (REQ-039 da OS-0424 não aparece) e "Receber devolução · REQ-031" não leva ao MB-05det.
- Impacto: Rui vê a falta no campo e não pode avisar compras nem separar pela fila.
- Proposta: Fila "A separar" lida das REQ liberadas, com lote e validade; no bloqueio, ação "Avisar Compras" que cria a solicitação de C-1; bloco de devolução com link para MB-05det#REQ-031. (esforço M)
- Evidência: MB-05.dc.html:26 (REQ-031 e REQ-038 fixos, 0 ocorrências de REQ-039, 0 links MB-05det); MB-05.dc.html:6483 M.m0 fixo; padrao/navegacao.json MB-05det "órfã"

**C-12 · alta · estado não propaga** · MB-05det/devolução no app → EST e OS-0417
- Hoje: MB-05det não carrega o cenário. "Confirmar recebimento de 10 sc" vem pré-preenchido e diz "custódia de Paula zerada", mas EST e OS-0417 não mudam.
- Impacto: Ao levar a tela ao visível, a devolução no app não encerra nada e o servidor deixa de ser a autoridade.
- Proposta: Ligar MB-05det a estDevolver (mesma regra do EST), quantidade contada sem pré-preencher e condição padrão quarentena. (esforço M)
- Evidência: v3/MB-05det.dc.html sem function cenGet; v3out/MB-05det.json status "recibo DV-0912 · custódia de Paula zerada"

**C-7 · média · contexto perdido** · IC, PSUP, EST, CMP → CMP / EST
- Hoje: IC "Abrir Compra de insumos", PSUP "Acompanhar compras" e EST "Ver pedido" abrem CMP na etapa 1 "Escolha a safra". CMP "Conferir no Estoque" abre EST sem a NF.
- Impacto: O item ou pedido escolhido se perde; a pessoa refaz a busca.
- Proposta: CMP aceitar #pc=PC-088 e #item=Óleo mineral (abre etapa 2 ou 6 no registro); EST aceitar #nf=NF 4533. (esforço P)
- Evidência: IC.dc.html:6069, 6076 h:'CMP.dc.html'; PSUP.dc.html:61; EST.dc.html:5326; CMP.dc.html:6258, 6264, 6557; CMP só aceita #sol=&saf= (CMP.dc.html:6440)

**C-9 · média · número diverge** · IC → CMP
- Hoje: Óleo mineral: IC manda "Comprar agora · necessidade 28/09 · pedir até 23/09"; a demanda da Compra tem falta só em 12/11; SU-01 diz "pedir até 13/09 · atrasado".
- Impacto: Compra antecipada ou pânico falso. Três datas para a mesma decisão.
- Proposta: IC usar a data de falta líquida da demanda única (cal01) e mostrar "cobre até DD/MM". (esforço M)
- Evidência: v3out/IC.json diálogo Óleo mineral; CMP.dc.html:5851 Óleo mineral est 400, liq 210, falta 2026-11-12; dumps/SU-01.txt Óleo mineral data 2026-09-25

**C-13 · média · redigitação** · Nota fiscal → EST/recebimento
- Hoje: O almoxarife digita conferida, apta, quarentena e validade. Apta + quarentena repete a conferida. Não há leitura da NF-e.
- Impacto: Rui gasta tempo e erra soma; risco de lote sem validade.
- Proposta: Ler XML/chave/QR da NF-e (SU-06), sugerir conferida = nota e quarentena = conferida − apta; digitar só a divergência. (esforço M)
- Evidência: v3out/EST.json diálogo Recebimento (11 campos, 4 vazios); padrao/ocultas.json SU-06 "O EST pede 11 campos e o almoxarife digita 5"

**C-14 · média · ação fora do lugar** · EST/divergência → CMP/pedido e fornecedor
- Hoje: Falta, avaria ou item diferente ficam como chip vermelho no Estoque. "Item diferente" manda "corrigir o pedido antes de receber", mas a Compra não tem essa ação nem mostra a divergência.
- Impacto: Ninguém de compras cobra o fornecedor; o pedido fica aberto ou errado.
- Proposta: Divergência gera pendência com dono Compras no PC (etapa 6), com link à NF; ação "Pedir correção ao fornecedor" ali mesmo. (esforço M)
- Evidência: EST.dc.html:5159 EST_ITEM_DIFERENTE; EST.dc.html:5334 chip divergência; CMP.dc.html:6253-6265 etapa 6 sem divergência

**C-15 · média · número diverge** · OS/reserva → EST/saldos
- Hoje: OS-0424 mostra "Na ordem 64 L" e "Reservado 65 L" e cita "recibo RS-7741", que o Estoque não conhece. No Estoque o lote F26-02 mostra só "Reservado 65 L", sem REQ nem O.S.
- Impacto: Rui não sabe de quem é a reserva; Ana vê dois números para a mesma reserva.
- Proposta: Um só número (REQ-039) em O.S., Estoque e app; explicar arredondamento à embalagem ("64 L → 13 galões = 65 L"); no lote, "Reservado para REQ-039 · OS-0424" com link. (esforço P)
- Evidência: OS.dc.html:2351 OS-0424 tot 64 × REQ-039 solicitado 65; OS.dc.html:2679 reserva x.tot; RS-7741 só em OS, SU-03det, SU-07, IN-04, PAGR; EST.dc.html:5307 res só número

**C-16 · média · contexto perdido** · OS/liberação → EST/lote de outra fazenda
- Hoje: A reserva escolhe o lote de maior disponível, sem fazenda e sem validade. OS-0501 (Lagoa Grande) reservaria Glifosato e Óleo do Almox. defensivos (Santa Rita), sem transferência.
- Impacto: Insumo reservado longe da área; ninguém programa o transporte; lote mais velho fica parado.
- Proposta: Filtrar lote pela fazenda da O.S. e ordenar por validade (FEFO); se só houver em outra fazenda, mostrar "Disponível em Santa Rita" e "Pedir transferência" (SU-08). (esforço M)
- Evidência: OS.dc.html:2514 cenLote ordena por cenDisp; OS.dc.html:2351 G26-14 e O26-05 em Almox. defensivos; dumps/CD-06.txt l3 Almox. defensivos faz Santa Rita

**C-17 · média · ação fora do lugar** · IN-01/Meu dia → OS-0418 e EST
- Hoje: Meu dia (vai para o visível) mostra "Falta insumo · Ureia 45%" e manda Ana "Liberar", ação bloqueada. "Receber devolução" de Rui abre EST sem a REQ.
- Impacto: Ana clica, cai no bloqueio e volta. Rui procura a REQ-031.
- Proposta: Próxima ação calculada pelo selo: "Ajustar ou trocar produto" ou "Ver compra"; devolução com EST.dc.html#dev=REQ-031. (esforço P)
- Evidência: IN-01.dc.html:58 f2 acao 'Liberar' h:'OS.dc.html#OS-0418'; f4 acao 'Receber devolução' h:'EST.dc.html'

**C-18 · média · passa por tela que será excluída** · Consumo da O.S. → GE-03/custo
- Hoje: GE-03 é estático e liga REQ-035 a SU-07, NF 8842 a SU-06 e apontamento a CA-02. O consumo da REQ-031 (3.500 kg de MAP na OS-0417) não aparece.
- Impacto: Custo da safra não bate com o Estoque; links quebram quando as telas legadas saírem.
- Proposta: Ler os lançamentos dos movimentos de consumo do cenário e apontar para EST.dc.html#ent=REQ-035 e OS.dc.html#OS-0421. (esforço M)
- Evidência: v3out/GE-03.json links SU-06/SU-07/CA-02; dumps/GE-03.txt g_lan sem OS-0417; OS.dc.html:2351 REQ-031 consumido 3500

**C-19 · média · passa por tela que será excluída** · EST/recebimento e CMP/pedido → GE-04/título
- Hoje: Nem Estoque nem Compra mostram o título. GE-04 abre o pedido no SU-05. O título PC-084 · NF 8790 não tem pedido na Compra. O título de R$ 233.000 do PC-088 corre "28 dias após a NF 4501", que tem 60.000 kg (10 t em quarentena).
- Impacto: Pagamento sem conferência pedido × nota × recebimento; risco de pagar o que não chegou.
- Proposta: Decidida a questão do financeiro: mostrar no PC (CMP etapa 6) e no recebimento a situação do título e a conferência em 3 vias; link GE-04 → CMP.dc.html#pc=PC-088. (esforço M)
- Evidência: v3out/GE-04.json "Abrir pedido" → SU-05.dc.html; PC-084 só em GE-04 e SU-03; dumps/GE-04.txt fer "Título único de R$ 233.000 · 28 dias após a NF 4501"; EST.dc.html:5021 r4501 conf 60000, quar 10000

**C-20 · baixa · estado não propaga** · PT-01/PT-02det (fornecedor) → CMP/cotação
- Hoje: O portal mostra "Comprador pergunta: o frete CIF vale para os 5 itens?" e "Comprador pede a placa da carga 3", mas a Compra não tem esclarecimento nem link ao portal. O portal é estático e a Compra simula as propostas.
- Impacto: A conversa com o fornecedor fica fora do registro da cotação.
- Proposta: Se o portal ficar: esclarecimentos e propostas gravados na SOL e visíveis na etapa 3-4 da Compra; senão, campo "Pergunta ao fornecedor" na própria cotação. (esforço G)
- Evidência: v3out/PT-01.json avisos; v3out/PT-02det.json g_esc; CMP.dc.html 0 ocorrências de "esclarec" e de PT-0

### Já funciona

- A demanda da O.S. chega à Compra sem redigitar: Ureia 1.140 kg, falta 24/09, "P1 · OS-0418 · 12,00 kg/ha × 95 ha" (CMP.dc.html:5851), contada uma vez (DEM-04).
- O selo "Falta insumo" é calculado ao vivo e diz o número: "60.000 kg disponíveis para 96.940 kg" (OS.dc.html:5208; os/os_lagoa.json OS-0502).
- No ajuste, cada produto mostra "N disponíveis" ou "sem saldo no Estoque", com saldo primeiro (OS.dc.html:6083).
- REQ com o mesmo número em O.S., app e movimento: REQ-038 na OS-0418 e no MB-05; a reserva grava req e os (OS.dc.html:2681; MB-05.dc.html:26).
- Reserva protege a O.S. que liberou: disponível = físico − quarentena − reservado; entrega baixa só a reserva própria (OS.dc.html:2515; EST.dc.html:2704).
- Iniciar bloqueado nomeia quem age: "Rui entrega no Estoque; Marcos confirma no app" e a entrega exige confirmação (os/os_lista.json OS-0424; EST.dc.html:5177).
- Recebimento idempotente, quarentena fora do disponível e laudo obrigatório para liberar (EST.dc.html:2726-2752).
- Compra ↔ Planejar safra com registro aberto: "Ver origem" → SAF.dc.html#saf=S2627&passo=demanda e #sol=…&saf=… abre a etapa 2 (v3out/CMP.json; CMP.dc.html:6440).
- Compra escolhe por padrão a proposta mais barata que chega antes da falta e marca "Chega depois da falta" (CMP.dc.html:6193, 6330).
- Grupo sem fornecedor homologado leva a Cadastros › Parceiros (CMP.dc.html:6290).
- Encerrar bloqueado por sobra em custódia diz quanto, com quem e quem resolve (os/os_lista.json OS-0417).
- Meu dia abre a O.S. certa: OS.dc.html#OS-0418 (IN-01.dc.html:58).
- Preços do portal batem com a Compra: MAP R$ 3,90 × 0,97 = R$ 3,783/kg (v3out/PT-02det.json; CMP.dc.html:5851 props F01).

### Ideias das telas que saem

- SU-01: "Pedir até = necessária − prazo do fornecedor − segurança", contador "18 itens com falta firme · 5 atrasados" e "Reprogramar proposta" com motivo → CMP etapa 2 e PSUP.
- SU-01: demanda aberta por origem (cultivo, plano, dose × área) com link ao Planejar safra → memória da CMP etapa 2, incluindo link à O.S.
- SU-05/SU-05det: "Uso previsto" por pedido (PC-090 → plantio T1-A e T2; PC-094 → OM-0234) e liberação de carga com "cobertura atendida" → CMP etapa 6 e selo da O.S.
- SU-06: ler NF-e/QR, tolerância +5 %, NF duplicada ("Mesma chave de acesso… nenhuma entrada nova"), divergência de preço contra contrato (R$ 0,12/L × 15.000 L) e "aceite físico não aprova o título" → EST Recebimentos.
- SU-03det: linha "Reserva confirmada · OS-0424 · 65 L" e "Pendência de compra" no lote → painel do lote no EST, usando REQ-039.
- SU-07: "Separar pelo FEFO e entregar à custódia de Marcos" → fila "A separar" do EST e do MB-05.
- SU-08: transferência TR-0452 "em trânsito" com confirmação no destino → EST, para O.S. de outra fazenda (OS-0501).
- SU-07det: devolução entra em quarentena de sobras (lote M26-05) até conferir → EST e MB-05det.
- CA-04: colunas "Devolvido declarado · recebido" e gaveta "Solicitar material da ordem" → painel da O.S. (seção Insumos).
- SU-02: mínimo, ponto de pedido e máximo por item e depósito → CD-06 seção Reposição, alimentando o PSUP.

## Cadeia D · Da máquina com problema à máquina liberada, com custo

Personas: Otávio · responsável de manutenção (PCM), Zé · mecânico (responsável técnico do Trator T1), Marcos e Carlos · operadores de campo, Caio · PCP, Ana · gestora (cotação, pedido e custos), Rui · almoxarife

### Etapas

| # | Etapa | Tela | Persona | Entidade | Estado | Como passa | Evidência |
|---|---|---|---|---|---|---|---|
| 1 | Calcular o vencimento do plano preventivo | MA (Sem ordem) · PMAN | Otávio | Vencimento de plano (PM-) | Em dia → Vencida · sem ordem | automático | v3out/MA.json linha 'PM-02 v2 · vencimento Trator 03 · 5.120 h … Vencida · 30 h além'; v3out/PMAN.json link 'Tratar pendências' → MA.dc.html#vis=semordem |
| 2 | Relatar a falha da máquina no app | MB-04 | Marcos ou Carlos (operador) | Achado (SM-) | — → Sem ordem · selo Nova, ligado à O.S. do turno | automático | MB-04 L6278 'Vai como achado para a Manutenção (Sem ordem), ligado à OS-…; o Otávio decide o serviço'; L6292 regAch → mbManCmd('achado') |
| 3 | Registrar achado de inspeção ou do checklist | MA (⋯ Registrar achado) · checklist da OM | Zé ou Otávio | Achado (INSP-, NC-) | — → Sem ordem | botão | v3out/MA.json menu 'Registrar achado'; MA L5453 manAchRegistrar (prefixo SM/INSP/NC pela origem) |
| 4 | Decidir o achado: corretiva, vincular ou preventiva | MA (painel do achado) | Otávio | Achado → OM | Sem ordem → Na OM-xxxx (OM em A liberar) | botão | v5out/MA.v5.json NC-0912 primária 'Gerar ordem preventiva com NC-0912'; INSP-104 'Vincular à OM-0234'; MA L5480 manAchOpcoes |
| 5 | Bloquear a máquina | MA (painel Condição) | Otávio ou responsável técnico | Ativo | Apto → Bloqueado | aviso | MA L5545 manCondicao: '… bloqueado (CMD-18) · … · alocado em OS-…: avise o PCP (O.S. › Recursos)' (texto só para quem bloqueou) |
| 6 | Gerar a ordem de manutenção preventiva | MA (Sem ordem) | Otávio | OM (OM-) | Vencida sem ordem → A liberar (com Falta peça quando falta) | botão | v3out/MA.json 'Gerar 3 ordens preventivas' → '3 ordens em A liberar: OM-0235, OM-0236, OM-0237 · OM-0235 com Falta peça' |
| 7 | Pedir a peça em falta | MA (painel da OM) | Otávio | Requisição de compra (SC-) | OM A liberar · Falta peça → SC A cotar em Compras › Materiais, peças e serviços, com a OM de origem | botão | MA L5254 manSolicitar → cmmDaOm (orig 'om', om: o.id, motivo 'Falta peça para liberar a OM-…'); v3out/MA.json primária 'Solicitar compra (simulado · Compras recebe no 1c)' |
| 8 | Cotar, emitir o pedido e receber a peça | CMP (Materiais, peças e serviços) | Ana (cotar e pedir) · Rui (receber) | SC → PC- | A cotar → Recebida · peça reservada para a OM | botão | CMP L6685 'Origem … Abrir OM-…' → MA.dc.html#om=; MA L5822 cmmReceber0 → manReceberSc (D5: reserva para a OM, trilha pedido › recebimento › reserva › ordem) |
| 9 | Liberar a OM para a oficina | MA (painel da OM) | Otávio | OM | A liberar → Liberadas · peças reservadas · executante definido | botão | MA L5242 manLiberar; ma_omPrim0 'Liberar serviço', 'Mover janela para dd/mm', 'Liberar mesmo assim' |
| 10 | Executar o serviço no app do mecânico | MB-09det | Zé | OM | Liberadas → Em execução → Em conferência (tarefas, teste, leitura e horas) | botão | v3out/MB-09det.json h1 'OM-0233 · Trator T1'; MB-09det mbManCmd → MA L5673 manAppCmd (fila sem sinal com chave do aparelho) |
| 11 | Declarar a máquina apta | MB-09det ou MA (painel da OM) | Zé (responsável técnico) ou Otávio | Ativo | Bloqueado → Apto | botão | MA L5415 manDeclararApto: '… apto · CMD-19 … a agenda antiga não é reassumida; volta pela reprogramação do PCP' (L5423) |
| 12 | Encerrar a OM com custo | MA (painel da OM) | Otávio | OM | Em conferência → Encerradas · custo final | botão | MA L5445 manEncerrar: custo = peças aplicadas + horas × Custo R$/h da oficina + terceiro; primária 'Encerrar ordem · R$ …' |
| 13 | Tirar o impedimento da O.S. que dependia da máquina | OS (painel da O.S.) · PAGR | Caio (PCP) · Ana (libera) | O.S. | Impedida · ativo bloqueado → A liberar · dono PCP 'reprogramar antes de liberar' (ou segue a fase) | automático | OS L5160 osManCond (só para O.S. com bloq.aid: OS-0420 e OS-0431) |
| 14 | Ver o custo da manutenção por máquina | MA (Ativos) · GE-03 | Ana · proprietário | Lançamento de custo | OM encerrada → Lançamento no fechamento da competência | nada | dumps/MA.txt g_at coluna 'Custo no mês'; GE-03 L58 lançamento om233 fixo R$ 18.400; GE-03 não lê o cenário |
| 15 | Acompanhar o conserto (quem relatou) | MB-09 | Operador | Ativo e OM | Relato enviado → Vê a condição só se abrir a máquina | nada | MB-09 L6247 mbCond 'Não opere · bloqueado · … · OM-0233'; L6277 'OM-… · etapa · abrir ordem' |

### Quebras

**D-1 · alta · estado não propaga** · MA/Bloquear a máquina → OS/impedimento da O.S.
- Hoje: Bloquear um ativo no MA não marca as O.S. que o usam. O impedimento só existe nas O.S. com bloq.aid fixo no cenário (OS-0420 e OS-0431, Trator T1). Os alertas de Recursos da O.S. mostram só choque de agenda, não a condição.
- Impacto: Caio e Ana liberam ou apontam O.S. com máquina parada. Ex.: bloquear o Trator 02 não afeta a OS-0420 (alocada de 24 a 28/09). O PAGR também não conta.
- Proposta: Derivar o impedimento de toda O.S. aberta cujo recurso (MAN_AL.rec + alocação vigente) esteja Bloqueado em c.man, sem depender de bloq.aid: selo 'Impedida · <ativo> bloqueado (OM-x)', dono PCP, link 'Acompanhar OM-x'; na linha do recurso, 'Bloqueado na Manutenção'. (esforço M)
- Evidência: MA L5337 manOsAloc '… aviso, nunca promessa de impedimento (A9)'; OS L5160 osManCond sai se !b.bloq.aid; OS L4999 alDaOrdem só usa alChoques; alBloqueado só em alCandidatos

**D-2 · alta · sem aviso ao próximo** · MA/Bloquear a máquina → PCP (Caio)
- Hoje: Ao bloquear, o comprovante diz ao próprio Otávio 'avise o PCP (O.S. › Recursos)'. Nada chega ao Caio: nenhuma fila, selo ou contagem nova fora das duas O.S. já ligadas.
- Impacto: O PCP só descobre ao abrir a O.S. ou por telefone; a janela de plantio corre.
- Proposta: O bloqueio cria item no Meu dia do PCP 'Reprogramar O.S. com <ativo> bloqueado' com as O.S. afetadas e link OS.dc.html#painel=…; o comprovante troca 'avise o PCP' por 'PCP avisado: OS-…'. (esforço M)
- Evidência: MA L5545 manCondicao (mensagem); IN-01 não lê o cenário (cenGet só no aviso de assinatura); OS.dc.html: 0 leituras de man.oms

**D-3 · alta · sem aviso ao próximo** · MA/Liberar OM com conflito → OS/PCP
- Hoje: 'Liberar mesmo assim' grava conflitoAceito e o comprovante diz 'conflito com a OS-… aceito e avisado ao PCP'. A O.S. e o PAGR não leem as OMs: nada é avisado.
- Impacto: Promessa falsa. Caio não sabe que a OM-0234 tomará o Trator 02 em 28/09 da OS-0420.
- Proposta: Na O.S. afetada, alerta no recurso 'OM-0234 usa Trator 02 em 28/09 (aceito por Otávio)' com link MA#om=OM-0234 e item no Meu dia do PCP. Até existir, trocar o texto para 'avise o PCP'. (esforço M)
- Evidência: MA L5252 manLiberar (mensagem); OS.dc.html: 0 ocorrências de 'conflitoAceito' e de 'man.oms'; PAGR só tem a cópia do motor

**D-8 · alta · passa por tela que será excluída** · OS/OS-0420 impedida → CA-01x-os0420
- Hoje: O impedimento do Trator T1 na OS-0420 leva a 'Abrir a ordem completa' → CA-01x-os0420.dc.html. Como o registro tem h próprio, o link 'Acompanhar OM-0233' não é gerado.
- Impacto: Ao excluir CA-01*, o PCP fica sem caminho da O.S. para a OM.
- Proposta: Tirar h e hl do bloq da OS-0420 para cair em 'Acompanhar OM-0233' (MA.dc.html#om=OM-0233). (esforço P)
- Evidência: OS L5021 bloq OS-0420 {'h': 'CA-01x-os0420.dc.html', 'hl': 'Abrir a ordem completa'}; OS L5160 'b.bloq.h?{}:{h:MA.dc.html#om=…}'

**D-9 · alta · passa por tela que será excluída** · IN-01 Meu dia → PL-05
- Hoje: Meu dia (vai virar atalho visível) mostra 'Substituir Trator T1 bloqueado · Ativo bloqueado · OM-0233' com ação 'Reprogramar saldo' → PL-05. A tela não lê o cenário: a linha segue igual depois do apto.
- Impacto: O PCP age sobre dado velho e cai numa tela que sai.
- Proposta: Gerar a linha do Meu dia do impedimento derivado da O.S. (D-1), com destino OS.dc.html#OS-0420; sai sozinha quando o ativo fica Apto. (esforço M)
- Evidência: IN-01 L58 linha f1 acao {'t': 'Reprogramar saldo', 'h': 'PL-05.dc.html'}; IN-01 sem leitura do cenário (cenGet só em assinLer)

**D-16 · alta · estado não propaga** · MB-04 'Pode operar? Não' → MA/Condição · MB-09
- Hoje: O 'Não' do operador só vira sugestão Bloqueado. A máquina segue 'Apto para operar' no MB-09 para outro operador até Otávio agir. No MA, criar a corretiva e bloquear são dois painéis (achado e 'Mudar condição ›'); corretiva criada com o ativo Apto não trata a condição.
- Impacto: Outro operador pode levar a máquina quebrada a campo; Otávio faz dois passos.
- Proposta: No MB-09, faixa amarela 'Relato de hoje: não operar (SM-…) · aguardando Otávio'. No painel do achado com sugestão Bloqueado, primária 'Bloquear e criar corretiva' (manCondicao + manAchCorretiva numa ação; decisão segue com Otávio ou responsável técnico). (esforço M)
- Evidência: MB-04 L6292 regAch sem 'bloquear'; MA L5453 manAchRegistrar bloqueia só com d.bloquear; MA L5501 manAchCorretiva trata só se a.cond≠Apto; v5out/MA.v5.json passagem 'Mudar condição ›'

**D-17 · alta · sem aviso ao próximo** · MA/Declarar apto · encerrar OM → OS/PCP
- Hoje: Com a máquina apta, o impedimento some e o dono da O.S. vira PCP ('reprogramar antes de liberar'), mas ninguém avisa o Caio. Na OS-0420 (Em execução), 'O Trator 02 assume a partir de 24/09' é só texto: trocar recurso só existe antes da execução.
- Impacto: Máquina pronta fica parada; O.S. espera sem ninguém saber.
- Proposta: O apto cria item no Meu dia do PCP 'Trator T1 apto (OM-0233) · reprogramar OS-0431' com link à O.S.; permitir 'Trocar recurso a partir de dd/mm' no saldo de O.S. Em execução (ideia do PL-05det). (esforço M)
- Evidência: MA L5423 mensagem 'volta pela reprogramação do PCP'; OS L5160 osManCond (dono 'PCP', prazo 'reprogramar antes de liberar'); OS L5015 alTrocar 'só antes da execução'; OS L5021 bloq OS-0420 q 'O Trator 02 assume a partir de 24/09'

**D-18 · alta · número diverge** · MA/Encerrar OM com custo → GE-03
- Hoje: GE-03 mostra OM-0233 R$ 18.400 ('peças + 6,5 h', Provisório · aguarda NF) com a OM ainda Em execução. No MA a mesma OM estima R$ 6.180 (peças R$ 4.100 + 6,5 h × R$ 320), mais R$ 1.843 do PC-201 quando aceito. GE-03 não lê o cenário: encerrar a OM não cria nem corrige lançamento, e não há visão de custo por máquina.
- Impacto: Ana fecha a competência com custo de manutenção errado; o custo por máquina só existe em MA › Ativos.
- Proposta: GE-03 gera o lançamento da OM por manCustoFinal no encerramento (provisório por manCusto 'est' enquanto aberta) e agrupa 'Manutenção por máquina' com link MA#ativo=. (esforço M)
- Evidência: GE-03 L58 GRIDS om233 val 18400; GE-03 sem leitura do cenário; cenário OM-0233 peças 3.600 + 2 × 250, tempo 6,5 h, custoh 320; SC-038 PC-201 R$ 1.843

**D-4 · média · beco sem saída** · MA/Propor substituto → OS/Trocar recurso
- Hoje: 'Propor substituto (simulado · o PCP decide)' grava c.prop e diz 'aguarda PCP em O.S. › Recursos'. A O.S. não lê c.prop; o selo só aparece no próprio MA (Ativos).
- Impacto: A proposta do Otávio morre; o PCP refaz a análise do substituto.
- Proposta: No painel da O.S. afetada, linha do recurso com 'Substituto proposto: Trator 02 (Otávio)' e 'Trocar recurso' já preenchido (alTrocar). Tirar '(simulado)' do rótulo. (esforço M)
- Evidência: MA L5643 manPropor (L5645 mensagem); MA L5914 ma_selosAtv; OS.dc.html: 0 ocorrências de 'c.prop' e 'Substituto proposto'

**D-5 · média · contexto perdido** · MA/painel da OM (Impacto na produção) · CD-03 → OS
- Hoje: 'Impacto na produção: OS-0431 · lido da alocação do PCP' é texto; os IDs não abrem. No CD-03, 'Ver ordens afetadas · OS-0420 e OS-0431' leva a OS.dc.html sem filtro.
- Impacto: Otávio e Ana procuram a O.S. na lista inteira.
- Proposta: Cada ID vira link OS.dc.html#painel=OS-… (formato que o PAGR já usa); no CD-03 o mesmo link com as O.S. listadas. (esforço P)
- Evidência: MA L52 template <div …>{{om_imp}}</div>; MA L6257; CD-03 L5411 {t:'Ver ordens afetadas …',h:'OS.dc.html'}

**D-6 · média · número diverge** · MA/painel da OM → CD-03 · PAGR
- Hoje: O.S. afetadas pelo Trator T1: MA mostra só OS-0431 (alocação de hoje em diante); CD-03 mostra OS-0420 e OS-0431 (lista fixa); PAGR conta 3 em 'Máquina ou equipamento'. A OS-0420, pausada pelo T1, some no MA.
- Impacto: Cada pessoa vê um impacto diferente para a mesma parada.
- Proposta: Uma função única 'O.S. afetadas pelo ativo' (O.S. abertas com o recurso desde condInfo.desde, como manPropAfeta) usada por MA, CD-03, OS e PAGR. (esforço P)
- Evidência: MA L6257 usa = alocação dia ≥ hoje; CD-03 L5317 cond a01 ordens ['OS-0420','OS-0431']; v3out/PAGR.json 'Abrir 3 O.S. por causa: Máquina ou equipamento' → OS#painel=OS-0420,OS-0431,OS-0507

**D-7 · média · beco sem saída** · OS/OS-0507 impedida → MA/OM-0251
- Hoje: OS-0507 aparece 'Impedida · bomba em manutenção (OM-0251)'. A OM-0251 e a Bomba do Pivô 5 não existem na Manutenção. O bloqueio não tem bloq.aid nem link e nunca sai.
- Impacto: Joaquim e o PCP esperam uma OM que ninguém executa; o PAGR conta um impedimento sem dono real.
- Proposta: Criar o ativo Bomba do Pivô 5 e a OM-0251 no cenário da Manutenção e ligar bloq.aid; ou tirar o selo da OS-0507. (esforço P)
- Evidência: OS L5021 OS-0507 bloq sem aid 'Apontamento parado: bomba do Pivô 5 em manutenção (OM-0251)'; MA.dc.html e PMAN.dc.html: 0 ocorrências de OM-0251

**D-10 · média · contexto perdido** · MA/painel da OM (Falta peça) → CMP/SC da OM
- Hoje: Depois de pedir, a compra aparece só como selo 'Compra SC-0xx (simulado)'. O MA não tem link para o CMP, que já abre direto por #tipo=materiais&sc=SC-…. O rótulo 'Solicitar compra (simulado · Compras recebe no 1c)' diz simulado, mas a SC já entra na fila real de Compras.
- Impacto: Otávio não vê cotação, PC e previsão de chegada; pergunta a Compras.
- Proposta: Selo vira link 'SC-0xx · PC-… · chega dd/mm ›' → CMP.dc.html#tipo=materiais&sc=SC-0xx; rótulo 'Solicitar compra da peça'. (esforço P)
- Evidência: MA L5187 selo; MA.dc.html: 0 ocorrências de 'CMP.dc.html'; CMP L6579 cmHashLer aceita sc=; MA L6197 rótulo

**D-11 · média · estado não propaga** · MA/Solicitar compra → CMP/reposição aberta
- Hoje: A falta da OM é calculada só pelo livre. O Filtro de óleo MF 4292 já tem a SC-039 de reposição (4 un, em cotação); a OM-0235 abre outra SC para 1 un.
- Impacto: Ana cota e compra duas vezes a mesma peça; a SC da OM fica sem uso quando a reposição chega ao livre.
- Proposta: Antes de criar a SC, mostrar 'SC-039 de reposição já pede 4 un (chega dd/mm)' com 'Reservar da SC-039 para a OM-0235' ou 'Pedir separado'. (esforço M)
- Evidência: MA L5254 manSolicitar qtd = necessidade − livre (não usa cmmPedido, L5757); cenário SC-039 'Filtro de óleo MF 4292' 4 un Em cotação; v3out/MA.json OM-0235 'Falta peça'

**D-12 · média · ação fora do lugar** · CMP/receber a peça → EST · MA
- Hoje: O recebimento da peça da OM tem duas portas: no MA, Otávio usa 'Registrar recebimento (simulado · papel do Almoxarifado)' (regra 'ponte' só do PCM); no CMP o mesmo recebimento exige almoxarife ou gestora. O Estoque (tela do Rui) não lista peças da oficina nem reservas por OM. As sobras também são devolvidas por Otávio no MA.
- Impacto: Rui não confere a peça que chega; mesma operação com quem pode diferente em cada tela.
- Proposta: Tirar 'Registrar recebimento' e 'Resolver sobras' do MA; no painel da OM mostrar 'Aguarda recebimento · Rui' com link para a SC; no EST, visão 'Peças da oficina' com saldo, reservado por OM e recebimento da SC. (esforço M)
- Evidência: MA L6198 botão; MA L5079 'ponte' só pcm; CMP cmmPode 'receber' → almoxarife ou gestor; dumps/EST.txt sem itens da oficina (FIL-MF4292, KIT-…)

**D-13 · média · sem volta à origem** · OS · CMP · GE-03 · CD-03 (links MA#om=) → MA/painel da OM
- Hoje: O painel da OM abre pelo endereço, mas o único caminho de volta é 'Voltar para Manutenção' (MOD-MAN). O endereço não guarda de onde veio.
- Impacto: PCP que foi da OS-0431 para a OM-0233 perde a O.S. de origem.
- Proposta: Aceitar &de=OS-0431 (ou SC-, CD-03) no endereço e mostrar 'Voltar à OS-0431' no topo do painel. (esforço P)
- Evidência: v3out/MA.json links 'Voltar para Manutenção' → MOD-MAN.dc.html; MA L5866 ma_hashLer/ma_hashDe sem parâmetro de origem

**D-14 · média · acessibilidade** · OS · CMP · GE-03 (links MA#om=) → MA/painel da OM
- Hoje: Pelo endereço, o painel abre como modal, mas o foco não entra nele: ma_aplicaHash não foca, ao contrário de ma_abrir. Ao fechar, não há elemento para devolver o foco.
- Impacto: Quem usa teclado ou leitor de tela fica fora do modal aberto.
- Proposta: Ao abrir pelo endereço, focar #ma-painel e anunciar 'Painel da OM-0233 aberto'; ao fechar, focar a linha da OM. (esforço P)
- Evidência: MA L5879 ma_aplicaHash (pan modal sem focus); MA L5896 ma_abrir com setTimeout focus em #ma-painel

**D-15 · média · sem aviso ao próximo** · MB-04/relato do operador → MA/OM e máquina apta
- Hoje: Após registrar, MB-04 mostra o estado uma vez ('Na Manutenção · Sem ordem'). A lista de ocorrências recentes traz só ocorrências da O.S., não os achados SM-. Nada avisa quando vira OM, quando é resolvido ou quando a máquina volta a Apto.
- Impacto: O operador que relatou não sabe se pode voltar a operar; liga para a oficina.
- Proposta: No MB-01 e no MB-04, bloco 'Meus relatos' com SM-…: Sem ordem → Na OM-0233 · Em execução → Resolvido · Trator T1 apto; aviso no app quando a máquina relatada volta a Apto. (esforço M)
- Evidência: MB-04 L6309 ocs de c.ocorr; código de MB-01, MB-04 e MB-09: 0 leituras de 'achados'; MB-09 L6247 só a condição atual

**D-19 · baixa · ação fora do lugar** · PMAN Painel → MA
- Hoje: Os cards 'Ativos bloqueados' e 'Em execução' não abrem nada. O painel não mostra O.S. afetadas, OMs com falta de peça nem compras em atraso.
- Impacto: Otávio e Ana não partem do painel para agir na parada.
- Proposta: Cards viram links (MA#vis=ativos com filtro Bloqueado; MA#vis=ordens por fase) e nova seção 'Manutenções e impacto na produção' (ideia do PL-03). (esforço P)
- Evidência: PMAN template section.pn-card sem link; v3out/PMAN.json cards com ação só 'Como calcular'

### Já funciona

- Pedir a peça em falta cria a SC na fila de Compras num clique, com a OM e o motivo; no CMP a SC mostra 'Origem … Abrir OM-…' → MA#om= (MA L5254 manSolicitar → cmmDaOm; CMP L6685).
- A peça que chega pela SC fica reservada para a OM que pediu, com trilha pedido › recebimento › reserva › ordem e 'pronta para liberar' (MA manReceberSc, manRecTxt; painel Peças 'Peça chegou · reservada').
- Gerar preventivas em lote abre a primeira e oferece 'Abrir as 3 › próxima: OM-0236' (v3out/MA.json).
- O painel da OM mostra Veio de · Está aqui · Falta (com dono) · Próxima ação e as cinco fases (v3out/MA.json OM-0235).
- Liberar trava sem peça e, com conflito na janela, propõe 'Mover janela para dd/mm' sem conflito dentro da tolerância (MA ma_omPrim0).
- OS-0431 lê a condição do Trator T1 da Manutenção, mostra 'Acompanhar OM-0233' e perde o impedimento sozinha quando o T1 fica Apto (OS L5160 osManCond).
- O app do mecânico executa a OM sem sinal, com chave de idempotência e 'Conflito a resolver · Otávio' quando a OM mudou no escritório (MA L5673 manAppCmd, L5686 manAppSinal).
- O relato do app vira achado SM- pela mesma função da web; Otávio abre em Sem ordem quando há achado grave (MB-04 L6292; MA ma_abertura).
- MB-09 mostra ao operador 'Não opere · bloqueado · motivo · OM-0233' e abre a OM em consulta (MB-09 L6247, L6277).
- PAGR agrupa O.S. impedidas por 'Máquina ou equipamento' e abre as três juntas (v3out/PAGR.json → OS.dc.html#painel=OS-0420,OS-0431,OS-0507).
- Dentro do MA, abrir painel foca o painel, Esc fecha e o foco volta à linha (MA L5896 ma_abrir, ma_fechar, ma_trap).
- CD-03 mostra a condição técnica só para leitura ('Vem da Manutenção (condição única)') com link MA#ativo= (v3out/CD-03.json; CD-03 L5411).
- MA › Ativos tem 'Custo no mês' por máquina pela função única de custo (dumps/MA.txt g_at; MA manCustoPeriodo).

### Ideias das telas que saem

- CA-03det: tabela 'Registros ligados' (O.S., ativo, OM, substituto, com estado e efeito) e trilha do caso (quem, quando, efeito) → bloco Origem do painel da OM e do achado no MA.
- CA-03: triagem de ocorrências com gravidade, destino, dono e próxima ação → Meu dia › Ocorrências, incluindo os achados SM- para quem relatou acompanhar.
- CA-03det (motivo da decisão nas ocultas): 'Encerrar a ocorrência não libera o Trator T1: o desbloqueio vem só da OM-0233' → texto do MB-04 após registrar e do MB-09.
- PL-05det: comparar substituir × aguardar reparo × terceirizar (custo, risco, início) e 'Confirmar substituição pelo Trator 02', também para O.S. Em execução → painel da O.S. impedida.
- PL-05: impedimento com responsável, prazo e alternativa; 'Aplicar alternativa' no ⋯ da O.S. impedida.
- PL-03: tabela 'Manutenções e impacto na produção' (OM, janela, produção afetada, 'retorno previsto não confirmado até teste aprovado', Abrir) → seção do PMAN.
- MA-01 a MA-05: só redirecionam para MA; nada a aproveitar.

## Cadeia E · Da lavoura colhida ao produto vendido, entregue e recebido

Personas: Ana · Gestora e RT (agrônoma): publica previsão, programa colheita, aprova crédito, Sérgio · equipe de colheita (app): contagem e carga no campo, Lúcia · recebimento (balança da Lagoa Grande), Igor · responsável de produção (beneficiamento), Marta · qualidade (inspeção e decisão do lote), Dora · comercial (vendas, reservas), Rui · almoxarife e expedição (saída e entrega), Proprietário (resultado, crédito), Financeiro (sem persona no protótipo: cobrança e baixa)

### Etapas

| # | Etapa | Tela | Persona | Entidade | Estado | Como passa | Evidência |
|---|---|---|---|---|---|---|---|
| 1 | Contar frutos e publicar a previsão | COLH (contagem no MB-07) | Sérgio (contagem) e Ana (publica) | Previsão por cultivo e semana (vN) | Sem previsão → Prevista (v1, v2…) | link | COLH L3809 'Coletar contagem' → MB-07 só navega; v3out/COLH primária 'Publicar previsão do Pivô 19' |
| 2 | Programar a colheita (emitir O.S. de colheita) | COLH → OS | Ana | O.S. de colheita (OS-0505, OS-0510) | Prevista → O.S. A liberar / Liberada | link | COLH L3811 'Programar colheita' → OS.dc.html#nova:<cultivo>:<atividade>:<semana> (só preenche; Ana emite) |
| 3 | Registrar a carga no campo | MB-10 (aba Colheita) | equipe de colheita (app) | Carga CG- | — → A pesar (do app) | automático | v3out/MB-10 primária 'Registrar carga · OS-0505'; v3out/CARGA linha 'CG-2108 · do app A pesar · Pesar · Lúcia' |
| 4 | Pesar e receber a carga | CARGA | Lúcia | Carga CG- (ticket TK-) → lote L | A pesar → Recebida; lote Liberado, Em inspeção ou Em processo | automático | CARGA L3682 líquido = bruto − tara; L3699-3711 cria ou acrescenta o lote com origem (carga, O.S., talhão) e MP de recebimento |
| 5 | Beneficiar o lote (packing) | BEN | Igor; Rui/Paula (caixas); Marta (impedimento de qualidade) | Ordem de beneficiamento OB- | Lote Em processo · aguarda ordem → OB Encerrada; lotes de saída Em inspeção (INSP-) | link | v3out/CARGA links 'Abrir ordem de beneficiamento' → BEN.dc.html#nova=L38-132; BEN L5504-5505 'Lotes gerados' |
| 6 | Inspecionar e decidir o lote | PROD | Marta | Lote L + inspeção INSP- | Em inspeção → Liberado, Bloqueado ou Destinado | nada | PROD L5487-5496 'Registrar resultado' e 'Registrar decisão'; status da tela 'N em inspeção' (PROD L5440-5443) |
| 7 | Registrar venda, contrato, CPR ou barter | VEN (a partir do PCOM) | Dora | Venda PV- / CT- / CRE- / BT- | Oferta livre no período → Sem reserva / Futura: compromete a previsão / Saca a conferir | link | PCOM L5953 'Vender <produto> · <período>' → VEN.dc.html#nova:…; VEN L5937-5975 |
| 8 | Reservar lote apto para a venda | VEN (ou PROD) | Dora | Reserva RS- | Sem reserva → Parcial / Coberto | botão | VEN L6011-6012 'Reservar lote para o PV'; PROD L5475 'Reservar L… para pedido' |
| 9 | Aprovar crédito do cliente (quando passa do limite) | VEN | Ana (gestora) | Venda | Aguardando crédito → Aprovado até R$ … | botão | VEN L5901-5902 e L6009-6010 'Aprovar crédito do PV' |
| 10 | Programar a carga de saída | VEN → EXPED | Comercial ou expedição (Rui) | Carga de saída RM- | Reservado sem carga → Programada | link | VEN L6013 → EXPED.dc.html#nova:PV-…; EXPED L6026 abre 'Programar carga' com a venda herdada |
| 11 | Verificar e confirmar a saída (pesagem) | EXPED | Rui | RM- | Programada → Em trânsito (ou Entregue, se o cliente retira); título a receber nasce | botão | EXPED L5949-5954 'Verificação da saída (ao vivo)'; L5731-5732 saída recusada com lote impedido; L5756 valor a receber |
| 12 | Confirmar a entrega ou registrar devolução | EXPED | Rui | RM- (e lote de devolução) | Em trânsito → Entregue / Entregue com devolução (lote novo Em inspeção) | botão | EXPED L5781-5800 comEntregar; L5764-5778 devolução cria lote Em inspeção com origem |
| 13 | Cobrar e baixar o recebível | VEN / PCOM (GE-05 oculta, decisão do proprietário) | Financeiro | Título (RM- × venda) | A receber / vencido · cobrar → não existe 'Recebido' na cadeia visível | nada | PCOM L5937 'Recebimento e baixa são do Financeiro (fora desta etapa)'; VEN L5898 |
| 14 | Apurar produtividade e resultado por talhão e safra | COLH, IN-04, PAGR, GE-03 | Ana e proprietário | Talhão / cultivo / safra | Colhido e recebido → Produtividade × meta (sem custo por t nem margem) | automático | IN-04 L8077 'Produtividade · meta'; COLH L5443 'Custo R$/t: sem custo realizado · Controle' |
| 15 | Vincular garantias de crédito à produção (CPR, penhor) | GE-08 | Proprietário e Ana (gestora) | Solicitação de crédito CRE- | Contratado → Obrigação física no VEN (CRE-0095) sem ligação | nada | dumps/GE-08 CRE-0095 'CPR física · 6.900 sc' → VE-05.dc.html; VEN const CEN0 CRE-0095 obs '(GE-08)' só texto |

### Quebras

**E-1 · alta · sem aviso ao próximo** · CARGA/PROD (lote recebido Em processo) → VEN (venda sem lote) e BEN (ordem)
- Hoje: O mamão recebido fica 'Em processo · fora do vendável até a ordem de processo'. A PV-031 diz 'Falta 10.000 kg e nenhum lote apto… que não vença antes de 28/09' e a PV-036 'sem lote apto · aguardar colheita ou liberação', sem citar a OB-0110 em execução nem o L38-132 à espera de ordem. O BEN não mostra que há venda esperando.
- Impacto: Dora não sabe quem cobrar nem quando terá fruta; Igor prioriza ordens sem ver a demanda; a janela da PV-031 (28/09–04/10) corre sem dono.
- Proposta: Na venda sem lote apto, se houver lote do produto em processo ou ordem aberta da rota, o próximo passo vira 'Aguarda OB-0110 (Em execução) · Igor' com link BEN.dc.html#OB-0110 (ou #nova=L38-132). No painel da OB e em 'Criar ordem', seção 'Vendas esperando' (PV-031 · 10.000 kg · janela 28/09). (esforço M)
- Evidência: v5out/VEN PV-031 passo; v3out/VEN linha PV-036; v3out/PROD L38-132 'Em processo · Abrir ordem de beneficiamento · Igor'; VEN L5917; PROD L3499

**E-2 · alta · sem aviso ao próximo** · PROD (Qualidade bloqueia ou lote nasce em inspeção) → VEN/EXPED (Comercial) e PROD (Marta)
- Hoje: O bloqueio trava a saída, mas o único aviso é a mensagem para quem bloqueou ('o Comercial troca o lote ou cancela') e o estado 'Em risco'. Nada chega à fila de Dora. Lote gerado pela OB nasce Em inspeção com prazo e Marta só sabe abrindo o PROD. O Meu dia (IN-01), que vai virar atalho, não lê o cenário e mostra 'Decidir o lote L27-013' (legado).
- Impacto: Comercial descobre o risco quando a saída é recusada; Marta perde prazo de inspeção; o caminho 'Meu dia' leva a lote que não existe na base viva.
- Proposta: Evento gera item no Meu dia do dono: bloqueio ou reclassificação com reserva ativa → 'Trocar lote do PV-… · Dora' (link VEN#PV-…); lote gerado em inspeção → 'Registrar resultado INSP-… · Marta · prazo' (link PROD#lote). IN-01 passa a ler o cenário compartilhado. (esforço M)
- Evidência: PROD L4500 (msg do benDecidir); BEN L5505 (INSP · prazo · resp só texto); dumps/IN-01.txt f7 'Decidir o lote L27-013'; IN-01 sem const CEN0

**E-3 · alta · contexto perdido** · VEN (venda) → PROD/CARGA/COLH (origem do produto)
- Hoje: A venda mostra só o ID do lote (reservas e cargas de saída). Talhão, O.S. e carga só aparecem abrindo o lote no PROD, onde talhão e O.S. são texto (só a carga é link). Lote do beneficiamento exige mais um salto ('De onde veio'). Não há visão para frente talhão → lotes → clientes.
- Impacto: Numa reclamação ou recolhimento, Marta e o proprietário fazem 3 a 4 saltos e montam a cadeia de cabeça.
- Proposta: No painel da venda, seção 'Origem' resolvendo a genealogia (talhão · O.S. · carga · ordem de beneficiamento · lote) com links. No lote do PROD, seção 'Rastreabilidade' (árvore do CO-06) com 'Simular recolhimento' listando RM e clientes; O.S. clicável (OS.dc.html#OS-…). (esforço M)
- Evidência: VEN L5983-5986 (reservas e cargas só com o lote); PROD L5458 (x.tal, x.os em texto; link só CARGA#); v5out/CARGA refs OS-0505 clic 0

**E-4 · alta · estado não propaga** · Talhão T7 (Santa Rita) / colheita → PROD/BEN (lotes do packing)
- Hoje: Os lotes do packing L38-115..118 e L39-117..119 (entradas da OB-0110 e OB-0112) são saldo de abertura sem origem estruturada. O talhão está só em texto ('…(OC-0507 · S38)', 'CG-1205 do T7'), com IDs que não existem no CARGA. O PROD diz '(não entra na produção por talhão)'.
- Impacto: A classe A que atenderia a PV-031 não tem rastreio estruturado até talhão e carga; a produção do T7 não volta ao COLH nem à produtividade.
- Proposta: No cenário, registrar as cargas do T7 no CARGA (CG- com O.S. de colheita) e gerar esses lotes pelo recebimento; trocar OC-0507 e CG-1205 por IDs vivos; deixar 'abertura' só para saldo de fato anterior ao sistema. (esforço M)
- Evidência: PROD const CEN0 (L2351) lote L38-115 obs 'OC-0507 · S38', L39-117 obs 'CG-1205 do T7'; PROD L5459

**E-6 · alta · número diverge** · EXPED/VEN/PCOM (a receber) → GE-05 (Contas a receber)
- Hoje: O Comercial mostra Frutas Real com R$ 91.470,00 a receber (RM-0001/PV-037, vence 15/10). O GE-05 mostra Frutas Real R$ 28.200 (FAT-2112, viagem VG-117, vence 20/10) e títulos dos PV-027 e PV-029, que não existem no VEN. O GE-05 não lê o cenário.
- Impacto: Proprietário vê dois saldos para o mesmo cliente; cobrança sobre título que a venda não conhece.
- Proposta: Se o GE-05 ficar (decisão do proprietário), gerar os títulos pela mesma função do VEN/PCOM (comTitulos), um por RM, com links VEN#PV-… e EXPED#RM-…. Se sair, apagar os números estáticos e manter a venda como fonte única. (esforço M)
- Evidência: v3out/PCOM 'R$ 91.470,00'; v3out/EXPED 'R$ 91.470,00 a receber até 15/10'; dumps/GE-05.txt frr/f2112, atb/f2090 (PV-029), rhb (PV-027)

**E-8 · alta · beco sem saída** · EXPED (título nasce na saída) → Baixa do recebível e crédito do cliente
- Hoje: A venda e o Painel dizem 'Recebimento e baixa são do Financeiro (fora desta etapa)', sem botão. Não existe registro de recebimento na cadeia visível. A exposição de crédito soma todo o expedido do cliente e nunca baixa: Frutas Real tem limite R$ 120.000 e 'a receber R$ 91.470,00'; a saída da PV-031 (10.000 kg × R$ 3,05) passa do limite e pedirá a gestora mesmo com o PV-037 pago.
- Impacto: Ana aprova crédito à toa; Dora não sabe se o cliente pagou; a cobrança fica fora do sistema.
- Proposta: Na seção 'Financeiro · a receber' da venda, 'Registrar recebimento' (data, valor, comprovante, idempotente) ou leitura do ERP (CF-03) que baixa o título e a exposição; 'Enviar à cobrança' no vencido. Onde mora (GE-05 ou ERP) segue a decisão do proprietário. (esforço M)
- Evidência: VEN L5481-5484 (comExpo soma prExpedido, sem pagamento); VEN L5492; v5out/VEN PV-031 'limite R$ 120.000,00 … a receber R$ 91.470,00'; PCOM L5937

**E-10 · alta · estado não propaga** · COLH/CARGA (produção) e VEN (receita) → GE-03 (resultado por talhão e safra)
- Hoje: O painel do talhão no COLH mostra 'Custo R$/t: sem custo realizado · Controle' fixo. O GE-03 não lê colheita, carga nem venda (sem cenário) e só lista custos por O.S. Receita e margem só existem no GE-01 (oculto).
- Impacto: Proprietário não vê custo por tonelada nem margem por talhão ou safra.
- Proposta: GE-03 ganha a visão 'Resultado da safra' (do GE-01): por talhão, custo realizado ÷ produção recebida (COLH) e receita pelo preço médio realizado (VEN). O COLH preenche 'Custo R$/t' com link ao GE-03 filtrado no talhão. (esforço G)
- Evidência: COLH L5439 e L5443; dumps/GE-03.txt (g_lan só custos); GE-03 sem const CEN0; padrao/ocultas.json GE-01

**E-5 · média · passa por tela que será excluída** · PROD (avaliação do destino) e IN-04 (carência do talhão) → CO-06
- Hoje: No painel do lote, 'Ver carência e destino' abre CO-06.dc.html sem âncora. No Mapa, carência e lotes do talhão abrem CO-06 (4 links, alguns com #LC-…).
- Impacto: Quem segue o link cai em tela legada, em outra base (L27-013), sem o lote de origem.
- Proposta: Trocar por PROD.dc.html#<lote> abrindo a seção 'Avaliação do destino'; o PROD aceita âncora #LC-… e abre o lote que contém aquele lote de campo. (esforço P)
- Evidência: PROD L5464; IN-04 L7823, L7935, L7941, L7947; padrao/ocultas.json CO-06 'Links a trocar'

**E-7 · média · passa por tela que será excluída** · GE-05, GE-08, GE-03 → VE-04, VE-06, VE-05, LO-04
- Hoje: Todos os títulos do GE-05 apontam para VE-04 (pedido) e VE-06 (caso). O GE-08 'Ver CPR' abre VE-05. O GE-03 'Romaneio de frete' abre LO-04. O Voltar não reabre o detalhe de origem.
- Impacto: Financeiro e proprietário saem da base viva para telas que serão apagadas.
- Proposta: GE-05 → VEN.dc.html#PV-… e EXPED.dc.html#RM-…; GE-08 CRE-0095 → VEN.dc.html#CRE-0095 (já existe no VEN); GE-03 frete → EXPED.dc.html#RM-…. (esforço P)
- Evidência: v3out/GE-05 links (VE-04 ×6, VE-06 ×5); v3out/GE-08 'Ver CPR' → VE-05.dc.html; v3out/GE-03 'Romaneio de frete' → LO-04.dc.html; v5out/GE-05 detalheReaberto false

**E-9 · média · beco sem saída** · EXPED (saída) → Faturamento (NF-e)
- Hoje: A 'Verificação da saída' checa lote, carência, reserva e crédito, mas não a NF-e. O título nasce na saída sem número de nota. O GE-05 diz que o título 'nasce no faturamento'.
- Impacto: Carga sai sem nota registrada; título sem vínculo fiscal; regra diferente entre Comercial e Financeiro.
- Proposta: Item 'NF-e autorizada' na verificação (do LO-02det), com dono fiscal; o título carrega o nº da NF; sem NF, a saída fica impedida. (esforço M)
- Evidência: EXPED L5949-5954 (itens da verificação); EXPED L5471-5475 (título de rm.saida); dumps/GE-05.txt f2112 'título nasce no faturamento'

**E-11 · média · estado não propaga** · COLH (produtividade realizada) → PAGR (Painel) e CD-01det (talhão)
- Hoje: A produtividade realizada aparece no COLH e no Mapa, mas o Painel Agrícola mostra só 'Previsão publicada' e 'Recebido' (sem t/ha nem meta) e o detalhe do talhão no cadastro mostra só a meta.
- Impacto: Gestor no Painel não vê quem está abaixo da meta sem abrir talhão por talhão.
- Proposta: Coluna 'Produtividade · meta' no PAGR com a mesma conta do Mapa (prPrtvResTxt); no CD-01det, histórico de produtividade por safra. (esforço P)
- Evidência: v3out/PAGR colunas 'PREVISÃO PUBLICADA, RECEBIDO'; PAGR L5998-6000; IN-04 L8077; CD-01det GRIDS 'Meta de produtividade'

**E-12 · média · estado não propaga** · GE-08 (garantia penhor) → PROD/PCOM/VEN (soja disponível)
- Hoje: O CRE-0102 tem 'penhor de 30% da soja', mas PROD, PCOM e VEN não mostram nem descontam a soja empenhada; o L10-031 aparece com 34.545 sc disponíveis.
- Impacto: Dora pode reservar ou vender soja dada em garantia sem saber.
- Proposta: GE-08 grava a garantia como compromisso sobre produto e safra; o PCOM mostra 'em garantia' na oferta e o VEN avisa ao reservar acima do livre de garantia. (esforço M)
- Evidência: dumps/GE-08.txt CRE-0102 gar 'penhor de 30% da soja'; busca por 'penhor' sem resultado em VEN, PCOM e PROD; v5out/PCOM 'L10-031 … disponível 34.545 sc'

**E-13 · média · redigitação** · GE-08 (CPR e barter) → VEN (obrigação física)
- Hoje: A CPR CRE-0095 (6.900 sc) existe no GE-08 (estático) e no VEN (cenário), sem ligação: o GE-08 aponta VE-05 e o VEN diz '(GE-08)' só em texto. CPR nova no VEN não aparece no GE-08; crédito com garantia 'CPR + penhor de safra' no GE-08 não cria a obrigação no VEN.
- Impacto: A mesma CPR é digitada duas vezes e pode divergir em sacas e safra.
- Proposta: Uma fonte: o compromisso físico mora no VEN (natureza CPR/Barter); o GE-08 lê e linka VEN#CRE-…; contratar crédito com CPR no GE-08 cria o rascunho no VEN com credor, sacas e safra herdados. (esforço M)
- Evidência: dumps/GE-08.txt CRE-0095 e formulário 'Garantia' (CPR + penhor de safra); VEN const CEN0 CRE-0095 obs '(GE-08)'; VEN L5943 (Natureza CPR); VEN L5997

**E-14 · média · ação fora do lugar** · PCOM e IV (período em déficit) → COLH (publicar previsão)
- Hoje: O painel do déficit e o IV dizem 'publicar a previsão de S41 (Previsão e colheita · Produção)' e 'Publique a previsão (Colheita)' só em texto, sem link e sem aviso a Ana.
- Impacto: Dora vê o déficit de 40.000 kg e precisa achar a agrônoma fora do sistema.
- Proposta: Link 'Publicar previsão no COLH' → COLH.dc.html#<cultivo> (o COLH já abre o talhão pela âncora, L5481) e item no Meu dia de Ana. (esforço P)
- Evidência: PCOM L5927; IV L6087; v5out/IV detalhe 'Mamão … safra comercializada' primarias []

**E-15 · média · sem aviso ao próximo** · COLH (talhão sem previsão) → MB-07/MB-01 (equipe de colheita)
- Hoje: O próximo passo diz 'Contar os frutos de 20 plantas · equipe de colheita (app)', mas 'Coletar contagem' só navega ao MB-07; nenhuma tarefa chega à equipe.
- Impacto: 10 talhões de mamão seguem sem previsão; a oferta futura fica vazia e o PCOM mostra déficit.
- Proposta: 'Pedir contagem' cria tarefa na fila do app (MB-01) para o cultivo, com prazo; o COLH mostra 'pedida a Sérgio em dd/mm'. (esforço M)
- Evidência: COLH L3809; v3out/COLH grupo 'Mamão Formosa … 10 sem previsão'; v5out/PAGR passagem 'Coletar contagem → MB-07.dc.html#lg24 · não reabriu'

**E-16 · média · contexto perdido** · Painéis de CARGA, EXPED, BEN e COLH → OS, VEN, PROD, BEN
- Hoje: IDs de outras entidades aparecem como texto: no CARGA, OS-0505 e LC-0505; no EXPED, 'Venda PV-037' no painel (só a linha da lista tem link); no BEN, INSP-94, OB-0110 e PC-096; no COLH, o lote da carga.
- Impacto: Quem está no detalhe precisa fechar, ir ao menu e buscar o registro.
- Proposta: Tornar link todo ID vivo: OS → OS.dc.html#OS-…; PV → VEN#PV-…; INSP → PROD#<lote>; OB → BEN#OB-…; lote → PROD#<lote>. (esforço P)
- Evidência: v5out/CARGA refs OS-0505 e LC-0505 clic 0; v5out/EXPED refs PV-037 clic 0; v5out/BEN refs INSP-94, PC-096, OB-0110 clic 0; COLH L5433

**E-17 · média · sem volta à origem** · Qualquer painel da cadeia → Tela de destino e volta
- Hoje: Os links dos painéis são href simples. No destino só há 'Voltar para Agrícola/Comercial'. O Voltar do navegador não reabre o detalhe de origem (CARGA→PROD, EXPED→VEN, EXPED→PROD, BEN→PROD, PCOM→PROD), porque abrir um registro não grava a âncora. Exceção boa: PROD mostra 'Abrir a OB-0110' quando veio do BEN.
- Impacto: Quem confere carga, lote e venda em sequência perde o registro de partida a cada salto.
- Proposta: g2pick grava #ID no endereço (history.replaceState); o destino mostra '‹ Voltar para CG-2103' usando a ficha g2volta que o motor já tem (CARGA L1460). (esforço M)
- Evidência: v5out/CARGA, EXPED, BEN, PCOM 'voltar.detalheReaberto: false'; CARGA L5374 (g2pick só muda estado); v5out/BEN PROD#L38-115 voltaOrigem true

**E-18 · média · acessibilidade** · Link de passagem → Painel aberto no destino
- Hoje: Ao chegar por link, o painel do registro abre, mas o foco fica no corpo da página (PROD#L38-132, VEN#PV-037) ou no botão '×' (BEN#nova=L38-132), e nada é destacado.
- Impacto: Usuário de teclado ou leitor de tela não sabe qual registro abriu nem onde está.
- Proposta: Ao abrir pelo hash, levar o foco ao título do painel (tabindex -1), anunciar 'Lote L38-132 aberto · Em processo' em aria-live e realçar a linha. (esforço P)
- Evidência: v5out/CARGA passagem PROD#L38-132 foco '' destacou false; v5out/CARGA BEN#nova=L38-132 foco '×'; v5out/IV VEN#PV-037 foco ''

**E-20 · média · contexto perdido** · OS (O.S. de colheita) → CARGA/PROD (cargas e lotes que ela gerou)
- Hoje: O painel da O.S. de colheita não lista suas cargas nem o kg recebido; usa as cargas só para recusar cancelamento e para o selo 'Encerrar bloqueado: Carga a pesar' (com link CARGA#CG). A produção da O.S. só aparece no COLH.
- Impacto: Ana e Caio acompanham a O.S. sem ver quanto já foi colhido e recebido; para conferir, trocam de tela.
- Proposta: Seção 'Cargas e produção' no painel da O.S. de colheita: CG- (link CARGA#), kg líquido, lote (link PROD#), produtividade do passe; reaproveita prResultado do COLH. (esforço P)
- Evidência: OS L5421-5427 (osCargasVivas só no cancelamento); OS L5214 (selo de encerramento → CARGA#CG); COLH L5431 (passes por O.S. só no COLH)

**E-19 · baixa · passa por tela que será excluída** · VEN e PCOM (venda em saca a conferir) → VE-05 (citada no texto)
- Hoje: O painel da venda mostra 'Unidade do contrato: a conferir · VE-05 (oculto): "Soja 26/27 · sc 50 kg"…' e o PCOM 'VE-05 oculto diz sc 50 kg'.
- Impacto: Dora é mandada a conferir numa tela que não acha no menu e será apagada.
- Proposta: Citar a fonte de negócio (contrato e cláusula) e não a tela legada. (esforço P)
- Evidência: v5out/VEN rótulo 'Unidade do contrato'; PCOM L5921

### Já funciona

- Peso líquido chega ao lote sem redigitar: o recebimento calcula bruto − tara, cria ou acrescenta o lote com origem (carga, O.S., talhão, dia) e grava o MP de recebimento (CARGA L3682, L3699-3711).
- Carga do app vira fila da balança: nasce 'A pesar' com a O.S.; a pesagem herda a origem e o formulário sugere pesar a carga do app; a O.S. não encerra com carga a pesar e linka CARGA#CG (CARGA L5413-5414, L5456; OS L5214).
- COLH liga previsão, O.S. e cargas: 'Programar colheita' abre OS.dc.html#nova:… com cultivo, atividade e semana herdados; passes linkam 'Abrir OS-…' e cargas 'Ver carga' (COLH L3811, L5431, L5433).
- Produtividade realizada volta ao talhão no Mapa ('Produtividade · meta' e link COLH#cultivo) e o Painel abre o cultivo no COLH (IN-04 L8077, L8084; PAGR L6000; COLH L5481).
- Previsão publicada alimenta a oferta livre do Painel comercial e o formulário de venda por semana, sem redigitar (PCOM L5924; VEN L5956).
- Lote recebido abre a ordem de beneficiamento já com o lote (BEN.dc.html#nova=L…), e o BEN avisa 'N lotes a beneficiar' no status (v3out/CARGA links; PROD L4093; BEN L5579).
- Genealogia do beneficiamento: entradas e lotes gerados linkam PROD#lote; o lote mostra 'De onde veio' e 'Para onde foi'; ao vir do BEN, o PROD oferece 'Abrir a OB-0110' (BEN L5491, L5505; PROD L5457, L5480; v5out/BEN voltaOrigem true).
- Lote não liberado impede a expedição no servidor: verificação ao vivo, recusa com dono ('Saída recusada… Nada foi alterado'), venda 'Em risco' e reserva 'Expedição impedida' (EXPED L5523, L5731-5732; PROD L3557, L5461).
- Venda → expedição sem perder contexto: 'Programar carga do PV' abre EXPED#nova:PV com a venda e o previsto; depois o endereço vira #RM (VEN L6013; EXPED L5939, L5943, L6026).
- Saída e entrega geram o a receber com vencimento pela condição, e VEN, EXPED e PCOM leem a mesma função (EXPED L5471-5476, L5756; PCOM L5914-5916).
- Devolução volta como lote novo Em inspeção, com origem e link à RM, sem recontar a produção do talhão; o a receber cai (EXPED L5764-5778; PROD L5460).
- Idempotência nas passagens: chave na pesagem, na reserva e na saída; repetir não soma de novo (CARGA L3671; EXPED L5718).
- Link antigo PROD#PV-… redireciona para VEN#PV-… (PROD L5503).

### Ideias das telas que saem

- CO-06: árvore do lote (talhão e O.S. → carga → beneficiamento → lote → cargas e clientes) e 'Simular recolhimento' mesmo com saldo zero → PROD, painel do lote, seção 'Rastreabilidade' (resolve E-3).
- CO-06det: tabela 'Tentativas recusadas' (reserva do PV-028 e programação de doca recusadas pelo bloqueio) mostra quem foi atingido → base para o aviso ao Comercial no bloqueio (E-2); e 'padrão × medido por critério' no 'Registrar resultado' do PROD.
- LO-02det: checklist antes da saída com NF-e autorizada, lacre com foto, conferência do lote por leitura e ticket da balança integrada; 'Baixa de estoque na saída · uma única vez · automática' → EXPED 'Verificação da saída' (E-9).
- VE-04det: seção 'Atendimento · origem do pedido' com genealogia (L38-115..118 → OB-0110 → L39-120 → PV-031) e quantidade 'sem origem' sinalizada ('não se promete classe A pelo peso bruto a colher'); 'Evento financeiro' da entrega com valor e vencimento → VEN painel da venda (E-1, E-3). A 'reserva provisória' de lote em inspeção (RT-0107) só com decisão, pois hoje a regra é reservar só lote apto.
- CO-05det: entrada da ordem mostra a origem da fruta ('origem OC-0507 · T7 (S38)') → BEN, seção 'Entradas', com talhão e O.S. de cada lote (E-4).
- CO-02det: 'Cargas do dia' na ordem de colheita com vínculo 'Conciliada / Aguardando recebimento' → painel da O.S. de colheita (E-20).
- GE-01: resultado por cultura (receita prevista, margem, custo unitário) → GE-03 visão 'Resultado da safra' (E-10).
- VE-06: evidência (foto ou laudo do cliente) na devolução → EXPED 'Registrar devolução'.

## Passagens com problema (robô v5)

| De | Clique | Chegou em | Chegou no registro | Volta à origem | Voltar reabre |
|---|---|---|---|---|---|
| AG-01 | Abrir OS-0504 | OS#OS-0504 | sim | não | — |
| AG-01 | Abrir OS-0508 | OS#OS-0508 | sim | não | — |
| AG-01 (detalhe) | Ver rota e evidências › | AG-01det#VIS-055 | sim | sim | não |
| AG-01 (detalhe) | Ver rota e evidências › | AG-01det#VIS-058 | sim | sim | não |
| AG-04 | Ver demanda gerada | PL-02 | — | não | — |
| AG-04 | DIA-007 | AG-03det | sim | não | — |
| AG-04det | Ficha da abamectina 500 FS › | AG-07#abamectina-500-fs | não | não | — |
| AG-04det | Pasteuria nishizawae FS (registrada para cisto) › | AG-07#pasteuria-nishizawae-fs | não | não | — |
| AG-04det | NEC-028 | PL-02 | não | não | — |
| AG-04det | OS-0420 | OS#OS-0420 | sim | não | — |
| AG-04det (detalhe) | LAU-2043 · zona 2 · K 0,08 cmolc/dm³ › | AG-02 | não | não | não |
| AG-04det (detalhe) | Abastecimento · 84 L × R$ 5,92 › | MA#vis=ativos&modo=abastecimentos | não | não | não |
| AG-07 (detalhe) | Abrir no Estoque › | EST | não | não | não |
| AG-07 (detalhe) | REC-014 v2 › | AG-04det | sim | não | não |
| BEN (detalhe) | Conferir a NF 7731 das caixas no Estoque › | EST | não | não | não |
| BEN (detalhe) | Ver no Estoque de produto › | PROD#L39-117 | sim | sim | não |
| BEN (detalhe) | Ver no Estoque de produto › | PROD#L39-118 | sim | sim | não |
| BEN (detalhe) | Ver no Estoque de produto › | PROD#L39-119 | sim | não | não |
| BEN (detalhe) | Ver no Estoque de produto › | PROD#L38-115 | sim | sim | não |
| BEN (detalhe) | Ver no Estoque de produto › | PROD#L38-116 | sim | sim | não |
| BEN (detalhe) | Ver no Estoque de produto › | PROD#L38-118 | sim | sim | não |
| BEN (detalhe) | Abrir no Estoque › | EST | não | não | não |
| CA-02 | OS-0421 · v2 | CA-01det | sim | não | — |
| CA-02 | Ver histórico › | CA-01det | — | não | — |
| CA-02 | Ver custódia › | CA-04 | — | não | — |
| CA-03 | Encaminhar à agronomia › | AG-03 | — | não | — |
| CA-03 | Reprogramar saldo › | PL-05 | — | não | — |
| CA-03det | OS-0420 | CA-01x-os0420 | sim | não | — |
| CA-03det | Trator T1 | MA#ativo=a01 | não | não | — |
| CA-03det | OM-0233 | MA#vis=ordens&om=OM-0233 | sim | não | — |
| CA-03det | Trator 02 · MF 7719 | PL-05 | — | não | — |
| CARGA | Abrir ordem de beneficiamento · Igor (responsável de produção) | BEN#nova=L39-132 | sim | não | — |
| CARGA | Abrir ordem de beneficiamento · Igor (responsável de produção) | BEN#nova=L38-132 | sim | não | — |
| CARGA (detalhe) | Abrir no estoque › | PROD#L38-132 | sim | não | não |
| CD-01 (detalhe) | Documentos para crédito › | GE-08#vis=documentos | não | não | não |
| CD-01 (detalhe) | Abrir talhão › | CD-01det#talhao=PV06 | sim | sim | não |
| CD-01det | Planejar T1 na safra › | SAF | — | não | — |
| CD-01det (detalhe) | Planejar safra › Safra 2026/27 › T1-B › | SAF | não | não | não |
| CD-03 (detalhe) | Ver ordens afetadas · OS-0420 e OS-0431 › | OS | não | não | não |
| CD-03 (detalhe) | Abrir OM-0233 na Manutenção › | MA#vis=ordens&om=OM-0233 | sim | não | não |
| CD-03 (detalhe) | Abrir Trator T1 na Manutenção › | MA#ativo=a01 | não | não | não |
| CD-03 (detalhe) | Abrir Colhedora Axial-Flow 7250 na Manutenção › | MA#ativo=a08 | não | não | não |
| CD-03 (detalhe) | Abrir Silo 01 na Manutenção › | MA#ativo=a14 | não | não | não |
| CD-04 (detalhe) | Acesso ao app: Ativo desde 28/06/2026 · gerenciar em Configurações › Usuários e alçadas › | CF-01#pessoa=Ana | sim | não | não |
| CD-04 (detalhe) | Acesso ao app: Ativo desde 01/07/2026 · gerenciar em Configurações › Usuários e alçadas › | CF-01#pessoa=Jo%C3%A3o | sim | não | não |
| CD-04 (detalhe) | Acesso ao app: Ativo desde 01/07/2026 · gerenciar em Configurações › Usuários e alçadas › | CF-01#pessoa=Dora | sim | não | não |
| CF-01 (detalhe) | Abrir no cadastro | CD-04 | não | não | não |
| CF-04 | Fatura ago/2026 | CF-05 | — | não | — |
| CF-04 | Contrato v2 | CF-05 | — | não | — |
| CF-04 (detalhe) | Abrir no domínio | CF-05 | não | não | não |
| CF-04 (detalhe) | Abrir no domínio | CF-01#pessoa=Rui | sim | não | não |
| CF-05 (detalhe) | Abrir no cadastro › | CD-01det#talhao=PV07 | sim | não | não |
| CMP | Ver origem | SAF#saf=S2627&passo=demanda | sim | não | — |
| CMP | Abrir Planejar safra | SAF#saf=S27SF&passo=demanda | sim | não | — |
| CMP | Abrir Planejar safra | SAF#saf=LG2627&passo=demanda | sim | não | — |
| CO-06 | Ver carência no mapa | IN-04 | — | não | — |
| EXPED | PV-037 | VEN#PV-037 | sim | não | — |
| EXPED (detalhe) | Abrir lote › | PROD#L38-131 | sim | não | não |
| GE-01 | Comparar cenário | GE-02 | — | não | — |
| GE-01 | Abrir origem do desvio | GE-02det | — | não | — |
| GE-01 | Criar ação | GE-07 | — | não | — |
| GE-01 | Abrir lote | CO-06det | — | não | — |
| GE-01 (detalhe) | Custo = R$ 5,84 mi da previsão V2 · composição documento a documento › | GE-03 | não | não | não |
| GE-01 (detalhe) | Premissas da versão V2 (rendimento e preço) › | GE-02 | não | não | não |
| GE-01 (detalhe) | L27-013 · INSP-88 aberta · Qualidade · prazo 25/09 › | CO-06det | sim | não | não |
| GE-01 (detalhe) | CT-198 e PV-028 dependem do lote › | VE-05 | não | não | não |
| GE-02det (detalhe) | Indicador de custo de pulverização › | GE-06det | não | não | não |
| GE-03 | NF 8842 · recebimento | SU-06 | — | não | — |
| GE-03 | REQ-035 · OS-0421 | SU-07 | não | não | — |
| GE-03 | Apontamento · OS-0421 | CA-02 | não | não | — |
| GE-03 | REQ-036 · OS-0420 | SU-07 | não | não | — |
| GE-03 (detalhe) | NF 8842 · recebimento · Defensivo · fungicida › | SU-06 | não | não | não |
| GE-03 (detalhe) | Apontamento · OS-0420 · Máquina e equipe · plantio › | CA-02 | não | sim | não |
| GE-03 (detalhe) | Ordem OS-0420 · plantio T4 · 30 de 100 ha › | CA-01 | não | sim | não |
| GE-04 | Abrir aprovação | IN-02 | — | não | — |
| GE-04 | Abrir pedido | IN-02 | — | não | — |
| GE-04 | Abrir crédito | GE-08 | — | não | — |
| GE-04 (detalhe) | NF 8790 · parcela 2 de 3 · alçada do Gerente da fazenda (até R$ 300 mil) › | IN-02 | não | não | não |
| GE-05 (detalhe) | Pedido PV-027 · entrega 2 de 2 em 20/09 · o pedido original não muda › | VE-04 | não | não | não |
| GE-05 (detalhe) | Caso RC-12 · retorno de 300 kg do lote L26-118 recebido bloqueado · crédito de 300 kg × R$ | VE-06 | não | não | não |
| GE-06 | Ver ordens | CA-01 | — | não | — |
| GE-06 | Ver packing | CO-05 | — | não | — |
| GE-06 (detalhe) | R$ 5.808 ÷ 120 ha·op (OS-0409) › | GE-06det | não | sim | não |
| GE-06 (detalhe) | Pivô 2 a 62% da volta · 10,81 mm aplicados › | IR-03 | não | não | não |
| GE-06 (detalhe) | Telemetria do pivô › | IR-01 | não | não | não |
| GE-08 | Ver CPR | VE-05 | — | não | — |
| GE-08 (detalhe) | Liberado R$ 300 mil de R$ 850 mil · 1ª parcela é título em Contas a pagar › | GE-04 | não | não | não |
| IC (detalhe) | Abrir Compra de insumos | CMP | não | não | não |
| IN-01 | Liberar | OS#OS-0430 | sim | não | — |
| IN-01 | Receber devolução | EST | — | não | — |
| IN-02 | Decidir | SU-09 | — | não | — |
| IN-02 | Decidir | SU-02 | — | não | — |
| IN-02 | Decidir | GE-02det | — | não | — |
| IN-02 | Decidir | CF-01 | — | não | — |
| IN-02 (detalhe) | Abrir a decisão no módulo de origem › | GE-02det | não | não | não |
| IN-02 (detalhe) | Abrir a decisão no módulo de origem › | CF-01 | não | não | não |
| IV (detalhe) | Abrir venda › | VEN#PV-037 | sim | não | não |
| MB-02 | Ver envios | MB-03x-recibo | — | não | — |
| MB-02 | Registrar ocorrência | MB-04 | — | não | — |
| MB-02det | Ver envios | MB-03x-recibo | — | não | — |
| MB-02det | Ver retirada | MB-05 | — | não | — |
| MB-03 | Abrir ordem | MB-02det | — | não | — |
| MB-03 | Retirar no almoxarifado | MB-05#OS-0424 | sim | não | — |
| MB-03x-recibo | Voltar à fila | MB-01 | — | não | — |
| MB-05 | Ver envios | MB-03x-recibo | — | não | — |
| MB-05 | Voltar à fila | MB-01 | — | não | — |
| MB-07 | Ver envios | MB-03x-recibo | — | não | — |
| MB-07 | Voltar a Hoje no campo | MB-01 | — | não | — |
| MB-08x-recibo | Voltar à fila do turno | MB-01 | — | não | — |
| MB-09det | Ver envios | MB-03x-recibo | — | não | — |
| MB-09det | Abrir Trator T1 › | MB-09#ativo=a01 | não | não | — |
| MB-10 | Ver envios | MB-03x-recibo | — | não | — |
| PAGR | Abrir 3 O.S. por causa: Máquina ou equipamento | OS#painel=OS-0420,OS-0431,OS-0507 | sim | não | — |
| PAGR | Abrir 2 O.S. por quem resolve: Manutenção | OS#painel=OS-0420,OS-0507 | sim | não | — |
| PAGR | Abrir 2 O.S. por quem resolve: Suprimentos | OS#painel=OS-0418,OS-0502 | sim | não | — |
| PCOM (detalhe) | Abrir lote › | PROD#L10-031 | sim | não | não |
| PCOM (detalhe) | Registrar a saca do PV-030 | VEN#PV-030 | sim | não | não |
| PCOM (detalhe) | Abrir venda › | VEN#CT-203 | sim | não | não |
| PL-04 | Abrir O.S. | OS | — | não | — |
| PL-04 | Resolver impedimento | PL-05det | — | não | — |
| PL-04 | Abrir na Irrigação | IR-03det | — | não | — |
| PL-04 | Abrir O.S. | OS#OS-0418 | sim | não | — |
| PT-01 | Abrir proposta | PT-02det | — | não | — |
| PT-01 | Abrir negócio | PT-05det | — | não | — |
| PT-01 | Responder esclarecimento | PT-02det | — | não | — |
| PT-01 (detalhe) | Abrir a proposta › | PT-02det | não | não | não |
| PT-02 (detalhe) | Abrir a proposta › | PT-02det | não | sim | não |
| PT-04 (detalhe) | Abrir o dossiê › | PT-04det | não | sim | não |
| PT-05 | Abrir proposta | PT-02det | — | não | — |
| PT-05 (detalhe) | Abrir o negócio › | PT-05det | não | sim | não |
| SU-01 | Ver contrato | SU-05det | — | não | — |
| SU-01 | Em cotação | CMP | — | não | — |
| SU-01 | Ver contrato | SU-05 | — | não | — |
| SU-02 | Ver efeito em Necessidades › | SU-01 | — | não | — |
| SU-05 | Receber › | SU-06 | — | não | — |
| SU-06 (detalhe) | Título encaminhado a Contas a pagar › | GE-04 | não | não | não |
| SU-06 (detalhe) | Ver o pedido › | SU-05 | não | não | não |
| SU-08 | Devolver › | SU-07 | — | não | — |
