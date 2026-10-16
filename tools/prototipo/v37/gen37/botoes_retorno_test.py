# -*- coding: utf-8 -*-
"""Retorno visual dos botões (proprietário, 14/10/2026: "botões como salvar, cancelar e outros estão com feedback visual ao usuário?").
Mede no navegador, no formulário "Cadastrar cultivar" (CD-02, aberto por "Criar cultivar" no cabeçalho desde 16/10, CAD-01) e na Manutenção, o que a pessoa vê (DS-HOVER-20261009, VIS-01 a VIS-04):
  B1 passar o mouse: Salvar (cheio) escurece; Cancelar (claro) ganha a camada verde. O Chrome sem janela não declara mouse com hover (a emulação
     não muda o (hover:hover)); por isso B1 confere a REGRA de hover que vale para cada botão (seletor que casa com ele e o efeito declarado),
     não o pixel. B2 (pressionar) mede o pixel
  B2 pressionar: Salvar escurece; Cancelar ganha a camada verde (pixel medido)
  B3 foco pelo teclado (Tab): contorno verde de 2 px fora do botão
  B4 indisponível: aparência apagada, cursor de proibido e o motivo em texto ao lado (Manutenção, perfil sem permissão)
  B5 depois de Salvar: aviso "Salvo: …" e a linha salva destacada em verde
  B6 sem erro de JS
Uso: python3 botoes_retorno_test.py (lê _render ou RENDER_DIR)."""
import os, sys, json, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
os.environ.setdefault('CDP_GL', '1')
from comp_lib import Chrome, servir

OK, FAIL = [], []
def chk(n, c, info=''):
    (OK if c else FAIL).append(n); print(('OK    ' if c else 'FALHA ') + n + ('' if c else ' · ' + str(info)[:700]), flush=True)
R = os.environ.get('RENDER_DIR') or os.path.join(HERE, '_render')
p, srv = servir(R); c = Chrome(); J = c.js
U = lambda pg: f'http://127.0.0.1:{p}/{pg}'
BT = "(t=>[...document.querySelectorAll('aside[role=dialog] button')].find(b=>b.innerText.trim()===t&&b.getClientRects().length))"
def ponto(t): return J(f"(()=>{{const b={BT}({json.dumps(t)}); if(!b) return null; const r=b.getBoundingClientRect(); return {{x:r.left+r.width/2,y:r.top+r.height/2}};}})()")
def estilo(t): return J(f"(()=>{{const b={BT}({json.dumps(t)}); if(!b) return null; const s=getComputedStyle(b); return {{f:s.filter,bg:s.backgroundImage,bc:s.backgroundColor,ol:s.outlineStyle+' '+s.outlineWidth+' '+s.outlineColor,oo:s.outlineOffset}};}})()")
def mouse(tp, x, y): c.call('Input.dispatchMouseEvent', {'type': tp, 'x': x, 'y': y, 'button': 'left', 'clickCount': 1})
def brilho(f):   # "brightness(0.92)" → 0.92; sem filtro → 1
    try: return float(f.split('brightness(')[1].split(')')[0])
    except Exception: return 1.0
SETV = ("((sel,val)=>{const i=document.querySelector(sel); if(!i) return false; const P=i.tagName==='SELECT'?HTMLSelectElement.prototype:HTMLInputElement.prototype;"
        " Object.getOwnPropertyDescriptor(P,'value').set.call(i,val); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true})); return true;})")
try:
    c.call('Page.addScriptToEvaluateOnNewDocument', {'source': "window.__err='';addEventListener('error',e=>{window.__err+=(e.message||'erro')+' | ';});"})
    c.aparelho(1440, 900, 1, False)
    # o Chrome sem janela não declara mouse com hover: emula o de um computador (hover e ponteiro fino), como a pessoa usa
    c.call('Emulation.setEmulatedMedia', {'features': [{'name': 'hover', 'value': 'hover'}, {'name': 'pointer', 'value': 'fine'}]})
    c.goto(U('Main.dc.html'), .3); J("localStorage.clear(); sessionStorage.clear(); 1")
    c.goto(U('CD-02.dc.html'), 1.4)
    J("(()=>{const b=[...document.querySelectorAll('button')].find(b=>b.innerText.trim()==='Criar cultivar'); if(b) b.click();})()"); time.sleep(.6)
    s0, c0 = estilo('Salvar'), estilo('Cancelar')
    ps, pc = ponto('Salvar'), ponto('Cancelar')
    REGRA = (f"(t=>{{ const b={BT}(t); const out=[]; for(const ss of document.styleSheets){{ let rs; try{{ rs=ss.cssRules; }}catch(e){{ continue; }}"
             " for(const m of rs){ if(!(m.media&&/hover:\\s*hover/.test(m.media.mediaText))) continue; for(const r of m.cssRules){ const sel=r.selectorText||''; if(!/:hover/.test(sel)) continue;"
             " const base=sel.split(',').map(x=>x.replace(/:hover/g,'').trim()).filter(Boolean); if(base.some(x=>{ try{ return b.matches(x); }catch(e){ return false; } })) out.push(r.style.cssText); } } }"
             " return out; })")
    rs, rc = J(f"({REGRA})('Salvar')") or [], J(f"({REGRA})('Cancelar')") or []
    chk('B1 hover (regra): Salvar escurece (brightness); Cancelar ganha a camada verde', any('brightness' in x for x in rs) and any('gradient' in x or 'background' in x for x in rc), [rs, rc])
    sh = estilo('Salvar'); ch = estilo('Cancelar')
    mouse('mousePressed', ps['x'], ps['y']); time.sleep(.2); sa = estilo('Salvar'); mouse('mouseMoved', 5, 5); mouse('mouseReleased', 5, 5); time.sleep(.2)
    mouse('mouseMoved', pc['x'], pc['y']); mouse('mousePressed', pc['x'], pc['y']); time.sleep(.2); ca = estilo('Cancelar'); mouse('mouseMoved', 5, 5); mouse('mouseReleased', 5, 5); time.sleep(.2)
    chk('B2 pressionar (pixel): Salvar escurece; Cancelar ganha a camada verde', brilho(sa['f']) < brilho(sh['f']) and ca['bg'] != ch['bg'] and 'gradient' in ca['bg'], [sh, sa, ch, ca])
    J(f"(()=>{{const b={BT}('Salvar'); const all=[...document.querySelectorAll('aside[role=dialog] button, aside[role=dialog] input, aside[role=dialog] select')].filter(e=>e.getClientRects().length&&!e.disabled); const i=all.indexOf(b); if(i>0) all[i-1].focus();}})()")
    c.call('Input.dispatchKeyEvent', {'type': 'keyDown', 'key': 'Tab', 'code': 'Tab', 'windowsVirtualKeyCode': 9}); c.call('Input.dispatchKeyEvent', {'type': 'keyUp', 'key': 'Tab', 'code': 'Tab', 'windowsVirtualKeyCode': 9}); time.sleep(.2)
    foco = J("document.activeElement?document.activeElement.innerText.trim():''"); sf = estilo(foco) if foco else None
    chk('B3 foco pelo teclado: contorno verde de 2 px fora do botão', bool(sf) and sf['ol'] == 'solid 2px rgb(30, 122, 76)' and sf['oo'] == '2px', [foco, sf])
    # B5 · salvar mostra o aviso e destaca a linha
    for k, v in (('cult', 'Soja'), ('nome', 'TMG 2383'), ('dias', '118')): J(f"({SETV})('aside[role=dialog] [id$=\"_{k}\"]',{json.dumps(v)})"); time.sleep(.15)
    # o realce é um pulso verde de ~0,5 s (DS-RETORNO-20261009): lido logo depois do toque em Salvar
    fl = J(f"(()=>{{ {BT}('Salvar').click(); return new Promise(ok=>setTimeout(()=>{{ const r=[...document.querySelectorAll('[role=row].g2-realce')].find(r=>r.getClientRects().length&&/TMG 2383/.test(r.innerText));"
           f" ok(r?[r.innerText.replace(/\\s+/g,' ').slice(0,60),getComputedStyle(r).backgroundColor]:null); }},60)); }})()")
    time.sleep(.5); av = J("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText.trim()).filter(Boolean).join(' | ')") or ''
    chk('B5 depois de Salvar: aviso "Salvo" e a linha salva com o realce verde', 'Salvo' in av and bool(fl) and 'TMG 2383' in fl[0] and fl[1] not in ('rgb(255, 255, 255)', 'rgba(0, 0, 0, 0)'), [av, fl])
    # B4 · indisponível com motivo (Manutenção, perfil que não pode gerar ordens)
    c.goto(U('MA.dc.html#vis=semordem'), 1.6)
    ind = J("(()=>{const b=[...document.querySelectorAll('header button, main button')].find(b=>b.disabled&&b.getClientRects().length); if(!b) return null; const s=getComputedStyle(b); const id=b.getAttribute('aria-describedby'); const m=id&&document.getElementById(id);"
            " return {t:b.innerText.trim(),op:s.opacity,cur:s.cursor,mot:m&&m.getClientRects().length?m.innerText.trim():''};})()")
    chk('B4 indisponível: apagado, cursor de proibido e o motivo em texto ao lado', bool(ind) and float(ind['op']) < 1 and ind['cur'] == 'not-allowed' and bool(ind['mot']), ind)
    chk('B6 sem erro de JS', not (J("window.__err") or ''), J("window.__err"))
finally:
    try: c.close()
    except Exception: pass
    srv.terminate()
print(f'RESULTADO: {len(OK)} ok · {len(FAIL)} falhas')
sys.exit(1 if FAIL else 0)
