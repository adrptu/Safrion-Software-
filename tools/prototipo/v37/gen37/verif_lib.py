# -*- coding: utf-8 -*-
"""Verificação independente (Chrome) · planos-safra-01..06: casos-limite que o saf38test não cobre."""
import sys, os, time, subprocess, json, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cdp import Chrome
from journeys import free
HERE = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(HERE, '_render')
SHOT = sys.argv[1] if len(sys.argv) > 1 else HERE
J = None
c = None
def setup(chrome):
    global J, c
    c = chrome; J = chrome.js
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
