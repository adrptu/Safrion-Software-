// Contraprova do handler real com DOM minimo; nao substitui o teste no navegador.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const source=fs.readFileSync(__dirname+'/areas/processo_os.py','utf8');
const start=source.indexOf('  const put=',source.indexOf('function osGrupoVals'));
const end=source.indexOf('  const key=',start);
let ok=0;
for(const [name,inside,closed,exists,expected] of [
 ['botao removido devolve foco ao dialogo',false,false,true,1],
 ['campo ainda focado preserva digitacao',true,false,true,0],
 ['fechar antes do callback nao reabre nem rouba foco',false,true,true,0],
 ['dialogo desmontado nao causa excecao',false,false,false,0]]){
 let focus=0,callback;
 const button={focus:()=>focus++};
 const self={state:{og:{aberto:true,ids:['OS-demo']}},setState(x){Object.assign(this.state,x)}};
 const document={activeElement:{},getElementById:id=>!exists?null:id==='og_dialog'?{contains:()=>inside}:button};
 vm.runInNewContext(source.slice(start,end)+'put({resultado:{msg:"Confirmado"}});',{self,document,setTimeout:f=>callback=f});
 if(closed)self.state.og.aberto=false;
 callback();assert.equal(focus,expected);assert.deepEqual(self.state.og.ids,['OS-demo']);
 console.log('OK '+name);ok++;
}
console.log(JSON.stringify({ok,fail:0,scope:'handler real; DOM simulado, nao navegador'}));
const escStart=source.indexOf('  const soltaEsc=',start),escEnd=source.indexOf('  v.og_titulo=',escStart);
assert.ok(escStart>start&&escEnd>escStart);
const listeners=new Set();let mounted=true;
const self={state:{og:{aberto:true,ids:['OS-demo']}}},v={og_show:true};
const document={addEventListener:(n,f)=>listeners.add(f),removeEventListener:(n,f)=>listeners.delete(f),getElementById:()=>mounted?{}:null};
const render=()=>vm.runInNewContext(source.slice(escStart,escEnd),{self,v,document,put:x=>Object.assign(self.state.og,x)});
const fire=(key,defaultPrevented=false)=>{let prevented=false;for(const f of [...listeners])f({key,defaultPrevented,preventDefault:()=>prevented=true});return prevented;};
render();render();assert.equal(listeners.size,1);console.log('OK documento registra apenas um listener');
fire('Enter');fire('Escape',true);assert.equal(self.state.og.aberto,true);console.log('OK outras teclas e Escape ja tratado preservados');
assert.equal(fire('Escape'),true);assert.equal(self.state.og.aberto,false);assert.equal(listeners.size,0);assert.deepEqual(self.state.og.ids,['OS-demo']);console.log('OK Escape sem foco fecha e remove listener, preservando rascunho');
self.state.og.aberto=true;render();mounted=false;fire('Escape');assert.equal(listeners.size,0);console.log('OK dialogo desmontado remove listener');
console.log(JSON.stringify({ok:8,fail:0,scope:'handlers reais; DOM simulado, nao navegador'}));
