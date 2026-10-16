# -*- coding: utf-8 -*-
"""Análise de solo (SOLO-01; docs/analise-solo/ESPECIFICACAO.md §6): fonte única dos laudos sintéticos, da regra de demonstração,
do produto padrão de correção por fazenda e das medições de água no solo (capacidade de campo, ponto de murcha).
Uso: EXTRAJS[0] = cenario.js_prefixo() + dados_solo.js_prefixo() + <js da tela>. As regras ficam em solo.js (já no prefixo do cenário).
Dados sintéticos (inclusive os da Lagoa Grande). Nenhum laudo aqui é aprovação do proprietário; a tabela regional é decisão da fazenda (D-02)."""
import json
import dados2 as D2
import dados_cad as DC
import dados_lagoa_safra as DLS

HOJE = D2.HOJE_ISO            # 2026-09-23 (data do cenário)
VIAVEL = D2.VIAVEL            # chegada viável de uma compra nova (hoje + PRAZO_REPOSICAO), R18
ROTULO = 'Demonstração — tabela regional a decidir pelo proprietário'


def _an(a, v, un, met='', ld='', q=''):
    """analito do laudo: valor em texto decimal (sem float), unidade explícita, método/extrator, limite de detecção e qualificador ('<')."""
    return dict(a=a, v=v, un=un, met=met, ld=ld, q=q)


def _solo(ca, mg, k, hal, al, ext='Mehlich-1', argila=None):
    out = [_an('Ca', ca, 'cmolc/dm³', 'KCl 1 mol/L', '0,1'), _an('Mg', mg, 'cmolc/dm³', 'KCl 1 mol/L', '0,1'),
           _an('K', k, 'mg/dm³', ext, '1')]
    if hal is not None: out.append(_an('H+Al', hal, 'cmolc/dm³', 'SMP', '0,1'))
    out.append(_an('Al', al, 'cmolc/dm³', 'KCl 1 mol/L', '0,1'))
    if argila is not None: out.append(_an('Argila', argila, '%', 'densímetro', '1'))
    return out


def _mais(ph, p, mo, s, b, cu, fe, mn, zn, argila=None, ext='Mehlich-1'):
    """indicadores-chave que faltavam no laudo (proprietário, 15/10/2026: "falta vários indicadores chave de análise de solo"): pH, P, MO, S e
    micronutrientes, com unidade e método explícitos (sintéticos)."""
    out = [_an('pH', ph, 'CaCl₂', 'CaCl₂ 0,01 mol/L', '0,1'), _an('P', p, 'mg/dm³', ext, '1'), _an('MO', mo, 'g/dm³', 'Walkley-Black', '1'),
           _an('S', s, 'mg/dm³', 'fosfato de cálcio', '1'), _an('B', b, 'mg/dm³', 'água quente', '0,05'), _an('Cu', cu, 'mg/dm³', 'Mehlich-1', '0,1'),
           _an('Fe', fe, 'mg/dm³', 'Mehlich-1', '1'), _an('Mn', mn, 'mg/dm³', 'Mehlich-1', '0,1'), _an('Zn', zn, 'mg/dm³', 'Mehlich-1', '0,1')]
    if argila is not None: out.append(_an('Argila', argila, '%', 'densímetro', '1'))
    return out


def L(id, faz, tal, prof, coleta, lab, ext, an, sit, area, zona='', tipo='solo', lab_idx=None, arq='', por='Ana (agrônoma)', em='2026-09-20'):
    v = sit == 'Validado'
    return dict(id=id, tipo=tipo, faz=faz, tal=tal, prof=prof, coleta=coleta, lab=lab, ext=ext, an=an, sit=sit, area=area, zona=zona,
                lab_idx=lab_idx or {}, arq=arq or f'laudo_{lab.split()[0].lower()}_{tal.replace(" ", "")}_{prof.replace("–", "-") or "folha"}.pdf',
                por=(por if v else ''), em=(em if v else ''))


SR, LG = 'Santa Rita', 'Lagoa Grande'
# §6 da especificação: cátions em cmolc/dm³; K em mg/dm³ (Mehlich-1 ou Resina); valores do laboratório preservados (lab_idx)
LAUDOS = [
    L('LAU-2043', SR, 'T4', '0–20', '2026-09-12', 'Lab Solo Vale', 'Mehlich-1', _solo('3.90', '1.40', '31.28', '3.82', '0.10') + _mais('5.4', '14.0', '28', '9.0', '0.32', '1.1', '38', '6.5', '2.1', argila='38'), 'Validado', 204,
      zona='composta por zona (Z2 de 3 zonas)'),
    L('LAU-2044', SR, 'T4', '20–40', '2026-09-12', 'Lab Solo Vale', 'Mehlich-1', _solo('1.10', '0.50', '23.46', '3.00', '0.10', argila='32') + _mais('4.9', '4.2', '18', '14.0', '0.21', '0.8', '30', '3.1', '0.9'), 'Validado', 204,
      zona='composta por zona (3 zonas)'),
    L('LAU-2048', SR, 'P1', '', '2026-09-18', 'Agrolab', 'digestão nítrico-perclórica',
      [_an('N', '48.2', 'g/kg', 'Kjeldahl', '0,1'), _an('P', '3.1', 'g/kg', 'nítrico-perclórica', '0,1'), _an('K', '17.4', '', 'nítrico-perclórica', '—'),
       _an('B', '42', 'mg/kg', 'azometina-H', '1')], 'Inconsistente', 95, tipo='folha', arq='laudo_agrolab_P1_folha.pdf'),
    L('LAU-2050', SR, 'C1', '0–20', '2026-09-19', 'Agrolab', 'Resina', _solo('3.40', '1.10', '97.75', None, '0', ext='Resina') + _mais('5.6', '22', '31', '11.0', '0.45', '2.4', '41', '9.8', '3.6', argila='45', ext='Resina'), 'Aguardando validação', 38),
    L('LAU-2061', SR, 'T1', '0–20', '2026-09-18', 'Lab Solo Vale', 'Mehlich-1', _solo('3.10', '1.25', '58.65', '3.00', '0') + _mais('5.5', '18.5', '30', '8.0', '0.38', '1.3', '35', '7.2', '2.6', argila='40'), 'Validado', 312),
    L('LAU-2063', SR, 'T2', '0–20', '2026-09-18', 'Lab Solo Vale', 'Mehlich-1', _solo('1.25', '0.44', '136.85', '3.06', '0.30') + _mais('4.8', '7.5', '22', '6.0', '0.18', '0.7', '52', '3.8', '0.8', argila='36'), 'Validado', 298),
    L('LAU-2071', LG, 'Pivô 12', '0–20', '2026-09-15', 'Agrolab', 'Mehlich-1', _solo('2.90', '0.95', '78.20', '4.05', '0.20') + _mais('5.1', '11.0', '25', '7.5', '0.27', '0.9', '44', '5.0', '1.4', argila='28'), 'Validado', 48.47,
      lab_idx={'V': '49'}),
    L('LAU-2072', LG, 'Pivô 12', '20–40', '2026-09-15', 'Agrolab', 'Mehlich-1', _solo('0.30', '0.20', '31.28', '4.00', '0.60', argila='20') + _mais('4.6', '3.0', '14', '12.0', '0.15', '0.6', '33', '2.2', '0.5'), 'Validado', 48.47),
    # campanha de amostragem em grade da Lagoa Grande (15/10/2026, sintética): mais pivôs com laudo para o mapa de calor do solo; V acima da meta
    # do mamão (70 %): sem sugestão de calagem
    L('LAU-2055', LG, 'Pivô 2', '0–20', '2026-09-16', 'Agrolab', 'Mehlich-1', _solo('3.60', '1.30', '110.00', '2.00', '0') + _mais('5.6', '16.0', '27', '8.5', '0.30', '1.0', '40', '6.0', '1.8', argila='30'), 'Validado', DLS.TALHOES['Pivô 2']),
    L('LAU-2056', LG, 'Pivô 5', '0–20', '2026-09-16', 'Agrolab', 'Mehlich-1', _solo('3.80', '1.40', '95.00', '2.10', '0') + _mais('5.5', '9.5', '24', '7.0', '0.24', '0.8', '46', '4.6', '1.2', argila='26'), 'Validado', DLS.TALHOES['Pivô 5']),
    L('LAU-2057', LG, 'Pivô 9', '0–20', '2026-09-16', 'Agrolab', 'Mehlich-1', _solo('4.00', '1.50', '125.00', '2.20', '0') + _mais('5.7', '21.0', '32', '9.5', '0.41', '1.4', '37', '7.8', '2.4', argila='34'), 'Validado', DLS.TALHOES['Pivô 9']),
    L('LAU-2058', LG, 'Pivô 19', '0–20', '2026-09-16', 'Agrolab', 'Mehlich-1', _solo('3.70', '1.20', '140.00', '1.90', '0') + _mais('5.8', '12.5', '29', '8.0', '0.35', '1.2', '42', '6.8', '2.0', argila='31'), 'Validado', DLS.TALHOES['Pivô 19']),
]
# ---------- indicadores do laudo e mapa de calor (proprietário, 15/10/2026: "cada indicador da análise de solo escolhido tem que gerar esse mapa
# de calor das manchas boas e ruins por todo o talhão com contraste") ----------
# k: analito do laudo (a) ou índice calculado (soloIdx: V, T, SB, m); d: '+' maior é melhor, '-' maior é pior, '0' textura (sem bom/ruim);
# cortes/classes: interpretação DEMONSTRATIVA (ROTULO: a tabela regional é decisão da fazenda, D-02), usada só no contraste "Absoluto".
IND = [
    dict(k='V', l='V %', un='%', dec=0, d='+', idx=True, cortes=['20', '35', '50', '70'], classes=['muito baixo', 'baixo', 'médio', 'adequado', 'alto']),
    dict(k='pH', l='pH', un='CaCl₂', dec=1, d='+', cortes=['4.4', '5.0', '5.5', '6.0'], classes=['acidez muito alta', 'acidez alta', 'acidez média', 'adequado', 'alto']),
    dict(k='P', l='P', un='mg/dm³', dec=1, d='+', cortes=['6', '12', '18', '30'], classes=['muito baixo', 'baixo', 'médio', 'adequado', 'alto']),
    dict(k='K', l='K', un='mg/dm³', dec=0, d='+', cortes=['40', '80', '120'], classes=['baixo', 'médio', 'adequado', 'alto']),   # os da regra do K (REGRA['k'], conferido abaixo)
    dict(k='Ca', l='Ca', un='cmolc/dm³', dec=2, d='+', cortes=['1.5', '2.5', '4.0'], classes=['baixo', 'médio', 'adequado', 'alto']),
    dict(k='Mg', l='Mg', un='cmolc/dm³', dec=2, d='+', cortes=['0.5', '0.9', '1.5'], classes=['baixo', 'médio', 'adequado', 'alto']),
    dict(k='MO', l='MO', un='g/dm³', dec=0, d='+', cortes=['15', '25', '35'], classes=['baixo', 'médio', 'adequado', 'alto']),
    dict(k='T', l='CTC', un='cmolc/dm³', dec=1, d='+', idx=True, cortes=['2.5', '4.5', '8', '12'], classes=['muito baixa', 'baixa', 'média', 'adequada', 'alta']),
    dict(k='SB', l='SB', un='cmolc/dm³', dec=2, d='+', idx=True, cortes=['1.5', '3.0', '6.0'], classes=['baixa', 'média', 'adequada', 'alta']),
    dict(k='m', l='m %', un='%', dec=0, d='-', idx=True, cortes=['15', '30', '50'], classes=['baixa', 'média', 'alta', 'muito alta']),
    dict(k='Al', l='Al', un='cmolc/dm³', dec=2, d='-', cortes=['0.2', '0.5', '1.0'], classes=['baixo', 'médio', 'alto', 'muito alto']),
    dict(k='H+Al', l='H+Al', un='cmolc/dm³', dec=2, d='-', cortes=['2.5', '5.0', '9.0'], classes=['baixa', 'média', 'alta', 'muito alta']),
    dict(k='S', l='S', un='mg/dm³', dec=1, d='+', cortes=['4', '9', '15'], classes=['baixo', 'médio', 'adequado', 'alto']),
    dict(k='B', l='B', un='mg/dm³', dec=2, d='+', cortes=['0.2', '0.3', '0.5'], classes=['baixo', 'médio', 'adequado', 'alto']),
    dict(k='Cu', l='Cu', un='mg/dm³', dec=1, d='+', cortes=['0.4', '0.8', '1.2'], classes=['baixo', 'médio', 'adequado', 'alto']),
    dict(k='Fe', l='Fe', un='mg/dm³', dec=0, d='+', cortes=['12', '30', '45'], classes=['baixo', 'médio', 'adequado', 'alto']),
    dict(k='Mn', l='Mn', un='mg/dm³', dec=1, d='+', cortes=['2', '5', '8'], classes=['baixo', 'médio', 'adequado', 'alto']),
    dict(k='Zn', l='Zn', un='mg/dm³', dec=1, d='+', cortes=['1.0', '1.6', '2.2'], classes=['baixo', 'médio', 'adequado', 'alto']),
    dict(k='Argila', l='Argila', un='%', dec=0, d='0', cortes=['15', '35', '60'], classes=['arenosa', 'média', 'argilosa', 'muito argilosa']),
]
# variação dentro do talhão por grupo de analitos (mesmo campo para as bases; Al e H+Al no sentido contrário): (grupo, amplitude relativa)
_VAR = {'Ca': ('bases', .28), 'Mg': ('bases', .24), 'pH': ('bases', None), 'Al': ('bases', -.6), 'H+Al': ('bases', -.22), 'K': ('k', .32), 'P': ('p', .45),
        'MO': ('mo', .18), 'S': ('mo', .25), 'B': ('micro', .3), 'Cu': ('micro', .3), 'Fe': ('fe', .25), 'Mn': ('micro', .3), 'Zn': ('micro', .35), 'Argila': ('arg', .08)}


def pontos(l):
    """pontos georreferenciados da amostragem em grade do laudo (sintéticos): posição (u, v) no quadrado unitário do talhão (o mapa leva ao polígono
    ou ao círculo do pivô) e o valor de cada analito no ponto. Média dos pontos = valor do laudo (composta), na casa decimal do laudo; a variação
    é suave no espaço (manchas), com o mesmo campo para Ca, Mg e pH (Al e H+Al no sentido contrário)."""
    import math, hashlib
    from decimal import Decimal, ROUND_HALF_UP
    if l['tipo'] != 'solo': return []
    n = max(8, min(30, round(float(l['area']) / 4)))
    h = int(hashlib.sha256(l['id'].encode()).hexdigest()[:8], 16)
    xy = []
    for i in range(n):   # espiral de Fermat no disco unitário: cobertura uniforme, sem acaso
        r = math.sqrt((i + .5) / n) * .92; t = i * 2.399963 + (h % 360) * math.pi / 180
        xy.append(((r * math.cos(t) + 1) / 2, (r * math.sin(t) + 1) / 2))
    def campo(g):
        a = 1 + (h + sum(map(ord, g))) % 7 * .23; b = .7 + (h // 7 + len(g) * 13) % 5 * .29; f1 = (h % 97) / 97 * 6.28 + len(g); f2 = (h % 89) / 89 * 6.28 + 2 * len(g)
        z = [math.sin(6.28 * a * u + f1) + math.cos(6.28 * b * v + f2) + .6 * math.sin(6.28 * (u + v) * .8 + f1 * f2) for u, v in xy]
        m = sum(z) / n; z = [x - m for x in z]; mx = max(abs(x) for x in z) or 1; return [x / mx for x in z]
    campos = {}; pts = [dict(id=f'A{i + 1:02d}', u=round(u, 4), v=round(v, 4), an={}) for i, (u, v) in enumerate(xy)]
    for x in l['an']:
        a = x['a']; g, amp = _VAR.get(a, ('outro', .2))
        if x['v'] is None or a not in _VAR: continue
        m = Decimal(x['v']); q = Decimal(1).scaleb(-len(x['v'].split('.')[1]) if '.' in x['v'] else 0)
        z = campos.setdefault(g, campo(g))
        vs = [(m + Decimal(str(.4 * zi)) if amp is None else m * (1 + Decimal(str(amp * zi)))).quantize(q, ROUND_HALF_UP) for zi in z]
        vs = [max(Decimal(0), v) for v in vs]
        d = m * n - sum(vs); j = max(range(n), key=lambda k: vs[k]); vs[j] = max(Decimal(0), vs[j] + d)   # média exata = valor do laudo
        for p_, v in zip(pts, vs): p_['an'][a] = str(v)
    return pts


for _l in LAUDOS: _l['pts'] = pontos(_l)

# laudo de exemplo do formulário "Registrar laudo" (D-23): nasce Aguardando validação; só depois de validado sugere a calagem do T7
EXEMPLO = dict(faz=SR, tal='T7', prof='0–20', coleta='2026-09-22', lab='Lab Solo Vale', ext='Mehlich-1', area=42,
               an=_solo('3.90', '1.30', '160.31', '2.89', '0'), arq='laudo_labsolovale_T7_0-20.pdf')
LABS = ['Lab Solo Vale', 'Agrolab', 'Embrapa Solos (convênio)']

# Regra de demonstração (D-02, D-03, D-18; R06–R08 e R10). estado: 'demonstração' ou 'desligada' (zero sugestões, laudo visível)
REGRA = dict(estado='demonstração', rotulo=ROTULO,
             v2={'Soja': '60', 'Milho': '60', 'Feijão': '60', 'Café': '60', 'Mamão Formosa': '70'},
             k=dict(culturas=['Soja'], ext='Mehlich-1', cortes=['40', '80', '120'], classes=['baixo', 'médio', 'adequado', 'alto'],
                    faixa=['2400', '4800'], tabela=[['3600', {'baixo': '90', 'médio': '72', 'adequado': '48', 'alto': '0'}],
                                                    ['4800', {'baixo': '108', 'médio': '90', 'adequado': '60', 'alto': '0'}]]),
             gesso=dict(estado='demonstração', ca='0.5', m='20', k={'Anual': '50', 'Perene': '75'}),
             validade=dict(meses=24),   # DEC-1610-04 (16/10/2026): 24 meses da coleta para todo talhão (PEND-13); a exceção de 12 meses para irrigado saiu
             tol=dict(pp='0.5', cmolc='0.05'))   # D-17: diferença do laboratório acima disto mostra "difere do laboratório"
assert next(i for i in IND if i['k'] == 'K')['cortes'] == REGRA['k']['cortes'], 'K do mapa de calor = K da regra (fonte única)'
# produto padrão de correção por fazenda (D-12); trocar o produto é ação explícita no painel (R19)
CORR = {SR: dict(cal='Calcário dolomítico'), LG: dict(cal='Calcário dolomítico filler', ges='Gesso agrícola')}

# ---------- água no solo (pedido do proprietário 05–09/10: teste de capacidade de campo por talhão) ----------
# Propriedade do solo, medida por talhão ou zona. Não é capacidade do equipamento (pivô) nem recomendação técnica: a lâmina continua
# vindo da política de água (PA-07) e do responsável técnico. CAD = (CC − PMP) × profundidade efetiva (solo.js, soloCAD).
AGUA = [
    dict(id='AGS-001', faz=SR, tal='T7', zona='', data='2026-08-20', prof='0–40', z='40', met='Curva de retenção (laboratório)', un='% volume',
         cc='32', pmp='18', fonte='Lab Solo Vale', resp='Ana (agrônoma)'),
    dict(id='AGS-002', faz=SR, tal='P1', zona='', data='2026-08-28', prof='0–30', z='30', met='Anel volumétrico (campo + estufa)', un='% volume',
         cc='28', pmp='15', fonte='Agrolab', resp='Ana (agrônoma)'),
    dict(id='AGS-003', faz=SR, tal='P2', zona='Z1 (baixada)', data='2026-09-02', prof='0–30', z='30', met='Curva de retenção (laboratório)', un='mm/cm',
         cc='3.1', pmp='1.6', fonte='Lab Solo Vale', resp='Ana (agrônoma)'),
    dict(id='AGS-004', faz=LG, tal='Pivô 12', zona='', data='2026-09-16', prof='0–40', z='40', met='Capacidade de campo no campo (inundação e drenagem)', un='% volume',
         cc='30', pmp='', fonte='Agrolab', resp='Ana (agrônoma)'),
]
METODOS_AGUA = ['Curva de retenção (laboratório)', 'Anel volumétrico (campo + estufa)', 'Capacidade de campo no campo (inundação e drenagem)']
UN_AGUA = ['% volume', 'mm/cm']
# quem mede (revisão A9, S4): pessoas do cadastro (CD-04, dados_cad.PESSOAS) das equipes de Agronomia e Irrigação; a agrônoma no texto da semente
RESP_AGUA = ['Ana (agrônoma)'] + [f"{p['nome']} ({p['funcao'].lower()})" for p in DC.PESSOAS if p['equipe'] in ('Agronomia', 'Irrigação') and p['nome'] != 'Ana']


def _talhao(c):
    return c['local'] if c['tipo'] != 'Parcela' else c['local'].rsplit('-', 1)[0]


def cultivos():
    """cultivos das safras abertas (AG-02, "Uso no plano"): mesma fonte do Planejar safra (dados2), com o talhão de cada parcela (R02)."""
    out = []
    for s in D2.SAFRAS:
        if s['ro']: continue
        for c in D2.CULTIVOS.get(s['id'], []):
            out.append(dict(id=c['id'], saf=s['id'], safNome=s['nome'], faz=s.get('fazenda', SR), local=c['local'], tal=_talhao(c), cultura=c['cultura'],
                            area=c['area'], meta=c['meta'], unm=c['un_meta'], plano=c['plano'] or '', plantio=c['plantio'], colheita=c.get('colheita') or ''))
    return out


def os_chave():
    """cultivo|atividade → O.S. do registro (R11: a O.S. existente decide se ainda dá para mudar a dose)."""
    import dados as D
    out = {}
    for o in D.ORDENS + D.ORDENS_LG:
        k = o.get('chave')
        for x in (k if isinstance(k, (list, tuple)) else ([k] if k else [])): out[x] = o['id']
    return out


def dados():
    itens = {}
    for p in D2.PLANOS:
        for a in p['atividades']:
            for x in a['prods']: itens.setdefault(x['prod'], dict(un=x['un'], grupo=x['grupo']))
    for n, x in DC.ITENS_NOVOS.items(): itens.setdefault(n, dict(un=x['un'], grupo=x['grupo']))
    corr_prods = sorted({p for f in CORR.values() for p in f.values()})
    return dict(hoje=HOJE, viavel=VIAVEL, laudos=LAUDOS, exemplo=EXEMPLO, ind=IND, labs=LABS, regra=REGRA, corr=CORR,
                gar={n: {k: v for k, v in g.items() if k != 'txt'} for n, g in DC.GARANTIA.items()},
                preco={n: DC.preco_ref(n) for n in list(itens) if DC.preco_ref(n) != ''},
                itens={n: itens[n] for n in corr_prods + ['KCl 60%'] if n in itens},
                classe={c[0]: c[2] for c in DC.CULTURAS}, agua=AGUA, metodosAgua=METODOS_AGUA, unAgua=UN_AGUA,
                cult=cultivos(), osChave=os_chave(),
                planos={p['id']: dict(id=p['id'], nome=p['nome'], versao=p['versao'], cultura=p['cultura'], atividades=p['atividades']) for p in D2.PLANOS},
                safras={s['id']: dict(nome=s['nome'], faz=s.get('fazenda', SR), ro=s['ro']) for s in D2.SAFRAS})


def js_prefixo():
    return 'const SOLO0 = ' + json.dumps(dados(), ensure_ascii=False).replace('</', '<\\/') + ';\n'


if __name__ == '__main__':
    d = dados(); print(len(d['laudos']), 'laudos ·', len(d['cult']), 'cultivos ·', d['preco'].get('Calcário dolomítico'), '· os', d['osChave'])
