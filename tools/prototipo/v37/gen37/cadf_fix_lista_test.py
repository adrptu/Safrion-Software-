# -*- coding: utf-8 -*-
"""Teste CDP do CD-01 · correções da verificação independente (frente cad-fazendas):
sem rolagem de página (só a tabela ou o mapa rolam dentro do bloco; a legenda do mapa nunca fica cortada), talhão com parcelas em safra aberta não muda de
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
# revisão TABR (09/10/2026, A1): a Situação vem logo depois do talhão ("T3 Em dia Sequeiro …"); a linha é achada pelo código na 1ª célula
def openrow1(ti,cod): J(f"""(()=>{{const r=[...document.querySelectorAll('[role=table]')[{ti}].querySelectorAll('[role=row]')].find(r=>{{const c=r.querySelector('[role=cell]'); return c&&c.innerText.replace(/\\s+/g,' ').replace(/^[▸▾]\\s*/,'').trim()==={json.dumps(cod)};}}); (r.querySelector('[role=cell] span')||r).click();}})()"""); time.sleep(.35)
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
def fill(i): return J(f"(()=>{{const e=document.querySelectorAll('main svg polygon, main svg circle')[{i}]; return e?e.getAttribute('fill'):null;}})()")
def aba(t): J(f"(()=>{{const b=[...document.querySelectorAll('[role=tab]')].find(b=>b.innerText.replace(/\\s+/g,' ').trim().startsWith({json.dumps(t)})); if(b) b.click();}})()"); time.sleep(.35)
def vis(t): J(f"({CLK})({json.dumps(t)},'main [role=group] button')"); time.sleep(.35)
# 16/10/2026 (padrão comum; fazendas e talhões numa árvore só): "Criar fazenda" no cabeçalho (BOT-01/03); o talhão se inclui de dentro da
# fazenda ("Incluir talhão" no painel dela); a linha da fazenda mostra empresa e município na 2ª linha
def novafaz(): J(f"({CLK})('Criar fazenda','header button')"); time.sleep(.35)
def novotal(faz='Santa Rita Santa Rita Agro'):
    J(f"(()=>{{const r={ROW(0,faz)}; (r.querySelector('.g2pw')||r).click();}})()"); time.sleep(.35); J(f"({BTN})('Incluir talhão')"); time.sleep(.35)
# sem rolagem de página: documento e <main> cabem na janela; a área de dados (ou o mapa) rola por dentro do bloco
PAG="""(()=>{const se=document.scrollingElement; const m=document.querySelector('main'); return {doc:se.scrollHeight<=innerHeight, main:m.scrollHeight<=m.clientHeight+1};})()"""
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
    novafaz(); d=dlg(); L=labels()
    chk('2 fazenda nova: texto de cadastro, sem instrução de inativar e sem campo Situação', 'Cadastre a fazenda' in d and 'Inativa' not in d and 'Altere' not in d and 'Situação' not in L, [d[:160],L])
    J(f"({BTN})('Cancelar')"); time.sleep(.25)
    novotal(); d=dlg(); L=labels()
    chk('3 talhão novo: texto de cadastro, sem "Área do polígono" vazio e sem Situação', 'Cadastre o talhão' in d and 'Inativo' not in d and 'Altere' not in d
        and 'Área do polígono' not in L and 'Situação' not in L and 'Área cultivável' in L, [d[:200],L])
    J(f"({BTN})('Cancelar')"); time.sleep(.25)
    # ---------- talhão com parcelas em safra aberta não muda de fazenda ----------
    openrow1(0,'T3'); d=dlg(); L=labels()
    chk('4 edição do T3 mantém texto de edição, polígono e Situação', 'Altere o talhão' in d and 'Área do polígono' in L and 'Situação' in L, [d[:120],L])
    fset('faz','Boa Vista'); save(); al=alerts()
    chk('5 T3 com parcelas na safra aberta não muda de fazenda (erro no campo Fazenda)', aberto() and 'T3 tem parcelas na Safra 2026/27 da Santa Rita. Tire-as no Planejar safra antes de mudar de fazenda.' in al
        and 'Salvo' not in toast(), [al,toast()])
    fechar(); sr=rowtxt(0,'Santa Rita Santa Rita Agro'); bv=rowtxt(0,'Boa Vista Boa Vista Ltda'); vis('Mapa')
    chk('6 depois de cancelar: T3 segue na Santa Rita (1.165,0 ha) e verde no mapa', '1.165,0 ha' in (sr or '') and '120,0 ha' in (bv or '') and fill(3)=='#8FD67F', [sr,bv,fill(3)])
    vis('Lista')
    # ---------- talhão sem parcelas muda de fazenda ----------
    openrow1(0,'B1'); fset('faz','Santa Rita'); save()
    chk('7 B1 sem parcelas muda para a Santa Rita', not aberto() and 'Salvo: B1 · Santa Rita.' in toast() and '1.285,0 ha' in (rowtxt(0,'Santa Rita Santa Rita Agro') or ''), [toast(),rowtxt(0,'Santa Rita Santa Rita Agro')])
    # ---------- reativar com toast próprio ----------
    openrow1(0,'B1'); fset('sit','Inativo'); save(); openrow1(0,'B1'); fset('sit','Ativo'); save()
    chk('8 reativar o B1 avisa que volta ao Planejar safra e ao Mapa', 'B1 reativado: volta ao Planejar safra e ao Mapa.' in toast(), toast())
    # ---------- sem rolagem de página: cadastrar fazendas e talhões não faz a página rolar; lista e mapa rolam no bloco ----------
    novafaz(); fset('nome','Nova Esperança'); fset('mun','Jataí'); fset('area','600'); save()
    J(f"(()=>{{const r={ROW(0,'Nova Esperança')}; [...r.querySelectorAll('button')].find(b=>b.innerText.trim()==='Incluir talhão').click();}})()"); time.sleep(.35)
    fset('t','N1'); fset('decl','250'); save()
    pg=J(PAG); rola=J("(()=>{const r=document.querySelector('main .g2rola'); return r?[r.scrollHeight,r.clientHeight,getComputedStyle(r).overflowY]:null;})()")
    print('   ', toast(), rowtxt(0,'Nova Esperança'))
    chk('9 com uma fazenda e um talhão novos a página não rola; a tabela rola dentro do bloco', pg['doc'] and pg['main'] and rola and rola[2]=='auto', [pg,rola])
    for nm in ('Serra Azul','Alvorada'):
        novafaz(); fset('nome',nm); fset('mun','Jataí'); fset('area','300'); save()
    vis('Mapa'); time.sleep(.2)
    # o mapa ocupa a área da lista na classe rola do motor (antes .cadx-rola, 16/10/2026)
    J("(()=>{const r=[...document.querySelectorAll('main .rola')].pop(); if(r) r.scrollTop=r.scrollHeight;})()"); time.sleep(.3)
    lg2=J("""(()=>{const l=[...document.querySelectorAll('main div')].filter(d=>d.children.length>=3&&d.innerText.indexOf('polígono validado')>=0&&d.innerText.indexOf('inativo')>=0).pop();
      const r=l&&l.closest('.rola'); if(!l||!r) return null; const b=l.getBoundingClientRect(), rb=r.getBoundingClientRect(); return {leg:Math.round(b.bottom), rola:Math.round(rb.bottom)};})()""")
    pg=J(PAG); c.shot(os.path.join(HERE,'_probe','cadf_fix_lista_rolagem.png')); vis('Lista')
    chk('10 com mais fazendas a página continua sem rolar e a legenda do mapa fica inteira dentro do bloco', pg['doc'] and pg['main'] and lg2 and lg2['leg']<=lg2['rola'], [pg,lg2])
    # ---------- mapa só mostra talhão da fazenda do mapa (cadastro salvo por versão anterior) ----------
    J("""(()=>{const k='talhao-os-cd01-v1'; const s=JSON.parse(localStorage.getItem(k)); s.tal.forEach(t=>{ if(t.id==='T3') t.v.faz='Boa Vista'; }); localStorage.setItem(k,JSON.stringify(s));})()""")
    c.goto(f'http://127.0.0.1:{p}/CD-01.dc.html',wait=1.2); vis('Mapa')
    J("document.querySelectorAll('main svg polygon')[3].dispatchEvent(new MouseEvent('click',{bubbles:true}))"); time.sleep(.3)
    chk('11 T3 de outra fazenda não aparece no Mapa · Santa Rita nem abre por ele', fill(3)=='#E9EEE6' and fill(2)=='#8FD67F' and not aberto() and erro_js()=='', [fill(3),fill(2),aberto()])
finally:
    c.close(); srv.terminate()
print('RESULTADO:', 'OK' if all(ok) else 'FALHOU', f'{sum(ok)}/{len(ok)}')
