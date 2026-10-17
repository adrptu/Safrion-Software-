# Revisão do app do Codex no PR #98 (HEAD f028139): dois achados P2 confirmados e corrigidos em f8fb069

**F1 (`safra_lote.js:269`): a faixa "Aplicar aos marcados" com Milho e a cultivar de soja que sobrou levava a cultivar de soja para as linhas de milho.**
- Causa:
  - `slPode('var')` aceitava qualquer cultivar, sem olhar a cultura da linha;
  - `setAp('cult')` limpava o plano incompatível, mas não a cultivar.
- Correção, regra única para a célula, a colagem e a faixa:
  - `slPode('var')` recusa cultivar cadastrada de outra cultura, com o motivo "cultivar de Soja, não de Milho" (a mesma regra do `slTrocaCult`);
  - a célula da variedade passa pela mesma conferência do plano;
  - na faixa, trocar a cultura tira a cultivar da outra cultura.
  - Texto livre continua aceito.

**F2 (`safra_lote.js:191`): depois de uma gravação recusada, corrigir pela faixa ou pela colagem deixava o erro e a mensagem geral na tela.**
- Correção:
  - `slAplicarSel` e `slColarBloco` passam a devolver as células feitas;
  - `slSemErro` tira essas células do erro, como faz a edição da célula (a cultura leva junto o erro do plano);
  - sem erro restante, a mensagem geral some.

## Proteção de regressão (executado; brutos nesta pasta)

| Teste | Correção | Contraprova (`safra_lote.js` / render de f028139) |
|---|---|---|
| saf_lote_unit_test (5 casos novos) | 59/59 | 54/59 (falham os 5 novos) |
| saf_lote_test (C5 erro limpo; C6 faixa troca a cultura) | 47/47 | 45/47 (C5 e C6) |
| tabelas_saf_test | 24/24 | — |
