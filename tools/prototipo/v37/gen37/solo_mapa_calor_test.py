# -*- coding: utf-8 -*-
"""Mapa (pedidos do proprietário de 15/10/2026): mapa de calor do solo por laudo, camada e indicador; lâmina recomendada e percentímetro na
Irrigação; indicadores do laudo no AG-02; "Agrupar por" Grupo de máquina nos Planos da Manutenção. Oráculos: dados_solo (laudos, pontos, IND),
dados_irrigacao (semente: déficit, eficiência, limite por passada e ficha) e as próprias regras escritas aqui de forma independente.
  S1 Lagoa Grande · Análises de solo: Laudo e Indicador como seletores (≥ 12 indicadores, com pH, P e MO), Camada e Contraste segmentados
  S2 rótulo de cada pivô com laudo = valor do laudo (P em mg/dm³); faixa: média ponderada pela área; canvas pintado nos pivôs com laudo
  S3 Santa Rita · V % · Talhão: cada talhão com laudo tem manchas (≥ 4 cores nas células) e os pontos da amostragem (30 por talhão)
  S4 painel do T2: áreas por classe somam a área do talhão; pontos com coordenada; escolher o LAU-2063 seleciona o T2 e tira os outros
  S5 Camada 20–40 cm: só T4 (Santa Rita) com laudo
  I1 Irrigação · Balanço (Lagoa Grande): rótulo do Pivô 5 = lâmina e percentímetro pela conta da ficha; painel com ETc, lâmina e velocidade
  A1 AG-02: colunas pH, P e MO no padrão; LAU-2061 com pH 5,5 e P 18,5 mg/dm³; clicar no laudo abre o laudo
  M1 Manutenção › Planos: "Agrupar por" oferece Grupo de máquina
  J sem erro de JS
Uso: python3 solo_mapa_calor_test.py (RENDER_DIR=<dir>; contraprova na base sem a mudança)."""
import os, sys, json, time, math
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
os.environ.setdefault('CDP_GL', '1'); os.environ.setdefault('SAFRION_DADOS', 'sintetico')
from comp_lib import Chrome, servir
import dados_solo as DS, dados_irrigacao as DI
OK, FAIL = [], []
def chk(n, c, info=''):
    (OK if c else FAIL).append(n); print(('OK    ' if c else 'FALHA ') + n + ('' if c else ' · ' + str(info)[:700]), flush=True)
R = os.environ.get('RENDER_DIR') or os.path.join(HERE, '_render')
p, srv = servir(R); c = Chrome(); J = c.js
U = lambda pg: f'http://127.0.0.1:{p}/{pg}'
br = lambda x, d: f'{x:,.{d}f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
def abre(ctx, lg=True):
    c.goto(U('Main.dc.html'), .3); J("localStorage.clear(); sessionStorage.clear(); 1")
    J(f"sessionStorage.setItem('mapa-ctx',{json.dumps(json.dumps(ctx))}); 1"); c.goto(U('IN-04.dc.html'), 2.0)
    if lg:
        for _ in range(60):
            if J("!!(window.__LGI&&window.__LGI.pronto)"): break
            time.sleep(.3)
    time.sleep(2.0)
def faixa(): return J("(document.querySelector('[role=group][aria-label^=Indicadores]')||{}).innerText||''").replace('\n', ' ')
def rot_lg(pid): return J(f"(window.__LGI&&window.__LGI.markers['{pid}'])?window.__LGI.markers['{pid}'].getElement().innerText.replace(/\\s+/g,' ').trim():''")
def rot_sr(t): return J(f"(()=>{{const e=[...document.querySelectorAll('svg [aria-label]')].find(x=>(x.getAttribute('aria-label')||'').startsWith('{t}:')); return e?e.getAttribute('aria-label').slice({len(t)+2}):'';}})()") or ''
def painel(): return J("(()=>{const a=[...document.querySelectorAll('main aside')].find(x=>x.getClientRects().length); return a?a.innerText.replace(/\\s+/g,' '):'';})()") or ''
SOLO = 'Análises de solo'
try:
    c.call('Page.addScriptToEvaluateOnNewDocument', {'source': "window.__err='';addEventListener('error',e=>{window.__err+=(e.message||'erro')+' | ';});"})
    c.aparelho(1440, 900, 1, False)
    abre({'mf_faz': 'Lagoa Grande', 'lay': SOLO, 'flt': {SOLO: {'ind': 'P'}}})
    sels = json.loads(J("JSON.stringify([...document.querySelectorAll('main select')].map(s=>[s.getAttribute('aria-label'),[...s.options].map(o=>o.value)]))") or '[]'); sd = dict(sels)
    segs = json.loads(J("JSON.stringify([...document.querySelectorAll('main [role=group]')].map(g=>g.getAttribute('aria-label')))") or '[]')
    lg_laudos = [l for l in DS.LAUDOS if l['faz'] == 'Lagoa Grande' and l['prof'] == '0–20']
    chk('S1 Laudo e Indicador como seletores (Mais recente + laudos da camada; ≥ 12 indicadores com pH, P e MO); Camada e Contraste segmentados',
        sd.get('Laudo', [None])[0] == 'Mais recente' and set(sd.get('Laudo', [])[1:]) == {l['id'] for l in lg_laudos}
        and len(sd.get('Indicador', [])) >= 12 and {'pH', 'P', 'MO'} <= set(sd.get('Indicador', [])) and 'Camada' in segs and 'Contraste' in segs, [sels, segs])
    pv = {l['tal']: l for l in lg_laudos}
    ids = {p_['nome'] if 'nome' in p_ else '': p_ for p_ in []}
    pivos = json.loads(J("JSON.stringify(window.__LGI?Object.keys(window.__LGI.markers):[])") or '[]')
    rots = {pid: rot_lg(pid) for pid in pivos}
    def pid_de(nome): n = int(nome.split()[-1]); return next((x for x in pivos if int(''.join(ch for ch in x if ch.isdigit())) == n), None)
    esp = {pid_de(t): 'P ' + br(float(next(a['v'] for a in l['an'] if a['a'] == 'P')), 1) + ' mg/dm³' for t, l in pv.items()}
    ruins = {k: [rots.get(k), v] for k, v in esp.items() if v not in (rots.get(k) or '')}
    area = sum(float(l['area']) for l in lg_laudos); med = sum(float(next(a['v'] for a in l['an'] if a['a'] == 'P')) * float(l['area']) for l in lg_laudos) / area
    fx = faixa(); pint = J("(()=>{const cv=window.__LGI&&window.__LGI.cv; if(!cv) return 0; const d=cv.getContext('2d').getImageData(0,0,cv.width,cv.height).data; let n=0; for(let i=3;i<d.length;i+=4) if(d[i]>0) n++; return n;})()")
    chk(f'S2 rótulo dos {len(esp)} pivôs com laudo = P do laudo; faixa: média ponderada {br(med, 1)} mg/dm³ e {sum(len(l["pts"]) for l in lg_laudos)} pontos; canvas pintado',
        not ruins and f'P {br(med, 1)} mg/dm³' in fx and f'Pontos {sum(len(l["pts"]) for l in lg_laudos)}' in fx and pint > 500, [ruins, fx, pint])
    abre({'mf_faz': 'Santa Rita', 'lay': SOLO, 'flt': {SOLO: {'ind': 'V %', 'ctr': 'Talhão'}}}, lg=False)
    cores = json.loads(J("""JSON.stringify((()=>{const o={}; document.querySelectorAll('svg g[clip-path] rect').forEach(r=>{ const g=r.closest('g[clip-path]'); const t=(g.getAttribute('clip-path')||'').replace(/^url\\(#cp_|\\)$/g,''); const f=r.getAttribute('fill'); if(f&&f!=='none'&&g.getAttribute('opacity')!=='0') (o[t]=o[t]||{})[f]=1; }); const r={}; Object.keys(o).forEach(t=>r[t]=Object.keys(o[t]).length); return r;})())""") or '{}')
    npts = J("document.querySelectorAll('svg circle[r=\"3.4\"]').length")
    chk('S3 Santa Rita · V % · Talhão: T1, T2 e T4 com manchas (≥ 4 cores) e 90 pontos (30 por talhão)', all(cores.get(t, 0) >= 4 for t in ('T1', 'T2', 'T4')) and npts == 90, [cores, npts])
    abre({'mf_faz': 'Santa Rita', 'lay': SOLO, 'flt': {SOLO: {'ind': 'V %', 'ctr': 'Absoluto'}}, 'tsel': ['T2']}, lg=False)
    pn = painel(); import re
    has = [float(x.replace('.', '').replace(',', '.')) for x in re.findall(r'· ([\d.,]+) ha \(\d+ %\)', pn)]
    J("""(()=>{const s=document.querySelector('main select[aria-label=Laudo]'); Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype,'value').set.call(s,'LAU-2063'); s.dispatchEvent(new Event('change',{bubbles:true}));})()"""); time.sleep(1.2)
    t1 = rot_sr('T1'); sel = J("(document.querySelector('main aside h2')||{}).innerText||''")
    chk(f'S4 painel do T2: áreas por classe somam 298 ha ({has}); pontos com coordenada; LAU-2063 seleciona o T2 e o T1 fica "fora do laudo escolhido"',
        abs(sum(has) - 298) < 0.6 and re.search(r'Ponto A\d\d · V % [\d,]+ % −15,', pn) and t1 == 'fora do laudo escolhido' and sel.startswith('T2'), [has, pn[:600], t1, sel])
    abre({'mf_faz': 'Santa Rita', 'lay': SOLO, 'flt': {SOLO: {'prof': '20–40 cm', 'ind': 'V %'}}}, lg=False)
    com = [t for t in ('T1', 'T2', 'P1', 'P2', 'T4', 'T3', 'T7', 'C1') if rot_sr(t).startswith('V %')]
    chk('S5 Camada 20–40 cm: só o T4 com laudo', com == ['T4'], [com, {t: rot_sr(t) for t in ('T1', 'T4', 'C1')}])
    # irrigação
    x = DI.seed()['setores']['PV05']; d = 13.2; brt = d / (x['efic'] / 100); np_ = max(1, math.ceil(brt / x['lmax'] - 1e-9)); por = brt / np_
    l100 = x['ficha']['lamina_100_mm']; pct = math.floor(l100 * 100 / por + 1e-9)
    if l100 * 100 / pct > x['lmax'] + 1e-9: pct = math.ceil(l100 * 100 / por - 1e-9)
    esp_irr = f"déficit {br(d, 1)} mm → {np_}× {br(l100 * 100 / pct, 1)} mm a {pct} %"
    abre({'mf_faz': 'Lagoa Grande', 'lay': 'Irrigação', 'flt': {'Irrigação': {'ver': 'Balanço hídrico'}}, 'tsel': ['PV05']})
    r5 = rot_lg('PV05'); pn = painel()
    chk(f'I1 Pivô 5: "{esp_irr}" (ficha {l100} mm a 100 %); painel com ETc, lâmina recomendada e percentímetro',
        esp_irr in r5 and 'Necessidade da cultura ETc' in pn and f'Lâmina recomendada {br(brt, 1)} mm brutos' in pn and f'percentímetro {pct} %' in pn, [r5, pn[:900]])
    # AG-02
    c.goto(U('AG-02.dc.html'), 2.0)
    cab = [h.split('\n')[0].strip() for h in (J("[...document.querySelectorAll('[data-g2g=g_lau] [role=columnheader]')].map(h=>h.innerText.replace(/[⇅▾▴▲▼]/g,'').trim()).filter(Boolean)") or [])]
    lin = J("(()=>{const r=[...document.querySelectorAll('[data-g2g=g_lau] [role=row][data-rid]')].find(r=>/LAU-2061/.test(r.innerText)); return r?r.innerText.replace(/\\s+/g,' '):'';})()") or ''
    J("(()=>{const r=[...document.querySelectorAll('[data-g2g=g_lau] [role=row][data-rid]')].find(r=>/LAU-2061/.test(r.innerText)); r&&r.click();})()"); time.sleep(1.2)
    abriu = J("/LAU-2061/.test((document.querySelector('[role=dialog]')||{}).innerText||'')")
    chk('A1 AG-02: pH, P e MO no padrão; LAU-2061 pH 5,5 e P 18,5 mg/dm³; clicar abre o laudo', {'PH', 'P', 'MO'} <= set(x.upper() for x in cab) and ' 5,5 ' in f' {lin} ' and '18,5 mg/dm³' in lin and abriu, [cab, lin, abriu])
    c.goto(U('MA.dc.html#vis=planos'), 2.0)
    J("(()=>{const b=document.querySelector('[data-g2agb=\"g_pl\"]'); b&&b.click();})()"); time.sleep(.5)
    ags = J("[...document.querySelectorAll('[data-g2agm=\"g_pl\"] [role=menuitemradio]')].map(x=>x.innerText.trim().split('\\n')[0].trim())") or []
    chk('M1 Planos da Manutenção: "Agrupar por" com Grupo de máquina', 'Grupo de máquina' in ags, ags)
    chk('J sem erro de JS', not J("window.__err||''"), J("window.__err||''"))
finally:
    c.close() if hasattr(c, 'close') else None
print(f'RESULTADO: {len(OK)}/{len(OK) + len(FAIL)}' + (' · FALHAS: ' + '; '.join(FAIL) if FAIL else ''))
sys.exit(1 if FAIL else 0)
