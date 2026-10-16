# PR #76: brutos da correção do cartão do `section()`

**Correção (bf19d26):** `min-height: auto` no cartão do `engine.section()`. O teste S4 entrou no `paginas_scan_test.py`.

**Composição para revisão (9434f72, a candidata atual):** merge da ponta bf7d8b6 da `claude/v44-v69-mapa`, sem rebase, pedido no comentário 6220286112 do PR #47. A composição anterior era eefecc4, com b87f79b, pedida no comentário 6219215674.

Tudo aqui foi **executado** em Chrome headless (`comp_lib.Chrome`, emulação, não é aparelho físico), com render sintético (`SAFRION_DADOS=sintetico`, 156 páginas) e só dados sintéticos.

## Como reproduzir

Build de cada commit (em uma worktree por commit):
```
cd tools/prototipo/v37/gen37 && SAFRION_DADOS=sintetico python3 -W error::SyntaxWarning -B build.py && SAFRION_DADOS=sintetico python3 -B montar_render.py
```
Variáveis comuns: `L='env CHROME_BIN=<chrome com --no-sandbox> CDP_GL=1 SAFRION_DADOS=sintetico'`. Na nuvem, `/tmp/cloudchrome/chrome` chama `/opt/pw-browsers/chromium --no-sandbox`.

Comandos do teste e da contraprova (de `gen37/`):
```
$L RENDER_DIR=<_render> python3 -B paginas_scan_test.py
$L DS_RENDER=<_render> python3 -B ds_test.py
```

Medidas, de `docs/integracao/V71/pr76/scripts/` (o `_base.py` acha o `gen37` pelo caminho do repositório):

| Script | O que faz |
|---|---|
| `inventario.py <_render>` | Lista as caixas de borda 16 px no `main` com o conteúdo passando da borda (`scrollHeight > clientHeight + 2`). |
| `retrato.py <_render> <saida.json>` | Mede `main`, filhos, cartões e áreas que rolam por dentro, nas 156 páginas × 2 tamanhos. |
| `compara.py <antes.json> <depois.json>` | Lista as diferenças entre dois retratos. |
| `fotos.py <_render> <rótulo> <dir> TELAS…` | Tira as fotos roladas até o fim, em 1440 × 900 e 390 × 844. |
| `tempo_co06det.py` e `tempo_390.py` | Repetem a medida 0 s, 1,5 s e 3 s depois de carregar, para separar instabilidade de efeito. |

## Rodada 3: base bf7d8b6 × composição 9434f72 (pasta `r3-bf7d8b6-9434f72/`)

**Candidata atual: 9434f72.** É o merge da ponta bf7d8b6, sem rebase, pedido no comentário 6220286112 do PR #47. A bf7d8b6 traz a frente CADASTROS-PADRAO (eabc4a3), com código executável: `ui37.py` (item de menu do Crédito), `areas/cad_*`, `areas/gestao.py` e testes, inclusive `ds_test.py` e `cadf_fix_lista_test.py`.

Esta rodada repete só as provas afetadas. As demais continuam valendo pela rodada 2.

**HEAD 2d5de61** junta também a ponta dee9dbe1, sem rebase. De bf7d8b6 a dee9dbe1 só mudaram `docs/integracao/V71` e `visoes_v23_codex_test.py`. O build sintético da 2d5de61 é idêntico, byte a byte, ao da 9434f72 (`render_2d5de61_igual_9434f72.txt`: `diff -rq` sem saída, 181 arquivos). Por isso, as provas desta rodada valem para a 2d5de61.

### Inventário e retrato do layout
| Medida | Resultado | Arquivo |
|---|---|---|
| Inventário | 29 telas na base bf7d8b6, 0 na composição | `inventario_bf7d8b6.txt`, `inventario_9434f72.txt` |
| Retrato | 29 diferenças em 312 | `compara_bf7d8b6_9434f72.txt` |

As 29 diferenças são exatamente as 29 telas em 1440 px. Não há diferença em 390 px nem em nenhuma tela de Cadastros (CD-*).

### Testes
Saídas em `resumo_testes.txt` e um `.log` por teste.

| Teste | Composição 9434f72 | Base bf7d8b6 |
|---|---|---|
| `paginas_scan_test.py` | 5 ok · 0 falhas; S4 com 470 cartões | S4 **reprova** (contraprova atual) |
| `cadastros_padrao_test.py` | 44/44 | 44/44 |
| `cadf_fix_lista_test.py` | 11/11 | não rodado |
| `ds_test.py` | 69/72 (D13, D15, E2) | 69/72 (D13, D15, E2) |

## Rodada 2: base b87f79b × composição eefecc4 (pasta `r2-b87f79b-eefecc4/`)

### Inventário
| Render | Cartões espremidos | Arquivo |
|---|---|---|
| Base b87f79b | 29 telas em 1440 px, 0 em 390 px | `inventario_b87f79b.txt` |
| Composição eefecc4 | 0 | `inventario_eefecc4.txt` |

### Retrato do layout
Arquivos: `retrato_b87f79b.json`, `retrato_eefecc4.json` e `compara_b87f79b_eefecc4.txt`. Resultado: 32 diferenças em 312 combinações de página e tamanho.

- **1440 px:** mudam exatamente as 29 telas do inventário.
  - Os cartões espremidos voltam à altura do conteúdo.
  - Onde havia sobra, ela se redistribui entre os cartões (PT-03, CO-05det e PT-04det).
  - OS, SAF e CD-01 ficam iguais.
- **390 px:** CA-01x-os0420, CA-03det e PL-03 aparecem como diferentes, mas é instabilidade da medida.
  - Em `tempo_390.txt`, os dois renders dão a mesma sequência.
  - CA-01x vai de 267 a 284 px e CA-03det de 366 a 306 px, conforme o tempo depois de carregar.
  - PL-03 fica estável e igual nos dois.
  - Na rodada 1, a diferença em 390 px foi a CO-06det, pelo mesmo motivo (`tempo_co06det.txt`).

### Testes
Saídas em `resumo_testes.txt` e um `.log` por teste.

| Teste | Composição eefecc4 | Base b87f79b |
|---|---|---|
| `paginas_scan_test.py` | 5 ok · 0 falhas; S4 com 470 cartões | S4 **reprova** (contraprova); por exemplo, `CO-01 0/220 px` |
| `acao_unica_test.py` | 10/10 | não rodado |
| `cadf_fix_lista_test.py` | 11/11 | não rodado |
| `ds_1510_test.py` | 17/17 | não rodado |
| `ds_1610_test.py` | 14/14 | não rodado |
| `ds_padrao_test.py` | 17/17 | não rodado |
| `ds_unit_test.py` | 44/44 e 31/31 | não rodado |
| `ds_test.py` | 69/72 | 69/72, com as mesmas D13, D15 e E2 |

As falhas D13, D15 e E2 do `ds_test.py` já existiam antes desta mudança e não são tratadas neste PR.

### Fotos
Pasta `fotos/`: CO-07, PL-01, VE-01, VE-02 e VE-04 em 1440 e 390 px, rótulo `antes` para b87f79b e `depois` para eefecc4.

## Rodada 1: base d482a07 × correção bf19d26 (pasta `r1-d482a07-bf19d26/`)

São os números citados no corpo do PR, medidos antes do merge da base.

| Arquivo | O que contém |
|---|---|
| `inventario_d482a07.txt` | 29 telas em 1440 px. |
| `retrato_d482a07.json`, `retrato_bf19d26.json` | Retrato de cada render. |
| `compara_d482a07_bf19d26.txt` | 30 diferenças: as 29 telas e a CO-06det em 390 px (instabilidade). |
| `paginas_scan_bf19d26.log` | 5 ok, 0 falhas. |
| `paginas_scan_RENDER_DIR_d482a07.log` | Contraprova: S4 reprova. |
| `*_bf19d26.log`, `ds_test_DS_RENDER_d482a07.log` | Testes afetados, com os mesmos números da rodada 2. |
| `fotos/` | CO-07, PL-01, VE-01 e VE-02 em 1440 e 390 px, e VE-04 em 1440 px. |

Na rodada 1, os scripts foram usados com caminhos fixos do scratchpad. As versões em `scripts/` são as mesmas medidas, com caminhos relativos ao repositório.
