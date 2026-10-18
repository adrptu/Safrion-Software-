// Contraprovas do revisor (Claude), rodada 2, sobre as funções reais de robot.html (PR #112 @7c2045d6). Sem navegador.
// Uso: node contraprova_alvo2.cjs <robot.html>
const fs=require('fs'),vm=require('vm');
const src=fs.readFileSync(process.argv[2],'utf8');
const code=src.slice(src.indexOf('const ENT_SRC'),src.indexOf('const LABENT'));
const ctx={topDlg:d=>d.dialog,dTitle:(_,d)=>d?.title||'',vis:()=>true};vm.createContext(ctx);vm.runInContext(code,ctx);
const target=(raw,h,t)=>ctx.expectedTarget({getAttribute:()=>raw},{h,t}).id;
// doc sintético: dialog (com título) ou null; h1; linhas selecionadas
const doc=(dialog,h1,sel=[])=>({dialog,querySelector:s=>s==='h1'&&h1!=null?{innerText:h1}:null,querySelectorAll:()=>sel.map(innerText=>({innerText}))});
const arr=(d,id)=>{const r=ctx.arrival(d,{id});return JSON.stringify({abriu:r.abriu,destacou:r.destacou})};
const casos=[
 // A2 (rodada 1: dava OS-0502 e OS-0420)
 ['A2', 'F1 ?de= com %23 na query', target(null,'EST.dc.html?de=OS.dc.html%23OS-0502#ent=REQ-039','Entregar no Estoque'), 'REQ-039'],
 ['A2', 'F1 ?de= com %23, hash sem ID', target(null,'MA.dc.html?de=OS.dc.html%23OS-0420#vis=ordens','Abrir na tela de Manutenção'), ''],
 ['A2', 'fragmento codificado', target(null,'EST.dc.html?de=OS.dc.html%23OS-0424#ent=REQ%2D039','Entregar'), 'REQ-039'],
 ['A2', 'só query ?de=, sem fragmento, texto sem ID', target(null,'EST.dc.html?de=OS.dc.html%23OS-0424','Entregar no Estoque ›'), ''],
 // A10
 ['A10','exactId sufixo /2', String(ctx.exactId('OS-0502/2 · parcial','OS-0502')), 'false'],
 ['A10','exactId título com 2 IDs (aberto é PC-0012)', String(ctx.exactId('PC-0012 · da OS-0502','OS-0502')), 'false'],
 ['A10','exactId controle positivo', String(ctx.exactId('OS-0502 · Pulverização','OS-0502')), 'true'],
 ['A10','hash com contexto para=OS, texto sem ID', target(null,'EST.dc.html#dev=lin3&para=OS-0502&ver=2','Abrir'), ''],
 // novos limites do recorte por '&'
 ['N1', 'hash de contexto + texto cita a ORIGEM (OS-0502 aberta)', target(null,'EST.dc.html#dev=lin3&para=OS-0502','Receber a devolução da OS-0502 no Estoque'), '(inconclusiva: OS-0502 é a origem)'],
 ['N2', 'formato F1 do Painel #painel=a&abre=b (abre OS-0431)', target(null,'OS.dc.html#painel=OS-0420&abre=OS-0431','Abrir ›'), 'OS-0431 ou inconclusiva'],
 ['N2', 'formato F1 do Painel com 2 OS', target(null,'OS.dc.html#painel=OS-0420,OS-0507&abre=OS-0431','Abrir ›'), 'OS-0431 ou inconclusiva'],
 ['N2', 'ID só no 2º parâmetro (#vis=ordens&om=OM-0233)', target(null,'MA.dc.html#vis=ordens&om=OM-0233','Acompanhar ordem ›'), 'OM-0233 ou inconclusiva'],
 // A3: h1 só sem diálogo
 ['A3', 'sem diálogo, h1 com o ID primeiro', arr(doc(null,'IR-03 · OS-0471 · Irrigação do pivô 2'),'OS-0471'), '{"abriu":true,"destacou":false}'],
 ['A3', 'sem diálogo, h1 é o registro', arr(doc(null,'OS-0420 · Caderno de campo'),'OS-0420'), '{"abriu":true,"destacou":false}'],
 ['A3', 'diálogo sem título, h1 com o ID: não conta', arr(doc({title:''},'OS-0502'),'OS-0502'), '{"abriu":false,"destacou":false}'],
 ['A3', 'diálogo com outro registro, h1 com o ID', arr(doc({title:'OS-0503'},'OS-0502'),'OS-0502'), '{"abriu":false,"destacou":false}'],
 ['A3', 'sem diálogo, h1 de lista filtrada que cita o alvo', arr(doc(null,'OM-0233 · ordens afetadas'),'OM-0233'), '(limite: conta como chegada)'],
 ['A3', 'seleção: linha começa por outro ID', arr(doc(null,'Estoque',['REQ-039 · OS-0502 · 3 itens']),'OS-0502'), '{"abriu":false,"destacou":false}'],
 ['A3', 'seleção: controle positivo', arr(doc(null,'Estoque',['REQ-039 · OS-0502 · 3 itens']),'REQ-039'), '{"abriu":false,"destacou":true}'],
];
let dif=0;for (const [a,n,obt,esp] of casos){const ok=obt===esp;if(!ok)dif++;console.log((ok?'OK  ':'DIF ')+a+' · '+n+' | obtido='+JSON.stringify(obt)+' | esperado='+esp);}
console.log(`${casos.length} casos, ${dif} DIF. Esperado entre parênteses = limite documentado (N1 e lista filtrada no A3); sem parênteses = achado (N2 no LEIAME da rodada 2)`);
