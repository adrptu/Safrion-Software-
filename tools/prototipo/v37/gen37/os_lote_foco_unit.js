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
