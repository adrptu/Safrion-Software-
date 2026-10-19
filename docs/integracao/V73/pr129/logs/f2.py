# F2: meta sem versão mostra "Nenhuma versão ainda" no histórico do editor
import os, sys, time, json
G = sys.argv[1]; sys.path.insert(0, G)
from comp_lib import Chrome, servir
port, srv = servir(os.path.join(G, '_render')); c = Chrome(); J = c.js
U = lambda p: f'http://127.0.0.1:{port}/{p}'
try:
    c.aparelho(1440, 900); c.goto(U('Main.dc.html'), .3); J("localStorage.clear(); sessionStorage.clear(); 1")
    c.goto(U('CF-06.dc.html'), 1.8)
    r = J("(()=>{ const r=[...document.querySelectorAll('[data-g2g=g_metas] [role=row][data-rid]')].find(r=>r.getAttribute('data-rid')==='venda-referencia'); if(!r) return 'sem linha'; (r.querySelector('.g2pw')||r.querySelector('[role=cell]')||r).click(); return 'ok'; })()")
    time.sleep(.6)
    d = J("(()=>{ const a=document.querySelector('aside[role=dialog]'); return a?a.innerText.replace(/\\s+/g,' ').trim():''; })()")
    i = d.find('Vers'); print('abre:', r); print('trecho:', d[i:i+160] if i >= 0 else d[:300])
    print('RESULTADO', 'OK' if 'Nenhuma versão ainda' in d else 'FALHA')
    c.shot(os.path.join(sys.argv[2], 'cf06_sem_versao_1440.png'))
finally:
    c.close(); srv.terminate()
