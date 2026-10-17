const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const ctx={CEN0:{diaOperacional:"2026-10-17"},g2ator:a=>a&&a.nome,g2papel:(a,p)=>a&&a.papel===p,g2quem:()=> 'Gestor',
 g2alc:()=>({}),g2alcN:()=>({modo:'todos',papeis:'gestor'}),g2pf:()=>null};
vm.createContext(ctx);
vm.runInContext(fs.readFileSync(__dirname+'/cenario.js','utf8'),ctx);
const operador={nome:'Teste',papel:'almoxarife'},gestor={nome:'Gestor',papel:'gestor'};
const seed=()=>({lotes:{k:{prod:'MAP',lote:'L1',un:'kg',fisico:100,quarentena:10,reservado:80}},movs:[],ajustes:[],reqs:{},ordens:{}});
let n=0;function test(name,fn){fn();console.log('PASS '+name);n++;}
test('submeter mantém físico e reserva, guarda motivo e autor',()=>{let c=seed();const r=ctx.cenPerdaNova(c,'k',30,'embalagem',operador);assert.equal(c.lotes.k.fisico,100);assert.equal(c.lotes.k.reservado,80);assert.equal(c.ajustes[0].motivo,'embalagem');assert.equal(c.ajustes[0].reg,'Teste');assert.ok(r.alerta);});
test('aprovar aplica uma vez sem apagar reserva alheia',()=>{let c=seed();const r=ctx.cenPerdaNova(c,'k',30,'embalagem',operador);ctx.cenAprovarAjuste(c,r.id,true,gestor);assert.equal(c.lotes.k.fisico,70);assert.equal(c.lotes.k.reservado,80);assert.equal(c.movs.length,1);assert.throws(()=>ctx.cenAprovarAjuste(c,r.id,true,gestor));assert.equal(c.lotes.k.fisico,70);});
test('AL09 recusada ao operador sem mutação',()=>{let c=seed();const r=ctx.cenPerdaNova(c,'k',20,'embalagem',operador);const before=JSON.stringify(c);assert.throws(()=>ctx.cenAprovarAjuste(c,r.id,true,operador));assert.equal(JSON.stringify(c),before);});
test('quantidade inválida e perda da quarentena não criam ajuste',()=>{for(const q of [0,-1,NaN,Infinity,101,95]){let c=seed();const before=JSON.stringify(c);assert.throws(()=>ctx.cenPerdaNova(c,'k',q,'teste',operador));assert.equal(JSON.stringify(c),before);}});
test('mudança física após submissão bloqueia aprovação',()=>{let c=seed();const r=ctx.cenPerdaNova(c,'k',20,'teste',operador);c.lotes.k.fisico=99;const before=JSON.stringify(c);assert.throws(()=>ctx.cenAprovarAjuste(c,r.id,true,gestor));assert.equal(JSON.stringify(c),before);});
test('repetição da chave não duplica ajuste',()=>{let c=seed();const run=()=>ctx.cenIdem(c,'teste:1','k:20:teste','Perda',()=>ctx.cenPerdaNova(c,'k',20,'teste',operador));run();run();assert.equal(c.ajustes.length,1);assert.equal(c.lotes.k.fisico,100);});
test('persistência estrita: falha preserva estado; retry mesma chave grava uma vez e recarrega',()=>{
  let saved=JSON.stringify(Object.assign(seed(),{v:1})),fail=true;
  ctx.CEN0.v=1;
  ctx.localStorage={getItem:()=>saved,setItem:(_,value)=>{if(fail)throw Error('quota');saved=value;}};
  const self={state:{draft:'motivo preservado'},setState(p){Object.assign(this.state,p);}};
  const before=saved;
  const run=()=>ctx.cenMudar(self,c=>ctx.cenIdem(c,'loss:1','k:20:teste','Perda',()=>ctx.cenPerdaNova(c,'k',20,'teste',operador)),{estrito:true});
  assert.ok(run().erro);assert.equal(saved,before);assert.equal(ctx.cenGet().ajustes.length,0);assert.equal(self.state.draft,'motivo preservado');
  fail=false;assert.ok(!run().erro);assert.equal(JSON.parse(saved).ajustes.length,1);assert.equal(ctx.cenGet().lotes.k.fisico,100);
  run();assert.equal(JSON.parse(saved).ajustes.length,1);
});
console.log(n+' testes; funções de ajuste/AL09 reais, perfis sintéticos; persistência em storage simulado; sem UI real.');
