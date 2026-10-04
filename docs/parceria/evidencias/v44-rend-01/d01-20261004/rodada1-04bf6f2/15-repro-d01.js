// reprodução do D-01 (issue 1, 5983640246): bloco REPARTIR exato de um safra.js
const fs=require('fs'); const f=process.argv[2];
const src=fs.readFileSync(f,'utf8'); const m=src.match(/\/\/ >>> REPARTIR[\s\S]*?\/\/ <<< REPARTIR/);
const repartir=new Function(m[0]+'\nreturn repartir;')();
const base=[{id:'A',nome:'A',rend:1,custo_h:1,jan:10,part:25,ativos:['ab','ac','ad']},{id:'B',nome:'B',rend:1,custo_h:1,jan:10,part:25,ativos:['ab','bc','bd']},
  {id:'C',nome:'C',rend:1,custo_h:1,jan:10,part:25,ativos:['ac','bc','cd']},{id:'D',nome:'D',rend:1,custo_h:1,jan:100,part:25,ativos:['ad','bd','cd']}];
const sem=base.map(x=>x.id==='D'?Object.assign({},x,{jan:''}):x);
for(const [nome,c] of [['D com 100 h',base],['D sem janela',sem]]){ const r=repartir(16,c,null);
  const hABC=r.itens.slice(0,3).reduce((s,x)=>s+x.h,0);
  console.log(nome,JSON.stringify({alocado:+r.alocado.toFixed(6),saldo:+r.saldo.toFixed(6),conflito:r.conflito,deficit:+r.deficit.toFixed(6),hABC:+hABC.toFixed(6),q:r.itens.map(x=>+x.q.toFixed(6)),motivos:r.motivos})); }
