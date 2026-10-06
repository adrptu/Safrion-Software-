# -*- coding: utf-8 -*-
"""Contas da especificação da Colheita (docs/colheita/ESPECIFICACAO.md §6), em Decimal, 6 casas, meio para cima.
Uso: python3 docs/colheita/verificacao/contas.py  → imprime cada caso e 'FALHAS: 0' quando todos fecham."""
from decimal import Decimal as D, ROUND_HALF_UP, getcontext
import datetime as dt
getcontext().prec = 40
q6 = lambda x: D(x).quantize(D('0.000001'), ROUND_HALF_UP)
q2 = lambda x: D(x).quantize(D('0.01'), ROUND_HALF_UP)
F = []
def ok(nome, got, exp):
    s = 'ok' if got == exp else 'FALHA'
    if s == 'FALHA': F.append(nome)
    print(f'{s:5} {nome}: {got} (esperado {exp})')

def corrigir(liq, u, imp, up, ip):          # R-08: impureza acima do padrão, depois umidade sobre o limpo; sem bônus abaixo do padrão
    liq, u, imp, up, ip = map(D, (liq, u, imp, up, ip))
    limpo = q6(liq * (1 - max(D(0), imp - ip) / 100))
    com = q6(limpo * (100 - u) / (100 - up)) if u > up else limpo
    return limpo, com

# K01 a K03 · grão
l, c = corrigir(30000, '16.5', '2.0', 14, 1); ok('K01 soja limpo', l, D('29700.000000')); ok('K01 soja comercial', c, D('28836.627907')); ok('K01 sc 60', q2(c / 60), D('480.61'))
l, c = corrigir(30000, '13.0', '0.8', 14, 1); ok('K02 sem bônus abaixo do padrão', c, D('30000.000000'))
l, c = corrigir(28000, '15.2', '1.4', 14, '0.5'); ok('K03 feijão comercial', c, D('27360.818605')); ok('K03 sc 60', q2(c / 60), D('456.01'))
# K04 · mistura 60/40 de 10.001 kg: o primeiro arredonda, o último leva o resto
a = q6(D(10001) * D('0.60')); ok('K04 parte 60 %', a, D('6000.600000')); ok('K04 parte 40 %', D(10001) - a, D('4000.400000'))
# K05 a K07 · mamão Lagoa Grande (cargas do §6.4)
P6 = [15280, 15210, 14960, 14870]; P19 = [12180, 11940, 12300]
ok('K05 Pivô 6 produção kg', sum(P6), 60320); ok('K05 Pivô 6 t/ha', q2(D(sum(P6)) / 1000 / D('62.79')), D('0.96'))
ok('K05 Pivô 6 desvio da previsão %', q2((D(sum(P6)) - 62000) / 62000 * 100), D('-2.71'))
ok('K05 Pivô 6 ciclo t/ha (área do cultivo)', q2(D(sum(P6)) / 1000 / D('62.79')), D('0.96'))
# v1.1: passe = realizado da O.S.; ciclo perene = área do cultivo (R-02, D-11)
ok('K06 Pivô 19 passe S39 parcial t/ha', q2(D(sum(P19)) / 1000 / 50), D('0.73'))
ok('K06 Pivô 19 passe com CG-2108 (12.050 kg)', q2(D(sum(P19) + 12050) / 1000 / 50), D('0.97'))
ok('K06 Pivô 19 ciclo t/ha', q2(D(sum(P19)) / 1000 / D('75.11')), D('0.48'))
ok('K06 Pivô 19 ciclo com CG-2108', q2(D(sum(P19) + 12050) / 1000 / D('75.11')), D('0.65'))
ok('K07 cultura ponderada no ciclo t/ha', q2(D(60320 + 36420) / 1000 / (D('62.79') + D('75.11'))), D('0.70'))
ok('K07 média simples (errada)', q2((D(60320) / 1000 / D('62.79') + D(36420) / 1000 / D('75.11')) / 2), D('0.72'))
# K08 · previsão pela contagem: área × plantas vivas/ha × frutos do estádio ÷ plantas da amostra × peso médio × (1 − perda)
prev = lambda a, st, fr, n, p, pe: q6(D(a) * st * fr / n * D(p) * (1 - D(pe)))
ok('K08 Pivô 19 S40 kg', prev('75.11', 1700, 10, 20, '1.20', '0.05'), D('72781.590000'))
ok('K08 Pivô 19 S41 kg', prev('75.11', 1700, 12, 20, '1.20', '0.05'), D('87337.908000'))
ok('K08 Pivô 6 S39 kg', prev('62.79', 1700, 10, 20, '1.20', '0.05'), D('60843.510000'))
ok('K09 pela meta Pivô 2 kg/semana', q6(D('37.75') * 50 * 1000 / 52), D('36298.076923'))
# K10 · soja: estoque físico × venda futura
ok('K10 L10-031 sc', D(2305200) / 60, D(38420)); ok('K10 RS-0001 sc', D(232500) / 60, D(3875)); ok('K10 disponível sc', (D(2305200) - D(232500)) / 60, D(34545))
soja = [(160, 64), (152, 62), (298, 63), (204, 60), (96, 62), (95, 66), (80, 66)]
of = sum(a * m for a, m in soja); ok('K10 oferta soja 26/27 sc', of, 68180)
FIS = 12000 + 6900 + 1000   # VE-05: CT-203 + CPR CRE-0095 + barter BT-090 (areas/comercial.py:31-36), sc 60 kg (D-19)
ok('K10 obrigações físicas soja 26/27 sc', FIS, 19900); ok('K10 oferta livre soja 26/27 sc', of - FIS, 48280)
ok('K10 PV-030 falta depois da RS-0001 kg', 4000 * 60 - 232500, 7500)
# K11 · unidades de mercado (DEC-0510-03)
ok('K11 laranja cx', D(24480) / D('40.8'), D(600)); ok('K11 laranja cx/ha em 2 ha', D(24480) / D('40.8') / 2, D(300)); ok('K11 laranja t/ha', D(24480) / 1000 / 2, D('12.24'))
ok('K11 coco mil frutos/ha', D(12500) / D('1.25') / 1000, D(10)); ok('K11 arroz RS sc 50', D(9044) / 50, D('180.88'))
# K12 · semana ISO do lote
for d, w in (('2026-09-16', 38), ('2026-09-22', 39), ('2026-03-05', 10), ('2026-09-26', 39)): ok('K12 semana ' + d, dt.date.fromisoformat(d).isocalendar()[1], w)
# K13 · tarefa do proprietário (§8.1): apontar 25 ha na OS-0505, pesar a CG-2108, reservar para o PV-036
ok('K13 passe S39 depois de apontar 25 ha', q2(D(sum(P19)) / 1000 / 75), D('0.49'))
ok('K13 CG-2108 líquido', D(19250) - 7200, D(12050))
ok('K13 passe S39 depois de pesar a CG-2108', q2(D(sum(P19) + 12050) / 1000 / 75), D('0.65'))
ok('K13 validade L39-133 (colheita 22/09 + 7 d)', (dt.date(2026, 9, 22) + dt.timedelta(days=7)).isoformat(), '2026-09-29')
res = min(D(12050), D(10000)); ok('K13 reserva sugerida kg', res, D(10000)); ok('K13 L39-133 disponível kg', D(12050) - res, D(2050))
ok('K13 mamão Em processo na semente kg (L38-132, L39-131, L39-132 pelo CAR0)', 29830 + 24120 + 12300, 66250)
ok('K13 PV-037 expedido kg (só L38-131)', 15280 + 15210, 30490)
# K14 · oferta livre da S41 (PV-038 futura 30.000 kg)
ok('K14 S41 sem versão publicada (déficit) kg', 0 - 30000, -30000); ok('K14 S41 com a v2 kg', D('87337.908') - 30000, D('57337.908'))
# K15 · contraexemplo da área do ciclo: passes parciais alternados (S38 31 ha, S39 31,79 ha na outra metade) com 30.000 kg cada
ok('K15 maior passe como área (errado) t/ha', q2(D(60000) / 1000 / D('31.79')), D('1.89'))
ok('K15 área do cultivo t/ha', q2(D(60000) / 1000 / D('62.79')), D('0.96'))
print('FALHAS:', len(F), F if F else '')
