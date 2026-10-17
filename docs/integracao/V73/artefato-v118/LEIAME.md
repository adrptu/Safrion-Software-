# Recibo da publicação do artefato v118/v119 (17/10/2026): prévia com o OS-LOTE (PR #105)

- **Artefato:** https://claude.ai/artifact/HqspGRcrX1wcayCVMe9emm. A publicação foi em dois envios:
  - v118 (`1792233331-0520`, 42 páginas);
  - v119 (`1792233349-ac59`, 18 páginas), que é o estado completo.
- **Origem:** prévia `0e13b19`, montada da composição `8a35f21` com o PR #105 (HEAD `3f6be1d`, do Codex), em revisão. Segue o regime leve (AGENTS §3.5) e o pedido do proprietário de pôr no artefato tudo o que está em andamento.
- **Branch única:** `claude/prototipo-v44` = `d83c055`.
- **Por que não está na composição:** o `os_lote_test` (navegador do OS-LOTE-F1) ficou com o oráculo obsoleto, porque procura as caixas de seleção que saíram. A integração espera o Codex portar o teste (6232844478).
- **Provas executadas na prévia** (`provas/`):

  | Prova | Resultado |
  |---|---|
  | `os_lote_unit` | 101/101 |
  | Fluxo pelo teclado a 1440 e 390 (`sonda105b.py`): calda proposta → conferir → confirmar → aprovar 3 uma a uma → liberar as 3 | "3 liberadas · 0 pendentes" |
  | `os_cenario` | 22/22 |
  | `kanban_raias` | 9/9 |
  | `quantidade_test` | 16/16 |
  | `paginas_scan` | 5 ok · 0 falhas (148 páginas) |
  | `os_lote_test` | rc=1, com oráculo obsoleto |

- **Conferência executada:** leitura de volta da v119 com sha256, 4 de 4 iguais. As páginas foram OS, MA, SAF e IN-04.
- **Manifesto:** as 60 páginas reenviadas.
