# Revisão e integração do PR #105 (OS-LOTE), executada em 17/10/2026

- **Integrado:** HEAD `62653c9` do Codex, sobre a composição vigente.
- **Ajuste do integrador** (AGENTS §3.4, quem integra aplica o patch): `os_lote_test.py`.
  - No fluxo do teste, o foco fica no "⋯ Mais ações de OS-0596", que tem dica explícita.
  - Pelo g2lib (WCAG 1.4.13), o 1º Esc fecha só a dica e mantém o modal; o 2º fecha o modal.
  - O teste passa a verificar isso, em vez de esperar um Esc só, e o total vai de 34 para 36.
  - Comportamento conferido no código: `g2lib.js`, listener de captura "Esc fecha a dica; a dica explícita (data-dica) consome a tecla…".

| Prova | Resultado | Bruto |
|---|---|---|
| `os_lote_unit` | 104/104 | — |
| `os_lote_foco_unit` | 8/8 | — |
| Fluxo pelo teclado a 1440 e 390 (`sonda105b.py`): "Agrupar estas 3" → conferir → confirmar → aprovar 3 uma a uma → "Liberar as 3 aprovadas" | "3 liberadas · 0 pendentes" | `sonda105_390.log` |
| `os_lote_test` com o teste original da HEAD | 32/34 (só o caso do Esc com a dica aberta) | `os_lote_test.log` |
| `os_lote_test` com o ajuste | 36/36 | `os_lote_test_patch.log` |
| `paginas_scan` | 5 ok · 0 falhas (148 páginas) | `paginas_scan_test.log` |

**Na rodada anterior (705efa0), sem mudança de domínio desde então:** `os_cenario` 22/22, `kanban_raias` 9/9 e `quantidade_test` 16/16 (`artefato-v120/provas-resumo.txt`).
