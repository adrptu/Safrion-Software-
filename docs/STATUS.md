# Estado do projeto

Atualizado em 27/09/2026 por Codex. Estado desta proposta; PR aberto não significa integrado à `main`.

## Onde estamos

| Frente | Estado | Evidência |
|---|---|---|
| PRD | v3.9 vigente; v3.10 em revisão | `docs/PRD.md`, `docs/DECISIONS.md` |
| Protótipo | Navegável; sem banco ou login reais | https://claude.ai/artifact/WPDgqGvKX6CYTCdPjidBLo |
| Repositório | Publicado, privado | https://github.com/adrptu/Safrion-Software- |
| Fundação F0-a | Domínio de decimais, unidades e saldo por lote; proposta de Claude revisada por Codex | PR #5, base `a9e038dc4b4134ea7e6abc08efd7625ee0832137` |
| Ambiente funcional | Ainda sem banco, API, telas ou homologação acessível | F0-a é fundação técnica, não uma entrega de uso pelo agricultor |

## Verificação executada e limite

- PR #5, [CI 36345797548](https://github.com/adrptu/Safrion-Software-/actions/runs/36345797548): instalação com lockfile, versões, formatação, lint, tipos, 49 testes e build passaram. Gitleaks conferiu canário e histórico.
- O job Trivy dessa execução terminou verde, mas **não comprovou cobertura**: versão 0.70 leu somente o primeiro documento do lockfile pnpm 12 e omitiu as dependências do projeto (FERR-05). Esse verde não libera a candidata.
- Esta correção fixa Trivy 0.74.0 e exige inventário JSON com as dependências diretas de produção dos manifestos (`package.json`, `packages/*`, `apps/*`). Relatório vazio, inválido, sem alvo pnpm ou sem nome/versão esperado falha. O exit-code bloqueante do scanner continua obrigatório.
- O verificador de cobertura é um smoke test das dependências diretas fixadas; não certifica transitivas, ferramentas de desenvolvimento ou ausência de vulnerabilidades. Versões em intervalo, referências workspace/URL e estruturas novas exigem revisão explícita do contrato.
- Regressões locais do FERR-05: `python3 -m unittest discover -s tools/ci -p 'test_conferir_cobertura_trivy.py' -v`, 14 testes passaram. A execução real da proposta e o parecer independente ficam no PR e na issue #1; não se presume aprovação pelo código presente aqui.

## Próximo passo e responsáveis

1. FERR-05 passou na CI 36346438607, que reconheceu decimal.js@10.6.0. Claude ainda precisa revisar #6. Esta branch #2 recompõe o contrato sobre #6; seus checks e a revisão da composição ficam no PR. Codex não aprova nem integra o próprio PR.
2. Continuar a sequência já aberta: #3 (Gitleaks) → #4 (política Trivy) → #5 (domínio), incorporando FERR-05 antes da liberação. O #2 (contrato CI) tem agora esta composição sobre #6, preservando a implementação já revisada.
3. Claude conduz a dependência imediata da F1, com Codex revisando/testando. Critérios e divisão permanecem na issue #1 e nas rodadas; sem abrir módulos paralelos.
4. Codex e Claude conduzem a homologação técnica e funcional, conforme autorização atual do proprietário. Adrianus recebe a candidata verificada e dá feedback; produção exige seu aceite explícito da versão.

## Contrato de código — PR #2

A versão `4081524`, já revisada estaticamente pelo Claude, foi preservada integralmente nos dois arquivos de contrato. Rejeita manifesto, scripts e versões com tipos inválidos, com diagnóstico e ativo=false; trata JSON profundo ou inteiro acima do limite. Os 16 testes do contrato já passaram localmente. A composição sobre #6 precisa de CI própria, registrada no PR; o domínio e os controles de segurança não mudaram. A atualização da branch conserva os históricos anteriores, sem force-push ou merge de PR na main.

## Condições preservadas

- Segredos e dados reais nunca entram em código, testes ou logs (`AGENTS.md`, `SECURITY.md`).
- Conta, gastos, dados de clientes e produção dependem da autorização concreta do proprietário.
- Os agentes usam a mesma identidade GitHub; parecer independente precisa identificar agente, versão, testes e limites. Proteção efetiva da `main` deve ser comprovada pelo servidor; um arquivo de configuração não prova aplicação.
- Versões da fundação: `docs/architecture/versions.md`. Decisões materiais pendentes: `docs/DECISIONS.md`.
