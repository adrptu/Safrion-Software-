# VEL-20261013-01 — exceção delimitada e método de trabalho

Autor: Codex. Revisor/integrador solicitado: Claude real. Base: `99edafe06ee320221f5ea3efe650e5d3ac7d8606`.

Adrianus autorizou diretamente no canal Codex: “Eu autorizo o que o claude te pediu”. Abrange a exceção delimitada e a atualização de AGENTS; não amplia a autorização para outras mudanças de segurança. [Recibo da autorização e autoria](https://github.com/adrptu/Safrion-Software-/pull/47#issuecomment-6136375909).

## Alteração

A regra `generic-api-key` passa a aceitar exclusivamente o literal de localStorage da ficha de pivô, nos caminhos completos `tools/prototipo/v37/gen37/ficha_pivo.py` e `tools/prototipo/v37/gen37/irrigacao_estado.js`. Bloco próprio, `AND`, alvo `secret`, valor e caminhos ancorados. O restante da configuração fica idêntico, incluindo as regras padrão e exceções anteriores.

Claude forneceu os trechos de declaração, leitura/gravação e evento de storage em [6136330759](https://github.com/adrptu/Safrion-Software-/pull/47#issuecomment-6136330759). Esses trechos foram lidos; a composição completa `302b26f` permanece local com o autor. Esta entrega não comprova ausência de outros achados na v56 nem resolve achados em patches documentais.

AGENTS §3.5/3.6 registra a proposta de velocidade do autor com os limites discutidos: teto de frentes sem ampliar autoria, teste por impacto, base corrigida com contraprova, cache por fonte limpa e entradas, espera observável com limite e provas recuperáveis. Auditoria integral e revisão final do PRD mantêm os gatilhos do proprietário.

## Evidência executada

Gitleaks 8.30.1: 15 históricos Git sintéticos, dois commits cada (introdução e remoção do arquivo), varridos com a configuração base e a candidata. Os 30 scans passaram. Base acusa os dois casos autorizados; candidata só os libera. Casos com outros valores, caminhos semelhantes, sufixos, prefixos, ponto não literal e canário de outra regra padrão continuam acusados no commit de introdução.

Configuração anterior preservada byte a byte ao remover o único bloco novo. AGENTS preservado byte a byte ao remover as duas inserções, sem novos links relativos nem marcadores de conflito.

O contrato permanente dos limites está em `tools/ci/test_gitleaks_excecoes.py`, descoberto pelo comando já existente da CI (`python3 -m unittest discover -s tools/ci -v`). Confere defaults, uma exceção, AND/secret, literal e dois caminhos exatos, além de valores e caminhos vizinhos. É teste de configuração; os 30 scans acima exercitam o detector real. Nenhum workflow foi alterado. Discovery focal executada: 7/7 testes passam; sete mutações dos limites falham na classe nova. Brutos em `ci-contract-evidence.json`. Os scans anteriores foram preservados por equivalência da configuração.

O script e os brutos sanitizados desta execução estão neste diretório. Só dados fabricados. A tentativa diagnóstica inicial usou quatro canários que a base também não detectava (22/30); foram corrigidos os dados sintéticos, sem relaxar asserções ou configuração. A execução final portátil e seu recibo são os usados para reprodução.

## Reprodução

Em checkout desta candidata, com Gitleaks 8.30.1 já instalado, crie uma pasta temporária fora do checkout para a saída. Recupere a configuração de base com `git show 99edafe06ee320221f5ea3efe650e5d3ac7d8606:.gitleaks.toml` e salve-a nessa pasta. Execute `python3 docs/parceria/rodadas/VEL-20261013-01/test-gitleaks-ficha-pivo.py --gitleaks /caminho/gitleaks --base-config /pasta/temporaria/base.toml --candidate-config .gitleaks.toml --output /pasta/temporaria/execucao.json`.

## Limites e próximo passo

Prova focal em histórico Git local, sem dados reais e sem varredura completa da composição do produto. Os testes de apoio Codex não substituem a revisão independente do Claude real. CI da candidata e parecer do revisor são verificados no PR antes da integração por ele; Codex não integra o próprio PR. Após integração, Claude incorpora a configuração e inspeciona os achados restantes antes de publicar suas branches. CTL-4 e sua autoria permanecem em andamento.

PR #53 foi integrado pelo revisor Claude em `999b0d0`, após sua reprodução30/30 e parecer6136712553. O contrato permanente e o registro STATUS são um complemento da mesma rodada, respondendo aos achados4254031552/4254031559; exigem revisão/CI próprios. A contraprova24→6 no histórico v56 e3→0 no commit único permanece relato do Claude até leitura dos brutos por Codex.

Reversão: reverter somente o commit do incremento pertinente; sem migração, dados do produto ou workflow alterados.

## Correção da revisão do PR #54

Os achados 4254083832/4254083841 foram reproduzidos: os sete testes anteriores aceitavam uma segunda exceção ampla antes ou depois do bloco exato, e uma exceção global. A candidata agora avalia todos os blocos de `generic-api-key` para os pares de valor/caminho proibidos; exige as formas AND/secret atualmente autorizadas e rejeita formas globais ou campos adicionais até revisão específica. Este contrato usa regexes Python compatíveis com as expressões atuais, não pretende substituir o detector Gitleaks.

O harness recuperável `test-ci-contract.py` executa discovery em cópias temporárias e preserva a configuração real. Execute, da raiz: `python3 docs/parceria/rodadas/VEL-20261013-01/test-ci-contract.py --repository . --output /tmp/vel-contract-nova-execucao.json`. A saída deve ser um caminho ainda inexistente. Python 3.11+; nenhuma dependência adicional. Resultado: 8/8 testes focais e dez mutações rejeitadas, total de 11 execuções verificadas. Fonte do harness e brutos antes/depois em `ci-contract-review-evidence.json`; a prova anterior de sete mutações permanece em `ci-contract-evidence.json`.

Para reproduzir o defeito, use este mesmo harness com `--repository` apontando para checkout separado de `1ef1c499be50099a65f40371a0f35e8e5a4e607c` e `--expected-tests 7`: três mutações novas escapam, portanto o harness termina com erro. A primeira tentativa local de preparar a reprodução encontrou `.gitleaksignore` ausente na cópia parcial; depois de recuperado da mesma SHA, os resultados antes/depois acima foram executados. Não foi defeito do produto.

## Revisão estrutural (4254146537 / Claude 6136974042)

A amostra de pares não é suficiente: outra versão exata (v3) e uma segunda regra generic-api-key escapavam. Reproduzidos os dois casos no2c8c450:11/13 execuções esperadas. Agora há exatamente uma regra generic-api-key; todas as suas allowlists são comparadas, em igualdade integral, com a referência autorizada em tools/ci/fixtures/gitleaks_generic_allowlists.json. Uma mudança de exceção exige mudança visível dessa referência no PR e revisão. A referência contém as cinco exceções existentes (HML-SECRET-01/03/04, NAV-F1-A e VEL), sem conceder nenhuma nova. O teste por pares permanece suplementar. Configuração real e workflows intactos.

O mesmo comando portátil agora executa8testes e12mutações,13/13 verificadas; harness copia também a referência fixa para as cópias isoladas. Brutos antes/depois em ci-contract-structural-evidence.json; evidências anteriores preservadas. Para a reprodução antes, usar o teste do2c8c450 com o novo harness e a referência copiada. Não é nova execução dos30scans do detector, cuja configuração não mudou.
