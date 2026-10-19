# INTEL-01 · Inteligência comercial de Vendas e de Compras

Pedido do proprietário (13/10/2026): "coloque inteligência comercial em vendas e inteligência comercial em compras. dos preços, etc. específico para cada um dos 2". Autor: Claude. Revisor: Codex (regime rápido do protótipo; a revisão não bloqueia a publicação). Dados sintéticos.

## Telas
- **Inteligência de vendas** (`IV.dc.html`, menu Comercial): preço × mercado, safra comercializada e recebimento líquido por venda.
- **Inteligência de compras** (`IC.dc.html`, menu Suprimentos): cotação × referência × último pago, fornecedores (preço e pontualidade) e custo de insumos por hectare.

## Regras (fonte única: `inteligencia.js`, em decimal pelos `pr*` do `producao.js`; ENG-011/013)
| Indicador | Conta | Alerta | Ausente |
|---|---|---|---|
| Diferença à referência (venda) | (preço médio contratado − referência) ÷ referência | pior que −5% | sem referência: null, "—" |
| Safra comercializada | compromissos ÷ (estoque apto + previsão publicada), pelas linhas do Painel comercial | venda acima da oferta ou venda sem previsão | saca a conferir (A-17): "Suspenso"; sem oferta: "Sem previsão"; nunca 0% |
| Recebimento líquido | preço − frete (R$ 190/t × kg da unidade ÷ 1000; retirada = 0) − preço × 1,2% a.m. × dias ÷ 30 | — | só venda com preço e massa conhecida |
| Cotação × referência (compra) | (melhor cotação válida − referência) ÷ referência | acima de +5% | sem cotação: null; vencida: não vira "melhor preço", pede nova |
| Economia | Σ quantidade × (referência − melhor) onde a melhor é menor | — | — |
| Pontualidade | entregas no prazo ÷ entregas (a entregar não conta) | abaixo de 80% | sem entrega: null |
| R$/ha | Σ quantidade × referência ÷ área da safra | — | área zero: null |

Parâmetros sintéticos (do proprietário quando for real): custo financeiro 1,2% a.m., frete R$ 190/t, limite de 5%.

## Fontes dos dados
- Vendas: o cenário (pedidos, lotes, previsões) pelas funções do Comercial (`comPrecos`, `comPainel`).
- Compras: `dados_inteligencia.py`, que lê:
  - a demanda e a referência do Planejar safra (`dados2.demanda`);
  - as propostas (`dados2.PROPOSTAS`);
  - os pedidos (`PED_2526`, `PEDIDOS`) e a área (`CULTIVOS`).
- Histórico de preço e atrasos: a semente não tem. `HIST_SINT` é sintético e aparece rotulado "sintético" na tela.

## Limites do protótipo
- Mostra sinais, não decide: vender ou comprar é de quem vende ou compra. Nenhum alerta trava ação.
- Referência de mercado com fonte própria (`COMC.ref`); não há cotação externa ao vivo.

## Testes
- `inteligencia_unit_test.py`: 22/22. Oráculo independente em Python (Decimal) para as compras. Fórmulas, ausente ≠ zero, saca a conferir, cotação vencida e limites de 5%.
- `inteligencia_nav_test.py`: 17/17, em 1440 e 390 px.
