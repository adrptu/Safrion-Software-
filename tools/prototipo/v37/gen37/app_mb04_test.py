# -*- coding: utf-8 -*-
"""MB-04 · ocorrência (Chrome real, ≤ 15 verificações): com 3 ordens na fila, ocorrências de texto longo e o formulário aberto
(erro e foto), a lista e a nota cabem acima do rodapé; a lista mostra as 2 mais recentes e conta as demais.
Uso: python3 app_mb04_test.py   (compile antes: areas.mobile.build())"""
from app_lib import App

CORTE = """(()=>{const m=document.querySelector('main'); const mr=m.getBoundingClientRect(); const pb=parseFloat(getComputedStyle(m).paddingBottom)||0; let b=0;
 m.querySelectorAll('*').forEach(e=>{const r=e.getBoundingClientRect(); if(r.height>0&&r.width>0&&r.bottom>b) b=r.bottom;}); return Math.round(b-(mr.bottom-pb));})()"""
LONGO = ['Bico entupido na seção 2 da barra; limpei com escova, conferi a vazão de todos os bicos da seção e segui a aplicação normalmente.',
         'Vento acima de 10 km/h às 10:30 na bordadura leste; parei a barra 20 min e retomei quando o vento baixou para 6 km/h.',
         'Chuva fraca às 11:00; suspendi a aplicação por 40 min e retomei com a folha seca, conforme a janela da ordem.']
a = App(['MB-01', 'MB-04'])
try:
    a.abrir('MB-01'); a.clk('Restaurar demonstração')
    a.mudar("c.ordens['OS-0430'].aprov=true; return cenLiberar(c,'OS-0430');")
    a.abrir('MB-04')
    a.ok(a.J("document.querySelectorAll('main [aria-label=\"Ordem da ocorrência\"] button').length") == 3, 'pré-carga: 3 ordens na fila de Marcos')
    for t in LONGO:
        a.setv('#oc_txt', t); a.clk('Registrar ocorrência'); a.clk('Nova ocorrência')
    a.clk('Anexar foto'); a.clk('Registrar ocorrência')   # sem texto: erro junto ao campo
    b = a.body(); k = a.J(CORTE)
    a.ok('Descreva a ocorrência' in b and '1 foto' in b, 'formulário aberto com erro junto ao campo e foto anexada')
    a.ok(k <= 0, f'3 ordens + formulário com erro + lista de ocorrências longas cabem (excesso {k} px)')
    a.ok(a.J("[...document.querySelectorAll('main b')].filter(x=>/^OC-50\\d · /.test(x.innerText)).map(x=>x.innerText.slice(0,6)).join(',')") == 'OC-503,OC-502'
         and '+ 1 anterior no detalhe de cada ordem' in b, 'lista: as 2 mais recentes (OC-503, OC-502) e "+ 1 anterior"')
    a.setv('#oc_txt', 'Mangueira do retorno rachada; troquei.'); a.clk('Registrar ocorrência'); k = a.J(CORTE)
    a.ok('OC-504' in a.body() and a.foot() == 'Voltar à fila' and k <= 0, f'registrada: cartão OC-504, rodapé Voltar à fila e cabe (excesso {k} px)')
    a.ok(not a.erros(), 'sem erros JS ' + str(a.erros()))
    a.abrir('MB-01'); a.clk('Restaurar demonstração')
finally:
    a.fim()
