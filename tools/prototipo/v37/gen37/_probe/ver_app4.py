# -*- coding: utf-8 -*-
"""Verificador App 4: MB-04 ocorrência (ordem, tipo, texto obrigatório, voz/foto simuladas, sem sinal, nova, lista) e reflexo em MB-02det."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ver_app_lib import V
v = V()
try:
    v.abrir('MB-01'); v.clk('Restaurar demonstração')
    v.abrir('MB-04')
    v.clk('Registrar ocorrência'); al = v.alerts(); print('   vazio ->', al, '|', v.toast()[:60])
    v.ok('Descreva a ocorrência' in al and v.cen('c.ocorr.length') == 0, 'descrição vazia: erro junto ao campo, nada gravado')
    v.clk('Ditar (simulado)'); print('   ditar ->', v.J("document.querySelector('#oc_txt').value"), '|', v.toast()[:50])
    v.ok(v.alerts() == '' and 'Seção 3' in v.J("document.querySelector('#oc_txt').value"), 'ditar preenche o texto e limpa o erro')
    v.clk('Anexar foto (simulado)'); print('   foto ->', v.toast()[:60], '| rótulo:', v.J("[...document.querySelectorAll('main button')].map(b=>b.innerText).filter(t=>/foto/i.test(t)).join(',')"))
    v.clk('OS-0424 · P2'); v.clk('Clima')
    print('   pressed:', v.J("[...document.querySelectorAll('main [aria-pressed=true]')].map(b=>b.innerText).join(', ')"))
    v.clk('Registrar ocorrência'); t = v.toast(); b = v.J("document.querySelector('main').innerText")
    print('   registrar ->', t[:80], '| hdr:', v.hdr(), '| foot:', v.foot())
    v.ok(v.cen("c.ocorr.length===1 && c.ocorr[0].os==='OS-0424' && c.ocorr[0].tipo==='Clima' && c.ocorr[0].sinc===true") and 'Registrada na O.S.' in b,
         'registrada na OS-0424, tipo Clima, com sinal')
    print('   texto gravado:', v.cen('c.ocorr[0].texto'))
    v.clk('Nova ocorrência'); v.clk('Sem sinal')
    print('   nova -> pressed:', v.J("[...document.querySelectorAll('main [aria-pressed=true]')].map(b=>b.innerText).join(', ')"), '| desc:', repr(v.J("document.querySelector('#oc_txt').value")))
    v.setv('#oc_txt', 'Bico entupido na seção 2.'); v.clk('Registrar ocorrência'); b = v.J("document.querySelector('main').innerText")
    print('   sem sinal ->', v.toast()[:80], '| hdr:', v.hdr()); print('   ', b.replace('\n', ' / ')[:700])
    v.ok(v.cen("c.ocorr[1].sinc") is False and 'No aparelho · aguardando sinal' in b and 'OC-501' in b, 'sem sinal: fica no aparelho; lista mostra a anterior')
    v.clk('Com sinal'); b = v.J("document.querySelector('main').innerText"); print('   com sinal ->', v.toast()[:90], '| hdr:', v.hdr())
    v.ok('Registrada na O.S.' in b and 'aguardando sinal' not in b.replace('Nada aguardando sinal', ''), 'sinal volta: selo da ocorrência atualiza')
    for i in range(3):
        v.clk('Nova ocorrência'); v.setv('#oc_txt', f'Ocorrência de teste número {i + 3} com texto mais longo para ocupar duas linhas no cartão do aparelho.'); v.clk('Registrar ocorrência')
    c = v.corte(); print('   5 ocorrências: corte', c, '| larg', v.larg())
    v.ok(c['excesso'] <= 0, 'MB-04 com lista de ocorrências cabe na altura ' + str(c))
    v.shot('ver_app4_mb04.png')
    v.abrir('MB-02det'); b = v.body(); print('   MB-02det hdr:', v.hdr())
    i = b.find('Ocorrências'); print('   ocorr no detalhe:', b[i:i + 300].replace('\n', ' / '))
    v.ok(not v.erros(), 'sem erros JS ' + str(v.erros()))
    v.abrir('MB-01'); v.clk('Restaurar demonstração')
finally:
    v.fim()
