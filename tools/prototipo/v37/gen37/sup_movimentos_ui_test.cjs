const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
let raw,fail=false,rows=[],actor={k:'Teste',nome:'Teste',papel:'almoxarife'};
const seed=()=>({v:1,lotes:{k:{prod:'MAP',lote:'L1',local:'Galpão',un:'kg',fisico:100,quarentena:10,reservado:20}},movs:[],ajustes:[],reqs:{},ordens:{}});
const ctx={CEN0:seed(),GRIDS:[{id:'g_mov'}],G2C:{gray:['',''],yellow:['','']},
 localStorage:{getItem:()=>raw,setItem:(_,x)=>{if(fail)throw Error('quota');raw=x;}},
 g2rows:()=>rows,g2num:Number,g2perfil:()=>actor,g2ator:a=>a&&a.nome,g2papel:(a,p)=>a&&a.papel===p,g2quem:()=> 'Gestor',g2alc:()=>({}),g2alcN:()=>({modo:'todos',papeis:'gestor'}),g2pf:()=>null};
vm.createContext(ctx);vm.runInContext(fs.readFileSync(__dirname+'/sup_movimentos_captured.js','utf8'),ctx);
const self={state:{},setState(p){Object.assign(this.state,p);}};
function values(){const v={};ctx.PREVALS(self,v);ctx.EXTRAVALS(self,v);return v;}
function reset(){raw=JSON.stringify(seed());rows=[];fail=false;self.state={};actor={k:'Teste',nome:'Teste',papel:'almoxarife'};}
let n=0;function test(name,fn){reset();fn();console.log('PASS '+name);n++;}
test('formulário real PN submete perda e reflete ajuste canônico',()=>{values().open_per();self.state.pd.q='20';self.state.pd.causa='dano';self.state.pd.ev='foto sintética';values().pn_ok();assert.equal(self.state.pn,null);assert.equal(JSON.parse(raw).ajustes.length,1);assert.equal(JSON.parse(raw).lotes.k.fisico,100);values();assert.equal(rows[0].v.st,'Aguardando gestor');});
test('falha de gravação mantém formulário e chave para retry',()=>{values().open_per();Object.assign(self.state.pd,{q:'20',causa:'dano',ev:'foto'});const key=self.state.supMovChave;fail=true;values().pn_ok();assert.equal(self.state.pn,'per');assert.equal(self.state.pd.causa,'dano');assert.equal(JSON.parse(raw).ajustes.length,0);fail=false;values().pn_ok();assert.equal(self.state.supMovChave,key);assert.equal(JSON.parse(raw).ajustes.length,1);});
test('aprovação exige AL09 e só fecha após sucesso',()=>{values().open_per();Object.assign(self.state.pd,{q:'20',causa:'dano',ev:'foto'});values().pn_ok();values().apr('AJ-71');values().pn_ok();assert.equal(self.state.pn,'aprovar');assert.equal(JSON.parse(raw).lotes.k.fisico,100);actor={k:'Gestor',nome:'Gestor',papel:'gestor'};values().pn_ok();assert.equal(self.state.pn,null);assert.equal(JSON.parse(raw).lotes.k.fisico,80);});
test('transferência é prévia, mantém estoque e extrato',()=>{values().open_trf();Object.assign(self.state.pd,{q:'10',d:'Galpão 2',mot:'teste'});const before=raw;values().pn_ok();assert.equal(raw,before);assert.match(self.state.g2toast,/Prévia/);assert.equal(rows.length,0);});
test('estorno genérico não muda original ou cria vínculo',()=>{const c=seed();c.movs.push({id:'MV-1',tipo:'ajuste',prod:'MAP',lote:'L1',qtd:5,un:'kg'});raw=JSON.stringify(c);values().open_est();self.state.pd.mot='teste';const before=raw;values().pn_ok();assert.equal(raw,before);assert.match(self.state.g2toast,/nenhum movimento ou vínculo criado/);});
console.log(n+' testes PN real, layout e storage simulados; sem navegador.');
