# -*- coding: utf-8 -*-
"""Cenário inicial compartilhado (CEN0) para O.S., Estoque e App de campo, a partir dos registros canônicos.
Uso nas áreas: EXTRAJS[0] = cenario.js_prefixo() + <js da tela>; a tela chama cenOuvir(self) e lê cenGet()."""
import json, os
import dados2 as D2
import dados_lagoa_safra as DL
import quantidade as _QTD   # regra única de quantidade (SINT-C03)

HERE = os.path.dirname(os.path.abspath(__file__))
REQ_DA_OS = {'OS-0417': 'REQ-031', 'OS-0421': 'REQ-035', 'OS-0420': 'REQ-036', 'OS-0418': 'REQ-038', 'OS-0424': 'REQ-039', 'OS-0425': 'REQ-040'}
EMB = {'Fungicida A': 'galão 5 L', 'Glifosato 480': 'galão 20 L', '2,4-D 806': 'galão 20 L', 'Óleo mineral': 'galão 20 L', 'Adjuvante espalhante': 'galão 5 L',
       'NPK 20-05-20': 'big bag 1.000 kg', 'MAP 11-52': 'saco 50 kg', 'Semente de soja 58 W': 'saco 40 kg', 'Ureia 45%': 'saco 50 kg'}
EMB.update(DL.EMB)
REQ_DA_OS.update({oid: r[0] for oid, r in DL.REQS.items()})


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
    # numeração dos lotes automáticos da Santa Rita preservada; a Lagoa Grande tem numeração e almoxarifado próprios
    base = sorted((k, v) for k, v in D2.ESTOQUE.items() if k not in DL.ESTOQUE)
    for i, (item, q) in enumerate(base):
        if q <= 0 or item in lote_de: continue
        un = UN.get(item, 'L' if any(w in item for w in ('Fungicida', 'Inseticida', 'Acaricida', 'Adjuvante', 'Óleo', '2,4-D', 'Cletodim', 'Inoculante', 'Atrazina', 'Diquat')) else 'kg')
        cod = (''.join(w[0] for w in item.replace(',', ' ').split() if w[0].isalpha()) or ''.join(ch for ch in item if ch.isalpha()))[:2].upper() + f'26-{i + 1:02d}'
        local = 'Almox. defensivos' if un == 'L' else 'Galpão 1'
        lotes[item + '|' + cod] = dict(prod=item, lote=cod, local=local, un=un, fisico=q, quarentena=0, reservado=0, validade='12/2027')
        lote_de[item] = cod
    for i, (item, q) in enumerate(sorted(DL.ESTOQUE.items())):
        if q <= 0 or item in lote_de: continue
        un = UN.get(item, 'kg'); cod = f'LG26-{i + 1:02d}'
        lotes[item + '|' + cod] = dict(prod=item, lote=cod, local='Almox. Lagoa Grande', un=un, fisico=q, quarentena=0, reservado=0, validade='12/2027')
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
        ins = [dict(p=x['p'], dose=x['dose'], un=x['un'], tot=x['tot'], emb=EMB.get(x['p'], '')) for x in o.get('ins', [])]
        ordens[o['id']] = dict(id=o['id'], tipo=o['tipo'], talhao=o['talhao'], area=o.get('area') or 0, etapa=o['etapa'], versao=v,
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
    # Lagoa Grande: entregue e consumido pela fração de cada requisição; o que não foi entregue fica reservado no lote
    for oid, (rid, fe, fc) in DL.REQS.items():
        o = ordens.get(oid)
        if not o: continue
        itens = []
        for x in o['ins']:
            lt = lote_de.get(x['p'], '—'); key = x['p'] + '|' + lt; sol = x['tot']; ent = round(sol * fe, 3); con = _QTD.qtd(x['dose'], o['realizado']) if fc == 1.0 or abs(fc * o['area'] - o['realizado']) < 1e-6 else round(sol * fc, 3)
            if key in lotes and sol - ent > 0: lotes[key]['reservado'] += sol - ent
            itens.append(dict(prod=x['p'], lote=lt, un=x['un'], emb=x.get('emb', ''), solicitado=sol, entregue=ent, consumido=con, devolvido=0, custodia=round(ent - con, 3), confirmado=ent > 0))
        reqs[rid] = dict(id=rid, os=oid, estado=('Reservada' if fe == 0 else 'Entregue'), itens=itens)
    # v=2 (01/10, O.S. sem revisão): descarta o cenário salvo no navegador que ainda tinha aprov, selos de aprovação e recibo APV-
    # v=3 (04/10, SINT-C03 + PRE-REV-20261004): quantidades da semente pela regra única; o salvo com a regra antiga travaria o apontamento
    # v=4 (1a · PCMS-M01, PCM simplificado §7.2): a manutenção entra no cenário único (c.man, com achados, leituras e recibos); a
    # chave própria da manutenção sai. O.S., Estoque, App, CD-03 e a tela MA leem e gravam o mesmo estado.
    # v=4 (06/10, colheita de ponta a ponta · docs/colheita): o estado ganha c.producao (contagens, previsões, cargas, lotes de produto,
    # pedidos, reservas e movimentos MP-); o salvo sem ele é descartado (D-18)
    # v=5 (06/10, beneficiamento BEN-1 · docs/beneficiamento): ordens de processo OB-0110 e OB-0112 (fam BEN) em c.ordens, REQ-030 e o lote
    # de caixas CX26-01; no estado da Produção, os lotes do packing, o PV-031 e as inspeções (c.producao.ben); o salvo sem eles é descartado
    # v=5 (09/10, junção PCM × Colheita na frente PCM, D-53): c.man e c.producao juntos
    # v=5 (06/10, comercial e logística · docs/comercial): c.producao ganha vendas com preço e condição, CT-203/CRE-0095/BT-090 no estado,
    # cargas de saída (RM-) e sequências rm/pv/ct; o salvo da v=4 é descartado
    # v=6 (10/10, junção PCM × BEN-1 na branch única): as duas frentes subiram para v=5 com conteúdos diferentes (BEN-1: ordens OB-,
    # REQ-030, CX26-01 e c.producao.ben; PCM: c.man, app.usuario e app.manFila); o salvo v=5 de qualquer uma volta ao seed (cenGet)
    # v=7 (10/10, integração V56: Comercial × v=6 da branch única): o salvo v=5 do Comercial (sem c.man e sem o BEN) e o v=6 da branch (sem
    # as vendas do Comercial) voltam ao seed
    import dados_manutencao as DM
    import dados_producao, dados_ben, dados_comercial
    est = dict(v=7, rev=0, diaOperacional='-'.join(reversed(D2.HOJE.split('/'))), ordens=ordens, reqs=reqs, lotes=lotes, movs=[], ocorr=[],
               # S4 (PCM §3.7): usuario = Ver como do app (Marcos · Zé, simulação); manFila = comandos da manutenção feitos sem sinal
               app=dict(online=True, fila=[], turno=None, operador='Marcos', usuario='Marcos', manFila=[]),
               man=DM.seed(), producao=dados_producao.seed())
    est = dados_ben.semear(est)   # integração V56: o BEN semeia o packing (lotes, PV-031) e o Comercial completa as vendas depois, inclusive o PV-031
    est['producao'] = dados_comercial.completar(est['producao'])
    return est


# Validade mensal é inclusiva até o último dia; ausência aplicável (—) conserva o comportamento do cadastro.
# O físico permanece registrado mesmo vencido. Tela e motor usam a mesma comparação, sem relógio do navegador.
VALIDADE_JS = r"""
function cenLoteVencido(l, hoje) {
  const m = /^(\d{2})\/(\d{4})$/.exec(String((l || {}).validade || ''));
  if (!m) return false;
  return m[2] + '-' + m[1] < String(hoje || CEN_DIA_OP).slice(0, 7);
}
"""


def js_prefixo():
    import dados_producao   # regras da produção (producao.js) em toda página do estado (D-22): O.S., Mapa, Estoque e app têm prPodeEncerrar
    import dados_ben        # regras do beneficiamento (ben.js) depois: a qualidade do lote de produção e as decisões valem em toda página do estado
    # análise de solo (SOLO-01): só as funções de solo.js (regras e comandos sobre c.solo); os dados (SOLO0) entram só no AG-02 e no Planejar safra
    return ('const CEN0 = ' + json.dumps(seed(), ensure_ascii=False).replace('</', '<\\/') + ';\n' + VALIDADE_JS + open(os.path.join(HERE, 'cenario.js'), encoding='utf-8').read() + '\n'
            + dados_producao.js_regras() + dados_ben.js_regras() + open(os.path.join(HERE, 'solo.js'), encoding='utf-8').read() + '\n')


def perfis_js():
    """Bloco de perfis de demonstração do g2lib.js (G2_PERFIS, g2pf, g2perfil, g2papel, g2ator, g2quem, g2umPapel, g2quemUm, g2mesma), entre os marcadores
    <perfis> e </perfis>: as decisões do cenário (cenExige) o usam, e os testes sem navegador montam o motor com ele. As telas já o têm (G2LIB)."""
    s = open(os.path.join(HERE, 'g2lib.js'), encoding='utf-8').read()
    i = s.index('// <perfis>'); j = s.index('// </perfis>')
    return s[i:j] + '\n'


if __name__ == '__main__':
    import sys; sys.path.insert(0, HERE)
    s = seed()
    for k, o in s['ordens'].items(): print(k, o['etapa'], o['versao'], o['req'], o['realizado'], '/', o['area'], [i['p'] for i in o['ins']])
    for k, r in s['reqs'].items(): print(k, r['os'], r['estado'], [(i['prod'], i['lote'], i['solicitado'], i['entregue'], i['custodia']) for i in r['itens']])
