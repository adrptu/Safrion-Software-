# LEVE-1 · travas sem dano viram clique, padrão preenchido ou aviso (19/10/2026)

**Pedido do proprietário (19/10):** "Não quero um sistema travado e burocrático, quero leve e fluido."
**Regra:** AGENTS §4. Trava só onde protege algo concreto; o resto vira aviso, padrão preenchido ou sai. Triagem em [`INVENTARIO.md`](INVENTARIO.md), seção "LEVE-1 · Claude aplica agora", itens 1 a 11.
**Autoria:** Claude. **Revisão:** Codex. **Base:** `cbe4cd38` (com o inventário `ffe73b0d`). **Branch:** `claude/v44-leve-1`. Protótipo, dados sintéticos (regime leve, AGENTS §3.5).

Todos os caminhos abaixo são de `tools/prototipo/v37/gen37`. "Executado" = rodado nesta árvore; os brutos estão em [`brutos/`](brutos/) (caminhos locais trocados por marcadores; e-mails, telefones e CNPJ do cadastro sintético no `nav_cadp.log` também).

## O que mudou, item por item

| # | Tela | Antes | Agora | Dano avaliado | Continua travando |
|---|---|---|---|---|---|
| 1 | O.S. e Mapa · Iniciar execução e Enviar para conferência | 2º bloco "Confirmar início" / "Confirmar envio" | grava no clique (`osDireto`, núcleo da O.S.); o aviso é o recibo: "OS-0424 em execução: insumos com Marcos, confirmados no app" e "OS-0424 enviada para conferência por Ana (gestora)" (CMD-08 com quem e quando). Toque duplo: "já está em …: nada foi feito de novo" | nenhum: o comando valida como antes e nada é reservado nem baixado | o comando (insumos com o operador, carência, saldo zero); Aprovar, Liberar e Encerrar com confirmação |
| 2 | App · Fechar turno (MB-03) e Apontar área da colheita (MB-10) | "Informe as horas trabalhadas." | horas = agora − início − pausas (`cenHorasTurno`, `cenario.js`, 1 casa, virada de dia soma 24 h), editáveis, com a dica do cálculo; o comando `cenFecharTurno` usa o mesmo cálculo quando as horas não vêm. MB-10 só preenche com turno aberto na mesma O.S. | nenhum | sem início registrado, campo apagado ou horas 0: continua pedindo (nada inventado) |
| 3 | O.S. › Nova ordem | "Informe o início da janela." | início da janela = data do gatilho da atividade no cultivo (núcleo `datas_atividade`, variante canônica, calculada no build) ou hoje (dia operacional) se o gatilho já passou ou não tem âncora; a dica diz a origem; editável; o atalho `#nova:…` e a data escolhida à mão valem | nenhum | campo apagado pede de novo; duplicidade e demais regras da ordem nova |
| 4 | Manutenção · Liberar OM | "Falta: executante" / "tempo previsto" | **sem mudança de código**: a base já abre o executante sugerido (`manExecSug`, pessoa única habilitada) e o tempo do serviço do plano, editáveis, e libera num clique. Verificação de regressão nova (U4, I4) | — | corretiva nasce sem tempo de serviço (`tempo:null`): não há valor a sugerir, continua pedindo (ver "Fora") ; "Não liberada: falta peça" |
| 5 | Manutenção · Vincular ativos ao plano | "Escolha como contar…" com a primária desligada | "Contar de agora" marcado por padrão (marco estimado, com o selo que já existia); "Informar a última execução" a um toque; o comando (`manVincRef`) faz o mesmo sem base | nenhum: o marco fica marcado como estimado | base do vínculo encerrado e da última OM encerrada vêm antes do padrão; ativo com contador e sem leitura continua pedindo |
| 6 | Cadastros › Produtos | "Informe a data do preço." | digitar o preço preenche a data com hoje (23/09/2026 na demonstração), editável; salvar preço sem data grava hoje | nenhum | — |
| 7 | Comercial · Encerrar saldo de venda | recusado com carga programada | o encerramento cancela a carga programada que não saiu no mesmo comando (antes das reservas) e o aviso diz qual; o saldo encerrado guarda `enc.cargas` | nenhum: a carga não saiu (sem baixa nem título) | carga que já saiu não é tocada (o expedido vira a quantidade vigente) |
| 8 | Gestão (GE-03) e Campo (CA-02) | botões "Conferir reabertura …" que diziam "Prévia · nada foi alterado" | saem; o atalho "Abrir O.S." do CA-02 fica | nenhum | — |
| 9 | Motivo obrigatório sem dano | campo obrigatório | opcional; quem e quando continuam gravados: desvincular ativo (`manDesvincular`), fechar achado sem serviço (`manAchFechar`), cancelar OM (`manCancelar`; botão "Cancelar ordem"), resposta fora de OK do checklist (não segura concluir; app MB-09det registra "Não feito" sem motivo), reordenar a fila (LO-02), encerrar saldo e cancelar carga (`comercial.js`), Irrigação (área e tempo incompatíveis, aceite da divergência com o botão "Aceitar divergência", fertirrigação), alçadas (`confAlcMudar`) | nenhum além do registro | 2º aprovador quando a mudança amplia o poder de quem propõe (R10) |
| 10 | Cadastros › Fazendas | soma dos talhões acima da área da fazenda e diferença cultivável × polígono sem motivo impediam salvar | aviso no recibo ("Aviso: os talhões ativos da Santa Rita somam … ha e a fazenda tem … ha; diferença de … % …, sem motivo"), no talhão, na fazenda, no polígono e no desenho do Mapa (`talmapa.js`, mesma regra); o selo "Diferença sem motivo" segue na lista | nenhum: a safra usa a área cultivável do talhão | parcelas da safra acima da área, inativar talhão com parcelas, sobreposição e contorno que cruza a si mesmo |
| 11 | Irrigação · Terminar | "Informe o volume medido…" | volume em branco termina com volume nulo (não zero), conferência "Sem leitura" (estado que já existia) e próximo passo "Informar leitura"; o balanço credita só o medido (`irrCredito` ignora nulo) | nenhum: o crédito segue só com leitura | volume inválido (negativo, texto) recusa |

## Testes trocados (oráculo antigo → comportamento novo, motivo na docstring: "leve, proprietário 19/10")

| Arquivo | Caso | Antes | Agora |
|---|---|---|---|
| `ostela.py` | início e envio | confirmação diz os insumos; clicar "Confirmar envio" | o recibo diz os insumos; em conferência no clique, sem "Confirmar …" |
| `os_v39_bloq_test.py`, `ap_unico_nav.py`, `verif_os.py`, `os_cenario_test.py`, `osfix.py`, `carencia_test.py` | passo "Confirmar início/envio" | clicavam o 2º botão | o passo sai (os demais oráculos ficam) |
| `ma_vinculo_test.py` | A2, B2 | primária desligada até escolher; 3 toques | "Contar de agora" marcado e primária ligada; 2 toques |
| `ma_vinculo_unit.js` | V4, V6 | sem escolha não vincula; desvincular pede motivo | conta de agora (estimado); desvincula sem motivo com quem e quando |
| `cadc_cd06_test.py` | Calcário sem data | "Informe a data do preço." | salvo com 23/09/2026 |
| `comercial_unit.js` | C09, RV-A5c, RV-A12c (M10) | encerrar sem motivo e com carga programada recusa; cancelar carga sem motivo recusa | encerra cancelando a carga que não saiu; repetir não cancela de novo; carga que saiu intocada; cancelar carga sem motivo grava quem e quando |
| `ma_regras_unit.js` | AC-PCM-09 | fechar sem serviço exige motivo | fecha sem motivo com quem e quando |
| `aprova_quem_decide_unit.js` | checklist R-D4 | "Não feito" sem motivo não conclui | conclui; Pendência sem "· " solto |
| `d5_reserva_test.py` | 5a | botão "Cancelar ordem · motivo" | "Cancelar ordem" (o teste ainda informa o motivo e confere que ele fica) |
| `irr_onda0_unit.js` | R1 antecipado, F1 volta completa, F1 parcela, R3 sem motivo, UI | recusavam sem leitura ou sem motivo | "Sem leitura" sem crédito; conferência sem crédito; aceite sem motivo com quem; UI "Aceitar divergência" |
| `irr_fluxo_test.py` | 7–8 e 23 | botão "Aceitar com motivo" | "Aceitar divergência" |
| `quantidade_test.py` | 15 | término sem hidrômetro recusava | aceito, volume nulo, "Sem leitura", nada creditado |
| `cadf_test.py`, `cadf_det_test.py` | 7, 8 | "somariam 700 ha"; "Informe o motivo da diferença" | não barra (o aviso é conferido no `leve1_test.py`); motivo à vista e opcional |
| `ma_vinculo_test.py` | A8 | Desvincular com a primária desligada até o motivo | primária ligada sem motivo; o motivo escolhido segue gravado |
| `irr_estado_test.py` | 18 | terminar sem leitura recusa sem alterar | Em conferência "Sem leitura", volume nulo, sem crédito; a leitura na conferência (`irrConferir`) encerra e só então credita |
| `cadc_cd06_test.py` | abertura | parava no 2º caso (TypeError; **vermelho antigo, igual na base**: a árvore abre recolhida desde o v129) | clica "Expandir tudo" ao abrir, como o `cadf_test`; assim o caso do preço (item 6) passa a rodar |

Nenhum teste foi apagado. Testes novos: `leve1_unit_test.py` + `leve1_unit.js` (sem navegador) e `leve1_test.py` (Chrome, os 11 itens; `RENDER_DIR`/`ANTES` para a contraprova).

## Resultados (executado em 19/10/2026, dados sintéticos)

Build do HEAD (árvore limpa) com `SAFRION_DADOS=sintetico python3 -W error::SyntaxWarning -B build.py && python3 -B montar_render.py`; contraprova = o teste novo contra o `_render` da base `cbe4cd38` (`ANTES=`) ou, quando o teste monta a página a partir dos módulos, o mesmo arquivo copiado para a árvore da base. Navegador: `env CHROME_BIN=/tmp/cloudchrome/chrome CDP_GL=1 SAFRION_DADOS=sintetico python3 -B <teste>`, um Chrome por vez.

**Sem navegador** (node/python):

| Teste | Ramo | Contraprova na base |
|---|---|---|
| `leve1_unit_test.py` | 17/17 | 4/17 (reprova os casos dos itens 1, 2, 5, 9 e 10; passam só os "continua travando" U1d, U2e, U10b e o U4, que já era assim) |
| `comercial_unit_test.py` | 119/119 | 114/119 |
| `ma_regras_test.py` | 150/150 | 149/150 (AC-PCM-09) |
| `ma_vinculo_test.py U` | 42/42 | 40/42 (V4, V6) |
| `aprova_quem_decide_test.py` | 103/103 | 102/103 (R-D4) |
| `irr_onda0_test.py` | 30/30 | 21/30 |
| `quantidade_test.py` | 16/16 | 15/16 (caso 15) |
| regressão das áreas tocadas | `config_unit` 226/226, `config_regressao` 6/6, `config_app_unit` 4/4, `inicio_entrega` 26/26, `ma_app` 36/36, `man_backlog_unit` 23/23, `man_cumprimento_unit` 14/14, `os_aprov_lib` 51/51, `kanban_raias` 9/9, `cen_grava` 10/10, `producao_unit` 160/160, `demanda_unica` 71/71, `assinatura_unit` 76/76, `ds_unit` 31/31, `usar_os_unit` 25/25, `painel_fixo_saldo` 8/8, `conferencia_diaria` 30/30, `carencia_test unit` 50/50, `dose_divergente unit` 35/35 | — |

**Navegador** (Chrome headless, 1440 px e 390 px conforme o teste):

| Teste | Ramo | Contraprova / base |
|---|---|---|
| `leve1_test.py` (os 11 itens) | **32/32** | **9/32 na base**: reprova todo item mudado; passam só os casos "continua travando" (I1d, I1e, I2b, I2e, I3b, I3d, I9f), o I4 (já era assim) e "sem erro de JS" |
| `irr_estado_test.py` | 38/38 | 37/38 (caso 18) |
| `cadc_cd06_test.py` | 14/14 | 12/14 (preço sem data e o caso seguinte) |
| O.S. e app: `os_v39_bloq_test` 14/14, `os_cenario_test` 22/22, `carencia_test fluxo` 40/40, `d5_reserva_test` 13/13, `app_mb03_turno_test` 11/11, `app_cenario_test` 15/15, `app_restaurar_test` 4/4, `app_saldo_zero_test` 12/12, `app_entrega_parcial_test` 7/7, `consumo_divergente_test` 21/21, `etapas_celular_test` 14/14 | verde | — |
| Manutenção: `ma_vinculo_test A B` 59/59, `ma_rastreio_test` 58/58, `ma_unica_test` 23/23 | verde | — |
| Cadastros, Irrigação, Configurações: `cadp_test` 15/15, `cadf_test` 15/15, `cadf_det_test` 13/13, `irr_fluxo_test` 34/34, `config_test` 90/90 | verde | — |
| Varreduras: `paginas_scan_test.py` 5/5 (147 páginas), `ds_1610_test.py` 16/16, `textos_soltos_test.py` 267/267 (64 telas) | verde | — |

**Vermelhos antigos, iguais na base `cbe4cd38`** (mesmas falhas, linha a linha; não são do LEVE-1 e não foram corrigidos aqui):
- `ostela.py`: 3 FALHOU (pendência, saldo 100, encerrada) e `RuntimeError: Uncaught` no fim; as linhas do item 1 passam antes da parada.
- `verif_os.py` (para na linha 60, `nova(…)`), `osfix.py` (cabeçalho inicial e parada na linha 54, `cancelar('OS-0431')`), `ap_unico_test.py nav` (6/13, para na linha 114) e `unit` ("FALHA motor JS": o harness concatena `JS_NUCLEO`, que traz a linha `# ---- camada Carência e destino`, inválida em JS). **Nestes três, o passo trocado ("Confirmar início/envio") fica depois da parada e não chegou a rodar**; o comportamento é provado pelo `leve1_test` (I1a–I1c, I1f) e pelos testes verdes acima que têm o mesmo passo (`os_v39_bloq`, `os_cenario`, `carencia fluxo`).
- `comercial_fluxo_test.py` 22/24 (AC-01: o cartão "Painel" abre `PG.dc.html#mod=com`), `comercial_revisao_test.py` 32/33 (A11), `lotest.py` (para no LO-02det, "Registrar lacre").

**Roteiro do `leve1_test` corrigido** (1ª execução no Chrome: 23/29, erros do roteiro, não do produto; bruto em `nav_leve1_test_1a_execucao_roteiro.log`): toque duplo pelo botão (I1b), Encerrar na OS-0508 sem impedimento (I1d), dia operacional pelo cenário (I3), "Liberar mesmo assim" na OM-0234 com conflito de janela (I4), fertirrigação pela tela (I9h), árvore do CD-01 expandida (I10); I8a/I8b passaram a procurar também no menu ⋯, onde a base guardava o botão (antes passavam na base).

**Disco cheio (18:10–18:20 UTC, aviso do coordenador):** os 8 testes que rodaram nesse intervalo foram refeitos depois (resultados acima); os da janela não entram nos brutos. `resumo_bateria_1.txt` guarda a lista original com horários.

## Fora desta fatia, e por quê
- **Item 4 · corretiva sem tempo de serviço.** Corretiva criada de achado ou da condição nasce com `tempo:null`; não há "tempo do serviço" a sugerir. Preencher seria inventar (a mesma regra do item 2) e o backlog já conta "sem estimativa". Fica pedindo; tornar o tempo opcional na liberação é decisão de produto que o INVENTARIO não traz.
- **Outros botões "Prévia · nada foi alterado"** fora das linhas citadas: `areas/gestao.py` "Conferir proposta de parâmetro" (GE-02 comparação) e, no GE-08 Crédito, "Conferir envio ao credor" e o aviso de "Registrar liberação da 2ª parcela" e o aviso "ajuste indisponível" do CA-02 (`areas/campo.py`). Mesmo padrão; não mexi por não estarem no pedido. Candidatos à LEVE-2.
- **Textos de especificação** que descrevem a trava antiga: R-C11 em `docs/comercial/ESPECIFICACAO.md` (recusa com carga programada) e PRD 54.4 citado no fechamento de achado ("informe o motivo"). Atualizar na próxima revisão do PRD/especificação (decisão do proprietário de 19/10).
- `docs/STATUS.md` não foi tocado (integração e status ficam com quem integra).
