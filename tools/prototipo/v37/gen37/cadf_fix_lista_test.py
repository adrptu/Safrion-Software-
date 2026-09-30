# -*- coding: utf-8 -*-
"""Teste CDP do CD-01 · correções da verificação independente (frente cad-fazendas):
altura (corpo rola dentro do artboard e a legenda do mapa nunca fica cortada), talhão com parcelas em safra aberta não muda de
fazenda, mapa só mostra talhão da fazenda do mapa, "Importar geometrias" retirado, formulários de cadastro novo com texto de cadastro.
Uso: python3 cadf_fix_lista_test.py  (serve _render/; ≤ 15 verificações; cada passo espera ≤ 0,5 s)."""
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
def dlg(): return J("(document.querySelector('aside[role=dialog]')||{innerText:''}).innerText.replace(/\\s+/g,' ')")
def labels(): return J("[...document.querySelectorAll('aside[role=dialog] label[for]')].map(l=>l.innerText.trim())")
def alerts(): return J("[...document.querySelectorAll('aside [role=alert]')].map(x=>x.innerText).join(' | ')")
def toast(): return J("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).filter(Boolean).join(' | ')")
def aberto(): return J("!!document.querySelector('aside[role=dialog]')")
def erro_js(): return J("[...document.querySelectorAll('.sc-logic-error')].map(e=>e.innerText).join(' | ')")
def save(): J(f"({BTN})('Salvar')"); time.sleep(.4)
def fechar(): J(f"({BTN})('Cancelar')"); time.sleep(.2); J(f"({BTN})('Descartar alterações')"); time.sleep(.2)
def fill(i): return J(f"document.querySelectorAll('main svg polygon, main svg circle')[{i}].getAttribute('fill')")
# posição da legenda do mapa em relação ao artboard e ao corpo que rola
LEG="""(()=>{const root=document.querySelector('[data-root]').getBoundingClientRect(); const m=document.querySelector('main'); const mb=m.getBoundingClientRect();
  const l=[...document.querySelectorAll('main div')].find(d=>d.children.length>=3&&d.innerText.indexOf('polígono validado')>=0&&d.innerText.indexOf('inativo')>=0);
  const b=l.getBoundingClientRect(); return {leg:Math.round(b.bottom), root:Math.round(root.bottom), mainBottom:Math.round(mb.bottom), rola:m.scrollHeight>m.clientHeight+1, ov:getComputedStyle(m).overflowY};})()"""
ok=[]
def chk(nome,cond,extra=''):
    ok.append(bool(cond)); print(('OK  ' if cond else 'FALHOU ')+nome+(' · '+str(extra)[:300] if extra else ''), flush=True)
try:
    c.size(1440,1000); c.goto(f'http://127.0.0.1:{p}/CD-01.dc.html',wait=1.2)
    bts=J("[...document.querySelectorAll('button,a')].map(b=>b.innerText.trim())")
    chk('1 sem erro JS e "Importar geometrias" retirado da tela', erro_js()=='' and 'Importar geometrias' not in bts, [erro_js()])
    # ---------- formulários de cadastro novo ----------
    J(f"({CLK})('+ Cadastrar fazenda')"); time.sleep(.35); d=dlg(); L=labels()
    chk('2 fazenda nova: texto de cadastro, sem instrução de inativar e sem campo Situação', 'Cadastre a fazenda' in d and 'Inativa' not in d and 'Altere' not in d and 'Situação' not in L, [d[:160],L])
    J(f"({BTN})('Cancelar')"); time.sleep(.25)
    J(f"({CLK})('Cadastrar talhão','header button')"); time.sleep(.35); d=dlg(); L=labels()
    chk('3 talhão novo: texto de cadastro, sem "Área do polígono" vazio e sem Situação', 'Cadastre o talhão' in d and 'Inativo' not in d and 'Altere' not in d
        and 'Área do polígono' not in L and 'Situação' not in L and 'Área cultivável' in L, [d[:200],L])
    J(f"({BTN})('Cancelar')"); time.sleep(.25)
    # ---------- talhão com parcelas em safra aberta não muda de fazenda ----------
    openrow(1,'T3 Sequeiro'); d=dlg(); L=labels()
    chk('4 edição do T3 mantém texto de edição, polígono e Situação', 'Altere o talhão' in d and 'Área do polígono' in L and 'Situação' in L, [d[:120],L])
    fset('faz','Boa Vista'); save(); al=alerts()
    chk('5 T3 com parcelas na safra aberta não muda de fazenda (erro no campo Fazenda)', aberto() and 'T3 tem parcelas na Safra 2026/27 da Santa Rita. Tire-as no Planejar safra antes de mudar de fazenda.' in al
        and 'Salvo' not in toast(), [al,toast()])
    fechar(); sr=rowtxt(1,'Santa Rita 8 talhões'); bv=rowtxt(1,'Boa Vista 1 talhão')
    chk('6 depois de cancelar: T3 segue na Santa Rita (1.165,0 ha) e verde no mapa', '1.165,0 ha' in (sr or '') and '120,0 ha' in (bv or '') and fill(3)=='#8FD67F', [sr,bv,fill(3)])
    # ---------- talhão sem parcelas muda de fazenda ----------
    openrow(1,'B1 Sequeiro'); fset('faz','Santa Rita'); save()
    chk('7 B1 sem parcelas muda para a Santa Rita', not aberto() and 'Salvo: B1 · Santa Rita.' in toast() and '1.285,0 ha' in (rowtxt(1,'Santa Rita 9 talhões') or ''), [toast(),rowtxt(1,'Santa Rita')])
    # ---------- reativar com toast próprio ----------
    openrow(1,'B1 Sequeiro'); fset('sit','Inativo'); save(); openrow(1,'B1 Inativo'); fset('sit','Ativo'); save()
    chk('8 reativar o B1 avisa que volta ao Planejar safra e ao Mapa', 'B1 reativado: volta ao Planejar safra e ao Mapa.' in toast(), toast())
    # ---------- altura: cadastrar fazenda e talhão não corta o mapa ----------
    lg0=J(LEG)
    J(f"({CLK})('+ Cadastrar fazenda')"); time.sleep(.35); fset('nome','Nova Esperança'); fset('mun','Jataí'); fset('area','600'); save()
    J(f"(()=>{{const r={ROW(1,'Nova Esperança')}; [...r.querySelectorAll('button')].find(b=>b.innerText.trim()==='Cadastrar talhão').click();}})()"); time.sleep(.35)
    fset('t','N1'); fset('decl','250'); save()
    lg=J(LEG); print('   ', toast(), rowtxt(1,'Nova Esperança'))
    chk('9 com uma fazenda e um talhão novos a legenda do mapa aparece inteira no artboard', lg['leg']<=lg['root'] and lg['leg']<=lg['mainBottom'] and lg['ov']=='auto', [lg0,lg])
    for nm in ('Serra Azul','Alvorada'):
        J(f"({CLK})('+ Cadastrar fazenda')"); time.sleep(.35); fset('nome',nm); fset('mun','Jataí'); fset('area','300'); save()
    J("(()=>{const m=document.querySelector('main'); m.scrollTop=m.scrollHeight;})()"); time.sleep(.3); lg2=J(LEG)
    c.shot(os.path.join(HERE,'_probe','cadf_fix_lista_rolagem.png'))
    chk('10 com mais fazendas o corpo rola dentro do artboard e a legenda fica alcançável (nada cortado)', lg2['rola'] and lg2['leg']<=lg2['mainBottom'] and lg2['mainBottom']<=lg2['root'], lg2)
    # ---------- mapa só mostra talhão da fazenda do mapa (cadastro salvo por versão anterior) ----------
    J("""(()=>{const k='talhao-os-cd01-v1'; const s=JSON.parse(localStorage.getItem(k)); s.tal.forEach(t=>{ if(t.id==='T3') t.v.faz='Boa Vista'; }); localStorage.setItem(k,JSON.stringify(s));})()""")
    c.goto(f'http://127.0.0.1:{p}/CD-01.dc.html',wait=1.2)
    J("document.querySelectorAll('main svg polygon')[3].dispatchEvent(new MouseEvent('click',{bubbles:true}))"); time.sleep(.3)
    chk('11 T3 de outra fazenda não aparece no Mapa · Santa Rita nem abre por ele', fill(3)=='#E9EEE6' and fill(2)=='#8FD67F' and not aberto() and erro_js()=='', [fill(3),fill(2),aberto()])
finally:
    c.close(); srv.terminate()
print('RESULTADO:', 'OK' if all(ok) else 'FALHOU', f'{sum(ok)}/{len(ok)}')
