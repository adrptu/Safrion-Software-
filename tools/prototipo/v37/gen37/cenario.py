# -*- coding: utf-8 -*-
"""Cenário inicial compartilhado (CEN0) para O.S., Estoque e App de campo, a partir dos registros canônicos.
Uso nas áreas: EXTRAJS[0] = cenario.js_prefixo() + <js da tela>; a tela chama cenOuvir(self) e lê cenGet()."""
import json, os
import dados2 as D2

HERE = os.path.dirname(os.path.abspath(__file__))
REQ_DA_OS = {'OS-0417': 'REQ-031', 'OS-0421': 'REQ-035', 'OS-0420': 'REQ-036', 'OS-0418': 'REQ-038', 'OS-0424': 'REQ-039', 'OS-0425': 'REQ-040'}
EMB = {'Fungicida A': 'galão 5 L', 'Glifosato 480': 'galão 20 L', '2,4-D 806': 'galão 20 L', 'Óleo mineral': 'galão 20 L', 'Adjuvante espalhante': 'galão 5 L',
       'NPK 20-05-20': 'big bag 1.000 kg', 'MAP 11-52': 'saco 50 kg', 'Semente de soja 58 W': 'saco 40 kg', 'Ureia 45%': 'saco 50 kg'}


def seed():
    import areas.processo_os as P
    ords = P._ordens()
    lotes = {}
    for l in D2.LOTES:
        lotes[l['item'] + '|' + l['lote']] = dict(prod=l['item'], lote=l['lote'], local=l['local'], un=l['un'], fisico=l['fisico'],
                                                   quarentena=l['quarentena'], reservado=0, validade=l['validade'])
    lote_de = {}
    for k, l in lotes.items(): lote_de.setdefault(l['prod'], l['lote'])
    # saldos do estoque sem lote registrado ganham um lote com o mesmo total (entrega e devolução são por lote)
    UN = {x['prod']: x['un'] for p in D2.PLANOS for a in p['atividades'] for x in a['prods']}
    for i, (item, q) in enumerate(sorted(D2.ESTOQUE.items())):
        if q <= 0 or item in lote_de: continue
        un = UN.get(item, 'L' if any(w in item for w in ('Fungicida', 'Inseticida', 'Acaricida', 'Adjuvante', 'Óleo', '2,4-D', 'Cletodim', 'Inoculante', 'Atrazina', 'Diquat')) else 'kg')
        cod = (''.join(w[0] for w in item.replace(',', ' ').split() if w[0].isalpha()) or ''.join(ch for ch in item if ch.isalpha()))[:2].upper() + f'26-{i + 1:02d}'
        local = 'Almox. defensivos' if un == 'L' else 'Galpão 1'
        lotes[item + '|' + cod] = dict(prod=item, lote=cod, local=local, un=un, fisico=q, quarentena=0, reservado=0, validade='12/2027')
        lote_de[item] = cod
    reqs = {}
    for r in D2.REQUISICOES:
        un = r['un']; lt = lote_de.get(r['item'], '—'); f = 1
        if un.startswith('sc '): f = int(un.split()[1]); un = 'kg'   # mesma unidade do lote (sacos viram kg)
        reqs[r['id']] = dict(id=r['id'], os=r['os'], estado=r['estado'], itens=[dict(prod=r['item'], lote=lt, un=un, emb=EMB.get(r['item'], ''), solicitado=r['solicitado'] * f,
                              entregue=r['entregue'] * f, consumido=r['consumido'] * f, devolvido=r['dev_recebida'] * f, custodia=r['custodia'] * f, confirmado=r['custodia'] > 0)])
    ordens = {}
    for o in ords:
        v = str(o.get('versao', ''))
        aprov = ('aprovada' in v) and ('em revisão' not in v.split('·')[-1] or o['id'] == 'OS-0420')
        ins = [dict(p=x['p'], dose=x['dose'], un=x['un'], tot=x['tot'], emb=EMB.get(x['p'], '')) for x in o.get('ins', [])]
        ordens[o['id']] = dict(id=o['id'], tipo=o['tipo'], talhao=o['talhao'], area=o.get('area') or 0, etapa=o['etapa'], versao=v, aprov=aprov,
                               realizado=o.get('realizado') or 0, saldo=o.get('saldo') if o.get('saldo') is not None else (o.get('area') or 0),
                               resp=o['resp'], ins=ins, req=REQ_DA_OS.get(o['id']), selos=o.get('selos', []),
                               ap=[dict(d=a['d'], dia=a['dia'], ha=a['ha'], st=a['st'], sinc=True, origem='web') for a in o.get('ap', [])],
                               reservado=o['id'] in REQ_DA_OS and o['etapa'] != 'A liberar')
    # reservas vigentes (liberadas e ainda não entregues): REQ-039 da OS-0424 e REQ-040 da OS-0425
    for oid, rid in (('OS-0424', 'REQ-039'), ('OS-0425', 'REQ-040')):
        o = ordens.get(oid)
        if not o or rid in reqs: continue
        itens = []
        for x in o['ins']:
            lt = lote_de.get(x['p'], '—'); key = x['p'] + '|' + lt
            res = 65 if rid == 'REQ-039' else min(x['tot'], lotes[key]['fisico'] - lotes[key]['quarentena'] if key in lotes else 0)
            if key in lotes: lotes[key]['reservado'] += res
            itens.append(dict(prod=x['p'], lote=lt, un=x['un'], emb=x.get('emb', ''), solicitado=res, entregue=0, consumido=0, devolvido=0, custodia=0, confirmado=False))
        reqs[rid] = dict(id=rid, os=oid, estado='Reservada', itens=itens)
    return dict(v=1, rev=0, ordens=ordens, reqs=reqs, lotes=lotes, movs=[], ocorr=[],
                app=dict(online=True, fila=[], turno=None, operador='Marcos'))


def js_prefixo():
    return 'const CEN0 = ' + json.dumps(seed(), ensure_ascii=False).replace('</', '<\\/') + ';\n' + open(os.path.join(HERE, 'cenario.js'), encoding='utf-8').read() + '\n'


if __name__ == '__main__':
    import sys; sys.path.insert(0, HERE)
    s = seed()
    for k, o in s['ordens'].items(): print(k, o['etapa'], 'aprov' if o['aprov'] else '-', o['req'], o['realizado'], '/', o['area'], [i['p'] for i in o['ins']])
    for k, r in s['reqs'].items(): print(k, r['os'], r['estado'], [(i['prod'], i['lote'], i['solicitado'], i['entregue'], i['custodia']) for i in r['itens']])
