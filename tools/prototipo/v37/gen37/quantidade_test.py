# -*- coding: utf-8 -*-
"""Regressão focal SINT-C03 (comentário 5974993475): regra única de quantidade de insumo (quantidade.py ⇄ cenQtd/cenQtdTrecho do
cenario.js) e o apontamento com custódia. Roda o JS real do protótipo (cenario.js + núcleo da O.S.) no jsc (macOS) ou node (Linux),
sem navegador. Uso (de gen37/): python3 quantidade_test.py"""
import json, os, random, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import quantidade as Q, cenario
from areas.processo_os import JS_NUCLEO
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'
MOTOR, PRELUDIO = ([JSC], '') if os.path.exists(JSC) else (['node'], 'globalThis.print=(...a)=>console.log(...a);\n')
OK = []
def chk(nome, cond, info=''):
    OK.append(bool(cond)); print(('OK    ' if cond else 'FALHOU ') + nome + ('' if cond else ' · ' + str(info)[:500]), flush=True)

# grade determinística: doses do protótipo × áreas com 2 casas, com empates (…,5 no 3º decimal) forçados
r = random.Random(20261004)
doses = [0.1, 0.25, 0.3, 0.4, 0.5, 1, 1.5, 2.5, 3, 20, 25, 30, 40, 45, 50, 150, 400, 1850, 2000]
areas = [62.25, 62.79, 30.55, 31.7, 0.01, 0.05, 48.47, 50.63, 73.18] + [round(r.uniform(0.01, 200), 2) for _ in range(400)]
casos = [(d, a) for d in doses for a in areas]
py = [Q.qtd(d, a) for d, a in casos]

JS = r"""
const R={};
// 1 · igualdade com o Python
R.grade=CASOS.map(([d,a])=>cenQtd(d,a));
// 2 · osc_apontar EXATO do núcleo da O.S., com custódia = total (quantidade da área da ordem)
function fixture(area){ const tot=cenQtd(0.5,area); return {tot,c:{ordens:{DEMO:{id:'DEMO',etapa:'Em execução',area,saldo:area,realizado:0,ap:[],req:'REQ-DEMO',
  ins:[{p:'Produto sintético',dose:0.5,un:'L',tot}]}},reqs:{'REQ-DEMO':{itens:[{prod:'Produto sintético',un:'L',custodia:tot,consumido:0}]}}}}; }
function apontar(area,partes){ const f=fixture(area); const out={area,tot:f.tot,erros:[],n:0};
  for(const h of partes){ try{ osc_apontar(f.c,'DEMO','24/09',h); out.n++; }catch(e){ out.erros.push(e.message); } }
  const o=f.c.ordens.DEMO, it=f.c.reqs['REQ-DEMO'].itens[0];
  Object.assign(out,{custodia:it.custodia,consumido:it.consumido,saldo:o.saldo,realizado:o.realizado,somaAp:o.ap.reduce((s,a)=>s+(a.cons['Produto sintético']||0),0)}); return out; }
R.apontar=[apontar(62.25,[62.25]),apontar(62.79,[62.79]),apontar(62.25,[30.55,31.7]),apontar(62.25,[20.01,20.02,22.22]),apontar(73.18,[0.05,36.5,36.63])];
// 3 · turno do app (cenFecharTurno) em dois trechos, mesma custódia
function turno(area,partes){ const f=fixture(area); const c=f.c; c.app={online:true,fila:[],turno:null,operador:'Teste'}; c.movs=[]; const out={area,tot:f.tot,erros:[]};
  for(const h of partes){ try{ c.app.turno={os:'DEMO',ini:'08:00'}; cenFecharTurno(c,h,4,{},'',[]); }catch(e){ out.erros.push(e.message); } }
  const it=c.reqs['REQ-DEMO'].itens[0]; Object.assign(out,{custodia:it.custodia,consumido:it.consumido,saldo:c.ordens.DEMO.saldo}); return out; }
R.turno=[turno(62.25,[62.25]),turno(62.25,[30.55,31.7])];
// 4 · sementes da Lagoa em execução: o saldo restante consome exatamente a custódia de cada item
R.lagoa=['OS-0506','OS-0507'].map(id=>{ const c=JSON.parse(JSON.stringify(CEN0)); const o=c.ordens[id]; const r=c.reqs[o.req]; let erro='';
  try{ osc_apontar(c,id,'24/09',o.saldo); }catch(e){ erro=e.message; }
  return {id,erro,saldo:o.saldo,custodias:r.itens.map(i=>i.custodia),consumido_vs_total:r.itens.map(i=>[i.consumido,i.solicitado])}; });
print(JSON.stringify(R));
"""
src = PRELUDIO + cenario.js_prefixo() + JS_NUCLEO + '\nconst CASOS=' + json.dumps(casos) + ';\n' + JS
f = tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8'); f.write(src); f.close()
p = subprocess.run(MOTOR + [f.name], capture_output=True, text=True, timeout=120); os.unlink(f.name)
if p.returncode != 0: print(p.stderr[-1500:]); sys.exit(1)
R = json.loads(p.stdout.strip().splitlines()[-1])

dif = [(c, a, b) for c, a, b in zip(casos, py, R['grade']) if a != b]
empates = [c for c in casos if (round(c[0] * c[1] * 1000) % 10 == 5)]
chk(f'1 regra única: Python qtd = JS cenQtd em {len(casos)} casos ({len(empates)} com empate no 3º decimal); 0,5 × 62,25 = 31,13 (meio para cima)',
    not dif and Q.qtd(0.5, 62.25) == 31.13 and Q.qtd(0.5, 62.79) == 31.4, dif[:5])
a = R['apontar']
chk('2 SINT-C03: apontamento cheio de 62,25 ha e de 62,79 ha passa; custódia 0; consumido = total; saldo 0',
    all(not x['erros'] and x['n'] == 1 and abs(x['custodia']) < 1e-9 and abs(x['consumido'] - x['tot']) < 1e-9 and x['saldo'] == 0 for x in a[:2]), a[:2])
chk('3 apontamentos parciais (2 e 3 trechos, inclusive 0,05 ha) conservam o total: soma dos consumos = total, custódia 0, realizado = área',
    all(not x['erros'] and abs(x['somaAp'] - x['tot']) < 1e-9 and abs(x['custodia']) < 1e-9 and abs(x['realizado'] - x['area']) < 1e-6 for x in a[2:]), a[2:])
t = R['turno']
chk('4 turno do app (cenFecharTurno), inteiro e em 2 trechos: consumo padrão pela mesma regra, custódia 0, saldo 0',
    all(not x['erros'] and abs(x['custodia']) < 1e-9 and abs(x['consumido'] - x['tot']) < 1e-9 and x['saldo'] < 1e-9 for x in t), t)
lg = R['lagoa']
chk('5 sementes da Lagoa (OS-0506 e OS-0507): apontar o saldo restante consome exatamente a custódia (0 em cada item), sem erro',
    all(not x['erro'] and x['saldo'] < 1e-9 and all(abs(cu) < 1e-9 for cu in x['custodias']) for x in lg), lg)
ctl = Q.qtd(0.5, 62.25) > 31.12
chk('6 controle de custódia preservado: consumo acima do que está em custódia continua recusado (sem tolerância nova)', ctl and 'acima do que está em custódia' in JS_NUCLEO, '')
print(f'RESULTADO: {sum(OK)}/{len(OK)}')
sys.exit(0 if all(OK) else 1)
