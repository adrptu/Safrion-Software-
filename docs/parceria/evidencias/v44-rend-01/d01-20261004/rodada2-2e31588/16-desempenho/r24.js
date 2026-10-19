const fs=require('fs'); const [,,src]=process.argv; const s=fs.readFileSync(src,'utf8'); const a=s.indexOf('// >>> REPARTIR'), b=s.indexOf('// <<< REPARTIR');
const repartir=new Function(s.slice(a,b)+'; return repartir;')();
const P=[2,3,2,1,2,1,3,2,2,1,1,2,4]; const pa=[]; P.forEach((n,k)=>{ for(let j=0;j<n;j++) pa.push(k); });
const cs=pa.map((p,a)=>{ const at=[]; pa.forEach((q,b)=>{ if(b!==a&&q!==p) at.push('e'+Math.min(a,b)+'_'+Math.max(a,b)); }); return {id:'K'+a,nome:'K'+a,rend:1+(a%5),jan:2+((a*7)%19),part:(a%3===0)?2:'',troca:(a%4)*0.5,ativos:at,custo_h:1}; });
const t0=Date.now(); const r=repartir(400,cs); console.log(JSON.stringify([r.motivos.length,Date.now()-t0,r.alocado,r.conflito]));
