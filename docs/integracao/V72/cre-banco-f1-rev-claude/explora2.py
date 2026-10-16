# -*- coding: utf-8 -*-
"""Exploração (revisão Claude do PR #90): estrutura do DOM da ficha GE-08#vis=ficha com 1 item. Não é teste."""
import os, sys, json, time
G = '/tmp/claude-0/pr90/tools/prototipo/v37/gen37'; sys.path.insert(0, G)
from comp_lib import Chrome, servir
R = os.environ.get('REV_RENDER') or os.path.join(G, '_render')
p, srv = servir(R); c = Chrome(); J = c.js
try:
    c.aparelho(1440, 900, 1, False)
    c.goto(f'http://127.0.0.1:{p}/GE-08.dc.html', .5)
    J("localStorage.clear(); localStorage.setItem('safrion.perfilDemo','Proprietário')")
    c.goto(f'http://127.0.0.1:{p}/GE-08.dc.html#vis=ficha', 1.0)
    print('vazio:', J("(()=>{const s=[...document.querySelectorAll('main section')].find(x=>x.offsetParent&&/Ficha do grupo/.test(x.innerText)); return s?s.innerText.slice(0,800):'sem seção'})()"))
    print('header:', J("(()=>{const h=document.querySelector('header'); return h?h.innerText.slice(0,400):''})()"))
    J("localStorage.setItem('safrion-credito-ficha-demo-grupo-v1', JSON.stringify({v:1,items:[{id:'n1_1',rev:1,historico:[],confirmacoes:[],nome:'Trator sintético',tipo:'Avaliação de mercado',valor:'850000.50',data:'2026-03-10',fonte:'Laudo sintético',responsavel:'Ana',registradoPor:'Proprietário',registradoEm:'2026-10-16'}]}))")
    c.goto(f'http://127.0.0.1:{p}/GE-08.dc.html#vis=ficha', 1.0)
    print('secao:', J("(()=>{const s=[...document.querySelectorAll('main section')].find(x=>x.offsetParent&&/Ficha do grupo/.test(x.innerText)); return s?s.outerHTML.replace(/<svg.*?<\\/svg>/g,'[svg]').replace(/ style=\"[^\"]*\"/g,'').slice(0,9000):'sem'})()"))
finally:
    c.close(); srv.terminate()
