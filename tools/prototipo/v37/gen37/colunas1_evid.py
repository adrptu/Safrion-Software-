# -*- coding: utf-8 -*-
"""COLUNAS-1 · evidência por tela (pedido do proprietário de 10/10; AUDITORIA COLUNAS §4.2), executada no navegador (Chrome headless, emulação).
Para cada tela do lote, num _render montado (antes = base 7e3d0d2; depois = esta branch):
- cabeçalhos de cada grade visível e largura de rolagem lateral da caixa (scrollWidth − clientWidth da .g2rola) a 1440 × 900 e 390 × 844;
- captura (JPEG) a 1440 × 900 e 390 × 844 com a 1ª grade da tela à vista;
- comportamento a 1440 (só com --comportamento): ordenar pela 2ª coluna, filtrar a coluna escolhida, abrir o detalhe e voltar (filtro, ordem,
  rolagem e foco na linha preservados); teclado: Tab da busca até uma linha, seta para baixo, Enter abre o detalhe, Esc fecha.
Uso (de gen37/): python3 colunas1_evid.py <pasta _render> <rótulo> <pasta de saída> [--comportamento]
Saída: <saída>/<rótulo>.json e <saída>/<rótulo>-<tela>-<largura>.jpg"""
import sys, os, time, json, base64
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, servir
REND, ROT, OUT = sys.argv[1], sys.argv[2], sys.argv[3]; COMP = '--comportamento' in sys.argv
os.makedirs(OUT, exist_ok=True)
# tela: (página, hash, perfil, preparo JS, coluna do filtro, rid preferido para abrir o detalhe)
ATIVO_ORDENS = "(()=>{const s=document.querySelector('section.ma-bl[aria-label=Ordens]'); const b=s&&s.querySelector('button.ma-blh'); if(b&&b.getAttribute('aria-expanded')!=='true') b.click(); return !!s;})()"
ATIVO_MARCA = "(()=>{const s=document.querySelector('section.ma-bl[aria-label=Ordens]'); const t=s&&s.querySelector('[role=table]'); if(t) t.setAttribute('data-evid','1'); return !!t;})()"
TELAS = [
    ('MA-semordem', 'MA.dc.html', 'vis=semordem', 'Otávio', None, 'Prazo', None),
    ('MA-ordens', 'MA.dc.html', 'vis=ordens', 'Otávio', None, 'Fase', None),
    ('MA-ativos', 'MA.dc.html', 'vis=ativos', 'Otávio', None, 'Condição', None),
    ('MA-abastecimentos', 'MA.dc.html', 'vis=ativos&modo=abastecimentos', 'Otávio', None, 'Qualidade', None),
    ('MA-planos', 'MA.dc.html', 'vis=planos', 'Otávio', None, 'Estado', None),
    ('MA-ativo-d_om', 'MA.dc.html', 'ativo=a01', 'Otávio', ATIVO_ORDENS, None, None),
    ('CA-01det', 'CA-01det.dc.html', '', None, None, 'Conferência', None),
    ('CA-01x', 'CA-01x-os0420.dc.html', '', None, None, None, None),
    ('CA-02', 'CA-02.dc.html', '', None, None, 'Conferência', 'f2'),
    ('CA-03', 'CA-03.dc.html', '', None, None, 'Gravidade', None),
    ('ON-01', 'ON-01.dc.html', '', None, None, 'Estado', None),
    ('ON-01det', 'ON-01det.dc.html', '', None, None, 'Estado', None),
    ('SAF-1', 'SAF.dc.html', 'saf=S2627&passo=safra', None, None, 'Estado', None),
    ('SAF-2', 'SAF.dc.html', 'saf=S2627&passo=cultivos', None, None, 'Cultura', None),
    ('SAF-3-g_op', 'SAF.dc.html', 'saf=S2627&passo=operacoes', None, None, 'Conjunto', 'op:Pulverização'),
]
p, srv = servir(REND); c = Chrome(); J = c.js; NAV = [0]; RES = {}
def abre(pag, h, w, hh, toque, perfil):
    NAV[0] += 1; c.aparelho(w, hh, 1, toque)
    c.goto(f'http://127.0.0.1:{p}/Main.dc.html', .3); J("localStorage.clear(); sessionStorage.clear()")
    if perfil: J(f"localStorage.setItem('safrion.perfilDemo',{json.dumps(perfil)})")
    c.goto(f'http://127.0.0.1:{p}/{pag}?r={NAV[0]}' + (('#' + h) if h else ''), 1.0); time.sleep(.6)
GRADES = """(()=>{const N=s=>(s||'').replace(/[⇅▾▴▲▼]/g,'').replace(/\\s+/g,' ').trim(); const ts=[...document.querySelectorAll('[role=table]')].filter(t=>t.offsetParent);
  const pg=[document.documentElement.scrollWidth,innerWidth];
  return {pagina:pg, grades:ts.map(t=>{const r=t.closest('.g2rola'); const c0=(t.querySelector('[role=row][data-rid] .g2c0')||t.querySelector('[role=row][data-rid] [role=cell]'));
    return {cols:[...t.querySelectorAll('[role=columnheader]')].map(h=>N(h.innerText)).filter(Boolean), linhas:t.querySelectorAll('[role=row][data-rid]').length,
            sw:r?r.scrollWidth:t.scrollWidth, cw:r?r.clientWidth:t.clientWidth, rola:r?Math.max(0,r.scrollWidth-r.clientWidth):0, c0preso:!!c0&&getComputedStyle(c0).position==='sticky'};})};})()"""
ALVO = "(document.querySelector('[role=table][data-evid]')||[...document.querySelectorAll('[role=table]')].find(t=>t.offsetParent))"
def foto(nome):
    J(f"(()=>{{const t={ALVO}; if(t){{const s=t.closest('section')||t; s.scrollIntoView({{block:'start'}});}}}})()"); time.sleep(.35)
    d = c.call('Page.captureScreenshot', {'format': 'jpeg', 'quality': 55, 'captureBeyondViewport': False})
    open(os.path.join(OUT, nome), 'wb').write(base64.b64decode(d['data']))
def rids(): return J(f"(()=>{{const t={ALVO}; return t?[...t.querySelectorAll('[role=row][data-rid]')].filter(r=>r.offsetParent).map(r=>r.getAttribute('data-rid')):[];}})()") or []
def detalhe_aberto(): return bool(J("!![...document.querySelectorAll('aside[role=dialog],#ma-painel[aria-modal=true]')].find(x=>x.getClientRects().length)"))   # o painel da MA é fixo (offsetParent nulo); o aberto ao lado (não modal) não conta
def pagina_det(): return J("(()=>{const b=[...document.querySelectorAll('main button')].find(b=>b.offsetParent&&/^‹ /.test(b.innerText.trim())); return b?b.innerText.trim():'';})()") or ''   # MA: a linha de Ativos e de Planos abre a página do registro
def volta_pagina():
    t = pagina_det()
    if t: J(f"[...document.querySelectorAll('main button')].find(b=>b.offsetParent&&b.innerText.trim()==={json.dumps(t)}).click()"); time.sleep(.7)
    return t
def foco(): return J("(()=>{const e=document.activeElement; if(!e) return ''; const r=e.closest&&e.closest('[role=row][data-rid]'); return r?'row:'+r.getAttribute('data-rid'):(e.tagName+(e.getAttribute('aria-label')?'['+e.getAttribute('aria-label')+']':''));})()") or ''
def rolagem(): return J("(()=>{const m=[document.scrollingElement,...document.querySelectorAll('main,[data-scroll],.g2rola')].filter(Boolean).map(e=>e.scrollTop); return m;})()")
def comportamento(nome, fcol, rid0, ocol=None):
    R = {}
    try:
        h = J(f"(()=>{{const t={ALVO}; const b=[...t.querySelectorAll('button.g2hb')]; return b.map(x=>x.getAttribute('aria-label'));}})()") or []
        R['ordenacao_botoes'] = len(h)
        r0 = rids()
        oi = next((i for i, x in enumerate(h) if ocol and x == 'Ordenar por ' + ocol), 1)
        if len(h) > 1:
            J(f"(()=>{{const t={ALVO}; t.querySelectorAll('button.g2hb')[{oi}].click();}})()"); time.sleep(.5)
            r1 = rids(); R['ordenar'] = {'coluna': h[oi], 'mudou_ordem': r1 != r0 and sorted(r1) == sorted(r0), 'mesmas_linhas': sorted(r1) == sorted(r0)}
        if fcol:
            J(f"(()=>{{const t={ALVO}; const b=t.querySelector('button.g2fb[aria-label=\"Filtrar {fcol}\"]'); b&&b.click();}})()"); time.sleep(.4)
            ops = J("[...document.querySelectorAll('[role=dialog] label')].filter(l=>l.offsetParent&&l.querySelector('input[type=checkbox]')).map(l=>l.innerText.replace(/\\s+/g,' ').trim())") or []
            if ops:
                J("[...document.querySelectorAll('[role=dialog] button')].find(b=>b.innerText.trim()==='Limpar').click()"); time.sleep(.2)
                J("(()=>{const l=[...document.querySelectorAll('[role=dialog] label')].filter(l=>l.offsetParent&&l.querySelector('input[type=checkbox]'))[0]; l&&l.querySelector('input').click();})()"); time.sleep(.2)
                J("[...document.querySelectorAll('[role=dialog] button')].find(b=>b.innerText.trim()==='OK').click()"); time.sleep(.5)
            rf = rids(); R['filtrar'] = {'coluna': fcol, 'valor': (ops or [''])[0], 'linhas_antes': len(r0), 'linhas_depois': len(rf), 'corta': 0 < len(rf) <= len(r0)}
        else:
            rf = rids()
        alvo = rid0 if rid0 in rf else (rf[0] if rf else None)
        if alvo:
            J(f"window.scrollTo(0,120)"); s0 = rolagem()
            J(f"""(()=>{{const r=[...document.querySelectorAll('[role=row][data-rid]')].find(r=>r.getAttribute('data-rid')==={json.dumps(alvo)}&&r.offsetParent); const z=[...r.querySelectorAll('[role=cell]')].find(z=>z.innerText.trim()&&!z.querySelector('button,a,input')); (z||r).click();}})()"""); time.sleep(.7)
            pg = '' if detalhe_aberto() else pagina_det()
            ab = detalhe_aberto() or bool(pg); txt = J("(()=>{const a=[...document.querySelectorAll('aside[role=dialog],#ma-painel[aria-modal=true]')].find(x=>x.getClientRects().length); return a?a.innerText.replace(/\\s+/g,' ').slice(0,400):'';})()") or ''
            if pg: volta_pagina()
            else: c.tecla('Escape', 'Escape', 27); time.sleep(.5)
            if detalhe_aberto():
                J("(()=>{const a=[...document.querySelectorAll('aside[role=dialog]')].find(x=>x.offsetParent); const b=a&&[...a.querySelectorAll('button')].find(b=>b.getAttribute('aria-label')==='Fechar'); b&&b.click();})()"); time.sleep(.4)
            R['detalhe'] = {'linha': alvo, 'abriu': ab, 'pagina': pg, 'trecho': txt[:240], 'fechou': not detalhe_aberto(), 'filtro_e_ordem_preservados': rids() == rf, 'rolagem_antes': s0, 'rolagem_depois': rolagem()}
        # teclado: Tab a partir da busca da grade (ou do 1º cabeçalho) até uma linha; seta; Enter; Esc
        J(f"(()=>{{const t={ALVO}; const cx=t.closest('.g2caixa'); const s=cx&&cx.querySelector('input[type=search]'); (s||t.querySelector('button.g2hb')).focus();}})()")
        n = 0; ok = False
        for n in range(1, 60):
            c.tab(1); time.sleep(.04)
            if foco().startswith('row:'): ok = True; break
        K = {'tabs_ate_linha': n if ok else None, 'linha_focada': foco()}
        if ok:
            f1 = foco(); c.tecla('ArrowDown', 'ArrowDown', 40); time.sleep(.3); K['seta_baixo'] = {'antes': f1, 'depois': foco()}
            J(f"(()=>{{const r=[...document.querySelectorAll('[role=row][data-rid]')].find(r=>r.getAttribute('data-rid')==={json.dumps(f1[4:])}&&r.offsetParent); r&&r.focus();}})()")
            c.tecla('Enter', 'Enter', 13); time.sleep(.7); pg = '' if detalhe_aberto() else pagina_det(); K['enter_abre'] = detalhe_aberto() or bool(pg); K['foco_apos_enter'] = foco()
            if pg:   # página do registro (MA): volta pelo "‹ …" e o foco deve voltar à linha
                volta_pagina(); K['pagina'] = pg; K['esc_fecha'] = None; K['foco_depois_volta'] = foco(); K['foco_volta_linha'] = foco() == f1; R['teclado'] = K; return R
            # o painel da G2 não toma o foco ao abrir: o 1º Tab entra nele (o Tab fica preso no painel modal) e só então o Esc o fecha
            if K['enter_abre'] and not J("!!(document.activeElement&&document.activeElement.closest&&document.activeElement.closest('aside[role=dialog],#ma-painel'))"):
                c.tab(1); time.sleep(.2); K['tab_entra_no_detalhe'] = bool(J("!!(document.activeElement&&document.activeElement.closest&&document.activeElement.closest('aside[role=dialog],#ma-painel'))"))
            c.tecla('Escape', 'Escape', 27); time.sleep(.6); K['esc_fecha'] = not detalhe_aberto(); K['foco_depois_esc'] = foco(); K['foco_volta_linha'] = foco() == f1
        R['teclado'] = K
    except Exception as e:
        R['erro'] = str(e)[:300]
    return R
try:
    for nome, pag, h, perfil, prep, fcol, rid0 in TELAS:
        RES[nome] = {}
        for w, hh, toque in ((1440, 900, False), (390, 844, True)):
            abre(pag, h, w, hh, toque, perfil)
            if prep: J(prep); time.sleep(.5); J(ATIVO_MARCA)
            RES[nome][f'{w}'] = J(GRADES); foto(f'{ROT}-{nome}-{w}.jpg')
        if COMP:
            abre(pag, h, 1440, 900, False, perfil)
            if prep: J(prep); time.sleep(.5); J(ATIVO_MARCA)
            RES[nome]['comportamento'] = comportamento(nome, fcol, rid0, {'SAF-3-g_op': 'Custo R$/ha', 'MA-ordens': 'Janela', 'CA-02': 'Apontamento'}.get(nome))
        g = RES[nome]['1440']['grades']; print(nome, [(len(x['cols']), x['rola']) for x in g], '| 390:', [(len(x['cols']), x['rola']) for x in RES[nome]['390']['grades']], flush=True)
finally:
    json.dump(RES, open(os.path.join(OUT, ROT + '.json'), 'w'), ensure_ascii=False, indent=1)
    c.close(); srv.terminate()
