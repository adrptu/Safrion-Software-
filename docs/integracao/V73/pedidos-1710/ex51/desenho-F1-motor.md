# EX-51 · F1 · Desenho do motor (R2, R3, R4, foco e teclado)

- **Autor:** Claude (subagente), 17/10/2026. **Revisor:** Codex. **Estado:** desenho para revisão. Nenhum código de produto foi alterado.
- **Base:** worktree `intdrill`, commit `e43ae07e` (composição + DS-MODULOS-2 + DRILL-RECOLHIDO).
  - `gen37/` quer dizer `tools/prototipo/v37/gen37/` dessa árvore. Os números de linha são dela e diferem dos das validações AC e BDE, que usaram `b2912bf8`.
- **Executado:**
  - leitura estática das fontes, com `grep` e `sed`;
  - leitura do robô v5 (`anexo-robo-v5.html`, `anexo-robo-v5-resumo.py`) e de `robo-v5-base/comparar.py`.
- **Não executado:** navegador, robô e testes.
  - A linha de base da candidata atual roda em paralelo em `robo-v5-base/`. Este desenho não usa nenhum número dela.

```text
ID / resultado útil / persona: EX-51 F1 · todo ID abre o registro; Voltar (da tela, do navegador) e recarregar devolvem o registro e a seção · todas as personas
Requisitos do PRD e fora do escopo: R2, R3, R4 e acessibilidade do pedido · fora: R1 fio (F4), R5 escopo global (F2), R7 pendências (F3), dados novos de domínio (origem estruturada B-2, pedidos no cenário C-3)
Autor / revisor / integrador: motor e telas: Claude · LO-02det, painéis dos .js do Codex e robô v5.1: Codex · revisão cruzada; integra quem revisa (§3.5)
Base / arquivos: e43ae07e · g2lib.js, engine.py, ui37.py, areas/{processo_os,processo_estoque,processo_compras,producao,maquinas,agronomia,vendas,processo_beneficiamento}.py, cenario.js, producao.js, ben.js · Codex: logistica_saida_ui.js e os seus *_ui.js
Aceite e comando de verificação: §4
Estado / impedimento / próximo passo: desenho · nenhum impedimento · revisão do Codex e acordo do robô v5.1 (§4) antes do passo 1
```

## 1. Inventário: quem abre o quê pelo endereço

- **Fonte do levantamento:** `grep -n "location.hash" areas/*.py *.js`, sem testes.
- **Como ler as colunas:**
  - "Abre" quer dizer que o tratador de endereço da dona abre o registro.
  - "Grava" quer dizer que a dona põe o registro aberto no endereço.

| Prefixo | Dona | Abre pelo endereço hoje | Grava ao abrir / limpa ao fechar | Falta na F1 |
|---|---|---|---|---|
| `OS-` | OS | **Abre:** `#OS-n`, `#OS-n:ajustar`, `:usar=` (`processo_os.py:1176`). Também `#painel=a,b` (`:1165`), `#tal=` (`:1169`, filtro) e `#nova:` (`:1174`). **ID inexistente:** silêncio (`:1177`). | **Não grava:** só reescreve ao consumir `:usar=` (`:1182`). **Não limpa:** fechar (`:1346`). | Gravar e limpar. Recorte `#painel=…&abre=OS-n`. Aviso de inexistente. `g2regAbriu`. Faixa de origem. |
| `OS-` de água | IR-03 | **Abre:** `#OS-n[:sub]` (`irrigacao.py:473-477`). | Limpa o subpainel (`:475`, `:477`). | O resolvedor escolhe IR-03 quando a O.S. não está em `c.ordens` (conferir no passo 5). |
| `OM-` | MA | **Abre:** `#om=`, `#achado=`, `#venc=`, `#leitura=` (`maquinas.py:90`, `:103-116`). | **Grava** a cada desenho, com estado `null` (`ma_hashSync` `:96`, `:277`). | **Foco e anúncio na chegada:** `ma_aplicaHash` não foca; `ma_abrir` foca (`:122`). Passar ao gravador único. |
| `PC-` | CMP | **Não abre:** `abrirHash` só lê `sol=`/`saf=` (`processo_compras.py:616`); `cmHashLer` só lê `tipo=`/`sc=` (`:756`). | — | `#pc=` (passo 5). Até lá, texto. |
| `SOL-` | CMP | **Abre:** `#sol=…[&saf=]`, achando a safra pela SOL (`:616-625`). | **Grava** (`hashSync` `:328`, `:541`). | Gravador único. |
| `SC-` | CMP, materiais | **Abre:** `#tipo=materiais&sc=` (`:756`, `:807-811`). | **Grava e limpa** (`cmAbrir` `:799`, `cmFechar` `:800`). | Gravador único. A MA mostra a SC sem link (D-10). |
| `REQ-` | EST | **Parcial:** `#dev=REQ&para=&ver=&sob=` abre só para o item caixa do BEN (`processo_estoque.py:655-659`). | **Limpa** depois de devolver (`:454`). A volta só vai ao BEN (`:662`). | `#ent=REQ` e `#dev=REQ` pela grade (§2.2). Faixa genérica. |
| `CG-` | CARGA | **Abre:** `#CG-n`, só carga sincronizada (`producao.py:515-516`). | **Não grava** (`g2pick` `:428`). | Gravar em `prPainel`. |
| `OB-` | BEN | **Abre:** `#OB-n` e `#nova=<lote>` (`processo_beneficiamento.py:306-308`). | **Não grava** (`g2pick` `:93`). | Idem. |
| `PV-` (`CRE-`) | VEN | **Abre:** `#PV-n` e `#nova:` (`vendas.py:233-238`). O PROD manda o PV antigo à VEN (`producao.py:386`). | **Não grava** (`g2pick` `vendas.py:131`). | Idem. |
| `RM-` | EXPED; LO-02det | **EXPED:** `#RM-n`, `#nova:PV` (`vendas.py:404-407`). **LO-02det:** `#rm=` (`logistica_saida_ui.js:2`, `:7`). | **EXPED** grava só ao programar (`vendas.py:323`). **LO-02det** grava depois da saída, com estado `null` (`logistica_saida_ui.js:42`). | EXPED: gravar. LO-02det: Codex. |
| `VIS-` | AG-01 (AG-01det) | **Abre:** `#VIS-n[:decidir\|:programar]` (`agronomia.py:588-598`). A AG-01det abre `#VIS-n` (`:817`). | **Grava** (`agOpen` `:611`). **Limpa** ao fechar (`:676`). | Gravador único. Anúncio. |
| `DIA-` `REC-` `RA-` | AG-01 (decisão da VIS) | **Não abre.** AG-03 e AG-03det saem no EX-50. A AG-04det é fixa na REC-014 (`agronomia.py:169`, `:331`). | — | Ficam texto, registradas como "sem dona". Candidata: a AG-01 resolve a VIS pelo `mipGet`. Decisão do Codex junto com a B-2. |
| `INSP-` | PROD (Qualidade do lote) | **Não abre pelo INSP;** abre o lote (`producao.py:385-386`). | — | Resolvedor INSP → `PROD#<lote>`, por `benB(c).insp[id].lotes` (`ben.js:27`, `:609-610`). |
| lote de produto | PROD | **Abre:** `#<lote>` (`producao.py:385-386`). `LC-` não abre (E-5). | **Não grava** (`g2pick` `:297`). | Gravar. |
| lote de insumo | EST, Saldos | **Não abre.** | — | `#lote=` pela grade `g_lot`. |
| talhão | CD-01det | **Abre:** `#talhao=` (`cad_fazendas.py:581`). | **Grava** (`det_set` `:680`). | **Referência explícita:** o nome não é detectável por padrão. O `#tal=` da OS é filtro, não registro. |
| ativo/máquina | MA (página do ativo) | **Abre:** `#ativo=` (`maquinas.py:110`). O CD-03 abre `#ficha=` só para pivô (`cad_ativos_pessoas.py:285`). | **Grava** (`ma_hashDe`). | Referência explícita. |
| produto | AG-07 (produto com registro) | **Abre:** `#reg-<NR>` e `#<ref>` (`agronomia.py:1496-1499`). | **Grava** (`:1481`, `:1483`). | **Produto sem registro:** não há dona que abra por ID (o CD-06 só abre `#aba=`, `cadastros.py:178`). Fica texto. |
| pessoa | CD-04 (cadastro); CF-01 (acesso) | **CF-01** abre `#pessoa=` (`configuracoes.py:106-107`). **CD-04** não abre. | — | CD-04 `#pessoa=` pela grade (§2.2). Até lá, texto. |
| já endereçáveis | — | **AG-02:** `LAU-` (`analise_solo.py:346`). **PA:** `#plano=` (`processo_planos.py:155`, grava em `:127`). **SAF:** `#saf=&passo=&cult=` (`safra.js:1716-1721`, grava com `location.hash`, `:1765`). **COLH:** `#<cultivo>` (`producao.py:664`). | — | Gravador único onde hoje se usa `replaceState(null…)`. |
| no app (`mobile37`) | MB | **OS:** MB-02 `#OS-n` foca a linha (`mobile.py:793`). **OM:** MB-09det (`mobile.py:1164`). **Ativo:** MB-09 `#ativo=` (`mobile.py:1055`). | — | Variante do app no registro de referências (§2.1). |

### Achados do inventário

- **Gravadores apagam o estado do histórico.** Quase todos passam `null` como estado:
  - `agronomia.py:610`;
  - `maquinas.py:96`;
  - `processo_compras.py:328`, `:757`;
  - `processo_planos.py:127`;
  - `logistica_saida_ui.js:42`.

  Isso apaga o `history.state`, inclusive a marca `g2volta` (`g2lib.js:1444`).
- **Comparações por texto exato do destino.** `processo_os.py:868` e `:898` testam `b.h==='EST.dc.html'`. Dar registro ao link "Entregar no Estoque" (`:374`, `:573`, `:697`) quebraria as duas. A comparação deve passar ao tipo do destino.

## 2. Desenho no motor

### 2.1 R2 · referência é link

**Componente: um registro e duas funções no `g2lib.js`.**

```js
// G2_REF: uma entrada por tipo; a ordem resolve conflito (OS agrícola antes da OS de água)
{ t:'os', re:/^OS-\d{4}$/, dona:'OS.dc.html', tela:'Ordens de serviço', end:id=>'#'+id, aceita:true,
  existe:id=>typeof cenGet!=='function'||!!cenGet().ordens[id], resumo:'cenResumo',
  app:{dona:'MB-02.dc.html', end:id=>'#'+id} }
```

- **`g2ref(id, ctx)`** devolve `{href, tela, resumo}`, ou `null` quando a referência fica texto.
- **`g2refPartes(texto, ctx)`** devolve partes `txt` e `ref`. O contexto é `ctx={self, cartao}`.
- **`g2part` (`g2lib.js:155`):**
  - ganha a parte `{k:'ref', id, t}`, que vira `isLink` com o `href` de `g2ref`, `data-ref` e a dica "Abrir REQ-039 no Estoque";
  - quando `g2ref` dá `null`, vira `isTxt`.
- **Link legado com ID e sem registro** (`{k:'link', t:'OS-0424', h:'OS.dc.html'}`): vira `ref` no mesmo ponto. Isso corrige a A-9 sem mexer na tela (`processo_estoque.py:524`, `:549`, `:565`, `:619`).
- **Python:** `Pt.ref(id, t=None)` (`engine.py:2061-2064`) para cadastro citado pelo nome (talhão, ativo, pessoa, produto), que não se detecta no texto.
- **Template único:** `_PARTS` (`engine.py:1706`) ganha `data-ref` e `data-dica`. O estilo atual do link fica igual (DS).

**Onde entra:**

1. **Célula da grade** (`g2lib.js:631`, antes do `g2part`):
   - as partes `txt`, `mut` e `b` passam por `g2refPartes`;
   - a coluna 0 fica de fora, porque é a identidade da linha;
   - clicar no link não abre a linha, porque `g2open` ignora `a` (`g2lib.js:209`).
2. **Formulário e aside do g2:**
   - `F.origins` (`g2lib.js:716`) vira lista de partes;
   - `_g2form` (`engine.py:2053`) a desenha com `_PARTS`;
   - isso resolve de uma vez a memória da demanda da CMP (`processo_compras.py:459`, `cal01Memo(...).map(t=>({t}))`, A-5) e a origem do EST (`processo_estoque.py:635`).
3. **Painéis próprios** usam `g2refs(t, ctx)` em JS e `E.refs_html(expr)` em Python.
   - **Um ponto cobre sete telas:** `prCel` e `painel()` (`producao.py:144`, `:67-80`) atendem PROD, CARGA, COLH, BEN, VEN, EXPED e PCOM. Hoje são texto nelas:
     - a O.S. na CARGA (`producao.py:483`);
     - a venda na EXPED (`vendas.py:345`);
     - o INSP no BEN (`processo_beneficiamento.py:192`);
     - o talhão e a O.S. no PROD (`producao.py:341`).
   - **As demais telas adotam uma a uma:**
     - OS: Origem (`:1393`, `:1701`), insumos, recursos e situação;
     - MA;
     - AG-01;
     - CD-03: "Ver ordens afetadas" passa a ir para `OS#painel=` (`cad_ativos_pessoas.py:298`).

**Pós-processamento no DOM: recusado.** O `support.js` é o React (cabeçalho do arquivo), e os nós de texto são dele. Quebrar um nó de texto num `<a>` traz três problemas:

- o React duplica o texto quando atualiza o `nodeValue`;
- falha em `removeChild` e `insertBefore` com nó movido;
- tira o foco do link a cada redesenho. O aviso some em 4,5 s e redesenha a tela (`engine.py:2217`).

O pós-processamento seguro tem duas partes:

- o de dados: os pontos 1 e 2 acima, cada um num lugar só;
- a varredura só de leitura que gera o aviso.

**Quando não vira link (fica texto):**

- **Sem dona que abra.** O prefixo não tem entrada ou está com `aceita:false`. Os casos de hoje:
  - DIA, REC e RA;
  - PC;
  - lote de insumo;
  - pessoa;
  - produto sem registro;
  - `LC-`.

  Quando a dona aceita, a entrada passa a `aceita:true` no mesmo commit do tratador e do teste T3.
- **O próprio registro do contêiner** (`ctx.self`).
- **Dentro de elementos que não podem ter link:**
  - título (h1, h2);
  - selo e tag;
  - botão e campo;
  - `[data-noref]`;
  - cartão com `role=button` (aninhar elementos interativos é inválido).
- **Registro inexistente.** Com o módulo carregado, `existe(id)` falso deixa texto e gera o aviso `[R2] inexistente`. Exemplo: a OS-0409 semeada (`gestao.py:40`).
- **Dona marcada Excluir no EX-50.** Ela nunca entra no registro (teste T2).
- **No app.** Dona web sem variante para o app fica texto.

**Aviso no console:**

- **Onde roda:** `g2refVarre()`, chamado em `g2montou` e `g2mudou` (`g2lib.js:1130`, `:1142`), 400 ms depois do desenho, só lendo a tela.
- **Quando avisa:** por contêiner (`[role=dialog]` ou `main`), quando um ID com `aceita:true` não tem nenhuma ocorrência clicável. Gera `console.warn('[R2] ID como texto', id, tela)`, uma vez por ID e contêiner, e registra em `window.__g2refTexto` para os testes.
- **Mesma unidade do robô:** o ID conta como clicável se ao menos uma ocorrência for link (`refsC`, `anexo-robo-v5-resumo.py:21`).
- **Não reprova a varredura:** `paginas_scan_test.py:20` e `cadc_lib.py:11` só capturam `console.error`.

### 2.2 R4 · endereço do registro e volta

**Gravador único (novo, `g2lib.js`):**

- **`g2hashReg(h)`:**
  - chama `history.replaceState({...history.state, g2reg:{h}}, '', pathname + search + h)`;
  - mantém a query (`?view`, `?ag`; regra de `visoes.py:104-121`) e o estado (`g2volta`);
  - não dispara `hashchange`.
- **`g2hashSync(self, h)`:**
  - a dona chama a cada desenho;
  - só grava se o endereço mudou e se não houver navegação pendente, isto é, se o hash atual não for diferente do último gravado e do último lido;
  - é a lição da MA v57 (`maquinas.py:225-229`).
- **Gravadores que passam a usar `g2hashReg`:**
  - `maquinas.py:96`;
  - `agronomia.py:610` e `:1470`;
  - `processo_compras.py:328` e `:757-759`;
  - `processo_planos.py:127`;
  - `cad_fazendas.py:680`;
  - `vendas.py:323`;
  - `processo_estoque.py:454`;
  - `processo_os.py:1182` e `:1237`;
  - `irrigacao.py:200`, `:337`, `:359`, `:475` e `:477`;
  - `logistica_saida_ui.js:42` (Codex).

**Formato de cada dona.** O leitor atual só muda onde a tabela indica.

| Dona | Ao abrir | Ao fechar |
|---|---|---|
| OS | `#OS-n`. No recorte do Painel: `#painel=a,b&abre=OS-n` (o leitor `:1165` passa a aceitar `&abre=`). | `''`. No recorte: `#painel=a,b`. |
| MA, AG-01, AG-07, CMP, PA, CD-01det, SAF | O formato de hoje (§1). | O de hoje. |
| PROD, CARGA, COLH, BEN, VEN, EXPED | `#<id>`, gravado por `prPainel` (`producao.py:171`) quando `pr_pan` é registro (não `nova`) e a tela tem leitor. A PCOM não tem leitor e não grava. | `pp_close` (`:180`) limpa. |
| EST e grades com formulário | `sp.hash`: `g_ent` → `#ent=REQ-039`, `g_dev` → `#dev=`, `g_lot` → `#lote=`, `g_rec` → `#nf=`. | `g2close` (`g2lib.js:256`) limpa. |

**Grade com endereço (motor):** `sp.hash={k, chave:r=>id de negócio}`.

- **Leitura:**
  - o motor lê o endereço no 1º desenho e no `hashchange`;
  - acha as linhas da chave (por exemplo, `REQ-039` → linhas `REQ-039|<item>`);
  - **uma linha:** abre o formulário;
  - **várias:** filtra pela busca e anuncia "N linhas da REQ-039".
- **Gravação:** em `g2open` e `g2close` (`g2lib.js:208-221`, `:256`).
- **Alcance:** dá endereço ao EST, ao CD-04 (`#pessoa=`) e aos cadastros, sem código por tela.
- **Caso especial:** o `estDevHash` (`processo_estoque.py:655`) continua para a caixa do BEN, que leva `para`, `ver` e `sob`.

**Seção, rolagem e gatilho:**

- **Saída.** O ouvinte de clique em link para outra tela já existe (`g2lib.js:1177-1181`). Ele grava `{h, sec, rol, gat, t, perfil}` em `history.state.g2reg` e em `sessionStorage['g2reg:'+arq+h]`:
  - **`sec`:** o `[data-sec]` mais próximo do gatilho. As seções passam a levar `data-sec`; na OS, isso entra no `sec()` (`processo_os.py:1543`).
  - **`rol`:** a rolagem do painel.
  - **`gat`:** o `data-ref` do gatilho.
- **Chegada.** Depois de abrir pelo endereço, a dona chama `g2regAbriu(self, id, {secAbre})`.
  - **Quando restaura:** só se a navegação for `back_forward` ou `reload` e `history.state.g2reg.h === location.hash`, ou se houver o bilhete de uso único que o Voltar da faixa deixa.
  - **O que faz:**
    - abre a seção pelo gancho da dona (na OS, `psx`);
    - rola até onde estava;
    - foca o gatilho ou, sem ele, o título do painel;
    - anuncia pelo `g2vivo` (`g2lib.js:1082`).
  - **Substitui o foco feito tela a tela** (D-14 e E-18). O `g2montou` já deixa o foco para o painel quando há hash (`g2lib.js:1136`).

**Origem ("Aberto a partir de"):**

- **Onde vai o parâmetro:** o link de referência leva `?de=<arq>%23<hash>` na query, não no hash. Os leitores são estritos e quebrariam com um parâmetro a mais no hash:
  - `processo_os.py:1176` e `agronomia.py:588` usam regex terminada em `$`;
  - `vendas.py:234` e `producao.py:386` buscam por chave exata.
- **Validação:**
  - o `de` precisa casar com `^[A-Za-z0-9-]+\.dc\.html(#[A-Za-z0-9=&:,._|%-]{0,120})?$`;
  - o arquivo precisa existir e não estar marcado Excluir;
  - `de` inválido é ignorado, com aviso `[R4]`.
- **Rótulo:** vem do ID achado no hash (`G2_REF`) ou do título da tela (`NAV`). Nunca usa texto livre da URL.
- **Faixa:** "Aberto a partir de OS-0424 · ‹ Voltar para OS-0424", com `<a href="OS.dc.html#OS-0424">`, desenhada por `E.origem_html()`:
  - **no topo do detalhe aberto:**
    - formulário g2;
    - `painel()` da família produção (PROD, CARGA, COLH, BEN, VEN, EXPED, PCOM);
    - painéis da OS, da MA, da AG-01 e da CMP.

    Fica dentro do painel porque o fundo do painel é um botão que fecha (`processo_os.py:1666`).
  - **no cabeçalho do `shell37`:** páginas de detalhe, ou chegada que só filtra a lista.
- **Duração:** vale enquanto o registro da chegada estiver aberto. Fechar ou abrir outro registro tira o `de` da URL e a faixa.
- **Sem `de`** (link digitado, favorito, tela antiga):
  - não há faixa;
  - continuam o Voltar do navegador e o "‹ Módulo" (`ui37.py:438-439`);
  - a origem não é adivinhada por `document.referrer`.
- **Voltar da faixa:**
  - navega; não usa `history.back()`, como o G2_VOLTA (`g2lib.js:1340-1342`);
  - deixa o bilhete de uso único para a origem restaurar a seção.
- **Robô:** a faixa atende a regra de volta do robô: texto com "Voltar" e o ID de origem, ou `href` para a tela de origem (`voltaOrigem`, `anexo-robo-v5.html:98`).

**G2_VOLTA e a recusa por "outro escopo" (casar com a F2):**

- **Papéis diferentes:**
  - o G2_VOLTA guarda o contexto da lista (visão, filtros, foco, rolagem) na ida para página de detalhe;
  - o R4 guarda o registro e não passa por `g2voltaValida`.
- **Na F1:**
  - `g2voltaGuarda` (`g2lib.js:1439`) grava também o `location.hash`, e `g2voltaUrl` (`:1353`) o devolve. Assim a lista volta com o painel aberto (D-13);
  - `g2voltaValida` (`:1348-1351`) não muda.
- **Chegada pelo endereço não falha por escopo:**
  - a dona abre o registro e, se ele estiver fora do filtro, troca o filtro com aviso, como já fazem a OS (`processo_os.py:1177-1179`) e a AG-01 (`agronomia.py:591`);
  - onde a dona não faz isso, a F1 garante só abrir o painel; trocar o filtro é F2.
- **Contrato para a F2:** com o escopo único da sessão, `g2voltaValida` deixa de recusar por "outro escopo". Passa a aplicar o contexto no escopo atual, com o aviso "Escopo: Lagoa Grande, escolhido depois". Assim a F1 e a F2 não se contradizem.

**Divergência do pedido para o Codex revisar: a forma `#OS-0502>PC-…` não entra.**

- **Por quê:** os leitores acima são estritos, e o `ma_hashSync` reescreve o hash a cada desenho (`maquinas.py:96`).
- **Em troca:**
  - o empilhado é passageiro e não vai ao endereço;
  - recarregar ou voltar reabre o detalhe, com o foco na referência que abriu o empilhado;
  - isso também mantém válida a conferência do robô, que compara o título do diálogo de cima.

### 2.3 R3 · painel empilhado, só leitura

- **Template único:**
  - `G2_PILHA` em `engine.py`, ao lado do `G2_TOAST`;
  - incluído no `shell37` (`ui37.py:492`) e no `mobile37`;
  - valores por `g2pilhaVals(self, v)` no `ENGINE_JS2` (`engine.py:2200-2212`);
  - estado `self.state.g2pilha=[{id, gat}]`.
- **Abertura:** clique simples em `a[data-ref]` (botão 0, sem Ctrl, ⌘ ou Shift), quando:
  - a função de resumo existe na página;
  - a pilha tem menos de 2 níveis.

  Com Ctrl, ⌘ ou Shift, ou sem essas condições, o link navega.
- **Conteúdo:**
  - título (ID · nome);
  - selo;
  - até 6 pares rótulo-valor;
  - até 3 listas curtas, cujas referências abrem o nível 2;
  - no rodapé, o link secundário "Abrir na tela de <Tela>" (BOT-08), com `href` da dona e `de=`.

  No nível 2, referência navega: não há 3º nível.
- **Topo:**
  - "‹ Voltar para <origem>" desempilha um nível;
  - trilha `<nav aria-label="Trilha">` "OS-0502 › REQ-0xx › LG26-03", com o elo atual em `aria-current="page"`;
  - tocar num elo desempilha até ele.
- **Esc:**
  - ouvinte em `window`, na fase de captura, ativo só com a pilha aberta;
  - chama `preventDefault` e `stopImmediatePropagation`, porque o detalhe de baixo também fecha com Esc:
    - `processo_os.py:1347`;
    - `producao.py:182`;
    - `g2lib.js:728`;
    - `processo_beneficiamento.py:293`;
    - `paEsc` (PA);
  - fecha um nível e devolve o foco ao gatilho.
- **Gerente de modais** (`g2lib.js:950-975`):
  - **hoje:** `modal()` pega o primeiro `aside[role=dialog]` (`.find`), e `aberto` guarda um só diálogo;
  - **mudança:** passa a pegar o diálogo de cima e a guardar uma pilha, para a armadilha de Tab e a devolução do foco valerem por nível.
- **Celular (≤ 640 px):** tela cheia, respeitando a `safe-area`, com o mesmo Voltar e a mesma trilha.
- **Fechamento junto:** a pilha fecha quando o detalhe de baixo fecha ou a tela navega.

**Resumo por entidade.** Nenhuma regra nova: só campos gravados e seletores que a dona já usa. Não há conta no empilhado (AGENTS §4; NÃO FAZER do pedido). Campo que exige regra só da tela dona fica fora, e o "Abrir na tela de X" leva até ela.

| Entidade | Função | Arquivo | Na página quando | Dona |
|---|---|---|---|---|
| OS | `cenResumo(c,id)`: fase, atividade, talhões e ha, janela, responsável, insumos com pedido, reservado e entregue das REQ | cenario.js | `cenario.js_prefixo()` está na página (`cenario.py:120-129`): OS, EST, CMP, SAF, família produção, painéis, AG-01, IN-04, MB | OS. Os selos de impedimento são da tela (`processo_os.py`) e não entram. |
| REQ, lote de insumo | `cenResumo` | cenario.js | Idem | EST |
| CG, lote de produto, PV, RM | `prResumo(P,id)` | producao.js | Idem (`dados_producao.js_regras`) | CARGA, PROD, VEN, EXPED |
| OB, INSP | `benResumo(c,id)` | ben.js | Idem | BEN; Qualidade no PROD |
| OM, ativo | `manResumo` | dados_manutencao | MA, CMP e painéis (`DM.js_regras`) | MA |
| VIS | `mipResumo` | mip.js | AG-01, AG-01det, IN-04, PAGR | AG-01 |
| pessoa | `g2pessoaResumo` (nome e papéis) | g2lib.js + CONF0 | Todas (`_conf_prefixo`, `engine.py:2233`) | CD-04 / CF-01 |
| SOL, PC, talhão, produto | Sem resumo na F1. SOL e PC moram fora do cenário até a C-3. | — | — | Navegam |

### 2.4 Acessibilidade

- **Foco:**
  - **abrir o empilhado:** vai ao título (`tabindex=-1`);
  - **fechar o empilhado:** volta ao gatilho;
  - **chegar pelo endereço ou pelo Voltar do navegador:** vai ao gatilho salvo ou ao título do painel.
- **`aria-live="polite"`,** pela região única `g2-vivo`:
  - **o que anuncia:**
    - chegada: "OS-0424 aberta · a partir de Estoque";
    - reabertura: "OS-0424 reaberta · Insumos";
    - endereço recusado: "OS-0409 não encontrada";
  - **o que não anuncia:** abrir o empilhado, porque o foco já informa;
  - **nunca rouba o foco.**
- **Link:**
  - o texto visível é o ID ou o nome;
  - o nome acessível é igual ao texto visível: nenhum `aria-label` o troca (WCAG 2.5.3);
  - o destino aparece na dica (`data-dica`, componente g2dica);
  - com empilhado, o link leva `aria-haspopup="dialog"`.
- **Alvo de toque:**
  - **referência isolada** (valor de par, célula só com o ID, Voltar, trilha, rodapé): 44 px no toque, com `--g2-alvo` (`engine.py:176-179`, `:1313-1316`), como o `p.alvo` (`g2lib.js:162`);
  - **referência no meio de frase:** ao menos 24 px de altura no toque (exceção de texto em linha do WCAG 2.5.8).
- **Teclado:**
  - as referências são `<a href>`;
  - Tab fica preso por nível, e Esc fecha por nível;
  - a trilha funciona com Tab e Enter.

## 3. Pontos de mudança

| Arquivo | Função (linha) | Mudança | Risco para testes |
|---|---|---|---|
| g2lib.js | Novo bloco | `G2_REF`, `g2ref`, `g2refPartes`, `g2refVarre`, `g2hashReg`, `g2hashSync`, `g2regAbriu`, `g2pilhaVals` | Baixo |
| g2lib.js | `g2part` (`:155`), células (`:631`), `F.origins` (`:716`) | Parte `ref`; link legado com ID vira `ref`; partes nas origens | Médio: toda grade |
| g2lib.js | `g2open` e `g2close` (`:208-221`, `:256`) | Grava e limpa quando a grade declara `sp.hash` | Médio |
| g2lib.js | Clique global (`:1168-1182`) | Captura de saída; abertura do empilhado | Médio: todo clique |
| g2lib.js | Gerente de modais (`:950-975`) | Diálogo de cima; pilha de devolução do foco | **Alto:** foco de todos os painéis |
| g2lib.js | `g2voltaGuarda` (`:1439`), `g2voltaUrl` (`:1353`) | Hash na ficha | Médio: testes de visões |
| engine.py | `_PARTS` (`:1706`), `_g2form` (`:2053`), `Pt` (`:2061`) | `data-ref` e `data-dica`; origens em partes; faixa; `Pt.ref` | Médio |
| engine.py | `G2_CSS`, `ENGINE_JS2` (`:2200-2212`) | `G2_PILHA`, CSS de referência e de pilha; `g2pilhaVals` | Baixo |
| ui37.py | `shell37` (`:492`), `mobile37` | Inclui `G2_PILHA`; faixa nas páginas de detalhe | Baixo/médio: alturas e visual |
| areas/producao.py | `prCel` (`:144`), `painel()` (`:67-80`), `prPainel` (`:171-182`) | Partes; grava e limpa; faixa | Médio |
| areas/processo_os.py | `abrirHash` (`:1164-1184`), fechar (`:1346`), Origem (`:1393`, `:1701`), `sec()` (`:1543`), `:868`/`:898`, links do EST (`:374`, `:573`, `:697`) | Grava e limpa; `&abre=`; aviso de inexistente; `data-sec`; comparar pelo tipo do destino; `EST#ent=` | **Alto:** muitos testes da OS |
| areas/processo_estoque.py | Grades (`:98-122`), `estDevHash` (`:655`), `dev_volta` (`:662`) | `sp.hash`; faixa genérica no lugar da volta só ao BEN | Médio |
| areas/processo_compras.py | `hashSync` (`:328`), `cmHash` (`:757`), `abrirHash` (`:616`) | Gravador único; `#pc=` | Médio |
| areas/maquinas.py | `ma_hashSync` (`:96`), `ma_aplicaHash` (`:103`), painel da OM | `g2hashSync`; `g2regAbriu`; referências (SC, ordens afetadas) | Médio |
| areas/agronomia.py | `agSetHash` (`:610`, `:1470`), `agHash` (`:588`) | Gravador único; `g2regAbriu` | Baixo/médio |
| Demais telas | `processo_planos.py:127`, `cad_fazendas.py:680`, `vendas.py:323`, irrigacao.py | Gravador único | Baixo |
| cenario.js, producao.js, ben.js | Novas funções | `cenResumo`, `prResumo`, `benResumo`, `existe` | Baixo |
| logistica_saida_ui.js (Codex) | `:42` | Gravador único e faixa | Baixo |

**Testes que provavelmente mudam de oráculo.** A lista é estimada pela leitura. Para confirmar, rodar a bateria na base antes do passo 1 (base verde, §3.6).

- **Hash depois de abrir e fechar a O.S.:**
  - `os_recurso_test.py` (`:69`, `painel=`);
  - `acao_unica_test.py` (`:358`);
  - `cartoes_test.py` (`:87`, `:242`);
  - `ctl5_test.py` (`:159`);
  - `ostest.py`;
  - `os_v39_*_test.py`.
- **Partes de célula e links:**
  - `tabelas_*_test.py`;
  - `est_a4_nav_test.py`;
  - `esttest.py`;
  - `drill_recolhido_test.py`;
  - `visual_corte_test.py`.
- **Painel da família produção:**
  - `producao_fluxo_test.py`;
  - `ben_fluxo_test.py` (`:837`);
  - `comercial_fluxo_test.py`.
- **MA e AG:**
  - `ma_unica_test.py`;
  - `ma_menu_test.py`;
  - `matest.py`;
  - `mip_fluxo_test.py`.
- **G2_VOLTA:**
  - `visoes_test.py`;
  - `visoes_unit_test.py` (saída de `g2voltaUrl`).
- **Foco e modais:**
  - `botoes_retorno_test.py`;
  - `retorno_acao_test.py`;
  - `popover_390_test.py`;
  - `ds_padrao_test.py`.
- **Não devem mudar:** `painel_agricola_test.py` (`:358`, `:415`, `:489`), que confere o hash. O `de` vai na query.

## 4. Aceite medido, combinado antes do código

**Robô.** Valores v108 de `robo-v5-base/comparar.py:7`. A medida nova da base substitui esses números quando sair. O pedido cita 29 % e 11 % de base no aceite e 50 % e 18 % no texto.

| Medida | Definição (`anexo-robo-v5-resumo.py`) | v108 | Meta da F1 |
|---|---|---|---|
| IDs clicáveis no detalhe | `refsClic/refsTotal` | 17/55 | ≥ 95 % |
| Chegada no registro | `chegou/navRegistro`, com a 2ª passada (`leva-check`) | 44/88 | ≥ 95 % |
| Volta à origem | `voltaOrigem/navRegistro` | 16/88 | ≥ 95 % |
| Voltar do navegador reabre o detalhe | `reabre/voltarDet` | 0/59 | ≥ 95 % |
| Cadastro clicável (informativo) | `rotClic/rotTotal` | 6/71 | Medir. A meta de 90 % fica para o passo de cadastros. |
| Portões | Nenhuma passagem para tela Excluir; cliques sem efeito (`nada`) não aumentam | — | 0; ≤ base |

**Robô v5.1.** O Codex implementa e o Claude revisa. Contraprova: rodado na base, o v5.1 dá os mesmos numeradores do v5, salvo o item a.

- **a) Denominador de IDs sem prefixos que não são registro:** `CMD-`, `EX-` e `DEC-`, que são regras e itens do projeto. Hoje entram no `ENT_SRC` (`anexo-robo-v5.html:23`).
- **b) Passagem que abre o empilhado** (`[data-g2pilha]`):
  - conta como "empilhado", e chegou se o título contém o ID;
  - em seguida o robô clica em "Abrir na tela de X" e mede esse clique como passagem de navegação (chegada, volta e reabre).
- **c) Execução isolada:** perfil e dados isolados por execução; 2ª passada sempre.
- **d) Relatório por prefixo** dos IDs que ficaram texto.
- **Dependência:** se os prefixos sem dona (DIA, REC, RA, PC, `LC-`, `OC-`…) passarem de 5 % do denominador na base, a meta de IDs passa a depender dos tratadores. A lista sai da linha de base.

**Testes novos com contraprova.**

| ID | O que verifica | Telas | Contraprova (deve reprovar) |
|---|---|---|---|
| T1 (unidade, node) | Partição do texto: ID próprio, `aceita`, `existe`, prefixo desconhecido e link legado | g2lib | `aceita:true` em `RA-`; remover `ctx.self` |
| T2 (estático) | Toda dona do `G2_REF` existe em `_render` e não está marcada Excluir (`ocultas.json`) | Todas | Entrada apontando para AG-04det |
| T3 (navegador) | **Volta completa:** clicar na linha grava o formato da dona; recarregar reabre o mesmo título; fechar limpa hash e `de`; voltar do destino reabre na seção, com foco no gatilho | OS, MA, AG-01, CMP (SC), EST (ent), PROD, CARGA, BEN, VEN, EXPED | `g2hashSync` sem efeito (chave de teste); OS sem limpar ao fechar |
| T4 (navegador) | **Jornada A-8/A-9:** OS-0424 → REQ-039 → `EST#ent=REQ-039`, com a linha aberta e a faixa "Aberto a partir de OS-0424" → Voltar → OS-0424 em Insumos, com foco em REQ-039. Também EST → `OS#OS-n`. | OS, EST | Sem tratar `de` (faixa ausente); `:868` comparando texto |
| T5 (navegador) | **Empilhado:** foco no título; Tab preso; Esc fecha só o empilhado e devolve o foco; nível 2; 3º clique navega; tela cheia em 390 × 844; sem erro de JS | OS, EST, PROD | `modal()` com `.find`; Esc sem captura (fecha a OS) |
| T6 (navegador) | Nenhum `[R2]` em `window.__g2refTexto` | Telas adotadas | Fixture com ID em texto dá 1 aviso |
| T7 (navegador) | Nome acessível contém o texto visível; `aria-modal` e `aria-labelledby`; foco visível; alvo ≥ 24 px em linha e ≥ 44 px isolado no toque (como em `regras_toque_test.py` R3); 1 anúncio por chegada (`g2-vivo`, `dataset.ultimo`) | OS, EST, MA | `aria-label="Abrir"` sobre "REQ-039" |

- **Teclado e leitor de tela:**
  - T5 e T7 são automáticos;
  - o leitor real (NVDA, VoiceOver) não roda no contêiner. Fica a árvore de acessibilidade do Chrome, se o arnês a expuser, ou os atributos;
  - a leitura real vai para o QA do Codex, se houver ambiente. Sem isso, entra como limitação declarada.
- **Baterias existentes a cada passo:**
  - `varredura.py`;
  - `paginas_scan_test.py`;
  - `links_ocultos_test.py`;
  - `ds_padrao_test.py`;
  - `regras_toque_test.py`;
  - `popover_390_test.py`;
  - os testes das telas tocadas.

  A bateria completa roda uma vez no fim da F1.

## 5. Ordem de implementação

Cada passo vira um commit verde na branch do protótipo. O Codex revisa pela branch (§3.5).

| Passo | Entrega | Autor | Verde quando |
|---|---|---|---|
| 0 | Robô v5.1 e linha de base na mesma candidata | Codex | v5.1 = v5 na base, salvo o item a |
| 1 | `G2_REF`, `g2ref`, `g2refPartes`, parte `ref`, `_PARTS`, `Pt.ref`. Sem adoção nas telas. | Claude | T1, T2, varredura |
| 2 | **Adoção central:** células (`:631`), `F.origins` (`:716`), link legado, aviso `[R2]` | Claude | T6 em EST e CMP; `tabelas_*` |
| 3 | **R4, núcleo:** gravador único, `g2regAbriu`, captura de saída, faixa `de`, grade com endereço. **OS:** gravar e fechar, `&abre=`, inexistente, `:868` e `:898`. **EST:** `ent`, `dev`, `lote`, `nf`. | Claude | T3 em OS e EST; T4 |
| 4 | **Família produção:** `prCel`, `painel()`, `prPainel` grava e limpa, faixa | Claude | T3 em PROD, CARGA, BEN, VEN, EXPED; testes `*_fluxo` |
| 5 | **Migração de gravadores** (MA, AG-01, AG-07, CMP, PA, CD-01det, IR), D-14 e E-18. **Referências:** na MA (SC, ordens afetadas) e na OS (Origem, insumos). **CMP:** `#pc=`. **CD-04:** `#pessoa=`. | Claude | T3 nas donas; testes `ma_*` e `mip_*` |
| 6 | **R3:** `G2_PILHA`, pilha, gerente de modais, Esc, resumos (cenario, producao, ben; man e mip onde carregados), celular | Claude. Cada resumo é escrito pelo autor do módulo. | T5, T7 |
| 7 | **LO-02det:** gravador único e faixa. **Referências nos painéis dos .js do Codex:** `campo_conferencia_ui.js`, `conferencia_diaria_ui.js`, `sup_movimentos_ui.js`, `plano_referencia_ui.js`. | Codex | `logistica_saida_test.cjs`; T6 nessas telas |
| 8 | Robô v5.1 depois da F1, revisão adversarial e artefato | Codex mede; Claude publica | As quatro metas ≥ 95 % |

### Divisão e pendências

- **Divergência com a validação AC.** A AC atribuía ao Codex os endereços do EST e da CMP (A-8, C-7). Aqui eles ficam com o Claude, por dois motivos:
  - estão em `areas/*.py`, que são telas;
  - o motor já dá a grade com endereço.

  O Codex revisa e continua dono dos seletores de domínio.
- **Arquivos .js do Codex.** Dos seus arquivos .js, só o `logistica_saida_ui.js` lê ou grava endereço. Nos demais, a parte dele é adotar as referências.
- **Suposições a conferir no passo 5:**
  - o CD-01det abre talhões fora de Santa Rita;
  - qual dona recebe a O.S. de água (OS ou IR-03).
- **Sem dona na F1:** DIA, REC e RA. O gatilho de retomada é a decisão da B-2 (origem estruturada) com o Codex.
