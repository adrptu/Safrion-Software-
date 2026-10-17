# CALDA-QTD — Codex

Contrato 6229825721 / aceite 6229840674. Base 24a632a5a8e717a2068913375149c98f8bf22738. Autor Codex; revisor/integrador Claude. ENG-011/ENG-013; caldeiro e almoxarife.

Preparo individual usa cenQtdTrecho por intervalo acumulado e cenQtd para a referência de tanque cheio. Agrupado calcula por O.S. na unidade original e somente depois converte mL/L ou g/kg, somando decimais com BigInt. Não altera volume, destinos, estoque ou comandos. Exceções de scanner caem de cinco para duas (custo e finitude).

Teste quantidade: 16/16 em JavaScriptCore e Node24, incluindo grade 7.777 pares Python/JS, fluxos anteriores e sete cenários de calda. 49,31ha, 2.000L, 150L/ha, dose0,5: cargas 6,67+6,66+6,67+4,66=24,66. Zero e área pequena; grupos com L/mL e kg/g. Cenário permanece intacto. Bruto Node e contraprova preservados. Teste novo sobre base:14/16, falhas16 (24,655 em vez de24,66) e10 (três multiplicações), demais aceites preservados.

Sem navegador Codex, teclado ou celular nesta alteração de cálculo; bloqueio vigente respeitado. Solicitar crítica/reteste do Claude na composição e integração pelo revisor; isto não publica nem conclui o protótipo.
