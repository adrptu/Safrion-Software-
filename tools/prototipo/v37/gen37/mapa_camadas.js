// EX55 D2: extração em andamento da base 29d923c7; funções puras.
// Recebe somente ordens já recortadas pelo adaptador da tela.
const mc_FASES=['A liberar','Liberadas','Em execução','Em conferência','Encerradas'];
const mc_FASEC={'A liberar':'gray','Liberadas':'blue','Em execução':'ok','Em conferência':'yellow','Encerradas':'gray'};
const mc_FASE1={'Liberadas':'Liberada','Encerradas':'Encerrada'};
const mc_PZC={'atrasada':'red','vence hoje':'orange','até 3 dias':'yellow','no prazo':'ok','irrigando hoje':'blue','encerrada':'gray'};
const mc_SEV=['red','orange','yellow','cloud','lime','ok','good','navy','blue','purple','gray','none'];
function mc_osAb(os){ return os.filter(o=>o.fase!=='Encerradas'&&o.fase!=='Canceladas'); }   // abertas: sem Encerradas nem Canceladas (Codex 6216014054: cancelada não entra no Avanço nem nos números)
function mc_osImp(o){ return o.selos.some(s=>s[1]==='red'); }
function mc_osSemAb(os){ return os.length&&os.every(o=>o.fase==='Canceladas')?'cancelada':'encerrada'; }   // rótulo quando não há ordem aberta
function mc_worstC(cs){ let b='none',bi=99; cs.forEach(c=>{ const i=mc_SEV.indexOf(c); if(i>=0&&i<bi){ bi=i; b=c; } }); return b; }
function mc_nfx(n,d){ return Number(n||0).toLocaleString('pt-BR',{minimumFractionDigits:d||0,maximumFractionDigits:d||0}); }
function mcOS(os,f){ if(!os.length) return {c:'none',l:'sem ordem'+(f.fase==='Todas'?'':' na fase')};
  const mais=(n)=>n>1?' · +'+(n-1):'';
  if(f.ver==='Atrasos'){ const c=mc_worstC(os.map(o=>mc_PZC[o.pz])); const o=os.find(x=>mc_PZC[x.pz]===c); return {c,l:o.id+' · '+o.pz+mais(os.length)}; }
  const ab=mc_osAb(os);
  if(f.ver==='Impedimentos'){ if(!ab.length) return {c:'none',l:mc_osSemAb(os)}; const im=ab.filter(mc_osImp), pe=ab.filter(o=>!mc_osImp(o)&&o.selos.length);
    if(im.length) return {c:'red',l:im[0].id+' · '+im[0].selos.find(s=>s[1]==='red')[0].toLowerCase()+mais(im.length)};
    if(pe.length) return {c:'yellow',l:pe[0].id+' · '+pe[0].selos[0][0].toLowerCase()+mais(pe.length)};
    return {c:'ok',l:'sem impedimento'}; }
  if(f.ver==='Avanço'){ const xs=ab.filter(o=>o.area>0); if(!xs.length) return {c:'none',l:ab.length?'sem área a executar':mc_osSemAb(os)};
    const a=xs.reduce((s,o)=>s+o.area,0), r=xs.reduce((s,o)=>s+Math.min(o.rz||0,o.area),0), p=r/a*100;
    return {c:p<=0?'gray':(p>=99.95?'good':'lime'),l:mc_nfx(r,r%1?1:0)+'/'+mc_nfx(a)+' ha · '+mc_nfx(p,0)+' %'+(xs.length>1?' · '+xs.length+' ordens':'')}; }
  const n={}; os.forEach(o=>{ n[o.fase]=(n[o.fase]||0)+1; }); const fs=mc_FASES.filter(x=>n[x]); const f0=fs.find(x=>x!=='Encerradas')||fs[0]||'';
  const nm=(x,k)=>(k===1?(mc_FASE1[x]||x):x).toLowerCase();   // uma ordem: "liberada", "encerrada"
  return {c:mc_FASEC[f0]||'gray',l:os.length===1?os[0].id+' · '+nm(os[0].fase,1):fs.map(x=>n[x]+' '+nm(x,n[x])).join(' · ')}; }

function mcOSLeg(f){
  if(f.ver==='Atrasos') return [mcLegenda('red','atrasada'),mcLegenda('orange','vence hoje'),mcLegenda('yellow','até 3 dias'),mcLegenda('ok','no prazo'),mcLegenda('gray','encerrada'),mcLegenda('none','sem ordem')];
  if(f.ver==='Impedimentos') return [mcLegenda('red','impedida ou conflito'),mcLegenda('yellow','pendência com dono'),mcLegenda('ok','sem impedimento'),mcLegenda('none','sem ordem aberta')];
  if(f.ver==='Avanço') return [mcLegenda('gray','não iniciada'),mcLegenda('lime','em andamento'),mcLegenda('good','área toda feita'),mcLegenda('none','sem ordem aberta')];
  return [mcLegenda('gray','a liberar · encerradas'),mcLegenda('blue','liberadas'),mcLegenda('ok','em execução'),mcLegenda('yellow','em conferência'),mcLegenda('none','sem ordem')]; }

function mcLegenda(k,t){return {k,t};}
// vs: vistorias já recortadas/ordenadas, com alvo resolvido pelo adaptador.
// ctx.alvos: null sem filtro; interseção filtro/protocolos quando filtrado.
function mcMIP(vs,ctx){
 if(!vs.length){
  if(ctx.semProt)return {c:'none',l:'sem cultura'};
  if(ctx.alvos!==null){
   if(!ctx.alvos.length)return {c:'none',l:'sem '+ctx.alvTxt+' no protocolo'};
   return {c:'gray',l:'sem vistoria de '+ctx.alvTxt+' em '+ctx.dias+' dias'};
  }
  return {c:'gray',l:ctx.atras?('vistoria atrasada '+ctx.atras+(ctx.atras>1?' dias':' dia')):'sem vistoria em '+ctx.dias+' dias'};
 }
 const x=vs[0];return {c:x.S.mc,l:x.alvo+' · '+x.S.t.charAt(0).toLowerCase()+x.S.t.slice(1)+(vs.length>1?' · +'+(vs.length-1):'')};
}
function mcMIPLeg(){return [['red','acima do NC'],['orange','foco'],['yellow','perto do NC ou coleta pendente'],['blue','em controle'],['lime','programada'],['ok','abaixo do NC'],['gray','vistoria atrasada ou sem vistoria no período'],['none','sem cultura']].map(x=>mcLegenda(x[0],x[1]));}

const MC_COR={"ok":["#7FAE68","#FFFFFF"],"good":["#5F8F55","#FFFFFF"],"lime":["#A9C06A","#FFFFFF"],"yellow":["#D4B25A","#FFFFFF"],"orange":["#D98A4E","#FFFFFF"],"red":["#C8553D","#FFFFFF"],"gray":["#C9CFCB","#FFFFFF"],"blue":["#6E9FC6","#FFFFFF"],"navy":["#44739A","#FFFFFF"],"none":["#E4E9DF","#FFFFFF"],"cloud":["#C9CFCB","#FFFFFF"],"purple":["#9B8BC4","#FFFFFF"],"sat":["#C9CFCB","#FFFFFF"]};
function mc_irrRecTxt(x){ const r=x&&x.rec; if(!r||!(r.br>0.05)) return ''; return (r.np>1?r.np+'× '+mc_nfx(r.pct?r.lamP:r.por,1):mc_nfx(r.pct?r.lamP:r.por,1))+' mm'+(r.pct?' a '+r.pct+' %':''); }
function mcIrr(x,ver){ if(!x) return {c:'none',l:''};
    if(ver==='Balanço hídrico'){ if(x.d===null) return {c:'gray',l:x.l}; const rt=mc_irrRecTxt(x); const cd=x.d<5?'ok':(x.d<10?'yellow':(x.d<15?'orange':'red'));
      if(x.est) return {c:cd,est:true,l:'≈ '+mc_nfx(x.d,1)+' mm · estimado'+(rt?' → '+rt:'')};
      return {c:cd,l:'déficit '+mc_nfx(x.d,1)+' mm'+(rt?' → '+rt:'')}; }
    return {c:x.c==='cloud'?'ok':x.c,est:x.c==='cloud',l:x.l}; }
function mcIrrLeg(ver){ const ETQ={k:null,t:'≈ = estimado por ET (sonda sem dado ou suspeita)'};   // NC10: etiqueta de origem, não classe de cor
    return ver==='Balanço hídrico'?[mcLegenda('ok','déficit < 5 mm'),mcLegenda('yellow','5–10 mm'),mcLegenda('orange','10–15 mm'),mcLegenda('red','≥ 15 mm'),mcLegenda('gray','sequeiro ou preparo'),ETQ]
    :[mcLegenda('blue','irrigando'),mcLegenda('lime','programada'),mcLegenda('yellow','pendente: janela, conferência ou liberação'),mcLegenda('red','impedida ou conflito'),mcLegenda('ok','sem necessidade hoje'),mcLegenda('gray','sequeiro ou preparo'),ETQ]; }
