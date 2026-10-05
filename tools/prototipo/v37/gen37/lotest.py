# -*- coding: utf-8 -*-
"""Teste CDP do módulo Logística (LO-01..LO-04 + LO-02det): faixa de etapas, fila DEMO-20, separação DEMO-19, saída única, recusa DEMO-08, frete.
Uso: python3 lotest.py [--shots]"""
import sys, os, time, subprocess, json
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from cdp import Chrome
from journeys import free
HERE=os.path.dirname(os.path.abspath(__file__)); R=os.path.join(HERE,'_render'); OUT=os.path.join(HERE,'_shots'); p=free()
srv=subprocess.Popen(['python3','-m','http.server',str(p),'--bind','127.0.0.1','--directory',R],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(0.8)
c=Chrome(port=free()); J=c.js; FAIL=[]
CLK="""((t,root)=>{const r=root?document.querySelector(root):document; if(!r) return 'SEM RAIZ '+root; const n=s=>(s||'').replace(/\\s+/g,' ').trim(); const els=[...r.querySelectorAll('button,a')]; const e=els.find(x=>n(x.innerText)===t)||els.find(x=>n(x.innerText).startsWith(t)); if(!e) return 'NÃO ACHEI: '+t; e.click(); return 'ok';})"""
SETV="""((sel,val)=>{const i=document.querySelector(sel); if(!i) return 'sem '+sel; const P=i.tagName==='SELECT'?HTMLSelectElement.prototype:(i.tagName==='TEXTAREA'?HTMLTextAreaElement.prototype:HTMLInputElement.prototype); Object.getOwnPropertyDescriptor(P,'value').set.call(i,val); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true})); return 'ok';})"""
T=lambda: J("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).filter(Boolean).join(' | ')")
def clk(t,root=None): r=J(f"({CLK})({json.dumps(t)},{json.dumps(root)})"); time.sleep(.45); return r
def setv(sel,val): r=J(f"({SETV})({json.dumps(sel)},{json.dumps(val)})"); time.sleep(.3); return r
def row(txt): return J(f"(()=>{{const r=[...document.querySelectorAll('[role=row]')].find(r=>r.innerText.indexOf({json.dumps(txt)})>=0); return r?r.innerText.replace(/\\s+/g,' '):'SEM LINHA';}})()")
def rowclick(txt,grid=0):
    return J(f"(()=>{{const t=document.querySelectorAll('[role=table]')[{grid}]; const r=[...t.querySelectorAll('[role=row]')].find(r=>r.innerText.indexOf({json.dumps(txt)})>=0); if(!r) return 'sem linha'; r.querySelector('[role=cell]').click(); return 'ok';}})()")
def ok(cond,msg):
    print(('  OK  ' if cond else '  FALHA ')+msg)
    if not cond: FAIL.append(msg)
def rowact(txt,btn):
    return J(f"(()=>{{const r=[...document.querySelectorAll('[role=row]')].find(r=>r.innerText.indexOf({json.dumps(txt)})>=0); if(!r) return 'sem linha'; const b=[...r.querySelectorAll('button,a')].find(b=>b.innerText.trim().startsWith({json.dumps(btn)})); if(!b) return 'sem botão'; b.click(); return 'ok';}})()")
def open_(tela):
    c.goto(f'http://127.0.0.1:{p}/{tela}'); time.sleep(.4)
    J("window.__errs=[]; window.addEventListener('error',e=>window.__errs.push(e.message));")
def shots(tela):
    n=J("(()=>{const m=document.querySelector('main[data-scroll]'); return m?Math.ceil(m.scrollHeight/ (m.clientHeight-80)):1;})()") or 1
    for i in range(min(n,5)):
        J(f"(()=>{{const m=document.querySelector('main[data-scroll]'); if(m) m.scrollTop={i}*(m.clientHeight-80);}})()"); time.sleep(.3)
        c.shot(os.path.join(OUT,tela.replace('.dc.html','')+f'_s{i}.png'))
    J("(()=>{const m=document.querySelector('main[data-scroll]'); if(m) m.scrollTop=0;})()")
try:
    c.size(1440,1000)
    # UX-ACAO-UNICA-20261003: LO-01…04 são telas irmãs de um módulo (navegação "Telas do módulo", sem número de etapa, atual com aria-current=page)
    for tela,cur in [('LO-01.dc.html','Programe o transporte'),('LO-02.dc.html','Expeça as cargas'),('LO-02det.dc.html','Expeça as cargas'),('LO-03.dc.html','Acompanhe viagens'),('LO-04.dc.html','Controle fretes')]:
        open_(tela); print(tela)
        a=J("(document.querySelector('nav.etp-sec .etp-itens [aria-current=page]')||{}).innerText||''").replace('\n',' ')
        ok(a.startswith(cur),f'tela atual destacada: {a}')
        ok(J("[...document.querySelectorAll('nav[aria-label=\"Telas do módulo\"] a')].filter(a=>!a.getAttribute('aria-label')).filter(a=>!a.getAttribute('aria-label')).map(a=>a.getAttribute('href')).join(',')")=='LO-01.dc.html,LO-02.dc.html,LO-03.dc.html,LO-04.dc.html','faixa por links LO-01..04')
        ok(J("document.body.innerText.indexOf('{{')<0"),'sem buracos {{}} visíveis')
        ok(J("![...document.querySelectorAll('[role=row] button, [role=row] a')].some(b=>/^(Editar|Alterar)/.test(b.innerText.trim()))"),'sem botões Editar nas linhas')
        ov=J("[...document.querySelectorAll('[role=table]')].map((t,i)=>{const w=t.parentElement; return w.scrollWidth-w.clientWidth>2?('grade '+i+' +'+(w.scrollWidth-w.clientWidth)+'px'):null;}).filter(Boolean)")
        ok(not ov,'grades cabem sem rolagem horizontal '+str(ov))
        if '--shots' in sys.argv: shots(tela)
    # ---------- LO-02 · DEMO-20 / DEMO-19 ----------
    print('LO-02 · fila'); open_('LO-02.dc.html')
    clk('Chamar próximo elegível'); t=T(); ok('bloqueada' in t and 'doca 1 ocupada pelo T2' in t, 'chamar bloqueia com doca 1 ocupada: '+t[:90])
    ok('Aguarda doca 1' in row('T3'),'T3 aguarda doca 1: '+row('T3')[:80])
    ok('Pronta p/ carregar' in row('VD-2101 · 3ª'),'carga do T3 pronta p/ carregar (coerente com Apto)')
    rowact('T4','Avaliar encaixe'); ok(J("document.body.innerText.indexOf('Doca 3 · ensacados livre')>=0"),'Avaliar encaixe abre painel de folga/impacto')
    clk('Encaixar T4 na doca 3'); ok('bloqueado' in T(),'encaixe bloqueado sem separação: '+T()[:70])
    # separação: PV-028 recusa L27-013
    clk('Separar lotes'); ok(J("!!document.querySelector('aside[role=dialog]')"),'painel Separar lotes aberto')
    setv('#ps_ped','PV-028'); opts=J("[...document.querySelectorAll('#ps_lote option')].map(o=>o.innerText+(o.disabled?' [x]':''))")
    ok(all('F26' not in o and 'D26' not in o and 'L27-012' not in o for o in opts) and any('L27-013' in o and '[x]' in o for o in opts),'lotes filtrados por pedido; L27-013 desabilitado: '+str(opts))
    clk('Confirmar separação','aside[role=dialog]'); er=J("[...document.querySelectorAll('aside [role=alert]')].map(x=>x.innerText).join(' | ')")
    ok('INSP-88' in er,'separação de PV-028 recusada com motivo: '+er[:100])
    setv('#ps_ped','TR-0459'); opts=J("[...document.querySelectorAll('#ps_lote option')].map(o=>o.innerText+(o.disabled?' [x]':''))")
    ok(any('50.000 kg aptos' in o for o in opts) and any('quarentena' in o and '[x]' in o for o in opts),'TR-0459 só K26-11 apto; quarentena desabilitada')
    setv('#ps_lote','K26-11'); setv('#ps_qtd','12000'); clk('Confirmar separação','aside[role=dialog]')
    ok('Máximo 10.000' in J("document.querySelector('aside[role=dialog]').innerText"),'quantidade acima da carga recusada junto ao campo')
    setv('#ps_qtd','10000'); clk('Confirmar separação','aside[role=dialog]')
    ok(not J("!!document.querySelector('aside[role=dialog]')") and 'TR-0459 separada' in T(),'TR-0459 separada: '+T()[:90])
    ok('Separada' in row('TR-0459'),'linha TR-0459 atualizada')
    rowact('T4','Avaliar encaixe'); clk('Encaixar T4 na doca 3'); ok('Chamado · doca 3' in row('frota própria'),'T4 chamado à doca 3 após separar: '+T()[:60])
    # chegada T1
    rowact('T1','Registrar chegada'); ok(J("(document.querySelector('aside[role=dialog] h2')||{}).innerText")=='Registrar chegada na portaria · T1','painel de chegada')
    ok(J("!!document.querySelector('#pc_hora[type=time]')"),'campo de hora presente')
    clk('Confirmar chegada do T1','aside[role=dialog]'); ok('identificação' in J("document.querySelector('aside[role=dialog]').innerText").lower(),'exige identificação verificada')
    setv('#pc_doc','ok'); clk('Confirmar chegada do T1','aside[role=dialog]')
    ok('Presente · apto' in row('check-in') and 'depois do T3' in T(),'T1 presente, entra depois do T3')
    ok(J("document.body.innerText.indexOf('T1 chegou')>=0"),'KPI no pátio atualizado')
    clk('Chamar próximo elegível'); ok('T1 (chegou' in T(),'chamada cita T1 depois do T3')
    # reordenar pela linha
    rowclick('Presente · carga pronta',0); ok(J("(document.querySelector('aside[role=dialog] h2')||{}).innerText").startswith('Posição na fila · T3'),'linha abre form de posição')
    ids=J("[...document.querySelectorAll('aside[role=dialog] select')].map(s=>s.id)"); setv('#'+ids[0],'3'); setv('#'+ids[1],'Janela em risco'); clk('Salvar','aside[role=dialog]')
    ok('Fila v5' in T(),'reordenação publica nova versão: '+T()[:70])
    ok(J("window.__errs.length")==0,'sem erros JS '+str(J("window.__errs")))
    # ---------- LO-02det · saída única ----------
    print('LO-02det'); open_('LO-02det.dc.html')
    clk('Registrar lacre'); ok(J("(document.querySelector('aside[role=dialog] h2')||{}).innerText").startswith('Registrar lacre'),'primária abre o lacre pela linha')
    ids=J("[...document.querySelectorAll('aside[role=dialog] input:not([readonly]), aside[role=dialog] select')].map(i=>i.id)")
    setv('#'+ids[0],'LC-778120'); setv('#'+ids[1],'Portaria (Jair)'); setv('#'+ids[2],'Foto do lacre anexada'); clk('Salvar','aside[role=dialog]')
    ok('Lacre LC-778120 registrado' in T(),'lacre registrado: '+T()[:60])
    clk('Pedir autorização de saída'); ok('Autorização' in T(),'autorização concedida (simulada)')
    clk('Confirmar saída'); ok('uma única vez' in T(),'saída confirmada: '+T()[:80])
    clk('Saída confirmada'); ok('não duplica' in T(),'repetir não duplica')
    ok(J("window.__errs.length")==0,'sem erros JS')
    # ---------- LO-03 · DEMO-08 ----------
    print('LO-03'); open_('LO-03.dc.html')
    r=row('VG-117'); ok('RC-15' in r and 'PV-026' in r,'VG-117 mostra caso RC-15 e pedido: '+r[:120])
    ok(J("(()=>{const r=[...document.querySelectorAll('[role=row]')].find(r=>r.innerText.indexOf('VG-117')>=0); const a=r.querySelector('a[href=\"VE-06.dc.html\"]'); return !!a && a.innerText.indexOf('RC-15')>=0;})()"),'link abre o caso RC-15 em VE-06')
    rowclick('VG-119',0); ids=J("[...document.querySelectorAll('aside[role=dialog] input:not([readonly])')].map(i=>i.id)"); setv('#'+ids[0],'11:30'); clk('Salvar','aside[role=dialog]')
    ok('11:30' in row('VG-119'),'VG-119 reprogramada pela linha')
    # ---------- LO-04 ----------
    print('LO-04'); open_('LO-04.dc.html')
    clk('Contratar Rota Sul'); ok('CT-0912' in T() and 'VG-119' in row('VG-119'),'contratação vincula VG-119')
    clk('Rota Sul contratada'); ok('nada duplicado' in T(),'contratar de novo é idempotente')
    rowact('VG-117','Encaminhar pagamento'); ok('CP-2291' in T(),'serviço encaminhado ao pagamento')
    clk('+ Pedir cotação'); ids=J("[...document.querySelectorAll('aside[role=dialog] select')].map(i=>i.id)"); [setv('#'+i,v) for i,v in zip(ids,['TransGrão Ltda','Carga 07 · mamão 9,6 t refrigerado','R$/t'])]
    clk('Salvar','aside[role=dialog]'); ok('Cotação pedida' in T(),'pedido de cotação simulado')
    ok(J("window.__errs.length")==0,'sem erros JS')
    # ---------- LO-01 ----------
    print('LO-01'); open_('LO-01.dc.html')
    clk('+ Reservar slot'); ids=J("[...document.querySelectorAll('aside[role=dialog] input:not([readonly]), aside[role=dialog] select')].map(i=>i.id)")
    setv('#'+ids[0],'09:55–10:30'); setv('#'+ids[1],'Doca 1 · granel'); setv('#'+ids[2],'Teste'); clk('Salvar','aside[role=dialog]')
    ok('ocupada' in T(),'slot sobreposto na doca 1 é recusado: '+T()[:80])
    rowclick('Carga 07',0); ids=J("[...document.querySelectorAll('aside[role=dialog] input:not([readonly]), aside[role=dialog] select')].map(i=>i.id)")
    setv('#'+ids[0],'12:00–13:00'); setv('#'+ids[1],'Documento fiscal pendente'); clk('Salvar','aside[role=dialog]')
    ok('original 11:00–12:00 preservada' in row('Carga 07'),'reprogramação preserva janela original')
    ok(J("window.__errs.length")==0,'sem erros JS')
finally:
    c.close(); srv.terminate()
print('\nRESULTADO:', 'OK' if not FAIL else f'{len(FAIL)} falha(s): '+' ; '.join(FAIL))
