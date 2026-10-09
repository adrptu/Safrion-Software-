# FRENTE-C · Realizado no plano: uma só fonte da demanda líquida, por fazenda (SAF etapa 6 = CMP etapa 2 = Mapa › Insumos)

Severidade: S2

Dano: Cálculo material errado nos dois sentidos, conferido na semente. Compra em dobro: Fungicida A 145,2 L (R$ 21.054) e Adjuvante 2,5 L. As atividades já estão na OS-0421, que tem 160 L entregues. Compra a menos: MAP 17.500 kg (R$ 68.250), porque a Compra ignora a OS-0420 (T4, em execução), e Ureia 1.140 kg (R$ 3.534) da OS-0418. A Lagoa Grande também compra a menos, porque a SAF e a CMP dela contam lotes que só existem na Santa Rita: Glifosato 1.200 L, Óleo mineral 400 L e Nitrato de cálcio 1.000 kg. Faltam 293,34 L de Glifosato a partir de 30/09 (OS-0501), 400 L de Óleo e 1.000 kg de Nitrato. O Mapa usa outra conta e diverge da Compra: Fungicida A 194 contra 145,2 L, porque desconta a reserva duas vezes; e Óleo 903 contra 210 L. Os 313 L de Glifosato e os 26.437 kg de Nitrato que o Mapa mostra somam as fazendas e acertam o total. Quem erra ali é a Compra da Lagoa Grande.

PRD: RN-006 (PRD l.208: a parcela convertida em ordem deixa de ser demanda do plano); AC-08 (l.4768); RN-008 (l.210); CAL-01 (l.4199–4201: o consumo realizado sai do físico e da demanda; a custódia só cobre o destino autorizado); RN-011 (l.213: mesmo escopo); RN-012/RN-013 (l.214–215); RN-003 (l.205: não trocar vínculo causal por coincidência); glossário l.5127–5128 (físico apto do escopo consultado, não o disponível); l.9184 (projeção por item/local; não somar plano e O.S. do mesmo consumo); ENG-011 (l.5233); DEMO-13 (l.4734); AGENTS §4 (trava só com dano nomeado).

Arquivos: tools/prototipo/v37/gen37/cal01.js, tools/prototipo/v37/gen37/safra.js, tools/prototipo/v37/gen37/dados2.py, tools/prototipo/v37/gen37/dados.py, tools/prototipo/v37/gen37/areas/inicio.py, tools/prototipo/v37/gen37/areas/processo_compras.py, tools/prototipo/v37/gen37/areas/processo_safra.py, tools/prototipo/v37/gen37/areas/mobile.py, tools/prototipo/v37/gen37/cal01_test.py, tools/prototipo/v37/gen37/saf_cmp_continuidade_test.py, tools/prototipo/v37/gen37/cmptest.py, tools/prototipo/v37/gen37/tabelas_saf_test.py, tools/prototipo/v37/gen37/map_decisoes_test.py, scratchpad/ctl/fc_cet/impl2.py, scratchpad/ctl/fc_cet/impl3.py, scratchpad/ctl/fc_cet/dem_js_v2.js, scratchpad/ctl/fc_cet/negativos3.py, scratchpad/ctl/fc_cet/parity2.py, scratchpad/ctl/fc_cet/run2.py, scratchpad/ctl/fc_cet/run_mapa2.py, scratchpad/ctl/fc_cet/c1b_aplicar_plano.py, scratchpad/ctl/fc_cet/c2_estoque_fazenda.py, scratchpad/ctl/fc_cet/c3_mapa_talhao.py, scratchpad/ctl/fc_cet/c4_n4_real.py, scratchpad/ctl/fc_cet/c5_n12.py, scratchpad/ctl/fc_cet/c6_dividir.py, scratchpad/ctl/fc_cet/c7_escopo.py, scratchpad/ctl/fc_cet/c8_pc090.py, scratchpad/ctl/fc_cet/c9_ureia_just.js

# Frente C · Realizado no plano: desenho corrigido

**Base:** `sp-tab5` 884620c (branch `claude/v44-tabelas-05`), PRD v3.9, AGENTS.md. Nenhum arquivo do repositório foi editado e nenhum navegador foi aberto.

**Rótulos:**
- *executado*: saiu de python ou node. Os scripts estão em `scratchpad/ctl/fc/` (desenho original) e em `scratchpad/ctl/fc_cet/` (contestação).
- *lido*: conferido no código, sem rodar.
- *especificado*: ainda não rodou.

A regra corrigida foi conferida no espelho `ctl/fc_cet/impl3.py`, que muda o `dados2` só em memória, e em `ctl/fc_cet/dem_js_v2.js`.

## 0. Resumo
Hoje a demanda trata como realizado tudo o que o plano marcava para antes de hoje (`cal01.js:14`), e as O.S. não contam. A SAF e a CMP da Lagoa Grande usam o estoque da Santa Rita (`dados2.py:799-801`). O Mapa tem uma conta própria (`inicio.py:335-373`).

A correção:
- A O.S. emitida substitui a parte do plano que ela cobre. O que ela cobre é a atividade da chave dela, nos talhões dela. Essa parte passa a contar pelo que a O.S. ainda vai tirar do almoxarifado: dose × saldo − custódia.
- O resto do plano continua contando.
- A O.S. sem vínculo com o plano também conta.
- O estoque e os recebimentos são os da fazenda da safra.
- A mesma função atende SAF etapa 6, CMP etapa 2 e Mapa: JS em `cal01.js` e espelho em `dados2.py`, com teste de paridade.

## 1. Problema reproduzido (executado)
`python3 ctl/fc/repro.py`, Safra 2026/27:
```
Fungicida A: estoque(fís. apto) 545 · plano 625.20 · líquida 145.20 · falta 2026-12-17 · R$ 21054.00
   own c1|a6 80.0 / c3|a6 149.0 / c2|a6 91.2 (29/11–09/12)   ← chaves da OS-0421 (Em execução, 190 de 350 ha, REQ-035 160 L entregues, 65 L em custódia)
MAP 11-52: estoque 90000 · plano 152500 · líquida 62500           ← sem a OS-0420 (T4, sem plano, saldo 70 ha = 17.500 kg)
Ureia 45% — sem demanda na S2627                                   ← OS-0418 (P1) pede 1.140 kg, estoque 0
```

`python3 ctl/fc_cet/c2_estoque_fazenda.py` mostra os lotes do cenário:
- Glifosato G26-14 fica no Almox. defensivos; Óleo O26-05 também; Nitrato ND26-16 fica no Galpão 1. Os três são da Santa Rita.
- A Lagoa Grande não tem lote desses três insumos (`dados_lagoa_safra.ESTOQUE`).

Mesmo assim, o LG2627 calcula com eles. Antes e depois de usar o estoque da própria fazenda:

| Insumo | Líquida com o estoque da Santa Rita | Líquida com o estoque da Lagoa Grande |
|---|---|---|
| Glifosato | 0 | 293,34 L a partir de 30/09/2026 (OS-0501, 147,93 L) |
| Óleo mineral | 292,81 L | 630,02 L |
| Nitrato de cálcio | 24.756,8 kg | 25.756,8 kg |

`python3 ctl/fc/repro_mapa.py` reproduz o Mapa (`inicio.py:336-372`):
- Fungicida A: o Mapa diz "Falta 194 L" e a CMP diz 145,2 L. O Mapa usa o disponível de 480 L e conta de novo os 64 L da OS-0424, que já estão reservados. Isso viola o glossário l.5128.
- Glifosato: o Mapa diz "Falta 313 L" e a CMP diz 20 L. Os 313 L são 20 da Santa Rita mais 293 da Lagoa, que não tem lote. O total do Mapa está certo.

Baseline executado: `python3 cal01_test.py` dá **43 ok · 2 falhas já no HEAD**. As duas falhas são expectativas velhas do LG2627.

## 2. Regras novas (testáveis)

| ID | Regra | Dano que evita | Fonte |
|---|---|---|---|
| **DEM-01** | **Escopo da O.S.** = as atividades das chaves dela × os talhões dela (o próprio cultivo ou as parcelas do talhão, pela regra de `processo_safra.py:50-51`). Para cada ocorrência do plano dentro do escopo, `f = máx(0, 1 − Σ área das O.S. não canceladas ÷ área das ocorrências do escopo)`. Quando o escopo tem mais de um cultivo, a memória diz "rateados pela área". | Compra em dobro (Fungicida A 145,2 L). Dividir um talhão com o mesmo plano não muda a demanda (`partest.py:68`). | RN-006, AC-08, RN-008, DEMO-13 |
| **DEM-02** | A O.S. em A liberar, Liberadas ou Em execução conta pelo pendente: `máx(0, quantidade(dose, saldo) − custódia da requisição)`. Sem realizado, usa o total da versão. A data é `máx(hoje, início da janela)`. Em conferência e Encerradas: pendente 0, mas o escopo continua coberto. Canceladas não cobrem nada. | Contar de novo o que já saiu do estoque ou já foi aplicado. | CAL-01 l.4201, RN-013 |
| **DEM-03** | A O.S. aberta sem chave conta pelo pendente e nunca some. A linha avisa só quando o plano do mesmo talhão usa o **mesmo produto**. | Compra a menos (MAP 17.500 kg, Ureia 1.140 kg) sem alarme falso. | RN-012, l.9184 |
| **DEM-04** | A reserva de uma O.S. contada pela DEM-02 é "a mesma demanda". A chave da reserva passa a ser o ID da ordem. | Contar duas vezes os 64/65 L da OS-0424. | CAL-01, AC-13 |
| **DEM-05** | SAF 6, CMP 2 e Mapa mostram a mesma líquida por fazenda. "Safra toda" é a líquida da safra. "Próximos 30 dias" é a mesma conta com os eventos até hoje + 30. No Mapa por talhão, a O.S. de vários talhões é rateada pela área, e a soma dos talhões fecha com a fazenda. | Comprar por números diferentes em telas diferentes. | ENG-011, l.9184 |
| **DEM-06** | O uso do plano com data passada e sem O.S. continua fora da demanda, mas deixa de se chamar "realizado". | Afirmar execução sem registro. | RN-003 |
| **DEM-07** | O físico apto e os recebimentos são os da fazenda da safra. Estoque de outra fazenda não cobre a demanda. | Compra a menos na Lagoa Grande (Glifosato 293 L a partir de 30/09). | RN-011, l.5127, l.9184 |
| **DEM-08** | Na Compra (etapa 4), quando nenhuma proposta chega antes da falta, a escolha padrão é a que chega primeiro (empate: menor custo), **sem justificativa obrigatória**. O aviso "chega depois da falta" continua. Quando existe proposta a tempo, a trava atual fica. | A trava sem dano que a Ureia passaria a disparar: "Enviar à Direção" e "Aprovar compra" ficariam bloqueados sem alternativa possível. | AGENTS §4, CAL-01 (l.9182: pedir antecipação ou alternativa) |
| **DEM-09** (acrescentada na implementação, 09/10) | Com a demanda viva (SAF e Mapa leem as O.S. do cenário), ela pode baixar depois do envio da solicitação (O.S. cancelada, plano mudado). No Planejar safra (etapa 4), o insumo que a SOL pede acima da líquida de agora fica "Acima da demanda · <diferença>", inclusive o que saiu da demanda; a primária vira "Atualizar <SOL>" e a versão nova tira só a diferença (o complemento continua subindo o que falta). Com pedido já emitido a SOL não muda: a linha só avisa e o excedente entra no estoque. Regra em `cal01.js` (`demSolSit`, `demSolRevisar`); a Compra lê o registro da versão inteiro. | Compra a mais em silêncio: OS-0418 cancelada depois do envio e a SOL-2026-07 seguia cotando 1.140 kg de Ureia (R$ 3.534,00), sem sinal no Planejar safra e com R$ 430.255,00 na Compra. | RN-006, AC-08, CAL-01, AGENTS §4 |

A OS-0420 recebe a chave da própria origem, `c4|a3`. As fontes:
- `processo_os.py:120`: "Soja alta tecnologia v6 · REC-014 v2 · Plantio e adubação de base";
- `campo.py:348`: "T4, 1ª onda de 100 ha dos 204 ha da NEC-028".

Sem plano no T4, a ordem conta inteira (N7). Com o plano aplicado, ela cobre 100 de 204 ha.

**Padrões adotados (o proprietário pode mudar):**
- **PA-C1 (DEM-06):** o passado sem O.S. é tratado como histórico. A Lagoa Grande mantém as 11 calagens (1.185.680 kg). No software real, isso passaria a "atrasado".
- **PA-C2:** a O.S. de várias chaves sem área por chave usa rateio pela área. No software real, a O.S. traz a área de cada chave.
- **PA-C3:** a O.S. sem vínculo conta a mais, com aviso, em vez de sumir.
- **PA-C4 (DEM-08):** sem proposta a tempo, o padrão é a que chega primeiro, sem justificativa.
- **PA-C5 (DEM-09):** a redução da SOL não pede confirmação extra: é a primária da etapa 4 e nomeia o insumo e a diferença. A Compra recomeça a cotação na versão nova, como já faz no complemento.

A entrada de Controle transversal fica para depois (padrão 3 do pedido).

## 3. Mudança de código por arquivo (especificado)

**`gen37/cal01.js`**
- `:5-7`: o comentário passa a citar DEM-01..07.
- `:47`: o texto vira `'Antes de '+d(r.hoje)+' sem O.S. · '+r.nreal+(r.nreal>1?' usos':' uso')+' · '+n(r.real)+u+' · fora da demanda (histórico do plano; se ainda vai acontecer, emita a O.S.)'`.
- Ao fim, entram `demRestante(osd, occ)` e `demOsEvs(osd, prod, saf, ordem, talProd)`.
  - `occ`: `[{k:'cultivo|atividade', a, local, tal, area}]` das safras abertas da fazenda.
  - Escopo: `ats[x.a] && (ts[x.local] || ts[x.tal])`.
  - `demOsEvs` é a do desenho, com uma diferença: o aviso usa `talProd[saf][talhão][prod]`.
  - Versão conferida: `ctl/fc_cet/dem_js_v2.js`.

**`gen37/safra.js` `demanda()` (`:338-353`)**
- Monta `occ` das safras abertas da fazenda com `ocorr(self,r.id)`, usando `tal = o.c.v.talhao`. Monta também `talProd` (talhão → produtos do plano).
- `fr = demRestante(osd, occ)`, com `osd = D2.osdem.filter(o=>o.faz===faz)`.
- O evento do plano passa a `q = p.dose × área × f`, com `t` "· parte sem O.S. (…)". Quando `f=0`, o evento é pulado.
- Os insumos usados só pelas O.S. são criados **antes** do laço das outras safras (`:344-346` só aceita `m[p.nome]` existente). Em seguida vêm os eventos `demOsEvs`.
- Linha `:350`: os recebimentos passam a `x.item===d.nome && x.faz===faz`.
- Linha `:352`: `d.est = ((D2.fisico||{})[faz]||{})[d.nome]||0`. Sem cair no estoque das duas fazendas somadas.

**`gen37/dados2.py`**
- Nova `os_dem()`, com cache, como no desenho:
  - import tardio de `cenario` e `areas.processo_os`;
  - DEM-02 com `quantidade.qtd`;
  - `loc` = nomes dos talhões da ordem.
- Novas `dem_restante(osd, occ)` e `dem_os_evs(...)`, espelhos das funções JS.
- `occ` sai das **mesmas ocorrências da demanda**: `_ocorr_py(s, AJUSTES, planos_extra se s==safra)` com o talhão por `talhao_de`. O espelho do desenho ignorava `planos_extra` em `area_k` e divergia do JS vivo.
- Estoque por fazenda (DEM-07):
  - `EST_FAZ={'Lagoa Grande':dict(_DL.ESTOQUE),'Santa Rita':<o literal de :109>}`;
  - `fisico_apto(item, faz)` = `EST_FAZ[faz].get(item,0)` + reservas da fazenda;
  - `RECEB_DT` ganha `faz` (os PEDIDOS são da Santa Rita; o calcário previsto é da Lagoa Grande);
  - `_outras_origens(safra,nm,fr)` filtra os recebimentos pela fazenda e aplica `f`.
- `RESERVAS` (`:798`): `chave='OS-0424'`.
- `js_data()` (`:677-680`): `osdem=os_dem()` e `fisico={faz:{item:fisico_apto(item,faz)}}`.
- Nova `situacao_insumos(dem, lim30)`, com `cal01` com e sem recebimentos, para o Mapa.
- **Não remover** `demanda_datada`, `falta_a_partir` e `faltas`: `verif_cmp1.py:11` chama `D.faltas()`.

**`gen37/dados.py`**
- `:93`: a OS-0420 ganha `chave='c4|a3'`.
- `:85-86`: o comentário cita a OS-0420.
- A semente do cenário não copia chaves (`cenario.seed()['ordens']['OS-0420']` não tem `keys`), então `v` não sobe.

**`gen37/areas/inicio.py`**
- Saem `_nec`, `_nec_cult` e `_fazst` (`:335-373`) e as linhas `:465-466`.
- `NEC` e `FAZST` vêm de `D2.demanda` por fazenda (S2627 e LG2627).
- `NEC[t]`: o evento com vários talhões é rateado pela área (DEM-05). O pseudo-código do desenho, `NEC[_tid(loc)]`, dá `TypeError: unhashable type: 'list'` (executado em `c3_mapa_talhao.py`).
- JS `:734`, `:784` e `:895`: `M.fazst[f.per]` vira `(M.fazst[FAZ]||{})[f.per]`.

**`gen37/areas/processo_compras.py`**
- `:235` (DEM-08): `ref = props.find(p=>!p.late) || <a que chega primeiro; empate: menor custo>`.
- `:237`: `naoMenor = !!(ch && ((ch.late && props.some(p=>!p.late)) || (ref && ch.f!==ref.f && ch.unit>ref.unit+1e-9)))`.
- `:319`: `'realizado: '` vira `'antes de hoje sem O.S.: '`.

**`gen37/areas/processo_safra.py:195`:** a coluna `'Já realizado'` vira `'Antes de hoje sem O.S.'`.

**`gen37/areas/mobile.py`** (MB-05, módulo oculto, aberto pelo passo da ordem):
- `:65`: `PLAN_FA` e `PEND_FA` passam a vir de `D2.demanda('S2627')`, como `suprimentos.py:73-74`.
- `:667`: com pendência 0, o cartão sai do vermelho e diz "sem pendência na SOL-2026-07". Hoje o texto fixo "pendência de 145,2 L" contradiria a CMP.
- `:38`: a docstring acompanha.

`cenario.py` e `cenario.js` não mudam.

## 4. Textos de tela (executado com `cal01Memo` em `ctl/fc/memo.py`)
- **Memória da O.S.:**
  `23/09/2026 · T1+T2 · OS-0421 · Fungicida 1ª aplicação · 0,50 L/ha × 160 ha − 65 L em custódia = 15,0 L → saldo 530 L`
- **Reserva da mesma ordem:**
  `24/09/2026 · Reserva REQ-039 · OS-0424 (P2) · 65,0 L da mesma demanda, contados uma vez`
  Em seguida: `24/09/2026 · P2 · OS-0424 · Fungicida · 0,80 L/ha × 80 ha = 64,0 L → saldo 466 L`
- **Parte do plano sem O.S.:**
  - `29/11/2026 · T1-A · Fungicida 1ª aplicação · parte sem O.S. (OS-0421 cobre 350 de 610 ha, rateados pela área) · 0,50 L/ha × 68,2 ha = 34,1 L → saldo 431,9 L`
  - `18/10/2026 · T2 · Plantio e adubação de base · parte sem O.S. (OS-0431 cobre 102 de 298 ha) · 250,00 kg/ha × 196 ha = 49.000,0 kg → saldo 0 kg · falta 42.000 kg`
- **Insumo que só a O.S. usa:**
  `24/09/2026 · P1 · OS-0418 · Fertirrigação de nitrogênio · 12,00 kg/ha × 95 ha = 1.140,0 kg → saldo -1.140 kg · ruptura 1.140 kg`
  Em seguida: `30/09/2026 · Reposição com chegada viável · +1.140,0 kg`
- **O.S. sem vínculo**, só quando o plano do talhão usa o mesmo produto:
  `… · sem vínculo com o plano do talhão: se for o mesmo uso, retire o produto do plano do talhão (etapa 2)`
- **Histórico:**
  `Antes de 23/09/2026 sem O.S. · 11 usos · 1.185.680 kg · fora da demanda (histórico do plano; se ainda vai acontecer, emita a O.S.)`
- **Mapa, Santa Rita:**
  - T1: `Fungicida A · 236,6 L`, Estoque cobre.
  - T2: `Fungicida A · 219,8 L`.
  - T4: `MAP 11-52 · 17.500 kg`, Falta 80.000 kg.
  - Detalhe do MAP: `precisa de 170.000 kg · estoque apto 90.000 kg · falta a partir de 18/10/2026 · Suprimentos compra na Compra de insumos`, com a ação "Comprar".
  - Pedido a receber: `Pedido a receber · PC-088 · 02/10`.
- **Mapa, Lagoa Grande:**
  - PV13: `Glifosato 480 · 147,9 L`, Falta 293 L.
  - PV02: Nitrato de cálcio, Falta 25.757 kg.
- **Compra (etapa 4), Ureia:** a escolha padrão vem sem selo de justificativa. O resumo diz "1 escolha chega depois da falta".

## 5. Testes

### 5.1 Unitário (node e python, sem navegador)
Executado no espelho `ctl/fc_cet/impl3.py`. Proposta: virar a seção 4 do `cal01_test.py`.

**Paridade:**
- `parity2.py`: `demRestante` com escopo dá frações e textos iguais em JS e Python.
  - Santa Rita: c1, c2 e c3|a6 com 0,42623; c3|a3 com 0,65772; c9|k1, c1|a1 e as 6 chaves da Lagoa com 0.
- `run2.py`: `cal01.js` = Python nos eventos corrigidos (S2627 19 insumos, S27SF 8, LG2627 14).
- `run_mapa2.py`: a soma dos talhões fecha com a fazenda em todos os insumos.

**`negativos3.py`: 20 ok · 0 falhas.**

Positivos:
- P1: Fungicida A 145,2 → 0 L; pendente da OS-0421 = 15 L.
- P2: MAP 80.000 kg a partir de 18/10/2026.
- P3: Ureia 1.140 kg a partir de 24/09/2026.
- P4: S2627 com 14 insumos · R$ 430.255,00.
- P5: S27SF Fungicida A 22,98 L · R$ 1.094.946,91.
- P6: LG2627 com **13 insumos · R$ 1.614.202,52**.

Negativos:
- N1: com a chave inteira, o MAP cairia para 31.000 kg.
- N2: OS-0431 cancelada devolve 74.500 kg a c3|a3.
- N3: OS-0421 em conferência deixa as chaves a6 com 136,48 L, nunca 320,2 L.
- **N4 (real):** chama `os_dem` com custódia de 200 L e dá pendente 0. O N4 do desenho recalculava a fórmula dentro do próprio teste.
- N5: saldo de 466 L em 24/09.
- N6: OS-0501 fora da Santa Rita.
- N7: chave fora do plano não dá erro.
- N8: 400 ha numa chave de 298 dão fração 0.
- N9: OS-0430 igual ao plano não muda nada.
- **N10:** Nitrato de cálcio fica Santa Rita 680 kg e Lagoa Grande 25.756,8 kg.
- **N11:** Lagoa Grande Glifosato 293,34 L a partir de 30/09, com estoque 0, nunca "Estoque cobre".
- **N12:** com "Aplicar plano em 4 cultivos", o MAP do T4 dá 26.000 + 17.500 = 43.500 = (204 − 30) × 250, nunca 68.500. MAP 173.750 kg · R$ 1.205.541,91.
- **N13:** P2 com plano e a OS-0424 sem chave: a ordem conta e avisa; Fungicida A 55,48 L.
- **N14:** dividir T2 em 3 parcelas com o mesmo plano mantém valor e líquidas iguais.

Contraprovas:
- N12 falha com a OS-0420 sem chave: 68.500 kg (`c1b_aplicar_plano.py`).
- N14 falha com a DEM-01 por cultivo: R$ 432.858,25 e MAP 80.667,5 (`c6_dividir.py`).
- N10 e N11 falham sem a DEM-07.

### 5.2 Navegador (especificado)
- **Estender `map_decisoes_test.py`**, em vez de criar um arquivo novo:
  - Santa Rita, Safra toda: `Produtos no período 19 · Faltam 14 · Aguardando pedido 3 · Estoque cobre 2`.
  - T1: `Fungicida A · 236,6 L` com "Estoque cobre".
  - T4: `MAP 11-52 · 17.500 kg` com "Falta 80.000 kg".
  - Santa Rita, Próximos 30 dias: MAP "Falta 42.000 kg" e Óleo "Estoque cobre".
  - Lagoa Grande, Safra toda: `14 · 13 · 1 · 0`.
  - PV13: Glifosato "Falta 293 L".
  - Negativo: nenhum "Falta 194 L" ou "Falta 903 L".
  - Sem erro de JS.
- **`saf_cmp_continuidade_test.py`:**
  - #21 reescrito: Fungicida A com 0 e as linhas da memória acima.
  - Negativo: Fungicida A e Adjuvante fora da SOL-2026-07.
  - #30: MAP 80.000 kg com falta em 18/10; memória igual na SAF e na CMP; Ureia 1.140 kg em 24/09.
  - #31: nenhum "Realizado antes" e nenhuma coluna "Já realizado".
- **`cmptest.py`**, caso novo: a Ureia sai sem justificativa pendente; o resumo da etapa 4 diz "1 escolha chega depois da falta"; "Enviar à Direção" segue.
- **Comando:** `python3 build.py && python3 montar_render.py && python3 cal01_test.py && python3 saf_cmp_continuidade_test.py && python3 cmptest.py && python3 tabelas_saf_test.py && python3 partest.py && python3 map_decisoes_test.py`. Depois, a bateria completa (`00-bateria.sh`, `ls *test*.py`) sem falha nova.

### 5.3 Testes que mudam de expectativa (lista completa)
- **`cal01_test.py`:**
  - `:88`: o texto da DEM-06.
  - `:93`: S2627 **(14, 430255.00)**, S27SF **(8, 1094946.91)** e LG2627 **(13, 1614202.52)**.
  - `:100-101`: Fungicida A vai a 0, mantendo estoque 545 e reservado 65.
  - `:104-107`: o calcário passa a **literais conferidos**: real 1.185.680, bruta 96.940, líquida 0, falta 25/09, ruptura 36.940, coberta em 30/09. O texto vira "96,94 t … ruptura de 36,94 t". Valores derivados do próprio código seriam tautologia.
- **`saf_cmp_continuidade_test.py`:**
  - `:61`, `:72`, `:75`, `:84`, `:92` e `:94-95`: S27SF R$ 1.094.946,91 e S2627 R$ 430.255,00. O desenho citava só #2 e #14.
  - `:135-141`: #21.
  - `:166-169`: #28, coluna "Antes de hoje sem O.S.".
  - `:171-172`: #29, `Antes de 23/09/2026 sem O.S. · `.
  - #27 (paridade LG) passa com o físico por fazenda no JS.
- **`cmptest.py`:**
  - `:56`: R$ 430.255,00.
  - `:58`, `:77` e `:104`: 62.500 vira 80.000.
  - `:102`: 70000 vira 90000.
  - `:124`: 62500 vira 80000.
  - **`:148` e `:151`: "18/10/2026" vira "15/10/2026".** Com as O.S. na demanda, a Semente 58 W falta no 1º plantio (T1-A, 15/10) quando o PC-090 vai para 20/10. Executado em `c8_pc090.py`.
  - `:169-181`: Fungicida A vira Fungicida TS (41 L, grupo Fungicidas).
  - `:133` continua válido: com MAP 40 t, o total fica abaixo de R$ 300 mil mesmo no fator máximo (1,04 × 274.255).
- **`tabelas_saf_test.py`:**
  - `:128-129`, `:137-138` e `:142-143`: "62.500 kg" vira "80.000 kg".
  - `:130` (QT6): "ANTES DE HOJE SEM O.S.".
- **`partest.py`:** sem mudança. O invariante `:68` continua passando pela DEM-01 por escopo; com o desenho original, falharia.
- **Fora da bateria** (o nome não tem "test"): `verif_cmp1.py`, `verif_ce_cmpA.py` e `verif_cmp3.py` fazem conta só com o plano. Ficam obsoletos e vão para uma tarefa de limpeza.

## 6. Riscos de regressão
1. **Semente estática.** SAF, CMP e Mapa leem as O.S. e o estoque da semente, como hoje. Cancelar, ajustar, criar ordem e conciliar não aparecem até haver leitura viva (fatia seguinte, P2).
2. **`localStorage talhao-os-compras-v1` antigo** mostra a SOL anterior até ser reenviado. Nos testes, limpar a chave.
3. **Telas que mudam de número:**
   - SU oculta (`suprimentos.py:73-74`);
   - MB-05 (`mobile.py:65,667`);
   - CD-05 (`parceiros.py:51-54`): Fertilizantes com 5 itens;
   - `pttest.py:30` digita "4 itens" (texto, não asserção).
4. **Rateio e dupla contagem visíveis:**
   - o rateio da OS-0421 (PA-C2) aparece escrito na memória;
   - a dupla contagem possível fica só nas ordens sem origem (OS-0424, OS-0418), com aviso apenas quando o plano do talhão usa o mesmo produto.
5. **Fora do escopo** (tarefas próprias):
   - `cenario.js:42` (`cenLote`) entrega de lote de qualquer fazenda;
   - `processo_os.py:794` impede emitir O.S. para a parte sem O.S. de uma chave já coberta (RN-008);
   - a 2ª onda da NEC-028 (104 ha do T4) só entra com o plano aplicado no T4 (a SAF já aponta "4 cultivos sem plano");
   - incoerências da semente: a OS-0421 aplica antes do plantio, e o Adjuvante e o MAP não estão nas requisições.

## 7. Tamanho estimado
- **Produto:** cerca de +125 e −45 linhas. dados2 +80, cal01.js +12, safra.js +12, inicio.py +15/−41, compras 2, mobile 3, dados 1, mais 2 rótulos.
- **Testes:** cerca de +110 novas (cal01_test +90, map_decisoes +20) e cerca de 45 alteradas.

## 8. Evidência (executado, em `scratchpad/ctl/fc_cet/`)
- Reprodução dos furos do desenho:
  - `c1b_aplicar_plano.py`: dupla contagem no T4;
  - `c2_estoque_fazenda.py`: estoque da outra fazenda;
  - `c3_mapa_talhao.py`: `TypeError` e dupla contagem por talhão;
  - `c6_dividir.py`: invariante do partest;
  - `c8_pc090.py`: 18/10 vira 15/10;
  - `c9_ureia_just.js`: trava da justificativa.
- Espelho corrigido: `impl2.py`, `impl3.py` e `dem_js_v2.js`.
- Conferência:
  - `negativos3.py`: 20/20;
  - `parity2.py`: True;
  - `run2.py`: paridade True nas 3 safras;
  - `run_mapa2.py`;
  - `c4_n4_real.py`;
  - `c5_n12.py`;
  - `c7_escopo.py`: escopo mantém os valores e o invariante, e a edição de T2 para 102 ha dá MAP 31.000 kg a partir de 25/10 · R$ 211.860,60 · 13 insumos.
- Lido sem executar: o bloqueio de "Enviar à Direção" e "Aprovar compra" por `podeAprovar` (`processo_compras.py:440-445`).
- Não feito: nenhuma edição no repositório e nenhum teste de navegador.

---

## Contestações: aceitas · recusadas

**Aceitas (mudaram o desenho):**
1. **A OS-0420 sem chave cria compra em dobro no caminho principal da SAF.** "Aplicar plano em 4 cultivos" é a ação primária da etapa 2 (`acao_unica_test.py:105`). Com ela, o T4 soma 51.000 kg do plano e 17.500 kg da OS-0420: 68.500 kg, quando o físico pede 43.500. São R$ 146.900 a mais (R$ 1.352.441,91 contra R$ 1.205.541,91), o mesmo dano que a frente quer evitar. Correção: a chave de origem `c4|a3`, declarada em `processo_os.py:120` e `campo.py:348` (AC-08). Executado: N12.
2. **A DEM-01 por cultivo quebra `partest.py:68`.** Dividir T2 em 3 parcelas leva o valor de R$ 430.255,00 a R$ 432.858,25 e o MAP a 80.667,5 kg. Correção: o escopo da O.S. passa a ser a atividade × os talhões da O.S. Executado: N14 e paridade JS = Python.
3. **A DEM-05 sem estoque por fazenda piora o Mapa da Lagoa Grande.** O Glifosato passaria de "Falta 313 L" (total certo) para "Estoque cobre" sem lote na fazenda, com a OS-0501 precisando de 147,93 L em 30/09. Correção: DEM-07 (RN-011, l.5127, l.9184). Executado: N10 e N11, LG2627 R$ 1.614.202,52 · 13 insumos. O texto do dano foi reescrito: 313 L e 26.437 kg não eram erro do Mapa.
4. **Mapa por talhão.** `NEC[_tid(loc)]` com lista dá `TypeError`. O "T1 244,0 L" esperado põe os 15 L da OS-0421 só no T1; iterar por talhão dobraria (535,48 L contra 520,48 L). Correção: rateio pela área. Ficam T1 236,6 L e T2 219,8 L, e a soma fecha com a fazenda.
5. **A Ureia entra na SOL e trava a aprovação.** Nenhuma proposta de Fertilizantes chega até 24/09 (01/10, 05/10, 08/10). A escolha padrão viraria "atrasada" com justificativa obrigatória, e `podeAprovar` bloquearia "Enviar à Direção" e "Aprovar compra". Isso quebraria `cmptest.py:131`, `:156` e `:182`, e seria uma trava sem dano. Correção: DEM-08 e PA-C4. A lógica foi executada isolada (`c9_ureia_just.js`); o navegador fica especificado.
6. **Remover `faltas` quebra `verif_cmp1.py:11`.** O grep do desenho estava errado. As três funções ficam, e a limpeza vai para tarefa própria.
7. **Lista de testes incompleta.** Faltavam `saf_cmp_continuidade_test.py:72`, `:75`, `:84` e `:92`, `cmptest.py:148` e `:151` (18/10 vira 15/10) e o LG (13, 1.614.202,52).
8. **N4 tautológico.** Agora chama `os_dem` com a semente alterada.
9. **Expectativas "derivadas" do calcário** viram literais conferidos.
10. **`mobile.py:65,667`** mostrava "pendência de 145,2 L na SOL-2026-07" fixo, contradizendo a CMP. Passa a vir da mesma fonte.
11. **O espelho montava `area_k` sem `planos_extra`** e divergia do JS vivo. A especificação agora usa as mesmas ocorrências da demanda.
12. **Aviso falso da O.S. sem vínculo.** P1 com SOJA-AT, que não usa Ureia, avisava na linha da OS-0418. Agora o aviso só aparece com o mesmo produto.
13. **Teste novo de 80 linhas para o Mapa.** Vira asserções Python mais a extensão de `map_decisoes_test.py`.
14. **Texto da memória da Ureia** corrigido para a saída real ("→ saldo -1.140 kg").

**Recusadas (ficam como no desenho):**
1. **Rateio pela área para a OS-0421 (PA-C2).** A semente não tem a área por chave. "T1 primeiro" seria inventar. A memória declara o rateio.
2. **Passado sem O.S. como histórico (PA-C1).** Contar como atrasado somaria 1.185.680 kg de calcário e outros insumos na Lagoa Grande. Fica como padrão adotado.
3. **O.S. sem chave conta mais aviso (PA-C3).** Casar por produto seria vínculo por coincidência (RN-003) e compraria a menos: a OS-0424 de setembro não é a aplicação de DAP+45 do plano (N13).
4. **Espelho JS/Python (ENG-011).** É o padrão do protótipo, com teste de paridade. O pendente só existe no Python (`os_dem`).
5. **Leitura estática da semente.** Não regride em relação ao HEAD; fica como fatia seguinte.
6. **NEC-028, bloqueio da Nova ordem e `cenLote` entre fazendas.** São problemas reais, mas de outra origem. Vão para tarefas próprias e não entram nesta frente.