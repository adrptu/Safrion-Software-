// uso: node run_lote.js <raiz> <entradas.json> [ini] [fim] → JSONL compacto (uma execução instrumentada por entrada, com tempo)
const {carrega,caminho}=require('./lib.js'); const fs=require('fs');
const [,,raiz,arq,iniS,fimS]=process.argv; const f=carrega(raiz,true); const L=JSON.parse(fs.readFileSync(arq,'utf8'));
const ini=+(iniS||0), fim=fimS?+fimS:L.length;
for(let k=ini;k<fim;k++){ const c=L[k]; globalThis.__BL=[]; const t0=process.hrtime.bigint(); const r=f(c.Q,c.cfgs,c.pools||{}); const ms=Number(process.hrtime.bigint()-t0)/1e6;
  console.log(JSON.stringify({k,nome:c.nome,alocado:r.alocado,saldo:r.saldo,deficit:r.deficit,conflito:r.conflito,pendente:r.pendente,q:r.itens.map(x=>x.q),motivos:r.motivos,caminho:caminho(r.motivos),bl:globalThis.__BL,ms:+ms.toFixed(2)})); }
