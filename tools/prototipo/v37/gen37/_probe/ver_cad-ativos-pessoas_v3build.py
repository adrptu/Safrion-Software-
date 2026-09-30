# Verificador (rodada 3): compila CD-03/CD-04 pelo laço de areas.cadastros num diretório temporário e compara com _render/ e project/.
import sys, os, tempfile, filecmp, time
HERE=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0,HERE); os.chdir(HERE)
t0=time.time()
import engine as E
tmp=tempfile.mkdtemp(prefix='vercap3_'); E.P=tmp
import areas.cadastros as C, importlib
for mod,fns in C.CAD_MODS:
    if 'ativos' not in mod: continue
    m=importlib.import_module(mod)
    for fn in fns:
        f=getattr(m,fn); print('dispatch',fn,'->',f.__module__); f()
for f in ('CD-03.dc.html','CD-04.dc.html'):
    a=os.path.join(tmp,f); b=os.path.join(HERE,'_render',f); p=os.path.join(HERE,'project',f)
    print(f,'render igual:',filecmp.cmp(a,b,shallow=False),'project igual:',os.path.exists(p) and filecmp.cmp(a,p,shallow=False), os.path.getsize(a))
import ui37
print('HEIGHTS37', ui37.HEIGHTS37.get('CD-03.dc.html'), ui37.HEIGHTS37.get('CD-04.dc.html'), 'H_OVR', ui37.H_OVR.get('CD-03.dc.html'), ui37.H_OVR.get('CD-04.dc.html'))
print(tmp, round(time.time()-t0,1),'s')
