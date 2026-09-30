# -*- coding: utf-8 -*-
"""CD-04 · regressão dos defeitos do verificador (12 verificações no Chrome): aviso sem ponto duplo, ajuda de Habilidades
"NR-10, NR-31 e CREA", líder inativado continua visível no formulário da equipe com aviso e salvar pede um líder ativo,
renomear a pessoa atualiza o líder, e 'Nova equipe' começa com o líder em "Escolha…"."""
from cada_lib import T
import time, json
t=T(); J=t.J
MULTI="""((t)=>{const l=[...document.querySelectorAll('aside[role=dialog] label')].find(x=>x.innerText.trim()===t); if(!l) return false; l.querySelector('input').click(); return true;})"""
def marca(txt): r=J(f"({MULTI})({json.dumps(txt)})"); time.sleep(.2); return r
def help_(rot): return J(f"(()=>{{const l=[...document.querySelectorAll('aside[role=dialog] label[for]')].find(x=>x.innerText.trim()==={json.dumps(rot)}); return l?l.parentElement.innerText:'';}})()")
def seltxt(k): return J(f"(()=>{{const i=document.querySelector('aside[role=dialog] select[id$=\"_{k}\"]'); return i?i.options[i.selectedIndex].text:null;}})()")
try:
    t.goto('CD-04.dc.html')
    t.openrow(0,'Ana'); t.btn('Salvar'); time.sleep(.2); ts=t.toast()
    t.chk('aviso "Salvo: Ana · alocável em O.S." sem ponto duplo', 'Salvo: Ana · alocável em O.S.' in ts and 'O.S..' not in ts, ts)
    t.openrow(0,'João'); marca('Operar trator'); marca('Aprovar O.S. (agrônomo)'); h=help_('Habilidades'); t.cancel()
    t.chk('ajuda de Habilidades: "Exige NR-10, NR-31 e CREA com validade."', 'Exige NR-10, NR-31 e CREA com validade.' in h, h[-60:])
    t.openrow(0,'Lucas'); t.fset('sit','Inativa'); t.btn('Salvar'); time.sleep(.2); ts=t.toast()
    t.chk('inativar o Lucas grava e nomeia o próximo passo: escolher outro líder para Campo 2', 'Salvo: Lucas · inativa · escolha outro líder para Campo 2.' in ts, ts)
    e=t.rowtxt(1,'Campo 2') or ''
    t.chk('linha da Campo 2 mostra o líder Lucas com "Inativa"', 'Lucas Inativa' in e, e)
    t.openrow(1,'Campo 2'); lv=[t.fv('lider'),seltxt('lider')]; hl=help_('Líder')
    t.chk('formulário da Campo 2 mostra o líder gravado "Lucas · inativa" (não Ana) com aviso', lv==['Lucas','Lucas · inativa'] and 'Lucas está inativa; escolha um líder ativo.' in hl, [lv,hl])
    t.fset('cal','seg–sex · 07–17h'); t.btn('Salvar'); a=t.alerts()
    t.chk('mudar só o calendário e salvar pede um líder ativo no campo Líder', t.isopen() and 'Lucas está inativa; escolha um líder ativo.' in a, a)
    t.fset('lider','Carlos'); t.btn('Salvar'); time.sleep(.2); e=t.rowtxt(1,'Campo 2') or ''
    t.chk('escolher Carlos grava: Campo 2 com líder Carlos e calendário seg–sex', not t.isopen() and 'Carlos' in e and 'seg–sex · 07–17h' in e and 'Inativa' not in e, [e,t.alerts()])
    t.openrow(0,'Marcos'); t.fset('nome','Marcos Silva'); t.btn('Salvar'); time.sleep(.2); ts=t.toast()
    t.chk('renomear Marcos avisa que o líder da Campo 1 foi atualizado', 'líder de Campo 1 atualizado' in ts and 'O.S..' not in ts, ts)
    e=t.rowtxt(1,'Campo 1') or ''; t.openrow(1,'Campo 1'); lv=t.fv('lider'); st=seltxt('lider'); t.cancel()
    t.chk('Campo 1: linha e formulário mostram o líder "Marcos Silva"', 'Marcos Silva' in e and lv=='Marcos Silva' and st=='Marcos Silva', [e,lv,st])
    t.clk('Nova equipe'); nt=[t.fv('lider'),seltxt('lider')]; t.fset('nome','Campo 3'); t.btn('Salvar'); a=t.alerts()
    t.chk('Nova equipe: Líder começa em "Escolha…" e salvar sem ele pede o líder no campo', nt==['','Escolha…'] and 'Informe líder' in a, [nt,a])
    t.fset('lider','Paula'); t.btn('Salvar'); time.sleep(.2); e=t.rowtxt(1,'Campo 3') or ''
    t.chk('com a Paula a equipe Campo 3 é criada', not t.isopen() and 'Paula' in e, [e,t.alerts()])
    t.shot('cada_fix04.png')
    t.chk('nenhum erro de JS', not t.errs(), t.errs())
finally:
    t.fim()
