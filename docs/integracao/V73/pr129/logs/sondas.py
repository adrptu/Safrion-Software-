# PR #129 (EX-53 D11) · contraexemplos do revisor: conflito entre abas, 390 px e teclado na CF-06, Mapa › Custos com meta, IC com meta.
import os, sys, time, json, re
G = sys.argv[1]; OUT = sys.argv[2]; os.makedirs(OUT, exist_ok=True); sys.path.insert(0, G)
from comp_lib import Chrome, servir
port, srv = servir(os.path.join(G, '_render')); c = Chrome(); J = c.js
U = lambda p: f'http://127.0.0.1:{port}/{p}'
falhas = []
def ok(cond, msg, info=''):
    print(('OK    ' if cond else 'FALHA ') + msg + ('' if cond else ' · ' + str(info)[:700]), flush=True)
    if not cond: falhas.append(msg)
N = "(s=>(s||'').replace(/\\s+/g,' ').trim())"
ABRE = "((id,W)=>{ W=W||window; const d=W.document; const r=[...d.querySelectorAll('[data-g2g=g_metas] [role=row][data-rid]')].find(r=>r.getAttribute('data-rid')===id); if(!r) return 'sem linha '+id; (r.querySelector('.g2pw')||r.querySelector('[role=cell]')||r).click(); return 'ok'; })"
SETV = "((k,val,W)=>{ W=W||window; const i=W.document.getElementById(k); if(!i) return 'sem '+k; const P=i.tagName==='TEXTAREA'?W.HTMLTextAreaElement.prototype:W.HTMLInputElement.prototype; Object.getOwnPropertyDescriptor(P,'value').set.call(i,val); i.dispatchEvent(new W.Event('input',{bubbles:true})); i.dispatchEvent(new W.Event('change',{bubbles:true})); return 'ok'; })"
BTN = "((t,W)=>{ W=W||window; const b=[...W.document.querySelectorAll('aside[role=dialog] button')].filter(b=>b.getClientRects().length).find(b=>(b.innerText||'').trim()===t); if(!b) return false; b.click(); return true; })"
DLG = "((W)=>{ W=W||window; const a=W.document.querySelector('aside[role=dialog]'); return a&&a.getClientRects().length?a.innerText.replace(/\\s+/g,' ').trim():''; })"
LINHA = "((id,W)=>{ W=W||window; const r=[...W.document.querySelectorAll('[data-g2g=g_metas] [role=row][data-rid]')].find(r=>r.getAttribute('data-rid')===id); return r?r.innerText.replace(/\\s+/g,' ').trim():null; })"
def grava_ui(id, valor, atencao, motivo):
    c.goto(U('CF-06.dc.html'), 1.8); J(ABRE + "(" + json.dumps(id) + ")"); time.sleep(.5)
    J(SETV + "('m6_valor'," + json.dumps(str(valor)) + ")"); J(SETV + "('m6_atencao'," + json.dumps(str(atencao)) + ")"); J(SETV + "('m6_motivo'," + json.dumps(motivo) + ")"); time.sleep(.3)
    J(BTN + "('Salvar meta')"); time.sleep(.8); return J(LINHA + "(" + json.dumps(id) + ")")
try:
    c.aparelho(1440, 900); c.goto(U('Main.dc.html'), .3); J("localStorage.clear(); sessionStorage.clear(); 1")
    # ---- S1 · conflito entre abas: A abre o editor na v0; B (outra janela, mesma origem) grava; A não pode sobrescrever ----
    c.goto(U('CF-06.dc.html'), 1.8)
    ok(J(ABRE + "('KPI-PCM-05')") == 'ok', 'S1a abre o editor do KPI-PCM-05 na aba A')
    time.sleep(.5)
    J("(()=>{ const f=document.createElement('iframe'); f.id='abaB'; f.src='CF-06.dc.html'; f.style.cssText='position:fixed;left:0;top:0;width:1200px;height:800px;opacity:0;pointer-events:none;'; document.body.appendChild(f); window.__B=null; f.onload=()=>{ window.__B=f.contentWindow; }; return 1; })()")
    for _ in range(40):
        if J("!!(window.__B&&window.__B.document&&window.__B.document.querySelector('[data-g2g=g_metas] [role=row][data-rid]'))"): break
        time.sleep(.25)
    rB = J("(()=>{ const W=window.__B; if(!W||!W.document||!W.document.querySelector('[data-g2g=g_metas]')) return 'aba B não carregou'; return 'ok'; })()")
    if rB == 'ok':
        J(ABRE + "('KPI-PCM-05',window.__B)"); time.sleep(.6)
        J(SETV + "('m6_valor','85',window.__B)"); J(SETV + "('m6_atencao','75',window.__B)"); J(SETV + "('m6_motivo','outra aba',window.__B)"); time.sleep(.3)
        J(BTN + "('Salvar meta',window.__B)"); time.sleep(1.0)
        rB = J(LINHA + "('KPI-PCM-05',window.__B)")
    time.sleep(1.0)
    dA = J(DLG + "()")
    ok(isinstance(rB, str) and 'v1' in rB and '85' in rB, 'S1b a aba B grava a meta 85/75 (v1) pela tela', rB)
    ok('A meta mudou' in dA, 'S1c a aba A, sem recarregar, mostra o aviso de conflito no editor aberto', dA[:400])
    J(SETV + "('m6_valor','70')"); J(SETV + "('m6_atencao','60')"); J(SETV + "('m6_motivo','aba A sobrescreve')"); time.sleep(.3)
    J(BTN + "('Salvar meta')"); time.sleep(.8)
    dA2 = J(DLG + "()")
    c.goto(U('CF-06.dc.html'), 1.8); vig = J(LINHA + "('KPI-PCM-05')")
    ok(bool(vig) and '85' in vig and 'v1' in vig and '70' not in vig and ('mudou' in dA2 or 'Compare' in dA2), 'S1d salvar na aba A com a versão antiga é recusado; a meta continua 85 v1', [vig, dA2[:300]])
    J("(()=>{ const f=document.getElementById('abaB'); f&&f.remove(); return 1; })()")
    # ---- S2 · 390 px: lista e editor cabem, sem rolagem lateral; botões visíveis ----
    c.aparelho(390, 844); c.goto(U('CF-06.dc.html'), 1.8)
    sw = J("document.scrollingElement.scrollWidth"); iw = J("innerWidth")
    J(ABRE + "('custo-desvio')"); time.sleep(.6)
    d390 = J("(()=>{ const a=document.querySelector('aside[role=dialog]'); if(!a) return null; const r=a.getBoundingClientRect(); const bs=[...a.querySelectorAll('button')].filter(b=>b.getClientRects().length).map(b=>{ const q=b.getBoundingClientRect(); return [b.innerText.trim(), Math.round(q.left), Math.round(q.right), Math.round(q.height)]; }); return {l:r.left, r:r.right, w:innerWidth, bs}; })()")
    sw2 = J("document.scrollingElement.scrollWidth")
    ok(sw <= iw and sw2 <= iw and d390 and d390['r'] <= d390['w'] + 1 and all(b[2] <= d390['w'] + 1 and b[3] >= 44 for b in d390['bs'] if b[0]), '390 px: lista e editor cabem na largura, sem rolagem lateral, botões com 44 px de altura', [sw, sw2, iw, d390])
    c.shot(os.path.join(OUT, 'cf06_editor_390.png'))
    # ---- S3 · teclado: Tab chega à linha, Enter abre, foco dentro do painel, Esc fecha e devolve o foco à linha ----
    c.aparelho(1440, 900); c.goto(U('CF-06.dc.html'), 1.8)
    alvo = None
    for i in range(60):
        c.call('Input.dispatchKeyEvent', {'type': 'keyDown', 'key': 'Tab', 'code': 'Tab', 'windowsVirtualKeyCode': 9}); c.call('Input.dispatchKeyEvent', {'type': 'keyUp', 'key': 'Tab', 'code': 'Tab', 'windowsVirtualKeyCode': 9}); time.sleep(.08)
        alvo = J("(()=>{ const a=document.activeElement; const r=a&&a.closest&&a.closest('[data-g2g=g_metas] [role=row][data-rid]'); return r?r.getAttribute('data-rid'):null; })()")
        if alvo: break
    for t in ('keyDown', 'keyUp'): c.call('Input.dispatchKeyEvent', {'type': t, 'key': 'Enter', 'code': 'Enter', 'windowsVirtualKeyCode': 13})
    time.sleep(.6)
    dentro = J("(()=>{ const a=document.querySelector('aside[role=dialog]'); return !!(a&&a.contains(document.activeElement)); })()")
    for t in ('keyDown', 'keyUp'): c.call('Input.dispatchKeyEvent', {'type': t, 'key': 'Escape', 'code': 'Escape', 'windowsVirtualKeyCode': 27})
    time.sleep(.5)
    volta = J("(()=>{ const a=document.activeElement; const r=a&&a.closest&&a.closest('[role=row][data-rid]'); return r?r.getAttribute('data-rid'):(a?a.tagName:null); })()")
    ok(bool(alvo) and dentro and volta == alvo, 'teclado: Tab chega a uma linha, Enter abre o editor com o foco dentro, Esc fecha e devolve o foco à linha', [alvo, dentro, volta])
    # ---- S4 · Mapa › Custos com meta: cor pela meta e rótulo do talhão sem a dica inteira ----
    print('      grava custo-desvio:', grava_ui('custo-desvio', 5, 10, 'sonda do revisor'))
    c.goto(U('IN-04.dc.html'), 2.0)
    J("(()=>{const b=[...document.querySelectorAll('nav[aria-label=\"Funcionalidades do mapa\"] [role=tab]')].find(b=>b.innerText.trim()==='Custos'); if(b) b.click();})()"); time.sleep(1.4)
    J("(()=>{const b=[...document.querySelectorAll('button,[role=radio],[role=tab]')].find(b=>b.getClientRects().length&&/^Realizado/.test(b.innerText.trim())); if(b) b.click();})()"); time.sleep(1.2)
    body = J("document.body.innerText")
    rot = J("[...document.querySelectorAll('svg text, .tl-rot, [data-rot]')].filter(e=>e.getClientRects().length).map(e=>(e.textContent||'').replace(/\\s+/g,' ').trim()).filter(t=>/R\\$|mil|%/.test(t)).slice(0,8)")
    longos = [t for t in (rot or []) if len(t) > 60]
    ok('Meta atendida' in body or 'Fora da meta' in body or 'Atenção à meta' in body, 'Mapa › Custos com meta: a legenda passa a ter as faixas da meta', re.findall(r'(Meta atendida|Atenção à meta|Fora da meta|Meta não configurada)', body)[:6])
    ok(not longos, 'Mapa › Custos com meta: nenhum rótulo de talhão leva a dica inteira (> 60 caracteres)', longos[:3] or rot[:5])
    c.shot(os.path.join(OUT, 'mapa_custos_meta_1440.png'))
    # ---- S5 · IC com meta de compra-referência ----
    print('      grava compra-referencia:', grava_ui('compra-referencia', 0, 2, 'sonda do revisor'))
    c.goto(U('IC.dc.html'), 2.2)
    bic = J("document.body.innerText")
    ok(any(x in bic for x in ('Meta atendida', 'Atenção à meta', 'Fora da meta', 'Base parcial')), 'IC com meta de compra: as comparações ganham o resultado da meta', re.findall(r'(Meta atendida|Atenção à meta|Fora da meta|Base parcial|Meta não configurada)', bic)[:8])
    c.shot(os.path.join(OUT, 'ic_meta_1440.png'))
    err = J("window.__err||''")
finally:
    c.close(); srv.terminate()
print('RESULTADO', 'OK' if not falhas else f'{len(falhas)} falha(s): ' + '; '.join(falhas))
