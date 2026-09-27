# Estado do projeto

Atualizado em 27/09/2026 por Claude Code. Leia este arquivo no início de cada sessão e atualize-o no fim de cada incremento (PRD 23.4).

## Incremento em revisão — Codex, 27/09/2026

- Branch `fix/codex-contrato-ci-tipos`: o portão de código rejeita tipos inválidos no manifesto e exige comandos textuais não vazios. O restante deste documento conserva o registro anterior do projeto.
- Verificação local executada: 14 testes passaram; os novos casos reproduziram 55 falhas de subtestes antes da correção. Código e testes publicados conferidos com os arquivos executados.
- Pendente: revisão crítica do Claude e CI remota da candidata. Este incremento não entrega aplicação ou acesso de homologação e não altera os ajustes de Gitleaks/Trivy.

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
1. **Publicar no GitHub.** Usuário `adrptu`, confirmado pelo conector do Codex. Nome `do-talhao-a-os`, privado. Publicação aprovada pelo Codex na R-003, só para executar a CI (não é aceite de produto). O Codex publica pelo GitHub Desktop. Nesta máquina não há `gh`.
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
1. Publicar o repositório e ligar a proteção da `main`: `tools/github/configurar_protecao.sh`.
2. PR da v3.10 do PRD. Autor: Claude; revisor: Codex.
3. Matriz de cobertura do PRD (definido / falta decidir / falta implementar / falta verificar). Autor: Claude; o Codex a converte em backlog.
4. Depois da publicação e da primeira CI verde: F0 (fundação verificável) em `feat/f0-fundacao`, sequência acordada na R-002/R-003 (F0 → F1 → F2 → F3 → F4 → F5). O primeiro incremento técnico foi delegado aos agentes. Dependências externas concretas continuam com o proprietário: custo e conta de homologação, dados reais, aceite de produção.
