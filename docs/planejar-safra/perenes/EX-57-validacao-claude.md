# EX-57 · Perenes: idade, fase e ciclo no plano agronômico · validação independente do Claude

- **Pedido:** `docs/integracao/V73/pedidos-1810/prompt-safrion-perenes-idade-ciclo.md` (sha256 `33edf8ee…`).
- **Base:** composição v135, `claude/v44-v135-osagrupa` @ `778c56fc`. Caminhos relativos a `tools/prototipo/v37/gen37/`.
- **Situação:** escrito sem ver o desenho do Codex; fica lacrado até ele publicar o dele.

## 1. Reprodução do comportamento atual (lido no código; o que foi executado está marcado)

| # | Afirmação do pedido | Resultado | Evidência |
|---|---|---|---|
| R1 | Uma regra única de data (`dataAtv`, espelhada em `soloDataAtv`) | **Ajustado.** A regra existe, mas há **6 cópias, e 2 divergem**. Ver o detalhe abaixo da tabela | `safra.js:21-24`, `solo.js:425-427`, `ocupacao.js:24-27`, `ocupacao.py:61-80`, `dados2.py:125-133`, `areas/inicio.py:277-282` |
| R2 | Na formação o DAP funciona: MAMAO-IMP vai de DAP −60 a DAP 270 | **Confirmado.** São 12 atividades, todas DAP (−60 … 270); a i12 "Início da colheita" é o DAP 270 | `dados_lagoa_safra.py:25-38` |
| R3 | Os planos de produção usam data com ano | **Confirmado.** Ver a lista abaixo da tabela | `dados_lagoa_safra.py:39-52`, `dados2.py:50-60` |
| R4 | Plano por DAP numa perene antiga gera datas antigas e o Planejar safra "só avisa" | **Ajustado.** A ocorrência antes do início da safra sai da capacidade, mas **entra no custo** ("inclui R$ … de antes de …"). Na LG2627 são 75 ocorrências antes do início, todas da MAMAO-IMP dos pivôs plantados em 2026 | `safra.js:299`, `:1279`, `:1324-1325`, `:1556-1558`; espelho `dados2.py:739-745` |
| R5 | A calagem do laudo diz "DAP −60 já passou" e usa a chegada de uma compra nova | **Ajustado.** A data usada não é a chegada de um pedido real: é `S0.viavel` = hoje + 7 dias (prazo nominal de reposição, 30/09/2026). A atividade incluída é gravada como DATA. Em plano todo DATA (CAFE-AR, MAMAO-PROD, MAMAO-F) a mensagem diz "DAP −60 não se aplica (plano sem DAP)" | `solo.js:199-214`; `dados2.py:1267-1269` |
| R6 | Não há idade nem fase; a troca de plano é manual; o mamão fica sem atividade depois do DAP 270 | **Confirmado**, com um agravante: a **fase já é calculada à parte em 6 lugares, com 3 conjuntos de limiares diferentes** para o mamão (90/240; 90/240/300; 240). Pivô 12 em renovação fica num dicionário solto (`RENOVACAO`). Há telas maquete sem função ("Editar atividade por idade", gatilho com segmentos DAP/Idade/DAF/DAC/Data, "Revisar idades" no PL-01) | `dados_irrigacao.py:121,140-147`; `dados_mip.py:87-97`; `areas/inicio.py:401-405`; `dados_carencia.py:168`; `dados_producao.py:22,30-33`; `dados_lagoa_sintetico/gerar.py:42-50`; `dados_lagoa_safra.py:71`; `engine.py:111,724-729`; `areas/planejamento.py:181-182` |
| R7 | A ocupação trata a perene como "sem fim" (OC_INF) | **Confirmado.** "Perene" é atributo da **cultura** (`CULTURAS` em `dados_cad.py:31-32`), não do cultivo. Concordo: está certo para a área | `ocupacao.js:5,18-22,45-46` |
| R8 | O Planejar safra já tem o vínculo da perene a uma nova safra | **Confirmado** pela R-24 "Vincular ciclo": cria o cultivo na nova safra com o plantio original, `v.ciclo`, **sem plano e sem colheita**. A especificação diz por quê: "copiar dobraria a demanda e levaria datas fixas de outra safra" | `safra.js:487,553-562,864`; `docs/planejar-safra/etapa-2-talhoes/ESPECIFICACAO.md` (R-24) |

**R1 · as duas cópias que divergem:**
- `dados2.data_atividade` (demanda e capacidade em Python): quando a colheita do plano é DATA, conta a partir do **plantio**. O JS conta da data da colheita.
- `inicio._data_atv` (o "previsto" do Mapa): DAPC e DANC sem `colheita` no cultivo devolvem **nada**, sem derivar a colheita do plano.

**R3 · os planos de produção:**
- MAMAO-PROD: 12 atividades DATA de 05/10/2026 a 20/01/2027, colheitas mensais e **nada de fev a ago/2027**.
- MAMAO-F: 3 atividades DATA, sem colheita.
- CAFE-AR: 4 DATA (15/10/2026 … colheita 20/05/2027) e 2 DAPC (+30 adubação; +45 esqueletamento).

**Achado novo A3 (lido no código, ainda não executado; reproduzir antes de dar a severidade):**
1. Aplicar à C1 vinculada na 2027/28 um plano com data com ano, como o CAFE-AR, gera ocorrências datadas de 2026/27.
2. Elas ficam "antes do início": fora da capacidade, mas dentro do custo.
3. A demanda de compra (`cal01.js:125-128`, `demFazenda`) filtra pela safra da ocorrência e não pela data. Então a necessidade de 2026/27 entra de novo na demanda da 2027/28.
4. Hoje só há o aviso "datas fixas fora desta safra" (`safra.js:461`).

É exatamente o dano que a R-24 quis evitar, agora pelo plano aplicado à mão. Se a reprodução confirmar, é **S2** (demanda duplicada).

## 2. Decisão por parte do modelo

| # | Parte do modelo | Decisão | Como |
|---|---|---|---|
| M1 | Plantio (ou recepa e replantio) e idade exibida | **Adotar** | Idade = data de referência do cenário − data de origem do ciclo vigente, mostrada como "7 anos e 8 meses". Uma função só, `perIdade` (a idade também alimenta o EX-53 e o Raio-X) |
| M2 | Fase com histórico | **Adaptar** | A fase mora no **ciclo** (o `v.ciclo` que a R-24 já cria), e não no cultivo de cada safra. As safras vinculadas compartilham fase, histórico e eventos sem copiar nada. Fases: formação · produção · renovação · encerrada. O tipo de renovação (recepa, esqueletamento, replantio) é um atributo, não mais uma fase. Histórico: `[{fase, desde, quem, motivo}]` |
| M3 | Eventos do ciclo com data prevista e real | **Adotar (F3)** | `ciclo.eventos[{tipo, safra, prevista, real, origem}]`. A colheita do cultivo passa a ser um evento, e o DAPC/DANC de hoje vira "dias em relação a um evento" |
| M4 | Gatilhos repetíveis | **Adaptar** | Os tipos estão listados abaixo da tabela |
| M5 | Plano declara a fase | **Adotar** | `plano.fase` ∈ {formação, produção, renovação, ciclo} ("ciclo" para as anuais). Plano de produção de perene com DATA com ano: **aviso** na biblioteca e na adoção, como pede o prompt, com a saída "trocar por dia e mês" |
| M6 | Parâmetros por cultura e cultivar, com fonte e RT | **Adotar** | No cadastro da cultura e da cultivar (já tem "Tipo de ciclo"): evento ou idade de entrada em produção, eventos que a cultura usa e duração típica das fases. **Os 6 limiares soltos passam a ler daqui.** Até o RT validar, ficam como "exemplo configurável · fonte: cenário sintético" |
| M7 | Mudança de fase proposta e confirmada | **Adotar (F4)** | Proposta por evento (1ª colheita registrada) ou idade, nunca automática. Confirmação por cultivo ou por grupo, com um registro por cultivo (quem, quando, motivo). As atividades em aberto do plano anterior aparecem para manter, cancelar ou reprogramar. **Não é aprovação de O.S.** e não fere a aprovação individual |
| M8 | Geração na safra | **Adaptar** | Ver as três regras abaixo da tabela |
| M9 | Onde aparece | **Adaptar** | F1 em três lugares: linha do cultivo no Planejar safra, cadastro do talhão e camada Estádio (**sem camada nova**: o Estádio já calcula a fase do mamão à parte e passa a usar a função única). Calendário J5, Frentes, EX-53 e Raio-X consomem a mesma função quando chegarem. As maquetes (`engine.py:111,724-729`; PL-01 "Revisar idades") são ligadas à regra ou removidas, sem ficar maquete |
| M10 | R-24 "Vincular ciclo" | **Adaptar (depois da F2)** | Com gatilhos repetíveis, o vínculo já **sugere o plano da fase vigente**, sem datas fixas e com confirmação, em vez de vir sem plano. Corta um passo e a redigitação (P25) sem o risco de duplicar |

**M4 · os tipos de gatilho.** É uma regra só, estendida. `dataAtv` passa a `ocorrDatas(cultivo, atividade, plano, safra)` e devolve uma **lista** `[{dt, prevista|real, origem}]`, com o motivo da data (ex.: "15 dias após a florada de 12/09/2027"). Tipos:
- DAP: fica para formação, renovação e anuais;
- DATA: fica para anuais;
- novos:
  - **DM**, dia e mês sem ano;
  - **DEV**, dias em relação a um evento do ciclo: colheita (absorve DAPC e DANC), florada, poda, recepa;
  - **DIS**, dias após o início da safra do cultivo;
  - **INT**, intervalo fixo com início e fim (produção contínua);
  - **IDM**, idade em meses;
  - **EST**, estádio confirmado em vistoria (F4).

**M8 · as três regras de geração:**
- As ocorrências saem dos gatilhos da **fase vigente no ciclo** naquela safra. DAP de formação nunca gera ocorrência numa perene em produção.
- Ocorrência fora do período da safra vira "fora desta safra · motivo", **só para consulta: fora da capacidade, do custo e da demanda**. Isso corrige o A3 e a inclusão em custo do R4 para perenes.
- Atividade de formação anterior ao início da safra numa lavoura em formação: proposta de separar o **custo de formação** do custo da safra de produção, para o custo por saca não carregar a implantação. **É ponto de domínio: vai ao Gemini (Q4) e ao RT antes de virar regra.**

## 3. Migração do cenário (sintético)

- **C1 · café:** fase produção desde a 1ª colheita (data a confirmar pelo RT; enquanto isso, "exemplo"). CAFE-AR fica assim:
  - k1–k3: DM 15/10, 15/12 e 20/01;
  - k4 colheita: evento colheita, previsto para DM 20/05;
  - k5 e k6: DEV colheita +30 e +45 (hoje já são DAPC).
- **Pivôs MAMAO-PROD e T7 (MAMAO-F):** fase produção.
  - Colheita: INT 30 dias (sem data com ano), de 10/2026 em diante, sem fim.
  - Fertirrigações: DM.
  - Isso preenche o buraco de fev a ago/2027.
- **Pivôs MAMAO-IMP:** fase formação, DAP como está. O DAP 270 "Início da colheita" passa a ser o evento **1ª colheita prevista**. A 1ª colheita registrada dispara a proposta de passar para MAMAO-PROD.
- **Pivô 12:** sai do dicionário `RENOVACAO` e vira fase renovação, tipo replantio, com data.
- **Planos em uso** não mudam no meio da safra sem nova versão publicada e adoção (EX-51 R7).

## 4. Fatias (reordenadas, com motivo)

| Fatia | Conteúdo | Motivo |
|---|---|---|
| **F0** | Regra de data única. Espelhos Python e Mapa iguais ao JS, com teste de **paridade JS × Python** sobre todos os planos × cultivos × safras (0 divergência). Reprodução do A3 por teste | Sem a regra única, o EX-57 multiplicaria por 6 a divergência que já existe |
| F1 | Ciclo com idade e fase (com histórico); função única de fase; parâmetros por cultura; exibição em 3 lugares; aviso de DATA com ano; maquetes ligadas ou removidas | Como no prompt |
| F2 | DM, INT, DIS e DEV colheita; regra "fora desta safra"; migração dos 3 planos; A3 corrigido se for reproduzido | Como no prompt |
| F3 | Eventos (florada, poda, recepa, 1ª colheita), DEV dos eventos e origem da data na O.S. | Como no prompt |
| F4 | Proposta de troca de fase, atividades em aberto, EST confirmado em vistoria; R-24 sugere o plano da fase | Como no prompt |

## 5. Aceite (medido antes do código)

Adoto os 6 critérios do prompt e acrescento:
1. Paridade da regra de data: JS × Python × Mapa × AG-02 iguais em todos os planos × cultivos × safras do cenário (0 divergência). A contraprova é a cópia antiga do `dados2.data_atividade`, que deve reprovar.
2. Uma perene vinculada à 2027/28 com o plano da fase tem **demanda de compra só da 2027/28**: nenhuma ocorrência datada fora da safra entra em custo ou demanda. A contraprova é a v135 (A3).
3. Uma função de fase: as 6 telas que hoje calculam fase à parte mostram a mesma fase para o mesmo cultivo.
4. A idade do C1 na data do cenário é "7 anos e 8 meses" (15/01/2019 → 23/09/2026).
5. Teste de virada de ano e bissexto para DM 29/02: proposta = 28/02 em ano não bissexto, com origem "29/02 → 28/02". **Decisão do RT.**

## 6. Pacote para o Gemini real (obrigatório; sem dados reais)

O Codex envia e registra.
- **Q1 · Fases:** formação · produção · renovação · encerrada servem para café, mamão, citros, banana, uva e cana? Contraexemplos esperados:
  - cana: corte (planta, soca, ressoca);
  - banana: gerações sobrepostas na touceira;
  - uva: poda de formação × de produção, e duas safras por ano no semiárido;
  - citros: alternância;
  - café: bienalidade, recepa e esqueletamento.
- **Q2 · Gatilhos:** DM, DEV (colheita, florada, poda, recepa), DIS, INT, IDM e EST bastam? Falta graus-dia (uva, citros, florada do café)?
- **Q3 · Entrada em produção:** por evento (1ª colheita) ou por idade, por cultura? Faixas típicas, com fonte.
- **Q4 · Custo de formação:** separar do custo da safra de produção (custo por saca sem a implantação)? Sem contabilidade no Safrion; só a separação gerencial.
- **Q5 · Florada como referência:** com várias floradas (café), qual vira o evento? Data prevista pelo histórico é aceitável?
- **Q6 · Produção contínua:** colheita do mamão e da banana por intervalo fixo serve ao planejamento, ou precisa da estimativa por contagem?

**RT (Ana):** valida os parâmetros por cultura e cultivar e o tratamento de 29/02 antes de virarem regra.

## 7. Três listas curtas

- **Aplicado (no desenho):**
  - fase e eventos no ciclo (sem cópia entre safras);
  - uma regra de data com lista de ocorrências e origem;
  - fora da safra = consulta;
  - função única de fase e parâmetros por cultura;
  - F0 antes de tudo.
- **Deixado de fora (com gatilho):**
  - EST (volta na F4, quando a vistoria registrar estádio);
  - graus-dia (volta se o Gemini indicar, Q2);
  - banana por planta ou geração (volta se o Q1 mostrar que o talhão não basta);
  - custo de formação separado (volta com Q4 + RT).
- **Cortado:**
  - camada nova no Mapa;
  - item novo na barra;
  - troca de fase ou plano automática;
  - limiar de fase fixo no código;
  - fase como campo do cultivo de cada safra (iria duplicar entre safras).

Autoria Claude; o Codex revisa e registra no checkpoint.
