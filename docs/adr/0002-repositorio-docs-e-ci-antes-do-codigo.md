# ADR 0002: Repositório privado com documentação e CI antes do código de produto

- **Situação:** aceita
- **Data:** 2026-09-27
- **Autor:** Claude Code
- **Revisor:** Codex (pendente)
- **Autorização:** proprietário, 27/09/2026. Resposta direta dele: "Sim, docs + CI" e "Conta pessoal, privado".

## Contexto
Até 27/09/2026, a regra do proprietário era validar primeiro o protótipo e o PRD e só iniciar o software real por comando explícito. Em 27/09 ele autorizou preparar o repositório com documentação, estrutura de desenvolvimento, CI e proteção da branch principal, para o trabalho conjunto entre Claude e Codex.

## Decisão
- **Repositório privado** na conta pessoal do proprietário no GitHub.
- **Conteúdo inicial:** PRD vigente, fluxogramas, decisões, instruções dos agentes (`AGENTS.md` como fonte única; `CLAUDE.md` importa esse arquivo), protocolo de parceria, modelos de issue e de pull request, e CI.
- **A CI começa pelo que já pode rodar sem código:** integridade da documentação, varredura de segredos e varredura de vulnerabilidades e configuração. Os jobs de código (instalação com lockfile, lint, tipos, testes e build) ativam sozinhos quando o primeiro pull request com `package.json` e `pnpm-lock.yaml` entrar.
- **Ficam fora sem nova autorização:** provisionamento de nuvem, integração real com ERP, dados reais de clientes e publicação de produção.

## Alternativas consideradas
| Alternativa | Por que não |
|---|---|
| Criar o esqueleto completo de apps e pacotes já | Criaria pacotes sem responsabilidade real (PRD 23.3) e configurações não verificadas; nesta máquina não há Node/pnpm para validar |
| Repositório público | Não há decisão de publicação; o proprietário escolheu privado |

## Consequências
- Nenhum job de código é declarado aprovado antes de rodar de fato.
- A proteção da `main` e a revisão obrigatória dependem da conta e das identidades reais no GitHub (ver `docs/STATUS.md`, bloqueios).

## Verificação
- CI verde nos jobs ativos no primeiro push.
- Configuração da proteção de branch conferida pela API do GitHub e registrada em `docs/STATUS.md`.
