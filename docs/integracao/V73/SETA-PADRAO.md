# SETA-PADRAO · Seta única de abrir e de ir (TAB-11)

```text
ID / resultado útil / persona: SETA-PADRAO (TAB-11) · uma seta só, fina e cinza, para abrir/recolher e para ir ao detalhe, em todas as telas · quem usa qualquer lista, árvore ou seção do protótipo
Requisitos do PRD e fora do escopo: PRD cap. 74 (DS) e padroes-1610 (TAB-04, TAB-08, TAB-09); fora: lista suspensa (▾ no fim), ordenação do cabeçalho (⇅ ▲ ▼), › de trilha e de texto corrido, › no fim de atalho de texto (BOT-08)
Autor / revisor / integrador: Claude / Codex / Codex (regime leve, AGENTS §3.5)
Base (commit ou hashes) / arquivos sob responsabilidade: c9ffa08 · engine.py, g2lib.js, safra.js, areas/{maquinas,processo_planos,processo_safra,colheita,analise_solo}.py, areas/processo_os.py (só o painel da O.S., _painel), testes listados abaixo
Aceite e comando de verificação: seta_padrao_test.py verde a 1440 e 390 e vermelho na base; regressão sem vermelho novo; galeria olhada
Estado / impedimento / próximo passo: ver "Resultado" abaixo
```

## Pedido

Proprietário, 16/10/2026, com a captura do CD-01 (Fazendas e talhões): "mude o estilo do drill down daquele preto para a setinha mais intuitiva e amigável dos debaixo, melhore ela e implemente como nosso padrão em tudo."

Na captura, o grupo "Santa Rita" tinha o triângulo preto cheio de texto (▾, 13 px, #15201A) e os talhões tinham a seta fina cinza (›, SVG de 14 px, #9AA59E).

## Regra (TAB-11)

Texto completo em `docs/design-system/padroes-1610.md` § TAB-11. Resumo:
- **um desenho:** chevron SVG de 16 px, traço de 1,75 px, cor do texto secundário (#65736A);
- **abrir/recolher:** dentro de um botão nativo com `aria-expanded`; fechado aponta para a direita, aberto gira 90° (120 ms; parado com `prefers-reduced-motion`); nome "Abrir …"/"Recolher …";
- **ir ao detalhe:** a mesma seta, parada; quem navega é a linha;
- **alvo:** 24 px no mouse, 44 px no toque; a seta de ir e a linha sem seta guardam a mesma largura;
- **interação:** hover verde (VIS-02), anel de foco verde de 2 px, Enter e Espaço alternam;
- **sem dica** (TAB-04, 15/10).

**Peça única:** `engine.seta`, `engine.seta_abrir`, `engine.seta_ir`, `engine.SETA_VAZIO`, `engine.SETA_CSS` (HTML) e `g2seta(aberta, nome)` no `g2lib` (estado e nome).

## Decisões tomadas sozinho

| Decisão | Por quê |
|---|---|
| Cor #65736A (texto secundário), não o #9AA59E da seta antiga das filhas | O #9AA59E dá 2,55:1 sobre o branco, abaixo dos 3:1 de componente de interface (WCAG 1.4.11). O #65736A é o token de texto secundário da DS (4,9:1) e continua cinza. |
| Sem dica na seta | A TAB-04 (proprietário, 15/10) tirou a dica da seta: "a seta é óbvia, e a dica cobria a linha de baixo" (`g2dicaTexto` ignora `.g2car`). A dica curta "Abrir/Recolher" pedida na tarefa contraria essa decisão escrita; fica para o proprietário decidir. |
| Nome acessível "Abrir …"/"Recolher …" em toda seta | Antes havia "Expandir …", "Mostrar …" e "Ocultar …" conforme a tela. A TAB-04 já dizia "Abrir …"/"Recolher …". |
| "Expandir tudo"/"Recolher tudo" com a mesma seta | Era um terceiro desenho (setas para cima e para baixo). Agora a seta mostra o estado das linhas: direita com linhas recolhidas, baixo com tudo aberto. |
| Lista suspensa fica com ▾ no fim | TAB-09: lista suspensa não é seta de abrir. |
| Faixa de etapas no estreito ("Etapa 2 de 4 · … ▾") fica | Abre uma folha com a lista (como lista suspensa), não abre conteúdo ali mesmo. |
| › no fim de atalho de texto ("Planejar ›", "Ficha no app ›") fica | É rótulo de navegação dentro do texto do botão (BOT-08), não a seta de linha; fora do escopo pedido. |

## Onde foi aplicado

| Onde | Antes | Depois |
|---|---|---|
| Motor, Tabela e árvore (`engine.grid`, `g2lib`) | botão `.g2car` com o texto ▸/▾ (13 px, #15201A); linha de ir com SVG próprio de 14 px (#9AA59E) | `seta_abrir` e `seta_ir`; nome "Abrir …"/"Recolher …" (`g2seta`) |
| Motor, Agrupar por e Cartões (cartão, filho, grupo) | ▸/▾ de texto | `seta_abrir` |
| "Expandir tudo"/"Recolher tudo" (motor, Agrofit, Atividades do plano) | SVG para baixo/para cima, 13 px, traço 2,6 | a mesma seta, no estado das linhas (`seta_xtog`) |
| Linha sem seta, espaço da seleção (TAB-09) | `span` de 22 px | `SETA_VAZIO`, com a largura do alvo |
| Atividades do plano (Cartões e Tabela) | ▸/▾ de texto; botão próprio de 38 × 44 px | `seta_abrir`; a coluna segue o alvo |
| Planejar safra, "Capacidade por mês" | texto "▸ Capacidade por mês" | botão com `seta()` e o nome (`g2seta-nome`) |
| Planejar safra, ajuste local do plano (grupos e atividades) | ▸/▾ de texto, **sem** `aria-expanded` | `seta_abrir` com `aria-expanded` |
| Manutenção: blocos do ativo e da ordem, Versões | ▸/▾ de texto num `span` | `seta()` no botão da seção |
| Manutenção: serviços do plano | ▸/▾ de texto | `seta_abrir` |
| Qualidade (CO-06), lotes | ▸/▾ de texto, preto | `seta()` no botão do lote |
| Painel da O.S., seções | dois SVG trocados (baixo/direita), 14 px, #15201A | `seta()` no botão da seção |
| O.S., raia do Kanban com Agrupar por (PR #89, AGR-02) | ▸/▾ de texto no botão que recolhe a raia | `seta()` no botão da raia; nome pelo `g2seta` (patch 02b) |
| Laudo de solo (AG-02, até 899 px), "Ver original" | marcador nativo do `summary` (triângulo preto) | `seta()` no `summary`, marcador oculto |
| `engine.openlink` e grupo do `engine.table` (sem uso) | › e ▾ de texto | `seta_ir()` e `seta("g2seta-on")` |

## Números antes → depois

Contagens executadas (scripts em `/tmp/claude-0/seta_scr`, saída abaixo resumida):

| Medida | Base c9ffa08 | Candidata | Como |
|---|---|---|---|
| Triângulos de abrir no código de produto (▸ ▾ fora de comentário e de lista suspensa) | 35 (19 ▸, 16 ▾) em 6 arquivos | 0 | varredura dos arquivos de produto (`engine.py`, `g2lib.js`, `ui37.py`, `areas/*.py`, JS de tela) |
| ▾ de lista suspensa no código (ficam, TAB-09) | 9 | 9 | idem |
| Desenhos de seta para abrir ou ir | 5 | 1 | inventário do código (triângulo de texto, SVG da linha de ir, 2 SVG do painel da O.S., SVG do "Expandir tudo", marcador do `summary`) |
| ▸ nas 148 páginas montadas | 1.198 (148 páginas) | 0 | contagem no HTML do `_render` (inclui o JS embutido) |
| ▾ nas 148 páginas montadas | 995 (148 páginas) | 94 (54 páginas), todos de lista suspensa ou da faixa de etapas | idem |
| Telas com triângulo de texto à vista (A do teste) | 20 a 1440 · 17 a 390 | 0 · 0 | `seta_padrao_test.py` |
| Controles de abrir/recolher sem o componente (B) | 21 telas a 1440 · 18 a 390 | 0 · 0 | idem |
| Setas desenhadas e medidas (C) | 0 com o componente | 1.706 a 1440 (1.340 de ir) · 1.559 a 390 na f1a4720; 1.716 · 1.569 na composição bde9f57 (com as 9 raias do Kanban) | idem |
| Telas com alvo pequeno ou sobreposto (F) | 17 a 1440 (22 px) · 14 a 390 | 0 · 0 | idem |

## Oráculos de teste mudados

O desenho mudou; o que cada teste verifica não ficou mais fraco. Onde o glifo ou o texto antigo era o oráculo:

| Teste | Antes | Agora | Por quê |
|---|---|---|---|
| `tab_drill_cab_test.py` A (seção) | posição do glifo ▸ ▾ › no texto do botão | posição do `.g2seta` (ou do glifo, em versão antiga) | a seta virou ícone; a regra (seta antes do nome) é a mesma |
| `saf_operacoes_test.py`, `rend_multiconjuntos_test.py`, `saf_capacidade_simetrica_test.py` | botão com o texto "▸ Capacidade por mês" (= fechado) | botão "Capacidade por mês" com `aria-expanded=false` | o estado vinha do glifo; agora do atributo |
| `saf_revisao_test.py` | botão "Capacidade por mês ▾" | "Capacidade por mês" | o texto já não existia na base (TAB-09 tinha passado a "▸ Capacidade por mês") |
| `solo_os_test.py`, `solo_rev_test.py`, `solo_saf_test.py` (EXP) | linha que começa por "▸ T1 " e botão com texto "▸" | linha com `.g2car[aria-expanded=false]` e nome "T1 …" | idem |
| `filtros_cultura_test.py` F2 | folha = linha que não começa por ▾/▸ | folha = linha sem `.g2car[aria-expanded]` | o grupo era reconhecido pelo glifo |
| `ma_rastreio_test.py` F18 | literal "Mostrar checklist e peças de" no HTML | `'checklist e peças de '` e `g2seta(` no HTML | o nome vem do `g2seta` ("Abrir …"/"Recolher …") |
| `pa_lista_test.py`, `patest.py`, `acao_unica_test.py` | nome "Mostrar insumos de …" | "Abrir insumos de …" | nome único da TAB-11 |
| `patest.py` (plano novo) | "Mostrar as versões" ausente | "Mostrar as versões" e "Abrir as versões" ausentes | mantém a força da negação com o nome novo |
| `tabelas_saf_test.py` (meta decimal do T2) | `/^T2\b/` no texto da linha | a mesma regra, só em linha sem `.g2car` | a linha-grupo do talhão começava pelo glifo e ficava de fora; agora ficaria dentro. A linha achada é a mesma da base (base 24/24; candidata com o teste antigo cai no mesmo ponto, reproduzido isolado) |
| `solo_os_test.py`, `solo_rev_test.py`, `solo_saf_test.py` (INS e LINHA) | `startsWith('T2 ')` no texto da linha | idem, sem a linha-grupo (`.g2car`) | mesmo caso: o `solo_os` caía no AC-SOLO-20 ("sem ação de insumos T2"); base 18/18, candidata 18/18 |
| `kanban_raias_unit.js` (PR #89, patch 02b do revisor) | `r.seta==='▾'` | nome "Recolher raia …"/"Abrir raia T2 …" e sem o campo `seta` | o glifo saiu do estado da raia |
| `tabelas_lib.py`, `tabelas_cad_test.py`, `tabelas_irr_test.py`, `tabelas_est_test.py`, `tabelas_saf_test.py`, `testes_pedido.py` | `button[aria-label^="Expandir"]` (e "Recolher") | `button.g2car[aria-expanded=false]` (e `button.g2car[aria-expanded]`) | o nome mudou; o T03 do `testes_pedido` podia achar o "Recolher menu" lateral, agora acha a seta |

Sem mudança de oráculo: `ds_1610_test.py` B2 (procura `.g2drill,.g2car`), `ds_1510_test.py` (S4 e C), `cartoes_test.py` M2h (`aria-expanded`), `cadastros_padrao_test.py` P5 (`.g2car` e `aria-expanded`), testes que só tiram o glifo do texto (`replace(/^[▸▾]…/)`).

## Raia do Kanban (código do Codex, PR #89) e pendências

A pendência inicial (a raia do Kanban com Agrupar por tinha um `›` de texto de "descer") mudou com o PR #89 (AGR-02, raias recolhíveis), que entrou na composição antes da TAB-11 (457ef14): a raia passou a recolher e expandir, com `aria-expanded`, o glifo ▸/▾ e o nome "Abrir/Recolher raia …" (ajuste 03 da revisão).

Como recolhe, a raia usa a seta que gira, não a de ir. Na junção com a composição entra o patch ensaiado pelo revisor do #89 (`docs/integracao/V72/kanban-raias-rev-claude/patches/02b-tab11-raia-seta-unica-depois-do-03.patch` da frente do #89, 3 arquivos, +8/−7):
- `areas/processo_os.py` (`osKbRaia` e `_kanban_raias`): `E.seta()` como 1º filho do botão da raia; `expandida` e `lab` pelo `g2seta`; o campo `seta` (glifo) sai;
- `kanban_raias_unit.js`: o oráculo olha o nome ("Recolher raia …"/"Abrir raia T2 …") e a ausência do campo `seta`, não mais o glifo;
- `seta_padrao_test.py`: estado novo `OS.dc.html?view=kanban&ag=onde` (Kanban agrupado), para a varredura alcançar a raia.

Contraprova: o render da junção sem o 02b (6023fb3) reprova a raia (log `seta/seta_padrao_test_contraprova_6023fb3_sem02b_kanban.log`).

Pendência aberta no código do Codex: nenhuma. Nos trechos listados (`cenario.js` do OS-LOTE, `areas/gestao.py` GE-08, `credito_docs.js`, `areas/processo_estoque.py`, BEN) não há seta de abrir/recolher de texto: as tabelas deles são do motor e já recebem o componente; o `›` que aparece neles é trilha ou texto corrido ("Estoque › Confira recebimentos", "abrir caso ›"), fora do escopo.

## Fora do escopo, com motivo

- **Lista suspensa** ("Agrupar por ▾", escolha de alvos do Mapa, `engine.pick`, `engine.pill`): o ▾ fica no fim (TAB-09).
- **Faixa de etapas no estreito** (`ui37._etp_abre`, "Etapa 2 de 4 · … ▾", gira 180°): abre uma folha com a lista, como lista suspensa.
- **Ordenação do cabeçalho** (⇅ ▲ ▼) e "▲ Ordenar crescente"/"▼ Ordenar decrescente".
- **› de trilha** (`ui37` cabeçalho, trilha da Compra de insumos), **separador entre etapas** (CSS da faixa de etapas) e **texto corrido**.
- **› no fim de atalho de texto** ("Planejar ›", "Abrir a ordem completa ›", "Ficha no app ›"): rótulo de navegação do botão (BOT-08). Migrar para a seta é outra decisão.
- **Dica na seta:** não entrou (TAB-04, decisão do proprietário de 15/10). Se ele quiser a dica, a peça é uma só (`g2dicaTexto` hoje ignora `.g2car`).

## Achados fora do escopo (não mexidos)

- Painel da O.S. a 390 px: a tabela "Insumos e doses" espreme a coluna Produto ("Semente / de / soja / 58 / W") e deixa um vão grande acima da linha. Igual na base (foto `os_painel_secoes_390_antes.jpg`).
- A 390 px a 1ª coluna presa do CD-01 é limitada a 45 % da caixa: com o alvo de 44 px o nome perde 8 px ("Rio Verde/GO" quebra em duas linhas; na base cabia).

## Composição e envio

| Commit | O que é |
|---|---|
| `ac8590d` | TAB-11 sobre a c9ffa08 (componente, telas, teste novo, testes que achavam a seta pelo glifo) |
| `f1a4720` | alvo de 44 px no toque sem roubar a 1ª coluna; seção com nome e seta com 44 px; contraprova |
| `c2a20d8`, `02eb624` | documento, galeria e brutos |
| `fb6dc9b` | merge da ponta publicada 47ccc1d (EST-ONDA0, Crédito), sem conflito; enviado a `origin/claude/v44-v73-seta` |
| `705317d` | `tabelas_saf_test` sem a linha-grupo |
| `f42f5c7` | merge da d995ded (PR #88, OS-LOTE), sem conflito; enviado a `origin/claude/v44-v73-seta` |
| `6023fb3` | merge da `claude/v44-v73-seta` (f42f5c7) sobre a composição 457ef14 (PR #89 com os ajustes 01 e 03), sem conflito, branch local `claude/v44-v73-seta-comp` |
| `bde9f57` | patch 02b na raia do Kanban e esta seção |
| `304ce82` | INS e LINHA dos testes de solo sem a linha-grupo |
| `e54bef1` | merge da 6631d58 (457ef14 + docs comp89), só documentação |

## Testes executados

Render montado da árvore limpa de cada commit (`build.py` + `montar_render.py`, dados sintéticos). Navegador: um Chrome meu por vez, só com no máximo 1 principal rodando. Logs em `docs/integracao/V73/seta/` e `docs/integracao/V73/seta/regressao/` (nome `<teste>_<candidata|base>_<commit>.log`).

### Na composição final (render de bde9f57 = e54bef1 nas telas)

| Teste | Comando | Candidata | Base c9ffa08 | Classificação |
|---|---|---|---|---|
| seta_padrao_test (TAB-11) | `seta_padrao_test.py` | 14/14 (148 telas + 10 estados; 387 controles; 1.716 setas, 1 desenho) | 3/14 (reprova A, B, C, D, F e E390) | novo; contraprova ok |
| contraprova da raia | `SPT_SO='OS.dc.html?view=kanban' seta_padrao_test.py` no render 6023fb3 (sem o 02b) | reprova A e B nas 9 raias, 1440 e 390 | — | contraprova ok |
| kanban_raias_test (Node) | `kanban_raias_test.py` | 9/9 | — | verde |
| visoes2_formas_test | `visoes2_formas_test.py` | 23/23 | — | verde |
| tab_drill_cab_test | `tab_drill_cab_test.py` (1440 e 390) | 6/6 | — | verde |
| ds_1610_test | `ds_1610_test.py` | 14/14 | — | verde |
| ds_1510_test | `ds_1510_test.py` | 17/17 | — | verde |
| ds_modulos --catraca | `ds_modulos.py --catraca` | catraca ok | — | verde |
| ds_inventario --catraca | `ds_inventario.py --catraca` | catraca ok (fb6dc9b) | — | verde |
| tabelas_os_test | `tabelas_os_test.py` | 40/40 | — | verde |
| os_cenario_test | `os_cenario_test.py` | 22/22 | — | verde |
| os_lote_test | `RENDER_DIR=<render> os_lote_test.py` | 32/32 | — | verde |
| visoes_test | `visoes_test.py` (comp) | 9/9 | — | verde |
| cartoes_test | `cartoes_test.py` | 70/70 | — | verde |
| pa_lista_test | `pa_lista_test.py` | 24/24 | — | verde |
| cadastros_padrao_test | `cadastros_padrao_test.py` | 44/44 | — | verde |
| cadastros_rev1_test | `cadastros_rev1_test.py` | 19/19 | — | verde |
| tabelas_est_test | `tabelas_est_test.py` | 34/34 | — | verde |
| ma_unica_test | `ma_unica_test.py` | 23/23 | — | verde |
| ma_rastreio_test | `ma_rastreio_test.py` | 58/58 | — | verde |
| popover_390_test | `popover_390_test.py` | 9/9 | — | verde |
| paginas_scan_test | `paginas_scan_test.py` | 5/5 (148 páginas) | — | verde |
| acao_unica_test | `acao_unica_test.py` (saf · familias) | 10/10 · 8/8 | — | verde |
| acao_unica_test gemini | `acao_unica_test.py gemini` | 1/3 | 1/3, as mesmas falhas 21 e 22 | vermelho antigo |
| acao_unica_test v3 | `acao_unica_test.py v3` | erro no item 23 (clique em nulo) | o mesmo erro | vermelho antigo (não chega à linha mudada) |
| rend_multiconjuntos_test | `rend_multiconjuntos_test.py` | 18/18 | — | verde |
| saf_capacidade_simetrica_test | `saf_capacidade_simetrica_test.py` | 38/38 | — | verde |
| saf_revisao_test | `saf_revisao_test.py` | 42/42 | — | verde |
| solo_os_test | `solo_os_test.py` | 18/18 (304ce82); com o teste antigo, 12/12 e erro no AC-SOLO-20 | 18/18 | oráculo de localização (corrigido) |
| solo_rev_test | `solo_rev_test.py` | 22/22 (e54bef1) | — | verde |
| solo_saf_test | `solo_saf_test.py` | 36/36 | — | verde |
| filtros_cultura_test | `filtros_cultura_test.py` | 10/10 | — | verde |
| patest | `patest.py` | para em "o nome da atividade abre o painel…" (erro) | o mesmo ponto e o mesmo erro | vermelho antigo |
| tabelas_irr_test | `tabelas_irr_test.py` | 98/106 | 98/106, as mesmas 8 (TABR-CTX-02) | vermelho antigo conhecido |
| ficha_pivo_test | `ficha_pivo_test.py` | 21/21 | — | verde |
| testes_pedido | `testes_pedido.py` | 7/11 (T01, T02, T05, T07 falham) | 6/11 (T01, T02, T03, T05, T07) | vermelhos antigos; o T03 passa na candidata |
| tabelas_saf_test | `tabelas_saf_test.py` | 24/24 (f42f5c7, teste corrigido) | 24/24 | oráculo de localização (corrigido) |
| visoes_unit_test, ds_unit_test | Node | 25/25 · 31/31 (fb6dc9b) | — | verde |

Reexecutados na e54bef1 (cruzam os merges: SAF carrega o `cenario.js` do #88; todas as telas carregam o `g2lib`): `saf_operacoes_test` 87/87, `saf_tab_test` 14/14, `tabelas_ben_test` 12/12, `tabelas_cad_test` 206/206. Também verdes na f1a4720: os mesmos quatro e `pa_regras_test` 18/18 (Node, sem tela mudada nos merges: prova equivalente).

### 2º lote (para não repetir)

`os_lote_test` (com `RENDER_DIR`), `ma_unica_test`, `popover_390_test`, `acao_unica_test` (saf, familias, gemini, v3), `paginas_scan_test`, `rend_multiconjuntos_test`, `saf_capacidade_simetrica_test`, `saf_revisao_test`, `solo_os_test`, `solo_rev_test`, `solo_saf_test`, `filtros_cultura_test`, `patest`, `ma_rastreio_test`, `tabelas_irr_test`, `ficha_pivo_test`, `testes_pedido`.

### Especificado, não executado

- Leitor de tela real (NVDA, VoiceOver): o nome e o `aria-expanded` foram conferidos no DOM, não com leitor.
- Aparelho físico: o toque foi emulado (CDP, 390 × 844, ponteiro grosso).

