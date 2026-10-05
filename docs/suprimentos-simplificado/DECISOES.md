# Decisões · Suprimentos simplificado v2

Abreviações e rótulos: os mesmos da `ESPECIFICACAO.md`. Tudo aqui é **especificado**; o que foi conferido rodando script está marcado **executado**.

## 1. Assumi (decisões técnicas e de produto delegadas aos agentes; o Codex revisa)
1. **Estoque em 4 seções** (Atenda requisições, Receba e inspecione, Faça contagens, Confira saldos), não numa fila mista: a fila mista fere "uma variável por coluna" ("Com quem" e "Quantidade" mudam de sentido por linha).
2. **Compras: lista + detalhe aberto pela fase do estado + Acompanhe pedidos.** A safra vira Origem e filtro. Confirmado pelo SUPv2 65.7: cotação, pedido e recebimento "não [são] avanços artificiais… por setas/etapas" (SUPv2:89).
3. **A linha identifica, o painel resolve.** Nenhum botão de comando dentro de `[role=row]`; a primária fica no rodapé do painel do registro, com rótulo que confirma o quê, quanto, lote e para quem. Fonte: PADRÃO:12-16 e :69-71. Custa 1 toque a mais que a v1 para REQs que não estão no topo (2 em vez de 1), e elimina a duplicata e o toque duplo que caía na REQ seguinte.
4. A ≥1024 px, o painel da 1ª linha com ação abre sozinho (abrir não executa); a ≤640 px a página abre na lista.
5. **"Entregar REQ inteira" em 1 toque no painel**, sem confirmação extra (PRD:9365, 9367), com "Separe:" (lote, validade, local, embalagem) acima do botão e tudo ou nada dentro de um `cenMudar`.
6. **Repetição pelo `cenMudar` com `cmd`** (PCMS-G04): chave criada ao abrir o painel; `ver` = versão de cada item da REQ (`it.ver`, PCMS:190); nunca o `c.rev` global (PCMS:364). Nasce no SUP-2a e o PCM 1b estende para OM.
7. **Entrega só do reservado** (72.3 item 2, PRD:12234): `cenEntregar` limita à reserva própria e baixa só ela. A semente passa a refletir a reserva da liberação (`res0`); o F26-02 vai a 80 L reservados (65 da REQ-039 + 15 da REQ-035). `CEN0.v` sobe para o próximo número livre e ganha `recibos:{}`.
8. **Quarentena por parcela** (`l.quar=[{doc,qtd,motivo}]`); o laudo libera só a parcela do documento. Lote salvo antes vira uma parcela "anterior".
9. **Contagem sempre gravada.** Abaixo do reservado ou bloqueado, o ajuste leva `afeta` e vai à gestora, que vê as O.S. atingidas; nenhuma mensagem mostra quantidade do sistema ao contador.
10. **Ajuste e consumo acima da custódia decididos por outra pessoa.** `aj.contador` e quem enviou o consumo ficam gravados; a função recusa a mesma pessoa só ao aprovar; recusar ou recontar continua livre.
11. **Ver como** (simulação, rotulado): define a abertura, habilita só as decisões do papel e é o `por` gravado em todo movimento. Não filtra a fila. `localStorage` em try/catch; nunca muda `c.rev`.
12. **Abertura pelo papel:** almoxarife → 1ª seção com pendência (Atenda requisições → Receba e inspecione → Faça contagens); contador com contagem atribuída → Faça contagens; gestora → 1ª seção com "Aguardando gestora"; Direção → Atenda solicitações com "Aguardando você".
13. **Filtro de fazenda real no Estoque** (DEC-2609-11, AC-72-10), pela fazenda do local (`dados_cad.LOCAIS`) e da O.S. (`o.faz`). Contadores esperados (executado sobre o cenário): Santa Rita 3 a entregar · 1 sobra; Lagoa Grande 1; Todas 4 · 1.
14. **Locais da fonte única** `dados_cad.LOCAIS` estocáveis da fazenda do filtro; o cenário só informa o saldo.
15. **Natureza** (SUPv2 65.7) como filtro rápido sobre os mesmos IDs, visível só com mais de uma natureza nas linhas; padrão "Todas" nas filas de trabalho, com Insumos agrícolas em 1º. Entra quando a 2ª natureza chega (PCM 1b no EST; SUP-3 na CMP).
16. **Receba e inspecione só com trabalho do almoxarife** (nota prevista, parcela aguardando laudo, compra sem pedido); o estado do pedido fica só em Acompanhe pedidos; "Registrar NF recebida" lista os PCs abertos.
17. **Situações novas na fila:** "Reserva parcial · faltam X" (com link ao pedido ou à solicitação) e "Lote insuficiente" (só "Entregar parte"); linhas "fora da requisição" e "sem requisição" para o consumo em conferência.
18. A 390/360 a grade promete Identificação e Situação à vista; o resto vai ao painel. **A casca (menu lateral de 68 px) não muda nesta frente.** Quantas linhas cabem é medido no SUP-0.
19. Contador de seção em cor neutra num slot novo de `secoes_state` (`ui37.py`), preenchido no `PREVALS`; `g2lib.js` não é tocado.
20. Testes do EST navegam por `ir_secao(nome)` novo em `est_lib.py`; o `IR_ETAPA` compartilhado (`comp_lib.py:13-18`) não muda nesta frente.
21. A aba Almoxarife do MB-05 e o MB-05det saem do caminho visível como **recorte temporário**, com condição de retorno: a mesma fila em cartões, com as funções do `est.js`.
22. "Aprovar e emitir" para quem tem a alçada, com prévia dos PCs antes do toque que emite; dois registros com horário.
23. Ordem dos PRs: SUP-0 já; SUP-1 depois de #43/#44 e da SAF-única; SUP-2a; SUP-2b; PCM 1a/1b/1c-dados; SUP-3 (= 1c-tela). Proposta: a ordem entre frentes é do Codex.

## 2. Parâmetros do dono, com o padrão que vale até ele decidir (perguntar só na homologação)
| Pergunta | Padrão | Fonte |
|---|---|---|
| Quem aceita consumo acima da custódia | a gestora quando há baixa do lote além da custódia; o almoxarife quando a custódia cobre. **Mudou** em relação à v1 ("o almoxarife, como hoje") para coincidir com a AUD | AUD:235; CMD-50 (revisão v3.10) |
| Quem aprova ajuste ou consumo quando uma pessoa acumula os dois papéis | a gestora; com uma pessoa só, fica registrada uma revisão posterior | PRD 2.1; AUD:235 |
| Laudo para todo lote em quarentena ou só para algumas classes | todo lote | RF-SUP-007 |
| Alçadas reais | valores de demonstração de `dados2.py:705`, que não valem como alçada de produção | RN-043; CF-02 |
| Tolerância de quantidade no recebimento | nenhuma; a diferença vira divergência registrada | DEC-07 pendente, PRD:10252 |

## 3. Pendente
| O quê | Quem | Impede |
|---|---|---|
| Registro do pedido de 05/10 e da nova redação: 71.6 (Compras, Estoque, Orientação), UX-03 (Entrada, Regra essencial, Etapas, fluxograma e `fluxos_v3_9.json`), 72.3 item 2, DEC-2609-11/AC-72-10, MB-05/SU-07/SU-09 como recorte temporário; uma redação que cubra também o SUPv2 (patch sobre v3.11) | Codex escreve, Claude revisa | integração de qualquer PR de tela |
| Mudanças na PCMS: M06 (contagem gravada, não recusada), M14 e G04 nascendo no SUP-2a, `CEN0.v` como "próximo livre", equivalência de etapas → seções nos aceites | autor da PCMS; Codex revisa | reserva do SUP-2a |
| Ordem entre frentes (SAF-única, TABELAS, PCM, BEN, CONTROLE-01) e re-corte do PCM 1c em dados e tela | Codex | SUP-1 em diante |
| Benchmark de 5 referências do módulo, com fonte oficial e data (AGENTS §3.3). Não pesquisado. O SUPv2 traz SAP e Oracle só para reposição | Codex (produto) | aceite humano |
| Nova expectativa do E11 (BEN:856): `aria-current` em "Atenda requisições" e filtro "Sobra a receber" | frente BEN | BEN-1c |
| Tabela grupo → natureza em `dados_cad.py` | PCM 1b | filtro Natureza |
| CONTROLE-01 item 10 (`cal01.js:14`) | frente CONTROLE-01 | levar a Compra ao proprietário |

## 4. Revisão aplicada
A revisão veio em três lentes com IDs repetidos; aqui: **C** = código, **D** = dono, **K** = contrato. Cada achado foi conferido no código ou rodando o script indicado antes de decidir.

| ID | Grav. | Achado (curto) | Decisão | Onde na v2 |
|---|---|---|---|---|
| C-R01 | alta | Um laudo libera a quarentena de outro documento no mesmo lote | **Aplicado.** Executado `rev_check.js` d1 (2.100 kg liberados de uma vez). Quarentena por parcela; laudo por parcela; N5b | ESP §0.2, §3 g_rec, §6; N5b |
| C-R02 | alta | Trava "quem contou não aprova" sem o contador no ajuste; N6 inexecutável; recontar quebraria | **Aplicado.** Executado `rev_check.js` a1-a3 e `rev/n6.js`. `aj.contador`; trava só ao aprovar; N6 sobre `estAprovar` com E2 de `_dados_js()`; N6b | ESP §0.2, §6; N6, N6b |
| C-R03 | média | `cenEntregar` baixa a reserva de outra O.S. | **Aplicado.** Executado `rev_check.js` c2 (65 → 50 L). Baixa só a reserva própria; N2b | ESP §0.2, §6; N2b |
| C-R04 | média | Contagem abaixo do reservado mostra o saldo e impede registrar perda | **Aplicado.** Executado `cont_check.js`. Contagem sempre gravada, ajuste com `afeta`, mensagem sem número; N10. Conflita com a frase da PCMS-M06 (PCMS:270), que passa a ser mudança a registrar | ESP §0.2, §6, §7; N10; DEC §3 |
| C-R05 | média | Consumo fora da REQ ou sem REQ sem lugar na fila | **Aplicado.** Linha filha "fora da requisição" e mãe "sem requisição"; `#os=`; CC-302 mantido | ESP §3 g_req, §2.2, §9.3 |
| C-R06 | média | N7 exige mudar `cenConciliar`, listado como "fica" | **Aplicado.** Executado `rev_check.js` b1-b2. `cenario.js:212` em "muda"; `consumo_divergente_test.py:111` adaptado | ESP §0.2, §9.3; N7 |
| C-R07 | média | Filtro de fazenda sem PR, AC nem teste; contadores esperados errados | **Aplicado.** Filtro real no SUP-1; contadores por fazenda; AC-SUP-16; locais de `dados_cad.LOCAIS` | ESP §0.2, §2.2, §9.2, §10, §11 |
| C-R08 | baixa | Ver como só grava pessoa no laudo e no ajuste | **Aplicado.** `por` em todas as funções, padrão Rui; N11 e caso "Ver como Paula" | ESP §0.2, §2.2, §6 |
| C-R09 | baixa | Rótulo da REQ-021 sem embalagem (`epk` só kg/L) | **Aplicado.** Executado `epk_check.js`. `eemb` aceita a unidade do item; N12 | ESP §0.2; N12 |
| C-R10 | baixa | Três imprecisões: EST já sem número; ordem do layout; fonte do M26-07 | **Aplicado.** AC-SUP-01 "4 seções (eram 6)"; ordem fixada por fazenda no teste; fonte `dados2.py:724` | ESP §2.1, §3, §5, §11 |
| D-R01 | alta | Toque duplo no botão da linha entrega a REQ seguinte; primária repete a linha | **Aplicado com ajuste.** Linhas sem comando; primária no painel do registro; comprovante no mesmo registro; chave + `ver` por item. **Recusado** o uso do `c.rev` como versão (conflito falso, PCMS:364) e o congelamento da ordem da grade (sem comando na linha, não protege dano) | ESP §2.3, §4.3; teste de toque duplo |
| D-R02 | alta | 390 px promete o que a casca atual não comporta | **Aplicado, opção (b) adaptada.** Conferido na captura `q_celular_depois_EST_390.png`. Grade a ≤640 px com Identificação e Situação; ação no painel; linhas medidas no SUP-0, não prometidas. **Recusada a opção (a)** (menu ☰): muda a casca de todas as telas; vai para FORA-DE-ESCOPO | ESP §2.4, §9.1 item 3, AC-SUP-12 |
| D-R03 | média | Trabalho da Lagoa Grande dentro de "Santa Rita" | **Aplicado** (mesmo do C-R07) | idem C-R07 |
| D-R04 | média | Falta da O.S. some com o corte do Detalhe; "Entregar inteira" recusa sem aviso | **Aplicado.** Executado `v2_chk.js` (11.400 × 8.000 kg). Situações "Reserva parcial · faltam X" e "Lote insuficiente"; painel com pedido, reservado e falta. "Reservar complemento" (CMD-44) fica fora: não existe hoje | ESP §3 g_req; FORA |
| D-R05 | média | Rótulo sem lote, validade e local | **Aplicado.** Linha "Separe:" por item acima da primária; lote no rótulo; teste confere antes do toque. Validade do F26-02 corrigida para 03/2028 (executado), não 12/2027 | ESP §2.4, §4.3 |
| D-R06 | média | Exemplo principal entrega sem reserva | **Aplicado, caminho A.** Executado `reg_entrega.js` e `rev/r35.js`. Semente com `res0`; `cenEntregar` limitado à reserva própria; N2 reescrito | ESP §0.2, §6; N2 |
| D-R07 | média | Abertura igual para todos os papéis | **Aplicado.** Abertura pelo papel do Ver como; Direção com "Aguardando você"; testado com `c.rev` igual | ESP §2.2; §9.2 |
| D-R08 | média | SUP v2 não lido; faltam recortes por natureza | **Aplicado em parte.** Lido `com_5974202396.md`. Filtro Natureza; Situação "Conferir serviço" reservada; corte de etapas citado como apoio (SUPv2:89); redação única do 71.6 no registro. Serviço com medição, bem/ativo e ação em lote entre documentos vão para FORA-DE-ESCOPO (sem dados no protótipo). Item "não lido" sai dos pendentes | ESP §0.1, §2.2; DEC §1.15; FORA |
| D-R09 | baixa | O mesmo PC em duas grades | **Aplicado.** g_rec só com trabalho do almoxarife; PCs no formulário "Registrar NF recebida" e em Acompanhe pedidos | ESP §3, §5 |
| D-R10 | baixa | Lista e Kanban da O.S. continuam dizendo "Sobras a receber" na conferência | **Aplicado.** `processo_os.py:242-244` com os três casos; regressão no `consumo_divergente_test` | ESP §0.2, §7 |
| K-R01 | alta | Primária "da 1ª linha" duplica o botão da linha; verificador cego | **Aplicado** (mesmo desenho do D-R01). Verificador estendido para verbo + ID alvo com controle negativo; teste "nenhum comando em `[role=row]`" | ESP §2.3, §9.1 item 4, AC-SUP-13 |
| K-R02 | média | REQ-035 sem reserva contraria 72.3 item 2 | **Aplicado** (mesmo do D-R06); a REQ-035 continua exemplo porque a semente passa a ter a reserva | ESP §0.2, §6 |
| K-R03 | média | Conciliação acima da custódia sem independência | **Aplicado.** "Enviar à gestora" quando falta > 0; outra pessoa aprova; `por` gravado; N9; padrão do §2 alinhado à AUD:235. Executado `rev/conc.js` (545 → 530 L por "Rui") | ESP §4.1, §6; N9; DEC §2 |
| K-R04 | média | N6 inexecutável; recontagem quebraria | **Aplicado** (mesmo do C-R02) | N6, N6b |
| K-R05 | média | PCM 1b reescreve `cenEntregar`; "implementa-se uma vez" falso | **Aplicado, opção A.** O SUP-2a nasce com `cenMudar(self, fn, cmd)`, M06 e M14; o 1b estende para OM. Mudança registrada como pendência da PCMS | ESP §0.2, §4.3, §7, §10; DEC §3 |
| K-R06 | média | SUP v2 não conciliado | **Aplicado em parte** (mesmo do D-R08) | idem D-R08 |
| K-R07 | média | LOCAIS "do cenário" contradiz §7, BEN e PCMS | **Aplicado.** Fonte única `dados_cad.LOCAIS` estocáveis, filtrados pela fazenda (conferido `dados_cad.py:135-138`, 10 locais) | ESP §0.2, §3 g_lot |
| K-R08 | média | SUP-0/SUP-1 tocam arquivos reservados pela SAF-única | **Aplicado.** Conferido SAF-única:51 e :610-616. Contador sem `g2lib.js`; `ir_secao` novo sem mexer no `IR_ETAPA`; SUP-1 depois do merge da SAF-única; sobreposições declaradas na reserva | ESP §0.2, §9.1, §10 |
| K-R09 | média | Registro de impedimento incompleto | **Aplicado.** Conferidas PRD:10370, 11855, 11861, 11879-11890, 1249, 1287, 1970-1978 e `fluxos_v3_9.json`. MB-05 como recorte temporário com dano e condição de retorno | ESP §0.1; DEC §3 |
| K-R10 | baixa | Linha de base incompleta | **Aplicado e ampliado.** Lidos os logs de `docs/parceria/evidencias/v44-tabelas-05/un-20261005/bateria`: além de partest T1-C e componentes #10 e #14, faltavam cotest (CO-01 a CO-04, CO-02det), getest (GE-04 `pc088_unico`) e vetest (OF-103), todos com código 0 | ESP §9.1 |

**Efeito no orçamento de atrito:** o D-R01/K-R01 tira 1 toque de ganho da v1 nas REQs que não estão no topo (Entregar REQ-039: 1 → 2; ainda 3 → 2 contra hoje); o K-R03 acrescenta 2 toques da gestora no consumo acima da custódia; o D-R07 tira 1 toque da gestora no ajuste (3 → 2). Nenhuma outra tarefa do §8 muda.
