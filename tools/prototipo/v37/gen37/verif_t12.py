# -*- coding: utf-8 -*-
"""Roda só o T12 de testes_pedido.py sem gravar resultado.json (verificador)."""
import sys, os, time, subprocess
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import testes_pedido as TP
from cdp import Chrome
from journeys import free
p=free(); srv=subprocess.Popen(['python3','-m','http.server',str(p),'--bind','127.0.0.1','--directory',TP.R],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(.8)
c=Chrome(port=free()); c.size(1440,1000); t=TP.T(c,f'http://127.0.0.1:{p}/','T12')
try: TP.t12(t)
finally: c.close(); srv.terminate()
print('T12', 'PASSOU' if t.ok else 'FALHOU'); [print('  ', 'ok' if x['ok'] else 'X', x['passo'], '→', str(x.get('obs',''))[:300]) for x in t.passos]
