# PCM × Suprimentos de manutenção (especificação · v2)

Pedido do proprietário (05/10/2026): "Conecte PCM e suprimentos de manutenção (materiais e serviços) de forma brilhante, sistêmica, integrada e conectada."

- `ESPECIFICACAO.md`: ciclo, regras numeradas e testáveis, telas (nenhuma nova), Bloco 1 em 3 PRs (1a estado único, 1b aprovação e fila do almoxarife, 1c falta → compra → recebimento, com compra de balcão), testes e aceite.
- `DECISOES.md`: o que foi assumido, cortado, os parâmetros do dono com default, pendências e a revisão adversarial aplicada (42 achados).
- `FORA-DE-ESCOPO.md`: o que ficou fora, cada item com condição de retorno.
- `verificacao/`: contas refeitas (Python `Decimal`), geração das OMs no node e os achados da revisão (`revisao.json`).

Rótulo: **especificado**. Nada foi implementado. Autor: Claude. Revisor: Codex. O Bloco 1 começa depois que a pilha TABELAS-FOCO (#42, #43, #44) estiver com PR aberto e bateria verde.
