# -*- coding: utf-8 -*-
"""Parte CD-02 do cd0102test.py (1/2: lista e cálculo ao vivo), com os mesmos valores esperados. Adaptações ao layout novo:
os rendimentos ficam na aba 'Operações e rendimentos' (tabela 0, árvore Operação → conjunto), a linha do conjunto é achada pelo
nome do conjunto e o formulário ganhou 'Cultura' logo após 'Conjunto ou equipe' (os campos do Planejar safra seguem iguais)."""
from cadc_lib import T
import json
t=T(); J=t.J
try:
    t.goto('CD-02.dc.html'); t.clk('Operações e rendimentos')
    t.chk('CD-02 sem erro JS', not t.errs(), t.errs())
    # TABELAS-FOCO (06/10/2026): uma variável por coluna. Revisão TABR (09/10/2026, A1): voltam os critérios de antes ("sem rolagem lateral a
    # 1440 px" e "no máximo 7 colunas"): modo, largura, velocidade e eficiência, que formam o rendimento, ficam no painel do rendimento
    sw=J("(()=>{const s=document.querySelectorAll('[role=table]')[0].closest('.g2rola')||document.querySelectorAll('[role=table]')[0].parentElement; return [s.scrollWidth,s.clientWidth];})()")
    t.chk('rendimentos sem rolagem lateral a 1440 px', sw[0]<=sw[1]+1, sw)
    t.chk('no máximo 7 colunas', J("document.querySelectorAll('[role=table]')[0].querySelectorAll('[role=columnheader]').length")<=7)
    hs=J("[...document.querySelectorAll('[role=table]')[0].querySelectorAll('[role=columnheader]')].map(h=>h.textContent.replace(/[⇅▾▴▼▲]/g,'').replace(/\\s+/g,' ').trim())")
    t.chk('colunas com uma variável cada', hs==['Operação › conjunto','Fonte','Processo','Cultura','Rendimento','Custo R$/h','Custo R$/ha'], hs)
    r=t.rowtxt(0,'PJ-3030'); t.chk('linha mostra custo por hora e por hectare', 'R$ 313,00' in r and 'R$ 14,49' in r, r)
    t.openrow(0,'Máquina TSI'); t.chk('rendimento informado sinalizado no painel (Modo "Informado", largura, velocidade e eficiência vazias)', t.fv('modo')=='Informado' and not t.fv('larg') and not t.fv('vel') and not t.fv('efic'), [t.fv(k) for k in ('modo','larg','vel','efic')])
    t.clk('Cancelar')
    t.openrow(0,'PJ-3030'); t.chk('painel mostra largura, velocidade e eficiência (36 m · 8 km/h · 75 %)', [t.fv(k) for k in ('larg','vel','efic')]==['36','8','75'], [t.fv(k) for k in ('larg','vel','efic')])
    t.clk('Cancelar')
    t.openrow(0,'PJ-3030'); L=t.labels()
    t.chk('formulário abre', len(L)>0, L)
    t.chk('mesmos rótulos do Planejar safra (+ Cultura do cadastro)', L==['Operação','Conjunto ou equipe','Cultura','Como obter o rendimento','Largura de trabalho','Velocidade de trabalho','Eficiência de campo',
        'Rendimento efetivo','Máquina','Implemento','Pessoas na equipe','Custo por pessoa','Custo por hora','Fonte do dado','Vigente até'], L)
    t.chk('rendimento ao vivo inicial = 21,60', t.fv('rend_c')=='21,60', t.fv('rend_c'))
    t.chk('custo/h ao vivo inicial = 313,00', t.fv('custo_c')=='313,00', t.fv('custo_c'))
    t.fset('vel','10'); t.chk('L × V ÷ 10 × E ao vivo: 36 × 10 ÷ 10 × 75% = 27,00', t.fv('rend_c')=='27,00', t.fv('rend_c'))
    t.fset('maq','200'); t.chk('custo/h ao vivo: 200 + 95 + 1 × 38 = 333,00', t.fv('custo_c')=='333,00', t.fv('custo_c'))
    AJ=["Largura × velocidade ÷ 10 × eficiência.","Máquina + implemento + pessoas × custo por pessoa.","Inclua combustível, manutenção e depreciação; o operador entra em Pessoas."]
    t.chk('ajudas das fórmulas e da composição visíveis', all(J(f"document.querySelector('aside[role=dialog]').innerText.indexOf({json.dumps(a)})>=0") for a in AJ))
finally:
    t.fim()
