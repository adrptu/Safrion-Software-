# -*- coding: utf-8 -*-
"""Teste CDP do CD-01det (detalhe do talhão). É a parte CD-01det do cd0102test.py ajustada ao comportamento novo:
parcelas em consulta com origem no Planejar safra (antes eram editadas aqui), resumo por safra pela área cultivável (312 ha, não o
polígono de 312,4 ha), "Dividir em parcelas" leva ao SAF e a área cultivável não fica abaixo do alocado. Mais: "Definir polígono"
(prévia, motivo acima de 1 %, nova versão preservando a anterior) e seletor de talhão no cabeçalho. ≤ 15 verificações."""
import re, sys, os, time, subprocess, json
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from cdp import Chrome
from journeys import free
R=sys.argv[1] if len(sys.argv)>1 else os.path.join(os.path.dirname(os.path.abspath(__file__)),'_render'); p=free()
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
def alerts(): return J("[...document.querySelectorAll('aside [role=alert]')].map(x=>x.innerText).join(' | ')")
def toast(): return J("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).filter(Boolean).join(' | ')")
def head(): return J("document.querySelector('header').innerText.replace(/\\s+/g,' ')")
def main(): return J("document.querySelector('main').innerText.replace(/\\s+/g,' ')")
def erro_js(): return J("[...document.querySelectorAll('.sc-logic-error')].map(e=>e.innerText).join(' | ')")
def aba(t): J(f"(()=>{{const b=[...document.querySelectorAll('[role=tab]')].find(b=>b.innerText.replace(/\\s+/g,' ').trim().startsWith({json.dumps(t)})); if(b) b.click();}})()"); time.sleep(.35)
ok=[]
def chk(nome,cond,extra=''):
    ok.append(bool(cond)); print(('OK  ' if cond else 'FALHOU ')+nome+(' · '+str(extra)[:300] if extra else ''))
try:
    c.size(1440,1100); c.goto(f'http://127.0.0.1:{p}/CD-01det.dc.html',wait=1.2)
    chk('1 CD-01det sem erro JS e T1 escolhido às claras no seletor', erro_js()=='' and J("document.querySelector('header select').value")=='T1' and 'T1-B sem polígono' in head(), [erro_js(),head()])
    s1=rowtxt(1,'Safra 2026/27'); s2=rowtxt(1,'Safrinha 2027')
    # TABELAS-FOCO (06/10/2026): a linha da safra mostra Área (alocada) e Livre em colunas próprias ("312 ha | 0 ha"), em vez de "312 de 312 ha · Área conferida"
    chk('2 resumo por safra pela área cultivável (312 ha), não pelo polígono (312,4 ha)', '312 ha 0 ha' in s1 and 'Em planejamento' in s1 and '160 ha 152 ha' in s2 and 'Rascunho' in s2 and '312,4' not in s1+s2, [s1,s2])
    openrow(1,'T1-B'); d=dlg()
    chk('3 T1-B abre em consulta com origem no Planejar safra', 'Parcela · T1-B' in d and 'ORIGEM' in d and 'Planejar safra › Safra 2026/27 › T1-B' in d
        and J("[...document.querySelectorAll('aside[role=dialog] a')].some(a=>a.getAttribute('href')==='SAF.dc.html')"), d)
    ed=J("document.querySelectorAll('aside[role=dialog] input:not([readonly]), aside[role=dialog] select:not([disabled])').length")
    chk('4 parcela sem campo editável e sem Salvar (muda só no Planejar safra)', ed==0 and 'Salvar' not in d and 'mudam no Planejar safra' in d, [ed,d])
    J(f"({BTN})('Fechar')"); time.sleep(.25)
    # 16/10/2026 (BOT-08): "Planejar T1 na safra ›" só leva a outra tela: é link secundário na barra das parcelas, não verde
    dv=J("(()=>{const a=[...document.querySelectorAll('main a')].find(a=>a.innerText.trim()==='Planejar T1 na safra ›'); return a?a.getAttribute('href'):null;})()")
    chk('5 "Planejar T1 na safra" (aba Parcelas) leva ao SAF e "Cadastrar parcela" saiu', dv=='SAF.dc.html' and 'Cadastrar parcela' not in head()+main(), dv)
    openrow(0,'Santa Rita'); fset('decl','300'); J(f"({BTN})('Salvar')"); time.sleep(.35); al=alerts()
    chk('6 área cultivável abaixo do alocado é barrada (regra da área cultivável)', 'As parcelas da Safra 2026/27 somam 312 ha; reduza-as no Planejar safra antes.' in al, al)
    J(f"({BTN})('Cancelar')"); time.sleep(.2); J(f"({BTN})('Descartar alterações')"); time.sleep(.2)
    # ---------- Definir polígono da T1-B ----------
    # 16/10/2026 (BOT-01): "Definir polígono da T1-B" é a primária do cabeçalho do detalhe (antes na barra da aba Geometria)
    aba('Geometria'); J(f"({CLK})('Definir polígono da T1-B','header button')"); time.sleep(.3); J(f"({BTN})('Salvar polígono')"); time.sleep(.25)
    chk('7 painel abre e não salva sem prévia', 'Definir polígono da T1-B' in dlg() and 'Gere a prévia antes de salvar.' in alerts(), dlg())
    J(f"({BTN})('Desenhar no mapa')"); time.sleep(.2); J(f"({BTN})('Gerar prévia')"); time.sleep(.25); d=dlg()
    J(f"({BTN})('Salvar polígono')"); time.sleep(.25); al=alerts()
    chk('8 desenho simulado: prévia com diferença −2,6 % pede motivo', 'Área do polígono 148,0 ha' in d and '−4,0 ha · 2,6 %' in d and 'Motivo da diferença' in d and 'Informe o motivo da diferença de 2,6 %.' in al, [d,al])
    J(f"({SETV})('#pg_mot','Carreador ou estrada')"); time.sleep(.2); J(f"({BTN})('Salvar polígono')"); time.sleep(.4)
    ts=toast(); vs=main()
    chk('9 nova versão v4 atual e v3 em consulta para as O.S. já emitidas', 'v4 do T1 é a atual; a v3 fica em consulta' in ts and 'Atual v4 · 312,4 ha' in vs and 'Consulta v3 · 312,4 ha' in vs and 'Carreador ou estrada' in vs, [ts,vs[-600:]])
    aba('Parcelas'); t1b=rowtxt(1,'T1-B'); hd=head()
    chk('10 T1-B validada; estado validado, sem primária pendente e o link "Planejar T1 na safra ›" na aba Parcelas', 'Polígono validado' in t1b and 'Polígono validado' in hd and 'Planejar T1 na safra' in main()
        and 'Definir polígono' not in hd
        and J("(()=>{const a=[...document.querySelectorAll('main a')].find(a=>a.innerText.trim()==='Planejar T1 na safra ›'); return a&&a.getAttribute('href');})()")=='SAF.dc.html', [t1b,hd])
    # ---------- seletor: outro talhão, sem misturar linhas ----------
    J(f"({SETV})('header select','T4')"); time.sleep(.35); m=main()
    # Área e Livre em colunas próprias (TABELAS-FOCO): Safra 2026/27 204 ha alocados e 0 livre; Safrinha 2027 0 alocado e 204 ha livres
    # revisão TABR (09/10/2026, A1): a Situação da safra vem logo depois do nome ("Safra 2026/27 <situação> … 204 ha 0 ha")
    chk('11 seletor troca para T4: só as safras do T4 e a primária do T4', 'T1-A' not in m and re.search(r'Safra 2026/27 [^0-9]{0,60}204 ha 0 ha', m) and re.search(r'Safrinha 2027 [^0-9]{0,60}0 ha 204 ha', m) and 'T4 · 204 ha' in head() and 'Planejar T4 na safra' in m, [m[:400],head()])
    J(f"({SETV})('header select','B1')"); time.sleep(.35); aba('Geometria'); J(f"({CLK})('Definir polígono do B1','header button')"); time.sleep(.3)
    J(f"({BTN})('Gerar prévia')"); time.sleep(.2); J(f"({BTN})('Cancelar')"); time.sleep(.2); w=alerts()
    J(f"({BTN})('Continuar editando')"); time.sleep(.2); J(f"({BTN})('Salvar polígono')"); time.sleep(.4)
    b1=rowtxt(0,'Boa Vista')
    chk('12 B1: fechar com prévia avisa; importar dentro de 1 % salva a v1 e preenche o polígono', 'Há alterações não salvas.' in w and '119,6 ha' in (b1 or '') and 'v1' in (b1 or '') and 'Polígono validado' in head(), [w,b1,toast()])
    c.goto(f'http://127.0.0.1:{p}/CD-01det.dc.html?nova=1#talhao=ZZ',wait=1.2)
    chk('13 talhão desconhecido não abre outro em silêncio', 'Talhão não encontrado' in main() and J("document.querySelector('header select').value")=='' and 'Escolha um talhão' in head(), [main()[:200],head()])
    c.shot(os.path.join(os.path.dirname(os.path.abspath(__file__)),'_probe','cadf_det_nf.png'))
finally:
    c.close(); srv.terminate()
print('RESULTADO:', 'OK' if all(ok) else 'FALHOU', f'{sum(ok)}/{len(ok)}')
