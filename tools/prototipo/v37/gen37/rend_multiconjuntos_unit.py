# -*- coding: utf-8 -*-
"""Teste unitário puro · REND-MULTICONJUNTOS-20261003 (sem navegador, < 5 s).
Roda a MESMA função da tela (bloco REPARTIR de safra.js, no JavaScriptCore do macOS) e o espelho dados2.repartir (Python, com Fraction,
sem arredondar) contra o oráculo do pacote (12 casos Codex · multiconjuntos-oraculo.json), a contraprova Gemini de três conjuntos
(multiconjuntos-gemini-contraprova.json) e as bordas do PRD (rendimento ausente/zero, área zero, janela zero, tarifa desconhecida,
partes acima de 100 %, recurso compartilhado por grupo da fazenda). Cada caso imprime esperado, JS e Python; JS confere com tolerância
relativa 1e-9 (ponto flutuante), Python confere exato (Fraction).
Correções da verificação (rodada 2): a sequência respeita a janela ANTES de dividir a área (PRD 44.3 · casos 05c, S1–S5), a troca da
primeira configuração conta (começa a de menor troca · S3), a pendência diz a causa real (E1, E4, E9, E10), e 400 entradas aleatórias
conferem paridade JS × Python e as invariantes (Σ q + sem conjunto = Q, h ≤ janela própria, sequência ≤ janela da sequência).
REND-RETORNO-1818 (decisão Codex 7ae753dc): necessidade da demanda inteira, atendido na janela e saldo (área + horas) separados. S5 sai do
contrato (54/3,6 + 54/7,2 = 22,5 h necessárias, janela 10 h, déficit 12,5 h), não da saída antiga (17,5 h / 7,5 h, que cortava a parte A na
janela antes de somar); S1 tinha o mesmo corte (6 h → 70/9 h). Novos: S6 (partes fixas ao mesmo tempo, janela própria) e, em todo caso e nas
400 entradas, necessário = atendido + saldo em ha e em horas-conjunto.
PRE-REV-20261004 (pré-revisão do autor): R1 janela 0 numa sequência declarada mantém a necessidade e o déficit (S5 com a janela de A = 0);
R2 o grupo de recursos que junta uma sequência declarada com uma configuração sem janela não relaxa a janela da sequência (1 e 2
plantadeiras); R3 partes que somam 100 % em área grande não deixam resíduo; nas 400 entradas, a sequência declarada cabe na janela dela.
Uso: python3 rend_multiconjuntos_unit.py"""
import sys, os, json, re, subprocess, tempfile
from fractions import Fraction as F
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
import dados2 as D2
JSC='/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'
# jsc no macOS; fora dele (Linux/nuvem) o node, com print → console.log; o mesmo bloco REPARTIR nos dois
MOTOR,PRELUDIO=([JSC],'') if os.path.exists(JSC) else (['node'],'globalThis.print=(...a)=>console.log(...a);')
src=open(os.path.join(HERE,'safra.js')).read()
m=re.search(r'// >>> REPARTIR.*?// <<< REPARTIR',src,re.S); assert m, 'bloco REPARTIR não encontrado em safra.js'
BLOCO=m.group(0)
A=dict(id='A',nome='A 6 m',rend='RA',custo_h=180,diesel=12)          # A (6 m, 8 km/h, 75 %) e B (12 m, 8 km/h, 75 %): rendimento calculado
B=dict(id='B',nome='B 12 m',rend='RB',custo_h=300,diesel=20)
def cf(base,**kw): d=dict(base); d.update(kw); return d
# casos: (id, descrição, Q, configurações, grupos de recursos, {campo: esperado})
CASOS=[
 ('03 paralelo_proporcional_tempo_horas_conjunto','108 ha, 3,6 e 7,2 ha/h, divide pelo rendimento → 36/72 ha, 10 h decorridas, 20 horas-conjunto',
   108,[A,B],None,dict(q=['36','72'],decorrido='10',hconj='20',saldo='0')),
 ('04 particao_fixa_tempo_horas_conjunto','54/54 ha fixos → 15 h decorridas, 22,5 horas-conjunto',
   108,[cf(A,part=50),cf(B,part=50)],None,dict(q=['54','54'],decorrido='15',hconj='45/2')),
 ('05a recurso_compartilhado_troca','36/72 ha com o mesmo operador (sequência) e 1 h de troca → 21 h decorridas, 20 horas-conjunto',
   108,[cf(A,seq=True),cf(B,seq=True,troca=1)],None,dict(decorrido='21',hconj='20',troca='1',conflito=False,**{'nec.decorrido':'21','nec.hconj':'20','falta.hconj':'0'})),
 ('05b mesmo_trator_do_cadastro','mesmo trator a01 nas duas (sem marcar sequência) → em sequência: 20 h decorridas',
   108,[cf(A,ativos=['a01','a06']),cf(B,ativos=['a01','a10'])],None,dict(decorrido='20',hconj='20')),
 ('05c sequencia_nao_cabe_na_janela','a mesma sequência precisaria de 21 h numa janela de 12 h → conflito (faltam 9 h) e a área que não cabe fica sem conjunto: 2 × 5,5 h + 1 h de troca = 12 h; 19,8 + 39,6 = 59,4 ha; 48,6 ha sem conjunto',
   108,[cf(A,seq=True,jan=12),cf(B,seq=True,troca=1,jan=12)],None,dict(conflito=True,deficit='9',decorrido='12',hconj='11',q=['99/5','198/5'],alocado='297/5',saldo='243/5',
   nq=['36','72'],motivo='precisam de 21 h para 108 ha; a janela tem 12 h',**{'nec.hconj':'20','nec.decorrido':'21','falta.hconj':'9','falta.decorrido':'9'})),
 ('S1 sequencia_janela_3h_B4.3','42 ha, 3,6 e 7,2 ha/h em sequência, janela de 3 h → 1,5 h cada: 5,4 + 10,8 = 16,2 ha (≤ 21,6 possíveis), 25,8 ha sem conjunto (≥ 20,4), decorrido 3 h; necessário 42 ÷ 10,8 × 2 = 70/9 h (não 6 h: o plano não corta na janela), déficit 43/9 h',
   42,[cf(A,seq=True,jan=3),cf(B,seq=True,jan=3)],None,dict(q=['27/5','54/5'],alocado='81/5',saldo='129/5',decorrido='3',hconj='3',conflito=True,deficit='43/9',motivo=['mesma janela','precisam de 7,78 h para 42 ha; a janela tem 3 h'],
   **{'nec.decorrido':'70/9','falta.hconj':'43/9','falta.decorrido':'43/9'})),
 ('S2 sequencia_e_paralela','A e B em sequência (janela 3 h) e C 6 ha/h ao mesmo tempo, sem janela, 42 ha → A e B param em 1,5 h; C faz o resto: 5,4 + 10,8 + 25,8 ha, nada sem conjunto, decorrido 4,3 h',
   42,[cf(A,seq=True,jan=3),cf(B,seq=True,jan=3),dict(id='C',nome='C',rend=6,custo_h=200)],None,dict(q=['27/5','54/5','129/5'],saldo='0',decorrido='43/10',hconj='73/10',conflito=True,deficit='2',
   motivo='precisam de 5 h para 27 ha; a janela tem 3 h',**{'nec.hconj':'73/10','falta.hconj':'0','falta.decorrido':'0'})),
 ('S3 troca_na_primeira_P10b','troca de 2 h só na 1ª configuração: começa a de menor troca (B, 0 h) e A entra com 2 h → 22 h decorridas, 20 horas-conjunto',
   108,[cf(A,seq=True,troca=2),cf(B,seq=True)],None,dict(decorrido='22',hconj='20',troca='2')),
 ('S4 grupo_da_fazenda_com_janela','1 plantadeira na fazenda e janela de 12 h → em sequência, 6 h cada: 21,6 + 43,2 ha; 43,2 ha sem conjunto; precisaria de 20 h',
   108,[cf(A,rec={'plant':1},jan=12),cf(B,rec={'plant':1},jan=12)],{'plant':{'un':1,'nome':'Plantadeiras'}},dict(q=['108/5','216/5'],saldo='216/5',decorrido='12',conflito=True,deficit='8',motivo='Plantadeiras',
   **{'nec.decorrido':'20','falta.hconj':'8'})),
 ('S5 partes_fixas_em_sequencia','PRD 22.1 · 50 % + 50 % em sequência, janela de 10 h. Necessário (demanda inteira, partilha do usuário): 54/3,6 + 54/7,2 = 22,5 h; janela 10 h; déficit 12,5 h (a saída antiga, 17,5 h / 7,5 h, cortava A em 36 ha antes de somar). Atendido (sem mudar a distribuição): A 36 ha na própria janela, a sequência reduz as duas a 4/7 → 144/7 + 216/7 ha em 10 h; saldo 396/7 ha = faltam 12,5 horas-conjunto; necessário 54 + 54 ha = atendido + saldo',
   108,[cf(A,part=50,seq=True,jan=10),cf(B,part=50,seq=True,jan=10)],None,dict(q=['144/7','216/7'],alocado='360/7',saldo='396/7',hconj='10',decorrido='10',conflito=True,deficit='25/2',nq=['54','54'],
   motivo=['partes fixas em sequência não cabem na janela de 10 h: cada uma faz 57,14 %','precisam de 22,5 h para 108 ha; a janela tem 10 h'],
   **{'nec.area':'108','nec.hconj':'45/2','nec.decorrido':'45/2','falta.area':'396/7','falta.hconj':'25/2','falta.decorrido':'25/2','falta.semHoras':'0'})),
 ('S6 partes_fixas_ao_mesmo_tempo','50 % + 50 % ao mesmo tempo (recursos próprios), janela de 10 h cada: A precisa de 15 h para 54 ha e faz 36 ha; B faz 54 ha em 7,5 h → atendido 90 ha, saldo 18 ha = faltam 5 h (de A); necessário 22,5 horas-conjunto e 15 h decorridas; sem sequência, sem conflito',
   108,[cf(A,part=50,jan=10),cf(B,part=50,jan=10)],None,dict(q=['36','54'],alocado='90',saldo='18',hconj='35/2',decorrido='10',conflito=False,deficit='0',nq=['54','54'],motivo='parte fixa não cabe na janela',
   **{'nec.hconj':'45/2','nec.decorrido':'15','falta.hconj':'5','falta.decorrido':'5'})),
 ('06 capacidade_janela_saldo','36 ha, A 4 h e B 2 h disponíveis → 28,8 ha atendidos, 7,2 ha sem conjunto',
   36,[cf(A,jan=4),cf(B,jan=2)],None,dict(alocado='144/5',saldo='36/5',pendente=False,**{'nec.hconj':'22/3','falta.hconj':'4/3','falta.decorrido':'2/3'})),
 ('07a custos_proporcional','tarifas 180 e 300 R$/h, 36/72 ha → R$ 4.800',108,[A,B],None,dict(custo='4800',custoOk=True)),
 ('07b custos_fixo','54/54 ha → R$ 4.950',108,[cf(A,part=50),cf(B,part=50)],None,dict(custo='4950')),
 ('08 custo_unitario_proporcional','custo por ha = custo total ÷ área atendida = 400/9 (R$ 44,44…/ha), não média de custos',108,[A,B],None,dict(custoHa='400/9')),
 ('10a diesel_recalculado_por_hora','12 e 20 L/h, 36/72 ha → 320 L',108,[A,B],None,dict(diesel='320')),
 ('10b diesel_fixo','54/54 ha → 330 L',108,[cf(A,part=50),cf(B,part=50)],None,dict(diesel='330')),
 ('G1 gemini_tres_conjuntos','150 ha; 4,5/6/7,5 ha/h; janelas 10/8/5 h; 200/250/320 R$/h → 45/48/37,5 ha; 130,5 atendidos; 19,5 sem conjunto; 23 horas-conjunto; 10 h; R$ 5.600',
   150,[dict(id='X',nome='X',rend='9/2',jan=10,custo_h=200),dict(id='Y',nome='Y',rend=6,jan=8,custo_h=250),dict(id='Z',nome='Z',rend='15/2',jan=5,custo_h=320)],None,
   dict(q=['45','48','75/2'],alocado='261/2',saldo='39/2',hconj='23',decorrido='10',custo='5600',custoHa='11200/261',**{'nec.hconj':'105/4','nec.decorrido':'133/12','falta.hconj':'13/4','falta.decorrido':'13/12'})),
 ('E1 rendimento_ausente','rendimento vazio não divide 50 ha: pendente, sem horas (nunca 0 h), área sem conjunto, causa "sem rendimento"',
   50,[dict(id='S',nome='S',rend='',custo_h=100)],None,dict(pendente=True,hconj=None,decorrido=None,saldo='50',motivo='sem rendimento',causa='sem rendimento',**{'nec.hconj':None,'falta.hconj':None,'falta.semHoras':'50'})),
 ('E2 rendimento_zero','rendimento 0 não divide: pendente',50,[dict(id='S',nome='S',rend=0,custo_h=100)],None,dict(pendente=True,hconj=None,saldo='50')),
 ('E3 area_zero','área 0 é válida: 0 horas-conjunto, nada pendente',0,[A],None,dict(pendente=False,hconj='0',decorrido='0',saldo='0',**{'nec.hconj':'0','falta.hconj':'0'})),
 ('E4 janela_zero','janela 0 h com rendimento válido: sem capacidade, os 10 ha ficam sem conjunto; pendente com a causa "sem horas na janela" (não "sem rendimento")',10,[dict(id='J',nome='J',rend=5,jan=0,custo_h=100)],None,
   dict(alocado='0',saldo='10',motivo='janelas não comportam',pendente=True,hconj=None,causa='sem horas na janela',**{'nec.hconj':'2','falta.hconj':'2','falta.decorrido':'2'})),
 ('E9 sem_configuracao','atividade sem configuração: pendente com a causa "sem conjunto"',10,[],None,dict(pendente=True,hconj=None,saldo='10',causa='sem conjunto')),
 ('E10 janela_zero_na_sequencia','a troca (3 h) passa a janela da sequência (2 h): nada cabe, pendente "sem horas na janela"',
   20,[cf(A,seq=True,jan=2,troca=3),cf(B,seq=True,jan=2,troca=3)],None,dict(pendente=True,hconj=None,saldo='20',causa='sem horas na janela')),
 ('E5 tarifa_desconhecida','tarifa vazia não vira R$ 0: custo não calculável, R$/ha vazio',108,[A,cf(B,custo_h='')],None,dict(custoOk=False,custoHa=None,motivo='tarifa desconhecida')),
 ('E6 partes_acima_de_100','70 % + 50 % → aviso e conservação (Σ q + sem conjunto = Q)',100,[dict(id='P',nome='P',rend=10,part=70,custo_h=1),dict(id='Q',nome='Q',rend=10,part=50,custo_h=1)],None,
   dict(motivo='partes fixas somam 120',conserva=True)),
 ('E7 invalida_na_divisao_pelo_rendimento','uma configuração sem rendimento na divisão pelo rendimento: a divisão fica pendente (não joga tudo na outra)',
   108,[A,cf(B,rend='')],None,dict(pendente=True,saldo='108',motivo='divisão pelo rendimento fica pendente')),
 ('E8a grupo_da_fazenda_1_plantadeira','duas configurações com plantadeira e a fazenda tem 1 → em sequência: decorrido = horas-conjunto',
   108,[cf(A,rec={'plant':1}),cf(B,rec={'plant':1})],{'plant':{'un':1,'nome':'Plantadeiras'}},dict(decorrido='20',hconj='20',motivo='Plantadeiras')),
 ('E8b grupo_da_fazenda_2_plantadeiras','com 2 plantadeiras trabalham ao mesmo tempo: 10 h',
   108,[cf(A,rec={'plant':1}),cf(B,rec={'plant':1})],{'plant':{'un':2,'nome':'Plantadeiras'}},dict(decorrido='10')),
 ('R1 janela_zero_na_sequencia_declarada','PRE-REV R1 · o S5 com a janela de A = 0: A não recebe área, mas a sequência declarada continua precisando de 54/3,6 + 54/7,2 = 22,5 h numa janela de 10 h (déficit 12,5 h, como com 0,01 h); B faz 54 ha em 7,5 h',
   108,[cf(A,part=50,seq=True,jan=0),cf(B,part=50,seq=True,jan=10)],None,dict(q=['0','54'],alocado='54',saldo='54',hconj='15/2',decorrido='15/2',conflito=True,deficit='25/2',nq=['54','54'],
   motivo=['parte fixa não cabe na janela de 0 h','precisam de 22,5 h para 108 ha; a janela tem 10 h'],**{'nec.decorrido':'45/2','falta.decorrido':'15'})),
 ('R2a grupo_de_recursos_nao_relaxa_janela_1','PRE-REV R2 · A e B em sequência declarada (janela 10 h), C sem janela; A e C usam plantadeira e a fazenda tem 1: a união por falta de plantadeira não tira a janela de A+B (5 h cada, 25 + 25 ha); C faz 150 ha; tudo em sequência: 40 h',
   200,[dict(id='A',nome='A',rend=5,seq=True,jan=10,rec={'plant':1},custo_h=100),dict(id='B',nome='B',rend=5,seq=True,jan=10,custo_h=100),dict(id='C',nome='C',rend=5,rec={'plant':1},custo_h=100)],
   {'plant':{'un':1,'nome':'Plantadeiras'}},dict(q=['25','25','150'],saldo='0',decorrido='40',conflito=True,deficit='50/3',motivo=['Plantadeiras','precisam de 26,67 h para 133,33 ha; a janela tem 10 h'])),
 ('R2b grupo_de_recursos_nao_relaxa_janela_2','PRE-REV R2 · o mesmo com 2 plantadeiras: a mesma divisão (menos recurso nunca dá plano mais otimista); C ao mesmo tempo: 30 h',
   200,[dict(id='A',nome='A',rend=5,seq=True,jan=10,rec={'plant':1},custo_h=100),dict(id='B',nome='B',rend=5,seq=True,jan=10,custo_h=100),dict(id='C',nome='C',rend=5,rec={'plant':1},custo_h=100)],
   {'plant':{'un':2,'nome':'Plantadeiras'}},dict(q=['25','25','150'],saldo='0',decorrido='30',conflito=True,deficit='50/3')),
]
RA='rendCalc(6,8,75)'; RB='rendCalc(12,8,75)'
def js_val(x):
    if x=='RA': return RA
    if x=='RB': return RB
    if isinstance(x,str) and re.fullmatch(r'\d+/\d+',x): a,b=x.split('/'); return f'({a}/{b})'
    return json.dumps(x)
def js_cfg(c): return '{'+','.join(f'{json.dumps(k)}:{js_val(v)}' for k,v in c.items())+'}'
def py_val(x):
    if x=='RA': return D2.rend_calc(F(6),F(8),F(75))
    if x=='RB': return D2.rend_calc(F(12),F(8),F(75))
    if isinstance(x,bool) or x is None or x=='' : return x
    if isinstance(x,(int,float)) : return F(str(x))
    if isinstance(x,str) and re.fullmatch(r'-?\d+(/\d+)?(\.\d+)?',x): return F(x)
    return x
def py_cfg(c): return {k:(py_val(v) if k in ('rend','part','jan','custo_h','diesel','troca','pess') else v) for k,v in c.items()}
SEL="r=>({alocado:r.alocado,saldo:r.saldo,pendente:r.pendente,causa:r.causa,hconj:r.hconj,decorrido:r.decorrido,troca:r.troca,custo:r.custo,custoOk:r.custoOk,custoHa:r.custoHa,diesel:r.diesel,hh:r.hh,conflito:r.conflito,deficit:r.deficit,nec:r.nec,falta:r.falta,motivos:r.motivos,q:r.itens.map(x=>x.q),nq:r.itens.map(x=>x.nq),fq:r.itens.map(x=>x.fq),Q:r.Q})"
js=['function nfa(n){ return String(n); }',BLOCO,'const SEL='+SEL+';','const OUT={};']
for cid,_,Q,cfgs,pools,_e in CASOS:
    js.append(f"OUT[{json.dumps(cid)}]=SEL(repartir({json.dumps(Q)},[{','.join(js_cfg(c) for c in cfgs)}],{json.dumps(pools)}));")
# especiais: 01 rendimentos, 02 recíproco, 09 insumos, 11 gargalo em série, 12 sem arredondar
js.append("OUT['01']=[rendCalc(6,8,75),rendCalc(12,8,75)];")
js.append("OUT['02']=[repartir(1,[{rend:rendCalc(6,8,75)}]).hconj,repartir(1,[{rend:rendCalc(12,8,75)}]).hconj];")
js.append("(()=>{ const r=repartir(108,[{rend:rendCalc(6,8,75)},{rend:rendCalc(12,8,75)}]); OUT['09']=[108*2,r.itens.reduce((a,x)=>a+x.q*2,0)+r.saldo*2]; })();")
js.append("OUT['11']=(()=>{ const t=[repartir(48,[{rend:6},{rend:4}]).decorrido,repartir(48,[{rend:6}]).decorrido,repartir(48,[{rend:8}]).decorrido]; const T=Math.max.apply(null,t); return [48/T,T,t]; })();")
js.append("OUT['R3']=(()=>{ const r=repartir(2882.53,[48.7,17.6,21.9,5.4,6.4].map((p,i)=>({nome:'P'+i,rend:5,part:p,seq:true})).concat([{nome:'L',rend:5,seq:true,troca:2}])); return [r.itens[5].q,r.motivos.filter(m=>/não cobrem/.test(m)).length,r.decorrido]; })();")
js.append("OUT['12']=[repartir(1,[{rend:rendCalc(1.1,3.7,63)}]).hconj, 1/(Math.round(rendCalc(1.1,3.7,63)*100)/100)];")
js.append('print(JSON.stringify(OUT));')
with tempfile.NamedTemporaryFile('w',suffix='.js',delete=False) as f: f.write(PRELUDIO+'\n'+'\n'.join(js)); jsf=f.name
pr=subprocess.run(MOTOR+[jsf],capture_output=True,text=True,timeout=30); os.unlink(jsf)
if pr.returncode!=0 or not pr.stdout.strip(): print('motor JS (jsc/node) falhou:',pr.stderr[:800]); print('RESULTADO: 0/1 · jsc não rodou'); sys.exit(1)
OUT=json.loads(pr.stdout.strip().splitlines()[-1])
OK=0; N=0
def near(a,b):
    if a is None or b is None: return a is b
    return abs(float(a)-float(b))<=1e-9*max(1.0,abs(float(b)))
def exp_val(v): return F(v) if isinstance(v,str) and re.fullmatch(r'-?\d+(/\d+)?',v) else v
def pega(d,k):   # campo simples ou aninhado ('nec.hconj')
    for parte in k.split('.'): d=d[parte]
    return d
def fecha(r,qs,nqs,fqs,eq):   # necessário = atendido + saldo (ha e horas-conjunto); saldo = Σ saldo por configuração + sem horas calculáveis
    n,f=r['nec'],r['falta']; hc=r['hconj'] or 0
    ok=eq(n['area'],r['Q']) and eq(f['area'],r['saldo']) and eq(sum(nqs)+f['semHoras'],r['Q']) and eq(sum(fqs)+f['semHoras'],r['saldo'])
    ok&= all(a>=b-1e-9 for a,b in zip(nqs,qs))
    if n['hconj'] is not None: ok&= f['hconj'] is not None and eq(n['hconj'],hc+f['hconj']) and n['decorrido']>=(r['decorrido'] or 0)-1e-9
    return bool(ok)
def chk(cid,desc,exp_s,js_s,py_s,ok):
    global OK,N; N+=1; OK+=1 if ok else 0
    print(f"{'OK   ' if ok else 'FALHA'} {cid} · {desc}\n        esperado={exp_s}\n        JS={js_s}\n        Py={py_s}",flush=True)
for cid,desc,Q,cfgs,pools,exp in CASOS:
    j=OUT[cid]; p=D2.repartir(py_val(Q) if not isinstance(Q,str) else Q,[py_cfg(c) for c in cfgs],pools)
    p_q=[x['q'] for x in p['itens']]; ok=True; ej={}; ep={}
    for k,v in exp.items():
        if k in ('q','nq'):
            pv=[x[k] for x in p['itens']]; e=[F(x) for x in v]; ej[k]=j[k]; ep[k]=[str(x) for x in pv]
            ok&= all(near(a,b) for a,b in zip(j[k],e)) and len(j[k])==len(e) and all(F(a)==b for a,b in zip(pv,e))
        elif k=='motivo':
            ej[k]=j['motivos']; ep[k]=p['motivos']
            for v_ in ([v] if isinstance(v,str) else v): ok&= any(v_ in m_ for m_ in j['motivos']) and any(v_ in m_ for m_ in p['motivos'])
        elif k=='conserva':
            sj=sum(j['q'])+j['saldo']; sp=sum(p_q)+p['saldo']; ej[k]=f'Σq+saldo={sj}'; ep[k]=f'Σq+saldo={sp}'; ok&= near(sj,j['Q']) and F(sp)==F(Q)
        else:
            e=exp_val(v); jv,pv=pega(j,k),pega(p,k); ej[k]=jv; ep[k]=str(pv) if pv is not None and not isinstance(pv,bool) else pv
            if isinstance(e,F): ok&= near(jv,e) and pv is not None and F(pv)==e
            else: ok&= (jv==e) and (pv==e)
    # conservação em todo caso: Σ q + sem conjunto = Q (JS e Python)
    cj=near(sum(j['q'])+j['saldo'],j['Q']); cp=F(sum(p_q,F(0))+p['saldo'])==F(p['Q'])
    # necessário = atendido + saldo, em ha e em horas-conjunto (JS com tolerância, Python exato)
    nj=fecha(j,j['q'],j['nq'],j['fq'],near); npy=fecha(p,p_q,[x['nq'] for x in p['itens']],[x['fq'] for x in p['itens']],lambda a,b: F(a)==F(b))
    cj=cj and nj; cp=cp and npy
    ok&= cj and cp
    chk(cid,desc,json.dumps(exp,ensure_ascii=False),json.dumps(ej,ensure_ascii=False)+f' · conserva={cj}',json.dumps(ep,ensure_ascii=False,default=str)+f' · conserva={cp}',ok)
# especiais
ra,rb=D2.rend_calc(F(6),F(8),F(75)),D2.rend_calc(F(12),F(8),F(75))
chk('01 capacidades_ha_h','A 6 m × 8 km/h × 75 % e B 12 m × 8 km/h × 75 %','(18/5, 36/5)',OUT['01'],(str(ra),str(rb)),near(OUT['01'][0],F(18,5)) and near(OUT['01'][1],F(36,5)) and (ra,rb)==(F(18,5),F(36,5)))
pa=D2.repartir(F(1),[dict(rend=ra)])['hconj']; pb=D2.repartir(F(1),[dict(rend=rb)])['hconj']
chk('02 reciproco_h_ha','horas por hectare = 1 ÷ rendimento','(5/18, 5/36)',OUT['02'],(str(pa),str(pb)),near(OUT['02'][0],F(5,18)) and near(OUT['02'][1],F(5,36)) and (pa,pb)==(F(5,18),F(5,36)))
p9=D2.repartir(F(108),[dict(rend=ra),dict(rend=rb)]); i9=sum((x['q']*2 for x in p9['itens']),F(0))+p9['saldo']*2
chk('09 insumos_conservados','dose 2 un/ha em 108 ha: 216 antes e depois da divisão (dose × área não muda com os conjuntos)','(216, 216)',OUT['09'],(216,str(i9)),near(OUT['09'][0],216) and near(OUT['09'][1],216) and i9==216)
t11=[D2.repartir(F(48),[dict(rend=F(6)),dict(rend=F(4))])['decorrido'],D2.repartir(F(48),[dict(rend=F(6))])['decorrido'],D2.repartir(F(48),[dict(rend=F(8))])['decorrido']]; T11=max(t11)
chk('11 gargalo_serie_limite_inferior','etapas em série: 6+4 ha/h em paralelo, 6 e 8 ha/h; 48 ha → gargalo 6 ha/h, limite inferior 8 h (paralelo soma, série não)','(6, 8)',
    OUT['11'],(str(F(48)/T11),str(T11),[str(x) for x in t11]),near(OUT['11'][0],6) and near(OUT['11'][1],8) and F(48)/T11==6 and T11==8)
p12=D2.repartir(F(1),[dict(rend=D2.rend_calc(F('1.1'),F('3.7'),F(63)))])['hconj']
chk('12 sem_arredondamento_intermediario','1,1 m × 3,7 km/h × 63 %: h/ha = 100000/25641 (≈ 3,9000039); arredondar o rendimento para 0,26 daria 3,846','100000/25641',
    OUT['12'],str(p12),near(OUT['12'][0],F(100000,25641)) and p12==F(100000,25641) and abs(OUT['12'][1]-OUT['12'][0])>0.05)
r3c=[dict(nome=f'P{i}',rend=5,part=p,seq=True) for i,p in enumerate([48.7,17.6,21.9,5.4,6.4])]+[dict(nome='L',rend=5,seq=True,troca=2)]
p3f=D2.repartir(2882.53,r3c); p3=D2.repartir(F('2882.53'),[py_cfg(c) for c in r3c])
chk('R3 resto_relativo_area_grande','PRE-REV R3 · 2.882,53 ha com partes 48,7 + 17,6 + 21,9 + 5,4 + 6,4 = 100 % e uma configuração sem % em sequência (troca 2 h): ela não recebe área nem soma troca, em ponto flutuante (JS e Python) e exato',
    '[0, 0 avisos "não cobrem", decorrido 2882,53/5]',OUT['R3'],(p3f['itens'][5]['q'],str(p3['itens'][5]['q']),str(p3['decorrido'])),
    OUT['R3'][0]==0 and OUT['R3'][1]==0 and near(OUT['R3'][2],F('2882.53')/5) and p3f['itens'][5]['q']==0 and p3['itens'][5]['q']==0 and p3['decorrido']==F('2882.53')/5
    and not any('não cobrem' in m for m in p3f['motivos']+p3['motivos']))
# ---------- 400 entradas aleatórias (semente fixa): paridade JS × Python (float) e invariantes nos dois ----------
import random
rng=random.Random(20261003); RND=[]
for n in range(400):
    k=rng.randint(1,4); cfs=[]
    for j in range(k):
        c=dict(id=f'c{j}',nome=f'C{j}',rend=(rng.choice([2.925,3.6,6.8,7.2,18,21.6,round(rng.uniform(.5,25),3)]) if rng.random()<.85 else rng.choice(['',0,'3,6'])),
               custo_h=rng.choice([rng.randint(50,400),'']),diesel=rng.choice(['',rng.randint(4,30)]))
        if rng.random()<.3: c['part']=rng.choice([0,20,30,50,70])
        if rng.random()<.8: c['jan']=rng.choice([0,1,2,3,5,8,12,20])
        if rng.random()<.6: c['seq']=True
        if rng.random()<.4: c['troca']=rng.choice([0,.5,1,2])
        if rng.random()<.3: c['ativos']=[rng.choice(['a01','a02'])]
        if rng.random()<.5: c['rec']={'plant':1}
        c['pess']=rng.choice([0,1,2])
        cfs.append(c)
    RND.append((rng.choice([0,rng.randint(1,300),round(rng.uniform(1,300),2),round(rng.uniform(1,300),2)]),cfs,rng.choice([None,{'plant':{'un':1,'nome':'Plantadeiras'}},{'plant':{'un':2,'nome':'Plantadeiras'}}])))
SELR="r=>({Q:r.Q,alocado:r.alocado,saldo:r.saldo,pendente:r.pendente,causa:r.causa,hconj:r.hconj,decorrido:r.decorrido,custo:r.custo,custoOk:r.custoOk,diesel:r.diesel,hh:r.hh,conflito:r.conflito,deficit:r.deficit,nec:r.nec,falta:r.falta,motivos:r.motivos,it:r.itens.map(x=>({q:x.q,h:x.h,ht:x.ht,H:isFinite(x.H)?x.H:-1,g:x.grupo,s:x.emSeq,nq:x.nq,fq:x.fq}))})"
jr=['function nfa(n){ return String(n); }',BLOCO,'const SELR='+SELR+';','const R=[];']+[f"R.push(SELR(repartir({json.dumps(Q)},{json.dumps(c)},{json.dumps(pl)})));" for Q,c,pl in RND]+['print(JSON.stringify(R));']
with tempfile.NamedTemporaryFile('w',suffix='.js',delete=False) as f: f.write(PRELUDIO+'\n'+'\n'.join(jr)); jsf=f.name
pr=subprocess.run(MOTOR+[jsf],capture_output=True,text=True,timeout=60); os.unlink(jsf); JR=json.loads(pr.stdout.strip().splitlines()[-1])
def inv(r,Q,cfs):   # invariantes de um resultado (JS ou Python no mesmo formato)
    e=[]; its=r['it']; sq=sum(x['q'] for x in its)
    ds=[x for x,c in zip(its,cfs) if c.get('seq') and x['nq']>1e-12]   # sequência declarada no plano: as horas dela cabem na maior janela dela (PRE-REV R2)
    if len(ds)>1 and all(x['H']>=0 for x in ds) and sum(x['h'] for x in ds)>max(x['H'] for x in ds)+1e-9: e.append('sequência declarada passa da janela')
    if abs(sq+r['saldo']-Q)>1e-7*max(1,Q): e.append('Σq+saldo≠Q')
    if any(x['q']<-1e-12 for x in its) or r['saldo']<-1e-12: e.append('negativo')
    if any(x['H']>=0 and x['h']>x['H']+1e-9 for x in its): e.append('h>janela própria')
    gs={}
    for x in its: gs.setdefault(x['g'],[]).append(x)
    for g,xs in gs.items():
        at=[x for x in xs if x['q']>1e-12]; Ws=[x['H'] for x in xs]
        if len(at)>1 and min(Ws)>=0 and sum(x['ht'] for x in at)>max(Ws)+1e-9: e.append('sequência passa da janela')
    if r['pendente'] and (r['hconj'] is not None or not r['causa']): e.append('pendente sem causa ou com horas')
    if not r['pendente'] and r['causa']: e.append('causa sem pendência')
    if r['hconj'] is not None and abs(r['hconj']-sum(x['h'] for x in its))>1e-9*max(1,r['hconj']): e.append('horas-conjunto≠Σh')
    if not fecha(r,[x['q'] for x in its],[x['nq'] for x in its],[x['fq'] for x in its],lambda a,b: abs(a-b)<=1e-7*max(1,abs(b))): e.append('necessário≠atendido+saldo')
    return e
def pyr(Q,c,pl):
    p=D2.repartir(Q,c,pl); f=lambda v: float(v) if v is not None and not isinstance(v,bool) else v
    return dict(Q=f(p['Q']),alocado=f(p['alocado']),saldo=f(p['saldo']),pendente=p['pendente'],causa=p['causa'],hconj=f(p['hconj']),decorrido=f(p['decorrido']),custo=f(p['custo']),
                custoOk=p['custoOk'],diesel=f(p['diesel']),hh=f(p['hh']),conflito=p['conflito'],deficit=f(p['deficit']),motivos=p['motivos'],
                nec={k:f(v) for k,v in p['nec'].items()},falta={k:f(v) for k,v in p['falta'].items()},
                it=[dict(q=f(x['q']),h=f(x['h']),ht=f(x['ht']),H=(-1 if x['H']==float('inf') else f(x['H'])),g=x['grupo'],s=x['emSeq'],nq=f(x['nq']),fq=f(x['fq'])) for x in p['itens']])
def igual(a,b):
    for k in ('alocado','saldo','hconj','decorrido','custo','diesel','hh','deficit'):
        x,y=a[k],b[k]
        if (x is None)!=(y is None) or (x is not None and abs(x-y)>1e-7*max(1,abs(y))): return k
    for k in ('pendente','causa','conflito','custoOk','motivos'):
        if a[k]!=b[k]: return k
    for g in ('nec','falta'):
        for k in ('area','hconj','decorrido','semHoras'):
            x,y=a[g][k],b[g][k]
            if (x is None)!=(y is None) or (x is not None and abs(x-y)>1e-7*max(1,abs(y))): return g+'.'+k
    if any(abs(x['nq']-y['nq'])>1e-7*max(1,abs(y['nq'])) or abs(x['fq']-y['fq'])>1e-7*max(1,abs(y['fq'])) for x,y in zip(a['it'],b['it'])): return 'itens.nq/fq'
    if any(abs(x['q']-y['q'])>1e-7*max(1,abs(y['q'])) or x['s']!=y['s'] for x,y in zip(a['it'],b['it'])): return 'itens'
    return None
npar=0; ninv=0; ex=[]; nseq=0; nconf=0; npend=0
for (Q,c,pl),j in zip(RND,JR):
    py=pyr(Q,c,pl); d=igual(j,py); ij=inv(j,float(Q),c); ip=inv(py,float(Q),c)
    if d is None: npar+=1
    elif len(ex)<3: ex.append(('paridade',d,Q,c,pl,j.get(d),py.get(d)))
    if not ij and not ip: ninv+=1
    elif len(ex)<3: ex.append(('invariante',ij,ip,Q,c,pl))
    nseq+=any(x['s'] for x in j['it']); nconf+=j['conflito']; npend+=j['pendente']
assert nseq>=100 and nconf>=20, (nseq,nconf)   # a amostra precisa exercitar sequência e conflito
chk('R1 paridade_js_python_400','400 entradas aleatórias (rendimento vazio/0/vírgula, partes, janelas 0–20 h, sequência, troca, mesmo ativo, grupo da fazenda): JS = Python',
    '400/400',f'{npar}/400 iguais',f'com sequência {nseq} · conflito {nconf} · pendentes {npend} · exemplos {ex[:2]}',npar==400)
chk('R2 invariantes_400','Σ q + sem conjunto = Q, sem negativos, h ≤ janela própria, sequência ≤ janela da sequência, sequência declarada ≤ a janela dela, pendente com causa e sem horas, horas-conjunto = Σ h, necessário = atendido + saldo (ha e horas-conjunto)',
    '400/400',f'{ninv}/400 sem violação',f'exemplos {ex[:2]}',ninv==400)
print(f'RESULTADO: {OK}/{N} OK · JS = bloco REPARTIR de safra.js no jsc · Python = dados2.repartir com Fraction',flush=True)
sys.exit(0 if OK==N else 1)
