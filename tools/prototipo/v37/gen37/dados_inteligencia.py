# -*- coding: utf-8 -*-
"""INTEL-01 · dados da Inteligência de compras (o que inteligencia.js lê e não muda). Fonte única por fato:
- itens, referência e quantidade da safra: dados2.demanda('S2627') (o mesmo preço de referência do Planejar safra e da Compra);
- cotações: dados2.PROPOSTAS (fator sobre a referência, prazo, frete e pagamento por fornecedor homologado do grupo);
- pedidos: processo_compras.PED_2526 (safra anterior) e dados2.PEDIDOS (em curso);
- área: dados2.CULTIVOS da safra.
O histórico de preço pago dos últimos 18 meses e a pontualidade das entregas não existem na semente: HIST_SINT é sintético,
determinístico e rotulado na tela ("histórico sintético"). Nenhum dado real. Decimal em texto (ENG-013)."""
import json
from decimal import Decimal, ROUND_HALF_UP

SAFRA = 'S2627'


def _d(x, casas='0.0001'):
    return '{:f}'.format(Decimal(str(x)).quantize(Decimal(casas), rounding=ROUND_HALF_UP).normalize())   # texto fixo, nunca '6.1E+2'


# histórico sintético: (item, data, fornecedor, fator sobre a referência, prazo combinado em dias, atraso na entrega em dias)
HIST_SINT = [
    ('Glifosato 480', '2025-04-10', 'F04', '0.94', 10, 0), ('Glifosato 480', '2025-10-02', 'F03', '0.97', 10, 4),
    ('2,4-D 806', '2025-04-10', 'F04', '0.96', 10, 0), ('2,4-D 806', '2025-10-02', 'F03', '1.02', 12, 2),
    ('Óleo mineral', '2025-09-15', 'F04', '0.95', 7, 0),
    ('Fungicida TS', '2025-08-20', 'F07', '1.04', 15, 6), ('Fungicida A', '2025-11-05', 'F03', '0.99', 12, 0),
    ('Inoculante líquido', '2025-09-01', 'F05', '0.98', 8, 0),
    ('MAP 11-52', '2025-03-12', 'F02', '0.93', 15, 1), ('KCl 60%', '2025-03-12', 'F01', '0.95', 12, 0),
    ('Semente de soja 58 W', '2025-08-25', 'F05', '0.97', 20, 3),
]


def dados():
    import dados2 as D2
    from areas import processo_compras as PC
    dem = D2.demanda(SAFRA)
    itens = [dict(nome=n, grupo=o['grupo'], un=o['un'], ref=_d(o['preco']), qtd=_d(o['bruta'], '0.01'))
             for n, o in sorted(dem.items(), key=lambda kv: (kv[1]['grupo'], kv[0])) if o['bruta'] > 0.001 and o['preco']]
    fn = {f['id']: f['nome'] for f in D2.FORNECEDORES}
    cot, prz = {}, {}
    for i in itens:
        for p in D2.PROPOSTAS.get(i['grupo'], []):
            cot.setdefault(i['nome'], []).append(dict(f=p['f'], nome=fn.get(p['f'], p['f']), preco=_d(Decimal(i['ref']) * Decimal(str(p['fator']))),
                                                      prazo=p['prazo'], frete=p['frete'], pag=p['pag'], validade=p['validade']))
            prz.setdefault(p['f'], []).append(p['prazo'])
    hist = []
    for item, d, f, fat, pz, atr in HIST_SINT:
        ref = next((i['ref'] for i in itens if i['nome'] == item), None)
        if ref is None: continue
        hist.append(dict(item=item, d=d, f=f, nome=fn.get(f, f), preco=_d(Decimal(ref) * Decimal(fat)), prazo=pz, atraso=atr, entregue=True, orig='histórico sintético'))
    for p in PC.PED_2526:   # safra anterior: entregue no prazo combinado (a semente não registra atraso)
        hist.append(dict(item=p['item'], d=p['previsao'], f=p['f'], nome=fn.get(p['f'], p['f']), preco=_d(p['preco']), prazo=None, atraso=0, entregue=True, orig=p['id']))
    for p in D2.PEDIDOS:     # em curso: preço vale; entrega ainda não conta na pontualidade
        dd, mm, aa = p['previsao'].split('/')
        hist.append(dict(item=p['item'], d=f'{aa}-{mm}-{dd}', f=p['f'], nome=fn.get(p['f'], p['f']), preco=_d(p['preco']), prazo=None, atraso=0, entregue=False, orig=p['id']))
    area = sum(c['area'] for c in D2.CULTIVOS.get(SAFRA, []))
    forn = [dict(id=k, nome=v, prazo=(round(sum(prz[k]) / len(prz[k]), 1) if prz.get(k) else None)) for k, v in fn.items()]
    return dict(safra=SAFRA, area=_d(area, '0.01'), itens=itens, cot=cot, hist=hist, forn=forn)


def js():
    return 'const INTC = ' + json.dumps(dados(), ensure_ascii=False) + ';\n'
