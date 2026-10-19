import ast,json
from pathlib import Path
from types import SimpleNamespace
p=Path(__file__).parent;s=(p/'areas/suprimentos.py').read_text();tree=ast.parse(s)
node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='su02')
sujs=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='SUJS' for t in n.targets))
globs=dict(Path=Path,json=json,__file__=str(p/'areas/suprimentos.py'),os=__import__('os'),E=SimpleNamespace(_reset_screen=lambda x:None),DEPOS=['Galpão 1'],METODOS=['Necessidade datada'],HEIGHTS37={},R=lambda id,v,**kw:dict(id=id,v=v,p={},s={},**kw),fs=lambda k,l,t='txt',**kw:dict(k=k,l=l,t=t,**kw),nf=str,MARK='§STATUS§',dyn_status=lambda *a,**kw:None)
for k in ['grid','painel','bloco','mini','alink','nota','shell37','prima','primb']:globs[k]=lambda *a,**kw:''
def js(pn,code,**kw):
 (p/'sup_politicas_captured.js').write_text('const PN='+json.dumps(pn)+';const SIMS={};const RUN={},CHECK={},MAXFN={},LINES={};\n'+sujs+code)
globs['js']=js
exec(compile(ast.Module(body=[node],type_ignores=[]),'<su02>','exec'),globs);globs['su02']()
print('SU02 JS capturado; layout substituído por stubs, não é build de página')
