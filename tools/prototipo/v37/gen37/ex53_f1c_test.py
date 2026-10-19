"""EX53 F1c: regras reais, sem meta não classifica desempenho.
NODE_BINARY=/path/node python3 -B ex53_f1c_test.py [--base REF]
--base deve reprovar na versão anterior (contraprova).
"""
from pathlib import Path
import subprocess,os,argparse,json
p=argparse.ArgumentParser();p.add_argument('--base');a=p.parse_args()
def read(f):
    return subprocess.check_output(['git','show',a.base+':tools/prototipo/v37/gen37/'+f],text=True) if a.base else Path(f).read_text()
s=read('areas/inicio.py'); fn=s[s.index('function cls0('):s.index('// MUX-F2 (17/10/2026): cada classe')]
u=read('areas/inteligencia.py'); fs='\n'.join(l for l in u.splitlines() if l.startswith(('function ivSit(', 'function icSit(', 'function ivAbaixoRef(')))
probe=r'''
const assert=require('node:assert/strict');let cfg={};const cenGet=()=>cfg;
const isCar=()=>false,isIns=()=>false,SOLO_L='solo',COLH_L='colheita',OS_L='ordens';
let real={ha:1,shared:[],rs:100,prevExec:100};
const prevOf=()=>({fonte:true,base:1,tot:100}),cusReal=()=>real,mil=String,nfx=(v,d)=>v.toFixed(d),money=String;
for(const rs of [0,99.5,100,100.5,105,111,200]) {real.rs=rs; const r=cls0('Custos',{},'T');assert.equal(r.c,'gray');assert.match(r.l,/%/);}
real.prevExec=0;assert.match(cls0('Custos',{},'T').l,/sem previsto/);
real.ha=0;assert.equal(cls0('Custos',{},'T').c,'none');
assert.equal(cls0('Custos',{most:'Previsto R$/ha'},'T').c,'blue');
const prCmp=(a,b)=>Number(a)-Number(b);
for(const sp of [-.5,-.05,0,.05,.5]) {let s=ivSit({medC:10,spread:sp,amb:[],abaixo:false});assert.equal(s,sp<0?'Abaixo da referência':sp>0?'Acima da referência':'Na referência');}
assert.equal(ivAbaixoRef({spread:-.016}),true);
assert.equal(ivAbaixoRef({spread:null}),false);
assert.equal(icSit({melhor:{},vRef:.5,acima:false}),'Cotação acima da referência');
assert.equal(icSit({melhor:null,nVenc:1}),'Cotação vencida');
assert.equal(ivSit({medC:null,amb:['x']}),'Saca a conferir');
cfg={conf:{metas:{'custo-desvio':{valor:0,atencao:5,sentido:'menor',un:'%',escopo:'organizacao'}}}};
real={ha:1,shared:[],pend:[],rs:110,prevExec:100};assert.equal(cls0('Custos',{},'T').c,'red');
real.pend=['preço ausente'];assert.equal(cls0('Custos',{},'T').c,'gray');
real.pend=[];real.rs=100;assert.equal(cls0('Custos',{},'T').c,'ok');
cfg.conf.metas['custo-desvio'].ativa=false;assert.equal(cls0('Custos',{},'T').c,'gray');
console.log('PASS F1c: custos neutros, valor/ausência, comparação descritiva e cotação vencida');
'''
assert u.count('I.prods.filter(ivAbaixoRef)') == 2
assert "rk ? 'yellow' : 'gray'" in u
raise SystemExit(subprocess.run([os.environ.get('NODE_BINARY','node'),'-e',read('metas.js')+'\n'+fn+'\n'+fs+'\n'+probe]).returncode)
