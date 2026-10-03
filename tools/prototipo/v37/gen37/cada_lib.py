# -*- coding: utf-8 -*-
"""Apoio dos testes cada_* (CD-03 e CD-04; cópia de cadc_lib): Chrome headless via CDP, servidor de _render e ações na grade G2.
Erros de JS (window.onerror e console.error) ficam em window.__errs desde o carregamento da página."""
import sys, os, time, subprocess, json
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
from cdp import Chrome
from journeys import free
SETV="""((sel,val)=>{const i=document.querySelector(sel); if(!i) return false; const P=i.tagName==='SELECT'?HTMLSelectElement.prototype:(i.tagName==='TEXTAREA'?HTMLTextAreaElement.prototype:HTMLInputElement.prototype); Object.getOwnPropertyDescriptor(P,'value').set.call(i,val); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true})); return true;})"""
BTN="""((t)=>{const b=[...document.querySelectorAll('aside[role=dialog] button')].find(b=>b.innerText.trim()===t); if(b){b.click(); return true;} return false;})"""
CLK="""((t)=>{const n=s=>(s||'').replace(/\\s+/g,' ').trim(); const els=[...document.querySelectorAll('button,a')]; const e=els.find(x=>n(x.innerText)===t)||els.find(x=>n(x.innerText).startsWith(t)); if(!e) return 'NÃO ACHEI: '+t; e.click(); return 'ok';})"""
ERRS="window.__errs=[];window.addEventListener('error',e=>window.__errs.push(String(e.message)));const __ce=console.error;console.error=function(){window.__errs.push([...arguments].map(String).join(' ').slice(0,300));__ce.apply(console,arguments);};"
class T:
    def __init__(s):
        s.p=free(); s.srv=subprocess.Popen(['python3','-m','http.server',str(s.p),'--bind','127.0.0.1','--directory',os.path.join(HERE,'_render')],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        time.sleep(0.6); s.c=Chrome(port=free()); s.J=s.c.js; s.ok=[]
        s.c.call('Page.addScriptToEvaluateOnNewDocument',{'source':ERRS}); s.c.size(1440,1100)
    def goto(s,f): s.c.goto(f'http://127.0.0.1:{s.p}/{f}',wait=1.2); time.sleep(.3)
    # erro conhecido do motor (engine.py, fora desta frente): o runtime chama componentDidUpdate(prevProps) sem o 2º argumento e
    # ENGINE_JS2 lê ps.g2toast → TypeError a cada aviso (o aviso aparece, só não some sozinho). Fica fora da contagem.
    def errs(s): return s.J("(window.__errs||[]).filter(e=>e.indexOf(\"reading 'g2toast'\")<0).join(' | ')") or ''
    def errs_motor(s): return s.J("(window.__errs||[]).filter(e=>e.indexOf(\"reading 'g2toast'\")>=0).length")
    def chk(s,nome,cond,extra=''):
        s.ok.append(bool(cond)); print(('OK  ' if cond else 'FALHOU ')+nome+(' · '+str(extra)[:300] if extra else ''))
    def ROW(s,ti,txt): return f"[...document.querySelectorAll('[role=table]')[{ti}].querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.replace(/\\s+/g,' ').indexOf({json.dumps(txt)})>=0)"
    def openrow(s,ti,txt): r=s.J(f"(()=>{{const r={s.ROW(ti,txt)}; if(!r) return false; (r.querySelector('.g2pw')||r).click(); return true;}})()"); time.sleep(.35); return r
    def rowtxt(s,ti,txt): return s.J(f"(()=>{{const r={s.ROW(ti,txt)}; return r?r.innerText.replace(/\\s+/g,' '):null;}})()")
    def anyrow(s,ti,txt): return s.J(f"(()=>{{const r=[...document.querySelectorAll('[role=table]')[{ti}].querySelectorAll('[role=row]')].find(r=>r.innerText.replace(/\\s+/g,' ').indexOf({json.dumps(txt)})>=0); return r?r.innerText.replace(/\\s+/g,' '):null;}})()")
    def fv(s,k): return s.J(f"(()=>{{const i=document.querySelector('aside[role=dialog] [id$=\"_{k}\"]'); return i?i.value:null;}})()")
    def fdis(s,k): return s.J(f"(()=>{{const i=document.querySelector('aside[role=dialog] [id$=\"_{k}\"]'); return i?(i.disabled||i.readOnly):null;}})()")
    def fopts(s,k): return s.J(f"(()=>{{const i=document.querySelector('aside[role=dialog] select[id$=\"_{k}\"]'); return i?[...i.options].map(o=>o.value):null;}})()")
    def fset(s,k,val): r=s.J(f"({SETV})('aside[role=dialog] [id$=\"_{k}\"]',{json.dumps(val)})"); time.sleep(.2); return r
    def btn(s,t): r=s.J(f"({BTN})({json.dumps(t)})"); time.sleep(.35); return r
    def clk(s,t): r=s.J(f"({CLK})({json.dumps(t)})"); time.sleep(.35); return r
    def labels(s): return s.J("[...document.querySelectorAll('aside[role=dialog] label[for]')].map(l=>l.innerText.trim())")
    def dlg(s): return s.J("(document.querySelector('aside[role=dialog]')||{}).innerText||''")
    def title(s): return s.J("(document.querySelector('aside[role=dialog] h2')||{}).innerText||''")
    def isopen(s): return s.J("!!document.querySelector('aside[role=dialog]')")
    def alerts(s): return s.J("[...document.querySelectorAll('aside [role=alert]')].map(x=>x.innerText).join(' | ')")
    def toast(s): return s.J("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).filter(Boolean).join(' | ')")
    def header(s): return s.J("document.querySelector('header').innerText.replace(/\\s+/g,' ')")
    # layout de 01/10 (um bloco por tela, abas por entidade, ações no bloco, cartões para fazendas, equipes e conjuntos)
    def bloco(s): return s.J("document.querySelector('main').innerText.replace(/\\s+/g,' ')")
    def aba(s,t): r=s.J(f"(()=>{{const b=[...document.querySelectorAll('[role=tab]')].find(b=>b.innerText.replace(/\\s+/g,' ').trim().startsWith({json.dumps(t)})); if(!b) return false; b.click(); return true;}})()"); time.sleep(.35); return r
    def card(s,t): return s.J(f"(()=>{{const c=[...document.querySelectorAll('.cadx-cartao')].find(c=>c.innerText.replace(/\\s+/g,' ').indexOf({json.dumps(t)})>=0); return c?c.innerText.replace(/\\s+/g,' '):null;}})()")
    def opencard(s,t): r=s.J(f"(()=>{{const c=[...document.querySelectorAll('.cadx-cartao')].find(c=>c.innerText.replace(/\\s+/g,' ').indexOf({json.dumps(t)})>=0); if(!c) return false; c.click(); return true;}})()"); time.sleep(.35); return r
    def mainsel(s,val): r=s.J(f"({SETV})('main select',{json.dumps(val)})"); time.sleep(.35); return r
    def cancel(s):
        s.btn('Cancelar'); s.btn('Descartar alterações'); s.btn('Fechar')
    def shot(s,nome): s.c.shot(os.path.join(HERE,'_probe',nome))
    def fim(s):
        try: s.c.close()
        finally: s.srv.terminate()
        print('RESULTADO:', 'OK' if all(s.ok) else 'FALHOU', f'{sum(s.ok)}/{len(s.ok)}')
