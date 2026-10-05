// uso: node cx_run.js <safra.js> <entrada.json> [reps] [idx_ini idx_fim]  -> JSONL na saída
const fs=require('fs');
const [,,SJ,IN,REPS,I0,I1]=process.argv; const reps=Number(REPS||1);
const src=fs.readFileSync(SJ,'utf8'); const m=src.match(/\/\/ >>> REPARTIR[\s\S]*?\/\/ <<< REPARTIR/);
const repartir=new Function(m[0]+'\nreturn repartir;')();
const casos=JSON.parse(fs.readFileSync(IN,'utf8'));
const a=Number(I0||0), b=Number(I1||casos.length);
for(let i=a;i<Math.min(b,casos.length);i++){ const c=casos[i]; const ts=[]; let r;
  for(let k=0;k<reps;k++){ const t0=process.hrtime.bigint(); r=repartir(c.Q,JSON.parse(JSON.stringify(c.cfgs)),c.pools||{}); ts.push(Number(process.hrtime.bigint()-t0)/1e6); }
  const mot=r.motivos; const est=mot.some(s=>s.indexOf('combinações demais para conferir quem trabalha')>=0); const cic=mot.some(s=>s.indexOf('máquinas compartilhadas em ciclo')>=0);
  console.log(JSON.stringify({i,nome:c.nome,cat:c.cat,alocado:r.alocado,saldo:r.saldo,deficit:r.deficit,conflito:r.conflito,q:r.itens.map(x=>x.q),est,cic,ms:ts,motivos:mot,decorrido:r.decorrido}));
}
