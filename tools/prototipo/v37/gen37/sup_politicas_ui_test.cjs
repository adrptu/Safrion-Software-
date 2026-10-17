const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
let raw=null,fail=false;const storage={getItem:()=>raw,setItem(k,v){if(fail)throw Error('quota');raw=v;}};
const c=vm.createContext({localStorage:storage,window:{},console,setTimeout:()=>0,clearTimeout(){}});
vm.runInContext(fs.readFileSync(__dirname+'/g2lib.js','utf8'),c);
vm.runInContext(fs.readFileSync(__dirname+'/sup_politicas_captured.js','utf8')+`\nvar GRIDS=[{id:'g_pol',rows:Object.entries(SUP_POL_SEED.politicas).map(([id,p])=>({id,v:JSON.parse(JSON.stringify(p.vigente)),p:{},s:{}})),cols:[],edit:{fields:['seg','prazo','lim','just'].map(k=>({k,l:k,t:k==='just'?'txt':'num',req:true}))}}];`,c);
const self={state:{},setState(p){Object.assign(this.state,p);}};let v={};c.PREVALS(self,v);c.EXTRAVALS(self,v);
function edit(){const r=c.RW(self,'g_pol')[0],orig=Object.fromEntries(Object.entries(r.v).map(([k,v])=>[k,String(v)]));c.g2set(self,'g_pol',{fm:{rid:r.id,isNew:false,orig,draft:{...orig,seg:'20',just:'Contraprova'}}});}
edit();c.g2save(self,c.GRIDS[0]);assert.equal(JSON.parse(raw).politicas.p1.vigente.seg,7);assert.equal(JSON.parse(raw).politicas.p1.proposta.dados.seg,20);console.log('PASS g2save real salva proposta e preserva vigente');
c.PREVALS(self,v);edit();const before=raw;fail=true;c.g2save(self,c.GRIDS[0]);assert.equal(raw,before);assert.ok(c.g2st(self,'g_pol').fm);assert.equal(c.g2st(self,'g_pol').fm.draft.just,'Contraprova');console.log('PASS falha real g2persist restaura formulário e rascunho');
fail=false;c.PREVALS(self,v);c.EXTRAVALS(self,v);v.pol_aprovar('p1');c.EXTRAVALS(self,v);v.pn_ok();assert.equal(JSON.parse(raw).politicas.p1.proposta.estado,'Aprovada');assert.equal(JSON.parse(raw).politicas.p1.vigente.seg,7);console.log('PASS painel de aprovação não publica');
c.PREVALS(self,v);c.EXTRAVALS(self,v);v.pol_publicar('p1');c.EXTRAVALS(self,v);const beforePub=raw;fail=true;v.pn_ok();assert.equal(raw,beforePub);assert.equal(self.state.pn,'publicar');assert.ok(self.state.pe.id);console.log('PASS falha na publicação mantém painel e estado');
fail=false;v.pn_ok();assert.equal(JSON.parse(raw).politicas.p1.vigente.seg,20);assert.equal(JSON.parse(raw).politicas.p1.recibos.length,1);console.log('PASS publicação após recuperação gera um recibo');
