# -*- coding: utf-8 -*-
"""Verificador cad-fazendas: gera CD-01/CD-01det do código atual numa pasta própria e compara com _render (não toca project/)."""
import sys, os, filecmp
HERE=os.path.dirname(os.path.abspath(__file__)); GEN=os.path.dirname(HERE); sys.path.insert(0,GEN); os.chdir(GEN)
import engine as E
OUT=os.path.join(HERE,'ver_cad-fazendas_r3tmp'); E.P=OUT
import areas.cad_fazendas as m
m.cd01(); m.cd01det()
for f in ['CD-01.dc.html','CD-01det.dc.html']:
    print(f, 'IGUAL ao _render' if filecmp.cmp(os.path.join(OUT,f),os.path.join(GEN,'_render',f),shallow=False) else 'DIFERENTE do _render', os.path.getsize(os.path.join(OUT,f)))
