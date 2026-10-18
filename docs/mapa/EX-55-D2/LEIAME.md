# EX-55 D2 · revisão do Claude da extração do Codex (`codex/ex55-camadas` @ `e23f9fc8`)

Base: `29d923c7`, o pai da candidata, com o render construído no próprio commit (`SAFRION_DADOS=sintetico`). Candidata: `e23f9fc8`, com o render do mesmo modo. Integrada na composição `claude/v44-v135-osagrupa` (merge `64dfa20e`).

## A2 · paridade no navegador (executada)

- **Coletor:** `coleta_ex55.py`, que roda o `SNAPSHOT_JS` do `mapa_camadas_test.py --coletor` da candidata nas duas versões.
- **Contextos:** 60, nas duas fazendas:
  - O.S.: 4 visões × 6 fases;
  - MIP: 7 e 30 dias, sem alvo e com o 1º alvo em ordem alfabética (Antracnose);
  - Irrigação: Hoje e Balanço hídrico.
- **Página isolada do ensaio** (só nos renders de teste, nunca publicada):
  - `IN-04x.dc.html` = IN-04 + `window.__ex55e = s => eval(s)`, para ler as funções no escopo da tela;
  - `vazio-ensaio.html`, página neutra da mesma origem.
- **Defeito do coletor encontrado e corrigido:** a página anterior regravava `mapa-ctx` ao sair, e as capturas herdavam o contexto anterior. Por isso a primeira rodada deu 45 diferenças falsas. O coletor agora grava o contexto na página neutra e só então abre o Mapa.
- **Resultado:** `mapa_camadas_test.py --comparar A2_base_29d923c7.json A2_cand_e23f9fc8.json` → **`PASS paridade de 60 contextos capturados`**, 0 de 60 diferentes.
- **A comparação não é trivial:**
  - a candidata tem `MC_COR` e `mcOS` no IN-04, e a base não;
  - são 930 linhas, 9 classes e 138 rótulos distintos.

## A5 · regressão do Mapa (executada)

| Teste | Candidata `e23f9fc8` | Base `29d923c7` |
|---|---|---|
| `mapa9_test` | 13/13 | erro do CDP ("Inspected target navigated or closed") na 1ª rodada; reexecução em `A5/base` |
| `mapa_filtros_test` | 7/7 | 7/7 |
| `mapa_faixa_test` | 25/25 | ver `A5/base` |
| `mapa_mux_f0_test` | 17/17 | ver `A5/base` |
| `mapa_mux_f1_test` | 43/43 | ver `A5/base` |
| `mapa_mux_f2_test` | 29/29 | ver `A5/base` |

**Unidade (executada na composição):**
- `node mapa_camadas_unit.js` → 1251 pass;
- `mapa_camadas_test.py` → mutação 5→6 rejeitada.

**Fora deste aceite:**
- `mapa_emb.js` e os adaptadores das telas (EX-55 F1, do Claude);
- a camada Estádio "fase e idade" (EX-57).
