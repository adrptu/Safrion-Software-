# -*- coding: utf-8 -*-
"""Retorno de cada ação (proprietário, 14/10/2026: "ao clicar nesse componente ... nao esta dando flash de feedback ao usuário quando muda
para a tela de destino" e "faça o mesmo para todas telas e botoes, inclusive com feedback de salvar, cancelar"), no navegador:
o controle acionado pulsa (g2-acionado); abrir o detalhe na mesma tela realça o bloco de destino e anuncia; ir para outra tela liga a barra
de carga e realça o título da tela nova; salvar, cancelar e descartar confirmam no aviso. Dados sintéticos."""
import sys, os, time, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, servir

R = os.environ.get('RENDER_DIR') or os.path.join(HERE, '_render')
ok_n = 0; falhas = []
def chk(nome, cond, det=''):
    global ok_n
    if cond: ok_n += 1; print('OK  ' + nome, flush=True)
    else: falhas.append(nome); print('FALHA ' + nome + ' · ' + str(det)[:500], flush=True)

p, srv = servir(R); c = Chrome(); J = c.js
c.call('Page.addScriptToEvaluateOnNewDocument', {'source': "window.__e=[];addEventListener('error',e=>window.__e.push(String(e.message)))"})
U = lambda x: f'http://127.0.0.1:{p}/{x}'
def centro(sel):
    return J("(()=>{const e=%s; if(!e) return null; e.scrollIntoView({block:'center'}); const r=e.getBoundingClientRect(); return [r.left+r.width/2,r.top+r.height/2];})()" % sel)
def clica(sel):
    xy = centro(sel)
    if not xy: return False
    c.mouse(*xy); c.mouse(*xy, 'mousePressed', 'left'); c.mouse(*xy, 'mouseReleased', 'left'); return True
def toast(): return J("(()=>{const t=document.querySelector('.g2toast'); return t&&getComputedStyle(t).display!=='none'?t.innerText.trim():'';})()") or ''
def realces(): return J("(window.__g2realces||[]).map(x=>x.txt)") or []
BOT = lambda txt, dentro='main': "[...document.querySelectorAll(%s)].map(r=>[...r.querySelectorAll('button')]).flat().find(b=>b.offsetParent&&b.innerText.trim()===%s)" % (json.dumps(dentro), json.dumps(txt))
try:
    c.aparelho(1440, 900, 1, False)
    c.goto(U('Main.dc.html'), .2); J("localStorage.clear();sessionStorage.clear()")
    # 1 · clique que fica na tela: o próprio botão pulsa
    c.goto(U('PA.dc.html'), 1.0)
    sel = "[...document.querySelectorAll('main button')].find(b=>b.offsetParent&&/^Soja/.test(b.innerText.trim()))"
    clica(sel); time.sleep(.05)
    chk('R1 botão que filtra na mesma tela pulsa ao ser acionado (anel verde)', J("!!document.querySelector('.g2-acionado')") and J("getComputedStyle(document.querySelector('.g2-acionado')).animationName") == 'g2acionado',
        J("[...document.querySelectorAll('.g2-acionado')].map(e=>e.innerText.trim().slice(0,30))"))
    time.sleep(.5)
    chk('R1b o pulso some sozinho', not J("!!document.querySelector('.g2-acionado')"))
    # 2 · cartão que abre o detalhe na mesma tela: o destino é realçado e anunciado
    J("window.__g2realces=[]")
    clica("document.querySelector('main .g2card[aria-label=\"Abrir plano Soja alta tecnologia\"]')"); time.sleep(.9)
    rr = realces(); viv = J("(document.getElementById('g2-vivo')||{}).textContent||''")
    chk('R2 abrir o plano realça o bloco de destino (o detalhe) e anuncia o novo contexto', any('Soja alta tecnologia' in x for x in rr) and 'Soja alta tecnologia' in viv, [rr, viv])
    # 3 · ir para outra tela: barra de carga no clique e título da tela nova realçado na chegada
    c.goto(U('MOD-CRE.dc.html'), 1.0)
    J("document.addEventListener('click',()=>{ setTimeout(()=>{ const b=document.getElementById('g2-carga'); sessionStorage.setItem('carga', b?b.className:''); },0); },true)")
    clica("document.querySelector('main a.mod-cartao')"); time.sleep(1.4)
    chk('R3 o cartão que muda de tela liga a barra de carga no clique e a tela nova chega com o título realçado',
        J("sessionStorage.getItem('carga')") == 'ini' and J("location.pathname").endswith('GE-08.dc.html') and any('Crédito e garantias' in x for x in realces()), [J("sessionStorage.getItem('carga')"), J("location.pathname"), realces()])
    # 4 · formulário: cancelar sem mudar confirma; mudar e descartar confirma; salvar confirma
    c.goto(U('SAF.dc.html'), 1.4)
    clica(BOT('Nova safra')); time.sleep(.6)
    clica(BOT('Cancelar', 'aside[role=dialog]')); time.sleep(.4)
    chk('R4 cancelar o formulário sem mudar nada confirma "Edição cancelada" (sem prometer desfazer o que já foi gravado)', toast() == 'Edição cancelada', toast())
    clica(BOT('Nova safra')); time.sleep(.6)
    J("(()=>{const i=document.querySelector('aside[role=dialog] input[type=text],aside[role=dialog] input:not([type])'); i.focus(); Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(i,'Safra teste'); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true}));})()"); time.sleep(.3)
    clica(BOT('Cancelar', 'aside[role=dialog]')); time.sleep(.4)
    desc = J("[...document.querySelectorAll('aside[role=dialog] button')].map(b=>b.innerText.trim()).filter(t=>/Descartar/.test(t))")
    if desc: clica(BOT(desc[0], 'aside[role=dialog]')); time.sleep(.4)
    chk('R5 mudar e descartar confirma "Alterações descartadas"', toast() == 'Alterações descartadas', [desc, toast()])
    # 5 · menos movimento: o pulso vira anel parado (sem animação)
    c.call('Emulation.setEmulatedMedia', {'features': [{'name': 'prefers-reduced-motion', 'value': 'reduce'}]})
    c.goto(U('PA.dc.html'), 1.0); clica(sel); time.sleep(.05)
    chk('R6 com "menos movimento" o acionado fica com anel parado, sem animação', J("(()=>{const e=document.querySelector('.g2-acionado'); if(!e) return false; const s=getComputedStyle(e); return s.animationName==='none'&&s.outlineStyle==='solid'&&s.outlineColor==='rgb(30, 122, 76)';})()"))
    c.call('Emulation.setEmulatedMedia', {'features': []})
    chk('R7 sem erro de JS', not J("(window.__e||[]).length"), J("window.__e"))
finally:
    c.close() if hasattr(c, 'close') else None
print(f'RESULTADO: {ok_n}/{ok_n + len(falhas)}' + (' · FALHAS: ' + '; '.join(falhas) if falhas else ''))
sys.exit(1 if falhas else 0)
