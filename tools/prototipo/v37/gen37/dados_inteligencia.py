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


# ---------------------------------------------------------------------------------------------------------------------
# INTEL-02 · preços, tendência e melhor mês (pedido do proprietário, 13/10/2026: "inteligência de compras e vendas é mais
# relativo aos preços, tendências, melhor mês para compra e venda"). A semente não tem histórico de preço de mercado:
# SÉRIE SINTÉTICA de 60 meses, determinística e rotulada na tela, com o último mês igual à referência atual (vendas:
# dados_comercial.REF; compras: preço de referência da safra). Forma: sazonalidade típica do produto ou grupo × tendência
# anual × movimento dos últimos 4 meses × ruído de ±1%. No software real a série vem de fonte pública (CEPEA/Esalq,
# CONAB, CEAGESP) e das compras da fazenda; nada aqui é cotação real.
# ---------------------------------------------------------------------------------------------------------------------
import hashlib
from datetime import date, timedelta
MESES = [f'{2021 + (9 + i) // 12}-{(9 + i) % 12 + 1:02d}' for i in range(60)]          # 2021-10 … 2026-09 (mês da demonstração)
HOJE = '2026-09-26'                                                                       # CEN_DIA_OP
# desvio sazonal por mês (jan … dez) sobre a média do ano, tendência anual e movimento recente (4 meses) — todos sintéticos
SAZ = {
    'Soja em grão':                   ('-0.03 -0.05 -0.07 -0.06 -0.03 0 0.02 0.04 0.05 0.06 0.05 0.02', '0.05', '0.08'),
    'Milho em grão':                  ('0.04 0.05 0.03 0 -0.03 -0.06 -0.08 -0.06 -0.02 0.02 0.05 0.06', '0.03', '-0.08'),
    'Mamão Formosa · fruta de campo': ('-0.08 -0.10 -0.06 -0.02 0.04 0.10 0.12 0.08 0.02 -0.03 -0.05 -0.07', '0.06', '-0.07'),
    'Fertilizantes': ('-0.05 -0.07 -0.06 -0.03 0 0.03 0.05 0.07 0.06 0.03 -0.01 -0.04', '-0.03', '0.09'),
    'Herbicidas':    ('-0.02 -0.04 -0.05 -0.04 -0.02 0 0.02 0.04 0.05 0.04 0.02 0', '0.02', '-0.07'),
    'Fungicidas':    ('-0.02 -0.04 -0.05 -0.04 -0.02 0 0.02 0.04 0.05 0.04 0.02 0', '0.02', '0'),
    'Inseticidas':   ('-0.02 -0.04 -0.05 -0.04 -0.02 0 0.02 0.04 0.05 0.04 0.02 0', '0.03', '0'),
    'Adjuvantes':    ('-0.01 -0.02 -0.03 -0.02 -0.01 0 0.01 0.02 0.03 0.02 0.01 0', '0.02', '0'),
    'Inoculantes':   ('-0.01 -0.02 -0.03 -0.02 -0.01 0 0.01 0.02 0.03 0.02 0.01 0', '0.02', '0'),
    'Sementes':      ('0 -0.02 -0.04 -0.05 -0.04 -0.02 0.01 0.04 0.06 0.05 0.02 0.01', '0.04', '0'),
}
UN_VENDA = {'Soja em grão': 'sc', 'Milho em grão': 'sc', 'Mamão Formosa · fruta de campo': 'kg'}
PERECIVEL = {'Mamão Formosa · fruta de campo'}   # não dá para estocar e esperar o mês bom: a sazonalidade orienta o plantio e a colheita
PRAZO_PADRAO = 15                                 # dias de entrega quando o insumo não tem cotação (sintético)


def _ruido(nome, mes):
    h = int(hashlib.md5((nome + '|' + mes).encode('utf-8')).hexdigest()[:8], 16)
    return (Decimal(h % 2001) - 1000) / Decimal(100000)                                   # −1% … +1%


def serie(nome, perfil, ancora):
    saz, tend, mov = perfil; sz = [Decimal(x) for x in saz.split()]; tend = Decimal(tend); mov = Decimal(mov)
    bruto = []
    for t, m in enumerate(MESES):
        k = 1 + tend * Decimal(t - 59) / 12                                               # tendência anual (último mês = 1)
        r = 1 + mov * Decimal(max(0, t - 55)) / 4                                         # movimento dos 4 últimos meses
        bruto.append(k * (1 + sz[int(m[5:]) - 1]) * r * (1 + _ruido(nome, m)))
    f = Decimal(str(ancora)) / bruto[-1]
    return [dict(m=m, p=_d(b * f, '0.01')) for m, b in zip(MESES, bruto)]


def precos():
    import dados_comercial as DC
    import dados2 as D2
    dem = D2.demanda(SAFRA); base = dados()
    vendas = []
    for prod, r in DC.REF.items():
        if not r: vendas.append(dict(prod=prod, un=None, fonte=None, serie=[])); continue   # sem cotação: sem série (ausente ≠ zero)
        vendas.append(dict(prod=prod, un=UN_VENDA[prod], fonte=r['fonte'], perecivel=prod in PERECIVEL, serie=serie(prod, SAZ[prod], r['p'])))
    compras = []
    for i in base['itens']:
        evs = sorted(e['dt'] for e in dem[i['nome']]['evs'] if e.get('tipo') == 'dem' and e['dt'] >= HOJE)
        prz = min((c['prazo'] for c in base['cot'].get(i['nome'], [])), default=PRAZO_PADRAO)   # o fornecedor mais rápido
        lim = (date.fromisoformat(evs[0]) - timedelta(days=prz)).isoformat() if evs else None   # último dia para pedir e receber a tempo
        compras.append(dict(nome=i['nome'], grupo=i['grupo'], un=i['un'], qtd=i['qtd'], nec=evs[0] if evs else None, prazo=prz, lim=lim,
                            serie=serie(i['nome'], SAZ[i['grupo']], i['ref'])))
    return dict(meses=MESES, hoje=HOJE, vendas=vendas, compras=compras,
                rotulo='série sintética de demonstração (60 meses); no software real: CEPEA/Esalq, CONAB, CEAGESP e as compras da fazenda')


def js():
    return 'const INTC = ' + json.dumps(dados(), ensure_ascii=False) + ';\n'


def js_precos():
    return 'const INTP = ' + json.dumps(precos(), ensure_ascii=False) + ';\n'
