# C-3/C-4 — candidata parcial para revisão cruzada

Codex autor; Claude revisor/integrador. Contrato 6242525214, ACK 6242544646. Base 5466c6d08eadf1cbd83d493675cf304e949bd4e4. Somente cenário e Compras/Estoque nos trechos combinados; F1/N1 intactos.

O andamento da compra lê/migra a chave antiga para `cenario.compras` sem apagar o legado, com recibo idempotente na gravação estrita. Memo só após durabilidade; erro conserva rascunho e chave de repetição. PC aprovado entra no seletor de Estoque por linha/produto/unidade; uma seleção ambígua de PC é recusada. Recebimentos deduplicados por estRec.id alimentam o saldo por item. Recebido é apto + quarentena da conferência; quarentena atual vem do lote, fica não apurável se não há atribuição segura à linha. Não há rateio entre produtos ou linhas. Recebimento do formulário exige gravação estrita. Dados antigos de previsão sem unidade só abatem quando as evidências do produto têm uma unidade única.

## Bloqueios para integrar

- C-3 ainda incompleto: emitir()/aprovar() anunciam sucesso antes da gravação no PREVALS. Esses callbacks estão fora dos trechos do contrato. Extensão delimitada solicitada em 6242581438; não integrar até corrigir a confirmação antes do recibo. O aviso de falha implementado não substitui essa correção.
- Navegador não executado por Codex. Claude deve executar Compras → receber parcialmente no EST → retornar à linha em Compras, teclado/celular e recuperação de cota. Não usar teste em VM como E2E.
- A comparação de armazenamento detecta mudanças já observáveis; não é trava multiaba.
- Planejamento ainda tem leitores do legado fora deste contrato; não alegar migração integral de todo consumidor.

## Provas executadas

`node c34_test.cjs`: 13 cenários com as funções reais de cenario.js, procGravar e adaptadores EST; armazenamento em memória com falha de quota injetada. Casos: recibo/repetição/conflito, migração e preservação, corrupção, PC-X 100 kg A + 50 L B recebendo 20 kg A → 80 kg A e 50 L B, deduplicação, linha/unidade diferentes, quarentena após inspeção e atribuição desconhecida, pedidos aprovados, legado sem unidade e memo após durabilidade. AST dos dois Python e sintaxe JS extraída + cenario.js passaram.

Contraprovas da base já entregues em 6241912132 (memo antes da escrita impede retry) e 6241983319 (recebimento de A reduz B). Testes novos não alteram fontes do revisor nem testes anteriores.
