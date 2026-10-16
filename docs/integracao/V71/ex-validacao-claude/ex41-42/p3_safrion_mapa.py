# -*- coding: utf-8 -*-
"""EX-42 · camada atual do Safrion no render (G/_render, 62f2c35, dados sintéticos): Mapa (IN-04) › Pragas e doenças e Satélite,
"Ver histórico" (AG-06) e a série do AG-01det. Lagoa Grande (mapa real em MapLibre, pixels sintéticos) e Santa Rita (desenho).
Saídas: out/p3_safrion_mapa.log, out/p3_safrion_mapa.json, png/saf_*.png. Só leitura."""
import os, sys, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from base import chrome, server, dump, log, OUT, PNG, G
R_DIR = os.path.join(G, '_render')
L = open(os.path.join(OUT, 'p3_safrion_mapa.log'), 'w', encoding='utf-8'); R = {}
port = server(R_DIR); c = chrome(); J = c.js
U = lambda pg: f'http://127.0.0.1:{port}/{pg}'
def espera(e, s=30):
    f = time.time() + s
    while time.time() < f:
        try:
            if J(e): return True
        except Exception: pass
        time.sleep(.3)
    return False
def abre(ctx, lg=False, w=1440, h=900, toque=False):
    c.aparelho(w, h, 1, toque); c.goto(U('Main.dc.html'), .3); J("localStorage.clear(); sessionStorage.clear(); 1")
    J(f"sessionStorage.setItem('mapa-ctx',{json.dumps(json.dumps(ctx))}); 1"); c.goto(U('IN-04.dc.html'), 1.6)
    if lg: R.setdefault('lg_pronto', []).append(espera("!!(window.__LGI&&window.__LGI.pronto)", 40)); time.sleep(1.2)
def leitura():
    return json.loads(J(r"""JSON.stringify((()=>{const n=s=>(s||'').replace(/\s+/g,' ').trim(); const m=document.querySelector('main')||document.body;
  const grupos=[...m.querySelectorAll('[role=group][aria-label]')].filter(g=>g.getClientRects().length).map(g=>g.getAttribute('aria-label')+': '+[...g.querySelectorAll('button')].map(b=>n(b.innerText)+(b.getAttribute('aria-pressed')==='true'?'*':'')).join(' | '));
  const sels=[...m.querySelectorAll('select')].filter(s=>s.getClientRects().length).map(s=>s.getAttribute('aria-label')+': '+[...s.options].map(o=>o.text+(o.selected?'*':'')).join(' | '));
  const nums=n((document.querySelector('[role=group][aria-label^="Indicadores de"]')||{innerText:''}).innerText);
  const ativa=[...document.querySelectorAll('nav[aria-label="Funcionalidades do mapa"] button')].filter(b=>b.getAttribute('aria-selected')==='true').map(b=>n(b.innerText));
  const links=[...m.querySelectorAll('a')].filter(a=>a.getClientRects().length&&/Ver histórico|Abrir Pragas|Ver o que|histórico/i.test(a.innerText)).map(a=>n(a.innerText)+' → '+a.getAttribute('href'));
  const leg=[...m.querySelectorAll('div')].filter(x=>x.getClientRects().length&&/position: absolute; left: 12px; bottom: 12px/.test(x.getAttribute('style')||'')).map(x=>n(x.innerText))[0]||'';
  const fonte=n(([...m.querySelectorAll('div,span,p')].find(x=>x.children.length===0&&/Sentinel-2|vistorias de Pragas/.test(x.innerText))||{innerText:''}).innerText);
  const range=!!m.querySelector('input[type=range]'); const alvos=[...m.querySelectorAll('[role=menu] [role^=menuitem], [aria-label*=Alvo] button')].map(b=>n(b.innerText)).slice(0,20);
  const painel=n((document.querySelector('main aside[aria-label], aside[role=dialog], [role=dialog]')||{innerText:''}).innerText).slice(0,2500);
  return {ativa,grupos,sels,nums,links,leg,fonte,range,alvos,painel};})())"""))
def shot(n): c.shot(os.path.join(PNG, n)); log(L, '  captura', n)

# 1 · Lagoa Grande · Pragas e doenças (hoje)
abre({'mf_faz': 'Lagoa Grande', 'lay': 'MIP/MID'}, lg=True)
R['lg_mip'] = leitura(); log(L, '1 LG Pragas', json.dumps(R['lg_mip'], ensure_ascii=False)); shot('saf_1440_lg_pragas.png')
# menu de alvos
ab = J("(()=>{const b=[...document.querySelectorAll('main button')].find(b=>/^Alvos?/.test(b.innerText.trim())); if(!b) return ''; b.click(); return b.innerText;})()"); time.sleep(.5)
R['lg_mip_alvos_menu'] = dict(botao=ab, itens=J("[...document.querySelectorAll('[role=menu] [role^=menuitem], [role=listbox] [role=option]')].filter(x=>x.getClientRects().length).map(x=>x.innerText.replace(/\\s+/g,' ').trim()+'|'+(x.getAttribute('role'))+'|'+(x.getAttribute('aria-checked')||x.getAttribute('aria-selected')))"))
c.tecla('Escape', 'Escape', 27); log(L, '1b alvos', R['lg_mip_alvos_menu'])
# 30 dias
J("(()=>{const b=[...document.querySelectorAll('main [role=group] button')].find(b=>b.innerText.trim()==='Últimos 30 dias'); if(b) b.click();})()"); time.sleep(.8)
R['lg_mip_30'] = leitura()['nums']; log(L, '1c 30 dias', R['lg_mip_30'])
# 2 · painel do PV04 (Pragas e doenças)
abre({'mf_faz': 'Lagoa Grande', 'lay': 'MIP/MID', 'tsel': ['PV04']}, lg=True)
R['lg_mip_pv04'] = leitura()['painel']; log(L, '2 PV04 painel', R['lg_mip_pv04']); shot('saf_1440_lg_pragas_PV04.png')
R['lg_mip_pv04_prim'] = J("[...document.querySelectorAll('main aside button')].filter(b=>getComputedStyle(b).backgroundColor==='rgb(30, 122, 76)').map(b=>b.innerText.trim())")
# 3 · Lagoa Grande · Satélite
abre({'mf_faz': 'Lagoa Grande', 'lay': 'Satélite'}, lg=True)
R['lg_sat'] = leitura(); log(L, '3 LG Satélite', json.dumps(R['lg_sat'], ensure_ascii=False)); shot('saf_1440_lg_satelite.png')
abre({'mf_faz': 'Lagoa Grande', 'lay': 'Satélite', 'tsel': ['PV09']}, lg=True)
R['lg_sat_pv09'] = leitura()['painel']; log(L, '3b PV09 painel', R['lg_sat_pv09']); shot('saf_1440_lg_satelite_PV09.png')
# 4 · Santa Rita · Satélite, cena 06/09 (nuvem em P2 e T7)
abre({'mf_faz': 'Santa Rita', 'lay': 'Satélite', 'flt': {'Satélite': {'dt': '06/09', 'ctr': 'Fazenda'}}})
R['sr_sat_0609'] = leitura(); R['sr_sat_0609']['rotulos'] = J("[...document.querySelectorAll('main svg text')].map(t=>t.textContent.trim()).filter(Boolean).slice(0,60)")
log(L, '4 SR Satélite 06/09', json.dumps(R['sr_sat_0609'], ensure_ascii=False)); shot('saf_1440_sr_satelite_0609_nuvem.png')
for ctr in ['Talhão', 'Absoluto']:
    abre({'mf_faz': 'Santa Rita', 'lay': 'Satélite', 'flt': {'Satélite': {'dt': '21/09', 'ctr': ctr}}}); R[f'sr_sat_{ctr}'] = leitura()['leg']
log(L, '4b legendas Talhão/Absoluto', R['sr_sat_Talhão'], '||', R['sr_sat_Absoluto'])
# 5 · Santa Rita · Pragas e doenças
abre({'mf_faz': 'Santa Rita', 'lay': 'MIP/MID'})
R['sr_mip'] = leitura(); log(L, '5 SR Pragas', json.dumps(R['sr_mip'], ensure_ascii=False)); shot('saf_1440_sr_pragas.png')
# 6 · "Ver histórico" → AG-06
c.goto(U('AG-06.dc.html'), 1.2)
R['ag06'] = J("(document.querySelector('main')||document.body).innerText.replace(/\\s+/g,' ').slice(0,2500)"); log(L, '6 AG-06', R['ag06']); shot('saf_1440_ag06.png')
# 7 · AG-01det: série de leituras do mesmo método
c.goto(U('AG-01det.dc.html'), 1.2)
R['ag01det'] = J("(document.querySelector('main')||document.body).innerText.replace(/\\s+/g,' ').slice(0,3000)")
R['ag01det_svg'] = J("[...document.querySelectorAll('main svg')].map(s=>(s.getAttribute('role')||'')+'|'+(s.getAttribute('aria-label')||'')).slice(0,6)")
log(L, '7 AG-01det', R['ag01det'][:1500], R['ag01det_svg']); shot('saf_1440_ag01det.png')
# 8 · 390 px toque · Lagoa · Pragas e doenças
abre({'mf_faz': 'Lagoa Grande', 'lay': 'MIP/MID'}, lg=True, w=390, h=844, toque=True)
R['m390'] = dict(leitura=leitura(), scrollW=J("document.documentElement.scrollWidth"))
log(L, '8 390', json.dumps(R['m390'], ensure_ascii=False)[:1500]); shot('saf_390_lg_pragas.png')
R['erros_js'] = J("window.__errs||[]"); dump('p3_safrion_mapa.json', R); log(L, 'FIM')
