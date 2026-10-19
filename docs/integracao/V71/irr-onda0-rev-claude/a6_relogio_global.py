# A6 (revisor): o relógio simulado é global; iniciar a OS-0419 (janela 20:00) leva "agora" a 20:02 para todas as ordens.
# Depois, a OS-0423 (liberada para 15:00–17:00) inicia às 20:04, fora da janela que a prontidão conferiu. Uso: python3 a6_relogio_global.py <gen37>
import sys, os, time, json
G = sys.argv[1]; sys.path.insert(0, G)
from comp_lib import Chrome, servir
R = os.environ.get('RENDER_DIR') or os.path.join(G, '_render')
p, srv = servir(R); c = Chrome(); J = c.js; U = lambda pg: f'http://127.0.0.1:{p}/{pg}'
DLG = "[...document.querySelectorAll('aside[role=dialog]')].find(x=>x.getBoundingClientRect().width>1)"
def clk(t, dlg=False):
    r = J(f"(()=>{{const R={'('+DLG+')' if dlg else 'document'}; const b=[...R.querySelectorAll('button')].find(b=>b.innerText.replace(/\\s+/g,' ').trim()==={json.dumps(t)}); if(!b) return false; b.click(); return true;}})()"); time.sleep(.9); return r
def toast(): time.sleep(.3); return J("((document.querySelector('.g2toast')||{}).innerText||'').trim()")
def S(): return json.loads(J("localStorage.getItem('talhao-os-irrigacao-v1')") or 'null')
try:
    c.aparelho(1440, 900); c.goto(U('Main.dc.html'), .3); J("localStorage.clear();sessionStorage.clear();1")
    c.goto(U('IR-03det.dc.html#OS-0423:conflito'), 1.6); clk('Aplicar janela', True); t1 = toast(); s = S()
    print('1 OS-0423:', t1, '· janela', [(q['ini'], q['dur']) for q in s['ordens']['OS-0423']['passadas']], '· agora', s['agora'])
    c.goto(U('Main.dc.html'), .2); c.goto(U('IR-03det.dc.html#OS-0419'), 1.6); clk('Iniciar irrigação'); t2 = toast(); s = S()
    print('2 OS-0419:', t2, '· agora', s['agora'])
    c.goto(U('Main.dc.html'), .2); c.goto(U('IR-03det.dc.html#OS-0423'), 1.6); clk('Iniciar irrigação'); t3 = toast(); s = S()
    o = s['ordens']['OS-0423']; pz = o['passadas'][0]
    print('3 OS-0423:', t3, '· janela liberada', pz['ini'], '→', pz['ini'] + pz['dur'], '· início real', pz.get('iniReal'), '· agora', s['agora'])
    print('RESULTADO A6:', 'início fora da janela liberada' if pz.get('iniReal', 0) > pz['ini'] + pz['dur'] else 'início dentro da janela')
finally:
    c.close(); srv.terminate()
