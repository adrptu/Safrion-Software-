const L=require('./cap2.js'); const {X,mk,nf}=L;
const s=mk('S2627',5); X.PREVALS(s,{}); const cs=L.capSaf(s,'S2627');
function linha(k,mi){ const g=cs.G[k]; const c=g.cells[mi]; const its=cs.oc.filter(i=>i.mi===mi&&L.cargaRec(i,k)>1e-9);
  const byOp={}; its.forEach(i=>{ const o=byOp[i.a.op]||(byOp[i.a.op]={h:0,hc:0,its:[]}); o.h+=L.cargaRec(i,k); o.hc+=i.horas; o.its.push(i); });
  console.log('\n'+g.nome+' · '+c.mes+': '+nf(c.d,1)+' h de '+nf(c.cap,1)+' h ('+nf(c.ocup,2)+' %) · desta safra '+nf(c.dThis,1)+(c.dOth>1e-4?' · outras '+nf(c.dOth,1):'')+' · precisa de '+c.nec+', tem '+g.un+' | Σ horas-conjunto das ocorrências '+nf(its.reduce((a,i)=>a+i.horas,0),2));
  Object.entries(byOp).forEach(([op,o])=>{ console.log('  '+op+': '+nf(o.h,2)+' h do recurso ('+nf(o.hc,2)+' h-conj)');
    o.its.forEach(i=>console.log('     '+i.c.v.local+' · '+i.a.nome+' '+i.dt+': '+nf(L.cargaRec(i,k),2)+' h'+(i.cfs.length>1?' | '+i.rp.itens.map((x,j)=>(i.cfs[j].v.nome||'')+' '+((i.cfs[j].rec||{})[k]?nf(x.nh*(i.cfs[j].rec[k]),2)+' h':'não usa')).join(' ; '):''))); });
  console.log('  TOTAL '+nf(Object.values(byOp).reduce((a,o)=>a+o.h,0),2)); }
linha('colh',5); linha('plant',1); linha('trator',1); linha('oper',1); linha('oper',8); linha('trator',5); linha('pulv',3);
// R-05: OS-0421 Fungicida 1ª aplicação em dez/26
const fung=cs.oc.filter(i=>i.mi===3&&/Fungicida/.test(i.a.nome)); fung.forEach(i=>console.log('dez/26',i.c.v.local,i.a.nome,i.dt,nf(i.area,0),'ha',nf(i.horas,2),'h'));
// fmtOcup: células perto do limiar
Object.values(cs.G).forEach(g=>g.cells.forEach(c=>{ if(c.d>1e-4&&c.ocup<1.5) console.log('limiar',g.nome,c.mes,nf(c.ocup,3),L.fmtOcup(c.ocup),c.own?'':'(só outra)'); }));
