# Verificador: remover o chip do filtro do estado (×) em CD-03 e CD-04.
import sys, os, time, json
HERE=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0,HERE)
from cada_lib import T
t=T(); J=t.J; t.c.size(1440,1000)
def conta(): return J("(document.body.innerText.match(/(\\d+) de (\\d+)/)||[]).slice(0,1).join('')")
X="""((txt)=>{const els=[...document.querySelectorAll('*')].filter(e=>e.children.length<=2&&e.innerText&&e.innerText.indexOf(txt)>=0&&e.innerText.length<txt.length+6); const c=els[els.length-1]; if(!c) return 'sem chip'; const b=c.querySelector('button')||c.parentElement.querySelector('button'); if(!b) return 'sem botão:'+c.outerHTML.slice(0,300); b.click(); return 'ok '+(b.getAttribute('aria-label')||b.innerText);})"""
try:
    t.goto('CD-03.dc.html'); t.clk('1 máquina em manutenção'); print('c3 filtrado:',conta())
    print(J(f"({X})('Em manutenção ou calibração a resolver')")); time.sleep(.3); print('c3 após ×:',conta())
    t.goto('CD-04.dc.html'); t.clk('2 não alocáveis'); print('c4 filtrado:',conta())
    print(J(f"({X})('Habilitação a resolver')")); time.sleep(.3); print('c4 após ×:',conta())
finally:
    t.fim()
