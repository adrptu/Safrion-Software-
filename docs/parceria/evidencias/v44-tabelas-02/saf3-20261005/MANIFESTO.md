# TABELAS-FOCO-20261004 v2 (5983172395) · incremento 2a: Planejar safra, etapa 3 — evidência executada

- Branch `claude/v44-tabelas-02`, base `5ad4cad` (incremento 1, PR #40), reserva `cd7c511`. Dados sintéticos.
- `tabelas_saf_test.log` — `python3 tabelas_saf_test.py` → **14/14** (cabeçalhos; nenhuma célula com duas medidas; árvore preservada; R$/kg só na colheita; filtro por valor exato em Operação, Modo, Largura e Planos; ordenação numérica; edição recalcula a linha; 390 px).
- `bateria/` + `00-bateria.sh` — bateria completa (101 passos). Mesmo conjunto de 13 logs com saída ≠ 0 que a bateria do incremento 1 (`v44-tabelas-01/tf-20261005/bateria`), todos anteriores; só entra `tabelas_saf_test` (novo).
- `rend_multiconjuntos_test` fluxo 16/16 · telas 5/5 · bordas 10/10 · bordas2 5/5: o teste lê as colunas novas por um adaptador (`LEG`) que remonta as 6 células antigas; as asserções não mudaram.
- `tf05-inventario.md/.json` — inventário refeito com a heurística ajustada (unidade entre parênteses e mês não são rótulo composto) e a coluna "Menu".
- `capturas/` — etapa 3 a 1440 e 390 px.

## Limites
- `saf38test` e `psfix38test` quebram na mesma linha da base (anteriores a este incremento).
- Fica para o incremento 2b: as outras etapas do SAF (Plano e ajustes, plano operacional, recursos, demanda) e as demais 41 grades suspeitas do menu.
