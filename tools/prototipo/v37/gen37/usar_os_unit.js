// CTL-5 · E2 (RL-E3) · AG-07 só consulta: "Usar na O.S." leva produto da fazenda, cultura e alvo à ordem A liberar da cultura; o registro
// (produto, dose, alvo e quem aprovou) só nasce na O.S., pela trava legal única do CTL-1. Executor: usar_os_unit_test.py (node, sem navegador).
// Na base 99537ca não existem carCult nem agOsCand e o alvo não chega à O.S.: os casos falham (stubs abaixo evitam parar no 1º).
const R=[]; const ok=(n,c,info)=>{ R.push(!!c); console.log((c?'OK    ':'FALHA ')+n+(c?'':' · '+String(JSON.stringify(info)).slice(0,500))); };
const T=(f)=>{ try{ const r=f(); return {ok:true,msg:r&&r.msg}; }catch(e){ return {ok:false,msg:e.message}; } };
const C=()=>cenClone(CEN0);
if(typeof carCult!=='function') globalThis.carCult=()=>'';
if(typeof agOsCand!=='function') globalThis.agOsCand=()=>[];
const ids=(L)=>L.map(o=>o.id).join(',');
const DSOJA='OS-0595,OS-0596,OS-0597', DMAM='OS-0584,OS-0585,OS-0586,OS-0587,OS-0588,OS-0589,OS-0590,OS-0591,OS-0592';   // demonstração das Frentes (EX-54)

// ---- U1 · cultura da ordem: uma regra só (carCult) para a trava legal da O.S. e para os candidatos do AG-07
// semente de demonstração das Frentes (EX-54, cenario.seed_agrupamento): a O.S. sai do plano com a cultura planejada (ex.: dessecação
// pré-plantio de soja no T3, hoje com milho), que pode diferir da do talhão no cadastro; a regra é a mesma carCult, conferida à parte
const DEMO=o=>!!(o.osc&&o.osc.novo&&o.osc.novo.demoLote);
{ const c=C(); const lin=[], dem=[]; Object.values(c.ordens).forEach(o=>carTals(o.talhao).forEach(t=>(DEMO(o)?dem:lin).push([o.id,t.tid,carCult(o,t.tid),DEMO(o)?String(o.osc.novo.cultura).split(' ')[0]:CARD.tal[t.tid].cult])));
  ok('U1 semente: cultura de cada talhão das '+Object.values(c.ordens).filter(o=>!DEMO(o)).length+' ordens = a do talhão no cadastro ('+lin.length+' pares)', lin.length>20&&lin.every(x=>x[2]===x[3]), lin.filter(x=>x[2]!==x[3]).slice(0,4));
  ok('U1b demonstração das Frentes: cultura de cada O.S. = a planejada na O.S., pela 1ª palavra como a carCult ('+dem.length+' pares)', dem.length>=10&&dem.every(x=>x[2]===x[3]), dem.filter(x=>x[2]!==x[3]).slice(0,4)); }
{ const c=C(); osc_nova(c,{id:'OS-0440',tipo:'Herbicida pós-emergente',talhao:'T1-A',area:160,versao:'v1',resp:'Marcos',ins:[],selos:[],atv:{op:'Pulverização'}}); const o=c.ordens['OS-0440']; o.osc.novo.cultura='Milho safrinha';
  ok('U2 ordem nova da safrinha no T1-A: cultura do cultivo (Milho), não a do talhão (Soja)', carCult(o,'T1')==='Milho', carCult(o,'T1'));
  ok('U3 AG-07: a ordem nova de milho é candidata em Milho e não em Soja', ids(agOsCand(c,'Milho'))==='OS-0440'&&ids(agOsCand(c,'Soja')).indexOf('OS-0440')<0, [ids(agOsCand(c,'Milho')),ids(agOsCand(c,'Soja'))]); }

// ---- U4 · candidatos do AG-07: só O.S. A liberar (não OB, não liberada) da cultura escolhida e de operação que aplica defensivo
// (revisão do CTL-5, S3-1: antes entravam Calagem, Sexagem e Fertirrigação, e a reserva de agrotóxico ia para operação que não pulveriza)
{ const c=C(); const s=ids(agOsCand(c,'Soja')), m=ids(agOsCand(c,'Mamão')), f=ids(agOsCand(c,'Feijão')), mi=ids(agOsCand(c,'Milho')), ca=ids(agOsCand(c,'Café'));
  // com a demonstração das Frentes: Soja ganha a dessecação pré-plantio OS-0595 a 0597; Mamão, o acaricida e o fungicida OS-0584 a 0592 (a calagem OS-0593/0594 fica fora)
  ok('U4 semente: Soja = OS-0430 + OS-0595 a 0597 (dessecação) · Mamão = OS-0501 + OS-0584 a 0592 (pulverização; calagem fora) · Feijão, Milho e Café = nenhuma',
     s==='OS-0430,'+DSOJA&&m==='OS-0501,'+DMAM&&f===''&&mi===''&&ca==='', [s,m,f,mi,ca]); }
{ const c=C(); const r=T(()=>osc_liberar(c,'OS-0430',false,'','Ana'));
  ok('U5 liberada sai da lista: depois de liberar a OS-0430, Soja = só a demonstração (OS-0595 a 0597)', r.ok&&ids(agOsCand(c,'Soja'))===DSOJA, [r,ids(agOsCand(c,'Soja'))]); }
{ const c=C(); const no=(id,tipo,op,cult,tal)=>osc_nova(c,{id,tipo,talhao:tal||'Pivô 15',area:36.17,versao:'v1',resp:'—',ins:[],selos:[],atv:{op},cultura:cult||'Mamão Formosa'});
  no('OS-0440','Colheita · semana 40','Colheita de frutas'); no('OS-0441','Pulverização · Controle de ácaro-rajado','Pulverização'); no('OS-0442','Fertirrigação · Ureia 45%','Fertirrigação');
  const m=ids(agOsCand(c,'Mamão'));
  ok('U14 NEGATIVO Calagem (OS-0502), Sexagem e desbaste (OS-0511), Fertirrigação (OS-0418, OS-0442) e Colheita (OS-0440) não são candidatas; pulverização nova (OS-0441) é',
     m==='OS-0441,OS-0501,'+DMAM&&ids(agOsCand(c,'Feijão'))==='', [m,ids(agOsCand(c,'Feijão'))]); }
{ const c=C(); c.ordens['OB-0199']={id:'OB-0199',tipo:'Pulverização · teste',talhao:'Pivô 13',area:10,etapa:'A liberar',versao:'v1',realizado:0,saldo:10,resp:'—',ins:[],req:null,selos:[],ap:[],reservado:false,osc:{novo:{atv:{op:'Pulverização'},cultura:'Mamão'}}};
  ok('U15 NEGATIVO ordem OB (beneficiamento) nunca é candidata, nem com operação de pulverização', ids(agOsCand(c,'Mamão'))==='OS-0501,'+DMAM, ids(agOsCand(c,'Mamão'))); }

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
// ---- U16..U18 · alvo × referência conferida da fazenda (revisão do CTL-5, S3-3): a trava legal única confere o alvo como confere a dose
{ cenReset(); const o0=JSON.parse(JSON.stringify(cenGet().ordens['OS-0501']));
  const r=M(c=>osc_ajustar(c,'OS-0501',o0.area,{},'',[],[{p:'Acetamiprido 200 SP',dose:0.3,un:'kg',g:'Inseticida',alvo:'Cochonilha'}],true,'Ana'));
  ok('U16 RECUSA alvo fora da referência: Acetamiprido 200 SP para Cochonilha no mamão (referência: mosca-branca) → "Cochonilha não está na referência conferida em mamão (mosca-branca)"; nada gravado',
     /Cochonilha não está na referência conferida em mamão \(mosca-branca\)/.test(r.erro||'')&&nada('OS-0501',o0), r); }
{ cenReset(); const o0=cenGet().ordens['OS-0501'];
  const r=M(c=>osc_ajustar(c,'OS-0501',o0.area,{},'',[],[{p:'Acetamiprido 200 SP',dose:0.3,un:'kg',g:'Inseticida',alvo:'mosca-branca'}],true,'Ana'));
  const ev=((cenGet().ordens['OS-0501'].osc||{}).ev||[]).find(e=>e.cmd==='CMD-42')||{};
  ok('U17 alvo da referência (mosca-branca) passa: CMD-42 "Acetamiprido 200 SP 0,3 kg/ha para mosca-branca"', !r.erro&&/Acetamiprido 200 SP 0,3 kg\/ha para mosca-branca \(CMD-42\)/.test(ev.t||''), [r,ev.t]); }
{ const P=(n)=>CARD.prod[n]; const casos=[['Tebuconazol 200 EC','Mamão','Antracnose','antracnose'],['Abamectina 18 EC','Mamão','Ácaro-branco','ácaro-branco'],['Acetamiprido 200 SP','Mamão','Cochonilha',''],
    ['Cletodim 240','Soja','Capim-amargoso','capim-amargoso'],['Glifosato 480','Mamão','capim-colchão','capim-colchão'],['Tebuconazol 200 EC','Soja','Antracnose','']];
  const got=casos.map(x=>typeof carAlvoRef==='function'?carAlvoRef(P(x[0]),x[1],x[2]):'?');
  ok('U18 regra única do alvo (carAlvoRef: AG-07 e trava da O.S.): nome igual, nome antes de "·" ou "(", ou item entre parênteses; herbicida: referência por grupo de plantas daninhas cobre a espécie; sem uso na cultura: nada',
     got.every((g,i)=>g===casos[i][3]), got); }
cenReset();
// ---- U13 · ordens da semente sem alvo: o texto da aprovação não muda
{ const c=C(); T(()=>osc_liberar(c,'OS-0430',false,'','Ana')); const t=((c.ordens['OS-0430'].osc||{}).ev||[]).find(e=>e.cmd==='CMD-42')||{};
  ok('U13 ordem sem alvo (semente): CMD-42 igual ao de antes, sem "para"', /Glifosato 480 2 L\/ha, 2,4-D 806 1 L\/ha, Óleo mineral 0,5 L\/ha \(CMD-42\)$/.test(t.t||''), t.t); }
console.log('JS: '+R.filter(Boolean).length+'/'+R.length);
