const fs = require('node:fs');
const crypto = require('node:crypto');
const source = process.argv[2] || '/home/user/sp-safc01/tools/prototipo/v37/gen37/ocupacao.js';
const code = fs.readFileSync(source, 'utf8');
eval(code);
const ctx = ocCtx({'Café':'Perene','Soja':'Anual'}, [['Soja','Teste',112]], [{id:'PTEST',cultura:'Soja',estado:'Publicado',atividades:[{op:'Colheita',nome:'Colheita',g:{tipo:'DAP',dias:120}}]}], 1);
function scenario(id, planting, area, expectedBlock) {
  const oldYear = planting.slice(0,4);
  const safras = {
    velha: {id:'velha',nome:'Perene original',ini:oldYear+'-01-01',fim:oldYear+'-12-31',faz:'Fictícia'},
    nova: {id:'nova',nome:'Safra teste 2027',ini:'2027-01-01',fim:'2027-12-31',faz:'Fictícia'}
  };
  const cafe = {id:'cafe',ciclo:'cafe',saf:'velha',faz:'Fictícia',talhao:'T1',faixa:'T1-A',tipo:'Parcela',area:40,cult:'Café',var:'Teste',plantio:planting};
  const soja = {id:'soja',ciclo:'soja',saf:'nova',faz:'Fictícia',talhao:'T1',faixa:'T1-B',tipo:'Parcela',area,cult:'Soja',var:'Teste',plantio:'2027-06-01',plano:'PTEST'};
  const result = ocChecar(ctx, safras, [cafe], [cafe,soja], 'nova','soja',100);
  const table = ocTabela(ctx,safras.nova,ocOcupacoes(ctx,safras,[cafe,soja]),[['T1',100]],safras);
  const blocked = result.trav.length > 0;
  return {id,fixture:{plantio_perene:planting,area_perene:40,plantio_anual:soja.plantio,area_anual:area,area_talhao:100,faixas_distintas:true},expected_block:expectedBlock,actual_block:blocked,pass:blocked===expectedBlock,raw:{trav:result.trav,pend:result.pend,aviso:result.aviso,table}};
}
const scenarios = [
  scenario('PERENE-ANTIGO-EXCESSO','2020-01-01',70,true),
  scenario('PERENE-ANTIGO-LIMITE','2020-01-01',60,false),
  scenario('PERENE-RECENTE-EXCESSO','2026-01-01',70,true)
];
console.log(JSON.stringify({source_sha256:crypto.createHash('sha256').update(code).digest('hex'),scenarios},null,2));
process.exitCode=scenarios.every(x=>x.pass)?0:1;
