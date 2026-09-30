# -*- coding: utf-8 -*-
"""Verificador · Estoque 8: busca, ordenação e menu de coluna nas grades do cenário; O.S. cancelada na etapa 2; formulário aberto quando outra tela muda o cenário."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ver_estoque_lib import V

v = V()
try:
    v.abrir(); v.etapa(2)
    n0 = len(v.rows())
    v.setv('main input[placeholder^="Buscar"]', 'NPK'); time.sleep(.3); print('busca NPK:', len(v.rows()), v.rows()[:2], '| contagem:', v.J("(document.querySelector('main').innerText.match(/\\d+ de \\d+/)||[''])[0]"))
    v.setv('main input[placeholder^="Buscar"]', ''); time.sleep(.3)
    # ordenar por Solicitado
    hdr = v.J("(()=>{const h=[...document.querySelectorAll('[role=columnheader]')].find(h=>/SOLICITADO/i.test(h.innerText)); const b=h&&[...h.querySelectorAll('button')]; return b?b.map(x=>x.innerText.trim()||x.getAttribute('aria-label')):'sem';})()")
    print('botões cabeçalho:', hdr)
    v.J("(()=>{const h=[...document.querySelectorAll('[role=columnheader]')].find(h=>/SOLICITADO/i.test(h.innerText)); const b=[...h.querySelectorAll('button')].find(x=>/⇅|↑|↓/.test(x.innerText)||/rden/i.test(x.getAttribute('aria-label')||'')); (b||h).click();})()"); time.sleep(.3)
    print('ordenado:', [r.split(' ')[0] + ' ' + r.split(' ')[1] for r in v.rows()], len(v.rows()) == n0)
    v.J("(()=>{const h=[...document.querySelectorAll('[role=columnheader]')].find(h=>/FASE/i.test(h.innerText)); const b=[...h.querySelectorAll('button')].find(x=>/▾/.test(x.innerText)); b&&b.click();})()"); time.sleep(.3)
    print('menu fase:', v.J("(document.querySelector('[role=menu],[role=dialog]:not(aside)')||{innerText:'(sem menu)'}).innerText.replace(/\\s+/g,' ').slice(0,300)"))
    v.J("document.body.click()"); time.sleep(.2)
    # O.S. cancelada (como a tela O.S. faz em osc_cancelar)
    print(v.mudar("const o=c.ordens['OS-0424']; const r=c.reqs[o.req]; r.itens.forEach(it=>{const l=c.lotes[it.prod+'|'+it.lote]; l.reservado=Math.max(0,l.reservado-(it.solicitado-it.entregue));}); r.estado='Cancelada'; o.etapa='Canceladas'; o.reservado=false; o.selos=[]; return {msg:'cancelada'};"))
    v.abrir(); v.etapa(2); print('REQ-039 cancelada:', v.rowtxt('REQ-039')); print('k2:', v.J("(document.querySelector('main').innerText.split('\\n').find(l=>/·/.test(l))||'')"))
    v.etapa(4); print('F26-02:', v.rowtxt('F26-02'))
    # formulário de entrega aberto com rascunho; outra tela muda o cenário
    v.etapa(2); v.row('REQ-040'); v.setv('fx_g_ent_qtd', '4000')
    print(v.mudar("return cenReceber(c,'KCl 60%','K26-99',100,'kg','Galpão 2','—','NF 9','true');"))
    v.J("window.dispatchEvent(new StorageEvent('storage',{key:'talhao-os-cenario-v1'}))"); time.sleep(.4)
    print('rascunho mantido:', v.aberto(), v.val('fx_g_ent_qtd'))
    v.clk('Salvar', 'aside[role=dialog]'); print('toast:', v.toast()); print('REQ-040:', v.rowtxt('REQ-040'))
    print('erros:', v.erros())
finally:
    v.fim()
