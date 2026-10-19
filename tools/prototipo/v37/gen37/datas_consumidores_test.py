"""EX57 F0c: dados sintéticos, batch/cache e âncora ausente dos consumidores."""
import copy
import dados2 as D
import datas_atividade as DA

original=DA.calcular_lote
chamadas=[]
def medir(entradas):
    chamadas.append(len(entradas))
    return original(entradas)
DA.calcular_lote=medir
D._DATAS_ATIVIDADE.clear()
for cs in D.CULTIVOS.values():
    for c in cs:
        if not c['plano']: continue
        for a in D.PLANO[c['plano']]['atividades']: D.data_atividade(c,a)
assert len(chamadas)==1, chamadas
print('OK catálogo inteiro usa um lote; leituras seguintes usam recibo por conteúdo', chamadas)
p=dict(id='TESTE-SEM-COLHEITA',atividades=[dict(nome='Após',op='Adubar',g=dict(tipo='DAPC',dias=2))])
D.PLANO[p['id']]=p
c=dict(id='test',plano=p['id'],plantio='2026-10-01',colheita=None)
a=p['atividades'][0]
assert D.data_atividade(c,a) is None
c['colheita']='2026-11-01'
assert D.data_atividade(c,a).isoformat()=='2026-11-03'
c['colheita']='2026-12-01'
assert D.data_atividade(c,a).isoformat()=='2026-12-03'
assert D.classe_oc(None,-1,'2026-01-01','2026-12-31')=='fora'
assert D.falta_a_partir([(None,100),('2026-11-01',3)],5,[]) is None
assert D.falta_a_partir([(None,100),('2026-11-01',6)],5,[])=='2026-11-01'
print('OK ausência não vira plantio/data; edição invalida cache; falta datada exclui ausência')

import ocupacao as OC
pl=dict(id='P',cultura='Teste',atividades=[dict(nome='Após',op='Adubação',g=dict(tipo='DAPC',dias=2)),dict(nome='Antes',op='Adubação',g=dict(tipo='DANC',dias=3))])
ctx=OC.ctx_de({'Teste':'Anual'},[],[pl])
plantio=OC.dia('2026-10-01')
pend=[]
assert OC.datas_validas(ctx,plantio,'P',plantio,plantio+365,None,pend)==([],[])
assert pend==[('ancora_ausente','Após','DAPC'),('ancora_ausente','Antes','DANC')]
assert OC.fim_estimado(ctx,'Teste','',plantio) is None
assert [OC.iso(x[2]) for x in OC.atividades(ctx,plantio,'P',OC.dia('2026-11-01'))]==['2026-11-03','2026-10-29']
print('OK ocupação Python: pendências explícitas, ausência fora da ordenação, datas canônicas')

OC._datas_plano.cache_clear()
antes=len(chamadas)
for _ in range(20): OC.atividades(ctx,plantio,'P')
assert len(chamadas)==antes+1
pl['atividades'][0]['g']['dias']=4
assert OC.atividades(ctx,plantio,'P',OC.dia('2026-11-01'))[0][2]==OC.dia('2026-11-05')
assert len(chamadas)==antes+2
saida=OC.atividades(ctx,plantio,'P')
saida.clear()
assert len(OC.atividades(ctx,plantio,'P'))==2
assert OC._datas_plano.cache_info().maxsize==2048
print('OK cache ocupação: 20 consultas/1 lote, edição invalida, saída isolada, limite2048')

o=OC.mk(ctx,dict(id='c',saf='S',faz='F',faixa='T',tipo='Talhão inteiro',area=1,cult='Teste',plantio='2026-10-01',plano='P'),dict(id='S',ini='2026-01-01',fim='2026-12-31'))
assert o['fim'] is None and o['classe']=='semdata'
assert OC.P(ctx,o)==OC.INF
print('OK plano sem âncora não inventa fim nem liberação confirmada')

# Percurso real: plano substituído na tela → origens da compra → CAL01.
saf, cultivo = next((s, c) for s, cs in D.CULTIVOS.items() for c in cs
                    if c.get('plano') and any(a.get('prods') for a in D.PLANO[c['plano']]['atividades']))
plano = copy.deepcopy(D.PLANO[cultivo['plano']])
atv = next(a for a in plano['atividades'] if a.get('prods'))
atv['g'] = dict(tipo='DAPC', dias=2)
plano['id'] = 'TESTE-PERCURSO-SEM-ANCORA'
plano['atividades'] = [atv]
D.PLANO[plano['id']] = plano
copia = copy.deepcopy(cultivo)
copia['colheita'] = None
anteriores = D.CULTIVOS[saf]
D.CULTIVOS[saf] = [copia]
try:
    override = {copia['id']: plano['id']}
    origens = D.demanda_datada(saf, ajustes={}, planos_extra=override)
    linhas = [x for xs in origens.values() for x in xs]
    assert linhas and all(x['data'] is None for x in linhas), linhas
    # Uma unidade/produto por cálculo; não somar unidades diferentes.
    for produto, xs in origens.items():
        esperado=sum(p['dose']*copia['area'] for p in atv['prods'] if D.prod_nome(p['prod'],copia)==produto)
        assert abs(sum(x['q'] for x in xs)-esperado)<1e-6
        r=D.cal01(0,[dict(dt=x['data'],q=x['q'],tipo='dem',own=True) for x in xs])
        assert r['parcial'] and r['liq']==0 and r['falta'] is None, (produto,r)
        assert abs(r['semData']-esperado)<1e-6
    copia['colheita']='2027-01-10'
    resolvidas=D.demanda_datada(saf, ajustes={}, planos_extra=override)
    assert all(x['data']=='2027-01-12' for xs in resolvidas.values() for x in xs)
    for produto, xs in resolvidas.items():
        assert [x['q'] for x in xs]==[x['q'] for x in origens[produto]]
finally:
    D.CULTIVOS[saf]=anteriores
    del D.PLANO[plano['id']]
print('OK percurso compra: override sem âncora preserva quantidade; resolução atualiza data sem alterar dose/área')

# SU-01: executar a função real isolada do gerador de telas; D2 não é simulado.
import ast
from pathlib import Path
fonte_su = Path(__file__).with_name('areas').joinpath('suprimentos.py')
func = next(n for n in ast.parse(fonte_su.read_text()).body if isinstance(n, ast.FunctionDef) and n.name == '_origens')
ns = {'D2': D, 'nf': lambda v, d=0: f'{v:.{d}f}'}
exec(compile(ast.Module(body=[func], type_ignores=[]), str(fonte_su), 'exec'), ns)
base_c = next(c for c in D.CULTIVOS['S2627'] if c.get('plano') and any(a.get('prods') for a in D.PLANO[c['plano']]['atividades']))
pl_su = copy.deepcopy(D.PLANO[base_c['plano']])
a_su = copy.deepcopy(next(a for a in pl_su['atividades'] if a.get('prods')))
a_su['g'] = dict(tipo='DAPC', dias=2)
pl_su['id'] = 'TESTE-SU01-SEM-ANCORA'
pl_su['atividades'] = [a_su]
c_su = copy.deepcopy(base_c)
c_su.update(plano=pl_su['id'], colheita=None)
cs_antes = D.CULTIVOS['S2627']
D.PLANO[pl_su['id']] = pl_su
D.CULTIVOS['S2627'] = [c_su]
try:
    pend = ns['_origens']()
    assert pend and all(x['dt'] is None for xs in pend.values() for x in xs)
    for produto, xs in pend.items():
        esperado = sum(D.AJUSTES.get(c_su['id'], {}).get(f"{a_su['id']}|{i}", p['dose']) * c_su['area']
                       for i, p in enumerate(a_su['prods']) if D.prod_nome(p['prod'], c_su) == produto)
        assert abs(sum(x['q'] for x in xs) - esperado) < 1e-6
    c_su['colheita'] = '2027-01-10'
    resol = ns['_origens']()
    assert resol.keys() == pend.keys()
    for produto in pend:
        assert len(pend[produto]) == len(resol[produto])
        for antes, depois in zip(pend[produto], resol[produto]):
            assert depois['dt'] == '2027-01-12'
            assert {k:v for k,v in antes.items() if k != 'dt'} == {k:v for k,v in depois.items() if k != 'dt'}
finally:
    D.CULTIVOS['S2627'] = cs_antes
    del D.PLANO[pl_su['id']]
print('OK SU01 _origens real: DAPC+2 sem colheita mantém quantidade/memória/origens; resolver só muda data')
