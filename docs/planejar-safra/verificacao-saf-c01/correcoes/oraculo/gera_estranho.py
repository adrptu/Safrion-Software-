# -*- coding: utf-8 -*-
"""Gerador de fixtures sintéticas para o oráculo diferencial SAF-C01 (fora do repositório).
Uso: python3 gera.py N SEMENTE > fixtures.json
Cada fixture = uma chamada ocChecar (antes, depois, sid, alvo, T) + a tabela da safra do alvo.
Categorias: perenes antigas/recentes, anuais em safras diferentes (plano publicado/rascunho, colheita informada, estimado, sem ciclo,
observado), mesma faixa e faixas distintas, talhão inteiro, áreas no limite exato (±0,004/±0,006/±0,01), edição, Dividir em partes,
ciclo vinculado (mesmo ciclo em duas safras), outra fazenda e outro talhão (não podem contar)."""
import sys, json, random, datetime as dt

N = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
SEED = int(sys.argv[2]) if len(sys.argv) > 2 else 20261009
R = random.Random(SEED)
EP = dt.date(1970, 1, 1)
def iso(d): return (EP + dt.timedelta(days=d)).isoformat()
def dia(s): return (dt.date.fromisoformat(s) - EP).days
def ano(a, b): return R.randint(dia('%d-01-01' % a), dia('%d-12-31' % b))

CTX = dict(
    culturas={'Café': 'Perene', 'Mamão Formosa': 'Perene', 'Soja': 'Anual', 'Milho': 'Anual', 'Feijão': 'Anual', 'Sorgo': 'Anual'},
    cultivares=[['Soja', '58 W', 112], ['Soja', '62 X', 118], ['Milho', 'AG 8700', 140], ['Feijão', 'Pérola', 90]],
    planos=[
        dict(id='PSOJA', nome='Soja AT', cultura='Soja', estado='Publicado', atividades=[
            dict(op='Dessecação', nome='Dessecação pré', g=dict(tipo='DAP', dias=-20)), dict(op='Plantio', nome='Plantio', g=dict(tipo='DAP', dias=0)),
            dict(op='Colheita', nome='Colheita', g=dict(tipo='DAP', dias=120))]),
        dict(id='PSOJA_R', nome='Soja rascunho', cultura='Soja', estado='Rascunho', atividades=[
            dict(op='Dessecação', nome='Dessecação pré', g=dict(tipo='DAP', dias=-15)), dict(op='Colheita', nome='Colheita', g=dict(tipo='DAP', dias=125))]),
        dict(id='PMILHO', nome='Milho SF', cultura='Milho', estado='Publicado', atividades=[dict(op='Colheita', nome='Colheita', g=dict(tipo='DAP', dias=150))]),
        dict(id='PCAFE', nome='Café AR', cultura='Café', estado='Publicado', atividades=[
            dict(op='Adubação', nome='Adubação de formação', g=dict(tipo='DAP', dias=-30)), dict(op='Colheita', nome='Colheita', g=dict(tipo='DAP', dias=240))]),
        dict(id='PSORGO_R', nome='Sorgo rascunho', cultura='Sorgo', estado='Rascunho', atividades=[dict(op='Colheita', nome='Colheita', g=dict(tipo='DAP', dias=100))]),
    ])

KINDS = ['perene_antigo', 'perene_recente', 'anual_plano', 'anual_rascunho', 'anual_informada', 'anual_estimado', 'anual_semdata', 'anual_observado', 'sorgo_rascunho', 'milho_plano']
def cultivo(kind, cid, saf, faixa, tipo, area, plantio, faz='F', talhao='T1'):
    c = dict(id=cid, saf=saf, faz=faz, talhao=talhao, faixa=faixa, tipo=tipo, area=area, cult='Soja', var='58 W', plantio=iso(plantio), plano=None,
             colheita=None, colheita_real=None, ciclo=None, origem='')
    if kind.startswith('perene'):
        c['cult'], c['var'] = R.choice([('Café', 'Catuaí 144'), ('Mamão Formosa', 'Formosa')])
        if c['cult'] == 'Café' and R.random() < 0.3: c['plano'] = 'PCAFE'
    elif kind == 'anual_plano': c['plano'] = 'PSOJA'; c['var'] = R.choice(['58 W', '62 X'])
    elif kind == 'anual_rascunho': c['plano'] = 'PSOJA_R'
    elif kind == 'milho_plano': c['cult'], c['var'], c['plano'] = 'Milho', 'AG 8700', 'PMILHO'
    elif kind == 'anual_informada': c['cult'], c['var'] = 'Milho', 'AG 8700'; c['colheita'] = iso(plantio + R.randint(-30, 220))
    elif kind == 'anual_estimado': c['cult'], c['var'] = R.choice([('Feijão', 'Pérola'), ('Soja', '62 X'), ('Soja', 'Nova sem ciclo')])
    elif kind == 'anual_semdata': c['cult'], c['var'] = 'Sorgo', 'Sem ciclo'
    elif kind == 'sorgo_rascunho': c['cult'], c['var'], c['plano'] = 'Sorgo', 'Sem ciclo', 'PSORGO_R'
    elif kind == 'anual_observado':
        c['plano'] = R.choice(['PSOJA', None]); c['colheita_real'] = iso(plantio + R.randint(-20, 200))
    return c

FAIXAS = ['T1-A', 'T1-B', 'T1-C', 'T1-D']
def area_lim(T, outros):
    """Área do alvo no limite: T − soma de um subconjunto dos outros, com delta de tolerância."""
    sub = [o['area'] for o in outros if R.random() < 0.6]
    delta = R.choice([0, 0, 0.004, -0.004, 0.006, 0.01, -0.01, 0.005, 1, -1])
    return round(max(0.01, T - sum(sub) + delta), 3)

def fixture(k):
    T = R.choice([100.0, 0.01, 5.0, 38.0])
    folga = R.choice([0, 1, 30])
    safras, cults = {}, []
    ano_nova = R.choice([2027, 2045, 2069])
    nova_ini = dia('%d-01-01' % ano_nova) + R.choice([0, 0, 181])
    safras['nova'] = dict(id='nova', nome='Safra nova', ini=iso(nova_ini), fim=iso(nova_ini + R.choice([364, 364, 180])), faz='F', ro=False)
    n = R.randint(1, 6); cat = []
    for i in range(n):
        kind = R.choice(KINDS)
        if kind == 'perene_antigo': pl = ano(1996, 2021)
        elif kind == 'perene_recente': pl = ano(2024, ano_nova)
        else: pl = R.choice([ano(2015, 2022), ano(ano_nova - 1, ano_nova + 1), ano(ano_nova, ano_nova)])
        mesma_saf = R.random() < 0.15
        sid = 'nova' if mesma_saf else 'S%d' % i
        if sid != 'nova':
            si = pl - R.randint(0, 90); safras[sid] = dict(id=sid, nome='Safra %d' % i, ini=iso(si), fim=iso(si + 364), faz='F', ro=R.random() < 0.2)
        inteiro = R.random() < 0.08
        faixa = 'T1' if inteiro else R.choice(FAIXAS)
        area = T if inteiro else round(R.choice([R.uniform(0, T * 0.7), T * 0.4, 0.0, T * 0.25, 0.01]), 2)
        faz, tal = 'F', 'T1'
        u = R.random()
        if u < 0.05: faz = 'G'                       # outra fazenda, mesmo nome de talhão: não conta
        elif u < 0.10: tal = 'T2'; faixa = 'T2' if inteiro else faixa.replace('T1', 'T2')   # outro talhão: não conta
        c = cultivo(kind, 'o%d' % i, sid, faixa, 'Talhão inteiro' if inteiro else 'Parcela', area, pl, faz, tal)
        if R.random() < 0.08 and sid != 'nova':      # ciclo vinculado: o mesmo ciclo aparece também na safra nova
            c['ciclo'] = 'ciclo_o%d' % i
            cults.append(c); cv = dict(c, id='v_o%d' % i, saf='nova'); cults.append(cv); cat.append('vinculo'); continue
        cults.append(c); cat.append(kind)
    safras['G0'] = dict(id='G0', nome='Safra G', ini=safras['nova']['ini'], fim=safras['nova']['fim'], faz='G', ro=False)
    for c in cults:
        if c['faz'] == 'G': c['saf'] = 'G0'
    modo = R.choices(['novo', 'edita', 'divide'], [0.6, 0.2, 0.2])[0]
    akind = R.choice(['anual_plano', 'anual_plano', 'anual_rascunho', 'milho_plano', 'anual_estimado', 'anual_informada', 'perene_recente', 'anual_semdata', 'sorgo_rascunho'])
    apl = R.choice([nova_ini + R.randint(0, 200), nova_ini + R.randint(0, 30)])
    outros_t1 = [c for c in cults if c['faz'] == 'F' and c['talhao'] == 'T1']
    afaixa = R.choice(FAIXAS + ['T1'] * 1)
    aarea = area_lim(T, outros_t1) if R.random() < 0.5 else round(R.uniform(1, T), 2)
    if afaixa == 'T1': aarea = T
    alvo_c = cultivo(akind, 'alvo', 'nova', afaixa, 'Talhão inteiro' if afaixa == 'T1' else 'Parcela', aarea, apl)
    fixtures = []
    if modo == 'novo':
        fixtures.append(dict(antes=cults, depois=cults + [alvo_c], alvo='alvo'))
    elif modo == 'edita':
        velho = dict(alvo_c, area=round(max(0.01, aarea * R.choice([0.5, 1.0])), 2), plantio=iso(apl + R.choice([0, -10, 30])))
        fixtures.append(dict(antes=cults + [velho], depois=cults + [alvo_c], alvo='alvo'))
    else:
        kparts = R.choice([2, 2, 3]); tot = aarea if R.random() < 0.6 else min(T, aarea * 1.2)
        nomes = R.sample(FAIXAS, kparts)
        base = round(tot / kparts, 2); areas = [base] * (kparts - 1) + [round(tot - base * (kparts - 1), 3)]
        partes = [dict(alvo_c, id='parte%d' % j, faixa=nomes[j], tipo='Parcela', area=areas[j]) for j in range(kparts)]
        antes = cults + [dict(alvo_c, id='alvo')]
        depois = cults + partes
        for p in partes: fixtures.append(dict(antes=antes, depois=depois, alvo=p['id']))
    out = []
    for j, fx in enumerate(fixtures):
        out.append(dict(id='F%04d.%d' % (k, j), modo=modo, cat=cat + ['alvo:' + akind], T=T, T2=T, folga=folga, safras=safras, sid='nova', **fx))
    return out

ALL = []
k = 0
while len(ALL) < N:
    ALL.extend(fixture(k)); k += 1
# casos fixos do Codex (comentário 6079770308), na mesma forma
def codex(pl_cafe, area):
    ano_c = pl_cafe[:4]
    saf = dict(velha=dict(id='velha', nome='Perene original', ini=ano_c + '-01-01', fim=ano_c + '-12-31', faz='Fictícia'),
               nova=dict(id='nova', nome='Safra teste 2027', ini='2027-01-01', fim='2027-12-31', faz='Fictícia'))
    cafe = dict(id='cafe', ciclo='cafe', saf='velha', faz='Fictícia', talhao='T1', faixa='T1-A', tipo='Parcela', area=40, cult='Café', var='Teste', plantio=pl_cafe)
    soja = dict(id='soja', ciclo='soja', saf='nova', faz='Fictícia', talhao='T1', faixa='T1-B', tipo='Parcela', area=area, cult='Soja', var='Teste', plantio='2027-06-01', plano='PTEST')
    return dict(id='CODEX-%s-%s' % (pl_cafe[:4], area), modo='codex', cat=['codex'], T=100.0, T2=100.0, folga=1, safras=saf, sid='nova', antes=[cafe], depois=[cafe, soja], alvo='soja',
                ctx=dict(culturas={'Café': 'Perene', 'Soja': 'Anual'}, cultivares=[['Soja', 'Teste', 112]],
                         planos=[dict(id='PTEST', cultura='Soja', estado='Publicado', atividades=[dict(op='Colheita', nome='Colheita', g=dict(tipo='DAP', dias=120))])]))
CODEX = [codex('2020-01-01', 70), codex('2020-01-01', 60), codex('2026-01-01', 70)]
json.dump(dict(ctx=CTX, seed=SEED, fixtures=CODEX + ALL), sys.stdout, ensure_ascii=False)
