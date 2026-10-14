Sirva a raiz do pacote via HTTP local e abra `provas/correcoes/regression.html`. A página expõe `window.testResults` e título `PASS 42/42`; usa dados sintéticos, sem dependências externas.

Na rodada Claude 6179132314, os assets anteriores 35c4c5f passam 17/30 e os corrigidos 1913beb passam 30/30 (logs r8-browser). A rodada R9 reproduziu o abort local: 30/34 antes, 36/36 depois (logs r9-browser). A rodada R10 reproduziu o aviso perdido: 36/37 antes, 37/37 depois (logs r10-browser). Cancelamento local mantém a gravação incerta; reconciliação exige término remoto, preserva rascunho e ignora recibos ultrapassados.

A suíte `provas/tabela/regression.html` tem 14/14 casos na rodada R12; os logs anteriores de 9/9 permanecem históricos. `provas/dominio/domain-test.mjs` extrai as referências: 56/68 antes e 68/68 depois (logs r8-domain). Requer TypeScript já presente no ambiente de validação.

Os logs eslint registram comando e saída 0 no caminho real do pacote, com a configuração raiz. Logs antigos documentam candidatas anteriores; não são os totais atuais. Revisão local não comprova CI nem carregamento cloud.

R11 (4276852743): 37/40 antes → 40/40 depois. Recibo tardio encerra o aviso de incerteza; mostra o sucesso configurado somente quando o rascunho coincide com o confirmado. Mensagem desativada e rascunho mais recente também cobertos.

R12: dois formulários incertos não trocam indevidamente seus avisos após recibo tardio (40/41→41/41). Atualização da tabela mantém seleção por identidade estável, grupo expandido e foco; remove seleção ausente/ambígua (11/14→14/14). Logs r12-browser/r12-table.

R13 (Claude 6179948396): confirmação tardia de B retoma automaticamente rascunho C sem nova tecla; contraprova 41/42→42/42. Tabela R12 14/14 permanece sem delta.
