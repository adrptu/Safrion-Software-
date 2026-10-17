# DRILL-RECOLHIDO · TAB-12 e TAB-13 (17/10/2026)

```text
ID / resultado útil / persona: DRILL-RECOLHIDO (TAB-12, TAB-13) · toda tabela e cartão abre na visão macro (recolhido) e só mostra a seta onde há o que abrir; Planejar safra › etapa 2 agrupa por fazenda também com uma só · quem usa qualquer lista do protótipo, primeiro o gestor no Planejar safra
Requisitos do PRD e fora do escopo: PRD cap. 74 (DS), padroes-1610 (TAB-08, TAB-11, TAB-12, TAB-13), padroes-1510 (TAB-04); fora: cabeçalho da tela, ds_modulos.py, raia do Kanban da O.S., seções do painel de UM registro, menus, listas suspensas e formulários
Autor / revisor / integrador: Claude / Codex / Codex (regime leve, AGENTS §3.5)
Base (commit ou hashes) / arquivos sob responsabilidade: 7d65025, com a composição ac5cd1d7 incorporada (0b48045) · g2lib.js, engine.py, safra.js, safra_lote.js, areas/*.py listados abaixo, testes listados abaixo
Aceite e comando de verificação: drill_recolhido_test.py e saf_fazenda_recolhida_test.py verdes a 1440 e 390 e vermelhos na 7d65025; bateria pelo impacto sem vermelho novo
Estado / impedimento / próximo passo: candidata verde (ver "Testes"); falta a revisão do Codex e o envio pelo coordenador
```

## Pedidos do proprietário (17/10/2026, literais)

1. Planejar safra › etapa 2 › "Talhões e cultivos": "quando so tem 1 fazenda nao agrupa por fazenda, só quando tem 2 ou mais. corrija."
2. "Por padrão coloque sempre os cartoes e tabelas com drill down recolhido, primeiro usuario tem a visao macro e depois consegue escolher onde precisar detalhar no drill down expandido. Em todas as telas."
3. Esclarecimento: "esse pedido de dril down recolhido por fazenda é em planejar safra etapa 2". Aceite principal: a tabela agrupa sempre por fazenda; cada fazenda começa recolhida, com a contagem e a área; a pessoa expande só a que quer.
4. Com o print da O.S. › Tabela agrupada por Talhão: "em C1 observe que OS do drill down tem também drill down, mas na verdade nao tem. o simbolo de drill down so deve aparecer onde de fato terá um detalhamento drill down".

Regras no DS: TAB-12 e TAB-13 em `docs/design-system/padroes-1610.md`; TAB-04 atualizada em `docs/design-system/padroes-1510.md`.

## O que mudou

### Motor (fonte única, `g2lib.js` e `engine.py`)

- `g2flat` decide a abertura de cada linha (`ab`) só pelo que a pessoa abriu (`st.x`): a seta (clique, Enter, Espaço) e "Expandir tudo". A faixa da fazenda (`r.fgrp`) deixou de nascer aberta.
- Abrem sozinhos, por serem escolha da pessoa: a busca e o filtro de coluna abrem o caminho até o filho que casou; o filtro rápido abre a faixa da fazenda (ele vale nos talhões dela). A seta recolhe esse caminho também (`x[id]=false`).
- A seta, os Cartões (`g2cdVals`) e o "Expandir tudo" leem o mesmo `ab`; antes a seta podia dizer "aberta" com a busca ativa sem os filhos à vista.
- `g2agRows` ("Agrupar por"): os grupos nascem recolhidos a cada novo agrupamento ou nível (antes, abertos).
- `g2caminho` (novo, chamado no `g2open`): abrir um registro pelo endereço ou por uma ação abre os pais recolhidos dele; o resto fica como está.
- `engine.grid` sem o parâmetro `x0` (abertura padrão); `engine.table` também.
- TAB-13: a seta só na linha com filhos (`caretOk`); a folha da árvore guarda o lugar dela (`SETA_VAZIO`) quando há alguma seta à vista; lista sem filhos não reserva espaço; a seta de ir (`seta_ir`, `.g2drill`) saiu da linha. Com seleção (TAB-09), só a seta de abrir vai para a 1ª célula.
- Faixa da fazenda: com ela recolhida, "Planejar talhões livres ›" e "Editar talhões ›" ficam na faixa e passam a ter alvo de toque (`p.alvo`, `--g2-alvo`, 44 px no celular); a 390 a faixa fica mais alta. Antes o alvo tinha 15 px e o `saf_lote` H1 reprovou.
- Cartões (`g2cdVals`): a faixa da fazenda leva o ⋯ (ações) também em Cartões, como na Tabela. Defeito anterior, achado pelo reteste do PR #93 com a faixa recolhida.

### Telas que abriam linhas por padrão (`x0`), todas recolhidas agora

| Tela · grade | Abria por padrão | Papel que continua |
|---|---|---|
| Planejar safra etapa 2 · `g_cult_*` (`safra.js`) | a faixa da fazenda (sempre) e o talhão com parcelas ou pendência (fora do celular) | gravar um cultivo, dividir um talhão, "Planejar talhões livres" e "Editar talhões" abrem só o caminho do que foi gravado (faixa e talhão) |
| Planejar safra etapa 3 · `g_op` | operações e atividades "Com pendência"; com o filtro da Capacidade, tudo | a célula de Capacidade escolhida (filtro da pessoa) abre o caminho até as ocorrências, uma vez por escolha (`xcap`); a seta recolhe |
| Planejar safra · `g_rend_*` (fonte do formulário Rendimento, não desenhada no corpo) | todas as operações e atividades divididas | a nova configuração abre o caminho dela (`rendAfter`) |
| Planejar safra · "Editar talhões" (`safra_lote.js`) | todos os talhões divididos depois de gravar | abre a faixa da fazenda gravada |
| Cadastros · CD-01 `g_tal` (fazendas), CD-01det `g_parc` (safras abertas), CD-02 `g_cv` (culturas), CD-08 `g_rend` (operações), CD-06 `g_itm` (grupos de itens, `cad_produtos_estrutura.py` e `cadastros.py`), CD-07 `g_dim` | todos os grupos | gravar um item abre o pai dele; o filtro rápido em chips abre o pai com filho que passa (`cadQfX`) |
| Agronomia · AG-01 `g_vis` (agrupamento de visitas) | todos os grupos | — |
| Estoque (EST) · saldos por lote `g_lot` | todos os itens | — |
| Produção · PROD `g_lot` (produtos) e COLH `g_tal` (culturas) | todos | o endereço do lote (`PROD.dc.html#<lote>`) abre o produto dele (`g2caminho`) |
| Vendas · PCOM `g_of` (produtos) | todos | — |
| Compras (CMP) · `g_ent` (pedidos da compra aprovada), `g_dem`, `g_conv`, `g_cmp` (grupos e o item de maior valor), `g_apr` | todos | os toques que abrem e recolhem o grupo (`tog`) |
| Irrigação · IR-02 `g_ag` (captações) | todas | — |
| Gestão · GE-05 `g_rec` (clientes) | todos | — |

### Expansores próprios das telas

| Onde | Antes | Agora |
|---|---|---|
| Manutenção · blocos do ativo | abria o da situação (leitura suspeita, situação, achados ou o que vence) | todos recolhidos, com o resumo |
| Manutenção · blocos da ordem (painel de UM registro) | abria o da fase (Janela e equipe, Tarefas, Peças, Custo) e Conclusão em execução | sem mudança: exceção, como o painel da O.S. (ver Decisões); `data-secao-registro` |
| Planejar safra · ajuste local do plano | grupos de gatilho e atividades abertos | recolhidos; erro de gravação abre o grupo e a atividade do campo |
| Atividades do plano, serviços do plano e Versões (Manutenção), lotes do CO-06, "Capacidade por mês" | já nasciam recolhidos | sem mudança (conferido no teste) |

## Decisões tomadas sozinho

| Decisão | Por quê |
|---|---|
| Raia do Kanban da O.S. (Agrupar por) continua aberta | Recolhida, a raia mostra só o total ("T2 · 5 ordens"), não a contagem por fase; a visão macro do Kanban são as 5 fases. Critério da tarefa. |
| Seções do painel de UM registro (O.S.) ficam como estão, com `data-secao-registro` | Não são tabela nem cartão; abrem o que faz a ordem andar na fase. Exclusão da tarefa; o atributo marca a exceção para o teste. |
| Blocos do detalhe do ativo (Manutenção) entram | A tarefa os lista; são resumos de listas (situação, o que vence, achados, ordens, leituras, custo): recolhidos mostram a visão macro. |
| Blocos do painel da ordem de manutenção ficam como estavam (exceção, igual ao painel da O.S.) | Primeiro foram recolhidos, como a tarefa pedia. Na composição ac5cd1d7, `ma_revisao` e `ma_correcoes_pm` (que passavam na composição) reprovaram com os blocos recolhidos (brutos `*_m0b48045.log`): concluir uma ordem passava a pedir abrir Tarefas e Conclusão, 2 cliques a mais por ordem, contra o AC-PCM-28 (nenhum total de cliques sobe). Com a exceção, os dois, o `ma_unica` e o `ma_atrito` passam sem mudança de oráculo (`*_omfix2.log`). O painel da ordem é o detalhe de UM registro, o mesmo papel do painel da O.S., que a tarefa deixa fora. A decisão fica para o coordenador confirmar. |
| Ajuste local do plano entra, e o erro de gravação abre o caminho do campo | A tarefa o lista. Sem abrir no erro, a recusa ficaria escondida numa atividade recolhida. |
| Busca e filtro abrem o caminho, mas a seta recolhe | Antes a seta não fazia nada com a busca ativa (o caminho era forçado aberto). |
| O filtro rápido abre a faixa da fazenda; o filtro por fazenda (`ffz`) não | O filtro rápido (Situação) casa nos talhões, dentro da faixa; o filtro por fazenda casa na própria faixa, que fica à vista recolhida, como na busca que casa no pai. |
| `x0` removido do motor em vez de ignorado | Uma fonte só: parâmetro passado por engano quebra o build em Python; no JS, nenhuma tela grava mais `x0`. |
| `_parc_rows` (CD-01det) devolve só as linhas | A segunda saída era a abertura padrão; `tabelas_cad_irr_unit.py` passou a ler a lista (interface, não oráculo). |
| Agrupar por: ao trocar o agrupamento, a abertura volta a vazia | Grupos novos nascem recolhidos; a abertura de antes (de outras linhas) não vale para os grupos novos. |
| TAB-13: folha da árvore guarda o lugar; lista sem nenhuma linha que abra não reserva | O pedido manda alinhar a folha com a linha que tem seta; numa lista plana não há o que alinhar. |
| Atividade do plano e do ajuste local sem insumo continua com seta | O detalhe embutido existe (inclusão de insumo, mensagem de vazio). |

## Oráculos de teste mudados

O que cada teste verifica continua o mesmo; muda só o que a pessoa faz antes de olhar (abrir o que agora nasce recolhido) ou, onde o oráculo contrariava um pedido de 17/10, a regra nova.

| Teste | Antes | Agora | Por quê |
|---|---|---|---|
| `rmenu_alignment_test.js` | a faixa `fz` abria pela abertura padrão (`x0` / faixa nascia aberta) | a sonda abre a faixa como a seta abriria (`st.x = {fz:true}`) | TAB-12; o conteúdo medido é o mesmo (A1 a A7) |
| `tabelas_cad_irr_unit.py` | `_parc_rows` devolvia `(linhas, abertura)` | lê só as linhas | interface: a abertura padrão saiu |
| `saf_lote_test.py` A1, cliques, H1 | "Editar talhões…" no título do bloco (uma fazenda) | "Editar talhões ›" na faixa da fazenda, e o título sem a ação; `abrir_saf` abre a faixa | pedido 1 (agrupa sempre por fazenda; a ação fica na faixa) e TAB-12 |
| `saf_multi_fazenda_test.py` B1 | grupo da fazenda incluída nascia aberto | chega recolhido, a seta o abre, e os talhões aparecem | TAB-12 |
| `saf_multi_fazenda_test.py` B5 | "uma fazenda sem o nível de grupo" | uma faixa "Santa Rita" recolhida; a seta abre os 8 talhões | pedido 1 |
| `saf_tab_test.py` T6 | T1 (parcelas) e P1 (a conferir) abertos | todo talhão recolhido; `abre` abre a faixa | TAB-12 |
| `saf_fazendas_test.py` F2 | os talhões das duas fazendas à vista ao entrar | a pessoa abre as duas faixas | TAB-12 |
| `tabelas_saf_test.py` etapa 2 | talhões à vista ao entrar | abre a faixa antes de ler | TAB-12 |
| `saf_nav_lib.py` (`rows`) | linhas à vista ao entrar | abre as faixas recolhidas antes de ler | TAB-12 (usado por `saf_revisao`, `saf_totais`, `saf_c01`) |
| `solo_saf_test.py`, `solo_os_test.py`, `solo_rev_test.py` (`ins`) | grupos e atividades do ajuste local abertos | abre a faixa e os grupos e atividades do painel antes de ler as doses | TAB-12 no ajuste local |
| `seta_padrao_test.py` | AJUSTE achava a linha do cultivo direto; mínimos 300 controles e 500 setas | AJUSTE abre a faixa antes; mínimos 150 e 150; espera o giro terminar antes de medir | TAB-12 (menos setas à vista na abertura), TAB-13 (sem as 1.340 setas de ir) e giro no clique |
| `tab_drill_cab_test.py` A | mínimo de 500 setas | 150 | TAB-12 e TAB-13 |
| `ds_1610_test.py` B2 | toda linha que abre o detalhe mostra a seta (TAB-04) | nenhuma linha com a seta de ir | TAB-13 substitui a TAB-04 neste ponto |
| `tabelas_lib.py` (`Grade.linhas`), `tabelas_cad_test.py` (`grupos`), `tabelas_irr_test.py` (`por_grupo`), `tabelas_est_test.py` (seções) | árvores abertas ao entrar | "Expandir tudo" antes de ler | TAB-12; a abertura de antes era tudo aberto nessas árvores |
| `saf_revisao_test.py` B15 | ocorrências da operação "Com pendência" à vista ao entrar na etapa 3 | "Expandir tudo" antes de ler | TAB-12 (a etapa 3 abria a operação com pendência) |
| `tabelas_os_test.py` TF06 | grupos do "Agrupar por" Talhão abertos | "Expandir tudo" antes de ler as O.S. de cada grupo | TAB-12 |
| `cartoes_test.py` M2h | o cartão do grupo (CD-06) nascia aberto e o clique recolhia (menos itens) | nasce recolhido e o clique abre (mais itens); Tabela e Cartões seguem iguais | TAB-12 |
| `ma_rastreio_test.py` F30 | o bloco da situação do ativo aberto | abre os blocos do ativo antes de ler as ordens | TAB-12 nos blocos do detalhe do ativo (os da ordem ficaram como exceção; `ma_unica`, `ma_revisao` e `ma_correcoes_pm` seguem sem mudança) |
| `seta_padrao_test.py` E | Tab e Shift+Tab para o anel de foco | se a seta é o último foco da página (árvore recolhida: o Tab sai do documento), Shift+Tab e Tab | harness: em IR-02 a 390 com a Lagoa Grande, a única captação recolhida é o último foco |
| `drill_recolhido_test.py` C2 (teste novo, ajuste) | a linha do lote à vista | a 390 o painel do lote ocupa a tela (mestre-detalhe): confere a lista por baixo | harness |
| `rev93_reteste_navegador.py` (reteste do PR #93, fora do repositório) | `abre` esperava 4 linhas na tabela da etapa 2 | cópia `rev93_reteste_navegador_tab12.py` nesta pasta abre a faixa da fazenda; o original fica como está | TAB-12; o original reprova na candidata por isso (ver Testes) |

## Testes (executados em 17/10/2026)

Candidata: código da `c33ce7c` (o gerador não muda desde a `a039a11`; depois só testes e documentos), render montado com `SAFRION_DADOS=sintetico`, Chrome headless a 1440 e 390 px. Base: render da `7d65025` (worktree temporária). Brutos em `regressao/<teste>_c33ce7c.log`, resumo em `regressao/_resumo_c33ce7c.txt`; base em `*_base_7d65025*.log` e `*_contraprova_*7d65025.log`. Comando de cada teste: `env CHROME_BIN=… CDP_GL=1 SAFRION_DADOS=sintetico RENDER_DIR=<gen37>/_render python3 -B <teste>.py`, um por vez, com o portão de menos de 4 Chrome.

**Testes novos e contraprova**

| Teste | Candidata | Base 7d65025 |
|---|---|---|
| `saf_fazenda_recolhida_test.py` (etapa 2: 1 e 2 fazendas, 1440 e 390) | 18 ok · 0 falhas | 2 ok · 16 falhas (contraprova: reprova) |
| `drill_recolhido_test.py` (148 telas a 1440 e 390, amostras, busca, endereço, TAB-13) | 66 ok · 0 falhas | 22 ok · 44 falhas (contraprova: reprova) |

**Bateria pelo impacto**

| Teste | Candidata | Base 7d65025 | Leitura |
|---|---|---|---|
| ma_vinculo | 101/101 | — | verde |
| ma_revisao, ma_correcoes_pm (oráculo da composição) | 18/18, 12/12 | — | verdes com a exceção da O.M.; com os blocos recolhidos reprovavam (`*_m0b48045.log`) |
| ma_unica, ma_rastreio, ma_atrito | 23/23, 58/58, 13/13 | — | verdes |
| os_lote, quantidade | 36/36, 16/16 | — | verdes |
| textos_soltos | 267 ok · 1 falha | 267 ok · 1 falha (a mesma) | vermelho antigo: o oráculo D CA-01det espera o texto anterior ao PAINEL-FIXO-1 (d3435d04, já na base) |
| saf_lote, tabelas_saf, saf_tab | 47/47, 24/24, 14/14 | — | verdes |
| saf_c01, saf_fazendas, saf_multi_fazenda | 68 ok, 14/14, 23/23 | — | verdes |
| saf_operacoes, saf_revisao, saf_totais, saf_contexto | 87 ok, 42 ok, 14 ok, 10/10 | — | verdes |
| solo_saf, solo_os, solo_rev | 36/36, 18/18, 22/22 | — | verdes (`solo_os` e `solo_rev` em `_resumo_solo_c33ce7c.txt`) |
| cartoes | 70/70 | — | verde |
| tabelas_os, tabelas_cad, tabelas_est, tabelas_ben | 40/40, 206/206, 34/34, 12/12 | — | verdes |
| tabelas_irr | 98/106 | 98/106 (as mesmas 8) | vermelho antigo TABR-CTX-02 (`tabelas_irr_base_7d65025.log`) |
| tabelas_cad_irr_unit (sem navegador, lendo o `_render`) | 44/51 | 44/51 (as mesmas 7) | vermelho antigo: A1 procura `g_rend` no CD-02 (está no CD-08) e C15–C19 TABR-CTX |
| pa_lista, kanban_raias, visoes2_formas | 24 ok, 9/9, 23/23 | — | verdes |
| tab_drill_cab, ds_1510, ds_1610 | 6 ok, 17 ok, 14 ok | — | verdes |
| paginas_scan | 5 ok (148 páginas) | — | verde |
| seta_padrao | 14 ok · 0 falhas | — | verde |
| `node rmenu_unit.js`, `rmenu_generator_test.py` | OK, OK | OK, OK | verdes |
| `node rmenu_alignment_test.js g2lib.js c93_base_g2lib.js` | 557 OK · 4 falhas | 557 OK · 4 falhas (as mesmas A6) | vermelho antigo |
| `rev93_reteste_navegador_tab12.py` (cópia adaptada) | 44 OK · 0 falhas | — | verde |
| `rev93_reteste_navegador.py` (original, fora do repositório) | erro em `abre` (a faixa recolhida esconde as linhas) | 44 OK | esperado pela TAB-12; ver Oráculos |

## Fotos (Planejar safra › etapa 2)

`antes_saf2_*` no render da 7d65025 e `depois_saf2_*` no da candidata, com 1 fazenda (`1faz`) e 2 fazendas (`2faz`), a 1440 e 390 px (`fotos.py`). Depois: a faixa da fazenda aparece também com uma fazenda só, recolhida, com área e contagem; a 390 a faixa fica mais alta pelo alvo de toque dos dois links.

## Não executado

- `painel_fixo_2_test.py`: verificação pontual do commit 2e94a490; pede a base anterior como argumento e confere que o `x0` do `gestao.py` não mudou, o que esta frente muda de propósito.
- Fora da lista de impacto, não rodados nesta frente: `cada_cd04`, `cada_fix04`, `ocupacao`, `saf_capacidade_simetrica`, `saf_impedimentos`, `ficha_pivo`, `ma_correcoes_om`, `ma_planos`, `galeria.py` e a bateria completa.
- Só emulação de tela no Chrome headless; nenhum aparelho real.
