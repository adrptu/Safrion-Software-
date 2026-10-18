# Sonda do nav_modulos N3: tempo até os cartões do MOD-AGR existirem e até o foco voltar ao cartão aberto, depois de "‹ Agrícola".
# Uso: python3 -B sonda_n3.py <gen37> [repetições]. Mede por condição (a cada 50 ms, até 10 s), sem espera fixa.
import os, sys, time
G = os.path.abspath(sys.argv[1]); N = int(sys.argv[2]) if len(sys.argv) > 2 else 3; sys.path.insert(0, G)
os.environ.setdefault('CDP_GL', '1')
from comp_lib import Chrome, servir
p, srv = servir(os.path.join(G, '_render')); c = Chrome(); J = c.js
U = lambda pg: f'http://127.0.0.1:{p}/{pg}'
def ate(expr, lim=10.0):
    t0 = time.time()
    while time.time() - t0 < lim:
        if J(expr): return round(time.time() - t0, 2)
        time.sleep(.05)
    return None
try:
    c.aparelho(1440, 900, 1, False)
    for i in range(N):
        c.goto(U('MOD-AGR.dc.html'), .2); t_ini = ate("document.querySelectorAll('a.mod-cartao').length>0")
        J("[...document.querySelectorAll('a.mod-cartao')].find(a=>a.innerText.trim()==='Ordens de serviço').click()")
        t_os = ate("location.pathname.endsWith('/OS.dc.html')&&!!document.querySelector('a.volta37')")
        J("document.querySelector('a.volta37').click()"); t0 = time.time()
        t_nav = ate("location.pathname.endsWith('/MOD-AGR.dc.html')")
        t_card = ate("document.querySelectorAll('a.mod-cartao').length>0")
        t_foco = ate("(document.activeElement&&document.activeElement.getAttribute('href'))==='OS.dc.html'")
        print(f'{i}: entrada {t_ini}s · O.S. {t_os}s · volta: url {t_nav}s, cartões {t_card}s, foco {t_foco}s (total {round(time.time()-t0,2)}s)', flush=True)
finally:
    c.close(); srv.terminate()
