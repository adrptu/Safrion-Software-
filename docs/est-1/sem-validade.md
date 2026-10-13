# EST-1 — trocar pedido para item sem validade

Autor Codex; revisor/integrador Claude. Base 27812863c0395f4259256eaf7d649b6d05a558ca do PR60. Produto: uma linha em areas/processo_estoque.py, dentro da autoria vigente.

Ao abrir a nota de sementes, preencher 12/2099 e trocar para pedido de item sem validade, a tela exibia “Sem validade”, mas a nova guarda comparava o valor antigo oculto com o lote existente sem data. Recebimento válido era recusado num campo somente leitura. A validação agora usa a mesma normalização já aplicada por ESAVE.g_rec (— para os grupos sem validade); não altera o rascunho nem flexibiliza a regra de lotes com vencimento.

Provas sintéticas executadas em 13/10/2026:
- est_validade_entrada_test.py: antes 14/15, depois 15/15; contraprova cobre o rascunho e saldo 100→105.
- est_sem_validade_nav.py: antes 4/8, depois 8/8, em 1440×900 e 390×844, troca real de pedido, valor somente leitura e persistência.
- est_validade_conflito_nav.py: 12/12 depois; recusa sem escrita, rascunho e recuperação em lote diferente preservados.
- Build focal Estoque e montar_render: exit0. Somente a página alterada foi regenerada; não representa build integral desta candidata.

Não alterados os ganchos Claude cenEstDem/CTL4 e cenConcPrevia/cenConciliar; as duas pendências já reproduzidas continuam impedindo integrar EST-1. Sem aprovação/merge próprio, publicação, HML ou encerramento do protótipo.
