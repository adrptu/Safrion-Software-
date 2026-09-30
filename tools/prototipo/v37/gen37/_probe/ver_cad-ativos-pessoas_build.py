# Verificador: compila CD-03/CD-04 via areas.cadastros num diretório temporário e compara com _render/.
import sys, os, tempfile, filecmp
HERE=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0,HERE); os.chdir(HERE)
import engine as E
tmp=tempfile.mkdtemp(prefix='vercap_'); E.P=tmp
import areas.cadastros as C
import importlib
m=importlib.import_module('areas.cad_ativos_pessoas')
print('dispatch:', [ (mod,fns) for mod,fns in C.CAD_MODS if 'ativos' in mod])
m.cd03(); m.cd04()
for f in ('CD-03.dc.html','CD-04.dc.html'):
    a=os.path.join(tmp,f); b=os.path.join(HERE,'_render',f); p=os.path.join(HERE,'project',f)
    print(f,'render igual:',filecmp.cmp(a,b,shallow=False),'project igual:',filecmp.cmp(a,p,shallow=False), os.path.getsize(a))
print(tmp)
