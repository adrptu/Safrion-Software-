# -*- coding: utf-8 -*-
"""CD-05 · abrir fornecedor pela linha, marcar grupo, e-mail inválido mostra erro no campo, corrigir e salvar; não homologado não recebe cotação."""
import sys, os, time, subprocess, json
HERE=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0,HERE)
from cdp import Chrome
from journeys import free
R=os.path.join(HERE,'_render'); p=free()
srv=subprocess.Popen(['python3','-m','http.server',str(p),'--bind','127.0.0.1','--directory',R],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(0.8)
c=Chrome(port=free()); J=c.js
SETV="""((sel,val)=>{const i=document.querySelector(sel); const P=i.tagName==='SELECT'?HTMLSelectElement.prototype:HTMLInputElement.prototype; Object.getOwnPropertyDescriptor(P,'value').set.call(i,val); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true}));})"""
BTN="""((t)=>{const b=[...document.querySelectorAll('aside[role=dialog] button')].find(b=>b.innerText.trim()===t); if(b){b.click(); return true;} return false;})"""
T=lambda: J("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).filter(Boolean).join(' | ')")
ok=[]
def chk(nome,cond,extra=''):
    ok.append(bool(cond)); print(('PASSOU ' if cond else 'FALHOU ')+nome, extra)
def abrir(nome):
    J(f"""(()=>{{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.indexOf({json.dumps(nome)})>=0); (r.querySelector('[role=cell] span')||r.querySelector('[role=cell]')).click();}})()"""); time.sleep(.45)
def fid(k): return J(f"(document.querySelector('[id$=\"_{k}\"]')||{{}}).id||''")
def cob(g): return J(f"""(()=>{{const t=document.querySelectorAll('[role=table]')[1]; const r=[...t.querySelectorAll('[role=row]')].find(r=>r.innerText.split('\\n')[0].trim()==={json.dumps(g)}); return r?r.innerText.replace(/\\s+/g,' '):'';}})()""")
try:
    c.size(1440,1100); c.goto(f'http://127.0.0.1:{p}/CD-05.dc.html'); time.sleep(.6)
    chk('sem erro JS', J("window.__err||''")=='', J("window.__err||''"))
    chk('sem botão Editar nas linhas', J("[...document.querySelectorAll('[role=row] button, [role=row] a')].every(b=>!/^Editar/.test(b.innerText.trim()))"))
    chk('nota de homologação visível', 'Não homologado não recebe cotação' in J("document.body.innerText"))
    antes=cob('Fungicidas'); print('  cobertura Fungicidas antes:', antes)
    abrir('Química Centro-Oeste')
    chk('abre formulário lateral', J("!!document.querySelector('aside[role=dialog]')"), J("(document.querySelector('aside[role=dialog] h2')||{}).innerText"))
    grupos=J("[...document.querySelectorAll('aside[role=dialog] label')].filter(l=>l.querySelector('input[type=checkbox]')).map(l=>l.innerText.trim()+(l.querySelector('input').checked?'*':''))")
    print('  opções de grupo/papel:', grupos)
    # marcar grupo Adjuvantes
    J("""(()=>{const l=[...document.querySelectorAll('aside[role=dialog] label')].find(l=>l.innerText.trim()==='Adjuvantes'&&l.querySelector('input[type=checkbox]')); l.querySelector('input').click();})()"""); time.sleep(.3)
    chk('marca grupo Adjuvantes', J("[...document.querySelectorAll('aside[role=dialog] label')].some(l=>l.innerText.trim()==='Adjuvantes'&&l.querySelector('input').checked)"))
    fe=fid('email'); fh=fid('homol'); print('  campos:', fe, fh)
    J(f"({SETV})('#{fh}','Sim')"); time.sleep(.2)
    J(f"({SETV})('#{fe}','compras@quimica')"); time.sleep(.2); J(f"({BTN})('Salvar')"); time.sleep(.4)
    err=J(f"""(()=>{{const i=document.querySelector('#{fe}'); let n=i.parentElement; for(let k=0;k<4&&n;k++,n=n.parentElement){{const a=n.querySelector('[role=alert]'); if(a) return a.innerText;}} return '';}})()""")
    chk('e-mail inválido mostra erro junto ao campo', 'E-mail inválido' in err, err)
    chk('formulário continua aberto com o preenchido', J(f"document.querySelector('#{fe}').value")=='compras@quimica')
    # WhatsApp inválido
    fw=fid('whats'); J(f"({SETV})('#{fw}','9999')"); J(f"({BTN})('Salvar')"); time.sleep(.3)
    chk('WhatsApp inválido mostra erro', 'DDD' in J("document.querySelector('aside[role=dialog]').innerText"))
    J(f"({SETV})('#{fw}','65 99377-8899')"); J(f"({SETV})('#{fe}','compras@quimicaco.com.br')"); time.sleep(.2)
    J(f"({BTN})('Salvar')"); time.sleep(.5)
    t=T(); chk('salva e fecha', not J("!!document.querySelector('aside[role=dialog]')"), t)
    row=J("""(()=>{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.indexOf('Química Centro-Oeste')>=0); return r.innerText.replace(/\\s+/g,' ');})()""")
    chk('linha atualizada (e-mail, Adjuvantes, homologado)', 'compras@quimicaco.com.br' in row and 'Adjuvantes' in row and 'Sim' in row, row)
    depois=cob('Fungicidas'); print('  cobertura Fungicidas depois:', depois)
    chk('cobertura recalculada', antes!=depois)
    # desomologar Fertisul: sai da cobertura
    abrir('Fertisul'); J(f"({SETV})('#{fid('homol')}','Não')"); J(f"({BTN})('Salvar')"); time.sleep(.5)
    chk('não homologado avisa que não recebe cotação', 'não recebe cotação' in T(), T())
    print('  cobertura Fertilizantes:', cob('Fertilizantes'))
    # homologar sem e-mail → erro
    abrir('Coopergrão');
    J("""(()=>{const l=[...document.querySelectorAll('aside[role=dialog] label')].find(l=>l.innerText.trim()==='Fornecedor'&&l.querySelector('input[type=checkbox]')); l.querySelector('input').click();})()"""); time.sleep(.2)
    J(f"({SETV})('#{fid('homol')}','Sim')"); J(f"({BTN})('Salvar')"); time.sleep(.3)
    chk('homologar sem grupo é barrado', 'Marque ao menos um grupo' in J("document.querySelector('aside[role=dialog]').innerText"))
    J(f"({BTN})('Cancelar')"); time.sleep(.2); J(f"({BTN})('Descartar alterações')"); time.sleep(.2)
    # CNPJ duplicado
    J("document.querySelector('main button, button').click");
    c.shot(os.path.join(HERE,'_probe','cd05_final.png'))
finally:
    c.close(); srv.terminate()
print('RESULTADO:', 'OK' if all(ok) else 'FALHOU', f'{sum(ok)}/{len(ok)}')
