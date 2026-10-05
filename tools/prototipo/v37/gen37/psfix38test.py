# -*- coding: utf-8 -*-
"""Teste real (Chrome) · Planejar safra, correções pedidas pelo verificador (26/09):
A · ordenar por data ('1º uso' da etapa 6 e 'Plantio' da etapa 2) segue o calendário, não o dia do mês;
C · a composição do custo por hora fecha com o total (centavos) e 'Pessoas na equipe' só aceita inteiro;
D · custo de máquina de 4 dígitos continua numa linha só, com o total alinhado e a tabela dentro do quadro;
E · na safrinha, o custo por kg por cultura é encontrado pela busca e o filtro oferece o texto visível."""
import sys, os, time, subprocess, json, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cdp import Chrome
from journeys import free
HERE = os.path.dirname(os.path.abspath(__file__)); R = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '_render')
p = free(); srv = subprocess.Popen(['python3', '-m', 'http.server', str(p), '--bind', '127.0.0.1', '--directory', R], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)
c = Chrome(port=free()); J = c.js
OK = []; FAIL = []
def chk(nome, cond, det=''):
    (OK if cond else FAIL).append(nome); print(('  ok  ' if cond else '  FALHOU ') + nome + (' · ' + str(det) if det != '' else ''))
CLK = """((t,root)=>{const r=root?document.querySelector(root):document; if(!r) return 'SEM RAIZ'; const n=s=>(s||'').replace(/\\s+/g,' ').trim(); const els=[...r.querySelectorAll('button,a')]; const e=els.find(x=>n(x.innerText)===t)||els.find(x=>n(x.innerText).startsWith(t)); if(!e) return 'NÃO ACHEI: '+t; e.click(); return 'ok';})"""
def clk(t, root=None): r = J(f"({CLK})({json.dumps(t)},{json.dumps(root)})"); time.sleep(.45); return r
from comp_lib import IR_ETAPA
def etapa(i): r = J(f"({IR_ETAPA})({i})"); time.sleep(.55); return r   # a faixa só informa (UX-ACAO-UNICA-20261003): anda pela área de ações
def abrir(nome):
    etapa(1); J(f"""(()=>{{const r=[...document.querySelectorAll('[role=row]')].find(x=>x.innerText.indexOf({json.dumps(nome)})>=0); [...r.querySelectorAll('button')].find(b=>/safra|^Continuar/.test(b.innerText.trim())).click();}})()"""); time.sleep(.55); etapa(2)
def panel(): return J("(()=>{const a=document.querySelector('aside[role=dialog]'); return a?a.innerText.replace(/\\s+/g,' '):'';})()") or ''
def row(txt): return J(f"(()=>{{const r=[...document.querySelectorAll('[role=table]')].filter(t=>t.offsetParent).flatMap(t=>[...t.querySelectorAll('[role=row]')]).find(r=>r.innerText.indexOf({json.dumps(txt)})>=0); return r?r.innerText.replace(/\\s+/g,' ').trim().replace(/^[▾▸] /,''):'';}})()") or ''
def rowclick(txt): J(f"(()=>{{const r=[...document.querySelectorAll('[role=row].g2ed')].filter(x=>x.offsetParent).find(r=>r.innerText.indexOf({json.dumps(txt)})>=0); (r.querySelector('[role=cell] span')||r).click();}})()"); time.sleep(.45)
def fset(label, val):
    r = J(f"""(()=>{{const a=document.querySelector('aside[role=dialog]'); const l=[...a.querySelectorAll('label')].find(l=>l.innerText.trim()==={json.dumps(label)}); if(!l) return 'sem'; const i=document.getElementById(l.getAttribute('for')); const pr=i.tagName==='SELECT'?HTMLSelectElement.prototype:HTMLInputElement.prototype; Object.getOwnPropertyDescriptor(pr,'value').set.call(i,{json.dumps(val)}); i.dispatchEvent(new Event(i.tagName==='SELECT'?'change':'input',{{bubbles:true}})); return 'ok';}})()""")
    time.sleep(.25); return r
def editar(conj, campos):
    rowclick(conj)
    for k, v in campos: fset(k, v)
    clk('Salvar', 'aside[role=dialog]')
def sortby(col): J(f"document.querySelector('main button[aria-label=\"Ordenar por {col}\"]').click()"); time.sleep(.5)
def busca(q): J(f"(()=>{{const i=[...document.querySelectorAll('main input[aria-label=\"Buscar nesta tabela\"]')].find(x=>x.offsetParent); Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(i,{json.dumps(q)}); i.dispatchEvent(new Event('input',{{bubbles:true}})); i.dispatchEvent(new Event('change',{{bubbles:true}}));}})()"); time.sleep(.45)
ROWS = "[...[...document.querySelectorAll('[role=table]')].find(t=>t.offsetParent).querySelectorAll('[role=row]')].slice(1).map(r=>({t:r.innerText.replace(/\\s+/g,' ').trim().replace(/^[▾▸] /,''),kid:r.classList.contains('g2kid')}))"
LARG = r"""(()=>{const t=[...document.querySelectorAll('[role=table]')].find(t=>t.offsetParent); const box=t.parentElement; return {box:box.clientWidth, scroll:box.scrollWidth, tab:Math.round(t.getBoundingClientRect().width)};})()"""
CUSTOH = r"""(()=>{const t=[...document.querySelectorAll('[role=table]')].find(t=>t.offsetParent); const hs=[...t.querySelectorAll('[role=columnheader]')].map(h=>h.innerText.replace(/\s+/g,' ').trim());
  const ci=hs.findIndex(h=>/^CUSTO R\$\/H/i.test(h)); return [...t.querySelectorAll('[role=row].g2kid')].map(r=>{ const cell=r.querySelectorAll('[role=cell]')[ci]; const cr=cell.getBoundingClientRect();
    const sp=[...cell.querySelectorAll('.g2pw span')].filter(s=>s.children.length===0&&s.innerText.trim()); const mids=new Set(sp.map(s=>Math.round(s.getBoundingClientRect().top+s.getBoundingClientRect().height/2)));
    return {nome:r.innerText.split('\n')[0], t:sp.map(s=>s.innerText).join(' | '), linhas:mids.size, esq:Math.round(Math.min(...sp.map(s=>s.getBoundingClientRect().left))-cr.left), dir:Math.round(sp[sp.length-1].getBoundingClientRect().right)}; });})()"""
num = lambda s: float(s.replace('.', '').replace(',', '.'))
def fecha(t):
    m = re.match(r'máq\. ([\d.,]+) · impl\. ([\d.,]+) · (\d+) × ([\d.,]+) = \| ([\d.,]+)$', t)
    return bool(m) and abs(num(m[1]) + num(m[2]) + int(m[3]) * num(m[4]) - num(m[5])) < 0.005
def data1(x):
    x = x['t'] if isinstance(x, dict) else x
    m = re.search(r'(\d{2})/(\d{2}) a \d{2}/\d{2}/(\d{4})', x)  # faixa do grupo: 15/10 a 25/10/2026 → começa em 15/10/2026
    if m: return (m[3], m[2], m[1])
    m = re.search(r'(\d{2})/(\d{2})/(\d{4})', x); return (m[3], m[2], m[1]) if m else None
def datas(lst): return [data1(x) for x in lst]
try:
    c.size(1440, 1000); c.goto(f'http://127.0.0.1:{p}/SAF.dc.html', wait=1.3)
    J("window.__errs=[]; window.addEventListener('error',e=>window.__errs.push(String(e.message)));")
    abrir('Safra 2026/27')
    # ---------- A · etapa 6: ordenar por 1º uso ----------
    etapa(6); clk('Expandir tudo'); sortby('1º uso')
    rs = J(ROWS); grupos = [x['t'] for x in rs if not x['kid'] and not x['t'].startswith('Total')]
    dg = datas(grupos)
    chk('A · grupos em ordem de calendário (crescente)', dg == sorted(dg) and grupos[0].startswith(('Adjuvantes', 'Herbicidas')) and grupos[1].startswith(('Adjuvantes', 'Herbicidas')), [g.split(' ')[0] + ' ' + re.search(r'\d{2}/\d{2}/\d{4}', g)[0] for g in grupos])
    blocos = []; cur = None
    for x in rs:
        if x['t'].startswith('Total'): continue
        if not x['kid']: cur = []; blocos.append(cur)
        else: cur.append(x['t'])
    chk('A · insumos em ordem de calendário dentro de cada grupo', all(datas(b) == sorted(datas(b)) for b in blocos), [[y[:20] for y in b] for b in blocos if datas(b) != sorted(datas(b))])
    ordem = [x['t'].split(' ')[0] for x in rs if x['kid']]
    fa, fc = [i for i, x in enumerate(rs) if x['t'].startswith('Fungicida A')][0], [i for i, x in enumerate(rs) if x['t'].startswith('Fungicida C')][0]
    chk('A · Fungicida A (29/11/2026) antes de Fungicida C (20/01/2027)', fa < fc)
    ix = lambda s: [i for i, x in enumerate(rs) if x['t'].startswith(s)][0]
    chk('A · MAP e NPK (15/10) antes de Nitrato de potássio (01/11) e KCl (04/11)', max(ix('MAP'), ix('NPK')) < min(ix('Nitrato de potássio'), ix('KCl')))
    sortby('1º uso'); rs = J(ROWS); dg = datas([x['t'] for x in rs if not x['kid'] and not x['t'].startswith('Total')])
    chk('A · decrescente: grupos da data mais tardia para a mais cedo', dg == sorted(dg, reverse=True), dg[:3])
    sortby('1º uso')
    busca('20/01/2027'); chk('A · busca pela data exibida encontra o insumo', any(x['t'].startswith('Fungicida C') for x in J(ROWS)), [x['t'][:30] for x in J(ROWS)])
    busca('')
    J("document.querySelector('main button[aria-label=\"Filtrar 1º uso\"]').click()"); time.sleep(.4)
    fv = J("[...document.querySelectorAll('main label')].filter(l=>l.querySelector('input[type=checkbox]')).map(l=>l.innerText.replace(/\\s+/g,' ').trim())")
    chk('A · filtro de 1º uso oferece as datas como aparecem (dd/mm/aaaa)', len(fv) > 3 and all(re.match(r'\d{2}/\d{2}/\d{4} \d+$', v) for v in fv), fv[:4])
    clk('Fechar', 'main')
    # ---------- A · etapa 2: ordenar por Plantio ----------
    etapa(2); sortby('Plantio')
    rs = [x for x in J(ROWS) if not x['kid'] and not x['t'].startswith('Total')]
    dp = datas(rs); chk('A · etapa 2: talhões por data de plantio (2019, 2025, 2026 …)', dp == sorted(dp) and rs[0]['t'].startswith('C1'), [x['t'].split(' ')[0] for x in rs])
    sortby('Plantio'); sortby('Plantio')
    # ---------- C · composição fecha com o total ----------
    etapa(3)
    ch = J(CUSTOH); chk('C · padrão: composição de todos os conjuntos soma o total', len(ch) == 8 and all(fecha(x['t']) for x in ch), [x['t'] for x in ch if not fecha(x['t'])])
    editar('Trator 02 MF 7719', [('Custo por pessoa', '38,5')])
    r = [x for x in J(CUSTOH) if x['nome'].startswith('Trator 02')][0]
    chk('C · custo por pessoa 38,5 → "máq. 180 · impl. 95 · 1 × 38,50 = 313,50"', r['t'] == 'máq. 180 · impl. 95 · 1 × 38,50 = | 313,50', r['t'])
    editar('Trator 03 + Distribuidor', [('Máquina', '150,6')])
    r = [x for x in J(CUSTOH) if x['nome'].startswith('Trator 03')][0]
    chk('C · máquina 150,6 → "máq. 150,60 · impl. 45 · 1 × 38 = 233,60"', r['t'] == 'máq. 150,60 · impl. 45 · 1 × 38 = | 233,60', r['t'])
    editar('Máquina TSI', [('Custo por pessoa', '38,333')])
    r = [x for x in J(CUSTOH) if x['nome'].startswith('Máquina TSI')][0]
    chk('C · custo com 3 casas é gravado em centavos e a conta fecha', fecha(r['t']) and '2 × 38,33 = | 136,66' in r['t'], r['t'])
    rowclick('Trator T1 JD 6M 155'); fset('Pessoas na equipe', '2,5'); clk('Salvar', 'aside[role=dialog]'); pt = panel()
    chk('C · 2,5 pessoas é recusado junto ao campo: "Use um número inteiro de pessoas."', 'Use um número inteiro de pessoas.' in pt, pt[:200])
    clk('Cancelar', 'aside[role=dialog]'); clk('Descartar alterações', 'aside[role=dialog]')
    chk('C · Plantio continua com 2 pessoas', '2 × 38 = 396,00' in row('Trator T1 JD 6M 155'), row('Trator T1 JD 6M 155'))
    # ---------- D · 4 dígitos numa linha só ----------
    editar('Colhedora', [('Máquina', '1050')])
    ch = J(CUSTOH); r = [x for x in ch if x['nome'].startswith('Colhedora')][0]
    chk('D · colhedora com máquina 1.050: composição e total numa linha', r['linhas'] == 1 and r['t'] == 'máq. 1.050 · impl. 120 · 2 × 38 = | 1.246,00', r)
    chk('D · totais de custo por hora alinhados à direita', len(set(x['dir'] for x in ch)) == 1, sorted(set(x['dir'] for x in ch)))
    chk('D · composição não invade a coluna vizinha', all(x['esq'] >= 0 for x in ch), [x['esq'] for x in ch])
    w = J(LARG); chk('D · tabela cabe no quadro a 1440 px', w['tab'] <= 1116 and w['scroll'] <= w['box'], w)
    editar('Colhedora', [('Máquina', '1200,5'), ('Custo por pessoa', '38,5')])
    ch = J(CUSTOH); r = [x for x in ch if x['nome'].startswith('Colhedora')][0]
    chk('D · máquina 1.200,50 e pessoa 38,50: ainda numa linha e a conta fecha', r['linhas'] == 1 and fecha(r['t']) and r['t'] == 'máq. 1.200,50 · impl. 120 · 2 × 38,50 = | 1.397,50', r)
    chk('D · totais continuam alinhados', len(set(x['dir'] for x in ch)) == 1, sorted(set(x['dir'] for x in ch)))
    w = J(LARG); chk('D · tabela continua dentro do quadro', w['tab'] <= 1116 and w['scroll'] <= w['box'], w)
    c.shot(os.path.join(HERE, '_probe', 'psfix38_e3.png'))
    # ---------- E · safrinha: custo por kg por cultura ----------
    abrir('Safrinha 2027'); etapa(3)
    r = row('Colhedora'); chk('E · célula mostra "por cultura" e o valor de cada cultura', r.endswith('por cultura Milho 0,0216 Feijão 0,0764'), r)
    cor = J("""(()=>{const r=[...document.querySelectorAll('[role=row]')].filter(x=>x.offsetParent).find(r=>r.innerText.indexOf('Colhedora')>=0); const cs=r.querySelectorAll('[role=cell]'); const c=cs[cs.length-1];
      const f=t=>[...c.querySelectorAll('span')].find(s=>s.children.length===0&&s.innerText.trim()===t); return [getComputedStyle(f('por cultura')).color, getComputedStyle(f('Milho 0,0216')).color, getComputedStyle(f('Feijão 0,0764')).color];})()""")
    chk('E · valores por cultura esmaecidos, rótulo em texto normal', cor[1] == cor[2] != cor[0], cor)
    for q in ['Milho', 'Feijão', 'por cultura']:
        busca(q); rs = J(ROWS); chk(f'E · busca "{q}" encontra a Colheita de grãos', any(x['t'].startswith('Colhedora') for x in rs), [x['t'][:30] for x in rs])
    busca('')
    J("document.querySelector('main button[aria-label=\"Filtrar Custo R$/kg\"]').click()"); time.sleep(.4)
    fv = J("[...document.querySelectorAll('main label')].filter(l=>l.querySelector('input[type=checkbox]')).map(l=>l.innerText.replace(/\\s+/g,' ').trim())")
    chk('E · filtro oferece o texto visível (por cultura · Milho … · Feijão …)', 'por cultura · Milho 0,0216 · Feijão 0,0764 1' in fv and 'por cultura 1' not in fv, fv)
    clk('Fechar', 'main')
    w = J(LARG); chk('E · Safrinha: tabela cabe no quadro', w['tab'] <= 1116 and w['scroll'] <= w['box'], w)
    chk('sem erro de JS', not J("window.__errs.length"), J("window.__errs"))
finally:
    c.close(); srv.terminate()
print(f'\nRESULTADO: {len(OK)} ok · {len(FAIL)} falhas'); [print('  -', f) for f in FAIL]
