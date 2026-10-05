# Conferência da síntese "Planejamento, execução e controle"

**Base:** protótipo `884620c` (sp-tab5), PRD v3.9, `DECISIONS.md` e especificações `sp-specs 9c53fc2`.

**O que foi executado:**
- Python: páginas do `canvas.json`, `D2.demanda()`, `inicio.FAZST` e `dados_cad.LG_AGUA`.
- node: `cenario.js` mais o `JS_NUCLEO` de `processo_os.py`, com os scripts `os_sim.js`, `t6.js` e `t7.js` em `scratchpad/`.

**O que não foi feito:** nenhum navegador e nenhuma edição no repositório.

## A. Cada afirmação

### §1 Veredito
- **"Planejamento e execução têm telas próprias em todos os domínios":** confirmada para os 4 domínios do menu. Gestão não tem tela visível.
- **"A O.S. junta os dois por desenho, como deve":** confirmada (DEC-2609-04; PRD 72.3 l.12233).
- **"O controle quase todo está em telas ocultas com números fixos":** exagerada.
  - Há controle operacional visível:
    - conferência e encerramento da O.S.;
    - EST 4, 5 (aprovação de ajuste) e 6;
    - CMP 5 e 6;
    - IR-03det (hidrômetro × estimativa);
    - MA-01 (condição e utilização), MA-03 (vencidas) e MA-05 (diesel em L/h × referência, `maquinas.py:686-697`);
    - Mapa › Custos.
  - O que está oculto e fixo é o controle gerencial.
  - Esse ocultamento é decisão do recorte de validação (PRD 71.6 l.10359; `ui37.py:31-34`), não defeito de código.
- **"…e por isso o realizado não volta ao plano":** errada como causa. São dois problemas independentes:
  - o mesmo fato entra por dois canais;
  - a demanda considera feito o que estava planejado para antes de hoje (`cal01.js:14`).

### §2 Matriz
- **Agrícola:**
  - PA e SAF estão certos.
  - AG-07 é consulta ao Agrofit, não planejamento. O receituário só fica no estado da própria tela (`agronomia.py:1715-1716`).
  - AG-01 é vistoria mais decisão técnica (`agronomia.py:5-11`), não apontamento.
  - "O.S., só ao encerrar": confirmada (`processo_os.py:373-376`).
  - CA-02 oculta e fixa: confirmada (`campo.py:435-438`, página "ocultos"). Mas a O.S. (`processo_os.py:153`) e o Mapa (`inicio.py:1372`) abrem essa tela.
- **Irrigação:** confirmada. O desempenho do IR-04 é fixo (`irrigacao.py:549-555`).
- **Manutenção:**
  - "MA-01 sem disponibilidade técnica": exagerada. O MA-01 mostra condição técnica, utilização em 30 dias e vencidas (`maquinas.py:136-163`). Falta só o indicador de disponibilidade (KPI-PCM-01, PRD l.4648).
  - Faltaram MA-05 e MA-03 na coluna de controle.
  - Lacuna no GE-06: confirmada. Ele tem MTBF/MTTR e custo por hora fixos (`gestao.py:469-491`).
- **Suprimentos:**
  - SAF 6 = CMP 2: confirmada (`processo_safra.py:12`; `processo_compras.py:16`).
  - SU-02 oculta: confirmada.
  - "Acurácia e OTIF (SU-05/09 ocultos)": exagerada. O PRD põe esses indicadores em SU-09 e SU-05/06 (KPI-SUP-02/05, l.4656/4659), mas nem as telas ocultas os mostram (`suprimentos.py:614, 1103`).
- **Cadastros e Mapa:**
  - Cadastro é base, não planejamento.
  - Painel da O.S. no Mapa: confirmada (`inicio.py:818-827`).
  - "Mapa › Custos é o único previsto × realizado": exagerada. É o único de custo com dados vivos (`inicio.py:697-787`). Colheita mostra realizado × meta com dados fixos (`inicio.py:193-198`).
- **App:**
  - MB-06 está na página de ocultos, mas funciona com o estado do MIP (`mobile.py:749-785`) e o MB-01 abre a tela (`mobile.py:331`).
  - MB-05det e MB-07 a MB-10 só simulam: confirmada (`mobile.py:23`).
- **Gestão:** confirmada.

### §3 O que está bem separado
Tudo confirmado:
- PA (`processo_planos.py:1-5, 229`) e PM (`maquinas.py:1139`) com versão, sem mexer no que está em andamento;
- cadeia da irrigação;
- MIP: app coleta, agrônomo decide;
- água liberada sem agrônomo (`processo_os.py:302-303`);
- MA-03 gera a ordem em "A liberar" sem reservar (`dados_manutencao.py:353-373`; a reserva só ocorre na liberação, l.389);
- consumo acima da custódia conciliado no EST (`cenario.js:158-228`).

### §4 Problemas
1. **Ajuste de estoque:** confirmada.
   - "Aprovar ajuste" fica na mesma linha da contagem e não verifica quem aprova (`processo_estoque.py:482`).
   - O autor gravado é sempre "Ana (gestora)" (`cenario.js:113`; `processo_estoque.py:230, 301`).
   - A recontagem exige outro contador (l.331); a aprovação não exige.
   - A DEC-2609-13 manda o gestor aprovar o ajuste.
2. **EST:**
   - Quarentena liberada sem laudo: confirmada (`cenario.js:101-103`; `processo_estoque.py:554-559`).
   - "Aceitar consumo baixa o físico sem o gestor": o fato está confirmado (`cenario.js:216-219`). Mas é exagero chamar de violação: o PRD v3.9 não exige o gestor aqui, e o código segue o CMD-50 da v3.10, ainda em revisão. É decisão de política.
3. **CMP:** errada na pessoa, exagerada no dano.
   - O perfil é Ana, gestora com alçada de gerente da fazenda (`processo_compras.py:19`), não a compradora.
   - O botão existe (l.587) e grava "Direção (simulado)" (l.446).
   - O risco vale para o software real, não é defeito do protótipo.
4. **O.S.:**
   - A caixa de validação agronômica da dispensa: confirmada (`processo_os.py:921, 650`).
   - Revisão e liberação num comando só: confirmada (`processo_os.py:44-47`). A liberação não grava aprovação nenhuma (l.300-311).
   - O pedido de 01/10 está em comentários e testes (`os_v39_liberar_test.py`, `os_cenario_test.py`), não no PRD nem no DECISIONS.
   - Nuance: o PRD 41.3 (l.6864) admite "Aprovar e liberar" numa só confirmação, desde que registre o CMD-42 e o CMD-06 separadamente.
5. **Manutenção:**
   - "Apto antes de concluir": exagerada. Isso exige teste aprovado (`maquinas.py:642`), e o PRD 47.5 (l.7738) admite liberação técnica antes do fechamento. Não é falta de independência.
   - "Marcar pendentes como feitas": confirmada (`maquinas.py:461-462, 513`).
6. **Apontamento web + app:** confirmada, executado (`t6.js`).
   - Web 50 ha e app 50 ha levam a OS-0421 de 190 para 290 ha, e o Fungicida A de 95 para 145 L, sem aviso.
   - Só o saldo é checado (`processo_os.py:358-361`; `cenario.js:158-163`).
   - Na web, o consumo é sempre dose × área (`processo_os.py:361`).
   - O PRD OSDIA-04 (l.3034) exige detectar esse conflito.
7. **Início com entrega parcial:** confirmada, executado (`t7.js`, OS-0430 só com glifosato entregue).
   - A web recusa: "Iniciar bloqueado: REQ-041 sem entrega · 2,4-D 806 160 L, Óleo mineral 80 L".
   - O app inicia o turno.
   - Causa: `cenario.js:128-135` não chama `osIniErro` (`processo_os.py:344-351`), e o app só pede retirada quando nenhum item tem custódia (`mobile.py:200`).
8. **Trava legal:** parcialmente errada.
   - A carência também trava na O.S. (colheita: `processo_os.py:301, 353, 1138`; na aplicação é só aviso, l.1139).
   - Registro, bula, dose e número de aplicações só existem no AG-01 (`mip.js:229-267`): confirmada.
   - PA e SAF aceitarem qualquer dose é desenho do PRD 41.1 (l.6846).
   - O furo real é "Ajustar antes de liberar" (`processo_os.py:320-333`).
   - AG-07: dose fora da bula é só aviso (l.1702), e o receituário só fica no estado da tela.
9. **Outorga em duas fontes:** confirmada, executado.
   - Na irrigação, a SINT-002 tem 573 L/s, vencimento 22/11/2023, "Em renovação" (`dados_irrigacao.py:42`). Os pivôs usam esse valor (l.120), e a trava de vazão também (`irrigacao_estado.js:183-190`).
   - No cadastro, a SINT-002 tem 150 m³/h ≈ 41,7 L/s, vencimento 20/11/2026 (`dados_lagoa_sintetico/kml.py:61`, via `dados_cad.py:162`).
   - Também divergem vencimento e situação, e o comentário do código cita "SINT-001" (`dados_irrigacao.py:12`).
10. **Realizado não volta ao plano:** confirmada, executado.
    - A demanda S2627 de Fungicida A dá 545 de estoque, 625,2 de plano e 145,2 L líquidos.
    - Ela inclui c1|a6, c2|a6 e c3|a6, datadas de 29/11 a 09/12/2026, que a OS-0421 já executa com a REQ-035 entregue (160 L).
    - Mapa contra CMP: MAP 80.000 × 62.500 kg; Fungicida A 194 × 145,2 L (`inicio.py:336-372`).
11. **Condição e horímetro:** confirmada. Detalhe por tela:
    - Condição: MA-01 (só local, `maquinas.py:205-210`), MA-02 (l.221-238) e MA-04det (estado da tela, l.642-645).
    - Horímetro: CD-03 (`cad_ativos_pessoas.py:107, 180-181`), MA-04 (`maquinas.py:464`) e MA-05 (l.682).
12. **Estoque próprio da manutenção:** confirmada. O recebimento está em `dados_manutencao.py:399-401`; a baixa e a devolução, em l.415-447.
13. **"Gerar ordem" repetido no PM:** confirmada (`maquinas.py:89, 961, 1129`).
14. **Conferência só no encerramento:** confirmada (`processo_os.py:375`). A DEMO-13 do PRD (l.4734) pede conferência diária.
15. **Plano sem versão de referência:** confirmada. O SAF não tem "publicar"; a RN-031 (l.233) exige orçamento-base.
16. **Links para telas ocultas:** confirmada, e é mais ampla. Varredura dos HTML:
    - IR-04 → GE-07;
    - MA-01 → PL-04;
    - MA-02 → PL-05det;
    - MA-05 → MB-09;
    - MB-01 → MB-06 a MB-10;
    - IN-04 → CA-02, CO-06, PL-05.

### §5 e §6
- PRD 71.6: confirmada.
- **SAF 3-4-5:** são todas planejamento, confirmada.
- **PCM:**
  - "Especificado, nada implementado": confirmada.
  - Resolve o item 12 (PR 1b "Um estoque", `ESPECIFICACAO.md:521`) e cria a aprovação da OM (PCMS-M05, l.265): confirmada.
  - "Não trata o item 11": errada. A condição única está no Bloco 2 (PCMS-A01/A02, l.620, 676-677).
  - Não trata o horímetro único nem o "Gerar ordem" do PM ("PM mantida", l.384).
  - Mantém "Marcar pendentes como feitas" (l.459): confirmada.
- **Beneficiamento:**
  - R-A01 (l.295), R-A12 (l.335) e R-F02 (l.421): confirmadas.
  - Registro no DECISIONS (P1, l.23): confirmada.
  - "Aposentar CO-05/06/07": imprecisa. Saem CO-04, CO-05, CO-05det, CO-06det e CO-07; a seção de carência do CO-06 fica (l.86-87).
  - "Depende do item 11": exagerada. Depende do PCM 1a–1c e só precisa do Bloco 2 para impedir a ordem por causa do ativo (l.25, 159, 250).

## B. Síntese corrigida

# Planejamento, execução e controle estão bem separados?

**Base:** protótipo `884620c`, PRD v3.9, DECISIONS.md e especificações `sp-specs 9c53fc2`. Li o código e rodei simulações em Python e node; o que vem marcado "executado" saiu delas. Não usei navegador e não editei nada.

## 1. Veredito
**Em parte.** Nos quatro domínios do menu, planejamento e execução têm telas próprias. A O.S. junta os dois por desenho, como deve (DEC-2609-04).

O controle operacional existe nas telas visíveis: conferência e encerramento da O.S., saldos, contagem e ajuste, aprovação da compra, hidrômetro, diesel e Mapa › Custos. Ele falha em três pontos:
- **Independência:** em vários lugares quem registra também aprova, ou a aprovação é uma caixa marcada.
- **Controle gerencial ausente:** previsto × realizado da safra, orçamento-base, indicadores e custo por ativo só existem em telas ocultas com números fixos. Elas estão ocultas por decisão do recorte de validação (PRD 71.6); trazê-las é decisão sua.
- **Fato em dois canais:** o mesmo fato entra pela web e pelo app com regras diferentes.

À parte disso, a demanda considera feito o que estava planejado para antes de hoje, e não o que as O.S. realizaram.

## 2. Matriz (menu vigente)
| Domínio | Planejamento | Execução / apontamento | Controle |
|---|---|---|---|
| Agrícola | PA, SAF (AG-07 é consulta) | O.S.; AG-01 (vistoria e decisão técnica) | O.S., conferência só ao encerrar. **Lacuna:** conferência diária (CA-02, oculta e fixa, mas aberta pela O.S. e pelo Mapa); previsto × realizado (GE-02/03, ocultos) |
| Irrigação | IR-01, IR-02 | IR-03, IR-03det | IR-03det (hidrômetro × estimativa); IR-04 com desempenho fixo |
| Manutenção | PM, MA-03 | MA-02, MA-04, MA-05 | MA-01 (condição e utilização; falta o indicador de disponibilidade), MA-03 (vencidas), MA-05 (diesel L/h × referência). **Lacuna:** cumprimento de preventiva, MTBF/MTTR e custo por ativo (GE-06, oculto e fixo) |
| Suprimentos | Demanda (SAF 6 = CMP 2). **Lacuna:** política de estoque (SU-02, oculto) | CMP 3–6; EST 1–3 e 5 | CMP 5 e 6; EST 4, 6 e a aprovação de ajuste na 5. **Lacuna:** acurácia de inventário e OTIF (o PRD os põe em SU-09 e SU-05, ocultas, e nem elas os mostram) |
| Cadastros/Mapa | Cadastros são base; Mapa › Insumos | Painel da O.S. no Mapa | Mapa › Custos (único previsto × realizado de custo, vivo); Mapa › Colheita (realizado × meta, fixo) |
| App | — (correto) | MB-01 a MB-05; MB-06 funciona, mas está na página de ocultos; **MB-05det e MB-07 a MB-10 só simulam** | — (correto) |
| Gestão | **Lacuna:** orçamento-base (GE-02, oculto) | — | **Lacuna:** custo realizado, indicadores e planos de ação (GE-01/03/06/07, ocultos e fixos) |

## 3. O que está bem separado
- PA e PM têm versão e não mexem no que já está em andamento.
- Irrigação segue a cadeia necessidade → programação → execução → hidrômetro.
- MIP: o app coleta (MB-06) e o agrônomo decide (AG-01).
- **Misturas legítimas, que ficam como estão:**
  - a O.S. reúne plano, realizado e encerramento nas 5 fases (DEC-2609-04);
  - a água é liberada sem agrônomo (DEC-2609-10);
  - o recebimento confere nota × pedido;
  - o MA-03 gera a ordem em "A liberar" sem reservar;
  - o consumo acima da custódia é anotado no app e conciliado no EST.

## 4. Problemas, em ordem de dano

**Controle sem independência**
1. **Ajuste de estoque:** a linha da contagem oferece "Aprovar ajuste" sem verificar quem aprova, e a trilha grava sempre "Ana (gestora)" (`processo_estoque.py:482`; `cenario.js:113`). A DEC-2609-13 exige o gestor. No software, quem contou poderia aprovar a própria perda.
2. **Quarentena:** é liberada sem laudo, só com confirmação (`cenario.js:101-103`).
3. **O.S.:**
   - a validação agronômica da dispensa é uma caixa marcada por quem dispensa (`processo_os.py:921`);
   - revisão e liberação viraram um comando só, sem registro de aprovação (`processo_os.py:44-47, 300-311`), contra a DEC-2609-05. O pedido de 01/10 só está em comentários e testes do código.
4. **Checklist da manutenção:** "Marcar pendentes como feitas" fecha o checklist num clique (`maquinas.py:461-462`).
5. **Compra (risco do software real):** na CMP, quem envia à Direção registra a decisão dela, marcada "simulado" (`processo_compras.py:446, 587`). No software, aprova quem tem a alçada.

**O mesmo fato em dois lugares**
6. **Apontamento web e app sem checar sobreposição** (executado): a OS-0421 vai de 190 para 290 ha e o Fungicida A de 95 para 145 L, sem aviso.
   - Só o saldo é verificado.
   - Na web, o consumo é sempre dose × área (`processo_os.py:361`).
   - O PRD OSDIA-04 exige detectar o conflito.
7. **Entrega parcial** (executado): a web bloqueia o início e o app inicia (`cenario.js:128-135`; `mobile.py:200`). A aplicação começa com a mistura incompleta.
8. **Trava legal:**
   - Registro, bula, dose e número de aplicações só existem no AG-01 (`mip.js:229-267`).
   - A O.S. já trava a carência na colheita (`processo_os.py:301, 353`), mas "Ajustar antes de liberar" aceita qualquer dose (`processo_os.py:320-333`).
   - PA e SAF aceitarem qualquer dose é desenho do PRD 41.1.
   - O AG-07 diz "Receituário emitido" e grava só no estado da própria tela (`agronomia.py:1715-1716`).
9. **Outorga em duas fontes** (executado):
   - A SINT-002, que abastece os pivôs, tem 573 L/s e venceu em 2023 na irrigação (`dados_irrigacao.py:42`).
   - No cadastro tem cerca de 42 L/s e vence em 2026 (`kml.py:61`).
   - A trava de vazão usa o valor da irrigação.
10. **O realizado não volta ao plano:** "já realizado" é o que estava planejado para antes de hoje (`cal01.js:14`).
    - Executado: a Compra mostra falta de 145,2 L de Fungicida A, contando atividades de nov–dez/2026 que a OS-0421 já executa, com 160 L entregues.
    - O Mapa usa fórmula própria (`inicio.py:336-372`): MAP 80.000 contra 62.500 kg; Fungicida A 194 contra 145,2 L.
11. **Condição e horímetro sem fonte única:**
    - a condição técnica muda no MA-01 (só local, `maquinas.py:205-210`), MA-02 e MA-04det;
    - o horímetro muda no CD-03, MA-04 e MA-05.

**Fora do lugar**
12. O MA-04 recebe peça sem nota, baixa e devolve num estoque próprio da manutenção (`dados_manutencao.py:399-401, 415-447`).
13. O PM repete o "Gerar ordem" do MA-03 (`maquinas.py:89, 961`).

**Lacunas**
14. A conferência só acontece no encerramento, em massa (`processo_os.py:375`). A DEMO-13 pede conferência diária.
15. O plano não tem versão de referência (RN-031).
16. Telas visíveis levam a telas ocultas e fixas: PL-05 (`inicio.py:122`, `maquinas.py:323`), CA-02, GE-07, MB-06 a MB-10.

## 5. Recomendação essencial
Menu por camada ou tela nova não resolve: o menu por domínio (PRD 71.6) serve. O problema é fato sem dono único e controle sem lugar. Em ordem:
1. **Um comando por fato, igual em todos os canais:**
   - apontamento, com data e checagem de sobreposição;
   - início, com a mesma checagem de entrega;
   - condição técnica, horímetro, outorga e devolução;
   - trava de registro, bula e dose na liberação e no ajuste da O.S., com o mesmo serviço do AG-01 (ENG-011).
2. **Aprova quem decide:** ajuste de estoque, quarentena, validação agronômica da dispensa e, no software, aprovação da Direção.
3. **Fechar o laço nas telas que já existem:**
   - versão de referência publicada no SAF;
   - conferência diária dentro da O.S.;
   - realizado das O.S. alimentando a demanda e o custo.
4. **Uma entrada de Controle** (previsto × realizado da safra: custo, insumo, área e prazo), ligada ao estado vivo. Até ela existir, tirar os links para telas ocultas e as ações do app que só simulam.

**Para você decidir** (entre parênteses, o que faço se você não decidir):
- O.S. sem revisão (pedido de 01/10) ou DEC-2609-05? (registrar a de 01/10, com o nome de quem aprovou a versão no recibo da liberação)
- Entrada de Controle já nesta validação ou depois? (depois dos itens 1 e 2)
- Quem aceita consumo acima da custódia: o almoxarife, como hoje, ou o gestor? E quem aprova o ajuste quando uma pessoa acumula papéis? (o gestor; se for a mesma pessoa, fica registrada uma revisão posterior, como prevê o PRD 2.1)

## 6. Relação com os pedidos em andamento
- **Etapa única 3-4-5 do SAF** (pendente): as três etapas são planejamento, então juntá-las não mistura camadas. Ela deve terminar em "Publicar versão", que é a base do controle, sem trazer o realizado para dentro.
- **PCM × suprimentos** (especificado em `sp-specs 9c53fc2`, nada implementado):
  - resolve o item 12 (PR 1b "Um estoque") e cria a aprovação da OM antes de liberar;
  - trata a condição única do ativo no Bloco 2 (PCMS-A01/A02);
  - não trata o horímetro único nem o item 13, e mantém "Marcar pendentes como feitas" (`ESPECIFICACAO.md:459`). Sugiro incluir os três no 1a.
- **Beneficiamento** (especificado):
  - já nasce separado: 5 fases, "Concluir" leva a Em conferência, faixa de tolerância e correção com motivo (R-A01, R-A12, R-F02). É o modelo de conferência que falta à O.S. agrícola;
  - precisa da decisão registrada no DECISIONS.md;
  - aposenta CO-04, CO-05, CO-05det, CO-06det e CO-07; a seção de carência do CO-06 continua;
  - depende do PCM 1a–1c, e do Bloco 2 só para impedir a ordem por causa do ativo.

## C. O que corrigi
- **Veredito:** o controle operacional está visível; o oculto é o gerencial, e por decisão do recorte (PRD 71.6). Também tirei o "por isso", porque a dupla entrada não causa a falha do realizado.
- **Matriz:**
  - AG-07 é consulta; AG-01 é vistoria e decisão;
  - incluí MA-03, MA-05 e CMP 6 no controle;
  - o MA-01 tem condição e utilização, falta o indicador de disponibilidade;
  - acurácia e OTIF não existem nem nas telas ocultas;
  - Mapa › Custos é o único previsto × realizado de custo, não o único de todos;
  - MB-06 está na página de ocultos, mas funciona;
  - cadastro não é planejamento.
- **Item 2:** o consumo acima da custódia saiu dos defeitos e virou decisão de política (o PRD v3.9 não exige o gestor aqui).
- **Item 3:** não é a compradora, é Ana, gestora. A ação é marcada "simulado"; virou risco do software real.
- **Item 5:** retirei a parte "apto antes de concluir", porque exige teste e o PRD 47.5 permite.
- **Item 8:**
  - a carência já trava na O.S.;
  - PA e SAF aceitarem qualquer dose é desenho do PRD 41.1;
  - o furo é o ajuste antes de liberar;
  - o AG-07 grava só no estado da tela.
- **Itens 6, 9, 10, 12, 14 e 16:** acrescentei o reforço do PRD (OSDIA-04, DEMO-13), a divergência de vencimento da outorga, o caso do Fungicida A no Mapa, as linhas corretas da baixa e da devolução, e mais links para telas ocultas.
- **§6 PCM:** o item 11 é tratado no Bloco 2; o que falta é o horímetro e o "Gerar ordem" do PM.
- **§6 Beneficiamento:** corrigi a lista de telas a aposentar (o CO-06 fica pela carência) e a dependência (PCM 1a–1c, mais o Bloco 2 só para o ativo).