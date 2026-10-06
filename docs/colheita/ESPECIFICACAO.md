# Colheita de ponta a ponta · especificação v1

**Pedido do proprietário (Adrianus, 05/10/2026, literal):** «adicione a previsão e programação de colheita (com monitoramento de frutos no campo)»; «ja tem previsto o apontamento de colheita? por cultura e talhão, gerando produtividade e produção total e por talhão/cultura e estoque de produto acabado conectando com comercial e estoque de produto acabado»; unidades pela DEC-0510-03.

- **Rótulo:** especificado. Nada de código foi alterado. "(executado)" marca o que saiu de comando rodado em 05–06/10/2026: `python3 docs/colheita/verificacao/contas.py` (FALHAS: 0), buscas de ID e uma sonda `node` do motor de carência sobre o `cenario.js_prefixo()` desta base.
- **Base:** `9c617c4` (branch `claude/v44-colheita`). `gen37/` = `tools/prototipo/v37/gen37/`. PRD = `Safrion-Software-/docs/PRD.md` v3.9, "l.N" = linha. Decisões tomadas sem o proprietário: `DECISOES.md` (D-nn).
- **Fontes reaproveitadas, não repetidas:** unidades e bases físicas em `docs/culturas/UNIDADES-DE-MERCADO.md`; modelo de lote, reserva e estados de qualidade da `docs/beneficiamento/ESPECIFICACAO.md` §3.1 e §2.2 (BEN).

```text
ID / resultado útil / persona: COLH-1 / do talhão previsto ao lote reservado para um pedido, sem redigitar / agrônoma, encarregado de colheita, balança, comercial
Requisitos do PRD e fora do escopo: CO-01..CO-04, CO-07 (l.973-1125), VE-04 (l.1359), MB-07 (l.2008), MB-10 (l.2068), cap. 43-45 e 49; fora: §9
Autor / revisor / integrador: Claude / Codex / integrador da branch única
Base / arquivos sob responsabilidade: 9c617c4 / areas/producao.py, producao.js, dados_producao.py, testes producao_*; trechos de §0 "Muda"
Aceite e comando de verificação: §8; bateria do §7.8
Estado / impedimento / próximo passo: especificado / nenhum para o código (D-01 a D-22 valem até o proprietário mudar) / P1
```

## 0. Mapa do existente

| Fica (reusar sem mudar o comportamento) | Onde |
|---|---|
| O.S. de colheita no Kanban de 5 fases, "Aprovar e liberar" (CMD-42 + CMD-06), carência que impede liberar e iniciar | `areas/processo_os.py:443-446` (`osc_nova`), `:325` e `:394` (`carBloqColheita`); `dados_carencia.py:384` |
| Apontamento de área web e app, com chave, duplicidade e fila sem sinal | `cenario.js:192-298` (`cenApontar` na l.264), `:333` (`cenFecharTurno`), `:386` (`cenSinal`) |
| Lote de campo da carência (O.S. + dia) e situação por talhão | `dados_carencia.py:248` (`carLid`), `:313` (`carLotes`), `carEstado`, `carTals` |
| Meta, área, plano e plantio do cultivo | `dados2.py:63-74` (Santa Rita), `dados_lagoa_safra.py:69-70` (Lagoa Grande, `meta`/`un_meta`) |
| Estado atômico e decimal | `cenario.js:15-20` (`cenMudar`), `:29-37` (`cenDec`) |
| O.S. da Lagoa Grande que já são colheita | `dados_lagoa_safra.py:122` (OS-0505, Pivô 19, Em execução) e `:127` (OS-0510, Pivô 6, Encerradas); apontamentos em `:139-144` |

| Muda | Arquivo:linha | Passo |
|---|---|---|
| Cadastro de unidade por cultura (fonte única, D-03) | `dados_cad.py:30-32`: + `CULTURA_UN` | P1 |
| Local de recebimento da Lagoa Grande | `dados_cad.py:135-138`: + `('l11','Galpão de frutas Lagoa Grande','Lagoa Grande','Galpão','','')` | P2 |
| Estado único ganha `producao`; versão `v = v(base) + 1` (3 → 4 nesta base), com linha de histórico | `cenario.py:80` | P2 |
| Carga e contagem sem sinal entram uma vez ao voltar o sinal; encerrar colheita confere cargas | `cenario.js:395` (ramo `else` também procura em `c.producao`); `:400` (`cenPodeEncerrar` chama `prPodeEncerrar` se existir) | P2 |
| Grupo "Produção" logo depois de "Agrícola" | `ui37.py:38-39` (MENU2); `build.py:40` (linha "App de campo" + MB-07, MB-10) | P3-P6 |
| Ordem nova pré-preenchida e duplicidade por semana na colheita de perene | `areas/processo_os.py:717-727` (`abrirHash` aceita `#nova:<cultivo>:<atividade>:<aaaa-mm-dd>`), `:869` (chave + semana) | P5 |
| MB-07 e MB-10 ligados ao estado; dois cartões no MB-01 | `areas/mobile.py:790-812`, `:907-972` (sai o MB-10det local), `:335` | P6 |
| VE-04 (oculto) lê reservas e reserva pela mesma função | `areas/comercial.py:294-360` | P7 |
| Regex de IDs do verificador de ações | `v37/ferramentas/acoes_duplicadas.py:15`: + `L\d\d-\d+`, `RS-`, `PV-`, `CT-`, `TK-`, `CNT-` | P3 |

**Novo:** `areas/producao.py` (3 páginas), `producao.js` (regras e comandos `pr*`, carregado depois de `cenario.js`), `dados_producao.py` (semente), `producao_unit.js` + `producao_unit_test.py` (node), `producao_fluxo_test.py` (navegador).
**Sai da função, sem apagar:** CO-01, CO-02, CO-02det, CO-03, CO-04 e CO-07 (`areas/colheita.py`) continuam ocultos e intocados (`cotest.py` e links do Mapa dependem deles); a função passa às páginas novas (D-12). CO-05, CO-05det, CO-06 e CO-06det ficam para a BEN.

## 1. Missão e princípios
1. **Um fato, um registro:** área vem do apontamento da O.S.; massa vem da pesagem; produção e produtividade são calculadas, nunca digitadas.
2. **Unidade da cultura na célula** (DEC-0510-03, DEC-0510-02): "0,96 t/ha", "480,61 sc", "18.400 L". Massa guardada em kg; conversão numa função só (`prUn`).
3. **Planejamento, execução e controle separados:** prever e programar (Previsão e colheita); pesar e receber (Cargas e recebimento); saber o que tenho e para quem (Estoque de produto).
4. **Trava só onde há dano nomeado** (§4); o resto é aviso com dono.
5. **Herdar contexto:** O.S. herda cultivo, atividade e janela da previsão; carga herda talhão e O.S. em execução; reserva sugere a quantidade.

## 2. Menu e telas, antes → depois

| Antes | Depois (grupo **Produção**, entre Agrícola e Manutenção) | Natureza |
|---|---|---|
| CO-01 Previsão (oculta, texto fixo) · CO-02 Ordens OC-* paralelas às O.S. | **Previsão e colheita** `COLH.dc.html`: previsão por talhão e semana, programar, resultado por talhão e cultura | planejamento + controle por talhão |
| CO-03 Cargas · CO-04 Recebimento (ocultas, `Pt.act` que só mostra aviso) | **Cargas e recebimento** `CARGA.dc.html`: ticket, origem, descontos, lote | execução |
| CO-07 Estoque de produção (oculta, saca de 50 kg na soja) | **Estoque de produto** `PROD.dc.html`: físico, bloqueado, apto, reservado, disponível; pedidos | controle |
| O.S. de colheita no Kanban | igual (Agrícola › Ordem de Serviço); nenhuma coluna nova | execução |
| MB-07 e MB-10 com dados locais, fora do app | MB-07 Contagem de frutos e MB-10 Colheita: área e cargas, no estado | execução (campo) |

## 3. Telas
Todas: master-detail (lista → painel do registro), filtros Fazenda e Safra no topo (DEC-2609-11), filtro rápido por situação e ordenação em todas as colunas (G2), unidade junto do número, **uma** ação primária com verbo, estado e próximo passo em toda linha. Celular (390 px): abaixo de 480 px a lista vira cartões (identificação, número principal com unidade, situação e próximo passo), sem rolagem horizontal; a ação primária fica fixa no rodapé.

### 3.1 Previsão e colheita (`COLH`)
**Pergunta:** quanto vou colher, em que semana, de cada talhão, e quanto já colhi contra o previsto e a meta?
**Visão "Por talhão"** (árvore cultura › talhão; a linha da cultura soma na mesma unidade):

| Talhão · cultura | Área | Previsão | Colhido | Produtividade | Referência · desvio | Situação · próximo passo |
|---|---|---|---|---|---|---|
| Pivô 19 · Mamão Formosa | 75,11 ha | 72,9 t · S39 | 36,42 t · 50 ha | 0,73 t/ha · parcial | previsão S39 · aguarda o passe | Em colheita · OS-0505 · 1 carga a receber |

**Visão "Por semana"** (semana × produto): Semana | Produto | Previsão publicada | Colhido | Vendas futuras | Oferta livre | Desvio.
**Filtros:** cultura; situação (Sem previsão, Prevista, Programada, Em colheita, Colhida); horizonte (4 semanas | safra).
**Painel do talhão:** contagens (data, plantas da amostra, frutos por estádio, peso médio, quem) e rascunho por semana; versões publicadas; O.S. de colheita com fase e área; cargas do talhão; resultado (bruto de campo, descontos, comercial, área colhida, produtividade parcial ou final, desvio da meta e da previsão, custo).
**Ação primária:** o próximo passo do talhão selecionado, um por vez: "Coletar contagem" (abre MB-07) → "Publicar previsão" (Ana) → "Programar colheita" (abre a O.S. nova pré-preenchida, §3.5) → "Abrir OS-0xxx". Sem seleção: "Programar colheita" do primeiro talhão Prevista.
**Estados do talhão:** Sem previsão · Prevista (vN) · Programada (O.S. A liberar ou Liberadas) · Em colheita · Colhida (passe ou ciclo final).

### 3.2 Cargas e recebimento (`CARGA`)
**Pergunta:** o que chegou de cada talhão, quanto pesou e em que lote está?

| Carga · ticket | Origem | Data · hora | Líquido | Comercial | Lote · local | Situação |
|---|---|---|---|---|---|---|
| CG-2105 · TK-4490 | Pivô 19 · OS-0505 · 100 % | 21/09 09:40 | 12.180 kg | 12.180 kg | L39-131 · Galpão de frutas LG | Recebida |

**Filtros:** situação (A pesar · Recebida · Bloqueada · Estornada), cultura, talhão, data. **Painel:** pesagem (bruto, tara), descontos com a conta (grão), participação por talhão, lote, trilha MP, chave e recibo.
**Ação primária:** "Pesar a CG-xxxx" se há linha A pesar selecionada; senão "Registrar pesagem". Formulário: origem por um toque entre as O.S. de colheita Liberadas ou Em execução (talhão herdado; "+ talhão" abre participação %, medida ou estimada); ticket; bruto e tara (teclado numérico, em kg, sem último valor); umidade % e impureza % só para grão; litros só para café; frutos só para coco e abacaxi; condição por um toque, sem valor herdado (Íntegra · Com avaria · Fora do padrão); local herdado da fazenda e da cultura. Linha Recebida: "Estornar" (motivo), no painel.

### 3.3 Estoque de produto (`PROD`)
**Pergunta:** quanto tenho de cada produto, quanto está livre para vender e para quem está reservado?

| Lote · produto | Local · validade | Físico | Bloqueado | Apto | Reservado | Disponível |
|---|---|---|---|---|---|---|
| L39-131 · Mamão Formosa · fruta de campo · Liberado | Galpão de frutas LG · vence 28/09 | 24.120 kg | 0 kg | 24.120 kg | 0 kg | 24.120 kg |

Árvore produto › lote, soma só dentro do produto. Filtros: qualidade (Liberado · Em inspeção · Bloqueado · Em processo · Esgotado), "com saldo" ligado de início.
**Seção Pedidos:** Pedido · cliente | Produto | Tipo · janela | Quantidade | Reservado | Falta | Situação (Sem reserva · Parcial · Coberto · Em risco · Futura: compromete a previsão).
**Painel do lote:** origem (cargas, talhões, O.S., lote de campo LC-), carência e destino (link para a seção existente da CO-06), reservas, movimentos MP. Lote Em inspeção mostra "Liberar lote" (Ana, §4 R-13).
**Ação primária:** "Reservar para pedido" (lote selecionado → pedidos de pronta entrega compatíveis com falta > 0; quantidade sugerida = mín(disponível, falta), editável). Cancelar reserva: na linha do pedido, com motivo.

### 3.4 App (390 px)
- **MB-07 Contagem de frutos:** escolhe o talhão (lista curta dos que estão em produção), conta por planta com botões +/− por estádio (Pintado: colher nesta semana · De vez: próxima · Verde desenvolvido: em 2 semanas), pesa a amostra (peso médio em kg); "Registrar e ir à planta N"; "Concluir talhão" grava a contagem. Não publica.
- **MB-10 Colheita: área e cargas:** um cartão por O.S. de colheita Em execução (talhão, área feita e saldo, cargas do dia). "Apontar turno" (ha e horas, o mesmo `cenApontar` com `origem:'app'`) e "Registrar carga" (veículo por toque, caixas ou kg estimados opcionais, talhões e %). Sem sinal: guarda e envia uma vez.

### 3.5 Integrações de tela
- **O.S.:** `OS.dc.html#nova:lg19:q3:2026-09-28` abre o formulário de ordem nova com safra, cultivo, atividade de colheita e janela preenchidos; Ana só confirma "Emitir". Em perene a ordem se chama "Colheita · semana NN", como OS-0505 e OS-0510. Nada muda no Kanban.
- **VE-04 (oculto):** seção "Reservas de produto" com os pedidos do estado e o mesmo comando `prReservar`.

## 4. Regras (testáveis, com o dano evitado)
| # | Regra | Dano que a trava evita |
|---|---|---|
| R-01 | Quantidade guardada na base do lote: kg com 6 casas, meio para cima (mesma escala da BEN §3.4); café do campo em L; coco e abacaxi em frutos. Unidades de produção (t para frutas e cana, sc para grão e café), de produtividade e comercial (estoque e pedido), e a massa da unidade, vêm de `CULTURA_UN`; conversão só em `prUn`; saca é derivada, nunca guardada. Soma só entre lotes do mesmo produto. | Somar saca de 50 com saca de 60, ou litros com kg (produção errada, S2) |
| R-02 | Área colhida vem só de apontamento somado (Provisório ou Conferido, com sinal) de O.S. de colheita do cultivo. Anual: mín(área do cultivo, Σ ha). Perene: por passe = realizado da O.S.; no ciclo = mín(área do cultivo, maior realizado de um passe). | Produtividade inflada por passes repetidos ou por área sem apontamento |
| R-03 | Produção só nasce de carga Recebida. Área não gera kg; estimativa de caixas ou kg do campo nunca soma. | Estoque e produção fictícios |
| R-04 | Produtividade = produção comercial ÷ área colhida, na unidade da cultura. Cultura e fazenda: Σ produção ÷ Σ área (ponderada, nunca média de médias). Parcial enquanto houver O.S. de colheita do período não Encerrada ou carga A pesar; final depois. | Número errado para decidir (K07: 0,86 e não 0,84 t/ha) |
| R-05 | Referência: anual, parcial e final contra a meta do Planejar safra; perene, cada passe contra a previsão publicada da semana e o ciclo encerrado contra a meta t/ha/ano. Desvio % = (real − ref) ÷ ref. Passe parcial não mostra desvio. | Comparar 1 semana com meta anual |
| R-06 | Carga tem origem: talhão com O.S. de colheita. Mistura: participação % por talhão, soma 100, medida ou estimada; kg por origem = rateio em 6 casas, o último leva o resto (K04). | Produção no talhão errado |
| R-07 | Comando com chave de quem inicia (formulário da web ou aparelho). Mesma chave e mesmo conteúdo = mesmo registro; mesma chave e outro conteúdo = conflito, nada grava. Ticket já Recebido na mesma fazenda: mesmo conteúdo = mesma carga; outro conteúdo = conflito. | Produção em dobro (S2) |
| R-08 | Pesagem: tara ≥ 0, líquido = bruto − tara > 0. Grão: umidade e impureza obrigatórias; limpo = líquido × (1 − máx(0, imp − imp padrão) ÷ 100); comercial = limpo × (100 − u) ÷ (100 − u padrão) se u > u padrão, senão limpo. Bruto, descontos e comercial aparecem separados. | Venda e estoque em sacas erradas |
| R-09 | Café recebe em L (e kg, se pesado), lote Em processo; produção em sc só pelo rendimento medido no beneficiamento; até lá "sc a apurar". | Saca presumida por fator fixo |
| R-10 | Estágio pelo tipo do local de destino (CD-06): Packing, Terreiro e Secador → Em processo (fora do vendável); Galpão, Armazém, Silo e Câmara fria → produto acabado. | Vender fruta que ainda vai ao packing |
| R-11 | Lote = produto + local + dia de recebimento + origem; carga mista gera lote próprio. ID `L<semana ISO>-<seq>` pela sequência única `c.producao.seq`, nunca reaproveitado. Mesma origem guarda o lote de campo `carLid(os, dia)`. | Rastreio perdido; mistura de talhão bloqueado com liberado |
| R-12 | Entrada não é liberação (CO-04): o lote só nasce Liberado quando quem recebe declara a condição Íntegra **e** a carência na data da colheita (`carEstado(c, talhão, dia, parcela, dia)`) não é `curso` nem `insuf`. `curso` → Bloqueado (motivo e prazo); `insuf`, condição Com avaria ou Fora do padrão, ou talhão sem O.S. de colheita Liberada ou Em execução na data → Em inspeção (motivo e dono). Registrar nunca é impedido. | Vender produto colhido na carência (lei, S1) |
| R-13 | "Liberar lote" (Em inspeção → Liberado): Ana; o comando reavalia a R-12 e recusa com a pendência e o dono se ela continua. Bloqueado por carência só sai pela Qualidade com laudo (fora, §9). | Liberar por cansaço o que não foi conferido |
| R-14 | Saldos por lote: físico = Σ movimentos; bloqueado = físico de Bloqueado ou Em inspeção; apto = físico de Liberado; reservado = Σ reservas Ativas; disponível = apto − reservado, nunca negativo. Em processo fica fora do acabado. | Vender o bloqueado ou o que não existe |
| R-15 | Reserva: pedido de pronta entrega, mesmo produto e classe, lote Liberado, quantidade ≤ disponível e ≤ falta; dedução única. Cancelar exige motivo. Bloquear lote reservado mantém a reserva com "Expedição impedida". | Prometer o mesmo quilo duas vezes |
| R-16 | Venda futura compromete a oferta publicada (semana ou safra), nunca o físico. Reservar lote para ela move a dedução: oferta livre = oferta − (futuras − reservado delas). Oferta livre negativa aparece como déficit ao produtor. | Dupla dedução (ATP-04/07) |
| R-17 | Previsão de fruta: rascunho por semana = área × plantas vivas/ha × (frutos do estádio ÷ plantas da amostra) × peso médio × (1 − perda). Estádio → semana: Pintado S, De vez S+1, Verde desenvolvido S+2. Sem contagem: meta × área (perene ÷ 52 por semana), rotulada "pela meta". Publicar (Ana) congela vN; oferta, desvio e venda futura leem só a publicada. | Oferta inflada por contagem parcial |
| R-18 | O.S. de colheita: um cultivo por ordem; perene, uma por cultivo e semana. Encerrar exige nenhuma carga da O.S. A pesar ou sem sinal (`prPodeEncerrar`). | Fechar a colheita com produção incompleta |
| R-19 | Carga Recebida não se edita: estorno com motivo devolve o efeito (MP de estorno, lote −kg). Recusa se a baixa deixa o lote abaixo do reservado; o ticket fica livre para novo registro. | Corrigir apagando rastro |
| R-20 | Custo R$/sc ou R$/t = custo realizado do cultivo no período ÷ produção comercial na unidade da cultura; só com `c.producao.custos[cultivo]`; sem fonte, "sem custo realizado · Controle". | Custo por saca inventado |

## 5. Estado único e integrações
`c.producao = { contagens[], previsoes{cultivo: [vN…]}, cargas{}, lotes{}, pedidos{}, reservas{}, movs[], custos{}, seq{} }`. Campos de lote, reserva e pedido seguem a BEN §3.1 (D-05). Comandos em `producao.js`, sempre dentro de `cenMudar`: `prContar`, `prPublicar`, `prCarga`, `prReceber`, `prEstornar`, `prLiberarLote`, `prReservar`, `prCancelarReserva`. Consultas: `prUn`, `prCorrigir`, `prAreaColhida`, `prResultado`, `prSaldos`, `prOferta`, `prPodeEncerrar`.

| Módulo | Lê | Grava |
|---|---|---|
| O.S. (`c.ordens`) | tipo Colheita, talhão, safra, etapa, `ap` somados | nada; a ordem nasce pelo formulário da O.S. (§3.5) |
| App (`c.app`) | operador, sinal, fila | `cenApontar` (área); `prContar` e `prCarga` com chave; fila `CNT-`/`CG-` |
| Carência | `carEstado`, `carTals`, `carLid` | nada |
| Planejar safra | cultivo, área, meta, plano (DAP da colheita) | nada |
| Cadastros | `CULTURA_UN`, LOCAIS (tipo), clientes do CD-05 | nada |
| Estoque de insumos (`c.lotes`) | nada | nada (produto acabado nunca entra em `c.lotes`) |
| Comercial VE-04 | `c.producao.pedidos`, `reservas` | `prReservar`, `prCancelarReserva` |
| BEN (depois) | lotes Em processo | lotes de saída com `origem`; a produção comercial do talhão segue a genealogia |

Quem age (sem login; grava o papel, como `cenDevolver`; com o seletor de perfil da frente D, vem de `g2ator`): contagem e carga do campo, Sérgio (colheita); publicar previsão, emitir e liberar O.S., liberar lote, Ana (agrônoma); pesar e receber, Lúcia (recebimento) na Lagoa Grande e Rui (almoxarife) na Santa Rita; reservar, Comercial.

## 6. Semente sintética (números fecham, executado em `verificacao/contas.py`)
**6.1 Unidades (`CULTURA_UN`, recorte da UNIDADES-DE-MERCADO):** Soja e Milho sc 60 kg/ha, base 14 % e MEI 1 %; Feijão sc 60 kg/ha, 14 % e 0,5 %; Café arábica sc 60 kg/ha beneficiado, campo em L; Mamão Formosa: produção em t e t/ha (perene, ciclo da safra), comercial em kg, vida útil 7 d; Laranja cx 40,8 kg/ha com t/ha ao lado; Coco e Abacaxi mil frutos/ha; Arroz RS e SC sc 50 kg (só no teste).
**6.2 Previsões e contagens (Lagoa Grande):** v1 publicada por Ana em 09/09: Pivô 6 S38 = 62.000 kg; v1 de 16/09: Pivô 19 S39 = 72.900 kg. CNT-0001 Pivô 19, 23/09, Sérgio: 20 plantas, Pintado 11, De vez 10, Verde 12, peso 1,20 kg; plantas vivas 1.700/ha; perda 5 % → rascunho S40 **72.781,59 kg**, S41 **87.337,908 kg** (K08). Demais pivôs em produção sem contagem: pela meta (Pivô 2: 36.298,08 kg/semana, K09).
**6.3 O.S.:** nenhuma nova. OS-0510 (Pivô 6, Encerradas, 16/09 31,79 ha e 18/09 31 ha) e OS-0505 (Pivô 19, Em execução, 21/09 25 ha Conferido, 22/09 25 ha Provisório, 24/09 Previsto). Carência nesses dias: `sem` (executado, sonda `node`).

**6.4 Cargas** (tara 7.200 kg, Galpão de frutas Lagoa Grande, condição Íntegra, Recebidas por Lúcia, salvo a CG-2108):

| Carga · ticket | Dia | O.S. | Líquido | Lote |
|---|---|---|---|---|
| CG-2101 · TK-4471 / CG-2102 · TK-4472 | 16/09 | OS-0510 | 15.280 / 15.210 kg | L38-131 = 30.490 kg |
| CG-2103 · TK-4478 / CG-2104 · TK-4479 | 18/09 | OS-0510 | 14.960 / 14.870 kg | L38-132 = 29.830 kg |
| CG-2105 · TK-4490 / CG-2106 · TK-4491 | 21/09 | OS-0505 | 12.180 / 11.940 kg | L39-131 = 24.120 kg |
| CG-2107 · TK-4502 | 22/09 | OS-0505 | 12.300 kg | L39-132 = 12.300 kg |
| CG-2108 (do app, sem ticket) | 22/09 | OS-0505 | A pesar · estimativa 590 caixas | — |

**6.5 Lotes, pedidos e reservas:** L38-131 e L38-132 expedidos ao PV-037 (Frutas Real, 60.320 kg, entregue 17–19/09; físico 0, rastreio fica). L39-131 vence 28/09; L39-132 vence 29/09. L10-031 Soja · grão · Silo 01 · saldo de abertura da safra 2025/26 (sem talhão) = 2.305.200 kg = **38.420 sc**; RS-0001 de 232.500 kg (3.875 sc) para CT-201 (Coop Grão Sul, pronta entrega) → disponível **34.545 sc** (K10, igual à BEN K66). PV-036 Frutas Real, Mamão fruta de campo, 20.000 kg, pronta entrega 24–26/09, sem reserva. PV-038 Frutas Real, mamão, 30.000 kg, futura S41. CT-203 Coop Grão Sul, Soja 26/27, futura fev–mar/27, 12.000 sc = 720.000 kg. Movimentos: MP-1001 a MP-1007 (recebimentos), MP-1008 e MP-1009 (expedição), MP-1010 (abertura), MP-1011 (RS-0001). `seq` = {cg: 2108, lote: {38: 132, 39: 132}, rs: 1, mp: 1011, cnt: 1}. IDs livres por busca (executado).

**6.6 Resultados esperados:** Pivô 6 final **60,32 t · 0,96 t/ha**, −2,71 % da previsão S38 (K05). Pivô 19 parcial **36,42 t · 0,73 t/ha** com selo "1 carga a receber"; pesar a CG-2108 com 12.050 kg → **0,97 t/ha** (K06). Mamão Lagoa Grande **0,86 t/ha** ponderado (K07). Soja 26/27 pela meta **68.180 sc**; CT-203 deixa **56.180 sc** de oferta livre e o L10-031 continua com 34.545 sc disponíveis (K10). Custo: "sem custo realizado" em todos (D-09).

## 7. Passos de implementação (cada um deixa o protótipo funcionando)
1. **P1 · Unidades e contas:** `CULTURA_UN`; `producao.js` com `prUn`, `prCorrigir`, rateio e produtividade; `producao_unit.js` com K01-K04 e K11. Sem tela.
2. **P2 · Estado:** `dados_producao.py` (§6), `cenario.py` (`producao`, v+1), `cenario.js:395` e `:400`; comandos `pr*` com R-02 a R-19; unidade K05-K10 e K12, idempotência, estorno, carência (R-12) e encerrar (R-18).
3. **P3 · Estoque de produto:** `PROD.dc.html`, grupo Produção com 1 item, regex do verificador.
4. **P4 · Cargas e recebimento:** `CARGA.dc.html` e 2º item.
5. **P5 · Previsão e colheita:** `COLH.dc.html`, 3º item, `#nova:` na O.S. e duplicidade por semana.
6. **P6 · App:** MB-07 e MB-10 no estado, cartões no MB-01, linha "App de campo" do canvas.
7. **P7 · VE-04:** seção de reservas. Artefato atualizado com uma linha do que mudou.
8. **Bateria por passo:** `python3 producao_unit_test.py`; `python3 build.py > /tmp/COLH-build.log; grep -c FALHA /tmp/COLH-build.log` (0); `python3 montar_render.py`; no navegador, um por vez: `env CHROME_BIN=/tmp/cloudchrome/chrome flock /tmp/cdpB.lock env CDP_GL=1 timeout 900 python3 <teste>` com `varredura.py`, `../ferramentas/acoes_duplicadas.py . /tmp/COLH-dup.json`, `producao_fluxo_test.py`, `os_cenario_test.py`, `app_cenario_test.py`, `est_cenario_test.py`, `carencia_test.py`, `cotest.py`. Vermelhos conhecidos da base (lista da tarefa, não reexecutada aqui): componentes_ajustes, componentes_interacao, etapas_complemento, etapas_desktop, cal01, cd05v, intest, os_cenario (19/20), patest, psfix38test, saf38test, consumo_divergente (19/20); ficam listados no log, sem esconder.

## 8. Critérios de aceite
| AC | Critério | Teste que prova |
|---|---|---|
| AC-01 | Menu: Produção logo depois de Agrícola, 3 itens, cada um abre a página; páginas sem erro | `producao_fluxo_test.py` (menu); `varredura.py` |
| AC-02 | Unidade de cada cultura e conversões K11; nenhuma soma entre unidades | `producao_unit.js` U01 |
| AC-03 | Descontos de grão K01-K03, com bruto, descontos e comercial separados | U02 e painel da carga no fluxo |
| AC-04 | Apontar 25 ha sem carga não muda a produção | U03; fluxo passo 6 |
| AC-05 | Mesma chave não duplica; outro conteúdo = conflito; ticket repetido = mesma carga | U04 |
| AC-06 | Mistura 60/40 em K04, rastreio nos dois talhões | U05 |
| AC-07 | Produtividade K05-K07: passe, ciclo, anual, parcial e final, ponderada | U06 |
| AC-08 | Íntegra e carência em dia → Liberado; `curso` → Bloqueado; `insuf`, avaria ou sem O.S. → Em inspeção; Liberar recusa enquanto a pendência existir | U07 (aplicação injetada no estado) |
| AC-09 | Saldos do L10-031: 38.420 / 0 / 38.420 / 3.875 / 34.545 sc | U08; tela PROD no fluxo |
| AC-10 | Reserva recusa lote não Liberado, acima do disponível ou da falta; cancelar sem motivo recusa | U09 |
| AC-11 | Venda futura não muda o disponível; oferta livre 56.180 sc | U10; visão Por semana |
| AC-12 | Contagem não publica; publicar gera vN congelada; K08 | U11; MB-07 no fluxo |
| AC-13 | Café: L, Em processo, "sc a apurar" | U12 |
| AC-14 | Estorno com motivo; recusa abaixo do reservado | U13 |
| AC-15 | Encerrar O.S. de colheita com carga A pesar é recusado com dono | U14; fluxo |
| AC-16 | Carga sem sinal não aparece na web; ao voltar, entra uma vez | U15; fluxo do app |
| AC-17 | Tarefa do proprietário (§8.1) de ponta a ponta, com cliques e digitação medidos e gravados no log | `producao_fluxo_test.py` |
| AC-18 | Toda grade com filtro e ordenação; unidade na célula; uma ação primária por tela | fluxo; `acoes_duplicadas.py` sem achado nas 3 páginas |
| AC-19 | 390 px: cartões, sem rolagem horizontal, primária visível | fluxo em 390×844 |
| AC-20 | Build 0 FALHA; testes de O.S., app, estoque e carência sem vermelho novo contra a base | bateria do §7.8 |

**8.1 Tarefa curta para o proprietário (homologação):** em Produção › Previsão e colheita, escolha o Pivô 19, publique a previsão S40 e programe a colheita; em Ordem de Serviço, aprove, libere e inicie; no app (MB-10), aponte 25 ha (a produção não muda) e registre uma carga; em Cargas e recebimento, pese a CG-2108 (12.050 kg) e veja a produtividade do Pivô 19 passar de 0,73 para 0,97 t/ha; em Estoque de produto, reserve 20.000 kg do L39-131 para o PV-036 e confira o disponível de 4.120 kg.

## 9. Fora de escopo (condição de retorno)
| Item | Volta quando |
|---|---|
| Packing, secagem, café em coco e beneficiado; liberar lote Bloqueado com laudo | BEN-1 a BEN-4, sobre `c.producao` (D-05) |
| Expedição, romaneio de saída, transporte (LO-*) | frente Comercial e logística (#27) |
| Telas comerciais além do vínculo pedido↔lote; contrato, preço, faturamento | idem |
| Custo realizado por cultivo | CONTROLE-02 / CTL-4 publicar a fonte `custos` |
| Mapa de colheita e produtividade espacial (cap. 62) | importação de monitor de colheita pedida pelo proprietário |
| Qualidade da previsão (WAPE, viés, amostragem) além do desvio % | primeira safra com 6 semanas publicadas |
| Grão em secagem como "Em processo" | BEN-3 (hoje o comercial corrigido entra acabado, D-07) |
| Mostrar `CULTURA_UN` no CD-02 | próxima passada de Cadastros |
| Cinco referências do setor do módulo (AGENTS §3.3) | Codex registra antes do aceite; não bloqueia o código |
