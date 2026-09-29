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
- O verificador de cobertura é um smoke test das dependências diretas fixadas; não certifica transitivas, ferramentas de desenvolvimento ou ausência de vulnerabilidades. `workspace:*` é aceito somente para nomes internos existentes e unívocos em `packages/*` ou `apps/*`; suas dependências externas continuam obrigatórias no inventário. Versões em intervalo, outras referências workspace/URL/file/link e estruturas novas exigem revisão explícita do contrato. Excluir o nome da raiz como alvo é uma restrição deste controle, não uma limitação do pnpm. A resolução real do workspace continua verificada pela instalação com lockfile congelado. Novo glob em pnpm-workspace.yaml exige atualizar o guard no mesmo PR.
- Regressões locais do FERR-05: `python3 -m unittest discover -s tools/ci -p 'test_conferir_cobertura_trivy.py' -v`, 25 testes passaram após adaptação para pacotes internos. Relatórios anteriores de CI não validam este delta; execução remota e pareceres por versão ficam no PR e na issue #1. Não se presume aprovação pelo código presente aqui.

## Próximo passo e responsáveis

1. Codex verifica a CI real desta correção; Claude faz revisão crítica e integra somente após aceite técnico. Codex não aprova nem integra o próprio PR.
2. Continuar a sequência já aberta: #3 (Gitleaks) → #4 (política Trivy) → #5 (domínio), incorporando FERR-05 antes da liberação. O #2 (contrato CI) permanece separado e requer atualização da base.
3. Claude conduz a dependência imediata da F1, com Codex revisando/testando. Critérios e divisão permanecem na issue #1 e nas rodadas; sem abrir módulos paralelos.
4. Codex e Claude conduzem a homologação técnica e funcional, conforme autorização atual do proprietário. Adrianus recebe a candidata verificada e dá feedback; produção exige seu aceite explícito da versão.

## Condições preservadas

- Segredos e dados reais nunca entram em código, testes ou logs (`AGENTS.md`, `SECURITY.md`).
- Conta, gastos, dados de clientes e produção dependem da autorização concreta do proprietário.
- Os agentes usam a mesma identidade GitHub; parecer independente precisa identificar agente, versão, testes e limites. Proteção efetiva da `main` deve ser comprovada pelo servidor; um arquivo de configuração não prova aplicação.
- Versões da fundação: `docs/architecture/versions.md`. Decisões materiais pendentes: `docs/DECISIONS.md`.
