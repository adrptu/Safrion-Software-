# -*- coding: utf-8 -*-
"""Plataforma de assinaturas (PLAT-01) · fonte única dos planos, dos parâmetros e do seed sintético da assinatura.

Tudo aqui é EXEMPLO para o protótipo: preço, mínimo, franquias, trial, calendário e régua de inadimplência são decisões do
proprietário (DEC-01, DEC-05, DEC-09 do PRD 70.4; docs/plataforma-assinaturas/DECISOES.md). Cobrança simulada: nenhum provedor
de pagamento, nenhuma credencial, nenhum campo de cartão. O estado vive em c.assin do cenário salvo (talhao-os-cenario-v1);
ausente, vale ASSIN0 (PLAT-D12). As telas leem a mesma tabela de planos (ASSIN_PAR) e calculam a mensalidade por assinMensalidade
(assinatura.js), que usa a regra decimal única cenQtd (cenario.js). Aqui o Python só monta o seed e confere os números dele."""
import json, os, math
from decimal import Decimal, ROUND_HALF_UP

HERE = os.path.dirname(os.path.abspath(__file__))
DECIDIR = 'exemplo · a decidir pelo proprietário'

# Trial da Organização Boa Esperança (ON-01 importa daqui: um só trial para ON-01, BO-01 e BO-02)
TRIAL = dict(coorte='set/2026', dias=30, fim='18/10/2026', area_ha=480, inicio_iso='2026-09-19', fim_iso='2026-10-18')

# ---- planos (exemplo, a decidir pelo proprietário) ----
NUCLEO = ['Mapa', 'Cadastros', 'Agrícola (O.S. e app de campo)', 'Colheita e produção por talhão', 'Manutenção', 'Suprimentos']
SO_COMPLETO = ['Pós-colheita (beneficiamento)', 'Comercial e logística', 'Gestão e resultados', 'Integração ERP (sandbox)']
PLANOS = [
    dict(id='aval', nome='Avaliação', pago=False, preco=0, minimo=0, limite=None, dias=TRIAL['dias'], sat=12, ia=200, sat_un='cenas no período',
         ia_un='interações no período', modulos=NUCLEO + SO_COMPLETO, usuarios='sem limite',
         obs='30 dias; limite = área declarada; consulta e exportação por 90 dias após o fim', dec='DEC-09'),
    dict(id='ess', nome='Essencial', pago=True, preco=1.5, minimo=199, limite=5000, sat=6, ia=100, sat_un='cenas/mês', ia_un='interações/mês',
         modulos=NUCLEO, usuarios='sem limite', obs='valor novo, só de exemplo', dec='DEC-01 · DEC-09'),
    dict(id='comp', nome='Completo', pago=True, preco=2, minimo=299, limite=5000, sat=12, ia=200, sat_un='cenas/mês', ia_un='interações/mês',
         modulos=NUCLEO + SO_COMPLETO, usuarios='sem limite', obs='hipótese do PRD 57.2', dec='DEC-01 · DEC-09'),
]
# ---- parâmetros (exemplo, a decidir pelo proprietário; PLAT-D05..D09, D13, D15) ----
PARAM = dict(
    base='medida',                 # DEC-01: 'medida' (cobra a medida limitada pela contratada) ou 'contratada'
    dia_venc=1, tentativas=3, janela_tent=10, prorata=False,
    dias_aviso=10,                 # 1..10 dias de atraso: só aviso; 11 ou mais: restrição
    restricoes=['ampliar_area'],   # o que a inadimplência restringe (lista vazia = só aviso)
    limite_ha=5000,                # acima: proposta empresarial
    contest_dias=5,                # nova data de vencimento depois de resolver uma contestação
    formas=['Pix', 'Boleto', 'Cartão final 4242'],   # forma escolhida numa lista; nenhum campo de cartão (princípio 1, PLAT-D11)
    cancelamento='sem fidelidade; cancelamento ao fim do ciclo · ' + DECIDIR,
    datas=['2026-09-23', '2026-10-01', '2026-10-06', '2026-10-16'],   # data simulada da cobrança (painel Demonstração, PLAT-D13)
    decidir=DECIDIR,
)
_P = {p['id']: p for p in PLANOS}


def dec(x):
    return Decimal(str(x))


def mensalidade(plano, medida, contratada, credito=0):
    """Conferência do seed em Python (mesma regra de assinMensalidade): cobrada = mín(medida; contratada); valor = máx(mínimo; preço × cobrada)
    − crédito, em decimal, 2 casas, meio para cima. As telas não usam esta função: calculam no navegador."""
    P = _P[plano]; med = dec(medida); cob = med if contratada is None else min(med, dec(contratada))
    if not P['pago']: return cob, Decimal('0.00')
    bruto = (dec(P['preco']) * cob).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    base = max(dec(P['minimo']), bruto)
    return cob, max(Decimal('0.00'), base - min(base, dec(credito))).quantize(Decimal('0.01'))


def cad0():
    """base do cadastro de fazendas e talhões (a mesma do Mapa, inicio._cad0), só com o que a medição usa: id, nome, fazenda, área cultivável e situação."""
    import areas.cad_fazendas as CF
    faz = [dict(id=r['id'], v=dict(nome=r['v']['nome'], sit=r['v']['sit'])) for r in CF._faz_rows()]
    tal = [dict(id=r['id'], v=dict(t=r['v']['t'], faz=r['v']['faz'], decl=r['v']['decl'], sit=r['v']['sit'], geo=r['v'].get('geo', ''), calc=r['v'].get('calc', '')))
           for r in CF._tal_rows()]
    return dict(faz=faz, tal=tal)


def medir(base, fazendas=None):
    """R1 na geração: soma decimal da área cultivável dos talhões ativos de fazendas ativas (opcional: só as fazendas pedidas)."""
    ativas = {f['v']['nome'] for f in base['faz'] if f['v']['sit'] != 'Inativa'}
    ts = [t for t in base['tal'] if t['v']['sit'] != 'Inativo' and t['v']['faz'] in ativas and (fazendas is None or t['v']['faz'] in fazendas)]
    return sum((dec(t['v']['decl']) for t in ts), Decimal('0')), len(ts)


def _r(x): return float(dec(x).quantize(Decimal('0.01')))


def _fat(org, comp, plano, contrato, medida, ntal, emitida, st, eventos, paga=None, evt=None, forma=None, tent=None):
    cob, val = mensalidade(plano, medida, contrato['ha'])
    P = _P[plano]
    fim = {'2026-07': '2026-07-31', '2026-08': '2026-08-31', '2026-09': '2026-09-30'}[comp]
    return dict(id=f'{org}-{comp}', comp=comp, st=st, valor=_r(val), emitida=emitida, venc=emitida, paga=paga, evt=evt, forma=forma, recibo=None,
                copia=dict(medida=_r(medida), ntal=ntal, contratada=contrato['ha'], cobrada=_r(cob), plano=plano, preco=P['preco'], minimo=P['minimo'],
                           versao='v' + str(contrato['v']), fechamento=fim, credito=0),
                eventos=eventos, tent=tent or [], contest=None)


def seed():
    """ASSIN0: estado inicial da assinatura (sintético). Data simulada da cobrança 23/09/2026 (= dados.HOJE)."""
    base = cad0()
    med_sr, n_sr = medir(base, {'Santa Rita'})          # jul e ago: só a Santa Rita no cadastro (Boa Vista e Lagoa entram em 01/09)
    med_all, _n = medir(base)
    v2 = int(math.ceil(med_all / 100) * 100)            # contrato v2: medida da base arredondada para cima à centena (2.600 ha)
    c1 = dict(v=1, plano='comp', ha=1200, desde='2026-07-01', aceite='2026-06-28')
    c2 = dict(v=2, plano='comp', ha=v2, desde='2026-09-01', aceite='2026-08-28')
    ev = lambda d, t: dict(d=d, t=t)
    sr = dict(id='sr', nome='Grupo Santa Rita', demo=True, uf='GO · MT · MG', cartao=None, contratos=[c1, c2], medida_inf=None, creditos=[],
              faturas=[_fat('sr', '2026-07', 'comp', c1, med_sr, n_sr, '2026-08-01', 'paga',
                            [ev('2026-08-01', 'Emitida · R$ 2.330,00'), ev('2026-08-01', 'Paga · evt_demo_0801 · Pix (simulado)')], '2026-08-01', 'evt_demo_0801', 'Pix'),
                       _fat('sr', '2026-08', 'comp', c1, med_sr, n_sr, '2026-09-01', 'paga',
                            [ev('2026-09-01', 'Emitida · R$ 2.330,00'), ev('2026-09-01', 'Paga · evt_demo_0901 · Pix (simulado)')], '2026-09-01', 'evt_demo_0901', 'Pix')])
    ca = dict(v=1, plano='comp', ha=60, desde='2026-08-01', aceite='2026-07-30')
    aurora = dict(id='aurora', nome='Fazenda Aurora', demo=False, uf='MT', cartao='final 1881', contratos=[ca], medida_inf=35, creditos=[],
                  faturas=[_fat('aurora', '2026-08', 'comp', ca, 35, None, '2026-09-01', 'aberta',
                                [ev('2026-09-01', 'Emitida · R$ 299,00'), ev('2026-09-01', 'Tentativa 1 recusada · cartão final 1881'),
                                 ev('2026-09-05', 'Tentativa 2 recusada · cartão final 1881'), ev('2026-09-10', 'Tentativa 3 recusada · tentativas automáticas encerradas')],
                                tent=['2026-09-01', '2026-09-05', '2026-09-10'])])
    ci = dict(v=1, plano='ess', ha=20, desde='2026-06-01', aceite='2026-05-28')
    ipe = dict(id='ipe', nome='Sítio Ipê', demo=False, uf='PR', cartao='final 3090', contratos=[ci], medida_inf=20, creditos=[],
               faturas=[_fat('ipe', '2026-08', 'ess', ci, 20, None, '2026-09-01', 'paga',
                             [ev('2026-09-01', 'Emitida · R$ 199,00'), ev('2026-09-01', 'Paga · evt_1JKQ3 · cartão final 3090 (simulado)')], '2026-09-01', 'evt_1JKQ3', 'Cartão final 3090')])
    cb = dict(v=1, plano='comp', ha=320, desde='2026-05-01', aceite='2026-04-27')
    bv = dict(id='bv', nome='Agro Bela Vista', demo=False, uf='BA', cartao=None, contratos=[cb], medida_inf=333, creditos=[],
              faturas=[_fat('bv', '2026-08', 'comp', cb, 333, None, '2026-09-01', 'pendente',
                            [ev('2026-09-01', 'Emitida · R$ 640,00'), ev('2026-09-02', 'Boleto pago pelo cliente · aguardando evento do provedor (evt_1JKT5)')])])
    cbe = dict(v=1, plano='aval', ha=TRIAL['area_ha'], desde=TRIAL['inicio_iso'], aceite=TRIAL['inicio_iso'])
    boa = dict(id='boaesp', nome='Org. Boa Esperança', demo=False, uf='GO', cartao=None, contratos=[cbe], medida_inf=TRIAL['area_ha'], creditos=[], faturas=[],
               trial=dict(inicio=TRIAL['inicio_iso'], fim=TRIAL['fim_iso'], dias=TRIAL['dias']))
    cd = dict(v=1, plano='ess', ha=40, desde='2026-03-01', aceite='2026-02-25')
    dois = dict(id='dois', nome='Rancho Dois Rios', demo=False, uf='MS', cartao=None, contratos=[cd], medida_inf=40, creditos=[], cancelada='2026-08-31',
                consulta_ate='2026-11-29',
                faturas=[_fat('dois', '2026-08', 'ess', cd, 40, None, '2026-09-01', 'paga',
                              [ev('2026-09-01', 'Emitida · R$ 199,00'), ev('2026-09-01', 'Paga · evt_1JKP7 · boleto (simulado)'),
                               ev('2026-08-31', 'Cancelamento a pedido ao fim do ciclo · consulta e exportação até 29/11/2026')], '2026-09-01', 'evt_1JKP7', 'Boleto')])
    fila = [dict(evt='evt_1JKT5', org='bv', fat='bv-2026-08', valor=640.0, ok=True, d='2026-09-22', forma='Boleto', motivo='pagamento confirmado'),
            dict(evt='evt_1JKR9', org='aurora', fat='aurora-2026-08', valor=299.0, ok=False, d='2026-09-22', forma='Cartão novo final 7702', motivo='recusado pelo emissor')]
    vistos = ['evt_demo_0801', 'evt_demo_0901', 'evt_1JKQ3', 'evt_1JKP7']
    return dict(v=1, hoje='2026-09-23', demo='sr', orgs={o['id']: o for o in (sr, aurora, ipe, bv, boa, dois)}, fila=fila, vistos=vistos, recibos={}, seq={})


_CACHE = {}


def js_prefixo():
    """prefixo de TODA tela (engine): ASSIN0 + ASSIN_PAR + ASSIN_CENV + assinatura.js, uma vez por página (RV-01)."""
    if 'js' not in _CACHE:
        import cenario
        par = dict(PARAM, planos=PLANOS)
        _CACHE['js'] = ('const ASSIN0 = ' + json.dumps(seed(), ensure_ascii=False).replace('</', '<\\/') + ';\n'
                        + 'const ASSIN_PAR = ' + json.dumps(par, ensure_ascii=False).replace('</', '<\\/') + ';\n'
                        + 'const ASSIN_CENV = ' + json.dumps(cenario.seed()['v']) + ';\n'
                        + open(os.path.join(HERE, 'assinatura.js'), encoding='utf-8').read() + '\n')
    return _CACHE['js']


def js_cad0():
    """base do cadastro para medir a área (só CF-05 e BO-02)."""
    return 'const ASSIN_CAD0 = ' + json.dumps(cad0(), ensure_ascii=False).replace('</', '<\\/') + ';\n'


if __name__ == '__main__':
    import sys; sys.path.insert(0, HERE)
    s = seed()
    for k, o in s['orgs'].items():
        print(k, o['nome'], [(f['comp'], f['st'], f['valor'], f['copia']['medida']) for f in o['faturas']], o['contratos'][-1])
