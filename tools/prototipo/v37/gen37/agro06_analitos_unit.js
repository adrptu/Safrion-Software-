// AGRO-06: pure entry/serialization helpers from the real screen; no domain mocks.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),path=require('node:path');
const source=fs.readFileSync(process.argv[2]||path.join(__dirname,'areas/analise_solo.py'),'utf8');
const begin=source.indexOf('const SO_UN='),end=source.indexOf('function soFazOk',begin);
const api=vm.runInNewContext(source.slice(begin,end)+';({SO_AN,SO_UN,soRlAnalito,soRlEnviarAnalitos})');
const plain=x=>JSON.parse(JSON.stringify(x));
assert.equal(api.SO_AN.length,15);assert.equal(new Set(api.SO_AN).size,15);
for(const name of ['pH','P','MO','Ca','Mg','K','H+Al','Al','S','B','Cu','Fe','Mn','Zn','Argila']){
 const x=api.soRlAnalito(name);assert.equal(x.v,'');assert.ok(api.SO_UN[name].includes(x.un));
}
const rows=api.SO_AN.map(a=>api.soRlAnalito(a));
assert.deepEqual(plain(api.soRlEnviarAnalitos(rows,'Mehlich-1')),[]);
const zero=api.soRlAnalito('Al',{v:0,un:'cmolc/dm³',met:'lab',ld:'0',q:'não detectado'});
assert.deepEqual(plain(api.soRlEnviarAnalitos([zero],'Resina')),[{a:'Al',v:'0',un:'cmolc/dm³',met:'lab',ld:'0',q:'não detectado'}]);
const p=api.soRlAnalito('P',{v:3.1,un:'mg/dm³',met:'Outro método',ld:'1',q:'< LD'});
assert.equal(p.v,'3,1');assert.equal(api.soRlEnviarAnalitos([p],'Resina')[0].met,'Outro método');
assert.equal(api.soRlEnviarAnalitos([{a:'P',v:'2',un:'mg/dm³'}],'Resina')[0].met,'Resina');
assert.equal(api.soRlEnviarAnalitos([{a:'K',v:'4',un:'mg/dm³'}],'Mehlich-1')[0].met,'Mehlich-1');
assert.equal(api.soRlEnviarAnalitos([{a:'MO',v:'4',un:'g/dm³'}],'Resina')[0].met,'');
assert.deepEqual(plain(api.soRlEnviarAnalitos([{a:'P',v:' ',un:'mg/dm³',met:'foo'}],'Resina')),[]);
assert.equal(api.soRlEnviarAnalitos([{a:'P',v:'inválido',un:'mg/dm³'}],'Resina')[0].v,'inválido'); // domain must reject, UI must not silently discard
const before=JSON.stringify(rows);api.soRlEnviarAnalitos(rows,'Resina');assert.equal(JSON.stringify(rows),before);
console.log('PASS: 15 analitos, ausentes/zero, decimal, unidades e metadados, extrator P/K, inválido preservado para validação; sem DOM/E2E');
