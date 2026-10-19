// uso: node run_js.js <raiz_da_cópia> <entradas.json> [reps]  → uma linha JSON por caso (resumo, chamadas do buraco, tempos em ms)
const {carrega,resumo}=require('./lib.js'); const fs=require('fs');
const [,,raiz,arq,repsS]=process.argv; const reps=+(repsS||3);
const fI=carrega(raiz,true), f=carrega(raiz,false); const casos=JSON.parse(fs.readFileSync(arq,'utf8'));
for(const c of casos){ globalThis.__BL=[]; const r=fI(c.Q,c.cfgs,c.pools||{}); const bl=globalThis.__BL.map(z=>({grafo:z[0],n:z[1],buraco:z[2],passos:z[3]}));
  const ms=[]; let r2; for(let k=0;k<reps;k++){ const t0=process.hrtime.bigint(); r2=f(c.Q,c.cfgs,c.pools||{}); ms.push(Number(process.hrtime.bigint()-t0)/1e6); }
  const a=resumo(r), b=resumo(r2); if(JSON.stringify(a)!==JSON.stringify(b)) throw new Error('instrumentado difere do normal: '+c.nome);
  console.log(JSON.stringify(Object.assign({nome:c.nome,n:c.cfgs.length},a,{buraco:bl,ms:ms.map(x=>+x.toFixed(2))}))); }
