# -*- coding: utf-8 -*-
"""EX-26 · texto visível dos painéis e das telas com indicadores (menu e ocultas), para a busca de cada indicador por módulo (executado).
Saída: out/ex26/<tela>.txt e out/ex26/IN-04_<função>.txt; depois p11_ex26_busca.py procura os indicadores nesses textos."""
import os, sys, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e40lib import S, OUT, G
sys.path.insert(0, G)
import ui37
D = os.path.join(OUT, 'ex26')
MENU = ['PAGR', 'PMAN', 'PSUP', 'PCOM', 'GE-02', 'GE-03', 'OS', 'AG-01', 'AG-02', 'PA', 'SAF', 'IR-01', 'COLH', 'CARGA', 'BEN', 'PROD', 'VEN', 'EXPED', 'IV', 'IC', 'EST', 'CMP']
OCULTAS = ['GE-01', 'GE-04', 'GE-05', 'GE-06', 'GE-06det', 'GE-07', 'AG-03', 'AG-04', 'AG-06', 'IR-02', 'IR-03', 'IR-04', 'CO-01', 'CO-02', 'CO-03', 'CO-04', 'CO-05', 'CO-06', 'CO-07',
           'LO-01', 'LO-03', 'LO-04', 'SU-01', 'SU-02', 'SU-04', 'SU-05', 'SU-08', 'SU-09', 'PL-01', 'PL-02', 'PL-03', 'PL-04', 'IN-01', 'IN-02', 'CA-01', 'CA-02', 'CA-04', 'VE-01', 'VE-03', 'VE-06']
s = S(1440, 1400); s.reset('Ana')
idx = {}
for f in MENU + OCULTAS:
    s.go(f + '.dc.html', espera=1.0); time.sleep(.4)
    t = s.body(); open(os.path.join(D, f + '.txt'), 'w', encoding='utf-8').write(t)
    idx[f] = dict(oculta=ui37.oculto(f + '.dc.html'), chars=len(t), h1=(s.J("(document.querySelector('h1')||{}).innerText") or '')[:60])
    print(f, idx[f], flush=True)
for vis in ('semordem', 'ordens', 'ativos', 'planos'):
    s.go(f'MA.dc.html#vis={vis}', espera=1.4); time.sleep(.4)
    open(os.path.join(D, f'MA_{vis}.txt'), 'w', encoding='utf-8').write(s.body()); idx[f'MA_{vis}'] = dict(oculta=False)
s.go('MA.dc.html#ativo=a01', espera=1.8); time.sleep(.6)
# abre o bloco "Custo e desempenho" do ativo (fica recolhido por padrão)
s.J("(()=>{const b=[...document.querySelectorAll('button,[role=button],summary')].find(e=>e.getClientRects().length&&/Custo e desempenho/.test(e.innerText)); if(b) b.click(); return !!b;})()"); time.sleep(.6)
open(os.path.join(D, 'MA_ativo_a01.txt'), 'w', encoding='utf-8').write(s.body()); idx['MA_ativo_a01'] = dict(oculta=False)
# Mapa: cada função da barra (MAP-03), o texto da faixa
s.go('IN-04.dc.html', espera=2.5); time.sleep(1.0)
fs = s.J("[...document.querySelectorAll('[role=tab]')].filter(e=>e.getClientRects().length).map(e=>(e.innerText||e.getAttribute('aria-label')||'').replace(/\\s+/g,' ').trim())")
print('funções do mapa:', fs, flush=True)
for i, nome in enumerate(fs or []):
    s.J(f"(()=>{{const t=[...document.querySelectorAll('[role=tab]')].filter(e=>e.getClientRects().length)[{i}]; if(t) t.click();}})()"); time.sleep(1.2)
    t = s.body(); open(os.path.join(D, f'IN-04_{i}_{nome[:20].replace(" ", "_").replace("/", "-")}.txt'), 'w', encoding='utf-8').write(t)
    idx[f'IN-04_{i}'] = dict(oculta=False, funcao=nome)
json.dump(idx, open(os.path.join(D, '_indice.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('erros JS:', s.errs())
s.fim()
