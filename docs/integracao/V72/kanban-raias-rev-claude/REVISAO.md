# Revisão Claude do PR #89 (AGR-02: recolher raias do Kanban sem perder contexto)

```text
ID / resultado útil / persona: PR #89 (AGR-02 no Kanban da O.S.) · o cabeçalho da raia recolhe e expande os cartões, sem trilha, sem perder filtros, seleção e visão · quem acompanha as O.S. no Kanban com Agrupar por
Requisitos do PRD e fora do escopo: padroes-1610 AGR-02 e TAB-09; padroes-1510 TAB-04 (nome "Abrir …"/"Recolher …"); VISOES-2 §3.3–3.4 · fora: TAB-11 (frente claude/v44-v73-seta, ainda fora da composição), cálculos, agenda, preferência gravada
Autor / revisor / integrador: Codex / Claude / Claude (DEC-0910-02; regime leve do protótipo, AGENTS §3.5)
Base (commit ou hashes) / arquivos sob responsabilidade: PR HEAD 2f22375 sobre 6dfa09c (HEAD antigo do PR #88) · composição d995ded (PR #88 em 703d9a1) · junção local e8f70fc · esta pasta
Aceite e comando de verificação: tabela "Resultados" abaixo (comandos executados, brutos em brutos/)
Estado / impedimento / próximo passo: integrar com o ajuste 01 (teste) e, de preferência, o 03 (textos e nome); a TAB-11 converte a raia depois, com o 02
```

Revisor: Claude, 17/10/2026. Sem push e sem comentário no GitHub nesta etapa.

## Junção

- Worktree `/tmp/claude-0/pr89` em **d995ded**. A referência local `origin/claude/v44-v69-mapa` estava parada em 47ccc1d (o refspec do remoto só traz `prototipo-limpo/v43`); o `ls-remote` dava d995ded, e a junção partiu desse SHA.
- `git merge --no-edit 2f22375` → **um conflito**, em `areas/processo_os.py`, `_kanban_raias()`:
  - composição (DS87, TAB-09): `›` antes do nome, `onClick=r.desce`, comentário `# TAB-09: seta antes do nome`;
  - PR: `r.seta` (▸/▾) antes do nome, `aria-expanded=r.expandida`, `onClick=r.alterna`, quadro dentro de `sc-if r.aberta`.
  - Resolução: o lado do PR, com o comentário da TAB-09 conservado (`# TAB-09: seta antes do nome (DS87); AGR-02: ▸/▾ pelo estado da raia`). Nada de "Descer em" voltou.
- Commit da junção: **e8f70fc** (pais d995ded e 2f22375).
- Delta 6dfa09c → 703d9a1 (correções do PR #88): não toca `osKbRaia`, `v.kb_raias` nem `_kanban_raias`. Delta 6dfa09c → d995ded nos arquivos do PR: só a linha da seta (DS87). A AGR-02 (sem trilha, `g2lib.js:363` e `:366`) **já estava em 6dfa09c**.
- Durante a revisão, a composição andou para f3ceb3c (só CF-01: `configuracoes.py`, `config_test.py`, brutos) e a TAB-11 para f42f5c7. `git merge-tree` da e8f70fc com cada uma: sem conflito.

## Resultados (candidata e8f70fc × base d995ded)

Render: `SAFRION_DADOS=sintetico python3 -W error::SyntaxWarning -B build.py && SAFRION_DADOS=sintetico python3 -B montar_render.py` (148 artboards, 156 páginas, sem erro) na junção e numa worktree limpa da d995ded. O `OS.dc.html` dessa base é idêntico (`cmp`) ao da `/tmp/claude-0/int90`, cuja árvore tem `configuracoes.py` sujo; por isso a base limpa foi usada.

Navegador: `env CHROME_BIN=/tmp/cloudchrome/chrome CDP_GL=1 SAFRION_DADOS=sintetico python3 -B <teste>`, um por vez, só com no máximo 1 navegador aberto (portão no `run.sh`; contagem na `brutos/runner.log`), perfil e porta próprios (`comp_lib.Chrome`).

| Teste (executado) | Candidata | Base | Leitura |
|---|---|---|---|
| `kanban_raias_test.py` (Node, PR) | **9/9** | 0/9 (`alterna` ausente) | contraprova do Codex reproduzida |
| `node os_lote_unit.js` | 85/85 | 85/85 | sem efeito no OS-LOTE |
| `visoes2_formas_test.py` do PR | **para em exceção**: OK F1, F3, F4; FALHA F2, F4a, F4b, F4c, F4d, F4e; `tira('Tirar a trilha')` lança TypeError | igual | achado A1 |
| `visoes2_formas_test.py` com o patch 01 | **23/23** | 17/23 (FALHA F2, F3, F4, F4a, F4b, F11d) | os oráculos novos reprovam a base |
| `visoes2_formas_test.py` antigo da base | — | OK F1; FALHA F2–F4; exceção | vermelho já registrado em `DS-MODULOS.md:200` |
| `tabelas_os_test.py` | 40/40 | 40/40 | |
| `os_cenario_test.py` | 22/22 | 22/22 | |
| `os_lote_test.py` (RENDER_DIR da própria árvore) | 32/32 | 32/32 | |
| `ds_modulos.py --catraca` | catraca ok (175 desvios em 80 de 148 telas) | não rodado | a catraca compara com `ds_modulos_base.json` |
| `sonda_raia.py` (manual, CDP) | **12/12** | 4/12 | teclado e toque abaixo |

A primeira versão da sonda supunha que o Tab saía do cabeçalho de T1 direto para T2; ele entra nos cartões de T1. Corrigida e rodada de novo; os brutos da versão errada ficam em `brutos/sonda_v1_invalida_*.log` e não contam.

### Teclado e toque (sonda, candidata)

- Shift+Tab e Tab devolvem o foco a T2 com `:focus-visible`.
- **Enter** (`'\r'`) recolhe T2: `aria-expanded` vai a `false`, os cartões somem, o foco fica no **mesmo** nó, o endereço não muda e as outras raias seguem abertas.
- Com T2 recolhida, o Tab seguinte vai ao cabeçalho de T3, sem cartão oculto no caminho.
- **Espaço** expande T2 com os mesmos cartões e o foco no mesmo botão.
- Ida ao Calendário e volta: T2 continua recolhida. Recarregar reabre (estado só da tela, como o PR declara).
- **390 px com toque real** (`Input.dispatchTouchEvent`): cabeçalho com 99 × 44 px e nada por cima. O 1º toque recolhe (sem navegar e sem rolagem lateral), o 2º expande. Sem erro de JS.
- Base: os botões não têm `aria-expanded`. Enter e toque gravam `trilha=` no endereço e as raias não mudam (botão sem efeito, como o `DS-MODULOS.md` já registrava).
- Diagnóstico: o Enter sem texto do F2 original (`c.tecla('Enter',vk=13)`) **não aciona** o botão nativo, e `aria-expanded` continua `true`.

## Achados

| # | Sev. | Prova | Dano | Correção |
|---|---|---|---|---|
| A1 | **S3** | `visoes2_formas_test.py:34` envia Enter sem `text='\r'`, e o botão não é acionado (F2, F4a e F4b reprovam; o Espaço sem texto da `:44` recolhe em vez de expandir). Em `:47-51`, `:65`, `:80` e no F11c, o teste exige recorte pela trilha, que a AGR-02 desligou antes da base do PR (`g2lib.js:363` `g2agNoTrilha` devolve `null`; `:366` `at=[]`). Em `:51`, `tira('Tirar a trilha')` lança exceção e o teste para. | O aceite de navegador do PR nunca roda inteiro: F6–F14 não executam, inclusive o F11d novo (toque a 390 px). Uma regressão no filtro de Talhão, no recorte do Painel ou no celular passaria sem aviso. Produto correto; só o teste falha. | `patches/01-visoes2_formas_test-agr02-teclas.patch`: Enter e Espaço com texto; F4c–F5, F9, F10 e F11c afirmam a AGR-02 (endereço antigo com trilha não recorta, sem chip de trilha); F11d com toque real. Candidata 23/23, base 17/23. |
| A2 | S4 | `REVISAO.md:5` do PR ("a trilha já chegou ao último nível") e `:17` ("a trilha existente continua pela Tabela/endereço"); comentários `processo_os.py:1068`, `:1219` e `:1419`. | Texto contradiz a AGR-02 e induz a próxima revisão a procurar trilha. | `patches/03-nome-abrir-e-textos-agr02.patch` (textos). |
| A3 | S4 | `processo_os.py:1073`: nome "Expandir raia …". A TAB-04 (`padroes-1510.md:18`) fixa "Abrir …"/"Recolher …". | Nome diferente para o mesmo gesto no leitor de tela. | Uma palavra no patch 03 ("Expandir" → "Abrir"). Com a TAB-11, o `g2seta` já dá esse nome (patch 02). |

Sem achado S1/S2. Nada muda em estoque, demanda, aprovação, dinheiro, OS-LOTE ou alocação. O estado `kbFechadas` é só da tela e está separado por perfil, fazenda, safra, dimensão, caminho e grupo; filtros, seleção e cenário ficam intactos (Node 9/9, sonda K2/K5).

## Seta única (TAB-11)

- **A TAB-11 não está na composição.** `fb6dc9b` e `f42f5c7` não são ancestrais de d995ded.
- A pendência anotada pela TAB-11 (`SETA-PADRAO.md`, "trocar o `›` por `E.seta_ir()`") foi escrita quando a raia **descia**. Com o #89 a raia **recolhe**, e na TAB-11 isso pede `E.seta()` como 1º filho do botão com `aria-expanded`, mais o nome pelo `g2seta`. `seta_ir` (seta parada, de navegação) seria a semântica errada.
- **Menor adaptação** (`patches/02-tab11-raia-seta-unica.patch`, 3 arquivos, +8/−7):
  - `<span>{r.seta}</span>` vira `E.seta()`; `align-items` muda de `baseline` para `center`;
  - `osKbRaia` usa `g2seta(aberta, 'raia …')` para `expandida` e `lab`, e o campo `seta` sai;
  - o oráculo do `kanban_raias_unit.js` passa do glifo para o nome;
  - o `seta_padrao_test.py` ganha o estado `OS.dc.html?view=kanban&ag=onde`.
  - `aria-expanded` e o estado por contexto ficam como estão. Se o 03 entrar antes, usar `02b-…-depois-do-03.patch`, que muda só a linha de contexto.
- **Ensaio executado** na junção e8f70fc + TAB-11 fb6dc9b (merge sem conflito):
  - build ok; `kanban_raias_test.py` 9/9;
  - `visoes2_formas` (com 01) 23/23; sonda 12/12, com nome "Abrir raia T2 …" e o chevron girando;
  - `seta_padrao_test.py` só nas telas da O.S. (`SPT_SO=OS.dc.html`, diagnóstico): A, B, D e F **sem desvio**, um desenho só;
  - **contraprova** sem o patch 02, com o estado novo no teste: A e B apontam `OS.dc.html?view=kanban&ag=onde` a 1440 e a 390 px.
  - Os mínimos de B, C, D e E (mais de 300 controles, mais de 500 setas, pelo menos 12 telas) só valem na rodada inteira; no recorte reprovam nos dois lados por construção.
- O patch 02 também aplica sobre a junção + f42f5c7 (`git apply --check` num índice temporário). O ensaio de navegador foi feito com a fb6dc9b.

**Recomendação: o #89 entra primeiro, com ▸/▾ e o ajuste 01; a TAB-11 converte a raia depois, com o 02.**

- **Dano evitado:**
  - hoje a composição tem um botão sem efeito (a raia grava `trilha=` e nada muda; ver o F2 da base), e o #89 o tira já;
  - ▸/▾ é o padrão vigente na composição (TAB-04/TAB-09, mesmo glifo do grupo da Tabela), então nada fica inconsistente até a TAB-11;
  - sem o estado novo no `seta_padrao_test.py`, a TAB-11 deixaria passar o glifo da raia, porque a varredura não abre o Kanban agrupado. O 02 fecha esse buraco.
- **Retrabalho:**
  - com a TAB-11 primeiro, o #89 precisaria de um terceiro empilhamento e de outra rodada de revisão, e o Codex está sem navegador para reproduzir;
  - a TAB-11 ainda empurraria `seta_ir` numa linha que o #89 reescreve.
  - Na ordem proposta, a TAB-11 aplica 8 linhas já ensaiadas e troca o texto da pendência no `SETA-PADRAO.md` (de `seta_ir` para `seta()` no botão com `aria-expanded`).

## Veredito

**Integrar com o ajuste 01** (teste). Antes do merge, de preferência também o 03 (S4: textos e uma palavra). Sem S1/S2. O 02 fica com a frente TAB-11, depois do #89.

## Arquivos

- `brutos/`: logs de cada execução (candidata, base e ensaio TAB-11), `runner.log` com a hora e a contagem de navegadores, logs de build e o `resultado.json` do `os_lote_test`.
- `patches/`: 01, 02, 02b e 03.
- `sonda_raia.py`: sonda de teclado e toque. `run.sh`: execução em fila com o portão de navegador.
- `capturas/`: T2 recolhida a 1440 px e C1 recolhida a 390 px (toque), na candidata e no ensaio com a TAB-11.
