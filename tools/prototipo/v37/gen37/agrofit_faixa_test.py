# -*- coding: utf-8 -*-
"""AG-07 · Consulta Agrofit: pedidos do proprietário de 15/10/2026, no navegador (base real AGROFIT/MAPA, dados abertos):
  A · "Filtro de cultura fora de esquadro e padrão": Cultura, Praga-alvo, Classe e Orgânicos na faixa "Filtros" de todas as telas
      (role=group "Filtros", funil, listas compactas com o rótulo AO LADO, o mesmo seletor da O.S.), alinhados (mesmo topo e mesma altura em
      1440 px) e quebrando sem sair da tela em 390 px; sem os rótulos soltos em cima nem a fileira de chips de classe; Classe e Orgânicos
      filtram e cada opção diz quantas linhas ficam.
  B · "Tox. amb. coluna menos importante": fora do padrão de colunas (VISOES-2 §3.6) e no painel "Colunas" para quem quiser; a escolha vale
      por modo (por produto × por uso) e "Restaurar padrão" volta sem ela.
  C · "concentração na frente do nome": cada ingrediente com a concentração antes do nome, com a unidade da fonte ("806 g/L 2,4-D-dimetilamina",
      "406 g/L 2,4-D + 103,6 g/L picloram"); a busca acha pela concentração ("806"); ordenar e filtrar pela coluna seguem pelo nome (a
      concentração é a 2ª chave da ordenação); sem valor na fonte, só o nome e a dica diz que falta (nada inventado).
Oráculos: agrofit_indice.json servido (nenhum número escrito à mão). Usa comp_lib.Chrome (perfil novo: colunas no padrão).
Contraprova (executada em 15/10/2026): com RENDER_DIR no _render da base a0db53a o teste reprova, 2/17 (A1–A4, A6, B1–B4 e C1–C6 em
vermelho; só A5 e A7 passam, porque não dependem da mudança); com a montagem desta mudança, 17/17.
Uso: python3 agrofit_faixa_test.py   (RENDER_DIR=<pasta> testa outra montagem; sai 1 se algum caso falhar)"""
import os, sys, re, json, time, unicodedata
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, servir

R = os.environ.get('RENDER_DIR') or os.path.join(HERE, '_render')
PROBE = os.path.join(HERE, '_probe'); os.makedirs(PROBE, exist_ok=True)
OK, FAIL = [], []
def chk(nome, cond, info=''):
    (OK if cond else FAIL).append(nome); print(('OK    ' if cond else 'FALHA ') + nome + ('' if cond else ' · ' + str(info)[:900]), flush=True)

IDX = json.load(open(os.path.join(R, 'agrofit_indice.json'), encoding='utf-8'))
F = {c: i for i, c in enumerate(IDX['campos'])}; IG = IDX['ingredientes']; CL = IDX['classes']; NP = len(IDX['produtos'])
def nz(t): return ''.join(ch for ch in unicodedata.normalize('NFD', str(t)) if not unicodedata.combining(ch)).lower()
def nf(n): return f'{int(n):,}'.replace(',', '.')
def nfc(v):   # número como a página escreve (pt-BR, sem arredondar o valor da fonte)
    s = repr(v) if isinstance(v, float) else str(v); i, _, d = s.partition('.')
    i = f'{int(i):,}'.replace(',', '.'); return i + (',' + d if d and d != '0' else '')
def conc_txt(ing): return ' + '.join((f'{nfc(x[1])} {x[2]} ' if x[1] is not None else '') + IG[x[0]][0] for x in ing)
PR = []
for r in IDX['produtos']:
    cls = r[F['classes']] or []
    PR.append(dict(reg=str(r[F['registro']]), marcas=r[F['marcas']] or [], ing=r[F['ingredientes']] or [], org=r[F['organico']],
                   comp=list(dict.fromkeys(CL[c][1] for c in cls))))
# produto de 2,4-D 806 g/L cuja marca e registro NÃO têm "806" (só a concentração pode achá-lo pela busca)
X = next(p for p in PR if len(p['ing']) == 1 and IG[p['ing'][0][0]][0].startswith('2,4-D') and p['ing'][0][1] == 806 and p['ing'][0][2] == 'g/L'
         and '806' not in p['reg'] and not any('806' in m for m in p['marcas']) and p['marcas'])
# mistura com concentração decimal (vírgula na tela)
XM = next(p for p in PR if len(p['ing']) == 2 and any(isinstance(x[1], float) for x in p['ing']) and IG[p['ing'][0][0]][0] == '2,4-D' and p['marcas'])
N806 = sum(1 for p in PR if any(x[1] == 806 for x in p['ing']))
DIM = next(i for i, g in enumerate(IG) if g[0] == '2,4-D-dimetilamina'); NDIM = sum(1 for p in PR if [x[0] for x in p['ing']] == [DIM])
# classe principal com mais produtos aprovados para orgânicos (o filtro combinado não fica num caso vazio)
CLS = max(['Herbicida', 'Inseticida', 'Fungicida', 'Acaricida', 'Nematicida'], key=lambda k: sum(1 for p in PR if k in p['comp'] and p['org'] == 'S'))
NHB = sum(1 for p in PR if CLS in p['comp']); NHBO = sum(1 for p in PR if CLS in p['comp'] and p['org'] == 'S')
COLS_P = ['Produto · registro', 'Ingrediente ativo · grupo químico', 'Classe · modo de ação', 'Culturas', 'Alvos', 'Na fazenda']
COLS_U = ['Produto · registro', 'Praga-alvo', 'Nome científico', 'Cultura do uso', 'Ingrediente ativo · grupo químico', 'Classe · modo de ação', 'Na fazenda']

p_, srv = servir(R); c = Chrome(); J = c.js
U = lambda x: f'http://127.0.0.1:{p_}/{x}'
c.call('Page.addScriptToEvaluateOnNewDocument', {'source': "window.__e=[];addEventListener('error',e=>window.__e.push(String(e.message)))"})
def espera(cond, lim=40.0):   # condição observável com limite explícito (AGENTS §3.6)
    t0 = time.time()
    while time.time() - t0 < lim:
        if J("(()=>{try{return !!(%s)}catch(e){return false}})()" % cond): return True
        time.sleep(.15)
    return False
cnt = lambda: J("(()=>{const s=[...document.querySelectorAll('main span')].find(x=>/ de [\\d.]+ (produtos|usos em .+)$/.test(x.innerText.trim())); return s?s.innerText.trim():'';})()") or ''
def pronto(): return espera("window.__agx&&__agx.AGX.st==='ok'&&__agx.AGX.uSt==='ok'") and espera("[...document.querySelectorAll('main span')].some(x=>/ de [\\d.]+ produtos$/.test(x.innerText.trim()))", 10)
def setsel(al, val):
    r = J(f"""(()=>{{const s=document.querySelector('main select[aria-label={json.dumps(al)}]'); if(!s) return 'sem lista';
      const o=[...s.options].find(o=>o.value==={json.dumps(val)}); if(!o) return 'sem opção'; s.value=o.value; s.dispatchEvent(new Event('change',{{bubbles:true}})); return 'ok';}})()""")
    time.sleep(.6); return r
def opcoes(al): return J(f"(()=>{{const s=document.querySelector('main select[aria-label={json.dumps(al)}]'); return s?[...s.options].map(o=>[o.value,o.text.trim()]):[];}})()") or []
def busca(t):
    J(f"""(()=>{{const i=document.querySelector('main input[type=search]'); const P=HTMLInputElement.prototype; Object.getOwnPropertyDescriptor(P,'value').set.call(i,{json.dumps(t)});
      i.dispatchEvent(new Event('input',{{bubbles:true}})); i.dispatchEvent(new Event('change',{{bubbles:true}}));}})()"""); time.sleep(.7)
cab = lambda: [re.sub(r'[⇅▾▲▼]', '', x).strip() for x in (J("[...document.querySelectorAll('main [role=columnheader] .g2hb')].map(h=>h.textContent.replace(/\\s+/g,' '))") or [])]   # texto do rótulo (o cabeçalho é em caixa alta só no CSS)
linhas = lambda: J("[...document.querySelectorAll('main [role=table] [role=row].g2ed')].map(r=>[...r.querySelectorAll('[role=cell]')].map(x=>x.innerText.trim()))") or []
def coluna(nome):
    h = cab(); i = h.index(nome) if nome in h else -1
    return [r[i] if 0 <= i < len(r) else '' for r in linhas()]
toca = lambda sel: J(f"(()=>{{const e=document.querySelector({json.dumps(sel)}); if(!e) return false; e.click(); return true;}})()")   # sem o alvo, a verificação reprova (não para o teste)
clica = lambda raiz, txt: J(f"(()=>{{const b=[...document.querySelectorAll({json.dumps(raiz + ' button')})].find(x=>x.innerText.replace(/\\s+/g,' ').trim().startsWith({json.dumps(txt)})); if(!b) return 'NÃO ACHEI'; b.click(); return 'ok';}})()")
# faixa: grupo "Filtros", listas (rótulo, retângulo, altura, estilo) e o que existe fora dela
FAIXA = r"""JSON.stringify((()=>{ const f=document.querySelector('main [role=group][aria-label="Filtros"]'); if(!f) return null; const R=f.getBoundingClientRect();
  const ss=[...f.querySelectorAll('select')].filter(s=>s.getClientRects().length).map(s=>{ const r=s.getBoundingClientRect(), l=s.closest('label'), lr=l?l.getBoundingClientRect():null, cs=getComputedStyle(s);
    return {al:s.getAttribute('aria-label'), rot:l?(l.innerText.split('\n')[0]||'').trim():'', top:Math.round(r.top), h:Math.round(r.height), l:Math.round(r.left), r:Math.round(r.right),
      lh:lr?Math.round(lr.height):0, ll:lr?Math.round(lr.left):0, lr:lr?Math.round(lr.right):0, fs:cs.fontSize, rad:cs.borderTopLeftRadius, fw:cs.fontWeight,
      linhas:(()=>{ if(!l) return 0; const g=document.createRange(); const t=[...l.childNodes].find(n=>n!==s&&!n.contains?.(s)&&(n.textContent||'').trim()); if(!t) return 0; g.selectNodeContents(t); return new Set([...g.getClientRects()].map(x=>Math.round(x.top))).size; })()}; });
  const fora=[...document.querySelectorAll('main select')].filter(s=>!f.contains(s)&&['Cultura','Praga-alvo','Classe','Orgânicos'].includes(s.getAttribute('aria-label'))).length;
  const solto=[...document.querySelectorAll('main span,main div')].filter(e=>e.children.length===0&&e.getClientRects().length&&/^(cultura|orgânicos|classe|praga-alvo)$/i.test(e.innerText.trim())&&!f.contains(e)).map(e=>e.innerText.trim());
  const chips=!!document.querySelector('main [role=group][aria-label="Filtrar por classe"]')||[...document.querySelectorAll('main button')].some(b=>/^Aprovados para orgânicos/.test(b.innerText.trim()));
  return {cls:f.className, funil:!!f.querySelector('.mf-rot svg'), L:Math.round(R.left), R:Math.round(R.right), ss, fora, solto, chips, sw:document.scrollingElement.scrollWidth, iw:innerWidth}; })())"""
def faixa(): return json.loads(J(FAIXA) or 'null')
def alinhada(fx, n):
    ss = (fx or {}).get('ss') or []
    return len(ss) == n and len({s['top'] for s in ss}) == 1 and len({s['h'] for s in ss}) == 1 and all(s['lh'] <= s['h'] + 2 and s['ll'] < s['l'] for s in ss)
def dentro(fx): return bool(fx) and fx['sw'] <= fx['iw'] and fx['R'] <= fx['iw'] and all(fx['L'] <= s['ll'] and s['lr'] <= fx['R'] and s['r'] <= fx['R'] for s in fx['ss'])
shot = lambda n: c.shot(os.path.join(PROBE, f'agrofit_faixa_{n}.png'))
try:
    # ---------- A · faixa "Filtros" (1440) ----------
    c.aparelho(1440, 900, 1, False)
    c.goto(U('OS.dc.html'), 1.0); espera("document.querySelector('main [role=group][aria-label=\"Filtros\"] select')", 15)
    pad = J("(()=>{const s=document.querySelector('main [role=group][aria-label=\"Filtros\"] select'); const cs=getComputedStyle(s); return [Math.round(s.getBoundingClientRect().height),cs.fontSize,cs.borderTopLeftRadius,cs.fontWeight];})()")
    c.goto(U('AG-07.dc.html'), 1.0); pr = pronto(); fx = faixa(); shot('1440')
    ok_ss = bool(fx) and [s['al'] for s in fx['ss']] == ['Cultura', 'Classe', 'Orgânicos'] and [s['rot'] for s in fx['ss']] == ['Cultura', 'Classe', 'Orgânicos']
    chk('A1 1440: Cultura, Classe e Orgânicos na faixa "Filtros" (grupo com funil, a mesma faixa das outras telas), rótulo ao lado de cada lista; nenhum filtro da tela fora dela, sem rótulo solto nem chips de classe',
        pr and ok_ss and 'mf-tela' in fx['cls'] and fx['funil'] and fx['fora'] == 0 and not fx['solto'] and not fx['chips'], [pr, fx])
    chk('A2 1440: as listas da faixa alinhadas (mesmo topo e mesma altura, rótulo na mesma linha) e com o seletor padrão da faixa da O.S. (altura, fonte, cantos)',
        alinhada(fx, 3) and pad and all([s['h'], s['fs'], s['rad'], s['fw']] == pad for s in fx['ss']), [pad, (fx or {}).get('ss')])
    SJ = next((v for v, t in opcoes('Cultura') if t == 'Soja'), '')
    setsel('Cultura', SJ); espera("document.querySelector('main [role=group][aria-label=\"Filtros\"] select[aria-label=\"Praga-alvo\"]')", 10); fx2 = faixa(); shot('1440_soja')
    chk('A3 1440 · Cultura = Soja: Praga-alvo entra na mesma faixa, depois de Cultura, e as 4 listas seguem alinhadas numa linha',
        bool(fx2) and [s['al'] for s in fx2['ss']] == ['Cultura', 'Praga-alvo', 'Classe', 'Orgânicos'] and alinhada(fx2, 4) and dentro(fx2), (fx2 or {}).get('ss'))
    setsel('Cultura', '')
    # Classe e Orgânicos filtram; cada opção diz quantas linhas ficam (oráculo: o índice)
    oc = dict(opcoes('Classe')); nhb = oc.get(CLS, ''); setsel('Classe', CLS); n1 = cnt()
    oo = dict(opcoes('Orgânicos')); setsel('Orgânicos', 'S'); n2 = cnt()
    chk(f'A4 Classe = {CLS} → {nf(NHB)} produtos (a opção diz "{CLS} ({nf(NHB)})"); + Orgânicos = Só aprovados → {nf(NHBO)} (a opção diz o mesmo número)',
        NHBO > 0 and nhb == f'{CLS} ({nf(NHB)})' and n1 == f'{nf(NHB)} de {nf(NP)} produtos' and oo.get('S') == f'Só aprovados ({nf(NHBO)})' and n2 == f'{nf(NHBO)} de {nf(NP)} produtos', [nhb, n1, oo, n2])
    setsel('Orgânicos', ''); setsel('Classe', ''); n3 = cnt()
    chk('A5 voltar Classe e Orgânicos a "Todas"/"Todos" devolve a lista inteira', n3 == f'{nf(NP)} de {nf(NP)} produtos', n3)

    # ---------- B · Tox · amb fora do padrão, no painel "Colunas" ----------
    h0 = cab(); cvb = J("(()=>{const b=document.querySelector('main [data-g2cvb]'); return b&&b.getClientRects().length?b.innerText.replace(/\\s+/g,' ').trim():'';})()") or ''
    chk('B1 por produto, o padrão abre sem Tox · amb (6 colunas) e o botão "Colunas" diz que há 1 oculta', h0 == COLS_P and cvb.startswith('Colunas') and '+1' in cvb, [h0, cvb])
    toca('main [data-g2cvb]'); espera("document.querySelector('[role=dialog][aria-label=\"Colunas desta tabela\"]')", 5)
    cx = J("(()=>{const l=[...document.querySelectorAll('[role=dialog][aria-label=\"Colunas desta tabela\"] label')].find(x=>x.innerText.trim()==='Tox · amb'); return l?l.querySelector('input').checked:null;})()")
    J("(()=>{const l=[...document.querySelectorAll('[role=dialog][aria-label=\"Colunas desta tabela\"] label')].find(x=>x.innerText.trim()==='Tox · amb'); if(l) l.querySelector('input').click();})()"); time.sleep(.6)
    clica('[role=dialog][aria-label="Colunas desta tabela"]', 'Fechar'); time.sleep(.4)
    h1 = cab(); tx = coluna('Tox · amb')[:5]
    chk('B2 no painel "Colunas", Tox · amb vem desmarcada; marcar mostra a coluna antes de Na fazenda, com a classificação de cada produto',
        cx is False and h1 == COLS_P[:5] + ['Tox · amb', 'Na fazenda'] and tx and all('Amb' in t for t in tx), [cx, h1, tx])
    setsel('Cultura', SJ); espera("/usos em Soja$/.test(document.querySelector('main').innerText)", 10); time.sleep(.4); h2 = cab()
    setsel('Cultura', ''); time.sleep(.4); h3 = cab()
    chk('B3 a escolha vale por modo: com Soja (por uso) o padrão segue sem Tox · amb e com Praga-alvo, Nome científico e Cultura do uso; sem cultura volta com Tox · amb',
        h2 == COLS_U and h3 == COLS_P[:5] + ['Tox · amb', 'Na fazenda'], [h2, h3])
    toca('main [data-g2cvb]'); time.sleep(.5); clica('[role=dialog][aria-label="Colunas desta tabela"]', 'Restaurar padrão'); time.sleep(.5)
    clica('[role=dialog][aria-label="Colunas desta tabela"]', 'Fechar'); time.sleep(.4); h4 = cab()
    chk('B4 "Restaurar padrão" volta às 6 colunas, sem Tox · amb', h4 == COLS_P, h4)

    # ---------- C · concentração antes do nome ----------
    nm = X['marcas'][0]; esp = conc_txt(X['ing'])
    busca('806'); n806 = int((cnt().split(' de ')[0] or '0').replace('.', '')); L806 = linhas()
    chk(f'C1 a busca "806" acha pela concentração: {n806} produtos (≥ {N806} com algum ingrediente a 806 no índice) e toda linha à vista tem 806',
        n806 >= N806 > 0 and L806 and all('806' in ' '.join(r) for r in L806), [n806, N806, [r[:2] for r in L806 if '806' not in ' '.join(r)][:3]])
    busca(f'806 {nm}'); LX = linhas(); ix = coluna('Ingrediente ativo · grupo químico')
    chk(f'C2 "{nm}" (reg. {X["reg"]}, sem 806 na marca): achado por "806 {nm}" e a célula começa pela concentração: "{esp}"',
        bool(LX) and all(r[0].split('\n')[0] == nm for r in LX) and ix and all(t.split('\n')[0] == esp for t in ix), [LX[:2], ix[:2]])
    shot('806')
    nm2 = XM['marcas'][0]; esp2 = conc_txt(XM['ing']); busca(XM['reg']); ix2 = coluna('Ingrediente ativo · grupo químico')
    J(f"location.hash='#reg-{XM['reg']}'"); espera("document.querySelector('aside[aria-label^=\"Ficha\"]')", 5); time.sleep(.4)
    fic = J("[...document.querySelectorAll('aside[aria-label^=\"Ficha\"] [role=table][aria-label=\"Ingredientes ativos\"] [role=row]')].slice(1).map(r=>[...r.querySelectorAll('[role=cell]')].map(c=>c.innerText.trim()))") or []
    J("document.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true}))"); time.sleep(.4)
    espf = [[IG[x[0]][0], f'{nfc(x[1])} {x[2]}'] for x in XM['ing']]
    chk(f'C3 mistura com decimal ({nm2}): "{esp2}" na lista; a ficha traz a mesma concentração, sem arredondar',
        bool(ix2) and ix2[0].split('\n')[0] == esp2 and [[r[0], r[2]] for r in fic] == espf, [ix2[:1], fic, espf])
    # ordenar pela coluna: pelo nome do ingrediente; na mesma combinação, da menor à maior concentração
    ORD = 'main [role=columnheader] button[aria-label="Ordenar por Ingrediente ativo · grupo químico"]'
    busca('2,4-D'); toca(ORD); time.sleep(.8)
    regs = [re.search(r'Reg\. (\S+)', r[0]).group(1) for r in linhas() if re.search(r'Reg\. (\S+)', r[0])]
    PRR = {p['reg']: p for p in PR}
    seq = [[' + '.join(IG[x[0]][0] for x in PRR[g]['ing']), [x[1] for x in PRR[g]['ing']]] for g in regs if g in PRR]
    ordem = J(f"""(()=>{{const C=new Intl.Collator('pt-BR',{{numeric:true,sensitivity:'base'}}); const a={json.dumps(seq)}; let ruim=[];
      for(let i=1;i<a.length;i++){{ const d=C.compare(a[i-1][0],a[i][0]); if(d>0||(d===0&&a[i-1][1].join(',')!==a[i][1].join(',')&&a[i-1][1][0]>a[i][1][0])) ruim.push([a[i-1],a[i]]); }} return ruim;}})()""")
    chk(f'C4 ordenar por Ingrediente ativo (busca "2,4-D"): {len(seq)} linhas pelo nome do ingrediente e, no mesmo ingrediente, da menor à maior concentração',
        len(seq) >= 30 and ordem == [], [len(seq), (ordem or [])[:3]])
    toca(ORD); time.sleep(.3); toca(ORD); time.sleep(.3)   # volta à ordem da lista
    # filtrar pela coluna: os valores são os nomes (sem a concentração na frente)
    busca(''); toca('main [role=columnheader] button[aria-label="Filtrar Ingrediente ativo · grupo químico"]'); time.sleep(.5)
    D = '[role=dialog][aria-label="Filtrar Ingrediente ativo · grupo químico"]'
    clica(D, 'Limpar'); time.sleep(.2)
    J("(()=>{const i=document.getElementById('g2fq_g_agf'); if(!i) return; const P=HTMLInputElement.prototype; Object.getOwnPropertyDescriptor(P,'value').set.call(i,'2,4-D-dimetilamina'); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true}));})()"); time.sleep(.4)
    vals = J(f"[...document.querySelectorAll('{D} label')].map(l=>l.innerText.trim().split('\\n')[0])") or []
    J(f"(()=>{{const l=[...document.querySelectorAll('{D} label')].find(x=>x.innerText.trim().startsWith('2,4-D-dimetilamina ·')); if(l) l.querySelector('input').click();}})()"); time.sleep(.2)
    clica(D, 'OK'); time.sleep(.8); nd = cnt(); idim = coluna('Ingrediente ativo · grupo químico')
    chk(f'C5 filtrar a coluna: os valores são os nomes ("2,4-D-dimetilamina · …"), sem a concentração na frente; marcar o só-dimetilamina → {NDIM} produtos, cada célula "<concentração> 2,4-D-dimetilamina"',
        vals and any(v.startswith('2,4-D-dimetilamina ·') for v in vals) and not any(re.match(r'^[\d.,]+ \S*/', v) for v in vals) and nd == f'{nf(NDIM)} de {nf(NP)} produtos'
        and idim and all(re.match(r'^[\d.,]+ \S+ 2,4-D-dimetilamina$', t.split('\n')[0]) for t in idim), [vals[:4], nd, NDIM, idim[:3]])
    clica('main', 'Limpar filtros'); time.sleep(.5)
    # sem concentração na fonte (nenhum no arquivo de hoje): só o nome e a dica diz que falta; nada inventado
    sem = J(f"JSON.stringify(__agx.agIngC?[__agx.agIngC([[{DIM},null,'g/L']]), __agx.agIngC([[{DIM},806,'g/L'],[{X['ing'][0][0]},'','']])]:null)")
    sem = json.loads(sem) if sem else None
    chk('C6 ingrediente sem concentração na fonte: só o nome (sem número), listado para a dica "Concentração não informada no AGROFIT"',
        bool(sem) and sem[0] == {'t': '2,4-D-dimetilamina', 'sem': ['2,4-D-dimetilamina'], 'k': ''}
        and sem[1]['t'] == '806 g/L 2,4-D-dimetilamina + ' + IG[X['ing'][0][0]][0] and sem[1]['sem'] == [IG[X['ing'][0][0]][0]], sem)

    # ---------- A · 390 px: a faixa quebra sem sair da tela ----------
    c.aparelho(390, 844, 2, True); c.goto(U('AG-07.dc.html'), 1.0); pronto(); fx3 = faixa(); shot('390')
    setsel('Cultura', SJ); espera("document.querySelector('main [role=group][aria-label=\"Filtros\"] select[aria-label=\"Praga-alvo\"]')", 10); time.sleep(.4); fx4 = faixa(); shot('390_soja')
    chk('A6 390 px: a faixa quebra em linhas sem rolagem lateral; cada lista com o rótulo (numa linha só) cabe na faixa (sem e com Soja), alvo de toque ≥ 44 px',
        dentro(fx3) and dentro(fx4) and len(fx3['ss']) == 3 and len(fx4['ss']) == 4 and all(s['h'] >= 44 and s['linhas'] == 1 for s in fx3['ss'] + fx4['ss']), [fx3, fx4])
    chk('A7 sem erro de execução', not (J("window.__e") or []), J("window.__e"))
finally:
    try: c.close()
    finally: srv.terminate()
print(f'\nRESULTADO: {len(OK)}/{len(OK) + len(FAIL)} ok', FAIL)
sys.exit(1 if FAIL else 0)
