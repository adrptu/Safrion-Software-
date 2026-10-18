# Robô v5.1 · rodada 2 da revisão (EX-51)

Autor do robô: Codex (PR #112, HEAD `7c2045d63e84455b2c28b97dcf26d08340b47af3`, que corrige o `96a99f68`). Revisor e executor: Claude. Retorno lido: comentário 6242306459 do PR #112. Base da comparação: a rodada 1 (`../LEIAME.md`, robô @`96a99f68`).

Tudo o que está marcado como executado foi rodado entre 17/10/2026 22:45 e 18/10/2026 00:27 UTC. Dados sintéticos do protótipo, sem segredo. Nada foi publicado no GitHub.

## Candidata e execução

- **Mesmo `_render` da rodada 1:** `/tmp/claude-0/int90/tools/prototipo/v37/gen37/_render`.
  - Antes de copiar, conferido com `../v3.sha256`: 181 arquivos iguais, sha256 do conjunto `39b88342b9aa985f011dd9fabc9c5482d7a03a0c983b23fb740e8845158dd038`.
  - A árvore `int90` está agora em `5466c6d0` (v129). O `_render` não foi remontado.
- **Uma cópia só**, feita pela fase `preparar` dentro da pasta de trabalho do revisor.
  - Ficou imutável durante a medida (`chattr +i`), conferida de novo no fim e apagada depois.
  - `ocultas.json`, `navegacao.json`, `screens.json` e `v3.sha256` são idênticos aos da rodada 1.
- **Comando:**
  ```sh
  python3 -I robo-v51/rodar.py --render <_render> --trabalho <nova> --fases preparar   # cópia única
  python3 -I robo-v51/rodar.py --trabalho <mesma> --fases robo,leva,nav,escopo28,criticos,resumo --entrega rodada2/medida
  ```
- **Antes de abrir o navegador:** o revisor esperou o fim da bateria `n1/int/bateria.sh` de outra frente, que terminou às 23:53:16 UTC.
- **Tempos:** robô 12,4 min; 2ª passada 8,0; títulos 2,8; `escopo28` 2,4; casos críticos 4,0 + 0,8. Total 30,4 min.
- **Ambiente:**
  - Chromium 141.0.7390.37, headless, modo isolado em 3 origens (portas 39999, 43879 e 41627); cada origem viu só a própria marca.
  - Havia de 1 a 3 Chrome principais abertos antes de cada abertura; uma outra frente usava o Playwright.
  - 0 diálogos JS e 0 `*.v5err.json`.
  - 1 passagem com erro, transitória (ver "Comparação").
- **Processos:** o script encerrou só os próprios PIDs, sem `pkill` nem `killall`.

## Medidas

| Medida | Rodada 1 (@96a99f68) | **Rodada 2 (@7c2045d6)** | Por que mudou |
|---|---|---|---|
| IDs clicáveis no detalhe | 39/80 | **39/80 (49 %)** | — |
| Cadastros clicáveis | 6/84 | 6/84 | — |
| Chegada (passagens com alvo da origem) | 34/68 (50 %) | **45/68 (66 %)** | A3: as 11 páginas do próprio registro contam pelo h1 |
| · só a 1ª passada | 34/68 | 45/68 | 2ª passada: 45 `chegouEstrito`, os mesmos da 1ª; 0 resgates; nas 122 passagens, a URL aberta é igual ao destino do clique |
| Volta à origem | 8/68 | 8/68 | Os mesmos 8 casos com `exactId` (A9) |
| Voltar reabre o detalhe | 9/107 | 9/106 | Saiu a passagem com erro transitório |
| Inconclusivas | 165/233 (minha divisão: 85 registro + 80 tela) | **82 registro inconclusivo de 150 com intenção de registro (55 %) + 82 navegações de tela** | A4: o resumo agora separa; ver o resíduo no A4 |
| Erros de passagem | 0 | 1 (`PAGR[4]`, "não reabriu") | Transitório: 2 repetições isoladas da PAGR dão `navega MB-07#lg24`, igual à base |
| Empilhado | 0 | 0 | A candidata não tem `data-g2pilha` |
| `escopo28` herdado | 0/28 | **0/28**, agora calculado de `escopo-28.json` (A11) | Igual tela a tela |
| Portão (`aceite`) | "PENDENTE" fixo | **BLOQUEADO, 15 bloqueios** | A1 |

**Contexto, igual ao da rodada 1:**
- 94 telas e 190 detalhes;
- 246 passagens: 232 navegam, 11 abrem no lugar e 3 não fazem nada;
- 32 detalhes com "Próximo passo", 13 dizendo quem age.

## Percursos críticos e o portão

O comando padrão rodou `casos_criticos.py` pela lista e pelo endereço:
- 17 + 3 casos, 0 `naoRodados`, sem truncar;
- os mesmos 20 casos da rodada 1, com o mesmo `r`, `para`, `alvo` e `abriu` (20/20).

O `aceite.avaliar()` real deu `BLOQUEADO`. Saídas: `medida/resumo.json` → `aceite`; os recibos estão em `medida/brutos-isolado/casos-criticos*.json`.

| Percurso (inventário do portão) | Casos nesta candidata | Resultado | Portão |
|---|---|---|---|
| O.S. → EST · entregar (OS-0424, OS-0425) | "Entregar no Estoque ›" → `EST.dc.html` | 2/2 inconclusivas | **bloqueia** |
| O.S. → EST · devolver (OS-0417) | "Receber devolução no Estoque ›" | inconclusiva | **bloqueia** |
| O.S. → EST · saldo (OS-0418) | "Ver saldos no Estoque ›" | inconclusiva | **bloqueia** |
| O.S. → receituário (OS-0504, OS-0508) | nenhum link | ausente | **bloqueia** (2) |
| Receituário → O.S. (VIS-051, VIS-052) | AG-01, AG-04 e AG-04det | 9/9 chegam | passa |
| O.S. ↔ RA, nos dois sentidos | nenhum | ausente | **bloqueia** (2) |
| Aprovações → O.S. | nenhum | ausente | **bloqueia** |
| OM → O.S. (OM-0233) | só o achado SM-0147, que abre na própria MA, sem alvo | ausente | **bloqueia** |
| O.S. → OM (OS-0420, OS-0431, OS-0507) | OS-0431: "Acompanhar OM-0233 ›", 2/2 chegam | OS-0420 e OS-0507 sem link | **bloqueia** (2) |
| Também bloqueiam | "Há caso crítico inconclusivo ou falho", chegada geral < 95 % e "Há erros de execução" (o `PAGR[4]` transitório) | — | **bloqueia** |

**Veredito:**
- O portão bloqueia de forma automática o crítico inconclusivo ou ausente. Executado na medida real e, com os recibos da rodada 1, em `revisor/portao_contraprovas.py` (P0).
- Nenhum caso crítico chegou num alvo errado.
- Os bloqueios continuam sendo do produto, como na base.

## Comparação caso a caso com a rodada 1

Script `revisor/comparar_r2.py`, saída `revisor/saidas/comparacao-r1-r2.json`. Chave (tela, tipo, texto, href); telas filtradas como no `resumo.py`. Os critérios de cada rodada são os do próprio resumo.

| Diferença | Casos | Razão |
|---|---|---|
| Iguais | 235 | Mesmo resultado, destino, alvo, chegada, volta e Voltar |
| Chegada falsa → verdadeira | 11 | **Exatamente os 11 do A3** |
| Só na rodada 1 | 1 | `PAGR[4]` "Coletar contagem" → `MB-07#lg24`: o `openRow()` não reabriu o detalhe nesta execução. Repetida 2× sozinha (`revisor/saidas/PAGR-repeticao-*.v5.json`), dá `navega MB-07#lg24`, igual à base. O código de `load`/`openRow` não mudou no PR |
| Alvo, comportamento, volta, Voltar, refs | 0 | — |

Os 11 do A3 chegam pelo h1, sem diálogo. O h1 visto na 2ª passada (`leva-check.json`) é a página do registro:

| Origem → destino | h1 |
|---|---|
| IR-01 → IR-03det (4) | `OS-0392 · Irrigação · Gotejo T7`, e o mesmo padrão para OS-0423, 0394 e 0419 |
| AG-04 → AG-04det (2) e AG-07 → AG-04det | `Recomendação · REC-014 plantio T4` |
| AG-04 → AG-03det | `Diagnóstico · DIA-007 nematoide T4` |
| AG-07 → CA-01x-os0420 e CA-03det → CA-01x-os0420 | `OS-0420 · Plantio Soja 58 W` |
| GE-01 → CO-06det | `INSP-88 · Lote L27-013 bloqueado` |

Há também 1 chegada pelo h1 fora da taxa: MB-06 → MB-06#VIS-017, que fica na mesma tela.

## Achados A1–A11 da rodada 1

| # | Sev. | Veredito | Contraprova (executada salvo indicação) |
|---|---|---|---|
| A1 | S2 | **Parcial** | **Corrigido:**<ul><li>casos dirigidos no comando padrão;</li><li>bloqueio automático: medida real `BLOQUEADO` com 15 bloqueios;</li><li>P0, com os recibos da rodada 1: 14 bloqueios;</li><li>P1: um crítico extra inconclusivo bloqueia.</li></ul>**Falta:**<ul><li>o portão só lê a chegada. A F1 tem quatro metas ≥ 95 % (`desenho-F1-motor.md` §4, passo 8): IDs clicáveis, chegada, volta à origem e Voltar. P4: com chegada 0,95 e as outras três a 0 %, `avaliar()` dá `PASSOU_MEDICAO`, porque a assinatura `avaliar(diretorio, taxa, erros)` nem recebe as outras;</li><li>N1 e N3 abaixo.</li></ul> |
| A2 | S2 | **Corrigido** | <ul><li>`EST.dc.html?de=OS.dc.html%23OS-0502#ent=REQ-039` → `REQ-039`;</li><li>`MA…%23OS-0420#vis=ordens` → inconclusiva;</li><li>fragmento codificado `REQ%2D039` → `REQ-039`.</li></ul>`revisor/contraprova_alvo2.cjs`, nas funções reais, e `oraculo_test`. Medida real: 0 alvos mudaram entre os 68. Resíduo: N2 |
| A3 | S3 | **Corrigido** | <ul><li>Os 11 casos chegam (tabela acima).</li><li>Diálogo sem título com o ID no h1 não conta.</li><li>Diálogo com outro registro e o ID no h1 também não conta.</li><li>Limite aceito: h1 de lista filtrada que começa pelo ID conta. Resíduo: N5</li></ul> |
| A4 | S3 | **Parcial** (resíduo S4) | Há tipo por linha, `chegou: null` nas inconclusivas e `navegacoesTela`. Mas a "intenção de registro" ignora IDs no texto do link: GE-03 "REQ-035 · OS-0421" e "REQ-036 · OS-0420" → SU-07 contam como navegação de tela. Os brutos da rodada 1, resumidos pelo `resumo.py` novo, dão 83 + 82; a divisão do revisor dava 85 + 80 |
| A5 | S3 | **Corrigido** | `LEVA_JS` e `chegada_estrita()` reais, no navegador (D): <ul><li>diálogo sem título cujo corpo cita OS-0502 → `dlg: ''` e `false`;</li><li>título OS-0503 → `false`;</li><li>título OS-0502 → `true`;</li><li>só h1 OS-0502, sem diálogo → `true`.</li></ul> |
| A6 | S3 | **Corrigido** | `fase_leva()` real (C):<ul><li>`ZZ-DESVIO`: o clique é desviado por JS para `ZZ-DONA#OS-0503` e a 1ª passada recusa;</li><li>a 2ª passada abre o href `ZZ-DONA#OS-0502`, vê o título "OS-0502 · registro na dona" e dá `chegouEstrito: false`, porque a URL difere do destino do clique;</li><li>a expressão da rodada 1 aceitaria;</li><li>medida real: 0 de 122 URLs divergem.</li></ul> |
| A7 | S3 | **Parcial** | Detecta a marca descendente e a pilha com hash alterado (`ZZ-PH-RAPIDA` mede a pilha e a dona). O resumo ganhou contadores. O ajuste abriu o **N1** |
| A8 | S3 | **Corrigido** | Na medida real, `PAGR[4]` entra em `erros` e bloqueia ("Há erros de execução"). O `resumo_test` cobre o `*.v5err.json`. Resíduo em N6 (b) |
| A9 | S4 | **Corrigido** | `exactId` e h1 igual: 8/68, os mesmos 8 casos |
| A10 | S4 | **Corrigido** | <ul><li>`OS-0502/2` → `false`;</li><li>"PC-0012 · da OS-0502" → `false`;</li><li>`#dev=lin3&para=OS-0502` com texto sem ID → inconclusiva.</li></ul>Limite: sem ID no hash, o alvo ainda pode vir do texto e ser o ID da origem. Na base são 10 casos, legítimos, como "Abrir O.S. ›" no apontamento da OS-0420 |
| A11 | S4 | **Corrigido** | `herda` = 0, lido de `escopo-28.json`. Sem o arquivo, dá `null` (execução sintética) |

## Achados novos

Escala da rodada 1, com uma precisão:
- **S2:** pode aceitar a F1 sem a prova, ou falta portão;
- **S3:** distorce a medida ou bloqueia pelo motivo errado, com a prova nos brutos;
- **S4:** menor.

| # | Sev. | Onde | Achado | Prova |
|---|---|---|---|---|
| N1 | **S2** | `robot.html:115-125`; `aceite.py:23-25` | **Empilhado com hash gravado: a chegada na dona não é medida, e o portão aceita o resumo como chegada.**<ul><li>Depois de "Abrir na tela de", `waitNav(fr, before)` compara com a URL anterior à pilha. Como o hash já mudou, a espera volta na 1ª checagem, sem esperar a dona.</li><li>A passagem vira `mesma tela`, com `abriu` tirado do título da pilha.</li><li>O `passa()` aceita `mesma tela`, e o `empilhadosChegaramDona` conta esses casos.</li><li>O contrato (6241229682, item 5b) pede a chegada na dona com o mesmo alvo.</li></ul>**Correção:**<ul><li>gravar `const b1 = cur(fr)` antes do clique e esperar com `waitNav(fr, b1)`;</li><li>pilha sem "Abrir na tela de" não é chegada;</li><li>no portão, exigir `navega` com a tela de destino diferente da origem nos percursos entre telas;</li><li>o `empilhadosChegaramDona` só deve contar `navega`.</li></ul>A contraprova deve reprovar o `ZZ-PH-LENTAERR` | Executado (B), com páginas sintéticas e `passage()` real:<ul><li>`ZZ-PH-RAPIDA`: correto.</li><li>`ZZ-PH-LENTA`, dona em 1,5 s: `mesma tela`, `abriu` pelo título da pilha.</li><li>**`ZZ-PH-LENTAERR`, em que a dona abre OS-0503: `mesma tela`, `abriu: true`, e `avaliar()` não acusa o caso.**</li><li>`ZZ-PH-SEMIR`, sem link: `mesma tela`, também passaria.</li><li>Controles sem hash (`ZZ-P-*`): a dona é medida, com 1,5 s inclusive, e sem link dá `abre no lugar` e bloqueia.</li><li>Resumo: `empilhadosChegaramDona: 6` para 3 chegadas reais na dona.</li></ul> |
| N2 | S3 | `robot.html:33` | **O fragmento é cortado no 1º `&`.**<ul><li>`OS#painel=OS-0420&abre=OS-0431`, formato da OS no desenho F1 §2.2, dá o alvo OS-0420, que está errado.</li><li>`MA#vis=ordens&om=OM-0233` vira inconclusiva.</li><li>Sem efeito nesta candidata, que não tem href com ID depois de `&`, nem em link com `data-ref`.</li></ul>**Correção:** ler todos os parâmetros, ignorar as chaves de contexto e de visão (`de`, `para`, `ver`, `sob`, `vis`…), preferir `abre` e tratar como inconclusiva quando houver mais de 1 ID distinto | Executado (`contraprova_alvo2.cjs`) |
| N3 | S3 | `aceite.py:33`; `casos_criticos.py:74-92` | **O portão bloqueia por casos fora do inventário nomeado e não diz quais.**<ul><li>O "Há caso crítico inconclusivo ou falho" inclui 3 casos "Retirar no almoxarifado" (`OS→EST/outro`, fora do contrato) e o achado SM-0147.</li><li>O SM-0147 é classificado como `OM→OS` pelo texto, mas abre o achado na MA e não vai a uma O.S.</li><li>A F1 pode ser bloqueada por eles, e a mensagem não os lista.</li></ul>**Correção:** listar os casos no bloqueio, classificar `OM→OS` pelo destino (href ou `data-ref` de O.S.) e tratar `outro` como informativo ou incluí-lo no contrato | Executado: medida real e rodada 1 (P0) |
| N4 | S4 | `aceite.py` | **Os recibos não se ligam à execução, e a origem casa por substring.**<ul><li>P3: um recibo fabricado passa, sem hash do render nem identificador da execução.</li><li>P2: sem caso da OS-0424, o título "OS-0425 · desdobrada da OS-0424" satisfaz a exigência da OS-0424.</li></ul>**Correção:** gravar o `sha256_conjunto` e um identificador da execução nos recibos e conferir os dois; casar a origem pelo 1º ID do título | Executado (`portao_contraprovas.py`) |
| N5 | S4 | `robot.html:130,137` | **A prova do h1 não fica no bruto.**<ul><li>Na chegada pelo h1, `titulo` fica vazio (12 passagens), e a auditoria depende da 2ª passada.</li></ul>**Correção:** gravar o `arrival().titulo` como prova | Executado (medida real) |
| N6 | S4 | `robot.html:103`; `rodar.py:637-642`, `:755` | **Robustez e higiene:**<ol type="a"><li>`openRow()` usa uma espera fixa de 650 ms. Com a máquina ocupada, gera "não reabriu" transitório, que bloqueia o portão (AGENTS §3.6: esperar a condição observável);</li><li>`resumo-isolado-1a-passada.json` dá sempre `BLOQUEADO` por "Execução ausente" e não vê `*.v5err.json`, porque os links simbólicos só cobrem `*.v5.json`;</li><li>no tempo-limite do `casos_criticos.py`, o `subprocess.run` mata só o Python filho, e o Chrome e o servidor dele ficariam órfãos (por leitura do código);</li><li>`execucao.json` não registra os tempos da fase `criticos`.</li></ol> | (a) e (b) executados; (c) e (d) por leitura do código |

**Observação de contrato (não é defeito do robô):**
- O portão exige O.S. ↔ RA nos dois sentidos, conforme o item 4 de 6241229682.
- O desenho da F1 diz "Sem dona na F1: DIA, REC e RA".
- Do jeito que estão, a F1 nunca chega a `PASSOU_MEDICAO`. Os dois agentes precisam combinar uma de duas saídas:
  - o RA ganha dona na F1;
  - o critério RA é adiado e registrado como tal.

  Pelos papéis, o Codex lidera os critérios de aceite.

## Testes e contraprovas executados

Saídas em `revisor/saidas/`.
- **Testes do PR @7c2045d6** (`testes.txt`), todos PASS, rc=0:
  - `node oraculo_test.cjs`: 13 casos, mais A2/A3 e A10;
  - `node segunda_passada_test.cjs`;
  - `python3 -I resumo_test.py`;
  - `python3 -I segunda_passada_test.py`: 7 casos;
  - `python3 -I aceite_test.py`: 6 casos;
  - `py_compile` dos quatro `.py`.
- **`revisor/contraprova_alvo2.cjs`:** 19 casos nas funções reais (`contraprova_alvo2.txt`):
  - 14 OK;
  - 3 DIF são o N2;
  - 2 DIF são limites documentados.
- **`revisor/portao_contraprovas.py`,** com o `aceite.avaliar()` real (`portao_contraprovas.json`):
  - P0, com os recibos da rodada 1: `BLOQUEADO`;
  - P1: o controle passa, e com um extra inconclusivo bloqueia;
  - P2, P3 e P4: veja N4 e A1.
- **`revisor/contraprovas_navegador2.py`,** com páginas sintéticas em `revisor/sint/`, no Chromium (`contraprovas2.json`, `.log`, `-resumo.json`, `-leva-check.json` e `sint-brutos/`):
  - A: isolamento reprovado com origem compartilhada (PASS);
  - B: 7 pilhas;
  - C: 2ª passada desviada;
  - D: 4 páginas da 2ª passada;
  - E: `resumo.py` e o portão sobre B.
- **Medida completa no mesmo `_render`** (`medida/`), com a repetição isolada da PAGR (2×).
- **Comparações:** caso a caso (`comparacao-r1-r2.json`) e o re-resumo dos brutos da rodada 1 com o `resumo.py` novo (83 + 82, no A4).

**Não executado:**
- teclado, leitor de tela e os testes T3/T5/T7 da F1;
- modo pacote, que o v5.1 recusa;
- pilha real, porque a candidata não tem `data-g2pilha`; o empilhado só foi medido em páginas sintéticas;
- (c) e (d) do N6, que foram só lidos;
- nenhuma candidata da F1;
- nenhum comentário, parecer ou push no GitHub.

## Parecer: o v5.1 @7c2045d6 está apto a ser a régua da F1?

**Ainda não.**

**O que avançou:**
- A1–A11 estão corrigidos ou parciais, e nenhum está sem correção.
- A medida é reprodutível no mesmo render: 235 de 246 iguais, 11 diferenças explicadas pelo A3 e 1 erro transitório, repetido.
- O portão existe e bloqueia o que deve bloquear nesta candidata.
- Nesta candidata não há falso positivo de chegada.

**Antes de medir a F1, o autor precisa de:**
1. **N1 (S2):** a pilha que grava o hash tem de esperar a dona, e o portão não pode aceitar `mesma tela` ou pilha como chegada nos percursos entre telas. A F1 introduz exatamente a pilha (R3).
2. **A1, resíduo:** o portão precisa cobrir as quatro metas ≥ 95 % do desenho §4 (IDs, chegada, volta e Voltar), ou deixar explícito que `PASSOU_MEDICAO` é só da chegada.
3. **N3 (S3):** o bloqueio precisa listar os casos, e a classificação `OM→OS` deve ser pelo destino.
4. **N2 (S3)** na mesma revisão, porque o formato `#painel=…&abre=` é da F1.

**Combinar:** a observação do RA. N4–N6 e o resíduo do A4 podem entrar junto.

**Os números de `medida/` são a nova base do robô corrigido:** chegada 45/68, volta 8/68, Voltar 9/106, IDs 39/80 e escopo 0/28. Não se comparam com a v5 nem com a v108.

## Arquivos

| Arquivo | O que é |
|---|---|
| `medida/resumo.json`, `medida/resumo-isolado-1a-passada.json` | Resumo v5.1 com o portão (`aceite`); o segundo é sem a 2ª passada |
| `medida/brutos-isolado/` | 102 `*.v5.json`, `escopo.v5.json`, `leva-check.json` e os dois recibos `casos-criticos*.json` (0,3 MB) |
| `medida/isolamento-v51.json`, `escopo-28.json`, `execucao.json`, `execucao-stdout.log`, `robo-isolado.log`, `preparo.json`, `v3.sha256`, `comparacao.json`, `entradas/` | Saídas do `rodar.py` |
| `revisor/comparar_r2.py`, `revisor/saidas/comparacao-r1-r2.json` | Comparação caso a caso com a rodada 1 |
| `revisor/contraprova_alvo2.cjs`, `revisor/portao_contraprovas.py`, `revisor/contraprovas_navegador2.py`, `revisor/sint/` | Contraprovas do revisor |
| `revisor/saidas/testes.txt`, `contraprova_alvo2.txt`, `portao_contraprovas.json`, `contraprovas2*`, `sint-brutos/`, `PAGR-repeticao-*.v5.json` | Saídas |
