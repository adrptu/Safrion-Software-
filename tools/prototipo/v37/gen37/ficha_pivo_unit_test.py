# -*- coding: utf-8 -*-
"""Ficha do pivô (pedido do proprietário, 09/10/2026: "na irrigação onde colocamos os dados da ficha do pivô, lâmina 21 h etc.") e as
correções da revisão de 10/10 (A1 tolerância, A2 vazão em um lugar, A3 limite do setor e política única, A4 registro, A7 equipamento do
setor, A8 valor antigo de reserva).
Parte 1 (python): dados, vínculo equipamento → setor → talhão, fonte única da vazão e do nome, política de água e o cd03 de reserva.
Parte 2 (node, sem navegador): o registro e a conta da ficha (ficha_pivo.store_js) com a semente, a ficha coerente da revisão (sem falsa
divergência), o limite exato da tolerância, a validação do registro e a vazão do setor que a Irrigação lê (irrGet → irrEqVaz).
Parte 3 (páginas geradas, depois do build.py): o componente no CD-03 e no IR-01, as entradas (abrir e registrar) e o ponto de leitura da CAD.
Na base 2f8a6e6 não existem store_js, fpvConf, fpvValida, irrEqVaz nem o setor com o equipamento (eq): os casos novos falham.
Uso: python3 ficha_pivo_unit_test.py   (sai 1 se algum caso falhar)"""
import os, sys, re, json, subprocess, tempfile, importlib
from decimal import Decimal, ROUND_HALF_UP
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); os.chdir(HERE)
sys.dont_write_bytecode = True
OK, FAIL = [], []
def chk(nome, cond, info=''):
    (OK if cond else FAIL).append(nome); print(('OK    ' if cond else 'FALHA ') + nome + ('' if cond else ' · ' + str(info)[:700]), flush=True)
import dados as D, dados_cad as DC, dados_irrigacao as DI, cenario
FP0 = getattr(D, 'FICHA_PIVO', None) or {}
try: FPM = importlib.import_module('ficha_pivo')
except Exception as e: FPM = None; print('sem ficha_pivo.py:', e)
f = FP0.get('a11') or {}
at = {a['id']: a for a in DC.ATIVOS}
sem = DI.seed(); S = sem['setores']
# ---------------- parte 1 · dados ----------------
chk('F1 a ficha é do equipamento de irrigação do cadastro (a11 · Bomba do Pivô 2) e o setor P2 da Irrigação guarda a chave dele (eq = a11)',
    bool(f) and at['a11']['classe'] == 'Irrigação' and S['P2'].get('eq') == 'a11' and set(FP0) <= {a['id'] for a in DC.ATIVOS if a['classe'] == 'Irrigação'}, [list(FP0), S['P2'].get('eq')])
tab = f.get('tabela') or []
chk('F2 tempo de volta e lâmina a 100 % vêm de dados.PIVO (9,0 h e 6,7 mm) e são a linha de 100 %: a tabela não repete essa linha (o mesmo dado não se digita duas vezes)',
    f.get('volta_100_h') == D.PIVO['volta_h'] and f.get('lamina_100_mm') == D.PIVO['lamina_100'] and len(tab) == 9 and all(Decimal(str(l[0])) != 100 for l in tab), [f.get('volta_100_h'), tab[:1]])
pv = FPM.pivos() if FPM and hasattr(FPM, 'pivos') else {}
chk('F3 vínculo equipamento → setor → talhão: a11 é o pivô do setor P2 (Pivô 2) e irriga o talhão P2 do cadastro; a fazenda vem do setor (Santa Rita, do cadastro de fazendas); a15 (Pivô 1) também pode ter ficha; o gotejo não',
    (pv.get('a11') or {}).get('setor') == 'P2' and (pv.get('a11') or {}).get('pivo') == 'Pivô 2' and [t['t'] for t in (pv.get('a11') or {}).get('tal', [])] == ['P2']
    and (pv.get('a11') or {}).get('faz') == next(x['nome'] for x in DC.FAZENDAS if x['id'] == S['P2']['faz']) and 'a15' in pv and 'a12' not in pv, pv)
m3 = lambda ls: Decimal(str(ls)) * Decimal('3.6')
vz = {k: (S[k].get('eq'), S[k]['vazao']) for k in ('P2', 'P1', 'T7')}
chk('F4 A2 · vazão em um lugar: cada setor de Santa Rita lê a vazão do seu equipamento (P2 = ficha 166 L/s; P1 e T7 = cadastro ÷ 3,6) e o cadastro tem o mesmo valor em m³/h',
    f.get('vazao_ls') == S['P2']['vazao'] == 166 and all(e and Decimal(str(at[e]['vazao'])) == m3(v) for e, v in vz.values()), [vz, {e: at[e]['vazao'] for e, _ in vz.values() if e}])
chk('F5 A7 · o setor mostra o nome do equipamento do cadastro (Bomba do Pivô 2, não "Bomba B2") e o modelo do cadastro descreve o conjunto da ficha (pivô + motobomba)',
    all(S[k].get('bnome') == at[S[k]['eq']]['nome'] for k in ('P2', 'P1', 'T7') if S[k].get('eq')) and S['P2'].get('bnome') == 'Bomba do Pivô 2'
    and 'pivô central' in at['a11']['modelo'] and 'motobomba' in at['a11']['modelo'], [S['P2'].get('bnome'), at['a11']['modelo']])
PA = D.POLITICA_AGUA; cfg = open(os.path.join(HERE, 'areas', 'configuracoes.py'), encoding='utf-8').read()
chk('F6 A3 · a política de água tem uma fonte (dados.POLITICA_AGUA): Configurações não escreve à mão "IR-LIM", "v4" nem "Ana (gestora)" na linha dela',
    PA.get('versao') == 'v3' and PA.get('id') == 'PA-07' and "'IR-LIM'" not in cfg and "'Ana (gestora)','sem validade'" not in cfg and "PA['autor']" in cfg, [PA, "'IR-LIM'" in cfg])
import areas.cadastros as CAD
res = {a[0]: a[4] for a in CAD.ATIVOS}
chk('F7 A8 · o cd03 de reserva (areas/cadastros.py) lê a vazão do cadastro: Bomba do Pivô 2 = 597,6 m³/h (não 340) e Gotejo T7 = o do cadastro',
    Decimal(str(res.get('a11'))) == Decimal('597.6') == Decimal(str(at['a11']['vazao'])) and res.get('a12') == at['a12']['vazao'], [res.get('a11'), res.get('a12')])
src = open(os.path.join(HERE, 'ficha_pivo.py'), encoding='utf-8').read()
conf_src = src.split('function fpvConf', 1)[1].split('\n', 3)[:3] if 'function fpvConf' in src else ['regime']
chk('F8 "21 h" é o regime de operação (h/dia, fora do horário de ponta) e não entra na conta da ficha',
    f.get('regime_h') == 21 and 'fora do horário de ponta' in (f.get('regime_obs') or '') and 'regime' not in ''.join(conf_src), [f.get('regime_h'), conf_src[:1]])
chk('F9 A7 · a ficha não escreve a fazenda à mão (ficha_pivo.py sem "Santa Rita")', 'Santa Rita' not in src.split('"""', 2)[-1])
# ---------------- parte 2 · node: registro, conta e a vazão que a Irrigação lê ----------------
STORE = FPM.store_js() if FPM and hasattr(FPM, 'store_js') else ''
L100 = Decimal(str(D.PIVO['lamina_100']))
q1 = lambda x: x.quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)
# ficha coerente da revisão (A1): lâmina a 100 % verdadeira = 166 L/s × 9,0 h ÷ 80 ha = 6,723 mm, impressa 6,7; cada linha arredondada a 1 casa
l100v = Decimal(166) * Decimal('3.6') * Decimal('9.0') / (Decimal(80) * 10)
coer = dict(f, lamina_100_mm=float(q1(l100v)), tabela=[[p, float(q1(Decimal('9.0') * 100 / p)), float(q1(l100v * 100 / p))] for p in (90, 80, 70, 60, 50, 40, 30, 20, 10)])
SHIM = ("var __LS={}; var localStorage={getItem:k=>(k in __LS?__LS[k]:null),setItem:(k,v)=>{__LS[k]=String(v);},removeItem:k=>{delete __LS[k];},clear:()=>{for(const k in __LS) delete __LS[k];}};\n"
        "var window={addEventListener(){}}; var location={hash:'',pathname:'/x'}; var document={querySelector(){return null;}};\n")
caso = r'''
const out={};
try{
  out.fn={fpvConf:typeof fpvConf==='function',fpvGravar:typeof fpvGravar==='function',irrEqVaz:typeof irrEqVaz==='function'};
  const conf=(f)=>fpvConf(f).map(r=>({pct:r.pct,lam:r.lam,conta:Math.round(r.conta*1e4)/1e4,dif:Math.round(r.dif*1e4)/1e4,ok:r.ok}));
  out.seed=conf(FPV0.a11); out.coer=conf(__COER__);
  // limite exato da tolerância (0,05 + 0,05 × 100 ÷ 50 = 0,15 mm a 50 %): 13,55 confere (= limite), 13,56 diverge; 10 %: 67,55 confere (0,55), 67,56 não
  const um=(p,l)=>fpvConf({volta_100_h:9,lamina_100_mm:6.7,tabela:[[p,1,l]]})[1].ok;
  out.lim=[um(50,13.55),um(50,13.56),um(50,13.25),um(50,13.24),um(10,67.55),um(10,67.56)];
  // registro gravado: a Irrigação lê a vazão da ficha (P2) e, com ficha registrada para a15, a do P1; restaurar a demonstração volta à semente
  localStorage.clear(); const s0=irrGet(); out.v0=[s0.setores.P2.vazao,s0.setores.P1.vazao,s0.setores.T7.vazao];
  fpvGravar('a11',Object.assign({},FPV0.a11,{vazao_ls:170})); fpvGravar('a15',{fabricante:'X',raio_m:550,area_ha:95,vazao_ls:155,pressao_mca:30,volta_100_h:10,lamina_100_mm:6.1,regime_h:21,regime_obs:'',tabela:[[50,20,12.2]]});
  const s1=irrGet(); out.v1=[s1.setores.P2.vazao,s1.setores.P1.vazao,s1.setores.T7.vazao,irrDur(s1.setores.P2,10)];
  out.lido=[fpvFicha('a11').vazao_ls,fpvFicha('a15').vazao_ls];
  // repetir o mesmo registro não muda nada
  const r1=JSON.stringify(fpvFichas()); fpvGravar('a11',Object.assign({},FPV0.a11,{vazao_ls:170})); out.rep=JSON.stringify(fpvFichas())===r1;
  // cenário restaurado (rev menor que a vista ao gravar) → a ficha volta à semente
  __LS['talhao-os-cenario-v1']=JSON.stringify({rev:5}); fpvGravar('a11',Object.assign({},FPV0.a11,{vazao_ls:171})); out.antes=fpvFicha('a11').vazao_ls;
  delete __LS['talhao-os-cenario-v1']; out.depois=[fpvFicha('a11').vazao_ls,!!fpvFicha('a15')];
}catch(e){ out.erro=String(e&&e.stack||e); }
console.log('JSON:'+JSON.stringify(out));
'''.replace('__COER__', json.dumps(coer))
# a validação do registro está no JS da gaveta (ficha_pivo.UI_JS); roda com g2num do g2lib
UI = FPM.js('IR') if FPM and hasattr(FPM, 'js') else ''
g2num = re.search(r'^function g2num\(.*$', open(os.path.join(HERE, 'g2lib.js'), encoding='utf-8').read(), re.M).group(0)
caso2 = r'''
const o2={};
try{
  o2.fn=typeof fpvValida==='function';
  const d0={fabricante:'Fab X',raio_m:'550',area_ha:'95',vazao_ls:'150',pressao_mca:'30',volta_100_h:'10,0',lamina_100_mm:'6,1',regime_h:'21',regime_obs:''};
  const L0=[{pct:'90',tempo:'11,1',lam:'6,8'},{pct:'80',tempo:'',lam:''},{pct:'',tempo:'',lam:''}];
  const a=fpvValida(d0,L0); o2.ok=[a.ok,JSON.stringify(a.tab)];
  const b=fpvValida(Object.assign({},d0,{vazao_ls:'',lamina_100_mm:'0',fabricante:' '}),L0); o2.campos=Object.keys(b.e).sort();
  const c=fpvValida(d0,[{pct:'100',tempo:'10',lam:'6,1'},{pct:'90',tempo:'11',lam:'6,8'},{pct:'90',tempo:'11',lam:'6,8'},{pct:'50',tempo:'20',lam:''},{pct:'150',tempo:'1',lam:'1'}]);
  o2.linhas=Array.from(c.le,x=>x||''); o2.okc=c.ok;
}catch(e){ o2.erro=String(e&&e.stack||e); }
console.log('JSON2:'+JSON.stringify(o2));
'''
def roda(src, tag):
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as t: t.write(src)
    r = subprocess.run(['node', t.name], capture_output=True, text=True, timeout=120); os.unlink(t.name)
    lin = [l for l in r.stdout.splitlines() if l.startswith(tag + ':')]
    return json.loads(lin[-1][len(tag) + 1:]) if lin else {'erro': (r.stderr or r.stdout)[-1200:]}
if STORE:
    O = roda(SHIM + cenario.js_prefixo() + DI.js_prefixo() + caso, 'JSON')
else:   # base: sem o registro em JS, a conta é a do python (ficha_pivo.conferencia) — o caso da ficha coerente mostra o defeito A1
    cf = (lambda g: [dict(pct=float(r['pct']), lam=float(r['lam']), conta=float(r['conta']), dif=float(r['dif']), ok=r['ok']) for r in FPM.conferencia(g)]) if FPM and hasattr(FPM, 'conferencia') else (lambda g: [])
    O = dict(fn={}, seed=cf(dict(f, tabela=[[str(x) for x in l] for l in tab])) if f else [],
             coer=cf(dict(coer, tabela=[['100', '9.0', str(coer['lamina_100_mm'])]] + [[str(x) for x in l] for l in coer['tabela']])))
chk('C0 o registro e a conta da ficha rodam no node (store_js + estado da Irrigação), sem erro', 'erro' not in O and all((O.get('fn') or {}).get(k) for k in ('fpvConf', 'fpvGravar', 'irrEqVaz')), O.get('erro') or O.get('fn'))
sd = {int(r['pct']): r for r in O.get('seed') or []}
chk('C1 conta de conferência = lâmina a 100 % × 100 ÷ percentímetro em todas as 10 linhas (100 % vem dos campos)',
    len(sd) == 10 and all(abs(Decimal(str(r['conta'])) - (L100 * 100 / Decimal(p)).quantize(Decimal('0.0001'))) <= Decimal('0.0001') for p, r in sd.items()), [(p, r['conta']) for p, r in list(sd.items())[:3]])
chk('C2 a semente tem uma linha divergente: 60 % = 11,0 mm × 11,17 mm pela conta (−0,17 mm); as outras conferem',
    60 in sd and not sd[60]['ok'] and round(sd[60]['dif'], 2) == -0.17 and all(r['ok'] for p, r in sd.items() if p != 60), [(p, r['lam'], r['conta'], r['ok']) for p, r in sd.items()])
co = O.get('coer') or []
chk('C3 A1 · ficha coerente (6,723 mm impressa 6,7; linhas arredondadas a 1 casa): nenhuma linha "Diverge" (antes 90, 30, 20 e 10 % divergiam)',
    len(co) == 10 and all(r['ok'] for r in co), [(r['pct'], r['lam'], round(r['dif'], 3)) for r in co if not r['ok']])
chk('C4 A1 · limite exato da tolerância (0,05 + 0,05 × 100 ÷ percentímetro, em centésimos inteiros): 50 % 13,55 e 13,25 conferem, 13,56 e 13,24 divergem; 10 % 67,55 confere, 67,56 diverge',
    O.get('lim') == [True, False, True, False, True, False], O.get('lim'))
chk('C5 A2 · a Irrigação lê a vazão da ficha gravada: P2 166 → 170 L/s (duração de 10 mm refeita), P1 150 → 155 L/s com a ficha registrada da Bomba do Pivô 1; T7 (gotejo) não muda',
    O.get('v0') == [166, 150, 233] and (O.get('v1') or [0])[:3] == [170, 155, 233] and O.get('lido') == [170, 155]
    and (O.get('v1') or [0, 0, 0, 0])[3] == round(10 * 80 * 10 / (170 * 3.6) * 60), [O.get('v0'), O.get('v1'), O.get('lido')])
chk('C6 REPETIÇÃO e restauração: gravar o mesmo registro não muda nada; restaurar a demonstração (cenário volta ao início) devolve a ficha à semente',
    O.get('rep') is True and O.get('antes') == 171 and O.get('depois') == [166, False], [O.get('rep'), O.get('antes'), O.get('depois')])
if UI and STORE:
    O2 = roda(SHIM + g2num + '\n' + FPM.store_js() + UI + caso2, 'JSON2')
else: O2 = {'erro': 'sem fpvValida'}
chk('C7 A4 · registro válido: linha com tempo e lâmina entra; linha só com o percentímetro (modelo) e linha em branco não entram',
    O2.get('fn') is True and O2.get('ok') == [True, '[[90,11.1,6.8]]'], O2)
chk('C8 A4 · RECUSA: fabricante, vazão em branco e lâmina fora da faixa apontados no campo; nada é gravado',
    O2.get('campos') == ['fabricante', 'lamina_100_mm', 'vazao_ls'], O2.get('campos'))
li = O2.get('linhas') or []
chk('C9 A4 · RECUSA nas linhas: 100 % (vem dos campos), percentímetro repetido, lâmina em branco e fora de 1–99 % — cada linha diz o motivo',
    O2.get('okc') is False and len(li) >= 5 and 'linha de 100 %' in li[0] and li[1] == '' and 'repetido' in li[2] and 'lâmina' in li[3] and '1 e 99' in li[4], li)
# ---------------- parte 3 · páginas geradas ----------------
P = os.path.join(HERE, 'project')
pg = lambda n: open(os.path.join(P, n), encoding='utf-8').read() if os.path.exists(os.path.join(P, n)) else ''
cd3, ir1, ir2 = pg('CD-03.dc.html'), pg('IR-01.dc.html'), pg('IR-02.dc.html')
COLS = ['Percentímetro', 'Tempo de volta', 'Lâmina', 'Lâmina pela conta', 'Conferência']
def cols_de(html):
    m = re.search(r'const GRIDS = (\[.*?\]);\n', html, re.S)
    if not m: return None
    g = [x for x in json.loads(m.group(1)) if x['id'] == 'g_fpv']
    return [c['l'] for c in g[0]['cols']] if g else None
chk('P1 o mesmo componente (gaveta "Ficha do pivô" + tabela com filtro e ordenação, uma variável por coluna) está no CD-03 e no IR-01',
    all('aria-label="Ficha do pivô' in h and cols_de(h) == COLS for h in (cd3, ir1)), [cols_de(cd3), cols_de(ir1)])
chk('P2 A4 · entradas: no CD-03 "Ficha do pivô ›" e "Registrar ficha do pivô ›" no detalhe do equipamento; no IR-01 "Ficha do pivô" e "Registrar ficha do pivô" no setor; a gaveta tem "Editar ficha" e "Salvar ficha"',
    all(x in cd3 for x in ("'Ficha do pivô ›'", "'Registrar ficha do pivô ›'", 'Editar ficha', 'Salvar ficha', 'IR-01.dc.html#'))
    and all(x in ir1 for x in ("'Ficha do pivô'", "'Registrar ficha do pivô'", 'Editar ficha', 'Salvar ficha', 'CD-03.dc.html#ficha=')))
chk('P3 A2 · o registro da ficha (FPV0 + fpvFicha) está em toda tela com o estado da Irrigação (IR-02 também) e no CD-03; o campo de vazão do CD-03 fica só leitura com ficha',
    all('const FPV0 = ' in h and 'function irrEqVaz' in h for h in (ir1, ir2)) and 'const FPV0 = ' in cd3 and "fx_g_atv_vazao_ir" in cd3 and 'f.dis=true' in cd3)
chk('P4 ponto de leitura da água disponível no solo (CAD) do talhão: lê irrCadTxt (frente SOLO) quando existir; sem ela, na Irrigação diz que não há medição e no cadastro diz onde ler',
    all('function fpvCad(' in h and "typeof irrCadTxt==='function'" in h and 'sem medição de água no solo neste talhão' in h and "'lida no setor '+E.setor+' da Irrigação" in h for h in (cd3, ir1)))
print(f'\nRESULTADO {len(OK)}/{len(OK) + len(FAIL)}')
sys.exit(1 if FAIL else 0)
