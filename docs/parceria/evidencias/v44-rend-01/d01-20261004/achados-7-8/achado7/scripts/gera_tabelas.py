# gera as tabelas do PACOTE.md a partir dos brutos (nada digitado à mão) → brutos/tabelas_geradas.md
import json,sys,os,statistics as st
W=sys.argv[1]; B=W+'/brutos/'
def ld(p): return [json.loads(l) for l in open(p) if l.startswith('{')] if os.path.exists(p) else []
def f(x,d=4):
    if x is None: return '—'
    if isinstance(x,str): return x
    s=f'{x:.{d}f}'
    if '.' in s: s=s.rstrip('0').rstrip('.')
    return s.replace('.',',')
def bur(bl):
    return ' '.join(f"{b['grafo']}:{'null' if b['buraco'] is None else str(b['buraco']).lower()}/{b['passos']}" for b in bl) or '—'
def th(v): return 'inf' if v['theta']=='inf' else (f(v['theta'],4) if v['theta'] is not None else 'n/a')
out=['### T1. Reprodução nos três commits (JS = bloco REPARTIR de safra.js; Python = dados2.repartir)\n',
 'Buraco: `grafo:resultado/passos` (p = plano, a = divisão; a 1ª chamada é o grafo, a 2ª o complemento). V3 = verificador independente (θ* ≥ 1 executável).\n',
 '| Caso | Commit | buraco | Caminho | Alocado (ha) | Saldo (ha) | Déficit (h) | Conflito | Python Fraction (alocado; saldo; déficit) | V3 θ* | JS ms (3 exec.) | Py ms | JS=Py |','|---|---|---|---|---|---|---|---|---|---|---|---|---|']
for c,h in (('c2e3','2e31588'),('c04b','04bf6f2'),('cee4','ee4f954')):
    for e in ('casos_principais','contraexemplo','M2'):
        J=ld(B+f'repro_js_{c}_{e}.txt'); P=ld(B+f'repro_py_{c}_{e}.txt'); F=ld(B+f'repro_pyfrac_{c}_{e}.txt'); V=ld(B+f'verif_repro_pyfrac_{c}_{e}.txt')
        par=open(B+f'paridade_repro_{c}_{e}.txt').read().strip().split('\n')[-1]
        for j,p,fr,v in zip(J,P,F,V):
            out.append(f"| {j['nome']} | {h} | {bur(j['buraco'])} | {j['caminho']} | {f(j['alocado'])} | {f(j['saldo'])} | {f(j['deficit'])} | {j['conflito']} | {fr['exato']['alocado']}; {fr['exato']['saldo']}; {fr['exato']['deficit']} | {th(v)}{' **inexecutável**' if v['violacoes'] else ''} | {', '.join(f(x,1) for x in j['ms'])} | {f(p['ms'][0],0)} | {'sim' if '0 com diferença' in par else 'NÃO'} |")
out+=['\n### T2. Esperado: caminho de cliques forçado (cópia var/cliq de 2e31588), Python com Fraction, e dois verificadores independentes\n',
 '| Caso | Alocado exato | Saldo exato | Déficit exato (h) | JS alocado | V2 cortes | V3 (verif.py) θ* | 2º verificador (emparelhamentos) θ* |','|---|---|---|---|---|---|---|---|']
J=ld(B+'esperado_cliq_js.txt'); F=ld(B+'esperado_cliq_pyfrac.txt'); V=ld(B+'verif_esperado_cliq_pyfrac.txt'); M=ld(B+'verif_matching_esperado_cliq_pyfrac.txt')
for j,fr,v,m in zip(J,F,V,M):
    v2=[x for x in v['violacoes'] if x.startswith('V2')]
    out.append(f"| {j['nome']} | {fr['exato']['alocado']} | {fr['exato']['saldo']} | {fr['exato']['deficit']} | {f(j['alocado'])} | {'ok' if not v2 else len(v2)} | {th(v)}{' **inexecutável**' if v['violacoes'] else ''} | {f(m['theta'],4)} ({m['emparelhamentos']} emparelhamentos, {m['segmentos']} segmentos) |")
VAR=[('P0','P0 = 2e31588'),('P1_2e18','P1 2^18'),('P1_2e20','P1 2^20'),('P1_2e22','P1 2^22'),('P2','P2'),('P2u','P2u')]
out+=['\n### T3. Propostas: casos principais, extras e contraexemplo (JS 3 execuções, mediana; Python 1 execução)\n',
 'Célula: alocado ha · déficit h · caminho (cliq = cliques; CONS = conservador por estouro; L = reconhecido sem busca) · JS ms · Py ms. **inexec.** = V3 prova que não há cronograma.\n',
 '| Caso | '+' | '.join(n for _,n in VAR)+' |','|---|'+'---|'*len(VAR)]
for e in ('casos_principais','casos_extras','contraexemplo'):
    for c in json.load(open(W+f'/entradas/{e}.json')):
        cel=[]
        for n,_ in VAR:
            j={x['nome']:x for x in ld(B+f'prop_js_{n}_{e}.txt')}[c['nome']]; py={}
            for ee in [e]+(['casos_extras_py','casos_extras_so_js'] if e=='casos_extras' else []): py.update({x['nome']:x for x in ld(B+f'prop_py_{n}_{ee}.txt')})
            p=py.get(c['nome']); v={x['nome']:x for x in ld(B+f'verif_prop_js_{n}_{e}.txt')}[c['nome']]
            cam='CONS' if 'estouro' in j['caminho'] else ('cliq' if j['caminho']=='cliques' else j['caminho'])
            if any(b['buraco']=='linhaBip' for b in j['buraco']): cam+=' L'
            cel.append(f"{f(j['alocado'],2)} · {f(j['deficit'],2)} · {cam}{' **inexec.**' if v['violacoes'] else ''} · {f(st.median(j['ms']),0)} · {f(p['ms'][0],0) if p else 'n/m'}")
        out.append(f"| {c['nome']} | "+' | '.join(cel)+' |')
out+=['\n### T4. Bateria adversarial (71 casos de 20–36 configurações, semente 20261004; JS em todos; Python em todos para P0, P2, P2u e P1 2^18, e só nos 7 piores para P1 2^20 e 2^22)\n',
 '| Variante | JS pior ms (caso) | JS casos no conservador por estouro do buraco | Python pior ms (caso) | Python casos | Verificador: casos inexecutáveis (V3) | JS = Python |','|---|---|---|---|---|---|---|']
for n,lab in VAR:
    J=ld(B+f'adv_js_{n}.txt'); jw=max(J,key=lambda d:d['ms'][0]); est=sum(1 for d in J if any(b['buraco'] is None for b in d['buraco']))
    P=ld(B+f'adv_py_{n}.txt'); pw=max(P,key=lambda d:d['ms'][0]); V=ld(B+f'verif_adv_js_{n}.txt'); bad=[v['nome'] for v in V if v['violacoes']]
    par=open(B+f'paridade_adv_{n}.txt').read().strip().split('\n')[-1]
    out.append(f"| {lab} | {f(jw['ms'][0],0)} ({jw['nome']}) | {est} | {f(pw['ms'][0],0)} ({pw['nome']}) | {len(P)} | {len(bad)}: {'; '.join(bad)} | {par.lstrip('# ')} |")
out+=['\n### T5. 3 300 entradas aleatórias (semente 20261004), verificador independente\n',
 '| Variante | Com violação (V3) | Novas em relação a P0 | Caminho cliques / conservador (estouro) / conservador (ciclo) | Reconhecidas sem busca | Igual a P0 onde P0 conferiu | JS ms máx | Python: entradas, diferenças JS×Py, ms máx |','|---|---|---|---|---|---|---|---|']
R={d['variante']:d for d in map(json.loads,open(B+'resumo_aleat.txt'))}; PA={d['variante']:d for d in map(json.loads,open(B+'paridade_aleat.txt'))}
for n,lab in VAR:
    d=R[n]; c=d['caminhos']; p=PA[n]
    out.append(f"| {lab} | {d['com_violacao']} ({', '.join(k+' '+str(v) for k,v in d['por_categoria'].items())}) | {d['novas_vs_P0']} | {c.get('cliques',0)} / {c.get('conservador (estouro do teto)',0)} / {c.get('conservador (ciclo ímpar)',0)} | {d['entradas_com_linhaBip']} | {'sim' if d['diferencas_vs_P0_onde_P0_conferiu']==0 else 'NÃO ('+str(d['diferencas_vs_P0_onde_P0_conferiu'])+')'} | {f(d['ms_max'],0)} (#{d['ms_max_k']}) | {p['entradas_python']}, {p['com_diferenca']}, {f(p['py_ms_max'],0)} (#{p['py_k_max']}) |")
open(B+'tabelas_geradas.md','w').write('\n'.join(out)+'\n'); print('\n'.join(out))
