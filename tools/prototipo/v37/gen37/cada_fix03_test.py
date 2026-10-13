# -*- coding: utf-8 -*-
"""CD-03 · regressão dos defeitos do verificador (11 verificações no Chrome): horímetro compara com a última leitura gravada,
subtítulo da edição sem 'escolha a classe', links da coluna Conjuntos identificam o conjunto e abrem o certo, plural em
'não alocáveis' e select do formulário sempre mostra o valor gravado ('Escolha…' quando vazio)."""
from cada_lib import T
import time, json
t=T(); J=t.J
MULTI="""((t)=>{const l=[...document.querySelectorAll('aside[role=dialog] label')].find(x=>x.innerText.trim()===t); if(!l) return false; l.querySelector('input').click(); return true;})"""
def marca(txt): r=J(f"({MULTI})({json.dumps(txt)})"); time.sleep(.2); return r
# linha da 1ª grade pelo nome em negrito (o texto da linha também traz nomes de outras máquinas na coluna Conjuntos)
LIN="(n=>[...document.querySelectorAll('[role=table]')[0].querySelectorAll('[role=row].g2ed')].find(r=>(r.querySelector('b')||{}).innerText===n))"
def cjlinks(nome):
    """conjuntos da máquina listados no painel dela (antes eram links na coluna Conjuntos)."""
    if not abre(nome): return None
    r=J("[...document.querySelectorAll('aside[role=dialog] button')].map(b=>b.innerText.trim()).filter(t=>t.endsWith('›')).map(t=>t.replace(/\\s*›$/,''))"); t.cancel(); return r
def cjclick(nome,txt):
    if not abre(nome): return False
    r=J(f"(()=>{{const b=[...document.querySelectorAll('aside[role=dialog] button')].find(b=>b.innerText.trim()==={json.dumps(txt+' ›')}); if(!b) return false; b.click(); return true;}})()"); time.sleep(.35); return r
def seltxt(k): return J(f"(()=>{{const i=document.querySelector('aside[role=dialog] select[id$=\"_{k}\"]'); return i?i.options[i.selectedIndex].text:null;}})()")
def abre(nome): r=J(f"(()=>{{const r={LIN}({json.dumps(nome)}); if(!r) return false; (r.querySelector('.g2pw')||r).click(); return true;}})()"); time.sleep(.35); return r
try:
    t.goto('CD-03.dc.html')
    abre('Trator 02'); t.fset('cont_tr','3100'); t.btn('Salvar'); time.sleep(.2); o1=t.isopen()
    abre('Trator 02'); t.fset('cont_tr','3000'); t.btn('Salvar'); time.sleep(.2); a2=t.alerts()
    t.chk('horímetro: 3.100 h grava; depois 3.000 h é barrado com "A última leitura foi 3.100 h"', not o1 and 'A última leitura foi 3.100 h' in a2, a2)
    t.fset('cont_tr','3150'); t.btn('Salvar'); time.sleep(.2); r=t.rowtxt(0,'Trator 02') or ''
    t.chk('horímetro maior que a última leitura grava', not t.isopen() and 'Salvo: Trator 02' in t.toast(), [t.alerts(),t.toast()])
    abre('Trator T1'); d=t.dlg()
    t.chk('edição: subtítulo pede capacidade/custo/calibração e não pede a classe (fixa)', 'Altere capacidade, custo por hora e calibração' in d and 'Escolha a classe' not in d and t.fdis('classe'), d[:160])
    t.cancel(); t.clk('Cadastrar máquina ou instalação'); d=t.dlg()
    t.chk('cadastro novo: subtítulo "Escolha a classe para abrir a capacidade dela."', 'Escolha a classe para abrir a capacidade dela.' in d and 'Altere capacidade' not in d, d[:160]); t.cancel()
    abre('Silo 01'); sv=[t.fv('custo_f'),seltxt('custo_f')]; t.cancel()
    t.chk('Silo 01 sem custo: "Fonte do custo" mostra "Escolha…" (valor vazio), não uma fonte que não foi gravada', sv==['','Escolha…'], sv)
    di=cjlinks('Distribuidor 3 t')
    t.chk('Distribuidor 3 t: o link identifica o conjunto pelo trator', di==['Trator 03 · Adubação a lanço'], di)
    t.aba('Conjuntos'); t.clk('Montar conjunto'); mt=seltxt('maq'); t.fset('impl','Plantadeira 24 linhas'); marca('Plantio'); t.btn('Salvar'); a=t.alerts()
    t.chk('Montar conjunto: Máquina começa em "Escolha…" e salvar sem ela pede a máquina no campo', mt=='Escolha…' and 'Informe máquina' in a, [mt,a])
    t.fset('maq','Trator 02'); t.btn('Salvar'); time.sleep(.2); t.aba('Máquinas')
    pl=cjlinks('Plantadeira 24 linhas'); t1=cjlinks('Trator T1')
    t.chk('Plantadeira 24 linhas: links "Trator T1 · Plantio" e "Trator 02 · Plantio"; Trator T1 mostra "Plantadeira 24 linhas · Plantio"',
          pl==['Trator T1 · Plantio','Trator 02 · Plantio'] and t1==['Plantadeira 24 linhas · Plantio'], [pl,t1])
    cjclick('Plantadeira 24 linhas','Trator 02 · Plantio'); ti=t.title(); t.cancel()
    t.chk('o link "Trator 02 · Plantio" abre o conjunto Trator 02 + Plantadeira 24 linhas', 'Trator 02 + Plantadeira 24 linhas' in ti, ti)
    t.aba('Conjuntos'); k1=t.card('Trator 03 + Distribuidor 3 t') or ''; k2=t.card('Trator 04 + Esqueletadeira') or ''
    t.chk('operadores: "Lucas, Beto não alocáveis" no plural', 'Lucas, Beto não alocáveis' in k1 and 'Lucas, Beto não alocáveis' in k2, [k1,k2])
    t.shot('cada_fix03.png')
    t.chk('nenhum erro de JS', not t.errs(), t.errs())
finally:
    t.fim()
