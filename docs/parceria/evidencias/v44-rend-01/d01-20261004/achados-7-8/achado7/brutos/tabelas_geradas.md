### T1. Reprodução nos três commits (JS = bloco REPARTIR de safra.js; Python = dados2.repartir)

Buraco: `grafo:resultado/passos` (p = plano, a = divisão; a 1ª chamada é o grafo, a 2ª o complemento). V3 = verificador independente (θ* ≥ 1 executável).

| Caso | Commit | buraco | Caminho | Alocado (ha) | Saldo (ha) | Déficit (h) | Conflito | Python Fraction (alocado; saldo; déficit) | V3 θ* | JS ms (3 exec.) | Py ms | JS=Py |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 5x6 partes fixas, todas 10 h | 2e31588 | p:null/65537 a:null/65537 | conservador (estouro do teto) | 20 | 580 | 290 | True | 20; 580; 290 | 4,24 | 121, 54,6, 54 | 1604 | sim |
| 6x5 partes fixas, todas 10 h | 2e31588 | p:null/65537 a:null/65537 | conservador (estouro do teto) | 20 | 580 | 290 | True | 20; 580; 290 | 5 | 57,3, 62,1, 90,8 | 1478 | sim |
| 5x6 T4+P5 sem janela (prestador) | 2e31588 | p:false/58035 p:false/2869 a:false/58035 a:false/2869 | cliques | 96,7273 | 503,2727 | 50 | True | 1064/11; 5536/11; 50 | 1 | 81,1, 78,7, 70,5 | 1913 | sim |
| caso 9: 5x6 janelas variadas (perf_casos #9) | 2e31588 | p:false/42764 p:false/2468 a:false/42764 a:false/2468 | cliques | 3000 | 0 | 255 | True | 3000; 0; 255 | 0,9247 **inexecutável** | 62, 51,8, 49 | 1322 | sim |
| controle 4x5 partes fixas, todas 10 h | 2e31588 | p:false/3610 p:false/940 a:false/3610 a:false/940 | cliques | 66,25 | 533,75 | 65 | True | 265/4; 2135/4; 65 | 1 | 3,2, 4,1, 3,5 | 71 | sim |
| controle 4x6 partes fixas, todas 10 h | 2e31588 | p:false/9990 p:false/1644 a:false/9990 a:false/1644 | cliques | 66,3158 | 533,6842 | 65 | True | 1260/19; 10140/19; 65 | 1 | 19,8, 16,8, 16,3 | 209 | sim |
| controle 5x5 partes fixas, todas 10 h | 2e31588 | p:false/20325 p:false/1825 a:false/20325 a:false/1825 | cliques | 84,7619 | 515,2381 | 50 | True | 1780/21; 10820/21; 50 | 1 | 41,2, 17,3, 17,3 | 370 | sim |
| contraexemplo 7 configurações, prazos 2/3/10, partes fixas (rend 1) | 2e31588 | p:false/36 p:false/28 a:false/36 a:false/28 | cliques | 15,5 | 0 | 0 | False | 31/2; 0; 0 | 0,9677 **inexecutável** | 6,8, 1,6, 0,5 | 1 | sim |
| contraexemplo 7 configurações, sem %, Q=15,5 | 2e31588 | p:false/36 p:false/28 a:false/36 a:false/28 | cliques | 15,5 | 0 | 2,4286 | True | 31/2; 0; 17/7 | 0,9677 **inexecutável** | 0,9, 0,7, 4,8 | 1 | sim |
| M2 fracao_final_no_corte_aninhado (oráculo, linhas 142–144) | 2e31588 | p:false/5 p:false/4 a:false/5 a:false/4 | cliques | 12 | 988 | 690 | True | 12; 988; 690 | 1 | 4,2, 0,7, 0,6 | 1 | sim |
| 5x6 partes fixas, todas 10 h | 04bf6f2 | p:null/65537 a:null/65537 | conservador (estouro do teto) | 20 | 580 | 290 | True | 20; 580; 290 | 4,24 | 75,6, 120,4, 166,9 | 1181 | sim |
| 6x5 partes fixas, todas 10 h | 04bf6f2 | p:null/65537 a:null/65537 | conservador (estouro do teto) | 20 | 580 | 290 | True | 20; 580; 290 | 5 | 59,9, 108,9, 78,5 | 1141 | sim |
| 5x6 T4+P5 sem janela (prestador) | 04bf6f2 | p:null/65537 a:null/65537 | conservador (estouro do teto) | 40 | 560 | 280 | True | 40; 560; 280 | 3,8364 | 56,1, 108,3, 54,4 | 942 | sim |
| caso 9: 5x6 janelas variadas (perf_casos #9) | 04bf6f2 | p:null/65537 a:null/65537 | conservador (estouro do teto) | 3000 | 0 | 1340 | True | 3000; 0; 1340 | 2 | 108,2, 50,9, 50,5 | 941 | sim |
| controle 4x5 partes fixas, todas 10 h | 04bf6f2 | p:false/3610 p:false/940 a:false/3610 a:false/940 | cliques | 66,25 | 533,75 | 65 | True | 265/4; 2135/4; 65 | 1 | 3,6, 3,2, 3,6 | 51 | sim |
| controle 4x6 partes fixas, todas 10 h | 04bf6f2 | p:false/9990 p:false/1644 a:false/9990 a:false/1644 | cliques | 66,3158 | 533,6842 | 65 | True | 1260/19; 10140/19; 65 | 1 | 9,6, 9,3, 55,9 | 142 | sim |
| controle 5x5 partes fixas, todas 10 h | 04bf6f2 | p:false/20325 p:false/1825 a:false/20325 a:false/1825 | cliques | 84,7619 | 515,2381 | 50 | True | 1780/21; 10820/21; 50 | 1 | 17,8, 18,7, 18,9 | 253 | sim |
| contraexemplo 7 configurações, prazos 2/3/10, partes fixas (rend 1) | 04bf6f2 | p:false/36 p:false/28 a:false/36 a:false/28 | cliques | 15,5 | 0 | 0 | False | 31/2; 0; 0 | 0,9677 **inexecutável** | 3,6, 1,5, 0,4 | 1 | sim |
| contraexemplo 7 configurações, sem %, Q=15,5 | 04bf6f2 | p:false/36 p:false/28 a:false/36 a:false/28 | cliques | 15,5 | 0 | 2,4286 | True | 31/2; 0; 17/7 | 0,9677 **inexecutável** | 1,6, 4,1, 0,4 | 1 | sim |
| M2 fracao_final_no_corte_aninhado (oráculo, linhas 142–144) | 04bf6f2 | p:false/5 p:false/4 a:false/5 a:false/4 | cliques | 12 | 988 | 690 | True | 12; 988; 690 | 1 | 3,5, 0,5, 0,6 | 2 | sim |
| 5x6 partes fixas, todas 10 h | ee4f954 | p:null/65537 a:null/65537 | conservador (estouro do teto) | 20 | 580 | 290 | True | 20; 580; 290 | 4,24 | 74,8, 59,2, 64 | 1347 | sim |
| 6x5 partes fixas, todas 10 h | ee4f954 | p:null/65537 a:null/65537 | conservador (estouro do teto) | 20 | 580 | 290 | True | 20; 580; 290 | 5 | 49,8, 51, 48,6 | 911 | sim |
| 5x6 T4+P5 sem janela (prestador) | ee4f954 | p:null/65537 a:null/65537 | conservador (estouro do teto) | 111,3333 | 488,6667 | 50 | True | 334/3; 1466/3; 50 | 0,6535 **inexecutável** | 124,1, 73,7, 59,7 | 1665 | sim |
| caso 9: 5x6 janelas variadas (perf_casos #9) | ee4f954 | p:null/65537 a:null/65537 | conservador (estouro do teto) | 3000 | 0 | 255 | True | 3000; 0; 255 | 0,3414 **inexecutável** | 51,7, 56,2, 54,4 | 2324 | sim |
| controle 4x5 partes fixas, todas 10 h | ee4f954 | p:false/3610 p:false/940 a:false/3610 a:false/940 | cliques | 66,25 | 533,75 | 65 | True | 265/4; 2135/4; 65 | 1 | 3,5, 4,4, 4,2 | 44 | sim |
| controle 4x6 partes fixas, todas 10 h | ee4f954 | p:false/9990 p:false/1644 a:false/9990 a:false/1644 | cliques | 66,3158 | 533,6842 | 65 | True | 1260/19; 10140/19; 65 | 1 | 15,8, 83,9, 9,3 | 184 | sim |
| controle 5x5 partes fixas, todas 10 h | ee4f954 | p:false/20325 p:false/1825 a:false/20325 a:false/1825 | cliques | 84,7619 | 515,2381 | 50 | True | 1780/21; 10820/21; 50 | 1 | 27,9, 18,6, 31,4 | 277 | sim |
| contraexemplo 7 configurações, prazos 2/3/10, partes fixas (rend 1) | ee4f954 | p:false/36 p:false/28 a:false/36 a:false/28 | cliques | 15,5 | 0 | 0 | False | 31/2; 0; 0 | 0,9677 **inexecutável** | 3,5, 0,8, 1,1 | 1 | sim |
| contraexemplo 7 configurações, sem %, Q=15,5 | ee4f954 | p:false/36 p:false/28 a:false/36 a:false/28 | cliques | 15,5 | 0 | 2,4286 | True | 31/2; 0; 17/7 | 0,7742 **inexecutável** | 0,8, 1,8, 0,4 | 1 | sim |
| M2 fracao_final_no_corte_aninhado (oráculo, linhas 142–144) | ee4f954 | p:false/5 p:false/4 a:false/5 a:false/4 | cliques | 12 | 988 | 690 | True | 12; 988; 690 | 1 | 3,2, 0,5, 0,5 | 0 | sim |

### T2. Esperado: caminho de cliques forçado (cópia var/cliq de 2e31588), Python com Fraction, e dois verificadores independentes

| Caso | Alocado exato | Saldo exato | Déficit exato (h) | JS alocado | V2 cortes | V3 (verif.py) θ* | 2º verificador (emparelhamentos) θ* |
|---|---|---|---|---|---|---|---|
| 5x6 partes fixas, todas 10 h | 424/5 | 2576/5 | 50 | 84,8 | ok | 1 | 1 (4050 emparelhamentos, 1 segmentos) |
| 6x5 partes fixas, todas 10 h | 100 | 500 | 50 | 100 | ok | 1 | 1 (4050 emparelhamentos, 1 segmentos) |
| 5x6 T4+P5 sem janela (prestador) | 1064/11 | 5536/11 | 50 | 96,7273 | ok | 1 | 1 (3549 emparelhamentos, 1 segmentos) |
| caso 9: 5x6 janelas variadas (perf_casos #9) | 3000 | 0 | 255 | 3000 | ok | 0,9247 **inexecutável** | 0,9247 (3121 emparelhamentos, 8 segmentos) |
| controle 4x5 partes fixas, todas 10 h | 265/4 | 2135/4 | 65 | 66,25 | ok | 1 | 1 (500 emparelhamentos, 1 segmentos) |
| controle 4x6 partes fixas, todas 10 h | 1260/19 | 10140/19 | 65 | 66,3158 | ok | 1 | 1 (1044 emparelhamentos, 1 segmentos) |
| controle 5x5 partes fixas, todas 10 h | 1780/21 | 10820/21 | 50 | 84,7619 | ok | 1 | 1 (1545 emparelhamentos, 1 segmentos) |

### T3. Propostas: casos principais, extras e contraexemplo (JS 3 execuções, mediana; Python 1 execução)

Célula: alocado ha · déficit h · caminho (cliq = cliques; CONS = conservador por estouro; L = reconhecido sem busca) · JS ms · Py ms. **inexec.** = V3 prova que não há cronograma.

| Caso | P0 = 2e31588 | P1 2^18 | P1 2^20 | P1 2^22 | P2 | P2u |
|---|---|---|---|---|---|---|
| 5x6 partes fixas, todas 10 h | 20 · 290 · CONS · 87 · 862 | 84,8 · 50 · cliq · 74 · 1235 | 84,8 · 50 · cliq · 68 · 1229 | 84,8 · 50 · cliq · 80 · 1171 | 84,8 · 50 · cliq L · 3 · 5 | 84,8 · 50 · cliq L · 6 · 5 |
| 6x5 partes fixas, todas 10 h | 20 · 290 · CONS · 52 · 872 | 100 · 50 · cliq · 73 · 1398 | 100 · 50 · cliq · 68 · 1622 | 100 · 50 · cliq · 93 · 1256 | 100 · 50 · cliq L · 4 · 9 | 100 · 50 · cliq L · 2 · 5 |
| 5x6 T4+P5 sem janela (prestador) | 96,73 · 50 · cliq · 47 · 794 | 96,73 · 50 · cliq · 46 · 811 | 96,73 · 50 · cliq · 45 · 997 | 96,73 · 50 · cliq · 46 · 792 | 96,73 · 50 · cliq L · 3 · 6 | 96,73 · 50 · cliq L · 5 · 5 |
| caso 9: 5x6 janelas variadas (perf_casos #9) | 3000 · 255 · cliq **inexec.** · 73 · 537 | 3000 · 255 · cliq **inexec.** · 35 · 583 | 3000 · 255 · cliq **inexec.** · 35 · 813 | 3000 · 255 · cliq **inexec.** · 38 · 538 | 3000 · 255 · cliq L **inexec.** · 7 · 6 | 3000 · 255 · cliq **inexec.** · 34 · 646 |
| controle 4x5 partes fixas, todas 10 h | 66,25 · 65 · cliq · 4 · 46 | 66,25 · 65 · cliq · 3 · 46 | 66,25 · 65 · cliq · 3 · 43 | 66,25 · 65 · cliq · 4 · 42 | 66,25 · 65 · cliq L · 1 · 3 | 66,25 · 65 · cliq L · 1 · 3 |
| controle 4x6 partes fixas, todas 10 h | 66,32 · 65 · cliq · 8 · 138 | 66,32 · 65 · cliq · 9 · 133 | 66,32 · 65 · cliq · 13 · 138 | 66,32 · 65 · cliq · 9 · 130 | 66,32 · 65 · cliq L · 1 · 4 | 66,32 · 65 · cliq L · 6 · 4 |
| controle 5x5 partes fixas, todas 10 h | 84,76 · 50 · cliq · 19 · 296 | 84,76 · 50 · cliq · 17 · 258 | 84,76 · 50 · cliq · 27 · 256 | 84,76 · 50 · cliq · 21 · 241 | 84,76 · 50 · cliq L · 4 · 4 | 84,76 · 50 · cliq L · 1 · 4 |
| extra 6x6 partes fixas, todas 10 h | 20 · 290 · CONS · 67 · 1087 | 20 · 290 · CONS · 274 · 5095 | 104,62 · 40 · cliq · 565 · 10127 | 104,62 · 40 · cliq · 541 · 9136 | 104,62 · 40 · cliq L · 9 · 9 | 104,62 · 40 · cliq L · 9 · 8 |
| extra 5x7 partes fixas, todas 10 h | 20 · 290 · CONS · 75 · 1586 | 20 · 290 · CONS · 222 · 4606 | 85,6 · 50 · cliq · 232 · 5038 | 85,6 · 50 · cliq · 230 · 4274 | 85,6 · 50 · cliq L · 4 · 8 | 85,6 · 50 · cliq L · 3 · 8 |
| extra 7x5 partes fixas, todas 10 h | 20 · 290 · CONS · 65 · 1175 | 20 · 290 · CONS · 218 · 4255 | 100 · 50 · cliq · 264 · 6337 | 100 · 50 · cliq · 261 · 5256 | 100 · 50 · cliq L · 2 · 7 | 100 · 50 · cliq L · 2 · 7 |
| extra 6x7 partes fixas, todas 10 h | 20 · 290 · CONS · 83 · 1716 | 20 · 290 · CONS · 304 · 5744 | 20 · 290 · CONS · 1140 · 23971 | 105,38 · 40 · cliq · 2926 · 50196 | 105,38 · 40 · cliq L · 2 · 10 | 105,38 · 40 · cliq L · 3 · 12 |
| extra 7x6 partes fixas, todas 10 h | 20 · 290 · CONS · 85 · 1432 | 20 · 290 · CONS · 516 · 5153 | 20 · 290 · CONS · 1248 · 19463 | 120 · 40 · cliq · 4020 · 55191 | 120 · 40 · cliq L · 2 · 10 | 120 · 40 · cliq L · 3 · 11 |
| extra 7x7 partes fixas, todas 10 h | 20 · 290 · CONS · 97 · 1761 | 20 · 290 · CONS · 603 · 5757 | 20 · 290 · CONS · 1529 · n/m | 20 · 290 · CONS · 5818 · n/m | 125,24 · 32,86 · cliq L · 2 · 13 | 125,24 · 32,86 · cliq L · 3 · 13 |
| extra 8x8 partes fixas, todas 10 h | 20 · 290 · CONS · 127 · 2238 | 20 · 290 · CONS · 484 · 7200 | 20 · 290 · CONS · 2062 · n/m | 20 · 290 · CONS · 7493 · n/m | 145,87 · 27,5 · cliq L · 6 · 22 | 145,87 · 27,5 · cliq L · 4 · 22 |
| extra 10x10 partes fixas, todas 10 h | 20 · 290 · CONS · 210 · 3012 | 20 · 290 · CONS · 764 · 10592 | 20 · 290 · CONS · 3307 · n/m | 20 · 290 · CONS · 12087 · n/m | 187,14 · 20 · cliq L · 9 · 52 | 187,14 · 20 · cliq L · 17 · 54 |
| extra 6x6 T5+P5 sem janela | 36,67 · 281,67 · CONS · 75 · 1264 | 36,67 · 281,67 · CONS · 255 · 4045 | 102,6 · 40 · cliq · 468 · 6336 | 102,6 · 40 · cliq · 430 · 6275 | 102,6 · 40 · cliq L · 4 · 8 | 102,6 · 40 · cliq L · 4 · 8 |
| contraexemplo 7 configurações, prazos 2/3/10, partes fixas (rend 1) | 15,5 · 0 · cliq **inexec.** · 2 · 1 | 15,5 · 0 · cliq **inexec.** · 2 · 1 | 15,5 · 0 · cliq **inexec.** · 2 · 1 | 15,5 · 0 · cliq **inexec.** · 2 · 1 | 15,5 · 0 · cliq L **inexec.** · 2 · 1 | 15,5 · 0 · cliq **inexec.** · 1 · 1 |
| contraexemplo 7 configurações, sem %, Q=15,5 | 15,5 · 2,43 · cliq **inexec.** · 1 · 1 | 15,5 · 2,43 · cliq **inexec.** · 1 · 1 | 15,5 · 2,43 · cliq **inexec.** · 1 · 1 | 15,5 · 2,43 · cliq **inexec.** · 1 · 1 | 15,5 · 2,43 · cliq L **inexec.** · 0 · 1 | 15,5 · 2,43 · cliq **inexec.** · 1 · 1 |

### T4. Bateria adversarial (71 casos de 20–36 configurações, semente 20261004; JS em todos; Python em todos para P0, P2, P2u e P1 2^18, e só nos 7 piores para P1 2^20 e 2^22)

| Variante | JS pior ms (caso) | JS casos no conservador por estouro do buraco | Python pior ms (caso) | Python casos | Verificador: casos inexecutáveis (V3) | JS = Python |
|---|---|---|---|---|---|---|
| P0 = 2e31588 | 358 (perf_casos: pares12x2 (24 cfg, 4096 cliques de 12)) | 8 | 1168 (trator×implemento 6x6 jan 10) | 71 | 1: perf_casos: trator×implemento 5×6 janelas variadas | 71 casos, 0 com diferença |
| P1 2^18 | 308 (perf_casos: pares12x2 (24 cfg, 4096 cliques de 12)) | 4 | 4399 (trator×implemento 6x6 janelas variadas (todas finitas)) | 71 | 1: perf_casos: trator×implemento 5×6 janelas variadas | 71 casos, 0 com diferença |
| P1 2^20 | 503 (trator×implemento 6x6 jan 10) | 0 | 43045 (extra 10x10 partes fixas, todas 10 h) | 7 | 2: trator×implemento 6x6 janelas variadas (todas finitas); perf_casos: trator×implemento 5×6 janelas variadas | 7 casos, 0 com diferença |
| P1 2^22 | 525 (trator×implemento 6x6 jan 10) | 0 | 176757 (extra 10x10 partes fixas, todas 10 h) | 7 | 2: trator×implemento 6x6 janelas variadas (todas finitas); perf_casos: trator×implemento 5×6 janelas variadas | 7 casos, 0 com diferença |
| P2 | 342 (perf_casos: pares12x2 (24 cfg, 4096 cliques de 12)) | 1 | 810 (perf_casos: pares12x2 (24 cfg, 4096 cliques de 12)) | 71 | 2: trator×implemento 6x6 janelas variadas (todas finitas); perf_casos: trator×implemento 5×6 janelas variadas | 71 casos, 0 com diferença |
| P2u | 337 (perf_casos: pares12x2 (24 cfg, 4096 cliques de 12)) | 3 | 1102 (trator×implemento 6x6 janelas variadas (todas finitas)) | 71 | 1: perf_casos: trator×implemento 5×6 janelas variadas | 71 casos, 0 com diferença |

### T5. 3 300 entradas aleatórias (semente 20261004), verificador independente

| Variante | Com violação (V3) | Novas em relação a P0 | Caminho cliques / conservador (estouro) / conservador (ciclo) | Reconhecidas sem busca | Igual a P0 onde P0 conferiu | JS ms máx | Python: entradas, diferenças JS×Py, ms máx |
|---|---|---|---|---|---|---|---|
| P0 = 2e31588 | 276 (B 92, C2 179, A 3, D 2) | 0 | 3062 / 119 / 119 | 0 | sim | 97 (#3006) | 3300, 0, 2969 (#2502) |
| P1 2^18 | 310 (B 92, C2 213, A 3, D 2) | 34 | 3150 / 31 / 119 | 0 | sim | 368 (#2829) | 40, 0, 7763 (#2800) |
| P1 2^20 | 319 (B 92, C2 222, A 3, D 2) | 43 | 3180 / 1 / 119 | 0 | sim | 1234 (#2509) | 40, 0, 9115 (#2800) |
| P1 2^22 | 320 (B 92, C2 223, A 3, D 2) | 44 | 3181 / 0 / 119 | 0 | sim | 1965 (#2509) | 40, 0, 7523 (#2800) |
| P2 | 320 (B 92, C2 223, A 3, D 2) | 44 | 3181 / 0 / 119 | 2272 | sim | 19 (#1981) | 3300, 0, 191 (#3298) |
| P2u | 276 (B 92, C2 179, A 3, D 2) | 0 | 3122 / 59 / 119 | 440 | sim | 114 (#2623) | 3300, 0, 2220 (#2909) |
