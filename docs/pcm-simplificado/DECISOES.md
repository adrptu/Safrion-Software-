# Decisões · PCM simplificado v2

Rótulo: **especificado**. Abreviações: as da `ESPECIFICACAO.md`.

Cada decisão foi tomada sem o proprietário, dentro da autonomia técnica e de produto delegada aos agentes (DEC-2709-01; RETOMADA-NUVEM, DECISOES-DELEGADAS-20261003). O Codex revisa sem bloquear (AGENTS §3.5).

Formato: o quê · por quê · alternativa descartada · como reverter.

A v2 muda D-04, D-07, D-09, D-10, D-15, D-19, D-20, D-22, D-28, D-30 e D-31, e acrescenta D-33 a D-49 (§6), pela revisão adversarial (ESPECIFICACAO, Anexo).

## 1. Base da escolha
- **Empate dos juízes:**
  - Juiz 1: "ordem" 40 · "ativo" 37 · "papel" 34,5.
  - Juiz 2: "ativo" 40 · "ordem" 37 · "papel" 34,5.
  - Soma: "ordem" 77 · "ativo" 77 · "papel" 69.
- **Síntese (D-06):**
  - do "ativo", a estrutura: master-detail com página do ativo, um comando de condição, nada ao lado do Kanban, consolidação antes do 1a;
  - do "ordem", a fila transversal (hoje "Sem ordem") e a calibração no CD-03;
  - do "papel", os tipos de tarefa, "Peças retiradas", "Aguardam você" e "Esta semana".
  - Os enxertos de cada juiz estão no §4.

## 2. Decisões que mudam decisões anteriores do proprietário sobre o menu
Todas são **mudança de decisão anterior a pedido de 05/10**. Pedido literal: "faça o melhor num só". Nenhuma vale como aprovação do dono. O Codex registra os três pedidos (01/10, 02/10, 05/10) antes do S1 (ESPECIFICACAO §0.2).

| ID | Decisão anterior (fonte) | O quê | Por quê | Alternativa descartada | Como reverter |
|---|---|---|---|---|---|
| D-01 | 01/10: Manutenção volta ao menu, abaixo de Agrícola, com MA-01..05 (UI:32) · 02/10: PM como 1º item (UI:33) | **Muda decisão anterior a pedido de 05/10.** O grupo Manutenção passa a ter 1 item, "Manutenção" → `MA.dc.html`. A posição de 01/10 fica | 6 itens + faixa de 5 telas = a queixa "telas e menus demais"; 6 lugares levavam às mesmas telas | manter 2 itens (Ordens · Planos) | acrescentar itens ao grupo em `MENU2` (UI:39-40) apontando para `MA#vis=…`; nenhuma tela muda |
| D-02 | 02/10 (a): "Planos de manutenção" como 1º item (UI:33; M:2-11) | **Muda decisão anterior a pedido de 05/10.** Planos vira a 4ª visão da tela `MA`. A função (cadastro versionado, gatilhos, tolerância, checklist, peças, tempo, especialidade) fica inteira | plano é planejamento de uso raro; um item próprio repete a entrada | 2º item de menu "Planos de manutenção" | 2º item → `MA.dc.html#vis=planos` (1 linha em `MENU2`) |
| D-03 | 02/10 (a): PM "em 3 etapas como os Planos agronômicos" (M:2, 730) | **Muda decisão anterior a pedido de 05/10.** Sem indicador de etapas: lista → detalhe → "Publicar vN" | "Escolha o plano" é a lista, e a etapa 3 vira "Ver versões" sem rascunho (M:985-987): não são etapas | manter o indicador só como informação | reativar `steps_state(PM_N)` no detalhe do plano |
| D-04 | 02/10 (b): MA-03 renomeado "Vencimentos e paradas" (UI:33) | **Muda decisão anterior a pedido de 05/10.** A tela deixa de existir; vencimentos sem ordem e achados formam a visão "Sem ordem". O princípio dele, "um nome por coisa", fica e vale também para visões, painéis e app | "paradas" significava impacto na produção, não parada da máquina; a mesma grade estava no PM | visão "Vencimentos" separada de "Achados" | separar a visão em duas pelo filtro Tipo |
| D-05 | 03/10 (UX-ACAO-UNICA-20261003): telas irmãs da Manutenção ganham a faixa "Telas da manutenção" (UI:79-89; M:32-36) | **Muda decisão anterior a pedido de 05/10**, só para a Manutenção. A faixa sai e o seletor de visão a substitui. Estoque e Irrigação não mudam aqui | com uma tela, a faixa repetiria o seletor; a de hoje parece processo e tem pendências fixas | manter a faixa com as 4 visões | — (sem tela irmã, não há o que voltar) |
| — | 25/09: menu vigente Mapa · Cadastros · Agrícola · Suprimentos (UI:31; PRD 71.6) | **Não muda.** A Manutenção continua onde a decisão de 01/10 a pôs | — | — | — |

## 3. Decisões de desenho (delegadas; o Codex revisa)

| ID | O quê | Por quê | Alternativa descartada | Como reverter |
|---|---|---|---|---|
| D-06 | Síntese no empate (§1) | os dois vencedores perdiam funções que o outro mantinha (F27, F48, F95, F101) | escolher um só por desempate arbitrário | — |
| D-07 | 4 visões; "Sem ordem" é visão própria, nunca bandeja sobre o Kanban | R01 da v0: nada que pareça 6ª fase; separa planejamento de execução | bandeja acima das 5 colunas ("ordem"); faixa no topo de Ativos (juiz 2) | mover "Sem ordem" para um bloco de Ordens, fora do modo Kanban |
| D-08 | Gerar a preventiva continua decisão do PCM ("Gerar N ordens preventivas"); a janela gerada não muda (DM:363) | regra de domínio (PCMS §2.2 passo 1); o pedido é de tela; a PCMS C2 depende da janela 24/09 da OM-0235 | geração automática na antecedência ("papel"); janela gerada já sem conflito (mudaria a PCMS C2) | FORA-DE-ESCOPO §1 |
| D-09 | Entrada de problema = **Achado**, com Origem (Relato · Inspeção · Alerta · Checklist da OM) e Componente; IDs SM, INSP e NC mantidos; prefixo dos novos pela tabela da D-48 | PRD 54 chama de achado; "Solicitação" colide com "solicitação de compra" (SC) | "Solicitação de manutenção (SM)" | trocar o rótulo; os IDs não mudam |
| D-10 | Condição: um painel (Bloquear · Restringir com prazo · Encerrar restrição; CMD-18). "Declarar apto" (CMD-19) fica só no painel da OM, em Em conferência, com teste válido para o risco. Quem age: Otávio ou o responsável técnico do ativo | uma instância por efeito; quem decide a aptidão vê o teste sem trocar de tela; o PRD l.2789-2790 dá o comando ao responsável técnico | "Liberar" no painel Condição e na página do ativo ("ativo"); só Otávio (v1) | pôr "Declarar apto" no painel Condição, exigindo a OM com teste |
| D-11 | Tipo de tarefa no plano: Serviço · Verificação · Medição · Teste. "Não feito" → OM de Pendência (como hoje); "Não conforme" e "Não foi possível verificar" → achado. Migração: tarefa texto → `{t, tipo:'Serviço'}` | o PRD 54.2 l.8371 vale para verificação; "Conforme" não serve para "Trocar filtro"; mantém DM:441-443 e `ma_correcoes_om_test` | só as 4 respostas do PRD para tudo ("ordem", "ativo") | tipo único "Serviço" no plano |
| D-12 | Teste é tarefa antes de Concluir; aptidão em Em conferência | PRD l.7738 ("conclusão exige teste") e regra do MA-04det (M:644). O PRD l.7740 diz "aguardando teste" em Em conferência: contradição registrada para o Codex | teste em Em conferência | Codex decide na revisão da v3.10 |
| D-13 | "Peças retiradas" (Recondicionar · Garantia · Sucata, com responsável) separado das sobras de material novo | a peça retirada nunca volta ao livre (PCMS-M24); preserva a F91 | fundir com a devolução do Estoque ("ordem", "ativo") | — |
| D-14 | Ativo e plano como páginas de detalhe; OM, achado, vencimento, condição e leitura como painéis | o ativo tem 6 blocos e o plano tem serviços: não cabem em 460 px | ativo como painel ("ordem") | — |
| D-15 | Modo "Abastecimentos" na visão Ativos, com "Salvar e registrar outro": chave nova, campos limpos, só a data fica | os três desenhos perdiam a lista transversal (F95) até o Bloco 6; transcrição de tíquetes do comboio; manter lote ou leitura seria último valor (AGENTS §3.3) | consulta só por ativo | tirar o modo quando o diesel virar lote (Bloco 6) e o razão estiver em Estoque › Movimentos |
| D-16 | Calibração fica no CD-03, como aferição | é usada por Irrigação, Colheita e app; não é preventiva; mexer no CD-03 amplia o escopo | serviço de plano com gatilho em dias ("ativo", "papel") | — |
| D-17 | Cartões: Sem ordem 3, Ordens 4, Ativos 4, Planos 0. "A liberar" sai da PCMS §7 (o chip já conta); KPI-SUP-06 fica em Ordens | PRD l.8505; alinhado à PCMS §7 (juiz 2) | KPI-SUP-06 só no Estoque ("ordem") | — |
| D-18 | Horas de oficina obrigatórias: chip "Previsto (x h)" ou digitadas | "vazio = previsto" (DM:421) é valor implícito; custo e MTTR dependem disso | manter o vazio | voltar ao vazio = previsto |
| D-19 | Abastecimento: lote pré-escolhido só se for o único elegível; operador da alocação do ativo no dia (AL), corrigível, e sem pré-escolha se não houver; `por` gravado à parte; data corrigível | não é "último valor"; quem transcreve ≠ quem abasteceu (PCMS-G01); tíquete atrasado tem data própria | operador = Ver como ("papel") | — |
| D-20 | Ver como (simulação): Otávio · Zé · Ana, com a matriz papel × comando (ESPECIFICACAO §3.1); reaproveita o componente da SUP §2.2 ou do CTL-3; Otávio entra no CD-04 no S1 | uma solução por problema (AGENTS §3.4); sem papel, a tela mistura PCM e mecânico | perfil fixo "Ana · Gestora" (UI:258) | — |
| D-21 | Ordem única: S1 → S2 → 1a → S3 → 1b → 1c → S4 | o S1 reduz o 1a de 6 telas para 1; o 1b reescreve o painel uma vez só; passos pequenos | consolidar junto com o 1b ("ordem"); consolidação como "novo 1a" ("papel") | Codex reordena; cada passo é independente |
| D-22 | Até o 1b/1c, o painel mantém "Solicitar compra", "Registrar recebimento", "Resolver sobras", "Liberar mesmo assim" e "Mover mesmo assim". Habilitados para Otávio, com o rótulo "(simulado · Compras recebe no 1c)" ou "(simulado · papel do Almoxarifado)", e a mensagem diz isso | sem eles, a OM com falta de peça ou sobra fica sem saída (juiz 2); sem papel habilitado, a saída sumia (PCM-R01) | tirar tudo no S1; pôr Rui no Ver como até o 1b | — |
| D-23 | "Marcar pendentes como feitas" sai já no S1 | PRD 54.2 l.8371 (nunca pré-marcar); AUD §6 | esperar o 1b | — |
| D-24 | Arquivos antigos (PM, MA-01..05, MA-04det) viram páginas de redirecionamento, fora do canvas e do Índice (lista em `build.py`, como l.23-24) | F5, favoritos e links antigos não quebram; `_wh` exige `$preview` (`build.py:28-32`) | apagar os arquivos | — |
| D-25 | Dados fixos saem sem substituto imediato: Pareto, utilização por grupo, Agenda, Elegível, "Tanque Sede 38 %", consumo fixo | parecem vivos e não são (inventário §2.E) | manter até haver dado | FORA-DE-ESCOPO §2 |
| D-26 | Aceite com IDs AC-PCM-nn | "PCMS-nn", sugerido pela tarefa, colide com as regras PCMS-Mnn da pcm-suprimentos | PCMS-nn | renomear |
| D-27 | Verbos: "Gerar" (preventiva, do plano) × "Criar" (corretiva, do achado); "Fechar sem serviço" (achado) × "Encerrar ordem" (OM) × "Encerrar restrição" (condição); "Vincular" (achado → OM; ativo → plano); "Mover janela" | um verbo por efeito; "Encerrar" tinha dois sentidos | "Criar" para as duas ordens | — |
| D-28 | Prazo de Sem ordem por uma base só: o início da janela (vencimento − tolerância), horizonte de 10 d (DM:20). Cartões "Vencidas sem ordem" e "Em breve sem ordem"; filtro Vencidas · Até 10 d · Até 30 d, cumulativo; gerar só em Vencida ou Em breve | quatro horizontes (7 d, 10 d, em breve, semana) davam números diferentes para a mesma pergunta (PCM-R18, R10) | cartão "Vencem em 7 d" (v1); "Janela abre em 7 d" | FORA-DE-ESCOPO §1 (antecipação) |
| D-29 | Corretiva nasce sem peças até "Incluir peça" (PCMS-M20, Bloco 2) | o 1b reescreve peças como lote; incluir antes seria reescrito | incluir peça no S1 | antecipar M20 para depois do 1b |
| D-30 | Repetição antes do 1b: barrada por estado (achado já vinculado devolve a mesma OM) e pela chave em `c.recibos` da manutenção. A chave é gerada por registro e renovada depois de cada comando gravado, inclusive em "Salvar e registrar outro". No 1b: `cenMudar(self, fn, cmd)` (PCMS-G04) | duplo toque cria 1; uma chave por abertura do painel engoliria o 2º tíquete (PCM-R06) | uma chave por abertura do painel (v1) | — |
| D-31 | O achado vinculado, ou que originou a OM, vira uma Verificação "Verificar: <sintoma>". Achados do mesmo ativo e componente viram uma Verificação só. O achado de origem da OM que trata a condição se resolve pelo teste válido dela (Teste Aprovado ou Medição Conforme). Vale para o seed | PRD 54.5 l.8404 (concluir não resolve o achado); sem repetir o mesmo fato três vezes na OM-0233 (PCM-R19, R18) | resolver o achado no Concluir; uma Verificação por achado (v1) | — |
| D-32 | Estado sem repetição: selo do cabeçalho só com impedimentos; contador por visão com o que espera quem vê; cartão de contagem é o filtro | evitar o mesmo número em três lugares | selo com tudo ("2 vencidas · 3 sem ordem") | — |

## 4. Enxertos dos juízes

| Juiz · enxerto | Decisão | Fundamento |
|---|---|---|
| J1 · "Aguardam você" e "Esta semana" agrupada por dia | aceito | ESPECIFICACAO §3.3 |
| J1 · tipos de tarefa; F81 mantida; não conforme → achado | aceito | D-11 |
| J1 · um comando de condição; bloco do ativo só leitura; "Declarar apto" só no painel da OM | aceito | D-10 |
| J1 · cartões = filtro; primária desabilitada com motivo | aceito | §3.1, §3.2 |
| J1 · consolidação antes do 1b/1c, como "novo 1a" | ajustado: S1 antes do 1a, sem ser o 1a | D-21 |
| J1 · só o bloco da fase aberto | aceito | §3.3 |
| J1 · Peças retiradas | aceito | D-13 |
| J1 · "Salvar e registrar outro" | aceito, no modo Abastecimentos | D-15 |
| J1 · MB-09 no ativo herdado, "Não opere" | aceito | §3.7 |
| J2 · tipo de tarefa com migração `{t, tipo}` | aceito | D-11 |
| J2 · Peças retiradas | aceito | D-13 |
| J2 · calibração no CD-03 | aceito | D-16 |
| J2 · coluna Consumo e filtro "Desvio de consumo" | aceito | §3.4 |
| J2 · faixa "Achados sem ordem" no topo de Ativos | ajustado: virou a visão Sem ordem | D-07 (não mistura controle e planejamento) |
| J2 · lote único pré-escolhido; operador da alocação; `por` à parte | aceito | D-19 |
| J2 · chave e versão por comando, nunca `c.rev` | aceito | §3.1; D-30; D-46 |
| J2 · rótulo "Declarar apto" | aceito | D-27 |
| J2 · "Esta semana"; cartões de Ordens = PCMS §7 | aceito | D-17 |
| J2 · atalhos de janela; teste "5 colunas" | aceito | §3.3; AC-PCM-04 |
| J2 · guarda de sequência (compra, recebimento, sobras) | aceito | D-22 |

Funções que os juízes apontaram como perdidas e onde ficaram:
- F95: D-15;
- F27: Sem ordem até 30 d e bloco O que vence;
- F48: Sem ordem, Tipo = Achados;
- F31/F32: D-08;
- F81: D-11;
- F91: D-13;
- F101/F99: coluna Consumo e filtro;
- F68/F69/F78: D-22.

## 5. Pendências

| O quê | Quem | Impede |
|---|---|---|
| Registrar como pedidos os de 01/10, 02/10 e 05/10 sobre a Manutenção (hoje só em UI:31-34 e M:2-11) | Codex escreve, Claude revisa | a mudança de menu do S1 |
| Proposta à v3.10: "MA-01..05 como famílias da tela MA" (precedente 71.6, l.10361, 10368); MA-02 com 4 abas (PRD 54.1 l.8365) → Sem ordem + detalhe do ativo; MB-09 → "Máquina" e painel da OM | Codex autor, Claude revisor | integração no software real |
| Contradição PRD 47.5 l.7738 × l.7740 sobre o momento do teste (D-12) | Codex | nada no protótipo; vale D-12 até a decisão |
| PCMS §3.1 (l.185, 190, 207): o 1a leva `achados`, `leituras` e `recibos` no lugar de `ach`; a versão do registro passa a `o.rv` (D-46, D-47) | autor da PCMS (Claude), revisor Codex | o 1a |
| Alinhar AL (OS-0420 em 28/09) com a O.S.: conferir `os_cenario_test` e `tabelas_os_test` no S1 | Claude (S1) | o S1 |
| Ordem entre frentes (CTL-3 em andamento, SUP, BEN, PCMS) | Codex | início do S1 |
| Conferir na página as citações de benchmark marcadas "a conferir" (Aegro suporte, Fleetio inspeções, módulos do Maximo) | Codex (produto) | entrada no PRD |
| Pendências da PCMS (D1-D5, P1-P10) continuam | dono / Codex | os passos 1b, 1c e Blocos 2-7 |

## 6. Decisões da revisão v1 → v2

| ID | O quê | Por quê (achado) | Alternativa descartada | Como reverter |
|---|---|---|---|---|
| D-33 | Matriz papel × comando (ESPECIFICACAO §3.1). Bloquear, Restringir, Encerrar restrição e Declarar apto: Otávio ou o responsável técnico do ativo. "Registrar e bloquear" no Registrar achado | sem matriz, os passos-ponte ficavam desabilitados para todos e o mecânico não bloqueava (PCM-R01, R11); CMD-18/19 l.2789-2790 | só Otávio decide a condição | restringir as linhas da matriz |
| D-34 | Saída para Apto: (1) a OM que trata a condição (registrada no painel Condição ou criada do achado de origem) ganha "Teste do reparo" não excluível se o ativo Bloqueado não tem Teste; no Restrito, Medição Conforme vale; (2) Encerrar exige "Declarar apto" ou "Manter · motivo"; (3) "Encerrar restrição" sem OM aberta, com motivo e evidência; a restrição tem prazo; (4) "Incluir tarefa" em Corretiva e Pendência. Encerrar com regra única: sobras, peças retiradas com destino, decisão de aptidão | sem Teste, a OM-0228 e as corretivas novas deixavam o ativo preso para sempre (PCM-R02, R01); peça recuperável sumia (R14); PRD l.7720 (prazo), l.2790 (teste válido para o risco) | Teste em toda OM do ativo restrito; exigir sempre Teste no Restrito | tirar o item (3) e voltar a exigir OM |
| D-35 | Vincular só a OM em A liberar, Liberadas ou Em execução (com o selo "Tarefa nova"); o achado volta a Sem ordem ("Voltou da OM-xxxx") se a OM é encerrada ou cancelada sem Conforme | "OM aberta" incluía Em conferência, e o achado sumia (PCM-R03, R04); M:281 já aceita Em execução | só A liberar e Liberadas | — |
| D-36 | Teste com tentativas `{r, evid, por, em}`, só por acréscimo; Concluir exige a última Aprovada; OM-0233 semeada com a 1ª Reprovada e com as peças retiradas | a 2ª resposta apagava a reprovação, o retrabalho e a reincidência (PCM-R08, R05; PRD l.7738) | uma resposta por tarefa | — |
| D-37 | Executante obrigatório para liberar, sugerido pela habilitação da especialidade no CD-04 (Mecânico → NR-12; Eletricista → NR-10); OM-0233 e OM-0230 → Zé; OM-0228 → João; fila pela janela e depois pela criticidade | sem executante, "Aguardam você" e a Minha fila ficavam vazias; Zé (NR-12) não pode fazer serviço elétrico (PCM-R09, R12) | Zé na OM-0228 "com motivo"; "Equipe elétrica" sem pessoa | executante opcional com aviso |
| D-38 | Conflito calculado por uma função: horas livres do recurso no dia (jornada AL − alocação firme ou condicional em O.S.) menores que o tempo previsto. Fonte: AL embutida no build. "Mover janela" é o único comando de janela, com "Próxima sem conflito" (1º dia livre em até 7 d). Fora da tolerância: aviso com motivo até o 1b; gerência no 1b. `o.vencOrig` preservado. AL ganha OS-0420 em 28/09 | conflito fixo só na OM-0234 (PCM-R12, R03, R13); dois comandos de janela com travas diferentes (PCM-R13); a trava de tolerância prendia a OM já vencida | conflito pelo dia inteiro (marcava o Trator 03 com 5 h livres); trava de tolerância (impede mover uma OM vencida); devolver a OM para A liberar | voltar ao conflito registrado só na OM-0234 |
| D-39 | Chip "Canceladas" fora das 5 fases e do Kanban, desde o 1b | a OM cancelada sumia (R15; PCMS-M19 l.325) | — | — |
| D-40 | Leitura: na conclusão, a leitura menor recusa o Concluir (como DM:420) e a implausível dá aviso; histórico em `c.leituras`; data corrigível; leitura com data anterior entra no histórico sem pedir troca | a v1 deixava a conclusão fechar o ciclo na escala errada e deslocar referências (PCM-R05, R02); tíquete atrasado virava troca falsa (PCM-R14); o bloco Leituras não tinha fonte (PCM-R21) | leitura a confirmar também na conclusão (v1) | — |
| D-41 | Marco do vínculo: pré-preenchido da última OM encerrada do mesmo serviço (ou de um que o "cumpre também"), com origem à vista, corrigível com motivo; corretiva nunca serve | herdar de qualquer OM, só leitura, calculava o vencimento errado (PCM-R04) | só leitura | pedir sempre data e leitura |
| D-42 | App: Ver como Marcos · Zé (`c.app.usuario`); a Minha fila do operador não mostra OM; os comandos seguem `cenSinal`, com chave no aparelho e revalidação de fase e `o.rv`; OM mudada vira "Conflito a resolver · Otávio". MB-04 "Equipamento" grava achado | o app tinha um usuário fixo e não tratava sem sinal (PCM-R10); a falha relatada no MB-01 nunca chegava à Manutenção (PCM-R07) | perfil fixo | — |
| D-43 | Custo por período (Mês atual · 30 d · 12 m), rotulado "das OMs encerradas no sistema", com o "em andamento" separado; histórico encerrado sintético a partir de `VINCULOS.ult`; cartão "Aptos agora"; disponibilidade 30 d e custo por hora operada "não calculável" | custo de 12 m fixo e subestimado; "Disponibilidade 14 de 16" lido como % (PCM-R11, R22, R23) | "não calculável" até o Bloco 7 | tirar o histórico sintético |
| D-44 | Visão "Sem ordem" (`#vis=semordem`); bloco da OM "Janela e equipe" | "A programar" × "A liberar" e "Programação" com dois sentidos (PCM-R20) | manter "A programar" | renomear |
| D-45 | Componente no achado (Motor · Hidráulico · Elétrico · Transmissão · Rodado e freios · Órgão de trabalho · Outro); soma só com mesmo ativo e mesmo componente, com "Somar / Registrar novo" | a regra de soma pedia um campo inexistente (PCM-R16, R16) | somar também pela origem | tirar o campo e não somar |
| D-46 | Versão do registro = `o.rv`; `o.ver` continua a versão do plano | colisão de nomes vinda da PCMS §3.1 (R17); `ma_planos_test:69-70` depende de `o.ver` | renomear a versão do plano | — |
| D-47 | Estado `v=3` no S1 e `v=4` no S2; `c.achados` substitui `c.ach`; estado antigo volta ao seed (DM:272) | estado salvo `v=2` quebraria a leitura de `c.achados` (R08) | migração campo a campo | — |
| D-48 | Prefixo por origem: Relato e Alerta → SM; Inspeção → INSP; Não conforme do checklist da OM → NC; número = maior do prefixo + 1 | "o prefixo da origem" não estava definido, e um contador ingênuo repetia INSP-105 (R25) | um prefixo só | — |
| D-49 | Responsável técnico nos dados de manutenção do ativo (DM), semeado do `RESP` de M:126 (a01, a02, a05 → Zé; a11, a15, a12 → Equipe elétrica; demais → Otávio); editável no painel Condição; só leitura no CD-03 (S3) | a fonte era um mapa local da tela que sai (PCM-R17) | campo no CD-03 já no S1 (amplia o escopo) | mover para o CD-03 no S3 |
