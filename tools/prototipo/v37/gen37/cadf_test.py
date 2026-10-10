# -*- coding: utf-8 -*-
"""Teste CDP do CD-01 (Fazendas, áreas e talhões): cadastrar fazenda nova com validação, cadastrar talhão na nova fazenda,
"Cadastrar fazenda…" a partir do talhão sem perder o preenchido, subtotal por fazenda, inativar e abrir o detalhe de outro talhão.
Uso: python3 cadf_test.py  (serve _render/; ≤ 15 verificações; cada passo espera ≤ 0,5 s)."""
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
def openrow(ti,txt): J(f"(()=>{{const r={ROW(ti,txt)}; (r.querySelector('[role=cell] span')||r).click();}})()"); time.sleep(.35)
# revisão TABR (09/10/2026, A1): a Situação vem logo depois do talhão ("T1 Em dia Sequeiro …"); a linha é achada pelo código na 1ª célula
def openrow1(ti,cod): J(f"""(()=>{{const r=[...document.querySelectorAll('[role=table]')[{ti}].querySelectorAll('[role=row]')].find(r=>{{const c=r.querySelector('[role=cell]'); return c&&c.innerText.replace(/\\s+/g,' ').replace(/^[▸▾]\\s*/,'').trim()==={json.dumps(cod)};}}); (r.querySelector('[role=cell] span')||r).click();}})()"""); time.sleep(.35)
def rowtxt(ti,txt): return J(f"(()=>{{const r={ROW(ti,txt)}; return r?r.innerText.replace(/\\s+/g,' '):null;}})()")
def fv(k): return J(f"(()=>{{const i=document.querySelector('aside[role=dialog] [id$=\"_{k}\"]'); return i?i.value:null;}})()")
def fset(k,val): J(f"({SETV})('aside[role=dialog] [id$=\"_{k}\"]',{json.dumps(val)})"); time.sleep(.2)
def labels(): return J("[...document.querySelectorAll('aside[role=dialog] label[for]')].map(l=>l.innerText.trim())")
def alerts(): return J("[...document.querySelectorAll('aside [role=alert]')].map(x=>x.innerText).join(' | ')")
def toast(): return J("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).filter(Boolean).join(' | ')")
def aberto(): return J("!!document.querySelector('aside[role=dialog]')")
def erro_js(): return J("[...document.querySelectorAll('.sc-logic-error')].map(e=>e.innerText).join(' | ')")
def save(): J(f"({BTN})('Salvar')"); time.sleep(.4)
def aba(t): J(f"(()=>{{const b=[...document.querySelectorAll('[role=tab]')].find(b=>b.innerText.replace(/\\s+/g,' ').trim().startsWith({json.dumps(t)})); if(b) b.click();}})()"); time.sleep(.35)
def cardtxt(t): return J(f"(()=>{{const c=[...document.querySelectorAll('.cadx-cartao')].find(c=>c.innerText.indexOf({json.dumps(t)})>=0); return c?c.innerText.replace(/\\s+/g,' '):null;}})()")
def opencard(t): J(f"(()=>{{const c=[...document.querySelectorAll('.cadx-cartao')].find(c=>c.innerText.indexOf({json.dumps(t)})>=0); if(c) c.click();}})()"); time.sleep(.35)
ok=[]
def chk(nome,cond,extra=''):
    ok.append(bool(cond)); print(('OK  ' if cond else 'FALHOU ')+nome+(' · '+str(extra)[:300] if extra else ''))
try:
    c.size(1440,1100); c.goto(f'http://127.0.0.1:{p}/CD-01.dc.html',wait=1.2)
    sr=rowtxt(0,'Santa Rita 8 talhões'); bv=rowtxt(0,'Boa Vista 1 talhão')
    chk('1 CD-01 sem erro, subtotal por fazenda e nenhum total somando fazendas',
        erro_js()=='' and '1.165,0 ha' in (sr or '') and '120,0 ha' in (bv or '') and J("document.querySelectorAll('.g2tot').length")==0, [erro_js(),sr,bv])
    # ---------- cadastrar fazenda nova com validação ----------
    aba('Fazendas'); J(f"({CLK})('Cadastrar fazenda','main button')"); time.sleep(.35); save()
    al=alerts(); chk('2 fazenda vazia: erros junto aos campos', 'Informe nome da fazenda.' in al and 'Informe município.' in al and 'Informe área total do imóvel.' in al, al)
    fset('nome','Nova Esperança'); fset('mun','Lucas do Rio Verde'); fset('uf','MT')
    chk('3 fuso sugerido pela UF (MT → Cuiabá)', fv('fuso')=='América/Cuiabá (UTC−4)', fv('fuso'))
    fset('area','600'); fset('posse','Arrendada'); L=labels(); save(); al=alerts()
    chk('4 arrendada pede arrendador, fim do contrato e custo da terra', all(x in L for x in ['Arrendador ou parceiro','Fim do contrato','Custo da terra'])
        and 'Informe o arrendador ou parceiro.' in al and 'Informe o fim do contrato.' in al and fv('nome')=='Nova Esperança', [L,al])
    fset('arrend','José Prado'); fset('fim','2030-06-30'); fset('custo','9'); save()
    cnv=cardtxt('Nova Esperança'); aba('Talhões')
    chk('5 fazenda salva: cartão novo e grupo vazio com "Cadastrar talhão"', not aberto() and 'Nova Esperança' in (cnv or '')
        and 'Cadastrar talhão' in (rowtxt(0,'Nova Esperança') or ''), [toast(),cnv,rowtxt(0,'Nova Esperança')])
    # ---------- cadastrar talhão na nova fazenda ----------
    J(f"({CLK})('Cadastrar talhão','[role=row] button')"); time.sleep(.35)
    chk('6 talhão nasce na fazenda do grupo', fv('faz')=='Nova Esperança', fv('faz'))
    fset('t','N1'); fset('sis','Pivô central'); fset('setor','Bomba do Pivô 1'); fset('decl','700'); save(); al=alerts()
    chk('7 regras do talhão: pivô já usado e área acima da fazenda', 'Bomba do Pivô 1 já irriga o P1' in al and 'somariam 700 ha; a fazenda tem 600 ha' in al, al)
    fset('sis','Sequeiro'); fset('decl','250'); save()
    ne=rowtxt(0,'Nova Esperança 1 talhão')
    chk('8 talhão salvo na nova fazenda com subtotal próprio (Santa Rita não muda)', not aberto() and '250,0 ha' in (ne or '') and '1.165,0 ha' in (rowtxt(0,'Santa Rita 8 talhões') or ''), [ne,toast()])
    # ---------- "Cadastrar fazenda…" a partir do talhão, sem perder o preenchido ----------
    J(f"({CLK})('Cadastrar talhão','main button')"); time.sleep(.35); fset('t','X9'); fset('decl','50'); fset('faz','Cadastrar fazenda…'); time.sleep(.2)
    sub=J("document.querySelector('aside[role=dialog]').innerText")
    fset('nome','Serra Azul'); fset('mun','Jataí'); fset('area','100'); save()
    chk('9 volta ao talhão com a fazenda nova escolhida e o preenchido mantido', 'Ao salvar, você volta ao talhão X9' in sub and fv('t')=='X9' and fv('decl')=='50' and fv('faz')=='Serra Azul', [fv('t'),fv('decl'),fv('faz')])
    save(); chk('10 talhão X9 salvo na Serra Azul', '50,0 ha' in (rowtxt(0,'Serra Azul 1 talhão') or ''), rowtxt(0,'Serra Azul'))
    # ---------- inativar sem excluir ----------
    openrow1(0,'T1'); fset('sit','Inativo'); save(); al=alerts()
    chk('11 T1 com parcelas na safra não inativa', 'T1 tem parcelas na Safra 2026/27 e na Safrinha 2027' in al, al)
    J(f"({BTN})('Cancelar')"); time.sleep(.2); J(f"({BTN})('Descartar alterações')"); time.sleep(.2)
    openrow1(0,'B1'); fset('sit','Inativo'); save()
    b1=rowtxt(0,'B1'); bv=rowtxt(0,'Boa Vista')
    chk('12 B1 inativo: continua na lista com chip e sai do subtotal', not aberto() and 'Inativo' in (b1 or '') and '0,0 ha' in (bv or '') and 'sem talhão ativo' in (bv or ''), [b1,bv])
    aba('Fazendas'); opencard('Boa Vista'); fset('sit','Inativa'); save()
    chk('13 fazenda sem talhão ativo inativa sem excluir', not aberto() and 'Inativa' in (cardtxt('Boa Vista') or ''), cardtxt('Boa Vista'))
    aba('Talhões')
    # ---------- abrir o detalhe de outro talhão ----------
    openrow1(0,'T2'); J(f"({BTN})('Abrir talhão ›')"); time.sleep(2.2)
    for _ in range(8):
        if J("document.readyState")=='complete' and J("!!document.querySelector('header select')"): break
        time.sleep(.4)
    time.sleep(.4)
    hd=J("document.querySelector('header').innerText.replace(/\\s+/g,' ')"); href=J("location.pathname.split('/').pop()+location.hash"); mn=J("document.querySelector('main').innerText.replace(/\\s+/g,' ')")
    chk('14 "Abrir talhão ›" do painel do T2 abre o detalhe do T2 (seletor, crumb e primária do T2 na aba Parcelas)', href=='CD-01det.dc.html#talhao=T2' and J("document.querySelector('header select').value")=='T2'
        and 'T2 · 298 ha' in hd and 'Planejar T2 na safra' in mn and erro_js()=='', [href,hd])
    J(f"({SETV})('header select','B1')"); time.sleep(.4); hd=J("document.querySelector('header').innerText.replace(/\\s+/g,' ')")
    # TABELAS-FOCO (06/10/2026): a data da inativação fica só no estado do cabeçalho; a Situação da ficha é o chip "Inativo" com "Reativar B1"
    mn=J("document.querySelector('main').innerText.replace(/\\s+/g,' ')") or ''
    chk('15 detalhe lê o cadastro salvo na lista: B1 inativo', 'Inativo desde 23/09/2026' in hd and 'Inativo Reativar B1' in mn, [hd[-120:],mn[:200]])
    c.shot(os.path.join(os.path.dirname(os.path.abspath(__file__)),'_probe','cadf_det_b1.png'))
finally:
    c.close(); srv.terminate()
print('RESULTADO:', 'OK' if all(ok) else 'FALHOU', f'{sum(ok)}/{len(ok)}')
