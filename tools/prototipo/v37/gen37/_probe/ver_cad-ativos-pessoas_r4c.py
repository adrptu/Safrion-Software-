# Verificador rodada 4 · sonda C: CD-03 painel lateral em 1440x1000 (rolagem até Salvar) e cadastro de Armazenagem sem custo
import sys, os, time, json
HERE=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0,HERE); os.chdir(HERE)
from cada_lib import T
T0=time.time()
t=T(); J=t.J
def lg(*a): print(round(time.time()-T0,1),*a, flush=True)
try:
    t.c.size(1440,1000); t.goto('CD-03.dc.html'); lg('carregou')
    t.clk('Cadastrar máquina ou instalação'); t.fset('classe','Pulverizador')
    lg('aside:',J("(()=>{const a=document.querySelector('aside[role=dialog]'); const cs=getComputedStyle(a); const r=a.getBoundingClientRect(); const chain=[]; let e=a; while(e){const s=getComputedStyle(e); chain.push(e.tagName+'.'+(s.position)+'.'+s.overflowY+'.'+e.scrollHeight+'/'+e.clientHeight); e=e.parentElement;} const b=[...a.querySelectorAll('button')].find(b=>b.innerText.trim()==='Salvar'); const br=b.getBoundingClientRect(); return {pos:cs.position,ov:cs.overflowY,sh:a.scrollHeight,ch:a.clientHeight,top:r.top,h:r.height,salvar:[br.top,br.bottom,innerHeight],chain:chain,docH:document.documentElement.scrollHeight};})()"))
    t.shot('ver_cad-ativos-pessoas_r4c_form.png')
    # rola a página até o fim e mede de novo
    J("window.scrollTo(0,99999)"); time.sleep(.3)
    lg('apos rolar janela:',J("(()=>{const a=document.querySelector('aside[role=dialog]'); const b=[...a.querySelectorAll('button')].find(b=>b.innerText.trim()==='Salvar'); const br=b.getBoundingClientRect(); return [scrollY,br.top,br.bottom,innerHeight];})()"))
    J("(()=>{const a=document.querySelector('aside[role=dialog]'); a.scrollTop=99999; [...a.querySelectorAll('*')].forEach(e=>e.scrollTop=99999);})()"); time.sleep(.3)
    lg('apos rolar aside:',J("(()=>{const a=document.querySelector('aside[role=dialog]'); const b=[...a.querySelectorAll('button')].find(b=>b.innerText.trim()==='Salvar'); const br=b.getBoundingClientRect(); return [a.scrollTop,br.top,br.bottom,innerHeight];})()"))
    t.shot('ver_cad-ativos-pessoas_r4c_form_rolado.png')
    t.cancel(); lg('cancel')
finally:
    t.fim()
