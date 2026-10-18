"""EX-55 F1 · visão Mapa da Irrigação (IR-01; navegador real, dados sintéticos, perfil descartável).

Aceite (docs/mapa/EX-55-validacao-claude.md §4):
  I1 paridade com o Mapa da fazenda: pintados = os talhões com setor da fazenda (dados_irrigacao.seed()); em cada um, a classe e o rótulo
     são os da camada Irrigação do IN-04 em "Hoje" e "Balanço hídrico", nas 2 fazendas. Oráculo: pacote do coletor A2 do IN-04 no MESMO
     render (MAPA_A2_PACK, casos "IRR|Hoje" e "IRR|Balanço hídrico"); sem o pacote, I1 sai "não executado" e o teste não passa.
  I2 recorte: a busca "Gotejo" feita na Tabela deixa só o T7 no mapa; o chip da busca aparece no Mapa e o × dele volta aos 3 setores.
  I3 clique e I4 teclado: tocar ou Enter no talhão abre o formulário do setor (o mesmo da linha); a dica tem talhão, situação, setor e ação.
  I5 endereço: ?view=mapa reabre a visão.
  I6 escala: selo "posição esquemática" só na Santa Rita; legenda com contagem.
  I7 Mapa da fazenda: o link leva #faz=…&lay=irr e grava o "Mostrar" no contexto do Mapa.
  I8 390 px: sem rolagem lateral; talhões com alvo de toque ≥ 44 px; nenhum erro de script.
"""
import json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, servir
import dados_irrigacao as DI

OK, FAIL = [], []
def chk(n, c, info=''):
    (OK if c else FAIL).append(n); print(('OK    ' if c else 'FALHA ') + n + ('' if c else ' · ' + str(info)[:700]), flush=True)

R = os.environ.get('RENDER_DIR') or os.path.join(HERE, '_render')
PACK = os.environ.get('MAPA_A2_PACK')
p, srv = servir(R); c = Chrome(); J = c.js
U = lambda pg: f'http://127.0.0.1:{p}/{pg}'
VERS = ['Hoje', 'Balanço hídrico']
SET = DI.seed()['setores']
FAZN = {'SR': 'Santa Rita', 'LG': 'Lagoa Grande'}
def tal_geo(k, x):   # irrTal (irrigacao_estado.js): na Santa Rita o setor é o talhão; na Lagoa Grande, o nome do pivô
    return k if x['faz'] == 'SR' else x['nome']
COM_SETOR = {FAZN[f]: sorted(tal_geo(k, x) for k, x in SET.items() if x['faz'] == f) for f in FAZN}
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
    J(f"""(()=>{{const s=document.querySelector('select[aria-label="{al}"]'); if(!s) return; s.value={json.dumps(val)}; s.dispatchEvent(new Event('change',{{bubbles:true}}));}})()"""); time.sleep(.6)
def talhoes():
    return json.loads(J("""JSON.stringify([...document.querySelectorAll('[data-mapa-emb=irm] .me-t')].filter(g=>g.getClientRects().length).map(g=>({t:g.dataset.t,c:g.dataset.c,al:g.getAttribute('aria-label'),tab:g.getAttribute('tabindex')})))""") or '[]')
def mostrar(v):
    J(f"""[...document.querySelectorAll('[data-mapa-emb=irm] .me-bt')].find(b=>b.innerText.trim()==={json.dumps(v)}).click()"""); time.sleep(.4)
def visao(k):
    J(f"document.querySelector('[role=toolbar] [data-visao={k}]').click()"); time.sleep(.6)
def pintados():
    return sorted(x['t'] for x in talhoes() if x['c'] != 'fora')
def dialogo():
    return J("(()=>{const d=[...document.querySelectorAll('[role=dialog]')].filter(x=>x.getClientRects().length).map(x=>x.innerText).join(' ');return d;})()") or ''
def abre(w=1440, m=False, faz='Santa Rita'):
    c.aparelho(w, 844 if m else 900, 2 if m else 1, m)
    c.goto(U('Main.dc.html'), .3); J("localStorage.clear(); sessionStorage.clear(); 1")
    c.goto(U('IR-01.dc.html?view=mapa'), 1.2); espera("!!document.querySelector('[data-mapa-emb=irm] .me-t')")
    if faz: sel('Filtrar por fazenda', faz); espera("!!document.querySelector('[data-mapa-emb=irm] .me-t')")

try:
    c.call('Page.addScriptToEvaluateOnNewDocument', {'source': "window.__err=[];addEventListener('error',e=>{window.__err.push(e.message||'erro');});"})
    abre(faz='')
    # ---- I1 paridade com o IN-04 (mesmo render, coletor A2) ----
    pk = json.load(open(PACK, encoding='utf-8')) if PACK and os.path.exists(PACK) else None
    if pk:
        dif = []; n = 0
        for faz in ('Santa Rita', 'Lagoa Grande'):
            sel('Filtrar por fazenda', faz)
            for v in VERS:
                mostrar(v); got = {x['t']: x for x in talhoes()}
                pint = sorted(t for t, x in got.items() if x['c'] != 'fora')
                if pint != COM_SETOR[faz]: dif.append((faz, v, 'pintados', pint, COM_SETOR[faz]))
                for r in pk[f'{faz}|IRR|{v}']['linhas']:
                    t = idGeo(r['id'])
                    if t not in COM_SETOR[faz]: continue
                    g = got.get(t); n += 1
                    if not g or g['c'] != r['c'] or not g['al'].startswith(t + ' · ' + r['l'] + ' · '): dif.append((faz, v, t, r, g))
        chk(f'I1 paridade com o Mapa da fazenda: {n} talhões com setor × "Mostrar" nas 2 fazendas, classe e rótulo iguais; sem setor fica neutro', not dif and n > 0, dif[:4])
    else:
        chk('I1 paridade com o Mapa da fazenda: NÃO EXECUTADO (defina MAPA_A2_PACK com o pacote A2 do IN-04 deste render)', False)
    # ---- I2 recorte pela busca da Tabela ----
    abre(); visao('lista'); espera("[...document.querySelectorAll('input[type=search]')].some(x=>x.getClientRects().length)")
    J("""(()=>{const i=[...document.querySelectorAll('input[type=search]')].find(x=>x.getClientRects().length&&/busc/i.test((x.getAttribute('aria-label')||'')+(x.placeholder||'')));
      const d=Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value'); d.set.call(i,'Gotejo'); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true}));})()"""); time.sleep(.8)
    visao('mapa'); espera("!!document.querySelector('[data-mapa-emb=irm] .me-t')")
    p1 = pintados(); ch = J("(()=>{const g=document.querySelector('[data-mapa-emb=irm] [data-me-recorte]'); return g&&g.getClientRects().length?g.innerText.replace(/\\s+/g,' '):'';})()") or ''
    chk('I2a busca "Gotejo" na Tabela: só o T7 no mapa, com o chip da busca visível no Mapa', p1 == ['T7'] and 'Busca: “Gotejo”' in ch, (p1, ch))
    J("[...document.querySelectorAll('[data-mapa-emb=irm] [data-me-recorte] button')].find(b=>b.getAttribute('aria-label')==='Limpar a busca').click()"); time.sleep(.7)
    p2 = pintados()
    chk('I2b o × do chip limpa a busca no próprio Mapa: volta aos 3 setores da Santa Rita', p2 == COM_SETOR['Santa Rita'], p2)
    # ---- I3 clique e I4 teclado ----
    abre(); tal = {x['t']: x for x in talhoes()}
    chk('I4a a dica tem talhão, situação, setor e o que o Enter faz', all(len(x['al'].split(' · ')) >= 4 and ' · setor ' in x['al'] for x in tal.values() if x['c'] != 'fora'),
        [x['al'] for x in tal.values()][:3])
    J("document.querySelector('[data-mapa-emb=irm] .me-t[data-t=\"T7\"]').dispatchEvent(new MouseEvent('click',{bubbles:true}))"); time.sleep(.7)
    chk('I3 tocar no T7 abre o formulário do setor Gotejo T7', 'Gotejo T7' in dialogo(), dialogo()[:200])
    abre()
    J("document.querySelector('[data-mapa-emb=irm] .me-t[data-t=\"P1\"]').focus()"); c.tecla('Enter', 'Enter', 13, text='\r'); time.sleep(.7)
    chk('I4b Enter no P1 abre o formulário do setor Pivô 1', 'Pivô 1' in dialogo(), dialogo()[:200])
    # ---- I5 endereço ----
    abre(); vis1 = J("location.search.indexOf('view=mapa')>=0")
    c.goto(U('IR-01.dc.html?view=mapa'), 1.2); vis2 = espera("!!document.querySelector('[data-irr-mapa]')&&document.querySelector('[data-irr-mapa]').getClientRects().length>0")
    chk('I5 ?view=mapa abre a visão Mapa e recarregar mantém', bool(vis1) and vis2)
    # ---- I6 escala ----
    abre()
    esqSR = espera("[...document.querySelectorAll('[data-mapa-emb=irm] .me-esq')].some(e=>e.getClientRects().length)")
    leg = J("[...document.querySelectorAll('[data-mapa-emb=irm] .me-li')].every(e=>/\\d+$/.test(e.innerText.trim()))")
    sel('Filtrar por fazenda', 'Lagoa Grande')
    esqLG = J("[...document.querySelectorAll('[data-mapa-emb=irm] .me-esq')].some(e=>e.getClientRects().length)")
    chk('I6 selo "posição esquemática" só na Santa Rita; legenda com contagem', esqSR and not esqLG and leg, (esqSR, esqLG, leg))
    # ---- I7 Mapa da fazenda ----
    abre(); mostrar('Balanço hídrico')
    href = J("document.querySelector('[data-mapa-emb=irm] .me-lk').getAttribute('href')")
    J("document.querySelector('[data-mapa-emb=irm] .me-lk').dispatchEvent(new MouseEvent('click',{bubbles:true,cancelable:true}))"); time.sleep(.3)
    ctx = json.loads(J("sessionStorage.getItem('mapa-ctx')") or '{}')
    chk('I7 "Abrir no Mapa da fazenda" leva #faz=SR&lay=irr e grava o "Mostrar" (Balanço hídrico) no contexto do Mapa',
        href == 'IN-04.dc.html#faz=SR&lay=irr' and ctx.get('lay') == 'Irrigação' and (ctx.get('flt') or {}).get('Irrigação', {}).get('ver') == 'Balanço hídrico', (href, ctx))
    # ---- I8 390 px ----
    abre(390, True)
    chk('I8a 390 px: sem rolagem lateral', J("document.documentElement.scrollWidth<=innerWidth+1"), J("[document.documentElement.scrollWidth,innerWidth]"))
    peq = json.loads(J("JSON.stringify([...document.querySelectorAll('[data-mapa-emb=irm] .me-t')].filter(g=>g.getClientRects().length&&g.getAttribute('tabindex')==='0').map(g=>{const r=g.getBoundingClientRect();return [g.dataset.t,Math.round(r.width),Math.round(r.height)];}).filter(x=>x[1]<44||x[2]<44))") or '[]')
    chk('I8b 390 px: talhões do recorte com alvo de toque ≥ 44 px', not peq, peq)
    err = J("JSON.stringify(window.__err||[])")
    chk('I8c nenhum erro de script', err == '[]', err)
finally:
    c.close(); srv.terminate()
print(f'RESULTADO: {len(OK)}/{len(OK) + len(FAIL)}')
sys.exit(1 if FAIL else 0)
