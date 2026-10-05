const fs=require('fs');
const [,,ROOT,CASES,OUTP]=process.argv;
function block(dir){ const s=fs.readFileSync(dir+'/tools/prototipo/v37/gen37/safra.js','utf8'); return s.match(/\/\/ >>> REPARTIR[\s\S]*?\/\/ <<< REPARTIR/)[0]; }
const mk=(b)=>new Function(b+'\nreturn repartir;')();
const bn=block(ROOT+'/new'), bo=block(ROOT+'/old'), bp=block(ROOT+'/pre');
function rep(b,a,c){ if(b.indexOf(a)<0) throw new Error('patch miss: '+a); return b.split(a).join(c); }
const R22a='const cf0=comp.filter(i=>isFinite(V[i].H));', R23a='gs.filter(g=>!SUB[g]).concat(gs.filter(g=>SUB[g]))';
const V={new:mk(bn),old:mk(bo),pre:mk(bp),
  noR22:mk(rep(bn,R22a,'const cf0=comp;')),
  noR23:mk(rep(bn,R23a,'gs')),
  noR2223:mk(rep(rep(bn,R22a,'const cf0=comp;'),R23a,'gs'))};
const cases=JSON.parse(fs.readFileSync(CASES,'utf8'));
const sel=(r)=>({alocado:r.alocado,saldo:r.saldo,pendente:r.pendente,causa:r.causa,conflito:r.conflito,conflitoEst:r.conflitoEst,deficit:r.deficit,decorrido:r.decorrido,troca:r.troca,
  motivos:r.motivos,q:r.itens.map(x=>x.q),h:r.itens.map(x=>x.h),ht:r.itens.map(x=>x.ht),emSeq:r.itens.map(x=>x.emSeq),seqEst:r.itens.map(x=>x.seqEst),fq:r.itens.map(x=>x.fq),nec:r.nec,falta:r.falta});
const out={}; const t0=Date.now();
for(const k of Object.keys(V)){ out[k]=cases.map(c=>{ try{ return sel(V[k](c.Q,c.cfgs,c.pools)); }catch(e){ return {erro:String(e)}; } }); }
fs.writeFileSync(OUTP,JSON.stringify(out)); console.log('ok',cases.length,'ms',Date.now()-t0);
