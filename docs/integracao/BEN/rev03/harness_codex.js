
const report={candidate:'bbe8417cd99b763875639e7cc2f7b15e044e4ed3',executor:'Node local, solicitado pelo Gemini real',cases:[]};
function setup(){const c=cenClone(CEN0);const id=benNova(c,{lotes:[{lote:'L39-132',kg:prFis(c,'L39-132')}],cx:540},'Igor').id;benAutorizarLiberar(c,id,'Igor');const rid=c.ordens[id].req;cenEntregar(c,rid,BENC.cx.item,540,'Igor','Rui');benIniciar(c,id,'Igor');const s=benSaida(c,id,{fluxo:'Produto',classe:'A',cx:540,bruto:5724,pallets:0},'Igor').s;const old=benReqItem(c,c.ordens[id]).lote;cenReceber(c,BENC.cx.item,'QA-CX-02',1000,'un','Packing','','NF-QA-02',true,'Rui');return{c,id,rid,s,old};}
function refusal(name,act){const z=setup(),before=JSON.stringify(z.c);let error=null;try{act(z);}catch(e){error=e.message;}report.cases.push({name,passed:!!error&&before===JSON.stringify(z.c),error,unchanged:before===JSON.stringify(z.c)});}
try{
 const {c,id,rid,s,old}=setup();const oldKey=BENC.cx.item+'|'+old,newKey=BENC.cx.item+'|QA-CX-02';const before={old:cenClone(c.lotes[oldKey]),new:cenClone(c.lotes[newKey])};
 const complement=benComplementar(c,id,100,'Igor',{chave:'QA-C100',ver:c.ordens[id].ver});
 const reverse=benEstornar(c,id,s.id,'Pesagem refeita','','Igor',{chave:'QA-REV',ver:c.ordens[id].ver});
 const returned=cenDevolver(c,rid,BENC.cx.item,540,true,'Rui');
 const original=c.movs.find(m=>m.id===s.mv);const reversal=c.movs.find(m=>m.id===s.estorno.mv);
 const after={old:c.lotes[oldKey],new:c.lotes[newKey]};
 report.cases.push({name:'origem por lote preservada ao complementar, estornar e devolver',passed:original.lote===reversal.lote&&after.old.fisico===before.old.fisico+540&&after.new.fisico===before.new.fisico,before,after,original,reversal,complement,reverse,returned,movements:c.movs.filter(m=>m.os===id)});
}catch(e){report.cases.push({name:'origem por lote',fixture_error:e.message,passed:false});}
refusal('versao vencida recusa sem escrita',z=>benComplementar(z.c,z.id,100,'Igor',{chave:'QA-V',ver:z.c.ordens[z.id].ver-1}));
refusal('perfil sem papel de producao recusa sem escrita',z=>benComplementar(z.c,z.id,100,'Rui',{chave:'QA-P',ver:z.c.ordens[z.id].ver}));
try{const z=setup();benComplementar(z.c,z.id,100,'Igor',{chave:'QA-I',ver:z.c.ordens[z.id].ver});const before=JSON.stringify(z.c);const repeat=benComplementar(z.c,z.id,100,'Igor',{chave:'QA-I'});let error;try{benComplementar(z.c,z.id,101,'Igor',{chave:'QA-I'});}catch(e){error=e.message;}report.cases.push({name:'recibo repetido e payload conflitante',passed:repeat.repetido&&!!error&&before===JSON.stringify(z.c),repeat,error,unchanged:before===JSON.stringify(z.c)});}catch(e){report.cases.push({name:'recibo',fixture_error:e.message,passed:false});}
report.passed=report.cases.every(x=>x.passed);console.log(JSON.stringify(report,null,2));process.exit(report.passed?0:1);

