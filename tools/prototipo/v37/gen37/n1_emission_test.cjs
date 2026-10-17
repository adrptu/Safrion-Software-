const fs=require('fs'),vm=require('vm'),assert=require('assert');
const mip=fs.readFileSync(__dirname+'/mip.js','utf8');
const cl=fs.readFileSync(__dirname+'/cenario.js','utf8').split('\n');
const actual=cl.slice(5,44).join('\n')+'\n'+cl.slice(305,310).join('\n')+'\n'+mip;
function setup(fail=false){
 const s={v:1,rev:0,vis:{V1:{id:'V1',tal:'T1'}},seq:{dia:1,rec:1,ra:1},dia:{},rec:{},apl:[]},c={v:1,rev:0,ordens:{}};
 const disk=new Map([['talhao-os-mip-v1',JSON.stringify(s)],['talhao-os-cenario-v1',JSON.stringify(c)]]),writes=[];
 const b={MIP0:s,CEN0:c,MIPD:{hoje:'2026-10-17'},MIP_SIT:{acima:['Acima']},localStorage:{getItem:k=>disk.get(k)||null,setItem:(k,v)=>{if(fail)throw Error('quota');writes.push(k);disk.set(k,v)},removeItem:()=>{throw Error('remove forbidden')}},cenExigeAlc:a=>{if(a.k!=='agro')throw Error('Sem alçada');return 'Agrônomo sintético'},g2pf:a=>a};
 vm.createContext(b);vm.runInContext(actual,b);
 vm.runInContext(`mipChecks=()=>({tr:[],u:{id:'P1',nome:'Produto sintético',un:'L',g:'Inseticidas'}});mipNo=(c)=>({id:'OS-0'+(440+Object.keys(c.ordens).length)});mipOsNova=(c,no)=>{c.ordens[no.id]={etapa:'A liberar'};return {msg:'OK'}};mipP=()=>({alvo:'Hipótese',chave:'x'});mipRes=()=>({k:'acima'});`,b);
 const a={kind:'controlar',area:'2',dose:'1',prod:'P1',data:'2026-10-17',ator:{k:'agro'},chave:'MIP-V1-v1-test',dver:1};
 return {disk,writes,run:(delta={})=>{b.arg={...a,...delta};return vm.runInContext("mipEmitir(null,'V1',arg)",b)}};
}
let count=0;
{const x=setup(true),before=JSON.stringify([...x.disk]),r=x.run();assert(r.erro);assert.equal(JSON.stringify([...x.disk]),before);count++;}
{const x=setup(),before=JSON.stringify([...x.disk]);assert(x.run({chave:''}).erro);assert.equal(JSON.stringify([...x.disk]),before);count++;}
{const x=setup(),r=x.run();assert(!r.erro,r.erro);const c=JSON.parse(x.disk.get('talhao-os-cenario-v1'));assert(c.ordens[r.os]);assert.equal(c.mip.rec[r.rec].os,r.os);assert.equal(c.mip.vis.V1.dec.ver,1);assert(c.recibos['MIP-V1-v1-test'].resultado);assert.deepEqual(x.writes,['talhao-os-cenario-v1']);count++;
 const again=x.run();assert(again.repetido);assert.equal(again.os,r.os);assert.equal(JSON.parse(x.disk.get('talhao-os-cenario-v1')).mip.seq.ra,2);count++;
 const before=JSON.stringify([...x.disk]);assert(x.run({dose:'3'}).erro);assert.equal(JSON.stringify([...x.disk]),before);count++;
 assert(x.run({ator:{k:'denied'}}).erro);assert.equal(JSON.stringify([...x.disk]),before);count++;
 assert(x.run({chave:'new',dver:1}).erro);assert.equal(JSON.stringify([...x.disk]),before);count++;
 const cancel=JSON.parse(x.disk.get('talhao-os-cenario-v1'));cancel.ordens[r.os].etapa='Canceladas';x.disk.set('talhao-os-cenario-v1',JSON.stringify(cancel));
 const next=x.run({chave:'new-decision',dver:2});assert(!next.erro,next.erro);assert.notEqual(next.os,r.os);assert.notEqual(next.rec,r.rec);
 const after=JSON.parse(x.disk.get('talhao-os-cenario-v1'));assert.equal(after.mip.rec[r.rec].sit,'Cancelado');assert.equal(after.mip.rec[r.rec].subst,next.rec);assert.equal(after.mip.vis.V1.historicoDec[0].os,r.os);assert.equal(after.mip.vis.V1.dec.ver,2);count++;
}
console.log(count+' PASS emission transaction/receipt; agronomy and OS construction stubbed, not browser/E2E.');
