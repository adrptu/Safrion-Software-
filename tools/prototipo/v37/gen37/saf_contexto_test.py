# -*- coding: utf-8 -*-
"""Achados do Codex 6174131920 na V68.2, no navegador (dados sintéticos):
C · SAF-FAZ-1-CONTEXTO-01: com o chip de uma fazenda escolhido, "Nova safra" nasce nessa fazenda; sem chip, o padrão; editar conserva a
    fazenda da safra existente.
U · DS-RETORNO-2-DUP-01: abrir a safra (troca de etapa) dá um realce e um anúncio só, e não dois.
Uso: python3 saf_contexto_test.py (RENDER_DIR=<dir> serve outro _render)."""
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
BOT = lambda txt, dentro='main': "[...document.querySelectorAll(%s)].map(r=>[...r.querySelectorAll('button')]).flat().find(b=>b.offsetParent&&b.innerText.trim()===%s)" % (json.dumps(dentro), json.dumps(txt))
def clica_js(sel): return J("(()=>{const b=%s; if(!b) return false; b.click(); return true;})()" % sel)
def chip(nome): return clica_js("[...document.querySelectorAll('main button')].find(b=>b.offsetParent&&b.innerText.trim().startsWith(%s))" % json.dumps(nome))
def campo(k):   # SAF-FAZ-2: 'faz' passou a ser o campo Fazendas (múltiplo); vale a única marcada (ou todas, unidas por '; ')
    if k == 'faz': return '; '.join(J("[...document.querySelectorAll('aside[role=dialog] label')].filter(l=>{const i=l.querySelector('input[type=checkbox]'); return i&&i.checked;}).map(l=>l.innerText.trim())") or []) or None
    return J("(()=>{const e=document.getElementById('fx_g_saf_%s'); return e?e.value:null;})()" % k)
def preenche(k, v): J("(()=>{const i=document.getElementById('fx_g_saf_%s'); i.focus(); Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(i,%s); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true}));})()" % (k, json.dumps(v)))
def linha(nome): return J("(()=>{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.indexOf(%s)>=0); return r?r.innerText.replace(/\\s+/g,' '):null;})()" % json.dumps(nome))
try:
    for w in (1440, 390):
        c.aparelho(w, 900 if w > 400 else 844, 1 if w > 400 else 2, w < 400)
        c.goto(U('Main.dc.html'), .2); J("localStorage.clear();sessionStorage.clear()")
        c.goto(U('SAF.dc.html'), 1.4)
        chip('Lagoa Grande'); time.sleep(.4)
        clica_js(BOT('Criar safra')); time.sleep(.6)
        chk(f'C1 {w}: chip Lagoa Grande → "Nova safra" já vem com a Fazenda Lagoa Grande', campo('faz') == 'Lagoa Grande', campo('faz'))
        nome = f'Contraprova de contexto {w}'
        preenche('nome', nome); preenche('ini', '2027-09-01'); preenche('fim', '2028-08-31'); time.sleep(.2)
        clica_js(BOT('Salvar', 'aside[role=dialog]')); time.sleep(1.0)
        faz = J("(()=>{try{ return window.__safRef.linhas().filter(r=>r.nome===%s).map(r=>r.faz); }catch(e){ return null; }})()" % json.dumps(nome))
        # SAF-FAZ-3 (15/10/2026): na etapa 2 a faixa "Trabalhando em" mostra as fazendas da safra em chips ✓ (não mais o texto "Fazenda X")
        ctx = J("[...document.querySelectorAll('#saf-fz .sfz-chip')].map(b=>b.innerText.trim())")
        chk(f'C1b {w}: salvar cria a safra em Lagoa Grande e a faixa mostra a Lagoa Grande (chip ✓)', faz == ['Lagoa Grande'] and ctx == ['✓ Lagoa Grande'], [faz, ctx])
        c.goto(U('SAF.dc.html'), 1.4)
        clica_js(BOT('Criar safra')); time.sleep(.6)
        chk(f'C2 {w}: sem chip, "Nova safra" vem com o padrão (Santa Rita)', campo('faz') == 'Santa Rita', campo('faz'))
        clica_js(BOT('Cancelar', 'aside[role=dialog]')); time.sleep(.4)
        chip('Lagoa Grande'); time.sleep(.4); chip('Todas'); time.sleep(.3); chip('Santa Rita'); time.sleep(.3); chip('Lagoa Grande'); time.sleep(.3)
        # editar a Safra 2026/27 (Santa Rita) com o chip Lagoa Grande: some da lista filtrada; volta a Todas e edita pela linha
        chip('Todas'); time.sleep(.3)
        J("(()=>{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>/Safra 2026\\/27/.test(r.innerText)&&!/Mamão/.test(r.innerText)); const a=r&&[...r.querySelectorAll('button,a,[role=button]')].find(b=>b.innerText.trim()==='Editar'); if(a) a.click();})()"); time.sleep(.6)
        chk(f'C3 {w}: editar a Safra 2026/27 conserva a fazenda dela (Santa Rita), sem receber o filtro', campo('faz') == 'Santa Rita', campo('faz'))
        clica_js(BOT('Cancelar', 'aside[role=dialog]')); time.sleep(.4)
    # U · um anúncio por troca de etapa
    c.aparelho(1440, 900, 1, False)
    c.goto(U('SAF.dc.html'), 1.4); time.sleep(.3)
    J("window.__g2realces=[]; window.__viv=[]; (()=>{const v=document.getElementById('g2-vivo'); if(v) new MutationObserver(()=>window.__viv.push(v.textContent)).observe(v,{childList:true,characterData:true,subtree:true});})()")
    J("(()=>{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>/Safrinha 2027/.test(r.innerText)); const b=r&&[...r.querySelectorAll('button')].find(b=>/^Continuar/.test(b.innerText.trim())); (b||r).click();})()"); time.sleep(1.5)
    rr = J("(window.__g2realces||[]).map(x=>x.txt)") or []; vv = [x for x in (J("window.__viv") or []) if x.strip()]
    chk('U1 abrir a safra (troca de etapa) realça e anuncia uma vez só', len(rr) == 1 and len(vv) <= 1, [rr, vv])
    chk('U2 sem erro de JS', not J("(window.__e||[]).length"), J("window.__e"))
finally:
    c.close() if hasattr(c, 'close') else None
print(f'RESULTADO: {ok_n}/{ok_n + len(falhas)}' + (' · FALHAS: ' + '; '.join(falhas) if falhas else ''))
sys.exit(1 if falhas else 0)
