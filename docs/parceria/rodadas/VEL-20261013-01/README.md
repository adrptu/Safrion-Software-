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

O script e os brutos sanitizados desta execução estão neste diretório. Só dados fabricados. A tentativa diagnóstica inicial usou quatro canários que a base também não detectava (22/30); foram corrigidos os dados sintéticos, sem relaxar asserções ou configuração. A execução final portátil e seu recibo são os usados para reprodução.

## Reprodução

Em checkout desta candidata, com Gitleaks 8.30.1 já instalado, crie uma pasta temporária fora do checkout para a saída. Recupere a configuração de base com `git show 99edafe06ee320221f5ea3efe650e5d3ac7d8606:.gitleaks.toml` e salve-a nessa pasta. Execute `python3 docs/parceria/rodadas/VEL-20261013-01/test-gitleaks-ficha-pivo.py --gitleaks /caminho/gitleaks --base-config /pasta/temporaria/base.toml --candidate-config .gitleaks.toml --output /pasta/temporaria/execucao.json`.

## Limites e próximo passo

Prova focal em histórico Git local, sem dados reais e sem varredura completa da composição do produto. Os testes de apoio Codex não substituem a revisão independente do Claude real. CI da candidata e parecer do revisor são verificados no PR antes da integração por ele; Codex não integra o próprio PR. Após integração, Claude incorpora a configuração e inspeciona os achados restantes antes de publicar suas branches. CTL-4 e sua autoria permanecem em andamento.

Reversão: reverter o commit deste PR; sem migração, dados do produto ou workflow alterados.
