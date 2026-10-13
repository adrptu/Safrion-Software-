# -*- coding: utf-8 -*-
"""Biblioteca de navegação (somente leitura do repositório) para reproduzir os dois S2 da CTL-4 em qualquer versão.
Copiada de ctl4rv/v1-estado/nav_estado*.py, com G (gen37) parametrizado por GEN, capturas por OUTD e log por LOGF."""
import sys, os, time, subprocess, json
G=os.environ['GEN']; sys.path.insert(0,G)
from cdp import Chrome
from journeys import free
from est_lib import FIND
R=os.path.join(G,'_render'); OUT=os.environ['OUTD']; os.makedirs(OUT,exist_ok=True)
LOGF=os.environ['LOGF']
CLK="""((t,root)=>{const r=root?document.querySelector(root):document; if(!r) return 'SEM RAIZ'; const n=s=>(s||'').replace(/\\s+/g,' ').trim(); const els=[...r.querySelectorAll('button,a')].filter(e=>e.offsetParent!==null); const e=els.find(x=>n(x.innerText)===t)||els.find(x=>n(x.innerText).startsWith(t)); if(!e) return 'NÃO ACHEI: '+t; e.click(); return 'ok';})"""
SETV="""((sel,val)=>{const i=document.querySelector(sel); if(!i) return 'sem campo '+sel; const P=i.tagName==='SELECT'?HTMLSelectElement.prototype:(i.tagName==='TEXTAREA'?HTMLTextAreaElement.prototype:HTMLInputElement.prototype); Object.getOwnPropertyDescriptor(P,'value').set.call(i,val); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true})); return 'ok';})"""
LOG=[]
def log(*a):
    s=' '.join(str(x) for x in a); LOG.append(s); print(s,flush=True)
class Nav:
    def __init__(self):
        self.p=free(); self.srv=subprocess.Popen(['python3','-m','http.server',str(self.p),'--bind','127.0.0.1','--directory',R],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(0.8)
        self.c=Chrome(port=free()); self.J=self.c.js; self.B=f'http://127.0.0.1:{self.p}/'
        self.c.call('Page.addScriptToEvaluateOnNewDocument',{'source':"window.__err=[];addEventListener('error',e=>window.__err.push(String(e.message)));"})
        self.c.size(1440,1000); self.ir('SAF.dc.html'); self.J("localStorage.clear(); sessionStorage.clear()")
    def close(self):
        try: self.c.close()
        finally: self.srv.terminate(); open(LOGF,'w').write('\n'.join(LOG)+'\n')
    def clk(self,t,root=None,w=.45): r=self.J(f"({CLK})({json.dumps(t)},{json.dumps(root)})"); time.sleep(w); return r
    def setv(self,sel,v): r=self.J(f"({SETV})({json.dumps(sel)},{json.dumps(v)})"); time.sleep(.25); return r
    def T(self): return self.J("[...document.querySelectorAll('[role=status],[role=alert]')].map(x=>x.innerText).filter(Boolean).join(' | ')") or ''
    def ir(self,f,w=1.4): self.c.goto('about:blank',wait=.1); self.c.goto(self.B+f,wait=w)
    def cel(self,nome,coluna):
        return self.J(f"""(()=>{{const t=[...document.querySelectorAll('[role=table]')].find(t=>t.offsetParent); if(!t) return ''; const hs=[...t.querySelectorAll('[role=columnheader]')].map(h=>h.innerText.replace(/[⇅▾▴]/g,'').replace(/\\s+/g,' ').trim().toUpperCase());
          const iI=hs.indexOf('INSUMO'), i=hs.indexOf({json.dumps(coluna.upper())}); if(i<0) return '(sem coluna '+{json.dumps(coluna)}+')'; const r=[...t.querySelectorAll('[role=row]')].find(x=>{{const cs=x.querySelectorAll('[role=cell]'); return cs[iI]&&cs[iI].innerText.replace(/\\s+/g,' ').trim()==={json.dumps(nome)};}});
          return r?[...r.querySelectorAll('[role=cell]')][i].innerText.replace(/\\s+/g,' ').trim():'(sem linha)';}})()""") or ''
    def heads(self): return self.J("(()=>{const t=[...document.querySelectorAll('[role=table]')].find(t=>t.offsetParent); return t?[...t.querySelectorAll('[role=columnheader]')].map(h=>h.innerText.replace(/[⇅▾▴]/g,'').replace(/\\s+/g,' ').trim()):[];})()") or []
    def rowtxt(self,nome): return self.J(f"(()=>{{const r=[...document.querySelectorAll('[role=row]')].filter(r=>r.offsetParent).find(r=>{{const c=r.querySelector('[role=cell]'); return c&&c.innerText.replace(/\\s+/g,' ').trim()==={json.dumps(nome)};}}) || [...document.querySelectorAll('[role=row]')].filter(r=>r.offsetParent).find(r=>r.innerText.indexOf({json.dumps(nome)})>=0); return r?r.innerText.replace(/\\s+/g,' ').trim():'(sem linha)';}})()") or ''
    def k6(self): return self.J("(document.body.innerText.match(/Valor da necessidade[^\\n]+/)||[''])[0]") or ''
    def prim(self): return (self.J("(()=>{const b=[...document.querySelectorAll('.acoes-prim')].find(x=>x.offsetParent); return b?b.innerText.replace(/\\s+/g,' ').trim():'';})()") or '')
    def saf(self,s='S2627'): self.ir(f'SAF.dc.html#saf={s}&passo=demanda',w=1.8); self.clk('Expandir tudo',w=.6)
    def safler(self,nomes,s='S2627'):
        self.saf(s); return dict(total=self.k6(),prim=self.prim(),**{n:[self.cel(n,k) for k in ('Necessidade líquida','Estoque apto','Situação')]+[self.rowtxt(n)] for n in nomes})
    def cmp_row(self,nome):
        self.ir('CMP.dc.html#sol=SOL-2026-07&saf=S2627',w=1.8); self.clk('Expandir tudo',w=.6)
        tot=self.J("[...document.querySelectorAll('.g2tot')].filter(x=>x.offsetParent).map(x=>x.innerText).join(' ')") or ''
        r=self.J(f"(()=>{{const r=[...document.querySelectorAll('[role=row]')].filter(r=>r.offsetParent).find(r=>r.innerText.indexOf({json.dumps(nome)})>=0); return r?r.innerText.replace(/\\s+/g,' '):'';}})()") or ''
        k2=self.J("(document.body.innerText.match(/SOL-2026-07 · [^\\n]*/)||[''])[0]") or ''
        return dict(tot=tot.replace('\n',' '),row=r,k2=k2,prim=self.prim())
    def tap(self,t):
        SV="[...document.querySelectorAll('svg [role=button]')]"
        self.J(f"(()=>{{const e={SV}.find(x=>(x.getAttribute('aria-label')||'').startsWith('{t}:')); e&&e.dispatchEvent(new MouseEvent('click',{{bubbles:true}}));}})()"); time.sleep(.5)
    def pan(self,t): return (self.J(f"(document.querySelector('aside[aria-label^=\"{t}\"]')||{{}}).innerText||''") or '').replace('\n',' · ')
    def mapa(self,tal,prod):
        self.J(f"sessionStorage.setItem('mapa-ctx',{json.dumps(json.dumps({'mf_faz':'Santa Rita','lay':'Insumos','tsel':[],'flt':{'Insumos':{'per':'Safra toda'}}}))})"); self.ir('IN-04.dc.html',w=2.2)
        self.tap(tal); x=self.pan(tal); self.tap(tal)
        j=x.find('INSUMOS'); m=x.find('compartilhado da fazenda',max(j,0)); st=m if m>=0 else max(j,0); k=x.find(prod,st)
        return (x[:110]+' … '+(x[k:k+200] if k>=0 else '(produto não aparece no painel)'))
    def est_secao(self,i): self.ir('EST.dc.html',w=1.6); self.J(f"document.querySelectorAll('nav[aria-label=\"Seções do estoque\"] button')[{i-1}].click()"); time.sleep(.5)
    def est_row(self,*ts):
        r=self.J(f"(()=>{{const r=({FIND})({json.dumps(list(ts))}); if(!r) return 'sem linha'; (r.querySelector('[role=cell] span')||r).click(); return 'ok';}})()"); time.sleep(.5); return r
    def os_painel(self,oid):
        self.ir('OS.dc.html',w=1.6)
        self.J(f"(()=>{{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.trim().startsWith({json.dumps(oid)})); r&&r.click();}})()"); time.sleep(.6)
    def motivo(self,txt):
        self.J(f"(()=>{{const i=document.querySelector('textarea[aria-label=\"Motivo do cancelamento\"]'); if(!i) return; const P=HTMLTextAreaElement.prototype; Object.getOwnPropertyDescriptor(P,'value').set.call(i,{json.dumps(txt)}); i.dispatchEvent(new Event('input',{{bubbles:true}})); i.dispatchEvent(new Event('change',{{bubbles:true}}));}})()"); time.sleep(.3)
    def foto(self,n): self.c.shot(os.path.join(OUT,f'{n}.png'))
    def cen(self,expr):
        """lê o estado do cenário pela própria página do Estoque (window.__cen)"""
        self.ir('EST.dc.html',w=1.4); return self.J(f"(()=>{{const c=window.__cen.cenGet(); return {expr};}})()")
    def pt(self,nome):
        self.ir('PT-02det.dc.html',w=1.6); b=self.J("document.body.innerText") or ''
        import re; m=re.findall(r'R\$ ?[\d\.]+,\d\d',b)
        return dict(total=(self.J("(document.body.innerText.match(/Total[^\\n]*\\n?[^\\n]*/)||[''])[0]") or '').replace('\n',' '),row=self.rowtxt(nome))
    def su03det(self):
        self.ir('SU-03det.dc.html',w=1.6); b=self.J("document.body.innerText") or ''; return [l for l in b.split('\n') if 'pendência' in l.lower() or 'cobre' in l.lower()][:6]
    def erros(self): return self.J("window.__err||[]")
