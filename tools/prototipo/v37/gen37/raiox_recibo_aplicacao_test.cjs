'use strict';
const fs=require('fs'),vm=require('vm'),assert=require('node:assert/strict');
const src=fs.readFileSync(process.argv[2]||__dirname+'/cenario.js','utf8');
function fn(name){const at=src.indexOf('function '+name+'(');assert(at>=0);const next=src.indexOf('\nfunction ',at+1);return src.slice(at,next<0?src.length:next);}
const ctx=vm.createContext({Date:class extends Date{constructor(x){super(x===undefined?'2026-10-19T18:25:00.000Z':x)}},Intl,
 cenClone:x=>JSON.parse(JSON.stringify(x)),cenNum:String,cenAgora:()=> '15:25',cenOnline:c=>c.online,
 cenQtdTrecho:(d,ant,ha)=>d*ha,cenApDiv:()=>[],cenApDup:()=>[],
 cenApBaixa:(c,o,a)=>{delete a.cons.Zero;return[];},cenApEntra:(c,o,a)=>({ap:a,ks:[],dup:[]})});
vm.runInContext(fn('cenApImp')+'\n'+fn('cenApontar')+'\n'+fn('cenReciboAplicacao'),ctx);
const run=(name,...args)=>ctx[name](...args);
function setup(){const o={id:'OS-X',versao:'v3',talhao:'T1',etapa:'Em execução',saldo:10,ap:[],ins:[],req:'R'};
return {online:false,ordens:{'OS-X':o},reqs:{R:{itens:[{prod:'P',lote:'L1',un:'L',custodia:10}]}},
app:{fila:[],turno:{os:'OS-X',chave:'TU-X',inicioISO:'2026-10-19T17:25:00.000Z',fuso:'America/Sao_Paulo'}}};}
const input={os:'OS-X',d:'19/10',ha:2,cons:{P:1,Zero:0},origem:'app',quem:'Operador DEMO',chave:'TU-X'};
let c=setup(),a=run('cenApontar',c,input).ap,r=a.reciboAplicacao;
assert.equal(r.tempo.precisao,'instante');assert.equal(r.tempo.fim,'2026-10-19T18:25:00.000Z');
assert.equal(r.tempo.inicio,'2026-10-19T17:25:00.000Z');assert.equal(a.sinc,false);assert.equal(a.st,'Provisório');
assert.equal(r.tipo,'relato_aplicacao');assert(!('execucaoConfirmada'in r));assert.equal(r.versaoOS,'v3');
assert.equal(r.produtos.find(p=>p.produto==='Zero').quantidade,0);assert(!('Zero'in a.cons));
assert.equal(r.produtos[0].lote,'L1');
const saved=JSON.stringify(r);c.app.turno.inicioISO='2026-10-19T18:00:00.000Z';
assert.equal(run('cenApontar',c,input).repetido,true);assert.equal(JSON.stringify(a.reciboAplicacao),saved);
assert.equal(c.app.fila.length,1);assert.throws(()=>run('cenApontar',c,{...input,ha:3}),/conflito/);
const copy=run('cenReciboAplicacao',c,c.ordens['OS-X'],a);copy.produtos[0].quantidade=99;assert.equal(JSON.stringify(r),saved);
for(const change of [t=>{delete t.inicioISO;t.ini='14:25'},t=>t.inicioISO='2026-10-20T00:00:00.000Z',
 t=>t.inicioISO='2026-02-30T00:00:00.000Z',t=>t.fuso='Invalid/Zone',t=>t.chave='OUTRA',t=>t.os='OUTRA']){
 c=setup();change(c.app.turno);r=run('cenApontar',c,input).ap.reciboAplicacao;
 assert.equal(r.tempo.precisao,'incompleta');assert.equal(r.tempo.inicio,null);assert.equal(r.tempo.fim,null);
}
c=setup();r=run('cenApontar',c,{...input,origem:'web'}).ap.reciboAplicacao;
assert.equal(r.tempo.precisao,'incompleta');assert.equal(r.tempo.dataInformada,'19/10');assert(!r.tempo.de);
c=setup();c.reqs.R.itens.push({prod:'P',lote:'L2',un:'L',custodia:10});
r=run('cenApontar',c,input).ap.reciboAplicacao;
assert.equal(r.produtos[0].lote,null);assert.equal(r.produtos[0].atribuicaoLote,'nao_demonstrada');
assert.equal(r.produtos[0].quantidade,1);assert.equal(r.produtos[0].lotesCandidatos.length,2);
c=setup();c.reqs.R.itens[0].lote='—';r=run('cenApontar',c,input).ap.reciboAplicacao;assert.equal(r.produtos[0].lote,null);
c=setup();c.ordens['OS-X'].etapa='Liberada';assert.throws(()=>run('cenApontar',c,input),/execução/);
assert.equal(c.ordens['OS-X'].ap.length,0);
assert.equal(JSON.stringify(JSON.parse(saved)),saved);
assert.equal(run('cenReciboAplicacao',setup(),{id:'OS-X'},{d:'01/01'}),null);
console.log('PASS recibo: relógio, legado/manual, offline, idempotência, cópia, lotes ambíguos e O.S. liberada');
