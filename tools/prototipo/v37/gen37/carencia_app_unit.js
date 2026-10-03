// App de campo (MB-*) × carência (MAPA-CARENCIA-LMR-20261003) · jsc: cenario.js + JS do app (JS_BASE + MBAPP_JS, com a guarda leve).
const R=[]; function ok(n,c,info){ R.push({n,ok:!!c,info:c?'':JSON.stringify(info===undefined?'':info).slice(0,600)}); }
function CEN(ordens){ return {v:CEN0.v,rev:1,ordens,reqs:{},lotes:{},movs:[],ocorr:[],app:{online:true,fila:[],operador:'Marcos'},car:{}}; }
function O(id,tipo,talhao,etapa,ins,ap,x){ return Object.assign({id,tipo,talhao,etapa,area:60,realizado:0,saldo:60,resp:'Marcos',
  ins:ins.map(p=>({p,dose:1,un:'L',tot:1})),ap:ap.map((a,i)=>({d:a[0],dia:i+1,ha:a[1],st:'Conferido',sinc:true})),selos:[],osc:{}},x||{}); }
const TRY=(f)=>{ try{ f(); return ''; }catch(e){ return String(e.message||e); } };
{ const c=CEN({'OS-T':O('OS-T','Pulverização · antracnose','Pivô 23','Em conferência',['Tebuconazol 200 EC'],[['22/09',60]]),
               'OS-K':O('OS-K','Colheita · semana 39','Pivô 23','Liberadas',[],[],{janela:'24/09'}),
               'OS-P':O('OS-P','Pulverização · ácaro','Pivô 6','Liberadas',[],[],{janela:'24/09'})});
  const p=mbPasso(c,c.ordens['OS-K']); const er=TRY(()=>mbIniciar(c,'OS-K'));
  ok('A1 app: cartão da colheita OS-K mostra "Carência até 28/09 · colheita impedida" e não oferece Iniciar turno', p.k==='none'&&/Carência até 28\/09 · colheita impedida/.test(p.chip[0])&&p.chip[1]==='red', p);
  ok('A2 app: iniciar turno da colheita recusado com motivo e dono; a O.S. continua Liberadas', /Iniciar bloqueado: carência em curso/.test(er)&&/Ana/.test(er)&&c.ordens['OS-K'].etapa==='Liberadas', er);
  const p2=mbPasso(c,c.ordens['OS-P']); const er2=TRY(()=>mbIniciar(c,'OS-P'));
  ok('A3 app: ordem que não é colheita segue o fluxo normal (Iniciar turno)', p2.k==='iniciar'&&er2===''&&c.ordens['OS-P'].etapa==='Em execução', [p2.k,er2]); }
print(JSON.stringify(R));
