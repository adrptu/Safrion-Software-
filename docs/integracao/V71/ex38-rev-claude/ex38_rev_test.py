# -*- coding: utf-8 -*-
"""EX-38 · revisão do Claude por contraexemplo no navegador (PR #77 do Codex): preparo, saldo e consumo com uma projeção por ordem.
Chrome headless real (comp_lib): mouse, Tab/Enter/Espaço com foco visível, toque a 390 px e mídia de impressão. Dados sintéticos.
Oráculos numéricos explícitos em decimal (Decimal), calculados à parte do código do protótipo:
  OS-0421: saldo 160 ha · Fungicida A 0,5 L/ha → 80 L; custódia 65 L → falta 15 L; Adjuvante 0,25 L/ha → 40 L, sem requisição e sem registro.
  OS-0424: 128 ha · tanque 3.000 L ÷ 100 L/ha = 30 ha por carga → 4 × (3.000 L, 30 ha, 15 L) + (800 L, 8 ha, 4 L); total 12.800 L, 128 ha, 64 L.
Uso: python3 ex38_rev_test.py   (RENDER_DIR = render a testar, padrão _render; BASE_RENDER = render da base para A7, mesma origem;
     MUT_RENDER = render opcional montado com o tanque do PJ-3030 em 2.500 L para A1-tanque; PDF_DIR = onde guardar os PDF da impressão)."""
import sys, os, time, json, re, tempfile, shutil, subprocess, base64
from decimal import Decimal as D
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, servir, MEDE, resumo

R = os.path.abspath(os.environ.get('RENDER_DIR') or os.path.join(HERE, '_render'))
BASE = os.environ.get('BASE_RENDER'); MUT = os.environ.get('MUT_RENDER'); PDF_DIR = os.environ.get('PDF_DIR') or tempfile.gettempdir()
RAIZ = tempfile.mkdtemp(prefix='ex38rev_')   # uma origem só: cur/ (render testado), old/ (base, A7), mut/ (tanque 2.500 L)
os.symlink(R, os.path.join(RAIZ, 'cur'))
if BASE: os.symlink(os.path.abspath(BASE), os.path.join(RAIZ, 'old'))
if MUT: os.symlink(os.path.abspath(MUT), os.path.join(RAIZ, 'mut'))
CEN_LS = 'talhao-os-cenario-v1'
OK, FAIL = [], []
def chk(n, c, x=''):
    (OK if c else FAIL).append(n); print(('OK    ' if c else 'FALHA ') + n + ('' if c else '  · observado: ' + str(x)[:500]), flush=True)

def num(s):   # "12.800" → 12800 · "12,5" → 12.5 (pt-BR), em Decimal
    return D(s.replace('.', '').replace(',', '.'))

p, srv = servir(RAIZ); c = Chrome(); J = c.js
U = lambda pg, w='cur': f'http://127.0.0.1:{p}/{w}/{pg}'

def espera(expr, t=8.0):
    fim = time.time() + t
    while time.time() < fim:
        try:
            v = J(expr)
            if v: return v
        except Exception: pass
        time.sleep(.2)
    return None
def ir(pg, w='cur', t=1.0):
    c.goto(U(pg, w), t); J("window.__errs=window.__errs||[]; if(!window.__ouve){window.__ouve=1; addEventListener('error',e=>__errs.push(e.message));} 1")
def body(): return J("document.body.innerText") or ''
def erros(): return (J("(window.__errs||[]).concat([...document.querySelectorAll('.sc-logic-error')].map(e=>e.innerText))") or [])
def mudar(fn):   # outra tela (Estoque/App/O.S.) muda o cenário pelo comando do próprio protótipo; a tela aberta recebe o aviso de mudança
    r = J(f"(()=>{{const X=window.__cen; if(!X) return 'SEM __cen'; with(X){{ const r=cenMudar(null,c=>{{{fn}}}); window.dispatchEvent(new StorageEvent('storage',{{key:'{CEN_LS}'}})); return r.erro||r.msg||''; }} }})()")
    time.sleep(.5); return r
def cen(expr): return J(f"(()=>{{const c=window.__cen.cenGet(); return ({expr});}})()")
def painel(oid, w='cur'):
    ir('OS.dc.html#' + oid, w, 1.2)
    espera("!!document.querySelector('aside[role=dialog]')")
    if J("(()=>{const bs=[...document.querySelectorAll('aside[role=dialog] section[aria-label] > button[aria-expanded=\"false\"]')]; bs.forEach(b=>b.click()); return bs.length;})()"): time.sleep(.4)
    return J("(()=>{const a=document.querySelector('aside[role=dialog]'); return a?a.innerText:'';})()") or ''
def mb02(oid, w='cur'):
    J(f"localStorage.setItem('talhao-os-mb-os','{oid}')"); ir('MB-02det.dc.html', w, 1.2); return body()
def mb01_card(oid, w='cur'):
    ir('MB-01.dc.html', w, 1.2); b = body(); i = b.find(oid + ' · ')
    if i < 0: return ''
    j = min([k for k in (b.find('OS-04', i + 8), b.find('Abrir por tipo', i)) if k > 0] or [len(b)]); return b[i:j]
PRODS = ('Fungicida A', 'Adjuvante espalhante')
def faltas(txt):
    """falta para terminar por produto, na ordem do texto (o produto é o último nome visto antes do número)."""
    out = {}; cur = None
    for m in re.finditer(r'(Fungicida A|Adjuvante espalhante)|falta para terminar ([\d.,]+) L', txt):
        if m.group(1): cur = m.group(1)
        elif cur and cur not in out: out[cur] = num(m.group(2))
    return out
def usado_painel(prod):   # célula USADO (4ª) da linha do produto na tabela de insumos do painel (linha = grade de 5 colunas)
    return J(f"""(()=>{{const a=document.querySelector('aside[role=dialog]'); if(!a) return null;
      const g=[...a.querySelectorAll('div,tr,[role=row]')].find(r=>/grid-template-columns/.test(r.getAttribute('style')||'')&&r.children.length>=5&&r.children[0].innerText.trim().startsWith({json.dumps(prod)}))
        ||[...a.querySelectorAll('tr,[role=row]')].find(r=>r.innerText.trim().startsWith({json.dumps(prod)}));
      return g?[...g.children].map(x=>x.innerText.trim()):null;}})()""")
FICHA_ROWS = """(()=>{const t=document.querySelector('[role=table][aria-label="Cargas de preparo"]');
  if(t) return [...t.querySelectorAll('[role=row]')].map(r=>{const q=r.getBoundingClientRect(); return {c:[...r.querySelectorAll('[role=cell],[role=columnheader]')].map(x=>x.innerText.trim()),h:q.height,r:q.right};});
  const tb=document.querySelector('table'); if(tb) return [...tb.querySelectorAll('tr')].map(r=>{const q=r.getBoundingClientRect(); return {c:[...r.querySelectorAll('td,th')].map(x=>x.innerText.trim()),h:q.height,r:q.right};});
  return null;})()"""
def cargas_ficha():
    rows = J(FICHA_ROWS) or []; cg, tot = [], None
    for r in rows:
        cs = r['c']
        if len(cs) < 4: continue
        v = re.search(r'([\d.,]+) L', cs[1]); a = re.search(r'([\d.,]+) ha', cs[2]); q = re.findall(r'([\d.,]+) L', cs[3])
        if cs[0].startswith('Total') and v and a and q: tot = (num(v.group(1)), num(a.group(1)), num(q[-1]))
        elif re.match(r'\d', cs[0]) and v and a and q: cg.append((int(re.match(r'\d+', cs[0]).group()), num(v.group(1)), num(a.group(1)), num(q[-1])))
    return cg, tot, rows
def oraculo(tanque, vazao, area, dose):
    hc = D(tanque) / D(vazao); n = int((D(area) / hc).to_integral_value(rounding='ROUND_CEILING')); L = []
    for i in range(n):
        a = min(hc, D(area) - hc * i); L.append((i + 1, a * D(vazao), a, a * D(dose)))
    return L, (D(area) * D(vazao), D(area), D(area) * D(dose))
def mesmo(cg, esp): return len(cg) == len(esp) and all(a[0] == b[0] and abs(a[1] - b[1]) < D('0.001') and abs(a[2] - b[2]) < D('0.001') and abs(a[3] - b[3]) < D('0.001') for a, b in zip(cg, esp))
AE = """(()=>{const e=document.activeElement; if(!e||e===document.body) return null; const cs=getComputedStyle(e);
  const vis=(cs.outlineStyle!=='none'&&parseFloat(cs.outlineWidth)>=2)||(cs.boxShadow&&cs.boxShadow!=='none');
  return {tag:e.tagName,t:(e.innerText||e.getAttribute('aria-label')||'').replace(/\\s+/g,' ').trim().slice(0,60),lab:e.getAttribute('aria-label')||'',rid:e.getAttribute('data-rid')||'',vis};})()"""
def tab_ate(pred, n=160, shift=False):
    for i in range(n):
        c.tab(1, shift); a = J(AE)
        if a and pred(a): return a, i + 1
    return None, n
def digitar(txt):   # teclado: seleciona tudo no campo focado e digita
    c.call('Input.dispatchKeyEvent', {'type': 'keyDown', 'key': 'a', 'code': 'KeyA', 'windowsVirtualKeyCode': 65, 'modifiers': 2, 'commands': ['selectAll']})
    c.call('Input.dispatchKeyEvent', {'type': 'keyUp', 'key': 'a', 'code': 'KeyA', 'windowsVirtualKeyCode': 65, 'modifiers': 2})
    c.call('Input.insertText', {'text': txt}); time.sleep(.15)
def enter(): c.tecla('Enter', 'Enter', 13, text='\r'); time.sleep(.6)
def espaco(): c.tecla(' ', 'Space', 32, text=' '); time.sleep(.6)
FOCO = []
def kbd_ok(a, nome):
    FOCO.append((nome, bool(a and a['vis'])))
    return a
SCROLL_X = "(()=>({doc:document.documentElement.scrollWidth,body:document.body.scrollWidth,w:innerWidth,fora:[...document.querySelectorAll('body *')].filter(e=>{const r=e.getBoundingClientRect(); if(!(r.width>0&&r.height>0)) return false; for(let p=e.parentElement;p;p=p.parentElement){const ox=getComputedStyle(p).overflowX; if((ox==='auto'||ox==='scroll')&&p!==document.body&&p!==document.documentElement) {const pr=p.getBoundingClientRect(); if(pr.right<=innerWidth+1) return false;}} return r.right>innerWidth+1;}).slice(0,4).map(e=>e.tagName+':'+(e.innerText||'').slice(0,30))}))()"
def alvo_txt(t, sel='button,a'):
    return J(f"""(()=>{{const n=s=>(s||'').replace(/\\s+/g,' ').trim(); const e=[...document.querySelectorAll({json.dumps(sel)})].find(x=>x.offsetParent!==null&&n(x.innerText)===({json.dumps(t)}));
      if(!e) return null; e.scrollIntoView({{block:'center'}}); const r=e.getBoundingClientRect(); return {{x:r.left+r.width/2,y:r.top+r.height/2,w:r.width,h:r.height,dis:!!e.disabled}};}})()""")

try:
    # ================= A6 · consumo ausente ≠ zero (estado inicial) =================
    c.aparelho(1440, 900); ir('Main.dc.html', t=.3); J("localStorage.clear(); sessionStorage.clear(); 1")
    pan = painel('OS-0421'); u = usado_painel('Adjuvante espalhante') or []
    print('     painel OS-0421 · Adjuvante:', u)
    chk('A6a painel OS-0421: USADO do Adjuvante = "Sem registro" (nem 47,5 L nem 0 L)', 'Sem registro' in u and not any(x in ('47,5 L', '0 L') for x in u), u)
    f0 = faltas(pan)
    chk('A2-0 painel OS-0421: falta para terminar Fungicida A = 15 L (0,5 × 160 − 65) e Adjuvante = 40 L (0,25 × 160 − 0)', f0.get('Fungicida A') == D(15) and f0.get('Adjuvante espalhante') == D(40), f0)
    chk('P2 painel OS-0421: preparo 3.000 L · 100 L/ha · 30 ha por carga · 6 cargas · última 10 ha · Fungicida A 15 L · Adjuvante 7,5 L (oráculo 160 ÷ 30)',
        all(s in pan for s in ('3.000 L · 100 L/ha · 30 ha por carga · 6 cargas · última 10 ha', 'Fungicida A 15 L por carga cheia', 'Adjuvante espalhante 7,5 L por carga cheia')),
        pan[pan.find('RETIRADA'):][:300] if 'RETIRADA' in pan else pan[:300])
    card = mb01_card('OS-0421'); f1 = faltas(card)
    chk('A6b MB-01 OS-0421: Adjuvante "Consumo sem registro", sem 47,5 L; falta 15 L e 40 L como no painel', 'Consumo sem registro' in card and '47,5' not in card and f1 == f0, (card[:400], f1))
    d421 = mb02('OS-0421'); f2 = faltas(d421[d421.find('Insumos'):])
    adj = d421[d421.find('Adjuvante espalhante ·'):][:200]
    chk('A6c MB-02det OS-0421: Adjuvante sem número de consumo inventado (sem "consumido 0" e sem 47,5 L); falta igual ao painel', 'consumido' not in adj and '47,5' not in adj and f2 == f0, (adj, f2))
    chk('P2 MB-02det OS-0421: o mesmo preparo do painel (6 cargas · última 10 ha · 15 L · 7,5 L)',
        all(s in d421 for s in ('3.000 L · 100 L/ha · 30 ha por carga · 6 cargas · última 10 ha', 'Fungicida A 15 L por carga cheia', 'Adjuvante espalhante 7,5 L por carga cheia')), d421[d421.find('Andamento'):][:300])

    # ================= A1 · ficha impressa da OS-0424 gerada da projeção =================
    esp0, tot0 = oraculo(3000, 100, 128, D('0.5'))
    ir('OS-0424-ficha.dc.html', t=1.4); cg, tot, rows = cargas_ficha()
    chk('A1a ficha OS-0424: 5 cargas = 4 × (3.000 L, 30 ha, 15 L) + (800 L, 8 ha, 4 L); total 12.800 L · 128 ha · 64 L', mesmo(cg, esp0) and tot == tot0, (cg, tot))
    ult = [r['c'][0] for r in rows if r['c'] and re.match(r'5\b', r['c'][0])]
    chk('A1e ficha: a última carga continua marcada como parcial (base: "5 · parcial")', any('parcial' in x for x in ult), ult)
    fb = body()
    chk('A1f ficha: mantém a instrução do caldeiro "complete com água até o volume da carga… última carga é proporcional" (base)', 'complete com água' in fb.lower() and 'proporcional' in fb.lower(), fb[fb.find('CALDEIRO'):][:300])
    # mídia de impressão: barra de ações some; a tabela inteira (cabeçalho, 5 cargas e total) aparece e cabe na folha
    c.call('Emulation.setEmulatedMedia', {'media': 'print'}); time.sleep(.4)
    np_ = J("(()=>{const e=document.querySelector('.noprint'); return e?getComputedStyle(e).display:'sem .noprint';})()"); cg_p, tot_p, rows_p = cargas_ficha()
    chk('A1c impressão (media print): ações ocultas e tabela inteira visível (5 cargas + total, todas as linhas com altura e dentro de 794 px)',
        np_ == 'none' and mesmo(cg_p, esp0) and tot_p == tot0 and all(r['h'] > 0 and r['r'] <= 795 for r in rows_p), (np_, cg_p, tot_p, [(r['h'], r['r']) for r in rows_p]))
    pdf = c.call('Page.printToPDF', {'printBackground': True, 'preferCSSPageSize': False, 'paperWidth': 8.27, 'paperHeight': 11.69})
    fp = os.path.join(PDF_DIR, 'ex38_ficha_0424_' + ('base' if 'v69b' in R else 'pr') + '.pdf'); open(fp, 'wb').write(base64.b64decode(pdf['data']))
    try: tx = subprocess.run(['pdftotext', '-layout', fp, '-'], capture_output=True, text=True, timeout=60).stdout
    except Exception as e: tx = 'pdftotext: ' + str(e)
    linhas = [l for l in tx.splitlines() if re.match(r'^\s*(\d+(\s*·\s*parcial)?|Total)\s+[\d.]+(,\d+)? L(\s+de(\s+calda)?)?\s+[\d.]+(,\d+)? ha', l)]
    print('     PDF:', fp, '·', len(tx), 'caracteres ·', linhas)
    chk('A1d PDF impresso (printToPDF + pdftotext): 5 linhas de carga e o total 12.800 L · 128 ha · 64 L', len([l for l in linhas if not l.strip().startswith('Total')]) == 5 and any('12.800 L' in l and '128 ha' in l and '64 L' in l for l in linhas), linhas)
    c.call('Emulation.setEmulatedMedia', {'media': ''}); time.sleep(.2)
    # instrução muda (outra tela grava 120 L/ha na versão vigente) → a ficha recalcula: 25 ha por carga, 6 cargas, última 3 ha (360 L, 1,5 L)
    ir('OS-0424-app.dc.html', t=1.2)
    r = mudar("const o=c.ordens['OS-0424']; o.instrucao={vazao:120,origem:'instrução da O.S. vigente (demonstração · teste)',versao:o.versao}; return {msg:'instrução 120'};")
    esp1, tot1 = oraculo(3000, 120, 128, D('0.5'))
    ir('OS-0424-ficha.dc.html', t=1.4); cg, tot, _ = cargas_ficha(); fb = body()
    chk('A1b instrução 120 L/ha → ficha com 6 cargas: 5 × (3.000 L, 25 ha, 12,5 L) + (360 L, 3 ha, 1,5 L); total 15.360 L · 128 ha · 64 L',
        mesmo(cg, esp1) and tot == tot1 and '120 L/ha' in fb, (r, cg, tot))
    ap_ = (ir('OS-0424-app.dc.html', t=1.2), body())[1]; p424 = painel('OS-0424')
    chk('A1b2 a mesma mudança chega ao app e ao painel da OS-0424 (25 ha por carga · 6 cargas · última 3 ha · 12,5 L)',
        'Carga 1 de 6' in ap_ and '25 ha por carga · 6 cargas · última 3 ha' in ap_ and '25 ha por carga · 6 cargas · última 3 ha' in p424 and 'Fungicida A 12,5 L por carga cheia' in p424,
        (ap_[ap_.find('CALDEIRO'):][:200], p424[p424.find('FICHAS'):][:200]))
    if MUT:
        ir('Main.dc.html', 'mut', .3); J("localStorage.clear(); 1")
        esp2, tot2 = oraculo(2500, 100, 128, D('0.5'))
        ir('OS-0424-ficha.dc.html', 'mut', 1.4); cg, tot, _ = cargas_ficha()
        chk('A1g tanque do PJ-3030 = 2.500 L no cadastro (montagem mutante) → ficha com 6 cargas: 5 × (2.500 L, 25 ha, 12,5 L) + (300 L, 3 ha, 1,5 L)', mesmo(cg, esp2) and tot == tot2, (cg, tot))
        pm = painel('OS-0421', 'mut'); dm = mb02('OS-0421', 'mut')
        s7 = '2.500 L · 100 L/ha · 25 ha por carga · 7 cargas · última 10 ha'
        chk('A1h tanque 2.500 L: OS-0421 com 7 cargas (160 ÷ 25 = 6,4) · Fungicida A 12,5 L · Adjuvante 6,25 L, igual no painel e no MB-02det',
            s7 in pm and s7 in dm and 'Adjuvante espalhante 6,25 L por carga cheia' in pm and 'Adjuvante espalhante 6,25 L por carga cheia' in dm, (pm[pm.find('RETIRADA'):][:200], dm[dm.find('Preparo'):][:200]))
        ir('Main.dc.html', 'mut', .3); J("localStorage.clear(); 1")
    else:
        print('     A1g/A1h: MUT_RENDER não informado (tanque mutante não executado)')

    # ================= A5 + A8 · marcar carga sem aplicar, só no teclado =================
    ir('Main.dc.html', t=.3); J("localStorage.clear(); 1")
    ir('OS-0424-app.dc.html', t=1.2)
    print('     Estoque (outra tela) entrega a REQ-039:', mudar("return cenEntregar(c,'REQ-039','Fungicida A',65,'Marcos','Rui');")[:80])
    ir('OS-0424-app.dc.html', t=1.2)
    a, n = tab_ate(lambda a: a['tag'] == 'BUTTON' and a['t'].startswith('Confirmar recebimento'), 40); kbd_ok(a, 'Confirmar recebimento')
    enter(); time.sleep(.4)
    antes = cen("JSON.stringify({rev:c.rev,ap:c.ordens['OS-0424'].ap,real:c.ordens['OS-0424'].realizado,saldo:c.ordens['OS-0424'].saldo,it:c.reqs['REQ-039'].itens.map(i=>[i.custodia,i.consumido]),movs:(c.movs||[]).length})")
    J("document.activeElement&&document.activeElement.blur&&document.activeElement.blur(); 1")
    a, n = tab_ate(lambda a: a['tag'] == 'BUTTON' and a['t'] == 'Carga 1 preparada', 40); kbd_ok(a, 'Carga 1 preparada')
    espaco(); t1 = body(); toast1 = J("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).join(' | ')") or ''
    a2 = J(AE); kbd_ok(a2 if a2 and a2['t'] == 'Carga 2 preparada' else None, 'Carga 2 preparada (foco fica no botão)')
    enter(); t2 = body()
    depois = cen("JSON.stringify({rev:c.rev,ap:c.ordens['OS-0424'].ap,real:c.ordens['OS-0424'].realizado,saldo:c.ordens['OS-0424'].saldo,it:c.reqs['REQ-039'].itens.map(i=>[i.custodia,i.consumido]),movs:(c.movs||[]).length})")
    chk('A8a teclado: Tab até "Confirmar recebimento" e "Carga 1 preparada"; Espaço e Enter acionam; foco visível em todos os alvos', all(v for _, v in FOCO) and '2 de 5 cargas preparadas' in t2, (FOCO, t2[t2.find('cargas prep') - 10:][:40]))
    chk('A5a marcar 2 cargas não grava aplicação nem consumo: cenário idêntico (rev, apontamentos, realizado 0, saldo 128, custódia 65, consumido 0, movimentos)', antes == depois and json.loads(depois)['it'] == [[65, 0]], (antes, depois))
    chk('A5b o retorno diz que a marcação é só desta tela e não é aplicação (sem "Salvo no aparelho")', 'ainda não é aplicação' in toast1 and 'Salvo no aparelho' not in toast1, toast1)
    p424 = painel('OS-0424'); u424 = usado_painel('Fungicida A') or []
    chk('A5c painel OS-0424 depois das marcações: USADO 0 L, nenhum apontamento, Liberadas', '0 L' in u424 and cen("[c.ordens['OS-0424'].etapa,(c.ordens['OS-0424'].ap||[]).length]") == ['Liberadas', 0], (u424, cen("[c.ordens['OS-0424'].etapa,(c.ordens['OS-0424'].ap||[]).length]")))
    ir('OS-0424-app.dc.html', t=1.2); t3 = body()
    chk('A5d recarregar a tela: a marcação não persiste (0 de 5 cargas preparadas)', '0 de 5 cargas preparadas' in t3, t3[t3.find('cargas prep') - 10:][:40])
    for k in (1, 2):
        bb = alvo_txt(f'Carga {k} preparada');
        if bb: c.mouse(bb['x'], bb['y']); c.mouse(bb['x'], bb['y'], 'mousePressed', 'left'); c.mouse(bb['x'], bb['y'], 'mouseReleased', 'left'); time.sleep(.6)
    t4 = body()
    r = mudar("const o=c.ordens['OS-0424']; o.instrucao={vazao:120,origem:'instrução nova (teste)',versao:o.versao}; return {msg:'instrução 120'};"); time.sleep(.4); t5 = body()
    chk('A5e preparo diferente (instrução 120 L/ha gravada por outra tela) não reaproveita as 2 marcações: 0 de 6', '2 de 5 cargas preparadas' in t4 and '0 de 6 cargas preparadas' in t5, (t4[t4.find('cargas prep') - 10:][:40], r, t5[t5.find('cargas prep') - 10:][:40]))
    r = mudar("c.ordens['OS-0424'].versao='v2'; return {msg:'v2'};"); time.sleep(.4); t6 = body()
    prim = J("(()=>{const b=document.querySelector('main').nextElementSibling.querySelector('button'); return b?[b.innerText.trim(),b.disabled]:null;})()")
    chk('A5f versão diferente (v2 sem instrução própria): preparo bloqueado com motivo, sem cargas e sem "100 L/ha"/"120 L/ha"',
        'Vazão não informada' in t6 and prim and prim[1] is True and 'Carga 1 ·' not in t6 and ' L/ha · ' not in t6[t6.find('CALDEIRO'):t6.find('OPERADOR')], (prim, t6[t6.find('CALDEIRO'):][:300]))

    # ================= A3 · versão diferente sem instrução (UI: OS-0430 liberada; estado: OS-0424 v2) =================
    ir('Main.dc.html', t=.3); J("localStorage.clear(); 1")
    p430 = painel('OS-0430')
    lib = J("(()=>{const b=[...document.querySelectorAll('aside[role=dialog] button')].find(b=>b.innerText.trim()==='Liberar para execução'&&b.getAttribute('aria-disabled')!=='true'); if(!b) return false; b.click(); return true;})()"); time.sleep(.5)
    cf = J("(()=>{const b=[...document.querySelectorAll('aside[role=dialog] button')].find(b=>b.innerText.trim()==='Confirmar liberação'); if(!b) return false; b.click(); return true;})()"); time.sleep(.8)
    p430 = painel('OS-0430'); fx = p430[p430.find('FICHAS') if 'FICHAS' in p430 else p430.find('RETIRADA'):][:260]
    chk('A3a OS-0430 liberada pela tela (v1 sem instrução de vazão): "Vazão não informada · conferir instrução", sem cargas nem 100 L/ha inventados',
        cen("c.ordens['OS-0430'].etapa") == 'Liberadas' and 'Vazão não informada' in fx and '100 L/ha' not in fx and 'cargas' not in fx, (lib, cf, cen("c.ordens['OS-0430'].etapa"), fx))
    ir('MB-01.dc.html', t=1.0); mudar("c.ordens['OS-0424'].versao='v2'; return {msg:'v2'};")
    p424 = painel('OS-0424'); fx = p424[p424.find('FICHAS'):][:200]; d424 = mb02('OS-0424'); dl = d424[d424.find('Preparo'):][:160]
    ir('OS-0424-ficha.dc.html', t=1.4); cg, tot, _ = cargas_ficha(); fb = body()
    imp = J("(()=>{const b=[...document.querySelectorAll('button')].find(b=>b.innerText.trim()==='Imprimir'); return b?b.disabled:null;})()")
    chk('A3b OS-0424 em v2 sem instrução própria: painel, MB-02det e ficha avisam "Vazão não informada", ficha sem cargas e Imprimir indisponível',
        'Vazão não informada' in fx and 'Vazão não informada' in dl and 'Vazão não informada' in fb and not cg and imp is True and '3.000 L de calda' not in fb, (fx, dl, cg, imp))

    # ================= A4 · sem conjunto =================
    ir('Main.dc.html', t=.3); J("localStorage.clear(); 1")
    p504 = painel('OS-0504'); fx = p504[p504.find('FICHAS') if 'FICHAS' in p504 else p504.find('RETIRADA'):][:260]
    print('     OS-0504 recursos:', p504[p504.find('RECURSOS'):][:120].replace('\n', ' | '))
    chk('A4a OS-0504 (Lagoa, pulverização sem pulverizador alocado): "Sem conjunto · alocar pulverizador", sem tanque/cargas padrão', 'Sem conjunto' in fx and '3.000' not in fx and 'cargas' not in fx, fx)
    ir('MB-01.dc.html', t=1.0); mudar("c.ordens['OS-0424'].rec={PJ:'DI'}; return {msg:'PJ trocado por DI'};")
    p424 = painel('OS-0424'); fx = p424[p424.find('FICHAS'):][:200]; d424 = mb02('OS-0424'); dl = d424[d424.find('Preparo'):][:160]
    ir('OS-0424-app.dc.html', t=1.2); ab = body(); ir('OS-0424-ficha.dc.html', t=1.4); cg, tot, _ = cargas_ficha(); fb = body()
    chk('A4b OS-0424 sem pulverizador (PJ trocado por distribuidor): "Sem conjunto" no painel, MB-02det, app e ficha; nenhum 3.000 L/100 L/ha inventado',
        all('Sem conjunto' in s for s in (fx, dl, ab, fb)) and not cg and '3.000 L de calda' not in ab + fb and '100 L/ha' not in fx + dl, (fx, dl, ab[ab.find('CALDEIRO'):][:120], cg))

    # ================= A2 + A8 · saldo após movimento real (apontamento no painel, só teclado) =================
    ir('Main.dc.html', t=.3); J("localStorage.clear(); 1"); ir('OS.dc.html', t=1.4)
    FOCO.clear()
    a, n = tab_ate(lambda a: a['rid'] == 'OS-0421', 220); kbd_ok(a, 'linha OS-0421 (%d Tab)' % n)
    enter(); espera("!!document.querySelector('aside[role=dialog]')")
    a, n = tab_ate(lambda a: a['tag'] == 'BUTTON' and a['t'] == 'Registrar apontamento', 30); kbd_ok(a, 'Registrar apontamento')
    enter(); espera("!!document.querySelector('aside[role=dialog] input[aria-label=\"Área feita em hectares\"]')")
    a, n = tab_ate(lambda a: a['lab'] == 'Área feita em hectares', 30); kbd_ok(a, 'Área feita'); digitar('20')
    a, n = tab_ate(lambda a: a['lab'] == 'Usado de Fungicida A (L)', 6); kbd_ok(a, 'Usado de Fungicida A'); digitar('8')
    a, n = tab_ate(lambda a: a['lab'] == 'Usado de Adjuvante espalhante (L)', 6); kbd_ok(a, 'Usado de Adjuvante'); digitar('0')
    a, n = tab_ate(lambda a: a['tag'] == 'BUTTON' and a['t'] == 'Salvar apontamento', 6); kbd_ok(a, 'Salvar apontamento')
    enter(); time.sleep(.6)
    st = cen("[c.ordens['OS-0421'].saldo,c.reqs['REQ-035'].itens[0].custodia,c.reqs['REQ-035'].itens[0].consumido,c.ordens['OS-0421'].ap.filter(a=>a.st!=='Previsto').length]")
    print('     após o apontamento (saldo, custódia, consumido, turnos):', st, '·', (J("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).join(' | ')") or '')[:200])
    chk('A8b teclado: Tab até a linha, Enter abre; Tab/Enter até Salvar apontamento; foco visível em cada alvo', all(v for _, v in FOCO) and st and st[0] == 140, (FOCO, st))
    pan = painel('OS-0421'); u = usado_painel('Adjuvante espalhante') or []; fp_ = faltas(pan[pan.find('INSUMOS'):]); fm = faltas(mb01_card('OS-0421')); fd_ = mb02('OS-0421'); fd = faltas(fd_[fd_.find('Insumos'):])
    print('     falta para terminar · painel', fp_, '· MB-01', fm, '· MB-02det', fd)
    print('     USADO do Adjuvante depois de informar 0 L no apontamento (o 0 fora da requisição não é gravado em cons):', u)
    chk('A2a apontamento de 20 ha com 8 L informados: falta Fungicida A = 0,5 × 140 − 57 = 13 L e Adjuvante = 0,25 × 140 = 35 L, iguais no painel, MB-01 e MB-02det',
        fp_ == fm == fd == {'Fungicida A': D(13), 'Adjuvante espalhante': D(35)}, (fp_, fm, fd))
    chk('A2b preparo do saldo novo igual no painel e no MB-02det: 140 ha → 5 cargas · última 20 ha', '30 ha por carga · 5 cargas · última 20 ha' in pan and '30 ha por carga · 5 cargas · última 20 ha' in fd_, (pan[pan.find('RETIRADA'):][:160], fd_[fd_.find('Preparo'):][:160]))
    # contraexemplo: turno fechado no app SEM SINAL (o caso normal do campo), cenário novo: 20 ha e 10 L (dose × área) baixam a custódia no aparelho
    ir('Main.dc.html', t=.3); J("localStorage.clear(); 1"); ir('MB-01.dc.html', t=1.0)
    print('     app sem sinal:', mudar("cenSinal(c,false); cenIniciarTurno(c,'OS-0421'); return cenFecharTurno(c,20,3,{'Fungicida A':10,'Adjuvante espalhante':0},'');")[:160])
    st = cen("[c.ordens['OS-0421'].saldo,c.reqs['REQ-035'].itens[0].custodia,(c.ordens['OS-0421'].ap||[]).filter(a=>a.sinc===false).map(a=>a.ha)]")
    pan = painel('OS-0421'); fp_ = faltas(pan[pan.find('INSUMOS'):]); fm = faltas(mb01_card('OS-0421')); fd_ = mb02('OS-0421'); fd = faltas(fd_[fd_.find('Insumos'):])
    print('     sem sinal (saldo, custódia, pendente ha):', st, '· falta painel', fp_, '· MB-01', fm, '· MB-02det', fd)
    ir('OS.dc.html#OS-0421', t=1.2); painel('OS-0421'); uf = usado_painel('Fungicida A') or []
    tri = J("(()=>{const a=document.querySelector('aside[role=dialog]'); const t=a?a.innerText:''; const i=t.indexOf('Reservado 175 L'); return i<0?'':t.slice(i,i+220);})()") or ''
    print('     sem sinal · painel Fungicida A (colunas):', uf, '· trilha:', tri.replace('\n', ' | '))
    chk('A2g sem sinal, a linha do painel é coerente: USADO e "falta" usam a mesma custódia da trilha (osReqVis: a baixa do aparelho volta até o envio)',
        bool(uf) and 'Em custódia 65 L' in tri and '95 L' in uf[3] and 'falta para terminar 15 L' in uf[4], (uf, tri))
    chk('A2c sem sinal, as três telas mostram a mesma falta (consistência)', fp_ == fm == fd and bool(fp_), (fp_, fm, fd))
    chk('A2d sem sinal, a falta não cresce pelo consumo já baixado no aparelho: 0,5 × (160 − 20) − 55 = 15 L (não 0,5 × 160 − 55 = 25 L)', fm.get('Fungicida A') == D(15), (st, fm))
    print('     MB-01 sem sinal:', mb01_card('OS-0421').replace('\n', ' | ')[:400])
    chk('A2f sem sinal, o preparo do MB-02det é do que falta aplicar (160 − 20 = 140 ha → 5 cargas · última 20 ha), não dos 160 ha do servidor',
        '30 ha por carga · 5 cargas · última 20 ha' in fd_, fd_[fd_.find('Preparo'):][:160])
    ir('MB-01.dc.html', t=1.0); print('     sinal volta:', mudar("return cenSinal(c,true);")[:120])
    st = cen("[c.ordens['OS-0421'].saldo,c.reqs['REQ-035'].itens[0].custodia]")
    fm = faltas(mb01_card('OS-0421')); pan = painel('OS-0421'); fp_ = faltas(pan[pan.find('INSUMOS'):])
    chk('A2e com sinal: saldo 140 ha, custódia 55 L → falta 15 L no painel e no MB-01', st == [140, 55] and fm.get('Fungicida A') == D(15) == fp_.get('Fungicida A'), (st, fm, fp_))

    # ================= A7 · cenário salvo na versão anterior (base) preservado na versão nova =================
    if BASE:
        ir('Main.dc.html', 'old', .3); J("localStorage.clear(); 1"); ir('MB-01.dc.html', 'old', 1.2)
        r = mudar("cenEntregar(c,'REQ-039','Fungicida A',65,'Marcos','Rui'); cenConfirmarRecebimento(c,'REQ-039'); return cenOcorrencia(c,'OS-0421','Clima','Vento forte às 10:30 (teste sintético)');")
        salvo = J(f"JSON.parse(localStorage.getItem('{CEN_LS}')||'null')") or {}
        print('     salvo pela base:', r[:80], '· v', salvo.get('v'), '· rev', salvo.get('rev'), '· instrucao na OS-0424:', 'instrucao' in (salvo.get('ordens') or {}).get('OS-0424', {}))
        ir('OS-0424-app.dc.html', t=1.4); ab = body()
        st = cen("[c.v,c.rev,c.reqs['REQ-039'].itens[0].custodia,c.reqs['REQ-039'].itens[0].confirmado,(c.ocorr||[]).length,'instrucao' in c.ordens['OS-0424']]")
        chk('A7a versão nova lê o cenário salvo pela base sem perder nada (mesma v e rev, REQ-039 com 65 L confirmados, ocorrência registrada)',
            st and st[0] == salvo.get('v') and st[1] == salvo.get('rev') and st[2] == 65 and st[3] is True and st[4] == len(salvo.get('ocorr') or []), (st, salvo.get('v'), salvo.get('rev')))
        chk('A7b sem instrução gravada no cenário antigo, a mesma versão usa a instrução da semente: app com 5 cargas de 30 ha e "Recebido · 65 L"',
            'Carga 1 de 5' in ab and '30 ha por carga · 5 cargas · última 8 ha' in ab and 'Recebido · 65 L' in ab, ab[:400])
        fm = faltas(mb01_card('OS-0424'))
        chk('A7c MB-01 OS-0424 com o cenário antigo: 65 L com você → falta para terminar 0 L (0,5 × 128 = 64 ≤ 65)', fm.get('Fungicida A') == D(0), fm)
    else:
        print('     A7: BASE_RENDER não informado (não executado)')

    # ================= X · contraexemplos adicionais (fora da lista A1–A9) =================
    def ins_sit(prod):   # 5ª coluna (situação) da linha do insumo no painel aberto
        u = usado_painel(prod) or []; return u
    # X1 · ruído de ponto flutuante no saldo: 160 − 0,2 − 39,8 = 120 ha (exato) → 4 cargas de 30 ha; não pode surgir 5ª carga de 0 ha
    ir('Main.dc.html', t=.3); J("localStorage.clear(); 1"); ir('OS.dc.html', t=1.2)
    r1 = mudar("return osc_apontar(c,'OS-0421','27/09',0.2,null,null,'X1-a');"); r2 = mudar("return osc_apontar(c,'OS-0421','28/09',39.8,null,null,'X1-b');")
    sd = cen("c.ordens['OS-0421'].saldo"); pan = painel('OS-0421'); d421 = mb02('OS-0421')
    print('     X1 saldo após 0,2 + 39,8 ha:', repr(sd), '·', r1[:60], '·', r2[:60])
    chk('X1 saldo 160 − 0,2 − 39,8 = 120 ha: preparo "4 cargas · última 30 ha" no painel e no MB-02det (sem 5ª carga de 0 ha)',
        '30 ha por carga · 4 cargas · última 30 ha' in pan and '30 ha por carga · 4 cargas · última 30 ha' in d421, (pan[pan.find('RETIRADA'):][:140], d421[d421.find('Preparo'):][:140]))
    # X2 · saldo menor que uma carga: 160 − 140 = 20 ha → "1 carga"
    ir('Main.dc.html', t=.3); J("localStorage.clear(); 1"); ir('OS.dc.html', t=1.2)
    r = mudar("return osc_apontar(c,'OS-0421','27/09',140,{'Fungicida A':65,'Adjuvante espalhante':0},[],'X2');"); pan = painel('OS-0421')
    pr = pan[pan.find('RETIRADA'):][:160]; print('     X2', r[:80], '·', pr.replace('\n', ' | '))
    chk('X2 saldo de 20 ha: o texto diz "1 carga" (não "1 cargas")', '1 carga ' in pr or '1 carga ·' in pr, pr)
    # X3 · recebimento não depende do preparo: versão nova sem instrução não pode esconder "Confirmar recebimento" no app
    ir('Main.dc.html', t=.3); J("localStorage.clear(); 1"); ir('OS-0424-app.dc.html', t=1.2)
    mudar("cenEntregar(c,'REQ-039','Fungicida A',65,'Marcos','Rui'); c.ordens['OS-0424'].versao='v2'; return {msg:'entregue e v2'};")
    ir('OS-0424-app.dc.html', t=1.2); prim = J("(()=>{const b=document.querySelector('main').nextElementSibling.querySelector('button'); return b?[b.innerText.trim(),b.disabled]:null;})()")
    ab = body(); print('     X3 app:', prim, '·', ab[ab.find('CALDEIRO'):][:260].replace('\n', ' | '))
    chk('X3 app OS-0424 entregue e versão sem instrução: "Confirmar recebimento" continua disponível (a trava do preparo não bloqueia a custódia)', prim == ['Confirmar recebimento', False], prim)
    # X4 · insumo com quantidade fixa (dose 0, total da versão): OB-0112 precisa de 881 caixas; a falta não pode ser 0 un
    ir('Main.dc.html', t=.3); J("localStorage.clear(); 1"); pob = painel('OB-0112'); u = ins_sit('Caixa de mamão Formosa 10 kg')
    print('     X4 OB-0112 insumo:', u, '· tot', cen("(c.ordens['OB-0112'].ins||[]).map(i=>[i.dose,i.tot])"))
    print('     X4 (informativo): OB-0112 não abre painel na O.S. (beneficiamento); a divergência com cenOsSup (total fixo da versão) fica latente, sem tela afetada nesta fatia')
    # X5/X6 · textos de situação que a fatia trocou (registro para o relatório; não reprovam)
    p430 = painel('OS-0430'); u430 = ins_sit('Glifosato 480'); p415 = painel('OS-0415'); u415 = ins_sit('Glifosato 480')
    print('     X5 OS-0430 (A liberar) Glifosato:', u430); print('     X6 OS-0415 (Encerradas) Glifosato:', u415)
    # X7 · ficha depois do início: cabeçalho com a área da ordem e tabela com o saldo
    ir('MB-01.dc.html', t=1.0); mudar("cenEntregar(c,'REQ-039','Fungicida A',65,'Marcos','Rui'); cenConfirmarRecebimento(c,'REQ-039'); cenIniciarTurno(c,'OS-0424'); return cenFecharTurno(c,30,2,null,'');")
    ir('OS-0424-ficha.dc.html', t=1.4); cg, tot, _ = cargas_ficha(); fb = body()
    print('     X7 ficha após 30 ha: cabeçalho', fb[fb.find('OS-0424 ·'):][:90].replace('\n', ' | '), '· total', tot, '· cargas', len(cg))

    # X8 · área toda feita sem sinal (sequência do app_mb03_turno_test): 20 ha com sinal (10 L), depois 120 ha (50 L) e 20 ha (5 L) no aparelho
    ir('Main.dc.html', t=.3); J("localStorage.clear(); 1"); ir('MB-01.dc.html', t=1.0)
    mudar("cenIniciarTurno(c,'OS-0421'); cenFecharTurno(c,20,3,{'Fungicida A':10},''); cenSinal(c,false); cenIniciarTurno(c,'OS-0421'); cenFecharTurno(c,120,8,{'Fungicida A':50},''); cenIniciarTurno(c,'OS-0421'); return cenFecharTurno(c,20,2,{'Fungicida A':5},'');")
    st = cen("[c.ordens['OS-0421'].saldo,c.reqs['REQ-035'].itens[0].custodia,(c.ordens['OS-0421'].ap||[]).filter(a=>a.sinc===false).reduce((s,a)=>s+a.ha,0)]")
    card = mb01_card('OS-0421'); fm = faltas(card)
    print('     X8 (saldo, custódia, ha no aparelho):', st, '· MB-01:', card.replace('\n', ' | ')[:420])
    chk('X8 área toda feita no aparelho (140 de 140 ha) e custódia 0: MB-01 não pede mais produto (falta 0 L), não 70 L', fm.get('Fungicida A') == D(0), (st, fm))

    # ================= A9 · 390 px com toque: app de campo e MB-02det =================
    c.aparelho(390, 844, 2, True); ir('Main.dc.html', t=.3); J("localStorage.clear(); 1")
    ir('MB-01.dc.html', t=1.0); mudar("cenEntregar(c,'REQ-039','Fungicida A',65,'Marcos','Rui'); return cenConfirmarRecebimento(c,'REQ-039');")
    res = {}
    for pg, oid in (('OS-0424-app.dc.html', None), ('MB-02det.dc.html', 'OS-0421'), ('MB-02det.dc.html', 'OS-0424')):
        if oid: J(f"localStorage.setItem('talhao-os-mb-os','{oid}')")
        ir(pg, t=1.3); sx = J(SCROLL_X); m = J(MEDE); res[(pg, oid)] = (sx, resumo(m))
    print('     390:', {k[0] + (k[1] or ''): v for k, v in res.items()})
    chk('A9a 390 px: app OS-0424 e MB-02det (OS-0421, OS-0424) sem rolagem horizontal e sem item cortado',
        all(v[0]['doc'] <= v[0]['w'] + 1 and v[0]['body'] <= v[0]['w'] + 1 and not v[0]['fora'] and not v[1] for v in res.values()), res)
    ir('OS-0424-app.dc.html', t=1.3); bb = alvo_txt('Carga 1 preparada')
    if bb: c.toque(bb['x'], bb['y']); time.sleep(.6)
    tt = body(); bb2 = alvo_txt('Carga 2 preparada')
    chk('A9b toque em "Carga 1 preparada" marca 1 de 5; alvo ≥ 44 × 44 px', bool(bb) and bb['h'] >= 44 and bb['w'] >= 44 and '1 de 5 cargas preparadas' in tt and bool(bb2), (bb, tt[tt.find('cargas prep') - 10:][:40]))
    J("localStorage.setItem('talhao-os-mb-os','OS-0424')"); ir('MB-02det.dc.html', t=1.3)
    lk = alvo_txt('Abrir ficha do caldeiro'); ft = J("(()=>{const b=[...document.querySelectorAll('a,button')].filter(e=>e.offsetParent!==null&&/font-size: 17px/.test(e.getAttribute('style')||'')); return b.map(e=>{const r=e.getBoundingClientRect(); return [e.innerText.trim(),Math.round(r.width),Math.round(r.height)];});})()")
    if lk: c.toque(lk['x'], lk['y']); time.sleep(1.2)
    href = J("location.pathname")
    chk('A9c MB-02det OS-0424: toque em "Abrir ficha do caldeiro" (≥ 44 px) abre o app da OS-0424; ação do rodapé ≥ 44 px', bool(lk) and lk['h'] >= 44 and href.endswith('OS-0424-app.dc.html') and all(x[2] >= 44 for x in (ft or [])), (lk, href, ft))
    c.aparelho(1440, 900)
    chk('A10 sem erro de JavaScript nas telas visitadas', not erros(), erros())
finally:
    try: c.close()
    finally:
        srv.terminate(); shutil.rmtree(RAIZ, ignore_errors=True)
print('     foco:', FOCO)
print(f'RESULTADO: {len(OK)}/{len(OK) + len(FAIL)}' + (' · FALHAS: ' + '; '.join(x.split(' ')[0] for x in FAIL) if FAIL else ''))
