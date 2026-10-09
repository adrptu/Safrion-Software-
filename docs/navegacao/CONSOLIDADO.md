# NAV-20261009-01 · Consolidação cética (09/10/2026)

- **Pedido:** "veja se tem algum submenu redundante para enxugar e integrar, bem como telas e etapas de processo, assim como fizemos com planejar safra" (proprietário, repassado pelo Codex em https://github.com/adrptu/Safrion-Software-/pull/47#issuecomment-6080540795).
- **Base:** `/home/user/sp-proto` em `cdc185f` (= `ecc8b00` + varredura + logs).
- **Autor:** Claude (consolidador). **Revisor:** Codex.
- **Executado nesta consolidação:**
  - leitura de código por `arquivo:linha` nas amostras do §1;
  - `git merge-tree` entre as 13 branches;
  - contagem de links no `_render/Main.dc.html`;
  - leitura dos registros dos fluxos de trabalho (§0).
- **Nenhum teste foi rodado nesta consolidação.** Os resultados de teste citados vêm das mensagens de commit das frentes.

---

## 0. Pergunta do proprietário: "por que, em tarefas concluídas, várias estão em vermelho, sem concluir todas as etapas?"

**Resposta curta.** As tarefas em vermelho não falharam no trabalho. Elas foram **interrompidas**.

**O que aconteceu (executado, lido nos registros da sessão):**
- **Às 13:05:09 UTC (10:05 em Brasília), a sessão principal registrou uma interrupção** ("Request interrupted by user").
  - Nesse mesmo instante, **15 fluxos que estavam rodando foram abortados juntos**, com o estado `killed` e o erro "Workflow aborted".
  - Os fluxos abortados foram:
    - módulos CTL-4, CTL-5, DOM, PCM, SUP, BEN, SOLO, DS, COM, TABR e CONF;
    - SAF-C01 e SAF-C02;
    - o Parecer;
    - este NAV.
  - O painel mostra cada um como "concluído" em vermelho porque ele terminou antes da última fase.
- **Junto com os fluxos, 19 baterias de teste que eles rodavam em segundo plano foram encerradas** (`[killed]`), quase todas às 13:05:09. Algumas pararam no meio. Exemplo: a bateria `bdopcufos` parou no `matest.py`, sem resultado.
- **Entre 13:27 e 13:28 UTC, os 15 fluxos foram retomados.**
  - Cada um voltou na fase em que parou.
  - As fases já terminadas foram reaproveitadas do diário de cada fluxo. Exemplos:
    - no NAV, os 5 mapeamentos foram guardados e só a consolidação recomeçou, que é este documento;
    - no BEN, a implementação foi guardada e a revisão recomeçou.
  - Os agentes retomados refazem as verificações da fase interrompida.
- **Outras tarefas em vermelho, de antes, têm duas causas:**
  - **Bateria encerrada quando o agente que a lançou terminou.** Algumas já tinham terminado tudo antes de serem encerradas: `bchzyp6v1` imprimiu "DONE" e `b79j693tw` deu 48/48 OK. Ficam vermelhas, mas estão completas.
  - **Uma falha real de script de sondagem**, não de teste do produto: `b5b8yl3o5`, com "TypeError … querySelector", EXIT 1.
- **Dois fluxos mais antigos também ficaram em vermelho** e já foram substituídos por novas execuções:
  - DS, abortado às 11:13 e substituído por `wf_7f677d2f`;
  - Parecer, abortado às 12:50 e substituído por `wf_8b5839d9`.

**O que fazer:** nada a mais. O vermelho é o registro da execução interrompida. O resultado que vale é o da execução retomada.

---

## 1. Verificação por amostragem (o que se sustentou e o que não)

| Alegação | Conferido em | Resultado |
|---|---|---|
| N1: menu × faixa da Manutenção | `maquinas.py:32-36`; MENU2 da PCM em `ui37.py:43` (1 item) | Confirmado. O conflito PCM × SUP também foi confirmado (`merge-tree`: `ui37.py`, `cenario.py`, `etapas_celular_test.py`). |
| N2-PA: etapas falsas | `processo_planos.py:18` (NOMES), `:351` ("whys"), `:366-368` (avanços e nota), `:519` ("Nada a publicar"), `:558` (`steps_state`) | Confirmado. Nenhuma branch toca `processo_planos.py`, `patest.py` ou `verif_pa.py`; a busca valeu para todas as refs desde `ecc8b00`. |
| N2-PA, aceite "tirar PA de GUIADO e ATUAL no `etapas_celular_test`" | `etapas_celular_test.py:122` filtra por `temEtapas` | **Ajustado.** A mudança é desnecessária, porque a PA sai do conjunto `et` sozinha. Mexer nas l.103-106 criaria um 3º conflito com PCM e SUP. Precisa ser confirmado rodando. |
| N3: CMP com 6 etapas | `processo_compras.py:16` e `:576-586` | Confirmado. |
| X-AGR-1: painel da O.S. leva a cópia fixa | `processo_os.py:150` e `:157`; `dados.py:93-94`; `campo.py:289-299` (`imsg` simulados, "Registrar avanço" → MB-03) | Confirmado, com **correção**. As telas CA-01det e CA-01x-os0420 **não estão** na página de ocultos: são detalhes visíveis de Agrícola (`build.py:44`) e pertencem ao item O.S. no menu (`ui37.py` MENU_OF). Faltava listar mais dois links: o índice DEMO-13 → CA-01det (`indice.py:21`) e o AG-06 → CA-01det e CA-01x (`agronomia.py:444-446`). |
| X-A-10: links SU-07 no CA-01det e no CA-01x | `campo.py:264`, `:293` e `:335` | Confirmado, mas **absorvido pelo X-AGR-1**: se essas telas saem do caminho visível, o link deixa de ser alcançado. |
| X-CAD-3, X-APP-3 e X-PROD-5: fazenda não acompanha | `engine.py:1434` (`'Santa Rita'`); `producao.py:135` (`'Todas'`); `agronomia.py:594-597` e `irrigacao.py:111-118` leem `mapa-ctx` | Confirmado. **As três propostas eram incompatíveis** entre si. Também foi visto que o Mapa grava `mapa-ctx` só por abrir (`inicio.py:976`, padrão Lagoa Grande). Por isso foram unificadas em X-CTX com gravação só por escolha (§2). |
| X-CAD-2 e X-APP-11: links ao SAF sem endereço | `cad_fazendas.py:506` e `:583`; `inicio.py:873`, `:916`, `:985` e `:1280`; `processo_os.py:1147`; o SAF lê `#saf&passo&cult` (`safra.js:1274-1280`) | Confirmado. |
| X-CAD-1: rendimento pede de novo o que o CD-03 e o CD-04 têm | `cad_culturas.py:112` (texto livre); `cadastros.py:422-423` (R$/h e pessoas); `cad_ativos_pessoas.py:112`; `:210` (link sem conjunto) | Confirmado. Além disso, a ajuda do CD-03, "O rendimento usa este valor", é **falsa hoje**. |
| X-CAD-4: "Comprar" do Mapa com a safra fixa | sp-sup `inicio.py:899` e `:905` (`#saf=S2627`); sp-ctl4 `inicio.py:669-676` (por fazenda) | Confirmado. O erro aparece ao integrar as duas. |
| X-CAD-5: barra × painel no Mapa | `inicio.py:932` × `:1215`; `:942` × `:985` | Confirmado. |
| X-CAD-8 e X-A-11: trilha "Mapa › Mapa" | `ui37.py:283` (`crumbs=[area,submenu]`) e `:52` (teste do grupo de 1 item) | Confirmado. **São o mesmo item.** |
| X-AGR-4: "Trocar safra" na etapa 1 | `ui37.py:265`: o botão sai sempre que `saf='contexto'` | Confirmado. |
| X-AGR-5: nova ordem com a safra vazia | `processo_os.py:879` | Confirmado. |
| X-AGR-6: link "Decidir em Planejar safra" | `processo_planos.py:346`; `c.id` e `c.safra` já estão em PA0 (`:59`) | Confirmado. A adoção de versão no SAF falta no protótipo: é o PRD 40.3, já registrado como fora do escopo em `docs/analise-solo/ESPECIFICACAO.md:411` da sp-solo. |
| X-PROD-4: o alvo `BEN#lote` não abre | sp-ben `processo_beneficiamento.py:214`: o hash só trata `nova=` e `OB-` | Confirmado. |
| X-PROD-5 e X-PROD-6 | `producao.py:135`; `:557-563` (kv × Resultado) | Confirmado. |
| X-PROD-3: reserva pelo lote sem a regra R-C05 | Só leitura de código, segundo o próprio autor | **Não executado (PLAUSÍVEL).** A frente dona reproduz o CE-08 nas duas portas antes de mudar. |
| X-APP-1: fila em 3 telas | `mobile.py:172-173`, `:331`, `:359` e `:483` | Confirmado. |
| X-APP-2: dois "quem" no app (PCM) | sp-pcm `mobile.py:1306-1311` (`c.app.usuario`) × `cenario.js:160` e `:361` (`c.app.operador`) | Confirmado. |
| X-APP-4: "Entrar como" sem link | `_render/Main.dc.html`: 0 links e 8 "começa em" (executado) | Confirmado, com **correção**. O `div` é proposital ("abra pelo menu abaixo"). O defeito real é que a lista não bate com o seletor: Beto e Dora não estão no seletor, e Paula e Zé não estão na lista. Fica a alternativa barata. |
| X-APP-5: "Restaurar" falso | `indice.py:81` e `:95` × `cenario.js:6-12` (localStorage) | Confirmado. O proprietário pode testar em estado sujo achando que restaurou. |
| X-APP-9: Voltar do app | `mobile.py:351` (`back='IN-01.dc.html'`) | Confirmado. |
| X-APP-10: apontamento falso do caldeiro | `os_campo.py:99` (só aviso) | Confirmado. |
| X-A-7: "Ver como" na MA | sp-pcm `maquinas.py:907` | Confirmado. |
| Commits citados como "já existe" | 19 commits nas 9 branches: `git merge-base --is-ancestor <commit> HEAD` | Todos existem e estão no HEAD da branch. |

**Duplicatas fundidas:**
- X-CAD-8 = X-A-11 → X-TRILHA;
- X-CAD-3 = X-APP-3 = X-PROD-5 → X-CTX;
- X-CAD-2 e a parte SAF do X-APP-11 → X-LNK;
- X-CAD-6, X-CAD-7 e o resto do X-APP-11 → X-REG;
- X-PROD-7, X-APP-6 e o DEMO-13 → X-IDX;
- X-CAD-10 = X-A-4;
- X-CAD-13 = X-APP-14.

**O que faltava na lista de frentes do orquestrador:**
- **A frente `claude/v44-cadux` não está na lista** (worktree `/home/user/sp-cadux`, "Cadastros intuitivos: seleção abre detalhes"). Ela ainda não tem commit, mas vai mexer em `cadastros.py` e `cad_*.py`. Por isso o X-CAD-1 e o `#reg` do X-REG vão para ela.
- **A `claude/v44-controle-05` está sobre `99537ca`, não sobre `cdc185f`** (executado, `merge-base`). O `merge-tree` mostra conflito em `processo_os.py` com outras 8 branches, inclusive as SAF-C01 e SAF-C02, que nem tocam o arquivo. É preciso atualizá-la sobre `cdc185f` antes de integrar.
- **A tarefa pendente "DS: padronizar a ação primária das telas do menu"** vai tocar todas as telas. Ela deve vir depois da NAV-2, ou ser combinada com ela.

---

## 2. Tabela final de decisões

**Aceite comum** (vale para toda linha marcada NAV):
- **Navegação:**
  - nenhum item de menu, faixa ou botão que só troca de tela;
  - `varredura.py` sem link quebrado;
  - `links_ocultos_test.py` sem par novo.
- **Teclado:**
  - Tab, Enter e Esc percorrem lista → detalhe → primária → voltar;
  - o foco volta ao cartão ou à linha de origem.
- **Celular, 390 px:**
  - sem rolagem lateral;
  - título, situação e primária na tela;
  - `etapas_celular_test.py` e `componentes_test.py` verdes.
- **Rascunho e retorno:**
  - formulário alterado avisa antes de descartar;
  - Voltar devolve a posição;
  - o endereço `#` reabre o mesmo registro depois de F5;
  - id inexistente abre a lista, sem erro.
- **Links de contexto:**
  - herdam o registro e continuam corrigíveis no topo ou no filtro;
  - abrir pelo endereço não muda o estado.
- **Comandos protegidos:**
  - nenhuma trava sai: aprovação individual, CMD-06 liberar, trava legal do CTL-1, reserva e estoque, chave de quem inicia, `manPode`;
  - nenhum comando fica em dois lugares com regras diferentes.
- **Produtividade (§3.3):** cliques medidos antes e depois, no mesmo cenário.

### 2.1 Propostas do Codex (N1–N6)

| ID | Decisão | Razão | Dono | Arquivos | Conflito e ordem de integração | P | Aceite próprio |
|---|---|---|---|---|---|---|---|
| N1 | já existe/em execução | A faixa repetia 5 destinos do menu. A PCM já fez a MA única (f9ea51a, eba72ba) | claude/v44-pcm | `ui37.py`, `maquinas.py`, `build.py` | Conflita com a SUP em `ui37.py` (MENU2), `cenario.py` e `etapas_celular_test.py`. A **PCM integra antes**. No MENU2, Manutenção fica com 1 item → `MA.dc.html` e Suprimentos com "Compras" | P1 | Menu Manutenção = 1 link, sem faixa; `MA-03.dc.html` → `MA#vis=semordem`; páginas antigas redirecionam; `ma_unica_test`, `links_ocultos_test`, `acao_unica_test` e `etapas_celular_test` sem falha nova contra a base |
| N2 (PM) | já existe/em execução | D-03 da PCM: lista → detalhe → "Publicar vN" | claude/v44-pcm | `maquinas.py` | junto com N1 | P1 | `PM.dc.html#PM-01` → `MA#plano=PM-01`, sem `.etp-ind`; `ma_planos_test` e `ma_correcoes_pm_test` |
| N2 (PA) | **aplicar agora** | A etapa 1 é a lista, as etapas 2 e 3 aparecem "impedidas" e a 3 sem rascunho só consulta. Mesmo corte que a PCM fez no PM | **NAV-1** | `processo_planos.py`, `patest.py`, `verif_pa.py`, `pa_lista_test.py` (novo) | **Nenhum arquivo de produto compartilhado** | P2 | §3.1 |
| N3 | já existe/em execução (SUP-3, adiado) | 6 etapas, 4 avanços que só navegam, progresso mostrado 3 vezes | claude/v44-suprimentos | `processo_compras.py`, `safra.js`, `ui37.py`, `cmptest.py` | Começa depois do **CTL-4** integrado, que mexe no mesmo arquivo. O rascunho `ddfb47f` está sobre a base antiga `99537ca` | P1 | AC-SUP-01 (`cmp_fila_test`); sem faixa; navegar não aprova; homologado, `sig`, alçada e motivo mantidos |
| N4 | já existe (preservar) | As 4 telas têm decisão própria; só a outorga se repetia | claude/v44-tabelas-r (6e71b3f) + claude/v44-controle-05 (2b52b39) | `irrigacao.py`, `cad_fazendas.py` | TABR × CTL5 conflitam em `irrigacao.py`, `cad_fazendas.py` e `processo_os.py`. **CTL5 precisa ser atualizada sobre `cdc185f`** antes | P3 | Outorga só no IR-04, com o valor do cadastro; IR-02 mostra o pico × outorgada; `irtest`, `irr_fluxo_test` e `ctl5_test` E3 |
| N5 | já existe/em execução | "Atenda requisições" no Estoque; a O.S. leva a `EST#req=`; as listas globais ficam | claude/v44-suprimentos (85a8405, 4e1023b) | `processo_estoque.py`, `est.js`, `processo_os.py` | SUP × CONF conflitam em `processo_estoque.py`, `processo_os.py`, `cenario.js` e `ui37.py` | P2 | OS-0417 "Receber devolução" → `EST#req=REQ-031`; `est_fila_test` e `est_cenario_test` |
| N6 | já existe/em execução | AG-07 só consulta (eeff236, a396c51); BEN como tela irmã de Cargas (7ab0cc5); Comercial com 3 itens (8231296); CONF com 4 itens (ca0016f) | ctl5, ben, com, conf | `ui37.py`, `agronomia.py` | BEN × COM conflitam em `ui37.py`, `producao.py`, `producao.js`, `g2lib.js` e `cenario.py` | P2 | MENU2 final: Produção 3, Comercial 3, Configurações 4; a varredura não acha item repetido |

### 2.2 Achados novos

| ID | Decisão | Razão | Dono | Arquivos | Conflito e ordem | P | Aceite próprio |
|---|---|---|---|---|---|---|---|
| X-AGR-1 | aplicar agora (NAV-2) | O painel vivo da O.S. leva a cópia fixa com comandos simulados ("Concluir execução" e "190/350 ha" fixos) | NAV-2 | `processo_os.py:150` e `:157`; `inicio.py:149`; `build.py:44`; `indice.py:21`; `ostest.py`, `intest.py`, `map_decisoes_test.py`, `links_ocultos_test.py` | `processo_os.py` está em 7 frentes; `build.py` na PCM, BEN e CONF. **Depois da PCM**, que altera a linha 150 | P1 | Painéis da OS-0420 e OS-0421 sem "Abrir ordem completa"; bloqueio da OS-0420 → `MA#om=OM-0233`; Mapa T1 e T4 → `OS#OS-0421` e `#OS-0420`; DEMO-13 → `OS#OS-0421`; CA-01det, CA-01x e CA-02 saem dos detalhes visíveis e ficam ocultas; não se perde a dose por zona nem a conferência diária (ficam em AG-04det e CA-02 até o CONTROLE-02) |
| X-CTX | aplicar agora (NAV-2) | A fazenda escolhida se perde entre telas: O.S. e EST voltam a Santa Rita e a Produção volta a Todas | NAV-2 | `engine.py:1433-1436`, `producao.py:135`, `inicio.py:970-976`, `agronomia.py:594`, `irrigacao.py:111` | `engine.py`: SUP, CONF e DS (CONF × DS já conflitam); `producao.py`: BEN, COM e DOM. **Depois de todas elas** | P2 | Regra única: a chave `mapa-ctx.mf_faz` com `esc:true` só quando a pessoa escolhe uma fazenda real num seletor (nunca "Todas"). Toda tela com seletor lê a chave; sem escolha, valem os padrões de hoje (D-26). `#OS-…`, `#tal=` e `#req=` impõem a fazenda do registro sem gravar. Teste novo: Lagoa Grande na COLH → O.S., EST, CARGA, PROD e VEN abrem em Lagoa Grande; aba nova abre nos padrões; `OS#OS-0420` abre em Santa Rita sem mudar a escolha |
| X-LNK | aplicar agora (NAV-2) | 7 links ao SAF sem endereço fazem a pessoa escolher de novo a safra e o talhão | NAV-2 | `cad_fazendas.py:506` e `:583`; `inicio.py:873`, `:916`, `:985` e `:1280`; `processo_os.py:1147` | `cad_fazendas.py`: TABR, CTL5 e CADUX; `inicio.py`: PCM, SUP, CTL4, CONF e SOLO | P2 | CD-01det#talhao=T2 › "Planejar T2 na safra" → SAF na etapa 2 da 2026/27 com o cultivo; Mapa › Lavoura idem; com duas safras abertas, vai a da parcela; "Trocar safra" continua |
| X-AGR-6 | **aplicar agora** | "Decidir em Planejar safra" cai na etapa 1 | **NAV-1** | `processo_planos.py:346` | nenhum | P3 | §3.1 |
| X-APP-1 | aplicar agora (NAV-2) | A mesma fila de ordens, com os mesmos botões, aparece em MB-01, MB-02 e MB-03 sem turno | NAV-2 | `mobile.py`, `mbtest.py`, `app_saldo_zero_test.py` | `mobile.py`: PCM, SUP, CTL4, CONF e DOM. Depois delas | P2 | Cada ordem da fila só tem ação no MB-01; o MB-02 mostra "aguardando" e a equipe; o MB-03 sem turno mostra o recibo e "Iniciar turno · OS-0421"; os toques para iniciar e fechar um turno ficam iguais ou menores |
| X-APP-5 | aplicar agora (NAV-2) | "Restaurar dados iniciais" diz que recarregar restaura, mas o estado fica no localStorage | NAV-2 | `indice.py:81` e `:95` | `indice.py`: SUP, COM, CONF e DS | P2 | Com confirmação, volta O.S., EST, MIP, Irrigação, PCM, Produção e assinatura ao início; o texto diz que recarregar não restaura |
| X-REG | ajustar nas frentes donas | Os cadastros só leem `#aba` (`cadastros.py:226`); os links de saída não levam o registro | `#reg` nos Cadastros: claude/v44-cadux. Links: PCM (CD-03 "ordens afetadas" → `OS#OS-0420`; MA "Abrir no CD-03"), CONF (CF-01 → CD-04), SUP (CMP → CD-05; CD-06 → EST), CTL5 (AG-07 → EST e → `PA#plano`), NAV-2 (MB-02det → `MB-05#OS`) | `cadastros.py`, `cad_*.py`, `processo_compras.py`, `agronomia.py`, `mobile.py` | `cadastros.py`: TABR, BEN, DS e CADUX | P3 | CMP › "Homologar em Parceiros" abre o CD-05 com o painel do fornecedor; MA › Trator T1 › "Abrir no CD-03" abre o painel; `#reg` inexistente abre a lista |
| X-CAD-4 | ajustar na frente dona | O "Comprar" do Mapa leva sempre a S2627; com a CTL-4, uma falta da Lagoa Grande abriria a compra da Santa Rita | claude/v44-suprimentos (avisar a CTL-4) | `inicio.py` | SUP × CTL4 | P2 | Lagoa Grande › PV13 › Comprar → `CMP#saf=LG2627`; `demanda_unica_test` e `sup_unit_test` |
| X-CAD-1 | ajustar na frente dona | O rendimento pede de novo conjunto e R$/h que já estão no CD-03 e no CD-04 | claude/v44-cadux, depois da TABR | `cad_culturas.py`, `cadastros.py`, `cad_ativos_pessoas.py` | TABR, CADUX, PCM, BEN e CONF (`cad_ativos_pessoas.py`) | P2 | "Cadastrar rendimento ›" do CD-03 abre com conjunto e operação; largura e R$/h só para leitura; mudar o R$/h do Trator 02 muda o R$/ha; O17 (paridade com o SAF) verde |
| X-APP-2 | ajustar na frente dona | "Ver como Zé" grava `usuario`, mas o turno e o recebimento gravam `operador` (Marcos) | claude/v44-pcm (`cenAppAtivo` com a CONF) | `mobile.py`, `cenario.js` | PCM × CONF | P2 | Com Ver como Zé, nada oferece o turno do Marcos; todo registro do app grava quem está no Ver como |
| X-PROD-3 | ajustar na frente dona, reproduzindo antes | A reserva pelo lote não aplica a validade (R-C05) nem o "quem age" | claude/v44-comercial, depois da BEN | `producao.py`, `producao.js` | BEN × COM | P2 | CE-08 igual nas duas portas; mesmo RS e MP |
| X-PROD-4 | ajustar na frente dona | PROD → CO-06, oculta e fixa; o alvo `BEN#lote` previsto no BEN-8 não abre | claude/v44-beneficiamento | `producao.py`, `links_ocultos_test.py`, spec BEN §8 | BEN × COM × DOM | P2 | L39-131 mostra todos os motivos com quem resolve; o par (PROD, CO-06) sai do residual; a spec troca o alvo para `PROD#lote` |
| X-TRILHA | aplicar agora (NAV-2) | A trilha mostra "Mapa › Mapa" e, com a PCM, "Manutenção › Manutenção" | NAV-2 | `ui37.py:283` | `ui37.py`: PCM, SUP, BEN, COM, CONF e SOLO | P3 | Um nível só; o CD-01det continua "Cadastros › Fazendas… › T1" |
| X-AGR-4 | aplicar agora (NAV-2) | Na etapa 1, "Trocar safra" leva para onde a pessoa já está | NAV-2 | `ui37.py:265`, `safra.js` | `ui37.py` (6 frentes); `safra.js`: CTL4, SAF-C02 e SOLO | P3 | Na etapa 1, sem "Trocar safra" nem a fazenda; na 2, os dois aparecem; a CMP não muda |
| X-AGR-5 | aplicar agora (NAV-2) | "Nova ordem" pede a safra que o topo já diz | NAV-2 (combinar com a SOLO) | `processo_os.py:879`, `os_cenario_test.py` | 7 frentes | P3 | Com "Santa Rita · 2026/27", a safra vem preenchida e editável; com "Todas", vazia; a trava cultivo\|atividade continua verde |
| X-CAD-5 | aplicar agora (NAV-2) | Barra e painel do Mapa repetem "Programar vistoria" e "Abrir Pragas" | NAV-2 | `inicio.py` | PCM, SUP, CTL4, CONF e SOLO | P3 | Com um talhão selecionado, um de cada; sem seleção, o modo da barra funciona; `mip_fluxo_test` |
| X-IDX | aplicar agora (NAV-2) | DEMO-03, 13, 17, 18, 19 e 20 levam a cópias fixas | NAV-2 (os alvos vêm da SUP, PCM, COM e BEN) | `indice.py:16-31`, `links_ocultos_test.py` | `indice.py`: SUP, COM, CONF e DS | P3 | Nenhum DEMO abre tela sem cenário quando a tela viva existe; a lista residual do Main encolhe |
| X-APP-4 | aplicar agora, alternativa barata (NAV-2) | A lista de perfis não bate com o seletor | NAV-2, depois da CONF (`g2perfis`) | `indice.py` | idem | P3 | Os nomes do índice são os do seletor; uma linha diz "troque no rodapé do menu" |
| X-APP-9 | aplicar agora (NAV-2) | O Voltar do app abre uma tela web oculta | NAV-2 | `mobile.py:351`, `os_campo.py:127`, `links_ocultos_test.py` | `mobile.py` (5 frentes); `os_campo.py` (DS) | P3 | Nenhum Voltar do app abre tela web; o par MB-01 → IN-01 sai do residual |
| X-APP-10 | aplicar agora (NAV-2) | "Registrar apontamento" do caldeiro diz "aberto", mas não abre nada | NAV-2 | `os_campo.py:99` | DS | P3 | A primária abre o MB-03 no turno da OS-0424 |
| X-PROD-6 | aplicar agora, só junto com o X-CTX (NAV-2) | Produtividade e Custo aparecem 2 vezes no painel do talhão | NAV-2, depois da DOM | `producao.py:557-563` | BEN, COM e DOM | P3 | Uma vez cada, em Resultado; COLH-C01 continua verde |
| X-A-7 | ajustar na frente dona | O "Ver como" no cabeçalho da MA duplica o seletor do menu | claude/v44-pcm | `maquinas.py:907` | — | P3 | `grep -c "Ver como (simulação)" _render/MA.dc.html` = 0; a troca no menu aplica `ma_abertura` |
| X-APP-12 | já existe + ajuste | A aba Almoxarife do MB-05 já saiu; falta o nome do atalho | claude/v44-suprimentos | `mobile.py` | SUP × CTL4 (`mobile.py`) | P3 | Atalho do MB-01 = "Minhas retiradas" |
| X-A-10 | não aplicar | Absorvido pelo X-AGR-1. Se o X-AGR-1 for recusado, volta para a SUP | — | `campo.py` | — | P3 | — |
| X-AGR-3 | não aplicar (pergunta ao Codex) | O SAF tem "Escolha a safra" como etapa 1, o mesmo padrão que o N2 corta. O proprietário citou o SAF como modelo | — | `safra.js`, `processo_safra.py` | — | P3 | Decisão registrada na rodada |
| X-CAD-9 | não aplicar | O mapa da Santa Rita é SVG esquemático; unificar apagaria função | registro para o software real | — | — | P3 | Registrado |
| X-APP-7, X-APP-8 | não aplicar | Telas ocultas (Início, IN-02) | registro; CONF §9 | — | — | P3 | Condição de retorno registrada |
| X-CAD-10/X-A-4, X-CAD-11, X-CAD-12, X-CAD-13/X-APP-14, X-CAD-14, X-AGR-9, X-PROD-1, X-PROD-2, X-A-1, X-A-2, X-A-3, X-A-5, X-A-6, X-A-8, X-A-9, X-APP-13 | já existe/em execução | Cobertos pelos commits citados em cada mapa (conferidos) | PCM, CONF, CTL5, CTL4, SUP, BEN, COM | — | Os mesmos conflitos de N1, N4, N5 e N6 | P1–P3 | Os aceites das próprias frentes |

**Ordem de integração sugerida** (vem do `merge-tree` executado; os worktrees sujos não entram na conta):
1. Atualizar a CTL5 sobre `cdc185f`.
2. TABR, depois CTL5 (resolver `irrigacao.py` e `cad_fazendas.py`).
3. PCM, depois SUP (resolver MENU2, `cenario.py` e `etapas_celular_test.py`).
4. CTL4 (`mobile.py`).
5. CONF (`processo_estoque.py`, `processo_os.py`, `cenario.js` e `ui37.py`).
6. DS (`engine.py` com a CONF).
7. BEN, depois COM (MENU2, `producao.py` e `g2lib.js`).
8. DOM.
9. SOLO.
10. SAF-C01 e SAF-C02.

A **NAV-1 entra a qualquer momento**. CADUX, NAV-2 e SUP-3 vêm depois da rodada.

---

## 3. Escopo da frente NAV

### 3.1 NAV-1: aplicar agora, sem dono e sem colisão de arquivo

**Acordo curto:**
- **ID:** NAV-1.
- **Resultado útil:** a agrônoma edita e publica um plano sem passar por etapas falsas.
- **Persona:** Beto ou Ana, como agrônomos.
- **Requisitos:** PRD 4.2 e 4.3 (master-detail, uma primária); AGENTS §3.3; o mesmo padrão da PCM D-03.
- **Fora do escopo:** adoção de versão no SAF (PRD 40.3).
- **Autor / revisor / integrador:** Claude / Codex / Claude.
- **Base:** worktree `/home/user/sp-nav`, branch `claude/v44-nav`, a partir de `cdc185f`.

**Arquivos sob responsabilidade:**
- `tools/prototipo/v37/gen37/areas/processo_planos.py`;
- `patest.py` e `verif_pa.py`;
- `pa_lista_test.py` (novo);
- `docs/navegacao/ESPECIFICACAO.md` (novo, com este escopo, as decisões de §2 e as pendências).

**Não tocar** em `ui37.py`, `engine.py`, `safra.js`, `agronomia.py` nem `etapas_celular_test.py`:
- o `etapas_celular_test.py` deve continuar verde sem edição, porque a PA sai do conjunto `et` pela linha 122;
- se não continuar, a correção vai ao integrador, depois da PCM e da SUP.

O `acao_unica_test.py` só pode ser mexido nas linhas da PA (156, 341 e 359), que ficam fora dos trechos da PCM e da SUP.

**O que muda em `processo_planos.py`:**

A PA deixa de ter etapas: passa a ser lista → detalhe, como o PM da PCM (D-03).

**O que sai:**
- `NOMES` e `steps=steps_state(NOMES)` (l.18 e l.558): sai o `.etp-ind`;
- `g2steps` com os "whys" de etapa impedida (l.351-352);
- o estado `step` 1/2/3 como etapa: `pid` nulo passa a ser a lista, e `pid` definido, o detalhe;
- o avanço que só navega, "Revisar e publicar ›" / "Ver versões e cultivos ›" (l.366);
- o bloco e a nota "Nada a publicar" (l.519 e l.368);
- as frases "publique na etapa 3" e "edite na etapa 2" (l.230, l.305, l.318 e l.324), trocadas por "publique a versão".

**Lista** (a biblioteca atual), que continua como está:
- cartões por cultura;
- filtros por cultura e por operação;
- "Novo plano" como primária, com a cultura do filtro herdada;
- volta com posição e foco no cartão (`__paPos`).

**Detalhe**, aberto por `PA.dc.html#plano=<id>`:
- O endereço é lido ao carregar e no `hashchange`, e é gravado ao abrir o cartão. Um id inexistente abre a lista, sem erro.
- No topo: nome, estado e versão, e a faixa do rascunho com "Descartar rascunho".
- **Atividades:**
  - a dose é editada na tabela;
  - "Incluir atividade" fica como secundária;
  - o painel da atividade continua igual.
- **Com rascunho:** o bloco "Alterações do rascunho vN em relação à vM" fica logo acima da área de ações, com as diferenças, o custo por ha e o impacto nos cultivos.
- **Blocos sempre visíveis:**
  - "Cultivos que usam este plano" (`g_cv`);
  - "Versões" (pode ficar recolhido).
- **Primária:**
  - "Publicar versão vN", só com rascunho e com o mesmo `paPub`. Ela continua não mudando os cultivos e desabilita com motivo se não houver atividade;
  - sem rascunho, nenhuma primária.
- **Voltar:** "‹ Biblioteca de planos".
- "Novo plano" cria o rascunho v1 e abre o detalhe.
- Sair do detalhe não perde nada, porque salvar já grava o rascunho. O aviso de descarte do painel de atividade e do novo plano continua.
- A altura de tela de trabalho com rolagem interna se mantém, como a MA da PCM.

**X-AGR-6:**
- Em `PREVALS` (l.346), o link passa a ser "Abrir cultivo no Planejar safra ›" → `SAF.dc.html#saf=<c.safra>&passo=cultivos&cult=<c.id>`.
- O chip passa a ser "Na vN · vM publicada".
- O texto de impacto continua dizendo que a adoção é por cultivo no SAF, porque é regra do PRD 40.3.
- A falta dessa adoção no protótipo vai como pendência da frente Planejar safra, já citada em `sp-solo/docs/analise-solo/ESPECIFICACAO.md:411`.

**Aceite (comandos):**

1. `python3 pa_lista_test.py` (novo, Chrome headless). Verifica:
   - sem `.etp-ind` e sem a palavra "impedida";
   - lista → cartão "Soja alta tecnologia" → detalhe, com `#plano=` no endereço;
   - F5 reabre o mesmo plano, e `#plano=XYZ` abre a lista;
   - mudar uma dose na tabela deixa **uma** primária, "Publicar versão v7", com as diferenças visíveis;
   - depois de publicar, um cultivo de safra aberta na versão anterior mostra o link com `#saf=…&passo=cultivos&cult=…`, e o SAF abre na etapa 2 com o painel desse cultivo;
   - Tab/Enter abre o cartão, Esc fecha o painel, e Voltar devolve o foco ao cartão;
   - a 390 px, sem rolagem lateral e com a primária visível;
   - os **cliques para publicar uma mudança de dose ficam 1 a menos** (sai "Revisar e publicar ›"), medidos no mesmo cenário em `cdc185f` e depois.
2. `python3 patest.py`, reescrito de etapas para lista → detalhe. As regras ficam as mesmas: rascunho v(n+1), diferenças, descartar, novo plano copiando de uma base, nome duplicado recusado.
3. Devem continuar verdes:
   - `python3 componentes_test.py` (itens 10 e 14 usam os cartões da PA);
   - `python3 etapas_celular_test.py`;
   - `python3 acao_unica_test.py`;
   - `python3 agrofit_test.py` (ordem do menu Agrícola);
   - `python3 varredura.py`;
   - `python3 links_ocultos_test.py`.

**Estado:** especificado. **Próximo passo:** o Codex revisa este escopo; depois, implementação.

### 3.2 Cortes para as frentes donas (depois que cada uma integrar)

- **PCM (PCM-2):**
  - X-APP-2: um só "quem" no app; `cenAppAtivo` combinado com a CONF;
  - X-A-7: sai o "Ver como" do cabeçalho da MA;
  - X-REG: CD-03 "Ver ordens afetadas" passa a ter um link por ordem (`OS#OS-0420`, `#OS-0431`), e "Abrir no CD-03" da MA usa `#reg=` quando a CADUX criar.
- **SUP (SUP-3 e o fechamento da SUP-2):**
  - N3 e X-A-8, como na spec;
  - X-CAD-4: a safra do "Comprar" segue a fazenda do Mapa;
  - X-APP-12: atalho "Minhas retiradas";
  - X-REG: CMP → `CD-05#reg=` e CD-06 → `EST#sec=saldos` ou `#lote=`.
- **BEN:**
  - X-PROD-4: motivos de carência no painel do lote; sai o link PROD → CO-06; o alvo do Mapa no BEN-8 passa a `PROD#lote`;
  - fornece o alvo vivo do DEMO-19 para o X-IDX.
- **COM:** X-PROD-3, reproduzindo antes o CE-08 nas duas portas.
- **CTL5:**
  - AG-07 "PL-xx ›" → `PA#plano=<id>`, depois da NAV-1;
  - AG-07 "Abrir no Estoque" → `EST#lote=` ou `#sec=saldos`.
- **CONF:** o link do CF-01 para o CD-04 passa o id da pessoa (`#reg=`).
- **CADUX (Cadastros intuitivos), depois da TABR:**
  - X-CAD-1: rendimento com o conjunto do CD-03;
  - auxiliar `#reg=<id>` em `cadAbas`, que abre a aba e o painel do registro;
  - a ajuda falsa do CD-03 é corrigida pelo próprio X-CAD-1.

### 3.3 NAV-2: sem dono, mas com colisão; só sobre a base integrada

Itens:
- X-AGR-1, com X-IDX DEMO-13 e o `build.py`;
- X-CTX, com X-PROD-6;
- X-LNK;
- X-APP-1, X-APP-9 e X-APP-10;
- X-APP-5, X-APP-4 e X-IDX;
- X-TRILHA e X-AGR-4;
- X-AGR-5 (com a SOLO);
- X-CAD-5.

Começa depois de integradas: PCM, SUP (até a SUP-2), CTL4, CTL5, CONF, DS, BEN, COM, DOM e SOLO. Abre com um acordo curto próprio, e em P1 só o X-AGR-1.

---

## 4. Rascunho de resposta ao Codex (não enviado)

> **NAV-20261009-01** (https://github.com/adrptu/Safrion-Software-/pull/47#issuecomment-6080540795) · consolidação de 09/10 · autor Claude · base `cdc185f`
>
> Mapeei os 5 grupos do menu e conferi por amostragem as evidências em `arquivo:linha`, com `merge-tree` entre as 13 branches. Não rodei testes nesta consolidação.
>
> | ID | Decisão | Dono | P |
> |---|---|---|---|
> | N1 Manutenção menu × faixa | já existe | v44-pcm (MA única) | P1 |
> | N2 PM | já existe | v44-pcm (D-03) | P1 |
> | N2 PA | **aplicar agora** | NAV-1 (só `processo_planos.py`, sem colisão) | P2 |
> | N3 Compra com 6 telas | em execução (SUP-3, depois da CTL-4) | v44-suprimentos | P1 |
> | N4 Irrigação | preservar; outorga única já feita | tabelas-r + controle-05 | P3 |
> | N5 Estoque | já existe (Atenda requisições; listas globais ficam) | v44-suprimentos | P2 |
> | N6 Agrofit, Produção, BEN, CONF | manter (já feito nas frentes) | ctl5, ben, com, conf | P2 |
> | X-AGR-1 O.S. → CA-01det/CA-01x fixos | aplicar depois da PCM | NAV-2 | P1 |
> | X-CTX fazenda que não acompanha | aplicar depois da rodada (regra única `mapa-ctx` só por escolha) | NAV-2 | P2 |
> | X-LNK links ao SAF sem `#saf&passo&cult` | aplicar depois da rodada | NAV-2 | P2 |
> | X-APP-1 fila do app em 3 telas · X-APP-5 "Restaurar" falso | aplicar depois da rodada | NAV-2 | P2 |
> | X-CAD-1 rendimento redigita o CD-03 e o CD-04 | ajustar | v44-cadux, depois da TABR | P2 |
> | X-CAD-4 "Comprar" do Mapa com safra fixa · X-APP-2 dois "quem" no app · X-PROD-3/4 | ajustar | SUP · PCM · COM/BEN | P2 |
> | Trilha "Mapa › Mapa", "Trocar safra" na etapa 1, nova O.S. sem safra, Mapa barra × painel, índice | aplicar depois da rodada | NAV-2 | P3 |
> | X-CAD-9, X-APP-7/8, X-A-10 | não aplicar (registro; o X-A-10 é absorvido pelo X-AGR-1) | — | P3 |
>
> **Achados de integração:**
> - A `v44-controle-05` está sobre `99537ca` e conflita em `processo_os.py` com outras 8 branches. Precisa ser atualizada sobre `cdc185f` antes de integrar.
> - PCM × SUP conflitam em MENU2, `cenario.py` e `etapas_celular_test.py`.
> - BEN × COM conflitam em MENU2, `producao.py` e `g2lib.js`.
>
> **Peço sua decisão em três pontos:**
> 1. **X-AGR-3:** o SAF fica com "Escolha a safra" como etapa 1, embora PA, PM e CMP saiam desse padrão?
> 2. **Publicar na PA:** um clique, com as diferenças visíveis acima da primária, ou um painel de confirmação como o PM da PCM?
> 3. **X-CTX:** a fazenda só passa a valer entre telas quando a pessoa escolhe (proposta), ou já ao abrir o Mapa?
>
> **Próximo passo:** a NAV-1 começa em `claude/v44-nav` a partir de `cdc185f` quando você revisar o §3.1 de `CONSOLIDADO.md`.
