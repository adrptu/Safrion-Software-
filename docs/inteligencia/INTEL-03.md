# INTEL-03 · Inteligência de mercado para comprar e vender

**Pedido do proprietário (18/10/2026):** "o submenu de inteligência em compras e comercial tem que ser uma ênfase em gráficos e informações mais estratégicos, mostrando preços de mercado futuro, câmbio, spot/físico… Gráfico por período selecionado (12m, 24m, 36m, 48m por exemplo) e também no período selecionado qual em média é melhor para comprar ou vender o que se está analisando no momento. Melhore esse prompt para si mesmo e melhore ao máximo junto com o Codex."

| Campo | Valor |
|---|---|
| ID / resultado útil / persona | INTEL-03. Em uma tela, quem decide vê se o preço de agora é bom, por quê e qual mês costuma ser melhor, com a força da evidência. Personas: Ana (gestora, decide venda e compra), Paulo (proprietário, decide hedge e prazo) |
| Requisitos e fora do escopo | Continua a INTEL-02 (`docs/inteligencia/INTEL-02.md`): índice sazonal, tendência sem época, custo do dinheiro. Fora: ordem de compra ou venda automática, previsão de preço, execução de hedge |
| Autor / revisor / integrador | Claude (autor) · Codex (revisor de produto, critérios e QA) · Claude (integrador) |
| Telas | Comercial › Inteligência de vendas (IV) e Suprimentos › Inteligência de compras (IC): a mesma peça, com o lado (vender ou comprar) trocando a cor e a pergunta |

## 1. As perguntas que a tela responde, nesta ordem

1. **O preço de agora é bom?** Preço atual contra o período escolhido: posição na faixa (percentil), distância da média e do melhor mês, em R$ e na moeda de referência.
2. **Por que mudou?** A variação do físico decomposta em bolsa, câmbio e base (prêmio local). Exemplo: "a soja subiu R$ 9/sc em 12 meses: bolsa −R$ 4, câmbio +R$ 11, base +R$ 2".
3. **Quando costuma ser melhor?** Mês a mês no período escolhido, já sem inflação e sem a tendência: índice médio, faixa (pior e melhor ano) e acerto, isto é, em quantos anos aquele mês ficou do lado bom da média.
4. **Vale esperar?** O ganho médio do melhor mês menos o custo do dinheiro e da armazenagem até lá, com o risco: em quantos anos esperar teria perdido.
5. **Quanto vale em troca?** Relação de troca: sacas de soja ou milho por tonelada do insumo (compra) e insumo por saca (venda), contra a média do período.

## 2. Uma tela, de cima para baixo

- **Faixa de contexto:** produto (seleção rápida da lista da fazenda), praça e o seletor de período **12m · 24m · 36m · 48m**, de um toque. Lembra a última escolha do aparelho.
- **Cabeçalho de decisão (uma linha por pergunta):** "Agora R$ 128,40/sc · percentil 78 dos últimos 36 meses · 6% acima da média · melhor mês em média: março (+4,1%, acerto 3 de 3 anos)". Selo: "Bom momento para vender", "Neutro" ou "Abaixo do normal", com a regra na dica.
- **Gráfico principal (preço no período):**
  - linha do físico (R$/unidade);
  - faixa sombreada mínima–máxima do mesmo mês nos anos do período;
  - linha da média do período;
  - ponto de hoje marcado.
  - Ao tocar ou passar o mouse, o mês, o físico, o futuro convertido e o câmbio.
- **Três gráficos pequenos, alinhados no mesmo eixo de tempo:** futuro na moeda da bolsa, câmbio (R$/US$) e base (físico − futuro convertido). São os três motores do preço.
- **Decomposição da variação no período:** barras em cascata (preço inicial → bolsa → câmbio → base → preço final), em R$/unidade.
- **Sazonalidade no período:** 12 barras do índice médio (100 = média do ano), com a faixa entre o pior e o melhor ano.
  - O melhor mês fica destacado: o mais alto para vender, o mais baixo para comprar.
  - Abaixo das barras, o acerto ("3 de 3 anos") e a força da evidência.
- **Vale esperar:** tabela curta com os próximos meses.
  - Colunas: ganho médio; custo do dinheiro; armazenagem (venda) ou atraso para a necessidade (compra); ganho líquido; anos em que esperar teria perdido.
  - A compra continua presa à data da necessidade (INTEL-02).
- **Relação de troca:** valor de agora contra a média e a faixa do período.

## 3. Contas

Fonte única: `inteligencia.js` (ENG-011). Decimal, unidade explícita e 6 casas nas razões.

| Grandeza | Conta |
|---|---|
| Preço real | Preço nominal × IPCA(hoje) ÷ IPCA(mês). As comparações entre anos usam o real; a tela mostra o nominal e diz qual usou |
| Percentil de agora | Posição do preço real de hoje entre os meses do período (0 = o mais baixo, 100 = o mais alto). Selo, só com evidência: venda ≥ 70 "Bom momento para vender", compra ≤ 30 "Abaixo do normal"; no meio, "Neutro" |
| Sem tendência | Antes do índice, o preço real de cada mês é dividido pela reta de mínimos quadrados do período (`int3SemTendencia`). Sem isso, uma série que só sobe põe o "melhor mês de venda" no último mês de cada janela |
| Índice sazonal do mês m (período de N anos) | Para cada ano completo do período: preço real sem tendência de m ÷ média dos 12 meses daquele ano. O índice é a média desses N valores; a faixa vai do menor ao maior |
| Melhor mês | Venda: maior índice médio; compra: menor. Empate: o mais cedo |
| Acerto do melhor mês | Número de anos em que o índice desse mês ficou acima de 1 (venda) ou abaixo de 1 (compra), de N |
| Força da evidência | **Forte:** N ≥ 3 e acerto ≥ N − 1 e amplitude média ≥ 3%. **Fraca:** N = 2, ou acerto abaixo disso. **Sem padrão:** N = 1 (12m: um ano só é um exemplo, não um padrão) ou amplitude < 3% |
| Futuro convertido | Futuro × câmbio × fator de unidade. Exemplo: soja CBOT US$/bushel × 2,2046 = US$/sc de 60 kg |
| Base | Físico − futuro convertido, em R$/unidade |
| Decomposição | Variação do físico = Δbolsa (com o câmbio inicial) + Δcâmbio (com a bolsa final) + Δbase. A soma fecha com a variação do físico por construção, e o teste confere |
| Custo do dinheiro | Taxa mensal do cadastro (INTEL-02: 1,2% a.m.) × meses de espera, sobre o preço de hoje |
| Ganho líquido de esperar até m | Índice(m) ÷ índice(hoje) − 1 − custo do dinheiro − armazenagem (venda; por unidade e mês, do cadastro) |
| Anos em que esperar perdeu | Anos do período em que o preço real de m ficou abaixo (venda) ou acima (compra) do preço real do mês de hoje |
| Relação de troca | Preço do insumo por tonelada ÷ preço da saca do produto, em sc/t. Mesmo mês, praça da fazenda |

### 3.1 Um índice só na tela (achado da F1, 18/10)

A INTEL-02 calculava o índice no preço nominal e com tendência. Com a F1 no topo da mesma tela, as duas leituras se contradiziam: o bloco novo dizia "Sem padrão" e a lista dizia "Esperar até setembro". A contraprova A4 mostra o efeito: numa série que só acompanha o IPCA, o método antigo acha setembro, o último mês de cada janela, com amplitude de 3% ou mais.

Correção: a lista da INTEL-02 (recomendação, "espere até", economia esperando) passou a usar o mesmo índice do bloco, sem inflação e sem tendência (`intZ` em `inteligencia.js`). Efeito nos dados sintéticos da IC, comparando o oráculo da v132 com o atual:
- a semente 58 W passou de "Esperar" para "Comprar até a necessidade", porque a época barateia só 1,2%;
- a economia esperando o mês certo passou de R$ 23.103,58 para R$ 37.353,87.
- Na tela, o filtro "Comprar agora" mostra 5; o teste esperava 4.

`inteligencia_nav` agora compara a recomendação de cada um dos 20 insumos com o oráculo em Decimal e tira dele os totais, em vez de usar valores fixos. Na v132, o valor fixo "R$ 41.363" da melhor cotação já estava obsoleto: o oráculo da v132 dá R$ 41.368.

## 4. Fontes

**Protótipo (este ambiente).** A rede deste ambiente recusa BCB, CEPEA, CONAB e Comex Stat; futuros da B3 e da CBOT exigem licença. Por isso as séries são **demonstrativas**:
- 60 meses gerados de forma coerente: futuro em US$, câmbio, base e IPCA. O físico sai da conta `futuro × câmbio + base`, para a decomposição fechar;
- cada gráfico traz o rótulo "Demonstração: série sintética, não é cotação";
- nenhuma série é apresentada como real.

**Software real** (fonte com data em cada ponto):

| Série | Fonte | Situação |
|---|---|---|
| Câmbio PTAX e IPCA | Banco Central, API SGS | Pública e gratuita |
| Físico | CEPEA/Esalq (uso com citação da fonte), CONAB e as vendas e compras da própria fazenda | Pública, com regras de citação |
| Futuro | B3 (milho, boi, café) e CBOT/CME (soja, milho) | Licença de dados paga: decisão do proprietário, com estimativa de custo |
| Fertilizante | Comex Stat (FOB importado) e as compras da fazenda | Pública |

## 5. Regras de leitura (o que a tela nunca faz)

- **Histórico não é previsão.** O selo diz "em média" e mostra o acerto. Nunca diz "vai subir".
- **Sem padrão não vira conselho:** com 12m, ou com evidência "Sem padrão", o melhor mês aparece só como "maior preço do período", sem selo de decisão.
- **Ausente ≠ zero:** produto sem série mostra "Sem série de preço", sem melhor mês e sem relação de troca.
- **Uma decisão por tela:** a ação principal é "Registrar decisão de venda" ou "Planejar compra". Ela leva ao contrato (VEN) ou à compra (CMP) com o produto e o mês escolhido, nunca grava sozinha.

## 6. Aceite (medido)

| ID | Aceite | Prova |
|---|---|---|
| A1 | Trocar 12/24/36/48m muda gráfico, percentil, índice e acerto, e o N de anos aparece | `intel03_nav` no navegador, 1440 e 390 px |
| A2 | Decomposição: Δbolsa + Δcâmbio + Δbase = Δfísico, com diferença ≤ 0,01 | Oráculo em Decimal (`intel03_unit`) |
| A3 | Índice sazonal e acerto iguais ao oráculo em Decimal, em 2 produtos × 4 períodos | `intel03_unit` |
| A4 | Contraprova da inflação: uma série só com IPCA e sem época sai "Sem padrão" no real (no nominal daria um falso melhor mês) | `intel03_unit` |
| A5 | 12m nunca mostra selo de decisão | `intel03_unit` e `intel03_nav` |
| A6 | A compra respeita a data da necessidade (regra da INTEL-02) | `inteligencia_unit` sem regressão (35/35) |
| A7 | Gráficos com rótulos e eixos legíveis nos dois temas; nada cortado a 390 px; foco por teclado em cada ponto do gráfico | `intel03_nav` + `paginas_scan` |
| A8 | A tela lê e não grava | Instantâneo do cenário igual antes e depois |

## 7. Fatias

- **F1 (implantada, v133):** período, gráfico principal, cabeçalho de decisão, sazonalidade com acerto e evidência, em vendas e compras. Provas: `intel03_unit` 28/28, `intel03_nav` 36/36, `inteligencia_unit` 35/35 e `inteligencia_nav` 28/28. A2 (decomposição) fica para a F2.
- **F2:** futuro, câmbio, base, decomposição e relação de troca.
- **F3:** "Vale esperar" com armazenagem e risco ("anos em que esperar perdeu"), e o caminho para Registrar decisão / Planejar compra.

## 8. Para o Codex (revisão pedida)

1. A força da evidência (§3) separa bem "padrão" de "acaso" com N = 2 a 4 anos? Proponha outro limiar se houver.
2. A decomposição pela ordem bolsa → câmbio → base é aceitável, ou prefere a média das duas ordens (Shapley), para não depender da ordem?
3. Na compra de fertilizante, a referência deve ser o FOB em US$ × câmbio (paridade de importação) em vez do preço local? Isso muda o "por que mudou".
4. Algum caso em que o selo induziria a uma decisão errada: perecível, produto com contrato a termo já fechado ou praça sem série?
