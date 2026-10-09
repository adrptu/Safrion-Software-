# -*- coding: utf-8 -*-
"""SAF-C01 · fixture do teste de desempenho do serviço de ocupação (dado sintético, ENG-017).
Grava <saida.json> com: cadastros do protótipo (culturas, cultivares, planos), safras e cultivos da base (Santa Rita e
Lagoa Grande) e um caso extremo sintético: talhão X1 de 500 ha com café perene de 1996 (30 anos) em X1-A e 20 ocupações anuais
(soja e milho, 2017 a 2027) em X1-B, mais a safra 2027/28 onde entra uma soja nova em X1-C: 400 ha (café 100 + 400 = 500, limite) e 410 ha (510 > 500, excesso).
Uso: python3 desempenho_fixture.py <pasta gen37> <saida.json>"""
import sys, os, json
GEN = os.path.abspath(sys.argv[1]); OUT = os.path.abspath(sys.argv[2]); sys.path.insert(0, GEN); os.chdir(GEN)
import dados2 as D2, ocupacao_cen as CEN

S = CEN.safras(); CU = CEN.cultivos(); TAL = {k: [list(x) for x in v] for k, v in CEN.talhoes().items()}
# safras novas já usadas pelo ocupacao_unit.py (NOVAS): leitura cruzada na Lagoa
S['NLG28'] = dict(id='NLG28', nome='Nova Lagoa 2027/28', ini='2027-09-01', fim='2028-08-31', faz='Lagoa Grande', ro=False)
# ---------- caso extremo (sintético) ----------
FZ = 'Fazenda Fictícia'
S['FX96'] = dict(id='FX96', nome='Café 1996', ini='1996-01-01', fim='1996-12-31', faz=FZ, ro=True)
X = [dict(id='xcafe', saf='FX96', faz=FZ, faixa='X1-A', tipo='Parcela', talhao='X1', area=100, cult='Café', var='Catuaí 144', plantio='1996-01-01')]
for k, ano in enumerate(range(2017, 2027)):
    sid = 'FX%02d' % (ano % 100)
    S[sid] = dict(id=sid, nome='Safra %d/%02d' % (ano, (ano + 1) % 100), ini='%d-09-01' % ano, fim='%d-08-31' % (ano + 1), faz=FZ, ro=True)
    X.append(dict(id='xs%d' % ano, saf=sid, faz=FZ, faixa='X1-B', tipo='Parcela', talhao='X1', area=200, cult='Soja', var='58 W', plantio='%d-10-01' % ano, plano='SOJA-AT'))
    X.append(dict(id='xm%d' % ano, saf=sid, faz=FZ, faixa='X1-B', tipo='Parcela', talhao='X1', area=200, cult='Milho', var='Híbrido AG 8700', plantio='%d-03-01' % (ano + 1), plano='MILHO-SF'))
S['FX2728'] = dict(id='FX2728', nome='Safra 2027/28', ini='2027-09-01', fim='2028-08-31', faz=FZ, ro=False)
NOVO = dict(id='xnovo', saf='FX2728', faz=FZ, faixa='X1-C', tipo='Parcela', talhao='X1', area=400, cult='Soja', var='58 W', plantio='2027-10-01', plano='SOJA-AT')
SR_NOVO = dict(id='nv', saf='S27SF', faz='Santa Rita', faixa='T1-B', tipo='Parcela', talhao='T1', area=152, cult='Milho', var='Híbrido AG 8700',
               plantio='2027-02-21', plano='MILHO-SF', colheita=None, colheita_real=None, ciclo=None, origem='')
out = dict(ctx=dict(culturas=CEN.CULTURAS, cultivares=[list(x) for x in CEN.cultivares()], planos=D2.PLANOS, folga=CEN.FOLGA),
           safras=S, cults=CU, talhoes=TAL, extremo=dict(faz=FZ, talhoes=[['X1', 500]], cults=X, novo=NOVO, excesso=dict(NOVO, area=410)),
           sr_novo=SR_NOVO)
dst = OUT
json.dump(out, open(dst, 'w'), ensure_ascii=False)
print(dst, len(CU), 'cultivos da base ·', len(X), 'ocupações no caso extremo')
