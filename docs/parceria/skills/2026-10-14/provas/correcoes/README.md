Sirva a raiz do pacote via HTTP local e abra `provas/correcoes/regression.html`. A página expõe `window.testResults` e título `PASS 50/50`; usa dados sintéticos, sem dependências externas.

Na rodada Claude 6179132314, os assets anteriores 35c4c5f passam 17/30 e os corrigidos 1913beb passam 30/30 (logs r8-browser). A rodada R9 reproduziu o abort local: 30/34 antes, 36/36 depois (logs r9-browser). A rodada R10 reproduziu o aviso perdido: 36/37 antes, 37/37 depois (logs r10-browser). Cancelamento local mantém a gravação incerta; reconciliação exige término remoto, preserva rascunho e ignora recibos ultrapassados.

A suíte `provas/tabela/regression.html` tem 14/14 casos na rodada R12; os logs anteriores de 9/9 permanecem históricos. `provas/dominio/domain-test.mjs` extrai as referências: 56/68 antes e 68/68 depois (logs r8-domain). Requer TypeScript já presente no ambiente de validação.

Os logs eslint registram comando e saída 0 no caminho real do pacote, com a configuração raiz. Logs antigos documentam candidatas anteriores; não são os totais atuais. Revisão local não comprova CI nem carregamento cloud.

R11 (4276852743): 37/40 antes → 40/40 depois. Recibo tardio encerra o aviso de incerteza; mostra o sucesso configurado somente quando o rascunho coincide com o confirmado. Mensagem desativada e rascunho mais recente também cobertos.

R12: dois formulários incertos não trocam indevidamente seus avisos após recibo tardio (40/41→41/41). Atualização da tabela mantém seleção por identidade estável, grupo expandido e foco; remove seleção ausente/ambígua (11/14→14/14). Logs r12-browser/r12-table.

R13 (Claude 6179948396): confirmação tardia de B retoma automaticamente rascunho C sem nova tecla; contraprova 41/42→42/42. Tabela R12 14/14 permanece sem delta.


### Rodada R14 — avisos no reenvio e retificação dos brutos
4277025876: confirmação normal (inclusive após retomada) só exibe sucesso se não houver snackbar ou se o atual pertencer à mesma instância. Aviso incerto de outro formulário é preservado. Contraprova no código anterior com oráculos corrigidos: 42/43; código corrigido: 43/43 (JSON bruto analisado integralmente, processo exit0). 20/20 skills, 17/17 adaptador e lint passaram. Tabela14/14 e domínio68/68 anteriores preservados. Manifesto 99237e91c966488fef25e7c94e98cb7d2dddb00675ef0345c243120e4037044d.
Retificação obrigatória de R13/6179987882: o bruto r13-browser-green.log contém40/42, não42/42. A consolidação anterior considerou indevidamente o exit do validador posterior. Um oráculo antigo esperava pending=false embora C estivesse reagendado; outro selecionava snackbar em animação de saída. Agora considera a fila pendente e o último snackbar anexado; código antigo reprova somente4277025876. Logs originais preservados; tentativas iniciais R14 também não contam como aprovação. Retificação enviada em6180085861. Revisão Claude, CI, integração e recibo cloud pendentes.


### Rodada R15 — confirmação sem aviso ativo e ciclo de vida dos comandos
4277091514: recibo tardio exibe sucesso quando a instância possui o aviso ou não há aviso ativo; continua preservando avisos de outros formulários. Testados fechamento manual e expiração (temporizador do aviso acelerado somente no teste).
4277091526: Kit.commands retorna destroy idempotente, que remove somente essa inscrição, atualiza a paleta aberta e impede open após destruir. Inscrições independentes do mesmo objeto são preservadas; remontagem usa o callback atual. Sem mudar as teclas ou criar novos menus.
Contraprova na base15afdc06:44/50; correção:50/50 (JSON integral e exit0 separados). 20/20 skills,17/17 adaptador,lint passaram. Tabela14/14 e domínio68/68 anteriores preservados sem delta. Primeiro harness expirou sem resultado (null); r15-harness-timeout.log não é prova de produto. Janela de coleta ampliada para concluir os sete novos casos. Manifesto c96cfc92e2e4b8861821e8375c03f60eddc9ab7ef6f280db9e42d32a77be450c. Revisão Claude/CI/integração e recibo cloud pendentes. Retificação R13 permanece válida.


### Rodada R16 — agregado da primeira coluna no agrupamento
4277143467: a célula que contém o rótulo de grupo também mostra o agregado da primeira coluna quando firstAgg=0. Não cria coluna adicional nem altera cálculo/formatador. Contraprova15/18 na base9b8d0d7d → 18/18 na candidata: soma, segundo agregado/alinhamento, expansão por teclado e média em coluna única. Emulação390px: total30 visível; toque expande duas linhas e Enter recolhe. Não é teste em aparelho físico.
20/20 skills,17/17 adaptador e lint passaram; autosave/comandos50/50 e domínio68/68 anteriores preservados sem delta. Manifesto 4f85fc6a088470d8e5215e34aa48d5da1050d19a439439948f2227f735a7a084. Revisão Claude/CI/integração e recibo cloud pendentes. Retificação R13 permanece válida.
