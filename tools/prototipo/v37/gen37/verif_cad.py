# -*- coding: utf-8 -*-
"""Verificação independente (CD-05, CD-02, CD-01det): cenários além dos testes do implementador."""
import sys, os, time, subprocess, json
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from cdp import Chrome
from journeys import free
R=os.path.join(os.path.dirname(os.path.abspath(__file__)),'_render'); p=free()
srv=subprocess.Popen(['python3','-m','http.server',str(p),'--bind','127.0.0.1','--directory',R],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(0.8)
c=Chrome(port=free()); J=c.js
PROBE=os.path.join(os.path.dirname(os.path.abspath(__file__)),'_probe')
SETV="""((sel,val)=>{const i=document.querySelector(sel); const P=i.tagName==='SELECT'?HTMLSelectElement.prototype:HTMLInputElement.prototype; Object.getOwnPropertyDescriptor(P,'value').set.call(i,val); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true}));})"""
BTN="""((t)=>{const b=[...document.querySelectorAll('aside[role=dialog] button')].find(b=>b.innerText.trim()===t); if(b){b.click(); return true;} return false;})"""
CLK="""((t)=>{const n=s=>(s||'').replace(/\\s+/g,' ').trim(); const els=[...document.querySelectorAll('button,a')]; const e=els.find(x=>n(x.innerText)===t)||els.find(x=>n(x.innerText).startsWith(t)); if(!e) return 'NÃO ACHEI: '+t; e.click(); return 'ok';})"""
def ROW(ti,txt): return f"[...document.querySelectorAll('[role=table]')[{ti}].querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.replace(/\\s+/g,' ').indexOf({json.dumps(txt)})>=0)"
def openrow(ti,txt): r=J(f"(()=>{{const r={ROW(ti,txt)}; if(!r) return 'sem linha'; (r.querySelector('[role=cell] span')||r).click(); return 'ok';}})()"); time.sleep(.4); return r
def rowtxt(ti,txt): return J(f"(()=>{{const r={ROW(ti,txt)}; return r?r.innerText.replace(/\\s+/g,' '):null;}})()")
def fv(k): return J(f"(()=>{{const i=document.querySelector('aside[role=dialog] [id$=\"_{k}\"]'); return i?i.value:null;}})()")
def fset(k,val): J(f"({SETV})('aside[role=dialog] [id$=\"_{k}\"]',{json.dumps(val)})"); time.sleep(.25)
def labels(): return J("[...document.querySelectorAll('aside[role=dialog] label[for]')].map(l=>l.innerText.trim())")
def alerts(): return J("[...document.querySelectorAll('aside [role=alert]')].map(x=>x.innerText).join(' | ')")
def toast(): return J("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).filter(Boolean).join(' | ')")
def isopen(): return J("!!document.querySelector('aside[role=dialog]')")
def cancel():
    J(f"({BTN})('Cancelar')||({BTN})('Fechar')"); time.sleep(.2); J(f"({BTN})('Descartar alterações')"); time.sleep(.2)
CAN=lambda t: f"[...document.querySelectorAll('aside[role=dialog] label')].find(l=>l.innerText.trim()==={json.dumps(t)} && l.querySelector('input[type=checkbox]')).querySelector('input')"
def cob(g): return J(f"(()=>{{const r=[...document.querySelectorAll('[role=table]')[1].querySelectorAll('[role=row]')].find(r=>r.innerText.split('\\n')[0].trim()==={json.dumps(g)}); return r?r.innerText.replace(/\\s+/g,' '):null;}})()")
def out(n,v): print('·',n,'→',v)
try:
    c.size(1440,1100)
    # ===================== CD-05 =====================
    c.goto(f'http://127.0.0.1:{p}/CD-05.dc.html'); time.sleep(.6)
    out('erro JS', J("window.__err||''"))
    out('cabeçalhos g_forn', J("[...document.querySelectorAll('[role=table]')[0].querySelectorAll('[role=columnheader]')].map(h=>h.innerText.replace(/\\s+/g,' ').trim())"))
    out('altura necessária', J("(()=>{const R=document.querySelector('[data-root]'); if(!R) return null; const h0=R.getBoundingClientRect().height; R.style.height='auto'; const h=Math.ceil(R.getBoundingClientRect().height); R.style.height=''; return [h0,h];})()"))
    c.shot(os.path.join(PROBE,'verif_cd05_lista.png'))
    # origem da cobertura: clicar num grupo
    J("(()=>{const r=[...document.querySelectorAll('[role=table]')[1].querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.split('\\n')[0].trim()==='Sementes'); (r.querySelector('[role=cell] span')||r).click();})()"); time.sleep(.4)
    out('origem Sementes', J("(document.querySelector('aside[role=dialog]')||{}).innerText"))
    cancel()
    # a) canal E-mail marcado sem e-mail (não homologado): salva? (compara com a regra do WhatsApp)
    J(f"({CLK})('Cadastrar parceiro')"); time.sleep(.4)
    fset('nome','Teste Email Vazio'); fset('cnpj','11.222.333/0001-81'); J(f"{CAN('Cliente')}.click()"); J(f"{CAN('E-mail')}.click()"); time.sleep(.2)
    J(f"({BTN})('Salvar')"); time.sleep(.5)
    out('E-mail autorizado sem e-mail, não homologado: aberto?', isopen()); out('  alertas', alerts()); out('  linha', rowtxt(0,'Teste Email Vazio'))
    if isopen(): cancel()
    J(f"({CLK})('Cadastrar parceiro')"); time.sleep(.4)
    fset('nome','Teste Whats Vazio'); fset('cnpj','11.222.333/0001-81'); J(f"{CAN('Cliente')}.click()"); J(f"{CAN('WhatsApp')}.click()"); time.sleep(.2)
    J(f"({BTN})('Salvar')"); time.sleep(.5)
    out('WhatsApp autorizado sem número: aberto?', isopen()); out('  alertas', alerts())
    cancel()
    # b) desmarcar E-mail num não homologado com e-mail → "não autorizado" no e-mail
    openrow(0,'Coopergrão'); J(f"{CAN('E-mail')}.click()"); time.sleep(.2); J(f"({BTN})('Salvar')"); time.sleep(.5)
    out('Coopergrão sem E-mail autorizado', rowtxt(0,'Coopergrão'))
    # c) homologar F07 (só WhatsApp, sem e-mail)
    openrow(0,'Química Centro-Oeste'); fset('homol','Sim'); J(f"({BTN})('Salvar')"); time.sleep(.4)
    out('F07 homologar sem e-mail/sem canal', alerts())
    fset('email','vendas@quimicaco.com.br'); J(f"{CAN('E-mail')}.click()"); time.sleep(.2); J(f"({BTN})('Salvar')"); time.sleep(.5)
    out('F07 homologado: aberto?', isopen()); out('  toast', toast()); out('  Fungicidas', cob('Fungicidas'))
    # d) autorizar WhatsApp da Sementes Vale
    openrow(0,'Sementes Vale'); J(f"{CAN('WhatsApp')}.click()"); time.sleep(.2); J(f"({BTN})('Salvar')"); time.sleep(.5)
    out('Sementes Vale com WhatsApp autorizado', rowtxt(0,'Sementes Vale'))
    # e) CNPJ duplicado da Fertisul (doc exibido e cnpj antigo)
    J(f"({CLK})('Cadastrar parceiro')"); time.sleep(.4)
    fset('nome','Dup'); J(f"{CAN('Cliente')}.click()"); fset('cnpj','12.345.678/0001-95'); J(f"({BTN})('Salvar')"); time.sleep(.4)
    out('CNPJ igual ao exibido da Fertisul', alerts())
    fset('cnpj','12.345.678/0001-95'); J(f"({BTN})('Salvar')"); time.sleep(.4)
    out('CNPJ antigo da Fertisul (dados2.cnpj / PT-07): aberto?', isopen()); out('  alertas', alerts())
    if isopen(): cancel()
    # f) apagar WhatsApp de quem tem o canal autorizado
    openrow(0,'Fertisul'); fset('whats',''); J(f"({BTN})('Salvar')"); time.sleep(.4)
    out('Fertisul sem número com WhatsApp autorizado', alerts()); cancel()
    # g) filtro por CPF
    out('busca/filtro disponíveis', J("document.querySelectorAll('[role=table]')[0].querySelectorAll('input').length"))
    c.shot(os.path.join(PROBE,'verif_cd05_fim.png'))
    # ===================== CD-02 =====================
    c.goto(f'http://127.0.0.1:{p}/CD-02.dc.html'); time.sleep(.6)
    out('CD-02 erro JS', J("window.__err||''"))
    out('altura necessária', J("(()=>{const R=document.querySelector('[data-root]'); if(!R) return null; const h0=R.getBoundingClientRect().height; R.style.height='auto'; const h=Math.ceil(R.getBoundingClientRect().height); R.style.height=''; return [h0,h];})()"))
    out('cabeçalhos g_rend', J("[...document.querySelectorAll('[role=table]')[1].querySelectorAll('[role=columnheader]')].map(h=>h.innerText.replace(/\\s+/g,' ').trim())"))
    out('linhas g_rend', J("[...document.querySelectorAll('[role=table]')[1].querySelectorAll('[role=row].g2ed')].map(r=>r.innerText.replace(/\\s+/g,' '))"))
    c.shot(os.path.join(PROBE,'verif_cd02_lista.png'))
    # Informado → Largura × velocidade
    openrow(1,'Tratamento de sementes'); out('TS modo', fv('modo')); out('TS rend', fv('rend'))
    fset('modo','Largura × velocidade'); out('rend_c ao trocar', fv('rend_c')); J(f"({BTN})('Salvar')"); time.sleep(.4); out('TS sem L/V/E', alerts())
    fset('larg','2'); fset('vel','3'); fset('efic','50'); out('rend_c 2×3÷10×50%', fv('rend_c')); J(f"({BTN})('Salvar')"); time.sleep(.5)
    out('TS salvo', rowtxt(1,'Tratamento de sementes')); out('  toast', toast())
    # Informado vazio
    openrow(1,'Colheita'); fset('modo','Informado'); fset('rend',''); J(f"({BTN})('Salvar')"); time.sleep(.4); out('Informado vazio', alerts()); cancel()
    # novo rendimento
    r=J(f"({CLK})('Novo rendimento')"); time.sleep(.4); out('novo rendimento', r); out('  rótulos', labels())
    out('  modo padrão', fv('modo')); out('  rend_c vazio', fv('rend_c')); out('  custo_c vazio', fv('custo_c'))
    J(f"({BTN})('Salvar')"); time.sleep(.4); out('  vazio', alerts())
    ops=J("[...document.querySelector('aside[role=dialog] select[id$=\"_op\"]').options].map(o=>o.value)"); out('  ops', ops)
    fset('op',ops[1] if len(ops)>1 else ops[0]); fset('conj','Trator X + Grade 20'); fset('larg','4'); fset('vel','7'); fset('efic','80'); fset('maq','150'); fset('pess','1'); fset('pess_rs','35'); fset('vig','2027-06-30')
    out('  rend_c', fv('rend_c')); out('  custo_c', fv('custo_c'))
    J(f"({BTN})('Salvar')"); time.sleep(.5); out('  aberto?', isopen()); out('  alertas', alerts() if isopen() else ''); out('  toast', toast()); out('  linha', rowtxt(1,'Trator X + Grade 20'))
    if isopen(): cancel()
    # ordenar por rendimento
    out('comparar com o apontado', J(f"({CLK})('Comparar com o apontado')")); time.sleep(.3); out('  toast', toast())
    # ===================== CD-01det =====================
    c.goto(f'http://127.0.0.1:{p}/CD-01det.dc.html'); time.sleep(.6)
    out('CD-01det erro JS', J("window.__err||''"))
    out('linhas', J("[...document.querySelectorAll('[role=table]')[0].querySelectorAll('[role=row].g2ed')].map(r=>r.innerText.replace(/\\s+/g,' '))"))
    openrow(0,'T1-A'); fset('area','313'); J(f"({BTN})('Salvar')"); time.sleep(.4); out('T1-A 313', alerts())
    fset('area','160,01'); J(f"({BTN})('Salvar')"); time.sleep(.4); out('T1-A 160,01', alerts())
    fset('area','159,9'); J(f"({BTN})('Salvar')"); time.sleep(.4); out('T1-A 159,9 aberto?', isopen()); out('  alertas', alerts() if isopen() else toast())
    if isopen(): cancel()
    openrow(0,'T1-B'); fset('area','152,1'); J(f"({BTN})('Salvar')"); time.sleep(.4); out('T1-B 152,1 (soma 312,0 com float)', isopen(), ); out('  alertas', alerts() if isopen() else toast())
    if isopen(): cancel()
    # safra S27SF: nova parcela
    J(f"({CLK})('Cadastrar parcela')"); time.sleep(.4)
    sfs=J("[...document.querySelector('aside[role=dialog] select[id$=\"_safra\"]').options].map(o=>o.value)"); out('safras', sfs)
    fset('parc','T1-B'); fset('safra',sfs[-1]); fset('var_s','58 W'); fset('area','153'); fset('plantio','2027-02-10'); J(f"({BTN})('Salvar')"); time.sleep(.4); out('S27SF 153', alerts())
    fset('area','152'); J(f"({BTN})('Salvar')"); time.sleep(.5); out('S27SF 152 aberto?', isopen()); out('  toast', toast()); out('  linha nova', rowtxt(0,sfs[-1]+' '))
    out('linhas finais', J("[...document.querySelectorAll('[role=table]')[0].querySelectorAll('[role=row].g2ed')].map(r=>r.innerText.replace(/\\s+/g,' '))"))
    openrow(0,'T1-A'); out('help área', J("[...document.querySelectorAll('aside[role=dialog] *')].map(e=>e.childElementCount===0?e.innerText:'').filter(t=>/soma das parcelas/.test(t)).join('|')")); cancel()
finally:
    c.close(); srv.terminate()
