# Guia do padrão de processos contínuos (decisão do proprietário · 25/09/2026)

Leia também `GUIA-AREAS.md` (API antiga, ainda válida). Este guia PREVALECE sobre ele onde divergir.

## As regras do proprietário (resumo obrigatório)
1. **Menu**: Mapa · Cadastros ▸ · Agrícola ▸ (Planos agronômicos, Planejar safra, Ordem de Serviço) · Suprimentos ▸ (Compras, Estoque). Os demais módulos ficam OCULTOS do menu, preservados (o shell já faz isso; telas ocultas mostram o rótulo "Módulo oculto no menu").
2. **Faixa "Etapas do processo"** no topo, fixa na rolagem (o shell/steps já fazem sticky). Cada etapa: nome curto no **imperativo afirmativo**, clicável, etapa atual destacada, **motivo do impedimento** visível quando houver, contexto e dados preservados. Voltar/avançar sem redigitar. Navegar NUNCA executa aprovação ou ação de negócio.
3. Sem páginas intermediárias que só repetem submenus. Quando o processo depende de um registro, a 1ª etapa é selecionar/criar esse registro (safra, plano, pedido…). **Nunca escolha um registro silenciosamente.**
4. **Edição pela linha** em toda tabela com registros editáveis: clicar na linha abre o formulário lateral à direita preenchido; sem botões "Editar"; destaque ao passar o mouse; teclado (Enter); seta de drill só expande; checkbox só seleciona; excluir só inicia exclusão (com confirmação); links abrem o destino sem editar; Salvar/Cancelar; salvar atualiza linha e cálculos mantendo filtros/ordem/expansões; cancelar preserva; aviso de alterações não salvas; erros junto ao campo preservando o preenchido; sem permissão → consulta; totais/indicadores calculados → abrem detalhamento/origem (nunca edição do resultado). **O motor G2 já implementa tudo isso**: basta usar `grid(...)` ou `table(..., edit=...)` corretamente.
5. **Visual**: só o essencial da etapa; **descrição curta no imperativo afirmativo abaixo de cada título de bloco e tabela** (ex.: "Confira os recebimentos e registre divergências."); formulários laterais pela direita; ícones claros com rótulo acessível e `title` nas ações secundárias; seta de drill à esquerda da 1ª coluna (G2 faz); **coluna de gatilho primeiro** quando existir; colunas ajustam ao conteúdo (G2 faz); números e ações compactos; quebra de texto e rolagem horizontal quando necessário; não reduzir fonte para caber; listas suspensas/cadastros existentes; campos condicionais só quando necessários (`cond`); parâmetros técnicos fora da tela; não repetir informação entre título, descrição, cards e tabela.
6. Não crie botões sem ação, telas sem continuidade ou dados desconectados entre etapas. Integrações/mensagens reais: SIMULE (e diga "simulado · nenhuma mensagem real enviada").

## Motor G2 (engine.py + g2lib.js) — API
```python
from engine import grid, table, Pt, esc, icon, BTN_ST, _MINI, _MINIP, EXTRA, EXTRAJS, INK, MUTED, LINE, BG, SURF, ACC, ACCS, YEL, YELS, RED, REDS, GRAYS, DISP
from ui37 import shell37, steps_state, steps_bar, HEIGHTS37, PARENT37, continuity, selo, etapa, farm_map, map_legend, tabs
```
- `grid(cols, rows, edit=..., sel=False, dele=False, tree=False, search=True, total=True, so=None, add=None, bulk='', gid=None, x0=None, frame=True, tools='')`
  - `cols=[dict(k, l, t='txt'|'num'|'date', a='r', u='ha', d=2, pre='R$ ', agg='sum'|'avg', chips={'Ativo':'green'}, w=300, zdash=True)]`
  - `rows=[dict(id, v={k: valor cru}, s={k: texto p/ busca/ordenação}, p={k:[partes]}, ro=False, kids=[...], o=[dict(t,h=None)], sh=None)]`
    - `v` = dados editáveis/numéricos; `p` = exibição rica (sobrepõe v); `ro=True` = sem permissão → abre em consulta; `kids` = drill (tree=True); `o` = origens mostradas no painel (modo 'origin'); `h` vazio = texto.
  - Partes: `Pt.txt(t)`, `Pt.b(t)`, `Pt.mut(t)`, `Pt.chip(t,'green'|'yellow'|'red'|'gray'|'blue')`, `Pt.tag(t)`, `Pt.link(t,href)`, `Pt.cta(t,href,u=False)`, `Pt.act(t,mensagem)` (botão que executa e mostra aviso, NÃO abre edição), `Pt.br()`; ação de processo com parâmetro: `{'k':'act','t':'Abrir','fn':'nome:arg','lk':True}` chama `v.nome(arg)` definido no seu JS.
  - `edit=dict(m='form'|'ro'|'origin'|'pick'|'none', title, sub, newTitle, leafOnly=True, fields=[dict(k, l, t='txt'|'num'|'sel'|'multi'|'date'|'area'|'email'|'tel', opts=[...], req, min, max, u, cond=dict(k,eq), help, def, ro)], calc=[dict(k, op='mul'|'div'|'sum'|'sub'|'max0sub', a=[...])])`
    - 'form' edita; 'ro' consulta; 'origin' consulta + lista de origens (valores calculados); 'pick' chama `self.g2pick(gid,rid,row)` (detalhamento na própria tela); 'none' linha não abre nada.
  - `add='Novo X'` põe "+ Novo X" na barra da tabela; o botão de novo registro também existe como buraco `{{gid_new}}` (use no botão primário e então passe `add=None` para não duplicar).
- `table(headers, rows, ..., edit=None|False|'ro'|'origin'|dict, sel, dele, add, gid)` — API antiga convertida em G2 (células HTML viram partes). `edit=None` = formulário automático com as colunas de texto simples (colunas ricas em consulta); use `edit='ro'` para registros sem edição (histórico, logs), `edit='origin'` para indicadores calculados, `edit=False` só se a linha realmente não é um registro. Para formulário com tipos corretos (listas, números, datas), passe `edit=dict(m='form', fields=[...])` com `k` = 'c0','c1',… (índice da coluna). Botões/links "Editar…" nas linhas são removidos automaticamente (a linha edita).
- **Processo numa só tela** (dados compartilhados entre etapas): `steps_state(nomes)` no `shell37(..., steps=...)` + no JS `g2steps(self, v, 'stp', n, etapaAtual, motivos, irPara)`; etapas em `<sc-if value="{{s1}}">…`. JS específico: `EXTRAJS[0] = 'const D2=...;' + código` com `function PREVALS(self,v){...}` (antes das grades: calcule linhas derivadas em `GRIDS.find(g=>g.id==='x').rows = [...]`) e `function EXTRAVALS(self,v){...}` (buracos, painéis, ação primária). Ganchos: `self.g2after=(gid,rows,r)=>{}` (após salvar/excluir), `self.g2pick=(gid,rid,r)=>{}`. Estado: `self.state.x` / `self.setState({...})`. Aviso: `self.setState({g2toast:'…'})`. Leia de fresco `self.state` dentro dos handlers.
- **Faixa por links** (módulos ocultos sequenciais): `steps_bar([dict(t='Confira o balanço', href='IR-01.dc.html'), ...], current=i)` no `shell37(..., steps=...)`.
- Botão primário dinâmico: `shell37(..., primary_html='<button onClick="{{prim_fn}}" style="{{prim_st}}">{{prim_t}}</button>')`.
- Templates DC: buraco `{{a.b}}` só leitura pontilhada; toda condição em `<sc-if value="{{x}}" hint-placeholder-val="{{false}}">`; listas em `<sc-for list="{{xs}}" as="i" hint-placeholder-count="2">`. NUNCA `<sc-for>` dentro de `<table>` (use grid/div). Sem `innerHTML`, sem teclado global.

## Exemplar completo
`areas/processo_safra.py` + `safra.js` + `dados2.py` (Planejar safra, 6 etapas). Copie o padrão: `bloco(titulo, descricao_imperativa, corpo, acao)`, `navpe()` (‹ anterior · próxima ›), painéis laterais com Salvar/Cancelar e aviso de não salvo, envio sem duplicar.

## Dados
- `dados2.py` = fonte única dos processos (safras, cultivos, planos com gatilhos por atividade, conjuntos/rendimentos, recursos, estoque, recebimentos, FORNECEDORES com grupos/e-mail/WhatsApp/homologado, SOL_INICIAL + `sol_itens()`, PROPOSTAS, ALCADA, PEDIDOS, RECEBIMENTOS, REQUISICOES, LOTES, CONTAGENS, `demanda()`). `dados.py` = ordens (OS, KANBAN, REQ, etc.) do mundo DEMO. Use-os; se faltar algo, crie constante local coerente e declare em `observacoes`.

## Testes obrigatórios antes de terminar
```bash
cd <gen37> && python3 -c "import sys; sys.path.insert(0,'.'); import importlib; importlib.import_module('areas.SEU_MODULO').build(); print('OK')"
cp project/<suas telas>.dc.html _render/ && python3 g2test.py <TELA>.dc.html       # grade: ordena, abre pela linha, valida, avisa, salva, teclado, link/botão não editam
python3 shot.py <TELA>.dc.html && (abra _shots/<TELA>.png com Read)                # visual
```
Para processos com etapas, escreva um teste CDP como `saftest.py` (copie e adapte) cobrindo o fluxo pedido; rode e corrija até passar.
