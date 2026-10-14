Sirva a raiz do pacote via HTTP local e abra `provas/correcoes/regression.html`. A página expõe `window.testResults` e título `PASS 37/37`; usa dados sintéticos, sem dependências externas.

Na rodada Claude 6179132314, os assets anteriores 35c4c5f passam 17/30 e os corrigidos 1913beb passam 30/30 (logs r8-browser). A rodada R9 reproduziu o abort local: 30/34 antes, 36/36 depois (logs r9-browser). A rodada R10 reproduziu o aviso perdido: 36/37 antes, 37/37 depois (logs r10-browser). Cancelamento local mantém a gravação incerta; reconciliação exige término remoto, preserva rascunho e ignora recibos ultrapassados.

A suíte `provas/tabela/regression.html` tem 9/9 casos. Seu asset não mudou e a prova anterior permanece válida. `provas/dominio/domain-test.mjs` extrai as referências: 56/68 antes e 68/68 depois (logs r8-domain). Requer TypeScript já presente no ambiente de validação.

Os logs eslint registram comando e saída 0 no caminho real do pacote, com a configuração raiz. Logs antigos documentam candidatas anteriores; não são os totais atuais. Revisão local não comprova CI nem carregamento cloud.
