# -*- coding: utf-8 -*-
"""Espera por condição do cdp.py (ACELERA, 13/10/2026) · teste de navegador, página própria servida em 127.0.0.1 (sem dados).
Oráculo: o relógio das esperas fixas. Entre duas ações do teste, a página tem de estar no mesmo estado que teria com as esperas
fixas (time.sleep do teto), e a soma das esperas nunca passa da soma dos tetos. Roda as duas esperas no mesmo arquivo: a fixa
(SAFRION_ESPERA=fixa, num processo filho) confirma o oráculo; a por condição tem de dar os mesmos estados.
 E1 aviso de 3,5 s e quatro esperas de 1 s: visível depois de 1, 2 e 3 s; some antes da quarta ação (4 s). Defeito protegido:
    sem o crédito, cada espera voltava em ~0,3 s e o aviso continuava na tela na quarta ação (solo_os_test, AC-SOLO-14, 13/10).
 E2 crédito acumulado (três esperas de 1 s numa página parada) e aviso NOVO de 1,5 s: visível depois de 1 s, some depois de 2 s.
    Defeito protegido: crédito aplicado a timer criado depois dele adiantaria a página (o aviso sumiria antes da leitura de 1 s).
 E3 resposta de rede de 1,5 s: ausente depois de 1 s, presente depois de 2 s.
 E4 a soma do tempo real das esperas (E1 a E3) não passa da soma dos tetos.
 E5 só por condição: goto que muda só a âncora volta antes do goto fixo (3,1 s) e sem esperar documento novo.
Uso: env CHROME_BIN=… flock /tmp/cdpX.lock env CDP_GL=1 timeout 300 python3 cdp_espera_test.py"""
import os, sys, time, json, threading, subprocess, http.server, socketserver, urllib.parse
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import cdp
from cdp import Chrome
from journeys import free

PAG = ("<!doctype html><html><head><meta charset=utf-8><title>espera</title></head><body>"
       "<p>Página de teste da espera por condição do cdp.py. Só texto sintético, sem dados.</p>"
       "<div id=av></div><div id=rd></div><script>"
       "window.aviso=function(ms){ var e=document.getElementById('av'); e.textContent='AVISO'; setTimeout(function(){ e.textContent=''; }, ms); return 'ok'; };"
       "window.busca=function(ms){ fetch('/lento?ms='+ms).then(function(r){ return r.text(); }).then(function(t){ document.getElementById('rd').textContent=t; }); return 'ok'; };"
       "</script></body></html>").encode()


class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        if u.path == '/lento':
            cdp._dormir(int(urllib.parse.parse_qs(u.query).get('ms', ['0'])[0]) / 1000.0)   # demora real do servidor
            corpo, tipo = b'RESPOSTA', 'text/plain'
        else:
            corpo, tipo = PAG, 'text/html; charset=utf-8'
        self.send_response(200); self.send_header('Content-Type', tipo); self.send_header('Content-Length', str(len(corpo)))
        self.send_header('Cache-Control', 'no-store'); self.end_headers(); self.wfile.write(corpo)

    def log_message(self, *a): pass


class S(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True


def cenarios():
    """Roda E1–E5 e devolve [(nome, estados observados, tempo real das esperas, soma dos tetos)]."""
    srv = S(('127.0.0.1', free()), H); threading.Thread(target=srv.serve_forever, daemon=True).start()
    url = f'http://127.0.0.1:{srv.server_address[1]}/p.html'
    c = Chrome(port=free()); J = c.js; res = []; real = [0.0]; tetos = [0.0]

    def espera(x):   # o time.sleep(x) de um teste, x ≥ 1 s fora de laço (por condição: settle(0,3, x))
        t = time.monotonic(); time.sleep(x); real[0] += time.monotonic() - t; tetos[0] += x

    def le(): return [J("document.getElementById('av').textContent"), J("document.getElementById('rd').textContent")]
    try:
        c.goto(url)
        cdp._CRED[0] = 0.0; c._poe_credito()   # cada cenário começa sem crédito (o crédito é por processo)
        J('aviso(3500)'); obs = []
        for _ in range(4): espera(1.0); obs.append(le()[0])
        res.append(('E1', obs))
        cdp._CRED[0] = 0.0; c._poe_credito()
        for _ in range(3): espera(1.0)
        J('aviso(1500)'); obs = []
        for _ in range(2): espera(1.0); obs.append(le()[0])
        res.append(('E2', obs))
        cdp._CRED[0] = 0.0; c._poe_credito()
        J('busca(1500)'); obs = []
        for _ in range(2): espera(1.0); obs.append(le()[1])
        res.append(('E3', obs))
        res.append(('E4', [real[0] <= tetos[0] + 0.25, round(real[0], 2), round(tetos[0], 2)]))
        t = time.monotonic(); c.goto(url + '#outra'); dt = time.monotonic() - t
        res.append(('E5', [dt, J('location.hash')]))
    finally:
        c.close(); srv.shutdown()
    return res


if __name__ == '__main__':
    if '--filho' in sys.argv:
        print('JSON ' + json.dumps(cenarios())); sys.exit(0)
    OK, FAIL = [], []

    def chk(n, cond, info=''):
        (OK if cond else FAIL).append(n); print(('OK  ' if cond else 'FALHOU ') + n + ' · ' + str(info)[:300])
    env = dict(os.environ, SAFRION_ESPERA='fixa')
    p = subprocess.run([sys.executable, os.path.abspath(__file__), '--filho'], env=env, capture_output=True, text=True, timeout=240)
    fixa = dict((n, v) for n, v in json.loads([l for l in p.stdout.splitlines() if l.startswith('JSON ')][-1][5:])) if p.returncode == 0 else {}
    cond = dict(cenarios()) if cdp.CONDICAO else {}
    esperado = {'E1': ['AVISO', 'AVISO', 'AVISO', ''], 'E2': ['AVISO', ''], 'E3': ['', 'RESPOSTA']}
    chk('oráculo: com as esperas fixas, E1/E2/E3 dão os estados do relógio fixo', all(fixa.get(k) == v for k, v in esperado.items()), [fixa, p.stderr[-300:]])
    if not cdp.CONDICAO:
        print('(SAFRION_ESPERA=fixa: só o oráculo)')
    else:
        chk('E1 aviso de 3,5 s: visível depois de 1, 2 e 3 s e some antes da quarta ação (4 s), como com as esperas fixas', cond.get('E1') == esperado['E1'], cond.get('E1'))
        chk('E2 crédito acumulado e aviso novo de 1,5 s: visível depois de 1 s (o crédito não adianta timer criado depois dele), some depois de 2 s', cond.get('E2') == esperado['E2'], cond.get('E2'))
        chk('E3 resposta de rede de 1,5 s: ausente depois de 1 s, presente depois de 2 s', cond.get('E3') == esperado['E3'], cond.get('E3'))
        chk('E4 a soma do tempo real das esperas não passa da soma dos tetos (folga de 0,25 s para as chamadas)', (cond.get('E4') or [False])[0], cond.get('E4'))
        chk('E5 goto que muda só a âncora volta antes do goto fixo (3,1 s), sem esperar documento novo', cond.get('E5') and cond['E5'][0] < 3.1 and cond['E5'][1] == '#outra', cond.get('E5'))
    print(f'RESULTADO: {len(OK)} ok · {len(FAIL)} falhas' + (' · FALHAS: ' + '; '.join(FAIL) if FAIL else ''))
    sys.exit(1 if FAIL else 0)
