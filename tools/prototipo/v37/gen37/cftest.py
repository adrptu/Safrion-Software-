# -*- coding: utf-8 -*-
"""Teste CDP de Configurações (CF-01, CF-02, CF-02det, CF-03, CF-03det; o CF-05 está em assinatura_test.py): DEMO-11 com 40 ha/APT-1187/REC-7741,
conflito offline separado do ERP, decisão atualiza Estado + cabeçalho + Falta; convite; proposta de revisão."""
import sys, os, time, subprocess, json
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from cdp import Chrome
from journeys import free
R=os.path.join(os.path.dirname(os.path.abspath(__file__)),'_render'); p=free()
srv=subprocess.Popen(['python3','-m','http.server',str(p),'--bind','127.0.0.1','--directory',R],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(0.8)
c=Chrome(port=free()); J=c.js
SETV="""((sel,val)=>{const i=document.querySelector(sel); const P=i.tagName==='SELECT'?HTMLSelectElement.prototype:(i.tagName==='TEXTAREA'?HTMLTextAreaElement.prototype:HTMLInputElement.prototype); Object.getOwnPropertyDescriptor(P,'value').set.call(i,val); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true}));})"""
BTN="""((t)=>{const b=[...document.querySelectorAll('aside[role=dialog] button')].find(b=>b.innerText.trim()===t); if(b){b.click(); return true;} return false;})"""
CLK="""((t)=>{const n=s=>(s||'').replace(/\\s+/g,' ').trim(); const e=[...document.querySelectorAll('button,a')].find(x=>n(x.innerText)===t); if(!e) return false; e.click(); return true;})"""
ok=[]
def chk(nome,cond,extra=''):
    ok.append(bool(cond)); print(('OK  ' if cond else 'FALHOU ')+nome+(' · '+str(extra)[:160] if extra else ''))
def body(): return J("document.body.innerText")
def toast(): return J("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).filter(Boolean).join(' | ')")
def row(ti,txt): return f"[...document.querySelectorAll('[role=table]')[{ti}].querySelectorAll('[role=row]')].find(r=>r.innerText.indexOf({json.dumps(txt)})>=0)"
def openrow(ti,txt): J(f"(()=>{{const r={row(ti,txt)}; (r.querySelector('[role=cell] span')||r).click();}})()"); time.sleep(.4)
def rowtxt(ti,txt): return J(f"(()=>{{const r={row(ti,txt)}; return r?r.innerText.replace(/\\s+/g,' '):null;}})()")
def setf(k,v): J(f"({SETV})('aside[role=dialog] [id$=\"_{k}\"]',{json.dumps(v)})"); time.sleep(.2)
def btn(t): r=J(f"({BTN})({json.dumps(t)})"); time.sleep(.45); return r
def clk(t): r=J(f"({CLK})({json.dumps(t)})"); time.sleep(.45); return r
def go(f): c.goto(f'http://127.0.0.1:{p}/{f}'); time.sleep(.7); chk(f+' sem erro JS', J("window.__err||''")=='', J("window.__err||''"))
try:
    c.size(1440,1100)
    # ---------- CF-03det · DEMO-11 ----------
    go('CF-03det.dc.html'); b=body()
    chk('40 ha, APT-1187, identidade e REC-7741 na tela', all(x in b for x in ['APT-1187','c9e2-…-4f1a','REC-7741','40 ha']))
    chk('sem "50 ha" em CF-03det', '50 ha' not in b)
    chk('bloco offline separado do ERP', 'Sincronização offline · OS-0421 dia 4' in b and 'Reconciliação · Sankhya (ERP simulado)' in b)
    chk('coluna Servidor no bloco offline', J("[...document.querySelectorAll('[role=table]')[1].querySelectorAll('[role=columnheader]')].some(h=>h.innerText.indexOf('SERVIDOR')>=0||h.innerText.indexOf('Servidor')>=0)"))
    chk('cabeçalho inicial 3 pendências', 'Simulado · 3 pendências' in b)
    openrow(1,'Relato B'); chk('decidir conflito pela linha', J("!!document.querySelector('aside[role=dialog]')"), J("(document.querySelector('aside[role=dialog] h2')||{}).innerText"))
    btn('Salvar'); chk('motivo obrigatório', 'Informe motivo' in J("document.querySelector('aside[role=dialog]').innerText"))
    setf('motivo','Mesma passada registrada por dois dispositivos'); btn('Salvar')
    chk('estado vira Decidido · relatos preservados', 'Decidido · relatos preservados' in (rowtxt(1,'Relato B') or ''), rowtxt(1,'Relato B'))
    b=body(); chk('cabeçalho 2 pendências', 'Simulado · 2 pendências' in b); chk('Falta sem conflito offline', 'conflito offline de OS-0421' not in b)
    chk('toast da decisão', '40 ha permanecem contados uma vez' in toast(), toast())
    # primário: próxima ação = corrigir NF
    chk('primário nomeia a próxima ação', clk('Corrigir e reprocessar a NF 4412'))
    chk('abre o formulário da NF', 'Unidade no ERP' in J("(document.querySelector('aside[role=dialog]')||{}).innerText||''"))
    setf('unid_erp','SC50'); btn('Salvar'); chk('NF aceita', 'Aceito · reprocessado' in (rowtxt(0,'NF 4412') or ''), rowtxt(0,'NF 4412'))
    clk('Consultar por chave'); chk('devolução aceita', 'Aceito' in (rowtxt(0,'Devolução') or ''), rowtxt(0,'Devolução'))
    b=body(); chk('cabeçalho conciliado', 'Simulado · conciliado' in b); chk('primário leva à trilha', J("!![...document.querySelectorAll('a')].find(a=>a.innerText.trim()==='Conferir a trilha de auditoria' && a.getAttribute('href')==='CF-04.dc.html')"))
    # ---------- CF-03 ----------
    go('CF-03.dc.html'); b=body()
    chk('CF-03 sem 50 ha e com APT-1187/REC-7741', '50 ha' not in b and 'APT-1187' in b and 'REC-7741' in b)
    chk('KPI erros = 2', J("[...document.querySelectorAll('div')].some(d=>d.innerText && d.innerText.replace(/\\s+/g,' ').indexOf('ERROS A TRATAR 2')===0)"))
    openrow(1,'NF 4412'); setf('unid_erp','SC50'); btn('Salvar')
    chk('KPI erros = 1 após reprocessar', '1 erro · 1 conflito' in body())
    openrow(1,'Devolução'); chk('item sem edição abre em consulta sem campos de unidade', 'Unidade no ERP' not in J("document.querySelector('aside[role=dialog]').innerText"))
    btn('Fechar')
    # ---------- CF-01 ----------
    go('CF-01.dc.html')
    clk('+ Convidar usuário'); setf('nome','Ivo Teste'); setf('email','ivo@'); btn('Salvar')
    chk('e-mail inválido junto ao campo', 'E-mail inválido' in J("document.querySelector('aside[role=dialog]').innerText"))
    setf('email','ivo@fazsantarita.com.br'); btn('Salvar')
    chk('convite pendente', 'Convite pendente' in (rowtxt(0,'Ivo Teste') or ''), rowtxt(0,'Ivo Teste'))
    chk('cabeçalho 2 convites', '2 convites pendentes' in body())
    openrow(0,'Caio Martins'); setf('escopo','Santa Rita + Boa Vista'); btn('Salvar')
    t=rowtxt(0,'Caio Martins'); chk('escopo proposto mantém vigente + pendência', 'proposto: Santa Rita + Boa Vista' in t and 'Alteração pendente' in t, t)
    clk('Revogar delegação'); chk('delegação revogada', 'Delegação revogada' in (rowtxt(0,'Paula Neri') or ''))
    # ---------- CF-02 ----------
    go('CF-02.dc.html')
    openrow(0,'Liberar ordem'); setf('lim','até R$ 100 mil por ordem; acima, Direção'); setf('motivo','Safra maior'); btn('Salvar')
    t=rowtxt(0,'Liberar ordem'); chk('AL-01 v5 em revisão, v4 vigente', 'v5 em revisão' in t and 'até R$ 80 mil' in t, t)
    chk('KPI em revisão = 2', '2 em revisão' in body())
    openrow(0,'Dispensar saldo'); chk('AL-05 abre em consulta', J("!!document.querySelector('aside[role=dialog]') && ![...document.querySelectorAll('aside[role=dialog] button')].some(b=>b.innerText.trim()==='Salvar')")); btn('Fechar')
    # ---------- CF-02det ----------
    go('CF-02det.dc.html'); clk('Decidir a v3'); chk('decisão abre pela ação primária', J("!!document.querySelector('aside[role=dialog]')"))
    setf('dec','Devolver para ajuste'); btn('Salvar'); chk('motivo exigido ao devolver', 'Informe motivo' in J("document.querySelector('aside[role=dialog]').innerText"))
    setf('motivo','25% amplia demais'); btn('Salvar'); chk('status v3 devolvida', 'v3 devolvida · v2 vigente' in body())
    # CF-05 saiu deste teste em 06/10/2026 (PLAT-01): a tela foi refeita em areas/assinatura.py e é coberta por assinatura_test.py
finally:
    c.close(); srv.terminate()
print(f'{sum(ok)}/{len(ok)} verificações OK'); sys.exit(0 if all(ok) else 1)
