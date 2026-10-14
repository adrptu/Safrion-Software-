# EST1-QUAR-01 — quarentena vencida cobre demanda (S2/P1)

Base PR60/a4b333d0a8afc35fdc62263f24a609447f4bccf7, autoria Codex da contraprova. Produto não alterado. Cenário exclusivamente sintético, Node local, 13/10/2026 21:10 BRT.

Demanda10L e lote100L integralmente em quarentena. Controle válido: compra0/condicional10. Vencido01/2000: continua compra0/condicional10. A memória orienta o gestor a liberar por laudo e diz que não há falta se liberar. Estoque não permite liberar lote vencido. Esperado: compra10/condicional0, físico/quarentena100 e histórico preservados. Contraprova1/2; funções reais cenEstDem, demFazenda, cal01Memo; nenhum dado mutado.

cenEstDem mantém a quantidade vencida em quar; demFazenda soma quarC à cobertura condicionada. A exclusão de físico já feita não cobre este consumidor. A autorização6157512088 limitava exclusão do físico; classificação de quarentena permanece com Claude salvo extensão explícita. Menor correção proposta: excluir vencido da cobertura condicionada, sem inventar laudo reprovado nem mudar físico/quarentena, e preservar motivo na memória. Claude corrige ou confirma fronteira; Codex retesta o mesmo caso e controles afetados. Parecer inicial enviado6157883127, readback confirmado.

Reprodução: no gen37, com Node no PATH, SAFRION_DADOS=sintetico python3 est_validade_quar_dem_test.py. Saída esperada atual exit1/1de2. Não interpretar vermelho como teste quebrado ou ignorá-lo para integrar. Não é auditoria global, não encerra EST1/PRD/HML.


## Correção Codex — extensão autorizada em 6157925031

Base 76e3adc; cenEstDem exclui somente a quarentena vencida da cobertura condicionada. As referências conservam lote, validade e motivo; cal01Memo explica a falta firme, sem prometer liberação por laudo e sem criar reprovação. O estoque físico, a quarentena e os laudos não são alterados. Caso misto: 7 L vencidos + 3 L válidos para demanda de 10 L = compra firme 7 L e condicional 3 L.

Contraprova original 2/2; versão reforçada 3/3 incluindo mistura e parâmetro quar física usado pela Compra. Regressão demanda_unica_test.py 71/71. Build focal processo_compras exit0. Testes sintéticos de funções reais via Node; este delta não teve validação visual própria. Reutilizadas evidências anteriores de fluxo/teclado/390 px apenas para trechos não alterados. Revisão e integração pendentes do Claude; ninguém integra o próprio PR. Correção não encerra protótipo/HML/PRD final.

Aplicado: classificação consistente com a validade operacional e memória rastreável no detalhe existente. Fora: laudos/estado físico, fórmulas de demanda e outras telas. Cortado: cobertura e promessa de liberação inválidas, sem etapa nova. Suposição: data operacional definida pelo cenário, como contrato vigente.
