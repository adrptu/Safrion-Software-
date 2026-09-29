# Estado do projeto

Atualizado em 29/09/2026 por Claude, sobre a `main` `15e53d27`. PR aberto não significa integrado; configuração só vale depois de lida no servidor.

## Onde estamos

| Frente | Estado | Evidência |
|---|---|---|
| PRD | v3.9 vigente; v3.10 em revisão, com propostas de edição por tema aguardando as três IAs | `docs/PRD.md`, `docs/DECISIONS.md` |
| Protótipo | Navegável; sem banco ou login reais | https://claude.ai/artifact/WPDgqGvKX6CYTCdPjidBLo |
| Repositório | Privado; PRs #2 a #15 integrados | https://github.com/adrptu/Safrion-Software- |
| Fundação | Domínio (decimal, unidades e saldo por lote); PostgreSQL/PostGIS com RLS e isolamento entre organizações; login OIDC com sessões; concessão e revogação de acesso; primeira interface de estoque e cadastros; imagens de homologação verificadas na CI | PRs #5, #7, #8, #9, #10 e #11 |
| Homologação | Terraform, conexão ao banco por IP privado e fila de vínculo integrados e validados na CI, sem plan nem apply. **Nenhum ambiente hospedado**: provisionar depende de autorização concreta de custo e destino | PR #14; `infra/terraform/`; `docs/OPERACAO.md` |
| Proteção da `main` | Ruleset ativo com exclusão e force push bloqueados e pull request obrigatório. Os 10 checks obrigatórios do PR #15 só contam como ativos depois da leitura do ruleset no servidor | PR #15; `tools/github/` |
| Produção | Não existe | — |

## Verificação executada e limite

- PR #14, candidata `a1c880e`: 10 checks com success; 247 testes unitários; integração com PostgreSQL real, 171 testes em 16 arquivos, nenhum pulado; jornadas de navegador no desktop e no celular; imagens com SBOM; Terraform validado sem credencial.
- PR #15, candidata `b300f6ad`: 10 checks com success, inclusive a regressão da proteção da `main` (`tools/ci/test_protecao_main.py`); simulação contra o GitHub real só com leitura.
- CI verde não prova operação hospedada, login com provedor real na homologação nem restauração de backup.

## Próximo passo e responsáveis

### Sequência

1. Codex aplica os checks obrigatórios no ruleset existente e confere a leitura de volta.
2. Ensaio remoto da homologação, com autorização de custo e destino do proprietário: restauração do backup em instância isolada, logs sem dados pessoais, acesso e revogação.
3. Antes do primeiro usuário externo: teste de todas as rotas com usuário de outra organização e inventário dos dados pessoais tratados.
4. PRD v3.10: revisão das propostas por tema pelas três IAs.
5. Codex e Claude conduzem a homologação técnica e funcional. Adrianus recebe a candidata verificada e dá feedback; produção exige o aceite explícito dele para a versão.

### Segurança estática — FERR-06

Semgrep CE 1.178.0 acrescenta duas regras locais: verificação TLS desabilitada e entrada de requisição usada no texto SQL. O alcance é intraprocedural; não certifica autorização, isolamento, fórmulas, migrações SQL ou todos os caminhos de injeção. Valores parametrizados são o contraexemplo seguro. Testes nativos `ruleid`/`ok` precisam detectar os positivos sem marcar os negativos. O guard rejeita relatório vazio, erro de parser reportado, regra ignorada, timeout de análise e inventário incompleto de JS/TS em `packages/*/src`, `apps/*/src` e na raiz desses pacotes (inclusive `next.config.ts`). Os pré-filtros do scanner podem dispensar o parse de arquivos sem padrões pertinentes: inventário não comprova sintaxe integral. A compilação TypeScript continua obrigatória em outro job.

Local: `python3 tools/ci/check_semgrep.py --semgrep /caminho/semgrep .` (mesma versão). CI: workflow próprio, imagem oficial por digest, código montado somente para leitura e rede desativada no container; sem login, métricas, regras remotas ou envio de achados. Os fixtures sintéticos são excluídos do lint tipado/formatação e verificados pelo scanner nativo. Resultados locais, CI e pareceres por versão ficam no PR e na issue #1; presença de configuração não equivale a gate executado/aprovado nem a proteção aplicada à main.

O Dependabot cobre GitHub Actions; pacotes, lockfile, imagens e ferramentas ficam com o Renovate (PR #12), cujo primeiro PR automático ainda não foi comprovado. Sonar (ENG-018) permanece pendente de consumidor/conta e comprovação do gate. Playwright/axe acompanham as telas do Claude; Terraform/TFLint, testes de carga/ZAP e telemetria exigem seus alvos concretos. Nenhum destes itens pendentes é contado como ativo.

## Jornadas de navegador na CI

O workflow `.github/workflows/navegador.yml` executa as jornadas Playwright/axe existentes em runner Ubuntu 24.04, com Chrome do runner e PostgreSQL/PostGIS efêmero fixado pelo mesmo digest da integração. Não usa segredos, dados reais ou serviços GCP. A versão efetiva do navegador fica no log; ela acompanha a imagem do runner e não é fixada pelo projeto.

`tools/ci/conferir_e2e.py` exige no mínimo nove jornadas desktop e uma celular, incluindo a nova jornada do pedido de acesso, resultado real aprovado em uma tentativa, nenhum skip/falha esperada/erro global e totais coerentes. O recibo publicado contém só commit, nome e resultado dos casos; traces, cookies e relatórios brutos não são artefatos publicados. A regressão recusa o relatório antigo de oito desktop e uma celular. A execução remota e a revisão tripla por versão são registradas no PR correspondente e na issue #1.

Essa prova usa a aplicação e o banco reais em modo DEV, com identidades fictícias. Não demonstra autenticação com provedor real, hospedagem funcional nem autonomia remota dos agentes. Os serviços descartáveis pertencem somente ao job e são removidos pelo runner.

Referências consultadas em 28/09/2026: [Playwright na CI](https://playwright.dev/docs/ci-intro), [relatório JSON](https://playwright.dev/docs/test-reporters#json-reporter), [serviço PostgreSQL](https://docs.github.com/en/actions/tutorials/use-containerized-services/create-postgresql-service-containers) e [inventário do runner Ubuntu 24.04](https://github.com/actions/runner-images/blob/main/images/ubuntu/Ubuntu2404-Readme.md).

## Condições preservadas

- Segredos e dados reais nunca entram em código, testes ou logs (`AGENTS.md`, `SECURITY.md`).
- Conta, gastos, dados de clientes e produção dependem da autorização concreta do proprietário.
- Os agentes usam a mesma identidade GitHub; parecer independente precisa identificar agente, versão, testes e limites. Proteção efetiva da `main` deve ser comprovada pelo servidor; um arquivo de configuração não prova aplicação.
- Versões da fundação: `docs/architecture/versions.md`. Decisões materiais pendentes: `docs/DECISIONS.md`.
