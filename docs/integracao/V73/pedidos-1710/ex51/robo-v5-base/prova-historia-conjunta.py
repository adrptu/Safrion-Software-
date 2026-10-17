# -*- coding: utf-8 -*-
"""Prova do motivo do modo isolado: num quadro (iframe), history.back() anda na história conjunta da aba e pode voltar OUTRO quadro.
Uso: python3 -I prova-historia-conjunta.py <trabalho já preparado>
Monta dois quadros A e B na mesma página, navega A (a=1, a=2) e B (b=1, b=2), chama A.contentWindow.history.back() e mostra quem voltou.
Saída de 17/10/2026: antes ['?a=2', '?b=2', 4] · depois de A.history.back() ['?a=2', '?b=1'] (voltou o B, não o A)."""
import importlib.util, os, shutil, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sp = importlib.util.spec_from_file_location('rodar', os.path.join(AQUI, 'rodar.py'))
m = importlib.util.module_from_spec(sp)
sp.loader.exec_module(m)
W = os.path.abspath(sys.argv[1])
m.esperar_vaga()
srv = m.Servidores()
c = None
try:
    c = m.Chrome(m.CHROME)
    base = srv.subir(W, m.ROBO, os.path.join(W, 'robot3', 'screens.json'), os.path.join(W, 'saida-prova'))
    a = c.abas[0]
    a.goto(base + '/robot3/vazio.html', espera_corpo=False)
    a.js("""(async () => { const mk = () => { const f = document.createElement('iframe'); document.body.appendChild(f); return f; };
      window.A = mk(); window.B = mk(); const go = (f, u) => new Promise(r => { f.onload = r; f.src = u; });
      await go(A, '/v3/Main.dc.html?a=1'); await go(B, '/v3/Main.dc.html?b=1'); await go(A, '/v3/Main.dc.html?a=2'); await go(B, '/v3/Main.dc.html?b=2'); return 1; })()""")
    print('antes', a.js("[A.contentWindow.location.search, B.contentWindow.location.search, history.length]"))
    a.js("A.contentWindow.history.back(); 1")
    a.pump(1.5)
    print('depois de A.history.back()', a.js("[A.contentWindow.location.search, B.contentWindow.location.search]"))
finally:
    if c:
        c.close()
    srv.parar()
    shutil.rmtree(os.path.join(W, 'saida-prova'), ignore_errors=True)
