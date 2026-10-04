# -*- coding: utf-8 -*-
"""Regressão focal SINT-C03 (comentário 5974993475) e PRE-REV-20261004: regra única de quantidade de insumo (quantidade.py ⇄
cenQtd/cenQtdTrecho do cenario.js), o apontamento com custódia e todo produtor de total de insumo (O.S., MIP, fertirrigação).
Roda o JS real do protótipo (cenario.js + núcleo da O.S. + mip.js + irrigacao_estado.js) no jsc (macOS) ou node (Linux), sem navegador.
Uso (de gen37/): python3 quantidade_test.py"""
import json, os, random, re, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import quantidade as Q, cenario, dados_mip, dados_irrigacao
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
casos = [(d, a) for d in doses for a in areas] + [(1e-7, 28.7), (2.5e-7, 62.25), (1e21, 2), (123456789.123, 98765.43), (0.005, 1), (0.004, 1)]
py = [Q.qtd(d, a) for d, a in casos]

JS = r"""
const R={};
// 1 · igualdade com o Python
R.grade=CASOS.map(([d,a])=>{ try{ return cenQtd(d,a); }catch(e){ return 'ERRO '+e.message; } });
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
// 6 · a trava de custódia continua: consumo acima do que está em custódia é recusado, sem gravar nada (web e app)
function recusa(){ const f=fixture(62.25); const it=f.c.reqs['REQ-DEMO'].itens[0]; it.custodia=31.12;   // custódia menor que o consumo 31,13
  const w={}; try{ osc_apontar(f.c,'DEMO','24/09',62.25); w.erro=''; }catch(e){ w.erro=e.message; }
  Object.assign(w,{ap:f.c.ordens.DEMO.ap.length,custodia:it.custodia,consumido:it.consumido,realizado:f.c.ordens.DEMO.realizado});
  const g=fixture(62.25); const c=g.c; const it2=c.reqs['REQ-DEMO'].itens[0]; it2.custodia=31.12; c.app={online:true,fila:[],turno:{os:'DEMO',ini:'08:00'},operador:'Teste'}; c.movs=[];
  const a={}; try{ cenFecharTurno(c,62.25,4,{},'',[]); a.erro=''; }catch(e){ a.erro=e.message; }
  Object.assign(a,{ap:c.ordens.DEMO.ap.length,custodia:it2.custodia,consumido:it2.consumido}); return {web:w,app:a}; }
R.recusa=recusa();
// 4 · sementes da Lagoa em execução: o saldo restante consome exatamente a custódia de cada item
R.lagoa=['OS-0506','OS-0507'].map(id=>{ const c=JSON.parse(JSON.stringify(CEN0)); const o=c.ordens[id]; const r=c.reqs[o.req]; let erro='';
  try{ osc_apontar(c,id,'24/09',o.saldo); }catch(e){ erro=e.message; }
  return {id,erro,saldo:o.saldo,custodias:r.itens.map(i=>i.custodia),consumido_vs_total:r.itens.map(i=>[i.consumido,i.solicitado])}; });
print(JSON.stringify(R));
"""
# 7/8 · produtores de total fora da O.S.: MIP (mipEmitir) e fertirrigação (irrReclassTudo), percorrendo liberar → entregar → confirmar →
# iniciar → apontar o saldo → conferência, como na tela. localStorage em memória (a tela grava no navegador).
LS = ('const __LS={};globalThis.localStorage={getItem:k=>(k in __LS?__LS[k]:null),setItem:(k,v)=>{__LS[k]=String(v)},'
      'removeItem:k=>{delete __LS[k]}};\n')
JS_FLUXO = r"""
(()=>{   // escopo próprio: os prefixos das telas já declaram nomes curtos
function fluxo(c,id,res){ const o=c.ordens[id]; res.area=o.area; res.tot=o.ins[0].tot; res.regra=cenQtd(o.ins[0].dose,o.area);
  const passo=(n,f)=>{ try{ f(); }catch(e){ res.erro=n+': '+e.message; throw e; } };
  // o assunto aqui é a custódia, não a falta de estoque: completa o lote antes de liberar (só no teste)
  (o.ins||[]).forEach(x=>{ const l=cenLote(c,x.p); if(l&&cenDisp(l)<x.tot) l.fisico+=x.tot; });
  try{ passo('liberar',()=>osc_liberar(c,id,false,''));
    const rq=c.reqs[o.req]; for(const it of rq.itens){ const q=cenSaldoEntregar(it); if(q>1e-9) passo('entregar',()=>cenEntregar(c,o.req,it.prod,q,'X')); }
    passo('confirmar',()=>cenConfirmarRecebimento(c,o.req)); passo('iniciar',()=>osc_iniciar(c,id));
    passo('apontar o saldo',()=>osc_apontar(c,id,'20/10',o.saldo)); passo('conferência',()=>osc_conferencia(c,id)); }catch(e){}
  const it=o.req&&c.reqs[o.req]&&c.reqs[o.req].itens[0]; res.custodia=it?it.custodia:null; res.etapa=o.etapa; return res; }
const R={mip:[],fert:[],area:[]};
const s0=mipGet(); const maior=a=>a.tr.filter(x=>/Área maior/.test(x));
// formulário "Decidir controle" (agDecIni real do AG-01), em toda vistoria da Lagoa: o que ele preenche passa nas checagens de área
if(typeof agDecIni==='function') for(const v of Object.values(s0.vis).filter(v=>/^PV/.test(v.tal))){ const t=mipT(v); let st=null;
  agDecIni({state:{},setState:x=>{ st=x; }},v.id); const d=st.dec;
  const ck=(ar)=>mipChecks(mipGet(),v,{kind:d.kind,prod:d.prod,dose:d.dose,area:ar,data:d.data},cenGet());
  R.area.push({vis:v.id,kind:d.kind,form:d.area,trava:maior(ck(d.area)),antes:d.kind==='controlar'&&maior(ck(mipN(t.area,1))).length>0}); }
// emissão pelo MIP: área do talhão e a maior área em que 3 casas ficariam ABAIXO da regra única (o caso que recusava o apontamento)
const tres=(dose,ar)=>Math.round(dose*ar*1000)/1000;
const sobe=(dose,max)=>{ for(let k=0;k<400;k++){ const ar=Math.round(max*100-k)/100; if(ar<=0) break; if(tres(dose,ar)<cenQtd(dose,ar)) return ar; } return null; };
const vis=Object.values(s0.vis).filter(v=>/^PV/.test(v.tal)&&!v.dec&&mipElig(v).length);
for(const v of vis){ const t=mipT(v);
  for(const u of mipElig(v)){ if(u.sit==='Cancelado') continue; for(const [dose,area] of [[u.dmin,t.area],[u.dmax,t.area],[u.dmin,sobe(u.dmin,t.area)]]){ if(!area) continue; cenReset(); mipReset();
    if(!cenLote(cenGet(),u.nome)){ R.semLote=(R.semLote||0)+1; continue; }   // produto sem lote no Estoque: a liberação recusa (outra trava)
    const a={kind:'controlar',prod:u.id,dose:String(dose),area:String(area),data:'2026-10-20',nota:''}; const res={vis:v.id,prod:u.nome,dose,sobe:tres(dose,area)<cenQtd(dose,area)};
    const k=mipChecks(mipGet(),mipGet().vis[v.id],a,cenGet()); if(k.tr.length){ res.trava=k.tr; R.mip.push(res); continue; }
    const r=mipEmitir(null,v.id,a); if(r.erro){ res.erro='emitir: '+r.erro; R.mip.push(res); continue; } const c=cenGet();
    const id=Object.keys(c.ordens).find(x=>c.ordens[x].osc&&c.ordens[x].osc.novo&&(c.ordens[x].osc.novo.keys||[]).indexOf('mip|'+v.id+'|'+v.prot)>=0);
    R.mip.push(fluxo(c,id,res)); } } }
const i0=irrGet(); const ords=Object.keys(i0.ordens).filter(k=>['A liberar','Liberadas','Em execução'].indexOf(i0.ordens[k].etapa)>=0&&!i0.ordens[k].fert);
for(const id of ords){ for(const dose of [1,7,12,50]){ cenReset(); irrReset(); const res={id,dose};
  const r=irrReclassTudo(null,id,{prod:'Nitrato de cálcio',dose,mot:'teste'}); if(r.erro){ res.recusa=r.erro; R.fert.push(res); continue; }
  res.msg=r.msg; R.fert.push(fluxo(cenGet(),id,res)); } }
// v2 com passada em curso (avanço com 2 casas): a O.S. recebe o que falta (2 casas, irrAreaV2, a mesma conta da prévia) e v1 + v2 = área do setor
R.parc=[]; for(const id of ords.filter(k=>i0.ordens[k].etapa==='Liberadas')){ for(const cob of [20.27,0.05]){ cenReset(); irrReset(); const res={id,cob};
  try{ const s=irrGet(); irrIniciar(s,id); irrAvanco(s,id,Math.min(cob,s.setores[s.ordens[id].setor].ha)); irrSave(s); }catch(e){ res.recusa=e.message; R.parc.push(res); continue; }
  const r=irrReclassTudo(null,id,{prod:'Nitrato de cálcio',dose:12,mot:'teste'}); if(r.erro){ res.recusa=r.erro; R.parc.push(res); continue; }
  const s1=irrGet(), o1=s1.ordens[id], x1=s1.setores[o1.setor]; res.ha=x1.ha; res.v1=o1.fert.v1; res.prev=irrAreaV2(x1,{cob:o1.fert.v1});
  R.parc.push(fluxo(cenGet(),id,res)); } }
print(JSON.stringify(R));
})();
"""

def roda(src):
    f = tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8'); f.write(src); f.close()
    p = subprocess.run(MOTOR + [f.name], capture_output=True, text=True, timeout=300); os.unlink(f.name)
    if p.returncode != 0: print(p.stderr[-1500:]); sys.exit(1)
    return json.loads(p.stdout.strip().splitlines()[-1])
R = roda(PRELUDIO + cenario.js_prefixo() + JS_NUCLEO + '\nconst CASOS=' + json.dumps(casos) + ';\n' + JS)
import areas.agronomia as AG
DOM = 'globalThis.document={getElementById:()=>null,querySelector:()=>null};globalThis.setTimeout=()=>0;\n'   # agFoco sem tela
F = roda(PRELUDIO + LS + DOM + cenario.js_prefixo() + JS_NUCLEO + dados_mip.js_prefixo() + dados_irrigacao.js_prefixo() + AG.JS_AG01 + JS_FLUXO)

dif = [(c, a, b) for c, a, b in zip(casos, py, R['grade']) if a != b]
empates = [c for c in casos if (round(c[0] * c[1] * 1000) % 10 == 5)]
chk(f'1 regra única: Python qtd = JS cenQtd em {len(casos)} casos ({len(empates)} com empate no 3º decimal; notação exponencial e valores extremos sem erro); 0,5 × 62,25 = 31,13 (meio para cima)',
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
w, a = R['recusa']['web'], R['recusa']['app']
chk('6 trava de custódia executada: 31,13 contra 31,12 em custódia é recusado na web e no app, sem apontamento nem baixa (sem tolerância nova)',
    'acima do que está em custódia' in w['erro'] and w['ap'] == 0 and w['custodia'] == 31.12 and w['consumido'] == 0 and w['realizado'] == 0
    and 'acima do que está com você' in a['erro'] and a['ap'] == 0 and a['custodia'] == 31.12 and a['consumido'] == 0, R['recusa'])
ok = lambda x: not x.get('erro') and not x.get('trava') and x['tot'] == x['regra'] and abs(x['custodia']) < 1e-9 and x['etapa'] == 'Em conferência'
m = F['mip']
ne = sum(1 for x in m if x['sobe'])
chk(f'7 MIP → O.S. ({len(m)} emissões nos pivôs da Lagoa, doses da bula; {ne} em que o total antigo de 3 casas ficaria abaixo do consumo; '
    f'{F.get("semLote", 0)} sem lote no Estoque, fora): total = regra única; liberar, entregar, iniciar e apontar o saldo zeram a custódia e levam à '
    'conferência', len(m) >= 6 and ne >= 2 and all(map(ok, m)), [x for x in m if not ok(x)][:4])
fe = F['fert']; fa = [x for x in fe if 'recusa' not in x]
pc = [x for x in F['parc'] if 'recusa' not in x]
PREV = open(os.path.join(HERE, 'areas', 'irrigacao.py'), encoding='utf-8').read()   # a prévia da tela usa a mesma função e a mesma regra
prev_ok = 'const area=irrAreaV2(x,pa);' in PREV and "irrN(cenQtd(n,area),2)" in PREV
okp = lambda x: prev_ok and ok(x) and abs(x['v1'] + x['area'] - x['ha']) < 1e-9 and x['area'] == x['prev'] and round(x['area'], 2) == x['area']
chk(f'8 fertirrigação → O.S. ({len(fa)} v2 de {len(fe)} tentativas, 1 a 50 kg/ha; {len(pc)} com passada em curso): total = regra única, com 2 casas na '
    'mensagem; com passada em curso, a O.S. recebe o que falta com 2 casas (= prévia) e v1 + v2 = área do setor; o saldo apontado zera a custódia',
    len(fa) >= 8 and all(map(ok, fa)) and all(re.search(r'requisição de [0-9.]+(,[0-9]{1,2})? kg', x['msg']) for x in fa) and len(pc) >= 2 and all(map(okp, pc)),
    [x for x in fa if not ok(x)][:4] or [x for x in pc if not okp(x)][:4] or [x['msg'][-90:] for x in fa][:2])
ar = F['area']
na = sum(1 for x in ar if x['antes'])
chk(f'9 "Decidir controle" (agDecIni em {len(ar)} vistorias da Lagoa): a área que o formulário preenche nunca passa do talhão '
    f'(com 1 casa, {na} travariam)', len(ar) >= 8 and na >= 1 and not any(x['trava'] for x in ar), [x for x in ar if x['trava']])
# 10 · varredura de todo o gen37 (JS e JS embutido nos .py, sem testes): produto dose × área fora da regra única. Exceções nomeadas, que não
#      são quantidade de custódia: custo (dose × preço), carga do tanque e demanda do planejamento (CAL-01, exata por desenho).
import glob
PROD = re.compile(r'(?:\b[\w.]*dose\s*\*\s*[\w.(\[\'\]]+|[\w.)\]]+\s*\*\s*[\w.]*\.dose\b|\bd\s*\*\s*(?:ar|ajA)\b)')
EXC = {('areas/inicio.py', 'x.dose*p'): 'custo por ha', ('areas/processo_os.py', 'x.dose*ac'): 'carga do tanque', ('areas/processo_planos.py', 'x.dose*x.preco'): 'custo',
       ('areas/suprimentos.py', "dose*c['area']"): 'demanda do planejamento', ('dados2.py', "dose*c['area']"): 'demanda do planejamento',
       ('safra.js', 'dose*area'): 'demanda do planejamento (CAL-01)'}
crus = []
for fn in sorted(glob.glob(os.path.join(HERE, '*.js')) + glob.glob(os.path.join(HERE, '*.py')) + glob.glob(os.path.join(HERE, 'areas', '*.py'))):
    rel = os.path.relpath(fn, HERE)
    if re.search(r'(_test|test|_unit|verif_)', os.path.basename(fn)): continue
    for i, ln in enumerate(open(fn, encoding='utf-8'), 1):
        for mm in PROD.finditer(ln):
            if (rel, mm.group(0)) not in EXC: crus.append((rel, i, mm.group(0)))
tots = re.findall(r'tot\s*:\s*(?:Math\.round|Number\(|[^,}]*toFixed)', ''.join(open(os.path.join(HERE, n), encoding='utf-8').read() for n in ('mip.js', 'irrigacao_estado.js', 'cenario.js')) + JS_NUCLEO)
chk(f'10 varredura de todo o gen37: nenhum dose × área fora da regra única (exceções nomeadas: {len(EXC)}) e nenhum tot: arredondado por conta própria',
    not crus and not tots, [crus[:6], tots])
print(f'RESULTADO: {sum(OK)}/{len(OK)}')
sys.exit(0 if all(OK) else 1)
