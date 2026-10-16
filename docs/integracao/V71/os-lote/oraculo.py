"""OS-LOTE R1: oráculo de especificação sintética; NÃO executa produto/banco/UI.
Reprodução: python3 -I docs/integracao/V71/os-lote/oraculo.py
Só biblioteca padrão. Valores decimais textuais, nenhum dado real/prescrição.
"""
from decimal import Decimal as D
from datetime import date, timedelta
import json

cases = []


def check(case, actual, expected, meaning):
    if actual != expected:
        raise AssertionError((case, actual, expected))
    cases.append(dict(id=case, result=actual, expected=expected, meaning=meaning))


def quantity(area, dose):
    a, d = D(area), D(dose)
    if not a.is_finite() or not d.is_finite() or a <= 0 or d <= 0:
        raise ValueError('area/dose invalidas')
    return a * d


def unit(dose, name, basis='ha'):
    factors = {'L': ('L', D('1')), 'mL': ('L', D('0.001')),
               'kg': ('kg', D('1')), 'g': ('kg', D('0.001'))}
    u, f = factors[name]
    return u, basis, D(dose) * f


def loads(areas, dose, volume, capacity):
    dose, volume, capacity = map(D, (dose, volume, capacity))
    if min(dose, volume, capacity) <= 0:
        raise ValueError('parametro nao positivo')
    result, destinations, used = [], [], D('0')
    for field, area in areas:
        remaining = D(area)
        if remaining <= 0:
            raise ValueError('area nao positiva')
        while remaining:
            part = min(remaining, (capacity - used) / volume)
            destinations.append([field, part])
            used += part * volume
            remaining -= part
            if used == capacity:
                result.append(dict(volume=used, product=used / volume * dose,
                                   destinations=destinations))
                used, destinations = D('0'), []
    if used:
        result.append(dict(volume=used, product=used / volume * dose,
                           destinations=destinations))
    return result


def overlap(intervals):
    return max(x[0] for x in intervals), min(x[1] for x in intervals)


def collision(a, b):
    return a[0] < b[1] and b[0] < a[1]


def hours(area, effective_capacity, travel, setup):
    if effective_capacity is None:
        return None
    cap = D(effective_capacity)
    if cap <= 0:
        raise ValueError('capacidade nao positiva')
    return D(area) / cap + D(travel) + D(setup)


# Resultados esperados independentes, derivados no PRD41.10 e na memoria R1.
a, b = quantity('10', '2'), quantity('15', '2')
check('A3-total', a + b, D('50'), '25ha a2L/ha; nao somar doses')
check('A3-cargas', loads([('A', '10'), ('B', '15')], '2', '100', '2000'), [
    dict(volume=D('2000'), product=D('40'), destinations=[['A', D('10')], ['B', D('10')]]),
    dict(volume=D('500'), product=D('10'), destinations=[['B', D('5')]])],
    'Carga compartilhada e ultima parcial; volume final nao e agua a adicionar')
check('A3-horas', hours('30', '5', '0.5', '0.25'), D('6.75'), '6h trabalho +0.5deslocamento +0.25setup')
check('A3-ausencia', hours('30', None, '0.5', '0.25'), None, 'Ausente nao e zero')
check('A4-demanda', sum([a, b], D('0')), D('50'), 'Grupo coordena origens; nao tem demanda adicional')
check('A4-contraprova', a + b + (a + b) == D('50'), False, 'Somar origens e grupo reprova:100L')
check('A4-reserva', sum([D('0'), D('0')]), D('0'), 'Antes CMD06 nao criar reserva')
check('A6-parcial', {'area': D('10') + D('5'), 'consumo': quantity('15', '2'),
                   'saldo_area': D('25') - D('15'), 'saldo_teorico': D('50') - D('30')},
      {'area': D('15'), 'consumo': D('30'), 'saldo_area': D('10'), 'saldo_teorico': D('20')},
      'Saldo teorico nao comprova estoque livre/calda; nao encerra ordem')
check('B3-delta', quantity('30', '1.5') - quantity('30', '2'), D('-15'), '60L para45L')
check('B3-custo', {'antes': D('60') * D('20'), 'depois': D('45') * D('20'),
                 'delta': D('-15') * D('20'), 'ha_antes': D('1200') / D('30'),
                 'ha_depois': D('900') / D('30')},
      {'antes': D('1200'), 'depois': D('900'), 'delta': D('-300'), 'ha_antes': D('40'),
       'ha_depois': D('30')}, 'Preco sintetico20R$/L; estimativa nao custo realizado')
check('B5-cancelar', quantity('30', '2') - quantity('5', '2'), D('50'), 'Retirar so demanda5ha; sem devolucao ficticia')
check('B1-calendario', str(date(2026, 10, 30) + timedelta(days=7)), '2026-11-06', 'Dias civis atravessam mes; horarios/fuso no contrato real')
check('N1-unidades', unit('1', 'L') == unit('1000', 'mL'), True, 'Conversao exata equivalente')
check('N2-base', unit('1', 'L') == unit('1', 'L', '100L'), False, 'Base diferente')
check('N3-dimensao', unit('1', 'L') == unit('1', 'kg'), False, 'Massa nao e volume')
check('N4-precisao', unit('1.0004', 'L') == unit('1.0005', 'L'), False, 'Tela arredondada nao decide equivalencia')
windows = [(D('8'), D('10')), (D('9'), D('12')), (D('11'), D('13'))]
start, end = overlap(windows)
check('N5-janela-global', end > start, False, 'A cruzaB eB cruzaC; grupo sem intersecao')
start, end = overlap([(D('8'), D('15')), (D('9'), D('14'))])
check('N6-duracao', hours('30', '5', '0.5', '0.25') <= end - start, False, '6.75h nao cabem nas5h comuns')
check('N7-choque', collision((D('9'), D('12')), (D('11'), D('13'))), True, 'Conflito mesmo recurso, interno ou externo ao lote')
check('N8-limite', collision((D('9'), D('12')), (D('12'), D('13'))), False, 'Intervalos sem sobreposicao; deslocamento e setup devem estar incluidos')
check('N9-embalagem', quantity('3.3', '0.2'), D('0.66'), 'Nao arredondar para frasco1L')
for value in ('0', '-1', 'NaN', 'Infinity'):
    try:
        quantity('10', value)
    except ValueError:
        refused = True
    else:
        refused = False
    check('N10-dose-' + value, refused, True, 'Recusa aritmetica; insumo ausente nao vira dosezero')

print(json.dumps({'scope': 'oraculo de especificacao; nao produto, UI ou banco',
                  'cases': cases, 'passed': len(cases)}, ensure_ascii=False, indent=2,
                 default=lambda x: format(x, 'f') if isinstance(x, D) else x))
