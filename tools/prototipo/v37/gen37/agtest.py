# -*- coding: utf-8 -*-
"""Teste CDP da área Agronomia: decisão da v3 (AG-04det), cadeia navegável, novo registro (AG-01/AG-03), correção do K (AG-02), limiar (AG-05)."""
import sys, os, time, subprocess, json
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from cdp import Chrome
from journeys import free
R=os.path.join(os.path.dirname(os.path.abspath(__file__)),'_render'); p=free()
srv=subprocess.Popen(['python3','-m','http.server',str(p),'--bind','127.0.0.1','--directory',R],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(0.8)
c=None; ok=[]
CLK="""((t,root)=>{const r=root?document.querySelector(root):document; const n=s=>(s||'').replace(/\\s+/g,' ').trim(); const els=[...r.querySelectorAll('button,a')]; const e=els.find(x=>n(x.innerText)===t)||els.find(x=>n(x.innerText).startsWith(t)); if(!e) return 'NÃO ACHEI: '+t; e.click(); return 'ok';})"""
SETV="""((sel,val)=>{const i=document.querySelector(sel); const P=i.tagName==='SELECT'?HTMLSelectElement.prototype:(i.tagName==='TEXTAREA'?HTMLTextAreaElement.prototype:HTMLInputElement.prototype); Object.getOwnPropertyDescriptor(P,'value').set.call(i,val); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true}));})"""
def chk(nome,cond,extra=''):
    ok.append(bool(cond)); print(('OK  ' if cond else 'FALHOU ')+nome, extra)
try:
    c=Chrome(port=free()); J=c.js
    body=lambda: J("document.body.innerText")
    clk=lambda t,root=None: (J(f"({CLK})({json.dumps(t)},{json.dumps(root)})"), time.sleep(.45))[0]
    def fill(label,val):
        fid=J(f"(()=>{{const l=[...document.querySelectorAll('aside[role=dialog] label')].find(l=>l.innerText.trim()==={json.dumps(label)}); return l?l.getAttribute('for'):null;}})()")
        J(f"({SETV})('#'+CSS.escape({json.dumps(fid)}),{json.dumps(val)})"); time.sleep(.2); return fid
    # ---- AG-04det: cadeia e decisão da v3
    c.size(1440,1000); c.goto(f'http://127.0.0.1:{p}/AG-04det.dc.html'); time.sleep(.6)
    links=J("[...document.querySelectorAll('nav[aria-label=\"Cadeia da demonstração\"] a')].map(a=>a.getAttribute('href'))")
    chk('cadeia com 5 elos navegáveis + próxima ação', len(links)==6 and 'AG-01det.dc.html' in links and 'AG-03det.dc.html' in links and 'CA-01x-os0420.dc.html' in links, links)
    chk('v3 aguardando decisão', 'Aguardando decisão' in body())
    clk('Rejeitar v3'); chk('rejeitar pede confirmação', 'Rejeitar a v3?' in body())
    clk('Voltar'); chk('voltar cancela sem decidir', 'Aguardando decisão' in body() and 'Recibo' not in body())
    clk('Aprovar v3 do saldo'); b=body()
    chk('aprovar gera recibo', 'Recibo · v3 aprovada' in b and 'R$ 26.333,28' in b)
    chk('v3 aprovada só no saldo', 'Aprovada · vale para o saldo de 70 ha' in b and 'Em uso nos 30 ha realizados' in b)
    chk('O.S. segue impedida aguardando prontidão', 'Saldo aguarda prontidão' in b and 'Impedida · OM-0233' in b)
    chk('primário vira próxima pendência', J("[...document.querySelectorAll('header a')].some(a=>a.innerText.includes('Revalidar prontidão no PCP') && a.getAttribute('href')==='PL-05.dc.html')"))
    chk('botões de decisão somem', 'Rejeitar v3' not in body())
    # ---- AG-01: programar vistoria pela barra da tabela
    c.goto(f'http://127.0.0.1:{p}/AG-01.dc.html'); time.sleep(.6)
    clk('+ Programar vistoria'); chk('formulário de nova vistoria', J("!!document.querySelector('aside[role=dialog]')"))
    fill('Data','2026-09-29'); clk('Salvar','aside[role=dialog]')
    b=body(); chk('VIS-018 criada como Programada', 'VIS-018' in b and 'Programada' in b, J("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).join('|')"))
    # editar VIS-014 pela linha (responsável)
    J("(()=>{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>/VIS-014/.test(r.innerText)); r.querySelector('[role=cell]').click();})()"); time.sleep(.4)
    fill('Estádio','R3'); clk('Salvar','aside[role=dialog]')
    chk('VIS-014 salva com estádio atualizado', J("[...document.querySelectorAll('[role=row].g2ed')].find(r=>/VIS-014/.test(r.innerText)).innerText.includes('R3')"))
    # ---- AG-02: corrigir unidade do K
    c.goto(f'http://127.0.0.1:{p}/AG-02.dc.html'); time.sleep(.6)
    J("(()=>{const t=document.querySelectorAll('[role=table]')[1]; const r=[...t.querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.trim().startsWith('K')); r.querySelector('[role=cell]').click();})()"); time.sleep(.4)
    fill('Unidade','g/kg'); clk('Salvar','aside[role=dialog]')
    b=body(); chk('K corrigido e LAU-2048 volta à validação', 'mapeamento salvo · aguarda validação humana' in b and 'sem unidade' not in b.split('Original ao lado')[1])
    # ---- AG-03: criar diagnóstico
    c.goto(f'http://127.0.0.1:{p}/AG-03.dc.html'); time.sleep(.6)
    clk('+ Criar diagnóstico'); fill('Evidências (vistoria · laudo)','VIS-017 · PLA-104'); fill('Hipótese · causa','Daninhas resistentes na bordadura')
    fill('Meta','plantio limpo'); fill('Ação proposta','Dessecação sequencial'); clk('Salvar','aside[role=dialog]')
    chk('DIA-011 criado em rascunho', 'DIA-011' in body() and 'Rascunho' in body())
    # ---- AG-05: anexar referência ao limiar
    c.goto(f'http://127.0.0.1:{p}/AG-05.dc.html'); time.sleep(.6)
    J("(()=>{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>/Limiar mosca-branca/.test(r.innerText)); r.querySelector('[role=cell]').click();})()"); time.sleep(.4)
    fill('Referência','Embrapa Café · boletim 2025'); fill('Unidade · gatilhos','adultos/folha'); fill('Validade · revisão','30/06/2027'); fill('Escopo (cultura · região · fase)','Café · Cerrado Mineiro')
    clk('Salvar','aside[role=dialog]')
    chk('limiar passa a Em validação (segue inativo)', 'segue inativo até validar' in body())
    # ---- AG-01det e AG-03det: caminho de volta
    c.goto(f'http://127.0.0.1:{p}/AG-03det.dc.html'); time.sleep(.5)
    chk('DIA-007 aponta para VIS-011 e REC-014', J("['AG-01det.dc.html','AG-04det.dc.html'].every(h=>!!document.querySelector('a[href=\"'+h+'\"]'))"))
finally:
    try:
        if c: c.close()
    finally: srv.terminate()
print('RESULTADO', f'{sum(ok)}/{len(ok)}')
