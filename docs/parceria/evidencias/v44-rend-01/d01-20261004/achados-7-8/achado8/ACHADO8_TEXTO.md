# Achado 8 — texto exato (rev.json, itens[8])

Fonte: `/tmp/claude-0/-home-user-Safrion-Software-/65558514-68d9-57f5-9da3-513cd6735cdc/scratchpad/d01rev/rev.json` (sha256 `504355e946c290ec6378bffa7e4708e8beff154069265bbae1dba8ee42021ad7`), chave `itens[8]`. Cada campo abaixo é o valor JSON impresso sem edição (bloco de texto). Revisão feita sobre 04bf6f2.

- lente: `restricao-falsa`

## Achado

### titulo

```text
Partes fixas: a restrição antiga de janela máxima (sq/at:/pl:) reduz antes do corte por prazo mais apertado, e a folga liberada não volta (atendido subestimado e motivo falso)
```

### severidade

```text
S3
```

### arquivo

```text
tools/prototipo/v37/gen37/safra.js
```

### linha

```text
169
```

### cenario_de_falha

```text
Entrada F5: Q=1000; pools={}; cfgs:
- A {rend 3, jan 100, part 60, ativos [a01]};
- B {rend 1, jan 20, part 20, ativos [a01]};
- C {rend 1, jan 20, part 20, ativos [a01]}.

O que 04bf6f2 devolve:
- alocado 234,29 ha (A 214,29 ha / 71,43 h; B 10 ha; C 10 ha), saldo 765,71, conflito true, decorrido 91,43 h;
- motivo 'as partes fixas em sequência não cabem na janela de 100 h: fazem de 50 % a 71,43 %', com 8,57 h da janela de 100 h ociosas e A abaixo da própria parte (600 ha) e da própria janela.

Agenda viável com as mesmas partes como teto: B 0–10 h, C 10–20 h, A 20–100 h (80 h = 240 ha). Total 260 ha; todos os prazos são cumpridos.

Mais casos:
- F1/F4 (A 100 h + cinco B de 10 h, mesmo trator ou sequência): 76,67 ha contra 100 viáveis (−23 %; agenda: os B fazem 2 h cada em 0–10, A faz 10–100).
- F1b, o mesmo mais D (1 %, sem janela, que trabalha depois): A sobe de 66,67 para 90,91 ha. O resultado depende de uma configuração que não altera a agenda de A e dos B.

Como acontece: Object.keys(jan) processa primeiro a restrição antiga 'sq'/'at:a01' (máximo de 100 h, igual ao corte de 100). Ela corta A, B e C pela mesma fração; depois o corte de 20 h corta B e C de novo, e as horas liberadas não voltam para A.

O antigo ee4f954 dava 242,86 ha, mas com B+C = 28,57 h em 20 h, o que é inviável (D-01).
```

### evidencia

```text
`node run6.js c4.json` (brutos/c4-js-novo-antigo-fixR.txt):
- NOVO 04bf6f2: alocado 234.2857; q A=214.2857ha/71.4286h, B=10ha/10h, C=10ha/10h; conflito true.
- ANTIGO ee4f954: 242.8571; B=C=14.2857h.
- CORRIGIDO(rascunho fixR): alocado 260; A=240ha/80h.

`python3 run.py c4.json`: NOVO py com o mesmo resultado (alocado 234.2857).

`node run.js c2.json`, F1b: NOVO A=90.9091 contra F1 (c1.json): A=66.6667.

`node ganho.js 1 20000 seq` → {novo:1270, novo5:998, novoMax:0.462, antigo:0}.
`node ganho.js 2 20000 semtroca` → {novo:1057, novo5:607, novoMax:0.272, antigo:0}.
`node ganho2.js 2 20000` → agenda_inviavel_no_rascunho: 0.

Em todos esses casos o novo já mostra conflito = true.
```

### introduzido_pelo_delta

```text
True
```

### correcao_proposta

```text
Correção mínima: depois do laço de redução das partes fixas, um passo de devolução de folga em JS e Python. Para cada x fixa com q < cab, subir q em r × min((cab−q)/r, min sobre pl(x) de (jan[g] − uso_fixo[g])) e descontar do saldo.

No scratch (fixR):
- F1/F3/F4/F5 → 100/100/100/260 ha, com agenda viável;
- nunca atende menos em 40 000 entradas;
- oráculo 90/91: só o M2 muda (q de B 2 → 7/3). O M2 fixa, desde a rodada 2, 0,33 h ociosas na janela de 4 h, então a mudança pede decisão do Codex sobre o M2.

Alternativas de ordem (processar os cortes por prazo crescente, ou não registrar em jan a restrição antiga igual a um corte) corrigem F1, F3 e F4, mas não são uniformes: 159 piores e 191 melhores em 20 000.

Se o Codex mantiver a redução sequencial, o motivo não deve dizer que 'não cabem na janela de X h' quando sobram horas nela.
```

## Veredito 0 (verif-restricao-falsa-0-0)

### refutado

```text
True
```

### reproduzido

```text
True
```

### severidade

```text
nenhuma
```

### introduzido_pelo_delta

```text
False
```

### comando

```text
Diretório: /tmp/claude-0/-home-user-Safrion-Software-/65558514-68d9-57f5-9da3-513cd6735cdc/scratchpad/prerev7/verif-restricao-falsa-0-0, com cópias novo/ (04bf6f2) e antigo/ (ee4f954) obtidas por git archive.
(1) `node run.js c.json`: F5 e F5 com sequência declarada.
(2) `node run.js c1.json`: F1 e F1b.
(3) `python3 py.py <novo|antigo> c.json|c1.json`: espelho dados2.repartir.
(4) `node run.js m2.json`: caso M2 do oráculo.
(5) `node run.js c5pre.json`: o mesmo arranjo físico de F5 e F1, escrito com restrições explícitas que o código antigo já tinha (sequência declarada mais um ativo comum de B e C, ou dos B).
(6) `node rnd.js 1|2|3`: 3 × 20 000 entradas aleatórias, só com o código novo; conta as reduções de parte fixa com conflito=false.
(7) `python3 rend_multiconjuntos_unit.py` na cópia novo/.
```

### saida

```text
(1) F5:
- NOVO 04bf6f2: alocado 234,2857; saldo 765,7143; conflito true; déficit 500; decorrido 91,4286; A 214,2857 ha / 71,4286 h; B e C 10 ha / 10 h cada.
- Motivo: "as partes fixas em sequência não cabem na janela de 100 h: fazem de 50 % a 71,43 % do que cabia na própria janela".
- ANTIGO ee4f954: alocado 242,8571; B e C 14,2857 h cada, ou seja, 28,57 h numa janela de 20 h.

(2) F1:
- NOVO: alocado 76,6667 (A 66,6667; cada B 2); conflito true; déficit 100.
- ANTIGO: 100, com os B somando 33,3 h numa janela de 10 h.
- F1b (com D de 1 %, sem janela; minha variante): NOVO A 90,9091; B 1,8182 cada.

(3) Python igual ao JS nos dois commits: F5 234,2857 / 242,8571; F1 76,6667 / 100.

(4) M2:
- NOVO e ANTIGO: q = 1,6667 / 2 / 8,3333. A+B usam 3,67 h da janela de 4 h, sobram 0,33 h ociosas.
- Motivo: "janela de 4 h: fazem de 41,67 % a 50 %". É o valor fixado no oráculo desde a rodada 2.

(5) Arranjo físico explícito:
- F5pre: ANTIGO ee4f954 = 234,2857 (A 214,2857; B e C 10), igual ao NOVO, com as mesmas 8,57 h ociosas.
- F1pre: ANTIGO = 76,6667 (A 66,6667; cada B 2), igual ao NOVO.

(6) Busca aleatória: {n:20000, red:3578, redSemConf:0}, {n:20000, red:3578, redSemConf:0}, {n:20000, red:3572, redSemConf:0}. As sementes 1 e 2 deram números idênticos, então o gerador provavelmente repetiu a sequência: são cerca de 40 000 entradas distintas, não 60 000.

(7) Oráculo: RESULTADO 91/91 OK, M2 incluído.
```

### fundamento

```text
Os números do achado foram reproduzidos exatamente, em JS e em Python, nos dois commits. Mesmo assim, o achado é refutado como defeito da candidata 04bf6f2, por quatro motivos.

**1. O delta não introduziu o mecanismo.**
- A falha descrita é a redução sequencial das partes fixas, uma restrição por vez, sem devolver a folga.
- Com o mesmo arranjo físico escrito por restrições que o ee4f954 já tratava (sequência mais o ativo comum de B e C), o código antigo já devolve exatamente 234,2857 ha em F5 e 76,6667 ha em F1, com as mesmas horas ociosas (comando 5).
- O oráculo fixa esse comportamento desde a rodada 2 no caso M2, que passa nos dois commits. Ali há 0,33 h ociosas na janela de 4 h, e o B poderia subir para 2,33 ha.
- O próprio achado admite que a correção proposta muda o M2. Portanto é uma mudança da política já aceita, a decidir pelo Codex, e não um defeito do D-01.
- O delta só acrescentou o corte por prazo decidido em 5983640246, que tornou viável o que antes era inviável: B e C com 28,57 h em 20 h.

**2. A restrição não é falsa.**
- A restrição antiga do ativo e da sequência (A+B+C ≤ 100 h) é verdadeira e coincide com o corte de 100 h.
- O resultado é sempre viável: cada redução só diminui q, então as restrições anteriores continuam atendidas.
- Na busca aleatória, toda redução de parte fixa (3 578, 3 578 e 3 572 casos) veio com conflito=true; nenhuma veio com conflito=false.
- O atendido menor nunca esconde inviabilidade nem aparece num plano sem conflito: o usuário já vê o déficit (500 h em F5, 100 h em F1).
- Isso não preenche a régua de S2 ("capacidade materialmente subestimada por restrição falsa no arranjo comum").

**3. O motivo não é falso.**
- As partes, cada uma limitada à própria janela, somam 140 h, e de fato não cabem em 100 h.
- As frações informadas (50 % a 71,43 %) são as frações finais reais, como o M2 exige ("o motivo diz a fração final").
- A frase não afirma que a janela fica cheia. O decorrido mostrado (91,43 h) também não diz que fica.

**4. A decisão do Codex cobre o restante.**
- A decisão diz "não é novo otimizador", sem promessa de capacidade máxima nem de monotonicidade.
- A dependência de ordem no F1b, em que acrescentar D faz A subir, está dentro da política conservadora já aceita.

**Severidade:** como defeito do delta, nenhuma. Se o Codex quiser rever o M2 e acrescentar a devolução da folga, isso é uma melhoria da política existente, no máximo S3: limitada, conservadora e sempre com conflito já à vista. Não bloqueia a candidata.
```

## Veredito 1 (verif-restricao-falsa-0-1)

### refutado

```text
False
```

### reproduzido

```text
True
```

### severidade

```text
S3
```

### introduzido_pelo_delta

```text
True
```

### comando

```text
Cópias em /tmp/claude-0/-home-user-Safrion-Software-/65558514-68d9-57f5-9da3-513cd6735cdc/scratchpad/prerev7/verif-restricao-falsa-0-1/{novo=04bf6f2,antigo=ee4f954}, extraídas com git archive.
1) node run.js f5.json e node run.js f1.json: bloco REPARTIR real dos dois commits.
2) python3 run.py <dir> f5.json e python3 run.py <dir> f1.json: dados2.repartir dos dois commits.
3) Instrumentação de Object.keys(jan) em F5, numa cópia, com node -e.
4) node rnd.js 7 20000 e node rnd.js 99 20000: entradas aleatórias de uma máquina; conferência EDF independente; variante de devolução de folga; variante com os cortes em prazo crescente.
5) node m2.js: caso M2 do oráculo e variante de diagnóstico sem a restrição antiga duplicada.
6) python3 rend_multiconjuntos_unit.py em novo/.../gen37.
```

### saida

```text
**F5** (A rend 3, janela 100, 60 %; B e C rend 1, janela 20, 20 %; ativo a01; Q 1000)
- NOVO: alocado 234,2857; A 214,2857 ha / 71,4286 h; B 10 ha; C 10 ha; conflito true; decorrido 91,4286.
- Motivo do NOVO: 'as partes fixas em sequência não cabem na janela de 100 h: fazem de 50 % a 71,43 % do que cabia na própria janela'.
- ANTIGO: 242,8571; B = C = 14,2857 h, ou seja, 28,57 h numa janela de 20 h.
- F5seq (sequência declarada): mesmos números. Python NOVO e ANTIGO: mesmos números.
- Ordem de jan em F5: at:a01@100 [A,B,C], depois acq:1,2@20 [B,C], depois acq:0,1,2@100 [A,B,C].

**F1** (A rend 1, janela 100, 50 %; cinco B de janela 10, 10 % cada; a01)
- NOVO: 76,6667, com A 66,6667 e cada B 2. ANTIGO: 100, com cada B 6,67 h numa janela de 10 h. F4seq: igual ao F1.
- F1b: o mesmo com D (1 %, sem janela). NOVO: A 90,9091, alocado 110.
- F1c: D com janela finita de 1000 h. NOVO: também A 90,9091. ANTIGO: 160 sem conflito.

**Entradas aleatórias** (rnd.js, 20 000 entradas, os dois seeds)
- O NOVO ficou viável em todas pela conferência EDF independente.
- A variante de devolução de folga atendeu mais em 967 casos, 569 deles acima de 5 %, com diferença máxima de 24,7 %. O NOVO marcou conflito = true em todos esses casos (confFalse 0).
- A devolução de folga atendeu menos em 41 casos, todos com configurações sem %.
- Ordenar os cortes por prazo crescente ficou pior em 851 casos e melhor em 1116.

**Caso M2 do oráculo** (já existia na rodada 2)
- NOVO: A 5/3, B 2, C 25/3. Sobram 0,33 h ociosas na janela de 4 h, e o motivo diz 'não cabem na janela de 4 h: fazem de 41,67 % a 50 %'.

**Variante de diagnóstico sem a restrição antiga** (sq/at:/pl: não é registrada quando há um corte com os mesmos membros e o mesmo prazo)
- M2: não muda.
- F1: 100, com A 90,9091, igual ao F1c.
- F5: 266,6667.

**Oráculo:** RESULTADO 91/91 OK.
```

### fundamento

```text
O achado foi reproduzido no JS e no Python de 04bf6f2, com os números exatos de F5 e F1, e o mecanismo foi confirmado. A restrição antiga do recurso físico continua sendo registrada em `jan`: o 'at:a01' com a maior janela finita (100 h). Ela é idêntica ao corte por prazo @100 e é processada antes do corte @20. O laço proporcional das partes fixas corta A, B e C por 100/140; depois o @20 corta B e C de novo, e as horas liberadas não voltam para A.

Nas cópias e nos casos executados, o resultado é sempre viável (EDF independente) e conservador. Em todos os casos subestimados, o NOVO já marca conflito = true. Por isso não é S2:
- nenhum plano inviável é aceito;
- não existe restrição falsa, porque A+B+C ≤ 100 h e B+C ≤ 20 h são restrições verdadeiras;
- o usuário já vê o conflito e o saldo, e tem uma alternativa segura (reprogramar).

Classifico como S3.

**Partes do achado que refuto**

1. **"Motivo falso".** As partes fixas, tomadas como teto, precisam de 140 h numa janela de 100 h; então "não cabem" é literalmente verdadeiro, e a fração informada (50 % a 71,43 %) é exata. O oráculo M2, do Codex, fixa desde a rodada 2 o mesmo padrão: 0,33 h ociosas na janela de 4 h, com o mesmo texto de motivo. É comportamento decidido.
2. **Folga que "não volta".** A redução proporcional sequencial sem devolver folga é política anterior ao delta, também fixada pelo M2. A correção proposta (devolver a folga) muda o M2 e acrescenta um passo de otimização, contra o "não é novo otimizador" da decisão 5983640246. Na minha variante, ela também atende menos em 41 de 20 000 entradas quando há configurações sem %; não é uniforme.

**O que sobra, introduzido pelo delta e não coberto pela decisão nem pelo fora de escopo**

O delta acrescentou os cortes por prazo, mas manteve a restrição antiga de janela máxima, redundante com o corte do maior prazo. Por causa disso, o resultado depende de uma configuração que não altera a agenda de A e dos B:
- em F1, A fica com 66,67 ha;
- em F1b (D sem janela) e em F1c (D com janela de 1000 h), A fica com 90,91 ha;
- com D, a restrição antiga deixa de coincidir com o corte de 100 h. Sem janela, ela nem é criada; com 1000 h, não aperta nada.

Em ee4f954 não existiam os cortes menores, mas o resultado era inviável (D-01). A subestimação viável e a dependência de D são novas.

**Correção mínima, para o Codex decidir**

Não registrar a restrição antiga quando existe um corte com os mesmos membros e o mesmo prazo. É só diagnóstico em JS, não validado no Python nem no oráculo:
- o M2 fica igual;
- F1 passa a 100 ha, igual ao F1c;
- F5 passa a 266,67 ha.

Não domina em todas as entradas: a variante equivalente com os cortes em prazo crescente ficou 851 vezes pior e 1116 vezes melhor em 20 000. Se a política sequencial for mantida, basta registrar a dependência de ordem como conservadora.
```

