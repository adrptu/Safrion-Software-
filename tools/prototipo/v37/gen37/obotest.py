# -*- coding: utf-8 -*-
"""Teste CDP do módulo onboarding_backoffice: ações de linha, validação da prévia, reconciliação, aprovação de ajustes."""
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
    clk('Salvar cultura e ciclo'); chk('ON-01 painel confirma e passo avança', cell(0,'3 · Cultura',1)=='Concluído' and cell(0,'3 · Cultura',3)=='Cultura e ciclo salvos', cell(0,'3 · Cultura',3))
    clk('Anexar CAR'); clk('Anexar documento'); chk('ON-01 CAR baixa pendência', bool(J("/PENDÊNCIAS\\s*2\\s*polígono · prévia/.test(document.body.innerText)")))
    rowclick(0,'5 · Importação'); chk('ON-01 linha abre consulta', FORM() and J("document.body.innerText.indexOf('Consulta')>=0")); clk('Fechar','aside[role=dialog]')
    # ---- ON-01det: validar sem corrigir, corrigir estoque na linha, validar de novo
    go('ON-01det.dc.html')
    chk('ON-01det falta inicial', 'corrigir 3 objetos' in J("document.body.innerText"))
    clk('Validar prévia'); t1=T(); chk('ON-01det 1ª validação', 'Gravados: 9 talhões, 6 máquinas' in t1 and 'estoque inicial' in t1, t1[:160])
    chk('ON-01det máquinas gravadas', cell(0,'Máquinas',5)=='Gravado', cell(0,'Máquinas',5))
    rowclick(0,'Estoque inicial'); chk('ON-01det campo condicional unidade', J("!!document.querySelector('#fx_g_imp_un')") and not J("!!document.querySelector('#fx_g_imp_dec')"))
    setv('#fx_g_imp_un','sc 50 kg'); clk('Salvar','aside[role=dialog]')
    chk('ON-01det erro some após salvar', cell(0,'Estoque inicial',4)=='—' and cell(0,'Estoque inicial',2).endswith('qtde em sc 50 kg'), cell(0,'Estoque inicial',2))
    chk('ON-01det falta recalculada', 'corrigir 2 objetos' in J("document.body.innerText"))
    clk('Validar prévia'); t2=T(); chk('ON-01det 2ª validação só grava o novo', t2.startswith('Gravados: 48 linhas de estoque') and 'máquinas' not in t2, t2[:120])
    rowclick(0,'Máquinas'); chk('ON-01det gravado abre em consulta', FORM() and J("document.querySelectorAll('aside[role=dialog] input:not([readonly]), aside[role=dialog] select:not([disabled])').length")==0); clk('Fechar','aside[role=dialog]')
    # ---- BO-01: criar versão pelo botão, vigente em consulta, estado vigente não é aceito
    go('BO-01.dc.html')
    chk('BO-01 KPIs', J("document.body.innerText.indexOf('VIGENTES NO PILOTO\\n2')>=0 || /VIGENTES NO PILOTO\\s*2/.test(document.body.innerText)"))
    clk('Criar versão'); chk('BO-01 nova versão abre form', FORM() and 'Nova versão de plano' in J("document.querySelector('aside[role=dialog] h2').innerText"))
    clk('Salvar','aside[role=dialog]'); chk('BO-01 nova versão salva', 'Produtor Piloto v5' in J("document.querySelectorAll('[role=table]')[0].innerText"), T()[:90])
    chk('BO-01 KPI hipóteses = 3', bool(J("/HIPÓTESES\\s*3/.test(document.body.innerText)")))
    rowclick(0,'Patrocínio Cooperativa v2'); chk('BO-01 vigente abre em consulta', FORM() and J("document.querySelectorAll('aside[role=dialog] input:not([readonly]), aside[role=dialog] select:not([disabled]), aside[role=dialog] textarea:not([readonly])').length")==0); clk('Fechar','aside[role=dialog]')
    chk('BO-01 link v3 vai ao detalhe', J("[...document.querySelectorAll('[role=table] a')].some(a=>a.getAttribute('href')==='BO-01det.dc.html')"))
    # ---- BO-02: reconciliar fatura pendente muda estado e KPI; idempotente
    go('BO-02.dc.html')
    chk('BO-02 KPI abertas 3', bool(J("/FATURAS ABERTAS\\s*3/.test(document.body.innerText)")))
    J("""(()=>{const t=document.querySelectorAll('[role=table]')[1]; const row=[...t.querySelectorAll('[role=row]')].find(r=>r.innerText.indexOf('FAT-2209-016')>=0); [...row.querySelectorAll('button')].find(b=>b.innerText.trim()==='Reconciliar').click();})()"""); time.sleep(.45)
    chk('BO-02 FAT-016 paga', cell(1,'FAT-2209-016',3)=='Pago' and not FORM(), T()[:100])
    chk('BO-02 KPI abertas 2 · R$ 6,7 mil', bool(J("/FATURAS ABERTAS\\s*2\\s*R\\$ 6,7 mil/.test(document.body.innerText)")))
    clk('Reconciliar pagamento'); t=T(); chk('BO-02 reconciliar tudo sem duplicar', 'Sem conciliação' in t and 'FAT-2209-016' not in t, t[:140])
    # ---- BO-03: aprovar AJ-009
    go('BO-03.dc.html')
    clk('Aprovar ajuste'); chk('BO-03 AJ-009 aprovado', cell(0,'Agro Bela Vista',3)=='Aprovado' and bool(J("/AJUSTES A APROVAR\\s*0/.test(document.body.innerText)")), T()[:80])
    clk('Aprovar ajuste'); chk('BO-03 segunda aprovação não duplica', 'Nenhum ajuste a aprovar' in T())
    rowclick(0,'Fazenda Aurora'); chk('BO-03 linha abre origem com link', FORM() and J("[...document.querySelectorAll('aside[role=dialog] a')].some(a=>a.getAttribute('href')==='BO-03det.dc.html')")); clk('Fechar','aside[role=dialog]')
    # ---- BO-03det: primário abre o ajuste; mudança de base é recusada; registrar; aprovar
    go('BO-03det.dc.html')
    clk('Registrar ajuste com origem'); chk('BO-03det primário abre form do ajuste', FORM() and 'Ajuste da medição' in J("document.querySelector('aside[role=dialog] h2').innerText"))
    setv('#fx_g_aj_tipo','Mudança de base (exige decisão comercial)'); clk('Salvar','aside[role=dialog]')
    chk('BO-03det mudança de base recusada', 'não foi registrado' in T() and J("document.body.innerText.indexOf('Registrar ajuste com origem')>=0"), T()[:90])
    clk('Registrar ajuste com origem'); clk('Salvar','aside[role=dialog]')
    chk('BO-03det ajuste registrado', 'AJ-010 registrado' in T() and 'Registrado' in cell(1,'AJ-010',4), cell(1,'AJ-010',4))
    chk('BO-03det selo acompanha', 'Ajustado · aguarda aprovação' in J("document.body.innerText"))
    clk('Aprovar ajuste'); chk('BO-03det aprovado', 'AJ-010 aprovado' in T() and cell(1,'AJ-010',4)=='Aprovado' and J("document.body.innerText.indexOf('✓ Ajustado')>=0") and 'Aprovado · set/2026' in J("document.body.innerText"))
    # ---- BO-04: coorte abre origem coerente
    go('BO-04.dc.html'); rowclick(0,'HF/frutas')
    chk('BO-04 origem da coorte', 'Ativação: 4 de 6' in J("document.querySelector('aside[role=dialog]').innerText"))
    print('erros JS:', J("window.__err||'nenhum'"))
finally:
    c.close(); srv.terminate()
print(f'{sum(ok)}/{len(ok)} verificações OK')
