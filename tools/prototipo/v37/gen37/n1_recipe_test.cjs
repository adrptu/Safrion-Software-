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
// As portas do grupo devem conservar a recusa, sem recibo de item liberado.
const groupSource=src.slice(src.indexOf('function cenGrupoAprovar('),src.indexOf('// efeito da liberação, sem o registro'));
const cenLines=fs.readFileSync(__dirname+'/cenario.js','utf8').split('\n');
// o cenIdem pelo nome, não pela linha: o C-3/C-4 e o Q5 deslocaram o cenario.js (integrador, 18/10)
const ci=cenLines.findIndex(l=>l.startsWith('function cenIdem('));
const idem=cenLines.slice(ci,ci+5).join('\n');
for(const cmd of ['approve','release']) {
 const o={id:'OS-0440',etapa:'A liberar',versao:'v1',area:2,ins:[{p:'Produto',un:'L',dose:3,tot:6}],osc:{ev:cmd==='release'?[{cmd:'CMD-42',v:'v1'}]:[],novo:{keys:['mip|V1|P1']}}};
 const c={ordens:{[o.id]:o},mip:{rec:{R:{id:'R',os:o.id,sit:'Receituário emitido',nome:'Produto',un:'L',dose:1,area:2}}},gruposExec:{G:{versao:1,ids:[o.id],escopos:{[o.id]:'scope'},origens:{[o.id]:'v1'},assinatura:'eq',historico:[]}}};
 let effects=0;
 const b={c,cenClone:x=>JSON.parse(JSON.stringify(x)),cenNum:String,cenQtd:(a,b)=>a*b,cenAgora:()=> '12:00',cenExigeAlc:()=> 'Ator',g2papel:()=>true,g2alc:()=>({papeis:['agronomo']}),OS_LIB:()=>['gestor'],g2alcQuem:()=> 'Ator',g2pf:()=>({k:'agro',t:'Ator'}),osc_o:(c,id)=>c.ordens[id],osUsoErro:()=>'',osUsoAtencao:()=>'',osc_libEfeito:()=>{effects++;return {msg:'OK'}},cenGrupoCanon:JSON.stringify,cenGrupoSnapshot:()=> 'snapshot',cenGrupoFicha:()=>({eq:'eq'}),cenGrupoEscopo:()=> 'scope',cenGrupoRecursos:()=>[]};
 vm.createContext(b);vm.runInContext(actual+'\n'+idem+'\n'+groupSource,b);
 if(cmd==='approve')assert.throws(()=>vm.runInContext("cenGrupoAprovar(c,'G','OS-0440',1,'snapshot','ator','test')",b),/Receituário/);
 else {const r=vm.runInContext("cenGrupoLiberar(c,'G',['OS-0440'],1,{'OS-0440':'snapshot'},'ator','test')",b);assert.equal(r.itens[0].estado,'Não liberada');assert.match(r.itens[0].motivo,/Receituário/);}
 assert.equal(effects,0);assert.equal(c.ordens[o.id].etapa,'A liberar');assert(!c.ordens[o.id].osc.ev.some(e=>e.cmd==='CMD-06'));assert(!(c.recibos||{})['test|OS-0440']);n++;
}
console.log(n+' PASS receipt guards including real group commands; legal checks/permission/reservation/group metadata stubbed.');
