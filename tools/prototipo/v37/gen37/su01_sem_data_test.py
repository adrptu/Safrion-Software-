"""EX57: gerador SU01 real; captura a grade, sem simular execução de navegador."""
import copy
import json
from areas import suprimentos as S
D = S.D2
captura = {}
def grade(cols, rows, **kw):
    captura['rows'] = copy.deepcopy(rows)
    return ''
S.grid = grade
S.js = lambda pn, codigo: captura.update(pn=pn, js=codigo)
S.painel = lambda: None
S.shell37 = lambda *a, **kw: captura.update(status=kw['status'])
cultivos = D.CULTIVOS['S2627']
planos = D.PLANO.copy()
estoque = D.ESTOQUE.copy()
receb = D.RECEB.copy()
c = copy.deepcopy(next(c for c in cultivos if c.get('plano') and any(p['prod']=='Fungicida A' for a in D.PLANO[c['plano']]['atividades'] for p in a.get('prods',[]))))
a = copy.deepcopy(next(a for a in D.PLANO[c['plano']]['atividades'] if any(p['prod']=='Fungicida A' for p in a.get('prods',[]))))
a['prods'] = [p for p in a['prods'] if p['prod']=='Fungicida A']
a['g'] = dict(tipo='DAPC', dias=2)
p = copy.deepcopy(D.PLANO[c['plano']]); p.update(id='TESTE-SU01', atividades=[a])
c.update(plano=p['id'], colheita=None)
D.PLANO[p['id']] = p
D.CULTIVOS['S2627'] = [c]
def gerar():
    S.su01()
    rows=captura['rows']
    r=next(x for x in rows if x['v']['item']=='Fungicida A')
    faltas=sum(x['v'].get('falta',0)>0.001 for x in rows)
    assert captura['status'][0].startswith(str(faltas)+' itens com falta firme'), captura['status']
    return r
try:
    D.ESTOQUE['Fungicida A'] = 10**9
    D.RECEB['Fungicida A'] = 0
    pend=gerar()
    assert 'Coberta' not in json.dumps(pend['p']), 'origem sem data foi marcada Coberta'
    assert pend['v'].get('semData') and pend['v']['data'] is None
    assert 'Coberta' not in json.dumps(pend['p'])
    assert 'sem data' in json.dumps(pend['p'],ensure_ascii=False)
    assert pend['kids'] and all(k['v']['data'] is None for k in pend['kids'])
    assert 'Sem data' in json.dumps(pend['kids'],ensure_ascii=False)
    assert 'Fungicida A' not in captura['pn']['rep']['fields'][0]['opts']
    D.ESTOQUE['Fungicida A'] = 0
    falta=gerar()
    assert falta['v']['falta']>0 and falta['v']['semData']
    assert '0 atrasados' in captura['status'][0], captura['status']
    a2=copy.deepcopy(a);a2['id']='DATED';a2['g']=dict(tipo='DATA',dias=None,data='2026-09-01')
    p['atividades'].append(a2)
    misto=gerar()
    assert misto['v']['semData'] and misto['v']['data']=='2026-09-01'
    assert '0 atrasados' in captura['status'][0]
    assert len(misto['kids'])==2 and sum(k['v']['data'] is None for k in misto['kids'])==1
    c['colheita']='2026-08-20'
    resol=gerar()
    assert not resol['v']['semData'] and resol['v']['data']=='2026-08-22'
    assert '1 atrasados' in captura['status'][0], captura['status']
    assert misto['v']['dem']==resol['v']['dem']
    assert [k['v']['dem'] for k in misto['kids']]==[k['v']['dem'] for k in resol['kids']]
    print('OK SU01: sem data/misto/resolvido; quantidade preservada; sem falsa cobertura/atraso; totais coerentes')
finally:
    D.CULTIVOS['S2627']=cultivos
    D.PLANO.clear(); D.PLANO.update(planos)
    D.ESTOQUE.clear(); D.ESTOQUE.update(estoque)
    D.RECEB.clear(); D.RECEB.update(receb)
