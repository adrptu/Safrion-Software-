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

### R17 — datas de calendário e âmbito da GTA
4277216807: datas brasileiras/ISO precisam conservar ano, mês e dia após construção; filtros com operador/intervalo inválido retornam vazio, inclusive !=. Contraprova22/27 na base50a15f9 →27/27 na candidata (calendário impossível, bissexto válido e intervalo válido). JSON bruto e exit do teste conferidos separadamente. Sem alteração de layout.
4277216804: GTA limitada ao trânsito sujeito à norma da espécie/origem/destino/jurisdição; eventos de inventário não criam exigência automática. Fonte oficial MAPA consultada14/10/2026: https://www.gov.br/pt-br/servicos/habilitar-se-para-emissao-da-guia-de-transito-animal . A página define GTA para transporte e normas por espécie; não equivale a todos os estados do inventário.
20/20skills,17/17adaptador,lint passaram; autosave50/50,domínio68/68 e mobile R16 preservados sem delta.53arquivos,34alterados vs instalaçãooriginal; manifesto7ef59739ce656c624f636b7c4d45a31649eb29dde0f96aa4ceb49b28da6727ef. ParecerClaude6180441509 aceita R16; seis threads encerradas conforme parecer. R17 aguarda nova revisão/CI/integração pelo Claude. HistóricoGitleaks e recibocloud pendentes; retificaçãoR13 preservada.

### R18 — CI com referências imutáveis e mínimo privilégio
Advisory4277265763: template opt-in ci.yml sem permissão global de escrita; cada job só contents:read, checkout persist-credentials:false. Cobertura preservada no resumo da execução (comment-on:none). Actions fixadas em commits completos e seis imagens por digest de manifest público conferido comSHA256; configs de quatro scanners inspecionadas sem executar imagens. Scanners recebem código somente para leitura, sem token nem socket Docker; Trivy lê docker-save. npx usa dependências locais do lockfile. Corrigidas expressões em mapaYAML e comandos echo com dois-pontos que invalidavam o arquivo.
Contraprova estática0/8exit1→8/8exit0, parserYAML real2.9.1. Não é execução do pipeline, imagem auditada integralmente ou liberação de produção. Sem mudanças em proteções/workflows ativos. Tentativas Python semPyYAML/SDK incompatível são falhas de ferramenta, não prova do template; abordagem alterada para parserNode existente.20skills/17adaptador e provas50/50autosave,27/27tabela,68/68domínio preservadas deR17 semdelta, não reexecutadas nesta rodada.
53arquivos, 35 alterados vsoriginal; manifesto0b494706cb86acae33324fc3be0ee62d12422989a6bc1f4759bfa3e4bbf05edf. Dependências upstream: https://github.com/davelosert/vitest-coverage-report-action/blob/8f86cfb56ed6d5613ea8cdc5259f207fbfd51ece/action.yml ; https://google.github.io/osv-scanner/ ; https://docs.semgrep.dev/semgrep-ci/sample-ci-configs . SemgrepActiondeprecated e OSV@v1inexistente foram substituídos porCLIs oficiais em digest. Atualizações exigemPR revisado; bases de vulnerabilidades/regrasOWASP continuam dados remotos. Claude/CI/integração e recibocloud pendentes; retificaçãoR13 preservada.

R18b: CI de9a44c6c falhou somente pelo proofscript.cjs fora do projeto tipado. Convertido para ESM.mjs, convenção JS já coberta pelo lint existente; nenhuma exclusão ou proteção alterada. ESLint real exit0, Prettier executado, prova estática ESM8/8exit0. AssetCI e manifesto R18 inalterados.
