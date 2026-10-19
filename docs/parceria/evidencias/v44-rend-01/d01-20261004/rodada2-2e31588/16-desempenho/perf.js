const fs=require('fs'); const [,,src,casos]=process.argv; const s=fs.readFileSync(src,'utf8'); const a=s.indexOf('// >>> REPARTIR'), b=s.indexOf('// <<< REPARTIR');
const repartir=new Function(s.slice(a,b)+'; return repartir;')(); const C=JSON.parse(fs.readFileSync(casos,'utf8'));
let mx=0, mxn='', mm=0, tot=0; const res=[];
C.forEach(c=>{ repartir(c.Q,c.cfgs,c.pools||{}); const t0=process.hrtime.bigint(); const r=repartir(c.Q,c.cfgs,c.pools||{}); const ms=Number(process.hrtime.bigint()-t0)/1e6; tot+=ms; if(ms>mx){mx=ms; mxn=c.nome;} if(r.motivos.length>mm) mm=r.motivos.length; res.push([r.alocado,r.conflito]); });
console.log(JSON.stringify({n:C.length,max_ms:Math.round(mx),caso:mxn.slice(0,60),med_ms:Math.round(tot/C.length),max_motivos:mm}));
