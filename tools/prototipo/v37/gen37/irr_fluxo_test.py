# -*- coding: utf-8 -*-
"""Jornada da irrigação ponta a ponta (02/10/2026): o mesmo estado gravado (localStorage 'talhao-os-irrigacao-v1') em IR-01..IR-04,
IR-03det e na camada Irrigação do Mapa. Conflito resolvido continua resolvido ao recarregar e some do Mapa; OS-0394 conferida (hidrômetro
prevalece); OS-0419 iniciada e terminada → conferência automática (−1,9 %) → balanço do Pivô 2 creditado uma vez (1,7 mm) → Mapa e IR-01
mudam; Lagoa Grande: Programar irrigação no PV02 recupera a tarefa única OS-0601 (sem duplicar); páginas sem rolagem lateral a 1280 e 1440 px.
TABELAS-FOCO (06/10/2026): no IR-01 a situação é chip e o rótulo composto ("janela a definir · OS-0422", "programada · hoje 21:00",
"falta insumo · OS-0418") virou colunas: Ordem, Situação, Pendência e Próxima passada (a fonte do déficit fica no painel do setor).
Revisão TABR (09/10/2026, A1): volta o critério de largura de antes das colunas novas: a 1440 px as grades IR cabem na caixa (sem rolar de
lado); a 1280 px a página não rola e situação/etapa, pendência e próximo passo ficam à vista sem rolar a grade.
Capturas em _probe/fluxo_*.png. Uso: python3 irr_fluxo_test.py"""
import sys, os, time, subprocess, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from cdp import Chrome
from journeys import free
R = os.path.join(HERE, '_render'); SH = os.path.join(HERE, '_probe'); os.makedirs(SH, exist_ok=True)
p = free(); srv = subprocess.Popen(['python3', '-m', 'http.server', str(p), '--bind', '127.0.0.1', '--directory', R], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)
c = None; OK = []; FAIL = []
def chk(nome, cond, info=''):
    (OK if cond else FAIL).append(nome); print(('OK   ' if cond else 'FALHA'), nome, ('' if cond else str(info)[:500]), flush=True)
U = lambda pg: f'http://127.0.0.1:{p}/{pg}'
try:
    c = Chrome(port=free()); J = c.js
    CLK = """((t,root)=>{const r=root?document.querySelector(root):document; if(!r) return 'SEM RAIZ'; const n=s=>(s||'').replace(/\\s+/g,' ').trim(); const els=[...r.querySelectorAll('button,a')]; const e=els.find(x=>n(x.innerText)===t)||els.find(x=>n(x.innerText).startsWith(t)); if(!e) return 'NÃO ACHEI: '+t; e.click(); return 'ok';})"""
    def clk(t, root=None): r = J(f"({CLK})({json.dumps(t)},{json.dumps(root)})"); time.sleep(.5); return r
    toast0 = lambda: J("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).filter(Boolean).join(' | ')") or ''
    def toast():
        for _ in range(10):
            t = toast0()
            if t: return t
            time.sleep(.25)
        return ''
    head = lambda: (J("document.querySelector('header').innerText.replace(/\\s+/g,' ')") or '')
    dlg = lambda: (J("(document.querySelector('aside[role=dialog]')||{innerText:''}).innerText.replace(/\\s+/g,' ')") or '')
    ROW = lambda txt: J(f"""(()=>{{const r=[...document.querySelectorAll('[role=row]')].find(r=>r.innerText.replace(/\\s+/g,' ').indexOf({json.dumps(txt)})>=0); return r?r.innerText.replace(/\\s+/g,' '):'—';}})()""")
    def goto(pg, w=1.6): c.goto(U(pg), wait=w); time.sleep(.4)
    def painel(txt, k):
        """campo do painel do setor no IR-01 (revisão TABR: fonte do déficit e responsável saíram da grade para o painel)"""
        J(f"""(()=>{{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.replace(/\\s+/g,' ').indexOf({json.dumps(txt)})===0); r&&(r.querySelector('[role=cell] span')||r).click();}})()"""); time.sleep(.5)
        v = J(f"(document.querySelector('#fx_g_set_{k}')||{{}}).value") or ''; clk('Cancelar', 'aside[role=dialog]'); return v
    erros = []
    def errs(nome): e = J("window.__err||''") or ''; (erros.append(nome + ': ' + e) if e else None)
    def setv(sel, val):
        return J(f"""(()=>{{const e=document.querySelector({json.dumps(sel)}); if(!e) return 'sem'; const d=Object.getOwnPropertyDescriptor(Object.getPrototypeOf(e),'value'); d.set.call(e,{json.dumps(val)}); e.dispatchEvent(new Event('input',{{bubbles:true}})); e.dispatchEvent(new Event('change',{{bubbles:true}})); return 'ok';}})()""")
    c.size(1440, 1000); goto('IR-01.dc.html', 1.0)
    J("localStorage.removeItem('talhao-os-irrigacao-v1'); localStorage.removeItem('talhao-os-cenario-v1'); sessionStorage.clear();")
    # 1 · conflito da OS-0423: link direto do Mapa (#OS-0423:conflito) abre o painel com opções calculadas
    goto('IR-03det.dc.html#OS-0423:conflito'); time.sleep(.6)
    d = dlg(); chk('1 IR-03det#OS-0423:conflito abre "Resolver conflito" com a parada da B3 e as opções 15:00–17:00 e 21:00–23:00',
                   'Resolver conflito · OS-0423' in d and 'parada da B3' in d and '15:00–17:00' in d and '21:00–23:00' in d, d[:400])
    c.shot(os.path.join(SH, 'fluxo_1_conflito.png'))
    clk('Aplicar janela', 'aside[role=dialog]'); t = toast()
    chk('2 aplicar a janela libera pela prontidão (LIB-2292), sem aprovação', 'LIB-2292' in t and 'Liberadas' in head() and 'Iniciar irrigação' in head(), [t, head()])
    goto('IR-03det.dc.html#OS-0423'); errs('IR-03det')
    chk('3 recarregar: a OS-0423 continua Liberadas (estado gravado) com janela 15:00–17:00', 'Liberadas' in head() and 'hoje 15:00–17:00' in (J("document.querySelector('main').innerText") or ''), head())
    goto('IR-03.dc.html'); errs('IR-03')
    chk('4 IR-03 lê o mesmo estado: OS-0423 Liberadas, sem conflito', 'Liberadas' in ROW('OS-0423') and 'Conflito' not in ROW('OS-0423'), ROW('OS-0423'))
    # 2 · Mapa (Santa Rita): o T7 deixa de estar em conflito
    J("sessionStorage.setItem('mapa-ctx','{\"mf_faz\":\"Santa Rita\"}')"); goto('IN-04.dc.html', 2.0); errs('IN-04')
    # MUX-F1 (17/10/2026): o talhão é um botão com data-talhao e o rótulo da camada em data-rotulo (o aria-label agora é o nome completo:
    # "T4, 204 ha, …"). Oráculo obsoleto na forma de achar; a asserção não muda
    lab = lambda t: J(f"(()=>{{const e=[...document.querySelectorAll('svg [role=button]')].find(x=>x.getAttribute('data-talhao')==='{t}'); return e?[e.getAttribute('data-talhao')+': '+e.getAttribute('data-rotulo'),e.getAttribute('fill')]:[null,null];}})()")
    l7 = lab('T7'); chk('5 Mapa Integrado: T7 sem "irrigação em conflito" (amarelo pela mancha do satélite)', l7[0] and 'conflito' not in l7[0] and l7[1] != '#C8553D', l7)
    J("[...document.querySelectorAll('nav[aria-label=\"Funcionalidades do mapa\"] button')].find(b=>(b.getAttribute('title')||'').startsWith('Mostrar Irrigação')).click()"); time.sleep(.6)
    chk('6 Mapa camada Irrigação: T7 "programada · hoje 15:00" e P2 "conferir medição · OS-0394"', 'programada · hoje 15:00' in (lab('T7')[0] or '') and 'conferir medição · OS-0394' in (lab('P2')[0] or ''), [lab('T7'), lab('P2')])
    c.shot(os.path.join(SH, 'fluxo_2_mapa_irrigacao.png'))
    # 3 · OS-0394: conferir a medição (hidrômetro prevalece)
    goto('IR-03det.dc.html#OS-0394:conferir'); time.sleep(.5)
    chk('7 IR-03det#OS-0394:conferir abre a conferência com 1.206 m³ medidos × 1.254 m³ estimados', 'Conferir medição · OS-0394' in dlg() and '1.206' in dlg(), dlg()[:300])
    setv('#cm_mot', 'Hidrômetro conferido em campo'); clk('Aceitar com motivo', 'aside[role=dialog]'); t = toast()
    chk('8 OS-0394 encerrada · hidrômetro prevalece, sem novo crédito (P2 segue 11,2 mm)', 'Encerradas' in head() and 'hidrômetro prevalece' in t and '11,2 mm' in t, [t, head()])
    # 4 · OS-0419: iniciar → término com a leitura da telemetria → conferência automática → crédito
    goto('IR-03det.dc.html#OS-0419'); clk('Iniciar irrigação'); t = toast()
    chk('9 OS-0419 Iniciar → Em execução (início hoje 20:02, EX-5120)', 'Em execução' in head() and '20:02' in t and 'EX-5120' in t, [t, head()])
    goto('IR-03det.dc.html#OS-0419')
    chk('10 recarregar: segue Em execução e o primário é Registrar término antecipado (Pausar só agora)', 'Em execução' in head() and 'Registrar término antecipado' in head() and J("[...document.querySelectorAll('main button')].some(b=>b.innerText.trim()==='Pausar')"), head())
    clk('Registrar término antecipado'); d = dlg()
    chk('11 término não inventa área/telemetria: campos vazios e motivo temporal necessário', J("document.querySelector('#tm_cob').value") == '' and J("document.querySelector('#tm_vol').value") == '' and 'Simulado' in d, d[:300])
    clk('Cancelar', 'aside[role=dialog]')
    # Fixture explícita de tempo decorrido; não é uma ação de produto nem prova de relógio real.
    J("(()=>{const k='talhao-os-irrigacao-v1'; const s=JSON.parse(localStorage.getItem(k)); const o=s.ordens['OS-0419']; const p=o.passadas.find(p=>p.st==='Em execução'); const pz=(o.exec.pausas||[]).filter(z=>z.n===p.n&&z.fim!==null&&z.fim!==undefined).reduce((a,z)=>a+z.fim-z.ini,0); o.trilha.push({q:p.iniReal+p.dur+pz,ev:'Fixture: tempo decorrido'}); localStorage.setItem(k,JSON.stringify(s)); return 1;})()")
    goto('IR-01.dc.html', 1.0)   # Recarrega de fato: mesma URL com # não recarrega a página
    goto('IR-03det.dc.html#OS-0419'); clk('Confirmar término')
    setv('#tm_cob', '80'); setv('#tm_vol', '8480')
    c.shot(os.path.join(SH, 'fluxo_3_termino.png'))
    clk('Confirmar término', 'aside[role=dialog]'); t = toast()
    chk('12 leitura explícita no tempo decorrido → conferência automática (−1,9 %) → Encerradas; P2 agora 1,7 mm', 'Encerradas' in head() and '−1,9 %' in t and 'agora 1,7 mm' in t, [t, head()])
    trl = J("[...document.querySelectorAll('[role=table]')].pop().innerText.replace(/\\s+/g,' ')") or ''
    chk('13 trilha com início, término (amanhã 10:33) e conferência automática', 'Início' in trl and 'amanhã 10:33' in trl and 'Conferência automática' in trl, trl[-400:])
    goto('IR-01.dc.html'); errs('IR-01')
    r2 = ROW('Pivô 2'); chk('14 IR-01: Pivô 2 com 1,7 mm e próximo passo da OS-0422 (Definir janela)', '1,7 mm' in r2 and 'OS-0422' in r2 and 'A programar' in r2 and 'Definir janela' in r2, r2)
    J("(()=>{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.indexOf('Pivô 2')>=0); (r.querySelector('[role=cell] span')||r).click();})()"); time.sleep(.5)
    d = dlg(); chk('15 painel do setor: aplicação da OS-0419 creditada uma vez (8.480 m³ = 10,6 mm × 90 % = 9,54 mm líquidos)', d.count('OS-0419 · volta completa') == 1 and '9,54 mm líquidos' in d, d[:600])
    c.shot(os.path.join(SH, 'fluxo_4_ir01_p2.png'))
    goto('IN-04.dc.html', 2.0)
    J("[...document.querySelectorAll('nav[aria-label=\"Funcionalidades do mapa\"] button')].find(b=>(b.getAttribute('title')||'').startsWith('Mostrar Irrigação')).click()"); time.sleep(.5)
    J("[...document.querySelectorAll('button')].find(b=>b.innerText.trim()==='Balanço hídrico').click()"); time.sleep(.5)
    lp = lab('P2'); chk('16 Mapa (Balanço hídrico): P2 com déficit 1,7 mm (verde)', 'déficit 1,7 mm' in (lp[0] or '') and lp[1] not in ('#D4B25A', '#C8553D', '#D98A4E'), lp)
    # 5 · Lagoa Grande: tarefa única recuperada a partir do Mapa (#programar=PV02)
    goto('IR-02.dc.html#programar=PV02'); time.sleep(.6); errs('IR-02')
    d = dlg(); fz = J("document.querySelector('select[aria-label=\"Filtrar por fazenda\"]').value")
    chk('17 IR-02#programar=PV02: fazenda Lagoa Grande e "Tarefa única OS-0601 já existe" (Abrir OS-0601, sem Programar)', fz == 'Lagoa Grande' and 'Tarefa única OS-0601 já existe' in d and 'Abrir OS-0601' in d
        and not J("[...document.querySelectorAll('aside[role=dialog] button')].some(b=>b.innerText.trim()==='Programar')"), [fz, d[:400]])
    c.shot(os.path.join(SH, 'fluxo_5_lg_programar.png'))
    n = J("Object.values(JSON.parse(localStorage.getItem('talhao-os-irrigacao-v1')).ordens).filter(o=>o.setor==='PV02').length")
    chk('18 PV02 continua com uma só ordem', n == 1, n)
    goto('IR-01.dc.html')
    nlg = J("[...document.querySelectorAll('[role=row].g2ed')].length"); r = ROW('Pivô 2 ')
    f2 = painel('Pivô 2 ', 'defT')
    chk('19 IR-01 na Lagoa Grande: 23 pivôs; Pivô 2 programado (OS-0601 hoje 21:00), balanço demonstrativo (no painel do setor)', nlg == 23 and 'OS-0601' in r and 'Programada' in r and 'hoje 21:00' in r and 'demonstrativo' in f2, [nlg, r, f2])
    # 7 · correções da verificação v43 (03/10): estado limpo
    def esc():
        for ty in ('keyDown', 'keyUp'): c.call('Input.dispatchKeyEvent', {'type': ty, 'key': 'Escape', 'code': 'Escape', 'windowsVirtualKeyCode': 27})
        time.sleep(.4)
    def mclick(txt):
        r = J(f"""(()=>{{const n=s=>(s||'').replace(/\\s+/g,' ').trim(); const e=[...document.querySelectorAll('button,a')].filter(x=>x.getClientRects().length).find(x=>n(x.innerText)==={json.dumps(txt)}); if(!e) return null; const b=e.getBoundingClientRect(); return [b.x+b.width/2,b.y+b.height/2];}})()""")
        if r:
            for ty in ('mousePressed', 'mouseReleased'): c.call('Input.dispatchMouseEvent', {'type': ty, 'x': r[0], 'y': r[1], 'button': 'left', 'clickCount': 1})
        time.sleep(.6); return r
    J("localStorage.removeItem('talhao-os-irrigacao-v1'); localStorage.removeItem('talhao-os-cenario-v1'); sessionStorage.clear();")
    J("sessionStorage.setItem('irr-faz','Santa Rita')"); goto('IR-01.dc.html')
    pr = J("[...document.querySelectorAll('header a')].map(a=>[a.innerText.trim(),a.getAttribute('href')]).filter(x=>x[0]).pop()")
    chk('22 IR-01 Santa Rita: o primário é o passo mais urgente (Resolver conflito · OS-0423 → IR-03det#OS-0423:conflito)', pr == ['Resolver conflito · OS-0423', 'IR-03det.dc.html#OS-0423:conflito'], pr)
    goto('IR-03det.dc.html#OS-0422'); mclick('Definir janela')
    ae = J("(()=>{const a=document.activeElement; return [a?a.id:'',!!(a&&a.closest('aside[role=dialog]')),(document.querySelector('aside[role=dialog]')||{getAttribute:()=>''}).getAttribute('aria-modal')];})()"); esc()
    chk('23 painel Definir janela: foco entra no painel, aria-modal e Esc fecha (foco volta à tela)', ae == ['jn_d1', True, 'true'] and not dlg(), ae)
    goto('IR-03det.dc.html#OS-0392:janela'); time.sleep(.3)
    chk('24 link direto inválido (OS-0392 Encerradas:janela) não abre o painel e explica o motivo', not dlg() and 'não vale' in toast() and J("location.hash") == '#OS-0392', [dlg()[:80], toast()])
    goto('IR-03det.dc.html#OS-0423'); clk('Adicionar produtos'); setv('#rc_prod', 'Nitrato de cálcio'); setv('#rc_dose', '5'); setv('#rc_mot', 'Ca'); time.sleep(.3)
    d = dlg(); clk('Criar versão v2', 'aside[role=dialog]'); tt = toast()
    chk('25 Adicionar produtos na OS-0423 (conflito com a parada da B3) é recusado: a v2 não fura o bloqueio', 'Resolva antes' in d and 'Resolva antes' in tt and J("(()=>{ const c=JSON.parse(localStorage.getItem('talhao-os-cenario-v1')||'null'); return !!(c&&c.ordens&&c.ordens['OS-0423']); })()") is False, [d[-200:], tt])
    clk('Cancelar', 'aside[role=dialog]'); clk('Descartar alterações', 'aside[role=dialog]')
    goto('IR-03det.dc.html#OS-0423:conflito'); clk('Aplicar janela', 'aside[role=dialog]')
    goto('IN-03.dc.html', 1.8); r23 = ROW('OS-0423')
    chk('26 Agenda (IN-03) lê o estado: OS-0423 resolvida vira Iniciar irrigação · João, prioridade Normal, sem selo de conflito', 'Iniciar irrigação · OS-0423' in r23 and 'João' in r23 and 'Normal' in r23 and 'Conflito' not in r23, r23)
    # fertirrigação OS-0418 parada por falta de insumo: mesma situação da O.S. e água sem o produto
    goto('IR-01.dc.html'); r1 = ROW('Pivô 1')
    d1 = painel('Pivô 1', 'donoT')
    chk('27 IR-01 Pivô 1: falta insumo · OS-0418 (como na O.S.) e próximo passo Programar só água · João (responsável no painel do setor)', 'OS-0418' in r1 and 'Impedida Falta insumo' in r1 and 'Programar só água' in r1 and d1 == 'João', [r1, d1])
    goto('IR-02.dc.html#programar=P1'); time.sleep(.5); clk('Programar só água', 'aside[role=dialog]'); tt = toast()
    chk('28 IR-02#programar=P1: Programar só água cria e libera a ordem de água; OS-0418 segue parada', 'criada' in tt and 'Liberadas' in tt and 'OS-0418 segue parada' in tt, tt)
    # v2 durante a execução, liberada na O.S.: a irrigação segue a O.S. (sem beco sem saída)
    goto('IR-03det.dc.html#OS-0419'); clk('Iniciar irrigação'); clk('Registrar avanço'); setv('#av_cob', '30'); clk('Salvar avanço', 'aside[role=dialog]')
    clk('Adicionar produtos'); setv('#rc_prod', 'Nitrato de potássio'); setv('#rc_dose', '7'); setv('#rc_mot', 'K'); time.sleep(.3); clk('Criar versão v2', 'aside[role=dialog]')
    h1 = head(); goto('OS.dc.html#OS-0419', 2.0); clk('Liberar para execução', 'aside[role=dialog]'); time.sleep(.4); clk('Confirmar liberação', 'aside[role=dialog]'); time.sleep(.8)
    goto('IR-03det.dc.html#OS-0419'); h2 = head(); m = J("document.querySelector('main').innerText.replace(/\\s+/g,' ')") or ''
    chk('29 v2 em execução: Revisão de saldo pendente; depois da liberação na O.S. a ordem segue a etapa da O.S. (Liberadas · Iniciar execução na O.S.) e a v1 fica creditada só na faixa de 30 ha',
        'Revisão de saldo pendente' in h1 and 'Liberadas' in h2 and 'Iniciar execução na O.S.' in h2 and 'na faixa de 30,0 ha' in m, [h1[-120:], h2[-120:]])
    # Restaurar demonstração no Estoque leva a irrigação junto
    goto('EST.dc.html', 1.8); clk('Restaurar demonstração'); J("(()=>{const b=[...document.querySelectorAll('button')].filter(b=>/Restaurar/.test(b.innerText)&&b.getClientRects().length); if(b.length) b[b.length-1].click();})()"); time.sleep(.8)
    goto('IR-03det.dc.html#OS-0419'); h3 = head()
    chk('30 Restaurar demonstração (Estoque) volta a irrigação à semente: OS-0419 Liberadas sem v2 órfã', 'Liberadas' in h3 and 'Iniciar irrigação' in h3 and 'v2' not in h3, h3[-140:])
    # passagem parcial: crédito só na faixa coberta
    clk('Iniciar irrigação'); goto('IR-03det.dc.html#OS-0419:termino'); time.sleep(.3)
    setv('#tm_cob', '40'); setv('#tm_vol', '3800'); setv('#tm_mot', 'Tempo do sensor a conferir'); clk('Registrar término antecipado', 'aside[role=dialog]')
    chk('31a área sem tempo compatível permanece Em conferência e não credita antes da validação', 'Em conferência' in head() and J("JSON.parse(localStorage.getItem('talhao-os-irrigacao-v1')).setores.P2.bal.ap.some(a=>a.os==='OS-0419')") is False, head())
    goto('IR-03det.dc.html#OS-0419:conferir'); time.sleep(.3); setv('#cm_vol', '3800'); setv('#cm_mot', 'Área e leitura verificadas; horário do sensor incorreto'); clk('Aceitar com motivo', 'aside[role=dialog]'); tt = toast()
    goto('IR-01.dc.html'); r2 = ROW('Pivô 2')
    chk('31 parada em 40 de 80 ha (3.800 m³): o Pivô 2 segue 11,2 mm e a faixa coberta (40 ha) é mostrada à parte', 'faixa de 40,0 ha' in tt and '11,2 mm' in r2, [tt, r2])
    # contexto: fazenda do Mapa ↔ Irrigação
    goto('IR-01.dc.html'); setv('select[aria-label="Filtrar por fazenda"]', 'Lagoa Grande'); time.sleep(.4); setv('select[aria-label="Filtrar por fazenda"]', 'Santa Rita'); time.sleep(.4)
    # 13/10/2026: o filtro de fazenda do Mapa saiu do topo e fica na faixa "Filtros desta tela" (.mf-tela)
    goto('IN-04.dc.html', 2.4); mf = J("(document.querySelector('.mf-tela select')||{}).value")
    setv('.mf-tela select', 'Lagoa Grande'); time.sleep(1.2); goto('IR-01.dc.html'); irf = J("document.querySelector('select[aria-label=\"Filtrar por fazenda\"]').value")
    chk('32 fazenda acompanha: escolhida na Irrigação abre o Mapa nela; trocada no Mapa, a Irrigação abre na do Mapa', mf == 'Santa Rita' and irf == 'Lagoa Grande', [mf, irf])
    # filtro rápido preservado ao voltar
    J("sessionStorage.setItem('irr-faz','Santa Rita')"); goto('IR-03.dc.html'); clk('A liberar'); n1 = J("document.querySelectorAll('[role=row].g2ed').length")
    goto('IR-03det.dc.html#OS-0422'); J("[...document.querySelectorAll('header a')].find(a=>!a.innerText.trim()).click()"); time.sleep(1.8)
    n2 = J("document.querySelectorAll('[role=row].g2ed').length")
    chk('33 IR-03: filtro rápido (A liberar) continua ao voltar do registro', n1 == n2 and (J("location.pathname") or '').endswith('IR-03.dc.html'), [n1, n2])
    errs('jornada v43')
    # 6 · largura (revisão TABR A1): a 1440 px nenhuma grade IR rola de lado; a 1280 px a página não rola e o estado, a pendência e o próximo passo
    # ficam à vista sem rolar a grade (antes das colunas novas, nenhuma grade rolava a 1280; com uma variável por coluna, o resto pode rolar)
    larg = []
    for w in (1280, 1440):
        c.size(w, 1000)
        for pg in ('IR-01.dc.html', 'IR-02.dc.html', 'IR-03.dc.html', 'IR-04.dc.html'):
            goto(pg, 1.2); o = J("""[document.documentElement.scrollWidth-innerWidth].concat([...document.querySelectorAll('.g2rola')].filter(e=>e.offsetParent).map(e=>{ const R=e.getBoundingClientRect();
              const hs=[...e.querySelectorAll('[role=table]>[role=row] [role=columnheader]')]; const fora=hs.filter(h=>['Situação','Etapa','Estado','Pendência','Próximo passo'].indexOf(h.textContent.replace(/[⇅▾▴▼▲]/g,'').trim())>=0&&h.getBoundingClientRect().right>R.right+1).length;
              return fora?99:(%s?e.scrollWidth-e.clientWidth:0); }))""" % ('true' if w == 1440 else 'false')) or []
            if any(x > 1 for x in o): larg.append((w, pg, o))
            if w == 1280: c.shot(os.path.join(SH, 'fluxo_6_' + pg.replace('.dc.html', '') + '_1280.png'))
    chk('20 sem rolagem lateral nas grades IR a 1440 px; a 1280 px a página não rola e estado, pendência e próximo passo ficam à vista (Lagoa Grande, 23 pivôs)', not larg, larg)
    chk('21 nenhuma tela com erro de execução', not erros, erros)
finally:
    try:
        if c: c.close()
    finally: srv.terminate()
print(f'\n{len(OK)} ok · {len(FAIL)} falhas', FAIL)

