import ast,json,sys
from pathlib import Path
from types import SimpleNamespace
p=Path(__file__).parent
s=(p/'areas/campo.py').read_text();tree=ast.parse(s)
node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='_ca02')
sys.modules['cenario']=SimpleNamespace(js_prefixo=lambda:(p/'cenario.js').read_text())
sys.modules['conferencia_diaria']=SimpleNamespace(js_nucleo=lambda:(p/'conferencia_diaria.js').read_text())
grids=[]
def grid(cols,rows,**kw):
 if kw.get('gid')=='g_fila':grids.append(dict(id=kw['gid'],cols=cols,rows=rows,edit=kw['edit']))
 return ''
pt=SimpleNamespace(**{k:(lambda *a,**kw:dict(t=str(a[0]) if a else '')) for k in ['txt','chip','br','mut','link','b','act']})
g=dict(__file__=str(p/'areas/campo.py'),E=SimpleNamespace(_reset_screen=lambda x:None),Pt=pt,grid=grid,EXTRAJS=[''],HEIGHTS37={},H=lambda s:'{{'+s+'}}')
for k in ['imsg','ilink','bloco','kpis','shell37']:g[k]=lambda *a,**kw:''
exec(compile(ast.Module(body=[node],type_ignores=[]),'<CA02>','exec'),g);g['_ca02']()
(p/'campo_conferencia_captured.js').write_text('var GRIDS='+json.dumps(grids)+';\n'+g['EXTRAJS'][0])
print('CA02 AST/JS capturado; layout substituído, não é build completo.')
