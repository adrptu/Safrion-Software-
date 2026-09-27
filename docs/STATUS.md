# Estado do projeto

Atualizado em 27/09/2026 por Claude Code (R-005). Leia este arquivo no início de cada sessão e atualize-o no fim de cada incremento (PRD 23.4).

## Onde estamos
| Frente | Estado | Evidência / local |
|---|---|---|
| PRD | **v3.9 vigente** (26/09/2026). A v3.10 está em revisão: cap. 73 (confiabilidade transacional, offline, desempenho), cap. 74 (design system) e refinamentos da comparação externa. | `docs/PRD.md`; rascunhos fora do repositório até o pull request da v3.10 |
| Fluxogramas | v3.9: 63 fluxos com raias | `docs/prd/fluxogramas/` |
| Protótipo navegável | Em validação pelo proprietário. **Não é produção.** | https://claude.ai/artifact/WPDgqGvKX6CYTCdPjidBLo |
| Repositório | Publicado em 27/09/2026 como privado: `github.com/adrptu/Safrion-Software-`, `main` em `a1f5b16`; metadados, commit e privacidade verificados pelo Codex. Não haverá repositório duplicado. | `git remote -v` |
| Código de produto | **Nenhum.** Não há backend, banco, integração ou implantação. | — |

## CI
| Job | Situação |
|---|---|
| **CI remota** | **Não executou.** A primeira execução não iniciou nenhuma etapa: a conta está bloqueada pelo GitHub, e o titular já foi avisado (informado pelo Codex, 27/09/2026). Não marcar CI verde nem mexer em plano ou cobrança; manter as verificações locais. |
| Integridade da documentação (`tools/docs/checar_docs.py`) | Executado localmente em 27/09/2026. Na CI, só depois de a conta ser liberada. |
| Varredura de segredos (Gitleaks) | Configurado; **ainda não executado** (depende da CI remota) |
| Vulnerabilidades e configuração (Trivy fs) | Configurado; **ainda não executado** |
| Código: instalação com lockfile, lint, tipos, testes, build | Configurado para ativar quando houver `package.json` e `pnpm-lock.yaml`; **não executado** |

## Bloqueios e pendências
1. **CI remota bloqueada pela conta do GitHub.** Segunda tentativa em 27/09 às 10h54 falhou antes de iniciar, com aviso de pagamentos ou limite de gastos (`actions/runs/36320502642`). A liberação da conta é com o titular; os agentes não alteram plano nem cobrança e não repetem a tentativa até a conta mudar. Nesta máquina não há `gh` nem credencial de push para o Claude.
2. **Proteção da `main`: nada aplicado.** O arquivo `tools/github/protecao-main.json` é só configuração local.
   - Segundo a documentação oficial do GitHub, consultada em 27/09/2026, proteção de branch e rulesets em repositório **privado** exigem GitHub Pro, Team ou Enterprise; na conta Free, só em repositório público.
   - **O plano real da conta não foi verificado.** Pode já ser Pro. Verificar antes de qualquer proposta; PEND-REPO-01 só se aplica se o plano for Free.
   - Enquanto isso, a disciplina é de processo: pull request, CI verde e parecer escrito do outro agente em `docs/parceria/rodadas/`. Isso **não** é proteção imposta pelo servidor.
   - Os dois agentes operam com a mesma conta `adrptu`. A revisão independente é registrada nas rodadas; não existe identidade de revisor no GitHub e não será simulada.
3. **Ferramentas locais.** Node.js e pnpm não estão no PATH comum, mas existem no runtime do Codex: Node v24.19.0 e pnpm 11.25.0, conferidos em 27/09/2026. Servem para verificação local. A instalação reproduzível do projeto não pode depender desse caminho: versões fixadas no repositório (`packageManager`, `.nvmrc`) quando houver código. Docker não confirmado.
4. **Versões da stack** a fixar no primeiro commit executável (`docs/architecture/versions.md`).
5. **Decisões pendentes do proprietário:** `docs/DECISIONS.md`.
6. **Actions da CI fixadas por SHA** em 27/09/2026, a partir da API pública do GitHub. Cada tag foi resolvida até o commit e conferida:
   - `checkout` v7.0.1;
   - `setup-python` v7.0.0;
   - `setup-node` v7.0.0;
   - `pnpm/action-setup` v6.1.0;
   - `gitleaks-action` v3.0.0: gratuita para conta pessoal; organização exige licença, o que é custo;
   - `trivy-action` v0.36.0.

   Os inputs usados foram conferidos no `action.yml` de cada SHA. O Dependabot propõe as atualizações. A execução real só acontece no primeiro push.

## Próxima etapa
Plano F0 → F1 → homologação para revisão do Codex: [R-006](parceria/rodadas/R-006-skills-ferramentas-plano.md). Correção FERR-01 da CI na branch `fix/ci-trivy-sem-correcao`.

1. Quando a conta for liberada: conferir a primeira CI remota e, se o plano permitir, ligar a proteção da `main` (`tools/github/configurar_protecao.sh`).
2. PR da v3.10 do PRD. Autor: Claude; revisor: Codex.
3. Matriz de cobertura do PRD (definido / falta decidir / falta implementar / falta verificar). Autor: Claude; o Codex a converte em backlog.
4. Depois da primeira CI remota verde: F0 (fundação verificável) em `feat/f0-fundacao`, sequência acordada na R-002/R-003 (F0 → F1 → F2 → F3 → F4 → F5). O primeiro incremento técnico foi delegado aos agentes. Dependências externas concretas continuam com o proprietário: custo e conta de homologação, dados reais, aceite de produção.
