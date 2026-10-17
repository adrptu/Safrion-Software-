'use strict';
const fs=require('fs'),vm=require('vm'),assert=require('node:assert/strict'),path=require('path');
const c=vm.createContext({console,setTimeout:()=>0,clearTimeout:()=>{}});
vm.runInContext(fs.readFileSync(process.argv[2]||path.join(__dirname,'g2lib.js'),'utf8'),c);
const rows=[{id:'a',v:{nome:'Registro'},p:{nome:[{k:'txt',t:'Registro'},{k:'act',t:'Conferir',fn:'conf:a'},{k:'act',t:'Ver detalhe ›',fn:'abrir'}]}},{id:'b',v:{nome:'Sem ação'}}];
let called='';
function render(extra={},state={}){
 const sp=Object.assign({id:'test',cols:[{k:'nome',l:'Nome'}],rows,edit:{m:'none'},rmenu:true,del:false,total:false},extra);
 const self={state:{g2:{test:state}},setState(x){Object.assign(this.state,x);}};
 const v={conf:x=>{called=x;}};c.g2vals(self,sp,v);return v;
}
let v=render(),a=v.test_rows[0].cells.at(-1);
assert.equal(a.rm,true);assert.equal(a.rmItems.length,1);a.rmItems[0].fn();assert.equal(called,'a');
assert.equal(v.test_ncols,2);assert.equal(v.test_rows[1].cells.length,2);assert.equal(v.test_rows[1].cells.at(-1).isDel,false);
assert.equal(v.test_rows[0].cells[0].parts.some(p=>p.t==='Ver detalhe ›'),true);
a=render({}, {cf:'a'}).test_rows[0].cells.at(-1);assert.equal(a.asking,false);
v=render({del:true});assert.equal(v.test_rows[0].cells.at(-1).rmItems.at(-1).t,'Excluir');
for(const flag of ['ro','nosel','fora','livre']){
 v=render({del:true,rows:[{id:'a',v:{nome:'Protegido'},[flag]:true}]});
 assert.equal(v.test_rows[0].cells.at(-1).isDel,false,flag);
}
v=render({rmenu:false});assert.equal(v.test_ncols,1);assert.equal(v.test_rows[0].cells.length,1);
assert.equal(v.test_rows[0].cells[0].parts.some(p=>p.isAct),true);
console.log('EX47: ações, chamada, navegação, alinhamento, confirmação obsoleta, exclusão e quatro guardas OK');
