# -*- coding: utf-8 -*-
"""Teste CDP da área Agronomia: REC-014 com a v3 (KCl) aprovada e o TS sem registro travado no saldo (AG-04det), cadeia navegável, programar vistoria e painel
(AG-01, base do MIP), novo diagnóstico com numeração única (AG-03), correção do K (AG-02), limiar (AG-05)."""
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
    # ---- AG-04det: cadeia, v3 aprovada no saldo (igual ao Mapa e à O.S.) e conferência Agrofit do TS
    c.size(1440,1000); c.goto(f'http://127.0.0.1:{p}/Main.dc.html'); J("localStorage.removeItem('talhao-os-mip-v1'); localStorage.removeItem('talhao-os-cenario-v1'); sessionStorage.clear()")
    c.goto(f'http://127.0.0.1:{p}/AG-04det.dc.html'); time.sleep(.6)
    links=J("[...document.querySelectorAll('nav[aria-label=\"Cadeia da demonstração\"] a')].map(a=>a.getAttribute('href'))")
    chk('cadeia com 5 elos navegáveis (o próximo passo fica só no primário)', len(links)==5 and 'AG-01.dc.html#VIS-011' in links and 'AG-03det.dc.html' in links and 'OS.dc.html#OS-0420' in links, links)
    b=body()
    chk('v3: KCl aprovado, TS travado (sem registro), sem botões de decisão', 'KCl aprovado por Ana' in b and 'TS travado · sem registro' in b and 'Em uso nos 30 ha realizados' in b and 'Aprovar v3' not in b and 'Rejeitar v3' not in b)
    chk('TS sem registro para nematoide-de-cisto, com a ficha e a alternativa registrada', 'Sem registro p/ nematoide-de-cisto' in b and J("['AG-07.dc.html#abamectina-500-fs','AG-07.dc.html#pasteuria-nishizawae-fs'].every(h=>!!document.querySelector('a[href=\"'+h+'\"]'))"))
    chk('primário cria a v4 com TS registrado (trava legal no saldo)', J("[...document.querySelectorAll('header a, header button')].some(a=>a.innerText.includes('Criar v4 com TS registrado'))") and 'Saldo de 70 ha travado' in b)
    chk('O.S. segue impedida pela máquina', 'Impedida · OM-0233' in b)
    # ---- AG-01: programar vistoria (talhão → alvo do protocolo → data → responsável) e painel da vistoria
    J("sessionStorage.setItem('mapa-ctx',JSON.stringify({mf_faz:'Santa Rita'}))")   # vindo do Mapa na Santa Rita
    c.goto(f'http://127.0.0.1:{p}/AG-01.dc.html'); time.sleep(.6)
    clk('Programar vistoria'); chk('formulário de nova vistoria', J("!!document.querySelector('aside[aria-label=\"Programar vistoria\"]')"))
    J(f"({SETV})('#pv_tal','T2')"); time.sleep(.3)
    alvos=J("[...document.querySelectorAll('aside[aria-label=\"Programar vistoria\"] select')][1].innerText")
    chk('alvo só do protocolo da cultura (T2 soja pré-plantio)', 'Nematoide-de-cisto' in alvos and 'Daninhas pré-plantio' in alvos and 'Mosca-branca' not in alvos, alvos)
    clk('Programar vistoria','aside[aria-label="Programar vistoria"]')
    chk('não duplica talhão × alvo aberto (VIS-017)', 'VIS-017 já está aberta para T2 × daninhas pré-plantio' in body())
    J(f"({SETV})('aside[aria-label=\"Programar vistoria\"] select[aria-label=\"Alvo\"]','soja-nematoide')"); time.sleep(.3)
    clk('Programar vistoria','aside[aria-label="Programar vistoria"]'); b=body()
    chk('VIS-018 programada (nematoide, 20 pontos) e painel aberto em "Coletar no app"', 'VIS-018 · Nematoide-de-cisto · T2' in b and 'Coletar no app' in b and '20 pontos' in b, J("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).join('|')"))
    c.goto(f'http://127.0.0.1:{p}/AG-01.dc.html'); time.sleep(.6)
    J("(()=>{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>/VIS-014/.test(r.innerText)); r.querySelector('[role=cell]').click();})()"); time.sleep(.5)
    chk('VIS-014 abre o painel (não o formulário) com "Continuar coleta" no app', J("(()=>{const a=document.querySelector('aside[role=dialog]'); return !!a && a.innerText.startsWith('VIS-014') && !!a.querySelector('a[href=\"MB-06.dc.html#VIS-014\"]');})()"))
    # ---- AG-02: corrigir unidade do K
    c.goto(f'http://127.0.0.1:{p}/AG-02.dc.html'); time.sleep(.6)
    J("(()=>{const t=document.querySelectorAll('[role=table]')[1]; const r=[...t.querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.trim().startsWith('K')); r.querySelector('[role=cell]').click();})()"); time.sleep(.4)
    fill('Unidade','g/kg'); clk('Salvar','aside[role=dialog]')
    b=body(); chk('K corrigido e LAU-2048 volta à validação', 'mapeamento salvo · aguarda validação humana' in b and 'sem unidade' not in b.split('Original ao lado')[1])
    # ---- AG-03: criar diagnóstico
    c.goto(f'http://127.0.0.1:{p}/AG-03.dc.html'); time.sleep(.6)
    clk('+ Criar diagnóstico'); fill('Evidências (vistoria · laudo)','VIS-017 · PLA-104'); fill('Hipótese · causa','Daninhas resistentes na bordadura')
    fill('Meta','plantio limpo'); fill('Ação proposta','Dessecação sequencial'); clk('Salvar','aside[role=dialog]')
    chk('DIA-011 criado em rascunho (numeração única com o MIP)', 'DIA-011' in body() and 'Rascunho' in body())
    # ---- AG-05: anexar referência ao limiar
    c.goto(f'http://127.0.0.1:{p}/AG-05.dc.html'); time.sleep(.6)
    J("(()=>{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>/Limiar mosca-branca/.test(r.innerText)); r.querySelector('[role=cell]').click();})()"); time.sleep(.4)
    fill('Referência','Embrapa Café · boletim 2025'); fill('Unidade · gatilhos','adultos/folha'); fill('Validade · revisão','30/06/2027'); fill('Escopo (cultura · região · fase)','Café · Cerrado Mineiro')
    clk('Salvar','aside[role=dialog]')
    chk('limiar passa a Em validação (segue inativo)', 'segue inativo até validar' in body())
    # ---- AG-01det e AG-03det: caminho de volta
    c.goto(f'http://127.0.0.1:{p}/AG-03det.dc.html'); time.sleep(.5)
    chk('DIA-007 aponta para VIS-011 e REC-014', J("['AG-01.dc.html#VIS-011','AG-04det.dc.html'].every(h=>!!document.querySelector('a[href=\"'+h+'\"]'))"))
    J("localStorage.removeItem('talhao-os-mip-v1'); localStorage.removeItem('talhao-os-cenario-v1')")
finally:
    try:
        if c: c.close()
    finally: srv.terminate()
print('RESULTADO', f'{sum(ok)}/{len(ok)}')
