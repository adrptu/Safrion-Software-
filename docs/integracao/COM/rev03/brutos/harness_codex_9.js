const out=[];
const mud=(c,fn)=>{const x=cenClone(c);try{const r=fn(x);Object.keys(c).forEach(k=>delete c[k]);Object.assign(c,x);return r;}catch(e){return {erro:e.message};}};
function must(r){if(r.erro)throw Error(r.erro);return r;}
function setup(){const c=cenClone(CEN0);must(mud(c,x=>prReceber(x,{carga:'CG-2108',ticket:'QA-COM',bruto:19250,tara:7200,cond:'Íntegra',chave:'QA-REC'})));must(mud(c,x=>prReservar(x,{pedido:'PV-036',lote:'L39-133',kg:10000,ator:'Dora',chave:'QA-RS'})));must(mud(c,x=>comAprovarCredito(x,{venda:'PV-036',ator:'Ana',chave:'QA-CR'})));must(mud(c,x=>comProgramar(x,{venda:'PV-036',lotes:[{lote:'L39-133',prev:10000}],veic:'Baú refrigerado 12 t',transp:'Rota Sul Transportes',placa:'ABC1D23',dprev:'2026-09-26',ator:'Dora',chave:'QA-PG'})));return c;}
function check(id,pass,raw){out.push({id,pass,raw});}
const c=setup(),before=JSON.stringify(c);
const dup=mud(c,x=>comProgramar(x,{venda:'PV-036',lotes:[{lote:'L39-133',prev:1},{lote:'L39-133',prev:1}],veic:'Baú refrigerado 12 t',transp:'Rota Sul Transportes',placa:'ABC1D23',dprev:'2026-09-26',ator:'Dora',chave:'QA-DUP'}));
check('duplicate-atomic',/repetido/.test(dup.erro||'')&&JSON.stringify(c)===before,dup);
const saida={rm:'RM-0002',bruto:17200,tara:7200,ator:'Rui',chave:'QA-SAI'};must(mud(c,x=>comSair(x,saida)));const saved=JSON.stringify(c);const replay=mud(c,x=>comSair(x,saida));check('saida-replay',replay.repetido&&JSON.stringify(c)===saved,{repetido:replay.repetido,entrega:c.producao.expedicoes['RM-0002'].entrega});
check('saida-not-delivery',!c.producao.expedicoes['RM-0002'].entrega&&c.producao.expedicoes['RM-0002'].st==='Em trânsito',c.producao.expedicoes['RM-0002'].st);
const entrega={rm:'RM-0002',d:'2026-09-26',dev:{lote:'L39-133',kg:400,motivo:'Maturação avançada'},ator:'Rui',chave:'QA-ENT'};must(mud(c,x=>comEntregar(x,entrega)));let after=JSON.stringify(c);let rr=mud(c,x=>comEntregar(x,entrega));check('delivery-replay',rr.repetido&&JSON.stringify(c)===after,rr.repetido);
const changed=mud(c,x=>comEntregar(x,{...entrega,dev:{...entrega.dev,lote:'L10-031'}}));check('delivery-different-lot-conflict',!!changed.erro&&JSON.stringify(c)===after,{error:changed.erro,repetido:changed.repetido,actualOrigin:c.producao.expedicoes['RM-0002'].devs[0].de,requestedOrigin:'L10-031'});
const lid=c.producao.expedicoes['RM-0002'].devs[0].lote;const deny=mud(c,x=>prLiberarLote(x,lid,'Dora'));check('unauthorized-no-write',!!deny.erro&&JSON.stringify(c)===after,deny);const lib=must(mud(c,x=>prLiberarLote(x,lid,'Marta')));check('actor-recorded',c.producao.lotes[lid].lib.quem==='Marta (qualidade)',c.producao.lotes[lid].lib);
const legacy=cenClone(c);
legacy.producao.expedicoes['RM-0002'].devs[0].chave='OUTRA';
const ss=JSON.stringify(legacy);
const omitted={...entrega,dev:{kg:400,motivo:'Maturação avançada'}};
const incomplete=mud(legacy,x=>comEntregar(x,omitted));
check('missing-receipt-omitted-lot-conflict',!!incomplete.erro&&JSON.stringify(legacy)===ss,{error:incomplete.erro,repetido:incomplete.repetido});
const orig=JSON.stringify(c);
const normal=mud(c,x=>comEntregar(x,omitted));
check('valid-omitted-lot-replay',normal.repetido&&JSON.stringify(c)===orig,normal.repetido);
console.log(JSON.stringify({candidate:process.env.CAND||'?',executor:'Claude Node local (harness do Codex 6091943041, sem mudança)',synthetic:true,checks:out.map(x=>({id:x.id,pass:x.pass,raw:x.raw}))},null,2));
