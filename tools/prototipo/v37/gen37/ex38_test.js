const assert=require('node:assert/strict');
let count=0,failed=0;const test=(name,fn)=>{try{fn();console.log('PASS '+name);count++}catch(e){failed++;console.log('FAIL '+name+': '+e.message)}};
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
test('offline real: 20ha/10L, necessidade 15L, Adjuvante35L, 5cargas e web95L',()=>{
 const d=clone(c),x=d.ordens[o.id];cenSinal(d,false);cenIniciarTurno(d,x.id);cenFecharTurno(d,20,3,{'Fungicida A':10},'EX38');
 const p=cenInsumosOrdem(d,x);assert.deepEqual([p[0].previsto,p[0].custodia,p[0].falta,p[1].previsto],[70,55,15,35]);
 assert.equal(p[0].pendente,true);assert.equal(cenPreparoOrdem(d,x).n,5);assert.equal(panel(d,x)[0].usado,'95 L');assert.match(panel(d,x)[1].sit,/previsto para o saldo 35 L/);
 assert.match(mbIns(d,x)[0].s,/com você 55 L/);assert.match(detail(d,x)[0].c,/falta para terminar 15 L/);
 const before=JSON.stringify(d);cenInsumosOrdem(d,x);cenPreparoOrdem(d,x);assert.equal(JSON.stringify(d),before);
 cenSinal(d,true);assert.equal(cenInsumosOrdem(d,x)[0].falta,15);assert.equal(panel(d,x)[0].usado,'105 L');
});
test('toda a área offline não solicita nova retirada',()=>{
 const d=clone(c),x=d.ordens[o.id];cenSinal(d,false);cenIniciarTurno(d,x.id);cenFecharTurno(d,160,8,{'Fungicida A':65},'EX38 fim');
 assert.equal(cenInsumosOrdem(d,x)[0].falta,0);assert.equal(cenPreparoOrdem(d,x).n,0);assert.doesNotMatch(mbIns(d,x)[0].s,/retirar|falta para terminar [1-9]/);
});
test('0,2 + 39,8ha não cria quinta carga fantasma',()=>{
 const d=clone(c),x=d.ordens[o.id];cenIniciarTurno(d,x.id);cenFecharTurno(d,.2,1,{'Fungicida A':.1},'primeiro');
 cenIniciarTurno(d,x.id);cenFecharTurno(d,39.8,2,{'Fungicida A':19.9},'segundo');
 const p=cenPreparoOrdem(d,x);assert.equal(p.n,4);assert.ok(Math.abs(p.ultima-30)<1e-9);assert.ok(p.cargas.every(x=>x.area>0));
});
test('projeção recusa dados inválidos sem lançar erro nem inventar zero',()=>{
 const d=clone(c),x=d.ordens[o.id];x.ins[0].dose=NaN;assert.equal(cenInsumosOrdem(d,x)[0].previsto,null);x.ins[0].dose=.5;d.reqs[x.req].itens[0].custodia=Infinity;assert.equal(cenInsumosOrdem(d,x)[0].falta,null);assert.deepEqual(cenInsumosOrdem(d,null),[]);
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
test('P3: 400 combinações, centésimos por carga conservam total e fecham área/volume',()=>{
 let seed=38;const rnd=()=>{seed=(1664525*seed+1013904223)>>>0;return seed/4294967296};const old=CEN_PREP_ATIVOS.a05.tanque;
 try {for(let j=0;j<400;j++){
  const d=clone(c),x=d.ordens[o.id];CEN_PREP_ATIVOS.a05.tanque=100+Math.floor(rnd()*5000);x.instrucao.vazao=20+rnd()*300;x.saldo=0.01+rnd()*500;
  x.ins=[{p:'A',dose:rnd()*4,un:'L'},{p:'B',dose:rnd()*2,un:'kg'}];const p=cenPreparoOrdem(d,x);assert.equal(p.ok,true);
  let ha=0;for(const cg of p.cargas){ha+=cg.area;assert.ok(cg.area>0);assert.ok(cg.vol<=p.tanque+1e-7);for(let k=0;k<x.ins.length;k++)assert.ok(Math.abs(cg.prods[k].q-cg.area*x.ins[k].dose)<0.01+1e-9)}
  assert.ok(Math.abs(ha-x.saldo)<1e-7);
  for(let k=0;k<x.ins.length;k++) assert.equal(p.cargas.reduce((s,cg)=>s+Math.round(cg.prods[k].q*100),0),Math.round(cenQtd(x.ins[k].dose,x.saldo)*100));
 }}finally{CEN_PREP_ATIVOS.a05.tanque=old}
});
test('app real: carga preparada mantém consumo, troca de versão bloqueia e aviso recupera',()=>{
 const d=clone(c),r=d.reqs['REQ-039'];r.itens.forEach(i=>{i.custodia=65;i.confirmado=true}); CEN_MEM=d;
 const self={state:{},setState(x){Object.assign(this.state,x)}},v={};appVals(self,v);assert.equal(v.cg_area,'30 ha');assert.equal(v.cg_prods[0].q,'15 L');
 const before=JSON.stringify(d);v.prim();assert.equal(JSON.stringify(d),before);assert.equal(self.state.feitas,1);
 const next={};appVals(self,next);assert.equal(next.cg_t,'Carga 2 de 5');
 d.ordens['OS-0424'].versao='v2';const blocked={};appVals(self,blocked);assert.equal(blocked.primDis,true);assert.match(blocked.preparo,/Vazão não informada/);
});
test('v2 sem instrução permite confirmar recebimento antes do preparo',()=>{
 const d=clone(c),x=d.ordens['OS-0424'];x.versao='v2';d.reqs['REQ-039'].itens.forEach(i=>{i.entregue=65;i.custodia=65;i.confirmado=false;});CEN_MEM=d;
 const self={state:{},setState(x){Object.assign(this.state,x)}},v={};appVals(self,v);assert.equal(v.primDis,false);assert.equal(v.prim_t,'Confirmar recebimento');v.prim();
 const w={};appVals(self,w);assert.equal(w.primDis,true);assert.match(w.preparo,/Vazão não informada/);assert.doesNotMatch(w.cg_t,/Carga 0/);
});
test('MB01 preserva retirada, embalagem, custódia e conferência',()=>{
 const d=clone(c),x=d.ordens['OS-0424'];assert.match(mbIns(d,x)[0].s,/retirar 65 L.*13 × galão 5 L/);
 d.reqs['REQ-039'].itens.forEach(i=>{i.entregue=65;i.custodia=65;i.confirmado=false;});cenConfirmarRecebimento(d,'REQ-039');d.reqs['REQ-039'].itens[0].custodia=1;
 assert.match(mbIns(d,x)[0].s,/com você 1 L/);
 cenIniciarTurno(d,x.id);cenFecharTurno(d,20,2,{'Fungicida A':2},'consumo divergente');assert.match(mbIns(d,x)[0].s,/em conferência.*com você 1 L/);
});
console.log(count+'/'+(count+failed)+' cenários Node; P3: 400 combinações');if(failed)process.exitCode=1;
