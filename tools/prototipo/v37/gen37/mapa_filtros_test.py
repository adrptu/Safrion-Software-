# -*- coding: utf-8 -*-
"""Mapa: Safra e Cultura na faixa de filtros e alvos da camada Pragas e doenças (proprietário, 15/10/2026: "Falta filtro de safra e cultura";
"falta opção de selecionar qual alvo se deseja focar a visualização, pode ser 1 só, todos ou mais de 1 selecionado").
Oráculos: os cultivos de cada safra (dados2.CULTIVOS) e o previsto do plano (inicio.MDATA); os alvos das vistorias lidos da própria camada.
  F1 faixa: Fazenda, Safra e Cultura no grupo "Filtros"; Safra só com as safras da fazenda (Lagoa Grande: 2026/27; Santa Rita: 3)
  F2 Santa Rita · Safrinha 2027 · Lavoura: só T1, T2 e P1 com cultivo (Milho, Milho, Feijão); os demais "sem cultivo na safra"
  F3 Cultura Milho: só T1 e T2 no filtro; os outros "fora do filtro" em Custos; Custos = previsto do plano da Safrinha 2027 (R$/ha)
  F4 Cultura some quando não existe na safra nova (volta a Todas); Fazenda Lagoa Grande: Safra 2026/27
  A1 Pragas e doenças: "Alvos · Todos"; abrir lista com Todos + alvos; marcar 1 alvo foca nele (talhões sem ele ficam "sem …")
  A2 marcar um 2º alvo soma (botão "2 de N"); "Todos" volta ao todo; Esc fecha a lista com foco no botão
  J sem erro de JS · 390 px sem rolagem lateral
Uso: python3 mapa_filtros_test.py (RENDER_DIR=<dir> para outro _render; contraprova na base sem a mudança)."""
import os, sys, json, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
os.environ.setdefault('CDP_GL', '1')
from comp_lib import Chrome, servir
OK, FAIL = [], []
def chk(n, c, info=''):
    (OK if c else FAIL).append(n); print(('OK    ' if c else 'FALHA ') + n + ('' if c else ' · ' + str(info)[:700]), flush=True)
R = os.environ.get('RENDER_DIR') or os.path.join(HERE, '_render')
p, srv = servir(R); c = Chrome(); J = c.js
U = lambda pg: f'http://127.0.0.1:{p}/{pg}'
TSR = ['T1', 'T2', 'P1', 'P2', 'T4', 'T3', 'T7', 'C1']
def abre(ctx):
    c.goto(U('Main.dc.html'), .3); J("localStorage.clear(); sessionStorage.clear(); 1")
    J(f"sessionStorage.setItem('mapa-ctx',{json.dumps(json.dumps(ctx))}); 1"); c.goto(U('IN-04.dc.html'), 1.8)
# MUX-F1 (17/10/2026): o nome acessível do talhão passou a ser o completo do pedido ("T4, 120 ha, …"); o talhão se acha por data-talhao e o
# rótulo da camada vem de data-rotulo, o mesmo texto que vinha depois de "T4: " (oráculo obsoleto na forma de achar; a asserção não muda)
def rot(t): return J(f"(()=>{{const e=[...document.querySelectorAll('svg [aria-label]')].find(x=>x.getAttribute('data-talhao')==='{t}'); return e?e.getAttribute('data-rotulo'):'';}})()") or ''
def faixa(): return json.loads(J("""JSON.stringify((()=>{const g=document.querySelector('.mf-tela'); if(!g) return null; return [...g.querySelectorAll('select')].map(s=>({l:s.getAttribute('aria-label'),v:s.value,o:[...s.options].map(o=>o.value)}));})())""") or 'null')
def escolhe(rotulo, val):
    J(f"""(()=>{{const s=document.querySelector('.mf-tela select[aria-label={json.dumps(rotulo)}]'); Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype,'value').set.call(s,{json.dumps(val)});
      s.dispatchEvent(new Event('change',{{bubbles:true}}));}})()"""); time.sleep(1.0)
def camada(nome):
    J(f"(()=>{{const b=[...document.querySelectorAll('nav[aria-label=\"Funcionalidades do mapa\"] [role=tab]')].find(b=>b.innerText.trim()==={json.dumps(nome)}); if(b) b.click();}})()"); time.sleep(1.2)   # 16/10/2026 (proprietário): a barra das funções foi para o alto do mapa, com o nome à vista; acha o botão pelo nome (sem data-dica)
try:
    c.call('Page.addScriptToEvaluateOnNewDocument', {'source': "window.__err='';addEventListener('error',e=>{window.__err+=(e.message||'erro')+' | ';});"})
    c.aparelho(1440, 900, 1, False)
    abre({'mf_faz': 'Lagoa Grande', 'lay': 'Lavoura'}); fx = faixa() or []
    lg = {x['l']: x for x in fx}
    abre({'mf_faz': 'Santa Rita', 'lay': 'Lavoura'}); fs = {x['l']: x for x in (faixa() or [])}
    chk('F1 faixa com Fazenda, Safra e Cultura; Safra da fazenda (Lagoa Grande só 2026/27; Santa Rita 3 safras, sem "Todas")',
        set(lg) >= {'Filtrar por fazenda', 'Filtrar por safra', 'Filtrar por cultura'} and lg['Filtrar por safra']['o'] == ['2026/27']
        and fs['Filtrar por safra']['o'] == ['2026/27', 'Safrinha 2027', '2025/26'] and fs['Filtrar por safra']['v'] == '2026/27', [lg, fs])
    escolhe('Filtrar por safra', 'Safrinha 2027')
    r = {t: rot(t) for t in TSR}
    com = {t for t in TSR if not r[t].startswith('sem cultivo')}
    chk('F2 Safrinha 2027 · Lavoura: só T1 (Milho), T2 (Milho) e P1 (Feijão) com cultivo; os outros "sem cultivo na safra"',
        com == {'T1', 'T2', 'P1'} and r['T1'].startswith('Milho') and r['T2'].startswith('Milho') and r['P1'].startswith('Feijão'), r)
    cults = (faixa() or [{}])[2].get('o') if len(faixa() or []) > 2 else None
    escolhe('Filtrar por cultura', 'Milho'); camada('Custos')
    r2 = {t: rot(t) for t in TSR}
    fora = {t for t in TSR if r2[t] == 'fora do filtro'}
    chk('F3 Cultura Milho na Safrinha: T1 e T2 no filtro (previsto R$/ha do plano), os outros "fora do filtro" em Custos; opções de Cultura = as da safra',
        fora == set(TSR) - {'T1', 'T2'} and all('/ha' in r2[t] for t in ('T1', 'T2')) and cults == ['Todas', 'Feijão', 'Milho'], [r2, cults])
    escolhe('Filtrar por safra', '2026/27'); time.sleep(.3)
    cu = {x['l']: x for x in (faixa() or [])}.get('Filtrar por cultura', {})
    escolhe('Filtrar por fazenda', 'Lagoa Grande'); fl = {x['l']: x for x in (faixa() or [])}
    chk('F4 Milho segue válido na 2026/27 da Santa Rita (milho em P2 hoje); na Lagoa Grande a Safra é 2026/27 e a Cultura volta a Todas',
        cu.get('v') == 'Milho' and fl.get('Filtrar por safra', {}).get('v') == '2026/27' and fl.get('Filtrar por cultura', {}).get('v') == 'Todas', [cu, fl])
    # alvos
    abre({'mf_faz': 'Santa Rita', 'lay': 'MIP/MID'})
    bt = J("(()=>{const b=document.querySelector('button[data-alv]'); return b?b.innerText.replace(/\\s+/g,' ').trim():'';})()")
    J("document.querySelector('button[data-alv]').click()"); time.sleep(.5)
    ops = json.loads(J("JSON.stringify([...document.querySelectorAll('[role=menu][aria-label=Alvos] [role=menuitemcheckbox]')].map(b=>[b.innerText.replace('✓','').trim(),b.getAttribute('aria-checked')]))") or '[]')
    r0 = {t: rot(t) for t in TSR}
    alvo = next((o[0] for o in ops[1:] if any(o[0].lower() in r0[t].lower() for t in TSR)), ops[1][0] if len(ops) > 1 else '')
    J(f"[...document.querySelectorAll('[role=menu][aria-label=Alvos] [role=menuitemcheckbox]')].find(b=>b.innerText.replace('✓','').trim()==={json.dumps(alvo)}).click()"); time.sleep(.8)
    r1 = {t: rot(t) for t in TSR}
    bt1 = J("document.querySelector('button[data-alv]').innerText.replace(/\\s+/g,' ').trim()")
    so = all((alvo.lower() in r1[t].lower()) or r1[t].startswith('sem ') for t in TSR)
    chk(f'A1 "Alvos · Todos"; lista com Todos + {len(ops) - 1} alvos; marcar {alvo} foca nele (os outros rótulos: "sem …")',
        bt.startswith('Todos') and ops and ops[0] == ['Todos', 'true'] and len(ops) > 2 and bt1.startswith(alvo) and so and r1 != r0, [bt, ops, r0, r1, bt1])
    outro = next(o[0] for o in ops[1:] if o[0] != alvo)
    J(f"[...document.querySelectorAll('[role=menu][aria-label=Alvos] [role=menuitemcheckbox]')].find(b=>b.innerText.replace('✓','').trim()==={json.dumps(outro)}).click()"); time.sleep(.8)
    bt2 = J("document.querySelector('button[data-alv]').innerText.replace(/\\s+/g,' ').trim()")
    marc = json.loads(J("JSON.stringify([...document.querySelectorAll('[role=menu][aria-label=Alvos] [aria-checked=true]')].map(b=>b.innerText.replace('✓','').trim()))") or '[]')
    J("document.querySelector('[role=menu][aria-label=Alvos]').dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true}))"); time.sleep(.6)
    fechou = not J("!!document.querySelector('[role=menu][aria-label=Alvos]')"); foco = J("!!(document.activeElement&&document.activeElement.hasAttribute('data-alv'))")
    J("document.querySelector('button[data-alv]').click()"); time.sleep(.4)
    J("[...document.querySelectorAll('[role=menu][aria-label=Alvos] [role=menuitemcheckbox]')][0].click()"); time.sleep(.8)
    bt3 = J("document.querySelector('button[data-alv]').innerText.replace(/\\s+/g,' ').trim()"); r3 = {t: rot(t) for t in TSR}
    chk('A2 2º alvo soma ("2 de N", os dois marcados); Esc fecha com foco no botão; "Todos" volta ao todo',
        bt2.startswith(f'2 de {len(ops) - 1}') and set(marc) == {alvo, outro} and fechou and foco and bt3.startswith('Todos') and r3 == r0, [bt2, marc, fechou, foco, bt3])
    err = J("window.__err||''")
    c.aparelho(390, 844, 2, True); abre({'mf_faz': 'Santa Rita', 'lay': 'MIP/MID'})
    lat = J("document.documentElement.scrollWidth>window.innerWidth+1")
    chk('J sem erro de JS; 390 px sem rolagem lateral', not err and not lat and not J("window.__err||''"), [err, lat])
finally:
    c.close() if hasattr(c, 'close') else None
print(f'RESULTADO: {len(OK)}/{len(OK) + len(FAIL)}' + (' · FALHAS: ' + '; '.join(FAIL) if FAIL else ''))
sys.exit(1 if FAIL else 0)
