PROJETO: Safrion (Do Talhão à O.S.)

CONTEXTO
Este arquivo reúne tudo o que foi definido na conversa: as diretrizes permanentes de UX, UI e design system (seção 0), os princípios de produto (Anexo A, P01–P66) e os achados e as funcionalidades novas para o protótipo (EX-01 a EX-50).
ANEXOS QUE O PROPRIETÁRIO ENVIA JUNTO (leia antes de começar; cada prompt próprio prevalece sobre o resumo do seu EX):
- prompt-safrion-raio-x-do-alvo.md e pragas-no-tempo.html (EX-42 e EX-43);
- prompt-safrion-mapa-ux.md e anexo-mapa-analise.md (EX-44);
- prompt-safrion-resolve-em-1-clique.md e anexo-insumos-analise.md (EX-45);
- prompt-safrion-entrada-acoes-revisao.md, anexo-varredura-achados.md, anexo-robo-varredura.html e anexo-robo-resumo.py (EX-46, EX-47 e EX-48);
- prompt-safrion-padrao-listas.md, padrao-listas-safrion.html, anexo-robo-v4.html e anexo-robo-v4-resumo.py (EX-49);
- prompt-safrion-telas-ocultas.md e anexo-telas-ocultas.md (EX-50).
Se algum faltar, peça ao proprietário; não reconstrua o conteúdo.

Uma sessão do Claude, fora do repositório, analisou o protótipo publicado "Do Talhão à O.S." (https://claude.ai/artifact/HqspGRcrX1wcayCVMe9emm, versão 1792123204-c09d, 16/10/2026).
- Telas: foram abertas 148 no navegador. De cada uma, no estado inicial, foram extraídos botões, campos, tabelas e texto.
- Modais: um robô clicou em 370 ações e capturou 83 modais e painéis, entre eles 64 formulários com 339 campos editáveis. Ele clicou em uma ação por verbo em cada tela, na primeira linha clicável de cada tabela e nos menus ⋯.
- Segunda varredura, na versão 1792184197-5a81: um robô novo abriu as 148 telas, clicou em 488 ações de primeiro nível e mediu campos (origem do valor, teclado, unidade, atalho de data), ações nas linhas e cartões, lotes e primárias; cinco revisões por área leram o resultado (EX-46 a EX-48). Os mapas e o fluxo insumo × estoque × compra foram lidos no código (EX-44 e EX-45).
- Reprodução manual: foram reproduzidos à mão os riscos mais graves (PL-04 "Liberar prontas", CA-01 "Liberar selecionadas") e os fluxos OS-0421, MB-03, CA-02, SAF e CO-03.
- O.S. por papel: as 21 O.S. das duas fazendas tiveram o detalhe aberto e as contas refeitas, cruzando com o app do operador (MB-01, MB-02det, MB-05), as fichas da OS-0424 e o almoxarifado (SU-07, SU-07det).
- Revisão: cinco revisões por área avaliaram cada tela e cada modal com duas lentes:
  (1) simplicidade e produtividade, contra os princípios P01–P66 do Anexo A;
  (2) valor de gestão, como um painel de agrônomo, gerente de PCP, engenheiro agrícola, engenheiro de produção, PCM, suprimentos, comercial e controller, com a IA como camada de automação.
- Limites:
  - o robô não preencheu nem enviou nenhum formulário;
  - todos os modais têm uma etapa só;
  - onde não está escrito "medido", cliques e campos são estimativas;
  - os dados sintéticos foram tratados como intencionais;
  - a versão do repositório pode estar à frente da publicada.

OBJETIVO
Validar esta análise com o Codex, corrigir o que estiver errado, completar o que faltou e implantar o que for aprovado. A meta é levar o protótipo à excelência: cada módulo sustentando as decisões que melhoram o resultado do agricultor (produtividade, custo por saca, margem, operação na janela, conformidade), com o mínimo de cliques, digitação, etapas e burocracia.
A análise é insumo, não requisito. PRD, NAV/DS, protocolo e decisões registradas prevalecem.
O objetivo não é um software só bonito: é um sistema de gestão agrícola excepcionalmente simples, intuitivo, rápido e eficiente, com a excelência comprovada por indicadores objetivos de usabilidade e produtividade.

0. DIRETRIZES PERMANENTES DE UX, UI E DESIGN SYSTEM
Valem para toda decisão de UX, UI e design system, no protótipo e no software real. A avaliação de 16/10 já as registrou no PRD (cap. 4, 55, 64, 74 e 75) e no AGENTS §3.3. Confira e referencie a fonte vigente; não crie lista paralela.
- ISO 9241-210 (design centrado no usuário) é o método central: o software se adapta à maneira como o usuário trabalha, e não o contrário. Cada fatia passa pelas quatro atividades: contexto de uso, requisitos do usuário, solução e avaliação com usuário real.
- As 10 heurísticas de Nielsen (NN/g) são o critério de projeto e de revisão de toda tela. A gravidade 0–4 da NN/g se liga ao S1–S4 do PRD 22.1. Prioridades:
  - menos carga cognitiva;
  - menos cliques e digitação;
  - navegação intuitiva;
  - consistência entre telas;
  - prevenção de erro;
  - retorno imediato de cada ação;
  - eficiência para iniciante e para quem usa muito.
- O design system é próprio e segue as práticas do IBM Carbon:
  - navegação e organização da informação;
  - tabelas, filtros e formulários;
  - painéis e visualização de dados;
  - botões, menus e componentes interativos;
  - hierarquia visual e tipografia;
  - acessibilidade e responsividade.
  Use o Microsoft Fluent 2 onde ele for melhor (por exemplo, a barra de comandos com ⋯). Não copie o visual de nenhum dos dois: a identidade é do Safrion, moderna e funcional.
- O processo é o Double Diamond: Descobrir → Definir → Desenvolver → Entregar, encaixado no ciclo da fatia. Antes de desenhar ou implementar uma tela, entenda o problema, o contexto operacional e o fluxo real do usuário.
- Simplicidade operacional (regra TELA-01): cada tela responde em segundos a três perguntas:
  1. O que está acontecendo? (estado em palavras)
  2. O que exige minha atenção? (com quantidade e motivo)
  3. Qual ação devo executar agora? (uma primária com verbo)
  A informação certa aparece no momento certo, com a ação certa. A complexidade fica dentro do sistema, não com o usuário.
- Indicadores de excelência. As metas são iniciais e só valem depois de validadas com usuários reais:
  - sucesso na tarefa essencial ≥ 95 %;
  - tempo por tarefa abaixo da linha de base e caindo a cada versão;
  - interações por tarefa nunca acima da versão anterior no mesmo cenário;
  - erros por tarefa ≤ 0,2;
  - facilidade de aprendizado: tempo da 2ª execução ÷ tempo da 1ª ≤ 0,7;
  - satisfação: SUS ≥ 80;
  - acessibilidade: 0 violação séria de WCAG 2.2 AA;
  - desempenho percebido: INP ≤ 200 ms, LCP ≤ 2,5 s e app sem sinal sem travar.
- Perfis e plataformas:
  - a experiência se adapta a gestores, agrônomos, PCP, almoxarife, caldeiro, operadores, líderes e equipes de campo;
  - os perfis usam as mesmas telas com permissões diferentes, sem menus por perfil (P65);
  - a excelência vale para o desktop e para o app de campo.
- Limite: não elimine funcionalidade necessária só para reduzir cliques. Rastreabilidade, segurança, integridade dos dados e regras de negócio ficam.

1. PREPARAÇÃO
- Carregue as skills safrion-equipe, master-detail-ux, ux-essencial, minimalismo-essencial, tabelas-interativas, agro-gestao-conhecimento, dev-ciclo-completo e dev-testes.
- Retome pelo registro vigente: AGENTS.md, docs/STATUS.md, checkpoint da issue #1 e docs/parceria/protocolo.md.
- Leia também a "Avaliação de UX e plano priorizado" de 16/10 (UX-01..UX-14 e decisões de 16/10). Os itens abaixo citam essa avaliação, sem repeti-la.
- Confira se a versão do protótipo no repositório é a publicada (1792123204-c09d). Se o repositório estiver à frente, valide cada achado na versão atual.
- Não passe na frente de risco crítico, correção ou revisão devolvida, nem interrompa autoria ativa. Os itens da Onda 0 são riscos e entram na fila como tal.

2. DIAGNÓSTICO
Notas de 0 a 5 (valor de gestão / simplicidade):
- Agronomia 4 / 3
- Cadastros 3,5 / 3,5
- Planejamento 4 / 2
- Entrada e pendências 3 / 3
- Painéis 3 / 2
- Execução de O.S. 3 / 2
- App de campo 3 / 3
- Irrigação 4 / 3
- Suprimentos e compras 3,5 / 2,5
- Estoque 4 / 2,5
- Manutenção 2,5 / 3
- Colheita e pós-colheita 3 / 2,5
- Comercial e logística 3 / 2
- Gestão e finanças 3,5 / 3
- Plataforma 3 / 3

Leitura:
- Forte em rastreabilidade, integridade de saldo, cálculo com origem, bloqueio que explica causa e responsável, e automação que propõe sem executar.
- Formulários:
  - todos têm uma etapa só;
  - metade dos 339 campos já vem preenchida;
  - os campos numéricos usam teclado decimal e mostram a unidade.
- Fraco em:
  (a) ações de risco que executam em lote ou com 1 clique, sem motivo nem alçada;
  (b) duas gerações de telas e formulários convivendo;
  (c) dados que se contradizem entre telas e dentro dos modais;
  (d) poucos indicadores de resultado (custo/sc, margem por talhão, % na janela, ha/h, paradas, cobertura, MTBF);
  (e) digitação de dados que o sistema já tem;
  (f) primária ausente, genérica ("Salvar" em 34 de 64 formulários) ou ativa só para recusar depois do clique.

Leitura pelas 10 heurísticas de Nielsen (achados que tocam cada uma):
- H1 Visibilidade do estado.
  - Forte: faixa VEIO DE → FALTA → PRÓXIMA AÇÃO.
  - Lacunas:
    - primária que falha depois do clique (EX-05);
    - recibo de "volta completa" com 14 % da volta (EX-36);
    - "faltam 15 L" ausente no app (EX-38).
- H2 Correspondência com o mundo real.
  - Forte: unidades do campo.
  - Lacunas: falta galão por carga, g por cova e sementes por metro (EX-39); códigos internos na tela (EX-03).
- H3 Controle e liberdade: ações de risco sem motivo, alçada ou Desfazer (EX-33); medidas já marcadas (EX-34).
- H4 Consistência e padrões: dados que se contradizem (EX-01), telas e formulários duplicados (EX-02), vocabulário (EX-03), "Salvar" genérico (EX-37), componentes (EX-41).
- H5 Prevenção de erro: aprovação em lote (EX-32), listas sem filtro (EX-35), cálculos divergentes e dupla alocação (EX-38), clima e calibração (EX-08).
- H6 Reconhecer em vez de lembrar: contexto não herdado (EX-04) e texto livre onde cabe lista (EX-37).
- H7 Flexibilidade e eficiência:
  - turno, abastecimento, NF, romaneio e safra nascendo preenchidos (EX-06, EX-09, EX-11, EX-12, EX-14);
  - visões salvas (EX-31);
  - busca global e atalhos (UX-10, UX-11).
- H8 Estética e minimalismo: painéis por exceção (EX-26), consolidação (EX-02), ajustes menores (EX-40).
- H9 Reconhecer e recuperar erro: bloqueio com motivo antes do clique (EX-05) e conferência por exceção (EX-10).
- H10 Ajuda: sem achado novo além do UX-12.

Por perfil e plataforma:
- agrônomo: caixa única de decisões (EX-31, UX-05, UX-06);
- almoxarife, caldeiro, operador e líder de campo: ficha por papel (EX-39);
- o app de campo hoje cobre só a pulverização. Plantio, adubação, fertirrigação, caldeiro e líder não têm fluxo móvel (EX-39).

3. PRESERVAR (não mexer sem motivo)
- Faixa "VEIO DE → ESTÁ AQUI → FALTA → PRÓXIMA AÇÃO" nos detalhes. Levar para todo detalhe.
- Coluna de próximo passo com verbo e responsável ("Pesar · Lúcia").
- Formulários de uma etapa, sem wizard, com unidade junto do campo.
- Painel MIP VIS-013:
  - vistoria → receituário → O.S. em 2 toques, sem digitação;
  - só produtos registrados para cultura × alvo;
  - IRAC, faixa de bula, carência e limite por ciclo;
  - "aplicar até" calculado;
  - O.S. nascendo "A liberar".
- Bloqueio que diz causa, solução e responsável ("Liberar bloqueado: sem lote de Ureia… Quem resolve: Suprimentos").
- Automação como proposta: "prévia de emissão", "Simular… sem reservar agenda", "Proposto · aguarda PCP", "revisão sugerida, nada alterado".
- Gerar OM preventiva a partir do plano ("Gerar 3 ordens preventivas", com vencimento original preservado).
- Conciliação automática que abre só a divergência (diesel "0,7 %, tolerância 1 %"; retorno do banco com "R$ 12,40").
- Prévia de importação com "Trazer 3 mudanças / Descartar prévia" (CD-07) e importação que grava os prontos e mantém os erros (ON-01det).
- Idempotência e rastreio: "mesmo recibo RS-7741", "Duplicado · sem nova entrada", extrato imutável, estorno com vínculo.
- Cálculo com origem visível:
  - "140 − 50 − 40 = 50 t";
  - dose × área e cargas por tanque;
  - caixas ⌈12.300 × 95 % ÷ 10⌉;
  - memória de cálculo da recomendação;
  - balanço de massa do beneficiamento;
  - hidrômetro com tolerância.
- Honestidade do dado: "ausente ≠ zero", "Parcial · conferir cobertura", "(HIPÓTESE)", "sem custo realizado" em vez de zero.
- Segregação: quem estava com a custódia não confirma o próprio recebimento; quem aplica o lacre não confere.
- Offline com recibo em três estados (no aparelho, enviado, conferido) e custódia em conta fechada.

4. MELHORIAS PROPOSTAS (EX-01 a EX-50)
Os P-IDs remetem ao Anexo A (P01–P66). Os UX-IDs remetem à avaliação de 16/10. "Medido" quer dizer contado nos modais.

Onda 0 · Riscos (corrigir primeiro)

EX-32 Aprovação em lote, contra a decisão de 16/10 ("Aprovação em lote: fora, de propósito"):
  - PL-04 "Liberar prontas" liberou a OS-0430 (dessecação com defensivo) num lote de 5: "OS-0430 ✓ liberada por Ana (agrônoma)". Reproduzido.
  - CA-01: "Selecionar as 12 linhas" + "Liberar selecionadas" processa o lote; a mensagem diz "Com produto, quem libera é o agrônomo". Reproduzido.
  - IN-02 "Aprovar selecionados" mistura alçadas: inventário, política de estoque, orçamento da Direção e acesso de operador.
  - CA-03 encerra ocorrências em lote, inclusive a OC-114 "Grave" com OM ainda em execução.
  Correção: lote só para O.S. "só água" com prontidão e para itens da mesma alçada e do mesmo tipo. O.S. com produto é liberada uma a uma, com "aprovou, abre a próxima" (UX-06).

EX-33 Fricção proporcional ao risco (motivo, alçada, prévia ou Desfazer, conforme o caso):
  - Executam com 1 clique, sem motivo nem alçada:
    - CO-06det "Liberar" um lote reprovado (defeitos 103 > 86);
    - PT-04det "Recusar crédito" (diz "registrada com motivo" sem ter pedido motivo);
    - GE-05 "Emitir crédito";
    - LO-04 "Contratar" frete de R$ 1.824;
    - AG-06 "Registrar parecer", que grava uma conclusão técnica pronta.
  - SU-05:
    - "Formalizar contrato" funciona antes da aprovação da Direção, cuja alçada vai "até R$ 300 mil" numa compra de R$ 360.905;
    - "Emitir pedido" agenda emissão automática contra um contrato com tolerância "hipótese, não aceita";
    - "Confirmar fornecedor" confirmou a carga da Fertisul, quando o único pedido "A confirmar" era o PC-094.
  - Envios sem prévia: SU-04 "Enviar COT-113" vai a 3 fornecedores sem mostrar os destinatários; GE-04 manda a remessa ao banco sem prévia do total.
  - Alçada fora do lugar:
    - SU-08 "Registrar perda": quem pede escolhe o aprovador; a alçada deve sair do valor;
    - GE-08: Ana registra "Autorizado pela Direção";
    - CD-04: "Liberar O.S. (agrônomo)" é um checkbox livre. Conferir a exigência de habilitação/RT.
  - Publicações sem Desfazer (UX-04): parcelamento (PL-06 publica mesmo "aguardando aprovação"), plano, ajuste, cenário.

EX-34 Medida e evidência nunca vêm pré-preenchidas:
  - CA-03 "Evidência: Foto" marcada sem foto;
  - LO-02det "Foto do lacre anexada" marcada;
  - SU-07det "Quantidade medida" vem com 10, contra o próprio texto ("medida… não a declarada");
  - PL-02 "Realizada" pré-marcada numa pendência vencida;
  - MB-04 "Equipamento" pré-marcado, o que obriga a escolher máquina.

EX-35 Listas filtradas por contexto e por organização:
  - PT-06: o fornecedor vê usuários da fazenda (Ana, Marcos, Rui, Paula) como responsáveis possíveis. É exposição entre organizações.
  - Listas com opções que não cabem no contexto:
    - CO-06 lista lotes de insumo (F26-02, D26-11) e métodos de MIP e solo;
    - CO-02 oferece plantadeira e pulverizador para colheita;
    - PL-06 oferece variedade de mamão para soja;
    - PL-05 oferece o Trator T1 bloqueado;
    - CA-01det oferece grãos como insumo;
    - AG-01 "Programar vistoria" oferece talhões de outra fazenda;
    - EST deixa ligar a NF 4533 ao pedido PC-096 (Mamão);
    - no portal, o tipo de documento oferece "Preventiva/Corretiva".

EX-36 Integridade da irrigação:
  - IR-01 "Conferir medição": com −3,8 % de desvio (tolerância 3 %), a ação continua "Validar e encerrar". Deve virar "Aceitar com motivo" ou "Devolver".
  - MB-08: aceita o término com 14,47 % da volta e emite o recibo "volta completa · 10,81 mm nos 80 ha". Antes do fim da volta, a ação deve ser "Término antecipado", com a área real.
  - IR-02: o plano de 2 mm por passada fica abaixo do mínimo físico do pivô (6,7 mm a 100 %).
  - IR-03det: começa às 20:02, dentro da ponta, sem aviso.

EX-38 Cálculos de execução com fonte única: O.S., app, ficha e almoxarifado mostram o mesmo número. Conferido nas 21 O.S. das duas fazendas; dose × área bate em todas, mas:
  - OS-0421:
    - A O.S. diz tanque de 3.000 L, 100 L/ha e 30 ha por carga, com Fungicida A 15 L e adjuvante 7,5 L por carga.
    - O app do operador diz 2.000 L, 120 L/ha, 16,7 ha e 8,3 L de Fungicida A, e "adjuvante fora da REQ-035 · nada com você".
    - Seguir uma ou outra muda a dose em até 20 %.
  - OS-0420/OS-0431:
    - o painel da O.S. lista MAP 11-52 250 kg/ha (25.000 kg), mas a O.S. completa e o almoxarifado usam KCl 60 % 120 kg/ha (REQ-037);
    - o TS nematicida (abamectina 5,2 L) está na recomendação e não tem requisição.
  - Adjuvante da OS-0421: 47,5 L consumidos sem requisição.
  - Calibração:
    - o bico 110-015 a 3 bar entrega cerca de 0,59 L/min, e 100 L/ha a 8 km/h pede cerca de 0,67 L/min por bico (supondo 50 cm); isso dá −11 % de calda;
    - a ficha deve mostrar a vazão alvo por bico e pedir o teste antes da 1ª carga.
  - Entrega em embalagem fechada e pela necessidade:
    - hoje há defensivo entregue fracionado (abamectina 31,4 L, tebuconazol 63,99 L, glifosato 147,93 L);
    - e adubo entregue acima da necessidade (OS-0417: 100 sc para 70).
  - Saldo para terminar: a OS-0421 tem 65 L com o operador e precisa de 80 L para os 160 ha. Os 15 L a entregar aparecem só na O.S. completa, não no app.
  - Agenda:
    - o PJ-3030 (há um só) está na OS-0421, na OS-0424 e na OS-0504 no mesmo 24/09;
    - o Trator 02 está na OS-0420 (Santa Rita) e na OS-0504 (Lagoa Grande);
    - só um desses conflitos é detectado;
    - a OS-0424 precisa de 5,9 h numa janela de 5 h.
  - Limpeza do pulverizador:
    - o mesmo PJ-3030 aplica 2,4-D (OS-0430, 25/09 13:00–20:24) entre duas manhãs de fungicida na soja (OS-0421) e perto da aplicação no mamão (OS-0504), sem passo de limpeza;
    - depois de produto hormonal, e antes de cultura sensível, a descontaminação do tanque deve ser registrada antes da próxima carga.

Onda A · Fundação

EX-01 Dados coerentes entre telas e dentro dos modais. Corrigir as contradições e criar um teste que compare contadores e valores da mesma entidade em todas as telas (aceite: 0 divergências). Principais:
  - Produção:
    - previsão de soja 26/27: 68.180 sc (COLH) × 51.280 sc (GE-01, VE-05, GE-08);
    - o IV soma safras: 106.600 = 38.420 + 68.180;
    - COLH mostra 0,48 e 0,73 t/ha no mesmo painel.
  - O.S.:
    - OS × CA-01 divergem (OS-0430 "Falta máquina" × "Sem pendência"; "3 impedidas" × "2");
    - o painel da OS-0420 lista "MAP 11-52 250 kg/ha", enquanto a O.S. completa e a REC-014 dizem "KCl 60 % 120 kg/ha";
    - a OS-0418 aparece como "Pivô 1" e como "gotejo T7";
    - "Trator 02 assume" × "aguarda PCP".
  - Manutenção e estoque:
    - MA mostra "Ordens 0" com 4 OMs;
    - PSUP "quarentena 1" × SU-03 "retidos 3";
    - "conflito de reserva 0" com uma linha "Reserva em conflito";
    - lote M26-05 × M26-07.
  - Compras:
    - SOL-2026-07 em três estados;
    - "pedir até" diverge entre SU-01 e IC;
    - MAP 62.500 × 79.500 kg;
    - o contrato sai com 78,85 t, mas a proposta de R$ 360.905 era de 96,99 t.
  - Vendas: recebíveis VE-04 × GE-05; PV-037 entregue mas ausente em GE-05; VD-2101 sem venda.
  - Irrigação: "sem pendências" × "1 conflito"; Pivô 2 com 9,8 × 11,2 mm.
  - Cadastros e insumos:
    - PJ-3030 com tanque de 3.000 × 2.000 L;
    - Inseticida B em L no CD-06 e em "1,0 kg/ha" na decisão;
    - K do LAU-2043 em mg/dm³ × cmolc/dm³;
    - "Pivô 22" × "PV22".
  - Planejamento: "publicado na v4" com a v4 ainda em rascunho.

EX-02 Uma entidade, uma listagem, um detalhe e um formulário. Consolidar, com redirecionamento como já feito em MA-01..05 → MA:
  - Colheita: CO-01..05 e CO-07 → COLH, CARGA, BEN, PROD. CO-05det vira detalhe de BEN; CO-06/det vira seção de qualidade do lote.
  - Vendas: VE-01, VE-02, VE-04, VE-05 → VEN e IV, com VE-04det como detalhe. Hoje são 3 formulários para a mesma venda. Antes, migrar PV-026..029 e PV-032..034.
  - Logística: LO-01..03 → EXPED com visões de agenda, fila e docas; LO-02det como detalhe.
  - Estoque: SU-03 e SU-06..09 → EST com abas por entidade. Hoje há 2 formulários diferentes para receber a mesma NF ("Local" × "Depósito"; "Apta/Em quarentena" × "Inspeção").
  - Compras: CMP, SU-01, SU-04, SU-05 e IC → listagem de solicitações por estado; detalhe com Demanda, Comparação, Pedido e Cargas; "quando comprar" vira coluna; SU-02 vai para configuração.
  - Safras: SAF + PL-01 → uma listagem de safras, com PL-02, PL-03 e PL-06 como seções. Hoje há 2 formulários "Nova safra" diferentes e o parcelamento aparece duas vezes (PL-06 e "Dividir em parcelas" no SAF).
  - Demais:
    - OS + CA-01 → uma listagem de O.S.;
    - IN-01 + IN-03 → Meu dia, com visão Lista | Semana;
    - IR-01..03 → uma listagem por setor;
    - MB-02 e a abertura do MB-03 deixam de repetir o MB-01.
  Antes de remover qualquer tela, confirme no registro que ela é versão antiga, e não variante deliberada.

EX-03 Vocabulário único (complementa UX-01):
  - um verbo por ação ("Registrar apontamento", "Registrar avanço", "Apontar uso", "Apontar área");
  - coluna "Próxima ação" em todas as listagens;
  - ciclo do plano com no máximo 4 estados (hoje são 7);
  - siglas sem colisão (PV, OC, ROM × RM, COT × NEG, CT de frete × CT de venda);
  - nenhum código interno nem nota interna na tela (CMD-06, DEC-09, RN-039, "VE-05 (oculto)… pergunta 4 ao proprietário");
  - nome do menu = título = trilha, com raiz única.

EX-04 Contexto Fazenda · Safra herdado em toda tela e em todo modal (P27):
  - Telas que abrem sem contexto: IN-04, PAGR, PCOM, PMAN, PSUP, SAF, PA, AG-02..04, COLH, CMP, MB-07.
  - Modais:
    - "Nova ordem" pede a safra;
    - "Programar vistoria", "Criar diagnóstico" e "Registrar laudo" ignoram o filtro;
    - "Programar pós" cai na AG-01 sem talhão, alvo nem data (deveria vir com 7 DAA);
    - SU-01 "Reprogramar" pega o primeiro item, não a linha clicada;
    - SU-01 "Abrir cotação" chega no CMP em "Nenhuma safra escolhida".
  - A etapa "Escolha a safra" sai do CMP e do SAF.

EX-05 A primária resolve o estado e nunca falha depois do clique (aplica UX-02):
  - Sem primária: IN-04, AG-03, AG-05, AG-06, IN-02, PAGR, SAF, PL-05, CMP, IC, CO-04, BEN, PROD, IV, VE-03, GE-01, GE-06det, IR-03, IR-04, MB-02, MB-05, MB-07, PT-02, PT-04..07, além dos painéis de O.S. (OS-0418, OS-0420).
  - Primária que não resolve o estado: SU-02, SU-03, SU-08, VEN, VE-01, VE-06, CO-02, CO-06, CD-07, CA-01x (falta "Confirmar substituto"), GE-08 (abre o portal do banco), ON-01, PT-02det ("Nada mudou desde a v1"), PT-04det ("Ainda não recebido").
  - Ativas que só recusam depois do clique; devem aparecer desabilitadas com o motivo e a ação de cobrar o responsável:
    - GE-03 "Fechar competência", CA-02 "Encerrar", CA-04 "Confirmar recebimento";
    - SU-07 "Confirmar entrega" e "Separar FEFO", SU-02 "Publicar vigência", SU-09 "Submeter ajuste";
    - PL-01 "Autorizar execução" e "Encerrar período", AG-05 "Publicar", OS-0424-app "Retirar".
  - Painel VIS-013 com dois botões verdes; CO-06det sem decisão neutra.

Onda B · Entrada mínima

EX-06 Turno por exceção (MB-03, MB-10; P24, P26, P29, P61):
  - abre preenchido: hectares do dia previsto, horas = fim − início − pausas, consumo = dose × ha;
  - "Fechar turno como previsto" em 1 toque; o operador toca só no valor que mudou;
  - sinaliza quando GPS ou telemetria contradizem.
  Medido: 5 toques e 2 números obrigatórios. Meta: 2 e 0. Turno com diferença: cerca de 11 toques, 2 números e 1–2 textos; meta 3 e 1.

EX-07 Paradas com causa:
  - MB-08 e CA-01det já pausam com motivo, mas sem duração; MB-03 pausa sem motivo;
  - reusar a lista de causas que já existe, com início e fim registrados sozinhos;
  - a ocorrência fica ligada à O.S. e à máquina, e o sistema propõe "Reprogramar saldo".
  Resultado: ha/h real, eficiência de campo e Pareto de paradas. Estimativa: 5,6 ha/h contra 28,8 ha/h teóricos do PJ-3030, e esse número não aparece em nenhuma tela.

EX-08 Condições de aplicação e calibração (OS-0424-app, MB-02det, MB-03, painel VIS-013, CA-01det; P43):
  - limites de vento, temperatura, UR e Delta T, mais reentrada, na ficha e na decisão;
  - "Iniciar turno" confere clima e checklist, com alerta ou bloqueio configurável e exceção liberada pelo RT;
  - "Aumentar dose" mostra o limite de bula;
  - conferência de calibração: vazão por bico × taxa. Estimativa: −11 % na OS-0424, supondo bicos a 50 cm.

EX-09 Abastecer com 1 número (MB-09):
  - horímetro vem da telemetria ou do turno;
  - tanque e lote vêm do último uso;
  - sai o segundo botão com a mesma validação.
  Medido: 5 toques, 2 números e 1 chip.

EX-10 Conferência por exceção (CA-02 e "Conferir dia" da OS; P39):
  - hoje "Conferidos 2 de 2" aceita junto o turno com "horas acima do previsto";
  - conferir em massa só o que está dentro da tolerância e destacar o divergente, com "Aceitar com motivo" ou "Devolver";
  - "Liberar OS-0418" e o roteiro saem da CA-02.

EX-11 Recebimento de NF (SU-06/EST; UX-09):
  - "Ler documento/QR" abre o mesmo formulário e não lê nada: deve ler chave/XML e preencher pedido, NF, lote, validade e preço;
  - "Confere com a NF" como primária, com a quantidade da NF quando estiver dentro da tolerância de +5 %;
  - apta e quarentena derivadas da inspeção;
  - NF e quantidade na nota somente leitura.
  Medido: SU-06 com 2 números (conferida, validade); EST com 4 números mais o motivo da quarentena. Meta: 0 ou 1.

EX-12 Romaneio de entrada (CARGA; P09, P28, P29):
  - estados Pesagem → Classificar → Fechar ("Fechar" não existe hoje);
  - ticket e bruto vêm da balança; tara vem do cadastro do veículo (hoje "sem valor anterior");
  - líquido corrigido ao vivo pela tabela do armazém (hoje "Calculado ao salvar"; CG-0988: 9.840 → cerca de 9.470 kg);
  - umidade, impureza e classe como campos numéricos com unidade (no CO-03 são um texto livre só).
  Medido no fluxo novo: cerca de 9 toques e 3 números, mais 2 no grão. Meta: cerca de 4 toques e 2 números.

EX-13 Laudo de solo (AG-02):
  - o modal tem 17 campos (7 digitados) e não tem pH, P e MO;
  - V % e CTC não são calculados;
  - o "OCR" anunciado é um campo de texto com o nome do PDF.
  Correção: importar o arquivo do laboratório com prévia, unidade padrão (mostrando a digitada como origem) e V %/CTC ao vivo. Ler PDF depende de IA.

EX-14 Nascer do anterior (SAF, PL-01, PA; P13, P15, P25):
  - nem "Criar safra" nem "Editar" oferecem cópia: incluir "Copiar cultivos e planos de 2025/26";
  - nome derivado das datas; período com seletor de data;
  - sai o campo "Estado" editável à mão;
  - "Aplicar modelo" e "Gerar sugestões pelas análises" saem do ⋯ do PL-02 e vão para o lugar da criação.
  Ganho: de 7 campos para 2 escolhas no cabeçalho, e a grade vira revisão das diferenças.

EX-15 MIP: ajustes no painel que já funciona (VIS-013):
  - um só botão verde;
  - origem da dose ("mínimo da bula" ou "protocolo MIP Feijão v2");
  - regra de rotação aplicada a todo grupo repetido (hoje marca o IRAC 1B, mas não o IRAC 23 de 25/08);
  - reentrada e condições de aplicação;
  - visão Mapa de calor na AG-01;
  - "Programar pós" já preenchido.
  A aprovação individual fica.

EX-16 Rascunhos automáticos em suprimentos e manutenção (P34, P44):
  - a OM preventiva já é gerada do plano: falta vir com a data sugerida ("Janela: 24/09") e com a compra da peça já reservada para a OM;
  - falta firme ou mínimo/máximo gera rascunho de solicitação, e o "Comprar agora" do IC também;
  - achado crítico nasce como OM em rascunho;
  - O.S. concluída sugere a devolução;
  - FEFO vem pré-selecionado.

EX-17 Um lançamento produz todos os efeitos (P25, P41). A conciliação bancária e a proposta aceita virando pedido já existem; falta:
  - venda com unidade e safra na quantidade (é a causa raiz do "saca a conferir");
  - preço do compromisso em campo próprio (hoje vai em "Condições", texto livre);
  - entrega baixa o contrato e cria o título a receber; medição de frete cria o título a pagar (não verificável no protótipo).

EX-37 Formulários enxutos:
  - Primária com verbo e objeto: 34 de 64 formulários usam "Salvar"; ON-01det diz "Validar" e grava; VE-04det diz "Salvar" e envia ao cliente.
  - Obrigatórios marcados: nenhum está marcado nos 15 formulários de agronomia e cadastros.
  - 3 a 5 campos visíveis e "Mais opções":
    - CD-04 tem 23 campos; separar Operação de Permissões, ficando cerca de 6 visíveis;
    - CD-03 tem 12; CA-02 "Reabrir saldo", 7; CA-03, 7 (cerca de 3 bastam).
  - Lista no lugar de texto livre: motivo, causa, local, evidência como foto, alteração de política com mínimo/máximo e unidade, "Compromisso" do IN-03 como busca de registro, evidências do diagnóstico, carga e horário do LO-01.
  - Derivar em vez de digitar:
    - razão social pelo CNPJ;
    - colhido = soma das cargas (CO-02det);
    - cenário a partir da V2 (GE-02);
    - pedido e lote vindos da linha (VE-06);
    - itens da versão vigente na requisição (CA-04);
    - R$/h do CD-03 e do CD-04 no CD-08, com "Aplicar 19,8 ha/h";
    - massa da saca vinda do contrato (PCOM);
    - área do talhão pelo polígono ou KML (CD-01);
    - data de hoje nos registros do dia.

EX-39 Ficha de execução por papel, só com o essencial, em toda O.S. com insumo. Hoje só a OS-0424 tem ficha completa (app e impressa); OS-0421, OS-0425 e OS-0504 têm só a linha de cargas; as demais, nada.
  - Almoxarife:
    - todos os produtos da O.S. na requisição, inclusive adjuvante e TS;
    - embalagens fechadas, com lote e validade por FEFO;
    - "faltam X para terminar";
    - sobra lacrada e embalagens vazias a receber (tríplice lavagem).
  - Caldeiro:
    - por carga, cada produto em embalagens ("3 galões de 5 L") e a fração com a medida;
    - ordem de mistura explícita (hoje a ficha diz "na ordem da instrução liberada", e essa ordem não aparece em lugar nenhum);
    - água inicial e agitação;
    - marcar a carga preparada com hora e lote;
    - limpeza obrigatória quando o produto anterior exige;
    - EPI e classe toxicológica;
    - o caldeiro não confere o consumo da própria O.S. (Paula é caldeiro e conferente da OS-0421).
  - Operador:
    - regulagem com vazão alvo por bico e teste de calibração;
    - condições de aplicação (vento, temperatura, UR, Delta T);
    - mapa com o talhão, as zonas de taxa variável e as áreas de exclusão.
    - Por tipo de operação:
      - plantio: sementes por metro, população, PMS e germinação, profundidade, g/m de adubo e mapa de zonas do KCl;
      - adubação: dose que dê para regular (36,84 kg/ha não dá) e, no café, g por planta ou por metro;
      - plantio de mudas: g por cova (400 kg/ha ÷ 1.850 covas ≈ 216 g);
      - fertirrigação: kg por volta, diluição pela solubilidade (sulfato de potássio ≈ 110 g/L), tempo de injeção e lavagem, e o conjunto certo (hoje "gotejo T7" aparece em pivô);
      - calagem: cargas e logística (96.940 kg ≈ 33 cargas de 3 t).
  - Líder de campo (não tem visão hoje):
    - plano do dia por equipe (O.S., conjunto, operador, caldeiro e ordem);
    - conflitos resolvidos antes de sair;
    - retirada consolidada do dia;
    - cargas preparadas × área aplicada por conjunto, que mostra erro de dose na hora;
    - condições do dia e ocorrências.
  - Pessoas:
    - responsável com habilidade para a operação: Paula, que é caldeiro, aparece como responsável de adubação a lanço com trator sem ter "Operar trator";
    - as pessoas da Lagoa Grande (Wesley, Lúcia, Renato, Sérgio, Joaquim) precisam estar cadastradas com habilidade e capacitação.
  - Sai o texto que não se aplica: na colheita aparece "insumos calculados pela dose".

EX-40 Ajustes menores (baixo esforço):
  - páginas de módulo (MOD-*) com a contagem de pendências por item, ou abrir direto na tela de trabalho; hoje são 3 a 5 links sem estado, um clique a mais;
  - PL-05 "Notificar responsáveis" passa a ser automático;
  - AG-05 "Validar" e "Publicar" num passo só, mantendo a aprovação do RT;
  - AG-06 "Propor melhoria" e "Propor revisão" viram uma ação só;
  - o bloco "Manutenções e impacto na produção", repetido em PL-03 e PL-04, aparece uma vez;
  - a tabela "Água no solo" do AG-02 vai para Irrigação;
  - PCOM: "Colunas" e "Tabela/Cartões" aparecem duas vezes;
  - CD-04: três formas de filtrar (lista "Função", chips e "Agrupar") viram uma;
  - ações destrutivas vão para o ⋯: "Encerrar saldo", "Cancelar reserva", "Cancelar sem execução";
  - MB-06 "Concluir com 9 de 14" pede confirmação ou oferece Desfazer;
  - contrato formal só para entrega programada; compra avulsa abaixo da alçada vira "Aprovar e emitir pedido" (sujeito à decisão da seção 5);
  - "Restaurar demonstração" fica só no protótipo e não vai para o produto.

EX-41 Componentes do design system padronizados (práticas do Carbon, com o Fluent 2 onde for melhor), a partir do que os modais mostraram:
  - Tabela de dados:
    - filtro e ordenação no cabeçalho, agrupar e colunas;
    - uma só forma de filtrar por tela (o CD-04 tem três);
    - barra de ação em lote só com ações permitidas em lote (EX-32).
  - Botões:
    - primária com verbo e objeto;
    - secundárias discretas;
    - destrutivas separadas e no ⋯ (barra de comandos do Fluent);
    - ação indisponível aparece desabilitada com o motivo e quem resolve (EX-05).
  - Formulários (EX-37):
    - rótulo visível, obrigatório marcado e ajuda curta só onde evita erro;
    - unidade como sufixo e teclado decimal (já existem);
    - "Mais opções" para o raro.
  - Painel lateral para detalhe e criação, que já é o padrão. Confirmação só no irreversível.
  - Avisos:
    - aviso na própria linha para o que pede ação;
    - aviso temporário de retorno com Desfazer;
    - nenhuma nota interna na tela.
  - Estado vazio com uma ação; skeleton no carregamento; etapas só onde há etapas reais.
  - Um componente por tarefa: um formulário de recebimento, um de nova safra, um de venda (EX-02).

Onda C · Gestão que gera resultado

EX-18 Janela agronômica como eixo do PCP (PL-02..04, PAGR):
  - folga da janela por operação e programação ordenada por folga × prioridade;
  - capacidade por semana (hoje é por mês);
  - "% de área dentro da janela" no painel;
  - término previsto pelo ha/h real (UX-07);
  - reprogramação sugerida após chuva ou quebra.

EX-19 Custo por saca e margem por hectare por talhão (PL-01, PA, GE-01, PCOM; P20, P45, P59):
  - o espaço "CUSTO R$/T" no painel do talhão e o custo por talhão no GE-03 já existem: falta ligar os dois;
  - simulação entre planos (PA: R$ 2.099,90 × R$ 1.383,50/ha);
  - GE-01 desce até talhão, romaneio, contrato e custo, marcando o que é parcial.

EX-20 Previsão móvel única de produção: hoje só o mamão é previsto por contagem, e a soja segue "Prevista (v1)". Uma previsão só (colhido + saldo × produtividade amostrada), alimentando comercial, garantias e caixa.

EX-21 Política de comercialização (IV, VEN):
  - % vendido × custo coberto por safra;
  - alerta de preço que considera o custo por saca;
  - gatilho que gera rascunho de oferta; posições de trava e basis.
  Hoje 61 % da soja está sem preço, com margem exposta estimada em R$ 484 mil.

EX-22 Caixa de 13 semanas (GE-04), montado a partir de títulos, contratos, plano e previsão.

EX-23 Suprimentos com indicadores de resultado:
  - prazo de entrega por fornecedor no "pedir até";
  - % da demanda coberta antes da janela; ruptura que parou O.S.;
  - economia realizada; validade e "vencendo" na lista;
  - capital sem demanda em 90 dias;
  - inventário cíclico pela curva ABC (hoje o escopo da contagem é manual).

EX-24 PCM com indicadores de resultado (MA):
  - disponibilidade da frota na janela;
  - MTBF/MTTR, % preventiva, backlog em horas, custo por hora;
  - kit de peças por plano.

EX-25 Irrigação de valor:
  - chuva medida e prevista no balanço (o cadastro aceita sensor de chuva, mas não há nenhum);
  - início fora da ponta, com o custo da ponta mostrado nas janelas e respeitando a outorga;
  - alerta de pressão e vazão.

EX-26 Painéis por exceção (PAGR, PMAN, PSUP, IN-04; P60):
  - todo número abre a lista filtrada;
  - sem somas repetidas e sem linhas "nada a fazer agora";
  - cerca de 6 indicadores de resultado por painel, com meta e tendência; o painel mostra primeiro os que pedem ação e deixa o resto sob demanda.
  - Indicadores que provam resultado, por módulo (do painel de especialistas):
    - agronomia: % de aplicações acima do NC e dentro da janela, eficácia por produto × alvo, custo de controle em R$/ha, % de recomendações com registro válido, % de vistorias no prazo;
    - PCP: % de área feita dentro da janela, aderência plano × executado, déficit de capacidade visto com semanas de antecedência, tempo entre impedimento e liberação;
    - execução: ha/h real × padrão, horas paradas por causa, custo por ha da operação, % da área aplicada dentro das condições;
    - irrigação: lâmina aplicada × necessidade, horas em ponta, % da outorga usada;
    - suprimentos e estoque: % da demanda coberta antes da janela, ruptura que parou O.S., economia realizada, capital parado, perda por validade, acuracidade de inventário;
    - manutenção: disponibilidade da frota na janela, MTBF/MTTR, % de preventiva, backlog em horas, custo por hora;
    - colheita e pós-colheita: perda na colheita, erro da previsão (WAPE), % classe A, % de lotes aprovados, quebra;
    - comercial: % vendido × custo coberto, preço contra referência, basis, OTIF, frete por tonelada;
    - gestão: custo por saca e margem por hectare por talhão, desvio decomposto, caixa de 13 semanas.

EX-27 Talhão como centro (CD-01det): seções Operações, Monitoramento, Solo, Custo e margem e Linha do tempo, reaproveitando as listagens filtradas.

EX-42 Manejo × resposta da lavoura no Mapa (camadas "Pragas e doenças" e "Satélite" do IN-04). Funcionalidade nova pedida pelo proprietário. O objetivo é ver o que de fato melhora a lavoura, em nutrição e em controle de pragas e doenças, para o manejo melhorar a cada ciclo.
  - Protótipo de referência para tirar boas ideias. Usa dados sintéticos e não é requisito:
    - link: https://claude.ai/artifact/BhceWUXPoT9BXgTGUCy6LP (versão 2). É privado: o Claude lê com a ferramenta Artifact (action "read").
    - arquivo: pragas-no-tempo.html, que o proprietário anexa ao pedido. É por ele que o Codex lê o protótipo; se o protocolo tiver uma pasta de insumos, salve uma cópia lá.
  - Primeiro melhorar, depois implantar:
    1. Claude e Codex, cada um sozinho, avaliam o protótipo contra o PRD, o NAV/DS, a camada Satélite atual (índices, cena, contraste Talhão/Fazenda/Absoluto e "Ver histórico") e a camada Pragas e doenças atual. Cada um lista o que adotar, adaptar ou descartar e o que falta.
    2. Divergência se resolve por fonte ou reprodução. O Gemini real entra se houver decisão material de domínio: métricas de efeito, janelas de comparação, condições favoráveis por alvo.
    3. O Codex registra o desenho final e as fatias. Só então se implanta, na fase registrada no STATUS, com revisão cruzada.
  - O que o desenho deve cobrir (pontos de partida do protótipo):
    - Barra de tempo arrastável, com teclado, "Reproduzir" e "Hoje", que recolore o mapa:
      - pragas pela última vistoria em relação ao NC;
      - satélite pela última cena válida, com nuvem e "sem imagem" em cinza hachurado, nunca com cor de índice.
    - Gráfico da fazenda e do talhão na mesma linha do tempo:
      - nível × NC em pragas, ou NDVI/NDRE com a faixa P10–P90 no satélite;
      - comparação com a média da fazenda ou dos pivôs do mesmo estádio.
    - Ícones de manejo clicáveis na linha do tempo: defensivo, adubação ou fertirrigação, e operação. Quando se sobrepõem, viram um ícone com contagem. O clique mostra:
      - insumos, dose por ha e total;
      - grupo IRAC/FRAC, entrada e sequência do grupo;
      - calda e equipamento;
      - nutrientes (N, K2O, S, B em kg/ha);
      - clima no dia, com alerta de dia quente e seco para aplicação;
      - o efeito medido e a janela usada: em pragas, vistoria até 10 dias antes → 5 a 14 dias depois; no vigor, cena até 10 dias antes → 10 a 25 dias depois, menos a variação dos pivôs do mesmo estádio;
      - um botão para ir à vistoria ou à cena que mediu o efeito.
    - Faixas de chuva e irrigação (mm) e de clima:
      - temperatura máxima e umidade do ar, dia a dia;
      - marca da condição favorável ao alvo, por exemplo quente e seco (≥ 32 °C e UR < 50 %) para ácaro, ou folha molhada por 8 h ou mais entre 18 e 30 °C para antracnose;
      - no satélite, marca de calor ≥ 35 °C;
      - ao passar o mouse: Tmáx/Tmín, UR, horas de folha molhada, chuva e irrigação.
    - Painel "o que funcionou", até a data da barra:
      - pragas: redução mediana e dias até voltar ao NC, agrupando por produto, por produto e calda, por sequência do grupo ou pelo clima da semana; e o crescimento semanal sem controle nas semanas favoráveis × nas demais;
      - vigor: resposta por programa de adubação, dose de N e estádio; nível de hoje em relação ao estádio; calor × irrigação;
      - sempre com o número de casos, aviso de pouca evidência abaixo de 3 e o texto "associação, não causa".
  - Dados que o sistema real precisa ligar, sem digitação nova:
    - vistorias (AG-01, MB-06);
    - O.S. com apontamento: produto, dose, calda e conjunto;
    - fertirrigação e irrigação (IR-*);
    - estação meteorológica ou API: Tmáx, Tmín, UR, horas de folha molhada, DPV;
    - chuva medida;
    - cenas de satélite com máscara de nuvem (C4);
    - protocolo com o NC por alvo e estádio (AG-05).
  - Regras:
    - valores observados, sem interpolação;
    - janelas e limiares configuráveis por cultura e estádio, validados pelo agrônomo;
    - nenhuma recomendação automática: a decisão continua com o RT.
  - Aceite observável: em até 2 ações, o usuário vê a evolução de um alvo ou índice num talhão, com manejo e clima na mesma linha do tempo, e abre os insumos e doses de qualquer aplicação. Validar com agrônomo real (UX-13).

EX-43 Raio-X do alvo: o que faz cada praga ou doença subir e descer, medido nos dados da própria fazenda (camada "Pragas e doenças" do IN-04, ao lado do gráfico do EX-42). Funcionalidade nova pedida pelo proprietário. O pedido completo, com variáveis, métodos, gabarito, lições do protótipo e aceite, está no arquivo prompt-safrion-raio-x-do-alvo.md, que o proprietário anexa; ele prevalece sobre este resumo. Protótipo funcional: https://claude.ai/artifact/BhceWUXPoT9BXgTGUCy6LP (versão 3, painel da camada Pragas e doenças), também no arquivo pragas-no-tempo.html.
  - Objetivo: por alvo, mostrar o que faz subir e o que faz descer, ordenado pelo tamanho do efeito, com limiar, janela, intervalo, número de casos e nível de evidência (Forte · Moderada · Fraca · Insuficiente); a eficácia real de cada produto, dose, volume e condição de aplicação; a perda de eficácia por grupo IRAC/FRAC; e o risco de passar do NC em 7 e 14 dias, com os 3 fatores de cada talhão.
  - Variáveis, por janela antes de cada vistoria (0–7, 8–14, 15–28 dias, configurável): clima (Tmáx, Tmín, graus-dia, UR, horas de UR ≥ 90 %, folha molhada, DPV, chuva e chuva de lavagem, vento, dias favoráveis ao alvo); água (irrigação, método, suficiência, déficit, NDMI); defensivos (dias desde a última, ingrediente ativo, grupo IRAC/FRAC por tabela de referência versionada, porque o Agrofit não traz esse dado, dose ÷ bula, calda, equipamento, condição na hora, sequência do grupo, aplicações contra outros alvos); nutrição (N, K2O, Ca, B, S, programa, intervalo); planta (estádio, idade, NDVI/NDRE, histórico); vizinhança; inimigos naturais; operações (poda, roçada, erradicação); esforço amostral e avaliador como controle.
  - Resposta principal: taxa de crescimento entre vistorias, r = ln((y2 + ε) ÷ (y1 + ε)) ÷ dias. Percentual de NC não é percentual de área; vistoria parcial não entra como completa; sem interpolação.
  - Método em quatro camadas:
    1. exploração: Spearman parcial por janela (nível de partida e estádio; a época só com 2 safras ou mais), bootstrap em blocos, Benjamini-Hochberg, variáveis que andam juntas medidas como grupo;
    2. modelo por alvo: efeitos mistos ou gradient boosting com SHAP, validação temporal, exibido só se vencer a persistência;
    3. efeito das aplicações por Henderson-Tilton com talhões-controle pareados (Abbott sem vistoria antes), estudo de eventos e dias de proteção por Kaplan-Meier; sem controle pareado, "sem comparação válida". Correlação crua de aplicação × alvo nunca é exibida como efeito (causalidade reversa e regressão à média);
    4. risco à frente com a previsão do tempo, calibrado (Brier e curva de calibração).
  - Honestidade: associação não é causa; abaixo do mínimo de evidência (proposta: 8 eventos e 3 talhões) o efeito não aparece; série curta avisada; ausente ≠ zero; conhecimento de referência validado pelo RT mostrado como "referência, não medido nesta fazenda" na partida a frio; achado contra a biologia vira "achado a confirmar"; versão do modelo e dados guardados com cada achado.
  - Tela: cabeçalho com base de dados e evidência; listas "Faz subir" e "Faz descer" com barra de efeito e intervalo; sub-detalhe com curva de resposta, janela e casos que abrem a linha do tempo do EX-42; "O que funcionou no controle"; "Risco nos próximos 7 dias" com "Criar vistoria" (rascunho, nunca O.S.); mapa de correlações sob demanda. Sem menu novo. O RT marca cada achado (Confere · Não confere · Investigar) e promove a regra validada ao protocolo AG-05, com versão.
  - Gabarito: a simulação do pragas-no-tempo.html tem efeitos conhecidos (clima por alvo, eficácia por produto e dose, resistência por sequência, sub-irrigação em P3, P14 e P21, programas de adubação). O motor recupera a direção de 100 % dos efeitos fortes e a magnitude em ≥ 80 %, com falso positivo ≤ 5 % nas variáveis de ruído, e passa nos testes de causalidade reversa e de vazamento. No protótipo, em 25/09: 12 de 14 efeitos recuperados e nenhum falso positivo forte ou moderado.
  - Fatias sugeridas: dados e gabarito → eficácia das aplicações → faz subir e faz descer → risco → marcação do RT.
  - Aceite observável: em até 2 ações a partir do mapa, o usuário vê o que faz o alvo subir e descer e abre a evidência de qualquer item; o RT valida o Raio-X de 2 alvos do mamão e 1 de grão; 4 de 5 agrônomos explicam corretamente o que um achado significa e o que não significa (UX-13).

Pedidos do proprietário de 16/10 (funcionalidades e padrões). Cada um tem um prompt próprio, que o proprietário anexa e que prevalece sobre o resumo daqui. Em todos: primeiro Claude e Codex melhoram o desenho, depois implantam.

EX-44 Mapa da fazenda com UX e UI de excelência (prompt-safrion-mapa-ux.md, com o anexo-mapa-analise.md):
  - Padrão único do talhão em todas as camadas e telas com mapa: hover e foco mostram um cartão com o essencial; clique seleciona e abre o detalhe ao lado com a ação primária da camada, sem sair do mapa; Esc, clique no fundo ou "‹ Todos os talhões" fecham; URL guarda camada, data e talhão.
  - Legenda que trabalha (contagem e área por classe, realça e filtra), busca "Ir para talhão", teclado e leitor de tela, celular sem depender de hover.
  - Hoje: nenhuma dica no hover, por decisão no código; a fazenda padrão (MapLibre) não é operável por teclado; zoom sem pan na Santa Rita; contraste "Talhão" com nomes absolutos no Satélite; destinos que perdem o talhão; "sem dado" da cor do fundo; 30 defeitos listados (D1–D30) e 15 oportunidades.
  - Referência visual: o mapa do pragas-no-tempo.html (versão 3).

EX-45 Resolver em 1 clique (prompt-safrion-resolve-em-1-clique.md, com o anexo-insumos-analise.md):
  - Na linha de cada material (O.S. agrícola, ordem de manutenção, ordem de beneficiamento e packing): necessário, reservado, disponível na fazenda, em outra fazenda, a caminho e falta, com estado em texto.
  - Para cada estado, a ação de 1 clique que vai pronta para quem resolve: reservar, pedir transferência, antecipar entrega, pedir compra urgente já preenchida (origem, data, falta) e, para o agrônomo, trocar produto com registro, carência, grupo de resistência e estoque conferidos.
  - Compra avulsa fora do plano, em até 6 campos, com motivo, vínculo e impacto no orçamento; defensivo exige receituário.
  - Modelo a generalizar: a ordem de manutenção (MA) já pede compra da peça em 1 clique, sem duplicar, e reserva a peça para a OM. Hoje a O.S. agrícola não mostra o disponível, aponta "Suprimentos" (papel que não existe) e não oferece compra; a requisição avulsa é vedada a insumo agrícola.

EX-46 Entrada inteligente e em lote (prompt-safrion-entrada-acoes-revisao.md):
  - Para cada campo, o primeiro método que se aplica: calculado → herdado do contexto → capturado → escolhido em lista com busca e chips → padrão seguro → digitado com teclado numérico, unidade e validação.
  - Lote por seleção com resultado por linha; grade editável e colar de planilha nos lançamentos repetitivos; duplicar e modelo.
  - Medido na versão 1792184197-5a81: 810 campos em 174 modais e painéis; 130 digitados à mão; 30 de 90 números sem teclado numérico e 42 sem unidade; 42 de 43 datas sem atalho.

EX-47 Ações das linhas e dos cartões no menu ⋯ (prompt-safrion-entrada-acoes-revisao.md):
  - Linha ou cartão abre o detalhe; estado e próximo passo em texto; todas as ações no ⋯ sempre visível, com o próximo passo em primeiro e as destrutivas por último; indisponível mostra o motivo; lote só onde é permitido.
  - Hoje: 85 tabelas e listas com botões de ação soltos na linha, 1 com ⋯ (CA-03det "Mais ações"). O motor de grades já tem a opção rmenu, que leva as ações da linha ao ⋯ (pedido de 15/10), mas só a SAF a liga e o ⋯ depende de a linha poder ser excluída: ligar em todas as grades e mostrar o ⋯ sempre que houver ação.

EX-48 Revisão centrada no usuário por módulo (prompt-safrion-entrada-acoes-revisao.md e o relatório da varredura):
  - Cinco revisões por área: 187 achados (57 de prioridade alta), por tela, elemento, persona, o que acontece hoje, proposta, método, ganho, prioridade, evidência e cuidado. Relatório interativo: https://claude.ai/artifact/3MEq1jkELpA6ony4nVcwsJ (privado; o Codex lê o anexo-varredura-achados.md).
  - A varredura confirma que o EX-32 continua aberto: PL-04 "Liberar prontas" liberou a OS-0430 (glifosato e 2,4-D) e CA-01 "Liberar selecionadas" inclui O.S. com produto.

EX-49 Padrão único e previsível para listas, cartões, linhas pai e filho, botões e menu ⋯ (prompt-safrion-padrao-listas.md, com o padrao-listas-safrion.html; especificação viva: https://claude.ai/artifact/RFjMhybbxQwZX67TBFcB2U). Pedido do proprietário de 17/10. Completa o EX-47 e prevalece sobre ele onde houver diferença.
  - Regras: clicar na linha ou no cartão abre o detalhe em consulta no painel lateral, com estado, próximo passo e ações no topo (nunca edição direta, execução ou outra tela); a seta só expande; corpo do pai abre o pai e a filha abre a filha, com a trilha "pai › filho"; linha de grupo expande inteira; ações no ⋯ sempre visível, com ícone do dicionário e texto, ordem fixa e destrutivas por último em vermelho; indisponível com o motivo; botão visível só para a primária do detalhe, a barra da listagem e o lote; painel lateral para ver e agir, modal pequeno só para confirmar ou pedir motivo, página inteira para trabalho longo; Tabela e Cartões iguais; contexto preservado (↑ ↓ trocam de registro, Esc volta à linha).
  - Dicionário de ações e ícones (Lucide): um verbo, um ícone, em todo o sistema; verbo novo entra no dicionário antes de entrar na tela.
  - Hoje (código das 261 listagens e robô em 380 testes, nos dois modos): o clique na linha abre consulta em 246 testes, edição direta em 105, nada em 15 e outra tela em 11; o corpo da linha pai faz uma coisa diferente em cada árvore; só 5 listagens têm ⋯ e ele depende de a linha poder ser excluída; o ícone vem de uma lista de 8 verbos e o resto recebe seta genérica; o mesmo ícone serve a 9 verbos e "Ver" tem 8 ícones; nenhum dos 36 painéis de detalhe tem ⋯, com painéis de 4 botões (destrutivo ao lado da primária) e 9 painéis só com "Fechar"; nenhum dos 188 cartões recebe foco pelo teclado; 9 listas mudam de comportamento entre Tabela e Cartões.
  - Onde mexer: no motor de grades (g2open, rmenu, g2acaoIco, modo Cartões), e uma mudança vale para as 261 listagens; depois as telas com lista própria.

EX-50 Telas, menus e funções ocultos: levar o que tem valor, excluir o resto (prompt-safrion-telas-ocultas.md, com o anexo-telas-ocultas.md). Pedido do proprietário de 17/10.
  - Hoje: das 148 telas, 38 estão nos hubs dos 9 itens da barra; 83 só por link dentro de outra tela; 7 órfãs (GE-01, IN-03, PL-03, PT-06, MB-05det, MB-08, MB-08x); 8 só redirecionam.
  - Proposta para as 110 telas fora do menu: levar 20 para o visível (16 levam a função e saem; Meu dia, Aprovações, MB-05det e MB-08 ficam e ganham entrada), manter 22 como detalhe, excluir 54, e 14 dependem de decisão do proprietário (financeiro no Safrion ou no ERP, portal do parceiro, onboarding, backoffice).
  - 12 funções só existem em telas ocultas e precisam ir para o visível antes de qualquer exclusão (recolhimento de lote, NF-e e lacre na saída, transferência, perda e estorno, leitura de NF-e, trava de registro no receituário, emissão do período, troca de recurso em execução, resultado por cultura, MTBF e MTTR, "pedir até", contrato com cargas, ponto de pedido).
  - Os botões de lote ocultos que violam a aprovação individual (PL-04, CA-01, IN-02) não migram. "Pagar fatura ›" sai do cabeçalho geral e fica no Mapa e na Assinatura, para quem paga.
  - Ordem: levar a função, trocar os links, só então excluir, com aceite do proprietário registrado.

EX-28 Insumo ligado ao registro do Agrofit (CD-06 → AG-07/AG-04; P36, P43):
  - o formulário do item ganha registro, concentração, ingrediente ativo, mecanismo de ação, carência e dose de bula (hoje não tem campo de registro);
  - seletor mostra registro e concentração (evita lançar 867 g/L como 806);
  - unidade única do item (Inseticida B em L × kg/ha).

EX-29 Cadastros alimentados pelo realizado (CD-03, CD-08):
  - ha/h e R$/h recalculados dos apontamentos;
  - "Aplicar" na revisão sugerida;
  - conjunto escolhido da aba Conjuntos.

EX-30 Plataforma:
  - escopo por fazenda (já pedido no convite do ON-01) também no CF-01, mais alçadas de pagamento, crédito a cliente e liberação de lote;
  - recibos de comando (QL-1148, CMD-5522) na trilha do CF-04, com antes → depois;
  - rótulo "Importar 9 talhões e 6 máquinas" no lugar de "Validar";
  - tirar "IA 200 interações" do CF-05, ON-01 e BO-01.

EX-31 Fila e entrada (IN-01, IN-02; UX-05, UX-06):
  - decidir no lugar, em painel lateral (hoje "Decidir" navega para SU-09 e as ações do Meu dia saem da tela);
  - idade da pendência e prioridade por impacto (ha parados × dias de janela);
  - visões salvas.

5. DECISÕES DO PROPRIETÁRIO (não implantar sem aceite registrado)
- EX-32: confirmar que a correção é tirar o lote das O.S. com produto. Esse é o entendimento da decisão de 16/10; só muda se o proprietário decidir o contrário.
- IR-01 e IN-03 dizem "libera ao programar, sem aprovação (água sem produto)", e o MB-08x diz "encerrada automaticamente". Confirmar se ficam fora da aprovação agronômica individual.
- Aceite automático do turno dentro da tolerância (EX-10) ou conferência humana de tudo.
- Bloqueio por clima (EX-08): alerta ou bloqueio, e quem libera a exceção.
- Alçadas por valor para perda, crédito a cliente, frete, liberação de lote e pagamento de manutenção (hoje uma fatura de oficina cai na alçada de suprimentos). Também "Aprovar e emitir pedido" em uma só ação abaixo da alçada.
- Automações que dependem de IA (foto de praga, leitura de PDF, produtividade por imagem, falhas recorrentes, comprar × esperar): ficam desligadas até a estimativa de custo.
- EX-50: financeiro (contas a pagar e a receber) no Safrion ou no ERP; portal do parceiro no escopo; onboarding por trial ou implantação assistida; backoffice como ferramenta separada; e o aceite da lista de exclusão de telas.
- EX-43: confirmar que o motor estatístico do Raio-X do alvo não está coberto por "assistente de IA desligado" (não usa IA generativa; os textos saem de modelos de frase com os números), o mínimo de evidência para exibir um efeito e que só o RT promove achado a regra do protocolo.
- Validações agronômicas com o RT (e com o Gemini real, se houver divergência). Os dados são sintéticos, mas viram regra do produto:
  - KCl 60 % a 120 kg/ha no sulco (72 kg/ha de K2O), acima do limite usual de cerca de 50 kg/ha de K2O no sulco; avaliar parte a lanço;
  - abamectina a 100 L/ha com barra no mamão (OS-0504): a cobertura do dossel costuma pedir atomizador e volume maior;
  - MAP 11-52 em cobertura no feijão a 36,84 kg/ha (OS-0417);
  - 2,4-D com janela até 20:24 (OS-0430): risco de deriva e de inversão térmica;
  - nitrato de amônio (OS-0506, OS-0507): conferir se exige registro de produto controlado.

6. MÉTODO COM O CODEX
- Claude: valide cada EX no código-fonte do protótipo, no PRD e no NAV/DS.
  - Classifique como Confirmado (cite arquivo ou tela), Refutado (diga o que a análise viu errado) ou Já resolvido.
  - Para cada item confirmado, decida: Adotar, Adaptar (diga como) ou Rejeitar (diga o motivo).
  - Os riscos da Onda 0 são reproduzidos primeiro.
- Codex: envie a lista EX-01..EX-50 sem a sua classificação, pelo canal do protocolo. Peça que o Codex, de forma independente:
  - classifique cada item;
  - aponte o que a análise errou ou deixou de fora, em especial em domínio e fluxo.
  Não simule o Codex.
- Gemini real: só quando houver divergência material de domínio ou fluxo. EX-08, EX-10, EX-21, EX-32, EX-36, EX-38, EX-42, EX-43 e EX-45 são os candidatos mais prováveis. Pacote mínimo, sem dados reais.
- Divergência se resolve por fonte ou reprodução. O Codex decide o escopo conforme o protocolo e registra no checkpoint (só ele edita o checkpoint).

7. CRITÉRIO PARA ENTRAR
Um item só entra se cumprir as quatro condições:
- aumenta o valor de gestão ou a segurança, ou reduz cliques, digitação, etapas e retrabalho numa tarefa frequente, com medida antes/depois;
- preserva estado, unidade, aprovação, rastreabilidade, acessibilidade e as decisões fixas;
- cabe no escopo vigente, ou justifica a mudança de PRD com evidência;
- tem custo proporcional ao ganho.
Na dúvida, o item fica fora, com o motivo registrado.

8. IMPLANTAÇÃO
- Ordem: Onda 0, depois A, depois B, depois C; dentro de cada onda, por risco e depois por ganho × esforço.
- Cada item adotado vira uma fatia com ID, persona, arquivos, autor, revisor e aceite observável.
- Cada fatia segue o Double Diamond:
  - Descobrir: contexto de uso e fluxo real do perfil;
  - Definir: aceite medido antes do código;
  - Desenvolver;
  - Entregar: com a medida depois.
- Toda tela nova ou alterada passa pela regra TELA-01 e pelas 10 heurísticas.
- Medida dos indicadores da seção 0:
  - interações por tarefa nos testes ponta a ponta, como na linha de base de 16/10 (UX-03);
  - tempo, sucesso, erros, aprendizado e SUS no teste moderado com 3 a 5 pessoas por perfil (UX-13);
  - acessibilidade por verificação automática, teclado e leitor de tela.
- Para a Onda 0, cada correção ganha um teste de regressão: lote recusado para O.S. com produto; ação de risco exige motivo e alçada; medida não pré-preenchida; lista filtrada por contexto e organização; irrigação fora da tolerância não encerra; O.S., app, ficha e almoxarifado com o mesmo cálculo; recurso único sem dupla alocação; limpeza registrada depois de produto hormonal.
- Siga a fase registrada no STATUS (protótipo ou transferência ao Next), sem evolução paralela.
- Revisão cruzada: quem revisa integra o PR do outro.
- Publique incrementos operáveis no artefato existente, com versão, URL e mudança concreta.
- O PRD só muda quando a decisão alterar um requisito, referenciando o design system e com revisão real.

9. NÃO FAZER
- Tratar a análise como requisito, ou duplicar regras no PRD.
- Remover tela sem confirmar no registro que ela é versão antiga.
- Criar tela, indicador ou etapa sem uma decisão concreta por trás.
- Mexer nas decisões fixas: aprovação agronômica individual, servidor como autoridade de saldo, idempotência e rastreabilidade, travas de receituário, carência e registro, sem modo escuro, IA desligada até a estimativa de custo.
- Fixar norma, dose ou alíquota no código.
- Passar na frente de item prioritário ou interromper autoria ativa.

10. ENTREGA (no canal registrado)
- Tabela EX-01..EX-50 com: validação e evidência · decisão Claude · decisão Codex · decisão final · onda · ganho medido (antes → depois) · esforço · risco.
- O que a análise errou ou deixou de fora, segundo o Codex, e como foi tratado.
- Plano das ondas, com as fatias, a autoria e a revisão.
- Decisões pendentes do proprietário (seção 5), cada uma com recomendação e impacto.
- Três listas curtas, com motivo: aplicado, deixado de fora, cortado.
- Suposições e pendências, cada uma com o gatilho de retomada.

ANEXO A · PRINCÍPIOS DE PRODUTO (P01–P66)
Definidos na conversa como padrão de excelência para gestão agrícola: o mais clean, minimalista e funcional possível, com o mínimo de digitação e cliques, o máximo de automação, autocomplete e listas, e zero retrabalho. Servem de régua para os EX; não são requisito por si.

A. Estrutura (Menu → Listagem → Detalhe → Sub-detalhe)
P01 Menu agrupado por tarefa: Hoje · Lavoura · Operação · Recursos · Resultado.
P02 A home "Hoje" é a lista de pendências, com a ação no próprio item. Sem gráficos decorativos.
P03 Talhão. Estados: Ativo · Inativo. Detalhe: Safra atual · Operações · Monitoramentos · Solo · Custo e resultado · Mapa.
P04 Plano de safra. Rascunho→Enviar para aprovação · Em aprovação→Aprovar · Vigente→Revisar (cria nova versão) · Encerrado. Detalhe: Talhões e culturas · Operações previstas · Insumos · Orçamento · Planejado × realizado.
P05 Ordem de serviço. Estados em P12. Detalhe: Resumo · Insumos · Máquinas e equipe · Apontamentos · Custo · Histórico.
P06 Monitoramento (MIP). Aberto→Avaliar · Avaliado→Decidir; controlar gera O.S., aguardar agenda revisita. Detalhe: Pontos · Pragas e níveis · Mapa de calor · Decisão e responsável técnico.
P07 Insumo/estoque. Disponível · Reservado · Vencendo · Bloqueado. Detalhe: Saldo por depósito e lote · Movimentos · Reservas · Preço médio.
P08 Máquina. Disponível · Em operação · Em manutenção · Inativa. Detalhe: Uso (h, ha) · Abastecimentos · Manutenções · Custo-hora.
P09 Romaneio. Pesagem→Classificar · Classificado→Fechar · Fechado. Detalhe: Pesos · Umidade e impureza · Destino · Contrato.
P10 Contrato de venda. Aberto→Registrar entrega · Em entrega · Cumprido. Detalhe: Volume · Entregas · Preço · Recebimentos.
P11 Mapa, calendário e quadro são visões da mesma listagem, não telas novas.

B. Ciclo da O.S.
P12 Uma ação primária por estado:
    Rascunho → Programar (pede só talhão, operação e janela);
    Programada → Liberar (verifica estoque e reserva, máquina e operador livres, receituário, carência e restrições, alçada);
    Liberada → Iniciar execução (envia ao app ou ao monitor da máquina; a reserva vira retirada);
    Em execução → Apontar (área, horas, insumo real, clima, GPS, foto; Pausar como secundária);
    Pausada → Retomar (com motivo);
    Concluída → Conferir e encerrar (supervisor confere, sobra devolvida, custo apurado);
    Encerrada (realizado definitivo); Cancelada (motivo, reserva liberada, histórico preservado).
P13 O estado só muda por ação; nenhum "status" editável à mão.
P14 Concluir ≠ encerrar; apontar 100 % da área não encerra a O.S.

C. Verbos além do CRUD
P15 Copiar da safra anterior e usar modelo; copia a estrutura, nunca o executado.
P16 Reprogramar (preserva a data original), pausar e retomar com motivo (vira indicador de parada), dividir e agrupar O.S.
P17 Estornar, inativar em vez de excluir, reabrir com permissão e motivo, desfazer no que é reversível. Nada que mexeu em estoque ou custo é excluído.
P18 Conferir apontamento (só o conferido entra no custo definitivo), devolver sobra, fechar período, ratear.
P19 Reservar, retirar, transferir e devolver como movimentos com rastro.
P20 Comparar (planejado × realizado, talhão × talhão, safra × safra, no mesmo recorte e unidade) e simular (sem gravar).
P21 Atribuir, comentar e mencionar, anexar foto ou documento, compartilhar a O.S. em PDF ou link; a conversa fica no registro.
P22 Importar e exportar (planilha, KML/shapefile, XML de NF-e, arquivo da máquina) com prévia do que entrou e do que falhou.
P23 Ação em massa com resultado parcial explícito; selecionar talhões gera uma O.S. por talhão; colar do Excel na grade. (Aprovação agronômica continua individual.)

D. Entrada mínima
P24 O usuário só informa o que o sistema não sabe: a diferença do planejado, decisões técnicas, medidas sem sensor e aprovações.
P25 Cada registro nasce preenchido pelo anterior: plano → O.S. → apontamento → custo → financeiro.
P26 Apontamento por exceção: "Executado como planejado" em 1 toque; só a diferença é digitada; sinalizado se GPS ou telemetria contradizem.
P27 Contexto Fazenda · Safra fixo e herdado; abrir pelo talhão ou pelo mapa já seleciona; máquina e operador sugeridos pelo contexto.
P28 Captura automática: GPS, hora, clima, telemetria, balança, XML da NF-e, QR de máquina e lote.
P29 Cálculo no lugar de campo: total = dose × área, nº de tanques, horas pelo horímetro, L/h, peso líquido corrigido por umidade e impureza, fim da carência, custo.
P30 Unidade ao lado do campo e conversões centralizadas; data da operação ≠ data do registro; executor ≠ usuário logado; último valor só para contexto, nunca para dose, lote ou quantidade; seletor que distingue homônimos; um campo de observação.
P31 Listas que aprendem (chips dos mais usados) e busca tolerante a acento, código e apelido.
P32 Criar ali mesmo o cadastro que falta.
P33 Todo valor automático mostra a origem e é editado no lugar.
P34 Automação gera rascunho e nunca executa (estoque mínimo → pedido; horímetro → preventiva; MIP → O.S.; O.S. concluída → devolução).

E. Zero retrabalho
P35 Validação na entrada, com a correção escrita na mensagem.
P36 Cadastro único, referenciado em todo lugar.
P37 Rascunho automático e offline, com fila visível; "salvo no aparelho" ≠ "recebido pelo servidor".
P38 Envio idempotente.
P39 Conferência por exceção: só divergências; o resto em massa.
P40 Corrigir = estorno + novo registro pré-preenchido.
P41 Um lançamento produz todos os efeitos: estoque, custo e planejado × realizado.

F. Regras de negócio
P42 Estoque atômico e nunca negativo; período fechado só aceita estorno; sincronização com versão e conflito visível.
P43 Produto registrado para cultura e alvo; dose acima da bula bloqueada ou exceção com RT; carência e reentrada bloqueiam; condições de aplicação registradas; área apontada maior que o talhão alerta; APP e reserva legal bloqueiam; capacitação do operador; rotação de mecanismo de ação. Normas: conferir vigência e parametrizar.
P44 Conflito de máquina ou operador no mesmo horário; preventiva pelo horímetro.
P45 Custo parcial ≠ zero; razões (custo/ha, produtividade) não se somam; rateio com critério declarado; planejado × realizado no mesmo recorte.
P46 Permissão por papel e fazenda; alçada por valor e tipo; auditoria com antes/depois, quem, quando e de onde.

G. Interface
P47 Lista e detalhe lado a lado no desktop; tela cheia no celular.
P48 Grade editável inline para lançar vários de uma vez.
P49 Etapas no detalhe com dica do próximo passo.
P50 Linha do tempo de eventos no detalhe.
P51 Busca global (⌘K), atalhos N/E/Esc, Enter cria a próxima linha, datas "hoje/ontem/+7".
P52 Visões salvas.
P53 Desfazer em snackbar; confirmação só no irreversível.
P54 Resposta ao toque em menos de 100 ms; skeleton no lugar de spinner.
P55 Plano enviado à máquina e aplicação real voltando como apontamento.
P56 MIP com mapa de calor e decisão.
P57 Anatomia clean: uma primária, secundárias no ⋯, sem cards nem ícones decorativos, uma cor de destaque, estado em texto.
P58 Modo campo: offline, fila visível, alvos de 48 px, contraste para sol, um apontamento por tela.

H a L. Fluxo, indicadores, metas, limites e cortes
P59 Fluxo encadeado: plano → recomendação → O.S. → liberar → retirada → execução → apontamento → conferência → devolução → encerramento → planejado × realizado; colheita → romaneio → armazém → contrato → receita → margem por talhão; ciclos paralelos de MIP, manutenção e compra.
P60 Indicadores que mudam decisão, com drill-down até o apontamento e marcados como parciais quando falta dado.
P61 Metas de toques: apontar como planejado 2 toques e 0 digitação; com diferença 3 toques e 1 número; mesma operação em 8 talhões 4 toques; receber compra 0 digitação; abastecer 1 número; romaneio 2 números; monitorar praga 0 texto; chuva 1 número.
P62 A automação para em liberar, receber, encerrar e pagar (sempre um toque explícito); dose, lote e quantidade vêm do plano ou da medição; todo valor automático é visível e editável.
P63 Formulário com 3 a 5 campos visíveis e o resto em "Mais opções"; sem wizard para cadastro.
P64 Uma ação primária com verbo e objeto; sem "Salvar", "Salvar e novo" e "Salvar e fechar" lado a lado.
P65 Sem menus por perfil: a mesma tela, com permissões diferentes.
P66 Sem um relatório em PDF para cada coisa: listagem com filtro, agrupamento e exportação.

Suposições dos princípios: foco em grão e fibra com operação mecanizada (pecuária, café e cana seguem o mesmo esqueleto com entidades próprias); telemetria, balança e estação são opcionais (sem elas, vira 1 número digitado); as referências de mercado citadas na conversa (Airtable, Linear, Stripe, Salesforce Path, SAP Fiori, John Deere Operations Center, Cropwise) vêm do comportamento público conhecido, não de auditoria atual; normas precisam de conferência de vigência; metas de toque precisam ser validadas com cronômetro e operador real.
