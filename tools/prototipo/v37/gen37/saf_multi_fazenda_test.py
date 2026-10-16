# -*- coding: utf-8 -*-
"""SAF-FAZ-3 · várias fazendas por vez e talhão sem plantio, no navegador (dados sintéticos). Pedidos do proprietário de 15/10/2026:
"em planejar safra ainda não aparece opção de selecionar fazendas e talhões de mais de 1 fazenda por vez… bem produtiva, rápida, prática e
fácil e visualmente intuitiva e organizada" e "pode ser que algum talhão o produtor não deseje plantar nada, então isso tem que ser permitido".
A faixa "Trabalhando em": chips ✓ e "+ Fazenda" (lista do DS); incluir; tirar com vínculo recusado no lugar; tirar vazia; etapa 1.
B tabela única agrupada por fazenda; filtro rápido por fazenda ao lado da busca; Situação atravessa o grupo; uma fazenda sem grupo; ação
  numa linha de outra fazenda abre a sub-safra dela.
C "Planejar talhões livres": 3 talhões de 2 fazendas, um cultivo cada, uma vez só (duplo clique e reabrir não duplicam); data fora da
  janela e meta vazia recusam sem gravar nada.
D "Não plantar nesta safra": Sem plantio cinza, fora da pendência, da lista de livres e da demanda; desfazer; talhão com cultivo não oferece.
E etapas 3 e 4 por fazenda; "Enviar as 2 fazendas" gera uma solicitação por fazenda.
F 390 px: lista e painel cabem, sem rolagem lateral. G sem erro de JS.
Uso: python3 saf_multi_fazenda_test.py (RENDER_DIR=<dir> serve outro _render). Emulação no Chrome headless: não é aparelho físico."""
import sys, os, time, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, servir

R = os.environ.get('RENDER_DIR') or os.path.join(HERE, '_render')
ok_n = 0; falhas = []
def chk(nome, cond, det=''):
    global ok_n
    if cond: ok_n += 1; print('OK  ' + nome, flush=True)
    else: falhas.append(nome); print('FALHA ' + nome + ' · ' + str(det)[:900], flush=True)

p, srv = servir(R); c = Chrome(); J = c.js
c.call('Page.addScriptToEvaluateOnNewDocument', {'source': "window.__e=[];addEventListener('error',e=>window.__e.push(String(e.message)))"})
U = lambda x: f'http://127.0.0.1:{p}/{x}'
NAV = [0]
def espera(expr, lim=6.0):
    fim = time.monotonic() + lim
    while time.monotonic() < fim:
        try:
            if J('(()=>{try{return !!(' + expr + ')}catch(e){return false}})()'): return True
        except Exception: pass
        time.sleep(.1)
    return False
def abre(h, w=1440):
    NAV[0] += 1; c.aparelho(w, 900 if w > 400 else 844, 1 if w > 400 else 2, w < 400)
    c.goto(U('Main.dc.html'), .2); J("localStorage.clear();sessionStorage.clear()")
    c.goto(U(f'SAF.dc.html?r={NAV[0]}{h}'), 1.2); espera("window.__safSelf&&document.querySelector('[role=table]')")
def clica(expr): return J("(()=>{const b=%s; if(!b) return false; b.click(); return true;})()" % expr)
def toast(): return J("(()=>{const t=document.querySelector('.g2toast'); return t&&getComputedStyle(t).display!=='none'?t.innerText.trim():'';})()") or ''
def espera_toast(trecho, lim=4.0): espera("(document.querySelector('.g2toast')||{}).innerText&&document.querySelector('.g2toast').innerText.indexOf(%s)>=0" % json.dumps(trecho), lim); return toast()
def chips(): return J("[...document.querySelectorAll('#saf-fz .sfz-chip')].map(b=>b.innerText.trim())") or []
def faixa_txt(): return J("(()=>{const f=document.querySelector('.mf-tela'); return f?f.innerText.replace(/\\s+/g,' '):'';})()") or ''
def pop_abre(): clica("document.getElementById('sfz-add')"); return espera("document.getElementById('sfz-pop')")
def pop_ops(): return J("[...document.querySelectorAll('#sfz-pop label')].map(l=>({t:l.querySelector('b').innerText.trim(),sub:l.querySelector('b').nextElementSibling.innerText.trim(),on:l.querySelector('input').checked,err:(l.querySelector('[role=alert]')||{}).innerText||''}))") or []
def pop_marca(faz): return clica("([...document.querySelectorAll('#sfz-pop label')].find(l=>l.querySelector('b').innerText.trim()===%s)||{}).querySelector?.('input')" % json.dumps(faz))
def linhas(): return J("window.__safRef.linhas()") or []
def cultivos(): return J("window.__safRef.cultivos()") or []
def grupos(): return J("[...document.querySelectorAll('[role=table] [role=row].g2fgrp')].filter(r=>r.offsetParent).map(r=>({id:r.getAttribute('data-rid'),t:r.innerText.replace(/[▾▸]/g,'').replace(/\\s+/g,' ').trim()}))") or []
def visiveis(): return J("[...document.querySelectorAll('[role=table] [role=row][data-rid]')].filter(r=>r.offsetParent&&!r.classList.contains('g2fgrp')&&!r.classList.contains('g2kid')).map(r=>r.getAttribute('data-rid'))") or []
def tal_de(rid): return J("(()=>{const r=document.querySelector('[role=row][data-rid=%s]'); if(!r) return null; const c=r.querySelector('.g2c0'); return c?c.innerText.replace(/[▾▸]/g,'').replace(/\\s+/g,' ').trim():null;})()" % json.dumps(rid))
def rid_tal(t): return J("(()=>{const rs=[...document.querySelectorAll('[role=table] [role=row][data-rid]')].filter(r=>r.offsetParent&&!r.classList.contains('g2fgrp')); const r=rs.find(r=>{const c=r.querySelector('.g2c0'); return c&&c.innerText.replace(/[▾▸⚠]/g,'').trim().split(/\\s/)[0]===%s;}); return r?r.getAttribute('data-rid'):null;})()" % json.dumps(t))
def ffz(): return J("[...document.querySelectorAll('[role=group][aria-label=Fazenda] button')].filter(b=>b.offsetParent).map(b=>[b.innerText.trim(),b.getAttribute('aria-pressed')])") or []
def ffz_clica(t): return clica("[...document.querySelectorAll('[role=group][aria-label=Fazenda] button')].find(b=>b.offsetParent&&b.innerText.trim()===%s)" % json.dumps(t))
def qf(): return J("[...document.querySelectorAll('[role=group][aria-label^=\"Filtro rápido\"] button')].filter(b=>b.offsetParent).map(b=>b.innerText.replace(/\\s+/g,' ').trim())") or []
def qf_clica(t): return clica("[...document.querySelectorAll('[role=group][aria-label^=\"Filtro rápido\"] button')].find(b=>b.offsetParent&&b.innerText.replace(/\\s+/g,' ').trim().startsWith(%s))" % json.dumps(t))
def menu_itens(t):
    rid = rid_tal(t); J("(()=>{const r=document.querySelector('[role=row][data-rid=\"%s\"]'); const b=r&&r.querySelector('button.g2mais'); if(b) b.click();})()" % rid); time.sleep(.2)
    return rid, J("[...(document.querySelector('[role=row][data-rid=\"%s\"]')||document).querySelectorAll('.g2mais-menu [role=menuitem]')].map(b=>b.textContent.trim())" % rid) or []
def menu(t, item):
    rid, its = menu_itens(t)
    return clica("[...document.querySelectorAll('[role=row][data-rid=\"%s\"] .g2mais-menu [role=menuitem]')].find(b=>b.textContent.trim()===%s)" % (rid, json.dumps(item)))
def na_linha(t, lab):
    rid = rid_tal(t); return clica("[...document.querySelectorAll('[role=row][data-rid=\"%s\"] button')].find(b=>b.innerText.replace(/\\s+/g,' ').trim()===%s)" % (rid, json.dumps(lab)))
def painel(): return J("(()=>{const a=[...document.querySelectorAll('aside[role=dialog]')].find(x=>x.offsetParent); return a?a.innerText.replace(/\\s+/g,' '):'';})()") or ''
def plt_lista(): return J("[...document.querySelectorAll('#plt-painel label')].filter(l=>l.querySelector('input[type=checkbox]')).map(l=>({t:l.querySelector('b').innerText.trim(),on:l.querySelector('input').checked,err:(l.querySelector('[role=alert]')||{}).innerText||''}))") or []
def plt_marca(want):
    J("(()=>{const w=%s; [...document.querySelectorAll('#plt-painel label')].filter(l=>l.querySelector('input[type=checkbox]')).forEach(l=>{const i=l.querySelector('input'); if(i.checked!==(w.indexOf(l.querySelector('b').innerText.trim())>=0)) i.click();});})()" % json.dumps(want)); time.sleep(.3)
def plt_campo(k, val):
    J("(()=>{const e=document.getElementById('plt_%s'); const pr=e.tagName==='SELECT'?HTMLSelectElement.prototype:HTMLInputElement.prototype; Object.getOwnPropertyDescriptor(pr,'value').set.call(e,%s); e.dispatchEvent(new Event(e.tagName==='SELECT'?'change':'input',{bubbles:true}));})()" % (k, json.dumps(val))); time.sleep(.25)
def plt_val(k): return J("(document.getElementById('plt_%s')||{}).value" % k)
def plt_erro(): return J("(()=>{const a=document.getElementById('plt-painel'); return a?[...a.querySelectorAll('[role=alert]')].map(e=>e.innerText.trim()).join(' | '):'(fechado)';})()") or ''
def k2(): return J("(document.body.innerText.match(/Nesta safra[^\\n]+/)||[''])[0]") or ''
def acoes(): return J("(()=>{const a=document.querySelector('[data-acoes]'); if(!a) return ''; const m=[...a.querySelectorAll('[role=menuitem]')].map(b=>b.textContent); return (a.innerText+' '+m.join(' ')).replace(/\\s+/g,' ');})()") or ''
def dem(saf): return J("(()=>{const m=window.__solo.dem(%s); return Object.keys(m).sort().map(k=>[k,Math.round(m[k].bruta*1000)/1000]);})()" % json.dumps(saf))
try:
    # ---------- A · faixa "Trabalhando em" ----------
    abre('#saf=S27SF&passo=cultivos')
    fx = faixa_txt(); ch0 = chips()
    chk('A1 faixa "Trabalhando em" da etapa 2: a fazenda da safra em chip ✓ e "+ Fazenda" (sem o rótulo de texto "Fazenda Santa Rita")',
        ch0 == ['✓ Santa Rita'] and '+ Fazenda' in fx and 'Fazenda Santa Rita' not in fx and 'Safrinha 2027' in fx, [ch0, fx])
    clica("[...document.querySelectorAll('button.g2xtog')].find(b=>b.offsetParent&&/Expandir tudo/.test(b.innerText))"); espera("[...document.querySelectorAll('button.g2xtog')].some(b=>b.offsetParent&&/Recolher tudo/.test(b.innerText))")   # grupos abertos pela pessoa antes de incluir a fazenda
    pop_abre(); ops = pop_ops()
    chk('A1b "+ Fazenda" abre a lista do DS (popover, não <select>) com as fazendas da organização, área e nº de talhões; Santa Rita marcada',
        [(o['t'], o['on']) for o in ops] == [('Santa Rita', True), ('Boa Vista', False), ('Lagoa Grande', False)]
        and ops[0]['sub'] == '1.165 ha · 8 talhões' and ops[1]['sub'] == '120 ha · 1 talhão' and J("!document.querySelector('#sfz-pop select')"), ops)
    l0 = linhas(); pop_marca('Boa Vista'); t = espera_toast('Boa Vista entrou'); l1 = linhas()
    s1 = next((x for x in l1 if x['id'] == 'S27SF'), {}); bv = next((x for x in l1 if x['faz'] == 'Boa Vista' and x.get('mae')), None)
    chk('A2 marcar Boa Vista inclui a fazenda na safra pelo mesmo comando do SAF-FAZ-2: S27SF conserva ID e estado, a nova nasce em rascunho, ligadas; sem abrir "Editar safra"',
        'Boa Vista entrou na safra em rascunho' in t and chips() == ['✓ Santa Rita', '✓ Boa Vista'] and bv and bv['estado'] == 'Rascunho' and s1.get('mae') == bv['mae']
        and s1.get('estado') == 'Rascunho' and len(l1) == len(l0) + 1 and J("window.__safSelf.state.step") == 2 and not J("!!document.querySelector('aside[role=dialog]')"), [t, chips(), l1])
    BV = bv['id'] if bv else ''
    pop_marca('Santa Rita'); espera("[...document.querySelectorAll('#sfz-pop [role=alert]')].length")
    ops = pop_ops(); er = next((o['err'] for o in ops if o['t'] == 'Santa Rita'), '')
    chk('A3 desmarcar Santa Rita (3 cultivos) é recusado com o motivo no próprio lugar; nada muda (linhas, chips e a marca)',
        'Santa Rita não pode sair da safra' in er and '3 cultivos planejados' in er and linhas() == l1 and chips() == ['✓ Santa Rita', '✓ Boa Vista']
        and next(o['on'] for o in ops if o['t'] == 'Santa Rita'), [er, ops])
    c.tecla('Escape', 'Escape', 27); espera("!document.getElementById('sfz-pop')")
    chk('A4 Esc fecha a lista e devolve o foco ao "+ Fazenda"', J("!document.getElementById('sfz-pop')&&document.activeElement&&document.activeElement.id==='sfz-add'"))
    # ---------- B · tabela única agrupada por fazenda ----------
    g = grupos(); vis = visiveis()
    chk('B1 a tabela mostra os talhões das duas fazendas juntos, um grupo por fazenda (aberto, mesmo com grupos já abertos antes) com área e "x de y talhões planejados"',
        [x['id'] for x in g] == ['fzg_S27SF', 'fzg_' + BV] and g[0]['t'].startswith('Santa Rita 553 ha · 3 de 8 talhões planejados')
        and g[1]['t'].startswith('Boa Vista 0 ha · 0 de 1 talhão planejado') and 'tal_B1' in vis and 'tal_T3' in vis
        and J("(document.querySelector('[role=table] .g2tot')||{}).innerText||''").replace('\n', ' ').count('553 ha') == 1, [g, vis])
    fz = ffz(); dep = J("(()=>{const s=[...document.querySelectorAll('input[type=search]')].find(x=>x.offsetParent); const f=[...document.querySelectorAll('[role=group][aria-label=Fazenda]')].find(x=>x.offsetParent); const q=[...document.querySelectorAll('[role=group][aria-label^=\"Filtro rápido\"]')].find(x=>x.offsetParent); return !!(s&&f&&q&&(s.compareDocumentPosition(f)&Node.DOCUMENT_POSITION_FOLLOWING)&&(f.compareDocumentPosition(q)&Node.DOCUMENT_POSITION_FOLLOWING));})()")
    ffz_clica('Boa Vista'); espera("[...document.querySelectorAll('[role=table] [role=row].g2fgrp')].filter(r=>r.offsetParent).length===1")
    g2 = grupos(); v2 = visiveis(); ffz_clica('Todas'); espera("[...document.querySelectorAll('[role=table] [role=row].g2fgrp')].filter(r=>r.offsetParent).length===2")
    chk('B2 filtro rápido por fazenda logo depois da busca (Todas · Santa Rita · Boa Vista): Boa Vista mostra só o grupo dela; Todas volta às duas',
        fz == [['Todas', 'true'], ['Santa Rita', 'false'], ['Boa Vista', 'false']] and dep and [x['id'] for x in g2] == ['fzg_' + BV] and v2 == ['tal_B1'] and len(grupos()) == 2, [fz, dep, g2, v2])
    q0 = qf(); qf_clica('Livre'); espera("[...document.querySelectorAll('[role=table] [role=row][data-rid]')].filter(r=>r.offsetParent&&!r.classList.contains('g2fgrp')).length<5")
    v3 = visiveis(); qf_clica('Todas')
    chk('B3 o filtro rápido da Situação atravessa o grupo da fazenda: conta e filtra os talhões das duas (Livre: T1 e B1)',
        'Todas 9' in q0 and 'Livre 2' in q0 and sorted(v3) == ['grp_T1', 'tal_B1'], [q0, v3])
    na_linha('B1', 'Planejar ›'); espera("[...document.querySelectorAll('aside[role=dialog]')].some(a=>a.offsetParent&&/Planejar B1/.test(a.innerText))")
    pn = painel(); st = J("window.__safSelf.state.saf")
    chk('B4 "Planejar ›" no B1 (outra fazenda) abre o painel na sub-safra da Boa Vista, com o contexto herdado; a tabela continua a mesma (2 grupos)',
        'Planejar B1' in pn and 'Boa Vista · Safrinha 2027 · B1 120 ha' in pn and st == BV and len(grupos()) == 2, [pn[:300], st, grupos()])
    clica("[...document.querySelectorAll('aside[role=dialog] button')].find(b=>b.offsetParent&&b.innerText.trim()==='Cancelar')"); espera("![...document.querySelectorAll('aside[role=dialog]')].some(a=>a.offsetParent)")
    # ---------- C · planejar vários talhões livres de uma vez ----------
    n0 = len(cultivos()); clica("document.getElementById('plt-abrir')"); espera("document.getElementById('plt-painel')")
    pl = plt_lista(); pn = painel()
    chk('C1 "Planejar talhões livres…" abre o painel com os livres das duas fazendas (marcados), por fazenda, e o contexto herdado (safra, fazendas, cultura e plano mais usados; meta vazia)',
        [x['t'] for x in pl] == ['T1', 'T3', 'T4', 'P2', 'B1'] and all(x['on'] for x in pl) and 'Safrinha 2027 · Santa Rita e Boa Vista' in pn and 'Santa Rita · 4 livres' in pn
        and 'Boa Vista · 1 livre' in pn and plt_val('cult') == 'Milho' and plt_val('plano') == 'MILHO-SF' and plt_val('meta') == '', [pl, pn[:400]])
    plt_marca(['T1', 'T3', 'B1']); dflt = plt_val('plantio'); plt_campo('meta', '')
    clica("document.getElementById('plt-gravar')"); time.sleep(.4); e1 = plt_erro(); n1 = len(cultivos())
    plt_campo('meta', '110'); plt_campo('plantio', '2027-02-01'); clica("document.getElementById('plt-gravar')"); espera("document.querySelectorAll('#plt-painel label [role=alert]').length")
    e2 = plt_erro(); pl2 = plt_lista(); n2 = len(cultivos())
    chk('C2 recusa sem gravar: meta vazia pede a meta; plantio 01/02/2027 antes de o T1 liberar trava o T1 no próprio item; nada é gravado',
        dflt == '2027-02-21' and 'Informe a meta' in e1 and n1 == n0 and next(x['err'] for x in pl2 if x['t'] == 'T1') and 'Nada foi gravado' in e2
        and n2 == n0 and J("!!document.getElementById('plt-painel')"), [dflt, e1, e2[:400], n0, n1, n2])
    plt_campo('plantio', '2027-02-21')
    J("(()=>{const b=document.getElementById('plt-gravar'); b.click(); b.click();})()")   # duplo clique: o mesmo comando duas vezes
    t = espera_toast('talhões planejados'); cs = cultivos(); novos = [x for x in cs if x['plantio'] == '2027-02-21' and x['cult'] == 'Milho']
    chk('C3 "Planejar 3 talhões" de 2 fazendas grava 3 cultivos, um por talhão, cada um na sub-safra da sua fazenda, uma vez só (duplo clique não duplica)',
        len(cs) == n0 + 3 and sorted(x['talhao'] for x in novos) == ['B1', 'T1', 'T3'] and all(x['plano'] == 'MILHO-SF' for x in novos)
        and next(x['saf'] for x in novos if x['talhao'] == 'B1') == BV and next(x['faz'] for x in novos if x['talhao'] == 'B1') == 'Boa Vista'
        and all(x['saf'] == 'S27SF' for x in novos if x['talhao'] != 'B1') and '3 talhões planejados: T1, T3 (Santa Rita) e B1 (Boa Vista)' in t, [t, novos, len(cs), n0])
    clica("document.getElementById('plt-abrir')"); espera("document.getElementById('plt-painel')"); pl3 = [x['t'] for x in plt_lista()]
    clica("[...document.querySelectorAll('#plt-painel button')].find(b=>b.innerText.trim()==='Cancelar')"); espera("!document.getElementById('plt-painel')")
    g3 = grupos()
    chk('C4 reabrir não repete: T1, T3 e B1 saem da lista de livres; os grupos contam os planejados', pl3 == ['T4', 'P2'] and len(cultivos()) == n0 + 3
        and '4 de 8 talhões planejados' in g3[0]['t'] and '1 de 1 talhão planejado' in g3[1]['t'], [pl3, g3])
    pop_abre(); pop_marca('Boa Vista'); espera("[...document.querySelectorAll('#sfz-pop [role=alert]')].length"); er = next((o['err'] for o in pop_ops() if o['t'] == 'Boa Vista'), '')
    chk('A5 com o cultivo do B1, tirar a Boa Vista também é recusado no lugar', 'Boa Vista não pode sair da safra' in er and '1 cultivo planejado' in er and chips() == ['✓ Santa Rita', '✓ Boa Vista'], er)
    l5 = linhas(); pop_marca('Lagoa Grande'); espera_toast('Lagoa Grande entrou'); ch5 = chips(); pop_marca('Lagoa Grande'); t5 = espera_toast('Lagoa Grande saiu')
    chk('A6 incluir e tirar a Lagoa Grande vazia: entra em rascunho e sai sem deixar sub-safra; as outras não mudam',
        ch5 == ['✓ Santa Rita', '✓ Boa Vista', '✓ Lagoa Grande'] and 'Lagoa Grande saiu da safra' in t5 and linhas() == l5 and chips() == ['✓ Santa Rita', '✓ Boa Vista'], [ch5, t5])
    c.tecla('Escape', 'Escape', 27); espera("!document.getElementById('sfz-pop')")
    # ---------- D · talhão sem plantio ----------
    d0 = dem('S27SF'); nc0 = len(cultivos()); _, it2 = menu_itens('T2'); c.tecla('Escape', 'Escape', 27)
    rid4, it4 = menu_itens('T4')
    menu('T4', 'Não plantar nesta safra'); t = espera_toast('sem plantio'); time.sleep(.3)
    r4 = tal_de(rid_tal('T4')); g4 = grupos(); q4 = qf()
    chk('D1 "Não plantar nesta safra" no ⋯ do T4 livre: fica "Sem plantio" (chip cinza na linha, sem Planejar ›), conta no grupo e na faixa; talhão com cultivo (T2) não oferece',
        'Não plantar nesta safra' in it4 and 'Não plantar nesta safra' not in it2 and 'T4 sem plantio nesta safra' in t and r4 and 'Sem plantio' in r4 and 'Planejar' not in r4
        and '1 sem plantio' in g4[0]['t'] and 'Sem plantio 1' in q4 and 'Sem plantio 204' in k2()
        and J("JSON.stringify(window.__safRef.semPlantio().S27SF)") == '{"faz":"Santa Rita","tal":{"T4":true}}', [it4, it2, t, r4, g4, q4, k2()])
    cor = J("(()=>{const r=document.querySelector('[role=row][data-rid=tal_T4]'); const ch=[...r.querySelectorAll('.g2c0 span')].find(s=>s.innerText.trim()==='Sem plantio'); return ch?getComputedStyle(ch).color:null;})()")
    d1 = dem('S27SF'); clica("document.getElementById('plt-abrir')"); espera("document.getElementById('plt-painel')"); pl4 = [x['t'] for x in plt_lista()]
    clica("[...document.querySelectorAll('#plt-painel button')].find(b=>b.innerText.trim()==='Cancelar')"); espera("!document.getElementById('plt-painel')")
    ac = acoes()
    chk('D2 Sem plantio não é pendência: sem cor de alerta, fora da lista de livres, a etapa avança (Dimensionar operações ›) e a nota não cita o T4; nada entra em cultivo nem na demanda',
        cor and cor not in ('rgb(180, 35, 24)', 'rgb(161, 98, 7)') and pl4 == ['P2'] and 'Dimensionar operações' in ac and 'T4' not in ac and len(cultivos()) == nc0 and d1 == d0, [cor, pl4, ac, d0 == d1])
    menu('T4', 'Voltar a planejar'); t = espera_toast('volta a ser planejado'); r4b = tal_de(rid_tal('T4'))
    chk('D3 "Voltar a planejar" desfaz: o T4 volta com Planejar › e sai das marcas', 'Planejar ›' in (r4b or '') and 'Sem plantio' not in (r4b or '')
        and J("JSON.stringify(window.__safRef.semPlantio().S27SF.tal)") == '{}', [t, r4b])
    menu('T4', 'Não plantar nesta safra'); espera_toast('sem plantio')
    # ---------- E · etapas 3 e 4 e a solicitação, por fazenda ----------
    clica("document.querySelector('[data-acoes] [data-acao=avancar]')"); espera("window.__safSelf.state.step===3")
    f3 = J("(()=>{const g=document.getElementById('saf-fazendas'); return g&&g.offsetParent?[...g.querySelectorAll('button[aria-pressed]')].map(b=>b.innerText.trim()):null;})()")
    clica("document.querySelector('[data-acoes] [data-acao=avancar]')"); espera("window.__safSelf.state.step===4&&document.getElementById('sg-env')")
    env = J("(document.getElementById('sg-env')||{}).innerText"); clica("document.getElementById('sg-env')"); t = espera_toast('Demanda das 2 fazendas')
    sols = J("(()=>{ try{ return Object.values((JSON.parse(localStorage.getItem('talhao-os-compras-v1'))||{}).sols||{}).map(x=>[x.safra,Object.keys(x.itens||{}).length]); }catch(e){ return 'x'; } })()") or []
    chk('E1 etapas 3 e 4 seguem por fazenda (Santa Rita · Boa Vista) e "Enviar as 2 fazendas para cotação" gera uma solicitação por fazenda, com itens',
        f3 == ['Santa Rita', 'Boa Vista'] and env == 'Enviar as 2 fazendas para cotação' and 'Santa Rita: SOL-' in t and 'Boa Vista: SOL-' in t
        and sorted(x[0] for x in sols) == sorted(['S27SF', BV]) and all(x[1] > 0 for x in sols), [f3, env, t, sols])
    # ---------- B5 · uma fazenda só: sem nível de grupo; etapa 1 com safra escolhida mostra os chips ----------
    abre('#saf=S2627&passo=cultivos')
    chk('B5 safra de uma fazenda (S2627): sem o nível de grupo e sem o filtro de fazenda; chip ✓ Santa Rita na faixa',
        not grupos() and not ffz() and chips() == ['✓ Santa Rita'] and 'tal_T1' not in visiveis() and len(visiveis()) == 8, [grupos(), ffz(), chips(), visiveis()])
    clica("[...document.querySelectorAll('[data-acoes] button')].find(b=>b.innerText.trim()==='‹ Trocar safra')"); espera("window.__safSelf.state.step===1")
    chk('A7 na etapa 1 com a safra escolhida, a faixa continua com os chips e "+ Fazenda"', chips() == ['✓ Santa Rita'] and J("!!document.getElementById('sfz-add')"), [chips(), faixa_txt()])
    # ---------- F · 390 px ----------
    abre('#saf=S27SF&passo=cultivos', 390)
    pop_abre(); bx = J("(()=>{const r=document.getElementById('sfz-pop').getBoundingClientRect(); return [r.left,r.right,innerWidth];})()")
    pop_marca('Boa Vista'); espera_toast('Boa Vista entrou'); c.tecla('Escape', 'Escape', 27); espera("!document.getElementById('sfz-pop')")
    fit = J("(()=>{const t=[...document.querySelectorAll('[role=table]')].find(x=>x.offsetParent); const tr=t.getBoundingClientRect(); return [...t.querySelectorAll('.g2fgrp .g2pw')].every(p=>p.getBoundingClientRect().right<=tr.right+1);})()")
    clica("document.getElementById('plt-abrir')"); espera("document.getElementById('plt-painel')")
    pb = J("(()=>{const r=document.getElementById('plt-painel').getBoundingClientRect(); return [r.left,r.right,innerWidth];})()")
    chk('F1 390: a lista de fazendas e o painel cabem na tela; o cabeçalho do grupo cabe na parte visível da tabela; sem rolagem lateral',
        bx and bx[0] >= 0 and bx[1] <= bx[2] and fit and pb and pb[0] >= 0 and pb[1] <= pb[2] and J("document.documentElement.scrollWidth<=innerWidth"), [bx, fit, pb])
    chk('G sem erro de JS', not J("(window.__e||[]).length"), J("window.__e"))
finally:
    c.close()
    srv.terminate()
print(f'RESULTADO: {ok_n}/{ok_n + len(falhas)}' + (' · FALHAS: ' + '; '.join(falhas) if falhas else ''))
sys.exit(1 if falhas else 0)
