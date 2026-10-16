(() => {
let falhas=0, total=0;
const caso=(nome,f)=>{total++;try{cenReset();f();console.log('OK '+nome);}catch(e){falhas++;console.log('FALHA '+nome+': '+e.message);}};
const exige=(x,m)=>{if(!x)throw Error(m);};
const dado=(apto,quar,div='Item diferente do pedido')=>{const p=E2.pedidos[0];return {id:'r99998',nf:'NF 99998',ped:p.id,item:p.item,un:p.un,qtd_nf:5,conf:5,apto,quar,lote:'EST2-SINTETICO',val:'12/2099',local:'Galpão 1',div,obs:'Produto recebido diferente do comprado'};};
for(const [apto,quar] of [[5,0],[0,5],[2,3]]) caso('item diferente recusa comando apto='+apto+' quarentena='+quar+' sem alterar estoque/recibo',()=>{
 const d=dado(apto,quar);cenGet();const antes=JSON.stringify({c:cenGet(),ls:__ls});const r=cenMudar(null,c=>estReceber(c,d,'Rui','EST2-DIF'));
 exige(!!r.erro,'recebimento indevido aceito');exige(JSON.stringify({c:cenGet(),ls:__ls})===antes,'estado alterado');
});
caso('erro junto da divergência mantém preenchimento',()=>{const fm={draft:dado(5,0)},antes=JSON.stringify(fm);const e=ESTV.g_rec(null,fm);exige(!!e.div,'campo divergência sem erro');exige(JSON.stringify(fm)===antes,'rascunho alterado');});
for(const [apto,quar,div] of [[5,0,'Sem divergência'],[0,5,'Avaria']]) caso('mesmo item continua recebível: '+div,()=>{const d=dado(apto,quar,div),r=cenMudar(null,c=>estReceber(c,d,'Rui','EST2-OK'));
 exige(!r.erro,r.erro);const l=cenGet().lotes[d.item+'|'+d.lote];exige(l.fisico===5&&l.quarentena===quar,'saldo divergente');const rev=cenGet().rev;const outra=cenMudar(null,c=>estReceber(c,d,'Rui','EST2-OK'));exige(!outra.erro,outra.erro);exige(cenGet().lotes[d.item+'|'+d.lote].fisico===5,'duplicou');
});
console.log('RESULTADO '+(total-falhas)+'/'+total);if(falhas)process.exitCode=1;
})();
