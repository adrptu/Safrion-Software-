"""EST-ONDA0: comandos/handlers reais em Node; sem navegador. GEN seleciona contraprova."""
import json, os, subprocess, sys, tempfile
from pathlib import Path
HERE = Path(__file__).resolve().parent
G = Path(os.environ.get('GEN', HERE)).resolve()
os.environ.setdefault('SAFRION_DADOS', 'sintetico')
sys.path.insert(0, str(G)); os.chdir(G)
import cenario
import engine
from areas import processo_estoque as PE
from areas import processo_os as PO
PE.shell37 = lambda *args, **kwargs: ""  # só coletar as grades reais, sem o shell limpar o registro
PE.build()
ls = "var __ls={};var localStorage={getItem:k=>__ls[k]??null,setItem:(k,v)=>__ls[k]=String(v),removeItem:k=>delete __ls[k]};var window={addEventListener(){}};var location={hash:'',pathname:'',search:''};var history={replaceState(){}};"
src = ls + (G/'g2lib.js').read_text() + '\n' + cenario.js_prefixo()
src += '\nconst E2='+json.dumps(PE._dados_js(),ensure_ascii=False)+';const GRIDS='+json.dumps(engine.GRIDS,ensure_ascii=False)+';const EST_BEN_H="";\n'+PE.JS
src += '\nconst OSD='+json.dumps(dict(ords=PO._ordens(),nova=PO._nova_ordem_dados(),aloc={},agf={}),ensure_ascii=False)+';const RC_OS=[];\n'+PO.JS_NUCLEO
src += '\n'+(HERE/'est_onda0_unit.js').read_text()
with tempfile.TemporaryDirectory(prefix='est_onda0_') as td:
    p=Path(td)/'run.js'; p.write_text(src)
    result=subprocess.run([os.environ.get('NODE','node'),str(p)],capture_output=True,text=True,timeout=120)
print(result.stdout,end=''); print(result.stderr,end='',file=sys.stderr)
raise SystemExit(result.returncode)
