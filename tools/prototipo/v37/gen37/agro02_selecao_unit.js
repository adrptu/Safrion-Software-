// AGRO-02: execute real UI state transitions, with precomputed context fixtures.
// No browser or agronomic-domain validation is claimed.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const path=require('node:path');
const source=fs.readFileSync(process.argv[2]||path.join(__dirname,'areas/agronomia.py'),'utf8');
const ini=source.slice(source.indexOf('function agDecIni('),source.indexOf('function agDec('));
const statement=ini.match(/self\.setState\(\{pan:id,dec:[\s\S]*?\}\}\);/)[0];
let failures=0,passed=0;
function check(name,fn){try{fn();passed++;console.log('PASS '+name);}catch(e){failures++;console.error('FAIL '+name+': '+e.message);}}
for(const product of [{id:'a',dmin:0.3},undefined]){
 check('open requires explicit product and dose '+(product?'eligible':'empty'),()=>{
 let state;vm.runInNewContext(statement,{id:'V1',kind:'controlar',area:'95',data:'2026-10-18',ok:product,mipN:String,self:{setState:x=>{state=x}}});
 assert.equal(state.dec.prod,'');assert.equal(state.dec.dose,'');assert.equal(state.dec.area,'95');assert.equal(state.dec.data,'2026-10-18');
 });
}
const expr=source.match(/pick:(\(\)=>up\(\{prod:u\.id,dose:[^\n]*?\}\)),h:/)[1];
for(const [name,prod,dose,target,expected] of [
 ['first selection stays blank','', '', 'a',''],
 ['changing product clears typed comma dose','a','0,7','b',''],
 ['same product preserves typed comma dose','a','0,7','a','0,7'],
 ['same product preserves explicit zero for validation','a','0','a','0'],
 ['same product preserves incomplete draft','a','0,','a','0,']
]){
 check(name,()=>{let patch;const state={dec:{prod,dose}};const cb=vm.runInNewContext('('+expr+')',{self:{state},u:{id:target,dmin:0.3},mipN:String,up:x=>{patch=x}});
 cb();assert.equal(patch.prod,target);assert.equal(patch.dose,expected);});
}
console.log(passed+' passed; '+failures+' failed');process.exitCode=failures?1:0;
