# Robô v5.1 · linha de base e revisão (EX-51)

Autor do robô: Codex (PR #112, HEAD `96a99f68cec0f5dc1b56d0468e1476fafa09785a`, base `259c13bc`). Revisor e executor: Claude. Contrato de medição: PR #47, comentários 6241203221, 6241229682, 6241254289 e 6241404422.

Medida **executada** em 17/10/2026, das 21:34:51 às 21:59:53 UTC, mais casos dirigidos e contraprovas até 22:12 UTC. Dados sintéticos do protótipo, sem segredo. Esta pasta é a nova linha de base imutável do v5.1: não sobrescrever.

## Candidata medida

- `_render` de `/tmp/claude-0/int90/tools/prototipo/v37/gen37/_render`, copiado antes da medida para uma pasta própria, somente leitura.
- **É a mesma candidata da base v5.** São 181 arquivos iguais byte a byte, com o mesmo sha256 do conjunto: `39b88342b9aa985f011dd9fabc9c5482d7a03a0c983b23fb740e8845158dd038`. O `v3.sha256` é idêntico ao de `robo-v5-base`.
- Durante a sessão, a árvore `int90` andou de `0ec3a342` para `31680412`, que integra o PR #111. O `_render` não foi remontado, e o hash acima confirma isso.
- `ocultas.json`, `screens.json` e `navegacao.json` são idênticos aos da base v5: 102 páginas no robô e 94 na conta.

**Comando** (o do LEIAME do v5.1):

```sh
python3 -I robo-v51/rodar.py --render <cópia do _render> --trabalho <pasta nova> --entrega robo-v51-base
```

**Tempos e ambiente:**
- Robô: 11,8 min. 2ª passada: 8,1 min. Títulos: 2,7 min. `escopo28`: 2,3 min. Total: 25,0 min.
- Chromium 141.0.7390.37, headless.
- Havia 1 Chrome principal alheio antes de abrir. O script encerrou só os próprios PIDs.
- 0 diálogos JS, 0 telas com erro (`.v5err.json`) e 0 passagens com erro.

## Resultados (v5.1, modo isolado)

| Medida | **v5.1 · nova base** | Base v5 (não comparável) |
|---|---|---|
| IDs clicáveis no detalhe | **39/80 (49 %)** | 39/85 |
| Cadastros clicáveis | 6/84 (7 %) | 6/84 |
| Passagens com alvo capturado na origem que chegam | **34/68 (50 %)** | 85/153 |
| · só 1ª passada | 34/68 (a 2ª passada estrita não resgatou nenhuma) | 82/153 |
| Volta à origem (link no destino) | **8/68 (12 %)** | 22/153 |
| Voltar do navegador reabre o detalhe | **9/107 (8 %)** | 10/107 |
| Inconclusivas (sem alvo único na origem) | **165/233 navegações (70,8 %)**: 85 levam registro e 80 são navegação de tela | — |
| Erros (não achou, não reabriu, erro) | 0 | 0 |
| Empilhado (`data-g2pilha`) | **0**: a candidata não tem painel empilhado (0 páginas com `data-g2pilha` ou "Abrir na tela de") | — |
| `escopo28`: Fazenda e Safra herdadas | **0/28**: não herdam IN-04, OS, EST, COLH, AG-01, AG-02, IR-01, CARGA e PROD; 19 telas sem seletor | 0/28, igual tela a tela |
| Isolamento por marcas | 3 trabalhadores em 3 origens (portas 33811, 36409 e 42783); cada um viu só a própria marca (`isolamento-v51.json`) | — |

Contexto, igual ao da base v5:
- 94 telas, 190 detalhes e 247 passagens.
- Das passagens, 233 navegam, 11 abrem no lugar e 3 ficam sem efeito.
- 32 de 190 detalhes têm Próximo passo, e 13 dizem quem age.

Origem do alvo nas 68 passagens:
- 45 vêm do `href` e 23 do texto do link.
- Nenhuma vem de `data-ref`, que a candidata ainda não tem.

Todas as 34 chegadas foram provadas pelo título do painel, com ID exato. Nenhuma veio da seleção nem da 2ª passada.

**Taxa geral:** 50 % das passagens com alvo, abaixo da meta de 95 %. É a linha de base antes da F1, não um defeito novo.

## Percursos críticos (100 % exigido; inconclusivo ou ausente bloqueia)

A amostra do robô não cobre esses percursos. Ela abre até 3 registros e até 9 passagens por tela, e na O.S. os 3 registros amostrados (OS-0415, OS-0430 e OS-0599) não têm nenhum link. Por isso o revisor rodou casos dirigidos (`revisor/casos_criticos.py`):
- todos os registros das telas de origem e os registros críticos abertos pelo endereço;
- para cada passagem crítica, a mesma `passage()` do v5.1.

Saídas em `revisor/saidas/casos-criticos*.json`.

| Percurso | O que existe na candidata | Resultado v5.1 | Veredito |
|---|---|---|---|
| O.S. → EST · entregar | OS-0424 e OS-0425: "Entregar no Estoque ›" → `EST.dc.html` | 2/2 inconclusivas: o link não leva o registro | **bloqueia** |
| O.S. → EST · devolver | OS-0417: "Receber devolução no Estoque ›" → `EST.dc.html` | 1/1 inconclusiva | **bloqueia** |
| O.S. → EST · saldo | OS-0418: "Ver saldos no Estoque ›" → `EST.dc.html` | 1/1 inconclusiva | **bloqueia** |
| (O.S. → EST · retirar, informativo) | OS-0420 (na lista e pelo endereço) e OS-0421 | 3/3 inconclusivas | — |
| O.S. → receituário (VIS/RA) | Nenhum detalhe das 15 O.S. da lista tem link para VIS, RA ou REC. As O.S. dos receituários, OS-0504 e OS-0508, abertas pelo endereço, não têm link nenhum | ausente | **bloqueia** |
| Receituário → O.S. | AG-01, da VIS-051 e da VIS-052 e da tela: 6 casos para OS-0504 e OS-0508. AG-04 → OS-0421 e OS-0418: 2 casos. AG-04det → OS-0420: 1 caso | **9/9 chegam**, 0 alvo errado. Voltar reabre a VIS em 4/4 a partir do detalhe; volta à origem 0/9 | cumpre para VIS/REC |
| RA ↔ O.S. | RA-0140 e RA-0141 existem só nos dados das páginas. Não há link com RA em nenhum detalhe percorrido, e na amostra do robô o RA também não aparece como texto | ausente | **bloqueia** |
| Aprovações (IN-02) → O.S. | As 4 decisões da caixa são de inventário, política de estoque, orçamento e acesso. Os links vão a SU-09, SU-02, GE-02det e CF-01, nenhum a uma O.S. | ausente | **bloqueia** |
| O.S. impedida → OM | OS-0431, impedida por máquina segundo o PAGR: "Acompanhar OM-0233 ›" → `MA#om=OM-0233` chega 2/2 (pela lista e pelo endereço). OS-0420, impedida e ligada à OM-0233, e OS-0507, impedida, não têm link para a OM | 2 chegam e 2 O.S. ficam sem caminho | **bloqueia** |
| OM → O.S. impedida | As 16 OM da visão de ordens e as OM-0233, 0228 e 0219 abertas pelo endereço não têm link para uma O.S. O botão do achado SM-0147 cita "OS-0420" no texto, mas abre o achado na própria Manutenção | ausente | **bloqueia** |

Nos JSON, a classificação automática por texto e destino rotula de outro jeito dois casos que a tabela acima reclassifica:
- a OS-0431 sai como `OS→OM`, porque o detalhe não traz a palavra "impedida";
- o achado SM-0147 sai como `OM→OS`, mas é falso, porque o link abre o achado (`mesma tela`, sem alvo).

**Veredito da base:**
- Nenhum percurso crítico está completo.
- Nenhum caso crítico chegou num alvo errado.
- Os bloqueios são de produto: link sem registro, ou nenhum link. É o que a F1 deve resolver com `data-ref`. Não são defeito da régua.

## Comparação caso a caso com a base v5

Script: `revisor/comparar_casos.py`. Saída: `revisor/saidas/comparacao-casos.json`.
- **Chave:** tela, tipo, texto e href.
- **Critérios:** a chegada é recalculada com o critério de cada resumo, copiado sem mudança. O recálculo do v5 reproduz os 85/153 da base.
- **Passagens:** as 247 da v5.1 são exatamente as 247 da v5, com a mesma chave.
- **Comportamento das páginas:** o resultado (`navega`, no lugar ou nada) e o destino são iguais nas 247. Não houve variação entre as execuções.
- **Volta à origem:** o critério não mudou. Nos 153 casos da v5, a v5.1 dá os mesmos 22. A queda para 8/68 vem só do denominador.

| Diferença | Casos | Razão |
|---|---|---|
| Iguais | 145 | — |
| Passam a inconclusivas | 85 | A origem não tem alvo único: o link não leva ID, leva vários, ou o hash e o texto divergem. Na v5, 51 contavam como "não chegou" e 34 como "chegou", todas pela 2ª passada frouxa da v5 (diálogo qualquer ou texto da página). Em 8 desses casos a v5 inferia o alvo, do hash do destino ou do 1º ID do texto: PAGR `#painel=` com 2 ou 3 O.S. (4 casos), CD-03 com "OS-0420 e OS-0431", GE-01 com "CT-198 e PV-028" e GE-03 com "REQ-035 · OS-0421" e "REQ-036 · OS-0420" |
| Chegada recusada com o mesmo alvo | 17 | A v5 aceitava pela 2ª passada frouxa. **11 são páginas do próprio registro com o ID exato no h1** (achado A3): IR-01 → IR-03det (4), AG-04 → AG-04det (2), AG-04 → AG-03det, AG-07 → AG-04det, AG-07 → CA-01x-os0420, CA-03det → CA-01x-os0420 e GE-01 → CO-06det. **6 são recusas corretas** por falta de título ou seleção com o ID: AG-01 → AG-01det#VIS (3) e MB-01/02/03 → MB-05#OS-0424 (3) |
| Voltar | 1, dentro das 85 | PAGR → MB-07#lg24. A v5 contava reaberto porque a volta caiu em COLH#lg24 com diálogo de mesmo título; a v5.1 exige a mesma tela de origem. É o caso que o LEIAME da base pedia conferir |
| IDs | 5 | Saíram 4 CMD e 1 DEC do denominador (85 → 80). Nenhum RA nos detalhes amostrados |

**Sensibilidade, não oficial:** se o h1 da página do registro com ID exato contasse como título do painel, a chegada iria a 45/68 (66 %).

## Achados da revisão do código (`robo-v51` @ `96a99f68`)

Severidade pelo efeito na régua:
- **S2:** pode aprovar ou reprovar a F1 pelo motivo errado, ou o portão do contrato não existe;
- **S3:** distorce a medida, mas há alternativa nos brutos;
- **S4:** menor.

| # | Sev. | Onde | Achado | Prova |
|---|---|---|---|---|
| A1 | **S2** | `resumo.py:65`; `robot.html:148,155` | **Os percursos críticos não são calculados nem bloqueiam.** O aceite é a cadeia fixa "PENDENTE"; não há inventário dos percursos nem a regra "inconclusivo ou ausente bloqueia", e a meta de ≥ 95 % não é calculada. A amostra (3 registros e 9 passagens por tela) não alcança a O.S.: 0 passagens medidas na O.S. Sem casos dirigidos, a régua não decide o aceite da F1. | Executado: OS.v5.json com 0 passagens; os casos dirigidos acima |
| A2 | **S2** | `robot.html:33-34` | **`decodeURIComponent` roda antes de separar o fragmento.** Um `%23` na query vira `#`, e o alvo passa a ser o ID da ORIGEM. O desenho da F1 põe `?de=<arq>%23<hash>` nos links (`desenho-F1-motor.md:210`). Não afeta esta base (0 hrefs com `%23`), mas afeta a F1 em todo link sem `data-ref` que leve `de=`. Correção: separar no `#` do href cru e decodificar só o fragmento. | Executado (`revisor/contraprova_alvo.cjs`): `EST.dc.html?de=OS.dc.html%23OS-0502#ent=REQ-039` → `OS-0502`, quando o esperado era REQ-039; `MA.dc.html?de=OS.dc.html%23OS-0420#vis=ordens` → `OS-0420`, quando o esperado era inconclusiva |
| A3 | S3 | `robot.html:44-49`; `rodar.py:503` | **A página do próprio registro não conta como título do painel.** Só contam o título do diálogo e a seleção, então 11 das 34 recusas são falsos negativos de método. Correção sugerida: sem diálogo aberto, aceitar o h1 com o ID exato; texto do corpo continua fora. | Executado: 11 casos com o ID exato no h1 do endereço; no IR-03det o h1 acompanha o hash |
| A4 | S3 | `resumo.py:44-46, 62` | **"Inconclusiva" mistura navegação de tela com passagem de registro.** São 165/233, mas 80 dessas navegações nunca tiveram registro (hubs, "Ver demanda gerada" etc.), o que superestima a lacuna. A lista `passagens`/`piores` marca as inconclusivas do detalhe como `chegou: false` e `prob`, o que contraria a separação. | Executado: as 165 se dividem em 85 + 80 |
| A5 | S3 | `rodar.py:454, 503`; `resumo_test.py:11` | **2ª passada: o título do diálogo cai para o texto do corpo.** Sem cabeçalho, `dlg` vira os primeiros 60 caracteres do corpo do painel, e `chegouEstrito` aceita o alvo citado ali. O teste do PR grava o `leva-check` sem `chegouEstrito` e não exercita essa expressão. Nesta base não houve efeito (0 resgates). | Executado (`revisor/contraprovas_navegador.py`, C): diálogo sem título cujo corpo cita OS-0502 dá `chegouEstrito: true`; com título OS-0503, dá `false` |
| A6 | S3 | `rodar.py:479-480`; `resumo.py:38` | **A 2ª passada abre o `href` do link, não o destino do clique.** O resgate não compara com `para`, então um clique desviado por JS pode ser "resgatado" pelo endereço certo. Sugestão: só resgatar quando o endereço aberto é o destino do clique. 0 resgates nesta base. | Leitura do código |
| A7 | S3 | `robot.html:115-123`; `resumo.py:62` | **Empilhado.** Só é medido quando a URL não muda e o `data-g2pilha` está no próprio elemento de diálogo. Se a F1 gravar o hash ao abrir a pilha (`g2hashReg`), o caso vira "mesma tela" e a pilha não é medida. O resumo conta só a abertura do resumo (`empilhadosCorretos`), não a chegada na dona nem o Voltar à pilha. | Executado com páginas sintéticas (B): positivo com pilha e dona `abriu: true`; negativo (pilha OS-0503 para alvo OS-0502, com o corpo da dona citando OS-0502) com pilha e dona `abriu: false`; resumo com `empilhados: 2` e `empilhadosCorretos: 1` |
| A8 | S3 | `resumo.py:9-10`; `robot.html:177` | **Telas com erro somem do resumo.** O resumo não lê `*.v5err.json`. Nesta base houve 0 erros. | Leitura do código |
| A9 | S4 | `robot.html:132-134` | **`voltaOrigem` mantém `includes` parcial**, por ID e por um prefixo de 18 caracteres do h1. É o mesmo critério do v5 (22 = 22 nos mesmos casos). | Leitura do código |
| A10 | S4 | `robot.html:39-43` | **`exactId` aceita casos frouxos:** `OS-0502/2`, e título com dois IDs ("PC-0012 · da OS-0502" para o alvo OS-0502). O alvo também pode vir de um parâmetro de contexto: `#dev=…&para=OS-0502` dá OS-0502, que é a origem. | Executado (`contraprova_alvo.cjs`) |
| A11 | S4 | `resumo.py:63` | **`escopo.herda` fixo em 0.** O resumo não lê `escopo-28.json`. Hoje coincide (0/28). | Leitura do código |

**O que cumpre o contrato:**
- **Alvo capturado antes do clique e nunca do destino:** `robot.html:111`, antes de `:113`, com `want = expected.id` em `:127`.
- **Igualdade exata de ID:** `:39-49`.
- **Sem alvo, inconclusiva separada:** `:137`; `resumo.py:40, 62`.
- **Chegada só por título ou seleção:** sem texto do corpo na 1ª passada; no B, o corpo da dona citando o alvo não passou.
- **Denominador:** RA entra e CMD/EX/DEC saem (`robot.html:23`; `resumo.py:29`).
- **Isolamento:** verificado por marcas (`rodar.py:371-382`), e o modo pacote é recusado.
  - Contraprova A, executada: com um servidor único forçado para dois trabalhadores, o portão reprova com `marks ['ex51-isolation-1','ex51-isolation-0']`.
- **Voltar:** exige a mesma tela (`robot.html:142`).
- **2ª passada sem `alvoNoCorpo`/`tokNoCorpo`** (`rodar.py:503`), salvo o A5.
- **`escopo28`:** igual ao v5 (`rodar.py:552-614`) e executado.

## Testes e contraprovas executados

Saídas em `revisor/saidas/testes.txt` e `contraprovas.json`.
- **Testes do PR:** `node oraculo_test.cjs` → PASS 13; `python3 -I resumo_test.py` → PASS.
- **`revisor/contraprova_alvo.cjs`:** 7 casos sobre as funções reais; 5 DIF documentados em A2 e A10.
- **`revisor/contraprovas_navegador.py`,** com páginas sintéticas em `revisor/sint/`:
  - A: isolamento reprovado com origem compartilhada (PASS);
  - B: empilhado positivo e negativo (PASS no oráculo; Voltar à pilha `false` nos dois, como esperado, porque a página sintética não restaura a pilha);
  - C: confirma o A5.
- **`revisor/casos_criticos.py`** (lista e `--por-endereco`).
  - Usa a `passage()` do robô.
  - Mudanças só no próprio script: o `load()` aceita um hash de visão (`MA#vis=ordens`); no modo por endereço, o `openRow()` devolve o painel que o endereço abriu, com a mesma `expandAll()`.
  - A 1ª execução tinha um erro meu na chave do hash (`MA#vis=ordens` não se aplicou); foi refeita depois da correção. O bruto antigo não foi entregue.

## Parecer: o v5.1 está apto a ser a régua da F1?

**Como linha de base desta candidata, sim.**
- A medida é reprodutível: as 247 passagens e os destinos são idênticos aos da base v5.
- O oráculo é mais estrito, e não achei falso positivo nos brutos.
- O isolamento está provado.

**Como régua de aceite da F1, ainda não.** Antes de medir a F1, o autor precisa de:
1. **A2:** corrigir o decode antes do split (uma linha), porque a F1 introduz `?de=…%23…`;
2. **A1:** levar os casos dirigidos dos percursos críticos para o comando, com bloqueio automático quando houver inconclusivo, ausente ou alvo errado, e calcular a meta de ≥ 95 % (sugestão: incorporar `revisor/casos_criticos.py`);
3. **A3:** aceitar o h1 da página do registro com ID exato;
4. **A5:** tirar o fallback para o corpo na 2ª passada.

A4, A6 e A7 entram na mesma revisão. Com isso a régua mede a F1 sem reprovar por método. Os números desta pasta valem como base v5.1 e não se comparam com a v5 nem com a v108.

## Arquivos

| Arquivo | O que é |
|---|---|
| `resumo.json`, `resumo-isolado-1a-passada.json` | Resumo v5.1, com e sem a 2ª passada (idênticos nesta base) |
| `brutos-isolado/` | 102 `*.v5.json`, `escopo.v5.json` e `leva-check.json` (0,3 MB, sem compressão) |
| `isolamento-v51.json`, `escopo-28.json`, `execucao.json`, `execucao.log`, `robo-isolado.log`, `preparo.json`, `v3.sha256`, `comparacao.json`, `entradas/` | Saídas do `rodar.py` do v5.1 |
| `revisor/casos_criticos.py`, `revisor/saidas/casos-criticos.json`, `casos-criticos-endereco.json`, `criticos*.log` | Casos dirigidos dos percursos críticos |
| `revisor/comparar_casos.py`, `revisor/saidas/comparacao-casos.json` | Comparação caso a caso v5 × v5.1 |
| `revisor/contraprova_alvo.cjs`, `revisor/contraprovas_navegador.py`, `revisor/sint/`, `revisor/saidas/contraprovas.*`, `revisor/saidas/testes.txt` | Contraprovas do revisor e testes do PR |

**Limites:**
- Não foram medidos aqui o teclado, o leitor de tela e as três jornadas de referência.
- Foco, seção e rolagem dependem dos testes T3/T5/T7 da F1.
- Voltar e volta nos percursos críticos são informativos, porque o contrato pede 100 % de chegada.
