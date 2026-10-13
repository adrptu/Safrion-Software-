# -*- coding: utf-8 -*-
"""Teste CDP de CD-05 com papéis (v3.9): filtros por papel com contagem; cadastrar cliente; cadastrar parceiro de crédito;
CNPJ já cadastrado → aviso ao digitar e "Abrir e ativar papel" sem duplicar; suspender com motivo obrigatório (sai da cotação).
15 verificações. Uso: python3 cadp_test.py (serve _render/ e abre o Chrome headless)."""
import sys, os, time, subprocess, json
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from cdp import Chrome
from journeys import free
R=os.path.join(os.path.dirname(os.path.abspath(__file__)),'_render'); p=free()
srv=subprocess.Popen(['python3','-m','http.server',str(p),'--bind','127.0.0.1','--directory',R],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(0.8)
c=Chrome(port=free()); J=c.js
SETV="""((sel,val)=>{const i=document.querySelector(sel); const P=i.tagName==='SELECT'?HTMLSelectElement.prototype:HTMLInputElement.prototype; Object.getOwnPropertyDescriptor(P,'value').set.call(i,val); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true}));})"""
SETK=lambda k,val: J(f"({SETV})('#fx_g_forn_{k}',{json.dumps(val)})")
BTN=lambda t: J(f"(()=>{{const b=[...document.querySelectorAll('aside[role=dialog] button')].find(b=>b.innerText.trim()==={json.dumps(t)}); if(b){{b.click(); return true;}} return false;}})()") or time.sleep(.4)
CAN=lambda t: J(f"[...document.querySelectorAll('aside[role=dialog] label')].find(l=>l.innerText.trim()==={json.dumps(t)} && l.querySelector('input[type=checkbox]')).querySelector('input').click()") or time.sleep(.2)
ON=lambda t: J(f"[...document.querySelectorAll('aside[role=dialog] label')].find(l=>l.innerText.trim()==={json.dumps(t)} && l.querySelector('input[type=checkbox]')).querySelector('input').checked")
AL=lambda: J("[...document.querySelectorAll('aside [role=alert]')].map(x=>x.innerText).join(' | ')")
LABS=lambda: J("[...document.querySelectorAll('aside[role=dialog] label[for]')].map(l=>l.innerText.trim())")
ST=lambda: J("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).join(' | ')")
ABERTO=lambda: J("!!document.querySelector('aside[role=dialog]')")
ROWS="[...document.querySelectorAll('[role=table]')[0].querySelectorAll('[role=row].g2ed')]"
LIN=lambda n: J(f"(()=>{{const r={ROWS}.find(r=>r.innerText.indexOf({json.dumps(n)})>=0); return r?r.innerText.replace(/\\s+/g,' '):'';}})()")
ABRE=lambda n: J(f"(()=>{{const r={ROWS}.find(r=>r.innerText.indexOf({json.dumps(n)})>=0); (r.querySelector('[role=cell] span')||r).click();}})()") or time.sleep(.4)
FILS=lambda: J("[...document.querySelectorAll('[role=group][aria-label=\"Filtrar por papel\"] button')].map(b=>b.innerText.replace(/\\s+/g,' ').trim()).join(' | ')")
FIL=lambda t: J(f"[...document.querySelectorAll('[role=group][aria-label=\"Filtrar por papel\"] button')].find(b=>b.innerText.trim().startsWith({json.dumps(t)})).click()") or time.sleep(.3)
NOVO=lambda: J("[...document.querySelectorAll('main button')].find(b=>b.innerText.trim()==='Cadastrar parceiro').click()") or time.sleep(.4)   # a ação fica no bloco (01/10)
def _aba(t): J(f"(()=>{{const b=[...document.querySelectorAll('[role=tab]')].find(b=>b.innerText.replace(/\\s+/g,' ').trim().startsWith({json.dumps(t)})); if(b) b.click();}})()"); time.sleep(.35)
def cob(g):
    """cobertura por grupo (layout de 01/10: aba "Cobertura de cotação" no mesmo bloco); lê e volta à aba Parceiros."""
    _aba('Cobertura'); r=J(f"(()=>{{const t=document.querySelectorAll('[role=table]')[0]; if(!t) return null; const r=[...t.querySelectorAll('[role=row]')].find(r=>r.innerText.split('\\n')[0].trim()==={json.dumps(g)}); return r?r.innerText.replace(/\\s+/g,' '):null;}})()"); _aba('Parceiros'); return r
ok=[]
def chk(nome,cond,extra=''):
    ok.append(bool(cond)); print(('OK  ' if cond else 'FALHOU ')+nome+(' · '+str(extra) if extra else ''))
try:
    c.size(1440,1100); c.goto(f'http://127.0.0.1:{p}/CD-05.dc.html'); time.sleep(.5)
    hd=J("document.querySelector('h1').parentElement.innerText.replace(/\\s+/g,' ')")
    chk('1 sem erro JS e estado do cabeçalho calculado', J("window.__err||''")=='' and '2 grupos sem fornecedor · 1 limite vencido' in hd, hd)
    f0=FILS(); chk('2 filtros por papel com contagem', f0=='Todos 20 | Fornecedores 8 | Clientes 7 | Parceiros de crédito 3 | Transportadores 2 | Prestadores 1', f0)
    FIL('Clientes')
    ls=J(f"{ROWS}.map(r=>r.innerText.replace(/\\s+/g,' '))")
    chk('3 filtro Clientes: só clientes, com limite, sem cobertura de cotação', len(ls)==7 and all('Cliente' in x for x in ls) and all('Limite' in x for x in ls)
        and J("document.querySelectorAll('[role=table]').length")==1, ls)
    # ---- cadastrar cliente ----
    NOVO(); SETK('cnpj','41.552.310/0001-04'); SETK('nome','Hortifruti Serra Azul'); CAN('Cliente')
    lb=LABS()
    chk('4 cliente: começa pelo CPF/CNPJ e mostra só a seção Cliente', lb[0]=='CPF ou CNPJ' and all(x in lb for x in ['Produtos de interesse','Local e horário de entrega','Condição de pagamento','Limite de crédito comercial','Validade da análise de crédito'])
        and 'Grupos homologados' not in lb and 'Linhas de crédito' not in lb, lb)
    SETK('lim','50.000'); time.sleep(.2); BTN('Salvar')
    al=AL(); chk('5 cliente: produtos e validade do limite obrigatórios', ABERTO() and 'Escolha ao menos uma opção.' in al and 'Informe a validade da análise de crédito.' in al, al)
    CAN('Mamão Formosa classe A'); SETK('limv','2027-03-31'); SETK('entrega','CD Salvador/BA · seg–sex 05–10h'); time.sleep(.2); BTN('Salvar'); time.sleep(.2)
    t=LIN('Hortifruti Serra Azul')
    # TABELAS-FOCO (06/10/2026): limite, validade e situação do papel em colunas próprias (antes "Limite R$ 50.000 até 31/03/2027" numa célula só);
    # revisão TABR (09/10/2026, A1): a situação do papel vem logo depois do parceiro
    chk('6 cliente salvo com limite e contagem', not ABERTO() and t.startswith('Hortifruti Serra Azul Limite vigente') and 'R$ 50.000 31/03/2027' in t and 'Clientes 8' in FILS(), f'{t} · {ST()}')
    # ---- cadastrar parceiro de crédito ----
    FIL('Parceiros de crédito'); NOVO(); SETK('cnpj','52.119.804/0001-08'); SETK('nome','Cooperativa Cerrado Crédito'); CAN('Parceiro de crédito')
    lb=LABS()
    chk('7 crédito: seção com linhas, garantias e gerente com e-mail e telefone', all(x in lb for x in ['Linhas de crédito','Garantias aceitas','Gerente do crédito','E-mail do gerente','Telefone do gerente'])
        and 'Produtos de interesse' not in lb and 'Homologado' not in lb, lb)
    BTN('Salvar'); al=AL()
    chk('8 crédito: linhas e gerente obrigatórios', ABERTO() and 'Escolha ao menos uma opção.' in al and 'Informe gerente do crédito.' in al, al)
    CAN('Custeio'); CAN('Penhor de safra'); SETK('ger','Luís Prado'); SETK('ger_email','luis.prado@cerradocredito.coop.br'); SETK('ger_tel','64 99111-2233'); time.sleep(.2); BTN('Salvar'); time.sleep(.2)
    t=LIN('Cooperativa Cerrado Crédito')
    chk('9 crédito salvo: linhas e garantias na linha; filtro conta 4', not ABERTO() and 'Custeio' in t and 'Penhor de safra' in t and 'Parceiros de crédito 4' in FILS(), f'{t} · {AL()}')
    # ---- CNPJ já cadastrado: aviso ao digitar e abrir o existente ativando o papel ----
    FIL('Todos'); NOVO(); CAN('Fornecedor'); SETK('cnpj','98.765.432/0001-98'); time.sleep(.2)
    av=J("[...document.querySelectorAll('aside [role=status]')].map(x=>x.innerText.replace(/\\s+/g,' ')).join(' | ')")
    BTN('Salvar'); al=AL()
    chk('10 CNPJ duplicado: aviso ao digitar e salvar barrado', 'Já cadastrado: Coop Grão Sul (Cliente)' in av and 'Abrir e ativar papel' in av and 'CNPJ já cadastrado em Coop Grão Sul' in al, f'{av} · {al}')
    BTN('Abrir e ativar papel')
    tit=J("(document.querySelector('aside[role=dialog] h2')||{}).innerText"); lb=LABS()
    chk('11 abre Coop Grão Sul com Fornecedor marcado e a seção Fornecedor', tit=='Parceiro · Coop Grão Sul' and ON('Fornecedor') and ON('Cliente') and 'Grupos homologados' in lb and 'Produtos de interesse' in lb, f'{tit} · {lb}')
    BTN('Salvar'); time.sleep(.2)
    t=LIN('Coop Grão Sul'); n=J(f"{ROWS}.filter(r=>r.innerText.indexOf('Coop Grão Sul')>=0).length"); f1=FILS()
    chk('12 salvo sem duplicar: Coop Grão Sul com 2 papéis, total 22, Fornecedores 9', not ABERTO() and 'Fornecedor' in t and 'Cliente' in t and n==1 and 'Todos 22' in f1 and 'Fornecedores 9' in f1, f'{t} · {f1}')
    # ---- suspender com motivo ----
    ABRE('Sementes Vale'); BTN('Suspender parceiro'); BTN('Salvar')
    al=J("(()=>{const i=document.getElementById('fx_g_forn_motivo'); let n=i; for(let k=0;k<4&&n;k++){ n=n.parentElement; const a=n&&n.querySelector('[role=alert]'); if(a) return a.innerText; } return ''; })()")
    chk('13 suspender sem motivo é barrado junto ao campo', ABERTO() and 'Motivo da suspensão' in LABS() and al=='Informe motivo da suspensão.', al)
    SETK('motivo','Documentação fiscal vencida'); time.sleep(.2); BTN('Salvar'); time.sleep(.2)
    st=ST(); t=LIN('Sementes Vale')
    chk('14 suspenso com motivo: aviso e situação na linha', not ABERTO() and 'Suspenso: Sementes Vale sai de cotação' in st and 'Suspenso' in t and 'Documentação fiscal vencida' in t, f'{st} · {t}')
    FIL('Fornecedores'); cs=cob('Sementes'); ABRE('Sementes Vale')
    sub=J("document.querySelector('aside[role=dialog]').innerText"); re_=J("[...document.querySelectorAll('aside[role=dialog] button')].some(b=>b.innerText.trim()==='Reativar parceiro')")
    # TABELAS-FOCO (06/10/2026): a cobertura mostra o número na coluna Fornecedores e o estado em chip ("Sem concorrência" no lugar de "Só 1")
    chk('15 suspenso sai da cobertura (Sementes: só 1) e abre com Reativar parceiro', cs and cs.startswith('Sementes 1 ') and 'Sem concorrência' in cs and 'Suspenso: fora de cotação' in sub and re_, f'{cs} · reativar={re_}')
finally:
    c.close(); srv.terminate()
print('RESULTADO:', 'OK' if all(ok) else 'FALHOU', f'{sum(ok)}/{len(ok)}')
