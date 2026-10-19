## implementacao

Retomei a frente DOM. As duas correções, B-R8 e COLH-C01, estavam commitadas antes de a sessão cair, e nesta retomada só faltava terminar a bateria de testes. Não houve commit novo. A worktree `<sp-dom>` (branch `claude/v44-dom`, base ecc8b00) não tem nada pendente; só sobram arquivos gerados fora do git (`project/`, `_render/`, `_probe/*.png`, `__pycache__`). Não fiz push.

**Estado encontrado**
- Os 5 commits da tarefa estavam no log e não havia mudança pendente.
- A bateria anterior tinha parado no meio de `producao_fluxo_test.py revisao` (o log terminava sem resultado). Rodei esse teste de novo, mais o `consumo_divergente_test.py`.
- Apaguei as duas cópias temporárias de base que eu tinha criado (cerca de 119 MB, em `scratchpad/dom/base` e `scratchpad/dom/copia`); as provas de vermelho na base já constavam dos commits.

**Commits (todos de 09/10, já existentes)**
- `e2d1040` B-R8: divergência de consumo/dose no fecho do turno abre revisão do agrônomo
- `f0a0cd8` B-R8: revisão técnica na linha do apontamento (O.S.) e divergência no recibo do app
- `f614da7` COLH-C01: café em litros fica "sc a apurar" com ou sem área apontada
- `dbc1acc` B-R8: testes da O.S. com a revisão técnica da dose antes do encerramento
- `7f26b3b` CONTROLE-01 G3: registro da B-R8 feita no protótipo e da precisão escolhida

**Testes executados hoje, no HEAD 7f26b3b**
- `python3 build.py`: 0 FALHA, 140 telas. `python3 montar_render.py`: 140 páginas montadas.
- Testes de regra (sem navegador), todos sem falha:
  - `dose_divergente_test.py unit`: 22/22. Na base ecc8b00 dava 4/22; o harness do Codex virou os casos D01 e D02.
  - `cafe_apurar_test.py unit`: 14/14. Na base dava 1/14.
  - `producao_unit_test.py`: 121/121.
  - `inicio_entrega_test.py`: 26/26.
  - `ap_unico_test.py unit`: 80/80.
  - `aprova_quem_decide_test.py`: 102/102.
  - `assinatura_unit_test.py`: 76 verificações, 0 falhas.
  - `carencia_test.py unit`: 50/50.
  - `legal_unit_test.py`: 35/35.
  - `mip_unit_test.py`: 34/34.
  - `os_aprov_lib_test.py`: 45, 0 falhas.
  - `quantidade_test.py`: 14/14.
- Navegador, um por vez na trava `/tmp/cdpB.lock`:
  - `producao_fluxo_test.py revisao`: 18/18 (era o teste interrompido).
  - `consumo_divergente_test.py`: 20/21, sai com código 1. É o vermelho já conhecido da base: o Estoque, etapa 4, não mostra "1 L em conferência" no disponível do Fungicida A.

**Navegador executado na sessão anterior (09/10, logs em `/tmp/DOM-lote1..3`)**
- Mesmo código de produto do HEAD (depois de `f614da7` só mudaram testes e documentos):
  - `dose_divergente_test.py nav`: 17/17. Cobre o app a 390 px, lista, Kanban, painel, recusa do Rui, motivo vazio, aceite, repetição, conferência bloqueada, correção a 390 px e encerramento.
  - `cafe_apurar_test.py nav`: 10/10.
  - `varredura.py`: 140/140 páginas sem erro.
  - `acoes_duplicadas.py . /tmp/DOM-dup.json`: 0 páginas com ação repetida.
  - `os_cenario_test.py`: 20/21. A falha que sobra é o vermelho da base "A liberar sem revisão" (PEND-OS-01).
  - Também passaram: `os_v39_bloq` 12/12, `os_v39_liberar` 20/20, `os_ator` 15/15, `ap_unico nav` 23/23, `est_cenario` 15/15, `est_fix2` 11/11, `esttest` 1/2/3 (22, 23 e 19 OK), `tabelas_est` 34/34, `tabelas_os` 38/38, `carencia fluxo` 41/41, e `producao_fluxo` modos os 8/8, fluxo 21/21, erros 12/12 e celular 7/7.
- Rodados antes do COLH-C01 (11:36–12:02), que não mexe nas telas do app: `app_cenario` 15/15, `app_entrega_parcial` 7/7, `app_mb02det` 8/8, `app_mb03_turno` 11/11, `app_mb03x` 7/7, `app_mb04` 6/6, `app_os0424` 9/9, `app_restaurar` 4/4 e `app_saldo_zero` 12/12.

**Expectativas mudadas, com o motivo escrito no commit**
- `inicio_entrega_unit.js` N5 (`e2d1040`): 80 L de Fungicida A e 0 L de Adjuvante em 100 ha, contra 50 L e 25 L planejados, agora mostram também o selo de divergência, pela regra nova.
- `os_cenario_test.py` passo 8 e o novo 8b (`dbc1acc`): 180 L de Glifosato informados contra 200 L planejados bloqueiam o encerramento até a Ana aceitar com motivo.
- `os_v39_bloq_test.py` (`dbc1acc`): 300 L informados contra 320 L planejados. Primeiro aparecem o selo e a pendência com a Ana; depois da revisão, volta "conferir e encerrar" com o Marcos.
- `consumo_divergente_test.py` (`f0a0cd8`): passa a sair com código 1 quando alguma verificação falha, como pediu o Codex no §5 ("19/20 com exit 0 é falha"). O vermelho dele não é o caso B-R8.

**Escolha registrada**
- A comparação usa o centésimo da unidade, a mesma precisão da regra de quantidade (`cenQtd`), sem tolerância. O LIM_DISP (20 %) é alçada de área dispensada, não tolerância de consumo, por isso não entrou.
- Está registrado em `docs/controle-01/PLANO.md` (G3) e em `docs/colheita/DECISOES.md` D-38.

**O que ficou fora**
- A-17 (fator 50/60 do contrato): é da frente COM.
- Estilos do design system: frente DS.
- Menu `MENU2` sem mudança, porque a especificação não pedia.
- O rendimento do café beneficiado (`x.ben`) só é lido. Quem grava é o BEN-4 (R-D02), da frente do Beneficiamento.

**Riscos**
- `producao.js` também está sendo mexido pela frente COM (tarefa #33). Na integração pode haver conflito em `prEstTxt`/`prLoteTxt` e `prResultado`.
- `cenario.js` e `processo_os.py` são compartilhados com as frentes do Controle e da O.S.
- Continuam vermelhos e não são desta frente: `consumo_divergente` (Estoque etapa 4) e `os_cenario` (PEND-OS-01).

## revisao

# Revisão adversarial da frente DOM (B-R8 e COLH-C01): HEAD 7f26b3b, branch claude/v44-dom

Resultado: as duas correções funcionam no caminho principal. Achei 1 caso S2 e 4 S3 na B-R8. Na COLH-C01 só sobram detalhes S4. Não houve S1.

Trabalhei numa cópia do HEAD e numa da base ecc8b00, no scratchpad. Não alterei nada em `<sp-dom>`: o git status segue limpo no 7f26b3b.

## Achados

### 1. S2 · Produto fora da requisição aplicado com 0 não abre a divergência (o mesmo fato com 0 digitado abre)
- **Reprodução (executada no node, `domrev_tools/p2.js` e `p3.js`):**
  - Ordem OS-0421, que é a ordem de demonstração do app. O app fecha um turno de 10 ha como o MB-03 faz quando o operador não mexe no campo do Adjuvante: Adjuvante 0 L, gravado como sugestão.
  - O planejado era 2,5 L. Sai "Turno fechado: 10 ha em 1 h. A ordem continua em execução.", sem divergência e sem selo.
  - Na web, na OS-0420, a Semente informada com 0 abre a divergência. O MAP 11-52 com 0 kg, contra 2.500 kg planejados, não abre nada.
  - Resultado: a ordem chega a "Conferir e encerrar" com 100 % de subdose sem revisão do agrônomo. É o dano que a B-R8 deveria evitar.
- **Causa:**
  - Em `cenario.js:335` (cenApontar), quando o produto não está na requisição, o consumo vira 0 sem marcar `inf`.
  - O app em `areas/mobile.py:540` e a web em `areas/processo_os.py:438` mandam esse 0 em `est`. O comentário do app chama esse valor de "0 explícito".
  - Em `cenario.js:267`, `cenApDiv` ignora tudo que não tem `inf`.
- **Correção proposta:** em cenApontar, quando o produto não está na requisição, gravar o 0 forçado como fato (`inf[x.p]=true`). A outra opção é `cenApDiv` comparar também os produtos fora da requisição. A baixa não muda, porque 0 não gera conferência.
- **Teste a acrescentar:** turno da OS-0421 com o campo do Adjuvante sem edição. Esperado: selo "Divergência de consumo/dose · Adjuvante espalhante" e planejado 2,5 L contra informado 0 L.

### 2. S3 · Precisão diferente da regra declarada: "planejado 10 L × informado 10 L" bloqueia o encerramento
- **Reprodução (executada, `p4.js` e `p5.js`):**
  - Informado 9,995 L contra 10 L planejados. A mensagem e o selo dizem "2,4-D 806 planejado 10 L × informado 10 L", e o encerramento fica bloqueado.
  - Informado 9,996 L não é sinalizado.
  - Pela regra de quantidade, `cenQtd(9.995,1)` dá 10,00, ou seja, igual ao planejado. O inverso também acontece: 10,005 vira 10,01.
- **Causa:** `cenario.js:266` arredonda com float (`Math.round(x*100)`), não com o decimal meio-para-cima de `cenQtd`. Além disso, `cenDivTxt` (linha 271) mostra só 2 casas.
  - O PLANO G3 e o commit afirmam "centésimo da unidade (cenQtd)", o que não confere com o código.
- **Correção proposta:** `const c2 = x => Math.round(cenQtd(x, 1) * 100)` e mostrar o informado com as casas usadas na comparação.
- **Teste a acrescentar:** D04 com 9,995 L e 10,005 L.

### 3. S3 · Início (IN-04) mostra "Sobras a receber" com custódia zero
- **Reprodução (executada, `domrev_tools/mapa_probe.py`):**
  - Roda a própria função `mapOrdsCen` extraída do `project/IN-04.dc.html` gerado.
  - Cenário: OS-0430 em conferência, sobras devolvidas, custódia 0/0/0, divergência aberta.
  - Selos que aparecem: `["Divergência de consumo/dose · 2,4-D 806","red"], ["Sobras a receber","yellow"]`.
- **Causa:** em `areas/inicio.py:642`, qualquer bloqueio que não seja carga ou sinal vira "Sobras a receber". O padrão já existia para duplicidade e consumo em conferência; a B-R8 acrescenta mais um caso.
- **Correção proposta:** só pôr "Sobras a receber" quando o bloqueio começa com "Sobra em custódia". O selo da divergência já vem de `co.selos`.

### 4. S3 · Depois que o almoxarifado recusa o relato, a divergência fica com um valor que o estoque declarou inexistente
- **Reprodução (executada, `p6.js`):**
  - Turno de 150 ha conforme. Em seguida, 10 ha com 2,4-D 15 L e custódia de 10 L: abre a conferência CC-301 e a divergência "planejado 10 × informado 15".
  - Rui recusa: "digitação errada: usou 10 L".
  - Depois disso, a baixa do dia 2 é 0 L, mas a divergência continua "informado 15 L".
  - O agrônomo revisa uma superdose quando o estoque registra subdose. O dia fica com dois fatos contraditórios.
- **Causa:** `cenConciliar` (`cenario.js:424`) não toca em `ap.div`.
- **Correção proposta:** ao recusar ou aceitar, recalcular `ap.div` do dia com o consumo decidido, ou anotar na divergência "relato recusado no Estoque (baixado 0 L)".

### 5. S3 · "Registrar correção" promete "a reaplicação sai em nova ordem", mas nada fica pendente
- **Situação (executada, D06):** a correção é gravada e o selo sai. A O.S. encerra sem nenhuma ordem de reaplicação nem pendência visível.
- **Dano:** a reaplicação decidida pelo agrônomo pode ser esquecida.
- **Causa:** `cenario.js:291`.
- **Correção proposta:** um link "Emitir O.S. de reaplicação" já preenchido, ou uma pendência do agrônomo até essa ordem existir. Pode ir para a próxima fatia, com registro.

### 6. S4 · Linha guardada como duplicidade mostra divergência e "A revisão técnica abre quando o apontamento somar."
- **Reprodução (executada no Chrome, `domrev_tools/nav_probe.py`, captura `domrev/.../_probe/rev_dup_guardado_div.png`):** Paula decide "mesmo turno". O dia 2 fica "Duplicidade · não somado" e continua com o texto vermelho da divergência e essa frase, embora esse apontamento nunca vá somar.
- **Causa:** `areas/processo_os.py:874`.
- **Correção proposta:** não mostrar `div` e `divQ` quando a linha está guardada como duplicidade. O recibo do app já faz isso pelo `!desc` (`mobile.py:501`). O recibo do app também mostra "revisão técnica de Ana" num turno retido como duplicidade a decidir.

### 7. S4 · COLH-C01: cartões do celular e ordenação
- **Cartão do grupo no celular** (`areas/producao.py:584`): com o café todo a apurar, `prPonderada` dá null (confirmado em C01e) e o cartão mostra "1 talhões", sem "a apurar". No desktop aparece "sc/ha a apurar · N talhões fora da conta".
- **Ordenação** (`areas/producao.py:500`): `v.colh` fica null também no caso misto ("50 sc + 8.000 L"), então o talhão é ordenado como vazio.

### 8. S4 · Produto fora da ordem divergente sai sem unidade
`cenario.js:269` grava `un: ''`, e o texto fica "planejado 0 × informado 5". Pela interface esse caso não é alcançável e não há teste para ele (mutante B7 sobreviveu).

## Mutantes nos testes novos (executado, `domrev_tools/mut.py`)

**`dose_divergente_unit.js`:** os testes pegaram 9 de 14 mutantes. Os 5 que sobreviveram:

| Mutante | O que foi alterado | Leitura |
|---|---|---|
| B6 | Decidir duplicidade sem recalcular a divergência | O comportamento está correto (provei em `p4.js` P2), mas não há teste |
| B7 | Produto fora da ordem | Sem teste |
| B11 | Planejado sem descontar a área no aparelho | Sem teste |
| B12 | Dono "Ana" na fase Em execução | Coberto só no teste de navegador |
| B14 | Sugestão também compara | Praticamente equivalente ao original |

**`cafe_apurar_unit.js`:** os testes pegaram 4 de 9 mutantes. Os 5 que sobreviveram:
- C2, C3 e C7 não são alcançáveis, porque o café não é semanal e não tem previsão por semana.
- C8 (cartão do celular) e C9 (ordenação do grupo) não têm teste.
- C01l já passava na base: é proteção contra regressão, não prova da correção.

Os vermelhos na base ecc8b00 se confirmam (executado): dose 4/22 e café 1/14.

## O que tentei e não quebrou (executado)
- Harness do Codex (D01 e D02).
- Recusa ao Rui, motivo vazio e texto de correção vazio.
- Repetição sem efeito e conflito de decisão.
- Sem sinal com envio duplo: o selo aparece uma vez.
- Duplicidade retida só abre a revisão depois de somar.
- O usado informado na conferência vira divergência (P2).
- Encerramento bloqueado no núcleo, no `osMerge`/Kanban e no Estoque (o Estoque mostra "Bloqueado" com o motivo).
- Origem com quem decidiu e quando.
- Não há caminho de encerramento que pule `cenPodeEncerrar`; cancelar só é possível sem realizado.
- Kanban continua com 5 fases; a revisão usa botões secundários.
- COLH-C01: com e sem área, transição para rendimento medido, zero medido, caso misto e lote "Café da roça" em L (na base aparecia "200 sc", fato que o relato não registrou).
- A reserva aceita só lote apto, e o café da roça nunca é apto.
- A grade de safra só lista grão, então o café não aparece como "0 sc" na oferta.
- Também passaram na cópia: `producao_unit` 121/121, `inicio_entrega` 26/26, `ap_unico unit` 80/80, `aprova_quem_decide` 102/102 e `quantidade` 14/14. O build deu 0 FALHA, com 140 páginas.
- O `consumo_divergente` dá 20/21 também na base (`/tmp/DOM-cd-base.log`). É a mesma falha da Estoque etapa 4 e não tem relação com a B-R8.

Arquivos de prova, todos em `<scratchpad>/`:
- `domrev_tools/` (runjs.py, p2–p6.js, mapa_probe.py, nav_probe.py, nav_probe.log, mut.py)
- `domrev/` (cópia do HEAD)
- `domrev_base/` (cópia da base)

## correcao

Fiz as correções de todos os achados S2 e S3 e de todos os S4 da revisão, cada uma com teste de regressão. A única parte adiada é a emissão automática da ordem de reaplicação (achado 5). Os vermelhos que ainda existem são os mesmos da base.

**Commit:** `1fd8cfa` "DOM: correções da revisão", na branch `claude/v44-dom` (worktree `<sp-dom>`). Não fiz push.

**O que mudou:**
- **Achado 1 (S2):** um produto da ordem que não está na requisição e foi aplicado com 0 agora abre a divergência. Vale para o Adjuvante da OS-0421 e o MAP 11-52 da OS-0420, no app e na web. A baixa do estoque não muda.
- **Achado 2 (S3):** a comparação usa a regra decimal de `cenQtd`, então 9,995 L conta como 10 L e não diverge. O texto mostra as mesmas casas usadas na conta.
- **Achado 3 (S3):** o Início (IN-04) só mostra "Sobras a receber" quando há sobra em custódia de fato.
- **Achado 4 (S3):** quando o almoxarifado recusa o relato, a divergência do dia passa a "planejado × baixado 0 L (informado X L, relato recusado)". Uma revisão já feita sobre o valor recusado é reaberta, e a anterior fica no histórico e na Origem da O.S.
- **Achado 5 (S3), resolvido em parte:** a mensagem não promete mais "a reaplicação sai em nova ordem". A emissão da O.S. de reaplicação ficou registrada no `docs/controle-01/PLANO.md` como próxima fatia. Motivo, conferido no código: o formulário Nova ordem recusa uma segunda ordem da mesma atividade no mesmo cultivo (`areas/processo_os.py:17` e `:898`), e a especificação do Codex proíbe forçar a reaplicação.
- **Achados 6, 7 e 8 (S4):**
  - Uma linha guardada como duplicidade não mostra mais divergência. O recibo do app diz que a revisão só abre se quem confere somar o turno.
  - O cartão do grupo a 390 px mostra "sc/ha a apurar · 1 talhão", e o talhão misto é ordenado pelo que foi medido.
  - O produto fora da ordem sai com unidade.
- **Mutantes que sobreviveram:** B6, B11 e B12 ganharam teste (D14, D15 e D16).
- **Testes antigos com expectativa nova:** D06 mudou porque a mensagem deixou de prometer a reaplicação. D15 lê o campo novo `ap.ant`, por isso falha no 7f26b3b mesmo com o cálculo antigo certo. Os motivos estão no commit.

**Testes (todos executados):**
- **Vermelho no 7f26b3b:** com os testes novos sobre uma cópia do HEAD, dose dá 25/35, Início 1/2 e café 14/16.
- **Sem navegador:**
  - `python3 build.py` → 0 FALHA, 140 páginas; `montar_render.py` → 140 páginas.
  - `dose_divergente_test.py unit` → 35/35 e Início 2/2; `cafe_apurar_test.py unit` → 16/16.
  - `producao_unit` 121/121, `ap_unico unit` 80/80, `aprova_quem_decide` 102/102, `inicio_entrega` 26/26, `quantidade` 14/14.
  - `os_aprov_lib` 45/45, `carencia unit` 50/50, `legal` 35/35, `mip` 34/34, `assinatura` 76/76.
- **Navegador, rodados agora** (`flock /tmp/cdpB.lock`, logs em `/tmp/DOM-bat2/`): `est_cenario` 15/15, `esttest 2` 23/23, `esttest 4` 13/13, `map_decisoes` 18/18, `map_irrig_filtro` 15/15, `producao_fluxo revisao` 18/18, `os_ator` 15/15.
- **Navegador, rodados antes da pausa sobre o mesmo código-fonte** (logs `/tmp/DOM-dose-nav.log`, `/tmp/DOM-cafe-nav.log`, `/tmp/DOM-varredura.log` e `/tmp/DOM-bateria/`; nenhum arquivo de produto mudou depois do build das 16:58):
  - `dose_divergente nav` 19/19, `cafe_apurar nav` 10/10, `varredura` 140/140, `acoes_duplicadas` 0 páginas com ação repetida.
  - Todos os testes `app_*` e `mbtest` verdes, `ap_unico nav` 23/23, `os_v39_bloq` 12/12.
- **Vermelhos iguais à base:** `os_cenario` 20/21 (PEND-OS-01) e `consumo_divergente` 20/21 (Estoque etapa 4). Não têm relação com a B-R8.

**Recusados, com motivo:**
- **B14:** é praticamente equivalente ao código original.
- **C2, C3 e C7:** não são alcançáveis, porque o café não é cultura semanal nem tem previsão por semana.

**Riscos que continuam:**
- Nada obriga a emitir a O.S. de reaplicação depois de uma "Correção decidida", então ela pode ser esquecida. Fica para a próxima fatia.
- A partir de agora, a OS-0420 e a OS-0421 abrem a divergência por padrão quando o turno é apontado sem editar o produto que não está na requisição. Isso é intencional, e os testes que usam essas ordens continuam verdes.

**O que o proprietário pode conferir:** no app (MB-03 → Iniciar turno na OS-0421), fechar um turno de 10 ha sem mexer no campo do Adjuvante. O recibo mostra "Adjuvante espalhante planejado 2,5 L × informado 0 L · revisão técnica de Ana". Depois, em O.S. → OS-0421, aparece o selo "Divergência de consumo/dose" e o encerramento só é liberado depois da revisão de Ana.