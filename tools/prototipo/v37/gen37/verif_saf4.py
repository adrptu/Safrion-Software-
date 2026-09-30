# -*- coding: utf-8 -*-
"""Verificação independente (Chrome) · planos-safra-03/04/06: busca, safra nova, safra encerrada, ordenação de datas."""
import sys, os, time, subprocess, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cdp import Chrome
from journeys import free
import verif_lib as L
from verif_lib import say, clk, toast, panel, etapa, abrir, row, rowclick, fset, LARG, CUSTOH, total_oper, num
HERE = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(HERE, '_render')
SHOT = sys.argv[1] if len(sys.argv) > 1 else HERE
p = free(); srv = subprocess.Popen(['python3', '-m', 'http.server', str(p), '--bind', '127.0.0.1', '--directory', R], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)
c = Chrome(port=free()); J = c.js; L.setup(c)
try:
    c.size(1440, 1000); c.goto(f'http://127.0.0.1:{p}/SAF.dc.html', wait=1.3)
    abrir('Safra 2026/27'); etapa(6); say('6 recolhida:', J(LARG)); clk('Expandir tudo'); say('6 expandida:', J(LARG))
    W = r"""(()=>{const t=[...document.querySelectorAll('[role=table]')].find(t=>t.offsetParent); const hs=[...t.querySelectorAll('[role=columnheader]')]; return hs.map(h=>h.innerText.replace(/\s+/g,' ').replace(/ ⇅.*$/,'').trim()+':'+Math.round(h.getBoundingClientRect().width));})()"""
    say('6 colunas expandida:', J(W))
    c.shot(os.path.join(SHOT, 'verif_e6_exp.png'))
finally:
    c.close(); srv.terminate()
