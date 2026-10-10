# -*- coding: utf-8 -*-
"""Teste CDP de CD-05 (defeitos do verificador): canal E-mail autorizado sem e-mail é barrado como o WhatsApp;
o CNPJ da Fertisul é o mesmo no CD-05 e no PT-07 (Portal do parceiro), e esse CNPJ é recusado como parceiro novo."""
import sys, os, time, subprocess, json, re
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from cdp import Chrome
from journeys import free
R=os.path.join(os.path.dirname(os.path.abspath(__file__)),'_render'); p=free()
srv=subprocess.Popen(['python3','-m','http.server',str(p),'--bind','127.0.0.1','--directory',R],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(0.8)
c=Chrome(port=free()); J=c.js
SETV="""((sel,val)=>{const i=document.querySelector(sel); const P=i.tagName==='SELECT'?HTMLSelectElement.prototype:HTMLInputElement.prototype; Object.getOwnPropertyDescriptor(P,'value').set.call(i,val); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true}));})"""
BTN="""((t)=>{const b=[...document.querySelectorAll('aside[role=dialog] button')].find(b=>b.innerText.trim()===t); if(b){b.click(); return true;} return false;})"""
ROW=lambda nome: f"[...document.querySelectorAll('[role=table]')[0].querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.indexOf({json.dumps(nome)})>=0)"
FID=lambda k: J(f"(document.querySelector('aside[role=dialog] [id$=\"_{k}\"]')||{{}}).id")
CAN=lambda t: f"[...document.querySelectorAll('aside[role=dialog] label')].find(l=>l.innerText.trim()==={json.dumps(t)} && l.querySelector('input[type=checkbox]')).querySelector('input')"
AL=lambda: J("[...document.querySelectorAll('aside [role=alert]')].map(x=>x.innerText).join(' | ')")
LIN=lambda n: J(f"(()=>{{const r={ROW(n)}; return r?r.innerText.replace(/\\s+/g,' '):'';}})()")
ABERTO=lambda: J("!!document.querySelector('aside[role=dialog]')")
ok=[]
def chk(nome,cond,extra=''):
    ok.append(bool(cond)); print(('OK  ' if cond else 'FALHOU ')+nome+(' · '+str(extra) if extra else ''))
def novo(nome,doc,papel='Cliente',canais=()):
    J("[...document.querySelectorAll('button')].find(b=>b.innerText.trim()==='Cadastrar parceiro').click()"); time.sleep(.4)
    J(f"({SETV})('#{FID('nome')}',{json.dumps(nome)})"); J(f"({SETV})('#{FID('cnpj')}',{json.dumps(doc)})"); time.sleep(.2)
    J(f"{CAN(papel)}.click()"); time.sleep(.2)
    # cliente exige ao menos um produto de interesse (regra do Comercial, posterior a este teste): marca o primeiro, se o grupo existir
    if papel=='Cliente': J("(()=>{const l=[...document.querySelectorAll('aside[role=dialog] label')].find(l=>l.innerText.trim()==='Soja em grão'&&l.querySelector('input[type=checkbox]')); if(l&&!l.querySelector('input').checked) l.querySelector('input').click();})()")
    for cn in canais: J(f"{CAN(cn)}.click()")
    # "Homologado" só existe no formulário quando o papel é Fornecedor (antes o teste quebrava aqui, já na base 24da80b: o campo não existe para Cliente)
    fh=FID('homol')
    if fh: J(f"({SETV})('#{fh}','Não')"); time.sleep(.2)
    J(f"({BTN})('Salvar')"); time.sleep(.5)
def descartar():
    J(f"({BTN})('Cancelar')"); time.sleep(.2); J(f"({BTN})('Descartar alterações')"); time.sleep(.3)
try:
    c.size(1440,1100)
    # CNPJ da Fertisul no Portal do parceiro (PT-07)
    c.goto(f'http://127.0.0.1:{p}/PT-07.dc.html'); time.sleep(.4)
    pt=sorted(set(re.findall(r'12\.345\.678/\d{4}-\d{2}',J("document.body.innerText")+' '+J("[...document.querySelectorAll('input')].map(i=>i.value).join(' ')"))))
    chk('PT-07 mostra um CNPJ da Fertisul', len(pt)==1, pt)
    c.goto(f'http://127.0.0.1:{p}/CD-05.dc.html'); time.sleep(.6)
    chk('sem erro JS', J("window.__err||''")=='', J("window.__err||''"))
    t=LIN('Fertisul'); cd=re.findall(r'12\.345\.678/\d{4}-\d{2}',t)
    chk('CD-05 mostra o mesmo CNPJ da Fertisul que o PT-07', pt and cd==pt, f'CD-05 {cd} · PT-07 {pt}')
    # parceiro novo com o CNPJ da Fertisul é recusado
    novo('Dup',pt[0] if pt else '12.345.678/0001-95')
    al=AL(); chk('CNPJ da Fertisul recusado como parceiro novo', ABERTO() and 'CNPJ já cadastrado em Fertisul' in al, al)
    if ABERTO(): descartar()
    chk('nenhum parceiro Dup criado', LIN('Dup')=='', LIN('Dup'))
    # canal E-mail autorizado sem e-mail é barrado (como o WhatsApp)
    novo('Teste Email Vazio','11.222.333/0001-81',canais=['E-mail'])
    al=AL(); chk('canal E-mail sem e-mail barrado', ABERTO() and 'Informe o e-mail ou desmarque o canal.' in al, al)
    chk('erro junto ao campo e-mail', 'Informe o e-mail ou desmarque o canal.' in (J(f"(()=>{{const i=document.getElementById('{FID('email')}'); let n=i; for(let k=0;k<4&&n;k++){{ n=n.parentElement; const a=n&&n.querySelector('[role=alert]'); if(a) return a.innerText; }} return ''; }})()") or ''))
    if ABERTO(): descartar()
    chk('nenhum parceiro salvo com e-mail autorizado vazio', LIN('Teste Email Vazio')=='', LIN('Teste Email Vazio'))
    novo('Teste Whats Vazio','11.222.333/0001-81',canais=['WhatsApp'])
    al=AL(); chk('canal WhatsApp sem número barrado', ABERTO() and 'Informe o WhatsApp ou desmarque o canal.' in al, al)
    if ABERTO():
        # corrigir: preencher o número salva
        J(f"({SETV})('#{FID('whats')}','65 99123-4567')"); time.sleep(.2); J(f"({BTN})('Salvar')"); time.sleep(.5)
        chk('com o número preenchido salva', not ABERTO() and '65 99123-4567' in LIN('Teste Whats Vazio'), LIN('Teste Whats Vazio'))
    # e-mail autorizado e preenchido salva
    novo('Teste Email Cheio','11.444.777/0001-61',canais=['E-mail'])
    if ABERTO():
        J(f"({SETV})('#{FID('email')}','contato@teste.com.br')"); time.sleep(.2); J(f"({BTN})('Salvar')"); time.sleep(.5)
    chk('com o e-mail preenchido salva', not ABERTO() and 'contato@teste.com.br' in LIN('Teste Email Cheio'), LIN('Teste Email Cheio'))
    # homologar sem e-mail mantém a mensagem própria da homologação
    J(f"(()=>{{const r={ROW('Química Centro-Oeste')}; (r.querySelector('[role=cell] span')||r).click();}})()"); time.sleep(.4)
    J(f"{CAN('E-mail')}.click()"); J(f"({SETV})('#{FID('homol')}','Sim')"); time.sleep(.2); J(f"({BTN})('Salvar')"); time.sleep(.4)
    al=AL(); chk('homologar sem e-mail pede o e-mail da cotação', 'Informe o e-mail: a cotação é enviada por ele.' in al, al)
    if ABERTO(): descartar()
finally:
    c.close(); srv.terminate()
print('RESULTADO:', 'OK' if all(ok) else 'FALHOU', f'{sum(ok)}/{len(ok)}')
