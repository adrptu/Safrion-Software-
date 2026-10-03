# -*- coding: utf-8 -*-
"""Capturas de conferência visual (v39): cabeçalho na safra 2025/26, painéis OS-0422/OS-0423 e lista com a OS-0418 bloqueada pelo Estoque (desde a abertura)."""
import sys, os, time, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from os_lib import Os
T = Os(copiar=False); J = T.J
def filtro(lab, val):
    J(f"""(()=>{{const i=document.querySelector('select[aria-label={json.dumps(lab)}]'); Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype,'value').set.call(i,{json.dumps(val)});
      i.dispatchEvent(new Event('input',{{bubbles:true}})); i.dispatchEvent(new Event('change',{{bubbles:true}}));}})()"""); time.sleep(.4)
try:
    T.abrir(wait=1.3)
    filtro('Filtrar por safra', '2025/26'); T.shot('os_v39_hdr_2526.png'); filtro('Filtrar por safra', 'Todas')
    for oid in ('OS-0422', 'OS-0423'): T.ordem(oid); T.shot(f'os_v39_{oid}.png'); T.fechar()
    J("window.scrollTo(0,0)"); T.shot('os_v39_lista_0418.png')
    print('erros', T.erros())
finally:
    T.fim()
