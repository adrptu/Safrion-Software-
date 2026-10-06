# -*- coding: utf-8 -*-
"""Produção · colheita de ponta a ponta (docs/colheita/ESPECIFICACAO.md v1.1; decisões D-01..D-25 em docs/colheita/DECISOES.md).

catalogo(): o que as regras de producao.js leem e não mudam (PRDC): unidade de mercado por cultura (dados_cad.CULTURA_UN, fonte
única), cultivos das safras abertas (área, meta, cultura, fazenda), O.S. de colheita da semente → cultivo, locais com tipo (R-10),
local de recebimento por fazenda e cultura, obrigações físicas da soja 26/27 do VE-05 (areas/comercial.py, D-19) e quem age (D-14).
seed(): c.producao da demonstração (§6): contagem, versões publicadas, cargas, lotes, pedidos, reserva, movimentos e sequências.
Os números valem na camada sintética (dados_lagoa_fonte.REAL = False); os testes rodam com SAFRION_DADOS=sintetico.
Dados sintéticos: nenhuma pessoa, cliente ou número real (a Lagoa Grande é sintética fora do Mac)."""
import json, os, re, datetime as dt
HERE = os.path.dirname(os.path.abspath(__file__))
import dados_cad as DC

HOJE = '2026-09-26'          # CEN_DIA_OP (cenario.js): data dos registros novos (D-25)
FRUTA = dict(plantas_ha=1700, perda='0.05')   # D-10: plantas vivas por ha e perda (sintéticos, editáveis ao publicar)
PROC = ('Packing', 'Terreiro', 'Secador')      # R-10: local de processo → lote Em processo
REC_LOCAL = {'Lagoa Grande': {'*': 'l11'},
             'Santa Rita': {'Mamão Formosa': 'l8', 'Soja': 'l6', 'Milho': 'l6', 'Feijão': 'l6', 'Café': 'l7', '*': 'l7'},
             'Boa Vista': {'*': 'l9'}}
QUEM = dict(ag='Ana (agrônoma)', gestor='Ana (gestora)', qual='Qualidade (Marta)', com='Comercial', colh='Sérgio',
            rec={'Lagoa Grande': 'Lúcia', 'Santa Rita': 'Rui (almoxarife)', 'Boa Vista': 'Rui (almoxarife)'})
SEMANAL = ('Mamão Formosa',)   # colheita por passe semanal (perene de fruta): uma O.S. por cultivo e semana (R-18)


def _mf(nome):
    m = re.search(r'\d{4}/\d{2}', nome)
    return m.group(0) if m and not nome.startswith('Safrinha') else nome.replace('Safra ', '')


def _em_producao(c):
    """perene de fruta colhe a partir de 240 dias do plantio (o mesmo critério de 'continua' do motor de carência)."""
    if c['cultura'] not in SEMANAL or not c.get('plantio'): return c['cultura'] not in SEMANAL
    return (dt.date.fromisoformat(HOJE) - dt.date.fromisoformat(c['plantio'])).days >= 240


def catalogo():
    import dados2 as D2, dados as D
    safras = {s['id']: dict(id=s['id'], nome=s['nome'], faz=s.get('fazenda', 'Santa Rita'), ini=s['ini'], fim=s['fim'], mf=_mf(s['nome']))
              for s in D2.SAFRAS if not s['ro']}
    cult, de = {}, {}
    for sid in safras:
        for c in D2.CULTIVOS.get(sid, []):
            cult[c['id']] = dict(id=c['id'], saf=sid, faz=safras[sid]['faz'], local=c['local'], cultura=c['cultura'], var=c.get('variedade', ''),
                                 area=c['area'], meta=c.get('meta'), un_meta=c.get('un_meta', ''), plano=c.get('plano'), plantio=c.get('plantio'),
                                 colheita=c.get('colheita'), semanal=c['cultura'] in SEMANAL, prod=_em_producao(c))
            de.setdefault(c['local'], []).append(c['id'])
    oscult = {}
    for o in D.ORDENS + D.ORDENS_LG:
        if not str(o['tipo']).startswith('Colheita'): continue
        sid = next((k for k, s in safras.items() if s['faz'] == o['faz'] and s['mf'] == o['saf']), None)
        cid = next((k for k in de.get(o['talhao'], []) if cult[k]['saf'] == sid), None)
        if cid: oscult[o['id']] = cid
    locais = {i: dict(id=i, nome=n, faz=f, tipo=t) for i, n, f, t, *_ in DC.LOCAIS}
    from areas import comercial as CM   # obrigações físicas da soja 26/27 (VE-05; D-19: sc de 60 kg)
    obrig = [dict(id='CT-203', tipo='Contrato', sc=CM.CT203, cont='Coop Grão Sul'), dict(id=CM.CPR['id'], tipo='CPR', sc=CM.CPR['sc'], cont=CM.CPR['contraparte']),
             dict(id=CM.BT['id'], tipo='Barter', sc=CM.BT['sc'], cont='Fornecedor de insumos')]
    return dict(un=DC.CULTURA_UN, safras=safras, cult=cult, cultDe=de, osCult=oscult, locais=locais, recLocal=REC_LOCAL, proc=list(PROC),
                fruta=FRUTA, quem=QUEM, obrig=[dict(x, prod='Soja em grão', cultura='Soja', saf='2026/27') for x in obrig],
                dest={'MI-BR': 'Mercado interno · Brasil'})


def seed():
    """Semente §6 (contas em docs/colheita/verificacao/contas.py). Quantidades em kg."""
    import dados2 as D2
    TARA = 7200; LG = 'Lagoa Grande'; L11 = 'l11'
    cargas, lotes, movs = {}, {}, []
    def mp(tipo, lote, kg, d, **x):
        m = dict(id='MP-%d' % (1001 + len(movs)), tipo=tipo, lote=lote, kg=kg, d=d, at=x.pop('at', '07:00'), **x); movs.append(m); return m
    REC = [('CG-2101', 'TK-4471', '2026-09-16', '09:20', 'OS-0510', 'lg06', 'Pivô 6', 15280, 'L38-131'),
           ('CG-2102', 'TK-4472', '2026-09-16', '11:05', 'OS-0510', 'lg06', 'Pivô 6', 15210, 'L38-131'),
           ('CG-2103', 'TK-4478', '2026-09-18', '09:30', 'OS-0510', 'lg06', 'Pivô 6', 14960, 'L38-132'),
           ('CG-2104', 'TK-4479', '2026-09-18', '11:10', 'OS-0510', 'lg06', 'Pivô 6', 14870, 'L38-132'),
           ('CG-2105', 'TK-4490', '2026-09-21', '09:40', 'OS-0505', 'lg19', 'Pivô 19', 12180, 'L39-131'),
           ('CG-2106', 'TK-4491', '2026-09-21', '11:20', 'OS-0505', 'lg19', 'Pivô 19', 11940, 'L39-131'),
           ('CG-2107', 'TK-4502', '2026-09-22', '10:15', 'OS-0505', 'lg19', 'Pivô 19', 12300, 'L39-132')]
    for cg, tk, d, h, os_, cid, tal, liq, lid in REC:
        o = dict(os=os_, cult=cid, tal=tal, pct=100, modo='medida', kg=liq, com=liq)
        cargas[cg] = dict(id=cg, ticket=tk, faz=LG, cultura='Mamão Formosa', os=os_, dcol=d, drec=d, hora=h, bruto=liq + TARA, tara=TARA, liq=liq, com=liq,
                          u=None, impG=None, litros=None, frutos=None, cond='Íntegra', local=L11, st='Recebida', lote=lid, origem=[o], quem='Lúcia',
                          veic='Carreta 02', chave='SEM-' + cg, sinc=True, via='web')
        L = lotes.setdefault(lid, dict(id=lid, prod='Mamão Formosa · fruta de campo', cultura='Mamão Formosa', classe='', saf='2026/27', faz=LG, local=L11,
                                       drec=d, dcol=d, validade=(dt.date.fromisoformat(d) + dt.timedelta(days=7)).isoformat(), q0='Liberado', cond='Íntegra',
                                       origem=[], cargas=[]))
        L['origem'].append(dict(carga=cg, os=os_, cult=cid, tal=tal, dcol=d, kg=liq, modo='medida')); L['cargas'].append(cg)
        mp('recebimento', lid, liq, d, at=h, carga=cg, quem='Lúcia')
    # CG-2108: do app, sem ticket, a pesar (estimativa 590 caixas: estimativa nunca soma, R-03)
    cargas['CG-2108'] = dict(id='CG-2108', ticket='', faz=LG, cultura='Mamão Formosa', os='OS-0505', dcol='2026-09-22', drec=None, hora='15:40', bruto=None, tara=None,
                             liq=None, com=None, u=None, impG=None, litros=None, frutos=None, cond='', local=L11, st='A pesar', lote='', est_cx=590, est_kg=None,
                             origem=[dict(os='OS-0505', cult='lg19', tal='Pivô 19', pct=100, modo='medida')], quem='Marcos', veic='Carreta 02',
                             chave='APP-CG-2108', sinc=True, via='app')
    # L38-131 expedido ao PV-037 (Frutas Real, entregue 17/09): físico 0, rastreio fica
    mp('expedição', 'L38-131', -30490, '2026-09-17', at='08:30', pedido='PV-037', quem='Comercial')
    # L10-031: saldo de abertura da soja 2025/26 (sem talhão, D-17): 2.305.200 kg = 38.420 sc
    lotes['L10-031'] = dict(id='L10-031', prod='Soja em grão', cultura='Soja', classe='Padrão', saf='2025/26', faz='Santa Rita', local='l6', drec='2026-03-05',
                            dcol=None, validade=None, q0='Liberado', cond='Íntegra', origem=[], cargas=[], abertura=True)
    mp('abertura', 'L10-031', 2305200, '2026-03-05', at='18:00', quem='Rui (almoxarife)', obs='Saldo de abertura da safra 2025/26 (anterior ao sistema)')
    reservas = {'RS-0001': dict(id='RS-0001', pedido='PV-030', lote='L10-031', kg=232500, st='Ativa', d='2026-09-20', at='10:12', quem='Comercial', chave='SEM-RS-0001')}
    mp('reserva', 'L10-031', 232500, '2026-09-20', at='10:12', fis=False, reserva='RS-0001', pedido='PV-030', quem='Comercial')
    pedidos = {
        'PV-030': dict(id='PV-030', cliente='Coop Grão Sul', prod='Soja em grão', cultura='Soja', classe='Padrão', saf='2025/26', tipo='pronta', janela='set–out/26',
                       qtd=240000, dest='MI-BR', ref='CT-201', obs='saldo 4.000 sc do CT-201 (8.000 sc já expedidos)'),
        'PV-036': dict(id='PV-036', cliente='Frutas Real', prod='Mamão Formosa · fruta de campo', cultura='Mamão Formosa', classe='', saf='', tipo='pronta',
                       janela='24–26/09', qtd=10000, dest='MI-BR'),
        'PV-037': dict(id='PV-037', cliente='Frutas Real', prod='Mamão Formosa · fruta de campo', cultura='Mamão Formosa', classe='', saf='', tipo='pronta',
                       janela='16–17/09', qtd=30490, dest='MI-BR', obs='entregue em 17/09 (L38-131)'),
        'PV-038': dict(id='PV-038', cliente='Frutas Real', prod='Mamão Formosa · fruta de campo', cultura='Mamão Formosa', classe='', saf='', tipo='futura',
                       janela='S41 (05–11/10)', sem='2026-W41', qtd=30000, dest='MI-BR'),
    }
    contagens = [dict(id='CNT-0001', cult='lg19', tal='Pivô 19', d='2026-09-23', at='07:40', quem='Sérgio', plantas=20, pintado=11, devez=10, verde=12,
                      peso='1.20', chave='SEM-CNT-0001', sinc=True, via='app')]
    soja = {c['id']: c for c in D2.CULTIVOS['S2627'] if c['cultura'] == 'Soja'}
    previsoes = {'lg06': [dict(v=1, d='2026-09-09', por=QUEM['ag'], base='contagem', sem={'2026-W38': 62000})],
                 'lg19': [dict(v=1, d='2026-09-16', por=QUEM['ag'], base='contagem', sem={'2026-W39': 72900})]}
    for cid, c in soja.items():
        previsoes[cid] = [dict(v=1, d='2026-09-15', por=QUEM['ag'], base='meta', safra=c['area'] * c['meta'] * 60)]
    return dict(contagens=contagens, previsoes=previsoes, cargas=cargas, lotes=lotes, pedidos=pedidos, reservas=reservas, movs=movs,
                seq=dict(cg=2108, lote={'38': 132, '39': 132}, rs=1, mp=1000 + len(movs), cnt=1))


def js_regras():
    """PRDC + producao.js (regras e comandos pr*): entra em cenario.js_prefixo() depois de cenario.js (D-22)."""
    return ('const PRDC = ' + json.dumps(catalogo(), ensure_ascii=False).replace('</', '<\\/') + ';\n'
            + open(os.path.join(HERE, 'producao.js'), encoding='utf-8').read() + '\n')


if __name__ == '__main__':
    s = seed(); print(len(s['cargas']), 'cargas ·', len(s['lotes']), 'lotes ·', len(s['movs']), 'movimentos · seq', s['seq'])
    k = catalogo(); print(len(k['cult']), 'cultivos ·', k['osCult'], '· obrigações', [(o['id'], o['sc']) for o in k['obrig']])
