# -*- coding: utf-8 -*-
"""EX-40.6 (complemento): valor do campo só leitura "Água disponível no solo (referência)" no painel do setor P2 da Irrigação (executado)."""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e40lib import S
s = S(); s.reset('Ana'); s.go('IR-01.dc.html#P2', espera=2.5); time.sleep(1)
v = s.J("""(()=>{const d=[...document.querySelectorAll('aside[role=dialog],[role=dialog]')].find(e=>e.getClientRects().length); if(!d) return null;
  return [...d.querySelectorAll('input,textarea,output,[aria-readonly],[readonly]')].map(e=>[(e.getAttribute('aria-label')||e.id||e.name||''),(e.value!==undefined?e.value:e.innerText)]).slice(0,14);})()""")
s.p('campos do painel do setor P2 (rótulo, valor):'); [s.p('  ', x) for x in (v or [])]
s.fim('p4b_cad.log')
