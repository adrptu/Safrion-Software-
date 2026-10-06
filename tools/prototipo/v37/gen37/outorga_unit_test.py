# -*- coding: utf-8 -*-
"""CTL-5 · E3 (RL-E4): outorga da captação com fonte única (o cadastro, dados_lagoa_fonte.LG_AGUA = aba Água do CD-01).
Defeito reproduzido na base 99537ca: a irrigação guardava a SINT-002/0000 com 573 L/s × 21 h/dia, vencida em 2023, "Em renovação";
o cadastro diz 150 m³/h = 41,67 L/s × 20 h/dia, vigente até 20/11/2026. A trava de vazão e o aviso usavam a cópia.
Monta cenario.js + IRR0 (dados_irrigacao.seed) + irrigacao_estado.js e roda os casos no node, sem navegador; a situação da outorga
no Python (agua_sit) é conferida contra a do CD-01 (aguaSit de areas/cad_fazendas.py). O esperado sai do cadastro, não de número
escrito à mão. Uso: python3 outorga_unit_test.py"""
import os, sys, re, json, subprocess, tempfile, datetime as dt
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); os.chdir(HERE)
sys.dont_write_bytecode = True
import cenario, dados_irrigacao as DI, dados_lagoa_fonte as F

OK, FAIL = [], []
def chk(nome, cond, info=''):
    (OK if cond else FAIL).append(nome); print(('OK    ' if cond else 'FALHA ') + nome + ('' if cond else ' · ' + str(info)[:600]), flush=True)

HOJE = str(DI.HOJE)
# ---------- oráculo do teste (independente do código): outorgas de captação superficial para irrigação do Rio A, vigentes hoje ----------
def l_s(v):
    m = re.match(r'([\d.,]+)\s*m³/h', v or ''); return float(m.group(1).replace('.', '').replace(',', '.')) / 3.6 if m else None
RIO = [a for a in F.LG_AGUA if a['tipo'] == 'Outorga' and a['modo'] == 'Captação superficial' and a['fin'] == 'Irrigação'
       and a['curso'] == 'Rio A (demonstração)' and a['venc'] >= HOJE]
LS = sum(l_s(a['vazao']) for a in RIO); VOL = sum(l_s(a['vazao']) * int(a['regime'].split()[0]) * 3.6 for a in RIO)
NUMS = ' + '.join(a['num'] for a in RIO)
print(f'oráculo (cadastro): {NUMS} · {LS:.2f} L/s · {VOL:.0f} m³/dia')

# ---------- Python: a irrigação lê o cadastro ----------
cp = DI.CAPT.get('LG-PAR', {})
chk('P1 dados_irrigacao: LG-PAR = soma das outorgas de irrigação do Rio A no cadastro (' + NUMS + ')',
    cp.get('outorga') == NUMS and abs(cp.get('ls', 0) - LS) < 1e-9 and abs(cp.get('ls', 0) * cp.get('h', 0) * 3.6 - VOL) < 1e-6, cp)
src = open(os.path.join(HERE, 'dados_irrigacao.py'), encoding='utf-8').read()
chk('P2 dados_irrigacao não guarda outro valor de outorga (sem ls=573, sem as cópias LG-STC e LG-BAR, sem datas de 2023/2024)',
    'ls=573' not in src and "'LG-STC'" not in src and "'LG-BAR'" not in src and '2023-11-22' not in src and '2024-02-13' not in src)
cap = getattr(F, 'captacao', None)
CASOS = {h: cap(F.LG_AGUA, h) for h in ('2026-11-21', '2033-07-01')} if cap else {}
# situação: Python (agua_sit) = CD-01 (aguaSit), nas 16 linhas do cadastro e em casos de borda
fsit = getattr(F, 'agua_sit', None)
cad = open(os.path.join(HERE, 'areas', 'cad_fazendas.py'), encoding='utf-8').read()
fn = re.search(r"function aguaSit\(V\)\{.*?return \{t:'Vigente'.*?\}; \}", cad, re.S).group(0)
borda = [dict(tipo='Outorga', venc='2026-12-22', renov=''), dict(tipo='Outorga', venc='2026-12-21', renov=''), dict(tipo='Outorga', venc='2026-09-22', renov=''),
         dict(tipo='Outorga', venc='2026-09-23', renov=''), dict(tipo='Outorga', venc='2020-01-01', renov='SINT-REN-1'), dict(tipo='', venc='2020-01-01', renov='')]
LIN = F.LG_AGUA + borda
js = ("const HOJE=" + json.dumps(HOJE) + "; function ddiff(a,b){ return Math.round((new Date(b+'T12:00:00')-new Date(a+'T12:00:00'))/86400000); }"
      "const br=x=>x, sitInfo=x=>x, chipc=x=>x, sitX=x=>x, sitOk=x=>x;\n" + fn + "\nconst L=" + json.dumps(LIN, ensure_ascii=False)
      + ";\nconsole.log(JSON.stringify(L.map(a=>aguaSit(a).t)));")
with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f: f.write(js)
sj = json.loads(subprocess.run(['node', f.name], capture_output=True, text=True, timeout=60).stdout); os.unlink(f.name)
sp = [fsit(a, HOJE) for a in LIN] if fsit else []
chk(f'P3 situação da outorga: Python = CD-01 nas {len(F.LG_AGUA)} linhas do cadastro e em {len(borda)} casos de borda (90 dias, vencida ontem, renovação, sem descrição)',
    sp == sj, [list(zip(sj, sp))[:6]])

fd = re.search(r"function aguaDoc\(V\)\{.*?\}", cad).group(0)
js = fd + "\nconsole.log(JSON.stringify([aguaDoc({tipo:'Outorga',num:'SINT-002/0000'}),aguaDoc({tipo:'Outorga estadual',num:'X-1'}),aguaDoc({tipo:'Certidão de uso insignificante',num:'SINT-006/0000'}),aguaDoc({tipo:'',num:'S'})]));"
with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f: f.write(js)
dd = json.loads(subprocess.run(['node', f.name], capture_output=True, text=True, timeout=60).stdout or '[]'); os.unlink(f.name)
chk('P4 CD-01 nomeia a outorga como a IR-04 ("Outorga SINT-002/0000"; antes "Certidão SINT-002/0000"); certidão continua certidão',
    dd == ['Outorga SINT-002/0000', 'Outorga X-1', 'Certidão SINT-006/0000', ''], dd)

# ---------- JS: estado da irrigação (irrigacao_estado.js) ----------
PRE = ("globalThis.print=(...a)=>console.log(...a);\nvar window={addEventListener(){}}; var location={hash:''};\n"
       "var __LS={}; var localStorage={getItem:k=>(k in __LS?__LS[k]:null),setItem:(k,v)=>{__LS[k]=String(v);},removeItem:k=>{delete __LS[k];}};\n")
JS = PRE + cenario.js_prefixo() + DI.js_prefixo() + ('const ESP=' + json.dumps(dict(nums=NUMS, ls=LS, vol=VOL), ensure_ascii=False)
      + ';\nconst CASOS=' + json.dumps(CASOS, ensure_ascii=False) + ';\n') + r'''
const R=[]; const ok=(n,f,info)=>{ let c=false, x=info; try{ const r=f(); c=r===true||(r&&r[0]===true); if(Array.isArray(r)) x=r[1]; }catch(e){ x='ERRO '+e.message; }
  R.push(c); console.log((c?'OK    ':'FALHA ')+n+(c?'':' · '+String(JSON.stringify(x)).slice(0,600))); };
const s=irrInicial(); const cp=s.capt['LG-PAR'];
ok('J1 trava: a captação dos pivôs vale o cadastro ('+ESP.nums+' · '+ESP.ls.toFixed(2)+' L/s)', ()=>[cp.outorga===ESP.nums&&Math.abs(cp.ls-ESP.ls)<1e-9&&Math.abs(cp.ls*cp.h*3.6-ESP.vol)<1e-6, cp]);
ok('J2 situação pela regra do cadastro: SINT-002/0000 vence em 20/11/2026 (≤ 90 dias) → aviso, não trava', ()=>[cp.st==='Vence em 90 dias'&&cp.aviso==='Outorga SINT-002/0000 vence em 20/11/2026', cp]);
ok('J3 sem cópia na irrigação: LG-STC e LG-BAR (sem setor ligado) só no cadastro; Santa Rita (sem aba Água) continua', ()=>[!s.capt['LG-STC']&&!s.capt['LG-BAR']&&!!s.capt['SR-RIO'], Object.keys(s.capt)]);
const g=Object.values(s.ordens).filter(o=>o.faz==='LG').map(o=>[o.id,o.setor,o.etapa,irrJanO(o)]);
ok('J4 tarefas automáticas da Lagoa Grande: 6 (PV02, PV08, PV09, PV18, PV21, PV24) a partir de OS-0601, Liberadas', ()=>[g.map(x=>x[1]).join()==='PV02,PV08,PV09,PV18,PV21,PV24'&&g[0][0]==='OS-0601'&&g.every(x=>x[2]==='Liberadas'), g]);
ok('J5 Pivô 2 continua "programada · hoje 21:00"', ()=>[irrSituacao(s,'PV02').l==='programada · hoje 21:00', irrSituacao(s,'PV02').l]);
const dia=[0,1,2,3,4,5].map(k=>{ let v=0; irrComprometidas(s,null).filter(w=>w.capt==='LG-PAR').forEach(w=>{ const a=Math.max(k*1440,w.ini),b=Math.min(k*1440+1440,w.fim); if(b>a) v+=w.ls*(b-a)*0.06; }); return Math.round(v); });
console.log('   volume comprometido por dia 23–28/09 (m³):', JSON.stringify(dia), '· limite', Math.round(ESP.vol));
ok('J6 trava diária: nenhum dia passa do volume outorgado no cadastro ('+Math.round(ESP.vol)+' m³)', ()=>[dia.every(v=>v<=ESP.vol+1e-6)&&dia.some(v=>v>0), dia]);
const prop=[{os:'X1',n:1,bomba:'B-PV09',capt:'LG-PAR',ls:s.setores.PV09.vazao,ini:2*1440+20*60,fim:2*1440+23*60},{os:'X2',n:1,bomba:'B-PV21',capt:'LG-PAR',ls:s.setores.PV21.vazao,ini:2*1440+20*60,fim:2*1440+23*60}];
const bq=()=>irrBloqJanela(s,s.setores.PV05,2*1440+21*60,2*1440+22*60,'novo',prop).map(b=>b.t);
ok('J7 NEGATIVO: PV09 + PV21 + PV05 juntos → "Sem vazão outorgada · … de 186 L/s" (gestor)', ()=>{ const b=bq(); return [b.some(t=>/^Sem vazão outorgada · \d+ de 186 L\/s$/.test(t)), b]; });
const nec=irrNec(s,'PV01'); const av=irrChecar(s,{id:'novo',faz:'LG',setor:'PV01',passadas:[{n:1,ini:21*60,dur:nec.dur,lam:nec.por,st:'Programada'}],exec:{pausas:[]}}).av.map(a=>a.t);
ok('J8 aviso de PV01: "Outorga SINT-002/0000 vence em 20/11/2026" (antes "Outorga em renovação")', ()=>[av.indexOf('Outorga SINT-002/0000 vence em 20/11/2026')>=0&&av.indexOf('Outorga em renovação')<0, av]);
const c1=CASOS['2026-11-21'], c2=CASOS['2033-07-01'];
ok('J9 NEGATIVO 21/11/2026: SINT-002/0000 vencida sai da soma (144 L/s) e fica na observação', ()=>[!!c1&&Math.abs(c1.ls-144.444444)<1e-3&&c1.outorga.indexOf('SINT-002')<0&&/fora da soma: SINT-002\/0000 vencida em 20\/11\/2026/.test(c1.obs), c1]);
const venc=()=>{ const s2=irrClone(IRR0); Object.assign(s2.capt['LG-PAR'],c2); s2.ger=false; irrGerar(s2); return [s2,Object.values(s2.ordens).filter(o=>o.faz==='LG')]; };
ok('J10 NEGATIVO todas vencidas (01/07/2033): captação "Vencida", 0 L/s; as 6 tarefas ficam A liberar', ()=>{ const [s2,g2]=venc(); return [c2.st==='Vencida'&&c2.ls===0&&g2.length===6&&g2.every(o=>o.etapa==='A liberar'), [c2,g2.map(o=>o.etapa)]]; });
ok('J11 todas vencidas: bloqueio "Outorga vencida" com o gestor (não só "Janela a definir" do irrigante) e próximo passo "Ajustar à outorga"', ()=>{ const [s2,g2]=venc();
  const b2=g2.map(o=>irrChecar(s2,o).bloq.map(b=>b.k+':'+b.dono).join('+')); const px=g2.map(o=>{ const p=irrProx(s2,o); return p.t+' · '+p.dono; });
  return [g2.length===6&&b2.every(x=>x==='outorga:Gestor da Lagoa Grande+jan:Joaquim')&&px.every(x=>x==='Ajustar à outorga · Gestor da Lagoa Grande'), [b2,px]]; });
ok('J12 exibição: "186 L/s × 19,6 h/dia · 13.120 m³/dia" (arredonda só a tela; uma conta só para o volume do dia)', ()=>{ const t=irrN(cp.ls)+' L/s × '+irrN(cp.h,1,0)+' h/dia · '+irrN(irrCapDia(cp))+' m³/dia'; return [t==='186 L/s × 19,6 h/dia · 13.120 m³/dia', t]; });
ok('J13 estado salvo com outra outorga (mesma versão) → a leitura repõe a do cadastro; a irrigação não guarda valor próprio', ()=>{ const v=irrClone(irrInicial()); v.capt['LG-PAR'].ls=573; v.capt['LG-PAR'].st='Em renovação';
  localStorage.setItem(IRR_KEY,JSON.stringify(v)); const r=irrGet().capt['LG-PAR']; localStorage.removeItem(IRR_KEY); return [Math.abs(r.ls-ESP.ls)<1e-9&&r.st==='Vence em 90 dias', r]; });
ok('J14 vencimento na tela: "até 20/11/2026"; vencida: "venceu em …"', ()=>{ const a=irrOutVenc(s,cp), b=irrOutVenc(s,{venc:'2023-11-22'}); return [a==='até 20/11/2026'&&b==='venceu em 22/11/2023'&&irrOutC('Vence em 90 dias')==='yellow'&&irrOutC('Vencida')==='red', [a,b]]; });
console.log('JS: '+R.filter(Boolean).length+'/'+R.length);
'''
with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f: f.write(JS)
r = subprocess.run(['node', f.name], capture_output=True, text=True, timeout=300); os.unlink(f.name)
print(r.stdout, end=''); print(r.stderr[-2000:], end='')
for ln in r.stdout.splitlines():
    if ln.startswith('OK    '): OK.append(ln)
    elif ln.startswith('FALHA '): FAIL.append(ln)
if r.returncode or 'JS: ' not in r.stdout: FAIL.append('node: execução interrompida')
print(f'\nRESULTADO {len(OK)}/{len(OK) + len(FAIL)}')
sys.exit(1 if FAIL else 0)
