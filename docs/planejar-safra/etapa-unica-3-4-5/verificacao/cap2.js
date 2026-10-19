// Oráculo da v2 (SAF etapa única): capSaf proposto sobre o motor real (saf_body.js = safra.js de 884620c).
// Regras aplicadas: demanda por item = x.nh × rc[k] (R-07/MN-01), necessárias = max(teto(h ÷ h de 1 unidade), maior rc[k] em uso no mês) (MN-01),
// soma das outras safras abertas da mesma fazenda (P02), classificação antes/fora/depois (MN-03), fmtOcup "<1 %" se 0<o<1 (MN-11).
const {X,mk}=require('../motor345/h.js');
const nf=(x,d=1)=>Number(x).toLocaleString('pt-BR',{minimumFractionDigits:d,maximumFractionDigits:d});
const MES=['jan','fev','mar','abr','mai','jun','jul','ago','set','out','nov','dez'];
const mlabDt=(dt)=>MES[Number(dt.slice(5,7))-1]+'/'+dt.slice(2,4);
const fmtOcup=(o)=>o===null?'não calculável':(o<=0?'—':(o<1?'<1 %':nf(Math.round(o),0)+' %'));
function safRows(s){ return X.g2rows(s,X.GR('g_saf')); }
function outrasSafras(s,saf){ const rows=safRows(s); const me=rows.find(r=>r.id===saf); const faz=(me&&me.v.faz)||'Santa Rita';
  return rows.filter(r=>r.id!==saf&&!r.ro&&(r.v.faz||'Santa Rita')===faz).map(r=>r.id); }
function recursos(s){ const M=X.g2rows(s,X.GR('g_recp_maq')), P=X.g2rows(s,X.GR('g_recp_pes'));
  return M.map(r=>[r,false]).concat(P.map(r=>[r,true])).map(([r,pes])=>{ const pc=k=>Math.min(100,Math.max(0,Number(r.v[k])||0))/100;
    const un=Number(r.v.un)||0, J=Number(r.v.jornada)||0, T=pes?1:(Number(r.v.turnos)||0), DP=pes?1-pc('abs'):pc('disp');
    return {id:r.id,nome:r.v.nome,pes,un,porUn:X.D2.meses.map(m=>(X.D2.dias[m[0]]||0)*J*T*DP)}; }); }
// carga do recurso k numa ocorrência: Σ por configuração de x.nh × rc[k] (necessário = atendido + saldo); semHoras marca "≥"
function cargaItens(i){ const o=[]; i.rp.itens.forEach((x,j)=>{ const rc=(i.cfs[j]&&i.cfs[j].rec)||{};
  Object.keys(rc).forEach(k=>{ const u=Number(rc[k])||0; if(u<=0) return; o.push({k,j,u,h:(x.nh||0)*u,ha:(x.h||0)*u,sim:x.nq>1e-12?u:0,semRec:!!x.semRec,x}); }); }); return o; }
function cargaRec(i,k){ return cargaItens(i).filter(c=>c.k===k).reduce((a,c)=>a+c.h,0); }
function classe(s,saf,i){ const r=safRows(s).find(q=>q.id===saf)||{v:{}}; const ini=r.v.ini||'', fim=r.v.fim||'';
  if(ini&&i.dt<ini) return 'antes'; if(fim&&i.dt>fim) return 'depois'; if(i.mi<0) return 'fora'; return 'cal'; }
function capSaf(s,saf){ const R=recursos(s); const G={}; const Z=()=>Array(12).fill(0);
  R.forEach(r=>{ G[r.id]=Object.assign(r,{cap:r.porUn.map(p=>r.un*p),dThis:Z(),dThisAt:Z(),dOth:Z(),oth:{},sim:Z(),semH:Z(),pendSR:Z()}); });
  const oc=X.ocorr(s,saf); const outs=outrasSafras(s,saf); const ocO={}; outs.forEach(o=>{ ocO[o]=X.ocorr(s,o); });
  const add=(i,own,sid)=>{ if(i.mi<0) return; cargaItens(i).forEach(c=>{ const g=G[c.k]; if(!g) return;
      if(own){ g.dThis[i.mi]+=c.h; g.dThisAt[i.mi]+=c.ha; if(c.semRec) g.pendSR[i.mi]++; } else { g.dOth[i.mi]+=c.h; (g.oth[sid]||(g.oth[sid]=Z()))[i.mi]+=c.h; }
      g.sim[i.mi]=Math.max(g.sim[i.mi],c.sim); });
    if(i.rp.falta.semHoras>1e-9) cargaItens(i).forEach(c=>{ if(G[c.k]&&own) G[c.k].semH[i.mi]+=i.rp.falta.semHoras; }); };
  oc.forEach(i=>add(i,true,saf)); outs.forEach(o=>ocO[o].forEach(i=>add(i,false,o)));
  Object.values(G).forEach(g=>{ g.cells=X.D2.meses.map((m,mi)=>{ const d=g.dThis[mi]+g.dOth[mi]; const cap=g.cap[mi];
      const nec=d>1e-4?Math.max(Math.ceil(d/g.porUn[mi]-1e-9),g.sim[mi]):0; const necThis=g.dThis[mi]>1e-4?Math.max(Math.ceil(g.dThis[mi]/g.porUn[mi]-1e-9),g.sim[mi]):0;
      return {mi,mes:m[1],d,dThis:g.dThis[mi],dOth:g.dOth[mi],cap,ocup:d>1e-4?(cap>0?100*d/cap:null):0,nec,red:d>1e-4&&nec>g.un,soma:nec>g.un&&!(necThis>g.un),own:g.dThis[mi]>1e-4,ge:g.semH[mi]>1e-9}; });
    const own=g.cells.filter(c=>c.own&&c.ocup!==null); g.max=own.reduce((b,c)=>(!b||c.ocup>b.ocup+1e-12)?c:b,null);
    g.reds=g.cells.filter(c=>c.own&&c.red); g.necMax=g.reds.reduce((b,c)=>(!b||c.nec>b.nec)?c:b,null);
    g.horasSafra=g.dThis.reduce((a,b)=>a+b,0); g.horasSafraAt=g.dThisAt.reduce((a,b)=>a+b,0); });
  return {G,oc,ocO,outs}; }
// atividades em uso sem janela (P07/R-02/MN-07): por atividade, alguma configuração com área necessária e janela vazia
function janelas(oc){ const A={}; oc.forEach(i=>{ if(i.mi<0) return; const key=i.a.op+'|'+i.a.nome; const a=A[key]||(A[key]={sem:false,com:false});
  i.rp.itens.forEach(x=>{ if(x.nq>1e-12){ if(isFinite(x.Hin)) a.com=true; else a.sem=true; } }); });
  const ks=Object.keys(A); return {M:ks.length,J:ks.filter(k=>A[k].sem).length,ops:new Set(ks.map(k=>k.split('|')[0])).size}; }
function situacao(i,G){ const pend=i.pend||i.saldo>1e-9||i.rp.conflito||(!i.pend&&!i.rp.custoOk);
  const capRed=i.mi>=0&&cargaItens(i).some(c=>G[c.k]&&G[c.k].cells[i.mi].red);
  if(pend||capRed) return 'Com pendência'; const sem=i.rp.itens.some(x=>x.nq>1e-12&&!isFinite(x.Hin)); return sem?'Janela não informada':'Cabe na janela'; }
function totais(s,saf,oc){ const S=(l,f)=>l.reduce((a,i)=>a+(Number(i[f])||0),0); const cls={antes:[],fora:[],depois:[],cal:[]}; oc.forEach(i=>cls[classe(s,saf,i)].push(i));
  const oper=(l,f)=>l.filter(i=>i.mi>=0).reduce((a,i)=>a+cargaItens(i).filter(c=>c.k==='oper').reduce((b,c)=>b+c[f],0),0);
  const t=(l)=>({n:l.length,ha:S(l,'area'),h:S(l,'horas'),cop:S(l,'cop'),cins:S(l,'cins'),hh:S(l,'hh'),diesel:S(l,'diesel'),pend:l.filter(i=>i.pend).length,saldo:S(l,'saldo'),
    falta:l.reduce((a,i)=>a+(i.rp.falta.hconj||0),0),semDiesel:l.filter(i=>i.rp.itens.some(x=>x.q>0&&x.d===null)).length});
  return {all:t(oc),antes:t(cls.antes),fora:t(cls.fora),depois:t(cls.depois),cal:t(cls.cal),operDem:oper(oc,'h'),operAt:oper(oc,'ha')}; }
function resumoCultura(s,saf,oc){ const by={}; const vistos={};
  oc.forEach(i=>{ const c=i.c.v.cult; const b=by[c]||(by[c]={cult:c,area:0,cop:0,cins:0,npend:0,ntar:0,copAntes:0,cinsAntes:0}); if(!vistos[i.c.id]){ vistos[i.c.id]=1; b.area+=i.area; }
    b.cop+=i.cop||0; b.cins+=i.cins; if(i.pend) b.npend++; else if(!i.rp.custoOk) b.ntar++; if(classe(s,saf,i)==='antes'){ b.copAntes+=i.cop||0; b.cinsAntes+=i.cins; } });
  Object.values(by).forEach(b=>{ b.tot=b.cop+b.cins; b.rha=(b.npend||b.ntar)?null:b.tot/b.area; b.rhaTodas=b.tot/b.area; b.rhaSemAntes=(b.tot-b.copAntes-b.cinsAntes)/b.area; }); return by; }
function nomeRec(g){ return g.nome; }
function veredito(s,saf,cs){ const {G,oc}=cs; const cult=X.cultRows(s,saf); const sp=cult.filter(c=>{ const pl=X.D2.planos?null:null; return !c.v.plano; });
  const comPlano=cult.filter(c=>c.v.plano); const aPlano=comPlano.reduce((a,c)=>a+(Number(c.v.area)||0),0), aTot=cult.reduce((a,c)=>a+(Number(c.v.area)||0),0);
  const sem=cult.filter(c=>!c.v.plano); const cal=oc.filter(i=>i.mi>=0); const tot=totais(s,saf,oc); const jn=janelas(oc);
  const fora=[]; if(sem.length) fora.push(sem.map(c=>c.v.local).join(', ').replace(/, ([^,]*)$/,' e $1')+' ('+nf(sem.reduce((a,c)=>a+(Number(c.v.area)||0),0),0)+' ha), sem plano');
  if(tot.antes.n) fora.push(tot.antes.n+' ocorrências antes do início da safra');
  if(tot.fora.n) fora.push(tot.fora.n+' ocorrências fora do calendário');
  const reds=Object.values(G).filter(g=>g.reds.length).sort((a,b)=>(b.necMax.nec/Math.max(b.un,1e-9))-(a.necMax.nec/Math.max(a.un,1e-9)));
  const pend=oc.filter(i=>i.pend||i.saldo>1e-9).length; const outros=oc.filter(i=>(i.pend&&i.rp.causa!=='sem recurso na fazenda')||(!i.pend&&i.saldo>1e-9)||i.rp.conflito||(!i.pend&&!i.rp.custoOk)).length;
  let R,cor,txt; const suf=jn.J?' Prazo por talhão não verificado: '+jn.J+' de '+jn.M+' atividades sem janela.':'';
  if(!comPlano.length){ R='R0'; }
  else if(!cal.length){ R='R1'; cor='cinza'; txt='Capacidade não calculada: as '+oc.length+' ocorrências desta safra ficam fora do calendário do protótipo (set/26 – ago/27).'; }
  else if(reds.length){ R='R2'; cor='vermelho'; txt='Falta recurso: '+reds.map((g,ix)=>{ const c=g.necMax; const somaO=g.reds.every(x=>x.soma)?', somando '+Object.keys(g.oth).map(o=>safRows(s).find(r=>r.id===o).v.nome+' ('+nf(g.oth[o][c.mi],1)+' h)').join(' e '):'';
      return (ix===0?g.nome+(g.pes||/s$/.test(g.nome)?' precisam de ':' precisa de '):g.nome+', ')+c.nec+' em '+c.mes+' e você tem '+g.un+(g.reds.length>1?' ('+g.reds.length+' meses)':'')+somaO; }).join('; ')+'.'
      +(pend?' Inclui '+pend+' ocorrências ainda sem alocação.':''); }
  else if(outros){ R='R3'; cor='âmbar'; txt='Cálculo incompleto: …'; }
  else if(fora.length){ R='R4'; cor='âmbar'; txt='Na estimativa mensal, cabe nos '+nf(aPlano,0)+' ha com plano.'+suf; }
  else { R='R5'; cor='verde'; txt='Na estimativa mensal, cabe com o que você tem.'+suf; }
  if(R==='R2'||R==='R4'||R==='R3') if(fora.length) txt+=' Fora da conta: '+fora.join('; ')+'.';
  return {R,cor,txt,aPlano,aTot,jn}; }
module.exports={X,mk,nf,fmtOcup,mlabDt,capSaf,cargaRec,cargaItens,classe,janelas,situacao,totais,resumoCultura,veredito,outrasSafras,safRows,recursos};
