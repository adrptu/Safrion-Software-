# -*- coding: utf-8 -*-
"""Verificador r3-6: compara a largura da tabela de Compromissos do IN-03 na base (_base/gen37/_render) com a atual."""
import os, json
import ver_mapa_lib as L
BASE=os.path.join(L.GEN,'..','_base','gen37','_render')
Q="""(()=>{const g=document.querySelector('[role=grid],[role=table],table'); const p=g.parentElement; const b=[...g.querySelectorAll('a,button')].map(x=>[x.innerText.trim(),Math.round(x.getBoundingClientRect().right)]).filter(x=>!/[⇅▾▲]/.test(x[0]));
  return {g_sw:g.scrollWidth,p_cw:p.clientWidth,p_right:Math.round(p.getBoundingClientRect().right),bts:b};})()"""
for nome,dirr in [('base',BASE),('atual',L.R)]:
    L.R=dirr; s=L.Sess(1440,1100)
    try:
        s.go('IN-03.dc.html'); print(nome,json.dumps(s.J(Q),ensure_ascii=False))
    finally:
        s.close()
