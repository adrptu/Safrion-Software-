# -*- coding: utf-8 -*-
"""Verificador (rodada 4) · roda o T06 de testes_pedido.py sem gravar resultado.json (evidência vai para _probe)."""
import sys, os, time, subprocess
P = os.path.dirname(os.path.abspath(__file__)); GEN = os.path.dirname(P); sys.path.insert(0, GEN)
import testes_pedido as TP
from cdp import Chrome
from journeys import free
def foto(s, nome):
    s.n += 1; s.c.shot(os.path.join(P, f'ver_est_r4_t06_{s.n:02d}_{nome}.png')); s.passos.append(dict(passo='Evidência', ok=True, obs=nome))
TP.T.foto = foto
p = free(); srv = subprocess.Popen(['python3', '-m', 'http.server', str(p), '--bind', '127.0.0.1', '--directory', TP.R], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(.8)
S = time.time()
try:
    c = Chrome(port=free()); c.size(1440, 1000); t = TP.T(c, f'http://127.0.0.1:{p}/', 'T06')
    try: TP.t06(t)
    except Exception as ex: t.log('Execução', False, f'erro: {ex}')
    finally: c.close()
    for x in t.passos: print(('  ok ' if x['ok'] else '  X  ') + x['passo'] + (' → ' + x['obs'] if x['obs'] and not x['ok'] else ''))
    print('T06', 'PASSOU' if t.ok else 'FALHOU', f'{time.time()-S:.1f}s')
finally: srv.terminate()
