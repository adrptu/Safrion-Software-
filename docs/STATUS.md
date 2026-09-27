# Estado do projeto

Atualizado em 27/09/2026 por Claude Code. Leia este arquivo no início de cada sessão e atualize-o no fim de cada incremento (PRD 23.4).

## Onde estamos
| Frente | Estado | Evidência / local |
|---|---|---|
| PRD | **v3.9 vigente** (26/09/2026). A v3.10 está em revisão: cap. 73 (confiabilidade transacional, offline, desempenho), cap. 74 (design system) e refinamentos da comparação externa. | `docs/PRD.md`; rascunhos fora do repositório até o pull request da v3.10 |
| Fluxogramas | v3.9: 63 fluxos com raias | `docs/prd/fluxogramas/` |
| Protótipo navegável | Em validação pelo proprietário. **Não é produção.** | https://claude.ai/artifact/WPDgqGvKX6CYTCdPjidBLo |
| Repositório | Criado localmente em 27/09/2026 com documentação e CI. **Ainda não publicado no GitHub.** | este repositório |
| Código de produto | **Nenhum.** Não há backend, banco, integração ou implantação. | — |

## CI
| Job | Situação |
|---|---|
| Integridade da documentação (`tools/docs/checar_docs.py`) | Executado localmente em 27/09/2026 (ver a saída no pull request inicial). Roda na CI a partir do primeiro push. |
| Varredura de segredos (Gitleaks) | Configurado; **ainda não executado** (roda no primeiro push) |
| Vulnerabilidades e configuração (Trivy fs) | Configurado; **ainda não executado** |
| Código: instalação com lockfile, lint, tipos, testes, build | Configurado para ativar quando houver `package.json` e `pnpm-lock.yaml`; **não executado** |

## Bloqueios e pendências
1. **Publicar no GitHub.** Usuário `adrptu`, confirmado pelo conector do Codex. Nome `do-talhao-a-os`, privado. O repositório remoto ainda não foi criado; o Codex faz as operações remotas depois da revisão deste pacote. Nesta máquina não há `gh`.
2. **Revisão obrigatória na `main`.** Com uma só conta humana, exigir uma aprovação impede todo merge, porque o autor não aprova o próprio pull request. É preciso decidir como o Codex e o Claude aparecem no GitHub (conta ou app de cada um) antes de ligar a exigência. Até lá: pull request obrigatório, checks obrigatórios, sem force push e revisão registrada em `docs/parceria/rodadas/`.
3. **Ferramentas locais.** Node.js e pnpm não estão no PATH comum, mas existem no runtime do Codex: Node v24.19.0 e pnpm 11.25.0, conferidos em 27/09/2026. Servem para verificação local. A instalação reproduzível do projeto não pode depender desse caminho: versões fixadas no repositório (`packageManager`, `.nvmrc`) quando houver código. Docker não confirmado.
4. **Versões da stack** a fixar no primeiro commit executável (`docs/architecture/versions.md`).
5. **Decisões pendentes do proprietário:** `docs/DECISIONS.md`.
6. **Actions da CI referenciadas por versão maior** (`@v4`, `@v5`, `@v2`, `@0.28.0`). Antes do primeiro push, conferir a versão atual de cada action na fonte oficial e fixar por SHA do commit (prática de cadeia de suprimento, PRD 26). O Dependabot mantém atualizado depois. Ainda não feito: nesta máquina não foi consultada a fonte.

## Próxima etapa
1. Publicar o repositório e ligar a proteção da `main`: `tools/github/configurar_protecao.sh`.
2. PR da v3.10 do PRD. Autor: Claude; revisor: Codex.
3. Matriz de cobertura do PRD (definido / falta decidir / falta implementar / falta verificar). Autor: Claude; o Codex a converte em backlog.
4. Primeiro pull request de código, só depois do backlog priorizado e da confirmação do proprietário sobre o primeiro incremento.
