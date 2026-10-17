<!-- Origem: anexo do proprietário (Adrianus), arquivo "anexo-insumos-analise.md" recebido no canal do Claude em 16/10/2026 junto do pedido. Cópia verbatim abaixo deste comentário, sem alteração. Atenção: as linhas citadas são do HTML publicado (OS.dc.html etc.), não da fonte; a confirmação na fonte vigente está em critica-claude.md §1. SHA-256 do original: 0bbabe88a9b0212cff5fbe53d3ca93fab526412f5ffe127715c02a494ea27539 -->

# Safrion v3 · Insumos da O.S. × estoque e compras: o que existe hoje

Análise do protótipo publicado ("Safrion — Do Talhão à O.S.", pasta `v3/`), feita só por leitura de código e dados (nenhuma tela executada). Datas do cenário: hoje operacional 23–26/09/2026.

Pedidos do proprietário:
- **A.** Na O.S. vista pelo agrônomo e pelo almoxarife, conferir rápido demanda × estoque de cada insumo e, em 1 clique, trocar o produto (outro registrado para a mesma cultura × alvo) ou pedir compra emergencial.
- **B.** Em Suprimentos, pedir compra avulsa de insumo fora do plano agronômico (problema inesperado na fazenda).
- **Extensão:** o mesmo olhar sobre Manutenção (preventiva, corretiva, peças) e Beneficiamento/packing, com o princípio "toda falta se resolve em 1 clique e vai direto ao processo e à pessoa que resolve (almoxarife para requisição, compras para compra), com prioridade e vínculo à origem".

Convenção: `arquivo:linha`. O código compartilhado (cenário, regras) aparece repetido em várias telas; cito a cópia de `OS.dc.html` quando a regra é comum.

---

## 0. Telas vivas e telas estáticas (importa para ler as evidências)

As telas que leem e gravam o **cenário compartilhado** (`CEN0` em `OS.dc.html:2351`, motor em `OS.dc.html:2358+`) são: OS, EST, CMP, MA, BEN, SAF, AG-01, AG-07, IN-04 (Mapa), MB-*, PSUP, PAGR e SU-03det.

As telas **SU-01, SU-02, SU-03, SU-04, SU-05, SU-05det, SU-06, SU-07, SU-07det, SU-08, SU-09, CA-04, PL-04, PL-05, IN-01, IN-02 e CD-06 não carregam o motor** (nenhuma tem `function cenGet`). São grades com dados fixos (`const GRIDS` na linha 58) e mensagens simuladas (`const SPEC`).

Consequência: há divergências entre elas e o cenário vivo. Exemplos:
- SU-03 mostra o lote N26-03 com "reservado 0 · disponível 8.000 kg" (`SU-03.dc.html:58`), mas o cenário tem `reservado: 8000` para a REQ-040 (`OS.dc.html:2351`).
- SU-07 diz que a REQ-036 deixa 3.640 kg "reservada no S58-0801" (`SU-07.dc.html:58`), mas o lote S58-0801 no cenário tem `reservado: 0`.

Toda conclusão abaixo sobre **comportamento** vem das telas vivas. As telas estáticas mostram a **intenção** de desenho.

---

## 1. O.S. por papel: o que aparece de cada insumo e que ações existem

### 1.1 Seção "Insumos" do detalhe da O.S. (`OS.dc.html`, igual para todos os papéis)

- Colunas: **Produto (grupo · origem) | Dose | Na ordem | Usado | Situação**, mais a trilha (`OS.dc.html:52`, modelo; `OS.dc.html:5982–5986`, valores `pan_ins`).
- "Situação" depende da fase:
  - **A liberar:** texto fixo do registro, por exemplo "Reserva ao liberar" ou "Reserva ao liberar · estoque 60.000 kg · pedido de 50.000 kg em 30/09" (OS-0502, dados `OSD` em `OS.dc.html:5021`). É texto semeado, **não é calculado**.
  - **Liberadas / Em execução:** `osInsSit` (`OS.dc.html:5186`), por exemplo "Reservado no Estoque · lote F26-02 · REQ-039 · faltam N", mais `cenInsumoSaldoTxt` (`OS.dc.html:2485`): "previsto para o saldo … · falta para terminar …". Esse "falta" é **consumo restante**, não falta de estoque.
- Trilha `osTrilha` (`OS.dc.html:5197`): Reservado → Entregue (com embalagens, ex. "13 × galão 5 L") → Confirmado no app → Consumido → Em custódia → Devolvido.

**O que a O.S. não mostra por insumo:** disponível no lote, reservado para outras O.S., local/depósito, validade, quantidade a caminho (pedido em trânsito, previsão), estoque em outra fazenda e falta numérica. Lote e requisição só aparecem dentro do texto da situação depois de liberada.

**Sinal de falta:** existe, mas só na fase A liberar e só como selo vermelho "Falta insumo · <produto>" (`OS.dc.html:5145`), com:
- dono "Suprimentos" e prazo "receber o insumo no Estoque" (`OS.dc.html:5146`);
- condição "A liberação aguarda <produto> no Estoque." (`OS.dc.html:5147`);
- dica do selo: "O saldo do lote no Estoque não cobre dose × área. Próximo passo: o Estoque recebe o insumo ou o agrônomo ajusta dose, área ou produto antes de liberar." (`OS.dc.html:195`).

A listagem de O.S. (`g_os`) mostra esse selo em Situação, com "Quem resolve" e "Próxima ação". Não há coluna de material.

### 1.2 Agrônomo (Ana · AL-02) e liberador (AL-01, gestor no padrão)

- **Primária em A liberar:** "Liberar para execução", que reserva os insumos. **Secundária:** "Ajustar antes de liberar" (`OS.dc.html:5463–5468`).
- Com falta, o painel mostra o bloqueio "Liberar bloqueado: saldo insuficiente de X: N disponíveis para M." e "Quem resolve: Suprimentos, recebendo o insumo no Estoque.", com o link "Ver saldos no Estoque" para `EST.dc.html` (`OS.dc.html:5481`).
- O ajuste continua possível e passa a "Salvar e liberar" quando o bloqueio é de estoque (`OS.dc.html:6051`: `ajLib … b.h==='EST.dc.html'`). No ajuste o agrônomo pode:
  - mudar a dose ou a área; a linha mostra "disponível N" (`OS.dc.html:6079`, `6107`);
  - **tirar** um produto e **incluir** outro do catálogo da fazenda. A lista "Incluir produto" traz classe e grupo de ação Agrofit e "N disponíveis" ou "sem saldo no Estoque", com os que têm saldo primeiro (`OS.dc.html:6083–6084`);
  - receber a trava de estoque por item: "Estoque: N disponíveis no lote X para M. Baixe a dose ou a área, ou troque o produto." (`OS.dc.html:5313`).
- **Não existe:** "pedir compra", "pedir transferência", "reservar parcial", "sugerir substituto equivalente" nem prioridade/urgência.

### 1.3 Almoxarife (Rui, Paula)

- **Na O.S.:** nenhuma ação própria sobre a falta. O almoxarife vê o mesmo painel; como não tem AL-01/AL-02, o primário vira o aviso "Liberar para execução: decisão de …" (`OS.dc.html:5501`). Depois de liberada, a O.S. oferece só o link "Retirada e fichas de execução" para o Estoque enquanto há saldo a entregar (`OS.dc.html:6011–6013`).
- **No Estoque (`EST.dc.html`, processo em 6 etapas, `EST.dc.html:5024`):** recebimento de NF, entrega por requisição, devolução, saldos por lote (físico, reservado, bloqueado, disponível, em custódia, validade), contagem e movimentos. Não há lista "O.S. aguardando insumo" nem ação de compra: a busca por "compra" na parte própria da tela não acha nada.
- **No app (`MB-05.dc.html`, Almoxarifado móvel):** mostra "Conferir e entregar · REQ-038 · Ureia 45% · Aguardando liberação da O.S. · Saldo apto 0 kg · bloqueado". Para o Fungicida A mostra "Conflito de reserva · a demanda da safra pede X · pendência de compra de Y (complemento no Planejar safra) · Conflito · decide o planejamento" (`MB-05.dc.html:6486–6490`). Ou seja, vê o conflito e manda ao Planejar safra, sem 1 clique.

### 1.4 Líder de campo e operador (app)

- `MB-02det` (Detalhe da ordem) mostra "Insumos · REQ" com situação, "Ver retirada" e "Registrar ocorrência". `OS-0424-app` mostra a retirada (produto, quantidade em embalagens, lote · validade, requisição) e o preparo do caldeiro.
- O início é bloqueado sem insumo entregue e confirmado (`cenIniFalta`, `OS.dc.html:2840–2851`): "Iniciar bloqueado: REQ sem entrega …" (dono almoxarife) ou "insumo esgotado … decide a área restante" (dono agrônomo).
- A ocorrência de campo (`CA-03`, `MB-04`) não tem o tipo "Falta de insumo". Os tipos são: Quebra de máquina, Praga acima do NC, Clima, Vazamento, Falha de aplicação, Acidente. "Almoxarifado · Rui" existe como destino (`CA-03.dc.html:58`).
- `CA-04` ("Minhas requisições") tem a gaveta "Solicitar material da ordem" com uma lista genérica e estática de itens (`CA-04.dc.html:52`).

### 1.5 PCP e programação

- `PL-04` "Liberar prontas" (estático) devolve o resultado por item: "OS-0418 continua: Ureia 45 % sem saldo apto (0 kg)" (`PL-04.dc.html:57`). Não aponta próximo passo de compra.
- `PL-05` lista o impedimento "Falta de insumo · Suprimentos · Rui · alternativa: atender a NEC-028 com as 50 t aptas" (estático, `PL-05.dc.html:58`).

### Resumo por dado

| Dado do insumo | Na O.S. (agrônomo/almoxarife) | Onde existe |
|---|---|---|
| Dose, total da ordem, usado | Sim | OS |
| Disponível no lote | Só no formulário Ajustar e na mensagem de bloqueio | `cenDisp` (`OS.dc.html:2515`) |
| Reservado (dela e de outras) | Não (só "Reservado · lote · REQ" depois de liberada) | EST, SU-03det |
| Lote, validade, local | Lote no texto; validade e local não | EST, `OS-0424-app` |
| Falta numérica | Só no texto do bloqueio | `osLibErro` |
| Em trânsito / previsão | Não (exceto texto semeado da OS-0502) | CMP (`CD.pedidos`), SU-05 |
| Estoque em outra fazenda | Não | Motor de demanda (`locFaz`) |
| Reservar | Automático ao liberar, tudo ou nada | `cenLiberar` |
| Requisitar | Automático ao liberar | `cenLiberar` |
| Trocar produto | Sim, manual, em Ajustar (só A liberar) | `osc_ajustar` |
| Comprar | **Não** | — |

---

## 2. Como a liberação confere o estoque hoje

1. **Prévia antes do clique.** `osLibErro` (`OS.dc.html:5208–5209`) roda a liberação numa cópia do cenário (`osc_libEfeito`) e transforma o erro no motivo do bloqueio. Por isso o selo e o bloqueio aparecem já na listagem, no Kanban e no painel (`OS.dc.html:5137–5148`).
2. **Ordem das travas** em `osc_libEfeito` (`OS.dc.html:5289–5305`): carência × colheita (`carBloqColheita`) → regra legal de uso (`osUsoErro`, RN-016) → `cenLiberar`.
3. **`cenLiberar`** (`OS.dc.html:2670–2689`), para cada insumo:
   - escolhe **um único lote** com `cenLote` (`OS.dc.html:2514`): o não vencido de **maior disponível**, **sem filtro de fazenda** e sem FEFO;
   - recusa com "Sem lote de X no Estoque." ou "Saldo insuficiente de X: N disponíveis para M.";
   - se passa, soma em `l.reservado`, cria ou refaz a REQ e grava o movimento `reserva`.

   O efeito é tudo ou nada: **não há reserva parcial nem divisão entre lotes**. O beneficiamento, por outro lado, divide (ver §8).
4. **Quando falta:** a ordem fica em A liberar, com selo vermelho, dono "Suprimentos" e o próximo passo "receber o insumo no Estoque". O único caminho de saída dentro da O.S. é o ajuste do agrônomo (dose, área ou produto).

   **Nada aciona Compras.** "Suprimentos" não é papel do catálogo: `G2_PAPEIS` (`OS.dc.html:775–781`) não tem comprador, e o próprio código diz "'Gestor de suprimentos' ainda não é papel do catálogo" (`CMP.dc.html:6175`).

Casos reais no cenário semeado (calculados pelas regras acima):
- **OS-0418 · Ureia 45% 1.140 kg:** não há lote de Ureia em `CEN0.lotes`, então a mensagem é "Sem lote de Ureia 45% no Estoque" e o selo "Falta insumo · Ureia 45%". PL-04 e MB-05 confirmam "saldo apto 0 kg".
- **OS-0502 · Calcário 96.940 kg:** o lote LG26-03 tem 60.000 kg, então falta. O texto semeado cita "pedido de 50.000 kg chega em 30/09", mas esse pedido não está no cenário e não entra na regra.
- **OS-0501 (Lagoa Grande) · Glifosato 480 e Óleo mineral:** os únicos lotes estão no "Almox. defensivos" da Santa Rita (G26-14, O26-05). `cenLote` não filtra fazenda, então a liberação **reservaria estoque de outra fazenda sem gerar transferência**.

   O motor de demanda sabe disso ("reserva em lote de outra fazenda cobre a ordem na fazenda dela", `OS.dc.html:2526–2528`). A O.S. não avisa.
- **OS-0425 · NPK 11.400 kg com lote de 8.000 kg:** aparece "Liberada" com "faltam 3.400 kg" (estado semeado). Pelas regras atuais **não seria possível liberar parcialmente**. SU-07 diz que a pendência é "coberta pela SOL-2026-07".
- **Proteção contra pegar o reservado de outra O.S.:** existe. A liberação usa só o disponível (`físico − quarentena − reservado`), e a entrega baixa só a reserva da própria requisição ("o resto está reservado para outras requisições", `OS.dc.html:2704`).

   O que **não** existe é proteção da **demanda futura** (O.S. ainda não liberada ou plano): quem libera primeiro leva. O conflito aparece no MB-05 "Conflito de reserva" e no Planejar safra, mas não na O.S. que está liberando.

---

## 3. Troca de produto e conferência de registro

**Existe (O.S.):** "Ajustar antes de liberar" (`osc_ajustar`, `OS.dc.html:5314–5338`), só em **A liberar** e só com o papel AL-02. O agrônomo tira um produto e inclui outro; o sistema grava a versão vN+1 com histórico ("tirado X; incluído Y z L/ha para <alvo>"). A cada produto incluído ou dose alterada roda `osUsoItem` (`OS.dc.html:5340–5352`), que confere:
- registro do produto × **cultura** de cada talhão ou parcela (inclusive o uso só em tratamento de sementes);
- **dose** dentro da faixa da bula (`cenUsoLegal`, `OS.dc.html:2498–2512`): "Dose fora da bula", unidade diferente, "Uso não conferido na bula" (alerta), registro cancelado, produto em reavaliação;
- **número máximo de aplicações** no ciclo;
- **alvo** × referência conferida, quando o produto veio da Consulta Agrofit ("não está na referência conferida");
- **carência:** conferida na liberação (`carBloqColheita`, `OS.dc.html:5290`) e na decisão MIP (AG-01).

**IRAC/FRAC/HRAC:** na O.S. aparece **só como informação** na lista de inclusão (`OSD.agf`: "Fungicida · FRAC 3 + FRAC 11"). Não há alerta de rotação na O.S. O alerta existe:
- no **AG-01**, decisão MIP: "Rotação: mesmo grupo … da última aplicação no talhão" (`AG-01.dc.html:5271`);
- no **AG-07**, Consulta Agrofit, seção "Rotação · cultura × alvo", que lista registros de **outro modo de ação** para o mesmo alvo (`AG-07.dc.html:5556–5571`).

**Pontes existentes:**
- **AG-07 "Usar na O.S.":** leva produto + cultura + alvo ao Ajustar de uma O.S. de pulverização A liberar daquela cultura (`AG-07.dc.html:5500–5516`, `location.href='OS.dc.html#<os>:usar=…'`). A dose fica em branco e o produto antigo não sai sozinho.
- **AG-07 "Na fazenda":** mostra lotes e disponível do mesmo ingrediente ativo e filtra "Com saldo / Sem saldo / Fora da fazenda" (`AG-07.dc.html:5055`, `5196–5203`, `5592`).
- **AG-01, painel de decisão MIP:** é o **melhor padrão existente para o pedido A**. Lista os produtos registrados para cultura × alvo, cada um com selo calculado ("Conferido", "Sem estoque", "Rotação", "Carência × colheita", "Dose fora da bula", "Máx. aplicações"), e escolhe em 1 toque (`AG-01.dc.html:5495–5507`). Quando falta estoque, só alerta: "Estoque: N de M · a liberação na O.S. aguarda a compra." (`AG-01.dc.html:5281`), sem ação de compra.

**Não existe:**
- sugestão automática de substituto na O.S.;
- troca depois de liberada: a REQ no SU-07 diz "Quantidade vem da versão aprovada da O.S.: excesso ou substituição exigem revisão" (`SU-07.dc.html:58`);
- troca para fertilizante, corretivo ou semente com critério de equivalência (garantia, nutriente). A regra legal ignora esses grupos (`OS.dc.html:5340`);
- "Usar na O.S." para ordens que não são de pulverização ou tratamento de sementes (`OS.dc.html` ~6070, CTL-5).

**Cadastro de insumo (CD-06):** os campos são nome, grupo, natureza de custo, unidade, embalagem, conteúdo, controle (lote/validade), preço, garantia ou densidade, local padrão e situação (`CD-06.dc.html:58`). **Não guarda** registro MAPA, ingrediente ativo, modo de ação nem alvos; isso vem da base Agrofit (`OSD.agf`, `CARD.prod`, `agrofit_*.json`). Também não tem estoque mínimo por item de insumo.

---

## 4. Fluxos de compra em Suprimentos

### 4.1 Compra de insumos (`CMP.dc.html`, tipo "ins", 6 etapas em uma tela; `CMP.dc.html:6069+`, `NOMES_` em 6563)

- **Origem única:** a **SOL** (solicitação) da safra, enviada pelo **Planejar safra** a partir da demanda líquida (`CD.sol` "SOL-2026-07 · Planejar safra · Safra 2026/27 · demanda de insumos", `CMP.dc.html:5851`).
  - A Compra não cria nem edita itens: "quem atualiza a SOL é o Planejar safra" (`CMP.dc.html:6098`).
  - Estados da linha (`demSolSit`, `SAF.dc.html:5244–5251`): A enviar → Em cotação → Complemento / Acima da demanda / Qualidade pendente / Coberto pelo recebimento / Coberto pelo estoque.
- **Etapas:** Escolha a safra → Confira a demanda → Solicite cotações → Compare propostas → Aprove a compra → Acompanhe a entrega.
  - **Cotação:** só a fornecedores homologados do grupo (`CD.forn`, F01–F07; F07 não homologado). Propostas trazem prazo, frete CIF/FOB, validade e pagamento (`CD.props`).
  - **Proposta padrão:** a de menor custo que chega antes da falta. Escolher outra exige justificativa (`CMP.dc.html:6317–6330`).
  - **Alçada por valor:** até R$ 50 mil, Gestor de suprimentos; até R$ 300 mil, Gerente da fazenda; acima, Direção (`CD.alcada`; também `CONF0.compras`, `OS.dc.html:1841`). A Ana (gestora) tem nível "Gerente da fazenda" (`CMP.dc.html:6174–6177`).
  - **Aprovação:** pendente → aprovada, devolvida ou recusada (`CMP.dc.html:6398–6416`) e emite PCs vinculados à safra e à SOL.
- **Pedidos e entrega:** `CD.pedidos` (`CMP.dc.html:5851`), por exemplo PC-088 KCl, estado Parcial, a entregar 40.000 kg, previsão 02/10. Recebimento: SU-06 (estático) e EST › Recebimento (vivo). O recebido separa apto e quarentena.
- **Urgência ou prioridade:** **não existe** para insumos.
- **Vínculo à O.S. ou ao problema:** só na memória de cálculo (eventos `evs` com "OS-0430 · Dessecação…"). A SOL não carrega a O.S. nem a vistoria de origem.
- **Prazo:** `CD.viavel = 2026-09-30` ("compra nova chega a partir da data viável", `CMP.dc.html:6132`) é **data fixa** (+7 dias); SU-01 calcula "Pedir até = data necessária − prazo do fornecedor − segurança".

### 4.2 Materiais, peças e serviços (`CMP.dc.html`, tipo "mat", V69; `CMP.dc.html:5716–5850`, 6565+)

- **Requisição SC-nnn** com origem `om` (da OM), `rep` (reposição por ponto de pedido) ou `avulsa` (`CM_ORIG`, `CMP.dc.html:6567`).
- **Urgência** Normal, Alta ou Urgente, que define "precisa até" = hoje + 3 dias (Alta) ou + 1 dia (Urgente) (`CMM.urgDias`, `CMP.dc.html:5714`, `5786`).
- **Etapas:** A cotar → Em cotação → Pedido emitido → Recebida (material) ou Aceita (serviço) (`CMM_ETAPAS`, `CMP.dc.html:5717`).
- **Quem faz** (`cmmPode`, `CMP.dc.html:5743–5750`): abrir avulsa, qualquer perfil com papel; repor, almoxarife/PCM/gestor; cotar e pedir, gestor/direção; receber, almoxarife/gestor; aceitar, PCM/gestor. O pedido passa pela alçada por valor: "Acima da sua alçada: … é decisão de …" (`CMP.dc.html:5802`).
- **A avulsa exclui insumo agrícola de forma explícita:** "requisição avulsa: tipo, item do almoxarifado ou descrição, quantidade, destino (ativo ou centro de custo), urgência e motivo. **Nunca safra ou cultura.**" (`CMP.dc.html:5774`).
  - O item vem só do catálogo da oficina (`c.itens`) ou é "Outro material (descrever)".
  - Material sem código vai direto ao centro de custo, como consumo e sem saldo (`CMP.dc.html:5818`).
  - Centros de custo: Oficina, Sede, Irrigação, Armazém e beneficiamento (`CMM.ccs`).
- Fornecedores e grupos próprios (`CMM.forn`: Peças, Lubrificantes, Materiais gerais, Serviços). Não há grupos de defensivo nem de fertilizante.

### 4.3 Compra fora do plano (pedido B)

**Não existe compra avulsa de insumo agrícola.** O único caminho hoje é indireto:
1. emitir uma O.S. (ou decidir controle no AG-01, que emite O.S. "A liberar" com receituário, `AG-01.dc.html:5324–5347`);
2. a O.S. entra na demanda da safra (`cenOsDem`, `OS.dc.html:2548`);
3. o Planejar safra mostra "Complemento" e a Ana envia o complemento da SOL ("Complemento SOL-…-Cn enviado com só a diferença", `SAF.dc.html:7717`);
4. a Compra de insumos refaz as 6 etapas.

Esse caminho não tem urgência, prazo curto, vínculo direto com a vistoria ou ocorrência, nem fornecedor de emergência. A data viável é fixa.

**Telas estáticas de Suprimentos:** SU-04 ("Solicitações e cotações": cotação por grupo da SOL + COT-113 rolamento da OM-0234), SU-05 (contratos, pedidos, cargas e exposição), SU-01 ("Necessidades e cobertura": demanda, disponível, recebimento firme, falta firme, pedir até). SU-01 traz uma linha "Parcela fora do plano S2627 = 54.908 kg" (KCl do contrato), que é cobertura de contrato, não compra avulsa.

---

## 5. Dados que alimentariam a conferência

| Dado | Existe? | Onde |
|---|---|---|
| Estoque por lote: físico, quarentena, reservado, validade, local | Sim (vivo) | `CEN0.lotes` (`OS.dc.html:2351`); `cenDisp` = físico − quarentena − reservado, vencido = 0 (`OS.dc.html:2515`) |
| Depósito → fazenda | Só no motor de demanda | `b.locFaz` em `cenOsDem`/`cenEstDem` (`OS.dc.html:2552`, `2599`); CD-06 tem fazenda por local (`CD-06.dc.html:58`, grade `g_loc`). `cenLote` não usa |
| Reservas por O.S. | Sim | `CEN0.reqs` (solicitado, entregue, consumido, devolvido, custódia, lote); movimento `reserva`; `cenResPropria` |
| Demanda futura (plano + O.S.) por data | Sim | `cenOsDem` + `demFazenda`/`cal01` (SAF, CMP, IN-04, MB-05) |
| Em trânsito (pedido, previsão, a entregar) | Sim, mas fora do cenário de lotes | `CD.pedidos` (`CMP.dc.html:5851`); `b.rec` em `cenEstDem` (recebimentos previstos menos o já conferido) |
| Quarentena / laudo pendente | Sim | `l.quarentena`, `quarRep`; "condicionada à qualidade, fora da compra" (`OS.dc.html:2585`) |
| Estoque mínimo / ponto de pedido | Só para itens da oficina | `CEN0.man.itens` min/max (`cmmRepos`); políticas de insumo só no SU-02 estático (segurança, prazo, método) |
| Prazo do fornecedor | Sim | `CD.props[grupo][].prazo`; `CMM.forn[].prazo` |
| Transferência entre depósitos/fazendas | Só estático | SU-08 "TR-0452 · Galpão Boa Vista → Almox. defensivos · em trânsito". Não há comando no motor |
| Registro de uso (cultura, alvo, dose, máx. aplicações, carência) | Sim | `CARD.prod[...].usos` (`OS.dc.html:5620`), `agrofit_*.json`, `MIPD.agf` |

---

## 6. Lacunas, riscos e as 12 melhorias mais valiosas (A e B)

### 6.1 Lacunas e riscos

1. **Falta sem dono acionável.** O dono "Suprimentos" não existe como papel (`G2_PAPEIS`; `CMP.dc.html:6175`). O bloqueio manda "receber o insumo no Estoque", mas ninguém é chamado a comprar.
2. **Estoque de outra fazenda reservado em silêncio** (`cenLote` sem fazenda, OS-0501). Não há transferência, frete nem aviso.
3. **Tudo ou nada em um lote.** Dois lotes que juntos cobrem a quantidade ainda bloqueiam. Não há liberação parcial por área. A OS-0425 "parcial" só existe na semente.
4. **Corrida pela demanda futura.** A primeira O.S. liberada consome o que o plano reservava para outra. O conflito só aparece no MB-05 e no Planejar safra.
5. **Compra emergencial de insumo inexistente.** O caminho via complemento da SOL é longo, sem urgência e com data viável fixa (+7 d).
6. **Risco de duplicidade se uma compra emergencial for criada sem integração.** O motor de demanda já desconta O.S., reserva, custódia e pedido (DEM-04, "conta uma vez com a ordem", `OS.dc.html:2618`). Um pedido avulso fora dele faria o Planejar safra pedir de novo.
7. **Compra sem receituário.** Nada na Compra exige receituário ou uso registrado para agrotóxico. A legislação federal (Lei 7.802/1989, art. 13) exige receituário agronômico na venda de agrotóxico ao usuário; convém validar com o jurídico ou RT. Uma compra "fora do plano" de defensivo precisa nascer de uma decisão do agrônomo (receituário, cultura × alvo).
8. **Alçada contornável.** A SC avulsa pode ser aberta por qualquer papel, e não há regra contra fracionamento (várias SCs < R$ 50 mil). A alçada só é conferida no pedido (`CMP.dc.html:5802`). Na compra de insumos, quem envia a SOL, cota e aprova pode ser a mesma pessoa (Ana).
9. **Troca de produto dispersa.** Pela O.S., o agrônomo precisa ir ao AG-07, voltar, tirar o antigo e digitar a dose. A boa lista de alternativas com selos (AG-01) não existe na O.S. Não há rotação IRAC/FRAC na O.S.
10. **Dados divergentes nas telas estáticas de Suprimentos** (SU-03 × cenário). O almoxarife pode decidir com saldo errado se essas telas forem para produção sem o motor.
11. **Em trânsito fora da conta da O.S.** O pedido com previsão (PC, 02/10) não aparece na O.S. Na OS-0502 o texto cita um pedido que o cenário não tem.
12. **Ocorrência sem tipo "Falta de insumo"** e sem roteamento para Compras.

### 6.2 As 12 melhorias (em ordem de valor)

1. **Quadro "Insumos × estoque" na O.S. (A).** Uma linha por insumo com Necessário · Disponível na fazenda · Reservado para esta O.S. · Em trânsito (data) · Falta, e um selo por linha (Coberto / Coberto com pedido em DD/MM / Falta N / Outra fazenda). Reusar `cenDisp`, `cenOsSup` (reservas e custódia) e `cenEstDem.recebDt`. *Evidência:* a O.S. hoje mostra só Dose/Na ordem/Usado/Situação (`OS.dc.html:52`) e o disponível aparece só no Ajustar (`OS.dc.html:6079`).
2. **"Trocar produto" em 1 clique na linha em falta (A).** Abrir a lista do AG-01: registrados para cultura × alvo da ordem, com selos Conferido / Sem estoque / Rotação / Carência / Dose (`AG-01.dc.html:5495–5507`), ordenados por "com saldo" e por outro modo de ação. Escolher já tira o antigo e preenche a dose mínima da bula, passando por `osUsoItem` e `osc_ajustar`. *Evidência:* hoje são tirar + incluir + digitar dose manuais, e o AG-07 fica fora da O.S.
3. **"Pedir compra urgente" em 1 clique na linha em falta (A + B).** Criar uma solicitação de insumo com origem O.S., quantidade = falta, precisa até = janela da O.S., urgência pela janela e fornecedor com menor prazo homologado no grupo. Reusar o padrão da Manutenção (`manSolicitar` → `cmmDaOm`, `MA.dc.html:5254–5258`): idempotente, só a falta, com vínculo. *Evidência:* o bloqueio de estoque não tem ação (`OS.dc.html:5481`).
4. **Compra avulsa de insumo em Suprimentos (B).** Abrir a SC avulsa ao grupo agrícola, retirando o "Nunca safra ou cultura" (`CMP.dc.html:5774`). Campos: item do catálogo de insumos, fazenda/depósito, motivo (ocorrência, vistoria, O.S.), urgência, precisa até. Defensivo exige vínculo a receituário/decisão do agrônomo (AL-02) antes de cotar.
5. **Integrar a compra avulsa à demanda única (B).** O pedido avulso e o pedido urgente entram em `b.rec`/`recebDt` como recebimento firme e na memória CAL-01, para que o Planejar safra **não** peça complemento do mesmo item. *Evidência:* a regra de não duplicar já existe para O.S./SOL (DEM-04/DEM-09, `SAF.dc.html:5244–5262`).
6. **Dono real da falta e rota por papel.** Criar o papel "Compras" (comprador) no catálogo e nas alçadas. O selo "Falta insumo" passa a ter dono Compras quando não há estoque e Almoxarife quando há estoque em outro depósito. *Evidência:* `G2_PAPEIS` sem comprador; `CMP.dc.html:6175`.
7. **Lote por fazenda e transferência em 1 clique.** `cenLote` filtra a fazenda da ordem. Se só há saldo em outra fazenda, a linha mostra "Disponível em Santa Rita: N" e a ação "Pedir transferência", que cria uma tarefa do almoxarife (SU-08 já desenha a TR com "em trânsito"). *Evidência:* OS-0501 × G26-14.
8. **Reserva multi-lote com FEFO e liberação parcial por área.** Reaproveitar `benAlocarCx` (`BEN.dc.html:3930`: um lote que cubra; senão divide, tudo ou nada) e permitir "Liberar N ha cobertos" com a pendência apontando para o pedido. *Evidência:* `cenLiberar` usa um lote; SU-07 descreve parcial para a OS-0425.
9. **Aviso de conflito com a demanda futura na liberação.** Antes de confirmar: "esta reserva deixa a OS-0431 (25/09) sem N; pedido chega em DD/MM". Ações: liberar mesmo assim (motivo) ou pedir compra. *Evidência:* conflito só no MB-05 (`MB-05.dc.html:6486–6490`).
10. **Prioridade e prazo realistas na compra de insumo.** Trocar a `CD.viavel` fixa pela data viável por fornecedor/grupo (prazo das propostas), urgência Normal/Alta/Urgente como na SC (`CMM.urgDias`) e escolha padrão "chega antes da falta" (já existe, `CMP.dc.html:6317`).
11. **Alçada e segregação na compra avulsa e urgente.** Quem pede não aprova o mesmo pedido acima do limite; somar SCs do mesmo item/fornecedor em 7 dias contra a alçada (antifracionamento); urgência "Urgente" exige motivo e origem. *Evidência:* alçada só no `cmmPedir` (`CMP.dc.html:5802`); avulsa aberta a qualquer papel (`CMP.dc.html:5748`).
12. **Origem rastreável e fila do comprador.** Ocorrência com tipo "Falta de insumo" e destino Compras; toda solicitação carrega origem (O.S./vistoria/ocorrência) com link de volta, e a O.S. mostra "Compra SC-x · fornecedor · chega DD/MM" no selo. PSUP ganha o card "O.S. aguardando insumo" (hoje tem só 4 indicadores de lote e requisição, `PSUP.dc.html:61`). *Evidência:* tipos de ocorrência em `CA-03.dc.html:58`; SOL sem origem por item.

---

## 7. Extensão · Manutenção (MA, PMAN, MOD-MAN, MB-09/MB-09det)

As telas MA-01..MA-05 redirecionam para `MA.dc.html` (visões Sem ordem, Ordens, Ativos e Planos).

### 7.1 O que existe

- **Peças com saldo livre e reserva por OM.**
  - Item da oficina com saldo, reservado e min/max (`CEN0.man.itens`).
  - `manLivreIt` = saldo − reservado (`MA.dc.html:5135`).
  - `manFalta` = peça da OM em A liberar cuja necessidade (qtd − já reservado) passa do livre (`MA.dc.html:5136`).
  - `manResTxt` diz **quem segura** a reserva ("reservada para a OM-xxx").
- **Preventiva antes de existir a OM.** Em Sem ordem, a coluna "Peças" mostra "Com saldo" ou "Falta N un · item" em vermelho (`ma_pecasTxt`, `MA.dc.html:5917–5927`). O plano mostra cada peça como "livre/falta" (`MA.dc.html:6354`).
- **Liberar a OM bloqueia na falta** com mensagem completa (`MA.dc.html:5247`): "Não liberada: falta peça · Kit (livre 0 de 1 un · …). Solicite a compra." ou "Aguarda o recebimento da SC-x." Ao liberar, a OM **reserva** as peças (`MA.dc.html:5249`).
- **1 clique para comprar.** Primária "Solicitar compra" na OM com falta (`MA.dc.html:6197`), via `manSolicitar` (`MA.dc.html:5254–5258`):
  - idempotente ("já foi enviada");
  - pede só **nec − livre**;
  - cria a SC em Compras com origem OM, ativo, motivo "Falta peça para liberar a OM …" e urgência pela criticidade (Alta → Alta, senão Normal) (`cmmDaOm`, `CMP.dc.html:5764`).
- **Recebimento.** O material que chega da SC fica **reservado para a OM** (D5, `manReceberSc`, `MA.dc.html:5265`) e a OM passa a "pronta para liberar".
- **Reposição.** `cmmRepos`/`cmmRepor` abrem a SC de reposição quando livre + pedido < mínimo (`CMP.dc.html:5758–5772`).
- **Execução.** Aplicar acima do planejado confere o disponível (`MA.dc.html:5378–5380`). Sobras são tratadas.

### 7.2 Lacunas

1. A **corretiva nasce sem peças**: "Sem peças nesta ordem (corretiva nasce sem peças até 'Incluir peça', PCMS Bloco 2)" (`MA.dc.html:52`). `manIncluir` aceita só tarefa (`MA.dc.html:5321`). Na quebra, que é o caso mais urgente, não há conferência de peça nem compra em 1 clique.
2. **O papel do almoxarife é simulado**: "Registrar recebimento (simulado · papel do Almoxarifado)", "Sobras … (simulado · papel do Almoxarifado)" (`MA.dc.html:5195`, `5287`, `5437`). Quem age é o PCM. Também não há "retirar peça no balcão" (entrega à custódia do mecânico), ao contrário dos insumos.
3. **Urgência não reflete o impacto.** Ativo bloqueado que para a produção (Trator T1, OM-0233 → OS-0420/OS-0431) gera SC "Alta" ou "Normal" pela criticidade da OM, não "Urgente". A SC-038 Urgente é seed.
4. **PMAN** não tem indicador "OM aguardando peça", e **MB-09det** (mecânico) mostra peças "planejado/aplicado" sem ação de pedir.
5. **Sem 2ª opção para peça.** Não há peça equivalente, compatível por modelo nem transferência entre oficinas/fazendas.

### 7.3 Melhorias (Manutenção)

- **M1.** "Incluir peça" na corretiva com o mesmo selo livre/falta e "Solicitar compra" na própria linha. A urgência vem do ativo: Bloqueado com produção afetada = Urgente.
- **M2.** Entregar o papel real ao almoxarife (receber SC, entregar peça à custódia do mecânico, receber sobra), tirando o "simulado" e alinhando com `cenEntregar`/`cenDevolver` dos insumos.
- **M3.** Card "OM aguardando peça · SC · chega DD/MM" no PMAN e na OM do app do mecânico, com link para a SC.
- **M4.** Gerar a SC já na **geração** da preventiva quando "Falta N" aparece em Sem ordem (antecipa o prazo do fornecedor), com 1 clique "Gerar ordem e pedir peças".
- **M5.** Peças equivalentes no cadastro (compatível com o modelo) e sugestão "trocar por equivalente com saldo" antes de comprar.

---

## 8. Extensão · Beneficiamento e packing (BEN, CO-05/CO-05det, PROD, CO-07)

### 8.1 O que existe

- A ordem de processo OB-nnn usa a mesma coleção das O.S. (`fam:'BEN'`). O **único material modelado é a caixa** "Caixa de mamão Formosa 10 kg" (`BENC.cx`, `OS.dc.html:3825`). As rotas (PACK-FRU, SEC-GRA, CAF-BEN) não têm lista de insumos. Busca no `BENC` por etiqueta, cera, fungicida pós-colheita, sanitizante ou insumo: 0 ocorrências.
- **Liberação:**
  - `benAutorizarLiberar` confere os impedimentos (`benImpedimentos`, `BEN.dc.html:4078–4090`): "Caixa…: N un disponíveis para M · Estoque", dono **almoxarife**, com link de recuperação;
  - **aloca em vários lotes** (`benAlocarCx`, `BEN.dc.html:3930`), tudo ou nada, e reserva uma REQ por lote.
- **Recuperação da falta** (`benFontesCx`/`benCaixasRec`, `BEN.dc.html:4004–4028`), em ordem de preferência:
  1. sobra de outra ordem ("Receber a devolução da OB-x", com link pré-preenchido no EST);
  2. NF de caixas a conferir;
  3. quarentena com laudo.
- **Na execução:** "Pedir mais caixas" (`benComplementar`, `BEN.dc.html:4313`) reserva o complemento, com recusa que explica as fontes.

### 8.2 Lacunas

1. **Sem compra.** Sem fonte, o texto diz "a compra de caixas entra no BEN-2" (`BEN.dc.html:4021–4022`, `4029`). Não há ação; o PC-096 (Embalagens Açu) aparece só como opção de recebimento no EST.
2. **A SC avulsa não serve.** Ela aceita centro de custo "Armazém e beneficiamento", mas caixa não é item do catálogo da oficina: entraria como "Materiais gerais" sem estoque (consumo direto, `CMP.dc.html:5818`) e não abasteceria o lote de caixas.
3. **Faltam os outros materiais de linha e pós-colheita** (fungicida/cera, etiquetas, pallets, sacaria do café e dos grãos, lenha ou gás do secador). Não há demanda nem falta para eles.
4. **Sem estoque mínimo nem demanda futura de caixas.** A previsão de colheita (CO-01) não gera necessidade de embalagem.

### 8.3 Melhorias (Beneficiamento)

- **B1.** "Pedir compra de caixas" em 1 clique no impedimento e no "Pedir mais caixas" quando não há fonte: SC com origem OB, quantidade = falta, precisa até = janela da OB, urgência pela janela e destino ao lote de embalagem (com estoque, não consumo direto).
- **B2.** Lista de materiais por rota (BOM: caixa, etiqueta, pallet, cera/fungicida pós-colheita, sacaria) com o mesmo impedimento e a mesma rota de recuperação.
- **B3.** Demanda de embalagem a partir da previsão de colheita publicada (AL-17/CO-01), com ponto de pedido e cobertura no SU-01.
- **B4.** Card "OB aguardando material" no painel de produção e no PSUP.

---

## 9. Princípio "toda falta em 1 clique, roteada a quem resolve": conformidade hoje

| Área | Detecta a falta | Mostra quem resolve | 1 clique para requisição | 1 clique para compra | Prioridade | Vínculo à origem |
|---|---|---|---|---|---|---|
| O.S. agrícola | Sim, na liberação (selo e bloqueio) | Sim, mas "Suprimentos" não é papel | Automática ao liberar (sem parcial) | **Não** | **Não** | — |
| Decisão MIP (AG-01) | Sim, selo "Sem estoque" por produto | Não ("aguarda a compra") | — | **Não** | Não | O.S. ← vistoria (orig) |
| Compra de insumos | Sim (demanda × estoque) | Planejar safra | — | Via SOL/complemento (vários passos) | Não | Só na memória de cálculo |
| Manutenção (OM preventiva) | Sim, antes e na liberação | Sim (PCM; almoxarife simulado) | Reserva ao liberar | **Sim** ("Solicitar compra") | Parcial (crit. da OM) | Sim (SC ↔ OM ↔ ativo) |
| Manutenção (corretiva) | Não (nasce sem peças) | — | — | Não (só avulsa manual) | Manual | Manual |
| Packing (caixas) | Sim, liberação e execução | Sim (almoxarife, com link) | Sim ("Pedir mais caixas") | **Não** ("BEN-2") | Não | — |
| Packing (outros materiais) | Não modelado | — | — | — | — | — |

**Referências internas que valem como padrão:**
- **Manutenção:** `manFalta` → `manSolicitar` → `cmmDaOm` → `manReceberSc`, com reserva ao chegar. É o modelo de "1 clique, só a falta, idempotente, com vínculo".
- **Beneficiamento:** `benAlocarCx` + `benFontesCx`. É o modelo de alocação multi-lote e de "de onde vem o que falta".
- **AG-01:** lista de alternativas com selos. É o modelo de "trocar produto".

O que falta é aplicar os três à O.S. agrícola e criar o papel e a fila de Compras para insumo.

---

## Suposições e limites

- Os comportamentos foram deduzidos do código e dos dados, sem executar as telas. Os casos OS-0418, OS-0501 e OS-0502 foram calculados aplicando `cenLote`/`cenDisp`/`cenLiberar` ao `CEN0` semeado. O estado salvo no navegador (localStorage `talhao-os-cenario-v1`) pode diferir.
- As telas SU-0x, CA-04, PL-04/05 e IN-01/02 são estáticas. Nelas descrevi a intenção, não a regra.
- Não deu para determinar, só pelo código, se haverá integração de compras com o ERP (o `CONF0.conexoes` cita "ERP · Sankhya traz pedidos de compra e notas fiscais", mas é simulado).
- A referência legal ao receituário (Lei 7.802/1989, art. 13) é para validação com o RT ou o jurídico, não é parecer.
