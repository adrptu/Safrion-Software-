"""AGRO-10b: metadados reais do formulário + g2save e sgCompor reais.
python3 agro10_estado_test.py [processo_safra.py alternativo]
Requer node no PATH; sem DOM ou hooks completos.
"""
import ast
import json
import os
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parent
source = Path(sys.argv[1]) if len(sys.argv) > 1 else root / "areas/processo_safra.py"
tree = ast.parse(source.read_text())
assignment = next(n for n in ast.walk(tree) if isinstance(n, ast.Assign)
                  and any(isinstance(t, ast.Name) and t.id == "g_saf" for t in n.targets))
call = assignment.value
edit = next(k.value for k in call.keywords if k.arg == "edit")
fields = next(k.value for k in edit.keywords if k.arg == "fields")
# Only keys are needed by this adversarial draft test, not dynamic farm options.
keys = [ast.literal_eval(next(k.value for k in item.keywords if k.arg == "k"))
        for item in fields.elts]
cols = [ast.literal_eval(next(k.value for k in item.keywords if k.arg == "k"))
        for item in call.args[0].elts]
assert "estado" in cols, "Estado precisa permanecer visível"
script = r"""
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const root=process.argv[1],keys=JSON.parse(process.argv[2]);
const c=vm.createContext({console,setTimeout:()=>0,clearTimeout:()=>{}});
vm.runInContext(fs.readFileSync(root+'/g2lib.js','utf8')+'\n'+fs.readFileSync(root+'/safra_grupo.js','utf8'),c);
for(const estado of ['Rascunho','Em planejamento']){
 const row={id:'S1',v:{nome:'Safra teste',ini:'2027-09-01',fim:'2028-08-31',faz:'Lagoa Grande',estado},s:{},p:{}};
 const sp={id:'g_saf',rows:[row],cols:[{k:'estado'}],edit:{m:'form',fields:keys.map(k=>({k,t:'txt'}))}};
 const self={state:{g2:{g_saf:{fm:{rid:'S1',isNew:false,draft:{nome:'Nome corrigido',ini:row.v.ini,fim:row.v.fim,fazs:'Lagoa Grande',estado:'Estado indevido'}}}}},setState(x){Object.assign(this.state,x)}};
 c.g2save(self,sp);
 const after=c.g2rows(self,sp)[0];
 assert.equal(after.v.nome,'Nome corrigido');
 assert.equal(after.v.estado,estado,'rascunho residual não pode editar estado');
 const r=c.sgCompor([{id:after.id,...after.v}],{chave:'edit',saf:'S1',nome:after.v.nome,ini:after.v.ini,fim:after.v.fim,fazendas:[after.v.faz]},{rec:{},novoId:()=> 'S2'});
 assert.equal(r.ok,true);assert.equal(r.safs[0].estado,estado);
}
console.log('PASS AGRO-10b: coluna visível; nome editável; estado preservado em 2 estados, inclusive draft residual. Sem DOM/hooks completos.');
"""
subprocess.run([os.environ.get("NODE", "node"), "-e", script, str(root), json.dumps(keys)], check=True)
