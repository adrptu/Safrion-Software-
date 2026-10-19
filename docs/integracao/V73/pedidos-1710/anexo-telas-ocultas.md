# Telas e funções ocultas do Safrion: o que levar, manter, excluir e decidir

Revisão de 17/10/2026 sobre a versão 1792184197-5a81 do protótipo (https://claude.ai/artifact/HqspGRcrX1wcayCVMe9emm). Base: o grafo de navegação (o que a barra e os hubs alcançam), o código de cada tela (`v3/` = cópia local dessa versão; linhas citadas como L…), o inventário do robô e os 187 achados da varredura.
A tabela completa, com evidência e links a trocar, está no fim deste anexo (123 itens).

## Como ler

- **Levar para o visível**: a função tem uso real e falta na tela visível. Leve a função e depois apague a tela. Exceção: IN-01, IN-02, MB-05det e MB-08 ficam como telas, só ganham entrada.
- **Manter como detalhe**: é o detalhe ou a subtela natural de algo visível e já se chega pelo clique certo.
- **Excluir**: duplica tela visível, é versão antiga, só redireciona ou não tem uso real.
- **Decidir com o proprietário**: o uso depende de escopo comercial.

## Contagens

| | Levar | Manter | Excluir | Decidir | Total |
|---|---|---|---|---|---|
| Telas fora do menu | 20 | 22 | 54 | 14 | 110 |
| Funções ocultas em telas visíveis | 6 | 1 | 4 | 0 | 11 |
| Outros acessos e Pagar fatura | 0 | 1 | 0 | 1 | 2 |

Se tudo for aceito, saem 70 telas: as 54 excluídas e as 16 cujas funções foram levadas.
As 14 telas a decidir saem também se o proprietário não quiser o escopo.

## Levar para o visível, por hub

**Mapa (Início).** A barra continua com 9 nomes.
- IN-01 Meu dia: atalho "Meu dia · N" no cabeçalho do Mapa e página inicial do operador e do almoxarife (UX-05). Absorve a Agenda (IN-03) como visão Calendário.
- IN-02 Aprovações: atalho "Aprovações · N" no Mapa e página inicial do agrônomo. Passa a listar cada O.S. com produto, uma por vez, "aprovou, abre a próxima". Sai o "Aprovar selecionados".
- CA-03 Ocorrências: vira a visão "Ocorrências" do Meu dia. Hoje nenhuma tela visível lista o que o app registra.

**Agrícola.**
- Ordens de serviço:
  - recebe o filtro "A conferir", com conferência por exceção (CA-02);
  - recebe "Emitir O.S. do período" (PL-04), sem levar o "Liberar prontas";
  - no painel, ganha a decisão de substituto lado a lado também em execução (PL-05det);
  - no painel, ganha a seção "Receituário e versões", com a trava de registro Agrofit (AG-04det);
  - ganha o filtro "Receituários" para o RT (AG-04).
- Planos agronômicos: fonte, validade e aprovador RT por versão (AG-05).
- Estoque de produto: rastreabilidade do lote e "Simular recolhimento" (CO-06).
- Custos e fechamento: visão "Resultado da safra" com receita, margem e ROIC por cultura (GE-01).
- Painel: custo de pulverização por ha e aderência ao dia previsto (GE-06).
- Pragas e doenças: o Painel passa a usar os atalhos #VIS-…:decidir e :programar.
- Irrigação: o menu suspenso de etapas vira abas visíveis.
- Ordens de serviço: a coluna "Situação · próximo passo" aparece por padrão.

**Manutenção.**
- Painel: disponibilidade, MTBF, MTTR e custo/h por ativo (GE-06).

**Suprimentos.**
- Compras: coluna "Pedir até", itens atrasados e "Comprar urgente" (SU-01).
- Compras: contratos de fornecimento com cargas sob demanda (SU-05).
- Estoque: ler NF-e ou QR no recebimento (SU-06, UX-09).
- Estoque: transferir, registrar perda e estornar com vínculo (SU-08).
- Painel: "Faltas atrasadas" (SU-01).

**Comercial.**
- Expedição: checklist da saída com NF-e, lacre com foto, conferência do lote e balança (LO-02det).

**Cadastros.**
- Produtos e locais: seção "Reposição" do item, com mínimo, ponto de pedido e máximo (SU-02).
- Fazendas e talhões: o clique na linha abre o detalhe do talhão.

**Outros acessos › App de campo.**
- MB-08 Irrigação de hoje: ganha entrada pelo cartão da ordem de água. Hoje está órfã.
- MB-05det Receber devolução: ganha link no bloco da aba Almoxarife. Hoje está órfã.
- Aba Almoxarife: ganha a fila "A separar".

**Todas as listagens.**
- O ⋯ da linha aparece sempre que a linha tiver ação. O proprietário pediu isso em 15/10.

## Manter como detalhe

- Detalhes já certos: AG-01det, CA-03det, CD-01det, GE-02det, IR-03det.
- OS-0424-app: generalizar para toda O.S. com calda.
- Subtelas da Irrigação: IR-03 e IR-04, que passam a ser abas.
- GE-02det absorve o GE-06det.
- App de campo: MB-01 a MB-10 e MB-08x-recibo.
- ON-01det: a mesma prévia serve para importar talhões na CD-01.

## Excluir

| Família | Telas | O que migrar antes |
|---|---|---|
| Início | IN-03 | visão Calendário e "Criar tarefa vinculada" para o Meu dia |
| Agronomia | AG-03, AG-03det, AG-06 | hipótese e evidências para a decisão da vistoria; "economia do MIP" é opcional |
| Campo | CA-01, CA-01det, CA-01x-os0420, CA-04, OS-0424-ficha | custódia com "Pedir entrega"; versão de impressão dentro da ficha do app |
| Planejamento | PL-01, PL-02, PL-02det, PL-03, PL-05, PL-06 | conferir no SAF: autorizar execução, pendência vencida e ajuste local; "Aplicar alternativa" no ⋯ da O.S. |
| Irrigação | IR-02 | "Programar irrigação" em lote dentro do IR-01 |
| Colheita (base antiga) | CO-01, CO-02, CO-02det, CO-03, CO-04, CO-05, CO-05det, CO-06det, CO-07 | padrão × medido no "Registrar resultado" do PROD |
| Logística | LO-01, LO-02, LO-03, LO-04 | valor do frete na carga, se faltar; a aba Motorista do app sai junto |
| Gestão | GE-06det, GE-07 | hipóteses no GE-02det; ação vira tarefa no Meu dia |
| Suprimentos | SU-03, SU-03det, SU-04, SU-05det, SU-07, SU-07det, SU-09 | condição padrão segura na devolução; FEFO, se faltar |
| Comercial | VE-01 a VE-06, VE-04det | evidência no "Registrar devolução" do EXPED; alerta de preço é opcional |
| Portal | PT-06 | nada (órfã) |
| Redirecionamentos | MA-01 a MA-05, MA-04det, PM, Main | nada; nenhum link aponta |

Funções a excluir:
- os recortes #vis= da GE-08 (o item Crédito abre a tela inteira);
- "Abrir ordem completa ›" de 2 O.S.;
- a aba Motorista do MB-10;
- as cópias de "Restaurar demonstração" (fica uma só no menu do avatar).

## Para o proprietário decidir

1. **Financeiro (GE-04, GE-05).** Contas a pagar e a receber ficam no Safrion ou no ERP?
   - A dica do GE-04 diz que a fonte oficial é o ERP.
   - VEN e PCOM dizem que o recebimento é do Financeiro, "fora desta etapa".
   - Recomendação: ERP. No Safrion fica só o estado do título e a aprovação na caixa de Aprovações.
2. **Portal do parceiro (PT-01 a PT-05det, PT-07).** Fornecedor, comprador e banco entram no Safrion?
   - Se sim, o mínimo é PT-02det (responder cotação por convite) e PT-05det (enviar XML da NF-e).
   - O portal tem login próprio e fica fora do menu da fazenda.
3. **Onboarding (ON-01).** O cliente entra por trial próprio ou por implantação assistida?
   - Em qualquer caso, sai do menu.
   - Abre sozinho na primeira entrada e mostra uma faixa "passo N de 6" no Mapa.
4. **Backoffice (BO-01, BO-02).** Vira uma ferramenta de administração separada.
   - O BO-02 mostra a cobrança de outras organizações a quem abre "Outros acessos".
   - Os preços ainda são "exemplo, a decidir" (DEC-01/05/09).
5. **Outros acessos.** O nome fica na barra.
   - O conteúdo cai para "App de campo" e, se o portal ficar, "Portal do parceiro".

## Outros acessos e "Pagar fatura ›"

- **Outros acessos**: manter o nome e enxugar o conteúdo.
  - Hoje mistura quatro públicos: operador, parceiro, cliente novo e operador do SaaS.
  - App de campo: manter.
  - Portal: decidir.
  - Onboarding: mover para a primeira entrada.
  - Backoffice: tirar.
- **"Pagar fatura ›"**: mover.
  - Hoje a faixa está no cabeçalho de todas as telas da organização.
  - Aparece quando a fatura está em atraso. No cenário inicial (23/09, faturas pagas) não aparece; só ao avançar a data simulada.
  - O link não confere papel, mas só o gestor paga (AL-15).
  - Mostrar só no Mapa e na Assinatura, e só para quem paga.
  - Nas outras telas, a restrição aparece no ponto de uso, por exemplo "Criar talhão" desligado com o motivo.

## Riscos

**Links quebrados.** Telas que ficam apontam para telas que saem:
- GE-03 L58 → CA-01, CA-02, LO-04, SU-06, SU-07 (documentos de origem do custo);
- GE-08 L58 → GE-04, VE-05;
- IN-04 → AG-06 (L7711, L7822), CA-01det e CA-01x (L6346, L7211), CO-06 (L7823, L7935–7947), IR-02 (L5722, L5740, L7211);
- OS → CA-01det e CA-01x (L5021), OS-0424-ficha (L52);
- PAGR L6183 → CA-01det e CA-01x;
- AG-01 L5578–5579, AG-02 L5128 e AG-07 L5045 → AG-03det e AG-04det;
- PROD L5464 → CO-06;
- IN-01 L58 e IN-02 L58 → CA-02, PL-05, LO-02, CO-06det, SU-02, SU-09.

O destino de cada troca está no campo `antes_de_excluir`.

**Números divergentes**, que somem ao excluir o legado:
- VE-04 mostra R$ 244 mil a receber; o PCOM mostra R$ 91.470.
- O lote F26-02 aparece "em conflito" no SU-03 e "sem conflito" no SU-03det.
- GE-02det e GE-06det explicam o mesmo desvio em duas telas.
- A família CO usa base antiga: OC-0510 no T7, contra a OS-0510 no Pivô 6 da OS.
- IN-01 e IN-03 repetem 5 tarefas com nomes diferentes.

**Perda de função.** Estas funções só existem em telas ocultas. Não apague a tela antes de levá-las:
- recolhimento de lote;
- lacre e NF-e na saída;
- transferência, perda e estorno;
- leitura de NF-e;
- trava de registro no receituário;
- emissão do período;
- troca de recurso em execução;
- resultado por cultura;
- MTBF e MTTR;
- "pedir até";
- contrato com cargas;
- ponto de pedido editável.

**Regras fixas violadas em telas ocultas.** Ficam fora da migração:
- PL-04 "Liberar prontas" liberou O.S. com defensivo em lote;
- CA-01 "Liberar selecionadas" faz o mesmo;
- IN-02 "Aprovar selecionados" aprova em lote.

**Isolamento.** O BO-02 expõe outras organizações dentro do menu da fazenda.

## O que não deu para concluir pelo código

- Se a publicação usa o `Main` como página inicial. Conferir antes de apagar.
- Se o SAF já tem "Autorizar execução", "Encerrar período", "Decidir pendência vencida" e "ajuste local × padrão". Há indícios, mas não testei os fluxos.
- Onde se editam o NC por alvo e a tabela regional de adubação. Não achei edição nas telas visíveis.
- O `navegacao.json` marca o MB-05 como "no menu" por um link no código comum, a trilha de auditoria. Nenhum hub lista o MB-05.

## Suposições

- "Visível" é o que os 9 itens da barra e seus hubs mostram hoje.
- Ordens só com água continuam na Irrigação, como diz a dica do MB-02.
- O app de campo segue em "Outros acessos" só enquanto for protótipo.

## Tabela completa (um item por tela ou função)

| Tela | Título | Hoje | Decisão | Destino ou equivalente | O que aproveitar | Antes de excluir | Valor | Motivo |
|---|---|---|---|---|---|---|---|---|
| AG-01 › #VIS-…:decidir e :programar | Atalhos de decisão da vistoria | função oculta em tela visível (só por endereço com #) | Levar para o visível | Agrícola › Painel › "MIP · onde agir": botão com o verbo ("Decidir controle VIS-013") e o link direto | Abrir o formulário certo em 1 clique. |  | Médio | O AG-01 aceita #VIS-xxx:decidir e :programar (AG-01 L5445), mas o Painel só usa "Conferir vistoria" (AGRO-15). |
| AG-04 | Recomendações | só por link dentro de outra tela | Levar para o visível | Agrícola › Ordens de serviço › filtro "Receituários" e coluna "Receituário · RT" | Lista do RT com o que assinou: recomendação, versão, produto · dose · janela, situação ("1 uso sem registro"). | Depois de levar, apagar a tela. Nenhum link de tela que fica. | Médio | Receituário é exigência legal e só aparece listado aqui ("Recomendações e receituários"). AGRO-11: o RT precisa achar o que assinou. Na OS não há coluna de receituário. |
| AG-04det | Recomendação · REC-014 plantio T4 | só por link dentro de outra tela | Levar para o visível | Agrícola › Ordens de serviço › painel da O.S. › seção "Receituário e versões" | Trava legal "sem registro Agrofit para cultura × alvo" com troca por produto registrado; versões com alcance (realizado na v2, saldo na v3); memória de cálculo por zona (laudo → dose); custo por recurso. | Conferir o registro já ao salvar cada versão (AGRO-05). Depois apagar a tela. Links a trocar: AG-01 L5579; AG-01det L48; AG-07 L5045 → OS.dc.html#OS-0420. | Alto | Única tela com a trava de registro e as versões da recomendação (tabelas Itens, Versões, Zonas; AGRO-04, AGRO-05). |
| AG-05 | Biblioteca e planos técnicos | só por link dentro de outra tela | Levar para o visível | Agrícola › Planos agronômicos › plano › cabeçalho da versão | Referência (fonte), validade/revisão e aprovador técnico (RT) por versão; protocolo MIP (NC por alvo) e tabela de adubação como referências versionadas. | Os planos-modelo (soja, feijão, mamão) já estão no PA. Depois apagar a tela. Nenhum link de tela que fica. | Médio | O PA tem plano e gatilhos, mas não tem fonte, validade nem aprovador; o AG-05 tem (g_bib: ref, val, apr). Não achei onde editar NC e a tabela regional nas telas visíveis (AG-02: "tabela regional a decidir pelo proprietário"). |
| CA-02 | Apontamentos e conferência | só por link dentro de outra tela | Levar para o visível | Agrícola › Ordens de serviço › filtro "A conferir" (apontamentos provisórios de todas as O.S.) | Fila única do conferente; conferência por exceção (dentro da tolerância em lote, divergência com motivo); "Devolver para esclarecimento" na linha. | Não levar o "Roteiro da OS-0418" (OS-19). Depois apagar a tela. Links a trocar: GE-02det L48/L58; GE-03 L58; IN-01 L58 → OS.dc.html (filtro A conferir) ou OS.dc.html#OS-…. | Alto | Na OS a conferência é dia a dia dentro de cada O.S. (3 cliques por dia, OS-16). Só a CA-02 junta a fila e tem "Devolver para esclarecimento". Hoje a primária confere até o dia divergente (OS-08). |
| CA-03 | Ocorrências | só por link dentro de outra tela | Levar para o visível | Mapa › Meu dia (IN-01) › visão "Ocorrências" (abertas, gravidade, destino, dono) | Triagem das ocorrências do app (MB-04): destino (manutenção, agronomia, O.S.), dono, próxima ação, encerrar tratamento. | Unificar os tipos do app e da web e incluir "Falta de insumo" (OS-24). Depois apagar a tela. Links a trocar: CA-03det L34/L36; IN-01 L39 → IN-01.dc.html (visão Ocorrências). | Médio | Nenhuma tela visível lista ocorrências; o app registra (MB-04) e a web só tem o link "Registrar ocorrência" do Meu dia (IN-01 L39). |
| CD-01 › detalhe do talhão | Detalhe do talhão escondido no formulário | função oculta em tela visível (atrás de formulário) | Levar para o visível | Cadastros › Fazendas e talhões › clique na linha abre o detalhe | Detalhe em 1 clique; editar vai para o ⋯. |  | Médio | Hoje o clique abre o formulário de edição e o detalhe só abre por botão dentro dele (GES-24). |
| CO-06 | Qualidade e rastreabilidade | só por link dentro de outra tela | Levar para o visível | Agrícola › Estoque de produto › painel do lote › seção "Rastreabilidade" com "Simular recolhimento" | Árvore do lote: talhão e O.S. de colheita → carga → beneficiamento → lote → cargas e clientes; simulação de recolhimento mesmo com saldo zero. | Depois apagar a tela. Links a trocar: IN-04 L7823/L7935/L7941/L7947; PROD L5464 → PROD.dc.html#<lote>. | Alto | Só o CO-06 tem árvore de lotes e "Rastrear clientes" (nenhuma tela visível fala de recolhimento). O PROD já guarda as origens do lote (prOrigCampo, PROD L3478). |
| GE-01 | Visão gerencial | órfã (nenhum link leva até ela) | Levar para o visível | Agrícola › Custos e fechamento (GE-03) › visão "Resultado da safra"; link no Mapa do gestor | Resultado por cultura (receita prevista, margem, custo unitário, capital com terra, ROIC); causas prioritárias; "Qualidade dos dados 96%" abrindo o que falta (GES-21). | Órfã: nenhum link entra. A trilha diz "Gestão e resultados", grupo que não existe: usar o nome do hub. Depois apagar a tela. | Alto | Receita, margem e ROIC só existem aqui. GES-01: o proprietário não chega ao resultado por nenhum caminho. |
| GE-06 | Indicadores operacionais | só por link dentro de outra tela | Levar para o visível | Manutenção › Painel (PMAN) › "Desempenho dos ativos"; Agrícola › Painel (PAGR) › indicadores agronômicos | Disponibilidade, utilização, MTBF, MTTR e custo/h por ativo; custo de pulverização por ha tratado e aderência ao dia previsto, abrindo o recorte que forma o número (GES-20). | Depois apagar a tela. Nenhum link de tela que fica. | Médio | MTBF e MTTR só existem aqui; o PMAN tem 4 cartões sem clique (SUP-23). |
| IN-01 | Meu dia | só por link dentro de outra tela | Levar para o visível | Barra › Mapa (IN-04) › cabeçalho: atalho "Meu dia · N"; página inicial do operador e do almoxarife (UX-05) | Fila do dia com a ação no próprio item (P02); filtro "Meu" / "Equipe" (OS-30); clique abre a decisão de origem ao lado e, feito, a próxima (OS-10); recebe a visão Calendário da Agenda (IN-03) e a visão Ocorrências (CA-03). | A tela fica. Trocar os destinos ocultos da fila (IN-01 L58): CA-02 → OS filtro "A conferir"; PL-05 → OS.dc.html#OS-0420; LO-02 → EXPED; CO-06det → PROD.dc.html#L27-013. "Registrar ocorrência" (IN-01 L39 → CA-03) vira formulário no próprio Meu dia. | Alto | Decisão fixa UX-05 manda o operador e o almoxarife entrarem pelo Meu dia; hoje só o app leva até ela (MB-01 L22). |
| IN-02 | Aprovações | só por link dentro de outra tela | Levar para o visível | Barra › Mapa (IN-04) › cabeçalho: atalho "Aprovações · N"; página inicial do agrônomo (UX-05) | Caixa única de decisões com cada O.S. A liberar com produto, uma por vez, "aprovou, abre a próxima" (UX-06, OS-04); painel da decisão ao lado (OS-10); entra aqui também a aprovação de pagamento se o financeiro ficar no Safrion (GE-04). | A tela fica. Tirar "Aprovar selecionados" (OS-32; decisão fixa: aprovação individual). Trocar destinos (IN-02 L58): SU-09 → EST etapa "Faça contagens"; SU-02 → CD-06 item › Reposição. Hoje a única entrada é GE-04 (L58). | Alto | Decisão fixa UX-05/UX-06. Lista 4 itens e nenhuma O.S., embora 5 O.S. com produto aguardem o agrônomo (OS-04, IN-02.dc.html:58). |
| IR-01 › seletor de etapas | Etapas da Irrigação escondidas num menu suspenso | função oculta em tela visível (menu suspenso) | Levar para o visível | Agrícola › Irrigação › abas "Necessidade · Ordens · Clima e sensores" | Trocar o menu suspenso "Confira a necessidade ▾" por abas à vista; "Programar" vira modal no próprio IR-01. |  | Médio | As 3 telas irmãs só aparecem dentro do menu suspenso (IR-01, barra "etp-lista"). |
| LO-02det | Conferir carga · T2 · VD-2101 | só por link dentro de outra tela | Levar para o visível | Comercial › Expedição › painel da carga › "Verificação da saída" | Checklist antes de "Confirmar saída": NF-e autorizada, lacre (número e foto, POS-22), conferência do lote por leitura, bruto e tara pela balança (POS-11). | Depois apagar a tela. Nenhum link de tela que fica. | Alto | O EXPED confere lote, qualidade, carência, reserva e crédito, mas não NF nem lacre (POS-06). |
| MB-05 › aba Almoxarife | Aba do almoxarife sem fila | função oculta em tela visível (por perfil) | Levar para o visível | App › Almoxarifado › aba Almoxarife › fila "A separar" | Requisições liberadas por início da janela, com lote, validade e local; "Separar → Entregar a <operador>" (OS-06). |  | Alto | A aba aparece pelo perfil e só mostra 3 blocos fixos; a REQ-039 da OS-0424 não aparece (OS-06). |
| MB-05det | Receber devolução | órfã (nenhum link leva até ela) | Levar para o visível | App › Almoxarifado (MB-05) › aba Almoxarife › bloco "Receber devolução · REQ-031" | Receber devolução por QR com a quantidade contada, sem pré-preencher (OS-27). | A tela fica; criar o link no bloco. | Médio | Órfã: o bloco da aba Almoxarife não tem link (OS-27). |
| MB-08 | Irrigação de hoje | órfã (nenhum link leva até ela) | Levar para o visível | App › Minha fila / Minhas ordens › ordem de irrigação (OS-0419) › "Abrir ordem" | Execução da volta: lâmina, andamento, pausar ou retomar com motivo, confirmar término. | A tela fica; criar o link no cartão da ordem de água. | Alto | Órfã: o MB-01 não tem atalho de Irrigação e nenhuma tela abre a MB-08; o irrigante não confirma término no app. |
| OS › colunas ocultas | Situação e próximo passo escondidos | função oculta em tela visível (coluna escondida) | Levar para o visível | Agrícola › Ordens de serviço › coluna padrão "Situação · próximo passo" | Situação, quem resolve e próxima ação em texto, à vista. |  | Médio | Existem, mas ficam em "Colunas +12"; o impedimento aparece só como ícone (OS-11). |
| PL-04 | Programação integrada | só por link dentro de outra tela | Levar para o visível | Agrícola › Ordens de serviço › ação "Emitir O.S. do período" (hoje, 7 ou 14 dias) | Prévia de emissão: já emitidas, novas elegíveis, aguardando dados, fora do período; emitir em lote, nascendo A liberar (P23, P34). | NÃO levar "Liberar prontas": liberou a OS-0430 com defensivo em lote, contra a decisão fixa (AGRO-01). Depois apagar a tela. Nenhum link de tela que fica. | Alto | A OS cria uma O.S. por vez (OS-31). Só PL-04 e CA-01 emitem o período a partir do plano. |
| PL-05det | Impedimento · OS-0431 ativo bloqueado | só por link dentro de outra tela | Levar para o visível | Agrícola › Ordens de serviço › painel da O.S. › impedimento › propostas lado a lado; primária "Alocar Trator 02 a partir de 24/09" | Comparar substituir, aguardar reparo ou terceirizar (custo, risco, início) e confirmar o substituto também com a O.S. em execução. | Depois apagar a tela. Nenhum link de tela que fica. | Alto | No painel da O.S. "Trocar recurso" só existe antes da execução (OS-13); só aqui se decide a substituição. |
| SU-01 | Necessidades e cobertura | só por link dentro de outra tela | Levar para o visível | Suprimentos › Compras › etapa "Confira a demanda" (coluna "Pedir até") e Painel (PSUP) › "Faltas atrasadas" | "Pedir até" (necessária − prazo do fornecedor − segurança), itens atrasados e "Comprar urgente" com item, quantidade e data preenchidos (SUP-02). | Depois apagar a tela. Nenhum link de tela que fica. | Alto | Só aqui a falta firme vem com a data limite de pedido; 5 itens já atrasados e a tela não oferece caminho urgente (SUP-02). |
| SU-02 | Políticas de estoque | só por link dentro de outra tela | Levar para o visível | Cadastros › Produtos e locais (CD-06) › item › seção "Reposição" | Mínimo / ponto de pedido, máximo e criticidade por item e depósito; exceção vai para Aprovações. | Não levar ABC financeira, método e limite econômico. Depois apagar a tela. Links a trocar: IN-02 L58 → CD-06.dc.html (item › Reposição). | Médio | O CMP gera reposição pelo ponto de pedido ("O estado salvo sem min/max lê a política da semente", CMP) e nenhuma tela visível edita esse valor (CD-06 sem "ponto de pedido"). |
| SU-05 | Contratos, pedidos e entregas | só por link dentro de outra tela | Levar para o visível | Suprimentos › Compras › etapa "Acompanhe a entrega" › agrupar por contrato | Contrato de fornecimento com saldo contratado, cargas liberadas e recebidas, "Reprogramar carga" e exposição contra o limite do fornecedor. | Depois apagar a tela. Links a trocar: GE-04 L58 → CMP.dc.html (Acompanhe a entrega). | Médio | O CMP acompanha pedido, mas não contrato com cargas sob demanda (CT-2026-11 KCl 140 t). |
| SU-06 | Recebimentos e divergências | só por link dentro de outra tela | Levar para o visível | Suprimentos › Estoque › "Confira recebimentos" › "Ler NF-e / QR" | Ler XML, chave ou QR da NF-e e gravar "conferido como na nota"; só a divergência é digitada (UX-09, SUP-05). | Depois apagar a tela. Links a trocar: GE-02det L58; GE-03 L58 → EST.dc.html (Confira recebimentos). | Alto | O EST pede 11 campos e o almoxarife digita 5; a leitura de NF existe só aqui (SUP-05). |
| SU-08 | Transferências e movimentos | só por link dentro de outra tela | Levar para o visível | Suprimentos › Estoque › "Acompanhe movimentos" (⋯ do movimento) e "Confira saldos" (⋯ do lote) | Transferir entre locais (em trânsito, confirma no destino), Registrar perda com aprovação, Estornar com vínculo (P17, P19). | Depois apagar a tela. Nenhum link de tela que fica. | Alto | O EST só mostra o extrato; transferir, perda e estorno só existem aqui. |
| Tabelas › ⋯ da linha | Menu ⋯ que só aparece em tabela com excluir | função oculta em tela visível (depende de configuração) | Levar para o visível | Fim de toda linha com ação (padrão da tabela) | ⋯ sempre visível quando a linha tem ação, próximo passo primeiro, excluir por último. |  | Alto | O ⋯ só aparece quando a tabela permite excluir; nas de Suprimentos e Manutenção nunca aparece e as ações viram links soltos (SUP-07). Pedido do proprietário em 15/10: "coloque os 3 pontinhos". |
| BO-01 | Planos e preços | só via Outros acessos e links | Decidir com o proprietário | Fora do menu da fazenda (app de administração próprio) ou apagar | Simulação por área (PRECO-03). |  | Médio | Preços e mínimos são "exemplo, a decidir pelo proprietário (DEC-01/05/09)". Ferramenta da plataforma, não da fazenda. |
| BO-02 | Assinaturas e cobrança | só em Outros acessos | Decidir com o proprietário | Tirar de Outros acessos; app de administração separado, com login próprio |  |  | Médio | Mostra cobrança de outras organizações (Fazenda Aurora inadimplente) a quem abre Outros acessos; risco de isolamento entre clientes (dica do BO-02). |
| GE-04 | Contas a pagar e caixa | só por link dentro de outra tela | Decidir com o proprietário | Se o financeiro ficar no ERP: apagar e mostrar só o estado do título em CMP e EST. Se ficar no Safrion: hub Crédito › Contas a pagar. | Aprovação de pagamento por alçada na caixa de Aprovações (IN-02). | Hoje é a única entrada do IN-02 (GE-04 L58). | Médio | Dica: "Fonte oficial: ERP designado; aqui se propõe, aprova e concilia". "Enviar remessa ao banco" sem prévia (GES-07). Escopo comercial do produto. |
| GE-05 | Contas a receber | só por link dentro de outra tela | Decidir com o proprietário | Se ficar: hub Crédito › Contas a receber e "Enviar à cobrança" na venda (POS-18). Se não: apagar. | Estado do título na venda. | Aponta só para telas legadas (VE-04 ×6, VE-06 ×5). | Médio | Mostra R$ 244 mil vencidos; o PCOM mostra R$ 91.470 a receber (POS-07). Escopo comercial. |
| MOD-OUT | Outros acessos | hub da barra | Decidir com o proprietário | Barra › Outros acessos (nome fixo) só com "App de campo" e, se ficar, "Portal do parceiro" | App de campo. | Tirar Backoffice (BO-02) e Onboarding (ON-01) da lista. | Médio | Mistura quatro públicos: operador (app), parceiro externo (portal), cliente novo (onboarding) e operador do SaaS (backoffice). |
| ON-01 | Entrada e implantação guiada | só em Outros acessos | Decidir com o proprietário | Fora do menu: abre sozinho na 1ª entrada da organização nova e some ao concluir; faixa "Implantação: passo 3 de 6" no Mapa | Passos retomáveis; convite com os mesmos papéis da CF-01 (GES-26). |  | Médio | Depende do modelo de venda (trial próprio × implantação assistida). Wizard linear: foge do master-detail de propósito. |
| PT-01 | Portal do parceiro | só em Outros acessos | Decidir com o proprietário | Fora do menu da fazenda: login próprio do parceiro |  |  | Médio | Público externo (fornecedor, comprador, banco). Escopo do ecossistema. |
| PT-02 | Cotações concedidas | só via Outros acessos e links | Decidir com o proprietário | Se o portal ficar: entrada do fornecedor pelo convite, sem lista |  |  | Baixo | Lado do fornecedor da cotação do CMP. |
| PT-02det | Proposta · SOL-2026-07 · Fertilizantes | só via Outros acessos e links | Decidir com o proprietário | Se o portal ficar: tela única do fornecedor, aberta pelo convite | Preço editável na tabela e "Colar da planilha" (POS-30); primária = responder esclarecimento (POS-29). |  | Médio | É onde o fornecedor responde a cotação; sem ela, cotação por e-mail ou WhatsApp. |
| PT-03 | Ofertas | só por link dentro de outra tela | Decidir com o proprietário | Se houver venda pelo portal; senão apagar |  |  | Baixo | Comprador vê ofertas e faz proposta. |
| PT-04 | Crédito | só por link dentro de outra tela | Decidir com o proprietário | Se o portal ficar: entrada do banco |  |  | Baixo | Lado do banco do dossiê de crédito. |
| PT-04det | Dossiê · CRE-0102 custeio | só por link dentro de outra tela | Decidir com o proprietário | Se o portal ficar | "Recusar crédito" com motivo obrigatório (POS-25). |  | Baixo | Dossiê do banco. |
| PT-05 | Negócios e documentos | só via Outros acessos e links | Decidir com o proprietário | Se o portal ficar |  |  | Baixo | Negócios do fornecedor. |
| PT-05det | Negócio · CT-2026-11 KCl 60% | só via Outros acessos e links | Decidir com o proprietário | Se o portal ficar | "Enviar XML da NF-e" da carga (POS-31). |  | Médio | Fornecedor envia NF e laudo por carga. |
| PT-07 | Perfil e assinatura | só via Outros acessos e links | Decidir com o proprietário | Se houver plano pago para parceiro |  |  | Baixo | Assinatura do parceiro = monetização ainda não decidida. |
| AG-03 | Diagnósticos | só por link dentro de outra tela | Excluir | AG-01 (Decisão e receituário) |  | Levar "hipótese · causa" e "evidências vinculadas" (vistoria + laudo, por seleção, AGRO-30) para a seção Decisão da vistoria no AG-01. Links a trocar: AG-01 L5578 → AG-01.dc.html#VIS-011. | Baixo | Só 4 diagnósticos e sem primária (AGRO-28). O AG-01 já decide o controle e emite o receituário: "a O.S. nasce em A liberar" (AG-01 L5171). |
| AG-03det | Diagnóstico · DIA-007 nematoide T4 | só por link dentro de outra tela | Excluir | AG-01 (vistoria) e AG-02 (laudo) |  | Mesma migração do AG-03. Links a trocar: AG-01 L5578; AG-01det L48; AG-02 L5128 → AG-01.dc.html#VIS-011. | Baixo | Detalhe de um caso de demonstração (DIA-007); a cadeia vistoria → decisão → O.S. → leitura pós já está no AG-01. |
| AG-06 | Eficácia e histórico | só por link dentro de outra tela | Excluir | AG-01 (leitura pós e redução observada) |  | Se quiser, levar o cartão "Economia do MIP" (aplicações evitadas) para PAGR › MIP · onde agir. No Mapa, "Ver histórico do talhão" (camada Satélite) passa a abrir o talhão. Links a trocar: AG-01det L48; IN-04 L7711/L7822 → CD-01det.dc.html#talhao=… (Mapa) e AG-01.dc.html#VIS-… (AG-01det). | Baixo | O AG-01 já programa a leitura pós e calcula a redução observada (AG-01 L5121, L5178). "Registrar parecer" grava texto pronto sem formulário (AGRO-29). |
| CA-01 | Ordens de campo | só por link dentro de outra tela | Excluir | OS (Ordem de Serviço) |  | A emissão do período vai pelo PL-04. Não levar "Liberar selecionadas" (libera O.S. com produto em lote, contra a decisão fixa; OS-05). Links a trocar: GE-03 L58 → OS.dc.html. | Baixo | Segunda listagem da mesma O.S. com colunas e regras diferentes (OS-17). |
| CA-01det | OS-0421 · Fungicida 1ª aplicação | só por link dentro de outra tela | Excluir | OS (painel da O.S.) |  | Conferir no painel da OS a custódia da equipe com "Pedir entrega do restante" (OS-22). Links a trocar: IN-04 L6346/L7211; OS L5021; PAGR L6183 → OS.dc.html#OS-0421. | Baixo | Página cheia só para 2 de 21 O.S. ("Abrir ordem completa ›", OS L5021); a primária leva ao app MB-03 (OS-17). |
| CA-01x-os0420 | OS-0420 · Plantio Soja 58 W | só por link dentro de outra tela | Excluir | OS (painel da O.S.) |  | "Alocar substituto" vai para o painel (ver PL-05det). Links a trocar: AG-07 L5045; CA-03det L58; IN-04 L6346/L7211; OS L5021; PAGR L6183 → OS.dc.html#OS-0420. | Baixo | Mesmo caso do CA-01det, só para a OS-0420; primária "Acompanhar OM-0233" em vez de alocar o Trator 02 (OS-13). |
| CA-04 | Minhas requisições | só por link dentro de outra tela | Excluir | EST (Custódia e devoluções) e app MB-05 (Minhas retiradas) |  | Se faltar no painel da O.S., levar "Solicitar material da ordem" com itens e quantidades da versão (OS-20). Nenhum link de tela que fica. | Baixo | A própria dica diz: "É o mesmo registro de Suprimentos e do Estoque". |
| CO-01 | Previsão e maturação | só por link dentro de outra tela | Excluir | COLH (Previsão e colheita) |  | Nada essencial; "qualidade da previsão (WAPE, viés)" só se o proprietário pedir. Nenhum link de tela que fica. | Baixo | COLH já prevê, publica e mostra por semana. Base antiga: OC-0510 no T7 aqui × OS-0510 no Pivô 6 na OS. |
| CO-02 | Programação e ordens de colheita | só por link dentro de outra tela | Excluir | OS (O.S. de colheita) e COLH |  | Nenhum link de tela que fica. | Baixo | Ordem de colheita já é O.S. (OS-0505, OS-0510). Base antiga: OC-0510 no T7 aqui × OS-0510 no Pivô 6 na OS. |
| CO-02det | OC-0510 · Colheita de mamão T7 | só por link dentro de outra tela | Excluir | OS (painel) |  | Nenhum link de tela que fica. | Baixo | Detalhe de ordem duplicada; "Horas de equipe" vem pré-preenchida "8 × 3,0 h" (POS-34). |
| CO-03 | Cargas, pesagens e romaneios | só por link dentro de outra tela | Excluir | CARGA (Cargas e recebimento) |  | Nenhum link de tela que fica. | Baixo | CARGA registra carga e pesagem. Aqui o botão reemite romaneio já emitido (POS-33). |
| CO-04 | Recebimento da produção | só por link dentro de outra tela | Excluir | CARGA (recebimento) e EXPED (devolução volta em inspeção) |  | Conferir se o CARGA segrega carga com problema; se não, levar "Segregar carga". Nenhum link de tela que fica. | Baixo | Mesmo recebimento da produção. |
| CO-05 | Beneficiamento | só por link dentro de outra tela | Excluir | BEN (Beneficiamento) |  | Nenhum link de tela que fica. | Baixo | Mesmas ordens de processo com balanço. |
| CO-05det | OB-0110 · Packing do mamão | só por link dentro de outra tela | Excluir | BEN (painel da ordem) |  | Nenhum link de tela que fica. | Baixo | Mesmo detalhe da ordem de beneficiamento. |
| CO-06det | INSP-88 · Lote L27-013 bloqueado | só por link dentro de outra tela | Excluir | PROD (Registrar resultado e decisão) |  | Levar "padrão × medido por critério" para o formulário "Registrar resultado" do PROD (POS-13). Não levar a primária verde que libera lote não conforme (POS-24). Links a trocar: IN-01 L58 → PROD.dc.html#L27-013. | Médio | Detalhe da inspeção em base antiga (L27-013). |
| CO-07 | Estoque de produção | só por link dentro de outra tela | Excluir | PROD (Estoque de produto) |  | Nenhum link de tela que fica. | Baixo | Mesmo saldo por lote, classe e local, em base antiga. |
| Ferramentas de demonstração | Restaurar demonstração e perfil de teste | função oculta em tela visível (⋯ e avatar) | Excluir | Menu do avatar |  | Deixar uma entrada só no menu do avatar, junto de "Trocar perfil": "Restaurar demonstração" e "data simulada da cobrança". | Baixo | "Restaurar demonstração" se repete no ⋯ de AG-01, COLH, CARGA, BEN, PROD, EST, PCOM, VEN, EXPED, MA e MB-01, e o estado é um só. O perfil "todos os papéis" foi pedido em 14/10 e fica enquanto houver teste. |
| GE-06det | Detalhar · custo de pulverização | só por link dentro de outra tela | Excluir | GE-02det |  | Levar "Hipótese a validar" com ação (GES-22) e "Documentos de origem" para o GE-02det. Links a trocar: GE-02det L48/L58 → tirar o link (conteúdo vai para o próprio GE-02det). | Baixo | Mesmo desvio OS-0409 com a mesma ponte (+R$ 800, +R$ 480, +R$ 528) do GE-02det (GES-18). |
| GE-07 | Planos de ação | só por link dentro de outra tela | Excluir | Meu dia (tarefa com dono e prazo) e GE-02det (proposta de parâmetro) |  | "Criar ação do desvio" vira "Criar tarefa" vinculada no Meu dia, com dono e prazo herdados (GES-02). Links a trocar: GE-02det L39 → IN-01.dc.html (Criar tarefa). | Baixo | Lista paralela de casos; os links abrem sem o desvio de origem e pedem 7 campos (GES-02). |
| GE-08 › #vis= | Recortes da GE-08 pelo hub Crédito | função oculta em tela visível (só por endereço com #) | Excluir | GE-08 |  | O item "Crédito" da barra abre a GE-08 inteira (nome da barra fica); os 4 links do hub somem (GES-23). | Baixo | O hub Crédito tem 4 links que abrem a mesma GE-08 escondendo seções por #vis=contratos/liberacoes/dossie/documentos (GE-08 L2455); dentro da tela não há como trocar. |
| IN-03 | Agenda e pendências | órfã (nenhum link leva até ela) | Excluir | IN-01 (Meu dia) |  | Levar para o Meu dia a visão Calendário/semana e "Criar tarefa vinculada" com busca do registro (OS-37). Órfã: nada aponta para ela. | Baixo | 5 dos 6 compromissos repetem o Meu dia com nomes e ações diferentes (OS-30; IN-03 L58 × IN-01 L58). P11: calendário é visão da mesma lista. |
| IR-02 | Programação | só por link dentro de outra tela | Excluir | IR-01 e IR-03 |  | Levar "Programar irrigação" para o próprio IR-01, com vários setores de uma vez (AGRO-12); a "Agenda por captação" vira visão Calendário do IR-03. Links a trocar: IN-04 L5722/L5740/L7211; IR-01 L46/L5722/L5740/L6032; IR-03 L46/L48/L5722/L5740; IR-03det L46/L5722/L5740; IR-04 L46/L5722/L5740 → IR-01.dc.html#programar=…. | Médio | Tela de passagem: o IR-01 manda para cá só para abrir o modal (#programar=). Agenda = mesmas ordens por hora (P11). |
| LO-01 | Programação de transporte | só por link dentro de outra tela | Excluir | EXPED (Hoje, Esta semana) |  | Links a trocar: GE-04 L58 → EXPED.dc.html. | Baixo | Agenda de docas, slots e agrupamento de entregas é escopo de armazém; o EXPED já programa a carga por data. |
| LO-02 | Expedições e cargas | só por link dentro de outra tela | Excluir | EXPED (carga programada → saída) |  | A aba "Motorista" do MB-10 depende desta fila e sai junto. Links a trocar: IN-01 L58 → EXPED.dc.html. | Baixo | Fila de portaria com política de prioridade e docas (FILA-07). Fazenda típica não opera fila de pátio; manter só se o proprietário quiser módulo de armazém. |
| LO-03 | Viagens e entregas | só por link dentro de outra tela | Excluir | EXPED (Entregue, Registrar devolução) |  | Links a trocar: GE-05 L58 → EXPED.dc.html. | Baixo | Entrega e recusa já são estados da carga no EXPED. |
| LO-04 | Fretes e transportadores | só por link dentro de outra tela | Excluir | EXPED (transportador) e ERP (conta do frete) |  | Se faltar, levar só o valor do frete para a carga do EXPED. Links a trocar: GE-03 L58 → EXPED.dc.html#RM-…. | Baixo | "Contratar Rota Sul" contrata num clique, sem resumo (POS-21); pagamento do frete é do financeiro. |
| MA-01 | Manutenção | redireciona para MA | Excluir | MA (Sem ordem, Ordens, Ativos, Planos) |  | Nenhum link aponta (busca em v3). O MA já abre por #vis=, #om= e #plano=. Risco só para endereço salvo fora do protótipo. | Baixo | Arquivo de 1 linha que só redireciona ("Esta tela agora é a Manutenção"). |
| MA-02 | Manutenção | redireciona para MA | Excluir | MA (Sem ordem, Ordens, Ativos, Planos) |  | Nenhum link aponta (busca em v3). O MA já abre por #vis=, #om= e #plano=. Risco só para endereço salvo fora do protótipo. | Baixo | Arquivo de 1 linha que só redireciona ("Esta tela agora é a Manutenção"). |
| MA-03 | Manutenção | redireciona para MA | Excluir | MA (Sem ordem, Ordens, Ativos, Planos) |  | Nenhum link aponta (busca em v3). O MA já abre por #vis=, #om= e #plano=. Risco só para endereço salvo fora do protótipo. | Baixo | Arquivo de 1 linha que só redireciona ("Esta tela agora é a Manutenção"). |
| MA-04 | Manutenção | redireciona para MA | Excluir | MA (Sem ordem, Ordens, Ativos, Planos) |  | Nenhum link aponta (busca em v3). O MA já abre por #vis=, #om= e #plano=. Risco só para endereço salvo fora do protótipo. | Baixo | Arquivo de 1 linha que só redireciona ("Esta tela agora é a Manutenção"). |
| MA-04det | Manutenção | redireciona para MA | Excluir | MA (Sem ordem, Ordens, Ativos, Planos) |  | Nenhum link aponta (busca em v3). O MA já abre por #vis=, #om= e #plano=. Risco só para endereço salvo fora do protótipo. | Baixo | Arquivo de 1 linha que só redireciona ("Esta tela agora é a Manutenção"). |
| MA-05 | Manutenção | redireciona para MA | Excluir | MA (Sem ordem, Ordens, Ativos, Planos) |  | Nenhum link aponta (busca em v3). O MA já abre por #vis=, #om= e #plano=. Risco só para endereço salvo fora do protótipo. | Baixo | Arquivo de 1 linha que só redireciona ("Esta tela agora é a Manutenção"). |
| MB-10 › aba Motorista | Aba Motorista do app | função oculta em tela visível (aba) | Excluir | EXPED |  | Sai com o LO-02. | Baixo | Mostra posição na fila de portaria (LO-02), que sai. |
| Main | Safrion | redireciona para IN-04 | Excluir | IN-04 (Mapa) |  | Nenhum link aponta. Confirmar que a publicação não usa o Main como página inicial (não dá para concluir pelo código). | Baixo | Só diz "O protótipo começa no Mapa". |
| OS › "Abrir ordem completa ›" | Página cheia de 2 O.S. | função oculta em tela visível (só em 2 registros) | Excluir | OS (painel) |  | Some junto com CA-01det e CA-01x-os0420. | Baixo | Aparece só na OS-0420 e na OS-0421 (campo "link", OS L5021); as outras 19 O.S. não têm. |
| OS-0424-ficha | OS-0424 · ficha impressa | só por link dentro de outra tela | Excluir | OS-0424-app |  | Juntar à OS-0424-app como versão de impressão (as duas já têm @media print); levar a tabela de cargas (Feito, Hora) e "Entregue por / Recebido por". Links a trocar: OS L52; OS-0424-app L21 → OS-0424-app.dc.html (impressão). | Baixo | A mesma ficha em duas telas; P66 (sem PDF para cada coisa); colunas Feito e Hora em branco (OS-38). |
| PL-01 | Safras, ciclos e metas | só por link dentro de outra tela | Excluir | SAF (etapas Escolha a safra e Defina cultivos e planos) |  | Conferir no SAF "Autorizar execução" (só com plano e orçamento aprovados) e "Encerrar período"; um só "Criar safra" que copia a anterior (AGRO-10). Nenhum link de tela que fica. | Baixo | A mesma safra e a mesma grade de cultivos em duas telas, com formulários diferentes (AGRO-09, AGRO-10). |
| PL-02 | Plano operacional | só por link dentro de outra tela | Excluir | SAF (Defina cultivos e planos) e PA |  | Conferir no SAF "Decidir pendência de operação vencida" sem valor pré-escolhido (AGRO-08) e "Gerar sugestões pelas análises"; levar se faltar. Links a trocar: AG-01det L48 → SAF.dc.html#saf=S2627&passo=operacoes. | Baixo | Plano operacional já é etapa do SAF (SAF.dc.html#passo=operacoes). |
| PL-02det | Plano do talhão T1-A · gatilhos | só por link dentro de outra tela | Excluir | SAF (ajuste local) |  | Levar "ajuste local × padrão" por talhão se o SAF não mostrar a diferença. Nenhum link de tela que fica. | Baixo | Sub-detalhe do PL-02, que sai. |
| PL-03 | Capacidade e recursos | órfã (nenhum link leva até ela) | Excluir | SAF (Dimensione operações e recursos) e OS (Carga por recurso) |  | Se quiser, levar "cenários para o déficit" (2º turno, aluguel) para a etapa 3 do SAF. Órfã. | Baixo | O SAF já calcula capacidade e déficit; a tabela de manutenções repete a do PL-04 (AGRO-22). |
| PL-05 | Impedimentos e reprogramação | só por link dentro de outra tela | Excluir | PAGR (O.S. · onde agir primeiro: por causa e por quem resolve) e selo Impedida na OS |  | Levar "Aplicar alternativa" (AGRO-17) para o ⋯ da O.S. impedida. Links a trocar: CA-03det L58; IN-01 L58 → OS.dc.html#OS-… (O.S. impedida). | Baixo | O PAGR já agrupa impedimentos por causa e por quem resolve; o selo fica na O.S. (dica do PL-05). |
| PL-06 | Parcelas e escalonamento | só por link dentro de outra tela | Excluir | SAF (Dividir em parcelas) e COLH/PCOM (oferta por semana) |  | Nenhum link de tela que fica. | Baixo | O próprio PL-06 manda usar "Dividir em parcelas" do Planejar safra (AGRO-09). |
| PM | Manutenção | redireciona para MA | Excluir | MA (Sem ordem, Ordens, Ativos, Planos) |  | Nenhum link aponta (busca em v3). O MA já abre por #vis=, #om= e #plano=. Risco só para endereço salvo fora do protótipo. | Baixo | Arquivo de 1 linha que só redireciona ("Esta tela agora é a Manutenção"). |
| PT-06 | Indicadores | órfã (nenhum link leva até ela) | Excluir |  |  | Órfã: nada aponta. | Baixo | Indicadores do parceiro; a própria dica diz que benchmark entre clientes exige governança e consentimento. |
| SU-03 | Saldos e lotes de materiais | só por link dentro de outra tela | Excluir | EST (Confira saldos) |  | Nenhum link de tela que fica. | Baixo | Mesmos saldos por lote. Números divergem: F26-02 "Reserva em conflito" aqui e "Sem conflito" no SU-03det (SUP-06). |
| SU-03det | Lote F26-02 · reservas | só por link dentro de outra tela | Excluir | EST (painel do lote) |  | Se faltar, levar a "linha do tempo das reservas" para o painel do lote no EST. Nenhum link de tela que fica. | Baixo | Números divergentes do SU-03 (SUP-06). |
| SU-04 | Solicitações e cotações | só por link dentro de outra tela | Excluir | CMP (Solicite cotações, Compare propostas) |  | Nenhum link de tela que fica. | Baixo | Mesma cotação SOL-2026-07 ("é a mesma de Compra de insumos", dica); diz ao Proprietário "você não tem permissão para editar" (SUP-06). |
| SU-05det | CT-2026-11 · Fertisul · KCl 60% | só por link dentro de outra tela | Excluir | CMP (painel do contrato) |  | Vai junto com o SU-05; "Emitir liberação da carga 4" aparece 2 vezes e sempre bloqueado (SUP-32). Nenhum link de tela que fica. | Baixo | Detalhe do contrato do SU-05. |
| SU-07 | Requisições e entregas | só por link dentro de outra tela | Excluir | EST (Entregue por O.S.) |  | Se faltar, levar a sugestão FEFO do lote na separação. Links a trocar: GE-02det L58; GE-03 L58 → EST.dc.html (Entregue por O.S.). | Baixo | Mesmas requisições e entregas; ações soltas na célula (SUP-25). |
| SU-07det | REQ-031 · OS-0417 · MAP 11-52 | só por link dentro de outra tela | Excluir | EST (Receba devoluções) |  | Unificar o padrão de condição: aqui "quarentena", no EST "apta" (SUP-08); usar o padrão seguro. Nenhum link de tela que fica. | Baixo | Mesmo balanço da REQ-031. |
| SU-09 | Inventários e ajustes | só por link dentro de outra tela | Excluir | EST (Faça contagens) |  | "Planejar contagem" em lote (SUP-09) só se faltar no EST. Links a trocar: IN-02 L58 → EST.dc.html (Faça contagens). | Baixo | O EST já faz contagem cega, recontagem e aprovação do ajuste. |
| VE-01 | Demanda e oferta | só por link dentro de outra tela | Excluir | PCOM (Oferta e compromissos) |  | Nenhum link de tela que fica. | Baixo | Mesmo balanço oferta × compromissos. |
| VE-02 | Mercado e preços | só por link dentro de outra tela | Excluir | IV (Inteligência de vendas) |  | Se o proprietário quiser, levar "Criar alerta de preço" para o IV. Nenhum link de tela que fica. | Baixo | Mesmos preços e referência de mercado. |
| VE-03 | Ofertas e propostas | só por link dentro de outra tela | Excluir | VEN e IV (líquido por venda) |  | Nenhum link de tela que fica. | Baixo | O IV já compara preço e líquido por venda; o VEN registra a venda. |
| VE-04 | Pedidos de venda | só por link dentro de outra tela | Excluir | VEN (Contratos e pedidos) |  | Links a trocar: GE-05 L48/L58 → VEN.dc.html#PV-…. | Baixo | Duas versões da venda com números que não batem: R$ 244 mil aqui × R$ 91.470 no PCOM (POS-07). |
| VE-04det | Pedido PV-031 · Mamão Formosa A | só por link dentro de outra tela | Excluir | VEN (painel da venda) |  | Nenhum link de tela que fica. | Baixo | Detalhe do pedido legado. |
| VE-05 | Contratos e compromissos | só por link dentro de outra tela | Excluir | VEN (natureza Venda, CPR, Barter) |  | Links a trocar: GE-08 L58 → VEN.dc.html. | Baixo | O VEN já registra CPR e barter (VEN L5943); derivativos ficam fora. |
| VE-06 | Reclamações e devoluções | só por link dentro de outra tela | Excluir | EXPED (Registrar devolução com motivo) |  | Levar "evidência (foto ou laudo do cliente)" para o "Registrar devolução" do EXPED (POS-26). Links a trocar: GE-05 L48/L58/L2363 → EXPED.dc.html#RM-…. | Médio | O EXPED já registra devolução que volta em inspeção (EXPED L5976). |
| AG-01det | Rota e evidências | só por link dentro de outra tela | Manter como detalhe | Agrícola › Pragas e doenças › painel da vistoria › "Ver rota e evidências ›" | Pontos com GPS, hora, contagem × NC e fotos da rota. |  | Médio | Sub-detalhe natural da vistoria; AG-01 L5566 abre com #VIS-…. |
| CA-03det | OC-114 · Quebra do Trator T1 | só por link dentro de outra tela | Manter como detalhe | Meu dia › Ocorrências › linha; painel da O.S. › "Ver ocorrência" | Trilha e registros ligados (OM, O.S.). | Hoje entra por CA-03 e CA-01x (as duas saem): ligar à visão Ocorrências do Meu dia. | Médio | Detalhe da ocorrência; dica: "Encerrar a ocorrência não libera o Trator T1: o desbloqueio vem só da OM-0233". |
| CD-01det | Talhão | só por link dentro de outra tela | Manter como detalhe | Cadastros › Fazendas e talhões › clique no talhão; Mapa e CF-05 por #talhao= | Parcelas por safra e versões do polígono. |  | Alto | Detalhe natural do talhão; entra por CD-01 L2620 e L2649, IN-04 L8397, CF-05 L5063. GES-24: o clique na linha deve abrir aqui direto. |
| Faixa "Pagar fatura ›" | Pagar fatura | faixa no cabeçalho de todas as telas | Manter como detalhe | Mover: só no Mapa (IN-04) e em Configurações › Assinatura (CF-05), e só para quem tem a alçada AL-15 (gestor); nas outras telas, a restrição aparece no ponto de uso (CD-01 "Criar talhão" desligado com o motivo) | Aviso de fatura em atraso com a consequência ("talhão novo suspenso"). | Tirar "(data simulada da cobrança: …)" do texto fora do protótipo. | Médio | A faixa está no cabeçalho de todas as telas da organização (ex.: MOD-SUP L42) e só aparece com fatura "Em atraso" ou "Inadimplente" (assinAvisoVals); no cenário inicial (23/09, faturas pagas) não aparece, só ao avançar a data simulada. O link CF-05.dc.html#pagar não confere papel, mas só o gestor paga (AL-15). |
| GE-02det | Comparar · V1 × V2 × real | só por link dentro de outra tela | Manter como detalhe | Agrícola › Orçamento › "Comparar base × previsão × real" | Absorver do GE-06det as hipóteses a validar e os documentos de origem (GES-18). | Trocar "Abrir documentos de origem" (→ GE-06det) e "Criar ação do desvio" (→ GE-07). | Alto | Detalhe do desvio por operação (ponte V1 → real); entra pela primária do GE-02 (GE-02 L39). |
| IR-03 | Ordens de irrigação | só por link dentro de outra tela | Manter como detalhe | Agrícola › Irrigação › aba "Ordens" | Trocar o seletor ▾ do IR-01 por abas (ver função IR-01). |  | Alto | Ordens só com água vivem na Irrigação ("Irrigação só com água abre em Irrigação", dica do MB-02); a OS não lista OS-0419, 0422 e 0423. Entra por IR-01 L46 e OS L5054. |
| IR-03det | Ordem de irrigação | só por link dentro de outra tela | Manter como detalhe | Irrigação › Ordens › linha; OS L5054 (OS-0419); Mapa #OS-0422 e #OS-0423 | Passadas, recibos e primária "Iniciar irrigação". |  | Alto | Detalhe natural da ordem de irrigação. |
| IR-04 | Clima e sensores | só por link dentro de outra tela | Manter como detalhe | Agrícola › Irrigação › aba "Clima e sensores" | Na linha do sensor sem dado: "Pedir manutenção da sonda" e "Registrar leitura manual" (AGRO-32). Cadastro do sensor no CD-03 e outorga só na CD-01 (cadastro único). |  | Médio | Sensor sem dado muda o balanço (passa a estimar por ET). Só aqui se vê fonte e atualização dos sensores. |
| Links diretos por ID | Links diretos para registros | função oculta em tela visível (endereço com #) | Manter como detalhe | Endereços #OS-…, #VIS-…, #LAU-…, #OB-…, #PV-…, #RM-…, #L…, #sol=, #saf=&passo=, #ficha=, #pessoa=, #alc=, #talhao=, #ativo=, #om=, #plano=, #dev=, #painel= | Base para a busca por ID com "/" (UX-10) e para o drill-down dos painéis. |  | Médio | Abrem um registro ou recorte que também se alcança clicando; não escondem função. |
| MB-01 | Hoje no campo | só em Outros acessos | Manter como detalhe | Outros acessos › App de campo (no protótipo); no produto, o app instalado no celular | Minha fila e atalhos por tipo de trabalho. |  | Alto | Entrada do app de campo (UX-08 decidido). |
| MB-02 | Minhas ordens | só por link dentro de outra tela | Manter como detalhe | App › Minhas ordens |  |  | Médio | Lista das ordens do operador e da equipe. |
| MB-02det | Detalhe da ordem | só por link dentro de outra tela | Manter como detalhe | App › Minhas ordens › ordem |  |  | Médio | Detalhe da ordem no app (instrução liberada, insumos, apontamentos). |
| MB-03 | Apontamento do turno | só por link dentro de outra tela | Manter como detalhe | App › Minha fila › "Iniciar turno" / "Fechar turno" | Botão "Executado como planejado" (OS-07; P26). |  | Alto | Apontamento do turno. |
| MB-03x-recibo | Envios e recibos | só por link dentro de outra tela | Manter como detalhe | App › "Ver envios" |  |  | Médio | Fila de envio e recibos visível (UX-08, P37). |
| MB-04 | Registrar ocorrência | só por link dentro de outra tela | Manter como detalhe | App › Registrar ocorrência | Lista única de tipos com "Falta de insumo" (OS-24). |  | Alto | Ocorrência com foto, voz e sem sinal. |
| MB-05 | Almoxarifado móvel | no menu (por link do código comum); de fato só pelo app | Manter como detalhe | App › Almoxarifado (atalho do MB-01) | Fila "A separar" do almoxarife (OS-06). |  | Alto | Retirada e custódia no app. A navegação o marca "no menu" só por um link no código comum (trilha de auditoria); nenhum hub lista o MB-05. |
| MB-06 | Vistoria por pontos | só por link dentro de outra tela | Manter como detalhe | Agrícola › Pragas e doenças › "Coletar no app"; Mapa; Painel |  |  | Alto | Vistoria por pontos; entra por AG-01 L5162, IN-04 L5894, PAGR L7190. |
| MB-07 | Contagem de frutos | só por link dentro de outra tela | Manter como detalhe | Agrícola › Previsão e colheita › próximo passo "Coletar contagem" (app) |  |  | Médio | Contagem de frutos para a previsão; entra pelo próximo passo do COLH (código comum de produção) e pelo MB-01. |
| MB-08x-recibo | Irrigação · recibo do término | órfã (nenhum link leva até ela) | Manter como detalhe | App › Irrigação de hoje › "Confirmar término" |  |  | Médio | Recibo do término (lâmina, liberação, conferência automática). |
| MB-09 | Máquina | só por link dentro de outra tela | Manter como detalhe | App › Máquina |  |  | Alto | Abastecimento e leitura com 1 número (P61). |
| MB-09det | Ordem de manutenção | só por link dentro de outra tela | Manter como detalhe | App › Minha fila (mecânico) › ordem de manutenção |  |  | Alto | OM no app do mecânico (tarefas, peças, conclusão). |
| MB-10 | Cargas e entregas | só por link dentro de outra tela | Manter como detalhe | App › Cargas e entregas › aba "Colheita" | Aba Colheita (apontar área e registrar carga). | A aba "Motorista" sai junto com o LO-02. | Médio | A carga do talhão é a origem da produção (dica: "a produção do talhão nasce só da carga pesada e recebida"). |
| ON-01det | Importação · prévia e erros | só via Outros acessos e links | Manter como detalhe | Onboarding › passo 5 "Importação" | Reusar a mesma prévia (mapeamento, sistema de coordenadas, duplicidade, erro por linha) para "Importar talhões" na CD-01 (GES-06). |  | Médio | P22 (importar com prévia); a unidade do estoque inicial é única para a coluna (GES-09). |
| OS-0424-app | OS-0424 · ficha de campo | só por link dentro de outra tela | Manter como detalhe | Agrícola › Ordens de serviço › painel › "Ficha no app (sem internet) ›"; app MB-02det › "Abrir ficha do caldeiro" | Generalizar para toda O.S. com calda (hoje só a OS-0424); uma ficha com versão de impressão. |  | Médio | Ficha de preparo por carga para uso sem internet (retirada, lote, caldeiro, regulagem). Entra por OS L52 e MB-02det L26. |
