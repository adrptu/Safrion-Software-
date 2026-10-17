# Composição com o PR #95 (AGRO-06, entrada dos 15 analitos do laudo)

- **Composição:** `2cd317d` = `6631d58` + merge do HEAD `74f13a6` do PR #95. O merge não teve conflito.
- **Revisão e reteste:** feitos pelo Claude, em `claude/v44-v73-rev95`, arquivo `docs/integracao/V73/AGRO-06/revisao-claude.md` (§6).
  - Os achados A1–A4 estão corrigidos.
  - Reteste no navegador: 16/16. Na versão anterior, `a10656a`, o mesmo roteiro reprova 14 dos 16.

## Testes executados no render de `2cd317d`

Render de árvore limpa, 156 páginas, dados sintéticos. Os brutos estão nesta pasta.

| Teste | Resultado |
|---|---|
| `agro06_analitos_unit.js` (teste do Codex) | PASS |
| `solo_unit_test.py` | 129/129 |
| `solo_ag02_test.py` (desktop e celular) | 32/32 |
| `solo_regressao_test.py` | 2/2 |

## Fica para a composição seguinte (S4, não bloqueia)

- Seta da TAB-11 nos summaries "Método e limites".
- Trocar a cor fixa `#5B6660` pelo token `MUTED`.
- O A5 (pH em H₂O lido pela régua de CaCl₂) vai na SOLO-UNID, do Codex.
