"""EX53 F1: presentation must not invent targets or hide partial data.
Run NODE_BINARY=/path/to/node python3 -B ex53_metas_test.py [--source old/file.py].
The optional source permits a red counterproof against the unchanged base.
"""
import ast
import os
from pathlib import Path
import subprocess
import argparse

ap = argparse.ArgumentParser()
ap.add_argument('--source', default=str(Path(__file__).parent / 'areas/painel_gestao.py'))
args = ap.parse_args()
tree = ast.parse(Path(args.source).read_text())
js = next(ast.literal_eval(n.value) for n in tree.body if isinstance(n, ast.Assign)
          and any(isinstance(t, ast.Name) and t.id == 'JS' for t in n.targets))
js = js[:js.index('const PG_COR=')]
probe = r'''
const assert=require('node:assert/strict');
const partial={id:'g',cultura:'Soja',faz:'Demo',saf:'2026',area_ha:100,ha_exec:20,
 desvio_exec_pct:0,orcado_rs:1000,real_total_rs:200,parcial:true,pend:['preço ausente']};
function pnValores(){return {labels:[],vals:[null,2,1,1],bars:[]};}
function agrPainelRef(){return null;}
function agrCustoRef(){return {cultivos:[partial]};}
function osProjecaoEstado(){return [];}
function comPrecoTxt(c,v){return String(v);}
for(const d of [-1,0,.05,.11,1,null,undefined,NaN]) assert.equal(pgCor(d),'gray','sem meta não avalia conformidade');
let R={blocos:{agr:{},man:{}},itens:[]};
pgAgr({},R);
let cost=R.blocos.agr.cus[0];
assert.equal(cost.v,'0,0%');assert.equal(cost.cor,'gray');
assert.match(cost.sub,/Indicador parcial/);assert.match(cost.sub,/Meta não configurada/);
assert.equal(cost.href,'GE-03.dc.html');
pgMan({man:{ativos:{a:{id:'a',cond:'Bloqueado',seg:true},b:{id:'b',cond:'Apto'}}}},R);
let assets=R.blocos.man.atv;
assert.equal(assets[0].cor,'red','bloqueio real continua vermelho');
assert.equal(assets[1].v,'50%');assert.equal(assets[1].cor,'gray');
assert.match(assets[1].sub,/Meta não configurada/);assert.doesNotMatch(assets[1].dica,/95%/);
assert.equal(R.itens.find(x=>x.k==='atv:a').classe,1,'risco à segurança preservado');
let a=pgAlavancas({custos:[partial],precos:[{cu:'Soja',medC:10,ref:{p:10},amb:['saca sem massa']}]})[0];
assert.equal(a.cus,cost.v);assert.equal(a.cusc,'gray');assert.match(a.cons,/Indicador parcial/);
assert.equal(a.pre,'10');assert.equal(a.prec,'gray');assert.match(a.prer,/Indicador parcial/);
assert.match(a.prer,/Meta não configurada/);
assert.equal(pgK('Hoje','Teste',null,'','green','','').v,'Sem dados');
assert.equal(pgK('Hoje','Teste',null,'','green','','').cor,'gray');
console.log('PASS EX53: sem meta, parcial, valor/link, alavancas e impedimento real');
'''
raise SystemExit(subprocess.run([os.environ.get('NODE_BINARY','node'),'-e',js+'\n'+probe]).returncode)
