# -*- coding: utf-8 -*-
"""Mapa (IN-04) · barra das funções. Histórico: 13/10/2026 só ícone e dica, na coluna da esquerda ("nos ícones à esquerda na barra coloque só o
ícone e tooltip. na parte de pragas e doenças mude ícone para um inseto intuitivo"). 16/10/2026 (DEC-0910-36): os nove nomes da DEC-2609-12; e,
no mesmo dia, o proprietário pediu a barra fora do lado da lateral dos módulos ("a barra de ícones do mapa por estar do lado da barra lateral de
ícones dos módulos não fica legal, melhore esses ícones do mapa de lugar"): ela fica no alto do bloco do mapa, na horizontal, com ícone e nome
(seletor de visões da DS com rótulo, VISOES-ROT). Os oráculos da coluna vertical (só ícone, ≤ 72 px de largura) saíram por esse pedido.
  I1 1440 px: as 9 funções, na ordem, cada uma com ícone de 16 px e o nome à vista, alvo de 32 px de altura (mouse)
  I2 a barra fica acima da faixa da camada e do mapa, em uma linha; o mapa começa na borda esquerda do bloco (nenhuma coluna de ícones)
  I3 Pragas e doenças = inseto (engine.ICONS['inseto']), único na barra; "Ver pragas e doenças" do painel usa o mesmo desenho
  I4 hover: a dica (role=tooltip) diz "Mostrar Pragas e doenças no mapa" (DS-48); I5 foco de teclado (Tab): a dica abre com "Mostrar Satélite no mapa"
  I6 o clique troca a camada (aria-selected, estado ativo da DS e título do mapa)
  I7 390 px com toque: barra em linha, rolável dentro dela, 9 botões de 44 px de altura com o nome à vista, sem rolagem lateral da página; I8 sem erro de JS.
Uso: python3 map_trilha_icones_test.py (lê _render ou RENDER_DIR)."""
import os, sys, json, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, servir
import engine as E

OK, FAIL = [], []
def chk(n, c, info=''):
    (OK if c else FAIL).append(n); print(('OK    ' if c else 'FALHA ') + n + ('' if c else ' · ' + str(info)[:700]), flush=True)

# DEC-0910-36 (decisão do proprietário, 16/10/2026): a barra volta aos nove nomes da DEC-2609-12, nesta ordem
NOMES = ['Integrado', 'Satélite', 'Solo', 'Pragas e doenças', 'Ordens de serviço', 'Irrigação', 'Estádio', 'Colheita e produtividade', 'Custos']
TRI = "[...document.querySelectorAll('nav[aria-label=\"Funcionalidades do mapa\"] [role=tab]')]"
# texto visível = texto dos nós de texto cujo pai tem área > 2 × 2 px
INFO = TRI + r""".map(b=>{ const r=b.getBoundingClientRect(); const s=b.querySelector('svg'); const sr=s?s.getBoundingClientRect():{width:0};
  const w=document.createTreeWalker(b,NodeFilter.SHOW_TEXT); let vis=''; while(w.nextNode()){ const n=w.currentNode; const p=n.parentElement.getBoundingClientRect();
    if(n.textContent.trim()&&p.width>2&&p.height>2) vis+=n.textContent.trim(); }
  return {nome:b.textContent.replace(/\s+/g,' ').trim(), vis, x:Math.round(r.left), y:Math.round(r.top), w:Math.round(r.width), h:Math.round(r.height), ic:Math.round(sr.width),
    d:(b.querySelector('svg path')||{getAttribute:()=>''}).getAttribute('d'), sel:b.getAttribute('aria-selected'), at:b.getAttribute('data-ativo'), bg:getComputedStyle(b).backgroundColor}; })"""
p, srv = servir(os.environ.get('RENDER_DIR') or os.path.join(HERE, '_render')); c = Chrome(); J = c.js
U = f'http://127.0.0.1:{p}/IN-04.dc.html'
def espera(js, ate=4.0):   # espera a condição observável (AGENTS §3.6), com limite explícito
    t0 = time.time()
    while time.time() - t0 < ate:
        if J(js): return True
        time.sleep(.1)
    return False
DICA_ON = "(()=>{const d=document.getElementById('g2-dica'); return !!d&&!d.hidden&&d.getClientRects().length>0&&!!d.innerText.trim();})()"
def dica():
    return json.loads(J("JSON.stringify((()=>{const d=document.getElementById('g2-dica'); return d?{on:!d.hidden&&d.getClientRects().length>0,t:d.innerText.trim(),role:d.getAttribute('role')}:{on:false,t:'',role:''};})())") or '{}')
GEO = """JSON.stringify((()=>{const n=document.querySelector('nav[aria-label="Funcionalidades do mapa"]').getBoundingClientRect(); const c=document.querySelector('.mapa-corpo').getBoundingClientRect();
  const a=document.querySelector('.mapa-area').getBoundingClientRect(); const fx=document.querySelector('main [role=group][aria-label^="Indicadores de"]').getBoundingClientRect();
  return {nb:Math.round(n.bottom), nl:Math.round(n.left), cl:Math.round(c.left), al:Math.round(a.left), at:Math.round(a.top), ft:Math.round(fx.top)};})())"""
try:
    c.aparelho(1440, 900, 1, False); c.goto(U, 1.4); J("window.__e=[];addEventListener('error',e=>window.__e.push(String(e.message)))")
    b = json.loads(J(f"JSON.stringify({INFO})") or '[]')
    chk(f'I1 1440: {len(NOMES)} funções na ordem, cada uma com ícone de 16 px e o nome à vista, alvo de 32 px de altura',
        [x['nome'] for x in b] == NOMES and all(x['vis'] == x['nome'] and x['h'] == 32 and x['ic'] == 16 for x in b), b)
    g = json.loads(J(GEO) or '{}')
    chk('I2 barra no alto, em uma linha, acima da faixa da camada e do mapa; o mapa começa na borda esquerda do bloco (sem coluna de ícones)',
        len({x['y'] for x in b}) == 1 and g['nb'] <= g['ft'] and g['nb'] <= g['at'] and g['al'] - g['cl'] <= 2, [g, sorted({x['y'] for x in b})])
    INS = E.ICONS.get('inseto', '')
    by = {x['nome']: x for x in b}
    chk('I3 Pragas e doenças = inseto, desenho único na barra (sem a lupa antiga)', bool(INS) and by.get('Pragas e doenças', {}).get('d') == INS
        and sum(1 for x in b if x['d'] == INS) == 1 and 'monitoramento' not in E.ICONS, [by.get('Pragas e doenças', {}).get('d', '')[:40], INS[:40]])
    # hover: 300 ms de espera do g2dica
    xy = json.loads(J(f"JSON.stringify((()=>{{const r={TRI}.find(b=>b.textContent.trim()==='Pragas e doenças').getBoundingClientRect(); return [r.left+r.width/2, r.top+r.height/2];}})())"))
    c.mouse(*xy); espera(DICA_ON); d1 = dica()
    chk('I4 hover em Pragas e doenças: a dica (role=tooltip) diz "Mostrar Pragas e doenças no mapa"', d1.get('on') and d1.get('t') == 'Mostrar Pragas e doenças no mapa' and d1.get('role') == 'tooltip', d1)
    c.mouse(700, 890); time.sleep(.5)
    J(f"{TRI}[0].focus()"); c.tecla('Tab', 'Tab', 9); espera(DICA_ON)
    d2 = dica(); foc = J("(()=>{const a=document.activeElement; return a?a.textContent.trim():'';})()") or ''
    chk('I5 Tab até Satélite: a dica abre com "Mostrar Satélite no mapa"', d2.get('on') and d2.get('t') == 'Mostrar Satélite no mapa' and foc == 'Satélite', [d2, foc])
    J(f"{TRI}.find(b=>b.textContent.trim()==='Pragas e doenças').click()"); time.sleep(.6)
    b2 = json.loads(J(f"JSON.stringify({INFO})") or '[]'); tit = J("(document.querySelector('main')||document.body).innerText") or ''
    on = [x for x in b2 if x['sel'] == 'true']
    chk('I6 o clique troca a camada: Pragas e doenças selecionada (aria-selected e estado ativo tonal da DS) e o mapa com o título da camada',
        [x['nome'] for x in on] == ['Pragas e doenças'] and on[0]['at'] == 'true' and on[0]['bg'] == 'rgb(228, 243, 233)' and 'Pragas e doenças' in tit, [(x['nome'], x['sel'], x['at'], x['bg']) for x in b2])
    J(f"{TRI}[0].click()"); time.sleep(.5)
    J("(()=>{const s=document.querySelector('select[aria-label=\"Filtrar por fazenda\"]'); s.value='Santa Rita'; s.dispatchEvent(new Event('change',{bubbles:true}));})()"); espera("document.querySelectorAll('svg [role=button]').length>0")
    mip = J("""(()=>{ const pol=document.querySelector('svg [role=button]'); if(!pol) return null; pol.dispatchEvent(new MouseEvent('click',{bubbles:true})); return pol.getAttribute('aria-label'); })()"""); time.sleep(.6)
    ver = json.loads(J("JSON.stringify((()=>{const b=[...document.querySelectorAll('main aside[aria-label] button, main aside[aria-label] a')].find(b=>b.innerText.trim()==='Ver pragas e doenças'); return b?[...b.querySelectorAll('svg path')].map(p=>p.getAttribute('d')):null;})())") or 'null')
    chk('I3b painel do talhão (Integrado): "Ver pragas e doenças" com o mesmo inseto', ver == [INS], [mip, (ver or [''])[0][:40] if ver else ver])
    c.aparelho(390, 844, 2, True); c.goto(U, 1.4)
    b3 = json.loads(J(f"JSON.stringify({INFO})") or '[]')
    row = J("(()=>{const n=document.querySelector('nav[aria-label=\"Funcionalidades do mapa\"]'); const w=n.parentElement; return [getComputedStyle(n).flexDirection, w.scrollWidth>w.clientWidth, getComputedStyle(w).overflowX];})()") or []
    lg = J("document.documentElement.scrollWidth-document.documentElement.clientWidth")
    chk(f'I7 390 px com toque: barra em linha e rolável dentro dela, {len(NOMES)} botões de 44 px de altura com o nome à vista, sem rolagem lateral da página',
        row[:1] == ['row'] and row[1] and row[2] == 'auto' and len(b3) == len(NOMES) and len({x['y'] for x in b3}) == 1 and all(x['vis'] == x['nome'] and x['h'] == 44 for x in b3) and (lg or 0) <= 0,
        [row, lg, [(x['nome'], x['w'], x['h'], x['vis']) for x in b3]])
    chk('I8 sem erro de JS', not (J("(window.__e||[]).join(' | ')") or ''), J("(window.__e||[]).join(' | ')"))
finally:
    try: c.close()
    except Exception: pass
    srv.terminate()
print(f'RESULTADO: {len(OK)} ok · {len(FAIL)} falhas')
sys.exit(1 if FAIL else 0)
