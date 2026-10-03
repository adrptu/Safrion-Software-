# -*- coding: utf-8 -*-
"""Helpers do verificador independente (Compras/Estoque). Só leitura do protótipo: serve _render e dirige o Chrome headless."""
import sys, os, time, subprocess, json
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from cdp import Chrome
from journeys import free
R=os.path.join(os.path.dirname(os.path.abspath(__file__)),'_render')
OUT='/private/tmp/claude-501/-Users-adrianussanders-Library-Application-Support-Claude-scratch-workspaces-3f2449ee-7729-4f0a-96cc-d0f539bf7a66-57b91317-014d-44f0-ad90-4438cd376723-scratch-2026-09-22-5d85a9/ed477ec7-a5fd-431d-bc5d-c0e06c6234e4/scratchpad/v38/verif_shots'
os.makedirs(OUT,exist_ok=True)
CLK="""((t,root)=>{const r=root?document.querySelector(root):document; if(!r) return 'SEM RAIZ'; const n=s=>(s||'').replace(/\\s+/g,' ').trim(); const els=[...r.querySelectorAll('button,a')]; const e=els.find(x=>n(x.innerText)===t)||els.find(x=>n(x.innerText).startsWith(t)); if(!e) return 'NÃO ACHEI: '+t; e.click(); return 'ok';})"""
SETV="""((sel,val)=>{const i=document.querySelector(sel); if(!i) return 'sem campo '+sel; const P=i.tagName==='SELECT'?HTMLSelectElement.prototype:(i.tagName==='TEXTAREA'?HTMLTextAreaElement.prototype:HTMLInputElement.prototype); Object.getOwnPropertyDescriptor(P,'value').set.call(i,val); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true})); return 'ok';})"""
ROWCLK="""((t)=>{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.replace(/\\s+/g,' ').indexOf(t)>=0); if(!r) return 'sem linha '+t; const s=r.querySelector('[role=cell] b')||r.querySelector('[role=cell] span'); s.click(); return 'ok';})"""
KID="""((g,t,click)=>{const rows=[...document.querySelectorAll('[role=row].g2r')]; const i=rows.findIndex(r=>!r.classList.contains('g2kid')&&r.innerText.replace(/\\s+/g,' ').replace(/^[\\s▾▸]+/,'').startsWith(g)); if(i<0) return 'sem grupo '+g;
  for(let k=i+1;k<rows.length&&rows[k].classList.contains('g2kid');k++){ const x=rows[k]; if(x.innerText.replace(/\\s+/g,' ').indexOf(t)>=0){ if(click){ (x.querySelector('[role=cell] b')||x.querySelector('[role=cell] span')).click(); return 'ok'; } return x.innerText.replace(/\\s+/g,' '); } } return 'sem linha '+t;})"""
class V:
    def __init__(s,page):
        s.p=free(); s.srv=subprocess.Popen(['python3','-m','http.server',str(s.p),'--bind','127.0.0.1','--directory',R],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(0.8)
        s.c=Chrome(port=free()); s.c.size(1440,1000); s.page=page; s.FAL=[]; s.OKN=0
    def open(s): s.c.goto(f'http://127.0.0.1:{s.p}/{s.page}'); time.sleep(.6)
    def J(s,x): return s.c.js(x)
    def chk(s,nome,cond,extra=''):
        print(('OK   ' if cond else 'FALHA')+' · '+nome+((' · '+str(extra)[:400]) if (extra!='' ) else ''),flush=True)
        if not cond: s.FAL.append(nome)
        else: s.OKN+=1
    def T(s): return s.J("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).filter(Boolean).join(' | ')")
    def clk(s,t,root=None,w=.45): r=s.J(f"({CLK})({json.dumps(t)},{json.dumps(root)})"); time.sleep(w); return r
    def setv(s,sel,val): r=s.J(f"({SETV})({json.dumps(sel)},{json.dumps(val)})"); time.sleep(.25); return r
    def row(s,t): r=s.J(f"({ROWCLK})({json.dumps(t)})"); time.sleep(.4); return r
    def kid(s,g,t,click=False): r=s.J(f"({KID})({json.dumps(g)},{json.dumps(t)},{json.dumps(click)})"); time.sleep(.4 if click else 0); return r
    def rowtxt(s,t): return s.J(f"(()=>{{const r=[...document.querySelectorAll('[role=row]')].find(r=>r.innerText.replace(/\\s+/g,' ').indexOf({json.dumps(t)})>=0); return r?r.innerText.replace(/\\s+/g,' '):'sem linha';}})()")
    def after(s,t,u): return s.J(f"(()=>{{const rows=[...document.querySelectorAll('[role=row]')]; const i=rows.findIndex(r=>r.innerText.replace(/\\s+/g,' ').indexOf({json.dumps(t)})>=0); const k=rows.slice(i+1).find(r=>r.innerText.indexOf({json.dumps(u)})>=0); return k?k.innerText.replace(/\\s+/g,' '):'sem linha';}})()")
    def opts(s,k): return s.J(f"[...document.querySelectorAll('[id$=_{k}] option')].map(o=>o.value)")
    def sub(s): return s.J("(()=>{const a=document.querySelector('aside[role=dialog]'); if(!a) return ''; const d=a.querySelector('h2').parentElement.nextElementSibling; return d?d.innerText:'';})()")
    def body(s): return s.J("document.body.innerText")
    def cur(s): return s.J("(document.querySelector('[aria-current=step]')||{innerText:''}).innerText.replace(/\\s+/g,' ')")
    def aside(s): return s.J("(document.querySelector('aside[role=dialog]')||{innerText:''}).innerText")
    def errs(s): return s.J("[...document.querySelectorAll('aside[role=dialog] [role=alert]')].map(x=>x.innerText).join(' | ')")
    def fid(s,k): return s.J(f"(document.querySelector('aside [id$=_{k}]')||{{id:''}}).id")
    def prim(s): return s.J("[...document.querySelectorAll('button,a')].filter(b=>getComputedStyle(b).backgroundColor==='rgb(30, 122, 76)'&&b.offsetParent&&!b.closest('aside')).map(b=>b.innerText.trim()).filter(Boolean).join(' | ')")
    def typ(s,sel,text):
        s.J(f"document.querySelector({json.dumps(sel)}).focus()"); time.sleep(.1)
        for ch in text: s.c.call('Input.insertText',{'text':ch}); time.sleep(.03)
        time.sleep(.3)
    def shot(s,nome):
        s.c.shot(os.path.join(OUT,nome))
    def close(s):
        try: s.c.close()
        except Exception: pass
        s.srv.terminate()
        print(f'\nOK {s.OKN} · FALHAS: {s.FAL if s.FAL else "nenhuma"}')
