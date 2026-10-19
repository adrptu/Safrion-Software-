# Pacote do achado 7: trator × implemento 5×6 e 6×5 no teto do teste de buraco

Executado em 04/10/2026, entre 23:14 e 23:50 UTC, por Claude. Os dados são sintéticos e o trabalho foi feito só em cópias (`git archive`); nada em `/home/user/*` foi editado. A máquina estava ocupada com outra cadeia de testes (loadavg de 2 a 11, registrado em cada bruto), então os tempos servem de ordem de grandeza.

Todos os números abaixo saem de comandos executados nesta rodada. As tabelas T1 a T5 foram geradas por `scripts/gera_tabelas.py` a partir dos brutos (`brutos/tabelas_geradas.md`). Uma tentativa anterior desta mesma tarefa, interrompida, tinha deixado brutos nesta pasta. Eles foram **apagados e refeitos**. As entradas foram regeneradas pelos geradores com semente e conferidas byte a byte contra as anteriores (iguais; o `M2.json` só é igual em conteúdo JSON).

## Texto do achado

O texto exato de `rev.json` `itens[7]` está em [`ACHADO7_TEXTO.md`](ACHADO7_TEXTO.md):
- o achado e os dois vereditos, verbatim, cada campo num bloco de texto;
- o JSON bruto no fim;
- sha256 do `rev.json`: `504355e9…021ad7`.

O gerador (`scripts/texto_achado.py`) confere que cada campo aparece byte a byte. Saída: "campos ausentes: nenhum".

Resumo, sem substituir o texto:
- **Achado (S3, não introduzido pelo delta).** 5×6 e 6×5, com rend 2, janela de 10 h, partes de 100/30 % e Q = 600, estouram o teto de 65 536 passos do `buraco` (safra.js:126 em 04bf6f2; dados2.py:325). O resultado cai no conservador: 20 ha e déficit de 290 h. O exato seria 84,80 ha e déficit de 50 h.
- **Veredito 0.** Confirma S3. O "agravamento" não é defeito do delta.
- **Veredito 1.** Confirma S3. Prefere o reconhecimento estrutural de König ao aumento do teto.

## Versão e arquivos

| Commit | Papel | sha256 safra.js | sha256 dados2.py |
|---|---|---|---|
| 2e31588496e704f2ef8d98f137287343466bd61d | candidata (rodada 2 do D-01) | bf4e06d6…c30c69 | 5cd56f15…f51deb |
| 04bf6f2afb67faa5faaeb3b8ae2e57d7924e5bbb | rodada 1 do D-01 | 210f6653…555ac2 | 085370f9…85bea7 |
| ee4f954c9b246667311dc3221bfb5d2e14cb2f70 | antes do D-01 | a9f4588e…a45f5 | 4ea89cdc…fec5689 |

**Cópias** em `src/{c2e3,c04b,cee4}`:
- comando: `git -C /home/user/sp-camada-sintetica archive <commit> tools/prototipo/v37 | tar -x -C src/<dir>`;
- `diff -rq` de `src/c2e3` contra um segundo `archive` de 2e31588 deu igual.

Em 2e31588, o teto fica em safra.js:126 (`ext`: `if(++passos>65536) return null`) e em dados2.py:325. A chamada do buraco, só para quem tem janela (R2-2), está em safra.js:146 e em dados2.py:382–383.

**Propostas**, em cópias de 2e31588 com JS e Python mudados juntos. São geradas por `scripts/mk_variantes.py`, que exige exatamente 1 ocorrência de cada âncora; os diffs ficam em `var/*.diff`.

| Variante | Mudança |
|---|---|
| P0 | `src/c2e3` sem mudança |
| P1 2^18 / 2^20 / 2^22 | só o teto do `ext` do buraco (`var/p1_2e18`, `p1_2e20`, `p1_2e22`) |
| P2 (`var/p2`) | `linhaBip(cf0)`: se toda exclusão entre as configurações com janela vem de ativo em comum, cada uma tem até 2 ativos compartilhados e esses ativos são 2-coloríveis, então o grafo é perfeito (Kőnig) e não há busca. Nos demais casos, a busca atual decide. |
| P2u (`var/p2u`) | P2 só quando todas as configurações com janela finita do componente têm **o mesmo prazo**. Foi derivada nesta rodada, pelo contraexemplo da seção seguinte. |
| cliq (`var/cliq`) | `h=false` fixo: força o caminho das cliques. Serve **só para medir o esperado**; não é proposta. |

**Verificadores independentes**, que não usam safra.js nem dados2.py:
- **`scripts/verif.py`**
  - V0 a V2: conservação, janela própria e cortes por prazo por recurso.
  - V3: programa linear do cronograma entre prazos (θ* = maior fator executável; θ* ≥ 1 quer dizer executável). Na versão V3e, enumera os conjuntos que podem trabalhar juntos (até 16 configurações); na V3b, usa a carga por ativo e por segmento (linhas de bipartido, Kőnig e Birkhoff).
  - Autoteste (`brutos/verif_autoteste.txt`): em 500 grades, V3b e V3e deram o mesmo θ*. Nenhum caso teve V2 falha com θ* ≥ 1, e nenhum cronograma em série construído foi reprovado.
  - V3 ignora a troca (relaxação). Por isso, uma reprovação é robusta.
- **`scripts/verif_matching.py`** (2º verificador, só para grades): enumera os emparelhamentos e resolve o mesmo programa linear de outra forma.

## Entrada

Todas as entradas estão em `entradas/` e são geradas por `scripts/gen_*.py` e `scripts/deriva_listas.py`.

**`casos_principais.json`** (`gen_casos.py`): grade `T{t}+P{p}` com ativos `t{t}` e `p{p}`, rend 2, jan 10, part 100/n %, Q = 600 e custo_h 1.
1. 5x6.
2. 6x5.
3. 5x6 com T4+P5 sem janela (`jan:''`).
4. Caso 9, igual a `prerev7/regressao/perf_casos.json[9]` (cópia `entradas/perf_casos_prerev7.json`; `cmp` deu igual): 5×6, rend 1–3, janelas 2 a 60 h, T2P1 e T3P5 sem janela, Q = 3000, sem parte fixa.
5. Controles 4x5, 4x6 e 5x5.

**`casos_extras.json`**: 6x6, 5x7, 7x5, 6x7, 7x6, 7x7, 8x8, 10x10 e 6x6 com T5+P5 sem janela. No Python, os três maiores ficaram fora de P1 2^20 e 2^22, por custo.

**`contraexemplo.json`** (`gen_contraex.py`, rend 1, portanto q = h), na forma configuração(trator, implemento, prazo, horas):
- A(t2,p0,2,2), B(t0,p0,10,4), C(t0,p1,10,3), D(t0,p2,10,3), E(t1,p1,2,1), F(t1,p2,2,1), G(t4,p2,3,1,5);
- Q = 15,5;
- duas variantes: com partes fixas proporcionais às horas, e sem %.

**`M2.json`**: lido por `deriva_listas.py` direto das linhas 142–144 do oráculo de 2e31588 (cópia literal em `entradas/M2_oraculo_linhas_142-144.txt`).
- Q = 1000.
- A: rend 1, part 30, seq, jan 4, rec plant 1.
- B: rend 1, part 30, seq, jan 4.
- C: rend 1, part 40, jan 10, rec plant 1.
- pools: `plant` com un 1 (Plantadeiras).
- Esperado no oráculo: q = [5/3, 2, 25/3] e motivos com "janela de 4 h: fazem de 41,67 % a 50 %" e "janela de 10 h: fazem de 41,67 % a 83,33 %".

**`adversariais.json`** (`gen_adv.py`, semente 20261004): 71 casos de 20 a 36 configurações.
- trator × implemento 5x6, 6x5, 6x6, 5x7, 7x5, 4x8 e 8x4, mais 5x6 e 6x6 com janelas variadas;
- anéis C20, C21, C24, C25, C29 e C30;
- complementos de anéis;
- 5 multipartidos completos;
- cadeias P20 e P30;
- malhas;
- 18 G(n, p) com n de 20 a 30 e p de 0,1 a 0,9;
- 2 bipartidos aleatórios;
- hipercubo Q5;
- os 20 `perf_casos`.

`adversariais_piores.json` reúne 7 desses casos, usados para P1 2^20 e 2^22 no Python.

**`aleatorias_s20261004.json`** (`gen_aleat.py`, semente 20261004): 3 300 entradas.
- A: 1 500 gerais, com ativos, sequência, grupos e troca.
- B: 1 000 grades médias.
- C1: 300 grades de 26 a 42 configurações com prazo único.
- C2: 300 grades de 26 a 42 configurações com prazos variados.
- D: 200 "quase grade", com 3º ativo, sequência ou grupo de 1 unidade.

**Comandos.** O pipeline está em `scripts/roda_tudo.sh`, e os demais rodaram à mão, nesta ordem:
- `bash scripts/roda_tudo.sh <pasta>`;
- `roda_aleat_py.sh` (P0 e P2u completos; P2 completo; P1 na amostra de 40 entradas C);
- `roda_adv_py.sh`;
- `roda_oraculos.sh`;
- `verif.py` sobre `adv_js_*`;
- `verif_matching.py`;
- `analise_violacoes.py`;
- `excesso.py` e `excesso_aleat.py`;
- `paridade_aleat.py`;
- `gera_tabelas.py`.

O passo do oráculo dentro do `roda_tudo.sh` falhou com saída 127 (`/usr/bin/time` não existe). Ele foi refeito por `roda_oraculos.sh`, e os brutos `oraculo_*.txt` são dessa segunda execução.

## Esperado × obtido

### Estado em 2e31588 (T1; JS = Python em todos, conferido por `paridade_repro_*`; Python também com Fraction)

| Caso | 2e31588 | 04bf6f2 | ee4f954 | Esperado (cliques forçadas, Fraction) |
|---|---|---|---|---|
| 5x6 | buraco **null**/65 537 passos; **conservador**; 20 ha, saldo 580, déficit 290 h; executável (θ* 4,24) | igual | igual | **424/5 = 84,8 ha**, déficit 50 h, θ* = 1 nos dois verificadores |
| 6x5 | null/65 537; conservador; 20 ha; déficit 290 | igual | igual | **100 ha**, déficit 50, θ* = 1 |
| 5x6 T4+P5 sem janela | buraco **false** (29 com janela; 58 035 + 2 869 passos); **cliques**; **1064/11 = 96,7273 ha**, déficit 50; θ* = 1 | null; conservador; 40 ha; déficit 280; θ* 3,84 | null; conservador; 111,3333 ha; θ* **0,6535 (inexecutável)** | 1064/11 ha; θ* = 1 |
| Caso 9 (janelas variadas) | false (28 com janela; 42 764 + 2 468); **cliques**; 3000 ha, **saldo 0**, déficit 255, conflito true; θ* **0,9247: inexecutável** (V3b e emparelhamentos) | null; conservador; 3000 ha; déficit 1340; θ* 2 | null; conservador; 3000 ha; déficit 255; θ* **0,3414: inexecutável** | o caminho de cliques dá 3000 ha e déficit 255, que é **inexecutável** (θ* 0,9247, excesso de **10 ha**: 379 ha com prazo, máximo executável 369) |
| 4x5 / 4x6 / 5x5 | cliques; 265/4, 1260/19 e 1780/21 ha; θ* = 1 | igual | igual | igual |
| Contraexemplo, partes fixas | cliques; 15,5 ha, saldo 0, **conflito false**; θ* **0,9677: inexecutável** | igual | igual | (máximo executável 15,0 ha) |
| M2 | cliques; q = [5/3, 2, 25/3], alocado 12, saldo 988, déficit 690, conflito true | q igual; motivos diferentes | q igual; motivos diferentes | oráculo: q = [5/3, 2, 25/3]; **OK** |

**Motivos em 2e31588, iguais em JS e Python.**
- 5x6 e 6x5: "combinações demais para conferir quem trabalha ao mesmo tempo: as configurações ligadas são consideradas juntas em cada janela nesta estimativa (conservador)".
- Em 04bf6f2 e ee4f954, o mesmo motivo terminava em "dividem a maior janela delas (conservador)".

**M2 em 2e31588: a saída completa.** Preservar como regressão.
- alocado 12, saldo 988, déficit 690, conflito true, decorrido 12;
- buraco: false nos dois grafos (5 + 4 passos);
- motivos, nesta ordem:
  1. "sequência declarada: dividem trator, implemento ou operador";
  2. "Plantadeiras: ao mesmo tempo precisariam de 2, a fazenda tem 1; configurações consideradas em sequência nesta estimativa";
  3. "A: a parte fixa não cabe na janela de 4 h";
  4. "B: a parte fixa não cabe na janela de 4 h";
  5. "C: a parte fixa não cabe na janela de 10 h";
  6. "as partes fixas em sequência não cabem na janela de 4 h: fazem de 41,67 % a 50 % do que cabia na própria janela";
  7. "as partes fixas em sequência não cabem na janela de 10 h: fazem de 41,67 % a 83,33 % do que cabia na própria janela";
  8. "A e C: em sequência precisam de 700 h para 700 ha; a janela tem 10 h".
- Em 04bf6f2, os dois últimos motivos eram "em sequência precisam de 600 h para 600 ha; a janela tem 4 h" e "… 700 h …".

**Tempos em 2e31588** (5x6 e 6x5, que gastam o teto):
- JS: 54 a 121 ms;
- Python: 1,5 a 1,6 s com carga, ou 0,86 a 0,87 s em `prop_py_P0`.

**O que a R2-2 mudou** (buraco só entre quem tem janela):
- **Sim:** a variante com T4+P5 sem janela **sai do conservador** em 2e31588. São 96,7273 ha com déficit de 50 h, exatamente o "exato" do achado, e θ* = 1 (executável).
- O caso 9 também sai do conservador, pois tem 2 configurações sem janela e só 28 com janela, abaixo do teto. **Mas o caminho de cliques produz um plano inexecutável:** todos os 3000 ha atendidos, saldo 0, θ* 0,9247.
- 5x6 e 6x5 com todas as janelas finitas continuam no conservador. A R2-2 não muda nada neles.

**Achado novo, exposto pela rodada (N1).** Em grafo perfeito com **prazos diferentes**, os cortes por clique e por prazo (a regra D-01 que o código implementa) **não bastam** para haver cronograma.
- **Contraexemplo, por raciocínio direto.**
  1. t0 precisa trabalhar os 10 h inteiros (B+C+D = 10 h).
  2. Em [0, 2], p0 está com A (2 h) e t1 está com E+F (2 h). Então t0 só pode rodar C ou D, e C ≤ 2 − E = 1 e D ≤ 2 − F − G[0,2].
  3. Daí C + D = 2 exige G[0,2] = 0.
  4. Sobra para G só [2, 3], ou seja, 1 h, para 1,5 h de trabalho. Logo, não há cronograma.
- Os dois verificadores dão θ* = 0,9677 e máximo executável de 15,0 ha, contra 15,5 ha atribuídos.
- Isso existe nos três commits: o contraexemplo dá o mesmo resultado em ee4f954, 04bf6f2 e 2e31588, e na versão com partes fixas sai **sem conflito**.
- **Nas 3 300 aleatórias, em P0 = 2e31588:**
  - 276 entradas inexecutáveis (B 92, C2 179, A 3, D 2), todas por V3. V2 nunca falha, ou seja, o código cumpre a própria regra.
  - Todas têm 2 ou mais prazos; nenhuma entrada de prazo único falha.
  - 119 dessas 276 têm saldo 0.
  - Todas as 276 têm `conflito` true.
  - θ* mínimo 0,786.
  - Excesso: até 13,8 ha, até 11 % da área com prazo e até 10 % de Q (`excesso_aleat.txt`).
- Brutos: `analise_violacoes_aleat.txt`, `excesso_*.txt` e `verif_matching_*.txt`.
- N1 é anterior ao achado 7 e não depende do teto, mas toda proposta que manda mais componentes para o caminho de cliques **amplia** N1.

## Propostas e efeitos

Detalhe completo nas tabelas T3 a T5, em `brutos/tabelas_geradas.md`.

| | P0 manter | P1 2^18 | P1 2^20 | P1 2^22 | P2 (Kőnig) | P2u (Kőnig, prazo único) |
|---|---|---|---|---|---|---|
| Oráculo (101 casos; M2 OK) | 101/101 | 101/101 | 101/101 | 101/101 | 101/101 | 101/101 |
| 5x6 / 6x5 | conservador, 20 ha | 84,8 / 100 | 84,8 / 100 | 84,8 / 100 | 84,8 / 100, sem busca | 84,8 / 100, sem busca |
| 6x6 / 5x7 / 7x5 | conservador | conservador | exatos | exatos | exatos | exatos |
| 6x7 / 7x6 | conservador | conservador | conservador | exatos | exatos | exatos |
| 7x7 / 8x8 / 10x10 | conservador | conservador | conservador | **conservador** | exatos (125,24 / 145,87 / 187,14 ha) | exatos |
| Inexecutáveis entre os casos principais, extras e contraexemplo (V3) | caso 9 e contraexemplo | idem | idem | idem | idem | idem |
| JS: pior tempo nos principais e extras (mediana) | 210 ms (10x10) | 764 ms (10x10) | 3,3 s (10x10) | **12,1 s** (10x10) | 9 ms | 17 ms |
| Python: pior tempo medido | 3,0 s (10x10, gasta o teto) | 10,6 s (10x10) | 43,0 s (10x10); 6x6 em 9,1–10,1 s | **176,8 s** (10x10); 7x6 em 55,2–58,0 s | **52 ms** (10x10) | 54 ms |
| Adversariais (71 casos), JS: pior / casos com estouro | 358 ms / 8 | 308 ms / 4 | 503 ms / 0 | 525 ms / 0 | 342 ms / 1 (hipercubo Q5) | 337 ms / 3 |
| Adversariais, Python: pior | 1,17 s | 4,4 s | (só os piores) 43 s | 177 s | 0,81 s (pares12x2, não é grade) | 1,10 s |
| Aleatórias, Python: pior | 2,97 s | 7,8 s (amostra de 40) | 9,1 s (amostra de 40) | 7,5 s (amostra de 40) | 0,19 s | 2,22 s |
| 3 300 aleatórias: inexecutáveis | 276 | 310 (**+34**) | 319 (**+43**) | 320 (**+44**) | 320 (**+44**) | 276 (**+0**, o mesmo conjunto) |
| Aleatórias: igual a P0 onde P0 conferiu | — | sim | sim | sim | sim | sim |
| Paridade JS × Python | 3 300/3 300; 71/71 | 40/40; 71/71 | 40/40; 7/7 | 40/40; 7/7 | 3 300/3 300; 71/71 | 3 300/3 300; 71/71 |

Leitura:
- **Todas as diferenças em relação a P0 estão em entradas onde P0 estourava o teto.** Nas demais, a saída é idêntica.
- **As novas inexecutáveis de P1 e P2** são todas da categoria C2 (grades grandes com prazos variados). Elas saem do conservador, que era executável, e caem no caminho de cliques, que tem a lacuna N1.
  - Nos adversariais, "trator×implemento 6x6 janelas variadas" passa a dar 164,96 ha com θ* 0,9952.
  - Portanto, **P1 e P2 passam a aceitar planos inexecutáveis que P0 não aceitava.** Isso decorre de N1, não de erro na mudança: o reconhecimento está certo, porque o grafo é mesmo perfeito.
- **P2u** só dispensa a busca quando há um único prazo finito. Nesse caso os cortes de Kőnig são exatos para o cronograma (autoteste V3b = V3e).
  - Nas 3 300 aleatórias, nenhuma nova inexecutável: as 276 restantes são exatamente o conjunto de P0.
  - Resolve 5x6, 6x5, a variante sem janela e todas as grades de prazo único até 10x10, em até 17 ms (JS) e 54 ms (Python). Fora delas, o tempo é o de P0.
  - **Não resolve** o caso 9 nem o contraexemplo, que dependem de N1.
- **P1 só adia o problema.** Com 2^22, 7x7 continua no conservador. O custo no Python passa do limite de 1 s cobrado no oráculo (Q5/V6), com 9 s em 6x6 já em 2^20, e no JS chega a 12 s.

**Ressalva de cobertura do verificador.** Nos adversariais, 54 dos 71 casos não são grade nem cabem na enumeração (mais de 16 configurações). Neles só V0 a V2 foram conferidos (`verif_adv_js_*`, motor "não aplicável").

## Brutos (caminho e sha256)

Pasta base: `/tmp/claude-0/-home-user-Safrion-Software-/65558514-68d9-57f5-9da3-513cd6735cdc/scratchpad/r2_7_8/achado7/`. A lista completa, gerada por `sha256sum` sobre `brutos/`, `entradas/`, `scripts/*.py|*.js|*.sh`, `var/*.diff` e `ACHADO7_TEXTO.md`, está no fim deste arquivo.

## Recomendação para decisão do Codex

1. **Achado 7: reproduz em 2e31588. Severidade proposta: S3**, mantida e não introduzida pelo delta.
   - 5x6 e 6x5 seguem no conservador (20 ha contra 84,8 e 100 ha), com resultado executável e motivo explícito.
   - A R2-2 já tirou do conservador a variante com prestador sem janela, que dá 96,7273 ha, executável.
2. **Adotar P2u** em vez de P1 e P2:
   - reconhece o grafo de linhas de bipartido sem busca, só quando o componente com janela tem um único prazo finito;
   - oráculo 101/101, M2 preservado, paridade 3 300/3 300 e nenhuma nova entrada inexecutável;
   - nas grades de prazo único até 10x10: até 17 ms em JS e 54 ms em Python;
   - nas demais entradas, o custo é o de P0, porque a busca continua (pior caso no Python: 2,2 s nas aleatórias, contra 3,0 s em P0).
   - Incluir no oráculo:
     - 5x6 com 424/5 ha;
     - 6x5 com 100 ha;
     - 5x6 com T4+P5 sem janela, 1064/11 ha.
3. **Recusar P1** (custo de 9 a 177 s no Python, não resolve 7x7 e amplia N1) e **P2 sem a restrição de prazo único** (amplia N1: +44 inexecutáveis).
4. **Abrir N1 para decisão própria.** Proposta: S2, porque é plano inexecutável aceito.
   - O contraexemplo sai sem conflito.
   - O caso 9 sai com saldo 0 e excesso de 10 ha.
   - Nas aleatórias, chega a 10 % de Q.
   - O texto atual afirma que, em grafo perfeito, "as cliques bastam (W1)". Isso só vale com um único prazo.
   - Opções:
     - (a) caminho de cliques só com prazo único; senão, conservador. Barato, mas o caso 9 volta a dar déficit de 1 340 h;
     - (b) teste exato por segmento entre prazos (carga de cada ativo por segmento, como o V3b) para linhas de bipartido;
     - (c) aceitar como limitação documentada.
   - A escolha é do Codex, que é o dono da regra D-01 e do "não é novo otimizador".
   - Ser anterior ao delta não aprova nem rejeita N1: ele já existe em ee4f954 e em 04bf6f2. A R2-2 de 2e31588 só aumenta quantas entradas passam pelo caminho afetado (exemplo: o caso 9).

### Lista sha256 (gerada por `sha256sum` em 2026-10-04T23:45:43Z, caminhos relativos à pasta base)

```text
722a656965b4b9c85c07d7c2c384131894fa221e55356e653f6283798eb7d6b3  ACHADO7_TEXTO.md
489738b83ddcfbe7cc3eadee94c8292db3fbc24c381c7df85dc6f490048c2beb  entradas/M2.json
cc775ed150fd21a9425b8d444c2f27a82cc667a53a2aa6ec45654e09639b35b6  entradas/M2_oraculo_linhas_142-144.txt
12768fbe75a0213a0e6f374b74734115b988301e5e6eec4705c218ba266a7028  entradas/adversariais.json
a094e670d9055c3c93378ea625fb7d215623c4175ad7416e83b85ca55701b712  entradas/adversariais_piores.json
0622b1094fe7d80ce927171a0ae7b7aafe94802bb7fe96a1c6dadf139386005b  entradas/aleatorias_amostra_P1_py.json
68d35f4d5f5bd222d2ce0a30cbb801dbeaf19b42e15322ec596797fb1f283ef9  entradas/aleatorias_s20261004.json
8d497c0fbda25befd1f318bef020a3c426cfe003e0016fb884b46d136adad7be  entradas/casos_extras.json
fb147ef1fe3ce48c0c7a2a2c52551aa195bae75cc2362e350c6b0fe9479930f8  entradas/casos_extras_py.json
6bda5d285c0aa930c7e9ea6ee11216579752fa6c0571cfe280b725a76b798c09  entradas/casos_extras_so_js.json
4fadea30f1b49449fbba5196aa6710087dba91171e1a48c3784123d43539f31d  entradas/casos_principais.json
22de4305f97003a67c4557be8577988cb762470356bd79cf91f7f729b4683607  entradas/contraexemplo.json
10cd18d25b5418049eb6aaa04adefd45821d43a033133a844ea8faf1e1cbcda3  entradas/perf_casos_prerev7.json
e104f086512da5792c18ada63ffa9efd17cdbd4dc3c35f3e674c5b23f8723c73  scripts/analise_violacoes.py
cac37c7fb7de9468a06653b2fa7e49dc49752c7b2d404130a47e7382e4213023  scripts/deriva_listas.py
22c5dc5951c5335daeb294b2094b579f7fe72534f8d4d180fd1188e096d26328  scripts/excesso.py
1260cee53bd5a45124619ab2d0ce45ddaf66941c6b3909c43a45cd76fd29c3bf  scripts/excesso_aleat.py
0e5396b2257412c9dc7bf9a858aaaea6be214c71f7898a2734e6a7a81ae36e04  scripts/gen_adv.py
e426bdc49bdeb17bebca733ac293384ca63a7da0f74c5c178c43226cd3b79f76  scripts/gen_aleat.py
912b6a01791cf6daf40188ee78c7da959a7561001beef0c7e623925ef88d0f81  scripts/gen_casos.py
294e8c1f102d273af643edde0f5fea3128643f033634223bca46879ca9a9025f  scripts/gen_contraex.py
1c61d61563b68a14b83663f6bd04bd5d19a712987c91d27c414568c7ef6c1707  scripts/gera_tabelas.py
a518baa2c685a4285f4bfe2b1bd7dd91494eeed05dfea65a6d380b16a1622385  scripts/lib.js
a21c099e14c4b9e626838738083640b1399dd7c7565e1823b4b891ee3d90349e  scripts/lib_py.py
9003e8a32420968a6c7936310393d0ef5622ec1bb8e060556c00251955e9cfe5  scripts/mk_variantes.py
7c53fa8d65a1704c85d28fd40bda101e5af0d6ee5fc11b4250f8c4e6d1a364a3  scripts/paridade.py
36261950dd2faf1a5c01752307bb93fc5131a60a6835367259dbed90e50a5dd9  scripts/paridade_aleat.py
bad4e4784122dfd8e92ec8076693fe1616541e910c7b71e7c39884ccc08abb1a  scripts/resumo_aleat.py
33b0c3ab5edb41f58e7a274b97b13af8974194643767feef211ce7b731837bb6  scripts/roda_adv.sh
2aa0661a32b6160148c234c1ee11ee5e3c3ec99472cb371c6d9968fa550f786a  scripts/roda_adv_py.sh
f0b5410bd1cf5296527ce2a6f91d6167d707efd22c06badb181f9382d0f012e9  scripts/roda_aleat_js.sh
7a7e6e6853a2b4823f04145ab718e4512197491906eac8a6a60b2dbc6ea88529  scripts/roda_aleat_py.sh
d087233dced1647c6db0d794536f540bca1686c5dc0eec900f9b4ddd5a1c35a3  scripts/roda_oraculos.sh
7b85d81565db6b1a1ccb037c37ced5ea54d6bae2c3007f091376e05fc5eedb69  scripts/roda_tudo.sh
cf2e9a714c01ef2521dfa3a977ac176d315b7356a5631abb51ae011d1e9c4b61  scripts/roda_var_js.sh
c1891180f72e931ce9d365c807ef6455df9e5834d5048c05c13c939160d000cc  scripts/roda_var_py.sh
efa9ac5164972a079aa36dfb78b03704391dd1eb911fa516860b9e4c2a676bdd  scripts/run_js.js
e35fcd87ffd4b50c7146027c40c8f24f5733fa2743638c51607df890f46990db  scripts/run_lote.js
db664181518fd5e3f9ecd082e38681b40f3a09380d9b7761438dd26d39576542  scripts/run_lote_py.py
53f5d4cda5b7cb1b2c5894103c21b9b9cf0af474e4554720257b68803e1cf8e0  scripts/run_py.py
bf8ca83704074977e58c3a5497ecc86169497b9f134fba9da2922e8958513c5d  scripts/texto_achado.py
ee777ef227ebcb076338967d0484fc772357072b3a5bffaf14dc28d643a54fe2  scripts/verif.py
f00b56d9025acb6d04b9f4d84732efedc062cbc01945ced5d75c1789babf1170  scripts/verif_aleat.py
fa672140777e4f491b96d7d509287bb0f480da3a70a4ecab1fe91f4475cf2a48  scripts/verif_autoteste.py
89e8c3168e9fde4a05882442816b4e9211eba5cdb5c8efe0eefbcf2c8ffa47f2  scripts/verif_lote.py
b16b1e413432b66bce08b8ddf15fbb7eb86083b3a40df6b3f3de5406565a1abf  scripts/verif_matching.py
a945b2670d1ff6facd4702f1f86aed4b34b0b129d33ec7961a1b565b5350c659  var/cliq.diff
296b869fe5459eabd8998d4c5524c3dd1c814f81c712cb2b8c0ba30123e23f8b  var/p1_2e18.diff
cdbf518035255e1fa62fc1abadb39bf761fd926c6bc1e60dd609521898e8149a  var/p1_2e20.diff
101702181d878dfda5f71006dd3f445c53f66908e677deefea922be5fbfc75fd  var/p1_2e22.diff
600dc0d732289613a701e78c18f34ccc18a02fd40f725676a46212b26385cd7c  var/p2.diff
c13ab25247fe570dacc948ddb1f41e30e2b989b271fd656552362a0b98b760b5  var/p2u.diff
692a6054eddaf786b6dc627b6d59cf250c5fd6d72f2ef881784798d159929d77  brutos/_adv_py.log
968550167e3a7fafe9388a333fd103e0c4fd82054ed3f1b37e480bacc4c4fd0f  brutos/_aleat_py_1.log
aaff4016daf71513cedce0ac10dcd12b8a64c2a753c8f48e08d3b31babf46e0b  brutos/_aleat_py_2.log
070e4164b5dade299ec5e5087b7e4afcf459aa1cfc0263c2d87895aee39515fb  brutos/_js_adv_mais_extras_P1_2e20.txt
5f4e5d4bbae387512f3006dfbabfa375bf4ba4b25f44216cdf756a16c56e0d5e  brutos/_js_adv_mais_extras_P1_2e22.txt
835fcc4b21f00163ae1352093519b20adedd25715ad690e2fafca23c71897350  brutos/_oraculos.log
d9f8193bc9600919d8317f660b0decd44e94cf56fae4875afb0ec272f39ff20f  brutos/_roda_tudo.log
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  brutos/_roda_tudo.out
eea65293a38a8bb4e7a62d3ae42c035b204a9666f4ff782aa50c764c33ae937a  brutos/_verif_aleat.log
5160046adfa289c009344b0af476de4cf908fcf0da3dd0a570fd59073801742e  brutos/adv_js_P0.txt
e61efccbd784266f0a906282884ab2b18aa6d17bbc72e7cd8d2756398726b1dd  brutos/adv_js_P1_2e18.txt
f474bee197d19313c1479369481ba42ed5f8e78463f7621cdd5e4ee3d41faf01  brutos/adv_js_P1_2e20.txt
3956b01810ff1fb149392faf816c07f5ad7ba21dc20c77530b8c2db5cbc45c85  brutos/adv_js_P1_2e22.txt
d962c2abb06cb4a3a493dcd3e322f8e19d62057b3f3b03311a565cfd5ccedcb5  brutos/adv_js_P2.txt
c9977ba75ac5e85d10f82090cddfdaa204873f458516be98a4878c3ae9b4f93d  brutos/adv_js_P2u.txt
997d92410f1c91c4d2696741e52a18eafea26041b4c7fab2a8805212e8604133  brutos/adv_py_P0.txt
23af8d472d3e555a69ffb6f52c2251ad2c589b07930af5ea0be97172b98c520f  brutos/adv_py_P1_2e18.txt
493b5d24b931c93a95fe86e6f94e3c9ceff978abe5e510b0f5a9896c8faa81dd  brutos/adv_py_P1_2e20.txt
9d631cbb7fdf7632b60a7939797706bd5f69e37a77dd81b30242cb40f8ab9cdb  brutos/adv_py_P1_2e22.txt
0ff489f9947bd11d6f9bb8a1be4426699532ecf2936595285dca6ee68974d32a  brutos/adv_py_P2.txt
c962555b106d956b2f92ad67d7da3ca0d595418eef1bc0b6fad62af90b88ea29  brutos/adv_py_P2u.txt
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  brutos/aleat_js_P0.err
78c02dbe2cca96aaed9e9f54870ab0de356aa2b3aebcf43ab719d721ed484997  brutos/aleat_js_P0.jsonl
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  brutos/aleat_js_P1_2e18.err
62871f6d05086fe33d327956a9880b4fa983c80bb2414223dcceabec0c633b74  brutos/aleat_js_P1_2e18.jsonl
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  brutos/aleat_js_P1_2e20.err
0dd072ad38a492aa0b3981f48463488e2215ac1c8f90b0fb90449df97acf2a01  brutos/aleat_js_P1_2e20.jsonl
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  brutos/aleat_js_P1_2e22.err
70a218b5b60ccba2c8126d9585822bd6d54eba7c523270617eb20608ddf36c46  brutos/aleat_js_P1_2e22.jsonl
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  brutos/aleat_js_P2.err
22b341a60750feb3072f79eef0c4fa138440ac9a7b2fd6790d257962a2fbdcd9  brutos/aleat_js_P2.jsonl
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  brutos/aleat_js_P2u.err
105b93600380e6e20c2ebea8b14bedf8a5708ba2df709b625a3c51713949f778  brutos/aleat_js_P2u.jsonl
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  brutos/aleat_py_P0.err
5c339a57dafd98e67d034e35148f8918161fa6dbb74c7c305a4dbec04b0750ff  brutos/aleat_py_P0.jsonl
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  brutos/aleat_py_P1_2e18.err
f67259a80a88252ed845c88dd2edfe4a7bac6544066e57b9004d1f2594ba6f75  brutos/aleat_py_P1_2e18.jsonl
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  brutos/aleat_py_P1_2e20.err
5584afb542494c6b02fad50d1e8f338491a65c46c189c1e63c8992045568ddaf  brutos/aleat_py_P1_2e20.jsonl
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  brutos/aleat_py_P1_2e22.err
dbd894ed341b315ef2be76f502528aa9b1e4108fd34c2f7edd857312111fd63e  brutos/aleat_py_P1_2e22.jsonl
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  brutos/aleat_py_P2.err
a7c61aba44bda8ddfb5c4cc372043c4f65c55293d51adddcf48ea76d8b0a164d  brutos/aleat_py_P2.jsonl
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  brutos/aleat_py_P2u.err
20741c93e50fd01265e5f805440ebde06c4e38bdeaa0aa732c5f74f07dedaff6  brutos/aleat_py_P2u.jsonl
60271caf4f12a3631094fd1f3ebf21e1b89dabb0fb4cce3b9672c93c95c00b3a  brutos/analise_violacoes_aleat.txt
95b247a36d6bdce54f440fed9ddb5de253773d7d73db6afbe8dd46e4711de76d  brutos/esperado_cliq_js.txt
678b31d1ab9a73de1c03d6476d23bf3658ba339113d4918b938f847d357c4819  brutos/esperado_cliq_pyfrac.txt
29cf4862a4e07f6b547e5d5474c84a675f56a989fc72c89a2ace847cb01ce152  brutos/excesso_aleat.txt
e112a528e3c9827aaf6258f08a4866a4b3fca730154a87bc3f37860b7a8f4e89  brutos/excesso_repro_c2e3.txt
a2e5217233d9f24c91670091a9e51a4e01de83d9bff1e9fa8beabd3da835e8ce  brutos/oraculo_P0.txt
cfdbb5a7a1772f62c7d0bad61139444f02423443b9f7aa29d23e16485c02225d  brutos/oraculo_P1_2e18.txt
df7b3f5e9663a093e26c0205eb8055a879bbc2a1ed3c5b0086bf5f759d55e5b6  brutos/oraculo_P1_2e20.txt
7d875d0978d7010663d4e4324fc4ea1ef0b3504e1d40286f7472e558f88a0f5b  brutos/oraculo_P1_2e22.txt
c5a0ec1b1b77eed5802d2e5f47e9c187a486759e85a6905421b586c885eb5552  brutos/oraculo_P2.txt
f0c77e8d937a7799f595645388253e81af5d7f3bf4aa4451eb35b515e2f0cffd  brutos/oraculo_P2u.txt
7c6b9f5eb52ee299c1199d2d402be50b590457d2087a343a4c0e9718c5c5ae42  brutos/paridade_P0_casos_extras.txt
a8e115a4ac7852a644d89dd149831885251dac78000b86fba8c0aca513bf09de  brutos/paridade_P0_casos_principais.txt
8b22078cf57e85cb8b06a78aacfdd7712dbbd1d568c0ca91e399b2ed05f3af2b  brutos/paridade_P0_contraexemplo.txt
7345f101953e56d6222b513def6af62f8e68142052db81b88482bfc9d22f7236  brutos/paridade_P1_2e18_casos_extras_py.txt
b253672e8586adcf16eefa0066fbc07f64563cff89a9659aa9ab95464bd02091  brutos/paridade_P1_2e18_casos_principais.txt
41bb89987c0594312ff4d4037d8cbd9f25a025ee0649fd8937ee21d01245afd7  brutos/paridade_P1_2e18_contraexemplo.txt
0199c530902ace9c7b8d940444f43c4b3e9ddf954d1e9e1e45415108dec15c10  brutos/paridade_P1_2e20_casos_extras_py.txt
812cac5818ec922cac470e7216c2d8058e43cd74789e025e109b705d9e991d15  brutos/paridade_P1_2e20_casos_principais.txt
81fc6040a023f1c6f43fa9e0c4391036eba902862142566c00cb33b3cfee10e8  brutos/paridade_P1_2e20_contraexemplo.txt
0dfd5020e6d380b9bf2f06bbdc3f95e86c1564d19452012fa9f5594babc865a1  brutos/paridade_P1_2e22_casos_extras_py.txt
622081f60927f7f165a8c78842990e21eec95935c47cb288ceb5fb32e817179e  brutos/paridade_P1_2e22_casos_principais.txt
dfebb5f103e28b42225997d6ff70a2e31daad00ccb338486934ec74c69085a3f  brutos/paridade_P1_2e22_contraexemplo.txt
c61c2309af0a0b83b7f829c08ec43731e6233562d760f308471b167990686eb6  brutos/paridade_P2_casos_extras.txt
d21e685e36cebcd35e3868d11045fd272d11f00a0d9cce5c51231446d5428c8b  brutos/paridade_P2_casos_principais.txt
70d4977a10aebf5febecc5f90bcf21aa2c2fc57f3434cc78438a7cb604723e05  brutos/paridade_P2_contraexemplo.txt
8753260d49715c6a08a5d2b3bd05ec858278c86b8db600c391a8f27aa4fa4892  brutos/paridade_P2u_casos_extras.txt
9e6f990ebd3f106b97b5ed3c377d030ad44535f1d752d1fe42577b36b951b83f  brutos/paridade_P2u_casos_principais.txt
03ed8300bb7a08ac66d30a243c941dc9257e90751ef66621c771b8fbdb7a750a  brutos/paridade_P2u_contraexemplo.txt
dfd262ee1ba0e28d6e8eb93679c9bdf9c0a8d5d67723a19b9a9f9067af8cb2ce  brutos/paridade_adv_P0.txt
ad15bf11a2ecfd9a121723fd7458e0dae30ed26a3b19df260b47c138bb871c39  brutos/paridade_adv_P1_2e18.txt
03501014341205502a04c8f33424125b50e9e19416b19b4c149b31a5a6d2fc95  brutos/paridade_adv_P1_2e20.txt
90b71c4f3193b89210125e2cc84314dc8dce2d3f86b3ff093ae893bf42bd42bc  brutos/paridade_adv_P1_2e22.txt
5b4685d095498799256facd831edf2db67b21f5a6aecf3d93fa6f4450a1921fa  brutos/paridade_adv_P2.txt
9e56c7e96ade2beef6ea3e65cd88ae8dda140de9b94729cdd002c43fdb23018d  brutos/paridade_adv_P2u.txt
d4156f1a79f1cd606fccd03d33bab61a2723791f2f53b7b8cd09aaa072a2b7af  brutos/paridade_aleat.txt
2e022fe59afa569de060e51d64f869d626c663425c7d8c82b40b24b03c8635ac  brutos/paridade_repro_c04b_M2.txt
1bbaa33d345b8df3113a8e34d18974958dbe6764ed4c2ddb7d7b72e5d001a409  brutos/paridade_repro_c04b_casos_principais.txt
972549c4ad5e65eee5ccd9ef5fd52e736f482145606f5c9d383497037cf73255  brutos/paridade_repro_c04b_contraexemplo.txt
35b7874b3aa7bd7e9092c99bd72a707f9af04d05aaef8189214902632951ed33  brutos/paridade_repro_c2e3_M2.txt
cd94b0549d99649301ef92c041f16bdcf2f33306cc78e0f0e38e6e719fe5317b  brutos/paridade_repro_c2e3_casos_principais.txt
84895b6a06409364ae206bd3271e45ffc5fb165f631ab7c9979cd4d1801bc6da  brutos/paridade_repro_c2e3_contraexemplo.txt
9a273995a2f02785d1946aab6e48e5e8baaf427d42abd91b6a1331b8de45739f  brutos/paridade_repro_cee4_M2.txt
fcefce2d2c87c62e0545b7edc982307731cdc59878d94a3cc33ad35aeb6f66b1  brutos/paridade_repro_cee4_casos_principais.txt
20bf8ed76d8431764c8e0a4b369b28cec1546554c933ee1c3ab941e248f36d93  brutos/paridade_repro_cee4_contraexemplo.txt
6ef4273e4744ad7711f903b4a7eca7178fe6fa2511816c7025c357a826141369  brutos/prop_js_P0_casos_extras.txt
28f06de65223d8ba50746fcd3e0529f16805830668bde5e1b15485f50897f923  brutos/prop_js_P0_casos_principais.txt
8e0c559cbd25e00ac84237cf7f5de72a1a00976d2e8f1c9190d9f0744f6396b3  brutos/prop_js_P0_contraexemplo.txt
7cddbea9759a76aeeb40aeb2c0028db0e99fa9322b534e8ad59a99c4690c9754  brutos/prop_js_P1_2e18_casos_extras.txt
9600796342414c45792a75b4c7c5801f5de043f2cfe83a70cc8579be9a401c59  brutos/prop_js_P1_2e18_casos_principais.txt
34e2e3313d9d87d7def05380a3ea70ca5bbda024f05cb0a3ac2dc0d585438a6f  brutos/prop_js_P1_2e18_contraexemplo.txt
3fd5a3422023be73c29bcd0b27a6cdbeb58bd4edc62449baf5057ce3768a5474  brutos/prop_js_P1_2e20_casos_extras.txt
4ffa9b2f0a9901f3bf0b1c1788dced16008afec2a7e45f5ef0371f1c5daa1e0f  brutos/prop_js_P1_2e20_casos_principais.txt
bfb2bb8ca718d6b9ffdfa3c7813ab843315badc3abc1fa001cea3f53964e89d6  brutos/prop_js_P1_2e20_contraexemplo.txt
4b1f4859b1994d966672e9cc05214a07b437bc096a5c5fe09f14b794f5782c49  brutos/prop_js_P1_2e22_casos_extras.txt
c3ee60d9baf88c0627576dbb44f24a49744f4c79fe537fac1c988050800f2c01  brutos/prop_js_P1_2e22_casos_principais.txt
527ebc714745502da60119f77fed439bd6108009bc247cb73a4f4d938722cabe  brutos/prop_js_P1_2e22_contraexemplo.txt
bdf242c80df2b42278abcb0d6db335d1df4ee17f0b9bdc37b712e77e308c866d  brutos/prop_js_P2_casos_extras.txt
9f25cdcfcda45a9d1c193d2293daa3a9942ca7c514016a5a6e313fabc8160f32  brutos/prop_js_P2_casos_principais.txt
5dd3809bf0b313b41e5714b376bfe7bd69086ab7309afc79feb33a3a0d34be27  brutos/prop_js_P2_contraexemplo.txt
1b14a017437f0ed788e21784dd06f06d080a3f4565b86b635aba291a53e87de9  brutos/prop_js_P2u_casos_extras.txt
a4b20fd815f529b69cd8be937908d559860eefe9bab759b188bcf607c27d193b  brutos/prop_js_P2u_casos_principais.txt
08e2cf2066ca7e4642f2df8bf6d27753121f6548da69825153589e5de7fc180b  brutos/prop_js_P2u_contraexemplo.txt
878bcb7f833d49ab5fe7c88660f6111a17a22a11bfd8548dd069f589f358c68c  brutos/prop_py_P0_casos_extras.txt
054770b17a4822fc21adb5596fa9fcf4837fde9604152a296ddd13d82682d252  brutos/prop_py_P0_casos_principais.txt
b6131c52a655c07d45e284c6706f7e1ba57ec22af3e670a6cccbd1009f95bd20  brutos/prop_py_P0_contraexemplo.txt
f588e5b0db2ce54cb4a553ea3563433147448022a4f404f89fe8e4889e698742  brutos/prop_py_P1_2e18_casos_extras_py.txt
0491c2d1307b5a753efc03740b5c26a5f76173f991229c2bd2088adfc7323394  brutos/prop_py_P1_2e18_casos_extras_so_js.txt
dc09952f2b822625bf024e77d8937c72d40262d393a4ac15d4c91e9bd50c7f19  brutos/prop_py_P1_2e18_casos_principais.txt
2cce79a7f6b8d5e2cf08d69ad801950e77d27d2881044ab9e7f77dde51554375  brutos/prop_py_P1_2e18_contraexemplo.txt
25941ca61d256d659b22434ce3ea3ba1e66a94f684585fe51baca85b3fd9c712  brutos/prop_py_P1_2e20_casos_extras_py.txt
bba22cc0f68bb25648f5c5a1df56ed7b8aceebc902ef19ac640d3b216d45c42e  brutos/prop_py_P1_2e20_casos_principais.txt
9082b53d0e5275fbeeb89480152f44225f276cd7264d811e0f477bacc256542a  brutos/prop_py_P1_2e20_contraexemplo.txt
0191f5079be9096c4125ee459d3d7a550b214178f20aed2085b4484e619f9044  brutos/prop_py_P1_2e22_casos_extras_py.txt
afa5e466520d443907f2a871b690115bb17f76b674733ba7522b20384bfb3415  brutos/prop_py_P1_2e22_casos_principais.txt
767b8f05c6cbeebc2adb9ad2b289514cf0c20d13cbf1373cec2ef8bea4bf4f1c  brutos/prop_py_P1_2e22_contraexemplo.txt
c289db4ddec8f511b2b1fdf49edc0406567dd4b73f3a241ef73a49924ea4e40b  brutos/prop_py_P2_casos_extras.txt
24cd8f7dfc0f521a96f41befe259099ef3ec011ae9685eaa334d5d2a60cd3dab  brutos/prop_py_P2_casos_principais.txt
b614a113f9ebeb7d6a38f409e796a0fa0a1ca0c3514e007da88431ff10b210ad  brutos/prop_py_P2_contraexemplo.txt
9713cda3431abc595760fb8855cf596e1c7d2a53f39816f4da8808f0682dbb8a  brutos/prop_py_P2u_casos_extras.txt
cd909a21d064d7d112486e14aa1c7e3d234f3c2c9f087f23d678c817034dc4dc  brutos/prop_py_P2u_casos_principais.txt
2e26dc2406fef17912c3d46767d8098cc8a5d12248a154d02efa830f9fa5775e  brutos/prop_py_P2u_contraexemplo.txt
910f5fc3dc7fd4b4fbec6c39990811135d27231c29cf539d57e6e1dd07b485db  brutos/repro_js_c04b_M2.txt
65e1e5b5212a337fb4323933cae1a570f4bd9de747636b0bd1fa4858e8886f10  brutos/repro_js_c04b_casos_principais.txt
2adcd9c367bf10a571e1a7e6845b12df123859043ec6ba858b575d6cb7eb2bba  brutos/repro_js_c04b_contraexemplo.txt
954d11cd312c5a884bc7f4443e11d44d730d94d8a3ec76465e7fa0099c6df7d8  brutos/repro_js_c2e3_M2.txt
2fb2b58c2d38f9647e94d6dad78957eb83a4b45783a7ac17a14180d0b645fa67  brutos/repro_js_c2e3_casos_principais.txt
bc7a40e597ebca88bb22f6c5fbe9f538e6e5310522ac6b535d483e22d55b0094  brutos/repro_js_c2e3_contraexemplo.txt
a6b2f3e8ffdbc09147b324de4d115a22a5f7cff8b754a089ce69995db715a78c  brutos/repro_js_cee4_M2.txt
571aa1e7f71c711893163a0804ca7585f047ee1da9daab2445b2ce19292045e6  brutos/repro_js_cee4_casos_principais.txt
9fb7bd712cb3987335951e3e7e6becdb17d12ecbd360becc01f2fc721ec10aeb  brutos/repro_js_cee4_contraexemplo.txt
7b72f04b23664699caa1edee178e518b2a1af90577d00400a55f82758c1c1a5d  brutos/repro_py_c04b_M2.txt
3215eda27d2ea701ade3b4e9a20300132398ca0860b3d809bb9e730e8ee7b686  brutos/repro_py_c04b_casos_principais.txt
91c5921d628cd172a21cd74f5a5d10c7667dd31759ddb941688b1f55185c4100  brutos/repro_py_c04b_contraexemplo.txt
cab59b941a7cf442097267dfda91c96d35b1c1a842e9f01d8c59a2de99e7385f  brutos/repro_py_c2e3_M2.txt
71e3dc59da761118b0021ea6161f21d7d05d8939c2112456935d2f7961cdbe13  brutos/repro_py_c2e3_casos_principais.txt
a92ff68848cd998c5f097090e042222e44fe87f2c845b523cbf5c01da49f2e04  brutos/repro_py_c2e3_contraexemplo.txt
98b810ce2f33d70d74151f73bfae5ab6777e475b2bf92e7bfa8dc6e02b07192e  brutos/repro_py_cee4_M2.txt
beab197af4f75adf05517a2cde326995c4815d6142c7e49a8a366431212fbdd1  brutos/repro_py_cee4_casos_principais.txt
1a492c3ed30de88affdea1bfed6527e31177fd52c4c0341aff9132f8c24a8627  brutos/repro_py_cee4_contraexemplo.txt
0aa94e5063c7d2e6cbb9022cd8218052a044ffadff95d63268141217e25aaf68  brutos/repro_pyfrac_c04b_M2.txt
5f2489a0b84151b33ff6e96063a949441863c8012abcf234535ffe0503a885ef  brutos/repro_pyfrac_c04b_casos_principais.txt
c864fa359ed8bb4bd5c09d7eb194785a1c1c180517892656fc37116e052fa2bb  brutos/repro_pyfrac_c04b_contraexemplo.txt
05d1fb7731ed31308eb20e8634ab108e378c01db92670e9f31a8f9c29aa55013  brutos/repro_pyfrac_c2e3_M2.txt
d5908c120a8a2d20522071478538d5e12c8dd9637accb79a3fe793465ce9833e  brutos/repro_pyfrac_c2e3_casos_principais.txt
8eb0477320f7fa9f21bb8d48dece0f5f7167395d67037a731025c9edfe6974d9  brutos/repro_pyfrac_c2e3_contraexemplo.txt
dc8e8b4d565a9d2311b7b314ef96dd0b8b6a84a88bf02d5cb9455973b4b1efe9  brutos/repro_pyfrac_cee4_M2.txt
6822629d95d44cc707a637699da5d1837571aa5a2738f82461bc1dc32c5a36f7  brutos/repro_pyfrac_cee4_casos_principais.txt
de3ab33b19dfe0ac289ca99272bb7ddabdc09c6a7809257af91b6bbdd891083a  brutos/repro_pyfrac_cee4_contraexemplo.txt
9c63cc78ddd85b8852428399f74845771ec5697e701550a26ef0073e27f6f456  brutos/resumo_aleat.txt
2cd303367dd1eea2e442a94d6004e36f5b9555a79618a3f6d18d2473c91b1bb2  brutos/tabelas_geradas.md
f3011eee929102c36e6d9007682d0f1e0e60774159b50b4f71d3b6ccbb07c7f0  brutos/verif_adv_js_P0.txt
42424a51f4ec59ae08f83760040e051064359888ac1b26be78d0377e26b5f7f2  brutos/verif_adv_js_P1_2e18.txt
5d0a297cbad48cf88a46b59c533fb7c5370419616d9e67f70a9d7ccb99e1a8b1  brutos/verif_adv_js_P1_2e20.txt
5d0a297cbad48cf88a46b59c533fb7c5370419616d9e67f70a9d7ccb99e1a8b1  brutos/verif_adv_js_P1_2e22.txt
5d0a297cbad48cf88a46b59c533fb7c5370419616d9e67f70a9d7ccb99e1a8b1  brutos/verif_adv_js_P2.txt
9c479711cf38017a560b4d20c75a300ea6a71aa4897c2996ccf7abebdc6d08f2  brutos/verif_adv_js_P2u.txt
3ea0b8e20d0c55bbb2652a427b52dbd0668b6415ae80ceeced67cbac76105c74  brutos/verif_aleat_P0.jsonl
4c41d3b921379d290ce52a172387274a889b09b9bf3a24d21950bcc220adb1a0  brutos/verif_aleat_P1_2e18.jsonl
a66d1718a2ebc2e14c32d13007b6a33fc54cffa9d860b082ba6fb05dd707fbd3  brutos/verif_aleat_P1_2e20.jsonl
f04ac883618328545677934d227e56418c0df67021c1a4f0d81e3d8e99577bbf  brutos/verif_aleat_P1_2e22.jsonl
f04ac883618328545677934d227e56418c0df67021c1a4f0d81e3d8e99577bbf  brutos/verif_aleat_P2.jsonl
7e1524bfabea517ea10b0ef98da3a83dd8e800f3eb9261fb529ada910177c0d8  brutos/verif_aleat_P2u.jsonl
dd6bc466f483b9e3484c91b1d5fa07b548405ba46517b9575c068995a20dd0e4  brutos/verif_autoteste.txt
63ae11667f4b24878b420675c6dfd689f1082fac1e82b1285d41d1e361d1061e  brutos/verif_esperado_cliq_js.txt
e97b8c121cd8a11b004c523b329cfd3d1d854f956c5b131c8f10f8dcfc2cad44  brutos/verif_esperado_cliq_pyfrac.txt
9f883d6fca88821b11fa88dac766a62f3b0069e692a3ffad39f2017f97461733  brutos/verif_matching_contraex_c2e3.txt
e75334c560fdb97ae1ba3e050b60d969ded31a78f8bb19a05ebacea764243e46  brutos/verif_matching_esperado_cliq_pyfrac.txt
44222907ce8be81012f2a54dc37d2700c40e238262c51f10514ed1386333f993  brutos/verif_matching_repro_pyfrac_c2e3.txt
b5507972ae92afd9873891677fae334a451ed6b824631ce65434314a77a8aa0d  brutos/verif_prop_js_P0_casos_extras.txt
6ccdc9fa47ef46a45fd101a9a08e4d707e059d5d59ae480892d65529fadd4f00  brutos/verif_prop_js_P0_casos_principais.txt
1be5d3ffc4deee26ac9162ab733bf6f8d298747e332d72a9ac2f254e1f91763a  brutos/verif_prop_js_P0_contraexemplo.txt
b5507972ae92afd9873891677fae334a451ed6b824631ce65434314a77a8aa0d  brutos/verif_prop_js_P1_2e18_casos_extras.txt
63ae11667f4b24878b420675c6dfd689f1082fac1e82b1285d41d1e361d1061e  brutos/verif_prop_js_P1_2e18_casos_principais.txt
1be5d3ffc4deee26ac9162ab733bf6f8d298747e332d72a9ac2f254e1f91763a  brutos/verif_prop_js_P1_2e18_contraexemplo.txt
ef95f7f09f719386041b127064a9c329d5d3506d11e5821e2fb68ad47779e72b  brutos/verif_prop_js_P1_2e20_casos_extras.txt
63ae11667f4b24878b420675c6dfd689f1082fac1e82b1285d41d1e361d1061e  brutos/verif_prop_js_P1_2e20_casos_principais.txt
1be5d3ffc4deee26ac9162ab733bf6f8d298747e332d72a9ac2f254e1f91763a  brutos/verif_prop_js_P1_2e20_contraexemplo.txt
9dbdfbdfa0607c3bd73e7f71edef7602380f425fbe126313abe5b1379e56838a  brutos/verif_prop_js_P1_2e22_casos_extras.txt
63ae11667f4b24878b420675c6dfd689f1082fac1e82b1285d41d1e361d1061e  brutos/verif_prop_js_P1_2e22_casos_principais.txt
1be5d3ffc4deee26ac9162ab733bf6f8d298747e332d72a9ac2f254e1f91763a  brutos/verif_prop_js_P1_2e22_contraexemplo.txt
d3f32a6b1b69bd28986cbcea593148a9f44ce3e0884862b2cf0be1b7e85ab051  brutos/verif_prop_js_P2_casos_extras.txt
63ae11667f4b24878b420675c6dfd689f1082fac1e82b1285d41d1e361d1061e  brutos/verif_prop_js_P2_casos_principais.txt
1be5d3ffc4deee26ac9162ab733bf6f8d298747e332d72a9ac2f254e1f91763a  brutos/verif_prop_js_P2_contraexemplo.txt
d3f32a6b1b69bd28986cbcea593148a9f44ce3e0884862b2cf0be1b7e85ab051  brutos/verif_prop_js_P2u_casos_extras.txt
63ae11667f4b24878b420675c6dfd689f1082fac1e82b1285d41d1e361d1061e  brutos/verif_prop_js_P2u_casos_principais.txt
1be5d3ffc4deee26ac9162ab733bf6f8d298747e332d72a9ac2f254e1f91763a  brutos/verif_prop_js_P2u_contraexemplo.txt
04a59ee631b1cb780980a7b83e897d31da17efba88cfd4f8d1a0aca8f8f9e11d  brutos/verif_repro_js_c04b_M2.txt
12f5c819d3740c10cfdeb03d04765b3e5e3a5330f2af4deeed2c984b62e3278f  brutos/verif_repro_js_c04b_casos_principais.txt
1be5d3ffc4deee26ac9162ab733bf6f8d298747e332d72a9ac2f254e1f91763a  brutos/verif_repro_js_c04b_contraexemplo.txt
04a59ee631b1cb780980a7b83e897d31da17efba88cfd4f8d1a0aca8f8f9e11d  brutos/verif_repro_js_c2e3_M2.txt
6ccdc9fa47ef46a45fd101a9a08e4d707e059d5d59ae480892d65529fadd4f00  brutos/verif_repro_js_c2e3_casos_principais.txt
1be5d3ffc4deee26ac9162ab733bf6f8d298747e332d72a9ac2f254e1f91763a  brutos/verif_repro_js_c2e3_contraexemplo.txt
04a59ee631b1cb780980a7b83e897d31da17efba88cfd4f8d1a0aca8f8f9e11d  brutos/verif_repro_js_cee4_M2.txt
861e97e63c9caadd60d8f249d3388ad83d6c9c55cb9025b441ef08e539d0682e  brutos/verif_repro_js_cee4_casos_principais.txt
806d63d4006f5e6518d227ebd7fa57afc4e8db4f03a103cf58b074869b7f453a  brutos/verif_repro_js_cee4_contraexemplo.txt
04a59ee631b1cb780980a7b83e897d31da17efba88cfd4f8d1a0aca8f8f9e11d  brutos/verif_repro_py_c04b_M2.txt
12f5c819d3740c10cfdeb03d04765b3e5e3a5330f2af4deeed2c984b62e3278f  brutos/verif_repro_py_c04b_casos_principais.txt
1be5d3ffc4deee26ac9162ab733bf6f8d298747e332d72a9ac2f254e1f91763a  brutos/verif_repro_py_c04b_contraexemplo.txt
04a59ee631b1cb780980a7b83e897d31da17efba88cfd4f8d1a0aca8f8f9e11d  brutos/verif_repro_py_c2e3_M2.txt
6ccdc9fa47ef46a45fd101a9a08e4d707e059d5d59ae480892d65529fadd4f00  brutos/verif_repro_py_c2e3_casos_principais.txt
1be5d3ffc4deee26ac9162ab733bf6f8d298747e332d72a9ac2f254e1f91763a  brutos/verif_repro_py_c2e3_contraexemplo.txt
04a59ee631b1cb780980a7b83e897d31da17efba88cfd4f8d1a0aca8f8f9e11d  brutos/verif_repro_py_cee4_M2.txt
861e97e63c9caadd60d8f249d3388ad83d6c9c55cb9025b441ef08e539d0682e  brutos/verif_repro_py_cee4_casos_principais.txt
806d63d4006f5e6518d227ebd7fa57afc4e8db4f03a103cf58b074869b7f453a  brutos/verif_repro_py_cee4_contraexemplo.txt
04a59ee631b1cb780980a7b83e897d31da17efba88cfd4f8d1a0aca8f8f9e11d  brutos/verif_repro_pyfrac_c04b_M2.txt
45a621ce2d5513b14b6f8195dd6cd907ea402c62f0f0c2f20de84070867430bc  brutos/verif_repro_pyfrac_c04b_casos_principais.txt
1be5d3ffc4deee26ac9162ab733bf6f8d298747e332d72a9ac2f254e1f91763a  brutos/verif_repro_pyfrac_c04b_contraexemplo.txt
04a59ee631b1cb780980a7b83e897d31da17efba88cfd4f8d1a0aca8f8f9e11d  brutos/verif_repro_pyfrac_c2e3_M2.txt
e6ef8cf284fd7e379e08cfac30b406958321b5737a68df9ad0c14cc5499ef13f  brutos/verif_repro_pyfrac_c2e3_casos_principais.txt
1be5d3ffc4deee26ac9162ab733bf6f8d298747e332d72a9ac2f254e1f91763a  brutos/verif_repro_pyfrac_c2e3_contraexemplo.txt
04a59ee631b1cb780980a7b83e897d31da17efba88cfd4f8d1a0aca8f8f9e11d  brutos/verif_repro_pyfrac_cee4_M2.txt
cb03d3a003f9f83f641a3ce8de67d2c7ede2e10396af7af587c9114d86802730  brutos/verif_repro_pyfrac_cee4_casos_principais.txt
806d63d4006f5e6518d227ebd7fa57afc4e8db4f03a103cf58b074869b7f453a  brutos/verif_repro_pyfrac_cee4_contraexemplo.txt
```
