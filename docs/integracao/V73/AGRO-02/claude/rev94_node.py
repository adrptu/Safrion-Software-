# -*- coding: utf-8 -*-
"""rev94 · verificações sem navegador do AGRO-02 (revisão Claude do PR #94). Dados sintéticos. Uso: python3 -B rev94_node.py <gen37>
A · isola a verificação 9 (A2: a mesma com o ajuste proposto no patch) do quantidade_test.py (agDecIni real em toda vistoria da Lagoa; o arquivo inteiro aborta antes, por irrigação, já na base)
B · guarda da emissão (mipEmitir real, VIS-013): sem produto, sem dose, dose 0, rascunho "0,", texto, fora da bula → recusa com o motivo;
    dose explícita dentro da bula → O.S. em A liberar com essa dose e total = dose × área (oráculo Decimal).
C · registro cancelado e produto sem registro para a cultura × alvo travam na mesma regra."""
import os, sys, json, subprocess, tempfile
from decimal import Decimal, ROUND_HALF_UP
G = os.path.abspath(sys.argv[1]); os.chdir(G); sys.path.insert(0, G)
src = open(os.path.join(G, 'quantidade_test.py'), encoding='utf-8').read(); ns = {}
exec(src[src.index('LS = ('):src.index('JS_FLUXO = r"""')], ns)
import cenario, dados_mip, dados_irrigacao
from areas.processo_os import JS_NUCLEO
import areas.agronomia as AG
PRE = 'globalThis.print=(...a)=>console.log(...a);\n'
DOM = 'globalThis.document={getElementById:()=>null,querySelector:()=>null};globalThis.setTimeout=()=>0;\n'
JS = r"""
const out={q9:[],guarda:[]};
const s0=mipGet(); const maior=a=>a.tr.filter(x=>/Área maior/.test(x));
for(const v of Object.values(s0.vis).filter(v=>/^PV/.test(v.tal))){ const t=mipT(v); let st=null;
  agDecIni({state:{},setState:x=>{ st=x; }},v.id); const d=st.dec;
  const ck=(ar)=>mipChecks(mipGet(),v,{kind:d.kind,prod:d.prod,dose:d.dose,area:ar,data:d.data},cenGet());
  out.q9.push({vis:v.id,kind:d.kind,prod:d.prod,dose:d.dose,form:d.area,trava:maior(ck(d.area)),antes:d.kind==='controlar'&&maior(ck(mipN(t.area,1))).length>0,tr0:ck(d.area).tr[0]||''}); }
// A2 · o mesmo laço com o ajuste proposto em rev94_testes_obsoletos.patch (escolha explícita do 1º registrado não cancelado, dose mínima digitada)
out.q9b=[]; for(const v of Object.values(s0.vis).filter(v=>/^PV/.test(v.tal))){ const t=mipT(v); let st=null;
  agDecIni({state:{},setState:x=>{ st=x; }},v.id); const d=st.dec;
  const u=(d.kind==='controlar'||d.kind==='localizado')?mipElig(v).find(x=>x.sit!=='Cancelado'):null;
  const ck=(ar)=>mipChecks(mipGet(),v,{kind:d.kind,prod:u?u.id:'',dose:u?String(u.dmin):'',area:ar,data:d.data},cenGet());
  out.q9b.push({vis:v.id,kind:d.kind,form:d.area,vazio:d.prod===''&&d.dose==='',trava:maior(ck(d.area)),antes:d.kind==='controlar'&&maior(ck(mipN(t.area,1))).length>0}); }
const v13=mipGet().vis['VIS-013']; const u0=mipElig(v13)[0]; const area=String(mipT(v13).area); const data=mipAmanha();
for(const [nome,prod,dose] of [['sem produto','',''],['sem dose',u0.id,''],['dose 0',u0.id,'0'],['rascunho 0,',u0.id,'0,'],['texto',u0.id,'abc'],['fora da bula',u0.id,String(u0.dmax*3).replace('.',',')]]){
  cenReset(); mipReset(); const r=mipEmitir(null,'VIS-013',{kind:'controlar',prod,dose,area,data});
  out.guarda.push({nome,prod,dose,r,os:Object.keys(cenGet().ordens).filter(k=>{const o=cenGet().ordens[k]; return o.osc&&o.osc.novo&&(o.osc.novo.keys||[]).indexOf('mip|VIS-013|'+v13.prot)>=0;})}); }
cenReset(); mipReset(); const dz=String((u0.dmin+u0.dmax)/2).replace('.',',');
const r=mipEmitir(null,'VIS-013',{kind:'controlar',prod:u0.id,dose:dz,area,data}); const o=cenGet().ordens[r.os]||null;
out.ok={dose:dz,area,un:u0.un,dmin:u0.dmin,r,o:o?{id:o.id,etapa:o.etapa,ins:o.ins}:null,rec:Object.values(mipGet().rec).filter(x=>x.os===r.os).map(x=>({dose:x.dose,un:x.un,area:x.area}))};
// C · travas legais na mesma regra (mipChecks/cenUsoLegal, intocada pelo PR): registro cancelado e produto sem registro para cultura × alvo
cenReset(); mipReset(); { const s=mipGet(); const v17=s.vis['VIS-017']; const uc=mipElig(v17).find(x=>x.sit==='Cancelado');
  out.canc=uc?{nome:uc.nome,tr:mipChecks(s,v17,{kind:'controlar',prod:uc.id,dose:String(uc.dmin),area:String(mipT(v17).area),data:mipAmanha()},cenGet()).tr}:null;
  const fora=Object.values(MIPD.agf).flat().find(x=>!mipElig(v13).some(y=>y.id===x.id));
  out.semreg=fora?{nome:fora.nome,tr:mipChecks(s,v13,{kind:'controlar',prod:fora.id,dose:String(fora.dmin),area,data},cenGet()).tr,
    r:mipEmitir(null,'VIS-013',{kind:'controlar',prod:fora.id,dose:String(fora.dmin),area,data})}:null; }
print(JSON.stringify(out));
"""
f = tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8')
f.write(PRE + ns['LS'] + DOM + cenario.perfis_js() + cenario.js_prefixo() + JS_NUCLEO + dados_mip.js_prefixo() + dados_irrigacao.js_prefixo() + AG.JS_AG01 + JS); f.close()
p = subprocess.run(['node', f.name], capture_output=True, text=True, timeout=300); os.unlink(f.name)
if p.returncode: print(p.stderr[-1500:]); sys.exit(2)
F = json.loads(p.stdout.strip().splitlines()[-1]); OK = []
def chk(nome, cond, info=''):
    OK.append(bool(cond)); print(('OK    ' if cond else 'FALHOU ') + nome + ('' if cond else ' · ' + json.dumps(info, ensure_ascii=False)[:600]), flush=True)
ar = F['q9']; na = sum(1 for x in ar if x['antes'])
chk(f'A quantidade_test 9 isolado: agDecIni em {len(ar)} vistorias da Lagoa; {na} travariam com 1 casa (contraprova precisa de ≥ 1); nenhuma trava de área no formulário',
    len(ar) >= 8 and na >= 1 and not any(x['trava'] for x in ar), [[x['vis'], x['prod'], x['dose'], x['tr0']] for x in ar])
ar = F['q9b']; na = sum(1 for x in ar if x['antes'])
chk(f'A2 verificação 9 com o ajuste proposto: abre vazio em {sum(1 for x in ar if x["vazio"])}/{len(ar)}; {na} travariam com 1 casa; nenhuma trava de área no formulário',
    len(ar) >= 8 and na >= 1 and all(x['vazio'] for x in ar) and not any(x['trava'] for x in ar), ar)
esp = {'sem produto': 'Escolha um produto registrado.', 'sem dose': 'Informe a dose.', 'dose 0': 'Informe a dose.', 'rascunho 0,': 'Informe a dose.', 'texto': 'Informe a dose.'}
for g in F['guarda']:
    e = (g['r'] or {}).get('erro', '')
    alvo = esp.get(g['nome'])
    chk(f'B guarda mipEmitir ({g["nome"]}: prod={g["prod"]!r}, dose={g["dose"]!r}) recusa com "{e}" e não cria O.S.',
        (e == alvo if alvo else e.startswith('Dose fora da bula')) and not g['os'], g)
k = F['ok']; o = k['o']; tot = float((Decimal(k['dose'].replace(',', '.')) * Decimal(k['area'])).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
chk(f'B emissão com dose explícita {k["dose"]} {k["un"]}/ha × {k["area"]} ha: O.S. {o and o["id"]} em A liberar com essa dose (mínima {k["dmin"]}) e total {tot} {k["un"]}; receituário com a mesma dose',
    o and o['etapa'] == 'A liberar' and abs(o['ins'][0]['dose'] - float(k['dose'].replace(',', '.'))) < 1e-9 and abs(o['ins'][0]['tot'] - tot) < 1e-9 and o['ins'][0]['un'] == k['un']
    and k['rec'] and abs(k['rec'][0]['dose'] - float(k['dose'].replace(',', '.'))) < 1e-9, k)
cn = F['canc']; sr = F['semreg']
chk(f'C1 registro cancelado ({cn and cn["nome"]}, VIS-017 soja × daninhas) com dose da bula: trava "Registro cancelado: uso proibido."', cn and 'Registro cancelado: uso proibido.' in cn['tr'], cn)
chk(f'C2 produto sem registro para feijão × mosca-branca ({sr and sr["nome"]}) na VIS-013: trava "Sem registro para …" e mipEmitir recusa',
    sr and any(x.startswith('Sem registro para') for x in sr['tr']) and (sr['r'] or {}).get('erro', '').startswith('Sem registro para'), sr)
print(f'RESULTADO {sum(OK)}/{len(OK)}'); sys.exit(0 if all(OK) else 1)
