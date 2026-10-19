PROJETO: Safrion (Do Talhão à O.S.)
PEDIDO: Um padrão único e previsível para listas, cartões, linhas pai e filho, botões e menu ⋯ em todas as telas

CONTEXTO
- Pedido do proprietário: varredura completa de todas as telas, nos modos de visão Tabela e Cartões. Várias telas se comportam de forma diferente ao clicar nas linhas pai e filho, nos botões de ação e nos três pontinhos. Muitos ⋯ mostram só texto, sem ícones intuitivos. Quer um padrão para tudo, para o usuário não se perder mais: todas as telas com o mesmo comportamento previsível, melhor uso de botão × clicar na linha e cair direto no modal ou similar, com base nas melhores práticas globais de UX, UI e design system.
- Este pedido completa o EX-47 (ações das linhas no ⋯) e prevalece sobre ele onde houver diferença.

REFERÊNCIAS PARA TIRAR BOAS IDEIAS (não são requisito)
- Especificação viva com demonstração clicável: https://claude.ai/artifact/RFjMhybbxQwZX67TBFcB2U. É privado: o Claude lê com a ferramenta Artifact (action "read"); o Codex lê o arquivo padrao-listas-safrion.html, que o proprietário anexa. Traz as regras, a demonstração (tabela e cartões, linhas pai e filho, ⋯ com ícone e texto, painel lateral, confirmação, lote, teclado), as tabelas de decisão e o dicionário verbo → ícone.
- Relatório da varredura anterior: https://claude.ai/artifact/3MEq1jkELpA6ony4nVcwsJ (aba "Padrão ⋯").
- Melhores práticas usadas:
  - IBM Carbon, Data table e Overflow menu: linhas expansíveis, menu da linha e ações em lote; o menu é para opções a mais em linhas e cartões; ações que mudam dados de forma significativa ficam separadas por divisor, no fim; painel lateral quando o conteúdo expandido fica apertado.
  - Microsoft Fluent 2, Drawer: painel para informação e ações ligadas ao conteúdo; diálogo para confirmar.
  - Shopify Polaris, Index table: clicar no item leva ao detalhe; a seleção fica na caixa; lote para tarefa aplicada a muitos itens.
  - Nielsen Norman Group: o ⋯ é para ações secundárias (esconder ação-chave nele prejudica o uso); ícones não são universais, por isso ícone sempre com texto.
  - Material Design, Menus: item com ícone à esquerda, texto e divisores para agrupar.
  - WAI-ARIA Authoring Practices: treegrid, menu button e dialog (teclado e leitor de tela).

O QUE A VARREDURA ACHOU
Leitura do código das 261 listagens de 118 telas (motor de grades) e um robô que, em todas as 148 telas, clicou em cada lista nos modos Tabela e Cartões (380 testes): na linha, na linha pai, na seta, na linha filha, no ⋯ e no botão da linha.
- Clicar na linha faz coisas diferentes conforme a tela:
  - no código, cada listagem escolhe o que o clique abre: formulário de edição (105), consulta (58), "valor calculado, veja a origem" (50), função própria da tela (41) ou nada (7);
  - no robô: abriu consulta em 246 testes, formulário de edição em 105, nada em 15, outra tela em 11 e edição ou mudança na própria linha em 3. Sempre num painel lateral, o que é bom: o destino é o mesmo, o conteúdo é que muda.
- Linha pai e filha:
  - a seta expande e recolhe nos 12 casos testados;
  - o corpo da linha pai abriu edição em 4 árvores, consulta em 1, nada em 6 e mudou a tela em 1;
  - a filha abriu edição em 6 e consulta em 5.
- Botões na linha: 26 listagens têm botões de ação na célula e 58 têm links. No robô, 34 dos 42 botões executaram ou mudaram algo na tela sem abrir nada, 6 abriram formulário e 2 levaram a outra tela.
- Menu ⋯:
  - o motor já leva as ações da linha para o ⋯ (pedido de 15/10), mas só 5 listagens ligam isso, e o ⋯ só aparece se a linha também puder ser excluída; o robô não achou nenhum ⋯ de linha nas listas testadas;
  - o ícone dos itens vem de uma lista de 8 verbos (excluir, dividir, plano, vincular, editar, não plantar, desfazer, criar); qualquer outro verbo (Liberar, Conferir, Registrar…) recebe uma seta genérica, por isso o menu parece "só texto";
  - nos menus com ícone desenhado à mão, o mesmo ícone (caixa com check) serve para 9 verbos (aprovar, conciliar, concluir, conferir, encerrar, finalizar, liquidar, publicar, ver), e "Ver" aparece com 8 ícones diferentes;
  - os ⋯ de seção ("Mais ações de …") existem em 35 lugares, quase todos com ícone, mas com 1 ou 2 itens cada.
- Painéis de detalhe (a primeira linha de 36 telas do menu): nenhum tem ⋯, e as ações variam de tela para tela:
  - painel com 3 ou 4 botões, com o destrutivo ao lado da primária: Beneficiamento ("Retirar L39-119 da ordem", "Cancelar a ordem", "Voltar à lista", "Autorizar rota e liberar"); O.S. ("Liberar para execução", "Ajustar antes de liberar", "Cancelar sem execução");
  - painel só com "Fechar", sem próximo passo: EST, GE-02, GE-03, GE-07, GE-08, IC, IV, SU-07 e IN-02;
  - painel que abre direto em edição, com Cancelar e Salvar: CD-01, CD-03, CD-04, CD-05, CD-06, GE-04 (título a pagar), CA-02 (corrigir apontamento) e IR-01 (setor).
- Em Planos agronômicos (PA), o ⋯ das atividades mostra só texto ("Editar atividade", "Excluir atividade"), sem ícone.
- Cartões: nenhum dos 188 cartões testados recebe foco pelo teclado (nas tabelas, 9 de 192 listas sem foco). Em 9 listas, clicar no cartão não faz o mesmo que clicar na linha (CD-01det, CD-07, COLH, EST, GE-01, GE-05, IR-02, PCOM e PROD).

ORDEM DE TRABALHO: PRIMEIRO MELHORAR, DEPOIS IMPLANTAR
1. Claude e Codex, cada um sozinho, criticam este padrão contra o PRD, o NAV/DS, as decisões fixas e o motor de grades do protótipo (g2open, g2acaoIco, rmenu, modo Cartões, caret ▸/▾ e ›). Cada um lista o que adotar, adaptar ou descartar, e o que falta.
2. Divergência se resolve por fonte ou reprodução. O Gemini real entra só em decisão material de fluxo ou acessibilidade. Pacote mínimo, sem dados reais.
3. O Codex registra o padrão final no design system (fonte única, referenciada pelo PRD) e as fatias no checkpoint (só ele edita o checkpoint).
4. Implantação na fase registrada no STATUS: primeiro no motor de grades e nos componentes (uma mudança vale para as 261 listagens), depois as telas com listas próprias, com revisão cruzada (quem revisa integra o PR do outro).
Não simule o Codex nem o Gemini.

1. AS REGRAS (ver a demonstração)
1. Clicar na linha ou no cartão abre o registro: o detalhe no painel lateral, sempre em consulta, com estado, próximo passo e ações no topo. Nunca abre edição direta, nunca executa ação, nunca leva para outra tela.
2. A seta só expande: ▸ à esquerda abre e fecha os filhos no lugar. O corpo da linha pai abre o detalhe do pai; o da filha, o detalhe da filha, no mesmo painel, com a trilha "pai › filho" e voltar ao pai. Linha de grupo (Agrupar por), que não é registro, expande pelo clique em qualquer parte.
3. Ações no ⋯, com ícone e texto: toda ação da linha fica no ⋯ ao fim da linha ou no canto do cartão, sempre visível. Ordem: próximo passo em primeiro e em negrito; frequentes; divisor; consultar e documentos; divisor; destrutivas por último, em vermelho. Até 7 itens; mais que isso, vai para o detalhe.
4. Indisponível ensina: ação que o estado não permite aparece desabilitada com o motivo embaixo ("falta 1.140 kg de ureia"); ação que o papel não pode fazer não aparece.
5. Botão só para a ação principal: botão visível existe no topo do detalhe (a primária do estado, uma só), na barra da listagem (criar, importar, exportar a lista) e na barra de lote. Na linha, só em fila de trabalho de ação única e repetitiva, e só se o teste com usuários mostrar ganho.
6. O destino certo: painel lateral para ver e agir num registro (480 a 640 px; tela cheia no celular); modal central pequeno só para confirmar ou pedir motivo; página inteira para trabalho longo ("Abrir página completa" no painel); link no ID para ir a outra entidade.
7. Tabela e cartões são a mesma lista: mesmo clique, mesma seta, mesmo ⋯, mesma seleção e mesmo painel. O cartão recebe foco e abre com Enter, como a linha.
8. O contexto nunca se perde: com o painel aberto, a linha fica marcada; ↑ ↓ trocam de registro; Esc fecha e devolve o foco à linha; filtros, ordem, grupos abertos e rolagem ficam como estavam.

2. TABELAS DE DECISÃO
Onde cada clique leva:
| Clica em | Acontece | Componente | Nunca |
|---|---|---|---|
| Corpo da linha ou do cartão | Abre o detalhe em consulta, com estado, próximo passo e ações | Painel lateral | Edição direta, executar, navegar |
| Seta ▸ | Mostra ou esconde os filhos | Linha em árvore ou itens no cartão | Abrir detalhe |
| Linha de grupo | Expande ou recolhe; contagem e somas | Cabeçalho de grupo | Abrir painel |
| Linha filha | Detalhe da filha no mesmo painel, com trilha e voltar ao pai | Painel lateral | Abrir o pai |
| ⋯ | Menu de ações com ícone e texto | Menu (menu button) | Abrir painel ou executar direto |
| Item sem risco e sem dados | Executa e avisa com Desfazer | Aviso no rodapé | Confirmação extra |
| Item com dados | Formulário curto da ação, já preenchido | Painel lateral (modal se até 2 campos) | Formulário genérico de edição |
| Item destrutivo ou irreversível | Confirma com a consequência e, se a regra pedir, motivo | Modal pequeno, primária vermelha com verbo e objeto | "Tem certeza?" vago |
| ID de outra entidade | Abre aquela entidade, com voltar | Link | Botão com cara de link |
| Caixa de seleção | Marca; aparece a barra de lote | Barra de lote no topo | Abrir detalhe |
| "Editar" no detalhe | O painel passa a editar, com Salvar e Cancelar no rodapé | Mesmo painel | Outro modal por cima |
| Trabalho longo | "Abrir página completa" | Página do registro, voltar preservado | Modal grande rolando |

Botão, linha ou ⋯:
- Clique na linha: ver o registro e decidir; caminho padrão de toda lista.
- Botão primário no topo do detalhe: o próximo passo do estado, para quem tem permissão; um por painel.
- ⋯ na linha, no cartão e no detalhe: todas as ações do registro, com o mesmo conteúdo nos três lugares (fonte única de ações por estado e papel).
- Botão na barra da listagem: o que não é de um registro (criar, importar, exportar).
- Barra de lote: ação repetida em vários registros onde a regra permite (nunca liberar O.S. com produto).
- Link: ir para outra entidade; nunca executar.

3. DICIONÁRIO DE AÇÕES E ÍCONES
Um verbo, um ícone, em todo o sistema (biblioteca Lucide, licença livre, traço 2, 16 px no desktop e 20 px no toque). O ícone ajuda a achar; o texto diz o que acontece. Verbo novo entra no dicionário antes de entrar na tela, e o componente avisa em desenvolvimento quando um verbo não tem ícone (hoje o motor cai numa seta genérica).
- Avançar o processo: Liberar unlock · Programar calendar-plus · Reprogramar calendar-clock · Iniciar ou retomar play · Pausar pause · Apontar ou registrar clipboard-pen · Conferir clipboard-check · Confirmar check · Concluir ou encerrar check-circle · Aprovar ou autorizar shield-check · Decidir scale · Validar badge-check · Reabrir rotate-ccw · Reprocessar refresh-cw.
- Editar e organizar: Editar ou ajustar pencil · Duplicar copy · Dividir split · Agrupar ou mesclar merge · Vincular link · Atribuir ou convidar user-plus · Trocar produto replace · Comparar git-compare · Desfazer undo-2.
- Materiais e compras: Reservar lock · Requisitar clipboard-list · Separar package · Receber package-check · Devolver ao estoque package-minus · Transferir arrow-left-right · Pedir compra ou repor shopping-cart · Ler código scan.
- Comunicar e cobrar: Enviar ou encaminhar send · Comentar message-square · Lembrar ou avisar bell · Cobrar banknote.
- Consultar e ir para: Ver detalhe eye · Ver no mapa map-pin · Ver histórico history · Ir para a origem arrow-up-right.
- Documentos: Emitir documento file-text · Imprimir printer · Exportar ou baixar download · Importar upload · Anexar paperclip.
- Destrutivas (sempre por último, em vermelho): Cancelar x-circle · Recusar ou revogar ban · Inativar ou arquivar archive · Excluir trash-2.

4. MEDIDAS E ACESSIBILIDADE
- Linha: 40 a 48 px (56 px no toque); focável; Enter abre; em árvore, role treegrid com aria-expanded e aria-level.
- Cartão: focável, nome acessível pelo título, Enter abre; até 4 campos; ⋯ no canto superior direito; seta à esquerda do título quando tem filhos.
- Seta: 28 px (44 px no toque), sempre à esquerda; botão "Expandir T1"; → e ← no teclado.
- ⋯: 32 px (44 px no toque), sempre visível; botão de menu "Ações de OS-0424" (aria-haspopup e aria-expanded); ↑ ↓ Home End no menu; Esc devolve o foco; no celular, o menu vira folha inferior com itens de 48 px.
- Item do menu: ícone 16 px (20 px no toque) + texto; role menuitem; desabilitado anunciado com o motivo.
- Painel lateral: 480 px (consulta) a 640 px (formulário), tela cheia no celular; diálogo com título; foco no título ao abrir; Esc fecha e volta à linha.
- Modal de confirmação: até 480 px; uma pergunta; primária com verbo e objeto; foco preso.

5. O QUE MUDAR NO MOTOR DE GRADES (uma mudança vale para as 261 listagens)
- g2open: o clique na linha abre sempre o detalhe em consulta ("Editar" vira ação do detalhe, atalho E). Os modos form, ro, origin e pick viram um só: o detalhe, com a seção "Origem" quando o valor é calculado. pick só pode abrir o mesmo painel. none só para linha que não é registro (sem cursor de mão e sem foco).
- rmenu: ligado em todas as grades; o ⋯ aparece sempre que a linha tiver ação, sem depender de a linha poder ser excluída (hoje só aparece com sp.del).
- g2acaoIco: trocar as 8 regras com seta genérica pelo dicionário completo da seção 3, com aviso em desenvolvimento para verbo sem ícone.
- Ações por estado e papel numa fonte única, usada pelo ⋯ da linha, do cartão e do detalhe e pela primária do detalhe.
- Cartões: foco, papel acessível e Enter, iguais aos da linha; o mesmo clique da Tabela.
- Linha pai: corpo abre o detalhe do pai; seta expande. Linha de grupo do Agrupar por: expande inteira.
- Botões e links soltos na célula (act, cta) vão para o ⋯; links de ID continuam como link.
- Telas com lista própria (fora do motor) passam a usar o motor ou os mesmos componentes.

6. ACEITE OBSERVÁVEL (repetir o robô v4 depois: anexo-robo-v4.html, com as instruções no topo, e anexo-robo-v4-resumo.py)
- Em 100 % das listagens, o clique na linha abre o detalhe em consulta (hoje uma parte abre edição direta, outra não faz nada, outra navega).
- Em 100 %, Tabela e Cartões têm o mesmo resultado de clique.
- 100 % dos cartões focáveis e abertos por Enter.
- 100 % dos itens de ⋯ com ícone do dicionário e texto; nenhum verbo com dois ícones; nenhum ícone para dois verbos.
- ⋯ em toda linha com ação; nenhum botão de ação solto na linha fora da exceção registrada.
- Seta só expande; corpo do pai abre o pai; filha abre a filha com trilha.
- Teclado e leitor de tela: Tab, Enter, setas, Esc e foco de volta, conferidos com leitor de tela.
- Teste com 3 a 5 usuários por perfil (UX-13): "abrir um registro e fazer o próximo passo" e "achar uma ação no ⋯" com sucesso de 95 % ou mais, sem ninguém dizer que se perdeu.

7. NÃO FAZER
- Esconder a ação principal só no ⋯ (ela fica no topo do detalhe).
- Abrir modal por cima do painel para editar.
- Ícone sem texto no menu, ou dois ícones para o mesmo verbo.
- Mudar o comportamento conforme o modo (Tabela ou Cartões) ou conforme a tela.
- Lote em aprovação agronômica de O.S. com produto (decisão fixa).

8. ENTREGA (no canal registrado)
- Padrão final no design system, com o que Claude e Codex mudaram e por quê.
- Fatias (motor, componentes, telas próprias), com autoria e revisão.
- Nova medida do robô v4, antes e depois.
- Três listas curtas, com motivo: aplicado, deixado de fora, cortado.
- Suposições e pendências, cada uma com o gatilho de retomada.
