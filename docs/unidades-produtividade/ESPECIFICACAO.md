# Unidade de produtividade selecionável · especificação v1.1

**Pedido do proprietário (Adrianus, 10/10/2026, literal, trazido pelo Codex em UNIDADES-PROD-20261010-01, PR #47, comentário 6093638004):** «Coloque opções para todas culturas em kg/ha, ton/ha, sc 60 kg/ha, etc.» O Codex aceitou a direção em 6093701812 com duas precisões: a base kg/ha vale só para o indicador em massa (item 4 do contrato) e a agregação não conta duas vezes a mesma área (item 6).

- **Rótulo:** especificado. Nenhum código foi alterado. "(executado)" marca o que saiu de comando rodado em 10/10/2026 nesta worktree: `python3 docs/unidades-produtividade/verificacao/contas.py` (FALHAS: 0), as buscas do §0 (`grep` de sc/ha, t/ha, kg/ha, produtividade, `prPrtv`, `un_meta`, `KG_UN`), a checagem de nomes globais (safra.js, ocupacao.js, cal01.js, g2lib.js, support.js e o JS do processo_safra.py contra producao.js e cenario.js: nenhuma colisão) e a sonda da semente no node (ponderada do mamão 96.740 kg ÷ 137,9 ha = 0,70 t/ha; nenhuma soja, milho ou café com produção na semente).
- **v1.1 (10/10/2026):** revisão por contraexemplo contra o código e o PRD. Os achados RC-01 a RC-17 e o que mudou estão no §10.
- **Base:** `47ff754` (branch `claude/v44-unidades`). `gen37/` = `tools/prototipo/v37/gen37/`. PRD = `Safrion-Software-/docs/PRD.md` v3.11, "l.N" = linha. Decisões tomadas sem o proprietário: `DECISOES.md` (D-Unn). O PRD não é reaberto: o requisito fica registrado em `DECISOES.md`, fica fora da v55 e entra na versão seguinte (contrato, item 8).
- **Fontes reaproveitadas, não repetidas:** a unidade de mercado e a massa de cada cultura vêm de `docs/culturas/UNIDADES-DE-MERCADO.md` (DEC-0510-03). Área colhida, produtividade, referência, café e "a apurar" vêm de `docs/colheita/ESPECIFICACAO.md` (R-02, R-04, R-05, R-09 e COLH-C01). Do PRD valem 10.0 (decimal sem arredondar a cada etapa, l.4237), 45.4 (no café, a quantidade tem base declarada e não há fator universal, l.7648) e 62.2/62.3 (a saca exige massa explícita, as passagens legítimas somam e produtos e estados não se misturam, l.9188 e l.9194-9196).

```text
ID / resultado útil / persona: UNID-PROD / ler e planejar a produtividade em kg/ha, t/ha, sc 60 kg/ha ou na unidade do mercado, sem conta de cabeça / agrônoma, gestor, encarregado de colheita
Requisitos do PRD e fora do escopo: DEC-0510-03; PRD 10.0, 45.4, 62.2, ENG-011, ENG-013; fora: §9
Autor / revisor / integrador: Claude / Codex / integrador da branch única
Base / arquivos sob responsabilidade: 47ff754 / producao.js (bloco novo e os pontos do §0), g2lib.js (preferência, chave de ordenação e filtro, gancho de abertura), areas/producao.py (COLH), safra.js e areas/processo_safra.py (meta), dados_cad.py e dados_producao.py (catálogo), cad_culturas.py (texto de ajuda), testes do §7
Aceite e comando de verificação: §8; bateria do §7
Estado / impedimento / próximo passo: especificado (v1.1, revisada) / nenhum (D-U01 a D-U21 valem até o proprietário mudar) / P1
```

## 0. Mapa do existente (busca executada)

| Fica (reusar sem mudar o comportamento) | Onde |
|---|---|
| Unidade de mercado por cultura (fonte única), com a massa da unidade em kg, a base física e o estágio de campo do café (`campo: 'L'`, `proc: 'Café da roça'`) | `dados_cad.py:41-53` (`CULTURA_UN`) → `PRDC.un` (`dados_producao.py:59`) |
| Massa declarada da caixa do packing (caixa de 10 kg do mamão) | `dados_cad.py:166-167` (`EMB_PACK`) |
| Produtividade = produção na base física ÷ área colhida. No perene, a área é a do cultivo; no anual, mín(área do cultivo, Σ ha apontados) | `producao.js:133` (`prPasse`), `:140-150` (`prResultado`) |
| Ponderada Σ produção ÷ Σ área; café a apurar fica fora da conta | `producao.js:161-162` (`prPonderada`) |
| Café a apurar como estado próprio (nunca "0 sc"); `cafe` = só os L a apurar (C01d, U12) | `producao.js:120-127`, `:153-158` |
| Peso líquido do fruto do café por origem (`x.kg`, rateado na pesagem) e o total em `liq` | `producao.js:124`, `:391` |
| Decimal com 6 casas por BigInt e texto pt-BR; `prMulDiv` com um arredondamento só | `producao.js:9-30` (`prM`, `prDiv`, `prMulDiv`, `prFmt`, `prFmtT`) |
| `prtv` de `prResultado`, `prPasse` e `prPonderada` no Padrão (U03, U06 e C01 leem) | `producao.js:138`, `:150`, `:162` |
| Perfil de quem usa a tela | `g2lib.js:257-275` (bloco `<perfis>`: `G2_PERFIS`, `g2perfil`) |
| Meta do cultivo guardada como valor + unidade; o texto do Padrão da meta, com o período, vem de `UN_META` (CD-02) e a massa vem do `CULTURA_UN` | `dados2.py:63-82`, `dados_lagoa_safra.py:69-70` (`meta`, `un_meta`); `ocupacao_cen.py:10` |

| Muda | Arquivo:linha | Passo |
|---|---|---|
| Conversor único (`prUnp*`, §5) num bloco novo depois da produtividade. `prPrtvTxt` e `prPrtvResTxt` ganham o parâmetro `op`: com `op`, delegam a `prUnpTxt(prUnpInd(…))`; sem `op`, o texto de hoje (mensagens, R-U12) | `producao.js:47-50`, `:158` | P1 |
| `prProdOS`, `prPasse` e `prResultado` passam a levar `litros` (todos os L de café da roça, medidos ou a apurar), `kgOk` (toda origem com peso líquido > 0) e `estim` (alguma origem `modo: 'estimada'`). `cafe` e `liq` não mudam | `producao.js:122-127`, `:137`, `:142-150` | P1 |
| O desvio contra a meta passa a ser calculado em kg/ha pelo conversor, lendo `k.un_meta` (mesmo número na semente) | `producao.js:147`, `:149` | P1 |
| O rascunho "pela meta" converte a meta por `prUnpKgHa(k.cultura, k.meta, k.un_meta)`; sai o `× 1000` fixo (mesmo número: U11c = 36.298,076923 kg, K-U12) | `producao.js:174`, `:176` | P1 |
| Guarda de agregação: produto ou estágio diferente não soma | `producao.js:161` | P1 |
| Algodão em caroço e algodão em pluma (@ de 15 kg) entram no catálogo, sem nenhuma fazenda | `dados_cad.py:41-53` | P1 |
| `PRDC.unAlt`: unidades com massa declarada por cultura, lidas de `EMB_PACK` | `dados_producao.py:59` | P1 |
| Preferência por perfil × cultura, **dentro do bloco `<perfis>`** (assim `cenario.perfis_js()` a leva aos testes sem navegador) | `g2lib.js:257-275` (`g2unidPref`, `g2unidSet`) | P2 |
| Chave estável de ordenação e de filtro por valores: `g2key` e `g2fkeys` leem `r.ordk[c.k]` antes do texto; o menu do filtro mostra o texto da célula | `g2lib.js:26-28`, `:155` | P2 |
| COLH: seletor na barra da tabela "Previsão e resultado por talhão"; linha, total da cultura, painel e cartão na unidade escolhida; `r.ordk.prtv`; meta com até 2 casas | `areas/producao.py:493-496` (`g_tal`, `tools=`), `:540-546` (`prTalRow`), `:550-552` (`prGrpNum`), `:559-563` (grupo), `:597-611` (painel), `:631-634` (cartões) | P2 |
| Testes cuja expectativa muda pela regra R-U05 (o motivo vai no commit) | `cafe_apurar_unit.js:22-25` (C01a, C01b), `:33-34` (C01f), `:62-63` (C01k) | P2 |
| SAF: o conversor único substitui a segunda tabela de fator; linha com unidade sem massa fica fora da conta, como hoje | `safra.js:591-596` (`KG_UN`, `prodColheita`) | P3 |
| SAF: meta na unidade escolhida (coluna, painel e Dividir), guardando a unidade informada e sem regravar o que não mudou (R-U06); `r.ordk.meta` | `safra.js:529`, `:747`, `:819`, `:827`, `:853-855`, `:869-887`, `:933`, `:947`; `areas/processo_safra.py:46`, `:61`, `:351-352` | P3 |
| Gancho de abertura do formulário (`self.g2openDraft`), para o SAF pôr no rascunho a meta convertida e a origem | `g2lib.js:110` (`g2open`) | P3 |
| SAF carrega o conversor (`cenario.js` + `PRDC` + `producao.js`) sem ler nem gravar o cenário | `areas/processo_safra.py:229` | P3 |
| CD-02: a ajuda e o aviso do campo "Unidade de produtividade" passam a dizer "Padrão da cultura" (hoje dizem que o Planejar safra usa só essa unidade) | `areas/cad_culturas.py:85`, `:229` | P3 |
| A guarda "nomes de producao.js não são redefinidos" passa a cobrir também o safra.js | `producao_unit_test.py` (lista `outros`) | P3 |

**Sai:** `KG_UN` (`safra.js:591`) e o `× 1000` do rascunho semanal (`producao.js:174`), segunda e terceira tabelas de conversão.
**Mapeado e sem mudança (§9):**
- **IN-04:** a camada "Colheita/produtividade" está fora da barra (`areas/inicio.py:100`, `LAYS_F2`). Os dados fixos `COL` (`:193-198`) não entram no `MDATA` (`:488`); `_proxima` (`:215`) e `engine.farm_layers` (`engine.py:788`) não têm uso.
- **CD-01 (visível no menu):** o detalhe do talhão mostra as parcelas do Planejar safra em consulta, com a meta como foi gravada, valor e unidade (`cad_fazendas.py:466`). É o fato registrado, não um indicador: fica sem seletor (D-U21).
- **PL-01:** "Meta (hipótese)" (`planejamento.py:167`) é tela oculta.
- **PROD e CARGA:** não mostram produtividade (nenhum `prPrtv` em `PROD_JS` e `CARGA_JS`, executado). A mensagem do recebimento (`producao.js:397`) mostra o passe no texto de hoje, sem `op`. O texto da carga de café (`prCargaCafeTxt`) é produção e não muda (C01n).
- **Gestão:** os textos de `gestao.py:13-14` e `:172-174` são fixos e a tela fica oculta.
- **"5,8 sc/ha":** em `comercial.py:454` é a troca do barter, um preço, não uma produtividade.
- **CD-02:** o campo "Unidade de produtividade" (`cad_culturas.py:73`, `:85`; `dados_cad.py:30-32`) continua sendo o texto do Padrão da meta (via `UN_META`); a massa do Padrão vem do `CULTURA_UN`, a mesma da COLH. A escolha no formulário do CD-02 não sai da página, como hoje.
- **Doses em kg/ha e L/ha:** `campo.py`, `agronomia.py` e `mobile.py` mostram doses, não produtividade.

## 1. Missão e princípios
1. A pessoa lê a produtividade na unidade em que decide (kg/ha, t/ha, sc 60 kg/ha ou a do mercado), sem fazer conta de cabeça e sem confundir produto.
2. Trocar a unidade só muda a exibição. Nenhum fato muda: cenário, meta, área e estoque ficam como estão, e um rascunho aberto fica na unidade em que foi aberto.
3. Uma fórmula só (ENG-011): toda conversão passa pelo conversor de `producao.js`, que lê a massa da unidade no cadastro (`CULTURA_UN`, `EMB_PACK`).
4. Massa só converte massa. Litro, fruto ou caixa sem massa declarada nunca vira kg.
5. O produto ou o estágio aparece junto do número quando a unidade é uma equivalência ou o estágio não é o produto-base da cultura (D-U18).
6. Essencial: um seletor por tabela e nenhuma tela, menu ou cadastro novo.

## 2. Menu e telas, antes → depois

| Tela | Antes | Depois | Natureza |
|---|---|---|---|
| Produção › Previsão e colheita (`COLH`), visão Por talhão | Produtividade e meta na unidade da cultura | Seletor "Unidade de produtividade · ‹cultura›" na barra da tabela. Linha, total da cultura, painel e cartão aparecem na unidade escolhida | planejamento + controle |
| Agrícola › Planejar safra (`SAF`), Talhões e cultivos | Meta na unidade de mercado, sem escolha | O mesmo seletor na barra da tabela. Coluna Meta, painel do cultivo e Dividir aparecem na unidade escolhida | planejamento |
| Mapa (`IN-04`) | Camada Colheita e produtividade fora da barra | Igual. Quando a camada voltar (DEC-0910-36), ela usa o mesmo conversor e a mesma preferência (D-U02) | controle |
| COLH Por semana, CARGA, PROD, CD-01 e app | Produção, estoque e meta gravada na unidade em que estão | Igual: essas telas não mostram o indicador de produtividade (D-U10, D-U21) | — |

O menu não ganha item.

## 3. Telas

**Seletor (igual nas duas telas):**
- **Controle:** `<select>` nativo com `<label>` "Unidade de produtividade · Mamão Formosa", na **barra da tabela** (`engine.grid`, `tools=`, à direita, depois da busca e dos filtros), nas duas telas. Tem o mesmo visual dos seletores do Mapa (`inicio.py:1250`). No celular a barra continua visível (abaixo de 480 px só a rolagem da grade vira cartões).
- **Contexto:** a cultura do registro com o painel aberto (COLH: `pr_sel`; SAF: o cultivo do formulário). Sem painel, a primeira cultura visível na lista, já com os filtros aplicados. O rótulo diz o nome da cultura.
- **Opções:** as da R-U03, do estágio-base da cultura. Opção sem massa no estágio-base vira `<option disabled>` com o motivo no texto. Se a escolha não vale para um estágio mostrado (Café da roça só em L), a célula desse estágio mostra o Padrão dele e uma nota curta aparece abaixo do seletor.
- **Teclado:** Tab, a partir da busca da tabela, chega ao seletor sem sair da barra; as setas trocam a opção; Enter confirma sem disparar nenhuma ação (nada gravado, painel e filtros como estavam).
- **390 px:** altura mínima de 44 px, fonte de 16 px (evita o zoom do iOS) e quebra de linha.
- **Não é ação:** não muda a ação primária, não abre painel e não limpa filtros, ordenação, rascunho (`pr_form`, `pr_ferr`, formulário e Dividir do SAF) nem foco (R-U11).
- **Ordenação e filtro por valores** das colunas Produtividade e Meta usam a chave em kg/ha (`r.ordk`, R-U11): a ordem e o filtro aplicado são os mesmos em qualquer unidade. A busca por texto procura o que está na tela.

### 3.1 COLH · Previsão e resultado por talhão
**Pergunta:** a mesma de hoje. Só mudam as colunas de produtividade (exemplo com kg/ha escolhido para o Mamão Formosa, números da §6):

| Coluna | Antes | Depois |
|---|---|---|
| Produtividade (Pivô 19) | 0,48 t/ha · ciclo parcial | 484,89 kg/ha · ciclo parcial |
| Referência · desvio | meta 50 t/ha/ano · ciclo aberto | meta 50.000 kg/ha/ano · ciclo aberto |
| Linha da cultura | 0,70 t/ha ponderada sobre 137,9 ha colhidos | 701,52 kg/ha ponderada sobre 137,9 ha colhidos |

- **Colunas que não mudam:** Área, Previsão, Colhido e Situação continuam na unidade da cultura, porque são produção e não taxa (D-U10).
- **Café com parte a apurar** (C1, 12.000 L, 6.000 kg pesados, 5 ha):
  - Padrão: "sc/ha a apurar · 2.400 L/ha de Café da roça".
  - kg/ha: "kg/ha a apurar · 1.200,00 kg/ha de Café da roça".
  - Sem peso do fruto: a célula mostra só os L/ha e a nota do seletor diz "kg/ha indisponível para Café da roça: falta peso ou conversão medida".
  - Sem área apontada: "sc/ha a apurar · sem área colhida apontada".
  - Medido o beneficiado de todas as origens, a célula mostra só o beneficiado, como hoje (C01i e C01j não mudam).
- **Painel:**
  - Na unidade escolhida: a meta do subtítulo, o kv Produtividade, os passes, o Resultado e o rascunho "pela meta".
  - O kv "Unidade (DEC-0510-03)" passa a "Unidade de produtividade", com o texto "kg/ha · Padrão da cultura: t/ha".
  - Passe sem área: "sem área colhida apontada" (o mesmo texto da R-U07; hoje "sem área apontada").
- **Ação primária e estados do talhão:** iguais aos de hoje (COLH §3.1).
- **Celular:** os cartões do talhão e da cultura mostram o número na unidade escolhida. O seletor fica na barra da tabela, com alvo de 44 px. Não há rolagem horizontal.

### 3.2 SAF · Talhões e cultivos
**Pergunta:** a mesma de hoje. A coluna Meta mostra a unidade junto do número (por exemplo, "3.840 kg/ha" no T1-A com kg/ha escolhido para a Soja), com até 2 casas. O talhão dividido continua mostrando "por parcela".
- **Painel do cultivo:** ao abrir, o campo "Meta de produtividade" mostra o valor na unidade da preferência, com a unidade ao lado. O campo só de leitura "Unidade da meta" passa a "kg/ha · Padrão da cultura: sc/ha (60 kg)". A unidade do rascunho fica fixa enquanto o painel está aberto: trocar o seletor não muda o número nem a unidade do campo.
- **Dividir:** cada parcela mostra a meta na unidade da preferência da cultura dela, fixada ao abrir a folha. A folha não tem seletor próprio.
- **Salvar (painel e Dividir, linha a linha):** se o texto do campo da meta é o mesmo mostrado ao abrir, guarda o `{meta, unm}` que já estava; se mudou, guarda {número digitado, unidade do rascunho} (R-U06).
- **Sem mudança:** ação primária, etapas e estados do SAF. O Custo R$/kg dá o mesmo valor, agora calculado pelo conversor.
- **Celular:** igual ao SAF de hoje, mais o seletor com 44 px.

## 4. Regras (testáveis, com o dano evitado)

| # | Regra | Dano que a regra evita |
|---|---|---|
| R-U01 | Conversor único em `producao.js` (`prUnpOpcoes`, `prUnpMassa`, `prUnpKgHa`, `prUnpInd`, `prUnpTxt`, §5). Nenhuma tela multiplica ou divide unidade por conta própria; saem o `KG_UN` e o `× 1000` do rascunho | Duas tabelas de fator divergentes (o arroz RS contado com saca de 60 kg dá 17 % menos sacas) |
| R-U02 | A base do indicador em massa é kg/ha: kg medidos ÷ área colhida (COLH R-02 e R-04), com 6 casas e meio para cima, para ordenar e comparar. O número na unidade escolhida sai da produção e da área com um arredondamento só: base ÷ (área × massa da unidade) (PRD 10.0). Na tela: realizado com 2 casas fixas ("0,00 kg/ha", "484,89 kg/ha"); meta com até 2 casas, em toda tela ("3,84 t/ha", "64 sc/ha"). Nunca se converte um texto já convertido | Deriva depois de trocas repetidas; tabela, painel e outra tela com números diferentes (COLH mostrava a meta com 1 casa e o SAF com 2) |
| R-U03 | Opções:<br>• "Padrão da cultura", com a unidade concreta e a massa no rótulo (ex.: "Padrão da cultura · sc/ha (60 kg)");<br>• kg/ha;<br>• t/ha;<br>• "sc 60 kg/ha (equivalência)";<br>• as unidades com massa declarada do produto em `CULTURA_UN` e `EMB_PACK` (ex.: "cx 10 kg/ha (equivalência)").<br>Sai a opção igual ao Padrão em todos os estágios da cultura (soja e milho ficam sem sc 60; o mamão fica sem t).<br>Texto da célula: "‹número› ‹un›", com `un` = "kg/ha", "t/ha", "sc60 eq./ha", "cx10 eq./ha" ou o Padrão; mais " de ‹produto›" quando a unidade é equivalência ou o estágio não é o base (D-U18: "16,01 sc60 eq./ha de Mamão Formosa · fruta de campo", "1.200,00 kg/ha de Café da roça"), e " · estimativa" (R-U07).<br>O período ("/ano") só aparece na meta e vem da unidade gravada nela; o realizado diz "ciclo" ou "safra", como hoje. O `lado` da laranja (t/ha ao lado das caixas) só aparece no Padrão | A pessoa precisar deduzir a unidade; confundir a equivalência de 60 kg com a saca do produto (arroz RS de 50 kg; PRD 62.2) |
| R-U04 | A equivalência de 60 kg não supõe embalagem e não muda a saca do pedido, do contrato nem do estoque: `prUn`, `prQ` e `prEstTxt` ficam intocados | Venda ou estoque contados em sacas erradas |
| R-U05 | Massa só vem de massa. kg, t, sc, @ e cx valem quando a produção do estágio é massa pesada na balança.<br>Café da roça: o kg do fruto só vale se todas as origens do resultado têm peso líquido maior que zero (`kgOk`). Sem isso, a tela mostra L/ha e as opções de massa ficam indisponíveis com o motivo "Falta peso ou conversão medida". O mesmo vale para coco e abacaxi, contados em frutos.<br>Não existe fator de L para kg nem de L para sc. Com massa do fruto, o indicador diz "de Café da roça", nunca café beneficiado | Saca presumida por fator fixo (PRD 45.4; COLH R-09) |
| R-U06 | A meta editável guarda o valor e a unidade informados (`meta`, `unm`). `unm` é o `un` da opção escolhida, mais o período quando a cultura tem ("kg/ha", "t/ha", "sc60 eq./ha", "kg/ha/ano", "cx10 eq./ha/ano") ou o texto do Padrão ("sc/ha", "t/ha/ano"); nunca a chave "padrao" nem o rótulo do seletor. O kg/ha sai de valor × massa (multiplicação exata) a cada leitura.<br>O rascunho (painel e cada linha do Dividir) fixa a unidade ao abrir. Salvar com o texto do campo igual ao mostrado ao abrir não regrava a meta, mesmo com outra unidade na tela.<br>Ao trocar a cultura, a unidade só fica se continuar válida; senão vira o Padrão da nova cultura, com o número como está e a unidade nova ao lado (como hoje).<br>Não há migração: as metas atuais já estão no Padrão | Meta que muda sem ninguém editar; deriva em conversão não exata (50 t/ha/ano mostrado como 833,33 sc60 eq. e regravado viraria 49,9998 t/ha); número digitado reinterpretado em outra unidade (3.900 kg/ha viraria 3.900 t/ha) |
| R-U07 | Estados do indicador:<br>• medido: mostra o número;<br>• zero medido: "0,00 kg/ha";<br>• a apurar: café beneficiado sem rendimento medido, nunca mostrado como "0";<br>• pendência de área: produção maior que zero com área colhida 0 mostra "sem área colhida apontada", sem dividir (linha, painel e passe);<br>• não colhido: "—";<br>• estimativa: se alguma origem tem participação estimada (`estim`), " · estimativa" vem junto | Decidir sobre zero falso ou sobre divisão inválida |
| R-U08 | Agregação:<br>• entre talhões ou parcelas distintas do mesmo produto e estágio: Σ produção ÷ Σ área (`prPonderada`);<br>• passagens do mesmo cultivo: somam a produção e usam a área do cultivo uma vez só (`prResultado`; perene = área do cultivo, anual = mín(área, Σ ha));<br>• chave de agregação = produto do estágio (`u.prod` no base, `u.proc` no campo); `prPonderada` lança o erro "Produtos ou estágios diferentes não se agregam: ‹A› × ‹B›" (algodão em caroço × pluma, café da roça × beneficiado, massa verde × seca quando existir);<br>• a linha da cultura agrega só o estágio-base, e os talhões em outro estágio ficam "fora da conta" | 750 kg/ha em vez de 1.500; média de médias; café da roça somado com café beneficiado |
| R-U09 | Planejado e realizado comparam na mesma base: desvio = (kg/ha real − kg/ha da meta) ÷ kg/ha da meta, os dois pelo conversor, com a unidade gravada na meta (`un_meta`). Produto ou estágio diferente (café da roça contra uma meta de café beneficiado) não compara e mostra "a apurar" | Desvio falso |
| R-U10 | A preferência fica no localStorage, na chave `safrion.pref.unidprod:<perfil>:<cultura>` (perfil = `g2perfil().k`; cultura = nome no cadastro), com o valor = chave da opção (`padrao`, `kg`, `t`, `sc60`, `cx10`…). Leitura e gravação ficam em try/catch, com a memória da página como reserva, e o valor inicial é o Padrão. Nada vai para o cenário nem para outra chave. Se a escolha não vale para o estágio, a tela mostra o Padrão e o motivo, sem apagar a preferência | Troca visual virar fato de negócio; perder a escolha ao voltar à tela |
| R-U11 | Trocar a unidade não é ação: não chama `cenMudar` e não mexe em `pr_sel`, `pr_form`, `pr_ferr`, no rascunho do SAF, nos filtros, na ordenação nem no foco. Ordenação e filtro por valores das colunas Produtividade e Meta usam `r.ordk` (kg/ha em 6 casas; "apurar", "pend" e "vazio" para os estados), não o texto | Perder rascunho, filtro ou ordem; filtro aplicado que passa a não achar nenhuma linha; "1.200,00 kg/ha" ordenado antes de "484,89 kg/ha" (texto) |
| R-U12 | Mensagens de comando (recebimento, publicar) ficam no texto de hoje (`op` ausente): o domínio não lê preferência de tela. As telas sempre passam `op` (o Padrão também) | Regra de domínio dependente do navegador |

## 5. Estado único e integrações

| Módulo | Lê | Grava |
|---|---|---|
| Cenário (`c.producao`, `c.ordens`) | Cargas recebidas, origens (kg, L, `ben`, `modo`) e apontamentos somados, via `prResultado` e `prPasse` | Nada; a prova é a comparação byte a byte (AC-c) |
| Cadastro (`PRDC.un` = `CULTURA_UN`; `PRDC.unAlt` montado de `EMB_PACK`) | Massa da unidade, base física e estágio de campo (`campo`, `proc`) | Nada |
| Planejar safra (linhas `g_cult`, estado da página) | `meta`, `unm` e cultura | `meta` e `unm`, só no Salvar e só se o texto do campo mudou |
| Perfil (`g2lib.js`, bloco `<perfis>`) | `g2perfil().k` | Nada |
| Navegador | `safrion.pref.unidprod:*` | Só essa chave |
| Mapa, quando a DEC-0910-36 trouxer a camada | `prUnpInd`, `prUnpOpcoes`, `g2unidPref` | Nada |

**Assinaturas:**
- `prUnpOpcoes(cultura, estagio)` → `[{k, rot, un, massa|null, ok, motivo}]`, com `estagio` = `'base'` ou `'campo'`.
- `prUnpMassa(cultura, unTxt)` → `{massa, per}` ou `null`; reconhece exatamente os `un` de `prUnpOpcoes` e o texto do Padrão, com ou sem "/ano".
- `prUnpKgHa(cultura, valor, unTxt)` → kg/ha com 6 casas, ou o erro "unidade sem massa".
- `prUnpInd(cultura, X, k)` → `{st, kgHa, num, un, prod, estagio, estim, motivo}`, onde `X` vem de `prResultado`, `prPasse` ou `prPonderada`; `num` = base ÷ (área × massa) com um arredondamento.
- `prUnpTxt(ind)` → texto da célula (R-U03).
- `g2unidPref(cultura)` e `g2unidSet(cultura, k)`, no bloco `<perfis>`. As funções das telas (`prTalRow`, `prPanTal`, `prGrpNum`, cartões, `leafParts`) leem `op = g2unidPref(cultura)`; sem localStorage (node, janela privada) dá o Padrão.
- `prResultado`, `prPasse` e `prPonderada` mantêm `prtv` no Padrão; o kg/ha sai de `prUnpInd`.

## 6. Semente sintética (os números fecham; executado em `verificacao/contas.py`, FALHAS: 0)
Nenhum dado novo entra no cenário e a versão `v` não muda. A preferência começa vazia, ou seja, no Padrão. Os números abaixo vêm da semente da COLH (§6.6 dela; a ponderada do mamão também saiu da sonda no node, executado):

| Contexto | Padrão | kg/ha | t/ha | sc60 eq./ha | Outra |
|---|---|---|---|---|---|
| Pivô 6, ciclo (60.320 kg em 62,79 ha) | 0,96 t/ha | 960,66 | é o Padrão | 16,01 | 96,07 cx10 eq./ha |
| Pivô 19, ciclo (36.420 kg em 75,11 ha) | 0,48 t/ha | 484,89 | é o Padrão | 8,08 | 48,49 cx10 eq./ha |
| Mamão ponderado (96.740 kg em 137,9 ha) | 0,70 t/ha | 701,52 | é o Padrão | 11,69 | a média simples daria 722,78 kg/ha (errada) |
| Meta do mamão | 50 t/ha/ano | 50.000 kg/ha/ano | é o Padrão | 833,33 /ano | 5.000 cx10 eq./ha/ano |
| Meta da soja T1-A | 64 sc/ha | 3.840 | 3,84 | é o Padrão | — |
| Meta digitada 3,85 t/ha (soja) | 64,17 sc/ha | 3.850 | 3,85 | é o Padrão | — |

Casos injetados no teste, com o estado montado como em `cafe_apurar_unit.js` (o que for injetado no `PRDC` volta ao original no fim do bloco):
- **K-U01:** 6.000 kg/ha = 6 t/ha = 100 sc60 eq./ha.
- **K-U02:** algodão em caroço 4.526 kg/ha = 301,73 @/ha; arroz RS 9.044 kg/ha = 180,88 sc/ha (50 kg) = 150,73 sc60 eq./ha.
- **K-U07 (contraprova i):** cultivo anual de soja de 10 ha (cultivo `tu1` injetado no `PRDC.cult`), com duas O.S. de colheita de 10 ha apontados cada e cargas de 10.000 kg e 5.000 kg a 14 % de umidade e 1 % de impureza. Resultado: 1.500 kg/ha = 1,5 t/ha = 25 sc/ha. O valor errado seria 750.
- **K-U08 (contraprova ii):** parcelas distintas de 10 ha com 10.000 kg e de 5 ha com 15.000 kg dão 1.666,67 kg/ha = 1,67 t/ha = 27,78 sc/ha. A média das taxas daria 2.000, que é o valor errado.
- **K-U09:** café do C1 (o caso da COLH-C01): 12.000 L, 6.000 kg pesados e 5 ha apontados.
  - Padrão: "sc/ha a apurar · 2.400 L/ha de Café da roça".
  - kg/ha: 1.200 kg/ha de Café da roça.
  - sc60 eq./ha: 20 sc60 eq./ha de Café da roça.
  - Sem peso: só 2.400 L/ha, com as opções de massa indisponíveis.
- **K-U10:** 0 kg em 10 ha = "0,00 kg/ha"; 5.000 kg com área 0 = "sem área colhida apontada"; sem área e sem produção = "—".
- **K-U11:** depois de 20 trocas, os textos são idênticos aos da primeira volta e o JSON do cenário também.
- **K-U12:** rascunho pela meta pelo conversor = o de hoje: Pivô 2 (37,75 ha × 50 t/ha/ano) = 36.298,076923 kg/semana (U11c).
- **K-U13 e K-U14** (contas da revisão): meta com até 2 casas ("3,84 t/ha", "64,17 sc/ha") e um arredondamento só, sem mudar os textos da tabela acima.

## 7. Passos de implementação (cada um deixa o protótipo funcionando)
1. **P1 · Conversor e regras, sem tela:**
   - `producao.js`: bloco `prUnp*`; `op` em `prPrtvTxt` e `prPrtvResTxt` (com `op`, delegam a `prUnpTxt`); `litros`, `kgOk` e `estim` em `prProdOS`, `prPasse` e `prResultado`; desvio em kg/ha lendo `un_meta`; rascunho "pela meta" pelo `prUnpKgHa`; guarda em `prPonderada`.
   - `dados_cad.py`: algodão no `CULTURA_UN`.
   - `dados_producao.py`: `unAlt`.
   - `producao_unit.js`: bloco U20 (aceites a, b, d, e, f, i, mais a parte de unidade do c; K-U12).
   - Ao fim do P1, todos os testes atuais continuam verdes: `op` ausente dá o texto de hoje, `prtv` continua no Padrão e U11c continua 36.298,076923.
2. **P2 · COLH:**
   - `g2unidPref` e `g2unidSet` no bloco `<perfis>`; `r.ordk` em `g2key` e `g2fkeys`; seletor na barra da `g_tal`; linha, total da cultura, painel e cartões; café da roça (R-U05); meta com até 2 casas.
   - Novas expectativas, com o motivo no commit ("R-U05: a parte do fruto aparece em L/ha com o produto; o beneficiado continua a apurar"):
     - C01a: `s.prtv` = "sc/ha a apurar · 2.400 L/ha de Café da roça"; `colh` e `ref` como hoje.
     - C01b: `colh` e `ref` iguais aos da C01a; `s.prtv` = "sc/ha a apurar · sem área colhida apontada".
     - C01f: kv Produtividade = "sc/ha a apurar · 2.400 L/ha de Café da roça"; o resto como hoje.
     - C01k: `s.prtv` = "sc/ha a apurar · 4.000 L/ha de Café da roça" (20.000 L em 5 ha).
     - Não mudam: C01c, C01d, C01e, C01g (mensagem, sem `op`), C01h, C01i, C01j, C01l, C01m, C01n (carga), C01o e C01p.
   - `producao_fluxo_test.py` ganha o modo `unid` (COLH), incluído na lista `MODOS`.
3. **P3 · SAF:**
   - O SAF carrega o conversor; `KG_UN` vira `prUnpKgHa` (linha com unidade sem massa fica fora da conta do Custo R$/kg, como hoje).
   - Seletor na `g_cult`; Meta na coluna (`r.ordk.meta`), no painel e no Dividir.
   - Rascunho: `self.g2openDraft` põe no rascunho a meta na unidade da preferência e guarda a origem (`_m0`, `_u0`), o texto mostrado (`_t0`) e a unidade do rascunho (`_un`); `dvRow` faz o mesmo por linha. No Salvar, `cultCheck` guarda o rascunho e `cultAfter` (e `dvSave`, linha a linha) grava `{_m0, _u0}` se o texto do campo é `_t0`, senão {número digitado, `_un`}. O campo "Unidade da meta" mostra `_un`.
   - `unMetaDe` aceita a unidade informada que for válida; ajuda e aviso do CD-02 dizem "Padrão da cultura".
   - Modo `unid` (parte SAF e a prova entre telas); a guarda de nomes passa a cobrir o safra.js.
4. **P4 · Fechamento:** `varredura.py`, `acoes_duplicadas.py`, a bateria do módulo e a dos vizinhos, `docs/STATUS.md` e o artefato com uma linha do que mudou.

**Bateria por passo** (com `SAFRION_DADOS=sintetico`, dentro de `gen37/`):
1. `python3 producao_unit_test.py`;
2. `python3 cafe_apurar_test.py unit` (sem o modo, o script abre também o navegador);
3. `python3 build.py > /tmp/UNID-PROD-build.log; grep -c FALHA /tmp/UNID-PROD-build.log` (precisa dar 0);
4. `python3 montar_render.py`;
5. no navegador, um teste por vez: `env CHROME_BIN=/tmp/cloudchrome/chrome flock /tmp/cdpU.lock env CDP_GL=1 timeout 900 python3 <teste>`, com `varredura.py`, `../ferramentas/acoes_duplicadas.py . /tmp/UNID-PROD-dup.json`, `producao_fluxo_test.py unid`, `producao_fluxo_test.py celular`, `cafe_apurar_test.py nav`, `saftest.py` e `tabelas_saf_test.py`. Não usar `python3 cafe_apurar_nav.py` direto: o arquivo não tem `__main__` e sai 0 sem abrir o navegador.

Os vermelhos conhecidos da base (lista da tarefa, não reexecutada aqui) ficam listados no log, sem esconder nenhum. Antes do P1, roda-se a bateria uma vez na base `47ff754` e o log fica guardado para comparar.

**Modo `unid` do `producao_fluxo_test.py`:**
1. COLH a 1440 px: a partir da busca da tabela, Tab chega ao seletor sem sair da barra. ArrowDown escolhe kg/ha, e as células do Mamão passam a kg/ha. Enter não muda nada (cenário, painel e filtros iguais).
2. A 390 × 844: o seletor tem pelo menos 44 × 44 px, não há rolagem horizontal e os cartões aparecem em kg/ha.
3. Pesar a CG-2108 no CARGA (um comando real grava o cenário) e guardar S0 = todas as chaves do localStorage, menos `safrion.pref.unidprod:*`. No COLH, abrir o Pivô 19 e digitar a perda em "Publicar previsão" sem publicar (rascunho). Aplicar o filtro rápido "Em colheita", filtrar a coluna Produtividade pelo valor do Pivô 19 e ordenar por ela. Pôr o foco no seletor e fazer 20 trocas pelo teclado (10 × ArrowDown, ArrowUp). Esperado: S1 = S0; o filtro rápido, o filtro por valor (o Pivô 19 continua na lista), a ordem, o rascunho e o `activeElement` continuam os mesmos.
4. Ir ao PROD e voltar: o seletor e as células continuam em kg/ha.
5. Perfil Caio: aparece o Padrão. Voltando à Ana: kg/ha.
6. Pivô 19: a mesma unidade na linha, no painel (kv Produtividade e passes) e no cartão; o mesmo número do ciclo na linha, no kv e no cartão.
7. Selecionar uma linha de soja e escolher kg/ha. A Referência do T1-A mostra "meta 3.840 kg/ha", e o SAF mostra "3.840 kg/ha" na Meta do T1-A.
8. SAF:
   - depois de 20 trocas, `meta` e `unm` das linhas ficam intactos;
   - com t/ha escolhido para a Soja, salvar o painel do T1-A sem mexer na meta (o campo mostra 3,84) mantém {64, sc/ha}; o mesmo no Dividir do T1, linha a linha;
   - com o painel aberto e 3,9 digitado em t/ha, trocar o seletor para kg/ha não muda o campo (3,9 t/ha); salvar grava {3,9, t/ha};
   - digitar 3,85 com t/ha escolhido grava {3,85, t/ha}, e a tabela mostra 64,17 sc/ha quando o Padrão é escolhido.
9. Mapa: se a camada "Colheita e produtividade" estiver na barra, a mesma unidade aparece nela. Se não estiver, o teste imprime "PENDENTE (DEC-0910-36)".

## 8. Critérios de aceite

| AC | Critério | Teste que prova |
|---|---|---|
| AC-a | 6.000 kg/ha ↔ 6 t/ha ↔ 100 sc60 eq./ha, nos dois sentidos | `producao_unit.js` U20a (K-U01) |
| AC-b | Unidade com massa declarada: algodão em @ de 15 kg; arroz RS em sc de 50 kg com a opção sc60 eq. separada; cx 10 kg do mamão vinda de `EMB_PACK` | U20b (K-U02); U20b2 (opções do mamão) |
| AC-c | 20 trocas repetidas não derivam e não mudam o cenário. Antes da medição, um comando real grava o cenário (pesagem da CG-2108); depois das trocas, todas as chaves do localStorage, menos `safrion.pref.unidprod:*`, ficam idênticas byte a byte. As linhas do SAF ficam com `meta`/`unm` intactos, inclusive salvando o painel e o Dividir sem mexer na meta com outra unidade na tela; o rascunho aberto não muda de unidade | U20c (K-U11, JSON igual); `producao_fluxo_test.py unid` passos 3 e 8 |
| AC-d | Soja, milho, mamão, algodão e café sem trava arbitrária: todas as opções de massa valem no estágio de massa; o coco em frutos tem a massa indisponível, com o motivo | U20d |
| AC-e | Não apurado ≠ zero ("0,00 kg/ha"); área 0 mostra pendência, sem divisão (K-U10) | U20e |
| AC-f | Volume sem equivalência não vira massa: café só em L mostra L/ha e a massa indisponível; não existe caminho de L para kg | U20f (K-U09); C01a, C01b, C01f e C01k novos |
| AC-g | Teclado (a partir da busca, Tab chega ao seletor; setas trocam a opção; Enter não dispara ação); em 390 px o alvo tem pelo menos 44 px e não há rolagem horizontal; a preferência volta ao voltar à tela e muda com o perfil (Caio vê o Padrão, Ana vê kg/ha) | `unid` passos 1, 2, 4, 5 |
| AC-h | A mesma unidade aparece na tabela, no painel e no cartão do mesmo contexto (perfil × cultura), e também entre telas, com o mesmo número de casas: soja em kg/ha no COLH aparece em kg/ha no SAF. Mapa: pendente da DEC-0910-36; o teste imprime "PENDENTE", e isso não conta como OK | `unid` passos 6, 7, 9 |
| AC-i | Contraprovas de agregação: (i) 1.500 kg/ha, não 750; (ii) 1.666,67 kg/ha, não 2.000; (iii) `prPonderada` lança o erro da R-U08 com café da roça e beneficiado e com algodão em caroço e pluma | U20i1 (pelo `prResultado`, K-U07), U20i2 (K-U08), U20i3 |
| AC-j | Fonte única: `KG_UN` e o `× 1000` do rascunho sumiram; nenhum nome do producao.js é redefinido no safra.js; filtro, filtro por valor, ordem, rascunho (`pr_form`) e foco ficam depois da troca | `producao_unit_test.py`; `unid` passo 3 |
| AC-k | Bateria sem vermelho novo: build com 0 FALHA, varredura e ações duplicadas iguais às da base | logs do P4 |

## 9. Fora de escopo, com a condição de retorno

| Item | Por que fica fora | Volta quando |
|---|---|---|
| Camada Colheita e produtividade do Mapa | Não existe na barra e os dados dela são fixos. A DEC-0910-36 é a frente que traz a camada de volta (D-U02) | A DEC-0910-36 entrar na branch: a camada chama `prUnpInd` e lê a mesma preferência, e o AC-h ganha o mapa |
| Relatórios de Gestão | Telas ocultas com números fixos | Algum relatório passar a ler a produção do estado (CONTROLE-02) |
| Produção, estoque e oferta em outras unidades | Não são produtividade; mudar exigiria regra de estoque e de pedido | O proprietário pedir unidade de exibição para a produção |
| Escala de 12 casas para taxas (PRD 10.0) | O protótipo usa as 6 casas do `producao.js` | No software real (`packages/domain`) |
| Recebimento de café da roça sem balança (só L) | Hoje o recebimento exige bruto e tara (`producao.js:363-364`). A regra R-U05 já cobre o caso só em L | A fazenda receber café sem pesagem |
| Massa verde × seca (silagem) | Não há cultura de forragem no catálogo. A guarda da R-U08 já impede somar os dois | Uma forragem entrar no `CULTURA_UN` |
| Alinhar `UNID_PROD` do CD-02 ao `CULTURA_UN` | É frente de Cadastros (D-03 da COLH) | Revisão do CD-02 |
| A meta editada no SAF chegar à COLH | Pré-existente: o `PRDC.cult` vem da semente na geração e o SAF guarda as linhas só no estado da página (RC-17). A COLH já lê `{meta, un_meta}` pelo conversor | O SAF gravar o cultivo no estado único: a COLH passa a ler a meta de lá, sem mudar a regra |

## 10. Revisão por contraexemplo (10/10/2026)
Feita contra o código da base `47ff754` e o PRD v3.11. Severidade pelo PRD 22.1 (ENG-003). Cada achado foi corrigido nesta especificação.

| ID | Sev. | Contraexemplo | O que mudou |
|---|---|---|---|
| RC-01 | S2 | Com o painel do SAF aberto e 3.900 digitado em kg/ha, trocar o seletor para t/ha deixaria o número com "t/ha" ao lado (R-U11 manda preservar o rascunho): salvar gravaria 1.000 vezes a meta | Unidade do rascunho fixada ao abrir (§3.2, R-U06, passo 8) |
| RC-02 | S2 | O formulário do g2 grava `r.v.meta = g2num(draft.meta)` em todo Salvar (`g2lib.js:131-132`) e não mexe em `unm`: mostrando 3.840 (kg/ha) no campo, salvar sem mexer gravaria {3840, sc/ha}; o `dvSave` regrava todas as parcelas. O teste "salvar sem mexer mantém {64, sc/ha}" passava no Padrão sem provar nada | Mecanismo do P3 (`g2openDraft`, `_m0/_u0/_t0/_un`, linha a linha no Dividir); teste com t/ha escolhido e no Dividir |
| RC-03 | S3 | "A coluna ordena pelo kg/ha" não era verdade: Produtividade é texto e ordena por `localeCompare` (executado no node: "1.200,00 kg/ha" vem antes de "484,89 kg/ha"); a Meta do SAF (`t: 'num'`) ordena por `r.v.meta`, em unidades misturadas depois do R-U06 | `r.ordk` lido por `g2key` (R-U11, §0) |
| RC-04 | S3 | O filtro por valores da coluna usa o texto da célula (`g2fkeys`): filtrado "0,48 t/ha · ciclo parcial", a troca para kg/ha esvazia a tabela, contra "preserva filtros" | A mesma `r.ordk` como chave do filtro; o menu mostra o texto (passo 3) |
| RC-05 | S3 | O seletor estava em dois lugares ("tools da grade" e "ao lado da escolha de Visão"), e o aceite "até 3 Tabs a partir da Visão" não passa com ele na barra (busca e seis chips de situação antes, `engine.py:1191-1199`). "Enter abre a lista" não é observável num `<select>` nativo no navegador sem tela | Barra da tabela nas duas telas; Tab a partir da busca; Enter sem efeito (§3, passo 1, AC-g) |
| RC-06 | S3 | `cafe_apurar_unit.js:63` é a C01k, não a C01n; a C01n é o texto da carga, que pela D-U10 não pode mudar. As novas expectativas não estavam escritas (a C01b deixaria de comparar igual) | C01a, C01b, C01f e C01k com o texto novo; lista do que não muda (P2, AC-f, D-U11) |
| RC-07 | S3 | `python3 cafe_apurar_nav.py` não tem `__main__`: sai 0 sem testar nada (falso verde). `python3 cafe_apurar_test.py` sem modo abre o navegador no passo "sem navegador" | `cafe_apurar_test.py unit` e `cafe_apurar_test.py nav` (bateria) |
| RC-08 | S3 | `g2unidPref` no g2lib.js fora do bloco `<perfis>` não existe nos testes sem navegador (`cafe_apurar_test.py` e `producao_unit_test.py` montam só esse bloco): o P2 deixaria `prTalRow` com ReferenceError e a bateria do C01 vermelha | Preferência dentro do bloco `<perfis>`; sem localStorage, Padrão (§0, §5) |
| RC-09 | S3 | Terceira tabela de fator não mapeada: o rascunho "pela meta" converte com `× 1000` fixo (`producao.js:174`) e com a massa do Padrão (`:176`), supondo `un_meta` = Padrão | `prUnpKgHa(k.cultura, k.meta, k.un_meta)`; K-U12 prova o mesmo número (executado) |
| RC-10 | S3 | A COLH mostra a meta com `prFmtT(x, 1)` e o SAF com até 2 casas: o T1-A em t/ha apareceria "3,8 t/ha" na COLH e "3,84 t/ha" no SAF (AC-h); a meta 64,17 sc/ha viraria "64,2" | Meta com até 2 casas em toda tela (R-U02); as metas da semente são inteiras, nenhum texto atual muda (K-U13, executado) |
| RC-11 | S4 | Mapa incompleto: o CD-01 (no menu) mostra a meta das parcelas; o PL-01 tem "Meta (hipótese)" (oculto); a ajuda do CD-02 diz que o Planejar safra usa só a unidade do cadastro; "CD-02 continua definindo o Padrão" não descrevia o código (a massa vem do `CULTURA_UN`) | §0 corrigido; CD-01 sem mudança (D-U21); ajuda do CD-02 no P3 |
| RC-12 | S4 | O contrato pede produto e base junto do número; a v1.0 reduziu isso sem decisão registrada e sem fixar o texto da célula (o teste não tinha string a comparar) | Formato na R-U03; D-U18 |
| RC-13 | S4 | Ambiguidades: `est` já é a unidade de estoque no domínio (`u.est`) e a v1.0 usava `est` para estágio e para estimativa; "0 kg/ha" × 2 casas fixas; "sem área apontada" (painel) × "sem área colhida apontada"; `lado` da laranja e período "/ano" com outra unidade; contexto "registro selecionado" no SAF (a grade tem seleção em lote) | `estagio` e `estim`; "0,00 kg/ha"; um texto de pendência; R-U03; contexto = painel aberto |
| RC-14 | S4 | kg/ha arredondado em 6 casas e depois dividido pela massa, de novo em 6 casas: dois arredondamentos, contra o PRD 10.0 | Número na unidade = base ÷ (área × massa), um arredondamento (R-U02, §5); os textos da semente não mudam (K-U14, executado) |
| RC-15 | S4 | "`prPonderada` recusa" sem dizer como (número, nulo ou erro) nem a chave de agregação; nada impedia mudar `prtv` para kg/ha, o que quebraria U03 e U06 | Erro com motivo e chave = produto do estágio (R-U08); `prtv` no Padrão (§0, §5) |
| RC-16 | S4 | Testes: `tu1` injetado no `PRDC` sem voltar ao original; modo `unid` fora da lista `MODOS`; "20 trocas" sem sequência (ArrowDown parado na última opção); "o mesmo número na linha e nos passes" mistura passe e ciclo | Restaurar o `PRDC`; `MODOS`; 10 × (ArrowDown, ArrowUp); passo 6 |
| RC-17 | S3 | Pré-existente, fora deste módulo: a meta editada no SAF não chega à COLH (o `PRDC.cult` vem da semente; o SAF não grava no estado único). Dado que não se integra | Registrado no §9, com a condição de retorno |
