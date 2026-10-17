# -*- coding: utf-8 -*-
"""Teste CDP do módulo Suprimentos (oculto): defeitos DEMO-02/03/18 e ações de SU-06..SU-09."""
import sys, os, time, subprocess, json
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from cdp import Chrome
from journeys import free
R=os.path.join(os.path.dirname(os.path.abspath(__file__)),'_render'); p=free()
srv=subprocess.Popen(['python3','-m','http.server',str(p),'--bind','127.0.0.1','--directory',R],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(0.8)
c=Chrome(port=free()); J=c.js
CLK="""((t,root)=>{const r=root?document.querySelector(root):document; const n=s=>(s||'').replace(/\\s+/g,' ').trim(); const els=[...r.querySelectorAll('button,a')]; const e=els.find(x=>n(x.innerText)===t)||els.find(x=>n(x.innerText).startsWith(t)); if(!e) return 'NÃO ACHEI: '+t; e.preventDefault&&0; e.click(); return 'ok';})"""
SETV="""((sel,val)=>{const i=document.querySelector(sel); if(!i) return 'sem '+sel; const P=i.tagName==='SELECT'?HTMLSelectElement.prototype:(i.tagName==='TEXTAREA'?HTMLTextAreaElement.prototype:HTMLInputElement.prototype); Object.getOwnPropertyDescriptor(P,'value').set.call(i,val); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true})); return 'ok';})"""
T=lambda: J("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).filter(Boolean).join(' | ')")
def clk(t,root=None): r=J(f"({CLK})({json.dumps(t)},{json.dumps(root)})"); time.sleep(.45); return r
def setv(sel,val): r=J(f"({SETV})({json.dumps(sel)},{json.dumps(val)})"); time.sleep(.25); return r
def txt(pat): return J(f"(document.body.innerText.match(new RegExp({json.dumps(pat)}))||['(não achou)'])[0]")
def row(pat): return J(f"(([...document.querySelectorAll('[role=row]')].find(r=>new RegExp({json.dumps(pat)}).test(r.innerText))||{{}}).innerText||'').replace(/\\s+/g,' ')")
def go(t): c.goto(f'http://127.0.0.1:{p}/{t}'); time.sleep(.4)
FAIL=[]
def ok(cond,msg):
    print(('OK   ' if cond else 'FALHA ')+msg)
    if not cond: FAIL.append(msg)
try:
    c.size(1440,1100)
    # ---------- SU-06 · DEMO-02 ----------
    go('SU-06.dc.html')
    # TAB-07 (DS-MODULOS-2, 17/10/2026): o cartão "EM QUARENTENA" saiu de cima da lista; a quarentena é lida no selo do cabeçalho
    # (contraprova: o render anterior ainda tem o cartão e reprova o 2º ok)
    ok('10 t em quarentena' in J("document.querySelector('h1').parentElement.innerText"),'SU-06 selo do cabeçalho: 10 t em quarentena')
    ok(not J("/EM QUARENTENA\\s+\\d/.test(document.querySelector('main').innerText)"),'SU-06 TAB-07: sem cartão de resumo da quarentena sobre a lista')
    clk('Liberar qualidade'); t=T(); print('   ',t)
    ok('10.000 kg liberados' in t and 'LQ-2031' in t,'SU-06 liberar qualidade soma uma vez com recibo')
    r=row('^NF 4501\\s+PC-088'); print('   ',r)
    ok('60.000 kg' in r and 'Liberar qualidade' not in r and 'LQ-2031' in r,'SU-06 linha PC-088 60.000 aptos e botão trocado pelo recibo')
    ok('quarentena' not in J("document.querySelector('h1').parentElement.innerText").lower(),'SU-06 selo sem quarentena')
    clk('Conferir NF 4533'); ok(J("!!document.querySelector('aside[role=dialog]')"),'SU-06 primário abre a conferência da NF 4533')
    ids=J("[...document.querySelectorAll('aside[role=dialog] input, aside[role=dialog] select')].map(i=>i.id)"); print('   campos',ids)
    vals=['18000','S58-0926','09/2027','Visual · aprovada','Câmara fria','Sem divergência']
    for i,v in zip(ids,vals): setv('#'+i,v)
    clk('Salvar','aside[role=dialog]'); t=T(); print('   ',t)
    ok('18.000' in t and '2.000 kg' in t,'SU-06 conferência parcial mantém saldo aberto')
    ok('Falta' in row('NF 4533'),'SU-06 falta registrada como divergência')
    clk('Resolver diferença'); clk('Registrar decisão','aside[role=dialog]'); print('   ',T())
    clk('Resolver diferença'); clk('Registrar decisão','aside[role=dialog]'); print('   repetir:',J("(document.querySelector('aside [role=alert]')||{}).innerText"))
    clk('Cancelar','aside[role=dialog]')
    # ---------- SU-07det · DEMO-03 ----------
    go('SU-07det.dc.html')
    clk('Conciliar custódia'); t=T(); ok('recusada' in t and '10 sc' in t,'SU-07det conciliar recusa com 10 sc em custódia')
    clk('Receber devolução'); clk('Confirmar recebimento','aside[role=dialog]'); t=T(); print('   ',t)
    ok('10 → 0' in t,'SU-07det receber devolução zera a custódia')
    hdr=J("document.querySelector('h1').parentElement.innerText"); print('   selo:',hdr.replace('\n',' '))
    ok('Custódia zerada' in hdr,'SU-07det selo do cabeçalho acompanha')
    r=row('Saldo em custódia'); print('   ',r); ok('0 sc' in r and 'Impede' not in r,'SU-07det linha saldo em custódia 0 e sem impedimento')
    clk('Conciliar custódia'); t=T(); print('   ',t); ok('pronta para encerrar' in t,'SU-07det conciliação libera o encerramento')
    ok('Encerrar a OS-0417' in J("document.body.innerText"),'SU-07det próximo passo encerrar')
    clk('Conciliar custódia') if 'Conciliar custódia' in J("document.body.innerText") else None
    # ---------- SU-07 ----------
    go('SU-07.dc.html')
    clk('Confirmar entrega'); t=T(); ok('Bloqueado' in t and '3.640' in t,'SU-07 REQ-036 entrega bloqueada com residual 3.640 kg')
    r=row('REQ-039'); J("""(()=>{const r=[...document.querySelectorAll('[role=row]')].find(r=>/REQ-039/.test(r.innerText)); [...r.querySelectorAll('button')].find(b=>/Separar FEFO/.test(b.innerText)).click();})()"""); time.sleep(.4)
    J("""(()=>{const r=[...document.querySelectorAll('[role=row]')].find(r=>/REQ-039/.test(r.innerText)); [...r.querySelectorAll('button')].find(b=>/Confirmar entrega/.test(b.innerText)).click();})()"""); time.sleep(.4)
    t=T(); print('   ',t); ok('custódia de Marcos 0 → 65 L' in t,'SU-07 REQ-039 separa e entrega à custódia')
    clk('Entregar 8.000 kg'); t=T(); print('   ',t); ok('3.400 kg pendentes' in t,'SU-07 REQ-040 entrega parcial')
    # edição pela linha REQ-038 com valores válidos
    J("""(()=>{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>/REQ-038/.test(r.innerText)); r.querySelector('[role=cell]').click();})()"""); time.sleep(.4)
    ids=J("[...document.querySelectorAll('aside[role=dialog] input:not([readonly]), aside[role=dialog] select:not([disabled])')].map(i=>i.id)"); print('   campos',ids)
    setv('#'+ids[1],'reservatório P1'); clk('Salvar','aside[role=dialog]'); ok('reservatório P1' in J("document.body.innerText") or 'Salvo' in T(),'SU-07 salvar edição pela linha')
    # ---------- SU-08 ----------
    go('SU-08.dc.html')
    clk('Confirmar recebimento'); t=T(); print('   ',t); ok('confirmada no destino' in t,'SU-08 confirma trânsito')
    clk('Estornar com vínculo'); clk('Estornar com vínculo','aside[role=dialog]'); print('   sem motivo:',J("(document.querySelector('aside [role=alert]')||{}).innerText"))
    ids=J("[...document.querySelectorAll('aside[role=dialog] input')].map(i=>i.id)"); setv('#'+ids[-1],'quantidade digitada errada'); clk('Estornar com vínculo','aside[role=dialog]'); t=T(); print('   ',t)
    ok('ES-0072' in t and 'original' in t,'SU-08 estorno cria movimento vinculado')
    ok('Estornado · ver ES-0072' in row('^MV-8788'),'SU-08 original marcado como estornado')
    # ---------- SU-09 ----------
    go('SU-09.dc.html')
    clk('Submeter ajuste'); t=T(); ok('Informe causa' in t,'SU-09 submeter sem causa recusa')
    clk('Aprovar ajuste INV-2609'); t=T(); print('   ',t); ok('AJ-0093' in t and '90.000 → 89.400' in t,'SU-09 aprova ajuste com vínculo')
    ok('Ver efeito no extrato' in J("document.querySelector('h1').parentElement.parentElement.innerText"),'SU-09 primário troca após aprovar')
    # ---------- SU-03det · DEMO-18 ----------
    # revisão do CTL-4 (S4): com a demanda única o Fungicida A não tem pendência na SOL-2026-07 e o DEMO-18 não tem conflito a decidir
    # (antes: "pendência 0 L" com "Reservar 480 L com pendência"); a tela mostra a reserva da OS-0424 e o uso da safra que o lote cobre
    go('SU-03det.dc.html')
    hdr=J("document.querySelector('h1').parentElement.innerText"); bd=J("document.body.innerText")
    # revisão do 853a6a8 (achado 6): a pendência vem da demanda única viva (a mesma do Planejar safra e da Compra), não da semente no build
    ok('Sem conflito' in hdr and 'Uso da safra 2026/27 de hoje em diante' in bd and 'Sem pendência de compra' in bd,'SU-03det sem conflito: selo, uso da safra e sem pendência')
    ok('com pendência' not in bd and 'Aguardar a compra' not in bd and 'pendência 0' not in bd,'SU-03det sem decisão de conflito inexistente')
    # ---------- SU-03 ----------
    go('SU-03.dc.html')
    clk('Reservar para ordem'); clk('Reservar','aside[role=dialog]'); t=T(); print('   ',t); ok('Reserva confirmada para a OS-0421' in t,'SU-03 reserva nomeia a ordem')
    r=row('F26-02'); print('   ',r)
    clk('Reservar para ordem'); clk('Reservar','aside[role=dialog]'); print('   repetir:',J("(document.querySelector('aside [role=alert]')||{}).innerText"))
    print('erros JS:', J("window.__err||'nenhum'"))
finally:
    c.close(); srv.terminate()
print('\nRESULTADO:', 'OK' if not FAIL else 'FALHOU '+str(FAIL))
