# Verificador CD-04 (A): várias habilitações, vigência (admissão futura, contrato encerrado, até < admissão), inativa, equipe no form.
import sys, os, time, json
HERE=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0,HERE)
from cada_lib import T
t=T(); J=t.J; t.c.size(1440,1000)
MULTI="""((t)=>{const l=[...document.querySelectorAll('aside[role=dialog] label')].find(x=>x.innerText.trim()===t); if(!l) return false; l.querySelector('input').click(); return true;})"""
def marca(txt): r=J(f"({MULTI})({json.dumps(txt)})"); time.sleep(.2); return r
def help_(rot): return J(f"(()=>{{const l=[...document.querySelectorAll('aside[role=dialog] label[for]')].find(x=>x.innerText.trim()==={json.dumps(rot)}); return l?l.parentElement.innerText.replace(/\\n/g,' / '):'';}})()")
def chips(): return J("[...document.querySelectorAll('button[aria-pressed]')].map(b=>b.innerText.replace(/\\s+/g,' ').trim()).join(' | ')")
try:
    t.goto('CD-04.dc.html')
    t.openrow(0,'João'); t.shot('ver_cap_c4_joao.png'); print('João labels:',t.labels())
    marca('Operar trator'); marca('Aprovar O.S. (agrônomo)'); print('após marcar:',t.labels()); print('help hab:',help_('Habilidades')[-80:])
    print('help v31:',help_('Validade da NR-31')); print('help crea:',help_('Validade do registro no CREA'))
    t.btn('Salvar'); time.sleep(.3); print('João salvo aberto:',t.isopen(),'alerts:',t.alerts()); print('row:',t.rowtxt(0,'João')); print('toast:',t.toast())
    print('header:',t.header()[:120]); print('chips:',chips())
    # admissão futura
    t.openrow(0,'Carlos'); t.fset('adm','2026-10-05'); t.btn('Salvar'); time.sleep(.3); print('Carlos adm futura:',t.rowtxt(0,'Carlos'),'| toast:',t.toast())
    # contrato encerrado
    t.openrow(0,'Nilton'); t.fset('vinc','Diarista'); t.fset('ate','2026-09-10'); t.btn('Salvar'); time.sleep(.3); print('Nilton encerrado:',t.rowtxt(0,'Nilton'),'| alerts:',t.alerts(),'| toast:',t.toast())
    # até < admissão
    t.openrow(0,'Lucas'); t.fset('ate','2019-01-01'); t.btn('Salvar'); print('Lucas ate<adm:',t.alerts()); t.cancel()
    # inativa
    t.openrow(0,'Marcos'); t.fset('sit','Inativa'); t.btn('Salvar'); time.sleep(.3); print('Marcos inativa:',t.rowtxt(0,'Marcos'),'| toast:',t.toast())
    print('header:',t.header()[:140]); print('chips:',chips())
    print('equipes:',J("[...document.querySelectorAll('[role=table]')[1].querySelectorAll('[role=row]')].slice(1).map(r=>r.innerText.replace(/\\s+/g,' ')).join(' || ')"))
    # equipe no formulário: trocar equipe atualiza ajuda
    t.openrow(0,'Beto'); print('Beto help equipe:',help_('Equipe')[-70:]); t.fset('equipe','Oficina'); print('-> Oficina:',help_('Equipe')[-70:]); t.cancel()
    print('erros:',t.errs(),'motor:',t.errs_motor())
finally:
    t.fim()
