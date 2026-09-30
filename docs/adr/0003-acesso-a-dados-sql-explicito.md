# ADR 0003: Acesso a dados com SQL explícito na fundação (sem Prisma por ora)

- **Situação:** implementada na `main` desde o PR #7 (SQL explícito com `pg`). Aceita em 29/09: parecer técnico favorável do Codex e parecer documental favorável do Gemini, na revisão do PR #16.
- **Data:** 2026-09-27
- **Autor:** Claude Code
- **Revisores:** Codex (parecer técnico) e Gemini (parecer documental), favoráveis em 29/09, na revisão do PR #16
- **Autorização:** decisão técnica delegada aos agentes (DEC-2709-01).

## Contexto
O PRD (cap. 23) cita Prisma no padrão de implementação nova e admite trocar componente por ADR que demonstre os mesmos controles. A F0-b é a camada que garante esses controles: isolamento por organização com RLS forçado (ENG-025), organização fixada por transação (ENG-021), unicidade da intenção com espera limitada na inserção da mesma chave (IDEM-12, IDEM-15), efeito desfeito por savepoint quando a regra de negócio recusa e só o resultado fica registrado (73.3.4), fato imutável por permissão e gatilho (ENG-026), e chaves estrangeiras compostas com a organização, porque a conferência de chave estrangeira não passa pelo RLS.

## Decisão
- A F0-b usa **SQL explícito** com o driver `pg`: migrações em arquivos `.sql` versionados com SHA-256, e consultas parametrizadas nas funções do pacote `@safrion/db`.
- Cada comando roda numa transação de conexão dedicada, controlada pelo código: `set_config` local, `lock_timeout` só na inserção da chave, `SAVEPOINT` do efeito e COMMIT único do efeito, do registro, do recibo, da auditoria e da outbox (ENG-022).
- Um ORM ou gerador de consultas pode entrar depois, por novo ADR, se passar nos mesmos testes de integração sem enfraquecer nenhum desses pontos.

## Alternativas consideradas
| Alternativa | Por que não agora |
|---|---|
| Prisma | Transação interativa com `SET LOCAL`, savepoint e trava limitada passaria por SQL cru dentro do ORM, e as políticas RLS, gatilhos e chaves compostas continuariam em SQL de migração. Acrescenta motor, geração de código e uma segunda linguagem de esquema sem reduzir o SQL que precisa ser revisado. |
| Gerador de consultas tipado (Kysely, Drizzle) | Possível mais adiante para consultas de leitura; não muda o controle transacional e ainda não há volume de consultas que o justifique. |

## Consequências
- O SQL das migrações é a fonte do esquema. O revisor lê um arquivo só para ver tabelas, políticas, permissões e gatilhos.
- Tipos das linhas lidas são declarados à mão nas funções. Erro de digitação em coluna aparece nos testes de integração, não no compilador.
- A prova de isolamento, idempotência e imutabilidade fica nos testes de integração com PostgreSQL real (`pnpm run test:integration`).

## Verificação
- Testes de integração da F0-b verdes na CI, com o papel `app_runtime`, contra PostgreSQL 17 + PostGIS 3.5 fixado por digest.
- Provas negativas registradas no PR: FORCE removido de uma tabela, organização fixada na sessão inteira, hash não conferido, inserção sem `ON CONFLICT` e savepoint não desfeito; cada uma reprovada pelo teste correspondente.

## Adendo de 30/09/2026 (contrato CMD-15 §9.3)
- O `lock_timeout` da inserção da chave passa a valer também para o efeito, na mesma transação. Ele substitui, só nesse ponto, o "`lock_timeout` só na inserção da chave" da Decisão. O resto desta ADR não muda.
- O limite vale para cada espera por trava, não para a duração do efeito, da transação ou da resposta. Reduz a espera indefinida por travas; não limita a espera total.
- Trava que passa do limite (55P03) com o ROLLBACK confirmado antes do COMMIT vira `FALHA_TRANSITORIA` com `resultadoIncerto: false` e `repetirEmMs`, sem repetição automática. ROLLBACK que falha ou COMMIT já enviado continuam dando resultado incerto. A espera pela chave em outra transação continua `IDEMPOTENCY_IN_PROGRESS`.
- Nas tentativas repetidas, o `statement_timeout` por comando (CMD-15 §6, v3.9) pode vencer antes e dar 57014, com a semântica de prazo que já existe.

