# -*- coding: utf-8 -*-
"""Mapa (IN-04) · barra de camadas só com ícone e dica (pedido do proprietário, 13/10/2026: "nos ícones à esquerda na barra coloque só o
ícone e tooltip. na parte de pragas e doenças mude ícone para um inseto intuitivo"). Confere no navegador:
  I1 1440 px: as 11 camadas (com Análises de solo, 13/10/2026, e Colheita, 14/10/2026) sem texto visível, cada botão com o nome acessível da camada, alvo ≥ 44 × 44 px e ícone de 22 px;
  I2 a barra ocupa ≤ 72 px (antes 108) e o mapa ganha a largura;
  I3 Pragas e doenças = inseto (engine.ICONS['inseto']), único na barra; "Ver pragas e doenças" do painel usa o mesmo desenho;
  I4 hover: a dica (role=tooltip) mostra o nome da camada; I5 foco de teclado (Tab): a dica abre com o nome e não descreve o botão
     (o nome acessível já é esse texto: o leitor de tela não lê duas vezes, regra do g2dica);
  I6 o clique continua trocando a camada (aria-selected e título do mapa);
  I7 390 px: barra em linha, botões 48 × 48 sem texto visível, sem rolagem lateral da página; I8 sem erro de JS.
Uso: python3 map_trilha_icones_test.py (lê _render ou RENDER_DIR)."""
import os, sys, json, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, servir
import engine as E

OK, FAIL = [], []
def chk(n, c, info=''):
    (OK if c else FAIL).append(n); print(('OK    ' if c else 'FALHA ') + n + ('' if c else ' · ' + str(info)[:700]), flush=True)

NOMES = ['Integrado', 'Satélite', 'Lavoura', 'Análises de solo', 'Pragas e doenças', 'Carência e destino', 'Colheita', 'Irrigação', 'Ordens de serviço', 'Insumos', 'Custos']
TRI = "[...document.querySelectorAll('nav[aria-label=\"Funcionalidades do mapa\"] button')]"
# texto visível = texto dos nós de texto cujo pai tem área > 2 × 2 px (o g2sr tem 1 × 1 e clip)
INFO = TRI + r""".map(b=>{ const r=b.getBoundingClientRect(); const s=b.querySelector('svg'); const sr=s?s.getBoundingClientRect():{width:0};
  const w=document.createTreeWalker(b,NodeFilter.SHOW_TEXT); let vis=''; while(w.nextNode()){ const n=w.currentNode; const p=n.parentElement.getBoundingClientRect();
    if(n.textContent.trim()&&p.width>2&&p.height>2) vis+=n.textContent.trim(); }
  return {nome:b.textContent.replace(/\s+/g,' ').trim(), vis, w:Math.round(r.width), h:Math.round(r.height), ic:Math.round(sr.width), d:(b.querySelector('svg path')||{getAttribute:()=>''}).getAttribute('d'), sel:b.getAttribute('aria-selected')}; })"""
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
try:
    c.aparelho(1440, 900, 1, False); c.goto(U, 1.4); J("window.__e=[];addEventListener('error',e=>window.__e.push(String(e.message)))")
    b = json.loads(J(f"JSON.stringify({INFO})") or '[]')
    chk(f'I1 1440: {len(NOMES)} camadas, nenhuma com texto visível, cada uma com o nome acessível, alvo ≥ 44 × 44 e ícone de 22 px',
        [x['nome'] for x in b] == NOMES and all(x['vis'] == '' and x['w'] >= 44 and x['h'] >= 44 and x['ic'] == 22 for x in b), b)
    lw = json.loads(J("JSON.stringify((()=>{const n=document.querySelector('nav[aria-label=\"Funcionalidades do mapa\"]').getBoundingClientRect(); const m=document.querySelector('main [aria-label=\"Ferramentas do mapa\"]').parentElement.getBoundingClientRect(); return [Math.round(n.width),Math.round(m.width)];})())") or '[0,0]')
    chk('I2 a barra ocupa ≤ 72 px e o mapa fica com a largura', lw[0] <= 72 and lw[1] > 0, lw)
    INS = E.ICONS.get('inseto', '')
    by = {x['nome']: x for x in b}
    chk('I3 Pragas e doenças = inseto, desenho único na barra (sem a lupa antiga)', bool(INS) and by.get('Pragas e doenças', {}).get('d') == INS
        and sum(1 for x in b if x['d'] == INS) == 1 and 'monitoramento' not in E.ICONS, [by.get('Pragas e doenças', {}).get('d', '')[:40], INS[:40]])
    # hover: 300 ms de espera do g2dica
    xy = json.loads(J(f"JSON.stringify((()=>{{const r={TRI}.find(b=>b.textContent.trim()==='Pragas e doenças').getBoundingClientRect(); return [r.left+r.width/2, r.top+r.height/2];}})())"))
    c.mouse(*xy); espera(DICA_ON); d1 = dica()
    chk('I4 hover em Pragas e doenças: a dica (role=tooltip) mostra "Pragas e doenças"', d1.get('on') and d1.get('t') == 'Pragas e doenças' and d1.get('role') == 'tooltip', d1)
    c.mouse(700, 890); time.sleep(.5)
    J(f"{TRI}[0].focus()"); c.tecla('Tab', 'Tab', 9); espera(DICA_ON)
    d2 = dica(); foc = J("(()=>{const a=document.activeElement; return a?[a.textContent.trim(), (a.getAttribute('aria-describedby')||'')]:[];})()") or []
    chk('I5 Tab até Satélite: a dica abre com o nome, sem aria-describedby repetindo o nome acessível', d2.get('on') and d2.get('t') == 'Satélite' and foc and foc[0] == 'Satélite' and 'g2-dica' not in foc[1], [d2, foc])
    J(f"{TRI}.find(b=>b.textContent.trim()==='Pragas e doenças').click()"); time.sleep(.6)
    b2 = json.loads(J(f"JSON.stringify({INFO})") or '[]'); tit = J("(document.querySelector('main')||document.body).innerText") or ''
    chk('I6 o clique troca a camada: Pragas e doenças selecionada e o mapa com o título da camada', any(x['nome'] == 'Pragas e doenças' and x['sel'] == 'true' for x in b2) and 'Pragas e doenças' in tit, [x['sel'] for x in b2])
    J(f"{TRI}[0].click()"); time.sleep(.5)
    J("(()=>{const s=document.querySelector('select[aria-label=\"Filtrar por fazenda\"]'); s.value='Santa Rita'; s.dispatchEvent(new Event('change',{bubbles:true}));})()"); espera("document.querySelectorAll('svg [role=button]').length>0")
    mip = J("""(()=>{ const pol=document.querySelector('svg [role=button]'); if(!pol) return null; pol.dispatchEvent(new MouseEvent('click',{bubbles:true})); return pol.getAttribute('aria-label'); })()"""); time.sleep(.6)
    ver = json.loads(J("JSON.stringify((()=>{const b=[...document.querySelectorAll('main aside[aria-label] button, main aside[aria-label] a')].find(b=>b.innerText.trim()==='Ver pragas e doenças'); return b?[...b.querySelectorAll('svg path')].map(p=>p.getAttribute('d')):null;})())") or 'null')
    chk('I3b painel do talhão (Integrado): "Ver pragas e doenças" com o mesmo inseto', ver == [INS], [mip, (ver or [''])[0][:40] if ver else ver])
    c.aparelho(390, 844, 2, True); c.goto(U, 1.4)
    b3 = json.loads(J(f"JSON.stringify({INFO})") or '[]')
    row = J("(()=>{const n=document.querySelector('nav[aria-label=\"Funcionalidades do mapa\"]'); return getComputedStyle(n).flexDirection;})()")
    lg = J("document.documentElement.scrollWidth-document.documentElement.clientWidth")
    chk(f'I7 390 px: barra em linha, {len(NOMES)} botões 48 × 48 sem texto visível, sem rolagem lateral da página',
        row == 'row' and len(b3) == len(NOMES) and all(x['vis'] == '' and x['w'] == 48 and x['h'] >= 48 for x in b3) and (lg or 0) <= 0, [row, lg, [(x['nome'], x['w'], x['h'], x['vis']) for x in b3]])
    chk('I8 sem erro de JS', not (J("(window.__e||[]).join(' | ')") or ''), J("(window.__e||[]).join(' | ')"))
finally:
    try: c.close()
    except Exception: pass
    srv.terminate()
print(f'RESULTADO: {len(OK)} ok · {len(FAIL)} falhas')
sys.exit(1 if FAIL else 0)
