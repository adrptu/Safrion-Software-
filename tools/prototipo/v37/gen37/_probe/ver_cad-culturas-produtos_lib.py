# -*- coding: utf-8 -*-
"""Apoio do verificador independente (frente cad-culturas-produtos). Chrome headless real via CDP, 1440x1000.
Captura TODOS os erros de JS (window.onerror, unhandledrejection, console.error)."""
import sys, os, time, subprocess, json
HERE=os.path.dirname(os.path.abspath(__file__)); GEN=os.path.dirname(HERE); sys.path.insert(0,GEN)
from cdp import Chrome
from journeys import free
ERRS=("window.__errs=[];window.addEventListener('error',e=>window.__errs.push('onerror: '+String(e.message)));"
      "window.addEventListener('unhandledrejection',e=>window.__errs.push('rej: '+String(e.reason)));"
      "const __ce=console.error;console.error=function(){window.__errs.push('console: '+[...arguments].map(String).join(' ').slice(0,300));__ce.apply(console,arguments);};")
SETV="""((el,val)=>{const P=el.tagName==='SELECT'?HTMLSelectElement.prototype:(el.tagName==='TEXTAREA'?HTMLTextAreaElement.prototype:HTMLInputElement.prototype); Object.getOwnPropertyDescriptor(P,'value').set.call(el,val); el.dispatchEvent(new Event('input',{bubbles:true})); el.dispatchEvent(new Event('change',{bubbles:true})); return true;})"""
N="(s=>(s||'').replace(/\\s+/g,' ').trim())"
class V:
    def __init__(s,w=1440,h=1000,clear_ls=True,root=None):
        s.p=free(); s.srv=subprocess.Popen(['python3','-m','http.server',str(s.p),'--bind','127.0.0.1','--directory',root or os.path.join(GEN,'_render')],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        time.sleep(0.6); s.c=Chrome(port=free(),w=w,h=h); s.J=s.c.js; s.res=[]
        s.c.call('Page.addScriptToEvaluateOnNewDocument',{'source':ERRS}); s.c.size(w,h)
    def goto(s,f,wait=1.2): s.c.goto(f'http://127.0.0.1:{s.p}/{f}',wait=wait); time.sleep(.3)
    def errs(s): return s.J("(window.__errs||[])")
    def chk(s,nome,cond,extra=''):
        s.res.append((nome,bool(cond))); print(('OK      ' if cond else 'DEFEITO ')+nome+(' · '+str(extra)[:600] if extra!='' else ''))
    def info(s,nome,val): print('INFO    '+nome+' · '+str(val)[:1500])
    # linhas
    def ROW(s,txt,ti=None):
        scope="document" if ti is None else f"document.querySelectorAll('[role=table]')[{ti}]"
        return f"[...{scope}.querySelectorAll('[role=row]')].find(r=>{N}(r.innerText).indexOf({json.dumps(txt)})>=0)"
    def rowtxt(s,txt,ti=None): return s.J(f"(()=>{{const r={s.ROW(txt,ti)}; return r?{N}(r.innerText):null;}})()")
    def clickrow(s,txt,ti=None,sel='.g2pw'):
        r=s.J(f"(()=>{{const r={s.ROW(txt,ti)}; if(!r) return 'sem linha'; const t=r.querySelector({json.dumps(sel)})||r.querySelector('[role=cell]'); t.click(); return 'ok';}})()"); time.sleep(.4); return r
    def keyrow(s,txt,ti=None):
        r=s.J(f"(()=>{{const r={s.ROW(txt,ti)}; if(!r) return 'sem linha'; r.focus(); r.dispatchEvent(new KeyboardEvent('keydown',{{key:'Enter',bubbles:true}})); return 'ok';}})()"); time.sleep(.4); return r
    # formulário
    def F(s,k): return f"document.querySelector('aside[role=dialog] [id$=\"_{k}\"]')"
    def fv(s,k): return s.J(f"(()=>{{const i={s.F(k)}; return i?i.value:null;}})()")
    def fdis(s,k): return s.J(f"(()=>{{const i={s.F(k)}; return i?(i.disabled||i.readOnly):null;}})()")
    def fopts(s,k): return s.J(f"(()=>{{const i={s.F(k)}; return i&&i.options?[...i.options].map(o=>o.value):null;}})()")
    def fset(s,k,val): r=s.J(f"(()=>{{const i={s.F(k)}; if(!i) return false; return ({SETV})(i,{json.dumps(val)});}})()"); time.sleep(.25); return r
    def labels(s): return s.J("[...document.querySelectorAll('aside[role=dialog] label')].map(l=>l.innerText.trim()).filter(Boolean)")
    def dlg(s): return s.J(f"{N}((document.querySelector('aside[role=dialog]')||{{}}).innerText||'')")
    def title(s): return s.J(f"{N}((document.querySelector('aside[role=dialog] h2')||{{}}).innerText||'')")
    def isopen(s): return s.J("!!document.querySelector('aside[role=dialog]')")
    def btn(s,t):
        r=s.J(f"(()=>{{const b=[...document.querySelectorAll('aside[role=dialog] button, [role=alertdialog] button')].find(b=>{N}(b.innerText)==={json.dumps(t)}); if(b){{b.click(); return true;}} return false;}})()"); time.sleep(.4); return r
    def clk(s,t,exact=True):
        r=s.J(f"(()=>{{const els=[...document.querySelectorAll('button,a,[role=tab]')].filter(e=>e.getClientRects().length); const e=els.find(x=>{N}(x.innerText)==={json.dumps(t)})||({'false' if exact else 'true'}&&els.find(x=>{N}(x.innerText).startsWith({json.dumps(t)}))); if(!e) return 'NAO ACHEI'; e.click(); return 'ok';}})()"); time.sleep(.4); return r
    def visible_btns(s): return s.J(f"[...document.querySelectorAll('header button, main button, header a')].filter(e=>e.getClientRects().length).map(e=>{N}(e.innerText)).filter(Boolean)")
    def alerts(s): return s.J(f"[...document.querySelectorAll('aside [role=alert]')].map(x=>{N}(x.innerText)).join(' | ')")
    def toast(s): return s.J(f"[...document.querySelectorAll('[role=status]')].map(x=>{N}(x.innerText)).filter(Boolean).join(' | ')")
    def header(s): return s.J(f"{N}(document.querySelector('header').innerText)")
    def cancel(s):
        s.btn('Cancelar'); s.btn('Descartar alterações'); s.btn('Fechar')
    # layout
    def overflow(s):
        """tabelas e caixas com rolagem lateral; conteúdo além da altura do artboard; textos cortados com reticências."""
        return s.J(r"""(()=>{const out={}; const root=document.querySelector('[data-root]');
          out.tabelas=[...document.querySelectorAll('[role=table]')].map(t=>{let e=t; while(e&&e!==document.body){ if(e.scrollWidth>e.clientWidth+1&&['auto','scroll'].includes(getComputedStyle(e).overflowX)) return {sw:e.scrollWidth,cw:e.clientWidth}; e=e.parentElement;} return {sw:t.scrollWidth,cw:t.clientWidth,ok:t.getBoundingClientRect().right<=root.getBoundingClientRect().right};});
          const main=document.querySelector('main'); const last=[...main.children].filter(x=>x.getClientRects().length).pop();
          out.alt_root=root.clientHeight; out.fim_main=Math.round(main.getBoundingClientRect().top+main.scrollHeight); out.fim_ultimo=last?Math.round(last.getBoundingClientRect().bottom-root.getBoundingClientRect().top):0;
          const foot=main.nextElementSibling; out.rodape_fim=foot?Math.round(foot.getBoundingClientRect().bottom-root.getBoundingClientRect().top):null;
          out.cortados=[...main.querySelectorAll('*')].filter(e=>{ if(!e.getClientRects().length||e.children.length>2) return false; const cs=getComputedStyle(e); return (cs.textOverflow==='ellipsis'||cs.overflow==='hidden'||cs.overflowX==='hidden'||cs.overflow==='clip') && e.scrollWidth>e.clientWidth+2 && (e.innerText||'').trim().length>0;}).map(e=>(e.innerText||'').replace(/\s+/g,' ').trim().slice(0,80)).slice(0,15);
          out.largura_main=[main.scrollWidth,main.clientWidth];
          return out;})()""")
    def shot(s,nome): s.c.shot(os.path.join(HERE,nome))
    def fim(s):
        try: s.c.close()
        finally: s.srv.terminate()
        bad=[n for n,o in s.res if not o]
        print('RESUMO:', f'{len(s.res)-len(bad)}/{len(s.res)} ok', ('· DEFEITOS: '+' ; '.join(bad)) if bad else '')
def load():
    return V
