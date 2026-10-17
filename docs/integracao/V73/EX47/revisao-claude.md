# EX47a · Revisão Claude do PR #93 (Codex)

```text
ID / resultado útil / persona: EX47a · as ações da linha vão para o ⋯ também em grade sem exclusão · quem consulta o Planejar safra (safra encerrada) no computador e no celular
Requisitos e fora do escopo: aceite combinado (abaixo) · fora: PR #89 (outro revisor), ligar o rmenu globalmente
Autor / revisor / integrador: Codex / Claude / Claude
Base (commit) / arquivos: 2f22375d (HEAD do #89) → 3010fc9482812ae467d13d0f61f083686fdd8c86 · engine.py, g2lib.js, rmenu_unit.js, rmenu_generator_test.py, REVISAO.md
Aceite e comando de verificação: §3 (executado)
Estado / impedimento / próximo passo: FAVORÁVEL COM AJUSTES · A1 e A2 (S4) e o retarget sobre a ponta (conflito trivial no engine.py) antes de integrar
```

Data: 17/10/2026. Dados só sintéticos (`SAFRION_DADOS=sintetico`).

## 1. Veredito

**Favorável com ajustes.** Nenhum S1, S2 ou S3 no escopo. A correção faz o que promete:
- Na grade com `menu_linha` sem `dele`, a ação da linha volta a ser alcançável pelo ⋯. Na base ela sumia: saía da célula e nenhum menu era montado.
- O alinhamento fecha em todas as linhas: cabeçalho, linhas, faixa `fgrp` com span e total.
- "Excluir" só aparece com `dele` e em linha permitida.
- O caminho sem `rmenu` é idêntico ao da base.

Ajustes pedidos, todos S4:
- **A1:** a coluna estrutural sem nenhuma ação.
- **A2:** o teste ainda não mede o alinhamento de cada linha com e sem `dele`, como o aceite pediu.

O retarget sobre `f3ceb3c` tem um conflito trivial, já resolvido e verificado na composição (§4).

## 2. Achados

### No escopo do PR

**A1 · S4 · coluna de ações vazia na grade sem exclusão e sem ação**
- **Caminho:** `engine.py:1810` (`hdel`) e `engine.py:1831` (célula final do total) com `acoes_linha`; `g2lib.js:570` (`_ncols`) e `g2lib.js:611` (célula estrutural).
- **Contraexemplo (executado):** Planejar safra › Safra 2025/26 (encerrada), etapa 2, a única tela real com `menu_linha` sem `dele`. Nos dados sintéticos nenhuma linha tem ação. Mesmo assim a grade ganha uma 6ª trilha com o cabeçalho sem nome (`""`) e todas as células vazias.
  - A 1440 px, essa trilha toma 116,5 px que eram da última coluna de dados: na base, Plantio tinha 236,7 px em 5 trilhas.
  - A 390 px ela fica com 0 px.
  - Para o leitor de tela, é uma coluna sem nome e vazia.
  - Isso contraria o item "nenhuma coluna vazia" do aceite.
  - Fonte: `claude/sonda_coluna_vazia.log` e `claude/capturas/head_S2526_1440_sem_acao.png` × `base_S2526_1440_sem_acao.png`.
- **Correção proposta:** a coluna existir só quando houver ⋯, nas grades com `rmenu` sem `del`.
  - No `g2vals`, depois de montar `v[id+'_rows']`: `const semAcao=sp.rmenu&&!sp.del&&!v[id+'_rows'].some(rw=>rw.cells.some(c=>c.rm))`. Com `semAcao`, tirar a célula estrutural final de cada linha, descontar 1 de `_ncols` e publicar `v[id+'_acoes']=!semAcao`.
  - No `engine.grid`, com `menu_linha and not dele`: `hdel` e a célula final do total dentro de `<sc-if value="{gid}_acoes">`, e `ntr=H('_ncols')` (trilhas dinâmicas também sem `ess`).
  - Teste: S2526 com 5 trilhas sem ação e 6 com a ação injetada.
  - Com O2 corrigido, essa grade nunca terá ação, e a coluna ficaria sempre vazia. Por isso o ajuste vale a pena.

**A2 · S4 · o teste não mede o alinhamento de cada linha com e sem `dele`**
- **Caminho:** `rmenu_unit.js`.
- **Contraexemplo:**
  - O teste Node confere `cells.length` (não a soma dos spans) só na linha "b", só sem `del`. Com `del`, nas linhas protegidas, em `fgrp` e com `sel` ele não mede nada.
  - O teste do gerador confere cabeçalho, total e trilhas, mas não as linhas, que são montadas no runtime.
  - O aceite pedia "o número de células de cada linha é igual ao de colunas do cabeçalho, com e sem `dele`".
- **Correção proposta:** em toda linha, para `rmenu×del×sel`, a soma dos spans (`grid-column:span N`) igual a `_ncols`. Cobrir linhas normais, `ro`, `livre`, `fora`, `nosel`, `xdel`, filho e `fgrp`.
  - A sonda `claude/sonda_rmenu_alinhamento.js` faz isso (547 verificações no mesmo padrão do `rmenu_unit.js`, sem mocks) e pode ser adotada como teste.
  - Ela também confere que, sem `rmenu`, as células são idênticas às da base.

**A3 · S4 · opcional · endurecimento**
- **Caminho:** `g2lib.js:604-609`.
- A célula ⋯ de linha protegida (ou de grade sem `del`) ainda carrega `ask`, `yes` (a função que remove a linha) e `delLabel`. Hoje isso é inalcançável: `asking` é falso e o ⋯ não chama `ask`.
- **Correção:** só definir `ask`, `yes` e `delLabel` quando `!semDel`. Assim, "Excluir só onde é permitido" passa a valer por construção.

### Fora do escopo: anteriores ao PR (tarefas separadas, não bloqueiam)

**O1 · S4 (design system) · o ⋯ da linha tem 32×32 px no toque**
- O DS (`docs/design-system/barra-limpa-mais-acoes.md`) pede "No toque, ⋯ e itens com 44 px".
- Causa: `.g2mais.g2mais-l` (`engine.py:1207`) vence, por especificidade, o `@media (pointer:coarse){.g2mais{…44px}}` (l.1210). Existe desde `b348b29` (15/10).
- Medido a 390 px na S2627 (com `dele`) e na S2526.
- **Correção:** `@media (pointer:coarse){.g2mais.g2mais-l{min-width:44px;min-height:44px}}`.

**O2 · S4 · "Reaplicar" sem a guarda de `r.ro`**
- **Caminho:** `safra.js:790`. As outras ações da linha ("Dividir", "Aplicar plano") têm a guarda.
- **Efeito com o PR:** um cultivo de safra encerrada com plano incompatível passa a mostrar ⋯ › Reaplicar.
- **Executado por injeção de estado:** a trava de domínio recusa com "Safra encerrada: somente consulta." Nada é gravado. Não acontece nos dados sintéticos.
- **Correção:** `r.p.plano=[chip].concat(r.ro?[]:[{k:'act',t:'Reaplicar',…}])`.

**O3 · S4 latente · o modo Cartões engole o ⋯ de linha `fgrp`**
- **Caminho:** `g2lib.js:471`. A fatia `dat=cs.slice(off,off+n)` inclui a célula de ação quando a 1ª célula tem span.
- Na base, com `del`, já era assim (`claude/sonda_fgrp_cartoes.*.log`).
- Nenhuma tela tem hoje faixa `fgrp` com ⋯: ela só traz "Planejar talhões livres ›", que fica na célula.
- **Correção:** `tr` = células que não são de dado depois da última de dado, por exemplo `cs.slice(off).filter(c=>!c.isData)`.

**Nota sobre a semântica de `ro`**
- No caminho antigo (sem `rmenu`), a linha `ro` com `dele` mantém a lixeira, igual à base, como o contrato pede.
- No ⋯, `ro` não exclui.
- No caminho `rmenu+del`, o PR troca a lixeira legada da linha `ro` sem ação por uma célula estrutural: melhora, de acordo com "Excluir só onde é permitido". Nos dados sintéticos não há essa linha: 0 lixeiras na S2627, na base e no HEAD.
- A divergência entre os dois caminhos fica para decidir fora deste PR.

## 3. Aceite × evidência (executado)

| Aceite | Resultado | Evidência |
|---|---|---|
| Ações alcançáveis com e sem exclusão | ok | Node·A2: em 8 combinações, toda ação vai para o ⋯ ou fica na célula; a navegação (›) fica na célula. Navegador N4: o ⋯ de T1 traz "Reaplicar"; na base a ação some (contraprova). |
| Nenhuma coluna ou controle vazio | ok para controle · **A1** para coluna | N3: nenhum botão sem nome; todo ⋯ tem item. Nos Cartões, o espaçador da trilha de ações não tem papel nem foco. A coluna sem ação é o A1. |
| Excluir só onde é permitido | ok | Node·A3/A5 e N2 (navegador): S2627 só nos cultivos; S2526 nunca; `cf` obsoleto não pergunta; `xdel` só no item Excluir. |
| Caminho antigo igual | ok | Node·A6: células idênticas às da base com `rmenu=false` (com e sem `del`/`sel`). HTML gerado: 147 páginas diferem só pelo g2lib embutido; no SAF, só a `g_cult_S2526` ganha o columnheader e a célula do total. |
| Alinhamento: células de cada linha = colunas do cabeçalho, com e sem `dele` | ok no produto · **A2** no teste do PR | Node·A1: soma dos spans = `_ncols` em toda linha das 8 combinações, `fgrp` incluída. N1 (navegador, 1440 e 390): todas as linhas visíveis, o ⋯ na última coluna, também com a pergunta "Excluir?" aberta. |
| Foco e Esc no ⋯; leitor de tela | ok | N4: ↓ abre e foca o item; Esc fecha e devolve o foco; Enter abre; Enter no item executa e devolve o foco. Rótulo "Mais ações de T1" no botão e no menu. |
| Confirmação `cf` | ok | N5: Excluir no ⋯ → "Excluir?" e "Manter" na linha, alinhada; Manter volta ao ⋯ sem excluir. `cf` obsoleto numa grade sem `del` não pergunta. |
| 390 px | ok (O1 à parte) | N7: na Tabela, o ⋯ é alcançável e a página não rola na horizontal. Nos Cartões, N6: o mesmo número de ⋯ da Tabela e nenhum controle vazio (a rolagem lateral dos Cartões não foi medida pela sonda; `cartoes_test` M5 e `saf_multi_fazenda_test` F1 a cobrem nas suas telas). |

### Comandos e resultados (executado)

Todos rodaram em `tools/prototipo/v37/gen37` do worktree no HEAD `3010fc9`, salvo indicação. Os brutos estão em `claude/`.

**Build**
- Comando: `SAFRION_DADOS=sintetico python3 -W error::SyntaxWarning -B build.py && SAFRION_DADOS=sintetico python3 -B montar_render.py`
- Resultado: 148 artboards, 156 páginas, exit 0 (`build.head.log`).

**Testes do Codex**

| Teste | HEAD | Base 2f22375d (contraprova) |
|---|---|---|
| `node rmenu_unit.js` | OK | reprova no 1º `rm` ausente (`undefined` ≠ `true`) |
| `python3 -B rmenu_generator_test.py` | 1 teste, 8 subtestes OK | `FAILED (failures=2)`: menu sem exclusão, com e sem `sel` |

**Sondas da revisão (sem navegador)** · as verificações da sonda são citadas como Node·A1 a Node·A7 (não confundir com os achados A1 a A3)
- `node claude/sonda_rmenu_alinhamento.js g2lib.js <g2lib da base>`: HEAD com 547 OK e 0 falhas; base com 47 falhas.
- `node claude/sonda_fgrp_cartoes.js`: O3 (latente, igual na base com `del`).

**Testes de navegador**
- Ambiente: `env CHROME_BIN=/tmp/cloudchrome/chrome CDP_GL=1 SAFRION_DADOS=sintetico`, com o portão de no máximo 1 Chrome principal (`claude/_roda.log`).

| Teste | Resultado |
|---|---|
| `claude/sonda_rmenu_navegador.py` | 61 OK, 0 falhas, 2 OBS (O1). Na base, reprova em N4: a ação some. |
| `ds_1510_test.py` (S, A, B, C) | 17 ok, 0 falhas |
| `saf_tab_test.py` | 14/14 |
| `saf_multi_fazenda_test.py` | 23/23 |
| `saf_capacidade_simetrica_test.py` | 38 ok, 0 falhas |
| `cartoes_test.py` | 70/70 |
| `cadastros_padrao_test.py` | 44/44 |
| `tabelas_saf_test.py` | 24/24 |
| `claude/sonda_coluna_vazia.py`, HEAD × base (A1) | HEAD: 6 trilhas, a última com 116,5 px e cabeçalho sem nome, a 1440; 0 px a 390. Base: 5 trilhas a 1440 e 3 a 390. |

Os outros `tabelas_*_test.py` não foram rodados. O motivo:
- só o SAF usa `menu_linha`;
- com `rmenu=false` as células são idênticas às da base (Node·A6);
- fora do g2lib, o HTML gerado só difere no SAF.

## 4. Composição com a ponta da branch única (executado sem navegador)

- **Commit do #93 sozinho sobre `f3ceb3c`:** conflita em `engine.py`, nas linhas `hsel`/`hdel`. Na ponta, elas ganharam `class="g2th"` e o `_selArw` do TAB-09.
  - Resolução verificada: manter as linhas da ponta e trocar, em `hdel`, `if dele` por `if acoes_linha`.
  - O g2lib aplica sem conflito.
- **Composição (`f3ceb3c` + `3010fc9` resolvido):** `rmenu_unit.js` OK; `rmenu_generator_test.py` OK; sonda Node 547 OK e 0 falhas (Node·A6 contra o g2lib de `f3ceb3c`); build com exit 0; `ds_1510_test` S/A 9 ok (`claude/composicao_f3ceb3c.log`).
- **PR #89 sobre `f3ceb3c`:** conflita em `areas/processo_os.py`. Isso é do #89; fica registrado só para a ordem do retarget.

## 5. Especificado, não executado

- Navegador na composição (`f3ceb3c` + #93): fica para depois do retarget, com a bateria da §3.
- A1 e O1 a O3: as correções acima estão descritas, não implementadas. Não editei arquivos do autor.
- Leitor de tela real (NVDA/VoiceOver): conferi os nomes acessíveis e os papéis pelo DOM, não com o leitor.

## 6. Nota de processo

- Uma única execução (`sonda_coluna_vazia.py` no HEAD) começou com 2 Chrome principais. O laço de espera tinha teto de 500 s. As demais respeitaram o portão (≤1).
- Nenhum processo de terceiros foi encerrado.
- A sonda de navegador na base para depois de N4, como esperado, porque o ⋯ não existe lá.
- A captura `rev93_S2526_injetado_tabela_1440.png`, fora do repositório, foi sobrescrita pela execução na base. As capturas versionadas em `claude/capturas/` têm prefixo `head_` ou `base_`.
