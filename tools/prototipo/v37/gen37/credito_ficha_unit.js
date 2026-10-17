// CRE-BANCO F1: domínio real; somente localStorage/perfil/relógio são fronteiras sintéticas.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const c={localStorage:{data:{},getItem(k){return this.data[k]??null;},setItem(k,v){if(this.fail)throw Error('quota');this.data[k]=v;}},g2pf:p=>p==='Ana'||p==='Carlos'?{k:p,papeis:{direcao:'direção'}}:p==='Rui'?{k:p,papeis:{almoxarife:'almoxarife'}}:null};
vm.createContext(c);vm.runInContext(fs.readFileSync(process.argv[2]||__dirname+'/credito_docs.js','utf8'),c);
const run=s=>vm.runInContext(s,c);let ok=0,fail=0;
function test(n,f){try{c.localStorage.data={};c.localStorage.fail=false;f();ok++;console.log('OK '+n);}catch(e){fail++;console.log('FALHA '+n+': '+e.message);}}
const draft={nome:'Trator de demonstração',tipo:'Avaliação de mercado',valor:'850.000,00',data:'2026-03-10',responsavel:'Ana',fonte:'Laudo sintético 01',oper:'Atualizar declaração'};
c.d=draft;
const save=(d=draft,id='bem1',rev=0,p='Ana',h='2026-10-16')=>c.credFichaSalvar(id,d,rev,p,h);
test('ausência inicial não é valor zero',()=>assert.deepEqual(JSON.parse(JSON.stringify(c.credFichaLer())),{v:1,items:[]}));
test('R$850.000,00 mantém unidade e centavos após recarga',()=>{save();assert.equal(c.credFichaLer().items[0].valor,'850000.00');});
test('centavos e valor grande voltam exatos após salvar e reabrir',()=>{save({...draft,valor:'850000,50'});save({...draft,valor:'12.500.000,00'},'bem2');assert.equal(c.credFichaLer().items[0].valor,'850000.50');assert.equal(c.credFichaLer().items[1].valor,'12500000.00');});
test('zero explícito é declaração, vazio fica pendente',()=>{save({...draft,valor:'0'});assert.equal(c.credFichaLer().items[0].valor,'0.00');save({...draft,valor:'',data:'',fonte:'',responsavel:''},'bem2');assert.equal(c.credFichaLer().items[1].valor,null);});
test('confirmação Carlos preserva declaração original Ana 10/03',()=>{save();save({oper:'Confirmar vigência'},'bem1',1,'Carlos');let x=c.credFichaLer().items[0];assert.equal(x.data,'2026-03-10');assert.equal(x.responsavel,'Ana');assert.equal(x.fonte,draft.fonte);assert.deepEqual(JSON.parse(JSON.stringify(x.confirmacoes)),[{quem:'Carlos',quando:'2026-10-16'}]);});
test('atualização mantém declaração e confirmações anteriores',()=>{save();save({oper:'Confirmar vigência'},'bem1',1,'Carlos');save({...draft,valor:'900000',data:'2026-10-16'},'bem1',2);let x=c.credFichaLer().items[0];assert.equal(x.valor,'900000.00');assert.equal(x.historico[0].valor,'850000.00');assert.equal(x.historico[0].confirmacoes[0].quem,'Carlos');assert.equal(x.confirmacoes.length,0);});
test('repetir confirmação no mesmo dia não duplica recibo',()=>{save();save({oper:'Confirmar vigência'},'bem1',1);save({oper:'Confirmar vigência'},'bem1',2);assert.equal(c.credFichaLer().items[0].rev,2);});
test('dado pendente não aceita confirmação',()=>{save({...draft,valor:'',data:'',fonte:'',responsavel:''});assert.throws(()=>save({oper:'Confirmar vigência'},'bem1',1),/pendente/i);});
test('valor sem origem ou responsável é recusado',()=>{assert.throws(()=>save({...draft,fonte:''}),/fonte/i);assert.throws(()=>save({...draft,responsavel:''}),/responsável/i);});
test('decimal ambíguo, negativo, não finito e centavo excedente são recusados',()=>{for(let valor of ['850000.00','-1','Infinity','1,001','12abc','90071992547409,92'])assert.throws(()=>save({...draft,valor}),/valor/i);});
test('datas impossíveis ou futuras são recusadas',()=>{for(let data of ['2026-02-30','2026-10-17'])assert.throws(()=>save({...draft,data}),/data/i);});
test('conflito de revisão preserva edição mais nova',()=>{save();save({...draft,valor:'900000'},'bem1',1);assert.throws(()=>save({...draft,valor:'1'},'bem1',1),/edição/i);assert.equal(c.credFichaLer().items[0].valor,'900000.00');});
test('salvar outro item preserva alterações concorrentes',()=>{save();save({...draft,nome:'Outro'},'bem2');save({...draft,valor:'2'},'bem1',1);assert.equal(c.credFichaLer().items.length,2);});
test('quota não confirma nem altera versão anterior',()=>{save();let before=JSON.stringify(c.localStorage.data);c.localStorage.fail=true;assert.throws(()=>save({...draft,valor:'1'},'bem1',1),/gravar/i);assert.equal(JSON.stringify(c.localStorage.data),before);});
test('armazenamento corrompido não é substituído por vazio',()=>{run("localStorage.setItem(CRED_FICHA_KEY,'{quebrado')");assert.throws(()=>save(),/ler/i);assert.equal(run('localStorage.getItem(CRED_FICHA_KEY)'),'{quebrado');});
test('perfil inexistente ou sem papel não grava',()=>{assert.throws(()=>save(draft,'bem1',0,'Rui'),/perfil/i);assert.throws(()=>save(draft,'bem1',0,{k:'Rui',papeis:{gestor:true}}),/perfil/i);assert.equal(c.credFichaLer().items.length,0);});
test('schema desconhecido não é apagado',()=>{run("localStorage.setItem(CRED_FICHA_KEY,JSON.stringify({v:9,items:[]}))");assert.throws(()=>save(),/ler/i);});
test('IDs duplicados falham fechados sem apagar dados',()=>{save();run("const db=credFichaLer(); db.items.push(db.items[0]); localStorage.setItem(CRED_FICHA_KEY,JSON.stringify(db));");let old=JSON.stringify(c.localStorage.data);assert.throws(()=>save(),/ler/i);assert.equal(JSON.stringify(c.localStorage.data),old);});
console.log(`RESULTADO ${ok}/${ok+fail}`);process.exitCode=fail?1:0;
