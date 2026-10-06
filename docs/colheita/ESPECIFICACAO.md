# Colheita de ponta a ponta · especificação v1.1

**Pedido do proprietário (Adrianus, 05/10/2026, literal):** «adicione a previsão e programação de colheita (com monitoramento de frutos no campo)»; «ja tem previsto o apontamento de colheita? por cultura e talhão, gerando produtividade e produção total e por talhão/cultura e estoque de produto acabado conectando com comercial e estoque de produto acabado»; unidades pela DEC-0510-03.

- **Rótulo:** especificado. Nada de código foi alterado. "(executado)" marca o que saiu de comando rodado em 05–06/10/2026: `python3 docs/colheita/verificacao/contas.py` (FALHAS: 0), buscas de ID e sondas `node` do motor de carência sobre o `cenario.js_prefixo()` desta base.
- **v1.2 (06/10/2026):** correções da revisão adversarial do Codex (A-01 a A-19) em R-06, R-07, R-12 e R-18; decisões D-31 a D-37.
- **v1.1 (06/10/2026):** revisão por contraexemplo contra o código e o PRD (commit "spec COLH: revisão por contraexemplo"). Mudaram R-01, R-02, R-04 a R-06, R-10 a R-17, R-20, a semente (§6.2, §6.3, §6.5, §6.6), as telas COLH, PROD e MB-10, a bateria, os aceites e a tarefa do proprietário.
- **Base:** `9c617c4` (branch `claude/v44-colheita`). `gen37/` = `tools/prototipo/v37/gen37/`. PRD = `Safrion-Software-/docs/PRD.md` v3.9, "l.N" = linha. Decisões tomadas sem o proprietário: `DECISOES.md` (D-nn). Os números do §6 valem na demonstração sintética (`dados_lagoa_fonte.REAL = False`, a única fora do Mac); os testes rodam com `SAFRION_DADOS=sintetico`.
- **Fontes reaproveitadas, não repetidas:** unidades e bases físicas em `docs/culturas/UNIDADES-DE-MERCADO.md`; modelo de lote, reserva, rateio e estados de qualidade da `docs/beneficiamento/ESPECIFICACAO.md` §2.2, §3.1 e §3.3 (BEN); carência, pós-colheita demonstrativo e avaliação por destino do motor `dados_carencia.py`.

```text
ID / resultado útil / persona: COLH-1 / do talhão previsto ao lote reservado para um pedido, sem redigitar / agrônoma, encarregado de colheita, balança, qualidade, comercial
Requisitos do PRD e fora do escopo: CO-01..CO-04, CO-07 (l.973-1125), VE-04 (l.1359), MB-07 (l.2008), MB-10 (l.2068), cap. 43-45 e 49; fora: §9
Autor / revisor / integrador: Claude / Codex / integrador da branch única
Base / arquivos sob responsabilidade: 9c617c4 / areas/producao.py, producao.js, dados_producao.py, testes producao_*; trechos de §0 "Muda"
Aceite e comando de verificação: §8; bateria do §7.8
Estado / impedimento / próximo passo: especificado / nenhum para o código (D-01 a D-25 valem até o proprietário mudar) / P1
```

## 0. Mapa do existente

| Fica (reusar sem mudar o comportamento) | Onde |
|---|---|
| O.S. de colheita no Kanban de 5 fases, "Aprovar e liberar" (CMD-42 + CMD-06, PEND-OS-01), carência que impede liberar e iniciar | `areas/processo_os.py:443-446` (`osc_nova`), `:325` e `:394` (`carBloqColheita`), `:426` (encerrar por `cenPodeEncerrar`); `dados_carencia.py:384` |
| Apontamento de área web e app, com chave, duplicidade e fila sem sinal | `cenario.js:192-298` (`cenApontar` na l.264, `cenApSomado` na l.202), `:333` (`cenFecharTurno`), `:386` (`cenSinal`) |
| Lote de campo, situação de carência por talhão e avaliação por destino (calculadas ao vivo) | `dados_carencia.py:248` (`carLid`), `:292` (`carEstado`), `:304` (`carLotes`), `:327` (`carAvaliar`), `:418` (`carc_bula`), `:424` (`carc_liberar_lote`) |
| Pós-colheita demonstrativo do mamão da Lagoa Grande (fato que a semente respeita) | `dados_carencia.py:190-201` (CAR0: imersão do LC-0510-2 em 19/09; divisão do LC-0505-2 em 22/09; mistura LM-39-01 = LC-0510-2 + LC-0505-1 em 23/09) |
| Meta, área, plano e plantio do cultivo | `dados2.py:63-74` (Santa Rita), `dados_lagoa_safra.py:69-70` (Lagoa Grande, `meta`/`un_meta`) |
| Estado atômico e decimal | `cenario.js:15-20` (`cenMudar`), `:29-37` (`cenDec`, `cenQtd`) |
| Data operacional dos registros novos | `cenario.js:198` (`CEN_DIA_OP` = 26/09/2026, semana ISO 39); `CARD.hoje` = 23/09 continua só como "hoje" da carência |
| O.S. da Lagoa Grande que já são colheita | `dados_lagoa_safra.py:122` (OS-0505, Pivô 19, Em execução) e `:127` (OS-0510, Pivô 6, Encerradas); apontamentos em `:139-144` |
| Obrigações físicas da soja 26/27 e pedido da soja 25/26 | `areas/comercial.py:31-36` (CT203 12.000 sc, CPR CRE-0095 6.900 sc, BT-090 1.000 sc); `:310` (PV-030, saldo 4.000 sc) |

| Muda | Arquivo:linha | Passo |
|---|---|---|
| Cadastro de unidade por cultura (fonte única, D-03) | `dados_cad.py:30-32`: + `CULTURA_UN` | P1 |
| Tipo do local Packing (D-24) | `dados_cad.py:137`: `l8` tipo `'Armazém'` → `'Packing'` (nenhum teste lê o tipo; busca executada) | P2 |
| Local de recebimento da Lagoa Grande | `dados_cad.py:135-138`: + `('l11','Galpão de frutas Lagoa Grande','Lagoa Grande','Galpão','','')` | P2 |
| Estado único ganha `producao`; versão `v = v(base) + 1` (3 → 4 nesta base), com linha de histórico; `producao.js` no prefixo (D-22) | `cenario.py:80`; `:84-85` (`js_prefixo` concatena `producao.js` depois de `cenario.js`: toda página do estado, inclusive O.S., Mapa, Estoque e app, tem `prPodeEncerrar`) | P2 |
| Carga e contagem sem sinal entram uma vez ao voltar o sinal; encerrar colheita confere cargas | `cenario.js:395` (ramo `else` também procura em `c.producao`); `:400` (`cenPodeEncerrar` chama `prPodeEncerrar`) | P2 |
| Grupo "Produção" logo depois de "Agrícola" | `ui37.py:38-39` (MENU2); `build.py:40` (linha "App de campo" + MB-07, MB-10) e `:23` (MB-10det na lista de telas que deixam de ser geradas) | P3-P6 |
| O.S. nova de outra fazenda | `areas/processo_os.py:877`: `faz` e `saf` herdados da safra escolhida (hoje `faz:'Santa Rita'` fixo e `saf:'Mamão 2026/27'`: a ordem do Pivô 19 some do filtro Lagoa Grande · 2026/27) | P5 |
| Ordem nova pré-preenchida e duplicidade por semana na colheita de perene | `areas/processo_os.py:717-727` (`abrirHash` aceita `#nova:<cultivo>:<atividade>:<aaaa-mm-dd>`), `:869` (perene: chave cultivo + semana; também conta O.S. de colheita do mesmo talhão com "semana NN" no tipo, como a OS-0505, que não tem chave) | P5 |
| MB-07 e MB-10 ligados ao estado; dois cartões no MB-01; área de colheita no app só pelo MB-10 | `areas/mobile.py:169` (`mbMinhas` sem O.S. de colheita), `:790-812` (MB-07), `:907-972` (MB-10: aba Colheita no estado, aba Motorista igual; Balança, Recebedor e MB-10det saem), `:335` | P6 |
| VE-04 (oculto) lê reservas e reserva pela mesma função | `areas/comercial.py:294-360` | P7 |
| Regex de IDs do verificador de ações | `v37/ferramentas/acoes_duplicadas.py:15`: + `L\d\d-\d+`, `RS-`, `PV-`, `CT-`, `TK-`, `CNT-` | P3 |
| Testes cuja expectativa muda por regra nova (motivo no commit) | `mbtest.py:12, 85-99` (MB-10 por papel, MB-10det); `links_ocultos_test.py:31-37` (RESIDUAL: PROD → CO-06, seção de carência: "vivo, falta pôr na página visível") | P3, P6 |

**Novo:** `areas/producao.py` (3 páginas, com `cenario.js_prefixo()` + `dados_carencia.js_nucleo()`), `producao.js` (regras e comandos `pr*`), `dados_producao.py` (semente), `producao_unit.js` + `producao_unit_test.py` (node), `producao_fluxo_test.py` (navegador).
**Sai da função, sem apagar:** CO-01, CO-02, CO-02det, CO-03, CO-04 e CO-07 (`areas/colheita.py`) continuam ocultos e intocados (`cotest.py` e links do Mapa dependem deles); a função passa às páginas novas (D-12). CO-05, CO-05det, CO-06 e CO-06det ficam para a BEN.

## 1. Missão e princípios
1. **Um fato, um registro:** área vem do apontamento da O.S.; massa vem da pesagem; pós-colheita vem do motor de carência até a BEN; produção e produtividade são calculadas, nunca digitadas.
2. **Unidade da cultura na célula** (DEC-0510-03, DEC-0510-02): "0,96 t/ha", "480,61 sc", "18.400 L". Massa guardada em kg; conversão numa função só (`prUn`).
3. **Planejamento, execução e controle separados:** prever e programar (Previsão e colheita); pesar e receber (Cargas e recebimento); saber o que tenho e para quem (Estoque de produto).
4. **Trava só onde há dano nomeado** (§4); o resto é aviso com dono. A carência é lida ao vivo, nunca copiada.
5. **Herdar contexto:** O.S. herda fazenda, safra, cultivo, atividade e janela da previsão; carga herda talhão e O.S.; reserva sugere a quantidade; registro novo leva a data operacional (`CEN_DIA_OP`).

## 2. Menu e telas, antes → depois

| Antes | Depois (grupo **Produção**, entre Agrícola e Manutenção) | Natureza |
|---|---|---|
| CO-01 Previsão (oculta, texto fixo) · CO-02 Ordens OC-* paralelas às O.S. | **Previsão e colheita** `COLH.dc.html`: previsão por talhão e semana, programar, resultado por talhão e cultura | planejamento + controle por talhão |
| CO-03 Cargas · CO-04 Recebimento (ocultas, `Pt.act` que só mostra aviso) | **Cargas e recebimento** `CARGA.dc.html`: ticket, origem, descontos, lote | execução |
| CO-07 Estoque de produção (oculta, saca de 50 kg na soja) | **Estoque de produto** `PROD.dc.html`: físico, bloqueado, apto, reservado, disponível; pedidos | controle |
| O.S. de colheita no Kanban | igual (Agrícola › Ordem de Serviço); nenhuma coluna nova | execução |
| MB-07 e MB-10 com dados locais, fora do app | MB-07 Contagem de frutos e MB-10 Cargas e entregas (aba Colheita: área e cargas), no estado | execução (campo) |

## 3. Telas
Todas: master-detail (lista → painel do registro), filtros Fazenda e Safra no topo (DEC-2609-11), filtro rápido por situação e ordenação em todas as colunas de toda grade, inclusive Pedidos (G2), unidade junto do número, **uma** ação primária com verbo, escolhida pelo registro selecionado, estado e próximo passo em toda linha. Celular (390 px): abaixo de 480 px a lista vira cartões (identificação, número principal com unidade, situação e próximo passo), sem rolagem horizontal; a ação primária fica fixa no rodapé.

### 3.1 Previsão e colheita (`COLH`)
**Pergunta:** quanto vou colher, em que semana, de cada talhão, e quanto já colhi contra o previsto e a meta?
**Visão "Por talhão"** (árvore cultura › talhão; a linha mostra a safra no anual e o ciclo no perene; a linha da cultura soma na mesma unidade):

| Talhão · cultura | Área | Previsão | Colhido | Produtividade | Referência · desvio | Situação · próximo passo |
|---|---|---|---|---|---|---|
| Pivô 19 · Mamão Formosa | 75,11 ha | 72,9 t · S39 (v1) | 36,42 t | 0,48 t/ha · ciclo parcial | meta 50 t/ha/ano · ciclo aberto | Em colheita · OS-0505 · 1 carga a receber |

**Visão "Por semana"** (semana × produto; grão por safra): Semana | Produto | Previsão publicada | Colhido | Vendas futuras | Oferta livre | Desvio.
**Filtros:** cultura; situação (Sem previsão, Prevista, Programada, Em colheita, Colhida); horizonte (4 semanas | safra).
**Painel do talhão:** contagens (data, plantas da amostra, frutos por estádio, peso médio, quem) e rascunho por semana; versões publicadas; **passes** (O.S. de colheita: semana, fase, área do passe, produção, t/ha parcial ou final, previsão da semana e desvio); cargas do talhão; resultado (bruto de campo, descontos, comercial, área colhida, produtividade, desvio da meta e da previsão, custo).
**Ação primária** (uma, do talhão selecionado; no perene manda a próxima semana ainda sem ordem, no anual a safra): sem contagem → "Coletar contagem" (abre MB-07); rascunho não publicado → "Publicar previsão" (Ana); publicada sem O.S. → "Programar colheita SNN" (abre a O.S. nova pré-preenchida, §3.5); com O.S. → "Abrir OS-xxxx". Sem seleção: a mesma regra no primeiro talhão da lista em que ela dá passo (na semente, "Publicar previsão" do Pivô 19).
**Estados do talhão:** Sem previsão · Prevista (vN) · Programada (O.S. A liberar ou Liberadas) · Em colheita · Colhida (passe ou ciclo final).

### 3.2 Cargas e recebimento (`CARGA`)
**Pergunta:** o que chegou de cada talhão, quanto pesou e em que lote está?

| Carga · ticket | Origem | Data · hora | Líquido | Comercial | Lote · local | Situação |
|---|---|---|---|---|---|---|
| CG-2105 · TK-4490 | Pivô 19 · OS-0505 · 100 % | 21/09 09:40 | 12.180 kg | 12.180 kg | L39-131 · Galpão de frutas LG | Recebida |

**Filtros:** situação (A pesar · Recebida · Bloqueada · Estornada), cultura, talhão, data. **Painel:** pesagem (bruto, tara), descontos com a conta (grão), participação por talhão, lote e qualidade efetiva, trilha MP, chave e recibo.
**Ação primária:** "Pesar a CG-xxxx" se há linha A pesar selecionada; senão "Registrar pesagem". Formulário: origem por um toque entre as O.S. de colheita Liberadas, Em execução ou Em conferência (o término físico vai a Em conferência e os últimos caminhões ainda chegam; talhão herdado; "+ talhão" abre participação %, medida ou estimada); ticket; bruto e tara (teclado numérico, em kg, sem último valor); umidade % e impureza % só para grão; litros só para café; frutos só para coco e abacaxi; condição por um toque, sem valor herdado (Íntegra · Com avaria · Fora do padrão); local herdado da fazenda e da cultura; data do recebimento = `CEN_DIA_OP`, dia da colheita = o da carga do app ou informado. Linha Recebida: "Estornar" (motivo), no painel.

### 3.3 Estoque de produto (`PROD`)
**Pergunta:** quanto tenho de cada produto, quanto está livre para vender e para quem está reservado?

| Lote · produto | Local · validade | Físico | Bloqueado | Apto | Reservado | Disponível |
|---|---|---|---|---|---|---|
| L10-031 · Soja · grão · Padrão · Liberado | Silo 01 · — | 38.420 sc | 0 sc | 38.420 sc | 3.875 sc | 34.545 sc |

Árvore produto › lote, soma só dentro do produto. Filtros: qualidade (Liberado · Em inspeção · Bloqueado · Em processo · Esgotado), "com saldo" ligado de início.
**Seção Pedidos** (filtro por situação e tipo; ordenação): Pedido · cliente | Produto | Tipo · janela | Quantidade | Reservado | Falta | Situação (Sem reserva · Parcial · Coberto · Em risco · Futura: compromete a previsão).
**Painel do lote:** origem (cargas, talhões, O.S., lote de campo LC-), qualidade efetiva com o motivo (condição, carência ao vivo ou operação de pós-colheita), avaliação do destino do pedido (`carAvaliar`; link para a seção de carência da CO-06), reservas, movimentos MP.
**Ação primária** (uma, do lote selecionado): Em inspeção → "Liberar lote" (Qualidade, R-13); Liberado com pedido compatível e falta > 0 → "Reservar para pedido" (quantidade sugerida = mín(disponível, falta), editável). Sem seleção: "Reservar para pedido" do primeiro lote com disponível e pedido compatível. Cancelar reserva: na linha do pedido, com motivo.

### 3.4 App (390 px)
- **MB-07 Contagem de frutos:** escolhe o talhão (lista curta dos que estão em produção), conta por planta com botões +/− por estádio (Pintado: colher nesta semana · De vez: próxima · Verde desenvolvido: em 2 semanas), pesa a amostra (peso médio em kg); "Registrar e ir à planta N"; "Corrigir a última planta" (PRD MB-07); "Concluir talhão" grava a contagem. Não publica. Quem = operador do app.
- **MB-10 Cargas e entregas** (nome e papéis do PRD): aba **Colheita**, no estado: um cartão por O.S. de colheita Em execução (talhão, área feita e saldo, cargas do dia, impedimento de carência de `carBloqColheita` quando houver); "Apontar área" (ha e horas, o mesmo `cenApontar` com `origem:'app'` e chave do aparelho) e "Registrar carga" (veículo por toque, caixas ou kg estimados opcionais, talhões e %). Sem sinal: guarda e envia uma vez. Aba **Motorista**: igual a hoje (logística, §9). Balança, Recebedor e MB-10det saem: pesar e receber ficam no `CARGA`, um lugar só. O MB-03 deixa de listar O.S. de colheita (`mbMinhas`): dois caminhos de área no mesmo aparelho somariam duas vezes, porque `cenApDup` não compara app × app do mesmo operador.

### 3.5 Integrações de tela
- **O.S.:** `OS.dc.html#nova:lg19:q3:2026-09-28` abre o formulário de ordem nova com safra, fazenda, cultivo, atividade de colheita (a primeira do plano, só como modelo de operação) e janela preenchidos; Ana só confirma "Emitir". Em perene a ordem se chama "Colheita · semana NN", como OS-0505 e OS-0510. Aprovar e liberar pelo "Aprovar e liberar" da O.S. (PEND-OS-01). Nada muda no Kanban.
- **VE-04 (oculto):** seção "Reservas de produto" com os pedidos do estado e o mesmo comando `prReservar`. A linha estática do PV-030 no VE-04 continua até a frente Comercial (§9).

## 4. Regras (testáveis, com o dano evitado)
| # | Regra | Dano que a trava evita |
|---|---|---|
| R-01 | Quantidade guardada na base do lote: kg com 6 casas, meio para cima (mesma escala da BEN §3.4); café do campo em L; coco e abacaxi em frutos. Unidades de produção (t para frutas e cana, sc para grão e café), de produtividade, de estoque e de pedido, e a massa da unidade, vêm de `CULTURA_UN` (DEC-0510-03: "fica no cadastro da cultura e vale para ... estoque de produto e comercial"); o item do CD-06 com fator (Soja em grão e Café beneficiado em sc 60 kg, `areas/cadastros.py:689-690`) tem de coincidir, e a BEN R-B05 passa a ler `prUn`. Conversão só em `prUn`; saca é derivada, nunca guardada. Soma só entre lotes do mesmo produto. | Somar saca de 50 com saca de 60, ou litros com kg; o mesmo lote com duas contagens de sacas (produção e estoque errados, S2) |
| R-02 | Área colhida vem só de apontamento somado (`cenApSomado`: Provisório ou Conferido, com sinal) de O.S. de colheita do cultivo. Anual: mín(área do cultivo, Σ ha). Perene: passe = realizado da O.S.; ciclo = área do cultivo, a partir do primeiro passe (t/ha/ano, como o IBGE). | Produtividade inflada por passes repetidos, por passes parciais alternados (K15) ou por área sem apontamento |
| R-03 | Produção só nasce de carga Recebida. Área não gera kg; estimativa de caixas ou kg do campo nunca soma. | Estoque e produção fictícios |
| R-04 | Produtividade = produção na base física da cultura (UNIDADES-DE-MERCADO, coluna "Base física") ÷ área colhida, na unidade da cultura: grão, comercial corrigido (R-08); café, beneficiado (R-09); fruta, cana e hortaliça, massa líquida pesada; coco e abacaxi, frutos. O comercial aparece ao lado. Cultura e fazenda: Σ produção ÷ Σ área (ponderada, nunca média de médias). Passe e safra são parciais enquanto houver O.S. de colheita do período não Encerrada ou carga A pesar; o ciclo perene é parcial até o fim da safra. | Número errado para decidir (K07: 0,70 e não 0,72 t/ha); fruta que vai ao packing sem produtividade até a BEN |
| R-05 | Referência: anual, parcial e final contra a meta do Planejar safra; perene, o passe contra a última versão publicada antes do início da semana do passe, e o ciclo encerrado contra a meta t/ha/ano. Desvio % = (real − ref) ÷ ref. Passe parcial e ciclo aberto não mostram desvio. | Comparar 1 semana com meta anual, ou com previsão feita depois da colheita |
| R-06 | Carga tem origem: O.S. de colheita do talhão em Liberadas, Em execução ou Em conferência. Lote de campo = `carLid(O.S., dia do apontamento da mesma data)`; sem apontamento na data, a carga guarda O.S. e data e o LC- entra quando o apontamento existir. Mistura: participação % por talhão, soma 100, medida ou estimada; kg por origem pelo rateio acumulado da BEN §3.3, `q6(S·acumᵢ/E) − q6(S·acumᵢ₋₁/E)` (K04), numa função só (`prRateio`). Revisão A-08: a mistura é de uma cultura e uma fazenda (`prMixOrig` recusa; `prMixCompat` lista só O.S. compatíveis). | Produção no talhão errado; último caminhão sem onde registrar |
| R-07 | Comando com chave de quem inicia (formulário da web ou aparelho). Mesma chave e mesmo conteúdo = mesmo registro; mesma chave e outro conteúdo = conflito, nada grava. Ticket já Recebido na mesma fazenda: mesmo conteúdo = mesma carga; outro conteúdo = conflito. Revisão A-07: ticket comparado normalizado (`prTk`: maiúsculas, sem espaço, hífen, ponto, barra e prefixo TK). Revisão A-03, A-09, A-10: a chave nasce quando o formulário abre (data e acaso), nunca da contagem do estado, e morre no sucesso. | Produção em dobro (S2) |
| R-08 | Pesagem: tara ≥ 0, líquido = bruto − tara > 0. Grão: umidade e impureza obrigatórias; limpo = líquido × (1 − máx(0, imp − imp padrão) ÷ 100); comercial = limpo × (100 − u) ÷ (100 − u padrão) se u > u padrão, senão limpo. A conversão por matéria seca é uma função só (`prMs`), a mesma que a BEN-3 usa como `benEst`. Bruto, descontos e comercial aparecem separados. | Venda e estoque em sacas erradas |
| R-09 | Café recebe em L (e kg, se pesado), lote Em processo (vale sobre a R-10); produção em sc só pelo rendimento medido no beneficiamento; até lá "sc a apurar". | Saca presumida por fator fixo |
| R-10 | Estágio pelo tipo do local de destino (CD-06; o l8 Packing passa ao tipo Packing, D-24): Packing, Terreiro e Secador → Em processo (fora do vendável); Galpão, Armazém, Silo e Câmara fria → produto acabado. Lote cuja origem LC- tem imersão, divisão ou mistura no motor de carência (`carOps`) com data igual ou posterior ao recebimento → Em processo, com a operação como motivo (D-23); a BEN troca esse registro por ordem de processo. | Vender fruta que vai ao packing, ou a mesma fruta no galpão e na mistura de exportação |
| R-11 | Lote = produto + local + dia de recebimento + origem; carga mista gera lote próprio. ID `L<semana ISO>-<seq>` pela sequência única `c.producao.seq`, nunca reaproveitado. Mesma origem guarda o lote de campo (R-06). | Rastreio perdido; mistura de talhão bloqueado com liberado |
| R-12 | Entrada não é liberação (CO-04): quem recebe declara a condição, e a qualidade gravada é Liberado só com Íntegra; Com avaria ou Fora do padrão → Em inspeção. **A carência é lida ao vivo** (`prQualidade`): `carEstado(c, tid, dia da colheita, parcela, dia da colheita)` = `curso` → Bloqueado (motivo e prazo); `insuf`, ou O.S. fora de Liberadas, Em execução e Em conferência na data → Em inspeção (motivo e dono); senão vale a gravada. Fato que chega depois (apontamento enviado ao voltar o sinal, bula corrigida por `carc_bula`) muda a qualidade efetiva na hora; reserva já feita fica "Expedição impedida". Registrar nunca é impedido. Revisão A-01: o dia da colheita é obrigatório, sem valor padrão (atalhos Hoje, Ontem e dias apontados); origem em dia sem apontamento somado da O.S. (`prApDia`) → Em inspeção, dono o responsável da O.S. (data errada decidiria a carência). | Vender produto colhido na carência (lei, S1), também quando o fato chega depois do recebimento (sonda: colheita do Pivô 23 em 01/10 "cumprida" vira "curso até 19/10" com a bula de 30 dias, executado) |
| R-13 | "Liberar lote" (Em inspeção → Liberado): Qualidade (Marta, `CARD.quem.qual`; o mesmo papel da BEN R-E02); o comando reavalia a R-12 e recusa com a pendência e o dono (carência `insuf`: quem a pendência nomeia confere na origem). Bloqueado por carência só sai pela Qualidade com laudo (fora, §9). | Liberar por cansaço o que não foi conferido |
| R-14 | Saldos por lote, pela qualidade efetiva (R-10, R-12): físico = Σ movimentos; bloqueado = físico de Bloqueado ou Em inspeção; apto = físico de Liberado; reservado = Σ reservas Ativas; disponível = máx(0, apto − reservado). Em processo fica fora do acabado. | Vender o bloqueado ou o que não existe |
| R-15 | Reserva: pedido de pronta entrega ou venda futura, mesmo produto e classe, lote apto, avaliação do destino do pedido (`carAvaliar` da origem LC-; sem destino, MI-BR) diferente de Não conforme (Pendente mostra a falta e o dono sem impedir; a expedição exige a liberação comercial, §9), quantidade ≤ disponível e ≤ falta; dedução única. Cancelar exige motivo. Lote que deixa de ser apto mantém a reserva com "Expedição impedida". | Prometer o mesmo quilo duas vezes; vender acima do limite de resíduo (lei) |
| R-16 | Venda futura compromete a oferta publicada (semana ou safra), nunca o físico. São vendas futuras os pedidos futuros e as obrigações físicas do VE-05 (CT-203, CPR CRE-0095 e barter BT-090, lidos de `areas/comercial.py:31-36`). Reservar lote para ela move a dedução: oferta livre = oferta − (futuras − reservado delas). Oferta livre negativa aparece como déficit ao produtor. | Dupla dedução (ATP-04/07); obrigação de entrega fora da conta (K10) |
| R-17 | Previsão de fruta: rascunho por semana = área × plantas vivas/ha × (frutos do estádio ÷ plantas da amostra) × peso médio × (1 − perda). Estádio → semana: Pintado S, De vez S+1, Verde desenvolvido S+2. Sem contagem: meta × área (perene ÷ 52 por semana), rotulada "pela meta". Publicar (Ana) congela vN só das semanas que ainda não começaram; a semana em curso (Pintado) fica como orientação da O.S. aberta. Oferta, desvio e venda futura leem só a publicada. | Oferta inflada por contagem parcial; referência trocada depois da colheita |
| R-18 | O.S. de colheita: um cultivo por ordem; perene, uma por cultivo e semana. Encerrar exige nenhuma carga da O.S. A pesar ou sem sinal (`prPodeEncerrar`, presente em toda página do estado). Revisão A-06: carga A pesar registrada por engano sai por "Descartar" com motivo (`prDescartarCarga`, CARGA e MB-10). Revisão A-04: O.S. de colheita com carga A pesar ou Recebida não é cancelada sem execução. | Fechar a colheita com produção incompleta |
| R-19 | Carga Recebida não se edita: estorno com motivo devolve o efeito (MP de estorno, lote −kg). Recusa se a baixa deixa o lote abaixo do reservado; o ticket fica livre para novo registro. | Corrigir apagando rastro |
| R-20 | Custo R$/sc ou R$/t = custo realizado do cultivo no período ÷ produção na unidade da cultura, lido da fonte do Controle quando ela existir (CONTROLE-02 / CTL-4), sem cópia em `c.producao`; sem fonte, "sem custo realizado · Controle". | Custo por saca inventado; custo em dois lugares |

## 5. Estado único e integrações
`c.producao = { contagens[], previsoes{cultivo: [vN…]}, cargas{}, lotes{}, pedidos{}, reservas{}, movs[], seq{} }`. Campos de lote, reserva e pedido seguem a BEN §3.1 (D-05); a origem do lote de colheita é `origem[{carga, os, tid, lc, kg, modo}]`. Comandos em `producao.js`, sempre dentro de `cenMudar`: `prContar`, `prPublicar`, `prCarga`, `prReceber`, `prEstornar`, `prLiberarLote`, `prReservar`, `prCancelarReserva`. Consultas: `prUn`, `prMs`, `prRateio`, `prAreaColhida`, `prResultado`, `prQualidade`, `prSaldos`, `prOferta`, `prPodeEncerrar`. `producao.js` vai no prefixo do cenário (D-22); o que usa a carência roda só onde há `CARD` completo (COLH, CARGA, PROD, O.S., Mapa); o app tem o núcleo leve e não decide qualidade de lote.

| Módulo | Lê | Grava |
|---|---|---|
| O.S. (`c.ordens`) | tipo Colheita, talhão, safra, etapa, `ap` somados | nada; a ordem nasce pelo formulário da O.S. (§3.5) |
| App (`c.app`) | operador, sinal, fila | `cenApontar` (área; na colheita, só pelo MB-10); `prContar` e `prCarga` com chave; fila `CNT-`/`CG-` |
| Carência | `carEstado`, `carTals`, `carLid`, `carOps`, `carAvaliar` (ao vivo) | nada |
| Planejar safra | cultivo, área, meta, plano (DAP da colheita) | nada |
| Cadastros | `CULTURA_UN`, LOCAIS (tipo), clientes do CD-05 | nada |
| Estoque de insumos (`c.lotes`) | nada | nada (produto acabado nunca entra em `c.lotes`) |
| Comercial VE-04 e VE-05 | `c.producao.pedidos`, `reservas`; obrigações físicas (`areas/comercial.py:31-36`) | `prReservar`, `prCancelarReserva` |
| Controle (depois) | custo realizado do cultivo | nada |
| BEN (depois) | lotes Em processo | lotes de saída com `origem`; a produção comercial do talhão segue a genealogia |

Quem age (sem login; grava o papel, como `cenDevolver`; com o seletor de perfil da frente D, `G2_PERFIS`/`g2perfil`, quando integrado, o papel vem dele): contagem, área e carga do campo, o operador do app (hoje Marcos; Sérgio é o responsável da colheita); publicar previsão, emitir e aprovar O.S., Ana (agrônoma); liberar O.S., o gestor (Ana age como gestora; CMD-42 e CMD-06 gravados em separado, PEND-OS-01); liberar lote, Qualidade (Marta); pesar e receber, Lúcia (recebimento) na Lagoa Grande e Rui (almoxarife) na Santa Rita; reservar, Comercial.

## 6. Semente sintética (números fecham, executado em `verificacao/contas.py`)
**6.1 Unidades (`CULTURA_UN`, recorte da UNIDADES-DE-MERCADO):** Soja e Milho sc 60 kg/ha, base 14 % e MEI 1 %; Feijão sc 60 kg/ha, 14 % e 0,5 %; Café arábica sc 60 kg/ha beneficiado, campo em L; Mamão Formosa: produção em t e t/ha (perene, ciclo da safra), comercial em kg, vida útil 7 d; Laranja cx 40,8 kg/ha com t/ha ao lado; Coco e Abacaxi mil frutos/ha; Arroz RS e SC sc 50 kg (só no teste).
**6.2 Previsões e contagens:** Lagoa Grande, v1 publicada por Ana em 09/09: Pivô 6 S38 = 62.000 kg; v1 de 16/09: Pivô 19 S39 = 72.900 kg. CNT-0001 Pivô 19, 23/09, Sérgio: 20 plantas, Pintado 11, De vez 10, Verde 12, peso 1,20 kg; plantas vivas 1.700/ha; perda 5 % → rascunho S40 **72.781,59 kg**, S41 **87.337,908 kg** (K08); o Pintado orienta a OS-0505 (a S39 já começou) e não entra na publicação. Demais pivôs em produção sem contagem: rascunho pela meta (Pivô 2: 36.298,08 kg/semana, K09), não publicado. Santa Rita: v1 da soja 26/27 pela meta, publicada por Ana em 15/09, por safra (7 cultivos, **68.180 sc**, K10).
**6.3 O.S.:** nenhuma nova. OS-0510 (Pivô 6, Encerradas, 16/09 31,79 ha e 18/09 31 ha) e OS-0505 (Pivô 19, Em execução, 21/09 25 ha Conferido, 22/09 25 ha Provisório, 24/09 Previsto). Carência nesses dias: `sem` (executado, sonda `node`). Pivô 6 em 28/09: `insuf` (OS-0504 liberada sem apontamento): a ordem da S40 do Pivô 6 é emitida, e "Aprovar e liberar" é recusado com dono Wesley, "confere a aplicação" (executado, sonda `node`); a do Pivô 19 passa.

**6.4 Cargas** (tara 7.200 kg, Galpão de frutas Lagoa Grande, condição Íntegra, Recebidas por Lúcia, salvo a CG-2108):

| Carga · ticket | Dia | O.S. · lote de campo | Líquido | Lote |
|---|---|---|---|---|
| CG-2101 · TK-4471 / CG-2102 · TK-4472 | 16/09 | OS-0510 · LC-0510-1 | 15.280 / 15.210 kg | L38-131 = 30.490 kg |
| CG-2103 · TK-4478 / CG-2104 · TK-4479 | 18/09 | OS-0510 · LC-0510-2 | 14.960 / 14.870 kg | L38-132 = 29.830 kg |
| CG-2105 · TK-4490 / CG-2106 · TK-4491 | 21/09 | OS-0505 · LC-0505-1 | 12.180 / 11.940 kg | L39-131 = 24.120 kg |
| CG-2107 · TK-4502 | 22/09 | OS-0505 · LC-0505-2 | 12.300 kg | L39-132 = 12.300 kg |
| CG-2108 (do app, sem ticket) | 22/09 | OS-0505 · LC-0505-2 | A pesar · estimativa 590 caixas | — |

**6.5 Lotes, pedidos e reservas:** L38-131 expedido ao PV-037 (Frutas Real, mamão fruta de campo, 30.490 kg, entregue 17/09; físico 0, rastreio fica). L38-132, L39-131 e L39-132 ficam Em processo pelo CAR0 (imersão 19/09; mistura LM-39-01 em 23/09; divisão em 22/09; R-10): 66.250 kg de mamão fora do acabado; apto de mamão na semente = 0. Validades: L39-131 28/09; L39-132 29/09. L10-031 Soja · grão · Silo 01 · saldo de abertura da safra 2025/26 (sem talhão) = 2.305.200 kg = **38.420 sc**; RS-0001 de 232.500 kg (3.875 sc) para o PV-030 (Coop Grão Sul, Soja · padrão 25/26, pronta entrega set–out/26, saldo 4.000 sc = 240.000 kg; o mesmo da BEN K66) → disponível **34.545 sc**, falta do PV-030 7.500 kg. PV-036 Frutas Real, mamão fruta de campo, 10.000 kg, pronta entrega 24–26/09, Sem reserva. PV-038 Frutas Real, mamão, 30.000 kg, futura S41. Obrigações físicas da soja 26/27 (VE-05, lidas de `areas/comercial.py`, sc 60 kg pela D-19): CT-203 12.000 sc, CRE-0095 6.900 sc, BT-090 1.000 sc = **19.900 sc**. Movimentos: MP-1001 a MP-1007 (recebimentos), MP-1008 (expedição do L38-131), MP-1009 (abertura do L10-031), MP-1010 (RS-0001). `seq` = {cg: 2108, lote: {38: 132, 39: 132}, rs: 1, mp: 1010, cnt: 1}. IDs livres por busca (executado).

**6.6 Resultados esperados:** Pivô 6: passe S38 final **60,32 t · 0,96 t/ha**, −2,71 % da previsão v1 (K05); ciclo 0,96 t/ha, parcial. Pivô 19: passe S39 parcial **36,42 t · 0,73 t/ha**, selo "1 carga a receber"; ciclo **0,48 t/ha**; pesar a CG-2108 (12.050 kg) sem outro apontamento → passe **0,97**, ciclo **0,65** (K06). Mamão Lagoa Grande no ciclo: **0,70 t/ha** ponderado; a média simples daria 0,72 (K07). Soja 26/27: oferta publicada 68.180 sc; obrigações 19.900 sc → oferta livre **48.280 sc**; o L10-031 continua com 34.545 sc disponíveis (K10). S41 sem versão publicada: PV-038 aparece como déficit de 30.000 kg; publicada a v2 do Pivô 19, oferta livre S41 = **57.337,908 kg** (K14). Custo: "sem custo realizado" em todos (D-09). Tarefa do §8.1 (K13): apontar 25 ha na OS-0505 → produção 36,42 t igual, passe **0,49 t/ha**; pesar a CG-2108 (bruto 19.250, tara 7.200) → L39-133, 12.050 kg, Liberado, vence 29/09; passe **0,65 t/ha**; reservar a sugestão para o PV-036 → 10.000 kg, L39-133 disponível **2.050 kg**, PV-036 Coberto.

## 7. Passos de implementação (cada um deixa o protótipo funcionando)
1. **P1 · Unidades e contas:** `CULTURA_UN`; `producao.js` com `prUn`, `prMs`, `prCorrigir`, `prRateio` e produtividade; `producao_unit.js` com K01-K04, K11 e K15. Sem tela.
2. **P2 · Estado:** `dados_producao.py` (§6), `cenario.py` (`producao`, v+1, `producao.js` no prefixo), `dados_cad.py:137` (l8 Packing), `cenario.js:395` e `:400`; comandos `pr*` com R-02 a R-19; unidade K05-K10, K12-K14, idempotência, estorno, carência ao vivo (R-12), pós-colheita do CAR0 (R-10) e encerrar (R-18) também no `OS.dc.html`.
3. **P3 · Estoque de produto:** `PROD.dc.html`, grupo Produção com 1 item, regex do verificador, RESIDUAL do `links_ocultos_test.py` (PROD → CO-06).
4. **P4 · Cargas e recebimento:** `CARGA.dc.html` e 2º item.
5. **P5 · Previsão e colheita:** `COLH.dc.html`, 3º item, `#nova:` na O.S. com fazenda e safra herdadas e duplicidade por semana.
6. **P6 · App:** MB-07 e MB-10 (aba Colheita) no estado, `mbMinhas` sem colheita, cartões no MB-01, linha "App de campo" do canvas, MB-10det fora do build, `mbtest.py` com a expectativa nova.
7. **P7 · VE-04:** seção de reservas. Artefato atualizado com uma linha do que mudou.
8. **Bateria por passo** (com `SAFRION_DADOS=sintetico`): `python3 producao_unit_test.py`; `python3 build.py > /tmp/COLH-build.log; grep -c FALHA /tmp/COLH-build.log` (0); `python3 montar_render.py`; `python3 links_ocultos_test.py` (estrutural, depois do build); no navegador, um por vez: `env CHROME_BIN=/tmp/cloudchrome/chrome flock /tmp/cdpB.lock env CDP_GL=1 timeout 900 python3 <teste>` com `varredura.py`, `../ferramentas/acoes_duplicadas.py . /tmp/COLH-dup.json`, `producao_fluxo_test.py`, `os_cenario_test.py`, `app_cenario_test.py`, `ap_unico_test.py`, `mbtest.py`, `acao_unica_test.py`, `est_cenario_test.py`, `carencia_test.py`, `cotest.py`, `vetest.py`. Vermelhos conhecidos da base (lista da tarefa, não reexecutada aqui): componentes_ajustes, componentes_interacao, etapas_complemento, etapas_desktop, cal01, cd05v, intest, os_cenario (19/20), patest, psfix38test, saf38test, consumo_divergente (19/20); ficam listados no log, sem esconder. Antes do P2, rodar a bateria uma vez na base `9c617c4` e guardar o log, para comparar.

## 8. Critérios de aceite
| AC | Critério | Teste que prova |
|---|---|---|
| AC-01 | Menu: Produção logo depois de Agrícola, 3 itens, cada um abre a página; páginas sem erro | `producao_fluxo_test.py` (menu); `varredura.py` |
| AC-02 | Unidade de cada cultura e conversões K11; item do CD-06 coincide com `CULTURA_UN` (Soja em grão, Café beneficiado); nenhuma soma entre unidades | `producao_unit.js` U01 |
| AC-03 | Descontos de grão K01-K03, com bruto, descontos e comercial separados | U02 e painel da carga no fluxo |
| AC-04 | Apontar 25 ha sem carga não muda a produção; o passe S39 cai de 0,73 para 0,49 t/ha | U03; fluxo passo 3 |
| AC-05 | Mesma chave não duplica; outro conteúdo = conflito; ticket repetido = mesma carga | U04 |
| AC-06 | Mistura 60/40 em K04 pelo rateio da BEN, rastreio nos dois talhões | U05 |
| AC-07 | Produtividade K05-K07 e K15: passe, ciclo (área do cultivo), anual, parcial e final, ponderada; passes parciais alternados não dobram o t/ha | U06 |
| AC-08 | Íntegra e carência em dia → Liberado; `curso` → Bloqueado; `insuf`, avaria ou sem O.S. → Em inspeção; Liberar (Qualidade) recusa enquanto a pendência existir; bula corrigida por `carc_bula` depois do recebimento muda o lote para Bloqueado e a reserva para "Expedição impedida" | U07 (aplicação e bula injetadas no estado) |
| AC-09 | Saldos do L10-031: 38.420 / 0 / 38.420 / 3.875 / 34.545 sc | U08; tela PROD no fluxo |
| AC-10 | Reserva recusa lote não apto, acima do disponível ou da falta, e avaliação do destino Não conforme (laudo injetado acima do limite); cancelar sem motivo recusa | U09 |
| AC-11 | Venda futura não muda o disponível; oferta livre da soja 48.280 sc com as três obrigações do VE-05; S41 com déficit de 30.000 kg até a v2 | U10; visão Por semana |
| AC-12 | Contagem não publica; publicar congela vN só das semanas não começadas; K08 | U11; MB-07 no fluxo |
| AC-13 | Café: L, Em processo, "sc a apurar" | U12 |
| AC-14 | Estorno com motivo; recusa abaixo do reservado | U13 |
| AC-15 | Encerrar O.S. de colheita com carga A pesar é recusado com dono, no `OS.dc.html` | U14; fluxo |
| AC-16 | Carga sem sinal não aparece na web; ao voltar, entra uma vez | U15; fluxo do app |
| AC-17 | Tarefa do proprietário (§8.1) de ponta a ponta, com cliques e campos digitados medidos e gravados no log, dentro de 30 cliques e 5 campos (25 ha, horas, ticket, bruto, tara); acima disso falha | `producao_fluxo_test.py` |
| AC-18 | Toda grade com filtro e ordenação; unidade na célula; uma ação primária por tela e por estado | fluxo; `acoes_duplicadas.py` sem achado nas 3 páginas; `acao_unica_test.py` |
| AC-19 | 390 px: cartões, sem rolagem horizontal, primária visível | fluxo em 390×844 |
| AC-20 | Build 0 FALHA; testes de O.S., app, estoque, carência, links e comercial sem vermelho novo contra o log da base | bateria do §7.8 |
| AC-21 | Semente respeita o CAR0: L38-132, L39-131 e L39-132 Em processo com a operação como motivo; apto de mamão 0 antes da tarefa; carga do T7 no l8 Packing nasce Em processo | U16 |
| AC-22 | "Programar colheita S40" do Pivô 19 abre a ordem em Lagoa Grande · 2026/27, "Colheita · semana 40", A liberar; segunda ordem da mesma semana recusada; "Aprovar e liberar" da S40 do Pivô 6 recusado por carência sem dados (dono Wesley) | fluxo; `os_cenario_test.py` |

**8.1 Tarefa curta para o proprietário (homologação):** (1) em Produção › Previsão e colheita, escolha o Pivô 19, "Publicar previsão" e "Programar colheita S40"; confirme "Emitir"; (2) em Ordem de Serviço, "Aprovar e liberar" a ordem nova; (3) no app, MB-10 › Colheita › OS-0505, "Apontar área" 25 ha: a produção continua 36,42 t e o passe S39 cai de 0,73 para 0,49 t/ha; (4) em Cargas e recebimento, "Pesar a CG-2108" (bruto 19.250, tara 7.200, Íntegra): nasce o L39-133 e o passe vai a 0,65 t/ha; (5) em Estoque de produto, no L39-133, "Reservar para pedido" (PV-036, sugestão 10.000 kg) e confira o disponível de 2.050 kg.

## 9. Fora de escopo (condição de retorno)
| Item | Volta quando |
|---|---|
| Packing, secagem, café em coco e beneficiado; liberar lote Bloqueado com laudo; trocar o pós-colheita do CAR0 por ordem de processo | BEN-1 a BEN-4, sobre `c.producao` (D-05) |
| Expedição, romaneio de saída, transporte (LO-*), aba Motorista do MB-10, liberação comercial por destino (`carc_liberar_lote`) na expedição | frente Comercial e logística (#27) |
| Telas comerciais além do vínculo pedido↔lote; contrato, preço, faturamento; linha estática do PV-030 no VE-04 | idem |
| Pesagem no app (aba Balança) | balança no campo, se o proprietário pedir |
| Custo realizado por cultivo | CONTROLE-02 / CTL-4 publicar a fonte |
| Mapa de colheita e produtividade espacial (cap. 62) | importação de monitor de colheita pedida pelo proprietário |
| Qualidade da previsão (WAPE, viés, amostragem) além do desvio % | primeira safra com 6 semanas publicadas |
| Grão em secagem como "Em processo" | BEN-3 (hoje o comercial corrigido entra acabado, D-07) |
| Mostrar `CULTURA_UN` no CD-02 | próxima passada de Cadastros |
| Cinco referências do setor do módulo (AGENTS §3.3) | Codex registra antes do aceite; não bloqueia o código |

## 10. Implementação (executado em 06/10/2026, branch `claude/v44-colheita`)
- **Rótulo:** executado. Commits P1 a P7 nesta branch, cada um com build 0 FALHA; números da §6 conferidos em `producao_unit_test.py` (node) e no navegador (`producao_fluxo_test.py`).
- **Arquivos novos:** `gen37/producao.js` (regras e comandos `pr*`), `gen37/dados_producao.py` (catálogo PRDC e semente), `gen37/areas/producao.py` (COLH, CARGA, PROD e o painel do registro), `gen37/producao_unit.js` + `producao_unit_test.py`, `gen37/producao_fluxo_test.py`.
- **Desvios desta especificação, decididos na implementação:** D-26 a D-30 (DECISOES.md). Defeitos achados nos testes e corrigidos: nome `prNum` da tela por cima do leitor de número (regressão nova em `producao_unit_test.py`); impedimento de encerrar por carga a pesar mostrado como "sobra em custódia" na O.S. (AC-15 em `producao_fluxo_test.py erros`).
- **Defeito A-05 reproduzido antes da correção:** `producao_fluxo_test.py os` na base `9c617c4` → 0/7; na branch → 8/8.
- **Fora (inalterado, §9):** beneficiamento, expedição e logística, telas comerciais além do vínculo pedido ↔ lote, custo realizado (Controle), mapa de produtividade, as cinco referências do setor (Codex).
