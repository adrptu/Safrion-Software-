# PR #124 (EX-53 F1c, Codex): revisão do Claude no navegador (19/10/2026)

- **Render testado:** a composição local `f44ab371` + o PR #124 `2636b9f4` + o ajuste de oráculo `dfd9022e`. A árvore `tools/` é idêntica à de `ccc6f7a6` em `claude/v44-v135-osagrupa`.
- **Servido de:** `/tmp/claude-0/f1a/tools/prototipo/v37/gen37/_render` (pasta do próprio teste).

| Teste | Resultado |
|---|---|
| `ex53_f1c_test` (HEAD, `--base 2636b9f4`) | PASS; no `d491c55e` reprova (contraprova) |
| `inteligencia_unit` | 35/35 |
| `intel03_unit` | 28/28 |
| `inteligencia_nav_test` | 28/28 com o oráculo ajustado (`inteligencia_nav_test2.log`). Rodado da pasta da composição antiga `d491c55e`, reprova (`contraprova_inteligencia_nav_d491.log`) |
| `intel03_nav_test` | 37/37 |
| `mapa_mux_f2_test` | 29/29 |
| `mapa_filtros_test` | 7/7 |
| `ds_test` | 72/72 |
| Prova focal (`f1c_focal.log`, 1440 e 390 px) | OK. No IV, o selo do cabeçalho e o indicador "Vendas abaixo da referência" dizem o mesmo número (1, Mamão −1,6%). "Meta não configurada" aparece uma vez em Preço × mercado e em Preço por insumo. Nenhuma diferença à referência fica vermelha. Mapa › Custos (Realizado × previsto): a legenda não tem limite fixo e o valor negativo leva o menos tipográfico. Nenhuma tela rola na lateral |

**Linhas do `resumo.txt` que não valem:**
- `f1c_focal` com "4 falha(s)": a primeira rodada da prova focal tinha dois defeitos do script. Não trocava o Mapa para "Realizado × previsto" e lia o indicador sem o número. Corrigido o script, a rodada final deu OK.
- `inteligencia_nav_test` 27/28: o oráculo antigo esperava "0 abaixo", pela regra de −5% que o PR retirou.

**Fotos (`fotos/`), conferidas:** IV, IC e Mapa › Custos em 1440 e 390 px.
