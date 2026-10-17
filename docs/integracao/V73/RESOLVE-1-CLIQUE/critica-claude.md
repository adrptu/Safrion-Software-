# RESOLVE-1-CLIQUE · crítica independente do Claude (passo 1)

Claude · 16/10/2026 · base `b989864` (worktree `claude/v44-v73-resolve1`), com leitura da composição `int90` `05947ad` (b989864 + PR #81 EST-ONDA0 + PRs #90/#91).
Escopo: só o passo 1 do pedido (`pedido.md`), a parte do Claude. Não simula Codex nem Gemini. Não registra desenho final nem fatias no checkpoint: as fatias do §8 são sugestão para o Codex decidir.
Rótulos: **executado** = rodei e a saída está em `reproducao/`; **lido** = li a fonte citada; **especificado** = proposta ou contagem por leitura, sem execução.
Fonte vigente = geradores em `tools/prototipo/v37/gen37/` (abreviado `gen37/`). O anexo cita linhas do HTML publicado; aqui toda citação é da fonte.

## 0. Resumo

- O anexo se confirma na fonte: das 36 afirmações de fato, 32 confirmadas, 3 em parte e 1 não reproduz (a base legal). Nenhuma está resolvida por frente integrada; o int90 (EST-ONDA0) dá a mesma saída na reprodução (**executado**).
- O desenho do proprietário é bom e, em boa parte, **já está no PRD**: a linha "Falta [produto] para [necessidade]" com a ação de cada papel é a SUBST-13 (PRD 40.6); a reserva antes da liberação é o CMD-44 (cobertura de planejamento, RSV-03 d); a urgência que não pula controle é o FL-27. O trabalho é implementar o contrato, não criar outro.
- O problema de raiz não é a falta do botão. É que **não existe fonte única de disponibilidade**: há 8 cálculos diferentes, e dois deles dão respostas opostas para a mesma ordem (OS-0501: a liberação diz "coberto", a demanda única diz "falta comprar"; **executado**, R3). Botão de 1 clique sobre estado errado leva a pessoa errada à ação errada.
- Proposta central: uma função `supCobertura` ao lado do `cenInsumosOrdem` do EX-38, lida por O.S., liberação, app, Estoque, AG-01, irrigação, BEN e (por adaptador) MA. Ela corrige antes de tudo o lote sem fazenda e o lote único.
- O padrão MA serve, com 2 correções reproduzidas: a 2ª compra da mesma OM vira beco sem saída (R7c) e a idempotência de Compras aceita a mesma chave com outro conteúdo (R9).
- O único caminho avulso que existe compra "Ureia 45%" como material de consumo de uma ferragem, sem entrar em lote, e a O.S. continua bloqueada (R8). Hoje isso é risco, não proteção.
- A Lei 7.802/1989 citada no pedido e no anexo foi revogada pela Lei 14.785/2023 (PRD 21.3 S7; página do MAPA consultada em 16/10/2026). O artigo que trata do receituário na lei nova fica "verificar".

## 1. Confirmação do anexo na fonte vigente

Legenda: ✔ confirma · ◐ confirma em parte · ✘ não reproduz. "int90" = se a composição candidata muda o item. Em todos, int90 **não muda** (reprodução idêntica, `reproducao/saida_int90_05947ad.txt`; o PR #81 só mexe em devolução e na identidade NF × pedido, `areas/processo_estoque.py`).

| ID | Afirmação do anexo (resumo) | | Fonte vigente / prova | Situação |
|---|---|---|---|---|
| A-01 | SU-01..09, CA-04, PL-04/05, IN-01/02, CD-06 não carregam o motor; OS, EST, CMP, MA, BEN, SAF, AG-01, AG-07, IN-04, MB-*, PSUP, SU-03det carregam | ✔ | `areas/suprimentos.py` só usa `cenario.js_prefixo` em SU-03det (:490); `areas/campo.py`, `areas/planejamento.py`, `areas/cad_produtos_estrutura.py` sem `cenGet` (lido) | Pendente: EX-01 |
| A-02 | SU-03 mostra N26-03 "reservado 0"; cenário tem 8.000 kg | ✔ | `dados2.LOTES` reservado 0 → `suprimentos.py:380-390`; CEN0 reserva 8.000 via REQ-040 (R0 e R4, executado) | Pendente: EX-01 |
| A-03 | SU-07 diz "reservada no S58-0801"; lote com reservado 0 | ✔ | `suprimentos.py:869`; S58-0801 com reservado 0 no CEN0 (R0, executado) | Pendente: EX-01 |
| A-04 | Colunas Produto · Dose · Na ordem · Usado · Situação | ✔ | `areas/processo_os.py:1379`, `:770-772` | — |
| A-05 | Dono "Suprimentos", prazo "receber o insumo no Estoque"; não é papel do catálogo | ✔ | `processo_os.py:298-299`, `:634`; `g2lib.js:714-719`; cópia em `irrigacao_estado.js:189`; R1 (executado) | Pendente |
| A-06 | Situação em A liberar é texto semeado; depois de liberar, `osInsSit` + `cenInsumoSaldoTxt`; "falta" é consumo restante | ✔ | `processo_os.py:339-348`, `:772`; `cenario.js:128-132`; texto da OS-0502 em `dados_lagoa_safra.py:176` (R2) | — |
| A-07 | A O.S. não mostra disponível, reservado por outras, validade, local, a caminho, outra fazenda, falta numérica | ✔ | `processo_os.py:770-772` monta só p, g, dose, tot, usado, sit, trilha | Pendente |
| A-08 | OS-0418: sem lote de Ureia | ✔ | R1: 0 lotes; "Sem lote de Ureia 45% no Estoque." | Pendente |
| A-09 | OS-0502: 96.940 kg × 60.000; "o pedido de 50.000 kg não está no cenário" | ◐ | R2: a recusa confere. O recebimento previsto de 50.000 kg em 30/09 **existe** na demanda (`dados2.py:949-950`, `cenEstDem.recebDt`, sem PC); a liberação não o lê | Pendente |
| A-10 | OS-0501 (Lagoa Grande) reservaria glifosato e óleo da Santa Rita, sem aviso | ✔ | `cenario.js:157` (`cenLote` sem fazenda); R3: G26-14 e O26-05 no Almox. defensivos; a demanda (DEM-07, `cal01.js:115`) diz o contrário | Pendente · S2 (§7) |
| A-11 | OS-0425 "Liberada com faltam 3.400 kg" só existe na semente | ✔ | R4: com a mesma ordem em A liberar, a regra recusa 8.000 para 11.400 | Pendente |
| A-12 | Liberação usa um lote, o de maior saldo, sem fazenda, sem FEFO, tudo ou nada | ✔ | `cenario.js:157`, `:313-332`; R5: 200 + 200 L não liberam 320 L | Pendente · S2 |
| A-13 | Protege o reservado de outra O.S.; não protege a demanda futura | ✔ | `cenDisp` (`cenario.js:158`); R6: liberar a OS-0501 deixa a OS-0430 sem saldo, sem aviso | Pendente |
| A-14 | Bloqueio com "Quem resolve: Suprimentos" e link "Ver saldos no Estoque"; ajuste vira "Salvar e liberar" | ✔ | `processo_os.py:634` | — |
| A-15 | Ajuste tira/inclui produto com "N disponíveis / sem saldo"; trava por item | ✔ | `processo_os.py:870`, `:463-466` | — |
| A-16 | Na O.S. não há pedir compra, transferência, reserva parcial, substituto, urgência | ✔ | sem comando no `processo_os.py`; `areas/processo_estoque.py` 0 ocorrências de "comprar/solicitar compra" | Pendente |
| A-17 | Almoxarife sem ação sobre a falta na O.S. e no Estoque | ✔ | `processo_os.py:654` (aviso de decisão de outro papel); EST sem ação de compra (lido) | Pendente |
| A-18 | MB-05 mostra "Conflito de reserva" e manda ao Planejar safra | ✔ | `areas/mobile.py:774-777` | Pendente |
| A-19 | Início bloqueado sem entrega (`cenIniFalta`); ocorrência sem tipo "Falta de insumo" | ✔ | `cenario.js:483`, `:497`; `areas/campo.py:457` | Pendente |
| A-20 | Avulsa vedada a insumo ("Nunca safra ou cultura") | ◐ | Só comentário (`dados_compras_mat.py:152`). R8 (executado): a avulsa **aceita** "Ureia 45%" como material sem código, grupo Materiais gerais, PC numa ferragem, recebida como consumo direto no centro de custo "Sede"; nenhum lote; a OS-0418 segue bloqueada | Pendente · S2 se fosse ao ar |
| A-21 | Insumo só pela SOL da safra, 6 etapas, alçada 50 mil/300 mil/Direção, sem urgência, data viável fixa (+7 d), SOL sem O.S. de origem | ✔ | `processo_compras.py:23`; `dados2.py:857`, `:1253-1255` | Pendente |
| A-22 | Caminho indireto O.S. → complemento no Planejar safra → compra | ✔ | `safra.js:1663`, `:2063` | Pendente |
| A-23 | Troca de produto só no Ajustar, só A liberar, AL-02; confere cultura, dose, máx. aplicações, alvo; carência na liberação; IRAC/FRAC só informativo | ✔ | `processo_os.py:467-468`, `:493-506`, `:443`; 0 ocorrências de "Rotação" em `processo_os.py` | Pendente |
| A-24 | AG-01 lista registrados com selos ("Sem estoque", "Rotação", "Carência"); estoque só alerta; AG-07 "Usar na O.S." deixa dose em branco | ✔ | `areas/agronomia.py:646-648`; `mip.js:249`, `:257-259`; `agronomia.py:1675`; `processo_os.py:982-987`. Nota: o AG-01 preenche a dose **mínima** da bula ao escolher (`agronomia.py:648`) | — |
| A-25 | Alçada contornável: avulsa aberta a qualquer papel, alçada só no pedido, sem antifracionamento; quem envia, cota e aprova pode ser a mesma pessoa | ✔ | `dados_compras_mat.py:121-128`, `:175-181`; R7b (executado): Ana abre, cota, emite e recebe a própria SC | Pendente · S2 |
| A-26 | CD-06 sem registro, ingrediente, modo de ação, alvo e mínimo de insumo | ◐ | `areas/cad_produtos_estrutura.py` sem campo de mínimo, ingrediente ou registro (busca); não abri a tela | — |
| A-27 | Em trânsito fora do cenário de lotes; entra só na demanda (`b.rec`) | ✔ | `cenario.js:242-271`; `dados2.py:949-951` | Pendente |
| A-28 | Transferência só estática (SU-08), sem comando no motor | ✔ | nenhuma função de transferência em `cenario.js`, `processo_estoque.py`, `dados_manutencao.py`; TR-0452 só em `suprimentos.py:1018` | Pendente |
| A-29 | PSUP com 4 indicadores de lote e requisição | ✔ | `areas/paineis.py:29-33` | Pendente |
| A-30 | MA: falta na OM, "Solicitar compra" em 1 clique, só a falta, não duplica, carrega OM e ativo, chega reservada (D5) | ✔ | `dados_manutencao.py:526`, `:644-653`, `:655-669`; `dados_compras_mat.py:142-145`; R7 (executado) | Integrado (V69) |
| A-31 | MA: urgência pela criticidade da OM; corretiva nasce sem peças; almoxarife simulado | ✔ | `dados_compras_mat.py:143`; `areas/maquinas.py:1154`; `dados_manutencao.py:711`; `maquinas.py:430-451` | Pendente |
| A-32 | BEN: só caixa; aloca em vários lotes, tudo ou nada; fontes de recuperação; compra no BEN-2 | ✔ | `ben.js:81-82`, `:105-109`, `:179-200` | Pendente (BEN-2) |
| NOVO-4 | BEN aloca sem FEFO e sem fazenda (achado meu, fora da contagem do anexo) | ✔ | `ben.js:81-82` ordena por livre, não por validade nem fazenda | Pendente |
| A-34 | PL-04/PL-05 estáticos com "Falta de insumo · Suprimentos · Rui" | ✔ | `planejamento.py:398`, `:468-469` | Pendente: EX-01 |
| A-35 | IN-01 mostra a OS-0418 com selo fixo | ✔ | `areas/inicio.py:1713` (linha fixa) | Pendente: EX-01 |
| A-36 | "Suprimentos ainda não é papel" também em Compras | ✔ | `processo_compras.py:352`; PRD 2 já tem o papel **Comprador** | Pendente |
| A-37 | Receituário: "Lei 7.802/1989, art. 13" | ✘ | Revogada pela Lei 14.785/2023: PRD 21.3 S7 (`docs/PRD.md:5246`) e página do MAPA "Legislação de agrotóxicos" (gov.br, consultada em 16/10/2026: "revoga as Leis nºs 7.802 … e 9.974"). O Planalto não respondeu (HTTP 503); o artigo do receituário na lei nova: **verificar** | Pendente |

Contagem (36 afirmações de fato; A-33 não existe porque o achado do BEN é meu): 32 ✔, 3 ◐ (A-09, A-20, A-26), 1 ✘ (A-37), 0 resolvidas por frente integrada. As melhorias do anexo (§6.2, §7.3, §8.3) são avaliadas nos §2 a §6, não contadas como fato. Achados novos: **NOVO-1** (beco da 2ª compra na OM, R7c, executado), **NOVO-2** (idempotência sem conteúdo em Compras, R9, executado), **NOVO-3** (8 cálculos de disponibilidade, §2.1, lido), **NOVO-4** (BEN sem FEFO nem fazenda, lido).

## 2. Padrão único: disponibilidade na linha do material

### 2.1 Hoje não há fonte única (lido; contradição executada em R3)

| # | Onde | O que calcula | Escopo |
|---|---|---|---|
| 1 | `cenario.js:157-158`, `:313-332` (`cenLote`, `cenDisp`, `cenLiberar`) | liberação da O.S. | 1 lote, maior saldo, qualquer fazenda |
| 2 | `processo_os.py:463-466` (`osc_ajFalta`) | trava do Ajustar | idem 1, mensagem própria |
| 3 | `mip.js:257-259` (`mipChecks`) | selo "Sem estoque" do AG-01 | idem 1 |
| 4 | `irrigacao_estado.js:185-190` (`irrFertBloq`) | falta na fertirrigação | cópia do 1, sem carência nem regra legal |
| 5 | `ben.js:81-109` (`benLotesCx`, `benAlocarCx`) | caixas do packing | vários lotes, sem FEFO nem fazenda |
| 6 | `dados_manutencao.py:525-526` (`manLivreIt`, `manFalta`) | peça da OM | outro estoque (`c.man.itens`), sem lote nem local |
| 7 | `cenario.js:172-306` + `cal01.js` (`cenOsSup`, `cenOsDem`, `cenEstDem`) | demanda única | por fazenda (DEM-07) |
| 8 | `agronomia.py:1214` | filtro "Na fazenda" do AG-07 | por fazenda |

Dano: a O.S. diz uma coisa, o Planejar safra e a compra dizem outra (OS-0501, R3). Isso fere a ENG-011 (fórmula num único serviço de domínio) e é exatamente o que o EX-38 corrigiu para preparo e saldo.

### 2.2 Proposta: `supCobertura`, uma função, todos os leitores (especificado)

- **Onde mora:** no protótipo, em `cenario.js`, ao lado de `cenInsumosOrdem` (`cenario.js:66`, a fonte do EX-38, lida por `processo_os.py`, `mobile.py` e `os_campo.py`). No software real, em `packages/domain` (cálculo) e `packages/application` (consulta), com o servidor como autoridade (PRD 24; AGENTS §4).
- **Assinatura:** `supCobertura(c, doc, {data})` → por linha `{item, un, nec, resDoc, dispFaz, outraFaz:[{faz, local, q}], aCaminho:[{ref, q, dt, aTempo}], falta, estado, acao}` e um resumo `{prontos, total, texto}`.
- **Monta sobre o que existe:** `nec` vem da regra única de quantidade (`cenQtd`) e do `cenOsSup` (need menos custódia); `resDoc` de `cenResPropria`; `dispFaz` de `cenDisp` filtrado pela fazenda do documento (a mesma regra da DEM-07); `aCaminho` dos recebimentos com pedido (`b.rec` com `ref`). Nenhuma fórmula nova.
- **Leitores:** detalhe da O.S. (`pan_ins`), prévia e comando da liberação (`osc_libEfeito` passa a alocar pelo resultado), app do líder (MB-02det), Estoque (lista "O.S. aguardando material", por O.S.), AG-01 (selo de estoque), fertirrigação (substitui `irrFertBloq`), BEN (alocação de caixas), MA por adaptador (`supLinhas` da OM sobre `c.man.itens`, até o estoque da oficina ter lote).
- **Aceite mensurável:** os 8 pontos do §2.1 passam a 1 função + 1 adaptador (contagem por busca no código); OS-0501 dá a mesma resposta na liberação e na demanda.

### 2.3 Colunas e estados

| Elemento do pedido | Decisão | Motivo |
|---|---|---|
| Necessário calculado, nunca digitado | **Adotar** | P29; `cenQtd` |
| Reservado para este documento | **Adotar** | `cenResPropria` |
| Disponível na fazenda, já sem reservas de outros | **Adotar** | RN-011 ("no mesmo escopo") |
| Em outra fazenda, transferível | **Adaptar:** sem coluna; vira o estado "Disponível na Santa Rita · transferir" só quando há falta | Cabe a 390 px; a coluna fica vazia em quase toda linha |
| A caminho, com previsão | **Adaptar:** conta só pedido emitido (PC) com previsão; "previsto sem pedido" (calcário da OS-0502) aparece como texto e não cobre | Previsão sem pedido não é compromisso (SU-01 usa "recebimento firme") |
| Falta = nec − (res + disp + a caminho a tempo) | **Adaptar:** duas leituras. Para **liberar**, só conta físico apto (RSV-03 a). Para **comprar**, conta o pedido a tempo | Pedido a caminho nunca autoriza CMD-06 nem entrega |
| Estados "Coberto", "Coberto com transferência", "Coberto por pedido, chega dd/mm", "Falta N" | **Adaptar** para: "Reservado" · "Disponível · reserva ao liberar" · "Na Santa Rita · transferir" · "A caminho · chega dd/mm" (atenção se depois da data) · "Falta N un" | "Coberto" com pedido a caminho induz a liberar sem material |
| Resumo no topo: "3 de 4 itens cobertos · falta 120 L de Abamectina" | **Adotar**, com "prontos para liberar" | TAB-06 (atenção na linha) |
| Mesmo check no detalhe, liberação, app e almoxarife | **Adotar** pela §2.2 | EX-38 |

**Regras de cálculo (especificado):**
- **Unidade de compra × uso:** a falta fica na unidade de uso; a compra arredonda para a embalagem (`EMB`, `cenario.py:11-13`) e mostra "120 L = 6 galões de 20 L". O excedente da embalagem é identificado e nunca eleva a dose (CAL-11; PRD 40.5).
- **Lote por fazenda:** `cenLote` passa a receber a fazenda do documento. Estoque de outra fazenda só por transferência explícita (pedido do proprietário; ENTREGA-FAZ ajuste 8: mover exige permissão nas duas fazendas).
- **FEFO e vários lotes:** ordena por validade, depois por lote; divide entre lotes (algoritmo do `benAlocarCx`, trocando "maior livre" por FEFO). Tudo ou nada **por ordem** continua (RSV-03 c).
- **Parcial com aceite do RT:** não existe "liberar parte" de uma versão (RSV-03 c). O caminho é o RT dividir a O.S. pela área coberta (P16; OS-LOTE §3, "Separar este talhão"), com nova versão e aprovação individual (DEC-1610-03). A OS-0425 semeada precisa ser refeita assim ou rotulada "legado".
- **Demanda futura (corrida):** a prévia da liberação mostra o impacto, sem travar: "esta reserva deixa a OS-0430 (início 25/09) sem 68 L". O PCP decide; quem quer proteger uma ordem usa a reserva de planejamento (CMD-44). Dano evitado: ordem da outra fazenda bloqueada sem ninguém saber (R6).

### 2.4 Design system: "1 clique" sem quebrar BOT-01 e BOT-07 (especificado)

- BOT-07 manda **uma ação por linha de tabela**, que abre o registro; BOT-01 manda **um verde por contexto**, e bloco de conteúdo não tem verde. Um botão verde por linha de insumo quebra os dois.
- Adaptação: o estado fica em texto na linha (TAB-06); o "Próximo passo" do documento (BOT-02) leva **a** ação da falta mais urgente, já com o verbo e o objeto: "Pedir compra · 120 L de Abamectina". Com duas ou mais faltas: "Pedir compra das 2 faltas" (uma solicitação com vários itens). Cada linha tem "Resolver ›", que abre o painel da linha com as outras saídas (transferir, trocar produto).
- Resultado: o caso comum continua em 1 clique; o raro custa 2.

## 3. Ações de 1 clique por estado

| Estado → ação | Quem pode | Efeito | Idempotência | O que quebra se for 1 clique "de verdade" | Clique |
|---|---|---|---|---|---|
| Disponível → **Reservar** | Almoxarife ou PCP (PRD 73.4.1; CMD-44). O agrônomo vê "reserva ao liberar" | Reserva de **cobertura de planejamento**, com validade (RSV-02; números da DEC-1610-04); CMD-06 converte (RSV-03 b) | chave + conteúdo; uma reserva por linha | Qualquer papel prenderia estoque para ordem de baixa prioridade | 1 |
| Outra fazenda → **Pedir transferência** | Quem pode liberar ou o almoxarife de destino | Pedido na fila do almoxarife de origem; nada se move até ele separar e o destino receber | uma por (documento, item) | Mover estoque sem as duas fazendas saberem; comando não existe hoje (A-28) | 1 |
| A caminho depois da data → **Pedir antecipação** | Quem pediu | Pendência no PC para o comprador; o PC muda só com o fornecedor ("Reprogramar PC", Suprimentos simplificado v2 §4.2) | uma por PC | Mudar a data do pedido sem o fornecedor | 1 |
| A caminho depois da data → **Reprogramar a O.S.** | PCP (CMD-05/CMD-11) | Nova janela; fora da janela aprovada pede nova versão (OS-LOTE §3) | versão esperada | Executar fora da janela aprovada | 1 + data |
| Falta → **Pedir compra** | Quem tem o documento (agrônomo, PCP, PCM, produção) | **Solicitação** (SC) pronta na fila do comprador. Não é pedido de compra: P34 e PRD 15.1 | uma SC aberta por (documento, item); 2º clique mostra a existente; falta maior oferece "Somar à SC-x" | Nada: é pedido interno, reversível (Desfazer, P53). O risco está na aprovação, que continua com alçada | 1 |
| Falta de defensivo sem receituário vinculado | — | O botão diz o que falta e leva a "Emitir receituário" (AG-01) | — | Compra de agrotóxico sem prescrição (§9) | 1 + receituário |
| Insumo em falta → **Trocar produto** | Só o agrônomo (AL-02). Some se o item for "Usar somente este produto" (PRD 40.5, SUBST-11/13): aí a saída é "Revisar modo do item" | Nova versão vN+1 (já existe em `osc_ajustar`); invalida a aprovação; refaz dose, total e calda | versão esperada | Dose errada ou carência violada. Por isso **não** é 1 clique: escolher (1) + dose dentro da faixa da bula (1 número; nunca a mínima por padrão, PRD 40.5 e OS-LOTE §4) + salvar vN+1; depois Revisar versão e Liberar, intenções separadas (APROV-09) | 3 |
| Peça com saldo → **Requisitar** | PCM | Reserva de manutenção (RSV-01) e separação pelo almoxarife real, com recibo | chave | Peça sai sem custódia | 1 |
| Peça sem saldo → **Pedir compra** | PCM | `supSolicitar` (§4); prioridade pelo ativo: bloqueado com produção afetada = Urgente | idem | — | 1 |
| Preventiva → rascunho N dias antes | Automação (P34), PCM confirma | Rascunho de SC, N = prazo do fornecedor do grupo | uma por OM e item | Compra emitida sozinha | 0 + 1 |
| Reservado para outro → **Remanejar** | PCP ou gestor; nunca quem só pede | Move a reserva e mostra o efeito na outra ordem antes | versão das duas linhas | Tirar material de ordem já liberada sem o dono saber | **1 + confirmação** |
| Aprovar compra urgente | Comprador ou alçada por valor; nunca quem pediu (segregação, PRD 2.1) | PC emitido | chave | Comprometer dinheiro (P62: a automação para no pagar) | **1 + confirmação** com valor e impacto |
| Receber | Almoxarife; nunca quem aprovou o PC (ou revisão posterior, como a PEND-CTL-02) | Entra no lote da fazenda de destino e reserva para o documento que pediu: OM = reserva de manutenção (DEC-1610-01); O.S. = cobertura de planejamento CMD-44 | chave + conteúdo | Reserva sem validade prende estoque; receber o que você mesmo comprou | 1 |

**Onde "1 clique" vira "1 clique + confirmação"** (AGENTS §4, dano nomeado): Remanejar (tira material de outra ordem), Aprovar e emitir compra (dinheiro), Trocar produto (resultado técnico e lei: dose, carência). Pedir compra, pedir transferência e reservar ficam em 1 clique, porque são reversíveis e não movem material nem dinheiro.

**Conflito de fonte a resolver (para o Codex):** a ENTREGA-FAZ aceita diz que, no insumo agrícola, "a reserva para a O.S. continua na liberação (P5)" (`docs/integracao/V71/ENTREGA-FAZ.md:215`). O pedido quer o recebido reservado para quem pediu. A DEC-1610-01 vale para peça de manutenção. Proposta: para insumo, a reserva no recebimento é CMD-44 (cobertura de planejamento, com validade), que o PRD permite antes do CMD-06 (RSV-03 d). Assim nada se entrega antes da liberação, e ninguém leva o material da urgência. A ENTREGA-FAZ P5 precisa citar essa exceção.

## 4. Generalizar o padrão MA (especificado)

Hoje: `manFalta` (`dados_manutencao.py:526`) → `manSolicitar` (`:644`) → `cmmDaOm` (`dados_compras_mat.py:142`) → `cmmReceber`/`manReceberSc` (`dados_compras_mat.py:198`; `dados_manutencao.py:655`).

API única proposta (mesmos verbos para O.S., OM e ordem de beneficiamento):

| Função | Parâmetros | Faz | Generaliza |
|---|---|---|---|
| `supLinhas(c, doc)` | doc = `{tipo: 'os'|'om'|'ob', id}` | linhas de material do documento: `{item, un, nec, fazenda, local, data}` | `o.ins`, `o.pecas`, BOM do BEN |
| `supCobertura(c, doc, opt)` | §2.2 | estado por linha | `cenLote`, `manFalta`, `benLotesCx`… |
| `supFalta(c, doc)` | — | linhas com falta > 0 | `manFalta` |
| `supSolicitar(c, doc, itens, ator, chave)` | itens opcional (padrão: todas as faltas) | cria a SC ou soma à aberta do mesmo (doc, item); grava `doc.scs[]` (lista, não um só `o.sc`) | `manSolicitar` + `cmmDaOm` |
| `supReceber(c, sc, qtds, ator, chave)` | — | entra no lote/local de destino e reserva para o documento (finalidade por tipo) | `cmmReceber` + `manReceberSc` |
| `supTransferir(c, doc, item, de, ator, chave)` | — | pedido de transferência (novo) | — |
| `supRemanejar(c, de, para, item, qtd, ator, chave)` | — | move reserva com prévia do impacto | — |

- **Estados vistos no documento:** Solicitado (SC "A cotar") → Em cotação → Pedido (PC e previsão) → A caminho → Recebido · reservado. São as etapas de `CMM_ETAPAS` traduzidas; nenhuma etapa nova.
- **Duas correções do padrão MA antes de copiar:**
  - **NOVO-1 (executado, R7c):** a SC pede `nec − livre`, mas não segura o livre. Outra OM libera e leva o livre; a SC chega, a OM continua com falta, "Solicitar compra" responde "já foi enviada" e a liberação manda "aguardar o recebimento da SC-041", que já foi recebida. Correção: idempotência por (documento, item, SC aberta), não por "o documento já tem SC"; e no mesmo comando reservar o livre que entrou na conta (CMD-44 ou reserva de manutenção).
  - **NOVO-2 (executado, R9):** `manCmd` (`dados_manutencao.py:480`) devolve "repetido" para a mesma chave com **outro** conteúdo (10 kg e depois 12 kg). O `cenIdem` do Estoque (`cenario.js:305`) acusa conflito. Vale a regra do PRD (chave + hash do conteúdo, glossário do PRD 21.1, "Idempotência", e 73.3): uma função de idempotência só.
- **O que muda em CMP:**
  - **SC aberta ao grupo agrícola:** novos grupos Defensivos, Fertilizantes, Corretivos, Sementes e Embalagens, com o item do catálogo de insumos (CD-06) e recebimento **em lote** da fazenda, não consumo direto. Fecha o R8.
  - **Origem e apropriação:** O.S. → safra e talhão (com "fora do plano" quando for o caso); OM → ativo; OB → ordem e rota; avulsa → motivo e vínculo. O "nunca safra ou cultura" continua para peça e material.
  - **Papel Comprador no catálogo** (`G2_PAPEIS`, `g2lib.js:714`), que o PRD 2 já tem. O dono da falta passa de "Suprimentos" ao comprador quando não há saldo em lugar nenhum, e ao almoxarife quando há saldo em outro local.
  - **Fila do comprador:** a "Atenda solicitações" de Compras ordena por "precisa até" e mostra a origem com link de volta. Só uma fila; nenhuma tela nova.
  - **Demanda única conta a SC:** a SC e o PC de urgência entram como recebimento com `ref` e chave da O.S. (DEM-04, "conta uma vez com a ordem"). Sem isso, o Planejar safra pede complemento do mesmo item (risco do anexo §6.1 item 6).

## 5. Compra avulsa fora do plano (especificado)

- **Seis campos visíveis:** item (busca no catálogo e "criar item" no campo, P32); quantidade com unidade (um campo); precisa até (atalhos hoje, amanhã, +7); local de entrega (herdado do contexto); motivo (chips: praga ou doença, quebra, perda ou avaria, clima, outro); vínculo (herdado quando nasce de vistoria, ocorrência ou ordem). Urgência é calculada da data e do prazo do grupo, não digitada.
- **Impacto antes de enviar:** "fora do plano: +R$ 3.420 na Safra 2026/27 · T4" (exemplo: 1.140 kg × R$ 3,00, preço sintético), pelo preço de referência do catálogo que a demanda já usa (`cat.preco` em `cenOsDem`). Não conferi onde o orçamento vivo da safra mora; até essa ligação (CONTROLE-02), o texto diz "estimativa pelo preço de referência", sem fingir saldo de orçamento.
- **Duplicidade e soma:** mesma (item, fazenda de destino) com SC aberta → mostra e oferece "Somar à SC-x"; mesma origem → abre a existente.
- **Demanda única:** a SC avulsa de insumo vira linha "fora do plano" na demanda da fazenda, com a chave da SC (DEM-04/DEM-09). O Planejar safra a mostra como cobertura e não compra de novo; o planejado × realizado mostra o desvio.
- **Receituário de defensivo:** padrão conservador até o RT ou o jurídico confirmar: defensivo avulso só com receituário vinculado (AL-02), emitido no AG-01. Base legal a citar: Lei 14.785/2023 (vigente; revogou a 7.802/1989) e Decreto 4.074/2002, que a página do MAPA ainda lista como "Decreto de Agrotóxicos" sem dizer se regulamenta a lei nova. Artigo e regulamentação: **verificar**.
- **Antifracionamento (especificado):** soma das SCs do mesmo item ou grupo, por solicitante, em janela móvel (proposta 7 dias, parâmetro), contra a alçada. Ao passar, sobe ao nível da soma. Quem pede não aprova (§3). Sem isso, três SCs de R$ 40 mil furam a alçada de R$ 50 mil.

## 6. Packing e agroindústria: BOM mínimo para a F1 (especificado)

- **Manter:** lista de materiais por rota, versionada: `{item, base: 'caixa' | 't' | 'pallet', coeficiente}`. A demanda é coeficiente × (caixas previstas ou t previstas da ordem). Mesmo `supCobertura`, mesmo `supSolicitar`.
- **Entra na F1, só o que segura a ordem:**
  - PACK-FRU: caixa (já existe), etiqueta (1 por caixa) e pallet (caixas por pallet);
  - SEC-GRA: lenha ou gás (kg por t seca);
  - CAF-BEN: sacaria (sc por t).
- **Cortar da F1:** cera e fungicida pós-colheita (são agrotóxicos: registro, receituário e carência próprios, outro domínio); sanitizante; fita; cantoneira; fumigação. Entram com a regra legal deles, não como "material de linha".
- **Estoque mínimo de embalagem:** rascunho de reposição pelo ponto de pedido (PRD 65; P34), igual ao `cmmRepos` da oficina. Demanda pela previsão de colheita publicada (AL-17) fica para depois da F1.

## 7. Riscos priorizados (severidade se fosse ao ar sem a correção; PRD 22.1)

| # | Risco | Dano | Sev. | Mitigação |
|---|---|---|---|---|
| 1 | Liberação reserva lote de outra fazenda (A-10, R3) | Material reservado onde não está; demanda e O.S. se contradizem; a outra fazenda perde estoque sem saber | S2 | `cenLote` por fazenda; transferência explícita |
| 2 | Duas respostas para "está coberto?" (NOVO-3) | Compra a mais ou a menos; ordem bloqueada sem motivo | S2 | `supCobertura` única |
| 3 | Lote único, tudo ou nada (A-12, R5) | Fluxo essencial bloqueado com estoque suficiente | S2 | FEFO em vários lotes |
| 4 | Avulsa compra insumo como consumo direto (A-20, R8) | Custo no centro errado, estoque que não aparece, O.S. bloqueada | S2 | Recusar item do catálogo agrícola na avulsa já; depois SC agrícola em lote |
| 5 | Mesma pessoa pede, aprova e recebe (A-25, R7b) | Dinheiro comprometido sem segunda pessoa | S2 | Segregação com exceção auditada (PRD 2.1; padrão da PEND-CTL-02) |
| 6 | Trocar produto com dose automática | Aplicação fora da intenção do RT | S1 se pular a aprovação; S2 se não | Dose em branco com a faixa da bula; nova versão; aprovação individual |
| 7 | Compra de defensivo sem receituário | Infração legal | S2 (a confirmar) | Receituário vinculado; consulta ao RT e ao Gemini |
| 8 | Recebido reservado sem validade | Estoque preso para sempre | S3 | CMD-44 com validade (RSV-02) |
| 9 | Beco da 2ª compra na OM (NOVO-1, R7c) | OM sem caminho no próprio fluxo | S3 (há a avulsa manual) | Idempotência por linha; reservar o livre ao pedir |
| 10 | Idempotência sem conteúdo (NOVO-2, R9) | 2º recebimento diferente some como "repetido" | S3 | Uma função de idempotência |
| 11 | Corrida pela demanda futura (A-13, R6) | Ordem de outra fazenda perde o saldo sem aviso | S3 | Impacto na prévia; CMD-44 |
| 12 | Dono "Suprimentos" inexistente (A-05) | Pendência sem pessoa | S3 | Papel Comprador; dono pelo estado |
| 13 | Telas SU estáticas divergentes (A-01..03) | Decisão com saldo errado | S3 no protótipo | EX-01 |

## 8. Fatias propostas (sugestão para o Codex decidir; especificado)

Teto: 3 frentes abertas (AGENTS §3.6). Em curso, pelo que li nesta sessão: MA-VINCULO (Claude, branch `claude/v44-v73-ma-vinculo`), OS-LOTE (Codex, PR #88, em revisão) e a composição int90 ainda não enviada; o Codex confere a contagem no checkpoint. Nenhuma RES começa antes de uma frente entrar numa versão publicada. A primeira é a **RES-0**, porque fecha três S2 (riscos 1 a 3), não cria tela e todo botão das outras depende de um estado correto.

| ID | Persona | Arquivos prováveis | Aceite observável | Regressão (pedido §6) | Medida antes → depois |
|---|---|---|---|---|---|
| RES-0 · fonte única | agrônomo, almoxarife | `cenario.js`, `processo_os.py`, `mip.js`, `irrigacao_estado.js`, `ben.js` | OS-0501 mostra "Na Santa Rita · transferir" e não libera com lote alheio; 200 + 200 L liberam 320 L (FEFO); linha com nec, reservado, disponível e estado; resumo no topo | reserva concorrente (duas O.S. pelo mesmo saldo); R3, R5, R6 viram testes | cálculos de disponibilidade 8 → 1 (+1 adaptador); liberáveis na própria fazenda 2/5 (R0) medido de novo |
| RES-1 · pedir compra da falta | agrônomo, PCM, comprador, almoxarife | `dados_compras_mat.py`, `dados_manutencao.py`, `processo_os.py`, `processo_compras.py`, `processo_estoque.py`, `g2lib.js` | "Pedir compra · 1.140 kg de Ureia" na OS-0418 cria SC agrícola na fila do Comprador; recebido entra no lote da Santa Rita e fica reservado (CMD-44) para a OS-0418; OM usa a mesma função | solicitação duplicada; NOVO-1; NOVO-2; segregação; Planejar safra não pede complemento | cliques O.S. → solicitação ≥ 10 → 1; dias até a chegada: data viável fixa +7 → prazo do fornecedor |
| RES-2 · trocar produto | agrônomo | `processo_os.py`, `mip.js`, `agronomia.py` | lista do AG-01 dentro da O.S.; produto fixo sem troca; dose em branco com faixa; vN+1 sem aprovação | troca com carência incompatível; reentrada "a conferir" até a frente 3.1 | toques para trocar: tirar + incluir + dose (hoje) → escolher + dose + salvar |
| RES-3 · avulsa fora do plano | gestor, agrônomo, comprador | `dados_compras_mat.py`, `processo_compras.py`, `campo.py` (ocorrência "Falta de insumo") | 6 campos; impacto; soma à aberta; defensivo pede receituário | compra de defensivo sem receituário; fracionamento | campos visíveis; SCs duplicadas por mês |
| RES-4 · peça na OM corretiva | PCM, mecânico, almoxarife | `dados_manutencao.py`, `maquinas.py` (depois da MA-VINCULO, mesmos arquivos) | "Incluir peça" na corretiva com o mesmo estado; urgência por ativo parado; almoxarife real | remanejamento sem permissão | tempo OM aberta → peça reservada |
| RES-5 · packing | produção, almoxarife | `ben.js`, `processo_beneficiamento.py` | BOM mínimo do §6; falta de embalagem vira SC em 1 clique (BEN-2) | ordem do turno com falta | % de OB liberadas sem falta |

## 9. O que precisa do Gemini e do proprietário

**Gemini real, pelo conector do Codex** (decisão material de domínio; pacote sintético):
- Receituário na compra de defensivo pelo produtor: o que a Lei 14.785/2023 e a regulamentação vigente exigem na compra e na venda. **Default até a resposta:** defensivo só com receituário vinculado.
- Troca de produto com carência, reentrada e rotação IRAC/FRAC/HRAC: critérios do filtro e se rotação trava ou avisa. **Default:** carência e registro travam; rotação avisa; reentrada "a conferir" até a frente 3.1 (DEC-0910-09).
- Alçada da compra urgente: só se o Codex achar divergência material; para mim é política do proprietário.

**Proprietário** (só o que depende da fazenda, do dinheiro ou da autorização):
- **Alçada da compra urgente.** Default: a mesma alçada por valor; urgente não pula; aprova no celular com motivo e impacto (FL-27).
- **Quando é urgente.** Default: quando o prazo normal do grupo chega depois da data do documento.
- **Custo por dia parado.** Default: sem valor; a tela mostra "parado desde dd/mm", sem R$.
- **Fornecedor de emergência.** Default: só homologado; outro só com justificativa e um nível de alçada acima, sem cadastro automático.
- **Equipe pequena (quem pede também aprova ou recebe).** Default: permitido com revisão posterior obrigatória, como a DEC-1610-08.

## 10. Aplicar, deixar de fora, cortar

**Aplicar**
- `supCobertura` única com lote por fazenda e FEFO: é o que torna os botões confiáveis.
- "Pedir compra" que cria SC, não PC: 1 clique sem tocar dinheiro (P34; PRD 15.1).
- A API `sup*` no lugar de uma segunda máquina para O.S. e BEN: uma solução por problema (AGENTS §3.4).
- Papel Comprador e dono da falta pelo estado: o PRD 2 já prevê.
- Recebido reservado para quem pediu, como CMD-44 com validade no insumo: atende o pedido sem quebrar RSV-03.

**Deixar de fora (com gatilho)**
- Eficácia medida na fazenda no Trocar produto: fronteira com o Raio-X (EX-43). Gatilho: a crítica do Raio-X fechada; a coluna fica reservada.
- Custo por dia parado em R$: gatilho, o proprietário dar o valor ou a fonte.
- Demanda de embalagem pela previsão de colheita: gatilho, a RES-5 em produção de demonstração.
- Integração real de compras com o ERP: com o proprietário (AGENTS §2).

**Cortar**
- Coluna "em outro depósito ou fazenda" fixa: vira estado só quando há falta (cabe no celular).
- "Coberto por pedido a caminho" como coberto: pedido não é material; vira "A caminho".
- Dose mínima da bula preenchida na troca (como o AG-01 faz hoje): dose é decisão do RT (PRD 40.5).
- "Liberação parcial" da mesma versão: vira divisão da O.S. pela área coberta (RSV-03 c).
- Notificação a quem só pediu, a cada etapa: só "Chegou e está reservado" (pedido §8).

**Suposições e pendências**
- S1. Os números do cenário são sintéticos; a reprodução vale para a regra, não para a fazenda. Gatilho: piloto com dados fictícios em HML.
- S2. A contagem "antes" de cliques do agrônomo é por leitura do código, não medida no navegador. Gatilho: `/tmp/claude-0/q30.out` com FIM e no máximo um Chrome; aí medir no mesmo cenário (§11).
- P1. ENTREGA-FAZ P5 × reserva no recebimento para O.S.: o Codex reconcilia (§3).
- P2. Artigo do receituário na Lei 14.785/2023 e regulamento vigente: verificar na fonte oficial quando o Planalto responder; senão, Gemini e RT.
- P3. OS-0425 "liberada com falta": refazer como divisão ou rotular "legado". Gatilho: RES-0.
- P4. Reentrada não é conferida na O.S. nem no AG-01 (busca sem ocorrência em `processo_os.py` e `mip.js`). Gatilho: frente 3.1 (DEC-0910-09).

## 11. Reprodução e medidas "antes"

**Executado.** `python3 -B docs/integracao/V73/RESOLVE-1-CLIQUE/reproducao/repro.py --gen <gen37>` monta no Node 22 o motor real (perfis, cenário, núcleo da O.S., manutenção, Compras de materiais, `dados2.os_base` e `est_base`), como o `ma_regras_test.py`, sem navegador e sem gravar na pasta do gerador (conferido: `git status` só mostra `docs/integracao/V73/`). Saídas: `reproducao/saida_base_b989864.txt` e `reproducao/saida_int90_05947ad.txt`, idênticas fora do cabeçalho. Resultado: 15 confirmações, 0 "não reproduz", 0 exceções em cada uma.

| Caso | Observado (executado) |
|---|---|
| R0 retrato | A liberar com insumo: 2 de 5 liberáveis na própria fazenda; OS-0418 e OS-0502 bloqueadas; OS-0501 só com lote de outra fazenda |
| R1 OS-0418 | 0 lotes de Ureia; "Sem lote de Ureia 45% no Estoque."; dono "Suprimentos", que não está nos 13 papéis |
| R2 OS-0502 | "60.000 kg disponíveis para 96.940 kg"; falta 36.940 kg; 50.000 kg previstos em 30/09 (sem PC), depois da janela 25–27/09 |
| R3 OS-0501 | libera e reserva G26-14 e O26-05 (Santa Rita); a demanda única manda comprar 147,93 L e 24,66 L na Lagoa Grande |
| R4 OS-0425 | semente "Liberada · faltam 3.400 kg"; a mesma ordem em A liberar é recusada |
| R5 dois lotes | 200 + 200 L não liberam 320 L |
| R6 corrida | liberar a OS-0501 (Lagoa Grande, início 30/09) deixa a OS-0430 (Santa Rita, início 25/09) com 252,07 L para 320 L, sem aviso |
| R7 MA | 1 comando cria SC-041 (1 un, origem OM, ativo a03, urgência Alta pela criticidade); repetir não duplica; recebido fica reservado para a OM; mesma chave não soma |
| R7b segregação | Ana abre, cota, emite PC-202 e recebe a própria SC sem recusa |
| R7c beco | SC recebida, OM ainda com falta, "já foi enviada", "aguarda o recebimento da SC-041" |
| R8 avulsa | "Ureia 45%" vira Materiais gerais, PC numa ferragem, consumo direto na "Sede"; OS-0418 segue bloqueada |
| R9 idempotência | Compras: 12 kg com a chave de 10 kg = "repetido"; Estoque: mesma situação = conflito |

**Medidas "antes"**

| Medida | Antes | Rótulo |
|---|---|---|
| Cliques do agrônomo, O.S. com falta → pedido de compra | Sem caminho a partir da O.S. (o link do bloqueio vai ao Estoque, `processo_os.py:634`). Pelo Planejar safra: menu (1) → etapa Demanda (1) → "Atualizar SOL-2026-07" (1, `safra.js:1663`) → "Abrir Compra de insumos ›" (1) → "Solicitar cotações ›" (1) → "Enviar convites" (1) → "Comparar propostas ›" (1) → "Revisar aprovação ›" (1) → "Aprovar compra" (1) → confirmação (1) (`processo_compras.py:697-733`) = **10 cliques em 3 telas**, +1 se a safra não vier do filtro. O pedido sai para a safra inteira, sem urgência nem vínculo à O.S. | especificado (leitura do código); a SUP v2 contou 7 cliques só no trecho menu → emitir em `884620c` (`docs/suprimentos-simplificado/ESPECIFICACAO.md` §8), coerente |
| Cliques do PCM, OM com falta → SC | **1** ("Solicitar compra", `maquinas.py:430`) depois de abrir a OM; a SC nasce na fila de Compras | executado no motor (R7); clique na tela especificado |
| Comandos até a peça reservada (OM) | 4, em 3 papéis: PCM pede; comprador cota e emite; almoxarife recebe | executado (R7) |
| Chegada mais cedo possível | Insumo: data viável fixa = hoje + 7 dias (`dados2.py:1253-1255`, 30/09). Peça da OM-0235: proposta de referência F08 chega em 1 dia (24/09) | lido; R7 executado |
| O.S. em A liberar sem falta e na própria fazenda | 2 de 5 (R0) | executado |
| Compras urgentes por mês | sem dado: o protótipo não tem urgência para insumo | — |

**Segredos (executado):** Gitleaks 8.30.1, `gitleaks detect --no-git --source docs/integracao/V73/RESOLVE-1-CLIQUE --config .gitleaks.toml --redact` (configuração da `main`), "no leaks found". As cópias `pedido.md` e `anexo-analise.md` são verbatim (SHA-256 do corpo igual ao do original, citado no cabeçalho de cada uma); nenhum literal precisou de troca. Os scripts não escrevem chave de armazenamento: o navegador é simulado por um objeto em memória.
