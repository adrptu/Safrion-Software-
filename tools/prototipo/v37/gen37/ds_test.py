# -*- coding: utf-8 -*-
"""DS-SEPARADOR, DS-HOVER, DS-RETORNO e DS-DICA (09/10/2026) · teste de navegador do módulo de design system.
Chrome headless por CDP (comp_lib.Chrome), servindo o _render:
 A · separador: todas as páginas a 1440 px (cabeçalho da página e linha de título de cada bloco), 8 telas a 390 px e o painel lateral
     (formulário "Nova safra" e registro do Cadastro); desde 15/10 (SEP-20261015) a linha do título só fica com conteúdo solto abaixo, a barra
     da tabela não tem linha sobre o cabeçalho e a tabela dentro de caixa com borda não tem moldura própria;
 B · hover verde: linha de grade (O.S. e Cadastros) e controles (secundário, opção de visão, primária) pela cor computada;
 C · retorno visual: tela nova (título realçado, anúncio, barra de carga, foco no título vindo de link); etapa do Planejar safra (avançar
     e voltar); liberar uma O.S. no Kanban (o cartão muda de coluna); normal, repetição e recusa no BO-02; menos movimento;
 D · dica: hover, foco, Esc e aria-describedby no botão indisponível; ícone sem texto; selo do Kanban; cabeçalho de coluna; título
     redundante sem dica (e sem a dica nativa); sigla na célula; foco de teclado na linha e no cartão (dica do selo); selo do bloqueio;
 E · 390 px com toque: etapa do SAF, liberar pela lista da O.S., conciliar e toque longo no BO-02;
 F · capturas antes/depois de 6 telas a 1440 e 390 px em _probe/ds/ (antes = DS_ANTES, o _render da base); DS_AMOSTRAS=1 grava as
     amostras do design system;
 G · motivo do botão indisponível visível em texto junto do controle (PRD DS-06 e 74.5.0, VIS-04), a 1440 e 390 px: normal, bloqueio e recusa.
     Ordem de execução: A, B, C, D, F, E, G (ligar o toque tira o hover da janela do teste).
Uso: python3 ds_test.py · DS_RENDER=<dir> serve outro _render (ex.: o da base ecc8b00, para ver o defeito) · DS_PARTES=A,B,C,D,E,F,G
· DS_ANTES=<dir> liga as capturas "antes"."""
import os, sys, time, json, glob
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, servir, troca_visao, cv_todas_sempre, cv_padrao
R = os.environ.get('DS_RENDER') or os.path.join(HERE, '_render')
ANTES = os.environ.get('DS_ANTES') or ''
PARTES = set((os.environ.get('DS_PARTES') or 'A,B,C,D,E,F,G').split(','))
PROBE = os.path.join(HERE, '_probe', 'ds'); os.makedirs(PROBE, exist_ok=True)
ok = []
def chk(nome, cond, extra=''):
    ok.append(bool(cond)); print(('OK  ' if cond else 'FALHOU ') + nome + (' · ' + str(extra)[:400] if (extra != '' and not cond) else ''), flush=True)

def _chrome_com_hover():
    """Chrome headless que se declara com mouse (hover:hover, pointer:fine): sem isso o headless responde (hover:none) e nenhuma regra de
    hover do sistema vale (Emulation.setEmulatedMedia não cobre hover). As telas a 390 px ligam o toque por emulação."""
    import subprocess, tempfile
    from cdp import CH
    from journeys import free
    porta = free(); d = tempfile.mkdtemp(prefix='cdp_ds_')
    gl = (['--use-angle=swiftshader', '--enable-unsafe-swiftshader'] if os.environ.get('CDP_GL') == '1' else ['--disable-gpu'])
    pr = subprocess.Popen([CH, '--headless=new'] + gl + ['--hide-scrollbars', f'--remote-debugging-port={porta}', f'--user-data-dir={d}', '--window-size=1440,900',
                           '--blink-settings=primaryHoverType=2,availableHoverTypes=2,primaryPointerType=4,availablePointerTypes=4', 'about:blank'],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    ant = os.environ.get('CDP_PORT'); os.environ['CDP_PORT'] = str(porta)
    try: ch = Chrome()
    finally:
        if ant is None: os.environ.pop('CDP_PORT', None)
        else: os.environ['CDP_PORT'] = ant
    return ch, pr, d
c, _proc, _pdir = _chrome_com_hover(); port, srv = servir(R); U = lambda f: f'http://127.0.0.1:{port}/{f}'
srv2 = None
J = lambda x: c.js(x)
TOQUE = [False]
def media(toque=False, rm=False):
    c.call('Emulation.setEmulatedMedia', {'features': [{'name': 'prefers-reduced-motion', 'value': 'reduce' if rm else 'no-preference'}]})
def janela(w, h, toque=False):
    """Desktop: só o tamanho (ligar/desligar a emulação de toque zera o mouse com hover do Chrome do teste). Toque: aparelho do comp_lib."""
    if toque: c.aparelho(w, h, toque=True); TOQUE[0] = True
    else: c.call('Emulation.setDeviceMetricsOverride', {'width': w, 'height': h, 'deviceScaleFactor': 1, 'mobile': False}); time.sleep(.2)
def abre(f, w=1440, h=900, toque=False, limpa=True, rm=False, base=None):
    janela(w, h, toque); media(toque, rm)
    u = (base or U)(f)
    if limpa: c.goto(u, .3); J("localStorage.clear();sessionStorage.clear();1")
    c.goto(u, .5); pronto()
def pronto():
    """o motor da tela carregou (o g2lib roda junto com a lógica da tela; antes disso a página mostra só o modelo); a aba fica na frente,
    com foco de janela (sem ele, focus() muda o elemento ativo mas não dispara focusin)"""
    try: c.call('Page.bringToFront')
    except Exception: pass
    for _ in range(50):
        if J("!!window.__g2glob&&!!document.querySelector('h1')"): break
        time.sleep(.1)
    time.sleep(.35)
def errs(): return J("(window.__errs||[]).filter(e=>e.indexOf(\"reading 'g2toast'\")<0).join(' | ')") or ''
def nreal(): return J("(window.__g2realces||[]).length") or 0
def realces(n): return J(f"(window.__g2realces||[]).slice({n})") or []
def vivo(): time.sleep(.15); return J("(document.getElementById('g2-vivo')||{}).textContent||''") or ''
def toast(): return J("(()=>{const t=document.querySelector('[role=status][aria-live=off]'); return t?t.innerText:[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).filter(Boolean).join(' | ');})()") or ''
def centro(expr):
    return J(f"(()=>{{const e={expr}; if(!e) return null; e.scrollIntoView({{block:'center',inline:'nearest'}}); const r=e.getBoundingClientRect(); return [r.left+r.width/2, r.top+r.height/2];}})()")
FORCADOS = []; NOTA = []
def forca(expr):
    """:hover forçado (CSS.forcePseudoState) quando o Chrome headless não aplica :hover ao mouse do CDP; o pointerover que o mouse dispararia
    vai junto, para a dica. A saída do teste diz quando isso aconteceu."""
    c.call('DOM.enable'); c.call('CSS.enable'); c.call('DOM.getDocument', {'depth': 0})
    oid = c.call('Runtime.evaluate', {'expression': expr})['result'].get('objectId')
    nid = c.call('DOM.requestNode', {'objectId': oid})['nodeId']
    c.call('CSS.forcePseudoState', {'nodeId': nid, 'forcedPseudoClasses': ['hover']}); FORCADOS.append(nid)
    J(f"({expr}).dispatchEvent(new PointerEvent('pointerover',{{bubbles:true,composed:true,pointerType:'mouse'}}))")
def hover(expr, espera=.5):
    p = centro(expr)
    if p:
        c.mouse(10, 880 if p[1] < 400 else 120); time.sleep(.05); c.mouse(p[0], p[1]); time.sleep(.12)
        if not J(f"({expr}).matches(':hover')"):
            if not NOTA: NOTA.append(1); print('     (nota: este Chrome headless não aplica :hover ao mouse do CDP; o hover é forçado por CSS.forcePseudoState e o pointerover é disparado no elemento)')
            forca(expr)
        time.sleep(espera)
    return p
def fora():
    c.mouse(1430, 890)
    for nid in FORCADOS:
        try: c.call('CSS.forcePseudoState', {'nodeId': nid, 'forcedPseudoClasses': []})
        except Exception: pass
    if FORCADOS: J("(document.querySelector('main')||document.body).dispatchEvent(new PointerEvent('pointerover',{bubbles:true,composed:true,pointerType:'mouse'}))")
    FORCADOS.clear(); time.sleep(.35)
def clk(t, root='body', forca=False):
    return J(f"""(()=>{{const n=s=>(s||'').replace(/\\s+/g,' ').trim(); const vis=e=>e.getClientRects().length>0;
      const R=[...document.querySelectorAll({json.dumps(root)})].filter(vis).pop()||document.body;
      const es=[...R.querySelectorAll('button,a')].filter(e=>vis(e)&&!e.disabled&&({'true' if forca else 'false'}||e.getAttribute('aria-disabled')!=='true'));
      const e=es.find(x=>n(x.innerText)===n({json.dumps(t)}))||es.find(x=>n(x.innerText).startsWith(n({json.dumps(t)})));
      if(!e) return 'sem '+{json.dumps(t)}; e.click(); return 'ok';}})()""")
DICA = "(()=>{const d=document.getElementById('g2-dica'); return d?{vis:!d.hidden&&d.getClientRects().length>0,t:d.textContent,role:d.getAttribute('role')}:{vis:false,t:'',role:''};})()"
SEP = r"""(()=>{ const vis=e=>!!e&&e.getClientRects().length>0;
  const hd=document.querySelector('[data-root]>div>header,[data-mroot]>header,header.g2-cab');
  const hs=hd?getComputedStyle(hd):null; const cab=!!hs&&parseFloat(hs.borderBottomWidth)>=1&&hs.borderBottomStyle!=='none'&&hs.borderBottomColor!=='rgba(0, 0, 0, 0)';
  const linha=(e)=>{ const s=getComputedStyle(e); return /linear-gradient\(rgb\(228, 233, 229\)/.test(s.backgroundImage)||(parseFloat(s.borderBottomWidth)>=1&&s.borderBottomStyle!=='none'); };
  const borda=(e)=>{ const s=getComputedStyle(e); return parseFloat(s.borderTopWidth)>=1&&s.borderTopStyle!=='none'&&!/rgba\(0, 0, 0, 0\)/.test(s.borderTopColor); };   /* borda visível */
  const prim=(e)=>{ let f=e&&e.firstElementChild; while(f&&getComputedStyle(f).display==='contents') f=f.firstElementChild; return f; };
  /* o conteúdo começa por uma borda no topo (tabela emoldurada, caixa com borda, ficha cuja 1ª célula tem border-top): ela é a linha */
  const moldura=(nx)=>{ const f=prim(nx); if(!f) return false; if(borda(f)) return true; const g=prim(f); return !!g&&borda(g); };
  /* linha dupla (revisão DS, achado 5): a linha do título e, até 14 px abaixo dela, outra borda larga no topo do conteúdo */
  const dupla=(row)=>{ const r=row.getBoundingClientRect(), nx=row.nextElementSibling; if(!nx) return false;
    return [nx,...nx.querySelectorAll('*')].filter(vis).slice(0,40).some(k=>{ const q=k.getBoundingClientRect(); return q.top-r.bottom<=14&&q.top>=r.bottom-1&&borda(k)&&q.width>r.width*0.5; }); };
  /* SEP-20261015 (proprietário, 15/10): a linha do título só fica com conteúdo solto logo abaixo (texto, formulário, lista sem moldura);
     sai quando o corpo começa por tabela, barra de visões, gráfico, caixa (ou cartões), borda no topo ou faixa com fundo próprio */
  const ctrl=e=>!!e.closest('button,input,select,textarea,a[href],label,[role=button],[role=tab],[role=group],[role=tablist]');
  const tr=c=>/rgba\(0, 0, 0, 0\)|transparent/.test(c);
  const caixaVis=e=>{ const s=getComputedStyle(e); return ['Top','Right','Bottom','Left'].every(l=>parseFloat(s['border'+l+'Width'])>=1&&s['border'+l+'Style']!=='none'&&!tr(s['border'+l+'Color'])); };
  const bordaVis=e=>borda(e)&&!tr(getComputedStyle(e).borderTopColor);
  const estrut=(row)=>{ const r0=row.getBoundingClientRect(), nx=row.nextElementSibling, fs=getComputedStyle(row.parentElement).backgroundColor;
    for(const k of [nx,...nx.querySelectorAll('*')].filter(vis).slice(0,80)){ const s=getComputedStyle(k); if(s.display==='contents') continue; const q=k.getBoundingClientRect(); if(q.top-r0.bottom>40) break;
      if(k.matches('.g2visoes-w')) return 'visões'; if(k.matches('.g2caixa,[role=table],table')) return 'tabela';
      /* TAB-01 (padroes-1510.md): filtro rápido em chips é parte da barra da visão (na O.S. a 390 px os chips quebram em 2 linhas antes do seletor) */
      if(k.matches('[role=group]')&&k.querySelector('[aria-pressed]')) return 'visões';
      if(k.matches('svg,[role=img]')&&q.width>r0.width*0.4) return 'gráfico'; if(ctrl(k)) continue;
      if(caixaVis(k)) return 'caixa'; if(bordaVis(k)&&q.width>r0.width*0.5) return 'borda';
      const fundo=!tr(s.backgroundColor)&&s.backgroundColor!==fs&&q.height>=16&&!(parseFloat(s.borderTopLeftRadius)>=14&&q.height<=48)&&!k.matches('[aria-current]');
      if(fundo&&q.width>r0.width*0.5) return 'faixa';
      if(fundo&&[...k.parentElement.children].some(x=>x!==k&&vis(x)&&getComputedStyle(x).backgroundColor!==fs&&!tr(getComputedStyle(x).backgroundColor))) return 'cartões';
      if([...k.childNodes].some(t=>t.nodeType===3&&t.textContent.trim().length>2)) return ''; }
    return ''; };
  const fora=[], duplas=[], sobra=[]; let n=0, nsolto=0;
  for(const s of document.querySelectorAll('main section')){ const row=s.firstElementChild; if(!vis(row)||!row.nextElementSibling) continue;
    if(!row.querySelector(':scope>h2,:scope>h3,:scope>div>h2,:scope>div>h3')) continue; n++;
    const ln=linha(row), t=(row.querySelector('h2,h3').innerText||'').slice(0,40), es=estrut(row);
    if(!es){ nsolto++; if(!ln) fora.push(t); }
    else if(ln) sobra.push(t+' ('+es+')');
    if(ln&&dupla(row)) duplas.push(t); }
  /* (c) barra da tabela sem linha sobre o cabeçalho; (d) tabela dentro de caixa com borda sem moldura própria */
  const barra=[...document.querySelectorAll('.g2caixa')].filter(vis).map(c=>c.firstElementChild).filter(b=>b&&vis(b)&&b.nextElementSibling&&!b.classList.contains('g2rola')
    &&(()=>{ const x=getComputedStyle(b); return parseFloat(x.borderBottomWidth)>=1&&x.borderBottomStyle!=='none'&&!tr(x.borderBottomColor); })()).map(b=>(b.innerText||'').slice(0,30));
  const dentro=[...document.querySelectorAll('.g2caixa')].filter(c=>vis(c)&&caixaVis(c)&&(()=>{ for(let p=c.parentElement;p&&p.tagName!=='MAIN';p=p.parentElement) if(caixaVis(p)) return true; return false; })()).map(c=>(c.innerText||'').slice(0,30));
  return {cab, n, nsolto, fora, duplas, sobra, barra, dentro, h1:!!document.querySelector('h1')}; })()"""
PAINEL = "(()=>{const d=[...document.querySelectorAll('aside[role=dialog]')].find(x=>x.getClientRects().length); if(!d) return null; const r=d.firstElementChild; const s=getComputedStyle(r); return {t:(d.querySelector('h2')||{}).innerText||'',b:parseFloat(s.borderBottomWidth)>=1&&s.borderBottomColor==='rgb(228, 233, 229)'};})()"
try:
    # ======================= A · separador =======================
    if 'A' in PARTES:
        pags = sorted(os.path.basename(p) for p in glob.glob(os.path.join(R, '*.dc.html')))
        # Main.dc.html é página técnica mínima desde 13/10/2026 (o índice saiu e o protótipo abre no Mapa: areas/indice.py), sem cabeçalho de
        # tela; sai da varredura só enquanto não tiver cabeçalho (se voltar a ser tela, volta a ser medida)
        pags = [p for p in pags if not (p == 'Main.dc.html' and '<header' not in open(os.path.join(R, p), encoding='utf-8').read())]
        janela(1440, 900); media()
        semcab, semlin, nblocos, duplas, nsolto, sobra, barras, dentro = [], [], 0, [], 0, [], [], []
        for p in pags:
            c.goto(U(p), .3); time.sleep(.25)
            r = J(SEP) or {}
            nblocos += r.get('n', 0); nsolto += r.get('nsolto', 0)
            if not r.get('cab'): semcab.append(p)
            if r.get('fora'): semlin.append((p, r['fora']))
            if r.get('duplas'): duplas.append((p, r['duplas']))
            if r.get('sobra'): sobra.append((p, r['sobra']))
            if r.get('barra'): barras.append((p, r['barra']))
            if r.get('dentro'): dentro.append((p, r['dentro']))
        chk(f'A1 separador abaixo do cabeçalho da página (título + ação do topo à direita) nas {len(pags)} páginas a 1440 px', not semcab and len(pags) >= 100, semcab)
        # SEP-20261015 (proprietário, 15/10: "deixe somente as que geram efetiva organização visual"): a linha do título fica só com conteúdo
        # solto logo abaixo; antes desta data o oráculo pedia linha (ou borda no topo do conteúdo) em todo bloco com título
        chk(f'A2 linha abaixo do título do bloco com conteúdo solto logo abaixo ({nsolto} de {nblocos} blocos com título)', not semlin and nblocos > 50 and nsolto > 5, semlin[:12])
        chk('A2c sem linha do título quando o corpo começa por tabela, barra de visões, gráfico, caixa ou cartões, borda no topo ou faixa com fundo (SEP-20261015 b)', not sobra, sobra[:12])
        chk('A2b sem linha dupla: a linha do título não fica sobre outra borda larga até 14 px abaixo (revisão DS, achado 5: AG-04det, GE-05, GE-06det)', not duplas, duplas[:12])
        chk('A7 barra da tabela (busca, Agrupar por, Colunas) sem linha sobre o cabeçalho da tabela, que já tem fundo (SEP-20261015 c)', not barras, barras[:12])
        chk('A8 tabela dentro de caixa com borda sem moldura própria (caixa dentro de caixa, SEP-20261015 d)', not dentro, dentro[:12])
        janela(390, 844); media()   # largura do celular sem a emulação de toque (o separador não depende dela; o hover das partes B a D, sim)
        cel = ['SAF.dc.html', 'OS.dc.html', 'EST.dc.html', 'CD-01.dc.html', 'CF-05.dc.html', 'PA.dc.html', 'AG-01.dc.html', 'MB-01.dc.html']
        r390 = {}
        for p in cel:
            c.goto(U(p), .3); time.sleep(.25); r390[p] = J(SEP) or {}
        chk('A3 a 390 px (8 telas): separador do cabeçalho e dos blocos (com a mesma regra do título), sem linha dupla nem linha de barra de tabela',
            all(x.get('cab') and not x.get('fora') and not x.get('duplas') and not x.get('sobra') and not x.get('barra') and not x.get('dentro') for x in r390.values()),
            {k: {kk: vv for kk, vv in v.items() if vv and kk in ('fora', 'duplas', 'sobra', 'barra', 'dentro')} for k, v in r390.items() if not (v.get('cab') and not v.get('fora') and not v.get('duplas') and not v.get('sobra') and not v.get('barra') and not v.get('dentro'))})
        abre('SAF.dc.html'); clk('Criar safra'); time.sleep(.4); pn = J(PAINEL)
        chk('A4 painel "Nova safra": linha abaixo do título e do × do topo à direita', bool(pn) and pn['t'] == 'Nova safra' and pn['b'], pn)
        abre('CD-03.dc.html'); J("(()=>{const r=document.querySelector('[role=row].g2ed'); (r.querySelector('.g2pw')||r).click(); return 1;})()"); time.sleep(.4); pn = J(PAINEL)
        chk('A5 painel do registro (Cadastros): linha abaixo do título', bool(pn) and pn['b'], pn)
        chk('A6 sem erro de execução nas telas da varredura do separador', not errs(), errs())

    # ======================= B · hover verde =======================
    if 'B' in PARTES:
        abre('OS.dc.html')
        chk('B0 pré-condição: a janela do teste tem mouse com hover ((hover:hover) e (pointer:fine))', TOQUE[0] or J("matchMedia('(hover:hover)').matches&&matchMedia('(pointer:fine)').matches"), '')
        row = "document.querySelector('[role=table] [role=row].g2ed')"
        hover(row); bg = J(f"getComputedStyle({row}).backgroundColor")
        chk('B1 linha da grade da O.S.: hover verde #F2F8F4', bg == 'rgb(242, 248, 244)', bg)
        # 13/10/2026 (filtros da O.S. na faixa "Filtros desta tela"): o seletor Talhão da barra da O.S. (ost_btn), secundário claro de referência
        # desde a VISOES-1, saiu; a barra da O.S. não tem outro botão secundário, e a referência passa a ser "Nova safra" do Planejar safra
        fora(); abre('SAF.dc.html')
        sec = "[...document.querySelectorAll('main button')].find(b=>b.getClientRects().length&&b.innerText.trim()==='Criar safra')"
        hover(sec); st = J(f"(()=>{{const s=getComputedStyle({sec}); return [s.backgroundImage,s.borderTopColor,s.boxShadow,s.filter];}})()") or ['', '', '', '']
        chk('B2 botão secundário (Criar safra): camada verde (rgba(30,122,76,.07)) e borda #9DBFAA; sem a camada cinza nem escurecer', '30, 122, 76, 0.07' in st[0] and st[1] == 'rgb(157, 191, 170)' and '21, 32, 26, 0.05' not in st[2] and st[3] == 'none', st)
        fora(); abre('OS.dc.html')
        seg = "document.querySelector('[role=toolbar] [data-visao=kanban]')"   # VISOES-1: opção de visão só com ícone
        hover(seg); st = J(f"(()=>{{const s=getComputedStyle({seg}); return [s.backgroundImage,s.boxShadow,s.filter];}})()") or ['', '', '']
        chk('B3 opção de visão (Kanban): camada verde, sem cinza', '30, 122, 76' in st[0] and '21, 32, 26, 0.05' not in st[1] and st[2] == 'none', st)
        prim = "[...document.querySelectorAll('main button,header button')].find(b=>b.innerText.trim()==='Criar ordem')"
        hover(prim); st = J(f"(()=>{{const s=getComputedStyle({prim}); return [s.backgroundImage,s.filter,s.backgroundColor];}})()") or ['', '', '']
        chk('B4 primária (Criar ordem): só escurece (brightness .92), sem camada clara sobre o texto branco', st[0] == 'none' and 'brightness(0.92)' in st[1] and st[2] == 'rgb(30, 122, 76)', st)
        fora()
        abre('CD-01.dc.html')
        kid = "[...document.querySelectorAll('[role=table] [role=row].g2ed.g2kid')].find(r=>/T1/.test(r.innerText))"
        hover(kid); bg = J(f"getComputedStyle({kid}).backgroundColor")
        chk('B5 linha da grade dos Cadastros (T1): hover verde #F2F8F4, não o cinza #F4F6F3', bg == 'rgb(242, 248, 244)', bg)
        # 16/10/2026 (padrão comum dos cadastros): a faixa e o hover próprios da linha de grupo (.cadx-arv, #E8F3EC) saíram com o CADX_CSS; a
        # linha de grupo que abre detalhe tem o hover verde do motor (.g2ed, #F2F8F4), igual às árvores das outras telas
        grp = "[...document.querySelectorAll('[role=table] [role=row].g2ed:not(.g2kid)')].find(r=>r.querySelector('.g2car'))"
        for pg in ('CD-01.dc.html', 'CD-02.dc.html', 'CD-06.dc.html', 'CD-07.dc.html'):
            abre(pg)
            if J(f"!!{grp}"): break
        if J(f"!!{grp}"):
            hover(grp); bg = J(f"getComputedStyle({grp}).backgroundColor")
            chk('B6 linha de grupo da árvore dos Cadastros: hover verde do motor (#F2F8F4), não cinza', bg == 'rgb(242, 248, 244)', bg)
        else: print('(B6 pulado: nenhuma linha de grupo que abre detalhe nas árvores dos Cadastros)')
        fora(); chk('B7 sem erro de execução', not errs(), errs())

    # ======================= C · retorno visual =======================
    if 'C' in PARTES:
        abre('OS.dc.html'); time.sleep(.3); rs = realces(0); v = vivo()
        chk('C1 tela nova: o título da tela é realçado e o novo contexto é anunciado (aria-live polite)', any(x['tag'] == 'H1' and 'Ordem de Serviço' in x['txt'] for x in rs) and v.startswith('Tela: Ordem de Serviço')
            and J("document.getElementById('g2-vivo').getAttribute('aria-live')") == 'polite', [rs, v])
        J("window.__pp=null; window.addEventListener('pageshow',e=>{window.__pp=e.persisted;}); 1")   # o C2c lê se a O.S. voltou da memória
        # barra lateral sempre recolhida (13/10/2026): o Planejar safra saiu da barra; o link é o ícone "Agrícola", que abre a tela de entrada do módulo
        cl = J("(()=>{const a=document.querySelector('.menu-lat a[href=\"MOD-AGR.dc.html\"]'); if(!a) return 'sem link'; a.click(); const g=document.getElementById('g2-carga'); return g?g.className:'sem barra';})()")
        chk('C2 clicar num link de outra tela liga a barra fina de carga no topo já no clique', cl == 'ini', cl)
        for _ in range(40):
            time.sleep(.2)
            if (J("location.pathname") or '').endswith('MOD-AGR.dc.html') and J("document.readyState") == 'complete': break
        time.sleep(.8)
        fo = J("(()=>{const a=document.activeElement; return a?[a.tagName,(a.innerText||'').trim()]:null;})()"); v = vivo(); rs = realces(0)
        stT = J("(()=>{const h=document.querySelector('header h1'); return h&&h.nextElementSibling?h.nextElementSibling.textContent.replace(/\\s+/g,' ').trim():'';})()") or ''
        # revisão DS (achado 10): com o foco no título o leitor de tela já lê "Agrícola"; o anúncio leva só o estado (antes: "Tela: … · …", o título duas vezes)
        chk('C3 tela aberta pelo link (ícone Agrícola da barra): foco no título da tela nova, título realçado e anúncio só do estado (sem repetir o título que o foco já lê)', fo and fo[0] == 'H1' and fo[1] == 'Agrícola'
            and any(x['tag'] == 'H1' for x in rs) and v == stT and 'Agrícola' not in v and not v.startswith('Tela:'), [fo, v, stT, rs])
        # revisão DS (achado 4, mutante M2): a barra termina depois da carga (o C2 só via o começo)
        time.sleep(.4); bar = J("(()=>{const b=document.getElementById('g2-carga'); return b?[b.className,getComputedStyle(b).opacity]:null;})()")
        chk('C2b a barra de carga termina depois que a tela nova monta (sem ini/chega, opacidade 0)', bool(bar) and bar[0] not in ('ini', 'chega') and bar[1] == '0', bar)
        # revisão DS (achado 1): voltar pelo navegador traz a tela anterior da memória (bfcache) sem montar de novo; a barra ligada no clique termina
        h = c.call('Page.getNavigationHistory'); c.call('Page.navigateToHistoryEntry', {'entryId': h['entries'][h['currentIndex'] - 1]['id']})
        for _ in range(30):
            time.sleep(.2)
            if (J("location.pathname") or '').endswith('OS.dc.html') and J("document.readyState") == 'complete': break
        time.sleep(1.0)
        bf = J("(()=>{const b=document.getElementById('g2-carga'); return {url:location.pathname, pp:window.__pp===true, cls:b?b.className:null, op:b?getComputedStyle(b).opacity:null, nav:sessionStorage.getItem('g2nav')};})()") or {}
        chk('C2c voltar pelo navegador (a O.S. volta da memória, pageshow persisted): a barra não fica presa (sem ini, opacidade 0) e a marca de navegação sai', bf.get('pp') and bf.get('url', '').endswith('OS.dc.html')
            and bf.get('cls') not in ('ini', 'chega') and bf.get('op') == '0' and not bf.get('nav'), bf)
        # etapa (SAF): avançar pela linha, pela área de ações, e voltar
        abre('SAF.dc.html'); n0 = nreal()
        J("(()=>{const r=[...document.querySelectorAll('main [role=row]')].find(r=>/Safra 2026\\/27/.test(r.innerText)); const b=r&&[...r.querySelectorAll('button')].find(b=>/^Continuar/.test(b.innerText.trim())); if(b) b.click(); return !!b;})()")
        time.sleep(.5); v = vivo(); rs = realces(n0)
        chk('C4 Planejar safra · escolher a safra leva à etapa 2: o bloco da etapa nova é realçado e a etapa é anunciada', v.startswith('Etapa 2 de 4: Defina cultivos e planos') and len(rs) >= 1 and rs[-1]['tag'] == 'SECTION', [v, rs])
        n1 = nreal(); J("document.querySelector('[data-acoes] [data-acao=avancar]').click()"); time.sleep(.6); v = vivo(); rs = realces(n1)
        foc = J("document.activeElement&&document.activeElement.tagName")
        chk('C5 avançar (área de ações) para a etapa 3: realce, anúncio "Etapa 3 de 4" e foco no título do bloco novo', v.startswith('Etapa 3 de 4: Dimensione operações e recursos') and len(rs) >= 1 and foc in ('H2', 'H3'), [v, rs, foc])
        n2 = nreal(); J("document.querySelector('[data-acoes] [data-acao=voltar]').click()"); time.sleep(.6); v = vivo(); rs = realces(n2)
        chk('C6 voltar para a etapa 2: realce e anúncio "Etapa 2 de 4"', v.startswith('Etapa 2 de 4') and len(rs) >= 1, [v, rs])
        # O.S. no Kanban: liberar move o cartão de "A liberar" para "Liberadas"
        abre('OS.dc.html'); troca_visao(J, 'kanban')
        COL = "(()=>{const l=document.querySelector('[role=list][aria-label=\"Kanban das ordens\"]'); if(!l) return null; const cols=[...l.querySelectorAll(':scope>sc-for>div,:scope>div')]; return cols.map(c=>[...c.querySelectorAll('[role=button] b')].map(b=>b.innerText.trim()));})()"
        k0 = J(COL) or []
        J("(()=>{const k=[...document.querySelectorAll('[role=list] [role=button]')].find(k=>(k.querySelector('b')||{}).innerText==='OS-0430'); if(k) k.click(); return !!k;})()"); time.sleep(.5)
        clk('Liberar para execução', 'aside[role=dialog]'); time.sleep(.4); n3 = nreal(); clk('Confirmar liberação', 'aside[role=dialog]'); time.sleep(.7)
        t = toast(); v = vivo(); rs = realces(n3); k1 = J(COL) or []
        chk('C7 Kanban com exatamente 5 fases antes e depois', len(k0) == 5 and len(k1) == 5, [len(k0), len(k1)])
        chk('C8 liberar a OS-0430: o cartão passa de A liberar para Liberadas e é realçado; o novo estado é anunciado (o aviso)', len(k0) == 5 and 'OS-0430' in k0[0] and len(k1) == 5 and 'OS-0430' in k1[1]
            and any('OS-0430' in x['txt'] for x in rs) and t and v.startswith(t.split(' | ')[0][:40]), [t, v, rs, k1[:2]])
        chk('C9 o aviso visível não é lido em dobro (aria-live=off; a região viva anuncia)', J("[...document.querySelectorAll('[role=status]')].some(x=>x.getAttribute('aria-live')==='off')"), '')
        # BO-02: normal, repetição (clique duplo) e recusa (indisponível com motivo)
        abre('BO-02.dc.html'); n4 = nreal()
        J("(()=>{const b=[...document.querySelectorAll('header button')].find(x=>x.innerText.trim()==='Conciliar pagamentos'); b.click(); b.click(); return 1;})()"); time.sleep(.7)
        t = toast(); v = vivo(); rs = realces(n4)
        NCON = "Object.values(JSON.parse(localStorage.getItem('talhao-os-cenario-v1')).assin.recibos).filter(r=>/^CON-/.test(r.id)).length"
        ncon = J(NCON)
        chk('C10 normal: conciliar realça o que mudou e anuncia o resultado', 'CON-0001' in t and len(rs) >= 1 and 'CON-0001' in v, [t, v, rs])
        chk('C11 repetição: o clique duplo grava um só recibo (CON-0001)', ncon == 1, ncon)
        J("(()=>{window.__chegou=[]; [...document.querySelectorAll('header button')].find(x=>x.innerText.trim()==='Conciliar pagamentos').addEventListener('click',()=>window.__chegou.push(1)); return 1;})()")   # revisão DS (achado 4, M6)
        J("[...document.querySelectorAll('header button')].find(x=>x.innerText.trim()==='Conciliar pagamentos').click()"); time.sleep(.4); v = vivo(); d = J(DICA)
        chk('C12 recusa: clicar de novo no botão indisponível não roda o comando; a dica no próprio botão (role=tooltip) diz o porquê e a recusa é anunciada',
            J(NCON) == 1 and d['vis'] and d['role'] == 'tooltip' and 'Nenhum evento do provedor a conciliar' in d['t'] and v.startswith('Indisponível: Nenhum evento'), [J(NCON), d, v])
        chk('C12b a recusa para o clique antes do botão: o ouvinte do próprio botão (onde o comando de uma tela nova estaria) não recebe o clique', J("(window.__chegou||[1]).length") == 0, J("window.__chegou"))
        # menos movimento: realce estático, sem animação
        abre('SAF.dc.html', rm=True)
        rm = J("""(async()=>{const r=[...document.querySelectorAll('main [role=row]')].find(r=>/Safra 2026\\/27/.test(r.innerText)); [...r.querySelectorAll('button')].find(b=>/^Continuar/.test(b.innerText.trim())).click();
          await new Promise(x=>setTimeout(x,120)); const e=document.querySelector('.g2-realce'); if(!e) return null;
          e.getAnimations().forEach(a=>{ try{ a.finish(); }catch(x){} });   /* a transição de 0,01 ms (menos movimento) conclui; o headless não desenha quadros na aba de fundo */
          const s=getComputedStyle(e); return [s.animationName,s.backgroundColor,s.boxShadow,(document.getElementById('g2-carga')?getComputedStyle(document.getElementById('g2-carga')).transitionDuration:''),document.visibilityState];})()""")
        chk('C13 prefers-reduced-motion: sem animação; realce estático curto (#EDF7F0 e anel verde)', bool(rm) and rm[0] == 'none' and rm[1] == 'rgb(237, 247, 240)' and '30, 122, 76' in rm[2], rm)
        time.sleep(.8); chk('C14 o realce estático sai sozinho (≈600 ms)', not J("!!document.querySelector('.g2-realce')"), '')
        abre('SAF.dc.html')
        an = J("""(async()=>{const r=[...document.querySelectorAll('main [role=row]')].find(r=>/Safra 2026\\/27/.test(r.innerText)); [...r.querySelectorAll('button')].find(b=>/^Continuar/.test(b.innerText.trim())).click();
          await new Promise(x=>setTimeout(x,60)); const e=document.querySelector('.g2-realce'); return e?[getComputedStyle(e).animationName,getComputedStyle(e).animationDuration]:null;})()""")
        chk('C15 sem a preferência: o realce é a animação g2realce de 0,52 s', bool(an) and an[0] == 'g2realce' and an[1] == '0.52s', an)
        # revisão DS (achado 3): trocar de etapa pelo botão da linha (Enter) tira o botão da tela; o foco vai ao título do novo contexto, não ao BODY
        for pg, rot in (('CMP.dc.html', 'Abrir compra'), ('SAF.dc.html', 'Continuar')):
            abre(pg)
            okb = J(f"(()=>{{const b=[...document.querySelectorAll('main [role=row] button')].find(b=>b.getClientRects().length&&b.innerText.trim().startsWith({json.dumps(rot)})); if(!b) return false; b.focus(); return document.activeElement===b;}})()")
            n7 = nreal(); c.tecla('Enter', 'Enter', 13, text='\r'); time.sleep(.9); v = vivo(); rs = realces(n7)
            fo = J("(()=>{const a=document.activeElement; return a?[a.tagName,(a.innerText||'').trim().slice(0,60),!!(document.querySelector('main')||document.body).contains(a)]:null;})()")
            chk(f'C17 {pg[:-8]} · Enter em "{rot}" na linha: a etapa 2 é anunciada e realçada, e o foco vai ao título do novo contexto (h2/h3), não ao BODY', okb and v.startswith('Etapa 2 de') and len(rs) >= 1 and fo and fo[0] in ('H2', 'H3') and fo[2], [okb, v, fo, rs])
        chk('C16 sem erro de execução', not errs(), errs())

    # ======================= D · dica =======================
    if 'D' in PARTES:
        abre('BO-02.dc.html'); clk('Conciliar pagamentos'); time.sleep(.6)
        BTN = "[...document.querySelectorAll('header button')].find(x=>x.innerText.trim()==='Conciliar pagamentos')"
        st = J(f"(()=>{{const b={BTN}; return b?[b.getAttribute('aria-disabled'),b.disabled,b.tabIndex,b.getAttribute('data-dica')]:null;}})()")
        chk('D1 botão indisponível com motivo continua focável (aria-disabled="true", sem disabled) e traz o motivo em data-dica', st and st[0] == 'true' and st[1] is False and st[2] == 0 and 'Nenhum evento' in (st[3] or ''), st)
        fora(); time.sleep(.3); hover(BTN, .7); d = J(DICA)
        db = J(f"({BTN}).getAttribute('aria-describedby')||''"); tt = J(f"({BTN}).getAttribute('title')")
        chk('D2 hover: a dica abre (role=tooltip) com o porquê; o leitor de tela recebe aria-describedby; a dica nativa (title) sai de cima', d['vis'] and 'Nenhum evento do provedor a conciliar' in d['t'] and 'g2-dica' in db and tt is None, [d, db, tt])
        fora(); time.sleep(.4); d = J(DICA); tt = J(f"({BTN}).getAttribute('title')")
        chk('D3 tirar o ponteiro fecha a dica e devolve o title', not d['vis'] and 'Nenhum evento' in (tt or '') and 'g2-dica' not in (J(f"({BTN}).getAttribute('aria-describedby')||''") or ''), [d, tt])
        J(f"({BTN}).focus()"); time.sleep(.3); d = J(DICA); db = J(f"({BTN}).getAttribute('aria-describedby')||''")
        chk('D4 foco de teclado: a dica abre e descreve o botão (aria-describedby="g2-dica")', d['vis'] and 'g2-dica' in db and J("document.getElementById(document.activeElement.getAttribute('aria-describedby').split(' ').pop()).getAttribute('role')") == 'tooltip', [d, db])
        c.tecla('Escape', 'Escape', 27); time.sleep(.25); d = J(DICA); db = J(f"({BTN}).getAttribute('aria-describedby')||''")
        chk('D5 Esc fecha a dica sem tirar o foco do botão', not d['vis'] and 'g2-dica' not in db and J(f"document.activeElement===({BTN})"), [d, db])
        c.tecla('Enter', 'Enter', 13, text='\r'); time.sleep(.4); v = vivo(); d = J(DICA)
        ncon = J("Object.values(JSON.parse(localStorage.getItem('talhao-os-cenario-v1')).assin.recibos).filter(r=>/^CON-/.test(r.id)).length")
        chk('D6 Enter no botão indisponível: o comando não roda (1 recibo), a dica mostra o porquê e a recusa é anunciada', ncon == 1 and d['vis'] and v.startswith('Indisponível: Nenhum evento'), [ncon, d, v])
        fora()
        # ícone sem texto (barra lateral sempre recolhida, 13/10/2026; antes: o botão de expandir/recolher o menu): a dica mostra o nome do
        # módulo, sem repetir para o leitor de tela; a dica nativa (title) sai enquanto a do sistema está aberta e volta quando o ponteiro sai
        abre('OS.dc.html'); ICO = "document.querySelector('.menu-lat a[aria-label=\"Mapa\"]')"; t0 = J(f"({ICO}).getAttribute('title')")   # aria-label: o logotipo (Início (Mapa)) também leva ao IN-04
        hover(ICO, .7); d = J(DICA); db = J(f"({ICO}).getAttribute('aria-describedby')||''"); t1 = J(f"({ICO}).getAttribute('title')")
        fora(); t2 = J(f"({ICO}).getAttribute('title')"); d2 = J(DICA)
        chk('D7 ícone sem texto (ícone "Mapa" da barra recolhida): a dica mostra o nome do módulo e não vira descrição repetida; a dica nativa sai enquanto ela está aberta e volta quando o ponteiro sai',
            d['vis'] and d['t'] == 'Mapa' and 'g2-dica' not in db and t0 == 'Mapa' and t1 is None and t2 == 'Mapa' and not d2['vis'], [d, db, t0, t1, t2, d2])
        # título igual ao rótulo visível: a barra recolhida não tem mais rótulo visível (antes: item "Mapa" do menu aberto) e a fonte do mapa,
        # o último caso real, foi para a dica ⓘ da camada (menos texto, 13/10/2026). A regra é da biblioteca (g2lib: g2ttTira/g2ttVolta):
        # o teste põe na tela um rótulo cortado com o mesmo texto no title e confere o comportamento
        abre('IN-04.dc.html'); FON = "window.__d8"
        t0 = J("(()=>{const m=document.querySelector('main'); const e=document.createElement('div'); e.textContent='Rótulo cortado de teste do D8'; e.title='Rótulo cortado de teste do D8';"
               " e.style.cssText='position:fixed;left:420px;top:420px;padding:8px;background:#fff;z-index:99;white-space:nowrap;'; m.appendChild(e); window.__d8=e; return e.getAttribute('title');})()")
        hover(FON, .7); d = J(DICA); t1 = J(f"(({FON})||{{getAttribute:()=>'sem fonte'}}).getAttribute('title')")
        chk('D8 título igual ao rótulo visível (rótulo cortado no IN-04): sem dica', bool(t0) and not d['vis'], [t0, d])
        # revisão DS (achado 9): o title igual ao rótulo faria o navegador mostrar a dica nativa repetida: ele sai enquanto o ponteiro está em cima
        fora(); t2 = J(f"(({FON})||{{getAttribute:()=>'sem fonte'}}).getAttribute('title')")
        chk('D8b ponteiro no rótulo cortado (title igual ao texto): o title sai (sem a dica nativa repetida) e volta quando o ponteiro sai', bool(t0) and t1 is None and t2 == t0, [t0, t1, t2])
        abre('OS.dc.html')
        fora(); troca_visao(J, 'kanban')
        COLT = "[...document.querySelectorAll('[role=list] [data-dica-de]')].find(s=>s.textContent.trim()==='A liberar')"   # textContent: o título da coluna é maiúsculo só no CSS
        hover(COLT, .7); d = J(DICA)
        chk('D9 selo de estado (coluna A liberar do Kanban): significado e próximo passo (Aprovar e liberar)', d['vis'] and 'Aprovar e liberar' in d['t'] and 'gestor libera' in d['t'], [d, J(f"!!{COLT}")])
        fora(); troca_visao(J, 'lista')
        hover("[...document.querySelectorAll('[role=table] [data-dica]')].find(s=>/Falta insumo/.test(s.innerText))", .7); d = J(DICA)
        chk('D10 selo da lista (Falta insumo · …): o que falta e quem resolve', d['vis'] and 'Estoque' in d['t'] and 'agrônomo' in d['t'], d)
        fora(); abre('BO-01.dc.html')
        hb = "[...document.querySelectorAll('[role=columnheader][data-dica]')].find(h=>/R\\$\\/ha/.test(h.getAttribute('data-dica')))"
        foc = J(f"(()=>{{const h={hb}; const b=h&&h.querySelector('button.g2hb'); if(b) b.focus(); return [!!h, !!b, document.activeElement===b, document.hasFocus()];}})()"); time.sleep(.3); d = J(DICA)
        db = J("document.activeElement&&document.activeElement.getAttribute('aria-describedby')||''")
        chk('D11 unidade no cabeçalho da coluna (R$/ha): a dica explica a conta no foco do botão de ordenar', d['vis'] and 'reais por hectare' in d['t'] and 'g2-dica' in db, [d, db, foc])
        c.tecla('Escape', 'Escape', 27); time.sleep(.2)
        # revisão DS (achado 8): a sigla ou a unidade que está na célula (unidade junto do valor) dá a dica do cabeçalho da coluna
        hs = {}; cv_todas_sempre(c)   # V2-3: Premissas (GE-02) fica fora do "Abre com"; aqui se confere a dica do cabeçalho, não o padrão
        for pg, rx in (('PL-02.dc.html', 'Gatilho por extenso'), ('GE-02.dc.html', 'Premissas')):
            abre(pg); hs[pg] = J(f"(()=>{{const h=[...document.querySelectorAll('[role=columnheader]')].find(h=>h.innerText.trim().toLowerCase().startsWith({json.dumps(rx.lower())})); return h?(h.getAttribute('data-dica')||''):null;}})()")
        foc = J("(()=>{const h=[...document.querySelectorAll('[role=columnheader]')].find(h=>/^premissas/i.test(h.innerText.trim())); const b=h&&h.querySelector('button.g2hb'); if(b) b.focus(); return !!b;})()"); time.sleep(.3); d = J(DICA)
        chk('D14 sigla ou unidade na célula vira dica do cabeçalho: DAP (PL-02 Gatilho por extenso) e sc/ha (GE-02 Premissas, "rendimento 62 sc/ha"), aberta no foco do botão de ordenar',
            (hs.get('GE-02.dc.html') or '').startswith('sc/ha:') and (hs.get('PL-02.dc.html') or '').startswith('DAP:') and foc and d['vis'] and 'sacas por hectare' in d['t'], [hs, foc, d])
        cv_padrao(c)
        c.tecla('Escape', 'Escape', 27); time.sleep(.2)
        # revisão DS (achado 2): o selo não recebe foco; com foco de teclado (Tab) na linha ou no cartão, a dica é a do selo e descreve a linha
        abre('OS.dc.html')
        def tab_ate(sel, rx):
            pos = J(f"""(()=>{{const q=[...document.querySelectorAll({json.dumps(sel)})].filter(e=>e.getClientRects().length); const i=q.findIndex(e=>{rx}.test(e.innerText)); if(i<0) return null;
              q[i].scrollIntoView({{block:'center'}}); const o=q[i>0?i-1:i+1]; o.focus(); return i>0?1:-1;}})()""")
            if pos is None: return None
            c.tab(shift=(pos < 0)); time.sleep(.4)
            return J("(()=>{const a=document.activeElement, d=document.getElementById('g2-dica'); return {foco:(a.innerText||'').replace(/\\s+/g,' ').slice(0,40), fv:a.matches(':focus-visible'), db:a.getAttribute('aria-describedby')||'', vis:!!d&&!d.hidden, t:d?d.textContent:''};})()")
        rl = tab_ate('[role=row].g2ed', '/OS-0418/')
        chk('D13 Tab até a linha da OS-0418: a dica do selo "Falta insumo" (o que falta e quem resolve) abre e descreve a linha (aria-describedby)', bool(rl) and 'OS-0418' in rl['foco'] and rl['fv'] and rl['vis']
            and rl['t'].startswith('Falta insumo:') and 'Estoque' in rl['t'] and 'agrônomo' in rl['t'] and 'g2-dica' in rl['db'], rl)
        c.tecla('Escape', 'Escape', 27); time.sleep(.2)
        p = centro("[...document.querySelectorAll('[role=row].g2ed')].find(r=>/OS-0418/.test(r.innerText)).firstElementChild")
        c.mouse(p[0], p[1]); c.mouse(p[0], p[1], 'mousePressed', 'left'); c.mouse(p[0], p[1], 'mouseReleased', 'left'); time.sleep(.45); d = J(DICA)
        chk('D13b o clique do ponteiro na linha não abre a dica do selo (só o foco de teclado)', not d['vis'] or not d['t'].startswith('Falta insumo:'), d)
        J("(()=>{const b=[...document.querySelectorAll('aside[role=dialog] button')].find(b=>/Fechar|×/.test(b.getAttribute('aria-label')||b.innerText)); if(b) b.click(); return 1;})()"); fora()
        troca_visao(J, 'kanban')
        kb = tab_ate('[role=list] [role=button]', '/OS-0418/')
        chk('D13c Tab até o cartão da OS-0418 no Kanban: a mesma dica do selo, descrevendo o cartão', bool(kb) and 'OS-0418' in kb['foco'] and kb['vis'] and kb['t'].startswith('Falta insumo:') and 'g2-dica' in kb['db'], kb)
        c.tecla('Escape', 'Escape', 27); time.sleep(.2); troca_visao(J, 'lista')
        # revisão DS (achado 6): o selo do bloqueio do encerramento leva o mesmo texto do painel e do comando (osEncBloq), com quem resolve
        SEL = "[...document.querySelectorAll('[role=row].g2ed')].find(r=>/OS-0417/.test(r.innerText)).querySelector('[data-dica^=\"Encerrar bloqueado\"]')"
        hover(SEL, .7); d = J(DICA); fora()
        J("(()=>{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>/OS-0417/.test(r.innerText)); (r.querySelector('.g2pw')||r).click(); return 1;})()"); time.sleep(.5)
        pn = J("(()=>{const a=[...document.querySelectorAll('aside[role=dialog]')].find(x=>x.getClientRects().length); return a?a.innerText.replace(/\\s+/g,' '):'';})()") or ''
        bt, _, bq = (d.get('t') or '').partition(' Próximo passo: ')
        chk('D15 selo "Sobras a receber" da OS-0417: a dica é o bloqueio do encerramento (o mesmo texto do painel) e quem resolve (Rui, almoxarife)', d['vis'] and bt.startswith('Encerrar bloqueado: sobra em custódia')
            and 'Rui (almoxarife) recebe a devolução no Estoque' in bq and bt in pn and bq.rstrip('.') in pn, [d, pn[:400]])
        chk('D12 sem erro de execução', not errs(), errs())

    # ======================= F · capturas antes/depois =======================
    if 'F' in PARTES:
        if os.environ.get('DS_AMOSTRAS'):   # antes das capturas: precisa do mouse com hover   # amostras do design system (docs/design-system/amostras): recortes de 1440 px
            AM = os.path.join(HERE, '..', '..', '..', '..', 'docs', 'design-system', 'amostras'); os.makedirs(AM, exist_ok=True)
            def recorte(nome, expr, m=10, h=None):
                b = J(f"(()=>{{const e={expr}; if(!e) return null; const r=e.getBoundingClientRect(); return [r.left,r.top,r.width,r.height];}})()")
                if not b: return False
                import base64
                d = c.call('Page.captureScreenshot', {'format': 'png', 'clip': {'x': max(0, b[0] - m), 'y': max(0, b[1] - m), 'width': b[2] + 2 * m, 'height': (h or b[3]) + 2 * m, 'scale': 1}})
                open(os.path.join(AM, nome), 'wb').write(base64.b64decode(d['data'])); return True
            fe = []
            # SEP-20261015: a amostra é um bloco que mantém a linha (conteúdo solto abaixo do título); o bloco da O.S. (barra de visões) ficou sem ela
            abre('GE-05.dc.html'); fe.append(recorte('separador-bloco.png', "[...document.querySelectorAll('main section')].find(s=>/Crédito solicitado pelo caso/.test(s.innerText))", 6))
            abre('OS.dc.html')
            hover("[...document.querySelectorAll('main button')].find(b=>b.innerText.trim()==='Agrupar por talhão')", .6)
            fe.append(recorte('hover-secundario.png', "[...document.querySelectorAll('main button')].find(b=>b.innerText.trim()==='Agrupar por talhão').parentElement", 12))
            abre('BO-02.dc.html'); clk('Conciliar pagamentos'); time.sleep(.6); fora(); time.sleep(.3)
            hover("[...document.querySelectorAll('header button')].find(x=>x.innerText.trim()==='Conciliar pagamentos')", .8)
            fe.append(recorte('dica-indisponivel.png', "(()=>{const b=[...document.querySelectorAll('header button')].find(x=>x.innerText.trim()==='Conciliar pagamentos'); const d=document.getElementById('g2-dica'); const r1=(b.closest('.g2ind')||b).getBoundingClientRect(), r2=d.getBoundingClientRect();   /* botão e motivo visível (acao_motivo) com a dica */ const x=Math.min(r1.left,r2.left), y=Math.min(r1.top,r2.top); return {getBoundingClientRect:()=>({left:x,top:y,width:Math.max(r1.right,r2.right)-x,height:Math.max(r1.bottom,r2.bottom)-y})};})()", 14))
            abre('SAF.dc.html', rm=True)
            J("(()=>{const r=[...document.querySelectorAll('main [role=row]')].find(r=>/Safra 2026\\/27/.test(r.innerText)); [...r.querySelectorAll('button')].find(b=>/^Continuar/.test(b.innerText.trim())).click(); return 1;})()"); time.sleep(.15)
            fe.append(recorte('realce-etapa.png', "document.querySelector('.g2-realce')", 8, 170))
            chk('F2 amostras do design system em docs/design-system/amostras (separador, hover, dica, realce)', all(fe), fe)
        telas = ['OS.dc.html', 'PA.dc.html', 'PM.dc.html', 'AG-01.dc.html', 'AG-01det.dc.html', 'AG-07.dc.html']   # telas do menu (e um detalhe) onde o censo da base achou título de bloco sem linha: o antes/depois mostra a mudança
        bases = [('depois', U)]
        if ANTES:
            p2, srv2 = servir(ANTES); bases.append(('antes', lambda f, p2=p2: f'http://127.0.0.1:{p2}/{f}'))
        feitas = 0
        for w, h, toque in ((1440, 900, False), (390, 844, True)):   # todas as de 1440 antes de ligar o toque (que tira o hover da janela)
            for nome, base in bases:
                for f in telas:
                    abre(f, w, h, toque=toque, base=base); time.sleep(.7)
                    c.shot(os.path.join(PROBE, f"{nome}_{f.replace('.dc.html', '')}_{w}.png")); feitas += 1
        chk(f'F1 capturas em _probe/ds/ ({feitas}: {len(telas)} telas × 1440 e 390 px{" × antes/depois" if ANTES else ""})', feitas == len(telas) * 2 * len(bases), feitas)
        if ANTES:   # a captura "antes" tem de vir de outro _render: idênticas byte a byte = o antes não mostra nada
            import hashlib
            md = lambda n: hashlib.md5(open(os.path.join(PROBE, n), 'rb').read()).hexdigest()
            iguais = [f for f in telas if md(f"antes_{f.replace('.dc.html', '')}_1440.png") == md(f"depois_{f.replace('.dc.html', '')}_1440.png")]
            chk('F3 antes ≠ depois a 1440 px nas 6 telas (a linha nova aparece na captura)', not iguais, iguais)
    # ======================= E · 390 px com toque =======================
    if 'E' in PARTES:
        abre('SAF.dc.html', 390, 844, toque=True); n0 = nreal()
        J("(()=>{const r=[...document.querySelectorAll('main [role=row]')].find(r=>/Safra 2026\\/27/.test(r.innerText)); const b=[...r.querySelectorAll('button')].find(b=>/^Continuar/.test(b.innerText.trim())); b.click(); return 1;})()")
        time.sleep(.6); v = vivo(); rs = realces(n0)
        chk('E1 390 px · Planejar safra: etapa 2 realçada e anunciada', v.startswith('Etapa 2 de 4') and len(rs) >= 1, [v, rs])
        abre('OS.dc.html', 390, 844, toque=True)
        J("(()=>{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>/OS-0430/.test(r.innerText)); (r.querySelector('.g2pw')||r).click(); return 1;})()"); time.sleep(.5)
        clk('Liberar para execução', 'aside[role=dialog]'); time.sleep(.4); n1 = nreal(); clk('Confirmar liberação', 'aside[role=dialog]'); time.sleep(.7)
        t = toast(); v = vivo(); rs = realces(n1); fase = J("(()=>{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>/OS-0430/.test(r.innerText)); return r?r.innerText.replace(/\\s+/g,' '):'';})()")
        chk('E2 390 px · liberar a OS-0430 pela lista: a linha muda para Liberadas, o que mudou é realçado e o aviso é anunciado', 'Liberadas' in fase and len(rs) >= 1 and t and v.startswith(t.split(' | ')[0][:40]), [fase, t, v, rs])
        abre('BO-02.dc.html', 390, 844, toque=True)
        p = centro("[...document.querySelectorAll('header button')].find(x=>x.innerText.trim()==='Conciliar pagamentos')"); c.toque(p[0], p[1]); time.sleep(.6)
        t = toast(); p = centro("[...document.querySelectorAll('header button')].find(x=>x.innerText.trim()==='Conciliar pagamentos')")
        c.call('Input.dispatchTouchEvent', {'type': 'touchStart', 'touchPoints': [{'x': p[0], 'y': p[1]}]}); time.sleep(.75)
        c.call('Input.dispatchTouchEvent', {'type': 'touchEnd', 'touchPoints': []}); time.sleep(.4); d = J(DICA)
        ncon = J("Object.values(JSON.parse(localStorage.getItem('talhao-os-cenario-v1')).assin.recibos).filter(r=>/^CON-/.test(r.id)).length")
        chk('E3 390 px · toque: conciliar; toque longo no botão indisponível mostra a dica sem acionar o comando', 'CON-0001' in t and d['vis'] and 'Nenhum evento' in d['t'] and ncon == 1, [t, d, ncon])
        c.toque(200, 600); time.sleep(.3); d = J(DICA)
        chk('E4 390 px · tocar fora fecha a dica', not d['vis'], d)
        dd = J("(()=>{const d=document.getElementById('g2-dica'); return d?d.getBoundingClientRect().right<=innerWidth:true;})()")
        chk('E5 390 px · sem erro de execução e a dica cabe na tela', not errs() and dd, [errs(), dd])

    # ======================= G · motivo do indisponível visível em texto (PRD DS-06 e 74.5.0; VIS-04) =======================
    # "Causa, quem resolve e atalho ficam visíveis na própria tela, sem depender de passar o ponteiro": a dica complementa, não substitui.
    if 'G' in PARTES:
        MOT = r"""(()=>{const b=[...document.querySelectorAll('header button')].find(x=>x.innerText.trim()==='Conciliar pagamentos'); if(!b) return null;
          const d=document.getElementById('g2-dica'); const dv=!!d&&!d.hidden&&d.getClientRects().length>0; const rb=b.getBoundingClientRect();
          const m=[...document.querySelectorAll('header *')].filter(e=>e.getClientRects().length>0&&!b.contains(e)&&e.children.length===0&&/Nenhum evento do provedor a conciliar/.test(e.textContent))
            .map(e=>{const r=e.getBoundingClientRect(), s=getComputedStyle(e); return {t:e.textContent.trim(), cor:s.color, fs:parseFloat(s.fontSize),
              perto:Math.max(0,r.top-rb.bottom,rb.top-r.bottom)<=24&&Math.max(0,r.left-rb.right,rb.left-r.right)<=24, cabe:r.left>=0&&r.right<=innerWidth+0.5};});
          return {dis:b.getAttribute('aria-disabled'), dica:dv, m};})()"""
        for w, h, toque in ((1440, 900, False), (390, 844, True)):
            abre('BO-02.dc.html', w, h, toque=toque); m0 = J(MOT)
            chk(f'G1 {w} px · normal: com evento a conciliar, a primária está disponível e não há motivo de bloqueio', bool(m0) and m0['dis'] != 'true' and not m0['m'], m0)
            J("[...document.querySelectorAll('header button')].find(x=>x.innerText.trim()==='Conciliar pagamentos').click()"); time.sleep(.7)
            if not toque: fora()
            J("document.activeElement&&document.activeElement.blur&&document.activeElement.blur()"); time.sleep(.3); m1 = J(MOT)
            chk(f'G2 {w} px · tudo conciliado: o motivo fica visível em texto junto do botão (sem ponteiro, sem foco, sem dica aberta), na cor do texto secundário e dentro da tela',
                bool(m1) and m1['dis'] == 'true' and not m1['dica'] and len(m1['m']) == 1 and m1['m'][0]['cor'] == 'rgb(101, 115, 106)' and m1['m'][0]['fs'] >= 12
                and m1['m'][0]['perto'] and m1['m'][0]['cabe'], m1)
            J("[...document.querySelectorAll('header button')].find(x=>x.innerText.trim()==='Conciliar pagamentos').focus()"); time.sleep(.3)
            sob = J("""(()=>{const d=document.getElementById('g2-dica'), m=document.querySelector('header .g2motivo'); if(!d||d.hidden||!m) return null;
              const a=d.getBoundingClientRect(), b=m.getBoundingClientRect(); return {cobre:!(a.right<=b.left||b.right<=a.left||a.bottom<=b.top||b.bottom<=a.top), t:d.textContent};})()""")
            chk(f'G2b {w} px · a dica do botão (foco) abre fora do par botão + motivo: não cobre o motivo visível', bool(sob) and not sob['cobre'] and 'Nenhum evento' in sob['t'], sob)
            c.tecla('Escape', 'Escape', 27); J("document.activeElement&&document.activeElement.blur&&document.activeElement.blur()"); time.sleep(.2)
            n5 = nreal()
            if toque:
                p = centro("[...document.querySelectorAll('header button')].find(x=>x.innerText.trim()==='Conciliar pagamentos')"); c.toque(p[0], p[1])
            else: J("[...document.querySelectorAll('header button')].find(x=>x.innerText.trim()==='Conciliar pagamentos').click()")
            time.sleep(.5); v = vivo(); rs = realces(n5)
            chk(f'G3 {w} px · recusa: ativar o botão indisponível realça o motivo visível e anuncia "Indisponível: …"', any('Nenhum evento do provedor a conciliar' in x['txt'] for x in rs) and v.startswith('Indisponível: Nenhum evento'), [rs, v])
        chk('G4 sem erro de execução', not errs(), errs())

finally:
    try: c.close()
    finally:
        srv.terminate()
        if srv2: srv2.terminate()
        try: _proc.terminate(); _proc.wait(5)
        except Exception:
            try: _proc.kill()
            except Exception: pass
        import shutil; shutil.rmtree(_pdir, ignore_errors=True)
print('RESULTADO:', 'OK' if all(ok) else 'FALHOU', f'{sum(ok)}/{len(ok)}')
sys.exit(0 if all(ok) else 1)
