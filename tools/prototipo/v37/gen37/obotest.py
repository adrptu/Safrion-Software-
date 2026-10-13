# -*- coding: utf-8 -*-
"""Teste CDP do onboarding (ON-01, ON-01det): ações de linha e validação da prévia. O backoffice (BO-01, BO-02) está em plataforma_test.py."""
import sys, os, time, subprocess, json
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from cdp import Chrome
from journeys import free
R=os.path.join(os.path.dirname(os.path.abspath(__file__)),'_render'); p=free()
srv=subprocess.Popen(['python3','-m','http.server',str(p),'--bind','127.0.0.1','--directory',R],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(0.8)
c=Chrome(port=free()); J=c.js
CLK="""((t,root)=>{const r=root?document.querySelector(root):document; const n=s=>(s||'').replace(/\\s+/g,' ').trim(); const els=[...r.querySelectorAll('button,a')]; const e=els.find(x=>n(x.innerText)===t)||els.find(x=>n(x.innerText).startsWith(t)); if(!e) return 'NÃO ACHEI: '+t; e.click(); return 'ok';})"""
SETV="""((sel,val)=>{const i=document.querySelector(sel); const P=i.tagName==='SELECT'?HTMLSelectElement.prototype:(i.tagName==='TEXTAREA'?HTMLTextAreaElement.prototype:HTMLInputElement.prototype); Object.getOwnPropertyDescriptor(P,'value').set.call(i,val); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true}));})"""
T=lambda: J("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).filter(Boolean).join(' | ')")
FORM=lambda: J("!!document.querySelector('aside[role=dialog]')")
def clk(t,root=None): r=J(f"({CLK})({json.dumps(t)},{json.dumps(root)})"); time.sleep(.45); return r
def setv(sel,val): J(f"({SETV})({json.dumps(sel)},{json.dumps(val)})"); time.sleep(.25)
def rowclick(gidx,txt):
    r=J(f"""(()=>{{const t=document.querySelectorAll('[role=table]')[{gidx}]; const row=[...t.querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.indexOf({json.dumps(txt)})>=0); if(!row) return 'sem linha'; (row.querySelector('[role=cell] span')||row).click(); return 'ok';}})()"""); time.sleep(.45); return r
def cell(gidx,txt,col):
    return J(f"""(()=>{{const t=document.querySelectorAll('[role=table]')[{gidx}]; const row=[...t.querySelectorAll('[role=row]')].find(r=>r.innerText.indexOf({json.dumps(txt)})>=0); return row?row.querySelectorAll('[role=cell]')[{col}].innerText.replace(/\\s+/g,' ').trim():'sem linha';}})()""")
def go(tela): c.goto(f'http://127.0.0.1:{p}/{tela}'); time.sleep(.6)
ok=[];
def chk(nome,cond,extra=''): ok.append(bool(cond)); print(('OK  ' if cond else 'FALHOU ')+nome, extra)
try:
    c.size(1440,1000)
    # ---- ON-01: ação de linha abre painel próprio, não a consulta da linha
    go('ON-01.dc.html')
    r=clk('Continuar cultura e ciclo'); chk('ON-01 ação de linha abre painel',r=='ok' and J("document.body.innerText.indexOf('Salvar cultura e ciclo')>=0") and not FORM())
    clk('Salvar cultura e ciclo'); chk('ON-01 painel confirma e passo avança', cell(0,'3 · Cultura',1)=='Concluído' and cell(0,'3 · Cultura',2)=='Cultura e ciclo salvos', cell(0,'3 · Cultura',2))
    clk('Anexar CAR'); clk('Anexar documento'); chk('ON-01 CAR baixa pendência', bool(J("/PENDÊNCIAS\\s*2\\s*polígono · prévia/.test(document.body.innerText)")))
    rowclick(0,'5 · Importação'); chk('ON-01 linha abre consulta', FORM() and J("document.body.innerText.indexOf('Consulta')>=0")); clk('Fechar','aside[role=dialog]')
    # ---- ON-01det: validar sem corrigir, corrigir estoque na linha, validar de novo
    go('ON-01det.dc.html')
    chk('ON-01det falta inicial', 'corrigir 3 objetos' in J("document.body.innerText"))
    clk('Validar prévia'); t1=T(); chk('ON-01det 1ª validação', 'Gravados: 9 talhões, 6 máquinas' in t1 and 'estoque inicial' in t1, t1[:160])
    chk('ON-01det máquinas gravadas', cell(0,'Máquinas',3)=='Gravado', cell(0,'Máquinas',3))
    rowclick(0,'Estoque inicial'); chk('ON-01det campo condicional unidade', J("!!document.querySelector('#fx_g_imp_un')") and not J("!!document.querySelector('#fx_g_imp_dec')"))
    setv('#fx_g_imp_un','sc 50 kg'); clk('Salvar','aside[role=dialog]')
    # colunas essenciais (10/10): o mapeamento e a unidade da "qtde" saíram da linha e ficam no detalhe do objeto (a mesma asserção, lida no formulário)
    chk('ON-01det erro some após salvar', cell(0,'Estoque inicial',2)=='—', cell(0,'Estoque inicial',2))
    rowclick(0,'Estoque inicial'); mp=J("[(document.querySelector('#fx_g_imp_map')||{}).value,(document.querySelector('#fx_g_imp_un')||{}).value]")
    chk('ON-01det mapeamento e unidade no detalhe do objeto', mp==['item, depósito, qtde','sc 50 kg'], mp); clk('Fechar','aside[role=dialog]')
    chk('ON-01det falta recalculada', 'corrigir 2 objetos' in J("document.body.innerText"))
    clk('Validar prévia'); t2=T(); chk('ON-01det 2ª validação só grava o novo', t2.startswith('Gravados: 48 linhas de estoque') and 'máquinas' not in t2, t2[:120])
    rowclick(0,'Máquinas'); chk('ON-01det gravado abre em consulta', FORM() and J("document.querySelectorAll('aside[role=dialog] input:not([readonly]), aside[role=dialog] select:not([disabled])').length")==0); clk('Fechar','aside[role=dialog]')
    # BO-01..BO-04 saíram deste teste em 06/10/2026 (PLAT-01): BO-01 e BO-02 foram refeitos em areas/plataforma.py (plataforma_test.py);
    # BO-01det, BO-02det, BO-03, BO-03det e BO-04 deixaram de ser gerados (PLAT-D02)
    print('erros JS:', J("window.__err||'nenhum'"))
finally:
    c.close(); srv.terminate()
print(f'{sum(ok)}/{len(ok)} verificações OK')
