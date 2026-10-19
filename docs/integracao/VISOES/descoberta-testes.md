# Descoberta · testes e padrões para o ViewSwitcher (seletor de visões)

- **Pedido:** proprietário, 10/10/2026 ("a visão nasce do atributo dominante").
- **Lente:** testes e padrões (somente leitura).
- **Base lida:**
  - protótipo: `/home/user/sp-proto` = `claude/prototipo-v44` @ `0139898`;
  - frentes não integradas, lidas sem editar: `sp-ds` @ `943433c`, `sp-tabr` @ `8f19e0d`, `sp-nav` @ `a7023ca`;
  - software real: `/home/user/Safrion-Software-` @ `b8d6f84`.
- **Caminhos:** relativos a `tools/prototipo/v37/gen37/`, salvo indicação.
- **Executado:** leitura de código, `grep` e `git diff` entre as branches.
- **Não executado:** nenhum build, nenhum teste e nenhum navegador. Toda afirmação sobre "quebra" é **especificada** (lida no código), não "executada". Confirmar rodando a bateria na worktree de rascunho (§4).

---

## 0. Achados que mudam o plano

1. **Ícone sem texto quebra 13 arquivos de teste que trocam de visão pelo texto visível.**
   - Os testes procuram `innerText === 'Kanban'`, `'Lista'` ou `'Recursos'`, e um botão só com ícone tem `innerText` vazio.
   - Nos dois que caem para `aria-label`, o critério é igualdade ou prefixo:
     - `ben_fluxo_test.py:56-57`: igual a `'Kanban'`;
     - `acao_unica_test.py:46`: começa com `'Kanban'`.
     - O rótulo pedido, "Ver em kanban", falha nos dois critérios.
   - A lista completa está na §5.
   - **Remédio:**
     - um auxiliar único de teste, `visao(nome)`, que procura `[data-visao=…]` dentro do grupo;
     - os testes trocados no mesmo commit, já que no regime leve tudo vai na mesma branch.
   - **Não use texto escondido** (`sr-only`) para salvar os testes. O `g2dica` decide que um botão é "só ícone" pelo `innerText` (`sp-ds g2lib.js:543`, `!/[\p{L}\p{N}]/u.test(vis)`). Com texto escondido, a dica no foco deixa de abrir.
2. **Preferência no `localStorage` derruba o TF02.**
   - `tabelas_os_test.py:44,52,105` compara o `localStorage` inteiro antes e depois de filtrar e trocar de visão: "filtrar não executou ação de negócio".
   - Gravar `safrion.visao.*` faz o TF02 falhar.
   - **Remédio:** chave com prefixo próprio, por exemplo `safrion.pref.visao:<perfil>:<entidade>`, e `negocio()` passa a ignorar esse prefixo. Quem dá a regra é o teste, não a tela.
   - "Por usuário" no protótipo é o perfil de demonstração: `G2_PERFIL_KEY='safrion.perfilDemo'`, em `g2lib.js:263-265`.
3. **Na O.S., `#` já é endereço de registro, com expressões ancoradas.**
   - Em `processo_os.py:754-760`, `abrirHash` reconhece só três formas:
     - `^#tal=…|…$`;
     - `^#nova:…$`;
     - `^#(O[SB]-\d+)(?::ajustar)?$`.
   - O Mapa usa `#car` (`inicio.py:1093`).
   - Acrescentar `&visao=` ao hash quebra a abertura de ordem que vem do Mapa e da IR-03:
     - `os_irrig_filtro_test.py` passo 5 espera `location.href` terminando em `OS.dc.html#OS-0418`;
     - `map_decisoes_test.py` também abre ordens assim.
   - **Remédio:**
     - `?view=` na *query*, como o proprietário pediu, lido por `URLSearchParams(location.search)`;
     - gravado por `history.replaceState(null,'',pathname+'?'+params+location.hash)`, que preserva o hash.
   - O `http.server` dos testes ignora a query, então o teste abre direto `OS.dc.html?view=kanban`.
   - Já existe precedente de ler a query e o hash juntos: `cad_fazendas.py:551`, `[?&#]talhao=`.
4. **A visão ativa não pode ganhar verde cheio, e isso contraria o PRD.**
   - O teste exige tom de escolha:
     - `acao_unica_test.py:375-384` (teste 29) exige que a visão atual da O.S. não seja `rgb(30, 122, 76)`;
     - os testes 15 e 27 contam como primária todo botão verde em `header` ou `main`, sem excluir `[role=group]`: `EST` (`acao_unica_test.py:30`) e `PRIM` (`:307`);
     - só o `MEDE` do `comp_lib.py:101` exclui o grupo.
   - O PRD pede o contrário: o PRD 74.5.10 (DS-36, `docs/PRD.md:14299-14306`) manda a "opção ativa passa a verde".
   - O BOT-01 ("um verde por contexto") e o teste 29 decidem hoje pelo tom de escolha.
   - **Remédio:** ativo **tonal com borda de 2 px** (`#E4F3E9`, ícone `#1E7A4C`, borda) e `aria-pressed="true"`. Assim o destaque não depende só de cor.
   - Registrar a divergência com o DS-36 para o Codex. Não é decisão do proprietário: é técnica e delegada.
5. **A dica no foco depende do DS-DICA, que ainda não está integrado.**
   - O `g2dica` está em `sp-ds g2lib.js:526-583`:
     - abre no hover (300 ms) e no foco de teclado;
     - no toque, abre com toque longo (500 ms);
     - num ícone sem texto, mostra o `aria-label`;
     - quando a dica repete o nome acessível, não põe `aria-describedby` (`ds_test.py:292`, D7).
   - Sem o DS, só resta o `title`, que não abre no foco. **O ViewSwitcher entra depois da integração do DS**, ou sobre a `sp-ds`.
   - O `ds_test.py` do DS também troca de visão pelo texto, em `:166`, `:227`, `:299` e `:336`, e quebra junto. É preciso combinar a ordem com a frente DS.
6. **Contexto vazio já esconde o seletor, e há teste disso.**
   - `os_irrig_filtro_test.py:98` (passo 9) exige que, com Safrinha 2027 sem ordens, não exista `[aria-label="Visão das ordens"]`.
   - A tela troca as visões por "uma frase e uma ação" em `processo_os.py:1236-1240`.
   - Recorte vazio de **filtro** é outra coisa. Exemplo: o Kanban com "Filtro da lista aplicado…" e "Limpar filtros", em `acao_unica_test.py:190`.
   - **Manter as duas regras.** O "estado vazio em toda visão" vale para o vazio de filtro. O vazio de contexto continua sem seletor.
7. **Não há atalhos numéricos no protótipo nem no software real.**
   - A busca por `Digit[1-9]`, `aria-keyshortcuts` e `accesskey` não achou nada em `g2lib.js`, `engine.py`, `areas/` e `apps/web/src`.
   - Pela regra do pedido ("1…9 se o projeto já tiver atalhos"), os atalhos numéricos ficam de fora.
8. **Não existe arrastar em lugar nenhum**: `draggable` e `dragstart` não aparecem em `g2lib.js`, `engine.py` nem `areas/`.
   - No Kanban da O.S., "a fase só muda por evento", e o teste 15 exige que a fase seja texto, não comando (`processo_os.py:1251`; `acao_unica_test.py:188-190`, `ctl==0`).
   - **Arrastar no Kanban da O.S. fica proibido**, com teste de ausência (`[draggable=true]` = 0).
   - Arrastar no Calendário só pela mesma função do formulário, com desfazer (§2.4).
9. **Software real: especificar, não implementar agora** (§6).

---

## 1. Teste de unidade JS no protótipo (padrão `*_unit.js` / `*_unit_test.py`, motor real no node)

### 1.1 Três formas em uso

**A · Executor Python que monta o JS real e roda no node ou no jsc.** É a forma das regras de domínio.
- **Modelo:** `legal_unit_test.py:6-24`.
- **Motor:** `jsc` no macOS, `node` no Linux. O prelúdio `globalThis.print=(...a)=>console.log(...a)` vem em `:7-8`.
- **Calço:** `localStorage` em memória, `window.addEventListener` e `location` (`:12-14`).
- **Fonte montada:** os pedaços que a tela usa. Exemplos:
  - `cenario.perfis_js()` e `cenario.js_prefixo()`;
  - `dados_mip.js_prefixo()`;
  - `JS_NUCLEO` da O.S.;
  - só a linha `function g2num` do `g2lib.js`.
  - Tudo vai num `tempfile`, depois `subprocess.run(MOTOR+[f])` (`:15-21`).
- **Saída:** uma linha `OK …` ou `FALHA …` por caso, com `RESULTADO n/m` e `sys.exit(1)` se houver falha (`:22-24`).
- **Variante com dois motores:**
  - `assinatura_unit_test.py:29-45` roda o mesmo `assinatura_unit.js` com `cenario.js` e sem ele, como as telas que não o carregam;
  - lê `TOTAL n` e soma.
  - As expectativas vêm de Python com `Decimal`, das mesmas linhas de dados (`:16-27`).
- **Casos em JS:**
  - `ok(nome,cond,info)` e `T(f)` capturam exceção (`legal_unit.js:6-8`);
  - os stubs da base fazem os casos falharem quando a regra não existe (`legal_unit.js:5`);
  - assim o vermelho na base prova que o teste testa.

**B · Funções puras do `g2lib.js` no node, sem montar a tela.** É a forma indicada para o ViewSwitcher.
- **Modelo:** `sp-ds/…/ds_unit.js:5-10`:
  ```js
  const src = fs.readFileSync(path.join(__dirname, 'g2lib.js'), 'utf8');
  const G = new Function('const G2_GLOSS=…;\n' + src + '\nreturn {g2dicaRegra, g2dicaDe, …};')();
  ```
- **Executor:** `ds_unit_test.py:17-20` roda `node ds_unit.js` e confere `returncode`. Também confere estruturas do gerador: CSS comum em `engine.G2_CSS` e todas as páginas do `project/` carregando o CSS.

**C · Regra do `g2lib` no meio de um teste de navegador, por `vm.runInContext`.**
- **Modelo:** `tabelas_os_test.py:72-77`, com linhas sintéticas para casos que a tela não permite montar.

### 1.2 O que testar em unidade no ViewSwitcher (proposta para `visoes_unit.js` + `visoes_unit_test.py`)

Funções puras no `g2lib.js`, uma fonte só, usada pelo gerador e pela tela.

| Função | Casos (positivos e negativos) |
|---|---|
| `visaoInicial(url, pref, validas)` | <ul><li>`?view=kanban` válida vence a preferência.</li><li>`?view=mapa` fora das válidas cai para a preferência.</li><li>Preferência inválida ou de outra entidade cai para `lista`.</li><li>Sem URL nem preferência: `lista`.</li><li>Valor com maiúscula, acento ou lixo (`<script>`) é ignorado.</li><li>Uma só válida: `lista` e sem seletor.</li></ul> |
| `visoesValidas(entidade, atributos)` | Uma visão só entra se o dado a sustenta (tabela 1.3). Exemplos negativos:<ul><li>sem data relevante, sem Calendário;</li><li>sem início **e** fim, sem Timeline;</li><li>sem geometria ou coordenada, sem Mapa;</li><li>sem fluxo de estados definido, sem Kanban;</li><li>sem categoria **e** valor somável, sem Tabela agrupada;</li><li>sem pai e filho, sem Árvore;</li><li>foto que não é a informação principal, sem Galeria.</li></ul>Também: a ordem é fixa (Lista primeiro) e a O.S. não ganha a 6ª fase. |
| `visoesCelular(validas, ativa)` | <ul><li>Até 3, todas aparecem.</li><li>4 ou mais: as 3 primeiras e "mais".</li><li>Ativa fora das 3 primeiras: continua visível e marcada, a regra decide se ela troca de lugar ou aparece no "mais" marcado; o teste fixa a escolha.</li><li>Uma só: nada.</li></ul> |
| `proximaVisao(i, tecla, n)` | <ul><li>`ArrowRight` e `ArrowDown` avançam; `ArrowLeft` e `ArrowUp` recuam.</li><li>Dá a volta.</li><li>`Home` e `End` vão ao primeiro e ao último.</li><li>Outras teclas não mudam nada.</li><li>Seta só move o foco: ativar é só Enter ou Espaço, conforme o pedido.</li></ul> |
| `urlComVisao(href, visao)` | <ul><li>Preserva os outros parâmetros e o hash (`#OS-0420`, `#tal=…`).</li><li>`lista` tira o `view`, para não poluir o endereço.</li><li>Ida e volta sem perda, como no `test/tabela.test.ts:216-252` do software real.</li></ul> |
| `chavePref(perfil, entidade)` | Prefixo fixo, por exemplo `safrion.pref.visao:`. Perfis diferentes geram chaves diferentes. Leitura e escrita com `try/catch`: no modo privado, sem `localStorage`, o resultado é `lista` e não há erro. |

**Prova de que o teste testa:** stubs como em `legal_unit.js:5`, ou um mutante, como em `ben_mutantes.py`. Exemplos:
- sem `aria-pressed`;
- precedência invertida;
- `visoesValidas` que aceita Calendário sem data.

Cada um tem de ficar vermelho.

### 1.3 "Visões válidas por entidade": onde testar a regra do atributo dominante

- **Onde mora a regra:** se as visões válidas forem calculadas no build a partir das colunas da grade (`grid([...dict(t='date'), multi=True…])`), o teste é Python, no padrão `capacidade_unit.py` e `ocupacao_unit.py`.
- **Paridade:** a função JS (`visoesValidas`) e a Python não podem divergir. Usar uma fonte só (ENG-011) ou um teste de paridade JS × Python, como `cal01_test.py` (docstring `:2-4`).
- **Expectativas por entidade, conferidas com o código:**
  - **O.S.:**
    - Lista, Kanban e Recursos já existem (`processo_os.py:1232`);
    - "Recursos" é a "Carga por recurso" (`processo_os.py:1158-1205`, `_recursos_tab`);
    - Calendário entra pelas datas `ini` e `fim` da grade (`processo_os.py:1221`);
    - Mapa entra pelos talhões multivalorados (`tal multi`).
  - **Talhões (CD-01):**
    - a Lista **já é árvore** fazenda › talhão (`cad_fazendas.py:250-259,265`);
    - já existe Lista | Mapa, em `seg('cdv', …)`, `cad_fazendas.py:259,263`;
    - um modo "Árvore" separado repetiria a Lista: o teste deve falhar se aparecerem as duas.
  - **Estoque (EST):** a árvore item › lote já existe (docstring do `tabelas_est_test.py`). A "Tabela agrupada" precisa de categoria e valor somável na mesma unidade.

---

## 2. Testes de componente e de navegador

### 2.1 Infraestrutura pronta (reaproveitar; não criar outra)

| Peça | Onde | Para quê |
|---|---|---|
| `cdp.Chrome` | `cdp.py:64-115` | <ul><li>Chrome headless por CDP, com perfil novo por execução.</li><li>`CDP_GL=1` liga o WebGL por software (SwiftShader), exigido pelo MapLibre do Mapa (`:67-69`).</li><li>`goto` espera `readyState` e texto (`:97-102`).</li><li>`size(w,h)` emula `mobile` abaixo de 500 px (`:103-104`).</li></ul> |
| `comp_lib.Chrome` | `comp_lib.py:20-87` | <ul><li>`aparelho(w,h,escala,toque)` controla toque, `hover:none` e `pointer:coarse` (`:51-57`).</li><li>`tecla(key,code,vk,text,mod)` usa `Input.dispatchKeyEvent` (`:69-72`).</li><li>`tab(n,shift)` usa mod 8 para Shift (`:73-74`).</li><li>`mouse` (`:75-76`) e `toque` (tap de 50 ms, `:77-79`).</li><li>`setFocusEmulationEnabled` dá à página foco de janela (`:38`).</li><li>`CDP_PORT` anexa a um Chrome já aberto.</li></ul> |
| `servir(dir)` | `comp_lib.py:89-90` | `http.server` em porta livre (`journeys.free`). |
| `MEDE` / `resumo` | `comp_lib.py:95-142` | <ul><li>Responsividade: título, comando principal alcançável, itens cortados fora de região rolável, fonte ≥ 10 px, página sem rolagem lateral.</li><li>`verde()` exclui `[role=group]` (`:101`).</li></ul> |
| `app_lib.App` | `app_lib.py:18-63` | <ul><li>App de campo a 390 × 1800 (`:24`).</li><li>`clk` por texto, `setv`.</li><li>`cen(expr)` lê o cenário na própria página.</li><li>`ok` e `fim` imprimem `n/m ok`.</li></ul> |
| Chrome com hover real | `sp-ds/ds_test.py:29-46` | <ul><li>`--blink-settings=primaryHoverType=2,…`: sem isso o headless responde `hover:none` e a dica de hover não abre.</li><li>`hover()` com `CSS.forcePseudoState` de reserva (`:78-94`).</li><li>`pronto()` chama `Page.bringToFront`; sem foco de janela, `focus()` não dispara `focusin` (`:61-68`).</li></ul> |
| Sonda da dica | `sp-ds/ds_test.py:108` (`DICA`) | `#g2-dica`: visível, texto, `role=tooltip`. |
| `Grade` | `sp-tabr/…/tabelas_lib.py:13-…` (só na TABR) | i-ésima grade visível, colunas, filtro pelo menu e ordem. |
| `rolagem()` | `acao_unica_test.py:54-55` | Posição de leitura: casca, conteúdo e caixas `.g2rola`. Aceite de ±4 px no teste 7 (`:137`). |
| Contador de cliques | `ben_fluxo_test.py:56-57` (`window.__cl`) e `sp-nav pa_lista_test.py` L12 | Cliques medidos antes e depois do mesmo cenário (AGENTS §3.3). |

**Teclas pelo CDP**, com o `windowsVirtualKeyCode` exigido:

| Tecla | Chamada |
|---|---|
| Seta à direita | `c.tecla('ArrowRight','ArrowRight',39)` |
| Seta à esquerda | `c.tecla('ArrowLeft','ArrowLeft',37)` |
| Seta abaixo e acima | 40 / 38 |
| Início e fim | `Home` 36 / `End` 35 |
| Enter | `c.tecla('Enter','Enter',13,text='\r')` |
| Espaço | `c.tecla(' ','Space',32,text=' ')` |
| Esc | `c.tecla('Escape','Escape',27)` |

- Com essas chamadas, o Tab, o Esc e o Enter já são exercitados em `tabelas_os_test.py:151-161`.
- O foco é lido por `document.activeElement` e `:focus-visible` (`ds_test.py:327`).

### 2.2 Componente: o que verificar (proposta `visoes_test.py comp`)

Na O.S. e na entidade da fatia 1, a 1440 × 900, com o Chrome com hover:

1. **Grupo:**
   - `role="group"`, rótulo mantido: "Visão das ordens" na O.S. (usado em `acao_unica_test.py:182-186,380` e `ben_fluxo_test.py:161`);
   - fica à direita, na barra da coleção (`processo_os.py:1233-1234`, `margin-left:auto`), ao lado dos filtros;
   - um botão por visão válida, com `data-visao`;
   - `aria-label` com o nome ("Ver em kanban");
   - ícone `aria-hidden="true"`, com o mesmo `icon()` do `engine.py:60-63`;
   - sem texto visível.
2. **Estado ativo:**
   - exatamente um botão com `aria-pressed="true"` e os demais `"false"`;
   - o ativo difere por borda ou forma, não só por cor: `borderTopWidth` ≥ 2 px, ou contorno no ativo e nenhum nos outros;
   - fundo diferente de `rgb(30, 122, 76)`, como no teste 29 (`acao_unica_test.py:383-384`);
   - contraste AA do ícone ativo e do inativo contra o trilho, no padrão do `ds_unit.js` §3.
3. **Dica:**
   - hover abre `#g2-dica` com "Ver em kanban";
   - **foco de teclado também abre** a dica;
   - Esc fecha sem tirar o foco (D5 do `ds_test.py:285`);
   - sem `aria-describedby` repetindo o nome (D7, `:292`).
4. **Teclado:**
   - Tab entra no grupo **uma vez**: tabindex itinerante, só o ativo com `tabindex=0`; contar as paradas de Tab, como `acao_unica_test.py:66-69`;
   - seta move o foco **sem** ativar: `aria-pressed` não muda e a visão não troca;
   - Enter ou Espaço ativam;
   - `Home` e `End` funcionam;
   - o foco fica no botão ativado depois de desenhar: o motor redesenha, e o `ds_test` já cobre foco que some, em BEN-D30;
   - sem atalho 1…9.
5. **Só visões válidas:** a contagem de botões é igual a `visoesValidas`. Numa entidade com uma visão só, não existe grupo: `!document.querySelector('[data-visoes]')`.
6. **Primária única:**
   - `EST().prims == ['Nova ordem']` em cada visão (teste 15);
   - `acoes_duplicadas.py` com 0 duplicata em cada visão, pela medida versionada (`acao_unica_test.py:303-305`).
7. **Controle negativo**, no padrão do 29b (`acao_unica_test.py:385-394`):
   - injetar um segundo `aria-pressed=true`, ou tirar o `aria-label` de um botão;
   - a verificação tem de acusar o erro.

### 2.3 Celular (proposta `visoes_test.py celular`)

Na tela de 390 × 844, escala 2, com toque (`c.aparelho(390,844,2,True)`):
1. **Alvos:**
   - cada botão do grupo e o "mais" com ≥ 44 × 44 px (`getBoundingClientRect`);
   - mesmo critério do `etapas_celular_test.py:253-256`.
   - Hoje `SEG_ON` e `SEG_OFF` têm `padding: 6px 14px`, `font 12.5px` (`engine.py:141-142`): cerca de 29 px de altura, abaixo do mínimo.
2. **Celular:** 3 primeiras e "mais", com o ícone Ellipsis e `aria-haspopup`.
   - O "mais" abre uma lista com as demais visões, nome e ícone, que fecha com Esc e devolve o foco.
   - A visão ativa, mesmo que esteja no "mais", fica identificável.
3. **Sem corte:**
   - `MEDE`/`resumo` vazio (`comp_lib.py:125-142`): nada cortado, página sem rolagem lateral, título e "Nova ordem" alcançáveis;
   - mesmos critérios da matriz `componentes_test.py:48-57`.
4. **Toque longo:** 600 ms entre `touchStart` e `touchEnd` mostra a dica (regra do `g2dica`, 500 ms). O `comp_lib.toque` só faz tap, então é preciso um `toque_longo` local.

### 2.4 Ponta a ponta (proposta `visoes_test.py e2e`, também a 390 px)

O roteiro pedido, na O.S., com dados sintéticos:
1. **Filtro:**
   - fase "Em execução" e talhão T1+T2 pelo `ost_btn`;
   - mesmos auxiliares de `tabelas_os_test.py:21-29`.
2. **Trocar a visão para o Kanban, pelo teclado e pelo clique:**
   - os cartões são as linhas da lista, como no TF02 `tabelas_os_test.py:91-92` e no 15 `acao_unica_test.py:181-190`;
   - a nota do recorte aparece;
   - a URL fica com `?view=kanban`.
3. **O filtro continua:** chips e `ost_btn` iguais, busca igual, ordem igual.
4. **Abrir item:**
   - (a) **painel:** o cartão abre o `aside[role=dialog]`; Esc ou Fechar devolve o foco ao cartão;
   - (b) **detalhe completo:** o link do painel leva ao `CA-01det.dc.html` (`ostest.py:60`); depois, `history.back()`.
5. **Voltar:**
   - a visão continua Kanban, pela URL;
   - filtros iguais, pelo `g2keep` em `sessionStorage` (`g2lib.js:16-20`);
   - rolagem ±4 px (`rolagem()`) e foco no item aberto, como o NAV1 L9/L10.
6. **Precedência:**
   - `OS.dc.html` sem `?view` abre na preferência (Kanban);
   - `?view=lista` vence a preferência;
   - `?view=invalida` cai para a preferência;
   - trocar o perfil de demonstração (`perfil_set`, `g2lib.js:278`) usa a preferência do outro perfil;
   - limpar o `localStorage` abre na Lista.
7. **Uma ação de negócio não acontece por trocar de visão:** o `talhao-os-cenario-v1` fica igual, como o `negocio()` ajustado pelo achado 0.2.
8. **Fases consistentes entre visões:**
   - estender o T12 (`testes_pedido.py:144-189`) com as novas visões (Calendário e Mapa da O.S.);
   - a mesma fase do registro em todas as leituras;
   - hoje ele lê Lista, Kanban, App, Detalhe e Mapa IN-04.
9. **Arrastar**, só na fatia que trouxer Calendário:
   - Kanban da O.S. sem `[draggable=true]`;
   - no Calendário, soltar chama a mesma função do formulário: contar chamadas de `carc_janela` ou do ajuste; recusa com o mesmo texto do formulário;
   - "Desfazer" devolve o cenário byte a byte (`localStorage['talhao-os-cenario-v1']`);
   - alternativa sem arrastar, por teclado ou formulário, conforme WCAG 2.5.7.
10. **Cliques medidos antes e depois** (AGENTS §3.3), no padrão `window.__cl` (`ben_fluxo_test.py:56-57`) e NAV1 L12:
    - "filtrar → ver no Kanban → abrir → voltar";
    - com a preferência, voltar à tela poupa um clique.

**Mapa (fatia 3):**
- rodar com `CDP_GL=1`, como o `talmapa_test.py`;
- não reaproveitar a chave `sessionStorage['mapa-ctx']` do IN-04 (`inicio.py:972-976`):
  - o T12 grava essa chave antes de abrir o IN-04 (`testes_pedido.py:169`);
  - os testes `map_*` dependem da camada padrão;
- uma visão Mapa que grave nela muda o IN-04.

---

## 3. Baterias obrigatórias por mudança (AGENTS §3.5, regime leve)

**A cada mudança**, na worktree de rascunho, nunca em `sp-proto`:
1. **Unidade das regras** que vão para o produto: o novo `visoes_unit_test.py`. Com a frente DS integrada, também o `ds_unit_test.py`, que confere o contraste AA do hover e da dica.
2. **Geração e varredura de páginas:**
   - `python3 build.py`, com 0 "MÓDULOS COM FALHA" e saída 0 (`build.py:21,89`);
   - `python3 montar_render.py`;
   - `varredura.py`, hoje com 141 páginas no `project/` e saída 1 se alguma tiver erro (`varredura.py:23-26`).
3. **Testes do módulo mexido.** Para o ViewSwitcher na O.S.:
   - `visoes_test.py` (comp, celular, e2e);
   - `ostest.py`, `tabelas_os_test.py`, `os_irrig_filtro_test.py`, `os_v39_bloq_test.py`, `os_v39_selo_agua_test.py`, `os_cenario_test.py`;
   - `testes_pedido.py T12`;
   - `acao_unica_test.py familias` e `v3`;
   - `../ferramentas/acoes_duplicadas.py . <saida.json> OS`;
   - `componentes_test.py matriz`;
   - `links_ocultos_test.py`, porque lê o `project/`; um link novo para uma tela oculta quebra o L1/L2 (`links_ocultos_test.py:61-79`);
   - na fatia do Mapa, também `map_decisoes_test.py`, `map_irrig_filtro_test.py`, `map_aprov_test.py` e `talmapa_test.py`;
   - na fatia do CD-01, `cadf_fix_lista_test.py`, `cadf_test.py`, `cadc_test.py` e o `tabelas_cad_test.py` da TABR depois da integração;
   - BEN: `ben_fluxo_test.py`, que tem um seletor Lista | Kanban próprio em `processo_beneficiamento.py:22-23`.

**Só a cada marco**, a bateria completa (modelo `docs/parceria/evidencias/v44-tabelas-05/un-20261005/00-bateria.sh`):
- build, montar, varredura e duplicadas;
- `acao_unica` em 5 modos, `componentes` em 5, `etapas_celular` em 3 e `rend` em 4;
- todo `*test*.py` com `CDP_GL=1`. Hoje são 102 arquivos casam com o padrão; `osacoes.py`, `verif_os.py` e `ostela.py` não casam e ficam fora;
- os de unidade.

A integração na branch única segue `docs/integracao/README.md:3-10`:
- merge do commit exato;
- build com 0 FALHA e varredura;
- módulo e regressão, comparados com o pré-merge;
- dois verificadores: A (integridade) e B (persona a 1440 × 900 e 390 × 844, com os 7 critérios NAV-CLAREZA).

**Continua valendo:**
- dados sintéticos (`SAFRION_DADOS=sintetico`);
- nunca declarar teste não executado;
- todo defeito corrigido ganha teste de regressão.

## 4. Comandos (com trava)

```sh
W=/home/user/sp-vis
git -C /home/user/sp-proto worktree add --detach "$W" <commit>      # nunca rodar build/teste em /home/user/sp-proto
cd "$W/tools/prototipo/v37/gen37"
python3 build.py && python3 montar_render.py
SAFRION_DADOS=sintetico python3 visoes_unit_test.py
L='env CHROME_BIN=/tmp/cloudchrome/chrome flock /tmp/cdpV.lock env CDP_GL=1 SAFRION_DADOS=sintetico'
$L timeout 900 python3 varredura.py
$L timeout 900 python3 ../ferramentas/acoes_duplicadas.py . /tmp/…/dup.json OS
$L timeout 900 python3 visoes_test.py comp      # e: celular, e2e
$L timeout 900 python3 ostest.py
$L timeout 900 python3 tabelas_os_test.py
$L timeout 1200 python3 acao_unica_test.py familias   # e: v3
$L timeout 900 python3 componentes_test.py matriz
$L timeout 900 python3 testes_pedido.py T12
git -C /home/user/sp-proto worktree remove "$W"                       # ao fim
```

- **Travas:**
  - existentes hoje: `/tmp/cdp9333.lock`, `cdpB`…`cdpI` e `cdpDS`;
  - os brutos mostram `cdp9333`, `cdpD` e outras;
  - **usar uma trava própria** (por exemplo `cdpV`) e não a de outra frente;
  - `/tmp/cloudchrome/chrome` existe (um invólucro de 380 bytes).
- **`RENDER_DIR`**: `componentes_test` e `acao_unica_test` (`acao_unica_test.py:27`) rodam contra outro `_render`. Serve para o "antes": o vermelho na base prova o teste.
- **Saídas:** os testes imprimem `RESULTADO …` ou `n/m ok` e saem com 1 em falha, exceto `ostest.py`.
  - O `ostest.py` imprime `n ok · m falhas` e **sai com 0 mesmo com falha** (`ostest.py:117`).
  - Conferir o resultado real, não só o código de saída (AGENTS §3.4).

---

## 5. Testes existentes que tocam O.S., Kanban, Mapa e cadastros, e o que quebra com o seletor no cabeçalho

**Legenda:**
- **T**: troca a visão pelo texto visível e quebra com o ícone sem texto;
- **P**: sensível à preferência gravada;
- **H**: sensível ao hash;
- **V**: sensível ao verde, à primária ou à duplicata;
- **D**: depende da estrutura do DOM das visões.

| Arquivo:linha | O que faz | Risco |
|---|---|---|
| `ostest.py:65,78` | `clk('Kanban')` e `clk('Lista')` por `innerText` (`CLK`, `:15`) | **T** |
| `ostest.py:37` | "abre na Lista": `[role=table]`.length == 1 | **D**: só a visão ativa montada (hoje `sc-if` por painel, `ui37.py:487`); **P** se a preferência do mesmo perfil for Kanban |
| `ostest.py:66-72` | 5 colunas `[aria-label="Kanban das ordens"] > div` e cartões `[role=button]` | **D**: não mudar o DOM do Kanban (5 fases, sem coluna nova) |
| `ostest.py:117` | sai com 0 mesmo com falha | conferir a saída, não o código |
| `testes_pedido.py:163` (T12) | `t.clk('Kanban')` por texto (`:12`) | **T**; estender com as novas visões (§2.4.8) |
| `testes_pedido.py:169` | grava `sessionStorage['mapa-ctx']` antes de abrir o IN-04 | não reaproveitar a chave na visão Mapa da O.S. |
| `acao_unica_test.py:182,184,185,186` (teste 15) | `clk('Kanban'/'Recursos'/'Lista','[aria-label="Visão das ordens"]')`, que cai para `aria-label` que começa com (`:46`) | **T** (falha com "Ver em kanban"); **V** (`o0['prims']==['Nova ordem']`, `:190`) |
| `acao_unica_test.py:356-363` (teste 27) | O.S. a 360 × 800, 768 × 1024 e zoom de 200 %: 0 duplicata e ≤ 1 primária | **V** |
| `acao_unica_test.py:375-384` (teste 29) | visão atual da O.S. (`[aria-label="Visão das ordens"] [aria-pressed=true]`) sem o verde cheio | **V**: decide o tom; manter o rótulo do grupo |
| `tabelas_os_test.py:28,91,93,95` | `aba('Kanban'/'Recursos'/'Lista')` por `innerText` | **T** |
| `tabelas_os_test.py:44,52,105` | `negocio()` compara o `localStorage` inteiro | **P**: quebra com a preferência; ajustar o filtro do prefixo |
| `tabelas_os_test.py:100-101` | recarregar `OS.dc.html` (sem `?view`) "conserva talhão e fase" | **P**: abre na preferência; o teste lê `ids()` da Lista e passa só se a última escolha foi Lista (é, pela `:95`) |
| `os_irrig_filtro_test.py:34,70,76,95,97` | `clica('Kanban'/'Lista')` por `innerText` | **T** |
| `os_irrig_filtro_test.py:98` (passo 9) | sem `[aria-label="Visão das ordens"]` no contexto vazio | regra a manter (achado 0.6) |
| `os_irrig_filtro_test.py` passo 5 | IR-03 → `OS.dc.html#OS-0418` | **H** (achado 0.3) |
| `os_v39_bloq_test.py:10,16,23,34,41` | `tab('Kanban'/'Lista')` por `innerText` | **T** |
| `os_v39_selo_agua_test.py:27,50` | `clica('Kanban'/'Lista')` | **T** |
| `os_cenario_test.py:127-129` | `aba('Kanban'/'Lista')` por `innerText` | **T** |
| `ben_fluxo_test.py:161,164` | `clk('Kanban','[aria-label="Visão das ordens"]')`; o `CLK` cai para `aria-label` **igual** (`:56-57`) | **T** (seletor próprio do BEN, `processo_beneficiamento.py:22-23`; vale se o BEN migrar) |
| `cadf_fix_lista_test.py:31,60,78,86` | `vis('Mapa')` por texto em `main [role=group] button` (CD-01 Talhões) | **T** se o CD-01 migrar para ícones |
| `sp-ds/ds_test.py:166,227,299,336` | `[role=group] button` com texto "Kanban" (B3: hover verde na opção de visão; C7: 5 fases; D9 e D13c: dica do selo no Kanban) | **T** (frente não integrada) |
| `osacoes.py:32-33`, `verif_os.py:26-27`, `ostela.py:127` | clicam em "Kanban" e "Lista" por texto | **T**, mas estão fora da bateria (não casam com `*test*.py`) |
| `componentes_test.py:53-57` | matriz de 7 dimensões em SAF, CMP, O.S. e PA (`MEDE`) | corte e alcance na barra da coleção a 360 px |
| `etapas_celular_test.py:107,182,212-215` | O.S. a 390 px e zoom de 200 %: lista alcançável e painel | altura da barra; a lista não pode ficar espremida |
| `ferramentas/acoes_duplicadas.py:11-21` | o mesmo rótulo (`innerText` ou `aria-label`) e o mesmo alvo duas vezes contam como duplicata; fora da conta: `[role=tablist]`, menu, etapas, linha, paginação | **V**: o grupo não está fora da conta. O "mais" no celular não pode deixar visível a mesma visão duas vezes (barra e lista abertas) |
| `links_ocultos_test.py:61-79` | links do `project/` para telas ocultas, por par | Mapa e Calendário não podem levar a telas ocultas (CA-01, PL-04…) |
| `map_decisoes_test.py`, `map_irrig_filtro_test.py`, `map_aprov_test.py`, `talmapa_test.py` | Mapa IN-04, camada O.S., painel do talhão | indiretos: `mapa-ctx` e deep link `OS.dc.html#…` (**H**) |
| `sp-tabr/tabelas_cad_test.py` | grades dos Cadastros, filtro rápido `[role=group][aria-label^="Filtro rápido"]` (`:131-135,382`) | não usar "Filtro rápido" no rótulo do seletor de visão; o `Grade` conta grades visíveis (só a ativa montada) |

**Remédio comum para os T:**
- um auxiliar em `comp_lib.py` (ou num novo `visoes_lib.py`), usado por todos:
  ```python
  VISAO = "((n,g)=>{const r=g?document.querySelector(g):document; const b=r&&r.querySelector('[data-visao=\"'+n+'\"]'); if(!b) return 'NÃO ACHEI visão '+n; b.click(); return 'ok';})"
  ```
- os 13 arquivos trocados no mesmo commit da fatia, na mesma branch;
- cada troca comparada com o pré-merge;
- nenhum teste ignorado.

---

## 6. Software real (`/home/user/Safrion-Software-/apps/web`)

**O que existe:**
- **Duas listagens**, ambas com o componente G2:
  - `/estoque` (lotes, `src/app/(app)/estoque/page.tsx:15-34`);
  - `/cadastros/produtos` (`src/app/(app)/cadastros/produtos/page.tsx:14-33`).
- **Componente G2:**
  - `src/tabela/Tabela.tsx` (558 linhas) e a lógica pura `src/tabela/logica.ts` (348 linhas);
  - estado na URL: `estadoDaUrl` `:251`, `urlDoEstado` `:284`, `hrefComVolta` `:337`, `caminhoDeVolta` `:343`;
  - `Tabela.tsx:79-81` grava com `history.replaceState` e **substitui a query inteira**: um `view` fora do `urlDoEstado` se perde.
- **Tabela agrupada já existe dentro da tabela:**
  - `agrupar` no `EstadoG2` (`logica.ts:48-55`);
  - soma por grupo só com a mesma unidade (`somavel`);
  - menu da coluna "Filtrar e agrupar …" (`Tabela.tsx:352`).
- **Celular:** abaixo de 768 px, a lista vira cartões (`componentes.css:798`; `e2e/celular.spec.ts`).
- **Testes:**
  - **Vitest** (`vitest.config.ts`):
    - unidade em `apps/*/test/**/*.test.ts`;
    - **cobertura ≥ 95 % por arquivo**, e `apps/web/src/tabela/logica.ts` está incluído (`:44`).
  - **Playwright** (`apps/web/playwright.config.ts`):
    - projetos `desktop` e `celular` (Pixel 7), Chrome do sistema;
    - servidor `e2e/servidor.mjs` com banco de DEV;
    - **axe WCAG 2.2 AA** em `e2e/apoio.ts:15-21` (`semViolacoes`).
  - **Não há jsdom nem Testing Library**: componente se testa no Playwright, não no Vitest.
  - `fast-check` disponível.
- **Ícones:**
  - **`lucide-react` não é dependência**: aparece só no manifesto gerado `.next/required-server-files.json`, na lista padrão do Next;
  - não há componente de ícone em `src` (só `src/app/icon.svg`).
- **Ainda não existe:** `packages/ui`, que a BOT-09 aponta como casa do componente comum (`packages/` tem só `contracts`, `db` e `domain`).
- **Ambiente:** o node desta máquina é v22.22.0, mas o `package.json` pede `>=24.21.0 <25`. O `pnpm run doctor`/`check` pode recusar aqui **[a verificar]**.

**Recomendação: só especificar para a transferência; não aplicar agora.**
1. O FOCO v2 é concluir o protótipo; depois vêm tela, domínio, banco e HML.
2. **Uma visão só por entidade, então nenhum seletor:**
   - no software real, a única candidata a duas visões é o Estoque (Lista + Tabela agrupada);
   - a Tabela agrupada já é `?agrupar=` dentro da própria tabela;
   - um seletor seria um segundo caminho para a mesma coisa (§3.4, "uma solução por problema");
   - pela própria regra, "uma só visão → sem seletor".
   - Os dados de DEV têm um lote (`DEMO-001`).
3. **Dependências em aberto:**
   - ícones (Lucide como dependência fixada em `docs/architecture/versions.md`, licença ISC, Renovate, ou SVG próprio);
   - casa do componente (`packages/ui`, só "quando tiver responsabilidade real").
   - São decisões técnicas da transferência, não desta fatia.

**Contrato a levar na transferência:**
- **Lógica pura num arquivo coberto**, `src/tabela/visoes.ts`, com o arquivo incluído na cobertura:
  - `visoesValidas(colunas/atributos)`;
  - `visaoInicial(url, preferencia)`;
  - `visao` dentro do `EstadoG2`;
  - `estadoDaUrl` aceita só visão válida e ignora o resto, como hoje faz com coluna desconhecida (`test/tabela.test.ts:229-252`);
  - `urlDoEstado` e `hrefComVolta` levam a visão.
- **Unidade:** a mesma tabela de casos da §1.2, em Vitest, com `fast-check` para ida e volta da URL.
- **Componente e ponta a ponta:** Playwright nos dois projetos (desktop e Pixel 7):
  - `getByRole('group',{name})`;
  - `getByRole('button',{name:'Ver em kanban', pressed:true})`;
  - `page.keyboard.press('ArrowRight')`;
  - `toHaveURL(/view=kanban/)`;
  - voltar do detalhe (`caminhoDeVolta`);
  - axe em cada visão.
- **Preferência:** por usuário e entidade, no servidor (sessão) ou no `localStorage` com `try/catch`, como faz `src/estoque/rascunho.ts:29-32` com o `sessionStorage`.

---

## 7. Testes por fatia (resumo da lente)

| Fatia | Unidade | Componente e navegador | Regressão obrigatória |
|---|---|---|---|
| 1 · ViewSwitcher + estado + URL + preferência (Lista + Tabela agrupada) | §1.2 completo; `visoesValidas` da entidade da fatia | §2.2 (1-7), §2.3, §2.4 (1-7) na entidade escolhida | build, montar, varredura, duplicadas, `acao_unica familias/v3`, `componentes matriz`, testes da tela; os 13 com **T** passam pelo auxiliar `visao()` |
| 2 · Kanban e Calendário (O.S.) | Calendário só com data relevante; mesmas 5 fases no Kanban | §2.4 (1-10); T12 estendido; Kanban sem `draggable` | todos os da O.S. da §5; `ben_fluxo` |
| 3 · Mapa (Talhão, depois Ocorrência e O.S.) | Mapa só com geometria ou coordenada | `CDP_GL=1`; sem gravar em `mapa-ctx`; T12 com o Mapa da O.S. | `map_*`, `talmapa_test`, `cadf_fix_lista_test`, `links_ocultos_test` |
| 4 · Timeline e Carga por recurso | Timeline só com início **e** fim | a carga por recurso da O.S. já existe ("Recursos"): migrar, não duplicar | `tabelas_os_test` TF02 (Recursos com o recorte) |
| 5 · Matriz, Árvore e Galeria | Árvore só com pai e filho, sem repetir a Lista que já é árvore (CD-01) | idem | testes de cada tela tocada |
