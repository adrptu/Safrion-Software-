"""Revisão Claude do PR #88 (OS-LOTE-F1) · navegador real, dados sintéticos, perfil Chrome descartável (comp_lib.Chrome).
Ponteiro real (mouse 1440 px; toque 390 px) nos passos de seleção/confirmação; campos de data/fuso/recursos por setter+change (declarado).
Uso (a partir de gen37): GEN37=<gen37> RENDER_DIR=<render> W=1440|390 SAIDA=<pasta> python3 -B ui_rev_test.py
Registra fatos (OBS) e verificações (OK/FALHA); não altera arquivos versionados."""
import json, os, sys, time
G = os.environ['GEN37']; sys.path.insert(0, G)
from comp_lib import Chrome, servir
R = os.environ['RENDER_DIR']; W = int(os.environ.get('W', '1440')); TOQUE = W < 600
SAIDA = os.environ.get('SAIDA', '.'); os.makedirs(SAIDA, exist_ok=True)
res = []
CEN_LS = 'talhao-os-cenario-v1'   # chave do cenário no localStorage (nome CEN_LS, não KEY)
def ok(n, v, info=''):
    res.append(dict(n=f'{W}px · {n}', ok=bool(v), info=str(info)[:600])); print(('OK    ' if v else 'FALHA ') + f'{W}px · {n}' + ('' if v else ' · ' + str(info)[:600]), flush=True)
def obs(n, v): print(f'OBS   {W}px · {n} · {str(v)[:900]}', flush=True); res.append(dict(n=f'{W}px · OBS {n}', ok=None, info=str(v)[:900]))
D = 'document.querySelector(\'aside[aria-label="Agrupamento de operações"]\')'
FOCO = "(()=>{const a=document.activeElement,d=%s;if(!a||a===document.body)return 'BODY';return (d&&d.contains(a)?'DENTRO ':'FORA ')+a.tagName+':'+((a.innerText||a.getAttribute('aria-label')||'').trim().slice(0,40))})()" % D
porta, srv = servir(R); c = None
def esperar(expr, s=6):
    fim = time.monotonic() + s
    while time.monotonic() < fim:
        if c.js(expr): return True
        time.sleep(.1)
    return False
def ponto(sel_js):
    """centro do elemento (após rolar para a vista) ou None"""
    return c.js("(()=>{const e=(%s);if(!e)return null;e.scrollIntoView({block:'center'});const r=e.getBoundingClientRect();return [r.left+r.width/2,r.top+r.height/2]})()" % sel_js)
def toca(sel_js):
    p = ponto(sel_js)
    if not p: return False
    time.sleep(.15); p = ponto(sel_js)
    if TOQUE: c.toque(p[0], p[1])
    else:
        c.call('Input.dispatchMouseEvent', {'type': 'mouseMoved', 'x': p[0], 'y': p[1]})
        c.call('Input.dispatchMouseEvent', {'type': 'mousePressed', 'x': p[0], 'y': p[1], 'button': 'left', 'clickCount': 1})
        c.call('Input.dispatchMouseEvent', {'type': 'mouseReleased', 'x': p[0], 'y': p[1], 'button': 'left', 'clickCount': 1}); time.sleep(.35)
    return True
def bt(txt, dentro=True):
    return "[...document.querySelectorAll(%s)].find(b=>b.offsetParent&&b.innerText.trim()===%s)" % (json.dumps(('aside[aria-label=\"Agrupamento de operações\"] ' if dentro else '') + 'button'), json.dumps(txt))
def chk(oid): return D + ".querySelector('input[aria-label^=\"%s ·\"]')" % oid
def setv(sel, val):
    return c.js("(()=>{const e=%s.querySelector(%s);if(!e)return false;const p=e.tagName==='SELECT'?HTMLSelectElement.prototype:HTMLInputElement.prototype;Object.getOwnPropertyDescriptor(p,'value').set.call(e,%s);e.dispatchEvent(new Event('input',{bubbles:true}));e.dispatchEvent(new Event('change',{bubbles:true}));return true})()" % (D, json.dumps(sel), json.dumps(val)))
def texto(): return c.js(D + "?" + D + ".innerText.replace(/\\s+/g,' '):''") or ''
def cen(expr): return c.js("(()=>{const c=window.__cen.cenGet();return (%s)})()" % expr)
def perfil(k, url):
    c.js("localStorage.setItem('safrion.perfilDemo',%s)" % json.dumps(k)); c.goto(url)
def filtro_lg():
    return c.js("(()=>{const e=document.querySelector('select[aria-label=\"Filtrar por fazenda\"]');if(!e)return false;Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype,'value').set.call(e,'Lagoa Grande');e.dispatchEvent(new Event('change',{bubbles:true}));return true})()")
try:
    c = Chrome(); c.aparelho(W, 900 if W == 1440 else 844, 1, TOQUE)
    url = f'http://127.0.0.1:{porta}/OS.dc.html'
    c.goto(url); perfil('Caio', url); filtro_lg(); time.sleep(.8)
    # 1 · abrir por teclado: foco entra no painel? Esc fecha sem Tab?
    c.js(bt('Agrupar operações compatíveis', False) + '.focus()'); c.tecla('Enter', 'Enter', 13, text='\r'); esperar('!!' + D)
    f1 = c.js(FOCO); obs('foco logo após abrir pelo teclado', f1)
    c.tecla('Escape', 'Escape', 27); time.sleep(.5); aberto = c.js('!!' + D)
    ok('Esc logo após abrir (sem Tab) fecha o painel', not aberto, f'aberto={aberto} foco={f1}')
    if aberto: toca(D + ".querySelector('header button')"); time.sleep(.4)
    # 2 · seleção por ponteiro
    toca(bt('Agrupar operações compatíveis', False)); esperar('!!' + D)
    n_linhas = c.js(D + ".querySelectorAll('input[type=checkbox][aria-label]').length"); obs('linhas no painel (recorte LG)', n_linhas)
    for oid in ('OS-0590', 'OS-0591', 'OS-0592'): toca(chk(oid))
    ok('três origens marcadas por ponteiro', c.js("['OS-0590','OS-0591','OS-0592'].every(id=>%s.querySelector('input[aria-label^=\"'+id+' ·\"]').checked)" % D))
    l593 = c.js("(()=>{const i=%s;const l=i&&i.closest('div');return i?[i.disabled,l.innerText.replace(/\\s+/g,' ')]:null})()" % chk('OS-0593'))
    ok('OS-0593 (dose 3) bloqueada com motivo em texto', l593 and l593[0] and 'incompat' in l593[1], l593)
    # 3 · programar recursos na composição
    toca(D + ".querySelector('input[type=checkbox]:not([aria-label])')"); time.sleep(.3)
    ok('campos de programação aparecem', c.js(D + ".querySelector('input[type=datetime-local]')!==null"))
    setv('input[type=datetime-local]', '2026-09-29T08:00'); fus_vazio = c.js(D + ".querySelector('select').value===''")
    obs('fuso inicia vazio (precisa escolher, apesar da janela da origem trazer -03:00)', fus_vazio)
    setv('select', '-03:00')
    sels = c.js("[...%s.querySelectorAll('label select')].map(s=>s.closest('label').innerText.split('\\n')[0].trim())" % D); obs('selects', sels)
    for i, v in enumerate(['T03', 'PJ', 'MAR', 'PAU']):
        c.js("(()=>{const s=[...%s.querySelectorAll('label select')].slice(1)[%d];Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype,'value').set.call(s,%s);s.dispatchEvent(new Event('change',{bubbles:true}))})()" % (D, i, json.dumps(v))); time.sleep(.2)
    toca(bt('Conferir agrupamento')); esperar(bt('Confirmar agrupamento').replace('.find', '.some'))
    t = texto(); obs('prévia (texto)', t[:900])
    ok('prévia: 30 ha, 60 kg, 6,75 h', '30 ha' in t and '60 kg' in t and '6,75 h' in t, t[:300])
    janela = c.js("[...%s.querySelectorAll('p')].map(p=>p.innerText).find(x=>x.startsWith('Janela comum'))" % D); obs('janela comum exibida', janela)
    rec = c.js("[...%s.querySelectorAll('p')].map(p=>p.innerText).filter(x=>/^OS-059\\d · /.test(x)&&/–/.test(x))" % D); obs('blocos programados exibidos', rec)
    ok('janela na mesma hora local dos blocos (08:00, fuso da fazenda)', janela and '08:00' in janela, [janela, rec[:1]])
    ok('primária única no rodapé, ≥44 px, dentro da tela', c.js("(()=>{const f=%s.querySelector('footer');const bs=[...f.querySelectorAll('button')].filter(b=>getComputedStyle(b).backgroundColor==='rgb(30, 122, 76)');const r=bs[0]&&bs[0].getBoundingClientRect();return bs.length===1&&r.height>=44&&r.right<=innerWidth&&r.bottom<=innerHeight})()" % D))
    ok('sem rolagem horizontal da página', c.js('document.documentElement.scrollWidth<=innerWidth+1'))
    c.shot(os.path.join(SAIDA, f'previa-programada-{W}.png'))
    # 4 · duplo toque/clique em Confirmar
    p = ponto(bt('Confirmar agrupamento'))
    if TOQUE: c.toque(p[0], p[1]); c.toque(p[0], p[1])
    else:
        for _ in range(2):
            c.call('Input.dispatchMouseEvent', {'type': 'mousePressed', 'x': p[0], 'y': p[1], 'button': 'left', 'clickCount': 1})
            c.call('Input.dispatchMouseEvent', {'type': 'mouseReleased', 'x': p[0], 'y': p[1], 'button': 'left', 'clickCount': 1})
    time.sleep(.8); t = texto()
    ok('duplo acionamento cria um só grupo e mostra recibo', cen("Object.keys(c.gruposExec||{}).length") == 1 and 'GRP-1 confirmado' in t, [cen("Object.keys(c.gruposExec||{})"), t[:200]])
    ok('agrupar não aprova, não libera, não reserva; programação gravada', cen("['OS-0590','OS-0591','OS-0592'].every(id=>c.ordens[id].etapa==='A liberar'&&!c.ordens[id].reservado&&!((c.ordens[id].osc||{}).ev||[]).length&&c.ordens[id].prog)"))
    c.shot(os.path.join(SAIDA, f'recibo-{W}.png'))
    # 5 · fechar e reabrir "Agrupar operações compatíveis": volta à seleção nova?
    toca(D + ".querySelector('header button')"); time.sleep(.4)
    toca(bt('Agrupar operações compatíveis', False)); esperar('!!' + D); tit = c.js(D + ".querySelector('h2').innerText")
    ok('"Agrupar operações compatíveis" após um grupo abre nova composição', tit == 'Agrupar operações', tit)
    toca(D + ".querySelector('header button')"); time.sleep(.4)
    # 6 · detalhe do grupo pela barra
    toca("[...document.querySelectorAll('[aria-label=\"Agrupamentos de execução\"] button')].find(b=>b.innerText.startsWith('GRP-1'))"); esperar('!!' + D)
    t = texto(); obs('detalhe do grupo (Caio)', t[:700])
    ok('detalhe mostra aprovação pendente por origem', t.count('Aprovação v1 pendente') == 3, t[:400])
    toca(D + ".querySelector('header button')"); time.sleep(.3)
    # 7 · a O.S. de origem informa o agrupamento?
    c.goto(url + '#OS-0590'); time.sleep(.8)
    pan = c.js("(()=>{const a=document.querySelector('aside[role=dialog]');return a?a.innerText.replace(/\\s+/g,' '):''})()") or ''
    obs('detalhe OS-0590 menciona o grupo?', 'GRP-1' in pan)
    ok('detalhe da O.S. mostra recursos programados (Marcos, T03)', 'Marcos' in pan, pan[:300])
    # 8 · Ana (gestora+agrônoma) vê "Liberar para execução" (aprova+libera numa confirmação, regra existente R13): para aprovar sem liberar,
    #     a AL-01 passa a PCP pela própria tela CF-01 (caminho do config_test.py), Ana aprova duas pela O.S. e Caio (PCP) libera pelo grupo
    perfil('Ana', url)
    c.goto(url + '#OS-0590'); time.sleep(.8)
    obs('botões do detalhe OS-0590 (Ana, AL-01 padrão)', c.js("[...document.querySelectorAll('aside[role=dialog] button')].filter(b=>b.offsetParent).map(b=>b.innerText.trim()).filter(Boolean).slice(0,4)"))
    base = f'http://127.0.0.1:{porta}/'
    c.goto(base + 'CF-01.dc.html'); time.sleep(1)
    c.js("(()=>{const r=[...document.querySelectorAll('[role=table]')[1].querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.replace(/\\s+/g,' ').indexOf('AL-01 · Liberar')>=0);if(r)(r.querySelector('.g2pw')||r).click()})()"); time.sleep(.5)
    c.js("(()=>{const d=[...document.querySelectorAll('aside[role=dialog]')].find(x=>x.getClientRects().length);const b=d&&[...d.querySelectorAll('button,a')].find(x=>x.innerText.trim()==='PCP');if(b)b.click()})()"); time.sleep(.4)
    c.js("(()=>{const i=document.querySelector('#cf1_mot');if(!i)return;const P=i.tagName==='TEXTAREA'?HTMLTextAreaElement.prototype:HTMLInputElement.prototype;Object.getOwnPropertyDescriptor(P,'value').set.call(i,'revisão PR #88: aprovar e liberar em pessoas diferentes');i.dispatchEvent(new Event('input',{bubbles:true}));i.dispatchEvent(new Event('change',{bubbles:true}))})()"); time.sleep(.3)
    c.js("(()=>{const d=[...document.querySelectorAll('aside[role=dialog]')].find(x=>x.getClientRects().length);const b=d&&[...d.querySelectorAll('button')].find(x=>x.innerText.trim()==='Salvar alçada');if(b)b.click()})()"); time.sleep(.8)
    l01 = c.js("(()=>{const r=[...document.querySelectorAll('[role=table]')[1].querySelectorAll('[role=row]')].find(r=>r.innerText.indexOf('AL-01')>=0);return r?r.innerText.replace(/\\s+/g,' '):''})()")
    ok('CF-01: AL-01 passa a PCP · Caio (configuração do cenário, pela tela)', 'PCP · Caio' in (l01 or ''), l01)
    for oid in ('OS-0590', 'OS-0591'):
        c.goto(url + '#' + oid); time.sleep(.9)
        bts = c.js("[...document.querySelectorAll('aside[role=dialog] button')].filter(b=>b.offsetParent).map(b=>b.innerText.trim()).filter(Boolean).slice(0,4)")
        obs(f'botões do detalhe {oid} (Ana, AL-01=PCP)', bts)
        toca("[...document.querySelectorAll('aside[role=dialog] button')].find(b=>b.offsetParent&&b.innerText.trim()==='Aprovar v1')"); time.sleep(.4)
        toca("[...document.querySelectorAll('aside[role=dialog] button')].find(b=>b.offsetParent&&b.innerText.trim()==='Confirmar aprovação')"); time.sleep(.7)
    evs = cen("['OS-0590','OS-0591','OS-0592'].map(id=>((c.ordens[id].osc||{}).ev||[]).map(e=>e.cmd+' '+e.v).join(','))"); obs('eventos após aprovar', evs)
    ok('aprovar pela O.S. grava só CMD-42 (sem CMD-06) e mantém A liberar', evs[0] == 'CMD-42 v1' and evs[1] == 'CMD-42 v1' and evs[2] == '' and cen("c.ordens['OS-0590'].etapa") == 'A liberar', evs)
    perfil('Caio', url); filtro_lg(); time.sleep(.5)
    toca("[...document.querySelectorAll('[aria-label=\"Agrupamentos de execução\"] button')].find(b=>b.innerText.startsWith('GRP-1'))"); esperar('!!' + D)
    dis = c.js("['OS-0590','OS-0591','OS-0592'].map(id=>{const i=%s.querySelector('input[aria-label^=\"'+id+' ·\"]');return i?i.disabled:null})" % D)
    ok('no grupo, só as aprovadas e prontas ficam selecionáveis', dis == [False, False, True], dis)
    toca(chk('OS-0590')); toca(chk('OS-0591'))
    toca(bt('Conferir liberação')); time.sleep(.5); t = texto(); obs('confirmação de liberação', t[:400])
    # 9 · recarregar no meio: o rascunho de liberação some? nada gravado?
    c.goto(url); filtro_lg(); time.sleep(.5)
    ok('recarregar antes de confirmar não libera nada', cen("['OS-0590','OS-0591'].every(id=>c.ordens[id].etapa==='A liberar')"))
    toca("[...document.querySelectorAll('[aria-label=\"Agrupamentos de execução\"] button')].find(b=>b.innerText.startsWith('GRP-1'))"); esperar('!!' + D)
    toca(chk('OS-0590')); toca(chk('OS-0591')); toca(bt('Conferir liberação')); time.sleep(.4)
    p = ponto(bt('Liberar selecionadas'))
    if p:
        if TOQUE: c.toque(p[0], p[1]); c.toque(p[0], p[1])
        else:
            for _ in range(2):
                c.call('Input.dispatchMouseEvent', {'type': 'mousePressed', 'x': p[0], 'y': p[1], 'button': 'left', 'clickCount': 1})
                c.call('Input.dispatchMouseEvent', {'type': 'mouseReleased', 'x': p[0], 'y': p[1], 'button': 'left', 'clickCount': 1})
    time.sleep(1); t = texto(); obs('recibo da liberação', t[:500])
    evs = cen("['OS-0590','OS-0591','OS-0592'].map(id=>c.ordens[id].etapa+'|'+((c.ordens[id].osc||{}).ev||[]).map(e=>e.cmd+' '+e.v).join(','))"); obs('estado após liberar', evs)
    ok('liberação por origem: 2 Liberadas só com CMD-06 novo; 3ª segue A liberar sem eventos', evs == ['Liberadas|CMD-42 v1,CMD-06 v1', 'Liberadas|CMD-42 v1,CMD-06 v1', 'A liberar|'], evs)
    ok('duplo acionamento não duplica movimento/reserva', cen("(c.movs||[]).filter(m=>['OS-0590','OS-0591'].includes(m.os)).length") in (2, 0) and cen("Object.keys(c.recibos||{}).filter(k=>k.indexOf('|OS-059')>0).length") == 2, [cen("(c.movs||[]).filter(m=>['OS-0590','OS-0591'].includes(m.os)).map(m=>m.os+' '+m.tipo)"), cen("Object.keys(c.recibos||{})")])
    c.shot(os.path.join(SAIDA, f'liberacao-{W}.png'))
    # 10 · aba velha: prévia aberta numa aba, outra aba agrupa as mesmas origens; a velha confirma
    c.js("window.__cen.cenReset()"); perfil('Caio', url); filtro_lg(); time.sleep(.4)
    toca(bt('Agrupar operações compatíveis', False)); esperar('!!' + D)
    for oid in ('OS-0590', 'OS-0591'): toca(chk(oid))
    toca(bt('Conferir agrupamento')); time.sleep(.4)
    c.js("(()=>{const X=window.__cen;const r=X.cenMudar(null,k=>{k.gruposExec={'GRP-1':{id:'GRP-1',versao:1,ids:['OS-0590','OS-0591'],historico:[]}};return {msg:'outra aba'}});window.dispatchEvent(new StorageEvent('storage',{key:%s}));return r})()" % json.dumps(CEN_LS)); time.sleep(.4)
    toca(bt('Confirmar agrupamento')); time.sleep(.6); t = texto()
    ok('aba velha: confirmação recusada com motivo, sem segundo grupo', cen("Object.keys(c.gruposExec).length") == 1 and ('vinculada' in t or 'mudou' in t), t[:300])
    ok('sem exceções JavaScript', not c.js('(window.__errs||[]).length'), c.js('window.__errs'))
finally:
    if c: c.close()
    srv.terminate()
    open(os.path.join(SAIDA, f'ui_rev-{W}.json'), 'w').write(json.dumps(res, ensure_ascii=False, indent=1))
v = [r for r in res if r['ok'] is not None]
print(f'RESULTADO {sum(r["ok"] for r in v)}/{len(v)}')
