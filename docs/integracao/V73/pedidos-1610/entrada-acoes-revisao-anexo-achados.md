# Varredura do Safrion · achados

Versão 1792184197-5a81 do protótipo, 16/10/2026. Perfil Proprietário (todos os papéis). Contagens medidas pelo robô no estado inicial de cada tela e no primeiro nível de cada ação (um clique por verbo, a primeira linha de cada tabela). Ações dentro de modais não foram clicadas, e nenhum formulário foi preenchido ou enviado. Achados vêm de cinco revisões por área sobre esses dados e sobre o código das telas; confirme cada um no código vigente antes de implantar. Dados do protótipo são sintéticos.

## Medidas

- Telas abertas: 148 · ações clicadas: 488.
- Modais e painéis com campos: 174, com 810 campos: 130 digitados, 279 escolhidos em lista, 110 pré-preenchidos, 290 calculados ou só leitura.
- Números: 90, sendo 30 sem teclado numérico e 42 sem unidade ao lado. Datas: 43, sendo 42 sem atalho.
- Tabelas e listas com botões soltos na linha: 85; com menu ⋯: 1.

## Achados (187), em ordem de prioridade

### AGRO-01 · Alta · PL-04 · Erro ou risco
- Módulo: Planejamento
- Nível: Lote
- Elemento: Botão primário 'Liberar prontas' (Ordens do período 23–29/09)
- Persona: planejador (PCP)
- Hoje: A primária verde da tela libera em lote as O.S. 'A liberar'. O clique liberou a OS-0430 (dessecação T1-A com glifosato e 2,4-D) e gravou 'liberada por Ana (agrônoma)'; as outras 4 ficaram com o motivo. Liberar O.S. com defensivo é a aprovação agronômica, que é individual.
- Proposta: Trocar a primária por 'Conferir prontidão' (só mostra prontas e travas, não libera). Na O.S. agronômica pronta, o ⋯ traz 'Pedir liberação a Ana', que põe a O.S. na fila dela (aprovou, abre a próxima, UX-06). Lote só para O.S. de água sem produto, que não passa pelo agrônomo.
- Método: Outro
- Ganho: fim da liberação em lote fora da alçada; PCP vê a prontidão em 1 clique; Ana libera uma a uma sem trocar de tela
- Evidência: v3out/PL-04.json results 'Liberar prontas' status 'Liberada 1 de 5 A liberar — OS-0430 ✓ liberada por Ana (agrônoma)…'; v3/PL-04.dc.html linha 57 SPEC q75 opts ['Preparar O.S. do período','Conferir prontidão','Liberar prontas',…]; CEN0 (v3/AG-01.dc.html) OS-0430 ins Glifosato 480 + 2,4-D 806
- Cuidado: Decisão fixa: aprovação agronômica individual por O.S., sem lote nem pré-autorização; servidor revalida prontidão.

### AGRO-02 · Alta · AG-01 · Resolver em 1 clique
- Módulo: Agronomia
- Nível: Modal
- Elemento: Formulário 'Decidir controle' · lista de produtos registrados (receituário)
- Persona: agrônomo e RT
- Hoje: A lista já traz só produtos registrados no Agrofit para cultura × alvo e marca carência, rotação e estoque. Mas o formulário pré-seleciona o 1º produto sem trava, e falta de estoque é só aviso. No VIS-013 (P1 feijão × mosca-branca, 95 ha) o 1º da lista é Ciantraniliprole 100 OD, sem nenhum lote no estoque; Acaricida D tem 10 L (precisa 38 L na dose mínima); Inseticida B repete o IRAC 1B da última aplicação. A linha diz 'Sem estoque', sem quanto há nem como resolver.
- Proposta: Ordenar a lista: 'Conferido' primeiro, depois avisos, travas no fim; pré-selecionar o primeiro Conferido. Mostrar em cada linha 'Estoque: 10 de 38 L' e o grupo IRAC/FRAC. Se nenhum cobre: botão 'Pedir compra de 28 L' (rascunho para Suprimentos com cultura, alvo, produto e data), sem sair da decisão.
- Método: Padrão seguro
- Ganho: evita receituário de produto sem estoque e O.S. parada em 'A liberar'; troca de produto sem cancelar receituário
- Evidência: v3/AG-01.dc.html agDecIni: ok=L.find(u=>!mipChecks(…).tr.length)||L[0]; mipChecks: falta de estoque entra em al (aviso), não em tr; MIPD.agf['Feijão|mosca-branca'] ordem Ciantraniliprole, Acaricida D, Inseticida B, Piriproxifem; CEN0.lotes sem Ciantraniliprole; 'Acaricida D|AD26-02' fisico 10 L; MIP0.apl P1 inseticida-b 08/09
- Cuidado: Receituário emitido nunca é reaproveitado (nasce outro); registro, dose de bula e carência seguem travas; a escolha é do RT.

### AGRO-03 · Alta · PL-04 · Resolver em 1 clique
- Módulo: Planejamento
- Nível: Linha da tabela
- Elemento: Linha OS-0418 fertirrigação P1 · selo 'Falta insumo · Ureia 45%' · ação 'Abrir O.S.'
- Persona: planejador (PCP)
- Hoje: A linha mostra a falta e só oferece 'Abrir O.S.'. A O.S. pede 1.140 kg de Ureia 45 % (12 kg/ha × 95 ha) e não há lote de ureia. Há fontes de N com saldo: nitrato de amônio 4.500 kg (Almox. Lagoa Grande), nitrato de cálcio 1.000 kg e nitrato de potássio 600 kg (Galpão 1). O PCP precisa abrir a O.S. e acionar agrônomo e comprador por fora.
- Proposta: No ⋯ da linha, nesta ordem: 1) 'Propor troca de fonte' — abre a O.S. em 'Ajustar antes de liberar' com as fontes com saldo e a dose recalculada pelo nutriente (kg de N/ha ÷ garantia do produto), para o agrônomo aceitar; 2) 'Pedir compra de 1.140 kg' (rascunho para Suprimentos); 3) 'Pedir transferência' do lote da outra fazenda.
- Método: Resolver em 1 clique
- Ganho: 3–4 telas e 2 contatos → 1 clique com contexto; a decisão técnica fica com o agrônomo
- Evidência: v3/PL-04.dc.html GRIDS g_ord o418 {sel:'Falta insumo · Ureia 45%', ab:'Abrir O.S.'}; CEN0 (v3/AG-01.dc.html) OS-0418 ins Ureia 45% dose 12 kg tot 1140; lotes 'Nitrato de amônio|LG26-06' 4500 kg, 'Nitrato de cálcio|ND26-16' 1000 kg, 'Nitrato de potássio|ND26-17' 600 kg
- Cuidado: Trocar insumo muda a instrução técnica: exige nova liberação pelo agrônomo; servidor é autoridade de saldo e reserva.

### AGRO-04 · Alta · AG-04det · Entrada mais rápida
- Módulo: Agronomia
- Nível: Modal
- Elemento: Painel 'Criar v4 · saldo de 70 ha' (TS registrado para cisto, Dose, KCl, Alcance, Aprovador RT)
- Persona: agrônomo e RT
- Hoje: A troca do tratamento de sementes sem registro por um registrado é feita em 5 campos de texto livre, já preenchidos: produto ('Pasteuria nishizawae FS'), dose com unidade no texto ('0,3 L/100 kg de sementes'), 'mantém a v3 (105,6 kg/ha)', 'saldo de 70 ha' e aprovador 'Ana'. Nada liga ao Agrofit, à bula ou ao estoque.
- Proposta: Produto por lista dos registrados para soja × nematoide-de-cisto (base do AG-07), com estoque e grupo; dose numérica com a unidade e a faixa da bula ao lado, sem valor inicial; KCl, alcance (saldo 70 ha) e aprovador (RT do talhão) vêm do contexto, só leitura.
- Método: Lista ou busca com autocompletar
- Ganho: 5 → 2 campos (produto e dose); registro e faixa de dose conferidos na entrada
- Evidência: v3/AG-04det.dc.html linha 52 drawer 'Criar v4 · saldo de 70 ha' inputs type=text ids tsregistradoparacisto, dose, kcl, alcance, aprovadorrt; linha 57 SPEC d2 label 'Criar v4 com TS registrado'
- Cuidado: Dose nunca vem com o último valor; a v4 segue para aprovação do RT; o realizado na v2 não muda.

### AGRO-05 · Alta · AG-04det · Erro ou risco
- Módulo: Agronomia
- Nível: Detalhe
- Elemento: Tabelas 'Itens' (coluna Registro Agrofit) e 'Versões' da REC-014
- Persona: agrônomo e RT
- Hoje: O TS nematicida (abamectina) aparece 'Sem registro p/ nematoide-de-cisto', mas a v2 que o contém está 'Em uso nos 30 ha realizados' (OS-0420). A trava só aparece na v3 ('TS travado · sem registro'). A evidência não mostra em que ponto a v2 deveria ter sido barrada.
- Proposta: Conferir registro (cultura × alvo), faixa de dose da bula e carência ao salvar cada versão da recomendação; 'Enviar para aprovação' fica desligado com a causa e, ao lado, os registrados com estoque para trocar.
- Método: Outro
- Ganho: uso sem registro barrado antes da compra e da O.S.
- Evidência: v3out/AG-04det.json inv.tables[0] linha 'TS nematicida (abamectina) … Sem registro p/ nematoide-de-cisto'; inv.tables[1] v2 'Em uso nos 30 ha realizados', v3 'TS travado · sem registro'; v3out/AG-04.inv2.json 'Recomendações 1 uso sem registro (REC-014)'
- Cuidado: Travas de receituário e registro são decisão fixa; não reescrever o realizado.

### AGRO-06 · Alta · AG-02 · Necessidade essencial
- Módulo: Agronomia
- Nível: Modal
- Elemento: Modal 'Registrar laudo de solo' · bloco de resultados
- Persona: agrônomo e RT
- Hoje: O formulário aceita 6 resultados (Ca, Mg, K, H+Al, Al, Argila). Os laudos da base trazem 15 (também pH, P, MO, S, B, Cu, Fe, Mn, Zn) e a listagem mostra pH, P e MO. Laudo lançado à mão fica sem pH e P, que pesam na calagem e na adubação fosfatada.
- Proposta: Mostrar o painel completo do laboratório (as linhas do padrão do lab, na ordem do laudo), com a unidade padrão do laboratório escolhido; linha vazia não grava.
- Método: Modelo ou duplicar
- Ganho: laudo completo; nenhuma recomendação calculada com dado faltando
- Evidência: v3/AG-02.dc.html SO_AN=['Ca','Mg','K','H+Al','Al','Argila']; SOLO0.laudos LAU-2043 com 15 atributos (pH, P, MO, S, B, Cu, Fe, Mn, Zn…); v3out/AG-02.json inv.tables[0].heads V %, PH, P, K, MO
- Cuidado: O laudo nasce 'Aguardando validação'; OCR e lançamento nunca validam.

### AGRO-07 · Alta · AG-02 · Lote
- Módulo: Agronomia
- Nível: Lote
- Elemento: Botão 'Registrar laudo' e campo 'Arquivo do laudo (PDF)'
- Persona: agrônomo e RT
- Hoje: Um laudo por vez: 17 campos (7 digitados, 10 escolhidos). O 'Arquivo do laudo (PDF)' é um campo de texto em que se digita o nome do arquivo; não há envio de arquivo. Um lote do laboratório com 20 amostras (talhão × profundidade) pede 20 modais.
- Proposta: 'Importar resultados do laboratório' (planilha/CSV ou vários PDFs): prévia com uma linha por amostra, talhão e profundidade casados pelo código da amostra, o que entrou e o que falhou; cada laudo nasce 'Aguardando validação'. A validação segue uma a uma com 'Validar e abrir o próximo'.
- Método: Captura (arquivo do laboratório)
- Ganho: 20 modais × 17 campos → 1 importação + conferência só do que falhou
- Evidência: v3out/AG-02.json results 'Registrar laudo' (17 campos; 'Arquivo do laudo (PDF)' type text, ph 'laudo.pdf'); v3/AG-02.dc.html linha 52 input id rl_arq sem type=file (0 ocorrências de type="file")
- Cuidado: Só o agrônomo valida; amostra repetida é recusada; prévia do que entrou e falhou (P22).

### AGRO-08 · Alta · PL-02 · Erro ou risco
- Módulo: Planejamento
- Nível: Campo
- Elemento: Campo 'Decisão da pendência' no modal da operação vencida (C1 · adubação pós-colheita)
- Persona: agrônomo e RT
- Hoje: A decisão vem pré-escolhida como 'Realizada'. Basta 'Salvar' para dar como feita uma operação vencida, sem O.S. ou apontamento ligado — o próprio texto pede 'consulte o realizado e decida'.
- Proposta: Campo sem valor inicial; mostrar ao lado o realizado encontrado (O.S. e apontamento do talhão). 'Realizada' só com O.S. ou apontamento vinculado; 'Não aplicável' pede motivo.
- Método: Padrão seguro
- Ganho: evita baixa falsa da necessidade (estoque, custo e planejado × realizado)
- Evidência: v3out/PL-02.json results 'Decidir pendência' → campo 'Decisão da pendência' select v='Realizada' (opções Realizada, Pendente, Não aplicável)
- Cuidado: P13: estado só muda por ação; rastreabilidade plano → O.S. → apontamento.

### AGRO-09 · Alta · SAF · Necessidade essencial
- Módulo: Safra
- Nível: Tela
- Elemento: Planejar safra (etapas 1–4) × PL-01 Safras e grade de cultivo × PL-06 Parcelas × PL-03 Capacidade
- Persona: planejador (PCP)
- Hoje: A mesma safra é tratada em telas paralelas: lista de safras e 'Nova safra' no PL-01 e no SAF; grade de cultivos no PL-01 e no SAF; divisão em parcelas no PL-06 e no SAF (o próprio PL-06 diz 'No Planejar safra, use Dividir em parcelas'); capacidade no PL-03 e na etapa 3 do SAF. O planejador não sabe onde a mudança vale.
- Proposta: Uma entidade Safra: listagem (safra, estado, próximo passo) → detalhe com seções Cultivos e parcelas, Plano operacional, Capacidade e Demanda de insumos. PL-01, PL-03 e PL-06 viram seções desse detalhe ou saem.
- Método: Outro
- Ganho: 4 telas → 1 detalhe; um só jeito de criar e dividir
- Evidência: v3/SAF.dc.html GRIDS g_saf, g_cult_*, g_cap_*, g_op, g_dem; v3out/PL-01.json tabelas de safras e de cultivos; dumps/PL-06.txt drawer 'Simular parcelamento … No Planejar safra, use Dividir em parcelas'; v3/PL-05.dc.html i4 'Ver capacidade' → SAF.dc.html#saf=S2627&passo=operacoes
- Cuidado: Preservar versões do plano, ajustes locais e histórico do talhão.

### AGRO-10 · Alta · PL-01 · Erro ou risco
- Módulo: Planejamento
- Nível: Modal
- Elemento: Modal '+ Criar safra' (PL-01) e formulário 'Safra' (SAF)
- Persona: planejador (PCP)
- Hoje: Dois formulários para a mesma coisa. PL-01: nome e 'Período' em texto livre ('Ex.: set/2027 – ago/2028') e 1 fazenda entre 2 (sem Lagoa Grande). SAF: início e fim em data, 3 fazendas e um campo 'Estado' (Rascunho / Em planejamento) escolhido à mão. Nenhum oferece copiar da safra anterior.
- Proposta: Um só 'Criar safra': nome e datas sugeridos pela safra anterior + 1 ano, fazendas do contexto, opção 'Copiar cultivos e planos da safra anterior' marcada; o estado nasce Rascunho e só muda por ação (Enviar para aprovação).
- Método: Modelo ou duplicar
- Ganho: 4–5 campos digitados → 0–1; nenhum estado editado à mão
- Evidência: v3out/PL-01.json results '+ Criar safra' (Nome text, Período text, Fazenda nOpt 2); dumps/SAF.txt g_saf edit fields ini/fim date, fazs multi 3 opções, estado sel ['Rascunho','Em planejamento']; busca por 'Copiar' sem resultado em v3/SAF.dc.html e v3/PL-01.dc.html
- Cuidado: P13: estado só por ação; contexto Fazenda·Safra herdado (P27).

### AGRO-11 · Alta · MOD-AGR · Necessidade essencial
- Módulo: Módulos
- Nível: Menu
- Elemento: Menu Agrícola (Planejamento · Execução · Resultados)
- Persona: planejador (PCP)
- Hoje: O menu tem 14 entradas e nenhuma leva a Programação integrada (PL-04), Capacidade (PL-03), Impedimentos (PL-05), Diagnósticos (AG-03) ou Recomendações (AG-04). PL-04 só é alcançado a partir do PL-03 e do PL-05; nenhuma tela leva ao PL-03. PL-04 repete funções do CA-01 'Ordens de campo' ('Preparar O.S. do período').
- Proposta: Programação e Impedimentos como visões da listagem de O.S. (filtros 'Período' e 'Impedidas'), com entrada 'Programação' no grupo Execução; 'Recomendações' (receituários) no grupo Execução, para o RT achar o que assinou.
- Método: Outro
- Ganho: PCP chega à tarefa diária em 1 clique; uma listagem em vez de duas
- Evidência: v3out/MOD-AGR.json inv.links (14); referências a 'PL-04.dc.html' só em v3/PL-03 e v3/PL-05, a 'PL-03.dc.html' em nenhuma tela; v3out/CA-01.json primária 'Preparar e emitir período'; v3/PL-04.dc.html SPEC q75 'Preparar O.S. do período'
- Cuidado: P65: sem menu por perfil; P11: programação é visão da mesma listagem, não tela nova.

### AGRO-12 · Alta · IR-02 · Lote
- Módulo: Irrigação
- Nível: Lote
- Elemento: Modal 'Programar irrigação' (campo Setor) a partir do IR-01
- Persona: técnico de irrigação
- Hoje: Programa um setor por vez: escolher o setor, conferir a janela sugerida e programar. A lista do IR-01 tem 23 setores na Lagoa Grande e o seletor traz 20 com déficit; à noite o técnico repete o modal para cada pivô.
- Proposta: No IR-01, selecionar setores (ou chip 'Acima do limite') → 'Programar N setores': uma O.S. por setor, janelas encadeadas por bomba e vazão outorgada, prévia do que trava (bomba parada, sem vazão) e do que entra.
- Método: Lote por seleção
- Ganho: 10 setores: 10 modais → 1 seleção + 1 confirmação
- Evidência: v3out/IR-02.json results 'Programar irrigação' (1 campo, Setor nOpt 20); v3out/IR-01.json inv.tables[0] nRows 23; v3/IR-02.dc.html irrSugerir e irrChecar (bomba, parada, outorga) por setor
- Cuidado: Água sem produto libera ao programar; fertirrigação segue com o agrônomo; outorga e conflito de bomba continuam travas.

### AGRO-13 · Alta · PL-02 · Entrada mais rápida
- Módulo: Planejamento
- Nível: Modal
- Elemento: Modal 'Operação' (linha do plano e 'Decidir pendência'): Dose/quantidade, Gatilho por extenso, Janela
- Persona: agrônomo e RT
- Hoje: Dose/quantidade é um texto com 2 produtos e unidades ('Semente 52 kg/ha + KCl 60% 120 kg/ha'); gatilho e janela também em texto ('no dia do plantio · 1ª onda 22–28/09', '±10 d'). Ao criar ('Nova operação do plano') o gatilho é estruturado (DAP/Idade/DAF/DAC/Data + número).
- Proposta: Editar igual a criar: uma linha por insumo (produto da lista + dose numérica com unidade); gatilho por base + dias; janela ± dias em número; a data resultante é calculada e mostrada.
- Método: Teclado numérico com unidade
- Ganho: 3 textos livres → 1 número por insumo; publicar recalcula sem erro de digitação
- Evidência: v3out/PL-02.json results (Dose/quantidade text 'Semente 52 kg/ha + KCl 60% 120 kg/ha'; Gatilho por extenso text; Janela text '22–28/09'); v3/PL-02.dc.html SPEC s70 opts DAP/Idade/DAF/DAC/Data e drawer 'Nova operação do plano' com input number
- Cuidado: O.S. já emitida só muda pelo ajuste do agrônomo ao liberar.

### AGRO-14 · Alta · AG-01 · Lote
- Módulo: Agronomia
- Nível: Lote
- Elemento: Botão 'Programar vistoria' (Talhão, Alvo, Data, Responsável)
- Persona: monitor de pragas
- Hoje: Programa 1 talhão × 1 alvo por vez (4 campos). Aberto pelo topo, o talhão vem como o 1º da fazenda (Pivô 1), não o mais atrasado. O seletor tem 20 pivôs na Lagoa Grande e o painel mostra 2 vistorias atrasadas. Data sem atalho.
- Proposta: Selecionar linhas (ou chip 'Atrasadas' / 'Fora do ritmo') → 'Programar vistorias': uma vistoria por talhão × alvo do protocolo, data pelo ritmo (perto do NC = 3 dias), responsável da fazenda; prévia do que não entra (vistoria já aberta).
- Método: Lote por seleção
- Ganho: 10 talhões: 10 modais × 4 campos → 1 seleção + 1 clique
- Evidência: v3out/AG-01.json results 'Programar vistoria' (Talhão PV01, nOpt 20; Data sem chips); v3/AG-01.dc.html agPvOpen t0=tal||tals[0]; mipNovaVis recusa talhão × alvo já aberto; v3out/PAGR.inv2.json VIS-006 e VIS-060 'Vistoria atrasada'
- Cuidado: Não duplicar talhão × alvo aberto; nº de pontos pelo protocolo e pela área.

### OS-01 · Alta · OS · Necessidade essencial
- Módulo: Ordem de Serviço
- Nível: Detalhe
- Elemento: Seção "Insumos e doses" do painel da O.S. (Produto · Dose · Na ordem · Usado · Situação)
- Persona: agrônomo, almoxarife, programador e PCP
- Hoje: A seção mostra dose, total da ordem, usado e um texto de situação. Em A liberar esse texto é fixo do registro ("Reserva ao liberar"), não é calculado. O disponível no lote só aparece dentro do formulário Ajustar ou na frase do bloqueio. Não mostra reservado para outras O.S., quantidade a caminho (pedido e data), validade nem a falta em número. Para conferir, a pessoa sai para "Ver saldos no Estoque".
- Proposta: Trocar por um quadro "Insumos × estoque": uma linha por insumo com Necessário · Disponível na fazenda da O.S. · Reservado para esta O.S. · A caminho (data) · Falta. Selo em texto na linha: Coberto / Coberto com pedido em DD/MM / Falta N / Só em outra fazenda. Na linha em falta, o ⋯ traz primeiro a ação que resolve (Trocar produto, Pedir compra urgente, Pedir transferência).
- Método: Calculado
- Ganho: Decisão de aprovar e liberar sem trocar de tela: 2 telas (O.S. + Estoque) → 1 por O.S. com produto.
- Evidência: OS.dc.html:52 (cabeçalho "Produto Dose Na ordem Usado Situação"); OS.dc.html:5983 (pan_ins); OS.dc.html:5186 (osInsSit: em A liberar devolve o texto do registro); OS.dc.html:6079 (disponível só no Ajustar); OS.dc.html:2515 (cenDisp já calcula físico − quarentena − reservado)
- Cuidado: O servidor segue como autoridade de saldo e reserva: o quadro é prévia e a liberação confere de novo.

### OS-02 · Alta · OS · Resolver em 1 clique
- Módulo: Ordem de Serviço
- Nível: Detalhe
- Elemento: Bloqueio "Liberar bloqueado: saldo insuficiente…" e selo "Falta insumo · <produto>"
- Persona: agrônomo, comprador, almoxarife
- Hoje: O bloqueio diz "Quem resolve: Suprimentos, recebendo o insumo no Estoque" e oferece só o link "Ver saldos no Estoque ›". "Suprimentos" não é papel no catálogo (não existe comprador), então ninguém é chamado. Não há "pedir compra" na O.S., no Meu dia nem no app. O caminho de hoje é indireto: a O.S. entra na demanda, o Planejar safra mostra complemento e a Compra refaz 6 etapas, sem urgência.
- Proposta: Na linha em falta e no bloqueio, ação "Pedir compra urgente · N <un>": cria a solicitação com origem na O.S., quantidade = só a falta, precisa até = início da janela, urgência pela janela, e coloca na fila do comprador. O selo da O.S. passa a "Compra SC-x · chega DD/MM". Para defensivo, só com a versão aprovada pelo agrônomo (receituário).
- Método: Resolver em 1 clique
- Ganho: Nenhum caminho direto → 1 clique; dono real (comprador) no lugar de "Suprimentos".
- Evidência: OS.dc.html:5481 (osProx: q 'Suprimentos, recebendo o insumo no Estoque.', link EST); OS.dc.html:5145–5147 (selo e dono 'Suprimentos'); OS.dc.html:775 (G2_PAPEIS sem comprador); os-insumos-analise.md §4.3 e §6 (padrão manSolicitar da Manutenção, MA.dc.html:5254–5258)
- Cuidado: Não duplicar com a solicitação da safra: a compra urgente entra na demanda única como recebimento previsto. Alçada por valor. Clique repetido não gera segunda solicitação.

### OS-03 · Alta · OS · Resolver em 1 clique
- Módulo: Ordem de Serviço
- Nível: Detalhe
- Elemento: "Ajustar antes de liberar" › Tirar · "Incluir produto…" · dose
- Persona: agrônomo
- Hoje: Para trocar o produto em falta: Ajustar antes de liberar → Tirar → digitar o nome em "Incluir produto…" → Incluir → digitar a dose → Salvar e liberar (5 cliques e 2 digitações). A lista traz todo o catálogo da fazenda; registro para a cultura, dose de bula e máximo de aplicações só são conferidos ao salvar, depois de digitar. Rotação FRAC/IRAC não aparece na O.S.
- Proposta: "Trocar produto" no ⋯ da linha em falta abre a lista de produtos registrados para a cultura e o alvo da O.S., com selos (Com saldo N / Sem estoque / Rotação / Carência × colheita / Máx. aplicações), com saldo e outro modo de ação primeiro (padrão do AG-01). Escolher substitui o antigo na nova versão; a dose fica vazia com chips da faixa da bula; salvar leva à aprovação individual.
- Método: Lista ou busca com autocompletar
- Ganho: 5 → 3 cliques; 2 → 1 digitação (0 com o chip de dose); erro de registro aparece antes de digitar.
- Evidência: OS.dc.html:52 (formulário Ajustar: Tirar, "Incluir produto…", Incluir); OS.dc.html:6083 (pan_ajopts: catálogo inteiro, ordenado por saldo); OS.dc.html:6120 (osUsoItem só ao salvar); OS.dc.html:6061 e 6093 (produto incluído entra com dose em branco); os-insumos-analise.md §3 (AG-01.dc.html:5495–5507)
- Cuidado: Aprovação agronômica individual da nova versão; dose nunca pré-preenchida com o último valor; travas de registro, carência e dose de bula.

### OS-04 · Alta · IN-02 · Necessidade essencial
- Módulo: Início
- Nível: Listagem
- Elemento: Caixa única de decisões e painel da O.S. depois de "Confirmar aprovação"
- Persona: agrônomo
- Hoje: Aprovações tem 4 itens (ajuste de inventário, política do diesel, orçamento, acesso) e nenhuma O.S., embora haja 5 ordens A liberar com produto (OS-0418, OS-0430, OS-0431, OS-0501, OS-0502). O agrônomo vai à O.S., filtra A liberar e abre uma por uma. Depois de "Confirmar aprovação" o painel continua na mesma ordem: não abre a próxima.
- Proposta: Aprovações lista cada O.S. com produto que aguarda aprovação (prazo, talhão, produtos e o check de estoque e de regra na linha). Clicar abre a revisão no painel ao lado com "Aprovar v1" individual; aprovou, abre a próxima (UX-06). Ajustar fica no ⋯.
- Método: Outro
- Ganho: Entrada do agrônomo com a fila pronta (UX-05); 3 telas → 1; sem voltar à lista entre aprovações.
- Evidência: IN-02.dc.html:58 (GRIDS g_ap, 4 linhas sem O.S.); v3out/IN-02.json (inv.tables); OS.dc.html:6134 (pan_yes → osRun com {pa:null}: o painel fica na mesma O.S.); OS.dc.html:5021 (O.S. A liberar com insumos)
- Cuidado: Aprovação individual, uma O.S. por vez, sem "aprovar selecionados" e sem pré-autorização.

### OS-05 · Alta · CA-01 · Lote
- Módulo: Campo
- Nível: Lote
- Elemento: Barra de seleção "Liberar selecionadas" da tabela Ordens da janela de trabalho
- Persona: agrônomo, programador e PCP
- Hoje: Marcando ordens aparece "Liberar selecionadas", que libera em lote com resultado por item. O próprio resultado diz "Com produto, quem libera é o agrônomo (pode ajustar antes)": ordens com produto entram no lote.
- Proposta: O lote só libera ordens cuja versão já foi aprovada uma a uma pelo agrônomo, e as de só água pela prontidão. Ordem com produto sem aprovação sai no resultado como "aguarda aprovação de Ana", com link para aprovar individualmente.
- Método: Lote por seleção
- Ganho: Lote continua útil para o PCP sem contornar a aprovação individual.
- Evidência: CA-01.dc.html:57 (SPEC q6 "Liberar selecionadas" e mensagem); modelo da CA-01 (barra g_os_hassel com "Liberar selecionadas"); criterios.md (decisões fixas)
- Cuidado: Decisão fixa: aprovação agronômica individual de cada O.S., sem lote.

### OS-06 · Alta · MB-05 · Necessidade essencial
- Módulo: App de campo
- Nível: Tela
- Elemento: Aba "Almoxarife" do Almoxarifado móvel; primária "Retirar no almoxarifado" do OS-0424-app; link "Retirar no almoxarifado ›" do painel da O.S.
- Persona: almoxarife, operador, caldeiro
- Hoje: A aba Almoxarife mostra 3 blocos fixos (devolução da REQ-031, REQ-038 bloqueada, conflito do Fungicida A) e nenhuma lista de requisições liberadas para separar e entregar. A REQ-039 da OS-0424 (Fungicida A 65 L, 13 × galão 5 L, aplicação 24/09 06:00) não aparece para o Rui nem no Meu dia. No app, "Retirar no almoxarifado" só mostra o aviso "retire com Rui". O link do painel da O.S. abre o Estoque geral, sem a requisição.
- Proposta: Fila "A separar" do almoxarife (web e app), ordenada pelo início da janela: requisição, O.S., itens em embalagens, lote, validade e local (primeiro a vencer). Ações: Separar → Entregar a <operador>, com a confirmação no app dele (já existe). No app do operador, "Avisar que vou retirar" sobe a requisição na fila do Rui.
- Método: Resolver em 1 clique
- Ganho: Separação puxada pela janela; operador troca o "procure o Rui" por 1 toque; 0 buscas da requisição.
- Evidência: MB-05.dc.html:26 (modelo da aba Almoxarife, texto fixo) e :6483 (mensagens m0 e m1); IN-01.dc.html:58 (7 linhas, nenhuma de separação); OS-0424-app.dc.html:5026 (primária só mostra aviso); OS.dc.html:52 (link para EST.dc.html sem a REQ)
- Cuidado: A entrega baixa só a reserva da própria requisição; a custódia passa ao operador só com a confirmação dele.

### OS-07 · Alta · MB-03 · Entrada mais rápida
- Módulo: App de campo
- Nível: Tela
- Elemento: Fechar turno: "Hectares feitos neste turno", "Horas trabalhadas" e consumo por insumo
- Persona: operador, líder de campo
- Hoje: Hectares e horas vêm em branco; o consumo só aparece calculado depois de digitar os hectares. Fechar um turno igual ao plano pede 2 números digitados. A O.S. já tem o turno previsto (ex.: OS-0421 dia 5 · 50 ha) e o app guarda a hora de início e as pausas, mas não usa. Na web o mesmo apontamento já abre com a área do turno previsto: web e app agem diferente.
- Proposta: Botão "Executado como planejado": 1 toque preenche a área prevista do turno (limitada ao saldo) e as horas pelo relógio do turno menos as pausas; consumo = dose × área. O operador só muda o que foi diferente. Se GPS ou telemetria contradizem, o turno vai marcado para a conferência.
- Método: Pré-preenchido pelo contexto
- Ganho: 2 números digitados → 0; atende a meta P61 (2 toques, 0 digitação).
- Evidência: MB-03.dc.html:6296 (ft_ha e ft_h vazios) e :6298 (consumo só com ha > 0); MB-03.dc.html:2834 (turno guarda início e pausas); robot3/summ.txt (MB-03 · 5 campos: 5 digitados); OS.dc.html:6029 (web abre com a área do turno previsto); OS.dc.html:5021 (turnos previstos da OS-0421)
- Cuidado: Nunca preencher com o último valor apontado; o "como planejado" é toque explícito, nunca automático; respeitar saldo e o que está no aparelho aguardando sinal.

### OS-08 · Alta · CA-02 · Lote
- Módulo: Ordem de Serviço
- Nível: Lote
- Elemento: Primária "Conferir 2 apontamentos"
- Persona: conferente
- Hoje: A primária confere os 2 provisórios de uma vez, inclusive o dia 2 da OS-0420, que está fora da tolerância de horas (o cabeçalho diz "1 divergência"). O resultado só registra "horas acima do previsto"; a divergência sai da fila sem decisão.
- Proposta: Conferência por exceção: a primária vira "Conferir 1 dentro da tolerância"; o que diverge (horas × rendimento do conjunto, área × turno previsto, consumo × dose) fica na fila com Devolver para esclarecimento ou Registrar divergência (motivo obrigatório).
- Método: Lote por seleção
- Ganho: Lote para o normal; divergência nunca aprovada sem olhar.
- Evidência: v3out/CA-02.json (results "Conferir 2 apontamentos"); CA-02.dc.html:57 (SPEC q12, mensagens 2 e 5); cabeçalho "2 a conferir · 1 divergência"
- Cuidado: Conferir não muda a fase nem repete a baixa de consumo; a divergência fica rastreável.

### OS-09 · Alta · IN-01 · Resolver em 1 clique
- Módulo: Início
- Nível: Linha da tabela
- Elemento: Linha "OS-0418 · fertirrigação": Impedimento "Falta insumo · Ureia 45%", Próxima ação "Liberar" (o mesmo em CA-01 "Liberar ›" e CA-02 "Liberar OS-0418")
- Persona: agrônomo, comprador
- Hoje: A próxima ação é "Liberar", que leva à O.S. onde a liberação está bloqueada (sem lote de Ureia 45%, 0 kg apto). O impedimento aparece na linha, mas a ação oferecida não o resolve e ninguém de compras é avisado.
- Proposta: A próxima ação segue o impedimento: "Pedir compra · 1.140 kg Ureia 45%" (comprador) ou "Trocar produto" (agrônomo). "Liberar" só aparece quando nada impede.
- Método: Resolver em 1 clique
- Ganho: Clique que termina em bloqueio → 1 clique que leva o problema a quem resolve.
- Evidência: IN-01.dc.html:58 (linha OS-0418: imp "Falta insumo · Ureia 45%", acao "Liberar"); CA-01.dc.html:58 (OS-0418 "Ureia 45 % sem saldo apto" + "Liberar ›"); CA-02 (link "Liberar OS-0418"); OS.dc.html:5481
- Cuidado: Compra sempre ligada à O.S. e à versão aprovada.

### OS-10 · Alta · IN-01 / IN-02 · Resolver em 1 clique
- Módulo: Início
- Nível: Listagem
- Elemento: "Fila do dia" (Meu dia) e "Caixa única de decisões" (Aprovações)
- Persona: agrônomo, almoxarife, conferente, programador e PCP
- Hoje: Toda ação leva para outra tela (OS, EST, PL-05, CA-02, LO-02, CO-06det, SU-09, GE-02det…). Clicar na linha do Meu dia abre o formulário "Tarefa" (trocar responsável e prazo); na Aprovação abre uma consulta só de leitura com "Abrir a decisão no módulo de origem ›". Decidir pede 2 a 3 trocas de tela e a volta à fila.
- Proposta: Clicar no item abre ao lado o painel da decisão de origem (aprovar O.S., receber devolução, conferir dia, decidir ajuste) com a ação primária dele; feito, abre o próximo. Reatribuir e mudar prazo vão para o ⋯.
- Método: Outro
- Ganho: 2–3 trocas de tela → 0 por item; a fila esvazia em sequência.
- Evidência: IN-01.dc.html:58 (edit "Tarefa"; ações com destino em outras telas); IN-02.dc.html:58 (edit só leitura e "Abrir a decisão no módulo de origem"); v3out/IN-02.json (dialog Decisão)
- Cuidado: Cada decisão mantém a alçada e a trilha do módulo de origem; aprovação de O.S. individual.

### OS-11 · Alta · OS · Clareza
- Módulo: Ordem de Serviço
- Nível: Listagem
- Elemento: Tabela de O.S.: colunas que abrem por padrão
- Persona: programador e PCP, agrônomo, gestor
- Hoje: A tabela abre com 6 colunas (O.S., Atividade, Talhão, Prazo, Fase, Progresso). Situação, Quem resolve e Próxima ação existem, mas ficam escondidas em "Colunas +12"; o impedimento aparece só como ícone colorido junto do ID (com o texto curto do selo vermelho).
- Proposta: Mostrar por padrão uma coluna "Situação · próximo passo" em texto: "Falta insumo · Ureia 45% → Pedir compra (comprador)", "Aprovada v2 → Liberar (gestor)". Progresso pode sair do padrão (já está no Kanban e no painel).
- Método: Outro
- Ganho: Estado e próximo passo visíveis sem abrir a O.S. nem mexer em colunas.
- Evidência: OS.dc.html:58 (g_os: só id, ativ, tal, prazo, fase e prog têm ess); OS.dc.html (g2cvPadrao: padrão = colunas com ess); extract/OS.json (captura anterior: 6 cabeçalhos e "Colunas +12"); OS.dc.html:5938 (ícone de situação no ID)

### OS-12 · Alta · OS · Erro ou risco
- Módulo: Ordem de Serviço
- Nível: Detalhe
- Elemento: Liberar para execução: escolha do lote e reserva
- Persona: almoxarife, agrônomo
- Hoje: A liberação escolhe um único lote (o de maior disponível), sem olhar a fazenda da O.S. e sem dar prioridade ao que vence antes. Dois lotes que juntos cobrem a dose × área não liberam. A OS-0501 (Lagoa Grande) reservaria glifosato do Almox. defensivos da Santa Rita sem transferência nem aviso.
- Proposta: Reservar na fazenda da O.S., em mais de um lote se preciso, primeiro o que vence antes. Se só há saldo em outra fazenda, a linha do insumo mostra "Disponível em Santa Rita: N" e a ação "Pedir transferência" (tarefa do almoxarife).
- Método: Resolver em 1 clique
- Ganho: Sem reserva de outra fazenda às cegas; sem bloqueio falso quando a soma dos lotes cobre.
- Evidência: OS.dc.html:2514 (cenLote: maior disponível, sem fazenda); OS.dc.html:2670–2689 (cenLiberar: um lote, tudo ou nada); os-insumos-analise.md §2 (OS-0501 × lote G26-14)
- Cuidado: Servidor é a autoridade da reserva; transferência registrada como movimento rastreado.

### OS-13 · Alta · CA-01x-os0420 · Resolver em 1 clique
- Módulo: Ordem de Serviço
- Nível: Detalhe
- Elemento: Primária "Acompanhar OM-0233" e ⋯ "Reprogramar saldo"
- Persona: programador e PCP
- Hoje: A OS-0420 está Impedida (Trator T1 bloqueado, 70 ha parados) e a própria tela diz que o substituto Trator 02 está apto a partir de 24/09 06:00. A primária só leva à OM da manutenção; alocar o substituto exige ir ao PL-05 pelo ⋯. No painel da O.S., "Trocar" recurso só existe antes da execução.
- Proposta: Primária para o PCP: "Alocar Trator 02 a partir de 24/09 06:00" (confirma janela e operador, troca o recurso e tira o impedimento). "Acompanhar OM-0233" vai para o ⋯.
- Método: Resolver em 1 clique
- Ganho: 2 telas e reprogramação manual → 1 clique com confirmação.
- Evidência: v3out/CA-01x-os0420.inv2.json (primária "Acompanhar OM-0233"); v3out/CA-01x-os0420.json (menu "Reprogramar saldo"); v3out/CA-03det.json (Trator 02 · MF 7719: Apto, livre a partir de 24/09 06:00); OS.dc.html:5990 (rcPode: troca de recurso só em A liberar e Liberadas)
- Cuidado: Recurso bloqueado nunca elegível; conflito de máquina e operador conferido na troca.

### SUP-01 · Alta · CMP · Necessidade essencial
- Módulo: Compras
- Nível: Modal
- Elemento: Nova requisição (Materiais, peças e serviços) e fluxo Insumos da safra
- Persona: comprador, agrônomo, gerente de suprimentos
- Hoje: Não existe compra avulsa de insumo fora do plano agronômico. A requisição avulsa só aceita material, peça ou serviço e proíbe safra e cultura (nota da tela: "Sem safra nem cultura"). Insumo para um problema inesperado (ex.: surto de praga) só entra pela solicitação do Planejar safra e pelo assistente de 6 etapas. Nenhuma das duas compras pede motivo agronômico, vínculo à ocorrência (OC-, VIS-) ou mostra impacto no orçamento.
- Proposta: Em Compras › Nova requisição, tipo "Insumo fora do plano": item (busca), quantidade com unidade, talhão e cultura, ocorrência de origem (pré-preenchidos quando nasce da ocorrência, do MIP ou da O.S.), motivo em chips (praga ou doença acima do NC, replantio, perda, quebra, outro) e urgência. O sistema calcula e mostra o impacto no orçamento (R$, R$/ha e saldo da rubrica da safra) e envia para a alçada pelo valor. A demanda entra na necessidade da safra marcada "fora do plano".
- Método: Pré-preenchido pelo contexto
- Ganho: insumo urgente fora do plano: Planejar safra + 6 etapas (2 pessoas) → 1 formulário com 4 escolhas e 1 número; impacto no orçamento visto antes de aprovar
- Evidência: v3/CMP.dc.html: função cmmNova (comentário "requisição avulsa ... Nunca safra ou cultura"), v.cmn_nota "Sem safra nem cultura"; etapa 1 A.nota "a demanda é enviada no Planejar safra"; busca por "orçament" em CMP só acha textos do motor comum
- Cuidado: A compra não libera aplicação: receituário, registro do produto e aprovação agronômica individual da O.S. continuam obrigatórios. Alçada por valor e rastro ocorrência → compra → O.S.

### SUP-02 · Alta · SU-01 · Resolver em 1 clique
- Módulo: Compras
- Nível: Linha da tabela
- Elemento: Necessidade líquida por data · coluna Próxima ação (linhas atrasadas)
- Persona: comprador
- Hoje: Hoje é 23/09. Óleo mineral (falta 210 L), 2,4-D 806 (falta 310 L) e Glifosato 480 (falta 20 L) são necessários em 25/09, com o "pedir até" já vencido; KCl 60% falta 50 t para 24/09. A única ação é o link "Em cotação" (ou "Ver contrato"), que abre Compras na etapa 1, sem a safra. A melhor proposta de óleo mineral entrega em 5 a 7 dias: chega depois da necessidade e a tela não avisa nem oferece caminho urgente. O topo já diz "5 atrasados".
- Proposta: Na linha atrasada, estado em texto "Atrasado · chega depois de 25/09" e, no ⋯, primeiro item "Comprar urgente": abre a requisição com item, quantidade da falta firme, data necessária e origens (talhões, O.S.) preenchidos, sugere o fornecedor do contrato ou do último pedido que chega a tempo e mostra "chega dd/mm".
- Método: Resolver em 1 clique
- Ganho: falta urgente: 3 telas e redigitar item, quantidade, data e destino → 1 clique + confirmar; atraso visível na linha
- Evidência: v3/SU-01.dc.html GRIDS g_nec: linhas "Óleo mineral", "2,4-D 806", "Glifosato 480" (data 2026-09-25, acao "Em cotação" → CMP.dc.html sem safra), "KCl 60%" (2026-09-24); HOJE="2026-09-23"; v3out/SU-04.json results[2] (Óleo mineral: Santa Rita 7 d, Agro Norte 5 d); cabeçalho "18 itens com falta firme · 5 atrasados"
- Cuidado: Compra urgente respeita homologação do fornecedor e alçada; não duplica item que já está em pedido.

### SUP-03 · Alta · EST · Resolver em 1 clique
- Módulo: Estoque
- Nível: Linha da tabela
- Elemento: Entregas por O.S. · linhas "Sem lote no estoque" e "lote cobre só X dos Y"; falta de caixas no packing
- Persona: almoxarife, PCP, comprador
- Hoje: Quando o estoque não cobre a O.S., a linha mostra só o texto vermelho "Sem lote no estoque" ou "lote cobre só X dos Y", sem ação. Na SU-07, a REQ-040 (café C1) entrega 8.000 de 11.400 kg e diz "pendência 3.400 kg coberta pela SOL-2026-07", com link que abre Compras na etapa 1. No packing, quando não há sobra nem nota de caixa, o código diz que "a compra é do BEN-2" (ainda sem caminho).
- Proposta: Linha com falta: estado "Falta X · necessária dd/mm" e, no ⋯, primeiro item "Pedir ao Compras", que cria a requisição urgente com item, quantidade que falta, O.S. ou ordem de embalagem, talhão e data da operação. Se já houver pedido, a linha mostra "Coberta pelo PC-xxx · chega dd/mm" no lugar da ação. Mesmo item no packing para caixas.
- Método: Resolver em 1 clique
- Ganho: falta na entrega: 3 a 4 trocas de tela até o comprador → 1 clique com o contexto junto
- Evidência: v3/EST.dc.html bloco "etapa 2: entregas por O.S." (sit "Sem lote no estoque", sub "lote cobre só ...", sem ação); v3/SU-07.dc.html GRIDS g_req REQ-040 o "Pendência 3.400 kg coberta pela SOL-2026-07" → CMP.dc.html; v3/EST.dc.html comentário "sem nenhuma, a compra é do BEN-2"
- Cuidado: Não criar compra para o que já tem pedido; a reserva da O.S. segue decidida pelo servidor.

### SUP-04 · Alta · MA · Resolver em 1 clique
- Módulo: Manutenção
- Nível: Detalhe
- Elemento: Painel da OM · seção Peças (ordem corretiva e troca de peça)
- Persona: mecânico, PCM, almoxarife
- Hoje: A ordem corretiva nasce sem peças e o painel da OM não tem "Incluir peça" (só o editor de plano tem). Na troca de peça descoberta no diagnóstico não dá para ver o saldo, reservar ou pedir a compra pela ordem: o PCM vai a Compras › Nova requisição e preenche tipo, item, quantidade, destino, urgência e motivo (6 campos).
- Proposta: Na seção Peças da OM (A liberar, Liberada ou Em execução), "Incluir peça" com busca no catálogo e quantidade. A linha mostra na hora "Livre 2 un · reservar" ou "Falta 1 un". Com saldo: reserva para a OM e vai à fila de entrega do almoxarife. Sem saldo: "Pedir ao Compras" em 1 clique (OM, ativo, urgência pela criticidade e data da janela já preenchidos).
- Método: Resolver em 1 clique
- Ganho: troca de peça na corretiva: 6 campos e troca de módulo → 1 busca, 1 número e 1 clique
- Evidência: v3/MA.dc.html manAchCorretiva e manCorretivaAtivo (criam pecas:[]); "Incluir peça" só em pmSvV (editor de plano); v3/CMP.dc.html cmVals, painel "novo" (campos tipo, item, qtd, un, preço, destino, urgência, motivo)
- Cuidado: Peça reservada para a ordem que pediu (decisão fixa); saldo e reserva decididos no servidor.

### SUP-05 · Alta · EST · Entrada mais rápida
- Módulo: Estoque
- Nível: Modal
- Elemento: Recebimento · NF 4533 (Conferir NF) e Ler documento/QR da SU-06
- Persona: almoxarife
- Hoje: No Estoque, a tela do menu, não há leitura de NF-e: o formulário tem 11 campos e o almoxarife digita 5 (quantidade conferida, apta, em quarentena, validade do lote, motivo), mesmo com a nota esperada. "Apta + quarentena = conferida" é feita de cabeça. A leitura de chave/QR existe só na SU-06, fora do menu, e mesmo lá ainda pede conferida, validade e inspeção.
- Proposta: Ler o XML ou a chave da NF-e (ou QR/código de barras): pedido, itens, quantidades, lote e validade vêm da nota. Botão "Conferido como na nota" grava tudo; só a divergência é digitada (falta, avaria, quarentena). "Apta" calculada = conferida − quarentena. Alinha com UX-09.
- Método: Captura (XML de NF-e)
- Ganho: recebimento sem divergência: 5 → 0 campos digitados (meta P61); 1 número quando há quarentena
- Evidência: v3out/EST.json results[0] (11 campos: 5 digitados, 3 escolhidos, 3 pré); robot3/summ.txt linha "EST | Conferir NF 4533"; v3/SU-06.dc.html v.ler (simulado) e edit.fields conf/lote/val/insp; busca por XML, GTIN e "chave de acesso" em EST.dc.html sem resultado
- Cuidado: Aceite físico não aprova o título; nota já lançada não cria segunda entrada; quarentena fica fora do disponível.

### SUP-06 · Alta · MOD-SUP · Clareza
- Módulo: Suprimentos
- Nível: Menu
- Elemento: Menu Suprimentos × telas SU-01 a SU-09
- Persona: comprador, almoxarife, gerente de suprimentos
- Hoje: O menu tem só Painel, Compras, Estoque e Inteligência. Necessidades (SU-01), Políticas (SU-02), Contratos (SU-05) e Inventários (SU-09) só abrem por links internos (SU-01 só a partir de SU-02 e SU-04). Recebimento, saldos, requisições, movimentos e contagens existem em dobro (EST e SU-03/06/07/08/09), com formulários diferentes e números que não batem: o lote F26-02 está "Reserva em conflito" na SU-03 e "Sem conflito" na SU-03det. A SU-04 diz ao Proprietário "você não tem permissão para editar".
- Proposta: Uma listagem por entidade no menu: Necessidades (SU-01) como entrada do comprador; Compras (cotação, pedido, contrato); Estoque com Recebimentos, Saldos e lotes, Requisições e entregas, Movimentos e Inventários; Políticas em Configurações. Desativar as telas em dobro e redirecionar os links.
- Método: Outro
- Ganho: 1 lugar por tarefa; 5 pares de telas em dobro → 5 telas; fim dos números conflitantes
- Evidência: v3out/MOD-SUP.json inv.links ["Painel","Compras","Estoque","Inteligência"]; links: SU-01 só em SU-02.dc.html e SU-04.dc.html, SU-02 só em IN-02.dc.html; v3out/SU-03.json tabela, linha "Fungicida A · F26-02 Reserva em conflito" × v3out/SU-03det.inv2.json "Sem conflito · livre 480 L"; v3out/SU-04.json results[2] "você não tem permissão"
- Cuidado: Manter IDs e rastro (REQ, INV, MV, REC) ao juntar; não perder regras que hoje só existem numa das versões (contagem cega, custódia, quarentena).

### SUP-07 · Alta · SU-01, SU-03, SU-05, SU-06, SU-07, SU-08, SU-09, EST, CMP, MA · Ações no ⋯
- Módulo: Suprimentos e Manutenção
- Nível: Linha da tabela
- Elemento: Menu ⋯ da linha (padrão das tabelas)
- Persona: todas
- Hoje: A tabela padrão do sistema já tem o ⋯ na linha, mas ele só aparece quando a tabela permite excluir. Nenhuma tabela de Suprimentos e Manutenção permite excluir, então o ⋯ nunca aparece (robô: kebab=False em todas) e as ações viram botões e links soltos dentro das células de estado.
- Proposta: Mostrar o ⋯ sempre que a linha tiver ação, independente de excluir: sempre visível no fim da linha, próximo passo em primeiro, excluir ou cancelar por último e separado. A célula de estado fica só com texto ("Separada · falta entregar"); clicar na linha abre o detalhe; IDs seguem como link.
- Método: Menu ⋯
- Ganho: padrão único em cerca de 14 tabelas; 1 a 3 botões a menos por linha
- Evidência: v3/SU-07.dc.html motor da grade, linha ~675: "if(sp.rmenu&&sp.del&&(!semDel||acts.length))"; robot3/summ.txt AÇÕES NA LINHA (kebab=False em CMP, MA, SU-03, SU-05, SU-09)
- Cuidado: Ação perigosa continua com motivo e alçada no modal.

### SUP-08 · Alta · SU-07det, EST · Erro ou risco
- Módulo: Estoque
- Nível: Modal
- Elemento: Receber devolução (Quantidade medida / Quantidade conferida e Condição)
- Persona: almoxarife
- Hoje: Na SU-07det a "Quantidade medida" já vem com 10 sc (o saldo em custódia), embora o texto peça "a quantidade medida pelo almoxarife, não a declarada". No Estoque, "Quantidade conferida" vem com a custódia inteira e a condição padrão é "Apta · volta ao disponível"; na SU-07det o padrão é "Embalagem aberta · quarentena". Um Enter confirma sem medir.
- Proposta: Campo vazio com o esperado ao lado ("esperado 10 sc") e chip "Igual ao esperado" que exige toque. Condição sem padrão (escolha obrigatória) ou padrão seguro igual nas duas telas (quarentena).
- Método: Padrão seguro
- Ganho: nenhuma custódia baixada sem conferência; mesma regra nas duas telas
- Evidência: v3/SU-07det.dc.html PN.rec: q def "10", cond def "Embalagem aberta · quarentena no M26-05"; v3/EST.dc.html bloco "etapa 3: custódia e devoluções": qtd = it.custodia, cond = E2.conds[0]; GRIDS g_dev edit opts ["Apta · volta ao disponível", ...]
- Cuidado: Decisão fixa: quantidade real nunca vem pré-preenchida; quem tinha a custódia não confirma o próprio recebimento.

### SUP-09 · Alta · SU-09, EST · Lote
- Módulo: Estoque
- Nível: Lote
- Elemento: Planejar contagem, Nova contagem e aprovação de ajustes
- Persona: almoxarife, gerente de suprimentos
- Hoje: "Planejar contagem" aceita 1 escopo (1 lote) por vez; "Nova contagem" no Estoque lança 1 lote por formulário (item, quantidade, contador, causa). Ajustes são aprovados linha a linha. "Submeter ajuste" sem causa só mostra o aviso "clique na linha do INV e preencha antes". Nenhuma tabela tem seleção múltipla.
- Proposta: Selecionar lotes em Saldos (ou um local inteiro) → "Planejar contagem cíclica": uma contagem por lote, mesmo corte e contador. Contagem no app pela leitura do código do lote. Na lista de ajustes: selecionar os sem diferença → "Encerrar sem ajuste"; os com causa e evidência → "Aprovar selecionados", com resultado parcial explícito.
- Método: Lote por seleção
- Ganho: inventário de 20 lotes: 20 formulários → 1 seleção + 1 confirmação; aprovação de ajustes em 1 passo
- Evidência: v3/SU-09.dc.html PN.plan (Escopo: select único), PREVALS nx por linha, v.sub toast "Informe causa e evidência: clique na linha"; v3/EST.dc.html GRIDS g_cnt edit.fields; robot3/summ.txt LOTES (nenhum lote em SUP)
- Cuidado: Contagem cega mantida; quem contou não aprova o próprio ajuste (AL-09); ajuste acima da alçada sai do lote e vai individual; evidência por linha.

### SUP-10 · Alta · CMP · Necessidade essencial
- Módulo: Compras
- Nível: Tela
- Elemento: Insumos da safra · etapa 1 "Escolha a safra" e linha da safra
- Persona: comprador
- Hoje: Compras abre sempre na etapa 1 de 6 "Escolha a safra", com as outras travadas, embora a safra já esteja no topo (Santa Rita · Safra 2026/27). Os links da SU-01 ("Em cotação", "Abrir cotação da SOL-2026-07") caem nessa etapa 1: o contexto se perde. A linha da safra tem 2 botões ("Ver origem", "Abrir compra").
- Proposta: Abrir direto na solicitação aberta da safra do contexto, na etapa em que ela está (hoje: Solicitar cotações), com "Trocar safra" secundário. Links de outras telas levam safra, etapa e item.
- Método: Pré-preenchido pelo contexto
- Ganho: 2 cliques a menos a cada entrada; o link chega no item certo
- Evidência: v3out/CMP.json batch (etapas 2 a 6 "travada: Escolha a safra a fazer"); v3out/CMP.json inv.tables[0] ações ["Ver origem","Abrir compra"]; v3/SU-01.dc.html acao h "CMP.dc.html" sem safra
- Cuidado: Safra encerrada segue só consulta.

### SUP-11 · Alta · CMP · Necessidade essencial
- Módulo: Compras
- Nível: Detalhe
- Elemento: Etapa 5 · Alçada de aprovação
- Persona: aprovador por alçada, financeiro
- Hoje: Na etapa 5 aparecem o valor total e quem aprova. Não há comparação com o orçamento da safra (orçado, já comprometido, esta compra), custo por hectare nem desembolso por data. Quem não tem a alçada envia e depois "Registra a aprovação da Direção" em nome dela; não encontrei fila do aprovador em Suprimentos.
- Proposta: Bloco de decisão na aprovação: valor, R$/ha, orçado da rubrica, já comprometido, saldo depois desta compra (estado em texto), diferença para o menor custo equalizado e desembolsos por data. A compra entra na fila de aprovações do aprovador (UX-05 e UX-06, "aprovou, abre a próxima"), com Aprovar ou Devolver com motivo.
- Método: Calculado
- Ganho: decisão sem trocar de tela; o aprovador age na própria fila
- Evidência: v3/CMP.dc.html etapa 5: v.a5, v.c5_msg "Aprovar R$ ... e emitir N pedidos", A.prim "Registrar aprovação da "+m.quem; busca por "orçament" em CMP sem uso na compra
- Cuidado: Alçada conferida na hora de gravar; devolução e recusa com motivo; nada acima da alçada aprovado em lote.

### POS-01 · Alta · BEN · Resolver em 1 clique
- Módulo: Beneficiamento
- Nível: Detalhe
- Elemento: Painel da ordem › Impedimentos da liberação › falta de caixas
- Persona: gerente do packing, almoxarife, comprador
- Hoje: Quando faltam caixas, o impedimento traz só texto e um atalho. Se há nota a conferir, 'Conferir a NF 7731 das caixas no Estoque ›' abre o Estoque genérico, sem a nota (o Estoque só aceita âncora #dev=). Sem nota nem sobra, o texto diz 'a compra de caixas entra no BEN-2' e, em A liberar, a única saída é cancelar a ordem. Nenhum botão cria requisição ou compra; o gerente precisa achar o almoxarife ou o comprador fora do sistema.
- Proposta: No impedimento, ação 'Pedir N caixas' (N = falta calculada) que, em 1 clique, gera requisição ao almoxarifado quando há saldo livre em outro lote ou local, ou rascunho de solicitação de compra ao comprador com item, quantidade, data de necessidade (início da ordem) e ordem vinculada. O atalho da nota abre a conferência da NF 7731 já filtrada e avisa o almoxarife (Rui ou Paula).
- Método: Resolver em 1 clique
- Ganho: Texto + troca de tela + contato fora do sistema → 1 clique com ordem, item, quantidade e prazo; o pedido cai na fila de quem resolve
- Evidência: v3/BEN.dc.html l.4011-4027 (benCaixasRec: 'a compra de caixas entra no BEN-2', 'Sem caixa, Cancelar a ordem', link h='EST.dc.html' sem âncora para a nota); l.5462-5463 (linha do impedimento com dono e link); l.5564 ('Pedir mais caixas' só em Em execução ou Liberadas); v3/EST.dc.html trata só a âncora #dev=; v3out/BEN.json results[2] (botão 'Conferir a NF 7731 das caixas no Estoque ›')
- Cuidado: Automação gera rascunho e nunca compra sozinha (P34); caixas continuam reservadas só na liberação; servidor decide o saldo; pedido idempotente pela chave.

### POS-02 · Alta · BEN · Necessidade essencial
- Módulo: Beneficiamento
- Nível: Detalhe
- Elemento: Ordem de beneficiamento › conferência de materiais × estoque (criação e liberação)
- Persona: gerente do packing e da agroindústria
- Hoje: A ordem confere só caixas. A rota PACK-FRU tem um único material ('Caixa de mamão Formosa 10 kg'); a função de impedimentos testa só a lista de caixas da ordem. As rotas de secagem de milho (SEC-GRA) e de café (CAF-BEN) não têm material nenhum. Se a linha usa outros itens (pallet, etiqueta de rastreio, filme, sacaria, combustível do secador), a ordem libera sem checar.
- Proposta: Lista de materiais por rota e versão (item, consumo por kg ou por caixa, unidade). Na criação, quadro 'necessário × livre no estoque' de cada item; na liberação, cada falta vira impedimento com dono e a mesma ação 'Pedir' do POS-01.
- Método: Calculado
- Ganho: Falta de material descoberta antes do turno, não com a linha parada; um quadro único de materiais por ordem
- Evidência: v3/BEN.dc.html l.3825 (BENC: só PACK-FRU tem 'cx'; SEC-GRA e CAF-BEN sem materiais); l.4078-4089 (benImpedimentos: só o.ins, as caixas); l.5495 (seção 'Caixas · REQ' é a única de materiais)
- Cuidado: Criar continua sem reservar (BEN-D22); consumo sugerido e confirmado, nunca o último valor.

### POS-03 · Alta · CARGA · Entrada mais rápida
- Módulo: Colheita e pós-colheita
- Nível: Modal
- Elemento: Painel 'Pesar e receber' (Registrar pesagem / Pesar a CG-xxxx): Ticket da balança, Peso bruto, Tara, Umidade, Impureza
- Persona: balanceiro
- Hoje: Tudo é digitado: ticket (texto), bruto e tara em kg; em grão também umidade e impureza. Fruta: 3 campos digitados; grão: 5. A balança não é lida, embora o protótipo já mostre 'Origem da medição: balança integrada · hoje 09:22' num ticket da expedição (LO-02det).
- Proposta: Botão 'Ler balança' que captura ticket, peso e hora da balança integrada: bruto na entrada e tara na saída do mesmo veículo (pela placa), cada um no seu momento. Umidade e impureza lidas do medidor ou classificador quando houver. Digitar fica como exceção, marcada 'leitura manual' com motivo.
- Método: Captura (balança)
- Ganho: Fruta 3 → 0 campos digitados; grão 5 → 0 a 2; meta P61 (romaneio com 2 números) superada
- Evidência: v3/CARGA.dc.html l.5379-5397 (prFormPesar: 'Ticket da balança' t:'txt', 'Peso bruto', 'Tara', 'Umidade', 'Impureza' digitados; ajuda 'Bruto e tara em kg, sem valor anterior'); v3/LO-02det.dc.html GRIDS g_ps ('orig': 'balança integrada · hoje 09:22')
- Cuidado: Nunca usar peso ou tara de pesagem anterior (decisão fixa); ticket repetido não duplica produção (R-07); leitura manual fica na trilha.

### POS-04 · Alta · PROD · Lote
- Módulo: Estoque de produto (qualidade)
- Nível: Lote
- Elemento: Painel do lote › 'Registrar resultado' e 'Registrar decisão' da inspeção
- Persona: classificador (qualidade)
- Hoje: Uma inspeção cobre vários lotes da mesma ordem (ex.: classes A e B de uma ordem de packing), mas resultado e decisão são gravados lote a lote: abrir o lote, escolher Conforme ou Não conforme, gravar; depois escolher a decisão, gravar. Com 2 lotes são 4 formulários; com mais lotes do dia, cresce na mesma proporção.
- Proposta: Na inspeção, uma grade com todos os lotes dela: resultado por linha, botão 'Marcar todos conforme' e texto só no não conforme; depois 'Liberar os conformes' numa ação, com recibo por lote. Não conforme segue para decisão individual.
- Método: Lote por seleção
- Ganho: 2 lotes: 4 formulários → 1 grade e 2 toques; o ganho cresce com o número de lotes
- Evidência: v3/PROD.dc.html l.4461-4469 (benResultado grava I.res[lid] lote a lote; a inspeção tem I.lotes); l.5488 (formulário 'Registrar resultado' por lote); v3out/PROD.json (lotes L38-115 a L38-118 em processo na OB-0110)
- Cuidado: Registro, autor e recibo por lote (rastreabilidade); não conforme exige observação; quem decide é a Qualidade. Não é aprovação agronômica de O.S., então o lote é permitido.

### POS-05 · Alta · COLH, CARGA, BEN, PROD, EXPED, VEN, PCOM · Ações no ⋯
- Módulo: Pós-colheita e comercial (telas do menu)
- Nível: Linha da tabela
- Elemento: Linhas das tabelas g_tal, g_cg, g_ob, g_lot, g_rm, g_ven, g_of
- Persona: todos
- Hoje: A linha mostra estado e próximo passo em texto e abre o painel ao clicar (conforme o padrão). Mas não há ⋯: toda ação, mesmo a do próximo passo, exige abrir o painel e achar o botão. O robô não achou nenhuma ação nas linhas (acts vazio, kebab=false).
- Proposta: ⋯ sempre visível no fim da linha, próximo passo primeiro. COLH: Coletar contagem | Publicar previsão | Programar colheita Sxx, Abrir O.S. CARGA: Pesar a CG, Descartar (a pesar) | Abrir no estoque, Estornar (recebida). BEN: o passo do estado (Autorizar e liberar, Iniciar, Registrar saída, Enviar para conferência, Conferir balanço, Fechar), Pedir mais caixas, Reabrir execução, Cancelar a ordem. PROD: Registrar resultado ou decisão | Reservar para pedido | Abrir ordem de beneficiamento, Ver carga. EXPED: Confirmar saída | Confirmar entrega, Registrar devolução, Cancelar carga. VEN: Reservar lote | Aprovar crédito | Programar carga | Registrar a saca, Encerrar saldo. PCOM: Vender produto · período, Registrar a saca. Ação que pede dado abre o painel já no formulário.
- Método: Menu ⋯
- Ganho: Ação alcançável sem ler o painel; mesmo padrão em todas as listas; ações destrutivas sempre no fim do ⋯
- Evidência: v3out/BEN.json, PROD.json, COLH.json, EXPED.json, PCOM.json (inv.tables[].rows[].acts vazio, kebab=false); ações hoje só nos painéis: BEN l.5554-5566, CARGA l.5416-5443 (prPanCarga), EXPED l.5979-6005, VEN l.5990-6015
- Cuidado: Perfil sem o papel não vê a ação (mesma regra do painel); nada que pede quantidade é executado direto do ⋯.

### POS-06 · Alta · EXPED · Necessidade essencial
- Módulo: Expedição
- Nível: Detalhe
- Elemento: Painel da carga › 'Verificação da saída (ao vivo)' antes de 'Confirmar saída'
- Persona: expedição e logística, fiscal
- Hoje: A verificação checa lote, qualidade, carência e destino, reserva e crédito. Não checa nota fiscal, lacre nem conferência do carregamento. Isso só existe em LO-01 a LO-04 (fila de portaria, docas, checklist com lacre e NF, fretes), que não estão no menu: Comercial leva a Painel, Contratos e pedidos, Expedição e Inteligência.
- Proposta: Trazer para a carga do EXPED os itens do checklist da LO-02det (NF autorizada, lacre com foto, conferência do lote por leitura) dentro da 'Verificação da saída', cada um com dono e ação no item ('Pedir NF ao fiscal', 'Registrar lacre'). Doca e frete viram seções da mesma carga, não telas soltas.
- Método: Outro
- Ganho: Saída só com documento e lacre; a expedição faz tudo da carga num lugar, pelo menu
- Evidência: v3/EXPED.dc.html l.5516-5534 (comImpede sem NF nem lacre); nenhuma ocorrência de 'lacre' ou NF de saída em EXPED e VEN; v3/LO-02det.dc.html GRIDS g_ck (produto, veículo, lacre, NF, financeiro); v3/MOD-COM.dc.html (links PCOM, VEN, EXPED, IV)
- Cuidado: Saída registrada uma única vez (CMD-26); NF e lacre não marcados sem evidência; quem aplica o lacre não confere.

### POS-07 · Alta · VE-04, VE-06, VE-05, LO-01, LO-03 (via GE-05, GE-08, GE-04) · Erro ou risco
- Módulo: Pós-colheita e comercial (telas legadas)
- Nível: Tela
- Elemento: Links de ID nos módulos financeiros que abrem as telas legadas
- Persona: financeiro, comercial
- Hoje: Há duas versões do pós-colheita e do comercial. O menu leva às telas vivas (COLH, CARGA, BEN, PROD, EXPED, VEN, PCOM). CO-01..07, LO-01..04 e VE-01..06 estão fora do menu, mas o Financeiro chega nelas: GE-05 tem 9 links para VE-04 e 8 para VE-06; GE-08 aponta VE-05; GE-04 aponta LO-01. Os números não batem: VE-04 mostra 'Recebíveis em aberto R$ 244 mil · PV-029'; o PCOM mostra a receber R$ 91.470,00 (RM-0001, PV-037). A VE-04 ainda mistura a carteira antiga (PV-026 a PV-034) com a tabela viva de reservas.
- Proposta: Uma só verdade: links de pedido, carga, lote e caso apontam para VEN#PV, EXPED#RM e PROD#lote. As telas legadas saem do caminho (sem link de entrada). O que só existe nelas (portaria, lacre, frete, casos de reclamação) migra para as telas vivas (ver POS-06).
- Método: Outro
- Ganho: Financeiro e comercial veem o mesmo saldo em qualquer tela; zero conciliação manual entre telas
- Evidência: v3/MOD-COM.dc.html e MOD-AGR.dc.html (sem links CO, LO, VE); v3/GE-05.dc.html ('h': 'VE-04.dc.html' ×9, 'VE-06.dc.html' ×8); v3/GE-08.dc.html (VE-05 ×2); v3/GE-04.dc.html (LO-01 ×2); v3/VE-04.dc.html (KPI 'R$ 244 mil · PV-029'; tabelas g_cart e g_rsv); v3out/PCOM.json inv.tables[1].rows[0] (R$ 91.470,00)
- Cuidado: Não perder a trilha dos registros antigos (casos RC-12 a RC-15, viagens VG-112 e VG-117).

### POS-08 · Alta · PT-05det, PT-03, PT-04det, CO-02, CO-06 · Erro ou risco
- Módulo: Portal do parceiro e colheita (legado)
- Nível: Campo
- Elemento: Listas das gavetas: 'Tipo' (Documento da carga 3), 'Motivo' (Pedir ajuste da oferta), 'Condição' (Condição precedente), 'Origem da demanda' e 'Máquinas' (Preparar ordens), 'Lote' e 'Padrão / método' (Nova inspeção)
- Persona: fornecedor, comprador, banco, encarregado de colheita, classificador
- Hoje: As listas vêm de cadastros de outro contexto. Documento de carga oferece 'Preventiva, Preditiva, Corretiva, Melhoria'; ajuste de oferta oferece 'Sonda deslocada, Praga acima do NC, Máquina diferente do padrão'; condição de crédito mistura 'acima de, abaixo de, FOB · à vista'; ordem de colheita oferece 'Almoxarifado · lote F26-02, Estoque de peças da oficina' e máquinas como pulverizador e plantadeira; inspeção pós-colheita oferece o lote de fungicida F26-02 e métodos de MIP e de solo (pano-de-batida, SMP, Al trocável).
- Proposta: Cada lista vem do cadastro do próprio contexto: tipos de documento da carga (NF-e, laudo, CT-e); motivos comerciais (preço, volume, janela, frete); condições de crédito; origem da demanda = previsão e pedido; máquinas de colheita e transporte; só lotes de produção e padrões de qualidade do produto.
- Método: Lista ou busca
- Ganho: Zero registro com opção sem sentido; lista curta e certa
- Evidência: v3/PT-05det.dc.html gaveta d65 (select 'Tipo'); v3/PT-03.dc.html d58 (select 'Motivo'); v3/PT-04det.dc.html d61 (select 'Condição'); v3/CO-02.dc.html d21 ('Origem da demanda', 'Máquinas'); v3/CO-06.dc.html d27 ('Lote', 'Padrão / método')
- Cuidado: Tipo de documento e método da inspeção entram na trilha; corrigir a lista não pode apagar registros antigos.

### GES-01 · Alta · GE-01 · Necessidade essencial
- Módulo: Gestão e finanças
- Nível: Menu
- Elemento: Entrada da Visão gerencial (GE-01) e das telas Contas a pagar (GE-04), Contas a receber (GE-05), Indicadores (GE-06) e Planos de ação (GE-07)
- Persona: proprietário e gestor, controller e financeiro
- Hoje: Nenhuma tela do protótipo tem link para a GE-01. A barra lateral (Mapa, Cadastros, Agrícola, Manutenção, Suprimentos, Comercial, Crédito, Configurações, Outros acessos) não tem Gestão. O hub Agrícola só leva a Orçamento (GE-02) e Custos (GE-03). GE-04 e GE-05 só abrem por links de outras telas (SU-06, VE-04 etc.). GE-06 só abre a partir da GE-07 e da GE-06det. A trilha mostra 'Gestão e resultados › Visão gerencial', um grupo que não está no menu.
- Proposta: Sem criar o 10º nome na barra: colocar Visão gerencial, Contas a pagar, Contas a receber, Indicadores e Planos de ação num hub que já existe (ex.: o hub Crédito, que hoje só repete 4 visões da GE-08) e pôr um atalho 'Resultado da safra ›' no painel do Mapa do gestor. A trilha deve usar o mesmo nome do hub.
- Método: Outro
- Ganho: Proprietário chega ao resultado, ao caixa e aos desvios em 1 clique. Hoje não chega por nenhum caminho.
- Evidência: grep de 'GE-01.dc.html' em v3/*.dc.html: nenhum link para a tela. Links de MOD-AGR: GE-02 e GE-03. GE-06 recebe links só de GE-07 e GE-06det. Menu lateral em v3/GE-01.dc.html antes do <main>.
- Cuidado: Decisão fixa: a barra continua com 9 nomes. Não criar menu por perfil (P65).

### GES-02 · Alta · GE-07 · Resolver em 1 clique
- Módulo: Gestão e finanças
- Nível: Modal
- Elemento: Links 'Criar ação' / 'Criar ação do desvio' / 'Abrir plano de ação' (GE-01, GE-02det, GE-06, GE-06det) → formulário 'Criar ação' da GE-07
- Persona: proprietário e gestor, controller
- Hoje: Os 4 links abrem a lista da GE-07 sem o desvio de origem. O usuário clica em 'Criar ação' e preenche 7 campos: Título, Hipótese, Ação definida e Evidência esperada são digitados; a Origem já vem como 'Custo de pulverização · feijão P1', mesmo quando veio de outro desvio; o Dono vem como 'Ana'; o Prazo fica em branco. No GE-01, 'Plantio parado por ativo bloqueado · OM-0233' oferece 'Criar ação', mas a AC-103 (OM-0233, Aguardando peça) já existe. Isso gera um caso duplicado.
- Proposta: Abrir o formulário já com o contexto: origem, título e efeito vêm do desvio; a hipótese vem da causa apontada; o dono vem do responsável pelo indicador. Se já existe caso aberto para a mesma origem, a linha mostra 'AC-103 · aguardando peça' e o ⋯ oferece 'Abrir AC-103' em vez de 'Criar ação'.
- Método: Pré-preenchido pelo contexto
- Ganho: 2 cliques e 7 campos (4 digitados) → 1 clique e 2 campos (ação e prazo). Sem caso duplicado.
- Evidência: v3/GE-07.dc.html GRIDS g_ac.edit.fields (orig def 'Custo de pulverização · feijão P1', dono def 'Ana'). A EXTRAVALS da GE-07 não lê o endereço. Links sem parâmetro em GE-01, GE-02det, GE-06 e GE-06det ('GE-07.dc.html'). AC-103 com origem OM-0233 em g_ac.rows.
- Cuidado: O estado do caso só muda por Verificar e Encerrar. Manter a rastreabilidade do vínculo com o desvio.

### GES-03 · Alta · GE-04 · Ações no ⋯
- Módulo: Gestão e finanças
- Nível: Linha da tabela
- Elemento: Botões e links de ação dentro das linhas: GE-04 'Títulos a pagar', GE-07 'Casos de melhoria', GE-08 'Solicitações' e 'Dossiê', GE-01 'Causas prioritárias', GE-06 'Painéis por processo'
- Persona: financeiro, controller, gestor de crédito, gestor
- Hoje: Nenhuma linha dessas tabelas tem ⋯. Os botões ficam soltos na célula: GE-04 tem 'Propor pagamento' e 'Importar retorno', além dos links 'Abrir aprovação', 'Abrir pedido', 'Ver retiradas' e 'Abrir crédito'. GE-07 tem 'Propor mudança', 'Verificar resultado', 'Encerrar com evidência' (os dois últimos lado a lado na AC-097), 'Reabrir com motivo' e 'Ver OM-0233'. GE-08 tem 'Autorizar bloco' e a coluna 'Ação' com '—', 'Ver título' e 'Ver CPR'. GE-01 tem a coluna 'Próxima ação'; GE-06, a coluna 'Ação'. O motor de tabelas já leva os botões da linha para o ⋯, mas só a SAF usa isso.
- Proposta: Ligar o ⋯ em todas essas tabelas. Ordem do ⋯: GE-04: [próximo passo do estado: Propor pagamento | Importar retorno | Abrir aprovação] → Programar pagamento → Abrir NF/pedido de origem. GE-07: Verificar resultado → Encerrar com evidência → Editar caso → Reabrir com motivo (só no encerrado). GE-08 Solicitações: Anexar documento condicionante (CRE-0102) → Comparar propostas → Ver título/CPR. GE-08 Dossiê: Autorizar bloco → Ajustar acesso. GE-01 e GE-06: clicar na linha abre o detalhe, e o ⋯ traz 'Criar ação' / 'Abrir AC-xxx'. O estado e o próximo passo ficam em texto na linha. IDs (PC-084, OM-0233, CRE-0098) continuam como links.
- Método: Menu ⋯
- Ganho: Linha limpa e padrão único em 6 tabelas. O próximo passo é sempre o 1º item do ⋯.
- Evidência: Motor em v3/GE-04.dc.html: 'if(sp.rmenu){ ... os botões da linha vão para o ⋯' (15/10, proprietário). 'rmenu: true' só aparece em v3/SAF.dc.html. summ.txt linhas 27–33. Os GRIDS g_tit, g_ac, g_cre, g_dos, g_cau e g_ind têm células 'act' ou 'cta'.
- Cuidado: Ações que dependem de alçada continuam aparecendo com o motivo quando estão impedidas.

### GES-04 · Alta · GE-03 · Resolver em 1 clique
- Módulo: Gestão e finanças
- Nível: Tela
- Elemento: Primária 'Fechar competência 09/2026' e faixa '2 pendências bloqueiam o fechamento'
- Persona: controller e financeiro
- Hoje: A primária verde fica ativa com 2 pendências; o clique só mostra o aviso 'Bloqueado · 2 pendência(s)'. Para tratar o frete (R$ 1.463, 'Sem versão de rateio'), é preciso achar a linha na tabela de 10 lançamentos, abri-la, escolher entre 7 opções de rateio e salvar. O diesel se resolve com o botão 'Conciliar diesel do tanque', que fica na seção de baixo. As pendências não levam a lugar nenhum.
- Proposta: Fazer a primária seguir a próxima pendência: 'Ratear frete (R$ 1.463)' abre o lançamento já com 'por tonelada transportada' sugerido; depois vem 'Conciliar diesel do tanque'; só então 'Fechar competência'. Cada pendência da faixa vira um link que abre a linha certa.
- Método: Resolver em 1 clique
- Ganho: Cerca de 4 cliques e uma busca na tabela → 1 clique por pendência a partir do topo. Nenhum clique cai em botão que só recusa.
- Evidência: v3/GE-03.dc.html EXTRAVALS: v.fechar retorna 'Bloqueado · ...' quando há pendências; pend = frete sem rateio e diesel sem conciliação. GRIDS g_lan, linha 'frete' com rat 'Sem versão de rateio'. O robô não abriu a tela (v3out/GE-03.json landed 'blank').
- Cuidado: O fechamento continua exigindo as pendências tratadas. Correção de lançamento definitivo só por estorno e relançamento.

### GES-05 · Alta · CD-08 · Entrada mais rápida
- Módulo: Cadastros
- Nível: Modal
- Elemento: Formulário 'Cadastrar rendimento': Conjunto ou equipe, Largura, Máquina R$/h, Implemento R$/h, Custo por pessoa
- Persona: quem implanta, gestor, PCP
- Hoje: 'Conjunto ou equipe' é texto livre, mas os conjuntos já existem na CD-03 (ex.: Trator 02 + Pulverizador PJ-3030). Largura (36 m), Máquina (R$ 180/h) e Implemento (R$ 95/h) são digitados, e são os mesmos valores do cadastro da CD-03. O Custo por pessoa (R$ 38/h) é o custo-hora da CD-04. No modo 'Largura × velocidade' são 8 campos digitados. A aba Conjuntos da CD-03 também tem uma coluna Rendimento (21,6 ha/h), o que dá duas fontes para o mesmo número.
- Proposta: Trocar o texto livre por uma busca nos conjuntos da CD-03, com 'Criar conjunto' no próprio campo. Ao escolher, vêm preenchidos (com a origem indicada) a largura do implemento, os R$/h da máquina e do implemento e o custo médio dos operadores habilitados. A pessoa digita só velocidade, eficiência e nº de pessoas. O rendimento fica numa fonte só: a CD-03 mostra o da CD-08.
- Método: Lista ou busca com autocompletar
- Ganho: 8 → 3 campos digitados. Fim do rendimento divergente entre CD-03 e CD-08.
- Evidência: v3/CD-08.dc.html GRIDS g_rend.edit.fields (conj 't':'txt'; larg, maq, impl, pess_rs 'num'). Linha r1: maq 180, impl 95, larg 36. v3/CD-03.dc.html g_atv: Trator 02 custo_h 180, PJ-3030 custo_h 95 e barra 36. g_cj tem rend 21.6.
- Cuidado: O valor editado no rendimento continua valendo só para o padrão e mostra a origem. Não alterar o custo do cadastro da máquina sem querer.

### GES-06 · Alta · CD-01 · Entrada mais rápida
- Módulo: Cadastros
- Nível: Listagem
- Elemento: Cadastro de talhões ('Incluir talhão' dentro da fazenda)
- Persona: quem implanta (cadastro inicial)
- Hoje: Na CD-01 os talhões entram um por um ('Incluir talhão', formulário com 6 ou mais campos). Não há importar KML/shapefile/planilha nem colar lista. Só existem importações fora daqui: no onboarding (ON-01det, 12 talhões por shapefile), no Mapa (IN-04, só na Lagoa Grande) e por talhão na CD-01det ('Importar arquivo' de um polígono). A Lagoa Grande tem 23 talhões.
- Proposta: Na CD-01, ação 'Importar talhões (KML, shapefile ou planilha)' com a mesma prévia do ON-01det (mapeamento, sistema de coordenadas, sobreposição, duplicidade com mesclar ou ignorar) e resultado parcial explícito. Também 'Colar lista' (nome; área cultivável; sistema) numa grade editável.
- Método: Grade editável ou colar de planilha
- Ganho: 23 formulários → 1 importação com prévia, mais a correção só das linhas com erro.
- Evidência: Contagem em v3/CD-01.dc.html: 0 'Importar', 0 'colar', GRIDS g_tal 'sel': false. A importação existe em v3/ON-01det.dc.html (g_imp) e em v3/IN-04.dc.html (tm_ok só na Lagoa Grande, conforme mapa-analise.md l.166).
- Cuidado: A área do polígono só muda com nova versão (CD-01det). Sobreposição exige justificativa. Respeitar o limite de área da assinatura (assinTrava).

### GES-07 · Alta · GE-04 · Modal e botões
- Módulo: Gestão e finanças
- Nível: Tela
- Elemento: Primária 'Enviar remessa ao banco'
- Persona: financeiro
- Hoje: Com 1 clique a remessa é enviada sem prévia. Só depois um aviso diz o que entrou (Fertisul PC-088, R$ 233.000, 17/10) e o que ficou fora (NF 8790, que aguarda alçada). Não dá para conferir os títulos, a conta e o total antes de mandar ao banco.
- Proposta: Ao clicar, abrir um resumo: títulos incluídos (qtde, total, conta de saída, datas) e títulos fora, com o motivo. O botão diz 'Enviar remessa · 1 título · R$ 233.000'. Depois do envio, a linha mostra 'Aguardando banco'.
- Método: Outro
- Ganho: Consequência visível antes do ato financeiro. 1 → 2 cliques só nesta ação de risco.
- Evidência: v3out/GE-04.json results[0] (effect, aviso 'Remessa REM-2609-02 enviada...'). v3/GE-04.dc.html EXTRAVALS v.remessa.
- Cuidado: Manter o envio idempotente (o mesmo recibo no 2º clique). Nada aparece pago antes do retorno do banco.

### GES-08 · Alta · CD-04 · Erro ou risco
- Módulo: Cadastros
- Nível: Campo
- Elemento: Habilidades de decisão no cadastro de pessoa ('Liberar O.S. (agrônomo)', 'Aprovar O.S. de manutenção', 'Liberar ativo', 'Autorizar rota e liberar ordem de processo', 'Liberar lote (qualidade)') × papéis e alçadas da CF-01
- Persona: administrador do sistema
- Hoje: Quem decide é marcado em dois lugares: nas caixas de habilidade da CD-04 (15 opções, 5 delas são decisões) e nos papéis e alçadas da CF-01 (AL-01 Liberar O.S. agrícola, AL-02 Aprovar a versão da O.S., etc.). Nada impede que os dois fiquem diferentes, por exemplo com a habilidade marcada e sem o papel.
- Proposta: A CD-04 fica só com as habilidades de execução e as habilitações legais (NR, CREA). O direito de decidir fica só na CF-01. No cadastro da pessoa, mostrar em leitura 'Decide: AL-02, AL-05 · via Usuários e alçadas ›'.
- Método: Outro
- Ganho: Uma fonte só para quem decide e auditoria sem contradição.
- Evidência: v3/CD-04.dc.html GRIDS g_pes.edit.fields 'hab' opts. v3/CF-01.dc.html CONF0.pessoas[].hab e G2_ALCADAS. v3out/CD-04.json results[0] (22 campos).
- Cuidado: Manter a trava legal: o papel de agrônomo só com CREA válido (a CF-01 já lê o CREA da CD-04). Aprovação agronômica continua individual por O.S.

### GES-09 · Alta · ON-01det · Erro ou risco
- Módulo: Implantação
- Nível: Modal
- Elemento: Correção do objeto 'Estoque inicial (planilha)': 'Unidade da coluna qtde' e 'Mapeamento de colunas'
- Persona: quem implanta (cadastro inicial)
- Hoje: As 48 linhas de estoque recebem uma unidade única para toda a coluna (sc 50 kg, kg, t, L ou un). Defensivo em L e fertilizante em kg na mesma planilha ficam com a mesma unidade. O mapeamento de colunas é um texto livre ('item, depósito, qtde').
- Proposta: Ler a unidade do cadastro de cada item (Produtos e locais) pelo código ou nome. Perguntar a unidade só nas linhas sem item cadastrado, com 'aplicar às semelhantes'. O mapeamento vira uma lista por coluna, com sugestão automática.
- Método: Calculado
- Ganho: 1 escolha arriscada para 48 linhas → 0 a poucas escolhas, sem estoque inicial com unidade trocada.
- Evidência: v3/ON-01det.dc.html GRIDS g_imp.edit.fields: un sel ['A definir','sc 50 kg','kg','t','L','un'] e map 't':'txt'. v3out/ON-01det.json inv.tables[0] (48 linhas, 'coluna qtde sem unidade').
- Cuidado: Nada é gravado sem validar. O resultado parcial continua explícito. O servidor é a autoridade do saldo.

### GES-10 · Alta · GE-02 · Entrada mais rápida
- Módulo: Gestão e finanças
- Nível: Modal
- Elemento: Formulário 'Criar cenário'
- Persona: controller, proprietário
- Hoje: 5 campos digitados do zero: Nome, Premissa alterada (texto), Volume soja, Preço médio soja e Custo total. O volume é conta de área × rendimento: o C1 'rendimento −8%' tem 47.180 sc = 51.280 × 0,92. Mesmo assim, a pessoa escreve a premissa em texto e faz a conta à mão.
- Proposta: 'Criar cenário a partir da V2': nome sugerido (C2), premissas como campos com chips (rendimento −5/−8/−10 %, preço ±, custo de irrigação +%) e volume, receita e custo calculados na hora, mostrando a diferença para a V2.
- Método: Modelo ou duplicar
- Ganho: 5 → 1 ou 2 campos digitados e nenhuma conta manual.
- Evidência: v3out/GE-02.json results[0] (5 campos digitados). summ.txt l.161. v3/GE-02.dc.html g_ver linhas V2 (vol 51280, prem 'rendimento 63 sc/ha') e C1 (vol 47180, prem 'rendimento −8%').
- Cuidado: V1 e V2 continuam intocadas. O cenário nasce em rascunho.

### GES-11 · Alta · GE-04 · Resolver em 1 clique
- Módulo: Gestão e finanças
- Nível: Linha da tabela
- Elemento: Agro Norte NF 8790 · R$ 96.000 · vence hoje · 'Proposto · aguarda alçada' · link 'Abrir aprovação'
- Persona: financeiro, proprietário
- Hoje: O título que vence hoje fica parado na alçada. A linha não diz quem aprova. 'Abrir aprovação' leva à caixa geral de Aprovações (IN-02), sem abrir o item. A remessa do dia sai sem ele ('NF 8790 não entrou').
- Proposta: Mostrar na linha 'aguarda: <aprovador> · desde <hora>'. No ⋯: 'Lembrar aprovador' (com a NF e o vencimento) e, para quem tem a alçada, 'Aprovar pagamento', que abre o item certo nas Aprovações.
- Método: Resolver em 1 clique
- Ganho: Caixa geral + busca → 1 clique até o item. Menos risco de multa por atraso.
- Evidência: v3/GE-04.dc.html g_tit linha Agro Norte (conc 'Proposto · aguarda alçada'; cta 'Abrir aprovação' h 'IN-02.dc.html' sem item). Aviso da remessa em v3out/GE-04.json results[0].
- Cuidado: Aprovar continua sendo da alçada (CF-01). Lembrar não aprova.

### AGRO-15 · Média · PAGR · Resolver em 1 clique
- Módulo: Painéis por perfil
- Nível: Cartão
- Elemento: Cartão 'MIP · onde agir' (VIS-013 acima do NC; VIS-006 e VIS-060 atrasadas)
- Persona: gerente agrícola
- Hoje: Todo item leva a 'Conferir vistoria VIS-xxx' (AG-01#VIS-xxx), que só abre o painel; depois é preciso clicar 'Decidir controle' ou 'Programar vistoria'. O AG-01 já aceita #VIS-xxx:decidir e #VIS-xxx:programar, que abrem o formulário direto.
- Proposta: Usar o verbo do próximo passo: 'Decidir controle VIS-013' (#VIS-013:decidir) e 'Programar vistoria VIS-006' (#VIS-006:programar).
- Método: Resolver em 1 clique
- Ganho: 2 → 1 clique; o verbo certo já no painel
- Evidência: v3/PAGR.dc.html linha 5910 origem:'AG-01.dc.html#'+v.id e linha ~6136 abrir:'Conferir vistoria '+x.vis; v3/AG-01.dc.html agHash aceita '(decidir|programar)'
- Cuidado: Abrir o formulário não registra decisão.

### AGRO-16 · Média · PL-01 · Resolver em 1 clique
- Módulo: Planejamento
- Nível: Tela
- Elemento: Primária 'Autorizar execução 2026/27'
- Persona: gerente agrícola
- Hoje: Botão verde ativo; ao clicar responde 'Não autorizado: o orçamento revisado da Safra 2026/27 aguarda a Direção… Como resolver: cobrar a aprovação em Aprovações'. A pessoa troca de tela e procura o item.
- Proposta: Enquanto o orçamento estiver pendente, a primária vira 'Cobrar aprovação do orçamento (Direção)', que abre o item na fila da Direção com a safra junto; 'Autorizar execução' aparece desligado com a causa.
- Método: Resolver em 1 clique
- Ganho: clique sem efeito + troca de tela → 1 clique
- Evidência: v3out/PL-01.json results 'Autorizar execução 2026/27' status 'Não autorizado: o orçamento revisado…'
- Cuidado: A data de início nunca supre a aprovação; alçada da Direção.

### AGRO-17 · Média · PL-05 · Resolver em 1 clique
- Módulo: Planejamento
- Nível: Linha da tabela
- Elemento: Linha 'Falta de insumo PC-088 · KCl 60% 40 t a entregar em 02/10'
- Persona: planejador (PCP)
- Hoje: A coluna Alternativa já diz 'atender a NEC-028 com as 50 t aptas · 10 t em quarentena', mas a única ação é 'Ver pedido' (Compras). Aplicar a alternativa exige ir ao Estoque e à NEC-028.
- Proposta: No ⋯: 'Aplicar alternativa: atender NEC-028 com o lote apto K26-11' (proposta de reserva que o Estoque confirma) em primeiro; depois 'Cobrar entrega do PC-088 (Rui · Suprimentos)' e 'Ver pedido'.
- Método: Resolver em 1 clique
- Ganho: 3 telas → 1 clique; dono e prazo juntos
- Evidência: v3/PL-05.dc.html GRIDS g_imp i2 alt 'atender a NEC-028 com as 50 t aptas 10 t em quarentena', ab 'Ver pedido' → CMP.dc.html; CEN0 'KCl 60%|K26-11' físico 60.000 kg, quarentena 10.000 kg
- Cuidado: Reserva firme só na liberação; servidor é autoridade de saldo; lote em quarentena não entra.

### AGRO-18 · Média · AG-07 · Resolver em 1 clique
- Módulo: Agronomia
- Nível: Detalhe
- Elemento: Ficha do produto · seções 'Rotação' e 'Usar na O.S.'
- Persona: agrônomo e RT
- Hoje: A ficha lista produtos de outro modo de ação para a mesma cultura × alvo (até 4 nomes por grupo), sem estoque nem carência. 'Usar na O.S.' exige escolher cultura, alvo, produto da fazenda e ordem (4 escolhas) e parte da consulta, não da O.S. que está sem produto. O robô só viu o cabeçalho ('Base de 02/10/2026 · desatualizada'); a lista não carregou na captura.
- Proposta: Abrir o AG-07 a partir da O.S. ou da decisão já filtrado (cultura, alvo, ordem); na Rotação mostrar 'na fazenda: x L com saldo' e carência × colheita prevista, com saldo primeiro; 'Usar na O.S.' em 1 clique.
- Método: Pré-preenchido pelo contexto
- Ganho: 4 escolhas → 1 clique; troca com estoque e rotação na mesma vista
- Evidência: v3/AG-07.dc.html agFichaVals: af_rotG ps só com nome; af_usar exige cul, al, pf e ord; AG_FAZ ['Com saldo disponível','Sem saldo disponível','Fora da fazenda'] só na lista; v3out/AG-07.inv2.json
- Cuidado: A consulta não emite receituário; ao liberar, a O.S. confere registro, dose e nº de aplicações.

### AGRO-19 · Média · PL-02 · Erro ou risco
- Módulo: Planejamento
- Nível: Modal
- Elemento: Painel 'Nova operação do plano' (Talhão, Atividade, Insumo, Dose, Janela, Data)
- Persona: agrônomo e RT
- Hoje: Inclui defensivo no plano (ex.: Glifosato 480) sem informar o alvo; sem alvo não há como conferir o registro para cultura × alvo, e a conferência fica para a liberação da O.S., depois da compra planejada. Atividade e dose em texto ('2,0 L/ha').
- Proposta: Ao escolher um defensivo, pedir o alvo (lista do protocolo da cultura) e mostrar o selo 'Registrado' / 'Sem registro' e a faixa de dose da bula; dose numérica com unidade; atividade por lista.
- Método: Lista ou busca com autocompletar
- Ganho: uso sem registro visto no plano, antes da compra
- Evidência: v3/PL-02.dc.html drawer 'Nova operação do plano' labels Talhão/parcela, Atividade, Insumo, Dose, Janela, Data; input Dose type text value '2,0 L/ha'; v3/AG-07.dc.html af_dica '…ao liberar, a O.S. confere registro, dose e nº de aplicações'
- Cuidado: A trava final continua na liberação.

### AGRO-20 · Média · AG-01 · Ações no ⋯
- Módulo: Agronomia
- Nível: Linha da tabela
- Elemento: Tabela de vistorias (Vistoria · Alvo · Contagem × NC · Talhão · Próximo passo)
- Persona: monitor de pragas
- Hoje: Cada linha tem um botão no Próximo passo ('Confirmar foco', 'Seguir monitorando', 'Decidir controle', 'Programar vistoria'), sem ⋯. As colunas Situação e Data ficam ocultas: a linha mostra o próximo passo, mas não o estado ('Foco', 'Acima do NC') nem há quantos dias foi a coleta.
- Proposta: Clique na linha abre o painel; Situação e Data visíveis por padrão; próximo passo em texto; ⋯ no fim: [próximo passo], Programar vistoria, Ver rota e evidências, Abrir talhão no mapa, Abrir O.S. de controle (se houver).
- Método: Menu ⋯
- Ganho: estado visível sem abrir; ações no mesmo lugar em todas as linhas
- Evidência: v3out/AG-01.json inv.tables[0].heads (5 colunas, sem Situação e Data), rows acts ['Confirmar foco'] kebab false; dumps/AG-01.txt g_vis cols sit e data com ess null
- Cuidado: Sem decisão em lote: a decisão MIP é por vistoria.

### AGRO-21 · Média · AG-03 · Ações no ⋯
- Módulo: Agronomia
- Nível: Linha da tabela
- Elemento: Tabelas de Diagnósticos (AG-03) e de Recomendações (AG-04)
- Persona: agrônomo e RT
- Hoje: As linhas misturam links de ID (DIA-007, VIS-011, REC-014) com a ação ('Abrir REC-014', 'Abrir vistoria', 'Decidir controle', 'Abrir OS-0421', 'Liberar OS-0418') na mesma coluna; sem ⋯.
- Proposta: IDs seguem como links; próximo passo em texto; ⋯ — Diagnóstico: [Decidir controle | Abrir recomendação], Abrir vistoria, Abrir laudo, Avaliar eficácia. Recomendação: [Abrir O.S. para liberar | Decidir controle | Criar nova versão], Ver receituário, Gerar prescrição, Avaliar eficácia.
- Método: Menu ⋯
- Ganho: mesmo padrão nas duas listas do RT
- Evidência: v3out/AG-03.json rows acts ['DIA-007','VIS-011','Abrir REC-014'], ['VIS-013','Decidir controle']; v3out/AG-04.json rows acts ['REC-014','DIA-007','Abrir REC-014'], links 'Liberar OS-0418'
- Cuidado: Liberar segue individual, dentro da O.S.

### AGRO-22 · Média · PL-04 · Ações no ⋯
- Módulo: Planejamento
- Nível: Linha da tabela
- Elemento: Tabelas Ordens do período, Pendências e Manutenções (PL-04) e Impedimentos (PL-05)
- Persona: planejador (PCP)
- Hoje: Coluna 'Abrir'/'Ação' com um link por linha ('Abrir O.S.', 'Resolver impedimento', 'Abrir na Irrigação', 'Receber devolução', 'Ver conflito', 'Propor substituição', 'Ver pedido'); clicar na linha abre consulta ou o 'Programar'. A tabela 'Manutenções e impacto na produção' é igual no PL-03 e no PL-04.
- Proposta: Linha abre o detalhe da O.S. ou do impedimento; ⋯ com o próximo passo primeiro — Ordem: [Resolver impedimento | Pedir liberação], Programar janela e conjunto, Reprogramar saldo, Abrir O.S.; Impedimento: [Propor substituição | Aplicar alternativa], Cobrar responsável, Reprogramar saldo, Ver origem. Tabela de manutenções só no PL-04.
- Método: Menu ⋯
- Ganho: padrão único; 1 tabela repetida a menos
- Evidência: robot3/summ.txt AÇÕES NA LINHA (PL-03, PL-04, PL-05); v3/PL-04.dc.html GRIDS g_mi4 com as mesmas 3 linhas da 3ª tabela do PL-03

### AGRO-23 · Média · IR-01 · Ações no ⋯
- Módulo: Irrigação
- Nível: Linha da tabela
- Elemento: Tabelas Setores (IR-01), Programação (IR-02) e Ordens de irrigação (IR-03)
- Persona: técnico de irrigação
- Hoje: IR-02: clicar na linha OS-0601 não abre nada; o próximo passo 'Iniciar irrigação' é só texto. IR-01: 'Iniciar irrigação' e 'Abrir OS-0507' como link na coluna. IR-03: a linha abre a ordem, sem ⋯.
- Proposta: Linha abre o IR-03det; ⋯ com o próximo passo primeiro: [Iniciar irrigação | Definir janela | Abrir O.M. da bomba], Registrar avanço, Pausar/retomar, Ver setor no mapa.
- Método: Menu ⋯
- Ganho: mesmo padrão nas 3 listas; nenhuma linha morta
- Evidência: v3out/IR-02.json results OS-0601 kind 'none'; v3out/IR-01.json rows acts ['Abrir OS-0507'], ['Iniciar irrigação']; v3out/IR-03.json rows acts []

### AGRO-24 · Média · IR-01 · Modal e botões
- Módulo: Irrigação
- Nível: Modal
- Elemento: Modal 'Setor · Pivô 5' (Déficit, Necessidade, Ordem que cobre, limites do setor)
- Persona: técnico de irrigação
- Hoje: O modal mostra déficit de 13,2 mm e 'Responsável pelo próximo passo: Manutenção', mas a primária é 'Salvar' de 3 limites técnicos editáveis (lâmina máxima 8 mm, intervalo 18 h, eficiência 85 %). 'Abrir OS-0507' e 'Programar irrigação' ficam secundários.
- Proposta: Primária = próximo passo do setor ('Abrir OS-0507' com a Manutenção, ou 'Programar irrigação'); limites só leitura, com '⋯ Editar limites do pivô' na ficha do pivô, com alçada.
- Método: Outro
- Ganho: próximo passo em 1 clique; parâmetro técnico protegido de edição acidental
- Evidência: v3out/IR-01.json results 'Setor · Pivô 5' btns ['Abrir OS-0507','Programar irrigação',…,'Salvar'(primária)]; campos Lâmina máxima, Intervalo mínimo e Eficiência editáveis
- Cuidado: Os limites valem para a próxima programação; ordens liberadas não mudam.

### AGRO-25 · Média · IR-01 · Resolver em 1 clique
- Módulo: Irrigação
- Nível: Campo
- Elemento: Campo 'Água disponível no solo (referência)' = 'sem medição de água no solo neste talhão'
- Persona: técnico de irrigação
- Hoje: O modal avisa que falta a medição, sem ação. Para resolver: Agrícola › Análises de solo › '+ Registrar medição' e escolher fazenda e talhão de novo (a fazenda vem Santa Rita mesmo para um pivô da Lagoa Grande).
- Proposta: Link 'Pedir medição de água no solo' que abre o AG-02 com fazenda e talhão do setor preenchidos, ou cria a tarefa para o agrônomo responsável.
- Método: Pré-preenchido pelo contexto
- Ganho: 4 cliques + 2 escolhas → 1 clique
- Evidência: v3out/IR-01.json campo 'Água disponível no solo (referência)' v 'sem medição de água no solo neste talhão'; v3out/AG-02.json '+ Registrar medição' Fazenda v 'Santa Rita', Talhão vazio
- Cuidado: CAD não é lâmina; a lâmina segue a política de água e o RT.

### AGRO-26 · Média · AG-01 · Modal e botões
- Módulo: Agronomia
- Nível: Modal
- Elemento: Modal 'VIS-055 · Mancha-anelar': opção 'Erradicar plantas' e botão 'Gerar O.S. de erradicação'
- Persona: agrônomo e RT
- Hoje: Dois botões verdes cheios: a opção escolhida ('Erradicar plantas') usa o mesmo verde da primária ('Gerar O.S. de erradicação'). Parece haver duas ações principais.
- Proposta: Opções como seleção (contorno com ✓ ou rádio); só 'Gerar O.S. de erradicação' em verde cheio.
- Método: Outro
- Ganho: 1 primária por contexto
- Evidência: robot3/summ.txt PRIMÁRIAS MÚLTIPLAS 'AG-01 | modal: VIS-055 · Mancha-anelar (PRSV) · Pivô 22 | ['Erradicar plantas', 'Gerar O.S. de erradicação']'; v3/AG-01.dc.html agDec dc_kinds selecionado background:#1E7A4C;color:#fff (mesmo de dc_okst)

### AGRO-27 · Média · PL-04 · Entrada mais rápida
- Módulo: Planejamento
- Nível: Modal
- Elemento: Modal 'Programar' (Janela, Recurso/conjunto, Operador, Duração)
- Persona: planejador (PCP)
- Hoje: Janela ('24–26/09') e Duração ('3 turnos') em texto. Recurso/conjunto lista 8 opções misturadas (pulverizadores, plantadeira, pivôs, oficina) para uma O.S. de fungicida, inclusive o Trator T1 bloqueado; operador sem habilitação indicada.
- Proposta: Janela por data de início e fim com atalhos; duração calculada pelo saldo (ha) ÷ rendimento do conjunto (biblioteca de rendimentos, UX-07); conjuntos filtrados pela operação, com disponibilidade e conflito na própria opção; operadores habilitados primeiro.
- Método: Calculado
- Ganho: 2 textos → 0; conflito visto antes de salvar
- Evidência: v3out/PL-04.json results 'Programar · OS-0421' (Janela text '24–26/09', Duração text '3 turnos', Recurso/conjunto nOpt 8); v3/PL-04.dc.html g_ord edit opts
- Cuidado: Programar não libera; conflito de máquina e operador (P44).

### AGRO-28 · Média · AG-03 · Necessidade essencial
- Módulo: Agronomia
- Nível: Tela
- Elemento: Topo das telas AG-03, AG-04, AG-05, AG-06, PL-05, IR-01, IR-03 e IR-04
- Persona: agrônomo e RT
- Hoje: Oito telas sem ação primária no topo, embora haja pendência: DIA-009 'A decidir'; REC-014 com '1 uso sem registro'; Feijão pivô v3 'em validação'; EF-021 com leitura pós que vence 27/09; impedimento que 'vence hoje'; '1 sem dado' em sensores.
- Proposta: Aplicar a TELA-01 com a pendência mais urgente: AG-03 'Decidir controle DIA-009'; AG-04 'Resolver uso sem registro REC-014'; AG-05 'Validar Feijão pivô v3'; AG-06 'Registrar leitura pós EF-021'; PL-05 'Decidir impedimento OS-0431'; IR-01 'Programar setores acima do limite'; IR-03 'Abrir ordem de hoje OS-0601'; IR-04 'Verificar sonda do Pivô 10'.
- Método: Outro
- Ganho: tarefa do dia em 1 clique ao entrar
- Evidência: v3out/<tela>.json inv.primary = [] em AG-03, AG-04, AG-05, AG-06, PL-05, IR-01, IR-03, IR-04; v3out/AG-04.inv2.json '1 uso sem registro (REC-014)'; v3out/AG-06.json status '1 pós vence em 27/09'; v3out/IR-04.inv2.json '1 sem dado'
- Cuidado: UX-02 já decidido; uma primária só.

### AGRO-29 · Média · AG-05 · Modal e botões
- Módulo: Agronomia
- Nível: Tela
- Elemento: Botões 'Publicar' (AG-05), 'Encerrar período' (PL-01) e 'Registrar parecer' (AG-06)
- Persona: agrônomo e RT
- Hoje: 'Publicar' responde 'Nada a publicar ainda'; 'Encerrar período' responde 'Nenhum período apto a encerrar agora'; 'Registrar parecer' grava na hora um parecer pronto ('redução observada não atribuída ao produto…') sem abrir campo nem confirmar.
- Proposta: Mostrar o botão só quando houver o que fazer (ou desligado com a causa); 'Registrar parecer' abre o formulário da avaliação pendente (método, confiança, parecer) e grava com o nome do RT.
- Método: Outro
- Ganho: zero cliques sem efeito; parecer escrito por quem assina
- Evidência: v3out/AG-05.json 'Publicar' status 'Nada a publicar ainda…'; v3out/PL-01.json 'Encerrar período' status 'Nenhum período apto…'; v3out/AG-06.json 'Registrar parecer' status 'Parecer registrado: …'
- Cuidado: Parecer técnico é do RT; rastreabilidade.

### AGRO-30 · Média · AG-03 · Entrada mais rápida
- Módulo: Agronomia
- Nível: Modal
- Elemento: Modal '+ Criar diagnóstico' (Talhão · cultura, Evidências, Hipótese, Meta, Risco, Ação proposta, Responsável)
- Persona: agrônomo e RT
- Hoje: 7 campos, 4 digitados. 'Evidências' pede para digitar IDs ('Ex.: VIS-017 · LAU-2063') que o sistema conhece; o talhão vem 'T2 · Soja', sem relação com o contexto.
- Proposta: Evidências por seleção das vistorias e laudos do talhão (últimos 60 dias), já marcadas quando o diagnóstico nasce de uma vistoria ou laudo; talhão do contexto; hipótese com sugestões dos alvos do protocolo.
- Método: Lista ou busca com autocompletar
- Ganho: 4 → 2 campos digitados; IDs sem erro
- Evidência: v3out/AG-03.json results '+ Criar diagnóstico' (Evidências text, Hipótese textarea, Meta text, Ação proposta textarea; Talhão v 'T2 · Soja')

### AGRO-31 · Média · AG-05 · Entrada mais rápida
- Módulo: Agronomia
- Nível: Modal
- Elemento: Modal '+ Criar versão' da biblioteca técnica
- Persona: agrônomo e RT
- Hoje: Formulário em branco com 4 textos livres (Escopo, Referência, Unidade · gatilhos, Validade · revisão) e Aprovador técnico '—'. Uma nova versão quase sempre parte da anterior.
- Proposta: 'Nova versão' no ⋯ da linha: copia a versão atual e mostra as diferenças ao salvar; escopo por listas (cultura, região, fase), validade em data, aprovador = RT do cadastro.
- Método: Modelo ou duplicar
- Ganho: 4 textos → só o que muda
- Evidência: v3out/AG-05.json results '+ Criar versão' (Escopo, Referência, Unidade · gatilhos, Validade · revisão text; Aprovador v '—')
- Cuidado: Publicar não reescreve planos em execução; aprovação técnica.

### AGRO-32 · Média · IR-04 · Resolver em 1 clique
- Módulo: Irrigação
- Nível: Linha da tabela
- Elemento: Linha 'Sonda de umidade · Pivô 10' (atualização 21/09 06:00) e faixa '1 sem dado'
- Persona: técnico de irrigação
- Hoje: A tela avisa '1 sem dado' e o balanço do Pivô 10 passa a estimativa por ET (≈); a linha não abre nada e não há ação para quem resolve.
- Proposta: No ⋯ da linha: 'Pedir manutenção da sonda' (O.M. com sensor, setor e última leitura) e 'Registrar leitura manual'.
- Método: Resolver em 1 clique
- Ganho: falha de sensor chega à manutenção em 1 clique
- Evidência: v3out/IR-04.json inv.tables[0] row 'Sonda de umidade · Pivô 10 … 21/09 06:00 … por estimativa de ET (≈)', results kind 'notfound'; v3out/IR-04.inv2.json 'Clima e sensores 1 sem dado'

### OS-14 · Média · OS · Ações no ⋯
- Módulo: Ordem de Serviço
- Nível: Linha da tabela
- Elemento: Linhas da tabela de O.S. e cartões do Kanban
- Persona: programador e PCP, agrônomo, gestor
- Hoje: Linha e cartão só abrem o painel; não há ⋯ nem seleção. Toda ação exige abrir o painel e achar o botão.
- Proposta: ⋯ sempre visível no fim da linha e do cartão, próximo passo primeiro, por fase. A liberar: Revisar e aprovar (abre o painel) → Ajustar antes de liberar → Cancelar sem execução. Liberadas: Iniciar execução → Trocar recurso → Cancelar sem execução. Em execução: Registrar apontamento → Pausar → Dispensar saldo. Em conferência: Conferir e encerrar. Clique na linha segue abrindo o detalhe; o ID segue como link.
- Método: Menu ⋯
- Ganho: Ação frequente a 2 cliques da lista, sem abrir o painel.
- Evidência: OS.dc.html:58 (g_os "edit":{"m":"pick"}, "sel":false); OS.dc.html:5938 (células sem ação)
- Cuidado: "Revisar e aprovar" pelo ⋯ abre a revisão da O.S.; nunca aprova direto da lista.

### OS-15 · Média · OS · Modal e botões
- Módulo: Ordem de Serviço
- Nível: Detalhe
- Elemento: Região "Próximo passo" do painel da O.S.
- Persona: agrônomo, gestor
- Hoje: Ficam lado a lado até 3 botões: Liberar para execução (primária), Ajustar antes de liberar e Cancelar sem execução; em execução, Registrar apontamento e Dispensar saldo.
- Proposta: Uma primária pelo estado; Ajustar, Trocar recurso, Dispensar saldo e Cancelar sem execução no ⋯ do cabeçalho do painel, com o que cancela por último.
- Método: Menu ⋯
- Ganho: 3 → 1 botão visível; menos risco de cancelar por engano.
- Evidência: OS.dc.html:52 (pan_hasBtn, pan_hasAj, pan_hasDisp e pan_hasCanc na mesma região); OS.dc.html:6154–6156 (canCanc, canDisp)
- Cuidado: Cancelar e dispensar continuam com motivo e alçada.

### OS-16 · Média · OS · Entrada mais rápida
- Módulo: Ordem de Serviço
- Nível: Detalhe
- Elemento: Conferência diária na seção "Apontamentos diários" do painel
- Persona: conferente
- Hoje: Para cada dia: Conferir dia → escolher "Conferir dia" ou "Registrar divergência" → Registrar conferência (3 cliques por dia, por O.S.). O texto de comparação diz "Não há meta diária registrada", embora a O.S. tenha turnos previstos (ex.: dia 5 · 50 ha) e rendimento do conjunto em ha/h.
- Proposta: Comparar cada dia com o turno previsto, horas × rendimento e consumo × dose, com faixa de tolerância. Dentro da faixa: o dia vem marcado "confere" e é confirmado em lote na fila do conferente (CA-02); fora: abre o caso com motivo.
- Método: Calculado
- Ganho: 3 cliques por dia → 1 clique para todos os dias normais.
- Evidência: OS.dc.html:6477–6518 (cdLinha; cdComparacao "Não há meta diária registrada", linha 6512); OS.dc.html:5021 (turnos previstos); OS.dc.html:5977 (rendimento do conjunto)
- Cuidado: Conferir não repete a baixa; divergência exige motivo.

### OS-17 · Média · CA-01 / CA-01det · Clareza
- Módulo: Campo
- Nível: Tela
- Elemento: Duas listagens e dois detalhes da mesma O.S. (Ordens de campo × Ordem de Serviço)
- Persona: programador e PCP, líder de campo, gestor
- Hoje: A O.S. tem duas listagens com colunas e regras diferentes: OS (com painel) e CA-01 (clique na linha abre o formulário "Ordem" de janela e equipe). Há também dois detalhes: o painel e "Abrir ordem completa", que só existe para 2 de 21 O.S. (OS-0420 e OS-0421). Na CA-01det a primária "Registrar avanço" leva ao MB-03, tela do celular. A CA-02 mostra o caminho "Agrícola › Ordem de Serviço", mas é outra tela.
- Proposta: Uma listagem de O.S. com visões (Tabela, Kanban, Calendário, Carga, Mapa) e um detalhe só; clique na linha sempre abre o detalhe; mudar janela e equipe vira "Reprogramar" no ⋯; na web, apontar pelo formulário do painel.
- Método: Outro
- Ganho: 2 listas + 2 detalhes → 1 + 1; mesmas palavras e ações em todas as O.S.
- Evidência: CA-01.dc.html:58 (edit form "Ordem"); OS.dc.html:5021 (link só em OS-0420 e OS-0421); v3out/CA-01det.inv2.json (primária "Registrar avanço" → MB-03.dc.html); caminho da CA-02 "Agrícola › Ordem de Serviço"

### OS-18 · Média · CA-01 · Ações no ⋯
- Módulo: Campo
- Nível: Linha da tabela
- Elemento: Tabela "Ordens da janela de trabalho"
- Persona: programador e PCP
- Hoje: As ações são links soltos na coluna "Condição · próxima ação" (Liberar ›, Definir janela ›, Resolver conflito ›, Abrir em Irrigação ›, Ver OM-0233 ›, Conferir dia 4 ›, Ver custódia ›); 5 das 12 linhas não têm ação; clicar na linha abre edição.
- Proposta: Linha abre o detalhe; condição e próximo passo em texto; ⋯ no fim: [próximo passo do estado] → Reprogramar janela e equipe → Abrir em Irrigação ou na OM → Ver custódia. IDs seguem como links.
- Método: Menu ⋯
- Ganho: Um lugar só para as ações; padrão igual ao da O.S.
- Evidência: CA-01.dc.html:58 (links por linha em p.cond); v3out/CA-01.json (rows acts)

### OS-19 · Média · CA-02 · Ações no ⋯
- Módulo: Ordem de Serviço
- Nível: Linha da tabela
- Elemento: "Fila de conferência diária" e seções soltas abaixo
- Persona: conferente
- Hoje: Na linha: botão "Conferir" e links "Ver histórico ›" / "Ver custódia ›". Fora da linha: "Devolver para esclarecimento" no cabeçalho da fila, sem dizer qual apontamento (age no dia 2 da OS-0420), e "Reabrir saldo da OS-0417" e "Encerrar OS-0417" em seções próprias. Abaixo, a tabela "Roteiro da OS-0418 após a liberação" (8 passos) não é tarefa de conferência.
- Proposta: ⋯ por linha: Conferir → Devolver para esclarecimento → Corrigir com motivo → Reabrir saldo → Encerrar O.S. (quando for o último dia). Tirar o roteiro da OS-0418 desta tela (fica no detalhe dela).
- Método: Menu ⋯
- Ganho: Cada ação ligada à linha certa; tela só com a fila.
- Evidência: Modelo da CA-02 (botão "Devolver para esclarecimento" no cabeçalho; seções "Reabrir saldo" e "Encerramento"; grade g_proj); CA-02.dc.html:57 (q12, mensagem 3 fixa na OS-0420); v3out/CA-02.inv2.json
- Cuidado: Devolver não apaga o fato.

### OS-20 · Média · CA-04 · Entrada mais rápida
- Módulo: Campo
- Nível: Modal
- Elemento: Gaveta "Solicitar material da ordem"
- Persona: líder de campo
- Hoje: Pede Ordem, Item, Quantidade e Necessário em. A lista de itens é fixa e mistura insumo, diesel, bico, óleo hidráulico e "Soja · CEPEA" (que é cotação de preço). O texto da gaveta diz que "itens e doses vêm da versão vigente", mas o formulário pede tudo.
- Proposta: Escolher a O.S. (chips das liberadas da equipe); a requisição nasce com os itens e as quantidades da versão (dose × saldo) e necessário em = início da janela. Item fora da O.S. só com motivo; tirar "Soja · CEPEA".
- Método: Pré-preenchido pelo contexto
- Ganho: 4 campos → 1 escolha.
- Evidência: CA-04.dc.html:52 (gaveta d17: "itens e doses vêm da versão vigente" seguido de Ordem, Item com a lista fixa, Quantidade, Necessário em)
- Cuidado: Quantidade da versão aprovada; excesso exige revisão.

### OS-21 · Média · CA-04 · Ações no ⋯
- Módulo: Campo
- Nível: Linha da tabela
- Elemento: Tabela "Requisições e custódia da equipe", coluna Próxima ação
- Persona: líder de campo, almoxarife
- Hoje: A REQ-038 mostra "Confirmar recebimento" com 0 kg entregue; o clique só diz "Indisponível: nada foi entregue". A REQ-035 ("faltam 15 L") e a REQ-036 ("faltam 3.640 kg") não têm ação. "Apontar uso ›" leva à conferência (CA-02), não ao apontamento.
- Proposta: Próximo passo em texto pelo estado ("Aguarda liberação · Ana"; "Faltam 15 L · Rui entrega"); ⋯: Pedir entrega do restante → Devolver sobra → Ver O.S. → Ver em Suprimentos. Ação indisponível não aparece.
- Método: Menu ⋯
- Ganho: Nenhum clique sem efeito; toda falta com ação.
- Evidência: CA-04.dc.html:57 (q16, mensagem 1); CA-04.dc.html:58 (linhas e "o" com "faltam"); v3out/CA-04.json

### OS-22 · Média · CA-01det · Resolver em 1 clique
- Módulo: Campo
- Nível: Linha da tabela
- Elemento: "Materiais em custódia da equipe" · Fungicida A (A entregar 15 L)
- Persona: líder de campo, almoxarife
- Hoje: O saldo de 160 ha × 0,50 L/ha pede 80 L; com o Marcos há 65 L e a linha mostra "A entregar 15 L". Não há ação na linha; "Requisitar material" leva ao SU-07. O último turno pode parar por falta.
- Proposta: No ⋯ da linha: "Pedir entrega dos 15 L ao Rui · até o próximo turno", que entra na fila de separação do almoxarife com a O.S. junto.
- Método: Resolver em 1 clique
- Ganho: Troca de tela → 1 clique; falta resolvida antes do turno.
- Evidência: v3out/CA-01det.json (linha Fungicida A: 175 / 160 / 95 / 65 / 15 L; dialog Custódia); CA-01det.dc.html:58 (g_mat "o": "faltam 15 L")
- Cuidado: Entrega só do que já está reservado para a REQ-035.

### OS-23 · Média · MB-03 / CA-01det / MB-08 · Entrada mais rápida
- Módulo: App de campo
- Nível: Tela
- Elemento: "Pausar turno" (app), "Pausar execução" (web), "Pausar" (irrigação)
- Persona: operador, líder de campo
- Hoje: No app, pausar grava só a hora, sem motivo. Na web, "Pausar execução" age direto e a mensagem diz "Pausada por chuva" sem perguntar. Na irrigação o botão promete "com motivo", mas não pede.
- Proposta: Ao pausar, chips de motivo em 1 toque (Chuva, Vento, Máquina, Falta de insumo, Refeição, Outro). Máquina e falta de insumo abrem a ocorrência já endereçada (manutenção, almoxarife).
- Método: Opções frequentes (chips)
- Ganho: Motivo com 1 toque; falta de insumo chega a quem resolve.
- Evidência: MB-03.dc.html:2838 (cenPausar sem motivo) e :6292; v3out/CA-01det.json ("Pausar execução" com efeito direto); modelo do MB-08 (botão "Pausar a volta com motivo" com mensagem fixa)
- Cuidado: Tempo parado não conta nas horas do turno.

### OS-24 · Média · MB-04 / CA-03 · Resolver em 1 clique
- Módulo: App de campo
- Nível: Campo
- Elemento: Tipo da ocorrência
- Persona: operador, caldeiro, almoxarife, comprador
- Hoje: Não há o tipo "Falta de insumo ou embalagem". Os tipos mudam entre o app (Equipamento, Clima, Praga ou doença, Falha de aplicação, Segurança, Outro) e a web (Quebra de máquina, Praga acima do NC, Clima interrompeu, Vazamento no pivô, Falha de aplicação, Acidente ou segurança).
- Proposta: Uma lista única nos dois e o tipo "Falta de insumo": com a O.S. já escolhida, vai ao almoxarife se há saldo na fazenda, ou ao comprador se não há, levando produto e quantidade da O.S.
- Método: Opções frequentes (chips)
- Ganho: Falta descoberta no campo chega a quem resolve em 1 toque; mesmo vocabulário na web e no app.
- Evidência: MB-04.dc.html:6269 (TIPOS); CA-03.dc.html:58 (opções do campo Tipo)

### OS-25 · Média · CA-03 · Entrada mais rápida
- Módulo: Campo
- Nível: Modal
- Elemento: Formulário "Registrar ocorrência" e clique na linha da ocorrência
- Persona: líder de campo, programador e PCP
- Hoje: 7 campos: Local é texto livre ("Ex.: T1 · OS-0421"), Instante é texto, Evidência é uma lista ("Foto") em vez de anexar. Clicar numa ocorrência já registrada abre o mesmo formulário editável (Tipo, Local, Instante, Relato) e "Salvar" troca o fato.
- Proposta: Local por busca de O.S., talhão ou máquina (já vem preenchido quando aberto da O.S.); Instante = agora, com atalhos hoje e ontem; Evidência = anexar foto. Clique na linha abre o detalhe (CA-03det); corrigir vira "Complementar relato", com trilha.
- Método: Lista ou busca com autocompletar
- Ganho: 2 digitações livres → 0; relato registrado protegido.
- Evidência: v3out/CA-03.json (dialog "Registrar ocorrência" e dialog OC-114 editável com Salvar); robot3/summ.txt (CA-03 · 7 campos: 2 digitados, 4 escolhidos, 1 pré-preenchido)
- Cuidado: Relato original preservado: corrigir = complemento com trilha.

### OS-26 · Média · MB-01 / MB-02 / MB-03 · Ações no ⋯
- Módulo: App de campo
- Nível: Cartão
- Elemento: Cartões de "Minha fila" e "Suas ordens"
- Persona: operador
- Hoje: Cada cartão tem 2 a 3 botões à vista: "Iniciar turno" + "Abrir ordem"; "Retirar no almoxarifado" + "Abrir ordem"; na OS-0420, "Reconhecer" + "Iniciar · bloqueado" + "Registrar ocorrência". A barra de baixo repete "Iniciar turno · OS-0421". "Iniciar · bloqueado" existe só para explicar o bloqueio.
- Proposta: Tocar no cartão abre a ordem; estado e próximo passo em texto ("Bloqueada: Trator T1 · substituto 24/09"); ⋯ com o próximo passo primeiro (Iniciar turno, Retirar, Registrar ocorrência, Reconhecer aviso); a única primária fica na barra de baixo.
- Método: Menu ⋯
- Ganho: 3 → 1 alvo por cartão; sem botão que só explica bloqueio.
- Evidência: v3out/MB-01.inv2.json e MB-02.inv2.json (ações por cartão); modelo do MB-02 (Reconhecer, Iniciar · bloqueado, Registrar ocorrência); v3out/MB-01.json (primária repetida)
- Cuidado: Modo campo (UX-08): ⋯ e itens com alvo de 48 px e contraste para sol.

### OS-27 · Média · MB-05det · Erro ou risco
- Módulo: App de campo
- Nível: Tela
- Elemento: "Receber devolução" e "Registrar divergência"
- Persona: almoxarife
- Hoje: Nenhuma tela leva ao MB-05det: o bloco "Receber devolução · REQ-031" da aba Almoxarife não tem link. "Registrar divergência" não pergunta a quantidade contada; responde fixo "Recebidas 8 de 10 sc".
- Proposta: O bloco da devolução (e o item no Meu dia) abre o MB-05det. "Registrar divergência" pede a quantidade contada (teclado numérico, em sc), sem valor inicial; a diferença vira pendência com dono e prazo.
- Método: Teclado numérico com unidade
- Ganho: Tela alcançável; divergência com o número real.
- Evidência: Busca em v3/*.dc.html: nenhum arquivo aponta para MB-05det.dc.html; MB-05.dc.html:26 (bloco sem link); v3out/MB-05det.json (results "Registrar divergência")
- Cuidado: Quantidade contada nunca pré-preenchida; custódia só zera com recebimento conferido.

### OS-28 · Média · MB-05 · Resolver em 1 clique
- Módulo: App de campo
- Nível: Cartão
- Elemento: Bloco "Conflito de reserva · lote F26-02 · Fungicida A"
- Persona: almoxarife, comprador, programador e PCP
- Hoje: Mostra saldo, demanda da safra e "pendência de compra … (complemento no Planejar safra) · decide o planejamento". A única ação é "Registrar divergência", que é para diferença física, não para este caso.
- Proposta: No ⋯ do bloco: "Avisar o planejamento" (leva saldo, demanda e O.S. afetadas) e "Pedir compra do complemento" (comprador). "Registrar divergência" só para diferença física.
- Método: Resolver em 1 clique
- Ganho: Conflito sai do aparelho do almoxarife para quem decide em 1 toque.
- Evidência: MB-05.dc.html:26 (bloco mbfa_conf com "Registrar divergência"); MB-05.dc.html:6488 (cálculo do conflito)
- Cuidado: Não duplicar a compra do complemento da safra.

### OS-29 · Média · OS / CA-02 · Resolver em 1 clique
- Módulo: Ordem de Serviço
- Nível: Detalhe
- Elemento: Bloqueio "Encerrar bloqueado: sobra em custódia" (OS-0417, 10 sc com Paula)
- Persona: conferente, líder de campo, almoxarife
- Hoje: O bloqueio leva a "Receber devolução no Estoque" (tela do almoxarife). Na CA-02, "Encerrar OS-0417" responde "Indisponível: 10 sc … sob custódia de Paula". Ninguém avisa a Paula.
- Proposta: "Cobrar devolução de Paula · 10 sc até 24/09": cria o item no Meu dia dela e no "A receber" do Rui; quando o Rui recebe, o encerramento libera.
- Método: Resolver em 1 clique
- Ganho: Bloqueio sem dono ativo → 1 clique que aciona as duas pessoas.
- Evidência: OS.dc.html:5210–5220 (osEncBloq: link EST "Receber devolução no Estoque"); CA-02.dc.html:57 (q12, mensagem 4)
- Cuidado: Só a devolução recebida volta ao estoque.

### OS-30 · Média · IN-01 / IN-03 · Necessidade essencial
- Módulo: Início
- Nível: Tela
- Elemento: "Fila do dia" (Meu dia) e "Agenda e pendências"
- Persona: almoxarife, operador, gestor
- Hoje: O Meu dia mostra tarefas de 6 donos (Carlos, Ana, Rui, Equipe expedição, Paula, Equipe qualidade) na mesma lista. Cinco itens se repetem na Agenda (Conferir dia 4 da OS-0421, Receber devolução REQ-031, Substituir Trator T1, Decidir lote L27-013, Definir janela da OS-0422), com nomes e ações diferentes.
- Proposta: Meu dia filtrado pelo perfil (UX-05: operador e almoxarife entram por ele), com "Equipe" como filtro. A Agenda vira a visão Calendário da mesma fila, não uma segunda lista.
- Método: Outro
- Ganho: 2 listas → 1; cada pessoa vê só o que é dela.
- Evidência: IN-01.dc.html:58 (g_dia, 7 linhas, 6 responsáveis); IN-03.dc.html:58 (g_ag, 6 linhas); v3out/IN-03.json

### OS-31 · Média · OS · Entrada mais rápida
- Módulo: Ordem de Serviço
- Nível: Modal
- Elemento: Formulário "Nova ordem" (Criar ordem)
- Persona: programador e PCP, agrônomo
- Hoje: 4 campos sempre em branco (Safra, Cultivo, Atividade, Início da janela), mesmo com Fazenda, Safra e Talhão filtrados na tela. Uma O.S. por vez (um cultivo por emissão). Data sem atalho.
- Proposta: Herdar safra e cultivo do filtro ou do talhão; sugerir o início pela regra da atividade no plano (ex.: DAP −20) com atalhos hoje, amanhã e +7; permitir marcar vários cultivos e emitir uma O.S. por talhão.
- Método: Pré-preenchido pelo contexto
- Ganho: 4 → 1–2 escolhas; 8 talhões em 1 emissão.
- Evidência: OS.dc.html:6418 (nv_open com safra, cultivo, atividade e janela vazios); OS.dc.html:52 (campos da gaveta "Nova ordem")
- Cuidado: Cada O.S. nasce A liberar e passa pela aprovação individual.

### OS-32 · Média · IN-02 · Lote
- Módulo: Início
- Nível: Lote
- Elemento: "Aprovar selecionados"
- Persona: gestor
- Hoje: O lote aprova os itens marcados como independentes, incluindo "Ajuste de inventário Galpão 2 · −12 sc MAP", sem abrir a folha de contagem. Só o orçamento fica de fora ("Exige revisão individual").
- Proposta: Lote só para itens de baixo risco (política, acesso). Ajuste de inventário com perda mostra a folha de contagem e é decidido um a um, ou entra no lote só abaixo de um valor definido. Quando as O.S. entrarem nas Aprovações, ficam fora do lote.
- Método: Lote por seleção
- Ganho: Lote rápido sem baixa de estoque às cegas.
- Evidência: IN-02.dc.html:2356 (v.lote aprova os itens ind = 1); IN-02.dc.html:58 (a6 "Independente: pode entrar em aprovação em lote")
- Cuidado: Alçada e trilha do ajuste; aprovação individual de O.S. (decisão fixa).

### SUP-12 · Média · CMP · Resolver em 1 clique
- Módulo: Compras
- Nível: Detalhe
- Elemento: Requisição de material ou peça com urgência Urgente/Alta
- Persona: comprador, PCM
- Hoje: Toda requisição, mesmo "Urgente" (precisa em 1 dia), passa por A cotar → "Solicitar cotações" → Em cotação → "Emitir pedido": 2 ações e uma espera, sem opção de compra direta pelo contrato ou pelo último fornecedor.
- Proposta: Para urgência Urgente ou Alta, primária "Comprar já · fornecedor do último pedido ou contrato · R$ X · chega dd/mm", com justificativa curta de dispensa de cotação; "Cotar" vira secundária.
- Método: Resolver em 1 clique
- Ganho: compra urgente: 2 ações e espera da cotação → 1 clique + justificativa
- Evidência: v3/CMP.dc.html cmProx ("solicitar cotações", "escolher a proposta e emitir o pedido"), prim("Solicitar cotações (simulado)"), CMM.urgDias {Alta:3, Urgente:1}
- Cuidado: Só fornecedor homologado; alçada pelo valor; dispensa de cotação registrada.

### SUP-13 · Média · MA · Resolver em 1 clique
- Módulo: Manutenção
- Nível: Detalhe
- Elemento: Painel do vencimento (Sem ordem) · primária "Gerar ordem preventiva"
- Persona: PCM
- Hoje: O painel do PM-02 mostra "Filtro de óleo MF 4292 · 1 un falta · livre 0 un", mas a primária é só "Gerar ordem preventiva". Para pedir a peça, o PCM gera a OM, abre a OM e clica "Solicitar compra": 2 cliques em 2 painéis, e o pedido só sai depois.
- Proposta: Com peça em falta, a primária vira "Gerar ordem e pedir peça" (gera a OM e a requisição da falta juntas); sem falta, segue "Gerar ordem preventiva".
- Método: Resolver em 1 clique
- Ganho: 2 → 1 clique; pedido sai no mesmo momento
- Evidência: v3out/MA.json results[2] (PM-02 · Revisão 250 h: "Filtro de óleo MF 4292 · 1 un falta", BTNS "Gerar ordem preventiva"); v3/MA.dc.html ma_omPrim0 ("Solicitar compra" só em A liberar)
- Cuidado: Gera requisição, não emite pedido (P34); peça reservada para a OM.

### SUP-14 · Média · MA · Lote
- Módulo: Manutenção
- Nível: Lote
- Elemento: Retorno de "Gerar 3 ordens preventivas" e filtro "Espera por peça"
- Persona: PCM
- Hoje: "Gerar 3 ordens preventivas" cria OM-0235, OM-0236 e OM-0237 e avisa "OM-0235 com Falta peça"; a compra é pedida ordem por ordem, no painel de cada uma. O filtro "Espera por peça · N" lista as ordens, sem ação em lote.
- Proposta: No retorno do lote e no filtro "Espera por peça": "Pedir peças em falta (N ordens)", uma requisição por grupo de fornecedor, cada item ligado à sua OM, com resultado parcial ("2 pedidas, 1 já tinha requisição").
- Método: Lote por seleção
- Ganho: N ordens com falta: N painéis e N cliques → 1 clique
- Evidência: v3out/MA.json results[0] dlg.text ("3 ordens em A liberar ... OM-0235 com Falta peça"); v3/MA.dc.html chip "Espera por peça · "
- Cuidado: Cada peça reservada para a OM que pediu; requisição repetida não é criada.

### SUP-15 · Média · MA · Erro ou risco
- Módulo: Manutenção
- Nível: Detalhe
- Elemento: Solicitar compra da OM · reserva do saldo livre
- Persona: PCM, almoxarife
- Hoje: Ao "Solicitar compra", o pedido cobre só a diferença (necessário − livre), mas a parte livre não é reservada: a reserva só acontece na liberação. Até a peça chegar, outra ordem pode usar esse livre e a OM continua com falta.
- Proposta: Ao pedir a compra, reservar já o livre para a OM e mostrar na linha "Reservado 1 de 2 · falta 1 (SC-041)".
- Método: Outro
- Ganho: evita segunda compra e OM travada na liberação
- Evidência: v3/MA.dc.html manSolicitar (qtd = manNec − manLivreIt, sem reserva) e manLiberar (reserva só ao liberar)
- Cuidado: Decisão fixa: peça reservada para a ordem que pediu; cancelar devolve a reserva ao livre com registro.

### SUP-16 · Média · MA · Modal e botões
- Módulo: Manutenção
- Nível: Modal
- Elemento: Primárias da OM: "Solicitar compra (simulado · Compras recebe no 1c)" e "Registrar recebimento (simulado · papel do Almoxarifado)"
- Persona: PCM
- Hoje: As primárias trazem texto de protótipo e, depois do pedido, o próximo passo mostrado ao PCM é registrar o recebimento, que é tarefa do almoxarife.
- Proposta: Primária "Pedir peça ao Compras". Depois, estado em texto "Aguardando peça · SC-041 · previsão dd/mm", sem primária para o PCM (só "Ver requisição"); o recebimento fica na fila do almoxarife.
- Método: Outro
- Ganho: próximo passo certo para cada pessoa; zero jargão
- Evidência: v3/MA.dc.html ma_omPrim0; v3out/MA.json results[0] BTNS ("Solicitar compra (simulado · Compras recebe no 1c)", primária)

### SUP-17 · Média · MA, EST · Necessidade essencial
- Módulo: Manutenção
- Nível: Listagem
- Elemento: Entrega da peça reservada ao mecânico
- Persona: almoxarife, mecânico
- Hoje: A OM liberada reserva as peças, mas não encontrei a separação e entrega dessas peças na fila do almoxarife: Estoque › Entregas por O.S. lista só requisições (REQ) de O.S. agrícolas. A baixa acontece quando o mecânico informa "Aplicado" na OM.
- Proposta: OM liberada gera a requisição de peças na fila Entregas do Estoque (separar → entregar ao mecânico, com leitura do código); a sobra volta pelo mesmo fluxo de devolução.
- Método: Pré-preenchido pelo contexto
- Ganho: 1 fila de entregas para insumo e peça; custódia da peça com rastro
- Evidência: v3/EST.dc.html bloco "etapa 2: entregas por O.S." (linhas de c.reqs: Requisição, O.S.); v3/MA.dc.html manLiberar (reserva) e om_pcs (aplicado digitado na execução)
- Cuidado: Sem baixa em dobro: entrega move para a custódia, aplicação baixa da custódia.

### SUP-18 · Média · CMP, MA · Entrada mais rápida
- Módulo: Compras
- Nível: Detalhe
- Elemento: Recebimento de peças e materiais
- Persona: almoxarife
- Hoje: Peça e material são recebidos no painel da requisição em Compras (quantidade digitada por item, com atalho "Tudo") ou pela "ponte" da Manutenção; não passam pelos Recebimentos do Estoque nem por NF.
- Proposta: Todo recebimento (insumo, peça, material) entra na mesma fila de Recebimentos do Estoque, com leitura da NF-e; Compras e Manutenção só mostram o estado ("Recebido · REC-xxx").
- Método: Captura (XML de NF-e)
- Ganho: 1 lugar e 1 método de recebimento; 0 digitação sem divergência
- Evidência: v3/CMP.dc.html cmVals (cm_recIt, "Registrar recebimento", "Tudo · "); v3/MA.dc.html manReceber ("simulado · papel do Almoxarifado"); v3/EST.dc.html g_rec (só PC-088, 090, 091, 096)
- Cuidado: Peça da OM chega reservada à OM (D5).

### SUP-19 · Média · CD-06 · Entrada mais rápida
- Módulo: Cadastros
- Nível: Modal
- Elemento: Cadastrar item / Item
- Persona: almoxarife, comprador
- Hoje: O cadastro mostra 11 campos de uma vez (nome, grupo, unidade, embalagem, conteúdo, controle, preço, data do preço, garantia, local padrão, situação). Não há código no fornecedor, GTIN/código de barras nem registro do produto, que permitiriam casar o item da NF-e e ler a embalagem. O preço de referência é digitado com data.
- Proposta: 5 campos visíveis (nome, grupo, unidade, embalagem e conteúdo, local) + "Mais opções". Seção "Códigos" (GTIN e código no fornecedor, gravados na 1ª NF lida). Preço de referência atualizado pelo último pedido ou NF, com a origem à vista.
- Método: Captura (XML de NF-e)
- Ganho: 11 → 5 campos visíveis; preço sem digitação; da 2ª nota em diante o item casa sozinho
- Evidência: v3/CD-06.dc.html GRIDS g_itm edit.fields (13 campos; 11 visíveis, 2 só com "Outro grupo…"); busca por GTIN, código de barras e XML em CD-06 sem resultado
- Cuidado: Item com saldo não troca de unidade (trava atual).

### SUP-20 · Média · SU-02, SU-03, SU-05det, SU-07, SU-07det, SU-08, SU-09 · Entrada mais rápida
- Módulo: Estoque
- Nível: Campo
- Elemento: Formulário lateral das telas SU: quantidades e datas
- Persona: almoxarife, comprador
- Hoje: Os formulários laterais das telas SU usam campo de texto sem teclado numérico (quantidade da reserva, da devolução, da transferência, da perda) e datas sem atalho (início e fim da exceção, nova emissão e chegada da carga, data de corte).
- Proposta: Campo numérico com teclado numérico e unidade ao lado; datas com chips "hoje", "+7", "fim do mês" ou relativos ao contexto ("depois da carga 3").
- Método: Teclado numérico com unidade
- Ganho: menos toques no celular e menos erro de vírgula
- Evidência: v3/SU-07det.dc.html modelo do painel: input "{{f.fid}}" sem inputMode; v3out/SU-03.json results[0] "Quantidade *" type text sem inputmode; robot3/summ.txt (SU-02: 2 datas sem atalho; SU-05det: 2; SU-09: 1)

### SUP-21 · Média · SU-08 · Entrada mais rápida
- Módulo: Estoque
- Nível: Modal
- Elemento: Transferir entre locais
- Persona: almoxarife
- Hoje: 5 campos: item·lote, quantidade com unidade "kg ou L", origem (padrão Galpão 2, sem relação com o lote), destino e motivo digitado. A origem e a unidade já estão no lote escolhido.
- Proposta: Abrir pelo ⋯ do lote em Saldos (item, lote, origem e unidade preenchidos); motivo em chips ("abastecer frente", "consolidar", "outro").
- Método: Pré-preenchido pelo contexto
- Ganho: 5 → 2 campos (quantidade e destino)
- Evidência: v3/SU-08.dc.html PN.trf (q u "kg ou L", o def "Galpão 2", mot txt); PN.per (u "kg ou L")
- Cuidado: Transferência fica em trânsito até confirmar no destino.

### SUP-22 · Média · PSUP · Necessidade essencial
- Módulo: Suprimentos
- Nível: Cartão
- Elemento: Cartões do Painel (Lotes com saldo físico, com reserva, em quarentena, Requisições a entregar)
- Persona: gerente de suprimentos, almoxarife, comprador
- Hoje: 4 cartões de contagem (28 lotes com saldo, 4 com reserva, 1 em quarentena, 5 requisições a entregar) e um gráfico de lotes. Os cartões não abrem nada (só "Como calcular") e não dizem o que fazer. Faltas atrasadas, NF a conferir, divergência de preço e ajustes a aprovar não aparecem.
- Proposta: Lista de pendências com a ação no item: "Faltas com pedir-até vencido (5) · Comprar urgente", "NF a conferir (1) · Conferir", "Divergência de preço (1) · Resolver", "Ajuste aguardando (1) · Aprovar", "Quarentena com laudo até 27/09". Cada item abre a listagem filtrada.
- Método: Resolver em 1 clique
- Ganho: a decisão do dia na 1ª tela; 1 clique até a ação
- Evidência: v3out/PSUP.json inv.cards (acts só "Como calcular", clickable false); v3/PSUP.dc.html textos "Com quarentena / Com reserva / Sem reserva"

### SUP-23 · Média · PMAN · Necessidade essencial
- Módulo: Manutenção
- Nível: Cartão
- Elemento: Cartões do Painel (Pendências sem ordem, Ordens abertas, Em execução, Ativos bloqueados)
- Persona: PCM
- Hoje: 4 cartões e um gráfico de ordens por estado, sem clique. Não mostra "Espera por peça", que a lista de ordens já calcula.
- Proposta: Cartões viram atalhos da listagem (clique abre Manutenção filtrada) e entra "Espera por peça (N) · Pedir peças"; o gráfico sai.
- Método: Resolver em 1 clique
- Ganho: 1 clique até a lista certa
- Evidência: v3out/PMAN.json inv.cards (acts só "Como calcular"); v3/MA.dc.html chip "Espera por peça · "

### SUP-24 · Média · SU-01 · Ações no ⋯
- Módulo: Compras
- Nível: Linha da tabela
- Elemento: Necessidade líquida por data · coluna Próxima ação e botão "Reprogramar proposta"
- Persona: comprador
- Hoje: A coluna "Próxima ação" tem links soltos ("Em cotação", "Ver contrato", "Cotar"). "Reprogramar proposta" é botão do topo: abre formulário com o item escolhido numa lista de 18 (padrão: o 1º, Adjuvante espalhante), nova data e motivo. Os 4 cartões do topo repetem o cabeçalho e não filtram.
- Proposta: Estado em texto na linha ("Em cotação · SOL-2026-07", "Atrasado"). ⋯ na ordem: linha atrasada → Comprar urgente, Ver cotação, Reprogramar necessidade, Ver origens; com contrato (KCl, Diesel) → Liberar carga do contrato, Ver contrato, Reprogramar; peça (Rolamento) → Cotar, Comprar urgente, Ver OM-0234. Cartões viram filtros.
- Método: Menu ⋯
- Ganho: Reprogramar: 3 campos → 2 (item vem da linha)
- Evidência: v3/SU-01.dc.html GRIDS g_nec p.acao (links), PN.rep (item def "Adjuvante espalhante", data, motivo); template linha 48 (cartões sem clique)

### SUP-25 · Média · SU-07 · Ações no ⋯
- Módulo: Estoque
- Nível: Linha da tabela
- Elemento: Fila de separação por ordem · coluna Estado · próxima ação
- Persona: almoxarife
- Hoje: A coluna tem botões soltos por linha: "Receber devolução", "Ver consumo", "Confirmar entrega", "Receber no Estoque", "Separar FEFO", "Entregar 8.000 kg". Na REQ-036 e na REQ-038 o botão só responde "Bloqueado".
- Proposta: Estado em texto ("Separada · falta entregar a Marcos"). ⋯ na ordem: próximo passo (Separar FEFO / Confirmar entrega / Entregar parcial / Receber devolução), Ver O.S., Ver lote, Reprogramar entrega. Linha bloqueada mostra o motivo e quem resolve ("Impedida pela OM-0233 · Carlos"), sem botão.
- Método: Menu ⋯
- Ganho: nenhum botão que falha; padrão único
- Evidência: v3/SU-07.dc.html PREVALS (nx por estado), v.ent36 e v.sep38 (toast "Bloqueado")

### SUP-26 · Média · SU-09, EST · Ações no ⋯
- Módulo: Estoque
- Nível: Linha da tabela
- Elemento: Contagens cegas (SU-09) e Contagens (EST) · ações na célula
- Persona: almoxarife, gerente de suprimentos
- Hoje: Ações dentro da célula: "Aprovar ajuste", "Submeter ajuste" + "Recontar", "Contar no app", "Ver efeito no extrato". "Aprovar ajuste INV-2609" ainda se repete como primária no topo.
- Proposta: ⋯ na ordem: Aprovar ajuste (ou Submeter ajuste, que já abre causa e evidência), Recontar, Contar no app, Ver extrato. Primária do topo = "Aprovar ajustes (N)", que abre a fila filtrada.
- Método: Menu ⋯
- Ganho: "Submeter" sem causa: 2 passos e aviso → 1 passo
- Evidência: v3out/SU-09.json inv.tables[0].rows (acts ["Aprovar ajuste"], ["Submeter ajuste","Recontar"], ["Ver efeito no extrato"], ["Contar no app"]); v3out/SU-09.json inv.primary; v3/EST.dc.html k:"act" "Aprovar ajuste", "Recontar"

### SUP-27 · Média · EST · Ações no ⋯
- Módulo: Estoque
- Nível: Linha da tabela
- Elemento: Saldos por lote e local; Custódia e devoluções · confirmação dentro da célula
- Persona: almoxarife, gestor
- Hoje: Em Saldos, "Liberar após inspeção" fica na célula e, ao clicar, a própria célula vira "informe o laudo acima" + "Manter". Em Custódia, "Aceitar consumo" e "Recusar relato" ficam lado a lado na célula e a confirmação ("Confirmar aceite" / "Voltar") também aparece dentro da tabela.
- Proposta: ⋯ do lote: Liberar com laudo, Reprovar com laudo, Segregar, Transferir, Reservar para ordem, Ver movimentos. ⋯ da custódia: Receber devolução, Aceitar consumo, Recusar relato, Ver O.S. Confirmação em modal com a consequência.
- Método: Menu ⋯
- Ganho: tabela limpa; decisão com consequência clara
- Evidência: v3/EST.dc.html elotRow ("Liberar após inspeção", "informe o laudo acima", "Manter") e ecfCel ("Aceitar consumo", "Recusar relato", "Confirmar aceite", "Voltar")
- Cuidado: Liberar quarentena exige laudo e alçada (AL-11); aceite acima da custódia é do gestor (AL-10).

### SUP-28 · Média · SU-06, SU-08 · Ações no ⋯
- Módulo: Estoque
- Nível: Linha da tabela
- Elemento: Recebimentos e divergências (SU-06); Extrato imutável (SU-08)
- Persona: almoxarife, comprador, financeiro
- Hoje: SU-06: a NF 4501 tem "Liberar qualidade" e "Encaminhar título" na célula; "Segregar lote" e "Resolver diferença" são botões do topo que agem sobre uma linha (K26-11, NF 8812) e pedem o lote de novo. SU-08: "Confirmar recebimento" e "Aprovar perda" na célula; "Estornar com vínculo" e "Registrar perda" no topo pedem escolher o movimento ou o lote numa lista.
- Proposta: SU-06, ⋯ da NF: Conferir, Resolver diferença, Liberar qualidade, Segregar, Encaminhar título, Ver pedido. SU-08, ⋯ do movimento: Confirmar no destino, Aprovar perda, Estornar com vínculo (movimento preenchido, só o motivo), Ver documento.
- Método: Menu ⋯
- Ganho: Estornar: 2 campos → 1; Segregar: lote já escolhido
- Evidência: v3/SU-06.dc.html PREVALS (k:"act" "Liberar qualidade", link "Encaminhar título"), PN.seg e PN.div; v3/SU-08.dc.html PREVALS ("Confirmar recebimento", "Aprovar perda"), PN.est (orig select)
- Cuidado: Estorno sempre cria movimento novo com vínculo; perda só baixa depois da alçada.

### SUP-29 · Média · SU-03, SU-05 · Ações no ⋯
- Módulo: Compras
- Nível: Linha da tabela
- Elemento: Saldos e lotes (SU-03); Contratos, Pedidos e Programação de entregas (SU-05)
- Persona: almoxarife, comprador
- Hoje: SU-03: a linha do F26-02 traz o link "Reserva em conflito" no meio do item; "Reservar para ordem" é botão do topo. SU-05: o link "Abrir contrato" fica dentro da célula do contrato; "Emitir pedido", "Confirmar fornecedor", "Receber ›" e "Formalizar contrato" são botões de seção, sem linha.
- Proposta: SU-03, ⋯ do lote: Resolver reserva em conflito (quando houver), Reservar para ordem (lote preenchido), Requisitar para O.S., Segregar, Transferir, Ver movimentos. SU-05: clique no contrato abre o detalhe; ⋯ do pedido: Receber, Confirmar fornecedor, Reprogramar previsão; ⋯ da carga: Emitir liberação, Reprogramar carga.
- Método: Menu ⋯
- Ganho: ação ao lado do registro certo; 1 escolha a menos em cada formulário
- Evidência: v3out/SU-03.json inv.tables[0].rows[2] acts ["Reserva em conflito"]; v3out/SU-05.json inv.tables[0].rows[0] acts ["Abrir contrato"]; v3/SU-05.dc.html botões "Emitir pedido", "Confirmar fornecedor", "Formalizar contrato"

### SUP-30 · Média · CMP · Ações no ⋯
- Módulo: Compras
- Nível: Linha da tabela
- Elemento: Safras e solicitações; Pedidos e entregas
- Persona: comprador
- Hoje: Safras e solicitações: 1 a 2 ações na célula ("Ver origem" + "Abrir compra", "Abrir Planejar safra", "Consultar pedidos"). Pedidos e entregas: "Confirmar fornecedor" na célula.
- Proposta: Clique na safra abre a compra. ⋯ da safra: Abrir compra (ou Abrir Planejar safra sem solicitação), Ver origem, Consultar pedidos. ⋯ do pedido: Confirmar fornecedor, Reprogramar previsão, Receber (abre o Estoque na NF).
- Método: Menu ⋯
- Ganho: linha limpa; 1 padrão
- Evidência: robot3/summ.txt "CMP | linha da tabela 1 | 2 ações [Ver origem, Abrir compra] | kebab=False"; v3/CMP.dc.html k:"act" "Abrir compra", "Consultar pedidos", "Confirmar fornecedor"

### SUP-31 · Média · MA · Ações no ⋯
- Módulo: Manutenção
- Nível: Linha da tabela
- Elemento: Sem ordem e Ordens
- Persona: PCM
- Hoje: Em "Sem ordem", a linha tem o link do ID e o próximo passo só como texto ("Gerar ordem preventiva"); para agir é preciso abrir o painel. Em "Ordens", a coluna Pendência mostra "Falta peça · Otávio" sem ação na linha.
- Proposta: ⋯ em Sem ordem: Gerar ordem (ou Gerar ordem e pedir peça), Vincular à OM aberta, Criar corretiva, Fechar sem serviço (motivo). ⋯ em Ordens: próximo passo da fase (Pedir peça / Liberar / Conferir), Mover janela, Cancelar com motivo (último, separado).
- Método: Menu ⋯
- Ganho: agir sem abrir o painel nos casos simples
- Evidência: v3out/MA.json inv.tables[0].rows (acts só o ID "PM-02 v2"); v3/MA.dc.html linhas de g_so (prox texto) e ma_linhaOm (pend)
- Cuidado: Cancelar exige motivo e devolve a reserva ao livre.

### SUP-32 · Média · SU-05det · Modal e botões
- Módulo: Compras
- Nível: Detalhe
- Elemento: Botão "Emitir liberação da carga 4" (2 vezes)
- Persona: comprador, financeiro
- Hoje: O botão aparece 2 vezes (topo e seção) e sempre responde "Bloqueado · o pico projetado de R$ 186,4 mil passa do limite de R$ 150 mil". A primária certa ("Reprogramar carga 4") já existe.
- Proposta: Um só lugar, desabilitado com o motivo à vista ("acima do limite de crédito até receber a carga 3 · Léo") e 2 saídas: Reprogramar carga 4 (primária) e Solicitar crédito (financeiro, com valor e data preenchidos).
- Método: Outro
- Ganho: nenhum clique que falha; caminho ao financeiro com contexto
- Evidência: v3out/SU-05det.json results[1] (status "Bloqueado ..."); v3/SU-05det.dc.html 2 botões "Emitir liberação da carga 4" (do_emit)
- Cuidado: Limite de crédito do fornecedor respeitado.

### SUP-33 · Média · SU-05 · Modal e botões
- Módulo: Compras
- Nível: Tela
- Elemento: Botão "Emitir pedido" (seção Pedidos)
- Persona: comprador
- Hoje: Sem modal, "Emitir pedido" responde "PC-095 programado · emissão automática em 26/09". O nome diz emitir; o efeito é agendar uma emissão automática futura, sem confirmação.
- Proposta: Botão "Programar pedido PC-095 para 26/09" com modal curto (quantidade, contrato, data, exposição); em 26/09 vira rascunho para o comprador confirmar a emissão.
- Método: Outro
- Ganho: consequência clara antes do clique
- Evidência: v3/SU-05.dc.html SIMS.ped ("PC-095 programado ... emissão automática em 26/09"); v3out/SU-05.json results[0]
- Cuidado: P34/P62: automação gera rascunho e nunca emite pedido sozinha.

### SUP-34 · Média · SU-04 · Modal e botões
- Módulo: Compras
- Nível: Listagem
- Elemento: Comparação equalizada · "Selecionar Fertisul" e link "Aprovar contratação ›"
- Persona: comprador, aprovador por alçada
- Hoje: A escolha da proposta é um botão no topo ("Selecionar Fertisul"); clicar numa proposta abre detalhe só com "Fechar". O link "Aprovar contratação ›" abre a lista de contratos, não uma aprovação.
- Proposta: ⋯ da proposta: Selecionar (a melhor equalizada em 1º), Pedir esclarecimento, Ver itens. Link renomeado "Ver contratos ›", ou trocado por "Enviar para aprovação" quando passar da alçada.
- Método: Menu ⋯
- Ganho: decisão no registro certo; nome igual ao destino
- Evidência: v3out/SU-04.json inv.primary ["Selecionar Fertisul"], results[3] (Proposta · Fertisul, BTNS só "Fechar"); v3/SU-04.dc.html link "Aprovar contratação ›" → SU-05.dc.html
- Cuidado: Seleção fora do menor custo exige justificativa.

### SUP-35 · Média · CMP · Lote
- Módulo: Compras
- Nível: Lote
- Elemento: Materiais, peças e serviços · linhas "Abaixo do ponto de pedido"
- Persona: comprador, almoxarife
- Hoje: Cada item abaixo do ponto de pedido (no exemplo, Filtro de óleo MF 4292 e Graxa EP2) abre o seu painel e a sua requisição de reposição, um por vez.
- Proposta: Selecionar as linhas "Abaixo do ponto de pedido" → "Abrir reposição dos selecionados": uma requisição por grupo de fornecedor, quantidades até o máximo da política, resultado parcial explícito.
- Método: Lote por seleção
- Ganho: N itens: N painéis e N cliques → 1 seleção e 1 clique
- Evidência: v3/CMP.dc.html cmPre (linhas "Abaixo do ponto de pedido"), cmmRepor (1 item por vez); semente: FIL-MF4292 saldo 0 / mín 2, GR-EP2 saldo 18 / mín 20
- Cuidado: Automação gera requisição, não pedido (P34); item já pedido não repete.

### POS-09 · Média · BEN · Entrada mais rápida
- Módulo: Beneficiamento
- Nível: Modal
- Elemento: Painel da ordem › 'Registrar saída' (Fluxo, Classe, Caixas, Bruto sem pallet)
- Persona: gerente do packing, apontador da linha
- Hoje: Cada saída é um formulário: escolhe fluxo e classe, digita caixas e bruto. Um turno com classe A, classe B, outro destino e descarte pede 4 formulários e até 8 números. A rota tem 'Balança do packing (a13)' cadastrada, mas o bruto é digitado; a tara já é calculada pelo cadastro da caixa.
- Proposta: Grade 'Saídas do turno' com uma linha por classe e destino da rota: caixas contadas e bruto lido da balança do packing ('Ler balança' por linha); Enter desce para a próxima linha; um 'Registrar saídas' grava tudo, com recibo por linha.
- Método: Grade editável
- Ganho: 4 formulários → 1; bruto digitado 4 → 0; só caixas digitadas
- Evidência: v3/BEN.dc.html l.5442 (bnSaidaForm: 'Caixas' e 'Bruto sem pallet' digitados, tara calculada); l.3825 (BENC.par.balanca 'Balança do packing (a13)', pesagem 'caixa')
- Cuidado: Estorno segue por registro; perda identificada só com ticket de pesagem; quantidade nunca vem do turno anterior.

### POS-10 · Média · BEN · Modal e botões
- Módulo: Beneficiamento
- Nível: Detalhe
- Elemento: Botão verde 'Autorizar rota e liberar' na ordem impedida (OB-0112)
- Persona: gerente do packing
- Hoje: Com 2 impedimentos abertos (lote L39-119 e caixas), o painel mostra 'Autorizar rota e liberar' como primária ativa. O clique é recusado ('Não gravado'). O próximo passo diz 'Resolver 2 impedimentos', mas o verde manda liberar.
- Proposta: Com impedimento, a primária vira a primeira resolução ('Pedir N caixas' ou 'Abrir inspeção do L39-119'); 'Autorizar rota e liberar' só fica verde com a lista vazia.
- Método: Outro
- Ganho: Zero clique recusado; o verde coincide com o próximo passo
- Evidência: v3/BEN.dc.html l.5554 (nx.acao 'liberar' gera a primária mesmo com impedimentos); v3out/BEN.json results[2] (botão primário 'Autorizar rota e liberar' com próximo passo 'Resolver 2 impedimentos')
- Cuidado: A trava de liberação no servidor continua valendo, independente do botão.

### POS-11 · Média · EXPED · Entrada mais rápida
- Módulo: Expedição
- Nível: Detalhe
- Elemento: Programar carga (Placa) e Confirmar saída (Peso bruto, Tara)
- Persona: balanceiro, expedição
- Hoje: Programar carga já é por toque, menos a placa, digitada. Confirmar saída pede bruto e tara digitados; com mais de um lote, um kg por lote (vem com o previsto). Nada é lido da balança.
- Proposta: Na saída, 'Ler balança' preenche bruto, tara e ticket; a placa vem do veículo do cadastro do transportador ou da leitura na portaria. O aviso de excesso sobre a reserva continua antes de gravar.
- Método: Captura (balança)
- Ganho: Saída 2 → 0 números digitados; programação 1 → 0 textos
- Evidência: v3/EXPED.dc.html l.5934 ('Placa' t:'txt'); l.5979 (Confirmar saída: 'Peso bruto' e 'Tara' digitados; ajuda 'Bruto e tara da balança em kg, sem valor anterior')
- Cuidado: Baixa do lote uma única vez; excesso e crédito continuam com a gestora; nunca peso anterior.

### POS-12 · Média · BEN · Resolver em 1 clique
- Módulo: Beneficiamento
- Nível: Linha da tabela
- Elemento: Impedimento de qualidade da entrada (L39-119 em inspeção · resolve Marta)
- Persona: gerente do packing, classificador
- Hoje: O impedimento diz quem resolve (Marta, qualidade), mas a única ação é 'Retirar L39-119 da ordem'. Não há atalho para a inspeção nem aviso à Marta; o link do lote está mais abaixo, em 'Entradas' ('Ver no Estoque de produto').
- Proposta: No próprio impedimento: 'Abrir inspeção do L39-119' (Estoque de produto já no formulário de resultado) e 'Avisar Marta' com o prazo da janela da ordem. 'Retirar da ordem' vai para o ⋯.
- Método: Resolver em 1 clique
- Ganho: Texto + rolagem + troca de tela → 1 clique até quem resolve, com o lote e o prazo
- Evidência: v3/BEN.dc.html l.5462-5463 (ação da linha só 'Retirar … da ordem'; link só existe para caixas); v3out/BEN.json results[2] (botões do painel)
- Cuidado: Liberar o lote segue como decisão da Qualidade.

### POS-13 · Média · PROD · Necessidade essencial
- Módulo: Estoque de produto (qualidade)
- Nível: Modal
- Elemento: Formulário 'Registrar resultado' (Resultado: Conforme ou Não conforme; Observação)
- Persona: classificador
- Hoje: O resultado é só Conforme ou Não conforme, mais texto livre. Os valores medidos (calibre, firmeza, defeitos, umidade, impureza, peneira) não ficam registrados. A tela legada CO-06det tinha 'Resultado da amostra' com padrão × medido.
- Proposta: O formulário traz os critérios do padrão da inspeção (critério, limite, unidade) e pede só o valor medido, com teclado numérico e unidade; o sistema calcula conforme por critério e sugere a classe atingida. Valor do medidor entra por captura quando houver.
- Método: Calculado
- Ganho: Decisão com evidência numérica; classe sugerida pelo sistema; texto só na exceção
- Evidência: v3/PROD.dc.html l.5488-5490 (campos 'Resultado' por opção e 'Observação' texto); v3/CO-06det.dc.html GRIDS g_am (Critério | Padrão do tipo 6 | Medido | Situação)
- Cuidado: Medição nunca pré-preenchida com o último valor; resultado não libera o lote sozinho.

### POS-14 · Média · PCOM · Resolver em 1 clique
- Módulo: Painel comercial
- Nível: Detalhe
- Elemento: Painel do período em déficit (ex.: Mamão S41 · PV-038 com déficit de 30.000 kg)
- Persona: comercial, gestor
- Hoje: O painel explica a conta e diz 'Para cobrir: publicar a previsão de S41 (Previsão e colheita · Produção) ou renegociar as vendas abaixo'. No déficit não há primária; as vendas têm só 'Abrir venda'.
- Proposta: Duas ações no painel: 'Pedir publicação da S41' (abre Previsão e colheita no talhão e semana e avisa a agrônoma) e 'Renegociar PV-038' (abre a venda já em encerrar saldo ou revisão, com o déficit calculado).
- Método: Resolver em 1 clique
- Ganho: Texto → 1 clique até a tela e a pessoa certa, com período e quantidade
- Evidência: v3/PCOM.dc.html l.5927 ('Para cobrir: publicar a previsão…'); l.5951 (linha em déficit sem primária); v3out/PCOM.json inv.tables[0] ('Déficit S41 … PV-038 déficit 30.000 kg')
- Cuidado: Déficit é aviso e não trava (D-C16); publicar previsão é ato da agrônoma.

### POS-15 · Média · VEN · Resolver em 1 clique
- Módulo: Vendas
- Nível: Detalhe
- Elemento: Venda 'Em risco' (expedição impedida no lote reservado)
- Persona: comercial
- Hoje: O próximo passo diz 'Se não resolver a tempo, Comercial troca o lote ou cancela a reserva'. Trocar exige cancelar a reserva (com motivo) e depois reservar outro lote em outro formulário.
- Proposta: 'Trocar lote' na linha da reserva: lista os lotes aptos do mesmo produto e classe, com disponível e validade, e troca numa operação (cancela e reserva com o mesmo motivo).
- Método: Resolver em 1 clique
- Ganho: 2 formulários e 1 motivo → 1 escolha
- Evidência: v3/VEN.dc.html l.5899-5900 (comProx 'troca o lote ou cancela a reserva'); comPanVenda l.5990+ ('Cancelar reserva' por linha; reservar em formulário separado)
- Cuidado: Dedução única (ATP-07); só lote apto e compatível; reserva atômica no servidor.

### POS-16 · Média · VEN, PROD · Entrada mais rápida
- Módulo: Vendas
- Nível: Modal
- Elemento: 'Reservar lote para o pedido' (Lote apto, Quantidade a reservar)
- Persona: comercial
- Hoje: A reserva é um lote por vez: escolhe o lote e confirma a quantidade sugerida (menor entre disponível e falta). Um pedido de 10.000 kg com lotes de cerca de 3.000 kg (L38-115 a L38-118) pede 4 formulários.
- Proposta: 'Alocar automaticamente': o sistema propõe a divisão da falta entre os lotes aptos (primeiro o que vence antes, mesma classe e local) e o usuário confirma uma vez; cada lote vira uma reserva com recibo.
- Método: Calculado
- Ganho: 4 formulários → 1 confirmação
- Evidência: v3/PROD.dc.html l.5372-5386 (prFormReserva: um lote, sugestão mínima entre disponível e falta); v3out/PROD.json (L38-115 3.010 kg, L38-116 2.980 kg…); v3out/PCOM.json (PV-036 10.000 kg)
- Cuidado: Reserva atômica e por lote; só lote apto; a proposta é editável antes de gravar.

### POS-17 · Média · COLH · Lote
- Módulo: Colheita e pós-colheita
- Nível: Lote
- Elemento: Talhões 'Sem previsão' (próximo passo 'Contar os frutos de 20 plantas · equipe de colheita (app)')
- Persona: agrônoma, encarregado de colheita
- Hoje: No mamão, 10 talhões aparecem sem previsão. Em cada um, a primária 'Coletar contagem' só navega para a tela do app (MB-07); não cria tarefa para a equipe. São 10 painéis abertos e nenhuma tarefa registrada.
- Proposta: Selecionar os talhões sem previsão e 'Pedir contagem à equipe': uma tarefa por talhão no app do encarregado (20 plantas, prazo, responsável); a contagem volta para o rascunho da previsão.
- Método: Lote por seleção
- Ganho: 10 painéis → 1 seleção e 1 clique; pedido com prazo e dono
- Evidência: v3out/COLH.json inv.tables[0].rows[0] ('1 em colheita · 1 colhida · 10 sem previsão'); v3/COLH.dc.html l.3809 (ação 'Coletar contagem' com h 'MB-07.dc.html#…')
- Cuidado: Publicar previsão continua individual e da agrônoma; contagem é medição, sem valor anterior.

### POS-18 · Média · VEN, PCOM · Resolver em 1 clique
- Módulo: Vendas
- Nível: Detalhe
- Elemento: Próximo passo 'vencido · cobrar' e frase 'Recebimento é do Financeiro (fora desta etapa)'
- Persona: financeiro, comercial
- Hoje: Venda entregue com título vencido mostra 'vencido · cobrar' e manda ao Financeiro só por texto. Nenhum botão leva o título para a cobrança.
- Proposta: Ação 'Enviar à cobrança' no próprio título (cliente, valor, vencimento, carga), que entra na fila do Financeiro (GE-05) já no título; o comercial vê o retorno na venda.
- Método: Resolver em 1 clique
- Ganho: Cobrança disparada sem troca de tela nem cópia de dados
- Evidência: v3/VEN.dc.html l.5898 ('Recebimento é do Financeiro (fora desta etapa)'); v3/PCOM.dc.html l.5937 ('Recebimento e baixa são do Financeiro (fora desta etapa)')
- Cuidado: Baixa e recebimento seguem com o Financeiro; envio idempotente.

### POS-19 · Média · CO-01, CO-02, CO-03, CO-04, CO-05, CO-06, CO-07 · Ações no ⋯
- Módulo: Colheita e pós-colheita (legado)
- Nível: Linha da tabela
- Elemento: Coluna 'Ação' das tabelas g_of, g_oc, g_cg, g_rc, g_ob, g_in, g_es
- Persona: encarregado de colheita, balanceiro, gerente do packing, classificador
- Hoje: Cada linha tem até 3 alvos com efeitos diferentes: o ID (OC-0510, OB-0110) abre o detalhe, o botão da coluna Ação executa ou navega, e o clique na linha abre um formulário de edição (ex.: em CO-02 abre 'Ordem de colheita' para janela e equipe, não o detalhe). Sem ⋯.
- Proposta: Linha abre o detalhe; ações no ⋯, próximo passo primeiro. CO-01: Coletar contagem | Programar colheita | Comparar pedidos, Revisar previsão. CO-02: Registrar avanço | Iniciar | Liberar | Conferir cargas, Ajustar janela e equipe, Ver cargas. CO-03: Confirmar chegada | Vincular pesagem, Reimprimir romaneio. CO-04: Conferir carga | Segregar | Receber bloqueado | Solicitar inspeção | Encaminhar processo. CO-05: Registrar saídas | Registrar avanço | Liberar ordem, Ver lote. CO-06: Registrar resultado | Decidir lote. CO-07: Alocar pedido | Abrir inspeção | Abrir lote. A coluna Ação some.
- Método: Menu ⋯
- Ganho: 1 alvo previsível por linha; 1 coluna a menos em 7 tabelas
- Evidência: v3/CO-0x.dc.html GRIDS (partes 'cta' e 'act' por linha; edit m=form no clique da linha); robot3/summ.txt 'AÇÕES NA LINHA' (CO-02 ['OC-0510', 'Registrar avanço'] kebab=False)
- Cuidado: Etapa só muda por ação (P13); ordem encerrada continua só em consulta.

### POS-20 · Média · LO-01, LO-02, LO-03, LO-04 · Ações no ⋯
- Módulo: Logística
- Nível: Linha da tabela
- Elemento: Tabelas g_ag, g_fi, g_ex, g_vg, g_pr, g_sv
- Persona: expedição e logística, financeiro
- Hoje: Uma ação por linha num botão (Ver fila, Conferir carga, Separar lotes, Contratar frete, Avaliar encaixe, Registrar chegada, Reprocessar NF, Cobrar NF, Abrir caso RC-15, Resolver na expedição, Ver frete, Solicitar documento, Encaminhar pagamento). O clique na linha abre outro formulário (Reprogramar janela, Posição na fila, Viagem programada). Sem ⋯.
- Proposta: Linha abre o detalhe; ⋯ com o próximo passo primeiro. LO-01: Separar lotes | Contratar frete | Conferir carga, Reprogramar janela, Ver na fila. LO-02 fila: Registrar chegada | Avaliar encaixe | Conferir carga | Reprocessar NF, Mudar posição. LO-02 expedições: Separar lotes | Cobrar NF | Conferir carga, Trocar veículo ou doca. LO-03: Abrir caso | Resolver na expedição | Conferir carga, Ver frete. LO-04: Solicitar documento, Ver programação; Encaminhar pagamento, Ver rateio.
- Método: Menu ⋯
- Ganho: Padrão único; a edição deixa de disparar no clique da linha
- Evidência: v3/LO-0x.dc.html GRIDS (partes cta e act); v3out/LO-02.json inv.tables[0] e [1] (row0 acts ['Conferir carga'], kebab=false)
- Cuidado: Mudar posição na fila exige motivo e mantém a janela original (FILA-07).

### POS-21 · Média · LO-04 · Modal e botões
- Módulo: Logística
- Nível: Tela
- Elemento: Primária 'Contratar Rota Sul · R$ 1.824'
- Persona: expedição e logística, financeiro
- Hoje: Um clique no cabeçalho contrata o frete e vincula a VG-119 ao contrato CT-0912, sem resumo, sem alçada e sem desfazer.
- Proposta: Confirmação curta com prestador, carga, base (9,6 t × R$ 190/t), condição de pagamento e quem aprova; depois, 'Desfazer' por alguns segundos e 'Cancelar contratação' com motivo enquanto a viagem não sai.
- Método: Outro
- Ganho: Compromisso com terceiro só com a consequência à vista; erro reversível
- Evidência: v3out/LO-04.json results[0] (effect 'Rota Sul contratada · R$ 1.824 … VG-119 vinculada ao contrato CT-0912'); dica da tela 'Contratar é ação autorizada'
- Cuidado: Alçada de contratação; idempotência; cotação não despacha transportador.

### POS-22 · Média · LO-02det · Entrada mais rápida
- Módulo: Logística
- Nível: Modal
- Elemento: 'Registrar lacre' (Nº do lacre, Conferido por, Evidência)
- Persona: expedição e logística
- Hoje: Nº do lacre é digitado e 'Evidência' é uma lista com uma única opção, 'Foto do lacre anexada': marca-se que há foto sem tirar a foto.
- Proposta: Ler o código do lacre pela câmera ou leitor e tirar a foto no próprio campo Evidência; 'Aplicado por' vem do perfil e 'Conferido por' sugere quem está na portaria.
- Método: Captura (código de barras, foto)
- Ganho: 1 texto digitado → 0; evidência real anexada
- Evidência: v3/LO-02det.dc.html GRIDS g_ck edit 'Registrar lacre' (Evidência: sel com opção única 'Foto do lacre anexada'); v3out/LO-02det.json results[0]
- Cuidado: Quem confere não pode ser quem aplicou (regra da tela).

### POS-23 · Média · VE-04 · Necessidade essencial
- Módulo: Vendas (legado)
- Nível: Linha da tabela
- Elemento: 'Confirmar pedido' em PV-032 e PV-033 (disputa de 1,8 t de classe B)
- Persona: comercial
- Hoje: Os dois pedidos disputam 1,8 t de classe B e cada linha tem 'Confirmar pedido'; quem confirmar primeiro leva o saldo e o outro vira conflito. O líquido por kg (R$ 2,10 FOB × R$ 1,99 CIF) só aparece em outra tela (VE-03).
- Proposta: Na disputa, mostrar na linha o líquido por kg e o prazo, ordenar pelo melhor líquido e oferecer no ⋯ 'Confirmar PV-032 e propor S41 ao PV-033' (contraproposta com a alternativa de 1,2 t na semana 05/10).
- Método: Calculado
- Ganho: Decisão sem trocar de tela; o pedido perdedor recebe alternativa em vez de conflito
- Evidência: v3/VE-04.dc.html l.5408-5415 (NEED, SALDO_B = 1,8; conflito ao confirmar o segundo); v3/VE-03.dc.html SPEC q35 'Comparar propostas' (R$ 2,10 × R$ 1,99)
- Cuidado: Confirmação atômica e idempotente (ATP-05); aceite do cliente por versão.

### POS-24 · Média · CO-06det · Erro ou risco
- Módulo: Colheita e pós-colheita (legado)
- Nível: Detalhe
- Elemento: 'Liberar para destinação compatível' (primária) e 'Manter bloqueio'
- Persona: classificador
- Hoje: Um clique libera o lote bloqueado L27-013 'para blend/mercado interno tipo 7' (destino escolhido pelo sistema), sem motivo, laudo nem classe confirmada. O verde é a liberação, num lote com defeitos 103 contra padrão ≤ 86.
- Proposta: Decisão num formulário: destinação (só as compatíveis), classe atingida, laudo e motivo. Com resultado não conforme, nenhuma opção vem verde por padrão.
- Método: Outro
- Ganho: Liberação com motivo e destino escolhidos por quem decide
- Evidência: v3/CO-06det.dc.html SPEC q28 ('Liberado para blend/mercado interno tipo 7 … Recibo QL-1148'); GRIDS g_am (defeitos medido 103, padrão ≤ 86)
- Cuidado: Decisão de qualidade rastreável; não reabre a ordem encerrada.

### POS-25 · Média · PT-04det, PT-07 · Modal e botões
- Módulo: Portal do parceiro
- Nível: Detalhe
- Elemento: 'Recusar crédito' (PT-04det) e 'Revogar acesso' (PT-07)
- Persona: banco parceiro, administradora do fornecedor
- Hoje: 'Recusar crédito' grava a recusa num clique ('Recusa registrada com motivo') sem pedir motivo e corta o acesso aos blocos do dossiê. 'Revogar acesso' encerra sessões na hora, direto da linha.
- Proposta: Recusar crédito abre confirmação com motivo obrigatório (lista + texto) e a consequência escrita. Revogar acesso vai para o fim do ⋯, com confirmação que nomeia a pessoa.
- Método: Outro
- Ganho: Ação irreversível só com motivo e confirmação
- Evidência: v3/PT-04det.dc.html SPEC q63 (mensagem imediata de 'Recusar crédito'); v3/PT-07.dc.html SPEC q67 ('Revogar acesso' imediato)
- Cuidado: Auditoria antes e depois (P46); histórico de acesso preservado.

### POS-26 · Média · VE-06 · Entrada mais rápida
- Módulo: Vendas (legado)
- Nível: Modal
- Elemento: 'Abrir caso' / 'Novo caso'
- Persona: comercial
- Hoje: 6 campos, 4 digitados: Pedido · entrega (texto), Lote (texto), Quantidade (texto com a unidade escrita, sem teclado numérico) e Evidências (texto). O caso não nasce da entrega.
- Proposta: Abrir o caso a partir da carga ou viagem: pedido, entrega, lote e cliente herdados; quantidade com teclado numérico e unidade da venda; evidência por foto ou anexo. Sobram 1 número e 1 escolha (motivo).
- Método: Pré-preenchido pelo contexto
- Ganho: 4 → 1 campo digitado
- Evidência: v3/VE-06.dc.html GRIDS g_rc edit 'Novo caso'; v3out/VE-06.json results[0]; robot3/summ.txt VE-06 ('4 dig … sem teclado 1, sem unidade 1')
- Cuidado: Item devolvido entra bloqueado até a Qualidade decidir.

### GES-12 · Média · IC · Resolver em 1 clique
- Módulo: Inteligência de compras
- Nível: Detalhe
- Elemento: Painel do insumo com recomendação 'Comprar agora' · primária 'Abrir Compra de insumos'
- Persona: comprador, gestor
- Hoje: O painel calcula o que fazer, até quando pedir, a quantidade da safra e a necessidade. A primária só abre a tela Compra de insumos (CMP), sem levar insumo, quantidade nem data.
- Proposta: Primária 'Criar rascunho de cotação · <insumo> · <qtd> · pedir até <data>', já com fornecedores homologados do grupo. A compra continua com o comprador.
- Método: Pré-preenchido pelo contexto
- Ganho: Abrir CMP e redigitar insumo, quantidade e data → 1 clique com rascunho pronto.
- Evidência: v3/IC.dc.html icPan: prim {t:'Abrir Compra de insumos', h:'CMP.dc.html'} nos painéis g_icm e g_ici. 'Pedir cotação' e 'rascunho de pedido': 0 ocorrências.
- Cuidado: A automação gera só rascunho e não envia cotação sozinha (P34/P62).

### GES-13 · Média · GE-08 · Modal e botões
- Módulo: Crédito
- Nível: Tela
- Elemento: Cabeçalho 'CRE-0102 · condição documental pendente' + link 'Solicitar proposta a credores'; ⋯ 'Registrar liberação da 2ª parcela'; painel 'Anexar documento condicionante'
- Persona: gestor de crédito, proprietário
- Hoje: O estado do topo pede um documento, mas a ação do topo é outra ('Solicitar proposta a credores' → PT-04). No ⋯ do acompanhamento aparece 'Registrar liberação da 2ª parcela', que sempre responde 'Bloqueado'. O painel de anexar tem 4 campos de texto: Solicitação, Documento, Validade '90 dias' e Arquivo, onde o nome 'matricula_1874.pdf' é digitado.
- Proposta: Primária do topo: 'Anexar certidão do CRE-0102'. 'Registrar liberação' fica desabilitada com o motivo até o credor aceitar. No painel, escolher o arquivo (ou foto) ou um documento já cadastrado em 'Documentos para crédito'. Solicitação e documento vêm do contexto; a validade vira data.
- Método: Pré-preenchido pelo contexto
- Ganho: Próximo passo certo no topo. 4 campos de texto → 1 escolha de arquivo. Nenhum botão que só recusa.
- Evidência: v3out/GE-08.json inv.links ('Solicitar proposta a credores' → PT-04) e results[2] (menu). v3/GE-08.dc.html EXTRAVALS v.lib2 (sempre 'Bloqueado') e o painel d47 em texto (inputs text).
- Cuidado: Liberação só com o aceite do credor. Cada liberação é um fato financeiro próprio.

### GES-14 · Média · GE-08 · Necessidade essencial
- Módulo: Crédito
- Nível: Listagem
- Elemento: Botão 'Comparar propostas' (Solicitações e contratos)
- Persona: gestor de crédito, proprietário
- Hoje: O clique só mostra um aviso: 'Banco Terra 14,2% a.a. vs. Coop Crédito 13,8% a.a. + tarifa'. Não há quadro lado a lado (CET, valor presente, garantia, prazo) nem ação para escolher a proposta.
- Proposta: Abrir a comparação lado a lado com CET, custo total em R$, garantia exigida e % da soja comprometida, além de 'Escolher proposta <credor>', que registra a decisão com motivo e leva ao próximo passo.
- Método: Outro
- Ganho: A decisão sai da tela de crédito, sem anotar números de um aviso.
- Evidência: v3/GE-08.dc.html SPEC q48 (msg única para 'Comparar propostas'). v3out/GE-08.json results[0] (effect).
- Cuidado: Garantias comprometidas (hoje 43% da soja V2) precisam aparecer antes de escolher.

### GES-15 · Média · GE-08 · Clareza
- Módulo: Gestão e finanças
- Nível: Modal
- Elemento: Texto do registro em consulta: 'Consulta: você não tem permissão para editar este registro.'
- Persona: todos (controller, gestor de crédito, financeiro)
- Hoje: Registros travados pelo estado (CRE-0102 aprovado, lançamento definitivo, caso encerrado, título conciliado) abrem dizendo que falta permissão, até no perfil Proprietário com todos os papéis. O motivo real (estado) está escrito no subtítulo do formulário, mas não aparece.
- Proposta: Quando o travamento vem do estado, mostrar o motivo do estado e o caminho: 'Aprovada pelo credor: abre em consulta. Para mudar, ...'. 'Sem permissão' só quando faltar papel ou alçada, dizendo quem pode.
- Método: Outro
- Ganho: O usuário entende por que não pode e o que fazer, sem chamar o administrador à toa.
- Evidência: v3out/GE-08.json results[4] (texto 'Consulta: você não tem permissão...'). Motor em v3/GE-08.dc.html: r.ro → 'Consulta: você não tem permissão para editar este registro.'
- Cuidado: Não liberar edição de registro travado.

### GES-16 · Média · GE-04 · Lote
- Módulo: Gestão e finanças
- Nível: Lote
- Elemento: Tabelas do grupo GES sem seleção de linhas
- Persona: financeiro, quem implanta, administrador do sistema
- Hoje: Nenhuma tabela das telas GE, CD, CF e ON tem seleção. Programar pagamento (GE-04), registrar cobrança (GE-05), inativar ou trocar a equipe de safristas (CD-04), definir sistema ou setor de vários talhões (CD-01), validar premissas de rendimento (CD-08) e mapear conta ERP de vários códigos (CD-07) são feitos linha a linha.
- Proposta: Ligar a seleção nessas tabelas com ações de lote que mostram prévia e resultado parcial: 'Programar pagamento' (data e conta), 'Incluir na remessa', 'Mudar equipe', 'Inativar', 'Definir sistema/setor', 'Mapear conta'.
- Método: Lote por seleção
- Ganho: N formulários → 1 ação de lote. Ex.: 10 safristas = 10 → 1.
- Evidência: 'sel': false em todos os GRIDS de v3/GE-0*.dc.html, CD-0*.dc.html, CF-0*.dc.html e ON-01*.dc.html. summ.txt seção LOTES (só CMP).
- Cuidado: Nada de lote em aprovação agronômica (decisão fixa). Aprovar pagamento em lote também fica fora: só a programação e a remessa.

### GES-17 · Média · GE-05 · Entrada mais rápida
- Módulo: Gestão e finanças
- Nível: Modal
- Elemento: 'Registrar cobrança autorizada' (painel da seção) × formulário do título (clique na linha)
- Persona: financeiro, comercial
- Hoje: Há dois formulários para a mesma tarefa. O painel da seção pede Cliente (lista), Título (texto 'FAT-2090 · PV-029'), Canal (telefone + e-mail, WhatsApp, E-mail, Push no app) e Acordo, sem data. O do título pede Próxima cobrança (data), Canal autorizado (Telefone, E-mail, WhatsApp, Portal do cliente) e Registro. Os canais não são os mesmos nem vêm dos canais autorizados do parceiro (CD-05).
- Proposta: Um formulário só, aberto pelo ⋯ da linha 'Registrar cobrança', com cliente e título já preenchidos e o canal limitado aos autorizados no cadastro. Data com chips (+3, +7 dias).
- Método: Pré-preenchido pelo contexto
- Ganho: 4 campos (2 digitados) → 2 escolhas e 1 texto opcional. Vocabulário de canal único.
- Evidência: v3/GE-05.dc.html: painel d43 (inputs Cliente, Título, Canal, Acordo) e GRIDS g_rec.edit.fields (cob date, canal opts). v3/CD-05.dc.html: campo canais 'Canais autorizados'.
- Cuidado: A cobrança é só registro e não altera o título. Nenhuma mensagem real é enviada.

### GES-18 · Média · GE-02det · Necessidade essencial
- Módulo: Gestão e finanças
- Nível: Detalhe
- Elemento: GE-02det 'Comparar · V1 × V2 × real' e GE-06det 'Detalhar · custo de pulverização'
- Persona: controller, gestor, agrônomo
- Hoje: Duas telas de detalhe tratam o mesmo desvio (OS-0409, +R$ 1.808) com a mesma decomposição (+R$ 800 área, +R$ 480 consumo, +R$ 528 preço) e títulos diferentes. Uma aponta para a outra ('Abrir documentos de origem'). A decisão (propor parâmetro) fica só na GE-02det; as hipóteses a validar ficam só na GE-06det.
- Proposta: Um detalhe só do desvio, com ponte de variações, hipóteses, documentos de origem e decisão (propor parâmetro ou criar ação). Entra pela GE-02 e pela GE-06 com o mesmo título.
- Método: Outro
- Ganho: 2 telas → 1. O contexto e a decisão ficam no mesmo lugar.
- Evidência: v3/GE-02det.dc.html (ponte '+ VOLUME +R$ 800 · + CONSUMO +R$ 480 · + PREÇO +R$ 528'). v3/GE-06det.dc.html GRIDS g_cau (ef +R$ 800, +R$ 480, +R$ 528). Link 'Abrir documentos de origem' → GE-06det.
- Cuidado: A base V1 fica inalterada.

### GES-19 · Média · GE-02det · Erro ou risco
- Módulo: Gestão e finanças
- Nível: Campo
- Elemento: Painel 'Proposta de parâmetro': Plano, Consumo (L/ha), Vigência, Justificativa
- Persona: controller, agrônomo
- Hoje: 'Consumo (L/ha)' é texto e já vem com '2,2 (antes 2,0)', ou seja, a dose real medida vira o novo parâmetro sem escolha. A Vigência é texto ('a partir da próxima aplicação'). O Plano vem como 'Fungicida · Feijão', nome que não existe nos Planos agronômicos (lá é 'Feijão pivô').
- Proposta: Campo numérico em L/ha, vazio, com o real (2,2) e o atual (2,0) como referência em chips que é preciso tocar. Vigência como escolha (próxima aplicação, próxima safra). O plano vem da O.S. de origem, com o nome da biblioteca.
- Método: Teclado numérico com unidade
- Ganho: A dose passa a ser uma escolha explícita. Nenhum texto livre em campo numérico.
- Evidência: v3/GE-02det.dc.html: inputs 'Consumo (L/ha)' value '2,2 (antes 2,0)' e 'Vigência' text; select 'Plano' com 1ª opção 'Fungicida · Feijão'.
- Cuidado: Decisão fixa: dose nunca vem pré-preenchida com o último valor. A revisão agronômica continua decidindo.

### GES-20 · Média · GE-06 · Necessidade essencial
- Módulo: Gestão e finanças
- Nível: Linha da tabela
- Elemento: Coluna 'Ação' de 'Painéis por processo': 'Ver ordens', 'Ver packing', 'Ver irrigação', 'Ver ações'
- Persona: gestor, PCM, PCP
- Hoje: O detalhamento abre a lista geral (CA-01, CO-05, IR-03, GE-07) sem filtro. A aderência de 86% não mostra quais O.S. saíram do dia previsto. 'Ritmo de plantio em risco', cuja causa é 'OS-0420 impedida · OM-0233', oferece 'Ver ações' em vez de levar à OM-0233.
- Proposta: Cada indicador abre o recorte que forma o número (ex.: as 14% de O.S. fora do dia, filtradas). A causa com ID leva ao registro que resolve ('Abrir OM-0233 · PCM'). Indicador parcial mostra o que falta.
- Método: Resolver em 1 clique
- Ganho: Lista geral + filtro manual → 1 clique até os registros do desvio.
- Evidência: v3out/GE-06.json inv.links ('Ver ordens' → CA-01.dc.html, 'Ver packing' → CO-05.dc.html, 'Ver irrigação' → IR-03.dc.html, 'Ver ações' → GE-07.dc.html, todos sem filtro). GRIDS g_ind linha Ritmo (causa 'OS-0420 impedida · OM-0233').

### GES-21 · Média · GE-01 · Necessidade essencial
- Módulo: Gestão e finanças
- Nível: Tela
- Elemento: Cartões 'Receita prevista', 'Margem projetada', 'Roic consolidado', 'Qualidade dos dados 96%' e cabeçalho sem primária
- Persona: proprietário e gestor
- Hoje: Os 4 números são texto, sem clique. A 'Qualidade dos dados 96%' não mostra os 4% que faltam nem quem resolve. O cabeçalho não tem ação principal, só o link 'Abrir composição do resultado'.
- Proposta: Cada cartão abre a composição (receita e margem por cultura, ROIC com e sem terra). 'Qualidade dos dados' abre a lista do que está provisório ou faltando, com o dono de cada item. A primária do topo é a causa nº 1 ('Resolver: plantio T4 impedido').
- Método: Outro
- Ganho: Indicador vira decisão com detalhamento em 1 clique.
- Evidência: Marcação de v3/GE-01.dc.html: os cartões são <div> sem href ou onClick. v3out/GE-01.json inv.primary [] e inv.links.
- Cuidado: Não somar razões (custo/ha). Mostrar o parcial quando faltar dado (P45/P60).

### GES-22 · Média · GE-06det · Resolver em 1 clique
- Módulo: Gestão e finanças
- Nível: Linha da tabela
- Elemento: Coluna 'Hipótese a validar': 'calda ajustada pelo agrônomo — validar', 'compra fora do contrato? — conferir pedido', 'reaplicação de 25 ha após chuva — checar'
- Persona: controller, agrônomo, comprador
- Hoje: Cada hipótese diz quem precisa validar, mas não tem ação. É preciso ir à GE-07, criar um caso e digitar a hipótese de novo.
- Proposta: ⋯ por hipótese: 'Pedir validação ao agrônomo', 'Conferir pedido com o comprador' e 'Checar apontamentos da OS-0409'. Cada uma cria o caso já com a hipótese, a evidência e o dono certo, ou comenta no caso que já existe.
- Método: Resolver em 1 clique
- Ganho: Troca de tela + 7 campos → 1 clique com o contexto junto.
- Evidência: v3/GE-06det.dc.html GRIDS g_cau (chip de hipótese, sem 'act'). Edit 'origin' em leitura.

### GES-23 · Média · CD · Necessidade essencial
- Módulo: Cadastros
- Nível: Menu
- Elemento: Hubs Cadastros (CD), Configurações (MOD-CFG) e Crédito (MOD-CRE)
- Persona: quem implanta, administrador do sistema, gestor de crédito
- Hoje: Os hubs são listas de links sem estado. Cada tela de cadastro já calcula as próprias pendências ('1 máquina bloqueada', 'N premissas a validar', 'traduções pendentes', 'não alocáveis'), mas o hub não mostra nenhuma. O MOD-CRE tem 4 links que abrem a mesma GE-08 com outra visão.
- Proposta: Mostrar em cada link do hub o estado e a contagem de pendências ('Pessoas e equipes · 2 habilitações vencem em 30 dias'). O MOD-CRE pode sair: o link do menu vai direto à GE-08.
- Método: Outro
- Ganho: O que precisa de atenção fica à vista no 1º clique, e cai um nível intermediário no Crédito.
- Evidência: v3/CD.dc.html, v3/MOD-CFG.dc.html e v3/MOD-CRE.dc.html: só links. Estados: c3e (CD-03), c4e (CD-04), c7e (CD-07) e c8e (CD-08) em cada EXTRAVALS. Links MOD-CRE → GE-08.dc.html#vis=...
- Cuidado: A barra continua com 9 nomes.

### GES-24 · Média · CD-01 · Clareza
- Módulo: Cadastros
- Nível: Linha da tabela
- Elemento: Clique na linha do talhão
- Persona: quem implanta, agrônomo
- Hoje: Clicar no talhão abre o formulário de edição. O detalhe (parcelas por safra, polígono, versões) só abre por um botão dentro do formulário ('Abrir talhão ›' ou 'Definir polígono ›'). O mesmo vale para a fazenda ('Incluir talhão' fica dentro do painel).
- Proposta: Clicar na linha abre a CD-01det. O ⋯ da linha traz: próximo passo (Definir polígono, se faltar) → Editar dados → Incluir talhão (na fazenda) → Inativar.
- Método: Menu ⋯
- Ganho: 2 → 1 clique até o detalhe, no padrão listagem → detalhe.
- Evidência: v3/CD-01.dc.html CAD_ACTS.g_tal ('Definir polígono ›' / 'Abrir talhão ›' dentro do formulário) e CAD_ACTS.g_faz ('Incluir talhão').
- Cuidado: Avisar antes de sair com alterações não salvas (já existe).

### GES-25 · Média · ON-01 · Entrada mais rápida
- Módulo: Implantação
- Nível: Modal
- Elemento: Passos 'Desenhar talhão', 'Cultura e ciclo', 'Importar dados' e 'Rever dados da organização'
- Persona: quem implanta (cadastro inicial)
- Hoje: 'Desenhar talhão' pede Cultura, e o passo 3 pede Cultura de novo, com Safra e Plantio. Desenhar T1 e T2 e depois importar o shapefile gera '2 duplicidades' para mesclar ou ignorar. Em 'Rever dados', o campo 'E-mail do responsável' é uma lista que mistura o e-mail com nomes de pessoas (Ana, Marcos, Rui, Paula).
- Proposta: No passo 2, oferecer primeiro 'Importar talhões (KML/shapefile)' e deixar desenhar como alternativa. Tirar Cultura do talhão: ela entra só no passo 3. O e-mail vem do responsável escolhido (campo calculado).
- Método: Calculado
- Ganho: Cultura 2 → 1 vez. Duplicidades evitadas em vez de resolvidas. 1 campo a menos e nenhum erro de e-mail.
- Evidência: Marcação de v3/ON-01.dc.html: painéis d50 (Fazenda, Nome do talhão, Cultura), d52 (Cultura, Safra, Plantio previsto) e d49 (select 'E-mail do responsável' com opções 'otavio@...', 'Ana', 'Marcos', 'Rui', 'Paula'). v3/ON-01det.dc.html g_imp linha 'Duplicidades'.
- Cuidado: 'Nada é presumido': CAR e polígono continuam pendentes até serem informados.

### GES-26 · Média · ON-01 · Erro ou risco
- Módulo: Implantação
- Nível: Modal
- Elemento: Painel 'Convidar pessoa' (E-mail, Papel, Fazenda)
- Persona: quem implanta, administrador do sistema
- Hoje: O onboarding convida por e-mail com 4 papéis (Operador, Agrônomo, Gestor, Consulta). Na CF-01 os papéis são outros (gestora, agrônoma, PCP, almoxarife, conferência, mecânica, qualidade, direção, ...), e o convite parte de uma pessoa já cadastrada na CD-04. Agrônomo pode ser convidado sem CREA.
- Proposta: Usar a mesma lista de papéis e a mesma regra da CF-01: escolher ou criar a pessoa (nome e equipe) e dar o papel. Agrônomo só com CREA válido, pedido no próprio convite.
- Método: Lista ou busca com autocompletar
- Ganho: Um vocabulário de papéis e uma regra de permissão desde o 1º dia.
- Evidência: Marcação de v3/ON-01.dc.html, painel d53: select Papel {Operador, Agrônomo, Gestor, Consulta}. v3/CF-01.dc.html G2_PAPEIS, a regra 'semCrea' e o texto 'Pessoa nova se cadastra no CD-04'.
- Cuidado: Trava legal de CREA para o papel agronômico (P43/P46).

### GES-27 · Média · GE-03 · Modal e botões
- Módulo: Gestão e finanças
- Nível: Modal
- Elemento: Painéis 'Reabertura de período fechado' (GE-03) e 'Reabrir caso encerrado' (GE-07): Motivo, Efeito, Aprovador
- Persona: controller
- Hoje: A lista de motivos da reabertura contábil mistura 1 motivo do caso com motivos de campo ('Sonda deslocada', 'Chuva', 'Quebra', 'Praga acima do NC'). A GE-07 usa a mesma lista. 'Aprovador' e 'Efeito' são textos já preenchidos ('Controladoria'; 'estorno + relançamento...').
- Proposta: Motivos próprios do contexto (classificação errada, documento atrasado, ajuste de rateio, outro com texto). Aprovador calculado pela alçada, só leitura com o nome. Efeito em texto fixo, sem campo.
- Método: Calculado
- Ganho: 2 campos de texto a menos e motivo útil para a auditoria.
- Evidência: Marcação de v3/GE-03.dc.html: painel d41 (select 'Motivo · lista do cadastro' com opções de campo; inputs Efeito e Aprovador). Painel d45 em v3/GE-07.dc.html com a mesma lista.
- Cuidado: Reabrir continua exigindo motivo e aprovação. Correção por estorno e relançamento.

### GES-28 · Média · ON-01 · Entrada mais rápida
- Módulo: Implantação
- Nível: Modal
- Elemento: Painel 'Anexar CAR' (Arquivo do CAR, Número do recibo do CAR)
- Persona: quem implanta (cadastro inicial)
- Hoje: O arquivo e o número do recibo do CAR são campos de texto digitados. O mesmo CAR é pedido de novo em Crédito › Documentos (GE-08 'CAR · Pendente · Boa Vista'). A aba Ambiental da CD-01 lê o CAR do KML.
- Proposta: Escolher o arquivo do CAR (PDF do recibo ou KML) e ler dele o número do recibo e as áreas (reserva, APP). Gravar uma vez só, no documento da fazenda que a GE-08 e a CD-01 consultam.
- Método: Captura (QR, código de barras, XML de NF-e, balança, telemetria, GPS, foto, voz)
- Ganho: 2 campos digitados → 1 arquivo. CAR informado 1 vez, não 2.
- Evidência: Marcação de v3/ON-01.dc.html: painel d51 (inputs text 'Arquivo do CAR' e 'Número do recibo do CAR'). v3out/GE-08.json inv.tables[2] (CAR Pendente Boa Vista). v3/CD-01.dc.html g_amb (recibo do CAR vindo do KML).
- Cuidado: O documento fica pendente e visível até ser anexado.

### GES-29 · Média · CD-03 · Entrada mais rápida
- Módulo: Cadastros
- Nível: Campo
- Elemento: 'Custo R$/h da máquina' + 'Fonte do custo' no cadastro de máquina; criar máquina parecida
- Persona: quem implanta, PCM
- Hoje: O custo/h é digitado (Trator T1: R$ 180/h, 'Apurado na fazenda'), mas a GE-06 já mostra o realizado (Trator T1 R$ 158/h). Para cadastrar uma frota (Trator 03 e 04, mesmo modelo), não há 'Duplicar': são 11 campos por máquina.
- Proposta: Mostrar o realizado ao lado do campo com 'Usar realizado (R$ 158/h)', que grava com a fonte 'Apurado' e a data. No ⋯ da máquina, 'Duplicar' copia classe, modelo, capacidade e custo; a pessoa muda só o nome.
- Método: Modelo ou duplicar
- Ganho: 11 → 1 campo por máquina repetida. Custo com origem e menos premissa velha.
- Evidência: v3out/CD-03.json results[0] (11 campos). v3/CD-03.dc.html g_atv (custo_h 180). v3out/GE-06.json inv.tables[1] (Trator T1 R$ 158/h). 'Duplicar': 0 em v3/CD-0*.dc.html.
- Cuidado: A troca do padrão de custo vale para novos planejamentos; O.S. já emitidas não mudam.

### GES-30 · Média · CD-04 · Entrada mais rápida
- Módulo: Cadastros
- Nível: Modal
- Elemento: Formulário 'Cadastrar pessoa' (22 campos)
- Persona: quem implanta, gestor
- Hoje: Todos os 22 campos ficam visíveis: Nome, Equipe, 15 caixas de habilidade, Vínculo, Admissão, Disponível até, Custo-hora e Situação. As datas não têm atalho. A contratação de safristas é feita uma pessoa por vez.
- Proposta: Mostrar 4 campos (Nome, Equipe, Habilidades em chips já marcadas conforme a equipe, Vínculo) e deixar o resto em 'Mais opções'. Para safristas, 'Cadastrar várias' (colar nomes) com equipe, vínculo 'Safrista' e 'Disponível até' em comum.
- Método: Grade editável ou colar de planilha
- Ganho: 22 → 4 campos visíveis. 10 safristas: 10 formulários → 1 lista.
- Evidência: v3out/CD-04.json results[0] (22 campos; Admissão e Disponível até sem atalho). summ.txt l.129.
- Cuidado: A habilitação legal exigida (NR, CREA) continua aparecendo quando a habilidade é marcada. Cadastrar não cria login.

### GES-31 · Média · CD-08 · Resolver em 1 clique
- Módulo: Cadastros
- Nível: Listagem
- Elemento: Botão 'Comparar com o realizado'
- Persona: PCP, gestor
- Hoje: O botão só mostra um aviso: 'Pulverização: padrão 21,6 ha/h × realizado 19,8 ha/h (OS-0421, 4 dias) · revisão sugerida, nada alterado.' Não há como aplicar a revisão nem ver as outras operações.
- Proposta: Coluna 'Realizado' em cada rendimento (com as O.S. de origem) e, no ⋯ da linha, 'Usar realizado como novo padrão'. Isso cria uma nova vigência com a fonte 'Medição local' e mantém a anterior no histórico.
- Método: Resolver em 1 clique
- Ganho: Aviso sem ação → 1 clique para atualizar o padrão.
- Evidência: v3/CD-08.dc.html SIMS.cmp (aviso) e botão onClick sim_cmp. GRIDS g_rend.edit.fields 'fonte' e 'vig'.
- Cuidado: Novos planejamentos usam o novo padrão; os já emitidos não mudam.

### GES-32 · Média · GE-02 · Modal e botões
- Módulo: Gestão e finanças
- Nível: Menu
- Elemento: ⋯ de 'Publicação' ('Publicar previsão V2', 'Autorizar versão') e link do topo 'Comparar base × previsão × real'
- Persona: controller, proprietário
- Hoje: 'Autorizar versão' é oferecido e sempre responde 'Bloqueado · só a alçada Direção autoriza'. 'Publicar previsão V2' aparece com a V2 já 'Publicada ao planejamento'. O link do topo promete comparar a versão inteira, mas abre um caso só (fungicida no feijão P1, OS-0409). O 'Cronograma de caixa' não leva aos títulos do trimestre.
- Proposta: Desabilitar 'Autorizar versão' com o motivo e o nome de quem autoriza, ou levar ao item nas Aprovações. 'Publicar' aparece só quando há recálculo pendente. Renomear o link para 'Ver maior desvio (OS-0409)' ou abrir a comparação da versão inteira. Trimestre abre os títulos (GE-04) daquele período.
- Método: Outro
- Ganho: Nenhum botão que só recusa. O destino do link fica claro.
- Evidência: v3/GE-02.dc.html SPEC q39 msgs[3] ('Bloqueado · só a alçada Direção...') e g_ver linha V2 'Publicada ao planejamento'. Link 'Comparar base × previsão × real' → GE-02det (OS-0409). g_cx edit 'origin' sem link.
- Cuidado: Autorizar continua sendo da alçada Direção.

### GES-33 · Média · GE-04 · Modal e botões
- Módulo: Gestão e finanças
- Nível: Modal
- Elemento: 'Importar retorno do banco' (seção) e 'Importar retorno' (linha Ipiranga)
- Persona: financeiro
- Hoje: Dois botões fazem a mesma coisa. O retorno é aplicado direto, sem escolher o arquivo e sem prévia: a NF 5531 é liquidada e conciliada, e uma divergência de R$ 12,40 fica aberta e só aparece no aviso.
- Proposta: Um botão só, 'Importar retorno do banco', com prévia: títulos liquidados, recusados e divergências, com o valor de cada um. A divergência vira item na linha com '⋯ Tratar divergência'.
- Método: Outro
- Ganho: Importação com prévia (P22). Divergência com ação, não só no aviso.
- Evidência: v3out/GE-04.json cands ('Importar retorno do banco', 'Importar retorno'). v3/GE-04.dc.html EXTRAVALS v.retorno (aplica e avisa '1 divergência de R$ 12,40').
- Cuidado: Idempotência: o 2º retorno não liquida de novo (já existe).

### GES-34 · Média · IN-04 · Lote
- Módulo: Mapa
- Nível: Lote
- Elemento: 'Selecionar área' com vários talhões (painel da seleção)
- Persona: proprietário e gestor, agrônomo, PCP
- Hoje: Com vários talhões selecionados, o painel mostra a área somada, 'Ordens na área', 'Programar vistoria nas áreas' e 'Limpar seleção'. Não há como planejar uma operação ou criar O.S. para os talhões escolhidos.
- Proposta: No painel da seleção, 'Planejar operação nos N talhões': abre o planejamento com uma O.S. por talhão em rascunho, com a área de cada um já preenchida.
- Método: Lote por seleção
- Ganho: Mesma operação em 8 talhões: 8 fluxos → 1 (meta P61: 4 toques).
- Evidência: mapa-analise.md l.108 (conteúdo de panelArea). v3/IN-04.dc.html r_vis/criarVis (só vistoria em lote).
- Cuidado: Cada O.S. continua com a própria aprovação agronômica individual (decisão fixa: sem aprovação em lote).

### AGRO-33 · Baixa · PL-05 · Entrada mais rápida
- Módulo: Planejamento
- Nível: Campo
- Elemento: Campo 'Prazo' no modal 'Impedimento'
- Persona: planejador (PCP)
- Hoje: Prazo é uma lista 'vence hoje / até 3 dias / no prazo': rótulo relativo que envelhece no dia seguinte; a linha já mostra datas ('no prazo · 02/10').
- Proposta: Data com atalhos Hoje, Amanhã, +3 dias; 'vence hoje' ou 'atrasado' passa a ser calculado.
- Método: Atalho de data
- Ganho: prazo certo amanhã sem reeditar
- Evidência: v3/PL-05.dc.html GRIDS g_imp edit fields prazo t 'sel' opts ['vence hoje','até 3 dias','no prazo']

### AGRO-34 · Baixa · AG-01 · Clareza
- Módulo: Agronomia
- Nível: Campo
- Elemento: Campos 'Área em hectares' e 'Data da aplicação' na decisão 'Erradicar plantas'
- Persona: agrônomo e RT
- Hoje: Na erradicação de virose a área vem fixa em 1 ha, sem 'ha' ao lado e sem origem; o resultado está em pontos com sintoma (1 de 20). A data se chama 'Data da aplicação', mas não há aplicação.
- Proposta: Sugerir a área pelos pontos com sintoma × área por ponto (62,1 ha ÷ 20 pontos ≈ 3,1 ha por ponto), mostrando a conta, com 'ha' ao lado; rótulo 'Data da erradicação'.
- Método: Calculado
- Ganho: valor com origem; O.S. de tratos com área coerente
- Evidência: v3/AG-01.dc.html agDecIni area=…(kind==='erradicar'?1:…); v3out/AG-01.json 'Confirmar foco' campos 'Área em hectares' v '1' sem unidade e 'Data da aplicação'
- Cuidado: Área maior que o talhão segue travada.

### AGRO-35 · Baixa · PL-02det · Clareza
- Módulo: Planejamento
- Nível: Modal
- Elemento: Mensagem 'Consulta: você não tem permissão para editar este registro' (Ajuste local, Medição AGS-004, Item da biblioteca)
- Persona: agrônomo e RT
- Hoje: Com o perfil Proprietário (todos os papéis), os modais dizem que falta permissão. O motivo real é o estado: atividade 'Realizada 05/09 · preservada', item publicado, medição gravada.
- Proposta: Dizer o motivo e o caminho: 'Realizada em 05/09: não muda; para corrigir, estorne', 'Versão publicada: crie nova versão', 'Medição gravada: registre nova medição'.
- Método: Outro
- Ganho: a pessoa sabe o próximo passo sem pedir permissão a ninguém
- Evidência: v3out/PL-02det.json, v3out/AG-02.json (AGS-004) e v3out/AG-05.json textos 'Consulta: você não tem permissão…'; v3/PL-02det.dc.html linha 738: a mensagem sai sempre que a linha é só leitura (r.ro)
- Cuidado: Permissão por papel continua (P46).

### AGRO-36 · Baixa · PL-01 · Entrada mais rápida
- Módulo: Planejamento
- Nível: Campo
- Elemento: 'Plantio previsto' e 'Meta de produtividade (hipótese)' (PL-01 Cultivo); 'Data da vistoria' (AG-01); 'Próxima calibração' (IR-04)
- Persona: planejador (PCP)
- Hoje: Datas sem atalho (Hoje, Amanhã, +7). A meta é texto com a unidade digitada ('64 sc/ha'), sem teclado numérico; no SAF a mesma meta é número + unidade.
- Proposta: Atalhos de data ao lado do campo; meta como número com a unidade fixa pela cultura (sc/ha; t/ha/ano no mamão).
- Método: Atalho de data
- Ganho: datas em 1 toque; meta sem erro de unidade
- Evidência: robot3/summ.txt FORMULÁRIOS: AG-01 Programar vistoria (datas sem atalho 1), PL-01 Cultivo (Meta text '64 sc/ha'; datas sem atalho 1), IR-04 Cadastrar sensor (datas sem atalho 1); dumps/SAF.txt g_cult meta numérica + unm

### AGRO-37 · Baixa · IR-04 · Erro ou risco
- Módulo: Irrigação
- Nível: Campo
- Elemento: Campo 'Cobertura' no modal '+ Cadastrar sensor'
- Persona: técnico de irrigação
- Hoje: Com o filtro em Lagoa Grande (23 setores), a lista traz só 'Pivô 1, Pivô 2, Gotejo T7, Fazenda', sem dizer de qual fazenda; há pivôs com o mesmo nome nas duas fazendas.
- Proposta: Lista dos setores da fazenda do filtro, com a fazenda no rótulo ('Pivô 10 · Lagoa Grande'); pré-selecionar o setor de onde se abriu.
- Método: Pré-preenchido pelo contexto
- Ganho: sensor no setor certo; sem homônimo
- Evidência: v3out/IR-04.json results '+ Cadastrar sensor' Cobertura nOpt 4 (texto 'Pivô 1 Pivô 2 Gotejo T7 Fazenda'); filtro 'Lagoa Grande'
- Cuidado: O estado do sensor vem das leituras validadas.

### OS-33 · Baixa · CA-03 · Ações no ⋯
- Módulo: Campo
- Nível: Linha da tabela
- Elemento: Tabela de ocorrências, coluna "Próxima ação"
- Persona: programador e PCP, gestor
- Hoje: As ações são links na coluna (Abrir ocorrência ›, Encaminhar à agronomia ›, Reprogramar saldo ›, Ver tratamento ›); clicar na linha abre edição.
- Proposta: Linha abre o detalhe; destino e próximo passo em texto; ⋯: [próximo passo] → Encaminhar → Encerrar tratamento.
- Método: Menu ⋯
- Ganho: Padrão único com as demais tabelas.
- Evidência: CA-03.dc.html:58 (links em p.prox); v3out/CA-03.json

### OS-34 · Baixa · MB-08 · Modal e botões
- Módulo: App de campo
- Nível: Tela
- Elemento: "Ações da volta" da irrigação
- Persona: operador (irrigante)
- Hoje: 5 botões à vista (Pausar, Retomar, Registrar avanço, Finalizar apontamento do turno, Ver próximo setor) além da primária "Confirmar término". Pausar e Retomar aparecem juntos.
- Proposta: Mostrar só Pausar ou Retomar, pelo estado; o resto no ⋯; a primária segue "Confirmar término".
- Método: Menu ⋯
- Ganho: 6 → 2 alvos.
- Evidência: Modelo do MB-08 (bloco "Ações da volta"); v3out/MB-08.inv2.json

### OS-35 · Baixa · MB-10 · Ações no ⋯
- Módulo: App de campo
- Nível: Cartão
- Elemento: Cartão da colheita OS-0505
- Persona: líder de campo, operador
- Hoje: "Apontar área · OS-0505" e "Descartar carga a pesar" ficam à vista no cartão, com a primária "Registrar carga"; o descarte fica ao lado das ações comuns. Horas digitadas no apontamento.
- Proposta: Cartão abre a O.S.; ⋯: Registrar carga → Apontar área → Descartar carga (por último, com motivo). Horas pelo relógio do turno, como proposto no MB-03.
- Método: Menu ⋯
- Ganho: Descarte longe do toque comum; 1 número a menos.
- Evidência: v3out/MB-10.inv2.json; v3out/MB-10.json (Apontar área: hectares e horas digitados)
- Cuidado: Descarte só com motivo; o registro fica.

### OS-36 · Baixa · MB-06 · Entrada mais rápida
- Módulo: App de campo
- Nível: Campo
- Elemento: "GPS fora da tolerância (ponto vai para recoleta)"
- Persona: agrônomo (monitor de pragas)
- Hoje: É uma caixa de marcar manual: quem coleta decide se o GPS está fora.
- Proposta: O app compara a posição do aparelho com o ponto da rota e marca sozinho, mostrando a distância; a pessoa só confirma a recoleta.
- Método: Captura (GPS)
- Ganho: 1 decisão manual → 0.
- Evidência: MB-06.dc.html:26 (checkbox mb_gpsfora) e :2724 (mb_toggps)
- Cuidado: Ponto fora da tolerância não entra na média sem recoleta.

### OS-37 · Baixa · IN-03 · Entrada mais rápida
- Módulo: Início
- Nível: Modal
- Elemento: "Nova tarefa vinculada"
- Persona: gestor, programador e PCP
- Hoje: "Compromisso" é texto livre, embora a ajuda peça para vincular a um registro (ordem, lote, requisição); Data sem atalho; Responsável começa em "Ana".
- Proposta: Compromisso por busca de registro (O.S., REQ, lote) com autocompletar; prazo da origem sugerido; atalhos hoje, amanhã e +7; responsável sugerido pelo dono do registro.
- Método: Lista ou busca com autocompletar
- Ganho: 1 digitação livre → busca; vínculo garantido.
- Evidência: v3out/IN-03.json (dialog "Nova tarefa vinculada"); robot3/summ.txt (IN-03 · datas 1 sem atalho)
- Cuidado: A tarefa não duplica a O.S.

### OS-38 · Baixa · OS-0424-ficha · Entrada mais rápida
- Módulo: Ordem de Serviço
- Nível: Tela
- Elemento: Tabela de cargas com colunas FEITO e HORA em branco
- Persona: caldeiro, operador
- Hoje: A ficha impressa pede FEITO e HORA à mão em 6 linhas; o app (OS-0424-app) já marca carga a carga. O que é escrito no papel precisa ser redigitado depois.
- Proposta: QR na ficha que abre a OS-0424 no app; o papel fica só como reserva sem sinal, e o registro é feito no app quando o sinal volta.
- Método: Captura (QR)
- Ganho: Evita redigitar 6 linhas por O.S.
- Evidência: v3out/OS-0424-ficha.json (tabela CARGA · CALDA · ÁREA · PRODUTOS · FEITO · HORA, sem ações); OS-0424-app.dc.html:5024–5026 ("Carga N preparada")

### SUP-36 · Baixa · SU-02 · Modal e botões
- Módulo: Estoque
- Nível: Modal
- Elemento: Política · Fertilizantes Galpão 2 (Salvar) e Submeter exceção (Alteração)
- Persona: gerente de suprimentos
- Hoje: O modal da política tem 10 campos e primária "Salvar", mas o efeito é "cria uma proposta de nova versão". "Submeter exceção" pede a mudança em texto livre ("mínimo 2 → 4 un durante a colheita"); "Lote/múltiplo de compra" também é texto ("carreta 36 t").
- Proposta: Primária "Propor versão v5". Exceção com parâmetro (lista), valor atual (preenchido) e novo valor numérico com unidade; múltiplo como número + unidade.
- Método: Lista ou busca com autocompletar
- Ganho: 1 texto livre → 1 número; nome do botão igual ao efeito
- Evidência: v3out/SU-02.json results[0] (Alteração * texto) e results[3] (10 campos, BTNS "Salvar", texto "Salvar cria uma proposta de nova versão")
- Cuidado: Versão vigente segue valendo até o gestor aprovar e publicar.

### SUP-37 · Baixa · SU-01 · Erro ou risco
- Módulo: Compras
- Nível: Linha da tabela
- Elemento: Linha "Rolamento 6310" · falta firme
- Persona: comprador, PCM
- Hoje: Demanda 4 un, disponível 0, recebimento firme 0; a tela mostra falta firme 3 un e a conta "4 − 0 − 0 = 3 un".
- Proposta: Corrigir para 4 un, ou mostrar a parcela que explica a diferença (ex.: 1 un já reservada em outra OM).
- Método: Calculado
- Ganho: número confiável para a compra da peça
- Evidência: v3/SU-01.dc.html GRIDS g_nec linha "Rolamento 6310": dem 4, disp 0, firm 0, falta 3, o "Falta firme = 4 − 0 − 0 = 3 un"

### SUP-38 · Baixa · IV · Resolver em 1 clique
- Módulo: Comercial
- Nível: Modal
- Elemento: Detalhe do produto: "Vender agora" (Soja) e "Sem previsão" (Mamão)
- Persona: comercial
- Hoje: IV é a Inteligência de vendas (módulo Comercial). O detalhe da Soja diz "Vender agora" e o do Mamão diz "Publique a previsão (Colheita) ou reveja as vendas" (40.000 kg vendidos sem oferta), mas os dois modais só têm "Fechar".
- Proposta: No detalhe: "Criar oferta de venda · X sc livres" (Soja) e "Publicar previsão de colheita" (Mamão), abrindo a tela com produto e safra preenchidos.
- Método: Resolver em 1 clique
- Ganho: da recomendação à ação: 3 a 4 trocas de tela → 1 clique
- Evidência: v3out/IV.json results[3] (Soja em grão, BTNS só "Fechar") e results[5] (Mamão "Sem previsão", BTNS só "Fechar")
- Cuidado: Venda não ultrapassa o livre para vender.

### POS-27 · Baixa · VE-01, VE-03, VE-04, VE-05, VE-06 · Ações no ⋯
- Módulo: Vendas (legado)
- Nível: Linha da tabela
- Elemento: Tabelas g_bal, g_of, g_cart, g_ob, g_rc
- Persona: comercial
- Hoje: Linhas com links de ID (PV-031, L39-120, RT-0112) e um botão de ação no fim (Detalhar demanda, Criar oferta, Confirmar pedidos, Propor ajuste; Ver reserva, Confirmar no pedido; Confirmar pedido, Resolver alocação, Programar entrega, Ver recebíveis, Tratar devolução, Tratar recusa; Ver crédito, Ver contas a pagar; Autorizar retorno, Cobrar evidências, Receber bloqueado, Decidir destinação). Sem ⋯.
- Proposta: Links de ID ficam; o botão vai ao ⋯ com o próximo passo primeiro (ex.: VE-04: Confirmar pedido | Resolver alocação | Programar entrega, Ver carga, Ver recebíveis; VE-06: Autorizar retorno | Cobrar evidências | Decidir destinação, Encerrar caso).
- Método: Menu ⋯
- Ganho: Padrão único com as demais listas
- Evidência: v3/VE-0x.dc.html GRIDS (partes cta e act por linha); robot3/summ.txt 'AÇÕES NA LINHA' (VE-06 ['Autorizar retorno'] kebab=False)

### POS-28 · Baixa · CARGA, EXPED, VEN · Clareza
- Módulo: Pós-colheita e comercial (telas do menu)
- Nível: Tela
- Elemento: Primária do cabeçalho que muda com a linha selecionada
- Persona: balanceiro, expedição, comercial
- Hoje: No CARGA a primária é 'Registrar pesagem' e vira 'Pesar a CG-xxxx' ao selecionar uma carga; no EXPED, 'Programar carga' vira 'Confirmar saída da RM-xxxx'; no VEN, 'Registrar venda' vira a ação da venda. O mesmo verde aparece também no painel. O BEN já tirou a primária do cabeçalho porque 'repetia o verde do painel'.
- Proposta: Cabeçalho com uma primária fixa por tela (Registrar pesagem, Programar carga, Registrar venda); a ação do item fica no painel e no ⋯ da linha.
- Método: Outro
- Ganho: Botão que não muda de sentido; um verde por contexto
- Evidência: v3/CARGA.dc.html l.5446-5449; v3/EXPED.dc.html l.6010-6014; v3/VEN.dc.html l.6019-6025; v3/BEN.dc.html l.5575 (comentário 'sem primária no cabeçalho')

### POS-29 · Baixa · PT-02det · Modal e botões
- Módulo: Portal do parceiro
- Nível: Detalhe
- Elemento: Primária 'Submeter proposta v2'
- Persona: fornecedor
- Hoje: O cabeçalho diz 'Próxima ação: Responder esclarecimento', mas a primária é 'Submeter proposta v2'. Sem mudança, o clique responde 'Nada mudou desde a v1'.
- Proposta: Primária = 'Responder esclarecimento' enquanto houver pergunta aberta; 'Submeter proposta v2' só depois de alterar preço ou condição.
- Método: Outro
- Ganho: Zero clique inútil; o verde é o próximo passo
- Evidência: v3out/PT-02det.json inv.primary e results[0] ('Nada mudou desde a v1…'); v3/PT-02det.dc.html (PRÓXIMA AÇÃO 'Responder esclarecimento')
- Cuidado: Cada versão submetida fica preservada.

### POS-30 · Baixa · PT-02det · Entrada mais rápida
- Módulo: Portal do parceiro
- Nível: Modal
- Elemento: Itens e preços › 'Item da proposta' (Preço)
- Persona: fornecedor
- Hoje: Para revisar a proposta, o fornecedor abre um modal por item (5 itens) e digita o preço em cada um; o robô não achou a unidade junto do campo Preço.
- Proposta: Coluna Preço editável na própria tabela, com R$/kg ao lado; Enter desce ao próximo item; 'Colar da planilha' para os 5 preços de uma vez; total recalculado na linha.
- Método: Grade editável
- Ganho: 5 modais → 1 grade; 5 preços colados em 1 ação
- Evidência: v3/PT-02det.dc.html GRIDS g_it (5 itens; edit m=form 'Item da proposta'); v3out/PT-02det.json results (campo 'Preço' sem unidade); robot3/summ.txt PT-02det ('sem unidade 1')
- Cuidado: Versão submetida preservada; frete e validade continuam por proposta.

### POS-31 · Baixa · PT-05det · Entrada mais rápida
- Módulo: Portal do parceiro
- Nível: Modal
- Elemento: 'Documento da carga 3' (Tipo, Número, Anexo)
- Persona: fornecedor
- Hoje: O fornecedor digita o número da NF-e e o 'Anexo' é um campo de texto, não um envio de arquivo.
- Proposta: 'Enviar XML da NF-e': lê número, chave, data, itens, peso e valor, confere com o pedido PC-088 e a carga 3 e mostra só as divergências ao comprador.
- Método: Captura (XML de NF-e)
- Ganho: 2 textos → 0; conferência do comprador só no que divergiu (UX-09)
- Evidência: v3/PT-05det.dc.html gaveta d65 (inputs 'Número' e 'Anexo' type=text)
- Cuidado: Documento vinculado ao pedido e à carga; divergência abre caso, não é aceita sozinha.

### POS-32 · Baixa · PT-01, PT-02, PT-03, PT-04, PT-05, PT-06, PT-07 · Ações no ⋯
- Módulo: Portal do parceiro
- Nível: Linha da tabela
- Elemento: Coluna 'Abrir' (g_op, g_av, g_cot, g_ds, g_ng) e ações em g_of, g_co, g_us
- Persona: fornecedor, comprador, banco (parceiros)
- Hoje: Cinco tabelas têm uma coluna 'Abrir' com um botão que repete o clique da linha (Abrir proposta, Abrir negócio, Abrir dossiê) ou faz uma ação (Baixar comprovante, Ver motivo, Ver decisão registrada). PT-07 tem 'Revogar acesso' e 'Reenviar convite' direto na linha.
- Proposta: Remover a coluna 'Abrir' (a linha abre o detalhe); ações no ⋯: Responder esclarecimento, Acompanhar negociação, Baixar comprovante, Ver motivo, Criar ação interna; em PT-07, Reenviar convite e, por último, Revogar acesso.
- Método: Menu ⋯
- Ganho: 1 coluna a menos em 5 tabelas; ação perigosa fora do alcance acidental
- Evidência: v3/PT-0x.dc.html GRIDS (coluna 'Abrir' com partes cta e act); v3out/PT-01.json e PT-02.json (row0 acts ['Abrir proposta'], kebab=false)

### POS-33 · Baixa · CO-03 · Modal e botões
- Módulo: Colheita e pós-colheita (legado)
- Nível: Linha da tabela
- Elemento: Botão 'Emitir romaneio' em cargas já recebidas
- Persona: balanceiro
- Hoje: Nas cargas recebidas (CG-1206, CG-1205, CG-0988) a ação da linha é 'Emitir romaneio', que reemite um documento já existente ('ROM-0790 emitido de novo'). O verbo sugere uma tarefa pendente que não existe.
- Proposta: A situação mostra 'Romaneio ROM-0790 emitido'; 'Reimprimir romaneio' vai para o ⋯.
- Método: Menu ⋯
- Ganho: Linha recebida sem botão; nada parece pendente
- Evidência: v3/CO-03.dc.html SPEC q22 (mensagens 'emitido de novo'); robot3/summ.txt CO-03
- Cuidado: Romaneio reimpresso continua o mesmo documento, sem novo número.

### POS-34 · Baixa · CO-02det · Erro ou risco
- Módulo: Colheita e pós-colheita (legado)
- Nível: Campo
- Elemento: 'Registrar avanço do turno': Horas de equipe e Dia
- Persona: encarregado de colheita
- Hoje: 'Horas de equipe' vem preenchido com '8 × 3,0 h' e 'Dia' com '24/09', ambos em texto livre. Quantidade real pré-preenchida tende a ser aceita sem conferir.
- Proposta: Dia com atalhos Hoje e Ontem; tamanho da equipe herdado da ordem (8) e horas calculadas pelo início e fim do turno no app, ou campo vazio a digitar; nunca padrão fixo.
- Método: Atalho de data
- Ganho: Horas sem chute; data em 1 toque
- Evidência: v3/CO-02det.dc.html GRIDS g_ap edit (dia def '24/09' t:'txt'; horas def '8 × 3,0 h' t:'txt'); v3out/CO-02det.json results[0]
- Cuidado: Decisão fixa: quantidade real nunca vem pré-preenchida.

### GES-35 · Baixa · CD-07 · Entrada mais rápida
- Módulo: Cadastros
- Nível: Campo
- Elemento: 'Conta ou centro no ERP', 'Tipo de operação (TOP)' e 'Código superior' no formulário de código
- Persona: controller, quem implanta
- Hoje: Os três campos são texto livre. O código superior só é conferido depois ('Não existe o código X'). A tela já importa do ERP (prévia de novos e alterados), mas o plano de contas não vira lista para escolher.
- Proposta: Busca com autocompletar no plano de contas e nas TOPs importadas do ERP. 'Código superior' como lista dos códigos da mesma dimensão.
- Método: Lista ou busca com autocompletar
- Ganho: 3 campos digitados → 3 escolhas, sem erro de digitação de conta.
- Evidência: v3/CD-07.dc.html GRIDS g_dim.edit.fields (sup, conta e top 't':'txt'). Validação 'Não existe o código ...'. Prévia c7imp (Importar do ERP).
- Cuidado: Código sem conta fica fora da publicação até ser mapeado (já existe).

### GES-36 · Baixa · CD-05 · Entrada mais rápida
- Módulo: Cadastros
- Nível: Campo
- Elemento: 'CPF ou CNPJ' e 'Nome ou razão social' no cadastro de parceiro
- Persona: quem implanta, comprador, comercial
- Hoje: O CNPJ é digitado e conferido (dígito verificador e duplicidade), mas a razão social é digitada à parte.
- Proposta: Ao completar o CNPJ, buscar a razão social e o município em consulta pública e preencher, mostrando a origem e deixando editar.
- Método: Lista ou busca com autocompletar
- Ganho: 2 → 1 campo digitado por parceiro.
- Evidência: v3/CD-05.dc.html GRIDS g_forn.edit.fields (cnpj, nome txt) e a função regras (docOk, dupDoc). 'Receita': 0 ocorrências.
- Cuidado: O CNPJ não muda depois do cadastro (já existe).

### GES-37 · Baixa · GE-04 · Entrada mais rápida
- Módulo: Gestão e finanças
- Nível: Campo
- Elemento: Datas 'Pagamento programado' (GE-04), 'Próxima cobrança' (GE-05), 'Prazo' (GE-07), 'Validade ou fim' (GE-08), 'Admissão' (CD-04)
- Persona: financeiro, gestor, quem implanta
- Hoje: São calendários sem atalho. No 'Pagamento programado', o valor mais comum (o próprio vencimento) precisa ser escolhido de novo.
- Proposta: Chips de data conforme o campo: 'no vencimento / hoje / +7' (pagamento), '+3 / +7' (cobrança), '+15 / +30 / fim do mês' (prazo).
- Método: Atalho de data
- Ganho: Calendário (3 ou 4 cliques) → 1 toque.
- Evidência: summ.txt l.129, l.165 e l.171 (datas sem atalho). GRIDS g_tit (prog), g_rec (cob), g_ac (prazo) e g_doc (val) com 't':'date', sem chips.

### GES-38 · Baixa · ON-01 · Clareza
- Módulo: Implantação
- Nível: Tela
- Elemento: Cabeçalho 'Passo 3 de 6 · retomável' + link 'Criar primeiro planejamento'; tabela 'Passos do assistente'
- Persona: quem implanta (cadastro inicial)
- Hoje: O topo leva ao passo 6 enquanto o passo 2 tem pendências, o 3 está em andamento e o 5 tem 3 objetos com erro. Na tabela, o passo 2 tem dois botões soltos ('Desenhar áreas' e 'Anexar CAR'), e o passo 6 diz 'pelo botão principal'.
- Proposta: Escrever no topo o motivo do atalho ('Você já pode planejar; faltam polígono e CAR') ou fazer a primária seguir o passo em andamento. Na tabela, clicar no passo abre a próxima ação; a 2ª ação vai para o ⋯.
- Método: Menu ⋯
- Ganho: Próximo passo coerente com o estado mostrado.
- Evidência: v3/ON-01.dc.html GRIDS g_passos (estados e células 'act'). Topo 'Passo 3 de 6 · retomável' com o link 'Criar primeiro planejamento' → SAF.
- Cuidado: O onboarding é retomável. Não forçar a ordem dos passos.

### GES-39 · Baixa · PA · Ações no ⋯
- Módulo: Planos agronômicos
- Nível: Cartão
- Elemento: Cartões da 'Biblioteca de planos por cultura' com o botão 'Abrir plano →'
- Persona: agrônomo, quem implanta
- Hoje: O cartão não abre com clique; só o botão 'Abrir plano →' abre. Não há ⋯ no cartão, e 'Copiar atividades' só aparece dentro de 'Criar plano' ('Começar de').
- Proposta: Clicar no cartão abre o plano. O ⋯ do cartão traz 'Criar plano a partir deste' (já com a cópia escolhida) → 'Arquivar'.
- Método: Menu ⋯
- Ganho: Alvo de clique maior e a cópia em 1 clique a partir do plano certo.
- Evidência: v3out/PA.inv2.json (cards 'clickable': false, ação 'Abrir plano ...'). v3/PA.dc.html paNp (np_bases 'Copiar atividades de ...').
- Cuidado: Um plano copiado nasce em rascunho e precisa ser publicado.

### GES-40 · Baixa · BO-02 · Resolver em 1 clique
- Módulo: Backoffice
- Nível: Detalhe
- Elemento: Painel da organização inadimplente (Fazenda Aurora · vencida há 22 dias · 3 tentativas)
- Persona: administrador da plataforma (backoffice)
- Hoje: O painel mostra plano, áreas, pagamento e faturas, mas não tem ação para a inadimplência. A primária do topo é 'Conciliar pagamentos', e a ação de resolução só existe para contestação.
- Proposta: No painel do inadimplente: 'Enviar 2ª via / link de pagamento ao responsável' (simulado), com o histórico de tentativas. A régua (aviso, restrição) fica visível com as datas.
- Método: Resolver em 1 clique
- Ganho: Caso parado → 1 clique com o contexto da fatura.
- Evidência: v3/BO-02.dc.html EXTRAVALS (bo_dec só quando há fatura contestada; nenhuma ação para inadimplente). v3out/BO-02.json inv.tables[0] linha 'Inadimplente Fazenda Aurora'.
- Cuidado: A plataforma vê só área e cobrança da organização (isolamento).

## Ações soltas nas linhas e nos cartões

| Tela | Onde | Botões | Usa ⋯ |
|---|---|---|---|
| AG-01 | Tabela 1 | Confirmar foco | não |
| AG-03 | Tabela 1 | DIA-007 · VIS-011 · Abrir REC-014 | não |
| AG-04 | Tabela 1 | REC-014 · DIA-007 · Abrir REC-014 | não |
| AG-05 | Tabela 1 | Simular | não |
| AG-06 | Tabela 1 | REC-016 · OS-0421 · Programar pós | não |
| MB-06 | Lista de 2 itens ou cartões | Concluir com 9 de 14 pontos | não |
| MB-08 | Lista de 2 itens ou cartões | Pausar · Retomar · Registrar avanço | não |
| CA-01 | Tabela 1 | Liberar › | não |
| CA-01x-os0420 | Lista de 2 itens ou cartões | Ver fichas | não |
| CA-02 | Tabela 1 | OS-0421 · v2 · Conferir | não |
| CA-02 | Lista de 3 itens ou cartões | Reabrir saldo da OS-0417 | não |
| CA-03 | Tabela 1 | Abrir ocorrência › | não |
| CA-03det | Lista de 2 itens ou cartões | Abrir manutenção · Mais ações de Relato | sim |
| CA-04 | Tabela 1 | Devolver saldo | não |
| CO-01 | Tabela 1 | Comparar pedidos | não |
| CO-02 | Tabela 1 | OC-0510 · Registrar avanço | não |
| CO-03 | Tabela 1 | Confirmar chegada | não |
| CO-04 | Tabela 1 | Receber bloqueado | não |
| CO-05 | Tabela 1 | OB-0110 · Registrar saídas | não |
| CO-06 | Tabela 1 | Decidir lote | não |
| CO-06det | Tabela 3 | Comercial (VE-04) | não |
| CO-07 | Tabela 1 | Abrir lote | não |
| CMP | Tabela 1 | Ver origem · Abrir compra | não |
| CF-04 | Tabela 1 | Fatura ago/2026 | não |
| CARGA | Tabela 1 | Abrir ordem de beneficiamento · Igor (responsável de produção) | não |
| GE-01 | Tabela 2 | Abrir origem do desvio | não |
| GE-03 | Tabela 1 | NF 8842 · recebimento | não |
| GE-04 | Tabela 1 | Abrir aprovação | não |
| GE-06 | Tabela 1 | Detalhar | não |
| GE-06 | Tabela 2 | Trator T1 · JD 6M 155 | não |
| GE-06det | Tabela 2 | Abrir ordens | não |
| GE-07 | Tabela 1 | Reabrir com motivo | não |
| GE-08 | Tabela 1 | Ver título | não |
| GE-08 | Tabela 2 | Autorizar bloco | não |
| ON-01 | Tabela 1 | Rever dados | não |
| IN-01 | Tabela 1 | Reprogramar saldo | não |
| IN-02 | Tabela 1 | Decidir | não |
| IN-03 | Tabela 1 | Abrir origem | não |
| IR-01 | Tabela 1 | Abrir OS-0507 | não |
| IR-03det | Lista de 2 itens ou cartões | Adicionar produtos | não |
| LO-01 | Tabela 1 | Ver fila | não |
| LO-02 | Tabela 1 | Conferir carga | não |
| LO-02 | Tabela 2 | Conferir carga | não |
| LO-03 | Tabela 1 | Ver frete | não |
| LO-04 | Tabela 2 | Solicitar documento | não |
| LO-04 | Tabela 3 | Encaminhar pagamento | não |
| MA | Tabela 1 | PM-02 v2 | não |
| PA | Lista de 2 itens ou cartões | Abrir plano Soja alta tecnologia | não |
| PA | Lista de 3 itens ou cartões | Abrir plano Milho safrinha | não |
| PA | Lista de 3 itens ou cartões | Abrir plano Mamão Formosa produção | não |
| PL-01 | Tabela 1 | Abrir plano | não |
| PL-01 | Lista de 2 itens ou cartões | Encerrar período | não |
| PL-02 | Tabela 1 | Abrir O.S. · Ver recomendação | não |
| PL-03 | Tabela 3 | Ver ordem | não |
| PL-04 | Tabela 1 | Abrir O.S. | não |
| PL-04 | Tabela 3 | Receber devolução | não |
| PL-04 | Tabela 4 | Ver ordem | não |
| PL-05 | Tabela 1 | Propor substituição | não |
| PT-01 | Tabela 1 | Abrir proposta | não |
| PT-01 | Tabela 2 | Responder esclarecimento | não |
| PT-02 | Tabela 1 | Abrir proposta | não |
| PT-02det | Lista de 2 itens ou cartões | Baixar comprovante | não |
| PT-03 | Tabela 1 | Acompanhar negociação | não |
| PT-04 | Tabela 1 | Abrir dossiê | não |
| PT-05 | Tabela 1 | Abrir negócio | não |
| PT-05det | Lista de 2 itens ou cartões | Abrir divergência | não |
| PT-06 | Tabela 2 | Criar ação interna | não |
| PT-06 | Lista de 2 itens ou cartões | Exportar autorizado | não |
| PT-07 | Tabela 2 | Revogar acesso | não |
| PT-07 | Lista de 2 itens ou cartões | Ver assinatura e fatura | não |
| SAF | Tabela 1 | Editar · Continuar: aplicar plano em 4 cultivos | não |
| SU-01 | Tabela 1 | Ver contrato | não |
| SU-03 | Tabela 1 | Reserva em conflito | não |
| SU-05 | Tabela 1 | Abrir contrato | não |
| SU-06 | Tabela 1 | Liberar qualidade | não |
| SU-07 | Tabela 1 | Receber devolução | não |
| SU-07det | Lista de 2 itens ou cartões | Destinar saldo · Conciliar custódia | não |
| SU-08 | Tabela 1 | Confirmar recebimento | não |
| SU-09 | Tabela 1 | Aprovar ajuste | não |
| VE-01 | Tabela 1 | PV-031 · L39-120 · Detalhar demanda | não |
| VE-03 | Tabela 1 | Ver reserva | não |
| VE-04 | Tabela 1 | Confirmar pedido | não |
| VE-04det | Tabela 2 | L39-120 · OB-0110 | não |
| VE-05 | Tabela 1 | PV-030 · Programar entrega | não |
| VE-06 | Tabela 1 | Autorizar retorno | não |

## Formulários e painéis (campos: digitados / escolhidos / pré-preenchidos / calculados)

| Tela | Ação | Abriu | Campos | Dig. | Esc. | Pré | Calc. | Nº sem teclado | Nº sem unidade | Data sem atalho |
|---|---|---|---|---|---|---|---|---|---|---|
| CD-08 | Criar rendimento | Cadastrar rendimento | 15 | 8 | 5 | 0 | 2 | 0 | 0 | 1 |
| AG-02 | Registrar laudo | Registrar laudo de solo | 17 | 7 | 10 | 0 | 0 | 0 | 5 | 0 |
| EST | Conferir NF 4533 | Recebimento · NF 4533 | 11 | 5 | 3 | 3 | 0 | 0 | 0 | 0 |
| GE-02 | Criar cenário | Criar cenário | 5 | 5 | 0 | 0 | 0 | 0 | 1 | 0 |
| MB-03 | Iniciar turno |  | 5 | 5 | 0 | 0 | 0 | 0 | 0 | 0 |
| MB-03 | Iniciar turno · OS-0421 |  | 5 | 5 | 0 | 0 | 0 | 0 | 0 | 0 |
| AG-02 | + Registrar medição | Registrar medição de água no solo | 13 | 4 | 8 | 0 | 1 | 0 | 1 | 1 |
| AG-03 | + Criar diagnóstico | Criar diagnóstico | 7 | 4 | 3 | 0 | 0 | 0 | 0 | 0 |
| AG-05 | + Criar versão | Criar versão | 6 | 4 | 2 | 0 | 0 | 0 | 0 | 0 |
| CARGA | Registrar pesagem | Registrar pesagem | 4 | 4 | 0 | 0 | 0 | 0 | 0 | 0 |
| CD-03 | Criar máquina ou instalação | Cadastrar máquina ou instalação | 11 | 4 | 5 | 0 | 2 | 0 | 0 | 0 |
| CD-06 | Criar item | Cadastrar item | 11 | 4 | 7 | 0 | 0 | 1 | 2 | 1 |
| GE-07 | Criar ação | Criar ação | 7 | 4 | 3 | 0 | 0 | 0 | 0 | 1 |
| VE-06 | Abrir caso | Novo caso | 6 | 4 | 2 | 0 | 0 | 1 | 1 | 0 |
| CD-01 | Criar fazenda | Cadastrar fazenda | 6 | 3 | 3 | 0 | 0 | 0 | 0 | 0 |
| CO-03 | Registrar carga | Registrar carga | 7 | 3 | 3 | 0 | 1 | 0 | 0 | 0 |
| SU-08 | Registrar perda | Registrar perda em alçada | 5 | 3 | 2 | 0 | 0 | 1 | 0 | 0 |
| VE-04 | + Criar pedido | Novo pedido de venda | 7 | 3 | 4 | 0 | 0 | 0 | 1 | 0 |
| VE-05 | Formalizar compromisso | Novo compromisso | 5 | 3 | 2 | 0 | 0 | 0 | 0 | 0 |
| CA-03 | Registrar ocorrência | Registrar ocorrência | 7 | 2 | 4 | 1 | 0 | 0 | 0 | 0 |
| CD-02 | Criar cultivar | Cadastrar cultivar | 6 | 2 | 4 | 0 | 0 | 0 | 0 | 0 |
| CD-04 | Criar pessoa | Cadastrar pessoa | 22 | 2 | 20 | 0 | 0 | 0 | 0 | 2 |
| CO-02det | Registrar avanço | Registrar avanço do turno · OC-0510 | 4 | 2 | 0 | 2 | 0 | 0 | 0 | 0 |
| GE-08 | Incluir documento | Incluir documento | 5 | 2 | 3 | 0 | 0 | 0 | 0 | 1 |
| GE-08 | CAR Registrado Santa Rita GO-5218805-7F2A.1C9B.44E | Documento · CAR | 6 | 2 | 1 | 1 | 2 | 0 | 0 | 1 |
| LO-01 | + Reservar slot | Reservar slot de doca | 4 | 2 | 1 | 1 | 0 | 0 | 0 | 0 |
| MB-10 | Apontar área · OS-0505 |  | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 0 |
| MB-10 | Registrar carga · OS-0505 |  | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 0 |
| PL-01 | + Criar safra | Nova safra | 4 | 2 | 1 | 0 | 1 | 1 | 1 | 0 |
| PT-07 | + Convidar usuário | Convidar usuário | 3 | 2 | 1 | 0 | 0 | 0 | 0 | 0 |
| SU-06 | Conferir NF 4533 | Recebimento · NF 4533 PC-090 Coop. Vale | 6 | 2 | 3 | 1 | 0 | 0 | 0 | 0 |
| SU-06 | Ler documento/QR | Recebimento · NF 4533 PC-090 Coop. Vale | 6 | 2 | 3 | 1 | 0 | 0 | 0 | 0 |
| SU-08 | Transferir entre locais | Transferir entre locais | 5 | 2 | 3 | 0 | 0 | 1 | 0 | 0 |
| VEN | Registrar venda | Registrar venda | 2 | 2 | 0 | 0 | 0 | 0 | 1 | 0 |
| AG-06 | EF-021 REC-016 → OS-0421 fungicida T1+T2 % folíolo | Avaliação de eficácia · EF-021 | 4 | 1 | 1 | 2 | 0 | 0 | 0 | 0 |
| CA-01det | 20/09 Dia 1 de 7 50 ha 50 / 350 ha Conferido app · | Turno · 20/09 | 5 | 1 | 0 | 1 | 3 | 0 | 0 | 0 |
| CO-01 | T7 Mamão Formosa · 42 ha produção · sem. 39 11.980 | Revisar previsão · T7 Mamão Formosa · 42 ha | 7 | 1 | 0 | 6 | 0 | 1 | 1 | 0 |
| IN-03 | Criar tarefa vinculada | Nova tarefa vinculada | 4 | 1 | 3 | 0 | 0 | 0 | 0 | 1 |
| IR-03det | Adicionar produtos | Adicionar produtos · OS-0419 | 3 | 1 | 1 | 1 | 0 | 0 | 1 | 0 |
| IR-04 | + Cadastrar sensor | Cadastrar sensor | 4 | 1 | 3 | 0 | 0 | 0 | 0 | 1 |
| LO-02 | Separar lotes aptos e reservados para um pedido | Separar lotes da carga | 3 | 1 | 2 | 0 | 0 | 0 | 0 | 0 |
| LO-02det | Registrar lacre | Registrar lacre · Lacre aplicado | 4 | 1 | 2 | 0 | 1 | 0 | 0 | 0 |
| MB-09 | Registrar leitura |  | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| MB-10 | Descartar carga a pesar |  | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| PA | Criar plano | Novo plano | 2 | 1 | 1 | 0 | 0 | 0 | 0 | 0 |
| PT-02det | O frete CIF até o Galpão 2 vale para os 5 itens? C | Esclarecimento · O frete CIF até o Galpão 2 vale para os 5 i | 2 | 1 | 0 | 1 | 0 | 0 | 0 | 0 |
| PT-06 | Criar ação interna | Ação interna da Fertisul · Fertilizantes e corretivos · Triâ | 4 | 1 | 2 | 0 | 1 | 0 | 0 | 1 |
| SAF | Criar safra | Nova safra | 7 | 1 | 6 | 0 | 0 | 0 | 0 | 2 |
| SU-01 | Reprogramar proposta | Reprogramar proposta de reposição | 3 | 1 | 2 | 0 | 0 | 0 | 0 | 1 |
| SU-02 | Submeter exceção | Submeter exceção versionada | 5 | 1 | 3 | 1 | 0 | 0 | 0 | 2 |
| SU-02 | Fertilizantes Galpão 2 A · Alta Necessidade datada | Política · Fertilizantes Galpão 2 | 10 | 1 | 4 | 5 | 0 | 1 | 1 | 0 |
| SU-08 | Estornar com vínculo | Estornar com vínculo | 2 | 1 | 1 | 0 | 0 | 0 | 0 | 0 |
| AG-01 | Programar vistoria | Programar vistoria | 4 | 0 | 4 | 0 | 0 | 0 | 0 | 1 |
| AG-01 | Confirmar foco | VIS-055 · Mancha-anelar (PRSV) · Pivô 22 | 2 | 0 | 1 | 1 | 0 | 0 | 1 | 1 |
| AG-01 | Programar vistoria | Programar vistoria | 4 | 0 | 4 | 0 | 0 | 0 | 0 | 1 |
| AG-02 | AGS-004 Pivô 12 16/09/2026 não calculável sem pont | Medição de água no solo · AGS-004 | 13 | 0 | 0 | 0 | 13 | 0 | 1 | 1 |
| AG-03det | VIS-011 Vistoria · trincheira 15/09/2026 Média vál | Evidência · VIS-011 | 5 | 0 | 0 | 0 | 5 | 0 | 0 | 1 |
| AG-04det | KCl 60 % kg/ha 118 120 fertilizante · fora do Agro | Item da recomendação · KCl 60 % | 2 | 0 | 0 | 0 | 2 | 1 | 1 | 0 |
| AG-04det | v1 KCl 100 kg/ha em dose única — Substituída 18/09 | Versão da recomendação · v1 | 5 | 0 | 0 | 0 | 5 | 0 | 0 | 0 |
| AG-04det | Z1 (reboleiras) 62 ha 0,05 cmolc/dm³ 140 kg/ha 123 | Dose da zona · Z1 (reboleiras) | 3 | 0 | 0 | 0 | 3 | 0 | 0 | 0 |
| AG-04det | NEC-028 Necessidade de plantio do T4 · 204 ha · 1ª | Registro vinculado · NEC-028 | 3 | 0 | 0 | 0 | 3 | 0 | 0 | 0 |
| AG-04det | Semente de soja 58 W REQ-036 1.560 kg × R$ 9,50 R$ | Custo realizado · Semente de soja 58 W | 3 | 0 | 0 | 0 | 3 | 1 | 1 | 0 |
| AG-05 | Soja alta tecnologia v6 plano-modelo Soja · Cerrad | Item da biblioteca · Soja alta tecnologia v6 plano-modelo | 6 | 0 | 0 | 0 | 6 | 0 | 0 | 0 |
| AG-06 | Efetivamente evitada R$ 41 mil 2 aplicações dispen | Economia estimada · Efetivamente evitada | 2 | 0 | 0 | 0 | 2 | 0 | 0 | 0 |
| AG-07 | 1,4 Sight Reg. 17622 · Bem Brasil Alimentos S/A. 9 | 1,4 Sight | 3 | 0 | 2 | 0 | 1 | 0 | 0 | 0 |
| BO-01 | Simular área | Simular área | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0 |
| BO-01 | Avaliação Mapa, Cadastros, Agrícola (O.S. e app de | Plano · Avaliação | 9 | 0 | 0 | 0 | 9 | 3 | 3 | 0 |
| CA-01 | OS-0418 v2 Fertirrigação · reclassificada P1 · 95  | Ordem · OS-0418 v2 | 5 | 0 | 1 | 1 | 3 | 0 | 0 | 0 |
| CA-01det | Fungicida A · lote F26-02 REQ-035 · 0,50 L/ha da v | Custódia · Fungicida A · lote F26-02 | 4 | 0 | 0 | 0 | 4 | 0 | 0 | 0 |
| CA-01x-os0420 | Semente de soja 58 W (resistente) 52 kg/ha 5.200 k | Instrução · Semente de soja 58 W (resistente) | 3 | 0 | 0 | 0 | 3 | 1 | 1 | 0 |
| CA-01x-os0420 | 21/09 Dia 1 18 ha 18 / 100 ha Conferido app · sinc | Turno · 21/09 | 4 | 0 | 0 | 0 | 4 | 1 | 0 | 0 |
| CA-01x-os0420 | REQ-036 Semente de soja 58 W 5.200 kg 1.560 kg 1.5 | Requisição · REQ-036 | 3 | 0 | 0 | 0 | 3 | 0 | 0 | 0 |
| CA-03 | OC-114 Quebra de máquina T4 · OS-0420 22/09 06:40  | Ocorrência · OC-114 Quebra de máquina | 7 | 0 | 4 | 3 | 0 | 0 | 0 | 0 |
| CD-01det | Santa Rita Sequeiro — 312,0 ha 312,4 ha v3 +0,4 ha | Talhão · T1 | 6 | 0 | 3 | 2 | 1 | 0 | 0 | 0 |
| CD-02 | ▾ Soja 3 cultivares | Cultura · Soja | 3 | 0 | 1 | 1 | 1 | 0 | 0 | 0 |
| CD-04 | Ana Agronomia 31/12/2027 Liberar O.S. (agrônomo) | Pessoa · Ana | 23 | 0 | 21 | 2 | 0 | 0 | 0 | 3 |
| CD-05 | Bloqueado Trator T1 R$ 180,00/h — | Parceiro · Fertisul | 22 | 0 | 17 | 4 | 1 | 0 | 0 | 0 |
| CD-06 | ▾ Adjuvantes 2 itens | Grupo · Adjuvantes | 2 | 0 | 1 | 1 | 0 | 0 | 0 | 0 |
| CD-08 | ▾ Pulverização 1 conjunto | Operação · Pulverização | 3 | 0 | 1 | 2 | 0 | 0 | 0 | 0 |
| CF-01 | Ana Agronomia · Agrônoma e gestora gestora agrônom | Ana · Agronomia | 13 | 0 | 0 | 0 | 13 | 0 | 0 | 0 |
| CF-05 | Alterar plano ou área | Alterar plano ou área | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0 |
| CMP | Abrir compra |  | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |
| CO-01 | PV-031 10,0 t classe A 9,6 t 12,0 t × 80% falta 0, | Pedido × oferta de classe A · PV-031 | 2 | 0 | 0 | 0 | 2 | 0 | 0 | 0 |
| CO-01 | Mamão · semanal v S39-02 · 21/09 7 d 9,4% +3,1% 18 | Erro da previsão · Mamão · semanal | 2 | 0 | 0 | 0 | 2 | 0 | 0 | 0 |
| CO-03 | CG-1207 09:40 · Carreta 03 OC-0510 · T7 (mamão) 4. | Carga · CG-1207 09:40 · Carreta 03 | 7 | 0 | 3 | 3 | 1 | 0 | 0 | 0 |
| CO-05 | Criar ordem de processo | Criar ordem de processo | 5 | 0 | 2 | 2 | 1 | 0 | 0 | 0 |
| CO-05det | Entrada 12,0 t mamão de campo (L38-115 a L38-118)  | Saída do packing · OB-0110 · Entrada | 4 | 0 | 0 | 0 | 4 | 0 | 0 | 0 |
| CO-06det | INSP-88 L27-013 Café beneficiado 3.690 sc 60 kg Qu | Pendência de qualidade · INSP-88 | 3 | 0 | 0 | 0 | 3 | 1 | 1 | 0 |
| CO-06det | Defeitos (equiv.) ≤ 86 103 Acima do tipo | Resultado da amostra · Defeitos (equiv.) | 2 | 0 | 0 | 0 | 2 | 0 | 0 | 0 |
| CO-06det | Reserva de 500 sc · pedido PV-028 Comercial (VE-04 | Tentativa recusada · Reserva de 500 sc · pedido PV-028 | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 0 |
| CO-07 | L27-013 Armazém Sede · Santa Rita Café beneficiado | Movimentos do lote · L27-013 Armazém Sede · Santa Rita | 3 | 0 | 0 | 0 | 3 | 0 | 0 | 0 |
| COLH | Publicar previsão do Pivô 19 | Pivô 19 · Mamão Formosa Tainung 1 | 2 | 0 | 0 | 2 | 0 | 0 | 0 | 0 |
| GE-01 | Soja 51.280 sc · previsão V2 814 ha R$ 6,20 mi R$  | Resultado · Soja 51.280 sc · previsão V2 | 4 | 0 | 0 | 0 | 4 | 1 | 0 | 0 |
| GE-01 | Custo de pulverização acima do orçado Feijão · P1  | Desvio · Custo de pulverização acima do orçado | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 0 |
| GE-03 | NF 8842 · recebimento Defensivo · fungicida Feijão | Lançamento · NF 8842 · recebimento | 5 | 0 | 0 | 0 | 5 | 1 | 1 | 0 |
| GE-06 | Custo de pulverização Agronômico R$ ÷ ha tratado ( | Indicador · Custo de pulverização | 3 | 0 | 0 | 0 | 3 | 0 | 0 | 0 |
| GE-06det | Área tratada acima do plano +R$ 800 120 vs. 100 ha | Causa · Área tratada acima do plano | 2 | 0 | 0 | 0 | 2 | 0 | 0 | 0 |
| GE-06det | OS-0409 · pulverização ordem encerrada · 95 ha + r | Documento · OS-0409 · pulverização | 2 | 0 | 0 | 0 | 2 | 0 | 0 | 1 |
| GE-07 | AC-090 atraso de liberação de O.S. aderência 86% p | Caso · AC-090 atraso de liberação de O.S. | 7 | 0 | 0 | 0 | 7 | 0 | 0 | 1 |
| GE-08 | CRE-0102 custeio safra 26/27 Banco Terra R$ 850 mi | Solicitação · CRE-0102 | 4 | 0 | 0 | 0 | 4 | 0 | 0 | 0 |
| GE-08 | Produção e áreas talhões, safras, produtividade 3  | Bloco do dossiê · Produção e áreas | 5 | 0 | 4 | 0 | 1 | 0 | 0 | 1 |
| IN-01 | OS-0420 · plantio Santa Rita · T4 Substituir Trato | Tarefa · OS-0420 · plantio Santa Rita · T4 | 3 | 0 | 2 | 0 | 1 | 0 | 0 | 0 |
| IN-02 | Ajuste de inventário Galpão 2 Ajuste de inventário | Decisão · Ajuste de inventário Galpão 2 Ajuste de inventário | 3 | 0 | 0 | 0 | 3 | 1 | 1 | 0 |
| IN-04 | Importar |  | 1 | 0 | 0 | 0 | 0 | 1 | 1 | 0 |
| IR-01 | Impedida Bomba parada Pivô 5 13,2 mm Abrir OS-0507 | Setor · Pivô 5 | 10 | 0 | 0 | 3 | 7 | 0 | 0 | 0 |
| IR-02 | Programar irrigação | Programar irrigação | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |
| IR-03det | hoje 06:12 AU-3098 Necessidade calculada pelo bala | Evento · hoje 06:12 | 4 | 0 | 0 | 0 | 4 | 0 | 0 | 0 |
| LO-01 | T1 · 1ª de 3 Retirada · cliente Milho a granel · 3 | Reprogramar janela · T1 · 1ª de 3 Retirada · cliente | 2 | 0 | 1 | 1 | 0 | 0 | 0 | 0 |
| LO-01 | 08:00–09:00 Doca 1 · granel T1 · janela original p | Slot de doca · 08:00–09:00 | 4 | 0 | 0 | 0 | 4 | 0 | 0 | 0 |
| LO-02 | Registrar chegada | Registrar chegada na portaria · T1 | 3 | 0 | 3 | 0 | 0 | 0 | 0 | 1 |
| LO-02 | Separar lotes | Separar lotes da carga | 3 | 0 | 2 | 1 | 0 | 0 | 0 | 0 |
| LO-02 | T2 1 08:30 08:12 espera 23 min até a chamada Em do | Posição na fila · T2 | 2 | 0 | 0 | 0 | 2 | 0 | 0 | 0 |
| LO-02 | VD-2101 · 2ª de 3 Cooperativa Central MZ-26-03 · 3 | Expedição · VD-2101 · 2ª de 3 Cooperativa Central | 2 | 0 | 0 | 0 | 2 | 0 | 0 | 0 |
| LO-02det | TK-5531 · balança 1 14,20 t 51,20 t 37,00 t 13,8%  | Ticket de pesagem · TK-5531 · balança 1 | 4 | 0 | 0 | 0 | 4 | 1 | 1 | 0 |
| LO-02det | Produto, lote e destino conferem com o pedido Conf | Registrar lacre · Produto, lote e destino conferem com o ped | 4 | 0 | 0 | 0 | 4 | 0 | 0 | 0 |
| LO-02det | Autorização de saída Aguarda o lacre Sandra (fisca | Evento da saída · Autorização de saída | 2 | 0 | 0 | 0 | 2 | 0 | 0 | 0 |
| LO-03 | VG-112 Diesel S10 · 8 mil L (transferência 19/09)  | Viagem programada · VG-112 | 2 | 0 | 0 | 0 | 2 | 0 | 0 | 0 |
| LO-03 | Janela original (compromisso) 22/09 até 18:00 · co | Registro da entrega · Janela original (compromisso) | 2 | 0 | 0 | 0 | 2 | 1 | 1 | 0 |
| LO-04 | + Pedir cotação | Pedir cotação | 4 | 0 | 3 | 1 | 0 | 0 | 0 | 0 |
| LO-04 | Rota Sul Transportes 9,6 t × R$ 190/t R$ 1.824 che | Cotação recebida · Rota Sul Transportes | 4 | 0 | 0 | 0 | 4 | 0 | 0 | 0 |
| LO-04 | Rota Sul Transportes Sede → Vitória/ES R$ 190/t 28 | Prestador · Rota Sul Transportes Sede → Vitória/ES | 4 | 0 | 1 | 3 | 0 | 0 | 0 | 0 |
| LO-04 | Peso líquido (t) v2 · vigente desde 01/08 padrão i | Direcionador de rateio · Peso líquido (t) | 3 | 0 | 0 | 0 | 3 | 0 | 0 | 0 |
| MA | Gerar 3 ordens preventivas | OM-0235 · Trator 03 | 3 | 0 | 2 | 1 | 0 | 0 | 0 | 1 |
| ON-01 | 1 · Organização Concluído nome e e-mail do respons | Passo · 1 · Organização | 3 | 0 | 0 | 0 | 3 | 0 | 0 | 0 |
| ON-01 | Cadastro, planejamento, execução e consultas Inclu | Direito do trial · Cadastro, planejamento, execução e consul | 4 | 0 | 0 | 0 | 4 | 0 | 0 | 0 |
| OS | Criar ordem | Nova ordem | 4 | 0 | 2 | 0 | 2 | 0 | 0 | 1 |
| PL-01 | Safra 2026/27 set/2026 – ago/2027 Santa Rita 9 cul | Safra · Safra 2026/27 | 4 | 0 | 1 | 2 | 1 | 1 | 1 | 0 |
| PL-01 | T1-A Parcela Soja 58 W 160 ha 15/10/2026 64 sc/ha  | Cultivo · T1-A Parcela | 7 | 0 | 3 | 2 | 2 | 0 | 0 | 1 |
| PL-02 | Decidir pendência | Operação · C1 Café Catuaí 144 | 8 | 0 | 1 | 3 | 4 | 1 | 1 | 0 |
| PL-02 | T4 Soja 58 W · 100 ha Plantio · 1ª onda NEC-028 ·  | Operação · T4 Soja 58 W | 6 | 0 | 0 | 3 | 3 | 1 | 1 | 0 |
| PL-02det | Dessecação de manejo 40 dias antes do plantio · DA | Ajuste local · Dessecação de manejo | 5 | 0 | 0 | 0 | 5 | 2 | 2 | 1 |
| PL-03 | Tratores 150+ cv Plantio soja 910 ha 1.180 h 910 h | Carga × capacidade · Tratores 150+ cv | 4 | 0 | 0 | 0 | 4 | 0 | 0 | 0 |
| PL-03 | Remanejar colhedora ociosa + operador 60 h R$ 4 mi | Cenário · Remanejar colhedora ociosa + operador | 4 | 0 | 0 | 3 | 1 | 0 | 0 | 0 |
| PL-03 | Corretiva OM-0233 Trator T1 · retorno previsto 14h | Manutenção × produção · Corretiva OM-0233 Trator T1 · retorn | 3 | 0 | 0 | 0 | 3 | 0 | 0 | 0 |
| PL-04 | OS-0421 fungicida T1+T2 24–26/09 dias 5–7 · saldo  | Programar · OS-0421 fungicida T1+T2 | 6 | 0 | 2 | 2 | 2 | 0 | 0 | 0 |
| PL-04 | Trator 02 · MF 7719 Apta livre hoje · 25/09 OS-043 | Máquina · Trator 02 · MF 7719 | 2 | 0 | 0 | 0 | 2 | 0 | 0 | 0 |
| PL-04 | OS-0417 · cobertura P1 Em conferência Sobras a rec | Pendência · OS-0417 · cobertura P1 | 2 | 0 | 0 | 0 | 2 | 0 | 0 | 0 |
| PL-04 | Corretiva OM-0233 Trator T1 · retorno previsto 14h | Manutenção × produção · Corretiva OM-0233 Trator T1 · retorn | 3 | 0 | 0 | 3 | 0 | 0 | 0 | 0 |
| PL-05 | Ativo bloqueado Trator T1 · OM-0233 pressão hidráu | Impedimento · Ativo bloqueado Trator T1 · OM-0233 pressão hi | 5 | 0 | 2 | 1 | 2 | 0 | 0 | 0 |
| PL-06 | T1-A polígono norte 160 ha Safra 2026/27 · soja 58 | Parcela · T1-A polígono norte | 6 | 0 | 2 | 1 | 3 | 0 | 0 | 1 |
| PL-06 | 01/02 5.120 sc 3.000 sc +2.120 sc → armazém 5.500  | Semana · 01/02 | 3 | 0 | 0 | 0 | 3 | 0 | 0 | 0 |
| PT-02det | MAP 11-52 79.500 kg R$ 3,783/kg R$ 300.748,50 | Item da proposta · MAP 11-52 | 3 | 0 | 0 | 1 | 2 | 0 | 1 | 0 |
| PT-02det | CIF · incluso até o Galpão 2 28 dias 12 dias 30/09 | Condições da proposta · CIF · incluso até o Galpão 2 | 5 | 0 | 3 | 2 | 0 | 0 | 0 | 1 |
| PT-03 | 2.000 kg 05/10–11/10 R$ 3,05 CIF Vitória/ES caixas | Proposta de compra · OF-103 · 2.000 kg | 5 | 0 | 2 | 3 | 0 | 0 | 1 | 0 |
| PT-05det | Cargas 1–2 60 t 19/09/2026 QAS-1B20 NF 4501 Recebi | Previsão da carga · Cargas 1–2 | 3 | 0 | 0 | 0 | 3 | 0 | 0 | 1 |
| PT-06 | Convites recebidos 14 — — | Etapa do funil · Convites recebidos | 2 | 0 | 0 | 0 | 2 | 0 | 1 | 0 |
| PT-06 | Fertilizantes e corretivos · Sudoeste GO 11 3 R$ 1 | Ação interna da Fertisul · Fertilizantes e corretivos · Sudo | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 0 |
| PT-06 | Preço mediano de fertilizantes NPK · Sudoeste GO − | Agregado · Preço mediano de fertilizantes NPK · Sudoeste GO | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 0 |
| PT-07 | Fertisul Fertilizantes Ltda 12.345.678/0001-95 Fer | Credenciamento · Fertisul Fertilizantes Ltda 12.345.678/0001 | 16 | 0 | 13 | 2 | 1 | 0 | 0 | 0 |
| PT-07 | Marta Nunes marta@fertisul.com.br Administradora A | Usuário · Marta Nunes | 3 | 0 | 0 | 0 | 3 | 0 | 0 | 0 |
| PT-07 | Novos convites Portal + e-mail | Preferência de aviso · Novos convites | 2 | 0 | 1 | 0 | 1 | 0 | 0 | 0 |
| SAF | Editar | Safra · Safra 2026/27 | 7 | 0 | 6 | 1 | 0 | 0 | 0 | 2 |
| SU-01 | ▸ Semente de soja 58 W Sementes · 3 origens Cobert | Necessidade · Semente de soja 58 W | 2 | 0 | 0 | 0 | 2 | 0 | 0 | 1 |
| SU-03 | Reservar para ordem | Reservar saldo para ordem | 3 | 0 | 2 | 1 | 0 | 1 | 0 | 0 |
| SU-03 | KCl 60% · K26-11 Galpão 2 60.000 kg 10.000 kg 50.0 | Saldo · KCl 60% · K26-11 | 2 | 0 | 0 | 0 | 2 | 0 | 0 | 0 |
| SU-03det | Físico no lote 545 L validade 03/2028 · NF 4390 | Saldo do lote · Físico no lote | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 0 |
| SU-04 | SOL-2026-07 · Adjuvantes Planejar safra · demanda  | Cotação · SOL-2026-07 · Adjuvantes | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 0 |
| SU-04 | Fertisul R$ 360.905 CIF · incluso 12 dias CIF · 28 | Proposta · Fertisul | 2 | 0 | 0 | 0 | 2 | 0 | 0 | 0 |
| SU-05det | Reprogramar carga 4 | Reprogramar carga 4 | 3 | 0 | 2 | 1 | 0 | 0 | 0 | 2 |
| SU-06 | NF 4501 PC-088 · Fertisul KCl 60% K26-11 60.000 kg | Recebimento · NF 4501 PC-088 Fertisul | 6 | 0 | 0 | 0 | 6 | 0 | 0 | 0 |
| SU-07 | Solicitar | Solicitar requisição | 4 | 0 | 2 | 2 | 0 | 1 | 0 | 0 |
| SU-07 | REQ-031 OS-0417 · Adubação de cobertura · P1 MAP 1 | Requisição · REQ-031 OS-0417 Adubação de cobertura · P1 | 3 | 0 | 0 | 0 | 3 | 0 | 0 | 1 |
| SU-07det | Receber devolução | Receber devolução · REQ-031 | 3 | 0 | 2 | 1 | 0 | 1 | 0 | 0 |
| SU-07det | Entregue à ordem 100 sc lote M26-07 · separado FEF | Balanço · Entregue à ordem | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 0 |
| SU-08 | TR-0452 23/09 10:12 Transferência reforço da desse | Movimento · TR-0452 23/09 10:12 | 5 | 0 | 0 | 0 | 5 | 0 | 0 | 0 |
| SU-09 | Planejar contagem | Planejar contagem | 4 | 0 | 4 | 0 | 0 | 0 | 0 | 1 |
| VE-01 | RT-0112 Frutas Real · portal · OF-103 Reserva temp | Reserva · RT-0112 Frutas Real · portal · OF-103 | 2 | 0 | 0 | 2 | 0 | 0 | 0 | 0 |
| VE-03 | OF-103 · enviada Mamão Formosa A 2.000 kg 05/10–11 | Oferta · OF-103 · enviada Mamão Formosa A | 7 | 0 | 0 | 0 | 7 | 0 | 0 | 0 |
| VE-04 | PV-033 Rede Hortifrúti BA Mamão Formosa · B 1,2 t  | Pedido · PV-033 | 7 | 0 | 4 | 3 | 0 | 0 | 1 | 0 |
| VE-04det | Enviar revisão v3 | Revisão v3 do pedido | 4 | 0 | 1 | 3 | 0 | 0 | 1 | 0 |
| VE-04det | v2 10,0 t R$ 3,05/kg · saída do packing 28/09–04/1 | Versão · v2 | 4 | 0 | 0 | 0 | 4 | 0 | 1 | 0 |
| VE-05 | CT-201 · venda Coop Grão Sul Soja 25/26 · sc 50 kg | Obrigação · CT-201 · venda Coop Grão Sul | 5 | 0 | 0 | 0 | 5 | 0 | 0 | 0 |
| VE-06 | RC-15 PV-026 · VG-117 entrega 22/09 · recusa em LO | Caso · RC-15 | 6 | 0 | 2 | 4 | 0 | 1 | 1 | 0 |
| VEN | BT-090 · Fertisul Barter · liquidação em produto S | BT-090 · Fertisul | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0 |
