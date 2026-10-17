# ENTRADA-ACOES · validação independente do Claude (passo 1)

Claude · 17/10/2026 · pedido EX-46, EX-47 e EX-48 do proprietário (entrada rápida e em lote, ações da linha no ⋯, revisão por módulo).
Só o passo 1, a parte do Claude. Não simula o Codex nem o Gemini. Não registra desenho, ondas nem fatias no checkpoint: as ondas abaixo são sugestão para o Codex decidir.

- **Insumos** (versionados, branch `claude/v44-v73-pedidos-1610`, commit `529adf7`, pasta `docs/integracao/V73/pedidos-1610/`): `entrada-acoes-revisao-pedido.md`, `entrada-acoes-revisao-anexo-achados.md` (187 achados), `entrada-acoes-revisao-robo-varredura.html`, `entrada-acoes-revisao-robo-resumo.py`, `excelencia-pedido-ex01-48.md`, `resolve-1-clique-*.md`. Não copiei nenhum de novo.
- **Fonte vigente:** base `b989864`, `tools/prototipo/v37/gen37` (nesta worktree). Toda citação `arquivo:linha` é relativa a essa pasta, salvo indicação.
- **Composição candidata lida:** `int90` `05947ad` (b989864 + PR #81 EST-ONDA0 + PRs #90/#91 crédito), sem alterar e sem build.
- **Render da varredura:** `site70` (versão 1792184197-5a81), só leitura. Ele já contém o EST-ONDA0 e a CRE F1/F2 (no `EST.dc.html` há `estRecIdentidadeErro` e a devolução abre com quantidade e condição vazias; o `MOD-CRE.dc.html` tem `#vis=ficha`). Logo o render da varredura equivale à int90, não à base.
- **PRD e DECISIONS:** `origin/main` `c827408`.
- **Frentes que se sobrepõem** (não alteradas): RESOLVE-1-CLIQUE (crítica `2957a33`, lida só depois de fechar a minha validação dos achados "Resolver em 1 clique"), SAF-LOTE (`a5c8e45`), TAB-11 seta (`c2a20d8`), MA-VINCULO (`67e4307`), OS-LOTE (PR #88, `3b38b3e`), MAPA-UX.
- **Rótulos:** *executado* = rodei e a saída está em `reproducao/`; *lido* = li a fonte citada; *especificado* = proposta ou estimativa sem execução.

## 0. Resumo

- **Contagem (187):** Confirmado 167 · Refutado 1 · Já resolvido 0 · Em andamento 19. Nos 57 altos: Confirmado 44 · Refutado 1 · Já resolvido 0 · Em andamento 12. Quatro confirmados têm parte já resolvida (SUP-08 no EST, AGRO-14 e GES-06 no Mapa, SUP-10 pelo endereço). Os 19 em andamento são 18 da RESOLVE-1-CLIQUE e 1 da MAPA-UX; todos também confirmei na fonte antes de marcar.
- **Decisões:** Adotar 108 · Adaptar 67 · Rejeitar 12. Os 12 rejeitados são polimento de tela fora do menu que já tem equivalente vivo.
- **O refutado:** AGRO-08. A lista mostra "Realizada", mas o Salvar recusa ("Informe decisão da pendência.") e nada é baixado (**executado**, M1). A causa real é do motor: a lista obrigatória sem valor não tem opção vazia e mostra a 1ª opção como escolhida. Isso atinge 77 listas no render (20 em telas do menu).
- **Causas que se repetem** (uma correção na peça comum resolve vários achados, DEC-1610-12):
  1. o ⋯ da linha só aparece se a grade também exclui (`g2lib.js:614`);
  2. a lista obrigatória sem opção vazia (`engine.py:1975`);
  3. o painel estático escolhe a lista pelo rótulo (`engine.py:695-709`): "Tipo" vira Preventiva/Corretiva, "Produto" vira soja e milho em grão, "E-mail" vira nomes (**executado**, M2 e M3);
  4. "Consulta: você não tem permissão" quando o bloqueio é do estado (`g2lib.js:677`);
  5. datas só com calendário nativo (`g2lib.js:684`, `engine.py:718-722`).
- **Achado de alcance (executado):** 79 das 87 telas fora do menu são alcançáveis por links internos ("portas dos fundos"); 8 não têm caminho. 67 achados citam só telas fora do menu, sem contar app e portal (`reproducao/achados_por_alcance.out`). Polir essas telas contraria o EX-02 e a decisão de 25/09 (módulos ocultos preservados, `ui37.py:33` e `:41`). Fechar as portas e levar a regra à tela viva custa menos e corta duplicidade.
- **O que a varredura deixou de fora** (§2): 33 painéis estáticos cujo "confirmar" mostra um resultado fixo, sem ler o que foi digitado. No CA-01det, "Ajustar e liberar saldo" diz "v3 liberada … por Ana" com dose 9,99 e com "Soja em grão" na lista de produto (**executado**, M2). Faltaram também os perfis sem todos os papéis e a web a 390 px.

## 1. Tabela única dos 187

**Convenções.**
- **Validação:**
  - *Confirmado*: o problema existe na fonte vigente. "Em parte" e "já resolvido em parte" ficam na evidência.
  - *Refutado*: o dano alegado não acontece.
  - *Já resolvido*: a base ou a int90 já corrige.
  - *Em andamento*: outra frente é dona. Confirmei na fonte do mesmo jeito.
- **Onda sugerida:**
  - 0: viola decisão fixa ou executa ato sem fricção; correção pequena, já;
  - 1: componente do DS ou correção do motor (uma peça, todas as telas);
  - 2: altos e fluxos diários;
  - 3: lote e grade editável;
  - 4: médios e baixos restantes;
  - EX-02: consolidação (fechar a porta da tela oculta e levar a regra à tela viva);
  - Prop.: depende de decisão do proprietário.
- **Esforço:** P até meio dia; M 1 a 2 dias; G mais de 2 dias (especificado, por leitura).
- **Risco:** risco de quebrar regra, dado ou decisão fixa ao implantar.

| ID | Prioridade | Tela · tipo | Validação | Evidência na fonte | Decisão Claude | Onda | Esforço | Risco |
|---|---|---|---|---|---|---|---|---|
| AGRO-01 | Alta | PL-04 · Erro ou risco | Confirmado | areas/planejamento.py:440 msgbtn('Liberar prontas', "… OS-0430 ✓ liberada por Ana …", primary=True); :439 "Conferir prontidão" já existe; PL-04 fora do menu, mas alcançável: CA-01det → PL-05 → PL-04 (reproducao/alcance_menu.out) | Adotar em parte: tirar "Liberar prontas"; "Conferir prontidão" vira a primária. Lote só de O.S. só com água. "Pedir liberação" por O.S. fica na OS viva (OS-04), não no PL-04 | 0 | P | Baixo: só remove ação |
| AGRO-02 | Alta | AG-01 · Resolver em 1 clique | Em andamento | RESOLVE-1-CLIQUE (RES-0 e RES-2). Confirmado na fonte: areas/agronomia.py:633 ok=L.find(u=>!mipChecks(…).tr.length)‖L[0]; mip.js:259 falta de estoque vai para al (aviso); agronomia.py:646 a linha vira só "Sem estoque"; :645 ordena só por Cancelado | Adaptar: ordenar Conferido → aviso → trava; pré-selecionar o 1º Conferido; "Estoque 10 de 38 L" e grupo IRAC/FRAC na linha; "Pedir compra" pela função da RES-1. Dose continua vazia ou na faixa da bula, nunca o último valor | 2 | M | Médio: regra do MIP; teste de unidade do mipChecks |
| AGRO-03 | Alta | PL-04 · Resolver em 1 clique | Em andamento | RESOLVE-1-CLIQUE (RES-1; A-34). Confirmado: areas/planejamento.py:397-398 o418 sel 'Falta insumo · Ureia 45%', ab 'Abrir O.S.'; PL-04 oculta | Adaptar: a ação mora na linha do insumo da O.S. viva, não no PL-04. "Propor troca de fonte" com dose recalculada pelo nutriente é regra agronômica nova: serviço único (ENG-011) e validação do RT antes | 2 | G | Alto: muda a instrução técnica; nova aprovação |
| AGRO-04 | Alta | AG-04det · Entrada mais rápida | Confirmado | areas/agronomia.py:334-336 painel 'Criar v4' estático com 5 textos já escritos (produto, '0,3 L/100 kg', KCl, alcance, 'Ana'); AG-04det oculta, alcançável por AG-01 | Adaptar: o painel é estático (não grava). A versão viva nasce no MIP (mip.js): lista dos registrados (mipElig) e dose numérica sem valor inicial com a faixa da bula. No AG-04det, só tirar a dose escrita | 2 | M | Médio |
| AGRO-05 | Alta | AG-04det · Erro ou risco | Confirmado | Dado estático: areas/agronomia.py:275-276 v2 'Em uso nos 30 ha realizados', v3 'TS travado'; :282 'Sem registro p/ nematoide-de-cisto'. O fluxo vivo já trava: mip.js:241-243 cenUsoLegal e a liberação da O.S. | Adaptar: corrigir a narrativa (v2 com "uso sem registro detectado") e chamar cenUsoLegal ao salvar versão quando o AG-04 voltar ao menu. Realizado não muda | 4 | P | Baixo |
| AGRO-06 | Alta | AG-02 · Necessidade essencial | Confirmado | areas/analise_solo.py:105 a lista SO_AN tem só Ca, Mg, K, H+Al, Al e Argila; dados_solo.py:50 LAU-2043 com 15 atributos | Adotar: painel completo do padrão do laboratório; linha vazia não grava; laudo nasce "Aguardando validação" | 2 | M | Médio: calagem e adubação passam a ler pH e P; solo_unit |
| AGRO-07 | Alta | AG-02 · Lote | Confirmado | areas/analise_solo.py:259 <input id="rl_arq" placeholder="laudo.pdf"> (texto); 0 type="file" | Adaptar: importar planilha/CSV do laboratório com prévia (entrou, falhou), reaproveitando o colar do EDL-01 (SAF-LOTE). Leitura de PDF por IA fica desligada (DEC-1610-11). Validação segue uma a uma | 3 | G | Médio |
| AGRO-08 | Alta | PL-02 · Erro ou risco | Refutado | Executado (reproducao/repro_modais_site70.out M1): a lista mostra "Realizada" (selectedIndex 0), mas o rascunho está vazio (g2lib.js:202); "Salvar" recusa com "Informe decisão da pendência." (g2lib.js:217) e "Evidência" nem aparece. Não dá baixa com 1 clique. Causa real: o select do motor não tem opção vazia (engine.py:1975) | Adaptar no motor: lista obrigatória sem valor ganha "Escolha…" vazia (77 listas no render, 20 em telas do menu). "Realizada" ligada a O.S. ou apontamento é melhoria do PL-02 (oculto): levar ao SAF | 1 | P | Baixo |
| AGRO-09 | Alta | SAF · Necessidade essencial | Confirmado | PL-01 g_saf (areas/planejamento.py:154-160), PL-06, PL-03 × SAF (areas/processo_safra.py:36); PL-* fora do menu, alcançáveis: AG-01det → PL-02 → PL-01 → PL-06 | Adaptar: a entidade já é o SAF. Não criar outra tela; fechar as portas dos fundos (links de AG-01det, AG-04det e CA-01det para PL-*) e apontar ao SAF, como MA-01..05 → MA | EX-02 | M | Médio: links e testes de navegação |
| AGRO-10 | Alta | PL-01 · Erro ou risco | Confirmado | PL-01 'Período' texto (areas/planejamento.py:158); SAF 'estado' sel Rascunho/Em planejamento escolhido à mão (areas/processo_safra.py:36); 0 "Copiar" | Adaptar no SAF: tirar o campo Estado (nasce Rascunho, muda por ação, P13); datas sugeridas pela safra anterior + 1 ano; opção "Copiar cultivos e planos da anterior". PL-01 redireciona | 2 | M | Médio |
| AGRO-11 | Alta | MOD-AGR · Necessidade essencial | Confirmado | ui37.py:53 MENU2 Agrícola sem PL-03/04/05 e AG-03/04; PL-03 sem caminho (alcance_menu.out) | Adaptar: Programação e Impedimentos como filtros rápidos da OS ("Período", "Impedidas"), sem item novo (P11). Recomendações no menu: decisão do proprietário | Prop. | M | Baixo |
| AGRO-12 | Alta | IR-02 · Lote | Confirmado | areas/irrigacao.py:336-366 painel de 1 setor; irrigacao_estado.js:374 irrProgramar(s, sid) | Adotar: lote só água (DEC-2609-10), por seleção ou chip "Acima do limite", prévia do que trava (irrChecar, irrigacao_estado.js:263) e resultado por linha. Fertirrigação fora do lote | 3 | M | Médio: bomba e outorga encadeadas |
| AGRO-13 | Alta | PL-02 · Entrada mais rápida | Confirmado | areas/planejamento.py:234-236 dose, gatilho e janela em texto; criar já é estruturado (engine.py:723 trigger_field) | Adaptar: PL-02 é oculta; garantir "editar = criar" onde o plano vive (PA e SAF) e redirecionar PL-02 | EX-02 | M | Médio |
| AGRO-14 | Alta | AG-01 · Lote | Confirmado | areas/agronomia.py:737 t0=tal‖tals[0]; mip.js:177 1 talhão × 1 alvo. Já resolvido em parte: o Mapa tem "Programar vistoria nas áreas" (areas/inicio.py:1097 → criarVis :923) | Adaptar: reaproveitar criarVis no AG-01 (chip "Atrasadas", seleção), recusa de talhão × alvo aberto (mip.js:182) e resultado por linha; talhão inicial = o mais atrasado | 3 | M | Baixo |
| OS-01 | Alta | OS · Necessidade essencial | Em andamento | RESOLVE-1-CLIQUE (RES-0, supCobertura). Confirmado: areas/processo_os.py:142 'Reserva ao liberar' fixo; :343 osInsSit devolve o texto do registro em A liberar; cenario.js:158 cenDisp já calcula | Adotar via RES-0: quadro calculado e prévia; o servidor confere ao liberar | 2 | M | Médio |
| OS-02 | Alta | OS · Resolver em 1 clique | Em andamento | RESOLVE-1-CLIQUE (RES-1). Confirmado: areas/processo_os.py:634 quem resolve: "Suprimentos, recebendo o insumo no Estoque.", link para EST.dc.html | Adotar via RES-1: SC idempotente com origem na O.S.; dono = papel Comprador (PRD 2); defensivo só com receituário | 2 | M | Médio |
| OS-03 | Alta | OS · Resolver em 1 clique | Em andamento | RESOLVE-1-CLIQUE (RES-2). Confirmado: areas/processo_os.py:870-871 pan_ajopts = catálogo inteiro (OSD.nova.prods) ordenado por saldo; uso legal só ao salvar | Adaptar via RES-2: lista do AG-01 (mipElig + mipChecks) na O.S.; dose vazia com faixa; vN+1 vai à aprovação individual. Não é 1 clique (3) | 2 | M | Alto se pular aprovação |
| OS-04 | Alta | IN-02 · Necessidade essencial | Confirmado | Regra explícita: areas/inicio.py:1667 "O.S. não entra aqui" e :1687 assert; areas/processo_os.py:921-922 pan_yes → osRun({pa:null}): o painel fica na mesma O.S. | Adaptar: manter a regra (O.S. fora da caixa geral). A fila do agrônomo fica na OS: filtro "Aguardam aprovação · com produto" e "aprovou, abre a próxima" no pan_yes. Sem lote | 2 | P | Baixo |
| OS-05 | Alta | CA-01 · Lote | Confirmado | areas/campo.py:192-198 sel=True e bulk 'Liberar selecionadas' ("Com produto, quem libera é o agrônomo"); CA-01 oculta, alcançável por GE-03 | Adotar (decisão fixa, EX-32, DEC-1610-03): tirar o lote da CA-01 ou limitá-lo a "só água". Conferir com o OS-LOTE (PR #88), que liga seleção na OS sem antecipar aprovação | 0 | P | Baixo |
| OS-06 | Alta | MB-05 · Necessidade essencial | Confirmado | areas/mobile.py:762-787 aba Almoxarife com 3 blocos fixos; :215 'Retirar no almoxarifado' só avisa; areas/processo_os.py:1483 link 'Retirar' → EST sem a REQ | Adotar: fila "A separar" (EST e app) pela janela, com lote, validade e local (FEFO), sobre cenEntregar; link com a REQ. Liga com a leitura "O.S. aguardando material" da RES-0 | 2 | M | Médio: custódia |
| OS-07 | Alta | MB-03 · Entrada mais rápida | Confirmado | areas/mobile.py:578 ft_ha vazio. Achado a mais: a web abre o apontamento com a área do turno previsto sem toque (areas/processo_os.py:816 ha=prox.ha) | Adaptar: botão explícito "Executado como planejado" no app e na web (o mesmo); a web deixa de pré-preencher sozinha; horas pelo relógio do turno menos pausas | 2 | M | Médio: medição; teste de regressão |
| OS-08 | Alta | CA-02 · Lote | Confirmado | areas/campo.py:432 'Conferir 2 apontamentos' confere os 2; :436 status '1 divergência'; :389 dia 2 da OS-0420 com horas acima | Adotar: conferência por exceção; a primária leva só os dentro da tolerância; divergência com Devolver ou Registrar com motivo. Aceite automático na tolerância é do proprietário (EX-10) | 2 | M | Médio |
| OS-09 | Alta | IN-01 · Resolver em 1 clique | Confirmado | areas/inicio.py:1713 OS-0418 com ação ('Liberar','OS.dc.html#OS-0418') e 'Falta insumo'; IN-01 oculta (só via MB-01) | Adaptar: a próxima ação segue o impedimento que o osProx já calcula (areas/processo_os.py:631-634). Depende da RES-1 (pedir compra) | 2 | P | Baixo |
| OS-10 | Alta | IN-01 / IN-02 · Resolver em 1 clique | Confirmado | areas/inicio.py:1724 clique abre 'Tarefa' (reatribuir, prazo); :1681 IN-02 em consulta "Abrir a decisão no módulo de origem" | Adaptar: decidir no lugar só onde a decisão é curta e já tem componente (receber devolução, conferir dia); aprovação de O.S. continua na OS. Lugar de IN-01/02 no menu: proprietário | 4 | G | Médio |
| OS-11 | Alta | OS · Clareza | Confirmado | areas/processo_os.py:1630-1635 ess só em id, ativ, tal, prazo, fase, prog; sit, dono e acao fora do padrão | Adotar: coluna "Situação · próximo passo" em texto no padrão; Progresso sai do padrão | 2 | P | Baixo |
| OS-12 | Alta | OS · Erro ou risco | Em andamento | RESOLVE-1-CLIQUE (RES-0; A-10, A-12, S2). Confirmado: cenario.js:157 cenLote = maior disponível, sem fazenda nem validade; :321-322 um lote, tudo ou nada | Adotar via RES-0: lote da fazenda da O.S., vários lotes, FEFO; outra fazenda → "Pedir transferência". Testes de propriedade da reserva | 2 | G | Alto: reserva e estoque |
| OS-13 | Alta | CA-01x-os0420 · Resolver em 1 clique | Confirmado | areas/campo.py:363 primária 'Acompanhar OM-0233'; areas/processo_os.py:777 rcPode só A liberar e Liberadas | Adaptar: primária do PCP "Alocar Trator 02 a partir de 24/09 06:00", com conflito de máquina e operador conferido. Trocar recurso Em execução pede regra no domínio, não só na tela | 2 | M | Médio |
| SUP-01 | Alta | CMP · Necessidade essencial | Em andamento | RESOLVE-1-CLIQUE (RES-3). Confirmado: areas/processo_compras.py:831 tipos Material e Serviço; :842 "Sem safra nem cultura"; a avulsa aceita insumo como material (crítica R8) | Adotar via RES-3: "Insumo fora do plano" com motivo, vínculo, impacto e alçada; entra na demanda marcada | 2 | G | Médio |
| SUP-02 | Alta | SU-01 · Resolver em 1 clique | Em andamento | RESOLVE-1-CLIQUE (RES-1). Confirmado: areas/suprimentos.py:248 ação 'Em cotação' → CMP sem safra; SU-01 oculta | Adaptar: "Comprar urgente" na demanda viva (CMP etapa 2, SAF) e na linha da O.S.; nada no SU-01. Alçada da urgência: proprietário | 2 | M | Médio |
| SUP-03 | Alta | EST · Resolver em 1 clique | Em andamento | RESOLVE-1-CLIQUE (RES-1; A-17). Confirmado: areas/processo_estoque.py:503 'Sem lote no estoque', :506 'lote cobre só …' sem ação; ben.js:188 'a compra é do BEN-2' | Adotar via RES-1: "Pedir ao Compras" na linha com falta ou "Coberta pelo PC-xxx · chega dd/mm" | 2 | M | Médio |
| SUP-04 | Alta | MA · Resolver em 1 clique | Em andamento | RESOLVE-1-CLIQUE (RES-4, depois da MA-VINCULO). Confirmado: areas/maquinas.py:1154 corretiva sem peças; 'Incluir peça' só no editor de plano (:1044) | Adotar via RES-4: "Incluir peça" na OM com saldo, reserva e "Pedir ao Compras" | 2 | M | Médio |
| SUP-05 | Alta | EST · Entrada mais rápida | Confirmado | areas/processo_estoque.py:87-97 11 campos; 'Apta' digitada embora a validação exija apta + quarentena = conferida; sem XML nem chave. Int90 já protege a identidade da nota (estRecIdentidadeErro) | Adaptar: "Apta" calculada; chip explícito "Igual à nota (N kg)", nunca automático; XML da NF-e como arquivo local no protótipo; consulta à SEFAZ é integração real (proprietário) | 2 | M | Médio |
| SUP-06 | Alta | MOD-SUP · Clareza | Confirmado | ui37.py:55 Suprimentos = Painel, Compras, Estoque, Inteligência; SU-01..09 fora do menu e alcançáveis (alcance_menu.out) | Adotar como consolidação (EX-02): fechar as portas, migrar o que só existe nas SU (contagem cega, políticas). Políticas em Configurações: decisão de menu do proprietário | EX-02 | G | Médio |
| SUP-07 | Alta | SU-01, SU-03, SU-05, SU-06, SU-07, SU-08, SU-09, EST, CMP, MA · Ações no ⋯ | Confirmado | g2lib.js:614 if(sp.rmenu&&sp.del&&(!semDel‖acts.length)); engine.py:1758 menu_linha; só areas/processo_safra.py:97 liga | Adotar (componente da onda 1): ⋯ com rmenu, sem depender de del; ligado por padrão; ação perigosa abre o painel com motivo | 1 | M | Médio: muitas telas; testes de DS |
| SUP-08 | Alta | SU-07det, EST · Erro ou risco | Confirmado | SU-07det: areas/suprimentos.py:959-960 def '10' e condição padrão de quarentena (oculta, alcançável CA-01det → CA-04 → SU-07det). EST já resolvido na int90 e no render da varredura: devolução com quantidade e condição vazias (PR #81, 7762fd3); a base ainda tem qtd = custódia (areas/processo_estoque.py:517) | Adotar só no SU-07det: tirar o padrão já ou fechar a porta para o EST | 0 | P | Baixo |
| SUP-09 | Alta | SU-09, EST · Lote | Confirmado | areas/suprimentos.py:1130 Escopo de 1 lote; areas/processo_estoque.py:130 g_cnt 1 lote por formulário; sem seleção | Adaptar no EST: grade de contagem EDL-01 (P1 na ENTRADA-RAPIDA do SAF-LOTE) e "Planejar contagem" por seleção; ajuste em lote só sem diferença ou abaixo da alçada; quem contou não aprova (AL-09) | 3 | M | Médio |
| SUP-10 | Alta | CMP · Necessidade essencial | Confirmado | Já resolvido em parte: areas/processo_compras.py:620-627 o endereço #saf= abre na etapa 2. Sem endereço abre na etapa 1 com a safra no topo (:631) | Adotar: sem endereço, abrir na safra do contexto e na etapa da solicitação; links internos levam #saf= | 2 | P | Baixo |
| SUP-11 | Alta | CMP · Necessidade essencial | Confirmado | areas/processo_compras.py:695 c5_msg só valor e pedidos; :730 'Registrar aprovação da '+m.quem (simulado) | Adaptar: bloco de decisão com orçado, comprometido, saldo e R$/ha de um serviço só (orçamento GE-02); fila do aprovador depende do lugar da IN-02 no menu | 2 | M | Médio |
| POS-01 | Alta | BEN · Resolver em 1 clique | Em andamento | RESOLVE-1-CLIQUE (RES-5; A-32). Confirmado: ben.js:190-200 'a compra de caixas entra no BEN-2', 'Sem caixa, Cancelar a ordem', link EST sem a nota | Adaptar via RES-5: "Pedir N caixas" pela mesma função de compra; o EST precisa aceitar âncora de recebimento (hoje só #dev) | 2 | M | Médio |
| POS-02 | Alta | BEN · Necessidade essencial | Em andamento | RESOLVE-1-CLIQUE (RES-5, BOM mínimo). Confirmado: ben.js:253-262 benImpedimentos só confere caixas; dados_ben.py:30-44 só PACK-FRU tem material | Adaptar via RES-5: BOM mínimo por rota; consumo de secagem e café só com dado real (proprietário) | 3 | G | Médio |
| POS-03 | Alta | CARGA · Entrada mais rápida | Confirmado | areas/producao.py:448-450 Ticket, Peso bruto e Tara digitados (txt, u kg); "balança integrada" só em texto no LO-02det | Adaptar: "Ler balança" simulado no protótipo (ticket, peso, hora), digitação como exceção marcada; balança real é integração (proprietário). Nunca peso anterior | 2 | M | Médio |
| POS-04 | Alta | PROD · Lote | Confirmado | ben.js:636 benResultado por lote; areas/producao.py:368-373 formulário por lote | Adotar: grade da inspeção, "Marcar todos conforme" por toque, "Liberar os conformes" com recibo por lote; não conforme individual | 3 | M | Médio |
| POS-05 | Alta | COLH, CARGA, BEN, PROD, EXPED, VEN, PCOM · Ações no ⋯ | Confirmado | 0 partes 'act' em producao.js, comercial.js, ben.js, areas/producao.py, areas/vendas.py, areas/processo_beneficiamento.py (grep); ações só nos painéis | Adotar com o componente da onda 1: ⋯ com o próximo passo do painel; item que pede dado abre o painel no formulário | 1 | M | Baixo |
| POS-06 | Alta | EXPED · Necessidade essencial | Confirmado | comercial.js:114 comImpede sem NF nem lacre; 0 'lacre' em comercial.js, producao.js e areas/vendas.py | Adaptar: NF autorizada e lacre com foto (conferente ≠ quem aplicou) na verificação da saída do EXPED; emissão de NF real é integração (proprietário) | 2 | M | Médio |
| POS-07 | Alta | VE-04, VE-06, VE-05, LO-01, LO-03 (via GE-05, GE-08, GE-04) · Erro ou risco | Confirmado | Portas dos fundos: GE-08 → VE-05 → VE-*; GE-03 → LO-04 → LO-*, VE-06 (alcance_menu.out) | Adotar (EX-02): links do Financeiro para VEN#PV, EXPED#RM e PROD#lote; nenhuma entrada nas telas legadas | EX-02 | P | Baixo |
| POS-08 | Alta | PT-05det, PT-03, PT-04det, CO-02, CO-06 · Erro ou risco | Confirmado | Causa única no motor: engine.py:695-709 _opts_for e is_select escolhem a lista pelo rótulo (OPTIONS 'tipo' = Preventiva…, 'motivo' = Sonda deslocada…); 41 listas assim no render, 11 em telas do menu (inventario_site70.out) | Adaptar no motor: painel estático declara a lista; sem lista declarada não vira select. Corrige POS-08, GES-25, GES-27 e CA-01det (repro M2) | 1 | P | Baixo |
| GES-01 | Alta | GE-01 · Necessidade essencial | Confirmado | Nenhum link para GE-01 (alcance_menu.out: SEM_CAMINHO); ui37.py:53-58 sem Gestão | Adaptar: lugar no menu é do proprietário (a barra lateral tem 9 itens e o achado pede não criar o 10º). Opção a levar: cartões em Agrícola › Resultados, que já tem Custos e Orçamento. Não no Crédito, que a CRE F2 acabou de reorganizar | Prop. | P | Baixo |
| GES-02 | Alta | GE-07 · Resolver em 1 clique | Confirmado | areas/gestao.py:533 ORIGENS; :560 dono def 'Ana'; links 'GE-07.dc.html' sem origem | Adotar: "Criar ação" abre com a origem do desvio pelo endereço; caso aberto da mesma origem → "Abrir AC-103" | 2 | P | Baixo |
| GES-03 | Alta | GE-04 · Ações no ⋯ | Confirmado | areas/gestao.py:345-352 cta e jact nas linhas de g_tit; :548-552 'Verificar resultado'; :610 'Autorizar bloco' (GE-08, menu) | Adotar com o componente da onda 1 | 1 | P | Baixo |
| GES-04 | Alta | GE-03 · Resolver em 1 clique | Confirmado | areas/gestao.py:308 v.fechar responde 'Bloqueado'; :284 frete 'Sem versão de rateio' | Adotar: primária segue a próxima pendência (padrão do osProx); critério de rateio sugerido só como destaque, escolha do controller | 2 | P | Baixo |
| GES-05 | Alta | CD-08 · Entrada mais rápida | Confirmado | areas/cad_culturas.py:236 txt('conj','Conjunto ou equipe'); largura e R$/h digitados | Adotar (EX-29): busca nos conjuntos da CD-03 com "Criar conjunto"; valores herdados com origem; rendimento numa fonte só | 2 | M | Médio: custo/ha do planejamento |
| GES-06 | Alta | CD-01 · Entrada mais rápida | Confirmado | Já resolvido em parte: areas/cad_fazendas.py:497 'Importar arquivo' por talhão e :557 'Importar KML ou GeoJSON ›' → IN-04 (mapa real só na Lagoa Grande); sem importar nem colar lista na CD-01 | Adotar reaproveitando a prévia do ON-01det (g_imp) e o colar do EDL-01 (CD-01 é P1 na ENTRADA-RAPIDA) | 3 | M | Médio: assinTrava e sobreposição |
| GES-07 | Alta | GE-04 · Modal e botões | Confirmado | areas/gestao.py:370-372 v.remessa envia e só depois avisa | Adotar (EX-33): resumo antes de enviar (títulos, total, conta, os de fora com motivo); idempotência mantida (:370) | 0 | P | Baixo |
| GES-08 | Alta | CD-04 · Erro ou risco | Confirmado | areas/cad_ativos_pessoas.py:29 a habilidade "Liberar O.S. (agrônomo)"; :376 'hab' multi | Adotar: CD-04 só execução e habilitação legal; decidir só na CF-01; CD-04 mostra "Decide: AL-xx ›" em leitura | 2 | M | Médio: CF-01 lê o CREA do CD-04 |
| GES-09 | Alta | ON-01det · Erro ou risco | Confirmado | areas/onboarding_backoffice.py:171 'map' txt; :174 unidade única para a coluna | Adotar: unidade do cadastro de cada item; perguntar só nas linhas sem item | 2 | M | Médio |
| GES-10 | Alta | GE-02 · Entrada mais rápida | Confirmado | areas/gestao.py:184-186 'Criar cenário' com nome e premissa em texto | Adaptar: "Criar a partir da V2" com premissas em chips e número; volume, receita e custo calculados por um serviço só | 2 | M | Baixo |
| GES-11 | Alta | GE-04 · Resolver em 1 clique | Confirmado | areas/gestao.py:345 e :377 'Abrir aprovação' → IN-02 sem item; a IN-02 nem tem o título (areas/inicio.py:1668-1673) | Adotar: o título entra na caixa do aprovador e o link abre o item; "Lembrar aprovador" no ⋯ | 2 | P | Baixo |
| AGRO-15 | Média | PAGR · Resolver em 1 clique | Confirmado | areas/painel_agricola.py:165 o texto da ação é "Conferir vistoria" + id; areas/agronomia.py:588 agHash aceita :decidir e :programar | Adotar: verbo do próximo passo com a âncora | 4 | P | Baixo |
| AGRO-16 | Média | PL-01 · Resolver em 1 clique | Confirmado | areas/planejamento.py:138 e :199 'Autorizar execução' responde 'Não autorizado'; PL-01 oculta | Adaptar: regra geral "primária que só recusa vira o próximo passo" na tela viva (SAF); PL-01 redireciona | EX-02 | P | Baixo |
| AGRO-17 | Média | PL-05 · Resolver em 1 clique | Confirmado | areas/planejamento.py:468-472 alternativa em texto, ação 'Ver pedido'; PL-05 oculta | Adaptar: "Aplicar alternativa" como proposta de reserva onde o impedimento vive (OS, SAF), não no PL-05 | 4 | M | Médio: reserva |
| AGRO-18 | Média | AG-07 · Resolver em 1 clique | Confirmado | areas/agronomia.py:1127 'Usar na O.S.' pede cultura, alvo, produto e ordem; :1147 rotação só com nomes | Adotar: AG-07 aberto da O.S. ou da decisão já filtrado; estoque e carência na rotação | 4 | M | Baixo |
| AGRO-19 | Média | PL-02 · Erro ou risco | Confirmado | areas/planejamento.py:245-247 'Nova operação do plano' sem alvo; dose '2,0 L/ha' texto | Adaptar: no PA e no SAF, defensivo pede alvo e mostra registro e faixa; PL-02 redireciona | EX-02 | M | Médio |
| AGRO-20 | Média | AG-01 · Ações no ⋯ | Confirmado | areas/agronomia.py:798 g_vis edit 'pick', sem rmenu; Situação e Data sem ess | Adotar com o componente ⋯; Situação e Data visíveis. Sem decisão em lote | 1 | P | Baixo |
| AGRO-21 | Média | AG-03 · Ações no ⋯ | Confirmado | AG-03 e AG-04: links e cta na mesma coluna (inventario_site70.out); ambas ocultas | Adaptar: ⋯ junto com a decisão de menu do AG-03/04 (AGRO-11) | 4 | P | Baixo |
| AGRO-22 | Média | PL-04 · Ações no ⋯ | Confirmado | areas/planejamento.py:389-405 coluna 'Abrir' com links; g_mi4 (:445) repete o painel do PL-03 (_painel_manut, :112) | Rejeitar o polimento no PL-04 e PL-05 (ocultas): consolidar na OS (AGRO-11); tirar a tabela repetida | EX-02 | P | Baixo |
| AGRO-23 | Média | IR-01 · Ações no ⋯ | Confirmado | irrigacao_estado.js:621 'Iniciar irrigação' como texto de próximo passo; linha do IR-02 não abre | Adotar com o componente ⋯ e linha que abre o IR-03det | 1 | P | Baixo |
| AGRO-24 | Média | IR-01 · Modal e botões | Confirmado | areas/irrigacao.py:191 limites editáveis (lmax, imin) com 'Salvar' como primária | Adotar: primária = próximo passo; limites só leitura, edição no ⋯ da ficha do pivô com alçada | 4 | P | Baixo |
| AGRO-25 | Média | IR-01 · Resolver em 1 clique | Confirmado | areas/irrigacao.py:196 'sem medição de água no solo neste talhão' sem ação | Adotar: link para o AG-02 com fazenda e talhão do setor | 4 | P | Baixo |
| AGRO-26 | Média | AG-01 · Modal e botões | Confirmado | areas/agronomia.py:638 dc_kinds escolhido com fundo #1E7A4C e texto branco (o verde da primária) | Adotar: escolha com contorno e ✓ (um verde por contexto, BOT-01) | 1 | P | Baixo |
| AGRO-27 | Média | PL-04 · Entrada mais rápida | Confirmado | areas/planejamento.py:385-389 CONJ com 8 opções misturadas; 'Duração' texto; PL-04 oculta | Adaptar: programar na OS viva, janela por data e duração calculada pelo rendimento (CD-08); PL-04 redireciona | EX-02 | M | Médio |
| AGRO-28 | Média | AG-03 · Necessidade essencial | Confirmado | Em parte: AG-03/04/05/06 e PL-05 sem primária (areas/agronomia.py:195, 268, 379, 425; areas/planejamento.py:512); IR-01/03/04 têm primária condicional (areas/irrigacao.py:270-272 prim_has) | Adaptar: primária da pendência mais urgente nas telas do menu (IR) quando houver pendência; AG-03..06 e PL-05 com a decisão de menu | 4 | P | Baixo |
| AGRO-29 | Média | AG-05 · Modal e botões | Confirmado | areas/agronomia.py:376 'Publicar' → 'Nada a publicar'; :399 'Registrar parecer' grava texto pronto; areas/planejamento.py:186 'Encerrar período' | Adotar: botão só com efeito possível (ou desligado com causa); "Registrar parecer" abre formulário e grava com o nome do RT (EX-33) | 0 | P | Baixo |
| AGRO-30 | Média | AG-03 · Entrada mais rápida | Confirmado | areas/agronomia.py:157 'Evidências' em texto ('Ex.: VIS-017 · LAU-2063'); talhão padrão 'T2 · Soja' | Adaptar: evidências por seleção quando o AG-03 voltar; hoje o diagnóstico nasce do MIP (mip.js) | 4 | M | Baixo |
| AGRO-31 | Média | AG-05 · Entrada mais rápida | Confirmado | areas/agronomia.py:363 4 textos livres; aprovador '—' | Adaptar: a biblioteca viva é o PA, que já versiona; AG-05 redireciona | EX-02 | M | Baixo |
| AGRO-32 | Média | IR-04 · Resolver em 1 clique | Confirmado | dados_irrigacao.py:58 sonda sem dado; linha do IR-04 sem ação | Adotar: ⋯ "Pedir manutenção da sonda" e "Registrar leitura manual" | 4 | P | Baixo |
| OS-14 | Média | OS · Ações no ⋯ | Confirmado | areas/processo_os.py:1637 g_os edit 'pick', sem sel nem rmenu. A seleção está em andamento no OS-LOTE (PR #88, mesmo arquivo) | Adotar o ⋯ com o componente da onda 1, depois do PR #88; "Revisar e aprovar" abre o painel, nunca aprova da lista | 1 | M | Médio |
| OS-15 | Média | OS · Modal e botões | Confirmado | areas/processo_os.py:826-833 pan_hasAj e pares na região do próximo passo | Adotar: uma primária pelo estado; Ajustar, Trocar recurso, Dispensar e Cancelar no ⋯ do cabeçalho (engine.mais e recolhe_acoes já existem) | 1 | P | Baixo |
| OS-16 | Média | OS · Entrada mais rápida | Confirmado | conferencia_diaria_ui.js:37 'Não há meta diária registrada' | Adaptar: comparar com o turno previsto e o rendimento; a faixa de tolerância é do proprietário (EX-10) | 3 | M | Médio |
| OS-17 | Média | CA-01 / CA-01det · Clareza | Confirmado | areas/campo.py:192 CA-01 abre o formulário 'Ordem'; areas/processo_os.py:1471 'Abrir ordem completa' só em 2 O.S. | Adotar (EX-02): a OS é a listagem única; CA-01 sai do caminho (GE-03 e GE-06 apontam para ela) | EX-02 | M | Médio |
| OS-18 | Média | CA-01 · Ações no ⋯ | Confirmado | areas/campo.py:395 links soltos na coluna 'Condição · próxima ação'; CA-01 oculta | Rejeitar na CA-01, que sai com o OS-17; o padrão vale na OS (OS-14) | EX-02 | P | Baixo |
| OS-19 | Média | CA-02 · Ações no ⋯ | Confirmado | areas/campo.py:423 'Devolver para esclarecimento' no cabeçalho, fixo na OS-0420; :429 'Roteiro da OS-0418' na fila | Adotar: ações por linha no ⋯; o roteiro sai da fila (CA-02 é do menu via OS) | 1 | P | Baixo |
| OS-20 | Média | CA-04 · Entrada mais rápida | Confirmado | areas/campo.py:567 'Solicitar material da ordem' com lista fixa (inclui 'Soja · CEPEA'); CA-04 oculta | Adaptar: a requisição nasce da versão (dose × saldo) na OS viva; item de cotação sai da lista | 4 | M | Médio |
| OS-21 | Média | CA-04 · Ações no ⋯ | Confirmado | areas/campo.py:535-537 'Apontar uso ›' leva à CA-02; 'Confirmar recebimento' que só recusa; CA-04 oculta | Adaptar: estado em texto e ⋯ só com ação possível (componente); CA-04 sai com o OS-17 | EX-02 | P | Baixo |
| OS-22 | Média | CA-01det · Resolver em 1 clique | Confirmado | areas/campo.py:267 'faltam {pend} L' sem ação na linha (g_mat, :271) | Adotar: "Pedir entrega do restante" na fila do almoxarife (OS-06), só da reserva da própria REQ | 2 | P | Baixo |
| OS-23 | Média | MB-03 / CA-01det / MB-08 · Entrada mais rápida | Confirmado | cenario.js:503 cenPausar sem motivo; areas/mobile.py:983 'Pausar a volta com motivo' sem pedir motivo | Adotar: chips de motivo em 1 toque; máquina e falta de insumo abrem ocorrência endereçada | 2 | P | Baixo |
| OS-24 | Média | MB-04 / CA-03 · Resolver em 1 clique | Em andamento | RESOLVE-1-CLIQUE (RES-3; A-19). Confirmado: areas/mobile.py:688 TIPOS do app × areas/campo.py:457 TIPOS da web; sem "Falta de insumo" | Adotar via RES-3: lista única, com "Falta de insumo ou embalagem" | 2 | P | Baixo |
| OS-25 | Média | CA-03 · Entrada mais rápida | Confirmado | areas/campo.py:472 Local em texto ('Ex.: T1 · OS-0421'); clique na linha reabre a edição do fato | Adotar: Local por busca; Instante = agora com atalhos; relato registrado só recebe complemento com trilha (integridade do fato) | 2 | M | Médio |
| OS-26 | Média | MB-01 / MB-02 / MB-03 · Ações no ⋯ | Confirmado | areas/mobile.py:431-439 cartões com 'Reconhecer', 'Iniciar · bloqueado' e outros botões | Adotar: cartão abre a ordem; ⋯ de 48 px no app; uma primária na barra; bloqueio vira estado em texto | 1 | M | Médio: modo campo |
| OS-27 | Média | MB-05det · Erro ou risco | Confirmado | areas/mobile.py:831 'Registrar divergência' fixo 'Recebidas 8 de 10 sc'; MB-05det sem caminho (alcance_menu.out) | Adotar: ligar o bloco ao MB-05det; contar a quantidade (numérico, sem valor inicial) | 2 | P | Baixo |
| OS-28 | Média | MB-05 · Resolver em 1 clique | Confirmado | areas/mobile.py:774-777 conflito só com 'Registrar divergência' (crítica RESOLVE A-18, sem fatia) | Adotar: "Avisar o planejamento" e "Pedir compra do complemento" sem duplicar a demanda da safra | 2 | P | Baixo |
| OS-29 | Média | OS / CA-02 · Resolver em 1 clique | Confirmado | areas/processo_os.py:363-373 osEncBloq → 'Receber devolução no Estoque' | Adotar: "Cobrar devolução de Paula · 10 sc" cria o item para ela e para o almoxarife | 2 | P | Baixo |
| OS-30 | Média | IN-01 / IN-03 · Necessidade essencial | Confirmado | areas/inicio.py:1726 g_dia com 6 donos; :1764 g_ag repete 5 itens | Adotar: Meu dia filtrado pelo perfil; Agenda = visão Calendário da mesma fila. Lugar no menu: proprietário | 4 | M | Baixo |
| OS-31 | Média | OS · Entrada mais rápida | Confirmado | areas/processo_os.py:1205 nv_open com safra, cultivo, atividade e janela vazios | Adotar: herdar safra e cultivo do filtro; data com atalhos; vários cultivos = uma O.S. por talhão, cada uma com aprovação individual | 2 | M | Médio |
| OS-32 | Média | IN-02 · Lote | Confirmado | areas/inicio.py:1669 ajuste de inventário com ind=True; :1690-1695 o lote aprova | Adotar (EX-32): lote só de baixo risco e mesma alçada; ajuste com perda um a um (AL-09) | 0 | P | Baixo |
| SUP-12 | Média | CMP · Resolver em 1 clique | Confirmado | dados_compras_mat.py:164 urgência só muda a data; sempre cota | Adaptar: "Comprar já" só com fornecedor homologado e alçada; dispensa de cotação é política do proprietário (crítica RESOLVE §9) | Prop. | M | Médio |
| SUP-13 | Média | MA · Resolver em 1 clique | Em andamento | RESOLVE-1-CLIQUE (RES-4, rascunho da preventiva). Confirmado: areas/maquinas.py:594 'Gerar ordem preventiva' mesmo com peça em falta | Adotar via RES-4, depois da MA-VINCULO: "Gerar ordem e pedir peça", idempotente | 2 | P | Baixo |
| SUP-14 | Média | MA · Lote | Confirmado | areas/maquinas.py:304 filtro 'Espera por peça' sem ação | Adotar depois da MA-VINCULO e da RES-4: "Pedir peças em falta (N)" com resultado por ordem, sem duplicar SC | 3 | M | Baixo |
| SUP-15 | Média | MA · Erro ou risco | Em andamento | RESOLVE-1-CLIQUE (RES-4; NOVO-1 executado). Confirmado: dados_manutencao.py:648 qtd = nec − livre sem reservar o livre; :640 reserva só em manLiberar | Adaptar via RES-4: reservar o livre que entrou na conta no mesmo comando; idempotência por (OM, item, SC aberta) | 2 | P | Médio |
| SUP-16 | Média | MA · Modal e botões | Em andamento | RESOLVE-1-CLIQUE (RES-4; A-31). Confirmado: areas/maquinas.py:430-431 '(simulado · Compras recebe no 1c)' e '(simulado · papel do Almoxarifado)' | Adotar via RES-4: rótulo sem jargão, próximo passo por pessoa; recebimento na fila do almoxarife | 2 | P | Baixo |
| SUP-17 | Média | MA, EST · Necessidade essencial | Em andamento | RESOLVE-1-CLIQUE (RES-4, "Requisitar"). Confirmado: EST › Entregas lê só c.reqs de O.S.; a OM reserva sem requisição (dados_manutencao.py:640) | Adaptar via RES-4: OM liberada gera requisição de peças na fila do EST, sem baixa em dobro | 2 | G | Médio |
| SUP-18 | Média | CMP, MA · Entrada mais rápida | Em andamento | RESOLVE-1-CLIQUE (supReceber). Confirmado: areas/processo_compras.py:129-131 recebimento por item no painel da requisição; areas/maquinas.py:431 ponte | Adaptar: um lugar de recebimento (EST) para insumo, peça e material; Compras e Manutenção mostram o estado | 4 | G | Médio |
| SUP-19 | Média | CD-06 · Entrada mais rápida | Confirmado | areas/cad_produtos_estrutura.py:83 g_itm; 0 GTIN ou código de barras | Adotar: 5 campos e "Mais opções" (CAD-02); seção Códigos; registro do Agrofit junto (EX-28) | 4 | M | Baixo |
| SUP-20 | Média | SU-02, SU-03, SU-05det, SU-07, SU-07det, SU-08, SU-09 · Entrada mais rápida | Confirmado | Por grupo: formulários SU (helper fs em areas/suprimentos.py) com 0 inputmode e datas sem atalho; SU-* ocultas | Rejeitar o polimento nas SU: o componente da onda 1 corrige o motor e as SU saem com o SUP-06 | EX-02 | P | Baixo |
| SUP-21 | Média | SU-08 · Entrada mais rápida | Confirmado | areas/suprimentos.py:1046 unidade 'kg ou L', origem padrão 'Galpão 2' | Adaptar: transferir a partir do lote (⋯ em EST › Saldos), com unidade e origem do lote; SU-08 sai | 4 | P | Baixo |
| SUP-22 | Média | PSUP · Necessidade essencial | Confirmado | areas/paineis.py:183 cartões só com 'Como calcular' (crítica RESOLVE A-29, sem fatia) | Adotar: lista de pendências com a ação no item (painel por exceção) | 4 | M | Baixo |
| SUP-23 | Média | PMAN · Necessidade essencial | Confirmado | PMAN: cartões sem clique (areas/paineis.py); 'Espera por peça' só na MA (areas/maquinas.py:304) | Adotar: cartões viram atalhos filtrados; entra "Espera por peça" | 4 | P | Baixo |
| SUP-24 | Média | SU-01 · Ações no ⋯ | Confirmado | areas/suprimentos.py:281 e :296 'Reprogramar proposta' no topo com item padrão; links na coluna | Rejeitar na SU-01 (oculta); o padrão do ⋯ vale na demanda viva | EX-02 | P | Baixo |
| SUP-25 | Média | SU-07 · Ações no ⋯ | Confirmado | areas/suprimentos.py:912-913 botões por estado ('Separar FEFO'); alguns só respondem 'Bloqueado' | Adaptar: a fila de separação viva é o EST (OS-06); SU-07 sai | EX-02 | P | Baixo |
| SUP-26 | Média | SU-09, EST · Ações no ⋯ | Confirmado | areas/suprimentos.py:1147-1148 ações na célula; EST g_cnt idem | Adotar no EST com o componente ⋯; SU-09 sai | 1 | P | Baixo |
| SUP-27 | Média | EST · Ações no ⋯ | Confirmado | areas/processo_estoque.py:229-231 'Aceitar consumo', 'Recusar relato' e 'Voltar' dentro da célula; :448 'Liberar após inspeção' | Adotar: ⋯ e confirmação em painel com a consequência (AL-10, AL-11). Integrar depois do PR #81 (mesmo arquivo) | 1 | M | Médio |
| SUP-28 | Média | SU-06, SU-08 · Ações no ⋯ | Confirmado | areas/suprimentos.py:806 'Liberar qualidade' na célula; :1052 'Estornar com vínculo' com escolha do movimento; :1076 | Rejeitar na SU-06 e SU-08 (ocultas); "Estornar com vínculo" só com o motivo vai ao EST › Movimentos | EX-02 | P | Baixo |
| SUP-29 | Média | SU-03, SU-05 · Ações no ⋯ | Confirmado | areas/suprimentos.py:389 'Reserva em conflito' no meio do item; :652 e :678 botões de seção | Rejeitar na SU-03 e SU-05 (ocultas); os números em conflito saem com a consolidação (SUP-06) | EX-02 | P | Baixo |
| SUP-30 | Média | CMP · Ações no ⋯ | Confirmado | areas/processo_compras.py:221 e :415-416 'Ver origem' e 'Abrir compra' na célula | Adotar com o componente ⋯; clique na safra abre a compra | 1 | P | Baixo |
| SUP-31 | Média | MA · Ações no ⋯ | Confirmado | areas/maquinas.py:150 próximo passo só texto; :164 ma_linhaOm pendência sem ação | Adotar depois da MA-VINCULO (mesmo arquivo; ela já usa ⋯ › Desvincular): ⋯ por fase, cancelar por último | 1 | M | Baixo |
| SUP-32 | Média | SU-05det · Modal e botões | Confirmado | areas/suprimentos.py:733 e :736 botão 2 vezes; :718 bloqueio | Adaptar: SU-05det oculta; a regra "botão que só recusa fica desligado com motivo" entra no componente; a tela sai | EX-02 | P | Baixo |
| SUP-33 | Média | SU-05 · Modal e botões | Confirmado | areas/suprimentos.py:671 'emissão automática em 26/09' sem confirmação | Adotar a regra (P34): automação gera rascunho, nunca emite; rótulo e mensagem já | 0 | P | Baixo |
| SUP-34 | Média | SU-04 · Modal e botões | Confirmado | areas/suprimentos.py:591 'Aprovar contratação' → SU-05 (contratos) | Adaptar: a escolha da proposta já existe no CMP (etapas 4 e 5); SU-04 sai | EX-02 | P | Baixo |
| SUP-35 | Média | CMP · Lote | Confirmado | areas/processo_compras.py:794-796 linhas 'Abaixo do ponto de pedido' uma a uma | Adotar: seleção e "Abrir reposição dos selecionados" (requisição, não pedido; P34) | 3 | M | Baixo |
| POS-09 | Média | BEN · Entrada mais rápida | Confirmado | areas/processo_beneficiamento.py:124-129 bnSaidaForm, um registro por vez, caixas e bruto digitados | Adaptar: grade "Saídas do turno" (EDL-01) e "Ler balança" simulado; quantidade nunca do turno anterior | 3 | M | Médio |
| POS-10 | Média | BEN · Modal e botões | Confirmado | ben.js:305 próximo passo 'Autorizar rota e liberar' mesmo com impedimentos | Adotar: primária = primeira resolução; liberar só verde com a lista vazia (servidor continua travando) | 2 | P | Baixo |
| POS-11 | Média | EXPED · Entrada mais rápida | Confirmado | areas/vendas.py:314 'Placa' texto; :371 bruto e tara digitados | Adaptar: placa do cadastro do transportador; "Ler balança" simulado (como POS-03) | 4 | P | Baixo |
| POS-12 | Média | BEN · Resolver em 1 clique | Confirmado | areas/processo_beneficiamento.py:150 só 'Retirar … da ordem' | Adotar: "Abrir inspeção do L39-119" e "Avisar Marta" no impedimento; retirar no ⋯ | 2 | P | Baixo |
| POS-13 | Média | PROD · Necessidade essencial | Confirmado | areas/producao.py:371-372 Resultado Conforme ou Não conforme + Observação | Adaptar: critérios do padrão (medido × limite) com número e unidade, sem valor inicial; classe sugerida pelo cálculo; padrões por produto vêm da fazenda (proprietário) | 4 | M | Médio |
| POS-14 | Média | PCOM · Resolver em 1 clique | Confirmado | areas/vendas.py:484 'Para cobrir: publicar…' só texto | Adotar: "Pedir publicação da S41" e "Renegociar PV-038" no painel | 4 | P | Baixo |
| POS-15 | Média | VEN · Resolver em 1 clique | Confirmado | areas/vendas.py:98 'troca o lote ou cancela a reserva' | Adotar: "Trocar lote" numa operação atômica | 4 | M | Médio: reserva (ATP-07) |
| POS-16 | Média | VEN, PROD · Entrada mais rápida | Confirmado | areas/producao.py:236 prFormReserva, um lote por vez | Adaptar: "Alocar automaticamente" como proposta editável (FEFO, mesma classe e local), confirmada uma vez; reserva atômica por lote | 3 | M | Médio |
| POS-17 | Média | COLH · Lote | Confirmado | producao.js:623 'Coletar contagem' só navega para o MB-07 | Adotar: "Pedir contagem à equipe" por seleção, uma tarefa por talhão no app | 3 | M | Baixo |
| POS-18 | Média | VEN, PCOM · Resolver em 1 clique | Confirmado | areas/vendas.py:96 e :494 'Recebimento é do Financeiro (fora desta etapa)' | Adaptar: "Enviar à cobrança" cria item na fila do Financeiro; GE-05 depende do menu | 4 | P | Baixo |
| POS-19 | Média | CO-01, CO-02, CO-03, CO-04, CO-05, CO-06, CO-07 · Ações no ⋯ | Confirmado | Por grupo: CO-01..07 com 7 grades de botões na linha (inventario_site70.out); ocultas, entrada pelo Mapa (IN-04 → CO-06) | Rejeitar: pós-colheita antigo; as telas vivas recebem o ⋯ (POS-05); fechar a porta do Mapa | EX-02 | P | Baixo |
| POS-20 | Média | LO-01, LO-02, LO-03, LO-04 · Ações no ⋯ | Confirmado | Por grupo: LO-01..04 com grades de botões (inventario_site70.out); ocultas, via GE-03 → LO-04 | Rejeitar o polimento; portaria, lacre e frete vão ao EXPED (POS-06); fechar a porta | EX-02 | P | Baixo |
| POS-21 | Média | LO-04 · Modal e botões | Confirmado | areas/logistica.py:552-560 contrata com 1 clique | Adotar a regra (EX-33): confirmação com consequência e alçada onde o frete viver; LO-04 sai | 0 | P | Baixo |
| POS-22 | Média | LO-02det · Entrada mais rápida | Confirmado | areas/logistica.py:396 Evidência com opção única 'Foto do lacre anexada' | Adotar a regra (EX-34): evidência só com a foto; vale no checklist do EXPED (POS-06) | 0 | P | Baixo |
| POS-23 | Média | VE-04 · Necessidade essencial | Confirmado | areas/comercial.py:338-344 disputa de 1,8 t sem líquido na linha | Rejeitar na VE-04 (oculta); levar o líquido por kg à alocação do VEN se a disputa existir lá | EX-02 | P | Baixo |
| POS-24 | Média | CO-06det · Erro ou risco | Confirmado | areas/colheita.py:584 'Liberar para destinação compatível' sem motivo nem laudo (defeitos 103 > 86) | Adotar a regra (EX-33): decisão em formulário com destino, classe, laudo e motivo no PROD; CO-06det sai | 0 | P | Baixo |
| POS-25 | Média | PT-04det, PT-07 · Modal e botões | Confirmado | areas/parceiros.py:361 'Recusar crédito' diz "com motivo" sem pedir; :506 'Revogar acesso' imediato | Adotar: motivo obrigatório e consequência escrita; revogar no fim do ⋯ com confirmação que nomeia a pessoa | 0 | P | Baixo |
| POS-26 | Média | VE-06 · Entrada mais rápida | Confirmado | areas/comercial.py:516 'Novo caso' com 4 textos | Rejeitar na VE-06 (oculta); casos migram para VEN e EXPED (POS-07) | EX-02 | P | Baixo |
| GES-12 | Média | IC · Resolver em 1 clique | Confirmado | areas/inteligencia.py:251 primária 'Abrir Compra de insumos' → CMP sem contexto | Adotar: abre a compra com insumo, quantidade e data (rascunho; P34) | 4 | P | Baixo |
| GES-13 | Média | GE-08 · Modal e botões | Confirmado | areas/gestao.py:645-646 painel estático com 4 textos ('matricula_1874.pdf'); :703 'Registrar liberação da 2ª parcela' sempre 'Bloqueado' (igual na int90, :762-764) | Adotar: primária do topo = documento pendente; liberação desligada com motivo; arquivo escolhido ou documento já cadastrado | 4 | M | Baixo |
| GES-14 | Média | GE-08 · Necessidade essencial | Confirmado | areas/gestao.py:701 'Comparar propostas' só mensagem | Adotar: quadro lado a lado (CET, garantias) e "Escolher proposta" com motivo | 4 | M | Baixo |
| GES-15 | Média | GE-08 · Clareza | Confirmado | g2lib.js:677 r.ro → 'Consulta: você não tem permissão para editar este registro.' | Adotar no motor (com o AGRO-35): motivo do estado; "sem permissão" só por papel | 1 | P | Baixo |
| GES-16 | Média | GE-04 · Lote | Confirmado | Por grupo: seleção só em 4 grades no render (SAF, CA-01, CA-03, IN-02); nenhuma em GE, CD, CF e ON (inventario_site70.out) | Adaptar: lote só onde a tarefa se repete (programar pagamento, remessa, mudar equipe); aprovar pagamento fora do lote; forma do lote conforme §4 (SEL-04) | 3 | M | Médio |
| GES-17 | Média | GE-05 · Entrada mais rápida | Confirmado | areas/gestao.py:446 painel 'Registrar cobrança autorizada' × formulário do título | Adotar: um formulário, do ⋯ do título; canal limitado aos autorizados (CD-05) | 4 | P | Baixo |
| GES-18 | Média | GE-02det · Necessidade essencial | Confirmado | areas/gestao.py:259 'Abrir documentos de origem' → GE-06det, mesma ponte de variações | Adotar (EX-02): um detalhe do desvio | EX-02 | M | Baixo |
| GES-19 | Média | GE-02det · Erro ou risco | Confirmado | areas/gestao.py:243 'Consumo (L/ha)' '2,2 (antes 2,0)' em texto já escrito; plano 'Fungicida · Feijão' | Adotar (decisão fixa): número vazio; real e atual como chips que exigem toque | 0 | P | Baixo |
| GES-20 | Média | GE-06 · Necessidade essencial | Confirmado | areas/gestao.py:476-478 'Ver packing' → CO-05, 'Ver irrigação' → IR-03, sem filtro | Adotar: recorte que forma o número; destinos vivos no lugar dos legados | 4 | P | Baixo |
| GES-21 | Média | GE-01 · Necessidade essencial | Confirmado | GE-01: cartões sem clique; sem primária (areas/gestao.py:167) | Adaptar: junto com a decisão de menu (GES-01) | 4 | P | Baixo |
| GES-22 | Média | GE-06det · Resolver em 1 clique | Confirmado | areas/gestao.py:509 hipótese em chip, sem ação | Adotar: ⋯ por hipótese cria ou comenta o caso com o dono certo | 4 | P | Baixo |
| GES-23 | Média | CD · Necessidade essencial | Confirmado | Em parte: os estados existem por cadastro (areas/cad_ativos_pessoas.py:319 c3e…); hubs sem estado; na int90 a CRE F2 refez o MOD-CRE com 4 cartões | Adotar o estado no cartão do hub; MOD-CRE: não mexer (decisão recente da CRE F2) | 4 | P | Baixo |
| GES-24 | Média | CD-01 · Clareza | Confirmado | areas/cad_fazendas.py:338 'Definir polígono ›' e 'Abrir talhão ›' dentro do formulário | Adaptar: clique na linha abre a CD-01det; editar no ⋯; conferir com CAD-03 e com a seta TAB-11 (em andamento) | 1 | P | Baixo |
| GES-25 | Média | ON-01 · Entrada mais rápida | Confirmado | Executado (repro M3): 'E-mail do responsável' lista otavio@…, Ana, Marcos, Rui, Paula; causa no motor (engine.py:705, chave 'responsável') | Adotar: cultura só no passo 3; e-mail calculado do responsável; importar antes de desenhar; a lista sai com o POS-08 | 4 | P | Baixo |
| GES-26 | Média | ON-01 · Erro ou risco | Confirmado | areas/onboarding_backoffice.py:67-68 Papel Operador, Agrônomo, Gestor, Consulta × G2_PAPEIS da CF-01 | Adotar: mesma lista e regra da CF-01; agrônomo só com CREA | 2 | P | Médio: acesso |
| GES-27 | Média | GE-03 · Modal e botões | Confirmado | areas/gestao.py:316 e :537 'Motivo' cai na lista global (engine.py:695: Sonda deslocada, Chuva…) | Adotar com a correção do motor (POS-08) e motivos próprios; aprovador calculado pela alçada | 1 | P | Baixo |
| GES-28 | Média | ON-01 · Entrada mais rápida | Confirmado | areas/onboarding_backoffice.py:64 'Arquivo do CAR' e recibo em texto | Adaptar: escolher o arquivo; número do recibo lido (simulado); gravar uma vez no documento da fazenda | 4 | M | Baixo |
| GES-29 | Média | CD-03 · Entrada mais rápida | Confirmado | 0 'Duplicar' em areas/cad_ativos_pessoas.py; custo/h digitado | Adotar: "Duplicar" no ⋯ da máquina; "Usar realizado" como chip que exige toque (EX-29) | 4 | P | Baixo |
| GES-30 | Média | CD-04 · Entrada mais rápida | Confirmado | areas/cad_ativos_pessoas.py:393 g_pes com 22 campos à vista | Adaptar: formulário essencial (CAD-02, DEC-1610-14); "Cadastrar várias" por colar (EDL-01) | 3 | M | Baixo |
| GES-31 | Média | CD-08 · Resolver em 1 clique | Confirmado | areas/cad_culturas.py:230 e :249 'Comparar com o realizado' só avisa | Adotar (EX-29): coluna Realizado e "Usar como novo padrão" (nova vigência, histórico mantido) | 4 | M | Baixo |
| GES-32 | Média | GE-02 · Modal e botões | Confirmado | areas/gestao.py:210-216 'Publicar previsão V2' com a V2 já publicada; 'Autorizar versão' sempre bloqueado; link do topo leva a 1 caso | Adotar: botão só com efeito possível; renomear o link | 4 | P | Baixo |
| GES-33 | Média | GE-04 · Modal e botões | Confirmado | areas/gestao.py:347 e :382 dois 'Importar retorno' sem prévia | Adotar: um botão com prévia (P22); divergência vira item | 4 | P | Baixo |
| GES-34 | Média | IN-04 · Lote | Em andamento | MAPA-UX (/tmp/claude-0/mapaux, avaliacao-claude.md: barra e painel da seleção). Confirmado: areas/inicio.py:1097 painel da seleção só com vistoria | Adaptar: "Planejar operação nos N talhões" cria O.S. em rascunho, uma por talhão, cada uma com aprovação individual; entra na MAPA-UX ou depois | 3 | M | Médio |
| AGRO-33 | Baixa | PL-05 · Entrada mais rápida | Confirmado | areas/planejamento.py:493 'Prazo' sel 'vence hoje', 'até 3 dias', 'no prazo'; PL-05 oculta | Adaptar: data com atalhos (onda 1) e faixa calculada (prazo()); só na tela viva do impedimento | 1 | P | Baixo |
| AGRO-34 | Baixa | AG-01 · Clareza | Confirmado | areas/agronomia.py:631 kind==='erradicar' → área 1; rótulo 'Data da aplicação' | Adaptar: área sugerida pela conta só como sugestão que exige toque; rótulo "Data da erradicação" | 4 | P | Baixo |
| AGRO-35 | Baixa | PL-02det · Clareza | Confirmado | g2lib.js:677 mensagem de permissão sempre que r.ro | Adotar no motor (com o GES-15) | 1 | P | Baixo |
| AGRO-36 | Baixa | PL-01 · Entrada mais rápida | Confirmado | Por grupo: engine.date_field (engine.py:718-722) e o formulário do motor (g2lib.js:684 type date) sem atalho; meta '64 sc/ha' em texto no PL-01 | Adotar o componente "data com atalhos" (onda 1); meta numérica com a unidade da cultura (como no SAF) | 1 | P | Baixo |
| AGRO-37 | Baixa | IR-04 · Erro ou risco | Confirmado | areas/irrigacao.py:654 Cobertura com opções fixas 'Pivô 1', 'Pivô 2', 'Gotejo T7', 'Fazenda' | Adotar: setores da fazenda do filtro, com a fazenda no rótulo; pré-selecionar o setor de origem | 4 | P | Baixo |
| OS-33 | Baixa | CA-03 · Ações no ⋯ | Confirmado | areas/campo.py:462 links na coluna 'Próxima ação'; CA-03 oculta | Adaptar: componente ⋯ quando a CA-03 for consolidada; a CA-03det já tem "Mais ações" | EX-02 | P | Baixo |
| OS-34 | Baixa | MB-08 · Modal e botões | Confirmado | areas/mobile.py:983-987 5 botões na volta | Adotar: Pausar ou Retomar pelo estado; o resto no ⋯ | 1 | P | Baixo |
| OS-35 | Baixa | MB-10 · Ações no ⋯ | Confirmado | areas/mobile.py:1300 'Descartar carga a pesar' ao lado das ações comuns | Adotar: descarte por último no ⋯, com motivo; horas pelo relógio (OS-07) | 1 | P | Baixo |
| OS-36 | Baixa | MB-06 · Entrada mais rápida | Confirmado | areas/mobile.py:860 e :886 checkbox mb_gpsfora manual | Adaptar: o app calcula a distância e propõe; a pessoa confirma (GPS real só no produto) | 4 | P | Baixo |
| OS-37 | Baixa | IN-03 · Entrada mais rápida | Confirmado | areas/inicio.py:1761 'Nova tarefa vinculada' com compromisso em texto; IN-03 sem caminho | Adaptar: busca de registro, junto com o OS-30 | 4 | P | Baixo |
| OS-38 | Baixa | OS-0424-ficha · Entrada mais rápida | Confirmado | areas/os_campo.py:174 colunas 'Feito' e 'Hora' em branco | Adotar: QR na ficha abre a O.S. no app; papel só como reserva | 4 | P | Baixo |
| SUP-36 | Baixa | SU-02 · Modal e botões | Confirmado | areas/suprimentos.py:309 e :319-320 'Salvar' cria proposta; 'carreta 36 t' texto | Adaptar: verbo do efeito ("Propor versão v5"); SU-02 sai; políticas em Configurações: proprietário | EX-02 | P | Baixo |
| SUP-37 | Baixa | SU-01 · Erro ou risco | Confirmado | areas/suprimentos.py:269-272 'Falta firme = 4 − 0 − 0 = 3 un' com 'res. 1' ao lado | Adotar: mostrar a parcela reservada na conta; vale para a demanda viva | 4 | P | Baixo |
| SUP-38 | Baixa | IV · Resolver em 1 clique | Confirmado | inteligencia.js:101 recomendação 'Vender agora'; detalhe só com 'Fechar' | Adotar: ação no detalhe com contexto ("Criar oferta", "Publicar previsão") | 4 | P | Baixo |
| POS-27 | Baixa | VE-01, VE-03, VE-04, VE-05, VE-06 · Ações no ⋯ | Confirmado | Por grupo: VE-01..06 com botões na linha (inventario_site70.out) | Rejeitar: telas legadas (POS-07) | EX-02 | P | Baixo |
| POS-28 | Baixa | CARGA, EXPED, VEN · Clareza | Confirmado | areas/vendas.py:108 a primária muda com a linha ('Confirmar saída da …') | Adotar: primária fixa por tela; ação do item no painel e no ⋯ (como o BEN) | 1 | P | Baixo |
| POS-29 | Baixa | PT-02det · Modal e botões | Confirmado | areas/parceiros.py:252 'Nada mudou desde a v'+vv | Adotar: primária "Responder esclarecimento" enquanto houver pergunta | 4 | P | Baixo |
| POS-30 | Baixa | PT-02det · Entrada mais rápida | Confirmado | areas/parceiros.py:231 modal por item 'Item da proposta' | Adaptar: preço editável em grade (EDL-01) com R$/kg; colar da planilha | 3 | M | Baixo |
| POS-31 | Baixa | PT-05det · Entrada mais rápida | Confirmado | areas/parceiros.py:430 'Número' e 'Anexo' texto; 'Tipo' cai na lista errada (engine.py:695) | Adaptar: enviar o XML (simulado) e conferir com pedido e carga; a lista do Tipo sai com o POS-08 | 4 | M | Baixo |
| POS-32 | Baixa | PT-01, PT-02, PT-03, PT-04, PT-05, PT-06, PT-07 · Ações no ⋯ | Confirmado | areas/parceiros.py:168 e :201 coluna 'Abrir' repete o clique da linha; 'Revogar acesso' na linha | Adotar: sem coluna 'Abrir' (a linha abre); ⋯ com revogar por último | 1 | P | Baixo |
| POS-33 | Baixa | CO-03 · Modal e botões | Confirmado | areas/colheita.py:317 'Emitir romaneio' reemite | Rejeitar na CO-03 (oculta); "Reimprimir" no ⋯ onde o romaneio vive (CARGA) | EX-02 | P | Baixo |
| POS-34 | Baixa | CO-02det · Erro ou risco | Confirmado | areas/colheita.py:265 'Horas de equipe' padrão '8 × 3,0 h' e 'Dia' padrão '24/09', em texto | Adotar a regra (quantidade real sem padrão): CO-02det é oculta mas alcançável (IN-04 → CO-06 → CO-02 → CO-02det); tirar os padrões já | 0 | P | Baixo |
| GES-35 | Baixa | CD-07 · Entrada mais rápida | Confirmado | areas/cad_produtos_estrutura.py:361 'Não existe o código' só depois; campos em texto | Adotar: busca no plano de contas importado | 4 | P | Baixo |
| GES-36 | Baixa | CD-05 · Entrada mais rápida | Confirmado | areas/cad_parceiros.py:259-262 CNPJ conferido; razão social digitada | Adaptar: consulta pública de CNPJ simulada no protótipo; no produto é serviço externo (proprietário) | 4 | P | Baixo |
| GES-37 | Baixa | GE-04 · Entrada mais rápida | Confirmado | Por grupo: areas/gestao.py:364 'Pagamento programado' date sem atalho; idem GE-05, GE-07, GE-08 e CD-04 | Adotar com o componente "data com atalhos" (chip "no vencimento" por campo) | 1 | P | Baixo |
| GES-38 | Baixa | ON-01 · Clareza | Confirmado | areas/onboarding_backoffice.py:111-112 status 'Passo 3 de 6' e primária 'Criar primeiro planejamento' | Adotar: dizer o motivo do atalho ou seguir o passo em andamento | 4 | P | Baixo |
| GES-39 | Baixa | PA · Ações no ⋯ | Confirmado | areas/processo_planos.py:183 e :585 cartão com 'Abrir plano →' | Adotar: cartão inteiro clicável e ⋯ "Criar plano a partir deste" | 1 | P | Baixo |
| GES-40 | Baixa | BO-02 · Resolver em 1 clique | Confirmado | areas/plataforma.py:81-85 bo_dec só para contestação | Adotar: "Enviar 2ª via" simulado; régua visível | 4 | P | Baixo |

**Contagem** (gerada por `reproducao/gera_tabela.py`, saída em `reproducao/tabela_claude.out`, **executado**):

| | Confirmado | Refutado | Já resolvido | Em andamento | Total |
|---|---|---|---|---|---|
| Todos | 167 | 1 | 0 | 19 | 187 |
| Prioridade Alta | 44 | 1 | 0 | 12 | 57 |

Por onda sugerida: 0 = 13 · 1 = 28 · 2 = 48 · 3 = 17 · 4 = 50 · EX-02 = 28 · Prop. = 3.

**Como validei:**
- **Os 57 altos:** um a um, com arquivo:linha lido. Em AGRO-08 e na causa do POS-08 e do GES-25, também no navegador (M1 a M3).
- **Os 130 médios e baixos:** cada um tem uma evidência de fonte, por busca dirigida (`grep`, lido).
- **Validados também por grupo:**
  - "ações soltas na linha" (POS-19, POS-20, POS-27, GES-16): contagem de grades com botões e com seleção no `inventario_site70.out`;
  - "data sem atalho" (AGRO-36, GES-37): amostra no motor (`g2lib.js:684`, `engine.py:718-722`) e nas telas (`gestao.py:364`, `planejamento.py:493`, `cad_ativos_pessoas.py`);
  - "formulários das telas SU" (SUP-20): 0 `inputmode` no `suprimentos.py`;
  - "lista pelo rótulo" (POS-08, GES-25, GES-27, POS-31): uma causa (`engine.py:695-709`) e 41 ocorrências no render.

## 2. O que a varredura deixou de fora

### 2.1 Ações dentro dos modais (o robô não clicou)

| # | O que acontece | Prova | Rótulo |
|---|---|---|---|
| M1 | PL-02 › "Decidir pendência": a lista mostra "Realizada" (`selectedIndex` 0), o rascunho fica vazio, "Evidência" não aparece e o Salvar responde "Informe decisão da pendência." A tela parece escolhida e recusa. | `reproducao/repro_modais_site70.out` M1; `g2lib.js:202`, `:217`; `engine.py:1975` | executado |
| M2 | CA-01det (do menu, pela OS) › "Ajustar produtos e doses do saldo": a lista "Produto" oferece Fungicida A, Soja em grão, Milho em grão, Mamão · cx 10 kg e Café beneficiado. A dose vem escrita ("0,45 L", texto, sem teclado numérico). Troquei a dose para 9,99 e "Ajustar e liberar saldo" respondeu "v3 liberada no saldo … liberada por Ana (agrônoma)". O painel não lê os campos, e a lista vem do rótulo. | M2; `areas/campo.py:272-275`; `engine.py:189-205`, `:695-709` | executado |
| M3 | ON-01 › "Rever dados": "E-mail do responsável" lista otavio@…, Ana, Marcos, Rui, Paula (mesma causa, chave "responsável"). | M3 | executado |
| M4 | 33 painéis estáticos (12 em telas do menu) confirmam com texto fixo, sem ler os campos. Exemplos: GE-02det "Propor novo parâmetro" (GES-19), GE-03 "Solicitar reabertura", GE-08 "Anexar documento condicionante" (GES-13), 7 no ON-01. | `reproducao/paineis_estaticos_site70.out`; `engine.py:189-205` | executado |
| M5 | 77 listas obrigatórias de formulário sem valor e sem opção vazia (20 em telas do menu: AG-02 Profundidade e Método, CMP Convite, Canal, Prazo e Proposta, EST Entregar a e Item · lote, GE-03 Rateio, GE-08 Credor, Garantia e Documento, CD-04 Líder…). Em registro novo, todas mostram a 1ª opção como se escolhida. | `reproducao/inventario_site70.out` | executado (contagem); efeito no navegador provado em M1 |
| M6 | Recusas e travas só aparecem ao salvar: EST › recebimento exige "Apta + quarentena = conferida" (`ESTV.g_rec`), conta que a pessoa faz de cabeça (SUP-05); OS › Ajustar confere o uso legal só ao salvar (OS-03). | `areas/processo_estoque.py` ESTV.g_rec; `areas/processo_os.py:870` | lido |

Consequência para a medida: os 810 campos do robô incluem campos de painéis que não gravam (M4) e listas que parecem pré-preenchidas sem estar (M5). Antes de comparar "antes × depois", separar o que é formulário real do que é painel estático.

### 2.2 Telas: alcance e versão

- **Portas dos fundos (executado, `reproducao/alcance_menu.out`):**
  - 79 das 87 telas fora do menu são alcançáveis a partir do menu: PL-04 por CA-01det → PL-05; CO-* pelo Mapa (IN-04 → CO-06); VE-* por GE-08 → VE-05; LO-* por GE-03 → LO-04; SU-* por GE-02det → SU-06 e por CA-01det → SU-07.
  - 8 não têm caminho: GE-01, IN-03, MB-05det, MB-08, MB-08x-recibo, PL-03, PM, PT-06.
  - O robô tratou as telas legadas como iguais às vivas. 67 achados citam só telas fora do menu (80 contando app e portal; `reproducao/achados_por_alcance.out`).
- **Versão:** o render da varredura já tem a int90 (EST-ONDA0, CRE F1/F2). Por isso a parte "EST" do SUP-08 não se reproduz no render. Ela só existe na base `b989864` (`areas/processo_estoque.py:517`).
- **GE-03** abriu em branco no robô (GES-04): as pendências do fechamento não foram medidas no navegador; validei pela fonte.

### 2.3 Perfis que não o Proprietário

- O robô usou o Proprietário (todos os papéis). Com outro perfil, a O.S. mostra a ação de outro papel desligada com o nome de quem pode ("Ajustar: disponível para … Troque o perfil no avatar", `areas/processo_os.py:831-833`). Isso segue o EX-05 e contraria a regra do EX-47 "ação sem permissão do papel não aparece" (ver §4).
- O inverso também acontece: o Proprietário vê "Consulta: você não tem permissão" quando o bloqueio é do estado (GES-15, AGRO-35, `g2lib.js:677`).
- Segregação (quem pede não aprova nem recebe) não aparece com um perfil que tem todos os papéis. A crítica RESOLVE reproduziu Ana abrindo, cotando, emitindo e recebendo a própria SC (R7b, executado lá).
- A ficha de crédito da int90 só grava para direção ou financeiro: com o Proprietário não se vê a recusa.

### 2.4 Celular a 390 px

- O ⋯ da linha tem 32 px no mouse e 44 px no toque (`engine.py:1207`, `:1210`). O EX-47 pede 36 e 48 px.
- Os cartões do app (MB-*) não usam o ⋯ do motor; cada tela monta os próprios botões (`areas/mobile.py:431-439`). Por isso OS-26, OS-34 e OS-35 precisam do "cartão com ⋯" da onda 1.
- A web a 390 px (OS, EST, CMP) não foi medida pelo robô. A barra de lote (`g2lib.js:640-650`) e o painel lateral precisam de prova a 390 px na onda 1.

### 2.5 Estados que a varredura não exercitou

- O robô clicou só na 1ª linha de cada tabela. As ações das outras fases da O.S. ficaram fora: Em execução (Registrar apontamento, Dispensar saldo), Em conferência (Conferir e encerrar) e Canceladas (custódia a devolver) (`areas/processo_os.py:616-645`).
- Linhas montadas em tempo de execução (EST, CMP, MA, SU-07, SU-09) mudam de ação conforme o estado (`areas/suprimentos.py:1147-1148`, `:912-913`).
- **Achado novo (lido):** a web pré-preenche a área do apontamento com o turno previsto, sem toque (`areas/processo_os.py:816`). É medição real vinda do plano, sem a pessoa pedir. Entra no OS-07.

## 3. Componentes do design system que a onda 1 precisa

| Componente | Já existe no motor | Falta | Decisão Claude |
|---|---|---|---|
| **Tabela com ⋯** | `engine.grid(…, menu_linha=True)` → `spec.rmenu` (`engine.py:1758`). O `g2lib.js:600` leva ao ⋯ só a parte de tipo `act` que não navega; `:614-618` monta o menu com ícone (`g2acaoIco`) e Excluir por último, em vermelho. Botão e menu em `engine.py:1205-1212` e `:1828-1829`; teclado do `g2mais` (↑ ↓ Home End, Esc devolve o foco; `docs/design-system/barra-limpa-mais-acoes.md`). O modo Cartões herda o ⋯ (`g2lib.js:470-482`). Só o SAF liga (`areas/processo_safra.py:97`). | 1) Não depender de `del` (`g2lib.js:614`). 2) Levar também a `cta` de ação (hoje fica na célula); link de ID e "Planejar ›" ficam. 3) Próximo passo em 1º e em negrito; separador antes das raras e destrutivas. 4) Item desligado com motivo (hoje o item não tem `dis` nem motivo). 5) Alvo de 36 px no mouse e 48 px no app. 6) Ligar por padrão nas grades do menu, com a lista de exceções medidas. 7) Item que pede dado abre o painel no formulário. 8) Nome acessível: manter "Mais ações de …" do DS (MAIS-01, testado) ou trocar para "Ações de …" do EX-47; o Codex decide. | Adotar e promover a padrão do `engine.grid`. Teste: `ds_1510_test.py` (TAB-05) com contraprova na base. |
| **Cartão com ⋯** | `engine.mais(contexto, itens, linha=True)` (`engine.py:1242-1250`) serve linha e cartão; os Cartões do motor herdam o ⋯. | Os cartões fora do motor não usam o componente: app (`areas/mobile.py`), biblioteca de planos (`areas/processo_planos.py:585`), painéis. Faltam cartão inteiro clicável e 48 px no app. | Adotar: passar app, PA e painéis pelo `engine.mais`. |
| **Barra de lote** | Seleção do motor: `sel`, `bulk`, `_selmsg`, `_selall` (`g2lib.js:640-650`, DS-40) diz o que está fora da vista. Resultado por item feito por tela (IN-02 `v.lote`, `areas/inicio.py:1690`; CA-01 mensagem). EDL-01 (SAF-LOTE) tem "aplicar aos marcados" dentro do painel. MA-VINCULO usa a SEL-04 (painel com a lista já marcada). | 1) Contrato por ação: a ação de lote declara se é permitida e recusa por linha. Hoje o motor não sabe, e por isso o CA-01 e o PL-04 levam O.S. com produto (EX-32). 2) Resultado padrão: feitas, com erro, pendentes, e "repetir só as pendentes". 3) Chave de idempotência do lote. 4) Conflito entre SEL-04 e caixas na tabela (§4). | Adaptar: um componente que abre o painel lateral com a lista já marcada (SEL-04), com o contrato `lote_ok`. Caixas na tabela só se o proprietário revir a SEL-04. |
| **Número com unidade** | No formulário do motor, o campo de tipo `num` abre o teclado decimal e mostra a unidade quando o campo declara `u` (`g2lib.js:684`, modo `decimal`, `hasU`). Erro junto ao campo (INP-11). INP-04 e INP-07 (selecionar ao focar, sem corretor) só na SAF-LOTE (`g2inp`, ainda não integrado). | Painéis estáticos montam número como texto, sem `inputmode` (`engine.py:736-743`; M2); `prFld` do pós-colheita usa campo de texto com unidade; 18 números sem unidade em formulários de telas do menu (`inventario_site70.out`); formulários das SU sem `inputmode`. | Adotar: um campo numérico do motor, usado também pelos painéis; INP-04/07 entram com a integração da SAF-LOTE. |
| **Data com atalhos** | Formulário do motor: `type=date` nativo (`g2lib.js:684`). Painéis: `engine.date_field` nativo (`engine.py:718-722`). Padrão local com chips "Hoje", "Ontem" e dias apontados na pesagem (`areas/producao.py:444-446`). INP-05 (dd/mm, ddmm) só no colar do EDL-01. | Campo do motor com atalhos declarados por campo (hoje, ontem, amanhã, +7; "no vencimento", "início da janela"), dd/mm digitável e a regra "data da operação ≠ data do registro". | Adotar: promover o padrão do `producao.py` ao motor. |
| **Busca com chips** | Lista suspensa do DS (`g2dsel`, `g2lib.js:1468`: ✓, teclado, letra inicial); busca da grade sem acento (`g2norm`, `g2lib.js:92`); `datalist` no Ajustar da O.S. (`areas/processo_os.py:1449`). "Buscar no cadastro…" e "+ Novo" do `engine.select` são só opções falsas da lista (`engine.py:749`). | Campo de busca tolerante (acento, código, apelido), chips dos mais usados no contexto e "criar no campo". Chips de frequência nunca para lote, dose ou quantidade. | Adotar para catálogo (produto, conjunto, registro); lista curta continua em um toque (SEL-03). |
| **Regra de entrada no guia** | INP-01 a INP-11 e EDL-01 em `padroes-1610.md` (SAF-LOTE, não integrado). | Ordem de método do EX-46 (calculado → herdado → capturado → lista → padrão seguro → digitado); "Mais opções" para o raro (CAD-02 já pede). | Adaptar: estender a seção INP, sem criar outra lista de regras. |

Duas correções do motor também são da onda 1, mesmo não sendo componente: opção vazia na lista obrigatória (M1, M5) e lista declarada no painel estático (POS-08, M2, M3).

## 4. Riscos de quebrar decisão fixa

1. **Aprovação agronômica individual** (DEC-1610-03, EX-32):
   - ~~Já quebrada em tela alcançável: PL-04 "Liberar prontas" (AGRO-01) e CA-01 "Liberar selecionadas" (OS-05).~~ → Δ 17/10-1: **errado**. Não há aprovação em lote nessas telas. As duas são mensagens fixas, sem operação (`msgbtn`/`imsg`), e liberar não é aprovar (CMD-06 ≠ CMD-42; DEC-1610-03 trata da aprovação). O O.S. em lote real (`cenGrupoLiberar`) revalida cada origem pelo `osc_liberar`, que exige a aprovação da versão. Ver §Δ.
   - O IN-02 mistura alçadas no lote (OS-32).
   - A barra de lote genérica repetiria o erro se não tiver o contrato por ação (§3).
   - Contraprova: um teste que reprova a base (lote com O.S. com produto) e passa na candidata.
2. **Último valor e medição real:**
   - Todo atalho novo é toque explícito e destacado, nunca padrão: "Executado como planejado", "Igual à nota", "Igual ao esperado", "Usar realizado", "Marcar todos conforme", "Alocar automaticamente", área sugerida.
   - Hoje já há três pré-preenchimentos sem toque: a web da O.S. (`processo_os.py:816`), o SU-07det (`suprimentos.py:959`) e o CO-02det (`colheita.py:265`).
   - O AG-01 preenche a dose mínima da bula ao escolher o produto (`areas/agronomia.py:649`). A crítica RESOLVE manda cortar isso na troca de produto.
3. **Kanban de 5 fases:** "Aguardam aprovação" é filtro, não coluna. O ⋯ por fase não cria etapa.
4. **Servidor como autoridade:**
   - Quadro "Insumos × estoque", "Alocar automaticamente" e prévias de lote são prévia; reserva e liberação reconferem.
   - Todo comando novo de 1 clique leva chave de idempotência com o conteúdo (a crítica RESOLVE reproduziu a mesma chave aceita com outro conteúdo, NOVO-2).
5. **Design system:**
   - **BOT-07 e BOT-01:** a linha abre o registro; um verde por contexto. O ⋯ não vira segundo verde, e a escolha não usa o verde da primária (AGRO-26).
   - **SEL-04 × EX-47:** a SEL-04 (padrão do proprietário de 15/10) diz "agir em várias linhas é no painel lateral, nunca com caixas na tabela". O EX-47 pede "caixa na primeira coluna e barra de lote". É divergência de padrão do proprietário. Proposta: o lote abre o painel com a lista já marcada (o filtro rápido ou o chip faz o recorte), como a MA-VINCULO já faz.
   - **EX-05 × EX-47:** hoje a ação de outro papel aparece desligada com quem pode; o EX-47 quer que ela não apareça. Proposta: no ⋯ ela some; no detalhe, o próximo passo diz em texto "Aguarda Ana (agrônoma)".
6. **Telas fora do menu (decisão de 25/09):** polir tela oculta gasta onda e mantém duas verdades (EX-01, EX-02). Corrigir nela só o risco de decisão fixa (onda 0) e fechar a porta.
7. **Painéis que fingem efeito:** no teste com usuários (DEC-1610-02), a pessoa veria "v3 liberada" com dose 9,99 (M2). Antes do teste, converter em comando real ou dizer "simulado" no resultado.
8. **Integrações reais** (NF-e na SEFAZ, balança, CNPJ, CAR, OCR de laudo): ficam com o proprietário (AGENTS §2). No protótipo, só leitura de arquivo local ou simulação rotulada.

## 5. Três listas

**Aplicar**
- **Onda 0 (11 achados, todos P; Δ 17/10-1 tirou AGRO-01 e OS-05, que passam à onda 1 como "sucesso sem operação"):** fecha as violações de decisão fixa e os atos sem fricção (OS-32, SUP-08, GES-19, POS-34, POS-22, AGRO-29, GES-07, POS-21, POS-24, POS-25, SUP-33).
- **Componentes da onda 1 e cinco correções do motor** (⋯ sem `del`, opção vazia, lista declarada, motivo do estado, data com atalhos), cada um numa peça comum. Atendem os 28 achados da onda 1 e tiram a causa de vários médios.
- **Fechar as portas dos fundos** antes de polir: 28 achados viram consolidação, e cai a divergência de números entre telas (EX-01).
- **RESOLVE-1-CLIQUE como dona dos 18 achados de falta de material:** uma fonte de disponibilidade (`supCobertura`) antes de qualquer botão de 1 clique.
- **EDL-01 promovido ao motor e reaproveitado:** contagem do EST, talhões da CD-01, saídas do turno, preços do portal, safristas.

**Deixar de fora (com gatilho)**
- Integrações reais (SUP-05, POS-03, POS-06, POS-11, GES-36, AGRO-07 OCR). Gatilho: o proprietário autorizar custo e conta.
- Lugar no menu de Gestão, Meu dia, Aprovações, Agenda, Recomendações e Políticas (GES-01, AGRO-11, OS-10, OS-30, SUP-06). Gatilho: decisão do proprietário.
- Aceite automático na tolerância (OS-08, OS-16, EX-10) e dispensa de cotação na urgência (SUP-12). Gatilho: proprietário.
- Troca de fonte de N com dose recalculada (AGRO-03). Gatilho: RT e Gemini.
- BOM de secagem e café (POS-02) e critérios de qualidade por produto (POS-13). Gatilho: dado real da fazenda.

**Cortar**
- Polimento de tela oculta com equivalente vivo: os 12 "Rejeitar" e o resto da EX-02.
- "Safra como entidade nova" (AGRO-09): o SAF já é a entidade.
- Botões "como planejado", "como na nota" e "igual ao esperado" como padrão automático: só chip com toque.
- Caixa de seleção em toda tabela por padrão: só onde o lote é permitido.
- ⋯ na fila de ação única antes da medida (exceção do próprio pedido).

## 6. Suposições e pendências

| # | Suposição ou pendência | Gatilho de retomada |
|---|---|---|
| S1 | O render da varredura equivale à int90 (provas no cabeçalho). | O Codex confirmar a versão publicada 1792184197-5a81. |
| S2 | Esforço P/M/G por leitura, não medido. | Fatia escrita pelo Codex, com aceite. |
| S3 | O inventário estático conta linhas da semente; o robô conta o que a tela monta. Os números não se comparam 1 a 1. | Repetir o robô (P1). |
| P1 | Não reproduzi a medida "antes" do robô. Preferi a reprodução dirigida no navegador (M1 a M3), depois que o `q30.out` deu FIM, com 1 Chrome meu, perfil e porta próprios. | Candidata da onda 1: rodar o robô no render da base da onda e na candidata, mesma pasta de saída, separando painel estático (M4) de formulário real. |
| P2 | SEL-04 × caixas na tabela. | Decisão do proprietário. |
| P3 | EX-05 × "sem permissão não aparece"; nome "Mais ações de" × "Ações de". | Desenho do Codex; proprietário se divergir. |
| P4 | Lugar no menu (GES-01, AGRO-11, OS-10, OS-30, SUP-06). | Proprietário. |
| P5 | Integrações reais e custo. | Proprietário. |
| P6 | Tolerância e aceite automático do turno (EX-10). | Proprietário. |
| P7 | Arquivos compartilhados: OS-14 espera o PR #88; SUP-04, SUP-13, SUP-14 e SUP-31 esperam a MA-VINCULO; SUP-27 espera o PR #81; GES-24 confere com a TAB-11; GES-34 com a MAPA-UX. | Integração de cada frente. |
| P8 | Teto de 3 frentes (AGENTS §3.6): RESOLVE, SAF-LOTE, TAB-11, MA-VINCULO, OS-LOTE e MAPA-UX já estão abertas. A onda 0 e a onda 1 precisam caber no teto. | O Codex contar no checkpoint. |

**Gemini real, pelo conector do Codex** (só decisão material de domínio; pacote sintético):
- **AGRO-03:** troca de fonte de nitrogênio com dose recalculada pelo nutriente (ureia → nitrato), com a garantia de cada produto.
- **SUP-15:** reservar o livre da peça já ao pedir a compra, ou só na liberação. A crítica RESOLVE propõe reservar; a regra atual reserva na liberação; a DEC-1610-01 cobre só a peça que chega.
- **Receituário na compra avulsa de defensivo:** já listado na crítica RESOLVE §9.

**Proprietário:**
- P2, P4, P5 e P6.
- Exceção do ⋯ na fila de conferência, depois do teste com usuários (DEC-1610-02).
- Alçada e dispensa de cotação na compra urgente (SUP-02, SUP-12).

## 7. Reprodução (comandos e saídas)

| Comando (na pasta `reproducao/`) | Saída | O que prova |
|---|---|---|
| `python3 -B -I alcance_menu.py <site70> <gen37>` | `alcance_menu.out` | 79 telas ocultas alcançáveis e 8 sem caminho |
| `python3 -B -I inventario_estatico.py <site70> <gen37>` | `inventario_site70.out` | grades com botões na linha, rmenu, seleção, números sem unidade, 77 listas sem opção vazia, 41 listas pelo rótulo |
| `python3 -B -I paineis_estaticos.py <site70> <gen37>` | `paineis_estaticos_site70.out` | 33 painéis com resultado fixo (12 no menu) |
| `CHROME_BIN=/tmp/cloudchrome/chrome python3 -B -I repro_modais.py <site70> <gen37>` | `repro_modais_site70.out` | M1, M2 e M3 no navegador (Chrome headless, perfil temporário, http.server em porta livre) |
| `python3 -I gera_tabela.py <anexo> tabela_claude.tsv` | `tabela_claude.out` | tabela do §1 e contagens; falha se faltar ou sobrar ID |
| `python3 -B -I achados_por_alcance.py <anexo> <gen37>` | `achados_por_alcance.out` | 67 achados só em telas fora do menu (80 com app e portal) |

- `<site70>` é o render somente leitura da varredura; `<gen37>` é `tools/prototipo/v37/gen37` desta worktree. O `-B` evita gravar bytecode na pasta do gerador. O anexo vem de `git show 529adf7:docs/integracao/V73/pedidos-1610/entrada-acoes-revisao-anexo-achados.md`.
- O robô não foi rodado (P1). As primeiras execuções, sem `-B`, criaram `__pycache__` na pasta do gerador; apaguei e rodei de novo com `-B`, com as mesmas saídas. Nada foi gravado no render nem versionado fora de `docs/integracao/V73/ENTRADA-ACOES/`.

## Δ 17/10-1: AGRO-01 e OS-05 não quebram a aprovação individual

O gatilho foi o comentário 6228421250 do Codex no PR #47, que eu li depois de entregar a validação. A conferência abaixo é minha, no código de `f3ceb3c`.

**Por que a classificação anterior estava errada.**
- `areas/planejamento.py:440`, "Liberar prontas" (PL-04): é `msgbtn`. Mostra uma mensagem fixa ("… liberada por Ana …") e não chama o motor.
- `areas/campo.py:196`, "Liberar selecionadas" (CA-01): é `imsg`. Mostra um resultado fixo por item e também não chama o motor.
- A liberação real em lote é o `cenGrupoLiberar` (`areas/processo_os.py:444`):
  - passa origem por origem pelo `osc_liberar` (`:432`), que exige a aprovação da versão (`osLibPor`);
  - só dispensa a aprovação na irrigação só com água (DEC-2609-10);
  - exige a AL-01 ("Liberar selecionadas").
- A DEC-1610-03 trata da **aprovação**, que é individual: "Mantida a aprovação agronômica individual de cada O.S.". A liberação é outro comando: CMD-06 ≠ CMD-42 (PRD 41.2/41.3, blob `f50555e`).
- Conclusão: liberar várias O.S., cada uma já aprovada e revalidada uma por uma, não quebra a decisão.

**A nova classificação.**
- AGRO-01 e OS-05 passam a "sucesso sem operação comprovada": a tela afirma um resultado que o motor não produziu.
- Severidade S3: a mensagem engana, mas existe o caminho real pela O.S.
- Prioridade P, onda 1, junto com o contrato do lote.
- A correção mínima é escolher um dos dois:
  - a ação chama o domínio real e mostra o estado de cada linha;
  - ou a ação vira prévia, sem afirmar sucesso.
- Não se remove a liberação em lote.

**Contraprova proposta, ainda não executada:** um teste que clica em "Liberar prontas" e confere que o estado da O.S. no motor não mudou. Ele precisa reprovar a base, onde a mensagem diz "liberada" e o estado não muda.

**Efeito no resto da validação:** os demais itens da onda 0 continuam. O total de confirmados (167) também não muda: os dois achados continuam confirmados, só mudam de classe.
