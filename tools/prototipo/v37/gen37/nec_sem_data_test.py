"""EX57: rateio do mapa preserva pendência fora dos períodos datados."""
import os, subprocess
from pathlib import Path
s=Path('areas/inicio.py').read_text(); f=s[s.index('function necAgg('):s.index('function brIso(')]
t='''
const assert=require('node:assert/strict');const M={lim30:'2026-10-31'};let ev=[];const insFaz=()=>({nec:{T:ev}});
for(const dt of [null,''])for(const reverse of [false,true]){
 ev=[{p:'X',q:100,un:'kg',dt,orig:'pendente'},{p:'X',q:20,un:'kg',dt:'2026-10-25',orig:'conhecida'},{p:'X',q:30,un:'kg',dt:'2026-11-25',orig:'futura'}];if(reverse)ev.reverse();
 let all=necAgg('T','Safra toda')[0],per=necAgg('T','Próximos 30 dias')[0];
 assert.equal(all.q,150);assert.equal(all.datada,50);assert.equal(all.semData,100);assert.equal(all.dt,'2026-10-25');
 assert.equal(per.q,20);assert.equal(per.semData,100);assert.equal(per.dt,'2026-10-25');
}
ev=[{p:'X',q:100,un:'kg',dt:null,orig:'pendente'}];let r=necAgg('T','Próximos 30 dias')[0];assert.equal(r.q,0);assert.equal(r.semData,100);assert.equal(r.dt,null);
ev[0].dt='2026-10-26';r=necAgg('T','Próximos 30 dias')[0];assert.equal(r.q,100);assert.equal(r.semData,0);assert.equal(r.dt,'2026-10-26');
console.log('PASS necAgg real: null/vazio, ordem inversa, horizonte, somente pendente e resolução');
'''
subprocess.run([os.environ.get('NODE_BINARY','node'),'-e',f+t],check=True)
compile(s,'inicio.py','exec')

# O indicador agregado não pode esconder falta firme atrás de pendência amarela.
start=s.index("if(isIns(l,f)){ const its=necAgg")
end=s.index("  if(l==='Custos')",start)
block=s[start:end]
js="const assert=require('node:assert/strict');let state='red';const necAgg=()=>[{p:'X',semData:100}],insFaz=()=>({st:{P:{X:['Falta',state]}}}),isIns=()=>true,mc_worstC=cs=>cs.includes('red')?'red':cs[0];function check(l,f,t){"+block+"}assert.equal(check('I',{per:'P'},'T').c,'red');state='ok';assert.equal(check('I',{per:'P'},'T').c,'yellow');console.log('PASS falta firme mantém vermelho junto de data pendente');"
subprocess.run([os.environ.get('NODE_BINARY','node'),'-e',js],check=True)
