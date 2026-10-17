# -*- coding: utf-8 -*-
"""MAPA-UX · medidas "antes" do IN-04 no render publicado (versão 1792184197-5a81, espelho local somente leitura).
Uso: SITE=<pasta do render> CHROME_BIN=/tmp/cloudchrome/chrome CDP_GL=1 python3 -I -B repro_mapa.py [saida.json]
Usa o cliente CDP do gerador (tools/prototipo/v37/gen37/cdp.py), perfil e porta próprios. Não grava nada no render.
Cada medida fica em try/except: falha de uma não esconde as outras; o erro vai para a saída."""
import sys, os, time, json, subprocess, math, traceback
AQUI = os.path.dirname(os.path.abspath(__file__))
G = os.environ.get('GEN37') or os.path.normpath(os.path.join(AQUI, '..', '..', '..', '..', '..', 'tools', 'prototipo', 'v37', 'gen37'))
sys.path.insert(0, G)
from cdp import Chrome
from journeys import free
SITE = os.environ['SITE']
SAIDA = sys.argv[1] if len(sys.argv) > 1 else os.path.join(AQUI, 'repro_mapa.json')
CTX = 'mapa' + '-ctx'   # chave do contexto do mapa no sessionStorage (variável, sem literal)
R = {'versao_publicada': '1792184197-5a81', 'site': os.path.basename(SITE.rstrip('/')), 'medidas': {}, 'erros': {}}
porta = free()
srv = subprocess.Popen([sys.executable, '-m', 'http.server', str(porta), '--bind', '127.0.0.1', '--directory', SITE], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(0.8)
c = Chrome(port=free(), w=1440, h=900)
J = c.js
c.call('Page.addScriptToEvaluateOnNewDocument', {'source': "window.__errs=[];window.addEventListener('error',e=>window.__errs.push(String(e.message)));"})
U = lambda f: f'http://127.0.0.1:{porta}/{f}'

def med(nome):
    def deco(fn):
        def run(*a, **k):
            t0 = time.time()
            try: R['medidas'][nome] = fn(*a, **k)
            except Exception as e: R['erros'][nome] = ''.join(traceback.format_exception_only(type(e), e)).strip()[:400]
            print(f'[{time.time()-t0:5.1f}s] {nome}: ' + ('ERRO ' + R['erros'][nome] if nome in R['erros'] else json.dumps(R['medidas'][nome], ensure_ascii=False)[:600]), flush=True)
        return run
    return deco

def espera(expr, s=45):
    fim = time.time() + s
    while time.time() < fim:
        try:
            if J(expr): return True
        except Exception: pass
        time.sleep(0.3)
    return False

def tela(w, h, toque=False):
    c.call('Emulation.setDeviceMetricsOverride', {'width': w, 'height': h, 'deviceScaleFactor': 1, 'mobile': w < 500})
    c.call('Emulation.setTouchEmulationEnabled', {'enabled': bool(toque), 'maxTouchPoints': 5 if toque else 1})

def abre(faz='Lagoa Grande', extra=None, hash_=''):
    """Abre o IN-04 limpo, com o contexto do mapa escolhido (fazenda e o resto em extra)."""
    c.goto(U('Main.dc.html'), wait=0.8)
    ctx = dict(mf_faz=faz); ctx.update(extra or {})
    J(f"localStorage.clear(); sessionStorage.clear(); sessionStorage.setItem({json.dumps(CTX)}, {json.dumps(json.dumps(ctx))}); 1")
    t0 = time.time(); c.goto(U('IN-04.dc.html' + hash_), wait=1.0)
    ok = True
    if faz == 'Lagoa Grande': ok = espera('!!(window.__LGI&&window.__LGI.pronto)', 60)
    else: ok = espera("!!document.querySelector('svg[aria-label=\"Mapa da fazenda Santa Rita\"]')", 20)
    time.sleep(0.8)
    return ok, round(time.time() - t0, 1)

def tecla(key, code=None, vk=None, shift=False):
    p = {'key': key, 'code': code or key, 'windowsVirtualKeyCode': vk or 0, 'nativeVirtualKeyCode': vk or 0, 'modifiers': 8 if shift else 0}
    c.call('Input.dispatchKeyEvent', dict(p, type='rawKeyDown')); c.call('Input.dispatchKeyEvent', dict(p, type='keyUp'))

def mouse(x, y, clicar=False):
    c.call('Input.dispatchMouseEvent', {'type': 'mouseMoved', 'x': x, 'y': y})
    if clicar:
        c.call('Input.dispatchMouseEvent', {'type': 'mousePressed', 'x': x, 'y': y, 'button': 'left', 'clickCount': 1})
        c.call('Input.dispatchMouseEvent', {'type': 'mouseReleased', 'x': x, 'y': y, 'button': 'left', 'clickCount': 1})

FOCO = """(()=>{const a=document.activeElement; if(!a||a===document.body) return {t:'BODY'}; const r=a.getBoundingClientRect();
  return {t:a.tagName, role:a.getAttribute('role')||'', nome:(a.getAttribute('aria-label')||a.innerText||'').replace(/\\s+/g,' ').trim().slice(0,60),
    mapa:!!a.closest('.mapa-area'), real:!!a.closest('#mapa-real'), svg:!!a.closest('svg'), canvas:a.classList.contains('maplibregl-canvas'), talhao:!!a.closest('svg [role=button]')||a.matches('svg [role=button]'), w:Math.round(r.width), h:Math.round(r.height)};})()"""

# centro de um talhão na tela: Santa Rita pelo polígono do SVG; Lagoa Grande pela projeção do centro do pivô
CENTRO_SR = """((t)=>{const e=[...document.querySelectorAll('svg [role=button]')].find(x=>(x.getAttribute('aria-label')||'').startsWith(t+':')); if(!e) return null; const r=e.getBoundingClientRect(); return [r.left+r.width/2, r.top+r.height/2];})"""
CENTRO_LG = """((id)=>{const L=window.__LGI, m=L&&L.map; const mk=L&&L.markers[id]; if(!m||!mk) return null; const ll=mk.getLngLat(); const p=m.project(ll); const r=m.getContainer().getBoundingClientRect(); return [r.left+p.x, r.top+p.y];})"""
TABS = "[...document.querySelectorAll('nav[role=tablist] [role=tab]')].filter(b=>b.offsetParent)"
FECHA = "(()=>{const b=document.querySelector('.mapa-linha aside button[aria-label=\"Fechar painel\"]'); if(b) b.click(); return 1;})()"
PAINEL = """(()=>{const a=document.querySelector('.mapa-linha aside[aria-label]'); if(!a) return null; const r=a.getBoundingClientRect();
  const verde=[...a.querySelectorAll('a,button')].filter(b=>getComputedStyle(b).backgroundColor==='rgb(30, 122, 76)'&&b.offsetParent).map(b=>b.innerText.replace(/\\s+/g,' ').trim());
  return {titulo:(a.querySelector('h2')||{}).innerText||'', top:Math.round(r.top), bottom:Math.round(r.bottom), alturaJanela:innerHeight, verdes:verde};})()"""

def talhoes_sr():
    return J("""[...document.querySelectorAll('svg [role=button]')].map(e=>({id:(e.getAttribute('aria-label')||'').split(':')[0], rot:(e.getAttribute('aria-label')||'').split(': ').slice(1).join(': '), fill:e.getAttribute('fill')}))""") or []

def talhoes_lg():
    return J("""(()=>{const L=window.__LGI, m=L.map; const ex=m.getPaintProperty('pv-fill','fill-color'); const op=m.getPaintProperty('pv-fill','fill-opacity'); const cor={}, opa={};
      for(let i=2;i<ex.length-1;i+=2){ cor[ex[i]]=ex[i+1]; } for(let i=2;i<op.length-1;i+=2){ opa[op[i]]=op[i+1]; }
      return Object.keys(L.markers).map(id=>({id, rot:(L.markers[id].getElement().getAttribute('aria-label')||'').split(': ').slice(1).join(': '), fill:cor[id], opac:opa[id]}));})()""") or []

LCOP = {'#7FAE68': 'ok', '#5F8F55': 'good', '#A9C06A': 'lime', '#D4B25A': 'yellow', '#D98A4E': 'orange', '#C8553D': 'red', '#C9CFCB': 'gray', '#6E9FC6': 'blue', '#44739A': 'navy', '#E4E9DF': 'none', '#9B8BC4': 'purple', 'url(#hatch)': 'cloud'}
SEV = ['red', 'orange', 'yellow', 'cloud', 'lime', 'ok', 'good', 'navy', 'blue', 'purple', 'gray', 'none']
VIGOR = ['#E4002B', '#FF6A00', '#FFD500', '#B5E61D', '#3FBF2A', '#0B7A1E']
def pior(ts):
    """talhão mais crítico da camada: ordem SEV do próprio protótipo (inicio.py:659); cor viva (satélite/solo) pela classe mais baixa."""
    def k(t):
        f = (t.get('fill') or '').upper() if t.get('fill') and t['fill'].startswith('#') else (t.get('fill') or '')
        if f in VIGOR: return (-1, VIGOR.index(f))
        c_ = LCOP.get(f, 'none'); return (SEV.index(c_), 0)
    return sorted(ts, key=k)[0] if ts else None

# ------------------------------------------------------------------------------------------------- medidas
@med('M0 carga do mapa padrão (Lagoa Grande, MapLibre do CDN)')
def m0():
    tela(1440, 900); ok, s = abre()
    return {'pronto': ok, 'segundos_ate_pronto': s, 'maplibre': J("!!window.maplibregl&&maplibregl.getVersion&&maplibregl.getVersion()"),
            'erro': J("window.__LGI&&window.__LGI.erro"), 'erros_js': J("(window.__errs||[]).slice(0,5)"),
            'canvas_aria': J("(()=>{const c=document.querySelector('.maplibregl-canvas'); return c?{label:c.getAttribute('aria-label'),role:c.getAttribute('role'),tabindex:c.getAttribute('tabindex')}:null;})()"),
            'container_aria': J("(()=>{const e=document.getElementById('mapa-real'); return e?{label:e.getAttribute('aria-label'),role:e.getAttribute('role')}:null;})()"),
            'marcador_exemplo': J("(()=>{const m=window.__LGI.markers['PV05']; const e=m&&m.getElement(); return e?{role:e.getAttribute('role'),label:e.getAttribute('aria-label'),tabindex:e.getAttribute('tabindex')}:null;})()")}

@med('M1 ordem de Tab na Lagoa Grande (1440)')
def m1():
    tela(1440, 900); abre(); J("document.activeElement&&document.activeElement.blur(); 1")
    seq = []
    for i in range(140):
        tecla('Tab', 'Tab', 9); f = J(FOCO); seq.append(f)
    no_mapa = [i + 1 for i, f in enumerate(seq) if f.get('mapa')]
    no_desenho = [i + 1 for i, f in enumerate(seq) if f.get('real')]
    return {'tabs': len(seq), 'primeiro_na_area_do_mapa': no_mapa[0] if no_mapa else None, 'focos_na_area_do_mapa': sorted({(seq[i-1].get('t'), seq[i-1].get('nome')) for i in no_mapa}),
            'primeiro_no_desenho': no_desenho[0] if no_desenho else None, 'algum_pivo_focado': any(f.get('real') and not f.get('canvas') for f in seq),
            'canvas_focado': any(f.get('canvas') for f in seq), 'sequencia_resumo': [(f.get('t'), f.get('role'), f.get('nome')) for f in seq[:40]]}

@med('M2 Santa Rita: Tab até os talhões e árvore de acessibilidade (1440)')
def m2():
    tela(1440, 900); abre('Santa Rita'); J("document.activeElement&&document.activeElement.blur(); 1")
    seq = []
    for i in range(80):
        tecla('Tab', 'Tab', 9); seq.append(J(FOCO))
    tal = [i + 1 for i, f in enumerate(seq) if f.get('talhao')]
    ax = c.call('Accessibility.getFullAXTree', {})
    nos = ax.get('nodes', [])
    def nome(n): return ((n.get('name') or {}).get('value') or '')
    def papel(n): return ((n.get('role') or {}).get('value') or '')
    btn_talhao = [nome(n) for n in nos if papel(n) == 'button' and ':' in nome(n) and nome(n).split(':')[0] in ('T1', 'T2', 'T3', 'T4', 'T7', 'C1', 'P1', 'P2') and not n.get('ignored')]
    img = [nome(n) for n in nos if papel(n) == 'image' and 'Santa Rita' in nome(n)]
    return {'tabs_ate_1o_talhao': tal[0] if tal else None, 'tabs_ate_ultimo_talhao': tal[-1] if tal else None, 'talhoes_focados': len(tal),
            'nome_acessivel_exemplo': [seq[i - 1].get('nome') for i in tal[:3]], 'ax_botoes_de_talhao_expostos': btn_talhao, 'ax_svg_como_imagem': img,
            'tamanho_foco_talhao': [(seq[i - 1].get('w'), seq[i - 1].get('h')) for i in tal[:2]]}

@med('M3 hover e foco: dica no talhão (1440)')
def m3():
    tela(1440, 900); out = {}
    abre('Santa Rita'); xy = J(f"({CENTRO_SR})('T4')"); mouse(xy[0], xy[1] - 30); time.sleep(0.9)
    out['SR_hover_dica_visivel'] = J("(()=>{const d=document.getElementById('g2-dica'); return !!d&&!d.hidden;})()")
    out['SR_hover_filtro_poligono'] = J(f"(()=>{{const e=[...document.querySelectorAll('svg [role=button]')].find(x=>(x.getAttribute('aria-label')||'').startsWith('T4:')); return getComputedStyle(e).filter;}})()")
    out['SR_hover_cursor'] = J("(()=>{const e=[...document.querySelectorAll('svg [role=button]')].find(x=>(x.getAttribute('aria-label')||'').startsWith('T4:')); return getComputedStyle(e).cursor;})()")
    J("(()=>{const e=[...document.querySelectorAll('svg [role=button]')].find(x=>(x.getAttribute('aria-label')||'').startsWith('T4:')); e.focus(); return 1;})()"); time.sleep(0.5)
    out['SR_foco_programatico_dica'] = J("(()=>{const d=document.getElementById('g2-dica'); return !!d&&!d.hidden;})()")
    # Satélite: o grupo de pixels fica por cima do polígono (pointer-events none): o elemento sob o ponteiro é o polígono, o que se vê é o pixel
    J(f"{TABS}.find(b=>b.innerText.trim()==='Satélite').click(); 1"); time.sleep(0.8)
    xy = J(f"({CENTRO_SR})('P2')"); mouse(xy[0], xy[1] + 40); time.sleep(0.9)
    out['SR_satelite_sob_ponteiro'] = J(f"(()=>{{const e=document.elementFromPoint({xy[0]},{xy[1]+40}); return e?e.tagName+(e.getAttribute('aria-label')?' '+e.getAttribute('aria-label'):''):null;}})()")
    out['SR_satelite_pixels_por_cima'] = J("(()=>{const g=document.querySelector('g[clip-path=\"url(#cp_P2)\"]'); return g?{opacidade:g.getAttribute('opacity'), depois_do_poligono:!!(g.previousElementSibling&&g.previousElementSibling.matches('[role=button]'))}:null;})()")
    out['SR_satelite_dica_no_pixel'] = J("(()=>{const d=document.getElementById('g2-dica'); return !!d&&!d.hidden;})()")
    abre(); xy = J(f"({CENTRO_LG})('PV05')"); mouse(xy[0], xy[1]); time.sleep(0.9)
    out['LG_hover_cursor_canvas'] = J("document.querySelector('.maplibregl-canvas').style.cursor")
    out['LG_hover_dica_visivel'] = J("(()=>{const d=document.getElementById('g2-dica'); return !!d&&!d.hidden;})()")
    out['LG_popup'] = J("!!document.querySelector('.maplibregl-popup')")
    return out

@med('M4 cliques até o detalhe do talhão mais crítico de cada camada (1440, mouse)')
def m4():
    tela(1440, 900); res = {}
    for faz in ('Santa Rita', 'Lagoa Grande'):
        abre(faz); nomes = J(f"{TABS}.map(b=>b.innerText.trim())") or []
        for i, nm in enumerate(nomes):
            J(f"{TABS}[{i}].click(); 1"); time.sleep(1.2 if faz == 'Lagoa Grande' else 0.6)
            if faz == 'Lagoa Grande' and nm in ('Satélite', 'Solo'): espera('!!window.__LGI.px', 30); time.sleep(1.0)
            ts = talhoes_sr() if faz == 'Santa Rita' else talhoes_lg(); p = pior(ts)
            if not p: res[f'{faz} · {nm}'] = None; continue
            xy = J(f"({CENTRO_SR if faz == 'Santa Rita' else CENTRO_LG})({json.dumps(p['id'])})"); mouse(xy[0], xy[1], True); time.sleep(0.8)
            pn = J(PAINEL)
            res[f'{faz} · {nm}'] = {'talhao': p['id'], 'rotulo': p['rot'], 'cliques_ate_detalhe': 2 if pn else None, 'painel': (pn or {}).get('titulo'),
                                    'primaria_verde': (pn or {}).get('verdes'), 'cliques_ate_decidir': (3 if pn and pn.get('verdes') else None)}
            J("(()=>{const b=document.querySelector('.mapa-linha aside button[aria-label=\"Fechar painel\"]'); if(b) b.click(); return 1;})()"); time.sleep(0.4)
    return res

@med('M5 alvos de toque e de clique (1440 fino; 390 toque)')
def m5():
    out = {}
    for w, h, toque in ((1440, 900, False), (390, 844, True)):
        tela(w, h, toque); abre('Santa Rita')
        xy = J(f"({CENTRO_SR})('T4')"); J(f"(()=>{{const e=[...document.querySelectorAll('svg [role=button]')].find(x=>(x.getAttribute('aria-label')||'').startsWith('T4:')); e.dispatchEvent(new MouseEvent('click',{{bubbles:true}})); return 1;}})()"); time.sleep(0.6)
        r = J("""(()=>{const q=(sel)=>[...document.querySelectorAll(sel)].filter(e=>e.offsetParent||e.getClientRects().length).map(e=>{const r=e.getBoundingClientRect(); return {n:(e.getAttribute('aria-label')||e.innerText||'').replace(/\\s+/g,' ').trim().slice(0,30), w:Math.round(r.width*10)/10, h:Math.round(r.height*10)/10};});
          return {coarse:matchMedia('(pointer: coarse)').matches, abas:q('nav[role=tablist] [role=tab]'), ferramentas:q('[role=toolbar][aria-label="Ferramentas do mapa"] button,[role=toolbar][aria-label="Ferramentas do mapa"] a'),
            zoom:q('[role=group][aria-label=Zoom] button'), fechar:q('.mapa-linha aside button[aria-label="Fechar painel"]'), segmentados:q('.mapa-flt [role=group] button'),
            atalho:q('.mapa-dir>a'), selects:q('.mapa-flt select'), acoes_painel:q('.mapa-linha aside a, .mapa-linha aside button')};})()""")
        lim = 44 if toque else 24
        resumo = {k: {'n': len(v), 'menor': min((min(x['w'], x['h']) for x in v), default=None), 'abaixo_do_limite': sum(1 for x in v if min(x['w'], x['h']) < lim)} for k, v in r.items() if isinstance(v, list)}
        out[f'{w}px'] = {'pointer_coarse': r.get('coarse'), 'limite_px': lim, 'resumo': resumo, 'ferramentas': r.get('ferramentas'), 'zoom': r.get('zoom'), 'fechar': r.get('fechar')}
    tela(1440, 900)
    return out

@med('M6 legenda sobre o mapa: talhões cobertos e cliques bloqueados')
def m6():
    out = {}
    for w, h in ((1440, 900), (390, 844)):
        tela(w, h, w < 500); abre('Santa Rita')
        out[f'SR {w}px'] = J("""(()=>{const lg=document.querySelector('.mapa-area>div[style*="bottom: 12px"]'), ar=document.querySelector('.mapa-area'); if(!lg) return null; const L=lg.getBoundingClientRect(), A=ar.getBoundingClientRect();
          const cob=[...document.querySelectorAll('svg [role=button]')].map(e=>{const r=e.getBoundingClientRect(); const ix=Math.max(0,Math.min(r.right,L.right)-Math.max(r.left,L.left)), iy=Math.max(0,Math.min(r.bottom,L.bottom)-Math.max(r.top,L.top)); return {t:(e.getAttribute('aria-label')||'').split(':')[0], pct:Math.round(100*ix*iy/(r.width*r.height))};}).filter(x=>x.pct>0);
          const el=document.elementFromPoint(L.left+L.width/2, L.top+L.height/2);
          return {legenda_h:Math.round(L.height), area_mapa_h:Math.round(A.height), pct_altura:Math.round(100*L.height/A.height), pointer_events:getComputedStyle(lg).pointerEvents, talhoes_sob_legenda:cob, clique_no_centro_da_legenda_cai_em:el?(el.closest('svg')?'mapa':'legenda'):null};})()""")
        abre()
        out[f'LG {w}px'] = J("""(()=>{const lg=document.querySelector('.mapa-area>div[style*="bottom: 12px"]'), ar=document.querySelector('.mapa-area'); if(!lg) return null; const L=lg.getBoundingClientRect(), A=ar.getBoundingClientRect();
          const m=window.__LGI.map, C=m.getContainer().getBoundingClientRect(); let n=0; Object.values(window.__LGI.markers).forEach(mk=>{const p=m.project(mk.getLngLat()); const y=C.top+p.y, x=C.left+p.x; if(y>=L.top&&y<=L.bottom&&x>=L.left&&x<=L.right) n++;});
          return {legenda_h:Math.round(L.height), area_mapa_h:Math.round(A.height), pct_altura:Math.round(100*L.height/A.height), pointer_events:getComputedStyle(lg).pointerEvents, centros_de_pivo_sob_legenda:n};})()""")
    tela(1440, 900)
    return out

@med('M7 rótulos do SVG da Santa Rita: tamanho efetivo e corte (D12)')
def m7():
    out = {}
    for w, h in ((1440, 900), (390, 844)):
        tela(w, h, w < 500); abre('Santa Rita')
        base = J("""(()=>{const s=document.querySelector('svg[aria-label="Mapa da fazenda Santa Rita"]'); const k=s.getBoundingClientRect().width/1000, kh=s.getBoundingClientRect().height/620; const e=Math.min(k,kh); return {escala:Math.round(e*1000)/1000, id_px:Math.round(40*e*10)/10, rotulo_px:Math.round(15*e*10)/10, sub_px:Math.round(13*e*10)/10};})()""")
        cortes = {}
        for camada, filtro in (('Integrado', None), ('Colheita e produtividade', 'Carência e destino'), ('Ordens de serviço', None), ('Irrigação', 'Balanço hídrico')):
            J(f"{TABS}.find(b=>b.innerText.trim()==={json.dumps(camada)}).click(); 1"); time.sleep(0.6)
            if filtro: J(f"(()=>{{const b=[...document.querySelectorAll('.mapa-flt [role=group] button')].find(b=>b.innerText.trim()==={json.dumps(filtro)}); if(b) b.click(); return 1;}})()"); time.sleep(0.6)
            cortes[camada + (' › ' + filtro if filtro else '')] = J("""[...document.querySelectorAll('svg foreignObject')].map(fo=>{const d=fo.firstElementChild; if(!d||!d.innerText.trim()) return null; const hFO=Number(fo.getAttribute('height')); return {t:d.innerText.trim().slice(0,70), cortado:d.scrollHeight>hFO+1||d.scrollWidth>Number(fo.getAttribute('width'))+1, h_texto:d.scrollHeight, h_caixa:hFO};}).filter(x=>x&&x.cortado)""")
        out[f'{w}px'] = {'escala_e_tamanhos': base, 'rotulos_cortados': cortes}
    tela(1440, 900)
    return out

@med('M8 rótulos da Lagoa Grande: sobreposição (D28)')
def m8():
    out = {}
    for w, h in ((1440, 900), (390, 844)):
        tela(w, h, w < 500); abre()
        out[f'{w}px'] = J("""(()=>{const rs=Object.values(window.__LGI.markers).map(m=>{const e=m.getElement(); const r=e.getBoundingClientRect(); return {t:e.innerText.replace(/\\s+/g,' ').trim(), r};});
          let n=0, ex=[]; for(let i=0;i<rs.length;i++) for(let j=i+1;j<rs.length;j++){ const a=rs[i].r, b=rs[j].r; if(a.left<b.right&&b.left<a.right&&a.top<b.bottom&&b.top<a.bottom){ n++; if(ex.length<4) ex.push(rs[i].t.slice(0,25)+' × '+rs[j].t.slice(0,25)); } }
          const m=window.__LGI.map; return {zoom:Math.round(m.getZoom()*100)/100, rotulos:rs.length, pares_sobrepostos:n, exemplos:ex, fonte_px:getComputedStyle(document.querySelector('.lg-rot b')).fontSize+' / '+getComputedStyle(document.querySelector('.lg-rot span')).fontSize};})()""")
    tela(1440, 900)
    return out

@med('M9 arrasto de um dedo sobre o mapa no celular (D29)')
def m9():
    tela(390, 844, True); abre(); time.sleep(0.5)
    a = J("""(()=>{const se=document.scrollingElement, mn=document.querySelector('main'); const m=window.__LGI.map; const r=m.getContainer().getBoundingClientRect(); const c=m.getCenter(); let an=m.getContainer().parentElement; while(an&&!(an.scrollHeight>an.clientHeight+2&&/auto|scroll/.test(getComputedStyle(an).overflowY))) an=an.parentElement; window.__rol=an;
      return {rolador:an?(an.tagName+(an.className?'.'+String(an.className).split(' ')[0]:'')):'documento', rolador_top:an?an.scrollTop:null, scroll:se.scrollTop, main:mn?mn.scrollTop:null, rola_pagina:se.scrollHeight>se.clientHeight+2, rola_main:mn?mn.scrollHeight>mn.clientHeight+2:null, centro:[c.lng,c.lat], x:r.left+r.width/2, y:r.top+r.height/2, h:r.height, touch_action:getComputedStyle(m.getCanvas()).touchAction};})()""")
    x, y = a['x'], a['y']
    c.call('Input.synthesizeScrollGesture', {'x': x, 'y': y + 60, 'yDistance': -160, 'gestureSourceType': 'touch', 'speed': 600}, timeout=30); time.sleep(0.8)
    b = J("""(()=>{const se=document.scrollingElement, mn=document.querySelector('main'); const c=window.__LGI.map.getCenter(); return {rolador_top:window.__rol?window.__rol.scrollTop:null, scroll:se.scrollTop, main:mn?mn.scrollTop:null, centro:[c.lng,c.lat]};})()""")
    tela(1440, 900)
    return {'antes': a, 'depois': b, 'mapa_moveu': abs(a['centro'][1] - b['centro'][1]) > 1e-6, 'pagina_rolou': (a['scroll'] != b['scroll']) or (a['main'] != b['main']) or (a.get('rolador_top') != b.get('rolador_top'))}

@med('M10 seleção: Esc, clique no fundo, endereço e foco (D16, D17, D20)')
def m10():
    out = {}
    tela(1440, 900); abre('Santa Rita'); h0 = J('location.hash')
    xy = J(f"({CENTRO_SR})('T4')"); mouse(xy[0], xy[1], True); time.sleep(0.6)
    out['painel_abriu'] = bool(J(PAINEL)); out['foco_apos_clique'] = J(FOCO); out['hash_antes_depois'] = [h0, J('location.hash')]
    tecla('Escape', 'Escape', 27); time.sleep(0.5); out['painel_apos_Esc'] = bool(J(PAINEL))
    fundo = J("""(()=>{const s=document.querySelector('svg[aria-label="Mapa da fazenda Santa Rita"]'); const r=s.getBoundingClientRect(); for(let y=r.top+5;y<r.bottom;y+=7) for(let x=r.left+5;x<r.right;x+=7){ const e=document.elementFromPoint(x,y); if(e&&e.tagName==='rect'&&e.getAttribute('fill')==='url(#grade)') return [x,y]; } return null;})()""")
    if fundo: mouse(fundo[0], fundo[1], True); time.sleep(0.5)
    out['painel_apos_clique_no_fundo'] = bool(J(PAINEL)); out['ponto_de_fundo'] = fundo
    tela(390, 844, True); abre('Santa Rita'); xy = J(f"({CENTRO_SR})('T4')")
    c.call('Input.synthesizeTapGesture', {'x': xy[0], 'y': xy[1], 'gestureSourceType': 'touch'}, timeout=30); time.sleep(0.8)
    p = J(PAINEL); out['390_painel'] = p; out['390_painel_visivel_sem_rolar'] = bool(p and p['top'] < p['alturaJanela']); out['390_foco_apos_toque'] = J(FOCO)
    tela(1440, 900)
    return out

@med('M11 #talhao= com o contexto salvo em outra fazenda (D18)')
def m11():
    tela(1440, 900); abre('Santa Rita', hash_='#talhao=PV05'); time.sleep(7)
    return {'fazenda_no_topo': J("(()=>{const s=[...document.querySelectorAll('select')].find(s=>[...s.options].some(o=>o.value==='Santa Rita')); return s?s.value:null;})()"),
            'painel': J(PAINEL), 'mapa_real_presente': J("!!document.getElementById('mapa-real')")}

@med('M12 Medir: resultado e anúncio (D19)')
def m12():
    tela(1440, 900); abre('Santa Rita')
    J("(()=>{const b=[...document.querySelectorAll('[role=toolbar] button')].find(b=>b.innerText.trim()==='Medir'); b.click(); return 1;})()"); time.sleep(0.6)
    xy = J(f"({CENTRO_SR})('T1')"); mouse(xy[0], xy[1], True); time.sleep(0.4)
    t1 = J("(document.querySelector('.g2toast')||{}).innerText||''"); viva = J("(document.getElementById('g2-vivo')||{}).textContent||''")
    time.sleep(5.0); t2 = J("(()=>{const e=document.querySelector('.g2toast'); return e&&getComputedStyle(e).display!=='none'?e.innerText:'';})()")
    return {'aviso': t1, 'regiao_viva': viva, 'aviso_apos_5s': t2, 'painel': bool(J(PAINEL))}

@med('M13 abas das camadas: setas e aria-controls (D21)')
def m13():
    tela(1440, 900); abre('Santa Rita')
    J(f"{TABS}[0].focus(); 1"); a = J(FOCO); tecla('ArrowRight', 'ArrowRight', 39); time.sleep(0.3); b = J(FOCO)
    return {'antes': a.get('nome'), 'depois_da_seta': b.get('nome'), 'seta_move_foco': a.get('nome') != b.get('nome'),
            'aria_controls': J(f"{TABS}.filter(b=>b.hasAttribute('aria-controls')).length"), 'tabpanel': J("document.querySelectorAll('[role=tabpanel]').length"),
            'orientacao': J("(document.querySelector('nav[role=tablist]')||{}).getAttribute&&document.querySelector('nav[role=tablist]').getAttribute('aria-orientation')")}

@med('M14 tela cheia e fazenda "Todas" (D5, D6)')
def m14():
    tela(1440, 900); out = {}
    abre(); out['LG_botao_tela_cheia'] = J("[...document.querySelectorAll('[role=toolbar] button')].some(b=>/Tela cheia/.test(b.innerText))")
    abre('Santa Rita'); out['SR_botao_tela_cheia'] = J("[...document.querySelectorAll('[role=toolbar] button')].some(b=>/Tela cheia/.test(b.innerText))")
    J("(()=>{const b=[...document.querySelectorAll('[role=toolbar] button')].find(b=>/Tela cheia/.test(b.innerText)); b.click(); return 1;})()"); time.sleep(0.6)
    out['tela_cheia_dialog'] = J("(()=>{const d=document.querySelector('[role=dialog][aria-label=\"Mapa em tela cheia\"]'); return d?{aria_modal:d.getAttribute('aria-modal'), foco_dentro:d.contains(document.activeElement)}:null;})()")
    tecla('Escape', 'Escape', 27); time.sleep(0.4); out['tela_cheia_apos_Esc'] = J("!!document.querySelector('[role=dialog][aria-label=\"Mapa em tela cheia\"]')")
    abre('Todas'); out['Todas'] = {'svg_santa_rita': J("!!document.querySelector('svg[aria-label=\"Mapa da fazenda Santa Rita\"]')"), 'mapa_real': J("!!document.getElementById('mapa-real')"),
                                   'aviso': J("[...document.querySelectorAll('[role=note]')].map(x=>x.innerText).join(' | ')")}
    return out

@med('M15 destinos e atalhos por camada (D7, D8, D24, D25)')
def m15():
    tela(1440, 900); abre('Santa Rita'); out = {}
    nomes = J(f"{TABS}.map(b=>b.innerText.trim())") or []
    for i, nm in enumerate(nomes):
        J(f"{TABS}[{i}].click(); 1"); time.sleep(0.5)
        out[nm] = J("(()=>{const a=document.querySelector('.mapa-dir>a'); return a?{t:a.innerText.trim(), href:a.getAttribute('href')}:null;})()")
    J(f"{TABS}.find(b=>b.innerText.trim()==='Ordens de serviço').click(); 1"); time.sleep(0.4)
    xy = J(f"({CENTRO_SR})('T4')"); mouse(xy[0], xy[1], True); time.sleep(0.6)
    out['painel O.S. · Nova O.S. neste talhão'] = J("(()=>{const a=[...document.querySelectorAll('.mapa-linha aside a')].find(a=>/Nova O.S./.test(a.innerText)); return a?a.getAttribute('href'):null;})()")
    J(f"{TABS}.find(b=>b.innerText.trim()==='Satélite').click(); 1"); time.sleep(0.5)
    out['painel Satélite · link de histórico'] = J("(()=>{const a=[...document.querySelectorAll('.mapa-linha aside a')].find(a=>/histórico/i.test(a.innerText)); return a?{t:a.innerText.trim(), href:a.getAttribute('href')}:null;})()")
    J(f"{TABS}.find(b=>b.innerText.trim()==='Colheita e produtividade').click(); 1"); time.sleep(0.5)
    xy = J(f"({CENTRO_SR})('T7')"); mouse(xy[0], xy[1], True); time.sleep(0.6)
    out['painel Colheita · ícone nos botões'] = J("[...document.querySelectorAll('.mapa-linha aside a, .mapa-linha aside button')].filter(b=>b.offsetParent&&b.innerText.trim()).map(b=>({t:b.innerText.trim().slice(0,40), svg:!!b.querySelector('svg')}))")
    return out

@med('M16 Lagoa Grande: opacidade do preenchimento × legenda e nuvem (D13)')
def m16():
    tela(1440, 900); abre()
    ts = talhoes_lg(); ops = sorted({t['opac'] for t in ts if t.get('opac') is not None})
    return {'opacidades_no_mapa': ops, 'amostra_legenda_opacidade': J("(()=>{const d=document.querySelector('.mapa-area>div[style*=\"bottom: 12px\"] span span'); return d?getComputedStyle(d).opacity:null;})()"),
            'hachura_no_mapa_LG': J("(()=>{const m=window.__LGI.map; return !!m.getPaintProperty('pv-fill','fill-pattern');})()")}

@med('M17 Satélite: contraste padrão, legenda e classe do pixel no painel (D9)')
def m17():
    tela(1440, 900); abre('Santa Rita'); out = {}
    J(f"{TABS}.find(b=>b.innerText.trim()==='Satélite').click(); 1"); time.sleep(0.6)
    out['contraste_padrao'] = J("(()=>{const b=[...document.querySelectorAll('.mapa-flt [role=group] button[aria-pressed=true]')].map(b=>b.innerText.trim()); return b;})()")
    out['legenda_sem_talhao'] = J("[...document.querySelectorAll('.mapa-area>div[style*=\"bottom: 12px\"]>span')].map(s=>s.innerText.trim()).filter(Boolean)")
    # um pixel vermelho ("Falha" no contraste Talhão) no P1: clicar nele e ler a classe do painel
    alvo = J("""(()=>{const g=document.querySelector('g[clip-path="url(#cp_P1)"]'); const r=[...g.querySelectorAll('rect')].find(x=>(x.getAttribute('fill')||'').toUpperCase()==='#E4002B'); if(!r) return null; const b=r.getBoundingClientRect(); return [b.left+b.width/2,b.top+b.height/2];})()""")
    out['pixel_vermelho_P1'] = alvo
    if alvo:
        mouse(alvo[0], alvo[1], True); time.sleep(0.7)
        out['painel_pixel'] = J("(()=>{const it=[...document.querySelectorAll('.mapa-linha aside div')].find(d=>/^Pixel selecionado/.test(d.innerText.trim())&&d.children.length>1); return it?it.innerText.replace(/\\s+/g,' ').trim().slice(0,160):null;})()")
        out['chip_do_talhao'] = J("(()=>{const a=document.querySelector('.mapa-linha aside'); const s=a&&a.querySelector('h2').parentElement.querySelector('span span, div>span'); return s?s.innerText:null;})()")
        out['legenda_com_talhao'] = J("[...document.querySelectorAll('.mapa-area>div[style*=\"bottom: 12px\"]>span')].map(s=>s.innerText.trim()).filter(Boolean)")
        out['pixels_vermelhos_por_talhao'] = J("""Object.fromEntries(['P1','P2','T7','C1'].map(t=>{const g=document.querySelector('g[clip-path="url(#cp_'+t+')"]'); const rs=g?[...g.querySelectorAll('rect')]:[]; const n=rs.filter(x=>(x.getAttribute('fill')||'').toUpperCase()==='#E4002B').length; return [t, rs.length?Math.round(100*n/rs.length):null];}))""")
    return out

@med('M18 mancha do T7 sobre o rótulo (D11)')
def m18():
    tela(1440, 900); abre('Santa Rita')
    J(f"{TABS}.find(b=>b.innerText.trim()==='Satélite').click(); 1"); time.sleep(0.6)
    return J("""(()=>{const fos=[...document.querySelectorAll('svg foreignObject')]; const chip=fos.find(f=>/mancha/.test(f.innerText)); const t7=fos.find(f=>f.getAttribute('x')==='606'&&f.getAttribute('height')==='46');
      if(!chip||!t7) return {chip:!!chip,t7:!!t7}; const a=chip.firstElementChild.getBoundingClientRect(), b=t7.firstElementChild.getBoundingClientRect(); const ix=Math.max(0,Math.min(a.right,b.right)-Math.max(a.left,b.left)), iy=Math.max(0,Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top));
      return {chip:chip.innerText.trim(), rotulo_T7:t7.innerText.trim(), sobreposicao_px2:Math.round(ix*iy), pct_do_chip:Math.round(100*ix*iy/(a.width*a.height))};})()""")


# ------------------------------------------------------------------------------- complemento (2ª passada: métodos alternativos)
@med('M3b hover em ponteiro fino: media query e realce do polígono')
def m3b():
    tela(1440, 900); abre('Santa Rita')
    xy = J("""(()=>{const e=[...document.querySelectorAll('svg [role=button]')].find(x=>(x.getAttribute('aria-label')||'').startsWith('T2:')); const r=e.getBoundingClientRect(); for(let y=r.top+8;y<r.bottom;y+=6) for(let x=r.left+8;x<r.right;x+=6){ if(document.elementFromPoint(x,y)===e) return [x,y]; } return null;})()""")
    mouse(xy[0], xy[1]); time.sleep(0.6)
    return {'hover_hover': J("matchMedia('(hover: hover)').matches"), 'ponto': xy, 'filtro_no_hover': J("(()=>{const e=[...document.querySelectorAll('svg [role=button]')].find(x=>(x.getAttribute('aria-label')||'').startsWith('T2:')); return getComputedStyle(e).filter+' · :hover='+e.matches(':hover');})()"),
            'dica_visivel': J("(()=>{const d=document.getElementById('g2-dica'); return !!d&&!d.hidden;})()")}

@med('M9b arrasto de um dedo com eventos de toque, com controle fora do mapa (D29)')
def m9b():
    tela(390, 844, True); abre(); time.sleep(0.5)
    est = lambda: J("""(()=>{const mn=document.querySelector('main'); const c=window.__LGI.map.getCenter(); const r=window.__LGI.map.getContainer().getBoundingClientRect(); return {main:mn.scrollTop, centro:[c.lng,c.lat], topo_mapa:Math.round(r.top), base_mapa:Math.round(r.bottom), janela:innerHeight};})()""")
    def arrasta(x, y, dy):
        c.call('Input.dispatchTouchEvent', {'type': 'touchStart', 'touchPoints': [{'x': x, 'y': y}]})
        for k in range(1, 13):
            c.call('Input.dispatchTouchEvent', {'type': 'touchMove', 'touchPoints': [{'x': x, 'y': y + dy * k / 12}]}); time.sleep(0.02)
        c.call('Input.dispatchTouchEvent', {'type': 'touchEnd', 'touchPoints': []}); time.sleep(0.8)
    a = est(); y0 = max(a['topo_mapa'] + 40, 120); y0 = min(y0, a['janela'] - 60)
    arrasta(195, y0 + 120, -150); b = est()
    # controle: o mesmo gesto sobre a faixa da camada (fora do mapa) deve rolar a página, se ela rola
    fx = J("(()=>{const f=document.querySelector('.mapa-faixa'); const r=f.getBoundingClientRect(); return [r.left+r.width/2, r.top+r.height/2];})()")
    J("document.querySelector('main').scrollTop=0; 1"); time.sleep(0.3)
    arrasta(fx[0], max(fx[1], 200), -150); ctl = est()
    tela(1440, 900)
    return {'antes': a, 'depois_no_mapa': b, 'mapa_moveu': abs(a['centro'][1] - b['centro'][1]) > 1e-7, 'pagina_rolou_no_mapa': a['main'] != b['main'], 'controle_fora_do_mapa_rolou': ctl['main'] != 0, 'controle': ctl}

@med('M10b toque num talhão a 390 px: painel e foco (D20)')
def m10b():
    tela(390, 844, True); abre('Santa Rita')
    xy = J("""(()=>{const e=[...document.querySelectorAll('svg [role=button]')].find(x=>(x.getAttribute('aria-label')||'').startsWith('T1:')); e.scrollIntoView({block:'center'}); const r=e.getBoundingClientRect(); for(let y=Math.max(r.top,0)+6;y<Math.min(r.bottom,innerHeight);y+=5) for(let x=r.left+6;x<r.right;x+=5){ if(document.elementFromPoint(x,y)===e) return [x,y]; } return null;})()""")
    time.sleep(0.4)
    c.call('Input.synthesizeTapGesture', {'x': xy[0], 'y': xy[1], 'gestureSourceType': 'touch'}, timeout=30); time.sleep(0.9)
    p = J(PAINEL)
    return {'ponto': xy, 'painel': p, 'painel_visivel_sem_rolar': bool(p and p['top'] < p['alturaJanela'] - 40), 'foco': J(FOCO),
            'main': J("(()=>{const m=document.querySelector('main'); return {scrollTop:m.scrollTop, scrollHeight:m.scrollHeight, clientHeight:m.clientHeight};})()")}

@med('M18b mancha do T7 sobre o rótulo, por textContent (D11)')
def m18b():
    tela(1440, 900); abre('Santa Rita')
    J(f"{TABS}.find(b=>b.innerText.trim()==='Satélite').click(); 1"); time.sleep(0.6)
    return J("""(()=>{const fos=[...document.querySelectorAll('svg foreignObject')]; const chip=fos.find(f=>/mancha/.test(f.textContent)); const t7=fos.find(f=>f.getAttribute('x')==='606'&&f.getAttribute('height')==='46');
      if(!chip||!t7) return {chip:!!chip,t7:!!t7}; const a=chip.firstElementChild.getBoundingClientRect(), b=t7.firstElementChild.getBoundingClientRect(); const ix=Math.max(0,Math.min(a.right,b.right)-Math.max(a.left,b.left)), iy=Math.max(0,Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top));
      return {chip:chip.textContent.trim(), opacidade_chip:chip.getAttribute('opacity'), rotulo_T7:t7.textContent.trim(), caixa_chip:[Math.round(a.left),Math.round(a.top),Math.round(a.width),Math.round(a.height)], caixa_rotulo:[Math.round(b.left),Math.round(b.top),Math.round(b.width),Math.round(b.height)], sobreposicao_px2:Math.round(ix*iy), pct_do_chip:Math.round(100*ix*iy/(a.width*a.height))};})()""")


@med('M10c toque a 390 px: eventos recebidos pelo talhão e por uma aba (diagnóstico do M10b)')
def m10c():
    tela(390, 844, True); abre('Santa Rita')
    J("""(()=>{window.__ev=[]; const e=[...document.querySelectorAll('svg [role=button]')].find(x=>(x.getAttribute('aria-label')||'').startsWith('T1:')); ['pointerdown','pointerup','touchstart','touchend','click'].forEach(t=>e.addEventListener(t,ev=>window.__ev.push('T1:'+t),true)); const b=[...document.querySelectorAll('nav[role=tablist] [role=tab]')][1]; ['click'].forEach(t=>b.addEventListener(t,()=>window.__ev.push('aba:'+t),true)); return 1;})()""")
    xy = J("""(()=>{const e=[...document.querySelectorAll('svg [role=button]')].find(x=>(x.getAttribute('aria-label')||'').startsWith('T1:')); e.scrollIntoView({block:'center'}); const r=e.getBoundingClientRect(); for(let y=Math.max(r.top,0)+6;y<Math.min(r.bottom,innerHeight);y+=5) for(let x=r.left+6;x<r.right;x+=5){ if(document.elementFromPoint(x,y)===e) return [x,y]; } return null;})()""")
    time.sleep(0.4); c.call('Input.synthesizeTapGesture', {'x': xy[0], 'y': xy[1], 'gestureSourceType': 'touch'}, timeout=30); time.sleep(0.9)
    ev1 = J('window.__ev.slice()'); p1 = J(PAINEL)
    # o mesmo talhão com um clique de ponteiro no mesmo ponto (prova de que o painel abre no estreito)
    mouse(xy[0], xy[1], True); time.sleep(0.9); p2 = J(PAINEL)
    ab = J("(()=>{const b=[...document.querySelectorAll('nav[role=tablist] [role=tab]')][1]; b.scrollIntoView({block:'center'}); const r=b.getBoundingClientRect(); return [r.left+r.width/2, r.top+r.height/2];})()")
    c.call('Input.synthesizeTapGesture', {'x': ab[0], 'y': ab[1], 'gestureSourceType': 'touch'}, timeout=30); time.sleep(0.6)
    return {'eventos_no_toque': ev1, 'painel_apos_toque': p1, 'painel_apos_clique': p2, 'eventos_total': J('window.__ev.slice()'),
            'main': J("(()=>{const m=document.querySelector('main'); return {scrollTop:m.scrollTop, clientHeight:m.clientHeight};})()")}


@med('M18c recorte da tela no T7 (Satélite 21/09, 1440 px) para conferir a mancha e o rótulo')
def m18c():
    import base64
    tela(1440, 900); abre('Santa Rita')
    J(f"{TABS}.find(b=>b.innerText.trim()==='Satélite').click(); 1"); time.sleep(0.8)
    r = J("(()=>{const e=[...document.querySelectorAll('svg [role=button]')].find(x=>(x.getAttribute('aria-label')||'').startsWith('T7:')); const b=e.getBoundingClientRect(); return [b.left,b.top,b.width,b.height];})()")
    d = c.call('Page.captureScreenshot', {'format': 'png', 'clip': {'x': r[0] - 4, 'y': r[1] - 4, 'width': r[2] + 8, 'height': r[3] + 8, 'scale': 1}})
    arq = os.path.join(AQUI, 'm18c_T7_satelite_1440.png'); open(arq, 'wb').write(base64.b64decode(d['data']))
    return {'arquivo': os.path.basename(arq), 'caixa': [round(x) for x in r], 'chip_altura_fo_un': 22,
            'chip_div_altura_px': J("(()=>{const f=[...document.querySelectorAll('svg foreignObject')].find(f=>/mancha/.test(f.textContent)); return Math.round(f.firstElementChild.getBoundingClientRect().height);})()"),
            'fo_altura_px': J("(()=>{const f=[...document.querySelectorAll('svg foreignObject')].find(f=>/mancha/.test(f.textContent)); return Math.round(f.getBoundingClientRect().height);})()"),
            'overflow_fo': J("(()=>{const f=[...document.querySelectorAll('svg foreignObject')].find(f=>/mancha/.test(f.textContent)); return getComputedStyle(f).overflow;})()")}


@med('M7b rótulos cortados em todas as camadas da Santa Rita (1440 e 390)')
def m7b():
    out = {}
    for w, h in ((1440, 900), (390, 844)):
        tela(w, h, w < 500); abre('Santa Rita'); nomes = J(f"{TABS}.map(b=>b.innerText.trim())") or []; res = {}
        for i, nm in enumerate(nomes):
            J(f"{TABS}[{i}].click(); 1"); time.sleep(0.6)
            vis = [None] + (J("[...document.querySelectorAll('.mapa-flt [role=group] button')].map(b=>b.innerText.trim())") or [])
            for v in vis:
                if v: J(f"(()=>{{const b=[...document.querySelectorAll('.mapa-flt [role=group] button')].find(b=>b.innerText.trim()==={json.dumps(v)}); if(b) b.click(); return 1;}})()"); time.sleep(0.5)
                cort = J("""[...document.querySelectorAll('svg foreignObject')].filter(fo=>fo.getAttribute('opacity')!=='0').map(fo=>{const d=fo.firstElementChild; if(!d||!d.textContent.trim()) return null; return {t:d.textContent.trim().slice(0,60), cortado:d.scrollHeight>Number(fo.getAttribute('height'))+1};}).filter(x=>x&&x.cortado).map(x=>x.t)""")
                if cort: res[nm + (' › ' + v if v else '')] = cort
        out[f'{w}px'] = res
    tela(1440, 900)
    return out


@med('M19 tempo do clique ao painel e da troca de camada (1440; SwiftShader, indicativo)')
def m19():
    out = {}
    ARMA = """(()=>{window.__t0=null; window.__t1=null; document.addEventListener('pointerdown',()=>{window.__t0=performance.now();},{capture:true,once:true});
      const ob=new MutationObserver(()=>{ if(window.__t0!==null&&window.__t1===null&&document.querySelector('.mapa-linha aside[aria-label]')){ window.__t1=performance.now(); ob.disconnect(); } }); ob.observe(document.body,{childList:true,subtree:true}); return 1;})()"""
    for faz, tid, fn in (('Santa Rita', 'T4', CENTRO_SR), ('Lagoa Grande', 'PV05', CENTRO_LG)):
        ts = []
        for k in range(5):
            if k == 0: abre(faz)
            else: J(FECHA)
            time.sleep(0.6)
            J(ARMA); xy = J(f"({fn})({json.dumps(tid)})"); mouse(xy[0], xy[1], True); time.sleep(1.0)
            d = J("window.__t1!==null&&window.__t0!==null?Math.round(window.__t1-window.__t0):null"); ts.append(d if d is not None else {'t0': J('window.__t0'), 't1': J('window.__t1'), 'painel': bool(J(PAINEL))})
        out[f'{faz} clique→painel ms'] = ts
        tr = []
        for k, nm in enumerate(['Satélite', 'Ordens de serviço', 'Pragas e doenças', 'Integrado']):
            t = J(f"(()=>{{const b={TABS}.find(b=>b.innerText.trim()==={json.dumps(nm)}); const t0=performance.now(); b.click(); return new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(()=>r(Math.round(performance.now()-t0)))));}})()"); tr.append([nm, t]); time.sleep(0.8)
        out[f'{faz} troca de camada até 2 quadros ms'] = tr
    return out


@med('M19b Lagoa Grande: clique no pivô logo após abrir × após trocar de camada (diagnóstico do M19)')
def m19b():
    tela(1440, 900); abre(); out = {}
    xy = J(f"({CENTRO_LG})('PV05')"); out['ponto'] = xy; out['elemento_no_ponto'] = J(f"(()=>{{const e=document.elementFromPoint({xy[0]},{xy[1]}); return e?e.tagName+'.'+String(e.className).slice(0,40):null;}})()")
    out['features_no_ponto'] = J(f"(()=>{{const m=window.__LGI.map, r=m.getContainer().getBoundingClientRect(); return m.queryRenderedFeatures([{xy[0]}-r.left,{xy[1]}-r.top],{{layers:['pv-fill']}}).map(f=>f.properties.id);}})()")
    mouse(xy[0], xy[1], True); time.sleep(1.0); out['painel_1o_clique'] = bool(J(PAINEL))
    mouse(xy[0], xy[1], True); time.sleep(1.0); out['painel_2o_clique'] = bool(J(PAINEL))
    J(f"{TABS}[1].click(); 1"); time.sleep(1.5); J(f"{TABS}[0].click(); 1"); time.sleep(1.2)
    xy = J(f"({CENTRO_LG})('PV05')"); mouse(xy[0], xy[1], True); time.sleep(1.0); out['painel_apos_trocar_camada'] = bool(J(PAINEL))
    return out


@med('M20 o mapa muda de lugar quando o painel abre? (salto de layout, 1440)')
def m20():
    tela(1440, 900); out = {}
    for faz, tid, fn in (('Santa Rita', 'T4', CENTRO_SR), ('Lagoa Grande', 'PV05', CENTRO_LG)):
        abre(faz); a = J(f"({fn})({json.dumps(tid)})"); larg0 = J("Math.round(document.querySelector('.mapa-area').getBoundingClientRect().width)")
        mouse(a[0], a[1], True); time.sleep(1.2); b = J(f"({fn})({json.dumps(tid)})")
        larg1 = J("Math.round(document.querySelector('.mapa-area').getBoundingClientRect().width)")
        sob = J(f"(()=>{{const e=document.elementFromPoint({a[0]},{a[1]}); if(!e) return null; if(e.closest('svg')) return (e.getAttribute('aria-label')||'').split(':')[0]||e.tagName; const m=window.__LGI&&window.__LGI.map; if(m&&e.classList.contains('maplibregl-canvas')){{ const r=m.getContainer().getBoundingClientRect(); const f=m.queryRenderedFeatures([{a[0]}-r.left,{a[1]}-r.top],{{layers:['pv-fill']}}); return f.length?f[0].properties.id:'fundo'; }} return e.tagName; }})()")
        out[faz] = {'talhao': tid, 'antes': [round(x) for x in a], 'depois': [round(x) for x in b], 'deslocamento_px': round(((a[0]-b[0])**2 + (a[1]-b[1])**2) ** 0.5), 'largura_do_mapa': [larg0, larg1], 'sob_o_ponteiro_depois': sob}
    return out

TODAS = dict(M20=m20, M19b=m19b, M19=m19, M7b=m7b, M18c=m18c, M10c=m10c, M0=m0, M1=m1, M2=m2, M3=m3, M4=m4, M5=m5, M6=m6, M7=m7, M8=m8, M9=m9, M10=m10, M11=m11, M12=m12, M13=m13, M14=m14, M15=m15, M16=m16, M17=m17, M18=m18, M3b=m3b, M9b=m9b, M10b=m10b, M18b=m18b)
ESC = [x for x in os.environ.get('MEDIDAS', ','.join(k for k in TODAS if not k.endswith('b'))).split(',') if x]   # MEDIDAS=M9b,M10b roda só essas
for k in ESC:
    if k in TODAS: TODAS[k]()
try: c.close()
finally: srv.terminate()
json.dump(R, open(SAIDA, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('FIM', len(R['medidas']), 'medidas,', len(R['erros']), 'erros ->', SAIDA)
