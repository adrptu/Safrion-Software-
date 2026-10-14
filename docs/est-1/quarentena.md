# EST1-QUAR-01 — quarentena vencida cobre demanda (S2/P1)

Base PR60/a4b333d0a8afc35fdc62263f24a609447f4bccf7, autoria Codex da contraprova. Produto não alterado. Cenário exclusivamente sintético, Node local, 13/10/2026 21:10 BRT.

Demanda10L e lote100L integralmente em quarentena. Controle válido: compra0/condicional10. Vencido01/2000: continua compra0/condicional10. A memória orienta o gestor a liberar por laudo e diz que não há falta se liberar. Estoque não permite liberar lote vencido. Esperado: compra10/condicional0, físico/quarentena100 e histórico preservados. Contraprova1/2; funções reais cenEstDem, demFazenda, cal01Memo; nenhum dado mutado.

cenEstDem mantém a quantidade vencida em quar; demFazenda soma quarC à cobertura condicionada. A exclusão de físico já feita não cobre este consumidor. A autorização6157512088 limitava exclusão do físico; classificação de quarentena permanece com Claude salvo extensão explícita. Menor correção proposta: excluir vencido da cobertura condicionada, sem inventar laudo reprovado nem mudar físico/quarentena, e preservar motivo na memória. Claude corrige ou confirma fronteira; Codex retesta o mesmo caso e controles afetados. Parecer inicial enviado6157883127, readback confirmado.

Reprodução: no gen37, com Node no PATH, SAFRION_DADOS=sintetico python3 est_validade_quar_dem_test.py. Saída esperada atual exit1/1de2. Não interpretar vermelho como teste quebrado ou ignorá-lo para integrar. Não é auditoria global, não encerra EST1/PRD/HML.
