---
name: dev-revisao
description: Revise código, diffs e PRs por correção, segurança, clareza e evidência. Use em autorrevisão, revisão independente e configuração de checks; mantenha achados reproduzíveis e o escopo da mudança.
---

# Revisão de código — correção, clareza e evidência

## Vincular parecer à candidata

Confira base, autoria, arquivos, dependências e versão exata antes da revisão; leia fontes recuperáveis, diff e saídas brutas pertinentes. Hash sem fonte não permite revisar; relato do autor, teste proposto e resultado verificado são evidências diferentes. Em PRs empilhados, declare a ordem de integração e revise novamente apenas o delta material após rebase/retarget.

Reproduza o comportamento afetado e os contraexemplos relevantes. Consolide um retorno por candidata, com versão, cenário, impacto, localização, severidade do projeto, prioridade separada e aceite observável. Não transforme preferência em bloqueio. Ao chegar correção, confira o novo delta e reteste o afetado, preservando provas equivalentes válidas. Ninguém aprova ou integra o próprio PR quando a revisão cruzada for exigida.


Aplicar ao diff e seus riscos. Reutilizar ferramentas do projeto; os assets são exemplos a validar, não uma lista de dependências obrigatórias. Não abrir uma refatoração ampla para satisfazer preferências estilísticas.

## Fluxo
1. **Self-review** — antes de abrir o PR, ler o diff inteiro como revisor hostil, com o checklist abaixo. Rodar os checks existentes aplicáveis à mudança e os exigidos pelo projeto.
2. **PR focado** — um assunto revisável; tamanho é sinal de complexidade, não limite que obriga a fragmentar uma mudança coerente. Template: [assets/PULL_REQUEST_TEMPLATE.md](assets/PULL_REQUEST_TEMPLATE.md).
3. **Automação bloqueante**: cumprir os checks exigidos e pertinentes. Formatação, tipos, testes, build e verificações de segurança são opções segundo o risco; não instalar ferramentas ou ampliar infraestrutura por rotina.
4. **Revisão humana/agente** com [assets/checklist-revisao.md](assets/checklist-revisao.md). Usar a escala de severidade do projeto e distinguir defeito, sugestão e preferência; prioridade de trabalho é outro eixo.
5. Merge conforme a política e autorização do projeto; não publicar, mesclar ou apagar branch só por seguir este checklist.

Ao revisar como agente: ler o código de verdade (não só o diff), executar os testes, procurar o que **falta** (erro não tratado, caso limite, permissão), e reportar cada achado com arquivo:linha, cenário concreto de falha e correção sugerida. Não aprovar com pipeline vermelho.

## Código limpo — regras não negociáveis
- **Nomes revelam intenção**: `diasAteVencimento`, não `d`; funções com verbo, booleanos com `is/has/pode`. Sem abreviação obscura.
- **Funções coesas**, com nomes e parâmetros claros. Tamanho/aninhamento orientam a revisão; não extrair funções nem criar abstrações apenas para cumprir contagens.
- Preferir fluxo legível e saídas antecipadas quando simplificam o raciocínio.
- **Imutabilidade por padrão** (`const`, spread, `readonly`); sem mutação de parâmetro.
- **Sem números/strings mágicos**: constantes nomeadas ou enums.
- **DRY com juízo**: duplicação de conhecimento é proibida (regra dos 3 → extrair); duplicação acidental de código parecido com significados diferentes é tolerada. Abstração precisa de ≥ 2 usos reais.
- **Sem código morto**: funções, imports, flags, arquivos, dependências, código comentado. Ferramenta: knip / vulture / `deadcode`.
- **Comentários explicam o porquê**, não o quê. Sem comentário óbvio, sem histórico em comentário (isso é do git).
- **Erros**: nunca engolir (`catch {}`), nunca `console.log` como tratamento; erros tipados de domínio; mensagem para o usuário ≠ mensagem de log.
- **Tipos estritos**: sem `any`, `as` forçado, `!` não-nulo sem prova, `@ts-ignore`, `# type: ignore`. Tipos vindos do schema (zod/pydantic) na borda.
- **Dependências**: adicionar só com motivo; preferir a plataforma; verificar manutenção, tamanho, licença; versão fixada.
- **Sem otimização prematura** — mas sem N+1, sem loop O(n²) em lista que cresce, sem carregar tudo em memória.

## Ferramentas por stack (configurar na fundação do projeto)
| Stack | Formatação | Lint / estática | Tipos | Extras |
|---|---|---|---|---|
| TS/JS | Prettier | ESLint flat config: `typescript-eslint` **strict-type-checked**, `eslint-plugin-sonarjs`, `unicorn`, `import-x`, `jsx-a11y`, `react-hooks` | `tsc --noEmit` com [assets/tsconfig.strict.json](assets/tsconfig.strict.json) | knip (morto), jscpd (duplicação), `npm audit`/osv-scanner, gitleaks |
| Python | Ruff format | Ruff (regras `ALL` com exclusões justificadas), Bandit (via Ruff `S`) | mypy `--strict` ou pyright strict | vulture, pip-audit |
| Go | gofmt/goimports | golangci-lint (govet, staticcheck, errcheck, gosec, revive) | compilador | govulncheck |
| Kotlin | ktlint | detekt | compilador | — |
| Swift | swift-format | SwiftLint | compilador | — |
| Todos | EditorConfig | Semgrep (regras OWASP), CodeQL (GitHub) | — | Renovate/Dependabot semanal, commitlint |

Prontos: [assets/eslint.config.js](assets/eslint.config.js), [assets/tsconfig.strict.json](assets/tsconfig.strict.json), [assets/lint-staged.config.js](assets/lint-staged.config.js) (pre-commit com husky: `npx husky init` e no hook `npx lint-staged`).

Cumprir a política de warnings do projeto; configurar regras relevantes de forma consistente. Exceções precisam de motivo concreto e revisão, sem desativar checks para ocultar defeitos. Uma mudança global justificada de configuração não é automaticamente proibida.

## O que o revisor procura (resumo do checklist)
1. **Correção**: faz o que a tarefa pede? Caso limite, nulo, vazio, concorrência, timezone, arredondamento?
2. **Erros**: toda falha externa tratada com timeout, retry adequado e mensagem útil? Transação onde precisa?
3. **Segurança**: entrada validada na borda, autorização em todo endpoint, sem injeção, sem segredo, sem PII em log.
4. **Testes**: existem, testam comportamento, cobrem erro/limite, são determinísticos?
5. **Legibilidade**: entendo em uma leitura? Nomes? Tamanho? Duplicação? Código morto?
6. **Desempenho**: N+1, índices, paginação, memória, bundle.
7. **Compatibilidade**: migração compatível e recuperação testada sem perda indevida, API retrocompatível, feature flag, dados existentes.
8. **Produto**: segue `ux-essencial` / `tabelas-interativas`; textos pt-BR.
