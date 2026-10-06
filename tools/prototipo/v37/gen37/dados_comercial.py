# -*- coding: utf-8 -*-
"""Comercial e logística (docs/comercial/ESPECIFICACAO.md v1.1; decisões D-C01..D-C25 em docs/comercial/DECISOES.md).

catalogo(): o que as regras de comercial.js leem e não mudam (COMC): contrapartes do CD-05 (cad_parceiros._parceiros(), sem
cadastro paralelo, D-C20) com papéis, condição de pagamento, limite e validade do crédito, texto de entrega e produtos; tipos de
veículo com capacidade lida do nome (D-C17); condições de pagamento; referência de mercado e frete sintéticos (ex-VE-02 e ex-LO-04,
sem tela própria, D-C05).
completar(seed): a semente comercial sobre c.producao da Colheita (§6.2-§6.3): preço, natureza, condição, modalidade e janela das
vendas da Colheita (PV-030, PV-036..038); CT-203, CRE-0095 e BT-090 como vendas futuras (D-C04); RM-0001 = a saída histórica do
L38-131 ao PV-037 (MP-1008), sem pesagem inventada (D-C19); sequências de RM, PV e CT (D-C18).
Dados sintéticos: nenhuma pessoa, cliente ou número real (a Lagoa Grande é sintética). Decimal: preços em texto."""
import json, os, re
HERE = os.path.dirname(os.path.abspath(__file__))

# referência de mercado sintética (D-1), dos valores do VE-02 oculto; o CEPEA cota soja em R$/sc 60 kg (D-19 da Colheita, CE-16)
REF = {'Soja em grão': dict(p='129.40', fonte='CEPEA/Esalq · Paraná · 22/09 (sintético, ex-VE-02)'),
       'Milho em grão': dict(p='61.80', fonte='CEPEA/Esalq · Campinas · 22/09 (sintético, ex-VE-02)'),
       'Mamão Formosa · fruta de campo': dict(p='3.10', fonte='CEAGESP · São Paulo · 22/09 (sintético, ex-VE-02)'),
       'Feijão em grão': None}   # sem cotação: ausente ≠ zero
# frete de referência sintético (ex-LO-04): só ajuda no "Programar carga"; contratar e medir frete fica fora (§9)
FRETE = {'Rota Sul Transportes': 'R$ 190/t · Sede → Vitória/ES (contrato vigente, sintético)',
         'Frota própria': 'R$ 4,10/km · custo interno (sintético)',
         'TransVale Transportes': 'sem cotação registrada'}


def _cond_dias(t):
    if t.startswith('À vista'): return 0
    m = re.match(r'(\d+) dias após a entrega', t)
    return int(m.group(1)) if m else None


def catalogo():
    from areas import cad_parceiros as CP
    cp = {}
    for p in CP._parceiros():
        papeis = list(p.get('papeis') or [])
        if not set(papeis) & {'Cliente', 'Fornecedor', 'Transportador'}: continue
        veic = p.get('veic') or []
        if isinstance(veic, str): veic = [v.strip() for v in veic.split(';') if v.strip()]
        cp[p['nome']] = dict(id=p['id'], nome=p['nome'], papeis=papeis, cond=p.get('pag') or '', lim=p.get('lim') or None, limv=p.get('limv') or '',
                             entrega=p.get('entrega') or '', prod=list(p.get('prod') or []), veic=[v for v in veic if v in CP.VEICULOS])
    veic = []
    for t in CP.VEICULOS:
        m = re.search(r'(\d+) t', t)
        veic.append(dict(t=t, cap=int(m.group(1)) * 1000, tipo='refrigerado' if 'refrigerado' in t.lower() else 'graneleiro'))
    cond = [dict(t=t, dias=_cond_dias(t), ant=(t == 'Antecipado')) for t in CP.COND_PAG]
    return dict(cp=cp, veic=veic, cond=cond, ref=REF, frete=FRETE, dest={'MI-BR': 'Mercado interno · Brasil'},
                motivos=['Maturação avançada', 'Avaria no transporte', 'Fora do padrão contratado', 'Quantidade a mais'])


def completar(seed):
    """Semente §6.2-§6.3 (contas em docs/comercial/verificacao/contas.py). Quantidades na base (kg); preço por unidade comercial."""
    from areas import comercial as CM
    P = seed
    ped = P['pedidos']
    QUEM = 'Dora (comercial)'
    com = {
        'PV-030': dict(preco='128.00', natureza='Venda', cond='À vista na entrega', modal='retira', local='Armazém Sede (FOB)', ini='2026-09-01', fim='2026-10-31'),
        'PV-036': dict(preco='3.05', natureza='Venda', cond='28 dias após a entrega comprovada', modal='entrega', local='CD Frutas Real · Vitória/ES', ini='2026-09-24', fim='2026-09-26'),
        'PV-037': dict(preco='3.00', natureza='Venda', cond='28 dias após a entrega comprovada', modal='entrega', local='CD Frutas Real · Vitória/ES', ini='2026-09-16', fim='2026-09-17'),
        'PV-038': dict(preco='3.10', natureza='Venda', cond='28 dias após a entrega comprovada', modal='entrega', local='CD Frutas Real · Vitória/ES', ini='2026-10-05', fim='2026-10-11'),
    }
    for k, x in com.items():
        ped[k].update(x, d='2026-09-15', at='09:00', quem=QUEM, chave='SEM-' + k, imp='')
    soja = dict(prod='Soja em grão', cultura='Soja', classe='Padrão', saf='2026/27', tipo='futura', janela='safra 2026/27', dest='MI-BR', ini='', fim='',
                d='2026-09-15', at='09:00', quem=QUEM, imp='')
    ped['CT-203'] = dict(soja, id='CT-203', cliente='Coop Grão Sul', qtd=CM.CT203 * 60, preco='132.00', natureza='Venda', cond='À vista na entrega',
                         modal='retira', local='Armazém Sede (FOB)', chave='SEM-CT-203')
    ped['CRE-0095'] = dict(soja, id='CRE-0095', cliente=CM.CPR['contraparte'], qtd=CM.CPR['sc'] * 60, preco='118.84', natureza='CPR', cond='Liquidação em produto',
                           modal='retira', local='Armazém Sede (FOB)', chave='SEM-CRE-0095', obs='R$ 820.000 em defensivos · equivalente R$ 118,84/sc (GE-08)')
    ped['BT-090'] = dict(soja, id='BT-090', cliente='Fertisul', qtd=CM.BT['sc'] * 60, preco='%.2f' % CM.BT['eq'], natureza='Barter', cond='Liquidação em produto',
                         modal='retira', local='Armazém Sede (FOB)', chave='SEM-BT-090', obs='barter de insumos 26/27 (GE-08)')
    for r in P['reservas'].values():
        r.setdefault('kg0', r['kg']); r.setdefault('exp', 0)
    mv = next(m for m in P['movs'] if m['tipo'] == 'expedição' and m['pedido'] == 'PV-037')   # MP-1008
    mv['rm'] = 'RM-0001'
    P['expedicoes'] = {'RM-0001': dict(id='RM-0001', pedido='PV-037', lotes=[dict(lote=mv['lote'], prev=-mv['kg'], kg=-mv['kg'])], modal='entrega',
                                       local='CD Frutas Real · Vitória/ES', transp='Rota Sul Transportes', veic='Baú refrigerado 12 t', placa='', dprev=mv['d'],
                                       st='Entregue', saida=dict(bruto=None, tara=None, liq=-mv['kg'], d=mv['d'], at=mv['at'], quem=mv['quem'], chave='SEM-RM-0001', imp='',
                                                                 aval=[], cred=None, exc=None),
                                       entrega=dict(d=mv['d'], at='', quem=mv['quem'], comp='registro da Colheita (MP-1008)', chave='SEM-ENT-RM-0001', imp=''),
                                       devs=[], canc=None, d=mv['d'], at=mv['at'], quem=mv['quem'], chave='SEM-RM-0001', imp='', hist=True)}
    P['seq'].update(rm=1, pv=38, ct=204)
    return P


def js_regras():
    """COMC + comercial.js (regras e comandos com*): só nas três telas do grupo Comercial (D-C15), depois de cenario.js_prefixo() e do núcleo da carência."""
    return ('const COMC = ' + json.dumps(catalogo(), ensure_ascii=False).replace('</', '<\\/') + ';\n'
            + open(os.path.join(HERE, 'comercial.js'), encoding='utf-8').read() + '\n')


if __name__ == '__main__':
    import sys; sys.path.insert(0, HERE)
    k = catalogo(); print(len(k['cp']), 'contrapartes ·', [v['t'] for v in k['veic']])
