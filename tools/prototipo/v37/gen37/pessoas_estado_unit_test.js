const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const ps=[{id:'p1',v:{nome:'Pessoa A',sit:'Ativa',equipe:'Oficina'}}],es=[{id:'e1',v:{nome:'Oficina',cal:'seg–sex · 07–17h'}}];
const ctx=vm.createContext({PESSOAS0:{v:'demo-1',pessoas:ps,equipes:es},CONF0:{v:'conf-1',pessoas:[],ev:[],hoje:'2026-09-26'},G2_PERFIS:[],G2_PAPEIS:[],g2papT:x=>Array.isArray(x)?x.join(" e "):String(x),g2perfisDe:()=>[{k:'Gestor',papeis:{gestor:'gestor'}}]});
for(const f of ['configuracoes.js','pessoas_estado.js'])vm.runInContext(fs.readFileSync(__dirname+'/'+f,'utf8'),ctx);
const c={};const copy=x=>JSON.parse(JSON.stringify(x));
assert.equal(ctx.pessoasCapacidade(c).p1.v,1);
const p=copy(ps),e=copy(es);e[0].v.cal='seg–sex · 08–16h';
ctx.pessoasGravar(c,p,e,0,'a','Gestor');assert.equal(c.cadPessoas.rev,1);assert.equal(ctx.pessoasCapacidade(c).p1.v,2);
e[0].v.cal='injetado depois';assert.equal(ctx.pessoasCapacidade(c).p1.calendario,'seg–sex · 08–16h');
const saved=JSON.stringify(c);assert.throws(()=>ctx.pessoasGravar(c,ps,es,0,'b','Gestor'),/mudaram/);assert.equal(JSON.stringify(c),saved);
assert.throws(()=>ctx.pessoasGravar(c,ps,es,1,'c','Desconhecido'),/perfil/);assert.equal(JSON.stringify(c),saved);
const e2=copy(c.cadPessoas.equipes);const p2=copy(p);p2[0].v.nome='Pessoa renomeada';
ctx.pessoasGravar(c,p2,e2,1,'d','Gestor');assert.equal(ctx.pessoasCapacidade(c).p1.v,2); // nome não muda dedicação
const again=JSON.stringify(c);assert.equal(ctx.pessoasGravar(c,p2,e2,1,'d','Gestor').repetido,true);assert.equal(JSON.stringify(c),again);
assert.throws(()=>ctx.pessoasGravar(c,p,e2,2,'d','Gestor'),/conflito/);assert.equal(JSON.stringify(c),again);
ctx.pessoasGravar(c,[],e2,2,'e','Gestor');assert.equal(ctx.pessoasCapacidade(c).p1,undefined);
ctx.pessoasGravar(c,p2,e2,3,'f','Gestor');assert.equal(ctx.pessoasCapacidade(c).p1.v,4); // ABA não ressuscita aprovação antiga
const now=JSON.stringify(c);assert.throws(()=>ctx.pessoasGravar(c,[p2[0],p2[0]],e2,4,'g','Gestor'),/repetido/);assert.equal(JSON.stringify(c),now);
const wrong=copy(p2);wrong[0].v.equipe='Ausente';assert.throws(()=>ctx.pessoasGravar(c,wrong,e2,4,'h','Gestor'),/equipe/);assert.equal(JSON.stringify(c),now);
console.log('PASS CD04 fonte: calendário atual por ID, revisão otimista, cópia defensiva, ator, idempotência/conflito, rename, remoção/recriação ABA, duplicidade e equipe inexistente. Prova unitária, não teste de UI.');
ctx.CAP_ESPECIALIDADES=['Mecânico','Eletricista','Lubrificador','Terceiro (concessionária)'];
vm.runInContext(fs.readFileSync(__dirname+'/capacidade.js','utf8'),ctx);
ctx.capacidadeGravar(c,'p1',{Mecânico:25,Lubrificador:15},'Dedicação informada',0,4,'cap1','Gestor');
assert.equal(ctx.capacidadeDe(c,'Mecânico').hhSemana,25);assert.equal(ctx.capacidadeDe(c,'Lubrificador').hhSemana,15);
const capSaved=JSON.stringify(c);assert.equal(ctx.capacidadeGravar(c,'p1',{Lubrificador:15,Mecânico:25},'Dedicação informada',0,4,'cap1','Gestor').repetido,true);assert.equal(JSON.stringify(c),capSaved);
for(const [novo,mot,v,pv,k] of [[{Mecânico:41},'x',1,4,'cap2'],[{Mecânico:20},'',1,4,'cap3'],[{Mecânico:20},'x',0,4,'cap4'],[{Mecânico:20},'x',1,3,'cap5'],[{Outra:2},'x',1,4,'cap6'],[{Mecânico:NaN},'x',1,4,'cap7']]){
 assert.throws(()=>ctx.capacidadeGravar(c,'p1',novo,mot,v,pv,k,'Gestor'));assert.equal(JSON.stringify(c),capSaved);
}
const short=copy(e2);short[0].v.cal='seg–sex · 08–14h';ctx.pessoasGravar(c,p2,short,4,'i','Gestor');
assert.equal(ctx.capacidadeDe(c,'Mecânico'),null); // fonte mudou: 40h antigas não viram 30h automaticamente
ctx.capacidadeGravar(c,'p1',{Mecânico:20,Lubrificador:10},'Repartição nova',1,5,'cap8','Gestor');assert.equal(ctx.capacidadeDe(c,'Mecânico').hhSemana,20);
ctx.capacidadeGravar(c,'p1',null,'Retirada',2,5,'cap9','Gestor');assert.equal(ctx.capacidadeDe(c,'Mecânico'),null);assert.equal(ctx.capacidadeRegistro(c,'p1').v,3);
assert.throws(()=>ctx.capacidadeGravar(c,'p1',{Mecânico:20},'Rascunho antigo',1,5,'cap10','Gestor'),/mudou/);
console.log('PASS D11b comandos: soma <= jornada, ID estável, motivo/versão/recibo, repetição com ordem de campos diversa, rejeição sem mutação, revisão de calendário e retirada ABA.');
ctx.capacidadeGravar(c,'p1',{Mecânico:20},'Ativar',3,5,'cap11','Gestor');
const contrato=copy(p2);contrato[0].v.ate='2026-09-25';ctx.pessoasGravar(c,contrato,short,5,'j','Gestor');
assert.equal(ctx.capacidadeDe(c,'Mecânico'),null);
assert.throws(()=>ctx.capacidadeGravar(c,'p1',{Mecânico:20},'Vencido',4,6,'cap12','Gestor'),/vigência/);
const antesPermissao=JSON.stringify(c);ctx.g2perfisDe=()=>[{k:'Gestor',papeis:{operador:'operador'}}];
assert.throws(()=>ctx.capacidadeGravar(c,'p1',null,'Retirar',4,6,'cap13','Gestor'),/decisão/);assert.equal(JSON.stringify(c),antesPermissao);
ctx.PESSOAS0.v='demo-2';assert.equal(ctx.capacidadeDe(c,'Mecânico'),null);
console.log('PASS vigência contratual, retirada sem papel gestor recusada e mudança da versão da fonte invalida leitura.');

const inativa=copy(ps);inativa[0].v.sit='Inativa';const ci={};ctx.g2perfisDe=()=>[{k:'Gestor',papeis:{gestor:'gestor'}}];
ctx.pessoasGravar(ci,inativa,[],0,'inativa-sem-equipe','Gestor');assert.equal(ctx.pessoasCapacidade(ci).p1.calendario,null);
assert.throws(()=>ctx.pessoasGravar({},ps,[],0,'ativa-sem-equipe','Gestor'),/equipe/);
console.log('PASS exclusão de equipe sem ativos preserva pessoa inativa; ativa exige equipe válida.');
