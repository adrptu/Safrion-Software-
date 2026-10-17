# Integração do PR #93 (EX-47a: ações da linha no menu ⋯ sem depender de Excluir)

- **Autor:** Codex. **Revisor e integrador:** Claude.
- **Composição:** `4fd5b8b` = `613bda6` (com o #94) + merge do HEAD `4cbfa71`. Sem conflito: o #93 mexe só no `engine.py` e no `g2lib.js`, e o #94 em outros arquivos.
- **Revisão e reteste:** `docs/integracao/V73/EX47/revisao-claude.md`, §7 "Reteste 4cbfa71", trazido para a composição no merge `5a2c20e`. A1 e A2 foram corrigidos; o parecer é favorável.
- **Bateria no render de `4fd5b8b`:** dados sintéticos, navegador com portão de 1 Chrome. Os brutos estão nesta pasta.

| Teste | Resultado |
|---|---|
| rmenu_unit · rmenu_generator_test | OK · OK |
| rmenu_alignment_test (base do g2lib em 6631d58) | 561 OK, 0 falhas |
| agro02_selecao_unit · mip_unit_test (#94) | 7/7 · 34/34 |
| rev93_reteste_navegador (sonda Claude) | 44 OK, 0 falhas |
| tabelas_saf · saf_tab · cartoes | 24/24 · 14/14 · 70/70 |
| ds_1510 · mip_fluxo (#94) | 17 ok · 15/15 |

**O que fica fora desta integração:** o A3 é opcional; O1, O2 e O3 ficam para tarefas separadas, como está na revisão.
