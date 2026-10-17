// Contraprovas do revisor (Claude) sobre as funções reais de robot.html v5.1. Sem navegador.
const fs=require('fs'),vm=require('vm');
const src=fs.readFileSync(process.argv[2],'utf8');
const code=src.slice(src.indexOf('const ENT_SRC'),src.indexOf('const LABENT'));
const ctx={topDlg:d=>d.dialog,dTitle:(_,d)=>d?.title||'',vis:()=>true};vm.createContext(ctx);vm.runInContext(code,ctx);
const target=(raw,h,t)=>ctx.expectedTarget({getAttribute:()=>raw},{h,t});
const casos=[
 ['F1 ?de= com %23 na query (link sem data-ref)', target(null,'EST.dc.html?de=OS.dc.html%23OS-0502#ent=REQ-039','Entregar no Estoque').id, 'REQ-039'],
 ['F1 ?de= com %23, hash sem ID', target(null,'MA.dc.html?de=OS.dc.html%23OS-0420#vis=ordens','Abrir na tela de Manutenção').id, ''],
 ['hash com parâmetro de contexto para=OS', target(null,'EST.dc.html#dev=lin3&para=OS-0502&ver=2','Receber a devolução da OS-0502 no Estoque').id, '(contexto: OS-0502 é a origem)'],
 ['hash painel com 3 OS', target(null,'OS.dc.html#painel=OS-0420,OS-0431,OS-0507','Abrir 3 O.S.').id, ''],
 ['texto com 2 IDs, sem hash', target(null,'OS.dc.html','Ver ordens afetadas · OS-0420 e OS-0431 ›').id, ''],
 ['exactId sufixo /2', String(ctx.exactId('OS-0502/2 · parcial','OS-0502')), 'false?'],
 ['exactId título com 2 IDs (registro aberto é outro)', String(ctx.exactId('PC-0012 · da OS-0502','OS-0502')), 'false?'],
];
for (const [n,obt,esp] of casos) console.log((obt===esp?'OK  ':'DIF ')+n+' | obtido='+JSON.stringify(obt)+' | esperado='+esp);
