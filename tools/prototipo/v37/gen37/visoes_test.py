# -*- coding: utf-8 -*-
"""VISOES-1 (pedido do proprietário, 10/10/2026) · seletor de visões por ícone na O.S., no navegador (Chrome headless por CDP).
Modos (DESENHO.md, F1):
 comp     · 1440 × 900, Chrome com hover real: C1 barra e rótulos; C2 um ativo tonal; C3 teclado (Tab uma vez, setas sem ativar, Enter/Espaço,
            Home/End, foco fica); C4 dica no foco e no hover (g2dica da DS); C5 uma primária, 0 duplicata e nenhum arrastar em cada visão;
            C6 controle negativo da verificação.
 celular  · 390 × 844, escala 2, toque: M1 alvos ≥ 44 px (com e sem toque); M2 3 + "mais" (menu com nome, Esc devolve o foco, ativa no
            "mais" marcada); M3 nada cortado, primária alcançável, 0 duplicata; M4 toque longo mostra a dica sem trocar a visão.
 e2e      · em 1440 × 900 e 390 × 844: E1 filtro → Tabela agrupada por Talhão (clique e teclado); E2 painel → Esc → foco na linha; E3 volta do detalhe
            (link "Voltar", trilha, history.back(), nova aba, deep-link); E3b vazio por regra (Canceladas no Kanban) e "Ver em tabela";
            E3c erro da visão (Kanban e Carga) e cenário ilegível; E4 precedência (URL › preferência › Lista; Lista explícita e F5; perfil);
            E5 trocar de visão não grava no cenário; E6 entrada por endereço (hash e outros parâmetros intactos).
 e7       · cliques medidos (window.__cl) em "filtrar → agrupar → abrir → voltar" e "voltar à O.S. em outra entrada", na tela que houver
            (seletor novo ou o botão "Agrupar por talhão" anterior): rode com VISOES_RENDER=<_render anterior> para o "antes".
Revisão VISOES-1 (lentes independentes, 10/10): C4b dica só no foco de teclado; C7 cores forçadas; M5 toque curto sem dica presa; M6 parada de
Tab depois de mudar a largura ou girar; M7 menu do "mais" ao alargar; M8 Kanban a 390 px; E1b subtotal do grupo = Total; E3 pela regra 02 (Voltar
sempre canônico; contexto antigo, de outro perfil, de outra safra e já usado; foco reafirmado); E3b2 recorte só com canceladas; E3d foco depois da
ação do estado; E5 trocar de visão não cria histórico; E6b entrada por endereço com a Safra guardada; E8 Carga com o mesmo recorte e "Sem alocação".
VISOES-2 (pedido do proprietário, 14/10): Lista e Tabela agrupada viraram uma visão só, a Tabela (data-visao=lista, "Ver em tabela"); agrupar é o
"Agrupar por" da grade (Atividade, Responsável, Início, Talhão), com descer e trilha, no endereço ?ag=&trilha= e guardado por perfil × tela × grade
(g2ag:<tela>:<grade>:<perfil>). A antiga "agrupada" é a Tabela + Agrupar por Talhão (?ag=onde): troca_visao(J, 'agrupada') faz esse caminho.
Uso: python3 visoes_test.py comp|celular|e2e|e7 · VISOES_RENDER=<dir> serve outro _render · VISOES_SAIDA=<dir> grava as capturas ·
VISOES_SO=E3,E8 roda só os passos cujo rótulo começa por um desses prefixos."""
import os, sys, time, json, re, subprocess, tempfile, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, servir, MEDE, resumo, troca_visao, agrupar_por, agrupado_por, cv_todas_js
from urllib.parse import parse_qsl
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
# talhão escolhido na faixa "Filtros desta tela" (13/10: o botão "Talhão: …" da barra, ost_btn, saiu; o mesmo filtro f.tal da coluna Talhão)
def tal_faixa(): return J("(()=>{const s=document.querySelector('select[aria-label=\"Filtrar por talhão\"]'); return s&&s.selectedIndex>=0?s.options[s.selectedIndex].text.trim():'';})()") or ''
def ag(): return agrupado_por(J)   # VISOES-2: nome no botão "Agrupar por" ('' = Sem agrupar)
def gpref(perfil='Ana'): return J(f"localStorage.getItem('g2ag:OS.dc.html:g_os:{perfil}')")   # agrupamento guardado por perfil × tela × grade
def params(s): return sorted(parse_qsl(str(s or '').lstrip('?'), keep_blank_values=True))   # parâmetros do endereço, sem depender da ordem
AG_ONDE = [('ag', 'onde'), ('view', 'lista')]   # endereço da Tabela agrupada por Talhão com a visão escolhida (sem ficha nem outro parâmetro)
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

SO = [x.strip() for x in (os.environ.get('VISOES_SO') or '').split(',') if x.strip()]
def mclique(p): c.mouse(p[0], p[1]); c.mouse(p[0], p[1], 'mousePressed', 'left'); c.mouse(p[0], p[1], 'mouseReleased', 'left'); time.sleep(.5)
def paradas(): return J("[...document.querySelectorAll('[role=toolbar][data-visoes] [data-visao],[role=toolbar][data-visoes] [data-visao-mais]')].filter(b=>b.getClientRects().length&&b.tabIndex===0).map(b=>b.getAttribute('data-visao')||'mais')") or []
def ultimo_chip(): J("(()=>{const bs=[...document.querySelectorAll('[aria-label=\"Filtrar por fase\"] button')].filter(b=>b.getClientRects().length); bs[bs.length-1].focus();})()"); time.sleep(.2)
def num_br(t):
    m = re.search(r'(\d{1,3}(?:\.\d{3})*(?:,\d+)?|\d+(?:,\d+)?)', t or '')
    return float(m.group(1).replace('.', '').replace(',', '.')) if m else None
GRUPOS_AREA = r"""(()=>{ const g=document.querySelector('[data-g2g=g_os]'); if(!g) return null; const hs=[...g.querySelectorAll('[role=columnheader]')]; const ia=hs.findIndex(h=>/^área/i.test(h.innerText.trim()));
 return [...g.querySelectorAll('[role=row][data-rid^="grp@"]')].filter(r=>r.getClientRects().length).map(r=>{ const cs=[...r.querySelectorAll('[role=cell]')]; return [r.getAttribute('data-rid').slice(4),(cs[ia]||{innerText:''}).innerText.trim()]; }); })()"""
# nota do total do agrupamento por Talhão (VISOES-2): "N O.S. · X ha · a O.S. de vários talhões aparece em cada um e conta uma vez no total"
def total_nota(): return J("[...document.querySelectorAll('main [role=note]')].filter(n=>n.getClientRects().length).map(n=>n.innerText.trim()).find(t=>/^\\d+ O\\.S\\. · .* · a O\\.S\\. de vários talhões/.test(t))||''") or ''
def blocos(): return sorted(set(J("[...document.querySelectorAll('[aria-label=\"Alocação de recursos na semana\"] button,[aria-label=\"Alocação de recursos na semana\"] a')].filter(b=>b.getClientRects().length).map(b=>b.innerText.split(' ')[0]).filter(x=>/^O[SB]-/.test(x))") or []))
def sem_aloc(): return J("(()=>{const g=document.querySelector('[role=group][aria-label^=\"Ordens do recorte sem alocação\"]'); return g&&g.getClientRects().length?g.innerText.replace(/\\s+/g,' ').trim():'';})()") or ''
def nav_tipo(): return J("(((performance.getEntriesByType('navigation')||[])[0]||{}).type)||''") or ''

def passo(rot, f):
    """cada passo roda mesmo que o anterior falhe: no _render anterior à F1 o vermelho aparece caso a caso"""
    if SO and not any(rot.startswith(x) for x in SO): return
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
        # VISOES-2 F2a (13/10): o Calendário entra entre o Kanban e a Carga (ordem do registro, visoes.ORDEM)
        # VISOES-2 (14/10): Lista e Tabela agrupada viraram a Tabela (agrupar é o "Agrupar por" da grade)
        chk('C1 barra role=toolbar "Visão das ordens" à direita dos filtros: 4 botões data-visao (lista = Tabela, kanban, calendario, carga), aria-label "Ver em …", sem texto visível nem title, svg aria-hidden',
            bool(b) and b['role'] == 'toolbar' and b['lab'] == 'Visão das ordens' and b['vs'] == 'lista kanban calendario carga' and ks == ['lista', 'kanban', 'calendario', 'carga']
            and labs == ['Ver em tabela', 'Ver em kanban', 'Ver em calendário', 'Ver em carga por recurso'] and all(x['txt'] == '' and not x['tit'] and x['svg'] for x in b['bs'])
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
            f1 == 'lista' and f2 not in ('lista', 'kanban', 'calendario', 'carga', 'mais') and f3 == 'lista'
            and seq == ['kanban', 'calendario', 'carga', 'lista', 'carga', 'lista', 'carga', 'carga', 'carga'] and sem_ativar
            and e1[0] == 'kanban' and e1[1] == 'kanban' and 'view=kanban' in e1[2] and e2[0] == 'calendario' and e2[1] == 'calendario' and 'view=calendario' in e2[2]
            and fora_ not in ('lista', 'kanban', 'calendario', 'carga') and volta == 'calendario', [f1, f2, f3, seq, sem_ativar, e1, e2, fora_, volta])
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
        chk('C4 foco de teclado em "kanban" abre #g2-dica (role=tooltip) "Ver em kanban", sem aria-describedby repetido; Esc fecha e o foco fica; hover abre "Ver em carga por recurso"',
            d['vis'] and d['t'] == 'Ver em kanban' and d['role'] == 'tooltip' and 'g2-dica' not in db and not d2['vis'] and fo == 'kanban' and d3['vis'] and d3['t'] == 'Ver em carga por recurso', [d, db, d2, fo, d3])
    passo('C4', _c4)
    def _c4b():
        # C4b (revisão, achado B1): o clique do mouse não deixa a dica aberta (ela cobria "Nova ordem" e engolia o 1º clique); o teclado continua
        abre('OS.dc.html')
        neutro = J("(()=>{const h=document.querySelector('h1'); const r=h.getBoundingClientRect(); return [r.right+300, r.top+r.height/2];})()")
        c.mouse(neutro[0], neutro[1]); time.sleep(.3); res = {}
        for k in ('kanban', 'lista', 'calendario', 'carga'):
            mclique(centro(f"document.querySelector('[role=toolbar] [data-visao={k}]')")); c.mouse(neutro[0], neutro[1]); time.sleep(.7); res[k] = (ativa(), J(DICA)['vis'])
        nb = J("(()=>{const b=[...document.querySelectorAll('main button,header button')].find(b=>b.innerText.trim()==='Nova ordem'&&b.getClientRects().length); if(!b) return null; const r=b.getBoundingClientRect(); return [r.left+r.width/2, r.bottom-3];})()")
        form = False
        if nb:
            mclique(nb); time.sleep(.4); form = bool(J("!!document.getElementById('nv_jan')&&document.getElementById('nv_jan').getClientRects().length>0"))
            J("(()=>{const b=[...document.querySelectorAll('aside[role=dialog] button')].find(b=>b.innerText.trim()==='Cancelar'); b&&b.click();})()"); time.sleep(.4)
        ultimo_chip(); tecla('Tab'); dt = J(DICA); ft = foco()
        chk('C4b clique de mouse em cada ícone troca a visão e não deixa #g2-dica aberta com o ponteiro fora; o 1º clique em "Nova ordem" (onde a dica cobria) abre o formulário; Tab até a barra ainda abre a dica',
            all(v[0] == k and not v[1] for k, v in res.items()) and form and ft == 'carga' and dt['vis'] and dt['t'] == 'Ver em carga por recurso', [res, nb, form, ft, dt])
    passo('C4b', _c4b)
    def _c5():
        # C5 uma primária, 0 duplicata, nenhum arrastar, em cada visão
        res = {}
        for k in ('lista', 'kanban', 'calendario', 'carga'):
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
    def _c7():
        # C7 (revisão, achado B3): em cores forçadas (alto contraste) a visão ativa continua distinta das outras
        abre('OS.dc.html'); troca_visao(J, 'kanban')
        c.call('Emulation.setEmulatedMedia', {'features': [{'name': 'forced-colors', 'value': 'active'}]}); time.sleep(.5)
        fc = J("matchMedia('(forced-colors: active)').matches")
        st = J("(()=>{const g=k=>{const b=document.querySelector('[role=toolbar] [data-visao='+k+']'); const cs=getComputedStyle(b); return [cs.backgroundColor,cs.color,cs.forcedColorAdjust||''];}; return {ativo:g('kanban'), inativo:g('lista')};})()")
        shot('comp_1440_cores_forcadas')
        c.call('Emulation.setEmulatedMedia', {'features': [{'name': 'forced-colors', 'value': 'none'}]}); time.sleep(.3)
        claro = ('rgba(0, 0, 0, 0)', 'rgb(255, 255, 255)')
        chk('C7 cores forçadas (forced-colors: active): o ativo tem fundo e cor do sistema (Highlight), diferentes do fundo da página e dos inativos',
            fc and st['ativo'][0] not in claro and st['ativo'][0] != st['inativo'][0] and st['ativo'][1] != st['inativo'][1], [fc, st])
    passo('C7', _c7)

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
        # VISOES-2 (14/10): com 4 visões (Tabela, Kanban, Calendário, Carga) a barra mostra as 3 primeiras e o "mais" fica com a Carga
        chk('M2 390 px: Tabela, Kanban e Calendário na barra + "mais"; o menu mostra "Carga por recurso" em texto; Esc fecha e devolve o foco ao "mais"; ↓ no "mais" abre o menu; com a Carga escolhida o "mais" leva a marca e diz o nome',
            vis == ['lista', 'kanban', 'calendario', 'mais'] and menu == [['carga', 'Carga por recurso', 'false']] and fm == 'menu:carga' and fechado and fe == 'mais' and fd == 'menu:carga'
            and ativa() == 'carga' and carga_on() and mais.get('ativo') == 'true' and mais.get('lab') == 'Mais visões (atual: carga por recurso)' and mais.get('bg') == 'rgb(228, 243, 233)'
            and not pressed_vis and 'view=carga' in busca(), [vis, menu, fm, fechado, fe, fd, ativa(), mais, pressed_vis, busca()])
    passo('M2', _m2)
    def _m3():
        # M3 nada cortado em cada visão; primária única alcançável; 0 duplicata. VISOES-2: a Tabela sem agrupar e a Tabela agrupada por Talhão
        # (o "Agrupar por" e a trilha também cabem a 390 px) contam como dois estados da mesma visão; o Calendário entrou (4 visões).
        # Página nova: depois do teclado da M2, a troca por clique deixa o foco no botão com a dica de teclado aberta (C4), e a 390 px a dica de
        # "Ver em kanban" (o Kanban agora é o 2º botão) caía sobre "Nova ordem"; a medida aqui é a do layout de cada visão, não a da dica
        abre('OS.dc.html', 390, 844, True, 2)
        res = {}
        for k in ('lista', 'agrupada', 'kanban', 'calendario', 'carga'):
            troca_visao(J, k); m = J(MEDE); res[k] = (resumo(m), J(EST), dup()[0], ativa(), ag()); shot('cel_390_' + k)
        esperado = {'lista': ('lista', ''), 'agrupada': ('lista', 'Talhão')}
        chk('M3 390 px, em cada visão (Tabela, Tabela agrupada por Talhão, Kanban, Calendário, Carga): nada cortado, sem rolagem lateral, título e "Nova ordem" alcançáveis (MEDE/resumo vazio), uma primária e 0 duplicata',
            all(v[0] == [] and v[1] == ['Nova ordem'] and v[2] == 0 and (v[3], v[4] if k in esperado else None) == esperado.get(k, (k, None)) for k, v in res.items()), res)
    passo('M3', _m3)
    def _m3b():
        # M3b (VISOES-2, novo): a 390 px com toque, a antiga "Tabela agrupada" (um botão da barra, ≥ 44 px, M1) passou a ser o "Agrupar por" da
        # Tabela. O mesmo caminho tem de caber na tela: tocar em "Agrupar por" abre o menu com todos os itens dentro da janela e tocáveis
        # (elementFromPoint no próprio item); tocar em "Talhão" agrupa (?ag=onde). Página recém-aberta, sem rolar, como a pessoa chega
        abre('OS.dc.html', 390, 844, True, 2); troca_visao(J, 'lista')
        pb = J("(()=>{const b=[...document.querySelectorAll('[data-g2agb=g_os]')].find(b=>b.getClientRects().length); if(!b) return null; const r=b.getBoundingClientRect(); return [r.left+Math.min(r.width/2,40), r.top+r.height/2];})()")
        if pb and 0 < pb[1] < 844: c.toque(pb[0], pb[1]); time.sleep(.4)   # toque onde o botão está, sem rolar a página (clique() centraliza antes)
        its = J("[...document.querySelectorAll('[data-g2agm=g_os] [role=menuitemradio]')].map(i=>{const r=i.getBoundingClientRect(); const e=document.elementFromPoint(Math.min(r.left+20,innerWidth-2),r.top+r.height/2);"
                " return {t:i.innerText.split('\\n')[0].trim(), top:Math.round(r.top), bottom:Math.round(r.bottom), left:Math.round(r.left), right:Math.round(r.right), toca:!!e&&i.contains(e)};})") or []
        bt = J("(()=>{const b=document.querySelector('[data-g2agb=g_os]'); const r=b.getBoundingClientRect(); return [Math.round(r.top),Math.round(r.bottom),innerHeight,innerWidth];})()")
        shot('cel_390_agrupar_menu')
        tal = next((x for x in its if x['t'] == 'Talhão'), None)
        if tal and tal['toca']: c.toque(tal['left'] + 20, (tal['top'] + tal['bottom']) / 2); time.sleep(.6)
        else: tecla('Escape')
        chk('M3b 390 px com toque: "Agrupar por" abre o menu com os 5 itens dentro da janela (390 × 844) e tocáveis; tocar em "Talhão" agrupa (?ag=onde)',
            len(its) == 5 and all(x['toca'] and x['top'] >= 0 and x['bottom'] <= 844 and x['left'] >= 0 and x['right'] <= 390 for x in its) and ag() == 'Talhão' and 'ag=onde' in busca(),
            {'botão (top, bottom, janela h, w)': bt, 'itens': its, 'ag': ag(), 'busca': busca()})
    passo('M3b', _m3b)
    def _m4():
        # M4 toque longo: dica sem trocar a visão
        troca_visao(J, 'lista'); p = centro("document.querySelector('[role=toolbar] [data-visao=kanban]')")
        c.call('Input.dispatchTouchEvent', {'type': 'touchStart', 'touchPoints': [{'x': p[0], 'y': p[1]}]}); time.sleep(.65); d = J(DICA)
        c.call('Input.dispatchTouchEvent', {'type': 'touchEnd', 'touchPoints': []}); time.sleep(.5)
        chk('M4 toque longo (650 ms) no Kanban mostra a dica "Ver em kanban" e não troca a visão', d['vis'] and d['t'] == 'Ver em kanban' and ativa() == 'lista', [d, ativa()])
        guarda_erros('celular')
    passo('M4', _m4)
    def _m5():
        # M5 (revisão, achados B1/C5): toque curto troca a visão sem deixar a dica presa sobre os chips; o chip coberto responde ao 1º toque
        abre('OS.dc.html', 390, 844, True, 2)
        clique("document.querySelector('[role=toolbar] [data-visao=kanban]')"); time.sleep(.6); d1 = J(DICA); a1 = ativa()
        clique("[...document.querySelectorAll('[aria-label=\"Filtrar por fase\"] button')].find(b=>b.innerText.trim().startsWith('Canceladas'))"); time.sleep(.5); ch = chip_on()
        clique("document.querySelector('[role=toolbar] [data-visao-mais]')"); time.sleep(.4)
        clique("document.querySelector('[role=menu][data-visoes-menu] [data-visao-menu=carga]')"); time.sleep(1.2); d2 = J(DICA); a2 = ativa()
        chk('M5 390 com toque: toque curto no Kanban troca a visão sem dica aberta; o chip "Canceladas" responde ao 1º toque; escolher a Carga pelo "mais" não deixa dica',
            a1 == 'kanban' and not d1['vis'] and ch == ['Canceladas'] and not d2['vis'], [a1, d1, ch, a2, d2])
    passo('M5', _m5)
    def _m6():
        # M6 (revisão, achados A6/B2): a parada de Tab lembrada pelas setas não fica num botão oculto depois de mudar a largura ou girar
        abre('OS.dc.html'); foca('lista'); tecla('End'); J("document.activeElement.blur()"); time.sleep(.3)
        janela(390, 844, False, 1); time.sleep(.6); t1 = paradas(); ultimo_chip(); tecla('Tab'); f1 = foco()
        abre('OS.dc.html', 390, 844, False, 1); foca('lista'); tecla('End'); J("document.activeElement.blur()"); time.sleep(.3)
        janela(1440, 900, False, 1); time.sleep(.6); t2 = paradas(); ultimo_chip(); tecla('Tab'); f2 = foco()
        abre('OS.dc.html', 390, 844, True, 2); foca('lista'); tecla('End'); J("document.activeElement.blur()"); time.sleep(.3)
        c.aparelho(844, 390, 2, True); time.sleep(.6); t3 = paradas(); c.aparelho(390, 844, 2, True)
        chk('M6 1440 → End (Carga) → sai → 390; 390 → End ("mais") → sai → 1440; celular em retrato → End → paisagem: sempre uma parada de Tab visível na barra e o Tab entra nela',
            len(t1) == 1 and f1 == t1[0] and len(t2) == 1 and f2 == t2[0] and len(t3) == 1, [t1, f1, t2, f2, t3])
    passo('M6', _m6)
    def _m7():
        # M7 (revisão, achado B5): o menu do "mais" aberto a 390 px não fica solto quando a janela passa de 640 px
        abre('OS.dc.html', 390, 844, False, 1); clique("document.querySelector('[role=toolbar] [data-visao-mais]')"); time.sleep(.4)
        ab = J("(()=>{const m=document.querySelector('[role=menu][data-visoes-menu]'); return !!m&&m.getClientRects().length>0;})()")
        janela(1440, 900, False, 1); time.sleep(.6)
        vis = J("(()=>{const m=document.querySelector('[role=menu][data-visoes-menu]'); return !!m&&m.getClientRects().length>0;})()")
        x = J("(document.querySelector('[role=toolbar] [data-visao-mais]')||{getAttribute:()=>''}).getAttribute('aria-expanded')")
        chk('M7 menu do "mais" aberto a 390 px: ao alargar para 1440 px ele some e o "mais" fica fechado (aria-expanded=false)', ab and not vis and x == 'false', [ab, vis, x])
    passo('M7', _m7)
    def _m8():
        # M8 (revisão, achado B6): Kanban a 390 px com colunas legíveis (≥ 140 px) e o quadro rolando na horizontal, sem rolagem lateral da página
        abre('OS.dc.html', 390, 844, True, 2); troca_visao(J, 'kanban'); time.sleep(.4)
        m = J("(()=>{const l=document.querySelector('[aria-label=\"Kanban das ordens\"]'); if(!l) return null; const cs=[...l.querySelectorAll(':scope>sc-for>div,:scope>div')].filter(x=>x.getClientRects().length);"
              " const tit=cs.map(c=>{const t=c.querySelector('span'); if(!t) return false; const a=t.getBoundingClientRect(), b=c.getBoundingClientRect(); return a.right<=b.right+1;});"
              " return {larg:cs.map(c=>Math.round(c.getBoundingClientRect().width)), rola:l.scrollWidth>l.clientWidth+4, ov:getComputedStyle(l).overflowX, pag:document.documentElement.scrollWidth<=innerWidth+1, tit};})()")
        shot('cel_390_kanban_rola')
        chk('M8 Kanban a 390 px: 5 colunas com 140 px ou mais, títulos sem corte, o quadro rola na horizontal e a página não', bool(m) and len(m['larg']) == 5 and min(m['larg']) >= 140 and m['rola'] and m['pag'] and all(m['tit']), m)
    passo('M8', _m8)

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
    """Fazenda Todas, Safra 2026/27, fase Em execução, Tabela agrupada por Talhão (VISOES-2: Tabela + "Agrupar por" Talhão); rola a lista; abre a OS-0421
    no painel (só ela e a OS-0420 têm página de detalhe)."""
    abre('OS.dc.html', w, h, toque, 2 if toque else 1)
    setsel('Filtrar por fazenda', 'Todas'); setsel('Filtrar por safra', '2026/27'); fase('Em execução'); troca_visao(J, 'agrupada')
    J("(()=>{const m=document.querySelector('main[data-scroll]'); const col=document.querySelector('.ml-tog+div'); const r=[...document.querySelectorAll('main .g2rola')].find(x=>x.getClientRects().length); if(r) r.scrollTop=Math.min(60,r.scrollHeight); if(m) m.scrollTop=Math.min(90,m.scrollHeight); if(col) col.scrollTop=Math.min(40,col.scrollHeight);})()")
    time.sleep(.3); r0 = rolagem()
    J(f"(()=>{{const r={LINHA('OS-0421')}; r&&r.focus({{preventScroll:true}}); return !!r;}})()"); tecla('Enter'); time.sleep(.6)
    ok = painel().startswith('OS-0421'); PREP.setdefault(w, []).append(ok)
    if not ok:
        # VISOES-2: Enter na O.S. da Tabela agrupada não abriu o painel (conferido à parte, chk "E3 … Enter na OS-0421"). Para seguir conferindo a
        # volta do detalhe, o painel abre pela entrada por endereço (#OS-0421, a mesma da E6), sem nova entrada no histórico
        J("location.replace(location.pathname+location.search+'#OS-0421'); 1"); time.sleep(.9)
    return r0
PREP = {}   # largura → o Enter na OS-0421 da Tabela agrupada abriu o painel? (uma entrada por prepara_e3)
def confere_volta(tag, r0, extra=None):
    time.sleep(.6)
    st = {'ativa': ativa(), 'ag': ag(), 'faz': sel('Filtrar por fazenda'), 'saf': sel('Filtrar por safra'), 'chip': chip_on(), 'rol': rolagem(), 'r0': r0, 'foco': foco(), 'painel': painel(),
          'busca': busca(), 'grupos': grupos()[:4]}
    if extra: st.update(extra)
    time.sleep(2.2); st['foco_2s'] = foco(); st['painel_2s'] = painel()   # revisão, achado A4: o redesenho do runtime ~2 s depois não toma o foco
    ok_f = lambda f, pa: f.startswith('linha:OS-0421') or pa.startswith('OS-0421')
    chk(f'E3 {tag}: volta à Tabela agrupada por Talhão com Fazenda Todas, Safra 2026/27, fase Em execução, rolagem ±4 px e o foco na OS-0421 (ou o painel dela, se a página voltou da memória), também 2 s depois',
        st['ativa'] == 'lista' and st['ag'] == 'Talhão' and len(st['grupos']) > 0 and st['faz'] == 'Todas' and st['saf'] == '2026/27' and st['chip'] == ['Em execução'] and abs(st['rol'] - r0) <= 4
        and ok_f(st['foco'], st['painel']) and ok_f(st['foco_2s'], st['painel_2s']), st)
    return st
ABRE_COMPLETA = "(()=>{const a=[...document.querySelectorAll('aside[role=dialog] a')].find(a=>/Abrir ordem completa/.test(a.innerText)); a&&a.click(); return !!a;})()"
def canonica():
    return {'url': J("location.pathname.split('/').pop()+location.search"), 'ativa': ativa(), 'ag': ag(), 'chip': chip_on(), 'faz': sel('Filtrar por fazenda'), 'saf': sel('Filtrar por safra'),
            'foco': foco(), 'linhas': len(ids())}

def agrupar_teclado(rot='Talhão'):
    """VISOES-2: só teclado, da barra de visões até o agrupamento: Home + Enter (Tabela), Tab até o "Agrupar por", Enter abre o menu (foco no item
    marcado), Tab até o item rot e Enter. Devolve onde o foco ficou depois de escolher."""
    foca(ativa()); tecla('Home'); tecla('Enter'); time.sleep(.4)
    for _ in range(12):
        if J("!!(document.activeElement&&document.activeElement.hasAttribute('data-g2agb'))"): break
        tecla('Tab')
    tecla('Enter'); time.sleep(.4)
    for _ in range(8):
        if J(f"(document.activeElement&&document.activeElement.getAttribute('role')==='menuitemradio'&&(document.activeElement.innerText||'').trim().split('\\n')[0].trim()==={json.dumps(rot)})"): break
        tecla('Tab')
    tecla('Enter'); time.sleep(.6)
    return J("(()=>{const a=document.activeElement; return a?(a.getAttribute('data-g2agb')?'agrupar:'+a.getAttribute('data-g2agb'):a.tagName):'';})()")

def modo_e2e():
    for (w, h, toque, tag) in ((1440, 900, False, '1440'), (390, 844, True, '390')):
        def _e12():
            # E1 · filtro → Tabela agrupada por Talhão, por clique e por teclado; hash intacto. VISOES-2 (14/10): a "agrupada" é a Tabela + "Agrupar
            # por" Talhão: no endereço ?ag=onde, junto com o ?view=lista da visão escolhida; o grupo leva o nome do talhão (grp@T1; a Fazenda, com
            # um valor só no recorte, desce sozinha). Entre as rodadas, "Sem agrupar" e o Kanban: o teclado escolhe a Tabela e o agrupamento de novo
            abre('OS.dc.html#tal=Santa Rita|T1', w, h, toque, 2 if toque else 1); time.sleep(.4)
            fase('Em execução'); l0 = sorted(x.split('@')[0] for x in ids()); t0 = tal_faixa()
            rodadas = []
            for como in ('clique', 'teclado'):
                fo = troca_visao(J, 'agrupada') if como == 'clique' else agrupar_teclado('Talhão')
                kids = sorted({x.split('@')[0] for x in ids() if not x.startswith('grp@')}); gt = total_nota()
                rodadas.append({'como': como, 'ativa': ativa(), 'ag': ag(), 'chip': chip_on(), 'tal': tal_faixa(), 'grupos': grupos(), 'kids': kids, 'tot': gt, 'busca': busca(), 'hash': hashd(), 'foco': fo})
                if como == 'clique': agrupar_por(J, 'Sem agrupar'); troca_visao(J, 'kanban')
            ok1 = all(r['ativa'] == 'lista' and r['ag'] == 'Talhão' and r['chip'] == ['Em execução'] and r['tal'] == t0 and r['grupos'] == ['T1'] and r['kids'] == l0
                      and r['tot'].startswith(f'{len(l0)} O.S. ·') and params(r['busca']) == AG_ONDE and r['hash'] == '#tal=Santa Rita|T1' for r in rodadas)
            chk(f'E1 {tag}: talhão T1 (pelo endereço) + fase Em execução → Tabela + Agrupar por Talhão por clique e por teclado: os mesmos chips, talhão e linhas, só o grupo T1 (o do filtro), total só do recorte, ?view=lista&ag=onde e o hash intacto',
                ok1 and len(l0) >= 1 and t0 == 'T1' and rodadas[1]['foco'] == 'agrupar:g_os', [l0, t0, rodadas])
            shot(f'e2e_{tag}_agrupada')
            # E2 · abrir a O.S. do grupo → painel → Esc → foco volta à linha
            alvo = l0[0]
            clique(LINHA(alvo)); pa = painel(); tecla('Tab'); dentro = J("!!(document.activeElement&&document.activeElement.closest('aside[role=dialog]'))"); tecla('Escape'); time.sleep(.5)
            chk(f'E2 {tag}: abrir {alvo} dentro do grupo abre o painel dela (Tab entra no painel); Esc fecha e o foco volta à linha', pa.startswith(alvo) and dentro and painel() == '' and foco().startswith('linha:' + alvo), [pa, dentro, painel(), foco()])
            guarda_erros(f'E1-E2 {tag}')
        passo(f'E1–E2 {tag}', _e12)
        def _e3():
            # E3 · volta do detalhe pela regra 02 (DESENHO §2.11; VISOES-REV-20261010-02/03): o link "Voltar" e a trilha SEMPRE navegam ao destino
            # canônico (nova entrada, ?view=lista&ag=onde; a ficha ?volta sai do endereço), nunca pelo histórico; o Voltar nativo do navegador restaura.
            # VISOES-2: a visão é a Tabela e o agrupamento (?ag=onde) vem junto no endereço do destino canônico
            for como in ('link Voltar', 'trilha', 'Voltar nativo'):
                r0 = prepara_e3(w, h, toque); pa = painel()
                J(ABRE_COMPLETA); espera_pag('CA-01det.dc.html'); h0 = J("history.length")
                if como == 'link Voltar': J("document.querySelector('a[aria-label=Voltar]').click()")
                elif como == 'trilha': J("(()=>{const a=[...document.querySelectorAll('header a[href]')].find(a=>a.getAttribute('aria-label')!=='Voltar'&&/OS\\.dc\\.html$/.test(a.getAttribute('href'))); a&&a.click();})()")
                else: J("history.back()")
                espera_pag('OS.dc.html'); h1 = J("history.length"); nt = nav_tipo()
                st = confere_volta(f'{tag} · {como} (mesma aba)', r0, {'painel_antes': pa, 'hist': [h0, h1], 'nav': nt})
                if como != 'Voltar nativo':
                    chk(f'E3 {tag} · {como}: navegação nova ao destino canônico (history.length {h0} → {h0 + 1}, tipo navigate), nunca o voltar do histórico; endereço OS.dc.html?view=lista&ag=onde sem a ficha',
                        h1 == h0 + 1 and nt == 'navigate' and params(st['busca']) == AG_ONDE, [h0, h1, nt, st['busca']])
                if tag == '1440' and como == 'link Voltar': shot('e2e_1440_volta_detalhe')
        passo(f'E3 {tag} mesma aba', _e3)
        def _e3n():
            # nova aba COM opener (o sessionStorage vem copiado): o "Voltar" vai ao destino canônico e o contexto válido restaura visão, filtros e foco
            r0 = prepara_e3(w, h, toque)
            J("(()=>{const a=[...document.querySelectorAll('aside[role=dialog] a')].find(a=>/Abrir ordem completa/.test(a.innerText)); a.dispatchEvent(new MouseEvent('auxclick',{bubbles:true,button:1}));})()")
            antes = {x['id'] for x in alvos()}
            c.call('Runtime.evaluate', {'expression': "window.open('CA-01det.dc.html','_blank'); 1", 'userGesture': True}); time.sleep(1.5)
            novo = [x for x in alvos() if x['id'] not in antes and x.get('type') == 'page']
            if novo:
                a = Aba(novo[0]); a.espera('CA-01det.dc.html')
                if toque: a.call('Emulation.setDeviceMetricsOverride', {'width': w, 'height': h, 'deviceScaleFactor': 2, 'mobile': True})
                a.js("document.querySelector('a[aria-label=Voltar]').click()"); a.espera('OS.dc.html'); time.sleep(.8)
                q = lambda: a.js("(document.activeElement&&document.activeElement.getAttribute('data-rid'))||''")
                st = {'url': a.js("location.pathname.split('/').pop()+location.search"), 'ativa': a.js("(document.querySelector('[role=toolbar] [data-visao][aria-pressed=true]')||{getAttribute:()=>''}).getAttribute('data-visao')"), 'ag': agrupado_por(a.js),
                      'faz': a.js("document.querySelector('select[aria-label=\"Filtrar por fazenda\"]').value"), 'saf': a.js("document.querySelector('select[aria-label=\"Filtrar por safra\"]').value"),
                      'chip': a.js("[...document.querySelectorAll('[aria-label=\"Filtrar por fase\"] [aria-pressed=true]')].map(b=>b.innerText.replace(/\\s+\\d+$/,'').trim())"), 'foco': q()}
                time.sleep(2.2); st['foco_2s'] = q()
                a.fecha(); c.call('Page.bringToFront')
                u0, _, u1 = st['url'].partition('?')
                chk(f'E3 {tag} · nova aba COM opener: o "Voltar" vai a OS.dc.html?view=lista&ag=onde (sem a ficha), na Tabela agrupada por Talhão, com Fazenda, Safra, fase e o foco na OS-0421, também 2 s depois',
                    u0 == 'OS.dc.html' and params(u1) == AG_ONDE and st['ativa'] == 'lista' and st['ag'] == 'Talhão' and st['faz'] == 'Todas' and st['saf'] == '2026/27' and st['chip'] == ['Em execução']
                    and str(st['foco']).startswith('OS-0421') and str(st['foco_2s']).startswith('OS-0421'), st)
            else: chk(f'E3 {tag} · nova aba COM opener', False, 'o Chrome não abriu a aba (window.open)')
        passo(f'E3 {tag} nova aba', _e3n)
        def _e3d():
            # nova aba SEM opener (link direto, sessão vazia): sem contexto, o link segue como está (OS.dc.html; a entrada usa a preferência)
            t = json.load(urllib.request.urlopen(urllib.request.Request(f'http://127.0.0.1:{porta}/json/new?{BASE}CA-01det.dc.html', method='PUT'), timeout=30))
            a = Aba(t); a.espera('CA-01det.dc.html'); href0 = a.js("document.querySelector('a[aria-label=Voltar]').getAttribute('href')")
            a.js("document.querySelector('a[aria-label=Voltar]').click()"); a.espera('OS.dc.html')
            dl = {'href0': href0, 'url': a.js("location.pathname.split('/').pop()+location.search"), 'hist': a.js("history.length")}
            a.fecha(); c.call('Page.bringToFront')
            chk(f'E3 {tag} · nova aba SEM opener (detalhe aberto direto, sem contexto): o "Voltar" segue o link (OS.dc.html, sem ?view e sem o voltar do histórico)', dl['href0'] == 'OS.dc.html' and dl['url'] == 'OS.dc.html' and dl['hist'] == 2, dl)
            guarda_erros(f'E3 {tag}')
        passo(f'E3 {tag} deep-link', _e3d)
        def _e3e():
            # link direto ao detalhe na mesma aba: o contexto desta aba (recente, mesmo perfil e escopo, não usado) vale
            r0 = prepara_e3(w, h, toque)
            J("(()=>{const a=[...document.querySelectorAll('aside[role=dialog] a')].find(a=>/Abrir ordem completa/.test(a.innerText)); a.addEventListener('click',e=>e.preventDefault(),{once:true}); a.click();})()"); time.sleep(.3)
            vai('CA-01det.dc.html'); J("document.querySelector('a[aria-label=Voltar]').click()"); espera_pag('OS.dc.html')
            confere_volta(f'{tag} · link direto ao detalhe na mesma aba (contexto válido desta aba)', r0)
        passo(f'E3 {tag} link direto', _e3e)
        def _e3f():
            # contexto recusado (regra 02): antigo (2 h), de outro perfil, de outro escopo (Safra da sessão mudou) e já usado → lista canônica
            # funcional, sem a visão, os filtros nem o foco antigos (revisão, achados A3/C2). VISOES-2: o agrupamento antigo (?ag=onde) também não volta pelo
            # endereço; a entrada usa a preferência do perfil (Ana: Tabela + Talhão, guardados na prepara_e3; Caio, sem preferência: Tabela sem agrupar)
            res = {}
            for caso in ('antigo', 'perfil', 'safra', 'usado'):
                prepara_e3(w, h, toque); J(ABRE_COMPLETA); espera_pag('CA-01det.dc.html')
                if caso == 'antigo': J("(()=>{const c=JSON.parse(sessionStorage.getItem('g2volta')); c.t-=2*3600*1000; sessionStorage.setItem('g2volta',JSON.stringify(c)); return 1;})()")
                if caso == 'perfil': setsel('Trocar perfil de demonstração', 'Caio')
                if caso == 'safra': J("(()=>{const k='g2:OS.dc.html:g_os'; const o=JSON.parse(sessionStorage.getItem(k)||'{}'); o.mf_saf='2025/26'; sessionStorage.setItem(k,JSON.stringify(o)); return 1;})()")
                if caso == 'usado': J("document.querySelector('a[aria-label=Voltar]').click()"); espera_pag('OS.dc.html'); vai('CA-01det.dc.html')
                J("document.querySelector('a[aria-label=Voltar]').click()"); espera_pag('OS.dc.html'); time.sleep(2.2)
                res[caso] = canonica()
                if caso == 'perfil': setsel('Trocar perfil de demonstração', 'Ana')
            sem = lambda r: r['url'] == 'OS.dc.html' and not str(r['foco']).startswith('linha:OS-0421') and r['linhas'] > 0
            chk(f'E3 {tag} · contexto antigo (2 h), de outro perfil (Caio), de outro escopo (Safra 2025/26 na sessão) e já usado: lista canônica (OS.dc.html, sem ?view, ?ag nem ficha), funcional e sem o foco antigo; '
                'filtros limpos nos recusados (antigo e safra: preferência da Ana = Tabela + Agrupar por Talhão; Caio sem preferência: Tabela sem agrupar; safra: 2025/26)',
                all(sem(r) for r in res.values()) and res['antigo']['chip'] == ['Todas'] and (res['antigo']['ativa'], res['antigo']['ag']) == ('lista', 'Talhão')
                and (res['safra']['ativa'], res['safra']['ag']) == ('lista', 'Talhão')
                and (res['perfil']['ativa'], res['perfil']['ag']) == ('lista', '') and res['perfil']['chip'] == ['Todas'] and res['safra']['chip'] == ['Todas'] and res['safra']['saf'] == '2025/26', res)
        passo(f'E3 {tag} recusado', _e3f)
        def _e3p():
            # VISOES-2: na Tabela agrupada, Enter na linha da O.S. abre o painel dela (como na Tabela sem agrupar), em cada preparação da E3
            chk(f'E3 {tag} · Enter na OS-0421 da Tabela agrupada por Talhão abre o painel dela (em todas as preparações da E3)', bool(PREP.get(w)) and all(PREP[w]), PREP.get(w))
        passo(f'E3 {tag} Enter na agrupada', _e3p)
    # ---------------- 1440 daqui em diante ----------------
    def _e5():
        # E5 · trocar de visão não grava no cenário (antes da E3b, que cancela uma ordem para montar o caso). VISOES-2: a "agrupada" é a Tabela + o
        # "Agrupar por" Talhão, que guarda a escolha por perfil (g2ag:…, preferência como a da visão, safrion.pref.); nenhuma outra chave muda
        abre('OS.dc.html')
        NEG = "JSON.stringify(Object.keys(localStorage).filter(k=>k.indexOf('safrion.pref.')!==0&&k.indexOf('g2ag:')!==0).sort().map(k=>[k,localStorage.getItem(k)]))"
        c0 = J("localStorage.getItem('talhao-os-cenario-v1')"); n0 = J(NEG); hl0 = J("history.length")
        for k in ('agrupada', 'kanban', 'carga', 'lista', 'kanban', 'agrupada'): troca_visao(J, k)
        foca(ativa()); tecla('End'); tecla('Enter'); tecla('Home'); tecla(' ')
        chk('E5 trocar de visão e agrupar (clique e teclado, 8 trocas, 2 delas com o "Agrupar por" Talhão) não muda o cenário talhao-os-cenario-v1 nem outra chave de negócio, byte a byte; só as preferências (safrion.pref. e o agrupamento g2ag: da Ana = Talhão)',
            J("localStorage.getItem('talhao-os-cenario-v1')") == c0 and J(NEG) == n0 and bool(pref()) and json.loads(gpref() or 'null') == {'d': 'onde', 't': []}, [c0 is None, len(n0 or ''), J(NEG) == n0, pref(), gpref()])
        # revisão, achado A7: trocar de visão não cria entrada no histórico (replaceState, nunca pushState); o Voltar do navegador sai da O.S.
        hl1 = J("history.length"); J("history.back()"); time.sleep(1.5)
        saiu = J("location.pathname.split('/').pop()")
        chk('E5b 8 trocas de visão (com o "Agrupar por") não mudam history.length e o Voltar do navegador sai da O.S. (para a tela anterior, Main)', hl1 == hl0 and saiu == 'Main.dc.html', [hl0, hl1, saiu])
    passo('E5', _e5)
    def _e3b():
        # E3b · vazio por regra da visão: Canceladas no Kanban
        abre('OS.dc.html')
        r = J("(()=>{ const r=window.__cen.cenMudar(null,c=>window.__cen.osc_cancelar(c,'OS-0424','teste VISOES-1',['','',''],{k:'Ana'})); window.dispatchEvent(new StorageEvent('storage',{key:'talhao-os-cenario-v1'})); return JSON.stringify(r); })()"); time.sleep(.5)
        fase('Canceladas'); nl = len(ids()); troca_visao(J, 'kanban'); es = estado(); cols = kb_cols(); pk = pref(); shot('e2e_1440_kanban_canceladas')
        J("(()=>{const b=[...document.querySelectorAll('[data-visoes-estado] button')].find(b=>b.innerText.trim()==='Ver em tabela'); b&&b.click();})()"); time.sleep(.6)
        a1 = (ativa(), busca(), pref(), len(ids()))
        c.goto(J("location.href"), .6); pronto(); a2 = (ativa(), busca())
        vai('OS.dc.html'); a3 = ativa()
        chk('E3b fase Canceladas → Kanban: "Canceladas ficam fora do quadro: 1 ordem no filtro." com "Ver em tabela" (o quadro segue com 5 colunas); "Ver em tabela" abre a Lista com ?view=lista sem mudar a preferência; F5 continua na Lista; nova entrada sem ?view abre o Kanban (preferência)',
            nl == 1 and es and es['tipo'] == 'regra' and es['t'] == 'Canceladas ficam fora do quadro: 1 ordem no filtro. Ver em tabela' and cols == 5 and pk == 'kanban'
            and a1[0] == 'lista' and 'view=lista' in a1[1] and a1[2] == 'kanban' and a1[3] == 1 and a2 == ('lista', a1[1]) and a3 == 'kanban', [r, nl, es, cols, pk, a1, a2, a3])
    passo('E3b', _e3b)
    def _e3c():
        # E3c · erro da visão (Kanban, Carga): o estado diz o motivo e "Ver em tabela" leva à Lista, que funciona; cenário ilegível: recuperação sem apagar
        for k, nome in (('kanban', 'Kanban'), ('carga', 'Carga por recurso')):
            abre('OS.dc.html?view=lista'); J(f"window.__g2visaoFalha={json.dumps(k)}"); p0 = pref(); troca_visao(J, k); es = estado(); sem = (kb_cols() == -1) if k == 'kanban' else (not carga_on())
            shot(f'e2e_1440_erro_{k}')
            J("(()=>{const b=[...document.querySelectorAll('[data-visoes-estado] button')].find(b=>b.innerText.trim()==='Ver em tabela'); b&&b.click();})()"); time.sleep(.6)
            chk(f'E3c erro ao montar a visão {nome}: "Não foi possível mostrar a visão {nome}: …" + "Ver em tabela" (painel não aparece); a Lista abre e funciona (linhas, ?view=lista), sem gravar preferência no fallback',
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
        # VISOES-2: o Caio escolhe a Tabela agrupada por Talhão (Tabela + "Agrupar por"): a preferência de visão dele vira a Tabela e o agrupamento fica
        # guardado só no perfil dele (g2ag:…:Caio); a Ana segue sem agrupamento guardado
        vai('OS.dc.html'); p6 = ativa(); troca_visao(J, 'agrupada'); setsel('Trocar perfil de demonstração', 'Ana'); p7 = (ativa(), ag()); vai('OS.dc.html')
        p8 = (ativa(), pref('Ana'), pref('Caio'), gpref('Ana'), json.loads(gpref('Caio') or 'null'))
        J("localStorage.clear(); 1"); vai('OS.dc.html'); p9 = (ativa(), ag())
        chk('E4 sem ?view abre a preferência (Kanban); ?view=lista vence a preferência e não a grava; ?view=xyz abre a preferência com aviso sem o valor e o endereço perde o valor (F5 sem aviso)',
            p1 == ('kanban', '') and p2 == ('lista', 'kanban') and p3[0] == 'kanban' and 'não existe nesta lista: aberta em Kanban (sua última escolha)' in p3[1] and 'xyz' not in p3[1]
            and 'view' not in p3[2] and p3b[0] == 'kanban' and 'não existe' not in p3b[1], [p1, p2, p3, p3b])
        chk('E4b (Codex, item 1) preferência Kanban → escolher Lista grava ?view=lista → F5 continua na Lista (e a Lista vira a preferência)', p4 == ('?view=lista', 'lista', 'lista'), p4)
        chk('E4c (Codex, item 3) trocar o perfil não muda a visão aberta nem o agrupamento; a próxima entrada sem ?view usa a preferência do perfil (Caio sem preferência: Tabela; Ana: Kanban; Caio depois de agrupar: Tabela + Talhão, só no perfil dele); localStorage limpo abre a Tabela sem agrupar',
            p5 == 'kanban' and p6 == 'lista' and p7 == ('lista', 'Talhão') and p8 == ('kanban', 'kanban', 'lista', None, {'d': 'onde', 't': []}) and p9 == ('lista', ''), [p5, p6, p7, p8, p9])
    passo('E4', _e4)
    def _e6():
        # E6 · entrada por endereço
        abre('OS.dc.html?view=kanban#OS-0418'); time.sleep(.5); q1 = (ativa(), painel(), hashd())
        vai('OS.dc.html#OS-0430:ajustar'); time.sleep(.6); q2 = (ativa(), painel(), J("!!document.querySelector('aside[role=dialog] input')"))
        # VISOES-2: o endereço antigo ?view=agrupada (compatibilidade) e o novo ?ag=onde abrem a Tabela agrupada por Talhão, com o filtro T1 e só o grupo T1
        vai('OS.dc.html?theme=dark&view=agrupada#tal=Santa Rita|T1'); time.sleep(.6); q3 = (ativa(), tal_faixa(), busca(), hashd(), grupos(), ag())
        vai('Main.dc.html'); vai('OS.dc.html?theme=dark&ag=onde#tal=Santa Rita|T1'); time.sleep(.6); q4 = (ativa(), tal_faixa(), busca(), hashd(), grupos(), ag())
        chk('E6 OS.dc.html?view=kanban#OS-0418 abre o Kanban e a OS-0418; #OS-0430:ajustar abre a ordem para ajustar; ?theme=dark&view=agrupada#tal=Santa Rita|T1 (endereço antigo) e ?theme=dark&ag=onde#tal=Santa Rita|T1 abrem a Tabela agrupada por Talhão com T1 (só o grupo T1), theme e hash intactos',
            q1[0] == 'kanban' and q1[1].startswith('OS-0418') and q1[2] == '#OS-0418' and q2[1].startswith('OS-0430') and q2[2]
            and all(q[0] == 'lista' and q[5] == 'Talhão' and q[1] == 'T1' and 'theme=dark' in q[2] and q[3] == '#tal=Santa Rita|T1' and q[4] == ['T1'] for q in (q3, q4))
            and ('view=agrupada' in q3[2] or 'ag=onde' in q3[2]) and 'ag=onde' in q4[2], [q1, q2, q3, q4])
        guarda_erros('E4-E6')
    passo('E6', _e6)
    def _e6b():
        # E6b (revisão, achado A1): entrada por endereço vinda de outra tela depois de a sessão guardar a Safra 2025/26: a ordem pedida
        # aparece na lista atrás do painel e o talhão pedido mostra as ordens dele (a Safra vai para a da ordem ou para Todas, com aviso)
        res = {}
        for hsh in ('#OS-0421', '#tal=Lagoa Grande|PV12', '#OS-0505'):
            abre('OS.dc.html'); setsel('Filtrar por safra', '2025/26'); vai('Main.dc.html'); vai('OS.dc.html' + hsh); time.sleep(.8)
            res[hsh] = {'saf': sel('Filtrar por safra'), 'faz': sel('Filtrar por fazenda'), 'painel': painel()[:8], 'linhas': [x.split('@')[0] for x in ids()], 'toast': toast()[:80]}
        r1, r2, r3 = res['#OS-0421'], res['#tal=Lagoa Grande|PV12'], res['#OS-0505']
        chk('E6b Safra 2025/26 guardada na sessão + entrada #OS-0421, #tal=Lagoa Grande|PV12 e #OS-0505: a ordem pedida está na lista atrás do painel; o PV12 mostra OS-0502 e OS-0509; a Safra muda com aviso',
            r1['painel'].startswith('OS-0421') and 'OS-0421' in r1['linhas'] and r1['saf'] != '2025/26' and 'Safra' in r1['toast']
            and {'OS-0502', 'OS-0509'} <= set(r2['linhas']) and r2['saf'] == 'Todas'
            and r3['painel'].startswith('OS-0505') and 'OS-0505' in r3['linhas'] and r3['faz'] == 'Lagoa Grande', res)
        guarda_erros('E6b')
    passo('E6b', _e6b)
    def abre_todas(f):
        """abre f (1440) com todas as colunas da grade da O.S.: a Área (ha), somada no grupo, não está no padrão "Abre com" (VISOES-2 §3.6)"""
        abre('OS.dc.html'); J(cv_todas_js('g_os')); vai('Main.dc.html'); vai(f)
    def _e1b():
        # E1b (revisão, achado C1, S2): o grupo da Tabela agrupada conta só as O.S. do recorte; sem sobreposição, a soma dos grupos = Total.
        # VISOES-2: com Fazenda Todas o 1º nível do Agrupar por Talhão é a Fazenda (Fazenda › Talhão): a soma dos grupos de fazenda = Total; descer
        # numa fazenda (o nome do grupo vira filtro, com a trilha) mostra os talhões dela, cuja soma = o subtotal da fazenda = o Total da tela
        abre_todas('OS.dc.html#tal=Santa Rita|T2'); time.sleep(.4); fase('A liberar'); troca_visao(J, 'agrupada'); time.sleep(.5)
        g1 = J(GRUPOS_AREA) or []; t1 = total_nota()
        abre_todas('OS.dc.html'); setsel('Filtrar por fazenda', 'Todas'); fase('A liberar'); troca_visao(J, 'agrupada'); time.sleep(.5)
        g2 = J(GRUPOS_AREA) or []; t2 = total_nota(); shot('e2e_1440_agrupada_aliberar_todas')
        a1 = num_br((t1.split('·') + ['', ''])[1]); a2 = num_br((t2.split('·') + ['', ''])[1]); s2 = round(sum(num_br(x) or 0 for _, x in g2), 2)
        chk('E1b fase A liberar + talhão T2 → Tabela agrupada por Talhão: o grupo T2 soma só a OS-0431 (= Total, 102 ha); A liberar + Fazenda Todas: grupos por fazenda e a soma dos grupos = Total (490,95 ha)',
            len(g1) == 1 and g1[0][0] == 'T2' and a1 is not None and abs((num_br(g1[0][1]) or -1) - a1) < .01 and abs(a1 - 102) < .01
            and len(g2) >= 2 and a2 is not None and abs(s2 - a2) < .01 and abs(a2 - 490.95) < .01, [g1, t1, g2, s2, t2])
        sr = num_br(dict(g2).get('Santa Rita', ''))
        J("(()=>{const b=[...document.querySelectorAll('[data-g2g=g_os] .g2desce')].find(b=>b.getClientRects().length&&b.innerText.trim()==='Santa Rita ›'); b&&b.click();})()"); time.sleep(.6)
        g3 = J(GRUPOS_AREA) or []; t3 = total_nota(); tr = J("(document.querySelector('[data-g2agtr=g_os]')||{innerText:''}).innerText.replace(/\\s+/g,' ').trim()") or ''
        cont = J("(()=>{const s=[...document.querySelectorAll('[data-g2g=g_os] span, main span')].find(s=>s.getClientRects().length&&/^\\d+ de \\d+$/.test(s.innerText.trim())); return s?s.innerText.trim():'';})()") or ''
        a3 = num_br((t3.split('·') + ['', ''])[1]); s3 = round(sum(num_br(x) or 0 for _, x in g3), 2); n3 = len({x.split('@')[0] for x in ids() if not x.startswith('grp@')})
        shot('e2e_1440_agrupada_aliberar_desce_santarita')
        chk('E1b descer em Santa Rita (A liberar, Fazenda Todas): trilha "Todas › Santa Rita", grupos por talhão cuja soma = subtotal de Santa Rita no nível de cima; o Total da tela (O.S. e ha) e o contador da grade seguem o recorte da trilha',
            tr.startswith('Todas › Santa Rita') and len(g3) >= 1 and sr is not None and abs(s3 - sr) < .01
            and a3 is not None and abs(a3 - s3) < .01 and t3.startswith(f'{n3} O.S. ·') and cont.startswith(f'{n3} de '), [sr, g3, s3, t3, tr, cont, n3])
    passo('E1b', _e1b)
    def _e1c():
        # E1c (revisão, achado C1, S2, a parte da busca): sem fase, a busca "0431" deixa só a OS-0431 no recorte; o grupo T2 soma só ela (= Total,
        # 102 ha), e não as 452 ha de todas as O.S. do talhão; a soma dos grupos = Total
        abre_todas('OS.dc.html')
        J("""(()=>{const i=[...document.querySelectorAll('main input[aria-label="Buscar nesta tabela"]')].find(x=>x.getClientRects().length);
          Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(i,'0431'); i.dispatchEvent(new Event('input',{bubbles:true})); return 1;})()"""); time.sleep(.6)
        troca_visao(J, 'agrupada'); time.sleep(.5)
        g = J(GRUPOS_AREA) or []; t = total_nota(); a = num_br((t.split('·') + ['', ''])[1]); s = round(sum(num_br(x) or 0 for _, x in g), 2)
        lin = sorted(set(x.split('@')[0] for x in ids() if not x.startswith('grp@')))
        chk('E1c busca "0431" (sem fase) → Tabela agrupada por Talhão: só o grupo T2, com a OS-0431, e o subtotal = Total (102 ha); a soma dos grupos = Total',
            lin == ['OS-0431'] and [k for k, _ in g] == ['T2'] and a is not None and abs(a - 102) < .01 and abs(s - a) < .01, [lin, g, s, t])
    passo('E1c', _e1c)
    def _e3b2():
        # E3b2 (revisão, achado A2): recorte só com ordens canceladas (Santa Rita · Safrinha 2027 depois de emitir e cancelar a OS nova):
        # toda visão diz o motivo e oferece "Ver canceladas" (antes: Lista em branco e Kanban com 5 colunas vazias, sem motivo)
        def setid(i, val):
            J(f"""(()=>{{const e=document.getElementById({json.dumps(i)}); const pr=e.tagName==='SELECT'?HTMLSelectElement.prototype:HTMLInputElement.prototype; Object.getOwnPropertyDescriptor(pr,'value').set.call(e,{json.dumps(val)});
              e.dispatchEvent(new Event('input',{{bubbles:true}})); e.dispatchEvent(new Event('change',{{bubbles:true}}));}})()"""); time.sleep(.5)
        opts = lambda i: J(f"[...document.getElementById({json.dumps(i)}).options].map(o=>o.value).filter(Boolean)") or []
        abre('OS.dc.html')
        J("[...document.querySelectorAll('button')].find(b=>/^Nova ordem/.test(b.innerText.trim())).click()"); time.sleep(.6)
        setid('nv_saf', 'S27SF'); setid('nv_cult', opts('nv_cult')[0]); setid('nv_atv', opts('nv_atv')[0]); setid('nv_jan', '2027-03-10')
        J("[...document.querySelectorAll('aside[role=dialog] button')].find(b=>b.innerText.trim()==='Emitir ordem').click()"); time.sleep(.8)
        J("(()=>{const b=[...document.querySelectorAll('aside[role=dialog] [role=alert] button')].find(x=>x.getClientRects().length); b&&b.click();})()"); time.sleep(.6)
        setsel('Filtrar por safra', 'Safrinha 2027'); novos = [x.split('@')[0] for x in ids()]
        for o in novos:
            J(f"(()=>{{ window.__cen.cenMudar(null,c=>window.__cen.osc_cancelar(c,{json.dumps(o)},'teste VISOES-1',['','',''],{{k:'Ana'}})); window.dispatchEvent(new StorageEvent('storage',{{key:'talhao-os-cenario-v1'}})); return 1; }})()"); time.sleep(.5)
        vai('OS.dc.html'); setsel('Filtrar por safra', 'Safrinha 2027')
        # VISOES-2: a Tabela agrupada por Talhão é a Tabela com "Agrupar por"; o Calendário entrou nas visões. Antes do "Ver canceladas", a Tabela
        # volta a "Sem agrupar" (o que a antiga "Lista" mostrava)
        est = {}
        for k in ('lista', 'agrupada', 'kanban', 'calendario', 'carga'):
            troca_visao(J, k); est[k] = estado()
        shot('e2e_1440_so_canceladas_carga'); troca_visao(J, 'lista'); agrupar_por(J, 'Sem agrupar')
        J("(()=>{const b=[...document.querySelectorAll('[data-visoes-estado] button')].find(b=>b.innerText.trim()==='Ver canceladas'); b&&b.click();})()"); time.sleep(.6)
        dep = (chip_on(), [x.split('@')[0] for x in ids()])
        txt = f'Só há ordens canceladas neste recorte (Santa Rita · safra Safrinha 2027): {len(novos)} ordem. Ver canceladas'
        chk('E3b2 Santa Rita · Safrinha 2027 só com a ordem cancelada: Tabela, Tabela agrupada por Talhão, Kanban, Calendário e Carga dizem "Só há ordens canceladas neste recorte (…): 1 ordem." com "Ver canceladas", que filtra a fase Canceladas e mostra a ordem',
            len(novos) == 1 and all(e and e['tipo'] == 'regra' and e['t'] == txt for e in est.values()) and dep[0] == ['Canceladas'] and dep[1] == novos, [novos, est, dep])
    passo('E3b2', _e3b2)
    def _e3d():
        # E3d (revisão, achados B4/C4): depois da ação do estado (Enter em "Limpar filtros" e em "Ver em tabela"), o foco fica num controle à vista,
        # o botão da visão aberta, e não no <body>
        abre('OS.dc.html?view=kanban'); fase('Canceladas'); e1 = estado()
        J("(()=>{const b=[...document.querySelectorAll('[data-visoes-estado] button')].find(b=>b.innerText.trim()==='Limpar filtros'); b&&b.focus();})()"); tecla('Enter'); time.sleep(.6)
        f1 = foco(); s1 = estado()
        J("window.__g2visaoFalha='carga'"); troca_visao(J, 'carga'); e2 = estado()
        J("(()=>{const b=[...document.querySelectorAll('[data-visoes-estado] button')].find(b=>b.innerText.trim()==='Ver em tabela'); b&&b.focus();})()"); tecla('Enter'); time.sleep(.6)
        f2 = foco(); J("window.__g2visaoFalha=null")
        chk('E3d teclado: Enter em "Limpar filtros" (vazio de filtro no Kanban) deixa o foco no botão Kanban; Enter em "Ver em tabela" (erro da Carga) deixa o foco no botão Lista; nunca no BODY',
            bool(e1) and e1['tipo'] == 'vazio' and s1 is None and f1 == 'kanban' and bool(e2) and e2['tipo'] == 'erro' and f2 == 'lista' and ativa() == 'lista', [e1, f1, s1, e2, f2, ativa()])
    passo('E3d', _e3d)
    def _e8():
        # E8 (revisão, achados A5 e C3): a Carga conta o mesmo recorte nos blocos, no estado e na faixa "Sem alocação"
        abre('OS.dc.html'); setsel('Filtrar por fazenda', 'Lagoa Grande'); troca_visao(J, 'carga'); time.sleep(.4)
        es = estado(); bl = blocos(); nota = J("[...document.querySelectorAll('main [role=note]')].filter(n=>n.getClientRects().length).map(n=>n.innerText).find(t=>/carga por recurso mostra/.test(t))||''"); shot('e2e_1440_carga_lagoa')
        setsel('Filtrar por fazenda', 'Todas'); fase('A liberar'); time.sleep(.4); bl2 = blocos(); sa = sem_aloc(); es2 = estado(); shot('e2e_1440_carga_aliberar_todas')
        J("(()=>{const g=document.querySelector('[role=group][aria-label^=\"Ordens do recorte sem alocação\"]'); const b=g&&[...g.querySelectorAll('button')].find(b=>b.innerText.trim()==='OS-0502'); b&&b.click();})()"); time.sleep(.6)
        pa = painel()
        chk('E8 Carga com Fazenda Lagoa Grande: nenhum bloco de outra fazenda e o estado diz "Nenhuma ordem de Lagoa Grande tem alocação…"; Fazenda Todas + A liberar: blocos só de OS-0418, OS-0430 e OS-0431 e a faixa "Sem alocação (3)" com OS-0501, OS-0502 e OS-0511, cada uma abre o painel',
            bl == [] and bool(es) and es['tipo'] == 'regra' and es['t'].startswith('Nenhuma ordem de Lagoa Grande tem alocação') and 'Lagoa Grande' in nota
            and bl2 == ['OS-0418', 'OS-0430', 'OS-0431'] and es2 is None and sa == 'Sem alocação (3) OS-0501 OS-0502 OS-0511' and pa.startswith('OS-0502'), [bl, es, nota[:160], bl2, sa, es2, pa])
        guarda_erros('E8')
    passo('E8', _e8)
    def _e8b():
        # E8b (revisão, achado A5, a parte da Safra): a Carga segue a Safra do topo. A safra 2025/26 só tem ordens encerradas, sem bloco na
        # semana: nenhum bloco (nem os da irrigação só com água, que são da 2026/27) e o estado diz o recorte. Controle: a 2026/27 mostra blocos
        abre('OS.dc.html'); setsel('Filtrar por safra', '2026/27'); troca_visao(J, 'carga'); time.sleep(.4); bl0 = blocos()
        setsel('Filtrar por safra', '2025/26'); time.sleep(.4); es = estado(); bl = blocos()
        nota = J("[...document.querySelectorAll('main [role=note]')].filter(n=>n.getClientRects().length).map(n=>n.innerText).find(t=>/carga por recurso mostra/.test(t))||''") or ''
        chk('E8b Carga com Safra 2025/26: nenhum bloco (as ordens dela não têm alocação) e o estado "Nenhuma ordem de … safra 2025/26 tem alocação…"; com a 2026/27 os blocos aparecem (OS-0419 e OS-0421)',
            {'OS-0419', 'OS-0421'} <= set(bl0) and bl == [] and bool(es) and es['tipo'] == 'regra' and es['t'].startswith('Nenhuma ordem de') and 'safra 2025/26' in es['t']
            and 'safra 2025/26' in nota, [bl0, bl, es, nota[:160]])
        guarda_erros('E8b')
    passo('E8b', _e8b)

def modo_e7():
    """Cliques da persona até o mesmo resultado (window.__cl conta cada clique no documento), na tela que existir."""
    def conta(): return J("window.__cl||0")
    def liga(): J("window.__cl=0; if(!window.__clOn){ window.__clOn=1; document.addEventListener('click',()=>{ window.__cl=(window.__cl||0)+1; },true); } 1")
    def agrupar():
        if J("!!document.querySelector('[role=toolbar] [data-visao=agrupada]')"): J("document.querySelector('[role=toolbar] [data-visao=agrupada]').click()")
        elif J("!!document.querySelector('[data-g2agb=g_os]')"):
            # VISOES-2: Tabela (só se outra visão estiver aberta) + "Agrupar por" › Talhão: 2 cliques no menu
            if ativa() != 'lista': J("document.querySelector('[role=toolbar] [data-visao=lista]').click()"); time.sleep(.4)
            agrupar_por(J, 'Talhão')
        else: J("[...document.querySelectorAll('button')].find(b=>b.innerText.trim()==='Agrupar por talhão').click()")
        time.sleep(.6)
    def agrupado(): return len(grupos()) > 0
    abre('OS.dc.html'); liga()
    # A · filtrar → agrupar → abrir → voltar (detalhe completo) → de volta onde estava (agrupada, filtro). O clique num link que troca de página
    # é contado à parte (+1): o contador da página que sai não sobrevive à navegação
    fase('Em execução'); agrupar()
    J(f"{LINHA('OS-0421')}.click()"); time.sleep(.5); n1 = conta()
    if not painel().startswith('OS-0421'):
        chk('E7 clicar na OS-0421 da tela agrupada abre o painel (sem ele não há "Abrir ordem completa" para medir a volta)', False, [painel(), grupos()[:4], ids()[:4]]); return
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
    b0 = 1; b = b0 + conta()
    tela = ('seletor + Agrupar por' if J("!!document.querySelector('[data-g2agb=g_os]')") else 'seletor') if J("!!document.querySelector('[role=toolbar][data-visoes]')") else 'botão Agrupar por talhão'
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
