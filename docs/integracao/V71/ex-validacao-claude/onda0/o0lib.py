# -*- coding: utf-8 -*-
"""Apoio da reprodução da Onda 0 (EX-32..36), só leitura: abre o render limpo, reinicia o cenário por perfil, clica como a pessoa."""
import os, sys, json, time
GEN = '/home/user/sp-v69/tools/prototipo/v37/gen37'
RENDER = '/tmp/claude-0/v69b/tools/prototipo/v37/gen37/_render'
OUT = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault('CHROME_BIN', '/tmp/cloudchrome/chrome'); os.environ.setdefault('CDP_GL', '1'); os.environ.setdefault('SAFRION_DADOS', 'sintetico')
sys.path.insert(0, GEN)
from comp_lib import Chrome, servir

VIS = "const vis=e=>!!e&&e.getClientRects().length>0&&getComputedStyle(e).visibility!=='hidden';const n=s=>(s||'').replace(/\\s+/g,' ').trim();"

class S:
    def __init__(self):
        self.p, self.srv = servir(RENDER); self.c = Chrome(); self.c.aparelho(1440, 1000)
        self.base = f'http://127.0.0.1:{self.p}/'; self.log = []
    def J(self, e): return self.c.js(e)
    def reset(self, perfil='Ana'):
        self.c.goto(self.base + 'Main.dc.html', .3)
        self.J(f"localStorage.clear(); sessionStorage.clear(); localStorage.setItem('safrion.perfilDemo',{json.dumps(perfil)}); true")
    def ir(self, pag, espera=1.2):
        self.c.goto(self.base + pag, espera)
    def perfil(self):
        return self.J("(()=>{try{return localStorage.getItem('safrion.perfilDemo')}catch(e){return null}})()")
    def ls(self):
        return self.J("(()=>{const o={}; for(let i=0;i<localStorage.length;i++){const k=localStorage.key(i); o[k]=localStorage.getItem(k);} return o;})()")
    def botoes(self, raiz=None, filtro=None):
        r = json.dumps(raiz)
        return self.J("(()=>{"+VIS+f"const R={r}?document.querySelector({r}):document; if(!R) return null; return [...R.querySelectorAll('button,a,[role=button]')].filter(vis).map(b=>n(b.innerText)||('['+(b.getAttribute('aria-label')||b.title||'')+']')).filter(x=>x)"+"})()")
    def clica(self, txt, raiz=None, idx=0, exato=True, espera=.7):
        r = json.dumps(raiz); t = json.dumps(txt)
        res = self.J("(()=>{"+VIS+f"const R={r}?[...document.querySelectorAll({r})].filter(vis).pop():document; if(!R) return 'SEM RAIZ'; const t={t};"
                     f"const c=[...R.querySelectorAll('button,a,[role=button],[role=tab],[role=option],[role=menuitem],[role=menuitemradio],label')].filter(vis).filter(b=>{'n(b.innerText)===t' if exato else 'n(b.innerText).includes(t)'}||n(b.getAttribute('aria-label'))===t);"
                     f"if(c.length<={idx}) return 'NÃO ACHEI: '+t+' ('+c.length+')'; c[{idx}].scrollIntoView({{block:'center'}}); c[{idx}].click(); return 'ok';"+"})()")
        time.sleep(espera); return res
    def toast(self):
        return self.J("(()=>{"+VIS+"return [...document.querySelectorAll('[role=status],[role=alert],[aria-live]')].filter(vis).map(e=>n(e.innerText)).filter(x=>x).join(' ¦ ');})()")
    def dialogo(self):
        return self.J("(()=>{"+VIS+"const d=[...document.querySelectorAll('[role=dialog],aside[aria-modal],dialog[open]')].filter(vis).pop(); return d?n(d.innerText):null;})()")
    def campos(self, raiz='[role=dialog]'):
        r = json.dumps(raiz)
        return self.J("(()=>{"+VIS+f"const d=[...document.querySelectorAll({r})].filter(vis).pop(); if(!d) return null;"
                      "return [...d.querySelectorAll('input,select,textarea,[role=checkbox],[role=radio],[role=switch],[aria-pressed],[aria-checked]')].filter(vis).map(e=>{"
                      "const lab=e.id&&d.querySelector('label[for=\"'+e.id+'\"]'); const L=n((lab&&lab.innerText)||e.getAttribute('aria-label')||(e.closest('label')&&e.closest('label').innerText)||(e.parentElement&&e.parentElement.innerText)||'').slice(0,90);"
                      "return {tag:e.tagName,type:e.type||e.getAttribute('role'),lab:L,val:e.value!==undefined?String(e.value).slice(0,60):null,checked:(e.checked!==undefined?e.checked:null),aria:e.getAttribute('aria-checked')||e.getAttribute('aria-pressed'),dis:!!e.disabled,opts:e.tagName==='SELECT'?[...e.options].map(o=>o.text).slice(0,40):undefined};});})()")
    def texto(self, sel='main'):
        return self.J(f"(()=>{{const e=document.querySelector({json.dumps(sel)}); return e?e.innerText:document.body.innerText;}})()")
    def shot(self, nome):
        p = os.path.join(OUT, nome + '.png'); self.c.shot(p); return p
    def erros(self): return self.J("window.__errs||[]")
    def fim(self):
        self.c.close()
        try: self.srv.terminate(); self.srv.wait(5)
        except Exception: pass

def cen(s):
    t = s.J("localStorage.getItem('talhao-os-cenario-v1')")
    return json.loads(t) if t else None

def clicaT(s, txt, raiz=None, idx=0, espera=.7):
    """clica no primeiro elemento visível cujo texto, aria-label ou title contenha txt (em raiz, se dada)."""
    r = json.dumps(raiz); t = json.dumps(txt)
    res = s.J("(()=>{"+VIS+f"const R={r}?[...document.querySelectorAll({r})].filter(vis).pop():document; if(!R) return 'SEM RAIZ'; const t={t};"
              "const c=[...R.querySelectorAll('button,a,[role=button],[role=tab],[role=menuitem],label,option')].filter(vis).filter(b=>n(b.innerText).includes(t)||n(b.getAttribute('aria-label')).includes(t)||n(b.title).includes(t));"
              f"if(c.length<={idx}) return 'NÃO ACHEI: '+t; const e=c[{idx}]; e.scrollIntoView({{block:'center'}}); e.click(); return 'ok: '+(n(e.innerText)||e.getAttribute('aria-label')||e.title);"+"})()")
    time.sleep(espera); return res

def preenche(s, mapa, raiz='[role=dialog]'):
    """mapa {rótulo contido: valor}; input/textarea/select por rótulo (label for, aria-label ou texto do contêiner)."""
    return s.J("(()=>{"+VIS+f"const d=[...document.querySelectorAll({json.dumps(raiz)})].filter(vis).pop(); if(!d) return 'sem diálogo'; const M={json.dumps(mapa,ensure_ascii=False)};"
      "const set=(el,v)=>{ if(el.tagName==='SELECT'){ const o=[...el.options].find(o=>o.text===v||o.value===v); if(o){ el.value=o.value; } } else { const p=Object.getPrototypeOf(el); Object.getOwnPropertyDescriptor(p,'value').set.call(el,v); }"
      " el.dispatchEvent(new Event('input',{bubbles:true})); el.dispatchEvent(new Event('change',{bubbles:true})); el.dispatchEvent(new Event('blur',{bubbles:true})); };"
      "const out={}; const els=[...d.querySelectorAll('input,select,textarea')].filter(vis);"
      "Object.keys(M).forEach(k=>{ const e=els.find(e=>{ const lab=e.id&&d.querySelector('label[for=\"'+e.id+'\"]'); const L=n((lab&&lab.innerText)||e.getAttribute('aria-label')||(e.closest('label')&&e.closest('label').innerText)||(e.parentElement&&e.parentElement.innerText)||''); return L.includes(k); });"
      " if(!e){ out[k]='NÃO ACHEI'; return; } set(e,M[k]); out[k]=e.value; }); return out; })()")
