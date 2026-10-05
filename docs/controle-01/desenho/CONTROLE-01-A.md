# CONTROLE-01-A · AP-UNICO · Apontamento único web × app: o mesmo turno conta uma vez, quem confere escolhe qual relato vale, e a web aceita o usado real

Severidade: S2

Dano: Hoje, o mesmo turno apontado na web e no app, ou duas vezes na web, soma duas vezes e não dá aviso. Executado na base 884620c e refeito pelo cético, com os mesmos números: a OS-0421 vai de 190 para 290 ha, quando deveria ir para 240, e o Fungicida A consumido vai de 95 para 145 L, quando deveria ir para 120. A ordem mostra saldo de 60 ha quando há 110 ha sem fungicida, e pode ir para conferência com área sem aplicação. Além disso, 25 L saem da custódia de Marcos sem uso físico: é uma sobra que ninguém cobra, e o estoque e o custo ficam errados. Pelo PRD 22.1 (l.5189), "duplicidade de obrigação/movimento" é S2. A proposta original corrige a soma, mas cria quatro defeitos novos, todos executados: um item fantasma no Estoque, um lote de colheita fantasma, a pendência com o dono errado na conferência e um turno do app que se perde enquanto a tela diz "Turno fechado". Além disso, só deixa valer o relato que chegou primeiro, o que contraria o DEMO-11.

PRD: PRD v3.9:
- 8.5: l.3017 (cada apontamento tem ID, data operacional, consumo, origem e estado) e l.3025 ("Reenvio não soma novamente; duplicidade de área, sobreposição de equipes e apontamentos conflitantes geram conferência");
- OSDIA-03 (l.3033), OSDIA-04 (l.3034), OSDIA-06 (l.3036) e OSFASE-09 (l.3004);
- DEMO-11 (l.4751): "capturar o mesmo fato com UUID diferente abre reconciliação por sobreposição, preservando ambos os relatos e sem somá-los"; "Relógio errado não define vencedor";
- CMD-09, Conferir apontamento (l.2780), e CMD-10, Encerrar (l.2781);
- RN-018 (l.220) e RN-020 (l.221: "Correção de fato usa ajuste/estorno vinculado");
- ENG-021 (l.5285): chave de idempotência; "mesma chave com payload diferente é conflito";
- 22.1 (l.5189): S2;
- 4.3 (l.285): uma ação primária;
- 2.1 (l.195): revisão posterior quando a pessoa acumula papéis;
- SINT-C03: regra única de quantidade (`cenario.js:26-41`).

AGENTS.md §3.3 e §4: herdar o contexto de forma visível; servidor como autoridade; chave de quem inicia a ação; fórmula única (ENG-011); trava só com o dano nomeado.

Arquivos: tools/prototipo/v37/gen37/cenario.js, tools/prototipo/v37/gen37/areas/processo_os.py, tools/prototipo/v37/gen37/areas/inicio.py, tools/prototipo/v37/gen37/areas/mobile.py, tools/prototipo/v37/gen37/dados_carencia.py, tools/prototipo/v37/gen37/quantidade_test.py, tools/prototipo/v37/gen37/ostela.py, tools/prototipo/v37/gen37/ap_unico_test.py (novo), tools/prototipo/v37/gen37/ap_unico_unit.js (novo), scratchpad/ctl/cetA/corrigida_cenario.js, scratchpad/ctl/cetA/corrigida_nucleo.js, scratchpad/ctl/cetA/mk.py, scratchpad/ctl/cetA/cetico.py, scratchpad/ctl/cetA/t1.js, scratchpad/ctl/cetA/t3.js, scratchpad/ctl/cetA/t4.js, scratchpad/ctl/cetA/t5.js, scratchpad/ctl/cetA/textos_c.js, scratchpad/ctl/cetA/run2.py, scratchpad/ctl/cetA/car2.py, scratchpad/ctl/cetA/roda_q.py, scratchpad/ctl/cetA/res.py, scratchpad/ctl/cetA/seed.js, scratchpad/ctl/proposta_cenario.js, scratchpad/ctl/proposta_nucleo.js, scratchpad/ctl/ap_unico_unit.js, scratchpad/ctl/vermelho_verde.js, scratchpad/ctl/sim_navegador.js, scratchpad/ctl/repro.js, scratchpad/ctl/textos.js, scratchpad/ctl/quantidade_test_ajustado.py, scratchpad/ctl/monta.py, scratchpad/ctl/run_unit.py

# AP-ÚNICO: apontamento único web × app (Frente A da CONTROLE-01), versão corrigida pelo cético

**Situação.** O desenho está especificado. O núcleo foi executado sem editar o repositório, em código de sobreposição carregado depois do original:
- a proposta está em `ctl/`;
- as correções do cético estão em `ctl/cetA/`, nos arquivos `corrigida_cenario.js` (152 linhas) e `corrigida_nucleo.js` (24 linhas). As mudanças em `osMerge` e em `dados_carencia` estão como substituição de texto em `ctl/cetA/mk.py`.

Não rodei navegador. Em `sp-tab5`, `git status` mostra zero arquivos versionados alterados.

**Base.** `sp-tab5` no commit 884620c, branch `claude/v44-tabelas-05`.

## 0. Acordo curto

```text
ID / resultado útil / persona: CONTROLE-01-A · AP-ÚNICO · o mesmo turno apontado na web e no app conta uma vez; quem confere escolhe qual relato vale; a web aceita o usado real · Marcos (operador, app), escritório (O.S. web), Paula (conferência)
Requisitos do PRD e fora do escopo: 8.5 l.3017–3036 (OSDIA-03/04/06), DEMO-11 l.4751, CMD-09/10 l.2780–2781, RN-018 l.220, RN-020 l.221, ENG-021 l.5285, 22.1 l.5189. Fora: talhão/parcela e operador editáveis na tela, consumo no formulário do Mapa, quem concilia consumo acima da custódia (padrão adotado 2, outra frente), excesso tardio sobre o saldo (PER-12, v3.10)
Autor / revisor / integrador: Claude / Codex / Codex
Base (commit ou hashes) / arquivos sob responsabilidade: 884620c · cenario.js, areas/processo_os.py, areas/inicio.py, areas/mobile.py, dados_carencia.py, quantidade_test.py, ostela.py, novos ap_unico_test.py + ap_unico_unit.js
Aceite e comando de verificação: ap_unico_unit (31 + 13 do cético) · quantidade_test.py (14/14 com o ajuste) · carencia_test.py unit (48/48) · ap_unico_test.py nav · ostela.py · consumo_divergente_test.py · app_mb03_turno_test.py · os_cenario_test.py · tabelas_est_test.py
Estado / impedimento / próximo passo: especificado, núcleo executado em sobreposição · sem impedimento · revisão do Codex, depois implementar
```

**Decisões técnicas** (delegadas aos agentes; o proprietário pode mudar):
- **A duplicata provável fica retida em conferência, sem aviso confirmável.** Essa decisão vem da proposta e continua. As razões:
  - o PRD diz que a duplicidade "gera conferência" e que não se soma (l.3025; DEMO-11);
  - sem sinal, não há a quem perguntar;
  - vale uma regra só para os dois canais.
- **Quem decide é Paula (conferência).** Fontes:
  - `configuracoes.py:8` ("Paula = conferência");
  - `processo_os.py:150`, onde o dono da OS-0421 é Paula, para "conferir o dia 4 hoje";
  - `campo.py:52`;
  - CMD-09.
- **A decisão tem três saídas, e não duas (cético).**
  - As saídas: "Mesmo turno: vale o dia N", "Mesmo turno: vale este" e "Outro turno: somar".
  - Motivo: o DEMO-11 diz que "relógio errado não define vencedor". A proposta só deixava valer o relato que chegou primeiro.
  - Executado: a web aponta com a estimativa de 25 L e o app informa o usado real, 27 L. Com "mesmo turno", a ordem ficava em 120 L consumidos, sem caminho para os 122 L reais.
  - "Vale este" estorna o relato já somado com vínculo (RN-020) e o guarda.
- **A web herda o operador (cético).** Herda quem está com o material na requisição ou, se ninguém, o responsável da ordem, e mostra esse nome no formulário. A web nunca grava "web" como pessoa.
- **Aviso no formulário (cético).** Antes de salvar, o formulário mostra o mesmo critério do servidor, como aviso. Não é trava nem pede clique.

Nenhum dos três padrões adotados de 05/10 muda esta frente. O consumo acima da custódia continua indo para `CEN_CONC_RESP`; quando a frente de consumo e ajuste mudar o responsável para o gestor (padrão 2), os textos daqui acompanham.

## 1. Problema reproduzido (executado)

Comando: `python3 ctl/monta.py repro.js`, refeito pelo cético. Saída na base 884620c:

```text
R0 seed OS-0421 Em execução T1+T2 realizado 190 / 350 saldo 160 · Fungicida A cons 95 cust 65
A1 web: Apontamento do dia 5: 50 ha (provisório) · usado: Fungicida A 25 L, Adjuvante espalhante 12,5 L. Saldo 110 ha; ...
A2 app: Turno fechado: 50 ha em 8 h. A ordem continua em execução.
A3 fim realizado 290 saldo 60 · Fungicida A cons 145 cust 15
B  web 2x mesmo dia: 290 ha · Fungicida A cons 145 cust 15
C2 app consumo real 27 L: ... Fungicida A cons 122 cust 38      (a web não tem como informar o real)
D  data do app = 05/10 (new Date(), hoje real)
E  offline+web: 290 ha · Fungicida A cons 145 cust 15
```

**Causas:**
- A web soma sem olhar o que já existe: `osc_apontar` (`areas/processo_os.py:358-367`) só checa o saldo, e o consumo é sempre dose × área (l.361).
- O app faz o mesmo: `cenFecharTurno` (`cenario.js:158-193`) só checa o saldo (l.161-163).
- Nenhum dos dois tem chave de idempotência.
- As datas não batem:
  - o app grava a data do relógio do aparelho (`cenario.js:177`);
  - a web usa 26/09 (`processo_os.py:550`);
  - o Mapa usa 23/09 (`inicio.py:828`).

## 2. Regra nova (numerada e testável)

| ID | Regra | Dano que evita | Fonte | Testes |
|---|---|---|---|---|
| AP-01 | Web (O.S. e Mapa) e app apontam só por `cenApontar(c,k)`, com `k = {os, d (dd/mm), parc (vazio = a ordem toda), ha, h, cons, est, origem, quem, chave}`. Na web, `quem` é herdado: quem está com o material na requisição ou, se ninguém, `o.resp`. O nome aparece no formulário. | O mesmo fato com regras diferentes por canal. O caso de conferência dizendo "custódia de web". | 8.5 l.3017; OSDIA-06; AGENTS §3.3 | W1, W4, N2, C2 |
| AP-02 | A data do turno do app é a data operacional do início do turno, e não o relógio. No protótipo é `CEN_DIA_OP = 2026-09-26`, a mesma da O.S. e do Mapa. | Um mesmo dia gravado como 26/09 e como 05/10 escapa da checagem. | 8.5 l.3017 | F1, V6 |
| AP-03 | Mesma chave e mesmos dados é o mesmo apontamento: nada é somado. Mesma chave com dados diferentes (área ou data) é conflito, e nada é gravado. A chave vem de quem inicia: na web, ao abrir o formulário; no app, ao iniciar o turno (`TU-<os>-<n>`). A chave reserva, para estado salvo sem chave, é `TU-`/`W-<os>-dia<n>`, que não colide com a do turno. | Duplo clique soma duas vezes. Dois fatos sob uma chave perdem um deles. Um turno sumido enquanto a tela diz "Turno fechado" (executado: 5 turnos fechados, 40 ha somados). | OSDIA-03; ENG-021 l.5285 | N4, P4b, C5, C9 |
| AP-04 | **Consumo:** o valor informado é o fato. Sem valor informado, vale dose × área do trecho (`cenQtdTrecho`, SINT-C03), só para o que está na requisição; fora dela, 0. Estimativa acima da custódia é recusada, com pedido do usado. Valor informado acima da custódia vai para conferência com o almoxarife, sem baixa. É a regra que o app já usa (`cenario.js:139-142, 166-176`), agora também na web. | Custódia baixada sem uso físico, ou consumo inventado (12,5 L de adjuvante nunca entregue). | RN-018 l.220; 8.5 l.3027 | W1–W3, R2 |
| AP-05 | **Duplicata provável** atende a todas as condições:<br>• mesma O.S. e mesma data;<br>• talhão sobreposto (igual, ou um dos dois vazio);<br>• o outro já está no servidor, com sinal;<br>• chave diferente.<br>**Não é duplicata:** turnos do mesmo operador no app. O formulário web mostra o mesmo critério como aviso antes de salvar (`osApDupAviso`, sem clique). | Soma duplicada por canais diferentes ou por repetição. Falso positivo por data padrão não conferida. | OSDIA-04; 8.5 l.3025; DEMO-11 | P1–P4, N1–N3, C10 |
| AP-06 | **A trava é no efeito, e não no fato.** A duplicata fica "Duplicidade a conferir":<br>• não soma área nem baixa consumo;<br>• a ordem ganha o selo "Apontamento em conferência", com dono Paula, em Em execução e também em Em conferência;<br>• o previsto não é consumido;<br>• se veio da fila sem sinal, a baixa do aparelho é desfeita no envio, o caso de consumo vai para "Aguarda duplicidade" e o movimento fica com `det` vazio e o motivo em `obs`. O Estoque lê `det` como itens (`processo_estoque.py:235-238`). | Área e consumo dobrados. Item fantasma "retido · duplicidade com o dia 6 = 6" no Estoque. Pendência com Rui ("receber a devolução") em vez de Paula. | AGENTS §4; OSFASE-09 | P1, P4, C1, C3, C7, C8 |
| AP-07 | **Decisão (CMD-09), um clique, três saídas:**<br>• **"Mesmo turno: vale o dia N":** este relato fica "Duplicidade · não somado", com o histórico guardado;<br>• **"Mesmo turno: vale este":** só contra um único relato já somado. Estorna esse relato (área, baixa e caso aberto), guarda-o como duplicidade e soma este uma vez;<br>• **"Outro turno: somar":** soma e baixa uma vez, e é recusado acima do saldo.<br>Ao somar, a estimativa é recalculada no acumulado do momento (SINT-C03). | Decisão sem trilha. O relógio decidindo o vencedor. Soma acima da área. Desvio de 0,01 na regra única (executado: 50,00 L contra 49,99 L). | CMD-09; DEMO-11; RN-020; SINT-C03 | D1–D4, C6, C11 |
| AP-08 | O retido não conta no realizado. "Enviar para conferência" depende do saldo real, e "Encerrar" é recusado enquanto houver retido. | Concluir por soma duplicada. | OSDIA-04; CMD-10 | N5, P1c, C1 |
| AP-09 | O fato decidido como duplicidade ("Duplicidade · não somado") não vira lote de colheita, aplicação, colheita em carência nem custo. O retido, ainda sem decisão, continua contando, o que é conservador. | Lote fantasma (executado: LC-0505-4 com 10 ha). Custo dobrado. | RN-018; DEMO-11 | C4 |

## 3. Mudança de código por arquivo

### 3.1 `cenario.js`

A proposta continua (`ctl/proposta_cenario.js`), com as correções de `ctl/cetA/corrigida_cenario.js`.

**Itens novos**, depois de `CEN_CONC_RESP` (l.142):
- constantes: `CEN_DIA_OP='2026-09-26'`, `CEN_AP_DUP='Duplicidade a conferir'`, `CEN_AP_DESC='Duplicidade · não somado'`, `CEN_CC_AGUARDA='Aguarda duplicidade'` e `CEN_CONF_AP='Paula (conferência)'`;
- funções: `cenDdMm`, `cenApSomado`, `cenApDup`, `cenApDupTxt`, `cenSeloAp`, `cenApBaixa` (o bloco que estava em `cenFecharTurno` l.169-191), `cenApEntra`, `cenApontar` e `cenApDecidir`.

**Correções do cético:**
- `cenApontar`:
  - chave repetida com área ou data diferente: `throw 'Este registro (W-1) já foi gravado como dia 5 com 50 ha em 26/09: conflito, nada gravado.'`;
  - `quem = k.quem || dono da custódia || o.resp`;
  - chave reserva `…-dia<n>`;
  - `reter = ap.sinc && cenApDup(o,ap).length>0`, e o previsto só sai quando não retém.
- `cenApEntra`, no caso já baixado no aparelho: `mv.det=''; mv.obs='Retido: mesma data do dia N; nada baixado até a decisão de Paula (conferência).'`.
- `cenApDecidir(c,id,dia,modo,quem)`, com `modo` `'anterior' | 'este' | 'somar'`; `true`/`false` continuam aceitos como "somar" e "anterior":

```js
if (modo === 'este') { const K = o.ap.find(a => a.dia === ap.dupDe[0]);
  if (ap.dupDe.length !== 1 || !K || !cenApSomado(K)) throw new Error('"Vale este" só contra um apontamento já somado: decida antes o dia ' + de + '.');
  if (r) r.itens.forEach(it => { const q = (K.cons || {})[it.prod] || 0; it.consumido -= q; it.custodia += q; });   // estorno vinculado (RN-020)
  /* casos abertos do dia K → Recusado; o.realizado -= K.ha; o.saldo += K.ha; K fica CEN_AP_DESC com det '' e obs */ }
/* somar e este: */ (o.ins||[]).forEach(x => { if (x.p in ap.cons && !ap.inf[x.p] && naRequisicao(x.p)) ap.cons[x.p] = cenQtdTrecho(x.dose, o.realizado + pend, ap.ha); });
```

- `cenFecharTurno`, se o apontamento for repetido: "Turno já registrado como dia N (X ha): nada foi somado de novo."

**Funções alteradas, como na proposta:**
- `cenIniciarTurno` (l.128-135): passa a guardar `d` e `chave` no turno;
- `cenFecharTurno` (l.158-193): vira um invólucro de `cenApontar(origem:'app')`;
- `cenSinal` (l.233-241): passa cada apontamento por `cenApEntra(...,true)`;
- `cenPodeEncerrar` (l.243): ganha a checagem do retido.

`CEN0.v` não sobe.

### 3.2 `areas/processo_os.py`

**`JS_NUCLEO`:**
- `osc_apontar(c,id,d,ha,cons,est,chave)` é um invólucro de `cenApontar(origem:'web')`, como na proposta.
- `osc_apDecidir(c,id,dia,modo)` repassa a decisão.
- Funções do formulário: `osApIns` e `osApColeta`.
- **Nova (cético):** `osApDupAviso(c,o,d)`:

```js
function osApDupAviso(c,o,d){ const co=c.ordens[o.id]; if(!co||!/^\d\d\/\d\d$/.test(d||'')) return '';
  const l=cenApDup(co,{d,parc:null,chave:'?',origem:'web'}); return l.length?'Já há '+cenApDupTxt(l)+' em '+d+'. Se for outro turno, salve: ele fica em conferência com '+CEN_CONF_AP+' e só soma depois da decisão.':''; }
```

- **`osMerge`:**
  - Em execução (l.237-238): com retido e `!mine`, `o.dono=CEN_CONF_AP` e `o.prazo='decidir se o dia N é outro turno'`, como na proposta;
  - Em conferência (l.242): `t` passa a 'Apontamento em conferência' quando `encM` fala em duplicidade;
  - **l.244 (cético):** acrescentar `else if(/duplicidade/.test(o.encM)){ o.dono=CEN_CONF_AP; o.prazo='decidir a duplicidade'; }` antes do ramo do almoxarife. Sem isso, a pendência aparece como "Rui (almoxarife) · receber a devolução" (executado).
- **`osEncBloq`** (l.287): `q: CEN_CONF_AP+' decide na linha do apontamento: mesmo turno conta uma vez; outro turno soma.'`

**`JS`:**
- `STCOR` (l.425): `[CEN_AP_DUP]:'yellow', [CEN_AP_DESC]:'gray'`.
- `pan_go` (l.550): `d:CEN_DIA_OP, ced:{}, chave:'W-'+o.id+'-'+Date.now()`.
- Formulário, depois da l.621:
  - `v.pan_acons`, as linhas de consumo;
  - `v.pan_aquem`, uma linha de texto "Turno de Marcos · quem está com os insumos";
  - `v.pan_adup = osApDupAviso(cenGet(), o, cenDdMm(pa.d))`.
- `pan_asave` (l.628): `osApColeta`, depois `osc_apontar(..., col.cons, col.est, cur.chave)`.
- `pan_ap` (l.754-755):
  - o que não está somado não entra em `ac` e mostra "não somado";
  - a linha retida ganha `vant` (o rótulo "Mesmo turno: vale o dia N") e `somar`;
  - `este` só aparece quando `dupDe.length===1` e esse relato está somado;
  - o erro da decisão vai para `g2toast`.

**Modelo (HTML):**
- `aprow` (l.881-882): `<sc-if a.dup>` com o texto e até três botões `_MINI`. O primário do painel continua sendo "Registrar apontamento" (PRD 4.3).
- Formulário (l.958-962): linha do operador, aviso de duplicidade em `role=status` e `<sc-for pan_acons>` com `inputMode=decimal` e `aria-label` "Usado de X (un)".

### 3.3 `areas/inicio.py` (Mapa)

Como na proposta:
- l.828: `d:CEN_DIA_OP, chave:'W-'+o.id+'-'+Date.now()`;
- l.839: `osc_apontar(...,undefined,undefined,cur.chave)`;
- l.702, `ordCusto`: `if(!cenApSomado(a)) return;`.

### 3.4 `areas/mobile.py`

- **l.489**, como na proposta: o chip passa a "Em conferência · duplicidade" e `last_cons` diz que nada foi baixado.
- **l.490-491 (cético):** o caso em "Aguarda duplicidade" conta como aberto, com o texto "Aguarda a decisão da duplicidade · Fungicida A 70 L relatados, 65 L em custódia · Paula (conferência)". Sem isso, o cartão diz "Conferência resolvida" e "Aguarda duplicidade por undefined" (executado).
- Docstring, l.20-22: atualizar.

### 3.5 `dados_carencia.py` (cético)

Três linhas trocam `a.st==='Previsto'` por `(a.st==='Previsto'||a.st===CEN_AP_DESC)`:
- `carAplic`, l.255;
- `carLotes`, l.299;
- `carColhidoEmCarencia`, l.397.

O retido continua contando. Todas as telas que chamam essas funções carregam `cenario.js` (`colheita.py`, `inicio.py`, `mobile.py` e o núcleo da O.S.).

### 3.6 Arquivos sem mudança

`processo_estoque.py` fica como está, porque o movimento retido ou descartado passa a ter `det` vazio. Com o texto que a proposta gravava em `det`, `econsDet` gerava o item "retido · duplicidade com o dia" com quantidade 6 (executado).

## 4. Textos de tela (executados, `ctl/textos.js` e `ctl/cetA/textos_c.js`)

**Web e app:**
- **Web, apontamento retido:** "Apontamento do dia 6 (50 ha em 26/09) em conferência: já há dia 5, 50 ha pelo app (Marcos) nesta data. Nada foi somado nem baixado; Paula (conferência) decide se é outro turno."
- **App, turno retido:** "Turno fechado: 50 ha em 8 h, em conferência: já há dia 5, 50 ha pela web em 26/09. Nada foi somado nem baixado; Paula (conferência) decide se é outro turno."
- **Aviso no formulário** (só quando há outro relato na data): "Já há dia 5, 50 ha pela web em 26/09. Se for outro turno, salve: ele fica em conferência com Paula (conferência) e só soma depois da decisão."
- **Volta do sinal:** "1 registro enviado ao voltar o sinal. Em conferência de duplicidade: OS-0421 dia 5 (mesma data do dia 6, 50 ha pela web). Nada foi somado; Paula (conferência) decide."

**Painel da O.S.:**
- **Linha retida:** "Mesma data e talhão do dia 5. É outro turno? Quem decide: Paula (conferência)." Botões: **Mesmo turno: vale o dia 5**, **Mesmo turno: vale este** e **Outro turno: somar**.
- **Pendência:** "Pendência com Paula (conferência) · decidir se o dia 6 é outro turno". Em Em conferência: "· decidir a duplicidade".
- **Encerrar bloqueado:** "Apontamento em conferência de duplicidade: dia 6 (26/09, 50 ha). Paula (conferência) decide se é outro turno."

**Decisões:**
- "Dia 6 guardado como duplicidade do dia 5: nada foi somado nem baixado; o relato fica no histórico."
- "Dia 6 vale como o turno de 26/09: 50 ha · saldo 110 ha. O dia 5 foi estornado e fica guardado como duplicidade."
- "Dia 6 somado como outro turno: 50 ha · saldo 60 ha."
- "Somar 50 ha passa do saldo da ordem (0 ha): confira se é o mesmo turno do dia 5."

**Reenvio e conflito:**
- "Apontamento do dia 5 já registrado (50 ha): nada foi somado de novo."
- "Turno já registrado como dia N (X ha): nada foi somado de novo."
- "Este registro (W-1) já foi gravado como dia 5 com 50 ha em 26/09: conflito, nada gravado."

**Movimento no Estoque** (coluna Observação, item vazio):
- "Retido: mesma data do dia 6; nada baixado até a decisão de Paula (conferência)."
- "Mesmo turno do dia 5: guardado como duplicidade, nada baixado."
- "Estornado: mesmo turno do dia 6, que ficou valendo."
- "Somado como outro turno · Paula (conferência)."

**Formulário web:**
- "Usado de Fungicida A (L)" = "25" · "0,5 L/ha × área · em custódia 65 L";
- "Usado de Adjuvante espalhante (L)" = "" · "Fora da REQ-035 · nada em custódia";
- avisos: "Sugestão acima do que está em custódia (10 L): informe quanto foi usado." e "Acima da custódia (10 L): o consumo vai para conferência com Rui (almoxarife).";
- erro: "Consumo de Fungicida A (25 L) acima do que está em custódia (10 L). Informe quanto foi usado ou confira a entrega no Estoque."

## 5. Testes

### 5.1 Unitário da proposta (executado)

Arquivo `ctl/ap_unico_unit.js`, 31 casos.

| Comando | Proposta | Corrigida |
|---|---|---|
| `python3 ctl/cetA/run2.py ap_unico_unit.js <modo>` | 31/31 | 31/31 |
| `vermelho_verde.js` | 6/6 (base 0/6) | 6/6 |
| `sim_navegador.js` | 10/10 | 10/10 |

Os números esperados foram refeitos:
- **P1:** 190 + 50 = 240 ha; 95 + 25 = 120 L; 65 − 25 = 40 L.
- **D2:** 290 ha, saldo 60; 145 L consumidos e 15 L em custódia.
- **W1:** 95 + 27 = 122 L; 65 − 27 = 38 L.

### 5.2 Casos novos do cético (executados)

Comando: `python3 ctl/cetA/cetico.py`. Resultado: **proposta 0/11** (C10 e C11b não se aplicam a ela); **corrigida 13/13**.

| Caso | Contraexemplo e número |
|---|---|
| C1 | Web 50 ha, app 50 ha retido, web 110 ha em 27/09 e envio para conferência. Na proposta, o dono fica "Rui (almoxarife) · receber a devolução". Na corrigida, "Paula (conferência) · decidir a duplicidade". |
| C2 | Web informa 80 L com 65 L em custódia. A prévia do Rui dizia "65 L da custódia de web"; passa a dizer "custódia de Marcos". |
| C3 / C3b | Sem sinal + web. `econsDet` do movimento retido ou descartado dava `[{prod:'retido · duplicidade com o dia', qtd:6}]`; passa a dar `[]`. |
| C4 | Colheita OS-0505: web 10 ha e app 10 ha, e "mesmo turno". A proposta criava o lote LC-0505-4 com 10 ha "Descartado"; a corrigida não cria lote. |
| C5 | Mesma chave W-1 com 30 ha depois de 50 ha. A proposta dizia "já registrado"; a corrigida dá conflito e nada é gravado (ENG-021). |
| C6 | Dose 0,3333, "somar" depois de outro apontamento: 50,00 L contra 49,99 L da regra única. Corrigida: 49,99 L. |
| C7 | Sem sinal, 70 L informados com 65 L em custódia, + web. O cartão do app dizia "Conferência resolvida" e "por undefined"; passa a dizer "Consumo em conferência · Aguarda a decisão da duplicidade". |
| C8 | Web retida: os previstos iam de "25/09:50, 26/09:60" para "26/09:60"; agora ficam iguais. |
| C9 | Estado salvo com turno aberto sem chave, mais 5 turnos de 10 ha: a proposta somava 40 ha e mostrava "Turno fechado" 5 vezes; a corrigida soma 50 ha. |
| C10 | Aviso no formulário: aparece em 26/09 e some em 27/09. |
| C11 / C11b | Web estima 25 L e o app informa 27 L. A proposta, com "mesmo turno", ficava em 240 ha e 120 L / 40 L. A corrigida, com "vale este", fica em 240 ha e 122 L / 38 L, com o dia 5 estornado e guardado. "Vale este" contra dois relatos é recusado com a causa. |

### 5.3 Testes existentes sem navegador (executados, base / proposta / corrigida)

| Teste | Base | Proposta | Corrigida |
|---|---|---|---|
| `quantidade_test.py` original | 14/14 | 13/14 | 13/14 |
| `quantidade_test.py` ajustado (data por trecho) | 14/14 | 14/14 | 14/14 |
| `carencia_test.py` unit + app (`ctl/cetA/car2.py`) | 48/48 | 48/48 | 48/48 |

O item que falha no original é o 3, com a mesma data para três trechos (seção 6).

### 5.4 Navegador (especificado, não executado)

**Teste novo `ap_unico_test.py nav`** (Chrome, App(['MB-01','MB-03','OS','EST']), até 18 verificações). Os passos 1 a 4 e 6 a 10 são os da proposta, com estas mudanças:

1. **Formulário da OS-0421.** Data 2026-09-26. "Turno de Marcos". "Usado de Fungicida A (L)" = 25. Adjuvante vazio. Sem aviso de duplicidade.
2. **Usado 27 e duplo clique em Salvar.** Resultado: 240 ha, 122 L / 38 L e uma só chave.
3. **Turno do app duplicado.** MB-03 com 50 ha fica retido, com o cartão "Em conferência · duplicidade". Reabrir o formulário web mostra o aviso "Já há dia 5, 50 ha pela web em 26/09".
4. **Painel:**
   - selo "Apontamento em conferência" e "Pendência com Paula (conferência)";
   - linha "Dia 6 · app · não somado" com os três botões;
   - acumulado 240/350 (**negativo:** não 290).
5. **"Mesmo turno: vale o dia 5".** A linha fica "Duplicidade · não somado", o selo sai e o realizado continua em 240 ha.
6. **"Mesmo turno: vale este" (novo).** Restaurar. Web 50 ha (25 L) e app 50 ha com 27 L informados. Clicar "vale este". Resultado: 240 ha, 122 L; o dia 5 fica "Duplicidade · não somado". No EST, o movimento do dia 5 aparece sem item e com a observação "Estornado".
7. **Somar.** Web 40 ha e app 50 ha; "Outro turno: somar" dá 280 ha e 140 L.
8. **Sem sinal, depois web, depois "Com sinal".** Resultado: 240 ha e 120 L. No EST, o movimento retido não tem item fantasma.
9. **Retido até Em conferência (novo).** Pendência com Paula, e não com Rui.
10. **Negativo.** Dois turnos do app de 20 ha cada: 230 ha.
11. **Sem erros JS.**
12. **Cliques:** apontamento web com 2 cliques antes e depois; decisão com +1 clique, qualquer das três saídas; o aviso não pede clique.

## 6. Testes existentes que mudam de expectativa

São os mesmos dois da proposta, ambos executados:
1. **`quantidade_test.py:31`.** Trocar a data fixa `'24/09'` por `(24+out.n)+'/09'`. Resultado: 13/14 → 14/14.
2. **`ostela.py:95`.** Informar `setin('Data do turno','2026-09-27')` no segundo apontamento da OS-0430. Previsto em `sim_navegador.js`.

`tabelas_est_test` deve ser conferido no navegador, porque a web passa a gravar o movimento de consumo, com `quem` = Marcos.

## 7. Riscos de regressão

1. **Falso positivo.** Um segundo turno legítimo no mesmo dia e talhão, pela web, fica retido e custa 1 clique de Paula. Mitigação nesta frente: o aviso no formulário, antes de salvar, permite corrigir uma data padrão que não foi conferida. Mitigação no próximo passo: talhão/parcela e operador editáveis. Dois operadores do app na mesma ordem e data também ficam retidos (executado); no protótipo há um operador só.
2. **"Hoje" da demonstração.**
   - O apontamento passa a usar 26/09 nos três canais.
   - O Mapa diz "hoje" = 23/09 (`inicio.py:1398`), mas o formulário dele passa a propor 26/09: **a divergência cresce no Mapa**, que antes era coerente.
   - Ficar com 23/09 retém todo primeiro apontamento da OS-0421 contra o dia 4 da semente (executado). Por isso, 26/09 fica.
3. **Estoque.** A web passa a gravar o movimento de consumo, com Marcos como quem. O movimento retido, descartado ou estornado mostra o item vazio e o motivo em Observação.
4. **Altura.** O formulário da O.S. ganha uma linha por insumo, mais a linha do operador e o aviso. Conferir `verif_overflow` e HEIGHTS37.
5. **Quem decide.** O botão grava "Paula (conferência)" seja quem for que clique, porque o protótipo não tem papéis. No software, a decisão exige a permissão do CMD-09, e quem registrou não decide o próprio caso sem revisão posterior (PRD 2.1 l.195).
6. **"Vale este" depois de aceite do Rui.** Se o Rui já tiver aceitado o caso de consumo do relato anterior, o estorno não desfaz esse aceite. É raro: o caso só existe acima da custódia. O certo é decidir a duplicidade antes, e o selo leva a isso.
7. **Previstos.** A diferença de exibição entre canais é mantida de propósito.
8. **Resíduo de 0,01 (executado, recusado como correção).** Ocorre com app sem sinal, depois web na mesma data, com dose que arredonda: 53,34 L contra 53,33 L. O trecho da web contou o pendente que depois fica retido. No último turno, a estimativa passa da custódia em 0,01 e o campo pede o usado (trava existente). Não há perda.
9. **Excesso tardio sobre o saldo** (PER-12, v3.10): fora daqui.

## 8. Tamanho estimado

| Parte | Linhas |
|---|---|
| `cenario.js` | +93 líquidas (152 entram, 59 saem) |
| `processo_os.py` | cerca de +42 |
| `inicio.py` | 3 alteradas |
| `mobile.py` | 4 alteradas |
| `dados_carencia.py` | 3 alteradas |
| **Produção** | **cerca de 140 líquidas (cerca de 205 tocadas)** |
| Testes | `ap_unico_unit.js` com cerca de 110 linhas (31 + 13 casos); `ap_unico_test.py` com cerca de 85; 2 linhas em `quantidade_test.py` e `ostela.py` |

## 9. Fora do escopo (próximo passo)

1. Talhão/parcela e operador editáveis no formulário web e no MB-03, para reduzir o falso positivo do AP-05.
2. O formulário de consumo no Mapa: `osApIns`, `osApColeta` e `osApDupAviso` ficam no núcleo.
3. Quem aceita o consumo acima da custódia: padrão adotado (2).
4. O excesso tardio sobre o saldo (PER-12, v3.10).
5. "Corrigir com histórico" fora da duplicidade (PRD 8.5).

---

**Contestações: aceitas · recusadas (com motivo)**

**Aceitas** (aplicadas e executadas em `ctl/cetA/`):
1. **C1 · Dono errado em Em conferência.** `osMerge` l.244 punha "Rui (almoxarife) · receber a devolução" para um retido. Agora fica Paula.
2. **C2 · "Custódia de web".** O `quem` da web passou a ser herdado: quem está com o material ou o responsável da ordem, mostrado no formulário.
3. **C3 · Item fantasma no Estoque.** A proposta escrevia texto em `mov.det`, que `econsDet` (`processo_estoque.py:235-238`) lê como itens. Agora `det` fica vazio e o motivo vai para `obs`. A afirmação "`processo_estoque.py` sem mudança" só se mantém com essa correção.
4. **C4 · Lote de colheita fantasma.** `carLotes`, `carAplic` e `carColhidoEmCarencia` ignoram o decidido como duplicidade. A afirmação "dados_carencia conservador" estava incompleta: `carLotes` gera lotes.
5. **C5 · ENG-021.** Mesma chave com dados diferentes passa a ser conflito.
6. **C6 · Regra única (SINT-C03).** "Somar" recalcula a estimativa no acumulado do momento.
7. **C7 · Cartão do app.** "Conferência resolvida" e "por undefined" com o caso em "Aguarda duplicidade" foram corrigidos em `mobile.py` l.490-491.
8. **C8 · Previsto.** O retido não consome o previsto.
9. **C9 · Turno perdido.** A chave reserva colidia com `TU-<os>-<n>`, e o turno sumia com "Turno fechado". Agora a reserva é `…-dia<n>`, e o repetido tem mensagem própria.
10. **C10 · Aviso antes de salvar.** O formulário mostra o mesmo critério do servidor. É a única mitigação barata dos dois testes da equipe que caem no falso positivo (`ostela`, `quantidade_test`).
11. **C11 · Três saídas na decisão.** DEMO-11: "relógio errado não define vencedor". Sem "vale este", o usado real do app (27 L) não tinha caminho.
12. **Texto: "Descartado" virou "Duplicidade · não somado".** O DEMO-11 manda preservar os relatos, e o CF-03det já usa "guardado como duplicidade" e "contar uma vez" (`configuracoes.py:380, 408`).
13. **Citações corrigidas:**
    - `CEN_CONC_RESP` está na l.142, e não na 149;
    - a regra CONC-07/13 está em `cenario.js:139-142, 166-176`, e não em 149-153;
    - o formulário está em l.958-962;
    - a fonte de "Paula = conferência" é `configuracoes.py:8`.

**Recusadas ou mantidas:**
1. **Trocar `CEN_DIA_OP` para 23/09, o "hoje" da demonstração.** Recusada. O dia 4 da semente da OS-0421 é 23/09, com origem web (`cenario.py:55`). Todo primeiro apontamento da ordem principal ficaria retido (executado: "Apontamento do dia 5 (50 ha em 23/09) em conferência: já há dia 4"). Evitar isso exigiria mudar a semente e quebraria os testes do app. A divergência no Mapa ficou registrada no risco 2.
2. **Tirar web + web do critério (só canais diferentes).** Recusada. O PRD 8.5 (l.3025) não distingue canal. O duplo clique já é resolvido pela chave. O falso positivo custa 1 clique e agora é avisado antes de salvar.
3. **Levar a baixa do aparelho para o envio (`CEN_BAIXA_NO_SINAL`), para eliminar o estado "Aguarda duplicidade".** Recusada nesta frente. Mudaria a exibição de custódia na O.S., no Estoque e no Mapa (`osPendCons`, `epCons`, `mapItVis`) e no app. É maior que o problema.
4. **Eliminar o resíduo de 0,01 do caso sem sinal + web (risco 8).** Recusada. Só se resolveria estornando a web já mostrada ao usuário. Ocorre só com dose que arredonda, e a trava existente pede o usado.
5. **Capturar talhão e operador editáveis agora.** Mantida fora, como na proposta. Aumenta a tela e a fatia; o aviso cobre o caso do protótipo.
