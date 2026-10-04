// Instrumenta uma CÓPIA em memória do bloco REPARTIR (2e31588): ordem das restrições da divisão e q depois de cada redução das partes fixas.
const fs=require('fs'); const [,,arq,ent]=process.argv;
let b=fs.readFileSync(arq,'utf8').match(/\/\/ >>> REPARTIR[\s\S]*?\/\/ <<< REPARTIR/)[0];
const a1="const gs=Object.keys(jan); gs.filter(g=>!SUB[g]).concat(gs.filter(g=>SUB[g])).forEach(g=>{";
if(b.indexOf(a1)<0) throw 'âncora';
b=b.replace(a1,"const gs0=Object.keys(jan); LOG.push('ordem: '+gs0.filter(g=>!SUB[g]).concat(gs0.filter(g=>SUB[g])).map(g=>g+' ['+pistaA[g].map(x=>x.nome).join(',')+'] jan='+jan[g]+(SUB[g]?' (sub)':'')).join(' → ')); "+a1);
const a2="cz.seq=1; cortes.push(g); liga[g]=1; } });";
b=b.replace(a2,"cz.seq=1; cortes.push(g); liga[g]=1; } LOG.push('  depois de '+g+': '+it.map(x=>x.nome+'='+(+q[x.i].toFixed(6))+' ha/'+(+(q[x.i]/(x.r||1)).toFixed(6))+' h').join(' ')); });");
const f=new Function('LOG',b+'\nreturn repartir;'); const E=JSON.parse(fs.readFileSync(ent,'utf8'));
for(const k of process.argv.slice(4)){ const LOG=[]; const r=f(LOG)(E[k].Q,E[k].cfgs,E[k].pools||{}); console.log('## '+k); LOG.forEach(l=>console.log(l)); console.log('  final: alocado '+r.alocado+'; decorrido '+r.decorrido); }
