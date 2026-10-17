const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),path=require('node:path');
const source=fs.readFileSync(process.argv[2]||path.join(__dirname,'areas/analise_solo.py'),'utf8');
const begin=source.indexOf('const SO_UN='),end=source.indexOf('function soFazOk',begin);
const api=vm.runInNewContext(source.slice(begin,end)+';({SO_AN,SO_UN,soRlAnalito,soRlEnviarAnalitos,soRlErroAnalitos})');
const plain=x=>JSON.parse(JSON.stringify(x));
assert.equal(api.SO_AN.length,15);assert.equal(new Set(api.SO_AN).size,15);
const rows=api.SO_AN.map(a=>api.soRlAnalito(a));
assert.deepEqual(plain(api.soRlEnviarAnalitos(rows,'Mehlich-1')),[]);
for(const a of api.SO_AN){assert.equal(api.soRlAnalito(a).v,'');assert.ok(api.SO_UN[a].length);}
const z=api.soRlAnalito('Al',{v:0,un:'cmolc/dm³',met:'lab',ld:0,q:'<'});
assert.deepEqual(plain(api.soRlEnviarAnalitos([z],'Resina')),[{a:'Al',v:'0',un:'cmolc/dm³',met:'lab',ld:'0',q:'<'}]);
for(const a of ['P','K'])for(const ext of ['Mehlich-1','Resina'])assert.equal(api.soRlEnviarAnalitos([api.soRlAnalito(a,{v:3.1,un:'mg/dm³',met:'Outro método'})],ext)[0].met,ext);
for(const q of ['< LD','não detectado','abaixo do limite','>'])assert.throws(()=>api.soRlEnviarAnalitos([{a:'K',v:'1',q}],'Mehlich-1'),/selecione/);
for(const detail of [{met:'lab'},{ld:0},{q:'<'}])assert.match(api.soRlErroAnalitos([{a:'Al',v:'',...detail}]),/informe o valor/);
assert.equal(api.soRlErroAnalitos([{a:'K',v:'',met:'Mehlich-1'}]),''); // extrator é derivado, não detalhe editável
const before=JSON.stringify(rows);api.soRlEnviarAnalitos(rows,'Resina');assert.equal(JSON.stringify(rows),before);
// Domínio real: qualificador canônico impede usar K como resultado quantificado (não precisa de aritmética).
const solo=fs.readFileSync(process.argv[3]||path.join(__dirname,'solo.js'),'utf8');
const dom=vm.runInNewContext(solo+';({soloKmg})');
const k=api.soRlEnviarAnalitos([api.soRlAnalito('K',{v:1,un:'mg/dm³',q:'<'})],'Mehlich-1')[0];
assert.deepEqual(plain(dom.soloKmg(k)),{v:null,nc:'K abaixo do limite de detecção'});
// Handler real: recusa antes de cenMudar e preserva exatamente rascunho/abertura.
const h=source.slice(source.indexOf('v.rl_pgo=()=>'),source.indexOf("\n'''",source.indexOf('v.rl_pgo=()=>'))).replace(/; }\s*$/, ';');
let calls=0;const self={state:{rl:{faz:'F',tal:'T',an:[{a:'Al',v:'',ld:'0,1',q:'<'}]}},setState(p){Object.assign(this.state,p)}};
const old=self.state.rl;const v={};vm.runInNewContext(h,{v,self,SOLO_TAL:{},...api,cenMudar:()=>{calls++;throw Error('não deve gravar')}});
v.rl_pgo();assert.equal(calls,0);assert.deepEqual(self.state.rl.an,old.an);assert.match(self.state.rl.err,/Al: informe/);
assert.ok(source.includes('class="so-met-summary"'));assert.ok(source.includes('min-height:24px'));assert.ok(source.includes('min-height:44px'));assert.ok(source.includes('readOnly="{H("x.metfix")}"'));assert.ok(!source.includes('Ex.: abaixo do limite'));
console.log('PASS:15 analitos; zero/LD0; qualificador fechado e soloKmg real; extrator P/K; detalhes sem valor recusados pelo handler real; CSS/markup estáticos. Sem DOM/E2E.');
