# -*- coding: utf-8 -*-
"""CTL-5 · teste de navegador (Chrome headless) do módulo, em 1440 px e 390 px. Lê a _render/ como está.
E3 (RL-E4) outorga com fonte única: o CD-01 (aba Água) é a fonte; IR-04 e IR-02 mostram a mesma outorga (soma das outorgas de irrigação do
Rio A: 186 L/s × 19,6 h/dia, vence em 20/11/2026) e a trava de vazão usa esse valor (janela da OS-0602 às 21:00 de hoje → "Sem vazão
outorgada · 244 de 186 L/s", com o gestor; a janela sugerida volta a "Pronta").
E2 (RL-E3) AG-07 só consulta: sem receituário paralelo; "Usar na O.S." leva produto da fazenda, cultura e alvo à ordem A liberar da cultura,
que abre em "Ajustar antes de liberar" com o produto incluído (dose em branco); dose fora da bula é recusada junto ao campo e nada é gravado;
0,8 L/ha libera a v2 e a aprovação (CMD-42) grava produto, dose e alvo; repetir o link não inclui de novo; sem o papel (Caio) nada é incluído.
Uso: python3 ctl5_test.py   (capturas em _probe/ctl5_*.png)"""
import sys, os, time, subprocess, json, re
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from cdp import Chrome
from journeys import free
R = os.path.join(HERE, '_render'); PR = os.path.join(HERE, '_probe'); os.makedirs(PR, exist_ok=True); p = free()
srv = subprocess.Popen(['python3', '-m', 'http.server', str(p), '--bind', '127.0.0.1', '--directory', R], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)
c = None; OK = []; FAIL = []; ERRS = []
def chk(nome, cond, info=''):
    (OK if cond else FAIL).append(nome); print(('OK    ' if cond else 'FALHA ') + nome + ('' if cond else ' · ' + str(info)[:700]), flush=True)
CLK = """((t,root)=>{const r=root?document.querySelector(root):document; if(!r) return 'SEM RAIZ'; const n=s=>(s||'').replace(/\\s+/g,' ').trim();
  const els=[...r.querySelectorAll('button,a')].filter(e=>e.getClientRects().length); const e=els.find(x=>n(x.innerText)===t)||els.find(x=>n(x.innerText).startsWith(t));
  if(!e) return 'NÃO ACHEI '+t; e.click(); return 'ok';})"""
SETV = """((sel,val)=>{const i=document.querySelector(sel); if(!i) return 'SEM '+sel; const P=i.tagName==='SELECT'?HTMLSelectElement.prototype:HTMLInputElement.prototype;
  Object.getOwnPropertyDescriptor(P,'value').set.call(i,val); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true})); return 'ok';})"""
try:
    c = Chrome(port=free())
    def J(expr):
        try: return c.js(expr)
        except Exception as e: print('   (página lançou: ' + str(e)[:120] + ')'); return None
    c.call('Page.addScriptToEvaluateOnNewDocument', {'source': "window.__errs=[];window.addEventListener('error',e=>window.__errs.push(String(e.message)));"})
    U = lambda f: f'http://127.0.0.1:{p}/{f}'
    def goto(pg, w=1.2): c.goto(U(pg), wait=w); time.sleep(.3)
    def clk(t, root=None): r = J(f"({CLK})({json.dumps(t)},{json.dumps(root)})"); time.sleep(.5); return r
    def sv(sel, val): r = J(f"({SETV})({json.dumps(sel)},{json.dumps(val)})"); time.sleep(.4); return r
    def junta(pg): ERRS.extend(f'{pg}: {e}' for e in (J("(window.__errs||[]).filter(e=>e.indexOf(\"reading 'g2toast'\")<0)") or []))
    ROW = lambda txt: J(f"""(()=>{{const r=[...document.querySelectorAll('[role=row]')].find(r=>r.innerText.replace(/\\s+/g,' ').indexOf({json.dumps(txt)})>=0); return r?r.innerText.replace(/\\s+/g,' '):'';}})()""") or ''
    MAIN = lambda: J("document.querySelector('main').innerText.replace(/\\s+/g,' ')") or ''
    TOAST = lambda: J("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).filter(Boolean).join(' | ')") or ''
    LARG = lambda: J("[document.documentElement.scrollWidth,innerWidth]") or [9, 0]
    shot = lambda n: c.shot(os.path.join(PR, f'ctl5_{n}.png'))
    def limpa():
        J("localStorage.removeItem('talhao-os-irrigacao-v1'); localStorage.removeItem('talhao-os-cenario-v1'); localStorage.removeItem('talhao-os-mip-v1'); localStorage.setItem('safrion.perfilDemo','Ana'); sessionStorage.clear();")
    def fazenda(nome): sv('select[aria-label="Filtrar por fazenda"]', nome)

    # =============== E3 · outorga com fonte única ===============
    c.size(1440, 1000); goto('IR-04.dc.html'); limpa(); goto('CD-01.dc.html', 1.5)
    clk('Água'); time.sleep(.4)
    rows = [r for r in (J("[...document.querySelectorAll('[role=row].g2ed')].filter(r=>r.getClientRects().length).map(r=>r.innerText.replace(/\\s+/g,' '))") or []) if r.startswith('Ponto de água')]
    rio = [r for r in rows if 'Captação superficial' in r and 'Rio A' in r and 'm³/h' in r and 'Vencida' not in r]
    ls = sum(float(re.search(r'([\d.,]+) m³/h', r).group(1).replace('.', '').replace(',', '.')) for r in rio) / 3.6
    p2 = next((r for r in rows if r.startswith('Ponto de água 2 ')), '')
    chk(f'E3.1 CD-01 › Água (a fonte): {len(rows)} pontos; "Outorga SINT-002/0000" 150 m³/h, vence 20/11/2026; captação superficial vigente do Rio A soma {ls:.2f} L/s',
        len(rows) == 16 and 'Outorga SINT-002/0000' in p2 and '150 m³/h' in p2 and 'Vence 20/11/2026' in p2 and len(rio) == 4 and abs(ls - 186.11) < 0.01, [len(rows), p2, rio])
    junta('CD-01')
    goto('IR-04.dc.html'); fazenda('Lagoa Grande'); time.sleep(.3)
    r4 = ROW('Rio A (demonstração)'); m4 = MAIN()
    chk('E3.2 IR-04 (Lagoa Grande): a captação lê o cadastro: SINT-001 + SINT-002 + SINT-007 + SINT-014, 186 L/s × 19,6 h/dia, "Vence em 90 dias" até 20/11/2026',
        'outorga SINT-001/0000 + SINT-002/0000 + SINT-007/0000 + SINT-014/0000' in r4 and f'{round(ls)} L/s' in r4 and '19,6 h/dia' in r4 and 'Vence em 90 dias' in r4
        and 'até 20/11/2026' in r4 and '573' not in m4 and 'Ribeirão B' not in m4 and 'Barramento' not in m4 and 'Em renovação' not in r4, [r4, m4[:300]])
    shot('ir04_1440'); junta('IR-04')
    goto('IR-02.dc.html'); fazenda('Lagoa Grande'); time.sleep(.3)
    r2 = ROW('Rio A (demonstração)')
    chk('E3.3 IR-02 (agenda por captação): a mesma outorga (pico de 186 L/s, volume do dia de 13.120 m³, "Vence em 90 dias" até 20/11/2026)',
        'de 186 L/s' in r2 and 'de 13.120 m³' in r2 and 'Vence em 90 dias' in r2 and 'até 20/11/2026' in r2, r2)
    junta('IR-02')
    # trava: janela da OS-0602 (Pivô 8) hoje às 21:00 junto com PV02, PV24 e a fertirrigação do PV04 → acima dos 186 L/s do cadastro
    goto('IR-03det.dc.html#OS-0602:janela', 1.4)
    sv('#jn_d1', '2026-09-23'); sv('#jn_h1', '21:00')
    ck = J("(document.querySelector('aside[role=dialog]')||{innerText:''}).innerText.replace(/\\s+/g,' ')") or ''
    chk('E3.4 RECUSA: janela da OS-0602 hoje às 21:00 → "Sem vazão outorgada · 244 de 186 L/s" com o Gestor da Lagoa Grande (na base, com 573 L/s, passava)',
        'Sem vazão outorgada · 244 de 186 L/s' in ck and 'Gestor da Lagoa Grande' in ck and 'Pronta' not in ck, ck[-600:])
    shot('ir03det_trava')
    clk('Usar janela sugerida', 'aside[role=dialog]'); ck2 = J("(document.querySelector('aside[role=dialog]')||{innerText:''}).innerText.replace(/\\s+/g,' ')") or ''
    chk('E3.5 recuperação: a janela sugerida respeita a outorga e volta a "Pronta"', 'Pronta' in ck2 and 'Sem vazão outorgada' not in ck2, ck2[-400:])
    clk('Salvar janela', 'aside[role=dialog]'); time.sleep(.4); junta('IR-03det')   # grava o estado da irrigação (para o E3.6)
    # repetição: recarregar mantém a fonte (o estado salvo não guarda outra outorga)
    adult = J("(()=>{ const k='talhao-os-irrigacao-v1'; const s=JSON.parse(localStorage.getItem(k)||'null'); if(!s) return false; s.capt['LG-PAR'].ls=573; s.capt['LG-PAR'].st='Em renovação'; localStorage.setItem(k,JSON.stringify(s)); return true; })()")
    goto('IR-04.dc.html'); fazenda('Lagoa Grande'); time.sleep(.3); r4b = ROW('Rio A (demonstração)')
    chk('E3.6 REPETIÇÃO: estado salvo adulterado (573 L/s, "Em renovação") → ao recarregar vale de novo o cadastro (186 L/s, "Vence em 90 dias")',
        adult is True and f'{round(ls)} L/s' in r4b and 'Vence em 90 dias' in r4b and '573' not in r4b, [adult, r4b])

    # =============== E2 · AG-07 só consulta → "Usar na O.S." ===============
    def ag_pronto(t=40):
        for _ in range(int(t / .25)):
            if J("!!(window.__agx&&__agx.AGX.st==='ok'&&__agx.AGX.uSt==='ok')"): return True
            time.sleep(.25)
        return False
    FX = 'aside[aria-label^="Ficha"]'
    PASSO = lambda: J(f"(document.querySelector('{FX} [role=region][aria-label=\"Próximo passo\"]')||{{innerText:''}}).innerText.replace(/\\s+/g,' ')") or ''
    OPTS = lambda rot: J(f"[...document.querySelectorAll('{FX} select[aria-label=\"{rot}\"] option')].map(o=>[o.value,o.innerText.trim()])") or []
    BTN = lambda t: J(f"(()=>{{const b=[...document.querySelectorAll('{FX} button')].find(x=>x.innerText.trim()==={json.dumps(t)}); return b?{{dis:b.disabled}}:null;}})()")
    goto('AG-07.dc.html', 1.5); limpa(); goto('AG-07.dc.html', 1.5); pr = ag_pronto()
    alvo = J("""(()=>{ try{ const {AGX,AG_REF,agAlvoT}=window.__agx; const r=AG_REF['tebuconazol-200-ec']; const MA=AGX.I.culturas.findIndex(c=>c[0]==='Mamão');
      const p=AGX.P.find(p=>p.key===r.key&&p.culSet.has(MA)&&AGX.PU[p.i].some(x=>x[0]===MA&&/antracnose/i.test(agAlvoT(x[1],true)))); if(!p) return null;
      const a=AGX.PU[p.i].find(x=>x[0]===MA&&/antracnose/i.test(agAlvoT(x[1],true)))[1]; return {reg:p.reg,nome:p.nome,MA,a,at:agAlvoT(a,true)}; }catch(e){ return null; } })()""") or {}
    AT = alvo.get('at') or 'antracnose'   # alvo como o AG-07 o mostra (nome comum do AGROFIT), o mesmo texto que vai para a O.S.
    J(f"location.hash='#reg-{alvo.get('reg')}'"); time.sleep(.9)
    b0 = BTN('Usar na O.S.'); f0 = J(f"(document.querySelector('{FX}')||{{innerText:''}}).innerText") or ''; pa0 = PASSO()
    chk(f'E2.1 AG-07 ficha {alvo.get("nome")} (reg. {alvo.get("reg")}): só consulta (sem "Preparar receituário", "Emitir receituário" ou "Receituário emitido"); "Usar na O.S." desligado até cultura e alvo',
        pr and bool(alvo) and b0 == {'dis': True} and 'Preparar receituário' not in f0 and 'Receituário emitido' not in f0 and 'Emitir receituário' not in f0
        and not J("!!document.querySelector('aside[aria-label=\"Preparar receituário agronômico\"]')") and 'Escolha a cultura e o alvo' in pa0, [pr, alvo, b0, pa0])
    sv(f'{FX} select[aria-label="Cultura do uso"]', str(alvo.get('MA'))); sv(f'{FX} select[aria-label="Alvo do uso"]', str(alvo.get('a')))
    op = [o[0] for o in OPTS('Ordem A liberar') if o[0]]
    chk('E2.2 cultura Mamão × antracnose: "Ordem A liberar" oferece só as ordens A liberar de mamão (OS-0501, OS-0502, OS-0511)', op == ['OS-0501', 'OS-0502', 'OS-0511'], OPTS('Ordem A liberar'))
    sv(f'{FX} select[aria-label="Ordem A liberar"]', 'OS-0501'); pa1 = PASSO(); b1 = BTN('Usar na O.S.')
    chk('E2.3 escolhida a OS-0501: "Usar na O.S." ligado; o texto diz o próximo passo (Ajustar antes de liberar, a agrônoma informa a dose, a O.S. confere e grava; a consulta não emite receituário)',
        b1 == {'dis': False} and 'Abre a OS-0501 em Ajustar antes de liberar com Tebuconazol 200 EC incluído' in pa1 and 'Esta consulta não emite receituário' in pa1, [b1, pa1])
    shot('ag07_usar_1440'); junta('AG-07')
    clk('Usar na O.S.', FX); time.sleep(2.2)
    for _ in range(20):
        if J("!!document.querySelector('[role=group][aria-label=\"Ajustar antes de liberar\"]')"): break
        time.sleep(.3)
    AJ = lambda: J("(document.querySelector('[role=group][aria-label=\"Ajustar antes de liberar\"]')||{innerText:''}).innerText.replace(/\\s+/g,' ')") or ''
    aj = AJ(); foco = J("(document.activeElement||{}).id") or ''; dose0 = J("(document.getElementById('aj_n0')||{value:'?'}).value")
    chk('E2.4 O.S. abre a OS-0501 em "Ajustar antes de liberar" com Tebuconazol 200 EC incluído "para antracnose em mamão · Consulta Agrofit", dose em branco e com foco; o link é consumido (#OS-0501)',
        J("location.pathname").endswith('OS.dc.html') and 'Tebuconazol 200 EC incluído' in aj and f'para {AT} em mamão · Consulta Agrofit' in aj and dose0 == '' and foco == 'aj_n0'
        and J("location.hash") == '#OS-0501', [J("location.href"), aj[:400], foco, dose0])
    shot('os_usar_1440')
    v0 = J("window.__cen.cenGet().ordens['OS-0501'].versao")
    sv('#aj_n0', '3'); clk('Salvar e liberar', '[role=group][aria-label="Ajustar antes de liberar"]')
    aj3 = AJ(); e3 = J("window.__cen.cenGet().ordens['OS-0501']") or {}
    chk('E2.5 RECUSA dose 3 L/ha: erro junto ao campo "dose fora da bula: 0,5–1 L/ha" (a trava legal única do CTL-1); OS-0501 continua A liberar, sem v2 e sem o produto',
        'dose fora da bula: 0,5–1 L/ha' in aj3 and e3.get('etapa') == 'A liberar' and e3.get('versao') == v0 and not any(x['p'] == 'Tebuconazol 200 EC' for x in e3.get('ins', [])), [aj3[-300:], e3.get('etapa'), e3.get('versao')])
    sv('#aj_n0', '0,8'); clk('Salvar e liberar', '[role=group][aria-label="Ajustar antes de liberar"]'); time.sleep(.4)
    t5 = TOAST(); e5 = J("window.__cen.cenGet().ordens['OS-0501']") or {}; ev = ' | '.join(x['t'] for x in (e5.get('osc') or {}).get('ev', []))
    ins = next((x for x in e5.get('ins', []) if x['p'] == 'Tebuconazol 200 EC'), {})
    chk('E2.6 dose 0,8 L/ha: "OS-0501 ajustada para v2 e liberada"; a aprovação (CMD-42) grava "Tebuconazol 200 EC 0,8 L/ha para antracnose" e a liberação (CMD-06) fica separada',
        'OS-0501 ajustada para v2 e liberada' in t5 and e5.get('etapa') == 'Liberadas' and ins.get('alvo') == AT
        and re.search(r'v2 aprovada por Ana \(agrônoma\).*Tebuconazol 200 EC 0,8 L/ha para ' + re.escape(AT) + r' \(CMD-42\)', ev) and 'v2 liberada por' in ev, [t5, e5.get('etapa'), ins, ev])
    pan = J("(()=>{const a=document.querySelector('aside[role=dialog]'); if(!a) return ''; [...a.querySelectorAll('section[aria-label] > button[aria-expanded=\"false\"]')].forEach(b=>b.click()); return '';})()") or ''
    time.sleep(.5); pan = J("(document.querySelector('aside[role=dialog]')||{innerText:''}).innerText.replace(/\\s+/g,' ')") or ''
    chk('E2.7 Origem da ordem mostra a aprovação com produto, dose e alvo (o registro nasce na O.S.)', f'Tebuconazol 200 EC 0,8 L/ha para {AT} (CMD-42)' in pan and f'incluído Tebuconazol 200 EC 0,8 L/ha para {AT}' in pan, pan[-700:])
    junta('OS')
    # repetição: o mesmo link de novo não inclui (a ordem já saiu de A liberar)
    n5 = len(e5.get('ins', []))
    goto('OS.dc.html#OS-0501:usar=' + '|'.join(map(lambda s: __import__('urllib.parse').parse.quote(s), ['Tebuconazol 200 EC', 'Mamão', AT])), 1.6)
    t6 = TOAST(); e6 = J("window.__cen.cenGet().ordens['OS-0501']") or {}
    chk('E2.8 REPETIÇÃO: o mesmo link com a OS-0501 já liberada → "OS-0501 está em Liberadas: Tebuconazol 200 EC não foi incluído"; nada muda',
        'OS-0501 está em Liberadas: Tebuconazol 200 EC não foi incluído' in t6 and len(e6.get('ins', [])) == n5 and e6.get('versao') == e5.get('versao')
        and not J("!!document.querySelector('[role=group][aria-label=\"Ajustar antes de liberar\"]')"), [t6, e6.get('versao')])
    goto('AG-07.dc.html', 1.5); ag_pronto(); J(f"location.hash='#reg-{alvo.get('reg')}'"); time.sleep(.9)
    sv(f'{FX} select[aria-label="Cultura do uso"]', str(alvo.get('MA'))); sv(f'{FX} select[aria-label="Alvo do uso"]', str(alvo.get('a')))
    op2 = [o[0] for o in OPTS('Ordem A liberar') if o[0]]
    chk('E2.9 de volta ao AG-07: a OS-0501 (liberada) saiu das ordens oferecidas (OS-0502, OS-0511)', op2 == ['OS-0502', 'OS-0511'], op2)
    # sem o papel: Caio (PCP) segue o link → nada é incluído, a mensagem nomeia quem decide
    J("localStorage.setItem('safrion.perfilDemo','Caio')")
    goto('OS.dc.html#OS-0502:usar=Tebuconazol%20200%20EC|Mam%C3%A3o|' + __import__('urllib.parse').parse.quote(AT), 1.6); t7 = TOAST(); e7 = J("window.__cen.cenGet().ordens['OS-0502']") or {}
    chk('E2.10 RECUSA sem o papel: Caio (PCP) → "Incluir Tebuconazol 200 EC na OS-0502 é decisão de Ana (agrônoma). Nada foi incluído."; sem formulário de ajuste',
        'Incluir Tebuconazol 200 EC na OS-0502 é decisão de Ana (agrônoma). Nada foi incluído.' in t7 and not J("!!document.querySelector('[role=group][aria-label=\"Ajustar antes de liberar\"]')")
        and not any(x['p'] == 'Tebuconazol 200 EC' for x in e7.get('ins', [])), [t7, e7.get('etapa')])
    J("localStorage.setItem('safrion.perfilDemo','Ana')"); junta('OS repetição')
    # registro sem produto da fazenda: "Usar na O.S." fica desligado e diz o motivo
    goto('AG-07.dc.html', 1.5); ag_pronto()
    sem = J("""(()=>{ try{ const {AGX}=window.__agx; const SO=AGX.I.culturas.findIndex(c=>c[0]==='Soja'); const p=AGX.P.find(p=>!AGX.FK[p.key]&&p.culSet.has(SO)&&AGX.PU[p.i].some(x=>x[0]===SO)); if(!p) return null;
      return {reg:p.reg,SO,a:AGX.PU[p.i].find(x=>x[0]===SO)[1]}; }catch(e){ return null; } })()""") or {}
    J(f"location.hash='#reg-{sem.get('reg')}'"); time.sleep(.9)
    sv(f'{FX} select[aria-label="Cultura do uso"]', str(sem.get('SO'))); sv(f'{FX} select[aria-label="Alvo do uso"]', str(sem.get('a')))
    chk('E2.11 RECUSA sem produto da fazenda: "Usar na O.S." desligado com "Sem produto da fazenda com este ingrediente ativo…"',
        BTN('Usar na O.S.') == {'dis': True} and 'Sem produto da fazenda com este ingrediente ativo' in PASSO(), [sem, PASSO()])

    # produto da fazenda só de referência de bula (sem lote nem plano, fora do catálogo da O.S.): sem link sem saída
    ref = J("""(()=>{ try{ const {AGX}=window.__agx; const SO=AGX.I.culturas.findIndex(c=>c[0]==='Soja'); const r=Object.values(AGX.FK).find(L=>L.every(x=>x.nomes_fazenda.length&&x.nomes_fazenda.every(n=>/^Mancozebe/.test(n))));
      const p=r&&AGX.P.find(p=>p.key===r[0].key&&p.culSet.has(SO)&&AGX.PU[p.i].some(x=>x[0]===SO)); if(!p) return null; return {reg:p.reg,SO,a:AGX.PU[p.i].find(x=>x[0]===SO)[1]}; }catch(e){ return null; } })()""") or {}
    J(f"location.hash='#reg-{ref.get('reg')}'"); time.sleep(.9)
    sv(f'{FX} select[aria-label="Cultura do uso"]', str(ref.get('SO'))); sv(f'{FX} select[aria-label="Alvo do uso"]', str(ref.get('a')))
    chk('E2.11b RECUSA produto só de referência (Mancozebe 750 WG, sem lote nem plano): "Usar na O.S." desligado com "… só como referência de bula … cadastre o produto"',
        bool(ref) and BTN('Usar na O.S.') == {'dis': True} and 'Mancozebe 750 WG só como referência de bula' in PASSO(), [ref, PASSO()])

    # =============== 390 px ===============
    c.size(390, 844); goto('AG-07.dc.html', 1.5); ag_pronto(); J(f"location.hash='#reg-{alvo.get('reg')}'"); time.sleep(.9)
    sv(f'{FX} select[aria-label="Cultura do uso"]', str(alvo.get('MA'))); sv(f'{FX} select[aria-label="Alvo do uso"]', str(alvo.get('a')))
    geo = J(f"""(()=>{{const a=document.querySelector('{FX}'); const b=[...a.querySelectorAll('button')].find(x=>x.innerText.trim()==='Usar na O.S.'); const r=b.getBoundingClientRect(), q=a.getBoundingClientRect();
      const s=a.querySelector('select[aria-label="Ordem A liberar"]').getBoundingClientRect(); return [Math.round(r.right),Math.round(q.right),Math.round(s.right),a.scrollWidth,a.clientWidth];}})()""") or [9, 0, 9, 9, 0]
    chk(f'E2.12 390 px: ficha do AG-07 sem rolagem lateral; "Ordem A liberar" e "Usar na O.S." cabem ({geo})', geo[0] <= geo[1] and geo[2] <= geo[1] and geo[3] <= geo[4] and LARG()[0] <= LARG()[1], [geo, LARG()])
    shot('ag07_390')
    sv(f'{FX} select[aria-label="Ordem A liberar"]', 'OS-0502'); clk('Usar na O.S.', FX); time.sleep(2.2)
    for _ in range(20):
        if J("!!document.querySelector('[role=group][aria-label=\"Ajustar antes de liberar\"]')"): break
        time.sleep(.3)
    aj8 = AJ(); g8 = J("(()=>{const g=document.querySelector('[role=group][aria-label=\"Ajustar antes de liberar\"]'); if(!g) return [9,0]; const i=document.getElementById('aj_n0').getBoundingClientRect(); return [Math.round(i.right),innerWidth];})()") or [9, 0]
    chk('E2.13 390 px: OS-0502 abre o ajuste com Tebuconazol 200 EC incluído para antracnose; campo da dose dentro da tela, sem rolagem lateral',
        'Tebuconazol 200 EC incluído' in aj8 and f'para {AT} em mamão' in aj8 and g8[0] <= g8[1] and LARG()[0] <= LARG()[1], [aj8[:200], g8, LARG()])
    shot('os_usar_390')
    goto('IR-04.dc.html'); fazenda('Lagoa Grande'); time.sleep(.3); r9 = ROW('Rio A (demonstração)')
    chk('E3.7 390 px: IR-04 mostra a mesma outorga (186 L/s, "Vence em 90 dias") sem rolagem lateral', '186 L/s' in r9 and 'Vence em 90 dias' in r9 and LARG()[0] <= LARG()[1], [r9, LARG()])
    shot('ir04_390'); junta('390')
    chk('E0 nenhum erro de execução nas páginas', not ERRS, ERRS[:5])
finally:
    try:
        if c: c.close()
    finally: srv.terminate()
print(f'\nRESULTADO {len(OK)}/{len(OK) + len(FAIL)}', FAIL)
sys.exit(1 if FAIL else 0)
