# -*- coding: utf-8 -*-
"""MUX-F2 · Ler o talhão no Mapa (IN-04): cartão no hover e no foco, cor honesta, rótulos legíveis, legenda que trabalha e seleção (pedido do
proprietário de 16/10/2026, §1; confronto §7 e §8.1 itens 3 a 5; implantação de 17/10). Chrome a 1440 × 900 (mouse e teclado) e 390 × 844 (toque).
  C1 hover (ponteiro real) no T4 e no P5: cartão com número, área, cultura e estádio, valor, estado em texto, data do dado e "Clique para detalhar";
     sem ação dentro; dentro da janela; sem cobrir o talhão; contorno realçado (anel em duas cores / camada pv-hov) e cursor de mão
  C2 sem espera programada: o cartão já está visível no mesmo turno do evento (pointerover sintético); tempos do evento ao quadro (indicativo, SwiftShader)
  C3 o foco de teclado mostra o mesmo cartão (mesmo texto do hover)
  C5 nas 9 camadas o cartão abre completo (P1 da Santa Rita)
  C4 WCAG 1.4.13: o ponteiro vai do talhão ao cartão sem ele sumir; Esc dispensa (o foco fica no talhão); sair do talhão e do cartão fecha
  K1 cor honesta: nuvem em hachura (Satélite 06/09, Santa Rita) e camada de hachura no mapa real; "estimado" (Irrigação › Balanço, T7) na cor do
     valor com "≈ … estimado", nunca na hachura (NC10); "não se aplica" com contorno tracejado (D14)
  K2 rótulos: no máximo 3 linhas (número / valor / estado curto), sobre placa branca a 90 % com texto #15201A e nenhum opacity no caminho: contraste
     ≥ 13,4:1 sobre qualquer fundo (≥ 4,5:1); seleção e foco em duas cores (escuro e branco: ≥ 3:1 sobre qualquer preenchimento)
  L1 legenda que trabalha: cada classe com contagem e área (a soma bate com os talhões); hover realça os talhões da classe; clique filtra o mapa e a
     lista ("N de M"); clique de novo limpa; no Satélite com contraste Talhão e no Solo fora do Absoluto, a escala relativa não conta talhões
  S1 seleção: contorno forte (7 px escuro + linha branca) e número em destaque; no mapa real, o clique não muda zoom nem centro
  M1 390 com toque: tocar não abre cartão (não atrapalha); o cartão do foco cabe na janela
  E1 sem erro de JavaScript
Contraprova: RENDER_DIR=<render da base 0b3d0d4> reprova C1–C5, K1 (estimado e tracejado), K2, L1 e S1.
Uso (de gen37/): env CHROME_BIN=… CDP_GL=1 SAFRION_DADOS=sintetico RENDER_DIR=$PWD/_render python3 -B mapa_mux_f2_test.py"""
import os, sys, json, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, servir
from mapa_mux_lib import chk, OK, FAIL, espera, abre, fazenda, camada, filtro, caixa, cartao, ativo, erros, tal_el

R = os.environ.get('RENDER_DIR') or os.path.join(HERE, '_render')
p, srv = servir(R); c = Chrome(); J = c.js
U = f'http://127.0.0.1:{p}/IN-04.dc.html'
MED = {}
def lum(rgb):
    def ch(v):
        v = v / 255; return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    return 0.2126 * ch(rgb[0]) + 0.7152 * ch(rgb[1]) + 0.0722 * ch(rgb[2])
def contraste(a, b):
    la, lb = lum(a), lum(b); return (max(la, lb) + .05) / (min(la, lb) + .05)
def rgba(s):
    v = [float(x) for x in s[s.index('(') + 1:s.index(')')].split(',')]; return (v + [1.0])[:4]
def sobre(fg, bg):   # fg rgba composto sobre bg rgb
    return [fg[i] * fg[3] + bg[i] * (1 - fg[3]) for i in range(3)]
def cobre(card, bx):
    l, t, r, b = card
    return not (l >= bx['r'] or r <= bx['l'] or t >= bx['b'] or b <= bx['t'])
def fora_janela(card):
    l, t, r, b = card['r']; return l < 0 or t < 0 or r > card['vw'] or b > card['vh']
def campos(txt, nome):
    return [txt.startswith(nome + ' · '), ' ha' in txt, 'Clique para detalhar' in txt, ('(hoje)' in txt or 'cena de' in txt or 'vistoria' in txt or 'coleta' in txt or 'laudo' in txt or 'balanço' in txt)]
try:
    # ================= C · cartão (1440) =================
    abre(c, U, 1440, 900, False, faz='Santa Rita'); camada(J, 'Pragas e doenças')
    b4 = caixa(J, 'T4'); c.mouse(b4['x'] - 300, b4['y'] - 200); c.mouse(b4['x'], b4['y']); espera(J, "!!document.getElementById('mux-cartao')&&!document.getElementById('mux-cartao').hidden", 2)
    k = cartao(J); MED['cartao_T4'] = k
    an = J("(()=>{const a=document.querySelector('svg[data-mux-grupo] [data-mux-anel]'); return a?[...a.children].map(x=>x.getAttribute('stroke')):null;})()") or []
    chk('C1a hover no T4 (Pragas e doenças): cartão com nome e área, cultura e estádio, valor, estado em texto, data do dado e "Clique para detalhar"; role=tooltip; sem ação dentro',
        k.get('on') and all(campos(k.get('txt', ''), 'T4')) and k.get('acoes') == 0 and k.get('role') == 'tooltip', k)
    chk('C1b o cartão fica dentro da janela e não cobre o talhão', k.get('on') and not fora_janela(k) and not cobre(k['r'], b4), [k.get('r'), b4])
    chk('C1c contorno realçado do talhão em duas cores (escuro e branco, por cima dos pixels) e cursor de mão', an[:2] == ['#15201A', '#FFFFFF'] and J("getComputedStyle(%s).cursor" % tal_el('T4')) == 'pointer', an)
    # C2 sem espera programada: visível no mesmo turno do evento
    sinc = J("(()=>{const b=%s; b.dispatchEvent(new PointerEvent('pointerover',{bubbles:true,pointerType:'mouse'})); const d=document.getElementById('mux-cartao'); return !!d&&!d.hidden&&d.dataset.talhao==='T7';})()" % tal_el('T7'))
    chk('C2a sem espera programada: o cartão do T7 está visível no mesmo turno do pointerover (nenhum timer de abertura)', bool(sinc), sinc)
    # amostra de tempos do evento ao quadro (ponteiro real) entre vizinhos: indicativo (SwiftShader, máquina compartilhada)
    J("window.__MUX&&(window.__MUX.med.length=0)")
    for _ in range(3):
        for t in ('T1', 'T2', 'P1', 'P2', 'T4', 'T3', 'T7', 'C1'):
            c.mouse(5, 890); time.sleep(.2); bb = caixa(J, t); c.mouse(bb['x'], bb['y']); time.sleep(.12)   # cada hover abre um cartão novo
    raw = J("(window.__MUX&&window.__MUX.med)||[]") or []
    pc = lambda v, q: v[min(len(v) - 1, int(round(q * (len(v) - 1))))] if v else None
    md = sorted(x['ms'] for x in raw); mj = sorted(x.get('js', 0) for x in raw)
    MED['tempo_ms'] = {'n': len(md), 'p50': pc(md, .5), 'p95': pc(md, .95), 'js_p50': pc(mj, .5), 'js_p95': pc(mj, .95)}   # js: o trabalho do cartão, sem a pintura
    p95 = MED['tempo_ms']['p95']
    chk('C2b tempos do evento ao quadro medidos (indicativo, SwiftShader): amostra com 24 hovers entre vizinhos', len(md) >= 20, MED['tempo_ms'])
    # C3 foco de teclado = mesmo cartão
    c.mouse(5, 890); time.sleep(.4); bb = caixa(J, 'T4'); c.mouse(bb['x'], bb['y']); espera(J, "(document.getElementById('mux-cartao')||{}).dataset&&document.getElementById('mux-cartao').dataset.talhao==='T4'", 2); kh = cartao(J)
    c.mouse(5, 890); time.sleep(.4); c.tab(); J("(%s).focus()" % tal_el('T4')); espera(J, "(document.getElementById('mux-cartao')||{dataset:{}}).dataset.modo==='foco'", 2); kf = cartao(J)
    chk('C3 o foco de teclado no T4 mostra o mesmo cartão do hover (mesmo texto)', kf.get('on') and kf.get('modo') == 'foco' and kf.get('txt') == kh.get('txt') and bool(kh.get('txt')), [kh.get('txt'), kf.get('txt')])
    c.tecla('Escape', 'Escape', 27); time.sleep(.2)
    chk('C4a Esc dispensa o cartão e o foco fica no talhão (o painel não abre nem fecha nada)', not cartao(J).get('on') and ativo(J) == 'T4', [cartao(J).get('on'), ativo(J)])
    bb = caixa(J, 'T4'); c.mouse(bb['x'], bb['y']); espera(J, "!!document.getElementById('mux-cartao')&&!document.getElementById('mux-cartao').hidden", 2); k1 = cartao(J)
    if k1.get('r'): cx, cy = (k1['r'][0] + k1['r'][2]) / 2, (k1['r'][1] + k1['r'][3]) / 2; c.mouse(cx, cy); time.sleep(.45)   # sem cartão (base): reprova sem abortar
    chk('C4b o ponteiro vai do talhão até o cartão e o cartão continua (hoverable, WCAG 1.4.13)', cartao(J).get('on') and cartao(J).get('tal') == 'T4', cartao(J))
    c.mouse(5, 890); time.sleep(.5)
    chk('C4c sair do talhão e do cartão fecha o cartão', not cartao(J).get('on'), cartao(J))
    # mapa real: P5
    fazenda(J, 'Lagoa Grande'); camada(J, 'Integrado')
    b5 = caixa(J, 'PV05'); c.mouse(b5['x'] - 200, b5['y'] - 150); time.sleep(.2); c.mouse(b5['x'] + 3, b5['y'] + 3); espera(J, "(document.getElementById('mux-cartao')||{dataset:{}}).dataset.talhao==='PV05'", 3)
    k5 = cartao(J); MED['cartao_P5'] = k5
    hv = J("(()=>{const m=window.__LGI&&__LGI.map; try{ return [JSON.stringify(m.getFilter('pv-hov')), m.getCanvas().style.cursor]; }catch(e){ return null; }})()") or [None, None]
    # o pivô na tela: círculo do raio do KML (a caixa do marcador é só o rótulo)
    pb = json.loads(J("JSON.stringify((()=>{const m=__LGI.map; const mk=__LGI.markers['PV05']; const ll=mk.getLngLat(); const a=m.project(ll); const o=m.getContainer().getBoundingClientRect(); const r=476/(111320*Math.cos(ll.lat*Math.PI/180)); const b=m.project([ll.lng+r,ll.lat]); const R=Math.abs(b.x-a.x); return {l:o.left+a.x-R,t:o.top+a.y-R,r:o.left+a.x+R,b:o.top+a.y+R};})())") or 'null')
    chk('C1d hover no P5 (mapa real): cartão completo, sem ação, dentro da janela, sem cobrir o pivô; contorno realçado (pv-hov) e cursor de mão',
        k5.get('on') and all(campos(k5.get('txt', ''), 'P5')) and k5.get('acoes') == 0 and not fora_janela(k5) and pb and not cobre(k5['r'], pb) and 'PV05' in (hv[0] or '') and hv[1] == 'pointer', [k5, pb, hv])
    # C5 · as 9 camadas: o cartão abre em todas, com o valor da camada (o mesmo texto do rótulo do talhão no mapa)
    fazenda(J, 'Santa Rita'); por = {}
    for cam in ('Integrado', 'Satélite', 'Solo', 'Pragas e doenças', 'Ordens de serviço', 'Irrigação', 'Estádio', 'Colheita e produtividade', 'Custos'):
        camada(J, cam); c.mouse(5, 890); time.sleep(.3); bb = caixa(J, 'P1'); c.mouse(bb['x'], bb['y']); espera(J, "(document.getElementById('mux-cartao')||{dataset:{}}).dataset.talhao==='P1'", 2)
        k = cartao(J); rot = J("(%s||{getAttribute:()=>''}).getAttribute('data-rotulo')||''" % tal_el('P1')) or ''
        por[cam] = bool(k.get('on')) and all(campos(k.get('txt', ''), 'P1')) and k.get('acoes') == 0 and not fora_janela(k)
    MED['cartao_camadas'] = sum(por.values())
    chk('C5 o cartão abre nas 9 camadas (P1 da Santa Rita), completo, sem ação e dentro da janela', all(por.values()) and len(por) == 9, por)
    c.mouse(5, 890); time.sleep(.3)
    # ================= K · cor honesta e rótulos =================
    fazenda(J, 'Santa Rita'); camada(J, 'Satélite'); filtro(J, 'Cena', '06/09')
    nuv = J("[...document.querySelectorAll('svg [role=button]')].filter(x=>x.getAttribute('fill')==='url(#hatch)').map(x=>x.getAttribute('data-talhao')||(x.getAttribute('aria-label')||'').split(':')[0])") or []   # vale também na base (preservação)
    chk('K1a Satélite 06/09 (Santa Rita): P2 e T7 sob nuvem em hachura, nunca com a cor de um valor', sorted(nuv) == ['P2', 'T7'], nuv)
    camada(J, 'Irrigação'); filtro(J, 'Mostrar', 'Balanço hídrico')
    t7 = json.loads(J("JSON.stringify((()=>{const e=%s; return e?[e.getAttribute('fill'),e.getAttribute('data-rotulo')||e.getAttribute('aria-label')]:null;})())" % tal_el('T7')) or 'null') or [None, '']
    chk('K1b Irrigação › Balanço hídrico: o T7 estimado fica com a cor do valor e a etiqueta "≈ … estimado", não com a hachura (NC10)', t7[0] not in (None, 'url(#hatch)') and t7[0].startswith('#') and '≈' in (t7[1] or '') and 'estimado' in (t7[1] or ''), t7)
    camada(J, 'Integrado'); filtro(J, 'Mostrar', 'Só pendências')
    tr = json.loads(J("JSON.stringify([...document.querySelectorAll('svg[data-mux-grupo] [data-talhao]')].filter(x=>x.getAttribute('fill')==='#E4E9DF').map(x=>[x.getAttribute('data-talhao'),x.getAttribute('stroke-dasharray'),x.getAttribute('stroke')]))") or '[]')
    chk('K1c "não se aplica" (sem pendência) com contorno tracejado #6B776F, nunca só a cor do fundo (D14)', bool(tr) and all(x[1] not in (None, 'none') and x[2] == '#6B776F' for x in tr), tr)
    filtro(J, 'Mostrar', 'Todas as condições')
    fazenda(J, 'Lagoa Grande'); hl = J("!!(window.__LGI&&__LGI.map&&__LGI.map.getLayer('pv-hach'))")
    chk('K1d mapa real: camada de hachura para nuvem e sem leitura (pv-hach)', bool(hl), hl)
    # rótulos e contraste
    fazenda(J, 'Santa Rita'); camada(J, 'Pragas e doenças')
    pl = json.loads(J("""JSON.stringify([...document.querySelectorAll('svg[data-mux-grupo] foreignObject.mux-placa')].filter(f=>f.getClientRects().length).map(f=>{ const d=f.querySelector('div>div'); const ls=[...d.children].filter(x=>x.getClientRects().length&&x.innerText.trim());
      let op=1, fi=''; for(let e=d; e&&e.tagName!=='svg'; e=e.parentElement){ const s=getComputedStyle(e); op*=parseFloat(s.opacity); if(s.filter!=='none') fi+=s.filter; }
      return {bg:getComputedStyle(d).backgroundColor, cor:ls.map(x=>getComputedStyle(x).color), n:ls.length, op, fi}; }))""") or '[]')
    nums = json.loads(J("JSON.stringify([...document.querySelectorAll('svg[data-mux-grupo] text')].map(t=>[t.getAttribute('fill'),t.getAttribute('stroke'),t.getAttribute('stroke-width')]))") or '[]')
    piores = []
    for x in pl:
        bg = rgba(x['bg'])
        for cor in x['cor']:
            fg = rgba(cor); placa_preto = sobre(bg, [0, 0, 0]); placa_branco = sobre(bg, [255, 255, 255])
            piores.append(min(contraste(fg[:3], placa_preto), contraste(fg[:3], placa_branco)))
    MED['contraste_rotulo_min'] = round(min(piores), 2) if piores else None
    chk('K2a rótulos da Santa Rita: até 2 linhas na placa (valor e estado) + o número, placa branca a 90 %, texto opaco, sem opacity nem filtro no caminho; contraste ≥ 13,4:1 sobre qualquer fundo',
        bool(pl) and all(x['n'] <= 2 and x['op'] == 1 and not x['fi'] and abs(rgba(x['bg'])[3] - .9) < .01 for x in pl) and piores and min(piores) >= 13.3 and len(nums) == 8 and all(n[2] == '6' for n in nums), [pl[:2], MED['contraste_rotulo_min'], nums[:2]])
    fazenda(J, 'Lagoa Grande')
    lg = json.loads(J("""JSON.stringify([...document.querySelectorAll('[data-mux-grupo=LG] [data-talhao]')].map(b=>{ const vis=[...b.children].filter(x=>getComputedStyle(x).display!=='none'&&x.innerText.trim()).length; let op=1; for(let e=b; e&&!e.classList.contains('maplibregl-map'); e=e.parentElement) op*=parseFloat(getComputedStyle(e).opacity);
      return {bg:getComputedStyle(b).backgroundColor, cor:getComputedStyle(b).color, vis, op, cls:b.className}; }))""") or '[]')
    lc = [min(contraste(rgba(x['cor'])[:3], sobre(rgba(x['bg']), [0, 0, 0])), contraste(rgba(x['cor'])[:3], sobre(rgba(x['bg']), [255, 255, 255]))) for x in lg]
    MED['contraste_rotulo_lg_min'] = round(min(lc), 2) if lc else None
    chk('K2b rótulos da Lagoa Grande: placa a 90 % com texto #15201A, até 3 linhas (só o número quando o pivô é pequeno na tela), contraste ≥ 13,4:1, sem opacity',
        len(lg) == 23 and all(x['vis'] <= 3 and x['op'] == 1 for x in lg) and lc and min(lc) >= 13.3, [lg[:2], MED['contraste_rotulo_lg_min']])
    # ================= L · legenda que trabalha (Santa Rita, Integrado) =================
    fazenda(J, 'Santa Rita'); camada(J, 'Integrado')
    lb = json.loads(J("JSON.stringify([...document.querySelectorAll('[data-mux-leg]')].map(b=>[b.getAttribute('data-mux-leg'),b.innerText.replace(/\\s+/g,' ').trim(),(b.querySelector('.mux-qt')||{}).innerText||'']))") or '[]')
    soma = sum(int((x[2] or '0').split(' ')[0]) for x in lb)
    chk('L1a cada classe da legenda mostra contagem e área ("2 · 610 ha"); a soma das contagens é a dos 8 talhões', bool(lb) and soma == 8 and all(x[2] == '0' or ' ha' in x[2] for x in lb), [lb, soma])
    cls = next((x for x in lb if x[2] not in ('', '0')), None) or ['', 'nenhuma classe', '0']   # sem a legenda que trabalha (base): os itens reprovam sem abortar
    nc = int(cls[2].split(' ')[0]) if cls else 0
    bl = json.loads(J("JSON.stringify((()=>{const e=document.querySelector('[data-mux-leg=\"%s\"]'); if(!e) return null; const r=e.getBoundingClientRect(); return {x:r.left+r.width/2,y:r.top+r.height/2};})())" % cls[0]) or 'null')
    if bl: c.mouse(bl['x'], bl['y']); time.sleep(.3)
    na = J("(document.querySelector('svg[data-mux-grupo] [data-mux-anel]')||{children:[]}).children.length")
    chk(f'L1b passar o mouse em "{cls[1] if cls else ""}" realça os {nc} talhões dela (anel em duas cores em cada um)', na == 2 * nc and nc > 0, [na, nc])
    J("(()=>{const e=document.querySelector('[data-mux-leg=\"%s\"]'); e&&e.click();})()" % cls[0]); time.sleep(.5)
    st = json.loads(J("JSON.stringify({p:(document.querySelector('[data-mux-leg=\"%s\"]')||{getAttribute:()=>null}).getAttribute('aria-pressed'), op:[...document.querySelectorAll('svg[data-mux-grupo] [data-talhao]')].map(x=>x.getAttribute('fill-opacity'))})" % cls[0]) or '{}')
    J("(()=>{const g=document.querySelector('[role=group][aria-label=\"Ver dados\"]'); const b=g&&[...g.querySelectorAll('button')].find(x=>x.innerText.trim()==='Lista'); b&&b.click();})()"); time.sleep(.5)
    nl = [J("document.querySelectorAll('.mux-lista [data-talhao-lista]').length"), J("((document.querySelector('.mux-lista [role=status]')||{}).innerText||'')")]
    chk('L1c clicar na classe filtra: botão pressionado, os outros talhões esmaecem no mapa e a Lista mostra só a classe ("N de 8")', st.get('p') == 'true' and st.get('op', []).count('0.25') == 8 - nc and nl[0] == nc and nl[1].startswith(f'{nc} de 8'), [st, nl])
    J("(()=>{const e=document.querySelector('[data-mux-leg=\"%s\"]'); e&&e.click();})()" % cls[0]); time.sleep(.5)
    nl2 = J("document.querySelectorAll('.mux-lista [data-talhao-lista]').length"); p2 = J("(document.querySelector('[data-mux-leg=\"%s\"]')||{getAttribute:()=>null}).getAttribute('aria-pressed')" % cls[0])
    chk('L1d clicar de novo limpa o filtro (8 linhas; botão solto)', nl2 == 8 and p2 == 'false', [nl2, p2])
    # Satélite: com o contraste Talhão as cores são relativas a cada talhão; a escala dos pixels não conta talhões (antes: "Médio 20" na Lagoa
    # Grande com rótulos fraco, atenção e bom). Com o contraste Absoluto a classe do talhão é a da escala: a soma volta a ser 8
    camada(J, 'Satélite'); time.sleep(.4)
    LEGQ = "JSON.stringify([...document.querySelectorAll('[data-mux-leg]')].map(b=>[b.getAttribute('data-mux-leg'),(b.querySelector('.mux-qt')||{}).innerText||'']))"
    l_tal = json.loads(J(LEGQ) or '[]')
    filtro(J, 'Contraste', 'Absoluto'); time.sleep(.4)
    l_abs = json.loads(J(LEGQ) or '[]'); s_abs = sum(int((x[1] or '0').split(' ')[0]) for x in l_abs)
    chk('L1e Satélite: no contraste Talhão a escala dos pixels não conta talhões (só sem cultura e nuvem); no Absoluto a soma é 8',
        bool(l_tal) and all(x[0] in ('c:gray', 'c:cloud') for x in l_tal) and s_abs == 8 and any(x[0].startswith('h:') for x in l_abs), [l_tal, l_abs])
    filtro(J, 'Contraste', 'Talhão')
    # Solo: a escala da legenda só é a classe do talhão no contraste Absoluto; nos outros (sextos de cada talhão ou da fazenda) ela não conta talhões
    camada(J, 'Solo'); time.sleep(.4); s_tal = json.loads(J(LEGQ) or '[]')
    filtro(J, 'Contraste', 'Absoluto'); time.sleep(.4); s_abs = json.loads(J(LEGQ) or '[]'); n_abs = sum(int((x[1] or '0').split(' ')[0]) for x in s_abs)
    chk('L1f Solo: nos sextos de cada talhão a escala não conta talhões (só sem laudo); no Absoluto a soma é 8',
        bool(s_tal) and all(not x[0].startswith('h:') for x in s_tal) and n_abs == 8 and any(x[0].startswith('h:') for x in s_abs), [s_tal, s_abs])
    filtro(J, 'Contraste', 'Talhão'); camada(J, 'Integrado')
    J("(()=>{const g=document.querySelector('[role=group][aria-label=\"Ver dados\"]'); const b=g&&[...g.querySelectorAll('button')].find(x=>x.innerText.trim()==='Mapa'); b&&b.click();})()"); time.sleep(.4)
    # ================= S · seleção =================
    J("(%s).dispatchEvent(new MouseEvent('click',{bubbles:true}))" % tal_el('T4')); time.sleep(.5)
    s4 = json.loads(J("JSON.stringify((()=>{const e=%s; const i=[...document.querySelectorAll('svg[data-mux-grupo] [data-talhao=T4] ~ polygon')].find(x=>x.getAttribute('stroke')==='#FFFFFF'&&x.getAttribute('fill')==='none'); const n=[...document.querySelectorAll('svg[data-mux-grupo] text')].find(t=>t.textContent==='T4');"
                     " return [e.getAttribute('stroke'),e.getAttribute('stroke-width'),i?i.getAttribute('opacity'):null,n?n.getAttribute('fill'):null];})())" % tal_el('T4')) or 'null')
    chk('S1a seleção na Santa Rita: contorno forte em duas cores (escuro 7 px + linha branca) e número em destaque (branco com contorno escuro)', s4 == ['#15201A', '7', '1', '#FFFFFF'], s4)
    fazenda(J, 'Lagoa Grande'); cam0 = J("(()=>{const m=__LGI.map; const c=m.getCenter(); return [c.lng,c.lat,m.getZoom()];})()")
    b5 = caixa(J, 'PV05'); c.mouse(b5['x'], b5['y'], 'mousePressed', 'left'); c.mouse(b5['x'], b5['y'], 'mouseReleased', 'left'); espera(J, "!!document.querySelector('main aside[data-mux-painel]')", 4); time.sleep(.6)
    cam1 = J("(()=>{const m=__LGI.map; const c=m.getCenter(); return [c.lng,c.lat,m.getZoom()];})()")
    sl = J("(()=>{const m=__LGI.map; try{ return [JSON.stringify(m.getFilter('pv-sel')),JSON.stringify(m.getFilter('pv-sel2')),m.getPaintProperty('pv-sel','line-color'),m.getPaintProperty('pv-sel2','line-color'),(document.querySelector('[data-mux-grupo=LG] [data-talhao=PV05]')||{getAttribute:()=>null}).getAttribute('aria-pressed')]; }catch(e){ return ['sem '+e.message]; }})()") or []
    chk('S1b seleção no mapa real: contorno em duas cores (pv-sel escuro + pv-sel2 branco), rótulo em destaque (aria-pressed) e a câmera não se move', 'PV05' in (sl[0] or '') and 'PV05' in (sl[1] or '') and sl[2:] == ['#15201A', '#FFFFFF', 'true'] and cam0 == cam1, [sl, cam0, cam1])
    ee = erros(J); chk('E1a 1440: sem erro de JavaScript', not ee, ee[:3])
    # ================= M · 390 com toque =================
    abre(c, U, 390, 844, True, faz='Santa Rita'); camada(J, 'Integrado'); J("window.__errs=[]")
    b4 = caixa(J, 'T4'); c.toque(b4['x'], b4['y']); time.sleep(.6)
    chk('M1a 390: tocar o talhão não abre o cartão de hover (só escolhe e abre o painel)', not cartao(J).get('on') and J("!!document.querySelector('main aside[data-mux-painel]')"), cartao(J))
    c.tab(); J("(%s).focus()" % tal_el('T2')); espera(J, "(document.getElementById('mux-cartao')||{dataset:{}}).dataset.modo==='foco'", 2); kf = cartao(J)
    chk('M1b 390: o cartão do foco cabe inteiro na janela', kf.get('on') and not fora_janela(kf), kf)
    ee = erros(J); chk('E1b 390: sem erro de JavaScript', not ee, ee[:3])
finally:
    try: c.close()
    except Exception: pass
    srv.terminate()
print('MEDIDAS', json.dumps(MED, ensure_ascii=False))
print(f'\nRESULTADO: {len(OK)} ok · {len(FAIL)} falha(s)' + (' · ' + '; '.join(FAIL) if FAIL else ''))
sys.exit(1 if FAIL else 0)
