# INTEL-02 · preço, tendência e melhor mês (compras e vendas)

**Pedido do proprietário (13/10/2026):** "inteligência de compras e vendas é mais relativo aos preços, tendências, melhor mês para compra e venda".

**Autoria:** Claude (autor), Codex (revisor), regime leve do protótipo (AGENTS §3.5). Dados sintéticos.

**Onde está:** a seção "Preço e melhor mês" abre as telas Comercial › Inteligência de vendas (IV) e Suprimentos › Inteligência de compras (IC). As seções da INTEL-01 ficam abaixo dela.

## Fonte do preço
- **Protótipo:** série mensal **sintética** de 60 meses (out/2021–set/2026), determinística e rotulada na tela, gerada por `dados_inteligencia.precos()`.
  - O último mês é igual à referência atual: em vendas, `dados_comercial.REF`; em compras, o preço de referência da safra.
  - Forma da série: sazonalidade típica do produto ou do grupo, tendência anual, movimento dos últimos 4 meses e ruído de ±1%.
- **Produto sem fonte de preço** (Feijão): sem série, sem preço, sem melhor mês e sem recomendação (ausente ≠ zero).
- **Software real:** CEPEA/Esalq, CONAB e CEAGESP (fonte pública com data) e as compras da própria fazenda. Contratar fonte paga é decisão do proprietário.

## Contas
Fonte única: `inteligencia.js`, em decimal, com 6 casas nas razões.

| Grandeza | Conta |
|---|---|
| Índice sazonal do mês | Média, nas janelas completas de 12 meses que terminam no mês mais recente, de preço do mês ÷ média da janela |
| Tendência | Média dos 3 últimos meses contra os 3 anteriores, **sem o efeito da época** (preço ÷ índice do mês). Acima de +3% é Alta; abaixo de −3%, Queda; entre os dois, Estável |
| Normal do mês | Média dos últimos 12 meses × índice do mês |
| Agora vs normal | Preço ÷ normal do mês − 1 |
| Melhor mês (histórico) | Venda: o de maior índice; compra: o de menor. Empate: o mês mais cedo. É informação: o mês-alvo da venda é o de maior ganho líquido (abaixo) |

## O que fazer
**Venda:**
- **"Vender agora":** o mês atual é o melhor dos próximos 12, ou o preço está 5% ou mais acima do normal.
- **"Esperar":** o maior ganho líquido nos próximos 11 meses passa de 3%. Ganho líquido de cada mês: índice do mês ÷ índice de agora − 1 − custo do dinheiro (1,2% a.m. × meses de espera). O alvo é esse mês; no empate, o mais cedo. A tela lembra de somar a armazenagem.
  - Revisão Codex INTEL-02-LIQUIDO-01 (13/10): antes o alvo era o mês de maior preço bruto, e um mês próximo que pagava a espera ficava de fora ("Sem ganho em esperar" falso; o Milho em grão da demonstração era um caso).
- **"Sem ganho em esperar":** nenhuma das condições acima.
- **Perecível (mamão):** "Vender na colheita". Não dá para estocar e esperar; a época boa orienta o plantio e a colheita.

**Compra:**
- **Limite:** o melhor mês é procurado entre agora e o último dia para pedir e receber a tempo, isto é, a próxima necessidade do Planejar safra menos o prazo de entrega do fornecedor mais rápido.
- **"Comprar agora":** a necessidade é neste mês, ou agora é o mais barato até a necessidade, ou o preço está 5% ou mais abaixo do normal.
- **"Esperar":** a época barateia 3% ou mais até o limite.
- **"Comprar até a necessidade":** nenhuma das condições acima.
- **Economia estimada:** quantidade × preço × redução, só onde a recomendação é "Esperar".

## Limites e o que fica fora
- **Histórico não é previsão.** A tela diz isso e mostra a conta, o mês a mês e os últimos 12 meses.
- **Fora desta entrega:**
  - custo de armazenagem por produto;
  - câmbio e mercado futuro (B3);
  - preço por praça;
  - alerta automático de "chegou o mês".

  Condição de retorno: fonte real de preço contratada, ou pedido do proprietário.

## Testes executados
- `inteligencia_unit_test.py`: **35/35** (32 antes da revisão INTEL-02-LIQUIDO-01; P11 a P13 entraram com ela; com a regra antiga, P5, P11 e P13 falham).
  - Casos P1 a P10, contra um oráculo em Decimal que refaz índice, tendência, normal, melhor mês, recomendação e economia a partir dos mesmos dados, sem o JS.
  - P7, contraprova da tendência: uma série só com a época sai Estável, onde a conta crua diria Alta (+10,5%).
  - P8, contraprova do prazo: necessidade neste mês → Comprar agora; necessidade em janeiro → Esperar até janeiro (9,5% mais barato).
  - P9: o perecível não espera.
  - P11, caso do revisor: outubro paga +8,8% líquido e agosto −1,2%; o certo é Esperar até outubro. P12: sem ganho líquido continua "Sem ganho em esperar". P13: empate fica com o mês mais cedo.
- `inteligencia_nav_test.py`: **27/27**, em 1440 e 390 px.
  - Indicadores de preço no topo.
  - Linhas: soja, milho, mamão, feijão, semente 58 W (pedir até 05/10) e glifosato.
  - Painel com os 12 meses em barras.
