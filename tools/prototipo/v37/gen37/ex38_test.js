const assert=require('node:assert/strict');
let count=0;const test=(name,fn)=>{fn();console.log('PASS '+name);count++};
const clone=x=>JSON.parse(JSON.stringify(x));
const mbReq=(c,o)=>c.reqs[o.req],mbConf=(c,id,p)=>cenConfAbertas(c,id).find(k=>k.prod===p),mbTx=x=>x;
const nd=cenNum,nf=cenNum,osTrilha=()=>[],osOrigem=()=>'',osInsSit=(o,x,it)=>it?'Em custódia':'Entregue';
const c=clone(CEN0),o=c.ordens['OS-0421'];
test('OS421: 80 necessários, 65 em custódia, faltam 15; adjuvante sem registro',()=>{
 const x=cenInsumosOrdem(c,o); assert.equal(x[0].previsto,80); assert.equal(x[0].custodia,65);assert.equal(x[0].falta,15);
 const a=x.find(i=>i.p==='Adjuvante espalhante');assert.equal(a.consumido,null);assert.equal(a.temReq,false);assert.equal(a.previsto,40);
});
test('P4/P5 nos blocos reais painel/MB01/MB02det',()=>{
 const a=panel(c,o); assert.equal(a[1].usado,'Sem registro');assert.match(a[1].sit,/Sem requisição/);assert.doesNotMatch(a[1].sit,/Entregue/);
 assert.match(a[0].sit,/falta para terminar 15 L/); assert.match(mbIns(c,o)[0].s,/falta para terminar 15 L/);assert.match(detail(c,o)[0].c,/falta para terminar 15 L/);
});
test('consumo zero registrado difere de registro ausente; lotes somam',()=>{
 const d=clone(c),r=d.reqs[o.req];r.itens[0].consumido=0;r.itens.push({...r.itens[0],lote:'outro',custodia:5});
 const x=cenInsumosOrdem(d,d.ordens[o.id])[0]; assert.equal(x.consumido,0);assert.equal(x.custodia,70);assert.equal(x.falta,10);
});
test('custódia acima da necessidade, ausência e unidade inválida',()=>{
 const d=clone(c),i=d.reqs[o.req].itens[0]; i.custodia=81;assert.equal(cenInsumosOrdem(d,o)[0].falta,0);
 i.un='kg';assert.equal(cenInsumosOrdem(d,o)[0].falta,null);delete d.reqs[o.req];assert.equal(cenInsumosOrdem(d,o)[0].consumido,null);
});
test('pendência offline não é deduzida duas vezes; estado fica explícito',()=>{
 const d=clone(c),x=d.ordens[o.id];x.ap.push({sinc:false,ha:20,cons:{'Fungicida A':10}});
 const p=cenInsumosOrdem(d,x)[0];assert.equal(p.previsto,80);assert.equal(p.falta,15);assert.equal(p.pendente,true);assert.match(cenInsumoSaldoTxt(p),/pendente/);
});
test('projeção não altera cenário',()=>{const before=JSON.stringify(c);cenInsumosOrdem(c,o);cenPreparoOrdem(c,o);assert.equal(JSON.stringify(c),before)});
test('P1/P2: OS421 tanque do PJ e instrução; OS424 painel/app/ficha mesma fonte',()=>{
 const p=cenPreparoOrdem(c,o);assert.deepEqual([p.tanque,p.vazao,p.haCarga,p.n,p.ultima],[3000,100,30,6,10]);
 assert.equal(panelPrep(c,o),cenPreparoTxt(p));const v={};oscPreparo(c,v);const q=cenPreparoOrdem(c,c.ordens['OS-0424']);
 assert.equal(v.preparo,panelPrep(c,c.ordens['OS-0424']));assert.deepEqual([q.n,q.ultima],[5,8]);assert.equal(q.cargas[4].prods[0].q,4);
});
test('sem conjunto, substituição sem capacidade e instrução ausente não usam padrão',()=>{
 const d=clone(c),x=d.ordens[o.id];x.rec={PJ:'DI'};assert.match(cenPreparoOrdem(d,x).motivo,/Sem conjunto/);
 delete x.rec;x.instrucao=null;assert.match(cenPreparoOrdem(d,x).motivo,/Vazão não informada/);
 x.instrucao={vazao:100,versao:'v999'};assert.equal(cenPreparoOrdem(d,x).ok,false);
});
test('cenário salvo usa instrução da semente só na mesma versão',()=>{
 const d=clone(c),x=d.ordens[o.id];delete x.instrucao;assert.equal(cenPreparoOrdem(d,x).ok,true);
 x.versao='v999';assert.equal(cenPreparoOrdem(d,x).ok,false);
});
test('zero, negativos, NaN e infinito',()=>{
 const d=clone(c),x=d.ordens[o.id];x.saldo=0;assert.equal(cenPreparoOrdem(d,x).n,0);
 for(const n of [-1,NaN,Infinity]){x.saldo=n;assert.equal(cenPreparoOrdem(d,x).ok,false)}
 x.saldo=10;for(const n of [0,-1,NaN,Infinity]){x.instrucao.vazao=n;assert.equal(cenPreparoOrdem(d,x).ok,false)}
});
test('P3: 400 combinações, cada carga cheia/parcial mantém dose e fecha área/volume',()=>{
 let seed=38;const rnd=()=>{seed=(1664525*seed+1013904223)>>>0;return seed/4294967296};const old=CEN_PREP_ATIVOS.a05.tanque;
 try {for(let j=0;j<400;j++){
  const d=clone(c),x=d.ordens[o.id];CEN_PREP_ATIVOS.a05.tanque=100+Math.floor(rnd()*5000);x.instrucao.vazao=20+rnd()*300;x.saldo=0.01+rnd()*500;
  x.ins=[{p:'A',dose:rnd()*4,un:'L'},{p:'B',dose:rnd()*2,un:'kg'}];const p=cenPreparoOrdem(d,x);assert.equal(p.ok,true);
  let ha=0;for(const cg of p.cargas){ha+=cg.area;assert.ok(cg.area>0);assert.ok(cg.vol<=p.tanque+1e-7);for(let k=0;k<x.ins.length;k++)assert.ok(Math.abs(cg.prods[k].q/cg.area-x.ins[k].dose)<1e-12)}
  assert.ok(Math.abs(ha-x.saldo)<1e-7);
 }}finally{CEN_PREP_ATIVOS.a05.tanque=old}
});
test('app real: carga preparada mantém consumo, troca de versão bloqueia e aviso recupera',()=>{
 const d=clone(c),r=d.reqs['REQ-039'];r.itens.forEach(i=>{i.custodia=65;i.confirmado=true}); CEN_MEM=d;
 const self={state:{},setState(x){Object.assign(this.state,x)}},v={};appVals(self,v);assert.equal(v.cg_area,'30 ha');assert.equal(v.cg_prods[0].q,'15 L');
 const before=JSON.stringify(d);v.prim();assert.equal(JSON.stringify(d),before);assert.equal(self.state.feitas,1);
 const next={};appVals(self,next);assert.equal(next.cg_t,'Carga 2 de 5');
 d.ordens['OS-0424'].versao='v2';const blocked={};appVals(self,blocked);assert.equal(blocked.primDis,true);assert.match(blocked.preparo,/Vazão não informada/);
});
console.log(count+'/'+count+' cenários Node; P3: 400 combinações');
