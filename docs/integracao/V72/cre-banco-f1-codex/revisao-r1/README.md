# PR90 — correção da revisão6225872706

Autor Codex; contribuição do patch Claude7aceb3f; revisor/integrador Claude. Base7860b8191cbf23af6be43440eefdb992b9e79dca, fontes locais conferidas por Git blob contra árvore do HEAD.

Achados1–6 tratados: rótulo do botão no EXTRA real; Incluir documento visível e Bens e avaliações no menu de ações; residualGE08→PT04 removido; estado do contrato restaurado no cabeçalho; ficha vazia com mensagem própria; perda de papel sinalizada no campo visível. Refino do vazio distingue consulta, filtro sem resultados e erro de armazenamento. Achado7 também corrigido: reabrir valor formatado em pt-BR reutiliza credFichaDinheiro, sem float nem mudança no valor persistido. P7 do runnerClaude deve esperar850.000,50 (formato canônico), P8 continua12.500.000,00; erro/quota mantém texto original do rascunho.

Quatro arquivos alterados em gen37: areas/gestao.py, credito_ficha_build.py, credito_ficha_motor_unit.js e links_ocultos_test.py. Nenhum arquivoMENU2/ui37 ou domínioCAD02/credito_docs alterado. CRE F2 não iniciado.

Executado Codex: build com novo oráculo contra HEAD reproduzAssertionError no botão; build final passa, incluindo botão real, ordem de ações, status e vínculo da mensagem vazia; domínio18/18, motor real17/17, AST3 e node--check. Cinco regressões novas: vazio, consulta vazia, filtro sem resultado, armazenamento ilegível e zero versus pendente. Tentativa inicial do build em recorte sem catalogo.json falhou por montagem; três arquivos de contexto foram copiados da base local antes da reprodução válida. Primeiro novo teste de pendente omitiu operação no fixture; fixture corrigido, não defeito do produto.

Provas Claude lidas: ajustes/reg-rev_ficha_nav.log105/107, apenasP8 em1440/390; ajustes-links_ocultos_test.log16/16; contraprova-build-head.logAssertionError. Esses brutos são da propostaClaude anterior ao refino desta candidata; não afirmar107/107 nem navegadorCodex. Falhasgetest herdadas conforme revisão, não retestadas aqui. Bateria integral não executada.

PendênciasS4#8: título/parágrafo redundante e vocabulárioCompletar ficha/completo/falta/usado emN dossiês ainda registrados; contagemdossiê não inventada nesta F1. Idempotência protótipo não substituiENG021/022 na aplicação real. Contratos/dossiê/documentos/liberações sem primária global indevida conforme especificação. Conjunto incompleto.

Publicação não tentada: bloqueio prévio da revisão automática sobre exposição de fontes do mesmo projeto em81/88 segue sem autorização específica nova. Não usar90 como contorno. Código e provas ficam locais; HEAD90 continua7860b81. Gatilho: autorização específica para publicar estes quatro arquivos e provas no mesmoPR90; então conferirHEAD, enviar, Claude reconfere apenas deltaUI e integra se aceito. Produção/HML real não incluídos.

Atualização: publicação destas correções e provas autorizada expressamente por Adrianus em adrptu/Safrion-Software-. Bloqueio anterior superado; aguardar revisão afetada Claude e integração por ele.
