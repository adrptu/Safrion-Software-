# Suprimentos simplificado · v2: cada papel abre no que tem de fazer e resolve no registro

**Pedido do proprietário (Adrianus, 05/10/2026):** "em suprimentos, me parece que também tem mais etapas do que precisa, com telas redundantes. simplifique também o fluxo do processo e botões de ação que resolvam tudo em menos telas."

**Rótulos.** Tudo é **especificado**, salvo o que está marcado **executado**. Nada foi editado no repositório e nenhum navegador foi aberto. Os cliques "antes" vêm da contagem da v1, feita lendo o código do HEAD `884620c`; "antes" e "depois" precisam ser medidos no mesmo cenário (`sup_atrito_test.py`, AGENTS §3.3).

**Executado:**
- `git log` em `/home/user/sp-tab5`: HEAD `884620c` (só evidência sobre a 2d `0cf6f90`).
- Em `scratchpad/sup/` (cenário inicial = `cenario.js_prefixo()` do HEAD):
  - `node fila_papel.js`: REQ-035, 039, 040 e 021 com saldo a entregar (5 itens); REQ-031 com 500 kg de sobra numa O.S. Em conferência; K26-11 com 10.000 kg em quarentena; 14 itens em 11 requisições.
  - `node setor.js`: 27 lotes em 5 locais; 10 no Almox. defensivos, 11 no Almox. Lagoa Grande; a REQ-021 (OS-0503, Renato) está toda no Almox. Lagoa Grande.
  - `node reg_entrega.js`: `cenEntregar` entrega 3.640 kg à REQ-036 da OS-0420 (selo "Impedida") e 15 L à REQ-035, que tem reserva própria 0.
  - `node rev_check.js`: um laudo libera 2.100 kg de duas origens no M26-07 (d1); `cenAprovarAjuste(c,'INV-2609',true)` → "Ajuste não está pendente." (a2); o ajuste não guarda quem contou (a3); recusa de consumo sem motivo grava o texto fixo (b1, b2); entregar à REQ-035 baixa a reserva da REQ-039 de 65 para 50 L (c2).
  - `node cont_check.js`: contar 7.900 kg no N26-03 devolve "Contagem abaixo do reservado e bloqueado (8.000 kg)" e não grava nada.
  - `node epk_check.js`: `epk(92500,'bandeja 50 mudas')` → "" (sem embalagem no rótulo).
  - `node rev/r35.js`, `rev/conc.js`, `rev/n6.js`, `v2_chk.js`: REQ-035 com `cenResTot` 0; F26-02 com 545 L físicos, 65 L reservados (todos da REQ-039), validade 03/2028; aceite de 80 L na REQ-035 baixa o F26-02 de 545 para 530 L, gravado "Rui (almoxarife)"; OS-0425 pede 11.400 kg de NPK e a REQ-040 tem 8.000 kg (N26-03: físico 8.000, reservado 8.000).
  - `python3 cmp_conta.py` (v1): 15 insumos, 15 convites, 14 respostas, referência R$ 379.580,00, menor total R$ 368.109,11 → Direção.
- Leitura da captura `gen37/_probe/q_celular_depois_EST_390.png` (390×844, após a 2d): menu lateral de 68 px, título e subtítulo até y≈152, caixa da grade com 266 px, 2 colunas inteiras e a 3ª cortada, 2 linhas de dados visíveis.
- Leitura dos logs da bateria 2d em `docs/parceria/evidencias/v44-tabelas-05/un-20261005/bateria` (`commit.txt` = `0cf6f90`): §9.1.

**Abreviações:** `gen37/` = `/home/user/sp-tab5/tools/prototipo/v37/gen37/` · PRD = `/home/user/Safrion-Software-/docs/PRD.md` (v3.9) · PCMS = `/home/user/sp-specs/docs/pcm-suprimentos/ESPECIFICACAO.md` · BEN = `/home/user/sp-specs/docs/beneficiamento/ESPECIFICACAO.md` · SAF-única = `scratchpad/saf345/especificacao.md` · AUD = `scratchpad/pce/verificada.md` · SUPv2 = `scratchpad/sup/com_5974202396.md` (contrato `e643eec7`) · PADRÃO = `tools/prototipo/v37/specs/padrao-comandos-v3-prompt.md` · RETOMADA = `tools/prototipo/v37/RETOMADA-NUVEM.md` · scratchpad = `/tmp/claude-0/-home-user-Safrion-Software-/65558514-68d9-57f5-9da3-513cd6735cdc/scratchpad`.

---

## 0. Como executar

### 0.1 Base, reserva e impedimento
- **Base:** `884620c` (ponta de `claude/v44-tabelas-05`, com a 2c `e1091d5`/#43 e a 2d `0cf6f90`/#44). Branches `claude/v44-sup-0N` (§10).
- **Reserva antes de editar:** um commit só de reserva no RETOMADA, no padrão do `1fbb354` (RETOMADA:200): seção "## Reserva ativa · SUP-SIMPLES-20261005 · branch …" com o acordo curto da AGENTS §3.4 e as **sobreposições declaradas** (§10). O mesmo acordo vai para um arquivo novo em `docs/parceria/rodadas/`.
- **Impedimento de contrato (AGENTS §2).** O pedido de 05/10 foi feito no chat e muda texto literal do PRD. O Codex registra o pedido e a nova redação na rodada ou em `docs/DECISIONS.md`; o Claude revisa. Nenhum PR de tela é integrado antes. Trechos atingidos:
  - 71.6 linhas Compras e Estoque (PRD:10367-10368) e linha Orientação, "Etapas do processo" (PRD:10370);
  - UX-03: Entrada "na seleção de safras" (PRD:11855), Regra essencial "Lista começa por safra" (PRD:11861), Etapas (PRD:11865) e o fluxograma "1 · Escolha a safra e abra a demanda" (PRD:11879-11890; `docs/prd/fluxogramas/fluxos_v3_9.json`, 4 ocorrências, executado);
  - 72.3 item 2, "etapa Receba devoluções" (PRD:12234). A frase "entrega somente o reservado" fica e passa a valer também no código (§6);
  - DEC-2609-11, "Trocar safra volta à etapa 1" (PRD:12225), e AC-72-10 (PRD:12249);
  - MB-05 do almoxarife (PRD:1970-1978), SU-07 "Ler QR → MB-05" (PRD:1249) e SU-09 "Contar → MB-05" (PRD:1287): **recorte temporário do protótipo**, com dano nomeado (dados fixos e contraditórios, §5) e condição de retorno ("a mesma fila em cartões, com as funções do `est.js`");
  - a mesma redação do 71.6 cobre o SUPv2 (65.7, "Lista de necessidades/cotações → detalhe da compra… conforme estado"; SUPv2:82-89), que é patch sobre a v3.11: o Codex concilia com a v3.9 (SUPv2:215).
- **Autoria:** uma por arquivo ao mesmo tempo (RETOMADA:22). A ordem entre frentes é do Codex (§10).

### 0.2 Fica · muda · sai

| Peça | Onde | Decisão | PR |
|---|---|---|---|
| `cenMudar` atômico | `cenario.js:15-19` | **muda**: ganha `cmd = {chave, nome, obj, ver, payload}` (PCMS-G04, PCMS:358-366): repetição com a mesma chave devolve o recibo sem efeito; `ver` diferente é conflito. Sem `cmd`, igual a hoje. Toda função que muda um item de REQ sobe `it.ver` (entregar, devolver, conciliar, confirmar no app, fechar turno, sinal) | Etapa SUP-2a |
| `cenDisp`, `cenLiberar`, `cenSaldoEntregar`, soma do recebimento no lote, `cenPodeEncerrar`, `cenConcPrevia` | `cenario.js:43, 48-64, 67, 95-97, 243-247, 195-209` | **fica** a regra (`cenConfAbertas` passa a contar também "Aguardando gestora") | — |
| `cenEntregar`: confere só fase e físico − quarentena; baixa a reserva de qualquer O.S.; grava "Rui" fixo | `cenario.js:68-79` (:70, :75, :76, :77) | **muda**: recusa selo "Impedida"; limita à **reserva própria** (72.3 item 2, PRD:12234); baixa só a reserva própria; grava `por` (Ver como) | Etapa SUP-2a |
| `cenDevolver`, `cenReceber`, `cenContar`, `cenConciliar` com quem fixo | `cenario.js:87, 98, 108, 142, 212, 225` | **muda**: recebem `por`; sem `por`, "Rui (almoxarife)" | Etapas SUP-2a/2b |
| `cenConciliar` grava recusa sem motivo | `cenario.js:212` | **muda**: recusa exige `motivo.trim()`; aceite com falta > 0 (baixa do lote além da custódia, :217) passa por "Aguardando gestora" e é decidido por outra pessoa | Etapa SUP-2a |
| `cenAprovarAjuste(c,id,aprovar)` grava "Ana" fixo; o ajuste não guarda o contador | `cenario.js:110, 112-113` | **muda**: `cenContar(c,key,contado,contador)` grava `aj.contador`; `cenAprovarAjuste(c,id,aprovar,por)` só aprova com o papel gestor (`cenExige`); se o gestor também contou, a decisão vale com "Decisão do gestor registrada · revisão independente pendente" (§0.3, PEND-CTL-02); recusar (recontagem) continua livre | Etapa SUP-2b |
| `cenContar` recusa abaixo de reservado + bloqueado e mostra o número | `cenario.js:109` | **muda**: grava sempre a contagem; o ajuste leva `afeta` (reserva ou quarentena atingida); mensagem sem quantidade do sistema | Etapa SUP-2b |
| `cenLiberarQuarentena` zera a quarentena do lote inteiro, sem laudo | `cenario.js:101-103` | **sai**; entra `cenLaudo(c,key,doc,num,resultado,por)` sobre **parcelas** `l.quar=[{doc,qtd,motivo}]` (§6) | Etapa SUP-2b |
| Semente: REQ-035 sem reserva própria | `cenario.py:57-64` | **muda**: cada item de O.S. liberada guarda `res0` (o que a liberação reservou) e o lote reserva `res0 − entregue`; `cenResTot` (`cenario.js:153-155`) soma `res0` + movimentos `reserva`. F26-02 passa a 80 L reservados (65 da REQ-039 + 15 da REQ-035). `CEN0.v` sobe para o próximo livre e ganha `recibos:{}` | Etapa SUP-2a |
| Funções `est*` e validações `ESTV`/`ESAVE` no texto JS da página | `processo_estoque.py:263-346` | **mudam de lugar** para `gen37/est.js` (tela, app futuro e node). `E2` (contagens, contadores, hoje, imped) é parâmetro; o teste em node lê um JSON gerado de `_dados_js()` (`processo_estoque.py:52-63`) | Etapa SUP-2a |
| 6 seções `NOMES` (já sem número, `secoes_state`, `ui37.py:480-482`) | `processo_estoque.py:16, 146` | **muda** para 4 seções (§2) | Etapas SUP-2a/2b |
| A página abre sempre na seção 1 | `processo_estoque.py:534` | **muda**: lê `#sec/#req/#os/#nf/#lote`; sem endereço, abre pelo papel do Ver como (§2.2) | Etapa SUP-1 |
| Pendência da seção em vermelho (`whys`) | `processo_estoque.py:539`; `ui37.py:486` (cor RED) | **muda**: contador neutro num slot novo de `secoes_state` em `ui37.py`, preenchido no `PREVALS`; **sem tocar `g2lib.js`** (reservado pela SAF-única) | Etapa SUP-1 |
| Filtro Fazenda: só "Boa Vista" muda algo | `processo_estoque.py:376`; `engine.py:1431` | **muda**: filtra linhas e contadores pela fazenda do local (`dados_cad.LOCAIS`, `dados_cad.py:135-138`) e da O.S. (`o.faz`, como `processo_os.py:435-437`); "Todas" soma | Etapa SUP-1 |
| `LOCAIS` fixos (4) | `processo_estoque.py:19, 84, 553` | **muda**: fonte única `dados_cad.LOCAIS` estocáveis da fazenda do filtro (com Packing, BEN:74; `l11` Almox. oficina, PCMS:516); o cenário só informa o saldo | Etapa SUP-2b |
| `g_ent` (12 col.) e `g_dev` (11 col.): o mesmo item em duas grades | `processo_estoque.py:89-102, 397-445` | **funde** em `g_req`, sem coluna de ação (§3) | Etapa SUP-2a |
| Linhas "fora da requisição"/"sem requisição" | `processo_estoque.py:442-444` | **fica** a cobertura, dentro de `g_req` (§3) | Etapa SUP-2a |
| `g_rec` com Apta digitada e unidade "kg" fixa; pedidos como linhas | `processo_estoque.py:72-87, 307-309` | **muda**: Apta calculada, quarentena começa em 0, unidade do item; só trabalho do almoxarife (§3) | Etapa SUP-2b |
| "Liberar após inspeção" em Saldos; "Aprovar ajuste" na linha de quem contou | `processo_estoque.py:366, 482, 554-559` | **saem**; viram "Registrar laudo" e decisão da gestora | Etapa SUP-2b |
| Árvore item › lote (54 linhas para 27 lotes); `g_mov` como seção; resumos k1-k6 | `processo_estoque.py:104-124, 446-465, 522-531` | **mudam**: uma linha por lote; Movimentos vira modo de Confira saldos; resumos saem | Etapas SUP-2a/2b |
| `PESSOAS` fixas em "Entregar a" | `processo_estoque.py:21` | **muda**: recebedor = `o.resp`, corrigível no painel | Etapa SUP-2a |
| `epk` só converte embalagem em kg ou L | `processo_estoque.py:170-172` | **muda**: aceita "<nome> <n> <unidade do item>" ("bandeja 50 mudas" → "1.850 bandejas") | Etapa SUP-2a |
| Rótulo fixo "Salvar" do painel | `engine.py:1286` | **muda**: rótulo por registro (`F("savel")`); mudança pequena em `engine.py`, depois do merge da SAF-única | Etapa SUP-2a |
| Links do EST para a O.S. sem `#OS-` | `processo_estoque.py:404, 429, 444, 499` | **muda**: `OS.dc.html#OS-…` (`processo_os.py:658-665`) | Etapa SUP-1 |
| Bloqueio de encerramento na O.S.: `osEncBloq` e selo/prazo da lista e do Kanban tratam conferência como sobra | `processo_os.py:242-244, 287-291` | **muda**: três casos (sinal, conferência, custódia); conferência → "Rui concilia o consumo no Estoque", prazo "conciliar o consumo", sem selo "Sobras a receber", link `EST#req=` (ou `#os=` sem REQ) | Etapa SUP-1 |
| Links da O.S. ao Estoque sem destino; comparação exata | `processo_os.py:291, 347, 416, 979`; `:542, :557` | **muda**: endereço com destino; comparação por prefixo `EST.dc.html` | Etapa SUP-1 |
| Mapa "Receber sobras/devolução"; "Falta insumo · Suprimentos" | `inicio.py:41, 127, 645, 1370`; `irrigacao_estado.js:156` | **muda**: `EST#req=`, `#lote=`; pedido e solicitação na Etapa SUP-3 | Etapa SUP-1/SUP-3 |
| CMP: etapas, `g_dem`, `g_apr`, trilha, k2-k6, "Registrar aprovação da Direção" pelo comprador, trava `whys` 4-6 | `processo_compras.py:16, 75-80, 99-122, 239-241, 312-323, 446, 494-497, 503-591` | **saem** (§5) | Etapa SUP-3 |
| Reprogramar sobrescreve a previsão | `processo_compras.py:468-474` | **muda**: versões `prevs[]` (RF-SUP-012, PRD:2594) | Etapa SUP-3 sobre o PCM 1c |
| Modelo da compra: convite só a homologado, escolha padrão, `sig`, `enviar`, `emitir`, `decidir` | `processo_compras.py:222-226, 235-237, 244, 255, 436-458` | **fica** | — |
| Aba Almoxarife do MB-05, MB-05det, link SU-03det | `mobile.py:655-720, 669` | **sai** do caminho visível (§0.1) | Etapa SUP-2b |
| MB-05 "Minhas retiradas" | `mobile.py:634-654` | **fica** | — |
| Componentes de seção, grade, painel (`aside role=dialog`, 460 px) e busca | `ui37.py:480`; `engine.py:1169-1188, 1266` | **fica** | — |

### 0.3 Implementação (06-09/10): o que valeu na prática
Rótulo: **executado** onde há comando e resultado no commit; o resto segue **especificado**.
- **Nomes das etapas.** "Etapa SUP-1", "Etapa SUP-2a" etc., para não confundir com severidade (S1–S4, PRD 22.1) nem com as etapas PCM-S1..S4 do PCM simplificado.
- **Ordem (Codex, 08/10):** Etapa SUP-1 → SUP-2a → SUP-2b antes do PCM-1a/1b; a **Etapa SUP-3 (tela de Compras) fica para depois da SAF-única e do PCM-1c-dados**. O rascunho da SUP-3 escrito em 06/10 está guardado, sem integrar, na branch local `claude/v44-sup-rascunho-0610`. Nesta entrega, Compras só ganha o nome "Compras" no menu e no título; o botão "Abrir Compra de insumos ›" do Planejar safra muda com a SUP-3.
- **"Ver como" = perfil de quem age no menu lateral** (G2_PERFIS/g2perfil, frente D do CONTROLE-01). Não existe seletor próprio no cabeçalho. Onde este documento diz "Ver como", leia "perfil do menu lateral": ele define a abertura, habilita as decisões do papel e é o `por` gravado (CTL-3).
- **Autoaprovação × PEND-CTL-02 (regra conciliada).** Quem decide ajuste de estoque, laudo de quarentena e consumo acima da custódia é o papel gestor (`cenExige`). Quem não tem o papel (o almoxarife que contou, recebeu ou entregou) não aprova: esta é a proibição geral de autoaprovação deste documento. **Exceção explícita:** quando a mesma pessoa tem o papel de gestor e também fez o fato (contou, registrou a contagem ou a entrada bloqueada, entregou o material), a decisão vale e fica gravada no registro, no movimento e na mensagem como **"Decisão do gestor registrada · revisão independente pendente (Ana contou e decidiu)"** (`cenRevisao`). Não se finge que outra pessoa revisou, não se apaga o fato e não se bloqueia a fazenda de uma pessoa só. Quem faz a revisão independente e como ela fecha o registro fica para o software real (CF-01). Esta regra substitui "recusa `por===aj.contador`" do §0.2, §4.1, §6, N6, AC-SUP-07 e DEC §1.10. Dano evitado: perda aprovada por quem a causou **sem rastro**.
- **Produto acabado da Colheita.** A Colheita já integrada guarda o produto em `c.producao` (D-05 da Colheita) e tem a página Produção › Estoque de produto (`PROD.dc.html`). O Estoque não copia essa grade: Confira saldos › Produção mostra o resumo lido de `c.producao` (por cultura, na unidade de estoque da cultura, `prEstTxt`) e o atalho "Abrir Estoque de produto ›". Assinatura para outras frentes: `estProducao(c, faz)` em `est.js` (só leitura).
- **Manutenção.** Ponto de entrada no Estoque: a REQ de OM entra em Atenda requisições pelo mesmo `estFila`/`estEntregarReq` e pelo `cenMudar(self, fn, cmd)`; o PCM-1b os estende para OM (§7). As SC da manutenção entram em Compras na Etapa SUP-3.
- **Semente:** `CEN0.v = 6` (a 4 é da Colheita e a 5 do BEN-1 na branch do protótipo; no merge de 09/10 as duas mudanças ficam na 6).
- **Painel aberto sozinho a ≥1024 px (§2.3, DEC 1.4): não implementado.** O painel comum do engine (`engine.py`, `_g2form`) é uma gaveta com fundo que cobre a página; abrir sozinho esconderia a fila e os contadores, que respondem "o que faço agora". Painel ao lado da grade é mudança do componente comum (frente DS/engine). Custo: Entregar REQ-039 fica em 2 toques, não 1.
- **Consumo acima da custódia sem "Enviar à gestora".** O relato que passa da custódia já nasce "Aguardando gestora" (`estSitCf`, `est.js`) e entra no contador dela; o almoxarife só recusa, com motivo. A decisão continua do papel gestor (`cenExige`).
- **Atrito medido (executado, `python3 sup_atrito_test.py --base <cópia do 99537ca>`, 09/10, 61/61).** Mesma semente e mesma régua nos dois: clique = botão, linha, chip, link ou escolha numa lista; campo = valor digitado; não contam abrir pelo menu, a preparação do cenário nem o perfil (no software real é o login). Cada tarefa confere o efeito gravado.

  | Tarefa | Antes (99537ca) | Depois |
  |---|---|---|
  | Entregar REQ-039 (1 item) · Rui | 3 | 2 |
  | Entregar REQ-021 (2 itens) a Renato · Rui | 5 (sem Renato no seletor) | 3 (com a troca de fazenda) |
  | Receber a sobra da REQ-031 · Rui | 3 | 2 + 1 campo (quantidade conferida) |
  | Aceitar consumo coberto pela custódia · Rui | 3 | 2 |
  | Recusar relato · Rui | 2 | 3 + 1 campo (motivo) |
  | Consumo acima da custódia | 3, só a gestora | 0 do almoxarife + 3 da gestora |
  | Receber a NF 4533 prevista · Rui | 2 + 4 campos | 3 + 2 campos |
  | Liberar a quarentena do K26-11 · Ana | 3 + 1 campo | 3 + 1 campo (com o resultado do laudo) |
  | Contar INV-2611 sem diferença · Paula | 3 + 1 campo | 2 + 1 campo |
  | Contar INV-2611 com diferença e causa · Paula | 5 + 2 campos | 3 + 2 campos |
  | Aprovar o ajuste do INV-2609 · Ana | 2 | 3 |
  | Da O.S. (OS-0417) à sobra no Estoque | 3 (link + seção + linha) | 1 (o link abre o registro) |
  | **Total (cliques + campos)** | **45** | **38** |

  Pioras, com o dano que evitam: a quantidade da devolução é digitada (devolução não conferida virava saldo apto); a recusa pede o motivo e é secundária do painel do aceite (o porquê do relato sumia; uma primária por painel); o ajuste é aprovado no painel, não na linha (o toque duplo na linha caía no registro seguinte; a conta e as O.S. atingidas ficam à vista antes do toque). Compras é medida na Etapa SUP-3.
- **Pontos de entrada para outras frentes (só o lugar e a assinatura).** Produção: `estProducao(c, faz)` (acima). Manutenção no Estoque: a REQ de OM entra pelo `estFila`/`estEntregarReq` e pelo `cenMudar(self, fn, cmd)`. SC da manutenção em Compras: contrato `c.scs` da PCMS:198, lido por `solDe('SC-…')` no PCM-1c (PCMS:536) e mostrado em Atenda solicitações na Etapa SUP-3; nada de SC é implementado aqui.
- **Verificador de duplicata (§9.1 item 4) não estendido.** `ferramentas/acoes_duplicadas.py` é ferramenta comum e não olha `[role=row]` nem o painel; a regra desta frente ("nenhum comando dentro de linha") é provada pelo caso 4 do `est_fila_test.py`.
- **Colunas essenciais (pedido do proprietário de 10/10; executado no Estoque, §3).** As grades do Estoque mostram só identificação, situação, quem retira ou devolve e os números que decidem; o resto vai para o painel do registro, sem perder dado, e o que servia para achar continua na busca da tabela. Saíram: Lote de Atenda requisições (fica em "Separe:" e na conta do item, e a busca acha a REQ pelo lote); Fornecedor e Item de Receba e inspecione (o item passa à célula do documento; pedido e fornecedor no painel da nota e da parcela e na busca); Contado de Faça contagens (painel; a Diferença é o número que a gestora decide); Reservado e Bloqueado de Confira saldos › Lotes (a conta "Disponível = físico − reservado − bloqueado" abre o painel, com a O.S. de cada reserva e a parcela com "Registrar laudo ›"; o estado de quarentena fica na linha como selo "Em quarentena", AGENTS §4); Lote de Movimentos (painel do movimento; a trilha de um lote é o extrato do painel do lote). Compras não foi tocada nesta entrega: a regra entra nas grades da Etapa SUP-3. DEC §1.29.
- **Testes do módulo saem com código ≠ 0 quando falham:** `cmptest.py`, `consumo_divergente_test.py` e `app_saldo_zero_test.py` saíam 0 mesmo falhando (retorno Codex de 08/10: "19/20 com saída 0 é falha").
- **Bateria das Etapas SUP-1, SUP-2a e SUP-2b (executado, 09/10, sobre o merge do `cdc185f`).** Build 0 FALHA (140 telas) e `montar_render`; varredura 140/140; `acoes_duplicadas` 0 de 140. Do módulo: `sup_unit` 64/64, `est_fila` 52/52, `esttest` OK, `est_cenario` 16/16, `est_fix1` 10/10, `est_fix2` 11/11, `tabelas_est` 25/25, `consumo_divergente` 23/23, `app_saldo_zero` 12/12, `cmptest` sem falhas, `sup_atrito` 61/61. Que tocam os arquivos mexidos: `ap_unico` 80/80 + 23/23, `aprova_quem_decide` 102/102, `sup_os` 5/5, `assinatura` 45/45, `acao_unica` saf/familias/v3, `etapas_celular`, `map_aprov`, `map_decisoes`, `mbtest`, `app_cenario`, `app_entrega_parcial`, `os_ator`, `saf_cmp_continuidade`, `irr_fluxo`, `sutest`, `componentes` sem falha. Vermelhos iguais no `cdc185f` (não são desta frente): `os_cenario` 19/20 (PEND-OS-01), `cal01` 43/45 (CTL-4), `acao_unica responsivo` 17 e 18 (SAF/CMP), `testes_pedido` T01, T02 e T05 (SAF, sai 0 mesmo falhando).

---

## 1. Papéis, perguntas e onde resolvem

| Papel (Ver como) | Pergunta | Abre em (sem endereço) | Resolve com |
|---|---|---|---|
| **Almoxarife (Rui, Paula)** | O que entrego agora, a quem, de onde separo? | Atenda requisições | painel da REQ → **Entregar REQ-… inteira** |
| | Que sobra recebo, que consumo concilio? (bloqueiam o encerramento) | mesma seção | **Registrar devolução** · **Aceitar consumo** · **Enviar à gestora** |
| | Quem chegou ao balcão? | busca da fila (O.S., REQ, pessoa, item, lote) | o painel do registro achado |
| | Que nota confiro, que parcela espera laudo? | Receba e inspecione | **Conferir NF …** · **Liberar parcela** |
| **Contador designado** (`contador` da contagem; INV-2611 = Paula, `processo_estoque.py:62`, `CONTADORES[0]`) | O que conto, sem ver o saldo? | Faça contagens, quando há contagem atribuída a ele | **Salvar contagem** · **Salvar e contar o próximo** |
| **Gestora (Ana)** | Aprovo este ajuste ou este consumo acima da custódia? | a 1ª seção com "Aguardando gestora" (INV-2609 → Faça contagens) | **Aprovar ajuste · −600 kg** · **Aprovar consumo** · **Pedir recontagem** |
| **Comprador (Ana, Gerente da fazenda, até R$ 300.000; `processo_compras.py:19`, `dados2.py:705`)** | O que cotar ou decidir, até quando? | Atenda solicitações | detalhe na fase do estado: **Enviar N convites** · **Aprovar e emitir** · **Enviar à Direção** |
| | Que pedido atrasa ou chega depois da falta? | Acompanhe pedidos | **Reprogramar PC-…** · **Confirmar com o fornecedor** |
| **Direção** | Aprovo esta compra acima da alçada? | Atenda solicitações, filtro "Aguardando você" | **Aprovar e emitir N pedidos** · **Devolver** · **Recusar** |
| **Agrônomo** | Minha O.S. tem insumo para liberar? | O.S. (Liberar = reserva, `cenario.js:48-64`) | **Liberar**; com falta, o selo leva ao pedido ou à solicitação |
| **Planejador** | A demanda foi enviada e em que pé está? | Planejar safra › Demanda de insumos (`passo=demanda`) | **Enviar para cotação** · **Abrir SOL-… ›** |
| **Operador** | O que retiro e confirmo? | App MB-05 › Minhas retiradas | **Confirmar recebimento** |
| **Mecânico / Beneficiamento** | A peça ou a caixa vem pela mesma Compra e pelo mesmo Estoque? | as mesmas filas (PCM 1b/1c; BEN) | as mesmas ações |

---

## 2. Telas finais

### 2.1 Antes × depois
- **Antes:** CMP com 6 etapas numeradas (`steps_state`, `processo_compras.py:147`), 4 avanços que só trocam de tela (`:578-591`) e a cópia da demanda; EST com 6 seções (já sem número), 71 colunas; aba fixa do almoxarife no app.
- **Depois:** **4 seções no Estoque e 2 seções + 1 detalhe em Compras**, nas mesmas 2 telas. Nenhum avanço só navega. Nenhuma linha de grade carrega botão de comando.

| Tela | Seção | Quem age | Substitui |
|---|---|---|---|
| Compras | **Atenda solicitações** (lista mestre) | comprador; Direção pelo filtro | CMP 1, trilha, k2-k6 |
| Compras | Detalhe da solicitação, aberto na fase do estado: **Cote** (A cotar) ou **Decida** (Em cotação em diante) | comprador; Direção | CMP 2 ("A pedir" e "Falta em"), 3, 4 e 5 |
| Compras | **Acompanhe pedidos** (qualquer origem) | comprador | CMP 6 |
| Estoque | **Atenda requisições** | almoxarife; gestora (consumo acima da custódia) | EST 2 + EST 3 (SU-07, PRD:1239-1257) |
| Estoque | **Receba e inspecione** | almoxarife, qualidade | EST 1 + "Liberar após inspeção" (SU-06, PRD:1226) |
| Estoque | **Faça contagens** | contador; gestora | EST 5 (SU-09, PRD:1287) |
| Estoque | **Confira saldos** (Lotes \| Movimentos) | todos, consulta | EST 4 + EST 6 (SU-03, PRD:1167; SU-08) |

### 2.2 Regras comuns
- **Seções em qualquer ordem** (`secoes_state`/`g2secoes`), cada uma com contador neutro do que espera ação, pela fazenda do filtro. Vermelho só para impedimento.
- **Endereço** (`hashchange`): `#sec=` com apelidos (recebimentos → Receba e inspecione; entregas e devolucoes → Atenda requisições com o filtro correspondente; saldos e movimentos → Confira saldos no modo; contagens → Faça contagens; nome desconhecido → regra sem endereço, sem gravar nada), `#req=`, `#os=` (O.S. sem requisição), `#nf=`, `#lote=`, `#sol=`, `#pc=`. Abrir por endereço nunca muda `c.rev` nem `c.movs`.
- **Abertura sem endereço, pelo papel do Ver como:**
  - almoxarife: Atenda requisições → Receba e inspecione → Faça contagens → Confira saldos (1ª com pendência);
  - contador com contagem atribuída "A contar": Faça contagens;
  - gestora: 1ª seção com "Aguardando gestora"; sem nenhuma, Confira saldos;
  - Compras: Atenda solicitações; Direção com o filtro "Aguardando você".
- **Ver como (simulação):** no cabeçalho, rotulado "simulação". Estoque: Rui (almoxarife), Paula (almoxarife), Ana (gestora). Compras: Ana (até R$ 300.000) ou Direção. Define a abertura, habilita só as decisões do papel (as outras ficam desabilitadas com o motivo, por exemplo "Ação do almoxarife") e é o `por` gravado em **todo** movimento. Não filtra a fila. Fica em `localStorage` dentro de try/catch e nunca muda `c.rev`. No software real, o papel vem do login e o servidor valida (CF-02).
- **Fazenda:** filtro real no Estoque (DEC-2609-11, AC-72-10). Santa Rita é o padrão (`engine.py:1431`). Boa Vista continua vazia com "Ver Santa Rita".
- **Natureza (SUPv2 65.7):** filtro rápido sobre os mesmos IDs (Insumos agrícolas primeiro; Peças e materiais; Serviços; Imobilizado), derivado do grupo do item numa tabela única em `dados_cad.py`. Só aparece quando as linhas têm mais de uma natureza; padrão "Todas" nas filas de trabalho, para não esconder pendência. Entra quando a 2ª natureza chega: EST no PCM 1b (peças), CMP na Etapa SUP-3.
- **Faixa no detalhe da compra:** Veio de → Está aqui → Falta → Próxima ação (PRD:280), com **um** link de origem (hoje 4: `processo_compras.py:278, 322, 398, 505`).

### 2.3 Padrão de comando: a linha identifica, o painel resolve
Fonte: PADRÃO:12-16 ("uma instância por efeito"; "rodapé fixo que repete a primária está proibido") e :69-71 ("a mesma ação duas vezes para o mesmo alvo é duplicata").
- A linha mostra Identificação, Situação e dados. **Nenhum botão de comando dentro de `[role=row]`** nas grades desta frente (o chevron da árvore e o link de identificação não são comando).
- Tocar a linha abre o painel do registro (`aside role=dialog`, `engine.py:1266`; a ≤640 px ocupa a tela). O painel tem **uma primária** no rodapé, com o rótulo que confirma o quê, quanto, de onde e para quem; secundárias ao lado.
- A ≥1024 px, o painel da 1ª linha com ação já abre ao lado da grade (abrir não executa). A ≤640 px a página abre na lista.
- **Comando com chave** (PCMS-G04): a chave nasce quando o painel abre e fica no estado da tela; `ver` = a versão de cada item da REQ (`it.ver`, PCMS:190) no momento em que o painel abriu; `payload` = itens e quantidades do rótulo. Repetir com a mesma chave devolve o recibo sem efeito; `ver` diferente → "Mudou desde que você abriu: … Revise e confirme.". Não usar o `c.rev` global como versão (PCMS:364).
- **Depois de executar:** o botão some e o painel mostra o comprovante (PRD:9367) do **mesmo** registro; a próxima REQ só aparece como link "Próxima: REQ-040 ›", que só navega. Um 2º toque no mesmo lugar não encontra comando.
- O comando coletivo (Entregar inteira, Enviar N convites, Aprovar e emitir) fica só no painel ou detalhe do documento, nunca no de um item.

### 2.4 Layout

**Estoque › Atenda requisições, 390 × 844, Santa Rita, Ver como Rui**
```
┌menu┬───────────────────────────────┐
│68px│ Estoque  Fazenda Santa Rita ▾  │ casca atual (menu lateral fica)
│    │ Ver como: Rui ▾ (simulação)    │
│    │ [Atenda requisições · 3 · 1 ▾] │ seletor de seção com contador
│    │ 🔍 O.S., REQ, pessoa, item…    │
│    │ Com ação · Em uso · Todas      │ filtro pela Situação
│    ├───────────────────────────────┤
│    │ Requisição›item │ Situação     │ 2 colunas à vista; o resto rola
│    │ REQ-035         │ A entregar   │ dentro da caixa (g2rola)
│    │ REQ-031         │ Sobra a rec. │
│    │ REQ-039         │ A entregar   │
│    │ REQ-040         │ A entregar   │
└────┴───────────────────────────────┘
toque em REQ-035 → painel em tela cheia:
┌────────────────────────────────────┐
│ ‹ Fila   REQ-035 · OS-0421 Em exec. │
│ Fungicida A: solicitado 175 L ·     │
│ entregue 160 L · consumido 95 L ·   │
│ em custódia 65 L · a entregar 15 L  │
│ Separe: F26-02 · val. 03/2028 ·     │
│ Almox. defensivos · 3 galões de 5 L │
│ Recebedor: Marcos (trocar)          │
├────────────────────────────────────┤
│ [Entregar REQ-035 · 15 L Fungicida A│ primária no rodapé do painel
│  lote F26-02 a Marcos]              │
└────────────────────────────────────┘
```
- Promessa a 390 e 360: a página não rola de lado; Requisição e Situação ficam à vista sem rolar a grade; o painel mostra "Separe:" e a primária sem rolar. **Quantas linhas cabem acima da dobra é medido na Etapa SUP-0** (a captura atual mostra 2), não prometido.
- Mudar a casca (menu ☰ a ≤640 px) fica fora (FORA-DE-ESCOPO).

**Estoque, 1440 × 900:** cabeçalho com Fazenda e Ver como; abas "Atenda requisições · 3 a entregar · 1 sobra", "Receba e inspecione · 1 nota · 1 laudo", "Faça contagens · 1 a contar · 1 ajuste", "Confira saldos"; grade à esquerda e painel de 460 px à direita, já aberto na REQ-035.

**Compras › SOL-2026-07, fase Decida, 390:** "‹ Solicitações"; faixa curta "Em cotação · 14 de 15 respostas · Próxima: Enviar à Direção · Ver origem"; resumo dos convites recolhido; grade Grupo › insumo › proposta com os grupos fechados (menos os que têm pendência); rodapé com "Total R$ X · N pedidos · aprova: Direção (acima de R$ 300.000)" e a primária do estado (§4.2). A 1440, a mesma estrutura; o detalhe substitui a lista e "‹ Solicitações" volta com filtro e posição (PRD 4.2).

---

## 3. Grades e colunas

**Regras:** uma variável por coluna; unidade na célula ("65 L", "R$ 3,90/kg"); até 7 colunas de dado (PRD:287); ordem **Identificação | Situação | dados**; 1ª coluna presa; filtro rápido pela Situação (`qf`, `engine.py:1182`); quem sai da grade vai para o painel, nunca some.

**g_req · Atenda requisições** (funde `g_ent` e `g_dev`; colunas essenciais desde 10/10: o Lote saiu para "Separe:" e a conta do item no painel, e segue na busca)

| Requisição › item | Situação | A entregar | Em custódia | Com quem | O.S. |
|---|---|---|---|---|---|
| REQ-039 | A entregar | 65 L | 0 L | Marcos (`o.resp`) | OS-0424 (`#OS-0424`) |
| ▾ REQ-021 › Muda de mamão Formosa | A entregar | 92.500 un | 0 un | Renato | OS-0503 |

- **Linhas além dos itens da REQ** (cobertura de `processo_estoque.py:442-444`): filha "<produto> · fora da requisição" sob a REQ, e mãe "<O.S.> · sem requisição" quando `k.req` é vazio (`cenario.js:183`); Situação "Consumo em conferência".
- **Situação** (uma por linha, nesta prioridade): O.S. impedida · Aguarda liberação · Lote insuficiente · Reserva parcial · faltam X · A entregar · Aguarda confirmação no app · Consumo em conferência · Aguardando gestora · Sobra a receber · Em uso · Concluída.
  - "Reserva parcial · faltam 3.400 kg": a O.S. pede mais do que a REQ reservou (OS-0425: 11.400 × 8.000 kg, executado); o painel mostra pedido, reservado e falta, com link ao pedido ou à solicitação. Não impede entregar o reservado.
  - "Lote insuficiente": o físico livre do lote não cobre a reserva própria (por exemplo, depois de um ajuste aprovado). O painel não oferece "Entregar inteira"; oferece "Entregar parte" até o que existe.
- **Ordem (fixada no teste):** O.S. Em execução com saldo a entregar → encerramento bloqueado (sobra ou conferência) → O.S. Liberadas com saldo, pela ordem da REQ. Santa Rita, "Com ação": REQ-035, REQ-031, REQ-039, REQ-040. Todas: REQ-035, REQ-031, REQ-021, REQ-039, REQ-040.
- **Painel da REQ:** a conta por item (`econta`: solicitado, entregue, consumido, devolvido, em custódia, a entregar), "Separe:" por item (lote, validade, local, embalagem), recebedor corrigível, trilha de movimentos e a primária.
- **Saem da grade:** Fase da O.S. (vai para a Situação), Solicitado/Entregue/Consumido/Devolvido, "A entregar em embalagens" e Detalhe (vão para o painel).

**g_rec · Receba e inspecione** (só trabalho do almoxarife; o estado do pedido fica em Acompanhe pedidos)

| Documento › item | Situação | Na nota | Em quarentena | Previsão |
|---|---|---|---|---|
| NF 4533 › Semente de soja 58 W | Nota prevista | 20.000 kg | 0 kg | 24/09 |
| NF 4501 › KCl 60% · K26-11 | Aguarda laudo | 60.000 kg | 10.000 kg | — |
| REQ-xxx › item · lote · devolução (bloqueada) | Aguarda laudo | — | … | — |

- Desde 10/10: a coluna Item saiu (repetia a identificação) e a célula do documento diz o item; pedido e fornecedor no painel da nota ("PC-090 · Coop. Vale · …") e da parcela ("Origem: …"), e na busca.

- Uma linha por **parcela** em quarentena (documento de origem), nunca por lote inteiro.
- **Situação:** Aguarda laudo · Nota prevista · Conferida · Sem pedido · regularizar (PCMS-M25, depois do 1c) · Conferir serviço (quando houver serviço, SUPv2 65.7).
- **Criar:** "Registrar NF recebida" à direita do título da lista (PADRÃO, tabela 1) abre o formulário com Pedido em lista dos PCs abertos da fazenda. Até o 1c, de `D2.PEDIDOS` (`processo_estoque.py:53`); depois, de `c.pedidos`.
- **Formulário:** herdados Pedido, Local (do item) e Unidade; digitados NF, Na nota, Conferida, Lote e Validade (só semente); Quarentena começa em 0; Apta = Conferida − Quarentena, só leitura; Divergência e Motivo só com quarentena ou divergência.
- **Painel da parcela:** nº do laudo e resultado (Aprovado ou Reprovado, com destino). Quem fica gravado é o Ver como. Lote vencido não aceita "Aprovado".

**g_cnt · Faça contagens**

| Contagem | Situação | Item | Lote | Local | Diferença |
|---|---|---|---|---|---|

- Contado (desde 10/10): no painel da contagem; a Diferença é o número que decide.

- **Situação:** A contar · Informar causa · Aguardando gestora · Ajustada · Recontar · Conferida.
- Sistema e diferença só aparecem **depois** de salvar; nenhuma mensagem de erro mostra quantidade do sistema.
- **Contar local** (secundária na barra da coleção): uma linha cega por lote do local, contador = Ver como; o painel anda por "Salvar e contar o próximo". Executado: o Almox. defensivos tem 10 lotes.

**g_lot · Confira saldos › Lotes** (uma linha por lote; hoje cada item tem 1 lote, executado)

| Item | Lote | Físico | Disponível | Validade |
|---|---|---|---|---|

- Reservado e Bloqueado (desde 10/10): na conta do painel ("Disponível = físico − reservado − bloqueado = …"), com a O.S. de cada reserva e cada parcela em quarentena. O estado fica na linha: o Item leva o selo "Vencido" ou "Em quarentena" (sem número, por causa da contagem cega).

- Chips de local da fonte única, filtrados pela fazenda. Painel: a conta do disponível, local, reservas e custódias por O.S., parcelas em quarentena com "Registrar laudo ›" (`#nf=`/`#lote=`) e o extrato (`processo_estoque.py:363`).
- **Contagem cega na consulta:** para quem tem contagem aberta atribuída do lote, Físico e Disponível mostram "— (contagem aberta)".

**g_mov · Confira saldos › Movimentos:** Data e hora | Movimento | Documento | Item | Quantidade | Quem (o Lote saiu em 10/10: painel do movimento e extrato do lote). Registro, condição, O.S., origem e sinal do app vão para o painel; fica o filtro "Aguardando sinal".

**g_sol · Atenda solicitações** (substitui a `g_saf`, `processo_compras.py:73`)

| Solicitação | Situação | Falta em | Origem | Itens | Valor ref. | Quem age |
|---|---|---|---|---|---|---|
| SOL-2026-07 | A cotar | a falta mais próxima (`faltaDe`, :208) | Safra 2026/27 | 15 insumos | R$ 379.580,00 | Ana (compras) |

- **Situação** (vocabulário único com o SAF, §7): A cotar · Em cotação · Justificar · Pronta para decidir · Aguardando Direção · Devolvida · Recusada · necessidade aberta · Pedidos emitidos.
- **Origem:** Safra · Manutenção OM-… (PCM 1c) · Beneficiamento OB-… · Balcão NF … (M25). Safra encerrada (SOL-2025-06) no filtro Concluídas.

**g_conv · fase Cote:** Grupo › fornecedor | Convite | Resposta | Homologação | Canal | Contato | Responder até. Tocar no fornecedor muda convite, canal e prazo (seleção da coleção). Não homologado aparece "Indisponível", com motivo e link ao CD-05.

**g_cmp · fase Decida:** Grupo › insumo › proposta | Escolha | A pedir | Falta em | Chega em | Preço ("R$ 3,90/kg") | Custo. Frete, pagamento, validade e prazo vão para o painel da proposta. Painel do insumo: necessidade (bruta − estoque apto − a receber), justificativa e "Ver memória no Planejar safra ›".

**g_ped · Acompanhe pedidos** (substitui a `g_ent` da CMP, `processo_compras.py:103-108`)

| Pedido › item | Situação | A entregar | Recebido | Previsão | Falta em | Fornecedor |
|---|---|---|---|---|---|---|

- **Situação:** Atrasado · Chega depois da falta · Aguarda confirmação · Parcial · Confirmado · Recebido.
- **Painel:** promessas anteriores (`prevs[]`, data e motivo), NFs recebidas com "Ver recebimento ›" (`EST#nf=`), parte em quarentena, origem (SOL ou SC), canal e contato autorizados.

---

## 4. Ações por contexto (uma primária por tela)

### 4.1 Estoque

| Contexto | Primária (rodapé do painel) | Secundárias |
|---|---|---|
| Lista de qualquer seção | nenhuma | busca, filtros, Contar local, Registrar NF recebida |
| Painel da REQ com saldo a entregar | **Entregar REQ-… inteira** (rótulo §4.3) | Próxima REQ › (navega) |
| Painel do item com saldo | **Entregar parte** (quantidade em branco, até a reserva própria) | Trocar recebedor |
| Painel do item com sobra | **Registrar devolução** · quantidade conferida **em branco**, dica "esperado: 500 kg com Paula"; Condição (Apta é o padrão); observação obrigatória se bloqueada | — |
| Painel do consumo em conferência, coberto pela custódia | **Aceitar consumo**, com a prévia de `cenConcPrevia` | **Recusar relato** (motivo digitado obrigatório) |
| Idem, com falta > 0 (baixa do lote além da custódia) | almoxarife: **Enviar à gestora**; gestora: **Aprovar consumo** (se foi ela quem entregou o material, fica revisão independente pendente, §0.3) | Recusar relato |
| Painel da nota prevista | **Conferir NF 4533** | — |
| Painel da parcela em quarentena | **Liberar parcela** (laudo aprovado) | Manter bloqueada (reprovado, com destino) |
| Painel da contagem (contador) | **Salvar contagem** → com diferença, o mesmo painel pede a causa → **Enviar ajuste à gestora** | Salvar e contar o próximo (Contar local) |
| Painel do ajuste (gestora) | **Aprovar ajuste · −600 kg**, com o efeito na reserva quando houver ("afeta a REQ-040: faltarão X kg") | Pedir recontagem. Quem contou sem o papel de gestor (Rui no INV-2609, `processo_estoque.py:28`) não vê "Aprovar"; se a gestora contou, a decisão dela vale e o painel diz "a decisão fica registrada como sua, com revisão independente pendente" (§0.3) |
| Confira saldos | nenhuma (consulta) | Registrar laudo › |

### 4.2 Compras

| Contexto | Primária | Secundárias |
|---|---|---|
| Atenda solicitações / Acompanhe pedidos (listas) | nenhuma | busca, filtros |
| Cote (A cotar) | **Enviar 15 convites (simulado)** | tocar no fornecedor |
| Decida, sem resposta | nenhuma; nota "Aguardando propostas · 0 de 15" | Convidar outro fornecedor |
| Decida, convidado novo depois do envio | **Enviar N convites adicionais (simulado)** (quem já recebeu não recebe de novo, `processo_compras.py:422-435`) | — |
| Decida, justificativa pendente | **Justificar N escolhas** (abre o 1º insumo) | — |
| Decida, dentro da alçada | **Aprovar e emitir N pedidos · R$ X** → prévia dos PCs na mesma área (`:554`) → **Confirmar emissão** | Convidar outro fornecedor |
| Decida, acima da alçada | **Enviar à Direção · R$ X** | Convidar outro fornecedor |
| Aguardando Direção (comprador) | nenhuma; nota "Aguardando Direção desde …"; mudar uma escolha invalida o envio (`sig`) e a primária vira **Reenviar à Direção** | — |
| Aguardando Direção (Ver como Direção) | **Aprovar e emitir N pedidos · R$ X**, com a prévia dos PCs já visível | **Devolver**, **Recusar** (motivo obrigatório, `:452-458`) |
| Devolvida | **Ajustar escolhas** (abre o insumo citado) | — |
| Recusada | nenhuma | "Ver demanda ›" (a necessidade continua aberta) |
| Painel do pedido | **Reprogramar PC-…** (data a partir de hoje e motivo; acrescenta versão) ou **Confirmar com o fornecedor (simulado)**, pelo estado | Ver recebimento › |

"Aprovar e emitir" grava a decisão e a emissão como dois registros com horário, como "Aprovar e liberar" (PRD:2968), para o KPI-SUP-04 e o OTIF.

### 4.3 "Entregar REQ inteira": o botão que resolve sem formulário
- **Rótulo** (vale como confirmação, PRD:9365): o quê, quanto, lote e para quem. Ex.: "Entregar REQ-021 · 92.500 un Muda de mamão (lote LG26-05) + 20.000 kg Superfosfato (lote LG26-09) a Renato". Acima dele, uma linha "Separe:" por item: lote, validade, local e embalagem ("LG26-05 · val. 12/2027 · Almox. Lagoa Grande · 1.850 bandejas de 50 mudas").
- **Efeito:** `estEntregarReq(c, rid, por, cmd)` chama `estEntregar` para cada item com saldo dentro de **um** `cenMudar` com `cmd`; um item recusado desfaz tudo (`cenario.js:15-19`).
- **Travas dentro do comando** (§6): O.S. Liberadas ou Em execução, sem selo "Impedida"; cada item até a reserva própria e o físico livre.
- **Repetição:** mesma chave → recibo, sem movimento; o botão some depois do efeito (§2.3).
- **Comprovante:** "REQ-039: 65 L de Fungicida A (13 galões de 5 L, lote F26-02) entregues a Marcos · aguarda confirmação no app".
- **Entrega parcial:** pelo painel do item. A O.S. continua sem iniciar até a mistura completa (ESTOS-03, PRD:7103).
- É a PCMS-M14 (PCMS:310). Implementa-se na Etapa SUP-2a, com o `cenMudar` com `cmd` (G04); o PCM 1b reaproveita e estende para OM (§10).

---

## 5. Cortes e fusões

| Hoje | Decisão | Motivo | Onde continua |
|---|---|---|---|
| CMP 1 "Escolha a safra" e "Trocar safra" | lista mestre e "‹ Solicitações" | é a listagem do master-detail; com SC e balcão deixa de ser "a safra" (PCMS:389) | Atenda solicitações; safra como Origem e filtro |
| CMP 2 "Confira a demanda" | **cortada** | cópia do SAF (`processo_compras.py:75`) com outro vocabulário e números que divergem depois de reprogramar (`:208-210`) | SAF `passo=demanda`; no detalhe ficam "A pedir" e "Falta em" |
| "Na compra" (`sitDem`, :260-270) × Situação do SAF (`safra.js:798`) | uma função | duas palavras para o mesmo estado | SAF e Compras |
| CMP 3 depois do envio; CMP 4 + CMP 5; bloco da alçada | resumo; fundidas na Decida; uma linha | a 5 é a 4 agrupada por fornecedor (`:239-241`); a alçada repetia o k5 | Decida |
| "Registrar aprovação da Direção" pelo comprador | **sai** | quem envia registrava a decisão de quem aprova (AUD:185) | Ver como Direção |
| CMP 6 | Acompanhe pedidos | rotina de todas as origens, presa atrás da cotação (`:494-496`) | Acompanhe pedidos |
| Avanços "Solicitar cotações ›" … "Acompanhar entrega ›", faixa de 6 etapas, trilha, k2-k6 | **cortados** | 4 a 5 cliques sem decisão; o progresso aparecia 3 vezes | o estado abre a fase; faixa Veio de → Próxima ação |
| EST 2 + EST 3 | fundidas | mesmo registro em duas grades | Atenda requisições |
| EST 6 | modo | repetia o extrato do lote (`processo_estoque.py:363`) | Confira saldos › Movimentos |
| Pedido como linha em Receba e inspecione | **sai** | o mesmo PC em duas grades com 5 colunas iguais | Acompanhe pedidos; o formulário de NF lista os PCs abertos |
| "Liberar após inspeção" em Saldos | "Registrar laudo" por parcela | ação longe do fato; liberava sem laudo e liberava o lote inteiro | Receba e inspecione; painel do lote |
| "Aprovar ajuste" na linha de quem contou | decisão da gestora | o almoxarife que conta não aprova a própria diferença (DEC-2609-13); a gestora que contou decide com revisão independente pendente (§0.3) | Faça contagens |
| Coluna de ação nas linhas e primária "da 1ª linha" | **saem** | o mesmo comando duas vezes para o mesmo alvo (PADRÃO:69-71); toque duplo na linha caía na REQ seguinte | painel do registro |
| Campo Apta digitado | calculado | Apta + quarentena = conferida (`:307`) | formulário, só leitura |
| "A entregar em embalagens", Detalhe | painel e rótulo | a mesma quantidade em duas unidades; o porquê vira Situação | "Separe:", painel |
| Árvore item › lote com 1 lote; resumos k1-k6; lista fixa "Entregar a" | linha única; contadores; `o.resp` | dobrava as linhas; repetiam as grades; faltavam Renato, Wesley e Joaquim | Lotes; abas; painel |
| Aba Almoxarife do MB-05, MB-05det e link SU-03det | **saem** do caminho visível | dados fixos e contraditórios: 10 sc × 500 kg; sobra no M26-05 × no M26-07 (`mobile.py:709` × CEN0, `dados2.py:724`); leva a tela oculta (`mobile.py:669`) | Atenda requisições a 390 |

---

## 6. Regras e invariantes

| Invariante | Como fica | Função | Dano evitado |
|---|---|---|---|
| Saldo só muda por movimento | nenhuma grade edita saldo; toda ação dentro de `cenMudar` | `cenario.js:15-19` | estoque sem fato físico |
| Reserva na liberação (DEC-2609-13) | Suprimentos não reserva; a semente reflete a liberação (`res0`) | `cenLiberar`, `cenResTot` | retirada sem O.S. aprovada |
| Entrega só do reservado da versão liberada (72.3 item 2) | dentro de `cenEntregar`: O.S. Liberadas ou Em execução, **sem selo Impedida**, até `cenResPropria` e o físico − quarentena; baixa só a reserva própria | `cenario.js:68-79`, `:156` + PCMS-M06 | insumo sem aprovação ou O.S. impedida (S1); desvio da reserva de outra O.S. (S2) |
| Entregar inteira é tudo ou nada e não repete | um `cenMudar` com `cmd` (chave, `ver`, payload) | `estEntregarReq` | entrega em dobro ou a outra REQ (S2) |
| Devolução conferida, até a custódia | quantidade digitada, em branco | `cenDevolver` | sobra não conferida virando saldo apto |
| Encerrar só com custódia zero e sem conferência aberta (inclui "Aguardando gestora") | igual; os links levam à linha certa | `cenPodeEncerrar`, `cenConfAbertas` | custo e saldo errados |
| Conciliação | prévia antes de aceitar; recusa com motivo não vazio; baixa além da custódia decidida por outra pessoa | `cenConciliar` | consumo fictício; perda aprovada por quem entregou |
| NF duplicada não entra | igual | `processo_estoque.py:311` | entrada em dobro |
| Um código de lote, uma validade | nota no lote existente com outra validade é recusada no campo Validade e no cenário; sem validade ("—") dos dois lados não conflita (DEC §1.31, executado) | `cenValidadeConflito` (`cenario.js`), lida por `cenReceber` e pela validação de Receba e inspecione | produto vencido sem o selo "Vencido" indo ao campo |
| Quarentena só sai por laudo, **parcela por parcela** | `l.quar=[{doc,qtd,motivo}]`, `l.quarentena` = soma; `cenLaudo` libera só a parcela do documento; reprovado mantém; lote vencido não libera. Lote salvo antes da mudança: a quarentena existente vira uma parcela "anterior" (K26-11: NF 4501/PC-088, "Laudo de umidade pendente", `processo_estoque.py:59`) | `cenReceber`, `cenDevolver`, `cenLaudo` | lote impróprio no disponível (RF-SUP-007) |
| Contagem cega; recontagem por outra pessoa | saldo oculto no formulário, na linha, no filtro, nas mensagens e em Saldos para o contador; a contagem é sempre gravada | `estContar`/`estRecontar` (`processo_estoque.py:277-292`), `cenContar` | perda escondida |
| Ajuste decidido pelo papel gestor; quem contou sem esse papel não aprova; o gestor que contou decide com revisão independente pendente | `aj.contador` gravado; `cenAprovarAjuste(c,id,true,por)` exige o papel gestor (`cenExige`) e grava `aj.rev` = "Decisão do gestor registrada · revisão independente pendente (… contou e decidiu)" quando `por` é quem contou; a trilha grava `por`; recusar continua livre | `cenario.js` (`cenAprovarAjuste`, `cenRevisao`) | perda aprovada por quem a causou sem rastro (§0.3) |
| Ajuste que atinge reserva | a gestora vê as O.S. atingidas antes de aprovar; depois, a REQ mostra "Lote insuficiente" e só "Entregar parte" | `cenContar` (`afeta`) | entrega prometida sem material |
| Quem fez fica gravado | `por` (Ver como) em entrega, devolução, recebimento, contagem, conciliação, laudo e ajuste | funções `cen*` | trilha que não diz quem fez |
| Convite só a homologado e canal autorizado; justificativa fora do menor custo a tempo; `sig` invalida aprovação | igual | `processo_compras.py:222-226, 235-237, 244, 255` | contratar sem cadastro; pagar mais sem motivo; aprovar compra diferente |
| Alçada | só o papel com alçada decide; quem envia não decide | `ALCADA`, `dados2.py:705` (valores de demonstração, RN-043) | comprometer dinheiro acima da competência |
| Previsão do pedido | versões em `prevs[]` | PCMS-M11 / 1c | atraso apagado (RF-SUP-012) |
| Marcos da compra | solicitação, envio, decisão, emissão, confirmação e recebimento apto, com horário | `emitir`, `env`, `aprov` | perda do KPI-SUP-04 e do OTIF |

**Sai, porque não tem dano nomeado:** a trava `whys` das etapas 4 a 6 da CMP (`processo_compras.py:494-496`).

---

## 7. Integrações

**Planejar safra (fonte única da demanda).** A demanda e a memória do CAL-01 ficam só no SAF, na etapa 4 da SAF-única ("Confira a demanda de insumos"), endereço `SAF.dc.html#saf=<id>&passo=demanda` (o `etapa=6` antigo é lido como 4, SAF-única:432-447). A SAF-única já troca os textos e o `safHref` em `processo_compras.py`; a Etapa SUP-3 parte disso. "Abrir Compra de insumos ›" (`safra.js:840`) vira "Abrir SOL-2026-07 ›" → `CMP.dc.html#sol=…&saf=…` (`solHref`, `safra.js:646`). Uma função de situação lida pelo SAF (`safra.js:798`) e pela Compra (`sitDem`); Recusada aparece no SAF como "Não contratado · necessidade aberta".

**O.S. (Etapa SUP-1)**

| Link | Destino |
|---|---|
| "Entregar no Estoque" (`processo_os.py:347`), "Retirar no almoxarifado ›" (`:979`), "Receber devolução no Estoque" (`:291`) | `EST.dc.html#req=REQ-…` |
| Bloqueio por consumo em conferência (`:242-244`, `:287-291`) | "Rui concilia o consumo no Estoque" → `#req=` (ou `#os=` sem REQ) |
| "Ver saldos no Estoque" (`:416`) | `#lote=`; depois da Etapa SUP-3, `CMP#pc=` se houver pedido, senão `CMP#sol=` |

Liberar continua na O.S. `processo_os.py:542, 557` passam a comparar o prefixo `EST.dc.html`.

**App:** "Minhas retiradas" (`mobile.py:634-654`) fica. A aba Almoxarife e o MB-05det saem até virarem a mesma fila em cartões (FORA-DE-ESCOPO). O passo "Retirar no almoxarifado" na entrega parcial (`mobile.py:200`; AUD:191) fica com o CONTROLE-01.

**Mapa:** "Receber sobras" e "Receber devolução" (`inicio.py:127, 645, 1370`) → `EST#req=`; o docstring de `inicio.py:41` passa a ser verdade. "Comprar" (`:897, 903`) → `CMP#sol=` na Etapa SUP-3.

**PCM × suprimentos (PR #45).**
- Equivalência para os aceites do PCM: EST etapa 1 → Receba e inspecione; EST 2 e 3 → Atenda requisições; EST 4 → Confira saldos; CMP 1 → Atenda solicitações; CMP 3 e 4 → detalhe Cote/Decida; CMP 6 → Acompanhe pedidos.
- **Mudanças a registrar na PCMS** (autor da PCMS escreve, o Codex revisa): M14 e o `cenMudar` com `cmd` (G04) nascem na Etapa SUP-2a e o 1b os estende para OM; M06 deixa de dizer "a contagem abaixo do reservado continua recusada" (PCMS:270): a contagem é gravada e o ajuste com `afeta` vai à gestora, sem desviar reserva; `CEN0.v` passa a "próximo livre" em cada PR (a Etapa SUP-2a usa um número antes do 1a).
- A SC-041 vira linha de Atenda solicitações (Origem "Manutenção · OM-0235", "Falta em" = data da peça, sem CAL-01). O PC-2xx vai para `c.pedidos` (1c) e aparece em Acompanhe pedidos e no formulário "Registrar NF recebida". A REQ de OM entra na fila com entrega no balcão (`confirmado:'balcao'`, M14). O teto de 6 cliques para comprar 1 item (PCMS:465) fica com folga (§8).

**Beneficiamento:** as caixas da OB entram em Atenda requisições (recebedor `o.resp`, balcão). LOCAIS da fonte única, com Packing (BEN:74). `#sec` com os apelidos do §2.2. O E11 (BEN:856) passa a esperar `aria-current` em "Atenda requisições" e o filtro "Sobra a receber": combinar com a frente BEN.

**CONTROLE-01 (AUD §4-5):** itens 1 (ajuste por outra pessoa) e 2 (laudo) entram na Etapa SUP-2b; o padrão de "quem aceita consumo acima da custódia" segue o da AUD:235 (a gestora) e entra na Etapa SUP-2a; o item 5 (compra) fica coberto no protótipo pelo Ver como. O item 10 (`cal01.js:14`, a demanda não lê o realizado) **continua errado** e é pré-condição para levar a Compra ao proprietário: a Compra segue pedindo 145,2 L de Fungicida A que a OS-0421 já executa.

---

## 8. Atrito, antes × depois
Clique = botão, linha ou chip; campo = valor digitado; partida pelo menu. "Antes" da v1 (código do `884620c`); "depois" especificado. Medir os dois no `sup_atrito_test.py`. **Estoque medido em 09/10 (executado): §0.3.**

| Tarefa | Antes | Depois | Nota |
|---|---|---|---|
| Descobrir o trabalho do dia (qualquer papel) | até 4 cliques + 4 resumos | **0** | abertura pelo papel e contadores |
| Entregar REQ-039 (1 item) | 3 | **2** (linha, Entregar); da O.S. pelo link, link + 1 | a ≥1024 px, a 1ª REQ com ação já abre: 1 |
| Entregar REQ-021 (2 itens) | 5, e o seletor não tem Renato | **2** com Lagoa Grande (+1 para trocar a fazenda) | recebedor herdado |
| Receber devolução REQ-031 | 3 cliques, 0 campos | 2 + **1 campo** | o campo é de propósito: conferir (PRD 42.4; CMD-45) |
| Conciliar coberto: aceitar · recusar | 3 · 2 sem motivo | 2 · 2 + motivo | — |
| Conciliar acima da custódia | 3, só o almoxarife | 2 do almoxarife + 2 da gestora | independência |
| Receber NF 4533 | 2 + 4 campos | 3 + **2 campos**; por `#nf=`, 2 | Apta calculada |
| Receber PC novo (PC-101…) | **sem caminho** (`processo_estoque.py:53, 68`) | 3 + 5 campos (Registrar NF, pedido, salvar) | depois do 1c |
| Liberar quarentena K26-11 | 3, sem laudo | 3 + nº + resultado | controle novo |
| Contar sem diferença · com diferença | 3+1 · 5+2 | 3+1 · **4**+2 | causa no mesmo painel |
| Contar o Almox. defensivos (10 lotes) | ~30 + 10 seleções numa lista de 27 + 10 campos | ~12 + 10 campos | Contar local |
| Aprovar ajuste | 1 de qualquer pessoa, gravado "Ana" | **2** da gestora (+1 do Ver como) | abre em Faça contagens |
| SAF (demanda pronta) → envio à Direção | 7 em 5 vistas e 2 telas | **4** em 2 vistas | ~5 s de respostas simuladas nos dois |
| Menu Compras → envio à Direção | 6 | **3** | — |
| Compra dentro da alçada, menu → emitir | 7 (teto 6, PCMS:465) | **4** | — |
| Direção aprova | 1 do comprador | 2 da Direção (+1 Ver como) | papel certo |
| SAF → PC emitido, acima da alçada | 8 | 6 (+1) | — |
| Reprogramar PC atrasado | 7 + 2 campos, só depois de cotar | 3 + 2 campos | versão nova |
| Da O.S. ao item no Estoque | link + troca de seção + procurar | só o link | `#req=` |

Pioras permitidas, com dano nomeado: laudo, devolução digitada, aprovação por outra pessoa (ajuste e consumo acima da custódia).

---

## 9. Testes

### 9.1 Etapa SUP-0: antes de mudar a tela
1. **Linha de base completa** (executado: leitura de `docs/parceria/evidencias/v44-tabelas-05/un-20261005/bateria`, base `0cf6f90`; refazer no `884620c` com `docs/parceria/evidencias/v44-tabelas-05/un-20261005/00-bateria.sh` e guardar o hash). Por log: nome, contagem, código de saída e IDs.
   - Saem com código ≠ 0: componentes ajustes (#26), componentes interação (#10 PA, #14 famílias), etapas complemento (1), etapas desktop (1), cal01 (2), os_cenario (14/15).
   - **Saem com 0 mesmo falhando** (julgar pela linha RESULTADO/FALHAS): partest (T1-C), consumo_divergente (18/19), cadp_fix (11/15), cotest (CO-01 a CO-04 e CO-02det, "faixa com 7 etapas"), getest (GE-04 `pc088_unico`), vetest (OF-103), testes_pedido (T05).
   - Varredura 144/144 sem erro; `acoes_duplicadas.py`: 0 de 144 páginas com ação repetida.
2. **Navegação por nome** nos testes do EST: função nova `ir_secao(nome)` em `est_lib.py` (hoje `etapa(i)`, `:35`). **Não** mexer no `IR_ETAPA` compartilhado (`comp_lib.py:13-18`), que a SAF-única reescreve.
3. **Captura de medida** a 390 e 360 de uma grade de 2 e de 3 colunas na casca atual (quantas linhas e colunas cabem).
4. **Verificador de duplicata** (PADRÃO v3.1 item 2): estender `acoes_duplicadas.py` para agrupar por verbo + ID alvo, contando linha e painel, com página-controle que tem a duplicata e precisa reprovar (molde do caso 29b do `acao_unica_test.py`). Combinar com a reserva V44-ACAO (RETOMADA:243) se ainda ativa.
5. `sup_unit.js` e `sup_atrito_test.py` no "antes", com os vermelhos registrados, não escondidos.

### 9.2 Novos (todos saem com código ≠ 0 quando falham)
**`sup_unit.js`** (node, sobre `cenario.js` + `est.js`, com `E2` de um JSON gerado de `_dados_js()`; molde `quantidade_test.py:155-212`). Negativos e positivos:
- N1: `cenEntregar` à REQ-036/OS-0420 (Impedida) é recusado. Hoje entrega 3.640 kg (executado).
- N2: entrega acima da reserva própria é recusada, mesmo com livre no lote (caso montado: REQ-035 com `res0` = 160 L, própria 0, livre 480 L → 15 L recusados); com a semente nova (própria 15 L), os 15 L saem.
- N2b: entregar 15 L à REQ-035 deixa a reserva própria da REQ-039 em 65 L (hoje cai para 50, executado).
- N3: `estEntregarReq` com um item inválido não grava nada (`c.rev`, lotes e `c.movs.length` iguais).
- N4: a mesma chave duas vezes → recibo, sem movimento; `ver` diferente → conflito, sem movimento.
- N5: liberar parcela sem laudo é recusado; reprovado mantém; lote vencido não aprova. **N5b:** devolução bloqueada de 100 kg (REQ-031) + NF com 2.000 kg em quarentena no M26-07: o laudo da NF libera 2.000 kg e mantém os 100 kg (hoje libera 2.100, executado).
- N6: sobre `estAprovar(c,'INV-2609',por)`: `por='Rui (almoxarife)'` (contou, sem papel de gestor) é recusado e `c.movs` não muda; `por='Ana (gestora)'` aplica −600 kg e grava "Ana", sem revisão pendente; Ana contou e aprova → vale com "Decisão do gestor registrada · revisão independente pendente (Ana contou e decidiu)" (§0.3). **N6b:** o contador ainda consegue "Recontar".
- N7: recusar relato sem motivo, ou com motivo só de espaços, é recusado.
- N8: devolução acima da custódia é recusada.
- N9: aceite com falta > 0 (80 L na REQ-035, custódia 65) pelo próprio almoxarife que enviou é recusado; pela gestora, baixa 15 L e grava "Ana".
- N10: contagem de 7.900 kg no N26-03 grava o ajuste com `afeta`, e nenhuma mensagem contém "8.000".
- N11: toda função grava o `por` recebido; sem `por`, "Rui (almoxarife)".
- N12: rótulo da REQ-021 traz "1.850 bandejas" e "400 sacos".
- F5 (CTL-2, executado 09/10): turno do app retido por duplicidade (mesma data de um dia já somado pela web) não vira linha, contador nem item no Estoque; "mesmo turno" o mantém fora; "outro turno" o traz uma vez só, "Aguardando gestora".

**`est_fila_test.py`** (navegador):
- 4 seções (eram 6); contadores da Santa Rita "3 a entregar · 1 sobra", "1 nota · 1 laudo", "1 a contar · 1 ajuste"; Lagoa Grande "1 a entregar"; Todas "4 a entregar · 1 sobra". Trocar a fazenda muda linhas e contadores; Boa Vista mostra "Ver Santa Rita".
- Ordem das linhas "Com ação" (Santa Rita e Todas, §3).
- Abertura pelo papel: Rui → Atenda requisições; Paula → Faça contagens (INV-2611); Ana → Faça contagens (INV-2609); `c.rev` igual.
- Endereços: `#sec` com apelidos de BEN e PCM; `#sec=xyz` abre sem erro; `#req=REQ-031` abre o painel; `#os=` abre a linha sem requisição. **Navegar não executa:** `c.rev` e `c.movs.length` iguais.
- Nenhum `button` de comando dentro de `[role=row]` em `g_req`, `g_rec`, `g_cnt`, `g_lot`, `g_mov`.
- Entregar REQ-021 com Renato em 2 toques; "Separe:" com lote e local visível **antes** do toque.
- **Toque duplo:** dois cliques em 100 ms no "Entregar REQ-039" entregam só a REQ-039; a REQ-040 fica intacta.
- REQ-040 mostra "Reserva parcial · faltam 3.400 kg" e entrega os 8.000 kg reservados.
- Linha "Adjuvante · fora da requisição" (CC-302) com Conciliar.
- Devolução em branco recusa salvar vazio. Laudo aprovado e reprovado.
- **Contagem cega:** o saldo não aparece em `g_cnt`, no formulário, no filtro da coluna (migrar `verif_ce_est.py:69`), nas mensagens nem em Saldos para o contador. A causa é pedida no mesmo painel.
- Ver como Paula → a trilha grava Paula; Ver como não muda `c.rev`.
- 390 e 360: a página não rola de lado; Requisição e Situação à vista; no painel, "Separe:" e a primária sem rolar.

**`cmp_fila_test.py`** (navegador): a lista abre com a SOL-2026-07 "A cotar"; o detalhe abre na fase; "Enviar 15 convites"; as respostas trocam para Decida sem clique; alçada numa linha; **Ana não vê "Aprovar e emitir" acima da alçada; a Direção vê e abre com "Aguardando você"**; devolver e recusar exigem motivo e recusa não emite PC; `sig` invalida; navegar não aprova (`cmptest.py:128`); reprogramar guarda a promessa anterior; nenhum botão de comando em linha; o PC emitido aparece no formulário "Registrar NF recebida" (depois do 1c).

**`sup_atrito_test.py`:** as tarefas do §8 no `884620c` e depois de cada PR, com cliques e campos guardados.

### 9.3 A adaptar (troca a forma; mantém a regra)

| Arquivo | Muda | Fica |
|---|---|---|
| `cmptest.py` | jornada lista → Cote → Decida → Direção; nomes de etapa (`:27, 36, 41-55`); `&etapa=6` → `passo=demanda`; href exato (`:140`) → prefixo | homologado, canal, justificativa, `sig`, motivo, sem duplicata, navegar não aprova |
| `esttest.py`, `est_cenario_test.py`, `est_fix1_test.py`, `est_fix2_test.py` | seção por nome (`ir_secao`); painel; devolução digitada; laudo por parcela; ajuste pela gestora; textos de `E.k()` (est_fix1 `:139, :166`; est_cenario `:37`; est_fix2 `:237`) viram contadores | saldo, reserva própria, custódia, NF duplicada, lote vencido, O.S. impedida, contagem cega, recontagem, efeito uma vez |
| `tabelas_est_test.py` | mapa de colunas (`:43-49`); `range(1, 7)` (`:70, :119`) → 4 seções e 2 modos | uma variável por coluna, unidade na célula, ordenar, filtrar, sem rolagem da página |
| `consumo_divergente_test.py` | `etapa(2)/(3)` (`:20-22`) → `#req`; motivo digitado no lugar do texto fixo (`:111`); aceite acima da custódia pela gestora | os casos CC-301 e **CC-302** (caso 5, `:100-111`); regressão do selo da O.S. em conferência |
| `saf_cmp_continuidade_test.py` | `passo=demanda`; "2 Confira a demanda" (`:82, :92`) → detalhe na fase | uma SOL por safra, mesmo valor, paridade CAL-01 |
| `acao_unica_test.py` (`:147`, `:165`, casos 27 e 31), `componentes_test.py:91`, `etapas_celular_test.py:104` | listas de seções e rótulos; **depois do merge da SAF-única**, que reescreve os mesmos arquivos | uma primária, navegar não executa, sem duplicata, 360 px |
| `os_cenario_test.py:54, 74`, `map_aprov_test.py:38`, `map_decisoes_test.py:67, 80`, `testes_pedido.py`, `irr_fluxo_test.py` | href exato → prefixo `EST.dc.html#req=`/`#lote=` | devolução libera o encerramento; o Mapa reflete; continua proibido o link SU-07 |
| `mbtest.py:92` | sai o MB-05det | — |
| `verif_ce_est.py`, `verif_ce_cmpA.py`, `verif_ce_cmpB.py` | migrar para a bateria: lote existente com outra validade (`verif_ce_est.py:35`; **migrado em 10/10**: `sup_unit` N13 e `esttest` parte 1, DEC §1.31), filtro que não revela o saldo (`:69`), recontagem com outro contador (`:75`), PC no dia exato da falta, motivo só com espaços | FEFO continua lacuna (`cenario.js:42`) |
| `sutest.py`, `app_*` | não mudam (telas SU ocultas; assinaturas `cen*` compatíveis, `por` opcional) | estorno, concorrência, app |

---

## 10. PRs pequenos e ordem (proposta; a ordem entre frentes é do Codex)

| PR | Branch | Conteúdo | Arquivos | Entra depois de |
|---|---|---|---|---|
| **Etapa SUP-0** | `claude/v44-sup-00` | §9.1 inteiro | testes novos, `est_lib.py` (`ir_secao`), `ferramentas/acoes_duplicadas.py` | pode correr já, em paralelo |
| **Etapa SUP-1** | `claude/v44-sup-01` | endereços e apelidos; contadores neutros (só `ui37.py` + `PREVALS`); Ver como (abertura e rótulo, sem decisões); filtro de fazenda real; links da O.S., do Mapa e da irrigação; EST → `#OS-`; bloqueio da conferência na O.S. (`:242-244, 287-291`); comparação por prefixo | `processo_estoque.py`, `ui37.py`, `processo_os.py`, `inicio.py`, `irrigacao_estado.js`, testes de href | #43 e #44; **SAF-única** (por `acao_unica_test.py` e `etapas_celular_test.py`). O BEN-1c reaproveita o `#sec` |
| **Etapa SUP-2a** | `claude/v44-sup-02` | Atenda requisições (`g_req`, painel, "Separe:"); `cenMudar` com `cmd` (G04) para entregar, devolver e conciliar; travas no `cenEntregar`; semente `res0` + `CEN0.v`; `est.js`; `estEntregarReq` (M14); `por` em todas as funções; devolução em branco; recusa com motivo; consumo acima da custódia pela gestora; linhas fora/sem requisição; `epk` com unidade do item; rótulo do painel | `cenario.js`, `cenario.py`, `processo_estoque.py`, `est.js` (novo), `engine.py` (só `:1286`), testes | Etapa SUP-1 |
| **Etapa SUP-2b** | `claude/v44-sup-03` | Receba e inspecione (parcelas, laudo, Apta calculada, NF contra pedido); Faça contagens (contador no ajuste, `afeta`, causa no painel, Contar local); Confira saldos (lote sem árvore, locais da fonte única, Movimentos, contagem cega na consulta); saída da aba Almoxarife e do MB-05det. CONTROLE-01 itens 1 e 2 | `cenario.js`, `processo_estoque.py`, `est.js`, `mobile.py`, testes | Etapa SUP-2a |
| **PCM 1a → 1b** | PR #45 | sobre a forma nova do EST; o 1b estende `cenMudar` com `cmd`, M06 e M14 para OM, e acrescenta o filtro Natureza no EST | conforme PCMS §11, com as mudanças do §7 | Etapa SUP-2b |
| **PCM 1c-dados** | — | `c.pedidos`, emitir grava no cenário, `cenReprogramarPC` com versões, NF contra pedido | conforme PCMS | 1b |
| **Etapa SUP-3** (= 1c-tela) | `claude/v44-sup-04` | Compras: lista, detalhe Cote/Decida, Acompanhe pedidos, Ver como Direção, SC como linha, nome "Compras", vocabulário único com o SAF, filtro Natureza; saem `g_dem`/`g_apr`/`g2steps` | `processo_compras.py`, `safra.js` (situação), `ui37.py:41` e nomes (PCMS:54), `comp_lib.py` se preciso, testes | SAF-única e PCM 1c-dados |

**Sobreposições declaradas na reserva:** `engine.py` e `g2lib.js` (SAF-única; esta frente só toca `engine.py:1286` e não toca `g2lib.js`); `acao_unica_test.py`, `etapas_celular_test.py`, `comp_lib.py`, `cmptest.py`, `saf_cmp_continuidade_test.py` (SAF-única: depois do merge dela); `cenario.js`, `cenario.py`, `processo_estoque.py`, `processo_os.py` (PCM: SUP antes do 1a, ou reordenar pelo Codex); `acoes_duplicadas.py` (V44-ACAO).

**Validação do proprietário:**
- Estoque depois da Etapa SUP-2b. Tarefa curta: "entregue a REQ-039, receba a sobra da OS-0417 e aprove o ajuste do INV-2609 como Ana".
- Compras depois da Etapa SUP-3 e do CONTROLE-01 item 10. Tarefa curta: "cote e mande à Direção a SOL-2026-07; aprove como Direção".
- Cada uma exige a bateria sem falha nova contra a linha de base e o parecer do Codex (AGENTS §3.1-3.2).

---

## 11. Aceite

| ID | Critério | Comando |
|---|---|---|
| AC-SUP-01 | Estoque com 4 seções (eram 6) e Compras com 2 seções + detalhe (eram 6 etapas numeradas); nenhuma faixa de etapas; nenhum botão que só troca de tela | `python3 est_fila_test.py && python3 cmp_fila_test.py` |
| AC-SUP-02 | Contadores por fazenda do cenário inicial; abertura pelo papel do Ver como | `est_fila_test.py`, `cmp_fila_test.py` |
| AC-SUP-03 | Endereços do §2.2 abrem o lugar certo, com `c.rev` e `c.movs.length` iguais | idem |
| AC-SUP-04 | Entregar inteira: tudo ou nada; mesma chave não repete; toque duplo entrega uma REQ; O.S. impedida e entrega acima da reserva própria recusadas pela função; reserva de outra O.S. intacta | `node sup_unit.js` (N1-N4, N2b) + `est_fila_test.py` |
| AC-SUP-05 | Devolução digitada; recusa com motivo não vazio; consumo acima da custódia decidido por outra pessoa; CC-301 e CC-302 com linha e ação | `sup_unit.js` (N7-N9) + `consumo_divergente_test.py` |
| AC-SUP-06 | Quarentena só sai por laudo, parcela por parcela; reprovado e vencido continuam bloqueados | `sup_unit.js` (N5, N5b) |
| AC-SUP-07 | Quem contou sem o papel de gestor não aprova; o gestor que contou decide com revisão independente pendente gravada; recontar continua livre; a trilha grava quem aprovou | `sup_unit.js` (N6, N6b, N6t) |
| AC-SUP-08 | Contagem cega em formulário, linha, filtro, mensagens e Saldos; contagem abaixo do reservado é gravada | `sup_unit.js` (N10) + `est_fila_test.py` |
| AC-SUP-09 | Comprador não registra a decisão da Direção; Ver como rotulado "simulação" e gravado em todo movimento | `cmp_fila_test.py`, `sup_unit.js` (N11) |
| AC-SUP-10 | Reprogramar acrescenta versão; pedido emitido aparece para receber | `cmp_fila_test.py` |
| AC-SUP-11 | Uma variável por coluna, unidade na célula, até 7 colunas de dado | `tabelas_est_test.py` adaptado + bloco CMP |
| AC-SUP-12 | 390 e 360 sem rolagem lateral da página; Identificação e Situação à vista; "Separe:" e primária no painel sem rolar | `etapas_celular_test.py`, `est_fila_test.py` |
| AC-SUP-13 | Uma primária por tela; nenhum comando em linha; verificador estendido com controle negativo reprovando | `acao_unica_test.py v3`; `python3 ../ferramentas/acoes_duplicadas.py . out.json` |
| AC-SUP-14 | Atrito medido antes e depois em todas as tarefas do §8; nenhuma piora sem dano nomeado | `sup_atrito_test.py` |
| AC-SUP-15 | Bateria completa sem falha nova contra a linha de base do §9.1 | script da bateria 2d sobre a base nova |
| AC-SUP-16 | Filtro de fazenda muda linhas e contadores no Estoque (AC-72-10) | `est_fila_test.py` |
