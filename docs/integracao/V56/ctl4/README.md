# V56 × CTL-4 · junção da CTL-4 corrigida, ajustes da revisão e aceite CTL-4-FIX (executado)

**Estado (13/10/2026):** candidata `211b3df` = `12dfaef` (código do `7e74e6d`) + os 4 ajustes S3 da revisão do Codex na CTL-4 (CTL4-FIX-REV-20261013-01, junção `3353f86`) + regressão J5 (`45a68b2`) + 1 teste obsoleto corrigido (`211b3df`). Aceite itens 2 e 5 e testes na seção 8; vermelho novo restante: nenhum.

Regime leve do protótipo (AGENTS.md 3.5). Integrador: Claude. Data: 13/10/2026. Dados sintéticos (`SAFRION_DADOS=sintetico`). Sem push, sem publicação, sem comentário no GitHub.
Acordo do aceite: comentários 6133716339 (contrato CTL-4-FIX) e 6133809632 (ajuste do oráculo) do PR #47.

## 1. O que entrou

| Peça | Commit | O que é |
|---|---|---|
| CTL-4 (origem) | branch `claude/v44-controle-04`, base `cdc185f`, ponta `16fb55e` | demanda única que lê o estado vivo (custódia, devoluções, quarentena, realizado das O.S.) no Planejar safra, na Compra, no Mapa › Insumos, no SU-03det e no MB-05 |
| Correções da revisão do `853a6a8` | `853a6a8..16fb55e` (10 commits: `7ffe412`, `b64d556`, `e907539`, `6fce782`, `1fe0902`, `84494d7`, `4130972`, `6202376`, `78711bb`, `16fb55e`) | os 2 S2 (custódia sem uso é suprimento; quarentena é falta condicionada) e os 5 S3 da revisão; registro em `docs/controle-01/PLANO.md` §7 e `docs/controle-01/desenho/FRENTE-C.md` §10 |
| Junção | `232f3d9` (pais `302b26f` e `16fb55e`) | `git merge --no-ff 16fb55e` na `int/v56` |
| Correções de integração | `3f9e4f6`, `7e74e6d` | a Compra lê a conta viva; falta condicionada com motivo, responsável e prazo; a cotação compara com a falta da versão da SOL (seção 3) |
| Ajustes da revisão do `16fb55e` (CTL4-FIX-REV-20261013-01; PR #47, comentário 6136083713) | `16fb55e..74063d1` na `claude/v44-controle-04` (`81aef42`, `7551f1a`, `0ee25bd`, `6236d70`, `718a914`; registro `80863f9`; brutos `74063d1`) | 4 S3: falta firme e qualidade pendente juntas no Mapa, SU-03det e MB-05; cada volume reprovado com o seu laudo; o motivo do laudo não migra entre lotes; reprovação pela mesma autora da entrada marca revisão posterior (seção 8) |
| Junção dos ajustes | `3353f86` (pais `12dfaef` e `74063d1`) e regressão J5 `45a68b2` | `git merge --no-ff 74063d1`; conflitos na seção 8.2 |
| Teste obsoleto | `211b3df` | `esttest` parte 4 com o nome vigente do perfil do Rui (seção 8.4) |

Fonte: a frente inteira está na branch remota `claude/v44-controle-04` (74063d1, que contém 16fb55e) e no bundle de `docs/integracao/CTL4-FIX/`. Patch das correções: `ctl4-correcao_853a6a8..16fb55e.patch` (`git diff 853a6a8..16fb55e`, 21 arquivos, +768 −176).

### 1.1 Conflitos da junção (as duas intenções)
| Arquivo | v56 (HEAD) | CTL-4 | Resolução |
|---|---|---|---|
| `safra.js` `demanda()` | demanda do plano + D2 da montagem, com a origem da dose na memória (SOLO R21: "pela análise · LAU" / "ajustado pelo usuário") | `demFazenda(cenDemEntradas(cenGet(), …))` | a da CTL-4; a origem da dose passou para a conta única (`demFazenda` no `cal01.js` e `dem_fazenda`/`occ_faz` no `dados2.py`), e a cópia das partes fixas da SOL (`_ent`) leva `orig` e `laudo` |
| `dados2.py` `demanda()` | rótulo "(ajustado pelo usuário)" na memória | `dem_fazenda(dem_entradas(…))` | a da CTL-4, com o rótulo em `dem_fazenda` (`_dem_orig`) |
| `areas/processo_safra.py` | prefixo do cenário + `solo.js` + `SOLO_UI_JS` (SOLO) | prefixo do cenário (CTL-4) | um prefixo só, com o SOLO |
| `areas/mobile.py` | `DM.js_regras()` (v55) | `pre_extra` (demanda viva no MB-05) | os dois |
| `areas/processo_os.py` | texto da carga do BEN ("Produção › Recebimento e beneficiamento (Cargas)") | `osc_cancTxt`/`osc_cancCust` (custódia com destino ao cancelar) | os dois |

`areas/inicio.py`, `dados.py`, `cenario.js` (com o BEN), `areas/processo_estoque.py`, `areas/suprimentos.py`, `areas/parceiros.py` e `areas/processo_compras.py` juntaram sem conflito. Etapa única do Planejar safra, "Análise sugere" na dose, BEN no cenário, COM, CTL5 e DS ficaram como estavam (testes na seção 4).
`solo_unit_test` passou a conferir a origem da dose na conta única (JS e Python) e o T1-B pela parte sem O.S. (152 × 260/610 = 64,79 ha): 128/128.

Build 138 quadros, 0 FALHA; render 145 páginas; sintaxe JS 145/0 (em `232f3d9`, `3f9e4f6` e `7e74e6d`); varredura 145/145 em `232f3d9` e em `7e74e6d`.

## 2. Aceite CTL-4-FIX item a item · base `0c0931f` × candidata `7e74e6d` (executado)

Base: medida antes, sem refazer (`contraprova-v55/` e `reproducao-versoes/`). Candidata: pela tela, com o storage limpo e o perfil Ana, com os comandos das próprias telas; o motor (`m_s2.py`, node com `cenario.js`, `cal01.js` e as funções `osc_*` reais) nas mesmas entradas. Valores antes/depois em `aceite/aceite_7e74e6d.json` e `aceite/7e74e6d/valores.json` (roteiro da contraprova sem mudança); a conferência automática (`aceite/harness/confere.py`) deu **22/22** (`aceite/aceite_resultado_7e74e6d.json`, `aceite/confere_7e74e6d.txt`). A mesma rodada no `3f9e4f6` (`aceite/intermediarios/3f9e4f6/`) deu 22/22 com os mesmos números (só a hora do cancelamento muda).

### Item 1 · devolução REQ-031, 500 kg de MAP 11-52 (OS-0417 Em conferência)
| Leitura | Base `0c0931f` (antes → depois) | Candidata `7e74e6d` (antes → depois) |
|---|---|---|
| Planejar safra · necessidade líquida | 62.500 → 62.500 kg | **79.500 → 79.500 kg** (igual: a custódia livre já conta) |
| Planejar safra · estoque apto | 90.000 → **90.000** kg (não via a devolução) | 90.000 → **90.500** kg |
| Memória | "Estoque apto hoje: 90.000 kg" nos dois | antes "90.000 kg + 500 kg em custódia sem uso nas O.S., a devolver ao Estoque (500 kg · REQ-031 · OS-0417 (em conferência)) = 90.500 kg"; depois "90.500 kg" — os 500 kg contam uma vez |
| Compra · estoque apto / necessidade | 90.000 / 62.500 nos dois | 90.000 / 79.500 → 90.500 / 79.500 |
| Estoque · lote M26-07 e custódia | físico 90.000 → 90.500; custódia 500 → 0 | físico 90.000 → 90.500; custódia 500 → 0; disponível 90.000 → 90.500 (enquanto estão com a OS-0417, os 500 kg ficam "em custódia (fora do depósito)" e não ficam livres) |
| Mapa › Insumos (T4) | "Falta 80.000 kg" (≠ 62.500 do Planejar safra; `reproducao-versoes/RELATORIO.md`, ressalva 5) | "Falta 79.500 kg" → "Falta 79.500 kg" |
| Portal do parceiro (SOL) | MAP 62.500 kg (o `pttest` da base espera o total 293.166,01) | MAP 79.500 kg → 79.500 kg |
| Total e primária | R$ 379.580,00 · "Abrir Compra de insumos ›" | R$ 428.305,00 · "Abrir Compra de insumos ›" nos dois |
| Motor | não aplicável (a v55 não lê o cenário) | "passo dev500 → sem mudança na demanda" |

**Passou.** Reconciliação com os 62.500 da v55 na seção 2.6.

### Item 2 · NF 4533 / PC-090 conferida com 20.000 kg em quarentena
| Leitura | Base `0c0931f` | Candidata `7e74e6d` |
|---|---|---|
| Recebimentos previstos (Planejar safra) / A receber (Compra) | 20.000 → **20.000** | 20.000 → **0** / 20.000 → **0** |
| Estoque apto | 12.000 | 12.000 (a quarentena não é apta) |
| Situação | "Coberto pelo estoque" / "Coberto" | "Qualidade pendente · 15.456 kg" no Planejar safra, na Compra e no Mapa; a Compra não diz "Coberto" |
| Falta condicionada (memória do Planejar safra e da Compra, aviso da Compra, Mapa) | escondida | "Falta condicionada à qualidade: 15.456 kg a partir de 15/10/2026 se o laudo reprovar · **motivo:** 20.000 kg em quarentena aguardam laudo (lote S58-0926 · NF 4533: <motivo da conferência>) · **responsável:** o gestor libera ou reprova com o laudo no Estoque (reprovado, vira falta firme) · **prazo:** decidir antes de 15/10/2026, quando a falta começa se reprovar · fora da compra: sem nova compra automática", com o link "Decidir a qualidade no Estoque ›" |
| Compra firme e primária | — | necessidade 0; total R$ 428.305,00 igual, com "1 insumo com qualidade pendente (R$ 146.832,00 condicionados ao laudo, fora da compra)"; primária igual ("Abrir Compra de insumos ›"; na Compra "Solicitar cotações ›") |
| Laudo liberado (LAB-1, tela do Estoque) | sem mudança (0 kg, coberto) | "Coberto pelo estoque", estoque apto 32.000 kg (Planejar safra, Compra) e "Estoque cobre" no Mapa |
| Laudo reprovado (LAB-2, "germinação 71%") | não existe na v55 | falta firme 15.456 kg, "Complemento", primária "Enviar para cotação"; memória "Reprovado: 20.000 kg do lote S58-0926 (NF 4533) · laudo LAB-2: germinação 71% · …"; Compra 15.456 com "Complemento · 15.456 kg · o Planejar safra envia o complemento da SOL-2026-07"; Mapa "Falta 15.456 kg" |
| Motor | não aplicável | NF e laudo: liq 0 e total 428.305 nos três passos; `demSolSit` = "Qualidade pendente" (cond 15.456); `demSolRevisar` não põe a semente na SOL |

**Passou depois da correção `3f9e4f6`.** Na junção `232f3d9` o Planejar safra já estava certo, mas a Compra mostrava a foto da versão ("A receber 20.000", memória com o PC-090 a chegar em 05/10 e "Coberto" ao lado de "Qualidade pendente") e a falta condicionada não trazia o motivo registrado nem o prazo na Compra (seção 3).

### Item 3 · entregar 8.000 kg de NPK (REQ-040), cancelar a OS-0425 (Ana, com motivo), devolver; devolução da OS-0421 (A11)
| Passo | Base `0c0931f` (NPK) | Candidata `7e74e6d` (NPK · Planejar safra / Compra / Mapa C1) |
|---|---|---|
| Antes | 14.800 kg · R$ 379.580,00 | 14.800 kg / 14.800 / "Falta 14.800 kg" · R$ 428.305,00 · "Abrir Compra de insumos ›" |
| Entrega 8.000 kg | 14.800 | 14.800 / 14.800 / "Falta 14.800 kg"; total e primária iguais |
| Cancelamento da OS-0425 | 14.800; aviso "Requisição REQ-040 cancelada; **nada tinha sido entregue**" (S3) | 14.800 / 14.800 / "Falta 14.800 kg"; aviso "8.000 kg de NPK 20-05-20 entregue segue em custódia com Paula: receba a devolução no Estoque. Cancelada por Ana (gestora)"; a O.S. cancelada guarda dono "Rui (almoxarife)", prazo "receber a devolução" e o link "Receber devolução ›" (Estoque); REQ-040 custódia 8.000 |
| Devolução 8.000 kg | 14.800 | 14.800 / 14.800 / "Falta 14.800 kg"; custódia 8.000 → 0; lote N26-03 0 → 8.000 |
| A11: OS-0421 aponta 150 ha com 20 L (pré-condição pelo comando da página da O.S., `osc_apontar`) e devolve 40 L (tela do Estoque) | não medido (a v55 não lê o cenário) | devolução: Safra 2026/27 Fungicida A 0,0 L e Safrinha 2027 0,0 L antes e depois, total R$ 1.091.615,00 e primária iguais; custódia 45 → 5 L, lote F26-02 545 → 585 L. (O apontamento com 20 L em vez de 75 L é que libera a sobra como suprimento: Safrinha 23,0 → 0,0 L, com "Divergência de consumo/dose … revisão técnica de Ana".) |
| Motor | não aplicável | ent8000, cancel e dev8000: "sem mudança na demanda"; dev40 (A11): "sem mudança"; T10: a SOL fica em 14.800 kg e a situação "Em cotação" |

**Passou.**

### Item 4 · projeção datada dos recebimentos
| Leitura | Base `0c0931f` | Candidata `7e74e6d` |
|---|---|---|
| Semente de soja 58 W | "05/10/2026 · Recebimento PC-090 (Coop. Vale) · +20.000,0 kg → saldo 32.000 kg" | "05/10/2026 · Recebimento PC-090 (Coop. Vale) · +20.000,0 kg → saldo 23.056 kg" (entre os usos de 24/09 e 15/10) |
| KCl 60% e Semente de soja 62 X | — | "02/10/2026 · Recebimento PC-088 (Fertisul) · +40.000,0 kg" e "08/10/2026 · Recebimento PC-091 (Sementes Vale) · +8.000,0 kg"; a mesma memória na Compra |
| Entrega parcial (NF 4533 com 12.000 aptos e divergência "Falta") | — | apto 12.000 → 24.000; o saldo aberto do PC-090 (8.000 kg) segue com a data 05/10 ("+8.000,0 kg"); PC-088 e PC-091 não mudam |
| Unidade | — | `cal01_test` 45/0 (recebimento só cobre uso na data dele ou depois; ruptura; data viável) |

**Passou.**

### Item 5 · os mesmos números nos quatro consumidores
| Insumo | Planejar safra | Compra/SOL-2026-07 | Mapa › Insumos | Portal do parceiro |
|---|---|---|---|---|
| MAP 11-52 (antes e depois da devolução) | 79.500 kg | 79.500 | Falta 79.500 kg | 79.500 kg |
| NPK 20-05-20 (os quatro passos) | 14.800 kg | 14.800 | Falta 14.800 kg | não lido nesta rodada (a SOL não muda; o `pttest` confere o total 360.904,99) |
| Semente de soja 58 W com a NF em quarentena | Qualidade pendente · 15.456 kg | Qualidade pendente · 15.456 kg | Qualidade pendente · 15.456 kg | fora da SOL (sem nova compra) |
| Semente com laudo reprovado | 15.456 kg | 15.456 (Complemento) | Falta 15.456 kg | fora da SOL até o Planejar safra enviar o complemento |

Na base, o Planejar safra dizia 62.500 kg de MAP e o Mapa "Falta 80.000 kg" (DEM-05). **Passou.**

### 2.6 Memória das parcelas · MAP 11-52 (reconciliação com os 62.500 da v55)
| Parcela | v55 `0c0931f` | candidata `7e74e6d` |
|---|---|---|
| Saldo inicial | estoque apto 90.000 | 90.000 + 500 em custódia sem uso (OS-0417) = 90.500 |
| 23/09 · T4 · OS-0420 (Em execução, saldo 70 ha × 250 kg/ha) | — (a v55 só lia o plano; o T4 não tem plano na Safra 2026/27) | 17.500 → saldo 73.000 |
| 24/09 · T2 · OS-0431 (102 ha) | (dentro dos 74.500 do T2) | 25.500 → saldo 47.500 |
| 15/10 · T1-A · 160 ha | 40.000 → saldo 50.000 | 40.000 → saldo 7.500 |
| 18/10 · T2 | 298 ha · 74.500 → falta 24.500 | parte sem O.S. 196 ha · 49.000 → falta 41.500 |
| 25/10 · T1-B · 152 ha | 38.000 → falta 38.000 | 38.000 → falta 38.000 |
| Necessidade líquida | 62.500 | 79.500 |

62.500 + 17.500 (o que a OS-0420 ainda tira do almoxarifado, que a v55 não contava no Planejar safra; o Mapa da v55 já mostrava 80.000) − 500 (custódia livre da OS-0417, suprimento) = 79.500. O T2 só se divide entre a O.S. e o resto do plano (25.500 + 49.000 = 74.500). Depois da devolução os 500 kg passam da custódia para o apto e a necessidade fica 79.500.
Semente de soja 58 W: bruta 23.816 (v55) + 3.640 da OS-0420 (52 kg/ha × 70 ha) = 27.456; sem os 20.000 em quarentena faltam 15.456 a partir de 15/10 (12.000 − 3.640 − 5.304 − 8.320 − 10.192). Os 11.816 calculados na contraprova são os mesmos 15.456 sem a OS-0420.

## 3. Correções de integração (com teste)

### 3.1 `3f9e4f6` · a Compra lê a conta viva (aceite itens 2 e 5)
| Achado (pela tela, na junção `232f3d9`) | Severidade | Correção | Teste |
|---|---|---|---|
| A Compra (etapa 2) mostrava a foto da versão da SOL: depois da devolução, "Estoque apto 90.000" e "+ 500 kg em custódia"; com a NF em quarentena, "A receber 20.000", memória com o PC-090 a chegar e "Coberto" ao lado de "Qualidade pendente". Mesmo código na `16fb55e` (a `processo_compras.py` da v56 é a da CTL-4): não é regressão da junção, é o item 2/5 do aceite | S3 (a compra firme e o total estavam certos; a tela contradizia o Planejar safra e escondia que o pedido virou quarentena) | as linhas da etapa 2 (bruta, estoque apto, a receber, necessidade, falta e memória) vêm da conta viva `vivaDe` (plano da versão + ordens e estoque de agora), como o desenho já dizia (FRENTE-C §10, achado 2); a SOL não muda; "Coberto" some quando a cobertura depende do laudo; "Complemento · <diferença>" quando a demanda pede mais do que a SOL (`demSolSit`) | `demanda_estado_nav_test` K2b, Q1b, Q2b |
| A falta condicionada não trazia o motivo registrado na conferência nem o prazo na Compra; o Mapa não dizia quem decide | S4 | um texto só, `demCondTxt` (`cal01.js`): motivo (lote, NF e `quarRef.mot`, gravado por `cenEstDem` e `dados2.est_dem`), responsável, prazo e decisão; usado na memória, no aviso da Compra e no Mapa; a última linha da memória diz "Sem falta nesta safra se o laudo liberar …" | `demanda_estado_nav_test` Q1b; `demanda_unica_test` G6 (paridade `est_dem` × `cenEstDem`) |

O que K2b e Q1b conferem estava errado na junção, medido pela tela com o mesmo roteiro (`aceite/232f3d9-antes-da-correcao/valores.json`: Compra com estoque apto 90.000 depois da devolução e "A receber 20.000" com a quarentena); o "—" calado do Q2b está em `aceite/intermediarios/aceite_r1_antes_do_complemento.json` (laudo reprovado: Compra 15.456 com "—"). Os três passam no `3f9e4f6` (14 ok · 0 falhas) e no `7e74e6d` (14 ok · 0 falhas). O teste em si não foi rodado contra o código da junção.

### 3.2 `7e74e6d` · vermelho novo do próprio `3f9e4f6`: DEM-08 (demanda_unica_nav_test R2)
| Achado | Correção | Teste |
|---|---|---|
| Na bateria do `3f9e4f6`, `demanda_unica_nav_test` deu 28 ok · 1 (R2): com a OS-0418 cancelada, a etapa 4 da Compra passou a comparar as propostas com a falta da conta de agora (a Ureia já não falta) e a escolha padrão da Ureia virou "Menor custo total" (Fertisul) em vez de "Chega primeiro" (Casa do Adubo). Vem da correção 3.1, não da junção | `faltaDe` ganha a fonte: a etapa 2 (a demanda) usa a conta de agora; cotação, aprovação e entrega comparam com a falta que a SOL pediu (DEM-08, desenho da CTL-4). E a linha que a SOL pede acima da demanda de agora mostra só "Acima da demanda", sem "Coberto" ao lado | `demanda_unica_nav_test` R2 (29 ok · 0 depois da troca da falta) e C1 (a linha da Ureia sem "Coberto"): 29 ok · 0 no `7e74e6d` |

## 4. Testes · candidata `7e74e6d` (executado)
Comando: `env CHROME_BIN=/tmp/cloudchrome/chrome flock /tmp/cdpN.lock env CDP_GL=1 SAFRION_DADOS=sintetico timeout 900 python3 <teste>` (`aceite/harness/nav.sh`, um por vez); sem navegador, `env SAFRION_DADOS=sintetico python3 <teste>`. Logs em `testes/cand-7e74e6d/` (`_resumo.txt`, `_resumo_unit.txt`). Regra da tarefa: a base `0c0931f` só roda o que falha na candidata; a coluna "Base" traz o que já estava medido em `../brutos/base-0c0931f/` ("—": o teste não existe na base).

### CTL-4
| Teste | Base `0c0931f` | Candidata `7e74e6d` |
|---|---|---|
| `demanda_unica_test.py` | — | 66 ok · 0 |
| `demanda_unica_nav_test.py` | — | 29 ok · 0 (no `3f9e4f6`: 28 ok · 1, R2; seção 3.2) |
| `demanda_estado_nav_test.py` | — | 14 ok · 0 (K1, K2, K2b, K3, Q1, Q1b, Q2, Q2b, Q3, A7, R1, F1, D3, E1); na bateria parou no `timeout 900` com 12 ok (carga da máquina 19–23 em 4 CPUs); refeito com `timeout 2400`: 14/0 em 855 s |
| `saf_cmp_continuidade_test.py` | não rodado (verde na candidata) | 31 ok · 0 |
| `cmptest.py` | não rodado | 98 OK · "FALHAS: nenhuma" |
| `pttest.py` | não rodado | 32 OK · "FALHAS: nenhuma" (total da SOL 360.904,99: MAP 79.500 e Ureia 1.140) |
| `cal01_test.py` · `quantidade_test.py` | não rodado | 45 ok · 0 · 14/14 |
| `sutest.py` | não rodado | OK (27) |
| `tabelas_saf_test.py` | 24/24 | 24/24 |

### Cruzamentos (quem mexe na demanda ou no cenário)
| Teste | Base `0c0931f` | Candidata `7e74e6d` |
|---|---|---|
| `solo_unit_test.py` | — | 128/128 (com as 3 verificações da origem da dose na conta única) |
| `solo_saf_test.py` · `solo_os_test.py` | — | 36/36 · 18/18 |
| `ben_unit_test.py` | 168/168 | 168/168 |
| `producao_fluxo_test.py` | 66/66 | 67/67 |
| `comercial_unit_test.py` | — | 114/114 |
| `ctl5_test.py` | — | 30/30 |
| `est_cenario_test.py` · `app_cenario_test.py` | não rodado | 15/15 · 15/15 |
| `os_cenario_test.py` | 20/21 | 20/21: a mesma asserção ("A liberar sem revisão…"; o número medido é 7, era 6: versão do cenário) |
| `acao_unica_test.py saf` | 10 ok · 0 | 10 ok · 0 |
| `partest.py` | 50 ok · 0 | 50 ok · 0 |
| `varredura.py` | 142/142 | 145/145 (e 145/145 na junção `232f3d9`) |
| Sintaxe JS das páginas | — | 145 arquivos · 0 erros |

Aceite (seção 2): `aceite.py` + `roteiro.py` + `m_s2.py` no `7e74e6d`, conferidos por `confere.py`: 22/22.

## 5. Vermelhos
- **Vermelho novo restante: nenhum** (também na candidata `211b3df`, seção 8.6).
- Novos, achados e corrigidos nesta integração (seção 3): a Compra com a foto da versão (aceite itens 2 e 5; `3f9e4f6`) e o R2 do `demanda_unica_nav_test` criado pela própria correção (`7e74e6d`). Nenhum afrouxa controle; nenhum teste antigo perdeu asserção (o `solo_unit_test` passou a medir o estado composto: o T1-B pela parte sem O.S.).
- Da base, iguais nos dois lados: `os_cenario_test` 20/21 (mesma asserção).
- De ambiente: o `timeout 900` do `demanda_estado_nav_test` na bateria, sob carga; refeito e verde.

## 6. Arquivos
- `ctl4-correcao_853a6a8..16fb55e.patch`; a frente inteira na branch `claude/v44-controle-04`.
- `contraprova-v55/` (RELATORIO.md e logs da contraprova `0c0931f` × `2e466eb`), `reproducao-versoes/` (RELATORIO.md e logs da reprodução por versão: `c5d337a`, `853a6a8`, `0c0931f`, `0ad2d0d`, `2e466eb`), `bateria-correcao/logs/` (bateria da correção `853a6a8` × `78711bb`, com `_comparacao.txt`).
- `aceite/`: `aceite_7e74e6d.json` (valores antes/depois, itens 1–4), `7e74e6d/` (roteiro da contraprova: `valores.json`, `roteiro.log`), `motor_7e74e6d.log`, `aceite_resultado_7e74e6d.json` e `confere_7e74e6d.txt` (22/22); `232f3d9-antes-da-correcao/` (o mesmo roteiro e o motor na junção); `intermediarios/` (a rodada completa no `3f9e4f6`, a do `aceite_r1` antes do complemento e o roteiro do primeiro passo da correção); `harness/` (`aceite.py`, `roteiro.py`, `confere.py`, `m_s2.py`, `navlib.py`, `nav.sh`, `final.sh`, a lista); `capturas/` (27, PNG de 8 bits, do `7e74e6d`).
- `aceite/45a68b2/` (aceite, roteiro, motor e `confere_45a68b2.txt` 22/22 na candidata dos ajustes; capturas do item 2) e `aceite/harness/final_45a68b2.sh`, `lista_45a68b2.txt`.
- `testes/cand-45a68b2/` (bateria da candidata dos ajustes, `_resumo.txt`, `unit/`, `base-0c0931f/esttest.log`, `esttest_211b3df.log`, `render_igual_3353f86.txt`), `testes/juncao-3353f86/` (build, render, sintaxe, varredura, unidade e J5 contra `74063d1` e `12dfaef`).
- `testes/cand-7e74e6d/` (bateria e testes de unidade), `testes/cand-3f9e4f6/` (o R2 vermelho e o verde depois da troca da falta), `testes/juncao-232f3d9/` (build, render, sintaxe, varredura e testes de unidade da junção).

## 7. Limites
- Chrome headless com emulação, 1440 × 1000; não é aparelho físico.
- A pré-condição do A11 (apontamento de 150 ha com 20 L na OS-0421) foi feita pelo comando da página da O.S. (`osc_apontar`, o mesmo do formulário "Apontar"), não pelo formulário; a devolução, que é o item do aceite, foi pela tela do Estoque.
- O `aceite.py` guarda 420 caracteres do painel do Mapa por insumo: o prazo e a decisão do Mapa estão conferidos no `demanda_estado_nav_test` Q1b, que lê o painel inteiro.
- A lista de pedidos da Compra (etapa 6, "Acompanhe a entrega") continua lendo os pedidos da montagem (`D2.PEDIDOS`); a demanda (etapa 2) é que lê o estado vivo.
- A falta condicionada diz "o gestor" (o papel que libera ou reprova, `cenExige(…, 'gestor')`), não o nome de uma pessoa.

## 8. Ajustes da revisão do Codex na CTL-4 (CTL4-FIX-REV-20261013-01) · candidata `45a68b2`/`211b3df` (executado)

Revisão do `16fb55e` pelo Codex (PR #47, comentário 6136083713): 4 S3. A CTL-4 corrigiu cada um com um commit e uma regressão que falha no `16fb55e` (registro em `docs/controle-01/PLANO.md` §7 e `docs/controle-01/desenho/FRENTE-C.md` §10.1; o Codex aceitou o `74063d1`). Aqui: a junção na `int/v56`, a regressão da combinação, o aceite itens 2 e 5 e os testes que tocam o que mudou, na candidata.

### 8.1 Os ajustes
| Ajuste (S3) | Commit | O que muda | Regressão |
|---|---|---|---|
| 1 · Mapa, SU-03det e MB-05 perdiam a qualidade pendente quando havia falta firme ao mesmo tempo | `81aef42` (M1 passou para o `est_laudo_lote_nav_test` em `718a914`) | `demSituacao` devolve a parte condicionada como 4º item: "Falta 5 L" e "Qualidade pendente · 10 L", com quem decide; a compra firme e a ação primária não mudam | `demanda_unica_test` J1, J1b; `est_laudo_lote_nav_test` M1 |
| 2 · a memória atribuía todo o reprovado ao último laudo | `7551f1a` | `cenRepsLote` (espelho `dados2._reps_lote`) lê o histórico do lote: "Reprovado: 20 L … = 10 L no laudo LAB-A: motivo A + 10 L no laudo LAB-B: motivo B"; o selo do lote no Estoque usa a mesma lista | J2 (Python = JS); nav L2 |
| 3 · o motivo do laudo migrava entre lotes | `6236d70` | abrir um lote, manter bloqueado, liberar, reprovar, trocar o perfil ou restaurar limpam o laudo e o motivo | nav L1, L1b |
| 4 · reprovação pela mesma autora da entrada bloqueada não marcava revisão posterior | `0ee25bd` | `cenRevEntrada`: a regra da liberação vale para as duas decisões; a reprovação grava `rev` e avisa "Fica revisão posterior pendente (…)"; sem veto nem segundo aprovador | J4 (positivo e negativo); nav L2b, L3 |

### 8.2 Junção `3353f86` (`git merge --no-ff 74063d1` sobre `12dfaef`): as duas intenções
| Arquivo | v56 (`12dfaef`) | Ajustes (`74063d1`) | Resolução |
|---|---|---|---|
| `cal01.js` `cal01Memo` | linha da falta condicionada com o texto único `demCondTxt` (motivo, responsável, prazo, fora da compra; seção 3.1) | reprovado por laudo, cada um com a sua quantidade (`x.reps`; ajuste 2) | os dois |
| `cal01.js` `demSituacao` | `demCondTxt` na falta condicionada | falta firme + qualidade pendente juntas (4º item e detalhe com o `qtx`; ajuste 1) | o 4º item do ajuste 1 com o mesmo `demCondTxt` nos dois ramos ("se o laudo reprovar, faltam mais X · motivo: … · responsável: … · prazo: … · fora da compra"); sai o `qtx`, que dizia o mesmo com outras palavras |
| `cenario.js` `cenEstDem` e `dados2.py` `est_dem` | `quarRef.mot` (motivo da entrada) | `quarRef.reps` (`cenRepsLote`/`_reps_lote`) | os dois no mesmo `quarRef` |
| `demanda_unica_test` J1/J1b e `est_laudo_lote_nav_test` M1 | — | conferiam a frase do `qtx` | conferem o texto único (quantidade aguardando laudo, quem decide, "faltam mais", fora da compra; J1 também o prazo). Nenhuma asserção saiu |

Build 138 quadros, 0 FALHA; render 145 páginas; sintaxe JS 145/0; varredura 145/145 (`testes/juncao-3353f86/`).

### 8.3 Regressão J5 (`45a68b2`)
A junção pôs `mot` (V56) e `reps` (ajuste 2) no mesmo `quarRef`, e o Mapa passou a usar `demCondTxt` também com falta firme. J5 protege a combinação: 30 L de Fungicida A devolvidos bloqueados e reprovados (LAB-9) e mais 10 L bloqueados com motivo; o `quarRef` tem o motivo e o laudo com a sua quantidade (Python = JS) e o Mapa diz "Falta 5 L", "Qualidade pendente · 10 L" e "se o laudo reprovar, faltam mais 10 L · motivo: … Galão amassado". `demanda_unica_test` 71 ok · 0 na junção; o mesmo arquivo dá FALHA no J5 no `74063d1` (sem o motivo) e no `12dfaef` (sem os laudos e sem o 4º item): `testes/juncao-3353f86/j5_em_74063d1.log` e `j5_em_12dfaef.log`.

### 8.4 Vermelho da bateria: teste obsoleto (`211b3df`)
| Teste | Candidata `45a68b2` | Base `0c0931f` | Classificação e correção |
|---|---|---|---|
| `esttest.py` parte 4, "trocar de perfil avisa que não é segurança de acesso" | 12/13: a tela avisa "Perfil de demonstração: Rui · Almoxarife e expedição (não é segurança de acesso)." e o teste esperava "Rui · Almoxarife (não é segurança de acesso)" | 13/13 ("Rui · Almoxarife") | teste obsoleto, não defeito: o COM P1 (`498104d`) renomeou o perfil de propósito (`comercial_unit` C11b). A asserção continua exigindo o aviso inteiro, com o nome vigente; não vem dos ajustes da CTL-4. `211b3df`: 13/13 (`esttest_211b3df.log`) |

### 8.5 Aceite CTL-4-FIX itens 2 e 5 · candidata `45a68b2` (executado)
Mesmo roteiro e mesmo harness da seção 2 (`aceite.py` percorre os itens 1–4; o item 5 lê os quatro), storage limpo, perfil Ana, comandos das próprias telas; no render do `45a68b2` (o `211b3df` só muda o `esttest.py`, que não entra na montagem). `confere.py`: **22/22** (`aceite/45a68b2/confere_45a68b2.txt`; o rótulo "motor_3f9e4f6.log" nas linhas do motor é fixo no `confere.py`: o arquivo lido é o `motor_45a68b2.log`). Em relação ao `7e74e6d`, todos os números são iguais; mudam só o aviso da reprovação do LAB-2 (ganha "Fica revisão posterior pendente (Ana registrou a entrada bloqueada e decidiu).", o ajuste 4: Ana conferiu a NF com a quarentena e reprovou) e a hora do cancelamento da OS-0425.

**Item 2 · NF 4533 / PC-090 com 20.000 kg em quarentena**
| Leitura | Candidata `45a68b2` |
|---|---|
| Recebimentos previstos (Planejar safra) / A receber (Compra) | 20.000 → 0 / 20.000 → 0; estoque apto 12.000 (a quarentena não é apta) |
| Situação | "Qualidade pendente · 15.456 kg" no Planejar safra, na Compra e no Mapa (T4); a Compra não diz "Coberto" |
| Falta condicionada (memória do Planejar safra, Compra, Mapa) | "15.456 kg a partir de 15/10/2026 se o laudo reprovar · motivo: 20.000 kg em quarentena aguardam laudo (lote S58-0926 · NF 4533: Aguarda laudo de germinação (aceite CTL-4-FIX)) · responsável: o gestor libera ou reprova com o laudo no Estoque (reprovado, vira falta firme) · prazo: decidir antes de 15/10/2026 … · fora da compra: sem nova compra automática"; o Mapa traz o mesmo texto (prazo e decisão no painel inteiro: `demanda_estado_nav_test` Q1b OK) |
| Compra firme e primária | necessidade 0; total R$ 428.305,00 igual, com "1 insumo com qualidade pendente (R$ 146.832,00 condicionados ao laudo, fora da compra)"; primárias iguais ("Abrir Compra de insumos ›"; na Compra "Solicitar cotações ›") |
| Laudo liberado (LAB-1) | "Coberto pelo estoque", apto 32.000 kg (Planejar safra, Compra); "Estoque cobre" no Mapa |
| Laudo reprovado (LAB-2, "germinação 71%") | falta firme 15.456 kg, "Complemento", primária "Enviar para cotação"; memória "Reprovado: 20.000 kg do lote S58-0926 (NF 4533) · laudo LAB-2: germinação 71% · …"; Compra 15.456 "Complemento · 15.456 kg"; Mapa "Falta 15.456 kg"; aviso com a revisão posterior (ajuste 4) |
| Motor (`m_s2.py`) | NF e laudo: liq 0, total 428.305; `demSolSit` "Qualidade pendente" (cond 15.456); a SOL não ganha a semente |

**Passou.**

**Item 5 · os mesmos números nos quatro consumidores**
| Insumo | Planejar safra | Compra/SOL-2026-07 | Mapa › Insumos | Portal do parceiro |
|---|---|---|---|---|
| MAP 11-52 (depois da devolução) | 79.500 kg | 79.500 | Falta 79.500 kg | 79.500 kg |
| NPK 20-05-20 (depois da devolução) | 14.800 kg | 14.800 | Falta 14.800 kg | não lido nesta rodada (a SOL não muda) |
| Semente de soja 58 W com a NF em quarentena | Qualidade pendente · 15.456 kg | Qualidade pendente · 15.456 kg | Qualidade pendente · 15.456 kg | fora da SOL (a linha da semente não aparece; MAP 79.500 kg) |
| Semente com laudo reprovado | 15.456 kg | 15.456 (Complemento) | Falta 15.456 kg | fora da SOL até o Planejar safra enviar o complemento |

**Passou.** Os itens 1, 3 e 4 rodaram juntos (o item 5 depende deles) e também passaram, com os mesmos números da seção 2.

### 8.6 Testes · candidata `45a68b2` (executado, um por vez)
Comando: `env CHROME_BIN=/tmp/cloudchrome/chrome flock /tmp/cdpN.lock env CDP_GL=1 SAFRION_DADOS=sintetico timeout 900 python3 <teste>` (`aceite/harness/nav.sh` com `lista_45a68b2.txt`; `final_45a68b2.sh`); sem navegador, `env SAFRION_DADOS=sintetico python3 <teste>`. Build 138 quadros, 0 FALHA; render 145 páginas, sha256 idêntico ao do `3353f86` (`render_igual_3353f86.txt`). Logs em `testes/cand-45a68b2/` (`_resumo.txt`). A base `0c0931f` rodou só o que falhou.

| Teste | Por quê | Candidata |
|---|---|---|
| `est_laudo_lote_nav_test.py` (novo nos ajustes) | ajustes 1–4 pela tela (L1, L1b, L2, L2b, L3, M1, E1) | 7 ok · 0 (rodado no `_render` do `3353f86`, sha256 idêntico; o arquivo de teste não mudou) |
| `demanda_unica_test.py` (mudado nos ajustes e na junção) | J1, J1b, J2, J4, J5 e o resto do motor | 71 ok · 0 |
| `demanda_estado_nav_test.py` | K/Q/A7/R1/F1/D3/E1 (Q1b: prazo e decisão no Mapa) | 14 ok · 0 (824 s, dentro do `timeout 900`) |
| `demanda_unica_nav_test.py` | demanda única nas telas | 29 ok · 0 |
| `cal01_test.py` · `quantidade_test.py` | `cal01.js` mudou | 45 ok · 0 · 14/14 |
| `aprova_quem_decide_test.py` | `cenRevEntrada` (ajuste 4) | 103/103 |
| `esttest.py` | Estoque (selo do lote, laudo) | 12/13 no `45a68b2` (teste obsoleto, 8.4) → 13/13 no `211b3df`; base 13/13 |
| `est_fix1_test.py` · `est_fix2_test.py` · `est_cenario_test.py` | Estoque e cenário | 13/13 · 11/11 · 15/15 |
| `talmapa_test.py` | Mapa | 8/8 |
| `sutest.py` · `mbtest.py a` | SU-03det e MB-05 (ajuste 1) | OK (27) · FALHAS: 0 |
| `cmptest.py` | Compra | 98 OK · "FALHAS: nenhuma" |
| Aceite (`roteiro.py`, `aceite.py`, `m_s2.py`, `confere.py`) | itens 2 e 5 (com 1, 3 e 4) | 22/22 |
| Sintaxe JS das páginas · varredura | | 145 arquivos · 0 erros · 145/145 (na junção, mesmo render) |

**Vermelho novo restante: nenhum.** O único vermelho da bateria (`esttest` parte 4) era teste obsoleto vindo do COM, corrigido em `211b3df` sem tirar asserção. Nenhum controle afrouxado.
