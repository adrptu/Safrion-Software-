# -*- coding: utf-8 -*-
"""Parte CD-02 do cd0102test.py (2/2: salvar, modo Informado e mesmos campos no Planejar safra), com os mesmos valores esperados.
Adaptações ao layout novo: aba 'Operações e rendimentos', tabela 0 (árvore Operação → conjunto), linha achada pelo nome do conjunto."""
from cadc_lib import T
import json, time
t=T(); J=t.J
AJ=["Largura × velocidade ÷ 10 × eficiência.","Máquina + implemento + pessoas × custo por pessoa.","Inclua combustível, manutenção e depreciação; o operador entra em Pessoas."]
try:
    t.goto('CD-02.dc.html'); t.clk('Operações e rendimentos')
    t.openrow(0,'PJ-3030'); t.fset('vel','10'); t.fset('maq','200')
    t.fset('larg','0,2'); t.btn('Salvar')
    al=t.alerts(); t.chk('largura abaixo do mínimo barrada', 'Mínimo 0,5 m' in al, al)
    t.chk('rendimento ao vivo acompanha o digitado', t.fv('rend_c')=='0,15', t.fv('rend_c'))
    t.fset('larg','36'); t.btn('Salvar'); time.sleep(.2)
    t.chk('salvou e fechou', not t.isopen(), t.alerts())
    ts=t.toast(); t.chk('aviso de salvo com o novo rendimento', '27,00 ha/h' in ts and 'R$ 333,00/h' in ts and 'R$ 12,33/ha' in ts, ts)
    r=t.rowtxt(0,'PJ-3030'); t.chk('linha recalculada (27,00 ha/h · R$ 333,00 · R$ 12,33)', all(x in r for x in ['36 m · 10 km/h · 75 %','27,00 ha/h','R$ 333,00','R$ 12,33']), r)
    # modo Informado: sem largura, rendimento digitado
    t.openrow(0,'Plantadeira 24 linhas'); t.fset('modo','Informado')
    L=t.labels(); t.chk('Informado esconde largura, velocidade e eficiência', 'Largura de trabalho' not in L and L.count('Rendimento efetivo')==1, L)
    t.chk('Informado parte do rendimento atual (6,8)', t.fv('rend')=='6,8', t.fv('rend'))
    t.fset('rend','7,5'); t.btn('Salvar'); time.sleep(.2)
    r=t.rowtxt(0,'Plantadeira 24 linhas'); t.chk('linha em modo informado (7,50 ha/h)', 'rendimento informado' in r and '7,50 ha/h' in r and 'R$ 52,80' in r, r)
    t.shot('cadc_cd02_rend.png')
    # mesma lista de campos no Planejar safra (etapa 3)
    t.goto('SAF.dc.html'); t.clk('Abrir safra'); time.sleep(.3); t.clk('3 Defina os rendimentos'); time.sleep(.3)
    J("(()=>{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>/Trator 02/.test(r.innerText)); (r.querySelector('[role=cell] span')||r).click();})()"); time.sleep(.4)
    LS=t.labels()
    LC=['Como obter o rendimento','Largura de trabalho','Velocidade de trabalho','Eficiência de campo','Rendimento efetivo','Máquina','Implemento','Pessoas na equipe','Custo por pessoa','Custo por hora']
    t.chk('Planejar safra usa os mesmos campos (fora os próprios do cadastro)', LS==LC, LS)
    t.chk('Planejar safra tem as mesmas ajudas', all(J(f"document.querySelector('aside[role=dialog]').innerText.indexOf({json.dumps(a)})>=0") for a in AJ))
    t.chk('Planejar safra calcula o mesmo rendimento ao vivo (21,60)', t.fv('rend_c')=='21,60', t.fv('rend_c'))
finally:
    t.fim()
