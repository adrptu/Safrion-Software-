# Unidade de produtividade selecionável · especificação v1.0

**Pedido do proprietário (Adrianus, 10/10/2026, literal, trazido pelo Codex em UNIDADES-PROD-20261010-01, PR #47, comentário 6093638004):** «Coloque opções para todas culturas em kg/ha, ton/ha, sc 60 kg/ha, etc.» O Codex aceitou a direção em 6093701812 com duas precisões: a base kg/ha vale só para o indicador em massa (item 4 do contrato) e a agregação não conta duas vezes a mesma área (item 6).

- **Rótulo:** especificado. Nenhum código foi alterado. "(executado)" marca o que saiu de comando rodado em 10/10/2026 nesta worktree: `python3 docs/unidades-produtividade/verificacao/contas.py` (FALHAS: 0), as buscas do §0 (`grep` de sc/ha, t/ha, kg/ha, produtividade, `prPrtv`, `un_meta`, `KG_UN`) e a checagem de nomes globais (safra.js, ocupacao.js, cal01.js e g2lib.js contra producao.js e cenario.js: nenhuma colisão).
- **Base:** `47ff754` (branch `claude/v44-unidades`). `gen37/` = `tools/prototipo/v37/gen37/`. PRD = `Safrion-Software-/docs/PRD.md` v3.11, "l.N" = linha. Decisões tomadas sem o proprietário: `DECISOES.md` (D-Unn). O PRD não é reaberto: o requisito fica registrado em `DECISOES.md`, fica fora da v55 e entra na versão seguinte (contrato, item 8).
- **Fontes reaproveitadas, não repetidas:** a unidade de mercado e a massa de cada cultura vêm de `docs/culturas/UNIDADES-DE-MERCADO.md` (DEC-0510-03). Área colhida, produtividade, referência, café e "a apurar" vêm de `docs/colheita/ESPECIFICACAO.md` (R-02, R-04, R-05, R-09 e COLH-C01). Do PRD valem 10.0 (decimal, l.4237), 45.4 (no café, a quantidade tem base declarada e não há fator universal, l.7648) e 62.2/62.3 (a saca exige massa explícita, as passagens legítimas somam e produtos e estados não se misturam, l.9188 e l.9194-9196).

```text
ID / resultado útil / persona: UNID-PROD / ler e planejar a produtividade em kg/ha, t/ha, sc 60 kg/ha ou na unidade do mercado, sem conta de cabeça / agrônoma, gestor, encarregado de colheita
Requisitos do PRD e fora do escopo: DEC-0510-03; PRD 10.0, 45.4, 62.2, ENG-011, ENG-013; fora: §9
Autor / revisor / integrador: Claude / Codex / integrador da branch única
Base / arquivos sob responsabilidade: 47ff754 / producao.js (bloco novo e os pontos do §0), g2lib.js (preferência), areas/producao.py (COLH), safra.js e areas/processo_safra.py (meta), dados_cad.py e dados_producao.py (catálogo), testes do §7
Aceite e comando de verificação: §8; bateria do §7
Estado / impedimento / próximo passo: especificado / nenhum (D-U01 a D-U17 valem até o proprietário mudar) / P1
```

## 0. Mapa do existente (busca executada)

| Fica (reusar sem mudar o comportamento) | Onde |
|---|---|
| Unidade de mercado por cultura (fonte única), com a massa da unidade em kg, a base física e o estágio de campo do café (`campo: 'L'`, `proc: 'Café da roça'`) | `dados_cad.py:41-53` (`CULTURA_UN`) → `PRDC.un` (`dados_producao.py:59`) |
| Massa declarada da caixa do packing (caixa de 10 kg do mamão) | `dados_cad.py:166-167` (`EMB_PACK`) |
| Produtividade = produção na base física ÷ área colhida. No perene, a área é a do cultivo; no anual, mín(área do cultivo, Σ ha apontados) | `producao.js:133` (`prPasse`), `:140-150` (`prResultado`) |
| Ponderada Σ produção ÷ Σ área; café a apurar fica fora da conta | `producao.js:161-162` (`prPonderada`) |
| Café a apurar como estado próprio (nunca "0 sc") | `producao.js:120-127`, `:153-158` |
| Decimal com 6 casas por BigInt e texto pt-BR | `producao.js:9-30` (`prM`, `prDiv`, `prFmt`, `prFmtT`) |
| Perfil de quem usa a tela | `g2lib.js:260-267` (`G2_PERFIS`, `g2perfil`) |
| Meta do cultivo guardada como valor + unidade | `dados2.py:63-82`, `dados_lagoa_safra.py:69-70` (`meta`, `un_meta`) |

| Muda | Arquivo:linha | Passo |
|---|---|---|
| Conversor único (`prUnp*`, §5) num bloco novo depois da produtividade. `prPrtvTxt` e `prPrtvResTxt` ganham o parâmetro `op`; o valor padrão mantém o texto atual | `producao.js:47-50`, `:158` | P1 |
| `prProdOS` soma também os L e os kg do fruto de todas as origens de café e marca as origens estimadas | `producao.js:122-127` | P1 |
| O desvio contra a meta passa a ser calculado em kg/ha pelo conversor (mesmo número na semente) | `producao.js:147`, `:149` | P1 |
| Guarda de agregação: produto ou estágio diferente não soma | `producao.js:161` | P1 |
| Algodão em caroço e algodão em pluma (@ de 15 kg) entram no catálogo, sem nenhuma fazenda | `dados_cad.py:41-53` | P1 |
| `PRDC.unAlt`: unidades com massa declarada por cultura, lidas de `EMB_PACK` | `dados_producao.py:59` | P1 |
| Preferência por perfil × cultura | `g2lib.js`, depois da `:267` (`g2unidPref`, `g2unidSet`) | P2 |
| COLH: seletor no cabeçalho do bloco "Previsão e resultado por talhão"; linha, total da cultura, painel e cartão na unidade escolhida | `areas/producao.py:504-506` (bloco), `:540-546` (`prTalRow`), `:550-552` (`prGrpNum`), `:562` (`pdT`), `:597-611` (painel), `:631-634` (cartões) | P2 |
| Testes cuja expectativa muda pela regra R-U05 (o motivo vai no commit) | `cafe_apurar_unit.js:22-25` (C01a, C01b), `:34` (C01f), `:63` (C01n) | P2 |
| SAF: o conversor único substitui a segunda tabela de fator | `safra.js:591-596` (`KG_UN`, `prodColheita`) | P3 |
| SAF: meta na unidade escolhida (coluna, painel e Dividir), guardando a unidade informada | `safra.js:529`, `:747`, `:819`, `:827`, `:853-855`, `:869-887`; `areas/processo_safra.py:46`, `:61`, `:351-352` | P3 |
| SAF carrega o conversor (`cenario.js` + `PRDC` + `producao.js`) sem ler nem gravar o cenário | `areas/processo_safra.py:229` | P3 |
| A guarda "nomes de producao.js não são redefinidos" passa a cobrir também o safra.js | `producao_unit_test.py` (lista `outros`) | P3 |

**Sai:** `KG_UN` (`safra.js:591`), a segunda tabela de conversão.
**Mapeado e sem mudança (§9):**
- **IN-04:** a camada "Colheita/produtividade" está fora da barra (`areas/inicio.py:100`, `LAYS_F2`). Os dados fixos `COL` (`:193-198`) não entram no `MDATA` (`:488`); `_proxima` (`:215`) e `engine.farm_layers` (`engine.py:765-799`) não têm uso.
- **PROD e CARGA:** não mostram produtividade (nenhum `prPrtv` em `PROD_JS` e `CARGA_JS`, executado). A mensagem do recebimento (`producao.js:397`) mostra o passe no Padrão.
- **Gestão:** os textos de `gestao.py:13-14` e `:172-174` são fixos e a tela fica oculta.
- **"5,8 sc/ha":** em `comercial.py:454` é a troca do barter, um preço, não uma produtividade.
- **CD-02:** continua definindo o Padrão (`cad_culturas.py:73`, `:85`; `dados_cad.py:30-32`).
- **Doses em kg/ha e L/ha:** `campo.py`, `agronomia.py` e `mobile.py` mostram doses, não produtividade.

## 1. Missão e princípios
1. A pessoa lê a produtividade na unidade em que decide (kg/ha, t/ha, sc 60 kg/ha ou a do mercado), sem fazer conta de cabeça e sem confundir produto.
2. Trocar a unidade só muda a exibição. Nenhum fato muda: cenário, meta, área e estoque ficam como estão.
3. Uma fórmula só (ENG-011): toda conversão passa pelo conversor de `producao.js`, que lê a massa da unidade no cadastro (`CULTURA_UN`, `EMB_PACK`).
4. Massa só converte massa. Litro, fruto ou caixa sem massa declarada nunca vira kg.
5. O produto ou o estágio aparece junto do número sempre que não for o produto-base da cultura ou que a unidade for uma equivalência.
6. Essencial: um seletor por tabela e nenhuma tela, menu ou cadastro novo.

## 2. Menu e telas, antes → depois

| Tela | Antes | Depois | Natureza |
|---|---|---|---|
| Produção › Previsão e colheita (`COLH`), visão Por talhão | Produtividade e meta na unidade da cultura | Seletor "Unidade de produtividade · ‹cultura›" no cabeçalho do bloco. Linha, total da cultura, painel e cartão aparecem na unidade escolhida | planejamento + controle |
| Agrícola › Planejar safra (`SAF`), Talhões e cultivos | Meta na unidade de mercado, sem escolha | O mesmo seletor na barra da tabela. Coluna Meta, painel do cultivo e Dividir aparecem na unidade escolhida | planejamento |
| Mapa (`IN-04`) | Camada Colheita e produtividade fora da barra | Igual. Quando a camada voltar (DEC-0910-36), ela usa o mesmo conversor e a mesma preferência (D-U02) | controle |
| COLH Por semana, CARGA, PROD e app | Produção e estoque na unidade da cultura | Igual: essas telas não mostram produtividade (D-U10) | — |

O menu não ganha item.

## 3. Telas

**Seletor (igual nas duas telas):**
- **Controle:** `<select>` nativo com `<label>` "Unidade de produtividade · Mamão Formosa", no espaço `tools` da grade g2 (`engine.grid`, `tools=`). No COLH fica ao lado da escolha de Visão. Tem o mesmo visual dos seletores do Mapa (`inicio.py:1250`).
- **Contexto:** a cultura do registro selecionado. Sem seleção, a primeira cultura visível na lista, já com os filtros aplicados. O rótulo diz o nome da cultura.
- **Opções:** as da R-U03. Opção indisponível vira `<option disabled>` com o motivo. Se a escolha guardada não vale para o estágio mostrado, uma nota curta aparece abaixo do seletor.
- **Teclado:** Tab chega ao seletor, as setas trocam a opção e Enter abre a lista.
- **390 px:** altura mínima de 44 px, fonte de 16 px (evita o zoom do iOS) e quebra de linha.
- **Não é ação:** não muda a ação primária, não abre painel e não limpa filtros, rascunho (`pr_form`, `pr_ferr`, formulário do SAF) nem foco (R-U11).

### 3.1 COLH · Previsão e resultado por talhão
**Pergunta:** a mesma de hoje. Só mudam as colunas de produtividade (exemplo com kg/ha escolhido para o Mamão Formosa, números da §6):

| Coluna | Antes | Depois |
|---|---|---|
| Produtividade (Pivô 19) | 0,48 t/ha · ciclo parcial | 484,89 kg/ha · ciclo parcial |
| Referência · desvio | meta 50 t/ha/ano · ciclo aberto | meta 50.000 kg/ha/ano · ciclo aberto |
| Linha da cultura | 0,70 t/ha ponderada sobre 137,9 ha colhidos | 701,52 kg/ha ponderada sobre 137,9 ha colhidos |

- **Colunas que não mudam:** Área, Previsão, Colhido e Situação continuam na unidade da cultura, porque são produção e não taxa (D-U10).
- **Ordenação:** a coluna Produtividade ordena pelo valor em kg/ha, então a ordem é a mesma em qualquer unidade.
- **Café com parte a apurar:**
  - Padrão: "sc/ha a apurar · 2.400 L/ha de Café da roça".
  - kg/ha: "kg/ha a apurar · 1.200 kg/ha de Café da roça".
  - Sem peso do fruto: a célula mostra só os L/ha e a nota do seletor diz "kg/ha indisponível para Café da roça: falta peso ou conversão medida".
- **Painel:**
  - Na unidade escolhida: a meta do subtítulo, o kv Produtividade, os passes, o Resultado e o rascunho "pela meta".
  - O kv "Unidade (DEC-0510-03)" passa a "Unidade de produtividade", com o texto "kg/ha · Padrão da cultura: t/ha".
- **Ação primária e estados do talhão:** iguais aos de hoje (COLH §3.1).
- **Celular:** os cartões do talhão e da cultura mostram o número na unidade escolhida. O seletor fica no cabeçalho do bloco, com alvo de 44 px. Não há rolagem horizontal.

### 3.2 SAF · Talhões e cultivos
**Pergunta:** a mesma de hoje. A coluna Meta mostra a unidade junto do número (por exemplo, "3.840 kg/ha" no T1-A com kg/ha escolhido para a Soja). O talhão dividido continua mostrando "por parcela".
- **Painel do cultivo:** o campo "Meta de produtividade" mostra o valor na unidade escolhida, com a unidade ao lado. O campo só de leitura "Unidade da meta" passa a "kg/ha · Padrão da cultura: sc/ha (60 kg)".
- **Dividir:** cada parcela mostra a meta na unidade da preferência da cultura dela. A folha não tem seletor próprio.
- **Salvar:** se o campo da meta mudou, guarda {valor digitado, unidade escolhida}; se não mudou, guarda o que já estava (R-U06).
- **Sem mudança:** ação primária, etapas e estados do SAF. O Custo R$/kg dá o mesmo valor, agora calculado pelo conversor.
- **Celular:** igual ao SAF de hoje, mais o seletor com 44 px.

## 4. Regras (testáveis, com o dano evitado)

| # | Regra | Dano que a regra evita |
|---|---|---|
| R-U01 | Conversor único em `producao.js` (`prUnpOpcoes`, `prUnpMassa`, `prUnpKgHa`, `prUnpInd`, `prUnpTxt`, §5). Nenhuma tela multiplica ou divide unidade por conta própria; o `KG_UN` sai | Duas tabelas de fator divergentes (o arroz RS contado com saca de 60 kg dá 17 % menos sacas) |
| R-U02 | A base do indicador em massa é kg/ha: kg medidos ÷ área colhida (COLH R-02 e R-04), com 6 casas e meio para cima. Na tela, base ÷ massa da unidade, arredondada só na exibição (2 casas, pt-BR, unidade na célula). Nunca se converte um texto já convertido | Deriva depois de trocas repetidas; tabela e painel com números diferentes |
| R-U03 | Opções:<br>• "Padrão da cultura", com a unidade concreta e a massa no rótulo (ex.: "Padrão da cultura · sc/ha (60 kg)");<br>• kg/ha;<br>• t/ha;<br>• "sc 60 kg/ha (equivalência)";<br>• as unidades com massa declarada do produto em `CULTURA_UN` e `EMB_PACK` (ex.: "cx 10 kg/ha (equivalência)").<br>Sai a opção igual ao Padrão em todos os estágios da cultura (soja e milho ficam sem sc 60; o mamão fica sem t). Na célula a unidade aparece como "sc60 eq./ha" e "cx10 eq./ha". O período do Padrão fica junto ("kg/ha/ano") | A pessoa precisar deduzir a unidade; confundir a equivalência de 60 kg com a saca do produto (arroz RS de 50 kg; PRD 62.2) |
| R-U04 | A equivalência de 60 kg não supõe embalagem e não muda a saca do pedido, do contrato nem do estoque: `prUn`, `prQ` e `prEstTxt` ficam intocados | Venda ou estoque contados em sacas erradas |
| R-U05 | Massa só vem de massa. kg, t, sc, @ e cx valem quando a produção do estágio é massa pesada na balança.<br>Café da roça: o kg do fruto só vale se todas as origens do resultado têm peso líquido maior que zero. Sem isso, a tela mostra L/ha e as opções de massa ficam indisponíveis com o motivo "Falta peso ou conversão medida". O mesmo vale para coco e abacaxi, contados em frutos.<br>Não existe fator de L para kg nem de L para sc. Com massa do fruto, o indicador diz "de Café da roça", nunca café beneficiado | Saca presumida por fator fixo (PRD 45.4; COLH R-09) |
| R-U06 | A meta editável guarda o valor e a unidade informados (`meta`, `unm`). O kg/ha sai de valor × massa (multiplicação exata) a cada leitura. Salvar sem mexer no campo não regrava a meta.<br>A unidade informada pode ser o Padrão ou uma unidade de massa válida para a cultura. Ao trocar a cultura, a unidade só fica se continuar válida.<br>Não há migração: as metas atuais já estão no Padrão | Meta que muda sem ninguém editar; deriva |
| R-U07 | Estados do indicador:<br>• medido: mostra o número;<br>• zero medido: "0 kg/ha";<br>• a apurar: café beneficiado sem rendimento medido, nunca mostrado como "0";<br>• pendência de área: produção maior que zero com área colhida 0 mostra "sem área colhida apontada", sem dividir;<br>• não colhido: "—";<br>• estimativa: se alguma origem tem participação estimada (`modo: 'estimada'`), a palavra "estimativa" vem junto | Decidir sobre zero falso ou sobre divisão inválida |
| R-U08 | Agregação:<br>• entre talhões ou parcelas distintas do mesmo produto e estágio: Σ produção ÷ Σ área (`prPonderada`);<br>• passagens do mesmo cultivo: somam a produção e usam a área do cultivo uma vez só (`prResultado`; perene = área do cultivo, anual = mín(área, Σ ha));<br>• `prPonderada` recusa produtos ou estágios diferentes (algodão em caroço × pluma, café da roça × beneficiado, massa verde × seca quando existir);<br>• a linha da cultura agrega só o estágio-base, e os talhões em outro estágio ficam "fora da conta" | 750 kg/ha em vez de 1.500; média de médias; café da roça somado com café beneficiado |
| R-U09 | Planejado e realizado comparam na mesma base: desvio = (kg/ha real − kg/ha da meta) ÷ kg/ha da meta, os dois pelo conversor. Produto ou estágio diferente (café da roça contra uma meta de café beneficiado) não compara e mostra "a apurar" | Desvio falso |
| R-U10 | A preferência fica no localStorage, na chave `safrion.pref.unidprod:<perfil>:<cultura>` (perfil = `g2perfil().k`; cultura = nome no cadastro). Leitura e gravação ficam em try/catch, com a memória da página como reserva, e o valor inicial é o Padrão. Nada vai para o cenário nem para outra chave. Se a escolha não vale para o estágio, a tela mostra o Padrão e o motivo, sem apagar a preferência | Troca visual virar fato de negócio; perder a escolha ao voltar à tela |
| R-U11 | Trocar a unidade não é ação: não chama `cenMudar` e não mexe em `pr_sel`, `pr_form`, `pr_ferr`, nos filtros da grade nem no foco | Perder rascunho ou filtro; registrar algo sem querer |
| R-U12 | Mensagens de comando (recebimento, publicar) ficam no Padrão: o domínio não lê preferência de tela | Regra de domínio dependente do navegador |

## 5. Estado único e integrações

| Módulo | Lê | Grava |
|---|---|---|
| Cenário (`c.producao`, `c.ordens`) | Cargas recebidas, origens (kg, L, `ben`, `modo`) e apontamentos somados, via `prResultado` e `prPasse` | Nada; a prova é a comparação byte a byte (AC-c) |
| Cadastro (`PRDC.un` = `CULTURA_UN`; `PRDC.unAlt` montado de `EMB_PACK`) | Massa da unidade, base física e estágio de campo (`campo`, `proc`) | Nada |
| Planejar safra (linhas `g_cult`) | `meta`, `unm` e cultura | `meta` e `unm`, só no Salvar e só se o campo mudou |
| Perfil (`g2lib.js`) | `g2perfil().k` | Nada |
| Navegador | `safrion.pref.unidprod:*` | Só essa chave |
| Mapa, quando a DEC-0910-36 trouxer a camada | `prUnpInd`, `prUnpOpcoes`, `g2unidPref` | Nada |

**Assinaturas:**
- `prUnpOpcoes(cultura, estagio)` → `[{k, rot, un, massa|null, ok, motivo}]`, com `estagio` = `'base'` ou `'campo'`.
- `prUnpMassa(cultura, unTxt)` → `{massa, per}` ou `null`.
- `prUnpKgHa(cultura, valor, unTxt)` → kg/ha com 6 casas, ou o erro "unidade sem massa".
- `prUnpInd(cultura, X, k)` → `{st, kgHa, num, un, prod, est, motivo}`, onde `X` vem de `prResultado`, `prPasse` ou `prPonderada`.
- `prUnpTxt(ind)` → texto da célula.
- `g2unidPref(cultura)` e `g2unidSet(cultura, k)`.

## 6. Semente sintética (os números fecham; executado em `verificacao/contas.py`, FALHAS: 0)
Nenhum dado novo entra no cenário e a versão `v` não muda. A preferência começa vazia, ou seja, no Padrão. Os números abaixo vêm da semente da COLH (§6.6 dela):

| Contexto | Padrão | kg/ha | t/ha | sc60 eq./ha | Outra |
|---|---|---|---|---|---|
| Pivô 6, ciclo (60.320 kg em 62,79 ha) | 0,96 t/ha | 960,66 | é o Padrão | 16,01 | 96,07 cx10 eq./ha |
| Pivô 19, ciclo (36.420 kg em 75,11 ha) | 0,48 t/ha | 484,89 | é o Padrão | 8,08 | 48,49 cx10 eq./ha |
| Mamão ponderado (96.740 kg em 137,9 ha) | 0,70 t/ha | 701,52 | é o Padrão | 11,69 | a média simples daria 722,78 kg/ha (errada) |
| Meta do mamão | 50 t/ha/ano | 50.000 kg/ha/ano | é o Padrão | 833,33 /ano | 5.000 cx10 eq./ha/ano |
| Meta da soja T1-A | 64 sc/ha | 3.840 | 3,84 | é o Padrão | — |
| Meta digitada 3,85 t/ha (soja) | 64,17 sc/ha | 3.850 | 3,85 | é o Padrão | — |

Casos injetados no teste, com o estado montado como em `cafe_apurar_unit.js`:
- **K-U01:** 6.000 kg/ha = 6 t/ha = 100 sc60 eq./ha.
- **K-U02:** algodão em caroço 4.526 kg/ha = 301,73 @/ha; arroz RS 9.044 kg/ha = 180,88 sc/ha (50 kg) = 150,73 sc60 eq./ha.
- **K-U07 (contraprova i):** cultivo anual de soja de 10 ha (cultivo `tu1` injetado no `PRDC.cult`), com duas O.S. de colheita de 10 ha apontados cada e cargas de 10.000 kg e 5.000 kg a 14 % de umidade e 1 % de impureza. Resultado: 1.500 kg/ha = 1,5 t/ha = 25,00 sc/ha. O valor errado seria 750.
- **K-U08 (contraprova ii):** parcelas distintas de 10 ha com 10.000 kg e de 5 ha com 15.000 kg dão 1.666,67 kg/ha = 1,67 t/ha = 27,78 sc/ha. A média das taxas daria 2.000, que é o valor errado.
- **K-U09:** café do C1 (o caso da COLH-C01): 12.000 L, 6.000 kg pesados e 5 ha apontados.
  - Padrão: "sc/ha a apurar · 2.400 L/ha de Café da roça".
  - kg/ha: 1.200 kg/ha de Café da roça.
  - sc60 eq./ha: 20 sc60 eq./ha de Café da roça.
  - Sem peso: só 2.400 L/ha, com as opções de massa indisponíveis.
- **K-U10:** 0 kg em 10 ha = "0 kg/ha"; 5.000 kg com área 0 = "sem área colhida apontada"; sem área e sem produção = "—".
- **K-U11:** depois de 20 trocas, os textos são idênticos aos da primeira volta e o JSON do cenário também.

## 7. Passos de implementação (cada um deixa o protótipo funcionando)
1. **P1 · Conversor e regras, sem tela:**
   - `producao.js`: bloco `prUnp*`; `op` em `prPrtvTxt` e `prPrtvResTxt`; L, kg do fruto e estimativa em `prProdOS`; desvio em kg/ha; guarda em `prPonderada`.
   - `dados_cad.py`: algodão no `CULTURA_UN`.
   - `dados_producao.py`: `unAlt`.
   - `producao_unit.js`: bloco U20 (aceites a, b, d, e, f, i, mais a parte de unidade do c).
   - Ao fim do P1, todos os testes atuais continuam verdes, porque `op` padrão dá o texto de hoje.
2. **P2 · COLH:**
   - `g2unidPref` e `g2unidSet`; seletor no bloco; linha, total da cultura, painel e cartões; café da roça (R-U05).
   - Novas expectativas de C01a, C01b, C01f e C01n, com o motivo no commit: "R-U05: a parte do fruto aparece em L/ha com o produto; o beneficiado continua a apurar".
   - `producao_fluxo_test.py` ganha o modo `unid` (COLH).
3. **P3 · SAF:**
   - O SAF carrega o conversor; `KG_UN` vira `prUnpKgHa`.
   - Seletor na `g_cult`; Meta na coluna, no painel e no Dividir; regra do campo que mudou (R-U06); `unMetaDe` aceita a unidade informada que for válida.
   - Modo `unid` (parte SAF e a prova entre telas); a guarda de nomes passa a cobrir o safra.js.
4. **P4 · Fechamento:** `varredura.py`, `acoes_duplicadas.py`, a bateria do módulo e a dos vizinhos, `docs/STATUS.md` e o artefato com uma linha do que mudou.

**Bateria por passo** (com `SAFRION_DADOS=sintetico`, dentro de `gen37/`):
1. `python3 producao_unit_test.py`;
2. `python3 cafe_apurar_test.py`;
3. `python3 build.py > /tmp/UNID-PROD-build.log; grep -c FALHA /tmp/UNID-PROD-build.log` (precisa dar 0);
4. `python3 montar_render.py`;
5. no navegador, um teste por vez: `env CHROME_BIN=/tmp/cloudchrome/chrome flock /tmp/cdpU.lock env CDP_GL=1 timeout 900 python3 <teste>`, com `varredura.py`, `../ferramentas/acoes_duplicadas.py . /tmp/UNID-PROD-dup.json`, `producao_fluxo_test.py unid`, `producao_fluxo_test.py celular`, `cafe_apurar_nav.py`, `saftest.py` e `tabelas_saf_test.py`.

Os vermelhos conhecidos da base (lista da tarefa, não reexecutada aqui) ficam listados no log, sem esconder nenhum. Antes do P1, roda-se a bateria uma vez na base `47ff754` e o log fica guardado para comparar.

**Modo `unid` do `producao_fluxo_test.py`:**
1. COLH a 1440 px: com até 3 Tabs a partir da escolha de Visão, o seletor recebe o foco. ArrowDown escolhe kg/ha, e as células do Mamão passam a kg/ha. Enter abre a lista.
2. A 390 × 844: o seletor tem pelo menos 44 × 44 px, não há rolagem horizontal e os cartões aparecem em kg/ha.
3. Pesar a CG-2108 no CARGA (um comando real grava o cenário) e guardar S0 = todas as chaves do localStorage, menos `safrion.pref.unidprod:*`. No COLH, abrir "Publicar previsão" do Pivô 19 e digitar a perda sem publicar (rascunho). Aplicar o filtro rápido "Em colheita", pôr o foco no seletor e fazer 20 trocas pelo teclado. Esperado: S1 = S0, e o filtro, o rascunho e o `activeElement` continuam os mesmos.
4. Ir ao PROD e voltar: o seletor e as células continuam em kg/ha.
5. Perfil Caio: aparece o Padrão. Voltando à Ana: kg/ha.
6. Pivô 19: a mesma unidade e o mesmo número na linha, no painel (kv Produtividade e passes) e no cartão.
7. Selecionar uma linha de soja e escolher kg/ha. A Referência do T1-A mostra "meta 3.840 kg/ha", e o SAF mostra "3.840 kg/ha" na Meta do T1-A.
8. SAF: depois de 20 trocas, `meta` e `unm` das linhas ficam intactos. Salvar o painel do T1-A sem mexer na meta mantém {64, sc/ha}. Digitar 3,85 com t/ha escolhido grava {3,85, t/ha}, e a tabela mostra 64,17 sc/ha quando o Padrão é escolhido.
9. Mapa: se a camada "Colheita e produtividade" estiver na barra, a mesma unidade aparece nela. Se não estiver, o teste imprime "PENDENTE (DEC-0910-36)".

## 8. Critérios de aceite

| AC | Critério | Teste que prova |
|---|---|---|
| AC-a | 6.000 kg/ha ↔ 6 t/ha ↔ 100 sc60 eq./ha, nos dois sentidos | `producao_unit.js` U20a (K-U01) |
| AC-b | Unidade com massa declarada: algodão em @ de 15 kg; arroz RS em sc de 50 kg com a opção sc60 eq. separada; cx 10 kg do mamão vinda de `EMB_PACK` | U20b (K-U02); U20b2 (opções do mamão) |
| AC-c | 20 trocas repetidas não derivam e não mudam o cenário. Antes da medição, um comando real grava o cenário (pesagem da CG-2108); depois das trocas, todas as chaves do localStorage, menos `safrion.pref.unidprod:*`, ficam idênticas byte a byte. As linhas do SAF ficam com `meta`/`unm` intactos, inclusive salvando o painel sem mexer na meta | U20c (K-U11, JSON igual); `producao_fluxo_test.py unid` passos 3 e 8 |
| AC-d | Soja, milho, mamão, algodão e café sem trava arbitrária: todas as opções de massa valem no estágio de massa; o coco em frutos tem a massa indisponível, com o motivo | U20d |
| AC-e | Não apurado ≠ zero; área 0 mostra pendência, sem divisão (K-U10) | U20e |
| AC-f | Volume sem equivalência não vira massa: café só em L mostra L/ha e a massa indisponível; não existe caminho de L para kg | U20f (K-U09); C01a, C01b, C01f e C01n novos |
| AC-g | Teclado (Tab chega ao seletor; setas e Enter trocam a opção); em 390 px o alvo tem pelo menos 44 px e não há rolagem horizontal; a preferência volta ao voltar à tela e muda com o perfil (Caio vê o Padrão, Ana vê kg/ha) | `unid` passos 1, 2, 4, 5 |
| AC-h | A mesma unidade aparece na tabela, no painel e no cartão do mesmo contexto (perfil × cultura), e também entre telas: soja em kg/ha no COLH aparece em kg/ha no SAF. Mapa: pendente da DEC-0910-36; o teste imprime "PENDENTE", e isso não conta como OK | `unid` passos 6, 7, 9 |
| AC-i | Contraprovas de agregação: (i) 1.500 kg/ha, não 750; (ii) 1.666,67 kg/ha, não 2.000; (iii) `prPonderada` recusa café da roça com beneficiado e algodão em caroço com pluma | U20i1 (pelo `prResultado`, K-U07), U20i2 (K-U08), U20i3 |
| AC-j | Fonte única: `KG_UN` sumiu do safra.js; nenhum nome do producao.js é redefinido no safra.js; o filtro, o rascunho (`pr_form`) e o foco ficam depois da troca | `producao_unit_test.py`; `unid` passo 3 |
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
