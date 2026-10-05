const L=require('./cap2.js'); const {X,mk,nf,mlabDt}=L;
// MN-03: faixa real de meses por operação e Y/Z da demanda
for(const saf of ['LG2627','S2526','S2627']){ const s=mk(saf,5); X.PREVALS(s,{}); const oc=X.ocorr(s,saf); const by={};
  oc.forEach(i=>{ const o=by[i.a.op]||(by[i.a.op]=[]); o.push(i.dt); });
  console.log(saf,Object.entries(by).map(([op,ds])=>{ ds.sort(); const a=mlabDt(ds[0]), b=mlabDt(ds[ds.length-1]); return op+': '+(a===b?a:a+' – '+b); }).join(' | '));
  const dm=X.demanda(s,saf); let Xp=0,Z=0,liq=0,n=0; Object.values(dm).forEach(d=>{ Xp+=d.plano*d.preco; Z+=d.bruta*d.preco; liq+=d.valor; if(d.liq>0.001) n++; });
  console.log('  insumos plano',nf(Xp,2),'Z bruta',nf(Z,3),'Y=X-Z',nf(Xp-Z,2),'| liquida',nf(liq,2),n); }
// LG2627 atividade de plantio de mudas
{ const s=mk('LG2627',5); X.PREVALS(s,{}); const oc=X.ocorr(s,'LG2627'); const pm=oc.filter(i=>/mudas/i.test(i.a.nome)); const ds=pm.map(i=>i.dt).sort();
  console.log('Plantio de mudas',pm.length,'ocorr',mlabDt(ds[0]),'–',mlabDt(ds[ds.length-1]),'cop',nf(pm.reduce((a,i)=>a+(i.cop||0),0),2),'antes',nf(pm.filter(i=>i.dt<'2026-09-01').reduce((a,i)=>a+(i.cop||0),0),2),pm.filter(i=>i.dt<'2026-09-01').length,'| op',pm[0]&&pm[0].a.op);
  const ent=oc.filter(i=>i.dt>='2026-09-01'&&i.dt<'2026-09-23'); console.log('01–22/09 dentro da safra antes de hoje',ent.length,'cop',nf(ent.reduce((a,i)=>a+(i.cop||0),0),2),'cins',nf(ent.reduce((a,i)=>a+i.cins,0),2)); }
// P11: áreas por safra
for(const saf of ['S2627','S27SF']){ const s=mk(saf,5); X.PREVALS(s,{}); const cs=X.cultRows(s,saf); console.log(saf,'cultivos',cs.length,'área',nf(cs.reduce((a,c)=>a+(Number(c.v.area)||0),0),2),'com plano',nf(cs.filter(c=>c.v.plano).reduce((a,c)=>a+(Number(c.v.area)||0),0),2),'sem plano',cs.filter(c=>!c.v.plano).map(c=>c.v.local+' '+c.v.area).join(', ')); }
// MN-02: quem deixa / volta a trabalhar
function semRecSet(saf,mod){ const s=mk(saf,5); if(mod) mod(s); X.PREVALS(s,{}); return X.ocorr(s,saf).filter(i=>i.rp.itens.some(x=>x.semRec)).map(i=>i.c.v.local+'·'+i.a.nome+'·'+i.rp.itens.filter(x=>x.semRec).map(x=>x.nome).join('+')); }
const setRec=(g,id,un)=>s=>{ const rows=X.g2clone(X.g2rows(s,X.GR(g))); rows.find(r=>r.id===id).v.un=un; X.g2set(s,g,{rows}); };
const dif=(a,b)=>({sai:b.filter(x=>!a.includes(x)),volta:a.filter(x=>!b.includes(x))});
{ const a=semRecSet('S2627'), b=semRecSet('S2627',setRec('g_recp_pes','oper',5)); const d=dif(a,b); console.log('S2627 oper 8→5 deixam',d.sai.length,d.sai.join(' | '),'voltam',d.volta.length); }
{ const a=semRecSet('LG2627'), b=semRecSet('LG2627',setRec('g_recp_pes','oper',10)); const d=dif(a,b); console.log('LG oper 8→10 deixam',d.sai.length,'voltam',d.volta.length,[...new Set(d.volta.map(x=>x.split('·').slice(1).join('·')))].join(' | ')); }
{ const a=semRecSet('LG2627'), b=semRecSet('LG2627',setRec('g_recp_pes','oper',5)); const d=dif(a,b); console.log('LG oper 8→5 deixam',d.sai.length,[...new Set(d.sai.map(x=>x.split('·').slice(1).join('·')))].join(' | ')); }
{ const a=semRecSet('S2627'), b=semRecSet('S2627',setRec('g_recp_maq','trator',5)); const d=dif(a,b); console.log('S2627 trator 4→5 deixam',d.sai.length,'voltam',d.volta.length); }
// MN-02 C14: serialização com 2 configurações de colhedora
const cf=(id,r)=>({id,nome:'Colhedora '+id,rend:r,part:'',jan:40,custo_h:100,diesel:'',pess:0,seq:false,troca:'',ativos:[],rec:{colh:1}});
for(const un of [1,2]){ const rp=X.repartir(300,[cf('a',5),cf('b',4)],{colh:{un,nome:'Colhedoras'}}); console.log('C14 colh',un,'hconj',nf(rp.hconj,2),'saldo',nf(rp.saldo,2),'decorrido',nf(rp.decorrido,2)); }
