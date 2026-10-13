# BEN rodada 3 · desenho mínimo da recuperação de caixas entre ordens e lotes

Rótulo: **especificado**. Nada foi executado para este documento. Ele se apoia em três fontes:

- leitura do código em `/home/user/sp-proto`, branch `claude/prototipo-v44`, HEAD `0139898`;
- as saídas que as lentes A e B executaram na rodada 2 (`ben-rod2-lentes.json`, `integ-ver/BEN-c2-A/`, `integ-ver/BEN-c2-B/`);
- o aceite adicional do Codex (`ben-rod3/codex-6093132750.md`, BEN-REV-20261010-06, com o acréscimo do Gemini).

Os números dos exemplos são as saídas das lentes ou contas feitas a partir delas.

[crítica: a revisão adversarial **executou** sondas no motor real de 0139898, numa cópia própria (`ben-rod3/crit/wt`, `git worktree add --detach`), com `ben_unit_test.motor()` + node. Scripts e saídas em `ben-rod3/crit/` (p1 a p4, run5 a run7). Cada correção abaixo vem marcada com `[crítica: …]`, e a seção 9 lista as mudanças com a evidência e o rótulo executado ou especificado.]

## 0. Acordo curto (AGENTS §3.4)

```text
ID / resultado útil / persona: BEN-ROD3 · a falta de caixas tem uma saída real, e nenhuma ordem perde as caixas de que ainda precisa ·
  Igor (produção), Rui (almoxarife), Ana (gestora), Paula (conferência)
Requisitos do PRD e fora do escopo: PRD 41/42 (reserva na liberação, entrega do saldo elegível, sobra devolvida e conferida), 24 (servidor é a
  autoridade), ENG-011 (fórmula numa fonte só), BEN-D22..D32. Fora: compra de caixas (BEN-2), cancelar ordem liberada (BEN-6), mudar o contrato
  "a entregar" da O.S./app/SUP (fica a pergunta P3 da seção 7), filtro por local de packing
Autor / revisor / integrador: desenho e implementação Claude (lane BEN, lock I) / Codex, que chama o Gemini para a crítica do delta material /
  regime leve §3.5 (branch única, revisão sem bloquear)
Base / arquivos: 0139898 · tools/prototipo/v37/gen37/{ben.js, cenario.js, areas/processo_beneficiamento.py, areas/processo_estoque.py,
  ben_unit.js, ben_mutantes.py, ben_fluxo_test.py, ben_prop.js (novo), ben_prop_test.py (novo)} · docs/beneficiamento/DECISOES.md ·
  pacote docs/integracao/BEN/rod3/
  [crítica: o HEAD da branch já é a5ab722. `git diff --stat 0139898 a5ab722` mostra só docs/integracao/VISOES/*, então o código do BEN é o
  mesmo. Registrar a5ab722 como base do commit e 0139898 como base dos brutos "antes"]
Aceite e comando: seção 8. Todo teste novo reprova em 0139898 e passa depois
Estado / impedimento / próximo passo: desenho pronto · nenhum impedimento externo · próximo passo: C1 da seção 4, começando pelo teste que reprova
```

## 1. Por que o mesmo mecanismo reabriu duas vezes

Hoje cinco contas independentes decidem quantas caixas uma ordem tem, precisa ou pode ceder, e cada rodada corrigiu uma delas:

| Conta | Onde está hoje | Defeito de origem |
|---|---|---|
| livre | `cenLote` mais `cenDisp`: um lote só, o de maior livre (ben.js 74, 161; cenario.js 61, 82) | A execução já trabalha com uma linha por lote (BEN-D31). A liberação, o impedimento e o complemento enxergam um lote só |
| sobra | `benCxSobra` (ben.js 87-89), definida por fase | Em conferência a sobra é a custódia inteira, mas o estorno, o relançamento e o Reabrir ainda usam essas caixas |
| devolução | `cenDevolver` (cenario.js 108-116) devolve tudo ao livre | Não distingue a sobra da caixa em uso. A caixa em uso volta livre e outra ordem a leva |
| a entregar | `cenSaldoEntregar` (cenario.js 94) = solicitado − consumido − custódia | Depois da devolução, o saldo reabre sem reserva por trás (o "fantasma"), e o `cenEntregar` baixa a reserva de outra requisição com `Math.max` (cenario.js 103) |
| pré-preenchido | `processo_estoque.py` 449: `qtd: cu ? it.custodia : ''` | A tela refaz a conta e oferece a custódia inteira |

O remédio é um conjunto único de definições em `ben.js` (ENG-011), lido pelo BEN, pelo Estoque e por um gancho do `cenario.js`, mais invariantes verificados a cada passo de sequências aleatórias (seção 6). Assim o defeito aparece em qualquer combinação de comandos, e não só no recorte que a lente reproduziu.

## 2. Definições (fonte única em ben.js, salvo onde indicado)

Notação:

- `o` é uma ordem BEN.
- `x` é uma linha de caixas da ordem (item da caixa numa REQ; `benLinhas`, uma linha por lote, BEN-D31). Os campos da linha são `sol` (solicitado), `disp` (dispensado, campo novo), `ent`, `cons`, `cust` e `dev`.
- `l` é um lote do item caixa. Nele, `fis`, `quar` e `res` são o físico, a quarentena e o reservado, e `livre(l) = ⌊cenDisp(l)⌋`.
- `ABERTA = {Liberadas, Em execução, Em conferência}`.

| Nome | Definição | Observação |
|---|---|---|
| `benLotesCx(c)` | Lotes elegíveis: os lotes de `BENC.cx.item` com `livre(l) > 0`. A quarentena fica fora por `cenDisp`. Ordem: maior livre primeiro, empate pelo código do lote | O mesmo conjunto serve para contar e para reservar (aceite do Codex 2). Hipótese: as caixas estão no packing da ordem. O filtro por local fica fora do escopo |
| `livreTot(c)` | Σ `livre(l)` sobre `benLotesCx` | Substitui `benCaixasLivres` |
| `quarCx(c)` | `[{lote, qtd = l.quar}]` dos lotes com quarentena | Fica só na mensagem, com quem resolve: a gestora libera com o laudo (`cenLiberarQuarentena`) |
| `kgAberto(o)` | Para `o.etapa ∈ ABERTA`: `max(0, entrada − Σ saídas válidas)` (`benEntrada`, `benSoma(benValidos)`). Fora de ABERTA: 0 | **Não depende de `o.ben.conc` nem do estado visual** (aceite do Codex 1). Por isso não é a `benEmProc` |
| `usoMax(o)` | `⌈kgAberto ÷ BENC.cx.massa⌉`, com toda a fruta em caixa | Teto de proteção (BEN-D32), arredondado para cima: o mutante A1 do piso morre |
| ~~`necRota(o)`~~ | ~~`benCaixas(kgAberto, rota)`~~ | [crítica: retirada. Reaplicar `frac_vend` ao kg que sobra conta o descarte previsto duas vezes, porque o descarte costuma ser pesado por último. **Executado** (crit/p1.js, roteiro do proprietário R7, OB-0113 com 12.300 kg e 1.169 cx): depois da S-01 A 1.000 cx, `necRota − cust − pend` = 219 − 169 − 0 = **50**; depois da S-02 B 169 cx, 58 − 0 − 0 = **58**. São 610 kg que vão para o descarte. Na cadeia K2 dá 124 − 69 = 55. O painel mostraria "Faltam 50/58 caixas" no caminho feliz, e o "Pedir mais caixas" pré-preenchido reservaria caixas de que outra ordem precisa. É o mesmo tipo de cálculo material errado (S2) que a rodada quer fechar. A necessidade planejada já está em Σ`sol` (diretriz do Codex)] |
| `sobra(o)` | `max(0, ⌊Σcust⌋ − usoMax(o))` | Ordem A liberar: sem linha, logo 0. Liberadas: `usoMax` conta a entrada inteira. Em execução e Em conferência: o kg aberto, **com conferência dada ou não**. Encerradas: `usoMax = 0`, então a sobra é a custódia, que o I-a4 obriga a ser 0. Canceladas: só saem de A liberar, sem linha, logo 0 |
| `faltaExec(o)` | `max(0, min(usoMax(o), Σsol − Σcons) − Σcust − Σpend)`. Com o I-d2, é igual a `max(0, Σdisp − max(0, Σsol − Σcons − usoMax))` | [crítica: fórmula trocada. A necessidade restante é o **planejado ainda não consumido**, limitado pelo teto do kg aberto. A falta só nasce do que saiu da ordem sem reposição: a sobra dispensada que voltou a ser necessária depois de um estorno, ou a devolução avariada. **Contas executadas com os dados de crit/p1.js e p4.js:** roteiro S-01 = min(230, 169) − 169 = 0; S-02 = 0; cadeia K2 = min(130, 69) − 69 = 0; limite adicional (descarte de 2.000 kg, sobra de 139 recebida, estorno do descarte) = min(1.230, 1.169) − 1.030 = **139**; devolução avariada de 50 = 50; ordem planejada acima do teto (1.300 cx para 12.300 kg, sobra de 70 recebida) = 0. Se a caixa real render menos que o planejado, a falta aparece no registro do Produto ("Caixas acima da custódia … Pedir mais caixas"), um caminho que já existe] |
| `pend(x)` | `max(0, sol − (disp‖0) − cons − cust)` (`cenSaldoEntregar`, cenario.js) | É o PRD 42.1 com o termo `disp` explícito. **Só o BEN grava `disp`.** Nas linhas de O.S., app e SUP o resultado é idêntico (aceite do Codex: não subtrair o devolvido para todos). [crítica: a O.S. já usa "dispensar/dispensado" para a área (`osc_dispensar`, `o.osc.disp`, "saldo 120 ha dispensado 40 ha"). O nome interno pode ficar, mas **nenhum texto de tela** diz "dispensado" para caixa. O Estoque diz "devolvido como sobra", "avariado" ou "baixado no Fechar". Além disso, o `econta` do Estoque (processo_estoque.py 218: "sol − consumido − em custódia") tem de mostrar o termo novo quando `disp > 0`. Sem isso, a conta impressa não fecha com o "a entregar" (I-c3)] |
| `resTot(x)` | Base da semente + Σ movimentos `reserva` − Σ `reserva-baixa` da (REQ, item) (`cenResTot`, cenario.js) | Base da semente: o solicitado quando a REQ da semente está Reservada (como hoje); senão, **o entregue da semente** (hoje é 0). Para todas as linhas de O.S. da semente a reserva própria segue 0 (prova na seção 5) |
| `own(x)` | `max(0, resTot(x) − ent(x))`, limitado ao `l.res` (`cenResPropria`) | Reserva legítima ainda não entregue da linha |
| `devPadrao(o, x)` | `min(x.cust, sobra(o))`. Em conferência com `kgAberto(o) ≤ benFaixa(entrada, rota)`, ou no passo "Fechar processo": `x.cust` | Valor que o Estoque pré-preenche numa linha BEN. A O.S. continua com a custódia. [crítica: ampliado. **Executado** (crit/p4.js): uma ordem enviada para conferência com diferença de +5 kg, dentro da faixa de 12,3 kg, tem `usoMax = 1`. O formulário viria com 8 das 9 caixas, 1 ficaria em custódia, o Fechar seria recusado e o Rui teria de voltar depois do "Conferir balanço". Dentro da faixa, o kg aberto é ruído de pesagem: pré-preencher a custódia inteira é seguro, porque a regra de divisão devolve reservada à linha a parte acima da sobra (no exemplo, 1 cx) e o Fechar baixa essa reserva. Acima da faixa (estorno a substituir, classe por registrar), vale `min(cust, sobra)`, que evita a ida e volta inútil: entregar em conferência é recusado, então o Igor teria de reabrir só para receber de volta] |
| `devLinha(o)` | Linha com o maior `min(cust, sobra)`; no empate, a mais nova | Destino do atalho de devolução. [crítica: falta definir a divisão da sobra entre linhas. A sobra é da ordem, mas cada formulário é de uma linha: com REQ-041 e REQ-042 de 100 cx cada e `usoMax` 50, a sobra é 150, só que o atalho abre uma linha com 100. Definir `sobraLinhas(o)`: as linhas em ordem de `cust` decrescente (no empate, a mais nova), `qtd_i = min(cust_i, resto)`, até cobrir `sobra(o)`. A fonte do I-f1 leva essas `linhas`, e o texto diz "sobra de 150 un (REQ-041 100 + REQ-042 50)". Depois de salvar uma linha, "Voltar à OB-…" mostra o resto] |

**Regra de divisão da devolução** (gancho do BEN em `cenDevolver`, calculado **antes** de baixar a custódia). Ao receber `q` da linha `x` da ordem `o`, com `s = sobra(o)`:

- **Apta:** `livre = min(q, s)` volta livre, e `disp += livre`. O restante, `volta = q − livre`, volta ao mesmo lote **reservado à mesma linha**: `l.res += volta`, mais um movimento `reserva` com o det "devolução de caixas em uso: voltam reservadas à OB-…". Esse resto é material para substituição e não vira sobra.
- **Bloqueada** (avaria): tudo vai para a quarentena e `disp += q`. A falta que nasce aparece como `faltaExec`, e a saída é "Pedir mais caixas" (reserva legítima).
- [crítica: a mensagem do `cenDevolver` ("N un … devolvidos ao disponível") fica falsa quando parte volta reservada. Com a divisão, ela diz as duas partes: "139 un ao disponível (sobra da OB-0113); 730 un voltam reservadas à OB-0113 (caixas em uso)". O K5 da cadeia, que tem 69 de sobra inteira, não muda]
- [crítica: o gancho falha fechado. Se a linha é de ordem BEN e `benSobraDev` não existe na página (`typeof` falso), o `cenDevolver` recusa sem gravar ("regra do beneficiamento ausente"). Não pode devolver tudo ao livre em silêncio. Hoje toda página com `cenario.js_prefixo` tem o ben.js, então a recusa só aparece num harness montado sem o ben.js]

Em consequência, devolver sobra **não** reabre o "a entregar". Devolver caixa em uso reabre o "a entregar", com a reserva própria por trás (aceite do Codex: "devolver sobra não autoriza nova entrega sem reserva legítima").

**Fechar** (`benFechar`): em cada linha com `own > 0`, faz `l.res −= own`, grava um movimento `reserva-baixa` e soma `pend` ao `disp`. Fecha também o S3 da rodada 1, a reserva presa depois do Fechar.

## 3. Invariantes (numerados e testáveis)

O teste de cada invariante está na seção 3.1 (unidade e tela) e na seção 6 (propriedade).

### I-a · Sobra só existe quando provada
- **I-a1:** `benCxSobra(c, o) == sobra(o)` em toda fase, pela fórmula da seção 2.
  - Ordem em conferência com saída estornada ou com fruta sem registro: a sobra é `cust − usoMax`. Ex.: OB-0113 com a S-01 estornada, 1.000 cx e 10.000 kg: sobra 0. "Faltou a classe B", 169 cx e 1.690 kg: sobra 0. Caso 1 do Codex, 60 cx e 600 kg: sobra 0.
- **I-a2:** a recomendação a uma ordem `o` só cita uma ordem `b ≠ o` com `sobra(b) > 0`, e a quantidade citada é exatamente `sobra(b)`, nunca `cust(b)`.
- **I-a3** (transição Devolver na linha de `b`):
  - `livreTot` sobe no máximo `sobra_antes(b)`;
  - se a devolução é apta e `b ∈ ABERTA`: `cust(b) + Σown(b) ≥ min(usoMax_antes(b), cust_antes(b) + Σown_antes(b))`. Nenhuma devolução, guiada ou digitada, entrega a outra ordem caixas de que `b` ainda precisa.
- **I-a4:** Encerradas implica `cust = pend = own = 0` em todas as linhas. Canceladas implica nenhuma linha.

### I-b · Livre total de todos os lotes elegíveis
- **I-b1:** a ordem em A liberar tem o impedimento de caixas **se e somente se** `livreTot < caixas da ordem`.
  - O texto mostra `livreTot`.
  - Se `quarCx ≠ ∅`, cita lote, quantidade e quem libera: "100 un em quarentena no CX26-02: Ana (gestora) libera com o laudo em Estoque › Confira saldos".
- **I-b2:** a liberação aceita implica:
  - Σ`sol` das linhas = caixas da ordem;
  - uma linha por lote, e nenhuma linha reserva mais que o `livre` do seu lote naquele momento;
  - **uma linha só quando o maior lote cobre** (o comportamento de hoje);
  - quando falta, recusa sem gravar nada: tudo ou nada, nenhuma reserva parcial órfã.
- **I-b3:** o "Pedir mais caixas" de `n` é aceito se e somente se `livreTot ≥ n` e a fase permite.
  - Ordem de escolha: primeiro um lote que cubra sozinho (as linhas da ordem primeiro, depois o de maior livre); senão, divide (linhas da ordem primeiro, depois por livre decrescente).
  - O lote de uma linha nunca muda.
  - O que vai para outro lote vira REQ própria (BEN-D31).
- **I-b4:** o aviso da ordem nova, o impedimento, o complemento e a recusa usam o mesmo `livreTot`.

### I-c · Devolução guiada
- **I-c1:** o atalho de devolução é `EST.dc.html#dev=<REQ>&para=<OB pedinte>&ver=<ver de b>&sob=<sobra(b)>`. O Estoque abre "Receba devoluções" com o formulário dessa linha aberto.
- **I-c2:** o pré-preenchido vale `devPadrao(b, x)`, nunca a custódia de ordem aberta, salvo em conferência dentro da faixa e no passo "Fechar processo" [crítica: ver `devPadrao`]. O valor zero deixa o campo vazio. A O.S. não muda: custódia.
- **I-c3:** a linha e o formulário dizem:
  - a ordem de origem;
  - a sobra e a conta dela (custódia − o que ainda embala: kg ÷ 10 kg);
  - a ordem pedinte (`para`);
  - o lote de destino;
  - o que passar da sobra "volta reservado à OB-…".
  - [crítica: o mesmo vale para a mensagem depois de salvar (ver a regra de divisão) e para a conta do "a entregar" no Estoque (`econta`, com o termo da sobra devolvida)]
- **I-c4:** a primária da seção 3 do Estoque nunca aponta linha BEN com `devPadrao = 0`. Quando se chega por `#dev`, a primária é a linha do endereço.
- **I-c5:** ao salvar pelo atalho, o Estoque revalida a versão de `b` (`ver`) e a sobra (`sob`).
  - Se divergem, recusa sem escrita com "a OB-… mudou depois que você abriu (sobra 139 → 50)" e atualiza o formulário com o valor atual (aceite do Codex: "se obsoleto, recusa sem escrita e oferece recuperação").
  - [crítica: comparar só `ver` gera recusa espúria. Cada saída que o Igor registra na OB em execução sobe `o.ver` (`benToca`), e uma saída de Produto não muda a sobra (−cx na custódia, −cx no teto). Na tela isso seria "sobra 139 → 139" a cada poucos minutos. A recusa só cabe quando muda o que o Rui está decidindo: `sobra(b)`, `b.etapa` ou a custódia da linha. A `ver` vai no endereço e no histórico como contexto. Se o Codex fizer questão da `ver` como trava, a mensagem diz o que mudou, nunca "139 → 139" (pergunta P4). A segurança não depende disso: a regra de divisão já impede tirar caixa em uso]
  - Depois de salvar, aparece "Voltar à OB-0112" (`BEN.dc.html#OB-0112`), e o voltar do navegador reabre o painel (`bnHash`).

### I-d · A entregar e reserva
- **I-d1:** `pend(x)` segue a definição da seção 2. Nenhum outro módulo grava `disp`.
- **I-d2:** em toda linha de ordem BEN em ABERTA, `pend(x) == own(x)` exatamente. Sem fantasma: o "Pedir mais caixas" sugere `faltaExec(o)` [crítica: era `necRota − cust − pend`, retirada]. Quando dá 0, o campo fica vazio e a ajuda mostra a estimativa pelo kg em processo, só como texto, sem pré-preencher.
- **I-d3:** `cenEntregar(x, q)`:
  - baixa primeiro a reserva própria (`min(q, own(x))`);
  - o que passar dela só sai do livre, e o pedido é recusado quando `q > own(x) + cenDisp(l)`;
  - [crítica: **e continua recusado quando `q > l.fisico − l.quarentena`**, a trava física de hoje (cenario.js 102). Ela não pode ser trocada pela regra acima. **Executado** (crit/p2.js): contar o CX26-02 em 1.100 com o físico em 1.200 (AJ-71 pendente), liberar a OB-0113 (reserva 1.169) e aprovar o ajuste dá físico 1.100 com reserva 1.169. Nesse estado `own + cenDisp = 1.169 + 0`. Sem a trava física, a entrega de 1.169 passa e o físico vai a **−69**, estoque negativo (S2). Hoje a entrega é recusada com "O lote CX26-02 não tem 1.169 un livres"];
  - **nunca muda a reserva de outra linha** (aceite do Codex 3).

### I-e · Conservação (a cada passo)
- **I-e1** (linha): `ent == cons + cust + dev`, e todos os campos ≥ 0, `disp` incluído.
- **I-e2** (lote): `fis = fis_semente + Σ recebimento-nf − Σ entrega + Σ devolucao + Σ ajuste`, somados os movimentos do lote.
- **I-e3** (lote): `quar = quar_semente + Σ recebimento-nf bloqueado + Σ devolucao bloqueada − Σ inspecao`, com `0 ≤ quar ≤ fis`.
- **I-e4** (lote): `res = Σ own(x)` das linhas do lote de ordens não encerradas, mais as reservas de O.S. no lote (não há no item caixa). Vale também `0 ≤ res ≤ fis − quar`. [crítica: a segunda parte **não vale** depois de um ajuste de inventário aprovado depois da reserva. O caminho já existe no Estoque (`estAprovar` → `cenAprovarAjuste`, sem conferir a reserva) e foi executado em crit/p2.js: físico 1.100, reserva 1.169. Duas mudanças: (a) o harness não gera contagem nem ajuste, e o desenho diz isso de forma explícita (fora do BEN); (b) o painel da ordem mostra "Reserva sem físico: N caixas da REQ-… · Rui confere o lote" quando `l.reservado > l.fisico − l.quarentena`. É só aviso, e a trava física do I-d3 continua protegendo. Travar a aprovação do ajuste abaixo da reserva é mudança do Estoque e fica para outra fatia]
- **I-e5** (ordem e lote):
  - Σ`cons` das linhas = Σ`cx` das saídas válidas de Produto;
  - cada parte de `s.cons` cai no lote da sua linha;
  - Σ consumo − Σ estorno-consumo do lote = Σ`cons` das linhas do lote.
- **I-e6** (global): `Σfis + Σcust + Σcons = semente + Σ NF + Σ ajustes`.
- **I-e7:** recusa não grava: o estado e a `rev` ficam idênticos. [crítica: no motor o I-e7 vale por construção, porque `benMudar`, `cenMudar` e o `MUD` do harness trabalham numa cópia. A verificação do harness não reprova nunca e não deve contar como cobertura. O risco real é o comando **devolver sucesso com efeito parcial**, por exemplo uma alocação que reserva o que dá e não lança erro. Quem pega isso são o I-b2 ("aceita ⇒ Σsol = caixas") e o I-e9]
- **I-e9** (novo) [crítica: invariantes baratos que faltavam]:
  - em ordem BEN em ABERTA ou Encerradas, `Σ sol das linhas == o.ins[0].tot`. A liberação e o complemento mexem nos dois;
  - em linha BEN, `sol − disp − cons − cust ≥ 0` sem o `max(0, …)`. O `pend` com piso esconderia uma entrega acima do planejado.
- **I-e8** (isolamento):
  - um comando sobre a ordem A, ou sobre uma linha de A, não muda `cust`, `cons`, `sol`, `disp` nem `own` de linhas de outra ordem;
  - liberar e pedir mais caixas só tiram do livre;
  - um estorno reabre só a necessidade da própria ordem.

### I-f · Recomendação compara com o que de fato fica livre
- **I-f1:** `benCaixasRec` devolve `{t, h, why, falta, fontes, cobre}`.
  - `falta = caixas − livreTot`.
  - As fontes, na ordem de preferência: `sobra` (os, linhas, qtd = `sobra(b)`), depois `nf` (id, lote, qtd), depois `quarentena` (lote, qtd, quem). Primeiro vale uma fonte que cubra sozinha; senão, todas.
  - [crítica: `linhas` = `sobraLinhas(b)` (ver `devLinha`), com Σ `qtd_i` = `sobra(b)`. Para a `nf`, o texto diz "traz até N un": a conferência pode ter divergência ou quarentena (U49a). Para a `quarentena`, o texto é condicional ("se a inspeção aprovar, Ana (gestora) libera com o laudo"), porque caixa avariada não é recuperação certa. O `cobre` vale como está, mas o I-f1 só promete liberar quando as fontes foram executadas como indicadas]
  - `cobre ⇔ Σ qtd ≥ falta`.
  - Executadas as fontes como indicadas (sobra recebida apta, NF conferida apta, quarentena liberada com laudo) e com `cobre`, o impedimento de caixas desaparece e a liberação passa, se não houver outro impedimento.
  - Como a liberação usa todos os lotes, o lote de chegada não importa: o S3 do "lote errado" deixa de existir por construção.
- **I-f2:** sem cobertura, o texto diz "ainda faltam K un" e a ação real da fase:
  - A liberar: Cancelar a ordem;
  - Liberadas e Em execução: Pedir mais caixas quando a nota chegar;
  - Em conferência: **Reabrir a execução** e depois Pedir mais caixas [crítica: **executado** (crit/p4.js). Em conferência, `benComplementar` recusa ("na conferência não entra embalagem nova; reabra a execução") e `cenEntregar` também recusa ("Entregue só para O.S. liberada ou em execução"). Indicar "Pedir mais caixas" ou "Rui entrega no balcão" nessa fase manda a pessoa para uma ação que o sistema recusa. A recusa do `benSaida` em conferência (ben.js 346-347, "A REQ tem N a entregar: Rui entrega no balcão") muda pelo mesmo motivo];
  - a compra entra no BEN-2.
  - "Cancelar a ordem" só aparece em A liberar.
- **I-f3:** a própria ordem nunca é fonte (o mutante A6 morre).
- **I-f4:** a ordem ABERTA com `faltaExec > 0` mostra no painel "Faltam N caixas para os Y kg em processo" com a recuperação da fase (I-f2: Pedir mais caixas, ou Reabrir a execução em conferência; se `livreTot < N`, as fontes do I-f1). [crítica: com a `faltaExec` nova, o roteiro do proprietário e a cadeia não mostram falta em nenhum passo (contas na seção 2). Com a fórmula antiga, mostrariam 50, 58 e 55]
  - Nenhum registro é recusado por isso: o estorno passa sempre e a saída de Produto continua exigindo custódia (R-C01).
  - É o "limite adicional" do Codex: devolução válida, outra ordem reserva, estorno posterior de descarte.

### I-g · Um gesto, uma ação
- **I-g1:** `keydown` de Enter ou Espaço com `e.repeat === true` não ativa comando no BEN (`preventDefault` na captura). [crítica: só quando o alvo é `button` ou `[role=button]`. Num campo de texto (motivo, justificativa), segurar o Espaço é digitação. O Espaço não precisa de tratamento em botão: o clique dele sai no `keyup`, uma vez. O defeito é o Enter, que clica a cada `keydown` repetido]
- **I-g2:** depois de um comando que muda a fase ou fecha um formulário, o foco vai para o título ou estado do painel (`tabindex=-1`, não acionável). Nunca vai para a primária nova: chegar a ela pede Tab.
- **I-g3:** o 2º toque ou clique em até 400 ms continua absorvido (BEN-D25).
- **I-g4:** o aviso (`role=status`) não cobre botão do rodapé do painel. O `elementFromPoint` no centro de cada botão devolve o próprio botão logo depois da ação.

### I-h · Rascunho
- **I-h1:** Esc, o X ou o "Voltar" com formulário alterado não descartam. Aparece "Rascunho não salvo" com "Continuar editando" (foco no 1º campo) e "Descartar".
  - Um 2º Esc com o aviso à vista descarta.
  - Formulário sem alteração fecha como hoje.
  - Formulário alterado: algum valor de `pr_form` diferente de vazio, já que `prFval` só grava o que foi editado. [crítica: conta só o campo **digitado** (número ou texto). Escolher fluxo ou classe por toque sem digitar nada não pede confirmação, porque o atrito superaria o dano evitado. O clique no fundo escurecido (producao.py 92, `aria-label="Fechar painel"`) entra na lista com o Esc, o X e o Voltar. Guardar o rascunho e reabri-lo preenchido, em vez de confirmar, está **vetado**: seria "último valor" de quantidade e bruto (AGENTS §3.3)]

### 3.1 Achados da rodada 2 · invariante, onde, menor mudança e teste que reprova antes

Os testes U47 a U52 entram em `ben_unit.js`. Os modos novos entram em `ben_fluxo_test.py`. Os valores "antes" são as saídas das lentes em 0139898.

**S2-1 · conferência: a sobra pega caixas para relançar ou registrar o que faltou**
- Invariantes: I-a1, I-a3, I-f4.
- Onde: ben.js 87-89, `benCxSobra`: `kg = Liberadas ? entrada : (Em execução ? benEmProc : 0)`.
- Mudança: novas `benKgAberto(o)` e `benCxUsoMax(o)` (seção 2); `benCxSobra = max(0, cust − usoMax)`. Não reaproveitar a `benEmProc`, porque ela zera com `conc`. `benSelos` (197): o selo "Sobra em custódia" passa a exigir `benCxSobra > 0`.
- Teste que reprova antes:
  - U47a: OB-0113 em conferência com diferença 0 e conferida; estorno da S-01 → `benCxSobra = 0`, e a recomendação da OB-0112 não cita a OB-0113 (antes: 1000 e o atalho).
  - U47b: "faltou a classe B" → 0 (antes 169).
  - U47c: fixture do Codex 1 (600 kg, saída de 10 kg estornada, custódia 60) → 0 (antes 60).
  - U47d, controle: conferência com tudo registrado → sobra = custódia (U46c e K4 continuam).
  - U47e [crítica: novo]: conferência com diferença de +5 kg dentro da faixa (crit/p4.js: A 1.000 + B 160 + descarte 695, custódia 9) → `sobra = 8`, `devPadrao = 9`. Devolver 9 deixa 8 livres e 1 reservado à linha, e o Fechar encerra com reserva 0 numa visita só. Antes, o formulário vinha com 9 e tudo ia para o livre; com o desenho sem a correção, viria com 8 e o Fechar seria recusado.
  - Modo `conferencia` (1440 e 390): estorno na conferência e a OB-0112 sem o atalho (antes: o atalho e 1.000 no formulário).

**S2-2 · sobra parcial: "139" no BEN e 869 no formulário; "a entregar" fantasma; a entrega consome a reserva alheia**
- Invariantes: I-c1..c5, I-d1..d3, I-a3.
- Onde:
  - processo_estoque.py 449 (o pré-preenchido), 566-567 (a primária), 611-612 (o texto), 362-363 (o salvar);
  - ben.js 99 (o `h` do atalho);
  - cenario.js 94, 95-106 e 108-116;
  - processo_beneficiamento.py 206 (`sx = max(1,…)`).
- Mudança:
  1. Gancho no `cenDevolver`: `benSobraDev(c, o, it)` antes de baixar a custódia, e `benAposDevolver(...)` depois (a divisão da seção 2). Devolve `null` para linha que não é do BEN, e a O.S. fica igual.
  2. `cenSaldoEntregar` subtrai `(it.dispensado‖0)`.
  3. `cenEntregar`: `own = cenResPropria(...)`; recusa se `q > own + cenDisp(l)`; `l.reservado −= min(q, own)`. O conserto pós-fato do `estEntregar` (290-293) sai, e fica uma regra só. [crítica: (a) a trava física `q > l.fisico − l.quarentena` **fica** (I-d3, crit/p2.js); (b) do `estEntregar` sai só a restauração da reserva. A linha `it0.confirmado = false` **fica**: é o único lugar que zera a confirmação do app numa nova entrega de O.S. (o inicio_entrega_unit registra o "R7 residual": o `cenEntregar` não zera)]
  4. Estoque: `qtd: cu ? edev(x) : ''` com `edev = benDevPadrao ?? custódia`; trata `#dev=…&para=…&ver=…&sob=…`; o texto da linha e do formulário segue o I-c3; a revalidação segue o I-c5; o "Voltar à OB-…" no retorno. [crítica: entram também o `econta` com o termo da sobra devolvida e a mensagem dividida do `cenDevolver`]
  5. Atalho: `h = 'EST.dc.html#dev=' + devLinha(b) + …`.
  6. Sugestão do complemento: `faltaExec(o)` [crítica: era `max(0, necRota − cust − pend)`, que no roteiro sugeriria 50 e 58 sem falta nenhuma]. Quando dá 0, o campo fica vazio e a ajuda diz "nada falta pelo planejado".
- Teste que reprova antes:
  - U48a: OB-0113 em execução, 869 cx e 7.300 kg; `cenDevolver(869)` → CX26-02 com `res += 730`, `pend(REQ-041) == own == 730`, e `livreTot` sobe só 139 (antes: `res += 0` e pend 869).
  - U48b: em seguida a OB-0112 libera, e a entrega de 730 à REQ-041 passa sem mexer na reserva da REQ-042 (antes: "CX26-02 fís 31 res 12" e a REQ-042 sem o livre). [crítica: **com o próprio desenho a OB-0112 não libera nesse ponto.** Executado (crit/p4.js, a fixture da lente p2b): o livre total antes é 631, depois da devolução de 869 é 631 + 139 = **770 < 881**, então a OB-0112 fica impedida com "Faltam 111". O U48b precisa de mais 111 caixas livres antes de liberar, por exemplo `cenReceber(QA-CX-02, 200)` com a nota marcada como conferida. Só então se confere que a entrega de 730 à REQ-041 baixa só a reserva própria e que a REQ-042 fica com 881 reservadas. Sem isso, o teste reprova pelo motivo errado]
  - U48c: devolução guiada de 139 → `pend = 0` e sugestão 0 (antes: sugestão 1).
  - U48d: fixture do Codex 3 (QA-A: 60 solicitado, recebido e devolvido; lote com 100 de físico, 80 reservados para QA-B) → `cenEntregar(QA-A, 60)` recusado e QA-B com 80 (antes: aceito, "40/20").
  - Modo `sobra` (1440 e 390): toque em "Receber a devolução da OB-0113" na OB-0112; a seção 3 abre com o formulário da REQ-041, quantidade 139, e o texto cita OB-0113, OB-0112 e CX26-02. Depois de salvar, a OB-0113 fica com custódia 730 e aparece o "Voltar à OB-0112" (antes: "Confira recebimentos", 869 ou 1.169 no formulário, primária REQ-031).
  - Revalidação: abrir o atalho, registrar uma saída na OB-0113 em outra aba e salvar → recusa sem escrita com a sobra nova. [crítica: a saída da outra aba tem de **mudar a sobra**. Serve um descarte, que aumenta a sobra, ou um estorno de Produto, que a reduz. Uma saída de Produto mantém a sobra (−cx e −cx). Acrescentar também o controle: uma saída de Produto na outra aba → o salvar **aceita** (I-c5 corrigido)]
  - U48e [crítica: novo]: com a sobra de 150 em duas linhas (REQ-041 100 e REQ-042 100 de custódia, `usoMax` 50), a fonte traz `linhas = [{REQ-041 ou a mais nova, 100}, {a outra, 50}]`, e Σ = 150. Seguidas as duas, o livre total sobe exatamente 150 e a custódia + reserva própria da ordem fica em 50.

**S2-3 · caixas em mais de um lote: "Sem caixa, Cancelar" com 920 a 1.700 livres**
- Invariantes: I-b1..b4, I-f1, I-f2.
- Onde: ben.js 74 (`benCaixasLivres`), 78 (`benCaixasPadrao`), 161-162 (impedimento), 311 (`cenLiberar` de um lote), 387-396 (complemento), 93-103 (`benCaixasRec`).
- Mudança:
  - `benLotesCx`, `benLivreCx` e `benAlocarCx(c, linhas, n)` (seção 2, tudo ou nada);
  - `benReservaCx(c, o, aloc, quem, det)`, que cria a linha ou soma, uma por lote, com movimento `reserva` e os mesmos campos do `cenLiberar` (quem é "Sistema" na liberação);
  - `benAutorizarLiberar` deixa de chamar o `cenLiberar`: aloca primeiro, grava depois, e só então `o.reservado = true` e `etapa = Liberadas`;
  - `benComplementar` usa a mesma alocação;
  - `benCaixasRec` passa a usar fontes estruturadas e combinação (I-f).
  - `cenLote` e `cenLiberar` não mudam.
- Teste que reprova antes:
  - U49a: NF de 1.200 conferida com 1.100 aptas e 100 em quarentena; com CX26-01 = 600, o livre total é 1.700 → sem impedimento; a liberação grava REQ-041 com 1.100 (CX26-02) e REQ-042 com 69 (CX26-01) (antes: "1.100 para 1.169", recusa e "Cancelar").
  - U49b: q3, a sobra de 289 recebida → 920 ≥ 881 → libera (antes: recusa).
  - U49c: L39-131 → "Faltam 492" (antes 1.092).
  - U49d: fixture do Codex 2 (500 + 420) → `benLivreCx = 920`; liberar 900 dá as linhas 500 e 400; liberar 921 é recusado **sem nenhuma reserva** (I-b2).
  - U49e: complemento de 600 com 640 livres em dois lotes → duas linhas (antes: "540 livres").
  - U49f: a quarentena é citada com a gestora.
  - Modo `multilote` (1440 e 390): `p1_nf_parcial`, liberar, entregar as duas REQ, saídas, conferir e fechar 12.300 kg com diferença 0.

**S3 · a sobra comparada à falta no lote errado**
- Invariantes: I-f1 e I-b1.
- Onde: ben.js 93-99.
- Mudança: nenhuma além do S2-3; com o livre total o lote de chegada é indiferente.
- Teste que reprova antes: U49b, e a propriedade I-f1 no `seguirRec` (seção 6).

**S3 · Enter segurado dispara a operação seguinte**
- Invariantes: I-g1, I-g2 e I-g3.
- Onde: processo_beneficiamento.py 43-47 (`bnGuarda`), 48-53 (`bnRun`), 251-262 (foco).
- Mudança: ouvinte `keydown` na captura que bloqueia `e.repeat` de Enter e Espaço na tela BEN. No `bnRun` com sucesso, o foco vai para o título do painel (`tabindex=-1` no template do painel).
- Teste que reprova antes, no modo `teclado` (CDP `autoRepeat: true`):
  - T13: Enter segurado 0,7 s em "Autorizar rota e liberar" → Liberadas, com uma "Liberada (CMD-06)" e sem "Iniciada" (antes: Em execução).
  - T14: Enter e outro Enter 1 s depois → Liberadas (antes: Em execução).
  - T15: Enter segurado no "Registrar" da última saída → Em execução e uma saída nova (antes: Em conferência).
  - Os toques do roteiro com mouse e toque não mudam (29 a 1440 e 31 a 390); no modo teclado entra um Tab a mais por passo, o que fica registrado.
  - [crítica: o T14 (um 2º Enter **deliberado** 1 s depois) não é repetição de tecla. Ele só se sustenta porque o próximo comando mudou de sentido no mesmo lugar e "Iniciar processo" não tem volta (BEN-6). O ganho do I-g2 tem de ser medido contra o custo de um Tab por passo e registrado na BEN-D36. Sem o I-g2, o I-g1 e o I-g3 já fecham o T13 e o T15]

**S3 · NAV-CLAREZA: o atalho perde o contexto**
- Invariantes: I-c1, I-c3, I-c4 e I-c5.
- Onde: ben.js 99; processo_estoque.py (o novo tratamento de endereço, 566-567 e 611-612).
- Mudança: igual ao S2-2, itens 4 e 5. A BEN-D13 ("o EST não abre seção pelo endereço") fica superada para `#dev=`.
- Teste que reprova antes: modo `sobra`, com a seção "Receba devoluções" à vista, a primária "Receber devolução da REQ-041" e o retorno à OB-0112.

**S4 · mutantes A1, A2 e A6; nenhum teste de conferência com estorno**
- Invariantes: I-a1, I-f1 e I-f3.
- Onde: ben_unit.js; ben_mutantes.py.
- Mudança, em testes:
  - U50a: `kgAberto = 7.305` → `usoMax = 731` (mata A1).
  - U50b: duas sobras e uma nota; vale a fonte que cobre sozinha, na ordem sobra, nota, quarentena.
  - U50c: a ordem com sobra 20 pede 700 com 600 livres; a recusa não a cita (mata A6).
  - A2 e A8 são **equivalentes** no código atual: com a ordenação decrescente, o `find(n ≥ falta)` já devolve o primeiro da lista, e com inteiros o teto da falta não muda. Ficam registrados como equivalentes, não como lacuna. U47 cobre a conferência com estorno.
- Teste que reprova antes: U50a e U50c reprovam com os mutantes A1 e A6 aplicados; U47a reprova em 0139898.

**S4 · Esc descarta a saída preenchida**
- Invariante: I-h1.
- Onde: processo_beneficiamento.py 250 e 258-259. [crítica: **não** mexer em producao.py 167. O `pp_key` chama `v.pp_close()` no momento da tecla, e o BEN já substitui o `v.pp_close` (processo_beneficiamento.py 250). Envolver esse mesmo `v.pp_close` com o `bnSujo` cobre o Esc, o X, o fundo escurecido e o Esc com foco fora do painel (258-259) sem tocar no template comum da Produção, que também serve o PROD e as Cargas]
- Mudança: o fechar do BEN (Esc, X e Voltar) passa por `bnSujo(self)`, que mostra o aviso da I-h1.
- Teste que reprova antes: no modo `teclado`, T16: digitar 1000 e 10600, Esc → painel aberto, valores mantidos e aviso à vista; 2º Esc → fecha (antes: fechado e `[None, None]`).

**S4 · o aviso cobre a primária por 2 a 4 s**
- Invariante: I-g4.
- Onde: posição do `[role=status]` no template comum.
- Mudança: só no BEN, com painel aberto, o aviso sobe acima do rodapé e ganha `pointer-events:none`.
- Teste que reprova antes: modo `rodape`, com o `elementFromPoint` no centro de cada botão logo depois da ação (antes: o aviso).

**S4 · rótulos "Voltar | Cancelar | Confirmar…" e "Fechar" ao lado de "Fechar processo"**
- Invariante: uma saída por formulário; nenhum verbo repetido no rodapé.
- Onde: producao.py 166 (`pp_closeT`); o `EXTRAVALS` do BEN.
- Mudança: no BEN, o fechar genérico some quando o formulário já tem "Voltar". Depois de uma recusa, o "Fechar" vira "Voltar à lista". [crítica: o botão do rodapé está no template comum (producao.py 88), sem condição. Para escondê-lo só no BEN, a menor mudança é um valor opcional `pp_closeHide`, falso por padrão nas outras telas. O producao_fluxo_test e a varredura do PROD e das Cargas entram na bateria deste commit]
- Teste que reprova antes: modo `rodape`: cancelar dá `['Voltar', 'Confirmar cancelamento da OB-0112']`; a ordem conferida não tem "Fechar" (antes: "Cancelar" e "Fechar").

**Relacionado (rodada 1, S3) · reserva presa depois do Fechar**
- Invariantes: I-a4 e I-e4.
- Onde: ben.js 471-499 e cenario.js 210-212.
- Mudança: o Fechar baixa a reserva própria (seção 2), e o `cenResTot` desconta a `reserva-baixa`.
- Teste que reprova antes: U51: pedir 5, entregar 1.169 e fechar → CX26-02 com reserva 0 e pend 0 (antes: "fís 31 res 5").

**Relacionado (rodada 1, S4) · Estoque mostra "O.S. pede 640, reservado 540" e "confirmação no app"**
- Invariante: I-c3 (texto verdadeiro).
- Onde: processo_estoque.py 439, 421 e 441.
- Mudança: o "O.S. pede" passa a comparar com Σ`sol` das linhas da mesma ordem. O chip "Aguardando confirmação no app" some quando `benEh(o)`.
- Teste que reprova antes: modo `multilote`, linha REQ-041 e REQ-042 sem "O.S. pede" e sem o chip do app.

**Limite adicional do Codex · devolução válida, outra ordem reserva, estorno do descarte**
- Invariantes: I-f4, I-e8 e I-a3.
- Onde: ben.js 200-217 (`benProx` e `benSelos`).
- Mudança: `faltaExec` no próximo passo e no selo "Faltam N caixas", com a recuperação; o estorno não ganha trava.
- Teste que reprova antes: U52: OB-A em execução registra descarte de 2.000 kg; Rui recebe a sobra (guiada); OB-B libera com ela; OB-A estorna o descarte → o estorno passa, OB-B fica intacta, OB-A mostra "Faltam N" com "Pedir mais caixas", e o pedido é aceito ou recusado conforme `livreTot` (antes: sem aviso de falta, e a sugestão ignora a falta real).
  - [crítica: fixar o número. Com a OB-A no L39-132 (12.300 kg, 1.169 cx entregues), a sobra recebida é 139 e a falta depois do estorno é **exatamente 139**. Acrescentar a variante em conferência: OB-A enviada para conferência e o estorno feito lá → o estorno passa, o painel mostra "Faltam 139" com **"Reabrir a execução"**, e não oferece "Pedir mais caixas" (I-f2)]
- U54 [crítica: novo, falso alarme]: no roteiro do proprietário (OB-0113, 1.169 cx) depois da S-01 A 1.000 cx e da S-02 B 169 cx, e na cadeia depois do A 1.100 cx, `faltaExec = 0`. Não aparece "Faltam N caixas" no painel nem no selo, e o "Pedir mais caixas" vem vazio. Com a fórmula pela `necRota`, o teste reprova: 50, 58 e 55 (crit/p1.js).

## 4. Mudanças por arquivo e ordem dos commits

Cada commit traz primeiro o teste, que reprova, e depois o código. Bateria da seção 8.

**C1, motor (definições, sobra, devolução, a entregar, Fechar):**
- `ben.js`: `benKgAberto`, `benCxUsoMax`, `benCxSobra` nova, `benSobraDev`, `benAposDevolver`, `benDevPadrao`, `benDevLinha`, `benSobraLinhas` e `faltaExec` [crítica: pela fórmula nova, sem `necRota`]; `benSelos`; baixa da reserva no `benFechar`; recusa do `benSaida` em conferência que aponta "Reabrir a execução" (I-f2).
- `cenario.js`:
  - `cenSaldoEntregar` com `dispensado`;
  - `cenDevolver` com o gancho, que falha fechado em linha BEN, e a mensagem dividida;
  - `cenResTot` com a base da semente e a `reserva-baixa`;
  - `cenEntregar` com a reserva própria (I-d3), **mantida a trava física** [crítica].
- Testes: U47 (com U47e), U48 (U48b com a nota extra, U48e), U51, U52 (com a variante em conferência) e U54; `TRILHA` reescrita; `ben_prop.js` e `ben_prop_test.py`.

**C2, motor (livre total e linha por lote):**
- `ben.js`: `benLotesCx`, `benLivreCx`, `benAlocarCx` e `benReservaCx`; `benImpedimentos`, `benCaixasPadrao`, `benAutorizarLiberar`, `benComplementar` e `benCaixasRec` (fontes, cobre, I-f).
- Testes: U49 e U50, mais os textos que mudam (seção 5).

**C3, tela do Estoque:**
- `processo_estoque.py`: pré-preenchido, endereço `#dev=`, textos, primária, revalidação (pela sobra e pela fase, I-c5 corrigido), retorno, `MTIPO['reserva-baixa']`, "O.S. pede" e chip. [crítica: também o `econta` (218) com o termo da sobra devolvida; no `estEntregar` sai só a restauração da reserva, e o `it0.confirmado = false` fica]
- Testes: modos `sobra` e `multilote`.

**C4, tela do BEN:**
- `processo_beneficiamento.py`: repetição de tecla (só em botão), foco depois da ação, `bnSujo` (envolvendo o `v.pp_close` do próprio BEN, sem mexer no `pp_key` comum), aviso fora do rodapé, rótulos (`pp_closeHide` opcional no template comum) e sugestão do complemento por `faltaExec`. [crítica]
- Testes: modos `teclado`, `rodape` e `conferencia`.

**C5, docs:**
- `DECISOES.md`: BEN-D33 (sobra pelo kg aberto em toda fase aberta; devolução dividida em sobra e caixa em uso; `dispensado`), BEN-D34 (livre total; linha por lote na liberação; tudo ou nada), BEN-D35 (Fechar baixa a reserva não entregue), BEN-D36 (teclado, rascunho, aviso e rótulos).
- Marcar a BEN-D13 e a BEN-D32 como em parte superadas.
- Pacote `docs/integracao/BEN/rod3/` com diff, brutos antes e depois e a trilha mínima da propriedade.

## 5. O que não muda e riscos de regressão

**Não muda (aceites anteriores e direção do Codex):**
- As caixas da ordem são a necessidade da rota (BEN-D23). `benCaixasPadrao.cx = sug`, sem redução ao livre, sem justificativa de perda, sem confirmação genérica e sem mudar rendimento ou `frac_vend`.
- A falta é impedimento antes da liberação, a recusa não grava, e a recuperação é só real: nota, sobra provada ou quarentena com laudo.
- Cancelar só em A liberar (BEN-D22). Cancelar ordem liberada continua no BEN-6.
- Recibo (`benRecibo`), versão esperada (`benVer`) e perfil (`cenExige` e `cenQuem`) em todo comando, inclusive na alocação nova. [crítica: "em todo comando" não é verdade hoje. `benAutorizarLiberar`, `benIniciar`, `benConcluir`, `benConferir`, `benReabrir` e `benFechar` não têm recibo. A repetição deles vira "Já feito" pela fase. O `cenDevolver` e o `cenEntregar` não têm recibo nem versão. Escrever: "recibo onde já existe (nova, retirar, cancelar, saída, complemento, estorno, justificar); nos outros, recusa pela fase. A alocação nova roda dentro do `benAutorizarLiberar` e do `benComplementar` e herda o que cada um tem"]
- Faixa móvel a 390 px; ordem criada aberta (D26); "Enviar para conferência" (D27); Canceladas como recusa (D28); sem primária no cabeçalho (D29); foco ao abrir (D30).
- Linha por lote no complemento (BEN-D31): o `it.lote` nunca muda, o consumo é FIFO por linha, e o estorno e a devolução vão ao lote de origem.
- Proteção de 100 % e teto (BEN-D32); `benEmProc` (exibição); `cenLote`, `cenLiberar`, `cenDisp` e `cenPodeEncerrar`; Kanban de 5 fases.

**Expectativas que mudam de propósito** (registrar uma a uma na BEN-D33 e BEN-D34, como U41e e U41g na BEN-D31):
- `TRILHA.res` de `ben_unit.js` 576-582: `Σ max(0, sol − ent)` vira `Σ pend` das linhas abertas, já que a caixa em uso devolvida fica reservada. Afeta U45c e U45g.
- Harness do Codex (`rev03/run_harness.py`): os 4 casos continuam passando, porque ele confere o físico. A saída impressa do CX26-01 passa de `[540, 0]` para `[540, 540]`: as 540 caixas devolvidas em execução, com 12.300 kg a embalar, voltam reservadas à ordem. Confirmar com o Codex (P1, seção 7).
- U46a, U46c, U46e e os passos do modo `cadeia` que citam 600 ou 281, entre eles K1 e K4 (ben_fluxo_test.py 653-655 e 669): "600 un disponíveis para 881" vira **631** (os 31 do CX26-02 contam), "Faltam 281" vira **250**, e o "600 un livres" da recusa do complemento vira 631. No K4, a sobra de 69 não cobre, então o texto passa a dizer "ainda faltam 181". [crítica: listar também o **K3** (ben_fluxo_test.py 664: "Pedir 1.000 un: 600 un livres … Faltam 400 un", que passa a 631 e 369) e o **U46e** (ben_unit.js 667: "Pedir 700 … Faltam 100 un", que passa a 631 e 69). O K2 e o roteiro R7 não ganham "Faltam N" com a `faltaExec` nova; com a fórmula antiga ganhariam (U54)]
- O caso "conference-all-custody" do harness 9/9 do Codex, com a expectativa 60, já foi retirado pelo Codex. Nenhum teste nosso deve exigir sobra igual à custódia em conferência com diferença aberta.
- No modo `teclado`, entra um Tab a mais depois de cada comando (I-g2). O rodapé depois de uma recusa diz "Voltar à lista" (BEN-D29).

**Chamadores das funções compartilhadas (cenario.js) e efeito:**

| Função | Muda? | Chamadores | Efeito |
|---|---|---|---|
| `cenSaldoEntregar` (94) | − `dispensado` | cenario.js 101 e 171-172 (`cenIniFalta`); ben.js 65; processo_estoque.py 199; processo_os.py 291 e 618; mobile.py 217, 436 e 690; testes ben_unit, inicio_entrega_unit e quantidade_test | O.S., app, SUP e DOM: nenhum, porque o campo só é gravado em linha BEN. BEN: some o fantasma |
| `cenLote` (61) | não | `cenLiberar` e `cenConcPrevia`; processo_os.py 367 e 657; irrigacao_estado.js 156; mip.js 258; legal_unit e quantidade_test; o BEN deixa de chamar (74, 161 e 390) | nenhum fora do BEN |
| `cenLiberar` (75) | não | processo_os.py e os testes de O.S., app e EST; o BEN deixa de chamar (311) | nenhum |
| `cenDevolver` (108) | gancho só para ordem BEN | processo_estoque.py 294; ben_unit (17 usos), aprova_quem_decide_unit (3), ben_fluxo_test, os_cenario_test e os_v39_bloq_test | O.S.: nenhum, porque o gancho devolve `null`. BEN: o que passa da sobra volta reservado, e a mensagem diz as duas partes [crítica] |
| `cenEntregar` (95) | baixa só a reserva própria; recusa acima de `own + livre` **e acima de `fis − quar`** [crítica] | processo_estoque.py 292; ben_unit (14), aprova_quem_decide_unit (5), inicio_entrega_unit, quantidade_test, app_*_test, ostela.py, osfix.py e tabelas_est_test | Na tela, nada muda, porque o ESTV.g_ent já limita a `livre + reserva própria` e o `estEntregar` já devolvia a reserva alheia. No motor, deixa de baixar a reserva de outra REQ: um teste que dependa disso revela o mesmo defeito latente e é registrado. [crítica: conferido na leitura. O aprova_quem_decide_unit 147 e 168 entrega 10 L na REQ-035, que tem reserva própria 0, e hoje baixa a reserva da REQ-039 de 65 para 55. Os testes não conferem o `reservado`, então seguem passando, e depois da mudança a REQ-039 fica com 65] |
| `cenResTot` (210) | base da semente não Reservada = o entregue da semente; − `reserva-baixa` | `cenResPropria`, usada por `cenConcPrevia` (conciliação da O.S. e o DOM consumo divergente); processo_estoque.py `eresTot` | O.S.: idêntico. Nas REQs da semente fora de Reservada (031, 035, 036, 038, 022 a 025), a reserva própria era `max(0, 0 − ent)` e passa a `max(0, ent0 − ent) = 0`. Não há `reserva-baixa` fora do BEN |
| `cenDisp`, `cenPodeEncerrar` e `cenIniFalta` | não | inicio.py 639; benProx e benFechar; estDevolver | nenhum |

O PCM (`areas/maquinas.py`) usa o estoque próprio (`c.itens`) e não é afetado. O `ben.js` entra em toda página do estado (`cenario.js_prefixo`): os nomes novos precisam passar pela verificação de nomes não redefinidos do `ben_unit_test.py`, e o `cenario.js` chama o gancho com `typeof`. [crítica: com a falha fechada para linha BEN (seção 2)]

**Riscos residuais (S3 no máximo):**
- [crítica: o ajuste de inventário aprovado depois da reserva deixa `reservado > físico − quarentena` (crit/p2.js). Com a trava física mantida no `cenEntregar`, não há estoque negativo [revisão A4, 13/10: isso vale para a entrega; aprovar um ajuste de contagem velha depois da entrega ainda pode deixar o físico negativo (−69, sondas/pE.js do revisor, também na base). É tarefa do Estoque, fora do BEN], e o aviso "Reserva sem físico" vai para o painel (I-e4). Travar a aprovação do ajuste fica para o Estoque, em outra fatia]
- [crítica: `cenAprovarAjuste` chamado direto no motor usa o `contado` absoluto, e um movimento entre a contagem e a aprovação some do físico. O `estAprovar` da tela recalcula `contado = físico + d` antes e escapa disso. Por isso o I-e2 só vale pelo caminho da tela, e o harness não chama `cenAprovarAjuste`]
- O `usoMax` supõe a caixa média dentro do aviso R-C04 (±5 %) e `frac_vend ≤ 100 %`. Caixa muito mais leve pode exigir mais caixas, e a saída é "Pedir mais caixas" (I-f4).
- A reserva acima do uso máximo (U46d: 1.300 cx para 12.300 kg) não é oferecida como recuperação, porque só a custódia é. Dispensar reserva excedente seria ação nova (BEN-6).
- Na O.S., a devolução de sobra no meio da execução continua reabrindo o "a entregar" (PRD 42.1). Com o I-d3 ela não consome reserva alheia, mas pode sair do livre: pergunta P3.

## 6. Propriedade aleatória: harness no motor real (esboço, especificado)

Arquivos: `ben_prop.js` e `ben_prop_test.py`. O executor carrega `ben_unit_test.motor()` (perfis, CEN0, cenario.js, producao.js, ben.js e o núcleo da O.S.) mais `ben_prop.js` no node.

- Sementes fixas: 20261010, 7 e 4242. RUNS = 120 e STEPS = 35, com orçamento de até 60 s na bateria; o noturno roda maior.
- Em cada falha o harness grava a semente, o passo, o invariante e a **menor sequência reprodutora**, encolhida por remoção de passos.
- O oráculo não chama as funções sob teste: refaz as contas a partir dos campos e dos movimentos, usando só os primitivos decimais (`prSoma`, `prSub`, `prM` e `prCmp`).
- [crítica: o esboço abaixo foi **executado** em 0139898 (crit/run5.js = motor + o bloco js como está). Saída: `{"ok":false,…,"falhas":[5× {"passo":0,"inv":"I-f1","info":["OB-0112","falta",null,341]}]}`. Todas as sequências param no passo 0, porque o `link.falta` não existe em 0139898. Com 5 falhas de teto e parada na primeira violação, **o aceite 1 não se cumpre**. Além disso, um `devolver` guiado chamaria `benDevPadrao`, que não existe, e o node pararia com ReferenceError. Correções no código abaixo: (1) detectar a API nova e pular a verificação que depende dela na rodada "antes"; (2) no "antes", registrar a 1ª ocorrência **de cada invariante** e seguir a sequência, sem parar na primeira; (3) conferir o `inv(CEN0)` antes do passo 0 e deixar o encolhimento tirar também o último passo; (4) acrescentar I-f4, I-b3 e I-e9. **Executado com (1) e (2)** (crit/ben_prop_shim2.js, 360 sequências × 35 passos, 21,8 s): aparecem os seis invariantes do aceite 1, a saber I-d2 (trilha mínima `[devolver REQ-030 guiado]`), I-a3 (`[estornar OB-0110, devolver REQ-030 guiado]`), I-b1, I-a4, I-e4 e I-a1. Com parada na primeira violação, I-a4 e I-e4 ficam escondidos atrás do I-d2. O orçamento de 60 s cabe: foram 21,8 s nas 3 sementes. **O bloco js corrigido abaixo também foi executado em 0139898** (crit/run8.js = motor + o bloco extraído deste arquivo, 27,6 s). Saída: `invariantes: [I-d2, I-a3, I-b1, I-a4, I-e4, I-b3, I-a1]`. Trilhas mínimas: I-d2 `[devolver REQ-030 guiado]` (1 passo); I-a3 `[estornar OB-0110, devolver REQ-030 guiado]`; I-a1 `[estornar OB-0110, concluir OB-0110]`; I-a4 `[devolver REQ-030 guiado, concluir, justificar, conferir, fechar OB-0110]`; I-e4 com 7 passos (pedir 636 sem entregar e fechar); I-b1 e I-b3 com 5 passos (dois lotes; 'Pedir 616 un: 538 un livres' com 750 livres no total). Essas trilhas são os casos fixos do U53]

```js
// ben_prop.js — depois do motor. Saída: JSON {ok, runs, falhas:[{seed, passo, inv, info, trilha}]}
const SEEDS = [20261010, 7, 4242], RUNS = Number((globalThis.process && process.env.RUNS) || 120), STEPS = Number((globalThis.process && process.env.STEPS) || 35);
const CX = BENC.cx.item, MASSA = BENC.cx.massa, IG = 'Igor', PA = 'Paula', AN = 'Ana', RU = 'Rui', EPS = 1e-9;
const ABERTA = ['Liberadas', 'Em execução', 'Em conferência'];
function rng(s) { return () => { s = (s + 0x6D2B79F5) | 0; let t = Math.imul(s ^ (s >>> 15), 1 | s); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
function MUD(c, fn) { const x = cenClone(c); let r; try { r = fn(x) || {}; } catch (e) { r = { erro: String(e.message || e) }; }
  if (!r.erro && !r.nada) { Object.keys(c).forEach(k => delete c[k]); Object.assign(c, x); } return r; }
/* ---------- oráculo (independente das funções sob teste) ---------- */
const N = v => Number(v) || 0;
const lotesCx = c => Object.values(c.lotes).filter(l => l.prod === CX);
const linhas = c => Object.values(c.reqs).flatMap(r => r.itens.filter(i => i.prod === CX).map(it => ({ r, it, o: c.ordens[r.os] })));
const livreTot = c => lotesCx(c).reduce((a, l) => a + Math.floor(Math.max(0, l.fisico - l.quarentena - l.reservado) + EPS), 0);
function kgAberto(o) { if (!benEh(o) || ABERTA.indexOf(o.etapa) < 0) return 0;
  const x = prSub(prSoma(o.ben.ent.map(e => e.kg)), prSoma(o.ben.sai.filter(s => !s.estorno).map(s => s.kg))); return prCmp(x, 0) > 0 ? x : 0; }
function usoMax(o) { const k = kgAberto(o), m = prM(MASSA); return prCmp(k, 0) > 0 ? Number((prM(k) + m - 1n) / m) : 0; }
const custO = (c, o) => linhas(c).filter(x => x.o === o).reduce((a, x) => a + x.it.custodia, 0);
const sobra = (c, o) => { const cu = Math.floor(custO(c, o) + EPS); return ABERTA.indexOf(o.etapa) >= 0 ? Math.max(0, cu - usoMax(o)) : cu; };
const pend = it => Math.max(0, it.solicitado - N(it.dispensado) - it.consumido - it.custodia);
function resTot(c, rid) { const s0 = CEN0.reqs[rid], i0 = s0 && s0.itens.find(i => i.prod === CX); const b = i0 ? (s0.estado === 'Reservada' ? i0.solicitado : i0.entregue) : 0;
  return b + c.movs.filter(m => m.req === rid && m.prod === CX && (m.tipo === 'reserva' || m.tipo === 'reserva-baixa')).reduce((a, m) => a + (m.tipo === 'reserva' ? m.qtd : -m.qtd), 0); }
const own = (c, x) => Math.max(0, resTot(c, x.r.id) - x.it.entregue);
function ledger(c, l) { const z = CEN0.lotes[CX + '|' + l.lote] || { fisico: 0, quarentena: 0 }; const mv = c.movs.filter(m => m.prod === CX && m.lote === l.lote);
  const S = (t, f) => mv.filter(m => m.tipo === t && (!f || f(m))).reduce((a, m) => a + m.qtd, 0);
  return { fis: z.fisico + S('recebimento-nf') - S('entrega') + S('devolucao') + S('ajuste'), quar: z.quarentena + S('recebimento-nf', m => !m.apto) + S('devolucao', m => !m.apto) - S('inspecao') }; }
const total0 = (() => { const c = CEN0; return lotesCx(c).reduce((a, l) => a + l.fisico, 0) + linhas(c).reduce((a, x) => a + x.it.custodia + x.it.consumido, 0); })();
/* ---------- invariantes de estado ---------- */
function inv(c) { const V = [], bad = (id, info) => V.push({ id, info }); const L = linhas(c);
  L.forEach(x => { const it = x.it;
    if (Math.abs(it.entregue - it.consumido - it.custodia - it.devolvido) > EPS) bad('I-e1', [x.r.id, it]);
    if ([it.entregue, it.consumido, it.custodia, it.devolvido, N(it.dispensado)].some(v => v < -EPS)) bad('I-e1', [x.r.id, 'negativo', it]);
    if (benEh(x.o) && ABERTA.indexOf(x.o.etapa) >= 0 && Math.abs(pend(it) - own(c, x)) > EPS) bad('I-d2', [x.r.id, pend(it), own(c, x)]);
    if (benEh(x.o) && x.o.etapa === 'Encerradas' && (it.custodia > EPS || pend(it) > EPS || own(c, x) > EPS)) bad('I-a4', [x.r.id, it, own(c, x)]);
    if (benEh(x.o) && x.o.etapa === 'Canceladas') bad('I-a4', [x.r.id, 'linha em ordem cancelada']); });
  lotesCx(c).forEach(l => { const g = ledger(c, l);
    if (Math.abs(g.fis - l.fisico) > EPS) bad('I-e2', [l.lote, g.fis, l.fisico]);
    if (Math.abs(g.quar - l.quarentena) > EPS || l.quarentena < -EPS || l.quarentena > l.fisico + EPS) bad('I-e3', [l.lote, g.quar, l.quarentena]);
    const r = L.filter(x => x.it.lote === l.lote && x.o && x.o.etapa !== 'Encerradas').reduce((a, x) => a + own(c, x), 0);
    if (Math.abs(r - l.reservado) > EPS || l.reservado > l.fisico - l.quarentena + EPS) bad('I-e4', [l.lote, r, l.reservado]); });
  const T = lotesCx(c).reduce((a, l) => a + l.fisico, 0) + L.reduce((a, x) => a + x.it.custodia + x.it.consumido, 0);
  const T0 = total0 + c.movs.filter(m => m.prod === CX && (m.tipo === 'recebimento-nf' || m.tipo === 'ajuste')).reduce((a, m) => a + m.qtd, 0);
  if (Math.abs(T - T0) > EPS) bad('I-e6', [T, T0]);
  benOrdens(c).forEach(o => { const cons = L.filter(x => x.o === o).reduce((a, x) => a + x.it.consumido, 0);
    const cx = o.ben.sai.filter(s => !s.estorno && s.fluxo === 'Produto').reduce((a, s) => a + s.cx, 0); if (Math.abs(cons - cx) > EPS) bad('I-e5', [o.id, cons, cx]);
    if (benCxSobra(c, o) !== sobra(c, o)) bad('I-a1', [o.id, o.etapa, benCxSobra(c, o), sobra(c, o)]);
    const tot = ((o.ins || [])[0] || {}).tot || 0;
    if (o.etapa === 'A liberar') { const im = benImpedimentos(c, o).find(x => x.cx);
      if (!!im !== (livreTot(c) < tot)) bad('I-b1', [o.id, livreTot(c), tot, im && im.t]);
      /* [crítica: 'falta' in k — no "antes" (0139898) a API nova não existe; pular em vez de reprovar tudo no passo 0] */
      const k = im && im.link; if (k && 'falta' in k) { if (k.falta !== tot - livreTot(c)) bad('I-f1', [o.id, 'falta', k.falta, tot - livreTot(c)]);
        (k.fontes || []).forEach(f => { if (f.os === o.id) bad('I-f3', [o.id, f]); if (f.tipo === 'sobra' && f.qtd !== sobra(c, c.ordens[f.os])) bad('I-a2', [f, sobra(c, c.ordens[f.os])]); });
        if (k.cobre !== ((k.fontes || []).reduce((a, f) => a + f.qtd, 0) >= k.falta)) bad('I-f1', [o.id, 'cobre', k]); } }
    else { const t = benCaixasRec(c, o, livreTot(c), livreTot(c) + 1).why || ''; if (/Cancelar a ordem/.test(t)) bad('I-f2', [o.id, o.etapa, t]);
      if (o.etapa === 'Em conferência' && /Pedir mais caixas|entrega no balcão/.test(t) && !/Reabr/.test(t)) bad('I-f2', [o.id, 'conferência sem Reabrir', t]); }
    /* [crítica: I-e9 e I-f4 (benFaltaCx = faltaExec da seção 2)] */
    const Lo = L.filter(x => x.o === o), sol = Lo.reduce((a, x) => a + x.it.solicitado, 0), consO = Lo.reduce((a, x) => a + x.it.consumido, 0);
    if (Lo.length && (ABERTA.indexOf(o.etapa) >= 0 || o.etapa === 'Encerradas') && sol !== (((o.ins || [])[0] || {}).tot || 0)) bad('I-e9', [o.id, 'Σsol ≠ ins.tot', sol, o.ins]);
    Lo.forEach(x => { if (x.it.solicitado - N(x.it.dispensado) - x.it.consumido - x.it.custodia < -EPS) bad('I-e9', [x.r.id, 'pend bruto < 0', x.it]); });
    if (ABERTA.indexOf(o.etapa) >= 0 && typeof benFaltaCx === 'function') { const f = Math.max(0, Math.min(usoMax(o), sol - consO) - custO(c, o) - Lo.reduce((a, x) => a + pend(x.it), 0));
      if (benFaltaCx(c, o) !== f) bad('I-f4', [o.id, benFaltaCx(c, o), f]); } });
  return V; }
/* ---------- comandos (parâmetros fixos no objeto: a trilha se repete igual) ---------- */
function exec(c, op) { const o = op.o && c.ordens[op.o]; const r0 = benRota('PACK-FRU|3');
  switch (op.k) {
    case 'criar': return MUD(c, x => benNova(x, { lotes: [{ lote: op.lote, kg: prFis(x, op.lote) }], cx: op.cx }, IG));
    case 'liberar': return MUD(c, x => benAutorizarLiberar(x, op.o, IG));
    case 'cancelar': return MUD(c, x => benCancelar(x, op.o, 'prop', IG));
    case 'iniciar': return MUD(c, x => benIniciar(x, op.o, IG));
    case 'pedir': return MUD(c, x => benComplementar(x, op.o, op.n, IG));
    case 'entregar': { const it = (c.reqs[op.rid] || { itens: [] }).itens.find(i => i.prod === CX); const q = op.q === 'pend' ? (it ? Math.floor(pend(it)) : 0) : op.q;
      return MUD(c, x => cenEntregar(x, op.rid, CX, q, IG, RU)); }
    case 'saidaP': { const sub = o && o.etapa === 'Em conferência' ? (o.ben.sai.find(s => s.estorno && !o.ben.sai.some(y => y.subst === s.id && !y.estorno)) || {}).id : '';
      const liq = prMul(op.cx, prMul(MASSA, op.fat)); const bruto = prSoma([liq, benTara(op.cx, 0, r0)]);
      return MUD(c, x => benSaida(x, op.o, { fluxo: 'Produto', classe: op.classe, cx: op.cx, bruto, subst: sub || '', motivo: 'prop' }, IG)); }
    case 'saidaD': return MUD(c, x => benSaida(x, op.o, { fluxo: 'Descarte', destino: 'Compostagem', kg: op.kg, motivo: 'prop' }, IG));
    case 'estornar': { const v = o ? o.ben.sai.filter(s => !s.estorno) : []; const s = v[op.i % Math.max(1, v.length)];
      return s ? MUD(c, x => benEstornar(x, op.o, s.id, 'Pesagem refeita', '', IG)) : { erro: 'sem saída' }; }
    case 'concluir': return MUD(c, x => benConcluir(x, op.o, IG));
    case 'reabrir': return MUD(c, x => benReabrir(x, op.o, 'prop', IG));
    case 'justificar': return MUD(c, x => benJustificar(x, op.o, 'Perda não identificada', 'prop', AN));
    case 'conferir': return MUD(c, x => benConferir(x, op.o, PA));
    case 'fechar': return MUD(c, x => benFechar(x, op.o, IG));
    case 'nf': return MUD(c, x => { if (op.apto > 0) cenReceber(x, CX, op.lote, op.apto, 'un', 'Packing', '—', op.doc, true, RU);
      if (op.quar > 0) cenReceber(x, CX, op.lote, op.quar, 'un', 'Packing', '—', op.doc, false, RU); });
    case 'laudo': return MUD(c, x => cenLiberarQuarentena(x, op.key, 'LAUDO-PROP', AN));
    case 'devolver': { const it = (c.reqs[op.rid] || { itens: [] }).itens.find(i => i.prod === CX); if (!it || !(it.custodia > 0)) return { erro: 'sem custódia' };
      /* [crítica: no "antes" não há benDevPadrao; o guiado de 0139898 é a custódia inteira (processo_estoque.py 449)] */
      const q = op.q === 'guiado' ? (typeof benDevPadrao === 'function' ? N(benDevPadrao(c, c.ordens[c.reqs[op.rid].os], it)) : it.custodia) : Math.min(op.q, it.custodia);
      return q > 0 ? MUD(c, x => cenDevolver(x, op.rid, CX, q, op.apto, RU)) : { erro: 'nada a devolver' }; }
    case 'seguirRec': { if (!o || o.etapa !== 'A liberar') return { erro: 'fase' }; const im = benImpedimentos(c, o).find(x => x.cx); if (!im || !im.link || !im.link.fontes) return { erro: 'sem falta ou sem fontes (antes)' };
      const k = im.link; for (const f of k.fontes || []) {
        if (f.tipo === 'sobra') for (const p of f.linhas) MUD(c, x => cenDevolver(x, p.rid, CX, p.qtd, true, RU));
        else if (f.tipo === 'nf') MUD(c, x => { const n0 = x.movs.length; cenReceber(x, CX, f.lote, f.qtd, 'un', 'Packing', '—', f.id, true, RU); x.movs[n0].estRec = { id: f.rid }; });
        else if (f.tipo === 'quarentena') MUD(c, x => cenLiberarQuarentena(x, CX + '|' + f.lote, 'LAUDO-PROP', AN)); }
      return { cobre: k.cobre }; } } }
/* ---------- invariantes de transição ---------- */
function passo(c, op) { const a = cenClone(c); const r = exec(c, op) || {}; const V = inv(c), bad = (id, info) => V.push({ id, info });
  if (r.erro && JSON.stringify(c) !== JSON.stringify(a)) bad('I-e7', op);
  if (op.k === 'devolver' && !r.erro) { const ob = a.ordens[a.reqs[op.rid].os];
    if (livreTot(c) - livreTot(a) > sobra(a, ob) + EPS) bad('I-a3', [op, livreTot(c) - livreTot(a), sobra(a, ob)]);
    const tem = (cc, o) => custO(cc, o) + linhas(cc).filter(x => x.o === o).reduce((s, x) => s + own(cc, x), 0);
    if (op.apto && ABERTA.indexOf(ob.etapa) >= 0 && tem(c, c.ordens[ob.id]) + EPS < Math.min(usoMax(ob), tem(a, ob))) bad('I-a3', [op, 'perdeu caixa em uso']); }
  const alvo = op.rid ? (a.reqs[op.rid] || {}).os : op.o;
  if (!r.erro && ['nf', 'laudo', 'seguirRec'].indexOf(op.k) < 0) linhas(a).filter(x => x.r.os !== alvo).forEach(x => { const y = linhas(c).find(z => z.r.id === x.r.id);
    if (!y || y.it.custodia !== x.it.custodia || y.it.consumido !== x.it.consumido || y.it.solicitado !== x.it.solicitado || N(y.it.dispensado) !== N(x.it.dispensado) || Math.abs(own(c, y) - own(a, x)) > EPS) bad('I-e8', [op, x.r.id]); });
  if (op.k === 'liberar' && a.ordens[op.o] && a.ordens[op.o].etapa === 'A liberar') { const tot = (a.ordens[op.o].ins[0] || {}).tot || 0;
    if (!benImpedimentos(a, a.ordens[op.o]).length && r.erro) bad('I-b2', [op, r.erro]);
    if (r.erro && lotesCx(c).some(l => l.reservado !== (a.lotes[CX + '|' + l.lote] || {}).reservado)) bad('I-b2', [op, 'reserva órfã']);
    if (!r.erro) { const ls = benLinhas(c, c.ordens[op.o]); const lt = ls.map(x => x.it.lote);
      if (ls.reduce((s, x) => s + x.it.solicitado, 0) !== tot || new Set(lt).size !== lt.length) bad('I-b2', [op, ls.map(x => [x.rid, x.it.lote, x.it.solicitado])]); } }
  if (op.k === 'seguirRec' && r.cobre && benImpedimentos(c, c.ordens[op.o]).some(x => x.cx)) bad('I-f1', [op, 'cobre e não libera']);
  /* [crítica: I-b3 — o complemento aceito se e só se há livre total, na fase que permite] */
  if (op.k === 'pedir' && a.ordens[op.o] && ['Liberadas', 'Em execução'].indexOf(a.ordens[op.o].etapa) >= 0 && !a.ordens[op.o].ben.conc && !!r.erro !== (livreTot(a) < op.n)) bad('I-b3', [op, livreTot(a), r.erro]);
  return { r, V }; }
/* ---------- gerador: só comandos plausíveis no estado, com uma fração inválida de propósito ---------- */
function escolher(c, R) { const n = (a, b) => a + Math.floor(R() * (b - a + 1)), pick = a => a[Math.floor(R() * a.length)], ops = [];
  benLotesAptos(c).slice(0, 3).forEach(L => ops.push({ k: 'criar', lote: L.id, cx: R() < 0.7 ? undefined : n(1, 2500) }));
  benOrdens(c).forEach(o => { const id = o.id;
    if (o.etapa === 'A liberar') ops.push({ k: 'liberar', o: id }, { k: 'seguirRec', o: id }, { k: 'cancelar', o: id });
    if (o.etapa === 'Liberadas') ops.push({ k: 'iniciar', o: id });
    if (ABERTA.indexOf(o.etapa) >= 0) ops.push({ k: 'pedir', o: id, n: n(1, 900) });
    if (['Em execução', 'Em conferência'].indexOf(o.etapa) >= 0) ops.push({ k: 'saidaP', o: id, cx: n(1, 1200), classe: pick(['A', 'B']), fat: pick(['1', '0.97', '1.02']) },
      { k: 'saidaD', o: id, kg: n(10, 3000) }, { k: 'estornar', o: id, i: n(0, 9) });
    if (o.etapa === 'Em execução') ops.push({ k: 'concluir', o: id });
    if (o.etapa === 'Em conferência') ops.push({ k: 'reabrir', o: id }, { k: 'justificar', o: id }, { k: 'conferir', o: id }, { k: 'fechar', o: id }); });
  linhas(c).forEach(x => { ops.push({ k: 'entregar', rid: x.r.id, q: R() < 0.6 ? 'pend' : n(1, 1500) });
    if (x.it.custodia > 0) ops.push({ k: 'devolver', rid: x.r.id, q: R() < 0.5 ? 'guiado' : n(1, Math.ceil(x.it.custodia)), apto: R() < 0.85 }); });
  ops.push({ k: 'nf', lote: pick(['CX26-02', 'QA-CX-02', 'QA-CX-03']), doc: 'NF-P' + n(1, 99), apto: n(0, 1300), quar: R() < 0.3 ? n(1, 200) : 0 });
  lotesCx(c).filter(l => l.quarentena > 0).forEach(l => ops.push({ k: 'laudo', key: CX + '|' + l.lote }));
  return pick(ops); }
/* ---------- execução, reprodução e encolhimento ---------- */
/* [crítica: a semente também é conferida (passo −1); cada invariante é registrado na 1ª vez que aparece e a sequência SEGUE (no "antes",
   parar no 1º esconde I-a4 e I-e4 atrás do I-d2, executado em crit/ben_prop_shim2.js); o encolhimento pode tirar inclusive o último passo] */
const V0 = inv(cenClone(CEN0)); const VISTOS = {}, falhas = [];
V0.forEach(v => { VISTOS[v.id] = 1; falhas.push({ seed: 0, passo: -1, inv: v.id, info: v.info, trilha: [] }); });
function rodar(seed) { const R = rng(seed), c = cenClone(CEN0), t = [], out = [];
  for (let i = 0; i < STEPS; i++) { const op = escolher(c, R); t.push(op); const { V } = passo(c, op);
    V.forEach(v => { if (!VISTOS[v.id]) { VISTOS[v.id] = 1; out.push({ seed, passo: i, V: [v], trilha: t.slice() }); } }); } return out; }
function reproduz(t, alvo) { const c = cenClone(CEN0); for (const op of t) { const { V } = passo(c, op); if (V.some(x => x.id === alvo)) return true; } return false; }
function encolher(f) { const alvo = f.V[0].id; let t = f.trilha.slice();
  for (let j = t.length - 1; j >= 0; j--) { const u = t.slice(0, j).concat(t.slice(j + 1)); if (reproduz(u, alvo)) t = u; } return t; }
SEEDS.forEach(s0 => { for (let k = 0; k < RUNS; k++) rodar(s0 * 1000 + k).forEach(f => falhas.push({ seed: f.seed, passo: f.passo, inv: f.V[0].id, info: f.V[0].info, trilha: encolher(f) })); });
console.log(JSON.stringify({ ok: !falhas.length, runs: SEEDS.length * RUNS, steps: STEPS, invariantes: Object.keys(VISTOS), falhas }));
```

```python
# ben_prop_test.py — mesmo padrão do ben_unit_test.py
import os, sys, json; os.environ.setdefault('SAFRION_DADOS', 'sintetico'); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ben_unit_test as T
r = T.node(T.motor() + open(os.path.join(T.HERE, 'ben_prop.js'), encoding='utf-8').read(), 'ben_prop_all.js')
out = json.loads(r.stdout.strip().splitlines()[-1]) if r.returncode == 0 and r.stdout.strip() else {'ok': False, 'falhas': [{'inv': 'motor', 'info': r.stderr[-800:]}]}
for f in out.get('falhas', []): print('FALHA', f['inv'], 'semente', f.get('seed'), 'passo', f.get('passo'), json.dumps(f.get('info'), ensure_ascii=False)[:400], '\n  trilha mínima:', json.dumps(f.get('trilha'), ensure_ascii=False))
print('RESULTADO:', 'OK' if out['ok'] else 'FALHOU', out.get('runs'), 'sequências ×', out.get('steps'), 'passos'); sys.exit(0 if out['ok'] else 1)
```

**Aceite do harness:**
1. Em 0139898 o harness **reprova** e mostra uma trilha mínima para cada um destes invariantes: I-a1 (conferência), I-d2 e I-e4 (fantasma e reserva), I-b1 (vários lotes), I-a4 (reserva depois do Fechar) e I-a3 (devolução da caixa em uso). Se algum desses não aparecer, o gerador não alcança o caso: aumentar o peso do comando antes de seguir. [crítica: com as correções do código acima, os seis já aparecem em 360 × 35 (executado). Acrescentar ao aceite: (a) a saída lista `invariantes` vistos, e o `ben_prop_test.py` reprova o "antes" se faltar algum dos seis; (b) o I-e7 não conta, porque não reprova por construção]
2. Depois de C1 e C2, OK nas três sementes. As trilhas mínimas do "antes" entram como casos fixos em `ben_unit.js` (U53). O `ben_prop_test.py` entra na bateria do BEN.
3. [crítica: o gerador não tem contagem, ajuste, `benRetirar`, `benConfirmarCorrecao` nem comandos de O.S. sobre outros itens. Os invariantes valem **para esse conjunto**, e isso fica escrito na saída. O ajuste sai de propósito (I-e4, riscos residuais). A O.S. fica coberta pelos testes de O.S. da bateria]

## 7. Decisões a registrar e perguntas ao Codex (não ao proprietário)

**Decisões:**
- **BEN-D33:** a sobra é a custódia acima do teto do kg aberto em toda fase aberta (inclui conferência, com ou sem conferência dada). A devolução se divide em sobra (dispensada, livre) e caixa em uso (volta reservada à mesma linha). O campo `dispensado` entra no "a entregar". [crítica: acrescentar (a) a falta na execução é o planejado ainda não consumido, limitado pelo teto, menos o que a ordem tem: `faltaExec`, sem reaplicar `frac_vend`; (b) em conferência dentro da faixa, o pré-preenchido é a custódia inteira; (c) a trava física do `cenEntregar` fica]
- **BEN-D34:** livre total dos lotes elegíveis; linha por lote na liberação; tudo ou nada; fontes de recuperação combinadas.
- **BEN-D35:** o Fechar baixa a reserva não entregue.
- **BEN-D36:** a repetição de tecla não age; foco no estado depois do comando; rascunho protegido; aviso fora do rodapé; rótulos sem verbo repetido.

**Perguntas ao Codex, com caminho e versão:**
- **P1:** aceitar que, no roteiro do BEN-REV-20261009-03, as 540 caixas devolvidas em execução depois do estorno voltem reservadas à OB (impressão do harness `[540, 540]`)?
- **P2:** no passo "Fechar processo", o pré-preenchido é a custódia inteira, e o que passa da sobra fica reservado até o Fechar baixar. Confirma? [crítica: ampliar a pergunta. Vale também em conferência com `kgAberto ≤ faixa` (ruído de pesagem), para o Rui não ter de voltar por 1 ou 2 caixas (U47e, crit/p4.js)]
- **P3:** na O.S., a devolução de sobra no meio da execução continua reabrindo o "a entregar" (PRD 42.1), agora sem consumir reserva alheia. Estender o `dispensado` à O.S. é mudança de contrato da O.S., do app e do SUP, para outra fatia.
- **P4** [crítica: nova]: a revalidação do atalho recusa quando muda a sobra, a fase ou a custódia da linha; a `ver` da OB vai só como contexto. Revalidar pela `ver` recusaria a cada saída de Produto, que não muda a sobra. Aceita? Se o Codex mantiver a `ver` como trava, a mensagem diz o que mudou.
- **P5** [crítica: nova]: aceitar a `faltaExec` pelo planejado (Σsol − Σcons, limitada pelo teto) no lugar da `necRota`? Com a `necRota`, o roteiro do proprietário mostraria "Faltam 50" e depois "Faltam 58" com 610 kg a descartar, e a cadeia K2 mostraria "Faltam 55" (crit/p1.js).

Nada aqui gera custo nem depende da fazenda: não há pergunta ao proprietário.

## 8. Verificação (comandos)

Em `tools/prototipo/v37/gen37`, com `SAFRION_DADOS=sintetico`. O navegador roda sempre com `env CHROME_BIN=/tmp/cloudchrome/chrome flock /tmp/cdpI.lock env CDP_GL=1 SAFRION_DADOS=sintetico timeout 900 python3 <teste>`.

1. **Antes** (0139898 com os testes novos):
   - `python3 ben_unit_test.py` reprova em U47 a U52;
   - `python3 ben_prop_test.py` reprova com as trilhas mínimas da seção 6;
   - `ben_fluxo_test.py sobra conferencia multilote teclado rodape` reprova nos passos citados.
   - Guardar os brutos em `docs/integracao/BEN/rod3/antes/`.
2. **Depois:**
   - `ben_unit_test.py` OK;
   - `ben_prop_test.py` OK nas 3 sementes;
   - `ben_mutantes.py` OK, com os mortos novos M77 a M88: sobra zero em conferência; piso; inclui a própria ordem; devolução sem divisão; `dispensado` ignorado; livre de um lote; liberação sem dividir; Fechar sem baixar a reserva; entrega com `Math.max` na reserva agregada; pré-preenchido com a custódia; repetição de tecla aceita; Esc descartando. [crítica: acrescentar M89, `faltaExec` pela `necRota` (morre no U54); M90, `cenEntregar` sem a trava física (morre num U55 com a fixture de crit/p2.js: ajuste aprovado depois da reserva → entrega recusada e físico ≥ 0); M91, gancho que falha aberto sem o ben.js; M92, revalidação só pela `ver` (morre no controle "saída de Produto na outra aba → aceita")]
   - `python3 ../../../../docs/integracao/BEN/rev03/run_harness.py`: OK 4/4, com `[540, 540]` registrado.
3. **Navegador:** `ben_fluxo_test.py` em todos os 15 modos de hoje mais `sobra`, `sobra390`, `multilote`, `multilote390`, `conferencia` e `rodape`. O roteiro e o roteiro390 continuam com 29 e 31 toques e 8 campos.
4. **Áreas tocadas:** tabelas_ben_test, producao_fluxo_test, tabelas_est_test, est_cenario_test, esttest, est_fix1_test, est_fix2_test, ap_unico_test, app_cenario_test, links_ocultos_test e cada_cd04_test.
   - Por causa do `cenario.js`, também: os_cenario_test e consumo_divergente_test (linha de base 19/20 e 20/21, iguais a 2678481), inicio_entrega_unit, quantidade_test e aprova_quem_decide_unit.
   - [crítica: a tabela da seção 5 cita como chamadores do `cenEntregar` testes que esta lista não roda. Acrescentar o os_v39_bloq_test (entrega e devolução na OS-0430), o app_entrega_parcial_test, o app_os0424_test, o app_saldo_zero_test, o app_mb02det_test e o ap_unico_unit (pelo ap_unico_test). Os scripts ostela.py, osfix.py e est_repro.py são demonstração e ficam de fora, com registro. O producao_fluxo_test e a varredura do PROD e das Cargas confirmam que o `pp_closeHide` não muda as outras telas]
   - Por fim: varredura.py e ../ferramentas/acoes_duplicadas.py.
5. Atualizar o `DECISOES.md`, o pacote `rod3/` e o `docs/STATUS.md`; rodar o `prep_site.sh` e fazer o push na `claude/prototipo-v44`.

## 9. Crítica adversarial · lista de mudanças [crítica]

Os scripts estão em `ben-rod3/crit/`. "Executado" quer dizer que rodaram no motor de 0139898 (`ben_unit_test.motor()` + node), numa cópia separada do código. "Especificado" quer dizer leitura do código.

| # | Sev. | Onde no desenho | Problema | Correção | Evidência |
|---|---|---|---|---|---|
| C-1 | S2 | §2 `faltaExec`/`necRota`, I-d2, I-f4, S2-2 item 6 | `necRota` reaplica `frac_vend` ao kg que sobra e dá falso "Faltam N" no caminho feliz, e o "Pedir mais caixas" pré-preenchido reservaria caixas de que outra ordem precisa | `faltaExec = max(0, min(usoMax, Σsol − Σcons) − Σcust − Σpend)`. A `necRota` sai; teste novo U54; mutante M89; pergunta P5 | Executado, p1.js: roteiro R7 dá 50 e 58 (610 kg a descartar); cadeia K2 dá 55. Pela fórmula nova dá 0 em todos; no limite adicional dá 139 |
| C-2 | S2 | I-d3, S2-2 item 3 | A regra `q ≤ own + cenDisp` substituindo a trava física deixa o físico negativo depois de um ajuste aprovado com reserva por cima | Manter `q ≤ fis − quar`; aviso "Reserva sem físico"; o I-e4 escreve a exceção do ajuste; U55 e mutante M90 | Executado, p2.js: AJ-71 aprovado → fís 1.100 e res 1.169; `own + cenDisp = 1.169` → físico −69 sem a trava; hoje a entrega é recusada |
| C-3 | S3 | I-f2, I-f4, recusa do `benSaida` | Em conferência, mandar "Pedir mais caixas" ou "Rui entrega no balcão" leva a comandos que o sistema recusa | A ação da fase é "Reabrir a execução"; verificação no harness; variante do U52 em conferência | Executado, p4.js: `benComplementar` e `cenEntregar` recusam em Em conferência |
| C-4 | S3 | §2 `devPadrao`, I-c2, P2 | Conferência com diferença dentro da faixa: o formulário vem com custódia − 1, e o Fechar fica recusado até uma 2ª devolução | Custódia inteira quando `kgAberto ≤ faixa`; a parte acima da sobra volta reservada e o Fechar baixa; U47e | Executado, p4.js: dif 5 kg, faixa 12,3 kg, custódia 9, pré-preenchido 8, resta 1 |
| C-5 | S3 | U48b | O teste descrito não acontece com o próprio desenho: a OB-0112 continua impedida | Receber mais 111 cx (nota QA) antes de liberar | Executado, p4.js: livre total 631 → 770 < 881 |
| C-6 | S3 | §6, aceite 1 | O harness como escrito reprova tudo no passo 0 por I-f1 (API nova ausente), quebra com `benDevPadrao` inexistente e, parando na 1ª violação com teto de 5, não mostra os seis invariantes | Detecção da API; 1ª ocorrência por invariante sem parar a sequência; `inv(CEN0)`; encolhimento até o último passo; I-b3, I-f4 e I-e9 no oráculo | Executado: run5 (esboço original) dá 5× I-f1 no passo 0; run8 (bloco corrigido, 27,6 s) dá I-d2, I-a3, I-b1, I-a4, I-e4, I-b3 e I-a1 com trilhas de 1 a 7 passos |
| C-7 | S3 | §2 `devLinha`, I-f1 `linhas` | A sobra é da ordem e o formulário é da linha: com duas linhas, o texto diz 150 e o formulário traz 100 | `sobraLinhas(o)` com Σ = sobra; texto por linha; U48e | Especificado (a conta segue da definição) |
| C-8 | S3 | Regra de divisão, I-c3 | A mensagem "devolvidos ao disponível" fica falsa quando parte volta reservada; o `econta` não mostra o termo novo | Mensagem com as duas partes; `econta` com a sobra devolvida; "dispensado" nunca aparece na tela (o nome já é da O.S.) | Especificado (cenario.js 115, processo_estoque.py 218; `osc_dispensar` na O.S.) |
| C-9 | S3 | S2-2 item 3, C3 | Tirar o `estEntregar` inteiro perderia o `it0.confirmado = false` da nova entrega de O.S. | Sai só a restauração da reserva | Especificado (processo_estoque.py 290-293; inicio_entrega_unit "R7 residual") |
| C-10 | S3 | Gancho no `cenDevolver` | O `typeof` deixa uma linha BEN ser devolvida sem a divisão se o ben.js faltar | Falha fechada em linha BEN; mutante M91 | Especificado |
| C-11 | S4 | I-c5 | A `ver` recusa a cada saída de Produto, que não muda a sobra | Recusar só quando muda a sobra, a fase ou a custódia da linha; pergunta P4; mutante M92 | Especificado (`benToca` em toda saída; −cx e −cx no teto) |
| C-12 | S4 | I-e7 | No motor é tautológico (`MUD` e `benMudar` trabalham numa cópia) | Não conta como cobertura; o risco real fica com o I-b2 e o I-e9 | Especificado |
| C-13 | S4 | I-e9 (novo) | Faltavam `Σsol = ins.tot` e `pend` bruto ≥ 0 | Acrescentados ao oráculo | Especificado |
| C-14 | S4 | I-g1, I-h1 | O bloqueio do Espaço em campo de texto impede digitar; a escolha por toque disparava "rascunho"; faltava o clique no fundo | Só em botão; só campo digitado; o fundo entra na lista; reabrir o rascunho preenchido fica vetado (último valor) | Especificado |
| C-15 | S4 | S4 Esc e rótulos | O Esc e os rótulos mexiam no `pp_key` e no template comum da Produção | `bnSujo` envolve o `v.pp_close` do BEN; `pp_closeHide` opcional; producao_fluxo_test na bateria | Especificado (producao.py 88, 166-167; processo_beneficiamento.py 250) |
| C-16 | S4 | §5 "Não muda" | "Recibo em todo comando" é falso hoje | Texto corrigido para "onde já existe; nos outros, recusa pela fase" | Especificado (ben.js 305-499) |
| C-17 | S4 | §5, §8 | Faltavam o K3 e o U46e na lista de textos que mudam, e os testes de app e O.S. que chamam `cenEntregar` na bateria | Listas completadas | Especificado (ben_fluxo_test.py 664, ben_unit.js 667) |
| C-18 | S4 | §0 Base | O HEAD da branch é a5ab722 | Registrar; o código do BEN é igual (o diff só toca docs/VISOES) | Executado: `git diff --stat 0139898 a5ab722` |

**Sem mudança (contraexemplo tentado, invariante resistiu):**
- I-a3 e I-d2 sob a regra de divisão. Prova algébrica: depois da devolução, `cust + own` cai exatamente `min(q, sobra)`, que é ≤ `cust − usoMax`. Vale para linha única e para duas linhas.
- I-e4 nas transições de liberar, entregar, devolver apta ou avariada, consumir, estornar, complementar e fechar.
- Base da semente do `cenResTot`: as REQs de O.S. da semente que não estão Reservadas seguem com reserva própria 0 (conferido na semente: só REQ-039, 040 e 021 têm reserva no lote, e são Reservadas). DOM e conciliação (`cenConcPrevia`) não mudam.
- O PCM usa `c.itens` e não é afetado.
- Cancelar em A liberar com custódia não é alcançável, porque a reserva e a linha nascem na liberação.
- Duas ordens no mesmo lote: a devolução reservada de uma não muda o livre da outra (I-e8).
- Mutantes A2 e A8 equivalentes no código atual: conferido na leitura de ben.js 94-95.
