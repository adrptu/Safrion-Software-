# -*- coding: utf-8 -*-
"""Teste CDP do CD-01det · correções da verificação independente (frente cad-fazendas):
safra encerrada mantém o resumo da época, talhão com parcelas em safra aberta não muda de fazenda no detalhe, talhão inativo tem
primária "Reativar", lista de versões do polígono não fica cortada (corpo rola dentro do artboard).
Uso: python3 cadf_fix_det_test.py  (serve _render/; ≤ 15 verificações; cada passo espera ≤ 0,5 s).
CADUX P2 (09/10/2026): a ficha de 1 linha do talhão (grade g_idt) virou o cabeçalho do detalhe (DS-58), com "Editar talhão" e, no
inativo, "Reativar {talhão}" no mesmo lugar; a grade das parcelas é a única da página (índice 0). As regras e os valores são os mesmos."""
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
def openrow(ti,txt): J(f"(()=>{{const r={ROW(ti,txt)}; (r.querySelector('.g2alvo')||r.querySelector('[role=cell] span')||r).click();}})()"); time.sleep(.35)   # CADUX: alvo da linha (BOT-07)
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
def save():   # CADUX: salvar sem erro volta à consulta do talhão (o painel fica); fecha com × para seguir na página, como antes
    J(f"({BTN})('Salvar')"); time.sleep(.4)
    J("(()=>{const d=document.querySelector('aside[role=dialog]'); if(d&&!d.querySelector('input:not([readonly]),select:not([disabled])')){ const b=d.querySelector('button[aria-label=Fechar]'); b&&b.click(); }})()"); time.sleep(.25)
def fechar():   # CADUX: Cancelar volta à consulta do talhão; × fecha
    J(f"({BTN})('Cancelar')"); time.sleep(.2); J(f"({BTN})('Descartar alterações')"); time.sleep(.2)
    J("(()=>{const b=document.querySelector('aside[role=dialog] button[aria-label=Fechar]'); b&&b.click();})()"); time.sleep(.25)
def editar(): J(f"({CLK})('Editar talhão','main button')"); time.sleep(.35)
def sub(): return J("(document.querySelector('main .cmd-ds')||{innerText:''}).innerText")
def tal(t): J(f"({SETV})('header select',{json.dumps(t)})"); time.sleep(.4)
ok=[]
def chk(nome,cond,extra=''):
    ok.append(bool(cond)); print(('OK  ' if cond else 'FALHOU ')+nome+(' · '+str(extra)[:300] if extra else ''), flush=True)
try:
    c.size(1440,1000); c.goto(f'http://127.0.0.1:{p}/CD-01det.dc.html#talhao=T3',wait=1.2)
    chk('1 sem erro JS; T3 aberto', erro_js()=='' and J("document.querySelector('header select').value")=='T3', erro_js())
    # ---------- safra encerrada mantém o resumo da época ----------
    editar(); fset('decl','100'); fset('motivo','Documento desatualizado'); save()
    J(f"({CLK})('Expandir tudo')"); time.sleep(.3)
    a=rowtxt(0,'Safra 2026/27'); e=rowtxt(0,'Safra 2025/26')
    # TABELAS-FOCO (06/10/2026): Área (alocada) e Livre em colunas próprias: aberta "96 ha | 4 ha"; encerrada "96 ha | 0 ha" (o resumo da época)
    chk('2 safra aberta recalcula (96 de 100 ha · 4 ha livres); encerrada fica 96 de 96 ha · Área conferida', '96 ha 4 ha' in (a or '') and 'Em planejamento' in (a or '')
        and '96 ha 0 ha' in (e or '') and 'Encerrada' in (e or ''), [a,e])
    # ---------- T3 não muda de fazenda com parcelas em safra aberta ----------
    editar(); fset('faz','Boa Vista'); save(); al=alerts()
    chk('3 no detalhe o T3 também não muda de fazenda', aberto() and 'T3 tem parcelas na Safra 2026/27 da Santa Rita. Tire-as no Planejar safra antes de mudar de fazenda.' in al, al)
    fechar()
    chk('4 T3 segue na Santa Rita', (sub() or '').startswith('Santa Rita') and 'Boa Vista' not in (sub() or ''), sub())
    # ---------- talhão inativo: primária Reativar ----------
    tal('B1'); editar(); fset('sit','Inativo'); save(); aba('Geometria'); hb=mbtns(); aba('Parcelas')
    chk('5 B1 inativo: estado Inativo, "Reativar B1" no topo do detalhe (no lugar de "Editar talhão") e sem "Definir polígono do B1"', 'Inativo desde' in head() and 'Reativar B1' in hb and 'Definir polígono do B1' not in hb and 'Reativar B1' not in hbtns() and 'Editar talhão' not in hb, [head()[-160:],hb])
    J(f"({CLK})('Reativar B1','main button')"); time.sleep(.45)
    foco=J("(document.activeElement||{}).id||''")
    chk('6 "Reativar B1" abre o formulário do B1 com Situação em Ativo e o foco nela', aberto() and fv('sit')=='Ativo' and foco.endswith('_sit'), [fv('sit'),foco])
    save(); aba('Geometria'); hb=mbtns(); mt=J("document.querySelector('main').innerText.replace(/\\s+/g,' ')"); aba('Parcelas')
    # CADUX (achado 5 da revisão; R18/AC-25): o próximo passo da geometria na Boa Vista é a frase do limite (mapa da fazenda ainda não existe),
    # não um "Definir polígono do B1" que gravava uma versão simulada
    chk('7 salvar reativa: toast, estado e a aba Geometria voltam a nomear o que falta (o polígono do B1 e o limite do mapa da Boa Vista)', 'B1 reativado: volta ao Planejar safra e ao Mapa.' in toast() and 'Inativo' not in head()
        and 'Polígono do B1 pendente: o mapa da Boa Vista ainda não existe no protótipo' in mt and 'Definir polígono do B1' not in hb and 'Reativar B1' not in hb, [toast(),hb,mt[-300:]])
    # ---------- versões do polígono não ficam cortadas ----------
    # CADUX (achado 5): sem o editor simulado não se criam versões novas aqui; confere a lista que existe (v3 atual, v2 em consulta)
    tal('T1'); aba('Geometria'); J(f"({CLK})('Expandir tudo')"); time.sleep(.3)
    J("(()=>{const m=document.querySelector('main'); m.scrollTop=m.scrollHeight;})()"); time.sleep(.3)
    geo=J("""(()=>{const root=document.querySelector('[data-root]').getBoundingClientRect(); const m=document.querySelector('main'); const mb=m.getBoundingClientRect();
      const s=[...document.querySelectorAll('main section')].find(x=>x.innerText.indexOf('VERSÕES DO POLÍGONO')>=0); const b=s.getBoundingClientRect();
      return {sec:Math.round(b.bottom), main:Math.round(mb.bottom), root:Math.round(root.bottom), ov:getComputedStyle(m).overflowY, txt:s.innerText.replace(/\\s+/g,' ').slice(-220)};})()""")
    c.shot(os.path.join(HERE,'_probe','cadf_fix_det_versoes.png'))
    chk('8 a lista de versões (v3 atual, v2 em consulta) e o bloco Geometria aparecem inteiros (corpo rola dentro do artboard)', geo['sec']<=geo['main']<=geo['root'] and geo['ov']=='auto'
        and 'Consulta v2' in geo['txt'], geo)
    chk('9 sem erro JS no fim', erro_js()=='', erro_js())
finally:
    c.close(); srv.terminate()
print('RESULTADO:', 'OK' if all(ok) else 'FALHOU', f'{sum(ok)}/{len(ok)}')
