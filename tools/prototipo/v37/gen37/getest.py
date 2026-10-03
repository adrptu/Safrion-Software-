# -*- coding: utf-8 -*-
"""Teste CDP do módulo Gestão (GE-*): edição pela linha em campos tipados, ações de processo sem duplicar, defeitos DEMO corrigidos."""
import sys, os, time, subprocess
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from cdp import Chrome
from journeys import free
SETV="""((sel,val)=>{const i=document.querySelector(sel); const P=i.tagName==='SELECT'?HTMLSelectElement.prototype:(i.tagName==='TEXTAREA'?HTMLTextAreaElement.prototype:HTMLInputElement.prototype); Object.getOwnPropertyDescriptor(P,'value').set.call(i,val); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true}));})"""
BTN="""((t)=>{const b=[...document.querySelectorAll('button')].filter(b=>b.offsetParent!==null).find(b=>b.innerText.trim()===t); if(b){b.click(); return true;} return false;})"""
ROWCLICK="""((txt)=>{const r=[...document.querySelectorAll('[role=row]')].find(r=>r.innerText.indexOf(txt)>=0); if(!r) return 'sem linha'; const c=[...r.querySelectorAll('[role=cell]')]; const cell=c.find(x=>!x.querySelector('a,button,input'))||c[c.length-1]; cell.click(); return true;})"""
TOAST="(document.querySelector('[role=status][aria-live],.g2toast')||{}).innerText||[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).join(' | ')"
BODY="document.body.innerText"
def ok(res,k,cond): res[k]=bool(cond); return cond

def run(port):
    c=Chrome(port=free()); J=c.js; out={}
    def go(t): c.goto(f'http://127.0.0.1:{port}/{t}'); time.sleep(.4)
    def btn(t): r=J(f"({BTN})({t!r})"); time.sleep(.4); return r
    def body(): return J(BODY)
    try:
        c.size(1440,1100)
        # GE-03: OS-0420 presente, linha provisória abre formulário com select de rateio; linha definitiva abre consulta; diesel concilia 1x; fechar bloqueado
        go('GE-03.dc.html'); r={}
        ok(r,'os0420',all(x in body() for x in ['REQ-036 · OS-0420','REQ-037 · OS-0420','Apontamento · OS-0420']))
        J(f"({ROWCLICK})('Romaneio de frete')"); time.sleep(.4)
        ok(r,'abre_form_frete',J("!!document.querySelector('aside[role=dialog] select')"))
        sid=J("document.querySelector('aside[role=dialog] select').id")
        J(f"({SETV})('#{sid}','por tonelada transportada')"); time.sleep(.2); btn('Salvar')
        ok(r,'frete_versionado','Rateio versionado' in body())
        J(f"({ROWCLICK})('REQ-035')"); time.sleep(.4)
        ok(r,'definitivo_consulta',J("document.querySelectorAll('aside[role=dialog] select:not([disabled]), aside[role=dialog] textarea:not([readonly])').length")==0)
        btn('Fechar'); btn('Fechar competência 09/2026'); ok(r,'fechar_bloqueado','diesel' in J(TOAST))
        btn('Conciliar diesel do tanque'); btn('Conciliar diesel do tanque'); ok(r,'diesel_idempotente','já conciliado' in J(TOAST))
        btn('Fechar competência 09/2026'); ok(r,'fechou','fechada' in J(TOAST)); out['GE-03']=r
        # GE-04: programar título (data + conta) salva e avisa; remessa e retorno não duplicam; PC-088 sem título duplicado
        go('GE-04.dc.html'); r={}
        ok(r,'pc088_unico',body().count('NF 4501 · PC-088')==1 and 'BT-090' in body() and 'Agroquímica Delta' not in body())
        J(f"({ROWCLICK})('NF 1203')"); time.sleep(.4)
        ids=J("[...document.querySelectorAll('aside[role=dialog] input[type=date]:not([readonly])')].map(i=>i.id)")
        J(f"({SETV})('#{ids[0]}','2026-10-05')"); time.sleep(.2); btn('Cancelar')
        ok(r,'aviso_nao_salvo','alterações não salvas' in body()); btn('Continuar editando'); btn('Salvar')
        ok(r,'salvou','Programação salva' in J(TOAST) and not J("!!document.querySelector('aside[role=dialog]')"))
        btn('Enviar remessa ao banco'); btn('Enviar remessa ao banco'); ok(r,'remessa_idempotente','já enviada' in J(TOAST))
        J("[...document.querySelectorAll('[role=row]')].find(r=>r.innerText.indexOf('NF 5531')>=0).querySelector('button').click()"); time.sleep(.4)
        ok(r,'retorno_na_linha','Liquidado' in body() and not J("!!document.querySelector('aside[role=dialog]')"))
        out['GE-04']=r
        # GE-05 ?caso=RC-12: filtra; crédito emite 1x e muda saldo
        go('GE-05.dc.html?caso=RC-12'); time.sleep(.5); r={}
        rows=J("[...document.querySelectorAll('[role=table] [role=row]')].slice(1).map(x=>x.innerText.split('\\n')[0])")
        ok(r,'filtrado_rc12',any('FAT-2096' in x for x in rows) and not any('FAT-2090' in x for x in rows)); r['linhas']=rows
        ok(r,'pv028_ausente','PV-028' not in body())
        btn('Emitir crédito do RC-12'); t1=J(TOAST); btn('Emitir crédito do RC-12'); t2=J(TOAST)
        ok(r,'credito','CR-031' in t1 and 'já emitido' in t2 and 'Crédito emitido' in body())
        go('GE-05.dc.html'); J(f"({ROWCLICK})('FAT-2088')"); time.sleep(.4)
        ids=J("[...document.querySelectorAll('aside[role=dialog] input[type=date]:not([readonly])')].map(i=>i.id)")
        J(f"({SETV})('#{ids[0]}','2026-10-01')"); time.sleep(.2); btn('Salvar')
        ok(r,'cobranca_salva','Cobrança registrada' in J(TOAST) and '01/10/2026' in body())
        out['GE-05']=r
        # GE-02det: proposta PP-014 com aviso e estado
        go('GE-02det.dc.html'); r={}
        btn('Propor novo parâmetro de consumo'); time.sleep(.3); btn('Enviar para revisão agronômica'); time.sleep(.4)
        ok(r,'aviso_pp','PP-014' in J(TOAST)); ok(r,'estado_pp','Em revisão agronômica' in body()); out['GE-02det']=r
        # GE-08: após enviar certidão, bloqueio diz em conferência pelo credor
        go('GE-08.dc.html'); r={}
        ok(r,'v2_51280','51.280' in body() and '43%' in body())
        btn('Anexar documento condicionante'); time.sleep(.3); btn('Enviar ao credor'); time.sleep(.3)
        btn('Registrar liberação da 2ª parcela'); ok(r,'bloqueio_conferencia','em conferência pelo credor (responsável: Banco Terra)' in J(TOAST))
        J("[...document.querySelectorAll('[role=row]')].find(r=>r.innerText.indexOf('Compromissos e garantias')>=0).querySelector('button').click()"); time.sleep(.4)
        ok(r,'autorizar_na_linha','Autorizado pela Direção' in body() and not J("!!document.querySelector('aside[role=dialog]')"))
        out['GE-08']=r
        # GE-07: criar ação pelo botão primário gera AC-104
        go('GE-07.dc.html'); r={}
        btn('Criar ação'); time.sleep(.3)
        f=J("[...document.querySelectorAll('aside[role=dialog] input:not([readonly]):not([type=date]), aside[role=dialog] textarea')].map(i=>i.id)")
        for i in f[:3]: J(f"({SETV})('#{i}','Teste de caso')")
        d=J("[...document.querySelectorAll('aside[role=dialog] input[type=date]')].map(i=>i.id)")
        J(f"({SETV})('#{d[0]}','2026-10-15')"); time.sleep(.2); btn('Salvar')
        ok(r,'criou_ac104','AC-104' in body()); out['GE-07']=r
    finally: c.close()
    return out

if __name__=='__main__':
    R=os.path.join(os.path.dirname(os.path.abspath(__file__)),'_render'); p=free()
    srv=subprocess.Popen(['python3','-m','http.server',str(p),'--bind','127.0.0.1','--directory',R],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(0.8)
    try:
        res=run(p)
        for k,v in res.items(): print(k,v)
        bad=[(k,x) for k,v in res.items() for x,y in v.items() if y is False]
        print('FALHAS:',bad or 'nenhuma')
    finally: srv.terminate()
