# -*- coding: utf-8 -*-
"""Verificador · Estoque 10: larguras das etapas 2 e 3 com estados ricos (parcial + aguardando app + O.S. pede mais)."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ver_estoque_lib import V

v = V()
try:
    v.abrir()
    print(v.mudar("cenEntregar(c,'REQ-040','NPK 20-05-20',4000,'Paula'); cenEntregar(c,'REQ-035','Fungicida A',5,'Marcos'); c.ordens['OS-0430'].aprov=true; cenLiberar(c,'OS-0430'); const r=c.ordens['OS-0430'].req; cenEntregar(c,r,'Glifosato 480',100,'Marcos'); return {msg:'ok'};"))
    v.abrir()
    for i in (2, 3):
        v.etapa(i); print(f'e{i}:', v.overflow())
    v.etapa(2); v.shot('ver_est_e2_rico.png')
    print('erros:', v.erros())
finally:
    v.fim()
