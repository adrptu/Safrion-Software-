# -*- coding: utf-8 -*-
"""SOLO-FOLHA-NIVEIS · conferência dos oráculos em Decimal (independente do solo.js).
Lê de dados_solo.py só os valores dos laudos (para provar que a cópia aqui é a do protótipo) e o corte demonstrativo (contraprova).
As faixas das fontes estão transcritas abaixo, com o localizador, das páginas abertas em 16/10/2026:
  CER04 = Embrapa Cerrados · Sousa & Lobato (ed.) · Cerrado: correção do solo e adubação · 2ª ed. 2004 · PDF Infoteca (impressão de 2017)
          sha256 986b1a7c5d4e75f950b56e54d9351334d36f44b9934ecd5da3ebbeeb70f475aa
  SOJ20 = Embrapa Soja · Tecnologias de produção de soja · Sistemas de Produção 17 · jun/2020
          sha256 a3bc85a7fbe29a6630583803fa54da38614c36da225b7e216ccb363ff166701e
Uso: python3 -B solo_folha_chk.py   (sai com código 1 se algum oráculo falhar)"""
import sys, datetime
from decimal import Decimal as D, ROUND_HALF_UP

import os
GEN = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..', 'tools', 'prototipo', 'v37', 'gen37'))
sys.path.insert(0, GEN)
import dados_solo as DS  # noqa: E402  (só dados)

OK, FAIL = [], []
def chk(nome, obtido, esperado):
    (OK if obtido == esperado else FAIL).append(nome)
    print(('OK    ' if obtido == esperado else 'FALHA ') + nome + ' → ' + str(obtido) + ('' if obtido == esperado else '  (esperado ' + str(esperado) + ')'))

def q(x, casas):
    return x.quantize(D(1).scaleb(-casas), ROUND_HALF_UP)

# ---------------- laudos do protótipo (valores copiados e conferidos contra dados_solo.py) ----------------
LAU = {l['id']: l for l in DS.LAUDOS}
def an(lid, a):
    x = next(y for y in LAU[lid]['an'] if y['a'] == a)
    return D(x['v']), x['un'], x['met']

COPIA = {  # id: {analito: valor como texto}
    'LAU-2061': dict(Ca='3.10', Mg='1.25', K='58.65', **{'H+Al': '3.00'}, Al='0', P='18.5', MO='30', Fe='35', B='0.38', Argila='40'),
    'LAU-2063': dict(Ca='1.25', Mg='0.44', K='136.85', **{'H+Al': '3.06'}, Al='0.30', P='7.5', Argila='36'),
    'LAU-2043': dict(Ca='3.90', Mg='1.40', K='31.28', **{'H+Al': '3.82'}, P='14.0', S='9.0', Argila='38'),
    'LAU-2044': dict(Ca='1.10', Mg='0.50', K='23.46', **{'H+Al': '3.00'}, Al='0.10', S='14.0'),
    'LAU-2071': dict(Ca='2.90', Mg='0.95', K='78.20', **{'H+Al': '4.05'}, P='11.0', B='0.27', Argila='28'),
    'LAU-2072': dict(Ca='0.30', Mg='0.20', K='31.28', Al='0.60'),
    'LAU-2055': dict(Ca='3.60', Mg='1.30', K='110.00', **{'H+Al': '2.00'}, Argila='30'),
    'LAU-2050': dict(P='22'),
}
for lid, d in COPIA.items():
    for a, v in d.items():
        chk(f'cópia {lid} {a}', an(lid, a)[0], D(v))
chk('cópia LAU-2050 extrator', LAU['LAU-2050']['ext'], 'Resina')
chk('cópia LAU-2061 MO unidade', an('LAU-2061', 'MO')[1], 'g/dm³')
chk('cópia LAU-2048 K sem unidade', an('LAU-2048', 'K')[1], '')
chk('cópia LAU-2071 V do laboratório', LAU['LAU-2071']['lab_idx'].get('V'), '49')

def cmolc_k(mg):  # PRD 38.3: mg/dm³ → cmolc/dm³ pelo elemento (K ÷ 391), o mesmo divisor do solo.js
    return mg / D('391')

def idx(lid, al=None):
    g = lambda a: an(lid, a)[0]
    ca, mg, k = g('Ca'), g('Mg'), cmolc_k(g('K'))
    sb = ca + mg + k
    r = dict(SB=sb)
    try:
        r['T'] = sb + g('H+Al')
        r['V'] = D(100) * sb / r['T']
    except StopIteration:
        pass
    try:
        alv = g('Al'); r['t'] = sb + alv; r['m'] = D(100) * alv / r['t']
    except StopIteration:
        pass
    return r

# ---------------- classificador "como escrito" (fronteira da fonte; vão = entre classes; duas = sobreposição) ----------------
INF = None
def C(nome, padrao, lo, lo_inc, hi, hi_inc):
    return dict(nome=nome, padrao=padrao, lo=None if lo is None else D(lo), lo_inc=lo_inc, hi=None if hi is None else D(hi), hi_inc=hi_inc)

def classifica(classes, v):
    hit = []
    for c in classes:
        ok_lo = c['lo'] is None or (v >= c['lo'] if c['lo_inc'] else v > c['lo'])
        ok_hi = c['hi'] is None or (v <= c['hi'] if c['hi_inc'] else v < c['hi'])
        if ok_lo and ok_hi: hit.append(c)
    if not hit: return ('entre classes', None)
    if len(hit) > 1: return ('sobreposição na fonte', None)
    return (hit[0]['nome'], hit[0]['padrao'])

COR = {'muito baixo': 'vermelho', 'baixo': 'laranja', 'médio': 'amarelo', 'adequado': 'verde', 'alto': 'azul', 'muito alto': 'roxo'}  # PEND-DS-11 (DEC-1610-06), estendida

# CER04 Anexo 6 · Tabela 6 (p. 394): P Mehlich-1, 0–20 cm, sequeiro, culturas anuais, por argila
P_SEQ = {
    '≤15':   [C('muito baixo', 'muito baixo', '0', True, '6.0', True), C('baixo', 'baixo', '6.1', True, '12.0', True), C('médio', 'médio', '12.1', True, '18.0', True), C('adequado', 'adequado', '18.1', True, '25.0', True), C('alto', 'alto', '25.0', False, None, True)],
    '16-35': [C('muito baixo', 'muito baixo', '0', True, '5.0', True), C('baixo', 'baixo', '5.1', True, '10.0', True), C('médio', 'médio', '10.1', True, '15.0', True), C('adequado', 'adequado', '15.1', True, '20.0', True), C('alto', 'alto', '20.0', False, None, True)],
    '36-60': [C('muito baixo', 'muito baixo', '0', True, '3.0', True), C('baixo', 'baixo', '3.1', True, '5.0', True), C('médio', 'médio', '5.1', True, '8.0', True), C('adequado', 'adequado', '8.1', True, '12.0', True), C('alto', 'alto', '12.0', False, None, True)],
    '>60':   [C('muito baixo', 'muito baixo', '0', True, '2.0', True), C('baixo', 'baixo', '2.1', True, '3.0', True), C('médio', 'médio', '3.1', True, '4.0', True), C('adequado', 'adequado', '4.1', True, '6.0', True), C('alto', 'alto', '6.0', False, None, True)],
}
def faixa_argila(arg):  # CER04 Anexo 6 Tab. 6: ≤ 15 · 16 a 35 · 36 a 60 · > 60 (vão entre 15 e 16 e entre 35 e 36: argila do laudo é inteira)
    if arg <= 15: return '≤15'
    if 16 <= arg <= 35: return '16-35'
    if 36 <= arg <= 60: return '36-60'
    if arg > 60: return '>60'
    return 'entre faixas'
# SOJ20 Tabela 10 (p. 152; Sousa et al., 2016): mesma grade, com "alto" fechado e "muito alto"; só a faixa 36–60
P_SOJ20_36_60 = [C('muito baixo', 'muito baixo', '0', True, '3.0', True), C('baixo', 'baixo', '3.1', True, '5.0', True), C('médio', 'médio', '5.1', True, '8.0', True),
                 C('adequado', 'adequado', '8.1', True, '12.0', True), C('alto', 'alto', '12.1', True, '18.0', True), C('muito alto', 'muito alto', '18.0', False, None, True)]
# CER04 Anexo 6 · Tabela 8 (p. 394): P resina, sequeiro
P_RES_SEQ = [C('muito baixo', 'muito baixo', '0', True, '5', True), C('baixo', 'baixo', '6', True, '8', True), C('médio', 'médio', '9', True, '14', True), C('adequado', 'adequado', '15', True, '20', True), C('alto', 'alto', '20', False, None, True)]
# CER04 Anexo 6 · Tabela 12 (p. 396): K Mehlich-1 (mg/dm³), 0–20 cm, por CTC a pH 7
K_ANU = {'<4': [C('baixo', 'baixo', None, True, '15', True), C('médio', 'médio', '16', True, '30', True), C('adequado', 'adequado', '31', True, '40', True), C('alto', 'alto', '40', False, None, True)],
         '>=4': [C('baixo', 'baixo', None, True, '25', True), C('médio', 'médio', '26', True, '50', True), C('adequado', 'adequado', '51', True, '80', True), C('alto', 'alto', '80', False, None, True)]}
# CER04 cap. perenes (L. R. M. de Andrade) · Tabela 3 (p. 324): P Mehlich-1, perenes e semiperenes, por argila
P_PER = {'16-35': [C('baixo', 'baixo', None, True, '10.0', False), C('médio', 'médio', '10.1', True, '15.0', True), C('adequado', 'adequado', '15.0', False, None, True)]}
# CER04 cap. perenes · Tabela 5 (p. 326): K, perenes; condição "CTC < 4,0 ou argila < 20 %" × "CTC > 4,0 ou argila > 20 %"
K_PER = {'baixa': [C('baixo', 'baixo', None, True, '15', False), C('médio', 'médio', '16', True, '40', True), C('adequado', 'adequado', '40', False, None, True)],
         'alta':  [C('baixo', 'baixo', None, True, '25', False), C('médio', 'médio', '25', True, '80', True), C('adequado', 'adequado', '80', False, None, True)]}
def cond_k_per(T, arg):
    a = T < 4 or arg < 20; b = T > 4 or arg > 20
    if a and not b: return 'baixa'
    if b and not a: return 'alta'
    return 'condição ambígua'
# CER04 Anexo 6 · Tabela 9 (p. 395): V %; alvo V₂ (p. 84): 50 % sequeiro, 60 % irrigado; produtividade estável 40–60 % e cai acima de 60 %
V_CLS = [C('baixo', 'baixo', None, True, '20', True), C('médio', 'médio', '21', True, '35', True), C('adequado', 'adequado', '36', True, '60', True), C('alto', 'alto', '61', True, '70', True), C('muito alto', 'muito alto', '71', True, None, True)]
# Tabela 10 (p. 395): B água quente · Tabela 28 da SOJ20 (p. 172): B água quente
B_CER04 = [C('baixo', None, None, True, '0.2', False), C('médio', None, '0.3', True, '0.5', True), C('alto', None, '0.5', False, None, True)]
B_SOJ20 = [C('baixo', None, None, True, '0.30', False), C('médio', None, '0.30', True, '0.50', True), C('alto', None, '0.50', False, None, True)]
# Tabela 11 (p. 395): S, média de 0–20 e 20–40 cm (sem ideal na fonte)
S_CER04 = [C('baixo', None, None, True, '4', True), C('médio', None, '5', True, '9', True), C('alto', None, '10', True, None, True)]
# Tabela 5 (p. 393): m % (sem classe "adequada" na fonte)
M_CER04 = [C('baixa', None, None, True, '20', False), C('alta', None, '20', True, '60', True), C('muito alta', None, '60', False, None, True)]
# Tabela 4 (p. 393): Ca abaixo de 20 cm
CA_SUB = [C('muito baixo', 'muito baixo', None, True, '0.1', False), C('baixo', 'baixo', '0.1', True, '0.5', True), C('adequado', 'adequado', '0.5', False, None, True)]
# SOJ20 Tabela 7 (p. 149): folha SEM pecíolo, soja, g/kg e mg/kg; época R1–R2 (determinado) ou R2 (indeterminado) (p. 149)
def faixa3(lo, hi):
    return [C('baixo', 'baixo', None, True, lo, False), C('adequado', 'adequado', lo, True, hi, True), C('alto', 'alto', hi, False, None, True)]
SOJA_T7 = dict(N=faixa3('45.0', '65.0'), P=faixa3('2.8', '4.5'), K=faixa3('18.0', '25.0'), Ca=faixa3('6.0', '10.0'), Mg=faixa3('2.8', '5.0'), S=faixa3('2.4', '4.0'),
               B=faixa3('40', '60'), Cu=faixa3('6', '12'), Fe=faixa3('90', '180'), Mn=faixa3('70', '150'), Zn=faixa3('30', '45'))
# CER04 cap. 10 (S. A. de Oliveira) · Tabelas 2 (pp. 252–253) e 3 (p. 254): faixa adequada; abaixo/acima nomeados pela curadoria
def faixa_ad(lo, hi):
    return [C('abaixo da faixa', 'baixo', None, True, lo, False), C('na faixa', 'adequado', lo, True, hi, True), C('acima da faixa', 'alto', hi, False, None, True)]
CAFE = dict(N=faixa_ad('26', '32'), P=faixa_ad('1.2', '2.0'), K=faixa_ad('18', '25'), Ca=faixa_ad('10', '15'), Mg=faixa_ad('3.5', '5.0'), S=faixa_ad('1.5', '2.0'),
            B=faixa_ad('50', '80'), Cu=faixa_ad('10', '20'), Fe=faixa_ad('50', '200'), Mn=faixa_ad('50', '200'), Zn=faixa_ad('10', '20'))
MAMAO_PEC = dict(N=faixa_ad('10', '25'), P=faixa_ad('2.2', '4.0'), K=faixa_ad('35', '50'), Ca=faixa_ad('10', '30'), Mg=faixa_ad('4.0', '10'), S=faixa_ad('4.0', '6.0'))
SOJA_COMPEC = dict(K=faixa_ad('17', '25'))

def mais_meses(iso, n):
    """validade = coleta + n meses; dia que não existe no mês de chegada vira o último dia válido dele (R2 do Codex, achado 4):
    29/02/2024 + 24 meses = 28/02/2026 (vale até 28/02; vencido em 01/03)."""
    import calendar
    y, m, d = map(int, iso.split('-')); m += n; y += (m - 1) // 12; m = (m - 1) % 12 + 1
    return datetime.date(y, m, min(d, calendar.monthrange(y, m)[1])).isoformat()

HOJE = DS.HOJE
chk('data do cenário', HOJE, '2026-09-23')
print('\n== SOLO (F1: CER04) ==')
# O1 · P do T2
p, un, met = an('LAU-2063', 'P'); arg = an('LAU-2063', 'Argila')[0]
fx = faixa_argila(arg); cl = classifica(P_SEQ[fx], p)
chk('O1 LAU-2063 P 7,5 Mehlich-1 · argila 36 % → faixa 36–60 → classe', (fx, cl[0], COR[cl[1]]), ('36-60', 'médio', 'amarelo'))
# posição do marcador no gráfico de bala (segmentos iguais por classe; dentro da classe, linear)
seg = 2; lo, hi = D('5.1'), D('8.0')
pos = (D(seg) + (p - lo) / (hi - lo)) / D(5)
chk('O1b marcador do P 7,5: 3º segmento a 82,76 % dele; 56,55 % da barra', (q((p - lo) / (hi - lo) * 100, 2), q(pos * 100, 2)), (D('82.76'), D('56.55')))
indP0 = next(i for i in DS.IND if i['k'] == 'P')
chk('O1c contraprova: a classe demonstrativa de hoje para o P 7,5 do T2 é "baixo" (cortes 6/12/18/30, sem argila nem cultura)', indP0['classes'][sum(1 for c in indP0['cortes'] if p >= D(c))], 'baixo')
# O2 · V do T2
r = idx('LAU-2063')
chk('O2 LAU-2063 SB, T, V', (q(r['SB'], 2), q(r['T'], 2), q(r['V'], 1)), (D('2.04'), D('5.10'), D('40.0')))
chk('O2b V 40,0 → classe da Tab. 9 e alvo V₂ 50 % (sequeiro): abaixo do alvo; NC = (50 − 40) × 5,10 ÷ 100 t/ha', (classifica(V_CLS, r['V'])[0], q((D(50) - r['V']) * r['T'] / 100, 3)), ('adequado', D('0.510')))
chk('O2c contraprova com o V₂ de demonstração (60 %): NC', q((D(60) - r['V']) * r['T'] / 100, 3), D('1.020'))
# O3 · K do T2
k = an('LAU-2063', 'K')[0]; cl = classifica(K_ANU['>=4' if r['T'] >= 4 else '<4'], k)
chk('O3 LAU-2063 K 136,85 mg/dm³ · T 5,10 ≥ 4 → classe', (cl[0], COR[cl[1]]), ('alto', 'azul'))
# O4 · K do T1 e contraprova da classe demonstrativa
r1 = idx('LAU-2061'); k1 = an('LAU-2061', 'K')[0]
cl = classifica(K_ANU['>=4' if r1['T'] >= 4 else '<4'], k1)
indK = next(i for i in DS.IND if i['k'] == 'K'); demo = indK['classes'][sum(1 for c in indK['cortes'] if k1 >= D(c))]
chk('O4 LAU-2061 K 58,65 · T 7,50 → fonte "adequado" (verde); demonstração de hoje "médio"', (q(r1['T'], 2), cl[0], COR[cl[1]], demo), (D('7.50'), 'adequado', 'verde', 'médio'))
# O5 · P do T1: CER04 × SOJ20 × demonstração
p1 = an('LAU-2061', 'P')[0]; fx1 = faixa_argila(an('LAU-2061', 'Argila')[0])
indP = next(i for i in DS.IND if i['k'] == 'P'); demoP = indP['classes'][sum(1 for c in indP['cortes'] if p1 >= D(c))]
chk('O5 LAU-2061 P 18,5 · argila 40 → CER04 "alto" · SOJ20 "muito alto" · demonstração "adequado"', (fx1, classifica(P_SEQ[fx1], p1)[0], classifica(P_SOJ20_36_60, p1)[0], demoP), ('36-60', 'alto', 'muito alto', 'adequado'))
# O6 · V do T1 na faixa ideal [50; 60] (p. 84)
chk('O6 LAU-2061 SB 4,50 · V 60,0 → na faixa ideal 50–60 (limite superior incluso)', (q(r1['SB'], 2), q(r1['V'], 1), D(50) <= r1['V'] <= D(60)), (D('4.50'), D('60.0'), True))
# O7 · MO em unidade diferente
mo, mo_un, _ = an('LAU-2061', 'MO')
chk('O7 LAU-2061 MO 30 g/dm³ × fonte em % (Tab. 1) → sem classe', 'unidade diferente' if mo_un != '%' else 'classifica', 'unidade diferente')
# O8 · Fe sem linha na fonte
chk('O8 LAU-2061 Fe 35 mg/dm³ → sem referência (Anexo 6 não classifica Fe)', 'Fe' in ('B', 'Cu', 'Mn', 'Zn'), False)
# O9 · S pela média das duas camadas
s_med = (an('LAU-2043', 'S')[0] + an('LAU-2044', 'S')[0]) / 2
chk('O9 T4 S (9,0 + 14,0) ÷ 2 = 11,5 → "alto" (Tab. 11; sem ideal na fonte)', (s_med, classifica(S_CER04, s_med)), (D('11.5'), ('alto', None)))
# O10 · subsuperfície (20–40 cm)
r44 = idx('LAU-2044'); ca44 = an('LAU-2044', 'Ca')[0]
chk('O10 LAU-2044 (20–40) m = 100 × 0,10 ÷ 1,76 = 5,68 % → "baixa" · Ca 1,10 → Tab. 4 "adequado"', (q(r44['t'], 2), q(r44['m'], 2), classifica(M_CER04, r44['m'])[0], classifica(CA_SUB, ca44)[0]), (D('1.76'), D('5.68'), 'baixa', 'adequado'))
r72 = idx('LAU-2072')
chk('O10b LAU-2072 (Pivô 12, 20–40, mamão) m 50,85 % > 20 (limite do mamão, p. 354) · Ca 0,30 < 0,5', (q(r72['t'], 2), q(r72['m'], 2), r72['m'] > 20, an('LAU-2072', 'Ca')[0] < D('0.5')), (D('1.18'), D('50.85'), True, True))
# O11 · V do Pivô 12 (mamão) × alvo 50 % (p. 353) × demonstração 70 %
r71 = idx('LAU-2071')
chk('O11 LAU-2071 V = 4,05 ÷ 8,10 = 50,0 % → no alvo (NC 0); laboratório 49: difere (|1,0| > 0,5); demonstração 70 %: NC 1,620 t/ha',
    (q(r71['V'], 1), max(D(0), (D(50) - r71['V']) * r71['T'] / 100), abs(r71['V'] - D('49')) > D('0.5'), q((D(70) - r71['V']) * r71['T'] / 100, 3)), (D('50.0'), D('0'), True, D('1.620')))
# O12/O13 · K perenes (Tab. 5)
k71, a71 = an('LAU-2071', 'K')[0], an('LAU-2071', 'Argila')[0]; c71 = cond_k_per(r71['T'], a71)
chk('O12 LAU-2071 K 78,20 · T 8,10 · argila 28 → condição "alta" → "médio" (amarelo)', (c71, classifica(K_PER[c71], k71)[0]), ('alta', 'médio'))
r55 = idx('LAU-2055'); c55 = cond_k_per(r55['T'], an('LAU-2055', 'Argila')[0])
chk('O13 LAU-2055 K 110 · T 7,18 · argila 30 → "adequado"', (q(r55['T'], 2), c55, classifica(K_PER[c55], an('LAU-2055', 'K')[0])[0]), (D('7.18'), 'alta', 'adequado'))
chk('O13b condição ambígua: T 3,50 com argila 30 % (uma regra diz baixa, a outra alta)', cond_k_per(D('3.50'), D('30')), 'condição ambígua')
# O14 · P perenes (Tab. 3)
p71 = an('LAU-2071', 'P')[0]
chk('O14 LAU-2071 P 11,0 · argila 28 → perenes 16–35 → "médio"', (faixa_argila(a71), classifica(P_PER['16-35'], p71)[0]), ('16-35', 'médio'))
# O15 · vão entre classes escritas
chk('O15 K 25,5 mg/dm³ com T ≥ 4 (Tab. 12: "≤ 25" e "26 a 50") → entre classes', classifica(K_ANU['>=4'], D('25.5'))[0], 'entre classes')
# O16 · B 0,27: CER04 (vão 0,2–0,3) × SOJ20 Tab. 28
b71 = an('LAU-2071', 'B')[0]
chk('O16 B 0,27 → CER04 entre classes · SOJ20 baixo', (classifica(B_CER04, b71)[0], classifica(B_SOJ20, b71)[0]), ('entre classes', 'baixo'))
# O17 · validade de 24 meses (DEC-1610-04)
chk('O17 LAU-2021 (T3) coleta 10/08/2024 → validade 10/08/2026 < 23/09/2026 → vencido', (mais_meses('2024-08-10', 24), mais_meses('2024-08-10', 24) < HOJE), ('2026-08-10', True))
chk('O17b coleta 23/09/2024 → validade 23/09/2026 = hoje → ainda vale (vence só depois)', mais_meses('2024-09-23', 24) < HOJE, False)
# O18 · método diferente
p50 = an('LAU-2050', 'P')[0]
chk('O18 LAU-2050 (C1 café) P 22 resina × Tab. 3 de perenes (Mehlich-1) → método diferente', 'método diferente' if LAU['LAU-2050']['ext'] != 'Mehlich-1' else 'classifica', 'método diferente')
chk('O18b fixture: P 22 resina, anual, sequeiro (Tab. 8) → "alto"', classifica(P_RES_SEQ, p50)[0], 'alto')
# O19 · área fora do ideal pelo P (laudo composto do talhão; T4 é laudo de zona)
fora = []
for lid in ('LAU-2061', 'LAU-2063'):
    l = LAU[lid]; pv = an(lid, 'P')[0]; f = faixa_argila(an(lid, 'Argila')[0]); c = classifica(P_SEQ[f], pv)
    if c[1] != 'adequado': fora.append((l['tal'], D(str(l['area']))))
chk('O19 Santa Rita · P · fora do ideal: T1 (alto) + T2 (médio) = 610 ha; T4 fica "laudo de zona (Z2)"', (sorted(t for t, _ in fora), sum(a for _, a in fora), bool(LAU['LAU-2043']['zona'])), (['T1', 'T2'], D('610'), True))
# O20 · exemplo do registro (D-23) com V abaixo de 50 %
ca, mg, kk, hal = D('1.40'), D('0.60'), D('160.31'), D('3.50')
sb = ca + mg + cmolc_k(kk); T = sb + hal; V = 100 * sb / T
chk('O20 exemplo novo do T7: SB 2,41 · T 5,91 · V 40,78 % · NC (50 − V) × T ÷ 100 = 0,545 t/ha', (q(sb, 2), q(T, 2), q(V, 2), q((50 - V) * T / 100, 3)), (D('2.41'), D('5.91'), D('40.78'), D('0.545')))
sb0 = D('3.90') + D('1.30') + cmolc_k(D('160.31')); T0 = sb0 + D('2.89')
chk('O20b exemplo de hoje (V 66 %) com alvo 50 %: sem calagem (contraprova da jornada D-23)', (q(100 * sb0 / T0, 1), 100 * sb0 / T0 > 50), (D('66.0'), True))

# O21 · saturação por K na CTC (CER04 Tab. 13: baixa < 1 · média 1 a 2 · adequada 2 a 3 · alta > 3) — o "alvo 3 %" fixo do AG-03det não é a faixa da fonte
r43 = idx('LAU-2043'); satk = 100 * cmolc_k(an('LAU-2043', 'K')[0]) / r43['T']
SATK = [C('baixa', 'baixo', None, True, '1', False), C('média', 'médio', '1', True, '2', True), C('adequada', 'adequado', '2', False, '3', True), C('alta', 'alto', '3', False, None, True)]
chk('O21 LAU-2043 sat. K = 100 × 0,08 ÷ 9,20 = 0,87 % → "baixa" (adequada 2 a 3 %)', (q(r43['T'], 2), q(satk, 2), classifica(SATK, satk)[0]), (D('9.20'), D('0.87'), 'baixa'))
# O22 · relação Ca:Mg (CER04 Tab. 3, Obs.: estreita < 2 · adequada 2 a 10 · alta > 10, respeitado o mínimo de 0,5 cmolc/dm³ de Mg)
ca63, mg63 = an('LAU-2063', 'Ca')[0], an('LAU-2063', 'Mg')[0]
chk('O22 LAU-2063 Ca:Mg = 1,25 ÷ 0,44 = 2,84 → "adequada", mas Mg 0,44 < 0,5 (mínimo da mesma observação)', (q(ca63 / mg63, 2), D(2) <= ca63 / mg63 <= D(10), mg63 < D('0.5')), (D('2.84'), True, True))

# O23 · limites como escritos
chk('O23 P (argila 36–60): 12,0 → "adequado"; 12,05 → "alto"; 8,05 → entre classes (8,0 e 8,1)', (classifica(P_SEQ['36-60'], D('12.0'))[0], classifica(P_SEQ['36-60'], D('12.05'))[0], classifica(P_SEQ['36-60'], D('8.05'))[0]), ('adequado', 'alto', 'entre classes'))
chk('O23b V 60,5 → Tab. 9 entre classes (60 e 61) e acima do ideal 50–60 (p. 84)', (classifica(V_CLS, D('60.5'))[0], D('60.5') > D(60)), ('entre classes', True))
# O24 · sistema irrigado (CER04 Anexo 6 Tab. 7, p. 394) × sequeiro (Tab. 6), argila 16–35
P_IRR_16_35 = [C('muito baixo', 'muito baixo', '0', True, '10.0', True), C('baixo', 'baixo', '10.1', True, '15.0', True), C('médio', 'médio', '15.1', True, '20.0', True), C('adequado', 'adequado', '20.1', True, '30.0', True), C('alto', 'alto', '30.0', False, None, True)]
chk('O24 P 15,0 · argila 30: sequeiro "médio" × irrigado "baixo"; V₂ 50 % × 60 % (p. 84)', (classifica(P_SEQ['16-35'], D('15.0'))[0], classifica(P_IRR_16_35, D('15.0'))[0]), ('médio', 'baixo'))

print('\n== FOLHA (F2: SOJ20 Tab. 7 e CER04 cap. 10) ==')
FOLHA_SOJA = dict(N='47.0', P='2.6', K='15.0', Ca='7.0', Mg='2.6', S='2.5', B='35', Cu='8', Fe='120', Mn='60', Zn='28')   # LAU-2023 (sintético)
res = {a: classifica(SOJA_T7[a], D(v))[0] for a, v in FOLHA_SOJA.items()}
chk('F1 LAU-2023 soja · 3º trifólio sem pecíolo · R2 · K 15,0 g/kg × 18,0–25,0 → "baixo" (laranja)', (res['K'], COR[classifica(SOJA_T7['K'], D('15.0'))[1]]), ('baixo', 'laranja'))
chk('F1b fora da faixa primeiro: P, K, Mg, B, Mn e Zn baixos; N, Ca, S, Cu e Fe adequados', sorted(a for a, c in res.items() if c != 'adequado'), sorted(['P', 'K', 'Mg', 'B', 'Mn', 'Zn']))
chk('F1c K em % (1,50 dag/kg) × 10 = 15,0 g/kg → mesma classe', classifica(SOJA_T7['K'], D('1.50') * 10)[0], 'baixo')
chk('F2 o mesmo K com pecíolo: Tab. 7 não vale (órgão); CER04 Tab. 2 (3ª folha com pecíolo, florescimento) → abaixo da faixa 17–25', classifica(SOJA_COMPEC['K'], D('15.0'))[0], 'abaixo da faixa')
def epoca_soja(est, crescimento, veg=None):   # SOJ20 p. 148 (texto da amostragem); Tab. 7 na p. 149
    if est == 'R2': return 'na época'
    if est == 'R1' and crescimento == 'determinado': return 'na época'
    if est == 'R3 inicial' and crescimento == 'indeterminado' and veg in ('V8', 'V9', 'V10'): return 'na época'   # "podendo-se estender até o início do estádio R3, desde que as plantas estejam no estádio vegetativo V8/V10"
    return 'fora da época de referência'
chk('F3 estádios: R2 com crescimento não cadastrado → na época; R1 sem tipo → fora; V6 → fora', (epoca_soja('R2', None), epoca_soja('R1', None), epoca_soja('V6', None)), ('na época', 'fora da época de referência', 'fora da época de referência'))
FOLHA_CAFE = dict(N='28.4', P='1.1', K='16.0', Ca='12.0', Mg='3.2', S='1.7', B='45', Cu='12', Fe='110', Mn='80', Zn='8')   # LAU-2022 (sintético)
rc = {a: classifica(CAFE[a], D(v))[0] for a, v in FOLHA_CAFE.items()}
chk('F4 LAU-2022 café · 3º/4º par · 12/01/2026 (época dez–jan) → abaixo: P, K, Mg, B, Zn', sorted(a for a, c in rc.items() if c != 'na faixa'), sorted(['P', 'K', 'Mg', 'B', 'Zn']))
chk('F4b café coletado em 05/03/2026 → fora da época (dez–jan)', 'na época' if datetime.date(2026, 3, 5).month in (12, 1) else 'fora da época de referência', 'fora da época de referência')
FOLHA_MAMAO = dict(N='14.0', P='2.0', K='30.0', Ca='18.0', Mg='4.5', S='4.2')   # LAU-2025 (sintético; pecíolo 17ª–20ª folha com flor na axila)
rm = {a: classifica(MAMAO_PEC[a], D(v))[0] for a, v in FOLHA_MAMAO.items()}
chk('F5 LAU-2025 mamão Pivô 2 · pecíolo → abaixo: P e K; micronutrientes: sem referência na fonte', sorted(a for a, c in rm.items() if c != 'na faixa'), ['K', 'P'])
chk('F5b leitura cruzada Pivô 2: K do solo (LAU-2055) adequado × K da folha abaixo — só leitura', (classifica(K_PER[c55], an('LAU-2055', 'K')[0])[0], rm['K']), ('adequado', 'abaixo da faixa'))
# F6 · K baixo no solo e abaixo na folha (Pivô 6, laudos sintéticos novos LAU-2026 solo e LAU-2027 folha)
T6 = D('3.00') + D('1.00') + cmolc_k(D('20')) + D('2.50'); c6 = cond_k_per(T6, D('30'))
chk('F6 Pivô 6: solo K 20 mg/dm³ (T 6,55; argila 30) → "baixo"; folha K 28 g/kg → abaixo de 35–50', (q(T6, 2), classifica(K_PER[c6], D('20'))[0], classifica(MAMAO_PEC['K'], D('28'))[0]), (D('6.55'), 'baixo', 'abaixo da faixa'))
# F7 · validade da folha: na safra e no estádio da coleta (DEC-0910-13 b)
chk('F7 LAU-2023 coletado em 18/12/2025 é da safra 2025/26 (encerrada): leitura histórica, não vale para 2026/27', '2025-10-12' <= '2025-12-18' < '2026-09-23', True)
# F8 · LAU-2048 (feijão, P1): K sem unidade e estádio R5 × época "florescimento"
chk('F8 LAU-2048 K 17,4 sem unidade → inconsistente, sem classe', an('LAU-2048', 'K')[1] == '', True)

print('\n== R2 (revisão do Codex, comentário 6221505413) ==')
# R2-4 · validade com 29/02: último dia válido do mês de chegada
chk('V1 coleta 29/02/2024 + 24 meses → validade 28/02/2026 (último dia válido)', mais_meses('2024-02-29', 24), '2026-02-28')
chk('V1b em 28/02/2026 ainda vale; em 01/03/2026 vencido (vencido = validade < hoje)', ('2026-02-28' < '2026-02-28', '2026-02-28' < '2026-03-01'), (False, True))
js = datetime.date(2026, 2, 1) + datetime.timedelta(days=29 - 1)   # Date.setUTCMonth do solo.js:25 transborda o dia 29 para março
chk('V1c contraprova: a conta de hoje (solo.js:25) dá 01/03/2026, um dia a mais (executada também no node)', js.isoformat(), '2026-03-01')

# R2-1 · regime hídrico explícito do cultivo (e da zona), nunca deduzido do setor da Irrigação
P_SEQ_16_35 = P_SEQ['16-35']
def diag_regime(regime, p, v, T, k):
    """regime: 'sequeiro' | 'irrigado' | 'não declarado' | 'dois regimes' (laudo composto sobre zonas de regimes diferentes).
    Só o P (Tab. 6 × Tab. 7) e o alvo V₂ (p. 84: 50 × 60 %) dependem do regime; o K (Tab. 12) não."""
    kcls = classifica(K_ANU['>=4' if T >= 4 else '<4'], k)[0]
    if regime == 'sequeiro':
        return (classifica(P_SEQ_16_35, p)[0], q(max(D(0), (D(50) - v) * T / 100), 3), kcls)
    if regime == 'irrigado':
        return (classifica(P_IRR_16_35, p)[0], q(max(D(0), (D(60) - v) * T / 100), 3), kcls)
    motivo = 'regime não declarado' if regime == 'não declarado' else 'laudo composto cobre dois regimes'
    return (motivo, motivo, kcls)
Pf, Vf, Tf, Kf = D('15.0'), D('45'), D('6.00'), D('60')   # fixture: argila 30 %, V 45 %, T 6,00, K 60 mg/dm³
chk('G1 sequeiro declarado: P "médio" (Tab. 6) · NC (50 − 45) × 6,00 ÷ 100 = 0,300 · K "adequado"', diag_regime('sequeiro', Pf, Vf, Tf, Kf), ('médio', D('0.300'), 'adequado'))
chk('G2 irrigado declarado: P "baixo" (Tab. 7) · NC (60 − 45) × 6,00 ÷ 100 = 0,900 · K igual', diag_regime('irrigado', Pf, Vf, Tf, Kf), ('baixo', D('0.900'), 'adequado'))
chk('G3 regime não declarado (com ou sem setor): P e alvo suspensos; K continua classificado', diag_regime('não declarado', Pf, Vf, Tf, Kf), ('regime não declarado', 'regime não declarado', 'adequado'))
chk('G4 importado sem setor, irrigado declarado → vale o declarado (o aviso do setor não muda a conta)', diag_regime('irrigado', Pf, Vf, Tf, Kf)[:2], ('baixo', D('0.900')))
chk('G5 infraestrutura sem uso: setor de pivô cadastrado, sequeiro declarado nesta safra → tabelas de sequeiro', diag_regime('sequeiro', Pf, Vf, Tf, Kf)[:2], ('médio', D('0.300')))
chk('G6 cobertura parcial: laudo composto sobre 60 ha irrigados + 40 ha de sequeiro → P e alvo suspensos; laudo da zona irrigada → "baixo"',
    (diag_regime('dois regimes', Pf, Vf, Tf, Kf)[:2], diag_regime('irrigado', Pf, Vf, Tf, Kf)[0]), (('laudo composto cobre dois regimes', 'laudo composto cobre dois regimes'), 'baixo'))
chk('G7 safra alterada, o mesmo laudo: P1 soja 2026/27 sequeiro → (médio, 0,300); P1 feijão safrinha 2027 irrigado → (baixo, 0,900)',
    (diag_regime('sequeiro', Pf, Vf, Tf, Kf)[:2], diag_regime('irrigado', Pf, Vf, Tf, Kf)[:2]), (('médio', D('0.300')), ('baixo', D('0.900'))))

# R2-2 · café sem linha conferida: nada de alvo novo pela demonstração
ALVO_CONFERIDO = {'Soja': D(50), 'Milho': D(50), 'Feijão': D(50), 'Mamão Formosa': D(50)}   # sequeiro: CER04 p. 84; mamão: p. 353
def alvo_v2(cultura):
    return ALVO_CONFERIDO.get(cultura, 'sem referência adotada')
chk('C1 café: alvo de V sem linha conferida → "sem referência adotada", sem NC; contraprova: a demonstração (60 %) daria 0,900 t/ha',
    (alvo_v2('Café'), q((D(60) - Vf) * Tf / 100, 3)), ('sem referência adotada', D('0.900')))

# R2-5 · época da soja de crescimento indeterminado (SOJ20 p. 148)
chk('E1 indeterminado: R3 inicial com V8/V10 → na época; R3 inicial sem V8/V10 → fora; determinado em R3 inicial → fora; determinado em R1 → na época',
    (epoca_soja('R3 inicial', 'indeterminado', 'V9'), epoca_soja('R3 inicial', 'indeterminado', 'V6'), epoca_soja('R3 inicial', 'determinado', 'V9'), epoca_soja('R1', 'determinado')),
    ('na época', 'fora da época de referência', 'fora da época de referência', 'na época'))

print('\nResumo:', len(OK), 'OK ·', len(FAIL), 'falhas')
sys.exit(1 if FAIL else 0)
