# -*- coding: utf-8 -*-
"""Teste CDP de CD-05 (defeitos do verificador, rodada 2): motivo da suspensão limpo ao reativar; menu do filtro de coluna só com
valores das linhas do filtro de papel; troca de papel sem chip de filtro inativo; clientes de Vendas e Gestão cadastrados no CD-05.
15 verificações. Uso: python3 cadp_fix_test.py (serve _render/ e abre o Chrome headless).
TABELAS-FOCO (06/10/2026): uma variável por coluna. "Parceiro · CPF/CNPJ" virou Parceiro e CPF/CNPJ; a situação do fornecedor é o chip
"Homologado" (os grupos ficam na coluna Grupos homologados do filtro Fornecedores); Papéis é multivalorada (filtra por item: Cliente pega
também Coop. Vale, que é Fornecedor e Cliente); o motivo da suspensão tem coluna própria logo depois da situação. O menu de filtro é o do
padrão Excel (rascunho com Limpar/OK): o filtro de um valor só é aplicado com Limpar, marcar e OK (helper SO)."""
import sys, os, time, subprocess, json
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from cdp import Chrome
from journeys import free
from comp_lib import cv_todas_sempre
R=os.path.join(os.path.dirname(os.path.abspath(__file__)),'_render'); p=free()
srv=subprocess.Popen(['python3','-m','http.server',str(p),'--bind','127.0.0.1','--directory',R],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(0.8)
c=Chrome(port=free()); J=c.js; cv_todas_sempre(c)   # V2-3: lê Situação do papel e Motivo da suspensão, fora do padrão das colunas
SETV="""((sel,val)=>{const i=document.querySelector(sel); const P=i.tagName==='SELECT'?HTMLSelectElement.prototype:HTMLInputElement.prototype; Object.getOwnPropertyDescriptor(P,'value').set.call(i,val); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true}));})"""
SETK=lambda k,val: J(f"({SETV})('#fx_g_forn_{k}',{json.dumps(val)})") or time.sleep(.15)
BTN=lambda t: J(f"(()=>{{const b=[...document.querySelectorAll('aside[role=dialog] button')].find(b=>b.innerText.trim()==={json.dumps(t)}); if(b){{b.click(); return true;}} return false;}})()") or time.sleep(.4)
ANY=lambda t: J(f"(()=>{{const b=[...document.querySelectorAll('button')].find(b=>b.innerText.trim()==={json.dumps(t)}); if(b){{b.click(); return true;}} return false;}})()") or time.sleep(.3)
ABERTO=lambda: J("!!document.querySelector('aside[role=dialog]')")
ROWS="[...document.querySelectorAll('[role=table]')[0].querySelectorAll('[role=row].g2ed')]"
LIN=lambda n: J(f"(()=>{{const r={ROWS}.find(r=>r.innerText.indexOf({json.dumps(n)})>=0); return r?r.innerText.replace(/\\s+/g,' '):'';}})()")
ABRE=lambda n: J(f"(()=>{{const r={ROWS}.find(r=>r.innerText.indexOf({json.dumps(n)})>=0); (r.querySelector('[role=cell] span')||r).click();}})()") or time.sleep(.4)
NOMES=lambda: J(f"{ROWS}.map(r=>r.querySelector('[role=cell]').innerText.split('\\n')[0].trim())")
FIL=lambda t: J(f"[...document.querySelectorAll('[role=group][aria-label=\"Filtrar por papel\"] button')].find(b=>b.innerText.trim().startsWith({json.dumps(t)})).click()") or time.sleep(.35)
MENU=lambda col: J(f"document.querySelector('[aria-label=\"Filtrar {col}\"]').click()") or time.sleep(.35)
OPTS="[...document.querySelectorAll('[data-root] label')].filter(e=>!e.closest('[role=table]')&&!e.closest('aside')&&e.querySelector('input[type=checkbox]')).map(e=>e.innerText.replace(/\\s+/g,' ').trim())"
# valor do menu de filtro: 1ª linha do rótulo (a 2ª é a contagem); exato=True compara o valor inteiro
MARCA=lambda ini,exato=False: J(f"[...document.querySelectorAll('[data-root] label')].find(l=>{{ const t=l.innerText.split('\\n')[0].trim(); return !l.closest('aside')&&l.querySelector('input[type=checkbox]')&&({'true' if exato else 'false'}?t==={json.dumps(ini)}:t.startsWith({json.dumps(ini)})); }}).querySelector('input').click()") or time.sleep(.3)
TOPO="document.querySelectorAll('[role=table]')[0].parentElement.parentElement.innerText.split(/PARCEIRO\\s*⇅/i)[0].replace(/\\s+/g,' ').trim()"
ERRO_MOTIVO="(()=>{const i=document.getElementById('fx_g_forn_motivo'); let n=i; for(let k=0;k<4&&n;k++){ n=n.parentElement; const a=n&&n.querySelector('[role=alert]'); if(a) return a.innerText; } return ''; })()"
NEED="(()=>{const R=document.querySelector('[data-root]'); const h0=R.style.height; R.style.height='auto'; const h=Math.ceil(R.getBoundingClientRect().height); R.style.height=h0; return h;})()"
def SO(col,val):
    """filtro de coluna com um só valor: abre o menu, Limpar, marca o valor exato e OK"""
    MENU(col); ANY('Limpar'); MARCA(val,True); ANY('OK')
def soma(opts): return sum(int(o.rsplit(' ',1)[1]) for o in opts)
ok=[]
def chk(nome,cond,extra=''):
    ok.append(bool(cond)); print(('OK  ' if cond else 'FALHOU ')+nome+(' · '+str(extra)[:500] if extra!='' else ''))
try:
    c.size(1440,1000)
    # ---- clientes de Vendas (VE-04, VE-05) e Gestão (GE-05) ----
    c.goto(f'http://127.0.0.1:{p}/VE-04.dc.html'); time.sleep(.5)
    ve4=set(J("[...document.querySelectorAll('[role=table]')[0].querySelectorAll('[role=row]')].slice(1).map(r=>(r.querySelectorAll('[role=cell]')[1]||{innerText:''}).innerText.trim()).filter(Boolean)"))
    ve4|=set(J("[...document.querySelectorAll('select')].filter(s=>[...s.options].some(o=>o.text==='Atacado Bom Preço')).flatMap(s=>[...s.options].map(o=>o.text))"))
    c.goto(f'http://127.0.0.1:{p}/VE-05.dc.html'); time.sleep(.5)
    ob=J("[...document.querySelectorAll('[role=table]')[0].querySelectorAll('[role=row]')].slice(1).map(r=>(r.querySelector('[role=cell]')||{innerText:''}).innerText.split('\\n').map(x=>x.trim()).filter(Boolean))")
    ve5_cli={x[1] for x in ob if len(x)>1 and x[0].endswith('venda')}; ve5_bar={x[1] for x in ob if len(x)>1 and x[0].endswith('barter')}
    c.goto(f'http://127.0.0.1:{p}/GE-05.dc.html'); time.sleep(.5)
    ge5=set(J("[...document.querySelectorAll('[role=table]')[0].querySelectorAll('[role=row].g2r:not(.g2kid)')].map(r=>r.querySelector('[role=cell]').innerText.split('\\n').map(x=>x.replace('▾','').replace('▸','').trim()).filter(Boolean)[0])"))
    c.goto(f'http://127.0.0.1:{p}/CD-05.dc.html'); time.sleep(.6)
    chk('1 sem erro JS', J("window.__err||''")=='', J("window.__err||''"))
    FIL('Clientes'); cli=set(NOMES()); FIL('Fornecedores'); forn=set(NOMES()); FIL('Todos')
    falta=sorted((ve4|ge5|ve5_cli)-cli)
    chk('2 clientes com pedido (VE-04), contrato de venda (VE-05) e título (GE-05) existem no CD-05 como Cliente',
        not falta and {'Coop Grão Sul','Atacado Bom Preço','CD Horti'}<=cli and len(ve4)>=5 and len(ge5)>=4, f'faltam {falta} · VE-04 {sorted(ve4)} · GE-05 {sorted(ge5)} · VE-05 {sorted(ve5_cli)}')
    chk('3 contraparte de barter (VE-05) cadastrada como Fornecedor; Coopergrão, sem uso em outra tela, saiu', ve5_bar and ve5_bar<=forn and 'Coopergrão' not in J("document.body.innerText"), f'{sorted(ve5_bar)} · {sorted(forn)}')
    # ---- motivo da suspensão: reativar limpa; nova suspensão exige motivo novo ----
    ABRE('Casa do Adubo'); BTN('Suspender parceiro'); SETK('motivo','Entrega fora do prazo'); BTN('Salvar')
    t=LIN('Casa do Adubo'); chk('4 suspenso com motivo na linha', not ABERTO() and 'Suspenso Entrega fora do prazo' in t, t)
    ABRE('Casa do Adubo'); BTN('Reativar parceiro'); BTN('Salvar')
    # revisão TABR (09/10/2026, A1): a situação do papel vem logo depois do parceiro
    t=LIN('Casa do Adubo'); chk('5 reativado: linha volta a Homologado, sem o motivo', not ABERTO() and t.startswith('Casa do Adubo') and 'Homologado' in t and 'Suspenso' not in t and 'Entrega fora do prazo' not in t, t)   # V2-3: a ordem é a do padrão (Papéis, Contato) e depois as demais
    ABRE('Casa do Adubo'); BTN('Suspender parceiro')
    mv=J("document.getElementById('fx_g_forn_motivo').value"); hp=J("document.getElementById('fx_g_forn_motivo').parentElement.parentElement.innerText.replace(/\\s+/g,' ')")
    chk('6 nova suspensão começa com motivo vazio e a ajuda não promete histórico', mv=='' and 'Aparece na listagem enquanto durar a suspensão.' in hp and 'histórico' not in hp, f'{mv!r} · {hp}')
    BTN('Salvar'); em=J(ERRO_MOTIVO)
    chk('7 salvar sem motivo novo é barrado junto ao campo', ABERTO() and em=='Informe motivo da suspensão.' and 'Suspenso' not in LIN('Casa do Adubo'), em)
    BTN('Cancelar'); BTN('Descartar alterações')
    # ---- menu de filtro de coluna dentro do filtro de papel ----
    FIL('Clientes'); MENU('Situação do papel'); o1=J(OPTS)
    chk('8 Clientes · Situação do papel: sem "—" dos não clientes, contagens somam 7', o1 and not any(x.startswith('—') for x in o1) and soma(o1)==7, o1)
    MENU('Papéis'); o2=J(OPTS)
    chk('9 Clientes · Papéis: só valores das 7 linhas de cliente (Coop. Vale também é Fornecedor), sem valor zerado', o2==['Cliente 7','Fornecedor 1'], o2)
    ANY('Cancelar')
    # ---- troca de papel com filtro de coluna ----
    FIL('Todos'); SO('Papéis','Cliente')
    a=J(TOPO); na=len(NOMES())
    FIL('Fornecedores'); b=J(TOPO); nb=len(NOMES())
    chk('10 Papéis: Cliente em Todos; em Fornecedores o filtro da coluna que sai é limpo (sem chip "papeis:")',
        'Papéis: Cliente' in a and na==7 and 'Papéis:' not in b and 'Limpar filtros' not in b and nb==8, f'{a} ({na}) → {b} ({nb})')
    FIL('Todos'); d=J(TOPO); nd=len(NOMES())
    chk('11 de volta a Todos o filtro limpo não reaparece', 'Papéis:' not in d and nd==20, f'{d} ({nd})')
    SO('Parceiro','Fertisul'); FIL('Fornecedores'); e=J(TOPO); ne=NOMES()
    chk('12 filtro de coluna comum às duas grades continua valendo em Fornecedores', 'Parceiro: Fertisul' in e and ne==['Fertisul'], f'{e} · {ne}')
    ANY('Limpar filtros'); FIL('Clientes'); SO('Situação do papel','Limite vencido'); g=J(TOPO); ng=len(NOMES())
    FIL('Todos'); h=J(TOPO); nh=len(NOMES())
    chk('13 filtro de Situação do papel (texto muda com o papel) é limpo ao trocar de papel', 'Situação do papel:' in g and ng==1 and 'Situação do papel:' not in h and nh==20, f'{g} ({ng}) → {h} ({nh})')
    # ---- altura da prancheta com 20 parceiros ----
    n1=J(NEED); FIL('Fornecedores'); n2=J(NEED); hp=J("parseInt(getComputedStyle(document.querySelector('[data-root]')).height)")
    chk('14 conteúdo cabe na prancheta em Todos e em Fornecedores', max(n1,n2)<=hp, f'Todos {n1} · Fornecedores {n2} · prancheta {hp}')
    chk('15 sem erro JS ao fim', J("window.__err||''")=='', J("window.__err||''"))
finally:
    c.close(); srv.terminate()
print('RESULTADO:', 'OK' if all(ok) else 'FALHOU', f'{sum(ok)}/{len(ok)}')
