# -*- coding: utf-8 -*-
"""Mapa: camada Análises de solo e menos texto (proprietário, 13/10/2026: "coloque analises de solo como uma das opcoes do menu do mapa" e
"diminua essa quantidade de textos e descrições no mapa. somos minimalistas e essencialistas"). Oráculo pelos laudos de dados_solo.py
(a mesma base do AG-02), com V = 100 × SB ÷ T calculado aqui em Decimal (SB = Ca + Mg + K ÷ 391; T = SB + H+Al) e meta V₂ da regra.
  S1 a barra do mapa tem "Solo" entre Satélite e Pragas e doenças (DEC-0910-36, 16/10/2026); ao tocar, o nome da camada é "Solo"
  S2 Lagoa Grande: números da faixa e rótulos dos pivôs pelo oráculo (só o Pivô 12 tem laudo 0–20; V 50 % abaixo da meta 70 %; os outros "Sem laudo")
  S3 tocar o Pivô 12 abre o painel com o laudo LAU-2071 0–20 cm, CTC 8,10 e V 50 %, e o atalho para o laudo no AG-02
  S4 Santa Rita: com análise = talhões com laudo de solo 0–20 (T1, T2, T4 e C1), a validar = C1, sem análise = os demais
  S5 talhão sem laudo (T3): "Sem laudo" e "Registrar laudo" abre o AG-02 com a fazenda e o talhão no formulário
  T1 em cada camada, a fonte técnica sai da tela e fica na dica ⓘ ao lado do nome; nenhuma linha solta acima de 60 caracteres no bloco do mapa
  T2 o selo "Demonstração sintética" continua à vista na legenda de toda camada da Lagoa Grande (dado sintético sempre rotulado)
  T3 o ⓘ abre a dica com a fonte (mouse sobre o ⓘ); sem a etiqueta "clique no talhão"
  T4 celular 390 px sem rolagem horizontal; sem erro de JS
Uso: python3 mapa_solo_texto_test.py (lê _render ou RENDER_DIR)."""
import os, sys, json, time
from decimal import Decimal as Dc
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
os.environ.setdefault('CDP_GL', '1')
from comp_lib import Chrome, servir
import dados_solo as DS, dados_lagoa_fonte as F, dados as D

OK, FAIL = [], []
def chk(n, c, info=''):
    (OK if c else FAIL).append(n); print(('OK    ' if c else 'FALHA ') + n + ('' if c else ' · ' + str(info)[:900]), flush=True)

from decimal import ROUND_HALF_UP
# ---------- oráculo ----------
def v_pct(an):
    g = {a['a']: Dc(a['v']) for a in an}; sb = g['Ca'] + g['Mg'] + g['K'] / Dc('391'); t = sb + g['H+Al']
    return (Dc(100) * sb / t).quantize(Dc('0.1'))
def ultimo_020(faz):
    out = {}
    for l in DS.LAUDOS:
        if l['faz'] == faz and l['tipo'] == 'solo' and l['prof'] == '0–20' and (l['tal'] not in out or l['coleta'] > out[l['tal']]['coleta']): out[l['tal']] = l
    return out
LG020 = ultimo_020(DS.LG); SR020 = ultimo_020(DS.SR)
NPIV = len(F.LG_PIVOS)
p12 = LG020.get('Pivô 12'); V12 = v_pct(p12['an']) if p12 else None; META12 = Dc(DS.REGRA['v2']['Mamão Formosa'])
fmt = lambda d: (str(d).rstrip('0').rstrip('.') if '.' in str(d) else str(d)).replace('.', ',')
ESP_LG = {'Com análise': len(LG020), 'V abaixo': sum(1 for l in LG020.values() if l['sit'] == 'Validado' and l['tal'] == 'Pivô 12' and V12 < META12),
          'A validar': sum(1 for l in LG020.values() if l['sit'] != 'Validado'), 'Sem análise': NPIV - len(LG020)}
SR_TAL = [t[0] for t in D.TALHOES]
ESP_SR = {'Com análise': len([t for t in SR020 if t in SR_TAL]), 'A validar': sum(1 for t, l in SR020.items() if t in SR_TAL and l['sit'] != 'Validado'),
          'Sem análise': len([t for t in SR_TAL if t not in SR020])}

R = os.environ.get('RENDER_DIR') or os.path.join(HERE, '_render')
p, srv = servir(R); c = Chrome(); J = c.js
U = lambda pg: f'http://127.0.0.1:{p}/{pg}'
def espera(e, s=45):
    f = time.time() + s
    while time.time() < f:
        if J(e): return True
        time.sleep(.4)
    return False
RAIL = "JSON.stringify([...document.querySelectorAll('nav[aria-label=\"Funcionalidades do mapa\"] [role=tab]')].filter(b=>b.getClientRects().length).map(b=>b.innerText.trim()))"   # 16/10/2026 (proprietário): a barra das funções foi para o alto do mapa, com o nome à vista; acha o botão pelo nome (sem data-dica)
def camada(nome, w=1.6):
    J(f"(()=>{{const b=[...document.querySelectorAll('nav[aria-label=\"Funcionalidades do mapa\"] [role=tab]')].find(b=>b.innerText.trim()==={json.dumps(nome)}); if(b) b.click(); return !!b;}})()"); time.sleep(w)
INFO = "(()=>{const b=document.querySelector('main button.g2-info[aria-label=\"Fonte e regra da camada\"]'); return b?b.getAttribute('data-dica'):null;})()"
# bloco do mapa: a seção que contém a barra de camadas; nome da camada = primeiro <b> do cabeçalho
BLOCO = "(()=>{const n=document.querySelector('nav[aria-label=\"Funcionalidades do mapa\"]'); let s=n; while(s&&s.parentElement&&!(s.innerText||'').match(/Selecionar área/)) s=s.parentElement; return s;})()"
NOME = f"(()=>{{const s={BLOCO}; const b=s&&[...s.querySelectorAll('b')].find(x=>x.getClientRects().length); return b?b.innerText.trim():'';}})()"
FAIXA = f"""JSON.stringify((()=>{{const s={BLOCO}; if(!s) return {{}}; const o={{}}; const t=s.innerText.replace(/\\s+/g,' ');
  ['Com análise','V abaixo','A validar','Vencidas','Sem análise'].forEach(k=>{{ const m=t.match(new RegExp(k+' (\\\\d+)')); if(m) o[k]=+m[1]; }}); return o;}})())"""
# linhas soltas: nós de texto à vista no bloco do mapa (fora do painel do talhão, dos pivôs e dos botões), com mais de 60 caracteres
LONGAS = f"""JSON.stringify((()=>{{const s={BLOCO}; if(!s) return ['sem bloco']; const out=[]; const w=document.createTreeWalker(s,NodeFilter.SHOW_TEXT);
  while(w.nextNode()){{ const n=w.currentNode, e=n.parentElement; const t=(n.textContent||'').trim(); if(t.length<=60||!e||!e.getClientRects().length) continue;
    if(e.closest('aside,button,select,.lg-rot,[role=dialog],nav')) continue; out.push(t.slice(0,90)); }} return out;}})())"""
LEG_NOTA = f"(()=>{{const s={BLOCO}; const d=s&&[...s.querySelectorAll('div')].filter(x=>x.getClientRects().length&&/position: absolute; left: 12px; bottom: 12px/.test(x.getAttribute('style')||''))[0]; return d?d.innerText.replace(/\\s+/g,' '):'';}})()"
def mk(pid): return J(f"(()=>{{const m=window.__LGI&&window.__LGI.markers['{pid}']; return m?m.getElement().innerText.replace(/\\s+/g,' ').trim():null;}})()")
def toca_piv(pid, dy=28):
    pt = json.loads(J(f"JSON.stringify((()=>{{const r=window.__LGI.markers['{pid}'].getElement().getBoundingClientRect(); return {{x:r.left+r.width/2,y:r.top+r.height/2}};}})())"))
    for tp in ('mouseMoved', 'mousePressed', 'mouseReleased'): c.call('Input.dispatchMouseEvent', {'type': tp, 'x': pt['x'], 'y': pt['y'] + dy, 'button': 'left', 'clickCount': 1})
try:
    c.call('Page.addScriptToEvaluateOnNewDocument', {'source': "window.__err='';addEventListener('error',e=>{window.__err+=(e.message||'erro')+' | ';});"})
    c.aparelho(1440, 900, 1, False); c.goto(U('Main.dc.html'), .3); J("localStorage.clear(); sessionStorage.clear(); sessionStorage.setItem('mapa-ctx','{\"mf_faz\":\"Lagoa Grande\"}'); 1")
    c.goto(U('IN-04.dc.html'), 1.0); pronto = espera("!!(window.__LGI&&window.__LGI.pronto)")
    rail = json.loads(J(RAIL) or '[]')
    # DEC-0910-36 (decisão do proprietário, 16/10/2026): a função se chama Solo, entre Satélite e Pragas e doenças
    camada('Solo'); nome = J(NOME)
    i = rail.index('Solo') if 'Solo' in rail else -1
    chk('S1 barra do mapa: "Solo" entre Satélite e Pragas e doenças; tocar mostra a camada "Solo"',
        pronto and i > 0 and rail[i - 1] == 'Satélite' and rail[i + 1] == 'Pragas e doenças' and nome == 'Solo', [pronto, rail, nome])
    # 15/10/2026 (mapa de calor do solo): a faixa conta laudos e pontos da camada; o rótulo é o indicador escolhido (padrão: V %)
    fxt = (J("(document.querySelector('[role=group][aria-label^=Indicadores]')||{}).innerText||''") or '').replace('\n', ' ')
    ids = [q[0] for q in F.LG_PIVOS]; rots = {q: mk(q) for q in ids}
    p12k = next(q for q in ids if q.endswith('12'))
    esp12 = f'P12 V % {fmt(V12.quantize(Dc("1"), rounding=ROUND_HALF_UP))} %'
    sem = [q for q in ids if (rots[q] or '').endswith('Sem laudo')]   # DEC-0910-36: talhão sem laudo = "Sem laudo", em cinza
    import re as _re
    nl = int((_re.search(r'Laudos (\d+)', fxt) or [0, -1])[1]); npt = int((_re.search(r'Pontos (\d+)', fxt) or [0, -1])[1])
    chk(f'S2 Lagoa Grande: faixa com {len(LG020)} laudos 0–20 e {sum(len(l["pts"]) for l in LG020.values())} pontos pelo oráculo; Pivô 12 "{esp12}"; os {NPIV - len(LG020)} pivôs sem laudo "Sem laudo"',
        nl == len(LG020) and npt == sum(len(l['pts']) for l in LG020.values()) and rots[p12k] == esp12 and len(sem) == NPIV - len(LG020), [fxt, rots[p12k], len(sem)])
    toca_piv(p12k); time.sleep(1.4)
    pan = J("(()=>{const a=[...document.querySelectorAll('main aside')].find(x=>x.getClientRects().length); return a?a.innerText.replace(/\\s+/g,' '):'';})()") or ''
    lk = J("(()=>{const a=[...document.querySelectorAll('main aside a, main aside button')].find(x=>x.getClientRects().length&&x.innerText.trim()==='Abrir laudo'); return a?(a.getAttribute('href')||a.getAttribute('data-h')||'botão'):'';})()") or ''
    chk(f'S3 tocar o Pivô 12: painel com {p12["id"]} · 0–20 cm, CTC 8,10 cmolc/dm³ e V {fmt(V12)} %; atalho "Abrir laudo"',
        f'{p12["id"]} · 0–20 cm' in pan and 'CTC 8,10 cmolc/dm³' in pan and f'V {fmt(V12)} %' in pan and bool(lk), [pan[:400], lk])
    # T1/T2 · todas as camadas da Lagoa Grande
    ruins, sem_selo, sem_info = {}, [], []
    for nm in rail:
        camada(nm, 1.2); inf = J(INFO); lg = J(LONGAS); nota = J(LEG_NOTA) or ''
        if inf is None or (not inf.strip() and nm != 'Custos'): sem_info.append(nm)
        lg = json.loads(lg or '[]')
        if lg or (inf and len(inf) > 60 and inf in (J("document.body.innerText") or '')): ruins[nm] = lg or ['fonte à vista']
        if 'Demonstração sintética' not in nota: sem_selo.append([nm, nota[-80:]])
    chk(f'T1 {len(rail)} camadas: a fonte técnica fica na dica ⓘ ao lado do nome; nenhuma linha solta acima de 60 caracteres no bloco do mapa',
        len(rail) == 9 and not ruins and not sem_info, [ruins, sem_info])   # nove funções (DEC-0910-36)
    chk('T2 o selo "Demonstração sintética" segue à vista na legenda de toda camada da Lagoa Grande', not sem_selo, sem_selo)
    camada('Satélite')
    pi = json.loads(J("JSON.stringify((()=>{const b=document.querySelector('main button.g2-info[aria-label=\"Fonte e regra da camada\"]'); const r=b?b.getBoundingClientRect():{left:-9,top:-9,width:0,height:0}; return {x:r.left+r.width/2,y:r.top+r.height/2};})())"))
    c.call('Input.dispatchMouseEvent', {'type': 'mouseMoved', 'x': pi['x'], 'y': pi['y']}); time.sleep(.6)
    dica = J("(()=>{const d=document.getElementById('g2-dica'); return d&&!d.hidden&&d.getClientRects().length?d.innerText.trim():'';})()") or ''
    corpo = J("document.body.innerText") or ''
    chk('T3 o ⓘ da camada (Satélite) abre a dica com a fonte ao passar o mouse; sem a etiqueta "clique no talhão"',
        'imagem e índices fictícios' in dica and 'aquisição' in dica and 'clique no talhão' not in corpo, [dica[:200], 'clique no talhão' in corpo])
    # S4 · Santa Rita
    c.goto(U('Main.dc.html'), .3); J("sessionStorage.setItem('mapa-ctx','{\"mf_faz\":\"Santa Rita\"}'); 1"); c.goto(U('IN-04.dc.html'), 1.6)
    camada('Solo'); fxs = (J("(document.querySelector('[role=group][aria-label^=Indicadores]')||{}).innerText||''") or '').replace('\n', ' ')
    # MUX-F1 (17/10/2026): o nome acessível do talhão passou a ser o completo do pedido ("T4, 120 ha, …"); o talhão se acha por data-talhao e o
    # rótulo da camada vem de data-rotulo, o mesmo texto que vinha depois de "T4: " (oráculo obsoleto na forma de achar; a asserção não muda)
    c1 = J("(()=>{const e=[...document.querySelectorAll('svg [aria-label]')].find(x=>x.getAttribute('data-talhao')==='C1'); return e?e.getAttribute('data-talhao')+': '+e.getAttribute('data-rotulo'):'';})()") or ''
    chk(f'S4 Santa Rita: {ESP_SR["Com análise"]} laudos 0–20 (T1, T2, T4 e C1) pelo oráculo; C1 aguardando validação e sem H+Al: V não calculável',
        f'Laudos {ESP_SR["Com análise"]}' in fxs and 'não calculável' in c1, [fxs, c1])
    # S5 · talhão sem análise: "Registrar laudo" leva ao AG-02 com fazenda e talhão no formulário (contexto herdado, visível e corrigível)
    J("sessionStorage.setItem('mapa-ctx',JSON.stringify({mf_faz:'Santa Rita',lay:'Análises de solo',tsel:['T3']})); 1"); c.goto(U('IN-04.dc.html'), 1.8)
    p5 = (J("(document.querySelector('aside[aria-label^=\"T3\"]')||{innerText:''}).innerText") or '').replace('\n', ' · ')
    h5 = J("(()=>{const a=[...document.querySelectorAll('aside[aria-label^=\"T3\"] a')].find(x=>x.innerText.trim()==='Registrar laudo'); return a?a.getAttribute('href'):'';})()") or ''
    f5 = []
    if h5:
        c.goto(U(h5), 2.0); espera("!!document.querySelector('[role=dialog]')", 10)
        f5 = json.loads(J("JSON.stringify((()=>{const d=[...document.querySelectorAll('[role=dialog]')].find(x=>x.getClientRects().length&&/Registrar laudo/.test(x.innerText)); return d?[...d.querySelectorAll('select')].map(s=>s.options[s.selectedIndex]?s.options[s.selectedIndex].text:''):[];})())") or '[]')
    chk('S5 Santa Rita T3 (sem laudo): painel "Sem laudo" com "Registrar laudo"; o AG-02 abre o formulário com Santa Rita e T3 já escolhidos',
        'Sem laudo' in p5 and h5.startswith('AG-02.dc.html#registrar=') and 'Santa Rita' in f5 and any(x.split(' · ')[0] == 'T3' for x in f5), [p5[:200], h5, f5])
    errs = J("window.__err") or ''
    c.aparelho(390, 844, 2, True); c.goto(U('IN-04.dc.html'), 1.6); camada('Solo')
    sw = J("document.documentElement.scrollWidth<=window.innerWidth+1")
    chk('T4 celular 390 px sem rolagem horizontal; sem erro de JS', sw and not errs and not (J("window.__err") or ''), [sw, errs, J("window.__err")])
finally:
    try: c.close()
    except Exception: pass
    srv.terminate()
print(f'RESULTADO: {len(OK)} ok · {len(FAIL)} falhas')
sys.exit(1 if FAIL else 0)
