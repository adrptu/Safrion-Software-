# Verificador rodada 4 · sonda K: excluir conjunto e equipe novos, barra de filtros com contagens maiores, nome acessível do estado
import sys, os, time, json
HERE=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0,HERE); os.chdir(HERE)
from cada_lib import T
T0=time.time()
t=T(); J=t.J
def lg(*a): print(round(time.time()-T0,1),*a, flush=True)
MULTI="""((t)=>{const l=[...document.querySelectorAll('aside[role=dialog] label')].find(x=>x.innerText.trim()===t); if(!l) return false; l.querySelector('input').click(); return true;})"""
def marca(txt): r=J(f"({MULTI})({json.dumps(txt)})"); time.sleep(.2); return r
def delrow(ti,txt): r=J(f"(()=>{{const r=[...document.querySelectorAll('[role=table]')[{ti}].querySelectorAll('[role=row]')].find(r=>r.innerText.indexOf({json.dumps(txt)})>=0); const b=r&&[...r.querySelectorAll('button')].find(b=>(b.getAttribute('aria-label')||'').indexOf('Excluir')===0); if(!b) return false; b.click(); return true;}})()"); time.sleep(.35); return r
try:
    t.c.size(1440,1000); t.goto('CD-03.dc.html')
    lg('nome acessível estado CD-03:',J("(()=>{const b=[...document.querySelectorAll('header button')].find(b=>b.getAttribute('aria-label')); return [b.getAttribute('aria-label'),b.innerText.trim()];})()"))
    t.clk('Montar conjunto'); t.fset('maq','Trator 02'); t.fset('impl','Distribuidor 3 t'); marca('Adubação a lanço'); t.btn('Salvar'); time.sleep(.2); lg('novo cj:',t.toast())
    lg('del click:',delrow(1,'Trator 02 + Distribuidor 3 t')); lg('apos del:',J("document.body.innerText.replace(/\\s+/g,' ').match(/.{0,80}(Excluir|excluíd|Desfazer).{0,80}/)"),'| ainda existe:',t.anyrow(1,'Trator 02 + Distribuidor 3 t'))
    btns=J("[...document.querySelectorAll('[role=dialog] button, [role=alertdialog] button')].map(b=>b.innerText.trim())"); lg('dialog btns:',btns)
    if btns: J("(()=>{const b=[...document.querySelectorAll('[role=dialog] button, [role=alertdialog] button')].find(b=>/Excluir/.test(b.innerText)); if(b) b.click();})()"); time.sleep(.3); lg('apos confirmar:',t.anyrow(1,'Trator 02 + Distribuidor 3 t'),t.toast())
    lg('col Trator 02:',t.rowtxt(0,'Trator 02'))
    t.goto('CD-04.dc.html')
    lg('nome acessível estado CD-04:',J("(()=>{const b=[...document.querySelectorAll('header button')].find(b=>b.getAttribute('aria-label')); return [b.getAttribute('aria-label'),b.innerText.trim()];})()"))
    for nm in ['Rafael Albuquerque','Sebastião Nogueira']:
        t.clk('Cadastrar pessoa'); t.fset('nome',nm); t.fset('adm','2026-01-10'); t.fset('custo','35'); marca('Operar trator'); marca('Irrigar'); marca('Almoxarifado'); marca('Aprovar O.S. (agrônomo)'); t.fset('v31','2026-10-10'); t.btn('Salvar'); time.sleep(.2)
    lg('toolbar:',J("(()=>{const b=document.querySelector('button[aria-pressed]'); let p=b.parentElement; while(p && p.scrollWidth<=p.clientWidth+1 && p.tagName!=='MAIN') p=p.parentElement; return p?[p.tagName,p.scrollWidth,p.clientWidth]:'sem overflow';})()"))
    lg('grades:',J("[...document.querySelectorAll('[role=table]')].map(t=>{const w=t.parentElement; return w.scrollWidth+'/'+w.clientWidth;})"),'docW',J("document.documentElement.scrollWidth"))
    lg('linha:',t.rowtxt(0,'Sebastião'))
    t.shot('ver_cad-ativos-pessoas_r4k_cd04.png')
    lg('erros:',t.errs())
finally:
    t.fim()
