# -*- coding: utf-8 -*-
"""Manutenção · estado e regras num só lugar (PCM simplificado v2, docs/pcm-simplificado/ESPECIFICACAO.md).

Fonte única dos dados de demonstração e das regras da manutenção (tela MA, CD-03, O.S. e app):
- ativos com a identidade do CD-03 (dados_cad.ATIVOS) + Comboio CB-01; leitura, ritmo, condição única com histórico e responsável técnico (D-49);
- planos PM-01..PM-10 com tarefas tipadas (D-11: {t, tipo}), vínculos e vencimento ("o que vencer primeiro");
- ordens (OM) com executante (D-37), versão do registro o.rv (D-46), tarefas por tipo, Teste com tentativas (D-36), peças retiradas (D-13);
- histórico encerrado sintético a partir de VINCULOS.ult (D-43), custo pela função única manCusto;
- achados (c.achados, D-09/D-45/D-48), leituras com histórico (c.leituras, D-40), abastecimentos (c.abast, D-15/D-19) e recibos (c.recibos, D-30);
- conflito com a produção calculado sobre a alocação da semana (alocacao.py, a mesma de O.S. › Recursos; D-38);
- matriz papel × comando (D-33): Otávio (PCM), Zé (mecânico), Ana (gestora), pelo perfil de demonstração (g2lib G2_PERFIS).
Hoje da demonstração: 23/09/2026. "Em breve" = a janela (vencimento − tolerância) começa em até 10 dias.
vencimento() é a mesma fórmula do manVenc() do JS (paridade conferida em ma_regras_test.py e ma_planos_test.py).
Estado v=4 (S2): estado salvo de versão antiga volta ao seed (D-47). Desde o 1a, o estado vive em c.man do cenário único (cenario.py v=4)."""
import json, math, datetime
import dados_cad as DC
import alocacao as AL

HOJE = '2026-09-23'
HORIZONTE = 10          # dias: "em breve" (início da janela)
LEIT_ANTIGA = 7         # dias: leitura antiga vira aviso
CUSTO_H = 320           # Custo R$/h da oficina (hipótese da OM-0233; DEC-0510-02)
# leitura implausível (aviso a confirmar, nunca bloqueio fora da conclusão): mais que 24 h por dia no horímetro ou 1.500 km por dia no odômetro
MAX_DIA = {'h': 24, 'km': 1500}
V = 4

# ---------- ativos: identidade do CD-03 + contador, leitura, ritmo, condição e responsável técnico ----------
# un: 'h' horímetro · 'km' odômetro · '' sem contador (só calendário) · lh: referência de consumo (L/h) para o desvio
EXTRA = {
 'a01': dict(un='h', leit=(4312, '2026-09-23', 'Inspeção INSP-105'), ritmo=9, cond='Bloqueado'),
 'a02': dict(un='h', leit=(2988, '2026-09-23', 'Abastecimento AB-1042'), ritmo=11, cond='Apto', lh=15.0),
 'a03': dict(un='h', leit=(5120, '2026-09-22', 'Apontamento de turno'), ritmo=10, cond='Apto'),
 'a04': dict(un='h', leit=(3410, '2026-09-12', 'Apontamento de turno'), ritmo=4, cond='Apto'),
 'a05': dict(un='h', leit=(1542, '2026-09-23', 'Abastecimento AB-1041'), ritmo=9, cond='Apto', lh=19.0),
 'a06': dict(un='h', leit=(886, '2026-09-20', 'Apontamento de turno'), ritmo=0, cond='Apto'),
 'a07': dict(un='h', leit=(640, '2026-09-18', 'Apontamento de turno'), ritmo=1, cond='Apto'),
 'a08': dict(un='h', leit=(2150, '2026-09-22', 'Abastecimento AB-1039'), ritmo=2, cond='Apto', lh=9.8),
 'a09': dict(un='h', leit=(720, '2026-09-19', 'Apontamento de turno'), ritmo=2, cond='Apto'),
 'a10': dict(un='h', leit=(310, '2026-09-15', 'Apontamento de turno'), ritmo=1, cond='Apto'),
 'a15': dict(un='h', leit=(7650, '2026-09-23', 'Telemetria'), ritmo=11, cond='Apto'),
 'a11': dict(un='h', leit=(8914, '2026-09-23', 'Telemetria'), ritmo=11, cond='Restrito'),
 'a12': dict(un='h', leit=(5210, '2026-09-23', 'Telemetria'), ritmo=9, cond='Apto'),
 'a13': dict(un='h', leit=(12301, '2026-09-22', 'Apontamento de turno'), ritmo=9, cond='Apto'),
 'a14': dict(un='', leit=None, ritmo=0, cond='Apto'),
}
GRUPO = {'Trator': 'Tratores', 'Pulverizador': 'Pulverizadores', 'Plantadeira': 'Plantadeiras', 'Distribuidor': 'Implementos',
         'Colhedora': 'Colhedoras', 'Tratamento de sementes': 'Beneficiamento', 'Implemento': 'Implementos', 'Irrigação': 'Irrigação',
         'Beneficiamento': 'Beneficiamento', 'Armazenagem': 'Armazenagem', 'Veículo': 'Veículos'}
# responsável técnico do ativo (D-49; antes um mapa local do MA-01): a01, a02, a05 → Zé; a11, a15, a12 → Equipe elétrica; demais → Otávio
RT = {'a01': 'Zé', 'a02': 'Zé', 'a05': 'Zé', 'a11': 'Equipe elétrica', 'a15': 'Equipe elétrica', 'a12': 'Equipe elétrica'}
# condição semeada (CMD-18 da OM-0233; restrição da Bomba do Pivô 2 com prazo, PRD l.7720)
COND = {
 'a01': dict(motivo='Pressão hidráulica baixa · SM-0147 e INSP-105', desde='2026-09-22', por='Zé (mecânico)', evid='checklist + manômetro',
             achado='INSP-105', om='OM-0233', ate='', lim=''),
 'a11': dict(motivo='Pressão baixa recorrente', desde='2026-09-22', por='Otávio (responsável de manutenção)', evid='3 leituras de telemetria',
             achado='SM-0152', om='OM-0228', ate='2026-09-30', lim='operar só com monitoramento de pressão'),
}


def _ativos():
    out = {}
    for a in DC.ATIVOS:
        x = EXTRA[a['id']]; ci = COND.get(a['id'])
        out[a['id']] = dict(id=a['id'], nome=a['nome'], modelo=a['modelo'], classe=a['classe'], grupo=GRUPO.get(a['classe'], a['classe']),
                            local=a['local'], un=x['un'], ritmo=x['ritmo'], cond=x['cond'], lh=x.get('lh'),
                            condInfo=(dict(ci) if ci else None), rt=RT.get(a['id'], 'Otávio'),
                            condHist=([dict(cond=x['cond'], motivo=ci['motivo'], por=ci['por'], em=ci['desde'], achado=ci['achado'], om=ci['om'], ate=ci['ate'])] if ci else []),
                            leit=(dict(val=x['leit'][0], data=x['leit'][1], origem=x['leit'][2]) if x['leit'] else None))
    out['cb01'] = dict(id='cb01', nome='Comboio CB-01', modelo='caminhão comboio 6 m³', classe='Veículo', grupo='Veículos', local='Sede',
                       un='km', ritmo=80, cond='Apto', lh=None, condInfo=None, rt='Otávio', condHist=[],
                       leit=dict(val=48200, data='2026-09-23', origem='Abastecimento AB-1040'))
    return out


ATIVOS = _ativos()
ORDEM_ATIVOS = [a['id'] for a in DC.ATIVOS] + ['cb01']

# ---------- itens de estoque da manutenção (grupo Peças / Lubrificantes) · saldo próprio até o 1b ----------
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
TIPOS_TAREFA = ['Serviço', 'Verificação', 'Medição', 'Teste']
COMPONENTES = ['Motor', 'Hidráulico', 'Elétrico', 'Transmissão', 'Rodado e freios', 'Órgão de trabalho', 'Outro']

T250 = ['Trocar óleo do motor', 'Trocar filtro de óleo do motor', 'Trocar filtro de combustível', 'Limpar filtro de ar', 'Lubrificar pontos de graxa']


def _tk(tarefas):
    """D-11: tarefa texto → {t, tipo}; o padrão é Serviço (a preventiva segue a versão do plano)."""
    return [dict(t=t, tipo='Serviço') if isinstance(t, str) else dict(t) for t in tarefas]


def _s(sid, nome, gat, tol, tarefas, pecas, tempo, esp, cumpre=(), base='exec'):
    return dict(id=sid, nome=nome, gat=gat, tol=tol, base=base, cumpre=list(cumpre), tempo=tempo, esp=esp,
                tarefas=_tk(tarefas), pecas=[dict(item=i, qtd=q) for i, q in pecas])


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

# ---------- pessoas da manutenção (CD-04): executante pela habilitação da especialidade (D-37) ----------
ESP_NR = {'Mecânico': 'NR-12', 'Lubrificador': 'NR-12', 'Eletricista': 'NR-10'}
_NR_HAB = {'Manutenção de máquinas': 'NR-12', 'Irrigar': 'NR-10'}


def pessoas():
    out = []
    for p in DC.PESSOAS:
        nr = sorted({_NR_HAB[h] for h in p['hab'] if h in _NR_HAB})
        if nr or p['id'] == 'p11':
            out.append(dict(k=p['nome'], f=p['funcao'], hab=list(p['hab']), nr=nr))
    return out


OPERADORES = [p['nome'] for p in DC.PESSOAS if any(h in p['hab'] for h in ('Operar trator', 'Operar colhedora', 'Irrigar'))]
# tanque/lote de diesel (lista curta): ativo no campo só pelo comboio; na sede, tanque ou comboio (D-19: pré-escolhido só se for o único elegível)
TANQUES = [dict(id='Sede · D-118', onde='sede'), dict(id='Comboio CB-01 · D-118', onde='campo')]


def _chk(tarefas, r='', por='', em=''):
    return [dict(t=t['t'], tipo=t.get('tipo', 'Serviço'), r=r, mot='', por=(por if r else ''), em=(em if r else '')) for t in _tk(tarefas)]


def _plano(pid): return next(p for p in PLANOS if p['id'] == pid)
def _serv(pid, sid): return next(s for s in _plano(pid)['servicos'] if s['id'] == sid)


def _ciclo(pid, aid, sid):
    v = VINCULOS[pid + '|' + aid]; u = v['ult'].get(sid) or v['marco']
    return f"{pid}|{aid}|{sid}@{u['data']}|{u['leit'] if u['leit'] is not None else ''}"


def _br(iso): return iso[8:10] + '/' + iso[5:7]


def _pecas(serv, aplicado=False):
    return [dict(item=p['item'], nome=ITENS[p['item']]['nome'], un=ITENS[p['item']]['un'], qtd=p['qtd'], res=0,
                 apl=(p['qtd'] if aplicado else 0), sob=0, preco=ITENS[p['item']]['preco']) for p in serv['pecas']]


ZE = 'Zé (mecânico)'


# ordens já existentes (as cinco fases canônicas; condições viram selo)
def _oms():
    s1 = _serv('PM-01', 's1'); s2p = _serv('PM-04', 's2')
    oms = {
     'OM-0221': dict(id='OM-0221', tipo='Corretiva', aid='a08', serv='Corretiva · rolamento do elevador', crit='Média', etapa='Encerradas',
                     origem='SM-0140 · falha em campo', jan='12/09', janIso='2026-09-12', ret='liberado 13/09', esp='Terceiro (concessionária)', tempo=14,
                     executante='Concessionária Case IH', chk=_chk(['Desmontar elevador', 'Trocar rolamentos', 'Montar e alinhar correntes', 'Teste em vazio'], 'Feito', 'Concessionária Case IH', '13/09'),
                     pecas=[dict(item='', nome='Rolamento do elevador', un='un', qtd=2, res=0, apl=2, sob=0, preco=640)], terc=2520,
                     exec=dict(data='2026-09-13', leit=2149, horas=0), selos=[], achados=[], rv=0),
     'OM-0228': dict(id='OM-0228', tipo='Corretiva', aid='a11', serv='Inspeção corretiva · pressão baixa', crit='Alta', etapa='Liberadas',
                     origem='SM-0152 · alerta agregado (3 leituras)', jan='23/09 14:00', janIso='2026-09-23', ret='23/09 17:00', esp='Eletricista', tempo=3,
                     executante='João', trata=True, origAch='SM-0152', achados=['SM-0152'],
                     chk=[dict(t='Medir pressão de recalque', tipo='Medição', un='bar', r='', mot='', val=''),
                          dict(t='Inspecionar selo mecânico', tipo='Verificação', r='', mot=''),
                          dict(t='Verificar painel e pressostato', tipo='Verificação', r='', mot='')],
                     pecas=[], exec=None, selos=[], rv=0),
     'OM-0230': dict(id='OM-0230', tipo='Preventiva', aid='a05', pid='PM-04', sid='s2', ver=2, cobre=['s2', 's1'], ciclos={}, serv='Revisão 500 h', crit='Média',
                     etapa='Em conferência', origem='PM-04 v2 · Revisão 500 h · 1.540 h (500 h após 1.040 h)', jan='20/09', janIso='2026-09-20', vencOrig='2026-09-20',
                     ret='liberado 21/09', esp='Mecânico', tempo=9, executante='Zé', chk=_chk(s2p['tarefas'], 'Feito', ZE, '20/09'),
                     pecas=[dict(item='KIT-U3030', nome='Kit filtros Uniport 3030', un='kit', qtd=3, res=0, apl=1, sob=2, preco=520),
                            dict(item='OL-HID68', nome='Óleo hidráulico 68', un='L', qtd=40, res=0, apl=40, sob=0, preco=24),
                            dict(item='GR-EP2', nome='Graxa EP2', un='kg', qtd=1, res=0, apl=1, sob=0, preco=32)],
                     exec=dict(data='2026-09-20', leit=1540, horas=9), selos=[], achados=[], rv=0),
     # D-36: o teste é tarefa do tipo Teste, com tentativas só por acréscimo; a 1ª tentativa foi reprovada às 09:00 (antes no MA-04det)
     'OM-0233': dict(id='OM-0233', tipo='Corretiva', aid='a01', serv='Corretiva · pressão hidráulica', crit='Alta', etapa='Em execução',
                     origem='SM-0147 · falha em campo · INSP-105', jan='23/09', janIso='2026-09-23', ret='24/09 12:00', esp='Mecânico', tempo=6.5,
                     executante='Zé', trata=True, origAch='SM-0147', achados=['SM-0147', 'INSP-105'], ini='2026-09-22',
                     chk=[dict(t='Substituir bomba hidráulica', tipo='Serviço', r='Feito', mot='', por=ZE, em='22/09'),
                          dict(t='Trocar mangueiras de alta pressão', tipo='Serviço', r='Feito', mot='', por=ZE, em='22/09'),
                          dict(t='Reaperto e sangria do circuito', tipo='Serviço', r='Feito', mot='', por=ZE, em='23/09'),
                          dict(t='Teste de pressão em carga', tipo='Teste', r='Reprovado', mot='', por=ZE, em='09:00', fixo=True,
                               tent=[dict(r='Reprovado', evid='manômetro 120 bar (mínimo 180 bar)', por=ZE, em='23/09 09:00')])],
                     pecas=[dict(item='', nome='Bomba hidráulica', un='un', qtd=1, res=1, apl=0, sob=0, preco=3600),
                            dict(item='', nome='Mangueira de alta pressão', un='un', qtd=2, res=2, apl=0, sob=0, preco=250)],
                     retiradas=[dict(nome='Bomba hidráulica usada (recuperável)', qtd=1, un='un', dest='A definir', resp=''),
                                dict(nome='Mangueiras usadas', qtd=2, un='un', dest='Sucata', resp=ZE)],
                     exec=None, selos=[], rv=0),
     'OM-0234': dict(id='OM-0234', tipo='Preventiva', aid='a02', pid='PM-01', sid='s1', ver=3, cobre=['s1'], ciclos={'s1': _ciclo('PM-01', 'a02', 's1')},
                     serv='Revisão 250 h', crit='Média', etapa='A liberar', origem='PM-01 v3 · Revisão 250 h · 3.043 h (250 h após 2.793 h)',
                     jan='28/09', janIso='2026-09-28', vencOrig='2026-09-28', ret='28/09 17:00', esp=s1['esp'], tempo=s1['tempo'], executante='',
                     chk=_chk(s1['tarefas']), pecas=_pecas(s1), exec=None, selos=[], achados=[], rv=0),
    }
    # histórico encerrado sintético (D-43): uma preventiva encerrada por última execução de VINCULOS.ult, com custo pela função única (manCusto)
    por_om = {}
    for vk, v in VINCULOS.items():
        pid, aid = vk.split('|')
        for sid, u in v['ult'].items():
            if u['om'] and u['om'] not in oms: por_om.setdefault(u['om'], dict(pid=pid, aid=aid, u=u, sids=[]))['sids'].append(sid)
    for om, x in por_om.items():
        p = _plano(x['pid']); ss = [_serv(x['pid'], s) for s in x['sids']]
        mx = next((s for s in ss if any(o in s.get('cumpre', []) for o in x['sids'])), ss[0])
        exe = 'João' if mx['esp'] == 'Eletricista' else 'Zé'; quem = 'João (irrigante)' if exe == 'João' else ZE
        u = x['u']
        oms[om] = dict(id=om, tipo='Preventiva', aid=x['aid'], pid=x['pid'], sid=mx['id'], ver=p['versao'], cobre=[mx['id']] + list(mx.get('cumpre', [])), ciclos={},
                       serv=mx['nome'], crit='Média', etapa='Encerradas', origem=f"{x['pid']} v{p['versao']} · {mx['nome']}", jan=_br(u['data']), janIso=u['data'],
                       ret='—', esp=mx['esp'], tempo=mx['tempo'], executante=exe, chk=_chk(mx['tarefas'], 'Feito', quem, _br(u['data'])), pecas=_pecas(mx, True),
                       exec=dict(data=u['data'], leit=u['leit'], horas=mx['tempo']), selos=[], achados=[], hist=True, rv=0)
    return oms


# ---------- achados (D-09, D-45, D-48): os 6 casos do MA-02 no estado, com os mesmos IDs, origem e componente ----------
def _achados():
    def A(id_, origem, comp, aid, sint, crit, sug, evid, leit, por, em, estado='Sem ordem', om='', oc=None, nova=False):
        return dict(id=id_, origem=origem, comp=comp, aid=aid, sint=sint, crit=crit, sug=sug, evid=evid, leit=leit, por=por, em=em,
                    oc=oc or [em], estado=estado, om=om, nova=nova, voltou='', mot='', rv=0)
    return {
     'INSP-105': A('INSP-105', 'Inspeção', 'Hidráulico', 'a01', 'Pressão hidráulica abaixo da faixa no pré-uso das 07:10', 'Alta', 'Bloqueado',
                   'checklist + manômetro', 4312, ZE, '2026-09-23', 'Na OM', 'OM-0233'),
     'SM-0147': A('SM-0147', 'Relato', 'Hidráulico', 'a01', 'Pressão hidráulica baixa · parou aos 30 ha da OS-0420', 'Alta', 'Bloqueado',
                  'telemetria + foto', 4312, 'Carlos (operador)', '2026-09-22', 'Na OM', 'OM-0233'),
     'SM-0152': A('SM-0152', 'Alerta', 'Hidráulico', 'a11', 'Pressão baixa 3 vezes esta noite', 'Alta', 'Restrito',
                  '3 leituras de telemetria', 8914, 'Telemetria do pivô', '2026-09-22', 'Na OM', 'OM-0228', oc=['2026-09-22', '2026-09-22', '2026-09-23']),
     'INSP-104': A('INSP-104', 'Inspeção', 'Hidráulico', 'a02', 'Vazamento leve em mangueira', 'Média', 'Apto', 'foto', 2988, 'Beto (operador)', '2026-09-23', nova=True),
     'SM-0150': A('SM-0150', 'Relato', 'Órgão de trabalho', 'a08', 'Ruído intermitente no elevador', 'Baixa', 'Apto', 'áudio do operador', 2150, 'Lucas (operador)', '2026-09-21', nova=True),
     'NC-0912': A('NC-0912', 'Inspeção', 'Órgão de trabalho', 'a06', 'Disco de corte com desgaste', 'Média', 'Apto', 'foto', 886, 'Carlos (operador)', '2026-09-20', nova=True),
    }


# ---------- abastecimentos (D-15) e leituras (D-40) no estado: os lançamentos fixos AB-1037..1042 do MA-05 ----------
def _abast():
    def B(id_, aid, tq, vol, data, hora, leit, op, cheio, qual='Confirmada', **k):
        a = ATIVOS[aid]
        return dict(id=id_, aid=aid, tq=tq, vol=vol, data=data, hora=hora, leit=leit, un=a['un'], op=op, evid='foto', cheio=cheio, qual=qual,
                    por='Rui (almoxarife)', **k)
    return [B('AB-1036', 'a08', 'Sede · D-117', 400, '2026-09-20', '17:30', 2124, 'Beto', True),
            B('AB-1037', 'a02', 'Sede · D-117', 320, '2026-09-22', '06:35', 2977, 'Beto', True, qual='Estornado', estorno='ES-0088'),
            dict(id='ES-0088', tipo='Estorno', ref='AB-1037', aid='a02', tq='Sede · D-117', vol=-320, data='2026-09-23', hora='07:00', leit=None, un='h', op='Beto',
                 evid='', cheio=False, qual='Estorno', motivo='volume digitado errado', por='Otávio (responsável de manutenção)'),
            B('AB-1038', 'a02', 'Sede · D-117', 332, '2026-09-22', '06:35', 2977, 'Beto', True, corrige='AB-1037'),
            B('AB-1039', 'a08', 'Sede · D-117', 310, '2026-09-22', '18:10', 2150, 'Beto', True),
            B('AB-1040', 'cb01', 'Sede · D-118', 220, '2026-09-23', '05:20', 48200, 'Beto', False),
            B('AB-1041', 'a05', 'Comboio CB-01 · D-117', 240, '2026-09-23', '05:50', 1542, 'João', False),
            B('AB-1042', 'a02', 'Sede · D-118', 180, '2026-09-23', '06:40', 2988, 'Beto', True)]


def _leituras():
    out = []; n = 0
    for aid in ORDEM_ATIVOS:
        a = ATIVOS[aid]
        if not a['leit']: continue
        n += 1
        ab = a['leit']['origem'].split(' ')[-1] if a['leit']['origem'].startswith('Abastecimento') else ''
        out.append(dict(id=f'LT-{n:04d}', aid=aid, val=a['leit']['val'], un=a['un'], data=a['leit']['data'], origem=a['leit']['origem'], qual='Confirmada',
                        por='seed', ab=ab))
    return out


# ---------- conflito com a produção (D-38): a alocação da semana (alocacao.py), a mesma fonte de O.S. › Recursos ----------
REC_DO_ATIVO = {'a01': 'T1', 'a02': 'T02', 'a03': 'T03', 'a04': 'T04', 'a08': 'COL', 'a15': 'PV1', 'a11': 'PV2', 'a05': 'PJ', 'a06': 'PL', 'a07': 'DI', 'a10': 'ES'}


def al_js():
    return dict(jor=AL.JORNADA, jorRec=AL.JOR_RECURSO, rec=REC_DO_ATIVO, nome=AL.NOME, tipo=AL.TIPO,
                aloc=[dict(r=a['r'], os=a['os'], dia=a['dia'], h=round(a['fim'] - a['ini'], 2), ini=a['ini'], fim=a['fim'], sit=a['sit']) for a in AL.ALOC])


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
    # v=4 (S2): achados no estado (c.achados substitui c.ach), condição com histórico, tarefas tipadas, leituras, abastecimentos e recibos
    return dict(v=V, rev=0, hoje=HOJE, horiz=HORIZONTE, antiga=LEIT_ANTIGA, custoh=CUSTO_H, maxdia=MAX_DIA, seq=235, seqpm=11, seqsc=41,
                ativos=ATIVOS, ordem=ORDEM_ATIVOS, itens=ITENS, esp=ESPECIALIDADES, planos=planos, ordemPlanos=[p['id'] for p in PLANOS],
                vinc=VINCULOS, oms=_oms(), achados=_achados(), leituras=_leituras(), abast=_abast(), recibos={})


def dados_js():
    """Constantes fixas das regras (não são estado): pessoas e habilitações (CD-04), alocação da semana (AL), tanques, operadores, listas curtas."""
    return ('const MAN_PES = ' + json.dumps(pessoas(), ensure_ascii=False) + ';\n'
            + 'const MAN_AL = ' + json.dumps(al_js(), ensure_ascii=False) + ';\n'
            + 'const MAN_TQ = ' + json.dumps(TANQUES, ensure_ascii=False) + ';\n'
            + 'const MAN_OPS = ' + json.dumps(OPERADORES, ensure_ascii=False) + ';\n'
            + 'const MAN_COMP = ' + json.dumps(COMPONENTES, ensure_ascii=False) + ';\n'
            + 'const MAN_TIPOS = ' + json.dumps(TIPOS_TAREFA, ensure_ascii=False) + ';\n'
            + 'const MAN_ESP_NR = ' + json.dumps(ESP_NR, ensure_ascii=False) + ';\n')


def js_prefixo():
    """Cenário único (CEN0, com c.man desde o 1a) + regras da manutenção: para telas que ainda não embutem cenario.js_prefixo()."""
    import cenario
    return cenario.js_prefixo() + js_regras()


def js_regras():
    """Regras da manutenção sobre o cenário único (1a): exige cenario.js_prefixo() antes (MAN0 = CEN0.man)."""
    return 'const MAN0 = CEN0.man;\n' + JS_ACESSO_CEN + dados_js() + JS + '\n'


JS_ACESSO_CEN = r'''
/* ===== Estado da manutenção dentro do cenário único (1a, PCMS-M01): c.man de 'talhao-os-cenario-v1'; O.S., Estoque, App e CD-03 leem o mesmo ===== */
function manClone(o){ return JSON.parse(JSON.stringify(o)); }
function manGet(){ return cenGet().man; }
function manReset(self){ cenReset(); try{ cenSave(cenClone(CEN0)); }catch(e){} if(self) self.setState({manrev:Date.now(),cenrev:Date.now(),g2toast:'Demonstração restaurada: manutenção, ordens, estoque e app voltam ao início.'}); }
function manMudar(self,fn){ const c=cenClone(cenGet()); let r;
  try{ r=fn(c.man,c)||{}; }catch(e){ r={erro:String(e.message||e)}; }
  if(r.erro){ if(self) self.setState({g2toast:r.erro}); return r; }
  if(r.nada){ if(self&&r.msg) self.setState(Object.assign({g2toast:r.msg},r.st||{})); return r; }
  c.man.rev=(c.man.rev||0)+1; c.rev=(c.rev||0)+1; cenSave(c); if(self) self.setState(Object.assign({manrev:c.man.rev,cenrev:c.rev,g2toast:r.msg||''},r.st||{})); return r; }
function manOuvir(self){ if(self.__manOuvindo) return; self.__manOuvindo=true;
  try{ window.addEventListener('storage',(e)=>{ if(e.key===CEN_KEY) self.setState({manrev:Date.now()}); }); }catch(e){} }
'''

JS = r'''
/* ===== Regras da manutenção (fonte única: tela MA, CD-03, O.S. e app) ===== */
const MAN_FASES=['A liberar','Liberadas','Em execução','Em conferência','Encerradas'];
const MAN_ABERTAS=['A liberar','Liberadas','Em execução'];
const MAN_RESP={'Serviço':['Feito','Não feito','Não se aplica'],'Verificação':['Conforme','Não conforme','Não se aplica','Não foi possível verificar'],'Medição':['Conforme','Não conforme'],'Teste':['Aprovado','Reprovado']};
const MAN_OK=['Feito','Conforme','Aprovado'];
/* ---------- números e datas (ISO em UTC, sem fuso) ---------- */
function manN(n,d){ return Number(n||0).toLocaleString('pt-BR',{minimumFractionDigits:0,maximumFractionDigits:d===undefined?0:d}); }
function manRS(n){ return 'R$ '+Number(n||0).toLocaleString('pt-BR',{minimumFractionDigits:2,maximumFractionDigits:2}); }
function manT(s){ const a=String(s).split('-'); return Date.UTC(+a[0],+a[1]-1,+a[2]); }
function manDias(a,b){ return Math.round((manT(b)-manT(a))/86400000); }
function manAdd(s,n){ return new Date(manT(s)+n*86400000).toISOString().slice(0,10); }
function manBr(s){ if(!s) return '—'; const a=String(s).split('-'); if(a.length!==3) return String(s); return a[2]+'/'+a[1]+(a[0]===String(MAN0.hoje).slice(0,4)?'':'/'+a[0]); }
function manSem(s){ return ['dom','seg','ter','qua','qui','sex','sáb'][new Date(manT(s)).getUTCDay()]; }
function manUn(u){ return u==='d'?'dias':u; }
function manQ(v,u){ return manN(v)+' '+u; }
function manHr(){ const d=new Date(); return ('0'+d.getHours()).slice(-2)+':'+('0'+d.getMinutes()).slice(-2); }
/* número digitado em pt-BR: vírgula decimal; ponto só como milhar (2.995 = 2995; 1,5 = 1.5) */
function manNum(x){ const t=String(x===undefined||x===null?'':x).trim(); if(!t) return NaN; if(t.indexOf(',')>=0) return Number(t.replace(/\./g,'').replace(',','.'));
  if(/^-?\d{1,3}(\.\d{3})+$/.test(t)) return Number(t.replace(/\./g,'')); return Number(t); }
function manVazio(x){ return String(x===undefined||x===null?'':x).trim()===''; }
/* ---------- pessoas, perfil de quem age e matriz papel × comando (D-33; perfil de demonstração, não é segurança) ---------- */
function manPessoa(k){ return MAN_PES.find(p=>p.k===k)||null; }
function manHab(k,h){ const p=manPessoa(k); return !!p&&p.hab.indexOf(h)>=0; }
function manExecCands(esp){ const nr=MAN_ESP_NR[esp]; if(!nr) return []; return MAN_PES.filter(p=>p.nr.indexOf(nr)>=0).map(p=>p.k); }
function manExecSug(o){ if(o.executante) return o.executante; const cs=manExecCands(o.esp); return cs.length===1?cs[0]:''; }
function manPf(pf){ const q=(typeof g2pf==='function')?g2pf(pf):null; if(q) return q; if(pf&&typeof pf==='object') return {k:pf.k||'',papeis:pf.papeis||{}}; return {k:String(pf||''),papeis:{}}; }
function manPapelDe(pf){ const p=(manPf(pf).papeis)||{}; return p.pcm?'pcm':(p.mecanico?'mecanico':(p.gestor?'gestor':'')); }
function manPor(pf){ const q=manPf(pf); const pa=manPapelDe(q); if(!q.k) return ''; if(typeof g2ator==='function'&&pa){ const t=g2ator(q,pa); if(t) return t; } return q.k; }
function manRtTxt(a){ return a?(a.rt||'Otávio'):'—'; }
function manPode(c,pf,cmd,x){ x=x||{}; const q=manPf(pf); const pa=manPapelDe(q); const k=q.k;
  const PCM='Ação do Otávio (responsável de manutenção)';
  if(cmd==='registrar') return pa?'':'Ação de Otávio, Zé ou Ana';
  if(['decidir','gerar','mover','liberar','encerrar','leituraDecidir','estorno','plano','ponte'].indexOf(cmd)>=0) return pa==='pcm'?'':PCM;
  if(cmd==='condicao'){ const a=x.aid?c.ativos[x.aid]:null; if(pa==='pcm') return ''; if(pa==='mecanico'&&a&&a.rt===k) return ''; return 'Ação do Otávio ou do responsável técnico ('+manRtTxt(a)+')'; }
  const o=x.o;
  if(cmd==='incluir'){ if(!o) return 'Ordem não encontrada.'; if(pa==='pcm'&&(o.etapa==='A liberar'||o.etapa==='Liberadas')) return ''; if(o.etapa==='Em execução'&&o.executante&&o.executante===k) return '';
    return o.etapa==='Em execução'?('Ação de '+(o.executante||'quem executa')+', executante'):PCM; }
  if(cmd==='executar'){ if(o&&o.executante&&o.executante===k) return ''; return 'Ação de '+((o&&o.executante)||'quem executa')+', executante'; }
  if(cmd==='teste'){ const e=manPode(c,pf,'executar',x); if(e) return e; return manHab(k,'Testar reparo')?'':'Teste só com a habilidade “Testar reparo” (CD-04)'; }
  return ''; }
function manExige(c,pf,cmd,x){ const m=manPode(c,pf,cmd,x); if(m) throw new Error(m+'. Nada foi alterado.'); }
/* ---------- chave de idempotência por comando (D-30) e versão do registro (o.rv, D-46) ---------- */
function manChave(){ return 'k'+Date.now().toString(36)+Math.random().toString(36).slice(2,8); }
function manCmd(c,chave,nome,fn){ c.recibos=c.recibos||{}; if(chave&&c.recibos[chave]){ const r=c.recibos[chave]; return {nada:true,repetido:true,msg:r.msg,id:r.id,ids:r.ids}; }
  const r=fn()||{}; if(chave&&!r.nada&&!r.erro) c.recibos[chave]={nome,msg:r.msg||'',id:r.id||'',ids:r.ids||null,em:c.hoje}; return r; }
function manRv(o,rv){ if(rv!==undefined&&rv!==null&&rv!==''&&(o.rv||0)!==Number(rv)) throw new Error('Mudou desde que você abriu: '+o.id+' agora em '+o.etapa+'. Revise e confirme.'); }
function manToca(o){ o.rv=(o.rv||0)+1; }
/* ---------- ativos, planos e serviços ---------- */
function manAtv(c,aid){ return c.ativos[aid]||null; }
function manNome(a){ return a? a.nome+(a.classe==='Trator'?' · '+a.modelo:'') : '—'; }
function manPub(p){ return p.versao?p.servicos:[]; }
function manWork(p){ return p.rasc?p.rasc.servicos:p.servicos; }
function manTk(t){ return (t&&typeof t==='object')?t:{t:String(t),tipo:'Serviço'}; }
function manTkT(t){ return manTk(t).t; }
function manGatTxt(s){ const g=s.gat||{}; const t=[]; if(g.h) t.push(manN(g.h)+' h'); if(g.km) t.push(manN(g.km)+' km'); if(g.d) t.push(manN(g.d)+' dias'); return t.length?('a cada '+t.join(' ou ')):'sem gatilho'; }
function manTolTxt(s){ const g=s.gat||{}, o=s.tol||{}; const t=[]; if(g.h) t.push('± '+manN(o.h||0)+' h'); if(g.km) t.push('± '+manN(o.km||0)+' km'); if(g.d) t.push('± '+manN(o.d||0)+' dias'); return t.join(' · '); }
function manCabe(c,p,a){ return p.aplica.t==='modelo'? p.aplica.v.indexOf(a.modelo)>=0 : p.aplica.v.indexOf(a.id)>=0; }
function manAplTxt(c,p){ if(p.aplica.t==='modelo') return (p.aplica.v.length>1?'Modelos ':'Modelo ')+p.aplica.v.join(' e ');
  const n=p.aplica.v.map(id=>(c.ativos[id]||{}).nome).filter(Boolean); return n.length>2?(n.length+' ativos'):n.join(' e '); }
function manRef(v,sid){ return (v.ult&&v.ult[sid])||v.marco; }
function manCiclo(pid,aid,sid,ref){ return pid+'|'+aid+'|'+sid+'@'+ref.data+'|'+(ref.leit===null||ref.leit===undefined?'':ref.leit); }
/* ---------- vencimento: o que vencer primeiro (mesma fórmula do dados_manutencao.vencimento) ---------- */
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
function manSitTxt(c,x){ const g=x.gats[x.prim]; if(!g) return x.sit;
  if(x.sit==='Vencida'){ const v=x.gats.find(y=>y.venc); return v.u==='d'?('Vencida desde '+manBr(v.due)):('Vencida · '+manQ(-v.falta,v.u)+' além'); }
  return x.sit; }
function manPrimTxt(x){ const g=x.gats[x.prim]; if(!g||x.gats.length<2) return ''; return g.u==='d'?'o calendário vence primeiro':(g.u==='h'?'o horímetro vence primeiro':'o odômetro vence primeiro'); }
/* início da janela (vencimento − tolerância) em dias a partir de hoje: a base única do prazo de Sem ordem (D-28) */
function manIniJanela(x){ if(!x||!x.gats.length) return Infinity; return Math.min.apply(null,x.gats.map(g=>g.di)); }
function manLeitTxt(a){ if(!a||!a.leit) return 'sem contador'; return manQ(a.leit.val,a.un)+' · '+manBr(a.leit.data); }
function manAntiga(c,a){ return !!(a&&a.leit&&manDias(a.leit.data,c.hoje)>c.antiga); }
/* ---------- ordens ---------- */
function manAberta(o){ return o.etapa!=='Encerradas'&&o.etapa!=='Canceladas'; }
function manOmCiclo(c,pid,aid,sid,ciclo){ return Object.values(c.oms).find(o=>o.pid===pid&&o.aid===aid&&(o.cobre||[]).indexOf(sid)>=0&&(o.ciclos||{})[sid]===ciclo)||null; }
function manFalta(c,o){ return (o.pecas||[]).filter(p=>p.item&&!p.res&&o.etapa==='A liberar'&&((c.itens[p.item].saldo-c.itens[p.item].reservado)<p.qtd)); }
/* todas as linhas plano × ativo × serviço (publicado), com cálculo, ordem do ciclo e selos */
function manLinhas(c,pid){ const out=[];
  Object.keys(c.vinc).forEach(vk=>{ const v=c.vinc[vk]; const k=vk.split('|'); if(pid&&k[0]!==pid) return; const p=c.planos[k[0]], a=c.ativos[k[1]]; if(!p||!a) return;
    const ss=manPub(p); if(!ss.length){ out.push({vk,pid:p.id,aid:a.id,sid:'',p,a,s:null,x:{sit:'Aguarda publicar',gats:[],prim:null,prev:null},ref:v.marco,om:null}); return; }
    ss.forEach(s=>{ const ref=manRef(v,s.id); const x=p.estado==='Inativo'?{sit:'Plano inativo',gats:[],prim:null,prev:null}:manVenc(c,s,a,ref);
      const ciclo=manCiclo(p.id,a.id,s.id,ref); const om=manOmCiclo(c,p.id,a.id,s.id,ciclo);
      const dup=om?null:(Object.values(c.oms).find(o=>o.tipo==='Preventiva'&&o.aid===a.id&&o.pid&&o.pid!==p.id&&manAberta(o)&&String(o.serv).toLowerCase()===String(s.nome).toLowerCase())||null);
      out.push({vk,pid:p.id,aid:a.id,sid:s.id,p,a,s,x,ref,ciclo,om,dup,est:!!(v.marco&&v.marco.est&&!(v.ult||{})[s.id])}); }); });
  return out; }
function manDevida(l){ return l.x.sit==='Vencida'||l.x.sit==='Vence em breve'; }
function manSemOm(c){ return manLinhas(c).filter(l=>manDevida(l)&&!l.om&&!l.dup); }
function manLinhaOm(c,o){ if(!o||!o.pid) return null; return manLinhas(c,o.pid).find(x=>x.aid===o.aid&&x.sid===o.sid&&x.om&&x.om.id===o.id)||null; }
function manDupServ(c,pid,aid,nomes){ const ns=nomes.map(x=>String(x).toLowerCase());
  for(const k of Object.keys(c.vinc)){ const q=k.split('|'); if(q[1]!==aid||q[0]===pid) continue; const o=c.planos[q[0]]; if(!o||o.estado==='Inativo') continue;
    const s=manWork(o).concat(manPub(o)).find(x=>ns.indexOf(String(x.nome).toLowerCase())>=0); if(s) return {pid:o.id,s:s.nome}; }
  return null; }
function manSelosLinha(c,l){ const s=[]; if(l.a.cond==='Bloqueado'){ s.push({t:'Ativo bloqueado',c:'red'}); }
  if(manAntiga(c,l.a)) s.push({t:'Leitura de '+manBr(l.a.leit.data),c:'yellow'}); if(l.a.suspeita) s.push({t:'Leitura a confirmar',c:'yellow'}); if(l.est) s.push({t:'Marco estimado',c:'yellow'}); return s; }
/* ---------- conflito com a produção (D-38): horas livres do recurso no dia (jornada − O.S. firme ou condicional) < tempo previsto ---------- */
function manLivre(c,aid,iso){ const r=MAN_AL.rec[aid]; if(!r) return null; const jor=(MAN_AL.jorRec||{})[r]||MAN_AL.jor;
  const its=MAN_AL.aloc.filter(a=>a.r===r&&a.dia===iso&&a.sit!=='manutenção'); const h=its.reduce((s,a)=>s+a.h,0); const os=[];
  its.forEach(a=>{ if(os.indexOf(a.os)<0) os.push(a.os); }); return {r,jor,h,livre:Math.round((jor-h)*100)/100,os}; }
function manConflito(c,o,iso){ if(!o) return null; iso=iso||o.janIso; if(!iso) return null; const L=manLivre(c,o.aid,iso); if(!L||!L.os.length) return null;
  const t=Number(o.tempo)>0?Number(o.tempo):1; if(L.livre+1e-9>=t) return null;
  return {os:L.os,dia:iso,livre:Math.max(0,L.livre),t:'Conflito · '+L.os.join(' e ')+' '+manBr(iso),det:manN(Math.max(0,L.livre),1)+' h livres de '+manN(L.jor,1)+' h para '+manN(t,1)+' h previstas'}; }
function manProxLivre(c,o){ for(let i=1;i<=7;i++){ const d=manAdd(c.hoje,i); if(!manConflito(c,o,d)) return d; } return null; }
/* operador da alocação do ativo no dia (AL): pessoa da mesma O.S. no mesmo dia; sem alocação, nenhum (D-19) */
function manOperadorDia(c,aid,iso){ const r=MAN_AL.rec[aid]; if(!r) return ''; const oss=MAN_AL.aloc.filter(a=>a.r===r&&a.dia===iso&&a.sit!=='manutenção').map(a=>a.os);
  const ps=MAN_AL.aloc.filter(a=>a.dia===iso&&oss.indexOf(a.os)>=0&&MAN_AL.tipo[a.r]==='Pessoa').map(a=>MAN_AL.nome[a.r]);
  const op=ps.find(n=>/operador|irrigante/.test(n))||''; return op?op.split(' · ')[0]:''; }
function manTanques(c,aid){ const a=c.ativos[aid]; const campo=!!a&&/^(Santa Rita|Pivô|Talhão)/.test(a.local||''); return MAN_TQ.filter(t=>campo?t.onde==='campo':true).map(t=>t.id); }
/* limite da tolerância de uma preventiva aberta (data) e se já venceu */
function manTolLim(c,o){ const l=manLinhaOm(c,o); if(!l||!l.x.gats.length) return null; const a=l.a; let dl=null;
  l.x.gats.forEach(g=>{ let d=null; if(g.u==='d') d=manAdd(g.due,g.tol||0); else if(a.leit&&a.ritmo>0) d=manAdd(a.leit.data,Math.floor((g.due+(g.tol||0)-a.leit.val)/a.ritmo)); if(d&&(!dl||d<dl)) dl=d; });
  return dl?{dl,venc:l.x.sit==='Vencida'}:null; }
/* ---------- selos da ordem: condição, nunca coluna; o principal tem dono e prazo ---------- */
function manSelos(c,o){ const s=[]; const a=c.ativos[o.aid];
  const cf=(o.etapa==='A liberar'||o.etapa==='Liberadas')?manConflito(c,o):null;
  if(manFalta(c,o).length) s.push({t:'Falta peça',c:'red',dono:'Otávio',ac:'compra'});
  if(o.sc&&manFalta(c,o).length) s.push({t:'Compra '+o.sc.id+' (simulado)',c:'yellow',dono:'Otávio'});
  if(cf) s.push(o.conflitoAceito?{t:'Conflito aceito · '+cf.os.join(' e '),c:'yellow',dono:'Otávio'}:{t:cf.t,c:'red',dono:'Otávio',prazo:manBr(o.janIso)});
  if(o.etapa==='A liberar'&&!manExecSug(o)) s.push({t:'Falta: executante',c:'red',dono:'Otávio'});
  if(o.tipo==='Preventiva'&&o.pid&&MAN_ABERTAS.indexOf(o.etapa)>=0){ const l=manLinhaOm(c,o); if(l&&l.x.sit==='Vencida') s.push({t:'Vencida',c:'red',dono:'Otávio'}); }
  if(a&&a.cond==='Bloqueado'&&manAberta(o)&&o.etapa!=='Em conferência') s.push({t:'Ativo bloqueado',c:'red',dono:o.trata?(o.executante||'Otávio'):'Otávio'});
  if(o.etapa==='Em execução'&&(o.chk||[]).some(t=>t.nova&&!t.r)) s.push({t:'Tarefa nova',c:'yellow',dono:o.executante});
  if(o.etapa==='Em execução'&&o.conflitoApp) s.push({t:'Conflito a resolver',c:'red',dono:'Otávio'});
  if(o.etapa==='Em conferência'&&o.trata&&!o.aptidao) s.push({t:'Decidir aptidão · '+(a?a.nome:''),c:'yellow',dono:'Otávio ou '+manRtTxt(a)});
  if((o.pecas||[]).some(p=>p.sob>0)) s.push({t:'Sobras a resolver',c:'yellow',dono:'Otávio (simulado · papel do Almoxarifado)'});
  if((o.retiradas||[]).some(r=>!r.dest||r.dest==='A definir'||!r.resp)) s.push({t:'Peça retirada sem destino',c:'yellow',dono:o.executante||'Otávio'});
  (o.pend||[]).forEach(id=>s.push({t:'Pendência '+id,c:'yellow'}));
  if(o.de) s.push({t:'Pendência da '+o.de,c:'yellow'});
  return s; }
/* custo da ordem pela função única (PCMS-C01): estimado = planejado × preço + tempo previsto × custo-hora + terceiro; final = aplicado × preço + horas × custo-hora + terceiro */
function manCusto(c,o,modo){ const pc=(o.pecas||[]).reduce((s,p)=>s+(modo==='est'?(p.qtd||0):(p.apl||0))*(p.preco||0),0);
  const h=modo==='est'?(Number(o.tempo)||0):((o.exec&&o.exec.horas)||0); return pc+h*c.custoh+(Number(o.terc)||0); }
function manCustoFinal(c,o){ return (o.custo!==undefined&&o.custo!==null)?o.custo:manCusto(c,o); }
/* ---------- gerar: uma OM por ativo × serviço × ciclo; serviço maior que "cumpre também" e também está devido gera uma só OM ---------- */
function manGerar(c,vk,sid,pf){ if(pf!==undefined) manExige(c,pf,'gerar'); const k=vk.split('|'); const p=c.planos[k[0]], a=c.ativos[k[1]], v=c.vinc[vk]; if(!p||!a||!v) throw new Error('Vínculo não encontrado.');
  const ls=manLinhas(c,p.id).filter(l=>l.aid===a.id); let l=ls.find(x=>x.sid===sid); if(!l) throw new Error('Serviço não está na versão publicada.');
  const maior=ls.find(x=>x.s&&(x.s.cumpre||[]).indexOf(sid)>=0&&manDevida(x)); if(maior) l=maior;
  if(l.om) return {nada:true,msg:'Já existe a '+l.om.id+' para este ciclo · nenhuma ordem nova.',id:l.om.id};
  if(l.dup) return {nada:true,msg:manNome(a)+' · '+l.s.nome+' já está na '+l.dup.id+' ('+l.dup.pid+') · nenhuma ordem nova.',id:l.dup.id};
  if(!manDevida(l)) throw new Error(a.nome+' · '+l.s.nome+' está em dia; gere a ordem quando a janela se aproximar.');
  const s=l.s; const id='OM-'+String(c.seq).padStart(4,'0'); c.seq++;
  const cobre=[s.id].concat(s.cumpre||[]); const ciclos={}; cobre.forEach(x=>{ ciclos[x]=manCiclo(p.id,a.id,x,manRef(v,x)); });
  const g=l.x.gats[l.x.prim];
  const ciclo=g.u==='d'?('vence '+manBr(g.due)):(manQ(g.due,g.u)+' ('+manN(s.gat[g.u])+' '+g.u+' após '+manQ(l.ref.leit,g.u)+')');
  const jIso=l.x.sit==='Vencida'?manAdd(c.hoje,1):(l.x.prev||manAdd(c.hoje,1));
  c.oms[id]={id,tipo:'Preventiva',aid:a.id,pid:p.id,sid:s.id,ver:p.versao,cobre,ciclos,serv:s.nome,crit:l.x.sit==='Vencida'?'Alta':'Média',etapa:'A liberar',
    origem:p.id+' v'+p.versao+' · '+s.nome+' · '+ciclo,jan:manBr(jIso),janIso:jIso,vencOrig:(l.x.prev||jIso),ret:manBr(jIso)+' 17:00',esp:s.esp,tempo:s.tempo,executante:'',
    chk:(s.tarefas||[]).map(t=>{ const q=manTk(t); return Object.assign({t:q.t,tipo:q.tipo||'Serviço',r:'',mot:''},q.un?{un:q.un,val:''}:{}); }),
    pecas:(s.pecas||[]).map(x=>{ const it=c.itens[x.item]; return {item:x.item,nome:it.nome,un:it.un,qtd:x.qtd,res:0,apl:0,sob:0,preco:it.preco}; }),exec:null,selos:[],achados:[],rv:0};
  const o=c.oms[id]; const falta=manFalta(c,o); const cf=manConflito(c,o);
  return {id,msg:id+' gerada para '+manNome(a)+' · '+s.nome+(maior?' (cumpre também '+ls.find(x=>x.sid===sid).s.nome+')':'')+' · janela '+manBr(jIso)+(cf?' · '+cf.t:'')+(falta.length?' · Falta peça: '+falta.map(x=>x.nome).join(', '):'')+'.'}; }
/* gerar as do filtro (keys = 'vk#sid'); sem keys, todas as devidas sem ordem */
function manGerarTodas(c,keys,pf){ if(pf!==undefined) manExige(c,pf,'gerar'); const ids=[]; const alvo=keys?keys.slice():manSemOm(c).map(l=>l.vk+'#'+l.sid);
  alvo.forEach(k=>{ const i=k.lastIndexOf('#'); const vk=k.slice(0,i), sid=k.slice(i+1); const l=manLinhas(c,vk.split('|')[0]).find(x=>x.vk===vk&&x.sid===sid);
    if(!l||l.om||l.dup||!manDevida(l)) return; const r=manGerar(c,vk,sid); if(r.id&&!r.nada&&ids.indexOf(r.id)<0) ids.push(r.id); });
  if(!ids.length) return {nada:true,msg:'Nada a gerar neste filtro: os vencimentos já têm ordem.'};
  const fp=ids.filter(id=>manFalta(c,c.oms[id]).length); const n=ids.length;
  return {ids,id:ids[0],msg:n+(n>1?' ordens em A liberar: ':' ordem em A liberar: ')+ids.join(', ')+(fp.length?' · '+fp.join(', ')+' com Falta peça':'')+'.'}; }
/* ---------- janela: "Mover janela" único para toda OM (D-38) ---------- */
function manMover(c,id,iso,motivo,pf,forcar){ const o=c.oms[id]; if(!o) throw new Error('Ordem não encontrada.'); if(pf!==undefined) manExige(c,pf,'mover');
  if(['A liberar','Liberadas'].indexOf(o.etapa)<0) throw new Error(id+' está '+o.etapa+': a janela só muda em A liberar ou Liberadas.');
  if(!iso) throw new Error('Escolha o dia da janela.'); if(iso<c.hoje) throw new Error('Escolha hoje ou um dia depois.');
  if(iso===o.janIso) return {nada:true,msg:id+' já está em '+manBr(iso)+'.'};
  const tl=manTolLim(c,o); const fora=!!tl&&(tl.venc||iso>tl.dl);
  if(fora&&manVazio(motivo)) return {nada:true,avisoTol:true,msg:'Fica fora da tolerância · '+(tl.venc?'venceu':'vence')+' em '+manBr(tl.dl)+'. Informe o motivo para mover mesmo assim.'};
  const cf=manConflito(c,o,iso);
  if(o.etapa==='Liberadas'&&cf&&!forcar) return {nada:true,avisoConf:true,msg:cf.t+' ('+cf.det+'). Mova para outro dia ou confirme mesmo assim.'};
  if(!o.vencOrig) o.vencOrig=o.janIso; const de=o.janIso; o.janAnt=o.jan; o.janIso=iso; o.jan=manBr(iso); o.ret=manBr(iso)+' 17:00'; o.conflitoAceito=false;
  o.movs=(o.movs||[]).concat([{de,para:iso,motivo:String(motivo||'').trim(),por:manPor(pf),em:c.hoje}]); manToca(o);
  return {msg:id+' movida para '+manBr(iso)+(fora?' · fora da tolerância ('+String(motivo).trim()+')':(tl?' · dentro da tolerância (até '+manBr(tl.dl)+')':''))+(cf?' · '+cf.t:' · sem conflito')+'.'}; }
/* liberar: executante e tempo; falta de peça trava (estoque); conflito com a produção é aviso confirmado até o 1b ("Liberar mesmo assim") */
function manLiberar(c,id,forcar,pf,d){ const o=c.oms[id]; if(!o) throw new Error('Ordem não encontrada.'); if(o.etapa!=='A liberar') throw new Error(id+' não está em A liberar.');
  if(pf!==undefined) manExige(c,pf,'liberar'); d=d||{};
  if(d.executante!==undefined&&d.executante!==null&&d.executante!=='') o.executante=d.executante;
  if(d.tempo!==undefined&&!manVazio(d.tempo)){ const t=manNum(d.tempo); if(isNaN(t)||t<=0||t>200) throw new Error('Tempo previsto inválido.'); o.tempo=t; }
  const ex=manExecSug(o); if(!ex) throw new Error('Falta: executante. Escolha quem executa.'); if(!(Number(o.tempo)>0)) throw new Error('Falta: tempo previsto (h).');
  const f=manFalta(c,o); if(f.length) throw new Error('Não liberada: falta peça · '+f.map(x=>x.nome+' ('+manN(c.itens[x.item].saldo-c.itens[x.item].reservado)+' de '+manN(x.qtd)+' '+x.un+')').join(', ')+(o.sc?'. Aguarda o recebimento da '+o.sc.id+'.':'. Solicite a compra.'));
  const cf=manConflito(c,o); if(cf&&!forcar) return {nada:true,aviso:true,msg:cf.t+' ('+cf.det+'). Mova a janela ou libere mesmo assim.'};
  (o.pecas||[]).forEach(p=>{ if(!p.item) return; c.itens[p.item].reservado+=p.qtd; p.res=p.qtd; });
  o.executante=ex; o.etapa='Liberadas'; if(cf) o.conflitoAceito=true; o.lib={por:manPor(pf),em:c.hoje,conf:cf?cf.t:''}; manToca(o);
  const pr=(o.pecas||[]).filter(p=>p.item).map(p=>p.nome+' '+manN(p.qtd)+' '+p.un);
  return {msg:id+' liberada para a oficina · executante '+ex+(pr.length?' · reservado: '+pr.join(', '):'')+(cf?' · conflito com a '+cf.os.join(' e ')+' aceito e avisado ao PCP':'')+'.'}; }
/* pontes até o 1b/1c (D-22): rotuladas "(simulado · …)" na tela */
function manSolicitar(c,id,pf){ const o=c.oms[id]; if(!o) throw new Error('Ordem não encontrada.'); if(pf!==undefined) manExige(c,pf,'ponte'); if(o.sc) return {nada:true,msg:'A '+o.sc.id+' já foi enviada a Compras (simulado).'};
  const f=manFalta(c,o); if(!f.length) return {nada:true,msg:'Nenhuma peça em falta nesta ordem.'};
  const sc='SC-'+String(c.seqsc||41).padStart(3,'0'); c.seqsc=(c.seqsc||41)+1;
  o.sc={id:sc,data:c.hoje,itens:f.map(p=>{ const it=c.itens[p.item]; return {item:p.item,nome:p.nome,un:p.un,qtd:Math.max(0,p.qtd-Math.max(0,it.saldo-it.reservado))}; })}; manToca(o);
  return {msg:sc+' enviada a Compras (simulado · Compras recebe no 1c): '+o.sc.itens.map(x=>x.nome+' '+manN(x.qtd,1)+' '+x.un).join(', ')+' · a '+id+' libera quando a peça chegar.'}; }
function manReceber(c,id,pf){ const o=c.oms[id]; if(!o||!o.sc) throw new Error('Esta ordem não tem compra solicitada.'); if(pf!==undefined) manExige(c,pf,'ponte'); if(o.sc.rec) return {nada:true,msg:'Recebimento da '+o.sc.id+' já registrado.'};
  o.sc.itens.forEach(x=>{ c.itens[x.item].saldo+=x.qtd; }); o.sc.rec=c.hoje; manToca(o);
  return {msg:'Recebimento da '+o.sc.id+' (simulado · papel do Almoxarifado): '+o.sc.itens.map(x=>x.nome+' '+manN(x.qtd,1)+' '+x.un).join(', ')+' · '+id+' pronta para liberar.'}; }
function manIniciar(c,id,pf){ const o=c.oms[id]; if(!o||o.etapa!=='Liberadas') throw new Error(id+' não está em Liberadas.'); if(pf!==undefined) manExige(c,pf,'executar',{o});
  o.etapa='Em execução'; o.ini=c.hoje; manToca(o);
  return {msg:id+' Em execução · responda as tarefas e informe a leitura do contador para concluir.'}; }
/* resposta tarefa a tarefa (PRD 54.2: nunca pré-marcar; guarda quem e quando); editar só o motivo não troca o autor da resposta (CTL-3, achado 2) */
function manResp(c,id,i,r,mot,pf,val){ const o=c.oms[id]; if(!o||o.etapa!=='Em execução') throw new Error('Responda as tarefas com a ordem Em execução.'); const t=o.chk[i]; if(!t) throw new Error('Tarefa não encontrada.');
  if(pf!==undefined) manExige(c,pf,'executar',{o}); const tp=t.tipo||'Serviço'; if(tp==='Teste') throw new Error('Teste: registre a tentativa com o resultado e a evidência.');
  if(r&&(MAN_RESP[tp]||[]).indexOf(r)<0) throw new Error('Resposta inválida para '+tp+'.');
  const hr=manHr(), quem=manPor(pf);
  if(r!==undefined&&(t.r||'')!==(r||'')){ t.r=r; t.por=r?quem:''; t.em=r?hr:''; }
  if(mot!==undefined&&mot!==(t.mot||'')){ t.mot=mot; t.motPor=quem; t.motEm=hr; }
  if(val!==undefined&&tp==='Medição'){ const n=manVazio(val)?'':manNum(val); if(n!==''&&isNaN(n)) throw new Error('Valor da medição inválido.'); t.val=n; }
  if(t.r) t.nova=false; manToca(o); return {msg:''}; }
/* Teste com tentativas, só por acréscimo (D-36): Reprovado mantém a OM Em execução e o ativo bloqueado */
function manTentativa(c,id,i,r,evid,pf){ const o=c.oms[id]; if(!o||o.etapa!=='Em execução') throw new Error('Registre o teste com a ordem Em execução.'); const t=o.chk[i];
  if(!t||t.tipo!=='Teste') throw new Error('Tarefa não é de Teste.'); if(pf!==undefined) manExige(c,pf,'teste',{o});
  if(['Aprovado','Reprovado'].indexOf(r)<0) throw new Error('Escolha Aprovado ou Reprovado.'); if(manVazio(evid)) throw new Error('Anexe a evidência do teste (foto ou leitura do instrumento).');
  const hr=manHr(), quem=manPor(pf); t.tent=(t.tent||[]).concat([{r,evid:String(evid).trim(),por:quem,em:manBr(c.hoje)+' '+hr}]); t.r=r; t.por=quem; t.em=hr; t.nova=false; manToca(o);
  const a=c.ativos[o.aid];
  return {msg:r==='Aprovado'?('Teste aprovado ('+t.tent.length+'ª tentativa) · conclua o serviço; a aptidão do '+(a?a.nome:'ativo')+' é decidida em Em conferência.'):('Teste reprovado ('+t.tent.length+'ª tentativa) · a '+id+' segue Em execução'+(a&&a.cond==='Bloqueado'?' e o '+a.nome+' segue bloqueado':'')+' · refaça o reparo e registre nova tentativa.')}; }
/* "Incluir tarefa": só em Corretiva e Pendência; a preventiva segue a versão do plano */
function manIncluir(c,id,tipo,txt,pf){ const o=c.oms[id]; if(!o) throw new Error('Ordem não encontrada.'); if(['Corretiva','Pendência'].indexOf(o.tipo)<0) throw new Error('A preventiva segue a versão do plano: inclua a tarefa no plano.');
  if(MAN_ABERTAS.indexOf(o.etapa)<0) throw new Error(id+' está '+o.etapa+': não recebe tarefa nova.'); if(pf!==undefined) manExige(c,pf,'incluir',{o});
  if(MAN_TIPOS.indexOf(tipo)<0) throw new Error('Escolha o tipo da tarefa.'); if(manVazio(txt)) throw new Error('Escreva a tarefa.');
  if(o.chk.some(t=>t.t.toLowerCase()===String(txt).trim().toLowerCase())) throw new Error('Esta tarefa já está na ordem.');
  o.chk.push(Object.assign({t:String(txt).trim(),tipo,r:'',mot:'',nova:o.etapa==='Em execução'},tipo==='Medição'?{val:'',un:''}:{})); manToca(o);
  return {msg:'Tarefa incluída na '+id+': '+String(txt).trim()+' ('+tipo+')'+(o.etapa==='Em execução'?' · o executante vê o selo “Tarefa nova”':'')+'.'}; }
/* a OM que trata a condição (D-34): Teste do reparo entra sozinho se o ativo Bloqueado ainda não tem Teste (no Restrito, Medição também vale) */
function manTratar(c,o,ach){ const a=c.ativos[o.aid]; if(!a||a.cond==='Apto') return false; o.trata=true; a.condInfo=a.condInfo||{}; a.condInfo.om=o.id;
  const temT=o.chk.some(t=>t.tipo==='Teste'); const temM=o.chk.some(t=>t.tipo==='Medição');
  if(!temT&&!(a.cond==='Restrito'&&temM)){ const s=(ach&&c.achados[ach])?c.achados[ach].sint:((a.condInfo&&a.condInfo.motivo)||'condição do ativo'); o.chk.push({t:'Teste do reparo · '+s,tipo:'Teste',r:'',mot:'',fixo:true,tent:[]}); }
  return true; }
function manTesteValido(c,o){ const a=c.ativos[o.aid]; const tt=o.chk.filter(t=>t.tipo==='Teste'); if(tt.length&&tt.every(t=>(t.tent||[]).length&&t.tent[t.tent.length-1].r==='Aprovado')) return true;
  const cond=a?(a.cond!=='Apto'?a.cond:((a.condHist||[]).slice(-2)[0]||{}).cond):''; if(!tt.length&&(cond==='Restrito'||(a&&a.cond==='Restrito'))&&o.chk.some(t=>t.tipo==='Medição'&&t.r==='Conforme')) return true; return false; }
/* o que falta para concluir (a mesma regra na web e no app): tarefas, teste, leitura, horas */
function manFaltaConcluir(c,o,leit,horas){ const f=[]; const a=c.ativos[o.aid];
  o.chk.forEach(t=>{ const tp=t.tipo||'Serviço';
    if(tp==='Teste'){ const ul=(t.tent||[]).slice(-1)[0]; if(!ul||ul.r!=='Aprovado') f.push('teste aprovado · '+t.t); return; }
    if(!t.r){ f.push('responder “'+t.t+'”'); return; }
    if(tp==='Medição'&&(t.val===''||t.val===undefined||t.val===null)) f.push('valor de “'+t.t+'”');
    if(MAN_OK.indexOf(t.r)<0&&manVazio(t.mot)) f.push('motivo de “'+t.t+'”'); });
  if(a&&a.un&&manVazio(leit)) f.push('leitura do '+(a.un==='km'?'odômetro':'horímetro'));
  if(manVazio(horas)) f.push('horas de oficina');
  return f; }
function manRefProg(c,s,a,r0,L){ const g=s.gat||{}; const out={data:c.hoje,leit:L};
  if(g.d) out.data=manAdd(r0.data,g.d);
  ['h','km'].forEach(u=>{ if(g[u]&&a&&a.un===u&&r0.leit!==null&&r0.leit!==undefined) out.leit=r0.leit+g[u]; });
  return out; }
/* achado novo ou soma (ativo × componente) a partir de uma resposta da OM (Não conforme / Não foi possível verificar) */
function manAchProx(c,pre){ const ns=Object.keys(c.achados||{}).filter(k=>k.indexOf(pre+'-')===0).map(k=>Number(k.slice(pre.length+1))||0); const piso={SM:150,INSP:104,NC:912}[pre]||0;
  const n=Math.max(piso,ns.length?Math.max.apply(null,ns):0)+1; return pre+'-'+String(n).padStart(pre==='INSP'?3:4,'0'); }
function manAchAberto(c,aid,comp,exceto){ return Object.values(c.achados||{}).find(x=>x.aid===aid&&x.comp===comp&&x.id!==exceto&&(x.estado==='Sem ordem'||x.estado==='Na OM'))||null; }
function manAchDaOm(c,o,t,por){ const a=c.ativos[o.aid]; const oa=o.origAch&&c.achados[o.origAch]; const comp=t.comp||o.comp||(oa?oa.comp:'')||'Outro'; const ab=manAchAberto(c,o.aid,comp);
  if(ab&&(t.ach||[]).indexOf(ab.id)>=0) return ab.id;
  if(ab){ ab.oc=(ab.oc||[]).concat([c.hoje]); ab.rv=(ab.rv||0)+1; return ab.id; }
  const id=manAchProx(c,'NC'); c.achados[id]={id,origem:'Checklist da OM',comp,aid:o.aid,sint:t.t+' · '+t.r+(t.mot?' ('+t.mot+')':''),crit:'Média',sug:'Apto',evid:'',leit:(a&&a.leit?a.leit.val:''),por,em:c.hoje,oc:[c.hoje],estado:'Sem ordem',om:'',nova:true,voltou:o.id,mot:'',rv:0,de:o.id};
  return id; }
/* concluir (término físico): uma regra (F77 + F90); leitura menor recusa (DM:420); implausível é aviso; horas pelo chip ou digitadas (D-18) */
function manConcluir(c,id,leit,horas,forcar,apl,pf){ const o=c.oms[id]; if(!o||o.etapa!=='Em execução') throw new Error(id+' não está Em execução.'); const a=c.ativos[o.aid];
  if(pf!==undefined) manExige(c,pf,'executar',{o});
  const fl=manFaltaConcluir(c,o,leit,horas); if(fl.length) throw new Error('Falta: '+fl.join(' · ')+'.');
  let L=null; if(a&&a.un){ L=manNum(leit); if(isNaN(L)) throw new Error('Leitura inválida.');
    if(a.leit&&L<a.leit.val) throw new Error('Leitura menor que a última registrada ('+manLeitTxt(a)+') · Falta: decidir a leitura (troca de contador) · Otávio.'); }
  const hh=manNum(horas); if(isNaN(hh)||hh<0||hh>200) throw new Error('Horas de oficina inválidas.');
  const qa=(o.pecas||[]).map((p,i)=>{ const t=apl&&apl[i]!==undefined?String(apl[i]).trim():''; const q=t===''?p.qtd:manNum(t);
    if(isNaN(q)||q<0) throw new Error('Quantidade aplicada inválida: '+p.nome+'.');
    if(p.item&&q>p.qtd){ const it=c.itens[p.item]; const disp=it.saldo-it.reservado; if(q-p.qtd>disp) throw new Error('Saldo insuficiente de '+p.nome+' para aplicar '+manN(q,1)+' '+p.un+' (disponível além do reservado: '+manN(Math.max(0,disp),1)+' '+p.un+').'); }
    return q; });
  if(L!==null&&!forcar){ const pl=manPlaus(c,a,L); if(pl) return {nada:true,avisoLeit:true,msg:pl+'. Confira o contador.'}; }
  const por=manPor(pf);
  (o.pecas||[]).forEach((p,i)=>{ const q=qa[i]; if(!p.item){ p.apl=q; p.sob=0; return; } const it=c.itens[p.item];
    it.saldo=Math.max(0,it.saldo-Math.max(p.qtd,q)); it.reservado=Math.max(0,it.reservado-(p.res||0)); p.res=0; p.apl=q; p.sob=Math.max(0,p.qtd-q); });
  const v=o.pid?c.vinc[o.pid+'|'+o.aid]:null; const pl=o.pid?c.planos[o.pid]:null; const novos={}; let prog=false;
  if(v){ (o.cobre||[o.sid]).forEach(sid=>{ const s=pl?manPub(pl).find(x=>x.id===sid):null;
    if(s&&s.base==='prog'){ const r=manRefProg(c,s,a,manRef(v,sid),L); novos[sid]={data:r.data,leit:r.leit,om:id,prog:true}; prog=true; }
    else novos[sid]={data:c.hoje,leit:L,om:id}; }); }
  o.exec={data:c.hoje,leit:L,horas:hh,por}; o.etapa='Em conferência';
  if(a&&L!==null) manLeitura(c,o.aid,L,'Conclusão '+id,pf,c.hoje,'',true);
  let prox='';
  if(v){ v.ult=v.ult||{}; Object.keys(novos).forEach(sid=>{ v.ult[sid]=novos[sid]; });
      const l=manLinhas(c,o.pid).find(x=>x.aid===o.aid&&x.sid===o.sid); if(l) prox=' · ciclo fechado: próxima '+l.s.nome+' em '+manProxTxt(c,l.x)+' ('+l.x.sit.toLowerCase()+')'+(prog?' · conta do vencimento programado':''); }
  const sb=(o.pecas||[]).filter(p=>p.sob>0); if(sb.length) prox+=' · sobra a devolver: '+sb.map(p=>manN(p.sob,1)+' '+p.un+' '+p.nome).join(', ');
  /* respostas → efeitos: Não feito abre Pendência; Não conforme / Não foi possível verificar abre ou soma achado; Conforme resolve o achado vinculado (PRD 54.4, 54.5) */
  const res=[], novosAch=[];
  o.chk.forEach(t=>{ if((t.tipo==='Verificação'||t.tipo==='Medição')&&(t.r==='Não conforme'||t.r==='Não foi possível verificar')){ const aid2=manAchDaOm(c,o,t,por); if(novosAch.indexOf(aid2)<0) novosAch.push(aid2); }
    if(t.tipo==='Verificação'&&t.r==='Conforme') (t.ach||[]).forEach(x=>{ if(res.indexOf(x)<0) res.push(x); }); });
  if(o.trata&&manTesteValido(c,o)&&o.origAch){ (o.achados||[]).forEach(x=>{ const q=c.achados[x]; if(q&&q.aid===o.aid&&!o.chk.some(t=>(t.ach||[]).indexOf(x)>=0)&&res.indexOf(x)<0) res.push(x); }); }
  res.forEach(x=>{ const q=c.achados[x]; if(q&&q.estado!=='Fechado sem serviço'){ q.estado='Resolvido'; q.res={om:id,em:c.hoje}; q.rv=(q.rv||0)+1; } });
  const nf=o.chk.filter(t=>t.r==='Não feito'); o.pend=[];
  nf.forEach(t=>{ const pid='OM-'+String(c.seq).padStart(4,'0'); c.seq++; o.pend.push(pid); const j=manAdd(c.hoje,1);
    c.oms[pid]={id:pid,tipo:'Pendência',aid:o.aid,serv:t.t,crit:'Média',etapa:'A liberar',origem:'Pendência da '+id+' · '+t.mot,de:id,jan:manBr(j),janIso:j,ret:'—',esp:o.esp,tempo:1,executante:o.executante||'',
      chk:[{t:t.t,tipo:'Serviço',r:'',mot:''}],pecas:[],exec:null,selos:[],achados:[],rv:0}; });
  manToca(o);
  return {msg:id+' em conferência'+prox+(o.pend.length?' · '+o.pend.join(', ')+' aberta para o que não foi feito':'')+(novosAch.length?' · achado '+novosAch.join(', ')+' em Sem ordem':'')+(res.length?' · resolvido: '+res.join(', '):'')+(o.trata&&a&&a.cond!=='Apto'?' · '+a.nome+' segue '+a.cond.toLowerCase()+' até a decisão de aptidão':'')+'.'}; }
/* aptidão (CMD-19; D-10): "Declarar apto" só em Em conferência, na OM que trata a condição, com teste válido para o risco */
function manAptoMotivo(c,o){ if(!o) return 'Ordem não encontrada.'; if(!o.trata) return 'Esta ordem não trata a condição do ativo.'; if(o.aptidao) return 'Aptidão já decidida.';
  if(o.etapa!=='Em conferência') return 'Declarar apto só em Em conferência.'; if(!manTesteValido(c,o)) return 'Falta: teste válido (Teste aprovado ou, no Restrito, Medição conforme).'; return ''; }
function manDeclararApto(c,id,pf){ const o=c.oms[id]; const m=manAptoMotivo(c,o); if(m) throw new Error(m); const a=c.ativos[o.aid]; if(pf!==undefined) manExige(c,pf,'condicao',{aid:o.aid});
  const ant=a.cond, por=manPor(pf); a.cond='Apto'; a.condInfo=null; a.condHist=(a.condHist||[]).concat([{cond:'Apto',de:ant,motivo:'Declarado apto pela '+id+' (teste válido)',por,em:c.hoje,om:id}]);
  o.aptidao={dec:'apto',por,em:c.hoje}; manToca(o);
  return {msg:manNome(a)+' apto · CMD-19 por '+por+' na '+id+' · a agenda antiga não é reassumida; volta pela reprogramação do PCP.'}; }
function manManter(c,id,motivo,pf){ const o=c.oms[id]; if(!o||!o.trata) throw new Error('Esta ordem não trata a condição do ativo.'); if(o.aptidao) throw new Error('Aptidão já decidida.');
  if(o.etapa!=='Em conferência') throw new Error('Decida a aptidão em Em conferência.'); if(pf!==undefined) manExige(c,pf,'condicao',{aid:o.aid}); if(manVazio(motivo)) throw new Error('Informe o motivo para manter.');
  const a=c.ativos[o.aid]; const por=manPor(pf); o.aptidao={dec:'manter',motivo:String(motivo).trim(),por,em:c.hoje};
  if(a.condInfo&&a.condInfo.om===id) a.condInfo.om=''; a.condHist=(a.condHist||[]).concat([{cond:a.cond,motivo:'Mantido '+a.cond.toLowerCase()+' na '+id+': '+String(motivo).trim(),por,em:c.hoje,om:id}]); manToca(o);
  return {msg:manNome(a)+' segue '+a.cond.toLowerCase()+' ('+String(motivo).trim()+') · o vínculo com a '+id+' foi desfeito; crie uma ordem corretiva no ativo.'}; }
/* peças retiradas (D-13): destino Recondicionar · Garantia · Sucata, com responsável; nunca volta ao livre */
function manRetirada(c,id,i,dest,resp,pf){ const o=c.oms[id]; if(!o) throw new Error('Ordem não encontrada.'); const r=(o.retiradas||[])[i]; if(!r) throw new Error('Peça retirada não encontrada.');
  if(pf!==undefined){ const m1=manPode(c,pf,'executar',{o}), m2=manPode(c,pf,'ponte'); if(m1&&m2) throw new Error(m1+'. Nada foi alterado.'); }
  if(['Recondicionar','Garantia','Sucata'].indexOf(dest)<0) throw new Error('Escolha o destino: Recondicionar, Garantia ou Sucata.'); if(manVazio(resp)) throw new Error('Informe o responsável pelo destino.');
  r.dest=dest; r.resp=String(resp).trim(); r.por=manPor(pf); r.em=c.hoje; manToca(o);
  return {msg:r.nome+' → '+dest.toLowerCase()+' com '+r.resp+' · não volta ao estoque livre.'}; }
function manSobras(c,id,pf){ const o=c.oms[id]; if(!o) throw new Error('Ordem não encontrada.'); if(pf!==undefined) manExige(c,pf,'ponte'); const sb=(o.pecas||[]).filter(p=>p.sob>0); if(!sb.length) return {nada:true,msg:'Sem sobras nesta ordem.'};
  const rc='AL-'+(412+Object.values(c.oms).filter(x=>x.recibo).length); sb.forEach(p=>{ if(p.item) c.itens[p.item].saldo+=p.sob; p.dev=(p.dev||0)+p.sob; p.sob=0; }); o.recibo=rc; manToca(o);
  return {msg:'Sobras da '+id+' devolvidas (simulado · papel do Almoxarifado) com recibo '+rc+' · '+sb.map(p=>manN(p.dev)+' '+p.un+' '+p.nome).join(', ')+'.'}; }
/* encerrar: uma regra (F79 + F92; D-34): sobras, peças retiradas com destino, decisão de aptidão na OM que trata a condição */
function manFaltaEncerrar(c,o){ const f=[]; const a=c.ativos[o.aid];
  if((o.pecas||[]).some(p=>p.sob>0)) f.push('resolver sobras · Otávio (simulado · papel do Almoxarifado)');
  (o.retiradas||[]).forEach(r=>{ if(!r.dest||r.dest==='A definir'||!r.resp) f.push('destino e responsável de '+r.nome+' · '+(o.executante||'Otávio')); });
  if(o.trata&&!o.aptidao) f.push('Declarar '+(a?a.nome:'o ativo')+' apto ou Manter '+(a&&a.cond!=='Apto'?a.cond.toLowerCase():'a condição')+' · Otávio ou '+manRtTxt(a));
  return f; }
function manEncerrar(c,id,pf){ const o=c.oms[id]; if(!o||o.etapa!=='Em conferência') throw new Error(id+' não está Em conferência.'); if(pf!==undefined) manExige(c,pf,'encerrar');
  const f=manFaltaEncerrar(c,o); if(f.length) throw new Error('Falta: '+f.join(' · ')+'.');
  o.custo=manCusto(c,o); o.etapa='Encerradas'; o.enc={por:manPor(pf),em:c.hoje}; const volta=manVolta(c,o); manToca(o);
  return {msg:id+' encerrada · custo '+manRS(o.custo)+' (peças + '+manN((o.exec||{}).horas||0,1)+' h × Custo R$/h da oficina '+c.custoh+(o.terc?' + terceiro':'')+')'+(volta.length?' · '+volta.join(', ')+' voltou a Sem ordem':'')+'.'}; }
/* volta do achado (D-35): OM encerrada ou cancelada sem Conforme devolve o achado a Sem ordem com "Voltou da OM-xxxx" */
function manVolta(c,o){ const out=[]; (o.achados||[]).forEach(x=>{ const q=c.achados[x]; if(!q||q.estado!=='Na OM'||q.om!==o.id) return; q.estado='Sem ordem'; q.om=''; q.voltou=o.id; q.rv=(q.rv||0)+1; out.push(x); }); return out; }
/* ---------- achados (D-09, D-45, D-48): registrar, somar, decidir ---------- */
const MAN_PREF={'Relato':'SM','Alerta':'SM','Inspeção':'INSP','Checklist da OM':'NC'};
function manAchRegistrar(c,d,pf,chave){ return manCmd(c,chave,'achado',()=>{ if(pf!==undefined) manExige(c,pf,'registrar'); d=d||{}; const a=c.ativos[d.aid]; const er=[];
    if(!a) er.push('ativo'); if(!MAN_PREF[d.origem]) er.push('origem'); if(MAN_COMP.indexOf(d.comp)<0) er.push('componente'); if(manVazio(d.sint)) er.push('sintoma');
    if(['Alta','Média','Baixa'].indexOf(d.crit)<0) er.push('criticidade'); if(['Apto','Restrito','Bloqueado'].indexOf(d.sug)<0) er.push('condição sugerida');
    if(er.length) throw new Error('Informe: '+er.join(', ')+'.');
    const ab=manAchAberto(c,d.aid,d.comp); const por=manPor(pf);
    if(ab&&!d.rep) return {nada:true,rep:ab.id,msg:'Possível repetição de '+ab.id+' ('+ab.sint+') · Somar ou Registrar novo.'};
    if(ab&&d.rep==='somar'){ ab.oc=(ab.oc||[]).concat([c.hoje]); if(!manVazio(d.evid)) ab.evid=(ab.evid?ab.evid+' + ':'')+String(d.evid).trim(); ab.rv=(ab.rv||0)+1;
      if(!manVazio(d.leit)) manLeitura(c,d.aid,manNum(d.leit),'Achado '+ab.id,pf,c.hoje); return {id:ab.id,msg:'Somado ao '+ab.id+' · '+ab.oc.length+' ocorrências.'}; }
    const id=manAchProx(c,MAN_PREF[d.origem]);
    c.achados[id]={id,origem:d.origem,comp:d.comp,aid:d.aid,sint:String(d.sint).trim(),crit:d.crit,sug:d.sug,evid:String(d.evid||'').trim(),leit:manVazio(d.leit)?'':manNum(d.leit),por,em:c.hoje,oc:[c.hoje],estado:'Sem ordem',om:'',nova:true,voltou:'',mot:'',rv:0,os:d.os||''};
    let lm=''; if(!manVazio(d.leit)&&a.un){ const r=manLeitura(c,d.aid,manNum(d.leit),'Achado '+id,pf,c.hoje); lm=r.msg?' · '+r.msg:''; }
    let bm=''; if(d.bloquear&&d.sug==='Bloqueado'){ manCondicao(c,d.aid,'bloquear',{motivo:String(d.sint).trim(),evid:d.evid,achado:id},pf); bm=' · '+a.nome+' bloqueado'; }
    return {id,msg:'Achado '+id+' registrado · '+manNome(a)+' · '+d.comp+bm+lm+(d.os?' · ligado à '+d.os:'')}; }); }
/* OM aberta do ativo que aceita vínculo: A liberar, Liberadas ou Em execução (M:281); nunca Em conferência (D-35) */
function manOmVinc(c,aid){ return Object.values(c.oms).filter(o=>o.aid===aid&&MAN_ABERTAS.indexOf(o.etapa)>=0).sort((a,b)=>(a.janIso||'').localeCompare(b.janIso||''))[0]||null; }
function manAchVenc(c,aid){ return manSemOm(c).filter(l=>l.aid===aid).sort((a,b)=>manIniJanela(a.x)-manIniJanela(b.x))[0]||null; }
/* primária do painel do achado, por precedência (§3.2) e as secundárias */
function manAchOpcoes(c,id){ const q=c.achados[id]; if(!q) return {prim:null,sec:[]}; if(q.estado!=='Sem ordem') return {prim:null,sec:[]};
  const om=manOmVinc(c,q.aid), vn=manAchVenc(c,q.aid); const amanha=manAdd(c.hoje,1); const grave=q.crit==='Alta'||q.sug==='Bloqueado';
  const vinc=om&&(!grave||(om.janIso&&om.janIso<=amanha))?{k:'vincular',t:'Vincular à '+om.id,om:om.id}:null;
  const ger=vn?{k:'gerar',t:'Gerar ordem preventiva com '+id,vk:vn.vk,sid:vn.sid}:null; const cor={k:'corretiva',t:'Criar ordem corretiva'};
  let prim; if(grave) prim=cor; else if(vinc) prim=vinc; else if(ger) prim=ger; else prim=cor;
  const sec=[vinc,ger,cor].filter(x=>x&&x.k!==prim.k).concat([{k:'fechar',t:'Fechar sem serviço'}]); return {prim,sec}; }
/* tarefa de Verificação do achado (D-31): achados do mesmo ativo e componente viram uma Verificação só */
function manVerifAch(o,q){ const t=o.chk.find(x=>x.tipo==='Verificação'&&x.comp===q.comp&&(x.ach||[]).length);
  if(t){ if(t.ach.indexOf(q.id)<0){ t.ach.push(q.id); t.t=t.t+' · '+q.sint; } return t; }
  const n={t:'Verificar: '+q.sint,tipo:'Verificação',r:'',mot:'',comp:q.comp,ach:[q.id],nova:o.etapa==='Em execução'}; o.chk.push(n); return n; }
function manAchVincular(c,id,omId,pf){ const q=c.achados[id]; if(!q) throw new Error('Achado não encontrado.'); if(pf!==undefined) manExige(c,pf,'decidir');
  if(q.estado==='Na OM'&&q.om===omId) return {nada:true,id:omId,msg:id+' já está na '+omId+' · nenhuma tarefa nova.'};
  if(q.estado!=='Sem ordem') throw new Error(id+' está '+q.estado.toLowerCase()+'.');
  const o=c.oms[omId]; if(!o||o.aid!==q.aid) throw new Error('Ordem do mesmo ativo não encontrada.'); if(MAN_ABERTAS.indexOf(o.etapa)<0) throw new Error(omId+' está '+o.etapa+': vincule só a ordem em A liberar, Liberadas ou Em execução.');
  o.achados=(o.achados||[]); if(o.achados.indexOf(id)<0) o.achados.push(id); manVerifAch(o,q);
  q.estado='Na OM'; q.om=omId; q.nova=false; q.voltou=''; q.dec={k:'vincular',por:manPor(pf),em:c.hoje}; q.rv=(q.rv||0)+1; manToca(o);
  return {id:omId,msg:'Achado '+id+' vinculado à '+omId+' · vira a tarefa “Verificar: '+q.sint+'”'+(o.etapa==='Em execução'?' (selo Tarefa nova para '+o.executante+')':'')+' · nenhuma ordem nova.'}; }
function manAchGerar(c,id,pf,chave){ return manCmd(c,chave,'achGerar',()=>{ const q=c.achados[id]; if(!q) throw new Error('Achado não encontrado.'); if(pf!==undefined) manExige(c,pf,'decidir');
    if(q.estado==='Na OM') return {nada:true,id:q.om,msg:id+' já está na '+q.om+'.'}; const vn=manAchVenc(c,q.aid); if(!vn) throw new Error('Nenhum vencimento devido sem ordem no '+(c.ativos[q.aid]||{}).nome+'.');
    const g=manGerar(c,vn.vk,vn.sid); const omId=g.id; const v=manAchVincular(c,id,omId);
    return {id:omId,msg:g.msg.replace(/\.$/,'')+' · com '+id+' vinculado.'}; }); }
function manAchCorretiva(c,id,pf,chave){ return manCmd(c,chave,'achCorretiva',()=>{ const q=c.achados[id]; if(!q) throw new Error('Achado não encontrado.'); if(pf!==undefined) manExige(c,pf,'decidir');
    if(q.estado==='Na OM'&&q.om) return {nada:true,id:q.om,msg:id+' já está na '+q.om+' · nenhuma ordem nova.'}; if(q.estado!=='Sem ordem') throw new Error(id+' está '+q.estado.toLowerCase()+'.');
    const a=c.ativos[q.aid]; const oid='OM-'+String(c.seq).padStart(4,'0'); c.seq++; const esp=a.classe==='Irrigação'?'Eletricista':'Mecânico';
    const o={id:oid,tipo:'Corretiva',aid:a.id,serv:'Corretiva · '+q.comp.toLowerCase()+' · '+q.sint,comp:q.comp,crit:q.crit,etapa:'A liberar',origem:id+' · '+q.origem.toLowerCase()+(q.os?' · '+q.os:''),
      jan:'',janIso:'',ret:'',esp,tempo:null,executante:'',chk:[],pecas:[],exec:null,selos:[],achados:[id],origAch:id,rv:0};
    c.oms[oid]=o; const pj=manProxLivre(c,o)||manAdd(c.hoje,1); o.janIso=pj; o.jan=manBr(pj); o.ret=manBr(pj)+' 17:00';
    const trata=(a.cond!=='Apto'&&!(a.condInfo&&a.condInfo.om&&c.oms[a.condInfo.om]&&manAberta(c.oms[a.condInfo.om])))?manTratar(c,o,id):false;
    if(!trata) manVerifAch(o,q);
    q.estado='Na OM'; q.om=oid; q.nova=false; q.voltou=''; q.dec={k:'corretiva',por:manPor(pf),em:c.hoje}; q.rv=(q.rv||0)+1;
    return {id:oid,msg:oid+' criada em A liberar · '+manNome(a)+' · '+q.comp+' · '+q.crit+' · janela '+manBr(pj)+(trata?' · trata a condição ('+a.cond+'): Teste do reparo incluído':'')+' · informe o tempo previsto para liberar.'}; }); }
function manAchFechar(c,id,mot,pf){ const q=c.achados[id]; if(!q) throw new Error('Achado não encontrado.'); if(pf!==undefined) manExige(c,pf,'decidir');
  if(q.estado!=='Sem ordem') throw new Error(id+' está '+q.estado.toLowerCase()+'.'); if(manVazio(mot)) throw new Error('Informe o motivo para fechar sem serviço.');
  q.estado='Fechado sem serviço'; q.mot=String(mot).trim(); q.nova=false; q.dec={k:'fechar',por:manPor(pf),em:c.hoje}; q.rv=(q.rv||0)+1;
  return {msg:id+' fechado sem serviço · '+q.mot+'.'}; }
function manAchCrit(c,id,crit,pf){ const q=c.achados[id]; if(!q) throw new Error('Achado não encontrado.'); if(pf!==undefined) manExige(c,pf,'decidir'); if(['Alta','Média','Baixa'].indexOf(crit)<0) throw new Error('Criticidade inválida.');
  if(q.crit===crit) return {nada:true}; q.crit=crit; q.nova=false; q.rv=(q.rv||0)+1; return {msg:id+' · criticidade '+crit+'.'}; }
/* corretiva pela condição (detalhe do ativo Bloqueado sem OM que trate, ex.: depois de "Manter"): herda o motivo e ganha o Teste do reparo */
function manCorretivaAtivo(c,aid,pf,chave){ return manCmd(c,chave,'corretivaAtivo',()=>{ const a=c.ativos[aid]; if(!a) throw new Error('Ativo não encontrado.'); if(pf!==undefined) manExige(c,pf,'decidir');
    const i=a.condInfo||{}; if(i.om&&c.oms[i.om]&&manAberta(c.oms[i.om])) return {nada:true,id:i.om,msg:'A '+i.om+' já trata a condição do '+a.nome+'.'};
    if(i.achado&&c.achados[i.achado]&&c.achados[i.achado].estado==='Sem ordem') return manAchCorretiva(c,i.achado);
    const oid='OM-'+String(c.seq).padStart(4,'0'); c.seq++; const esp=a.classe==='Irrigação'?'Eletricista':'Mecânico';
    const o={id:oid,tipo:'Corretiva',aid,serv:'Corretiva · '+(i.motivo||a.cond),crit:'Alta',etapa:'A liberar',origem:'Condição '+a.cond+' · '+(i.motivo||''),jan:'',janIso:'',ret:'',esp,tempo:null,executante:'',chk:[],pecas:[],exec:null,selos:[],achados:[],rv:0};
    c.oms[oid]=o; const pj=manProxLivre(c,o)||manAdd(c.hoje,1); o.janIso=pj; o.jan=manBr(pj); o.ret=manBr(pj)+' 17:00'; manTratar(c,o,'');
    return {id:oid,msg:oid+' criada em A liberar · trata a condição do '+a.nome+' (Teste do reparo incluído) · informe o tempo previsto para liberar.'}; }); }
/* marco sugerido do vínculo (D-41): última OM encerrada do mesmo serviço, ou de um que o "cumpre também"; corretiva nunca serve */
function manMarcoSug(c,p,aid){ const nomes=manWork(p).concat(manPub(p)).map(s=>String(s.nome).toLowerCase()); let best=null;
  Object.values(c.oms).forEach(o=>{ if(o.aid!==aid||o.tipo!=='Preventiva'||o.etapa!=='Encerradas'||!o.exec) return; const pl=o.pid?c.planos[o.pid]:null;
    const cob=[String(o.serv).toLowerCase()].concat(pl?manPub(pl).filter(s=>(o.cobre||[]).indexOf(s.id)>=0).map(s=>String(s.nome).toLowerCase()):[]);
    if(!nomes.some(n=>cob.indexOf(n)>=0)) return; if(!best||o.exec.data>best.data) best={data:o.exec.data,leit:o.exec.leit,om:o.id}; });
  return best; }
/* ---------- condição única (CMD-18, PRD 47.3 l.7720; D-10, D-34): painel Condição ---------- */
function manCondicao(c,aid,acao,d,pf){ const a=c.ativos[aid]; if(!a) throw new Error('Ativo não encontrado.'); if(pf!==undefined) manExige(c,pf,'condicao',{aid}); d=d||{}; const por=manPor(pf);
  const hist=(x)=>{ a.condHist=(a.condHist||[]).concat([Object.assign({por,em:c.hoje},x)]); };
  if(acao==='rt'){ if(manVazio(d.rt)) throw new Error('Escolha o responsável técnico.'); if(manVazio(d.motivo)) throw new Error('Informe o motivo da troca.'); const de=a.rt; a.rt=String(d.rt).trim();
    hist({cond:a.cond,motivo:'Responsável técnico: '+de+' → '+a.rt+' ('+String(d.motivo).trim()+')'}); return {msg:'Responsável técnico do '+a.nome+': '+a.rt+'.'}; }
  if(acao==='bloquear'){ if(a.cond==='Bloqueado') return {nada:true,msg:a.nome+' já está bloqueado.'}; if(manVazio(d.motivo)) throw new Error('Informe o motivo do bloqueio.');
    a.cond='Bloqueado'; a.condInfo={motivo:String(d.motivo).trim(),desde:c.hoje,por,evid:String(d.evid||'').trim(),achado:d.achado||'',om:'',ate:'',lim:''};
    let t=''; if(d.om){ const o=c.oms[d.om]; if(!o||o.aid!==aid||MAN_ABERTAS.indexOf(o.etapa)<0) throw new Error('Escolha uma ordem aberta do mesmo ativo.'); manTratar(c,o,d.achado); manToca(o); t=' · tratado na '+o.id; }
    hist({cond:'Bloqueado',motivo:a.condInfo.motivo,achado:a.condInfo.achado,om:a.condInfo.om||''});
    return {msg:a.nome+' bloqueado (CMD-18) · '+a.condInfo.motivo+t+' · as O.S. que usam o ativo ficam impedidas.'}; }
  if(acao==='restringir'){ if(manVazio(d.motivo)) throw new Error('Informe o motivo da restrição.'); if(manVazio(d.lim)) throw new Error('Informe os limites de operação.');
    if(manVazio(d.ate)) throw new Error('Informe o prazo da restrição.'); if(d.ate<c.hoje) throw new Error('O prazo não pode ser anterior a hoje.');
    if(a.cond==='Bloqueado') throw new Error(a.nome+' está bloqueado: a saída é Declarar apto na ordem que trata a condição.');
    a.cond='Restrito'; a.condInfo={motivo:String(d.motivo).trim(),desde:c.hoje,por,evid:String(d.evid||'').trim(),achado:d.achado||'',om:'',ate:d.ate,lim:String(d.lim).trim()};
    if(d.om){ const o=c.oms[d.om]; if(o&&o.aid===aid&&MAN_ABERTAS.indexOf(o.etapa)>=0){ manTratar(c,o,d.achado); manToca(o); } }
    hist({cond:'Restrito',motivo:a.condInfo.motivo,ate:d.ate,om:a.condInfo.om||''}); return {msg:a.nome+' restrito até '+manBr(d.ate)+' · '+a.condInfo.lim+'.'}; }
  if(acao==='encerrar'){ if(a.cond!=='Restrito') throw new Error('Encerrar restrição só com o ativo Restrito.');
    const om=a.condInfo&&a.condInfo.om&&c.oms[a.condInfo.om]; if(om&&manAberta(om)) throw new Error('A '+om.id+' trata a restrição: a saída é Declarar apto nela.');
    if(manVazio(d.motivo)) throw new Error('Informe o motivo.'); if(manVazio(d.evid)) throw new Error('Informe a evidência (medição).');
    a.cond='Apto'; a.condInfo=null; hist({cond:'Apto',de:'Restrito',motivo:'Restrição encerrada: '+String(d.motivo).trim()+' · '+String(d.evid).trim()}); return {msg:'Restrição do '+a.nome+' encerrada · Apto.'}; }
  throw new Error('Ação de condição desconhecida.'); }
function manRestricaoVencida(c,a){ return !!(a&&a.cond==='Restrito'&&a.condInfo&&a.condInfo.ate&&a.condInfo.ate<c.hoje); }
/* ---------- leitura: uma função para abastecimento, conclusão, achado e leitura avulsa (D-40); histórico em c.leituras ---------- */
function manPlaus(c,a,n,data){ if(!a||!a.un||!a.leit||isNaN(n)) return ''; const md=(c.maxdia||{h:24,km:1500})[a.un]||24;
  const dias=Math.max(1,manDias(a.leit.data,data||c.hoje)); const lim=dias*md, d=n-a.leit.val;
  return d>lim?('Leitura de '+manQ(n,a.un)+' fica '+manQ(d,a.un)+' acima da última ('+manLeitTxt(a)+'), mais que '+manQ(lim,a.un)+' possíveis em '+dias+(dias>1?' dias':' dia')):''; }
function manLtId(c){ const ns=(c.leituras||[]).map(x=>Number(String(x.id).slice(3))||0); return 'LT-'+String((ns.length?Math.max.apply(null,ns):0)+1).padStart(4,'0'); }
function manLeitura(c,aid,val,origem,pf,data,ab,conclusao){ const a=c.ativos[aid]; if(!a||!a.un) return {msg:''}; const n=Number(val); if(isNaN(n)) return {msg:''}; data=data||c.hoje;
  c.leituras=c.leituras||[]; const por=pf===undefined?'':(typeof pf==='string'?pf:manPor(pf)); const lt={id:manLtId(c),aid,val:n,un:a.un,data,origem,qual:'Confirmada',por,ab:ab||''};
  const prevSus=()=>{ if(a.suspeita){ const e=c.leituras.find(x=>x.id===a.suspeita.lt); if(e&&e.qual==='A confirmar') e.qual='Substituída'; const b=(c.abast||[]).find(x=>x.id===a.suspeita.ab); if(b&&b.qual==='A confirmar') b.qual='Substituída'; } };
  /* tíquete com data anterior à última: comparado com as leituras vizinhas; entra no histórico sem mudar a atual e sem pedir troca (D-40) */
  if(a.leit&&data<a.leit.data){ const hs=c.leituras.filter(x=>x.aid===aid&&['Confirmada','Troca de contador'].indexOf(x.qual)>=0);
    const ant=hs.filter(x=>x.data<=data).sort((x,y)=>x.data.localeCompare(y.data)).slice(-1)[0], dep=hs.filter(x=>x.data>data).sort((x,y)=>x.data.localeCompare(y.data))[0];
    const ok=(!ant||n>=ant.val)&&(!dep||n<=dep.val); lt.qual=ok?'Confirmada':'A confirmar'; lt.antiga=true; c.leituras.push(lt);
    return {lt:lt.id,qual:lt.qual,msg:'Leitura de '+manQ(n,a.un)+' em '+manBr(data)+' no histórico'+(ok?' · coerente com as vizinhas':' · fora das vizinhas, a confirmar')+' · a leitura atual segue '+manLeitTxt(a)+'.'}; }
  if(!conclusao&&a.leit&&n<a.leit.val){ prevSus(); lt.qual='A confirmar'; c.leituras.push(lt); a.suspeita={val:n,data,origem,ab:ab||'',lt:lt.id,tipo:'menor'};
    return {lt:lt.id,qual:lt.qual,sus:'menor',msg:'Leitura de '+manQ(n,a.un)+' menor que a anterior ('+manLeitTxt(a)+') · confirme a troca de contador ou descarte; os vencimentos seguem na leitura anterior.'}; }
  const pl=conclusao?'':manPlaus(c,a,n,data); if(pl){ prevSus(); lt.qual='A confirmar'; c.leituras.push(lt); a.suspeita={val:n,data,origem,ab:ab||'',lt:lt.id,tipo:'alta'};
    return {lt:lt.id,qual:lt.qual,sus:'alta',msg:pl+' · confirme ou descarte; os vencimentos seguem na leitura anterior.'}; }
  prevSus(); const antes=manLinhas(c).filter(l=>l.aid===aid&&l.s).map(l=>l.x.sit); a.leit={val:n,data,origem}; delete a.suspeita; c.leituras.push(lt);
  const dep=manLinhas(c).filter(l=>l.aid===aid&&l.s); const mud=dep.filter((l,i)=>l.x.sit!==antes[i]);
  return {lt:lt.id,qual:lt.qual,msg:manNome(a)+' em '+manQ(n,a.un)+(mud.length?' · '+mud.map(l=>l.s.nome+': '+l.x.sit.toLowerCase()).join(' · '):' · vencimentos recalculados')+'.'}; }
function manLeituraAvulsa(c,aid,val,data,pf,chave){ return manCmd(c,chave,'leitura',()=>{ if(pf!==undefined) manExige(c,pf,'registrar'); const a=c.ativos[aid]; if(!a) throw new Error('Escolha o ativo.'); if(!a.un) throw new Error(a.nome+' não tem contador.');
    const n=manNum(val); if(isNaN(n)||n<0) throw new Error('Informe a leitura com '+a.un+'.'); if(data&&data>c.hoje) throw new Error('A data não pode ser futura.'); return manLeitura(c,aid,n,'Leitura avulsa',pf,data||c.hoje); }); }
/* decidir a leitura a confirmar: alta vira atual; menor é troca de contador (o histórico passa à escala do contador novo) */
function manLeituraOk(c,aid,pf){ if(pf!==undefined) manExige(c,pf,'leituraDecidir'); const a=c.ativos[aid]; const s=a&&a.suspeita; if(!s) throw new Error('Nenhuma leitura a confirmar.');
  const e=(c.abast||[]).find(x=>x.id===s.ab); const lt=(c.leituras||[]).find(x=>x.id===s.lt);
  const antes=manLinhas(c).filter(l=>l.aid===aid&&l.s).map(l=>l.x.sit);
  if(s.tipo==='menor'){ const delta=a.leit.val-s.val; const ck=()=>{ const m={}; manLinhas(c).filter(l=>l.aid===aid&&l.s).forEach(l=>{ m[l.vk+'#'+l.sid]=l.ciclo; }); return m; };
    const c0=ck(); const sh=(r)=>{ if(r&&r.leit!==null&&r.leit!==undefined) r.leit=r.leit-delta; };
    Object.keys(c.vinc).filter(k=>k.split('|')[1]===aid).forEach(k=>{ const v=c.vinc[k]; sh(v.marco); Object.values(v.ult||{}).forEach(sh); });
    (a.trocas=a.trocas||[]).push({data:c.hoje,de:a.leit.val,para:s.val,ab:s.ab}); a.leit={val:s.val,data:s.data||c.hoje,origem:'Troca de contador · '+(s.ab||s.origem)}; delete a.suspeita;
    const c1=ck(); Object.values(c.oms).filter(o=>o.aid===aid&&o.ciclos&&o.pid).forEach(o=>{ Object.keys(o.ciclos).forEach(sid=>{ const k=o.pid+'|'+aid+'#'+sid; if(c0[k]&&o.ciclos[sid]===c0[k]) o.ciclos[sid]=c1[k]; }); });
    if(e) e.qual='Troca de contador'; if(lt) lt.qual='Troca de contador';
    return {msg:'Troca de contador confirmada: '+manNome(a)+' passa a '+manQ(s.val,a.un)+' · histórico ajustado em '+manQ(delta,a.un)+' · vencimentos mantidos.'}; }
  a.leit={val:s.val,data:s.data||c.hoje,origem:s.origem}; delete a.suspeita; if(e) e.qual='Confirmada'; if(lt) lt.qual='Confirmada';
  const dep=manLinhas(c).filter(l=>l.aid===aid&&l.s); const mud=dep.filter((l,i)=>l.x.sit!==antes[i]);
  return {msg:'Leitura confirmada: '+manNome(a)+' em '+manQ(s.val,a.un)+(mud.length?' · '+mud.map(l=>l.s.nome+': '+l.x.sit.toLowerCase()).join(' · '):' · vencimentos recalculados')+'.'}; }
function manLeituraDescartar(c,aid,pf){ if(pf!==undefined) manExige(c,pf,'leituraDecidir'); const a=c.ativos[aid]; const s=a&&a.suspeita; if(!s) throw new Error('Nenhuma leitura a confirmar.');
  const e=(c.abast||[]).find(x=>x.id===s.ab); const lt=(c.leituras||[]).find(x=>x.id===s.lt);
  delete a.suspeita; if(e) e.qual='Descartada'; if(lt) lt.qual='Descartada';
  return {msg:'Leitura de '+manQ(s.val,a.un)+' descartada'+(s.ab?' ('+s.ab+')':'')+' · '+manNome(a)+' segue em '+manLeitTxt(a)+'.'}; }
/* ---------- abastecimento (RF-AST-006; D-15, D-19): um lançamento, L/h só com método (tanque cheio), estorno com lançamento novo ---------- */
function manAbProx(c,pre){ const ns=(c.abast||[]).filter(x=>String(x.id).indexOf(pre+'-')===0).map(x=>Number(String(x.id).slice(pre.length+1))||0); return pre+'-'+String((ns.length?Math.max.apply(null,ns):(pre==='ES'?87:1042))+1).padStart(4,'0'); }
function manLh(c,b){ if(!b||b.tipo||b.qual==='Estornado'||!b.cheio||b.leit===null||b.leit===undefined) return null;
  const ant=(c.abast||[]).filter(x=>x.aid===b.aid&&!x.tipo&&x.qual!=='Estornado'&&x.cheio&&x.leit!==null&&x.leit!==undefined&&x.leit<b.leit&&(x.data+(x.hora||''))<=(b.data+(b.hora||''))&&x.id!==b.id)
    .sort((x,y)=>y.leit-x.leit)[0]; if(!ant) return null; const dh=b.leit-ant.leit; if(dh<=0) return null; return {lh:b.vol/dh,de:ant.id,h:dh}; }
function manAbastecer(c,d,pf,chave){ return manCmd(c,chave,'abast',()=>{ if(pf!==undefined) manExige(c,pf,'registrar'); d=d||{}; const a=c.ativos[d.aid]; const er=[];
    if(!a) er.push('ativo'); if(manVazio(d.tq)) er.push('tanque/lote'); const vol=manNum(d.vol); if(isNaN(vol)||vol<=0) er.push('volume em L');
    if(a&&a.un&&manVazio(d.leit)) er.push('leitura ('+a.un+')'); if(manVazio(d.op)) er.push('operador');
    if(er.length) throw new Error('Informe: '+er.join(', ')+'.'); if(vol>2000) throw new Error('Volume acima de 2.000 L num lançamento: confira.');
    const data=d.data||c.hoje; if(data>c.hoje) throw new Error('A data não pode ser futura.');
    const id=manAbProx(c,'AB'); const L=a.un?manNum(d.leit):null; if(a.un&&(isNaN(L)||L<0)) throw new Error('Leitura inválida.');
    const b={id,aid:a.id,tq:d.tq,vol,data,hora:d.hora||manHr(),leit:L,un:a.un,op:d.op,evid:String(d.evid||'').trim(),cheio:!!d.cheio,qual:'Confirmada',por:manPor(pf),os:d.os||''};
    c.abast=(c.abast||[]).concat([b]); let m={msg:''}; if(a.un){ m=manLeitura(c,a.id,L,'Abastecimento '+id,pf,data,id); b.qual=m.qual||'Confirmada'; b.lt=m.lt; }
    const lh=manLh(c,b);
    return {id,msg:'Lançamento '+id+' registrado · '+manNome(a)+' · '+manN(vol)+' L'+(lh?' · '+manN(lh.lh,1)+' L/h (tanque cheio)':'')+(m.msg?' · '+m.msg:'')}; }); }
function manEstornar(c,id,motivo,pf,chave){ return manCmd(c,chave,'estorno',()=>{ if(pf!==undefined) manExige(c,pf,'estorno'); const b=(c.abast||[]).find(x=>x.id===id); if(!b||b.tipo) throw new Error('Lançamento não encontrado.');
    if(b.qual==='Estornado') return {nada:true,msg:id+' já foi estornado ('+b.estorno+').'}; if(manVazio(motivo)) throw new Error('Informe o motivo do estorno.');
    const es=manAbProx(c,'ES'); c.abast.push({id:es,tipo:'Estorno',ref:id,aid:b.aid,tq:b.tq,vol:-b.vol,data:c.hoje,hora:manHr(),leit:null,un:b.un,op:b.op,evid:'',cheio:false,qual:'Estorno',motivo:String(motivo).trim(),por:manPor(pf)});
    b.qual='Estornado'; b.estorno=es; const lt=(c.leituras||[]).find(x=>x.id===b.lt); if(lt&&lt.qual==='A confirmar'){ const a=c.ativos[b.aid]; if(a&&a.suspeita&&a.suspeita.lt===lt.id) delete a.suspeita; lt.qual='Descartada'; }
    return {id:es,msg:'Estorno '+es+' lançado para '+id+' ('+String(motivo).trim()+') · o original fica no histórico; registre o lançamento correto.'}; }); }
/* ---------- indicadores (PRD 55.2: até 4 cartões; "não calculável" sem dado) ---------- */
function manPeriodo(c,k){ const h=c.hoje; if(k==='30d') return {de:manAdd(h,-30),ate:h,t:'30 d'}; if(k==='12m') return {de:manAdd(h,-365),ate:h,t:'12 m'};
  const M=['jan','fev','mar','abr','mai','jun','jul','ago','set','out','nov','dez']; return {de:h.slice(0,8)+'01',ate:h,t:M[Number(h.slice(5,7))-1]+'/'+h.slice(0,4)}; }
function manCustoPeriodo(c,k,aid){ const P=manPeriodo(c,k); let enc=0, and=0;
  Object.values(c.oms).forEach(o=>{ if(aid&&o.aid!==aid) return; if(o.etapa==='Encerradas'&&o.exec&&o.exec.data>=P.de&&o.exec.data<=P.ate) enc+=manCustoFinal(c,o);
    else if(manAberta(o)&&o.etapa!=='A liberar') and+=manCusto(c,o,'est'); }); return {enc,and,P}; }
function manCumprimento(c,k){ const P=manPeriodo(c,k); const os=Object.values(c.oms).filter(o=>o.tipo==='Preventiva'&&o.etapa==='Encerradas'&&o.vencOrig&&o.exec&&o.exec.data>=P.de&&o.exec.data<=P.ate);
  if(!os.length) return null; const ok=os.filter(o=>o.exec.data<=o.vencOrig).length; return {ok,n:os.length,pct:Math.round(ok*100/os.length)}; }
/* acesso para os testes de navegador (mesmo padrão do window.__cen da O.S.) */
try { window.__man = { manGet, manClone, manLinhas, manVenc, manGerar, manGerarTodas, manLiberar, manConcluir, manReset, manLeitura, manLeituraOk, manLeituraDescartar, manSolicitar, manReceber, manPlaus, manNum,
  manConflito, manProxLivre, manMover, manPode, manAchOpcoes, manCusto, manCustoFinal, manTesteValido, manFaltaEncerrar, manFaltaConcluir, manMarcoSug }; } catch (e) {}
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
    s = seed()
    enc = [k for k, o in s['oms'].items() if o['etapa'] == 'Encerradas']
    assert {'OM-0102', 'OM-0118', 'OM-0181', 'OM-0205', 'OM-0207', 'OM-0212', 'OM-0219', 'OM-0221', 'OM-0222', 'OM-0225', 'OM-0229', 'OM-0231'} == set(enc), enc
    assert sorted(s['achados']) == ['INSP-104', 'INSP-105', 'NC-0912', 'SM-0147', 'SM-0150', 'SM-0152'], s['achados'].keys()
    print('autoteste ok ·', len(L), 'vencimentos ·', len(devidas), 'devidos ·', 'sem plano:', ', '.join(sem_plano), '·', len(enc), 'OMs encerradas no histórico')
