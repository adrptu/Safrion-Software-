# -*- coding: utf-8 -*-
"""Carência e destino (MAPA-CARENCIA-LMR-20261003) · testes.
Parte 1 (unit): motor puro (dados_carencia.JS + núcleo da O.S.) no jsc, com os seis contraexemplos do canal (carencia_unit.js).
Parte 2 (fluxo): Chrome headless com o mapa real da Lagoa Grande (CDP_GL=1): fluxo do mamão mapa → aplicação → colheita/lote →
avaliação do destino, com resposta impeditiva (liberar colheita no Pivô 23) e recuperação (Rever programação), aviso preventivo da
aplicação, colheita registrada em carência (fato não impedido, vai para conferência), lote por destino na CO-06 e telas de celular.
Uso: python3 carencia_test.py [unit|fluxo]   (sem argumento: as duas partes). Capturas em _probe/carencia_*.png."""
import os, sys, time, json, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'
PARTE = sys.argv[1] if len(sys.argv) > 1 else 'tudo'
# SINT-T01: jsc no macOS; fora dele (Linux/nuvem) o node, com print → console.log; o mesmo JS nos dois
MOTOR, PRELUDIO = ([JSC], '') if os.path.exists(JSC) else (['node'], 'globalThis.print=(...a)=>console.log(...a);\n')
FAIL = []; N = [0]
def ok(cond, msg, extra=''):
    N[0] += 1; print(('OK    ' if cond else 'FALHA ') + msg + ('' if cond else ' · ' + str(extra)[:400]), flush=True)
    if not cond: FAIL.append(msg)


def unit():
    import cenario
    from areas.processo_os import JS_NUCLEO
    src = PRELUDIO + cenario.perfis_js() + cenario.js_prefixo() + JS_NUCLEO + open(os.path.join(HERE, 'carencia_unit.js'), encoding='utf-8').read()
    p = os.path.join(HERE, '_probe', 'carencia_unit_all.js'); open(p, 'w', encoding='utf-8').write(src)
    r = subprocess.run(MOTOR + [p], capture_output=True, text=True, timeout=60)
    out = r.stdout.strip().splitlines()
    ok(r.returncode == 0 and out, 'motor JS (jsc/node) executou sem erro', r.stderr[:400])
    for x in (json.loads(out[-1]) if out else []): ok(x['ok'], 'unit ' + x['n'], x['info'])
    # app de campo: a mesma guarda no início do turno de colheita (JS do app com o motor leve)
    from areas import mobile
    src = PRELUDIO + cenario.js_prefixo() + mobile.JS_BASE + mobile.MBAPP_JS + open(os.path.join(HERE, 'carencia_app_unit.js'), encoding='utf-8').read()
    p = os.path.join(HERE, '_probe', 'carencia_app_all.js'); open(p, 'w', encoding='utf-8').write(src)
    r = subprocess.run(MOTOR + [p], capture_output=True, text=True, timeout=60); out = r.stdout.strip().splitlines()
    ok(r.returncode == 0 and out, 'motor JS (jsc/node) executou o JS do app sem erro', r.stderr[:400])
    for x in (json.loads(out[-1]) if out else []): ok(x['ok'], 'app ' + x['n'], x['info'])


def fluxo():
    os.environ['CDP_GL'] = '1'   # o mapa real (MapLibre) precisa de WebGL por software no Chrome headless
    from cadc_lib import T
    t = T(); J = t.J; PR = os.path.join(HERE, '_probe')
    shot = lambda n: t.c.shot(os.path.join(PR, n))
    def setv(sel, val):
        return J(f"""(()=>{{const i=document.querySelector({json.dumps(sel)}); if(!i) return false; const P=i.tagName==='SELECT'?HTMLSelectElement.prototype:HTMLInputElement.prototype;
          Object.getOwnPropertyDescriptor(P,'value').set.call(i,{json.dumps(val)}); i.dispatchEvent(new Event('input',{{bubbles:true}})); i.dispatchEvent(new Event('change',{{bubbles:true}})); return true;}})()""")
    def btn(txt, root=''):
        r = J(f"(()=>{{const b=[...document.querySelectorAll({json.dumps((root + ' button').strip())})].find(b=>b.innerText.trim()==={json.dumps(txt)}); if(!b) return false; b.click(); return true;}})()"); time.sleep(.4); return r
    def pronto():
        for _ in range(80):
            if J("!!(window.__LGI&&__LGI.pronto)"): return True
            time.sleep(.25)
        return False
    pan = lambda: (J("(()=>{const a=document.querySelector('aside[aria-label]'); return a?a.innerText.replace(/\\s+/g,' '):'';})()") or '')
    acts = lambda: J("[...document.querySelectorAll('aside[aria-label] > div:last-child a')].map(a=>[a.innerText.trim(),a.getAttribute('href')])") or []
    rot = lambda pid: J(f"(()=>{{const m=__LGI.markers['{pid}']; return m?m.getElement().getAttribute('aria-label'):'';}})()") or ''
    nums = lambda: (J("(document.querySelector('[role=group][aria-label^=\"Indicadores de\"]')||{innerText:''}).innerText.replace(/\\n/g,' ')") or '')
    ospan = lambda: (J("(()=>{const a=document.querySelector('aside[role=dialog]'); if(!a) return ''; [...a.querySelectorAll('section[aria-label] > button[aria-expanded=\"false\"]')].forEach(b=>b.click()); return a.innerText.replace(/\\s+/g,' ');})()") or '')
    cen = lambda expr: J(f"(()=>{{const X=window.__car; const c=X.cenGet(); return ({expr});}})()")
    LONGOS = "[...document.querySelectorAll('aside[aria-label] *')].filter(e=>e.children.length===0&&e.innerText&&e.innerText.trim().split(/\\s+/).length>=14).map(e=>e.innerText.trim())"
    # aplicação com carência NÃO conferida na bula (azoxistrobina, 05/09, Pivô 24) e colheita A liberar a partir de 24/09 no mesmo pivô
    MKBULA = """(()=>{const r=window.__car.cenMudar(null,c=>{ const base=c.ordens['OS-0440'].osc.novo;
      const mk=(id,tipo,tal,area,etapa,ins,ap,jan)=>{ const no=Object.assign(JSON.parse(JSON.stringify(base)),{id,tipo,talhao:tal,area,saldo:area,keys:[id],janela:jan,ins:ins.map(p=>({p,dose:1,un:'L',tot:area,sit:'Reserva ao liberar'})),faz:'Lagoa Grande'});
        c.ordens[id]={id,tipo,talhao:tal,area,etapa,versao:'v1',realizado:ap.length?area:0,saldo:ap.length?0:area,resp:'Wesley',ins:no.ins.map(x=>({p:x.p,dose:1,un:'L',tot:area})),req:null,selos:[],ap,reservado:false,osc:{novo:no}}; };
      mk('OS-0465','Pulverização · antracnose','Pivô 24',20,'Encerradas',['Azoxistrobina 250 SC'],[{d:'05/09',dia:1,ha:20,st:'Conferido',sinc:true}],'05/09');
      mk('OS-0466','Colheita · semana 39','Pivô 24',20,'A liberar',[],[],'a partir de 24/09/2026');
      return {msg:'ok'}; }); return r.erro||r.msg;})()"""
    try:
        # ---------- 1 · mapa: camada, ícone, PV23 em carência (dados reais do cenário: OS-0508 tebuconazol 19–20/09) ----------
        t.goto('Main.dc.html'); J("localStorage.removeItem('talhao-os-cenario-v1'); sessionStorage.setItem('mapa-ctx',JSON.stringify({mf_faz:'Lagoa Grande',lay:'Integrado',tsel:[]}))")
        t.goto('IN-04.dc.html#car:PV23'); ok(pronto(), 'mapa real da Lagoa Grande pronto'); time.sleep(.8)
        rail = J("[...document.querySelectorAll('nav[aria-label=\"Funcionalidades do mapa\"] button')].map(b=>b.innerText.trim())") or []
        ico = J("(()=>{const b=[...document.querySelectorAll('nav[aria-label=\"Funcionalidades do mapa\"] button')].find(b=>b.innerText.trim()==='Carência e destino'); const p=b&&b.querySelector('svg path'); return p?p.getAttribute('d'):'';})()") or ''
        ok('Carência e destino' in rail and rail.index('Carência e destino') == rail.index('Pragas e doenças') + 1, 'barra do mapa com a camada Carência e destino depois de Pragas e doenças', rail)
        ok(ico.startswith('M12 12m-9 0a9 9') and 'M10.3 3.9' not in ico, 'ícone da camada = relógio do catálogo (o triângulo fica para alerta real)', ico)
        sel = J("(()=>{const b=[...document.querySelectorAll('nav[aria-label=\"Funcionalidades do mapa\"] button')].find(b=>b.innerText.trim()==='Carência e destino'); return b?b.getAttribute('aria-selected'):'';})()")
        p = pan(); a = acts()
        ok(sel == 'true' and 'Pivô 23' in p and 'carência até 26/09' in rot('PV23'), 'link #car:PV23 abre a camada com o Pivô 23 selecionado; rótulo do pivô "carência até 26/09" = último dia em carência (texto, não só cor)', [sel, rot('PV23'), p[:160]])
        ok('Colheita impedida até 26/09 · Tebuconazol 200 EC (OS-0508)' in p and 'determina o prazo' in p and 'faixa não registrada: vale o talhão todo' in p and 'Consultado em 23/09/2026 (hoje)' in p and 'Atualização' in p,
           'painel: prazo determinante, faixa não identificada vale para o pivô, data consultada e atualização', p[:600])
        ok(a == [['Ver restrição', 'OS.dc.html#OS-0508']], 'uma ação primária no estado: Ver restrição → OS-0508', a)
        ok('Em carência 1' in nums() and 'Prazo cumprido não é conformidade' in p, 'faixa de números e aviso "prazo cumprido não é conformidade"', nums())
        ok(not J(LONGOS), 'painel sem parágrafo explicativo (nenhum texto com 14 palavras ou mais num elemento)', J(LONGOS))
        shot('carencia_mapa_pv23.png')
        # 2 · consultar em 7 dias: prazo cumprido, nunca "conforme"
        btn('Em 7 dias'); time.sleep(.5); p = pan()
        ok('prazo cumprido em 27/09 · destino a avaliar' in rot('PV23') and 'situação em 30/09' in p.lower() and 'conforme no escopo' not in p.lower() and 'pode exportar' not in p.lower(),
           'consultado em 30/09: prazo cumprido e destino a avaliar (sem selo de conforme/exportar)', [rot('PV23'), p[:300]])
        shot('carencia_mapa_7dias.png'); btn('Hoje'); time.sleep(.3)
        # 3 · PV06: aplicação só planejada (OS-0504) não conta; lotes colhidos antes, avaliação por destino
        J("location.hash='#car:PV06'"); time.sleep(.8); p = pan()
        ok('Previsto, não conta: OS-0504 · Abamectina 18 EC' in p and 'colheita impedida até 07/10' in p and 'sem aplicação apontada' in rot('PV06'),
           'PV06: OS-0504 liberada aparece como previsão (não conta) com a colheita impedida até 07/10 se aplicada em 24/09', [rot('PV06'), p[:500]])
        ok(not J(LONGOS), 'PV06: painel sem parágrafo explicativo (previsão e lotes em frases curtas)', J(LONGOS))
        ok('Lote LC-0510-1' in p and 'Conforme no escopo · Mercado interno · Brasil' in p and 'Lote LC-0510-2' in p and 'Não conforme' in p,
           'PV06: lotes colhidos com a avaliação do destino (LC-0510-1 conforme no escopo do mercado interno; LC-0510-2 não conforme no mercado sintético)', p[p.find('LOTES'):][:400])
        # 4 · Integrado: uma linha da camada no painel do talhão, que leva até ela
        J("(()=>{const b=[...document.querySelectorAll('nav[aria-label=\"Funcionalidades do mapa\"] button')].find(b=>b.innerText.trim()==='Integrado'); b.click();})()"); time.sleep(.6)
        J("location.hash='#car:PV23'"); time.sleep(.8)
        J("(()=>{const b=[...document.querySelectorAll('nav[aria-label=\"Funcionalidades do mapa\"] button')].find(b=>b.innerText.trim()==='Integrado'); b.click();})()"); time.sleep(.6); p = pan()
        ok('Carência e destino carência até 26/09' in p and 'Ver carência' in p, 'Integrado: linha "Carência e destino" com Ver carência', p[:700])
        btn('Ver carência', 'aside'); time.sleep(.5)
        ok('CARÊNCIA E DESTINO' in pan().upper() and J("location.hash")=='', 'Ver carência abre a camada sem perder o talhão', pan()[:200])
        ok(t.errs() == '', 'mapa sem erro de JavaScript', t.errs())
        # ---------- 5 · O.S.: colheita no Pivô 23 impedida pela carência (comando, não cor) e recuperação ----------
        t.goto('OS.dc.html'); time.sleep(.5)
        btn('Criar ordem', 'header'); setv('#nv_saf', 'LG2627'); time.sleep(.3); setv('#nv_cult', 'lg23'); time.sleep(.3); setv('#nv_atv', 'q3'); time.sleep(.3); setv('#nv_jan', '2026-09-25'); time.sleep(.3)
        btn('Emitir ordem', 'aside[role=dialog][aria-label="Nova ordem"]'); time.sleep(.6)
        oid = (J("(()=>{const a=document.querySelector('aside[role=dialog]'); return a?a.getAttribute('aria-label'):'';})()") or '').split(' · ')[0]; p = ospan()
        ok(oid == 'OS-0440' and 'Liberar bloqueado: carência em curso em Pivô 23 até 26/09' in p and 'OS-0508' in p and 'Quem resolve: Ana (agrônoma) reprograma a colheita para 27/09' in p,
           'colheita OS-0440 (Pivô 23, a partir de 25/09): Liberar bloqueado com motivo (OS-0508, carência até 26/09) e quem resolve (colheita a partir de 27/09)', [oid, p[:700]])
        ok(not J("[...document.querySelectorAll('aside[role=dialog] button')].some(b=>b.innerText.trim()==='Liberar para execução')") and 'Rever programação' in p and 'Carência até 26/09' in p and 'a colheita pode começar em 27/09' in p,
           'sem botão Liberar; Rever programação junto ao impedimento; selo "Carência até 26/09"', p[:400])
        er = J("(()=>{const X=window.__car; const r=X.cenMudar(null,c=>{ const o=c.ordens['OS-0440']; if(!o) throw new Error('sem OS-0440'); return window.__cen.osc_liberar(c,'OS-0440',false,'','Ana'); }); return r.erro||'';})()") or ''
        ok('carência em curso' in er and cen("c.ordens['OS-0440'].etapa") == 'A liberar', 'o próprio comando recusa a liberação (não é só a cor do mapa)', er)
        shot('carencia_os_impedida.png')
        # o mapa mostra o mesmo impedimento e leva à O.S. (Rever programação)
        t.goto('IN-04.dc.html#car:PV23'); pronto(); time.sleep(.8)
        ok(acts() == [['Rever programação', 'OS.dc.html#OS-0440']], 'mapa: com a colheita impedida, a ação primária do Pivô 23 vira Rever programação → OS-0440', acts())
        t.goto('OS.dc.html#OS-0440'); time.sleep(.8)
        setv('aside[role=dialog] [aria-label="Rever programação da colheita"] input[type=date]', '2026-09-26'); time.sleep(.2); btn('Rever programação', 'aside[role=dialog]'); time.sleep(.5); p = ospan()
        ok('Liberar bloqueado' in p and cen("c.ordens['OS-0440'].osc.janela") == 'a partir de 26/09/2026', 'reprogramar para 26/09 ainda cai na carência: continua impedida', [p[:300], cen("c.ordens['OS-0440'].osc.janela")])
        btn('Rever programação', 'aside[role=dialog]'); time.sleep(.5)   # valor sugerido = fim da carência (27/09)
        setv('aside[role=dialog] [aria-label="Rever programação da colheita"] input[type=date]', '2026-09-27'); time.sleep(.2); btn('Rever programação', 'aside[role=dialog]'); time.sleep(.6); p = ospan()
        ok('Liberar bloqueado' not in p and J("[...document.querySelectorAll('aside[role=dialog] button')].some(b=>b.innerText.trim()==='Liberar para execução')") and 'Colheita reprogramada por Ana (agrônoma)' in p,
           'recuperação: colheita a partir de 27/09 libera o comando e a origem guarda a reprogramação', p[:600])
        btn('Liberar para execução', 'aside[role=dialog]'); btn('Confirmar liberação', 'aside[role=dialog]'); time.sleep(.4)
        ok(cen("c.ordens['OS-0440'].etapa") == 'Liberadas', 'OS-0440 liberada depois de reprogramada', cen("c.ordens['OS-0440'].etapa"))
        shot('carencia_os_reprogramada.png')
        # 5b · carência não conferida na bula (prazo provisório já vencido): colheita impedida; o agrônomo registra a carência conferida e recupera
        r = J(MKBULA); t.goto('Main.dc.html'); t.goto('OS.dc.html#OS-0466'); time.sleep(.9); p = ospan()
        bts = J("[...document.querySelectorAll('aside[role=dialog] button')].map(b=>b.innerText.trim())") or []
        ok(r == 'ok' and 'Liberar bloqueado: carência sem dados suficientes em Pivô 24' in p and 'não conferidos na bula' in p and 'Liberar para execução' not in bts and 'Registrar carência conferida' in bts,
           'colheita OS-0466 após azoxistrobina (7 dias não conferidos, 05/09): Liberar bloqueado e o formulário "Registrar carência conferida"', [r, bts, p[:500]])
        shot('carencia_os_bula_impedida.png')
        setv('aside[role=dialog] [aria-label="Registrar carência conferida na bula"] input', '10'); time.sleep(.2); btn('Registrar carência conferida', 'aside[role=dialog]'); time.sleep(.6); p = ospan()
        bts = J("[...document.querySelectorAll('aside[role=dialog] button')].map(b=>b.innerText.trim())") or []
        ok('Liberar bloqueado' not in p and 'Liberar para execução' in bts and cen("c.car.bula['Azoxistrobina 250 SC|Mamão'][0].dias") == 10,
           'recuperação: carência conferida (10 dias, até 14/09) registrada no cenário e a colheita pode ser liberada', [bts, p[:300]])
        shot('carencia_os_bula_conferida.png')
        # ---------- 6 · aviso preventivo na aplicação e aplicação efetiva da OS-0504 (Pivô 6) ----------
        # SINT-T01: a área feita é a do Pivô 6 na fonte única (dados_lagoa_fonte), na forma digitada (vírgula), sem literal de área
        import dados_lagoa_fonte as _F; A06 = format(_F.PIVOS_HA[6], 'g').replace('.', ',')
        t.goto('OS.dc.html#OS-0504'); time.sleep(.8); p = ospan()
        ok('Conflito com a colheita em Pivô 6' in p and 'impedida até 07/10' in p and 'Conflito com colheita até 07/10' in p and J("[...document.querySelectorAll('aside[role=dialog] button')].some(b=>b.innerText.trim()==='Iniciar execução')"),
           'OS-0504 liberada: aviso preventivo do conflito com a colheita do mamão (até 07/10) sem bloquear o início', p[:700])
        shot('carencia_os_conflito_aplicacao.png')
        btn('Iniciar execução', 'aside[role=dialog]'); btn('Confirmar início', 'aside[role=dialog]'); time.sleep(.4)
        btn('Registrar apontamento', 'aside[role=dialog]'); time.sleep(.3)
        setv('aside[role=dialog] input[type=date]', '2026-09-24'); setv('aside[role=dialog] input[aria-label="Área feita em hectares"]', A06); time.sleep(.2)
        btn('Salvar apontamento', 'aside[role=dialog]'); time.sleep(.5)
        ok(cen("c.ordens['OS-0504'].ap.filter(a=>a.st!=='Previsto').length") == 1 and cen("c.ordens['OS-0504'].etapa") == 'Em execução', f'OS-0504 executada: apontamento de 24/09 em {A06} ha', cen("JSON.stringify(c.ordens['OS-0504'].ap)"))
        # a colheita da semana 39 no Pivô 19 é registrada (fato) depois de uma aplicação: nunca impedida, vai para conferência
        r = J("""(()=>{const X=window.__car; const r=X.cenMudar(null,c=>{ c.ordens['OS-0441']={id:'OS-0441',tipo:'Pulverização · Controle de ácaro e cochonilha',talhao:'Pivô 19',area:42,etapa:'Em conferência',versao:'v1',realizado:42,saldo:0,resp:'Wesley',
             ins:[{p:'Abamectina 18 EC',dose:0.5,un:'L',tot:21}],req:null,selos:[],ap:[{d:'22/09',dia:1,ha:42,st:'Conferido',sinc:true,origem:'app'}],reservado:false,osc:{}};
             const o=c.ordens['OS-0505']; o.ap=o.ap.filter(a=>a.st!=='Previsto').concat([{d:'24/09',dia:3,ha:14,st:'Provisório',sinc:true,origem:'app'}]); o.realizado=42; o.saldo=0; return {msg:'ok'}; }); return r.erro||r.msg;})()""")
        t.goto('OS.dc.html#OS-0505'); time.sleep(.8); p = ospan()
        ok(r == 'ok' and 'Colhido em carência · conferir' in p and 'Pendência com Ana (agrônoma)' in p and 'LC-0505-3' in p,
           'colheita apontada em carência no Pivô 19 (app): registrada, com selo "Colhido em carência · conferir" e dono Ana', [r, p[:600]])
        # ---------- 7 · mapa depois da aplicação: PV06 em carência; lotes colhidos antes seguem com a avaliação deles ----------
        t.goto('IN-04.dc.html#car:PV06'); pronto(); time.sleep(.8); p = pan()
        ok('carência até 07/10' in rot('PV06') and 'Abamectina 18 EC · OS-0504 · 24/09' in p and 'Lote LC-0510-1' in p and 'Conforme no escopo · Mercado interno · Brasil' in p,
           'PV06 após aplicar a OS-0504: carência até 07/10; o lote LC-0510-1 (colhido em 16/09) não é contaminado retroativamente', [rot('PV06'), p[:500]])
        shot('carencia_mapa_pv06_aplicada.png')
        t.goto('IN-04.dc.html#car:PV19'); time.sleep(.8); p = pan()
        ok('carência até 05/10' in rot('PV19') and 'Lote LC-0505-3' in p and 'Não conforme' in p, 'PV19: carência até 05/10 e o lote de 24/09 aparece Não conforme', p[:600])
        ok(t.errs() == '', 'mapa e O.S. sem erro de JavaScript', t.errs())
        # ---------- 8 · CO-06: lote por destino, genealogia, troca de destino com histórico ----------
        t.goto('CO-06.dc.html#LC-0505-3'); time.sleep(1.0)
        det = lambda: (J("(document.getElementById('car-det')||{innerText:''}).innerText.replace(/\\s+/g,' ')") or '')
        d = det()
        ok('Lote LC-0505-3' in d and 'Não conforme' in d and 'dentro da carência de Abamectina 18 EC' in d and 'OS-0441' in d and 'Quem resolve: Ana (agrônoma)' in d,
           'CO-06 abre o lote do link: Não conforme por colheita em carência, com aplicação, prazo e quem resolve', d[:600])
        shot('carencia_co06_nao_conforme.png')
        J("(()=>{const b=[...document.querySelectorAll('[role=listitem] button')].find(b=>b.innerText.trim().startsWith('LC-0510-1')); b&&b.click(); return !!b;})()"); time.sleep(.5)
        d = det()
        ok('Conforme no escopo · Mercado interno · Brasil' in d and 'Conforme apenas neste destino e neste escopo' in d and 'Nenhuma aplicação apontada na parcela até a colheita' in d,
           'LC-0510-1: conforme só no escopo do mercado interno (aplicação posterior não conta)', d[:500])
        btn('Liberar para Mercado interno · Brasil', '#car-det'); time.sleep(.5); d = det()
        ok('Liberado para Mercado interno · Brasil' in d and 'só neste destino e escopo' in d and cen("c.car.lib['LC-0510-1'][0].dest") == 'MI-BR',
           'liberação comercial do LC-0510-1 registrada só para o mercado interno, no escopo avaliado', d[:500])
        setv('#car-det select', 'EXP-UE'); time.sleep(.3); btn('Trocar destino e reavaliar', '#car-det'); time.sleep(.6); d = det()
        ok('Pendente · Exportação · União Europeia' in d and 'Regra do destino não carregada' in d and 'antes: Conforme no escopo · Mercado interno · Brasil · depois: Pendente · Exportação · União Europeia' in d,
           'troca de destino reavalia (UE: regra não carregada → Pendente) e preserva a avaliação anterior no histórico', d[-500:])
        bts = J("[...document.querySelectorAll('#car-det button')].map(b=>b.innerText.trim())") or []
        ok('suspensa' in d and 'Liberação comercial impedida enquanto o lote estiver pendente' in d and not any(x.startswith('Liberar para') for x in bts),
           'destino UE: a liberação anterior fica suspensa e o comando de liberar não aparece (impedido com motivo)', [bts, d[:600]])
        shot('carencia_co06_troca_destino.png')
        J("(()=>{const b=[...document.querySelectorAll('[role=listitem] button')].find(b=>b.innerText.trim().startsWith('LM-39-01')); b&&b.click();})()"); time.sleep(.5); d = det()
        ok('LC-0510-2' in d and 'LC-0505-1' in d and 'Tiabendazol' in d and 'Laudo multirresíduo' in d and 'Pendente' in d,
           'mistura LM-39-01: genealogia com as duas origens, pós-colheita herdado e requisito do comprador separado da lei', d[:700])
        ok(t.errs() == '', 'CO-06 sem erro de JavaScript', t.errs())
        # ---------- 8b · link "Ver carência no mapa" (#car, sem talhão) não troca fazenda nem seleção ----------
        t.goto('Main.dc.html'); J("sessionStorage.setItem('mapa-ctx',JSON.stringify({mf_faz:'Santa Rita',lay:'Lavoura',tsel:['T7'],flt:{}}))")
        t.goto('IN-04.dc.html#car'); time.sleep(1.2); ctx = J("sessionStorage.getItem('mapa-ctx')") or ''
        ok('"mf_faz":"Santa Rita"' in ctx and '"tsel":["T7"]' in ctx and '"lay":"Carência e destino"' in ctx and J("location.hash") == '',
           'link #car vindo da CO-06 abre a camada na fazenda e com o talhão que já estavam (Santa Rita, T7)', ctx)
        ok(t.errs() == '', 'link #car sem erro de JavaScript', t.errs())
        # ---------- 9 · celular (390 × 844): camada e lotes alcançáveis, sem erro ----------
        t.c.size(390, 844); t.goto('IN-04.dc.html#car:PV23'); pronto(); time.sleep(1.0)
        ok('Colheita impedida até 26/09' in (J("document.body.innerText") or '') or 'carência até 26/09' in (J("document.body.innerText") or ''), 'celular: mapa abre a camada no Pivô 23 (texto presente)', '')
        shot('carencia_mobile_mapa.png')
        t.goto('CO-06.dc.html#LC-0510-2'); time.sleep(1.0)
        w = J("(()=>{const d=document.getElementById('car-det'); if(!d) return null; const m=d.closest('main')||document.body; return [Math.round(d.getBoundingClientRect().width),d.scrollWidth<=d.clientWidth+1,Math.round(m.getBoundingClientRect().width),document.documentElement.scrollWidth];})()") or [0,False,0,0]
        # a largura mínima da casca (≈980 px) é da frente de responsividade; aqui: a seção nova não transborda o próprio contêiner
        ok(w[0] > 0 and w[1] and w[0] <= w[2] and t.errs() == '', 'celular: a avaliação do lote não transborda o contêiner (sem largura fixa) e sem erro', w)
        shot('carencia_mobile_co06.png')
    finally:
        t.c.close(); t.srv.terminate()


if PARTE in ('tudo', 'unit'): unit()
if PARTE in ('tudo', 'fluxo'): fluxo()
print(f'RESULTADO: {N[0] - len(FAIL)}/{N[0]} verificações' + (' · FALHAS: ' + ' | '.join(FAIL) if FAIL else ''))
sys.exit(1 if FAIL else 0)
