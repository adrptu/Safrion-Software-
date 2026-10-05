# -*- coding: utf-8 -*-
"""Teste CDP do módulo Comercial (VE-01..VE-06): faixa de etapas, edição pela linha, disputa de saldo (DEMO-18),
revisão v3 do PV-031 (DEMO-06), criação de oferta/compromisso/caso."""
import sys, os, time, subprocess, json
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from cdp import Chrome
from journeys import free
R=os.path.join(os.path.dirname(os.path.abspath(__file__)),'_render'); p=free()
srv=subprocess.Popen(['python3','-m','http.server',str(p),'--bind','127.0.0.1','--directory',R],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(0.8)
c=Chrome(port=free()); J=c.js
SETV="""((sel,val)=>{const i=document.querySelector(sel); if(!i) return 'sem campo '+sel; const P=i.tagName==='SELECT'?HTMLSelectElement.prototype:(i.tagName==='TEXTAREA'?HTMLTextAreaElement.prototype:HTMLInputElement.prototype); Object.getOwnPropertyDescriptor(P,'value').set.call(i,val); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true})); return 'ok';})"""
CLK="""((t,root)=>{const r=root?document.querySelector(root):document; if(!r) return 'sem raiz'; const n=s=>(s||'').replace(/\\s+/g,' ').trim(); const els=[...r.querySelectorAll('button,a')]; const e=els.find(x=>n(x.innerText)===t)||els.find(x=>n(x.innerText).startsWith(t)); if(!e) return 'NÃO ACHEI: '+t; e.click(); return 'ok';})"""
ROWBTN="""((rid,t)=>{const row=[...document.querySelectorAll('[role=row]')].find(r=>r.innerText.indexOf(rid)>=0); if(!row) return 'sem linha '+rid; const b=[...row.querySelectorAll('button,a')].find(x=>x.innerText.trim().startsWith(t)); if(!b) return 'sem botão '+t; b.click(); return 'ok';})"""
ROWOPEN="""((rid)=>{const rs=[...document.querySelectorAll('[role=row].g2ed')].filter(r=>r.innerText.indexOf(rid)>=0); const row=rs.find(r=>r.innerText.trim().startsWith(rid))||rs[0]; if(!row) return 'sem linha '+rid; const c=row.querySelectorAll('[role=cell]'); (c[1]||c[0]).click(); return 'ok';})"""
ROWTXT="""((rid)=>{const rs=[...document.querySelectorAll('[role=row]')].filter(r=>r.innerText.indexOf(rid)>=0); const row=rs.find(r=>r.innerText.trim().startsWith(rid))||rs[0]; return row?row.innerText.replace(/\\s+/g,' '):'sem linha';})"""
T=lambda: J("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).filter(Boolean).join(' | ')")[:260]
def clk(t,root=None): r=J(f"({CLK})({json.dumps(t)},{json.dumps(root)})"); time.sleep(.45); return r
def rowbtn(rid,t): r=J(f"({ROWBTN})({json.dumps(rid)},{json.dumps(t)})"); time.sleep(.45); return r
def rowopen(rid): r=J(f"({ROWOPEN})({json.dumps(rid)})"); time.sleep(.45); return r
def rowtxt(rid): return J(f"({ROWTXT})({json.dumps(rid)})")[:220]
def fld(): return J("[...document.querySelectorAll('aside[role=dialog] input, aside[role=dialog] select, aside[role=dialog] textarea')].map(i=>i.id+'='+i.value)")
def setv(sel,v): r=J(f"({SETV})({json.dumps(sel)},{json.dumps(v)})"); time.sleep(.15); return r
def aside(): return J("!!document.querySelector('aside[role=dialog]')")
def fid(k): return J(f"(()=>{{const i=[...document.querySelectorAll('aside[role=dialog] input, aside[role=dialog] select, aside[role=dialog] textarea')].find(x=>x.id.endsWith('_{k}')||x.id==='{k}'||x.name==='{k}'); return i?('#'+i.id):null;}})()")
FAIL=[]
def ok(cond,msg):
    print(('OK  ' if cond else 'FALHA ')+msg)
    if not cond: FAIL.append(msg)
NOMES=['Confira demanda e oferta','Acompanhe o mercado','Faça ofertas','Registre pedidos','Controle contratos','Trate reclamações']
try:
    c.size(1440,1000)
    for i,t in enumerate(['VE-01','VE-02','VE-03','VE-04','VE-04det','VE-05','VE-06']):
        c.goto(f'http://127.0.0.1:{p}/{t}.dc.html'); time.sleep(.5)
        # UX-ACAO-UNICA-20261003: VE-01…06 são telas irmãs do módulo (navegação "Telas do módulo", sem setas, atual com aria-current=page)
        st=J("[...document.querySelectorAll('nav[aria-label=\"Telas do módulo\"] .etp-itens a')].map(a=>a.getAttribute('href')+'|'+a.innerText.replace(/\\s+/g,' ').trim())")
        cur=J("(document.querySelector('nav[aria-label=\"Telas do módulo\"] .etp-itens [aria-current=page]')||{}).innerText")
        ok(len(st)==6 and all(NOMES[k] in st[k] for k in range(6)),f'{t}: faixa 6 etapas por links')
        ok(cur and NOMES[min(i,3) if i<5 else i-1] in cur,f'{t}: etapa atual = {cur!r}')
        ok(J("window.__err||''")=='' ,f'{t}: sem erro JS')
        desc=J("[...document.querySelectorAll('h2')].map(h=>{const n=h.closest('section')||h.parentElement.parentElement; return h.innerText;}).length")
    # VE-04 · disputa de saldo
    c.goto(f'http://127.0.0.1:{p}/VE-04.dc.html'); time.sleep(.5)
    print('confirmar PV-032:',rowbtn('PV-032','Confirmar pedido')); t1=T(); ok('confirmado' in t1 and 'CMD-5521' in t1,'PV-032 confirmado com recibo: '+t1)
    print('confirmar PV-033:',rowbtn('PV-033','Confirmar pedido')); t2=T(); ok('Conflito de saldo' in t2,'PV-033 conflito: '+t2)
    ok('Conflito' in rowtxt('PV-033'),'linha PV-033 mostra conflito: '+rowtxt('PV-033'))
    ok(aside()==False,'ação da linha não abre edição')
    # repetir PV-032 -> linha virou ro, mas o botão foi substituído? recibo idempotente
    r=rowbtn('PV-032','Confirmar pedido'); print('repetir PV-032:',r, T())
    ok('Confirmado' in rowtxt('PV-032'),'linha PV-032 confirmada: '+rowtxt('PV-032'))
    # editar PV-033 pela linha
    print('abrir PV-033:',rowopen('PV-033'),fld())
    q=fid('qtd'); print('campo qtd',q, setv(q,'1,0')); clk('Salvar','aside[role=dialog]')
    ok(not aside() and '1,0 t' in rowtxt('PV-033'),'PV-033 editado pela linha: '+rowtxt('PV-033'))
    # novo pedido
    print('novo pedido:',clk('+ Novo pedido')); print(fld())
    setv(fid('qtd'),'2'); setv(fid('preco'),'3,10'); setv(fid('janela'),'05/10–11/10'); clk('Salvar','aside[role=dialog]')
    ok(not aside() and 'PV-034' in J("document.body.innerText"),'novo pedido PV-034 criado: '+T())
    # VE-04det · revisão v3
    c.goto(f'http://127.0.0.1:{p}/VE-04det.dc.html'); time.sleep(.5)
    body=J("document.body.innerText")
    ok('L39-120' in body and 'OB-0110' in body and 'INSP-92' in body and 'L38-115..118' in body,'PV-031 mostra origem L39-120/OB-0110/INSP-92/genealogia')
    ok('A confirmar' in body and 'Confirmado' not in body,'PV-031 não aparece Confirmado')
    print('enviar v3:',clk('Enviar revisão v3')); print(fld())
    clk('Salvar','aside[role=dialog]'); t3=T(); ok('v3' in t3,'v3 enviada: '+t3)
    body=J("document.body.innerText"); ok('Revisão v3 aguardando aceite' in body,'estado muda para Revisão v3 aguardando aceite')
    ok('Aguardando aceite da v3' in body,'ação primária muda')
    clk('Aguardando aceite da v3'); ok('já enviada' in T(),'reenvio não duplica: '+T())
    # VE-03 · ajustar OF-103 e criar oferta
    c.goto(f'http://127.0.0.1:{p}/VE-03.dc.html'); time.sleep(.5)
    print('abrir OF-103:',rowopen('OF-103')); setv(fid('volkg'),'1500'); clk('Salvar','aside[role=dialog]')
    ok('1.500 kg' in rowtxt('OF-103'),'OF-103 editada: '+rowtxt('OF-103'))
    print('abrir OF-101 (aceita):',rowopen('OF-101')); ok(J("document.querySelectorAll('aside[role=dialog] input:not([readonly]),aside[role=dialog] select:not([disabled])').length")==0,'OF-101 aceita abre em consulta'); clk('Fechar','aside[role=dialog]')
    print('nova oferta:',clk('+ Nova oferta')); setv(fid('volkg'),'800'); setv(fid('janela'),'12/10–18/10'); setv(fid('preco'),'3,00'); setv(fid('val'),'05/10'); clk('Salvar','aside[role=dialog]')
    ok('OF-104' in J("document.body.innerText"),'nova oferta OF-104: '+rowtxt('OF-104'))
    # VE-05
    c.goto(f'http://127.0.0.1:{p}/VE-05.dc.html'); time.sleep(.5)
    body=J("document.body.innerText"); ok('CRE-0095' in body and '6.900' in body and '51.280' in body,'VE-05 inclui CPR 6.900 e base V2 51.280')
    print('formalizar:',clk('Formalizar compromisso')); setv(fid('vol'),'3000'); setv(fid('janela'),'mar/27'); setv(fid('condv'),'R$ 133,00/sc · contra entrega'); clk('Salvar','aside[role=dialog]')
    ok('CT-204' in J("document.body.innerText"),'CT-204 formalizado: '+T())
    # VE-06
    c.goto(f'http://127.0.0.1:{p}/VE-06.dc.html'); time.sleep(.5)
    ok('VG-117' in J("document.body.innerText"),'VE-06 tem caso da VG-117')
    print('abrir caso:',clk('Abrir caso')); setv(fid('pedtx'),'PV-030 · entrega 3 de 3'); setv(fid('lote'),'L27-021'); setv(fid('qtd'),'200 sc'); clk('Salvar','aside[role=dialog]')
    ok('RC-16' in J("document.body.innerText"),'caso RC-16 aberto: '+T())
    print('autorizar retorno RC-15:',rowbtn('RC-15','Autorizar retorno'),T()); ok(not aside(),'ação da linha não edita')
    # VE-01 reserva
    c.goto(f'http://127.0.0.1:{p}/VE-01.dc.html'); time.sleep(.5)
    print('abrir RT-0112:',rowopen('RT-0112')); setv(fid('qtd'),'1500'); clk('Salvar','aside[role=dialog]')
    ok('1.500 kg' in rowtxt('RT-0112'),'reserva ajustada: '+rowtxt('RT-0112'))
    body=J("document.body.innerText"); ok('3.500 kg' in body and '1.500 kg firmes' not in body and '6.000 kg firmes + 1.500 kg' in body,'saldo e balanço recalculados: '+T())
    print('abrir RT-0109 expirada:',rowopen('RT-0109')); ok(J("document.querySelectorAll('aside[role=dialog] input:not([readonly])').length")==0,'reserva expirada em consulta')
finally:
    c.close(); srv.terminate()
print('\nRESULTADO:', 'OK' if not FAIL else f'{len(FAIL)} FALHA(S)')
