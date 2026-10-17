const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const path = require('node:path');
const base = fs.readFileSync(path.join(__dirname,'dados_manutencao.py'),'utf8');
const deps = ['manNec','manLivreIt'].map(n => base.split('\n').find(s=>s.startsWith('function '+n+'('))).join('\n');
const ctx = vm.createContext({});
vm.runInContext(deps+'\n'+fs.readFileSync(path.join(__dirname,'sup_necessidades.js'),'utf8'),ctx);
function run(c,pol={prazo:3,seguranca:2}) { return JSON.parse(JSON.stringify(ctx.supNecMan(c,'OM-0234',pol))); }
function fixture(){return {oms:{'OM-0234':{id:'OM-0234',etapa:'A liberar',aid:'a02',serv:'Revisão 250 h',janIso:'2026-09-28',pecas:[{item:'F',qtd:4,res:1}]}},itens:{F:{nome:'Filtro',un:'un',saldo:1,reservado:1}}};}
let tests=0;
function test(name,fn){fn();tests++;console.log('PASS '+name);}
test('origem e falta descontam reserva própria uma vez',()=>{const r=run(fixture());assert.equal(r.itens[0].falta,3);assert.equal(r.pedirAte,'2026-09-23');assert.equal(r.servico,'Revisão 250 h');});
test('reserva de outra ordem não cobre demanda',()=>{const c=fixture();c.oms['OM-0234'].pecas[0].res=0;assert.equal(run(c).itens[0].falta,4);});
test('livre cobre apenas necessidade sem reserva',()=>{const c=fixture();c.itens.F.saldo=3;assert.equal(run(c).itens[0].falta,1);});
test('linhas repetidas não reutilizam saldo livre',()=>{const c=fixture();c.oms['OM-0234'].pecas=[{item:'F',qtd:3,res:0},{item:'F',qtd:2,res:0}];c.itens.F={nome:'Filtro',un:'un',saldo:2,reservado:0};assert.equal(run(c).itens[0].falta,3);});
test('OM encerrada não gera compra',()=>{const c=fixture();c.oms['OM-0234'].etapa='Encerrada';assert.equal(run(c).itens.length,0);});
test('item sem cadastro não vira compra fictícia',()=>{const c=fixture();delete c.itens.F;assert.equal(run(c).pendencias.length,1);assert.equal(run(c).itens.length,0);});
test('política ausente não inventa prazo',()=>assert.equal(run(fixture(),null).pedirAte,null));
test('data inválida não rola silenciosamente para outro mês',()=>{const c=fixture();c.oms['OM-0234'].janIso='2026-02-30';assert.equal(run(c).pedirAte,null);});
test('ano bissexto e data civil',()=>{const c=fixture();c.oms['OM-0234'].janIso='2028-03-01';assert.equal(run(c,{prazo:1,seguranca:0}).pedirAte,'2028-02-29');});
test('consulta não reserva nem modifica estado',()=>{const c=fixture(),before=JSON.stringify(c);run(c);assert.equal(JSON.stringify(c),before);});
test('OM inexistente é pendência explícita',()=>assert.equal(run({oms:{},itens:{}}).pendencias.length,1));
test('linha inválida não produz necessidade parcial do mesmo item',()=>{const c=fixture();c.oms['OM-0234'].pecas.push({item:'F',qtd:-1,res:0});assert.equal(run(c).itens.length,0);});
test('consumidores recalculam sem duplicar nem manter saldo antigo',()=>{
 const c=fixture(),rows=[],cot={v:{},p:{}};
 Object.assign(ctx,{manGet:()=>c,RW:()=>rows,RF:()=>cot,B:x=>x,M:x=>x,T:x=>x,nf:String,dm:String,chipc:(t,c)=>({t,c})});
 ctx.supAtualizaNec({});ctx.supAtualizaCot({});assert.equal(rows.find(r=>r.id==='MAN|F').v.falta,3);assert.equal(cot.v.itens,1);
 c.itens.F.saldo=10;ctx.supAtualizaNec({});ctx.supAtualizaCot({});assert.equal(rows.filter(r=>r.id==='MAN|F').length,1);assert.equal(rows.find(r=>r.id==='MAN|F').v.falta,0);assert.equal(cot.v.itens,0);
 delete c.oms['OM-0234'];ctx.supAtualizaNec({});ctx.supAtualizaCot({});assert.equal(rows.some(r=>r.id==='MAN|F'),false);assert.equal(cot.p.estado[0].c,'yellow');
});
console.log(tests+' testes aprovados');
