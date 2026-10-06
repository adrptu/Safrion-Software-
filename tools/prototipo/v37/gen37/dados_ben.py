# -*- coding: utf-8 -*-
"""Beneficiamento · BEN-1 packing de mamão (docs/beneficiamento/ESPECIFICACAO.md v2; adaptações à base com Colheita em
docs/beneficiamento/DECISOES.md §12).

catalogo(): BENC, o que as regras de ben.js leem e não mudam: versões de rota (dado estático até o editor, BEN-6), caixa do packing
com massa declarada e tara (fonte única: dados_cad.EMB_PACK, DEC-0510-03), ativo do packing (CD-03) e condição da Manutenção na
semente (dados_manutencao; a tela lê o estado da Manutenção quando existe). A rota é por cultura, produto e estágio: grão (SEC-GRA) e
café (CAF-BEN) já são dados com o bloco em que entram, mas só a PACK-FRU v3 está aprovada no BEN-1.
semear(est): grava no estado do cenário (cenario.seed) as ordens OB-0110 e OB-0112 (c.ordens, fam 'BEN': reaproveitam cenLiberar,
cenEntregar, cenDevolver e cenPodeEncerrar), a REQ-030 das caixas, o lote de caixas CX26-01 (c.lotes) e, no estado da Produção
(c.producao, o mesmo modelo de lote, movimento MP-, pedido e reserva da Colheita), os lotes do packing, o PV-031 e as inspeções.
Dados sintéticos (ENG-017): pessoas, clientes e números fictícios."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
import dados_cad as DC

CX = DC.CX_MAMAO
CXD = DC.EMB_PACK[CX]
EMB_CX = 'pallet de entrega de 60 caixas vazias'
LOCAL = 'l8'   # Packing (Santa Rita), tipo Packing (colheita D-24)
QUEM_PROD = 'Igor (responsável de produção)'
QUEM_QUAL = 'Marta (qualidade)'
MANGO = 'Mamão Formosa · fruta de campo'
EMBAL = 'Mamão Formosa · fruta embalada'

PACK3 = dict(id='PACK-FRU', v=3, nome='packing de mamão', estado='Aprovada', aprov=dict(quem='Igor', em='2026-09-10'), bloco='BEN-1', seg='Frutas/HF', cultura='Mamão Formosa',
             ent=MANGO, est_ent='Fruta de campo',
             saidas=[dict(fluxo='Produto', prod=EMBAL, est='Fruta embalada', classes=['A', 'B'], caixa=True),
                     dict(fluxo='Outro destino', destinos=['Indústria']),
                     dict(fluxo='Descarte', destinos=['Compostagem']),
                     dict(fluxo='Perda identificada', causas=['Avaria no manuseio'])],
             etapas=[dict(nome='Recepção', pert='Exigida'), dict(nome='Lavagem', pert='Não se aplica', mot='a PACK-FRU v3 não lava'),
                     dict(nome='Triagem e classificação', pert='Exigida'), dict(nome='Embalagem', pert='Exigida'),
                     dict(nome='Paletização', pert='Não se aplica', mot='pallet no BEN-8'), dict(nome='Pré-resfriamento', pert='Não se aplica', mot='câmara no BEN-6')],
             ativos=['a13'], equipe=6, avanco='concluir', cx=CX,
             par=dict(frac_vend='0.95', tol_pesado='0.001', pesagem='caixa', tara_pallet='25', aviso_cx='0.05', prazo_insp=2,
                      alcada_pct='0.5', alcada_kg='100', balanca='Balança do packing (a13)', fonte='sintético · v3'))
ROTAS = {
    'PACK-FRU|3': PACK3,
    'PACK-FRU|4': dict(PACK3, v=4, estado='Rascunho', aprov=None),   # nunca oferecida (K26)
    # rotas por cultura já como dado; entram nos blocos seguintes (uma fatia por vez): não são oferecidas no BEN-1
    'SEC-GRA|2': dict(id='SEC-GRA', v=2, estado='Aprovada', aprov=dict(quem='Igor', em='2026-09-10'), bloco='BEN-3', seg='Grãos', cultura='Milho',
                      ent='Milho em grão · úmido', est_ent='Grão úmido', saidas=[dict(fluxo='Produto', prod='Milho em grão', est='Grão seco', classes=['Padrão'])],
                      etapas=[], ativos=[], equipe=2, avanco='saida', par=dict(fonte='sintético · v2', u_ref='14.0')),
    'CAF-BEN|1': dict(id='CAF-BEN', v=1, estado='Aprovada', aprov=dict(quem='Igor', em='2026-09-10'), bloco='BEN-4', seg='Café', cultura='Café',
                      ent='Café em coco', est_ent='Café em coco', saidas=[dict(fluxo='Produto', prod='Café beneficiado', est='Café beneficiado', classes=['COB tipo 6', 'COB tipo 7'])],
                      etapas=[], ativos=[], equipe=4, avanco='concluir', par=dict(fonte='sintético · v1')),
}


def catalogo():
    import dados_manutencao as DM
    at = {a['id']: dict(nome=a['nome'], kgh=a.get('kgh'), custo_h=a.get('custo_h')) for a in DC.ATIVOS if a['id'] in ('a13',)}
    return dict(rotas=ROTAS, cx=dict(item=CX, massa=CXD['massa'], tara=CXD['tara'], un=CXD['un'], emb=EMB_CX, fonte=CXD['fonte'], preco=DC.PRECO_EXTRA.get(CX)),
                ativos=at, cond0={k: v['cond'] for k, v in DM.ATIVOS.items() if k in at}, manKey='talhao-os-manutencao-v1',
                quem=dict(prod=QUEM_PROD, qual=QUEM_QUAL), local=LOCAL, emb=EMBAL)


def _lote(i, prod, kg, drec, q0, cond, obs, classe='', **x):
    import datetime as dt
    vd = (dt.date.fromisoformat(drec) + dt.timedelta(days=7)).isoformat()
    return dict(dict(id=i, prod=prod, cultura='Mamão Formosa', classe=classe, saf='2026/27', faz='Santa Rita', local=LOCAL, drec=drec, dcol=drec,
                     validade=vd, q0=q0, cond=cond, origem=[], cargas=[], abertura=True, tal='T7', obs=obs), **x), kg


def semear(est):
    """Ordens, requisição, lote de caixas e lotes do packing da semente (§10.2 da especificação, com as adaptações do DECISOES §12)."""
    c, P = est, est['producao']
    # lote de caixas do Estoque de insumos: 540 un livres (1.200 já entregues à OB-0110)
    c['lotes'][CX + '|CX26-01'] = dict(prod=CX, lote='CX26-01', local='Packing', un='un', fisico=540, quarentena=0, reservado=0, validade='—')
    c['reqs']['REQ-030'] = dict(id='REQ-030', os='OB-0110', estado='Entregue', itens=[dict(prod=CX, lote='CX26-01', un='un', emb=EMB_CX, solicitado=1200, entregue=1200,
                                consumido=1140, devolvido=0, custodia=60, confirmado='balcao', quem='Igor')])
    # lotes do packing (Santa Rita): saldo de abertura do packing, como o L10-031 da Colheita (D-17): o T7 não tem O.S. de colheita no sistema
    L = [_lote('L38-115', MANGO, 3010, '2026-09-20', 'Liberado', 'Íntegra', 'Fruta do T7 recebida no packing em 20/09 (OC-0507 · S38), antes do registro de cargas', ordem='OB-0110'),
         _lote('L38-116', MANGO, 2980, '2026-09-20', 'Liberado', 'Íntegra', 'Fruta do T7 recebida no packing em 20/09 (OC-0507 · S38), antes do registro de cargas', ordem='OB-0110'),
         _lote('L38-117', MANGO, 2990, '2026-09-20', 'Liberado', 'Íntegra', 'Fruta do T7 recebida no packing em 20/09 (OC-0507 · S38), antes do registro de cargas', ordem='OB-0110'),
         _lote('L38-118', MANGO, 3020, '2026-09-20', 'Liberado', 'Íntegra', 'Fruta do T7 recebida no packing em 20/09 (OC-0507 · S38), antes do registro de cargas', ordem='OB-0110'),
         _lote('L39-117', MANGO, 2960, '2026-09-25', 'Liberado', 'Íntegra', 'CG-1205 do T7: T7-Q1 1.776 kg + T7-Q2 1.184 kg (participação estimada 60/40)'),
         _lote('L39-118', MANGO, 3180, '2026-09-25', 'Liberado', 'Íntegra', 'CG-1206 do T7: 3.210 kg na origem, 3.180 kg na balança do packing (−30 kg)'),
         _lote('L39-119', MANGO, 3130, '2026-09-25', 'Em inspeção', 'Com avaria', 'CG-1207 do T7: avaria térmica parcial (AM-3315) · área segregada do packing', insp='INSP-94'),
         _lote('L26-118', EMBAL, 300, '2026-09-24', 'Bloqueado', 'Fora do padrão', 'Retorno do cliente RC-12 (PV-027) em 24/09 · área de bloqueio do packing', classe='A',
               insp='INSP-93', benef='RC-12', cx=30, bloq=dict(motivo='Maturação avançada em 40 % da amostra (INSP-93)', quem=QUEM_QUAL, d='2026-09-24'))]
    for lot, kg in L:
        P['lotes'][lot['id']] = lot
        P['seq']['mp'] = P['seq'].get('mp', 1000) + 1
        P['movs'].append(dict(id='MP-%d' % P['seq']['mp'], tipo='abertura', lote=lot['id'], kg=kg, d=lot['drec'], at='07:00', quem=('Rui (almoxarife)' if lot['id'] != 'L26-118' else QUEM_QUAL),
                              obs=('Saldo de abertura do packing (anterior ao registro de cargas do T7)' if lot['id'] != 'L26-118' else 'Retorno do cliente RC-12 (PV-027): entra bloqueado')))
    P['pedidos']['PV-031'] = dict(id='PV-031', cliente='Frutas Real', prod=EMBAL, cultura='Mamão Formosa', classe='A', saf='', tipo='pronta', janela='28/09–04/10',
                                  qtd=10000, dest='MI-BR')
    P['ben'] = dict(insp={
        'INSP-92': dict(id='INSP-92', lotes=[], ordem='OB-0110', padrao='PACK-FRU v3 · classes A e B (sintético)', resp=QUEM_QUAL, prazo='', estado='Planejada', res={}),
        'INSP-93': dict(id='INSP-93', lotes=['L26-118'], padrao='Mamão embalado classe A (sintético)', resp=QUEM_QUAL, prazo='2026-09-26', estado='Resultado registrado',
                        res={'L26-118': dict(sit='Não conforme', obs='maturação avançada em 40 % da amostra', quem=QUEM_QUAL, d='2026-09-24', at='15:20')}),
        'INSP-94': dict(id='INSP-94', lotes=['L39-119'], padrao='Recepção de fruta de campo (sintético)', resp=QUEM_QUAL, prazo='2026-09-27', estado='Aberta', res={})},
        recibos={}, seq=dict(insp=105))
    base = dict(fam='BEN', tipo='Beneficiamento · packing de mamão', talhao='Packing', area=0, realizado=0, saldo=0, resp='Igor', selos=[], ap=[])
    def ins(n): return [dict(g='Embalagem', p=CX, dose=0, un='un', tot=n, emb=EMB_CX)]   # grupo: a regra legal de agrotóxico (osUsoItem) não se aplica
    def h(d, at, ev, det, quem=QUEM_PROD, **x): return dict(dict(d=d, at=at, quem=quem, ev=ev, det=det), **x)
    S = lambda i, fluxo, kg, at, **x: dict(dict(id=i, fluxo=fluxo, classe='', destino='', causa='', prod='', lote='', cx=0, pallets=0, bruto=None, tara=None, kg=kg, orig='Pesado',
                                                ev=dict(ticket='', balanca=PACK3['par']['balanca'], em='2026-09-26 ' + at), d='2026-09-26', at=at, quem=QUEM_PROD, chave='SEM-OB-0110-' + i,
                                                estorno=None, subst=''), **x)
    c['ordens']['OB-0110'] = dict(base, id='OB-0110', etapa='Em execução', versao='v1', ver=1, ins=ins(1200), req='REQ-030', reservado=True,
        ben=dict(rota='PACK-FRU|3', faz='Santa Rita', local=LOCAL, ini='2026-09-26', fim='2026-09-27', cxSug=1140, insp='INSP-92', nsai=3,
                 ent=[dict(lote='L38-115', kg=3010), dict(lote='L38-116', kg=2980), dict(lote='L38-117', kg=2990), dict(lote='L38-118', kg=3020)],
                 sai=[S('S-01', 'Produto', 9600, '09:10', classe='A', prod=EMBAL, lote='L39-120', cx=960, bruto=10176, tara=576),
                      S('S-02', 'Produto', 1800, '10:40', classe='B', prod=EMBAL, lote='L39-121', cx=180, bruto=1908, tara=108),
                      S('S-03', 'Descarte', 600, '11:15', destino='Compostagem')],
                 conc=None, conf=None, just=[], corr=None,
                 hist=[h('2026-09-25', '16:40', 'Versão v1 da ordem autorizada (CMD-42)', 'PACK-FRU v3 · 12.000 kg · 1.200 un de caixa (sugestão 1.140 confirmada em 1.200: 20 pallets de entrega)'),
                       h('2026-09-25', '16:40', 'Liberada (CMD-06)', 'REQ-030 reservou 1.200 un de ' + CX + ' no CX26-01'),
                       h('2026-09-25', '17:10', 'Caixas entregues no balcão', '1.200 un do CX26-01 em custódia de Igor', quem='Rui (almoxarife)'),
                       h('2026-09-26', '06:30', 'Iniciada', 'Entradas L38-115, L38-116, L38-117 e L38-118 em processo'),
                       h('2026-09-26', '09:10', 'Saída S-01 registrada', 'Produto A · 960 cx · bruto 10.176 kg − tara 576 kg = 9.600 kg → L39-120'),
                       h('2026-09-26', '10:40', 'Saída S-02 registrada', 'Produto B · 180 cx · bruto 1.908 kg − tara 108 kg = 1.800 kg → L39-121'),
                       h('2026-09-26', '11:15', 'Saída S-03 registrada', 'Descarte · Compostagem · 600 kg')]))
    c['ordens']['OB-0112'] = dict(base, id='OB-0112', etapa='A liberar', versao='v1', ver=1, ins=ins(881), req=None, reservado=False,
        ben=dict(rota='PACK-FRU|3', faz='Santa Rita', local=LOCAL, ini='2026-09-27', fim='2026-09-28', cxSug=881, insp='', nsai=0,
                 ent=[dict(lote='L39-117', kg=2960), dict(lote='L39-118', kg=3180), dict(lote='L39-119', kg=3130)], sai=[], conc=None, conf=None, just=[], corr=None,
                 hist=[h('2026-09-25', '18:05', 'Ordem criada · v1', 'PACK-FRU v3 · L39-117, L39-118 e L39-119 · 9.270 kg · 881 un de caixa (sugestão confirmada)')]))
    return est


def js_regras():
    """BENC + ben.js (regras e comandos ben*): entra em cenario.js_prefixo() depois de producao.js (as regras de lote são as dela)."""
    return ('const BENC = ' + json.dumps(catalogo(), ensure_ascii=False).replace('</', '<\\/') + ';\n'
            + open(os.path.join(HERE, 'ben.js'), encoding='utf-8').read() + '\n')


if __name__ == '__main__':
    import cenario
    s = cenario.seed(); print(sorted(k for k in s['ordens'] if k.startswith('OB')), s['reqs']['REQ-030']['itens'][0]['custodia'], s['producao']['seq'])
