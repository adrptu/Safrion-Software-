"""EX-55 F1 · visão Mapa de Pragas e doenças (AG-01; navegador real, dados sintéticos, perfil descartável).

Aceite (docs/mapa/EX-55-validacao-claude.md §4):
  P1 paridade com o Mapa da fazenda: sem filtro (cultura, talhão e situação "Todas"), a classe e o rótulo de cada talhão são os da camada
     MIP do IN-04 em "Últimos 7 dias" e "Últimos 30 dias", nas 2 fazendas. Oráculo: pacote do coletor A2 do IN-04 no MESMO render
     (MAPA_A2_PACK, casos "MIP|7|sem alvo" e "MIP|30|sem alvo"); sem o pacote, P1 sai "não executado" e o teste não passa.
  P2 recorte: o chip de situação "Acima do NC" pinta só os talhões que o IN-04 mostra em vermelho; a Cultura "Feijão" deixa só os talhões de
     feijão (dados_mip.TAL); o resto fica neutro e fora do Tab.
  P3 clique: talhão com uma vistoria no período abre essa vistoria; com várias, a lista curta (cada item abre a sua); sem vistoria no
     período e com protocolo, abre "Programar vistoria" já no talhão.
  P4 teclado: Enter faz o mesmo que o clique; a dica tem talhão, situação, contagem e o que o Enter faz.
  P5 endereço: ?view=mapa reabre a visão.
  P6 escala: selo "posição esquemática" na Santa Rita; "sem cultura" em hachura e contado na legenda.
  P7 Mapa da fazenda: o link leva #faz=…&lay=pragas e grava o período no contexto do Mapa.
  P8 390 px: sem rolagem lateral; talhões com alvo de toque ≥ 44 px; nenhum erro de script.
"""
import json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, servir
import dados_mip as DM

OK, FAIL = [], []
def chk(n, c, info=''):
    (OK if c else FAIL).append(n); print(('OK    ' if c else 'FALHA ') + n + ('' if c else ' · ' + str(info)[:700]), flush=True)

R = os.environ.get('RENDER_DIR') or os.path.join(HERE, '_render')
PACK = os.environ.get('MAPA_A2_PACK')
p, srv = servir(R); c = Chrome(); J = c.js
U = lambda pg: f'http://127.0.0.1:{p}/{pg}'
PERS = {'7': 'Últimos 7 dias', '30': 'Últimos 30 dias'}
def idGeo(t):
    return 'Pivô %d' % int(t[2:]) if t.startswith('PV') and t[2:].isdigit() else t
def espera(expr, lim=8.0):
    t0 = time.time()
    while time.time() - t0 < lim:
        try:
            if J(expr): return True
        except Exception: pass
        time.sleep(.05)
    return False
def sel(al, val):
    J(f"""(()=>{{const s=document.querySelector('select[aria-label="{al}"]'); if(!s) return; s.value={json.dumps(val)}; s.dispatchEvent(new Event('change',{{bubbles:true}}));}})()"""); time.sleep(.5)
def talhoes():
    return json.loads(J("""JSON.stringify([...document.querySelectorAll('[data-mapa-emb=mi] .me-t')].filter(g=>g.getClientRects().length).map(g=>({t:g.dataset.t,c:g.dataset.c,al:g.getAttribute('aria-label'),tab:g.getAttribute('tabindex')})))""") or '[]')
def mostrar(v):
    J(f"""[...document.querySelectorAll('[data-mapa-emb=mi] .me-bt')].find(b=>b.innerText.trim()==={json.dumps(v)}).click()"""); time.sleep(.35)
def chip(t):
    J(f"""[...document.querySelectorAll('[aria-label="Filtrar por situação"] button')].find(b=>b.innerText.trim().startsWith({json.dumps(t)})).click()"""); time.sleep(.5)
def toca(t):
    J(f"""document.querySelector('[data-mapa-emb=mi] .me-t[data-t="{t}"]').dispatchEvent(new MouseEvent('click',{{bubbles:true}}))"""); time.sleep(.6)
def abre(w=1440, m=False, faz='Santa Rita'):
    c.aparelho(w, 844 if m else 900, 2 if m else 1, m)
    c.goto(U('Main.dc.html'), .3); J("localStorage.clear(); sessionStorage.clear(); 1")
    c.goto(U('AG-01.dc.html?view=mapa'), 1.2); espera("!!document.querySelector('[data-mapa-emb=mi] .me-t')")
    if faz: sel('Filtrar por fazenda', faz)

try:
    c.call('Page.addScriptToEvaluateOnNewDocument', {'source': "window.__err=[];addEventListener('error',e=>{window.__err.push(e.message||'erro');});"})
    abre(faz='')
    # ---- P1 paridade com o IN-04 (mesmo render, coletor A2) ----
    pk = json.load(open(PACK, encoding='utf-8')) if PACK and os.path.exists(PACK) else None
    if pk:
        dif = []; n = 0
        for faz in ('Santa Rita', 'Lagoa Grande'):
            sel('Filtrar por fazenda', faz)
            for d, per in PERS.items():
                mostrar(per); got = {x['t']: x for x in talhoes()}
                for r in pk[f'{faz}|MIP|{d}|sem alvo']['linhas']:
                    t = idGeo(r['id']); g = got.get(t); n += 1
                    if not g or g['c'] != r['c'] or not g['al'].startswith(t + ' · ' + r['l'] + ' · '): dif.append((faz, per, t, r, g))
        chk(f'P1 paridade com o Mapa da fazenda: {n} talhões × período nas 2 fazendas, classe e rótulo iguais', not dif and n > 0, dif[:4])
    else:
        chk('P1 paridade com o Mapa da fazenda: NÃO EXECUTADO (defina MAPA_A2_PACK com o pacote A2 do IN-04 deste render)', False)
    # ---- P2 recorte: situação e cultura ----
    abre(); chip('Acima do NC'); tal = {x['t']: x for x in talhoes()}
    pint = sorted(t for t, x in tal.items() if x['c'] != 'fora')
    esper = sorted(idGeo(r['id']) for r in (pk or {}).get('Santa Rita|MIP|7|sem alvo', {}).get('linhas', []) if r['c'] == 'red')
    chk('P2a chip "Acima do NC": pinta só os talhões em vermelho no IN-04; os outros ficam neutros e fora do Tab',
        bool(esper) and pint == esper and all(x['tab'] == '-1' for t, x in tal.items() if x['c'] == 'fora'), (pint, esper))
    abre(); sel('Filtrar por cultura', 'Feijão'); tal = {x['t']: x for x in talhoes()}
    pint = sorted(t for t, x in tal.items() if x['c'] != 'fora')
    esper = sorted(idGeo(k) for k, x in DM.TAL.items() if x.get('faz') == 'Santa Rita' and x.get('cultura') == 'Feijão')
    chk('P2b Cultura "Feijão": só os talhões de feijão da Santa Rita no mapa', bool(esper) and pint == esper, (pint, esper))
    # ---- P3 clique ----
    abre(); tal = {x['t']: x for x in talhoes()}
    um = next((t for t, x in tal.items() if ' · 1 vistoria no período · Enter abre VIS-' in x['al']), None)
    varios = next((t for t, x in tal.items() if 'Enter abre a lista do talhão' in x['al']), None)
    nenhum = next((t for t, x in tal.items() if 'Enter programa a vistoria' in x['al']), None)
    vid = tal[um]['al'].rsplit('Enter abre ', 1)[1] if um else ''
    if um: toca(um)
    chk(f'P3a clique em {um} (uma vistoria) abre {vid}', bool(um) and J('location.hash') == '#' + vid, (um, J('location.hash')))
    abre()
    if varios: toca(varios)
    curta = json.loads(J("JSON.stringify([...document.querySelectorAll('[data-mapa-emb=mi] .me-curta .me-bt')].filter(b=>b.getClientRects().length).map(b=>b.innerText.trim()))") or '[]')
    n_v = int(tal[varios]['al'].split(' · ')[-2].split(' ')[0]) if varios else 0
    chk(f'P3b clique em {varios} (várias) abre a lista curta com {n_v} vistorias e o Fechar', bool(varios) and len(curta) == n_v + 1 and curta[-1] == 'Fechar', curta)
    alvo = curta[0].split(' · ')[0] if curta else ''
    if curta: J("[...document.querySelectorAll('[data-mapa-emb=mi] .me-curta .me-bt')][0].click()"); time.sleep(.6)
    chk(f'P3c item da lista curta abre {alvo}', bool(alvo) and J('location.hash') == '#' + alvo, J('location.hash'))
    abre()
    if nenhum: toca(nenhum)
    pv = J("(()=>{const s=document.getElementById('pv_tal'); return s&&s.getClientRects().length?s.value:'';})()")
    chk(f'P3d clique em {nenhum} (sem vistoria no período) abre "Programar vistoria" no talhão', bool(nenhum) and idGeo(pv or '') == nenhum, (nenhum, pv))
    # ---- P4 teclado e dica ----
    abre(); tal = {x['t']: x for x in talhoes()}
    chk('P4a a dica tem talhão, situação, contagem e o que o Enter faz', all(len(x['al'].split(' · ')) >= 4 for x in tal.values()), [x['al'] for x in tal.values()][:3])
    if um:
        J(f"document.querySelector('[data-mapa-emb=mi] .me-t[data-t=\"{um}\"]').focus()"); c.tecla('Enter', 'Enter', 13, text='\r'); time.sleep(.6)
    chk(f'P4b Enter no talhão {um} abre {vid}', bool(um) and J('location.hash') == '#' + vid, J('location.hash'))
    # ---- P5 endereço ----
    abre(); vis1 = J("location.search.indexOf('view=mapa')>=0")
    c.goto(U('AG-01.dc.html?view=mapa'), 1.2); vis2 = espera("!!document.querySelector('[data-mip-mapa]')&&document.querySelector('[data-mip-mapa]').getClientRects().length>0")
    chk('P5 ?view=mapa abre a visão Mapa e recarregar mantém', bool(vis1) and vis2)
    # ---- P6 escala e hachura ----
    abre()
    chk('P6a Santa Rita: selo "posição esquemática"; legenda com contagem', espera("[...document.querySelectorAll('[data-mapa-emb=mi] .me-esq')].some(e=>e.getClientRects().length)")
        and J("[...document.querySelectorAll('[data-mapa-emb=mi] .me-li')].every(e=>/\\d+$/.test(e.innerText.trim()))"))
    sel('Filtrar por fazenda', 'Lagoa Grande'); tal = {x['t']: x for x in talhoes()}
    semc = [t for t, x in tal.items() if x['c'] == 'none']
    leg = J("(()=>{const e=[...document.querySelectorAll('[data-mapa-emb=mi] .me-li')].find(e=>/sem cultura/.test(e.innerText)); return e?e.innerText.trim():'';})()") or ''
    hach = J(f"(()=>{{const g=document.querySelector('[data-mapa-emb=mi] .me-t[data-t=\"{semc[0] if semc else ''}\"]'); return g?g.querySelectorAll('path')[1].getAttribute('opacity'):'';}})()")
    chk('P6b Lagoa Grande: "sem cultura" em hachura e contado na legenda', bool(semc) and hach == '1' and leg.endswith(str(len(semc))), (semc, hach, leg))
    # ---- P7 Mapa da fazenda ----
    abre(); mostrar('Últimos 30 dias')
    href = J("document.querySelector('[data-mapa-emb=mi] .me-lk').getAttribute('href')")
    J("document.querySelector('[data-mapa-emb=mi] .me-lk').dispatchEvent(new MouseEvent('click',{bubbles:true,cancelable:true}))"); time.sleep(.3)
    ctx = json.loads(J("sessionStorage.getItem('mapa-ctx')") or '{}')
    chk('P7 "Abrir no Mapa da fazenda" leva #faz=SR&lay=pragas e grava o período (30 dias) no contexto do Mapa',
        href == 'IN-04.dc.html#faz=SR&lay=pragas' and ctx.get('lay') == 'MIP/MID' and (ctx.get('flt') or {}).get('MIP/MID', {}).get('per') == 'Últimos 30 dias', (href, ctx))
    # ---- P8 390 px ----
    abre(390, True)
    chk('P8a 390 px: sem rolagem lateral', J("document.documentElement.scrollWidth<=innerWidth+1"), J("[document.documentElement.scrollWidth,innerWidth]"))
    peq = json.loads(J("JSON.stringify([...document.querySelectorAll('[data-mapa-emb=mi] .me-t')].filter(g=>g.getClientRects().length&&g.getAttribute('tabindex')==='0').map(g=>{const r=g.getBoundingClientRect();return [g.dataset.t,Math.round(r.width),Math.round(r.height)];}).filter(x=>x[1]<44||x[2]<44))") or '[]')
    chk('P8b 390 px: talhões do recorte com alvo de toque ≥ 44 px', not peq, peq)
    err = J("JSON.stringify(window.__err||[])")
    chk('P8c nenhum erro de script', err == '[]', err)
finally:
    c.close(); srv.terminate()
print(f'RESULTADO: {len(OK)}/{len(OK) + len(FAIL)}')
sys.exit(1 if FAIL else 0)
