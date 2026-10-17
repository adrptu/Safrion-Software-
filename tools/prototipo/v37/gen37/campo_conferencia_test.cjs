const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
let raw,fail=false,allowed=true;
const seed=()=>({v:1,ordens:{'OS-1':{id:'OS-1',versao:2,etapa:'Em execução',area:100,realizado:10,saldo:90,ins:[{p:'MAP',un:'kg'}],ap:[{dia:1,d:'17/10',ha:10,h:2,st:'Provisório',sinc:true,quem:'Operador',origem:'app',cons:{MAP:5}}]}},confs:[],lotes:{},movs:[],reqs:{}});
const ctx={CEN0:seed(),localStorage:{getItem:()=>raw,setItem:(_,x)=>{if(fail)throw Error('quota');raw=x;}},window:{},console,setTimeout:()=>0,clearTimeout(){}};
vm.createContext(ctx);vm.runInContext(fs.readFileSync(__dirname+'/g2lib.js','utf8'),ctx);
vm.runInContext(fs.readFileSync(__dirname+'/campo_conferencia_captured.js','utf8'),ctx);
ctx.g2perfil=()=>({k:'Paula'});ctx.cenExigeAlc=()=>{if(!allowed)throw Error('AL-12 recusada');return 'Paula';};ctx.cenRevisao=()=>'';
const self={state:{},setState(p){Object.assign(this.state,p);}};
function refresh(){const v={};ctx.PREVALS(self,v);ctx.EXTRAVALS(self,v);return v;}
function open(dec='Conferir dia',mot=''){refresh().ca_revisar('OS-1:1');const fm=ctx.g2st(self,'g_fila').fm;fm.draft.decisao=dec;fm.draft.motivo=mot;return fm;}
function save(){ctx.g2save(self,ctx.GRIDS[0]);}
function reset(){raw=JSON.stringify(seed());self.state={};fail=false;allowed=true;ctx.GRIDS[0].rows=[];}
let n=0;function test(name,fn){reset();fn();console.log('PASS '+name);n++;}
test('g2open/save real confere sem repetir efeito físico',()=>{open();save();const c=JSON.parse(raw);assert.equal(c.ordens['OS-1'].ap[0].st,'Conferido');assert.equal(c.ordens['OS-1'].realizado,10);assert.equal(c.ordens['OS-1'].saldo,90);assert.equal(c.movs.length,0);assert.equal(c.ordens['OS-1'].ap[0].cons.MAP,5);});
test('falha de gravação conserva formulário e motivo',()=>{open('Registrar divergência','dado divergente');const before=raw;fail=true;save();assert.equal(raw,before);assert.equal(ctx.g2st(self,'g_fila').fm.draft.motivo,'dado divergente');fail=false;save();assert.ok(JSON.parse(raw).ordens['OS-1'].ap[0].conferenciaDia.caso);});
test('referência da abertura recusa fato alterado mesmo após refresh',()=>{open('Registrar divergência','dado divergente');const c=JSON.parse(raw);c.ordens['OS-1'].versao++;raw=JSON.stringify(c);refresh();const before=raw;save();assert.equal(raw,before);assert.ok(ctx.g2st(self,'g_fila').fm);});
test('divergência e vínculo usam o caso oficial sem refazer consumo',()=>{open('Registrar divergência','foto pendente');save();assert.equal(JSON.parse(raw).ordens['OS-1'].ap[0].conferenciaDia.estado,'Não conforme');open('Vincular evidência','foto confirma relato');save();const a=JSON.parse(raw).ordens['OS-1'].ap[0];assert.equal(a.conferenciaDia.estado,'Conferido');assert.equal(a.conferenciaDia.caso.estado,'Vinculado');assert.equal(a.cons.MAP,5);});
test('AL12 negada não grava',()=>{open();allowed=false;const before=raw;save();assert.equal(raw,before);assert.ok(ctx.g2st(self,'g_fila').fm);});
test('divergência sem motivo fica no campo',()=>{open('Registrar divergência');save();assert.ok(ctx.g2st(self,'g_fila').fm.errs.motivo);assert.equal(JSON.parse(raw).ordens['OS-1'].ap[0].conferenciaDia,undefined);});
test('offline é somente leitura e quantidade não tem edição',()=>{const c=JSON.parse(raw);c.ordens['OS-1'].ap[0].sinc=false;raw=JSON.stringify(c);open();assert.equal(ctx.g2st(self,'g_fila').fm.ro,true);assert.equal(ctx.GRIDS[0].edit.fields.find(f=>f.k==='real').ro,true);});
console.log(n+' testes: G2 e comandos reais; perfil/storage simulados, sem UI/browser.');
