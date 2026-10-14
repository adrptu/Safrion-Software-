(()=>{let total=0,fail=0;
function preparar(){
cenReset(); const c=cenGet(); const o=c.ordens['OS-0430'];
cenLiberar(c,o.id); const r=c.reqs[o.req];
for(const it of r.itens)cenEntregar(c,r.id,it.prod,1,'Marcos','Rui');
cenConfirmarRecebimento(c,r.id);cenIniciarTurno(c,o.id);
const it=r.itens[0],l=c.lotes[it.prod+'|'+it.lote];
const cons=Object.fromEntries(r.itens.map(x=>[x.prod,x===it?3:0]));
cenFecharTurno(c,1,1,cons,'',[]);const k=c.confs.find(x=>x.prod===it.prod);return {c,r,it,l,k};}
function caso(n,f){total++;try{if(!f())throw Error('invariante não atendida');console.log('OK '+n);}catch(e){fail++;console.log('FALHA '+n+': '+e.message);}}
caso('conciliação não retira lote vencido por reserva antiga',()=>{const {c,l,k}=preparar();l.validade='01/2000';
const prev=cenConcPrevia(c,k.id),fis=l.fisico;let erro='';
try{cenConciliar(c,k.id,true,'Conferência sintética','Ana');}catch(e){erro=e.message;}
console.log(JSON.stringify({falta:prev.falta,reserva:prev.res,livre:prev.livre,erroPrevia:prev.erro,erroComando:erro,fisicoAntes:fis,fisicoDepois:l.fisico,estado:k.estado}));
return !!prev.erro&&!!erro&&l.fisico===fis&&k.estado==='Em conferência';});
caso('custódia entregue antes do vencimento ainda pode ser conciliada sem nova retirada',()=>{const {c,r,it,l,k}=preparar();cenEntregar(c,r.id,it.prod,2,'Marcos','Rui');l.validade='01/2000';const fis=l.fisico;
const prev=cenConcPrevia(c,k.id);cenConciliar(c,k.id,true,'Fato físico já em custódia','Rui');return prev.falta===0&&!prev.erro&&l.fisico===fis&&it.consumido===3&&it.custodia===0&&k.estado==='Aceito';});
caso('recusar relato mantém físico e reserva vencidos sem retirada',()=>{const {c,it,l,k}=preparar();l.validade='01/2000';const antes=JSON.stringify({l,it});cenConciliar(c,k.id,false,'Relato sem confirmação física','Rui');return JSON.stringify({l,it})===antes&&k.estado==='Recusado';});
console.log('RESULTADO '+(total-fail)+'/'+total);if(fail)process.exitCode=1;
})();
