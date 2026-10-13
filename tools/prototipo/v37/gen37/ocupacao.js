// ===== Ocupação dos talhões no tempo (Planejar safra, etapa 2 · ESPECIFICACAO.md R-01 a R-25) =====
// Fonte única das regras (ENG-011); espelho em ocupacao.py e paridade em ocupacao_unit.py. Datas são dias inteiros desde 01/01/1970;
// OC_INF = sem fim. Previsão não trava, o certo trava: núcleo (plantio até o ciclo mínimo da cultura), perene, colheita real e área.
// Cruzamento de previsões vira pendência visível; o plano entra na demanda. Sem dependência da tela: recebe cadastros e cultivos.
const OC_INF=100000000;
const OC_ROT={perene:'Perene',observado:'Observado',plano:'Pelo plano',informada:'Colheita informada',estimado:'Estimado (ciclo)',semdata:'Sem ciclo'};
function ocDia(s){ if(!s) return null; const m=/^(\d{4})-(\d{2})-(\d{2})/.exec(String(s)); if(!m) return null; return Math.round(Date.UTC(+m[1],+m[2]-1,+m[3])/86400000); }
function ocIso(d){ if(d===null||d===undefined||d>=OC_INF) return ''; return new Date(d*86400000).toISOString().slice(0,10); }
function ocBr(d){ if(d===null||d===undefined) return 'sem data'; if(d>=OC_INF) return 'sem fim'; const s=ocIso(d); return s.slice(8,10)+'/'+s.slice(5,7)+'/'+s.slice(0,4); }
function ocDdmm(d){ return ocBr(d).slice(0,5); }
function ocR2(x){ return Math.floor(x*100+0.5)/100; }
function ocHa(x){ let v=ocR2(x); const neg=v<0; v=Math.abs(v); let ip=Math.floor(v), fr=Math.round((v-ip)*100); if(fr===100){ ip++; fr=0; }
  let s=String(ip).replace(/\B(?=(\d{3})+(?!\d))/g,'.'); if(fr) s+=','+String(fr).padStart(2,'0').replace(/0+$/,''); return (neg?'-':'')+s; }
function ocMais(d,n){ return d>=OC_INF?OC_INF:d+n; }
function ocMin(a){ return a.reduce((m,x)=>x<m?x:m,Infinity); }
function ocMax(a){ return a.reduce((m,x)=>x>m?x:m,-Infinity); }
// ---------- contexto (cadastros) ----------
// culturas {nome: 'Anual'|'Perene'}; cultivares [[cultura, variedade, dias]]; planos [plano]
function ocCtx(culturas,cultivares,planos,folga){ const cic={}, mn={}, mx={};
  (cultivares||[]).forEach(([c,v,d])=>{ if(d===''||d===null||d===undefined) return; d=Number(d); cic[c+'|'+v]=d; mn[c]=Math.min(mn[c]===undefined?1e6:mn[c],d); mx[c]=Math.max(mx[c]||0,d); });
  const pl={}; (planos||[]).forEach(p=>{ pl[p.id]=p; });
  return {classe:Object.assign({},culturas||{}),cic,cicmin:mn,cicmax:mx,planos:pl,pub:(planos||[]).filter(p=>(p.estado||'Publicado')==='Publicado'),folga:Number(folga===undefined?1:folga)}; }
function ocAntecedencia(ctx,pid){ const pl=ctx.planos[pid]; if(!pl) return 0; let m=0; pl.atividades.forEach(a=>{ if(a.g.tipo==='DAP'&&(a.g.dias||0)<0) m=Math.max(m,-a.g.dias); }); return m; }
function ocColheitaPlano(pl,plantio){ const ca=pl.atividades.find(a=>String(a.op).indexOf('Colheita')===0); if(ca&&ca.g.tipo==='DAP') return plantio+ca.g.dias; if(ca&&ca.g.tipo==='DATA') return ocDia(ca.g.data); return plantio; }
function ocAtividades(ctx,plantio,pid,colheita){ const pl=ctx.planos[pid]; if(!pl) return [];
  return pl.atividades.map(a=>{ const g=a.g, t=g.tipo; let d; if(t==='DAP') d=plantio+g.dias; else if(t==='DATA') d=ocDia(g.data);
    else { const col=(colheita!==null&&colheita!==undefined)?colheita:ocColheitaPlano(pl,plantio); d=col+(t==='DAPC'?g.dias:-g.dias); } return [a.nome,t,d]; }); }
function ocDatasValidas(ctx,plantio,pid,safini,safim,colheita){ const ok=[], fora=[]; const ant=ocAntecedencia(ctx,pid);
  ocAtividades(ctx,plantio,pid,colheita).forEach(([n,tp,d])=>{ if(tp==='DATA'&&!(safini<=d&&d<=safim&&d>=plantio-ant)) fora.push([n,d]); else ok.push([n,tp,d]); }); return [ok,fora]; }
function ocFimEstimado(ctx,cult,vr,plantio){ const cands=[]; const k=cult+'|'+vr; if(k in ctx.cic) cands.push(plantio+ctx.cic[k]);
  ctx.pub.forEach(p=>{ if(p.cultura!==cult) return; const ds=ocAtividades(ctx,plantio,p.id,null).filter(x=>x[1]!=='DATA').map(x=>x[2]); if(ds.length) cands.push(ocMax(ds)); });
  return cands.length?ocMax(cands):null; }
// ---------- ocupação ----------
function ocTalhaoDe(local,tipo){ return tipo!=='Parcela'?local:String(local).replace(/-[^-]*$/,''); }
// c: {id, ciclo, saf, faz, talhao, faixa, tipo, area, cult, var, plantio, plano, colheita, colheita_real, origem}; s: {id, nome, ini, fim, ro}
function ocMk(ctx,c,s){ const folga=ctx.folga; let pid=c.plano||null;
  if(pid&&(!ctx.planos[pid]||ctx.planos[pid].cultura!==c.cult)) pid=null;   // plano de outra cultura não vale (R-04)
  const pl=ocDia(c.plantio); const colh=c.colheita?ocDia(c.colheita):null; const real=c.colheita_real?ocDia(c.colheita_real):null;
  const o={id:c.id,ciclo:c.ciclo||c.id,saf:c.saf,safs:[c.saf],safnome:s.nome||c.saf,faz:c.faz,t:c.talhao||ocTalhaoDe(c.faixa,c.tipo),faixa:c.faixa,tipo:c.tipo,area:Number(c.area||0),
    cult:c.cult,var:c.var||'',plantio:pl,plano:pid,safini:ocDia(s.ini),safim:ocDia(s.fim),ro:!!s.ro,colh_inf:colh,colh_real:real,origem:c.origem||'',avisos:[],folga,ini:pl};
  let dfim=null;
  if(pid){ const [ok,fora]=ocDatasValidas(ctx,pl,pid,o.safini,o.safim,colh); const iniC=[pl].concat(ok.filter(x=>x[1]==='DAP'||x[1]==='DATA').map(x=>x[2])); o.ini=ocMin(iniC);
    if(fora.length) o.avisos.push(['datas_fixas',pid,fora[0][1]]);
    dfim=ocMax([pl].concat(ok.map(x=>x[2])).concat(colh!==null?[colh]:[])); }
  const classe=ctx.classe[o.cult]||'Anual';
  if(classe==='Perene'){ o.fim=OC_INF; o.classe='perene'; }
  else if(real!==null){ o.fim=real; o.classe='observado'; }
  else if(pid){ o.fim=dfim; o.classe='plano'; }
  else if(colh!==null){ o.fim=colh; o.classe='informada'; }
  else { const e=ocFimEstimado(ctx,o.cult,o.var,pl); if(e!==null){ o.fim=e; o.classe='estimado'; } else { o.fim=null; o.classe='semdata'; } }
  const cm=ctx.cicmin[o.cult];
  if(o.classe==='perene') o.nuc=OC_INF; else if(o.classe==='observado') o.nuc=real; else if(cm) o.nuc=Math.min(o.fim!==null?o.fim:OC_INF,pl+cm-1); else o.nuc=pl;
  return o; }
function ocP(ctx,o){ if(o.classe==='perene') return OC_INF; if(o.classe==='plano'||o.classe==='informada'||o.classe==='observado') return o.fim;
  if(o.classe==='estimado') return Math.max(o.safim,o.fim); const mc=ctx.cicmax[o.cult]; return mc?Math.max(o.safim,o.plantio+mc):OC_INF; }
function ocOcupaAte(ctx,o,modo){ if(modo==='pior') return ocP(ctx,o); if(o.classe==='semdata') return o.plantio; return o.fim; }
function ocLib(ctx,o,modo){ return ocMais(ocOcupaAte(ctx,o,modo),o.folga); }
function ocNucLib(o){ return ocMais(o.nuc,o.folga); }
function ocNucAtivo(o,x){ return (o.plantio<=x&&x<ocNucLib(o))||o.plantio===x; }
function ocMesmaArea(a,b){ return a.faixa===b.faixa||a.tipo!=='Parcela'||b.tipo!=='Parcela'; }
function ocComPlano(o){ return !!o.plano||o.classe==='perene'; }
function ocOcupacoes(ctx,safras,cults){ const recs=[], vistos={};
  (cults||[]).forEach(c=>{ const s=safras[c.saf]; if(!s) return; const o=ocMk(ctx,c,s);
    if(vistos[o.ciclo]){ vistos[o.ciclo].safs.push(c.saf); return; } vistos[o.ciclo]=o; recs.push(o); }); return recs; }
function ocIntersec(a0,a1,b0,b1){ const x0=Math.max(a0,b0), x1=Math.min(a1,b1); return x0<x1?[x0,x1]:null; }
function ocCmp(a,b){ return (a.plantio-b.plantio)||(a.id<b.id?-1:(a.id>b.id?1:0)); }
// R-14 trava e R-15 pendência entre as ocupações de um talhão de área T. A pendência fica na de plantio mais tardio.
// Soma no tempo por eventos (SAF-C01): os núcleos ativos só mudam em plantio, plantio + 1 e fim do núcleo (com folga), e os períodos previstos
// em início e liberação (est). Entre dois pontos seguidos nada muda: cada trecho é avaliado uma vez, sem horizonte (o teto antigo, d0 + 900
// dias, deixava uma perene ou ocupação antiga esconder a soma de anos depois). Depois do último ponto só ficam perenes, com núcleo igual ao
// previsto: dá trava ou nada, nunca pendência; por isso o último trecho conta 1 dia.
function ocAvalia(ctx,occs,T,alvo){ const trav=[], pend={}; const oc=occs.slice().sort(ocCmp); const add=(k,x)=>{ (pend[k]||(pend[k]=[])).push(x); };
  for(let i=0;i<oc.length;i++){ const A=oc[i]; for(let j=i+1;j<oc.length;j++){ const B=oc[j];
    if(A.ciclo===B.ciclo) continue; if(alvo&&alvo!==A.id&&alvo!==B.id) continue; if(!ocMesmaArea(A,B)) continue;
    [[A,B],[B,A]].forEach(([X,Y])=>{ if(Y.classe==='observado'&&ocIntersec(X.ini,ocLib(ctx,X,'est'),Y.plantio,ocNucLib(Y))&&X.plantio>=Y.plantio) trav.push(['observado',Y.id,X.id,Math.max(X.ini,Y.plantio)]); });
    if((ocComPlano(A)||ocComPlano(B))&&ocIntersec(A.plantio,ocNucLib(A),B.plantio,ocNucLib(B))){ trav.push(['faixa',A.id,B.id,B.plantio]); continue; }
    const kind={plano:'prevista',informada:'prevista',observado:'prevista',estimado:'provavel',semdata:'naoconf'}[A.classe];
    if(kind){ const fimA=ocLib(ctx,A,kind==='naoconf'?'pior':'est'); const r=ocIntersec(A.ini,fimA,B.ini,ocLib(ctx,B,'est')); if(r) add(B.id,[kind,A.id,r[0],r[1]-1,r[1]-r[0]]); } } }
  if(occs.length){ const pts=new Set();
    occs.forEach(o=>{ [o.plantio,o.plantio+1,ocNucLib(o),o.ini,ocLib(ctx,o,'est')].forEach(x=>{ if(x<OC_INF) pts.add(x); }); });
    const xs=Array.from(pts).sort((p,q)=>p-q);
    const visT={}, visP={}, ordP=[]; const sum=(l)=>l.reduce((s,o)=>s+o.area,0);
    const cruz=(l)=>l.some((a,k)=>l.slice(k+1).some(b=>ocMesmaArea(a,b)&&a.ciclo!==b.ciclo));
    const ult=(l)=>l.reduce((m,o)=>(!m||ocCmp(o,m)>0)?o:m,null);
    for(let i=0;i<xs.length;i++){ const x=xs[i], n=(i+1<xs.length?xs[i+1]:x+1)-x; const nu=occs.filter(o=>ocNucAtivo(o,x));
      if(sum(nu)>T+0.005&&nu.some(ocComPlano)&&!cruz(nu)){ const last=ult(nu);
        if(!alvo||nu.some(o=>o.id===alvo)){ const k=nu.filter(o=>o!==last).map(o=>o.id).sort().join('+'); const kk=k+'>'+last.id; if(!visT[kk]){ visT[kk]=1; trav.push(['soma',k,last.id,x,ocR2(sum(nu))]); } } }
      else { const pv=occs.filter(o=>o.ini<=x&&x<ocLib(ctx,o,'est'));
        if(sum(pv)>T+0.005&&!cruz(pv)){ const last=ult(pv); const key=last.id+'>'+pv.filter(o=>o!==last).map(o=>o.id).sort().join('+');
          if(!visP[key]){ visP[key]=[x,x,0]; ordP.push(key); } const v=visP[key]; v[1]=x+n-1; v[2]+=n; } } }
    ordP.forEach(key=>{ const i=key.indexOf('>'); const lid=key.slice(0,i), causa=key.slice(i+1); const v=visP[key];
      if(alvo&&alvo!==lid&&causa.split('+').indexOf(alvo)<0) return; add(lid,['soma',causa,v[0],v[1],v[2]]); }); }
  return [trav,pend]; }
// ---------- tabela da etapa 2 ----------
// safra {id, ini, fim, faz, ro}; talhoes [[nome, área]] na ordem do CD-01; occ = ocOcupacoes de todas as safras; safras {id: safra}
function ocTabela(ctx,safra,occ0,talhoes,safras){ const sid=safra.id, a=ocDia(safra.ini), b=ocDia(safra.fim), faz=safra.faz;
  const occ=occ0.filter(o=>o.faz===faz); const linhas=[]; const band={nesta:0,livre:0,conf:0,perene:0,ocup:0};
  (talhoes||[]).forEach(([t,T0])=>{ const T=Number(T0);
    const own=occ.filter(o=>o.t===t&&o.safs.indexOf(sid)>=0);
    const fora=occ.filter(o=>o.t===t&&o.safs.indexOf(sid)<0&&o.ini<=b&&ocLib(ctx,o,'pior')>a);
    const A=own.reduce((s,o)=>s+o.area,0); const n=b-a+1;
    const lib={pior:fora.map(o=>ocLib(ctx,o,'pior')),est:fora.map(o=>ocLib(ctx,o,'est'))};
    const mfirst=(modo)=>{ const L=lib[modo]; const m=new Array(n); let cur=1e18;
      for(let i=n-1;i>=0;i--){ const x=a+i; let f=T-A; fora.forEach((o,k)=>{ if(o.ini<=x&&x<L[k]) f-=o.area; }); cur=Math.min(cur,f); m[i]=cur; }
      for(let i=0;i<n;i++){ if(m[i]>0.005) return [ocR2(m[i]),a+i]; } return [0,null]; };
    const [Lp,dp]=mfirst('pior'), [Le,de]=mfirst('est');
    const fix=fora.filter(o=>(o.classe==='estimado'||o.classe==='semdata')&&dp!==null&&dp===ocLib(ctx,o,'pior')).map(o=>o.id);
    let livre, conf, desde; if(fix.length){ livre=0; conf=Math.max(Le,Lp); desde=de; } else { livre=Lp; conf=ocR2(Math.max(0,Le-Lp)); desde=(Lp>0.005?dp:de); }
    const est=conf>0.005||fix.length>0;
    const [tr,pe]=ocAvalia(ctx,own.concat(fora),T,null);
    const idsOwn=own.map(o=>o.id); const pendOwn={}; Object.keys(pe).forEach(k=>{ if(idsOwn.indexOf(k)>=0||pe[k].some(p=>idsOwn.indexOf(p[1])>=0)) pendOwn[k]=pe[k]; });
    const seq=[]; const todos=own.concat(fora);
    todos.forEach(x=>{ if(x.classe!=='estimado'&&x.classe!=='semdata') return; todos.forEach(y=>{ if(y===x||((own.indexOf(x)>=0)===(own.indexOf(y)>=0))||!ocMesmaArea(x,y)) return;
      if(x.ini<y.ini&&y.ini<ocLib(ctx,x,'pior')) seq.push([x.id,y.id]); }); });
    let sit; if(tr.length) sit='Sobreposição'; else if(conf>0.005||seq.length||Object.keys(pendOwn).length) sit='A conferir'; else if(livre>0.005) sit='Livre'; else if(own.length) sit='Planejado';
    else if(fora.some(o=>o.classe==='perene')) sit='Perene'; else sit='Ocupado';
    const nomes={}; own.forEach(o=>{ nomes[o.faixa]=1; }); const inteiro=own.some(o=>o.tipo!=='Parcela'); const adj=[];
    own.forEach(x=>{ const ant=fora.filter(o=>ocMesmaArea(o,x)&&o.ini<x.ini), suc=fora.filter(o=>ocMesmaArea(o,x)&&o.ini>x.ini);
      if(ant.length) adj.push(ant.reduce((m,o)=>(!m||o.ini>m.ini||(o.ini===m.ini&&o.id>m.id))?o:m,null).id);
      if(suc.length) adj.push(suc.reduce((m,o)=>(!m||o.ini<m.ini||(o.ini===m.ini&&o.id<m.id))?o:m,null).id); });
    const vis=fora.filter(o=>!(nomes[o.faixa]||inteiro)||adj.indexOf(o.id)>=0).sort((x,y)=>(x.ini-y.ini)||(x.id<y.id?-1:(x.id>y.id?1:0)));
    let nl; if(!own.length) nl=vis.length<=1?1:1+vis.length; else if(own.length===1&&own[0].tipo!=='Parcela'&&!vis.length) nl=1; else nl=1+own.length+vis.length;
    const resid=T-A-livre-conf; const per=resid>0.005?Math.min(resid,fora.filter(o=>o.classe==='perene').reduce((s,o)=>s+o.area,0)):0;
    // excesso (SAF-C01): a maior soma certa acima da área nas travas de soma. Fica fora da partição da faixa (que soma T, R-09: a Perene vai
    // só até o resíduo) e aparece no texto da faixa, para a sobreposição não sumir no resumo
    const exc=ocR2(Math.max(0,tr.reduce((m,x)=>x[0]==='soma'?Math.max(m,x[4]):m,T)-T));
    const editavel=!safra.ro;
    const vinc=fora.filter(o=>o.classe==='perene'&&editavel&&!o.safs.some(s2=>safras[s2]&&ocDia(safras[s2].ini)<=b&&ocDia(safras[s2].fim)>=a)).map(o=>o.id);
    linhas.push({t,T,A:ocR2(A),sit,livre:ocR2(livre),conf:ocR2(conf),area_livre:ocR2(livre+conf),desde,est,own,fora,vis,seq,pend:pe,pend_own:pendOwn,trav:tr,exc,fix,linhas:nl,vinc,planejar:(livre+conf>0.005&&editavel)});
    band.nesta+=A; band.livre+=livre; band.conf+=conf; band.perene+=Math.max(per,0); band.ocup+=Math.max(resid-per,0); });
  Object.keys(band).forEach(k=>{ band[k]=ocR2(band[k]); });
  return [linhas,band]; }
function ocChips(linhas){ const c={}; linhas.forEach(v=>{ c[v.sit]=(c[v.sit]||0)+1; }); return c; }
function ocSucessoes(linhas){ return linhas.filter(v=>v.sit==='A conferir'&&v.conf<=0.005).length; }
function ocFaixaTxt(band,linhas,tot){ const p=['Nesta safra '+ocHa(band.nesta)].concat([['Livre','livre'],['A conferir','conf'],['Perene','perene'],['Ocupado','ocup']].filter(([r,k])=>band[k]>0.005).map(([r,k])=>r+' '+ocHa(band[k])));
  const s=ocSucessoes(linhas); const ex=ocR2(linhas.reduce((q,v)=>q+(v.exc||0),0));
  return p.join(' · ')+' · de '+ocHa(tot)+' ha'+(ex>0.005?' · '+ocHa(ex)+' ha em sobreposição':'')+(s===1?' · 1 sucessão a conferir':(s?' · '+s+' sucessões a conferir':'')); }
// ---------- salvar: trava, pendência nova e aviso (R-14, R-15) ----------
function ocPendNovas(antes,depois){ const out={}; const eq=(p,q)=>p.length===q.length&&p.every((x,i)=>x===q[i]);
  Object.keys(depois).forEach(k=>{ const n=depois[k].filter(p=>!(antes[k]||[]).some(q=>eq(p,q))); if(n.length) out[k]=n; }); return out; }
function ocChecar(ctx,safras,antes,depois,sid,alvo,T){ const occ=ocOcupacoes(ctx,safras,depois); const o=occ.find(x=>x.id===alvo);
  if(!o) return {trav:[],pend:{},aviso:[],o:null,mesmo:[]}; T=Number(T);
  const mesmo=occ.filter(x=>x.faz===o.faz&&x.t===o.t); let [trav,pe]=ocAvalia(ctx,mesmo,T,alvo);
  const soma=mesmo.filter(x=>x.safs.indexOf(sid)>=0).reduce((s,x)=>s+x.area,0); if(soma>T+0.005) trav=[['safra',sid,alvo,o.plantio,ocR2(soma)]].concat(trav);
  const occ0=ocOcupacoes(ctx,safras,antes); const pe0=ocAvalia(ctx,occ0.filter(x=>x.faz===o.faz&&x.t===o.t),T,null)[1];
  const aviso=mesmo.filter(y=>y!==o&&ocMesmaArea(o,y)&&(y.classe==='estimado'||y.classe==='semdata')&&y.ini<o.ini&&o.ini<ocLib(ctx,y,'pior'));
  return {trav,pend:ocPendNovas(pe0,pe),aviso,o,mesmo}; }
function ocTroca(cults,novo){ return cults.filter(c=>c.id!==novo.id).concat([novo]); }
function ocPlantioMin(ctx,safras,cults,sid,novo,desde,T,ate){ const t=novo.talhao||ocTalhaoDe(novo.faixa,novo.tipo);
  const base=cults.filter(c=>c.faz===novo.faz&&(c.talhao||ocTalhaoDe(c.faixa,c.tipo))===t&&c.id!==novo.id); const antes=base.concat(cults.filter(c=>c.id===novo.id));
  let d=desde+(novo.plano?ocAntecedencia(ctx,novo.plano):0); const fim=(ate!==undefined&&ate!==null)?ate:ocDia(safras[sid].fim);
  for(;d<=fim;d++){ const nv=Object.assign({},novo,{plantio:ocIso(d)}); const r=ocChecar(ctx,safras,antes,base.concat([nv]),sid,novo.id,T); if(!r.trav.length&&!Object.keys(r.pend).length) return d; }
  return null; }
// ---------- textos (OC-U4): fato, dano e saída ----------
const OC_FEM={'Soja':1};
const OC_FEM_ATV={'dessecação':1,'adubação':1,'colheita':1,'calagem':1,'gessagem':1,'fertirrigação':1,'poda':1,'sexagem':1,'pulverização':1,'aplicação':1};
function ocNomeCv(o){ return (o.cult+' '+String(o.var).replace('Híbrido ','')).trim(); }
function ocMinus(s){ return s?s.charAt(0).toLowerCase()+s.slice(1):s; }
function ocArt(c){ return OC_FEM[c]?'a':'o'; }
function ocDe(c){ return OC_FEM[c]?'da':'do'; }
function ocGen(c,masc){ return OC_FEM[c]?masc.slice(0,-1)+'a':masc; }
function ocPlanoNome(ctx,o){ return (o.plano&&ctx.planos[o.plano])?ctx.planos[o.plano].nome:''; }
function ocAtvEm(ctx,o,d){ if(!o.plano) return 'plantio'; const x=ocAtividades(ctx,o.plantio,o.plano,o.colh_inf).find(a=>a[2]===d); return x?ocMinus(x[0].split(' ')[0]):'plantio'; }
function ocAtvDo(ctx,o){ const a=ocAtvEm(ctx,o,o.ini); const pn=ocPlanoNome(ctx,o); return (OC_FEM_ATV[a]?'A':'O')+' '+a+' '+ocDe(o.cult)+' '+(pn||ocMinus(o.cult)); }
function ocPomar(cult){ return {'Café':'o cafezal','Mamão Formosa':'o pomar'}[cult]||'a lavoura perene'; }
function ocDaSafra(o,sid){ return o.safs.indexOf(sid)>=0?'desta safra':'da '+o.safnome; }
function ocDias(n){ return n+(n===1?' dia':' dias'); }
function ocMsgTrava(ctx,chk,sid,T,pmin){ const o=chk.o, tr=chk.trav; const by={}; chk.mesmo.forEach(x=>{ by[x.id]=x; }); const folga=ctx.folga; const tipos=tr.map(x=>x[0]);
  if(tipos.indexOf('safra')>=0||tipos.indexOf('soma')>=0){
    const outros=chk.mesmo.filter(x=>x!==o&&ocIntersec(o.ini,ocLib(ctx,o,'est'),x.ini,ocLib(ctx,x,'est')));
    if(outros.length){ const ini=ocMax([o.ini].concat(outros.map(x=>x.ini))); const fim=ocMin([o.fim!==null?o.fim:o.plantio].concat(outros.filter(x=>x.fim!==null).map(x=>x.fim)));
      // maior soma dos outros nos dias ini..ate: só muda no início e na liberação de cada um (SAF-C01; o laço dia a dia ia até 10^8 com perenes)
      const ate=ini+Math.max(1,fim-ini+1)-1; const pts=[ini].concat(outros.map(x=>x.ini),outros.map(x=>ocLib(ctx,x,'est'))).filter(d=>ini<=d&&d<=ate);
      const pior=ocMax(pts.map(d=>outros.filter(x=>x.ini<=d&&d<ocLib(ctx,x,'est')).reduce((q,x)=>q+x.area,0)));
      const quem=outros.map(x=>x.cult+' ('+x.faixa+', '+x.safnome+')').join(' e ');
      return (fim>=OC_INF?'A partir de '+ocBr(ini):'De '+ocBr(ini)+' a '+ocBr(fim))+', '+ocHa(pior)+' ha de '+o.t+' estão com '+quem+'. Máximo '+ocHa(Math.max(0,T-pior))+' ha nesse período.'; }
    const s=(tr.find(x=>x[0]==='safra')||[0,0,0,0,0])[4];
    return 'As áreas de '+o.t+' nesta safra somariam '+ocHa(s)+' ha; o talhão tem '+ocHa(T)+' ha (livre: '+ocHa(Math.max(0,T-(s-o.area)))+' ha).'; }
  const ob=tr.find(x=>x[0]==='observado');
  if(ob){ let Y=by[ob[1]], X=by[ob[2]]; if(Y===o){ const z=Y; Y=X; X=z; } const a=ocAtvDo(ctx,X);
    return ocArt(Y.cult).toUpperCase()+' '+ocNomeCv(Y)+' de '+Y.faixa+' foi '+ocGen(Y.cult,'colhido')+' em '+ocBr(Y.colh_real)+'; '+ocMinus(a.charAt(0))+a.slice(1)+' cai em '+ocBr(X.ini)+', com '+ocArt(Y.cult)+' '+ocMinus(Y.cult)+' em campo.'+((pmin!==null&&pmin!==undefined)?' Plantio a partir de '+ocBr(pmin)+' resolve.':''); }
  const fx=tr.find(x=>x[0]==='faixa');
  if(fx){ const a=by[fx[1]], b=by[fx[2]]; const outro=(a===o)?b:a;
    if(outro.classe==='perene') return outro.faixa+' tem '+outro.cult+' perene, sem fim registrado. O plano geraria insumo e O.S. sobre '+ocPomar(outro.cult)+'. O encerramento do ciclo ainda não existe no sistema.';
    if(o.classe==='perene') return outro.faixa+' tem '+outro.cult+' '+ocDaSafra(outro,sid)+' desde '+ocBr(outro.plantio)+'. O plano geraria insumo e O.S. sobre lavoura em campo.';
    const pri=outro.plantio<=o.plantio?outro:o, seg=(pri===outro)?o:outro; const cm=ctx.cicmin[pri.cult]; let base;
    if(pri.classe==='observado') base=ocGen(pri.cult,'colhido')+' em '+ocBr(pri.colh_real); else if(cm&&pri.nuc===pri.plantio+cm-1) base='ciclo mínimo '+ocDe(pri.cult)+' '+ocMinus(pri.cult)+', '+cm+' dias, CD-02'; else base='colheita prevista em '+ocBr(pri.fim);
    if(pri===outro) return pri.faixa+' está com '+ocNomeCv(pri)+' '+ocDaSafra(pri,sid)+', '+ocGen(pri.cult,'plantado')+' em '+ocBr(pri.plantio)+': ocupa a área até pelo menos '+ocBr(pri.nuc)+' ('+base+'). O plano geraria insumo e O.S. sobre lavoura em campo. Informe a colheita '+ocDe(pri.cult)+' '+ocMinus(pri.cult)+' ou plante a partir de '+ocBr(ocMais(pri.nuc,folga))+'.';
    return pri.faixa+': '+ocArt(pri.cult)+' '+ocNomeCv(pri)+' '+ocDaSafra(pri,sid)+', '+ocGen(pri.cult,'plantado')+' em '+ocBr(pri.plantio)+', ocupa a área até pelo menos '+ocBr(pri.nuc)+' ('+base+'), e '+ocArt(seg.cult)+' '+seg.cult+' '+ocDaSafra(seg,sid)+' começa em '+ocBr(seg.plantio)+'. O plano geraria insumo e O.S. sobre lavoura em campo.'; }
  return 'Sobreposição com outra ocupação do talhão.'; }
function ocMsgSemJanela(ctx,o,seg,baseLib,sid){ const ant=o.plano?ocAntecedencia(ctx,o.plano):0; const pl=baseLib+ant; let fim;
  if(o.plano){ const [ok]=ocDatasValidas(ctx,pl,o.plano,o.safini,o.safim,null); fim=ocMax([pl].concat(ok.map(x=>x[2]))); } else fim=ocFimEstimado(ctx,o.cult,o.var,pl)||pl;
  return o.faixa+' tem '+seg.cult+' '+ocDaSafra(seg,sid)+' a partir de '+ocBr(seg.plantio)+'. Para '+ocArt(o.cult)+' '+ocMinus(o.cult)+' com '+(ocPlanoNome(ctx,o)||'o plano')+' começar depois do cultivo anterior ('+ocBr(baseLib)+'), replaneje esse '+ocMinus(seg.cult)+' para '+ocBr(ocMais(fim,ctx.folga))+' ou depois.'; }
function ocMsgPend(ctx,chk,sid,pmin){ const o=chk.o; const by={}; chk.mesmo.forEach(x=>{ by[x.id]=x; }); if(!Object.keys(chk.pend).length) return '';
  if(chk.pend[o.id]){ const p=chk.pend[o.id][0];
    if(p[0]==='soma') return o.t+': a soma prevista das áreas passa da área do talhão de '+ocBr(p[2])+' a '+ocBr(p[3])+' ('+ocDias(p[4])+').';
    const A=by[p[1]];
    return o.faixa+': sobreposição prevista de '+ocDias(p[4])+'. '+ocAtvDo(ctx,o)+' cai em '+ocBr(o.ini)+' e '+ocArt(A.cult)+' '+ocNomeCv(A)+' ('+A.safnome+') está '+ocGen(A.cult,'previsto')+' até '+(A.fim!==null?ocBr(A.fim):'sem data')+'. '+((pmin!==null&&pmin!==undefined)?'Mude o plantio para '+ocBr(pmin)+' ou depois, ':'Mude o plantio ')+'ou confirme a colheita '+ocDe(A.cult)+' '+ocMinus(A.cult)+'.'; }
  const k=Object.keys(chk.pend)[0], p=chk.pend[k][0], B=by[k];
  if(p[0]==='soma') return o.t+': a soma prevista das áreas passa da área do talhão de '+ocBr(p[2])+' a '+ocBr(p[3])+' ('+ocDias(p[4])+').';
  return o.faixa+': a colheita prevista '+ocDe(o.cult)+' '+o.cult+' passa para '+ocBr(o.fim)+', depois do plantio '+ocDe(B.cult)+' '+B.cult+' da '+B.safnome+' ('+ocBr(B.plantio)+'). Sobreposição prevista de '+ocDias(p[4])+'.'; }
function ocMsgAviso(ctx,chk){ const o=chk.o; return chk.aviso.map(y=>{ const pe=(chk.pend[o.id]||[]).filter(p=>p[1]===y.id);
  if(y.classe==='semdata') return 'saída '+ocDe(y.cult)+' '+ocMinus(y.cult)+' não conferida';
  if(pe.length) return 'provável sobreposição ('+ocDias(pe[0][4])+') com '+ocArt(y.cult)+' '+ocMinus(y.cult)+' da '+y.safnome;
  return 'saída '+ocDe(y.cult)+' '+ocMinus(y.cult)+' estimada em '+ocBr(y.fim)+'; confirme a colheita'; }).join('; '); }
function ocPendCurta(ctx,o,p,by){ if(p[0]==='soma') return 'Soma prevista acima da área: '+ocDias(p[4])+' ('+ocDdmm(p[2])+' a '+ocDdmm(p[3])+')';
  const A=by[p[1]]; return 'Sobreposição prevista: '+ocDias(p[4])+' ('+ocAtvEm(ctx,o,o.ini)+' '+ocDdmm(o.ini)+' × '+ocMinus(A.cult)+' até '+(A.fim!==null?ocDdmm(A.fim):'sem data')+')'; }
