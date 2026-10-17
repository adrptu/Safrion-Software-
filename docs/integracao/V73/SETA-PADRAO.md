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
| Setas desenhadas e medidas (C) | 0 com o componente | 1.706 a 1440 (1.340 de ir) · 1.559 a 390 | idem |
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
