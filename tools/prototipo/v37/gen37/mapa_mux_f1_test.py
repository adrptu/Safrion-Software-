# -*- coding: utf-8 -*-
"""MUX-F1 · Achar e abrir o talhão no Mapa (IN-04), aceite da §8.2 de docs/integracao/V73/MAPA-UX/confronto-claude-codex.md (pedido do
proprietário de 16/10/2026; implantação de 17/10). Chrome a 1440 × 900 (teclado e mouse) e a 390 × 844 (toque).
  F1-1 nas duas fazendas, o mapa é um grupo com nome ("Talhões da Fazenda X · N talhões"); Tab entra uma vez (1 parada de Tab no mapa); as setas
       vão ao vizinho na direção (todos os talhões alcançáveis só com setas); Home e End vão ao primeiro e ao último pelo nome; Enter abre o painel
       com o foco no título; Esc fecha e devolve o foco ao talhão; o Tab seguinte sai do mapa
  F1-2 instruções visíveis junto do mapa e no aria-describedby do grupo
  F1-3 cada talhão é role=button, com aria-pressed igual à seleção e nome completo ("P5, 71 ha, …, data")
  F1-4 "/" (com o foco no bloco do mapa) abre a busca; "P5", "PV05", "Pivô 5" (e "T4" na Santa Rita) + Enter escolhe e abre o painel; na Lagoa
       Grande a busca enquadra o pivô (pedido explícito); fora disso a câmera não se move
  F1-5 "Ver dados": Lista | Mapa no mesmo bloco; uma linha por talhão com valor, estado em texto e data; ordem pela gravidade; "N de M"; a linha
       abre o mesmo painel; "Localizar no mapa" volta ao mapa com o talhão escolhido; o filtro de cultura vale na lista
  F1-6 "Todas": a lista traz as três fazendas; o mapa mostra a Santa Rita e diz onde estão as outras
  F1-7 Esc desliga o modo (Medir), depois fecha a seleção; o rascunho de desenho não se perde; clique no fundo desmarca
  F1-8 o endereço guarda fazenda, camada, talhão e data (#faz=&lay=&t=&dt=); recarregar #faz=LG&lay=sat&t=PV05&dt=25-09 restaura; voltar do
       CD-01det ("Abrir talhão ›") restaura a câmera e a seleção, sem reenquadrar
  F1-10 com o MapLibre indisponível (CDN bloqueado), a Lista continua e o aviso oferece "Tentar de novo" sem recarregar
  F1-11 390 px com toque: tocar o talhão escolhe e abre o painel embaixo, com o título à vista; sem cartão de hover no toque
  F1-12 sem erro de JavaScript
  Portão (não executável aqui): F1-9 prova com leitor de tela real (NVDA, VoiceOver, TalkBack) antes de fechar D1, D2 e T7.
Medidas (antes → depois): M1 pivôs da Lagoa Grande alcançáveis por teclado; M2 paradas de Tab no mapa da Santa Rita; talhões com aria-pressed;
lista equivalente; Esc fecha o painel; location.hash com a seleção.
Contraprova: RENDER_DIR=<render da base 0b3d0d4> reprova F1-1 a F1-8 e F1-10.
Uso (de gen37/): env CHROME_BIN=… CDP_GL=1 SAFRION_DADOS=sintetico RENDER_DIR=$PWD/_render python3 -B mapa_mux_f1_test.py"""
import os, sys, json, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, servir
from mapa_mux_lib import chk, OK, FAIL, espera, abre, fazenda, camada, caixa, cartao, painel, ativo, erros, tal_el, LG_PRONTO, pivo_livre

R = os.environ.get('RENDER_DIR') or os.path.join(HERE, '_render')
p, srv = servir(R); c = Chrome(); J = c.js
U = f'http://127.0.0.1:{p}/IN-04.dc.html'
MED = {}
ENTER = lambda: c.tecla('Enter', 'Enter', 13, '\r')
ESC = lambda: c.tecla('Escape', 'Escape', 27)
SETA = {'ArrowRight': 39, 'ArrowLeft': 37, 'ArrowUp': 38, 'ArrowDown': 40}
def seta(k): c.tecla(k, k, SETA[k])
def foca(tid): J("(()=>{const b=%s; if(b) b.focus(); })()" % tal_el(tid)); time.sleep(.12)
def grupo():
    return json.loads(J("JSON.stringify((()=>{const g=document.querySelector('[data-mux-grupo]'); if(!g) return null; const bs=[...g.querySelectorAll('[data-talhao]')];"
                        " return {role:g.getAttribute('role'),nome:g.getAttribute('aria-label'),desc:g.getAttribute('aria-describedby'),n:bs.length,tab0:bs.filter(b=>b.tabIndex===0).length,"
                        " pressed:bs.filter(b=>b.hasAttribute('aria-pressed')).length,botao:bs.filter(b=>b.getAttribute('role')==='button'||b.tagName==='BUTTON').length};})())") or 'null')
def paradas_tab():
    """Quantas paradas de Tab ficam dentro do mapa (grupo de talhões ou o SVG/canvas antigo) andando do 1º controle da faixa até sair do bloco."""
    J("(()=>{const b=document.querySelector('nav[aria-label=\"Funcionalidades do mapa\"] [role=tab][aria-selected=true]'); b&&b.focus();})()"); n = 0; dentro = []
    for _ in range(140):
        c.tab(); a = J("(()=>{const a=document.activeElement; if(!a) return null; const m=a.closest('[data-mux-grupo],svg,.maplibregl-canvas-container,#mapa-real'); return [!!m,(a.getAttribute('data-talhao')||a.getAttribute('aria-label')||a.tagName).slice(0,24),!!a.closest('.mapa-corpo')];})()")
        if not a: break
        if a[0]: n += 1; dentro.append(a[1])
        if not a[2]: break
    return n, dentro
def alcance_setas():
    """Talhões alcançáveis a partir do primeiro só com as setas (busca em largura com teclas reais; cada nó é reaberto pelo foco)."""
    ids = J("[...document.querySelectorAll('[data-mux-grupo] [data-talhao]')].map(b=>b.getAttribute('data-talhao'))") or []
    if not ids: return 0, 0
    vistos = {ids[0]}; fila = [ids[0]]
    while fila:
        t = fila.pop(0)
        for k in SETA:
            foca(t); seta(k); a = ativo(J)
            if a and a not in vistos and a in ids: vistos.add(a); fila.append(a)
    return len(vistos), len(ids)
try:
    # ================= 1440 · teclado =================
    for fz, n in (('Santa Rita', 8), ('Lagoa Grande', 23)):
        abre(c, U, 1440, 900, False, faz=fz); camada(J, 'Integrado')
        g = grupo() or {}
        MED[f'grupo_{fz}'] = g
        chk(f'F1-1a {fz}: o mapa é um grupo com nome ("Talhões da Fazenda {fz} · {n} talhões") e um botão por talhão', g.get('role') == 'group' and g.get('nome') == f'Talhões da Fazenda {fz} · {n} talhões' and g.get('n') == n and g.get('botao') == n, g)
        par, den = paradas_tab(); MED[f'paradas_tab_{fz}'] = par
        chk(f'F1-1b {fz}: Tab entra uma vez no mapa (1 parada de Tab; tabindex móvel)', par == 1 and g.get('tab0') == 1, [par, den[:10]])
        al, tot = alcance_setas(); MED[f'alcance_setas_{fz}'] = [al, tot]
        chk(f'F1-1c {fz}: só com as setas, todos os {n} talhões são alcançados (vizinho na direção)', al == n and tot == n, [al, tot])
        ids = J("[...document.querySelectorAll('[data-mux-grupo] [data-talhao]')].map(b=>b.getAttribute('data-talhao'))") or ['']
        foca(ids[min(3, len(ids) - 1)]); c.tecla('Home', 'Home', 36); h = ativo(J); c.tecla('End', 'End', 35); e = ativo(J)
        esp = ('C1', 'T7') if fz == 'Santa Rita' else ('PV01', 'PV24')
        chk(f'F1-1d {fz}: Home e End vão ao primeiro e ao último pelo nome ({esp[0]} e {esp[1]})', (h, e) == esp, [h, e])
        alvo = 'T4' if fz == 'Santa Rita' else 'PV05'; nome = 'T4' if fz == 'Santa Rita' else 'P5'
        foca(alvo); ENTER(); espera(J, "document.activeElement&&document.activeElement.id==='mux-pan-t'", 5)
        ti = J("(()=>{const a=document.activeElement; return a?[a.id,a.innerText]:null;})()") or [None, '']
        ap = J("(%s||{getAttribute:()=>null}).getAttribute('aria-pressed')" % tal_el(alvo))
        chk(f'F1-1e {fz}: Enter no {nome} abre o painel com o foco no título; aria-pressed=true', ti[0] == 'mux-pan-t' and ti[1].startswith(nome + ' ·') and ap == 'true', [ti, ap])
        ESC(); espera(J, "!document.querySelector('main aside[data-mux-painel]')", 4); espera(J, "(document.activeElement||{}).getAttribute&&document.activeElement.getAttribute('data-talhao')===%s" % json.dumps(alvo), 3)
        fe = J("!document.querySelector('main aside[data-mux-painel]')"); af = ativo(J); ap2 = J("(%s||{getAttribute:()=>null}).getAttribute('aria-pressed')" % tal_el(alvo))
        MED[f'esc_fecha_{fz}'] = bool(fe)
        chk(f'F1-1f {fz}: Esc fecha o painel e devolve o foco ao {nome} (aria-pressed=false)', fe and af == alvo and ap2 == 'false', [fe, af, ap2])
        c.tab(); sai = J("(()=>{const a=document.activeElement; return !!a&&!a.closest('[data-mux-grupo]');})()")
        chk(f'F1-1g {fz}: o Tab seguinte sai do mapa', bool(sai), ativo(J))
        ins = json.loads(J("JSON.stringify((()=>{const g=document.querySelector('[data-mux-grupo]'); const id=g&&g.getAttribute('aria-describedby'); const i=id&&document.getElementById(id); return i?[i.innerText,i.getClientRects().length>0&&getComputedStyle(i).visibility!=='hidden']:null;})())") or 'null')
        chk(f'F1-2 {fz}: instruções visíveis junto do mapa e no aria-describedby do grupo (setas, Enter, Esc, /)', bool(ins) and ins[1] and all(x in ins[0].lower() for x in ('setas', 'enter', 'esc', '/')), ins)
        al3 = J("(%s||{getAttribute:()=>''}).getAttribute('aria-label')" % tal_el(alvo)) or ''
        partes = al3.split(', ')
        chk(f'F1-3a {fz}: nome acessível completo no formato do pedido ("{nome}, N ha, cultura e estádio, valor, estado, data")', partes[0] == nome and len(partes) >= 5 and partes[1].endswith(' ha') and ('hoje' in al3 or '/' in partes[-1]), al3)
        MED[f'aria_pressed_{fz}'] = g.get('pressed')
        chk(f'F1-3b {fz}: os {n} talhões têm aria-pressed', g.get('pressed') == n, g.get('pressed'))
        # ---------- F1-4 busca ----------
        foca(alvo); c.tecla('/', 'Slash', 191, '/'); foc = ativo(J)
        chk(f'F1-4a {fz}: "/" com o foco no mapa abre a busca "Ir para talhão"', foc == 'mux-busca', foc)
        termos = (('T4', 'T4'), ('t4', 'T4'), ('Talhão 4', 'T4')) if fz == 'Santa Rita' else (('P5', 'PV05'), ('PV05', 'PV05'), ('Pivô 5', 'PV05'))
        res = []
        for txt, esp_id in termos:
            ESC(); time.sleep(.2); J("(()=>{const a=document.querySelector('main aside[data-mux-painel] button[aria-label=\"Fechar painel\"]'); a&&a.click();})()"); time.sleep(.3)
            cam0 = J("(()=>{const m=window.__LGI&&__LGI.map; if(!m) return null; const c=m.getCenter(); return [c.lng,c.lat,m.getZoom()];})()")
            J("(()=>{const i=document.getElementById('mux-busca'); if(i){ i.focus(); i.value=''; }})()")   # sem a busca (base): o item reprova sem abortar
            for ch in txt: c.call('Input.insertText', {'text': ch}); time.sleep(.02)
            ENTER(); espera(J, "document.activeElement&&document.activeElement.id==='mux-pan-t'", 5); time.sleep(.6)
            cam1 = J("(()=>{const m=window.__LGI&&__LGI.map; if(!m) return null; const c=m.getCenter(); return [c.lng,c.lat,m.getZoom()];})()")
            res.append([txt, J("(document.querySelector('main aside[data-mux-painel] h2')||{}).innerText||''"), ativo(J), J("(%s||{getAttribute:()=>null}).getAttribute('aria-pressed')" % tal_el(esp_id)), cam0 != cam1])
        okb = all(r[1].startswith(nome + ' ·') and r[2] == 'mux-pan-t' and r[3] == 'true' for r in res)
        chk(f'F1-4b {fz}: {" / ".join(t for t, _ in termos)} + Enter escolhe o {nome} e abre o painel com o foco no título', okb, res)
        if fz == 'Lagoa Grande':
            chk('F1-4c Lagoa Grande: a busca enquadra o pivô (pedido explícito: a câmera muda na busca)', res[0][4], res)
            J("(()=>{const a=document.querySelector('main aside[data-mux-painel] button[aria-label=\"Fechar painel\"]'); a&&a.click();})()"); time.sleep(.4)
            cam0 = J("(()=>{const m=__LGI.map; const c=m.getCenter(); return [c.lng,c.lat,m.getZoom()];})()")
            foca('PV05'); ENTER(); espera(J, "!!document.querySelector('main aside[data-mux-painel]')", 4); time.sleep(.6); ESC(); time.sleep(.4)
            cam1 = J("(()=>{const m=__LGI.map; const c=m.getCenter(); return [c.lng,c.lat,m.getZoom()];})()")
            chk('F1-4d Lagoa Grande: Enter e Esc no P5 (à vista) não mexem na câmera (sem zoom nem recentralização sozinhos)', cam0 == cam1, [cam0, cam1])
        # ---------- F1-5 Ver dados (Lista | Mapa) ----------
        J("(()=>{const g=document.querySelector('[role=group][aria-label=\"Ver dados\"]'); const b=g&&[...g.querySelectorAll('button')].find(x=>x.innerText.trim()==='Lista'); b&&b.click();})()")
        espera(J, "document.querySelectorAll('.mux-lista [data-talhao-lista]').length>0", 5)
        li = json.loads(J("JSON.stringify((()=>{const s=document.querySelector('.mux-lista'); if(!s) return null; const rs=[...s.querySelectorAll('[data-talhao-lista]')];"
                          " return {nm:(s.querySelector('[role=status]')||{}).innerText||'',n:rs.length,rows:rs.map(r=>[r.getAttribute('data-talhao-lista'),r.querySelector('.mux-l-v').innerText,r.querySelector('.mux-l-e').innerText,r.querySelector('.mux-l-d').innerText]),"
                          " mapaOculto:[...document.querySelectorAll('[data-mux-grupo]')].every(g=>getComputedStyle(g).visibility==='hidden'||!g.getClientRects().length), seg:[...document.querySelectorAll('[role=group][aria-label=\"Ver dados\"] button')].map(b=>[b.innerText.trim(),b.getAttribute('aria-pressed')])};})())") or 'null')
        MED[f'lista_{fz}'] = (li or {}).get('n')
        okl = bool(li) and li['n'] == n and all(r[1] and r[2] and r[2] != '—' and r[3] for r in li['rows']) and li['nm'].startswith(f'{n} de {n} talhões') and li['mapaOculto'] and ['Lista', 'true'] in li['seg']
        chk(f'F1-5a {fz}: "Ver dados" troca para a Lista no mesmo bloco: {n} linhas com valor, estado em texto e data, "{n} de {n} talhões"', okl, li if not okl else li['nm'])
        # ordem pela gravidade: o estado de cada linha segue a ordem de cores (a pior primeiro): o 1º da lista não é melhor que o último
        cores = J("[...document.querySelectorAll('.mux-lista [data-talhao-lista] > span:first-child')].map(s=>getComputedStyle(s).backgroundColor)") or []
        RANK = {'rgb(200, 85, 61)': 0, 'rgb(217, 138, 78)': 1, 'rgb(212, 178, 90)': 2, 'rgb(169, 192, 106)': 4, 'rgb(127, 174, 104)': 5, 'rgb(95, 143, 85)': 6, 'rgb(68, 115, 154)': 7, 'rgb(110, 159, 198)': 8, 'rgb(155, 139, 196)': 9, 'rgb(201, 207, 203)': 10, 'rgb(228, 233, 223)': 11}
        rk = [RANK.get(x, 3) for x in cores]
        chk(f'F1-5b {fz}: ordem pela gravidade da camada (a pior primeiro)', rk == sorted(rk) and len(rk) == n, [rk, cores[:3]])
        prim = (li or {'rows': [['']]})['rows'][0][0]
        J("(()=>{const r=document.querySelector('.mux-lista [data-talhao-lista=%s]'); r&&r.click();})()" % json.dumps(prim)); espera(J, "!!document.querySelector('main aside[data-mux-painel]')", 4); time.sleep(.3)
        tl = J("(document.querySelector('main aside[data-mux-painel] h2')||{}).innerText||''"); prs = J("(document.querySelector('.mux-lista [data-talhao-lista=%s]')||{getAttribute:()=>null}).getAttribute('aria-pressed')" % json.dumps(prim))
        chk(f'F1-5c {fz}: a linha abre o mesmo painel do mapa (e fica escolhida)', bool(tl) and prs == 'true', [prim, tl, prs])
        J("(()=>{const r=document.querySelector('.mux-lista [data-talhao-lista=%s]'); const b=r&&r.parentElement.querySelector('.mux-loc'); b&&b.click();})()" % json.dumps(prim))
        espera(J, "!document.querySelector('.mux-lista')&&document.activeElement&&document.activeElement.getAttribute('data-talhao')===%s" % json.dumps(prim), 5)
        loc = [J("!document.querySelector('.mux-lista')"), ativo(J), J("(%s||{getAttribute:()=>null}).getAttribute('aria-pressed')" % tal_el(prim))]
        chk(f'F1-5d {fz}: "Localizar no mapa" volta ao mapa com o talhão escolhido e focado', loc == [True, prim, 'true'], loc)
        if fz == 'Santa Rita':   # filtro de cultura: na Santa Rita (na Lagoa Grande todo pivô tem mamão na safra)
            J("(()=>{const s=document.querySelector('select[aria-label=\"Filtrar por cultura\"]'); if(!s) return; const o=[...s.options].map(x=>x.value).find(v=>v!=='Todas'); if(o){ s.value=o; s.dispatchEvent(new Event('change',{bubbles:true})); }})()"); time.sleep(.6)
            J("(()=>{const g=document.querySelector('[role=group][aria-label=\"Ver dados\"]'); const b=g&&[...g.querySelectorAll('button')].find(x=>x.innerText.trim()==='Lista'); b&&b.click();})()"); time.sleep(.6)
            nm = J("((document.querySelector('.mux-lista [role=status]')||{}).innerText||'')") or ''
            nr = J("document.querySelectorAll('.mux-lista [data-talhao-lista]').length")
            chk('F1-5e Santa Rita: o filtro Cultura do topo vale na Lista ("N de 8", com N = linhas)', nm.startswith(f'{nr} de 8') and 0 < nr < 8, [nm, nr])
            J("(()=>{const s=document.querySelector('select[aria-label=\"Filtrar por cultura\"]'); if(s){ s.value='Todas'; s.dispatchEvent(new Event('change',{bubbles:true})); }})()"); time.sleep(.4)
            J("(()=>{const g=document.querySelector('[role=group][aria-label=\"Ver dados\"]'); const b=g&&[...g.querySelectorAll('button')].find(x=>x.innerText.trim()==='Mapa'); b&&b.click();})()"); time.sleep(.5)
    # ---------- F1-6 Todas ----------
    abre(c, U, 1440, 900, False, faz='Todas'); camada(J, 'Integrado')
    av = J("((document.querySelector('.mux-aviso')||{}).innerText||'')") or ''
    J("(()=>{const g=document.querySelector('[role=group][aria-label=\"Ver dados\"]'); const b=g&&[...g.querySelectorAll('button')].find(x=>x.innerText.trim()==='Lista'); b&&b.click();})()"); espera(J, "document.querySelectorAll('.mux-lista li').length>8", 5)
    tx = J("((document.querySelector('.mux-lista')||{}).innerText||'')") or ''
    chk('F1-6 Todas: a Lista traz as três fazendas (Santa Rita, Lagoa Grande, Boa Vista sem geometria); o mapa diz onde estão as outras', 'Lagoa Grande' in tx and 'Boa Vista' in tx and 'sem geometria' in tx and 'T4' in tx and 'Lagoa Grande' in av, [av, tx[:200]])
    # ---------- F1-7 Esc por nível; rascunho; clique no fundo ----------
    abre(c, U, 1440, 900, False, faz='Santa Rita'); camada(J, 'Integrado')
    J("(()=>{const b=[...document.querySelectorAll('[role=toolbar][aria-label=\"Ferramentas do mapa\"] button')].find(x=>x.innerText.trim()==='Medir'); b&&b.click();})()"); time.sleep(.4)
    foca('T1'); time.sleep(.1); ESC(); ESC(); time.sleep(.4)   # 1º Esc: cartão do foco; 2º: o modo
    md = J("(()=>{const b=[...document.querySelectorAll('[role=toolbar][aria-label=\"Ferramentas do mapa\"] button')].find(x=>x.innerText.trim()==='Medir'); return b?b.getAttribute('aria-pressed'):null;})()")
    chk('F1-7a Esc desliga o modo Medir (antes da seleção)', md == 'false', md)
    J("(()=>{const b=%s; b&&b.dispatchEvent(new MouseEvent('click',{bubbles:true}));})()" % tal_el('T2')); antes = espera(J, "!!document.querySelector('main aside[aria-label]')", 3)
    J("(()=>{const r=document.querySelector('svg [role=button]').ownerSVGElement.querySelector(':scope > rect'); r&&r.dispatchEvent(new MouseEvent('click',{bubbles:true}));})()"); time.sleep(.4)
    chk('F1-7b clique no fundo do mapa desmarca (D16): o painel do T2 estava aberto e fecha', antes and J("(()=>{const r=document.querySelector('svg [role=button]').ownerSVGElement.querySelector(':scope > rect'); return !!r;})()") and J("!document.querySelector('main aside[aria-label]')&&!document.querySelector('[data-mux-grupo] [aria-pressed=true]')"), [antes, painel(J)[:80]])
    fazenda(J, 'Lagoa Grande')
    J("(()=>{const b=[...document.querySelectorAll('[role=toolbar][aria-label=\"Ferramentas do mapa\"] button')].find(x=>x.innerText.trim()==='Desenhar'); b&&b.click();})()"); time.sleep(.5)
    b = caixa(J, 'PV05') or {'x': 600, 'y': 500}
    for dx, dy in ((0, 0), (40, 0), (40, 40)): c.mouse(b['x'] + dx, b['y'] + dy, 'mousePressed', 'left'); c.mouse(b['x'] + dx, b['y'] + dy, 'mouseReleased', 'left'); time.sleep(.25)
    p0 = J("((document.querySelector('[role=group][aria-label=\"Desenho do talhão\"] [role=status]')||{}).innerText||'')") or ''
    J("document.querySelector('.mapa-corpo').focus&&document.querySelector('nav[aria-label=\"Funcionalidades do mapa\"] [role=tab]').focus()"); ESC(); time.sleep(.4)
    p1 = J("((document.querySelector('[role=group][aria-label=\"Desenho do talhão\"] [role=status]')||{}).innerText||'')") or ''
    chk('F1-7c Esc não apaga o rascunho de desenho (3 pontos continuam)', p0.startswith('3 pontos') and p1 == p0, [p0, p1])
    J("(()=>{const b=[...document.querySelectorAll('[role=group][aria-label=\"Desenho do talhão\"] button')].find(x=>x.innerText.trim()==='Cancelar'); b&&b.click();})()"); time.sleep(.3)
    # ---------- F1-8 endereço, recarga e volta do CD-01det ----------
    abre(c, U, 1440, 900, False, faz='Lagoa Grande'); camada(J, 'Satélite')
    J("(()=>{const g=[...document.querySelectorAll('main [role=group]')].find(x=>x.getAttribute('aria-label')==='Cena'); const b=g&&[...g.querySelectorAll('button')].find(x=>x.innerText.trim()==='25/09'); b&&b.click();})()"); time.sleep(.4)
    foca('PV05'); ENTER(); espera(J, "location.hash.indexOf('t=PV05')>=0", 4)
    h1 = J("location.hash"); MED['hash'] = h1
    chk('F1-8a o endereço guarda fazenda, camada, talhão e data: #faz=LG&lay=sat&t=PV05&dt=25-09', h1 == '#faz=LG&lay=sat&t=PV05&dt=25-09', h1)
    abre(c, U, 1440, 900, False, faz='Santa Rita'); camada(J, 'Irrigação')   # outro contexto salvo na sessão
    c.goto(U + '#faz=LG&lay=sat&t=PV05&dt=25-09', 1.2); espera(J, LG_PRONTO, 25); espera(J, "(%s||{getAttribute:()=>null}).getAttribute('aria-pressed')==='true'" % tal_el('PV05'), 6)
    rs = [J("(document.querySelector('select[aria-label=\"Filtrar por fazenda\"]')||{}).value"), J("((document.querySelector('nav[aria-label=\"Funcionalidades do mapa\"] [aria-selected=true]')||{}).innerText||'').trim()"),
          J("(%s||{getAttribute:()=>null}).getAttribute('aria-pressed')" % tal_el('PV05')), J("(()=>{const g=[...document.querySelectorAll('main [role=group]')].find(x=>x.getAttribute('aria-label')==='Cena'); const b=g&&g.querySelector('[aria-pressed=true]'); return b?b.innerText.trim():'';})()")]
    chk('F1-8b recarregar #faz=LG&lay=sat&t=PV05&dt=25-09 restaura fazenda, camada, seleção e data', rs == ['Lagoa Grande', 'Satélite', 'true', '25/09'], rs)
    J("void __LGI.map.zoomIn({duration:0})"); time.sleep(.8); cam0 = J("(()=>{const m=__LGI.map; const c=m.getCenter(); return [Math.round(c.lng*1e6),Math.round(c.lat*1e6),Math.round(m.getZoom()*1e3)];})()")
    J("(()=>{const a=[...document.querySelectorAll('main aside[data-mux-painel] a')].find(x=>x.innerText.trim().startsWith('Abrir talhão')); a&&a.click();})()"); time.sleep(1.5)
    pg = J("location.pathname.split('/').pop()+location.hash")
    J("history.back()"); time.sleep(1.5); espera(J, LG_PRONTO, 25); espera(J, "(%s||{getAttribute:()=>null}).getAttribute('aria-pressed')==='true'" % tal_el('PV05'), 6); time.sleep(.6)
    cam1 = J("(()=>{const m=__LGI.map; const c=m.getCenter(); return [Math.round(c.lng*1e6),Math.round(c.lat*1e6),Math.round(m.getZoom()*1e3)];})()")
    sel = J("(%s||{getAttribute:()=>null}).getAttribute('aria-pressed')" % tal_el('PV05'))
    chk('F1-8c "Abrir talhão ›" leva ao CD-01det do P5; voltar restaura a câmera e a seleção, sem reenquadrar', (pg or '').startswith('CD-01det.dc.html#talhao=PV05') and cam1 == cam0 and sel == 'true', [pg, cam0, cam1, sel])
    # ---------- F1-10 sem o MapLibre (CDN bloqueado) ----------
    # CDN indisponível, simulado na página: o <script> do MapLibre aponta para um endereço que não responde enquanto window.__semCDN for verdadeiro
    sem = c.call('Page.addScriptToEvaluateOnNewDocument', {'source': "window.__semCDN=true;(function(){const ap=Element.prototype.appendChild; Element.prototype.appendChild=function(n){ if(window.__semCDN&&n&&n.tagName==='SCRIPT'&&/maplibre-gl/.test(n.src||'')) n.src='http://127.0.0.1:9/maplibre-indisponivel.js'; return ap.call(this,n); };})();"}).get('identifier')
    c.goto('about:blank', .3); c.goto(U + '#faz=LG&lay=int', 1.5); espera(J, "!!document.querySelector('main [role=alert] button')", 15)   # documento novo (só o # mudaria a mesma página)
    er = J("((document.querySelector('main [role=alert]')||{}).innerText||'')") or ''
    J("(()=>{const g=document.querySelector('[role=group][aria-label=\"Ver dados\"]'); const b=g&&[...g.querySelectorAll('button')].find(x=>x.innerText.trim()==='Lista'); b&&b.click();})()"); espera(J, "document.querySelectorAll('.mux-lista [data-talhao-lista]').length===23", 5)
    nl = J("document.querySelectorAll('.mux-lista [data-talhao-lista]').length")
    J("window.__semCDN=false"); c.call('Page.removeScriptToEvaluateOnNewDocument', {'identifier': sem})   # a rede volta
    J("(()=>{const g=document.querySelector('[role=group][aria-label=\"Ver dados\"]'); const b=g&&[...g.querySelectorAll('button')].find(x=>x.innerText.trim()==='Mapa'); b&&b.click();})()"); time.sleep(.3)
    J("(()=>{const b=document.querySelector('main [role=alert] button'); b&&b.click();})()"); ok2 = espera(J, LG_PRONTO, 30)
    chk('F1-10 sem o MapLibre: aviso com "Tentar de novo", a Lista continua (23 linhas) e o mapa volta sem recarregar a página', 'Tentar de novo' in er and nl == 23 and ok2, [er[:120], nl, ok2])
    ee = erros(J); chk('F1-12a 1440: sem erro de JavaScript (fora o aviso esperado do CDN bloqueado)', not [e for e in ee if 'maplibre' not in e.lower() and 'carregar o mapa' not in e], ee[:3])
    # ================= 390 · toque =================
    abre(c, U, 390, 844, True, faz='Santa Rita'); camada(J, 'Integrado'); J("window.__errs=[]")
    b = caixa(J, 'T4'); c.toque(b['x'], b['y']); espera(J, "!!document.querySelector('main aside[data-mux-painel]')", 4); time.sleep(.8)
    pv = json.loads(J("JSON.stringify((()=>{const a=document.querySelector('main aside[data-mux-painel]'); const m=document.querySelector('.mapa-area'); if(!a||!m) return null; const r=a.getBoundingClientRect(), q=m.getBoundingClientRect(), h=a.querySelector('h2').getBoundingClientRect();"
                       " return {abaixo:r.top>=q.bottom-1, titulo:h.top>=0&&h.bottom<=innerHeight, t:a.querySelector('h2').innerText};})())") or 'null')
    cv = cartao(J)
    chk('F1-11a 390 com toque: tocar o T4 escolhe e abre o painel embaixo do mapa, com o título à vista; sem cartão de hover', bool(pv) and pv['abaixo'] and pv['titulo'] and pv['t'].startswith('T4 ·') and not cv.get('on'), [pv, cv.get('on')])
    J("sessionStorage.removeItem('mapa-cam')")   # quem chega ao celular sem câmera guardada (a de 1440 px, ampliada no P5, deixaria os pivôs fora da vista estreita)
    abre(c, U, 390, 844, True, faz='Lagoa Grande'); camada(J, 'Integrado')
    pl = pivo_livre(J) or {'id': 'PV05'}; pv = pl['id']; nm = J("__LGI.markers[%s].getElement().querySelector('b').innerText" % json.dumps(pv))   # pivô com o centro livre (fora da legenda e da barra)
    J("window.__ev=[];['touchstart','touchend','click'].forEach(t=>document.addEventListener(t,e=>window.__ev.push(t+':'+e.target.tagName),true));")
    b = pl; c.toque(b['x'], b['y']); espera(J, "!!document.querySelector('main aside[data-mux-painel]')", 5); time.sleep(.8)
    t5 = J("(document.querySelector('main aside[data-mux-painel] h2')||{}).innerText||''")
    chk(f'F1-11b 390 com toque: tocar um pivô da Lagoa Grande ({nm}) escolhe e abre o painel dele', bool(nm) and t5.startswith(nm + ' ·'), [pv, nm, t5, b, J("window.__ev"), J("location.hash"), J("[...document.querySelectorAll('[data-mux-grupo] [aria-pressed=true]')].map(x=>x.getAttribute('data-talhao'))")])
    g = grupo() or {}; chk('F1-11c 390: o mesmo grupo e os mesmos botões (23, um na ordem de Tab)', g.get('n') == 23 and g.get('tab0') == 1, g)
    ee = erros(J); chk('F1-12b 390: sem erro de JavaScript', not ee, ee[:3])
finally:
    try: c.close()
    except Exception: pass
    srv.terminate()
print('MEDIDAS', json.dumps(MED, ensure_ascii=False))
print('PORTÃO F1-9 (não executado aqui): leitor de tela real (NVDA/Chrome e VoiceOver/Safari, mais VoiceOver iOS ou TalkBack) antes de fechar D1, D2 e T7')
print(f'\nRESULTADO: {len(OK)} ok · {len(FAIL)} falha(s)' + (' · ' + '; '.join(FAIL) if FAIL else ''))
sys.exit(1 if FAIL else 0)
