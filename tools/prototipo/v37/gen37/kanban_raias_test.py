"""AGR-02: geração real e estado do Kanban em Node. Não executa navegador."""
import json, os, subprocess, sys, tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
G=Path(os.environ.get('GEN',HERE)).resolve()
os.environ.setdefault('SAFRION_DADOS','sintetico')
sys.path.insert(0,str(G));os.chdir(G)
from areas import processo_os as P
import engine
captura={};original=P.shell37
def shell(*a,**kw):
    captura.update(grids=json.dumps(engine.GRIDS,ensure_ascii=False),js=P.EXTRAJS[0])
    return original(*a,**kw)
P.shell37=shell
P.build()
prefix="""var window={addEventListener(){},innerWidth:1440};var location={search:'?view=kanban&ag=onde',pathname:'/OS.dc.html',hash:''};var history={replaceState(){}};var mem={};var localStorage={getItem:k=>mem[k]||null,setItem:(k,v)=>mem[k]=String(v),removeItem:k=>delete mem[k]};"""
src=prefix+(G/'g2lib.js').read_text()+'\nconst GRIDS='+captura['grids']+';\n'+captura['js']+'\n'+(HERE/'kanban_raias_unit.js').read_text()
with tempfile.TemporaryDirectory(prefix='kanban_raias_') as td:
    p=Path(td)/'run.js';p.write_text(src)
    r=subprocess.run([os.environ.get('NODE','node'),str(p)],text=True,capture_output=True,timeout=120)
print(r.stdout,end='');print(r.stderr,end='',file=sys.stderr)
raise SystemExit(r.returncode)

