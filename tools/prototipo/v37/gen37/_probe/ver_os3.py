# -*- coding: utf-8 -*-
"""Verificador independente (frente os) · 3: painéis (água, OS-0417, OS-0421), overflow no painel de 820 px e fluxo da OS-0419 (água)."""
import sys, os, time, json
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, HERE)
from os_lib import Os
T = Os(copiar=False); J = T.J
POVF = r"""(()=>{const a=document.querySelector('aside[role=dialog]'); if(!a) return 'sem painel'; const out=['aside '+a.scrollWidth+'/'+a.clientWidth];
  const R=a.getBoundingClientRect();
  [...a.querySelectorAll('*')].forEach(e=>{ if(e.offsetParent===null) return; const r=e.getBoundingClientRect(); if(r.width>0&&(r.right>R.right-2)&&e.children.length===0&&e.innerText&&e.innerText.trim()) out.push('fora: '+e.innerText.trim().slice(0,60)+' '+Math.round(r.right)+'>'+Math.round(R.right));
    if(e.scrollWidth>e.clientWidth+1 && e.children.length===0 && getComputedStyle(e).overflow!=='visible') out.push('corte: '+e.innerText.slice(0,60)); });
  return out.slice(0,20);})()"""
try:
    T.abrir(wait=1.3)
    for oid in ('OS-0422', 'OS-0423', 'OS-0419', 'OS-0418', 'OS-0417', 'OS-0421', 'OS-0424', 'OS-0431', 'OS-0420'):
        T.ordem(oid); p = T.pan()
        btns = J("[...document.querySelectorAll('aside[role=dialog] button')].map(b=>b.innerText.trim()).filter(Boolean)")
        print('==', oid, '| linha:', T.linha(oid))
        print('   passo:', p[p.find('PRÓXIMO'):p.find('ATIVIDADE')][:420])
        print('   botões:', btns, '| ovf', J(POVF))
        if oid in ('OS-0417', 'OS-0421', 'OS-0424'): print('   ins:', T.ins()[:520])
        if oid in ('OS-0422', 'OS-0423', 'OS-0417'): T.shot(f'ver_os3_{oid}.png')
        T.fechar()
    # fluxo da OS-0419 (só água): iniciar → apontar 80 ha → conferência → encerrar
    T.ordem('OS-0419'); T.btn('Iniciar execução'); T.btn('Confirmar início'); print('0419 iniciar', T.toast(), '|', T.linha('OS-0419'))
    T.btn('Registrar apontamento'); print('   form ap', T.pan()[T.pan().find('PRÓXIMO'):][:260])
    J("(()=>{const i=[...document.querySelectorAll('aside[role=dialog] input')].find(x=>x.getAttribute('aria-label')==='Área feita em hectares'); Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(i,'80'); i.dispatchEvent(new Event('input',{bubbles:true}));})()"); time.sleep(.2)
    T.btn('Salvar apontamento'); print('   ap', T.toast(), '|', T.linha('OS-0419'), '| aps', T.aps())
    T.btn('Enviar para conferência'); T.btn('Confirmar envio'); p = T.pan(); print('   conf', p[p.find('PRÓXIMO'):][:240])
    T.btn('Conferir e encerrar'); T.btn('Confirmar encerramento'); print('   enc', T.toast(), '|', T.linha('OS-0419'))
    T.fechar(); print('erros', T.erros())
finally:
    T.fim()
