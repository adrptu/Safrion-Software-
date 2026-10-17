# -*- coding: utf-8 -*-
"""Teste CDP da área Colheita (CO-*): faixa de etapas, ciclo da OB-0110 (DEMO-07/19), ciclo da OC-0510, visões do estoque,
retornos do DEMO-08, nova carga com líquido calculado. Rode depois de copiar as telas CO-* para _render/."""
import sys, os, time, subprocess, json
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from cdp import Chrome
from journeys import free
R=os.path.join(os.path.dirname(os.path.abspath(__file__)),'_render'); p=free()
srv=subprocess.Popen(['python3','-m','http.server',str(p),'--bind','127.0.0.1','--directory',R],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(0.8)
c=Chrome(port=free()); J=c.js
CLK="""((t,root)=>{const r=root?document.querySelector(root):document; const n=s=>(s||'').replace(/\\s+/g,' ').trim(); const els=[...r.querySelectorAll('button,a')].filter(e=>e.offsetParent!==null); const e=els.find(x=>n(x.innerText)===t)||els.find(x=>n(x.innerText).startsWith(t));
  if(!e){ const it=[...r.querySelectorAll('.g2mais-menu [role=menuitem]')].find(x=>n(x.textContent)===t||n(x.textContent).startsWith(t)); if(!it) return 'NÃO ACHEI: '+t; it.closest('.g2mais-w').querySelector('.g2mais').click(); it.click(); return 'ok (⋯ da linha)'; }
  e.click(); return 'ok';})"""   # TAB-05 no motor (DS-MODULOS-2, 17/10/2026): a ação da linha mora no ⋯; abre-se o ⋯ e escolhe-se o item, como o usuário
SETV="""((sel,val)=>{const i=document.querySelector(sel); const P=i.tagName==='SELECT'?HTMLSelectElement.prototype:(i.tagName==='TEXTAREA'?HTMLTextAreaElement.prototype:HTMLInputElement.prototype); Object.getOwnPropertyDescriptor(P,'value').set.call(i,val); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true}));})"""
TOAST=lambda: J("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).filter(Boolean).join(' | ')")
BODY=lambda: J("document.body.innerText")
ok=[]
def chk(nome,cond,extra=''):
    ok.append(bool(cond)); print(('OK  ' if cond else 'FALHOU ')+nome+(' · '+str(extra)[:200] if extra else ''))
def clk(t,root=None): r=J(f"({CLK})({json.dumps(t)},{json.dumps(root)})"); time.sleep(.45); return r
def go(t): c.goto(f'http://127.0.0.1:{p}/{t}'); time.sleep(.7)
def fid(k): return J(f"(document.querySelector('aside[role=dialog] [id$=\"_{k}\"]')||{{}}).id")
def setf(k,v): J(f"({SETV})('#{fid(k)}',{json.dumps(v)})"); time.sleep(.15)
try:
    c.size(1440,1000)
    # ---------- faixa de etapas em todas as telas ----------
    for t,cur in [('CO-01',1),('CO-02',2),('CO-02det',2),('CO-03',3),('CO-04',4),('CO-05',5),('CO-05det',5),('CO-06',6),('CO-06det',6),('CO-07',7)]:
        go(t+'.dc.html')
        et=J("[...document.querySelectorAll('nav[aria-label=\"Etapas do processo\"] a')].map(a=>a.getAttribute('href'))")
        atual=J("(document.querySelector('nav[aria-label=\"Etapas do processo\"] [aria-current=step]')||{}).innerText||''").replace('\n',' ')
        chk(f'{t}: faixa com 7 etapas por link e etapa {cur} atual', et==[f'CO-0{i}.dc.html' for i in range(1,8)] and atual.startswith(str(cur)), atual)
        chk(f'{t}: sem erro JS', J("window.__err||''")=='', J("window.__err||''"))
    # ---------- CO-05det · ciclo OB-0110 ----------
    go('CO-05det.dc.html')
    chk('OB-0110 começa Em execução · balanço sem divergência', 'Em execução · balanço sem divergência' in BODY())
    clk('Conferir balanço'); t=TOAST()
    chk('Conferir antes de concluir: ainda não disponível + balanço parcial', 'Ainda não disponível' in t and '12,0 = 9,6 + 1,8 + 0,6' in t, t)
    clk('Finalizar apontamento do turno'); t=TOAST(); chk('Finalizar turno mantém Em execução', 'PERMANECE Em execução' in t, t)
    clk('Concluir execução'); t=TOAST(); b=BODY()
    chk('Concluir execução → Em conferência (aviso)', 'Em conferência' in t, t)
    chk('selo muda e o antigo some', 'Em conferência · balanço a conferir' in b and 'Em execução · balanço sem divergência' not in b)
    STEP="(n)=>{const d=[...document.querySelectorAll('main div')].find(d=>d.children.length===1 && d.innerText.trim().endsWith(n) && d.innerText.length<30); return d?d.children[0].textContent:null;}"
    chk('stepper avança (Em execução ✓ · Em conferência ●)', J(f"({STEP})('Em execução')")=='✓' and J(f"({STEP})('Em conferência')")=='●', (J(f"({STEP})('Em execução')"),J(f"({STEP})('Em conferência')")))
    chk('próxima ação nomeada: Conferir balanço', J("[...document.querySelectorAll('header button')].some(b=>b.innerText.trim()==='Conferir balanço')"))
    clk('Conferir balanço'); t=TOAST(); b=BODY()
    chk('Conferir balanço após concluir: conciliado, sem "Ainda não disponível"', 'Ainda não disponível' not in t and 'sem divergência' in t and '12,0 = 9,6 + 1,8 + 0,6' in t, t)
    chk('nada diz "liberado"', 'liberado' not in b.lower().replace('liberadas',''), '')
    chk('elegível: primário vira Fechar processo', J("[...document.querySelectorAll('header button')].some(b=>b.innerText.trim()==='Fechar processo')"))
    # divergência: editar saída A para 9,5 t → conferir falha
    J("(()=>{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.indexOf('Saída A')>=0); r.querySelector('[role=cell]').click();})()"); time.sleep(.4)
    setf('q','9,5'); clk('Salvar','aside[role=dialog]'); t=TOAST()
    chk('editar saída recalcula divergência', 'divergência de 0,1 t' in t, t)
    chk('volta a exigir conferência', J("[...document.querySelectorAll('header button')].some(b=>b.innerText.trim()==='Conferir balanço')"))
    clk('Conferir balanço'); t=TOAST(); chk('conferir com divergência recusa com motivo', 'Divergência de 0,1 t' in t, t)
    J("(()=>{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.indexOf('Saída A')>=0); r.querySelector('[role=cell]').click();})()"); time.sleep(.4)
    setf('q','9,6'); clk('Salvar','aside[role=dialog]'); clk('Conferir balanço')
    clk('Fechar processo'); t=TOAST(); b=BODY()
    chk('Fechar processo → Encerrada sem liberar lotes', 'Encerrada' in t and 'L39-120/121 seguem Aguardando inspeção' in t and 'Encerrada · lotes Aguardando inspeção' in b, t)
    chk('próxima ação: Encaminhar qualidade (link CO-06)', J("[...document.querySelectorAll('header a')].some(a=>a.innerText.trim()==='Encaminhar qualidade' && a.getAttribute('href')==='CO-06.dc.html')"))
    J("(()=>{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.indexOf('Saída B')>=0); r.querySelector('[role=cell]').click();})()"); time.sleep(.4)
    chk('saídas travadas após encerrar (consulta)', J("!!document.querySelector('aside[role=dialog]') && document.querySelectorAll('aside[role=dialog] input:not([readonly])').length===0"))
    # ---------- CO-05 · origem única ----------
    go('CO-05.dc.html'); b=BODY()
    chk('CO-05: OB-0110 com origem OC-0510 (sem OC-0507)', 'OC-0510' in b and 'OC-0507' not in b)
    # TEXTO-2 (14/10/2026): a regra "fechar processo não libera lote" saiu do corpo para a dica ⓘ da tela (data-dica do header button.g2-info); os dados seguem à vista
    dica=J("(()=>{ const i=document.querySelector('header button.g2-info'); return i?(i.getAttribute('data-dica')||''):''; })()") or ''
    chk('CO-05: âncoras DEMO-19', all(x in b for x in ['balanço 0,0 t · sem divergência','balanço 0 · conciliado','perdas 4,1%','L27-013 bloqueado · INSP-88','Encerrada ≠ liberada']) and 'Fechar processo não libera lote' in dica, dica[:200])
    # ---------- CO-02det · ciclo OC-0510 ----------
    go('CO-02det.dc.html')
    clk('Registrar avanço'); time.sleep(.3)
    chk('Registrar avanço abre formulário novo', J("(document.querySelector('aside[role=dialog] h2')||{}).innerText||''").startswith('Registrar avanço'))
    setf('q','1,2'); clk('Salvar','aside[role=dialog]'); t=TOAST()
    chk('novo avanço acumula na mesma ordem', 'acumulado 10,5 t' in t and 'saldo 1,5 t' in t, t)
    clk('Concluir execução'); t=TOAST(); b=BODY()
    chk('OC-0510 entra em Em conferência', 'Em conferência' in t and 'Em conferência · cargas a conferir' in b, t)
    clk('Conferir cargas'); t=TOAST(); chk('conferir cargas aponta CG-1207', 'CG-1207' in t, t)
    chk('próxima ação: Receber a CG-1207 → CO-04', J("[...document.querySelectorAll('header a')].some(a=>a.innerText.trim()==='Receber a CG-1207' && a.getAttribute('href')==='CO-04.dc.html')"))
    # ---------- CO-03 · nova carga ----------
    go('CO-03.dc.html'); clk('Registrar carga'); time.sleep(.3)
    setf('bru','4000'); setf('tar','1180'); setf('qual','Classe A · calibre 9'); clk('Salvar','aside[role=dialog]'); t=TOAST()
    chk('nova carga CG-1208 com líquido 2.820 kg', 'CG-1208' in t and '2.820 kg' in t, t)
    # ---------- CO-04 · retornos ----------
    go('CO-04.dc.html'); b=BODY()
    chk('CO-04: RC-13 como retorno bloqueado e L27-020 fora de carga comum', 'RC-13' in b and 'L27-020 · soja (retorno)' in b and 'L27-020 · café' not in b)
    clk('Receber bloqueado'); t=TOAST(); chk('Receber bloqueado não aumenta vendável', 'estoque vendável não aumenta' in t, t)
    # TEXTO-2 (14/10/2026): a regra "a entrada não equivale a liberação comercial" saiu do corpo para a dica ⓘ da tela
    dica=J("(()=>{ const i=document.querySelector('header button.g2-info'); return i?(i.getAttribute('data-dica')||''):''; })()") or ''
    chk('CO-04: âncoras DEMO-07', 'L38-118' in b and 'entrada não equivale a liberação comercial' in dica.lower(), dica[:200])
    # ---------- CO-06 · retorno L26-118 ----------
    go('CO-06.dc.html'); b=BODY()
    chk('CO-06: inspeção do L26-118 (RC-12)', 'L26-118 · retorno RC-12' in b and '1 lote bloqueado · decisão até 25/09' in b)
    J("(()=>{const r=[...document.querySelectorAll('[role=row]')].find(r=>r.innerText.indexOf('INSP-93')>=0); [...r.querySelectorAll('button')].find(b=>b.innerText.trim()==='Decidir lote').click();})()"); time.sleep(.4)
    chk('Decidir lote do L26-118 abre destinação na própria tela', 'Destinação do retorno L26-118' in BODY())
    # ---------- CO-07 · visões ----------
    go('CO-07.dc.html'); b=BODY()
    chk('CO-07: L26-118 bloqueado, disponível 0', 'L26-118' in b and 'Bloqueado · aguarda qualidade' in b)
    chk('CO-07: âncoras DEMO-07/19', all(x in b for x in ['9,6 t provisória (PV-031)','0 t até liberar','Bloqueado · INSP-88','0 · bloqueado','3.690 sc 60 kg','Tentar alocar ou expedir o L27-013 falha com motivo']))
    cnt=lambda: J("document.querySelectorAll('[role=table] [role=row].g2r').length")
    clk('Bloqueados'); nb=cnt(); clk('Livres'); nl=cnt(); clk('Comprometidos'); nc=cnt(); clk('Tudo'); nt=cnt()
    chk('visões filtram: Bloqueados 4 · Livres 2 · Comprometidos 3 · Tudo 7', (nb,nl,nc,nt)==(4,2,3,7), (nb,nl,nc,nt))
    J("(()=>{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.indexOf('L26-118')>=0); r.querySelector('[role=cell]').click();})()"); time.sleep(.4)
    chk('linha do estoque abre movimentos (origem), sem edição', 'Movimentos do lote' in BODY() and J("document.querySelectorAll('aside[role=dialog] input:not([readonly])').length")==0)
finally:
    c.close(); srv.terminate()
print(f'\n{sum(ok)}/{len(ok)} verificações OK')
