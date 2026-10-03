## O que muda e por quê
<!-- 1–3 frases. Link da issue/ADR. O problema antes, o comportamento depois. -->

## Como testar
<!-- Passos reprodutíveis. Comandos. Dados de exemplo. -->

## Evidências
<!-- Capturas/vídeo para UI (claro e escuro, mobile e desktop). Saída resumida dos testes. -->

## Riscos e reversão
<!-- Migração? Feature flag? Como desfazer em produção? Impacto em dados existentes? -->

## Checklist
- [ ] Self-review feito; diff só contém o assunto do PR (< 400 linhas)
- [ ] Testes novos cobrem comportamento, limites e erros; bug tem regressão
- [ ] `lint` · `typecheck` · `test` · `build` verdes localmente
- [ ] Sem `any`/`ignore`/`skip`/código morto/duplicação
- [ ] Migração reversível; `.env.example` e docs atualizados
- [ ] UX conforme `ux-essencial`; tabelas conforme `tabelas-interativas`
