// SAF-FAZ-2: contrato independente de Codex; domínio/fixtures pertencem ao Claude.
// node safra_grupo_contrato_test.js; SG_ARQ=... usa outra candidata sem alterar o teste.
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const source = fs.readFileSync(process.env.SG_ARQ || path.join(__dirname, 'safra_grupo.js'), 'utf8');
const G = new Function(source + '\nreturn {sgGrupo,sgCompor,sgLeitura,sgEnviar};')();
const FX = JSON.parse(fs.readFileSync(path.join(__dirname, 'safra_grupo_fixtures.json'), 'utf8'));
const copy = value => structuredClone(value);
const freeze = value => { Object.freeze(value); Object.values(value).forEach(v => { if (v && typeof v === 'object') freeze(v); }); return value; };
function context(deps = {}) { let sequence = 0; return { rec: {}, deps: id => deps[id] || {}, novoId: type => `CONTRATO-${type}-${++sequence}` }; }
const group = () => ({mae:'MAE',nome:'Safra sintética',subs:[{id:'A',faz:'Santa Rita',estado:'Em planejamento'},{id:'B',faz:'Lagoa Grande',estado:'Rascunho'}]});
const edit = (saf, fazendas, chave='editar') => ({chave,saf,nome:'Safra revista',ini:'2026-09-01',fim:'2027-08-31',fazendas});
let passed=0, failed=0;
function test(name, run) { try { run(); passed++; console.log('OK '+name); } catch(error) { failed++; console.log('FALHOU '+name+'\n'+error.stack); } }

test('C01 criar grupo não muda entradas congeladas nem safras anteriores', () => {
 const safs=freeze(copy(FX.safs)), pedido=freeze(copy(FX.pedidos.duas_fazendas));
 const result=G.sgCompor(safs,pedido,context());
 assert.equal(result.ok,true); assert.deepEqual(result.safs.slice(0,safs.length),safs);
 assert.equal(result.safs.length,safs.length+2); assert.equal(new Set(result.safs.map(s=>s.id)).size,result.safs.length);
 assert.deepEqual(G.sgGrupo(result.safs,result.mae).subs.map(s=>s.faz),['Santa Rita','Lagoa Grande']);
});

test('C02 um vínculo bloqueia toda edição, inclusive nome/datas e adição de outra fazenda', () => {
 const ctx=context(); const original=G.sgCompor(copy(FX.safs),FX.pedidos.duas_fazendas,ctx);
 const children=G.sgGrupo(original.safs,original.mae).subs, blocked=children[0];
 const deps={ [blocked.id]:{orcamento_aprovado:true} }; const op=context(deps);
 const before=copy(original.safs); const result=G.sgCompor(freeze(original.safs),edit(children[1].id,['Lagoa Grande','Fazenda Nova']),op);
 assert.equal(result.ok,false); assert.deepEqual(result.safs,before); assert.deepEqual(op.rec,{});
 assert.equal(result.bloqueios[0].saf,blocked.id); assert.ok(result.bloqueios[0].motivos.some(m=>m.destino==='Orçamento da safra'));
});

for (const [label,dependency] of Object.entries({cultivo:{cultivos:1},compra:{sol:{id:'SOL-SINT',estado:'Enviada'}},os:{os:['OS-SINT']},plano:{plano_aprovado:true}})) {
 test('C03 remoção com '+label+' é recusada com destino e sem mutação', () => {
  const safs=[{id:'A',faz:'Santa Rita',nome:'Safra',ini:'2026-09-01',fim:'2027-08-31',estado:'Rascunho'}];
  const result=G.sgCompor(freeze(copy(safs)),edit('A',['Lagoa Grande']),context({A:dependency}));
  assert.equal(result.ok,false);assert.deepEqual(result.safs,safs);assert.ok(result.bloqueios[0].motivos.every(m=>m.t&&m.destino));
 });
}

test('C04 edição preserva vínculos da sub-safra existente e nova fazenda nasce em rascunho', () => {
 const safs=freeze(copy(FX.safs)),ctx=context(FX.deps);
 const result=G.sgCompor(safs,edit('S2627',['Santa Rita','Lagoa Grande']),ctx);assert.equal(result.ok,true);
 const g=G.sgGrupo(result.safs,'S2627');assert.equal(g.subs[0].id,'S2627');assert.equal(g.subs[0].estado,'Em planejamento');
 assert.equal(g.subs[1].estado,'Rascunho');assert.equal(g.subs[1].ro,undefined);
 assert.deepEqual(result.safs.find(s=>s.id==='LG2627'),FX.safs.find(s=>s.id==='LG2627'));
});

test('C05 recusa não consome chave: corrigir e reenviar aplica uma vez; replay não gera IDs', () => {
 const ctx=context(),pedido={...FX.pedidos.duas_fazendas,chave:'recuperar',fazendas:[]};
 assert.equal(G.sgCompor(FX.safs,pedido,ctx).ok,false);assert.deepEqual(ctx.rec,{});
 pedido.fazendas=['Santa Rita','Lagoa Grande'];const first=G.sgCompor(FX.safs,pedido,ctx);assert.equal(first.ok,true);
 ctx.novoId=()=>assert.fail('replay não deve gerar IDs');
 const again=G.sgCompor(first.safs,pedido,ctx);assert.equal(again.repetido,true);assert.deepEqual(again.safs,first.safs);assert.deepEqual(again.recibo,first.recibo);
});

test('C06 safras encerradas não editam nem enviam e não bloqueiam recibo das demais', () => {
 const closed=FX.safs.find(s=>s.ro);assert.equal(G.sgCompor(FX.safs,edit(closed.id,['Santa Rita']),context()).ok,false);
 const g=group();g.subs[0].ro=true;let calls=[];
 const sent=G.sgEnviar(g,'fechada',{},id=>{calls.push(id);return {ok:true,recibo:'SOL-'+id};});
 assert.deepEqual(calls,['B']);assert.equal(sent.ok,false);assert.equal(sent.parcial,true);assert.equal(sent.falhas[0].saf,'A');
});

test('C07 decimal e unidades preservam origem/destino sem transformar pendente em aprovado', () => {
 const info=copy(FX.leitura.uma_aprovada_outra_pendente);info.A.area_ha=0.1;info.B.area_ha=0.2;
 const before=copy(info),result=G.sgLeitura(freeze(group()),freeze(info));
 assert.equal(result.area.ha,0.3);assert.equal(result.parcial,true);assert.equal(result.estado,undefined);assert.equal(result.aprovado,undefined);
 assert.deepEqual(result.demanda.porInsumo.filter(x=>x.insumo==='Glifosato 480').map(x=>[x.un,x.qtd]),[['L',470.25],['kg',10]]);
 assert.deepEqual(result.demanda.linhas.filter(x=>x.un==='L').map(x=>[x.saf,x.talhao,x.ciclo,x.destino]),[['A','T1-A','c1','Almoxarifado Santa Rita'],['B','Pivô 19','p19','Almoxarifado Lagoa Grande']]);
 assert.deepEqual(info,before);
});

test('C08 zero conhecido difere de área ausente; demanda vazia difere de não calculada', () => {
 const result=G.sgLeitura(group(),{A:{area_ha:0,demanda:[]},B:{area_ha:null,demanda:null}});
 assert.equal(result.area.ha,0);assert.equal(result.area.completa,false);assert.deepEqual(result.area.faltam,['Lagoa Grande']);
 assert.deepEqual(result.demanda.incompleta,['Lagoa Grande']);assert.equal(result.fazendas[0].area_ha,0);assert.equal(result.fazendas[1].area_ha,null);
});

test('C09 exceção no segundo envio fica parcial; retry fora de ordem só tenta pendente', () => {
 const g=group(),rec={},calls=[];let fail=true;
 const send=id=>{calls.push(id);if(id==='B'&&fail)throw new Error('Falha sintética');return {ok:true,recibo:{id:'SOL-'+id}};};
 const first=G.sgEnviar(g,'lote',rec,send);assert.equal(first.ok,false);assert.equal(first.parcial,true);assert.equal(first.falhas[0].erro,'Falha sintética');
 fail=false;g.subs.reverse();const second=G.sgEnviar(g,'lote',rec,send);assert.equal(second.ok,true);assert.deepEqual(calls,['A','B','B']);
 assert.equal(second.recibos.find(x=>x.saf==='A').repetido,true);
 G.sgEnviar(g,'lote',rec,send);assert.deepEqual(calls,['A','B','B']);
});

test('C10 envio totalmente recusado não diz parcial nem consome recibos', () => {
 const rec={};const r=G.sgEnviar(group(),'recusado',rec,()=>({ok:false,erro:'Revalidar origem'}));
 assert.equal(r.ok,false);assert.equal(r.parcial,false);assert.deepEqual(r.recibos,[]);assert.equal(r.falhas.length,2);assert.deepEqual(rec,{});
});

test('C11 datas civis impossíveis são recusadas sem criar safra ou recibo', () => {
 const ctx=context();const result=G.sgCompor(FX.safs,{...FX.pedidos.duas_fazendas,ini:'2027-02-31'},ctx);
 assert.equal(result.ok,false,'31/02 não pode criar uma safra');assert.deepEqual(result.safs,FX.safs);assert.deepEqual(ctx.rec,{});
});

test('C12 área vazia não vira zero conhecido nem total completo', () => {
 const result=G.sgLeitura(group(),{A:{area_ha:160,demanda:[]},B:{area_ha:'',demanda:[]}});
 assert.equal(result.fazendas[1].area_ha,null);assert.equal(result.area.completa,false);assert.deepEqual(result.area.faltam,['Lagoa Grande']);
});

test('C13 quantidade desconhecida não desaparece numa demanda declarada completa', () => {
 const info=copy(FX.leitura.uma_aprovada_outra_pendente);info.B.demanda[0].qtd=null;
 const result=G.sgLeitura(group(),info);
 assert.ok(result.demanda.incompleta.includes('Lagoa Grande'),'quantidade ausente exige marcação de incompletude da fazenda');
});

console.log(`TOTAL ${passed+failed} · OK ${passed} · FALHAS ${failed}`);
process.exitCode=failed?1:0;
