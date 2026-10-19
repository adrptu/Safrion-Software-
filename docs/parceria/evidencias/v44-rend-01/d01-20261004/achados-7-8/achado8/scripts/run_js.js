// uso: node run_js.js <safra.js> <entradas.json> [saida.json] — roda o bloco REPARTIR real (extraído do arquivo) em cada entrada
const fs=require('fs');
const [,,arq,ent,sai]=process.argv;
const bloco=fs.readFileSync(arq,'utf8').match(/\/\/ >>> REPARTIR[\s\S]*?\/\/ <<< REPARTIR/)[0];
const repartir=new Function(bloco+'\nreturn repartir;')();
const E=JSON.parse(fs.readFileSync(ent,'utf8'));
const ks=Array.isArray(E)?E.map((_,i)=>i):Object.keys(E);
const OUT={}; let tmax=0, tk=null;
for(const k of ks){ const e=E[k];
  const t0=process.hrtime.bigint(); const r=repartir(e.Q,e.cfgs,e.pools||{}); const ms=Number(process.hrtime.bigint()-t0)/1e6;
  if(ms>tmax){ tmax=ms; tk=k; }
  OUT[k]={alocado:r.alocado,saldo:r.saldo,conflito:r.conflito,deficit:r.deficit,decorrido:r.decorrido,motivos:r.motivos,q:r.itens.map(x=>x.q),h:r.itens.map(x=>x.h),ms}; }
const s=JSON.stringify({arquivo:arq,tmax_ms:tmax,tmax_caso:tk,res:OUT});
if(sai) fs.writeFileSync(sai,s); else console.log(s);
