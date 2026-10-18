# -*- coding: utf-8 -*-
"""INTEL-03 F1 · bloco "Mercado e momento" na Inteligência de vendas (IV) e de compras (IC), no Chrome a 1440 × 900 e 390 × 844 (toque).
  A1 trocar 12/24/36/48 meses muda o gráfico, o percentil, o índice e o acerto; o N de anos aparece
  A5 12 meses nunca mostra selo de decisão
  A7 gráfico com rótulos; nada vaza a 390 px; produto e período com um toque; dica ⓘ com a regra; sem erro de JavaScript
  A8 a tela lê e não grava (armazenamento igual antes e depois)
Contraprova: o render da v132 reprova A1 (o bloco não existe).
Uso (de gen37/): env CHROME_BIN=… SAFRION_DADOS=sintetico [RENDER_DIR=…] python3 -B intel03_nav_test.py"""
import os, sys, json, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, servir

R = os.environ.get('RENDER_DIR') or os.path.join(HERE, '_render')
OK = FAIL = 0
def chk(nome, cond, info=''):
    global OK, FAIL
    if cond: OK += 1; print('OK   ', nome)
    else: FAIL += 1; print('FALHA', nome, '·', str(info)[:500])

port, srv = servir(R); c = Chrome(); J = c.js
LE = r"""JSON.stringify((()=>{const b=document.querySelector('.i3'); if(!b) return null; const q=s=>(b.querySelector(s)||{}).innerText||'';
  return {agora:q('.i3-agora'), selo:q('.i3-selo'), l1:q('.i3-l1'), l2:q('.i3-l2'), pts:(b.querySelector('polyline')||{getAttribute:()=>''}).getAttribute('points')||'',
   n:((b.querySelector('.i3-saz figcaption')||{}).innerText||''), barras:b.querySelectorAll('.i3-saz [role=listitem]').length,
   per:[...b.querySelectorAll('[role=group][aria-label="Período"] button')].map(x=>[x.innerText.trim(),x.getAttribute('aria-pressed')]),
   dica:(b.querySelector('.g2dica-i')||{getAttribute:()=>''}).getAttribute('data-dica')||''};})())"""
def le(): return json.loads(J(LE) or 'null')
def periodo(t):
    J("(()=>{const b=[...document.querySelectorAll('.i3 [role=group][aria-label=\"Período\"] button')].find(x=>x.innerText.trim()==='%s'); b&&b.click();})()" % t); time.sleep(.6)
try:
    for W, Hh, toque in ((1440, 900, False), (390, 844, True)):
        c.aparelho(W, Hh, toque=toque)
        for pg, lado in (('IV.dc.html', 'vender'), ('IC.dc.html', 'comprar')):
            c.goto(f'http://127.0.0.1:{port}/Main.dc.html', .3); J("localStorage.clear()")
            c.goto(f'http://127.0.0.1:{port}/{pg}', 1.4); J("window.__errs=window.__errs||[]")
            ls0 = J("JSON.stringify(Object.keys(localStorage).sort().map(k=>[k,localStorage.getItem(k)]))")
            r36 = le()
            chk(f'A1a {W} {pg}: o bloco abre em 36 meses, com preço de agora, percentil, melhor mês, gráfico e 12 barras',
                bool(r36) and r36['agora'].startswith('R$') and 'Percentil' in r36['l1'] and '36 meses' in r36['l1'] and len(r36['pts'].split()) == 36 and r36['barras'] == 12 and '3 anos' in r36['n']
                and ['36 meses', 'true'] in r36['per'], r36)
            res = {}
            for t in ('12 meses', '24 meses', '48 meses'):
                periodo(t); res[t] = le()
            n_ok = all(res[t] and len(res[t]['pts'].split()) == int(t.split()[0]) and (t.split()[0] + ' meses') in res[t]['l1'] for t in res)
            anos = [res['12 meses']['n'], res['24 meses']['n'], res['48 meses']['n']]
            chk(f'A1b {W} {pg}: 12, 24 e 48 meses mudam o gráfico (pontos = meses), o percentil e o N de anos (1, 2, 4)', n_ok and '1 ano' in anos[0] and '2 anos' in anos[1] and '4 anos' in anos[2]
                and len({res[t]['l1'] for t in res} | {r36['l1']}) >= 2, [anos, [res[t]['l1'] for t in res]])
            chk(f'A5 {W} {pg}: 12 meses não mostra selo e diz que um ano é exemplo, não padrão', res['12 meses']['selo'] == '' and 'não padrão' in res['12 meses']['l2'], res['12 meses'])
            chk(f'A1c {W} {pg}: com 48 meses, a leitura diz o melhor mês para {lado}, o acerto em N anos e a força da evidência (ou "Sem padrão")',
                ('Melhor mês para ' + lado in res['48 meses']['l2'] and 'acerto' in res['48 meses']['l2'] and 'de 4 anos' in res['48 meses']['l2']) or 'Sem padrão' in res['48 meses']['l2'], res['48 meses']['l2'])
            chk(f'A7a {W} {pg}: a dica ⓘ traz a regra do percentil, do selo e da evidência', 'Percentil' in r36['dica'] and 'Evidência' in r36['dica'] and 'não é previsão' in r36['dica'], r36['dica'][:200])
            d = json.loads(J("""JSON.stringify({sw:document.documentElement.scrollWidth, vw:innerWidth, vaza:[...document.querySelectorAll('.i3 *')].filter(e=>{const r=e.getBoundingClientRect(); const m=document.querySelector('.i3').getBoundingClientRect(); return r.width>0&&r.right>m.right+1;}).length,
              alvos:[...document.querySelectorAll('.i3 button')].filter(b=>b.getBoundingClientRect().height>0).every(b=>b.getBoundingClientRect().height>=36)})""") or '{}')
            chk(f'A7b {W} {pg}: nada vaza (página nem bloco) e os toques de produto e período têm 36 px ou mais', d.get('sw', 9e9) <= d.get('vw', 0) and d.get('vaza') == 0 and d.get('alvos'), d)
            if pg == 'IC.dc.html':
                ops = J("[...document.querySelectorAll('.i3 select[aria-label=Insumo] option')].map(o=>o.value)") or []
                if len(ops) > 1:
                    J("(()=>{const s=document.querySelector('.i3 select[aria-label=Insumo]'); s.value=%s; s.dispatchEvent(new Event('change',{bubbles:true}));})()" % json.dumps(ops[1])); time.sleep(.6)
                    r2 = le()
                    chk(f'A7c {W} IC: o catálogo de insumos é uma lista de escolha e trocar o insumo muda a leitura', r2 and r2['pts'] != res['48 meses']['pts'], [ops[:3], r2 and r2['agora']])
            else:
                bs = J("[...document.querySelectorAll('.i3 [role=group][aria-label=Produto] button')].map(b=>b.innerText.trim())") or []
                if len(bs) > 1:
                    J("(()=>{const b=[...document.querySelectorAll('.i3 [role=group][aria-label=Produto] button')][1]; b.click();})()"); time.sleep(.6)
                    r2 = le()
                    chk(f'A7c {W} IV: a lista curta de produtos é um toque e trocar o produto muda a leitura', r2 and r2['pts'] != res['48 meses']['pts'], [bs, r2 and r2['agora']])
            ls1 = J("JSON.stringify(Object.keys(localStorage).sort().map(k=>[k,localStorage.getItem(k)]))")
            chk(f'A8 {W} {pg}: o bloco lê e não grava (armazenamento igual antes e depois)', ls0 == ls1, [ls0[:120], ls1[:120]])
            ee = J("window.__errs||[]") or []
            chk(f'A7d {W} {pg}: sem erro de JavaScript', not ee, ee[:3])
            if W == 1440 and os.environ.get('I3_SHOTS'):
                periodo('36 meses'); c.shot(os.path.join(os.environ['I3_SHOTS'], f'intel03_{pg[:2]}_{W}.png'))
finally:
    c.close(); srv.terminate()
print(f'RESULTADO: {OK} ok · {FAIL} falhas')
sys.exit(1 if FAIL else 0)
