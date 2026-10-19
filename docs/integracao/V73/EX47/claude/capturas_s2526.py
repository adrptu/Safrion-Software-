# -*- coding: utf-8 -*-
"""EX47 · revisão Claude: capturas da g_cult_S2526 (safra encerrada: menu_linha sem dele) a 1440. RENDER_DIR e PREFIXO escolhem o _render e o nome.
1) sem ação na linha (dados sintéticos); 2) com a ação injetada no estado (T1 com plano de Milho) e o ⋯ aberto."""
import os, sys, time, json
GEN = os.environ.get('GEN37') or os.getcwd(); sys.path.insert(0, GEN)
from comp_lib import Chrome, servir
R = os.environ.get('RENDER_DIR') or os.path.join(GEN, '_render'); PRE = os.environ.get('PREFIXO', 'head')
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'capturas')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
p, srv = servir(R); c = Chrome(); J = c.js
INJ = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sonda_rmenu_navegador.py'), encoding='utf-8').read()
INJ = INJ[INJ.index('INJ = r"""') + 10:]; INJ = INJ[:INJ.index('"""')]
try:
    c.aparelho(1440, 1000, 1, False)
    c.goto(f'http://127.0.0.1:{p}/Main.dc.html', .3); J("localStorage.clear();sessionStorage.clear()")
    c.goto(f'http://127.0.0.1:{p}/SAF.dc.html#saf=S2526&etapa=2', .6)
    for _ in range(60):
        if J("document.querySelectorAll('[data-g2g=g_cult_S2526] [role=row]').length>=4"): break
        time.sleep(.15)
    J("document.querySelector('[data-g2g=g_cult_S2526]').scrollIntoView({block:'start'})"); time.sleep(.3)
    c.shot(os.path.join(OUT, f'{PRE}_S2526_1440_sem_acao.png'))
    print('cultura injetada:', J(INJ)); time.sleep(.6)
    b = J("!!document.querySelector('[data-g2g=g_cult_S2526] [role=row][data-rid=e1] button.g2mais')")
    if b: J("document.querySelector('[data-g2g=g_cult_S2526] [role=row][data-rid=e1] button.g2mais').click()"); time.sleep(.4)
    txt = J("(()=>{const r=document.querySelector('[data-g2g=g_cult_S2526] [role=row][data-rid=e1]'); return r?r.innerText.replace(/\\s+/g,' '):'';})()")
    print('⋯ em T1:', b, '· texto da linha T1:', txt)
    c.shot(os.path.join(OUT, f'{PRE}_S2526_1440_acao_injetada.png'))
finally:
    c.close(); srv.terminate()
