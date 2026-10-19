PROJETO: Safrion (Do Talhão à O.S.)
PEDIDO: Entrada de dados mais rápida e em lote, ações das linhas no menu ⋯ e revisão centrada no usuário de cada módulo

CONTEXTO
Três pedidos do proprietário, tratados juntos porque mexem nas mesmas telas:
- Varredura de 100 % do sistema para achar onde o usuário pode preencher mais rápido, mais fácil, de forma mais intuitiva e em lote, para máxima satisfação e produtividade.
- Revisão geral centrada no usuário: as necessidades essenciais estão excelentes em cada módulo, submenu, funcionalidade, tela, botão de ação, campo e modal?
- Concentrar os botões de ação das linhas das tabelas e dos cartões no menu ⋯ (três pontinhos), para tudo ficar mais limpo, intuitivo e padronizado.
E uma filosofia que vale para todos: resolver os problemas em 1 clique, mandando direto para o processo e a pessoa que resolvem a dor (detalhada no prompt-safrion-resolve-em-1-clique.md).

COMO A VARREDURA FOI FEITA
- Versão analisada: 1792184197-5a81 do protótipo (https://claude.ai/artifact/HqspGRcrX1wcayCVMe9emm), em 16/10/2026.
- Um robô abriu as 148 telas com o perfil Proprietário (todos os papéis). Em cada tela, fez o inventário (tabelas e as ações de cada linha, cartões e listas, campos e seus atributos) e clicou em cada ação (uma por verbo, a primeira linha de cada tabela, "selecionar todos"), capturando o que abriu: modal com campos e botões, navegação, menu ou edição na própria tela. Não preencheu nem enviou formulários, e não clicou em ações dentro de modais.
- Cinco revisões por área (Agronomia e planejamento; Ordens de serviço e campo; Suprimentos, estoque e manutenção; Colheita, packing e vendas; Gestão, cadastros e implantação) leram esses dados e o código das telas com os olhos de cada persona.
- Relatório interativo com todos os achados, formulários e ações na linha: https://claude.ai/artifact/3MEq1jkELpA6ony4nVcwsJ. É privado: o Claude lê com a ferramenta Artifact (action "read"). O Codex lê pelo arquivo anexo-varredura-achados.md, que o proprietário anexa.
- O código do robô vai no anexo-robo-varredura.html (com as instruções de uso no topo) e o resumo da saída no anexo-robo-resumo.py, para repetir a medida depois de cada onda.

O QUE A MEDIDA MOSTROU
- 148 telas abertas e 488 ações clicadas no primeiro nível.
- 174 modais e painéis com campos, somando 810 campos:
  - 130 digitados à mão (16 %);
  - 279 escolhidos em lista (34 %);
  - 110 pré-preenchidos (14 %);
  - 290 calculados ou só leitura (36 %).
- Números: 30 de 90 sem teclado numérico e 42 de 90 sem unidade ao lado.
- Datas: 42 de 43 sem atalho (Hoje, Ontem, +7).
- Ações nas linhas: 85 tabelas e listas com botões de ação soltos na linha; só 1 usa o ⋯ (CA-03det "Mais ações").
- Lote: só 1 tela mostra ações ao marcar "selecionar todos" no primeiro nível; e as liberações em lote que existem (PL-04 "Liberar prontas", CA-01 "Liberar selecionadas") incluem O.S. com produto, contra a decisão fixa (EX-32 continua aberto).
- Revisão: 187 achados, 57 de prioridade alta. Por tipo: Entrada mais rápida 40 · Resolver em 1 clique 35 · Ações no ⋯ 27 · Necessidade essencial 24 · Modal e botões 20 · Erro ou risco 19 · Lote 13 · Clareza 9.
- Padrões que atravessam os módulos:
  - falta de insumo, peça ou embalagem aparece sem a ação que resolve (O.S., Estoque, Necessidades, Beneficiamento, OM corretiva); só a OM preventiva resolve em 1 clique;
  - entrada que o sistema poderia capturar ou calcular: NF-e no recebimento, balança na pesagem, arquivo do laboratório no laudo, conjunto já cadastrado no rendimento;
  - telas fora do menu, ou antigas, duplicam funções com números diferentes (SU-01 a SU-09, VE-*, LO-*, PT-*, links do Financeiro): uma só verdade por entidade (EX-01, EX-02);
  - o próximo passo existe, mas a primária não segue a pendência real (Meu dia, fechamento de custos, aprovações).

ORDEM DE TRABALHO: PRIMEIRO MELHORAR, DEPOIS IMPLANTAR
1. Claude e Codex, cada um sozinho, validam os achados no código vigente: Confirmado (com arquivo e trecho), Refutado (o que a varredura viu errado) ou Já resolvido. Para cada confirmado: Adotar, Adaptar (como) ou Rejeitar (por quê). Cada um aponta o que a varredura deixou de fora, em especial nas ações dentro dos modais, que o robô não clicou.
2. Divergência se resolve por fonte ou reprodução. O Gemini real entra só em decisão material de domínio ou fluxo. Pacote mínimo, sem dados reais.
3. O Codex registra o desenho final, as ondas e as fatias no checkpoint (só ele edita o checkpoint).
4. Implantação na fase registrada no STATUS: primeiro no protótipo, depois na aplicação Next, com revisão cruzada (quem revisa integra o PR do outro).
Não simule o Codex nem o Gemini.

1. ENTRADA INTELIGENTE (EX-46)
Regra: o usuário só informa o que o sistema não sabe. Para cada campo de cada formulário, escolher o primeiro método que se aplica, nesta ordem:
1. Calculado (total = dose × área, nº de tanques, horas pelo horímetro, peso líquido corrigido, custo), em só leitura, com a origem visível e editável no lugar quando a regra permitir.
2. Herdado do contexto confiável (fazenda, safra, talhão, O.S. de origem, data da operação), mostrado e revisável.
3. Capturado (QR ou código de barras, XML de NF-e, balança, telemetria, GPS, foto, voz).
4. Escolhido em lista com busca tolerante (acento, código, apelido), com os mais usados em chips; criar o cadastro que falta no próprio campo.
5. Padrão seguro, sempre visível e trocável.
6. Digitado, com o teclado certo (numérico com vírgula), unidade ao lado, máscara que aceita colar e validação ao sair do campo dizendo como corrigir.
Regras que não mudam:
- medição, dose, lote e quantidade real nunca vêm do último valor (decisão fixa);
- data da operação ≠ data do registro; executor ≠ usuário logado;
- datas com atalhos (Hoje, Ontem, Amanhã, +7);
- formulário com 3 a 5 campos visíveis e "Mais opções" para o resto;
- uma ação primária por contexto.
Lote:
- seleção de linhas com barra de lote no topo e resultado por linha (feitas, com erro, pendentes), repetindo só as pendentes;
- grade editável e colar de planilha onde se lançam muitas linhas iguais (vistorias, pesagens, inventário, laudos);
- duplicar e modelo para registros parecidos;
- nunca lote em aprovação agronômica de O.S. com produto (decisão fixa).

2. AÇÕES DA LINHA NO MENU ⋯ (EX-47)
Padrão único para toda tabela e toda lista de cartões. Demonstração clicável na aba "Padrão ⋯" do relatório.
- Clique (ou Enter) na linha ou no cartão abre o detalhe: ao lado, no desktop; em tela cheia, no celular. O detalhe tem a ação primária do estado.
- A linha mostra o estado e o próximo passo em texto, com verbo, sem botão.
- Todas as ações ficam no ⋯ ao fim da linha ou no canto do cartão, sempre visível (não só no hover), com alvo de 36 px (48 px no app) e nome acessível "Ações de OS-0424".
- Ordem no menu: o próximo passo em primeiro e em negrito; depois as ações frequentes; separador; por último as raras e as destrutivas, em vermelho.
- Ação que o estado não permite aparece desabilitada com o motivo ("falta receituário"). Ação sem permissão do papel não aparece.
- Links de ID (OS-0421, REC-014) seguem como links de navegação.
- Seleção múltipla: caixa na primeira coluna e barra de lote no topo com a contagem, só onde o lote é permitido.
- Teclado: Tab chega na linha; Enter abre; o ⋯ abre com Enter ou Espaço; setas andam no menu; Esc fecha e devolve o foco.
- Um componente do design system para tabela com ⋯, cartão com ⋯ e barra de lote, usado em todas as telas (EX-41).
- O motor de grades do protótipo já tem a opção rmenu, que leva os botões de ação da linha para o ⋯ e põe Excluir por último (pedido do proprietário em 15/10). Segundo a revisão, só a SAF a liga, e o ⋯ só aparece quando a linha também pode ser excluída. Ligar em todas as grades e mostrar o ⋯ sempre que a linha tiver ação. O CA-03det tem um "Mais ações" à parte, que deve passar a usar o mesmo componente.
- Exceção só com medida: se o teste com usuários mostrar que uma fila de trabalho de ação única e repetitiva (por exemplo, a fila de conferência) fica mais lenta com o ⋯, a linha pode manter um botão de texto com o próximo passo. A exceção fica registrada com a medida.

3. REVISÃO CENTRADA NO USUÁRIO POR MÓDULO (EX-48)
Para cada módulo e cada persona, a revisão respondeu: a tarefa mais frequente e a decisão mais importante estão na primeira tela, claras e completas? Falta algo essencial? Sobra ruído? Os achados estão no relatório, com tela, elemento, o que acontece hoje, a proposta, o método, o ganho, a prioridade, a evidência e o cuidado. Resumo por área:
- Agronomia e planejamento (37 achados, 14 altos):
  - "Liberar prontas" (PL-04) libera em lote O.S. com produto (liberou a OS-0430, glifosato e 2,4-D). Trocar por "Conferir prontidão" e pôr "Pedir liberação" no ⋯ de cada O.S. (EX-32).
  - Decisão de controle (AG-01) pré-escolhe o 1º produto registrado mesmo sem estoque. Ordenar por "Conferido", mostrar "estoque 10 de 38 L" e o grupo, oferecer "Pedir compra".
  - Falta de ureia na OS-0418 só oferece "Abrir O.S."; no ⋯: "Propor troca de fonte" com a dose recalculada pelo N, "Pedir compra" e "Pedir transferência".
  - Recomendação (AG-04det) troca produto em 5 campos de texto livre, sem conferir registro ao salvar a versão. Lista do Agrofit para cultura × alvo e checagem ao salvar.
  - Laudo de solo (AG-02) aceita 6 de 15 resultados e não importa o arquivo do laboratório. Importar com prévia do que entrou e falhou.
  - Lote real: programar vistorias atrasadas e programar irrigação de vários setores numa ação.
  - Safra como uma entidade só (listagem → detalhe), em vez de telas espalhadas.
- Ordens de serviço e campo (38 achados, 13 altos):
  - Quadro "Insumos × estoque" no detalhe da O.S.; "Pedir compra urgente" e "Trocar produto" (lista do AG-01) em 1 clique.
  - Aprovações (IN-02) não lista as O.S. com produto que aguardam o agrônomo; aprovar não abre a próxima (UX-06).
  - "Liberar selecionadas" (CA-01) inclui O.S. com produto: o lote só pode levar as já aprovadas uma a uma.
  - Fila "A separar" do almoxarife (web e app), por início da janela, com lote, validade e local.
  - "Executado como planejado" em 1 toque no app; conferência por exceção (só a divergência).
  - "Meu dia" decide no lugar e a próxima ação segue o impedimento ("Pedir compra", "Trocar produto"); "Liberar" só quando nada impede.
  - Reserva na fazenda da O.S., em vários lotes, primeiro o que vence antes.
- Suprimentos, estoque e manutenção (38 achados, 11 altos):
  - Compra de insumo fora do plano não existe (a avulsa proíbe safra e cultura). Tipo "Insumo fora do plano" com motivo, vínculo e impacto no orçamento.
  - Necessidade atrasada (óleo mineral, 2,4-D, glifosato para 25/09) sem "Comprar urgente"; falta no Estoque sem "Pedir ao Compras".
  - OM corretiva sem "Incluir peça" com saldo, reserva e compra.
  - Recebimento sem leitura de NF-e (11 campos, 5 digitados); "Conferido como na nota" e só a divergência digitada.
  - Contagem cíclica em lote pela seleção de lotes, com leitura do código no app.
  - Menu de Suprimentos com telas duplicadas (SU-01 a SU-09 fora do menu, números diferentes do EST e do CMP): uma listagem por entidade.
  - Aprovação de compra com bloco de decisão: valor, R$/ha, orçado, comprometido e saldo.
- Colheita, packing e vendas (34 achados, 8 altos):
  - Falta de caixas no beneficiamento sem saída ("a compra é do BEN-2"): "Pedir N caixas" em 1 clique; lista de materiais por rota.
  - Pesagem digita ticket, bruto e tara: "Ler balança" com captura de ticket, peso e hora, sem usar o peso anterior.
  - Inspeção lote a lote (4 formulários para 2 lotes): grade com "Marcar todos conforme" e "Liberar os conformes".
  - Expedição sem conferir NF e lacre (só nas telas LO, fora do menu).
  - Links do Financeiro abrem telas antigas com números diferentes (R$ 244 mil × R$ 91.470): uma só verdade.
  - Listas de opções de outro assunto ("Preventiva/Corretiva" num documento de carga).
- Gestão, cadastros e implantação (40 achados, 11 altos):
  - Financeiro e indicadores sem lugar no menu: agrupar num hub existente, sem criar o 10º nome. (Atualização de 18/10: os indicadores ganharam o Painel, 10º item da barra; ver EX-53.)
  - Plano de ação nasce do desvio já preenchido (origem, efeito, causa, dono).
  - Fechamento de custos com a primária seguindo a próxima pendência ("Ratear frete · R$ 1.463").
  - Cadastro de operação com texto livre para o conjunto: busca na CD-03 com "Criar conjunto" no campo.
  - "Importar talhões (KML, shapefile, planilha)" na CD-01, com a mesma prévia do ON-01det.
  - Remessa de pagamento com resumo antes de enviar; "Lembrar aprovador" e "Aprovar pagamento" no ⋯.
  - Permissão de decidir só na configuração de papéis (CF-01), não no cadastro de habilidades.

4. ONDAS SUGERIDAS (o Codex decide)
- Onda 1: componentes do design system (tabela com ⋯, cartão com ⋯, barra de lote, campo numérico com unidade, campo de data com atalhos, busca com chips) e a regra de entrada no guia de formulários.
- Onda 2: achados de prioridade Alta, módulo por módulo, começando pelos fluxos diários (O.S., app de campo, almoxarifado, vistoria, pesagem).
- Onda 3: lote e grade editável onde há lançamento repetitivo.
- Onda 4: achados de prioridade Média e Baixa que passarem no critério de entrada.
Cada item vira fatia com ID, persona, arquivos, autor, revisor e aceite observável, no Double Diamond.

5. ACEITE OBSERVÁVEL (repetir o robô depois de cada onda)
- Campos digitados à mão: de 130 para no máximo 65, sem perder medição real.
- Números: 100 % com teclado numérico e unidade ao lado (hoje 30 de 90 sem teclado e 42 sem unidade).
- Datas: 100 % com atalhos (hoje 42 de 43 sem atalho).
- Linhas e cartões: nenhum botão de ação solto fora do ⋯, salvo exceção registrada (hoje 85 tabelas e listas com botões de ação na linha, 1 com ⋯).
- Uma ação primária por contexto em 100 % dos modais (hoje 1 modal com duas: AG-01, VIS-055).
- Os 57 achados de prioridade alta resolvidos ou com motivo registrado.
- Tarefas da linha de base (UX-03) com menos interações e tempo, sem aumento de erro; SUS e sucesso com 3 a 5 usuários por perfil (UX-13).

6. NÃO FAZER
- Pré-preencher medição, dose, lote ou quantidade com o último valor.
- Lote em aprovação agronômica de O.S. com produto.
- Esconder ação essencial só no hover, ou esconder o estado e o próximo passo para "limpar" a linha.
- Criar tela nova para entrada em lote quando a grade da própria listagem resolve.
- Mexer nas decisões fixas.

7. ENTREGA (no canal registrado)
- Tabela dos achados com: validação e evidência · decisão Claude · decisão Codex · decisão final · onda · ganho medido (antes → depois) · esforço · risco.
- O que a varredura deixou de fora, segundo Claude e Codex, e como foi tratado.
- A nova medida do robô depois de cada onda.
- Três listas curtas, com motivo: aplicado, deixado de fora, cortado.
- Suposições e pendências, cada uma com o gatilho de retomada.
