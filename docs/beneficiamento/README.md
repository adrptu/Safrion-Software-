# Beneficiamento: grãos, frutas/HF e café (especificação · v2)

Pedido do proprietário (05/10/2026): "coloque também o módulo de beneficiamento (frutas, grãos e café) melhorado com tudo que aprendemos e melhoramos até agora."

- `ESPECIFICACAO.md`: ordem de processo no menu (Produção › Beneficiamento), as três rotas, balanço de massa com fonte única, qualidade antes da reserva, estorno, lições aplicadas com fonte, BEN-1 (packing de mamão de ponta a ponta) e os blocos seguintes (BEN-2 compra de caixa e custo provisório, BEN-3 grão, BEN-4 café).
- `DECISOES.md`: assumido, cortado, parâmetros do dono com default, pendências e a revisão adversarial aplicada (42 achados).
- `FORA-DE-ESCOPO.md`: o que ficou fora, com condição de retorno.
- `verificacao/`: contas em `decimal` (`contas.py`), reconferência independente (`verifica.py`, FALHAS: 0), conferência de referências (`confere.py`) e os achados da revisão (`revisao.json`).

Rótulo: **especificado**. Nada foi implementado. Autor: Claude. Revisor: Codex. Ordem: depois da TABELAS-FOCO e do PCM × suprimentos 1a–1c (o cenário compartilhado muda de versão em sequência).
