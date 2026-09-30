# Verificador CD-04: líder da equipe no formulário — caso base, após renomear a pessoa e após inativá-la (foto).
import sys, os, time, json
HERE=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0,HERE)
from cada_lib import T
t=T(); J=t.J; t.c.size(1440,1000)
try:
    t.goto('CD-04.dc.html')
    t.openrow(1,'Campo 2'); print('base Campo 2 lider:',t.fv('lider')); t.cancel()
    t.openrow(0,'Lucas'); t.fset('sit','Inativa'); t.btn('Salvar'); time.sleep(.3)
    t.openrow(1,'Campo 2'); print('Lucas inativo -> Campo 2 lider no form:',t.fv('lider'),'| linha:',t.anyrow(1,'Campo 2'))
    t.shot('ver_cap_c4_lider.png')
    t.fset('cal','seg–sex · 07–17h'); t.btn('Salvar'); time.sleep(.3); print('após salvar (só mudou calendário):',t.anyrow(1,'Campo 2'),'| toast:',t.toast())
finally:
    t.fim()
