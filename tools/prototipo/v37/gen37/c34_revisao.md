# C-3/C-4 — candidata para revisão cruzada

Codex autor; Claude revisor/integrador. Contrato 6242525214, ACK 6242544646; ampliação dos callbacks autorizada em 6242583468. Base 5466c6d08eadf1cbd83d493675cf304e949bd4e4. Somente cenário e Compras/Estoque nos trechos combinados; F1/N1 intactos.

O andamento da compra lê/migra a chave antiga para `cenario.compras` sem apagar o legado, com recibo idempotente na gravação estrita. Memo só após durabilidade; erro conserva rascunho e chave de repetição. PC aprovado entra no seletor de Estoque por linha/produto/unidade; uma seleção ambígua de PC é recusada. Recebimentos deduplicados por estRec.id alimentam o saldo por item. Recebido é apto + quarentena da conferência; quarentena atual vem do lote, fica não apurável se não há atribuição segura à linha. Não há rateio entre produtos ou linhas. Recebimento do formulário exige gravação estrita. Dados antigos de previsão sem unidade só abatem quando as evidências do produto têm uma unidade única.

## Bloqueios para integrar

- A confirmação prematura foi corrigida após a ampliação: emitir/aprovar, decisões, confirmação de fornecedor e cotações passam por procAplicar antes do setState. Falha mantém campos/formulário; a chave da mesma intenção é preservada inclusive após PREVALS intermediário. Ainda requer revisão e execução real pelo revisor.
- Navegador não executado por Codex. Claude deve executar Compras → receber parcialmente no EST → retornar à linha em Compras, teclado/celular e recuperação de cota. Não usar teste em VM como E2E.
- A comparação de armazenamento detecta mudanças já observáveis; não é trava multiaba.
- Planejamento ainda tem leitores do legado fora deste contrato; não alegar migração integral de todo consumidor.

## Provas executadas

`node c34_test.cjs`: 17 cenários com as funções reais de cenario.js, procGravar e adaptadores EST; armazenamento em memória com falha de quota injetada. Casos: recibo/repetição/conflito, migração e preservação, corrupção, PC-X 100 kg A + 50 L B recebendo 20 kg A → 80 kg A e 50 L B, deduplicação, linha/unidade diferentes, quarentena após inspeção e atribuição desconhecida, pedidos aprovados, legado sem unidade e memo após durabilidade, emissão real que só confirma depois do recibo e repetição após render intermediário. AST dos três Python e sintaxe JS extraída + cenario.js passaram.

Contraprovas da base já entregues em 6241912132 (memo antes da escrita impede retry) e 6241983319 (recebimento de A reduz B). Testes novos não alteram fontes do revisor nem testes anteriores.

## Retorno P1–P6 (6242615315)

P1: est_dem de dados2.py usa a mesma identidade PC/item/unidade/linha e deduplicação de cenEstDem. P2: RECEB_DT conserva unidade/linha dos pedidos; previsão ambígua fica fora da oferta, registrada em recebNaoApuravel e sinalizada em Compras. P3: marcador de migração após recibo e antes de reset impede ressurreição do legado; com armazenamento disponível, o marcador preserva o reset entre sessões. P4: armazenamento bloqueado gera aviso distinto de cópia corrompida, inclusive no EST. P5: SOL_KEY referencia CEN_COMP_ANTIGA. P6: histórico da quarentena está no tooltip de uma única linha.

c34_paridade_test.py passou em 6 comparações das funções reais JS/Python: duas fazendas da previsão canônica, parcial deduplicado, multi-item, legado ambíguo e lotes de unidades diferentes. Extração AST evita importar o build inteiro. Ordens vazias e lotes explicitamente tratados como não vencidos delimitam o teste à previsão/recebimento; não valida vencimento, build completo nem navegador. Os 17 testes JS incluem reset antes/depois da migração e armazenamento bloqueado. Revisão cruzada e execução de navegador seguem pendentes.

## Retorno Q1/Q2 (6242793381)

Marcador tolera armazenamento ausente/bloqueado; reset restaura compras vazias em memória. Sem escrita disponível não promete persistir reset entre sessões. Identidade da NF é verificada contra todos os pedidos antes de escolher linha/item/unidade dentro do mesmo PC. 19 testes JS PASS, incluindo os dois contraexemplos devolvidos; AST Estoque PASS. Baterias completas citadas pelo revisor e navegador pendentes de reteste pelo Claude.
