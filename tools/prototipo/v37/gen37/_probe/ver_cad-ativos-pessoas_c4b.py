# Verificador CD-04 (B): equipes (renomear, nova, excluir, líder), filtros rápidos com contagem e Limpar, estado clicável, acesso no novo.
import sys, os, time, json
HERE=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0,HERE)
from cada_lib import T
t=T(); J=t.J; t.c.size(1440,1000)
MULTI="""((t)=>{const l=[...document.querySelectorAll('aside[role=dialog] label')].find(x=>x.innerText.trim()===t); if(!l) return false; l.querySelector('input').click(); return true;})"""
def marca(txt): r=J(f"({MULTI})({json.dumps(txt)})"); time.sleep(.2); return r
def nomes(): return J("[...document.querySelectorAll('[role=table]')[0].querySelectorAll('[role=row].g2ed')].map(r=>r.querySelector('b').innerText)")
def conta(): return J("(document.body.innerText.match(/(\\d+) de (\\d+)/)||[]).slice(0,1).join('')")
def tb(): return J("(()=>{const t=document.querySelectorAll('[role=table]')[0]; let p=t.parentElement; for(let i=0;i<4&&p;i++){ if(p.innerText.indexOf('Buscar')>=0||p.querySelector('input')) break; p=p.parentElement;} return (p?p.innerText:'').split('\\n').slice(0,14).join(' ¦ ');})()")
try:
    t.goto('CD-04.dc.html')
    t.clk('Caldeiros 2'); print('Caldeiros:',nomes(),'conta:',conta(),'| limpar?',J("[...document.querySelectorAll('button')].some(b=>b.innerText.trim()==='Limpar filtros')"))
    t.clk('Limpar filtros'); print('após limpar:',nomes().__len__(),conta(),J("[...document.querySelectorAll('button[aria-pressed=true]')].map(b=>b.innerText.replace(/\\s+/g,' '))"))
    # quick filter + busca
    t.clk('Operadores 4'); J("(()=>{const i=document.querySelector('input[placeholder^=Buscar]'); const P=HTMLInputElement.prototype; Object.getOwnPropertyDescriptor(P,'value').set.call(i,'Lucas'); i.dispatchEvent(new Event('input',{bubbles:true}));})()"); time.sleep(.3)
    print('Operadores+Lucas:',nomes(),conta()); t.clk('Limpar filtros'); print('limpar:',len(nomes()),conta(),J("document.querySelector('input[placeholder^=Buscar]').value"))
    # estado clicável: 2 cliques
    t.clk('2 não alocáveis'); a=nomes(); t.clk('2 não alocáveis'); b=nomes(); print('estado toggle:',a,len(b))
    # renomear equipe Campo 2
    t.openrow(1,'Campo 2'); print('eq titulo:',t.title(),'lider opts:',t.fopts('lider')); t.fset('nome','Campo Sul'); t.btn('Salvar'); time.sleep(.3)
    print('rename toast:',t.toast()); print('Lucas:',t.rowtxt(0,'Lucas')); print('Nilton:',t.rowtxt(0,'Nilton'))
    t.openrow(0,'Lucas'); print('Lucas equipe v:',t.fv('equipe'),'opts:',t.fopts('equipe')); t.cancel()
    # nova equipe
    t.clk('Nova equipe'); print('nova eq titulo:',t.title()); t.fset('nome','Colheita'); t.fset('lider','Carlos'); t.fset('cal','seg–sex · 07–17h'); t.btn('Salvar'); time.sleep(.3)
    print('nova eq toast:',t.toast()); print('row:',t.anyrow(1,'Colheita'))
    btns=J(f"""(()=>{{const r=[...document.querySelectorAll('[role=table]')[1].querySelectorAll('[role=row]')].find(r=>r.innerText.indexOf('Colheita')>=0); return r?[...r.querySelectorAll('button')].map(b=>b.getAttribute('aria-label')||b.innerText):null;}})()"""); print('botões nova equipe:',btns)
    # novo com Solicitar acesso
    t.clk('Cadastrar pessoa'); print('novo acesso opts:',t.fopts('acesso'),'v:',t.fv('acesso'),'equipe opts',t.fopts('equipe'))
    for k,v in [('nome','Rafa'),('adm','2026-09-01'),('custo','30')]: t.fset(k,v)
    marca('Conferir'); t.fset('acesso','Solicitar acesso ao app'); t.btn('Salvar'); time.sleep(.3); print('Rafa:',t.rowtxt(0,'Rafa'),'| toast:',t.toast(),'| alerts:',t.alerts())
    t.openrow(0,'Rafa'); print('Rafa acesso dis:',t.fdis('acesso'),t.fv('acesso')); t.cancel()
    print('erros:',t.errs(),'motor:',t.errs_motor())
finally:
    t.fim()
