# Verificador rodada 4 · sonda H: CD-04 estado até verde, filtros rápidos + Limpar filtros, equipes (renomear, calendário, excluir), inativar
import sys, os, time, json
HERE=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0,HERE); os.chdir(HERE)
from cada_lib import T
T0=time.time()
t=T(); J=t.J
def lg(*a): print(round(time.time()-T0,1),*a, flush=True)
def st(): return J("(()=>{const b=[...document.querySelectorAll('header button')].find(b=>b.getAttribute('aria-label')); return b?b.innerText.trim()+' | '+getComputedStyle(b).color:null;})()")
def chips(): return J("[...document.querySelectorAll('button[aria-pressed]')].map(b=>b.innerText.replace(/\\s+/g,' ').trim()+(b.getAttribute('aria-pressed')==='true'?'*':''))")
def nomes(): return J("[...document.querySelectorAll('[role=table]')[0].querySelectorAll('[role=row].g2ed')].map(r=>r.querySelector('b').innerText)")
def conta(): return J("(document.body.innerText.match(/(\\d+) de (\\d+)/)||[]).slice(1,3).join('/')")
def barra(): return J("document.querySelectorAll('[role=table]')[0].parentElement.parentElement.innerText.replace(/\\s+/g,' ').slice(0,200)")
try:
    t.c.size(1440,1000); t.goto('CD-04.dc.html')
    t.clk('Operadores 4'); lg('ope:',nomes(),conta(),'| barra:',barra()); lg('chips',chips())
    t.clk('Limpar filtros'); lg('limpar:',conta(),chips())
    t.clk('Almoxarifes 1'); lg('alm:',nomes()); t.clk('Agrônomos 1'); lg('agr:',nomes()); t.clk('Irrigantes 1'); lg('irr:',nomes()); t.clk('Irrigantes 1'); lg('toggle off:',conta(),chips())
    # estado → verde
    t.openrow(0,'Lucas'); t.fset('v31','2027-08-15'); t.btn('Salvar'); time.sleep(.2)
    t.openrow(0,'Beto'); t.fset('v31','2027-09-01'); t.btn('Salvar'); time.sleep(.2)
    t.openrow(0,'Marcos'); t.fset('v31','2027-09-30'); t.btn('Salvar'); time.sleep(.2)
    lg('st verde:',st(),chips())
    t.clk(st().split(' | ')[0]); time.sleep(.2); lg('clicar verde:',conta(),'| barra:',barra(),'| chips',chips())
    t.clk('Limpar filtros'); lg('limpar:',conta())
    # inativar Nilton → contagem
    t.openrow(0,'Nilton'); t.fset('sit','Inativa'); t.btn('Salvar'); time.sleep(.2); lg('inativa:',t.toast(),'| linha',t.rowtxt(0,'Nilton'),'| chips',chips(),'| equipe',t.rowtxt(1,'Campo 2'))
    # equipe: mudar calendário do Campo 1 → ajuda da pessoa
    t.openrow(1,'Campo 1'); t.fset('cal','seg–sex · 08–18h'); t.btn('Salvar'); time.sleep(.2); lg('eq cal:',t.toast())
    t.openrow(0,'Paula'); lg('help equipe Paula:',J("(()=>{const l=[...document.querySelectorAll('aside[role=dialog] label[for]')].find(x=>x.innerText.trim()==='Equipe'); return l?l.parentElement.innerText.replace(/\\s+/g,' '):'';})()")); t.cancel()
    # renomear equipe
    t.openrow(1,'Campo 1'); t.fset('nome','Campo Norte'); t.btn('Salvar'); time.sleep(.2); lg('eq ren:',t.toast()); lg('Paula:',t.rowtxt(0,'Paula'))
    # excluir equipe sem pessoas: cria e exclui
    t.clk('Nova equipe'); t.fset('nome','Temporária'); t.fset('lider','Rui'); t.btn('Salvar'); time.sleep(.2); lg('nova eq:',t.toast(),t.alerts())
    lg('del eq:',J("(()=>{const r=[...document.querySelectorAll('[role=table]')[1].querySelectorAll('[role=row]')].find(r=>r.innerText.indexOf('Temporária')>=0); return r?[...r.querySelectorAll('button')].map(b=>(b.getAttribute('aria-label')||b.innerText).trim()):null;})()"))
    lg('erros:',t.errs())
finally:
    t.fim()
