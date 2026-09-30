# -*- coding: utf-8 -*-
"""Teste CDP de CD-01det (parcelas somam pela área declarada, como no Planejar safra) e CD-02 (rendimento com os mesmos
campos, rótulos e cálculo ao vivo da etapa 3 do Planejar safra; tabela sem colunas novas e sem rolagem lateral a 1440 px)."""
import sys, os, time, subprocess, json
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from cdp import Chrome
from journeys import free
R=sys.argv[1] if len(sys.argv)>1 else os.path.join(os.path.dirname(os.path.abspath(__file__)),'_render'); p=free()
srv=subprocess.Popen(['python3','-m','http.server',str(p),'--bind','127.0.0.1','--directory',R],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(0.8)
c=Chrome(port=free()); J=c.js
SETV="""((sel,val)=>{const i=document.querySelector(sel); const P=i.tagName==='SELECT'?HTMLSelectElement.prototype:HTMLInputElement.prototype; Object.getOwnPropertyDescriptor(P,'value').set.call(i,val); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true}));})"""
BTN="""((t)=>{const b=[...document.querySelectorAll('aside[role=dialog] button')].find(b=>b.innerText.trim()===t); if(b){b.click(); return true;} return false;})"""
CLK="""((t)=>{const n=s=>(s||'').replace(/\\s+/g,' ').trim(); const els=[...document.querySelectorAll('button,a')]; const e=els.find(x=>n(x.innerText)===t)||els.find(x=>n(x.innerText).startsWith(t)); if(!e) return 'NÃO ACHEI: '+t; e.click(); return 'ok';})"""
def ROW(ti,txt): return f"[...document.querySelectorAll('[role=table]')[{ti}].querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.replace(/\\s+/g,' ').indexOf({json.dumps(txt)})>=0)"
def openrow(ti,txt): J(f"(()=>{{const r={ROW(ti,txt)}; (r.querySelector('[role=cell] span')||r).click();}})()"); time.sleep(.4)
def rowtxt(ti,txt): return J(f"(()=>{{const r={ROW(ti,txt)}; return r?r.innerText.replace(/\\s+/g,' '):null;}})()")
def fv(k): return J(f"(()=>{{const i=document.querySelector('aside[role=dialog] [id$=\"_{k}\"]'); return i?i.value:null;}})()")
def fset(k,val): J(f"({SETV})('aside[role=dialog] [id$=\"_{k}\"]',{json.dumps(val)})"); time.sleep(.25)
def labels(): return J("[...document.querySelectorAll('aside[role=dialog] label[for]')].map(l=>l.innerText.trim())")
def alerts(): return J("[...document.querySelectorAll('aside [role=alert]')].map(x=>x.innerText).join(' | ')")
def toast(): return J("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).filter(Boolean).join(' | ')")
ok=[]
def chk(nome,cond,extra=''):
    ok.append(bool(cond)); print(('OK  ' if cond else 'FALHOU ')+nome+(' · '+str(extra) if extra else ''))
try:
    c.size(1440,1100)
    # ================= CD-01det · parcelas pela área declarada =================
    c.goto(f'http://127.0.0.1:{p}/CD-01det.dc.html'); time.sleep(.5)
    chk('CD-01det sem erro JS', J("window.__err||''")=='', J("window.__err||''"))
    # ================= CD-02 · rendimento como a etapa 3 do Planejar safra =================
    c.goto(f'http://127.0.0.1:{p}/CD-02.dc.html'); time.sleep(.5)
    chk('CD-02 sem erro JS', J("window.__err||''")=='', J("window.__err||''"))
    sw=J("(()=>{const s=document.querySelectorAll('[role=table]')[1].parentElement; return [s.scrollWidth,s.clientWidth];})()")
    chk('rendimentos sem rolagem lateral a 1440 px', sw[0]<=sw[1], sw)
    chk('no máximo 7 colunas', J("document.querySelectorAll('[role=table]')[1].querySelectorAll('[role=columnheader]').length")<=7)
    t=rowtxt(1,'Pulverização'); chk('linha mostra largura · velocidade · eficiência', '36 m · 8 km/h · 75 %' in t, t)
    chk('linha mostra custo por hora e por hectare', 'R$ 313,00' in t and 'R$ 14,49' in t, t)
    t=rowtxt(1,'Tratamento de sementes'); chk('rendimento informado sinalizado', 'rendimento informado' in t, t)
    openrow(1,'Pulverização'); L=labels()
    chk('formulário abre', len(L)>0, L)
    chk('mesmos rótulos do Planejar safra', L==['Operação','Conjunto ou equipe','Como obter o rendimento','Largura de trabalho','Velocidade de trabalho','Eficiência de campo',
        'Rendimento efetivo','Máquina','Implemento','Pessoas na equipe','Custo por pessoa','Custo por hora','Fonte do dado','Vigente até'], L)
    chk('rendimento ao vivo inicial = 21,60', fv('rend_c')=='21,60', fv('rend_c'))
    chk('custo/h ao vivo inicial = 313,00', fv('custo_c')=='313,00', fv('custo_c'))
    fset('vel','10'); chk('L × V ÷ 10 × E ao vivo: 36 × 10 ÷ 10 × 75% = 27,00', fv('rend_c')=='27,00', fv('rend_c'))
    fset('maq','200'); chk('custo/h ao vivo: 200 + 95 + 1 × 38 = 333,00', fv('custo_c')=='333,00', fv('custo_c'))
    AJ=["Largura × velocidade ÷ 10 × eficiência.","Máquina + implemento + pessoas × custo por pessoa.","Inclua combustível, manutenção e depreciação; o operador entra em Pessoas."]
    chk('ajudas das fórmulas e da composição visíveis', all(J(f"document.querySelector('aside[role=dialog]').innerText.indexOf({json.dumps(a)})>=0") for a in AJ))
    fset('larg','0,2'); J(f"({BTN})('Salvar')"); time.sleep(.4)
    al=alerts(); chk('largura abaixo do mínimo barrada', 'Mínimo 0,5 m' in al, al)
    chk('rendimento ao vivo acompanha o digitado', fv('rend_c')=='0,15', fv('rend_c'))
    fset('larg','36'); J(f"({BTN})('Salvar')"); time.sleep(.5)
    chk('salvou e fechou', J("!document.querySelector('aside[role=dialog]')"), alerts())
    ts=toast(); chk('aviso de salvo com o novo rendimento', '27,00 ha/h' in ts and 'R$ 333,00/h' in ts and 'R$ 12,33/ha' in ts, ts)
    t=rowtxt(1,'Pulverização'); chk('linha recalculada (27,00 ha/h · R$ 333,00 · R$ 12,33)', all(x in t for x in ['36 m · 10 km/h · 75 %','27,00 ha/h','R$ 333,00','R$ 12,33']), t)
    # modo Informado: sem largura, rendimento digitado
    openrow(1,'Plantio'); fset('modo','Informado'); time.sleep(.2)
    L=labels(); chk('Informado esconde largura, velocidade e eficiência', 'Largura de trabalho' not in L and L.count('Rendimento efetivo')==1, L)
    chk('Informado parte do rendimento atual (6,8)', fv('rend')=='6,8', fv('rend'))
    fset('rend','7,5'); J(f"({BTN})('Salvar')"); time.sleep(.5)
    t=rowtxt(1,'Plantio'); chk('linha em modo informado (7,50 ha/h)', 'rendimento informado' in t and '7,50 ha/h' in t and 'R$ 52,80' in t, t)
    c.shot(os.path.join(os.path.dirname(os.path.abspath(__file__)),'_probe','cd02_rend.png'))
    # ================= mesma lista de campos no Planejar safra (etapa 3) =================
    c.goto(f'http://127.0.0.1:{p}/SAF.dc.html'); time.sleep(.5)
    J(f"({CLK})('Abrir safra')"); time.sleep(.5); J(f"({CLK})('3 Defina os rendimentos')"); time.sleep(.5)
    J("(()=>{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>/Trator 02/.test(r.innerText)); (r.querySelector('[role=cell] span')||r).click();})()"); time.sleep(.4)
    LS=labels(); proprios=['Operação','Conjunto ou equipe','Fonte do dado','Vigente até']
    LC=['Como obter o rendimento','Largura de trabalho','Velocidade de trabalho','Eficiência de campo','Rendimento efetivo','Máquina','Implemento','Pessoas na equipe','Custo por pessoa','Custo por hora']
    chk('Planejar safra usa os mesmos campos (fora os próprios do cadastro)', LS==LC, LS)
    chk('Planejar safra tem as mesmas ajudas', all(J(f"document.querySelector('aside[role=dialog]').innerText.indexOf({json.dumps(a)})>=0") for a in AJ))
    chk('Planejar safra calcula o mesmo rendimento ao vivo (21,60)', fv('rend_c')=='21,60', fv('rend_c'))
finally:
    c.close(); srv.terminate()
print('RESULTADO:', 'OK' if all(ok) else 'FALHOU', f'{sum(ok)}/{len(ok)}')
