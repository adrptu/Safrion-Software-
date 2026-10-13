"""Transação F2 com cenário/CONF reais; adaptador de domínio explícito em teste.
Não prova as regras agronômicas ou UI de publicação. Node no PATH.
"""
import json, os, subprocess, tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
os.environ['SAFRION_DADOS']='sintetico'
os.chdir(HERE)
import engine as E
import dados_config, dados_assinatura
from areas import processo_safra as SAF
SAF.shell37=lambda *a,**k:None
SAF.build()
shim="""const assert=require('node:assert/strict');const __ls={};let __cota=false;
const localStorage={getItem:k=>__ls[k]||null,setItem:(k,v)=>{if(__cota)throw new Error('QuotaExceededError');__ls[k]=String(v);},removeItem:k=>{delete __ls[k];}};
const window={addEventListener(){}};const location={hash:'',pathname:'',search:''};const history={replaceState(){}};
"""
source=shim+'\nconst GRIDS='+json.dumps(E.GRIDS,ensure_ascii=False)+';\n'+(HERE/'g2lib.js').read_text()+'\n'+dados_assinatura.js_prefixo()+dados_config.js_prefixo()+'\n'+E.EXTRAJS[0]+'\n'+(HERE/'plano_referencia_comando.js').read_text()+'\n'+(HERE/'plano_referencia_comando_unit.js').read_text()
with tempfile.TemporaryDirectory(prefix='safrion-f2-cmd-') as td:
 p=Path(td)/'test.js';p.write_text(source);r=subprocess.run(['node',str(p)],capture_output=True,text=True,timeout=90)
print(r.stdout,end='');print(r.stderr,end='')
if r.returncode: raise SystemExit(r.returncode)
# Base anterior sem gravador estrito: deve recusar antes de tocar qualquer estado.
guarda="const assert=require('node:assert/strict');\n"+(HERE/'plano_referencia_comando.js').read_text()+"\nassert.match(PlanoReferenciaComando.publicar(null,{},()=>({impedimentos:[]})).erro,/Gravação segura indisponível/);console.log('OK guarda sem dependência estrita: 1/1');"
r=subprocess.run(['node','-e',guarda],capture_output=True,text=True,timeout=10)
print(r.stdout,end='');print(r.stderr,end='')
raise SystemExit(r.returncode)
