// CTL-5 · E2 (RL-E3) · AG-07 só consulta: "Usar na O.S." leva produto da fazenda, cultura e alvo à ordem A liberar da cultura; o registro
// (produto, dose, alvo e quem aprovou) só nasce na O.S., pela trava legal única do CTL-1. Executor: usar_os_unit_test.py (node, sem navegador).
// Na base 99537ca não existem carCult nem agOsCand e o alvo não chega à O.S.: os casos falham (stubs abaixo evitam parar no 1º).
const R=[]; const ok=(n,c,info)=>{ R.push(!!c); console.log((c?'OK    ':'FALHA ')+n+(c?'':' · '+String(JSON.stringify(info)).slice(0,500))); };
const T=(f)=>{ try{ const r=f(); return {ok:true,msg:r&&r.msg}; }catch(e){ return {ok:false,msg:e.message}; } };
const C=()=>cenClone(CEN0);
if(typeof carCult!=='function') globalThis.carCult=()=>'';
if(typeof agOsCand!=='function') globalThis.agOsCand=()=>[];
const ids=(L)=>L.map(o=>o.id).join(',');

// ---- U1 · cultura da ordem: uma regra só (carCult) para a trava legal da O.S. e para os candidatos do AG-07
{ const c=C(); const lin=[]; Object.values(c.ordens).forEach(o=>carTals(o.talhao).forEach(t=>lin.push([o.id,t.tid,carCult(o,t.tid),CARD.tal[t.tid].cult])));
  ok('U1 semente: cultura de cada talhão das '+Object.keys(c.ordens).length+' ordens = a do talhão no cadastro ('+lin.length+' pares)', lin.length>20&&lin.every(x=>x[2]===x[3]), lin.filter(x=>x[2]!==x[3]).slice(0,4)); }
{ const c=C(); osc_nova(c,{id:'OS-0440',tipo:'Herbicida pós-emergente',talhao:'T1-A',area:160,versao:'v1',resp:'Marcos',ins:[],selos:[]}); const o=c.ordens['OS-0440']; o.osc.novo.cultura='Milho safrinha';
  ok('U2 ordem nova da safrinha no T1-A: cultura do cultivo (Milho), não a do talhão (Soja)', carCult(o,'T1')==='Milho', carCult(o,'T1'));
  ok('U3 AG-07: a ordem nova de milho é candidata em Milho e não em Soja', ids(agOsCand(c,'Milho'))==='OS-0440'&&ids(agOsCand(c,'Soja')).indexOf('OS-0440')<0, [ids(agOsCand(c,'Milho')),ids(agOsCand(c,'Soja'))]); }

// ---- U4 · candidatos do AG-07: só O.S. A liberar (não OB, não liberada) da cultura escolhida
{ const c=C(); const s=ids(agOsCand(c,'Soja')), m=ids(agOsCand(c,'Mamão')), f=ids(agOsCand(c,'Feijão')), mi=ids(agOsCand(c,'Milho')), ca=ids(agOsCand(c,'Café'));
  ok('U4 semente: Soja = OS-0430, OS-0431 · Mamão = OS-0501, OS-0502, OS-0511 · Feijão = OS-0418 · Milho e Café = nenhuma', s==='OS-0430,OS-0431'&&m==='OS-0501,OS-0502,OS-0511'&&f==='OS-0418'&&mi===''&&ca==='', [s,m,f,mi,ca]); }
{ const c=C(); const r=T(()=>osc_liberar(c,'OS-0430',false,'','Ana'));
  ok('U5 liberada sai da lista: depois de liberar a OS-0430, Soja = OS-0431', r.ok&&ids(agOsCand(c,'Soja'))==='OS-0431', [r,ids(agOsCand(c,'Soja'))]); }

// ---- U6 · caminho normal: Tebuconazol 200 EC (Consulta Agrofit: mamão × antracnose) incluído na OS-0501 com 0,8 L/ha
{ const c=C(); const o0=c.ordens['OS-0501'], a0=o0.area, v0=o0.versao;
  const r=T(()=>osc_ajustar(c,'OS-0501',a0,{},'',[],[{p:'Tebuconazol 200 EC',dose:0.8,un:'L',g:'Fungicida',alvo:'antracnose'}],true,'Ana'));
  const o=c.ordens['OS-0501'], x=(o.ins||[]).find(y=>y.p==='Tebuconazol 200 EC')||{}, ev=((o.osc||{}).ev||[]), aj=((o.osc||{}).aj||[]);
  const c42=ev.find(e=>e.cmd==='CMD-42')||{}, c06=ev.find(e=>e.cmd==='CMD-06')||{};
  ok('U6 incluir pela O.S. libera a v2 com o alvo: ins.alvo, linha da versão "incluído Tebuconazol 200 EC 0,8 L/ha para antracnose"', r.ok&&o.etapa==='Liberadas'&&x.alvo==='antracnose'
     &&aj.some(h=>/incluído Tebuconazol 200 EC 0,8 L\/ha para antracnose/.test(h.t)), [r,o.etapa,x,aj.map(h=>h.t)]);
  ok('U7 a aprovação (CMD-42) grava produto, dose e alvo; a liberação (CMD-06) fica separada', /aprovada por Ana \(agrônoma\).*Tebuconazol 200 EC 0,8 L\/ha para antracnose/.test(c42.t||'')&&/liberada por/.test(c06.t||''), [c42.t,c06.t]);
  ok('U8 total pela regra única: 0,8 L/ha × '+cenNum(a0)+' ha', Math.abs(x.tot-cenQtd(0.8,a0))<1e-9, [x.tot,cenQtd(0.8,a0)]); }

// ---- U9..U12 · recusas pela mesma gravação atômica da tela (cenMudar, como osRun): nada é gravado
const nada=(id,o0)=>{ const o=cenGet().ordens[id]; return o.etapa==='A liberar'&&o.versao===o0.versao&&JSON.stringify(o.ins)===JSON.stringify(o0.ins)&&!((o.osc||{}).ev||[]).length&&!((o.osc||{}).aj||[]).length; };
const M=(fn)=>cenMudar(null,fn);
{ cenReset(); const o0=JSON.parse(JSON.stringify(cenGet().ordens['OS-0430']));
  const r=M(c=>osc_ajustar(c,'OS-0430',o0.area,{},'',[],[{p:'Abamectina 18 EC',dose:0.5,un:'L',g:'Inseticida',alvo:'ácaro-rajado'}],true,'Ana'));
  ok('U9 RECUSA trava legal (a do CTL-1): Abamectina 18 EC na soja → "sem registro para soja"; nada gravado', /sem registro para soja/.test(r.erro||'')&&nada('OS-0430',o0), r); }
{ cenReset(); const o0=JSON.parse(JSON.stringify(cenGet().ordens['OS-0501']));
  const r=M(c=>osc_ajustar(c,'OS-0501',o0.area,{},'',[],[{p:'Tebuconazol 200 EC',dose:3,un:'L',g:'Fungicida',alvo:'antracnose'}],true,'Ana'));
  ok('U10 RECUSA dose fora da bula: Tebuconazol 3 L/ha no mamão → "dose fora da bula: 0,5–1 L/ha"; nada gravado', /dose fora da bula: 0,5–1 L\/ha/.test(r.erro||'')&&nada('OS-0501',o0), r); }
{ cenReset(); const o0=JSON.parse(JSON.stringify(cenGet().ordens['OS-0501']));
  const r=M(c=>osc_ajustar(c,'OS-0501',o0.area,{},'',[],[{p:'Tebuconazol 200 EC',dose:0.8,un:'L',g:'Fungicida',alvo:'antracnose'}],true,'Caio'));
  ok('U11 RECUSA sem o papel: Caio (PCP) não inclui produto (decisão do agrônomo); nada gravado', !!r.erro&&nada('OS-0501',o0), r); }
{ cenReset(); const a=cenGet().ordens['OS-0501'].area, add=[{p:'Tebuconazol 200 EC',dose:0.8,un:'L',g:'Fungicida',alvo:'antracnose'}];
  const r1=M(c=>osc_ajustar(c,'OS-0501',a,{},'',[],add,false,'Ana')); const n1=cenGet().ordens['OS-0501'].ins.length, v1=cenGet().ordens['OS-0501'].versao;
  const r=M(c=>osc_ajustar(c,'OS-0501',a,{},'',[],add,false,'Ana')); const o=cenGet().ordens['OS-0501'];
  ok('U12 REPETIÇÃO: usar o mesmo produto de novo na mesma ordem é recusado ("já está na ordem"); não duplica nem muda a versão', !r1.erro&&/já está na ordem/.test(r.erro||'')&&o.ins.length===n1&&o.versao===v1, [r1,r,n1,v1]); }
cenReset();
// ---- U13 · ordens da semente sem alvo: o texto da aprovação não muda
{ const c=C(); T(()=>osc_liberar(c,'OS-0430',false,'','Ana')); const t=((c.ordens['OS-0430'].osc||{}).ev||[]).find(e=>e.cmd==='CMD-42')||{};
  ok('U13 ordem sem alvo (semente): CMD-42 igual ao de antes, sem "para"', /Glifosato 480 2 L\/ha, 2,4-D 806 1 L\/ha, Óleo mineral 0,5 L\/ha \(CMD-42\)$/.test(t.t||''), t.t); }
console.log('JS: '+R.filter(Boolean).length+'/'+R.length);
