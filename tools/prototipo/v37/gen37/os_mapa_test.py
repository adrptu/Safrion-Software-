"""EX-55 F1 · visão Mapa da O.S. (navegador real, dados sintéticos, perfil descartável).

Aceite (docs/mapa/EX-55-validacao-claude.md §4 e §6):
  M1 paridade com o Mapa da fazenda: com Fazenda e Safra iguais às do IN-04, a classe e o rótulo de cada talhão são os do IN-04 em cada
     "Mostrar" (Fases, Avanço, Atrasos, Impedimentos). O oráculo é o pacote do coletor A2 do IN-04 no MESMO render (MAPA_A2_PACK);
     sem o pacote, M1 sai como "não executado" e o teste não passa.
  M2 recorte: a busca por uma O.S. pinta só os talhões dela, e o talhão com outra O.S. filtrada fora pinta só pela visível; o Mapa e as
     Frentes mostram a busca em chip removível (a busca fica na Tabela; sem o chip, o recorte ficaria escondido).
  M3 clique: talhão com uma O.S. abre essa O.S.; com várias, a lista curta, e cada item abre a sua.
  M4 teclado: Enter no talhão faz o mesmo que o clique; talhão fora do recorte sai do Tab; a dica tem 3 ou 4 valores.
  M5 endereço: ?view=mapa reabre a visão; recarregar mantém.
  M6 escala: selo "posição esquemática" só na Santa Rita; legenda com contagem.
  M7 Mapa da fazenda: o link leva fazenda e camada (#faz=…&lay=os) e grava o "Mostrar" no contexto do Mapa.
  M8 O.S. só com o selo cinza "Demonstração" não vira pendência em Impedimentos.
  M9 390 px: sem rolagem lateral; talhões com alvo de toque ≥ 44 px; nenhum erro de script.
"""
import json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, servir

OK, FAIL = [], []
def chk(n, c, info=''):
    (OK if c else FAIL).append(n); print(('OK    ' if c else 'FALHA ') + n + ('' if c else ' · ' + str(info)[:700]), flush=True)

R = os.environ.get('RENDER_DIR') or os.path.join(HERE, '_render')
PACK = os.environ.get('MAPA_A2_PACK')
p, srv = servir(R); c = Chrome(); J = c.js
U = lambda pg: f'http://127.0.0.1:{p}/{pg}'
SAF_ATUAL = '2026/27'   # safra padrão do IN-04 (coleta A2) e da O.S.
VERS = ['Fases', 'Avanço', 'Atrasos', 'Impedimentos']
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
    return json.loads(J("""JSON.stringify([...document.querySelectorAll('[data-mapa-emb=om] .me-t')].filter(g=>g.getClientRects().length).map(g=>({t:g.dataset.t,c:g.dataset.c,al:g.getAttribute('aria-label'),tab:g.getAttribute('tabindex')})))""") or '[]')
def mostrar(v):
    J(f"""[...document.querySelectorAll('[data-mapa-emb=om] .me-bt')].find(b=>b.innerText.trim()==={json.dumps(v)}).click()"""); time.sleep(.35)
def abre(w=1440, m=False):
    c.aparelho(w, 844 if m else 900, 2 if m else 1, m)
    c.goto(U('Main.dc.html'), .3); J("localStorage.clear(); sessionStorage.clear(); 1")
    c.goto(U('OS.dc.html?view=mapa'), 1.2); espera("!!document.querySelector('[data-mapa-emb=om] .me-t')")
def painel_os():   # O.S. aberta no detalhe (painel lateral da lista)
    return J("(()=>{const a=[...document.querySelectorAll('aside,[role=dialog]')].filter(x=>x.getClientRects().length).map(x=>x.innerText).join(' ');return (a.match(/OS-0\\d{3}/)||[''])[0];})()")

try:
    c.call('Page.addScriptToEvaluateOnNewDocument', {'source': "window.__err=[];addEventListener('error',e=>{window.__err.push(e.message||'erro');});"})
    abre()
    # ---- M1 paridade com o IN-04 (mesmo render, coletor A2) ----
    if PACK and os.path.exists(PACK):
        pk = json.load(open(PACK, encoding='utf-8')); dif = []; n = 0
        for faz in ('Santa Rita', 'Lagoa Grande'):
            # o IN-04 e a O.S. filtram a safra exata (osSaf em areas/inicio.py; PRD 8.4): mesma safra dos dois lados, a atual do coletor A2
            sel('Filtrar por fazenda', faz); sel('Filtrar por safra', SAF_ATUAL)
            for v in VERS:
                mostrar(v); got = {x['t']: x for x in talhoes()}
                for r in pk[f'{faz}|OS|{v}|Todas']['linhas']:
                    t = idGeo(r['id']); g = got.get(t); n += 1
                    if r['l'].startswith('sem ordem'):
                        if not g or g['c'] != 'fora': dif.append((faz, v, t, r, g))
                    elif not g or g['c'] != r['c'] or not g['al'].startswith(t + ' · ' + r['l'] + ' · '): dif.append((faz, v, t, r, g))
        chk(f'M1 paridade com o Mapa da fazenda: {n} talhões × "Mostrar" nas 2 fazendas, classe e rótulo iguais', not dif and n > 0, dif[:4])
    else:
        chk('M1 paridade com o Mapa da fazenda: NÃO EXECUTADO (defina MAPA_A2_PACK com o pacote A2 do IN-04 deste render)', False)
    abre()
    sel('Filtrar por fazenda', 'Santa Rita'); mostrar('Fases')
    # ---- M6 escala e legenda ----
    chk('M6 Santa Rita: selo "posição esquemática" e legenda com contagem',
        espera("(document.querySelector('.me-esq')||{}).innerText===undefined?false:document.querySelector('.me-esq').getClientRects().length>0")
        and J("[...document.querySelectorAll('[data-mapa-emb=om] .me-li')].every(e=>/\\d+$/.test(e.innerText.trim()))"))
    # ---- M3 clique: uma O.S. abre; várias abrem a lista curta ----
    tal = {x['t']: x for x in talhoes()}
    um = next((t for t, x in tal.items() if x['c'] != 'fora' and ' · 1 O.S. · ' in x['al']), None)
    varios = next((t for t, x in tal.items() if x['c'] != 'fora' and ' · 1 O.S. · ' not in x['al']), None)
    alvo1 = tal[um]['al'].split('Enter abre ')[-1] if um else ''
    J(f"document.querySelector('[data-mapa-emb=om] .me-t[data-t=\"{um}\"]').dispatchEvent(new MouseEvent('click',{{bubbles:true}}))"); time.sleep(.6)
    chk(f'M3a clique em {um} (uma O.S.) abre {alvo1}', bool(um) and espera(f"(()=>{{const a=[...document.querySelectorAll('aside,[role=dialog]')].filter(x=>x.getClientRects().length).map(x=>x.innerText).join(' ');return a.includes({json.dumps(alvo1)});}})()"), painel_os())
    abre(); sel('Filtrar por fazenda', 'Santa Rita')
    J(f"document.querySelector('[data-mapa-emb=om] .me-t[data-t=\"{varios}\"]').dispatchEvent(new MouseEvent('click',{{bubbles:true}}))"); time.sleep(.4)
    itens = json.loads(J("JSON.stringify([...document.querySelectorAll('[data-mapa-emb=om] .me-curta .me-bt')].map(b=>b.innerText.trim()))") or '[]')
    nv = int(tal[varios]['al'].split(' O.S. · ')[0].split(' · ')[-1]) if varios else -1
    chk(f'M3b clique em {varios} ({nv} O.S.) abre a lista curta com as {nv} e o Fechar', bool(varios) and len(itens) == nv + 1 and itens[-1] == 'Fechar', itens)
    prim = itens[0].split(' · ')[0] if itens else ''
    J("document.querySelector('[data-mapa-emb=om] .me-curta .me-bt').click()"); time.sleep(.6)
    chk(f'M3c item da lista curta abre {prim}', bool(prim) and espera(f"(()=>{{const a=[...document.querySelectorAll('aside,[role=dialog]')].filter(x=>x.getClientRects().length).map(x=>x.innerText).join(' ');return a.includes({json.dumps(prim)});}})()"), painel_os())
    # ---- M4 teclado ----
    abre(); sel('Filtrar por fazenda', 'Santa Rita'); tal = {x['t']: x for x in talhoes()}
    fora = [t for t, x in tal.items() if x['c'] == 'fora']
    chk('M4a talhão fora do recorte sai do Tab (tabindex -1); os do recorte ficam (0)', all(tal[t]['tab'] == '-1' for t in fora) and all(x['tab'] == '0' for t, x in tal.items() if x['c'] != 'fora'), tal)
    chk('M4b a dica tem talhão, situação, contagem e o que o Enter faz', all(len(x['al'].split(' · ')) >= 4 for x in tal.values() if x['c'] != 'fora'), [x['al'] for x in tal.values()][:3])
    J(f"document.querySelector('[data-mapa-emb=om] .me-t[data-t=\"{um}\"]').focus()"); c.tecla('Enter', 'Enter', 13, text='\r'); time.sleep(.6)
    chk(f'M4c Enter no talhão {um} abre {alvo1}', espera(f"(()=>{{const a=[...document.querySelectorAll('aside,[role=dialog]')].filter(x=>x.getClientRects().length).map(x=>x.innerText).join(' ');return a.includes({json.dumps(alvo1)});}})()"), painel_os())
    # ---- M2 recorte: busca por uma O.S. (a busca fica na Tabela; Mapa e Frentes mostram o recorte em chips removíveis) ----
    def visao(k):
        J(f"document.querySelector('[role=toolbar] [data-visao={k}]').click()"); time.sleep(.6)
    def chips():
        return J("(()=>{const g=[...document.querySelectorAll('[data-os-recorte]')].find(x=>x.getClientRects().length); return g?g.innerText.replace(/\\s+/g,' ').trim():'';})()") or ''
    abre(); sel('Filtrar por fazenda', 'Santa Rita'); visao('lista'); espera("[...document.querySelectorAll('input[type=search]')].some(x=>x.getClientRects().length)")
    J("""(()=>{const i=[...document.querySelectorAll('input[type=search]')].find(x=>x.getClientRects().length&&/busc/i.test((x.getAttribute('aria-label')||'')+(x.placeholder||'')));
      const d=Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value'); d.set.call(i,'OS-0421'); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true}));})()"""); time.sleep(.8)
    visao('mapa'); espera("!!document.querySelector('[data-mapa-emb=om] .me-t')")
    tal = {x['t']: x for x in talhoes()}; pint = sorted(t for t, x in tal.items() if x['c'] != 'fora')
    chk('M2 busca "OS-0421": só T1 e T2 pintados, e o T1 (com outras O.S. fora do recorte) pinta só pela OS-0421',
        pint == ['T1', 'T2'] and tal['T1']['al'].startswith('T1 · OS-0421 · ') and ' · 1 O.S. · ' in tal['T1']['al'], (pint, tal.get('T1')))
    chk('M2b contador do recorte: "2 talhões · 1 O.S. no mapa"', (J("document.querySelector('[data-mapa-emb=om] .me-cont').innerText") or '').startswith('2 talhões · 1 O.S. no mapa'),
        J("document.querySelector('[data-mapa-emb=om] .me-cont').innerText"))
    ch = chips()
    chk('M2c o Mapa mostra o recorte: chip "Busca: “OS-0421”" visível (a busca não fica escondida)', 'Busca: “OS-0421”' in ch, ch)
    visao('frentes'); ch2 = chips()
    chk('M2d as Frentes mostram o mesmo recorte (mesmo chip da busca)', 'Busca: “OS-0421”' in ch2, ch2)
    visao('mapa'); J("[...document.querySelectorAll('[data-os-recorte] button')].find(b=>b.getAttribute('aria-label')==='Limpar a busca').click()"); time.sleep(.7)
    tal = {x['t']: x for x in talhoes()}; pint2 = sorted(t for t, x in tal.items() if x['c'] != 'fora')
    chk('M2e o × do chip limpa a busca no próprio Mapa: o recorte volta à fazenda inteira e o chip some', len(pint2) > 2 and 'Busca:' not in chips(), (pint2, chips()))
    # ---- M8 selo cinza "Demonstração" não é pendência ----
    abre(); sel('Filtrar por fazenda', 'Santa Rita'); mostrar('Impedimentos'); tal = {x['t']: x for x in talhoes()}
    chk('M8 Impedimentos: nenhum talhão em amarelo por "demonstração" (selo cinza é informativo)', not any('demonstração' in x['al'] for x in tal.values()), [x['al'] for x in tal.values()])
    # ---- M7 Mapa da fazenda ----
    lk = J("document.querySelector('[data-mapa-emb=om] .me-lk').getAttribute('href')")
    J("(()=>{const a=document.querySelector('[data-mapa-emb=om] .me-lk'); a.addEventListener('click',e=>e.preventDefault(),{once:true}); a.click();})()"); time.sleep(.2)
    ctx = json.loads(J("sessionStorage.getItem('mapa-ctx')") or 'null')
    chk('M7 "Abrir no Mapa da fazenda" leva #faz=SR&lay=os e grava o "Mostrar" (Impedimentos) no contexto do Mapa',
        lk == 'IN-04.dc.html#faz=SR&lay=os' and ctx and ctx.get('lay') == 'O.S./prazos' and ctx['flt']['O.S./prazos']['ver'] == 'Impedimentos', (lk, ctx))
    # ---- M5 endereço ----
    abre(); vis1 = J("!!document.querySelector('[data-os-mapa]')&&document.querySelector('[data-os-mapa]').getClientRects().length>0")
    c.goto(U('OS.dc.html?view=mapa'), 1.2); vis2 = espera("!!document.querySelector('[data-os-mapa]')&&document.querySelector('[data-os-mapa]').getClientRects().length>0")
    chk('M5 ?view=mapa abre a visão Mapa e recarregar mantém', bool(vis1) and vis2 and 'view=mapa' in (J('location.search') or ''))
    # ---- M6b Lagoa Grande sem selo esquemático ----
    sel('Filtrar por fazenda', 'Lagoa Grande'); time.sleep(.4)
    chk('M6b Lagoa Grande (projeção em lon/lat): sem o selo esquemático', not J("!!document.querySelector('.me-esq')&&document.querySelector('.me-esq').getClientRects().length>0"))
    # ---- M9 390 px ----
    abre(390, True); sel('Filtrar por fazenda', 'Santa Rita')
    alvo = json.loads(J("JSON.stringify([...document.querySelectorAll('[data-mapa-emb=om] .me-t')].filter(g=>g.getClientRects().length&&g.dataset.c!=='fora').map(g=>{const r=g.getBoundingClientRect();return [g.dataset.t,Math.round(r.width),Math.round(r.height)];}))") or '[]')
    chk('M9a 390 px: sem rolagem lateral', J('document.documentElement.scrollWidth<=innerWidth+1'))
    chk('M9b 390 px: talhões do recorte com alvo de toque ≥ 44 px', alvo and all(w >= 44 and h >= 44 for _, w, h in alvo), alvo)
    chk('M9c nenhum erro de script', J("(window.__err||[]).length===0"), J("JSON.stringify(window.__err||[])"))
finally:
    c.close(); srv.terminate()
print(f'RESULTADO: {len(OK)}/{len(OK) + len(FAIL)}', flush=True)
sys.exit(1 if FAIL else 0)
