# Estado do projeto

Atualizado em 28/09/2026 por Codex. Estado desta proposta; PR aberto não significa integrado à `main`.

## Onde estamos

| Frente | Estado | Evidência |
|---|---|---|
| PRD | v3.9 vigente; v3.10 em revisão | `docs/PRD.md`, `docs/DECISIONS.md` |
| Protótipo | Navegável; sem banco ou login reais | https://claude.ai/artifact/WPDgqGvKX6CYTCdPjidBLo |
| Repositório | Publicado, privado | https://github.com/adrptu/Safrion-Software- |
| Fundação F0-a | Domínio de decimais, unidades e saldo por lote; proposta de Claude revisada por Codex | PR #5, base `a9e038dc4b4134ea7e6abc08efd7625ee0832137` |
| Ambiente funcional | Sem homologação hospedada acessível; banco e servidor web em revisão local na cadeia de Claude | Esta base remota contém o domínio; não é uma entrega de uso pelo agricultor |

## Verificação executada e limite

- PR #5, [CI 36345797548](https://github.com/adrptu/Safrion-Software-/actions/runs/36345797548): instalação com lockfile, versões, formatação, lint, tipos, 49 testes e build passaram. Gitleaks conferiu canário e histórico.
- O job Trivy dessa execução terminou verde, mas **não comprovou cobertura**: versão 0.70 leu somente o primeiro documento do lockfile pnpm 12 e omitiu as dependências do projeto (FERR-05). Esse verde não libera a candidata.
- Esta correção fixa Trivy 0.74.0 e exige inventário JSON com as dependências diretas de produção dos manifestos (`package.json`, `packages/*`, `apps/*`). Relatório vazio, inválido, sem alvo pnpm ou sem nome/versão esperado falha. O exit-code bloqueante do scanner continua obrigatório.
- O verificador de cobertura é um smoke test das dependências diretas fixadas; não certifica transitivas, ferramentas de desenvolvimento ou ausência de vulnerabilidades. `workspace:*` é aceito somente para nomes internos existentes e unívocos em `packages/*` ou `apps/*`; suas dependências externas continuam obrigatórias no inventário. Versões em intervalo, outras referências workspace/URL/file/link e estruturas novas exigem revisão explícita do contrato. Excluir o nome da raiz como alvo é uma restrição deste controle, não uma limitação do pnpm. A resolução real do workspace continua verificada pela instalação com lockfile congelado. Novo glob em pnpm-workspace.yaml exige atualizar o guard no mesmo PR.
- Regressões locais do FERR-05: `python3 -m unittest discover -s tools/ci -p 'test_conferir_cobertura_trivy.py' -v`, 25 testes passaram após adaptação para pacotes internos. Relatórios anteriores de CI não validam este delta; execução remota e pareceres por versão ficam no PR e na issue #1. Não se presume aprovação pelo código presente aqui.

## Próximo passo e responsáveis

### Segurança estática — FERR-06

Semgrep CE 1.178.0 acrescenta duas regras locais: verificação TLS desabilitada e entrada de requisição usada no texto SQL. O alcance é intraprocedural; não certifica autorização, isolamento, fórmulas, migrações SQL ou todos os caminhos de injeção. Valores parametrizados são o contraexemplo seguro. Testes nativos `ruleid`/`ok` precisam detectar os positivos sem marcar os negativos. O guard rejeita relatório vazio, erro de parser reportado, regra ignorada, timeout de análise e inventário incompleto de JS/TS em `packages/*/src`, `apps/*/src` e na raiz desses pacotes (inclusive `next.config.ts`). Os pré-filtros do scanner podem dispensar o parse de arquivos sem padrões pertinentes: inventário não comprova sintaxe integral. A compilação TypeScript continua obrigatória em outro job.

Local: `python3 tools/ci/check_semgrep.py --semgrep /caminho/semgrep .` (mesma versão). CI: workflow próprio, imagem oficial por digest, código montado somente para leitura e rede desativada no container; sem login, métricas, regras remotas ou envio de achados. Os fixtures sintéticos são excluídos do lint tipado/formatação e verificados pelo scanner nativo. Resultados locais, CI e pareceres por versão ficam no PR e na issue #1; presença de configuração não equivale a gate executado/aprovado nem a proteção aplicada à main.

Dependabot para npm/pnpm 12 permanece sem compatibilidade comprovada; a configuração existente cobre GitHub Actions. Sonar (ENG-018) permanece pendente de consumidor/conta e comprovação do gate. Playwright/axe acompanham as telas do Claude; Terraform/TFLint, testes de carga/ZAP e telemetria exigem seus alvos concretos. Nenhum destes itens pendentes é contado como ativo.

### Sequência de integração

1. A base #6 `82ba9ca` tem CI 36362052077 aprovada e parecer estático final do Claude; o Gemini revisou o mesmo script de produção, inalterado. A composição atual do #2 preserva os dois arquivos de contrato de `d0e7e336` e incorpora essa base. CI e revisão específicas da nova composição são registradas no PR antes da integração. Codex não aprova nem integra o próprio PR.
2. Continuar a sequência já aberta: #3 (Gitleaks) → #4 (política Trivy) → #5 (domínio) → #6 (cobertura Trivy) → #2 (contrato CI). A nova composição do #2 está alinhada à base #6, sem mudança de comportamento no contrato. Nenhum desses registros equivale a merge ou homologação funcional.
3. Claude conduz a dependência imediata da F1, com Codex revisando/testando. Critérios e divisão permanecem na issue #1 e nas rodadas; sem abrir módulos paralelos.
4. Codex e Claude conduzem a homologação técnica e funcional, conforme autorização atual do proprietário. Adrianus recebe a candidata verificada e dá feedback; produção exige seu aceite explícito da versão.

## Jornadas de navegador na CI

A proposta em `.github/workflows/navegador.yml` executa as jornadas Playwright/axe existentes em runner Ubuntu 24.04, com Chrome do runner e PostgreSQL/PostGIS efêmero fixado pelo mesmo digest da integração. Não usa segredos, dados reais ou serviços GCP. A versão efetiva do navegador fica no log; ela acompanha a imagem do runner e não é fixada pelo projeto.

`tools/ci/conferir_e2e.py` exige no mínimo as oito jornadas desktop e uma celular, resultado real aprovado em uma tentativa, nenhum skip/falha esperada/erro global e totais coerentes. O recibo publicado contém só commit, nome e resultado dos casos; traces, cookies e relatórios brutos não são artefatos publicados. As contraprovas locais do verificador passam; a execução remota e a revisão tripla por versão são registradas no PR #8 e na issue #1.

Essa prova usa a aplicação e o banco reais em modo DEV, com identidades fictícias. Não demonstra autenticação com provedor real, hospedagem funcional nem autonomia remota dos agentes. Os serviços descartáveis pertencem somente ao job e são removidos pelo runner.

Referências consultadas em 28/09/2026: [Playwright na CI](https://playwright.dev/docs/ci-intro), [relatório JSON](https://playwright.dev/docs/test-reporters#json-reporter), [serviço PostgreSQL](https://docs.github.com/en/actions/tutorials/use-containerized-services/create-postgresql-service-containers) e [inventário do runner Ubuntu 24.04](https://github.com/actions/runner-images/blob/main/images/ubuntu/Ubuntu2404-Readme.md).

## Condições preservadas

- Segredos e dados reais nunca entram em código, testes ou logs (`AGENTS.md`, `SECURITY.md`).
- Conta, gastos, dados de clientes e produção dependem da autorização concreta do proprietário.
- Os agentes usam a mesma identidade GitHub; parecer independente precisa identificar agente, versão, testes e limites. Proteção efetiva da `main` deve ser comprovada pelo servidor; um arquivo de configuração não prova aplicação.
- Versões da fundação: `docs/architecture/versions.md`. Decisões materiais pendentes: `docs/DECISIONS.md`.
