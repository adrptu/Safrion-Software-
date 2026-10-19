# -*- coding: utf-8 -*-
"""Teste CDP do módulo Irrigação por tela (02/10/2026): faixa de etapas com contadores do estado, IR-01 (memória do balanço com irrigação
líquida, limites valem para as próximas), IR-02 (agenda por captação, sem coluna de ação; Programar irrigação cria ou recupera a tarefa
única), IR-03det (janela por passada com checagens ao vivo, pausa só em execução, Adicionar produtos → v2 no cenário da O.S.) e IR-04
(marcar leitura suspeita muda o setor para estimativa em todas as telas; sensor novo aguarda a 1ª leitura). O estado é o mesmo do Mapa
(localStorage 'talhao-os-irrigacao-v1'). A jornada ponta a ponta está em irr_fluxo_test.py. Uso: python3 irtest.py"""
import sys, os, time, subprocess, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from cdp import Chrome
from journeys import free
R = os.path.join(HERE, '_render'); p = free()
srv = subprocess.Popen(['python3', '-m', 'http.server', str(p), '--bind', '127.0.0.1', '--directory', R], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)
c = Chrome(port=free()); J = c.js
CLK = """((t,root)=>{const r=root?document.querySelector(root):document; const n=s=>(s||'').replace(/\\s+/g,' ').trim(); const els=[...r.querySelectorAll('button,a')]; const e=els.find(x=>n(x.innerText)===t)||els.find(x=>n(x.innerText).startsWith(t)); if(!e) return 'NÃO ACHEI: '+t; e.click(); return 'ok';})"""
SETV = """((sel,val)=>{const i=document.querySelector(sel); const P=i.tagName==='SELECT'?HTMLSelectElement.prototype:(i.tagName==='TEXTAREA'?HTMLTextAreaElement.prototype:HTMLInputElement.prototype); Object.getOwnPropertyDescriptor(P,'value').set.call(i,val); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true}));})"""
T0 = lambda: J("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).filter(Boolean).join(' | ')") or ''
def T():   # aviso da ação: espera o desenho (máquina carregada)
    for _ in range(10):
        t = T0()
        if t: return t
        time.sleep(.25)
    return ''
ROW = lambda txt: J(f"""(()=>{{const r=[...document.querySelectorAll('[role=row]')].find(r=>r.innerText.replace(/\\s+/g,' ').indexOf({json.dumps(txt)})>=0); return r?r.innerText.replace(/\\s+/g,' '):'—';}})()""")
HDR = lambda: J("document.querySelector('header').innerText.replace(/\\s+/g,' ')") or ''
DLG = lambda: J("(document.querySelector('aside[role=dialog]')||{innerText:''}).innerText.replace(/\\s+/g,' ')") or ''
def clk(t, root=None): r = J(f"({CLK})({json.dumps(t)},{json.dumps(root)})"); time.sleep(.45); return r
def sv(sel, val): J(f"({SETV})({json.dumps(sel)},{json.dumps(val)})"); time.sleep(.3)
def rowopen(txt):
    J(f"""(()=>{{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.replace(/\\s+/g,' ').indexOf({json.dumps(txt)})>=0); (r.querySelector('[role=cell] span')||r).click();}})()"""); time.sleep(.45)
def painel(txt, ks):
    """valores dos campos do painel do setor (IR-01): o que saiu da grade na revisão TABR (fonte do déficit, passadas, cobertura e resta)"""
    rowopen(txt); out = [J(f"(document.querySelector('#fx_g_set_{k}')||{{}}).value") or '' for k in ks]; clk('Cancelar', 'aside[role=dialog]'); return out
def goto(pg, w=1.4): c.goto(f'http://127.0.0.1:{p}/{pg}', wait=w); time.sleep(.3)
ok = []
def chk(nome, cond, info=''): ok.append((nome, bool(cond))); print(('✓ ' if cond else '✗ ') + nome + ('' if cond else '  ' + str(info)[:400]), flush=True)
try:
    c.size(1440, 1000); goto('IR-01.dc.html', 1.0)
    J("localStorage.removeItem('talhao-os-irrigacao-v1'); localStorage.removeItem('talhao-os-cenario-v1'); sessionStorage.clear();")
    # ---------- faixa de etapas (contadores do estado) ----------
    for t, cur in [('IR-01', 1), ('IR-03det', 3), ('IR-04', 4)]:
        goto(f'{t}.dc.html')
        nav = J("[...document.querySelectorAll('nav[aria-label=\"Telas da irrigação\"] a')].filter(a=>!a.getAttribute('aria-label')).map(a=>a.getAttribute('href')+'|'+(a.getAttribute('aria-current')||'')+'|'+a.innerText.replace(/\\s+/g,' '))")
        chk(f'{t}: telas da irrigação (4, sem setas), atual = {cur}, pendências do estado', len(nav) == 4 and nav[cur - 1].split('|')[1] == 'page' and [x.split('|')[0] for x in nav] == ['IR-01.dc.html', 'IR-02.dc.html', 'IR-03.dc.html', 'IR-04.dc.html']
            and '1 conflito · 1 janela a definir' in nav[1] and '1 a conferir' in nav[2] and '1 suspeita · 1 sem dado' in nav[3], nav)
    # ---------- IR-01 ----------
    goto('IR-01.dc.html'); b = J("document.body.innerText")
    chk('IR-01: título igual ao menu, sem seções explicativas nem rodapé de regra', J("document.querySelector('h1').innerText.trim()") == 'Irrigação' and 'Passagem parcial do pivô' not in b and 'Água sem produto não passa' not in b)
    # TABELAS-FOCO (06/10/2026): uma variável por coluna; cobertura é coluna numérica ("38 %"). Revisão TABR (09/10/2026, A1): a fonte do
    # déficit, o que resta e as passadas necessárias ficam no painel do setor (antes "12,44 mm brutos em 3 passadas" numa célula)
    f1, f2 = painel('Pivô 1', ['defT'])[0], painel('Pivô 2', ['defT'])[0]
    chk('IR-01: P2 11,2 mm medido · P1 ≈8,4 mm e T7 ≈10,0 mm por estimativa de ET', '11,2 mm' in ROW('Pivô 2') and 'sonda' in f2 and 'estimativa' not in f2 and '≈8,4 mm' in ROW('Pivô 1') and 'estimativa por ET' in f1 and '≈10,0 mm' in ROW('Gotejo T7'), [f1, f2])
    o7 = painel('Gotejo T7', ['ordT'])[0]
    chk('IR-01: T7 cobre 38 % e resta 6,2 mm; primeiro da lista é o impedido (Resolver conflito)', '38 %' in ROW('Gotejo T7') and o7 == 'OS-0423 · cobre 38 % · resta 6,2 mm' and J("[...document.querySelectorAll('[role=row].g2ed')][0].innerText").startswith('Gotejo T7') and 'Resolver conflito' in ROW('Gotejo T7'))
    rowopen('Pivô 2'); d = DLG()
    chk('IR-01: painel do setor com a memória (irrigação líquida) e a passagem parcial só na área coberta',
        '5,0 + ETc 7 dias 35,1 − chuva efetiva 12,0 − irrigação líquida 16,9 = 11,2 mm' in d and 'faixa de 11,6 ha (OS-0394): 1,8 mm · resto do pivô: 11,2 mm' in d
        and '1.206 m³ em 11,6 ha = 10,4 mm brutos na faixa × 90 % = 9,36 mm líquidos · fora do déficit do pivô · provisório' in d, d[d.find('Passagem parcial'):][:700])
    sv('#fx_g_set_lmax', '4,5'); clk('Salvar', 'aside[role=dialog]'); t = T()
    n2 = painel('Pivô 2', ['necT'])[0]
    chk('IR-01: limite de 4,5 mm vale para a próxima programação; OS-0419 liberada não muda', 'até 4,5 mm por passada' in t and 'OS-0419 não muda' in t and '12,44 mm OS-0419' in ROW('Pivô 2') and '3 passadas necessárias' in n2, [t, ROW('Pivô 2'), n2])
    # ---------- IR-02 ----------
    goto('IR-02.dc.html'); hd = J("[...document.querySelectorAll('[role=columnheader]')].map(h=>h.innerText.replace(/\\s+/g,' ').trim())")
    chk('IR-02: cabeçalho "1 conflito · 1 janela a definir"; agenda por captação, sem coluna Ação', '1 conflito · 1 janela a definir' in HDR() and not any(h.startswith('AÇÃO') or h.startswith('Ação') for h in hd) and 'Rio · captação da sede' in J("document.body.innerText"), [HDR(), hd])
    J(f"({SETV})('select[aria-label=\"Filtrar por fazenda\"]','Lagoa Grande')"); time.sleep(.5)
    clk('Programar irrigação'); sv('#pg_sel', 'PV01'); d = J("[...document.querySelectorAll('aside[role=dialog] > div, aside[role=dialog] [role=list]')].map(e=>e.innerText).join(' ')").replace('\n', ' ')
    dl = d.lower()   # innerText traz o text-transform dos rótulos: comparar sem caixa
    chk('IR-02: painel Programar irrigação com necessidade, passadas e janela sugerida (PV01, Lagoa Grande)', 'pivô 1' in dl and 'janela sugerida' in dl and 'pronta' in dl and 'vence em 20/11/2026' not in dl and 'em renovação' not in dl, d[-500:])   # CTL-5 (revisão S3-2): a janela de hoje não passa do vencimento da SINT-002/0000 (20/11/2026): sem aviso de outorga
    clk('Programar', 'aside[role=dialog]'); t = T()
    chk('IR-02: nova tarefa OS-0607 liberada automaticamente (água sem produto)', 'OS-0607' in t and 'Liberadas' in t and 'Liberadas' in ROW('OS-0607'), t)
    clk('Programar irrigação'); sv('#pg_sel', 'PV01'); d = J("[...document.querySelectorAll('aside[role=dialog] [role=status]')].map(e=>e.innerText).join(' ')") or ''
    chk('IR-02: programar de novo recupera a tarefa única (sem duplicar)', 'Tarefa única OS-0607 já existe' in d and J("[...document.querySelectorAll('[role=row]')].filter(r=>r.innerText.indexOf('OS-0607')>=0).length") == 1, d[:300])
    clk('Cancelar', 'aside[role=dialog]')
    # ---------- IR-03det: janela por passada ----------
    goto('IR-03det.dc.html#OS-0422:janela'); time.sleep(.4)
    d = DLG(); v1 = [J("document.querySelector('#jn_d1').value"), J("document.querySelector('#jn_h1').value"), J("document.querySelector('#jn_d2').value"), J("document.querySelector('#jn_h2').value")]
    chk('IR-03det: Definir janela da OS-0422 com 2 passadas preenchidas pela sugestão (24/09 e 25/09 às 21:00) e "Pronta"', v1 == ['2026-09-24', '21:00', '2026-09-25', '21:00'] and 'Pronta' in d, [v1, d[:300]])
    sv('#jn_d2', '2026-09-24'); d = DLG()
    chk('IR-03det: passadas fora de ordem ou sobrepostas aparecem na hora, antes de salvar', 'Corrija · A passada 2 começa antes do fim da passada 1' in d, d[:400])
    clk('Usar janela sugerida', 'aside[role=dialog]'); clk('Salvar janela', 'aside[role=dialog]'); time.sleep(.5)
    m = J("document.querySelector('main').innerText.replace(/\\s+/g,' ')") or ''   # efeito gravado (o aviso some em 4,5 s)
    chk('IR-03det: janela salva libera a OS-0422 (LIB-2291 automática, 2 passadas amanhã e 25/09 às 21:00)', 'LIB-2291 · automática pela prontidão' in m and 'amanhã 21:00–25/09 06:02' in m
        and '25/09 21:00–26/09 06:02' in m and 'Liberadas' in HDR(), [HDR(), m[:400]])
    # ---------- IR-03det: execução com pausa ----------
    goto('IR-03det.dc.html#OS-0419')
    chk('IR-03det: Liberadas sem botão Pausar (só vale em execução)', not J("[...document.querySelectorAll('main button')].some(b=>b.innerText.trim()==='Pausar')") and 'Iniciar irrigação' in HDR())
    clk('Iniciar irrigação'); clk('Pausar')
    chk('IR-03det: pausa vira selo e o primário vira Retomar irrigação (etapa preservada)', 'Em execução · Pausada' in HDR() and 'Retomar irrigação' in HDR(), HDR())
    clk('Retomar irrigação')
    chk('IR-03det: retomada volta a Confirmar término', 'Confirmar término' in HDR() and 'Pausada' not in HDR(), HDR())
    # ---------- IR-03det: Adicionar produtos em execução (v2 com o agrônomo na O.S.) ----------
    clk('Adicionar produtos'); sv('#rc_dose', ''); clk('Criar versão v2', 'aside[role=dialog]')
    chk('IR-03det: Adicionar produtos valida dose e motivo junto ao campo', 'maior que zero' in DLG() and 'motivo' in DLG())
    clk('Cancelar', 'aside[role=dialog]'); clk('Descartar alterações', 'aside[role=dialog]')
    clk('Registrar avanço'); sv('#av_cob', '30'); clk('Salvar avanço', 'aside[role=dialog]')
    clk('Adicionar produtos'); sv('#rc_prod', 'Nitrato de potássio'); sv('#rc_dose', '7'); sv('#rc_mot', 'Deficiência de K'); clk('Criar versão v2', 'aside[role=dialog]'); t = T()
    chk('IR-03det: v2 em execução → selo Revisão de saldo pendente, passada 1 parada em 30 ha (v1) e primário Liberar saldo na O.S.', 'Revisão de saldo pendente · v2' in HDR() and 'Liberar saldo na O.S.' in HDR()
        and J("(document.querySelector('header a[href=\"OS.dc.html#OS-0419\"]')||{}).innerText||''").startswith('Liberar saldo') and 'Parcial · v1' in (J("document.querySelector('main').innerText") or ''), [t, HDR()])
    chk('IR-03det: a v2 entra no cenário da O.S. (A liberar, Nitrato de potássio, 50 ha × 7 = 350 kg)', J("(c=>c&&c.ordens['OS-0419']?[c.ordens['OS-0419'].etapa,c.ordens['OS-0419'].ins[0].p,c.ordens['OS-0419'].ins[0].tot]:null)(JSON.parse(localStorage.getItem('talhao-os-cenario-v1')))") == ['A liberar', 'Nitrato de potássio', 350])
    # ---------- IR-04 ----------
    goto('IR-04.dc.html'); J(f"({SETV})('select[aria-label=\"Filtrar por fazenda\"]','Santa Rita')"); time.sleep(.5)
    chk('IR-04: sem elo para GE-07 (oculta e fixa · CTL-1, Frente F)', not J("[...document.querySelectorAll('a[href]')].some(a=>a.getAttribute('href').startsWith('GE-07'))"), J("[...document.querySelectorAll('a[href]')].map(a=>a.getAttribute('href'))"))
    rowopen('Sonda de umidade · P2'); clk('Marcar leitura suspeita', 'aside[role=dialog]'); t = T()
    chk('IR-04: marcar leitura suspeita tira a sonda do balanço e o P2 passa a estimativa', 'suspeita' in t and 'Suspeita' in ROW('Sonda de umidade · P2') and 'Pivô 2 por estimativa de ET' in ROW('Sonda de umidade · P2'), [t, ROW('Sonda de umidade · P2')])
    clk('+ Cadastrar sensor'); sv('#fx_g_src_nome', 'Sonda de umidade · P2 (40 cm)'); sv('#fx_g_src_cal', '2027-03-31'); clk('Salvar', 'aside[role=dialog]'); time.sleep(.3)
    chk('IR-04: sensor novo aguarda a 1ª leitura e nada entra no balanço sem origem', 'Aguardando 1ª leitura' in ROW('P2 (40 cm)') and 'primeira leitura' in T(), ROW('P2 (40 cm)'))
    goto('IR-01.dc.html')
    f2 = painel('Pivô 2', ['defT'])[0]
    chk('IR-01: o mesmo estado — P2 agora com ≈ e estimativa por ET (no painel do setor)', '≈' in ROW('Pivô 2') and 'estimativa por ET' in f2, [ROW('Pivô 2'), f2])
    goto('IR-01.dc.html#PV02', 1.8); time.sleep(.6); d = DLG()
    chk('IR-01#PV02 (link do Mapa): troca para a Lagoa Grande e abre o setor com a memória demonstrativa', J("document.querySelector('select[aria-label=\"Filtrar por fazenda\"]').value") == 'Lagoa Grande'
        and 'Setor · Pivô 2' in d and 'Memória (demonstrativa)' in d, d[:300])
    print('erros JS:', J("window.__err||'nenhum'"))
finally:
    c.close(); srv.terminate()
print(f"\n{sum(1 for _,o in ok if o)} de {len(ok)} verificações OK")
