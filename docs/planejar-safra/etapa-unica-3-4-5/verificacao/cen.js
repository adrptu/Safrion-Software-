const L=require('./cap2.js'); const {X,mk,nf,fmtOcup}=L;
const setRec=(g,id,un)=>s=>{ const rows=X.g2clone(X.g2rows(s,X.GR(g))); rows.find(r=>r.id===id).v.un=un; X.g2set(s,g,{rows}); };
function run(saf,mod,lbl,recs){ const s=mk(saf,5); if(mod) mod(s); X.PREVALS(s,{}); const cs=L.capSaf(s,saf); const v=L.veredito(s,saf,cs);
  const semRec=cs.oc.filter(i=>i.rp.itens.some(x=>x.semRec)).length;
  const t=L.totais(s,saf,cs.oc);
  console.log('\n==',saf,lbl,'|',v.R,v.cor,'|',v.txt,'| ocorr c/ item semRec',semRec,'| pend',t.all.pend,'| h',nf(t.all.h,2),'hh',nf(t.all.hh,2),'cop',nf(t.all.cop,2));
  (recs||Object.keys(cs.G)).forEach(k=>{ const g=cs.G[k]; console.log('  ',g.nome,'un',g.un,'max',g.max?(g.max.ocup===null?'n/c':nf(g.max.ocup,2)+'%')+' '+g.max.mes:'—','| reds',g.reds.map(c=>c.mes+':'+c.nec+(c.soma?'(soma)':'')).join(','),'| HS',nf(g.horasSafra,2),
    '\n     ',g.cells.filter(c=>c.d>1e-4).map(c=>c.mes+' '+(c.ocup===null?'n/c':nf(c.ocup,2)+'%')+' nec '+c.nec+(c.red?' RED':'')+' ('+nf(c.dThis,2)+(c.dOth>1e-4?'+'+nf(c.dOth,2):'')+'/'+nf(c.cap,2)+')').join(' | ')); });
  return {s,cs,v}; }
module.exports={run,setRec};
if(require.main===module){
 run('S2627',setRec('g_recp_maq','colh',0),'Colhedoras=0',['colh','trator','oper']);
 run('S2627',setRec('g_recp_pes','oper',5),'Operadores=5',['oper']);
 run('S2627',setRec('g_recp_pes','oper',0),'Operadores=0',['oper']);
 run('S2627',setRec('g_recp_maq','trator',5),'Tratores=5',['trator']);
 run('S2627',setRec('g_recp_maq','trator',1),'Tratores=1',['trator']);
 run('S2627',s=>{ const rows=X.g2clone(X.g2rows(s,X.GR('g_saf'))); const r=rows.find(r=>r.id==='S27SF'); r.ro=true; r.v.estado='Encerrada'; X.g2set(s,'g_saf',{rows}); },'S27SF encerrada',['trator','oper']);
 run('LG2627',setRec('g_recp_pes','oper',10),'LG Operadores=10',['oper','trator']);
 run('LG2627',setRec('g_recp_pes','oper',5),'LG Operadores=5',['oper','trator']);
 run('S2627',s=>{ const gc='g_cult_S2627'; const rows=X.g2clone(X.g2rows(s,X.GR(gc))); const lv=[]; const w=l=>l.forEach(r=>{ if(r.kids) w(r.kids); else lv.push(r); }); w(rows);
   lv.forEach(r=>{ if(!r.livre&&r.v.cult==='Soja'&&!r.v.plano) r.v.plano='SOJA-AT'; }); X.g2set(s,gc,{rows}); },'C9 SOJA-AT',['colh']);
}
