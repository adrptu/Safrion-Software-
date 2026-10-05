# Cético do achado 8 — refazimento independente (04/10/2026)

Tudo **executado** em cópias próprias (`git archive` de ee4f954, 04bf6f2, 2e31588 em `src/`; variantes P1, P2, P0nR23, P2nR23 recriadas aplicando `../var/*.diff` com `patch` sobre 2e31588 em `var/`; `brutos/aplica_patches.txt`: os arquivos resultantes são byte a byte iguais aos do pacote). A worktree não foi tocada. Runners próprios: `scripts/cr.js`, `scripts/cr.py` (Fraction), `scripts/cr_list.*`.

## O que confere (comando → bruto)
- sha256: as 80 linhas de `../SHA256SUMS.txt` e as 19 da tabela do PACOTE conferem (`sha256sum -c` → `brutos/sha_pacote_80.txt`, `brutos/sha_pacote_check.txt`).
- Esperado × obtido, todas as linhas (F5, F5seq, F1, F1b, F1c, F3, F4, M2; ee4f954, 04bf6f2, 2e31588, P1, P2, P0nR23, P2nR23): `python3 scripts/tab.py` → `brutos/tabela_cetico.txt`. Viabilidade por EDF exato (grafos completos) e por caminho B–A–C (M2). Paridade JS×Py True em todas.
- Motivos (F5/F1/F3/F4/M2; 04bf6f2, 2e31588, P1, P2): `brutos/motivos_cetico.txt`. M2: 8 motivos idênticos ao PACOTE; P1 muda só "41,67 % a 58,33 %".
- Agendas esperadas: verificação própria → `brutos/agendas_cetico.txt` (todas sem erro; totais 260/260/100/110/110/100/100/37/3).
- Oráculo: P0 101/101, P1 100/101 (falha só M2: q 5/3, 7/3, 25/3), P2 101/101 (diferenças só de tempo), P0nR23 e P2nR23 100/101 (falha R2-3) → `brutos/oraculo_*.txt`.
- Instrumentação de ordem: `node ../scripts/ordem_jan.js … M2 F5 F1 F3` → `brutos/ordem_jan_cetico.txt`, idêntico ao bruto do pacote.
- Aleatórias: `gera_aleatorias.py 20261004 6000` regera os 3 arquivos com sha idêntico (`brutos/sha_aleat_regerado.txt`). Métricas → `brutos/metricas_aleat_cetico.txt`: P1 mais 323 / menos 24 (24 com sem %), P2 mais 45 / menos 56, maior perda P2 17,78 % = 33,33 ha (idx 5549), mudança onde P0 sem conflito 0, monotonicidade janela×2 498/478/497, Q×2 92/94/98, paridade 5999/6000 (idx 1188: 34,38 × 34,37). R2-3: q muda em 6 (4 mais, 2 menos); P2nR23: 465 (263/180) → `brutos/extra2_cetico.txt`. idx 2644 Python com float '6.666666666666671'.
- Contagens com o verificador do próprio pacote: JS 0/0/0, Python tol 0 8/4/9 (`brutos/extra2_cetico.txt`).

## Divergências
1. **Viabilidade nas aleatórias (afirmação "inviáveis JS 0", "P1 é sempre viável", "excesso de ~4e-15 h").** O verificador do pacote só testa cortes por clique (necessário, não suficiente quando o grafo de exclusão não é completo). Com verificador exato (PL de escalonamento preemptivo com início comum, `scripts/viab_pl.py` → `brutos/viab_aleat_cetico.txt`; autoteste em `brutos/autoteste_pl.txt`): JS inviáveis P0 5, P1 5, P2 4 (idx 1750, 2462, 3327, 4617, 4934); Python exato 12/8/11. Certificados à mão (`brutos/extra_cetico.txt`): idx 2462 (P0) precisa de 290/3 h em [20,100] = 80 h; idx 4934 (P0) precisa de 85 h em 80 h. Todas com conflito=true; já existem em 2e31588 (P0) e em P0nR23/P2nR23 (`brutos/viab_aleat_nR23_cetico.txt`). P1 aumenta o atendido em duas delas (3327: 226,04→235,40; 4617: 193,93→202,13).
2. **"perda máxima de 8,57 ha, 14 %" (recomendação, P1).** 8,57 ha é a perda da maior perda relativa (idx 4422); a maior perda absoluta é 11,67 ha (idx 1582: 125,67→114, 9,28 %).
3. **"maior ganho 20,78 %" (P1) e "10,80 %" (P2)** são relativos ao valor novo; sobre o P0 são 26,23 % e 12,10 % (base não declarada).

## Brutos (sha256)
Ver `SHA256SUMS_cetico.txt`.

```text
5f32ca61ea60fd55f36c3574240629df515de89d5657d89b258acc2ab46108bb  brutos/F_js_04bf6f2.json
2276cc80d60be0df752d61d3d7fe367ed03bc2cb61398a879e91e33d4075f8b2  brutos/F_js_2e31588.json
2276cc80d60be0df752d61d3d7fe367ed03bc2cb61398a879e91e33d4075f8b2  brutos/F_js_P0nR23.json
7525ada05a0e5b890408765975949b360f98913623258d5eba8bac7d0e33c965  brutos/F_js_P1.json
2276cc80d60be0df752d61d3d7fe367ed03bc2cb61398a879e91e33d4075f8b2  brutos/F_js_P2.json
1dc6462134b21f42e696d3f5b1ca4901ca35821642762e6600f008292261a47b  brutos/F_js_P2nR23.json
643ec1dfb746c4e79c3c1da717feb74529c7149c0004e43af3f789d7d1e0c0e8  brutos/F_js_ee4f954.json
28f13a2160fb3f32133019b6772819bf02bf086b7d42f28a82f824d4324c9f2d  brutos/F_py_04bf6f2.json
a59473849130a37c66c6fb1c1a79e38f21dbb2755cf94d8906dca818d370deff  brutos/F_py_2e31588.json
a59473849130a37c66c6fb1c1a79e38f21dbb2755cf94d8906dca818d370deff  brutos/F_py_P0nR23.json
3344ec35cb281bb6d016d0387aa1a11017abe418bf76652b2ff748f8011875e8  brutos/F_py_P1.json
a59473849130a37c66c6fb1c1a79e38f21dbb2755cf94d8906dca818d370deff  brutos/F_py_P2.json
809a914699ce38da321f5a0d858c04b8647a1fb15195be83b0b14dd839c33055  brutos/F_py_P2nR23.json
7a30b810e323a15bb6a0aec1fb017341ca6c1a0c8b2908c41e8a10dfd32dfbd7  brutos/F_py_ee4f954.json
86591b4c4cf03f46e7ca13a6e0a9485c92c89db47f0c90f9c7d9cd2175aa165a  brutos/agendas_cetico.txt
3bbbd6831cae81bff4fc045b687f49f3049dcd686bfc6f8b3809b7f37420a911  brutos/aplica_patches.txt
5b1912f6abe7d32690b7f097353ad0d0feb61bf753feb9165fe9a20ece6392fa  brutos/autoteste_pl.txt
b6295643bc9d4973960b8c3ba55eaff2801b88570dde675267ca8ea7477aa49e  brutos/extra2_cetico.txt
7d12a0345036826c2b92b28d6f2fa9dcca62fc72c7bfe34fc2be44ba795ed278  brutos/extra_cetico.txt
ff46ed72d6bcd3f7bccf9c8be3a576d220b36aa7e6009131a41d10915232b10e  brutos/inviaveis_P0_detalhe.txt
9d5dbd7a476302ebf390a2715ed879a031ab754e8d337c6f465724f386fc84a9  brutos/metricas_aleat_cetico.txt
950ff8feb189925aca0fd2bdae78ac707b171e9de279ef7a655a3043a0adb0a3  brutos/motivos_cetico.txt
90f2be508f935f7bbd93186feacb6a5034c967c7ce8fa235873b135f599a78be  brutos/oraculo_P0.txt
19f266a1f39bc3a1af2b4e7686eab972b159bd6cf816ac9ae773c542365a8961  brutos/oraculo_P0nR23.txt
3691b817ebc4212669e6ad8b6af966f0fb37c95d6e18bf158a07fd6858427c08  brutos/oraculo_P1.txt
6fd235d4c99fcc28789b886005cbce76ce2be86c49df8494364942677c73766f  brutos/oraculo_P2.txt
b8b56579f4509edf712df8d23ab00ea7ab8669866969788ead9996a8f548c3a0  brutos/oraculo_P2nR23.txt
a5e61dbea1fa2b82778fd2c2538e3da1cb7eac33187d06f92c80563b30e15064  brutos/ordem_jan_cetico.txt
44daa508f8e9f4aa8b033a585a8770fa5f9d6fd5f56e259cf61247c462a51e0f  brutos/sha_aleat_regerado.txt
50af3d118c46dd91f5bb692a78c5a86ca0169f672bc3134a928640e1d92580cf  brutos/sha_pacote_80.txt
8a5e819433e07d5b4f1ca0666f54f30dab075c6ba78d7c9abfd36bcd3f864aff  brutos/sha_pacote_check.txt
cb84e9ff0dda0107b80dd6b885d76bf61e92d0eaf09c89584d38a850dafa5b05  brutos/tabela_cetico.txt
c8795db31b12312451d328145a102304c614e5ba9caead275a4f9fa2624055d3  brutos/viab_aleat_cetico.txt
8e26089f426280f6b0efff651101264d16a78e219df403eaf710d6ca9b1b1210  brutos/viab_aleat_nR23_cetico.txt
```
(os A_*.json das aleatórias e scripts/entradas estão em SHA256SUMS_cetico.txt)
