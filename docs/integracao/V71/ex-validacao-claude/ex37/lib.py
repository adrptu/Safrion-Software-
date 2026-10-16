# -*- coding: utf-8 -*-
"""Apoio da validação EX-37/EX-01/EX-04/EX-05 (só leitura). Anexa ao Chrome e ao servidor já abertos (pids.txt)."""
import os, sys, json, time
EX=os.path.dirname(os.path.abspath(__file__))
GEN='/home/user/sp-v69/tools/prototipo/v37/gen37'
sys.dont_write_bytecode=True
os.environ.setdefault('CHROME_BIN','/tmp/cloudchrome/chrome'); os.environ.setdefault('CDP_GL','1')
sys.path.insert(0, GEN)
L={l.split()[0]: l.split()[1:] for l in open(os.path.join(EX, 'pids.txt')) if l.strip()}
os.environ['CDP_PORT'] = L[os.environ.get('EXCH','CHROME')][1]
os.environ.setdefault('SAFRION_DADOS', 'sintetico')
from comp_lib import Chrome
BASE = f"http://127.0.0.1:{L['SRV'][1]}/"
CAP = os.path.join(EX, 'cap')

def novo():
    c = Chrome(); c.aparelho(1440, 900); return c

def abre(c, tela, hash='', perfil='Ana'):
    """Main.dc.html, limpa localStorage/sessionStorage, perfil Ana, depois a tela."""
    c.call('Page.navigate', {'url': BASE + 'Main.dc.html'})
    for _ in range(50):
        try:
            if c.js("document.readyState")=='complete' and c.js("location.pathname").endswith('Main.dc.html'): break
        except Exception: pass
        time.sleep(.1)
    c.js("localStorage.clear(); sessionStorage.clear(); localStorage.setItem('safrion.perfilDemo', %s); 1" % json.dumps(perfil))
    c.call('Page.navigate', {'url': 'about:blank'}); time.sleep(.15)
    c.goto(BASE + tela + '.dc.html' + hash, .5)
    time.sleep(.4)

N = "const n=s=>(s||'').replace(/\\s+/g,' ').trim();"
VIS = "const vis=e=>{ if(!e) return false; const r=e.getBoundingClientRect(); const cs=getComputedStyle(e); return r.width>1&&r.height>1&&cs.visibility!=='hidden'&&cs.display!=='none'&&cs.opacity!=='0'; };"
VERDE = "const verde=e=>getComputedStyle(e).backgroundColor==='rgb(30, 122, 76)';"

def clica(c, rotulo, escopo='document', exato=False, idx=0):
    """Clica no botão/link visível com o rótulo (igual, depois começa com, depois contém)."""
    js = f"""(()=>{{ {N}{VIS} const R={escopo}; const els=[...R.querySelectorAll('button,a,[role=button],[role=menuitem],[role=option],[role=tab]')].filter(vis);
      const t={json.dumps(rotulo)}; let c=els.filter(e=>n(e.innerText)===t||n(e.getAttribute('aria-label'))===t);
      if(!c.length&&!{str(exato).lower()}) c=els.filter(e=>n(e.innerText).startsWith(t)); if(!c.length&&!{str(exato).lower()}) c=els.filter(e=>n(e.innerText).includes(t));
      const e=c[{idx}]; if(!e) return null; e.scrollIntoView({{block:'center'}}); e.click(); return {{txt:n(e.innerText).slice(0,80), dis:!!e.disabled||e.getAttribute('aria-disabled')==='true', tag:e.tagName, href:e.getAttribute('href')}}; }})()"""
    r = c.js(js); time.sleep(.6); return r

DLG = r"""(()=>{ %s%s%s
 const ds=[...document.querySelectorAll('[role=dialog],aside[aria-modal],dialog[open]')].filter(vis);
 return ds.map(d=>{ const lab=e=>{ if(e.id){ const l=document.querySelector('label[for="'+e.id+'"]'); if(l) return n(l.innerText);} const l=e.closest('label'); if(l) return n(l.innerText).slice(0,60); const p=e.parentElement; return n((p&&p.innerText)||e.getAttribute('aria-label')||e.placeholder||'').slice(0,60); };
   const ins=[...d.querySelectorAll('input,select,textarea')].filter(e=>e.type!=='hidden');
   const campos=ins.map(e=>({tag:e.tagName,type:e.type||'',lab:lab(e),req:!!e.required||e.getAttribute('aria-required')==='true',vis:vis(e),val:(e.value||'').slice(0,40),ro:!!e.readOnly||!!e.disabled}));
   const bts=[...d.querySelectorAll('button')].filter(vis).map(b=>({t:n(b.innerText).slice(0,50),verde:verde(b),dis:!!b.disabled||b.getAttribute('aria-disabled')==='true'}));
   const h=d.querySelector('h1,h2,h3,[class*=tit]'); const ast=[...d.querySelectorAll('*')].filter(e=>e.children.length===0&&/\*|obrigat/i.test(e.textContent)).map(e=>n(e.textContent).slice(0,60)).slice(0,10);
   return {titulo:n(h&&h.innerText).slice(0,80), campos, bts, ast, txt:n(d.innerText).slice(0,1500)}; }); })()""" % (N, VIS, VERDE)

def dialogo(c):
    return c.js(DLG)

def shot(c, nome):
    p = os.path.join(CAP, nome + '.png'); c.shot(p); return p

def texto(c):
    return c.js("document.body.innerText")

def botoes(c, escopo='document'):
    return c.js(f"""(()=>{{ {N}{VIS}{VERDE} return [...({escopo}).querySelectorAll('button,a')].filter(vis).map(b=>({{t:n(b.innerText).slice(0,60),verde:verde(b),dis:!!b.disabled||b.getAttribute('aria-disabled')==='true',title:(b.title||'').slice(0,120)}})).filter(x=>x.t); }})()""")

def resume_dlg(d):
    out=[]
    for x in d or []:
        cv=[f for f in x['campos'] if f['vis']]
        tipos={}
        for f in cv: tipos[f['type'] or f['tag']]=tipos.get(f['type'] or f['tag'],0)+1
        out.append({'titulo':x['titulo'],'n_campos_vis':len(cv),'n_campos_total':len(x['campos']),'tipos':tipos,
                    'req':sum(1 for f in cv if f['req']),'ast':x['ast'],
                    'rotulos':[f['lab'][:40] for f in cv],
                    'verdes':[b['t'] for b in x['bts'] if b['verde']],'bts':[b['t']+(' [dis]' if b['dis'] else '') for b in x['bts']]})
    return out

def clica_linha(c, nome, idx=0):
    """Clica na linha (role=row ou tr) visível cujo texto tem uma folha igual a nome."""
    r = c.js(f"""(()=>{{ const es=[...document.querySelectorAll('main *, body > div *')].filter(x=>x.children.length===0&&x.textContent.trim()==={json.dumps(nome)}&&!x.closest('select,option,[role=dialog]')&&x.getClientRects().length);
      const rows=[]; es.forEach(e=>{{ const r=e.closest('[role=row],tr'); if(r&&!rows.includes(r)) rows.push(r); }}); const r=rows[{idx}]; if(!r) return null; r.scrollIntoView({{block:'center'}});
      const cel=r.querySelector('[role=cell],td')||r; const alvo=[...r.querySelectorAll('*')].find(x=>x.children.length===0&&x.textContent.trim()==={json.dumps(nome)})||cel; alvo.click(); return r.innerText.replace(/\\s+/g,' ').slice(0,120); }})()""")
    time.sleep(.8); return r

def paineis(c):
    return c.js("(()=>{const d=[...document.querySelectorAll('[role=dialog],aside')].filter(e=>e.getClientRects().length&&getComputedStyle(e).visibility!=='hidden'); return d.map(e=>e.innerText).join('\\n#\\n');})()")
