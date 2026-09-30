# Verificador: o erro "reading 'g2toast'" também ocorre fora da frente (CD-05)? E o aviso some sozinho em CD-04?
import sys, os, time, json
HERE=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0,HERE)
from cada_lib import T
t=T(); J=t.J; t.c.size(1440,1000)
try:
    for f in ('CD-05.dc.html','CD-04.dc.html'):
        t.goto(f); r=J("document.querySelectorAll('.g2ed').length"); J("document.querySelectorAll('.g2ed')[0].querySelector('[role=cell]').click()"); time.sleep(.4); t.btn('Salvar'); time.sleep(.4)
        print(f,'toast:',t.toast()[:80],'motor:',t.errs_motor(),'outros:',t.errs()[:200])
        time.sleep(4.5); print('  após 4,5 s toast:',t.toast()[:60])
finally:
    t.fim()
