// SAF-C01 · trava de soma entre duas perenes (café antigo 40 ha em T1-A + café 2027 70 ha em T1-B, talhão 100 ha) e tempo da mensagem M1.
// Uso: node mensagem_perene_perene.js <ocupacao.js> <plantio do café antigo>
const fs=require('fs'); eval(fs.readFileSync(process.argv[2],'utf8'));
const ctx=ocCtx({'Café':'Perene','Soja':'Anual'},[],[],1);
const S={v:{id:'v',nome:'Café antigo',ini:'2010-01-01',fim:'2026-12-31',faz:'F'},n:{id:'n',nome:'Café 2027',ini:'2027-01-01',fim:'2027-12-31',faz:'F'}};
const a={id:'ca',saf:'v',faz:'F',talhao:'T1',faixa:'T1-A',tipo:'Parcela',area:40,cult:'Café',var:'X',plantio:process.argv[3]||'2026-01-01'};
const b={id:'cb',saf:'n',faz:'F',talhao:'T1',faixa:'T1-B',tipo:'Parcela',area:70,cult:'Café',var:'X',plantio:'2027-06-01'};
const r=ocChecar(ctx,S,[a],[a,b],'n','cb',100); console.log('trav',JSON.stringify(r.trav));
const t0=Date.now(); const m=r.trav.length?ocMsgTrava(ctx,r,'n',100,null):''; console.log('msg',m,'ms',Date.now()-t0);
