"""M5: contrato do cartão com o domínio real, incluindo contraprova encerradas-only."""
import ast
import os
from pathlib import Path
import subprocess
import cenario
import dados_manutencao as DM

p = Path(__file__).parent
js = next(ast.literal_eval(n.value) for n in ast.parse((p/'areas/painel_gestao.py').read_text()).body
          if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'JS' for t in n.targets))
js = js[:js.index('const PG_COR=')]
probe = r'''
const assert=require('node:assert/strict');
const c=manClone(MAN0), molde=Object.values(c.oms).find(o=>o.tipo==='Preventiva');
c.oms={};c.planos={};c.vinc={};
let k=pgPreventiva(c);
assert.equal(k.v,'Sem base no período');assert.equal(k.cor,'gray');
assert.match(k.sub,/12 m/);assert.match(k.sub,/Meta não configurada/);
assert.equal(k.href,'MA.dc.html#vis=ordens');
for(const [id,etapa,v,e] of [['a','Encerradas',-10,-12],['b','Encerradas',-20,-15],['c','Liberadas',-5,null]]){
 c.oms[id]=Object.assign(manClone(molde),{id,etapa,vencOrig:manAdd(c.hoje,v),exec:e===null?null:{data:manAdd(c.hoje,e)}});
}
k=pgPreventiva(c);
assert.equal(k.v,'33%');assert.match(k.sub,/1 de 3 preventivas/);
assert.match(k.sub,new RegExp(pgDdmm(manPeriodo(c,'12m').de)));assert.match(k.sub,new RegExp(pgDdmm(c.hoje)));
assert.equal(k.cor,'gray');assert.match(k.dica,/sem ordem/);
const real=manCumprimento;
manCumprimento=()=>({ok:1,n:2,pct:50,de:manPeriodo(c,'12m').de,ate:c.hoje});
assert.throws(()=>assert.equal(pgPreventiva(c).v,'33%'),'contador antigo deve reprovar');
manCumprimento=real;
assert.equal(pgPreventiva(c).v,'33%');
console.log('PASS M5: base vazia, domínio real 1/3, período, cor, destino e mutante 1/2');
'''
src = cenario.perfis_js()+DM.js_prefixo()+js+probe
# o código passa por arquivo temporário: no Linux, -e com o prelúdio inteiro estoura o limite de argumentos (E2BIG)
import tempfile
with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as tf: tf.write(src)
try: r=subprocess.run([os.environ.get('NODE_BINARY','node'),tf.name],capture_output=True,text=True,timeout=120)
finally: os.unlink(tf.name)
print(r.stdout, end='');print(r.stderr,end='')
raise SystemExit(r.returncode)
