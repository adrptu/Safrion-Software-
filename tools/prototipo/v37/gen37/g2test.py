# -*- coding: utf-8 -*-
"""Teste interativo da grade G2 numa tela: ordena, busca, abre pela linha, valida, avisa alteração não salva, salva, teclado, link sem abrir edição."""
import sys, os, time, subprocess
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from cdp import Chrome
from journeys import free
SETV="""((sel,val)=>{const i=document.querySelector(sel); const P=i.tagName==='SELECT'?HTMLSelectElement.prototype:(i.tagName==='TEXTAREA'?HTMLTextAreaElement.prototype:HTMLInputElement.prototype); Object.getOwnPropertyDescriptor(P,'value').set.call(i,val); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true}));})"""
BTN="""((t)=>{const b=[...document.querySelectorAll('aside[role=dialog] button')].find(b=>b.innerText.trim()===t); if(b){b.click(); return true;} return false;})"""
def run(tela, port_srv):
    c=Chrome(port=free()); J=c.js; res={}
    try:
        c.size(1440,1100); c.goto(f'http://127.0.0.1:{port_srv}/{tela}')
        res['grades']=J("document.querySelectorAll('[role=table]').length")
        first=lambda: J("[...document.querySelectorAll('[role=table]')[0].querySelectorAll('[role=row]')].slice(1).map(r=>r.innerText.split('\\n')[0].trim())")
        a=first(); J("document.querySelectorAll('[role=table]')[0].querySelectorAll('.g2hb')[0].click()"); time.sleep(.3); b=first()
        J("document.querySelectorAll('[role=table]')[0].querySelectorAll('.g2hb')[0].click()"); time.sleep(.3); d=first()
        res['ordena']= (b!=d) or len(a)<2
        ed=J("document.querySelectorAll('.g2ed').length"); res['linhas_editaveis']=ed
        if ed:
            J("(()=>{const r=document.querySelectorAll('.g2ed')[0]; const s=r.querySelector('[role=cell] span')||r.querySelector('[role=cell]'); s.click();})()"); time.sleep(.4)
            res['abre_form']=J("!!document.querySelector('aside[role=dialog]')")
            ids=J("[...document.querySelectorAll('aside[role=dialog] input:not([readonly]), aside[role=dialog] select:not([disabled]), aside[role=dialog] textarea:not([readonly])')].map(i=>i.id)")
            res['campos_editaveis']=len(ids); res['consulta']= (len(ids)==0)
            if ids:
                J(f"({SETV})('#{ids[0]}','')"); time.sleep(.2); J(f"({BTN})('Salvar')"); time.sleep(.3)
                res['valida']=J("[...document.querySelectorAll('aside [role=alert]')].map(x=>x.innerText).join(' | ')")[:120]
                J(f"({SETV})('#{ids[0]}','TESTE-EDICAO')"); time.sleep(.2); J(f"({BTN})('Cancelar')"); time.sleep(.3)
                res['aviso_nao_salvo']=J("document.body.innerText.indexOf('Há alterações não salvas')>=0")
                J(f"({BTN})('Continuar editando')"); time.sleep(.2); J(f"({BTN})('Salvar')"); time.sleep(.4)
                res['salvou']=J("!document.querySelector('aside[role=dialog]') && document.body.innerText.indexOf('TESTE-EDICAO')>=0")
            else:
                J(f"({BTN})('Fechar')"); time.sleep(.2)
            J("(()=>{const r=document.querySelectorAll('.g2ed')[0]; r.focus(); r.dispatchEvent(new KeyboardEvent('keydown',{key:'Enter',bubbles:true}));})()"); time.sleep(.3)
            res['teclado']=J("!!document.querySelector('aside[role=dialog]')")
            J(f"({BTN})('Fechar')||({BTN})('Cancelar')"); time.sleep(.2); J(f"({BTN})('Descartar alterações')"); time.sleep(.2)
            res['link_nao_edita']=J("(()=>{const a=document.querySelector('.g2ed a'); if(!a) return 'sem link'; a.addEventListener('click',e=>e.preventDefault(),{once:true}); a.click(); return !document.querySelector('aside[role=dialog]');})()")
            res['botao_nao_edita']=J("(()=>{const b=document.querySelector('.g2ed button:not(.g2car)'); if(!b) return 'sem botão'; b.click(); return !document.querySelector('aside[role=dialog]');})()")
    finally: c.close()
    return res
if __name__=='__main__':
    R=os.path.join(os.path.dirname(os.path.abspath(__file__)),'_render'); p=free()
    srv=subprocess.Popen(['python3','-m','http.server',str(p),'--bind','127.0.0.1','--directory',R],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(0.8)
    try:
        for t in sys.argv[1:]: print(t, run(t,p))
    finally: srv.terminate()
