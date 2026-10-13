# EST-2 — item diferente no recebimento

Autor Codex; revisor/integrador Claude. Contrato6152932155 noPR47. Base5ec321ddad3019fbd66090fe8b0543b8066a8ff9 (claude/v44-v59), arquivo processo_estoque.py conferido byte a byte com a fonte remota. ID/severidade vêm do APENDICE do parecer0910: EST-2/S2. Escopo: recebimento de item diferente não pode virar o produto comprado, nem mesmo em quarentena.

Antes: a opção Item diferente do pedido só exigia observação; apto, quarentena e mistura gravavam com a identidade do pedido. Agora: erro junto ao campo e recusa do comando antes do recibo/estoque. Rascunho preservado, orientação para conferir com fornecedor e corrigir pedido antes de receber. Não resolve regularização de produto divergente, histórico já lançado, FEFO, validade, fazenda ou reserva; essas pendências conservam seus IDs.

Validação executada com dados sintéticos (Node24/Python3.12/Chromeisolado):
- est_item_divergente_test.py: base2/6(exit1; quatro reproduções); correção6/6(exit0). Inclui comando direto nos três destinos, formulário sem mutação, recebimento correto/apto e avaria/quarentena com idempotência.
- est_item_divergente_nav.py:12/12 em1440×1000/390×844; motivo, rascunho, armazenamento intacto, sem overflow, recuperação ao conferir itemcorreto e semerroJS.
- est_a4_test.py:53/53(exit0), regressão deestoque existente.
- build áreaEstoque e montar_render:exit0, dadossintéticos5/5. Sem banco/HML/publicação.

Reproduzir de tools/prototipo/v37/gen37 comNode noPATH e SAFRION_DADOS=sintetico: python3 est_item_divergente_test.py. GEN permite executar o teste contra fonte anterior. Para navegação: gerar areas.processo_estoque.build(), python3 montar_render.py, python3 est_item_divergente_nav.py. Brutos antes/depois/nav/a4 neste diretório.

Aplicado: erro contextual, estado intacto, recuperação no formulário existente. Fora: novo cadastro de produto ou fluxo de disputa/fornecedor; usar itens autorizados do registro. Cortado: entrada indevida inclusive na quarentena, sem criar tela/etapa. Suposição: regularizar a identidade antes da entrada; revisão críticaClaude pendente. Teste manual de teclado virtual não executado; nenhum controle novo foi criado.
