# -*- coding: utf-8 -*-
"""Teste CDP do CD-01det (detalhe do talhão). É a parte CD-01det do cd0102test.py ajustada ao comportamento novo:
parcelas em consulta com origem no Planejar safra (antes eram editadas aqui), resumo por safra pela área cultivável (312 ha, não o
polígono de 312,4 ha), "Dividir em parcelas" leva ao SAF e a área cultivável não fica abaixo do alocado. Mais: aba Geometria sem
editor simulado fora da Lagoa Grande (CADUX, achado 5: a frase do limite, a mesma do CD-01) e seletor de talhão no cabeçalho. ≤ 15 verificações.
CADUX P2 (09/10/2026): a ficha de 1 linha do talhão (grade g_idt) virou o cabeçalho do detalhe (DS-58: fazenda, sistema, área, polígono
e versão numa linha, com "Editar talhão"); a grade das parcelas passou a ser a única da página (índice 0) e o talhão se edita pelo botão."""
import sys, os, time, subprocess, json
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
def openrow(ti,txt): J(f"(()=>{{const r={ROW(ti,txt)}; (r.querySelector('.g2alvo')||r.querySelector('[role=cell] span')||r).click();}})()"); time.sleep(.35)   # CADUX: alvo da linha (BOT-07)
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
    s1=rowtxt(0,'Safra 2026/27'); s2=rowtxt(0,'Safrinha 2027')
    # TABELAS-FOCO (06/10/2026): a linha da safra mostra Área (alocada) e Livre em colunas próprias ("312 ha | 0 ha"), em vez de "312 de 312 ha · Área conferida"
    chk('2 resumo por safra pela área cultivável (312 ha), não pelo polígono (312,4 ha)', '312 ha 0 ha' in s1 and 'Em planejamento' in s1 and '160 ha 152 ha' in s2 and 'Rascunho' in s2 and '312,4' not in s1+s2, [s1,s2])
    openrow(0,'T1-B'); d=dlg()
    chk('3 T1-B abre em consulta com origem no Planejar safra', 'Parcela · T1-B' in d and 'ORIGEM' in d and 'Planejar safra › Safra 2026/27 › T1-B' in d
        and J("[...document.querySelectorAll('aside[role=dialog] a')].some(a=>a.getAttribute('href')==='SAF.dc.html')"), d)
    ed=J("document.querySelectorAll('aside[role=dialog] input:not([readonly]), aside[role=dialog] select:not([disabled])').length")
    chk('4 parcela sem campo editável e sem Salvar (muda só no Planejar safra)', ed==0 and 'Salvar' not in d and 'mudam no Planejar safra' in d, [ed,d])
    J(f"({BTN})('Fechar')"); time.sleep(.25)
    dv=J("(()=>{const a=[...document.querySelectorAll('main a')].find(a=>a.innerText.trim().startsWith('Planejar T1 na safra')); return a?a.getAttribute('href'):null;})()")
    # CADUX P2 (09/10/2026): o link leva à safra aberta da fazenda do talhão no formato X-LNK da NAV-2 (SAF.dc.html#saf=&passo=&cult=), não à tela vazia;
    # é link de navegação com "›" (BOT-08), não botão verde
    chk('5 "Planejar T1 na safra" (aba Parcelas) leva ao SAF da safra aberta da Santa Rita e "Cadastrar parcela" saiu', (dv or '').startswith('SAF.dc.html#saf=S2627&passo=') and 'Cadastrar parcela' not in head()+main(), dv)
    J(f"({CLK})('Editar talhão','main button')"); time.sleep(.35); fset('decl','300'); J(f"({BTN})('Salvar')"); time.sleep(.35); al=alerts()
    chk('6 área cultivável abaixo do alocado é barrada (regra da área cultivável)', 'As parcelas da Safra 2026/27 somam 312 ha; reduza-as no Planejar safra antes.' in al, al)
    J(f"({BTN})('Cancelar')"); time.sleep(.2); J(f"({BTN})('Descartar alterações')"); time.sleep(.2)
    J("(()=>{const b=document.querySelector('aside[role=dialog] button[aria-label=Fechar]'); b&&b.click();})()"); time.sleep(.25)   # CADUX: Cancelar volta à consulta do talhão; × fecha
    # ---------- Geometria da T1-B (CADUX, achado 5 da revisão; R18/AC-25) ----------
    # Antes: "Definir polígono da T1-B" abria um editor simulado (importar/desenhar, prévia, motivo) que gravava uma versão "validada" que o
    # CD-01 contradizia. Agora o polígono só se define onde o Mapa IN-04 abre a fazenda (Lagoa Grande); na Santa Rita a aba diz o limite
    aba('Geometria'); m=main()
    chk('7 Santa Rita: a aba Geometria diz o limite (mapa da fazenda ainda não existe) e não oferece "Definir polígono"',
        'Polígono da T1-B pendente: o mapa da Santa Rita ainda não existe no protótipo; o planejamento usa a área cultivável.' in m and 'Definir polígono' not in m, m[-500:])
    chk('8 nenhum editor de polígono simulado na página (sem "Salvar polígono", "Gerar prévia" nem "Motivo da diferença")',
        J("!document.querySelector('#pg_mot')") and 'Salvar polígono' not in J("document.body.innerText") and 'Gerar prévia' not in J("document.body.innerText") and 'Desenhar no mapa' not in m, m[-300:])
    chk('9 versões em consulta como estão: v3 atual e v2 para as O.S. já emitidas', 'Atual v3 · 312,4 ha' in m and 'Consulta v2 · 311,8 ha' in m, m[-600:])
    aba('Parcelas'); hd=head()
    chk('10 estado continua "T1-B sem polígono" (nada foi validado de mentira); a aba Parcelas leva ao SAF da safra aberta', 'T1-B sem polígono' in hd and 'Planejar T1 na safra' in main()
        and (J("(()=>{const a=[...document.querySelectorAll('main a')].find(a=>a.innerText.trim().startsWith('Planejar T1 na safra')); return a&&a.getAttribute('href');})()") or '').startswith('SAF.dc.html#saf=S2627'), hd)
    # ---------- seletor: outro talhão, sem misturar linhas ----------
    J(f"({SETV})('header select','T4')"); time.sleep(.35); m=main()
    # Área e Livre em colunas próprias (TABELAS-FOCO): Safra 2026/27 204 ha alocados e 0 livre; Safrinha 2027 0 alocado e 204 ha livres
    chk('11 seletor troca para T4: só as safras do T4 e a primária do T4', 'T1-A' not in m and 'Safra 2026/27 204 ha 0 ha' in m and 'Safrinha 2027 0 ha 204 ha' in m and 'T4 · 204 ha' in head() and 'Planejar T4 na safra' in m, [m[:400],head()])
    J(f"({SETV})('header select','B1')"); time.sleep(.35); aba('Geometria'); m=main()
    # CADUX (achado 5): antes, "Definir polígono do B1" salvava uma v1 simulada e o CD-01 dizia "sem polígono"; agora as duas telas dizem o mesmo
    chk('12 B1 (Boa Vista): sem "Definir polígono do B1"; a aba diz que o mapa da Boa Vista ainda não existe e o estado segue "B1 sem polígono"',
        'Definir polígono' not in m and 'Polígono do B1 pendente: o mapa da Boa Vista ainda não existe no protótipo' in m and 'B1 sem polígono' in head(), [m[-400:], head()])
    c.goto(f'http://127.0.0.1:{p}/CD-01det.dc.html?nova=1#talhao=ZZ',wait=1.2)
    # CADUX (09/10/2026, SEL-02 da DEC-0910-01): o aviso é neutro (não diz se o talhão existe), em role=alert, com a saída para a lista
    chk('13 talhão desconhecido não abre outro em silêncio', 'Talhão “ZZ” indisponível' in main() and 'Nada foi aberto' in main() and J("!!document.querySelector('main [role=alert]')")
        and J("document.querySelector('header select').value")=='' and 'Escolha um talhão' in head() and 'Ver todas as fazendas' in main(), [main()[:200],head()])
    c.shot(os.path.join(os.path.dirname(os.path.abspath(__file__)),'_probe','cadf_det_nf.png'))
finally:
    c.close(); srv.terminate()
print('RESULTADO:', 'OK' if all(ok) else 'FALHOU', f'{sum(ok)}/{len(ok)}')
