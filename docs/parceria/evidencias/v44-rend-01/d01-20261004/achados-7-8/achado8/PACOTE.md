# Pacote do achado 8: partes fixas reduzidas uma restrição por vez, sem devolver a folga ("muda o M2")

Pacote para a decisão do Codex. Tudo aqui foi **executado** nesta sessão (04/10/2026, 23:10–23:20) sobre cópias tiradas com `git archive`. A worktree `/home/user/sp-camada-sintetica` não foi editada. Os dados são sintéticos.

Pasta: `/tmp/claude-0/-home-user-Safrion-Software-/65558514-68d9-57f5-9da3-513cd6735cdc/scratchpad/r2_7_8/achado8/` (os caminhos abaixo são relativos a ela).

Nota de organização: quando cheguei, a pasta já tinha arquivos de uma tentativa anterior (22:42–23:08), sem autoria minha. Movi esses arquivos para `_tentativa_anterior_2242_2308/` e **não os usei como evidência**. Todos os números deste pacote vêm dos brutos listados no fim.

## Texto do achado

O texto completo do achado e dos dois vereditos (`rev.json` `itens[8]`) está copiado por programa, sem edição, em `ACHADO8_TEXTO.md`. A conferência automática encontrou os 22 campos verbatim (`scripts/copia_texto.py`).

- Título: "Partes fixas: a restrição antiga de janela máxima (sq/at:/pl:) reduz antes do corte por prazo mais apertado, e a folga liberada não volta (atendido subestimado e motivo falso)". Severidade proposta: S3. Revisão feita sobre 04bf6f2.
- Veredito 0: refutado como defeito do delta. Severidade "nenhuma"; no máximo S3 como melhoria da política.
- Veredito 1: confirmado, S3. Propõe como correção mínima "não registrar a restrição antiga quando há corte com os mesmos membros e o mesmo prazo".

## Versão e arquivos

| commit | safra.js (sha256) | bloco REPARTIR | laço das partes fixas | dados2.py: REPARTIR / laço |
|---|---|---|---|---|
| ee4f954c9b24… (antes do D-01) | a9f4588e… | 29–216 | 158–159 | 187–533 / 412–417 |
| 04bf6f2afb67… (rodada 1) | 210f6653… | 29–231 | 169–170 | 187–561 / 434–439 |
| 2e31588496e7… (candidata, rodada 2) | bf4e06d6… | 29–262 | 185–186 | 187–614 / 458–463 |

Pontos do código em 2e31588:
- Registro das restrições em `safra.js`: as antigas `sq`, `at:` e `pl:` nas linhas 88–90 e 113; os cortes por prazo nas linhas 136–137 e 154; `jan`, `SUB` e `pistaA` nas linhas 172–176.
- O laço com a ordem R2-3 (grupo inteiro primeiro) está nas linhas 185–186.
- O motivo da fração final está nas linhas 188–193.
- O caso M2 do oráculo está em `rend_multiconjuntos_unit.py`, linhas 142–144.
- sha256 de 2e31588: `dados2.py` 5cd56f15…, `rend_multiconjuntos_unit.py` d1fe83e8….

As variantes são cópias de 2e31588 com patch idêntico em JS e Python, gerado por `scripts/patch_variantes.py`. Os diffs estão em `var/*.diff`.

| variante | o que muda |
|---|---|
| P0 | nada (2e31588) |
| P1 | Logo depois do laço das partes fixas e antes dos motivos: para cada x fixa com q < cab, soma r × min((cab−q)/r, min sobre pl(x) de (jan[g] − uso_fixo[g])), com o uso recalculado a cada x na ordem das configurações, e desconta do saldo. |
| P2 | A restrição antiga (`sq`/`at:`/`pl:`) perde os membros da divisão (xa = []) quando há um corte da divisão com os mesmos membros e o mesmo prazo. O plano (`pista`) não muda. |
| P0nR23, P2nR23 | Só diagnóstico: P0 e P2 sem a ordem R2-3, ou seja, a ordem de `Object.keys(jan)` como em 04bf6f2. |

## Entrada

Todas as entradas estão em `entradas/casos_F.json`, com a fonte de cada uma:

| caso | resumo | fonte |
|---|---|---|
| F5 | Q 1000. A: 3 ha/h, 60 %, janela 100. B e C: 1 ha/h, 20 %, janela 20. Ativo `a01` nas três. | `prerev7/falsa/c4.json[0]` |
| F5seq | O mesmo de F5, com sequência declarada. | `verif-restricao-falsa-0-0/c.json` |
| F1 | Q 1000, sequência. A: 20 %, janela 100. B1–B5: 16 %, janela 10. Todas com 1 ha/h. | `c1.json[4]` |
| F1b | F1 com A em 19 % e D (1 %, sem janela). | `c2.json[5]` |
| F1c | F1b com D de janela 1000. | `c2.json[6]` |
| F3 | Q 1000, sequência. A: 50 %, janela 100. B e C: 25 %, janela 10. | `c2.json[8]` |
| F4 | Q 150, ativo `a01`. A: 66,67 %, janela 100. B1–B5: 6,67 %, janela 10. | `c3.json[0]` |
| M2 | Copiado do oráculo (ver a seção "M2: o que muda"). | oráculo |

O "esperado" de cada caso é uma agenda viável explícita, em `entradas/agendas_esperadas.json`. O script `scripts/verif.py` (`agenda_ok`) confere cada uma:
- as horas valem q/r;
- cada configuração termina dentro da própria janela;
- quem se exclui não se sobrepõe;
- q não passa da parte.

As oito agendas passaram, com `erros_agenda=[]` e verificador True.

**Verificador independente** (`scripts/verif.py`, `viavel`, não usa `repartir`):
- Duas configurações se excluem quando ambas têm `seq`, quando têm ativo em comum ou quando ambas usam um grupo de 1 unidade.
- Exigências: cada h ≤ a própria janela; para todo subconjunto que se exclui duas a duas e todo prazo t de um membro, Σ h (janela ≤ t) ≤ t.
- Como controle, ele recusa as saídas inviáveis conhecidas de ee4f954 (veja a tabela).

## Esperado × obtido

Comandos:
- `node scripts/run_js.js <safra.js> entradas/casos_F.json brutos/F_js_<v>.json`
- `python3 scripts/run_py.py <gen37> entradas/casos_F.json brutos/F_py_<v>.json` (Fraction)
- `python3 scripts/tabela_F.py > brutos/tabela_F.txt`

Leitura das tabelas:
- Valores em ha, salvo indicação. O déficit é em horas.
- JS e Python coincidem em q, alocado, saldo, déficit, conflito e motivos em **todas** as linhas: "paridade JS×Py=True" em `brutos/tabela_F.txt`.

| caso | esperado (agenda) | ee4f954 | 04bf6f2 | **2e31588 (P0)** | P1 | P2 |
|---|---|---|---|---|---|---|
| F5 | B 0–10 h, C 10–20 h, A 20–100 h → A 240, B 10, C 10 = **260** | A 214,29, B=C 14,29 → 242,86, **inviável** (B+C 28,57 h em 20 h) | A 214,29 (71,43 h), B=C 10 → 234,29 | **igual a 04bf6f2**: 234,29; saldo 765,71; conflito true; déficit 500 h; decorrido 91,43 h | A 240 → **260** | = P0 (234,29) |
| F5seq | igual ao F5: 260 | 242,86, inviável | 234,29 | 234,29 (iguais ao F5) | 260 | 234,29 |
| F1 | B1…B5 com 2 h cada em 0–10, A 10–100 → A 90, Bi 2 = **100** | A 66,67, Bi 6,67 → 100, **inviável** (B1+B2 13,33 h em 10 h) | A 66,67, Bi 2 → 76,67 | 76,67; saldo 923,33; conflito true; déficit 900 h | A 90 → **100** | = P0 (76,67) |
| F1b | igual ao F1, mais D 100–110 → **110** | 160, conflito **false**, inviável (A+B1 110 h em 100 h) | A 90,91, Bi 1,82, D 10 → 110 | 110 (= esperado); conflito true; déficit 890 h | 110 | 110 |
| F1c | igual ao F1b: **110** | 160, conflito false, inviável | 110 | 110 | 110 | 110 |
| F3 | B 0–5, C 5–10, A 10–100 → A 90, B 5, C 5 = **100** | A 83,33, B=C 8,33 → 100, inviável | A 83,33, B=C 5 → 93,33 | 93,33; saldo 906,67; conflito true; déficit 900 h | A 90 → **100** | = P0 (93,33) |
| F4 | B1…B5 com 2 h cada em 0–10, A 10–100 → **100** | 100, inviável | 76,67 | 76,67; saldo 73,33; conflito true; déficit 50 h | **100** | = P0 (76,67) |
| M2 | A 0–5/3, B 5/3–4, C 5/3–10 → A 5/3, B 7/3, C 25/3 = **37/3** | 12 (5/3, 2, 25/3) | 12 | 12 | **37/3** | 12 |

Motivos de 2e31588, as frases das partes fixas:
- F5: "as partes fixas em sequência não cabem na janela de 100 h: fazem de 50 % a 71,43 % do que cabia na própria janela" e "… janela de 20 h: cada uma faz 50 % …". A janela de 100 h fica com **8,57 h ociosas** (decorrido 91,43 h).
- F1: "janela de 100 h: fazem de 20 % a 66,67 %" e "janela de 10 h: cada uma faz 20 %".
- F3: "100 h: 50 % a 83,33 %" e "10 h: 50 %".
- F4: o mesmo de F1.
- Conflito: 2e31588 dá uma frase por grupo, por exemplo "A, B e C: em sequência precisam de 600 h para 1000 ha; a janela tem 100 h". O 04bf6f2 dava duas.

Com P1, a frase de F5 passa a "fazem de 50 % a 80 %", e a janela de 100 h fica cheia (A 80 h + B 10 h + C 10 h). Em F1, F3 e F4 passa a "20 % a 90 %" ou "50 % a 90 %".

Leitura:
- **O achado se reproduz em 2e31588** com os mesmos números de 04bf6f2 (F1, F3, F4, F5 e as variantes com `seq`). Todas as saídas são viáveis e todas mostram conflito.
- F1b e F1c não são subestimação: 110 é o total da agenda. Eles mostram a dependência de ordem: com D, o A sobe de 66,67 para 90,91.

**O mecanismo mudou de forma em 2e31588.** Instrumentação de uma cópia em memória (`node scripts/ordem_jan.js … M2 F5 F1 F3` → `brutos/ordem_jan_2e31588.txt`):
- Ordem em F5: `at:a01 [A,B,C] 100` → `acq:0,1,2@100 [A,B,C] 100` → `acq:1,2@20 [B,C] 20 (sub)`.
- A restrição antiga corta A, B e C por 100/140 e deixa A com 71,43 h e B e C com 14,29 h cada. O corte do grupo inteiro @100 é idêntico e não corta mais nada. O subcorte @20 baixa B e C para 10, e as 8,57 h liberadas não voltam.
- Se a restrição antiga for retirada (P2), o corte do grupo inteiro @100, que a ordem R2-3 processa antes do subcorte, faz exatamente a mesma redução. Por isso **P2 não muda nenhum número de F1–F5 em 2e31588**.
- P2 sem a ordem R2-3 (P2nR23) reproduz os números da variante do veredito 1 sobre 04bf6f2: F1 100 (A 90,91, Bi 1,82), F5 266,67 (A 250, B=C 8,33) e F3 100. Mas falha o caso R2-3 do oráculo (`brutos/oraculo_P2nR23.txt`: 100/101).

**A ordem R2-3 mudou algum número?**
- Em F1–F5 e no M2, não. P0nR23 e 2e31588 dão números idênticos em todas as linhas de `brutos/tabela_F.txt`.
- Nas 6 000 entradas aleatórias, q muda em 6: 4 atendem mais e 2 menos, todas viáveis (`python3 scripts/diag_r23.py` → `brutos/diag_r23.txt`).
- O efeito real da R2-3 é o caso R2-3 do oráculo, que falha sem ela (`brutos/oraculo_P0nR23.txt`: 100/101).
- Para o achado 8, a R2-3 **neutraliza a proposta P2**.

## M2: o que muda

Entrada exata do oráculo (2e31588, linhas 142–144), com Q = 1000 e pools `{'plant':{'un':1,'nome':'Plantadeiras'}}`:

| config | rend | part | seq | jan | rec | custo_h |
|---|---|---|---|---|---|---|
| A | 1 | 30 | True | 4 | `{'plant':1}` | 1 |
| B | 1 | 30 | True | 4 | — | 1 |
| C | 1 | 40 | — | 10 | `{'plant':1}` | 1 |

O oráculo espera `q=['5/3','2','25/3']`. Nos motivos, exige as substrings 'janela de 4 h: fazem de 41,67 % a 50 %' e 'janela de 10 h: fazem de 41,67 % a 83,33 %'.

Saída exata de 2e31588 (`brutos/oraculo_P0_2e31588.txt`, JS e Python idênticos):
- q = 5/3, 2, 25/3; alocado 12; saldo 988; conflito true; déficit 690 h.
- Motivos, na ordem:
  1. "sequência declarada: dividem trator, implemento ou operador"
  2. "Plantadeiras: ao mesmo tempo precisariam de 2, a fazenda tem 1; configurações consideradas em sequência nesta estimativa"
  3. "A: a parte fixa não cabe na janela de 4 h"
  4. "B: a parte fixa não cabe na janela de 4 h"
  5. "C: a parte fixa não cabe na janela de 10 h"
  6. "as partes fixas em sequência não cabem na janela de 4 h: fazem de 41,67 % a 50 % do que cabia na própria janela"
  7. "as partes fixas em sequência não cabem na janela de 10 h: fazem de 41,67 % a 83,33 % do que cabia na própria janela"
  8. "A e C: em sequência precisam de 700 h para 700 ha; a janela tem 10 h"
- Frações finais: A 5/3 de 4 = 5/12 (41,67 %); B 2 de 4 = 1/2 (50 %); C 25/3 de 10 = 5/6 (83,33 %).

Por que sobram horas na janela de 4 h (`brutos/ordem_jan_2e31588.txt`):
1. A ordem é `sq [A,B] 4` → `pl:plant [A,C] 10` → `acq:0,1@4` → `acq:0,2@10`. Os dois cortes são idênticos às duas restrições antigas, e nenhum é subcorte.
2. `sq`: A+B pedem 8 h em 4 h. A e B ficam com 2 h cada.
3. `pl:plant`: A+C pedem 2 + 10 = 12 h em 10 h, fração 10/12. A fica com 5/3 h e C com 25/3 h.
4. A+B passam a usar 11/3 h da janela de 4 h. **Sobra 1/3 h** que o B poderia usar, porque ele não usa a plantadeira e cabia até 4 h, mas a redução sequencial não devolve a folga.

A agenda A 0–5/3, B 5/3–4, C 5/3–10 é viável e sem preempção. O verificador também aceita.

| proposta | M2: q (A, B, C) | alocado | motivo da janela de 4 h | motivo da janela de 10 h | oráculo |
|---|---|---|---|---|---|
| P0 | 5/3, **2**, 25/3 | 12 | "fazem de 41,67 % a 50 %" | "41,67 % a 83,33 %" | 101/101 |
| P1 | 5/3, **7/3**, 25/3 | **37/3** (+1/3 ha) | "fazem de 41,67 % a **58,33 %**" | sem mudança | **100/101**: só o M2 falha, em q e no motivo (`brutos/oraculo_P1.txt`) |
| P2 | 5/3, 2, 25/3 | 12 | sem mudança | sem mudança | 101/101 (`brutos/oraculo_P2.txt`) |

A mudança do P1 no M2 **não corrige inviabilidade**: as duas saídas são viáveis. É **aumento do atendido** (+1/3 ha, B de 50 % para 58,33 % da própria janela), e o conflito e o déficit continuam iguais.

## Propostas e efeitos

Entradas aleatórias:
- Gerador: `python3 scripts/gera_aleatorias.py 20261004 6000 entradas/aleat.json`. **Semente 20261004**, 6 000 entradas.
- Cada entrada tem de 2 a 6 configurações e pelo menos uma parte fixa.
- Modos sorteados: mesmo ativo, sequência ou misto (ativos a1–a3, `seq` e plantadeira de 1 unidade).
- Sem troca. Janelas em {0, 5, 10, 20, 50, 100, vazio}.
- Variantes de monotonicidade: uma janela finita ×2 (0 → 10) em `aleat_janx2.json`, e Q ×2 em `aleat_Qx2.json`.
- Resultados: `python3 scripts/analisa_aleat.py` → `brutos/aleat_resumo.txt`; `scripts/perdas.py` → `brutos/perdas_ganhos.txt`; `scripts/excesso_exato.py` → `brutos/excesso_exato.txt`.

| | P0 (2e31588) | P1 | P2 |
|---|---|---|---|
| oráculo (101) | 101/101 | 100/101 (muda só o M2) | 101/101 (nenhum caso muda; as diferenças no bruto são só tempos) |
| F5 / F1 / F3 / F4 | 234,29 / 76,67 / 93,33 / 76,67 | **260 / 100 / 100 / 100** (= agenda) | iguais ao P0 |
| F1b / F1c | 110 / 110 | 110 / 110 | 110 / 110 |
| M2 | 12 | 37/3 | 12 |
| inviáveis JS (tolerância 1e-7 h) | 0 | 0 | 0 |
| inviáveis Python exato (tolerância 0) | 8, maior excesso 4,3e-15 h | 4, 4,0e-15 h | 9, 4,3e-15 h |
| atende mais que P0 | — | **323**, maior ganho 20,78 % (idx 449: 83,18 → 105) | 45, maior ganho 10,80 % (idx 113) |
| atende menos que P0 | — | **24**, todas com configuração sem %; maior perda 14,04 % = 8,57 ha (idx 4422: 61,07 → 52,5) | **56**; maior perda 17,78 % = 33,33 ha (idx 5549: 187,5 → 154,17) |
| alguma mudança onde P0 não tinha conflito | — | 0 | 0 |
| monotonicidade, janela ×2: alocado cai | 498/6000 | 478/6000 | 497/6000 |
| monotonicidade, Q ×2: alocado cai | 92/6000 | 94/6000 | 98/6000 |
| paridade JS×Python | 5 999/6 000 | 5 999/6 000 | 5 999/6 000 |

Notas sobre a tabela:
- **Inviáveis no Python exato.** Recusados só com tolerância zero, por um excesso numérico de cerca de 4e-15 h. A causa é anterior às propostas e já está no P0: uma parte da divisão das configurações sem % no Python sai em float, não em Fraction (idx 2644: `'6.666666666666671'`). Fica fora deste achado.
- **Paridade.** A única diferença é a mesma nas três variantes (idx 1188): os q são iguais, e o motivo diz "34,38 %" no Python e "34,37 %" no JS, por arredondamento de 34,375 em float. Isso também já está no P0 e fica fora deste achado, como S4.
- **Perdas do P1.** A folga devolvida a uma parte fixa tira horas de uma configuração sem % mais rápida, porque as partes fixas vêm primeiro (idx 4422: c1 sem %, 3 ha/h, cai de 12,86 para 0).

Tempo por chamada, medido em série (`brutos/tempo_serial.txt`), nas 6 000 entradas:

| | mediana JS | máximo JS | mediana Python | máximo Python |
|---|---|---|---|---|
| P0 | 0,077 ms | 52 ms | 0,72 ms | 24 ms |
| P1 | 0,080 ms | 25 ms | 0,77 ms | 29 ms |
| P2 | 0,080 ms | 45 ms | 0,76 ms | 31 ms |

Pior caso do oráculo (casos grandes, JS / Python):

| caso | P0 | P1 | P2 |
|---|---|---|---|
| R2-1 | 65 / 95 ms | 97 / 106 ms | 122 / 91 ms |
| R2-4 | 81 / 125 ms | 68 / 148 ms | 76 / 106 ms |
| W4 | 24 / 48 ms | 38 / 45 ms | 42 / 45 ms |

Todos ficam abaixo de 1 s. O P1 não muda a ordem de grandeza. O `aleat_resumo.txt` também traz tempos, mas foram medidos com 18 processos em paralelo e não valem como medida.

## Brutos (caminho e sha256)

A lista completa, com 80 arquivos (brutos, entradas, scripts, diffs e o texto do achado), está em `SHA256SUMS.txt`. Ela foi gerada por `sha256sum brutos/* entradas/* scripts/* var/*.diff ACHADO8_TEXTO.md`. Os principais:

| arquivo | sha256 |
|---|---|
| brutos/tabela_F.txt | ff554f343cda4387bc53747f00667c1324dcfd05a4937844a456023da055e475 |
| brutos/ordem_jan_2e31588.txt | a5e61dbea1fa2b82778fd2c2538e3da1cb7eac33187d06f92c80563b30e15064 |
| brutos/oraculo_P0_2e31588.txt | eb9326f1835a7142a3c186a9c156e9b73ed2ab88f25cdf72259781bb433be36e |
| brutos/oraculo_P1.txt | 7c8fa0b176bc1b173118ddc2412154aab7523855192b37885a43edf9bab94aab |
| brutos/oraculo_P2.txt | cfa3280aa769b1c0036ca97cf64ffb2871804a9996510cf5ae758d27a41f7856 |
| brutos/oraculo_P0nR23.txt | 8475d8a7c2f4a2790b76fafdb8d03c25cf7f29214a6d324713023864883a53f6 |
| brutos/oraculo_P2nR23.txt | 83a59b38799564b56ce77c1bfe15ed00f5f372067aaf62921a4e0477f856a62f |
| brutos/aleat_resumo.txt | f7ee0b361a7e1ef93e863cb403924d6206de1d8ab0561520bf0b53d3fec11381 |
| brutos/perdas_ganhos.txt | d8b8b9b2afabd3a265b905d92325fc2165ea35b05ebe5bbd5cf1573b02c59fd8 |
| brutos/excesso_exato.txt | 552cb14e9b3a91c941d2c4bc09f4aefdb939e7e48fb4964404b44ae98ccc909d |
| brutos/diag_r23.txt | 41d5022206c87f90ace60e8386c53659a6d47c9eeea7cbdc54058690619dc21a |
| brutos/tempo_serial.txt | f02d3036d05e0f761fa581148b0ddc1ac2492d36779f4e2a72426c5bf778e590 |
| brutos/R_py_P0_aleat.json | 649b9e0f0d252e45a396fe5f6983fb234af8f05873fd02eb35f4c287f751754c |
| brutos/R_py_P1_aleat.json | d0fec0a4e17c6f18e447d4eb1bc2c22bb53624549c059a7c2d44b3e96e963982 |
| brutos/R_py_P2_aleat.json | 02866a0bc1dbb38952dacf96315a3621facadea24ceb2b4e9b5d681679fb9ea0 |
| entradas/casos_F.json | 9001ab006dfe020f108b0638ab4159f6dbebf460c3fefde7c767c55a2811c047 |
| entradas/agendas_esperadas.json | 557ba0d4d0d8757a840512d4c2ee38f9a2f07362932d190fad5aafc9ccde11bd |
| entradas/aleat.json | 7f491a5368b44225a11d6d17ecdf57890a7fe2a7818b089fd3792b753851f72b |
| var/P1.safra.diff / var/P1.dados2.diff | 5c2bc4d6…a692a9 / f27408c7…e4e7 |
| var/P2.safra.diff / var/P2.dados2.diff | cf50c92f…1f28 / 13272964…5806 |
| ACHADO8_TEXTO.md | 97adc55ec6c645fa64e7ecbe6e6199844733d96a654efdb9c9ee2f27aa7b7959 |

## Recomendação para decisão do Codex

Não decido por ele. Fatos para a decisão:

1. **Estado em 2e31588:** o achado se reproduz com os números de 04bf6f2. Em F1 e F4 o atendido é 76,67 contra 100 viáveis (−23 %), em F3 93,33 contra 100 e em F5 234,29 contra 260. Os resultados são sempre viáveis, sempre com conflito, e há alternativa segura (reprogramar). É conservador e limitado: **S3**, e não S2, porque nenhum plano inviável é aceito e as restrições usadas são verdadeiras. O motivo "não cabem na janela de 100 h" é literalmente verdadeiro para as partes como teto (140 h em 100 h), mas a janela fica com 8,57 h ociosas em F5.
2. **O que preserva o M2:**
   - **P0 (manter).** Preserva o M2 e o oráculo 101/101, e fica dentro da decisão "não é novo otimizador; sem promessa de capacidade máxima nem monotonicidade". Melhoria opcional, sem mudar números: acrescentar ao motivo que sobram horas na janela quando sobram. Não testei se isso preserva as substrings do M2. Como elas só exigem trechos, um acréscimo ao fim da frase as preservaria, mas isso é especificado, não executado.
   - **P2.** Também preserva o M2 e o oráculo 101/101, mas **não corrige nada do achado em 2e31588**: F1–F5 ficam iguais, porque o corte do grupo inteiro, que a R2-3 põe primeiro, faz a mesma redução que a restrição antiga. Nas aleatórias não é uniforme: 45 entradas melhores e 56 piores, com perda máxima de 33,33 ha. Só teria efeito sem a R2-3, o que quebraria o caso R2-3 do oráculo. Não há base executada para adotá-lo.
3. **O que exige mudar o M2:**
   - **P1 (devolver a folga).** Leva F1, F3, F4 e F5 aos valores da agenda (100/100/100/260). É sempre viável. Atende mais que o P0 em 323 de 6 000 entradas e menos em 24, todas com configurações sem %: a folga devolvida à parte fixa tira horas de uma sem % mais rápida (perda máxima de 8,57 ha, 14 %). Não muda nenhuma entrada sem conflito e não melhora a monotonicidade (478 contra 498 quedas).
   - Para adotar o P1, o Codex precisa mudar o esperado do M2: `q` de `['5/3','2','25/3']` para `['5/3','7/3','25/3']`, e o motivo da janela de 4 h de "fazem de 41,67 % a 50 %" para "fazem de 41,67 % a 58,33 %". É aumento do atendido (+1/3 ha), não correção de inviabilidade.
   - O P1 é um passo de otimização local, com resultado dependente da ordem das configurações, o que toca o "não é novo otimizador" da decisão vigente.
4. **Fora deste achado, encontrados de passagem e presentes já no P0:**
   - o Python "Fraction" deixa escapar float na divisão das configurações sem %, com excesso de até 4,3e-15 h;
   - um motivo arredonda diferente em JS e Python (34,37 contra 34,38 %): S4.
