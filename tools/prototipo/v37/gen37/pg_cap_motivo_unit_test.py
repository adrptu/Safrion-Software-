# -*- coding: utf-8 -*-
"""EX-53 D11b · motivo de não haver semanas equivalentes no cartão "Backlog da oficina" (pgCapMotivo, areas/painel_gestao.py), com os comandos
reais da CF-06 e da CD-04 (capacidadeGravar, pessoasGravar; PR #132), no node, sem navegador.
Achado do Codex no PR #134 (4311510516): pessoa removida da CD-04 com dedicação ativa dizia "não configurada" em vez de "a revisar".
  M1 nada configurado: "capacidade semanal não configurada"
  M2 30 HH/semana de Mecânico para o Zé: capacidadeDe dá 30 (o motivo não se aplica)
  M3 o calendário da Oficina muda: capacidadeDe null e o motivo é "a revisar"
  M4 o Zé sai da CD-04 com a dedicação ativa: capacidadeDe null e o motivo é "a revisar" (não "não configurada")
  M5 a dedicação é retirada na CF-06: o motivo volta a "não configurada"
  M6 Zé 30 e Otávio 20 de Mecânico; o Zé sai da CD-04: capacidadeOrfas lista o Zé e o total fica suspenso (null, nunca 20 como se fosse completo)
  M7 retirada versionada da dedicação órfã: capacidadeDe volta a 20 HH/semana (1 pessoa), a órfã some e o motivo não acusa "a revisar"
  M8 o histórico da órfã continua: duas versões (definida e retirada), com motivo e recibo
Contraprova: com o painel_gestao.py de 5401dc50, M4 reprova.
Uso: SAFRION_DADOS=sintetico python3 -B pg_cap_motivo_unit_test.py [caminho do painel_gestao.py]"""
import os, sys, json, re, subprocess
os.environ.setdefault('SAFRION_DADOS', 'sintetico')
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
ARQ = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'areas', 'painel_gestao.py')
OK = []
def ok(nome, cond, info=''):
    OK.append(bool(cond)); print(('OK    ' if cond else 'FALHA ') + nome + ('' if cond else ' · ' + str(info)[:600]), flush=True)

src = open(ARQ, encoding='utf-8').read()
m = re.search(r'^function pgCapMotivo\(c,esp\)\{.*?(?=^function )', src, re.M | re.S)   # a função inteira, até a seguinte
ok('M0 pgCapMotivo existe no gerador', bool(m), ARQ)
import cenario, dados_config
CASOS = r"""
const R=[]; const ok=(n,c,i)=>R.push({n,ok:!!c,info:c?'':JSON.stringify(i===undefined?'':i).slice(0,500)});
const ANA='Ana'; let k=0; const chave=()=>'t'+(++k);
try{
  const c={}; const ze=Object.entries(pessoasCapacidade(c)).find(([id,p])=>p.nome==='Zé');
  ok('M1 nada configurado: "capacidade semanal não configurada"', pgCapMotivo(c,'Mecânico')==='capacidade semanal não configurada', pgCapMotivo(c,'Mecânico'));
  const id=ze[0];
  const g=capacidadeGravar(c,id,{'Mecânico':30},'teste',0,ze[1].v,chave(),ANA);
  const cap=capacidadeDe(c,'Mecânico');
  ok('M2 30 HH/semana de Mecânico para o Zé: capacidadeDe = 30', !!cap&&cap.hhSemana===30, [g,cap]);
  const x=pessoasLer(c), es=JSON.parse(JSON.stringify(x.equipes)); es.find(e=>e.v.nome==='Oficina').v.cal='seg–sex · 08–18h';
  const d=JSON.parse(JSON.stringify(c)); pessoasGravar(d,JSON.parse(JSON.stringify(x.pessoas)),es,x.rev,chave(),ANA);
  ok('M3 calendário da Oficina mudou: sem capacidade e o motivo é "a revisar"', capacidadeDe(d,'Mecânico')===null&&/a revisar/.test(pgCapMotivo(d,'Mecânico')), [capacidadeDe(d,'Mecânico'),pgCapMotivo(d,'Mecânico')]);
  const e=JSON.parse(JSON.stringify(c)); const xe=pessoasLer(e); pessoasGravar(e,JSON.parse(JSON.stringify(xe.pessoas)).filter(p=>p.id!==id),JSON.parse(JSON.stringify(xe.equipes)),xe.rev,chave(),ANA);
  ok('M4 o Zé saiu da CD-04 com a dedicação ativa: sem capacidade e o motivo é "a revisar (pessoa saiu do cadastro…)"', !pessoasCapacidade(e)[id]&&capacidadeDe(e,'Mecânico')===null&&/pessoa saiu do cadastro/.test(pgCapMotivo(e,'Mecânico')), [capacidadeDe(e,'Mecânico'),pgCapMotivo(e,'Mecânico')]);
  const f=JSON.parse(JSON.stringify(c)); capacidadeGravar(f,id,null,'retirada',1,ze[1].v,chave(),ANA);
  ok('M5 dedicação retirada: o motivo volta a "não configurada"', capacidadeDe(f,'Mecânico')===null&&pgCapMotivo(f,'Mecânico')==='capacidade semanal não configurada', pgCapMotivo(f,'Mecânico'));
  const o2=JSON.parse(JSON.stringify(c)), ot=Object.entries(pessoasCapacidade(o2)).find(([i,p])=>p.nome==='Otávio');
  capacidadeGravar(o2,ot[0],{'Mecânico':20},'teste',0,ot[1].v,chave(),ANA); const g50=capacidadeDe(o2,'Mecânico');
  const xg=pessoasLer(o2); pessoasGravar(o2,JSON.parse(JSON.stringify(xg.pessoas)).filter(p=>p.id!==id),JSON.parse(JSON.stringify(xg.equipes)),xg.rev,chave(),ANA);
  const orf=capacidadeOrfas(o2);
  ok('M6 Zé 30 + Otávio 20; o Zé sai da CD-04: capacidadeOrfas lista o Zé e o total fica suspenso (null)', !!g50&&g50.hhSemana===50&&Object.keys(orf).join()===id&&capacidadeDe(o2,'Mecânico')===null, [g50,Object.keys(orf),capacidadeDe(o2,'Mecânico')]);
  const rz=capacidadeRegistro(o2,id); capacidadeGravar(o2,id,null,'saiu do cadastro',rz.v,rz.pessoaV,chave(),ANA); const g20=capacidadeDe(o2,'Mecânico');
  ok('M7 retirada versionada da órfã: capacidadeDe = 20 HH/semana (1 pessoa), nenhuma órfã e sem "a revisar"', !!g20&&g20.hhSemana===20&&g20.pessoas===1&&!Object.keys(capacidadeOrfas(o2)).length&&!/a revisar/.test(pgCapMotivo(o2,'Eletricista')), [g20,Object.keys(capacidadeOrfas(o2)),pgCapMotivo(o2,'Eletricista')]);
  const hz=((o2.conf&&o2.conf.ev)||[]).filter(e=>e.tipo==='capacidade'&&e.alvo===id);
  ok('M8 o histórico da órfã continua: definida e retirada, com motivo e recibo', hz.map(e=>e.t).join('|')==='Dedicação semanal definida|Dedicação retirada'&&hz.every(e=>e.motivo&&e.id)&&capacidadeRegistro(o2,id).ativa===false&&capacidadeRegistro(o2,id).v===2, hz.map(e=>[e.t,e.motivo,e.id]));
}catch(e){ R.push({n:'exceção',ok:false,info:String(e&&e.stack||e).slice(0,500)}); }
console.log(JSON.stringify(R));
"""
if m:
    js = 'globalThis.print=(...a)=>console.log(...a);\n' + cenario.perfis_js() + dados_config.js_prefixo() + m.group(0) + '\n' + CASOS
    os.makedirs(os.path.join(HERE, '_probe'), exist_ok=True)
    p = os.path.join(HERE, '_probe', 'pg_cap_motivo_unit.js'); open(p, 'w', encoding='utf-8').write(js)
    r = subprocess.run(['node', p], capture_output=True, text=True, timeout=120)
    out = r.stdout.strip().splitlines()
    ok('motor JS (node) executou sem erro', r.returncode == 0 and out, r.stderr[-600:])
    for x in (json.loads(out[-1]) if out else []): ok(x['n'], x['ok'], x['info'])
print(f'RESULTADO: {"OK" if all(OK) else "FALHOU"} {sum(OK)}/{len(OK)}')
sys.exit(0 if all(OK) else 1)
