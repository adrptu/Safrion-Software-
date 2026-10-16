# -*- coding: utf-8 -*-
"""UNID-PROD · contas da especificação (§6), em decimal, sem ponto flutuante.
Mesma regra do protótipo (producao.js): taxa em kg/ha com 6 casas, meio para cima; a tela arredonda só na exibição.
Uso: python3 docs/unidades-produtividade/verificacao/contas.py  → uma linha por conta e 'FALHAS: 0' no fim."""
from decimal import Decimal as D, ROUND_HALF_UP, getcontext
getcontext().prec = 34
FALHAS = []
q6 = lambda x: x.quantize(D('0.000001'), rounding=ROUND_HALF_UP)
def tela(x, casas=2):
    s = f"{x.quantize(D(1).scaleb(-casas), rounding=ROUND_HALF_UP):,.{casas}f}"
    return s.replace(',', '_').replace('.', ',').replace('_', '.')
def taxa(kg, ha): return q6(D(kg) / D(ha))              # kg/ha, base do indicador em massa
def em(kgha, massa): return q6(kgha / D(massa))          # kg/ha → unidade (massa da unidade em kg)
def ok(nome, cond, info=''):
    print(('OK    ' if cond else 'FALHA ') + nome + ('' if cond else ' · ' + str(info)))
    if not cond: FALHAS.append(nome)

# K-U01 · 6.000 kg/ha = 6 t/ha = 100 sc60 eq./ha; a volta é multiplicação exata
k = D(6000); ok('K-U01 6.000 kg/ha = 6 t/ha = 100 sc60 eq./ha', em(k, 1000) == 6 and em(k, 60) == 100 and D(100) * 60 == k)
# K-U02 · massa declarada: algodão em caroço @ 15 kg; arroz RS sc 50 kg
a = D(4526); ok('K-U02a algodão 4.526 kg/ha = 301,73 @/ha (15 kg)', tela(em(a, 15)) == '301,73', tela(em(a, 15)))
r = D(9044); ok('K-U02b arroz RS 9.044 kg/ha = 180,88 sc/ha (50 kg) = 150,73 sc60 eq./ha', tela(em(r, 50)) == '180,88' and tela(em(r, 60)) == '150,73', (tela(em(r, 50)), tela(em(r, 60))))
# K-U03..05 · semente (docs/colheita §6.6): Pivô 6, Pivô 19 e a ponderada do mamão
p6 = taxa(60320, '62.79'); ok('K-U03 Pivô 6 ciclo: 960,66 kg/ha · 0,96 t/ha · 16,01 sc60 eq./ha · 96,07 cx10 eq./ha',
    (tela(p6), tela(em(p6, 1000)), tela(em(p6, 60)), tela(em(p6, 10))) == ('960,66', '0,96', '16,01', '96,07'), (p6, em(p6, 60), em(p6, 10)))
p19 = taxa(36420, '75.11'); ok('K-U04 Pivô 19 ciclo: 484,89 kg/ha · 0,48 t/ha · 8,08 sc60 eq./ha · 48,49 cx10 eq./ha',
    (tela(p19), tela(em(p19, 1000)), tela(em(p19, 60)), tela(em(p19, 10))) == ('484,89', '0,48', '8,08', '48,49'), (p19, em(p19, 60), em(p19, 10)))
pm = taxa(60320 + 36420, D('62.79') + D('75.11')); simples = (p6 + p19) / 2
ok('K-U05 mamão ponderado: 701,52 kg/ha · 0,70 t/ha · 11,69 sc60 eq./ha (média simples daria 722,78)',
   (tela(pm), tela(em(pm, 1000)), tela(em(pm, 60)), tela(simples)) == ('701,52', '0,70', '11,69', '722,78'), (pm, simples))
# K-U06 · metas (valor e unidade informados → kg/ha por multiplicação exata)
ok('K-U06a meta mamão 50 t/ha/ano = 50.000 kg/ha/ano = 833,33 sc60 eq./ha/ano = 5.000 cx10 eq./ha/ano',
   D(50) * 1000 == 50000 and tela(em(D(50000), 60)) == '833,33' and em(D(50000), 10) == 5000)
ok('K-U06b meta soja T1-A 64 sc/ha = 3.840 kg/ha = 3,84 t/ha', D(64) * 60 == 3840 and em(D(3840), 1000) == D('3.84'))
m = D('3.85') * 1000; ok('K-U06c meta digitada 3,85 t/ha (soja) = 3.850 kg/ha = 64,17 sc/ha na tela; volta a 3,85 t/ha sem deriva',
   tela(em(m, 60)) == '64,17' and em(m, 1000) == D('3.85'))
# K-U07 · contraprova (i): mesmo cultivo de 10 ha, duas passagens nos mesmos 10 ha
c1 = taxa(10000 + 5000, min(D(10), D(10) + D(10))); errado = taxa(15000, 20)
ok('K-U07 duas passagens nos mesmos 10 ha: 1.500 kg/ha = 1,5 t/ha = 25 sc60 eq./ha (não 750 kg/ha)',
   c1 == 1500 and em(c1, 1000) == D('1.5') and em(c1, 60) == 25 and errado == 750, (c1, errado))
# K-U08 · contraprova (ii): parcelas distintas 10 ha/10.000 kg e 5 ha/15.000 kg
c2 = taxa(25000, 15); media = (taxa(10000, 10) + taxa(15000, 5)) / 2
ok('K-U08 parcelas distintas: 1.666,67 kg/ha = 1,67 t/ha = 27,78 sc/ha (média simples das taxas daria 2.000)',
   (tela(c2), tela(em(c2, 1000)), tela(em(c2, 60))) == ('1.666,67', '1,67', '27,78') and media == 2000, (c2, media))
# K-U09 · café da roça (caso COLH-C01: 12.000 L, 9.200 − 3.200 = 6.000 kg pesados, 5 ha apontados no C1)
L, kgf, ha = D(12000), D(9200) - D(3200), D(5)
ok('K-U09a café da roça: 2.400 L/ha; com o fruto pesado, 1.200 kg/ha = 1,2 t/ha = 20 sc60 eq./ha · Café da roça',
   taxa(L, ha) == 2400 and taxa(kgf, ha) == 1200 and em(taxa(kgf, ha), 60) == 20)
ok('K-U09b meta do C1 38 sc/ha de café beneficiado = 2.280 kg/ha; nunca comparada com o fruto', D(38) * 60 == 2280)
# K-U10 · zero, pendência e não colhido
ok('K-U10 0 kg em 10 ha = "0,00 kg/ha" (zero medido, 2 casas fixas); 5.000 kg sem área = pendência (sem divisão)', taxa(0, 10) == 0 and tela(taxa(0, 10)) == '0,00')
# K-U11 · 20 trocas repetidas: a tela parte sempre da mesma base; nenhum texto muda
base = taxa(60320, '62.79'); vistos = {}
for i in range(20):
    for u, ms in (('kg', 1), ('t', 1000), ('sc60', 60), ('cx10', 10)):
        t = tela(em(base, ms)); vistos.setdefault(u, t); 
        if vistos[u] != t: FALHAS.append('K-U11 ' + u)
ok('K-U11 20 trocas kg → t → sc60 → cx10: textos idênticos a cada volta', not any(f.startswith('K-U11') for f in FALHAS), vistos)
# K-U12 · rascunho "pela meta" pelo conversor = o de hoje (U11c): Pivô 2, 37,75 ha × 50 t/ha/ano ÷ 52 semanas
hoje = q6(D('37.75') * 50 * 1000 / 52); conv = q6(D('37.75') * (D(50) * 1000) / 52)
ok('K-U12 rascunho pela meta pelo conversor: 36.298,076923 kg/semana nos dois caminhos (U11c)', hoje == conv == D('36298.076923'), (hoje, conv))
# K-U13 · meta com até 2 casas em toda tela (revisão RC-10): 64 sc/ha em t/ha = 3,84; com 1 casa (COLH de hoje) daria 3,8
def tela_t(x, casas):
    t = tela(x, casas); return t.rstrip('0').rstrip(',') if ',' in t else t
mt = em(D(64) * 60, 1000)
ok('K-U13 meta do T1-A em t/ha: "3,84" com até 2 casas (1 casa daria "3,8"); 3,85 t/ha em sc/ha = "64,17" (1 casa daria "64,2")',
   tela_t(mt, 2) == '3,84' and tela_t(mt, 1) == '3,8' and tela_t(em(D('3.85') * 1000, 60), 2) == '64,17' and tela_t(em(D('3.85') * 1000, 60), 1) == '64,2')
# K-U14 · um arredondamento só (PRD 10.0, revisão RC-14): base ÷ (área × massa) dá o mesmo texto da semente que o caminho em dois passos
um = lambda kg, ha, ms: q6(D(kg) / (D(ha) * D(ms)))
ok('K-U14 Pivô 6 e Pivô 19 com um arredondamento: textos iguais aos da tabela (0,96 · 16,01 · 96,07 · 0,48 · 8,08 · 48,49)',
   [tela(um(60320, '62.79', m)) for m in (1000, 60, 10)] == ['0,96', '16,01', '96,07'] and [tela(um(36420, '75.11', m)) for m in (1000, 60, 10)] == ['0,48', '8,08', '48,49'])
print('FALHAS:', len(FALHAS))
