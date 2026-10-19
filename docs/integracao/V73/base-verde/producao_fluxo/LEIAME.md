# Base verde · `producao_fluxo_test.py`, 19/10/2026

**Antes:** 15/20 desde a v138 (`docs/integracao/V73/v139/logs/bateria43/`). O teste parava no modo `fluxo` com exceção, e os modos seguintes (erros, celular, revisão e unid) nem rodavam.

## Causa (medida, não suposta)
A sonda no render mostrou que a tabela da Previsão e colheita abre **agrupada por cultura e recolhida**. É o padrão DRILL-RECOLHIDO, publicado na v129 e pedido pelo proprietário. A linha "Pivô 19" fica dentro do grupo fechado "Mamão Formosa".
- **Logo depois do clique em "Expandir tudo":** 0 linhas.
- **0,8 s depois:** a linha aparece, e o painel do Pivô 19 mostra o 0,73 t/ha e o 0,48 t/ha que o oráculo pede.

O mesmo vale para o Estoque de produto, os cartões a 390 px e a etapa 2 do Planejar safra, que abre agrupada por fazenda.

**Classificação:** teste obsoleto. A navegação foi escrita para a tabela aberta. O produto está certo.

## Correção (só a navegação do teste; nenhum oráculo mudou)
- `ir()` e a mudança de etapa do Planejar safra chamam `expande()`. Ele faz o que o usuário faz: "Expandir tudo", com o clique contado no AC-17. Depois espera o botão virar "Recolher tudo", em vez de um tempo fixo.
- `row()`, se a linha não aparece, expande e espera a linha.
- **Medida do AC-17:** 14 cliques e 5 campos digitados, dentro do limite de 30 cliques e 5 campos.

## Resultado (render da composição, dados sintéticos)
- **Antes:** 15/20, com o teste parando no meio.
- **Depois:** **92/93**, com os seis modos executados até o fim (`producao_fluxo_final.log`). O AC-17 fica em 14 cliques e 5 campos.

## Vermelho que fica, e por quê
**AC-h Mapa:** a camada "Colheita e produtividade" não segue a unidade de produtividade escolhida (P5 da UNID-PROD).
- **Classificação:** pendência real do produto, não do teste. O teste foi escrito para reprovar assim que a camada aparecesse na barra sem estar ligada ao conversor, e a camada entrou com a DEC-0910-36.
- **Severidade:** S3. O Mapa mostra a produtividade na unidade padrão da cultura enquanto a Previsão e colheita mostra a unidade escolhida; o número está certo em cada unidade.
- **Fica como item da base verde**, sem esconder o teste.
