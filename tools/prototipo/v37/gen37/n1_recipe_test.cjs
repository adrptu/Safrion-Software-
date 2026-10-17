const fs=require('fs'),vm=require('vm'),assert=require('assert');
const src=fs.readFileSync(__dirname+'/areas/processo_os.py','utf8');
const actual=src.slice(src.indexOf('function osVn('),src.indexOf('// OS-LOTE-F1 (movida'));
let n=0;
for(const cmd of ['approve','release'])for(const mutation of ['same','dose','area','unit','product','missing','cancelled','duplicate','total','unrelated','eradication']){
 const o={id:'OS-0440',etapa:'A liberar',versao:'v1',area:2,ins:[{p:'Produto',un:'L',dose:1,tot:2}],osc:{ev:[],novo:{keys:['mip|V1|P1'],mip:{vis:'V1',rec:'REC-001',ra:'RA-0001',kind:'controlar'}}}};
 const r={id:'REC-001',ra:'RA-0001',os:o.id,sit:'Receituário emitido',nome:'Produto',un:'L',dose:1,area:2};const c={ordens:{[o.id]:o},mip:{rec:{'REC-001':r}}};
 if(mutation==='dose')o.ins[0].dose=3;
 if(mutation==='area')o.area=1;
 if(mutation==='unit')o.ins[0].un='kg';
 if(mutation==='product')o.ins[0].p='Outro';
 if(mutation==='missing')delete c.mip;
 if(mutation==='cancelled')r.sit='Cancelado';
 if(mutation==='duplicate')c.mip.rec.R2={...r,id:'R2'};
 if(mutation==='total')o.ins[0].tot=3;
 if(mutation==='unrelated'){o.osc.novo={};delete c.mip;}
 if(mutation==='eradication'){o.ins=[];o.osc.novo.mip={rec:'',kind:'erradicar'};delete c.mip;}
 let effects=0;const b={c,cenNum:String,cenQtd:(a,b)=>a*b,cenAgora:()=> '12:00',cenExigeAlc:()=> 'Ator',g2papel:()=>true,g2alc:()=>({papeis:['agronomo']}),OS_LIB:()=>['gestor'],g2alcQuem:()=> 'Ator',osc_o:(c,id)=>c.ordens[id],osUsoErro:()=>'',osUsoAtencao:()=>'',osc_libEfeito:()=>{effects++;return {msg:'OK'}}};
 vm.createContext(b);vm.runInContext(actual,b);
 const expr=cmd==='approve'?"osc_aprovar(c,'OS-0440','ator')":"osc_liberar(c,'OS-0440',false,'','ator')";
 if(['same','unrelated','eradication'].includes(mutation)){vm.runInContext(expr,b);assert(o.osc.ev.length);}
 else {assert.throws(()=>vm.runInContext(expr,b),/Receituário/);assert.equal(o.osc.ev.length,0);assert.equal(effects,0);}
 n++;
}
console.log(n+' PASS receipt guards; legal checks/permission/reservation stubbed.');
