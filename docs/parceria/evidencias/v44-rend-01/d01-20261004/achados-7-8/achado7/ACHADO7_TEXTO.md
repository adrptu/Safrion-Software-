# Achado 7: texto exato (rev.json itens[7])

Fonte: `/tmp/claude-0/-home-user-Safrion-Software-/65558514-68d9-57f5-9da3-513cd6735cdc/scratchpad/d01rev/rev.json` (sha256 504355e946c290ec6378bffa7e4708e8beff154069265bbae1dba8ee42021ad7). Campos copiados sem edição; cada campo vai dentro de um bloco de texto para preservar quebras de linha.

## Achado

- lente: `regressao-desempenho`
- titulo: `Trator × implemento 5×6 e 6×5 (30 configurações, grafo perfeito) estouram o teto de 65 536 passos do teste de buraco e caem no conservador; o delta agrava o efeito com janelas variadas ou vazias`
- severidade: `S3`
- arquivo: `tools/prototipo/v37/gen37/safra.js`
- linha: `126`
- introduzido_pelo_delta: `False`

### achado.cenario_de_falha

```text
Entrada: 5 tratores × 6 plantadeiras (ativos t*, p*), rend 2, jan 10, partes fixas de 10/3 % cada, Q=600.
- Na antiga e na nova: buraco=null, então "combinações demais" e o conservador. Resultado: 20 ha atendidos e déficit de 290 h.
- Com teto maior no buraco (o grafo é reconhecido como perfeito): 84,80 ha e déficit de 50 h, em cerca de 77 ms.

Agravamento pelo delta, com T4+P5 sem janela (prestador):
- 04bf6f2: 40 ha e déficit de 280 h.
- Exato: 96,73 ha e déficit de 50 h.
- ee4f954: 111,33 ha, mas viola os cortes da linha e da coluna do prestador.

Caso "5×6 janelas variadas" (perf_casos.json #9): o déficit vai de 255 h (antiga) para 1 340 h (nova).
```

### achado.evidencia

```text
Na node dbg.js (busca instrumentada):
- 5x6 e 6x5 dão "buraco":null e conservador=true;
- 4x7, 5x5, 3x9, 3x10, 2x15, 6x4 e 7x4 dão "buraco":false.

rook.py e runjs (old,new,fixo3,teto) para "5x6 partes fixas, todas 10 h":
- old 20.00, new 20.00, teto 84.80 (déficit 50);
- "1 sem janela": new 40.00 (déficit 280) e teto 96.73 (déficit 50).

Variante com teto de 2^20 (b20) em 183 casos adversariais: 5×6 e 6×5 saem do conservador, com no máximo 332 ms.
```

### achado.correcao_proposta

```text
Subir o teto de passos do buraco (2^20 já tira 5×6 e 6×5 do conservador, com no máximo 332 ms nos 183 casos medidos) ou reconhecer trator × implemento (grafo de linhas de bipartido) como perfeito sem busca. O mesmo vale para dados2.py, linha 325.

Antes de fixar o teto, medir o pior caso do buraco. O gatilho já existia na ee4f954. O delta só agrava o efeito porque agora o fc corta por prazo todos os membros com janela, mesmo quando algum não tem janela.
```

## Veredito 0

- refutado: `False`
- reproduzido: `True`
- severidade: `S3`
- introduzido_pelo_delta: `False`

### vereditos[0].comando

```text
D=/tmp/claude-0/-home-user-Safrion-Software-/65558514-68d9-57f5-9da3-513cd6735cdc/scratchpad/prerev7/verif-regressao-desempenho-4-0

Cópias:
git -C /home/user/sp-d01 archive 04bf6f2 tools/prototipo/v37 | tar -x -C $D/new
git -C /home/user/sp-d01 archive ee4f954 tools/prototipo/v37 | tar -x -C $D/old

Scripts próprios:
- $D/run.js: extrai o bloco REPARTIR e roda com new Function. O 2º argumento troca só o teto do `ext` do buraco (65536 → N).
- $D/cortes.js: confere Σh ≤ t para cada ativo e cada prazo finito.
- $D/runpy.py: roda dados2.repartir.
- $D/casos.py: gera $D/casos.json (grafo de torre AxB, rend 2, jan 10, part 100/n %, Q=20·n; e 5x6 com T4P5 sem janela).
- $D/caso9.json: copiado de prerev7/regressao/perf_casos.json[9].

Comandos executados:
node run.js $D/{old,new} {-,1048576} < casos.json
node cortes.js $D/{old,new} {-,1048576} 2 < casos.json
node run.js / node cortes.js ... < caso9.json
python3 runpy.py $D/{old,new} casos.json|caso9.json
python3 runpy.py $D/newb20 ... (cópia de 04bf6f2 com dados2.py:325 trocado para >1048576)
```

### vereditos[0].saida

```text
5x6, partes fixas, todas 10 h:
- old e new: alocado 20, déficit 290, conservador (motivo "combinações demais...(conservador)"), cerca de 68 ms.
- Teto 2^20 em old e new: 84,8 ha, déficit 50, sem conservador, 81 ms.

6x5:
- old e new: 20 ha, déficit 290, conservador.
- Teto 2^20: 100 ha, déficit 50.

Fora do conservador com o teto atual: 4x7, 5x5, 3x9, 3x10, 2x15, 6x4, 7x4 e 4x6.

Também caem no conservador com o teto atual, nas duas versões:
- 6x6: 20 ha. Com 2^20: 103,87 ha, 529 ms em JS.
- 5x7: 20 ha. Com 2^20: 84,83 ha, 265 ms em JS.

5x6 com T4P5 sem janela:
- old: 111,3333 ha, déficit 50. VIOLA os cortes "p5@10: 15,303 h; t4@10: 12,000 h" (classe D-01).
- new: 40 ha, déficit 280, sem violação.
- new com teto 2^20: 96,7273 ha, déficit 50, sem violação.

Caso 9 (5x6, janelas variadas, sem % fixo):
- old: 3000 ha, déficit 255. Viola 20 cortes, por exemplo "t1@2: 4,000 h" e "p2@3: 5,000 h".
- new: 3000 ha, déficit 1340, conservador, sem violação.
- new com teto 2^20: 3000 ha, déficit 255, sem violação.

Python: valores idênticos ao JS nos quatro casos (old e new).
- Com o teto atual: cerca de 0,9–1,0 s por caso, porque já gasta o teto.
- Com 2^20: 1,1–1,25 s nos casos 5x6 e 6x5; 5x7 leva 4,0 s e 6x6 leva 8,9 s.
```

### vereditos[0].fundamento

```text
Reproduzi o achado e não o refuto. A severidade S3 se sustenta, e o defeito não foi introduzido pelo delta.

1) O gatilho é o teto de 65 536 passos do `buraco`. Ele está em safra.js:126 e no espelho dados2.py:325. Prova: subir só esse teto, sem mexer no teto do Bron–Kerbosch nem no de cliques, tira 5x6 e 6x5 do conservador. O grafo de torre é então reconhecido como perfeito, e o resultado fica em 84,8 e 100 ha, contra 20 ha.

Na ee4f954 o resultado é idêntico (20 ha, déficit 290), então o problema é anterior ao delta. É resíduo do W1: o comentário afirma que trator × implemento é perfeito e que as cliques bastam, mas isso só vale até cerca de 29 configurações.

O caso não está na lista "fora do escopo", que fala de trios com 24+ configurações e teto de cliques. Aqui são pares e quem estoura é o teto de buraco. A DECISÃO do Codex trata do teto de 8 192 cortes, não deste.

2) Classifico como S3, não S2. A estimativa é conservadora e tem motivo explícito ("combinações demais ... (conservador)"). Ela subestima a capacidade, mas nunca aceita plano inviável: cortes.js mostra zero violações na 04bf6f2. O arranjo também não é comum: são 30 configurações cobrindo todos os pares de uma ocorrência. Existe alternativa segura, que é declarar menos configurações.

3) O "agravamento pelo delta" não é defeito do delta. Ele é o comportamento decidido em 5983640246: nos componentes no conservador, os membros com janela ≤ t cabem em t, e um membro sem janela não amplia a disponibilidade dos outros.
- Os 111,33 ha da ee4f954 violavam t4@10 (12 h) e p5@10 (15,3 h), o mesmo defeito do D-01.
- No caso 9, o déficit de 255 h da ee4f954 vinha acompanhado de 20 cortes violados.
- O déficit de 1 340 h da 04bf6f2 é a inflação conservadora do teto antigo, agora aplicada de forma coerente.

Esse sub-item não deve ser tratado como regressão do delta. É custo do gatilho anterior.

4) Ressalva de desempenho sobre a correção proposta, medida no espelho Python: subir o teto para 2^20 custa 8,9 s em 6x6 e 4,0 s em 5x7. Antes de subir o teto, convém preferir o reconhecimento estrutural (configurações com no máximo dois ativos, em que cada aresta vem de um ativo comum: grafo de linhas de bipartido, portanto perfeito) ou medir o pior caso em Python.

A correção não deve ser bloqueante para a D-01: é S3, anterior ao delta e conservadora.
```

## Veredito 1

- refutado: `False`
- reproduzido: `True`
- severidade: `S3`
- introduzido_pelo_delta: `False`

### vereditos[1].comando

```text
D=/tmp/claude-0/-home-user-Safrion-Software-/65558514-68d9-57f5-9da3-513cd6735cdc/scratchpad/prerev7/verif-regressao-desempenho-4-1
git -C /home/user/sp-d01 archive 04bf6f2 tools/prototipo/v37 | tar -x -C $D/new
git -C /home/user/sp-d01 archive ee4f954 tools/prototipo/v37 | tar -x -C $D/old
node $D/h/run.js $D      # old, new e new com teto do buraco 2^22, grades trator x implemento
node $D/h/dbg.js $D      # buraco instrumentado: resultado e passos por grade
python3 $D/h/py.py $D    # espelho dados2.repartir, old e new
node $D/h/c9.js $D       # perf_casos.json #9 e T4+P5 sem janela, com verificador dos cortes por prazo em linhas e colunas
node $D/h/steps.js $D    # passos necessários sem teto
node $D/h/worst.js $D; python3 $D/h/pyteto.py $D   # custo da correção proposta (teto 2^20) em JS e Python
(Os scripts estão em $D/h/. Carregam o bloco REPARTIR por regex e new Function. O teto só foi alterado em cópias.)
```

### vereditos[1].saida

```text
Executado.

5x6, partes fixas, todas com janela de 10 h (Q=600, 2 ha/h):
- ee4f954: 20,00 ha, déficit 290 h, conservador.
- 04bf6f2: 20,00 ha, déficit 290 h, conservador.
- 04bf6f2 com teto maior: 84,80 ha, déficit 50 h, exato.
- 6x5 dá o mesmo quadro: 20 ha nas duas versões e 100,00 ha com teto maior.
- Espelho Python: old e new dão 20,00 ha e déficit 290 h (cerca de 850 ms).

buraco instrumentado (passos até o teto ou até a resposta):
- 5x6, 6x5, 6x6 e 7x5: null, 65537 passos.
- false: 5x5 (20325), 4x7 (23758), 3x9, 3x10, 2x15, 6x4, 7x4 (29680) e 4x8 (50200).

T4+P5 sem janela, mais o verificador dos cortes por prazo em linhas e colunas:
- old: 111,33 ha, déficit 50 h, com 2 violações (t4@10: 12,00 h > 10 h; p5@10: 15,30 h > 10 h).
- new: 40,00 ha, déficit 280 h, 0 violações.
- teto maior: 96,73 ha, déficit 50 h, 0 violações.

perf_casos #9 (5x6 com janelas variadas, Q=3000):
- old: 3000 ha, déficit 255 h, 20 violações (t0@10: 17,13 h > 10 h; p1@10: 29,29 h > 10 h).
- new: 3000 ha, déficit 1340 h, 0 violações.
- teto maior: 3000 ha, déficit 255 h, 0 violações.

Passos necessários sem teto:
- 5x6: 82.815
- 6x5: 92.465
- 7x5: 328.370
- 6x6: 584.391
- 8x5: 953.380
- 7x6: 3.181.578
- 7x7: 23.886.121 (29,7 s em JS)

Correção proposta, com teto 2^20:
- JS: 6x6 em 581 ms (exato). 7x6 e 7x7 levam cerca de 1,25 s e 1,31 s e continuam no conservador.
- Python: 5x6 em 1068 ms, 6x5 em 1170 ms e 6x6 em 9069 ms.
```

### vereditos[1].fundamento

```text
Não refutado. O achado se reproduz no JS de 04bf6f2 e de ee4f954 e no espelho dados2.py, com os mesmos números do achado:
- 5x6: 20 ha contra 84,80 ha exatos;
- 6x5: 20 ha contra 100 ha exatos;
- 1 sem janela: 40 ha contra 96,73 ha exatos.

**Causa confirmada.** O teste de buraco ímpar estoura o teto de 65.536 passos.
- Linha: safra.js, linha 126 (ext); dados2.py, linha 325.
- Onde estoura: grafo de torres com 30 vértices ou mais, com 5 ou mais em cada lado. 5x6 precisa de 82.815 passos.
- Efeito: h=null, então est=true e o componente vai para o fc conservador.
- Contraste: com até 28 configurações (5x5, 4x7, 7x4) o resultado é exato.

**Por que não está fora do escopo.**
- A exclusão cobre "trios com 24+" (MANIFESTO, linha 68). Ali o limite é o teto de cliques, porque o grafo de trios tem 3^10 cliques maximais.
- Aqui o grafo de torres tem só 11 cliques. O limite é a busca de buraco, que cresce exponencialmente.
- O próprio código (comentário em grafo) e o MANIFESTO (W1, corrigido em 6afb511) afirmam que trator × implemento é perfeito e fica só com as cliques. A revisão da rodada 5 dizia que isso era "viável para n ≤ 30". Em n=30 isso não vale.
- É, portanto, um resíduo do W1, não a política (a), (b), (c) nem o caso de trios.

**Severidade S3, não S2.**
- O resultado é viável: o verificador encontra 0 violações dos cortes por prazo em linhas e colunas.
- O motivo "(conservador)" fica explícito.
- O erro vai para o lado seguro: subestima a capacidade e superestima o déficit, sem aceitar plano inviável.
- 30 combinações completas numa mesma ocorrência não é arranjo comum. O caso realista medido antes tinha de 8 a 12 configurações, e até 28 configurações a grade é exata.
- O W1, mesmo sintoma, já foi classificado S3.

**Não introduzido pelo delta.** O caso base dá resultado idêntico em ee4f954: 20 ha e 290 h.

**A parte do "agravamento pelo delta" está refutada como defeito.**
- Os valores de ee4f954 não servem de base: violam os cortes. No caso T4+P5, a antiga aceita t4@10 com 12 h e p5@10 com 15,30 h. No caso #9, aceita 20 violações.
- O fc mais restritivo, em que o membro sem janela não amplia os demais, é exatamente a DECISÃO 5983640246 para componentes conservadores.
- Corrigir o teto resolve as duas coisas de uma vez, porque o caso deixa de ir para o conservador.

**Crítica à correção proposta.**
- Teto 2^20 só adia o problema. 7x6 precisa de 3,18 milhões de passos e continua conservador, e o JS passa a levar cerca de 1,25 s.
- No Python, 5x6 passa de 1 s (1068 ms) e 6x6 leva 9,07 s, acima do limite de 1 s cobrado em Q5 e V6.
- Prefiro reconhecer a estrutura sem busca. Quando toda exclusão vem de ativos e os ativos se dividem em duas classes, com no máximo um ativo de cada classe por configuração, o grafo é de linhas de um bipartido e é perfeito por König. Nesse caso o buraco é dispensado no grafo e no complemento.
- Manter o teto atual para os demais casos.
- Incluir 5x6 e 6x5 no oráculo, em JS e Python, com 84,80 ha e 100 ha.
- Incluir o caso T4+P5 sem janela, com 96,73 ha e 0 violações.
```

## JSON bruto de itens[7]

```json
{
 "lente": "regressao-desempenho",
 "achado": {
  "titulo": "Trator × implemento 5×6 e 6×5 (30 configurações, grafo perfeito) estouram o teto de 65 536 passos do teste de buraco e caem no conservador; o delta agrava o efeito com janelas variadas ou vazias",
  "severidade": "S3",
  "arquivo": "tools/prototipo/v37/gen37/safra.js",
  "linha": 126,
  "cenario_de_falha": "Entrada: 5 tratores × 6 plantadeiras (ativos t*, p*), rend 2, jan 10, partes fixas de 10/3 % cada, Q=600.\n- Na antiga e na nova: buraco=null, então \"combinações demais\" e o conservador. Resultado: 20 ha atendidos e déficit de 290 h.\n- Com teto maior no buraco (o grafo é reconhecido como perfeito): 84,80 ha e déficit de 50 h, em cerca de 77 ms.\n\nAgravamento pelo delta, com T4+P5 sem janela (prestador):\n- 04bf6f2: 40 ha e déficit de 280 h.\n- Exato: 96,73 ha e déficit de 50 h.\n- ee4f954: 111,33 ha, mas viola os cortes da linha e da coluna do prestador.\n\nCaso \"5×6 janelas variadas\" (perf_casos.json #9): o déficit vai de 255 h (antiga) para 1 340 h (nova).",
  "evidencia": "Na node dbg.js (busca instrumentada):\n- 5x6 e 6x5 dão \"buraco\":null e conservador=true;\n- 4x7, 5x5, 3x9, 3x10, 2x15, 6x4 e 7x4 dão \"buraco\":false.\n\nrook.py e runjs (old,new,fixo3,teto) para \"5x6 partes fixas, todas 10 h\":\n- old 20.00, new 20.00, teto 84.80 (déficit 50);\n- \"1 sem janela\": new 40.00 (déficit 280) e teto 96.73 (déficit 50).\n\nVariante com teto de 2^20 (b20) em 183 casos adversariais: 5×6 e 6×5 saem do conservador, com no máximo 332 ms.",
  "introduzido_pelo_delta": false,
  "correcao_proposta": "Subir o teto de passos do buraco (2^20 já tira 5×6 e 6×5 do conservador, com no máximo 332 ms nos 183 casos medidos) ou reconhecer trator × implemento (grafo de linhas de bipartido) como perfeito sem busca. O mesmo vale para dados2.py, linha 325.\n\nAntes de fixar o teto, medir o pior caso do buraco. O gatilho já existia na ee4f954. O delta só agrava o efeito porque agora o fc corta por prazo todos os membros com janela, mesmo quando algum não tem janela."
 },
 "vereditos": [
  {
   "refutado": false,
   "reproduzido": true,
   "severidade": "S3",
   "introduzido_pelo_delta": false,
   "comando": "D=/tmp/claude-0/-home-user-Safrion-Software-/65558514-68d9-57f5-9da3-513cd6735cdc/scratchpad/prerev7/verif-regressao-desempenho-4-0\n\nCópias:\ngit -C /home/user/sp-d01 archive 04bf6f2 tools/prototipo/v37 | tar -x -C $D/new\ngit -C /home/user/sp-d01 archive ee4f954 tools/prototipo/v37 | tar -x -C $D/old\n\nScripts próprios:\n- $D/run.js: extrai o bloco REPARTIR e roda com new Function. O 2º argumento troca só o teto do `ext` do buraco (65536 → N).\n- $D/cortes.js: confere Σh ≤ t para cada ativo e cada prazo finito.\n- $D/runpy.py: roda dados2.repartir.\n- $D/casos.py: gera $D/casos.json (grafo de torre AxB, rend 2, jan 10, part 100/n %, Q=20·n; e 5x6 com T4P5 sem janela).\n- $D/caso9.json: copiado de prerev7/regressao/perf_casos.json[9].\n\nComandos executados:\nnode run.js $D/{old,new} {-,1048576} < casos.json\nnode cortes.js $D/{old,new} {-,1048576} 2 < casos.json\nnode run.js / node cortes.js ... < caso9.json\npython3 runpy.py $D/{old,new} casos.json|caso9.json\npython3 runpy.py $D/newb20 ... (cópia de 04bf6f2 com dados2.py:325 trocado para >1048576)",
   "saida": "5x6, partes fixas, todas 10 h:\n- old e new: alocado 20, déficit 290, conservador (motivo \"combinações demais...(conservador)\"), cerca de 68 ms.\n- Teto 2^20 em old e new: 84,8 ha, déficit 50, sem conservador, 81 ms.\n\n6x5:\n- old e new: 20 ha, déficit 290, conservador.\n- Teto 2^20: 100 ha, déficit 50.\n\nFora do conservador com o teto atual: 4x7, 5x5, 3x9, 3x10, 2x15, 6x4, 7x4 e 4x6.\n\nTambém caem no conservador com o teto atual, nas duas versões:\n- 6x6: 20 ha. Com 2^20: 103,87 ha, 529 ms em JS.\n- 5x7: 20 ha. Com 2^20: 84,83 ha, 265 ms em JS.\n\n5x6 com T4P5 sem janela:\n- old: 111,3333 ha, déficit 50. VIOLA os cortes \"p5@10: 15,303 h; t4@10: 12,000 h\" (classe D-01).\n- new: 40 ha, déficit 280, sem violação.\n- new com teto 2^20: 96,7273 ha, déficit 50, sem violação.\n\nCaso 9 (5x6, janelas variadas, sem % fixo):\n- old: 3000 ha, déficit 255. Viola 20 cortes, por exemplo \"t1@2: 4,000 h\" e \"p2@3: 5,000 h\".\n- new: 3000 ha, déficit 1340, conservador, sem violação.\n- new com teto 2^20: 3000 ha, déficit 255, sem violação.\n\nPython: valores idênticos ao JS nos quatro casos (old e new).\n- Com o teto atual: cerca de 0,9–1,0 s por caso, porque já gasta o teto.\n- Com 2^20: 1,1–1,25 s nos casos 5x6 e 6x5; 5x7 leva 4,0 s e 6x6 leva 8,9 s.",
   "fundamento": "Reproduzi o achado e não o refuto. A severidade S3 se sustenta, e o defeito não foi introduzido pelo delta.\n\n1) O gatilho é o teto de 65 536 passos do `buraco`. Ele está em safra.js:126 e no espelho dados2.py:325. Prova: subir só esse teto, sem mexer no teto do Bron–Kerbosch nem no de cliques, tira 5x6 e 6x5 do conservador. O grafo de torre é então reconhecido como perfeito, e o resultado fica em 84,8 e 100 ha, contra 20 ha.\n\nNa ee4f954 o resultado é idêntico (20 ha, déficit 290), então o problema é anterior ao delta. É resíduo do W1: o comentário afirma que trator × implemento é perfeito e que as cliques bastam, mas isso só vale até cerca de 29 configurações.\n\nO caso não está na lista \"fora do escopo\", que fala de trios com 24+ configurações e teto de cliques. Aqui são pares e quem estoura é o teto de buraco. A DECISÃO do Codex trata do teto de 8 192 cortes, não deste.\n\n2) Classifico como S3, não S2. A estimativa é conservadora e tem motivo explícito (\"combinações demais ... (conservador)\"). Ela subestima a capacidade, mas nunca aceita plano inviável: cortes.js mostra zero violações na 04bf6f2. O arranjo também não é comum: são 30 configurações cobrindo todos os pares de uma ocorrência. Existe alternativa segura, que é declarar menos configurações.\n\n3) O \"agravamento pelo delta\" não é defeito do delta. Ele é o comportamento decidido em 5983640246: nos componentes no conservador, os membros com janela ≤ t cabem em t, e um membro sem janela não amplia a disponibilidade dos outros.\n- Os 111,33 ha da ee4f954 violavam t4@10 (12 h) e p5@10 (15,3 h), o mesmo defeito do D-01.\n- No caso 9, o déficit de 255 h da ee4f954 vinha acompanhado de 20 cortes violados.\n- O déficit de 1 340 h da 04bf6f2 é a inflação conservadora do teto antigo, agora aplicada de forma coerente.\n\nEsse sub-item não deve ser tratado como regressão do delta. É custo do gatilho anterior.\n\n4) Ressalva de desempenho sobre a correção proposta, medida no espelho Python: subir o teto para 2^20 custa 8,9 s em 6x6 e 4,0 s em 5x7. Antes de subir o teto, convém preferir o reconhecimento estrutural (configurações com no máximo dois ativos, em que cada aresta vem de um ativo comum: grafo de linhas de bipartido, portanto perfeito) ou medir o pior caso em Python.\n\nA correção não deve ser bloqueante para a D-01: é S3, anterior ao delta e conservadora."
  },
  {
   "refutado": false,
   "reproduzido": true,
   "severidade": "S3",
   "introduzido_pelo_delta": false,
   "comando": "D=/tmp/claude-0/-home-user-Safrion-Software-/65558514-68d9-57f5-9da3-513cd6735cdc/scratchpad/prerev7/verif-regressao-desempenho-4-1\ngit -C /home/user/sp-d01 archive 04bf6f2 tools/prototipo/v37 | tar -x -C $D/new\ngit -C /home/user/sp-d01 archive ee4f954 tools/prototipo/v37 | tar -x -C $D/old\nnode $D/h/run.js $D      # old, new e new com teto do buraco 2^22, grades trator x implemento\nnode $D/h/dbg.js $D      # buraco instrumentado: resultado e passos por grade\npython3 $D/h/py.py $D    # espelho dados2.repartir, old e new\nnode $D/h/c9.js $D       # perf_casos.json #9 e T4+P5 sem janela, com verificador dos cortes por prazo em linhas e colunas\nnode $D/h/steps.js $D    # passos necessários sem teto\nnode $D/h/worst.js $D; python3 $D/h/pyteto.py $D   # custo da correção proposta (teto 2^20) em JS e Python\n(Os scripts estão em $D/h/. Carregam o bloco REPARTIR por regex e new Function. O teto só foi alterado em cópias.)",
   "saida": "Executado.\n\n5x6, partes fixas, todas com janela de 10 h (Q=600, 2 ha/h):\n- ee4f954: 20,00 ha, déficit 290 h, conservador.\n- 04bf6f2: 20,00 ha, déficit 290 h, conservador.\n- 04bf6f2 com teto maior: 84,80 ha, déficit 50 h, exato.\n- 6x5 dá o mesmo quadro: 20 ha nas duas versões e 100,00 ha com teto maior.\n- Espelho Python: old e new dão 20,00 ha e déficit 290 h (cerca de 850 ms).\n\nburaco instrumentado (passos até o teto ou até a resposta):\n- 5x6, 6x5, 6x6 e 7x5: null, 65537 passos.\n- false: 5x5 (20325), 4x7 (23758), 3x9, 3x10, 2x15, 6x4, 7x4 (29680) e 4x8 (50200).\n\nT4+P5 sem janela, mais o verificador dos cortes por prazo em linhas e colunas:\n- old: 111,33 ha, déficit 50 h, com 2 violações (t4@10: 12,00 h > 10 h; p5@10: 15,30 h > 10 h).\n- new: 40,00 ha, déficit 280 h, 0 violações.\n- teto maior: 96,73 ha, déficit 50 h, 0 violações.\n\nperf_casos #9 (5x6 com janelas variadas, Q=3000):\n- old: 3000 ha, déficit 255 h, 20 violações (t0@10: 17,13 h > 10 h; p1@10: 29,29 h > 10 h).\n- new: 3000 ha, déficit 1340 h, 0 violações.\n- teto maior: 3000 ha, déficit 255 h, 0 violações.\n\nPassos necessários sem teto:\n- 5x6: 82.815\n- 6x5: 92.465\n- 7x5: 328.370\n- 6x6: 584.391\n- 8x5: 953.380\n- 7x6: 3.181.578\n- 7x7: 23.886.121 (29,7 s em JS)\n\nCorreção proposta, com teto 2^20:\n- JS: 6x6 em 581 ms (exato). 7x6 e 7x7 levam cerca de 1,25 s e 1,31 s e continuam no conservador.\n- Python: 5x6 em 1068 ms, 6x5 em 1170 ms e 6x6 em 9069 ms.",
   "fundamento": "Não refutado. O achado se reproduz no JS de 04bf6f2 e de ee4f954 e no espelho dados2.py, com os mesmos números do achado:\n- 5x6: 20 ha contra 84,80 ha exatos;\n- 6x5: 20 ha contra 100 ha exatos;\n- 1 sem janela: 40 ha contra 96,73 ha exatos.\n\n**Causa confirmada.** O teste de buraco ímpar estoura o teto de 65.536 passos.\n- Linha: safra.js, linha 126 (ext); dados2.py, linha 325.\n- Onde estoura: grafo de torres com 30 vértices ou mais, com 5 ou mais em cada lado. 5x6 precisa de 82.815 passos.\n- Efeito: h=null, então est=true e o componente vai para o fc conservador.\n- Contraste: com até 28 configurações (5x5, 4x7, 7x4) o resultado é exato.\n\n**Por que não está fora do escopo.**\n- A exclusão cobre \"trios com 24+\" (MANIFESTO, linha 68). Ali o limite é o teto de cliques, porque o grafo de trios tem 3^10 cliques maximais.\n- Aqui o grafo de torres tem só 11 cliques. O limite é a busca de buraco, que cresce exponencialmente.\n- O próprio código (comentário em grafo) e o MANIFESTO (W1, corrigido em 6afb511) afirmam que trator × implemento é perfeito e fica só com as cliques. A revisão da rodada 5 dizia que isso era \"viável para n ≤ 30\". Em n=30 isso não vale.\n- É, portanto, um resíduo do W1, não a política (a), (b), (c) nem o caso de trios.\n\n**Severidade S3, não S2.**\n- O resultado é viável: o verificador encontra 0 violações dos cortes por prazo em linhas e colunas.\n- O motivo \"(conservador)\" fica explícito.\n- O erro vai para o lado seguro: subestima a capacidade e superestima o déficit, sem aceitar plano inviável.\n- 30 combinações completas numa mesma ocorrência não é arranjo comum. O caso realista medido antes tinha de 8 a 12 configurações, e até 28 configurações a grade é exata.\n- O W1, mesmo sintoma, já foi classificado S3.\n\n**Não introduzido pelo delta.** O caso base dá resultado idêntico em ee4f954: 20 ha e 290 h.\n\n**A parte do \"agravamento pelo delta\" está refutada como defeito.**\n- Os valores de ee4f954 não servem de base: violam os cortes. No caso T4+P5, a antiga aceita t4@10 com 12 h e p5@10 com 15,30 h. No caso #9, aceita 20 violações.\n- O fc mais restritivo, em que o membro sem janela não amplia os demais, é exatamente a DECISÃO 5983640246 para componentes conservadores.\n- Corrigir o teto resolve as duas coisas de uma vez, porque o caso deixa de ir para o conservador.\n\n**Crítica à correção proposta.**\n- Teto 2^20 só adia o problema. 7x6 precisa de 3,18 milhões de passos e continua conservador, e o JS passa a levar cerca de 1,25 s.\n- No Python, 5x6 passa de 1 s (1068 ms) e 6x6 leva 9,07 s, acima do limite de 1 s cobrado em Q5 e V6.\n- Prefiro reconhecer a estrutura sem busca. Quando toda exclusão vem de ativos e os ativos se dividem em duas classes, com no máximo um ativo de cada classe por configuração, o grafo é de linhas de um bipartido e é perfeito por König. Nesse caso o buraco é dispensado no grafo e no complemento.\n- Manter o teto atual para os demais casos.\n- Incluir 5x6 e 6x5 no oráculo, em JS e Python, com 84,80 ha e 100 ha.\n- Incluir o caso T4+P5 sem janela, com 96,73 ha e 0 violações."
  }
 ]
}
```
