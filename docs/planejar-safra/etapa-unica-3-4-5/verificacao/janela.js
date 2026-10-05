const L=require('./cap2.js'); const {X,mk,nf}=L;
function setJan(saf,op,val,soAtv){ return s=>{ const gid='g_rend_'+saf; const rows=X.g2clone(X.g2rows(s,X.GR(gid)));
  const leaves=[]; const w=l=>l.forEach(r=>{ if(r.kids&&r.kids.length) w(r.kids); else if(!r.grp) leaves.push(r); }); w(rows);
  leaves.forEach(k=>{ if((op===null||k.v.op===op)&&(!soAtv||k.v.atv===soAtv)) k.v.jan=val; }); X.g2set(s,gid,{rows}); }; }
function run(saf,mod,lbl){ const s=mk(saf,5); if(mod) mod(s); X.PREVALS(s,{}); const cs=L.capSaf(s,saf); const v=L.veredito(s,saf,cs); const t=L.totais(s,saf,cs.oc);
  console.log('\n==',saf,lbl,'|',v.R,v.cor,'|',v.txt,'| h',nf(t.all.h,2),'saldo',nf(t.all.saldo,2));
  const ops={}; cs.oc.forEach(i=>{ (ops[i.a.op]||(ops[i.a.op]=[])).push(L.situacao(i,cs.G)); });
  Object.entries(ops).forEach(([op,ss])=>{ const st=ss.includes('Com pendência')?'Com pendência':(ss.includes('Janela não informada')?'Janela não informada':'Cabe na janela'); console.log('   op',op,'→',st); });
  cs.oc.filter(i=>/Colheita/.test(i.a.op)).forEach(i=>console.log('   ',i.c.id,i.c.v.local,i.a.nome,nf(i.area,0),'ha | nec',nf(i.rp.nec.hconj,2),'h | atend',nf(i.rp.hconj||0,2),'h | saldo',nf(i.saldo,2),'ha | sit',L.situacao(i,cs.G),'|',i.rp.motivos.join(' · ')));
  const c=cs.G.colh; console.log('   Colhedoras', c.cells.filter(x=>x.d>1e-4).map(x=>x.mes+' '+nf(x.ocup,2)+'% '+nf(x.d,2)+'h').join(' | ')); }
run('S2627',setJan('S2627','Colheita de grãos',60),'Colheita de grãos jan 60');
run('S2627',setJan('S2627','Colheita de grãos',50),'Colheita de grãos jan 50');
run('S2627',setJan('S2627','Colheita de grãos',40),'Colheita de grãos jan 40');
run('S27SF',setJan('S27SF',null,60),'S27SF todas jan 60');
run('S27SF',setJan('S27SF','Colheita de grãos',40),'S27SF Colheita jan 40');
