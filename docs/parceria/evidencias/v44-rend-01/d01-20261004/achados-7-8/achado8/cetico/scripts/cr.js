// cético: node cr.js <safra.js> <entradas.json> -> JSON {caso:{q,h,alocado,saldo,conflito,deficit,decorrido,motivos}}
const fs=require('fs'); const [,,a,e]=process.argv;
const src=fs.readFileSync(a,'utf8'); const m=src.match(/\/\/ >>> REPARTIR[\s\S]*?\/\/ <<< REPARTIR/);
const rep=new Function(m[0]+'\nreturn repartir;')(); const E=JSON.parse(fs.readFileSync(e,'utf8')); const O={};
for(const k of Object.keys(E)){ const x=E[k]; const r=rep(x.Q,JSON.parse(JSON.stringify(x.cfgs)),x.pools||{});
 O[k]={q:r.itens.map(i=>i.q),h:r.itens.map(i=>i.h),alocado:r.alocado,saldo:r.saldo,conflito:r.conflito,deficit:r.deficit,decorrido:r.decorrido,motivos:r.motivos}; }
console.log(JSON.stringify(O));
