import ast,json,sys
from pathlib import Path
from types import SimpleNamespace
p=Path(__file__).parent
tree=ast.parse((p/'areas/logistica.py').read_text())
# Executa apenas o trecho LO-02det do gerador, com layout substituído.
fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and any(isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='fname' for t in x.targets) and isinstance(x.value,ast.Constant) and x.value.value=='LO-02det.dc.html' for x in n.body))
i=next(i for i,n in enumerate(fn.body) if isinstance(n,ast.Assign) and isinstance(n.value,ast.Constant) and n.value.value=='LO-02det.dc.html')
j=next(j for j in range(i+1,len(fn.body)) if isinstance(fn.body[j],ast.Assign) and isinstance(fn.body[j].value,ast.Constant) and fn.body[j].value.value=='LO-03.dc.html')
nodes=fn.body[i:j]
sys.modules['cenario']=SimpleNamespace(js_prefixo=lambda:'')
sys.modules['dados_comercial']=SimpleNamespace(js_regras=lambda:'')
sys.modules['areas']=SimpleNamespace()
sys.modules['areas.processo_os']=SimpleNamespace(JS_NUCLEO='')
grids=[]
def grid(cols,rows,**kw):
 grids.append(dict(id=kw['gid'],cols=cols,rows=rows,edit=kw['edit']))
 return ''
g=dict(__file__=str(p/'areas/logistica.py'),E=SimpleNamespace(_reset_screen=lambda x:None),grid=grid,C=lambda k,l,**kw:dict(k=k,l=l,**kw),EXTRAJS=[''],HEIGHTS37={},PARENT37={},H=lambda x:'{{'+x+'}}',esc=str,MUTED='',PRIM='')
for k in ['continuity','bloco','nota','ilink','shell37','faixa','BTN_ST','_selo_dinamico']:g[k]=lambda *a,**kw:''
exec(compile(ast.Module(body=nodes,type_ignores=[]),'<LO02det>','exec'),g)
(p/'logistica_saida_captured.js').write_text('var GRIDS='+json.dumps(grids)+';\n'+g['EXTRAJS'][0])
print('LO02det AST/adapter captured; layout e prefixo substituídos, não é build/UI.')

