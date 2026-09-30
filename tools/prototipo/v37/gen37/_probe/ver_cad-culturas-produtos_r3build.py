# -*- coding: utf-8 -*-
"""Verificador r3: gera CD-02/06/07 pelo despacho CAD_MODS num diretório próprio e compara com _render/ (não toca project/)."""
import sys, os, filecmp, time, importlib
HERE=os.path.dirname(os.path.abspath(__file__)); GEN=os.path.dirname(HERE); sys.path.insert(0,GEN); os.chdir(GEN)
t0=time.time()
import engine as E
OUT=os.path.join(HERE,'ver_cad-culturas-produtos_r3tmp'); os.makedirs(OUT,exist_ok=True); E.P=OUT
import areas.cadastros as C
for mod,fns in C.CAD_MODS:
    if mod not in ('areas.cad_culturas','areas.cad_produtos_estrutura'): continue
    m=importlib.import_module(mod)
    for fn in fns:
        f=getattr(m,fn); print('dispatch',fn,'->',f.__module__); f()
for f in ['CD-02.dc.html','CD-06.dc.html','CD-07.dc.html']:
    a=os.path.join(OUT,f); b=os.path.join(GEN,'_render',f); p=os.path.join(GEN,'project',f)
    print(f,'render igual:',filecmp.cmp(a,b,shallow=False),'project igual:',os.path.exists(p) and filecmp.cmp(a,p,shallow=False),os.path.getsize(a))
import ui37
print('HEIGHTS37',[ui37.HEIGHTS37.get(x) for x in ('CD-02.dc.html','CD-06.dc.html','CD-07.dc.html')],'H_OVR',[ui37.H_OVR.get(x) for x in ('CD-02.dc.html','CD-06.dc.html','CD-07.dc.html')])
print(round(time.time()-t0,1),'s')
