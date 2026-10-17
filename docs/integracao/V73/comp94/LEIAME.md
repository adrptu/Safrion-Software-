# Composição com o PR #94 (AGRO-02: produto e dose escolhidos explicitamente na decisão MIP)

- **Composição:** `26d7957` = `adca8ba` + merge do HEAD `2f0a1f0` do PR #94, sem conflito.
- **Revisão e reteste (Claude):** branch `claude/v44-v73-rev94`, arquivo `docs/integracao/V73/AGRO-02/revisao-claude.md`.
  - A1 e A2 foram corrigidos.
  - A sonda de navegador passou de 28/32 para 32/32.
  - A verificação 9 do `quantidade_test` abre vazia nas 10 vistorias; a contraprova feita com a base reprova.

**Testes executados no render de `26d7957`** (árvore limpa, dados sintéticos; brutos nesta pasta):

| Teste | Resultado |
|---|---|
| `agro02_selecao_unit.js` (do Codex) | 7/7 |
| `mip_unit_test.py` | 34/34 |
| `mip_fluxo_test.py` | 15/15 |
| `mip_correcoes_test.py` | 14/14 |

**O que continua aberto e não bloqueia:**
- **S4:** A3 (rótulo "Dose (/ha)" antes da escolha do produto), A4 (foco inicial no "Fechar") e A5 (o teste novo não tem invólucro `.py`).
- **O1, anterior ao PR:** o `quantidade_test` inteiro aborta em `irrTerminar`. É a fatia BASE-QTD, do Codex.
