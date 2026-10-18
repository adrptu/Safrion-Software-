const fs=require('fs'),vm=require('vm'),assert=require('assert');
const pure={};vm.createContext(pure);vm.runInContext(fs.readFileSync(__dirname+'/mapa_camadas.js','utf8'),pure);
const base=fs.existsSync(__dirname+'/inicio.base.py')?fs.readFileSync(__dirname+'/inicio.base.py','utf8'):require('child_process').execFileSync('git',['show','29d923c754ceaf2843ab6f1fb3d3ac7817afba07:tools/prototipo/v37/gen37/areas/inicio.py'],{encoding:'utf8'});
const line=t=>{const i=base.indexOf(t);assert(i>=0,t);return base.slice(i,base.indexOf('\n',i));};
const old={};vm.createContext(old);
vm.runInContext(['const FASES','const FASEC','const FASE1','const PZC','const SEV','function osAb','function osImp','function osSemAb','function worstC','function nfx','function irrRecTxt'].map(line).join('\n')+'\n'+base.slice(base.indexOf('function osCls('),base.indexOf('function osStrip('))+'\nfunction ordsOf(){return ORD;}\nfunction Lc(l,k,t){return {k,t};}',old);
const a=base.indexOf("  if(l==='Irrigação'){ const x=M.irr[t];"),b=base.indexOf('\n  if(isIns(l,f))',a);
vm.runInContext('function originalIrr(x,ver){const l="Irrigação",f={ver},t="T",M={irr:{T:x}};'+base.slice(a,b)+'}',old);
let count=0;const same=(a,b)=>{assert.deepStrictEqual(JSON.parse(JSON.stringify(a)),JSON.parse(JSON.stringify(b)));count++;};
const phases=['A liberar','Liberadas','Em execução','Em conferência','Encerradas','Canceladas'];
const ord=(fase,extra={})=>({id:'OS-1',fase,pz:'no prazo',area:10,rz:3,selos:[],...extra});
const sets=[[],...phases.map(f=>[ord(f)]),[ord('Liberadas'),ord('Em execução',{id:'OS-2',pz:'atrasada'})],[ord('Liberadas',{selos:[['Impedida','red']]})],[ord('Liberadas',{selos:[['Pendência','yellow']]})],[ord('Liberadas',{area:0})],[ord('Liberadas',{rz:0})],[ord('Liberadas',{rz:12})]];
for(const os of sets)for(const fase of ['Todas',...phases])for(const ver of ['Fases','Avanço','Atrasos','Impedimentos']){old.ORD=os;const f={fase,ver};same(pure.mcOS(os,f),old.osCls('T',f));same(pure.mcOSLeg(f),old.osLegend('O.S.',f));}
for(const x of [null,{d:null,c:'gray',l:'sem leitura'},...[0,4.99,5,9.99,10,14.99,15].flatMap(d=>[false,true].map(est=>({d,est,c:est?'cloud':'yellow',l:'estado',rec:{br:5,np:2,lamP:2,por:3,pct:40}})))])for(const ver of ['Hoje','Balanço hídrico'])same(pure.mcIrr(x,ver),old.originalIrr(x,ver));
const ctx={semProt:false,alvos:null,alvTxt:'Ácaro',atras:0,dias:7};
same(pure.mcMIP([],{...ctx,semProt:true}),{c:'none',l:'sem cultura'});
same(pure.mcMIP([],{...ctx,alvos:[]}),{c:'none',l:'sem Ácaro no protocolo'});
same(pure.mcMIP([],{...ctx,alvos:['Ácaro'],dias:30}),{c:'gray',l:'sem vistoria de Ácaro em 30 dias'});
same(pure.mcMIP([],ctx),{c:'gray',l:'sem vistoria em 7 dias'});
for(const atras of [1,2])same(pure.mcMIP([],{...ctx,atras}),{c:'gray',l:'vistoria atrasada '+atras+(atras===1?' dia':' dias')});
const v={alvo:'Ácaro',S:{mc:'red',t:'Acima do NC'}};
same(pure.mcMIP([v,v],ctx),{c:'red',l:'Ácaro · acima do NC · +1'});

const ma=base.indexOf("  if(l==='MIP/MID'){ const vs=mipOf(t,f.per);"),mb=base.indexOf('  // NC10',ma);
vm.runInContext('function originalMIP(vs,ctx){const l="MIP/MID",f={per:""},t="T",ALV=ctx.alvos===null?null:["alvo"],MIPD={prots:{T:ctx.alvos&&ctx.alvos.length?["p"]:[]},prot:{p:{alvo:"alvo"}}};function mipOf(){return vs;}function mipSemProt(){return ctx.semProt;}function alvTxt(){return ctx.alvTxt;}function mipPer(){return ctx.dias;}function mipRitmo(){return {atras:ctx.atras};}function mipGet(){return {};}function mipP(v){return {alvo:v.alvo};}function mipMin(t){return t.charAt(0).toLowerCase()+t.slice(1);}'+base.slice(ma,mb)+'}',old);
for(const dias of [7,30])for(const alvos of [null,[],['alvo']])for(const semProt of [false,true])for(const atras of [0,1,2])for(const n of [0,1,2]){
 const ctx={dias,alvos,semProt,atras,alvTxt:'Ácaro'};
 const vs=Array.from({length:n},()=>({alvo:'Ácaro',v:{alvo:'Ácaro'},S:{mc:'red',t:'Acima do NC'}}));
 same(pure.mcMIP(vs,ctx),old.originalMIP(vs,ctx));
}
// A3: o contrato recebe somente a ordem visível, sem contar a oculta.
const visible=ord('Liberadas',{id:'VISIVEL',pz:'no prazo'}),hidden=ord('Liberadas',{id:'OCULTA',pz:'atrasada'});
same(pure.mcOS([visible],{fase:'Todas',ver:'Atrasos'}),{c:'ok',l:'VISIVEL · no prazo'});
assert.notEqual(pure.mcOS([visible,hidden],{fase:'Todas',ver:'Atrasos'}).l,pure.mcOS([visible],{fase:'Todas',ver:'Atrasos'}).l);

for(const ver of ['Hoje','Balanço hídrico']){
 const leg=pure.mcIrrLeg(ver);assert(leg.length>=6);assert.equal(leg[leg.length-1].k,null);
 for(const x of leg)assert.deepEqual(Object.keys(x).sort(),['k','t']);
}
for(const x of pure.mcMIPLeg())assert.deepEqual(Object.keys(x).sort(),['k','t']);
// Diferenciar ausência, preparo e origem estimada sem alterar sua classe.
same(pure.mcIrr(undefined,'Hoje'),{c:'none',l:''});
same(pure.mcIrr({d:null,c:'gray',l:'sequeiro'},'Balanço hídrico'),{c:'gray',l:'sequeiro'});
same(pure.mcIrr({d:10,c:'cloud',l:'sem necessidade · ≈ estimado'},'Hoje'),{c:'ok',est:true,l:'sem necessidade · ≈ estimado'});
for(const rec of [null,{br:0.05},{br:1,np:1,por:3},{br:1,np:2,por:2}])for(const est of [true,false]){
 const x={d:12,c:'yellow',l:'déficit',rec,est};same(pure.mcIrr(x,'Balanço hídrico'),old.originalIrr(x,'Balanço hídrico'));
}
assert(!('M' in pure)&&!('window' in pure)&&!('document' in pure));
// S4: a faixa e o mapa compartilham impedimentos/ordens abertas.
const candPath=fs.existsSync(__dirname+'/inicio.py')?__dirname+'/inicio.py':__dirname+'/areas/inicio.py';
const cand=fs.readFileSync(candPath,'utf8');
const strip=s=>s.slice(s.indexOf('function osStrip('),s.indexOf('function osFonte('));
vm.runInContext(strip(base),old);
vm.runInContext('function nfx(n,d){return mc_nfx(n,d);}',pure);
vm.runInContext(strip(cand),pure);
for(const os of sets)for(const fase of ['Todas',...phases])for(const ver of ['Fases','Avanço','Atrasos','Impedimentos'])same(pure.osStrip({fase,ver},os),old.osStrip({fase,ver},os));
// Contraprova: ignorar selos vermelhos precisa quebrar a paridade da faixa.
const bad={};vm.createContext(bad);vm.runInContext(fs.readFileSync(__dirname+'/mapa_camadas.js','utf8')+'\nfunction nfx(n,d){return mc_nfx(n,d);}',bad);
vm.runInContext(strip(cand),bad);vm.runInContext('mc_osImp=function(){return false;}',bad);
const blocked=[ord('Liberadas',{selos:[['Impedida','red']]})];
assert.notEqual(JSON.stringify(bad.osStrip({fase:'Todas',ver:'Impedimentos'},blocked)),JSON.stringify(old.osStrip({fase:'Todas',ver:'Impedimentos'},blocked)));
console.log(JSON.stringify({pass:count,scope:'VM e paridade de funções com fixtures; não substitui render LG/SR nem A5'}));
