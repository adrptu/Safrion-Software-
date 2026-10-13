# -*- coding: utf-8 -*-
"""Manutenção · planos de manutenção periódica e cenário compartilhado (PM, MA-01, MA-03, MA-04, MA-05).

Fonte única dos dados de demonstração da manutenção:
- ativos com a identidade do CD-03 (dados_cad.ATIVOS) + Comboio CB-01 (veículo com odômetro, só nos dados da manutenção);
- leituras de contador (valor, data, origem) e ritmo projetado pelo PCP (h/dia ou km/dia);
- itens de estoque da manutenção (peças e lubrificantes) com saldo, reservado e preço;
- planos PM-01..PM-10 (serviços com gatilhos h/km/dias "o que vencer primeiro", tolerância, checklist, peças, tempo, especialidade);
- vínculos plano × ativo com marco inicial e última execução por serviço;
- ordens de manutenção já existentes (OM-0221, 0228, 0230, 0233, 0234).
Hoje da demonstração: 23/09/2026. "Vence em breve" = a janela (vencimento − tolerância) começa em até 10 dias (parâmetro de política).
vencimento() é a mesma fórmula do manVenc() do JS (paridade conferida em ma_planos_test.py).
Passo 4 (03/10): base "vencimento programado" no fechamento do ciclo; leitura implausível (> 24 h/dia ou 1.500 km/dia) e leitura menor
viram "a confirmar" com Confirmar/Descartar (troca de contador ajusta o histórico); quantidade aplicada gera sobra; falta de peça →
SC → recebimento (simulado); um serviço por ativo entre planos (sem OM em dobro); achados do MA-02 vinculados à OM (ach)."""
import json, math, datetime
import dados_cad as DC

HOJE = '2026-09-23'
HORIZONTE = 10          # dias: "vence em breve"
LEIT_ANTIGA = 7         # dias: leitura antiga vira aviso
CUSTO_H = 320           # R$/h de oficina (hipótese já usada na OM-0233)
# leitura implausível (aviso a confirmar, nunca bloqueio): mais que 24 h por dia no horímetro ou 1.500 km por dia no odômetro desde a última leitura
MAX_DIA = {'h': 24, 'km': 1500}

# ---------- ativos: identidade do CD-03 + contador, leitura, ritmo e condição técnica ----------
# un: 'h' horímetro · 'km' odômetro · '' sem contador (só calendário)
EXTRA = {
 'a01': dict(un='h', leit=(4312, '2026-09-23', 'Inspeção INSP-105'), ritmo=9, cond='Bloqueado'),
 'a02': dict(un='h', leit=(2988, '2026-09-23', 'Abastecimento AB-1042'), ritmo=11, cond='Apto'),
 'a03': dict(un='h', leit=(5120, '2026-09-22', 'Apontamento de turno'), ritmo=10, cond='Apto'),
 'a04': dict(un='h', leit=(3410, '2026-09-12', 'Apontamento de turno'), ritmo=4, cond='Apto'),
 'a05': dict(un='h', leit=(1542, '2026-09-23', 'Abastecimento AB-1041'), ritmo=9, cond='Apto'),
 'a06': dict(un='h', leit=(886, '2026-09-20', 'Apontamento de turno'), ritmo=0, cond='Apto'),
 'a07': dict(un='h', leit=(640, '2026-09-18', 'Apontamento de turno'), ritmo=1, cond='Apto'),
 'a08': dict(un='h', leit=(2150, '2026-09-22', 'Abastecimento AB-1039'), ritmo=2, cond='Apto'),
 'a09': dict(un='h', leit=(720, '2026-09-19', 'Apontamento de turno'), ritmo=2, cond='Apto'),
 'a10': dict(un='h', leit=(310, '2026-09-15', 'Apontamento de turno'), ritmo=1, cond='Apto'),
 'a15': dict(un='h', leit=(7650, '2026-09-23', 'Telemetria'), ritmo=11, cond='Apto'),
 'a11': dict(un='h', leit=(8914, '2026-09-23', 'Telemetria'), ritmo=11, cond='Restrito · monitorado'),
 'a12': dict(un='h', leit=(5210, '2026-09-23', 'Telemetria'), ritmo=9, cond='Apto'),
 'a13': dict(un='h', leit=(12301, '2026-09-22', 'Apontamento de turno'), ritmo=9, cond='Apto'),
 'a14': dict(un='', leit=None, ritmo=0, cond='Apto'),
}
GRUPO = {'Trator': 'Tratores', 'Pulverizador': 'Pulverizadores', 'Plantadeira': 'Plantadeiras', 'Distribuidor': 'Implementos',
         'Colhedora': 'Colhedoras', 'Tratamento de sementes': 'Beneficiamento', 'Implemento': 'Implementos', 'Irrigação': 'Irrigação',
         'Beneficiamento': 'Beneficiamento', 'Armazenagem': 'Armazenagem', 'Veículo': 'Veículos'}


def _ativos():
    out = {}
    for a in DC.ATIVOS:
        x = EXTRA[a['id']]
        out[a['id']] = dict(id=a['id'], nome=a['nome'], modelo=a['modelo'], classe=a['classe'], grupo=GRUPO.get(a['classe'], a['classe']),
                            local=a['local'], un=x['un'], ritmo=x['ritmo'], cond=x['cond'],
                            leit=(dict(val=x['leit'][0], data=x['leit'][1], origem=x['leit'][2]) if x['leit'] else None))
    out['cb01'] = dict(id='cb01', nome='Comboio CB-01', modelo='caminhão comboio 6 m³', classe='Veículo', grupo='Veículos', local='Sede',
                       un='km', ritmo=80, cond='Apto', leit=dict(val=48200, data='2026-09-23', origem='Abastecimento AB-1040'))
    return out


ATIVOS = _ativos()
ORDEM_ATIVOS = [a['id'] for a in DC.ATIVOS] + ['cb01']

# ---------- itens de estoque da manutenção (grupo Peças / Lubrificantes) ----------
ITENS = {
 'KIT-MF7719': dict(nome='Kit filtros MF 7719', un='kit', saldo=2, reservado=0, preco=690),
 'FIL-MF4292': dict(nome='Filtro de óleo MF 4292', un='un', saldo=0, reservado=0, preco=160),
 'KIT-JD': dict(nome='Kit filtros John Deere', un='kit', saldo=3, reservado=0, preco=740),
 'KIT-U3030': dict(nome='Kit filtros Uniport 3030', un='kit', saldo=3, reservado=0, preco=520),
 'KIT-C7250': dict(nome='Kit filtros Case IH 7250', un='kit', saldo=1, reservado=0, preco=1350),
 'KIT-CB01': dict(nome='Kit filtros caminhão comboio', un='kit', saldo=1, reservado=0, preco=480),
 'OL-1540': dict(nome='Óleo de motor 15W-40', un='L', saldo=120, reservado=0, preco=28),
 'OL-HID68': dict(nome='Óleo hidráulico 68', un='L', saldo=200, reservado=0, preco=24),
 'GR-EP2': dict(nome='Graxa EP2', un='kg', saldo=18, reservado=0, preco=32),
 'VED-MB': dict(nome='Kit vedação da motobomba', un='kit', saldo=1, reservado=0, preco=380),
 'DSC-15': dict(nome='Disco de corte 15"', un='un', saldo=24, reservado=0, preco=210),
}
ESPECIALIDADES = ['Mecânico', 'Eletricista', 'Lubrificador', 'Terceiro (concessionária)']

T250 = ['Trocar óleo do motor', 'Trocar filtro de óleo do motor', 'Trocar filtro de combustível', 'Limpar filtro de ar', 'Lubrificar pontos de graxa']


def _s(sid, nome, gat, tol, tarefas, pecas, tempo, esp, cumpre=(), base='exec'):
    return dict(id=sid, nome=nome, gat=gat, tol=tol, base=base, cumpre=list(cumpre), tempo=tempo, esp=esp,
                tarefas=list(tarefas), pecas=[dict(item=i, qtd=q) for i, q in pecas])


PLANOS = [
 dict(id='PM-01', nome='Trator MF 7719 · revisões', grupo='Tratores', aplica=dict(t='modelo', v=['MF 7719']), versao=3,
      hist=[(3, '14/07/2026'), (2, '10/01/2026'), (1, '05/03/2025')],
      servicos=[_s('s1', 'Revisão 250 h', dict(h=250, d=180), dict(h=25, d=15), T250, [('KIT-MF7719', 1), ('OL-1540', 16)], 5, 'Mecânico'),
                _s('s2', 'Revisão 500 h', dict(h=500, d=365), dict(h=25, d=15),
                   T250 + ['Trocar óleo hidráulico e filtro', 'Regular folga das válvulas', 'Inspecionar mangueiras hidráulicas'],
                   [('KIT-MF7719', 1), ('OL-1540', 16), ('OL-HID68', 40)], 8, 'Mecânico', cumpre=['s1'])]),
 dict(id='PM-02', nome='Trator MF 4292 · revisões', grupo='Tratores', aplica=dict(t='modelo', v=['MF 4292']), versao=2,
      hist=[(2, '20/02/2026'), (1, '11/04/2025')],
      servicos=[_s('s1', 'Revisão 250 h', dict(h=250, d=180), dict(h=25, d=15), T250, [('FIL-MF4292', 1), ('OL-1540', 12)], 4, 'Mecânico')]),
 dict(id='PM-03', nome='Tratores John Deere · revisões', grupo='Tratores', aplica=dict(t='modelo', v=['JD 6M 155', 'JD 5078E']), versao=4,
      hist=[(4, '03/08/2026'), (3, '15/12/2025')],
      servicos=[_s('s1', 'Revisão 250 h', dict(h=250, d=180), dict(h=25, d=15), T250, [('KIT-JD', 1), ('OL-1540', 18)], 5, 'Mecânico')]),
 dict(id='PM-04', nome='Pulverizador Uniport 3030 · revisões', grupo='Pulverizadores', aplica=dict(t='ativos', v=['a05']), versao=2,
      hist=[(2, '30/06/2026'), (1, '12/03/2025')],
      servicos=[_s('s1', 'Revisão 250 h', dict(h=250), dict(h=25),
                   ['Trocar filtros de linha e de bico', 'Verificar bicos e vazão', 'Lubrificar articulações da barra', 'Inspecionar mangueiras'],
                   [('KIT-U3030', 1), ('GR-EP2', 1)], 3, 'Mecânico'),
                _s('s2', 'Revisão 500 h', dict(h=500), dict(h=25),
                   ['Trocar filtros de linha e de bico', 'Verificar bicos e vazão', 'Lubrificar articulações da barra', 'Inspecionar mangueiras',
                    'Trocar óleo hidráulico', 'Trocar filtro hidráulico'],
                   [('KIT-U3030', 3), ('OL-HID68', 40), ('GR-EP2', 1)], 9, 'Mecânico', cumpre=['s1'])]),
 dict(id='PM-05', nome='Plantadeira · revisão pré-plantio', grupo='Plantadeiras', aplica=dict(t='ativos', v=['a06']), versao=1,
      hist=[(1, '02/08/2025')],
      servicos=[_s('s1', 'Revisão pré-plantio', dict(d=365), dict(d=0),
                   ['Trocar discos de corte desgastados', 'Regular dosadores de semente', 'Lubrificar correntes e mancais', 'Calibrar adubadora', 'Testar monitor de plantio'],
                   [('DSC-15', 8), ('GR-EP2', 2)], 6, 'Mecânico')]),
 dict(id='PM-06', nome='Colhedora Case IH 7250 · revisões', grupo='Colhedoras', aplica=dict(t='modelo', v=['Case IH 7250']), versao=2,
      hist=[(2, '18/09/2025'), (1, '20/10/2024')],
      servicos=[_s('s1', 'Revisão 500 h', dict(h=500, d=365), dict(h=25, d=7),
                   ['Trocar óleo e filtros do motor', 'Trocar filtro de ar primário', 'Inspecionar elevador e correntes', 'Lubrificar pontos de graxa', 'Revisar rotor e côncavos'],
                   [('KIT-C7250', 1), ('OL-1540', 30), ('GR-EP2', 2)], 10, 'Mecânico')]),
 dict(id='PM-07', nome='Motobombas de pivô · preventiva mensal', grupo='Irrigação', aplica=dict(t='ativos', v=['a15', 'a11']), versao=3,
      hist=[(3, '01/07/2026'), (2, '15/01/2026')],
      servicos=[_s('s1', 'Preventiva mensal', dict(h=1000, d=30), dict(h=50, d=3),
                   ['Medir isolamento e corrente do motor', 'Reapertar conexões elétricas', 'Trocar vedação se houver vazamento', 'Lubrificar mancais', 'Testar pressostato e proteção'],
                   [('VED-MB', 1), ('GR-EP2', 1)], 4, 'Eletricista')]),
 dict(id='PM-08', nome='Packing linha 1 · preventiva mensal', grupo='Beneficiamento', aplica=dict(t='ativos', v=['a13']), versao=1,
      hist=[(1, '10/01/2026')],
      servicos=[_s('s1', 'Preventiva mensal', dict(d=30), dict(d=3),
                   ['Lubrificar rolamentos da esteira', 'Verificar tensão das correias', 'Aferir balança com peso-padrão', 'Limpar sensores'],
                   [('GR-EP2', 1)], 3, 'Mecânico')]),
 dict(id='PM-09', nome='Silo e aeração · trimestral', grupo='Armazenagem', aplica=dict(t='ativos', v=['a14']), versao=1,
      hist=[(1, '05/04/2026')],
      servicos=[_s('s1', 'Inspeção trimestral', dict(d=90), dict(d=5),
                   ['Inspecionar ventiladores de aeração', 'Testar termometria', 'Verificar vedação e escadas', 'Limpar fundo do silo'], [], 4, 'Eletricista')]),
 dict(id='PM-10', nome='Caminhão comboio · revisões', grupo='Veículos', aplica=dict(t='ativos', v=['cb01']), versao=1,
      hist=[(1, '02/05/2026')],
      servicos=[_s('s1', 'Revisão 10.000 km', dict(km=10000, d=180), dict(km=500, d=15),
                   ['Trocar óleo e filtros do motor', 'Inspecionar freios', 'Verificar bomba e medidor de diesel', 'Revisar pneus'],
                   [('KIT-CB01', 1), ('OL-1540', 20)], 4, 'Mecânico')]),
]

# vínculos plano × ativo: marco inicial + última execução por serviço (data, leitura, ordem)
def _u(data, leit, om): return dict(data=data, leit=leit, om=om)
VINCULOS = {
 'PM-01|a02': dict(marco=_u('2025-03-05', 0, None), ult={'s1': _u('2026-09-02', 2793, 'OM-0219'), 's2': _u('2026-09-02', 2793, 'OM-0219')}),
 'PM-02|a03': dict(marco=_u('2025-04-11', 3010, None), ult={'s1': _u('2026-08-08', 4840, 'OM-0212')}),
 'PM-03|a01': dict(marco=_u('2024-12-15', 2950, None), ult={'s1': _u('2026-09-12', 4200, 'OM-0231')}),
 'PM-03|a04': dict(marco=_u('2024-12-15', 1980, None), ult={'s1': _u('2026-06-02', 3300, 'OM-0205')}),
 'PM-04|a05': dict(marco=_u('2025-03-12', 210, None), ult={'s1': _u('2026-09-20', 1540, 'OM-0230'), 's2': _u('2026-09-20', 1540, 'OM-0230')}),
 'PM-05|a06': dict(marco=_u('2025-08-02', 610, None), ult={'s1': _u('2025-09-20', 640, 'OM-0118')}),
 'PM-06|a08': dict(marco=_u('2024-10-20', 1300, None), ult={'s1': _u('2025-10-15', 1800, 'OM-0102')}),
 'PM-07|a15': dict(marco=_u('2025-01-15', 3100, None), ult={'s1': _u('2026-09-15', 7500, 'OM-0229')}),
 'PM-07|a11': dict(marco=_u('2025-01-15', 3400, None), ult={'s1': _u('2026-09-01', 8300, 'OM-0222')}),
 'PM-08|a13': dict(marco=_u('2026-01-10', 9800, None), ult={'s1': _u('2026-09-08', 12100, 'OM-0225')}),
 'PM-09|a14': dict(marco=_u('2026-04-05', None, None), ult={'s1': _u('2026-07-12', None, 'OM-0207')}),
 'PM-10|cb01': dict(marco=_u('2026-05-02', 39400, None), ult={'s1': _u('2026-05-15', 40000, 'OM-0181')}),
}


def _chk(tarefas, r=''):
    return [dict(t=t, r=r, mot='') for t in tarefas]


def _plano(pid): return next(p for p in PLANOS if p['id'] == pid)
def _serv(pid, sid): return next(s for s in _plano(pid)['servicos'] if s['id'] == sid)


def _ciclo(pid, aid, sid):
    v = VINCULOS[pid + '|' + aid]; u = v['ult'].get(sid) or v['marco']
    return f"{pid}|{aid}|{sid}@{u['data']}|{u['leit'] if u['leit'] is not None else ''}"


# ordens já existentes (as cinco fases canônicas; condições viram selo)
def _oms():
    s1 = _serv('PM-01', 's1'); s2p = _serv('PM-04', 's2')
    return {
     'OM-0221': dict(id='OM-0221', tipo='Corretiva', aid='a08', serv='Corretiva · rolamento do elevador', crit='Média', etapa='Encerradas',
                     origem='SM-0140 · falha em campo', jan='12/09', ret='liberado 13/09', esp='Terceiro (concessionária)', tempo=14,
                     chk=_chk(['Desmontar elevador', 'Trocar rolamentos', 'Montar e alinhar correntes', 'Teste em vazio'], 'Feito'),
                     pecas=[dict(item='', nome='Rolamento do elevador', un='un', qtd=2, res=0, apl=2, sob=0, preco=640)],
                     exec=dict(data='2026-09-13', leit=2149, horas=14), custo=3800, selos=[]),
     'OM-0228': dict(id='OM-0228', tipo='Corretiva', aid='a11', serv='Inspeção corretiva · pressão baixa', crit='Alta', etapa='Liberadas',
                     origem='SM-0152 · alerta agregado (3 leituras)', jan='hoje 14:00', ret='hoje 17:00', esp='Eletricista', tempo=3,
                     chk=_chk(['Medir pressão de recalque', 'Inspecionar selo mecânico', 'Verificar painel e pressostato']), pecas=[], exec=None, selos=[]),
     'OM-0230': dict(id='OM-0230', tipo='Preventiva', aid='a05', pid='PM-04', sid='s2', ver=2, cobre=['s2', 's1'], ciclos={}, serv='Revisão 500 h', crit='Média',
                     etapa='Em conferência', origem='PM-04 v2 · Revisão 500 h · 1.540 h (500 h após 1.040 h)', jan='20/09', ret='liberado 21/09', esp='Mecânico', tempo=9,
                     chk=_chk(s2p['tarefas'], 'Feito'),
                     pecas=[dict(item='KIT-U3030', nome='Kit filtros Uniport 3030', un='kit', qtd=3, res=0, apl=1, sob=2, preco=520),
                            dict(item='OL-HID68', nome='Óleo hidráulico 68', un='L', qtd=40, res=0, apl=40, sob=0, preco=24),
                            dict(item='GR-EP2', nome='Graxa EP2', un='kg', qtd=1, res=0, apl=1, sob=0, preco=32)],
                     exec=dict(data='2026-09-20', leit=1540, horas=9), selos=[]),
     'OM-0233': dict(id='OM-0233', tipo='Corretiva', aid='a01', serv='Corretiva · pressão hidráulica', crit='Alta', etapa='Em execução',
                     origem='SM-0147 · falha em campo · INSP-105', jan='hoje', ret='24/09 12:00', esp='Mecânico', tempo=6.5, det='MA-04det.dc.html',
                     chk=[dict(t='Substituir bomba hidráulica', r='Feito', mot=''), dict(t='Trocar mangueiras de alta pressão', r='Feito', mot=''),
                          dict(t='Reaperto e sangria do circuito', r='Feito', mot=''), dict(t='Teste de pressão em carga', r='', mot='')],
                     pecas=[dict(item='', nome='Bomba hidráulica', un='un', qtd=1, res=1, apl=1, sob=0, preco=3600),
                            dict(item='', nome='Mangueira de alta pressão', un='un', qtd=2, res=2, apl=2, sob=0, preco=250)],
                     exec=None, selos=[]),
     'OM-0234': dict(id='OM-0234', tipo='Preventiva', aid='a02', pid='PM-01', sid='s1', ver=3, cobre=['s1'], ciclos={'s1': _ciclo('PM-01', 'a02', 's1')},
                     serv='Revisão 250 h', crit='Média', etapa='A liberar', origem='PM-01 v3 · Revisão 250 h · 3.043 h (250 h após 2.793 h)',
                     jan='28/09', ret='28/09 17:00', esp=s1['esp'], tempo=s1['tempo'], chk=_chk(s1['tarefas']),
                     pecas=[dict(item=p['item'], nome=ITENS[p['item']]['nome'], un=ITENS[p['item']]['un'], qtd=p['qtd'], res=0, apl=0, sob=0, preco=ITENS[p['item']]['preco']) for p in s1['pecas']],
                     exec=None, conflito=dict(os='OS-0420', t='Janela 28/09 em conflito com a OS-0420 (plantio T4 · saldo 70 ha)'), selos=[]),
    }


# ---------- vencimento (mesma fórmula do manVenc em JS) ----------
def _d(s): return datetime.date.fromisoformat(s)
def _iso(d): return d.isoformat()


def vencimento(serv, ativo, ref, hoje=HOJE):
    """serv: dict(gat, tol); ativo: dict(un, leit, ritmo); ref: dict(data, leit) = última execução ou marco.
    Devolve dict(sit, gats=[...], prim=índice do gatilho que vence primeiro, prev=data projetada)."""
    H = _d(hoje); gats = []
    L = ativo.get('leit'); r = ativo.get('ritmo') or 0
    for u in ('h', 'km'):
        if not serv['gat'].get(u) or ativo.get('un') != u or not L or ref.get('leit') is None: continue
        due = ref['leit'] + serv['gat'][u]; tol = serv['tol'].get(u, 0) or 0
        idade = (H - _d(L['data'])).days
        if r > 0:
            d_due = (due - L['val']) / r - idade; d_ini = (due - tol - L['val']) / r - idade
        else:
            d_due = (-idade if L['val'] >= due else math.inf); d_ini = (-idade if L['val'] >= due - tol else math.inf)
        gats.append(dict(u=u, due=due, tol=tol, d_due=d_due, d_ini=d_ini, venc=L['val'] > due + tol, falta=due - L['val']))
    if serv['gat'].get('d'):
        due = _d(ref['data']) + datetime.timedelta(days=serv['gat']['d']); tol = serv['tol'].get('d', 0) or 0
        d_due = (due - H).days
        gats.append(dict(u='d', due=_iso(due), tol=tol, d_due=d_due, d_ini=d_due - tol, venc=(H - due).days > tol, falta=d_due))
    if not gats: return dict(sit='Sem gatilho', gats=[], prim=None, prev=None)
    prim = min(range(len(gats)), key=lambda i: (gats[i]['d_due'], i))
    sit = 'Vencida' if any(g['venc'] for g in gats) else ('Vence em breve' if any(g['d_ini'] <= HORIZONTE for g in gats) else 'Em dia')
    dd = gats[prim]['d_due']
    prev = _iso(H + datetime.timedelta(days=math.floor(dd))) if dd != math.inf else None
    return dict(sit=sit, gats=gats, prim=prim, prev=prev)


def linhas():
    """Todos os vencimentos (plano publicado × ativo vinculado × serviço) da demonstração."""
    out = []
    for vk, v in VINCULOS.items():
        pid, aid = vk.split('|'); p = _plano(pid); a = ATIVOS[aid]
        for s in p['servicos']:
            ref = v['ult'].get(s['id']) or v['marco']
            out.append(dict(pid=pid, aid=aid, sid=s['id'], **vencimento(s, a, ref)))
    return out


def seed():
    planos = {}
    for p in PLANOS:
        planos[p['id']] = dict(id=p['id'], nome=p['nome'], grupo=p['grupo'], aplica=p['aplica'], estado='Ativo', versao=p['versao'],
                               servicos=p['servicos'], rasc=None, hist=[dict(v=v, at=at) for v, at in p['hist']])
    # v=2: achados vinculados (ach), solicitações de compra (seqsc), proposta de substituição (prop) e leituras a confirmar com tipo
    return dict(v=2, rev=0, hoje=HOJE, horiz=HORIZONTE, antiga=LEIT_ANTIGA, custoh=CUSTO_H, maxdia=MAX_DIA, seq=235, seqpm=11, seqsc=41,
                ativos=ATIVOS, ordem=ORDEM_ATIVOS, itens=ITENS, esp=ESPECIALIDADES, planos=planos, ordemPlanos=[p['id'] for p in PLANOS],
                vinc=VINCULOS, oms=_oms(), abast=[], ach={}, prop=False)


def js_prefixo():
    return ('const MAN0 = ' + json.dumps(seed(), ensure_ascii=False).replace('</', '<\\/') + ';\n' + JS + '\n')


JS = r'''
// ===== Cenário compartilhado da manutenção (Planos ↔ Vencimentos ↔ Ordens ↔ Abastecimentos ↔ Ativos) =====
// Um estado gravado no navegador (localStorage 'talhao-os-manutencao-v1'); sem localStorage vale só para a tela aberta.
const MAN_KEY='talhao-os-manutencao-v1'; let MAN_MEM=null;
const MAN_FASES=['A liberar','Liberadas','Em execução','Em conferência','Encerradas'];
function manClone(o){ return JSON.parse(JSON.stringify(o)); }
function manLoad(){ try{ const t=localStorage.getItem(MAN_KEY); return t?JSON.parse(t):null; }catch(e){ return null; } }
function manSave(c){ MAN_MEM=c; try{ localStorage.setItem(MAN_KEY,JSON.stringify(c)); }catch(e){} }
function manGet(){ const c=manLoad()||MAN_MEM; if(c&&c.v===MAN0.v) return c; MAN_MEM=manClone(MAN0); return MAN_MEM; }
function manReset(self){ MAN_MEM=manClone(MAN0); try{ localStorage.removeItem(MAN_KEY); }catch(e){} if(self) self.setState({manrev:Date.now(),g2toast:'Demonstração da manutenção restaurada.'}); }
// mudança atômica: aplica fn numa cópia; erro não grava nada e vira aviso
function manMudar(self,fn){ const c=manClone(manGet()); let r;
  try{ r=fn(c)||{}; }catch(e){ r={erro:String(e.message||e)}; }
  if(r.erro){ if(self) self.setState({g2toast:r.erro}); return r; }
  if(r.nada){ if(self&&r.msg) self.setState({g2toast:r.msg}); return r; }
  c.rev=(c.rev||0)+1; manSave(c); if(self) self.setState(Object.assign({manrev:c.rev,g2toast:r.msg||''},r.st||{})); return r; }
function manOuvir(self){ if(self.__manOuvindo) return; self.__manOuvindo=true;
  try{ window.addEventListener('storage',(e)=>{ if(e.key===MAN_KEY) self.setState({manrev:Date.now()}); }); }catch(e){} }
// ---------- números e datas (ISO em UTC, sem fuso) ----------
function manN(n,d){ return Number(n||0).toLocaleString('pt-BR',{minimumFractionDigits:0,maximumFractionDigits:d===undefined?0:d}); }
function manRS(n){ return 'R$ '+Number(n||0).toLocaleString('pt-BR',{minimumFractionDigits:2,maximumFractionDigits:2}); }
function manT(s){ const a=String(s).split('-'); return Date.UTC(+a[0],+a[1]-1,+a[2]); }
function manDias(a,b){ return Math.round((manT(b)-manT(a))/86400000); }
function manAdd(s,n){ return new Date(manT(s)+n*86400000).toISOString().slice(0,10); }
function manBr(s){ if(!s) return '—'; const a=String(s).split('-'); if(a.length!==3) return String(s); return a[2]+'/'+a[1]+(a[0]===String(MAN0.hoje).slice(0,4)?'':'/'+a[0]); }
function manUn(u){ return u==='d'?'dias':u; }
function manQ(v,u){ return manN(v)+' '+u; }
// número digitado em pt-BR: vírgula decimal; ponto só como milhar (2.995 = 2995; 1,5 = 1.5)
function manNum(x){ const t=String(x===undefined||x===null?'':x).trim(); if(!t) return NaN; if(t.indexOf(',')>=0) return Number(t.replace(/\./g,'').replace(',','.'));
  if(/^-?\d{1,3}(\.\d{3})+$/.test(t)) return Number(t.replace(/\./g,'')); return Number(t); }
// contexto no endereço (F5 reabre o plano ou a ordem) sem criar entrada no histórico
function manHash(h){ try{ const u=location.pathname+location.search+(h?'#'+encodeURIComponent(h).replace(/%3A/g,':'):''); if((location.hash||'').slice(1)!==(h||'')) history.replaceState(null,'',u); }catch(e){} }
// ---------- ativos, planos e serviços ----------
function manAtv(c,aid){ return c.ativos[aid]||null; }
function manNome(a){ return a? a.nome+(a.classe==='Trator'?' · '+a.modelo:'') : '—'; }
function manPub(p){ return p.versao?p.servicos:[]; }               // vencimentos usam só a versão publicada
function manWork(p){ return p.rasc?p.rasc.servicos:p.servicos; }    // o que se edita (rascunho ou v1 ainda não publicada)
function manGatTxt(s){ const g=s.gat||{}; const t=[]; if(g.h) t.push(manN(g.h)+' h'); if(g.km) t.push(manN(g.km)+' km'); if(g.d) t.push(manN(g.d)+' dias'); return t.length?('a cada '+t.join(' ou ')):'sem gatilho'; }
function manTolTxt(s){ const g=s.gat||{}, o=s.tol||{}; const t=[]; if(g.h) t.push('± '+manN(o.h||0)+' h'); if(g.km) t.push('± '+manN(o.km||0)+' km'); if(g.d) t.push('± '+manN(o.d||0)+' dias'); return t.join(' · '); }
function manCabe(c,p,a){ return p.aplica.t==='modelo'? p.aplica.v.indexOf(a.modelo)>=0 : p.aplica.v.indexOf(a.id)>=0; }
function manAplTxt(c,p){ if(p.aplica.t==='modelo') return (p.aplica.v.length>1?'Modelos ':'Modelo ')+p.aplica.v.join(' e ');
  const n=p.aplica.v.map(id=>(c.ativos[id]||{}).nome).filter(Boolean); return n.length>2?(n.length+' ativos'):n.join(' e '); }
function manRef(v,sid){ return (v.ult&&v.ult[sid])||v.marco; }
function manCiclo(pid,aid,sid,ref){ return pid+'|'+aid+'|'+sid+'@'+ref.data+'|'+(ref.leit===null||ref.leit===undefined?'':ref.leit); }
// ---------- vencimento: o que vencer primeiro (mesma fórmula do dados_manutencao.vencimento) ----------
function manVenc(c,s,a,ref){ const H=c.hoje, L=a.leit, r=a.ritmo||0, gats=[];
  ['h','km'].forEach(u=>{ if(!s.gat[u]||a.un!==u||!L||ref.leit===null||ref.leit===undefined) return;
    const due=ref.leit+s.gat[u], tol=(s.tol&&s.tol[u])||0, idade=manDias(L.data,H); let dd, di;
    if(r>0){ dd=(due-L.val)/r-idade; di=(due-tol-L.val)/r-idade; } else { dd=L.val>=due?-idade:Infinity; di=L.val>=due-tol?-idade:Infinity; }
    gats.push({u,due,tol,dd,di,venc:L.val>due+tol,falta:due-L.val}); });
  if(s.gat.d){ const due=manAdd(ref.data,s.gat.d), tol=(s.tol&&s.tol.d)||0, dd=manDias(H,due); gats.push({u:'d',due,tol,dd,di:dd-tol,venc:manDias(due,H)>tol,falta:dd}); }
  if(!gats.length) return {sit:'Sem gatilho',gats:[],prim:null,prev:null};
  let prim=0; gats.forEach((g,i)=>{ if(g.dd<gats[prim].dd) prim=i; });
  const sit=gats.some(g=>g.venc)?'Vencida':(gats.some(g=>g.di<=c.horiz)?'Vence em breve':'Em dia');
  const dd=gats[prim].dd; return {sit,gats,prim,prev:(dd===Infinity?null:manAdd(H,Math.floor(dd)))}; }
const MAN_SITC={'Vencida':'red','Vence em breve':'yellow','Em dia':'green','Sem gatilho':'gray','Aguarda publicar':'gray','Plano inativo':'gray'};
function manProxTxt(c,x){ const g=x.gats[x.prim]; if(!g) return '—';
  if(g.u==='d') return manBr(g.due); return manQ(g.due,g.u)+(x.prev?(g.dd<0?' · passou ≈ ':' ≈ ')+manBr(x.prev):''); }
// situação curta (o vencimento em si já está na coluna Próximo vencimento)
function manSitTxt(c,x){ const g=x.gats[x.prim]; if(!g) return x.sit;
  if(x.sit==='Vencida'){ const v=x.gats.find(y=>y.venc); return v.u==='d'?('Vencida desde '+manBr(v.due)):('Vencida · '+manQ(-v.falta,v.u)+' além'); }
  return x.sit; }
function manPrimTxt(x){ const g=x.gats[x.prim]; if(!g||x.gats.length<2) return ''; return g.u==='d'?'o calendário vence primeiro':(g.u==='h'?'o horímetro vence primeiro':'o odômetro vence primeiro'); }
function manLeitTxt(a){ if(!a||!a.leit) return 'sem contador'; return manQ(a.leit.val,a.un)+' · '+manBr(a.leit.data); }
function manAntiga(c,a){ return !!(a&&a.leit&&manDias(a.leit.data,c.hoje)>c.antiga); }
// ---------- ordens ----------
function manAberta(o){ return o.etapa!=='Encerradas'; }
function manOmCiclo(c,pid,aid,sid,ciclo){ return Object.values(c.oms).find(o=>o.pid===pid&&o.aid===aid&&(o.cobre||[]).indexOf(sid)>=0&&(o.ciclos||{})[sid]===ciclo)||null; }
function manFalta(c,o){ return (o.pecas||[]).filter(p=>p.item&&!p.res&&o.etapa==='A liberar'&&((c.itens[p.item].saldo-c.itens[p.item].reservado)<p.qtd)); }
// todas as linhas plano × ativo × serviço (publicado), com cálculo, ordem do ciclo e selos
function manLinhas(c,pid){ const out=[];
  Object.keys(c.vinc).forEach(vk=>{ const v=c.vinc[vk]; const k=vk.split('|'); if(pid&&k[0]!==pid) return; const p=c.planos[k[0]], a=c.ativos[k[1]]; if(!p||!a) return;
    const ss=manPub(p); if(!ss.length){ out.push({vk,pid:p.id,aid:a.id,sid:'',p,a,s:null,x:{sit:'Aguarda publicar',gats:[],prim:null,prev:null},ref:v.marco,om:null}); return; }
    ss.forEach(s=>{ const ref=manRef(v,s.id); const x=p.estado==='Inativo'?{sit:'Plano inativo',gats:[],prim:null,prev:null}:manVenc(c,s,a,ref);
      const ciclo=manCiclo(p.id,a.id,s.id,ref); const om=manOmCiclo(c,p.id,a.id,s.id,ciclo);
      // mesmo serviço do mesmo ativo já aberto por outro plano: não gera ordem em dobro
      const dup=om?null:(Object.values(c.oms).find(o=>o.tipo==='Preventiva'&&o.aid===a.id&&o.pid&&o.pid!==p.id&&manAberta(o)&&String(o.serv).toLowerCase()===String(s.nome).toLowerCase())||null);
      out.push({vk,pid:p.id,aid:a.id,sid:s.id,p,a,s,x,ref,ciclo,om,dup,est:!!(v.marco&&v.marco.est&&!(v.ult||{})[s.id])}); }); });
  return out; }
function manDevida(l){ return l.x.sit==='Vencida'||l.x.sit==='Vence em breve'; }
function manSemOm(c){ return manLinhas(c).filter(l=>manDevida(l)&&!l.om&&!l.dup); }
// outro plano ativo, ligado ao mesmo ativo, com serviço de mesmo nome (um serviço por ativo)
function manDupServ(c,pid,aid,nomes){ const ns=nomes.map(x=>String(x).toLowerCase());
  for(const k of Object.keys(c.vinc)){ const q=k.split('|'); if(q[1]!==aid||q[0]===pid) continue; const o=c.planos[q[0]]; if(!o||o.estado==='Inativo') continue;
    const s=manWork(o).concat(manPub(o)).find(x=>ns.indexOf(String(x.nome).toLowerCase())>=0); if(s) return {pid:o.id,s:s.nome}; }
  return null; }
function manSelosLinha(c,l){ const s=[]; if(l.a.cond==='Bloqueado'){ const ob=Object.values(c.oms).find(o=>o.aid===l.a.id&&o.tipo==='Corretiva'&&manAberta(o)); s.push({t:'Ativo bloqueado'+(ob?' · '+ob.id:''),c:'red'}); }
  if(manAntiga(c,l.a)) s.push({t:'Leitura de '+manBr(l.a.leit.data),c:'yellow'}); if(l.a.suspeita) s.push({t:'Leitura a confirmar',c:'yellow'}); if(l.est) s.push({t:'Marco estimado',c:'yellow'}); return s; }
// gerar: uma OM por ativo × serviço × ciclo; serviço maior que "cumpre também" e também está devido gera uma só OM
function manGerar(c,vk,sid){ const k=vk.split('|'); const p=c.planos[k[0]], a=c.ativos[k[1]], v=c.vinc[vk]; if(!p||!a||!v) throw new Error('Vínculo não encontrado.');
  const ls=manLinhas(c,p.id).filter(l=>l.aid===a.id); let l=ls.find(x=>x.sid===sid); if(!l) throw new Error('Serviço não está na versão publicada.');
  const maior=ls.find(x=>x.s&&(x.s.cumpre||[]).indexOf(sid)>=0&&manDevida(x)); if(maior) l=maior;
  if(l.om) return {nada:true,msg:'Já existe a '+l.om.id+' para este ciclo · nenhuma ordem nova.',id:l.om.id};
  if(l.dup) return {nada:true,msg:manNome(a)+' · '+l.s.nome+' já está na '+l.dup.id+' ('+l.dup.pid+') · nenhuma ordem nova.',id:l.dup.id};
  if(!manDevida(l)) throw new Error(a.nome+' · '+l.s.nome+' está em dia; gere a ordem quando a janela se aproximar.');
  const s=l.s; const id='OM-'+String(c.seq).padStart(4,'0'); c.seq++;
  const cobre=[s.id].concat(s.cumpre||[]); const ciclos={}; cobre.forEach(x=>{ ciclos[x]=manCiclo(p.id,a.id,x,manRef(v,x)); });
  const g=l.x.gats[l.x.prim]; const vq=l.x.gats.find(y=>y.venc)||g;
  const ciclo=g.u==='d'?('vence '+manBr(g.due)):(manQ(g.due,g.u)+' ('+manN(s.gat[g.u])+' '+g.u+' após '+manQ(l.ref.leit,g.u)+')');
  const jan=l.x.sit==='Vencida'?manBr(manAdd(c.hoje,1)):(l.x.prev?manBr(l.x.prev):manBr(manAdd(c.hoje,1)));
  c.oms[id]={id,tipo:'Preventiva',aid:a.id,pid:p.id,sid:s.id,ver:p.versao,cobre,ciclos,serv:s.nome,crit:l.x.sit==='Vencida'?'Alta':'Média',etapa:'A liberar',
    origem:p.id+' v'+p.versao+' · '+s.nome+' · '+ciclo,jan,ret:jan,esp:s.esp,tempo:s.tempo,chk:s.tarefas.map(t=>({t,r:'',mot:''})),
    pecas:(s.pecas||[]).map(x=>{ const it=c.itens[x.item]; return {item:x.item,nome:it.nome,un:it.un,qtd:x.qtd,res:0,apl:0,sob:0,preco:it.preco}; }),exec:null,selos:[]};
  const falta=manFalta(c,c.oms[id]);
  return {id,msg:id+' gerada para '+manNome(a)+' · '+s.nome+(maior?' (cumpre também '+ls.find(x=>x.sid===sid).s.nome+')':'')+(falta.length?' · Falta peça: '+falta.map(x=>x.nome).join(', '):'')+'.'}; }
function manGerarTodas(c){ const ids=[]; let n=0;
  manSemOm(c).forEach(l=>{ const cur=manLinhas(c,l.pid).find(x=>x.aid===l.aid&&x.sid===l.sid); if(!cur||cur.om) return; const r=manGerar(c,l.vk,l.sid); if(r.id&&!r.nada){ ids.push(r.id); n++; } });
  if(!n) return {nada:true,msg:'Nenhuma ordem a gerar: todos os vencimentos próximos já têm ordem.'};
  const fp=ids.filter(id=>manFalta(c,c.oms[id]).length);
  return {msg:n+(n>1?' ordens preventivas geradas: ':' ordem preventiva gerada: ')+ids.join(', ')+' · em A liberar'+(fp.length?' · '+fp.join(', ')+' com Falta peça':'')+'.',ids}; }
// selos da ordem: condição, nunca coluna
function manSelos(c,o){ const s=[]; const a=c.ativos[o.aid];
  if(manFalta(c,o).length) s.push({t:'Falta peça',c:'red'});
  if(o.sc&&manFalta(c,o).length) s.push({t:'Compra '+o.sc.id,c:'yellow'});
  if(o.conflito&&manAberta(o)&&o.etapa!=='Em conferência') s.push(o.conflitoAceito?{t:'Conflito aceito · '+o.conflito.os,c:'yellow'}:{t:'Conflito · '+o.conflito.os,c:'red'});
  if(o.tipo==='Preventiva'&&o.pid&&['A liberar','Liberadas','Em execução'].indexOf(o.etapa)>=0){ const l=manLinhas(c,o.pid).find(x=>x.aid===o.aid&&x.sid===o.sid&&x.om&&x.om.id===o.id); if(l&&l.x.sit==='Vencida') s.push({t:'Vencida',c:'red'}); }
  if(a&&a.cond==='Bloqueado'&&manAberta(o)) s.push({t:'Ativo bloqueado',c:'red'});
  if((o.pecas||[]).some(p=>p.sob>0)) s.push({t:'Sobras a resolver',c:'yellow'});
  (o.pend||[]).forEach(id=>s.push({t:'Pendência '+id,c:'yellow'}));
  if(o.de) s.push({t:'Pendência da '+o.de,c:'yellow'});
  return s; }
// liberar: falta de peça bloqueia (estoque); conflito com a produção é aviso confirmado
function manLiberar(c,id,forcar){ const o=c.oms[id]; if(!o) throw new Error('Ordem não encontrada.'); if(o.etapa!=='A liberar') throw new Error(id+' não está em A liberar.');
  const f=manFalta(c,o); if(f.length) throw new Error('Não liberada: falta peça · '+f.map(x=>x.nome+' ('+manN(c.itens[x.item].saldo-c.itens[x.item].reservado)+' de '+manN(x.qtd)+' '+x.un+')').join(', ')+(o.sc?'. Aguarda o recebimento da '+o.sc.id+'.':'. Solicite a compra.'));
  if(o.conflito&&!forcar) return {nada:true,aviso:true,msg:o.conflito.t+'.'};
  (o.pecas||[]).forEach(p=>{ if(!p.item) return; c.itens[p.item].reservado+=p.qtd; p.res=p.qtd; });
  o.etapa='Liberadas'; if(o.conflito) o.conflitoAceito=true;
  const pr=(o.pecas||[]).filter(p=>p.item).map(p=>p.nome+' '+manN(p.qtd)+' '+p.un);
  return {msg:id+' liberada para a oficina'+(pr.length?' · reservado: '+pr.join(', '):'')+(o.conflito?' · conflito com a '+o.conflito.os+' enviado ao PCP':'')+'.'}; }
// falta de peça: a ordem pede a compra (SC) e libera quando o almoxarifado recebe; uma SC por ordem
function manSolicitar(c,id){ const o=c.oms[id]; if(!o) throw new Error('Ordem não encontrada.'); if(o.sc) return {nada:true,msg:'A '+o.sc.id+' já foi enviada a Suprimentos.'};
  const f=manFalta(c,o); if(!f.length) return {nada:true,msg:'Nenhuma peça em falta nesta ordem.'};
  const sc='SC-'+String(c.seqsc||41).padStart(3,'0'); c.seqsc=(c.seqsc||41)+1;
  o.sc={id:sc,data:c.hoje,itens:f.map(p=>{ const it=c.itens[p.item]; return {item:p.item,nome:p.nome,un:p.un,qtd:Math.max(0,p.qtd-Math.max(0,it.saldo-it.reservado))}; })};
  return {msg:sc+' enviada a Suprimentos: '+o.sc.itens.map(x=>x.nome+' '+manN(x.qtd,1)+' '+x.un).join(', ')+' · a '+id+' libera quando a peça chegar.'}; }
function manReceber(c,id){ const o=c.oms[id]; if(!o||!o.sc) throw new Error('Esta ordem não tem compra solicitada.'); if(o.sc.rec) return {nada:true,msg:'Recebimento da '+o.sc.id+' já registrado.'};
  o.sc.itens.forEach(x=>{ c.itens[x.item].saldo+=x.qtd; }); o.sc.rec=c.hoje;
  return {msg:'Recebimento da '+o.sc.id+' no almoxarifado (simulado): '+o.sc.itens.map(x=>x.nome+' '+manN(x.qtd,1)+' '+x.un).join(', ')+' · '+id+' pronta para liberar.'}; }
function manIniciar(c,id){ const o=c.oms[id]; if(!o||o.etapa!=='Liberadas') throw new Error(id+' não está em Liberadas.'); o.etapa='Em execução'; o.ini=c.hoje;
  return {msg:id+' Em execução · responda o checklist e informe a leitura do contador para concluir.'}; }
// resposta item a item (PRD 54.2: não pré-marcar; registra usuário/papel e momento)
// a resposta guarda quem respondeu; editar só o motivo não troca esse autor e grava à parte quem editou (revisão do CTL-3, achado 2; dano
// evitado: a trilha dizer que outra pessoa decidiu que o item não foi feito, e o registro de quem respondeu se perder)
function manResp(c,id,i,r,mot,ator){ const o=c.oms[id]; if(!o||o.etapa!=='Em execução') throw new Error('Responda o checklist com a ordem Em execução.'); const t=o.chk[i];
  const d=new Date(), hr=('0'+d.getHours()).slice(-2)+':'+('0'+d.getMinutes()).slice(-2), quem=ator?g2ator(ator,'mecanico'):'';
  if((t.r||'')!==(r||'')){ t.r=r; t.por=r?quem:''; t.em=r?hr:''; }
  if(mot!==undefined&&mot!==(t.mot||'')){ t.mot=mot; t.motPor=quem; t.motEm=hr; } return {msg:''}; }
// leitura acima do fisicamente possível desde a última (zero a mais, dedo errado): aviso a confirmar, nunca bloqueio
function manPlaus(c,a,n){ if(!a||!a.un||!a.leit||isNaN(n)) return ''; const md=(c.maxdia||{h:24,km:1500})[a.un]||24;
  const dias=Math.max(1,manDias(a.leit.data,c.hoje)); const lim=dias*md, d=n-a.leit.val;
  return d>lim?('Leitura de '+manQ(n,a.un)+' fica '+manQ(d,a.un)+' acima da última ('+manLeitTxt(a)+'), mais que '+manQ(lim,a.un)+' possíveis em '+dias+(dias>1?' dias':' dia')):''; }
// "Próximo ciclo conta de: vencimento programado" — a referência é o vencimento (data e leitura), não a execução
function manRefProg(c,s,a,r0,L){ const g=s.gat||{}; const out={data:c.hoje,leit:L};
  if(g.d) out.data=manAdd(r0.data,g.d);
  ['h','km'].forEach(u=>{ if(g[u]&&a&&a.un===u&&r0.leit!==null&&r0.leit!==undefined) out.leit=r0.leit+g[u]; });
  return out; }
// concluir (término físico): exige checklist respondido e leitura do contador; fecha o ciclo sem zerar o horímetro
// apl = {índice da peça: quantidade aplicada} (vazio = planejado); aplicado < planejado vira sobra a devolver
function manConcluir(c,id,leit,horas,forcar,apl){ const o=c.oms[id]; if(!o||o.etapa!=='Em execução') throw new Error(id+' não está Em execução.'); const a=c.ativos[o.aid];
  const sem=o.chk.filter(t=>!t.r); if(sem.length) throw new Error('Responda o checklist: '+sem.length+(sem.length>1?' tarefas sem resposta.':' tarefa sem resposta.'));
  const smot=o.chk.filter(t=>t.r!=='Feito'&&!String(t.mot||'').trim()); if(smot.length) throw new Error('Informe o motivo de “'+smot[0].t+'”.');
  let L=null; if(a&&a.un){ L=manNum(leit); if(String(leit===undefined||leit===null?'':leit).trim()===''||isNaN(L)) throw new Error('Informe a leitura do '+(a.un==='km'?'odômetro':'horímetro')+' na conclusão.');
    if(a.leit&&L<a.leit.val) throw new Error('Leitura menor que a última registrada ('+manLeitTxt(a)+')'+(a.suspeita&&a.suspeita.tipo==='menor'?' · confirme antes a troca de contador em Abastecimentos ('+a.suspeita.ab+').':'. Confira o contador.')); }
  const hh=(horas===undefined||horas===null||String(horas).trim()==='')?o.tempo:manNum(horas); if(isNaN(hh)||hh<0||hh>200) throw new Error('Horas de oficina inválidas.');
  const qa=(o.pecas||[]).map((p,i)=>{ const t=apl&&apl[i]!==undefined?String(apl[i]).trim():''; const q=t===''?p.qtd:manNum(t);
    if(isNaN(q)||q<0) throw new Error('Quantidade aplicada inválida: '+p.nome+'.');
    if(p.item&&q>p.qtd){ const it=c.itens[p.item]; const disp=it.saldo-it.reservado; if(q-p.qtd>disp) throw new Error('Saldo insuficiente de '+p.nome+' para aplicar '+manN(q,1)+' '+p.un+' (disponível além do reservado: '+manN(Math.max(0,disp),1)+' '+p.un+').'); }
    return q; });
  if(L!==null&&!forcar){ const pl=manPlaus(c,a,L); if(pl) return {nada:true,avisoLeit:true,msg:pl+'. Confira o contador.'}; }
  // baixa: sai do estoque o que foi requisitado (planejado) ou o aplicado, se maior; o que sobrou volta pelo recibo de sobras
  (o.pecas||[]).forEach((p,i)=>{ const q=qa[i]; if(!p.item){ p.apl=q; p.sob=0; return; } const it=c.itens[p.item];
    it.saldo=Math.max(0,it.saldo-Math.max(p.qtd,q)); it.reservado=Math.max(0,it.reservado-(p.res||0)); p.res=0; p.apl=q; p.sob=Math.max(0,p.qtd-q); });
  // ciclos: a referência nova sai antes de mudar a leitura do ativo (vencimento programado usa a referência antiga)
  const v=o.pid?c.vinc[o.pid+'|'+o.aid]:null; const pl=o.pid?c.planos[o.pid]:null; const novos={}; let prog=false;
  if(v){ (o.cobre||[o.sid]).forEach(sid=>{ const s=pl?manPub(pl).find(x=>x.id===sid):null;
    if(s&&s.base==='prog'){ const r=manRefProg(c,s,a,manRef(v,sid),L); novos[sid]={data:r.data,leit:r.leit,om:id,prog:true}; prog=true; }
    else novos[sid]={data:c.hoje,leit:L,om:id}; }); }
  o.exec={data:c.hoje,leit:L,horas:hh}; o.etapa='Em conferência';
  if(a&&L!==null&&(!a.leit||L>=a.leit.val)){ if(a.suspeita){ const e=(c.abast||[]).find(x=>x.id===a.suspeita.ab); if(e) e.res='Substituída'; delete a.suspeita; } a.leit={val:L,data:c.hoje,origem:'Execução '+id}; }
  let prox='';
  if(v){ v.ult=v.ult||{}; Object.keys(novos).forEach(sid=>{ v.ult[sid]=novos[sid]; });
      const l=manLinhas(c,o.pid).find(x=>x.aid===o.aid&&x.sid===o.sid); if(l) prox=' · ciclo fechado: próxima '+l.s.nome+' em '+manProxTxt(c,l.x)+' ('+l.x.sit.toLowerCase()+')'+(prog?' · conta do vencimento programado':''); }
  const sb=(o.pecas||[]).filter(p=>p.sob>0); if(sb.length) prox+=' · sobra a devolver: '+sb.map(p=>manN(p.sob,1)+' '+p.un+' '+p.nome).join(', ');
  const nf=o.chk.filter(t=>t.r==='Não feito'); o.pend=[];
  nf.forEach(t=>{ const pid='OM-'+String(c.seq).padStart(4,'0'); c.seq++; o.pend.push(pid);
    c.oms[pid]={id:pid,tipo:'Pendência',aid:o.aid,serv:t.t,crit:'Média',etapa:'A liberar',origem:'Pendência da '+id+' · '+t.mot,de:id,jan:manBr(manAdd(c.hoje,1)),ret:'—',esp:o.esp,tempo:1,chk:[{t:t.t,r:'',mot:''}],pecas:[],exec:null,selos:[]}; });
  return {msg:id+' em conferência'+prox+(o.pend.length?' · '+o.pend.join(', ')+' aberta para o que não foi feito':'')+(a&&a.cond==='Bloqueado'?' · o ativo segue bloqueado até a decisão de aptidão':'')+'.'}; }
function manSobras(c,id){ const o=c.oms[id]; if(!o) throw new Error('Ordem não encontrada.'); const sb=(o.pecas||[]).filter(p=>p.sob>0); if(!sb.length) return {nada:true,msg:'Sem sobras nesta ordem.'};
  const rc='AL-'+(412+Object.values(c.oms).filter(x=>x.recibo).length); sb.forEach(p=>{ if(p.item) c.itens[p.item].saldo+=p.sob; p.dev=(p.dev||0)+p.sob; p.sob=0; }); o.recibo=rc;
  return {msg:'Sobras da '+id+' devolvidas ao Almoxarifado Sede com recibo '+rc+' · '+sb.map(p=>manN(p.dev)+' '+p.un+' '+p.nome).join(', ')+'.'}; }
function manCusto(c,o){ return (o.pecas||[]).reduce((s,p)=>s+(p.apl||0)*(p.preco||0),0)+((o.exec&&o.exec.horas)||0)*c.custoh; }
function manEncerrar(c,id){ const o=c.oms[id]; if(!o||o.etapa!=='Em conferência') throw new Error(id+' não está Em conferência.');
  if((o.pecas||[]).some(p=>p.sob>0)) throw new Error('Resolva as sobras antes de encerrar.');
  o.custo=manCusto(c,o); o.etapa='Encerradas'; return {msg:id+' encerrada · custo '+manRS(o.custo)+' (peças + '+manN((o.exec||{}).horas||0,1)+' h × R$ '+c.custoh+'/h) · aptidão do ativo decidida à parte.'}; }
// leitura do contador (abastecimento, apontamento, telemetria): menor que a anterior é evento a confirmar, nunca uso negativo
// ab = lançamento de origem (AB-xxxx): a leitura a confirmar fica presa a ele, com Confirmar e Descartar no MA-05
function manLeitura(c,aid,val,origem,ab){ const a=c.ativos[aid]; if(!a||!a.un) return {msg:''}; const n=Number(val); if(isNaN(n)) return {msg:''};
  const prev=()=>{ if(a.suspeita){ const e=(c.abast||[]).find(x=>x.id===a.suspeita.ab); if(e) e.res='Substituída'; } };
  if(a.leit&&n<a.leit.val){ prev(); a.suspeita={val:n,data:c.hoje,origem,ab,tipo:'menor'}; return {sus:'menor',msg:'Leitura de '+manQ(n,a.un)+' menor que a anterior ('+manLeitTxt(a)+') · confirme a troca de contador ou descarte; os vencimentos seguem na leitura anterior.'}; }
  const pl=manPlaus(c,a,n); if(pl){ prev(); a.suspeita={val:n,data:c.hoje,origem,ab,tipo:'alta'}; return {sus:'alta',msg:pl+' · confirme ou descarte; os vencimentos seguem na leitura anterior.'}; }
  prev(); const antes=manLinhas(c).filter(l=>l.aid===aid&&l.s).map(l=>l.x.sit); a.leit={val:n,data:c.hoje,origem}; delete a.suspeita;
  const dep=manLinhas(c).filter(l=>l.aid===aid&&l.s); const mud=dep.filter((l,i)=>l.x.sit!==antes[i]);
  return {msg:manNome(a)+' em '+manQ(n,a.un)+(mud.length?' · '+mud.map(l=>l.s.nome+': '+l.x.sit.toLowerCase()).join(' · '):' · vencimentos recalculados')+'.'}; }
// confirmar: leitura alta vira a leitura atual; leitura menor é troca de contador — o histórico do ativo passa à escala do contador novo
function manLeituraOk(c,aid){ const a=c.ativos[aid]; const s=a&&a.suspeita; if(!s) throw new Error('Nenhuma leitura a confirmar.'); const e=(c.abast||[]).find(x=>x.id===s.ab);
  const antes=manLinhas(c).filter(l=>l.aid===aid&&l.s).map(l=>l.x.sit);
  if(s.tipo==='menor'){ const delta=a.leit.val-s.val; const ck=()=>{ const m={}; manLinhas(c).filter(l=>l.aid===aid&&l.s).forEach(l=>{ m[l.vk+'#'+l.sid]=l.ciclo; }); return m; };
    const c0=ck(); const sh=(r)=>{ if(r&&r.leit!==null&&r.leit!==undefined) r.leit=r.leit-delta; };
    Object.keys(c.vinc).filter(k=>k.split('|')[1]===aid).forEach(k=>{ const v=c.vinc[k]; sh(v.marco); Object.values(v.ult||{}).forEach(sh); });
    (a.trocas=a.trocas||[]).push({data:c.hoje,de:a.leit.val,para:s.val,ab:s.ab}); a.leit={val:s.val,data:c.hoje,origem:'Troca de contador · '+(s.ab||s.origem)}; delete a.suspeita;
    const c1=ck(); Object.values(c.oms).filter(o=>o.aid===aid&&o.ciclos&&o.pid).forEach(o=>{ Object.keys(o.ciclos).forEach(sid=>{ const k=o.pid+'|'+aid+'#'+sid; if(c0[k]&&o.ciclos[sid]===c0[k]) o.ciclos[sid]=c1[k]; }); });
    if(e) e.res='Troca confirmada';
    return {msg:'Troca de contador confirmada: '+manNome(a)+' passa a '+manQ(s.val,a.un)+' · histórico ajustado em '+manQ(delta,a.un)+' · vencimentos mantidos.'}; }
  a.leit={val:s.val,data:c.hoje,origem:s.origem}; delete a.suspeita; if(e) e.res='Leitura confirmada';
  const dep=manLinhas(c).filter(l=>l.aid===aid&&l.s); const mud=dep.filter((l,i)=>l.x.sit!==antes[i]);
  return {msg:'Leitura confirmada: '+manNome(a)+' em '+manQ(s.val,a.un)+(mud.length?' · '+mud.map(l=>l.s.nome+': '+l.x.sit.toLowerCase()).join(' · '):' · vencimentos recalculados')+'.'}; }
function manLeituraDescartar(c,aid){ const a=c.ativos[aid]; const s=a&&a.suspeita; if(!s) throw new Error('Nenhuma leitura a confirmar.'); const e=(c.abast||[]).find(x=>x.id===s.ab);
  delete a.suspeita; if(e) e.res='Leitura descartada';
  return {msg:'Leitura de '+manQ(s.val,a.un)+' descartada'+(s.ab?' ('+s.ab+')':'')+' · '+manNome(a)+' segue em '+manLeitTxt(a)+'.'}; }
// acesso para os testes de navegador (mesmo padrão do window.__cen da O.S.)
try { window.__man = { manGet, manClone, manLinhas, manVenc, manGerar, manGerarTodas, manLiberar, manConcluir, manReset, manLeitura, manLeituraOk, manLeituraDescartar, manSolicitar, manReceber, manPlaus, manNum }; } catch (e) {}
'''


if __name__ == '__main__':
    # autoteste com os números do desenho (passo 1)
    L = {(x['pid'], x['aid'], x['sid']): x for x in linhas()}
    def sit(pid, aid, sid='s1'): return L[(pid, aid, sid)]['sit']
    esperado = {('PM-01', 'a02', 's1'): 'Vence em breve', ('PM-01', 'a02', 's2'): 'Em dia', ('PM-02', 'a03', 's1'): 'Vencida',
                ('PM-03', 'a01', 's1'): 'Em dia', ('PM-03', 'a04', 's1'): 'Em dia', ('PM-04', 'a05', 's1'): 'Em dia', ('PM-04', 'a05', 's2'): 'Em dia',
                ('PM-05', 'a06', 's1'): 'Vencida', ('PM-06', 'a08', 's1'): 'Em dia', ('PM-07', 'a11', 's1'): 'Vence em breve',
                ('PM-07', 'a15', 's1'): 'Em dia', ('PM-08', 'a13', 's1'): 'Em dia', ('PM-09', 'a14', 's1'): 'Em dia', ('PM-10', 'cb01', 's1'): 'Em dia'}
    erros = [(k, L[k]['sit'], v) for k, v in esperado.items() if L[k]['sit'] != v]
    t2 = L[('PM-01', 'a02', 's1')]; assert t2['gats'][t2['prim']]['due'] == 3043 and t2['prev'] == '2026-09-28', t2
    t3 = L[('PM-02', 'a03', 's1')]; assert t3['gats'][0]['due'] == 5090 and -t3['gats'][0]['falta'] == 30, t3
    co = L[('PM-06', 'a08', 's1')]; assert co['gats'][co['prim']]['u'] == 'd' and co['prev'] == '2026-10-15', co
    cb = L[('PM-10', 'cb01', 's1')]; assert cb['gats'][cb['prim']]['u'] == 'km' and cb['prev'] == '2026-10-15', cb
    b2 = L[('PM-07', 'a11', 's1')]; assert b2['gats'][b2['prim']]['u'] == 'd' and b2['prev'] == '2026-10-01', b2
    pl = L[('PM-05', 'a06', 's1')]; assert pl['gats'][0]['due'] == '2026-09-20', pl
    devidas = [k for k, x in L.items() if x['sit'] in ('Vencida', 'Vence em breve')]
    assert not erros, erros
    assert len(devidas) == 4, devidas
    sem_plano = [a['nome'] for aid, a in ATIVOS.items() if not any(k.split('|')[1] == aid for k in VINCULOS)]
    assert sem_plano == ['Distribuidor 3 t', 'Máquina TSI', 'Esqueletadeira', 'Gotejo T7'], sem_plano
    print('autoteste ok ·', len(L), 'vencimentos ·', len(devidas), 'devidos ·', 'sem plano:', ', '.join(sem_plano))
