# -*- coding: utf-8 -*-
"""Verificação independente (Chrome) · planos-safra-01..06: casos-limite que o saf38test não cobre."""
import sys, os, time, subprocess, json, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cdp import Chrome
from journeys import free
HERE = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(HERE, '_render')
SHOT = sys.argv[1] if len(sys.argv) > 1 else HERE
p = free(); srv = subprocess.Popen(['python3', '-m', 'http.server', str(p), '--bind', '127.0.0.1', '--directory', R], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)
c = Chrome(port=free()); J = c.js
def say(*a): print(*a, flush=True)
CLK = """((t,root)=>{const r=root?document.querySelector(root):document; if(!r) return 'SEM RAIZ'; const n=s=>(s||'').replace(/\\s+/g,' ').trim(); const els=[...r.querySelectorAll('button,a')]; const e=els.find(x=>n(x.innerText)===t)||els.find(x=>n(x.innerText).startsWith(t)); if(!e) return 'NÃO ACHEI: '+t; e.click(); return 'ok';})"""
def clk(t, root=None): r = J(f"({CLK})({json.dumps(t)},{json.dumps(root)})"); time.sleep(.45); return r
def toast(): return J("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).filter(Boolean).join(' | ')") or ''
def panel(): return J("(()=>{const a=document.querySelector('aside[role=dialog]'); return a?a.innerText.replace(/\\s+/g,' '):'';})()") or ''
def etapa(i): J(f"document.querySelectorAll('nav[aria-label=\"Etapas do processo\"] button')[{i-1}].click()"); time.sleep(.55)
def abrir(nome):
    etapa(1); r = J(f"""(()=>{{const r=[...document.querySelectorAll('[role=row]')].find(x=>x.innerText.indexOf({json.dumps(nome)})>=0); if(!r) return 'sem linha'; const b=[...r.querySelectorAll('button')].find(b=>/safra/.test(b.innerText)); b.click(); return 'ok';}})()""")
    time.sleep(.55); return r
def row(txt, ti=0): return J(f"(()=>{{const r=[...document.querySelectorAll('[role=table]')].filter(t=>t.offsetParent)[{ti}].querySelectorAll('[role=row]'); const x=[...r].find(r=>r.innerText.indexOf({json.dumps(txt)})>=0); return x?x.innerText.replace(/\\s+/g,' ').trim().replace(/^[▾▸] /,''):'';}})()") or ''
def rowclick(txt):
    r = J(f"(()=>{{const r=[...document.querySelectorAll('[role=row].g2ed')].filter(x=>x.offsetParent).find(r=>r.innerText.indexOf({json.dumps(txt)})>=0); if(!r) return 'sem linha'; (r.querySelector('[role=cell] span')||r).click(); return 'ok';}})()"); time.sleep(.45); return r
def fset(label, val):
    r = J(f"""(()=>{{const a=document.querySelector('aside[role=dialog]'); const l=[...a.querySelectorAll('label')].find(l=>l.innerText.trim()==={json.dumps(label)}); if(!l) return 'sem '+{json.dumps(label)}; const i=document.getElementById(l.getAttribute('for')); const pr=i.tagName==='SELECT'?HTMLSelectElement.prototype:HTMLInputElement.prototype; Object.getOwnPropertyDescriptor(pr,'value').set.call(i,{json.dumps(val)}); i.dispatchEvent(new Event(i.tagName==='SELECT'?'change':'input',{{bubbles:true}})); return 'ok';}})()""")
    time.sleep(.25); return r
LARG = r"""(()=>{const t=[...document.querySelectorAll('[role=table]')].find(t=>t.offsetParent); const box=t.parentElement; return {box:box.clientWidth, scroll:box.scrollWidth, tab:Math.round(t.getBoundingClientRect().width)};})()"""
CUSTOH = r"""(()=>{const t=[...document.querySelectorAll('[role=table]')].find(t=>t.offsetParent); const hs=[...t.querySelectorAll('[role=columnheader]')].map(h=>h.innerText.replace(/\s+/g,' ').trim());
  const ci=hs.findIndex(h=>/^CUSTO \(R\$\/H\)/i.test(h)); return [...t.querySelectorAll('[role=row].g2kid')].map(r=>{ const cell=r.querySelectorAll('[role=cell]')[ci]; const cr=cell.getBoundingClientRect(); const prev=r.querySelectorAll('[role=cell]')[ci-1].getBoundingClientRect();
    const sp=[...cell.querySelectorAll('.g2pw span')].filter(s=>s.children.length===0&&s.innerText.trim()); const tops=new Set(sp.map(s=>Math.round(s.getBoundingClientRect().top+s.getBoundingClientRect().height/2)));
    return {nome:r.innerText.split('\n')[0].slice(0,30), t:sp.map(s=>s.innerText).join(' | '), linhas:tops.size, esq:Math.round(Math.min(...sp.map(s=>s.getBoundingClientRect().left))-cr.left), cellL:Math.round(cr.left), prevR:Math.round(prev.right), dir:Math.round(sp[sp.length-1].getBoundingClientRect().right)}; });})()"""
def total_oper():
    return J(r"""(()=>{const rs=[...document.querySelectorAll('[role=table]')].filter(t=>t.offsetParent)[1].querySelectorAll('[role=row]'); let on=false;
      for(const r of rs){ const t=r.innerText.replace(/\s+/g,' ').trim(); if(/Operadores e equipe/.test(t)) on=true; else if(on && /^Demanda \(h\)/.test(t)){ const cs=r.querySelectorAll('[role=cell]'); return cs[cs.length-1].innerText.trim(); } } return '';})()""")
num = lambda s: float(str(s).replace('.', '').replace(',', '.').replace('h', '').replace('−', '-').strip() or 'nan')
try:
    c.size(1440, 1000); c.goto(f'http://127.0.0.1:{p}/SAF.dc.html', wait=1.3)
    J("window.__errs=[]; window.addEventListener('error',e=>window.__errs.push(String(e.message)));")
    abrir('Safra 2026/27'); etapa(3)
    say('A0 inicial:', [(x['nome'], x['t'], x['esq']) for x in J(CUSTOH)])
    # A1 · Colhedora com máquina de 1.050 R$/h
    rowclick('Colhedora'); say('A1 painel:', panel()[:100]); fset('Máquina', '1050'); clk('Salvar', 'aside[role=dialog]'); say('A1 toast:', toast())
    ch = J(CUSTOH); say('A1 custo/h:', [(x['nome'], x['t'], 'esq', x['esq'], 'cellL', x['cellL'], 'prevR', x['prevR'], 'linhas', x['linhas']) for x in ch])
    say('A1 largura:', J(LARG))
    c.shot(os.path.join(SHOT, 'verif_a1_maq1050.png'))
    # A2 · custo por pessoa com centavos
    rowclick('Pulverizador'); fset('Custo por pessoa', '38,5'); clk('Salvar', 'aside[role=dialog]'); say('A2 toast:', toast())
    say('A2 linha:', row('Pulverizador'))
    # A2b · máquina com centavos
    rowclick('Distribuidor'); fset('Máquina', '150,6'); clk('Salvar', 'aside[role=dialog]'); say('A2b linha:', row('Distribuidor'))
    # A3 · pessoas 0 no plantio
    etapa(5); o0 = total_oper(); etapa(3)
    rowclick('Plantadeira'); fset('Pessoas na equipe', '0'); clk('Salvar', 'aside[role=dialog]'); say('A3 toast:', toast(), '| linha:', row('Plantadeira'))
    etapa(5); o1 = total_oper(); say('A3 Operadores:', o0, '->', o1, 'diff', round(num(o1) - num(o0), 1))
    # A4 · pessoas decimais
    etapa(3); rowclick('Plantadeira'); fset('Pessoas na equipe', '2,5'); clk('Salvar', 'aside[role=dialog]'); say('A4 toast:', toast(), '| linha:', row('Plantadeira'), '| erro painel:', panel()[:200] if J("!!document.querySelector('aside[role=dialog]')") else '')
    etapa(5); say('A4 Operadores:', total_oper())
    # B · meta do cultivo muda o R$/kg
    etapa(3); say('B0 colhedora:', row('Colhedora'))
    etapa(2); clk('Expandir tudo'); r = rowclick('T1-A'); say('B clique T1-A:', r, panel()[:120])
    fset('Meta de produtividade', '70'); clk('Salvar', 'aside[role=dialog]'); say('B toast:', toast())
    etapa(3); say('B1 colhedora:', row('Colhedora'))
    # B2 · unidade da meta t/ha/ano em cultivo de soja
    etapa(2); rowclick('T2'); say('B2 painel:', panel()[:80]); fset('Unidade da meta', 't/ha/ano'); fset('Meta de produtividade', '4'); clk('Salvar', 'aside[role=dialog]'); say('B2 toast:', toast())
    etapa(3); say('B2 colhedora:', row('Colhedora'))
    # C · ordenação por 1º uso na etapa 6
    etapa(6); clk('Expandir tudo')
    J("""(()=>{const b=[...document.querySelectorAll('[role=table]')].find(t=>t.offsetParent).querySelector('button[aria-label="Ordenar por 1º uso"]'); b.click();})()"""); time.sleep(.5)
    ds = J(r"""(()=>{const t=[...document.querySelectorAll('[role=table]')].find(t=>t.offsetParent); return [...t.querySelectorAll('[role=row]')].map(r=>{const cs=r.querySelectorAll('[role=cell]'); return cs.length>2?(r.classList.contains('g2kid')?'  ':'')+cs[0].innerText.replace(/\s+/g,' ').trim().slice(0,22)+' | '+cs[1].innerText.trim():null;}).filter(Boolean);})()""")
    say('C ordem por 1º uso (asc):'); [say('   ', x) for x in ds]
    c.shot(os.path.join(SHOT, 'verif_c_sort_uso.png'))
    # E · busca na etapa 3 por cultura (Safrinha)
    abrir('Safrinha 2027'); etapa(3)
    J("""(()=>{const i=[...document.querySelectorAll('input[aria-label="Buscar nesta tabela"]')].find(x=>x.offsetParent); const P=HTMLInputElement.prototype; Object.getOwnPropertyDescriptor(P,'value').set.call(i,'Milho'); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true}));})()"""); time.sleep(.5)
    say('E busca Milho linhas:', J("[...[...document.querySelectorAll('[role=table]')].find(t=>t.offsetParent).querySelectorAll('[role=row]')].map(r=>r.innerText.replace(/\\s+/g,' ').slice(0,60))"))
    say('erros JS:', J("window.__errs"))
finally:
    c.close(); srv.terminate()
