Sirva a raiz do pacote via HTTP local e abra `provas/correcoes/regression.html`. A página expõe `window.testResults` e título `PASS 36/36`; usa dados sintéticos, sem dependências externas. Na rodada Claude6179132314, os assets anteriores35c4c5f passam17/30 e os corrigidos1913beb passam36/36. Logs `r8-browser-red.log` e `r8-browser-green.log`.

A suíte `provas/tabela/regression.html` tem9/9 casos; o asset não mudou nesta rodada e sua prova anterior permanece válida. `provas/dominio/domain-test.mjs` extrai as referências:56/68 antes e68/68 depois (logs r8-domain). Requer TypeScript já presente no ambiente de validação.

`r8-eslint.log` registra comando/saída0 do asset corrigido no caminho real do pacote, usando configuração raiz. Logs antigos (inclusive `eslint-green.log` vazio por saída0) documentam candidatas anteriores; não são os totais atuais. Não confundir revisão local com CI ou carregamento cloud.

Rodada R9: cancelamento local mantém gravação incerta; readback terminal preserva rascunho, bloqueia GET inconclusivo e ignora recibo antigo após reconciliação. Contraprova inicial 30/34, final 36/36. Domínio 68/68 e tabela 9/9 preservados sem alteração.
