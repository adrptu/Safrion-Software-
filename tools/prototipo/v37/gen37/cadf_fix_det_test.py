# -*- coding: utf-8 -*-
"""Teste CDP do CD-01det · correções da verificação independente (frente cad-fazendas):
safra encerrada mantém o resumo da época, talhão com parcelas em safra aberta não muda de fazenda no detalhe, talhão inativo tem
primária "Reativar", lista de versões do polígono não fica cortada (corpo rola dentro do artboard).
Uso: python3 cadf_fix_det_test.py  (serve _render/; ≤ 15 verificações; cada passo espera ≤ 0,5 s)."""
import sys, os, time, subprocess, json
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from cdp import Chrome
from journeys import free
HERE=os.path.dirname(os.path.abspath(__file__))
R=sys.argv[1] if len(sys.argv)>1 else os.path.join(HERE,'_render'); p=free()
srv=subprocess.Popen(['python3','-m','http.server',str(p),'--bind','127.0.0.1','--directory',R],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(0.6)
c=Chrome(port=free()); J=c.js
SETV="""((sel,val)=>{const i=document.querySelector(sel); const P=i.tagName==='SELECT'?HTMLSelectElement.prototype:HTMLInputElement.prototype; Object.getOwnPropertyDescriptor(P,'value').set.call(i,val); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true}));})"""
BTN="""((t)=>{const b=[...document.querySelectorAll('aside[role=dialog] button')].find(b=>b.innerText.trim()===t); if(b){b.click(); return true;} return false;})"""
CLK="""((t,sc)=>{const n=s=>(s||'').replace(/\\s+/g,' ').trim(); const els=[...document.querySelectorAll(sc||'button,a')]; const e=els.find(x=>n(x.innerText)===t)||els.find(x=>n(x.innerText).startsWith(t)); if(!e) return 'NÃO ACHEI: '+t; e.click(); return 'ok';})"""
def ROW(ti,txt): return f"[...document.querySelectorAll('[role=table]')[{ti}].querySelectorAll('[role=row]')].find(r=>r.innerText.replace(/\\s+/g,' ').indexOf({json.dumps(txt)})>=0)"
def openrow(ti,txt): J(f"(()=>{{const r={ROW(ti,txt)}; (r.querySelector('[role=cell] span')||r).click();}})()"); time.sleep(.35)
def rowtxt(ti,txt): return J(f"(()=>{{const r={ROW(ti,txt)}; return r?r.innerText.replace(/\\s+/g,' '):null;}})()")
def fset(k,val): J(f"({SETV})('aside[role=dialog] [id$=\"_{k}\"]',{json.dumps(val)})"); time.sleep(.2)
def fv(k): return J(f"(()=>{{const i=document.querySelector('aside[role=dialog] [id$=\"_{k}\"]'); return i?i.value:null;}})()")
def alerts(): return J("[...document.querySelectorAll('aside [role=alert]')].map(x=>x.innerText).join(' | ')")
def toast(): return J("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).filter(Boolean).join(' | ')")
def aberto(): return J("!!document.querySelector('aside[role=dialog]')")
def head(): return J("document.querySelector('header').innerText.replace(/\\s+/g,' ')")
def hbtns(): return J("[...document.querySelectorAll('header button, header a')].map(e=>e.innerText.trim()).filter(Boolean)")
def mbtns(): return J("[...document.querySelectorAll('main button, main a')].map(e=>e.innerText.trim()).filter(Boolean)")
def aba(t): J(f"(()=>{{const b=[...document.querySelectorAll('[role=tab]')].find(b=>b.innerText.replace(/\\s+/g,' ').trim().startsWith({json.dumps(t)})); if(b) b.click();}})()"); time.sleep(.35)
def erro_js(): return J("[...document.querySelectorAll('.sc-logic-error')].map(e=>e.innerText).join(' | ')")
def save(): J(f"({BTN})('Salvar')"); time.sleep(.4)
def fechar(): J(f"({BTN})('Cancelar')"); time.sleep(.2); J(f"({BTN})('Descartar alterações')"); time.sleep(.2)
def tal(t): J(f"({SETV})('select[aria-label=Talhão]',{json.dumps(t)})"); time.sleep(.4)
ok=[]
def chk(nome,cond,extra=''):
    ok.append(bool(cond)); print(('OK  ' if cond else 'FALHOU ')+nome+(' · '+str(extra)[:300] if extra else ''), flush=True)
try:
    c.size(1440,1000); c.goto(f'http://127.0.0.1:{p}/CD-01det.dc.html#talhao=T3',wait=1.2)
    chk('1 sem erro JS; T3 aberto', erro_js()=='' and J("document.querySelector('select[aria-label=Talhão]').value")=='T3', erro_js())
    # ---------- safra encerrada mantém o resumo da época ----------
    openrow(0,'Santa Rita'); fset('decl','100'); fset('motivo','Documento desatualizado'); save()
    J(f"({CLK})('Expandir tudo')"); time.sleep(.3)
    a=rowtxt(1,'Safra 2026/27'); e=rowtxt(1,'Safra 2025/26')
    # TABELAS-FOCO (06/10/2026): Área (alocada) e Livre em colunas próprias: aberta "96 ha | 4 ha"; encerrada "96 ha | 0 ha" (o resumo da época)
    chk('2 safra aberta recalcula (96 de 100 ha · 4 ha livres); encerrada fica 96 de 96 ha · Área conferida', '96 ha 4 ha' in (a or '') and 'Em planejamento' in (a or '')
        and '96 ha 0 ha' in (e or '') and 'Encerrada' in (e or ''), [a,e])
    # ---------- T3 não muda de fazenda com parcelas em safra aberta ----------
    openrow(0,'Santa Rita'); fset('faz','Boa Vista'); save(); al=alerts()
    chk('3 no detalhe o T3 também não muda de fazenda', aberto() and 'T3 tem parcelas na Safra 2026/27 da Santa Rita. Tire-as no Planejar safra antes de mudar de fazenda.' in al, al)
    fechar()
    chk('4 T3 segue na Santa Rita', 'Santa Rita' in (rowtxt(0,'Sequeiro') or '') and 'Boa Vista' not in (rowtxt(0,'Sequeiro') or ''), rowtxt(0,'Sequeiro'))
    # ---------- talhão inativo: primária Reativar ----------
    tal('B1'); openrow(0,'Boa Vista'); fset('sit','Inativo'); save(); aba('Geometria'); hb=mbtns(); aba('Parcelas')
    chk('5 B1 inativo: estado Inativo, "Reativar B1" na linha do talhão e sem "Definir polígono do B1"', 'Inativo desde' in head() and 'Reativar B1' in hb and 'Definir polígono do B1' not in hb and 'Reativar B1' not in hbtns(), [head()[-160:],hb])
    J(f"({CLK})('Reativar B1','main button')"); time.sleep(.45)
    foco=J("(document.activeElement||{}).id||''")
    chk('6 "Reativar B1" abre o formulário do B1 com Situação em Ativo e o foco nela', aberto() and fv('sit')=='Ativo' and foco.endswith('_sit'), [fv('sit'),foco])
    # 16/10/2026 (BOT-01): o próximo passo do talhão ("Definir polígono do B1") é a primária do cabeçalho do detalhe
    save(); aba('Geometria'); hb=mbtns(); hh=hbtns(); aba('Parcelas')
    chk('7 salvar reativa: toast, estado e o cabeçalho voltam a nomear o próximo passo', 'B1 reativado: volta ao Planejar safra e ao Mapa.' in toast() and 'Inativo' not in head()
        and 'Definir polígono do B1' in hh and 'Reativar B1' not in hb, [toast(),hb,hh])
    # ---------- versões do polígono não ficam cortadas ----------
    tal('T1'); aba('Geometria'); J(f"({CLK})('Definir polígono da T1-B','header button')"); time.sleep(.3); J(f"({BTN})('Gerar prévia')"); time.sleep(.25); J(f"({BTN})('Salvar polígono')"); time.sleep(.4)
    for _ in range(2):
        J(f"({CLK})('Nova versão do polígono')"); time.sleep(.3); J(f"({BTN})('Gerar prévia')"); time.sleep(.25); J(f"({BTN})('Salvar polígono')"); time.sleep(.4)
    J(f"({CLK})('Expandir tudo')"); time.sleep(.3)
    J("(()=>{const m=document.querySelector('main'); m.scrollTop=m.scrollHeight;})()"); time.sleep(.3)
    geo=J("""(()=>{const root=document.querySelector('[data-root]').getBoundingClientRect(); const m=document.querySelector('main'); const mb=m.getBoundingClientRect();
      const s=[...document.querySelectorAll('main section')].find(x=>x.innerText.indexOf('VERSÕES DO POLÍGONO')>=0); const b=s.getBoundingClientRect();
      return {sec:Math.round(b.bottom), main:Math.round(mb.bottom), root:Math.round(root.bottom), ov:getComputedStyle(m).overflowY, txt:s.innerText.replace(/\\s+/g,' ').slice(-220)};})()""")
    c.shot(os.path.join(HERE,'_probe','cadf_fix_det_versoes.png'))
    chk('8 com v6 a lista de versões e o bloco Geometria aparecem inteiros (corpo rola dentro do artboard)', geo['sec']<=geo['main']<=geo['root'] and geo['ov']=='auto'
        and 'Consulta v2' in geo['txt'], geo)
    chk('9 sem erro JS no fim', erro_js()=='', erro_js())
finally:
    c.close(); srv.terminate()
print('RESULTADO:', 'OK' if all(ok) else 'FALHOU', f'{sum(ok)}/{len(ok)}')
