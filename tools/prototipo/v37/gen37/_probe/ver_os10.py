# -*- coding: utf-8 -*-
"""Verificador independente (frente os) · 10: OS-0418 aprovada com liberar bloqueado (sem lote) — o que a lista mostra (x OS-0431)."""
import sys, os, time
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, HERE)
from os_lib import Os
T = Os(copiar=False); J = T.J
try:
    T.abrir(wait=1.3)
    T.ordem('OS-0418'); T.btn('Revisar versão'); T.btn('Aprovar versão'); p = T.pan(); T.fechar()
    print('painel:', p[p.find('PRÓXIMO'):][:230])
    print('LISTA 0418:', T.linha('OS-0418')); print('LISTA 0431:', T.linha('OS-0431'))
    T.shot('ver_os10_lista.png')
finally:
    T.fim()
