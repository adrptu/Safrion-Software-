"""EX57: data desconhecida não prova capacidade nem custo histórico."""
import ast, os, subprocess
from pathlib import Path
s=Path('safra.js').read_text()
cap=s[s.index('function capRec('):s.index('// <<< CAPACIDADE')]
nota=s[s.index('  const somaIns='):s.index('  const S=(lst,f)')]
av=s[s.index('  const avisos=(its)=>'):s.index('  const ETQ=')]
js=cap+'''\nconst assert=require('node:assert/strict');
for(const dt of [null,''])assert.equal(classeOc(dt,-1,null,null),'semdata');
assert.equal(classeOc('2028-01-01',-1,null,null),'fora');
let x={semPlano:[],cls:{semdata:1,cal:0},aPlano:10,outras:{}};
let oc=[{dt:null,mi:-1}];assert.equal(capVeredito({},oc,x).R,'R3');
x.cls.cal=1;oc.push({dt:'2026-10-20',mi:0,a:{op:'x',nome:'x'},rp:{itens:[]}});assert.equal(capVeredito({},oc,x).R,'R3');
const D2={hoje:'2026-10-19'},rs=x=>String(x),br=x=>x;let v={};
oc=[{dt:null,cins:100},{dt:'',cins:50},{dt:'2026-10-18',cins:20},{dt:'2026-10-20',cins:30}];
'''+nota+'''
assert(v.rs_nota.includes('20 com data antes'));assert(v.rs_nota.includes('30 de hoje'));assert(v.rs_nota.includes('150 sem data'));
const naConta=()=>false;
'''+av+'''
let alerts=avisos([{dt:null,rp:{causa:'',conflito:false,custoOk:true},saldo:0}]);assert(alerts.some(x=>x.t.includes('Data pendente')));
console.log('PASS classificação, veredito semdata/misto, custos100+50pendentes/20passados/30futuros e aviso da grade');
'''
subprocess.run([os.environ.get('NODE_BINARY','node'),'-e',js],check=True)
t=ast.parse(Path('dados2.py').read_text()); ns={};exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,ast.FunctionDef) and n.name=='classe_oc'],type_ignores=[]),'dados2','exec'),ns)
for d in [None,'']: assert ns['classe_oc'](d,-1,None,None)=='semdata'
