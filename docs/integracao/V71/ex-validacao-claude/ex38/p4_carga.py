# Carga do PCP (visão "carga" da O.S.), nas duas fazendas; cadastro de pessoas CD-04 e conjuntos CD-03
from base import *
from comp_lib import troca_visao
SETV = """((sel,val)=>{const i=document.querySelector(sel); if(!i) return 'NAO ACHEI'; const P=i.tagName==='SELECT'?HTMLSelectElement.prototype:HTMLInputElement.prototype; Object.getOwnPropertyDescriptor(P,'value').set.call(i,val); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true})); return 'ok';})"""
s = S(1440, 1400)
try:
    s.reset('Caio'); s.go('OS.dc.html', 1.5)
    print('visao', troca_visao(s.J, 'carga'))
    time.sleep(.8)
    t = s.J("(()=>{const m=document.querySelector('[aria-label=\"Alocação de recursos na semana\"]'); return (m?m.innerText:'SEM TABELA')})()")
    s.save('carga_santarita.txt', t); s.shot('carga_santarita.png')
    print(s.J("document.body.innerText.match(/[^\\n]*mesmo recurso em duas ordens[^\\n]*/g)"))
    print(s.J("document.body.innerText.match(/Nenhuma ordem[^\\n]*/g)"))
    print(s.J(f"({SETV})('select[aria-label=\"Filtrar por fazenda\"]','Lagoa Grande')")); time.sleep(.8)
    t2 = s.J("(()=>{const m=document.querySelector('[aria-label=\"Alocação de recursos na semana\"]'); return (m?m.innerText:'SEM TABELA')})()")
    s.save('carga_lagoa.txt', t2); s.shot('carga_lagoa.png')
    print('LAGOA:', s.J("document.body.innerText.match(/Nenhuma ordem[^\\n]*|[^\\n]*mesmo recurso[^\\n]*/g)"))
    for p in ['CD-04', 'CD-03']:
        s.reset('Ana'); s.go(p + '.dc.html', 1.5); s.save(p + '.txt', s.body())
    print('ERRS', s.J("window.__errs"))
finally:
    s.fim()
