# -*- coding: utf-8 -*-
"""SAF-FAZ-2 · safra com várias fazendas, no navegador (proprietário, 14/10/2026: "E se planejar safra puder selecionar mais de 1 fazenda e
os talhoes de cada fazenda?"; contraprovas do Codex 6173977617). Dados sintéticos.
F1 criar com duas fazendas · F2 trocar de fazenda na mesma etapa (talhões da fazenda) · F3 "2 fazendas" na escolha · F4 acrescentar fazenda
sem herdar estado · F5 tirar fazenda com vínculo é recusado no campo, nada muda · F6 tirar fazenda vazia · F7 enviar as fazendas: falha numa,
nova tentativa só da que falhou, sem solicitação duplicada · F8 teclado · F9 sem erro de JS. Uso: python3 saf_fazendas_test.py"""
import sys, os, time, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, servir

R = os.environ.get('RENDER_DIR') or os.path.join(HERE, '_render')
ok_n = 0; falhas = []
def chk(nome, cond, det=''):
    global ok_n
    if cond: ok_n += 1; print('OK  ' + nome, flush=True)
    else: falhas.append(nome); print('FALHA ' + nome + ' · ' + str(det)[:600], flush=True)

p, srv = servir(R); c = Chrome(); J = c.js
c.call('Page.addScriptToEvaluateOnNewDocument', {'source': "window.__e=[];addEventListener('error',e=>window.__e.push(String(e.message)))"})
U = lambda x: f'http://127.0.0.1:{p}/{x}'
BOT = lambda txt, dentro='main': "[...document.querySelectorAll(%s)].map(r=>[...r.querySelectorAll('button')]).flat().find(b=>b.offsetParent&&b.innerText.trim()===%s)" % (json.dumps(dentro), json.dumps(txt))
def clica(sel): return J("(()=>{const b=%s; if(!b) return false; b.click(); return true;})()" % sel)
def preenche(k, v): J("(()=>{const i=document.getElementById('fx_g_saf_%s'); i.focus(); Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(i,%s); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true}));})()" % (k, json.dumps(v)))
def marcadas(): return J("[...document.querySelectorAll('aside[role=dialog] label')].filter(l=>{const i=l.querySelector('input[type=checkbox]'); return i&&i.checked;}).map(l=>l.innerText.trim())") or []
def marca(faz): return J("(()=>{const l=[...document.querySelectorAll('aside[role=dialog] label')].find(l=>l.innerText.trim()===%s&&l.querySelector('input[type=checkbox]')); if(!l) return false; l.querySelector('input').click(); return true;})()" % json.dumps(faz))
def linhas(): return J("window.__safRef.linhas().map(r=>({id:r.id,nome:r.nome,faz:r.faz,mae:r.mae||null,estado:r.estado||''}))") or []
def toast(): return J("(()=>{const t=document.querySelector('.g2toast'); return t&&getComputedStyle(t).display!=='none'?t.innerText.trim():'';})()") or ''
def faixa(): return J("(()=>{const g=document.getElementById('saf-fazendas'); if(!g||!g.offsetParent) return null; return {chips:[...g.querySelectorAll('button[aria-pressed]')].map(b=>[b.innerText.trim(),b.getAttribute('aria-pressed')]),txt:g.innerText.replace(/\\s+/g,' ')};})()")
def editar(pred):   # pred: expressão JS sobre a linha r
    return J("(()=>{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>%s); const a=r&&[...r.querySelectorAll('button,a,[role=button]')].find(b=>b.innerText.trim()==='Editar'); if(a) a.click(); return !!a;})()" % pred) and (time.sleep(.6) or True)
S2627 = r"/Safra 2026\/27/.test(r.innerText)&&/Santa Rita/.test(r.innerText)&&!/Mamão/.test(r.innerText)"
def salvar(): clica(BOT('Salvar', 'aside[role=dialog]')); time.sleep(1.0)
def erro_campo(): return J("(()=>{const a=document.querySelector('aside[role=dialog]'); return a?a.innerText.replace(/\\s+/g,' '):'';})()") or ''
def trocar_safra():
    if not clica(BOT('Trocar safra')): clica("[...document.querySelectorAll('button,a')].find(b=>b.offsetParent&&/Trocar safra/.test(b.innerText))")
    time.sleep(.6)
try:
    for w in (1440, 390):
        c.aparelho(w, 900 if w > 400 else 844, 1 if w > 400 else 2, w < 400)
        c.goto(U('Main.dc.html'), .2); J("localStorage.clear();sessionStorage.clear()")
        c.goto(U('SAF.dc.html'), 1.4)
        # F1 · nova safra com Santa Rita + Lagoa Grande
        clica(BOT('Nova safra')); time.sleep(.6)
        m0 = marcadas(); marca('Lagoa Grande'); time.sleep(.2)
        nome = f'Safra 2027/28 · {w}'
        preenche('nome', nome); preenche('ini', '2027-09-01'); preenche('fim', '2028-08-31'); time.sleep(.2); salvar()
        ls = [x for x in linhas() if x['nome'] == nome]; t1 = toast(); fx = faixa()
        chk(f'F1 {w}: "Nova safra" com Santa Rita e Lagoa Grande cria uma sub-safra por fazenda, ligadas, em rascunho; abre a primeira com a faixa das fazendas',
            m0 == ['Santa Rita'] and [x['faz'] for x in ls] == ['Santa Rita', 'Lagoa Grande'] and ls[0]['mae'] and ls[0]['mae'] == ls[1]['mae']
            and all(x['estado'] == 'Rascunho' for x in ls) and '2 fazendas' in t1 and fx and fx['chips'] == [['Santa Rita', 'true'], ['Lagoa Grande', 'false']], [m0, ls, t1, fx])
        time.sleep(.6); tal_sr = J("(()=>{const t=document.querySelector('main').innerText; return t.indexOf('T7')>=0&&t.indexOf('Pivô')<0;})()")
        if not tal_sr: print('   (diag) main SR:', (J("document.querySelector('main').innerText") or '')[:600].replace('\n',' | '))
        # F2 · troca de fazenda na mesma etapa
        clica("document.querySelector('#saf-fazendas button[aria-pressed=false]')"); time.sleep(1.0)
        fx2 = faixa(); st = J("[window.__safSelf.state.saf,window.__safSelf.state.step]"); txt = J("document.querySelector('main').innerText")
        chk(f'F2 {w}: tocar em Lagoa Grande abre a sub-safra dela na mesma etapa (2), com os talhões da Lagoa Grande e não os da Santa Rita',
            fx2 and fx2['chips'] == [['Santa Rita', 'false'], ['Lagoa Grande', 'true']] and st and st[0] == ls[1]['id'] and st[1] == 2 and tal_sr and 'Pivô' in txt and 'T7' not in txt
            and 'Fazenda Lagoa Grande' in J("document.body.innerText"), [fx2, st, tal_sr])
        # F3 · na escolha da safra, "2 fazendas"
        trocar_safra()
        n2 = J("[...document.querySelectorAll('[role=row].g2ed')].filter(r=>r.innerText.indexOf(%s)>=0).map(r=>/2 fazendas/.test(r.innerText))" % json.dumps(nome))
        chk(f'F3 {w}: na escolha da safra as duas linhas dizem "2 fazendas"', n2 == [True, True], n2)
    # F4–F7 a 1440
    c.aparelho(1440, 900, 1, False)
    c.goto(U('Main.dc.html'), .2); J("localStorage.clear();sessionStorage.clear()"); c.goto(U('SAF.dc.html'), 1.4)
    antes = {x['id']: x for x in linhas()}
    editar(S2627)
    m4 = marcadas(); marca('Lagoa Grande'); time.sleep(.2); salvar()
    l4 = linhas(); s4 = next(x for x in l4 if x['id'] == 'S2627'); n4 = [x for x in l4 if x['mae'] and x['id'] != 'S2627']
    chk('F4 acrescentar Lagoa Grande à Safra 2026/27: S2627 conserva ID e estado (Em planejamento); a nova sub-safra nasce em rascunho, com a mesma mãe',
        m4 == ['Santa Rita'] and s4['estado'] == 'Em planejamento' and s4['mae'] and len(n4) == 1 and n4[0]['faz'] == 'Lagoa Grande' and n4[0]['estado'] == 'Rascunho'
        and n4[0]['mae'] == s4['mae'] and 'Lagoa Grande entrou na safra em rascunho' in toast(), [m4, s4, n4, toast()])
    # F5 · tirar Santa Rita (cultivos e SOL-2026-07) é recusado no campo, sem mudar nada
    l5a = linhas(); editar(S2627); marca('Santa Rita'); time.sleep(.2); salvar()
    e5 = erro_campo(); l5 = linhas()
    chk('F5 tirar Santa Rita da Safra 2026/27 é recusado no campo Fazendas, com o motivo (cultivos e SOL-2026-07) e onde resolver; nada muda',
        'Santa Rita não pode sair da safra' in e5 and 'SOL-2026-07' in e5 and 'resolva em' in e5 and l5 == l5a, [e5[:400], l5 == l5a])
    clica(BOT('Cancelar', 'aside[role=dialog]')); time.sleep(.4)
    if J("!!document.querySelector('aside[role=dialog]')"):
        clica("[...document.querySelectorAll('aside[role=dialog] button')].find(b=>/Descartar/.test(b.innerText))"); time.sleep(.4)
    # F6 · tirar a fazenda vazia
    editar(S2627); marca('Lagoa Grande'); time.sleep(.2); salvar()
    l6 = linhas(); s6 = next(x for x in l6 if x['id'] == 'S2627')
    chk('F6 tirar a Lagoa Grande vazia: a sub-safra sai e a Safra 2026/27 volta a uma fazenda, com o mesmo ID e estado', len(l6) == len(antes) and not s6['mae']
        and s6['estado'] == 'Em planejamento' and 'Lagoa Grande saiu da safra' in toast(), [l6, toast()])
    # F7 · enviar as fazendas: a gravação da 1ª falha (navegador sem espaço); a nova tentativa só envia a que falhou
    editar("/Safrinha 2027/.test(r.innerText)"); marca('Lagoa Grande'); time.sleep(.2); salvar()
    c.goto(U('SAF.dc.html#saf=S27SF&passo=demanda'), 2.0)
    J("(()=>{window.__falhar=1; const o=Storage.prototype.setItem; Storage.prototype.setItem=function(k,v){ if(k==='talhao-os-compras-v1'&&window.__falhar>0){ window.__falhar--; throw new Error('QuotaExceededError'); } return o.call(this,k,v); };})()")
    env = J("(()=>{const b=document.getElementById('sg-env'); return b&&b.offsetParent?b.innerText.trim():null;})()")
    clica("document.getElementById('sg-env')"); time.sleep(.8); t7 = toast()
    sol1 = J("(()=>{ try{ return Object.keys((JSON.parse(localStorage.getItem('talhao-os-compras-v1'))||{}).sols||{}); }catch(e){ return 'x'; } })()")
    chk('F7 enviar as 2 fazendas com a gravação da Santa Rita falhando: envio parcial, a Lagoa Grande (nada a cotar) conta, nada gravado como enviado da Santa Rita',
        env == 'Enviar as 2 fazendas para cotação' and 'Envio parcial' in t7 and 'Falhou: Santa Rita' in t7 and 'S27SF' not in (sol1 or []), [env, t7, sol1])
    clica("document.getElementById('sg-env')"); time.sleep(.8); t7b = toast()
    sols = J("(()=>{ try{ const o=(JSON.parse(localStorage.getItem('talhao-os-compras-v1'))||{}).sols||{}; return Object.values(o).filter(x=>x.safra==='S27SF').map(x=>x.id); }catch(e){ return 'x'; } })()")
    chk('F7b a nova tentativa envia só a Santa Rita (SOL-2027-02) e reaproveita a Lagoa Grande; uma solicitação só', 'Demanda das 2 fazendas enviada' in t7b and 'SOL-2027-02' in t7b
        and 'já enviada' in t7b and sols == ['SOL-2027-02'], [t7b, sols])
    clica("document.getElementById('sg-env')"); time.sleep(.8); t7c = toast()
    sols2 = J("(()=>{ try{ return Object.values((JSON.parse(localStorage.getItem('talhao-os-compras-v1'))||{}).sols||{}).filter(x=>x.safra==='S27SF').map(x=>[x.id,x.comp||0]); }catch(e){ return 'x'; } })()")
    chk('F7c enviar de novo sem mudança na demanda não duplica nem complementa', sols2 == [['SOL-2027-02', 0]], [t7c, sols2])
    # F8 · teclado a 390: Tab até a fazenda e Enter troca
    c.aparelho(390, 844, 2, True)
    c.goto(U('SAF.dc.html#saf=S27SF&passo=cultivos'), 2.0)
    J("(()=>{const b=document.querySelector('#saf-fazendas button[aria-pressed=false]'); b.focus();})()")
    c.tecla('Enter', 'Enter', 13, '\r'); time.sleep(1.0); fx8 = faixa()
    chk('F8 390 · teclado: foco na fazenda e Enter abre a Lagoa Grande na mesma etapa; a faixa cabe sem rolagem lateral',
        fx8 and fx8['chips'][1] == ['Lagoa Grande', 'true'] and J("window.__safSelf.state.step") == 2 and J("document.documentElement.scrollWidth<=innerWidth"), [fx8, J("window.__safSelf.state.step")])
    chk('F9 sem erro de JS', not J("(window.__e||[]).length"), J("window.__e"))
finally:
    c.close() if hasattr(c, 'close') else None
print(f'RESULTADO: {ok_n}/{ok_n + len(falhas)}' + (' · FALHAS: ' + '; '.join(falhas) if falhas else ''))
sys.exit(1 if falhas else 0)
