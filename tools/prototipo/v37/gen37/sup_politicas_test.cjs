const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const c=vm.createContext({});vm.runInContext(fs.readFileSync(__dirname+'/sup_politicas.js','utf8'),c);
const v={grp:'Fertilizantes',seg:7,prazo:12,lim:400000,lote:'36 t',dep:'Galpão 2',abc:'A',crit:'Alta',met:'Necessidade datada',estado:'Vigente · v4',just:''};
const seed=()=>c.supPolSeed([{id:'p1',v}]);const gestor={k:'Ana',papeis:{gestor:true}};
const prop=s=>c.supPolPropor(s,'p1',{...v,seg:20,just:'Janela alterada'},s.rev);
let count=0;function test(n,f){f();console.log('PASS '+n);count++;}
test('propor preserva vigente e entrada',()=>{let s=seed(),before=JSON.stringify(s),n=prop(s);assert.equal(n.politicas.p1.vigente.seg,7);assert.equal(n.politicas.p1.proposta.dados.seg,20);assert.equal(JSON.stringify(s),before);});
test('simular não aprova nem modifica',()=>{let s=prop(seed()),before=JSON.stringify(s);assert.equal(c.supPolSimular(s,'p1').totalDias,32);assert.equal(JSON.stringify(s),before);});
test('publicar sem aprovação é rejeitado',()=>assert.throws(()=>c.supPolPublicar(prop(seed()),'p1',1,gestor)));
test('aprovação exige papel pertinente',()=>assert.throws(()=>c.supPolAprovar(prop(seed()),'p1',1,{k:'Caio',papeis:{pcp:true}})));
test('edição após aprovação invalida aceite',()=>{let s=c.supPolAprovar(prop(seed()),'p1',1,gestor);s=prop(s);assert.throws(()=>c.supPolPublicar(s,'p1',2,gestor));});
test('publicação cria versão e recibo; repetição não duplica',()=>{let s=c.supPolAprovar(prop(seed()),'p1',1,gestor),r=c.supPolPublicar(s,'p1',1,gestor);assert.equal(r.state.politicas.p1.versao,5);assert.equal(r.state.politicas.p1.vigente.seg,20);let rr=c.supPolPublicar(r.state,'p1',1,gestor);assert.equal(rr.repetido,true);assert.equal(JSON.stringify(rr.state),JSON.stringify(r.state));});
test('nova proposta não reutiliza recibo anterior',()=>{let s=c.supPolPublicar(c.supPolAprovar(prop(seed()),'p1',1,gestor),'p1',1,gestor).state;s=prop(s);assert.equal(s.politicas.p1.proposta.rev,2);s=c.supPolAprovar(s,'p1',2,gestor);assert.equal(c.supPolPublicar(s,'p1',2,gestor).state.politicas.p1.recibos.length,2);});
test('falha na gravação conserva proposta e vigente',()=>{let s=c.supPolAprovar(prop(seed()),'p1',1,gestor),raw=JSON.stringify(s);const storage={getItem:()=>raw,setItem(){throw Error('quota');}};let n=c.supPolPublicar(s,'p1',1,gestor).state;assert.throws(()=>c.supPolWrite(storage,seed(),n,s.rev));assert.equal(raw,JSON.stringify(s));assert.equal(s.politicas.p1.vigente.seg,7);assert.equal(s.politicas.p1.proposta.estado,'Aprovada');});
test('conflito de versão rejeita escrita',()=>{const s=seed(),n=prop(s),storage={getItem:()=>JSON.stringify(n),setItem(){throw Error('não deve escrever');}};assert.throws(()=>c.supPolWrite(storage,seed(),n,s.rev),/mudou/);});
test('dados corrompidos não viram seed silenciosamente',()=>assert.throws(()=>c.supPolRead({getItem:()=>'{'},seed())));
test('dias fracionários e valores inválidos rejeitados',()=>{for(const seg of [-1,1.2,NaN,Infinity])assert.throws(()=>c.supPolPropor(seed(),'p1',{...v,seg,just:'teste'},0));});
console.log(count+' testes aprovados');
