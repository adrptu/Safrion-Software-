const fs=require('fs'),vm=require('vm'),assert=require('assert');
const mip=fs.readFileSync(__dirname+'/mip.js','utf8').split('// outras telas')[0];
const cen=fs.readFileSync(__dirname+'/cenario.js','utf8').split('\n').slice(5,44).join('\n');
function env(mode={}) {
 const seed={v:1,rev:2,vis:{},dia:{},rec:{},seq:{dia:1,rec:1,ra:1},apl:[]};
 const cseed={v:1,rev:4,ordens:{},unrelated:'preserve'};
 const disk=new Map([['talhao-os-mip-v1',JSON.stringify(seed)],['talhao-os-cenario-v1',JSON.stringify(cseed)]]);
 if(mode.badLegacy)disk.set('talhao-os-mip-v1','{bad');
 if(mode.badScenario)disk.set('talhao-os-cenario-v1','{bad');
 const writes=[];
 const b={MIP0:seed,CEN0:cseed,localStorage:{getItem:k=>disk.has(k)?disk.get(k):null,setItem:(k,v)=>{if(mode.fail)throw Error('quota');writes.push(k);disk.set(k,v)},removeItem:()=>{throw Error('Must not remove storage');}}};
 vm.createContext(b);vm.runInContext((mode.noScenario?'':cen)+'\n'+mip,b);
 return {b,disk,writes,run:s=>vm.runInContext(s,b)};
}
let n=0;
for(const mode of [{fail:true},{badLegacy:true},{badScenario:true},{noScenario:true}]) {
 const x=env(mode),before=JSON.stringify([...x.disk]);
 const r=x.run("mipMudar(null,s=>{s.vis.V1={id:'V1'};return {msg:'OK'}})");
 assert(r.erro);assert.equal(JSON.stringify([...x.disk]),before);assert.equal(x.writes.length,0);n++;
}
{
 const x=env(),legacy=x.disk.get('talhao-os-mip-v1');
 assert(!x.run("mipMudar(null,s=>{s.vis.V1={id:'V1'};return {msg:'OK'}})").erro);
 const c=JSON.parse(x.disk.get('talhao-os-cenario-v1'));
 assert(c.mip.vis.V1);assert.equal(c.mip.rev,3);assert.equal(c.mip.migradoDe.rev,2);assert.equal(c.unrelated,'preserve');assert.equal(c.rev,5);
 assert.equal(x.disk.get('talhao-os-mip-v1'),legacy);assert.deepEqual(x.writes,['talhao-os-cenario-v1','talhao-os-mip-v1:migrado']);n++;
 x.disk.set('talhao-os-mip-v1','{changed legacy');
 assert(x.run('mipGet().vis.V1'));n++;
}
console.log(n+' PASS: migration/adapter; emission and B-3 covered in separate tests.');
