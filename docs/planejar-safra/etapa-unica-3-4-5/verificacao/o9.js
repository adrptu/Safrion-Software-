const L=require('./cap2.js'); const {X,mk,nf}=L; const saf='S2627', gid='g_rend_S2627';
function snap(s,lbl){ X.PREVALS(s,{}); const cs=L.capSaf(s,saf); const t=L.totais(s,saf,cs.oc); const v={}; X.PREVALS(s,v);
  const op=n=>{ const o=X.GR('g_op').rows.find(o=>o.v.nome===n); return nf(o.v.horas,2); };
  console.log(lbl,'| h',nf(t.all.h,2),'cop',nf(t.all.cop,2),'hh',nf(t.all.hh,2),'| Adub',op('Adubação a lanço'),'| Dist nov',nf(cs.G.dist.cells[2].ocup,2),'% | Oper out',nf(cs.G.oper.cells[1].ocup,2),'% HS oper',nf(cs.G.oper.horasSafra,2),'| max dist',nf(cs.G.dist.max.ocup,2),cs.G.dist.max.mes); return cs; }
{ const s=mk(saf,3); snap(s,'O9 antes'); const rows=X.g2clone(X.g2rows(s,X.GR(gid))); const g=rows.find(q=>q.grp&&q.v.op==='Adubação a lanço'); const r=g.kids.find(k=>k.v.atv==='Adubação de cobertura');
  r.v.larg=12; r.v.esc='Só esta atividade'; X.rendAfter(s,gid,rows,r,false); console.log(' aviso:',s.state.g2toast);
  const rr=X.g2rows(s,X.GR(gid)).find(q=>q.grp&&q.v.op==='Adubação a lanço'); console.log(' irmãs',rr.kids.map(k=>k.v.atv+':'+nf(k.v.rend,2)+' R$/ha '+nf(k.v.custo_ha,2)).join(', ')); snap(s,'O9 depois'); }
{ const s=mk(saf,3); snap(s,'O20 antes'); const rows=X.g2clone(X.g2rows(s,X.GR(gid))); const g=rows.find(q=>q.grp&&q.v.op==='Plantio'); const r=g.kids[0].kids.find(k=>k.v.conj_id!=='prestador');
  console.log(' folha',r.id,r.v.nome,'pess',r.v.pess); r.v.pess=3; X.rendAfter(s,gid,rows,r,false); snap(s,'O20 depois'); }
