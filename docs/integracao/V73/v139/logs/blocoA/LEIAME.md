# Bloco A: VIS-08 + PR #121 + PR #122 (brutos de 19/10/2026, madrugada UTC)

**Renders e caminhos servidos (efetivos):**

| Lado | Commit da fonte | Render servido |
|---|---|---|
| Composição | `5955e3db`, igual ao `d491c55e` no que gera páginas: o `d491c55e` só muda `datas_consumidores_test.py` | `/tmp/claude-0/osg/tools/prototipo/v37/gen37/_render` |
| Base (sem VIS-08) | `e1b12cd2` = `7aa910df` + PR #121 `27b36334` | `/tmp/claude-0/r121/tools/prototipo/v37/gen37/_render` |

- **O que cada teste serve:**
  - O `ben_fluxo_test` (via `cadc_lib.T`) **ignora o `RENDER_DIR`** e serve o `_render` da própria pasta. Por isso, cada lado rodou de dentro da sua pasta, com o `RENDER_DIR` apontando para o mesmo lugar.
  - O `visual_corte_test` lê o `RENDER_DIR`, que também apontava para a pasta do próprio lado.
- **Montagem:** cada render foi montado com `SAFRION_DADOS=sintetico python3 -W error::SyntaxWarning -B build.py && python3 -B montar_render.py`.

## Resultados

| Teste | Composição | Base |
|---|---|---|
| `visual_corte_test` | 145 achados (`visual_corte_test.log`) | 145 achados (`base_visual_corte_test.log`) |
| Comparação normalizada (página, largura e texto, sem os pixels) | `visual_corte_comparacao.txt`: 0 só na composição, 0 só na base, 145 iguais | — |
| `ben_fluxo_test` | 222/224 (`ben_fluxo_test.log`) | 222/224 (`base_ben_fluxo_test.log`) |
| As 2 falhas do `ben_fluxo` | M3 ("Ver na Manutenção" → `MA.dc.html#ativo=a13`) e EP-390 (`.pr-card`) | as mesmas 2 |

**Os outros testes da composição** (`resumo.txt` e os `.log` desta pasta):
- `painel03` 48/48 e `painel_agricola` 81/81;
- `ds_test` 72/72 e `ds_padrao` 17/17;
- `saf_mapa` 10/10, `cmptest` sem falha e `saf_cmp_continuidade` 31/31;
- `paginas_scan` 5/5 (146 páginas);
- os testes de unidade do PR #121 e do PR #122.

**Pendências reais do conjunto, que já existiam antes e vão para a base verde:**
- os 145 cortes do `visual_corte`, quase todos de texto na Manutenção (Sem ordem, MA, MA-01, MA-02/03);
- o M3 e o EP-390 do `ben_fluxo`.
