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
    J("window.__errs=[]; window.addEventListener('error',e=>window.__errs.push(String(e.message)));")
    say('4 nova safra:', clk('Nova safra')); fset('Nome da safra', 'Safra teste 27/28'); fset('Período', 'set/2027 – ago/2028'); clk('Salvar', 'aside[role=dialog]'); say('4 toast:', toast())
    say('4 contexto:', J("document.body.innerText.slice(0,120).replace(/\\s+/g,' ')"))
    etapa(3); say('4 etapa 3 nova:', row('Plantadeira')); rowclick('Plantadeira'); say('4 painel:', panel()[:160])
    fset('Pessoas na equipe', '4'); clk('Salvar', 'aside[role=dialog]'); say('4 salvar:', toast(), '|', row('Plantadeira'))
    say('4 colheita sem cultivos:', row('Colhedora'), '|', row('Derriçadeiras'))
    etapa(4); say('4 k4:', J("document.querySelector('main').innerText.slice(0,400).replace(/\\s+/g,' ')"))
    abrir('Safra 2026/27'); etapa(3); say('4 2026/27 depois:', row('Plantadeira'))
    abrir('Safrinha 2027'); etapa(3); say('4 Safrinha depois:', row('Plantadeira'))
    abrir('Safra teste'); etapa(3); say('4 volta à nova:', row('Plantadeira'))
    say('erros JS:', J("window.__errs"))
finally:
    c.close(); srv.terminate()
