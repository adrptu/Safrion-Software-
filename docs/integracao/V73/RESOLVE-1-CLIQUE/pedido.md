<!-- Origem: pedido do proprietário (Adrianus), arquivo "prompt-safrion-resolve-em-1-clique.md" recebido no canal do Claude em 16/10/2026. Cópia verbatim abaixo deste comentário, sem alteração. SHA-256 do original: 0fa8d02701ee9a2266d1d3b2d1d6cfb83dd0fe11032b512bab12b1007fc01a2b -->

PROJETO: Safrion (Do Talhão à O.S.)
PEDIDO: Resolver em 1 clique — falta de insumo, peça ou material vira ação imediata, enviada direto ao processo e à pessoa que resolve

CONTEXTO
- Pedido do proprietário: na ordem de serviço, o agrônomo e o almoxarife precisam de um check rápido da demanda de cada insumo contra o estoque disponível. Com isso, o agrônomo age na hora: troca o produto ou pede compra de emergência em 1 clique.
- O mesmo vale para a manutenção preventiva e a troca de peças: ver se há estoque; se houver, já faz a requisição; se não houver, pede ao Compras em 1 clique.
- E também para o packing house e a agroindústria (embalagens, materiais de linha, insumos de pós-colheita).
- Em Suprimentos, também é preciso pedir compra de insumos avulsos, fora do plano agronômico, para atacar os problemas inesperados que sempre surgem na fazenda.
- Filosofia, que vale para o sistema inteiro: todo problema se resolve em 1 clique e vai direto para o processo e a pessoa que resolvem a dor, de forma imediata, com o contexto junto.

REFERÊNCIAS
- Protótipo: https://claude.ai/artifact/HqspGRcrX1wcayCVMe9emm (versão 1792184197-5a81). É privado: o Claude lê com a ferramenta Artifact (action "read"). O Codex lê pela cópia do protocolo, se houver.
- Telas a estudar: OS, OS-0424-app, OS-0424-ficha, PL-04, CA-01, CA-04, AG-04 e AG-04det, SU-01 a SU-09 e seus det, CMP, MA (Sem ordem, Ordens, Ativos, Planos), PMAN, MB-*, CO-05, CO-06, CO-07, BEN, EST, PROD, CD-06.
- A seção "O QUE JÁ EXISTE" resume a leitura do código do protótipo; o detalhe está no anexo-insumos-analise.md. Confirme cada item no código vigente antes de usar.
- Modelo a seguir: a ordem de manutenção (MA) já resolve a falta de peça em 1 clique, sem duplicar e com a peça reservada para a OM que pediu. Generalize esse padrão para a O.S. agrícola e para o packing, em vez de criar outro.

ORDEM DE TRABALHO: PRIMEIRO MELHORAR, DEPOIS IMPLANTAR
1. Claude e Codex, cada um sozinho, criticam este desenho contra o PRD, o NAV/DS, as decisões fixas e o que já existe no protótipo. Cada um lista o que adotar, adaptar ou descartar e o que falta.
2. Divergência se resolve por fonte ou reprodução. O Gemini real entra só em decisão material de domínio, como receituário na compra de defensivo, alçada de compra urgente ou troca de produto com carência. Pacote mínimo, sem dados reais.
3. O Codex registra o desenho final e as fatias no checkpoint (só ele edita o checkpoint).
4. Implantação na fase registrada no STATUS: primeiro no protótipo; depois na aplicação Next, por fatias tela → domínio → banco, com revisão cruzada (quem revisa integra o PR do outro).
Não simule o Codex nem o Gemini.

1. O PADRÃO ÚNICO: DISPONIBILIDADE NA LINHA DO MATERIAL
Vale para todo documento que consome material: O.S. agrícola (insumos), ordem de manutenção e preventiva (peças e lubrificantes), ordem de beneficiamento e de packing (embalagens, etiquetas, cera, fungicida pós-colheita, paletes).
Em cada linha de material, sem abrir outra tela (o lote é escolhido na fazenda do documento; estoque de outra fazenda só por transferência explícita, nunca por reserva silenciosa, como hoje na OS-0501; reserva pode dividir entre lotes e a liberação pode ser parcial quando o RT aceitar):
- necessário: calculado pelo documento (dose × área, quantidade da lista de peças, caixas por tonelada), nunca digitado;
- reservado para este documento;
- disponível no depósito da fazenda, já descontadas as reservas de outros documentos;
- em outro depósito ou fazenda da mesma empresa, transferível;
- a caminho: pedido com previsão de entrega, comparada com a data do documento;
- falta: necessário − (reservado + disponível + a caminho a tempo).
Estado da linha em texto e cor do design system:
- Coberto;
- Coberto com transferência;
- Coberto por pedido a caminho, chega em dd/mm (atenção se chega depois da data);
- Falta 120 L.
Um resumo no topo do documento: "3 de 4 itens cobertos · falta 120 L de Abamectina". O check fica igual no detalhe da O.S., na liberação, no app do líder e na tela do almoxarife (fonte única de cálculo, como o EX-38).

2. A AÇÃO DE 1 CLIQUE PARA CADA CASO
Cada estado da linha tem uma ação primária, que já vai pronta para quem resolve:
- Disponível e não reservado → "Reservar". Na liberação a reserva é automática, com recibo.
- Disponível em outro depósito → "Pedir transferência", que cai na fila do almoxarife de origem.
- A caminho, mas chega depois da data → "Antecipar entrega" (fila do comprador) ou "Reprogramar a O.S." (quem programa).
- Falta → "Pedir compra urgente". A solicitação nasce preenchida:
  - item, quantidade (a falta, arredondada à embalagem de compra) e unidade;
  - data necessária (a data do documento) e local de entrega;
  - origem e vínculo (O.S., OM ou ordem de beneficiamento; vistoria ou ocorrência que causou);
  - prioridade urgente e justificativa automática, por exemplo "OS-0424 · T4 · falta 120 L para 23/09".
  A solicitação vai para a fila do comprador, com a alçada vigente. Quem pediu acompanha no próprio documento: Solicitado → Em cotação → Pedido → A caminho → Recebido. Ao receber, a quantidade fica reservada para o documento que pediu (decisão fixa: a peça é reservada para a ordem que pediu).
- Insumo agronômico com falta ou vencendo → "Trocar produto", só para o agrônomo. Mostra as alternativas com estoque, já filtradas por:
  - registro para a cultura e o alvo (Agrofit) e dose de bula;
  - carência compatível com a colheita prevista do talhão e reentrada compatível com a operação;
  - grupo IRAC, FRAC ou HRAC, com alerta se repete o grupo das últimas aplicações do talhão (tabela de grupos por ingrediente, versionada, porque o Agrofit não traz esse dado);
  - eficácia medida na fazenda, quando o Raio-X do alvo tiver (EX-43);
  - custo por hectare.
  O clique troca o produto na O.S. como nova versão, refaz dose, total, calda e receituário, e mantém a aprovação agronômica individual.
  Reaproveitar a lista da decisão MIP do AG-01, que já mostra os produtos registrados para cultura × alvo com os selos "Sem estoque", "Rotação" e "Carência".
- Peça de manutenção:
  - com estoque → "Requisitar ao almoxarifado": o almoxarife separa e o mecânico retira com recibo, ligado à OM;
  - sem estoque → "Pedir compra", com prioridade pela criticidade do ativo e "máquina parada" desde dd/mm, com custo por dia parado quando houver;
  - na preventiva, a previsão de peças nasce com antecedência igual ao prazo de entrega: a automação gera o rascunho da solicitação N dias antes do vencimento (P34: automação gera rascunho, não executa).
- Packing house e agroindústria: a ordem de beneficiamento ou de embalagem mostra embalagens e materiais por turno, com o mesmo check. A falta vira requisição ou compra em 1 clique, e o estoque mínimo gera rascunho de reposição.

3. COMPRA AVULSA, FORA DO PLANO
- Entrada em Suprimentos e também no lugar onde o problema aparece: vistoria, ocorrência, O.S., OM, ordem de beneficiamento. Um só formulário, com 4 a 6 campos visíveis:
  - item, com busca no catálogo e "criar item" no próprio campo;
  - quantidade e unidade;
  - data necessária, com atalhos (hoje, amanhã, +7);
  - local de entrega;
  - motivo, em opções: praga ou doença inesperada, quebra de máquina, perda ou avaria, clima, outro;
  - vínculo (já preenchido quando nasce de vistoria, ocorrência ou ordem).
- O sistema mostra o impacto antes de enviar: "fora do plano e do orçamento: +R$ 4.800 na safra 2026/27 · T4". A rotulagem "fora do plano" segue para a alçada certa e para o planejado × realizado, sem esconder o desvio.
- Defensivo exige receituário vinculado antes da compra (confirmar a regra com o RT). Sem receituário, o botão diz o que falta e leva para emitir.
- Duplicidade: se já existe solicitação aberta para o mesmo item e destino, o sistema mostra e oferece somar a ela. A compra avulsa entra na demanda da safra, para o Planejar safra não comprar o mesmo item de novo.
- Hoje a requisição avulsa é vedada a insumo agrícola ("Nunca safra ou cultura", CMP). A regra muda para: permitida, marcada como fora do plano, com receituário quando for defensivo.

4. PARA ONDE VAI E QUEM RESOLVE
- A falta tem dono real: o papel Compras (hoje a O.S. aponta "Suprimentos", que não existe no catálogo de papéis).
- Cada ação cai na fila de quem resolve, em "Meu dia" ou "Aprovações", com contexto e uma ação primária: almoxarife (reservar, separar, transferir), comprador (cotar, pedir, antecipar), aprovador (aprovar dentro da alçada), agrônomo (trocar produto, emitir receituário).
- Quem pediu não precisa perguntar: o estado aparece no documento de origem, e a notificação só chega quando exige ação ("Chegou: 120 L reservados para a OS-0424").
- Urgente não pula alçada. Fica mais rápido: aprovação em 1 clique no celular, com o motivo e o impacto na tela.

5. REGRAS QUE NÃO PODEM QUEBRAR
- O servidor é a autoridade de saldo e de reserva; a reserva é atômica e idempotente.
- Estoque reservado para outro documento não é usado sem "Remanejar", feito por quem tem permissão, com o impacto no outro documento mostrado e registrado.
- Segregação: quem pede não aprova a própria compra, e quem tinha a custódia não confirma o próprio recebimento.
- Rastreabilidade de ponta a ponta: origem → solicitação → pedido → recebimento → reserva → consumo → custo.
- Unidade de compra × unidade de uso convertidas no domínio (galão de 20 L, saco de 25 kg, caixa com 12).
- Nenhuma compra é emitida sozinha: a automação gera rascunho, e a pessoa confirma.

6. ACEITE OBSERVÁVEL
- Na O.S. com falta, o agrônomo vê a falta sem abrir outra tela e resolve em 1 clique: troca o produto (com as checagens do item 2) ou pede compra urgente já preenchida.
- O almoxarife vê, por O.S., o que separar e o que falta, e reserva ou transfere em 1 clique.
- Na OM, peça com estoque vira requisição em 1 clique e peça sem estoque vira solicitação de compra em 1 clique, com a OM vinculada.
- No packing, falta de embalagem da ordem do turno vira requisição ou compra em 1 clique.
- A compra avulsa fora do plano sai em até 6 campos visíveis, com impacto no orçamento e alçada.
- Quem pediu acompanha o estado no documento de origem, e o recebido fica reservado para ele.
- Testes de regressão: reserva concorrente (duas O.S. pelo mesmo saldo), solicitação duplicada, remanejamento sem permissão, compra de defensivo sem receituário, troca de produto com carência incompatível.
- Medidas: tempo da falta detectada até resolvida; % de O.S. liberadas sem falta; compras urgentes por mês (devem cair com a previsão); cliques por resolução (meta: 1 para pedir, 1 para aprovar).

7. O QUE JÁ EXISTE NO PROTÓTIPO (evidência)
Leitura do código da versão 1792184197-5a81. O relatório completo, com linhas de código e 21 melhorias (12 para O.S. e compras, 5 para manutenção, 4 para packing), está no arquivo anexo-insumos-analise.md, que o proprietário anexa. Confirme no código vigente.
- Ressalva: SU-01 a SU-09, CA-04, PL-04, PL-05, IN-01 e IN-02 são grades estáticas, fora do motor do cenário, e divergem dele (ex.: SU-03 mostra o lote N26-03 com "reservado 0"; o cenário tem 8.000 kg reservados). O comportamento real está em OS, EST, CMP, MA, BEN, SAF, AG-01, AG-07 e MB-*. Ligar essas telas ao cenário entra junto com o EX-01.
- O.S.:
  - A seção Insumos mostra produto, dose, na ordem, usado e situação. Não mostra disponível, reservado por outras O.S., validade, local, pedido a caminho nem estoque de outra fazenda.
  - A liberação confere o estoque numa cópia do cenário e usa um único lote por insumo, o de maior saldo, sem filtrar a fazenda e sem parcial.
  - Quando falta: selo "Falta insumo", dono "Suprimentos" e a orientação "receber o insumo no Estoque". "Suprimentos" não é papel do catálogo, e não há botão de compra nem de transferência.
  - Casos no cenário: OS-0418 sem nenhum lote de ureia; OS-0502 pede 96.940 kg de calcário com 60.000 kg em estoque; OS-0501 (Lagoa Grande) reservaria glifosato do almoxarifado da Santa Rita sem avisar.
  - O almoxarife não tem ação sobre a falta, nem na O.S. nem no Estoque; no app (MB-05) vê "Conflito de reserva" e é mandado ao Planejar safra.
  - Troca de produto: só pelo "Ajustar antes de liberar", à mão (tirar, incluir, digitar a dose) e só em "A liberar". Cada inclusão confere cultura, dose de bula, número máximo de aplicações e alvo; a carência é conferida na liberação; o grupo IRAC/FRAC é só informativo.
  - Melhor padrão já existente para a troca: a decisão MIP do AG-01 lista os produtos registrados para cultura × alvo com os selos "Sem estoque", "Rotação" e "Carência". Levar essa lista para dentro da O.S.
- Compras:
  - Insumo só se compra pela solicitação da safra, que nasce no Planejar safra, em 6 etapas, com cotação a homologados e alçada por valor (50 mil, 300 mil, Direção). Não há urgência, a chegada viável é fixa (+7 dias) e a solicitação não carrega a O.S. de origem.
  - A requisição avulsa existe, com urgência Normal, Alta ou Urgente, mas é vedada a insumo agrícola ("Nunca safra ou cultura", CMP). Compra de insumo fora do plano não existe; o caminho é indireto (O.S. → complemento no Planejar safra → compra).
- Manutenção (o melhor modelo do protótipo, a seguir nas outras áreas):
  - A OM mostra a peça em falta, bloqueia a liberação e oferece "Solicitar compra" em 1 clique. A requisição sai só com a falta, não duplica, carrega OM e ativo, e a peça que chega fica reservada para a OM.
  - Lacunas: a corretiva nasce sem peças; o papel do almoxarife é simulado; a urgência não reflete ativo parado.
- Packing e agroindústria:
  - Só a caixa está modelada. A reserva divide entre lotes e a falta aponta de onde recuperar (sobra de outra ordem, nota a conferir, quarentena).
  - Comprar caixa ficou para um bloco futuro (BEN-2). Outros materiais de linha e de pós-colheita não existem.
- Em aberto: a integração real com o ERP, que no protótipo é simulada; e a exigência de receituário na compra de defensivo (Lei 7.802/1989, art. 13), a confirmar com o RT ou o jurídico.

8. NÃO FAZER
- Tela nova de "estoque da O.S." separada do documento: o check mora na linha do material.
- Compra emitida sem confirmação humana ou fora da alçada.
- Trocar produto sem as checagens de registro, carência e grupo, ou fora da aprovação agronômica.
- Esconder o "fora do plano" do planejado × realizado.
- Notificar quem não precisa agir.

9. ENTREGA (no canal registrado)
- Desenho final, com o que Claude e Codex mudaram neste pedido e por quê.
- Fatias, com autoria e revisão.
- Medidas antes e depois, e os testes de regressão.
- Três listas curtas, com motivo: aplicado, deixado de fora, cortado.
- Suposições e pendências, cada uma com o gatilho de retomada.
