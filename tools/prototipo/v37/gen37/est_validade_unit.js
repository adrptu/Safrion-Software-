(() => {
let falhas=0,total=0;
const exige=(x,m)=>{if(!x)throw Error(m);};
const caso=(nome,f)=>{total++;try{cenReset();f();console.log('OK '+nome);}catch(e){falhas++;console.log('FALHA '+nome+': '+e.message);}};
const mudar=f=>cenMudar(null,f),foto=()=>JSON.stringify({c:cenGet(),ls:__ls});
caso('saldo vencido sai do disponível sem apagar físico',()=>{const l={prod:'Sintético',lote:'VENCIDO',fisico:100,quarentena:0,reservado:10,validade:'01/2000'};exige(cenDisp(l)===0,'disponível='+cenDisp(l));exige(l.fisico===100&&l.reservado===10,'lote alterado na leitura');});
caso('lote válido menor é escolhido em vez de vencido com maior saldo',()=>{const c={lotes:{v:{prod:'Sintético',lote:'V',fisico:100,quarentena:0,reservado:0,validade:'01/2000'},a:{prod:'Sintético',lote:'A',fisico:5,quarentena:0,reservado:0,validade:'12/2099'}}};exige(cenLote(c,'Sintético').lote==='A','selecionou vencido');});
caso('O.S. não reserva produto com todos os lotes vencidos',()=>{
 const c=cenGet(),prod=c.ordens['OS-0430'].ins[0].p;mudar(x=>{Object.values(x.lotes).filter(l=>l.prod===prod).forEach(l=>l.validade='01/2000');return {msg:'precondição sintética'};});
 const antes=foto(),r=mudar(x=>cenLiberar(x,'OS-0430'));exige(!!r.erro,'O.S. liberada');exige(foto()===antes,'reservou ou alterou ordem');
});
caso('reserva antiga não permite entregar lote que venceu',()=>{
 const r=mudar(x=>cenLiberar(x,'OS-0430'));exige(!r.erro,r.erro);const c=cenGet(),rid=c.ordens['OS-0430'].req,it=c.reqs[rid].itens[0];
 mudar(x=>{x.lotes[it.prod+'|'+it.lote].validade='01/2000';return {msg:'precondição sintética'};});const antes=foto();
 const e=mudar(x=>cenEntregar(x,rid,it.prod,1,'Marcos','Rui','EST1-ENT'));exige(!!e.erro,'entrega vencida aceita');exige(foto()===antes,'alterou estoque/custódia/recibo');
});
caso('sem validade aplicável e lote futuro preservam disponível',()=>{for(const validade of ['—','12/2099'])exige(cenDisp({fisico:100,quarentena:5,reservado:10,validade})===85,'saldo válido mudou');});
caso('reserva e entrega válidas continuam possíveis',()=>{const r=mudar(x=>cenLiberar(x,'OS-0430'));exige(!r.erro,r.erro);const c=cenGet(),rid=c.ordens['OS-0430'].req,it=c.reqs[rid].itens[0];const r2=mudar(x=>cenEntregar(x,rid,it.prod,1,'Marcos','Rui','EST1-OK'));exige(!r2.erro,r2.erro);exige(cenGet().reqs[rid].itens[0].custodia===1,'custódia incorreta');});
caso('tela recusa lote vencido com motivo e mantém saldo pendente',()=>{const r=mudar(x=>cenLiberar(x,'OS-0430'));exige(!r.erro,r.erro);const c=cenGet(),rid=c.ordens['OS-0430'].req,it=c.reqs[rid].itens[0];c.lotes[it.prod+'|'+it.lote].validade='01/2000';const v=eitem(c,c.reqs[rid],it);exige(!v.pode&&v.bloq.includes('vencido')&&v.motivo.includes('Revise a reserva'),'tela oferece entrega ou omite recuperação');exige(v.pend===it.solicitado,'apagou pendência');});
caso('comando da tela recusa estoque vencido antes do motor',()=>{const r=mudar(x=>cenLiberar(x,'OS-0430'));exige(!r.erro,r.erro);const c=cenGet(),rid=c.ordens['OS-0430'].req,it=c.reqs[rid].itens[0];mudar(x=>{x.lotes[it.prod+'|'+it.lote].validade='01/2000';return {msg:'precondição'};});const antes=foto(),r2=mudar(x=>estEntregar(x,rid,it.prod,1,'Marcos','Rui','EST1-UI'));exige(!!r2.erro&&/vencido/.test(r2.erro),'entrega aceita');exige(foto()===antes,'estado alterado');});

caso('regra única respeita último dia do mês, ano e fevereiro bissexto',()=>{
 for(const [hoje,validade,vencido] of [['2026-12-31','12/2026',false],['2027-01-01','12/2026',true],['2028-02-29','02/2028',false],['2028-03-01','02/2028',true]])exige(cenLoteVencido({validade},hoje)===vencido,hoje+' '+validade);
 exige(CEN_DIA_OP===eiso(E2.hoje),'datas operacionais diferentes');
});
caso('lote vencido não volta ao disponível ao retirar reserva ou quarentena',()=>{const l={fisico:100,quarentena:100,reservado:0,validade:'01/2000'};exige(cenDisp(l)===0,'quarentena');l.quarentena=0;exige(cenDisp(l)===0,'liberação indevida');l.reservado=20;exige(cenDisp(l)===0,'reserva');l.reservado=0;exige(cenDisp(l)===0,'cancelamento');});
caso('replay de entrega anterior ao vencimento não duplica movimento',()=>{
 let r=mudar(c=>cenLiberar(c,'OS-0430'));exige(!r.erro,r.erro);const c=cenGet(),rid=c.ordens['OS-0430'].req,it=c.reqs[rid].itens[0];
 r=mudar(c=>cenEntregar(c,rid,it.prod,1,'Marcos','Rui','REPLAY-VALIDADE'));exige(!r.erro,r.erro);
 mudar(c=>{c.lotes[it.prod+'|'+it.lote].validade='01/2000';return {msg:'vencimento'};});
 const antes=JSON.stringify({lotes:cenGet().lotes,reqs:cenGet().reqs,movs:cenGet().movs});r=mudar(c=>cenEntregar(c,rid,it.prod,1,'Marcos','Rui','REPLAY-VALIDADE'));exige(!r.erro&&r.repetido,'não recuperou recibo');exige(JSON.stringify({lotes:cenGet().lotes,reqs:cenGet().reqs,movs:cenGet().movs})===antes,'duplicou efeito');
});
console.log('RESULTADO '+(total-falhas)+'/'+total);if(falhas)process.exitCode=1;
})();
