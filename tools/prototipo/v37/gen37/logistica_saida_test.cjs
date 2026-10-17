const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
let raw,fail=false,actor='Rui';
const seed=()=>({v:1,ordens:{},producao:{seq:{mp:1000},lotes:{L1:{id:'L1',prod:'Milho',cultura:'Milho',q0:'Liberado',local:'Silo',abertura:true,origem:[]}},pedidos:{PV1:{id:'PV1',prod:'Milho',cultura:'Milho',qtd:1000,natureza:'Venda',preco:'1',cond:'Antecipado',cred:{ant:true,quem:'Ana'},cliente:'Demo',modal:'retira'}},reservas:{R1:{id:'R1',pedido:'PV1',lote:'L1',kg:1000,st:'Ativa'}},expedicoes:{RM1:{id:'RM1',pedido:'PV1',st:'Programada',modal:'retira',lotes:[{lote:'L1',prev:1000}]}},movs:[{id:'M0',lote:'L1',kg:2000,tipo:'abertura'}]}});
const ctx={CEN0:seed(),PRDC:{hoje:'2026-10-17',un:{Milho:{prod:'Milho',un:'kg',massa:1}},locais:{Silo:{tipo:'silo'}},proc:[],cult:{}},COMC:{cond:[{t:'Antecipado',ant:true}],cp:{}},CARD:{},carAvaliar(){throw Error('Fixture só usa origem de abertura');},URLSearchParams,location:{hash:''},localStorage:{getItem:()=>raw,setItem:(_,s)=>{if(fail)throw Error('quota');raw=s;}},window:{},console,setTimeout:()=>0,clearTimeout(){}};
vm.createContext(ctx);
for(const f of ['g2lib.js','cenario.js','producao.js','comercial.js','logistica_saida_captured.js'])vm.runInContext(fs.readFileSync(__dirname+'/'+f,'utf8'),ctx);
ctx.g2perfil=()=>actor;ctx.cenRevisao=()=>'';ctx.prHoje=()=> '2026-10-17';
const self={state:{},setState(x){Object.assign(this.state,x);}};
function refresh(){const v={};ctx.PREVALS(self,v);ctx.EXTRAVALS(self,v);return v;}
function open(b='1200',t='200'){refresh().lo_revisar();const f=ctx.g2st(self,'g_ps').fm;f.draft.bruto=b;f.draft.tara=t;return f;}
function save(){ctx.g2save(self,ctx.GRIDS.find(g=>g.id==='g_ps'));}
function reset(){raw=JSON.stringify(seed());fail=false;actor='Rui';self.state={};self.loId=null;self.loHash=null;ctx.location.hash='';ctx.GRIDS.forEach(g=>g.rows=[]);}
let n=0;function test(name,fn){reset();fn();console.log('PASS '+name);n++;}
test('saída real baixa mil kg uma vez e gera recibo',()=>{open();save();const c=JSON.parse(raw);assert.equal(c.producao.expedicoes.RM1.st,'Entregue',self.state.g2toast);assert.equal(ctx.prFis(c,'L1'),1000);const k={...self.loPendente,ator:actor};const r=ctx.cenMudar(self,c=>ctx.comSair(c,k),{estrito:true});assert.equal(r.repetido,true);assert.equal(ctx.prFis(JSON.parse(raw),'L1'),1000);});
test('perfil Caio recusado com rascunho preservado',()=>{actor='Caio';open();const before=raw;save();assert.equal(raw,before);assert.ok(ctx.g2st(self,'g_ps').fm);});
test('falha de storage não baixa e mantém pesos para repetir',()=>{open();const before=raw;fail=true;save();assert.equal(raw,before);assert.equal(ctx.g2st(self,'g_ps').fm.draft.bruto,'1200');fail=false;save();assert.equal(ctx.prFis(JSON.parse(raw),'L1'),1000,self.state.g2toast);});
test('bruto/tara inválidos ficam no formulário',()=>{for(const [b,t] of [['','0'],['abc','0'],['100','100'],['100','-1']]){open(b,t);const before=raw;save();assert.equal(raw,before);assert.ok(Object.keys(ctx.g2st(self,'g_ps').fm.errs).length);}});
test('RM alterada depois da abertura bloqueia',()=>{open();const c=JSON.parse(raw);c.producao.expedicoes.RM1.lotes[0].prev=900;raw=JSON.stringify(c);refresh();const before=raw;save();assert.equal(raw,before);assert.match(self.state.g2toast,/carga mudou/);});
test('âncora inexistente não escolhe outra carga',()=>{ctx.location.hash='#rm=RM-inexistente';assert.equal(refresh().lo_id,'');assert.equal(ctx.g2rows(self,ctx.GRIDS[1]).length,0);});
test('sem programada não restaura cenário fictício',()=>{const c=JSON.parse(raw);c.producao.expedicoes={};raw=JSON.stringify(c);assert.equal(refresh().lo_estado,'Nenhuma carga programada');});
test('estado encerrado continua no mesmo detalhe após saída',()=>{open();save();assert.equal(refresh().lo_id,'RM1');assert.equal(refresh().lo_estado,'Entregue');assert.ok(ctx.g2rows(self,ctx.GRIDS[3]).length);});
test('dois lotes exigem soma igual ao líquido e baixam cada origem',()=>{const c=JSON.parse(raw),P=c.producao;P.lotes.L2={...P.lotes.L1,id:'L2'};P.movs.push({id:'M2',lote:'L2',kg:1000,tipo:'abertura'});P.reservas.R1.kg=600;P.reservas.R2={id:'R2',pedido:'PV1',lote:'L2',kg:400,st:'Ativa'};P.expedicoes.RM1.lotes=[{lote:'L1',prev:600},{lote:'L2',prev:400}];raw=JSON.stringify(c);const f=open();f.draft.kg_0='600';f.draft.kg_1='300';const before=raw;save();assert.equal(raw,before);assert.ok(ctx.g2st(self,'g_ps').fm.errs.bruto);ctx.g2st(self,'g_ps').fm.draft.kg_1='400';save();assert.equal(ctx.prFis(JSON.parse(raw),'L1'),1400,self.state.g2toast);assert.equal(ctx.prFis(JSON.parse(raw),'L2'),600);});
test('crédito sem pagamento antecipado recusa a saída',()=>{const c=JSON.parse(raw);delete c.producao.pedidos.PV1.cred;raw=JSON.stringify(c);open();const before=raw;save();assert.equal(raw,before);assert.match(self.state.g2toast,/crédito/);});
console.log(n+' testes G2/comSair/produção reais, fixture sintética de abertura; sem navegador.');

