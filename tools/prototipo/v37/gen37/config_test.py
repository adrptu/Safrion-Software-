# -*- coding: utf-8 -*-
"""CONF-01 · Configurações no Chrome real (substitui o cftest.py): CF-01 Usuários e alçadas (P4), CF-04 Auditoria (P5), CF-03 Integrações (P6)
e a assinatura no mesmo estado (P7, CF-05 com AL-15), em 1440 px e em 390 px.
Fluxo principal: normal (AL-01 → PCP e a O.S. separa aprovar e liberar; AL-05 pendente e confirmada por outro gestor; Resolver AL-12;
convidar Beto), erro/recusa (autoconcessão, último gestor, perfil sem gestor) e repetição (duplo clique = um registro).
Cada parte parte do seed (cenReset). Uma primária (verde cheio) por tela; com o painel aberto, só a do painel (medida v3.1 do acao_unica_test.py).
rev = reverificação adversarial do 8be23d8 (10/10): colheita pela web confere quem age, encerrar grava quem agiu, detalhe da trilha estável
e ninguém retira todos os próprios papéis.
rev2 = rodada de 13/10 (S3/S4 restantes): duplo clique real, realce estável, 390 px, teclado, foco no painel, chave da dispensa e Compra pelo Ver como.
Uso (de gen37/, depois de build e montar_render): python3 config_test.py [cf01] [cf04] [cf03] [cf05] [rev] [rev2] [m390]   (sem argumento: todas; sai 1 se alguma falhar)
RDIR=<pasta> serve outra cópia do _render (sonda)."""
import sys, os, time, json, subprocess, re
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from cdp import Chrome
from journeys import free
PARTES = sys.argv[1:] or ['cf01', 'cf04', 'cf03', 'cf05', 'rev', 'rev2', 'm390']
RDIR = os.environ.get('RDIR', os.path.join(HERE, '_render'))
SHOT = os.path.join(HERE, '_probe')
ERRS = ("window.__errs=[];window.addEventListener('error',e=>window.__errs.push(String(e.message)));const __ce=console.error;"
        "console.error=function(){window.__errs.push([...arguments].map(String).join(' ').slice(0,300));__ce.apply(console,arguments);};")
# medida v3.1 (acao_unica_test.py): com painel modal aberto conta só o painel; senão cabeçalho + conteúdo; botão/link verde cheio visível
PRIM = r"""(()=>{const vis=e=>{const r=e.getBoundingClientRect(); const cs=getComputedStyle(e); return r.width>1&&r.height>1&&cs.visibility!=='hidden'&&cs.display!=='none';};
  const n=s=>(s||'').replace(/\s+/g,' ').trim(); const verde=e=>getComputedStyle(e).backgroundColor==='rgb(30, 122, 76)';
  const d=[...document.querySelectorAll('aside[role=dialog]')].find(x=>vis(x)&&x.parentElement&&getComputedStyle(x.parentElement).position==='fixed');
  const raiz=d?[d]:[...document.querySelectorAll('header,main')];
  return {prims:raiz.flatMap(r=>[...r.querySelectorAll('button,a')]).filter(e=>vis(e)&&verde(e)&&!e.closest('.menu-lat')).map(e=>n(e.innerText).slice(0,48)),dialogo:!!d};})()"""
p = free(); srv = subprocess.Popen(['python3', '-m', 'http.server', str(p), '--bind', '127.0.0.1', '--directory', RDIR], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(.7)
c = Chrome(port=free()); J = c.js; c.call('Page.addScriptToEvaluateOnNewDocument', {'source': ERRS}); OK = []


def chk(nome, cond, extra=''):
    OK.append(bool(cond)); print(('OK  ' if cond else 'FALHOU ') + nome + ('' if cond else ' · ' + str(extra)[:600]), flush=True)


def go(f, w=1440, h=1000):   # mesma URL (com âncora) não recarrega: passa por about:blank para o estado e o perfil salvos valerem
    c.size(w, h); c.goto('about:blank', wait=.2); c.goto(f'http://127.0.0.1:{p}/{f}', wait=1.2); time.sleep(.5)


def reset(perfil=''):
    J("(()=>{ try{ localStorage.removeItem('talhao-os-cenario-v1'); localStorage.removeItem('safrion.perfilDemo'); }catch(e){} })()")
    if perfil: J(f"localStorage.setItem('safrion.perfilDemo',{json.dumps(perfil)})")


def perfil(k): J(f"localStorage.setItem('safrion.perfilDemo',{json.dumps(k)})")
def espera(js, ate=20.0):
    """espera a condição observável (página nova pronta), não um tempo fixo; no limite devolve False e a verificação falha"""
    t0 = time.time()
    while time.time() - t0 < ate:
        try:
            if J(js): return True
        except Exception: pass
        time.sleep(.1)
    return False
def pronta(pg, extra='true'): return f"location.pathname.endsWith('/{pg}') && document.readyState==='complete' && !!document.body && ({extra})"
def errs(): return J("(window.__errs||[]).filter(e=>e.indexOf(\"reading 'g2toast'\")<0).join(' | ')") or ''
def hdr(): return J("document.querySelector('header').innerText.replace(/\\s+/g,' ')")
def dlg(): return J("(()=>{const d=[...document.querySelectorAll('aside[role=dialog]')].find(x=>x.getClientRects().length); return d?d.innerText.replace(/\\s+/g,' '):'';})()") or ''
def toast(): return J("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).filter(Boolean).join(' | ')") or ''
def prims(): return J(PRIM)


def clk(t, onde='body'):
    r = J(f"""(()=>{{const n=s=>(s||'').replace(/\\s+/g,' ').trim(); const raiz=[...document.querySelectorAll({json.dumps(onde)})].filter(x=>x.getClientRects().length);
      const els=raiz.flatMap(r=>[...r.querySelectorAll('button,a')]).filter(e=>e.getClientRects().length); const e=els.find(x=>n(x.innerText)===n({json.dumps(t)}))||els.find(x=>n(x.innerText).startsWith(n({json.dumps(t)})));
      if(!e) return 'NÃO ACHEI: '+{json.dumps(t)}; if(e.disabled) return 'DESABILITADO: '+{json.dumps(t)}; e.click(); return 'ok';}})()""")
    time.sleep(.45); return r


def dclk(t):   # duplo clique no mesmo tique (repetição): dois click() seguidos antes de redesenhar
    r = J(f"""(()=>{{const n=s=>(s||'').replace(/\\s+/g,' ').trim(); const e=[...document.querySelectorAll('aside[role=dialog] button')].find(x=>x.getClientRects().length&&n(x.innerText)===n({json.dumps(t)}));
      if(!e) return 'NÃO ACHEI'; e.click(); e.click(); return 'ok';}})()"""); time.sleep(.5); return r


def linha(ti, txt): return J(f"(()=>{{const r=[...document.querySelectorAll('[role=table]')[{ti}].querySelectorAll('[role=row]')].find(r=>r.innerText.replace(/\\s+/g,' ').indexOf({json.dumps(txt)})>=0); return r?r.innerText.replace(/\\s+/g,' '):null;}})()")


def abre(ti, txt):
    r = J(f"(()=>{{const r=[...document.querySelectorAll('[role=table]')[{ti}].querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.replace(/\\s+/g,' ').indexOf({json.dumps(txt)})>=0); if(!r) return false; (r.querySelector('.g2pw')||r).click(); return true;}})()")
    time.sleep(.45); return r


def setv(sel, val):
    J(f"""(()=>{{const i=document.querySelector({json.dumps(sel)}); if(!i) return false; const P=i.tagName==='TEXTAREA'?HTMLTextAreaElement.prototype:HTMLInputElement.prototype;
      Object.getOwnPropertyDescriptor(P,'value').set.call(i,{json.dumps(val)}); i.dispatchEvent(new Event('input',{{bubbles:true}})); i.dispatchEvent(new Event('change',{{bubbles:true}})); return true;}})()"""); time.sleep(.3)


def papel(t):   # liga/desliga um papel no painel da pessoa
    r = J(f"(()=>{{const b=[...document.querySelectorAll('aside[role=dialog] [role=switch]')].find(x=>x.querySelector('.conf-swt').innerText.trim()==={json.dumps(t)}); if(!b) return 'NÃO ACHEI'; if(b.disabled) return 'DESABILITADO'; b.click(); return b.getAttribute('aria-checked');}})()")
    time.sleep(.3); return r


def fl(ti, txt):   # revisão F13: a linha gravada fica realçada (classe g2flash, o fl da grade)
    return J(f"(()=>{{const r=[...document.querySelectorAll('[role=table]')[{ti}].querySelectorAll('[role=row]')].find(r=>r.innerText.replace(/\\s+/g,' ').indexOf({json.dumps(txt)})>=0); return !!r&&r.classList.contains('g2flash');}})()")


def ordem(*txts):   # índice da 1ª linha da trilha (CF-04, mais recente primeiro) que contém cada texto
    return J(f"(()=>{{const R=[...document.querySelectorAll('[role=table]')[0].querySelectorAll('[role=row].g2ed')].map(r=>r.innerText.replace(/\\s+/g,' ')); return {json.dumps(list(txts))}.map(t=>R.findIndex(x=>x.indexOf(t)>=0));}})()")


def aba_js(f, expr):   # segunda aba do mesmo Chrome (outro documento, mesma origem): grava como "outra aba"; o evento storage chega na primeira
    import urllib.request
    from cdp import WS
    t = c.call('Target.createTarget', {'url': f'http://127.0.0.1:{p}/{f}'}); time.sleep(2.5)
    u = [x for x in json.load(urllib.request.urlopen(f'http://127.0.0.1:{c.port}/json')) if x.get('id') == t['targetId']][0]['webSocketDebuggerUrl']
    ws = WS(u); ws.send(json.dumps({'id': 1, 'method': 'Runtime.evaluate', 'params': {'expression': expr, 'returnByValue': True}}))
    while True:
        m = json.loads(ws.recv(timeout=60))
        if m.get('id') == 1: break
    c.call('Target.closeTarget', {'targetId': t['targetId']}); time.sleep(.8)
    return ((m.get('result') or {}).get('result') or {}).get('value')


def dclk_real(sel):   # duplo clique da mão (revisão CONF 13/10): dois eventos de mouse a 120 ms, clickCount 1 e 2, no centro do botão
    rc = J(f"(()=>{{const b=document.querySelector({json.dumps(sel)}); if(!b) return null; const r=b.getBoundingClientRect(); return [r.left+r.width/2, r.top+r.height/2];}})()")
    if not rc: return False
    for cc in (1, 2):
        c.call('Input.dispatchMouseEvent', {'type': 'mousePressed', 'x': rc[0], 'y': rc[1], 'button': 'left', 'clickCount': cc})
        c.call('Input.dispatchMouseEvent', {'type': 'mouseReleased', 'x': rc[0], 'y': rc[1], 'button': 'left', 'clickCount': cc})
        if cc == 1: time.sleep(.12)
    time.sleep(1.0); return True


def tecla(k, code, vk):
    for t in ('keyDown', 'keyUp'): c.call('Input.dispatchKeyEvent', {'type': t, 'key': k, 'code': code, 'windowsVirtualKeyCode': vk})
    time.sleep(.4)


def vercomo(k):   # troca o Ver como pelo seletor da barra lateral (sem recarregar)
    J(f"(()=>{{const s=document.querySelector('.menu-lat select'); const P=HTMLSelectElement.prototype; Object.getOwnPropertyDescriptor(P,'value').set.call(s,{json.dumps(k)}); s.dispatchEvent(new Event('change',{{bubbles:true}})); }})()"); time.sleep(.6)


def nev(): return J("(()=>{ try{ const c=JSON.parse(localStorage.getItem('talhao-os-cenario-v1')||'null'); return (c&&c.conf&&c.conf.ev||[]).length; }catch(e){ return -1; } })()")


try:
    if 'cf01' in PARTES:
        # ---------- seed ----------
        go('CF-01.dc.html'); reset(); go('CF-01.dc.html')
        # navegação sem submenus (13/10/2026, ui37.MENU2/HUB37/CURTO37/VOLTA37): barra só com ícones (aria-label) e, por último, "Outros acessos";
        # os itens do módulo são os cartões da tela de entrada. Como o usuário: "‹ Configurações" → tela de entrada → cartão "Usuários e alçadas"
        nv = J("(()=>{const n=document.querySelector('nav[aria-label=Menu]'); const v=document.querySelector('a.volta37'); return {mods:[...n.querySelectorAll('a[aria-label]')].filter(a=>!a.closest('.ml-topo')).map(a=>a.getAttribute('aria-label')), cur:[...n.querySelectorAll('a[aria-current=page]')].map(a=>a.getAttribute('aria-label')), volta:v?[v.getAttribute('href'),v.innerText.replace(/\\s+/g,' ').trim()]:null};})()") or {}
        J("document.querySelector('a.volta37').click()"); h0 = espera(pronta('MOD-CFG.dc.html', "document.querySelectorAll('a.mod-cartao').length>0"))
        cs = J("[...document.querySelectorAll('a.mod-cartao')].filter(a=>a.getClientRects().length).map(a=>[a.getAttribute('href'),a.innerText.replace(/\\s+/g,' ').trim()])") or []; e0 = errs()
        r1 = clk('Usuários e alçadas', '.mod-grade'); h1 = espera(pronta('CF-01.dc.html', "document.querySelectorAll('[role=table] [role=row]').length>2")); time.sleep(.5)
        ORD = [['CF-01.dc.html', 'Usuários e alçadas'], ['CF-04.dc.html', 'Auditoria'], ['CF-03.dc.html', 'Integrações'], ['CF-05.dc.html', 'Assinatura']]
        chk('A15 navegação: Configurações é o último módulo da barra (antes de Outros acessos), marcado no CF-01; a tela de entrada ("‹ Configurações") tem no máximo 4 cartões na ordem Usuários e alçadas · Auditoria · Integrações · Assinatura, e o cartão abre o CF-01',
            nv.get('mods', [])[-2:] == ['Configurações', 'Outros acessos'] and nv.get('cur') == ['Configurações'] and nv.get('volta') == ['MOD-CFG.dc.html', '‹ Configurações']
            and h0 and len(cs) <= 4 and cs[:1] == ORD[:1] and cs[-1:] == ORD[-1:] and cs == [x for x in ORD if x in cs] and not e0 and r1 == 'ok' and h1, [nv, h0, cs, e0, r1, h1])
        chk('CF-01 seed: "14 com acesso · 1 sem acesso" (Igor e Marta do BEN-1; Otávio e Dora da v56 entram) e a primária "Convidar pessoa"; sem erro de JS', '14 com acesso · 1 sem acesso' in hdr() and prims()['prims'] == ['Convidar pessoa'] and not errs(), [hdr(), prims(), errs()])
        tbl = J("[...document.querySelectorAll('[role=table]')].map(t=>t.querySelectorAll('[role=columnheader] button').length)")
        # um campo de busca por tela (proprietário, 13/10/2026): o da 1ª grade busca nas duas (a 2ª está no mesmo grupo, data-g2q)
        chk('A14 as duas grades têm filtro rápido e ordenação/filtro por coluna e um campo de busca só, para as duas; "%" na célula da AL-05', len(tbl) == 2 and all(x >= 8 for x in tbl)
            and J("[...document.querySelectorAll('main input[type=search]')].filter(i=>i.getClientRects().length).length") == 1 and J("document.querySelectorAll('main [data-g2q]').length") == 2
            and 'até 20 % da área da ordem' in (linha(1, 'AL-05 · Dispensar') or ''), [tbl, linha(1, 'AL-05 · Dispensar')])
        l = linha(1, 'AL-01 · Liberar') or ''
        chk('AL-01 alinhada ao comando (CONF-D10): gestor · Ana, editável; nenhum "Caio (PCP)" como liberador', 'gestor · Ana' in l and 'Editável: papel' in l and 'Liberador do domínio' not in J("document.body.innerText"), l)
        # ---------- AL-01 → PCP (vale na hora; R13 na O.S.) ----------
        abre(1, 'AL-01 · Liberar'); d = dlg()
        chk('painel da AL-01: definição, ordens afetadas (6 em A liberar) e versões; com o painel aberto, nenhuma primária fora dele', 'ordens e registros afetados agora (6)' in d.lower() and 'v1 · 01/07/2026 implantação · gestor' in d and prims()['dialogo'], [d[-500:], prims()])
        clk('PCP', 'aside[role=dialog]'); setv('#cf1_mot', 'decisão do proprietário'); d = dlg()
        chk('prévia: muda gestor → PCP, Caio ganha, Ana perde, vale na hora; primária do painel "Salvar alçada" (uma só)', 'gestor → PCP' in d and 'Quem ganha Caio' in d and 'Quem perde Ana' in d and 'vale na hora' in d
            and prims()['prims'] == ['Salvar alçada'], [d[:600], prims()])
        n0 = nev(); clk('Salvar alçada', 'aside[role=dialog]'); l = linha(1, 'AL-01 · Liberar') or ''
        chk('AL-01 v2 vigente: PCP · Caio; 1 evento; painel fechado', 'PCP · Caio' in l and 'Vigente v2' in l and nev() == n0 + 1 and not dlg(), [l, toast()])
        chk('F13 a linha da AL-01 gravada fica realçada (g2flash)', fl(1, 'AL-01 · Liberar'), l)
        go('OS.dc.html#OS-0430'); t = J("document.body.innerText.replace(/\\s+/g,' ')")
        chk('O.S. com AL-01 = PCP: Ana vê "Aprovar v1" (não "Liberar para execução")', 'Aprovar v1' in t and 'Liberar para execução' not in t, t[:300])
        clk('Aprovar v1'); clk('Confirmar aprovação'); t = J("document.body.innerText.replace(/\\s+/g,' ')")
        chk('Ana aprova: selo "Aprovada v1 · aguarda liberação" e a ordem segue em A liberar', 'Aprovada v1 · aguarda liberação' in t and 'aprovada por Ana (agrônoma)' in toast(), [toast(), t[:300]])
        perfil('Caio'); go('OS.dc.html#OS-0430'); clk('Liberar para execução'); clk('Confirmar liberação')
        chk('Ver como Caio (PCP): libera a v1 aprovada; só o CMD-06 (aviso cita a aprovação anterior)', 'liberada por Caio (PCP); aprovada antes por Ana (agrônoma)' in toast(), toast())
        go('CF-04.dc.html'); o = ordem('Liberar O.S. · CMD-06', 'Aprovar a versão · CMD-42', 'AL-01 v1 → v2')
        chk('F1 trilha (mais recente primeiro): CMD-06, CMD-42 e a mudança da AL-01 na ordem em que foram gravados, mesmo no mesmo minuto', -1 not in o and o[0] < o[1] < o[2], o)
        J("document.querySelector('[aria-label=\"Filtrar Quando\"]').click()"); time.sleep(.3); clk('↑ Classificar do mais antigo para o mais recente', '[role=dialog]'); o2 = ordem('Liberar O.S. · CMD-06', 'Aprovar a versão · CMD-42', 'AL-01 v1 → v2')
        chk('F1 coluna Quando em ordem crescente: mudança da AL-01, CMD-42, CMD-06 (ordena pela ordem da trilha, não só pela data)', -1 not in o2 and o2[2] < o2[1] < o2[0], o2)
        # ---------- AL-05: 20 → 25 % por Ana fica pendente; Caio com gestor confirma ----------
        go('CF-01.dc.html'); reset(); go('CF-01.dc.html')
        abre(1, 'AL-05 · Dispensar'); setv('#cf1_lim', '25'); setv('#cf1_mot', 'safra com chuva'); d = dlg()
        chk('AL-05 20 → 25 % por Ana: prévia "aguarda 2º aprovador" (amplia o seu poder); OS-0421 70 → 87,5 ha; primária "Enviar para confirmação"', 'aguarda 2º aprovador' in d and '70 ha → 87,5 ha' in d and prims()['prims'] == ['Enviar para confirmação'], [d[:700], prims()])
        clk('Enviar para confirmação'); l = linha(1, 'AL-05 · Dispensar') or ''
        chk('AL-05 "Aguarda 2º aprovador"; o cabeçalho diz "AL-05 aguarda confirmação"; Ana não confirma (primária segue "Convidar pessoa")', 'Aguarda 2º aprovador' in l and 'AL-05 aguarda confirmação' in hdr() and prims()['prims'] == ['Convidar pessoa'], [l, hdr(), prims()])
        abre(0, 'Caio'); r = papel('gestor'); clk('Salvar papéis')
        chk('Ana concede gestor a Caio pelo painel da pessoa', 'gestor' in (linha(0, 'Caio') or '') and 'Papéis de Caio: + gestor' in toast(), [r, linha(0, 'Caio'), toast()])
        chk('F13 a linha de Caio fica realçada depois de "Salvar papéis"', fl(0, 'Caio'), linha(0, 'Caio'))
        perfil('Rui'); go('CF-01.dc.html'); abre(1, 'AL-05 · Dispensar'); d = dlg()
        chk('F12 Ver como Rui na AL-05 pendente: "Confirma ou recusa: Caio (gestor)", sem mandar à própria proponente (Ana)', 'Confirma ou recusa: Caio (gestor).' in d and '(Ana (gestora))' not in d, d[-300:])
        perfil('Caio'); go('CF-01.dc.html')
        chk('Ver como Caio: a primária vira "Confirmar AL-05"', prims()['prims'] == ['Confirmar AL-05'], prims())
        clk('Confirmar AL-05'); d = dlg()
        chk('F7 painel da AL-05 para Caio: "Recusar mudança" como secundária e uma só primária "Confirmar mudança"', 'Recusar mudança' in d and prims()['prims'] == ['Confirmar mudança'], [d[-200:], prims()])
        clk('Confirmar mudança', 'aside[role=dialog]'); l = linha(1, 'AL-05 · Dispensar') or ''
        chk('Caio confirma: AL-05 v2 vigente com 25 %', 'até 25 % da área da ordem' in l and 'Vigente v2' in l, [l, toast()])
        abre(0, 'Caio'); d = dlg(); J("document.querySelector('aside[role=dialog] button[aria-label=Fechar]').click()"); time.sleep(.3)
        chk('F11 Ver como Caio (gestor): o painel dele não oferece "Desativar acesso"', 'Caio' in d and 'Desativar acesso' not in d, d[-200:])
        # ---------- recusas (R3, R5) e repetição ----------
        go('CF-01.dc.html'); reset(); go('CF-01.dc.html'); n0 = nev()
        abre(0, 'Ana'); papel('direção'); clk('Salvar papéis'); d = dlg()
        chk('ERRO R3: Ana concede direção a si mesma → recusa com o motivo no painel; nada gravado', 'Ninguém concede papel a si mesmo' in d and nev() == n0, d[-400:])
        papel('direção'); papel('gestora'); clk('Salvar papéis'); d = dlg()
        chk('ERRO R5: Ana retira o próprio gestor (última gestora) → recusa; nada gravado', 'última pessoa ativa com o papel de gestor' in d and nev() == n0, d[-400:])
        sw = J("(()=>{const b=[...document.querySelectorAll('aside[role=dialog] [role=switch]')]; return b.map(x=>x.querySelector('.conf-swt').innerText+':'+x.disabled).join('|');})()")
        J("document.querySelector('aside[role=dialog] button[aria-label=Fechar]').click()"); time.sleep(.3)
        abre(0, 'Caio'); swc = J("(()=>{const b=[...document.querySelectorAll('aside[role=dialog] [role=switch]')].find(x=>x.querySelector('.conf-swt').innerText==='agrônomo'); return b?[b.disabled,b.innerText.replace(/\\s+/g,' ')]:null;})()")
        chk('R4 no painel: "agrônomo" desabilitado para Caio, com o motivo (exige CREA válido no CD-04)', swc and swc[0] and 'exige CREA válido' in swc[1], swc)
        papel('conferência'); r = dclk('Salvar papéis')
        chk('REPETIÇÃO: duplo clique em "Salvar papéis" = 1 evento (chave de quem inicia)', r == 'ok' and nev() == n0 + 1, [r, nev() - n0])
        # ---------- desativar Paula → Resolver AL-12 → Rui ----------
        go('CF-01.dc.html'); reset(); go('CF-01.dc.html')
        abre(0, 'Paula'); clk('Desativar acesso', 'aside[role=dialog]')
        chk('A8 desativar Paula: cabeçalho vermelho "AL-12 sem titular" e primária "Resolver AL-12"; Paula fora do Ver como', 'AL-12 sem titular' in hdr() and prims()['prims'] == ['Resolver AL-12']
            and 'Paula' not in J("[...document.querySelectorAll('.menu-lat select option')].map(o=>o.value).join(',')") and 'Desativado em 26/09/2026' in (linha(0, 'Paula') or ''), [hdr(), prims(), linha(0, 'Paula')])
        go('OS.dc.html#OS-0421'); t = J("document.body.innerText")
        chk('A8 O.S.: ninguém diz "Paula (conferência) decide"', 'Paula (conferência)' not in t, re.findall(r'.{40}Paula \(conferência\).{40}', t)[:2])
        go('CF-01.dc.html'); clk('Resolver AL-12'); d = dlg()
        chk('Resolver AL-12: lista curta com quem tem a habilidade "Conferir" primeiro (Caio, Rui)', 'AL-12 sem titular' in d and d.index('Caio · Agronomia · habilidade no CD-04') < d.index('Carlos') and 'Rui · Suprimentos · habilidade no CD-04' in d, d[:600])
        clk('Rui · Suprimentos', 'aside[role=dialog]'); chk('um toque escolhe: primária "Conceder conferência a Rui"', prims()['prims'] == ['Conceder conferência a Rui'], prims())
        clk('Conceder conferência a Rui', 'aside[role=dialog]')
        chk('AL-12 volta a ter titular (Rui); cabeçalho sem pendência', 'conferência · Rui' in (linha(1, 'AL-12 · ') or '') and 'sem titular' not in hdr(), [linha(1, 'AL-12 · '), hdr()])
        # ---------- revisão F9: Ana retira o próprio agrônomo → Resolver AL-02 explica o caminho ----------
        go('CF-01.dc.html'); reset(); go('CF-01.dc.html'); abre(0, 'Ana'); papel('agrônoma'); d = dlg(); clk('Salvar papéis')
        chk('F9 Ana retira o próprio agrônomo: a prévia avisa AL-02 sem titular e a primária vira "Resolver AL-02"', 'AL-02' in d and prims()['prims'] == ['Resolver AL-02'], [d[-300:], prims()])
        clk('Resolver AL-02'); d = dlg(); b = J("(()=>{const b=[...document.querySelectorAll('aside[role=dialog] button')].find(x=>x.innerText.trim()==='Conceder agrônomo'); return b?[b.disabled,b.title]:null;})()")
        chk('F9 painel da AL-02 sem candidato: diz por quê e o caminho (R3: outra pessoa com gestor; conceda gestor antes; CREA no CD-04); botão com o motivo',
            'Ninguém pode receber agora' in d and 'ninguém concede papel a si mesmo' in d and 'conceda gestor a outra pessoa antes' in d and 'Cadastros › Pessoas e equipes' in d and b and b[0] and 'veja o caminho' in b[1], [d[:700], b])
        # ---------- convidar Beto (do seed) ----------
        go('CF-01.dc.html'); reset(); go('CF-01.dc.html'); clk('Convidar pessoa'); clk('Beto', 'aside[role=dialog]'); d = dlg()
        chk('Convidar pessoa → Beto (lista curta) → painel com "Convidar (simulado)" como única primária', 'Sem acesso' in d and prims()['prims'] == ['Convidar (simulado)'], [d[:300], prims()])
        clk('Convidar (simulado)', 'aside[role=dialog]')
        chk('A9 Beto com acesso Ativo, só app de campo; cabeçalho "15 com acesso · 0 sem acesso"; primária desabilitada "Todas as pessoas do cadastro têm acesso"',
            'Ativo desde 26/09/2026' in (linha(0, 'Beto') or '') and '15 com acesso · 0 sem acesso' in hdr()
            and J("(()=>{const b=document.querySelector('header .conf-prim'); return !!b&&b.disabled&&b.title;})()") == 'Todas as pessoas do cadastro têm acesso', [linha(0, 'Beto'), hdr()])
        go('CD-04.dc.html'); b = J("(()=>{const r=[...document.querySelectorAll('[role=table]')[0].querySelectorAll('[role=row]')].find(r=>r.innerText.indexOf('Beto')>=0); return r?r.innerText.replace(/\\s+/g,' '):'';})()")
        J("(()=>{const r=[...document.querySelectorAll('[role=table]')[0].querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.indexOf('Beto')>=0); (r.querySelector('.g2pw')||r).click();})()"); time.sleep(.4)
        d = dlg(); lab = J("[...document.querySelectorAll('aside[role=dialog] label[for]')].map(l=>l.innerText.trim())")
        chk('CD-04 lê o acesso de Configurações: Beto sem "Sem acesso ao app"; no formulário, origem "Acesso ao app: Ativo desde 26/09/2026" com link; sem campo de acesso',
            'Sem acesso ao app' not in b and 'Acesso ao app: Ativo desde 26/09/2026' in d and 'Acesso ao app' not in lab
            and J("!![...document.querySelectorAll('aside[role=dialog] a')].find(a=>a.getAttribute('href')==='CF-01.dc.html#pessoa=Beto')"), [b, d[-300:], lab])
        # ---------- perfil sem gestor ----------
        go('CF-01.dc.html'); reset('Rui'); go('CF-01.dc.html')
        chk('perfil Rui (sem gestor): primária desabilitada com "decisão de Ana (gestora)"', J("(()=>{const b=document.querySelector('header .conf-prim'); return !!b&&b.disabled&&/decisão de Ana \\(gestora\\)/.test(b.title);})()"), J("(document.querySelector('header .conf-prim')||{}).title"))
        abre(0, 'Zé'); dis = J("[...document.querySelectorAll('aside[role=dialog] [role=switch]')].every(b=>b.disabled)")
        chk('perfil Rui: papéis só leitura e o motivo no painel', dis and 'decisão de Ana (gestora)' in dlg(), dlg()[-300:])
        c.shot(os.path.join(SHOT, 'conf_cf01_1440.png'))
        chk('CF-01 sem erro de JS na jornada', not errs(), errs())

    SEGREDO = re.compile(r'(senha|token|secret|apikey)\s*[:=]|[A-Za-z0-9_-]{24,}', re.I)
    if 'cf04' in PARTES:
        go('CF-04.dc.html'); reset(); go('CF-04.dc.html'); res = J("(document.querySelector('main [role=status]')||{}).innerText||''")
        chk('CF-04 seed: "18 registros · 3 autores · lidos dos comandos gravados; nada é digitado aqui"; uma primária "Baixar trilha (CSV)"',
            res.startswith('18 registros · 3 autores') and 'nada é digitado aqui' in res and prims()['prims'] == ['Baixar trilha (CSV)'] and not errs(), [res, prims(), errs()])
        qf = J("[...document.querySelectorAll('main [role=group] button')].map(b=>b.innerText.replace(/\\s+/g,' ').trim()).join('|')")
        chk('filtro rápido por mês: Todos 18 · jul/2026 12 · ago/2026 3 · jun/2026 2 · set/2026 1', all(x in qf for x in ['Todos 18', 'jul/2026 12', 'ago/2026 3', 'jun/2026 2', 'set/2026 1']), qf)
        clk('jul/2026'); n0 = nev(); clk('Baixar trilha (CSV)'); csv = J("window.__confCsv||''") or ''
        chk('A11 CSV = as 12 linhas de jul/2026 (+ cabeçalho), sem segredo; a exportação vira registro', len([l for l in csv.split('\r\n') if l]) == 13 and nev() == n0 + 1 and not SEGREDO.search(csv)
            and 'Exportação · 12 registros · mês jul/2026' in J("JSON.stringify(JSON.parse(localStorage.getItem('talhao-os-cenario-v1')).conf.ev)"), [csv[:300], nev() - n0])
        clk('Todos'); res = J("(document.querySelector('main [role=status]')||{}).innerText||''")
        chk('a própria exportação aparece na trilha: 19 registros', res.startswith('19 registros'), res)
        chk('F13 a linha da exportação fica realçada (g2flash)', fl(0, 'Baixar trilha (CSV)'), linha(0, 'Baixar trilha (CSV)'))
        n1 = nev(); k1 = J("window.__confCsvN||0"); J("(()=>{const b=document.querySelector('header .conf-prim'); b.click(); b.click();})()"); time.sleep(.6)
        chk('F16 duplo clique em "Baixar trilha": 1 registro e 1 arquivo', nev() == n1 + 1 and J("window.__confCsvN||0") == k1 + 1, [nev() - n1, J("window.__confCsvN||0") - k1])
        J("document.querySelector('[aria-label=\"Filtrar Quem\"]').click()"); time.sleep(.3); clk('Limpar', '[role=dialog]')
        J("(()=>{const l=[...document.querySelectorAll('[role=dialog] label')].find(x=>x.innerText.indexOf('Provedor')>=0); l.querySelector('input').click();})()"); time.sleep(.2); clk('OK', '[role=dialog]')
        res = J("(document.querySelector('main [role=status]')||{}).innerText||''")
        chk('filtro por pessoa (Quem): Provedor → 2 registros de 20 (faturas pagas pelo provedor simulado; a 2ª exportação, do F16, entra na conta)', res.startswith('2 registros de 20') and 'Provedor (simulado)' in (linha(0, 'jul/2026') or linha(0, 'Fatura') or ''), [res, linha(0, 'Fatura')])
        abre(0, 'Fatura jul/2026'); d = dlg()
        chk('detalhe só leitura: de onde vem a data (simulada da cobrança), registro de origem e "A trilha não se edita"', 'data simulada da cobrança' in d and 'evt_demo_0801' in d and 'A trilha não se edita' in d and 'Abrir no domínio' in d, d[:500])
        J("document.querySelector('aside[role=dialog] button[aria-label=Fechar]').click()"); time.sleep(.3)
        setv('main input[type=search]', 'zzzz'); dis = J("(()=>{const b=document.querySelector('header .conf-prim'); return [b.disabled,b.title];})()")
        chk('filtro sem resultado: "Nenhuma linha corresponde aos filtros" e a primária desabilitada "Nenhum registro para baixar"', dis == [True, 'Nenhum registro para baixar'] and 'Nenhuma linha corresponde aos filtros' in J("document.querySelector('main').innerText"), dis)
        go('CF-01.dc.html'); abre(1, 'AL-05 · Dispensar'); setv('#cf1_lim', '15'); setv('#cf1_mot', 'safra curta'); clk('Salvar alçada', 'aside[role=dialog]')
        go('CF-04.dc.html'); l = linha(0, 'AL-05') or ''
        chk('ato do CF-01 entra na trilha na hora: "Alterar alçada · AL-05" por Ana (gestora), 26/09/2026 hh:mm, web', 'Alterar alçada' in l and 'Ana (gestora)' in l and re.search(r'26/09/2026 \d\d:\d\d', l), l)
        vis = J("document.body.innerText")
        chk('A12 nenhum texto com cara de segredo no CF-04', not SEGREDO.search(vis), (SEGREDO.search(vis) or [None])[0])
        chk('CF-04 sem erro de JS', not errs(), errs())
    if 'cf03' in PARTES:
        go('CF-03.dc.html'); reset(); go('CF-03.dc.html')
        chk('CF-03 seed: selo "Demonstração · nenhuma conexão real", 5 conexões, fila do ERP 0, uma primária "Sincronizar agora (simulado)"',
            'Demonstração · nenhuma conexão real' in hdr() and J("document.querySelectorAll('[role=table] [role=row].g2ed').length") == 5 and 'Fila do ERP: 0 movimentos' in J("document.querySelector('main').innerText")
            and prims()['prims'] == ['Sincronizar agora (simulado)'] and not errs(), [hdr(), prims(), errs()])
        # um movimento que muda o físico: libera a OS-0430 e entrega Glifosato 480 pelo Estoque (window.__cen da tela EST)
        go('EST.dc.html'); r = J("""(()=>{ const C=window.__cen; let rid=''; const a=C.cenMudar(null,c=>{ const x=C.cenLiberar(c,'OS-0430'); rid=c.ordens['OS-0430'].req; return x; });
            const b=C.cenMudar(null,c=>C.cenEntregar(c,rid,'Glifosato 480',20,'Marcos','Rui')); return [a.erro||'',b.erro||'',rid]; })()""")
        go('CF-03.dc.html'); m = J("document.querySelector('main').innerText"); l = linha(0, 'ERP') or ''
        chk('fila do ERP 1 (a entrega; as 3 reservas ficam fora)', r[:2] == ['', ''] and 'Fila do ERP: 1 movimento' in m and 'Com pendência' not in l and '1' in l, [r, l])
        abre(0, 'ERP · Sankhya'); d = dlg()
        chk('painel do ERP: quem escreve cada objeto, ambiente de demonstração, credencial "Não configurada" mascarada, pendência com o movimento da entrega',
            'Quem escreve cada objeto' in d and 'Demonstração (dados sintéticos)' in d and 'Não configurada' in d and '••••••••' in d and 'entrega · OS-0430' in d and not SEGREDO.search(d), d[:700])
        J("document.querySelector('aside[role=dialog] button[aria-label=Fechar]').click()"); time.sleep(.3)
        n0 = nev(); clk('Sincronizar agora (simulado)'); t1 = toast(); time.sleep(.2); clk('Sincronizar agora (simulado)'); t2 = toast()
        chk('sincronizar envia 1; de novo, nada é reenviado; cada sincronização é um registro', '1 movimento enviado ao ERP' in t1 and 'nada foi reenviado' in t2 and nev() == n0 + 2
            and 'Fila do ERP: 0 movimentos' in J("document.querySelector('main').innerText"), [t1, t2, nev() - n0])
        r = J("""(()=>{ const n=s=>(s||'').replace(/\\s+/g,' ').trim(); const b=[...document.querySelectorAll('header button')].find(x=>n(x.innerText)==='Sincronizar agora (simulado)'); b.click(); b.click(); return 'ok'; })()"""); time.sleep(.5)
        chk('REPETIÇÃO: duplo clique em "Sincronizar" = 1 registro (chave do desenho)', nev() == n0 + 3, nev() - n0)
        chk('F13 a linha do ERP fica realçada depois de sincronizar', fl(0, 'ERP · Sankhya'), linha(0, 'ERP · Sankhya'))
        chk('F15 app de campo: "pelo sinal do aparelho (simulado)", sem "tempo real"', 'pelo sinal do aparelho (simulado)' in (linha(0, 'App de campo') or '') and 'tempo real' not in J("document.body.innerText"), linha(0, 'App de campo'))
        abre(0, 'App de campo'); d = dlg()
        chk('app de campo: "Com sinal (simulado)", nunca "online" ou "ao vivo"', 'Com sinal (simulado)' in d and not re.search(r'\bonline\b|ao vivo', d, re.I), d[:300])
        J("document.querySelector('aside[role=dialog] button[aria-label=Fechar]').click()"); time.sleep(.3)
        vis = J("document.body.innerText"); chk('A12 nenhum texto com cara de segredo no CF-03', not SEGREDO.search(vis), (SEGREDO.search(vis) or [None])[0])
        chk('CF-03 sem erro de JS', not errs(), errs())
    if 'cf05' in PARTES:
        go('CF-05.dc.html'); reset('Rui'); go('CF-05.dc.html')
        # 14/10/2026 (TEXTO-2): a origem "(Configurações › Usuários e alçadas)" saiu da tela para a dica ⓘ; a contagem (14) segue conferida à vista
        chk('A9 CF-05 conta as pessoas com acesso do estado de Configurações (14 no seed, com Igor, Marta, Otávio e Dora)', 'Pessoas com acesso: 14 · fora da cobrança' in J("document.body.innerText")
            and 'Configurações › Usuários e alçadas' in (J("(document.querySelector('header button.g2-info')||{}).getAttribute?document.querySelector('header button.g2-info').getAttribute('data-dica'):''") or ''), J("document.body.innerText")[:200])
        clk('01/10/2026'); clk('Pagar fatura'); clk('Pix · simulado', 'aside[role=dialog]'); clk('Confirmar pagamento (simulado)', 'aside[role=dialog]'); d = dlg()
        pago = J("(()=>{ const c=JSON.parse(localStorage.getItem('talhao-os-cenario-v1')); return c.assin.orgs.sr.faturas.find(f=>f.comp==='2026-09').st; })()")
        chk('A18 Ver como Rui: pagar a fatura é recusado "decisão de Ana (gestora)" e nada é pago', 'decisão de Ana (gestora)' in d and pago == 'aberta', [d[-300:], pago])
        perfil('Ana'); go('CF-05.dc.html'); clk('Pagar fatura'); clk('Pix · simulado', 'aside[role=dialog]'); clk('Confirmar pagamento (simulado)', 'aside[role=dialog]'); d = dlg()
        chk('A18 com Ana: paga e o evento grava "por Ana (gestora)"', 'recibo PAG-0001 · por Ana (gestora)' in d, d[-400:])
        perfil('Rui'); go('BO-02.dc.html'); clk('Conciliar pagamentos'); t = toast()
        chk('A18 backoffice com o Ver como em Rui: conciliar segue com "Admin plataforma" (sem AL-15)', 'Conciliado' in t or 'Nenhum evento novo' in t, t)
        go('CF-04.dc.html'); l = linha(0, 'Fatura set/2026') or ''
        chk('o pagamento entra na trilha com Ana (gestora) e a data simulada da cobrança', 'Ana (gestora)' in l and 'Pagar fatura (simulado)' in l, l)
        chk('CF-05 sem erro de JS', not errs(), errs())
    if 'rev' in PARTES:
        # ---------- REV6 · Ana (com Caio gestor) não retira todos os próprios papéis: o Ver como passaria a Caio em silêncio ----------
        go('CF-01.dc.html'); reset(); go('CF-01.dc.html'); abre(0, 'Caio'); papel('gestor'); clk('Salvar papéis'); n0 = nev()
        abre(0, 'Ana'); papel('gestora'); papel('agrônoma'); d = dlg()
        chk('REV6 prévia no painel da própria Ana sem nenhum papel: "Você sem nenhum papel" com o porquê', 'Você sem nenhum papel' in d and 'o próximo ato sairia em nome dela' in d, d[-500:])
        clk('Salvar papéis'); d = dlg(); sel = J("(document.querySelector('.menu-lat select')||{}).value||''")
        chk('REV6 NEGATIVO Salvar: recusado "Ninguém retira todos os próprios papéis", nada gravado; o Ver como segue Ana', 'Ninguém retira todos os próprios papéis' in d and nev() == n0 and sel == 'Ana', [d[-400:], nev() - n0, sel])
        # ---------- REV5 · detalhe aberto no CF-04 não troca de registro quando outra aba grava ----------
        go('CF-04.dc.html'); reset(); go('CF-04.dc.html'); abre(0, 'Lucas'); d0 = dlg()
        r = aba_js('EST.dc.html', "(()=>{ const X=window.__cen; const r=X.cenMudar(null,c=>X.cenEntregar(c,'REQ-035','Fungicida A',5,'Marcos','Rui')); return r.erro||r.msg; })()")
        time.sleep(1.0); d1 = dlg(); res = J("(document.querySelector('main [role=status]')||{}).innerText||''")
        chk('REV5 outra aba entrega no Estoque (19 registros): o detalhe aberto segue o de Lucas (01/08/2026), o mesmo registro', 'Objeto Lucas' in d0 and res.startswith('19 registros') and 'Objeto Lucas' in d1 and '01/08/2026' in d1 and d1 == d0, [r, res, d0[:160], d1[:160]])
        J("document.querySelector('aside[role=dialog] button[aria-label=Fechar]').click()"); time.sleep(.3)
        # ---------- REV1 · colheita pela web: pesar, estornar e descartar conferem quem age (Santa Rita: o almoxarife) ----------
        from ben_unit_test import motor, node
        fx = node(motor() + """ const c = cenClone(CEN0); c.ordens['OS-0932'] = { id: 'OS-0932', tipo: 'Colheita · semana 39', talhao: 'T7', area: 0, etapa: 'Em execução', versao: 'v1', realizado: 6, saldo: 0, resp: 'Sérgio', ins: [], req: null, selos: [],
          ap: [{ d: '25/09', dia: 1, ha: 6, st: 'Conferido', sinc: true, origem: 'web' }], reservado: false, osc: {} };
          prReceber(c, { quem: 'Rui', os: 'OS-0932', ticket: 'TK-T7A', bruto: 9400, tara: 3200, cond: 'Íntegra', dcol: '2026-09-25' }); c.rev = (c.rev || 0) + 1; print(JSON.stringify(c));""", 'conf_rev1.js')
        est = fx.stdout.strip().splitlines()[-1]
        go('CARGA.dc.html'); reset('Zé'); J(f"localStorage.setItem('talhao-os-cenario-v1', {json.dumps(est)})"); go('CARGA.dc.html')
        r0 = J("JSON.parse(localStorage.getItem('talhao-os-cenario-v1')).rev"); abre(0, 'CG-2109'); clk('Estornar', 'aside[role=dialog]'); setv('#pf_mot', 'ticket trocado'); clk('Confirmar estorno', 'aside[role=dialog]'); d = dlg()
        st = J("(()=>{ const c=JSON.parse(localStorage.getItem('talhao-os-cenario-v1')); return [c.rev, c.producao.cargas['CG-2109'].st]; })()")
        chk('REV1 NEGATIVO Ver como Zé (mecânico) estorna a CG-2109 (Santa Rita) pela tela: recusado "decisão de Rui (almoxarife)", a carga segue Recebida, nada gravado', 'decisão de Rui (almoxarife)' in d and st == [r0, 'Recebida'], [d[-300:], st, r0])
        perfil('Rui'); go('CARGA.dc.html'); abre(0, 'CG-2109'); clk('Estornar', 'aside[role=dialog]'); setv('#pf_mot', 'ticket trocado'); clk('Confirmar estorno', 'aside[role=dialog]')
        q = J("(()=>{ const c=JSON.parse(localStorage.getItem('talhao-os-cenario-v1')); const g=c.producao.cargas['CG-2109']; return [g.st, (g.estorno||{}).quem||'']; })()")
        go('CF-04.dc.html'); l = linha(0, 'Estornar carga') or ''
        chk('REV1 Ver como Rui estorna: a carga grava "Rui (almoxarife)" e o CF-04 mostra Rui (almoxarife) · Estornar carga', q == ['Estornada', 'Rui (almoxarife)'] and 'Rui (almoxarife)' in l, [q, l])
        # ---------- REV4 · encerrar a O.S. grava quem agiu e entra na trilha ----------
        go('OS.dc.html#OS-0508'); reset('Zé'); go('OS.dc.html#OS-0508'); clk('Conferir e encerrar'); clk('Confirmar encerramento'); t = toast()
        go('CF-04.dc.html'); res = J("(document.querySelector('main [role=status]')||{}).innerText||''"); l = linha(0, 'OS-0508') or ''
        chk('REV4 Ver como Zé encerra a OS-0508: o aviso diz por quem; o CF-04 passa a 19 registros · 4 autores com "Encerrar O.S. · CMD-10" por Zé (mecânico)',
            'encerrada por Zé (mecânico)' in t and res.startswith('19 registros · 4 autores') and 'Encerrar O.S. · CMD-10' in l and 'Zé (mecânico)' in l, [t, res, l])
        chk('REV sem erro de JS', not errs(), errs())
    if 'rev2' in PARTES:
        # ---------- duplo clique da mão em "Baixar trilha" e em "Sincronizar" (S4 de correção do F16) ----------
        go('CF-04.dc.html'); reset(); go('CF-04.dc.html'); n0 = nev(); k0 = J("window.__confCsvN||0"); dclk_real('header .conf-prim')
        chk('REV12a duplo clique real (120 ms) em "Baixar trilha": 1 exportação e 1 arquivo', nev() == n0 + 1 and J("window.__confCsvN||0") == k0 + 1, [nev() - n0, J("window.__confCsvN||0") - k0])
        time.sleep(.6); clk('Baixar trilha (CSV)')
        chk('REV12b referência: um novo clique depois do duplo clique é outra exportação (+1)', nev() == n0 + 2 and J("window.__confCsvN||0") == k0 + 2, [nev() - n0, J("window.__confCsvN||0") - k0])
        f0 = J("(()=>{const r=document.querySelector('[role=table] [role=row].g2flash'); return r?r.innerText.replace(/\\s+/g,' '):'';})()") or ''
        aba_js('EST.dc.html', "(()=>{ const X=window.__cen; const r=X.cenMudar(null,c=>X.cenEntregar(c,'REQ-035','Fungicida A',5,'Marcos','Rui')); return r.erro||r.msg; })()"); time.sleep(1.0)
        f1 = J("(()=>{const r=document.querySelector('[role=table] [role=row].g2flash'); return r?r.innerText.replace(/\\s+/g,' '):'';})()") or ''
        chk('REV12c F13: outra aba entrega no Estoque e o realce segue na linha da exportação gravada (não pula de linha)', 'Exportação · ' in f0 and f1 == f0, [f0[:160], f1[:160]])
        go('CF-03.dc.html'); n0 = nev(); dclk_real('header .conf-prim')
        chk('REV12d duplo clique real em "Sincronizar agora (simulado)": 1 registro', nev() == n0 + 1, nev() - n0)
        # ---------- 390 px: Quem fica visível com Quando; primária desabilitada diz o motivo; rodapé do painel preso ----------
        go('CF-04.dc.html', 390, 844)
        q = J("""(()=>{ const t=document.querySelector('[role=table]'); const box=t.closest('.g2rola')||t.parentElement; box.scrollLeft=box.scrollWidth; const r=t.querySelectorAll('[role=row].g2ed')[0];
          const c0=r.querySelector('[role=cell]'); const b=box.getBoundingClientRect(), k=c0.getBoundingClientRect(); return [c0.innerText.replace(/\\s+/g,' '), k.left>=b.left-1&&k.right<=b.right+1, box.scrollLeft>0]; })()""")
        chk('REV13a CF-04 a 390 px, rolado até o fim à direita: a 1ª coluna (presa) mostra Quando e Quem ("Ana (gestora)")', q and '(gestora)' in q[0] and q[1] and q[2], q)
        go('CF-01.dc.html', 390, 844); perfil('Rui'); go('CF-01.dc.html', 390, 844)
        b = J("(()=>{const b=document.querySelector('header .conf-prim'); return b?[b.disabled,b.innerText.replace(/\\s+/g,' ')]:null;})()")
        chk('REV13b Ver como Rui a 390 px: a primária desabilitada diz no rótulo "decisão de Ana (gestora)"', b and b[0] and 'decisão de Ana (gestora)' in b[1], b)
        perfil('Ana'); go('CF-01.dc.html', 390, 844); abre(0, 'Paula')
        y = J("(()=>{const b=[...document.querySelectorAll('aside[role=dialog] button')].find(x=>x.innerText.trim()==='Salvar papéis'); if(!b) return null; const r=b.getBoundingClientRect(); return [Math.round(r.top),Math.round(r.bottom),innerHeight];})()")
        chk('REV13c painel da Paula a 390 px: "Salvar papéis" à vista (rodapé preso no fim do painel)', y and y[1] <= y[2] + 1, y)
        # ---------- teclado: o foco entra no painel; Esc fecha; setas no radiogroup ----------
        go('CF-01.dc.html'); reset(); go('CF-01.dc.html'); abre(0, 'Paula'); time.sleep(.3)
        f = J("!!document.activeElement&&!!document.activeElement.closest('aside[role=dialog]')"); tecla('Escape', 'Escape', 27)
        chk('REV14a abrir o painel da Paula põe o foco dentro dele, e Esc fecha sem um Tab antes', f and not dlg(), [f, dlg()[:80]])
        abre(0, 'Paula'); clk('Desativar acesso', 'aside[role=dialog]'); clk('Resolver AL-12')
        r0 = J("[...document.querySelectorAll('aside[role=dialog] [role=radiogroup] [role=radio]')].map(b=>b.tabIndex)")
        J("document.querySelector('aside[role=dialog] [role=radiogroup] [role=radio]').focus()"); tecla('ArrowDown', 'ArrowDown', 40)
        r1 = J("(()=>{const bs=[...document.querySelectorAll('aside[role=dialog] [role=radiogroup] [role=radio]')]; return [bs.findIndex(b=>b.getAttribute('aria-checked')==='true'), bs.indexOf(document.activeElement), bs.map(b=>b.tabIndex).filter(t=>t===0).length];})()")
        chk('REV14b Resolver AL-12: um só ponto de Tab no grupo; seta para baixo marca e foca o 2º candidato', r0 and r0.count(0) == 1 and r1 == [1, 1, 1], [r0, r1])
        # ---------- a dispensa pela tela leva a chave de quem inicia ----------
        go('OS.dc.html#OS-0421'); reset(); go('OS.dc.html#OS-0421'); clk('Dispensar saldo')
        setv('input[aria-label="Área a dispensar em hectares"]', '5'); setv('textarea[aria-label="Motivo da dispensa"]', 'chuva'); clk('Confirmar dispensa')
        k = J("(()=>{ const c=JSON.parse(localStorage.getItem('talhao-os-cenario-v1')); return [Object.keys(c.recibos||{}), (c.ordens['OS-0421'].osc.disps||[]).length]; })()")
        chk('REV14c "Confirmar dispensa" grava 1 CMD-47 com a chave gerada ao abrir o painel (W-DSP-OS-0421-…)', k and k[1] == 1 and any(x.startswith('W-DSP-OS-0421-') for x in k[0]), k)
        # Compra de insumos pelo Ver como (achado de base): no cmptest.py, na etapa 5 da SOL-2026-07 (o caminho até lá é o do teste da Compra)
        chk('REV2 sem erro de JS', not errs(), errs())
    if 'm390' in PARTES:
        go('CF-01.dc.html', 390, 844); reset(); go('CF-01.dc.html', 390, 844)
        m = J("(()=>{const b=document.querySelector('header .conf-prim'); const r=b.getBoundingClientRect(); return {prim:r.width>0&&r.right<=innerWidth+1&&r.bottom<=innerHeight, sw:document.documentElement.scrollWidth, w:innerWidth};})()")
        chk('A16 390 px: primária visível e sem rolagem horizontal da página', m['prim'] and m['sw'] <= m['w'] + 1, m)
        abre(0, 'Paula'); pw = J("(()=>{const a=[...document.querySelectorAll('aside[role=dialog]')].find(x=>x.getClientRects().length); const r=a.getBoundingClientRect(); return [Math.round(r.width),innerWidth];})()")
        chk('A16 390 px: painel da pessoa em largura total', pw[0] >= pw[1] - 1, pw)
        c.shot(os.path.join(SHOT, 'conf_cf01_390.png'))
        chk('CF-01 390 px sem erro de JS', not errs(), errs())
finally:
    c.close(); srv.terminate()
print(f'RESULTADO: {"OK" if all(OK) else "FALHOU"} {sum(OK)}/{len(OK)}')
sys.exit(0 if OK and all(OK) else 1)
