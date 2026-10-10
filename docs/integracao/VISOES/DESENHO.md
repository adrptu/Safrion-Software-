# Visões das listagens (ViewSwitcher) · desenho

- **Pedido:** proprietário, 10/10/2026. Regra: "a visão nasce do atributo dominante"; uma visão só entra se o dado a sustenta. O texto chegou por roteiro de agentes e vale pelo que o proprietário escreveu no canal dele.
- **O que é:** síntese dos quatro relatórios de descoberta (`descoberta-inventario.md`, `-infra.md`, `-testes.md`, `-regras.md`, na mesma pasta), com conferência pontual no código. Onde os relatórios divergiam, a decisão e o motivo estão escritos.
- **Bases (só leitura):**
  - protótipo `sp-proto` = `claude/prototipo-v44` @ `0139898`;
  - composição em andamento `sp-comp` = `int/comp` @ `47ff754` (SAF-C01b, BEN rodada 2, PCM);
  - frentes não integradas: DS `sp-ds` @ `943433c`, TABR `sp-tabr` @ `8f19e0d`, NAV1 `sp-nav` @ `a7023ca`, PCM `sp-pcm` @ `ba03515`, CADUX `sp-cadux` @ `5d533a8`, SUP `sp-sup` @ `6ccd050`, DOM `sp-dom` @ `c764de9`;
  - software real `Safrion-Software-` @ `b8d6f84`.
- **Rótulo:** tudo aqui é **especificado**. Executado: só leitura de código, `grep` e `git log/diff`. Nenhum build, teste ou navegador; nada publicado; nenhum custo.
- **Revisão do Codex (VISOES-REV-20261010-01, PR #47 comentário 6093255041, 10/10):** 5 achados de especificação (S3) aplicados neste arquivo; os trechos mudados dizem "rev. Codex 01". Decisão de produto do Codex: onde mora a Atividade planejada (1.4). Ainda especificado; as provas executadas dos contraexemplos vão no pacote `docs/integracao/VISOES-1/`.
- **Revisão crítica (completude e minimalismo, 10/10):** aplicada neste arquivo; os trechos mudados dizem "revisão crítica". Também só leitura, sem build nem teste.
- **Caminhos:** relativos a `tools/prototipo/v37/gen37/` do `sp-proto`, salvo prefixo (`sp-comp:`, `sp-ds:`, `sp-cadux:`). `PRD:n` é a linha de `docs/PRD.md` @ `b8d6f84`. As linhas de `processo_os.py` mudam depois da composição e da DS.

## 0. Decisões em uma tela

1. **A fatia 1 é a O.S.** É a única listagem do menu em que Lista e Tabela agrupada (talhão + área somável) já existem sobre a mesma grade, com filtro guardado na sessão, e o seletor de texto atual já está no lugar pedido. Kanban e Carga por recurso entram só como migração do botão, sem mudança de regra.
2. **A visão vai em `?view=<k>`**, na query e não no hash, porque o hash já abre registros com expressões ancoradas. Precedência: URL › preferência (perfil × entidade) › Lista.
3. **O estado mora na grade** (`self.state.g2[gid].visao`); não há estado novo de tela.
4. **A dica no foco é o `g2dica` da DS.** Por isso a fatia 1 entra depois da DS e da composição, sem dica paralela.
5. **Nenhum arrastar nas 5 fatias do protótipo.** No Kanban, a fase só muda por comando com efeito (aprovação, reserva) e sem desfazer. No Calendário, ainda não existe validador único de janela. O pedido exige "com desfazer": **o Kanban fica sem arraste também no software real**, e o Calendário só arrasta onde há desfazer legítimo (2.10).
6. **Fatia 5 (Matriz, Árvore, Galeria): nada a implementar hoje.** Nenhuma listagem cumpre a regra. Os critérios de entrada ficam nos testes.
7. **Software real: especificar para a transferência, não aplicar agora** (seção 5).
8. **O Mapa da O.S. fica no IN-04** (rev. Codex 01, delegação de 09/10): a DEC-2609-09 não é reaberta e não há pergunta pendente ao proprietário. Só um pedido dele reabre.
9. **Mapa é um componente só** (revisão crítica): a visão Mapa reusa o mapa que já existe (IN-04 ou CD-01 da CADUX), com a geometria de fonte única. Nada de `mapa_visao()` novo. Onde a camada do IN-04 já responde à mesma pergunta sem filtro próprio da lista, a visão não entra (Setor de irrigação).
10. **Cortes por minimalismo** (revisão crítica): Irrigação IR-03 (Kanban e Carga), Setor IR-01 (Mapa) e Vistoria (Calendário) saem; Manutenção (Calendário) e Pedido de compra (Calendário) ficam ⏸. Motivos em 1.4.

---

## 1. Tabela final: entidade × visões

Legenda: ✓ entra (fatia) · ✗ não entra (motivo em 1.4) · ⏸ o dado sustenta, mas depende de decisão ou integração · "= L" a Lista já tem essa forma (árvore ou agrupada), então não vira visão separada.

### 1.1 Entidades com visão além da Lista (ou ⏸)

| Entidade | Tela / grade | Lista | Agrupada | Kanban | Calendário | Timeline | Mapa | Carga | Matriz | Árvore | Galeria |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Ordem de serviço | OS · `g_os` (`areas/processo_os.py:1220`) | ✓ F1 | ✓ F1 | ✓ F1 migra · F2 | ✓ F2 | ✗ | ✗ | ✓ F1 migra · F4 | ✗ | ✗ | ✗ |
| Ordem de beneficiamento | BEN · `g_ob` (`areas/processo_beneficiamento.py:18`) | ✓ | ✗ | ✓ F2 migra | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| Ordem de manutenção | MA › Ordens · `g_om` (`sp-comp:areas/maquinas.py:296`) | ✓ | ✗ | ✓ F2b migra | ⏸ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| Vistoria (MIP/MID) | AG-01 · `g_vis` (`areas/agronomia.py:831`) | ✓ | ✗ | ✗ | ✗ | ✗ | ✓ F3 | ✗ | ✗ | ✗ | ✗ |
| Talhão | CD-01 · `g_tal` (`areas/cad_fazendas.py:258`) | ✓ (árvore) | = L | ✗ | ✗ | ✗ | ✓ F3 migra | ✗ | ✗ | = L | ✗ |
| Cultivo (ocupação do talhão) | SAF · `g_cult_{k}` (`areas/processo_safra.py:84`) | ✓ | ✗ | ✗ | ✗ | ✓ F4 | ✗ | ✗ | ✗ | = L | ✗ |
| Máquina / ativo | MA › Ativos (PCM); CD-03 `g_atv` fica só Lista | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ F4 | ✗ | ✗ | ✗ |
| Pedido de compra | CMP etapa 6 · `g_ent` (`areas/processo_compras.py:103`) | ✓ (árvore) | = L | ✗ | ⏸ | ✗ | ✗ | ✗ | ✗ | = L | ✗ |
| Atividade planejada | SAF etapa consolidada · `g_op` (`areas/processo_safra.py:180`) | ✓ (árvore) | = L | ✗ | ⏸ | ✗ | ✗ | ✗ | ✗ | = L | ✗ |

Enquanto uma linha só tiver Lista e ⏸, ela não ganha seletor (Pedido de compra e Atividade planejada hoje).

### 1.2 O que sustenta cada ✓ (atributo dominante e fonte)

| Entidade · visão | Atributo dominante | Fonte |
|---|---|---|
| O.S. · Agrupada | Talhão (multivalor) + Área em ha, somada como ha-operação; o grupo conta O.S. distintas | colunas em `areas/processo_os.py:1220`; agrupamento TF06 em `:557-567`; PRD:297 e PRD:7292 |
| O.S. · Kanban | Fase com fluxo fixo de 5 etapas | `areas/processo_os.py:67` (`FASES`), `:942` (`_kanban`); PRD:2972-2988 |
| O.S. · Calendário | Início e Fim em ISO. Toda O.S. agrícola do cenário tem janela, e a "Nova ordem" pede o início (`nv_jan`, `areas/processo_os.py:892,1149`). A OS-0422, a única sem janela, é de água e mora na IR-03 desde 01/10 (`areas/processo_os.py:173`; `os_irrig_filtro_test.py`) | `dados.py:116-119` (`_JAN`); colunas `t='date'` em `areas/processo_os.py:1221` |
| O.S. · Carga | Recurso (máquina, implemento, pessoa) × dia e hora | `alocacao.py:6,10,17` (`DIAS`, `RECURSOS`, `ALOC`); aba Recursos em `areas/processo_os.py:1158`; DEC-2609-09 (PRD:12477) |
| BEN · Kanban | Fase com 5 etapas | `ben.js:21` (`BEN_FASES`); seletor atual em `areas/processo_beneficiamento.py:22-28` |
| Manutenção · Kanban | Fase com 5 etapas | `dados_manutencao.py:268` (`MAN_FASES`); seletor atual em `sp-comp:areas/maquinas.py:296-297` |
| Manutenção · Calendário (⏸) | Janela em ISO (`janIso`). A rotina "Esta semana" já é a agenda por dia, com HH por especialidade | `sp-comp:dados_manutencao.py:228-262`; `sp-comp:areas/maquinas.py:294-300` |
| Vistoria · Mapa | Lat/lon do talhão (nível do talhão; o ponto não tem coordenada gravada). Ganho sobre a camada MIP do IN-04: o recorte da lista (alvo, situação) | `dados_mip.py:99-104`; camada MIP do IN-04 em `areas/inicio.py:99,108`; cor e próximo passo por `mipSit`/`mipProx` (`mip.js:105-140`), os mesmos do IN-04 |
| Talhão · Mapa | Geometria: T1 com polígono validado, os outros em desenho; Lagoa Grande em círculo do KML | `areas/inicio.py:93` e `areas/cad_fazendas.py:206` (duas cópias divergentes); `dados.py:126`; `dados_lagoa_sintetico/kml.py:1-31`; seletor atual em `areas/cad_fazendas.py:259,263` |
| Cultivo · Timeline | Plantio → "Ocupa até", com o fim estimado marcado | `dados2.py:65-86`; `areas/processo_safra.py:42-44`; `ocupacao.py` |
| Máquina · Carga | Máquina e implemento × dia, no mesmo quadro da O.S. | `alocacao.py:10,17`; PRD:7487 (quadro único, sem agenda paralela) |
| Pedido · Calendário (⏸) | Previsão de entrega, já reprogramável no formulário com motivo. A SUP põe a mesma Previsão na lista do Estoque | `areas/processo_compras.py:105-107`; `dados2.py:847`; `sp-sup:areas/processo_estoque.py:109` |
| Atividade · Calendário e Matriz (⏸) | Data projetada pelo gatilho (DAP/DATA) e ha-operação por talhão. A matriz recurso × mês já existe como grade própria | `areas/processo_safra.py:180-194`; `dados2.py:125,903`; PRD:6772, 7338, 10616 |

### 1.3 Só Lista (sem seletor: uma visão só)

| Entidade | Tela / grade | Por que não ganha outra visão |
|---|---|---|
| Safra | SAF etapa 1 · `g_saf` (`areas/processo_safra.py:32`) | São 3 safras na Santa Rita, com a Safrinha dentro da 2026/27 (`dados2.py:14-17`). A Timeline não decide nada. Os estados não têm fluxo (`:15-17`) |
| Estoque · saldos | EST etapa 4 · `g_lot` (`areas/processo_estoque.py:116-120`) | A Lista já é árvore item › lote, com subtotal na unidade do item. Agrupar por grupo ou local mistura kg e L (`dados2.py:861-869`). Rever depois da SUP, que reescreve a tela |
| Requisição | EST · `g_ent`/`g_dev` (`areas/processo_estoque.py:98,106`) | Agrupar por O.S. mistura unidades; só daria contagem |
| Colaborador | CD-04 · `g_pes` (`areas/cad_ativos_pessoas.py:301`) | Por equipe, só contagem; custo por hora não se soma. A carga das pessoas é a da O.S. |
| Colheita por talhão | COLH · `g_tal` (`areas/producao.py:493`) | Já é árvore cultura › talhão. Talhão × semana tem pouco dado (`dados_producao.py:111-115`) |
| Carga recebida | CARGA · `g_cg` (`areas/producao.py:363`) | 2 estados; registro do dia, sem decisão de agenda |
| Estoque de produto | PROD · `g_lot` (`areas/producao.py:244`) | Já é árvore produto › lote. A qualidade é decisão com laudo, não fluxo (`producao.js:193-204`) |
| Ordem de irrigação | IR-03 · `g_os` (`areas/irrigacao.py:295`) | 4 linhas (3 de água + a fertirrigação, só leitura), já ordenadas por etapa e com filtro rápido de Etapa (`:296-297`, `rk`). A decisão da água é de horário e bomba, que é a IR-02. Um Kanban de 4 cartões em 5 colunas não decide nada |
| Agenda por captação | IR-02 · `g_ag` (`areas/irrigacao.py:213`) | Já é a agenda por recurso (captação › ordem, com janela sugerida por `irrSugerir` e conflito escrito). Uma Carga gráfica repetiria |
| Setor de irrigação | IR-01 · `g_set` (`areas/irrigacao.py:151`) | O mapa desta lista já existe: camada Irrigação do IN-04 ("Hoje · Balanço hídrico", `areas/inicio.py:111`). A decisão é pelo déficit, que a Lista ordena |
| Pedido de venda | PROD · `g_ped` (`areas/producao.py:246`) | Janela em texto ("Tipo · janela"); a frente COM reescreve |
| Cadastros CD-02, CD-05, CD-06, CD-07, PA; AG-07; IR-04; CF-05; MA › Sem ordem e Planos | as grades de cada tela | Lista ou árvore única; nenhum atributo sustenta segunda visão. "Sem ordem" já tem o horizonte Vencidas · 10 d · 30 d (PCM D-28) |

### 1.4 Cortes e mudanças na sugestão do proprietário

| Entidade · visão sugerida | Decisão | Motivo e fonte |
|---|---|---|
| Talhão · Árvore "fazenda › setor › talhão" | Corta | O setor é a bomba ou o sistema de irrigação: atributo opcional, não nível (`dados_cad.py:21-22`; PRD:7258). Como pai, deixaria órfão o talhão de sequeiro. A Lista já é árvore fazenda › talhão com subtotal (`areas/cad_fazendas.py:258`), e a parcela por safra fica no detalhe CD-01det (`:507`) |
| Safra · Timeline | Corta | Ver 1.3. A linha do tempo útil é a da ocupação dos cultivos, que entra como linha própria (Cultivo) |
| O.S. · Mapa | Fica no IN-04 (rev. Codex 01) | Tarefa já atendida: DEC-2609-06 e DEC-2609-09 (PRD:9516, 12474, 12477) puseram o mapa das ordens no IN-04 e deram à O.S. "Recursos" no lugar de "Mapa". Não reabre sem pedido do proprietário. Se ele pedir, a visão reusa a função "Ordens de serviço" do IN-04 (PRD:3002-3010), leva a Safra (o Mapa só filtra Fazenda, PRD:12479) e mostra contagem quando há várias ordens por talhão (PRD:3008) |
| O.S. · Tabela agrupada | Acrescenta | Já existe ("Agrupar por talhão"); vira a visão |
| Atividade/Aplicação · Lista, Calendário, Matriz, Mapa | Lista ✓ (existe); Calendário ⏸ (apto depois da integração SAF); Matriz e Mapa ✗ por ora | **Decisão de produto do Codex (rev. Codex 01):** a Atividade planejada mora em Planejar safra, na etapa consolidada de operações e recursos, como ocorrência ligada a safra, cultivo, talhão ou parcela e versão do plano; `g_op` (`areas/processo_safra.py:180`) é a entrada canônica, sem menu "Atividades", cadastro ou tela paralela. O detalhe mostra gatilho e data projetada (ou a pendência da âncora), área, quantidade e unidade, recursos, custo, vínculo e saldo da O.S.; o próximo verbo segue o estado (completar ou revisar a programação, gerar ordem quando elegível, abrir a ordem existente), e gerar O.S. não duplica demanda nem libera execução: vincula e aloca o saldo planejado ainda não convertido, sem representar consumo físico nem realizado, que dependem dos comandos próprios. O realizado vem dos apontamentos da O.S. (PRD 44.1). O Calendário entra depois da etapa consolidada como outra leitura das **mesmas** ocorrências, com projeção ou intervalo e "Aguardando marco" visíveis, só leitura, sem inventar data sem âncora (PRD 39.4). A Matriz talhão × semana só entra se responder uma comparação que a Lista e o Calendário não resolvem, com quantidade distribuída sem duplicação; a matriz de capacidade recurso × mês (`g_cap`) continua no contexto de recursos. Mapa: seria o da O.S., segunda fonte (PRD:2856) |
| Insumo/Estoque · Tabela agrupada | Corta como visão | Ver 1.3 |
| Máquina · Mapa | Corta | O local é texto, sem coordenada (`dados_cad.py:63-64`); PRD:7505 proíbe inventar posição |
| Vistoria/Ocorrência · Galeria | Corta | Não há imagem: a vistoria só conta fotos (`areas/agronomia.py:865`), os cartões são marcadores (`:914`) e no app a foto é simulada (`areas/mobile.py:599-624`). A decisão vem da contagem contra o nível de controle |
| Ocorrência · Lista e Mapa | Fora | Sem listagem no menu (CA-03 oculto, `areas/campo.py:467`) e local em texto livre (`:457`). Na fatia 3 a Vistoria entra no lugar dela |
| Vistoria · Calendário | Corta (revisão crítica) | A data dominante é a da coleta, que é fato. Agenda real só há na VIS-017 (programada); as "previstas" são cálculo (`mipPrevista`, `mip.js:59`) e já aparecem na Lista como situação **Vistoria atrasada · prevista para…**, com chip de filtro (`mip.js:118-122`; `areas/agronomia.py:615,833`). O atributo dominante é contagem × NC por talhão: Lista + Mapa |
| Lançamento de custo · Lista, Agrupada, Árvore | Fora agora | Sem listagem no menu (GE-03 oculto, `areas/gestao.py:291`). As dimensões estão numa coluna de texto (`:272-281`), e o centro de resultado é plano (`dados_cad.py:186-189`). Quando existir: Lista + Agrupada em R$, com a Natureza em 2 níveis como agrupamento hierárquico (não uma Árvore separada) e "Não alocado" visível (PRD:8363) |
| (fora da sugestão) BEN, Manutenção, Cultivo | Acrescenta | Ver 1.1 e 1.2. Só migram seletores que já existem (BEN, Manutenção) ou trocam o "Ocupa até" em barra (Cultivo) |
| O.S. · Timeline | Corta | Sustentada por início e fim, mas repete o Calendário e a Carga (uma solução por problema, AGENTS §3.4) |
| Irrigação IR-03 · Kanban, Carga, Calendário, Timeline | Corta (revisão crítica) | Ver 1.3. Kanban: 4 ordens, a Lista já ordena e filtra por etapa. Carga por bomba: é a IR-02 "Agenda por captação". Calendário e Timeline: a janela da IR-03 é texto (`areas/irrigacao.py:294`) |
| Setor IR-01 · Mapa | Corta (revisão crítica) | Duplica a camada Irrigação do IN-04 sem filtro próprio da lista que mude a resposta (1.3) |
| Manutenção · Calendário | ⏸ (revisão crítica) | A rotina "Esta semana" da PCM já é a agenda por dia (`sp-comp:areas/maquinas.py:294-300`), recém-revisada pelo autor da PCM. Entra como visão só se o autor da PCM aceitar trocar a rotina por ela; as duas juntas seriam dois caminhos |
| Manutenção · Carga | Corta | As horas por especialidade já aparecem no dia da "Esta semana"; um quadro a mais repetiria |
| Pedido de compra · Calendário | ⏸ (revisão crítica) | A SUP leva a mesma Previsão para a lista do Estoque. O Calendário de entregas entra numa das duas listas, nunca nas duas, e só depois da SUP |

### 1.5 O que o seletor não absorve

- **Abas de entidade:** `cadastros.abas`, em `areas/cadastros.py:128` (Talhões | Fazendas | Ambiental | Água).
- **Visões-pergunta da PCM:** `#vis=` Sem ordem · Ordens · Ativos · Planos (`sp-comp:areas/maquinas.py:14,34`). Também "Ativos | Abastecimentos", que troca de entidade.
- **COLH "Por talhão | Por semana"** (`areas/producao.py:502-503`): são blocos e perguntas diferentes, não a mesma linha vista de outro jeito.
- **Horizonte e período:** PL-04 "Hoje · 7 · 14 dias" (`areas/planejamento.py:429`) e "4 semanas | Safra" (`areas/producao.py:497`) são filtros.
- **Agrupar sem subtotal:** o `<select>` "Agrupar" do AG-01 (Talhão, Alvo, Situação, Fazenda; `areas/agronomia.py:827-829`) continua estado da Lista. Sem valor somável, não é "Tabela agrupada" pela regra do pedido.
- **Rotinas e entidade dentro da PCM:** "Aguardam você · Esta semana · Com conflito" são filtros-pergunta; "Ativos | Abastecimentos" (`#…&modo=abastecimentos`) troca de entidade.
- **Telas ocultas** (SU-05, CA-01, VE-*): não migram.
- **Nunca viram visão:**
  - Kanban por selo, de lote ou de integração (PRD:2984; INTEG-27);
  - Calendário editável de fatos;
  - Mapa de Estoque ou de Custo.

---

## 2. Desenho do ViewSwitcher no protótipo

### 2.1 Onde mora (uma peça por camada)

| Camada | Arquivo | O que entra |
|---|---|---|
| Regra | `visoes.py` (novo) | `ORDEM` fixa (`lista, agrupada, kanban, calendario, timeline, mapa, carga, matriz, arvore, galeria`), `NOME`, `ICONE`, `EXIGE` (atributos por visão) e o registro por entidade (visões ativas com atributo e fonte; cortes com motivo). `validas(ent)` é a fonte única para o build e os testes. O JS não recalcula: recebe a lista pronta |
| Componente | `engine.py` | Ícones `v_*` (2.2); `visoes(gid, ent, paineis, rotulo)`, que devolve barra e painéis; CSS `.g2visoes` no `G2_CSS` |
| Comportamento | `g2lib.js` | Funções puras `g2visaoInicial`, `g2visaoUrl`, `g2visaoTecla`, `g2visaoChave`, `g2visoesCelular`; `g2visao(self,gid)` e `g2visaoIr(self,gid,k,origem)`; ligação no `g2vals` |
| Telas | `areas/*.py` | Cada tela passa os painéis. Fatia 1 só na `processo_os.py` |

Permanecem: `ui37.tabs` (`ui37.py:476-488`) e `engine.seg` (`engine.py:176-178`) para o que não é visão. Os seletores antigos migram por fatia: O.S. (F1), BEN (F2), PCM `om_modos` (F2b), CD-01 `cdv` e o botão "mostrar mapa" `cd_mtog` da CADUX (F3). Cada migração **remove** o controle antigo no mesmo commit: nunca dois caminhos para a mesma visão.

Os nomes evitam colisão: a DS já tem `g2vis()` (`sp-ds:g2lib.js:445`) e a PCM usa `#vis=`. Por isso o prefixo é `g2visao*`, a classe é `.g2visoes`, o atributo é `data-visao` e a chave de estado é `visao`.

### 2.2 API, ícones e rótulos

```python
barra, corpo = visoes('g_os', 'os', {
    'lista':    g_os,                    # a mesma grade serve Lista e Tabela agrupada
    'agrupada': 'lista',                 # mesmo painel; o agrupamento é estado da grade
    'kanban':   kb_nota + _kanban(),
    'carga':    rc_nota + _recursos_tab(),
}, rotulo='Visão das ordens')            # rótulo mantido: os testes o usam
```

**Regras de build** (falha o build quando quebradas):
- as chaves de `paineis` são iguais a `visoes.validas('os')`;
- visão sem atributo declarado com fonte é recusada;
- com uma visão só, devolve `('', painel)`: sem seletor.

**HTML gerado:**
- `role="toolbar"` com `aria-label` do rótulo e `data-visoes="lista agrupada kanban carga"`. Com foco itinerante e setas, o papel certo é barra de ferramentas (WAI-ARIA APG): o leitor de tela anuncia que as setas funcionam. Os testes usam o `aria-label`, não o papel (`acao_unica_test.py:182-186,380`; `os_irrig_filtro_test.py:98`; `ben_fluxo_test.py:161`);
- um `button` por visão: `data-visao`, `data-i`, `aria-label="Ver em <nome>"`, `aria-pressed`, `tabIndex` itinerante, `icon('v_…')` com `aria-hidden`;
- sem texto visível e sem `title` (a dica vem da DS).

| k | Rótulo | Ícone Lucide 1.45.0 → chave | Fatia em que entra |
|---|---|---|---|
| lista | Ver em lista | List → `v_lista` | F1 |
| agrupada | Ver em tabela agrupada | Rows3 → `v_agrupada` | F1 |
| kanban | Ver em kanban | SquareKanban → `v_kanban` | F1 |
| carga | Ver em carga por recurso | Users → `v_carga` | F1 |
| (mais) | Mais visões | Ellipsis → `v_mais` | F1 |
| calendario | Ver em calendário | CalendarDays → `v_calendario` | F2 |
| mapa | Ver em mapa | Map → `v_mapa` | F3 |
| timeline | Ver em linha do tempo | ChartGantt → `v_timeline` | F4 |

- **Os caminhos já convertidos** estão em `descoberta-infra.md` §1. Só entra o ícone que alguma tela usa.
- **Licença:** `LICENSES/lucide-ISC.txt` com o aviso ISC e o MIT do Feather, que também cobre os ícones atuais de `engine.ICONS` (hoje sem atribuição).
- **Traço e tamanho:** o traço fica o de `icon()` (1,8). Tamanho de 16 px no computador e 20 px no toque (CORR-DS-33).
- **"Recursos" passa a "Carga por recurso"** só no rótulo, como pede o pedido de 10/10. A decisão DEC-2609-09 continua.

**Desenho:**
- trilho e raio da DS-36;
- 32 × 32 px no computador e 44 × 44 em `@media (pointer:coarse), (max-width:640px)`, no padrão de `engine.py:1084`. Só `pointer:coarse` deixaria 32 px num celular emulado sem toque ou numa janela estreita com mouse;
- inativo: ícone em `MUTED` (PRD 74.5.10 mede 5,25:1 sobre o trilho);
- **ativo tonal:** fundo `#E4F3E9`, ícone `#1E6B47`, borda e barra interna inferior de 2 px (`box-shadow: inset 0 -2px 0 #1E7A4C`, o mesmo da etapa atual em `g2lib.js:371`), mais `aria-pressed="true"`. O destaque não depende só de cor, e não é verde cheio (BOT-01; caso 29 em `acao_unica_test.py:375-384`);
- hover verde-claro da DS (VIS-02) e anel de foco visível.

**Lugar:** na barra da coleção, à direita, depois dos filtros que valem para todas as visões, fora do painel da Lista. Na O.S. já é assim (`areas/processo_os.py:1233-1234`). Filtro que vale para todas as visões não pode morar dentro do painel da Lista: na migração do BEN, os chips de fase saem da barra da grade.

### 2.3 Estado compartilhado (sem duplicar)

- **A visão** fica em `self.state.g2[gid].visao`, ao lado de `f`, `q`, `so`, `qv` e `sel` (`g2lib.js:12-14`). O `st.sel[segId]` do motor antigo (`engine.py:208-214`) sai da O.S.
- **Agrupada = Lista com agrupamento ligado.** Na O.S., o `self.state.os_agr` (`areas/processo_os.py:559,767-769`) passa a ler `g2visao(self,'g_os')==='agrupada'`.
  - O botão "Agrupar por talhão" (`:968`) sai: um caminho só.
  - A regra TF06 não muda: a O.S. aparece em cada talhão vinculado, o grupo conta O.S. distintas e o total conta cada uma uma vez.
  - A chave de agrupamento só vira estado (`agr`) quando alguma entidade oferecer mais de uma.
- **Mesmas linhas:** o Kanban e a Carga já leem o filtro da grade (`areas/processo_os.py:794-807`). Na fatia 2 entra `g2visiveis(self,gid,base)`: IDs das folhas filtrados, buscados e ordenados, consumidos pelo Kanban, Calendário, Carga e Mapa. Com isso o Kanban passa a respeitar a ordenação.
- **Mesmo detalhe:** toda visão abre o mesmo painel pela mesma função (O.S.: `pan`, `areas/processo_os.py:764-765`). Seleção e item aberto são estado comum.
- **Persistência:** os filtros pelo `g2keep` (sessão; a O.S. já usa, `:535`); a visão pela URL; a preferência no `localStorage`; a rolagem por visão no `sessionStorage` (2.11).
  - **Filtros do topo também:** o `g2keep` hoje guarda só `f,q,so,qv` e não `mf_faz`/`mf_saf` (`g2lib.js:15-19`; `engine.py:1433-1435`). Na volta, a Fazenda e a Safra voltam a "Santa Rita/Todas" e um `f.tal` de outra fazenda pode esvaziar a lista com "filtro ativo". A F1 estende o `g2keep` da tela com a visão para os filtros do topo (mesma chave por `pathname`), e o E3 cobre isso.
- **Vazio por regra da visão** (não é vazio de filtro): fase "Canceladas" nos chips (`areas/processo_os.py:791`) + Kanban dá 5 colunas vazias, porque Canceladas fica fora do quadro (PRD:2984). A visão diz o motivo e oferece **Ver em lista** (2.8).

### 2.4 URL e preferência

- **Formato:** `OS.dc.html?view=agrupada#OS-0420`.
  - Valores ASCII sem acento: `lista, agrupada, kanban, calendario, timeline, mapa, carga, matriz, arvore, galeria`.
  - **Toda escolha explícita grava `?view=<k>`, inclusive `lista`** (rev. Codex 01, achado 1). O fallback "Ver em lista" também grava `?view=lista`, sem mudar a preferência. Assim, com preferência Kanban, escolher Lista e dar F5 continua na Lista. A ausência do parâmetro significa "preferência" só na entrada sem escolha.
  - Grava com `history.replaceState(history.state,'',pathname+'?'+params+location.hash)`, nunca `pushState`: o Voltar sai da tela, não percorre visões.
  - Lê por `URLSearchParams(location.search)` e preserva os outros parâmetros: o runtime já lê `?theme=` (`support.js`, `URLSearchParams(location.search).get("theme")`).
  - O hash não muda. Endereços vivos que a visão não pode quebrar, conferidos no código: O.S. `#OS-0420`, `#OS-0430:ajustar`, `#tal=Faz|T1`, `#nova:c:a:AAAA-MM-DD` (`areas/processo_os.py:751-763`, regex ancorada); SAF `#saf=S2627&passo=cultivos&cult=c5` (`safra.js:1276-1325`; `ocupacao_test.py:19`); CMP `#sol=…&saf=…` (`areas/processo_compras.py:198`); PCM `MA.dc.html#vis=ordens&modo=kanban&om=OM-0233` (`sp-comp:areas/maquinas.py:14,81-96`); AG-01 `#VIS-012[:decidir|programar]`; CD-01 `#talhao=ID&aba=…`; IN-04 `#car`, `#car:T1`, `#desenhar=ID`, `#importar`; GE `[?&#]caso=`; NAV1 `PA.dc.html#plano=ID`. O `g2keep` usa só o `pathname` (`g2lib.js:17`).
  - **Regra para toda tela com seletor:** toda escrita de URL preserva `location.search`. Hoje todas preservam, salvo `history.replaceState(null,'',location.pathname)` em `areas/irrigacao.py:161,262,283`, que apaga query e hash. A IR não ganha visão nesta frente; se ganhar, isso é corrigido antes. A varredura ganha uma checagem estática dessa regra nas telas com `data-visoes`.
- **Precedência** (`g2visaoInicial(search, pref, validas)`, pura): URL válida › preferência válida › `lista`.
  - Valor fora das válidas, ou que não casa com `^[a-z]+$`: segue a precedência e mostra um aviso uma vez (`role="status"`), sem repetir o valor cru: "A visão pedida no endereço não existe nesta lista: aberta em Kanban (sua última escolha)."
  - A URL é reescrita para a visão aberta, para o F5 não repetir o aviso.
  - Resolve a divergência entre os relatórios: segue a precedência como pede o pedido, e não escolhe em silêncio (SEL-02).
- **Preferência:** `localStorage['safrion.pref.visao:<perfil>:<entidade>']`.
  - "Usuário" no protótipo é o perfil de demonstração (`g2perfil()`, `g2lib.js:263-265`).
  - Leitura e escrita em try/catch, com cópia em memória.
  - Grava só quando a pessoa escolhe no seletor; abrir por URL não grava.
  - Trocar de perfil não muda a visão aberta; vale na próxima entrada sem `?view`.
  - "Restaurar demonstração" (`cenReset`, `cenario.js:12`) não apaga.
  - O prefixo `safrion.pref.` permite ao `negocio()` do TF02 ignorar a chave (`tabelas_os_test.py:44,52,105`).
- **PCM:** `#…&modo=kanban` vira sinônimo de `?view=kanban` na migração da Manutenção (F2b). O `#vis=` continua sendo a visão-pergunta da PCM.
  - Só `modo=kanban` migra; `modo=abastecimentos` troca de entidade e fica como está.
  - Uma fonte só: o `ma_hashDe` (`sp-comp:areas/maquinas.py:84`) deixa de gravar `modo=kanban`. Na leitura, `modo=kanban` vale só sem `?view`; a URL é reescrita para `?view=kanban`, mantendo `vis=` e `om=`.
  - Teste: `MA.dc.html#vis=ordens&modo=kanban&om=OM-0233` abre o Kanban **e** a OM-0233; `?view=lista#vis=ordens&modo=kanban` abre a Lista (a query vence).

### 2.5 Teclado

- **Foco itinerante:** a barra tem uma parada de Tab. A visão ativa tem `tabIndex=0` e as outras `-1`; botões ocultos no celular são pulados.
- **Setas:** ← → movem o foco com volta; Home e End vão às pontas. **Seta não ativa.** ↑ e ↓ não movem o foco na barra horizontal: no "mais", ↓ abre o menu (sem isso, a mesma tecla teria dois efeitos).
- **Ativar:** Enter e Espaço (nativos do `button`). Depois do redesenho, o foco volta ao botão ativado (por `data-visao`).
- **Sem atalhos 1…9.** O projeto não tem atalho de dígito (`g2lib.js:58-76,293-300`; `apps/web` também não), e o pedido só os quer onde já existem.
- **"Mais":**
  - Enter, Espaço ou ↓ abrem o menu;
  - as setas percorrem os itens;
  - Esc fecha e devolve o foco ao "mais", com `preventDefault` e `stopPropagation`, para não acionar o Esc global (`g2lib.js:293-300`).

### 2.6 Dica no foco

- **Reaproveita o `g2dica` da DS** (`sp-ds:g2lib.js:526-630`). Um botão só com ícone e `aria-label` já ganha a dica com o nome, sem atributo a mais (`:539-544`):
  - hover de 300 ms;
  - foco de teclado na hora;
  - toque longo de 500 ms;
  - Esc fecha sem tirar o foco;
  - `aria-describedby` só quando o texto difere do nome, então sem leitura dupla.
- **Não usar texto escondido.** O `g2dica` decide que o botão é "só ícone" pelo texto visível (`sp-ds:g2lib.js:543`); com `sr-only`, a dica deixa de abrir.
- **Dependência:** a fatia 1 é desenvolvida numa worktree de rascunho com a DS mesclada localmente e só integra depois da DS.
  - Só se o proprietário pedir antes, entra uma dica mínima com o mesmo `id="g2-dica"` e `role="tooltip"` (hover e foco, Esc), marcada "remover no merge da DS".
  - Os testes sondam `#g2-dica` e não mudam.

### 2.7 Celular

- **Até 640 px** (o corte de celular já usado em `engine.py:1061-1064`): as 3 primeiras visões pela `ORDEM` mais "mais" (Ellipsis). Os botões de índice 3 em diante ficam ocultos por CSS (`data-i`), e as posições não mudam.
- **O menu do "mais"** (`role="menu"`, itens `menuitemradio` com `aria-checked`) mostra ícone **e nome em texto**: no toque não há hover, e a VIS-04 pede o texto. Os itens usam `data-visao-menu`, para o auxiliar de teste não achar dois alvos.
- **Visão ativa dentro do "mais":** o botão "mais" recebe a marca de ativo (tonal + barra) e `aria-label="Mais visões (atual: carga por recurso)"`.
- **Alvos de toque:** 44 × 44 px. Hoje o seletor tem cerca de 29 px de altura (`engine.py:141-142`).
- **O.S. a 390 px:** Lista, Agrupada e Kanban na barra; Carga no "mais". Depois da F2, também o Calendário.

### 2.8 Estados em toda visão

Um contrato comum, `g2visaoEstado(self,gid,k)` → `{tipo, texto, acao}`, desenhado no topo de cada painel com `role="status"`.

| Estado | Quando | Texto e ação nomeada |
|---|---|---|
| Vazio de contexto | Fazenda ou Safra sem nenhum registro | **Não muda:** sem seletor, uma frase e uma ação (`areas/processo_os.py:1236-1240`). O passo 9 de `os_irrig_filtro_test.py:98` exige isso |
| Vazio de filtro | O recorte zerou | "Nenhuma ordem no filtro: fase Liberadas · talhão T4." + **Limpar filtros** (o mesmo `os_limpar`), igual em toda visão |
| Vazio por regra da visão | O recorte só tem itens que a visão não mostra por regra (ex.: fase Canceladas no Kanban, PRD:2984) | "Canceladas ficam fora do quadro: 2 ordens no filtro." + **Ver em lista** (troca sem gravar a preferência). Nunca 5 colunas "Nenhuma ordem nesta fase" sem motivo |
| Parcial | Itens sem o atributo da visão | Faixa própria, mostrada quando n > 0: **Sem data (n)** no Calendário, **Sem localização (n)** no Mapa (OB-0104, do armazém), **Sem alocação (n)** na Carga. O item abre o mesmo detalhe. Na O.S. não há caso de "Sem data" no cenário (toda O.S. agrícola tem janela; a OS-0422 é de água, 1.2): a faixa é provada na unidade com uma ordem sintética sem janela |
| Erro da visão | O desenho da visão falhou (ex.: exceção no render do Calendário) | "Não foi possível mostrar o calendário: <motivo>." + **Ver em lista** (grava `?view=lista`, sem mudar a preferência); a Lista é provada funcional nesse caso. Registro sem geometria **não** é erro: vai para **Sem localização (n)** (rev. Codex 01, achado 5) |
| Cenário ilegível | O estado salvo não pode ser lido (afeta também a Lista) | Recuperação sem apagar dados: frase com o motivo e a ação de recuperação já existente da tela; nunca "Ver em lista" para uma Lista que também falharia, nunca limpar o `localStorage` em silêncio (rev. Codex 01, achado 5) |
| Carregando | Dado assíncrono | O protótipo não chega a esse estado: os dados vêm embutidos e as visões não usam rede (o MapLibre fica fora da listagem). O contrato vale para o software real (`aria-busy`, esqueleto) e é testado lá. Declarado, não fingido |

### 2.9 Ação primária: única e fixa

- **A primária é a que a tela já tem.** Na O.S., hoje "Nova ordem", no bloco "Ordens por fase". O rótulo e o lugar mudam pela frente de botões (BOT-02/03 pedem "Criar ordem" no cabeçalho), não por esta.
- **É a mesma em todas as visões.** O seletor nunca é verde cheio.
- **Ações próprias de uma visão são secundárias mini:** Limpar filtros, semana ‹ ›, Sem data.
- **Teste:** `prims == [primária]` e 0 duplicata em cada visão, a 1440 e a 390 px (casos 15 e 27 do `acao_unica_test.py` e `acoes_duplicadas.py`).

### 2.10 Arrastar

| Onde | Protótipo (fatias 1–5) | Motivo | Software real (transferência) |
|---|---|---|---|
| Kanban (O.S., BEN, Manutenção) | **Proibido.** Teste de ausência `[draggable=true] = 0`; a mudança de fase continua pelos botões do painel | `osc_liberar` grava aprovação e liberação juntas (CMD-42 + CMD-06, `areas/processo_os.py:327-343`), e APROV-05 proíbe aprovar por arraste (PRD:13421). Iniciar e concluir são fatos do executor (PRD:2869, 2875-2877). Não há desfazer de fase: a reserva não volta (PRD:2845, 7516). Errar seria S1 (liberar sem aprovação) ou S2 (reserva indevida) | **Também sem arraste.** O pedido só admite arrastar "com desfazer", e nenhuma transição tem desfazer legítimo: CMD-06 cria reserva que pode não voltar, CMD-10 fecha a edição e grava a outbox. Trocar o desfazer por confirmação (o que o PRD:2996 permitiria) muda a condição do proprietário: só ele decide. Se decidir, o drop só **inicia** CMD-06 sobre versão já aprovada em CMD-42 separado, ou CMD-10, com confirmação no contexto (DS-44); os demais pares, saltos e voltas recusam com motivo e quem resolve |
| Calendário | **Só leitura.** "Programar" continua no detalhe | Não há validador único de janela: a janela é texto livre (`areas/planejamento.py:411`, `areas/campo.py:189`). APROV-11 (PRD:13442) exige revalidar dentro e fora da janela técnica. Arrastar sem isso seria S2 | Depois do serviço único (proposta JANELA-01, tarefa do Codex), e **só para O.S. em A liberar dentro da janela técnica** (antes da liberação não há reserva, então o desfazer é limpo): o drop **abre o mesmo formulário** com a data nova preenchida e nunca grava sozinho. "Desfazer" no aviso = o mesmo comando com a data anterior, como fato de compensação e chave de idempotência nova (padrão `assinDesfazer`, `assinatura.js:159-169`). Liberadas, Em execução e o resto: **sem arraste** (mudar a data pode tirar a liberação e soltar a reserva, sem volta, PRD:2954, 7516); reprogramar pelo detalhe. Sempre há alternativa sem arrastar (WCAG 2.5.7; PRD:15021) |
| Carga por recurso | **Só leitura** | Não há validador de realocação; publicar alocação é CMD-34 com simulação (PRD:2825) | Simular e publicar, sem mover a agenda na simulação |

### 2.11 Rolagem e volta

- **Antes de trocar de visão:** guardar `{main[data-scroll].scrollTop, .g2rola scrollTop/scrollLeft}` da visão atual.
- **Depois do desenho:** restaurar a da nova visão no `setTimeout`, como faz `g2etapa` (`g2lib.js:382-387`). Hoje o `sc-if` desmonta a visão oculta e a rolagem se perde.
- **Entre páginas:** `sessionStorage['g2rol:<arquivo>:<gid>:<k>']`. O Voltar **nativo** do navegador (`performance.getEntriesByType('navigation')[0].type === 'back_forward'`) restaura como hoje, no padrão da NAV1 (`sp-nav:areas/processo_planos.py:129-131,452-453`). O "Voltar" **da aplicação** é navegação comum (`navigate`) e restaura só mediante o contexto de retorno validado abaixo; entrada comum sem esse contexto não restaura estado antigo (rev. Codex 02).
- **Na O.S.**, o painel é modal sobre a lista montada, então visão, filtros e rolagem já ficam. A página de detalhe aberta pelo link do painel (`ostest.py:60`, CA-01det) é o caso que exige URL, `g2keep` e rolagem.
- **A volta da persona é o link "Voltar"/trilha, não o botão do navegador.** **Regra (rev. Codex 01 e 02):** o "Voltar" da aplicação **sempre navega ao destino canônico da lista** (arquivo da lista com `?view`), nunca chama `history.back()` e não tenta inferir a entrada anterior: `sessionStorage` pode ser copiado para uma aba aberta com opener, e no link direto ou `noopener` o contexto nem existe. Ao abrir o detalhe, a lista grava no `sessionStorage` um contexto de retorno (arquivo, entidade, perfil, Fazenda e Safra, `?view`, filtros do `g2keep`, rolagem e id do item para o foco). Na lista de destino, o contexto só é aplicado se for válido: mesma origem, mesmo arquivo e entidade, mesmo perfil e mesmo escopo de Fazenda e Safra. Sem contexto válido (ausente, antigo, de outro perfil ou safra), a lista abre canônica, no escopo autorizado, com foco inicial coerente, sem prometer filtros ou posição que não existem. O Voltar nativo continua com a restauração `back_forward`. O E3 cobre esses casos.

---

## 3. Plano das 5 fatias

### Acordo curto da fatia 1 (AGENTS §3.4)

```text
ID / resultado útil / persona: VISOES-1 · trocar a O.S. entre Lista, Tabela agrupada, Kanban e Carga por recurso por ícone, sem perder filtro, e voltar onde estava · PCP (Caio) e gestora (Ana), no computador e no celular
Requisitos do PRD e fora do escopo: PRD 4.2/4.3, 297, 2972-2996, DS-36 (74.5.10), DS-57, SEL-02, BOT-01/BOT-09, VIS-02/VIS-04; pedido de 10/10. Fora: Calendário, Mapa, Timeline, arrastar, software real
Autor / revisor / integrador: Claude (autor) / Codex (revisão sem bloqueio, §3.5) / Claude junta na branch única do protótipo pelo regime leve §3.5. Não é aprovação nem integração de PR: no software real, PR é integrado pelo revisor (DEC-0910-02)
Base / arquivos: claude/prototipo-v44 depois da composição (int/comp) e da DS · visoes.py (novo), engine.py, g2lib.js, LICENSES/lucide-ISC.txt, areas/processo_os.py, comp_lib.py e os testes listados abaixo
Aceite e comando de verificação: "Pronto quando" da F1; bateria no fim desta seção (worktree de rascunho, trava cdpV)
Estado / impedimento / próximo passo: especificado · impedimento: composição e DS não integradas · próximo: revisão deste desenho pelo Codex
```

### F1 · VISOES-1: componente, estado, URL e preferência na O.S.

- **Tela:** OS. Visões: Lista e Agrupada (novas sob o componente); Kanban e Carga migram sem mudança de regra.
- **Por que a O.S. e não outra entidade:**
  - a EST está em reescrita na SUP (20 commits, cerca de 980 linhas em `processo_estoque.py`), e a Lista dela já é a forma agrupada;
  - o Talhão está em reescrita na TABR e na CADUX;
  - o AG-01 não tem valor somável ("Contagem × NC" é razão, `areas/agronomia.py:826`);
  - o custo não tem listagem no menu.
- **Arquivos:**
  - `visoes.py`: novo; registro `os` = lista, agrupada, kanban, carga; cortes timeline e mapa com motivo.
  - `engine.py`: `v_lista`, `v_agrupada`, `v_kanban`, `v_carga`, `v_mais`; `visoes()`; CSS `.g2visoes`.
  - `LICENSES/lucide-ISC.txt`.
  - `g2lib.js`: funções puras de 2.4, 2.5 e 2.7; `g2visao`, `g2visaoIr`, rolagem; ligação no `g2vals`.
  - `areas/processo_os.py`:
    - `os_agr` passa a ler `g2visao` (`:559`, `:767-771`);
    - o botão "Agrupar por talhão" sai (`:968`), e a nota `os_gtot` fica sob a Agrupada (`:969`);
    - `tabs(...)` vira `visoes(...)` (`:1232-1234`).
  - `comp_lib.py`: auxiliar único `visao(k, grupo)` por `[data-visao]`.
- **Testes que mudam no mesmo commit** (hoje clicam pelo texto visível):
  - `ostest.py:65,78`;
  - `testes_pedido.py:163`;
  - `acao_unica_test.py:46,182-186,380`;
  - `tabelas_os_test.py:28,91-95`, mais `negocio()` ignorando `safrion.pref.` (`:44,52,105`);
  - `os_irrig_filtro_test.py:34,70,76,95,97`;
  - `os_v39_bloq_test.py:10-41`;
  - `os_v39_selo_agua_test.py:27,50`;
  - `os_cenario_test.py:127-129`;
  - `ds_test.py:166,227,299,336`, que chega com a DS;
  - fora da bateria, também ajustados: `osacoes.py`, `verif_os.py`, `ostela.py`.
- **Unidade** (`visoes_unit.js`, forma B: `new Function` sobre `g2lib.js`, como `sp-ds:ds_unit.js:5-10`; e `visoes_unit_test.py`, que roda também os casos Python):

| Caso | O que verifica |
|---|---|
| U1 | `?view=agrupada` válida vence a preferência `kanban` |
| U2 | `?view=mapa` fora das válidas cai para a preferência, com aviso e sem repetir o valor cru |
| U3–U4 | Preferência antiga ou inválida, ou nenhuma, abre `lista` |
| U5 | Lixo (`KANBAN`, `kanbán`, `<x>`) é inválido |
| U6 | `g2visaoUrl` preserva `#OS-0420`, `#tal=Santa Rita\|T1` e outros parâmetros; toda escolha grava `view` (inclusive `lista`); ida e volta sem perda (rev. Codex 01) |
| U7 | ← → com volta, Home e End; ↑ ↓ não movem (no "mais", ↓ abre o menu); Enter, Espaço e outras teclas devolvem nulo (seta não ativa) |
| U8 | Chave por perfil × entidade com o prefixo `safrion.pref.visao:`; storage que lança abre `lista` sem erro |
| U9 | Celular: até 3 visões, todas; 4 ou mais, 3 + "mais"; ativa no "mais" marcada; uma só, nada |
| P1 | `validas('os') == ['lista','agrupada','kanban','carga']`; cada visão com os atributos que `EXIGE` pede, com fonte; cada corte com motivo |
| P2 | Negativos: sem data, sem Calendário; sem início e fim, sem Timeline; sem geometria, sem Mapa; sem fluxo, sem Kanban; sem valor somável, sem Agrupada; sem pai e filho, sem Árvore; sem foto principal, sem Galeria; uma visão só, sem barra |
| P3 | Painel para visão não sustentada faz o build falhar |
| Mutantes | Precedência invertida, `aria-pressed` ausente, seta que ativa e Calendário aceito sem data: cada um tem de ficar vermelho |

- **Componente** (`visoes_test.py comp`, 1440 × 900, Chrome com hover real da DS):
  - C1: barra (`role="toolbar"`) "Visão das ordens" com 4 botões `data-visao`, `aria-label="Ver em …"`, sem texto visível, `svg` com `aria-hidden`.
  - C2: exatamente um `aria-pressed="true"`; o ativo tem barra ou borda de 2 px ou mais e fundo diferente de `rgb(30, 122, 76)`.
  - C3: `role="toolbar"`; Tab para uma vez na barra; ← → movem o foco sem mudar `aria-pressed` nem a visão; ↑ ↓ não movem; Enter e Espaço ativam; Home e End funcionam; o foco fica no botão depois do redesenho.
  - C4: o foco abre `#g2-dica` com "Ver em tabela agrupada"; Esc fecha sem tirar o foco; sem `aria-describedby` repetindo o nome; o hover de 300 ms também abre.
  - C5: uma primária e 0 duplicata em cada visão.
  - C6: controle negativo. Injetar um segundo `aria-pressed=true` ou tirar um `aria-label`: a verificação tem de acusar.
- **Celular** (`visoes_test.py celular`, 390 × 844, escala 2, toque):
  - M1: todo alvo com 44 × 44 px ou mais, com toque emulado **e** sem toque (janela de 390 px com mouse).
  - M2: Lista, Agrupada e Kanban na barra, mais o "mais" com "Carga por recurso" em texto. Esc fecha e devolve o foco. Com a Carga escolhida, o "mais" mostra a marca e o nome.
  - M3: `MEDE`/`resumo` vazio (`comp_lib.py:95-142`): nada cortado, sem rolagem lateral, primária alcançável.
  - M4: toque longo de 600 ms mostra a dica.
- **Ponta a ponta** (`visoes_test.py e2e`, em 1440 × 900 **e** 390 × 844):
  - E1: filtro (fase Em execução e talhão T1) → Agrupada, uma rodada por clique e outra por teclado. Chips e talhão iguais, subtotal só do recorte, `?view=agrupada`, hash intacto.
  - E2: abrir uma O.S. do grupo → painel → Esc → o foco volta à linha.
  - E3: Fazenda Lagoa Grande + filtro → link do painel para o detalhe (CA-01det) → volta pelo link "Voltar"/trilha da página **e**, noutra rodada, pelo Voltar nativo do navegador (`back_forward`); e ainda o detalhe aberto em **nova aba** (com e sem opener) e por **link direto**: chega à lista correta; contexto ausente, antigo, de outro perfil ou de outra safra cai na lista canônica funcional sem estado antigo (rev. Codex 01 e 02) → Agrupada, Fazenda, Safra, filtros (`g2keep`) e rolagem com ±4 px (`rolagem()`, `acao_unica_test.py:54`).
  - E3b: fase "Canceladas" → Kanban → frase com o motivo e **Ver em lista** (nunca 5 colunas vazias sem motivo); a preferência não muda.
  - E4: precedência na entrada:
    - sem `?view` abre a preferência;
    - `?view=lista` vence a preferência;
    - `?view=xyz` abre a preferência com aviso;
    - trocar o perfil **não** muda a visão aberta; a preferência do outro perfil vale na próxima entrada sem `?view`, preservando rascunho e permissões (rev. Codex 01, achado 4);
    - preferência Kanban → escolher Lista → F5 → continua na Lista, com `?view=lista` (rev. Codex 01, achado 1);
    - `localStorage` limpo abre a Lista.
  - E5: trocar de visão não muda `localStorage['talhao-os-cenario-v1']`, byte a byte.
  - E6: entrada por `OS.dc.html?view=kanban#OS-0418` continua abrindo a ordem; `OS.dc.html#OS-0430:ajustar` e `?theme=dark&view=agrupada#tal=Santa Rita|T1` também (hash e outros parâmetros intactos).
  - E7: cliques medidos antes e depois (`window.__cl`, padrão de `ben_fluxo_test.py:56-57`): "filtrar → agrupar → abrir → voltar" e "voltar à O.S. em outra entrada". Hoje a O.S. reabre sempre em Lista.
- **Regressão:**
  - build, `montar_render` e `varredura`;
  - `ostest.py` (conferir a saída: ele sai com 0 mesmo quando falha, `:117`);
  - `tabelas_os_test.py`, `os_irrig_filtro_test.py`, `os_v39_bloq_test.py`, `os_v39_selo_agua_test.py`, `os_cenario_test.py`;
  - `testes_pedido.py T12`;
  - `acao_unica_test.py familias` e `v3`;
  - `acoes_duplicadas.py … OS`;
  - `componentes_test.py matriz`, `etapas_celular_test.py`, `links_ocultos_test.py`;
  - `ds_test.py`, `ds_unit_test.py`;
  - `ben_fluxo_test.py`, porque o `_kanban` é compartilhado.
- **Pronto quando:**
  - tudo acima foi **executado** na worktree de rascunho, com as saídas brutas em `docs/integracao/VISOES-1/`;
  - os testes novos ficam vermelhos no `_render` anterior e verdes depois;
  - não há regressão contra o pré-merge;
  - o artefato publicado foi conferido com `OS.dc.html?view=agrupada` e F5;
  - DECISIONS e STATUS foram atualizados;
  - o artefato tem uma linha do que mudou;
  - o pedido de revisão ao Codex foi feito com caminho e versão.
- **Lacunas conhecidas que ficam escritas:**
  - o Kanban ainda ignora a ordenação da lista (fatia 2);
  - a Carga esconde blocos em vez de realçar (S3 hoje: o uso da semana continua inteiro e a nota avisa; fatia 4).

### F2 · VISOES-2: Kanban e Calendário (O.S. primeiro)

- **F2a, O.S.:**
  - Calendário só de leitura: semana de segunda a domingo com ‹ › e Hoje; a ordem aparece em cada dia da janela; faixa **Sem data**; no celular, agenda por dia; clique abre o painel.
  - Kanban:
    - ordem das colunas pela ordenação da lista, via `g2visiveis`, e sem ela pelo risco e prazo explicados (PRD:2998);
    - no celular, seletor das 5 etapas com lista vertical (PRD:2992) **[a verificar se já existe]**;
    - sem arraste.
  - BEN: o `.pr-vis` (`areas/processo_beneficiamento.py:22-28`) migra para o seletor, os chips de fase vão para a barra da coleção, e o Kanban passa a ler o recorte da lista. Hoje ele usa todas as ordens (`:63,233`): é defeito e ganha regressão.
- **F2b, cada um só depois da sua dependência:**

| Tela | Mudança | Depende de |
|---|---|---|
| Manutenção | `om_modos` migra (Lista e Kanban); alias `modo=kanban` (2.4). A rotina "Esta semana" fica como está; o Calendário ⏸ só entra se o autor da PCM aceitar trocar a rotina por ele | Composição com a PCM |

IR-03, AG-01 e CMP saíram da F2b na revisão crítica (1.4).

- **Arquivos:**
  - `engine.py`: `v_calendario` e o componente `calendario(gid, campos)`;
  - `g2lib.js`: `g2visiveis` e as funções puras da semana;
  - `areas/processo_os.py` e `areas/processo_beneficiamento.py`;
  - `visoes.py`;
  - `ben_fluxo_test.py:56-57,161,164`, que passa ao auxiliar.
- **Testes:**
  - Unidade:
    - Calendário só com data;
    - janela que cruza semanas aparece em todos os dias;
    - item sem data vai para a faixa;
    - o Kanban segue a ordenação.
  - Regressão do defeito "lista 2 ordens, Kanban 10" (`areas/processo_os.py:794`), estendida: com o filtro "Liberadas", Lista = Kanban = Calendário + Sem data.
  - T12 estendido (`testes_pedido.py:144-189`): a mesma fase em Lista, Kanban, Calendário, App, Detalhe e Mapa IN-04.
  - `[draggable=true] = 0` em todo Kanban e Calendário.
  - BEN: Kanban com o filtro (vermelho antes).
  - 390 px: agenda por dia; nenhuma faixa "Sem data" com o cenário (toda O.S. agrícola tem janela); a faixa é provada na unidade.
- **Pronto quando:** mesmo padrão da F1, com as saídas em `docs/integracao/VISOES-2/`.

### F3 · VISOES-3: Mapa (Talhão, depois Vistoria)

- **F3.0, pré-requisito: uma fonte só de geometria e um componente só de mapa.**
  - Geometria em `dados.py` ou `dados_cad.py`, lida pelo IN-04 (`areas/inicio.py:93`), pelo CD-01 (`areas/cad_fazendas.py:206`; a CADUX ainda tem `GEO_MAPA` próprio, `sp-cadux:areas/cad_fazendas.py:214`) e pela visão. Mostra a qualidade da geometria: T1 validado, os demais em desenho, Lagoa Grande sintética (PRD:407).
  - **Reusar, não criar:** hoje há 4 mapas (IN-04 `_mapsvg`, CD-01 `_mapa`/`_mapa_lg`, CADUX `_mapa_sr`/`_mapa_lg`, CA-01 e PL-02). A F3.0 escolhe **um** dos que já existem, o `_mapsvg` do IN-04 ou o da CADUX (já tem foco por talhão, zoom e "Fora do mapa", que é a faixa "Sem localização"), e o parametriza por prefixo de furos e recorte de IDs. IN-04, CD-01 e as visões passam a chamá-lo; os demais saem. Nenhum `mapa_visao()` novo. A escolha entre os dois é combinada com o autor da CADUX.
  - Regressão com `map_*`, `talmapa_test.py` e `cadux_rev_test.py`.
- **Uso na visão:**
  - alimentado pelos IDs de `g2visiveis` → talhões; fora do recorte, neutro e sem ação;
  - cor, rótulo e próximo passo vêm da **mesma função** da camada correspondente do IN-04 (Vistoria: `mipSit`/`mipProx`, `mip.js:105-140`; O.S.: `_ORD_MAPA`), nunca de uma cópia;
  - várias ordens no mesmo talhão aparecem como contagem (PRD:3008);
  - **sem MapLibre** (depende de rede) e **sem gravar `mapa-ctx`** (`areas/inicio.py:972-976`).
- **F3a, Talhão (depois da TABR e da CADUX):** o `cdv` e o `cd_mtog` da CADUX migram para o seletor, e os dois saem.
  - No computador, "Mapa" = mapa com a tabela sincronizada embaixo (SEL-01; layout da CADUX, `sp-cadux:areas/cad_fazendas.py:256-299`); "Lista" = só a tabela.
  - No celular, as duas visões são exclusivas.
  - O Mapa passa a respeitar o filtro da lista (hoje ignora, `areas/cad_fazendas.py:349-352`).
  - O `g_tal` passa a chamar `g2keep` (hoje não chama), para o "Voltar" do CD-01det (2.11).
- **F3b, Vistoria (AG-01):** mapa por talhão, com contagem e a pior situação, e faixa "Sem localização". O ganho sobre a camada MIP do IN-04 é o recorte da lista (alvo, situação).
- **F3c, O.S.:** só se o proprietário reabrir a DEC-2609-09; então é a camada "O.S./prazos" do IN-04 pelo mesmo componente.
- Setores (IR-01) saíram na revisão crítica: a camada Irrigação do IN-04 já é esse mapa (1.3).
- **Testes:**
  - `CDP_GL=1`;
  - unidade: Mapa só com geometria, fora do recorte neutro, faixa sem localização;
  - `map_decisoes_test.py`, `map_irrig_filtro_test.py`, `map_aprov_test.py`, `talmapa_test.py`;
  - `cadf_fix_lista_test.py:31,60,78,86` pelo auxiliar;
  - `links_ocultos_test.py`;
  - 390 px.

### F4 · VISOES-4: Carga por recurso e Timeline

- **F4a, Carga:** o `_recursos_tab` (`areas/processo_os.py:1158-1205`) vira o componente `carga_visao(recursos, blocos)`.
  - **O filtro realça e não esconde:** os blocos de fora aparecem como "ocupado (fora do filtro)" (RECURSO-06; PRD:7451). Corrige o S3 de hoje.
  - Faixa **Sem alocação (n)** para ordem do cenário sem alocação: a semana é fixa em Python (`alocacao.py:6`).
  - Célula vazia é "sem apontamento", nunca "livre" (PRD:7442). Sem ranking de pessoas (PRD:7461).
  - Máquina (MA › Ativos, depois da PCM): o mesmo componente filtrado por classe (PRD:7487), sem quadro paralelo. O seletor fica à direita; "Ativos | Abastecimentos" continua troca de entidade (1.5).
- **F4b, Timeline:** cultivos no SAF (depois da integração da SAF-C01/C02).
  - Barra do plantio a "Ocupa até", com o trecho estimado marcado "A conferir" (`docs/DECISIONS.md:54-66`).
  - Só leitura.
- **Testes:**
  - TF02 com a Carga realçando (`tabelas_os_test.py`);
  - unidade: a contagem de blocos é igual com e sem filtro; Timeline só com início **e** fim;
  - 390 px.

### F5 · VISOES-5: Matriz, Árvore e Galeria, só onde justificado

**Hoje nenhuma entra; não há código nesta fatia.** Os critérios de entrada já estão em `EXIGE` e nos negativos P2 da F1.

| Visão | Reabre quando |
|---|---|
| Matriz | A Atividade ganhar listagem própria (decisão de produto, Codex) e a TABR aceitar coluna-pivô por semana ("uma variável por coluna", `areas/processo_os.py:534`). O valor é contagem ou ha-operação, nunca soma de produtos diferentes (PRD:7292) |
| Árvore | Existir uma Lista plana com hierarquia que não seja a própria forma da Lista. Exemplo: custo com o campo "superior" no centro de resultado (PRD:8262). Toda Lista hierárquica de hoje já é árvore |
| Galeria | Houver imagem real como informação principal; não com dado sintético (ENG-017) |

### Bateria (por mudança, regime leve §3.5)

```sh
W=/home/user/sp-vis   # worktree da fatia 1 (branch claude/v44-visoes)
git -C /home/user/sp-proto worktree add --detach "$W" <commit>   # nunca rodar build ou teste em /home/user/sp-proto
cd "$W/tools/prototipo/v37/gen37" && python3 build.py && python3 montar_render.py
SAFRION_DADOS=sintetico python3 visoes_unit_test.py
L='env CHROME_BIN=/tmp/cloudchrome/chrome flock /tmp/cdpV.lock env CDP_GL=1 SAFRION_DADOS=sintetico'
$L timeout 900 python3 varredura.py
$L timeout 900 python3 visoes_test.py comp      # e: celular, e2e
$L timeout 900 python3 ostest.py                 # conferir "n ok · m falhas": sai com 0 mesmo com falha
$L timeout 1200 python3 acao_unica_test.py familias   # e: v3
git -C /home/user/sp-proto worktree remove "$W"
```

A trava `cdpV` é própria: `cdp9333`, `cdpB` a `cdpI` e `cdpDS` são de outras frentes. A bateria completa roda só nos marcos, pelo modelo `docs/parceria/evidencias/v44-tabelas-05/un-20261005/00-bateria.sh`.

---

## 4. Riscos

### 4.1 Conflitos com frentes não integradas

| Frente (base) | O que tem em comum com o seletor | Risco | Tratamento |
|---|---|---|---|
| Composição `int/comp` (`sp-comp@47ff754`: SAF-C01b, BEN r2, PCM) | `processo_os.py` (+60: `:767`, `:875-890`, painel), `g2lib.js`, `ui37.py`, `acao_unica_test.py`, `componentes_test.py`, `ben_fluxo_test.py`, `os_cenario_test.py`, `os_v39_bloq_test.py` | **Alto**: são os testes que a F1 troca | A F1 parte da branch única **depois** da composição |
| DS (`sp-ds@943433c`) | `engine.py` (+190), `g2lib.js` (+233: `g2dica`, `g2vis`), `processo_os.py` (+27: `_kanban`, `bloco`), `ds_test.py` (troca de visão pelo texto) | **Alto** | A DS entra antes; nomes `g2visao*`; o `ds_test.py` passa ao auxiliar no commit da F1 |
| PCM (dentro da composição) | `#vis=` e `&modo=kanban` (`sp-comp:areas/maquinas.py:14,34,84,96,297`) | Médio | Não usar `vis`; alias de `modo=kanban` na F2b; "Esta semana" vira Calendário só com acordo do autor da PCM |
| TABR (`sp-tabr@8f19e0d`) | `cad_*.py`, `cadastros.py`, `irrigacao.py`; "uma variável por coluna"; o rótulo "Filtro rápido" usado pelo `tabelas_cad_test.py:131-135` | Médio | Talhão depois da TABR (IR-01 e IR-03 saíram, 1.4); nenhum rótulo do seletor com "Filtro rápido"; Matriz só com acordo |
| CADUX (`sp-cadux@5d533a8`) | `cad_fazendas.py` (651), `cadastros.py` (651), `engine.py` (+76), `g2lib.js` (+83) | **Alto no Talhão** | F3a depois da CADUX, adotando o layout dela (mapa e tabela sincronizados) |
| NAV1 (`sp-nav@a7023ca`) | `processo_planos.py`; `acao_unica_test.py` (+32) | Baixo | Merge textual do teste; copiar o padrão de volta (rolagem e foco) |
| SUP (`sp-sup@6ccd050`) | `processo_estoque.py` (cerca de ±980), `processo_compras.py`, `processo_os.py` (+27) | Médio | EST e CMP só depois da SUP |
| DOM (`sp-dom@c764de9`) | `processo_os.py` (+44, EXTRAVALS e painel) | Baixo: regiões diferentes | Merge textual |

### 4.2 O que não muda

- **Kanban da O.S.:**
  - continua com 5 colunas fixas: A liberar, Liberadas, Em execução, Em conferência, Encerradas;
  - Canceladas fica fora do quadro, e selo não vira coluna (PRD:2984);
  - a fase só muda por comando ("A fase só muda por evento", `areas/processo_os.py:1251`);
  - o DOM `[aria-label="Kanban das ordens"] > div` continua com 5 filhos (`ostest.py:66-72`).
- **Ação primária:** uma, no mesmo lugar e com o mesmo rótulo em todas as visões. O seletor nunca é verde.
- **Rótulo** "Visão das ordens" (os testes usam o `aria-label`; o papel passa a `toolbar`) e vazio de contexto sem seletor.
- **Endereços por hash** (`#OS-…`, `#tal=…`, `#VIS-…`, `#talhao=…`, `#car`) e a chave `mapa-ctx` do IN-04.
- **Regras de domínio:** aprovação, liberação, reserva e apontamento ficam iguais. Trocar de visão nunca é ação de negócio (E5).
- **Abas de entidade e visões-pergunta** (1.5).

### 4.3 Divergências a registrar (e quem decide)

| Divergência | Quem decide | Registro |
|---|---|---|
| Só ícone × "Ícones não substituem rótulo" (PRD:291) e BOT-05 ("sempre com rótulo") | O proprietário: é o pedido dele de 10/10. A VIS-04 já admite dica em ícone sem texto | Em `docs/DECISIONS.md`, com a fonte dele. Os agentes não estendem a exceção a outros botões e não declaram aprovação além do que ele escreveu |
| Barra (`toolbar`) com `aria-pressed` × DS-57 ("visões alternativas são abas", PRD:14541) | Técnica (agentes; Codex revisa). O segmentado é variante válida da DS-36 (PRD:14304) e é o que o pedido diz | DECISIONS |
| Ativo tonal × verde cheio do PRD 74.5.10 | Técnica. Mantém o BOT-01 e o caso 29 | DECISIONS |
| "Recursos" → "Carga por recurso" | Rótulo pelo pedido de 10/10; a DEC-2609-09 continua | STATUS |
| Mapa dentro da O.S. × DEC-2609-09 | Decidido (rev. Codex 01): fica no IN-04 | Seção 0, item 8. Só um pedido do proprietário reabre |
| Onde a Atividade mora | Decidido pelo Codex (rev. Codex 01): Planejar safra, etapa consolidada | 1.4 |
| Arraste no Kanban com confirmação no lugar do desfazer (PRD:2996 permite; o pedido de 10/10 exige desfazer) | **Proprietário**, só se ele pedir arraste no Kanban | Hoje: sem arraste no protótipo e no real (2.10) |
| Calendário da Manutenção no lugar da rotina "Esta semana" | Autor da PCM (técnica) | Rodada; sem acordo, fica ⏸ |
| Mapa único: `_mapsvg` do IN-04 ou mapa da CADUX | Autor da CADUX e Claude (técnica) | F3.0 |

### 4.4 Suposições (a conferir)

1. **O artefato publicado mantém `?view=` no F5 e na navegação [a verificar na F1].** Se não mantiver: `#…&view=` com leitura tolerante, corrigindo os leitores ancorados (`areas/processo_os.py:755-760`, `areas/inicio.py:1093`, `areas/agronomia.py:621,1419`) e as comparações exatas de MA, BEN, Produção, Irrigação e Mobile.
2. **A dica da DS abre no foco em botão só com ícone:** lido em `sp-ds:g2lib.js:539-544`, não executado.
3. **Botão com `display:none` não conta como duplicata** no `acoes_duplicadas.py` [a verificar].
4. **Ícones Lucide 1.45.0 (ISC, de 11/09)**, baixados como dado; legíveis a 16 px com traço 1,8, e o Ellipsis é pequeno [a verificar contraste e legibilidade no `ds_unit`].
5. **"Por usuário" no protótipo é o perfil de demonstração;** no software real, o usuário autenticado.
6. **A troca de visão não abre o `#OS-…`** (abrir o painel não grava hash, `areas/processo_os.py:754-763`). O E6 confere.
7. **As linhas citadas são do `0139898`;** a composição e a DS deslocam `processo_os.py`.
8. **Motivo dos cortes é a tarefa redundante ou o atributo ausente, não o volume** (rev. Codex 01). Poucas linhas sintéticas não provam que a necessidade real não existe. IR-03: a decisão da água é de horário e bomba, já respondida pela IR-02 (Agenda por captação), e a janela é texto. Vistoria: a data dominante é a da coleta (fato) e as previstas já aparecem na Lista. Se a fazenda real mostrar uma tarefa que essas telas não respondem, a visão volta à mesa com esse dado.
9. **A "Nova ordem" exige o início da janela** (`nv_jan` entre os campos validados, `areas/processo_os.py:892`): lido, não executado. Se não exigir, a faixa "Sem data" da O.S. ganha caso real no e2e.
10. **O host do artefato preserva `?theme=`** além de `?view=`; o runtime lê os dois da mesma query.

---

## 5. Software real: especificar para a transferência (não aplicar agora)

**Decisão (rev. Codex 01, achado 3):** especificar agora; transferir ao software real **só depois que todo o conjunto vigente do protótipo estiver concluído e validado** (FOCO v2). A VISOES-1, parcial, não aciona transferência, auditoria integral nem revisão do PRD. Quando a transferência vier, a primeira candidata é `/estoque`, que já sustenta Lista e Agrupada (abaixo).

**Motivos:**
1. **O FOCO v2 manda concluir e validar o protótipo vigente inteiro** e só depois passar tela, domínio, banco e homologação (`docs/decisoes-delegadas/FOCO-v2-confronto.md`, fonte: issue #1, comentário 5974888468).
2. **Correção da revisão crítica:** `/estoque` **já sustenta duas visões pela regra do pedido**: Produto é agrupável e Utilizável e Físico são somáveis na mesma unidade (`apps/web/src/estoque/lista.ts:13-20`). O agrupamento já é estado da tabela: `agrupar` no `EstadoG2` (`apps/web/src/tabela/logica.ts:52,55`), na URL (`:251`, `:284`), escolhido no menu da coluna (`Tabela.tsx:537-541`). Para não haver dois estados, na transferência a Agrupada **não** ganha campo próprio: `visao === 'agrupada'` ⇔ `agrupar !== null`. O botão Agrupada liga o agrupamento padrão da entidade (Produto), a Lista o desliga, e o menu da coluna continua escolhendo a chave. `/cadastros/produtos` (agrupável só por Unidade, sem valor somável) fica só Lista.
3. **Faltam peças que são decisão técnica da transferência:**
   - ícones: `lucide-react` não é dependência; fixar a versão em `docs/architecture/versions.md`, ou copiar o SVG com o aviso ISC;
   - casa do componente: `packages/ui` não existe (BOT-09).
4. **Uma fatia ativa por vez** (AGENTS §3.1); código de produto só entra por PR revisado.

**Contrato a levar:**
- **`apps/web/src/tabela/visoes.ts`, puro:** `visoesValidas`, `visaoInicial(url, pref, validas)`, `urlComVisao`, `proximaVisao`. Coberto pelo Vitest com 95 % ou mais por arquivo, incluído em `vitest.config.ts`.
- **`visao` no `EstadoG2`:**
  - validada em `estadoDaUrl`, ignorando valor desconhecido como já faz com coluna (`test/tabela.test.ts:229-252`);
  - escrita em `urlDoEstado` e levada por `hrefComVolta` (`logica.ts:337`).
  - `Tabela.tsx:80-81` troca a query inteira e descarta o hash: passa a preservar `location.hash`.
- **Preferência por usuário autenticado e entidade:** `localStorage` com o id do usuário na chave e try/catch, como `src/estoque/rascunho.ts:29-32`. Preferência no servidor só se o proprietário pedir entre aparelhos.
- **Componente em `packages/ui`** quando existir, com a mesma ARIA, teclado, celular e estados de 2.5 a 2.8. Lá o "carregando" e o "erro" existem de verdade e são testados.
- **Testes:**
  - Vitest com a tabela de casos da F1 e `fast-check` para a ida e volta da URL;
  - Playwright `desktop` e `celular` (Pixel 7): `getByRole('group',{name})`, `getByRole('button',{name:'Ver em kanban',pressed:true})`, setas, `toHaveURL(/view=kanban/)`, volta do detalhe (`caminhoDeVolta`, `logica.ts:343`), axe em cada visão (`e2e/apoio.ts:15-21`), servidor lento (carregando) e servidor com falha (erro).
- **Kanban real:** sem arraste, como no protótipo: o pedido exige desfazer, e CMD-06 e CMD-10 não têm desfazer legítimo. Trocar o desfazer por confirmação é decisão do proprietário (2.10).
- **Ambiente [a verificar]:** o node desta máquina é v22 e o repositório pede ≥ 24.21. O `pnpm run check` pode recusar aqui.

**Próximo passo:** revisão do Codex recebida e aplicada (rev. Codex 01). A F1 está em implementação na branch `claude/v44-visoes` (base composição + DS mesclada localmente) e entra na branch única depois da composição e da DS, com as provas dos contraexemplos no pacote `docs/integracao/VISOES-1/`.
