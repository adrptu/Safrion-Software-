## O que muda e por quê
<!-- 1–3 frases. Link da issue/ADR. O problema antes, o comportamento depois. -->

## Como testar
<!-- Passos reprodutíveis. Comandos. Dados de exemplo. -->

## Evidências
<!-- Versão/base, fontes/diff e resultados executados. UI: capturas nos contextos, temas e dispositivos pertinentes. Distinguir limitações e testes não executados. -->

## Riscos e reversão
<!-- Migração? Feature flag? Como desfazer em produção? Impacto em dados existentes? -->

## Checklist
- [ ] Self-review feito; diff só contém o assunto do PR 
- [ ] Testes novos cobrem comportamento, limites e erros; bug tem regressão
- [ ] Checks aplicáveis e exigidos aprovados; resultados vinculados à candidata
- [ ] Sem `any`/`ignore`/`skip`/código morto/duplicação
- [ ] Migração compatível e recuperação verificada; `.env.example` e docs atualizados
- [ ] UX conforme `ux-essencial`; tabelas conforme `tabelas-interativas`
