# -*- coding: utf-8 -*-
"""Verificador 6 · altura fixa do artboard (overflow: clip): o conteúdo cabe depois de cadastrar uma fazenda (CD-01) e de novas versões (CD-01det)?"""
import importlib.util, os, sys, time, json
H=os.path.dirname(os.path.abspath(__file__)); sp=importlib.util.spec_from_file_location('vl',os.path.join(H,'ver_cad-fazendas_lib.py')); L=importlib.util.module_from_spec(sp); sp.loader.exec_module(L)
s=L.Sess()
MED=r"""(()=>{const root=document.querySelector('[data-root]'); const rb=root.getBoundingClientRect(); const cs=getComputedStyle(root);
  const all=[...root.querySelectorAll('main *, section *')].filter(e=>e.getClientRects().length&&e.innerText!==undefined);
  let maxb=0, last=''; all.forEach(e=>{ const b=e.getBoundingClientRect(); if(b.height>0&&b.bottom>maxb){ maxb=b.bottom; last=(e.innerText||e.tagName).slice(0,60);} });
  return {rootH:rb.height, rootBottom:rb.bottom+window.scrollY, overflow:cs.overflow, conteudo:maxb+window.scrollY, ultimo:last, docH:document.documentElement.scrollHeight};})()"""
try:
    s.go('CD-01.dc.html'); print('CD-01 inicial', s.js(MED))
    s.click('+ Cadastrar fazenda'); s.fset('nome','Nova Esperança'); s.fset('mun','Jataí'); s.fset('area','600'); s.btn('Salvar'); time.sleep(.3)
    print('CD-01 + 1 fazenda', s.js(MED))
    s.shot('ver_cadf_cd01_1faz.png',full=True)
    s.click('Cadastrar talhão','[role=row]'); s.fset('t','N1'); s.fset('decl','250'); s.btn('Salvar'); time.sleep(.3)
    print('CD-01 + 1 fazenda + 1 talhão', s.js(MED))
    s.shot('ver_cadf_cd01_1faz1tal.png',full=True)
    s.go('CD-01det.dc.html#talhao=T1'); print('det T1', s.js(MED))
    s.click('Expandir tudo'); print('det T1 expandido', s.js(MED))
    s.click('Definir polígono da T1-B','header'); s.btn('Gerar prévia'); s.btn('Salvar polígono'); time.sleep(.3)
    s.click('Nova versão do polígono'); s.btn('Gerar prévia'); s.btn('Salvar polígono'); time.sleep(.3)
    s.click('Expandir tudo'); print('det T1 v5 expandido', s.js(MED), s.toast()[:120])
    s.shot('ver_cadf_det_v5.png',full=True)
finally: s.close()
