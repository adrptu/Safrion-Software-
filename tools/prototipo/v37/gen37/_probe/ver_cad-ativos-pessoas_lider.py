# Verificador CD-04: renomear pessoa que é líder de equipe; toast com ponto duplo.
import sys, os, time, json
HERE=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0,HERE)
from cada_lib import T
t=T(); J=t.J; t.c.size(1440,1000)
try:
    t.goto('CD-04.dc.html')
    t.openrow(0,'Ana'); t.btn('Salvar'); time.sleep(.3); print('toast Ana:',repr(t.toast()))
    t.openrow(0,'Marcos'); t.fset('nome','Marcos Silva'); t.btn('Salvar'); time.sleep(.3); print('toast:',t.toast())
    print('Campo 1 row:',t.anyrow(1,'Campo 1'))
    t.openrow(1,'Campo 1'); print('lider v:',t.fv('lider'),'opts:',t.fopts('lider')); t.btn('Salvar'); time.sleep(.3); print('salvar equipe: aberto',t.isopen(),'alerts:',t.alerts(),'toast:',t.toast())
    print('Campo 1 row depois:',t.anyrow(1,'Campo 1'))
finally:
    t.fim()
