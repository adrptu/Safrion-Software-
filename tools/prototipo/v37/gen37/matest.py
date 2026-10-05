# -*- coding: utf-8 -*-
"""Teste CDP do módulo Manutenção (MA-01..MA-05 + MA-04det): faixa de etapas, largura das grades, edição pela linha e jornadas DEMO-04/DEMO-17.
Planos de manutenção (PM) e o giro das preventivas ficam em ma_planos_test.py; aqui o cenário da manutenção é zerado no início."""
import sys, os, time, subprocess, json
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from cdp import Chrome
from journeys import free
R=os.path.join(os.path.dirname(os.path.abspath(__file__)),'_render'); p=free()
srv=subprocess.Popen(['python3','-m','http.server',str(p),'--bind','127.0.0.1','--directory',R],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(0.8)
c=Chrome(port=free()); J=c.js
CLK="""((t,root)=>{const r=root?document.querySelector(root):document; const n=s=>(s||'').replace(/\\s+/g,' ').trim(); const els=[...r.querySelectorAll('button,a')]; const e=els.find(x=>n(x.innerText)===t)||els.find(x=>n(x.innerText).startsWith(t)); if(!e) return 'NÃO ACHEI: '+t; e.click(); return 'ok';})"""
T=lambda: J("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).filter(Boolean).join(' | ')")
def clk(t,root=None): r=J(f"({CLK})({json.dumps(t)},{json.dumps(root)})"); time.sleep(.45); return r
ROWCLICK="""((gi,txt,ci)=>{const g=document.querySelectorAll('[role=table]')[gi]; const r=[...g.querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.indexOf(txt)>=0); if(!r) return 'sem linha'; r.querySelectorAll('[role=cell]')[ci].click(); return 'ok';})"""
def rowclick(gi,txt,ci=1): r=J(f"({ROWCLICK})({gi},{json.dumps(txt)},{ci})"); time.sleep(.4); return r
SETV="""((sel,val)=>{const i=document.querySelector(sel); if(!i) return 'sem campo '+sel; const P=i.tagName==='SELECT'?HTMLSelectElement.prototype:(i.tagName==='TEXTAREA'?HTMLTextAreaElement.prototype:HTMLInputElement.prototype); Object.getOwnPropertyDescriptor(P,'value').set.call(i,val); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true})); return 'ok';})"""
def setv(sel,val): r=J(f"({SETV})({json.dumps(sel)},{json.dumps(val)})"); time.sleep(.25); return r
dlg=lambda: J("(document.querySelector('aside[role=dialog] h2')||{}).innerText||null")
def dlgis(t): d=dlg(); return bool(d) and (d==t or d.startswith(t+' · '))
body=lambda: J("document.body.innerText")
FALHAS=[]
def ok(cond,msg):
    print(('  ok  ' if cond else '  FALHA ')+msg)
    if not cond: FALHAS.append(msg)
def comum(tela,cur):
    c.goto(f'http://127.0.0.1:{p}/{tela}'); time.sleep(.4)
    ok(J("window.__err||null") is None, f'{tela}: sem erro JS')
    st=J("[...document.querySelectorAll('nav[aria-label=\"Telas da manutenção\"] a')].filter(a=>!a.getAttribute('aria-label')).filter(a=>!a.getAttribute('aria-label')).map(a=>a.getAttribute('href')+'|'+(a.getAttribute('aria-current')||''))")
    ok(len(st)==5 and st[cur-1].endswith('|page') and [s.split('|')[0] for s in st]==['MA-01.dc.html','MA-02.dc.html','MA-03.dc.html','MA-04.dc.html','MA-05.dc.html'], f'{tela}: faixa com 5 links e etapa {cur} atual')
    ov=J("[...document.querySelectorAll('[role=table]')].map(t=>{const w=t.parentElement; return w.scrollWidth-w.clientWidth;})")
    ok(all(x<=2 for x in ov), f'{tela}: grades sem rolagem horizontal a 1440 px {ov}')
    ed=J("[...document.querySelectorAll('button')].filter(b=>/^Editar/.test(b.innerText.trim())).length")
    ok(ed==0, f'{tela}: sem botões Editar')
try:
    c.size(1440,1000)
    c.goto(f'http://127.0.0.1:{p}/MA-01.dc.html'); time.sleep(.3); J("localStorage.removeItem('talhao-os-manutencao-v1')")
    # ---------- MA-01 ----------
    print('MA-01'); comum('MA-01.dc.html',1)
    ag=J("(()=>{const r=[...document.querySelectorAll('[role=table]')[0].querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.indexOf('Trator 02')>=0); return r?r.innerText.replace(/\\s+/g,' '):'';})()")
    t=body(); ok('Proposto' in ag and 'OS-0420 saldo 70 ha · aguarda PCP' in ag and 'Comprometido · OS-0420' not in t, 'MA-01: substituto com rótulo único antes do PCP · '+ag[:120])
    ok('Colhedora Axial-Flow 7250' in t and 'S680' not in t and 'Comboio CB-01' in t and J("document.querySelectorAll('[role=table]')[0].querySelectorAll('[role=row].g2ed').length")==16, 'MA-01: 16 ativos com a identidade do CD-03 + comboio')
    ok('Sem plano' in t and 'Criar plano' in t and 'Vence em breve' in t and 'Vencida' in t, 'MA-01: próxima manutenção vem dos planos (Vencida · Vence em breve · Sem plano)')
    rowclick(0,'Colhedora',1); ok(dlgis('Ativo'), 'MA-01: clique na linha abre formulário do ativo')
    setv('aside[role=dialog] select[id$=_cond]','Restrito · monitorado'); clk('Salvar','aside[role=dialog]')
    ok('Motivo' in (J("(document.querySelector('aside[role=dialog]')||{}).innerText")or''), 'MA-01: restrição exige motivo')
    setv('aside[role=dialog] textarea[id$=_motr]','Ruído no elevador'); clk('Salvar','aside[role=dialog]')
    ok('restrito' in T(), 'MA-01: salvar restrição avisa alocações '+T()[:80])
    rowclick(0,'Trator T1',1); setv('aside[role=dialog] select[id$=_cond]','Apto'); clk('Salvar','aside[role=dialog]')
    ok('continua Bloqueado' in T(), 'MA-01: T1 só é liberado pela OM-0233')
    setv('select[aria-label^=Tarefa]','pu'); ok('pulverização' in body(), 'MA-01: troca de tarefa recalcula elegíveis')
    # ---------- MA-02 ----------
    print('MA-02'); comum('MA-02.dc.html',2)
    t=body(); ok('INSP-105' in t and 'OS-0431' in t, 'MA-02: inspeção INSP-105 e OS-0431 na contingência')
    clk('Registrar inspeção'); ok(dlg()=='Registrar inspeção (checklist)', 'MA-02: registrar inspeção abre formulário')
    clk('Salvar','aside[role=dialog]'); ok('Informe ativo' in (J("document.querySelector('aside[role=dialog]').innerText") or ''), 'MA-02: novo achado exige escolher o ativo')
    setv('aside[role=dialog] select[id$=_ativo]','Colhedora Axial-Flow 7250'); setv('aside[role=dialog] textarea[id$=_sint]','Folga na direção'); setv('aside[role=dialog] input[id$=_evid]','foto'); clk('Salvar','aside[role=dialog]')
    ok('registrado' in T(), 'MA-02: novo achado registrado '+T()[:80])
    ok(J("document.querySelectorAll('[role=table]')[0].querySelectorAll('[role=row].g2ed').length")==7, 'MA-02: fila com 7 casos')
    clk('Vincular à OM-0234'); ok('vinculado' in T(), 'MA-02: vincular achado não cria ordem nova')
    # ---------- MA-03 ----------
    print('MA-03'); comum('MA-03.dc.html',3)
    t=body(); ok('Mover OM-0234 para 29/09' in t and 'Propor substituição' in t and 'Manutenções e impacto na produção' in t, 'MA-03: painel com Mover OM-0234 e Propor substituição')
    ok(J("document.querySelector('h1').innerText")=='Vencimentos e paradas' and 'Gerar 3 ordens preventivas' in t and 'Simular paradas' not in t and 'Confirmar 2 paradas' not in t, 'MA-03: Vencimentos e paradas com a primária pelo estado; ações sem efeito cortadas')
    clk('Mover OM-0234 para 29/09'); ok('movida para 29/09' in T() and 'Mover OM-0234' not in body(), 'MA-03: mover a OM-0234 para 29/09 tira o conflito · '+T()[:100])
    clk('Propor substituição'); ok('aguarda PCP' in T() and 'Propor substituição' not in body(), 'MA-03: propor substituição registra proposta (uma vez)')
    ok(clk('Abrir impedimentos')!='ok' and 'PL-05' not in (J("document.body.innerHTML") or ''), 'MA-03: sem link para impedimentos (PL-05 oculta e fixa · CTL-1, Frente F)')
    # ---------- MA-04 ----------
    print('MA-04'); comum('MA-04.dc.html',4)
    clk('Iniciar serviço'); ok('Em execução' in T(), 'MA-04: iniciar serviço da OM-0228')
    clk('Resolver sobras'); ok('devolvidas' in T(), 'MA-04: resolver sobras da OM-0230')
    clk('Encerrar ordem'); ok('encerrada' in T(), 'MA-04: encerrar OM-0230')
    rowclick(0,'OM-0234',2); ok((dlg() or '').startswith('OM-0234 · Trator 02') and 'Liberar serviço' in J("document.querySelector('aside[role=dialog]').innerText"), 'MA-04: clique na linha abre o painel da ordem com o próximo passo')
    ok('Planejar e autorizar ordem' not in body(), 'MA-04: painel cravado Planejar e autorizar ordem removido')
    # ---------- MA-04det ----------
    print('MA-04det'); comum('MA-04det.dc.html',4)
    t=body(); ok('OS-0431' in t and 'publicado pelo PCP' not in t, 'MA-04det: OS-0431 no impacto e substituto só proposto')
    clk('Definir aptidão do ativo'); ok('exige teste aprovado' in T(), 'MA-04det: aptidão recusada sem teste')
    clk('Registrar teste do reparo'); ok('aprovado' in T(), 'MA-04det: teste registrado')
    ok(J("[...document.querySelectorAll('[role=table]')[2].querySelectorAll('[role=row]')].map(r=>r.innerText).join('|')").count('Aprovado')==1, 'MA-04det: 2ª tentativa vira Aprovado')
    clk('Encerrar ordem'); te=T(); ok('concluir o serviço' in te and 'teste' not in te.split('falta')[1], 'MA-04det: recusa de encerrar lista só serviço e sobras · '+te[:120])
    clk('Definir aptidão do ativo'); ok('Trator T1 apto' in T() and 'reprogramação' in T(), 'MA-04det: aptidão definida')
    clk('Concluir serviço'); ok('Em conferência' in T(), 'MA-04det: concluir serviço')
    ok(dlg() is None, 'MA-04det: nenhuma edição aberta')
    J("(()=>{const b=[...document.querySelectorAll('header button, button')].find(b=>b.innerText.trim()==='Resolver sobras'); b.click();})()"); time.sleep(.4)
    ok(dlgis('Destinar sobra'), 'MA-04det: resolver sobras abre a sobra pela linha')
    setv('aside[role=dialog] select[id$=_dest]','Enviar para recondicionamento'); clk('Salvar','aside[role=dialog]')
    ok('sobras resolvidas' in T(), 'MA-04det: sobras resolvidas')
    clk('Encerrar ordem'); ok('encerrada' in T(), 'MA-04det: ordem encerrada')
    ok('Voltar às ordens' in body(), 'MA-04det: próxima ação volta às ordens')
    rowclick(1,'Reaperto',1); ok(dlgis('Tarefa'), 'MA-04det: tarefa abre pela linha')
    c.shot('_probe/ma04det_fim.png')
    # ---------- MA-05 ----------
    print('MA-05'); comum('MA-05.dc.html',5)
    rowclick(1,'Colhedora',1); ok('ORIGEM' in (J("(document.querySelector('aside[role=dialog]')||{}).innerText")or''), 'MA-05: consumo abre origem')
finally:
    c.close(); srv.terminate()
print('FALHAS:',len(FALHAS)); [print(' -',f) for f in FALHAS]

if FALHAS: raise AssertionError('; '.join(FALHAS))
