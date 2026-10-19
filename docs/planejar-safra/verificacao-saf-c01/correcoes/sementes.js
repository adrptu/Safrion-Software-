// Verificador · base × HEAD nas sementes (Santa Rita, Boa Vista, Lagoa Grande): ocTabela de cada safra + novas, ocChecar sem mudança e com área +10 % de cada cultivo.
const fs=require('node:fs'), vm=require('node:vm');
const F=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
function carrega(src){ const sb={}; vm.createContext(sb); vm.runInContext(fs.readFileSync(src,'utf8')+'\n;globalThis.X={ocCtx,ocOcupacoes,ocTabela,ocChecar,ocFaixaTxt,ocChips,ocMsgTrava,ocMsgPend,ocPlantioMin,ocDia};',sb); return sb.X; }
const V={base:carrega(process.argv[3]),head:carrega(process.argv[4])};
const NOV=[['N5','Nova (caso 5)','2027-01-10','2027-08-30','Santa Rita'],['N28','Nova 2027/28','2027-09-01','2028-08-31','Santa Rita'],['NBV','Nova Boa Vista','2026-09-01','2027-08-31','Boa Vista'],
 ['NLG28','Nova Lagoa 2027/28','2027-09-01','2028-08-31','Lagoa Grande'],['NLG27','Nova Lagoa 2026/27','2026-09-01','2027-08-31','Lagoa Grande'],['N40','Nova 2040','2040-01-01','2040-12-31','Santa Rita'],['NLG40','Lagoa 2040','2040-01-01','2040-12-31','Lagoa Grande']];
const SEM=['S2627','S27SF','S2526','LG2627'];
const res={base:{},head:{}};
for(const k of ['base','head']){ const X=V[k];
  for(const folga of [1,0]){ const ctx=X.ocCtx(F.ctx.culturas,F.ctx.cultivares,F.ctx.planos,folga);
    const safs=JSON.parse(JSON.stringify(F.safras)); NOV.forEach(([id,nome,ini,fim,faz])=>{ safs[id]={id,nome,ini,fim,faz,ro:false}; });
    const occ=X.ocOcupacoes(ctx,safs,F.cults);
    SEM.concat(NOV.map(x=>x[0])).forEach(sid=>{ const s=safs[sid]; const tal=F.talhoes[s.faz]; const [L,b]=X.ocTabela(ctx,s,occ,tal,safs);
      res[k]['tab '+sid+' f'+folga]={faixa:X.ocFaixaTxt(b,L,tal.reduce((q,x)=>q+x[1],0)),chips:X.ocChips(L),linhas:L.map(v=>[v.t,v.sit,v.livre,v.conf,v.desde,v.trav,v.pend,v.planejar,v.vinc])}; });
    F.cults.forEach(c=>{ const T=F.talhoes[c.faz].find(x=>x[0]===c.talhao); if(!T) return;
      [['igual',c],['+10%',Object.assign({},c,{area:Math.round(c.area*110)/100})],['+60%',Object.assign({},c,{area:Math.round(c.area*160)/100})]].forEach(([rot,nc])=>{
        const dep=F.cults.map(x=>x.id===c.id?nc:x); const r=X.ocChecar(ctx,safs,F.cults,dep,c.saf,c.id,T[1]);
        res[k]['chk '+c.id+' '+rot+' f'+folga]={trav:r.trav,pend:r.pend,mt:r.trav.length?X.ocMsgTrava(ctx,r,c.saf,T[1],null):'',mp:X.ocMsgPend(ctx,r,c.saf,null)}; }); });
  } }
const dif=Object.keys(res.base).filter(k=>JSON.stringify(res.base[k])!==JSON.stringify(res.head[k]));
console.log('casos',Object.keys(res.base).length,'diferentes',dif.length);
dif.slice(0,12).forEach(k=>{ console.log('==',k); console.log(' base',JSON.stringify(res.base[k]).slice(0,700)); console.log(' head',JSON.stringify(res.head[k]).slice(0,700)); });
