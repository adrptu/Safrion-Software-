const fs=require('fs'),vm=require('vm'),crypto=require('crypto');
const path=process.argv[2]; const src=fs.readFileSync(path,'utf8');
const hash=crypto.createHash('sha256').update(src).digest('hex');
if(process.env.CHECA_HASH && hash!=='d96875f8348ccde6073e2780da510b2ca72cc974f27af096567d5181176e9677') throw Error('Fonte divergente');
const bloco=src.slice(src.indexOf('// >>> CAPACIDADE'),src.indexOf('// <<< CAPACIDADE'));
const ctx={};vm.createContext(ctx);vm.runInContext(bloco+'\nthis.C={capSaf,classeOc,capVeredito}',ctx);
const meses=[['2027-02','fev/27']], dias={'2027-02':20};
const rec=[{id:'trator',nome:'Tratores',un:1,jornada:8,turnos:1,disp:100}];
const oc=(id,h,dt)=>({id,mi:0,dt,a:{op:'Teste',nome:id},rp:{itens:[{nh:h,h,nq:h,Hin:2000}],falta:{semHoras:0}},cfs:[{rec:{trator:1}}]});
const A=[oc('A1',100,'2027-02-10')], B=[oc('B1',40,'2027-02-10'),oc('B2',200,'2027-02-28')];
const period={A:['2027-02-01','2027-02-15'],B:['2027-02-01','2027-02-15']};
function view(id,own,other,oid){
 const typed=own.map(i=>({...i,cls:ctx.C.classeOc(i.dt,i.mi,...period[id])}));
 const G=ctx.C.capSaf(typed,[{id:oid,nome:oid,ini:period[oid][0],fim:period[oid][1],oc:other}],rec,meses,dias);   // SAF-C02: período da outra safra (única adaptação)
 const counts={antes:0,fora:0,depois:0,cal:0};typed.forEach(i=>counts[i.cls]++);
 const verdict=ctx.C.capVeredito(G,typed,{aPlano:100,semPlano:[],cls:counts,ini:period[id][0],outras:{A:'A',B:'B'},pend:0,semHoras:0,incompleto:'',periodoCal:'fev/27'});
 return {view:id,source_period:period[id],occurrences:typed.map(i=>({id:i.id,dt:i.dt,cls:i.cls,h:i.rp.itens[0].nh})),cell:G.trator.cells[0],verdict};
}
const a=view('A',A,B,'B'),b=view('B',B,A,'A');
console.log(JSON.stringify({source_hash:hash,a,b,same_total:a.cell.d===b.cell.d},null,2));
