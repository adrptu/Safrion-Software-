// MN-04/R-09 (escopo "Todas" = atividades em uso) sobre o corpo com a correção (saf_body_mn04.js) + MN-06 origemCfg
const H=require('../motor345/h_mn04.js'); const X=H.X, mk=H.mk; const nf=(x,d=2)=>Number(x).toLocaleString('pt-BR',{minimumFractionDigits:d,maximumFractionDigits:d});
const num=v=>(v===''||v===null||v===undefined)?null:Number(String(v).replace(',','.'));
function origemCfg(k){ const v=k.v; const base=String(v.base||String(k.id).split('.')[0]); const c=(X.D2.conj||[]).find(q=>q.id===base); const co=(X.D2.conj_opts||{})[base]; if(!c) return 'Ajustado nesta safra';
  const eq=(a,b)=>{ const x=num(a), y=num(b); if(x===null&&y===null) return true; if(x===null||y===null) return false; return Math.abs(x-y)<1e-9; };
  const atual=co?co.atual:c.id; if(String(v.conj_id)!==String(atual)) return 'Ajustado nesta safra';
  const calc=!!c.larg; if((v.modo==='Largura × velocidade')!==calc) return 'Ajustado nesta safra';
  if(calc){ if(!eq(v.larg,c.larg)||!eq(v.vel,c.vel)||!eq(v.efic,c.efic)) return 'Ajustado nesta safra'; } else if(!eq(v.rend,c.rend)) return 'Ajustado nesta safra';
  for(const f of ['maq','impl','pess','pess_rs','diesel']) if(!eq(v[f],c[f])) return 'Ajustado nesta safra';
  return 'Padrão do cadastro (CD-02)'; }
function leaves(rows){ const o=[]; const w=l=>l.forEach(r=>{ if(r.kids&&r.kids.length) w(r.kids); else if(!r.grp) o.push(r); }); w(rows); return o; }
function cont(s,saf){ const ls=leaves(X.g2rows(s,X.GR('g_rend_'+saf))); const p=ls.filter(k=>origemCfg(k).startsWith('Padrão')).length; return p+' de '+ls.length+' padrão; ajustadas: '+ls.filter(k=>!origemCfg(k).startsWith('Padrão')).map(k=>k.v.atv+' ['+k.v.nome+']').join(', '); }
for(const saf of ['S2627','S27SF','LG2627','S2526']){ const s=mk(saf,3); X.PREVALS(s,{}); console.log('base',saf,cont(s,saf)); }
const saf='S2627', gid='g_rend_S2627';
{ const s=mk(saf,3); const v={}; X.PREVALS(s,v); const uso=new Set(X.ocorr(s,saf).filter(o=>o.a.op==='Pulverização').map(o=>o.a.nome)); console.log('em uso Pulverização',uso.size,[...uso].join(', '));
  const rows=X.g2clone(X.g2rows(s,X.GR(gid))); const g=rows.find(q=>q.grp&&q.v.op==='Pulverização'); const r=g.kids.find(k=>uso.has(k.v.atv)); const antes=g.kids.map(k=>k.v.atv+':'+k.v.vel);
  r.v.vel=12; r.v.esc='Todas as atividades da operação'; X.rendAfter(s,gid,rows,r,false); console.log('aviso:',s.state.g2toast);
  const g2=X.g2rows(s,X.GR(gid)).find(q=>q.grp&&q.v.op==='Pulverização');
  g2.kids.forEach(k=>console.log('  ',k.v.atv,uso.has(k.v.atv)?'(em uso)':'(fora)',nf(k.v.rend),'ha/h vel',k.v.vel,'|',origemCfg(k)));
  X.PREVALS(s,{}); const oc=X.ocorr(s,saf); const S=f=>oc.reduce((a,i)=>a+(Number(i[f])||0),0); console.log('totais h',nf(S('horas')),'cop',nf(S('cop'))); }
{ const s=mk(saf,3); X.PREVALS(s,{}); const rows=X.g2clone(X.g2rows(s,X.GR(gid))); const g=rows.find(q=>q.grp&&q.v.op==='Pulverização'); const r=g.kids.find(k=>k.v.atv==='Dessecação pré-plantio')||g.kids[0];
  r.v.esc='Todas as atividades da operação'; X.rendAfter(s,gid,rows,r,false); console.log('salvar sem mudar (Todas):',cont(s,saf)); }
{ const s=mk(saf,3); X.PREVALS(s,{}); const rows=X.g2clone(X.g2rows(s,X.GR(gid))); const g=rows.find(q=>q.grp&&q.v.op==='Plantio'); const r=g.kids[0].kids.find(k=>k.v.conj_id!=='prestador');
  r.v.vel=9; X.rendAfter(s,gid,rows,r,false); console.log('Plantio dividido vel 7→9:',origemCfg(X.g2rows(s,X.GR(gid)).find(q=>q.grp&&q.v.op==='Plantio').kids[0].kids.find(k=>k.v.conj_id!=='prestador'))); }
