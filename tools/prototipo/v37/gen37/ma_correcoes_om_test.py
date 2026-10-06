# -*- coding: utf-8 -*-
"""Teste CDP das correções do passo 4 nas ordens e leituras (MA-01..MA-05):
leitura implausível na conclusão vira aviso a confirmar · quantidade aplicada gera sobra e entra no custo ·
abastecimento com leitura alta ou menor: Confirmar / Descartar (troca de contador ajusta o histórico) · contador do MA-01 = última leitura ·
achado do MA-02 vinculado persiste e aparece na OM · falta de peça: Solicitar compra → Registrar recebimento → Liberar ·
F5 reabre a OM · Tab preso e Esc fora do painel da OM · nenhuma coluna cortada a 1.280 × 800.
Uso: python3 ma_correcoes_om_test.py   (lê _render; zera o cenário da manutenção em cada bloco)"""
import sys, os, time, json
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from cadc_lib import T, SETV

t=T(); J=t.J; FALHAS=[]
def ok(cond,msg):
    print(('  ok  ' if cond else '  FALHA ')+msg)
    if not cond: FALHAS.append(msg)
def toast(): return J("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).filter(Boolean).join(' | ')") or ''
def clk(txt,root=''):
    r=J(f"""(()=>{{const n=s=>(s||'').replace(/\\s+/g,' ').trim(); const els=[...document.querySelectorAll('{root} button, {root} a')].filter(e=>e.getClientRects().length); const e=els.find(x=>n(x.innerText)==={json.dumps(txt)})||els.find(x=>n(x.innerText).startsWith({json.dumps(txt)})); if(!e) return 'NAO ACHEI'; e.click(); return 'ok';}})()""")
    time.sleep(.4); return r
def setv(sel,val): r=J(f"({SETV})({json.dumps(sel)},{json.dumps(val)})"); time.sleep(.2); return r
def pan(): return J("(document.querySelector('aside[role=dialog]')||{}).innerText||''") or ''
def feitas():   # CTL-3 (R-D4): sem ação em massa; cada tarefa sem resposta recebe "Feito", uma a uma (PRD 54.2), com quem e hora
    n=0
    for _ in range(30):
        r=J("(()=>{const g=[...document.querySelectorAll('aside [role=group]')].find(g=>{const bs=[...g.querySelectorAll('button')]; return bs.some(b=>b.innerText.trim()==='Feito')&&!bs.some(b=>b.getAttribute('aria-pressed')==='true');}); if(!g) return false; [...g.querySelectorAll('button')].find(b=>b.innerText.trim()==='Feito').click(); return true;})()"); time.sleep(.3)
        if not r: break
        n+=1
    return n
def key(k,code,vk):
    t.c.call('Input.dispatchKeyEvent',{'type':'keyDown','key':k,'code':code,'windowsVirtualKeyCode':vk}); t.c.call('Input.dispatchKeyEvent',{'type':'keyUp','key':k,'code':code,'windowsVirtualKeyCode':vk}); time.sleep(.05)
def novo(): J("localStorage.clear()")
def ir(f):
    """navegação rápida: espera o documento novo (marca some) e o corpo renderizado; hash na mesma página volta em até 3 s"""
    J("window.__velho=1"); t.c.call('Page.navigate',{'url':f'http://127.0.0.1:{t.p}/{f}'})
    for _ in range(30):
        time.sleep(.1)
        try:
            if J("!window.__velho && document.readyState==='complete' && document.body && document.body.innerText.length>50"): break
        except Exception: pass
    time.sleep(.45)
t.goto=ir
def sem_erro(tela): e=t.errs(); ok(not e, f'{tela}: sem erro de JS {e[:160]}')
def abast(ativo,cont):
    clk('Registrar abastecimento'); setv('aside[role=dialog] select[id$=_ativo]',ativo); setv('aside[role=dialog] select[id$=_tq]','Sede · D-118')
    setv('aside[role=dialog] input[id$=_vol]','150'); setv('aside[role=dialog] input[id$=_cont]',cont); setv('aside[role=dialog] select[id$=_op]','Beto'); setv('aside[role=dialog] input[id$=_evid]','foto')
    clk('Salvar','aside'); return toast()
def linha(ti,txt): return t.anyrow(ti,txt) or ''
try:
    t.goto('MA-04.dc.html'); novo()
    # 1 · leitura absurda na conclusão: aviso a confirmar; corrigir e concluir com aplicado menor que o planejado (sobra entra no recibo e no custo)
    t.goto('MA-04.dc.html#OM-0234'); time.sleep(.4); sem_erro('MA-04')
    clk('Liberar serviço','aside'); clk('Liberar mesmo assim','aside'); clk('Iniciar serviço','aside'); feitas(); ok('por Ana (gestora) às' in pan(),'CTL-3 (R-D4): cada tarefa respondida mostra quem e a hora')
    setv('#om-leitura','29.950'); clk('Concluir serviço','aside'); p=pan(); fase=J("__man.manGet().oms['OM-0234'].etapa")
    ok('Concluir com esta leitura' in p and 'acima da última' in p and fase=='Em execução', f'leitura 29.950 h: aviso a confirmar, ordem segue Em execução · {fase}')
    clk('Corrigir leitura','aside'); foco=J("document.activeElement&&document.activeElement.id")
    setv('#om-leitura','2.995'); setv('aside input[aria-label^="Aplicado · Óleo de motor"]','12'); clk('Concluir serviço','aside'); c=toast()
    ok(foco=='om-leitura' and 'em conferência' in c and 'sobra a devolver: 4 L Óleo de motor 15W-40' in c, f'corrigir leitura e aplicar 12 de 16 L: sobra de 4 L · {c[:150]}')
    clk('Resolver sobras','aside'); clk('Encerrar ordem','aside'); e=toast()
    ok('encerrada' in e and 'R$ 2.626,00' in e, f'custo com o aplicado (690 + 12 × 28 + 5 h × 320) · {e[:100]}')
    # 2 · abastecimento: leitura alta (zero a mais) fica a confirmar e pode ser descartada; leitura menor confirma a troca de contador
    novo(); t.goto('MA-05.dc.html'); sem_erro('MA-05')
    a1=abast('Trator 02 · MF 7719','29880'); r1=linha(0,'AB-1043')
    clk('Descartar','[role=table]'); d1=toast(); t2=J("__man.manGet().ativos.a02.leit.val")
    ok('acima da última' in a1 and 'Leitura a confirmar' in r1 and 'Confirmar leitura' in r1 and 'descartada' in d1 and t2==2988 and 'Leitura descartada' in linha(0,'AB-1043'),
       f'leitura alta: a confirmar, descartada, Trator 02 segue em 2.988 h · {r1[:110]}')
    a2=abast('Comboio CB-01','48100'); clk('Confirmar troca','[role=table]'); c2=toast()
    t.goto('MA-03.dc.html'); lc=linha(0,'Comboio')
    ok('troca de contador' in a2 and 'Troca de contador confirmada' in c2 and '48.100 km' in lc and '49.900 km' in lc and 'Leitura a confirmar' not in lc,
       f'troca de contador confirmada: 48.100 km, vencimento ajustado para 49.900 km · {lc[:140]}')
    # 3 · MA-01: contador da linha = última leitura (abastecimento)
    t.goto('MA-05.dc.html'); abast('Trator 04 · JD 5078E','3530'); t.goto('MA-01.dc.html'); l4=linha(0,'Trator 04')
    ok('3.530 h' in l4 and '3.410 h' not in l4, f'MA-01: contador do Trator 04 atualizado · {l4[:110]}')
    # 4 · achado do MA-02 vinculado à preventiva persiste e aparece na OM
    novo(); t.goto('MA-03.dc.html'); clk('Gerar 3 ordens preventivas'); t.goto('MA-02.dc.html'); clk('Vincular à OM-0236'); v=toast()
    t.goto('MA-02.dc.html'); l6=linha(0,'NC-0912'); hr=J("[...document.querySelectorAll('a')].filter(a=>a.innerText.trim()==='Ver OM-0228').map(a=>a.getAttribute('href'))")
    t.goto('MA-04.dc.html#OM-0236'); time.sleep(.4); p=pan()
    ok('vinculado' in v and 'Ver OM-0236' in l6 and 'Vincular à' not in l6 and 'Achado vinculado: NC-0912' in p and hr==['MA-04.dc.html#OM-0228'], f'MA-02: vínculo persiste e aparece na OM-0236 · {l6[-60:]} · {hr}')
    # 5 · falta de peça: Solicitar compra → Registrar recebimento → Liberar serviço
    J("document.querySelector('aside[role=dialog] button[aria-label=Fechar]').click()"); time.sleep(.3)
    t.goto('MA-04.dc.html#OM-0235'); time.sleep(.4); clk('Solicitar compra','aside'); s1=toast(); p1=pan()
    clk('Registrar recebimento','aside'); s2=toast(); clk('Liberar serviço','aside'); s3=toast()
    ok('SC-041 enviada' in s1 and 'Registrar recebimento' in p1 and 'Recebimento da SC-041' in s2 and 'liberada para a oficina' in s3, f'falta de peça: compra, recebimento e liberação · {s3[:80]}')
    # 6 · F5 reabre a OM aberta pela linha
    t.goto('MA-04.dc.html'); J("(()=>{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.indexOf('OM-0228')>=0); r.querySelectorAll('[role=cell]')[1].click();})()"); time.sleep(.5)
    h=J("location.hash"); J("window.__velho=1; location.reload()"); time.sleep(1.2); d=J("(document.querySelector('aside[role=dialog] h2')||{}).innerText||''")
    ok(h=='#OM-0228' and d.startswith('OM-0228'), f'F5 reabre a OM: {h} · {d}')
    # 7 · painel da OM: Tab gira dentro; Esc com o foco fora fecha
    J("document.getElementById('om-painel').focus()")
    for _ in range(25): key('Tab','Tab',9)
    dentro=J("!!document.activeElement.closest('#om-painel')")
    J("document.querySelector('[aria-label=\"Filtrar por fase\"] button').focus()"); key('Escape','Escape',27); time.sleep(.3)
    ok(dentro and not J("!!document.getElementById('om-painel')") and J("location.hash")=='', f'OM: Tab preso ({dentro}), Esc fora fecha e limpa o endereço')
    # 8 · 1.280 × 800 com ordens geradas: nenhuma grade com rolagem horizontal escondida
    t.c.size(1280,800); cort=[]
    for f in ['PM.dc.html#PM-07','MA-01.dc.html','MA-02.dc.html','MA-03.dc.html','MA-04.dc.html','MA-05.dc.html']:
        t.goto(f); time.sleep(.3)
        r=J("[...document.querySelectorAll('[role=table]')].map(tb=>{const w=tb.parentElement; return w.scrollWidth-w.clientWidth;})")
        if any(x>1 for x in r): cort.append(f+' '+str(r))
    ok(not cort, f'1.280 px: grades sem coluna cortada {cort}')
    t.c.size(1440,1100); sem_erro('fim')
finally:
    t.c.close(); t.srv.terminate()
print('FALHAS:',len(FALHAS)); [print(' -',f) for f in FALHAS]
if FALHAS: raise AssertionError('; '.join(FALHAS))
