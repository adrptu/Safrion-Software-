const fs=require('fs'); const [,,a,e,o]=process.argv;
const m=fs.readFileSync(a,'utf8').match(/\/\/ >>> REPARTIR[\s\S]*?\/\/ <<< REPARTIR/); const rep=new Function(m[0]+'\nreturn repartir;')();
const E=JSON.parse(fs.readFileSync(e,'utf8')); const O=E.map(x=>{const r=rep(x.Q,JSON.parse(JSON.stringify(x.cfgs)),x.pools||{}); return {q:r.itens.map(i=>i.q),h:r.itens.map(i=>i.h),alocado:r.alocado,saldo:r.saldo,conflito:r.conflito,deficit:r.deficit,motivos:r.motivos};});
fs.writeFileSync(o,JSON.stringify(O));
