"""D11: comandos reais e persistência sintética, sem navegador."""
from pathlib import Path
import subprocess, tempfile, os
import cenario, dados_assinatura as DA, dados_config as DC
p=Path(__file__).parent
src='''const assert=require('node:assert/strict');
let mem={};const localStorage={getItem:k=>mem[k]||null,setItem:(k,v)=>{mem[k]=v},removeItem:k=>delete mem[k]};
const window={addEventListener(){}};const location={hash:'',pathname:'',search:''};const history={replaceState(){}};
'''+(p/'g2lib.js').read_text()+DA.js_prefixo()+DC.js_prefixo()+cenario.js_prefixo()+r'''
const m={valor:90,atencao:80,sentido:'maior',un:'%'};
const run=(n,mot,v,key,ator='Ana')=>cenMudar(null,c=>metaGravar(c,'KPI-PCM-05',n,mot,v,key,ator),{estrito:true});
assert.match(run(m,'',0,'a').erro,/motivo/);
assert.match(run(m,'teste',0,'a','Rui').erro,/decisão/);
assert.equal(metaDe(cenGet(),'KPI-PCM-05'),null);
let r=run(m,'Plano anual',0,'a');assert.ok(!r.erro,r.erro);
const primeiro=JSON.stringify(cenGet().conf.metas);
assert.ok(run(m,'Plano anual',0,'a').repetido);assert.equal(JSON.stringify(cenGet().conf.metas),primeiro);
assert.match(run({...m,valor:95},'mudança',0,'b').erro,/mudou/);
assert.match(run({...m,valor:95},'mudança',1,'a').erro,/conflito/);
assert.ok(!run(null,'Reavaliar parâmetro',1,'c').erro);
assert.equal(metaDe(cenGet(),'KPI-PCM-05'),null);assert.equal(metaRegistro(cenGet(),'KPI-PCM-05').v,2);
assert.match(run(m,'rascunho antigo',0,'d').erro,/mudou/);
const antes=JSON.stringify(cenGet());const save=localStorage.setItem;localStorage.setItem=()=>{throw Error('quota')};
assert.match(run(m,'nova política',2,'d').erro,/Não foi possível gravar/);assert.equal(JSON.stringify(cenGet()),antes);localStorage.setItem=save;
assert.ok(!run(m,'nova política',2,'d').erro);
const k=cenGet().conf;assert.equal(k.ev.filter(e=>e.tipo==='meta').length,3);
assert.match(k.metas['KPI-PCM-05'].quem,/Ana/);assert.ok(k.metas['KPI-PCM-05'].d);assert.equal(k.metas['KPI-PCM-05'].motivo,'nova política');
console.log('PASS D11: permissão, motivo, idempotência, conflito, versão/retirada ABA, autoria e falha de gravação sem efeito.');
'''
with tempfile.NamedTemporaryFile('w',suffix='.js',delete=False) as f:f.write(src)
try:r=subprocess.run([os.environ.get('NODE_BINARY','node'),f.name],capture_output=True,text=True,timeout=120)
finally:os.unlink(f.name)
print(r.stdout,end='');print(r.stderr,end='');raise SystemExit(r.returncode)
