# -*- coding: utf-8 -*-
"""VISOES-1 (pedido do proprietário, 10/10/2026) · seletor de visões por ícone na O.S., no navegador (Chrome headless por CDP).
Modos (DESENHO.md, F1):
 comp     · 1440 × 900, Chrome com hover real: C1 barra e rótulos; C2 um ativo tonal; C3 teclado (Tab uma vez, setas sem ativar, Enter/Espaço,
            Home/End, foco fica); C4 dica no foco e no hover (g2dica da DS); C5 uma primária, 0 duplicata e nenhum arrastar em cada visão;
            C6 controle negativo da verificação.
 celular  · 390 × 844, escala 2, toque: M1 alvos ≥ 44 px (com e sem toque); M2 3 + "mais" (menu com nome, Esc devolve o foco, ativa no
            "mais" marcada); M3 nada cortado, primária alcançável, 0 duplicata; M4 toque longo mostra a dica sem trocar a visão.
 e2e      · em 1440 × 900 e 390 × 844: E1 filtro → Agrupada (clique e teclado); E2 painel → Esc → foco na linha; E3 volta do detalhe
            (link "Voltar", trilha, history.back(), nova aba, deep-link); E3b vazio por regra (Canceladas no Kanban) e "Ver em lista";
            E3c erro da visão (Kanban e Carga) e cenário ilegível; E4 precedência (URL › preferência › Lista; Lista explícita e F5; perfil);
            E5 trocar de visão não grava no cenário; E6 entrada por endereço (hash e outros parâmetros intactos).
 e7       · cliques medidos (window.__cl) em "filtrar → agrupar → abrir → voltar" e "voltar à O.S. em outra entrada", na tela que houver
            (seletor novo ou o botão "Agrupar por talhão" anterior): rode com VISOES_RENDER=<_render anterior> para o "antes".
Uso: python3 visoes_test.py comp|celular|e2e|e7 · VISOES_RENDER=<dir> serve outro _render · VISOES_SAIDA=<dir> grava as capturas."""
import os, sys, time, json, re, subprocess, tempfile, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, servir, MEDE, resumo, troca_visao
from cdp import WS, CH
from journeys import free
R = os.environ.get('VISOES_RENDER') or os.path.join(HERE, '_render')
MODO = sys.argv[1] if len(sys.argv) > 1 else 'comp'
OUT = os.environ.get('VISOES_SAIDA') or os.path.join(HERE, '_probe', 'visoes'); os.makedirs(OUT, exist_ok=True)
OK, FAIL = [], []
def chk(nome, cond, info=''):
    (OK if cond else FAIL).append(nome); print(('OK   ' if cond else 'FALHA ') + nome + ('' if cond else ' · ' + str(info)[:900]), flush=True)
def info(t, v): print('     (informativo) ' + t + ' ' + str(v)[:600], flush=True)

# ---------------- Chrome com hover real (como o ds_test): sem isso o headless responde (hover:none) e a dica de hover não abre ----------------
porta = free(); _dir = tempfile.mkdtemp(prefix='cdp_vis_')
_gl = (['--use-angle=swiftshader', '--enable-unsafe-swiftshader'] if os.environ.get('CDP_GL') == '1' else ['--disable-gpu'])
_proc = subprocess.Popen([CH, '--headless=new'] + _gl + ['--hide-scrollbars', f'--remote-debugging-port={porta}', f'--user-data-dir={_dir}', '--window-size=1440,900',
                          '--blink-settings=primaryHoverType=2,availableHoverTypes=2,primaryPointerType=4,availablePointerTypes=4', 'about:blank'],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
_ant = os.environ.get('CDP_PORT'); os.environ['CDP_PORT'] = str(porta)
try: c = Chrome()
finally:
    if _ant is None: os.environ.pop('CDP_PORT', None)
    else: os.environ['CDP_PORT'] = _ant
port, srv = servir(R); BASE = f'http://127.0.0.1:{port}/'
J = c.js
TOQUE = [False]
def janela(w, h, toque=False, escala=1):
    if toque: c.aparelho(w, h, escala, True); TOQUE[0] = True
    else:
        c.call('Emulation.setDeviceMetricsOverride', {'width': w, 'height': h, 'deviceScaleFactor': escala, 'mobile': False})
        if TOQUE[0]:
            c.call('Emulation.setTouchEmulationEnabled', {'enabled': False, 'maxTouchPoints': 1})
            c.call('Emulation.setEmulatedMedia', {'features': [{'name': 'hover', 'value': 'hover'}, {'name': 'pointer', 'value': 'fine'}]}); TOQUE[0] = False
        time.sleep(.2)
def pronto():
    try: c.call('Page.bringToFront')
    except Exception: pass
    for _ in range(60):
        if J("!!window.__g2glob&&!!document.querySelector('h1')"): break
        time.sleep(.1)
    time.sleep(.4)
def vai(f, espera=.6): c.goto(BASE + f, espera); pronto()
def limpa(): c.goto(BASE + 'Main.dc.html', .2); J("localStorage.clear(); sessionStorage.clear(); 1")
def abre(f, w=1440, h=900, toque=False, escala=1, zera=True):
    janela(w, h, toque, escala)
    if zera: limpa()
    vai(f)
def shot(nome): c.shot(os.path.join(OUT, nome + '.png'))
def errs(): return [e for e in (J("window.__errs||[]") or []) if "reading 'g2toast'" not in e]
ERROS = []
def guarda_erros(tag):
    e = errs()
    if e: ERROS.append((tag, e[:3]))

# ---------------- sondas ----------------
BAR = r"""(()=>{ const t=document.querySelector('[role=toolbar][data-visoes]'); if(!t) return null; const vis=e=>!!e&&e.getClientRects().length>0;
 const bs=[...t.querySelectorAll('[data-visao],[data-visao-mais]')].map(b=>{ const r=b.getBoundingClientRect(), cs=getComputedStyle(b), sv=b.querySelector('svg');
   return {k:b.getAttribute('data-visao')||'mais', lab:b.getAttribute('aria-label'), p:b.getAttribute('aria-pressed'), tab:b.tabIndex, txt:(b.innerText||'').trim(), tit:b.getAttribute('title'),
     svg:!!sv&&sv.getAttribute('aria-hidden')==='true', vis:vis(b), w:Math.round(r.width), h:Math.round(r.height), bg:cs.backgroundColor, sh:cs.boxShadow, bb:cs.borderBottomWidth,
     ativo:b.getAttribute('data-ativo'), x:b.getAttribute('aria-expanded')}; });
 const r=t.getBoundingClientRect(); return {role:t.getAttribute('role'), lab:t.getAttribute('aria-label'), vs:t.getAttribute('data-visoes'), bs, esq:Math.round(r.left), dir:Math.round(r.right)}; })()"""
CHK_C = r"""(()=>{ const t=document.querySelector('[role=toolbar][data-visoes]'); if(!t) return ['sem barra']; const f=[];
  const bs=[...t.querySelectorAll('[data-visao]')]; const pr=bs.filter(b=>b.getAttribute('aria-pressed')==='true');
  if(pr.length!==1) f.push('aria-pressed=true: '+pr.length);
  bs.forEach(b=>{ if(!/^Ver em /.test(b.getAttribute('aria-label')||'')) f.push('aria-label '+b.dataset.visao); if((b.innerText||'').trim()) f.push('texto visível '+b.dataset.visao);
    const s=b.querySelector('svg'); if(!s||s.getAttribute('aria-hidden')!=='true') f.push('svg '+b.dataset.visao); });
  pr.forEach(b=>{ const cs=getComputedStyle(b); if(cs.backgroundColor==='rgb(30, 122, 76)') f.push('verde cheio'); if(!(/inset/.test(cs.boxShadow)&&/-2px/.test(cs.boxShadow))&&parseFloat(cs.borderBottomWidth)<2) f.push('sem barra de 2 px'); });
  return f; })()"""
def bar(): return J(BAR)
def ativa(): return J("(()=>{const b=document.querySelector('[role=toolbar] [data-visao][aria-pressed=true]'); return b?b.getAttribute('data-visao'):'';})()") or ''
def foco(): return J("(()=>{const a=document.activeElement; if(!a) return ''; return a.getAttribute('data-visao')||(a.hasAttribute('data-visao-mais')?'mais':'')||a.getAttribute('data-visao-menu')&&('menu:'+a.getAttribute('data-visao-menu'))||(a.getAttribute('data-rid')?'linha:'+a.getAttribute('data-rid'):'')||a.tagName;})()") or ''
def estado(): return J("(()=>{const e=[...document.querySelectorAll('[data-visoes-estado]')].find(x=>x.getClientRects().length); return e?{t:e.innerText.replace(/\\s+/g,' ').trim(),tipo:e.getAttribute('data-tipo')}:null;})()")
def ids(): return J("[...document.querySelectorAll('[role=row].g2ed')].filter(r=>r.getClientRects().length).map(r=>r.getAttribute('data-rid'))") or []
def grupos(): return J("[...document.querySelectorAll('[data-g2g=g_os] [role=row][data-rid^=\"grp@\"]')].filter(r=>r.getClientRects().length).map(r=>r.getAttribute('data-rid').slice(4))") or []
def kanban_ids(): return J("[...document.querySelectorAll('[aria-label=\"Kanban das ordens\"] [role=button]')].filter(e=>e.getClientRects().length).map(b=>b.getAttribute('aria-label').split(' ')[1])") or []
def kb_cols(): return J("(()=>{const l=document.querySelector('[aria-label=\"Kanban das ordens\"]'); if(!l||!l.getClientRects().length) return -1; return l.querySelectorAll(':scope>sc-for>div,:scope>div').length;})()")
def carga_on(): return bool(J("(()=>{const t=document.querySelector('[aria-label=\"Alocação de recursos na semana\"]'); return !!t&&t.getClientRects().length>0;})()"))
def chip_on(): return J("[...document.querySelectorAll('[aria-label=\"Filtrar por fase\"] [aria-pressed=true]')].map(b=>b.innerText.replace(/\\s+\\d+$/,'').trim())") or []
def tal_btn(): return J("(document.getElementById('ost_btn')||{innerText:''}).innerText.replace(/\\s+/g,' ').trim()") or ''
def sel(lab): return J(f"(document.querySelector('select[aria-label={json.dumps(lab)}]')||{{value:''}}).value") or ''
def setsel(lab, val):
    J(f"""(()=>{{const i=document.querySelector('select[aria-label={json.dumps(lab)}]'); Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype,'value').set.call(i,{json.dumps(val)});
      i.dispatchEvent(new Event('input',{{bubbles:true}})); i.dispatchEvent(new Event('change',{{bubbles:true}}));}})()"""); time.sleep(.6)
def fase(t): J(f"(()=>{{const b=[...document.querySelectorAll('[aria-label=\"Filtrar por fase\"] button')].find(b=>b.innerText.trim().startsWith({json.dumps(t)})); b&&b.click();}})()"); time.sleep(.5)
def pref(perfil='Ana'): return J(f"localStorage.getItem('safrion.pref.visao:{perfil}:os')")
def busca(): return J("location.search") or ''
def hashd(): return J("(()=>{try{return decodeURIComponent(location.hash)}catch(e){return location.hash}})()") or ''
def toast(): return J("[...document.querySelectorAll('[role=status][aria-live=off]')].map(x=>x.innerText).filter(Boolean).join(' | ')") or ''
def rolagem(): return J("(()=>{const col=document.querySelector('.ml-tog+div'); const m=document.querySelector('main[data-scroll]'); return Math.round((col?col.scrollTop:0)+(m?m.scrollTop:0)+[...document.querySelectorAll('main .g2rola,main .rola')].reduce((a,x)=>a+x.scrollTop,0));})()") or 0
def tecla(k):
    vk = {'ArrowRight': 39, 'ArrowLeft': 37, 'ArrowDown': 40, 'ArrowUp': 38, 'Home': 36, 'End': 35, 'Enter': 13, ' ': 32, 'Escape': 27, 'Tab': 9}[k]
    code = {' ': 'Space'}.get(k, k); txt = {'Enter': '\r', ' ': ' '}.get(k)
    c.tecla(k, code, vk, text=txt); time.sleep(.25)
def foca(k): J(f"document.querySelector('[role=toolbar] [data-visao={k}]').focus()"); time.sleep(.2)
def centro(expr):
    # ponto dentro da janela (a linha da grade é mais larga que a tela: o centro dela ficaria fora)
    return J(f"(()=>{{const e={expr}; if(!e) return null; e.scrollIntoView({{block:'center',inline:'nearest'}}); const r=e.getBoundingClientRect(); return [Math.max(1,Math.min(r.left+r.width/2,r.left+40,innerWidth-2)), r.top+r.height/2];}})()")
def clique(expr):
    """clique de verdade (mouse ou toque, conforme a janela): foca o alvo como a pessoa faria"""
    p = centro(expr)
    if not p: return False
    if TOQUE[0]: c.toque(p[0], p[1])
    else: c.mouse(p[0], p[1]); c.mouse(p[0], p[1], 'mousePressed', 'left'); c.mouse(p[0], p[1], 'mouseReleased', 'left')
    time.sleep(.5); return True
LINHA = lambda oid: f"[...document.querySelectorAll('[data-g2g=g_os] [role=row].g2ed')].find(r=>r.getClientRects().length&&String(r.getAttribute('data-rid')).split('@')[0]==={json.dumps(oid)})"
def painel(): return J("(()=>{const d=[...document.querySelectorAll('aside[role=dialog]')].find(x=>x.getClientRects().length); return d?d.innerText.slice(0,40):'';})()") or ''
DICA = "(()=>{const d=document.getElementById('g2-dica'); return d?{vis:!d.hidden&&d.getClientRects().length>0,t:d.textContent,role:d.getAttribute('role')}:{vis:false,t:'',role:''};})()"
EST = r"""(()=>{const n=s=>(s||'').replace(/\s+/g,' ').trim(); const vis=e=>{ if(!e) return false; const r=e.getBoundingClientRect(); const cs=getComputedStyle(e); return r.width>1&&r.height>1&&cs.visibility!=='hidden'&&cs.display!=='none'; };
 const verde=e=>getComputedStyle(e).backgroundColor==='rgb(30, 122, 76)';
 return [...document.querySelectorAll('header button,header a,main button,main a')].filter(e=>vis(e)&&verde(e)&&!e.closest('.menu-lat')).map(e=>n(e.innerText).slice(0,48)); })()"""
_dup_src = open(os.path.join(HERE, '..', 'ferramentas', 'acoes_duplicadas.py'), encoding='utf-8').read()
DUP = re.search(r'JS=r"""(.*?)"""', _dup_src, re.S).group(1)   # a mesma medida da ferramenta de duplicatas
def dup(): d = J(DUP) or {}; return len(d.get('mesmoRotulo', [])), d
def drag(): return J("document.querySelectorAll('[draggable=true]').length")

def passo(rot, f):
    """cada passo roda mesmo que o anterior falhe: no _render anterior à F1 o vermelho aparece caso a caso"""
    try: f()
    except Exception as e: chk(f'{rot} (exceção)', False, repr(e)[:300])

def modo_comp():
    def _c12():
        abre('OS.dc.html')
        b = bar()
        # C1
        ks = [x['k'] for x in (b or {}).get('bs', []) if x['k'] != 'mais']
        labs = [x['lab'] for x in (b or {}).get('bs', []) if x['k'] != 'mais']
        chips = J("(()=>{const g=document.querySelector('[aria-label=\"Filtrar por fase\"]'); return g?Math.round(g.getBoundingClientRect().right):0;})()")
        chk('C1 barra role=toolbar "Visão das ordens" à direita dos filtros: 4 botões data-visao (lista, agrupada, kanban, carga), aria-label "Ver em …", sem texto visível nem title, svg aria-hidden',
            bool(b) and b['role'] == 'toolbar' and b['lab'] == 'Visão das ordens' and b['vs'] == 'lista agrupada kanban carga' and ks == ['lista', 'agrupada', 'kanban', 'carga']
            and labs == ['Ver em lista', 'Ver em tabela agrupada', 'Ver em kanban', 'Ver em carga por recurso'] and all(x['txt'] == '' and not x['tit'] and x['svg'] for x in b['bs'])
            and b['esq'] >= chips - 1, b)
        # C2
        f = J(CHK_C); at = [x for x in b['bs'] if x['p'] == 'true'] if b else []
        chk('C2 exatamente um aria-pressed="true" (Lista ao entrar); o ativo é tonal (fundo #E4F3E9, barra interna de 2 px), nunca rgb(30, 122, 76); 32 × 32 px no computador',
            not f and len(at) == 1 and at[0]['k'] == 'lista' and at[0]['bg'] == 'rgb(228, 243, 233)' and all(x['w'] == 32 and x['h'] == 32 for x in b['bs'] if x['vis']), [f, at])
        shot('comp_1440_lista')
    passo('C1–C2', _c12)
    def _c3():
        # C3 teclado
        J("(()=>{const bs=[...document.querySelectorAll('[aria-label=\"Filtrar por fase\"] button')]; bs[bs.length-1].focus();})()"); time.sleep(.2)
        tecla('Tab'); f1 = foco(); tecla('Tab'); f2 = foco(); c.tab(1, True); time.sleep(.25); f3 = foco()
        seq = []
        foca('lista')
        for k in ('ArrowRight', 'ArrowRight', 'ArrowRight', 'ArrowRight', 'ArrowLeft', 'Home', 'End', 'ArrowUp', 'ArrowDown'):
            tecla(k); seq.append(foco())
        sem_ativar = ativa() == 'lista' and 'view=' not in busca()
        tecla('Home'); tecla('ArrowRight'); tecla('Enter'); time.sleep(.4); e1 = (ativa(), foco(), busca())
        tecla('ArrowRight'); tecla(' '); time.sleep(.4); e2 = (ativa(), foco(), busca())
        tecla('Tab'); fora_ = foco(); c.tab(1, True); time.sleep(.25); volta = foco()
        chk('C3 Tab para uma vez na barra (entra na ativa e sai com o próximo Tab); ← → com volta, Home/End, ↑ ↓ não movem; seta não ativa (Lista segue ativa, sem ?view); Enter e Espaço ativam e o foco fica no botão; Shift+Tab volta à mesma parada',
            f1 == 'lista' and f2 not in ('lista', 'agrupada', 'kanban', 'carga', 'mais') and f3 == 'lista'
            and seq == ['agrupada', 'kanban', 'carga', 'lista', 'carga', 'lista', 'carga', 'carga', 'carga'] and sem_ativar
            and e1[0] == 'agrupada' and e1[1] == 'agrupada' and 'view=agrupada' in e1[2] and e2[0] == 'kanban' and e2[1] == 'kanban' and 'view=kanban' in e2[2]
            and fora_ not in ('lista', 'agrupada', 'kanban', 'carga') and volta == 'kanban', [f1, f2, f3, seq, sem_ativar, e1, e2, fora_, volta])
    passo('C3', _c3)
    def _c4():
        # C4 dica (g2dica da DS): no foco de teclado na hora; Esc fecha sem tirar o foco; sem aria-describedby repetindo o nome; hover de 300 ms
        tecla('ArrowLeft'); time.sleep(.3); d = J(DICA)
        db = J("document.activeElement.getAttribute('aria-describedby')") or ''
        tecla('Escape'); time.sleep(.2); d2 = J(DICA); fo = foco()
        p = centro("document.querySelector('[role=toolbar] [data-visao=carga]')"); c.mouse(10, 880); time.sleep(.1); c.mouse(p[0], p[1]); time.sleep(.15)
        if not J("document.querySelector('[role=toolbar] [data-visao=carga]').matches(':hover')"):
            J("document.querySelector('[role=toolbar] [data-visao=carga]').dispatchEvent(new PointerEvent('pointerover',{bubbles:true,composed:true,pointerType:'mouse'}))")
        time.sleep(.6); d3 = J(DICA); c.mouse(1430, 890); time.sleep(.3)
        chk('C4 foco de teclado em "tabela agrupada" abre #g2-dica (role=tooltip) "Ver em tabela agrupada", sem aria-describedby repetido; Esc fecha e o foco fica; hover abre "Ver em carga por recurso"',
            d['vis'] and d['t'] == 'Ver em tabela agrupada' and d['role'] == 'tooltip' and 'g2-dica' not in db and not d2['vis'] and fo == 'agrupada' and d3['vis'] and d3['t'] == 'Ver em carga por recurso', [d, db, d2, fo, d3])
    passo('C4', _c4)
    def _c5():
        # C5 uma primária, 0 duplicata, nenhum arrastar, em cada visão
        res = {}
        for k in ('lista', 'agrupada', 'kanban', 'carga'):
            troca_visao(J, k); n, dd = dup(); res[k] = (J(EST), n, drag(), ativa()); shot('comp_1440_' + k)
        chk('C5 em cada visão (1440): só "Nova ordem" como primária, 0 duplicata (acoes_duplicadas) e nenhum [draggable=true]',
            all(v[0] == ['Nova ordem'] and v[1] == 0 and v[2] == 0 and v[3] == k for k, v in res.items()), res)
    passo('C5', _c5)
    def _c6():
        # C6 controle negativo
        limpo = J(CHK_C)
        J("(()=>{const b=document.querySelector('[role=toolbar] [data-visao=lista]'); const k=b.cloneNode(true); k.id='inj'; k.setAttribute('aria-pressed','true'); b.parentElement.appendChild(k);})()")
        s1 = J(CHK_C); J("document.getElementById('inj').remove()")
        J("document.querySelector('[role=toolbar] [data-visao=kanban]').removeAttribute('aria-label')"); s2 = J(CHK_C)
        J("document.querySelector('[role=toolbar] [data-visao=kanban]').setAttribute('aria-label','Ver em kanban')")
        chk('C6 controle negativo: a verificação acusa um 2º aria-pressed=true injetado e um aria-label tirado (e passa limpa)', limpo == [] and any('aria-pressed=true: 2' in x for x in s1) and any('aria-label kanban' in x for x in s2), [limpo, s1, s2])
        guarda_erros('comp')
    passo('C6', _c6)

def modo_celular():
    def _m1():
        abre('OS.dc.html', 390, 844, True, 2)
        b = bar(); vis = [x['k'] for x in b['bs'] if x['vis']] if b else []
        pequenos = [(x['k'], x['w'], x['h']) for x in (b['bs'] if b else []) if x['vis'] and (x['w'] < 44 or x['h'] < 44)]
        shot('cel_390_lista')
        janela(390, 844, False, 1); vai('OS.dc.html'); b2 = bar(); peq2 = [(x['k'], x['w'], x['h']) for x in (b2['bs'] if b2 else []) if x['vis'] and (x['w'] < 44 or x['h'] < 44)]
        chk('M1 alvos ≥ 44 × 44 px a 390 px com toque (pointer:coarse) e sem toque (janela de 390 px com mouse)', bool(b) and not pequenos and bool(b2) and not peq2 and len(vis) == 4, [pequenos, peq2, vis])
    passo('M1', _m1)
    def _m2():
        abre('OS.dc.html', 390, 844, True, 2)
        b = bar(); vis = [x['k'] for x in b['bs'] if x['vis']]
        clique("document.querySelector('[role=toolbar] [data-visao-mais]')"); time.sleep(.3)
        menu = J("(()=>{const m=document.querySelector('[role=menu][data-visoes-menu]'); return m&&m.getClientRects().length?[...m.querySelectorAll('[role=menuitemradio]')].map(i=>[i.getAttribute('data-visao-menu'),i.innerText.trim(),i.getAttribute('aria-checked')]):null;})()")
        fm = foco(); tecla('Escape'); time.sleep(.3)
        fechado = not J("!!document.querySelector('[role=menu][data-visoes-menu]')"); fe = foco()
        tecla('ArrowDown'); time.sleep(.4); fd = foco(); tecla('Enter'); time.sleep(.6)
        b3 = bar(); mais = next((x for x in b3['bs'] if x['k'] == 'mais'), {}); pressed_vis = [x['k'] for x in b3['bs'] if x['vis'] and x['p'] == 'true']
        shot('cel_390_carga')
        chk('M2 390 px: Lista, Tabela agrupada e Kanban na barra + "mais"; o menu mostra "Carga por recurso" em texto; Esc fecha e devolve o foco ao "mais"; ↓ no "mais" abre o menu; com a Carga escolhida o "mais" leva a marca e diz o nome',
            vis == ['lista', 'agrupada', 'kanban', 'mais'] and menu == [['carga', 'Carga por recurso', 'false']] and fm == 'menu:carga' and fechado and fe == 'mais' and fd == 'menu:carga'
            and ativa() == 'carga' and carga_on() and mais.get('ativo') == 'true' and mais.get('lab') == 'Mais visões (atual: carga por recurso)' and mais.get('bg') == 'rgb(228, 243, 233)'
            and not pressed_vis and 'view=carga' in busca(), [vis, menu, fm, fechado, fe, fd, ativa(), mais, pressed_vis, busca()])
    passo('M2', _m2)
    def _m3():
        # M3 nada cortado em cada visão; primária única alcançável; 0 duplicata
        res = {}
        for k in ('lista', 'agrupada', 'kanban', 'carga'):
            troca_visao(J, k); m = J(MEDE); res[k] = (resumo(m), J(EST), dup()[0], ativa()); shot('cel_390_' + k)
        chk('M3 390 px, em cada visão: nada cortado, sem rolagem lateral, título e "Nova ordem" alcançáveis (MEDE/resumo vazio), uma primária e 0 duplicata',
            all(v[0] == [] and v[1] == ['Nova ordem'] and v[2] == 0 and v[3] == k for k, v in res.items()), res)
    passo('M3', _m3)
    def _m4():
        # M4 toque longo: dica sem trocar a visão
        troca_visao(J, 'lista'); p = centro("document.querySelector('[role=toolbar] [data-visao=kanban]')")
        c.call('Input.dispatchTouchEvent', {'type': 'touchStart', 'touchPoints': [{'x': p[0], 'y': p[1]}]}); time.sleep(.65); d = J(DICA)
        c.call('Input.dispatchTouchEvent', {'type': 'touchEnd', 'touchPoints': []}); time.sleep(.5)
        chk('M4 toque longo (650 ms) no Kanban mostra a dica "Ver em kanban" e não troca a visão', d['vis'] and d['t'] == 'Ver em kanban' and ativa() == 'lista', [d, ativa()])
        guarda_erros('celular')
    passo('M4', _m4)

# ---------- abas extras (nova aba e deep-link) ----------
class Aba:
    def __init__(s, alvo):
        s.alvo = alvo['id']; s.ws = WS(alvo['webSocketDebuggerUrl']); s.i = 0; s.call('Page.enable'); s.call('Runtime.enable')
    def call(s, m, p=None, timeout=60):
        s.i += 1; mid = s.i; s.ws.send(json.dumps({'id': mid, 'method': m, 'params': p or {}})); fim = time.monotonic() + timeout
        while True:
            r = json.loads(s.ws.recv(timeout=max(.1, fim - time.monotonic())))
            if r.get('id') == mid:
                if 'error' in r: raise RuntimeError(str(r['error']))
                return r.get('result', {})
    def js(s, e):
        r = s.call('Runtime.evaluate', {'expression': e, 'awaitPromise': True, 'returnByValue': True})
        if 'exceptionDetails' in r: raise RuntimeError(str(r['exceptionDetails'])[:300])
        return r['result'].get('value')
    def espera(s, pag):
        for _ in range(80):
            time.sleep(.25)
            try:
                if pag in (s.js("location.href") or '') and s.js("document.readyState") == 'complete' and s.js("!!window.__g2glob&&!!document.querySelector('h1')"): break
            except Exception: pass
        time.sleep(.8)
    def fecha(s):
        try: urllib.request.urlopen(f'http://127.0.0.1:{porta}/json/close/{s.alvo}', timeout=10)
        except Exception: pass
def alvos(): return json.load(urllib.request.urlopen(f'http://127.0.0.1:{porta}/json/list', timeout=10))
def espera_pag(pag):
    for _ in range(80):
        time.sleep(.25)
        try:
            if pag in (J("location.href") or '') and J("document.readyState") == 'complete' and J("!!window.__g2glob&&!!document.querySelector('h1')"): break
        except Exception: pass
    time.sleep(.9); pronto()

def prepara_e3(w, h, toque):
    """Fazenda Todas, Safra 2026/27, fase Em execução, Tabela agrupada; rola a lista; abre a OS-0421 no painel (só ela e a OS-0420 têm página de detalhe)."""
    abre('OS.dc.html', w, h, toque, 2 if toque else 1)
    setsel('Filtrar por fazenda', 'Todas'); setsel('Filtrar por safra', '2026/27'); fase('Em execução'); troca_visao(J, 'agrupada')
    J("(()=>{const m=document.querySelector('main[data-scroll]'); const col=document.querySelector('.ml-tog+div'); const r=[...document.querySelectorAll('main .g2rola')].find(x=>x.getClientRects().length); if(r) r.scrollTop=Math.min(60,r.scrollHeight); if(m) m.scrollTop=Math.min(90,m.scrollHeight); if(col) col.scrollTop=Math.min(40,col.scrollHeight);})()")
    time.sleep(.3); r0 = rolagem()
    J(f"(()=>{{const r={LINHA('OS-0421')}; r&&r.focus({{preventScroll:true}}); return !!r;}})()"); tecla('Enter'); time.sleep(.6)
    return r0
def confere_volta(tag, r0, extra=None):
    time.sleep(.6)
    st = {'ativa': ativa(), 'faz': sel('Filtrar por fazenda'), 'saf': sel('Filtrar por safra'), 'chip': chip_on(), 'rol': rolagem(), 'r0': r0, 'foco': foco(), 'painel': painel(),
          'busca': busca(), 'grupos': grupos()[:4]}
    if extra: st.update(extra)
    foco_ok = st['foco'].startswith('linha:OS-0421') or st['painel'].startswith('OS-0421')
    chk(f'E3 {tag}: volta à Tabela agrupada com Fazenda Todas, Safra 2026/27, fase Em execução, rolagem ±4 px e o foco na OS-0421 (ou o painel dela, se a página voltou da memória)',
        st['ativa'] == 'agrupada' and st['faz'] == 'Todas' and st['saf'] == '2026/27' and st['chip'] == ['Em execução'] and abs(st['rol'] - r0) <= 4 and foco_ok, st)
    return st

def modo_e2e():
    for (w, h, toque, tag) in ((1440, 900, False, '1440'), (390, 844, True, '390')):
        def _e12():
            # E1 · filtro → Agrupada, por clique e por teclado; hash intacto
            abre('OS.dc.html#tal=Santa Rita|T1', w, h, toque, 2 if toque else 1); time.sleep(.4)
            fase('Em execução'); l0 = sorted(x.split('@')[0] for x in ids()); t0 = tal_btn()
            rodadas = []
            for como in ('clique', 'teclado'):
                if como == 'clique': troca_visao(J, 'agrupada')
                else:
                    foca(ativa()); tecla('Home'); tecla('Enter'); time.sleep(.4); tecla('ArrowRight'); tecla(' '); time.sleep(.5)
                kids = sorted({x.split('@')[0] for x in ids() if not x.startswith('grp@')}); gt = J("[...document.querySelectorAll('main [role=note]')].filter(n=>n.getClientRects().length).map(n=>n.innerText).find(t=>/^Total:/.test(t))||''")
                rodadas.append({'como': como, 'ativa': ativa(), 'chip': chip_on(), 'tal': tal_btn(), 'grupos': grupos(), 'kids': kids, 'tot': gt, 'busca': busca(), 'hash': hashd()})
                if como == 'clique': troca_visao(J, 'lista')
            ok1 = all(r['ativa'] == 'agrupada' and r['chip'] == ['Em execução'] and r['tal'] == t0 and r['grupos'] == ['Santa Rita|T1'] and r['kids'] == l0
                      and r['tot'].startswith(f'Total: {len(l0)} O.S.') and 'view=agrupada' in r['busca'] and r['hash'] == '#tal=Santa Rita|T1' for r in rodadas)
            chk(f'E1 {tag}: talhão T1 (pelo endereço) + fase Em execução → Tabela agrupada por clique e por teclado: os mesmos chips, talhão e linhas, subtotal só do recorte, ?view=agrupada e o hash intacto',
                ok1 and len(l0) >= 1 and t0.startswith('Talhão: T1'), [l0, t0, rodadas])
            shot(f'e2e_{tag}_agrupada')
            # E2 · abrir a O.S. do grupo → painel → Esc → foco volta à linha
            alvo = l0[0]
            clique(LINHA(alvo)); pa = painel(); tecla('Tab'); dentro = J("!!(document.activeElement&&document.activeElement.closest('aside[role=dialog]'))"); tecla('Escape'); time.sleep(.5)
            chk(f'E2 {tag}: abrir {alvo} dentro do grupo abre o painel dela (Tab entra no painel); Esc fecha e o foco volta à linha', pa.startswith(alvo) and dentro and painel() == '' and foco().startswith('linha:' + alvo), [pa, dentro, painel(), foco()])
            guarda_erros(f'E1-E2 {tag}')
        passo(f'E1–E2 {tag}', _e12)
        def _e3():
            # E3 · volta do detalhe: link "Voltar", trilha e history.back() (mesma aba); nova aba e deep-link (revisão Codex, item 2)
            for como in ('link Voltar', 'trilha', 'history.back()'):
                r0 = prepara_e3(w, h, toque); pa = painel()
                J("(()=>{const a=[...document.querySelectorAll('aside[role=dialog] a')].find(a=>/Abrir ordem completa/.test(a.innerText)); a&&a.click();})()"); espera_pag('CA-01det.dc.html')
                marca = J("JSON.stringify([history.length, (history.state||{}).g2voltaDe||''])")
                if como == 'link Voltar': J("document.querySelector('a[aria-label=Voltar]').click()")
                elif como == 'trilha': J("(()=>{const a=[...document.querySelectorAll('header a[href]')].find(a=>a.getAttribute('aria-label')!=='Voltar'&&/OS\\.dc\\.html$/.test(a.getAttribute('href'))); a&&a.click();})()")
                else: J("history.back()")
                espera_pag('OS.dc.html')
                st = confere_volta(f'{tag} · {como} (mesma aba)', r0, {'marca': marca, 'painel_antes': pa})
                hl = json.loads(marca)
                chk(f'E3 {tag} · {como}: a página de detalhe registrou o histórico comprovado (history.length > 1 e a marca própria)', hl[0] > 1 and bool(hl[1]), marca)
                if tag == '1440' and como == 'link Voltar': shot('e2e_1440_volta_detalhe')
        passo(f'E3 {tag} mesma aba', _e3)
        def _e3n():
            # nova aba: o detalhe aberto em outra aba tem o referrer da lista e nenhum histórico; o "Voltar" vai ao destino canônico (?view) e restaura
            r0 = prepara_e3(w, h, toque)
            J("(()=>{const a=[...document.querySelectorAll('aside[role=dialog] a')].find(a=>/Abrir ordem completa/.test(a.innerText)); a.dispatchEvent(new MouseEvent('auxclick',{bubbles:true,button:1}));})()")
            antes = {x['id'] for x in alvos()}
            c.call('Runtime.evaluate', {'expression': "window.open('CA-01det.dc.html','_blank'); 1", 'userGesture': True}); time.sleep(1.5)
            novo = [x for x in alvos() if x['id'] not in antes and x.get('type') == 'page']
            if novo:
                a = Aba(novo[0]); a.espera('CA-01det.dc.html')
                if toque: a.call('Emulation.setDeviceMetricsOverride', {'width': w, 'height': h, 'deviceScaleFactor': 2, 'mobile': True})
                na = a.js("JSON.stringify([history.length,(history.state||{}).g2voltaDe||'',(()=>{try{return new URL(document.referrer).pathname.split('/').pop();}catch(e){return '';}})()])")
                a.js("document.querySelector('a[aria-label=Voltar]').click()"); a.espera('OS.dc.html'); time.sleep(.8)
                st = {'url': a.js("location.pathname.split('/').pop()+location.search"), 'ativa': a.js("(document.querySelector('[role=toolbar] [data-visao][aria-pressed=true]')||{getAttribute:()=>''}).getAttribute('data-visao')"),
                      'faz': a.js("document.querySelector('select[aria-label=\"Filtrar por fazenda\"]').value"), 'saf': a.js("document.querySelector('select[aria-label=\"Filtrar por safra\"]').value"),
                      'chip': a.js("[...document.querySelectorAll('[aria-label=\"Filtrar por fase\"] [aria-pressed=true]')].map(b=>b.innerText.replace(/\\s+\\d+$/,'').trim())"),
                      'foco': a.js("(document.activeElement&&document.activeElement.getAttribute('data-rid'))||''"), 'na': na}
                a.fecha(); c.call('Page.bringToFront')
                chk(f'E3 {tag} · nova aba (referrer da lista, history.length 1, sem marca): o "Voltar" não usa history.back(); abre OS.dc.html?view=agrupada com Fazenda, Safra, fase e o foco na OS-0421',
                    json.loads(na)[0] == 1 and not json.loads(na)[1] and json.loads(na)[2] == 'OS.dc.html' and st['url'] == 'OS.dc.html?view=agrupada' and st['ativa'] == 'agrupada'
                    and st['faz'] == 'Todas' and st['saf'] == '2026/27' and st['chip'] == ['Em execução'] and str(st['foco']).startswith('OS-0421'), st)
            else: chk(f'E3 {tag} · nova aba', False, 'o Chrome não abriu a aba (window.open)')
        passo(f'E3 {tag} nova aba', _e3n)
        def _e3d():
            # deep-link: detalhe aberto direto, sem contexto: o link segue como está (OS.dc.html, a entrada usa a preferência)
            t = json.load(urllib.request.urlopen(urllib.request.Request(f'http://127.0.0.1:{porta}/json/new?{BASE}CA-01det.dc.html', method='PUT'), timeout=30))
            a = Aba(t); a.espera('CA-01det.dc.html'); href0 = a.js("document.querySelector('a[aria-label=Voltar]').getAttribute('href')")
            a.js("document.querySelector('a[aria-label=Voltar]').click()"); a.espera('OS.dc.html')
            dl = {'href0': href0, 'url': a.js("location.pathname.split('/').pop()+location.search"), 'hist': a.js("history.length")}
            a.fecha(); c.call('Page.bringToFront')
            chk(f'E3 {tag} · deep-link (detalhe aberto direto, sem contexto): o "Voltar" segue o link (OS.dc.html, sem ?view e sem history.back())', dl['href0'] == 'OS.dc.html' and dl['url'] == 'OS.dc.html' and dl['hist'] == 2, dl)
            guarda_erros(f'E3 {tag}')
        passo(f'E3 {tag} deep-link', _e3d)
    # ---------------- 1440 daqui em diante ----------------
    def _e5():
        # E5 · trocar de visão não grava no cenário (antes da E3b, que cancela uma ordem para montar o caso)
        abre('OS.dc.html')
        NEG = "JSON.stringify(Object.keys(localStorage).filter(k=>k.indexOf('safrion.pref.')!==0).sort().map(k=>[k,localStorage.getItem(k)]))"
        c0 = J("localStorage.getItem('talhao-os-cenario-v1')"); n0 = J(NEG)
        for k in ('agrupada', 'kanban', 'carga', 'lista', 'kanban', 'agrupada'): troca_visao(J, k)
        foca(ativa()); tecla('End'); tecla('Enter'); tecla('Home'); tecla(' ')
        chk('E5 trocar de visão (clique e teclado, 8 trocas) não muda o cenário talhao-os-cenario-v1 nem outra chave de negócio, byte a byte; só a preferência (safrion.pref.)',
            J("localStorage.getItem('talhao-os-cenario-v1')") == c0 and J(NEG) == n0 and bool(pref()), [c0 is None, len(n0 or ''), pref()])
    passo('E5', _e5)
    def _e3b():
        # E3b · vazio por regra da visão: Canceladas no Kanban
        abre('OS.dc.html')
        r = J("(()=>{ const r=window.__cen.cenMudar(null,c=>window.__cen.osc_cancelar(c,'OS-0424','teste VISOES-1',['','',''],{k:'Ana'})); window.dispatchEvent(new StorageEvent('storage',{key:'talhao-os-cenario-v1'})); return JSON.stringify(r); })()"); time.sleep(.5)
        fase('Canceladas'); nl = len(ids()); troca_visao(J, 'kanban'); es = estado(); cols = kb_cols(); pk = pref(); shot('e2e_1440_kanban_canceladas')
        J("(()=>{const b=[...document.querySelectorAll('[data-visoes-estado] button')].find(b=>b.innerText.trim()==='Ver em lista'); b&&b.click();})()"); time.sleep(.6)
        a1 = (ativa(), busca(), pref(), len(ids()))
        c.goto(J("location.href"), .6); pronto(); a2 = (ativa(), busca())
        vai('OS.dc.html'); a3 = ativa()
        chk('E3b fase Canceladas → Kanban: "Canceladas ficam fora do quadro: 1 ordem no filtro." com "Ver em lista" (o quadro segue com 5 colunas); "Ver em lista" abre a Lista com ?view=lista sem mudar a preferência; F5 continua na Lista; nova entrada sem ?view abre o Kanban (preferência)',
            nl == 1 and es and es['tipo'] == 'regra' and es['t'] == 'Canceladas ficam fora do quadro: 1 ordem no filtro. Ver em lista' and cols == 5 and pk == 'kanban'
            and a1[0] == 'lista' and 'view=lista' in a1[1] and a1[2] == 'kanban' and a1[3] == 1 and a2 == ('lista', a1[1]) and a3 == 'kanban', [r, nl, es, cols, pk, a1, a2, a3])
    passo('E3b', _e3b)
    def _e3c():
        # E3c · erro da visão (Kanban, Carga): o estado diz o motivo e "Ver em lista" leva à Lista, que funciona; cenário ilegível: recuperação sem apagar
        for k, nome in (('kanban', 'Kanban'), ('carga', 'Carga por recurso')):
            abre('OS.dc.html?view=lista'); J(f"window.__g2visaoFalha={json.dumps(k)}"); p0 = pref(); troca_visao(J, k); es = estado(); sem = (kb_cols() == -1) if k == 'kanban' else (not carga_on())
            shot(f'e2e_1440_erro_{k}')
            J("(()=>{const b=[...document.querySelectorAll('[data-visoes-estado] button')].find(b=>b.innerText.trim()==='Ver em lista'); b&&b.click();})()"); time.sleep(.6)
            chk(f'E3c erro ao montar a visão {nome}: "Não foi possível mostrar a visão {nome}: …" + "Ver em lista" (painel não aparece); a Lista abre e funciona (linhas, ?view=lista), sem gravar preferência no fallback',
                es and es['tipo'] == 'erro' and es['t'].startswith(f'Não foi possível mostrar a visão {nome}: falha simulada pelo teste') and sem and ativa() == 'lista' and len(ids()) >= 5 and 'view=lista' in busca()
                and pref() == k and estado() is None, [es, sem, ativa(), len(ids()), busca(), p0, pref()])
        abre('OS.dc.html?view=lista'); J("localStorage.setItem('talhao-os-cenario-v1','{corrompido'); 1"); c.goto(BASE + 'OS.dc.html?view=lista', .6); pronto()
        e1 = estado(); nl = len(ids()); v1 = J("localStorage.getItem('talhao-os-cenario-v1')"); troca_visao(J, 'kanban'); e2 = estado(); shot('e2e_1440_cenario_ilegivel')
        J("(()=>{const b=[...document.querySelectorAll('[data-visoes-estado] button')].find(b=>/Recomeçar/.test(b.innerText)); b&&b.click();})()"); time.sleep(.6)
        v2 = J("JSON.stringify([localStorage.getItem('talhao-os-cenario-v1'), localStorage.getItem('talhao-os-cenario-v1:ilegivel')])")
        chk('E3c cenário ilegível (afeta a Lista também): a Lista e o Kanban dizem o que houve com "Recomeçar a demonstração"; nada é apagado (o gravado fica em talhao-os-cenario-v1:ilegivel)',
            e1 and e1['tipo'] == 'cenario' and 'não pôde ser lido' in e1['t'] and nl >= 5 and v1 == '{corrompido' and e2 and e2['tipo'] == 'cenario'
            and json.loads(v2) == [None, '{corrompido'] and estado() is None, [e1, nl, v1, e2, v2])
        guarda_erros('E3b-E3c')
    passo('E3c', _e3c)
    def _e4():
        # E4 · precedência na entrada (URL › preferência › Lista), Lista explícita e F5 (Codex, item 1), perfil (Codex, item 3)
        abre('OS.dc.html'); troca_visao(J, 'kanban')
        vai('OS.dc.html'); p1 = (ativa(), busca())
        vai('OS.dc.html?view=lista'); p2 = (ativa(), pref())
        vai('OS.dc.html?view=xyz'); time.sleep(.3); p3 = (ativa(), toast(), busca()); c.goto(J("location.href"), .6); pronto(); p3b = (ativa(), toast())
        vai('OS.dc.html'); troca_visao(J, 'lista'); u = busca(); c.goto(J("location.href"), .6); pronto(); p4 = (u, ativa(), pref())
        vai('OS.dc.html'); troca_visao(J, 'kanban'); setsel('Trocar perfil de demonstração', 'Caio'); p5 = ativa()
        vai('OS.dc.html'); p6 = ativa(); troca_visao(J, 'agrupada'); setsel('Trocar perfil de demonstração', 'Ana'); p7 = ativa(); vai('OS.dc.html'); p8 = (ativa(), pref('Ana'), pref('Caio'))
        J("localStorage.clear(); 1"); vai('OS.dc.html'); p9 = ativa()
        chk('E4 sem ?view abre a preferência (Kanban); ?view=lista vence a preferência e não a grava; ?view=xyz abre a preferência com aviso sem o valor e o endereço perde o valor (F5 sem aviso)',
            p1 == ('kanban', '') and p2 == ('lista', 'kanban') and p3[0] == 'kanban' and 'não existe nesta lista: aberta em Kanban (sua última escolha)' in p3[1] and 'xyz' not in p3[1]
            and 'view' not in p3[2] and p3b[0] == 'kanban' and 'não existe' not in p3b[1], [p1, p2, p3, p3b])
        chk('E4b (Codex, item 1) preferência Kanban → escolher Lista grava ?view=lista → F5 continua na Lista (e a Lista vira a preferência)', p4 == ('?view=lista', 'lista', 'lista'), p4)
        chk('E4c (Codex, item 3) trocar o perfil não muda a visão aberta; a próxima entrada sem ?view usa a preferência do perfil (Caio sem preferência: Lista; Ana: Kanban); localStorage limpo abre a Lista',
            p5 == 'kanban' and p6 == 'lista' and p7 == 'agrupada' and p8 == ('kanban', 'kanban', 'agrupada') and p9 == 'lista', [p5, p6, p7, p8, p9])
    passo('E4', _e4)
    def _e6():
        # E6 · entrada por endereço
        abre('OS.dc.html?view=kanban#OS-0418'); time.sleep(.5); q1 = (ativa(), painel(), hashd())
        vai('OS.dc.html#OS-0430:ajustar'); time.sleep(.6); q2 = (ativa(), painel(), J("!!document.querySelector('aside[role=dialog] input')"))
        vai('OS.dc.html?theme=dark&view=agrupada#tal=Santa Rita|T1'); time.sleep(.6); q3 = (ativa(), tal_btn(), busca(), hashd(), grupos())
        chk('E6 OS.dc.html?view=kanban#OS-0418 abre o Kanban e a OS-0418; #OS-0430:ajustar abre a ordem para ajustar; ?theme=dark&view=agrupada#tal=Santa Rita|T1 abre a Agrupada com T1, theme e hash intactos',
            q1[0] == 'kanban' and q1[1].startswith('OS-0418') and q1[2] == '#OS-0418' and q2[1].startswith('OS-0430') and q2[2]
            and q3[0] == 'agrupada' and q3[1].startswith('Talhão: T1') and 'theme=dark' in q3[2] and 'view=agrupada' in q3[2] and q3[3] == '#tal=Santa Rita|T1' and q3[4] == ['Santa Rita|T1'], [q1, q2, q3])
        guarda_erros('E4-E6')
    passo('E6', _e6)

def modo_e7():
    """Cliques da persona até o mesmo resultado (window.__cl conta cada clique no documento), na tela que existir."""
    def conta(): return J("window.__cl||0")
    def liga(): J("window.__cl=0; if(!window.__clOn){ window.__clOn=1; document.addEventListener('click',()=>{ window.__cl=(window.__cl||0)+1; },true); } 1")
    def agrupar():
        if J("!!document.querySelector('[role=toolbar] [data-visao=agrupada]')"): J("document.querySelector('[role=toolbar] [data-visao=agrupada]').click()")
        else: J("[...document.querySelectorAll('button')].find(b=>b.innerText.trim()==='Agrupar por talhão').click()")
        time.sleep(.6)
    def agrupado(): return len(grupos()) > 0
    abre('OS.dc.html'); liga()
    # A · filtrar → agrupar → abrir → voltar (detalhe completo) → de volta onde estava (agrupada, filtro). O clique num link que troca de página
    # é contado à parte (+1): o contador da página que sai não sobrevive à navegação
    fase('Em execução'); agrupar()
    J(f"{LINHA('OS-0421')}.click()"); time.sleep(.5); n1 = conta()
    J("[...document.querySelectorAll('aside[role=dialog] a')].find(a=>/Abrir ordem completa/.test(a.innerText)).click()"); espera_pag('CA-01det.dc.html'); liga()
    J("document.querySelector('a[aria-label=Voltar]').click()"); espera_pag('OS.dc.html'); liga()
    extra = 0
    if not agrupado(): agrupar(); extra = conta()
    a = n1 + 2 + extra; ok_a = agrupado() and chip_on() == ['Em execução']
    # B · voltar à O.S. em outra entrada (menu, sem ?view): 1 clique para entrar + o que faltar para estar agrupado
    vai('Main.dc.html'); achou = J("(()=>{const a=[...document.querySelectorAll('a[href]')].find(a=>/(^|\\/)OS\\.dc\\.html$/.test(a.getAttribute('href'))); if(a) a.click(); return !!a;})()")
    if not achou: vai('OS.dc.html')
    espera_pag('OS.dc.html'); liga()
    if not agrupado(): agrupar()
    b0 = 1; b = b0 + conta(); tela = 'seletor' if J("!!document.querySelector('[role=toolbar][data-visoes]')") else 'botão Agrupar por talhão'
    print(f'CLIQUES · tela: {tela} · A (filtrar → agrupar → abrir → voltar e estar agrupado): {a} (dos quais {extra} para reagrupar) · B (outra entrada até agrupado): {b} (dos quais {b0} para entrar)', flush=True)
    chk(f'E7 cliques medidos ({tela}): A = {a}, B = {b}', ok_a and agrupado(), [a, b, ok_a])

try:
    {'comp': modo_comp, 'celular': modo_celular, 'e2e': modo_e2e, 'e7': modo_e7}[MODO]()
    chk('sem erro de script nas páginas', not ERROS and not errs(), ERROS + [errs()])
except Exception as e:
    import traceback; traceback.print_exc(); chk('execução sem exceção', False, repr(e)[:400])
finally:
    try: c.close()
    except Exception: pass
    try: _proc.terminate(); _proc.wait(5)
    except Exception: pass
    srv.terminate()
print(f'RESULTADO: {len(OK)} ok · {len(FAIL)} falhas ({MODO})' + (' · FALHAS: ' + ' | '.join(FAIL) if FAIL else ''))
sys.exit(1 if FAIL else 0)
