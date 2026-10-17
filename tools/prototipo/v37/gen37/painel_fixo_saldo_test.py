"""PAINEL-FIXO-1: ação real extraída do CA-01det, sem navegador."""
import ast, json, pathlib, subprocess, sys
root = pathlib.Path(__file__).resolve().parent
source = pathlib.Path(sys.argv[1]) if len(sys.argv)>1 else root/'areas/campo.py'
tree = ast.parse(source.read_text())
ap = next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='APJS' for t in n.targets))
js = r'''
const assert=require('node:assert/strict'),vm=require('node:vm');
let current={};const ctx={AREA:350,DID:'fixture',FICHAS_REV:'v3 fixa',FICHAS_V2:'Prévia',cenGet:()=>current,window:{location:{href:'origem'}}};vm.createContext(ctx);
vm.runInContext(SOURCE,ctx);
function run(o){current={ordens:o?{'OS-0421':o}:{}};ctx.window.location.href='origem';const self={state:{},setState(v){Object.assign(this.state,v)}};const v={};ctx.EXTRAVALS(self,v);assert.equal(typeof v.ajustar_saldo,'function');const before=JSON.stringify(current);v.ajustar_saldo();assert.equal(JSON.stringify(current),before);return self;}
for(const etapa of ['A liberar']){const self=run({saldo:160,etapa});assert.equal(ctx.window.location.href,'OS.dc.html#OS-0421:ajustar');assert.equal(self.state.ajuste_indisponivel,undefined);}
for(const o of [{saldo:160,etapa:'Liberadas'},{saldo:160,etapa:'Em execução'},null,{saldo:0,etapa:'Em execução'},{saldo:160,etapa:'Encerradas'},{saldo:160,etapa:'Canceladas'},{saldo:'x',etapa:'Liberadas'}]){const self=run(o);assert.equal(ctx.window.location.href,'origem');assert.equal(self.state.ajuste_indisponivel,true);}
console.log('8 casos PASS; navegação ou prévia honesta, cenário intacto');
'''.replace('SOURCE',json.dumps(ap))
subprocess.run(['node','-e',js],check=True)
