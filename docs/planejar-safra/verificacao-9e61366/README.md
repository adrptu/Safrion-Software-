# Saídas brutas da bateria SAF (commit 9e61366, "SAF: correções da revisão")

Resposta ao pedido do Codex no adendo SAF-C02 (comentário 6079770308 do PR #47): apontar os logs já executados e a base deles, sem repetir testes por transporte.

## Onde e quando rodaram (executado)

- **Quem executou:** o agente de correção do SAF (revisão interna Claude), na worktree `claude/v44-saf`, em 06/10/2026, entre 04:07 e 06:19 UTC.
- **Árvore testada:** a árvore de trabalho que virou o commit `9e61366` às 06:23:58 UTC, com pai `7cd152d`.
- **Navegador:** headless, um teste por vez, com o lock do Chrome.
- **Script da bateria:** `roda_saf.sh`; os caminhos de máquina foram trocados por `<scratchpad>` e `<sp-saf>`.
- **Resumo da bateria:** `logs/resumo.txt`, com o horário de início de cada teste e o código de saída.

| Teste | Resultado | Horário (UTC) | Log |
|---|---|---|---|
| `capacidade_unit.py` | 76 OK · 0 FALHA | 04:07 | (saída no relato do agente; não salvo em arquivo) |
| `ocupacao_test.py` | 65 ok · 0 falhas | 04:29 | `logs/ocupacao_test.log` |
| `saf_operacoes_test.py` | 87 ok · 0 falhas | 04:35 | `logs/saf_operacoes_test.log` |
| `tabelas_saf_test.py` | 24/24 | iniciou 04:43:17, durante a edição e o rebuild de 04:43:39–04:43:55; conta como "antes" | `logs/tabelas_saf_test.log` |
| `saf_revisao_test.py` | 42 ok · 0 falhas | 04:44 | `logs/saf_revisao.log` |
| `rend_multiconjuntos_test` (fluxo, telas, bordas, bordas2) | 18/18 · 5/5 · 9/9 · 5/5 | 04:46–04:56 | `logs/rend_*.log` |
| `ocupacao_test.py` (repetição) | 65 ok | 04:54 | `logs/ocupacao_test_2.log` |
| `partest.py` | 45 ok · 2 falhas, depois 46 ok · 1 falha após a mudança de expectativa | 05:09 e 06:19 | `logs/partest.log`, `logs/partest2.log` |
| `saf_cmp_continuidade_test`, `acao_unica` (saf, v3, gemini), `etapas_celular`, `cmptest`, `tabelas_os_test`, `tabelas_est_test` | ver `resumo.txt` | 05:13–05:51 | `logs/*.log` |
| `saf38test`, `psfix38test`, `testes_pedido` | vermelhos pelo motivo antigo da base | 05:41–05:58 | `logs/*.log` |
| `varredura.py` | 144/144 | 06:12 | `logs/varredura.log` |

## Limites (para não exagerar a prova)

1. **Edições depois de parte da bateria.** Às 04:43 o agente editou duas funções de tela em `safra.js`: `cultAfter` e o trecho de `normCult`, para corrigir "o grupo recolhia e o cultivo novo sumia".
   - Rodaram **antes** dessa edição e **não foram repetidos depois**: `capacidade_unit` (04:07), `saf_operacoes_test` (04:35) e `tabelas_saf_test` (iniciado 04:43:17). O `ocupacao_test` também rodou antes (04:29), mas foi repetido depois (04:54).
   - O bloco CAPACIDADE não foi tocado por essa edição. Mesmo assim, `saf_operacoes_test` 87/87 não prova o estado final de `9e61366`.
2. **Nenhum desses testes rodou na `ecc8b00` integrada.** A `ecc8b00` é o merge do SAF com a Colheita. Nela foram executados só:
   - `build.py` com 0 FALHA;
   - `montar_render.py` com 140 páginas;
   - `varredura.py`: 139/140 sob carga, depois 140/140 com a espera corrigida em `16d6734`.

   As verificações de regressão das frentes SAF-C01 e SAF-C02 rodam `capacidade_unit`, `saf_operacoes_test`, `saf_revisao_test` e outros na base `ecc8b00`/`16d6734` e no HEAD de cada correção. Essas saídas vão em `docs/planejar-safra/verificacao-saf-c01/` e `docs/planejar-safra/verificacao-saf-c02/`.
3. **O que as pastas `verificacao/` mais antigas cobrem.** As pastas `etapa-2-talhoes/verificacao/` (base `884620c`) e `etapa-unica-3-4-5/verificacao/` são sondas da especificação v2. Valem como prova do desenho, não da implementação.
