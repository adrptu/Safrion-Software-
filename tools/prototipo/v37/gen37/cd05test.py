# -*- coding: utf-8 -*-
"""Teste CDP de CD-05 (Parceiros e fornecedores): abrir fornecedor pela linha, marcar grupo, e-mail inválido mostra erro no campo
(preservando o digitado), corrigir, salvar; a linha e a cobertura por grupo refletem o salvo; não homologado não recebe cotação;
CPF (11) ou CNPJ (14), contato e canais autorizados: homologar exige contato e e-mail autorizado; canal sem autorização aparece na linha.
v3.9 (papéis): grupos, homologação e cobertura só no filtro Fornecedores; parceiro de crédito não mostra campos de fornecedor;
prestador exige as operações que presta."""
import sys, os, time, subprocess, json
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
ok=[]
def chk(nome,cond,extra=''):
    ok.append(bool(cond)); print(('OK  ' if cond else 'FALHOU ')+nome+(' · '+str(extra) if extra else ''))
FIL=lambda t: J(f"[...document.querySelectorAll('[role=group][aria-label=\"Filtrar por papel\"] button')].find(b=>b.innerText.trim().startsWith({json.dumps(t)})).click()") or time.sleep(.3)
def _aba(t): J(f"(()=>{{const b=[...document.querySelectorAll('[role=tab]')].find(b=>b.innerText.replace(/\\s+/g,' ').trim().startsWith({json.dumps(t)})); if(b) b.click();}})()"); time.sleep(.35)
def cob(g):
    """cobertura por grupo (layout de 01/10: aba "Cobertura de cotação" no mesmo bloco); lê e volta à aba Parceiros."""
    _aba('Cobertura'); r=J(f"(()=>{{const t=document.querySelectorAll('[role=table]')[0]; if(!t) return null; const r=[...t.querySelectorAll('[role=row]')].find(r=>r.innerText.split('\\n')[0].trim()==={json.dumps(g)}); return r?r.innerText.replace(/\\s+/g,' '):null;}})()"); _aba('Parceiros'); return r
try:
    c.size(1440,1100); c.goto(f'http://127.0.0.1:{p}/CD-05.dc.html'); time.sleep(.6)
    chk('sem erro JS', J("window.__err||''")=='', J("window.__err||''"))
    FIL('Fornecedores')
    chk('não homologado: não recebe cotação', J("document.querySelectorAll('[role=table]')[0].innerText.indexOf('não recebe cotação')>=0"))
    antes=cob('Combustível'); chk('Combustível começa sem fornecedor', antes and 'Sem fornecedor' in antes, antes)
    # 1 · abrir fornecedor pela linha
    J(f"(()=>{{const r={ROW('Agro Norte')}; (r.querySelector('[role=cell] span')||r).click();}})()"); time.sleep(.4)
    chk('abre formulário lateral', J("!!document.querySelector('aside[role=dialog]')"), J("(document.querySelector('aside[role=dialog] h2')||{}).innerText"))
    chk('grupos já marcados', J("[...document.querySelectorAll('aside[role=dialog] label')].filter(l=>l.querySelector('input[type=checkbox]:checked')).map(l=>l.innerText.trim()).join(',')"))
    # 2 · marcar grupo Combustível
    J("[...document.querySelectorAll('aside[role=dialog] label')].find(l=>l.innerText.trim()==='Combustível' && l.querySelector('input[type=checkbox]')).querySelector('input').click()"); time.sleep(.3)
    chk('grupo Combustível marcado', J("[...document.querySelectorAll('aside[role=dialog] label')].find(l=>l.innerText.trim()==='Combustível').querySelector('input').checked"))
    # 3 · e-mail inválido → erro no campo, preenchido preservado
    em=FID('email'); J(f"({SETV})('#{em}','vendas@agronorte')"); time.sleep(.2); J(f"({BTN})('Salvar')"); time.sleep(.4)
    err=J(f"(()=>{{const i=document.getElementById('{em}'); let n=i; for(let k=0;k<4&&n;k++){{ n=n.parentElement; const a=n&&n.querySelector('[role=alert]'); if(a) return a.innerText; }} return ''; }})()")
    chk('erro junto ao campo e-mail', 'E-mail inválido' in (err or ''), err)
    chk('formulário continua aberto', J("!!document.querySelector('aside[role=dialog]')"))
    chk('digitado preservado', J(f"document.getElementById('{em}').value")=='vendas@agronorte')
    chk('grupo marcado preservado', J("[...document.querySelectorAll('aside[role=dialog] label')].find(l=>l.innerText.trim()==='Combustível').querySelector('input').checked"))
    # WhatsApp inválido também
    wa=FID('whats'); J(f"({SETV})('#{wa}','9999')"); time.sleep(.2); J(f"({BTN})('Salvar')"); time.sleep(.3)
    chk('WhatsApp inválido barrado', J("document.body.innerText.indexOf('Informe DDD e número')>=0"))
    # 4 · corrigir e salvar
    J(f"({SETV})('#{em}','vendas@agronorte.com.br')"); J(f"({SETV})('#{wa}','65 99888-1122')"); time.sleep(.2); J(f"({BTN})('Salvar')"); time.sleep(.5)
    chk('salvou e fechou', J("!document.querySelector('aside[role=dialog]')"))
    chk('aviso de salvo', J("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).join(' ')"))
    linha=J(f"{ROW('Agro Norte')}.innerText.replace(/\\s+/g,' ')"); J(f"(()=>{{const r={ROW('Agro Norte')}; (r.querySelector('[role=cell] span')||r).click();}})()"); time.sleep(.4)
    em2=J(f"(document.getElementById('{FID('email')}')||{{}}).value"); J(f"({BTN})('Cancelar')"); time.sleep(.2)
    chk('linha atualizada (grupos na linha; e-mail salvo no painel)', em2=='vendas@agronorte.com.br' and 'Combustível' in linha, [linha,em2])
    # TABELAS-FOCO (06/10/2026): número na coluna Fornecedores e estado em chip ("Sem concorrência" no lugar de "Só 1")
    depois=cob('Combustível'); chk('cobertura de Combustível recalculada', depois and depois.startswith('Combustível 1 ') and 'Sem concorrência' in depois, depois)
    # 5 · desomologar: fornecedor sai da cobertura
    J(f"(()=>{{const r={ROW('Agro Norte')}; (r.querySelector('[role=cell] span')||r).click();}})()"); time.sleep(.4)
    J(f"({SETV})('#{FID('homol')}','Não')"); time.sleep(.2); J(f"({BTN})('Salvar')"); time.sleep(.5)
    st=J("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).join(' ')"); chk('aviso: não recebe cotação', 'não recebe cotação' in st, st)
    chk('Combustível volta a sem fornecedor', 'Sem fornecedor' in (cob('Combustível') or ''), cob('Combustível'))
    # 6 · parceiro de crédito não mostra homologação; ao marcar Fornecedor, homologar sem grupo e sem e-mail é barrado
    FIL('Todos')
    J(f"(()=>{{const r={ROW('Banco Terra')}; (r.querySelector('[role=cell] span')||r).click();}})()"); time.sleep(.4)
    labs=J("[...document.querySelectorAll('aside[role=dialog] label[for]')].map(l=>l.innerText.trim())")
    chk('crédito sem campos de fornecedor', 'Linhas de crédito' in labs and 'Homologado' not in labs and 'Grupos homologados' not in labs, labs)
    J("[...document.querySelectorAll('aside[role=dialog] label')].find(l=>l.innerText.trim()==='Fornecedor' && l.querySelector('input[type=checkbox]')).querySelector('input').click()"); time.sleep(.3)
    J(f"({SETV})('#{FID('email')}','')"); J(f"({SETV})('#{FID('homol')}','Sim')"); time.sleep(.2); J(f"({BTN})('Salvar')"); time.sleep(.3)
    al=J("[...document.querySelectorAll('aside [role=alert]')].map(x=>x.innerText).join(' | ')")
    chk('homologar exige grupo e e-mail', 'grupo' in al and 'e-mail' in al, al)
    J(f"({BTN})('Cancelar')"); time.sleep(.2); J(f"({BTN})('Descartar alterações')"); time.sleep(.2)
    chk('cancelar preserva e fecha', J("!document.querySelector('aside[role=dialog]')"))
    # 7 · CPF ou CNPJ, contato e canais autorizados
    AL=lambda: J("[...document.querySelectorAll('aside [role=alert]')].map(x=>x.innerText).join(' | ')")
    CAN=lambda t: f"[...document.querySelectorAll('aside[role=dialog] label')].find(l=>l.innerText.trim()==={json.dumps(t)} && l.querySelector('input[type=checkbox]')).querySelector('input')"
    LIN=lambda n: J(f"(()=>{{const r={ROW(n)}; return r?r.innerText.replace(/\\s+/g,' '):'';}})()")
    chk('coluna Parceiro · CPF/CNPJ', J("document.querySelectorAll('[role=table]')[0].innerText.indexOf('CPF/CNPJ')>=0"))
    t=LIN('Sementes Vale'); chk('WhatsApp sem autorização mostra o aviso', '65 99555-6677 não autorizado' in t, t)
    t=LIN('Fertisul'); chk('canal autorizado sem aviso', 'não autorizado' not in t, t)
    t=LIN('Adão Ferreira'); chk('pessoa física com CPF', '123.456.789-09' in t, t)
    FIL('Fornecedores')
    J(f"(()=>{{const r={ROW('Fertisul')}; (r.querySelector('[role=cell] span')||r).click();}})()"); time.sleep(.4)
    labs=J("[...document.querySelectorAll('aside[role=dialog] label[for]')].map(l=>l.innerText.trim())")
    chk('formulário tem CPF ou CNPJ, contato e canais', all(x in labs for x in ['CPF ou CNPJ','Nome do contato','Canais autorizados']), labs)
    chk('contato preenchido', J(f"document.getElementById('{FID('contato')}').value"))
    chk('canais do cadastro marcados', J(f"{CAN('E-mail')}.checked && {CAN('WhatsApp')}.checked"))
    J(f"{CAN('E-mail')}.click()"); time.sleep(.2); J(f"({SETV})('#{FID('contato')}','')"); time.sleep(.2); J(f"({BTN})('Salvar')"); time.sleep(.4)
    al=AL(); chk('homologar exige e-mail autorizado e contato', 'Marque E-mail' in al and 'nome do contato' in al, al)
    chk('cobertura não muda antes de salvar', 'Fertilizantes 3' in (cob('Fertilizantes') or ''), cob('Fertilizantes'))
    J(f"({BTN})('Cancelar')"); time.sleep(.2); J(f"({BTN})('Descartar alterações')"); time.sleep(.2)
    # novo parceiro pessoa física: 12 dígitos barra, 11 dígitos salva, CPF repetido barra
    FIL('Todos')
    J("[...document.querySelectorAll('button')].find(b=>b.innerText.trim()==='Criar parceiro').click()"); time.sleep(.4)
    J(f"({SETV})('#{FID('nome')}','Joana Prado')"); J(f"({SETV})('#{FID('cnpj')}','987.654.321-001')"); time.sleep(.2)
    J(f"{CAN('Prestador')}.click()"); time.sleep(.2); J(f"({BTN})('Salvar')"); time.sleep(.4)
    al=AL(); chk('12 dígitos barrado', 'Informe CPF (11 dígitos) ou CNPJ (14 dígitos).' in al, al)
    J(f"({SETV})('#{FID('cnpj')}','123.456.789-09')"); time.sleep(.2); J(f"({BTN})('Salvar')"); time.sleep(.4)
    al=AL(); chk('CPF repetido barrado', 'CPF já cadastrado em Adão Ferreira' in al, al)
    J(f"{CAN('WhatsApp')}.click()"); J(f"({SETV})('#{FID('cnpj')}','987.654.321-00')"); time.sleep(.2); J(f"({BTN})('Salvar')"); time.sleep(.4)
    al=AL(); chk('canal WhatsApp sem número barrado', 'Informe o WhatsApp ou desmarque o canal.' in al, al)
    J(f"{CAN('WhatsApp')}.click()"); J(f"{CAN('Poda')}.click()"); time.sleep(.2); J(f"({BTN})('Salvar')"); time.sleep(.5)
    chk('pessoa física com CPF de 11 dígitos salva', J("!document.querySelector('aside[role=dialog]')") and '987.654.321-00' in LIN('Joana Prado'), LIN('Joana Prado'))
finally:
    c.close(); srv.terminate()
print('RESULTADO:', 'OK' if all(ok) else 'FALHOU', f'{sum(ok)}/{len(ok)}')
