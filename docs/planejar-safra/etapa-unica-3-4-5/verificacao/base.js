const L=require('./cap2.js'); const {X,mk,nf,fmtOcup}=L;
function rel(saf,mod,lbl){ const s=mk(saf,5); if(mod) mod(s); X.PREVALS(s,{}); const cs=L.capSaf(s,saf); const v=L.veredito(s,saf,cs);
  console.log('\n=====',saf,lbl||'','| outras:',cs.outs.join(',')||'—');
  console.log('VEREDITO',v.R,v.cor,'|',v.txt,'| área plano',v.aPlano,'de',v.aTot,'| janelas',JSON.stringify(v.jn));
  Object.values(cs.G).forEach(g=>{ const cells=g.cells.map(c=>{ if(c.d<=1e-4) return c.mes+' —'; return c.mes+' '+(c.ocup===null?'n/c':nf(c.ocup,2)+'%')+(c.red?' VERM precisa '+c.nec:'')+' [nec '+c.nec+' '+nf(c.dThis,2)+(c.dOth>1e-4?'+'+nf(c.dOth,2)+'oth':'')+'h/'+nf(c.cap,2)+(c.own?'':' só outra')+(c.ge?' ≥':'')+']'; });
    console.log(' '+g.nome+' un '+g.un+' | maior uso '+(g.max?nf(g.max.ocup,2)+'% '+g.max.mes+' ('+fmtOcup(g.max.ocup)+')':'—')+' | reds '+g.reds.map(c=>c.mes+':'+c.nec).join(',')+' | horas safra '+nf(g.horasSafra,2)+' (atendidas '+nf(g.horasSafraAt,2)+')\n    '+cells.join(' | ')); });
  const all=Object.values(cs.G).map(g=>g.max).filter(Boolean); const mx=Object.values(cs.G).filter(g=>g.max).sort((a,b)=>b.max.ocup-a.max.ocup)[0]; if(mx) console.log('MAIOR USO GERAL',mx.nome,nf(mx.max.ocup,2),mx.max.mes);
  const t=L.totais(s,saf,cs.oc); const f=(o)=>`n ${o.n} ha ${nf(o.ha,2)} h ${nf(o.h,2)} cop ${nf(o.cop,2)} cins ${nf(o.cins,2)} hh ${nf(o.hh,2)} diesel ${nf(o.diesel,2)} pend ${o.pend} saldo ${nf(o.saldo,2)} falta ${nf(o.falta,2)} semDiesel ${o.semDiesel}`;
  ['all','antes','fora','depois','cal'].forEach(k=>console.log(' TOT',k,f(t[k]))); console.log(' OPER dem cal',nf(t.operDem,2),'atend cal',nf(t.operAt,2));
  const rc=L.resumoCultura(s,saf,cs.oc); Object.values(rc).forEach(b=>console.log(' CULT',b.cult,'area',nf(b.area,2),'cop',nf(b.cop,2),'cins',nf(b.cins,2),'pend',b.npend,'tar',b.ntar,'rha',b.rha===null?'parcial':nf(b.rha,2),'rhaTodas',nf(b.rhaTodas,2),'semAntes',nf(b.rhaSemAntes,2),'copAntes',nf(b.copAntes,2),'cinsAntes',nf(b.cinsAntes,2)));
  const sit={}; cs.oc.forEach(i=>{ const k=L.situacao(i,cs.G); sit[k]=(sit[k]||0)+1; }); console.log(' SIT ocorr',JSON.stringify(sit));
  return {s,cs,v}; }
module.exports={rel};
if(require.main===module){ const w=process.argv[2]; (w?[w]:['S2627','S27SF','LG2627','S2526']).forEach(x=>rel(x)); }
