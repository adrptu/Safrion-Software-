# Comercial e logística · especificação v1.0

**Pedidos do proprietário (Adrianus, 05/10/2026, literal):** «o módulo comercial entra onde nisso?»; «...estoque de produto acabado conectando com comercial e estoque de produto acabado»; «quero todos os módulos e funcionalidades do protótipo prontos». Diretriz permanente: essencialismo, separar planejamento, execução e controle, tudo no mesmo estado, sem redigitar.

- **Rótulo:** especificado. Nenhum código alterado. "(executado)" marca o que saiu de comando rodado em 06/10/2026 nesta base: `python3 docs/comercial/verificacao/contas.py` (FALHAS: 0) e uma sonda `node` sobre `cenario.js_prefixo()` + `JS_NUCLEO` + `PR_UI_JS` (saldos, oferta e `carAvaliar` da semente).
- **Base:** `f4121bd` (branch `claude/v44-comercial`). `gen37/` = `tools/prototipo/v37/gen37/`. PRD = `Safrion-Software-/docs/PRD.md` v3.9: VE-01..LO-04 l.1298-1500; cap. 46 l.7575; cap. 48 l.7857; cap. 49 l.7965. Decisões sem o proprietário: `DECISOES.md` (D-Cnn).
- **Fontes reaproveitadas, não repetidas:** Colheita (`docs/colheita/ESPECIFICACAO.md`): lote, qualidade efetiva (R-12), saldos (R-14), reserva (R-15), venda futura (R-16), `prReservar`, `prOfertaSem`/`prOfertaSafra`, data operacional (D-25). Unidades: `docs/culturas/UNIDADES-DE-MERCADO.md` (DEC-0510-03). Estados de lote e destinação: BEN §3.

```text
ID / resultado útil / persona: COM-1 / da venda ao lote reservado, à carga pesada, à entrega e ao a receber, sem redigitar / comercial (Dora), expedição (Rui), gestora (Ana)
Requisitos do PRD e fora do escopo: VE-01, VE-04, VE-05, VE-06 (retorno físico), LO-02, LO-03 (entrega); cap. 46.3-46.5, 48.1-48.5, 49.2-49.3; VEN-02/03/04/07/10, LOG-01/04/05/07/08, ATP-07; fora: §9
Autor / revisor / integrador: Claude / Codex / integrador da branch única
Base / arquivos sob responsabilidade: f4121bd / areas/vendas.py, comercial.js, dados_comercial.py, testes comercial_*; trechos do §0 "Muda"
Aceite e comando de verificação: §8; bateria do §7
Estado / impedimento / próximo passo: especificado / nenhum (D-C01..D-C22 valem até o proprietário mudar) / P1
```

## 0. Mapa do existente

| Fica (reusar, sem mudar o comportamento) | Onde |
|---|---|
| Pedidos, reservas, lotes e movimentos no estado único | `cenario.py:84` (`producao=dados_producao.seed()`); `dados_producao.py:99-109` (RS-0001, PV-030, PV-036..038) |
| Saldos, qualidade efetiva, falta, situação do pedido, oferta | `producao.js:178` (`prQualidade`), `:195` (`prSaldos`), `:202` (`prFalta`), `:205` (`prSitPed`), `:213-226` (`prOfertaSem`, `prOfertaSafra`) |
| Reservar e cancelar reserva, liberar lote | `producao.js:380` (`prReservar`), `:398` (`prCancelarReserva`), `:371` (`prLiberarLote`) |
| Formulário de reserva, painel, topo, cartões, primária, chave | `areas/producao.py:124-222` (`PR_UI_JS`: `prTopo`, `prFld`, `prPainel`, `prRun`, `prPrim`, `prChave`, `prCards`; `PR_PED_JS`: `prFormReserva`, `prPanPed`) e `:37-117` (`bloco`, `cartoes`, `painel`, `prim_html`, `_shell`) |
| Unidade de cada cultura (fonte única) | `dados_cad.py:41-53` (`CULTURA_UN`); `producao.js:33-46` (`prUn`, `prEstUn`, `prEstBase`, `prEstTxt`) |
| Clientes, fornecedores, transportadores, condição de pagamento, limite de crédito | `areas/cad_parceiros.py:31-35` (`VEICULOS`, `COND_PAG`), `:39-88` (`OUTROS`, `NOVOS`), `:89` (`_parceiros()`) |
| Avaliação do lote por destino (carência, LMR) | `dados_carencia.py:327` (`carAvaliar`) |
| Perfis e papel de quem age | `g2lib.js:250-262` (`G2_PERFIS`, `g2perfil`, `g2ator`); `cenario.js:68-71` (`cenExige`, `cenExigeUm`, `cenRevisao`) |
| Obrigações físicas da soja 26/27 (número) | `areas/comercial.py:31-36` (`CT203`, `CPR`, `BT`): continuam a fonte do número |
| VE-01..VE-06 e LO-01..LO-04 ocultos, com seus testes (`vetest.py`, `lotest.py`) | `areas/comercial.py`, `areas/logistica.py`: intocados (D-C02) |

| Muda | Arquivo:linha | Passo |
|---|---|---|
| Unidade de preço onde difere da de produção: Mamão `pun='kg', pmassa='1'`; Coco e Abacaxi `pun='fruto', pmassa='1'` | `dados_cad.py:46,48,49` | P1 |
| `prNovoLote(c, dia)` extraído de `prReceber` (o mesmo gerador `L<semana>-<seq>`) | `producao.js:338` | P1 |
| `prExpedido` desconta movimentos `devolução`; `prSitPed` devolve "Encerrada" quando `ped.enc` | `producao.js:200`, `:205` | P1 |
| `prReservar` e `prCancelarReserva` aceitam `ator`; com ator, `cenExigeUm(ator, ['comercial','gestor'])` e `quem = g2ator` | `producao.js:380`, `:398`; chamadas em `areas/producao.py:203`, `:214` passam `g2perfil()` | P1 |
| Obrigações do VE-05 saem do catálogo (`obrig=[]`) e entram no estado como vendas futuras | `dados_producao.py:56-61`; `producao_unit.js:153` (U10a: `of.ob.length===3` → CT-203, CRE-0095 e BT-090 em `of.fut`; motivo no commit) | P1 |
| Estado v=5 com a semente comercial | `cenario.py:83-84` (`v=5`; `producao=dados_comercial.completar(dados_producao.seed())`) | P1 |
| Perfis: + `Dora · Comercial` `{comercial}`; Rui + `expedicao` | `g2lib.js:250-251`; testes que fixam 5 perfis passam a usar o tamanho do cadastro: `os_aprov_lib_unit.js:121-122`, `aprova_quem_decide_unit.js:224-225` | P1 |
| Grupo **Comercial** (ícone `Vendas`) logo depois de Produção, 3 itens | `ui37.py:40-41` (MENU2) | P2-P4 |
| Regex de IDs do verificador de ações: + `RM` | `v37/ferramentas/acoes_duplicadas.py:15` | P2 |
| Índice: persona Dora aponta para a tela nova | `areas/indice.py:13` (`VE-01` → `VEN`) | P5 |
| Estoque de produto sem a grade Pedidos (vai a Contratos e pedidos); reservar a partir do lote fica | `areas/producao.py:231-238`, `:251`, `:265`, `:273-282`, `:291`, `:312`; `producao_fluxo_test.py:197-203` (cancelar reserva e A-17 passam à VEN) | P6 |
| Previsão e colheita › Por semana sem "Vendas futuras" e "Oferta livre" (vão ao Painel) | `areas/producao.py:453-455`, `:528-541` | P7 |

**Novo:** `areas/vendas.py` (VEN, EXPED, PCOM; monta tela e chama comandos), `comercial.js` (regras e comandos `com*`), `dados_comercial.py` (catálogo `COMC` e `completar(seed)`), `comercial_unit.js` + `comercial_unit_test.py` (node), `comercial_fluxo_test.py` (navegador). **Sai:** nada é apagado.

## 1. Missão e princípios
1. **Um acordo, um registro:** a venda (pronta entrega ou futura) é o mesmo registro do pedido que a Colheita já reserva; a entrega, a saída física e o a receber nascem dele, sem redigitar cliente, produto, preço ou lote.
2. **O físico sai uma vez:** saída só de lote apto, reservado para a venda, pesado, com o destino conforme; repetir não baixa de novo.
3. **Unidade da cultura e preço de mercado na célula:** "4.000 sc", "R$ 128,00/sc", "10.000 kg", "R$ 3,05/kg". Base guardada em kg ou frutos; conversão só em `prUn`/`comValor`.
4. **Planejamento, execução e controle separados:** comprometer (Contratos e pedidos), carregar e entregar (Expedição e entregas), saber o que posso vender e o que vou receber (Painel comercial).
5. **Trava só com dano nomeado** (§4): lote inapto, carência ou destino, reserva de outro, baixa em dobro, crédito. O resto é aviso com dono.

## 2. Menu e telas, antes → depois

| Antes (oculto, texto fixo) | Depois: grupo **Comercial**, entre Produção e Manutenção | Natureza |
|---|---|---|
| VE-03 Ofertas · VE-04 Pedidos (+ VE-04det) · VE-05 Contratos | **Contratos e pedidos** `VEN.dc.html`: venda pronta ou futura, preço, crédito, reserva de lote | planejamento (compromisso) |
| LO-01 Programação · LO-02 Expedições (+ LO-02det) · LO-03 Viagens · VE-06 Devoluções | **Expedição e entregas** `EXPED.dc.html`: carga de saída (romaneio), pesagem, saída única, entrega, devolução | execução |
| VE-01 Demanda e oferta · VE-02 Mercado | **Painel comercial** `PCOM.dc.html`: oferta × compromissos × livre por período; preço médio e a receber | controle |
| LO-04 Fretes | frete de referência sintético como ajuda do "Programar carga" | — |
| Estoque de produto (grade Pedidos) · Previsão e colheita (Vendas futuras, Oferta livre) | grade e colunas passam às telas acima (D-C14) | — |

## 3. Telas
Todas: master-detail (grade G2 com filtro por coluna e ordenação → painel do registro), topo Fazenda e Safra (padrão Todas, D-26 da Colheita), filtro rápido de situação, unidade junto do número, estado e próximo passo com verbo em toda linha, **uma** ação primária no cabeçalho escolhida pelo registro selecionado (sem seleção, a regra de cada tela); secundárias só no painel. Celular (390 px): abaixo de 480 px a lista vira cartões (identificação, número principal com unidade, situação, próximo passo), sem rolagem horizontal, primária fixa no rodapé. Mesmo motor da Colheita (`areas/producao.py`: `painel`, `_shell`, `PR_UI_JS`); `comercial.js` só nas três telas (D-C15). Nenhum elo para tela oculta (`links_ocultos_test.py` L2).

### 3.1 Contratos e pedidos (`VEN`)
**Pergunta:** o que vendi, a quem, a que preço, para quando, e o que falta cobrir com lote?

| Venda · cliente | Produto | Tipo · janela | Quantidade | Preço | Entregue | Reservado | Falta | Situação · próximo passo |
|---|---|---|---|---|---|---|---|---|
| PV-030 · Coop Grão Sul | Soja em grão · Padrão 25/26 | Pronta entrega · set–out/26 · saldo do CT-201 | 4.000 sc | R$ 128,00/sc | 0 sc | 3.875 sc | 125 sc | Parcial · Reservar lote · Comercial |
| CT-203 · Coop Grão Sul | Soja em grão 26/27 | Futura · safra 2026/27 | 12.000 sc | R$ 132,00/sc | 0 sc | 0 sc | 12.000 sc | Futura: compromete a previsão · reservar na colheita |

**Situações** (precedência): Encerrada · Entregue · Em risco (reserva com expedição impedida) · Aguardando crédito · Coberto · Parcial · Sem reserva · Futura (compromete a previsão | parcial). O próximo passo diz a janela ("janela vencida em 26/09" quando há falta ou reservado sem saída).
**Painel:** Comercial (cliente, natureza, condição com o evento do vencimento, modalidade e local, destino, preço, valor, quem registrou; crédito do cliente: limite, validade, a receber, situação); Atendimento (reservas por lote com "Cancelar reserva"; cargas RM com estado e link `EXPED#RM`); Financeiro (entregas: valor, vencimento, a vencer ou vencido); Movimentos MP.
**Ação primária** da venda selecionada: Aguardando crédito → "Aprovar crédito do PV-xxx" (gestor); falta > 0 e lote apto compatível com disponível → "Reservar lote para o PV-xxx" (`prFormReserva` modo pedido, sugestão mín(disponível, falta)); reservado ainda não programado > 0 → "Programar carga do PV-xxx" (link `EXPED.dc.html#nova:PV-xxx`); senão nenhuma. Sem seleção: "Registrar venda". Secundária no painel: "Encerrar saldo" (motivo).
**Formulário "Registrar venda"** (só dois números digitados; o resto por toque ou herdado): Cliente (busca; papel Cliente do CD-05; Fornecedor só para CPR e barter) → herda condição de pagamento, modalidade ("Retira…" no CD-05 → Cliente retira na fazenda; senão Agricultor organiza a entrega) e local; Natureza (Venda; CPR ou Barter só com fornecedor, um toque); Produto (um toque: produtos do CD-05 do cliente primeiro, todos os de `CULTURA_UN` com lote ou previsão no estado) → herda fazenda, unidade e classe; Tipo (Pronta entrega | Venda futura); Janela (pronta: Esta semana, Próxima semana ou datas; futura: semana publicada no perene ou safra no grão, mostrando a oferta livre); **Quantidade** (unidade comercial, teclado numérico, sem último valor); **Preço** (R$ por unidade de preço; ajuda: referência de mercado sintética); Destino (Mercado interno · Brasil, padrão). Avisos no formulário: crédito do cliente; déficit da oferta do período.

### 3.2 Expedição e entregas (`EXPED`)
**Pergunta:** o que sai hoje, de que lote, para quem, quanto pesou, e o que já foi entregue?

| Carga · romaneio | Venda · cliente | Produto · lotes | Previsto | Saída | Modalidade · veículo | Data | Situação · próximo passo |
|---|---|---|---|---|---|---|---|
| RM-0001 | PV-037 · Frutas Real | Mamão · L38-131 | 30.490 kg | 30.490 kg | Agricultor entrega · registro da Colheita | 17/09 | Entregue · R$ 91.470 a receber até 15/10 |

**Situações:** Programada (· impedida: motivo e dono) · Em trânsito · Entregue · Entregue com devolução · Cancelada. Filtros rápidos: situação; data (Hoje, Esta semana, Todas).
**Painel:** romaneio (venda, cliente, destino, local, modalidade, transportador, veículo, placa, data prevista); lotes (previsto, reservado da venda no lote, saída); verificação ao vivo da saída (lote apto, destino por lote de campo, crédito), cada impedimento com dono e link (`PROD#lote`, `VEN#PV`); pesagem (bruto, tara, líquido em kg e na unidade da cultura); entrega (data, comprovante); devoluções (lote de retorno, link `PROD#lote`); movimentos MP e recibo.
**Ação primária:** Programada sem impedimento → "Confirmar saída da RM-xxxx" (bruto e tara em kg, teclado numérico, sem último valor; kg por lote só com 2+ lotes, pré-preenchido com o previsto, soma = líquido); Em trânsito → "Confirmar entrega da RM-xxxx" (data Hoje | Ontem; "Recebido tudo" ou "Com devolução": quantidade e motivo por toque; comprovante opcional); Entregue → nenhuma (secundária "Registrar devolução"); Programada impedida → nenhuma (o próximo passo diz quem resolve). Sem seleção: "Programar carga". Gravado um registro, ele fica selecionado e a primária passa ao próximo passo. Secundária: "Cancelar carga" (Programada, motivo).
**Formulário "Programar carga":** Venda (um toque entre as que têm reserva não programada; herdada de `#nova:PV-xxx`) → lotes reservados (um toque para tirar), modalidade e local; Transportador (só Agricultor entrega: transportadores do CD-05 ou Frota própria); Veículo (um toque, só tipos compatíveis com o produto, capacidade do nome: 37, 30, 14, 12 t); **Placa** (texto); Data prevista (Hoje, padrão | Amanhã); Previsto (pré-preenchido mín(reserva não programada, capacidade), editável). Ajuda: frete de referência sintético (ex-LO-04).

### 3.3 Painel comercial (`PCOM`)
**Pergunta:** quanto ainda posso vender de cada produto em cada período, quanto está comprometido, a que preço vendi e quanto vou receber?
**Indicadores (R$):** A receber (a vencer) · Vencido (cobrar) · Entregue nos últimos 30 dias.
**Oferta e compromissos** (árvore produto › período; horizonte 4 semanas | safra):

| Produto › período | Oferta | Compromissos | Coberto por lote | Livre para vender | Situação |
|---|---|---|---|---|---|
| Soja em grão › Estoque (2025/26) | 38.420 sc apto | 4.000 sc | 3.875 sc | 34.420 sc | Livre |
| Soja em grão › Safra 2026/27 | 68.180 sc publicada | 19.900 sc | 0 sc | 48.280 sc | Livre |
| Mamão Formosa › Estoque | 0 kg apto | 10.000 kg | 0 kg | −10.000 kg | Déficit |
| Mamão Formosa › S41 | sem versão publicada | 30.000 kg | 0 kg | −30.000 kg | Déficit |

Horizonte 4 semanas = S40 a S43 (a S39 está em colheita e entra pelo estoque); semana sem previsão nem venda não aparece.

**Preço e recebimento** (por produto): Vendido · Preço médio contratado · Entregue · Preço médio realizado · Referência de mercado (sintética, ex-VE-02) · A receber · Vencido. Painel do produto: entregas a receber (RM, cliente, valor, vencimento) e vendas (link `VEN#id`); CPR e barter à parte, "liquidação em produto (GE-08)".
**Ação primária:** linha com livre > 0 → "Vender <produto> · <período>" (link `VEN.dc.html#nova:<produto>:<período>`, formulário com produto, tipo e período herdados); linha em déficit → "Ver vendas de <período>". Sem seleção: a primeira linha com livre > 0.

### 3.4 Integrações de tela
- **Estoque de produto:** só lotes (`PROD#PV-…` passa a `VEN#PV-…`); "Reservar para pedido" a partir do lote fica (mesmo `prReservar`, agora com ator); lote devolvido aparece Em inspeção com "devolvido na RM-xxxx" e "Liberar lote · Qualidade".
- **Previsão e colheita › Por semana:** previsão publicada × colhido × desvio; nota "Oferta livre e vendas futuras: Painel comercial" com link.
- **Índice:** Dora (Comercial e logística) → `VEN.dc.html`. **VE-*/LO-*:** ocultos. **MB-10 aba Motorista:** igual (§9). **O.S., Kanban de 5 fases e aprovação agronômica:** nada muda; carga de saída não é ordem.

## 4. Regras (testáveis, com o dano evitado)
| # | Regra | Dano que a trava evita |
|---|---|---|
| R-C01 | Quantidade digitada na unidade comercial (`prEstUn`), guardada na base (`prEstBase`); preço em R$ por unidade de preço: `pun = u.pun ‖ u.un`, `pmassa = u.pmassa ‖ u.massa`; valor = base ÷ pmassa × preço, decimal, um arredondamento, só em `comValor`. | Preço de saca aplicado a kg; valor e preço médio errados (S2) |
| R-C02 | Venda: contraparte do CD-05 (Cliente; CPR e barter, Fornecedor), sem cadastro paralelo; produto com unidade em `CULTURA_UN`; quantidade e preço > 0; pronta com janela (fim ≥ início) ou futura com semana (perene semanal) ou safra (grão); condição do CD-05 com evento explícito (`comVenc`: "À vista na entrega" = 0 d; "N dias após a entrega comprovada" = N d; "Antecipado" vence no registro). ID `PV-0NN` (pronta) ou `CT-2NN` (futura). | Venda sem cliente ou com prazo sem evento: cobrança impossível (VEN-04) |
| R-C03 | Todo comando `com*` com chave de quem inicia, nascida ao abrir o formulário (`prChave`) e morta no sucesso: mesma chave e mesmo conteúdo = mesmo registro e mesma mensagem; outro conteúdo = conflito, nada grava. Registro já no estado final ("Saída confirmada", "Entregue") recusa repetir com outra chave. | Venda ou saída em dobro (S2) |
| R-C04 | Venda futura não toca o físico; compromete a oferta do período (Colheita R-16); reservar lote para ela move a dedução. Acima da oferta livre: aviso de déficit, não trava (D-C16). | Dupla dedução (ATP-07) |
| R-C05 | Reservar e cancelar reserva: `prReservar`/`prCancelarReserva` (Colheita R-15), papel comercial ou gestor. | Reserva gravada em nome de quem não responde pela venda |
| R-C06 | Programar carga: venda com reserva ativa; por lote, previsto ≤ reserva ativa ainda não programada; total ≤ capacidade do veículo; veículo compatível (cultura com vida útil → baú refrigerado; grão → graneleiro). | Caminhão na doca sem produto reservado; excesso de peso; fruta em graneleiro |
| R-C07 | **Confirmar saída** (uma vez): para cada lote, qualidade efetiva Liberado (`prSaldos`); cada lote de campo de origem (`prLcs`) com `carAvaliar(c, lc, destino da venda)` = conforme (pendente recusa com a falta e o dono; não conforme recusa); lote sem lote de campo (abertura) sai com "origem anterior ao sistema" gravado; tara ≥ 0 e líquido = bruto − tara > 0; kg do lote ≤ reserva ativa da venda no lote; crédito (R-C08). Efeito na mesma transação: MP `expedição` −kg por lote, reservas da venda no lote consumidas da mais antiga para a mais nova (`r.kg` −kg, `r.exp` +kg; zerada = "Expedida"), avaliação gravada na RM. Lote vencido é aviso (D-21 da Colheita). Disponível do lote não muda; expedido da venda sobe; falta não muda. | Expedir lote bloqueado ou colhido na carência (lei, S1); vender o reservado de outro; baixa em dobro (S2) |
| R-C08 | Crédito (natureza Venda, condição ≠ Antecipado): cliente sem limite, limite vencido (`limv` < hoje) ou a receber do cliente + valor da saída > limite → a saída exige "Aprovar crédito" na venda (`cenExige(ator,'gestor')`); a aprovação grava quem, quando e o valor coberto e vale até ele; mesma pessoa que registrou a venda → `cenRevisao` (revisão posterior). Na lista, "Aguardando crédito" quando a regra recusaria a próxima saída (reservado não expedido) ou o limite está vencido ou ausente. | Entregar a prazo sem cobertura: perda de dinheiro (S2; PRD 46.4, VEN-07) |
| R-C09 | Entrega: Cliente retira → a saída é a entrega (ponto contratado, PRD 48.2); Agricultor entrega → "Confirmar entrega" com data ≥ saída e ≤ hoje. Vencimento = data do evento + dias da condição. A receber = valor das saídas confirmadas líquido de devolução (em trânsito: "vence N d após a entrega"), sem baixa no protótipo (D-C07); é também a exposição do R-C08. | Prazo de pagamento contado da data errada (LOG-08) |
| R-C10 | Devolução: só de carga entregue; quantidade ≤ saída − já devolvido; motivo por toque. Cria lote novo (`prNovoLote`) com `q0` Em inspeção, `cond` "Devolvido", a origem do lote expedido (carência e genealogia) e o local dele; MP `devolução` +kg; o expedido da venda cai (falta volta; venda Encerrada baixa a quantidade vigente junto, sem reabrir falta) e o a receber cai. Só a Qualidade libera (`prLiberarLote`); destinação é da BEN. | Produto devolvido vendido de novo sem conferência (DEMO-08, VEN-10) |
| R-C11 | Encerrar saldo (cancelar o que falta): motivo; recusa com carga Programada (cancelar a carga antes); cancela na mesma transação as reservas ativas da venda, listadas na mensagem; quantidade vigente = expedido líquido (`qtd0` e `enc` guardados). | Venda fantasma comprometendo oferta e estoque |
| R-C12 | Cancelar carga: só Programada, motivo; reservas intactas. | Romaneio de carga que não veio contado como saída |
| R-C13 | Painel: só funções do estado (`prSaldos`, `prOfertaSem`, `prOfertaSafra`, `comValor`, `comAReceber`), nenhum número fixo. Estoque: oferta = Σ apto; compromissos = Σ saldo das prontas; livre = Σ disponível − Σ falta das prontas. Período futuro = semana que ainda não começou (perene) ou safra ainda não colhida (grão): livre = `prOferta.livre`; o período em curso entra pelo estoque (realizado substitui previsão, PRD 49.2). Preço médio = Σ valor ÷ Σ quantidade, só natureza Venda; realizado sobre o entregue líquido. | Média de médias; barter ou CPR como receita; número velho |
| R-C14 | Quem age (`g2perfil()`; recusa "<ação>: decisão de <quem>. Nada foi alterado."): vender, encerrar, reservar e cancelar reserva → comercial ou gestor; programar, cancelar carga, saída, entrega e devolução → expedição ou gestor; aprovar crédito → gestor. O registro grava `g2ator`. | Registro em nome de quem não fez |
| R-C15 | Datas dos registros = `CEN_DIA_OP` (26/09/2026, D-25 da Colheita); entrega e devolução por atalhos, nunca futuras. | Vencimento e semana ambíguos |

## 5. Estado único e integrações
`c.producao` (v=5) ganha: `pedidos[id]` + `preco, natureza, cond, modal, local, faz, ini, fim, d, at, quem, chave, imp, cred{quem,d,at,ate,rev}, enc{motivo,quem,d,qtd0}`; `reservas[id]` + `kg0, exp`; `expedicoes[RM]` = `{id, pedido, lotes[{lote,prev,kg}], modal, transp, veic, placa, dprev, st, saida{bruto,tara,liq,d,at,quem,chave,aval[],cred}, entrega{d,at,quem,comp}, devs[{lote,kg,motivo,d,quem}], canc, hist}`; `seq` + `rm, pv, ct`. Comandos em `comercial.js`, sempre dentro de `cenMudar`: `comVender`, `comEncerrar`, `comAprovarCredito`, `comProgramar`, `comCancelarCarga`, `comSair`, `comEntregar`, `comDevolver`. Consultas: `comPun`, `comValor`, `comVenc`, `comAReceber`, `comCredito`, `comSitVenda`, `comPainel`. Catálogo `COMC` (`dados_comercial.catalogo()`, lido no build): contrapartes do CD-05 (`_parceiros()`: papéis, condição, limite, validade, local, produtos), transportadores e veículos com capacidade, condições → dias, referência de mercado sintética.

| Módulo | Lê | Grava |
|---|---|---|
| Produção (`c.producao`) | lotes, qualidade, saldos, previsões publicadas, oferta | vendas, reservas (`prReservar`), RM, MP `expedição` e `devolução`, lote de devolução |
| Cadastros | CD-05 (contrapartes, condição, crédito, transportadores); `CULTURA_UN` | nada |
| Carência | `carAvaliar` por lote de campo e destino, ao vivo | nada |
| Perfis | `g2perfil`, `g2ator`, `cenExige*` | nada |
| BEN (depois) | — | lotes classificados no mesmo `c.producao`, vendáveis pelas mesmas regras |
| O.S., Kanban, app | nada | nada |

**Quem age:** Dora (comercial, persona do Índice); Rui (almoxarife e expedição; "Supervisor de expedição" na AL-08); Ana (gestora: tudo acima e o único que aprova crédito); Marta (Qualidade) libera lote devolvido no Estoque de produto.

## 6. Semente sintética (números fecham, executado em `verificacao/contas.py`)
**6.1 Catálogo:** CD-05 como está (Frutas Real limite R$ 120.000 até 31/12/2026, 28 d; Coop Grão Sul R$ 2.000.000 até 30/06/2027, à vista na entrega, retira FOB; Rede Hortifrúti BA R$ 40.000 vencido em 31/08/2026; Rota Sul baú refrigerado 12 t; TransVale bitrem 37 t e truck 14 t). Referência de mercado (sintética, D-1, dos valores do VE-02 oculto): soja R$ 129,40/sc 60 kg; milho R$ 61,80/sc; mamão R$ 3,10/kg; feijão "sem cotação" (ausente ≠ zero).
**6.2 Vendas** (`dados_comercial.completar`; `seq` = {rm: 1, pv: 38, ct: 204}):

| Venda | Contraparte · natureza | Produto · tipo | Quantidade | Preço | Condição · modalidade |
|---|---|---|---|---|---|
| PV-030 (CT-201) | Coop Grão Sul · Venda | Soja 25/26 · pronta set–out/26 | 4.000 sc | R$ 128,00/sc | à vista na entrega · cliente retira |
| PV-036 | Frutas Real · Venda | Mamão · pronta 24–26/09 | 10.000 kg | R$ 3,05/kg | 28 d · agricultor entrega |
| PV-037 | Frutas Real · Venda | Mamão · pronta 16–17/09 (entregue) | 30.490 kg | R$ 3,00/kg | 28 d · agricultor entrega |
| PV-038 | Frutas Real · Venda | Mamão · futura S41 | 30.000 kg | R$ 3,10/kg | 28 d · agricultor entrega |
| CT-203 | Coop Grão Sul · Venda | Soja 26/27 · futura safra | 12.000 sc | R$ 132,00/sc | à vista na entrega · cliente retira |
| CRE-0095 | Agroquímica Delta · CPR | Soja 26/27 · futura safra | 6.900 sc | R$ 118,84/sc equivalente | liquidação em produto |
| BT-090 | Fertisul · Barter | Soja 26/27 · futura safra | 1.000 sc | R$ 131,00/sc equivalente | liquidação em produto |

**6.3 Carga:** RM-0001 = saída histórica do L38-131 ao PV-037 já gravada pela Colheita (MP-1008, 17/09 08:30, recebe `rm`), entregue 17/09, sem pesagem inventada (`hist`). Nenhuma Programada.
**6.4 Resultados esperados (KC02, KC05-KC08):** Painel como no §3.3; preço médio contratado soja R$ 131,00/sc (R$ 2.096.000 ÷ 16.000 sc) e mamão R$ 3,05/kg (R$ 214.970 ÷ 70.490 kg); realizado mamão R$ 3,00/kg; a receber R$ 91.470, vence 15/10; vencido R$ 0. CRE-0095 e BT-090 fora do preço e do a receber. Sondas (executado): `carAvaliar` MI-BR: LC-0505-1, LC-0505-2 e LC-0510-1 conformes, LC-0510-2 pendente (pós-colheita não conferido); oferta soja 26/27 4.090.800 kg.
**6.5 Tarefa do proprietário (KC03, KC04, KC11):** reservar 125 sc (RS-0002, 7.500 kg) → disponível 34.420 sc; programar bitrem do cliente → previsto 37.000 kg (616,67 sc); bruto 51.200, tara 14.240 → líquido 36.960 kg = 616 sc; L10-031 físico 37.804 sc, reservado 3.384 sc, disponível 34.420 sc (igual), PV-030 entregue 616 sc, falta 0; a receber + R$ 78.848, vence 26/09; total R$ 170.318. **Crédito (KC09):** depois da tarefa da Colheita (L39-133 reservado ao PV-036), a saída da Frutas Real dá 91.470 + 30.500 = R$ 121.970 > R$ 120.000 → Ana aprova. **Devolução (KC10):** 400 kg do PV-036 → lote novo Em inspeção, entregue 9.600 kg, a receber R$ 29.280, vence 24/10, falta 400 kg.

## 7. Passos de implementação (cada um deixa o protótipo funcionando)
1. **P1 · Regras e estado, sem tela:** `CULTURA_UN` (pun), `producao.js` (`prNovoLote`, `prExpedido`, `prSitPed`, ator na reserva), perfis e os dois testes de 5 perfis, `dados_comercial.py`, `cenario.py` v=5, `obrig=[]` e U10a, `comercial.js`; `comercial_unit.js` C01-C12 (§8).
2. **P2 · Contratos e pedidos:** `VEN.dc.html`, grupo Comercial com 1 item, `RM` no verificador.
3. **P3 · Expedição e entregas:** `EXPED.dc.html`, 2º item, `#nova:PV`.
4. **P4 · Painel comercial:** `PCOM.dc.html`, 3º item, `#nova:<produto>:<período>` na VEN.
5. **P5 · Integrações:** Índice (Dora) → VEN; elos `VEN#`, `EXPED#` e `PROD#` entre as três telas e o Estoque de produto.
6. **P6 · Estoque de produto sem Pedidos** e `producao_fluxo_test.py` com a expectativa nova (motivo no commit). Pode sair sozinho se conflitar com outra frente.
7. **P7 · Previsão e colheita sem as colunas comerciais**, idem.
8. **P8 · Artefato** atualizado, com uma linha do que mudou.
9. **Bateria por passo** (`SAFRION_DADOS=sintetico`): `python3 docs/comercial/verificacao/contas.py`; `python3 comercial_unit_test.py`; `python3 producao_unit_test.py`; `node os_aprov_lib_unit.js` e `aprova_quem_decide_unit.js` pelos seus `_test.py`; `python3 build.py > /tmp/COM-build.log; grep -c FALHA /tmp/COM-build.log` (0); `python3 montar_render.py`; `python3 links_ocultos_test.py`; no navegador, um por vez: `env CHROME_BIN=/tmp/cloudchrome/chrome flock /tmp/cdpC.lock env CDP_GL=1 timeout 900 python3 <teste>` com `varredura.py`, `../ferramentas/acoes_duplicadas.py . /tmp/COM-dup.json`, `comercial_fluxo_test.py`, `producao_fluxo_test.py`, `acao_unica_test.py`, `vetest.py`, `lotest.py`, `est_cenario_test.py`, `os_cenario_test.py`, `app_cenario_test.py`, `carencia_test.py`. Vermelhos conhecidos da base (não são desta frente, ficam no log): componentes_ajustes, componentes_interacao, etapas_complemento, etapas_desktop, cal01, cd05v, intest, os_cenario (19/20), patest, psfix38test, saf38test, consumo_divergente (19/20). Antes do P1, rodar a bateria na base `f4121bd` e guardar o log para comparar.

## 8. Critérios de aceite
| AC | Critério | Teste que prova |
|---|---|---|
| AC-01 | Menu: Comercial logo depois de Produção, 3 itens, cada um abre a tela; sem erro de JS | `comercial_fluxo_test.py menu`; `varredura.py` |
| AC-02 | Valor e unidade: 616 sc × R$ 128,00 = R$ 78.848; mamão em kg e R$/kg; coco em fruto; nenhuma soma entre unidades | C01 |
| AC-03 | Registrar venda: obrigatórios, condição com evento, IDs PV-039 e CT-205, mesma chave = mesma venda, outro conteúdo = conflito, Caio (PCP) recusado | C02 |
| AC-04 | Venda futura não muda o disponível; soja 26/27 livre 48.280 sc com CT-203, CRE-0095 e BT-090 no estado; nova CT-205 de 4.000 sc → 44.280 sc; déficit é aviso | C03; U10a |
| AC-05 | Programar: recusa sem reserva, acima da reserva não programada, acima da capacidade e veículo incompatível; previsto sugerido 37.000 kg | C04 |
| AC-06 | Saída: KC04 exato; repetir com a mesma chave não baixa; outra chave na RM saída recusa; líquido acima da reserva recusa; tara ≥ bruto recusa | C05 |
| AC-07 | Saída recusada com lote Em inspeção, com bula corrigida que põe o lote na carência (`carc_bula`) e com laudo acima do limite; pendente diz a falta e o dono; abertura sai com "origem anterior ao sistema" | C06 |
| AC-08 | Crédito: Rede Hortifrúti (vencido) e Frutas Real (KC09) recusam a saída com "decisão de Ana (gestora)"; Caio não aprova; Ana aprova e a saída passa; aprovação não cobre valor maior | C07 |
| AC-09 | Entrega e devolução: KC10; lote de retorno Em inspeção não é reservável até a Qualidade liberar; devolver mais que o entregue recusa | C08 |
| AC-10 | Encerrar saldo: sem motivo recusa; com carga Programada recusa; cancela as reservas na mesma transação; oferta e falta recalculadas | C09 |
| AC-11 | Painel da semente (§3.3, §6.4) e depois da tarefa (§6.5), lidos das funções do estado | C10; `comercial_fluxo_test.py painel` |
| AC-12 | Perfis: R-C14 para cada comando; o registro grava quem agiu | C11 |
| AC-13 | Decimal: três saídas de 1/3 do reservado fecham o físico sem resto; nenhuma soma de float | C12 |
| AC-14 | Tarefa do proprietário (§8.1) de ponta a ponta com cliques e campos medidos no log: no máximo 16 cliques e 3 campos (placa, bruto, tara); acima disso falha | `comercial_fluxo_test.py tarefa` |
| AC-15 | Toda grade com filtro e ordenação; unidade na célula; uma ação primária por tela e por estado | `comercial_fluxo_test.py`; `acoes_duplicadas.py` sem achado nas 3 telas; `acao_unica_test.py` |
| AC-16 | 390 px: cartões, sem rolagem horizontal, primária visível | `comercial_fluxo_test.py celular` (390×844) |
| AC-17 | Estoque de produto sem grade Pedidos, com reservar a partir do lote; Previsão e colheita sem as colunas comerciais | `producao_fluxo_test.py` (expectativa nova) |
| AC-18 | Build 0 FALHA; Colheita, O.S., estoque, carência, links e VE/LO ocultos sem vermelho novo contra o log da base | bateria do §7 |

**8.1 Tarefa curta para o proprietário (homologação, perfil Ana):** (1) Comercial › Contratos e pedidos, PV-030, "Reservar lote para o PV-030" com a sugestão (L10-031, 125 sc) e confira "Coberto"; (2) "Programar carga do PV-030": Bitrem graneleiro 37 t do cliente, placa, Hoje; (3) "Confirmar saída da RM-0002": bruto 51.200, tara 14.240 (pode tocar duas vezes: a baixa é uma só) → 616 sc entregues, disponível do L10-031 continua 34.420 sc; (4) Painel comercial: soja realizado R$ 128,00/sc e a receber R$ 170.318.

## 9. Fora de escopo (condição de retorno)
| Item | Volta quando |
|---|---|
| Ofertas e contrapropostas versionadas, portal do cliente, reserva temporária, confirmação automática (VE-03, PT-03/05, ATP-01/04/06) | proprietário pedir venda iniciada pelo cliente |
| Revisão de contrato com novo aceite (versões); correção de venda | primeiro pedido real de revisão na homologação (hoje: encerrar e registrar outra, D-C21) |
| Preço a fixar, basis, câmbio, alertas, cotação em tempo real (VE-02) | fonte de preço licenciada autorizada pelo proprietário (custo) |
| Faturamento, NF e documentos fiscais | integração fiscal/ERP autorizada pelo proprietário |
| Registrar recebimento, baixa e conciliação de títulos; reclamação sem retorno físico (desconto, crédito) | Financeiro (GE-05) no estado |
| Destinação do lote devolvido (descarte, reclassificação) | BEN (decisão da Qualidade) |
| Fila de caminhões, slots de doca, agrupamento de entregas, eventos de viagem, OTIF (LO-01..03, cap. 50) | volume de cargas por dia que peça fila, ou pedido do proprietário |
| Cotação, contratação, medição e rateio de frete (LO-04, 48.5) | custo realizado no Controle (CONTROLE-02) |
| Aba Motorista do MB-10 no estado (confirmar entrega pelo motorista) | proprietário pedir a entrega pelo app |
| Liberação comercial por destino registrada (`carc_liberar_lote`) e exportação com laudo | primeira venda de exportação |
| Cliente criado na tela do CD-05 aparecer na venda | CD-05 no estado (frente Cadastros) |
| Classes e embalagens do packing na venda | BEN-1 publicar lotes classificados em `c.producao` |
| Cinco referências do setor do módulo (AGENTS §3.3) | Codex registra antes do aceite; não bloqueia o código |
