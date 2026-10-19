# Descoberta · infraestrutura do protótipo para o ViewSwitcher (seletor de visões)

- Pedido: proprietário, 10/10/2026 ("a visão nasce do atributo dominante").
- Lente: infraestrutura do protótipo (somente leitura).
- Base lida: `/home/user/sp-proto` = `claude/prototipo-v44` @ `0139898`. Frentes não integradas lidas sem editar:
  - DS: `sp-ds` @ `943433c`, 11 commits à frente;
  - TABR: `sp-tabr` @ `8f19e0d`, 20 à frente;
  - NAV1: `sp-nav` @ `a7023ca`, 5 à frente;
  - PCM: `sp-pcm` @ `ba03515`, 12 à frente;
  - CADUX: `sp-cadux` @ `5d533a8`.
- Caminhos relativos a `tools/prototipo/v37/gen37/`, salvo indicação.
- O que foi executado: leitura de código e `git log/diff`. Também baixei, como dado, os SVG do Lucide 1.45.0 e do Feather 4.29.2 pelo jsDelivr, para comparar caminhos e a licença.
- O que não foi executado: nenhum build, nenhum teste e nenhum navegador. O que depende de execução está marcado **[a verificar]**.

---

## 0. Achados que mudam o plano (resumo)

1. **Já existem 7 seletores de visão diferentes, nenhum compartilhado.** Só o da O.S. aplica o filtro da lista à outra visão. Os outros ignoram o recorte:
   - CD-01 (Mapa): `cad_fazendas.py:349-352`;
   - BEN (Kanban): `processo_beneficiamento.py:63,233`.
2. **A O.S. já tem 3 das visões pedidas sobre o mesmo estado da grade:**
   - Lista;
   - Kanban, que lê o filtro da grade em `processo_os.py:796-804`;
   - "Recursos" (carga por recurso × dia, em `processo_os.py:1158-1205`);
   - mais um "Agrupar por talhão", que é uma Tabela agrupada sobre as mesmas linhas (`processo_os.py:559-567,767-772`).
3. **A troca de visão não guarda nada fora da memória.** O estado do seg vive em `st.sel[segId]` (`engine.py:208-214`). Por isso a escolha:
   - não vai para a URL;
   - não vai para o localStorage;
   - zera no F5 e ao voltar de outra página.
4. **`sc-if` desmonta o painel oculto** (`support.js`, `fe()` devolve `null`). Ao trocar de visão:
   - a rolagem interna da lista (`.g2rola`) se perde;
   - o estado lógico (`self.state.g2`) é mantido.
5. **Pôr a visão no hash quebra links.** Vários leitores de hash usam regex ancorada (`^…$`) ou comparação exata. A convenção de query `?view=` não é usada por nenhuma tela, e todas as escritas de hash preservam `location.search`.
6. **Não há arrastar** (nem Kanban, nem calendário). Não há "desfazer" de fase. A fase da O.S. só muda por comando com papel e pré-condição (`processo_os.py:340-473`; rodapé em `:1251`).
7. **Não há dica no foco em `sp-proto`, só o `title` nativo.** A dica acessível (`g2dica`) está só na DS, ainda não integrada. A regra dela já serve a botão só com ícone: mostra o `aria-label` (`sp-ds g2lib.js:539-544`).
8. **Ícones:**
   - `engine.ICONS` são transcrições de **Feather (MIT)**, sem atribuição no repositório;
   - nenhum ícone de visão pedido existe;
   - os 12 do Lucide 1.45.0 (ISC) foram convertidos para o formato de `icon()` (seção 1).
9. **Choque de nome:** a PCM (não integrada) já usa `#vis=` para a "visão-pergunta" (Sem ordem, Ordens…) e `&modo=kanban` para a apresentação (`sp-pcm areas/maquinas.py:14,81-87,96,296-297`). Por isso, não usar `vis` para o ViewSwitcher.
10. **O Talhão (CD-01) está em reescrita em duas frentes:**
    - TABR: 134 linhas alteradas em `cad_fazendas.py`;
    - CADUX: 651 linhas em `cad_fazendas.py` e 651 em `cadastros.py`.

    A fatia 1 não deve começar pelo Talhão.

---

## 1. `engine.icon()`: ícones, origem, licença e como acrescentar

**Como é hoje**
- `ICONS` é um dicionário Python de `nome → um único atributo d` (`engine.py:12-28`, ampliado em `:29-59`).
- `icon(name,size=16,color)` (`engine.py:60-63`) emite um `<svg viewBox="0 0 24 24" fill="none" stroke-width="1.8" stroke-linecap/linejoin="round" aria-hidden="true">` com **um só `<path d>`**. Consequências:
  - `rect` e `circle` precisam virar subcaminho;
  - nome desconhecido cai num quadrado (`'M4 4h16v16H4z'`, `:62`);
  - `'Mapa'` é alias de `'map'` (`:61`).
- Chaves existentes: `Início, Cadastros, Agronomia, PCP, PCM, Compras, Campo, Irrigação, Oficina, Colheita, Beneficiamento, Vendas, Logística, Controle, Mercado, Indicadores, PCE, Estoque, lista, doc, calc, lab, trend, map, users, pivot, cash, clock, alert, cart, box, card, fuel, scale, tag, truck, check, grid, drop, wrench, leaf, calendar, layers, satelite, monitoramento`.
- Uso direto nas telas: `icon("map"|"doc"|"check"|"leaf"|"calendar"|"alert"|…)` e helpers `_ic/ilink`. Exemplos:
  - `agronomia.py:56-66`;
  - `inicio.py:69,1200-1231`;
  - `maquinas.py:48`.
- `componentes_test.py:325` lê `E.ICONS['satelite'|'monitoramento'|'leaf'|'alert'|'grid']`. **Não sobrescrever chaves existentes.**

**Origem e licença**
- Conferi contra o Feather 4.29.2 (jsDelivr):
  - `users` (`engine.py:35`) tem a mesma geometria do `users` do Feather;
  - `lista` (`:30`) é o `list` do Feather;
  - `alert` é o `alert-triangle` arredondado;
  - `clock` foi adaptado (r 9 em vez de 10).
- Conclusão: os ícones são **derivados do Feather (MIT, Cole Bemis)**, sem nota de licença no repositório. A busca por "lucide|feather" não encontrou nada. Isso é uma lacuna de atribuição, já existente e alheia ao pedido.
- O Lucide é ISC e inclui o aviso MIT do Feather para os ícones herdados. Usar Lucide exige:
  - copiar o aviso ISC e o trecho MIT do `LICENSE` do pacote;
  - um lugar sugerido: `tools/prototipo/v37/gen37/LICENSES/lucide-ISC.txt`, citado num comentário acima de `ICONS`.
- Versão: `lucide-static@1.45.0`, publicada em 2026-09-11 (mais de 2 semanas). A 1.54.0 é de 09/10, recente demais.

**Os 12 ícones pedidos, já no formato de `icon()`**
- Conversão `rect/circle → path` feita por script.
- Chaves novas, com prefixo `v_` para não colidir.
- Origem: `lucide-static@1.45.0/icons/<nome>.svg`.

```python
# Lucide 1.45.0 (ISC; ver LICENSES/lucide-ISC.txt) — ícones do seletor de visões
 'v_lista':'M3 5h.01M3 12h.01M3 19h.01M8 5h13M8 12h13M8 19h13',   # list
 'v_tabela':'M5 3h14a2 2 0 0 1 2 2v14a2 2 0 0 1 -2 2h-14a2 2 0 0 1 -2 -2v-14a2 2 0 0 1 2 -2zM21 9H3M21 15H3',   # rows-3
 'v_tabela_alt':'M15 3v18M5 3h14a2 2 0 0 1 2 2v14a2 2 0 0 1 -2 2h-14a2 2 0 0 1 -2 -2v-14a2 2 0 0 1 2 -2zM21 9H3M21 15H3',   # table-properties
 'v_kanban':'M5 3h14a2 2 0 0 1 2 2v14a2 2 0 0 1 -2 2h-14a2 2 0 0 1 -2 -2v-14a2 2 0 0 1 2 -2zM8 7v7M12 7v4M16 7v9',   # square-kanban
 'v_calendario':'M8 2v3M16 2v3M5 3h14a2 2 0 0 1 2 2v14a2 2 0 0 1 -2 2h-14a2 2 0 0 1 -2 -2v-14a2 2 0 0 1 2 -2zM3 9h18M8 13h.01M12 13h.01M16 13h.01M8 17h.01M12 17h.01M16 17h.01',   # calendar-days
 'v_timeline':'M10 6h8M12 16h6M3 3v16a2 2 0 0 0 2 2h16M8 11h7',   # chart-gantt
 'v_mapa':'M14.106 5.553a2 2 0 0 0 1.788 0l3.659-1.83A1 1 0 0 1 21 4.619v12.764a1 1 0 0 1-.553.894l-4.553 2.277a2 2 0 0 1-1.788 0l-4.212-2.106a2 2 0 0 0-1.788 0l-3.659 1.83A1 1 0 0 1 3 19.381V6.618a1 1 0 0 1 .553-.894l4.553-2.277a2 2 0 0 1 1.788 0zM15 5.764v15M9 3.236v15',   # map
 'v_carga':'M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2M16 3.128a4 4 0 0 1 0 7.744M22 21v-2a4 4 0 0 0-3-3.87M5 7a4 4 0 1 0 8 0a4 4 0 1 0 -8 0',   # users
 'v_matriz':'M5 3h14a2 2 0 0 1 2 2v14a2 2 0 0 1 -2 2h-14a2 2 0 0 1 -2 -2v-14a2 2 0 0 1 2 -2zM3 9h18M3 15h18M9 3v18M15 3v18',   # grid-3x3
 'v_arvore':'M8 5h13M13 12h8M13 19h8M3 10a2 2 0 0 0 2 2h3M3 5v12a2 2 0 0 0 2 2h3',   # list-tree
 'v_galeria':'M4 3h5a1 1 0 0 1 1 1v5a1 1 0 0 1 -1 1h-5a1 1 0 0 1 -1 -1v-5a1 1 0 0 1 1 -1zM15 3h5a1 1 0 0 1 1 1v5a1 1 0 0 1 -1 1h-5a1 1 0 0 1 -1 -1v-5a1 1 0 0 1 1 -1zM15 14h5a1 1 0 0 1 1 1v5a1 1 0 0 1 -1 1h-5a1 1 0 0 1 -1 -1v-5a1 1 0 0 1 1 -1zM4 14h5a1 1 0 0 1 1 1v5a1 1 0 0 1 -1 1h-5a1 1 0 0 1 -1 -1v-5a1 1 0 0 1 1 -1z',   # layout-grid
 'v_mais':'M11 12a1 1 0 1 0 2 0a1 1 0 1 0 -2 0M18 12a1 1 0 1 0 2 0a1 1 0 1 0 -2 0M4 12a1 1 0 1 0 2 0a1 1 0 1 0 -2 0',   # ellipsis
```

- **Tamanho.** Pelo CORR-DS-33 (PRD l.15224), ícones só em 12, 14, 16, 20 e 24 px. Para o seletor: 16 px no computador e 20 px no toque.
- **Contraste.** O traço 1,8 de `icon()` é mais fino que o 2 do Lucide; o "mais" (círculos de r=1) fica pequeno. **[a verificar]** contraste e legibilidade a 16 px.
- **Software real.** `apps/web` não tem `lucide-react` (`apps/web/package.json`). Já usa `searchParams` (`src/app/(app)/estoque/page.tsx`, `cadastros/produtos/page.tsx`), o que facilita o `?view=` lá.

---

## 2. Estado da grade (`g2lib.js`) e se ele já é compartilhável entre visões

**Onde vive.** `self.state.g2[gridId]`, lido por `g2st(self,id)` (`g2lib.js:12`) e escrito por `g2set(self,id,patch)` (`:13-14`). Chaves:

| chave | o quê | onde |
|---|---|---|
| `f` | filtros por coluna `{col:[valores]}` (multivalor por ID, `g2fkeys`) | `:26,29-35,164-175` |
| `q` | busca | `:32-33,203` |
| `so` | ordenação `{k,d}` | `:36-38,147-149,173` |
| `qv` | filtro rápido (chips) | `:43-55` |
| `x` | grupos expandidos | `:77-84,190-192,218-223` |
| `sel` | seleção por ID (caixas) | `:181-182,206-216` |
| `fm` | formulário lateral aberto = **rascunho** `{rid,draft,orig,errs,warn,ro,isNew,mode}` | `:104-139,228-248` |
| `fl` | linha realçada depois de salvar ou escolher | `:111,135,199` |
| `fmc,fpos,fmd,fmq` | menu de filtro da coluna aberto, posição, marcação e busca | `:150-176` |
| `cf` | confirmação de exclusão | `:195-197` |
| `rows` | linhas alteradas (salvar/excluir) | `:20,133-136` |

**Persistência.**
- `g2keep(self,id)` (`:15-19`) guarda **só `f,q,so,qv`** em `sessionStorage['g2:<arquivo>:<id>']`.
- Só a O.S. chama (`processo_os.py:535`; `g_os`).
- **Não guarda:** `sel`, `x`, rolagem, `fm`, a visão escolhida, nem os filtros do topo `mf_faz`/`mf_saf`.
- Os filtros do topo são estado da página, voltando sempre a "Santa Rita"/"Todas" (`engine.py:1433-1435`).
- **[a verificar]** Ao voltar de outra página, um `f.tal` de outra fazenda pode ser restaurado com `mf_faz` de volta a Santa Rita, e a lista fica vazia com "filtro ativo".

**Compartilhável entre visões?**
- Sim, por construção: o estado é por `gridId`, e não pela visão.
- A ordem de montagem ajuda (`engine.py:1437-1440`): `PREVALS` → `g2vals` para cada grade → `EXTRAVALS`. Em `EXTRAVALS`, `v[gid+'_rows']` já existe filtrado, ordenado e achatado (`g2lib.js:178-200`).
- **Como cada tela usa isso:**
  - **Bom exemplo:** os cartões de celular de Produção e BEN derivam de `v[gid+'_rows']` (`producao.py:179` `prCards`; `processo_beneficiamento.py:235`). São a mesma fonte, com o mesmo filtro e a mesma ordem.
  - **O.S. › Kanban:** reaplica `g2match(r,spO,stO)` sobre `__osBase` (`processo_os.py:796-798`). Respeita filtro e busca, **não** respeita a ordenação (`so`); a ordem é a do registro. O filtro ativo fica escrito com "Limpar filtros" (`:799-804`, nota em `:1229-1230`).
  - **O.S. › Recursos:** usa o mesmo conjunto (`okId`) para mostrar ou esconder blocos `rcv_*` (`:805-807`).
  - **O.S. › seleção do item:** é `st.pan`, comum às 3 visões. O cartão aberto ganha borda (`:837`).
  - **Ruim (CD-01):** o Mapa pinta todos os talhões da fazenda pela situação, ignorando o filtro rápido `cd_qf` e a busca (`cad_fazendas.py:349-352,379-381`). Tem um seletor de fazenda próprio (`cdm`, `:263,377`).
  - **Ruim (BEN):** o Kanban usa todas as ordens (`bnKanban(self,c,ords)`, `processo_beneficiamento.py:63,233`), não o recorte de `g_ob`.
- Em árvore, `v[gid+'_rows']` só traz os filhos expandidos. Para alimentar outra visão, use `g2flat` com tudo expandido, ou `g2match` nas folhas.
- **Recomendação:** um único `g2visiveis(self,gid)` em `g2lib`, com `g2qrows` + `g2flat` + `g2sort` sobre as folhas, devolvendo IDs, para alimentar toda visão. O Kanban, o Calendário e o Mapa leem dele.

**Rascunho e troca de visão.** O formulário e o painel são modais com véu (`g2lib.js:341-367`), então não há como trocar de visão com um rascunho aberto. Não há risco de perder rascunho pela troca.

**Rolagem.**
- `sc-if` desmonta o painel oculto, e a rolagem da `.g2rola` se perde ao ir e voltar.
- Padrão reaproveitável: `g2etapa(self,patch,pos)` restaura `{top, rolas[i]}` (`g2lib.js:382-387`). NAV1 guarda `[elemento,scrollTop]` ao abrir e devolve ao voltar (`sp-nav areas/processo_planos.py:129-131,452-453`).
- Para a visão: guardar `{main[data-scroll].scrollTop, .g2rola.scrollTop/scrollLeft}` por visão antes do `setState` e restaurar no `setTimeout` (como em `g2etapa`). Para atravessar páginas, usar `sessionStorage`.

---

## 3. URL: convenções atuais e como encaixar a visão

**Inventário**

| Tela / arquivo | Formato | Leitura |
|---|---|---|
| O.S. `processo_os.py:754-763` | `#OS-0420`, `#OS-0430:ajustar`, `#tal=Faz\|T1`, `#nova:c:a:AAAA-MM-DD` | regex **ancorada** `^…$` (`:755,758,760`); só na carga e no `hashchange`; abrir o painel **não** grava hash |
| SAF `safra.js:1276-1325` | `#saf=S2627&passo=cultivos&cult=c5` | `[#&]saf=` tolerante; grava com `location.hash=` |
| Compras `processo_compras.py:198,483-492` | `#sol=…&saf=…` | tolerante; `replaceState(pathname+search+h)` |
| CD-01 `cadastros.py:233-235` | `#talhao=T1&aba=geometria` | `cadHash` troca só `aba=` e preserva os outros; `replaceState(null,'','#'+…)` |
| CD-01 → det `cad_fazendas.py:324` | `CD-01det.dc.html#talhao=ID` | `location.href=`; a volta é o `PARENT37`, link simples `CD-01.dc.html` (`:499`): **perde aba, visão e filtros** |
| Mapa IN-04 `inicio.py:1092-1094`, `talmapa.js:162-167` | `#car`, `#car:T1`, `#desenhar=ID`, `#importar`, `#talhao=ID` | `#car` ancorado; o resto tolerante. Contexto em `sessionStorage['mapa-ctx']` (`inicio.py:972-976`: `mf_faz, lay, tsel, flt, zoom, osel, px`) |
| Agronomia `agronomia.py:621,643,851,1419-1420` | `#VIS-12[:decidir\|programar]`, `#reg-…`, `#<id>` | ancorado ou exato |
| MA base `maquinas.py:421` · BEN `processo_beneficiamento.py:272-274` · Produção `producao.py:353-354,483-484,639` · Irrigação `irrigacao.py:141-143` · Mobile `mobile.py:680,753,821` | `#<id>` puro, `#OS-0422:janela` | igualdade exata ou `^…$` |
| PCM (não integrada) `sp-pcm maquinas.py:14,33-34,81-101` | `MA.dc.html#vis=ordens&modo=kanban&om=OM-0233` (`ma_hashLer/De/Sync`) | tolerante; `replaceState` preserva `search` |
| NAV1 (não integrada) `sp-nav processo_planos.py:126-128` | `PA.dc.html#plano=ID` | lido na carga e no `hashchange`, gravado ao abrir |
| `?query` | ninguém usa (só `agrofit_test.py:89` `?falha=1`) | — |

**Conclusões**
- **Não usar o hash para a visão.** `#OS-0420&view=kanban` deixa de casar em `processo_os.py:760`, e o mesmo vale para `#car`, `#VIS-…`, `#OS-…` e as igualdades exatas `oms[h]`/`lotes[h]`. Corrigir todos os leitores é trabalho e risco desnecessários.
- **Usar `?view=<k>`, como pediu o proprietário.** Motivos:
  - todas as escritas de hash do protótipo preservam `location.search`, seja por `pathname+search+h` (`processo_compras.py:198`, `agronomia.py:643`, `dados_manutencao.py:295`, `sp-pcm ma_hashSync`, `sp-nav paHashSet`, `inicio.py:1094`), seja por URL relativa `'#'+…` (`cadastros.py:234`, `agronomia.py:1420`) ou por `location.hash=` (`safra.js:1324`);
  - `g2keep` usa só o `pathname` (`g2lib.js:17`), então a chave dos filtros não muda.
- Escrever com `history.replaceState(history.state,'',pathname+'?'+params+location.hash)`, nunca `pushState`, para o Voltar sair da tela e não percorrer visões. Assim a entrada atual do histórico guarda a visão, e o Voltar de uma página de detalhe volta a ela.
- Links do menu e de outras telas não levam `?view`, e aí vale a preferência. É o comportamento certo pela precedência.
- **Valores:** chaves curtas em pt, sem acento: `lista, agrupada, kanban, calendario, timeline, mapa, carga, matriz, arvore, galeria`.
  - Visão inválida para a entidade: ignorar, seguir a precedência e avisar uma vez ("Visão indisponível nesta lista: abrindo em Lista").
  - **PCM:** `#…&modo=kanban` deve virar alias de `?view=kanban` na integração (uma solução por problema, AGENTS §3.4), e o `#vis=` da PCM continua sendo a visão-pergunta.
- **[a verificar]** O host do artefato publicado (`prep_site.sh` copia `_render/*.dc.html` como arquivos) precisa servir `X.dc.html?view=…` e manter a query no F5. O fragmento nunca vai ao servidor; a query vai. Se o host recusar a query, o fallback é `#…&view=` com um parser tolerante e a correção dos leitores ancorados listados acima.

---

## 4. Preferências: chaves e onde guardar perfil × entidade

**localStorage hoje**
- Preferências: `safrion.menuRecolhido` (`g2lib.js:256,280`) e `safrion.perfilDemo` (`G2_PERFIL_KEY`, `g2lib.js:263-265,278`).
- Cenário e dados: `talhao-os-cenario-v1` (`CEN_KEY`), `talhao-os-cd01-v1`, `-mip-v1`, `-irrigacao-v1`, `-compras-v1`, `-manutencao-v1`, `-cadastros-v1`, `-mb-os`, `ASSIN_KEY` e outros.
- `sessionStorage`: `g2:<arquivo>:<grid>`, `mapa-ctx`, `irr-faz`. A DS acrescenta `g2nav` (`sp-ds g2lib.js:524`).
- Todas as leituras usam `try{…}catch(e){}`, com cópia em memória quando falham (`G2_PERFIL_MEM`, `g2lib.js:263-265`).

**Perfil.**
- `g2perfil()` (`g2lib.js:265`) devolve o perfil salvo, ou `G2_PERFIS[0]` (Ana).
- A troca acontece em `v.perfil_set`; outra aba avisa por `window 'storage'` (`g2lib.js:276-279`). Cada tela diz o que fecha em `self.g2perfilFecha`; na O.S. é `{pa:null}` (`processo_os.py:749`).

**Proposta**
- **Chave plana**, no estilo das duas existentes: `safrion.visao.<perfil.k>.<entidade>` (ex.: `safrion.visao.Ana.os` = `kanban`). Com prefixo, o teste limpa fácil (`Object.keys(localStorage).filter(k=>k.startsWith('safrion.visao.'))`).
- Ler e gravar sempre com `try/catch`. Validar contra as visões válidas da entidade: um valor antigo ou removido é ignorado.
- Gravar a preferência só quando a pessoa clica no seletor. Não gravar ao abrir por URL, para um link compartilhado não mudar a preferência de quem abre.
- **Restaurar demonstração não apaga preferências:** `cenReset` só remove `CEN_KEY` (`cenario.js:12`), e isso está certo, porque a preferência não é cenário.
- **Trocar de perfil não muda a visão aberta.** Só a próxima entrada sem `?view` usa a preferência do novo perfil. Decisão técnica minha; registrar.

---

## 5. Dica acessível

**`sp-proto` (base)**
- Só `title` nativo, que não aparece no foco nem no toque.
- O chip tem `p.dica` → `title` + `.g2sr` para leitor de tela (`g2lib.js:85-89`; `engine.py:1145`).
- Os botões do mapa usam `title` + `aria-label` (`inicio.py:1200-1201`).

**`sp-ds` (`DS-DICA-20261009`, não integrada), em `sp-ds g2lib.js:526-630`**
- **Texto** (`g2dicaRegra`, `:539-544`), em ordem de prioridade: `data-dica` explícito, depois `data-dica-de` (dicionário `G2_DICAS`), depois um `title` que acrescente algo ao rótulo visível, depois **o `aria-label` de comando sem letra nem número visível** (`button,a[href],[role=button]`).
  - Um botão só com ícone e `aria-label="Ver em mapa"` ganha a dica "Ver em mapa" **sem nenhum atributo a mais**.
- **Abertura:**
  - ponteiro fino: hover de 300 ms;
  - foco (`focusin`): na hora;
  - toque: toque longo de 500 ms, sem acionar o comando (`:600-618`).
- **Fechamento:** sair, perder o foco, `Esc` (captura, `:610-611`; a explícita consome a tecla), redimensionar, ou o gatilho sumir (`:628-629`).
- **ARIA:**
  - `role=tooltip` com id `g2-dica`;
  - `aria-describedby` só quando o texto difere do nome acessível (`:580-581`); no botão só com ícone eles são iguais, e não há leitura dupla;
  - `title` igual ao rótulo sai durante o hover (`:590-596`).
- **Botão indisponível:** `aria-disabled="true"` com motivo; o clique é recusado e a dica diz o porquê (`:625-627`); o motivo também aparece em texto (VIS-04).
- **Dependência:** o ViewSwitcher precisa da DS integrada, ou duplicaria a dica (contra AGENTS §3.4). Se vier antes, ponha `aria-label` + `title` e deixe a DS cobrir depois.
- **Teste:** a DS já tem `ds_test.py` e `ds_unit.js`/`ds_unit_test.py`. Basta acrescentar um caso "botão do seletor com foco → `#g2-dica` visível com 'Ver em …'".

---

## 6. Teclado: atalhos existentes e foco circulante

**Globais**
- `g2glob` (`g2lib.js:289-339`): `Enter` no rótulo de etapa; `Esc` fecha a lista de etapas e o menu sobreposto (respeita `e.defaultPrevented`).
- Modal (`:345-367`): `Tab` preso no painel e foco devolvido a quem abriu.
- Por tela:
  - `agTeclas` (`agronomia.py:1438-1444,1491`);
  - Esc da PCM (`maquinas.py:73`);
  - BEN (`processo_beneficiamento.py:258`);
  - Irrigação (`irrigacao.py:122`);
  - PA na NAV1 (`sp-nav processo_planos.py:161`).
- **Sem atalhos 1…9 nem `/`.** Pela regra do pedido, não implementar números.

**Setas**
- Só no autocompletar `g2ac` (`g2lib.js:58-76`, `aria-activedescendant`).
- **Não há foco circulante (roving tabindex) no projeto.** Os grupos `aria-pressed` existentes (`ui37.tabs`, `cadastros.seg`, `.pr-vis`, chips) são um botão por parada de Tab.

**Proposta para o seletor**
- `role="group"` com `aria-label="Visão de <entidade>"`, um `button` por visão e `aria-pressed`.
- Foco circulante: a visão ativa tem `tabIndex=0`, as outras `-1`.
  - ←/→ (e ↑/↓) movem o foco com volta; Home/End vão às pontas.
  - Enter e Espaço ativam (nativo do `button`).
  - É um handler `onKeyDown` no grupo, como o `acTecla` de `g2ac`.
- O "mais" no celular abre uma lista (`aria-haspopup="menu"`/`aria-expanded`). Esc fecha e devolve o foco ao "mais" com `preventDefault` + `stopPropagation`, para não acionar o Esc de `g2glob`.

---

## 7. Master-detail da O.S.: painel, volta e preservação; abas Lista/Kanban/Recursos

**Abas**
- `ui37.tabs(opts,contents,active,label)` (`ui37.py:476-488`) usa `engine.seg_buttons` (`engine.py:171-175`): `role="group"`, um `button` por opção com `aria-pressed`, rótulo em texto e sem ícone.
- Na O.S.: `tabs(['Lista','Kanban','Recursos'],…,label='Visão das ordens')` em `processo_os.py:1232`, à direita da barra da coleção (`:1233-1234`). Fica fora da barra da grade, porque os filtros (Talhão, chips de fase, Agrupar) valem para as três.
- **Trocar** grava `st.sel[segId]=i` e `open:null`, e fecha pick/menu/drawer do motor antigo (`engine.py:213`). **Não zera** `g2` (filtros, busca, ordenação), `pan`, `pa` nem `os_agr`.
- **Não persiste:** F5 ou voltar de outra página voltam a "Lista".
- **Estilo ativo:**
  - seg: `SEG_ON` branco com sombra (`engine.py:141-142`);
  - `ACOES_CSS` transforma escolhas desenhadas como cheias em tonais (`engine.py:1071-1074`);
  - `acao_unica_test.py:376-384` (caso 29) exige que a visão atual da O.S. **não** seja verde cheio;
  - **Conflito com o PRD:** o 74.5.10 (`docs/PRD.md:14299+`) manda a opção escolhida em `cor.acao.primaria` com texto inverso, e o protótipo usa o tonal (DS-36 v2; `sp-ds engine.py:1011` `_TONAL`). O ViewSwitcher deve seguir o protótipo vigente e registrar a divergência.
  - **Sinal sem cor:** reaproveitar a barra interna inferior de 2 px da etapa atual (`box-shadow:inset 0 -2px 0 #1E7A4C`, `g2lib.js:371`) mais `aria-pressed`.

**Painel**
- Clique na linha (`g2pick` → `setState({pan:id})`, `processo_os.py:765`), no cartão do Kanban (`:838`) ou no bloco de Recursos (`op_*`, `:764,1191`) abre um `aside role=dialog` sobre véu fixo (`:1098-1126`).
- A lista fica montada por baixo, então filtros, visão e rolagem continuam intactos.
- Fechar: ×, véu ou Esc (`:841-842`); o foco volta a quem abriu (`g2lib.js:356-366`).
- `#OS-xxxx` abre o painel uma vez (`:754-763`). Abrir **não** grava o hash, e o F5 não reabre.
- Não há mais página de detalhe da O.S. (o docstring `:10` cita "Abrir ordem", mas o painel é o único detalhe).
- **Para o e2e "abrir item → voltar":** na O.S. o critério já passa pelo painel, que fica na mesma página. A dificuldade está nas listagens com **página** de detalhe, como CD-01 → CD-01det (`cad_fazendas.py:324,499`). Lá o Voltar perde:
  - a aba;
  - a visão (`cd_vis`, `:382`);
  - os filtros (`g_tal` não chama `g2keep`);
  - a rolagem.

**Outros seletores de visão (inconsistentes; unificar no componente único)**

| Tela | Visões | Implementação | Filtro compartilhado? |
|---|---|---|---|
| `OS.dc.html` | Lista · Kanban · Recursos (+ Agrupar por talhão) | `ui37.tabs` (`processo_os.py:1232`) + botão `os_agr` (`:968`) | sim (Kanban sem a ordenação) |
| `CD-01` Talhões | Lista · Mapa | `cadastros.seg/cadSeg` (`cadastros.py:166-169,237-238`; `cad_fazendas.py:259,263,382`), duplicado na barra da lista e na do mapa | **não** |
| `BEN` | Lista · Kanban | `.pr-vis` (`processo_beneficiamento.py:22-28,232`) | **não** (Kanban) |
| `PROD` | Por talhão · … | `.pr-vis` (`producao.py:36-38,502-505,623-624`) | a verificar |
| `CA-01` (legado, fora do menu; `ui37.py:45` manda para a O.S.) | Lista · Kanban · Mapa | `ui37.tabs` com Kanban e Mapa estáticos (`campo.py:196-198`) | não |
| Suprimentos | Por carga · item · depósito · mês | `ui37.tabs` com 4 grades diferentes (`suprimentos.py:575-590`) | não (são agrupamentos, cada um com seu filtro) |
| MA na PCM (não integrada) | Lista · Kanban em Ordens | `om_modos`/`ma_pill` (`sp-pcm maquinas.py:296-297`), `&modo=kanban` no hash | a verificar |

**Testes que clicam pelo texto das abas** (somem com botões só de ícone; trocar o helper para `aria-label`):
- `acao_unica_test.py:182-186,380`;
- `ben_fluxo_test.py:161`;
- `cadf_fix_lista_test.py:60,78,86`;
- `os_cenario_test.py:128`;
- `os_irrig_filtro_test.py:70,95`;
- `os_v39_bloq_test.py:16-41`;
- `os_v39_selo_agua_test.py:50`;
- `tabelas_os_test.py:91-93`;
- e as ocorrências em `ostest.py` e `testes_pedido.py`.

---

## 8. Mapa: dá para virar visão de uma listagem?

**Implementações existentes (4, com geometria duplicada)**
1. **IN-04 Mapa** (`inicio.py`):
   - Santa Rita em SVG: `GEO` (`:93-96`, viewBox 1000×620), com camadas `LAYS` (`:99-101`, inclui "O.S./prazos" com filtro de fase em `:107`) e ordens por talhão em `_ORD_MAPA` (`:120-157`);
   - o SVG é interativo e acessível, com `tabIndex=0 role=button aria-label` por talhão (`_mapsvg`, `:1101-1131`);
   - Lagoa Grande é **MapLibre GL 5.9.0 por CDN** (`:520-521,562-579`) + Sentinel-2, com o singleton `LGI`;
   - o cartão do mapa (`_mapcard`, `:1193-1233`) tem filtros por camada, ferramentas e painel;
   - entrada por URL **não** aceita um recorte de lista: só `#car`, `#talhao=ID` (só Lagoa Grande), `#desenhar=` e `#importar`. O contexto fica em `sessionStorage['mapa-ctx']`.
2. **CD-01** (`cad_fazendas.py`): `GEO_MAPA` (`:206`, **outra cópia** da Santa Rita, com coordenadas diferentes, viewBox 1000×460) e `_mapa`/`_mapa_lg` estáticos com furos de cor (`:211-244`).
   - Falhas: ignora o filtro da lista; os polígonos **não** têm foco nem papel (sem `tabIndex`/`role`/`aria-label`); usa `title` nativo.
3. **CA-01** (legado): caixas fixas (`campo.py:140-164`).
4. **PL-02**: `_mapa_t1` (`planejamento.py:80-91`).

**Visão Mapa de uma listagem.**
- **Viável com SVG**, no modelo do `_mapsvg` (acessível) e não do `_mapa` do CD-01:
  - uma função Python `mapa_visao(pre, fazenda)` com furos `pre+'_f_'+id`, `pre+'_s_'+id`, `pre+'_a_'+id` (rótulo) e `pre+'_k_'+id` (clique/tecla);
  - em JS, `g2visiveis(self,gid)` → IDs → talhões (`m.tal`, multivalor por `faz|tid` na O.S., `processo_os.py:537,551`) → cor e destaque por talhão;
  - fora do recorte fica neutro e sem ação;
  - o clique abre **o mesmo detalhe** (`g2pick`/`pan`).
- **Não reutilizar o MapLibre na listagem:** depende de rede, singleton e imagens fora do repositório (`montar_render.py`). Para Lagoa Grande, usar o círculo do KML do `_mapa_lg` (centro + área declarada).
- **Antes:** consolidar a geometria numa fonte só, `dados.py`/`dados_cad.py`, usada por IN-04, CD-01 e pela visão. Hoje `inicio.py:93` ≠ `cad_fazendas.py:206`.
- **Vistoria/Ocorrência:**
  - têm coordenadas (`dados_mip.py:104` `lat/lon` do talhão; `:247` GPS dos pontos), então Mapa é sustentado;
  - **Galeria não é:** as "fotos" são placeholders (gradiente + ícone, `agronomia.py:884-916`, em `:914`).

---

## 9. Calendários, gantt, timeline e heatmap reutilizáveis

- **Não existe componente de calendário mensal, gantt ou linha do tempo** no protótipo. A busca por calendário, gantt, timeline, linha do tempo e heatmap só achou textos e colunas.
- **Carga por recurso:**
  - O.S. › Recursos, `_recursos_tab` (`processo_os.py:1158-1205`): grade recurso × dia em HTML;
  - os dados vêm de `alocacao.py` (`DIAS`, `RECURSOS`, `ALOC`, `semana()`, `conflitos()`), uma **semana fixa 22–27/09 gerada em Python**: ordem nova do cenário não entra;
  - o filtro da lista só esconde blocos (`rcv_*`).
  - Uso: reaproveitar como está para "Carga por recurso" da O.S. (renomear e pôr o ícone `v_carga`). Para Máquina, filtrar `AL.semana()` por recurso.
- **Matriz:** Planejar safra `g_cap` (recurso × mês como grade g2) com células tocáveis que filtram (`p.full`, `aria-pressed`, 44 px; `processo_safra.py:184-194`, `g2lib.js:93`). É o modelo para "talhão × semana".
  - Risco: a TABR pede "uma variável por coluna" (`processo_os.py:534`). Colunas por semana são pivô da mesma variável; alinhar com a TABR antes.
- **Agenda por dia:**
  - "Esta semana" da PCM: OMs por dia com HH por especialidade (`sp-pcm maquinas.py:298-300`, não integrada);
  - IN-03 "Agenda e pendências" é lista (`inicio.py:1397-1453`);
  - IR-02 "Agenda por captação" é grade (`irrigacao.py:287`).
- **Eixo de tempo em SVG:** `_curva` (barras por semana, `planejamento.py:93-106`) serve de base para Timeline e Gantt.
- **Dados que sustentam as visões:**
  - O.S.: `ini`/`fim` (datas ISO nas colunas, `processo_os.py:1221`) sustentam Calendário e Timeline;
  - Safra: `ini`/`fim` (`D2.SAFRAS`, `processo_safra.py:191`) sustenta Timeline;
  - OM da PCM: `janIso`.
- **Tabela agrupada:**
  - já existe na O.S. como "Agrupar por talhão": regrupa as mesmas linhas, conta O.S. distintas e soma a área (`processo_os.py:559-567,767-772`);
  - árvores fixas: Talhão por fazenda (`cad_fazendas.py:256-260`, subtotal por fazenda) e Estoque item › lote (`processo_estoque.py:116-120`);
  - o total do rodapé soma só o nível 0 (`g2sum`, `g2lib.js:96`). Generalizar o `os_agr` num helper `g2agrupar(rows,chave,somas)`.
- **Árvore do Talhão:** é fazenda › talhão (› parcela no CD-01det, `g_parc`, `cad_fazendas.py:507-509`). "Setor" é **atributo** (pivô ou setor de irrigação, `:93,132`), não nível. A árvore "fazenda › setor › talhão" da sugestão não é sustentada pelos dados atuais.

---

## 10. Arrastar e desfazer no Kanban e no calendário

- **Não há arrastar** em lugar nenhum (busca por `draggable`, `drag` e `drop`). O único arraste é o pan do mapa (`inicio.py:554`).
- **A fase da O.S. só muda por comando** gravado com `cenMudar`, que aplica numa cópia, grava atômico ou devolve o erro sem gravar (`cenario.js:15-21`), via `osRun` (`processo_os.py:315`):

  | Mudança de fase | Comando | Linha |
  |---|---|---|
  | A liberar → Liberadas | `osc_liberar`/`osc_libEfeito`, com aprovação + liberação, `cenLiberar` com reserva por lote e trava legal `cenUsoLegal` | `:340-365` |
  | Liberadas → Em execução | `osc_iniciar` | `:415` |
  | Em execução → Em conferência | `osc_conferencia` | `:443` |
  | Em conferência → Encerradas | `osc_encerrar`, só com `cenPodeEncerrar` vazio | `:447` |
  | Cancelar sem execução | `osc_cancelar`, papel gestor | `:454` |

  - Os papéis são conferidos por `cenExige`/`cenExigeUm` (`cenario.js:68-70`). O próximo passo e o impedimento vêm de `osProx` (`processo_os.py:484-506`).
  - **Não há comando de volta de fase nem "desfazer"**. O rodapé da tela diz "A fase só muda por evento" (`:1251`).
- **Conclusão para o Kanban da O.S.:** arrastar não pode mover direto.
  - No máximo, soltar na coluna seguinte **abre a mesma confirmação do painel** (`v.pan_go`, `:635`), com a mesma validação, papel e trava legal, e a pessoa confirma.
  - Para trás: recusar com o motivo.
  - "Desfazer" de liberar ou encerrar não existe no domínio e criaria movimento de estoque (reserva). O dano evitado é um duplo movimento, S2. **Não oferecer.**
- **Datas (Calendário):**
  - comandos existentes: `carc_janela` (colheita, `dados_carencia.py:430`; usado em `processo_os.py:1283`), "Mover janela" da PCM (D-38, `sp-pcm`), "Reprogramar janela" em Logística (`logistica.py:161`);
  - o padrão de desfazer amigável ao domínio está em `assinDesfazer` (`assinatura.js:159-169`): grava um fato de compensação e não apaga nada;
  - um "desfazer" de mudança de janela teria de ser um novo comando com chave de idempotência (ENG-021/022), não uma reversão local.

---

## 11. Recomendações de infraestrutura (especificado; não executado)

1. **`engine.py`:**
   - acrescentar os 12 `v_*` (seção 1) e o arquivo de licença ISC/MIT, incluindo a atribuição do Feather para os ícones existentes;
   - criar o helper `visoes(pre, ent, opcoes)`, que gera o grupo:
     - `aria-label="Ver em <nome>"`, `title` igual;
     - `icon(...,16)`, `data-visao=<k>`, classe `g2vis`;
     - CSS de 32×32 px no computador e `@media (pointer:coarse){.g2vis button{min-width:44px;min-height:44px}}` (padrão de `engine.py:1062,1084`);
     - ativo tonal com barra interna inferior de 2 px.
   - Lugar: o slot `tools` à direita da barra da grade (`engine.py:1198-1200`, "visão/apresentação: fim da barra") ou a barra da coleção quando os filtros valem para todas as visões (`processo_os.py:1233-1234`).
   - Com uma visão só, não renderizar nada. No estreito (`G2_ESTREITO`, `g2lib.js:254`), mostrar 3 botões + "mais".
2. **`g2lib.js`:** criar quatro helpers.
   - `g2visao(self,ent,validas)`, com precedência `?view` › `safrion.visao.<perfil>.<ent>` › `validas[0]`. Faz o `replaceState` da query, grava a preferência ao clicar (com try/catch) e guarda e restaura a rolagem por visão.
   - `g2visiveis(self,gid)`, que alimenta toda visão (seção 2).
   - `g2keep` estendido, opcionalmente com `sel` e com os filtros do topo.
   - `g2agrupar` (seção 9).
3. **Fatia 1:**
   - **O.S.** é a entidade de menor custo: Lista + Tabela agrupada já compartilham o mesmo `g_os` (`os_agr`), e Kanban e Recursos já existem;
   - converter as abas atuais é trocar `ui37.tabs` pelo componente;
   - Talhão está em reescrita (TABR/CADUX) e deve ficar para depois da integração delas;
   - EST é a alternativa (`g_lot` em árvore).
4. **Ordem de integração:** DS (dica, hover, tonal) → ViewSwitcher. Antes, combinar com a TABR o pivô da Matriz e com a PCM o alias `modo=kanban`.
5. **Testes:**
   - **Unidade, em Node como os `*_unit.js`:** visão inicial pela precedência; visões válidas por entidade; valor inválido; storage que falha.
   - **Componente, pelo `cdp.py`:**
     - `aria-label`/`aria-pressed`;
     - roving (Tab entra uma vez e as setas circulam);
     - Enter/Espaço;
     - dica no foco (`#g2-dica`, com a DS);
     - 44 px em `pointer:coarse`.
   - **E2E (critério NAV-CLAREZA):** filtro → trocar visão → filtro mantido (nota do Kanban) → abrir item → voltar → visão, filtro e rolagem mantidos. Em 1440×900 e 390×844 (`docs/integracao/README.md:9`), incluindo F5 com `?view=` e entrada sem `?view` usando a preferência.
   - Ajustar os testes que clicam pelo texto (seção 7).

## 12. Conflitos com frentes não integradas

| Frente | Arquivos que o ViewSwitcher também tocaria | Risco |
|---|---|---|
| DS (`claude/v44-ds`) | `engine.py` (+190), `g2lib.js` (+233), `processo_os.py` (selos com dica, `_chip_hole`) | alto: integrar a DS antes |
| TABR (`claude/v44-tabelas-r`) | `cad_fazendas.py`, `cadastros.py`, `irrigacao.py`, `cad_*` (não toca `engine`/`g2lib`) | médio no Talhão: princípio "uma variável por coluna" × Matriz |
| CADUX (`claude/v44-cadux`) | `cad_fazendas.py` (651), `cadastros.py` (651), `cad_*`, `irrigacao.py` | alto no Talhão (seletor Lista/Mapa do CD-01) |
| NAV1 (`claude/v44-nav`) | `processo_planos.py` (PA) | baixo; padrão de volta (rolagem + foco) a copiar |
| PCM (`claude/v44-pcm`) | `maquinas.py` (MA com `#vis=` e `&modo=kanban`) | médio: nome e alias da visão |
