# Relatos da frente PCM (Manutenção simplificada: S1, S2, 1a, S3 e S4)

Fonte: resultado do workflow `modulo-prototipo` da PCM (run `wf_56a8f31e-86f`, concluído em 09/10 às 18:48 UTC), o mesmo texto que cada agente devolveu no `journal.jsonl`. Foram três agentes Claude separados: implementar, revisar e corrigir. **A revisão abaixo é adversarial, feita por um agente Claude no papel de revisor. Não é a revisão do Codex, que continua pendente.**

Rótulos usados neste resumo:
- **executado**: a saída da execução está neste pacote, em `brutos/`;
- **relatado**: o agente diz que rodou, mas a saída não está no pacote.

As transcrições `brutos/*_transcricao_*.txt` são saídas copiadas do transcript do agente, para comandos que não gravaram arquivo de log. Nada foi reexecutado para montar o pacote.

## Resumo

### Implementação (`f9ea51a`..`21c0e51`)
- **Entrou:** Manutenção numa tela só (MA, com âncoras), regras no cenário único, CD-03 e O.S. lendo a condição da máquina, app de campo (MB-01, MB-09, MB-09det, MB-04), item 12 (um saldo, um custo) e horímetro único.
- **Ficou fora:** PCM 1b e 1c, que dependem do `cenMudar(cmd)` da SUP-2a.
- **Junções com a branch única:** `562bc23` (ecc8b00) e `6af8486` (cdc185f, sem conflito).
- **Testes depois da junção com cdc185f:**
  - executado: `ma_regras_test` 104/104 (`PCM-ma_regras.log`), `ma_app_test` 29/29, `os_aprov_lib_test` 45/45 e `aprova_quem_decide_test` 103/103 (`PCM-aqd.log`);
  - executado: `varredura` 141/141, `cmptest` sem falhas, `ma_rastreio` 58/58 e `acoes_duplicadas` 0 (`PCM-r4_*`);
  - executado: `ma_unica_test` 22/23 com espera fixa (`PCM-r4`) e depois 23/23 (`PCM-r5`, sobre 21c0e51).
- **Logs reaproveitados** (executados sobre 98c214f, antes da junção): `PCM-r1_*`, `PCM-r2_*` e `PCM-r3_*`.
- **Vermelhos atribuídos à base:** executado em `PCM-base_*` (ecc8b00: `acao_unica` responsivo, `etapas_celular` complemento e desktop, `componentes` ajustes) e `PCM-base2_cmptest.log`.

### Revisão adversarial (HEAD `21c0e51`): 1 S1, 3 S2, 6 S3 e S4

| ID | Sev. | Achado | Evidência da revisão | Correção em `ba03515` | Regressão |
|---|---|---|---|---|---|
| A1 | **S1** | "Declarar apto" deixa o Trator T1 Apto com o INSP-106 (freio, Alta, sugere Bloqueado) aberto na OM-0235. App e O.S. passam a liberar a máquina. | executado: sonda P3 em `PCM-rev_transcricao_sondas_e_mutantes.txt` (T1 "Apto", OM-0235 "A liberar") | A condição vira uma lista de motivos, e o apto encerra só o motivo daquela OM. Botão: "Encerrar o motivo da OM-0233 · Trator T1 segue bloqueado"; resposta: "Falta: INSP-106 · OM-0235". **Adaptado:** não recusa o comando, senão uma ordem esperaria a outra. | casos `REV-A1` (regras); `ma_revisao_test` A1 (executado: `PCM-r6/r8_ma_revisao_test.log`) |
| A2 | S2 | "Somar" perde a criticidade Alta e a sugestão Bloqueado | executado: P2 | Somar eleva a gravidade e oferece "Somar e bloquear"; o app avisa antes | `REV-A2` (regras e app), `ma_revisao_test` A2 |
| A3 | S2 | Estorno não desfaz a leitura; a correção vira troca de contador | executado: P1 | 3.010 h → estorno → 2.988 h; depois 2.995 h entra Confirmada | `REV-A3`; P1 de novo depois da correção (`PCM-corr_transcricao_unidade.txt`, 16:43) |
| A4 | S2 | L/h de tanque cheio ignora o parcial (7,5 em vez de 15,8 L/h) | executado: P8 | soma os parciais do intervalo | `REV-A4` |
| A5 | S3 | Depois do apto, as O.S. ficam com "Pendência com PCP · reprogramar" em qualquer fase | executado: `PCM-rev_b3.log`, `PCM-rev_b4.log` | PCP reprograma uma vez, só em A liberar | `REV-A5` em `ma_os_unit.js` (140/143 com o `processo_os` antigo: executado, transcrição 16:50) |
| A6 | S3 | "Gerar N" ignora a busca | executado: `PCM-rev_b1.log` | aplica o filtro da grade | `ma_revisao_test` A6 |
| A7 | S3 | App sem sinal: o 2º registro entra em silêncio numa OM mudada | executado: P4 | os registros seguintes da mesma OM viram conflito | `REV-A7` (`ma_app_test` 30/36 no código antigo: executado, transcrição) |
| A8 | S3 | OMs de eletricista sem executor possível (João fora do Ver como) | executado: P18 e leitura | João entra no Ver como da tela e do app (7 perfis) | `REV-A8`, `ma_revisao_test` A8 |
| A9 | S3 | "As O.S. que usam o ativo ficam impedidas" é falso fora do T1 | executado: `PCM-rev_b2.log` | só avisa ao PCP quais O.S. usam o ativo | `REV-A9` |
| A10 | S3 | Comboio (km) com consumo em L/h | executado: P9 | unidade pela `a.un` (km/L) | `REV-A10`, `ma_revisao_test` A10 |
| A11 | S3 | `o.rv` não é conferido em nenhum comando da web | especificado (grep; o caso D-46 testava a função isolada) | o painel confere a versão: "Mudou desde que você abriu" | `REV-A11`, `ma_revisao_test` A11 |
| S4 | S4 | 9 de 40 mutantes de regra vivos (M18, M21, M24, M30, M31, M36, M37, M39, M40); AC-PCM-17 nunca conferido; BM6 (F22) passa; `ma_atrito` conta 9 em vez de 8; AC-PCM-14 com "Apto" por padrão. Também: encerrar com conflito do app pendente, autor não gravado e "Mover mesmo assim" zerando o conflito aceito. | executado: mutantes em `PCM-rev_transcricao_sondas_e_mutantes.txt` e `PCM-rev_mut_browser_*` | testes corrigidos; travas e autor gravados | casos `REV-S4`. **Relatado:** "os 9 mutantes vivos agora são pegos" (não há saída da nova rodada dos mutantes). `ma_revisao_test` com A6, A11 e F22 desfeitos: 15/18 (executado: `PCM-r6_mutantes_ma_revisao.log`). |

### Correção (`ba03515`): testes

| Comando | Resultado | Rótulo |
|---|---|---|
| `ma_regras_test.py` (com `ma_os_unit.js`) | 143/143 | executado: `PCM-corr_transcricao_unidade.txt` (18:08) |
| `ma_app_test.py` | 36/36 | executado: idem |
| `aprova_quem_decide_test.py` | 103/103 | executado: idem |
| `os_aprov_lib_test.py` | 45/45 | executado: idem |
| regras e app contra o código antigo | 113/129 e 30/36 | executado: idem (16:49–16:50) |
| `build.py` / `montar_render.py` | 0 FALHA / 141 páginas | executado: `PCM-build.log`, `PCM-render.log` e transcrição |
| `varredura.py` | 141/141 | executado: `PCM-r7/r8/r9_varredura.log` |
| `acoes_duplicadas.py` | 0 com ação repetida | executado: `PCM-r7/r9_acoes_duplicadas_*` |
| `ma_unica_test` | 23/23 | executado: `PCM-r7` |
| `ma_revisao_test` (novo) | 18/18 | executado: `PCM-r6`, `PCM-r8` |
| `ma_app_fluxo_test` | 24/24 | executado: `PCM-r9` (o `PCM-r8` deu 23/24 antes do último ajuste) |
| `ma_rastreio_test` | 58/58 | executado: `PCM-r8` (o `PCM-r7` deu 57/58 em F95 antes da troca da coluna para "Consumo") |
| `ma_atrito` 13/13, `ma_planos` 18/18, `ma_correcoes_om` 15/15, `ma_correcoes_pm` 12/12, `matest` 40/40, `cada_fix03` 11/11, `links_ocultos` 8/8, `map_decisoes` 18/18 | todos sem falha | executado: `PCM-r7` |
| `mbtest` / `cada_cd03` / `app_restaurar` | 0 falhas / 14/14 / 4/4 | executado: `PCM-r9`, `PCM-r8`, `PCM-r9` |
| `ostest` 32/33 e `osacoes` 5 falhas | vermelho atribuído à base | executado: `PCM-r7`. **Relatado:** "iguais aos da base" (a base dessa comparação não está no pacote) |

### Pontos para o revisor
- **A1, o antigo S1, precisa de nova tentativa pela tela e pela regra.** O critério do aceite está na fila do integrador:
  - com INSP-105 (OM-0233) e INSP-106 (OM-0235) abertos, concluir a OM-0233 com o teste aprovado não deixa o T1 Apto;
  - o app continua dizendo que o T1 não pode operar;
  - a OS-0420 e a OS-0431 continuam impedidas.
- **Continuam fora do merge:**
  - item 12: as peças da oficina não geram movimento no Estoque. É S2 da base até o PCM-1b;
  - cerca de 40 páginas ainda mostram "T1 bloqueado" fixo;
  - a Gestão mostra a OM-0233 a R$ 18.400, contra R$ 6.180 na MA (dado anterior ao PCM).
- **O estado salvo subiu para a versão 5 (D-53).** Quem tinha a versão 4 salva volta à demonstração inicial.

## implementacao

**Por que a tarefa do PCM aparecia em vermelho:** a execução foi interrompida duas vezes antes do fim: pela cota semanal em 06/10 e pela interrupção da sessão em 09/10 às 13:05. Nada se perdeu: todo o código já estava em commits na branch, e só faltavam a última bateria de testes e este relatório. Hoje concluí as duas coisas. Os passos S1, S2, 1a, S3 e S4 estão prontos; 1b e 1c ficaram de fora, como a tarefa mandou. No começo não havia nada sem commit; as pastas `.base*/`, `_render/` e `project/` são cópias e saídas de build, fora do controle de versão.

#### Commits (branch `claude/v44-pcm`, base 99537ca)
- `f9ea51a` PCM S1+S2+1a: Manutenção num só lugar (tela MA) com regras no cenário único
- `eba72ba` PCM S1: links de fora apontam para o registro na tela MA
- `a89a05d` PCM S3: CD-03 e O.S. leem condição, responsável técnico e leitura da Manutenção
- `5f4ff11` PCM S4: app de campo (MB-01, MB-09, MB-09det, MB-04) com Ver como e sem sinal
- `a88d51f` PCM S1/S2: testes antigos da Manutenção no endereço novo e correções que eles acharam
- `0725404` PCM: aceite da tela única (ma_unica), rastreio F01–F111, atrito e testes vizinhos
- `562bc23` Merge claude/prototipo-v44 (ecc8b00)
- `0c68f18` PCM 1a: item 12 (um saldo, um custo) e horímetro único / Gerar ordem conferidos em teste
- `98c214f` docs: DECISOES §7 (implementação, D-50 a D-54, item 12, próximos passos 1b/1c)
- `6af8486` Merge claude/prototipo-v44 (cdc185f), feito hoje, sem conflito
- `21c0e51` PCM: ma_unica com recusa e repetição a 390 px e espera do redirecionamento, feito hoje

#### Testes executados hoje, depois da junção com cdc185f
- `build.py` → 0 FALHA. `montar_render.py` → 141 páginas.
- `ma_regras_test.py` → 104/104. Inclui o item 12 e o horímetro único / Gerar ordem.
- `ma_app_test.py` → 29/29. `os_aprov_lib_test.py` → 45/45. `aprova_quem_decide_test.py` → 103/103.
- `varredura.py` → 141/141 páginas sem erro.
- `acoes_duplicadas.py . /tmp/PCM-dup.json` → 141 páginas, 0 com ação repetida, 0 erros.
- `ma_rastreio_test.py` → 58/58. Cobre F01–F111, cada função uma vez.
- `ma_unica_test.py`:
  - Primeira rodada: 22/23. O AC-PCM-02 leu MA-02 e MA-03 antes de a tela MA montar, porque a máquina estava carregada por outras frentes.
  - Mudei a espera do teste, sem mudar a regra nem a expectativa: em vez de 1,3 s fixos, ele espera o destino por até 10 s.
  - Acrescentei dois casos a 390 px: a recusa (Ana vê os comandos desabilitados com o motivo, e nada muda) e a repetição (duplo toque reserva as peças uma vez só).
  - Segunda rodada: 23/23.
- `cmptest.py` → sem falhas. Na rodada de 09/10 às 12:5x ele falhou uma vez em "envio adicional simulado": a resposta simulada apagou o aviso antes da leitura. O código de Compras é idêntico ao da base, então registro como intermitente, não como corrigido.

#### Logs reaproveitados (executados em 09/10 entre 11:25 e 12:56 sobre `98c214f`)
A junção mudou só o `varredura.py` e documentos; o código das telas é o mesmo, então valem estes resultados:
- **Manutenção:** matest 40/40, ma_planos 18/18, ma_correcoes_om 15/15, ma_correcoes_pm 12/12, ma_atrito 13/13, ma_app_fluxo 22/22.
- **Cadastros e O.S.:** cada_cd03 14/14, cada_fix03 11/11, cada_cd04 15/15, map_decisoes 18/0, os_v39_bloq 11/11, tabelas_os 38/38, os_ator 15/15.
- **App de campo:** mbtest 0 falhas, app_cenario 15/15, app_mb04 6/6, app_mb02det 8/8, app_mb03_turno 11/11, app_mb03x 7/7, app_entrega_parcial 7/7, app_os0424 9/9, app_saldo_zero 12/12, app_restaurar 4/4.
- **Outros:** links_ocultos 8/0, producao_fluxo 66/66, esttest OK.
- **Variantes:** acao_unica saf 10/0, familias 8/0 e v3 10/0; componentes matriz 3/0 e rotacao 6/0; etapas_celular celular 14/0.

#### Testes ainda vermelhos (nenhum aponta para a Manutenção)
- **Já conhecidos da base:**
  - os_cenario 19/20 (PEND-OS-01).
  - componentes_ajustes 2 falhas, iguais às da base ecc8b00. No item 26 a MA passa; a falha está em SAF e SU-01.
  - etapas_complemento 2 falhas, iguais às da base (CMP, SAF e O.S.).
  - etapas_desktop 0/1: falta a base `gen37_antes`.
- **Fora da lista de conhecidos:** acao_unica responsivo, 1 ok e 2 falhas. Na base ecc8b00 as falhas são idênticas (SAF etapa 6, CMP etapa 3 e SAF a 360×420). Vieram com a junção da SAF, não do PCM. O integrador precisa saber.

#### Expectativas mudadas, com motivo (detalhe nos commits `a88d51f` e `0725404`)
- **Tela única:** MA-0x e PM viram âncoras da MA, e a faixa "Telas da manutenção" sai (D-05). Por isso:
  - acao_unica 12 e 14 mudam;
  - map_decisoes 6 e 14 apontam para MA#om=;
  - MA-01 sai das faixas do etapas_celular;
  - componentes 26 usa MA#vis=ativos.
- **Regras novas da especificação:**
  - Só o executante edita a resposta da tarefa (matriz §3.1).
  - OM com conflito libera por "Liberar mesmo assim", ponte até o 1b.
  - Gerar ordem sai do detalhe do plano e passa ao painel do vencimento (F21).
- **Perfis:**
  - O perfil "Otávio · Gestor" dos testes antigos passa a "Gil · Gestor" (D-51), porque Otávio agora é o responsável de manutenção.
  - cada_cd04 passa de 10 para 11 pessoas, com o Otávio.

#### Fora desta entrega
- PCM 1b e 1c: dependem do `cenMudar(cmd)` do SUP-2a, que está em outra frente; registrados como próximos no DECISOES §7.
- Ficha do pivô e teste do solo: frente Irrigação + Solo.
- Separadores, hover e retorno visual na troca de tela: frente DS.
- COLH-C01 e A-17: módulo Colheita.

#### Riscos
- **Item 12, ainda S2:** o estoque da manutenção (`c.man.itens`) continua próprio. O 1a garante um saldo e um custo, e a conservação está testada. Mas receber, aplicar e devolver ainda não geram movimento em `c.movs`, e o Estoque não vê as peças da oficina. Isso só fecha no 1b.
- **Estado salvo:** o cenário agora está na versão 5 (D-53). Quem tinha uma versão 4 salva volta à demonstração inicial.
- **Revisão:** o Codex ainda não revisou (revisão sem bloquear, AGENTS §3.5).
- **Testes com espera fixa:** com a máquina carregada, testes de outras frentes que esperam um tempo fixo podem falhar de forma intermitente.

Não fiz push nem PR, e não publiquei o artefato: isso fica com o integrador.

Arquivos mexidos hoje:
- <sp-pcm>/tools/prototipo/v37/gen37/ma_unica_test.py
- <sp-pcm>/docs/pcm-simplificado/DECISOES.md

Logs em /tmp/PCM-r1 a /tmp/PCM-r5 e na base em /tmp/PCM-base.

## revisao

### Revisão adversarial PCM (S1, S2, 1a, S3 e S4) · branch `claude/v44-pcm` @ 21c0e51

Encontrei 1 achado S1, 3 achados S2, 6 achados S3 e alguns S4. Tudo rodou numa cópia em `scratchpad/pcmrev`, que já apaguei. Nenhum arquivo versionado foi alterado e não há trabalho meu pendente na worktree. Fiz testes de unidade sem navegador, sondas no navegador uma por vez e mutantes nos testes novos. A tag no início de cada reprodução diz o que rodou (executado) e o que só li no código (especificado).

**Base conferida antes dos ataques:**
- `ma_regras_test` 104/104.
- `ma_app` 28/28.
- `ma_unica_test` 23/23, em 225 s.

#### S1

**A1 · "Declarar apto" libera a máquina com um segundo defeito bloqueante aberto.**
- **Reprodução (executado, probes/p1.js P3; a mensagem também em p2.js P20):**
  1. Zé registra INSP-106 no Trator T1, já bloqueado: "Rodado e freios · Freio de serviço sem ação", Alta, sugere Bloqueado, com "Registrar e bloquear".
  2. O sistema responde "Trator T1 bloqueado", mas a condição não muda: o achado de origem continua INSP-105.
  3. A corretiva OM-0235 é criada sem tratar a condição e sem "Teste do reparo".
  4. Zé conclui a OM-0233 com o teste aprovado e declara apto.
  5. Resultado: o Trator T1 fica **Apto**, com o INSP-106 (Alta/Bloqueado) aberto na OM-0235 em A liberar. O app passa a dizer "Apto para operar", e as OS-0420 e OS-0431 perdem o impedimento.
- **Dano:** a máquina vai a campo com um defeito de freio registrado como bloqueante. É um comando físico perigoso.
- **Causa:**
  - `dados_manutencao.py:768`: a mensagem "bloqueado" aparece mesmo quando `manCondicao` devolve `nada`.
  - `:830`: num ativo já bloqueado, o novo motivo não é gravado.
  - `:801`: a corretiva não trata a condição porque `condInfo.om` está aberta.
  - `:723-728`: `manAptoMotivo` e `manDeclararApto` não olham outros motivos nem achados abertos com sugestão Bloqueado.
- **Correção:**
  - A condição passa a ser uma lista de motivos, cada um com seu achado e sua OM.
  - "Registrar e bloquear" num ativo bloqueado acrescenta um motivo.
  - "Declarar apto" encerra só o motivo daquela OM e só deixa o ativo Apto quando não sobra nenhum motivo. Fora isso, recusa com "Falta: INSP-106 · OM-0235".
  - Corrigir a mensagem.

#### S2

**A2 · "Somar" perde a sugestão Bloqueado e a criticidade Alta.**
- **Reprodução (executado, P2 e sonda b4):**
  - Achado no Trator 02, Hidráulico, Alta, sugere Bloqueado.
  - O painel oferece como **única primária** "Somar ao INSP-104". Bloquear só existe na secundária "Registrar novo".
  - Depois de somar, o INSP-104 continua Média/Apto, o Trator 02 continua Apto e a primária do achado vira "Vincular à OM-0234" (janela 28/09).
  - No app, `manAppConfAplicar` soma sozinho quando há repetição (`:975`).
- **Causa:** `dados_manutencao.py:763-764`, que só acrescenta ocorrência e evidência; `maquinas.py:614`; MB-04 em `mobile.py` perto de 681-686.
- **Correção:**
  - Somar eleva criticidade e sugestão para o valor mais grave e guarda criticidade, sugestão e autor por ocorrência.
  - Com sugestão Bloqueado, quem tem a competência ganha "Somar e bloquear".
  - O app não soma em silêncio quando a ocorrência nova é mais grave.

**A3 · O estorno não desfaz a leitura do lançamento estornado; a correção vira "troca de contador" e desloca o histórico.**
- **Reprodução (executado, P1):**
  1. AB-1043 no Trator 02 com 3.010 h por erro de digitação (era 2.995). É plausível, então entra Confirmada e vira a leitura atual.
  2. "Corrigir com estorno": a leitura atual continua 3.010 h e LT-0016 continua Confirmada.
  3. O lançamento certo, com 2.995 h, cai em "menor que a anterior · confirme a troca de contador".
  4. Confirmar desloca marco e últimas execuções em −15 h: OM-0219 passa a 2.778 h e a Revisão 250 h passa a vencer em 3.028 h em vez de 3.043 h.
- **Causa:** `dados_manutencao.py:902-906` só descarta a leitura se ela estiver "A confirmar"; `:873-877` aplica o deslocamento.
- **Correção:** o estorno marca a leitura do lançamento como Estornada e, se ela for a atual, volta à última leitura confirmada anterior e recalcula.
- **Aceite:** 3.010 → estorno → 2.988; depois 2.995 entra Confirmada, sem pedir troca.

**A4 · O L/h "tanque cheio" ignora o abastecimento parcial entre dois tanques cheios.**
- **Reprodução (executado, P8):** parcial de 100 L a 2.994 h, depois cheio de 90 L a 3.000 h (anterior cheio a 2.988 h). O sistema mostra "7,5 L/h (tanque cheio)"; o correto é (100+90)/12 = 15,8 L/h.
- **Dano:** desvio de −50% contra a referência de 15 L/h; o filtro e o alerta "Desvio de consumo" erram.
- **Causa:** `dados_manutencao.py:889-891`, que usa só `b.vol`.
- **Correção:** somar todos os lançamentos não estornados do ativo com leitura no intervalo (anterior cheio, atual].

#### S3

**A5 · Regressão na O.S.: depois do apto, OS-0420 e OS-0431 ficam com "Pendência com PCP · reprogramar".**
- **Executado (b3/b4):**
  - Antes: OS-0431 com "PCP · substituto"; OS-0420 com "Manutenção · OM-0233".
  - Depois do apto: as duas com "PCP reprogramar". O painel da OS-0431 diz ao mesmo tempo "O agrônomo confere… e libera" e "Pendência com PCP"; a OS-0420, Em execução, passa a ter o PCP como dono.
- **Especificado (leitura):** `osManCond` (`processo_os.py:278-283`) roda em todo merge e em qualquer fase, sobrescrevendo `o.cond`, `o.dono` e `o.prazo`. A pendência fica para sempre, inclusive em Em conferência e Encerradas.
- **Correção:** com a máquina apta, só limpar `bloq` e os selos e deixar o dono normal da fase; o "reprogramar" vale uma vez e só em A liberar.

**A6 · "Gerar N" ignora a busca da grade Sem ordem.**
- **Executado (b1):** a busca "Trator 03" deixa 1 linha, mas a primária continua "Gerar 3 ordens preventivas" e gerou OM-0235 (a03), OM-0236 (a06) e OM-0237 (a11).
- **Causa:** `maquinas.py:320` usa `self.__so` sem `g2match`; o Kanban já usa, em `:297`.
- **Correção:** aplicar `g2match(r, ma_G('g_so'), g2st(self, 'g_so'))`.

**A7 · App sem sinal: a versão `o.rv` projetada colide e o 2º registro entra em silêncio numa OM que mudou no escritório.**
- **Executado (P4):**
  1. Zé, sem sinal, responde t0 (rv=2 na fila) e t1 "Não feito" (rv=3 na fila).
  2. No escritório, Otávio vincula o INSP-104 à OM-0234, que vai para rv=3.
  3. Na volta do sinal, d1 vira conflito e **d2 é aplicado** (t1 = Não feito).
- **Causa:** `dados_manutencao.py:953`, que grava o rv da projeção na fila, e `:965`, que compara com o rv atual.
- **Correção:** guardar o rv do servidor no primeiro registro daquela OM e comparar com base + registros aplicados desta fila; os registros seguintes da mesma OM viram conflito.

**A8 · As OMs de eletricista não têm executor possível no protótipo.**
- **Executado (P18 e leitura):**
  - O Ver como da tela e o do app não têm João: G2_PERFIS = Ana, Caio, Rui, Paula, Zé, Otávio (`g2lib.js:260-262`); `MA_PERFIS` (`maquinas.py:68`); `MB_US` = Marcos, Zé (`mobile.py:1305`).
  - A OM-0228 fica em Liberadas para sempre e "Encerrar restrição" é recusado porque ela trata a restrição. A Bomba do Pivô 2 fica presa em Restrito. A OM-0237 libera para João e também para.
  - O teste AC-PCM-13 só passa com um perfil inventado `{k:'João'}` (`ma_regras_unit.js:151-156`).
- **Correção:** João (irrigante, NR-10) no Ver como e no app, e um teste de navegador desse caminho.

**A9 · A mensagem "as O.S. que usam o ativo ficam impedidas" é falsa fora do T1.**
- **Executado (b2):** bloquear o Trator 02, alocado na OS-0420 de 24 a 28/09, mostra a mensagem. A O.S. segue só com o selo do T1 e diz "O Trator 02 assume a partir de 24/09".
- **Causa:** `dados_manutencao.py:834`; o `BLOQ` da O.S. só tem `aid=a01`.
- **Correção:** mensagem sem promessa ("impedimento nas O.S. no Bloco 2, PCMS-A05"), ou listar as O.S. alocadas como aviso.

**A10 · O comboio (km) mostra consumo com unidade errada.**
- **Executado (P9):** "0,3 L/h (tanque cheio)" a partir de km.
- **Causa:** `dados_manutencao.py:889-901` e o rótulo L/h em `ma_consumo`/`ma_linhaAb`.
- **Correção:** unidade pela `a.un` (L/km ou km/L).

**A11 · A versão do registro (`o.rv`) não é conferida em nenhum comando da web.**
- **Executado (grep):** `manRv` (`dados_manutencao.py:473`) não tem chamador. O caso "D-46 · comando com versão… é recusado" (`ma_regras_unit.js:241`) testa essa função direto, então passa sem testar nada que exista na tela.
- **Por que é S3:** a especificação §3.1 diz que todo comando leva `o.rv`. A barreira por estado reduz o dano.
- **Correção:** `ma_cmd` passa o `o.rv` lido ao abrir o painel e cada comando chama `manRv`; ou tirar a promessa e o teste.

#### S4

**Testes que passam sem testar (executado):**
- **Mutantes de regra:** 31 de 40 morreram. Os 9 vivos são M18 (apto fora de Em conferência), M21 (incluir tarefa em preventiva), M24 (restringir sem prazo), M30 (autor muda ao editar o motivo), M31 (resposta sem ser executante), M36 (aplicar acima do planejado sem saldo), M37 (gerar em dia), M39 (vincular OM Em conferência), M40 (encerrar com sobra).
  - A regra de cada um está certa no código hoje: as sondas P10 a P17 mostram as travas funcionando (a P12 cobre M36; a M30 não tem sonda).
  - O problema é que nenhum teste protege essas regras.
- **AC-PCM-17 (`ma_unica_test.py:84`):** `'Aptos agora' in apt.title()` é sempre falso, porque `title()` gera "Aptos Agora", e o `and/or` faz o limite de 4 cartões nunca ser conferido. O mutante BM1, com 5 cartões, passou 23/23. O mutante BM2 (primária no cabeçalho com painel aberto) foi pego.
- **F22 / AC-PCM-23:** o mutante BM6 tira a sugestão de marco do painel Vínculo e passa em `ma_rastreio` 58/58, `ma_planos` 18/18 e `ma_correcoes_pm` 12/12. O exit 1 do `ma_planos` foi só falta da pasta `_probe/manut` na cópia.
  - Em `ma_rastreio`, 14 funções são conferidas só por texto no HTML gerado: F06/07, F22, F68/69/78, F76, F79/92, F103/104, F107/108 e F110.
- **`ma_atrito_test.py:74`:** conta o clique em "Sede · D-118", que não existe para o Trator 02 (só o comboio é elegível). O total publicado é 9; o real é 8.
- **AC-PCM-14 `tres()` (`ma_unica_test.py:111`):** "Apto" é o valor padrão para qualquer página sem o texto, então uma O.S. quebrada passaria.

**Outros:**
- "Encerrar" é aceito com um conflito do app ainda "A resolver" (P5; `:744-748`).
- Quem iniciou a OM não é gravado (P6; `:629-631`). Também não gravam o autor: solicitar compra, registrar recebimento, resolver sobras e mudar criticidade.
- "Mover mesmo assim" numa OM Liberada zera o `conflitoAceito` (P19; `:605`).
- O app grava como operador o próprio usuário: Zé, mecânico, vira operador do abastecimento (`mobile.py:1035`).
- A lista de responsável técnico é fixa (`maquinas.py:580`), um cadastro paralelo ao CD-04. "Equipe elétrica" não é pessoa.
- **Já existia antes do PCM, agora com link direto:**
  - A Gestão mostra a OM-0233 a R$ 18.400 (NF de oficina terceira, `gestao.py:279`, `:347`), enquanto a MA calcula R$ 6.180 estimados, feita pelo Zé e sem terceiro.
  - Cerca de 40 páginas seguem com "T1 bloqueado" fixo depois do apto.

#### O que tentei e não quebrou (executado)

- **Repetição:**
  - Duplo toque em "Gerar" gera 3, não 6.
  - Liberar duas vezes reserva uma vez só.
  - Abastecimento e leitura avulsa com a mesma chave gravam uma vez.
  - Corretiva repetida, com outra chave, devolve a mesma OM.
  - A fila do app reenviada não duplica.
- **Permissões:** Ana não responde tarefa; Zé não gera, não move nem libera; Zé não bloqueia o Trator 03; Otávio não registra o teste; Ana não declara apto.
- **Travas:** apto fora de Em conferência, gerar em dia, vincular OM Em conferência, incluir tarefa em preventiva, restringir sem prazo, aplicar sem saldo e encerrar com sobra são recusados.
- **Números:** Item 12 conserva saldo e custo; C1 R$ 2.626, C3 R$ 4.392 e R$ 1.692 conferem.
- **Leituras:** leitura menor recusada na conclusão; tíquete com data antiga; leitura implausível dá aviso.
- **Conflito sobre a alocação:** OM-0234 e OM-0236 com conflito; OM-0235 e OM-0237 sem.
- **Chave antiga:** `talhao-os-manutencao-v1` não aparece em nenhum código nem página.
- **Links e telas de fora:** os links de fora apontam para `MA#om=` e `MA#ativo=`. O CD-03 mostra o Trator 02 bloqueado e o T1 apto nos três lugares. Redirecionamentos e F5 funcionam (`ma_unica` 23/23).
- **Célula de volume:** mostra "180 L", com unidade.

#### Fora do que conferi

Não refiz a bateria das outras frentes. Não conferi de novo os vermelhos herdados da base que o implementador citou (`acao_unica` responsivo e outros).

Arquivos (em `<scratchpad>/pcmrev/`, ~1 MB):
- probes/p1.js
- probes/p2.js
- probes/run.py
- mut/mutar.py
- mut/bmut.sh
- mut/browser/resumo.txt
- b1.log a b4.log
- unica_base.log

## correcao

Commit **ba03515** "PCM: correções da revisão" na branch `claude/v44-pcm` (`<sp-pcm>`), sem push. Ao retomar, não havia nada pela metade: a worktree estava limpa em 21c0e51, então nada foi refeito nem descartado. Corrigi todos os achados S1, S2 e S3 e os S4 de custo baixo, cada um com teste de regressão (registro em `docs/pcm-simplificado/DECISOES.md` §8, D-50 a D-56).

**O que mudou**
- **A1 (S1):** o ativo pode ter vários motivos de bloqueio, cada um com seu achado e sua ordem. "Declarar apto" encerra só o motivo daquela ordem; o ativo só fica Apto quando não sobra nenhum. Com outro motivo aberto, o botão diz "Encerrar o motivo da OM-0233 · Trator T1 segue bloqueado" e a resposta mostra o que falta (ex.: "Falta: INSP-106 · OM-0235").
  - Não recusei o comando, como o revisor sugeria: cada ordem ficaria esperando a outra e nenhuma poderia ser encerrada.
- **A2 (S2):** somar uma ocorrência mais grave eleva a criticidade e a condição sugerida do achado e guarda o autor de cada ocorrência. Quem tem a competência ganha "Somar e bloquear".
- **A3 (S2):** o estorno desfaz a leitura do lançamento estornado (3.010 h volta a 2.988 h; depois, 2.995 h entra sem pedir troca de contador).
- **A4 (S2):** o consumo de tanque cheio a tanque cheio soma os abastecimentos parciais do meio (15,8 L/h no caso da revisão).
- **A5:** com a máquina apta, a O.S. perde só o impedimento. O PCP reprograma uma vez, em A liberar; nas outras fases, a ordem volta ao dono normal.
- **A6:** "Gerar N" gera só o que a busca da grade Sem ordem mostra.
- **A7:** no app sem sinal, um registro feito numa OM que mudou no escritório vira conflito, e os seguintes da mesma OM também.
- **A8:** João entrou no Ver como da tela e do app. Ele executa as ordens de eletricista e é o responsável técnico das bombas e do pivô; a "Equipe elétrica", que não é pessoa, saiu.
- **A9:** bloquear deixa de prometer que as O.S. ficam impedidas; só avisa ao PCP quais O.S. usam o ativo.
- **A10:** o consumo mostra a unidade certa na célula (L/h ou km/L).
- **A11:** o painel da OM confere a versão em todo comando. Se a OM mudou em outra aba, o toque é recusado com "Mudou desde que você abriu"; o toque seguinte confirma.
- **S4:**
  - "Encerrar ordem" exige resolver antes os registros do app pendentes.
  - Iniciar, solicitar compra, registrar recebimento, resolver sobras e mudar criticidade passam a gravar quem fez.
  - "Mover mesmo assim" mantém o conflito como aceito.
  - O operador do abastecimento no app nunca é o mecânico por padrão.
  - Os testes que passavam sem testar foram corrigidos, e os 9 mutantes vivos agora são pegos.

**Testes (executados)**

| Comando | Resultado |
|---|---|
| `ma_regras_test.py` (inclui o novo `ma_os_unit.js`) | 143/143 |
| `ma_app_test.py` | 36/36 |
| `aprova_quem_decide_test.py` | 103/103 |
| `os_aprov_lib_test.py` | 45/45 |
| `build.py` | 0 FALHA |
| `montar_render.py` | 141 páginas |
| `varredura.py` | 141/141 |
| `acoes_duplicadas.py` | 0 com ação repetida |
| `ma_unica_test.py` | 23/23 |
| `ma_revisao_test.py` (novo) | 18/18 |
| `ma_app_fluxo_test.py` | 24/24 |
| `ma_atrito_test.py` | 13/13 |
| `ma_rastreio_test.py` | 58/58 |
| `ma_planos_test.py` | 18/18 |
| `ma_correcoes_om_test.py` | 15/15 |
| `ma_correcoes_pm_test.py` | 12/12 |
| `matest.py` | 40/40 |
| `mbtest.py` | 0 falhas |
| `cada_cd03_test.py` | 14/14 |
| `cada_fix03_test.py` | 11/11 |
| `links_ocultos_test.py` | 8/8 |
| `map_decisoes_test.py` | 18/18 |
| `app_restaurar_test.py` | 4/4 |

- **Os testes novos pegam o defeito:** contra o código antigo, as regras falham (113/129 e 30/36). Na tela, devolvendo os erros de A6, A11 e F22, `ma_revisao_test` cai para 15/18.
- **Vermelhos que vieram da base, não do PCM:** `ostest` 32/33 e `osacoes` 5 falhas, as mesmas já vistas nos logs da base de outras frentes.
- **Testes de outras frentes que alterei:**
  - `aprova_quem_decide_unit.js` e `os_aprov_lib_unit.js` agora esperam 7 perfis, por causa do João.
  - Em `ma_rastreio` (F95), a coluna passou a se chamar "Consumo".
  - Em `ma_atrito` (e), o toque no tanque só conta quando há escolha: o total medido é 8, não 9.

**Recusados:** nenhum.

**Riscos que ficam**
- A Gestão mostra a OM-0233 a R$ 18.400 (nota de oficina terceira), contra os R$ 6.180 estimados na Manutenção. O dado é anterior ao PCM e é da Gestão; fica para o 1b/1c.
- Cerca de 40 páginas ainda mostram "T1 bloqueado" fixo, porque não leem o estado da Manutenção.
- 13 funções do rastreio ainda são conferidas só pelo texto da página. As F79/92 e F107/108 também têm teste de regra.
- A entrada de João no cadastro de perfis compartilhado pode dar conflito de merge com outras frentes que mexam nessa lista.

Apaguei as cópias `.base99537ca` e `.baseecc8b00` e os arquivos de sonda.

**O que o proprietário pode conferir:** em Manutenção › Ativos › Trator T1, com Ver como Zé, use "Registrar achado" (freio, Alta, Bloqueado) e toque "Registrar e bloquear". Depois conclua a OM-0233 e veja que o botão de aptidão diz que o T1 segue bloqueado. Em seguida, com Ver como João, abra a OM-0228 e leve a Bomba do Pivô 2 até apta.
