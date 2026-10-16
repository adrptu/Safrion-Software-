# -*- coding: utf-8 -*-
"""Manutenção · estado e regras num só lugar (PCM simplificado v2, docs/pcm-simplificado/ESPECIFICACAO.md).

Fonte única dos dados de demonstração e das regras da manutenção (tela MA, CD-03, O.S. e app):
- ativos com a identidade do CD-03 (dados_cad.ATIVOS) + Comboio CB-01; leitura, ritmo, condição única com histórico e responsável técnico (D-49);
- planos PM-01..PM-10 com tarefas tipadas (D-11: {t, tipo}), vínculos e vencimento ("o que vencer primeiro");
- ordens (OM) com executante (D-37), versão do registro o.rv (D-46), tarefas por tipo, Teste com tentativas (D-36), peças retiradas (D-13);
- histórico encerrado sintético a partir de VINCULOS.ult (D-43), custo pela função única manCusto;
- achados (c.achados, D-09/D-45/D-48), leituras com histórico (c.leituras, D-40), abastecimentos (c.abast, D-15/D-19) e recibos (c.recibos, D-30);
- conflito com a produção calculado sobre a alocação da semana (alocacao.py, a mesma de O.S. › Recursos; D-38);
- matriz papel × comando (D-33): Otávio (PCM), Zé (mecânico), João (irrigante, eletricista NR-10; revisão 09/10), Ana (gestora), pelo perfil de demonstração (g2lib G2_PERFIS).
Hoje da demonstração: 23/09/2026. "Em breve" = a janela (vencimento − tolerância) começa em até 10 dias.
vencimento() é a mesma fórmula do manVenc() do JS (paridade conferida em ma_regras_test.py e ma_planos_test.py).
Estado v=4 (S2): estado salvo de versão antiga volta ao seed (D-47). Desde o 1a, o estado vive em c.man do cenário único (cenario.py v=5 desde a junção com a Colheita)."""
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
# responsável técnico do ativo (D-49; antes um mapa local do MA-01): a01, a02, a05 → Zé; a11, a15, a12 → João (irrigante, NR-10); demais → Otávio.
# Revisão de 09/10 (S4): "Equipe elétrica" não é pessoa do CD-04; o responsável técnico é sempre uma pessoa (a lista do painel vem de pessoas()).
RT = {'a01': 'Zé', 'a02': 'Zé', 'a05': 'Zé', 'a11': 'João', 'a15': 'João', 'a12': 'João'}
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
                            condInfo=(dict(ci, cond=x['cond']) if ci else None), rt=RT.get(a['id'], 'Otávio'),
                            condHist=([dict(cond=x['cond'], motivo=ci['motivo'], por=ci['por'], em=ci['desde'], achado=ci['achado'], om=ci['om'], ate=ci['ate'])] if ci else []),
                            leit=(dict(val=x['leit'][0], data=x['leit'][1], origem=x['leit'][2]) if x['leit'] else None))
    out['cb01'] = dict(id='cb01', nome='Comboio CB-01', modelo='caminhão comboio 6 m³', classe='Veículo', grupo='Veículos', local='Sede',
                       un='km', ritmo=80, cond='Apto', lh=None, condInfo=None, rt='Otávio', condHist=[],
                       leit=dict(val=48200, data='2026-09-23', origem='Abastecimento AB-1040'))
    return out


ATIVOS = _ativos()
ORDEM_ATIVOS = [a['id'] for a in DC.ATIVOS] + ['cb01']

# ---------- itens de estoque da manutenção (grupo Peças / Lubrificantes) · saldo próprio até o 1b ----------
# min = ponto de pedido e max = repor até (V69, Compras › Materiais: saldo livre + já pedido abaixo do min sugere a reposição até o max)
ITENS = {
 'KIT-MF7719': dict(nome='Kit filtros MF 7719', un='kit', saldo=2, reservado=0, preco=690, min=1, max=3),
 'FIL-MF4292': dict(nome='Filtro de óleo MF 4292', un='un', saldo=0, reservado=0, preco=160, min=2, max=4),
 'KIT-JD': dict(nome='Kit filtros John Deere', un='kit', saldo=3, reservado=0, preco=740, min=1, max=3),
 'KIT-U3030': dict(nome='Kit filtros Uniport 3030', un='kit', saldo=3, reservado=0, preco=520, min=1, max=3),
 'KIT-C7250': dict(nome='Kit filtros Case IH 7250', un='kit', saldo=1, reservado=0, preco=1350, min=1, max=2),
 'KIT-CB01': dict(nome='Kit filtros caminhão comboio', un='kit', saldo=1, reservado=0, preco=480, min=1, max=2),
 'OL-1540': dict(nome='Óleo de motor 15W-40', un='L', saldo=120, reservado=0, preco=28, min=60, max=200),
 'OL-HID68': dict(nome='Óleo hidráulico 68', un='L', saldo=200, reservado=0, preco=24, min=60, max=200),
 'GR-EP2': dict(nome='Graxa EP2', un='kg', saldo=18, reservado=0, preco=32, min=20, max=40),
 'VED-MB': dict(nome='Kit vedação da motobomba', un='kit', saldo=1, reservado=0, preco=380, min=1, max=2),
 'DSC-15': dict(nome='Disco de corte 15"', un='un', saldo=24, reservado=0, preco=210, min=8, max=24),
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
        if nr or p['id'] == 'p14':   # p14 Otávio (PCM; p11 até a v56)
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
REC_DO_ATIVO = AL.REC_DO_ATIVO   # fonte: alocacao.py (o mesmo mapa da troca de recurso na O.S.)


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
                vinc=VINCULOS, oms=_oms(), achados=_achados(), leituras=_leituras(), abast=_abast(), recibos={},
                cmp=__import__('dados_compras_mat').seed())   # V69: requisições de materiais, peças e serviços (SC-038..040)


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
    import dados_compras_mat as CM   # V69: Compras de materiais, peças e serviços (c.man.cmp) com as mesmas regras em toda página do estado
    return 'const MAN0 = CEN0.man;\n' + JS_ACESSO_CEN + dados_js() + JS_VINC_BASE + JS + '\n' + CM.js() + '\n'


JS_ACESSO_CEN = r'''
/* ===== Estado da manutenção dentro do cenário único (1a, PCMS-M01): c.man de 'talhao-os-cenario-v1'; O.S., Estoque, App e CD-03 leem o mesmo ===== */
function manClone(o){ return JSON.parse(JSON.stringify(o)); }
function manGet(){ return cenGet().man; }
function manReset(self){ cenReset(); try{ cenSave(cenClone(CEN0)); }catch(e){} if(self) self.setState({manrev:Date.now(),cenrev:Date.now(),g2toast:'Demonstração restaurada: manutenção, ordens, estoque, colheita e app voltam ao início.'}); }
/* opt.estrito (MA-VINCULO, 16/10): o comando só vale se o navegador gravou; se a gravação falha, nada muda (memória e armazenamento) e volta o erro */
function manMudar(self,fn,opt){ const c=cenClone(cenGet()); let r;
  try{ r=fn(c.man,c)||{}; }catch(e){ r={erro:String(e.message||e)}; }
  if(r.erro){ if(self) self.setState({g2toast:r.erro}); return r; }
  if(r.nada){ if(self&&r.msg) self.setState(Object.assign({g2toast:r.msg},r.st||{})); return r; }
  c.man.rev=(c.man.rev||0)+1; c.rev=(c.rev||0)+1;
  if(opt&&opt.estrito){ try{ cenSave(c,true); }catch(e){ const er={erro:String(e.message||e),naoGravado:true}; if(self) self.setState({g2toast:er.erro}); return er; } }
  else cenSave(c); if(self) self.setState(Object.assign({manrev:c.man.rev,cenrev:c.rev,g2toast:r.msg||''},r.st||{})); return r; }
function manOuvir(self){ if(self.__manOuvindo) return; self.__manOuvindo=true;
  try{ window.addEventListener('storage',(e)=>{ if(e.key===CEN_KEY) self.setState({manrev:Date.now()}); }); }catch(e){} }
'''

JS_VINC_BASE = r'''
/* ===== Vínculo ativo × plano · recorte comum (MA-VINCULO, 16/10/2026): a mesma regra de "Sem plano" na Manutenção, na entrada do módulo e no CD-03 =====
   c.vinc['PM|ativo'] é o vínculo; desvincular guarda o registro com fim (nada se apaga). "Sem plano" = ativo em uso sem vínculo em plano ativo e
   publicado (o vínculo só em rascunho ou em plano inativo continua "Sem plano", com o motivo à vista). */
function manAtvAtivo(a){ return !!a&&a.sit!=='Inativo'&&a.sit!=='Baixado'; }
function manVincVale(v){ return !!v&&!v.fim; }
function manPlVale(p){ return !!p&&p.estado!=='Inativo'&&!!p.versao; }
function manPlanosDe(c,aid){ return Object.keys(c.vinc||{}).filter(k=>k.split('|')[1]===aid&&manVincVale(c.vinc[k])).map(k=>(c.planos||{})[k.split('|')[0]]).filter(Boolean); }
function manSemPlano(c){ return (c.ordem||[]).map(id=>(c.ativos||{})[id]).filter(a=>manAtvAtivo(a)&&!manPlanosDe(c,a.id).some(manPlVale)); }
'''


def hub_semplano_js():
    """Entrada do módulo (MOD-MAN) e CD-03: o recorte comum + o estado mínimo do seed; com o cenário gravado (mesma versão), vale o gravado."""
    import cenario
    s = seed(); v = cenario.seed()['v']
    mini = dict(ordem=s['ordem'], ativos={k: dict(id=a['id'], nome=a['nome']) for k, a in s['ativos'].items()},
                planos={k: dict(id=p['id'], estado=p['estado'], versao=p['versao']) for k, p in s['planos'].items()}, vinc={k: {} for k in s['vinc']})
    return (JS_VINC_BASE + 'const MAN_HUB0 = ' + json.dumps(dict(v=v, man=mini), ensure_ascii=False) + ';\n'
            + "const CEN_LS = 'talhao-os-cenario-v1';\n"
            + 'function manHubEstado(){ try{ const t=localStorage.getItem(CEN_LS); if(t){ const x=JSON.parse(t); if(x&&x.v===MAN_HUB0.v&&x.man) return x.man; } }catch(e){} return MAN_HUB0.man; }\n')


JS = r'''/* ===== Regras da manutenção (fonte única: tela MA, CD-03, O.S. e app) ===== */
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
/* hora de um lançamento novo no dia data: o relógio, nunca antes do último lançamento já gravado nesse dia (integração COMP, 10/10).
   O protótipo congela a data (c.hoje) e lê só a hora do relógio: entre 00:00 e 06:40 o lançamento novo ficava antes do AB-1042 da
   semente e o consumo pelo tanque cheio (manLh) pegava o cheio errado (8,3 L/h em vez de 15,8 L/h, REV-A4). Registrar é agora: depois do
   que já está gravado. No software a hora vem do servidor e não volta. */
function manHrNo(c,data){ const h=manHr(); const u=(c.abast||[]).filter(x=>x.data===data&&x.hora).reduce((m,x)=>x.hora>m?x.hora:m,''); return u>h?u:h; }
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
function manPapelDe(pf){ const p=(manPf(pf).papeis)||{}; return p.pcm?'pcm':((p.mecanico||p.eletricista)?'mecanico':(p.gestor?'gestor':'')); }   /* eletricista (João, NR-10) age como técnico de manutenção: executa e, se responsável técnico, decide a aptidão */
function manPor(pf){ const q=manPf(pf); const pa=manPapelDe(q); if(!q.k) return ''; if(typeof g2ator==='function'&&pa){ const t=g2ator(q,pa); if(t) return t; } return q.k; }
function manRtTxt(a){ return a?(a.rt||'Otávio'):'—'; }
function manPode(c,pf,cmd,x){ x=x||{}; const q=manPf(pf); const pa=manPapelDe(q); const k=q.k;
  const PCM='Ação do Otávio (responsável de manutenção)';
  if(cmd==='registrar') return (pa||MAN_OPS.indexOf(k)>=0)?'':'Ação de Otávio, Zé, Ana ou do operador da máquina';   /* operador do app (Marcos, S4) registra achado, leitura e abastecimento */
  if(['decidir','gerar','mover','liberar','encerrar','cancelar','leituraDecidir','estorno','plano','ponte'].indexOf(cmd)>=0) return pa==='pcm'?'':PCM;
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
/* a quem o plano se aplica (MA-VINCULO): {t:'modelo', v:[modelos], x:[ativos de outro modelo vinculados como exceção]} ou {t:'ativos', v:[ativos escolhidos]} */
function manCabe(c,p,a){ return p.aplica.t==='modelo'? (p.aplica.v.indexOf(a.modelo)>=0||(p.aplica.x||[]).indexOf(a.id)>=0) : p.aplica.v.indexOf(a.id)>=0; }
function manAplTxt(c,p){ const ap=p.aplica; const na=(n)=>n+(n===1?' ativo':' ativos');
  if(ap.t==='modelo'){ const n=c.ordem.map(id=>c.ativos[id]).filter(a=>a&&manAtvAtivo(a)&&ap.v.indexOf(a.modelo)>=0).length; const x=(ap.x||[]).filter(id=>c.ativos[id]).length;
    return 'Todos '+(ap.v.length>1?'dos modelos ':'do modelo ')+ap.v.join(' e ')+' ('+na(n)+')'+(x?' + '+na(x)+' de outro modelo':''); }
  return 'Ativos escolhidos ('+ap.v.filter(id=>c.ativos[id]).length+')'; }
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
function manOmCiclo(c,pid,aid,sid,ciclo){ return Object.values(c.oms).find(o=>o.etapa!=='Canceladas'&&o.pid===pid&&o.aid===aid&&(o.cobre||[]).indexOf(sid)>=0&&(o.ciclos||{})[sid]===ciclo)||null; }
/* falta peça: o que a OM ainda precisa além do já reservado para ela (D5: a peça que chegou da compra já vem reservada) e o livre não cobre */
function manNec(p){ return Math.max(0,(p.qtd||0)-(p.res||0)); }
function manLivreIt(c,k){ const it=c.itens[k]; return it?it.saldo-it.reservado:0; }
function manFalta(c,o){ return (o.pecas||[]).filter(p=>p.item&&o.etapa==='A liberar'&&manNec(p)>1e-9&&manLivreIt(c,p.item)<manNec(p)-1e-9); }
/* quem segura a reserva do item (outras OMs abertas): o motivo de "falta" quando há saldo físico, mas preso a outra ordem (D5) */
function manResDe(c,k,exceto){ const out=[]; Object.values(c.oms).forEach(o=>{ if(o.id===exceto||!manAberta(o)) return; const q=(o.pecas||[]).filter(p=>p.item===k).reduce((s,p)=>s+(p.res||0),0); if(q>1e-9) out.push({om:o.id,qtd:q}); }); return out; }
function manResTxt(c,k,exceto){ const it=c.itens[k]||{}; const rs=manResDe(c,k,exceto); return rs.length?rs.map(x=>manN(x.qtd,1)+' '+(it.un||'')+' reservada'+(x.qtd>1?'s':'')+' para a '+x.om).join(', '):''; }
/* todas as linhas plano × ativo × serviço (publicado), com cálculo, ordem do ciclo e selos */
function manLinhas(c,pid){ const out=[];
  Object.keys(c.vinc).forEach(vk=>{ const v=c.vinc[vk]; const k=vk.split('|'); if(pid&&k[0]!==pid) return; if(!manVincVale(v)) return; const p=c.planos[k[0]], a=c.ativos[k[1]]; if(!p||!a) return;
    const ss=manPub(p); if(!ss.length){ out.push({vk,pid:p.id,aid:a.id,sid:'',p,a,s:null,x:{sit:'Aguarda publicar',gats:[],prim:null,prev:null},ref:v.marco,om:null}); return; }
    ss.forEach(s=>{ const ref=manRef(v,s.id); const x=p.estado==='Inativo'?{sit:'Plano inativo',gats:[],prim:null,prev:null}:manVenc(c,s,a,ref);
      const ciclo=manCiclo(p.id,a.id,s.id,ref); const om=manOmCiclo(c,p.id,a.id,s.id,ciclo);
      const dup=om?null:(Object.values(c.oms).find(o=>o.tipo==='Preventiva'&&o.aid===a.id&&o.pid&&o.pid!==p.id&&manAberta(o)&&String(o.serv).toLowerCase()===String(s.nome).toLowerCase())||null);
      out.push({vk,pid:p.id,aid:a.id,sid:s.id,p,a,s,x,ref,ciclo,om,dup,est:!!(v.marco&&v.marco.est&&!(v.ult||{})[s.id])}); }); });
  return out; }
function manDevida(l){ return l.x.sit==='Vencida'||l.x.sit==='Vence em breve'; }
function manSemOm(c){ return manLinhas(c).filter(l=>manDevida(l)&&!l.om&&!l.dup); }
// a lista "Sem ordem" do PCM (fonte única da visão Sem ordem e do Painel de Manutenção): vencimentos de plano ativo sem ordem que já venceram
// ou cuja janela abre até o horizonte (c.horiz dias, ou hz), e achados (inspeção, relato, alerta) ainda sem ordem de um ativo cadastrado
function manSemOrdem(c,hz){ const h=hz===undefined?c.horiz:hz;
  const venc=manLinhas(c).filter(l=>l.s&&!l.om&&!l.dup&&l.p.estado!=='Inativo'&&(l.x.sit==='Vencida'||manIniJanela(l.x)<=h));
  const ach=Object.values(c.achados||{}).filter(q=>q.estado==='Sem ordem'&&c.ativos[q.aid]);
  return {venc,ach,n:venc.length+ach.length}; }
function manLinhaOm(c,o){ if(!o||!o.pid) return null; return manLinhas(c,o.pid).find(x=>x.aid===o.aid&&x.sid===o.sid&&x.om&&x.om.id===o.id)||null; }
function manDupServ(c,pid,aid,nomes){ const ns=nomes.map(x=>String(x).toLowerCase());
  for(const k of Object.keys(c.vinc)){ const q=k.split('|'); if(q[1]!==aid||q[0]===pid||!manVincVale(c.vinc[k])) continue; const o=c.planos[q[0]]; if(!o||o.estado==='Inativo') continue;
    const s=manWork(o).concat(manPub(o)).find(x=>ns.indexOf(String(x.nome).toLowerCase())>=0); if(s) return {pid:o.id,s:s.nome}; }
  return null; }
function manSelosLinha(c,l){ const s=[]; if(l.a.cond==='Bloqueado'){ s.push({t:'Ativo bloqueado',c:'red'}); }
  if(manAntiga(c,l.a)) s.push({t:'Leitura de '+manBr(l.a.leit.data),c:'yellow'}); if(l.a.suspeita) s.push({t:'Leitura a confirmar',c:'yellow'}); if(l.est) s.push({t:'Marco estimado',c:'yellow'}); return s; }
/* ---------- conflito com a produção (D-38): horas livres do recurso no dia (jornada − O.S. firme ou condicional) < tempo previsto ---------- */
// alocação vigente (alocacao.py: semana do PCP + trocas de recurso das O.S. no cenário); sem o cenário (motor isolado), a semana fixa
function manAloc(){ try{ if(typeof alVigente==='function'&&typeof cenGet==='function') return alVigente(cenGet()); }catch(e){} return MAN_AL.aloc; }
function manLivre(c,aid,iso){ const r=MAN_AL.rec[aid]; if(!r) return null; const jor=(MAN_AL.jorRec||{})[r]||MAN_AL.jor;
  const its=manAloc().filter(a=>a.r===r&&a.dia===iso&&a.sit!=='manutenção'); const h=its.reduce((s,a)=>s+a.h,0); const os=[];
  its.forEach(a=>{ if(os.indexOf(a.os)<0) os.push(a.os); }); return {r,jor,h,livre:Math.round((jor-h)*100)/100,os}; }
function manConflito(c,o,iso){ if(!o) return null; iso=iso||o.janIso; if(!iso) return null; const L=manLivre(c,o.aid,iso); if(!L||!L.os.length) return null;
  const t=Number(o.tempo)>0?Number(o.tempo):1; if(L.livre+1e-9>=t) return null;
  return {os:L.os,dia:iso,livre:Math.max(0,L.livre),t:'Conflito · '+L.os.join(' e ')+' '+manBr(iso),det:manN(Math.max(0,L.livre),1)+' h livres de '+manN(L.jor,1)+' h para '+manN(t,1)+' h previstas'}; }
function manProxLivre(c,o){ for(let i=1;i<=7;i++){ const d=manAdd(c.hoje,i); if(!manConflito(c,o,d)) return d; } return null; }
/* operador da alocação do ativo no dia (AL): pessoa da mesma O.S. no mesmo dia; sem alocação, nenhum (D-19) */
function manOperadorDia(c,aid,iso){ const r=MAN_AL.rec[aid]; if(!r) return ''; const oss=manAloc().filter(a=>a.r===r&&a.dia===iso&&a.sit!=='manutenção').map(a=>a.os);
  const ps=manAloc().filter(a=>a.dia===iso&&oss.indexOf(a.os)>=0&&MAN_AL.tipo[a.r]==='Pessoa').map(a=>MAN_AL.nome[a.r]);
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
  if(o.conflitoApp) s.push({t:'Conflito a resolver',c:'red',dono:'Otávio'});   /* registro do app que chegou depois de a OM mudar (S4) */
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
function manGerar(c,vk,sid,pf){ if(pf!==undefined) manExige(c,pf,'gerar'); const k=vk.split('|'); const p=c.planos[k[0]], a=c.ativos[k[1]], v=c.vinc[vk]; if(!p||!a||!manVincVale(v)) throw new Error('Vínculo não encontrado.');
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
  if(!o.vencOrig) o.vencOrig=o.janIso; const de=o.janIso; o.janAnt=o.jan; o.janIso=iso; o.jan=manBr(iso); o.ret=manBr(iso)+' 17:00'; o.conflitoAceito=!!(cf&&forcar&&o.etapa==='Liberadas');   /* S4: "Mover mesmo assim" é aceite do conflito do dia novo */
  o.movs=(o.movs||[]).concat([{de,para:iso,motivo:String(motivo||'').trim(),por:manPor(pf),em:c.hoje}]); manToca(o);
  return {msg:id+' movida para '+manBr(iso)+(fora?' · fora da tolerância ('+String(motivo).trim()+')':(tl?' · dentro da tolerância (até '+manBr(tl.dl)+')':''))+(cf?' · '+cf.t:' · sem conflito')+'.'}; }
/* liberar: executante e tempo; falta de peça trava (estoque); conflito com a produção é aviso confirmado até o 1b ("Liberar mesmo assim") */
function manLiberar(c,id,forcar,pf,d){ const o=c.oms[id]; if(!o) throw new Error('Ordem não encontrada.'); if(o.etapa!=='A liberar') throw new Error(id+' não está em A liberar.');
  if(pf!==undefined) manExige(c,pf,'liberar'); d=d||{};
  if(d.executante!==undefined&&d.executante!==null&&d.executante!=='') o.executante=d.executante;
  if(d.tempo!==undefined&&!manVazio(d.tempo)){ const t=manNum(d.tempo); if(isNaN(t)||t<=0||t>200) throw new Error('Tempo previsto inválido.'); o.tempo=t; }
  const ex=manExecSug(o); if(!ex) throw new Error('Falta: executante. Escolha quem executa.'); if(!(Number(o.tempo)>0)) throw new Error('Falta: tempo previsto (h).');
  const f=manFalta(c,o); if(f.length) throw new Error('Não liberada: falta peça · '+f.map(x=>{ const rt=manResTxt(c,x.item,o.id); return x.nome+' (livre '+manN(Math.max(0,manLivreIt(c,x.item)),1)+' de '+manN(manNec(x),1)+' '+x.un+(rt?' · '+rt+', que ninguém usa em outra ordem':'')+')'; }).join(', ')+(o.sc?'. Aguarda o recebimento da '+o.sc.id+'.':'. Solicite a compra.'));
  const cf=manConflito(c,o); if(cf&&!forcar) return {nada:true,aviso:true,msg:cf.t+' ('+cf.det+'). Mova a janela ou libere mesmo assim.'};
  (o.pecas||[]).forEach(p=>{ if(!p.item) return; const q=manNec(p); if(q>0) c.itens[p.item].reservado+=q; p.res=p.qtd; });   /* reserva o que ainda não está reservado (D5: a peça recebida da SC já chega reservada) */
  o.executante=ex; o.etapa='Liberadas'; if(cf) o.conflitoAceito=true; o.lib={por:manPor(pf),em:c.hoje,conf:cf?cf.t:''}; manToca(o);
  const pr=(o.pecas||[]).filter(p=>p.item).map(p=>p.nome+' '+manN(p.qtd)+' '+p.un);
  return {msg:id+' liberada para a oficina · executante '+ex+(pr.length?' · reservado: '+pr.join(', '):'')+(cf?' · conflito com a '+cf.os.join(' e ')+' aceito e avisado ao PCP':'')+'.'}; }
/* pontes até o 1b/1c (D-22): rotuladas "(simulado · …)" na tela */
function manSolicitar(c,id,pf){ const o=c.oms[id]; if(!o) throw new Error('Ordem não encontrada.'); if(pf!==undefined) manExige(c,pf,'ponte'); if(o.sc) return {nada:true,msg:'A '+o.sc.id+' já foi enviada a Compras (simulado).'};
  const f=manFalta(c,o); if(!f.length) return {nada:true,msg:'Nenhuma peça em falta nesta ordem.'};
  const sc='SC-'+String(c.seqsc||41).padStart(3,'0'); c.seqsc=(c.seqsc||41)+1;
  o.sc={id:sc,data:c.hoje,por:manPor(pf),itens:f.map(p=>({item:p.item,nome:p.nome,un:p.un,qtd:Math.max(0,manNec(p)-Math.max(0,manLivreIt(c,p.item)))}))}; manToca(o);
  cmmDaOm(c,o);   /* V69: a SC entra na fila de Compras › Materiais, peças e serviços (dados_compras_mat) */
  return {msg:sc+' enviada a Compras (Materiais, peças e serviços): '+o.sc.itens.map(x=>x.nome+' '+manN(x.qtd,1)+' '+x.un).join(', ')+' · a '+id+' libera quando a peça chegar.'}; }
/* recebimento da SC da OM, a função única da ponte da Manutenção e de Compras › Materiais (V69). porItem = {código: quantidade que chegou agora}
   (sem ele, tudo o que falta receber: a ponte simulada). D5 (proprietário, 16/10/2026): o que chega para uma OM aberta fica reservado para ela,
   até a necessidade da ordem (o.pecas[].res), com a origem em o.pecas[].rsv (pedido → recebimento → reserva → ordem). Não entra no livre e
   nenhuma outra ordem o usa (manFalta e manLiberar contam só o livre). Passou da necessidade, ou a OM foi cancelada ou encerrada: vai ao livre.
   A peça que já estava no livre continua reservada na liberação (DEC-2609-13). A requisição de Compras fica Recebida quando chega tudo. */
function manReceberSc(c,o,quem,porItem){ const sc=o.sc; const r=c.cmp&&c.cmp.reqs[sc.id];
  const pend={}; sc.itens.forEach(x=>{ const f=Math.max(0,x.qtd-(x.rec||0)); if(f>1e-9) pend[x.item]=(pend[x.item]||0)+f; });
  const rq={}; Object.keys(pend).forEach(k=>{ const q=porItem?Number(porItem[k]||0):pend[k];
    if(q>pend[k]+1e-9) throw new Error('Acima do pedido: chegou '+manN(q,1)+' de '+((c.itens[k]||{}).nome||k)+' e falta receber '+manN(pend[k],1)+'. Nada foi gravado.'); if(q>1e-9) rq[k]=q; });
  if(!Object.keys(rq).length) throw new Error('Informe a quantidade recebida. Nada foi gravado.');
  const hist=r?(r.recs=r.recs||[]):(sc.recs=sc.recs||[]); const pc=r&&r.ped?r.ped.id:''; const rid=(pc||sc.id)+'/'+(hist.length+1);
  const aberta=MAN_ABERTAS.indexOf(o.etapa)>=0; const ent=[], res=[], livre=[];
  const marca=(its,k,q)=>{ (its||[]).forEach(x=>{ if(x.item!==k||q<=1e-9) return; const d=Math.min(q,Math.max(0,x.qtd-(x.rec||0))); x.rec=(x.rec||0)+d; q-=d; }); };
  Object.keys(rq).forEach(k=>{ const it=c.itens[k]; let q=rq[k]; it.saldo+=q; marca(sc.itens,k,q); if(r) marca(r.itens,k,q); ent.push({item:k,nome:it.nome,un:it.un,qtd:q});
    if(aberta) (o.pecas||[]).forEach(p=>{ if(p.item!==k||q<=1e-9) return; const d=Math.min(q,manNec(p),Math.max(0,manLivreIt(c,k))); if(!(d>1e-9)) return;
      it.reservado+=d; p.res=(p.res||0)+d; p.rsv=(p.rsv||[]).concat([{pc,rec:rid,sc:sc.id,qtd:d,em:c.hoje,por:quem}]); res.push({item:k,nome:p.nome,un:p.un,qtd:d}); q-=d; });
    if(q>1e-9) livre.push({item:k,nome:it.nome,un:it.un,qtd:q}); });
  const completo=sc.itens.every(x=>(x.rec||0)>=x.qtd-1e-9); hist.push({id:rid,em:c.hoje,por:quem,om:o.id,ent,res,livre});
  if(completo){ sc.rec=c.hoje; sc.recPor=quem; if(r&&r.etapa!=='Recebida'){ r.etapa='Recebida'; r.rec={em:c.hoje,por:quem,dest:'om',res:res.map(x=>x.nome+' '+manN(x.qtd,1)+' '+x.un)}; } }
  manToca(o); return {rid,ent,res,livre,completo,falta:sc.itens.filter(x=>(x.rec||0)<x.qtd-1e-9).map(x=>x.nome+' '+manN(x.qtd-(x.rec||0),1)+' '+x.un)}; }
/* o texto do recebimento da OM (Compras e a ponte): o que chegou, o que ficou reservado para a OM, o que foi ao livre e o próximo passo */
function manRecTxt(c,o,e,pre){ const L=xs=>xs.map(x=>x.nome+' '+manN(x.qtd,1)+' '+x.un).join(', ');
  return (pre||('Recebimento '+e.rid+' da '+o.sc.id))+': '+L(e.ent)+(e.res.length?' · Reservado para '+o.id+': '+L(e.res)+' (fora do estoque livre)':'')
    +(e.livre.length?' · no estoque livre: '+L(e.livre)+(manAberta(o)?'':' ('+o.id+' '+({'Canceladas':'cancelada','Encerradas':'encerrada'}[o.etapa]||o.etapa.toLowerCase())+')'):'')
    +(e.falta.length?' · recebimento parcial: falta receber '+e.falta.join(', '):'')
    +(o.etapa==='A liberar'&&!manFalta(c,o).length?' · '+o.id+' pronta para liberar':'')+'.'; }
function manReceber(c,id,pf){ const o=c.oms[id]; if(!o||!o.sc) throw new Error('Esta ordem não tem compra solicitada.'); if(pf!==undefined) manExige(c,pf,'ponte'); if(o.sc.rec) return {nada:true,msg:'Recebimento da '+o.sc.id+' já registrado.'};
  const e=manReceberSc(c,o,manPor(pf)); return {msg:manRecTxt(c,o,e,'Recebimento da '+o.sc.id+' (simulado · papel do Almoxarifado)')}; }
/* cancelar sem execução (PCMS-M19, só a parte da reserva; D5): em A liberar ou Liberadas, pelo PCM, com motivo. A reserva da ordem (a da
   liberação e a da peça que chegou pela compra) volta ao estoque livre, com registro na ordem (o.canc.dev, com a origem do recebimento);
   o achado volta a Sem ordem e o ciclo do plano pode gerar outra ordem. Peça ainda não recebida chega livre. Repetir não devolve de novo. */
function manCancelar(c,id,motivo,pf,chave){ return manCmd(c,chave,'cancelar',()=>{ const o=c.oms[id]; if(!o) throw new Error('Ordem não encontrada.'); if(pf!==undefined) manExige(c,pf,'cancelar');
    if(o.etapa==='Canceladas') return {nada:true,msg:id+' já cancelada em '+manBr((o.canc||{}).em)+' · nada devolvido de novo.'};
    if(['A liberar','Liberadas'].indexOf(o.etapa)<0) throw new Error(id+' está '+o.etapa+': trabalho iniciado não se cancela; conclua e encerre.');
    if(manVazio(motivo)) throw new Error('Informe o motivo do cancelamento.');
    const por=manPor(pf), dev=[];
    (o.pecas||[]).forEach(p=>{ const q=p.res||0; if(!p.item||!(q>1e-9)) return; const it=c.itens[p.item]; it.reservado=Math.max(0,it.reservado-q); p.res=0;
      dev.push({item:p.item,nome:p.nome,un:p.un,qtd:q,orig:(p.rsv||[]).map(x=>x.rec).join(', ')}); });
    const de=o.etapa; o.etapa='Canceladas'; o.canc={por,em:c.hoje,motivo:String(motivo).trim(),de,dev}; const volta=manVolta(c,o); manToca(o);
    return {msg:id+' cancelada por '+por+' · motivo: '+String(motivo).trim()+(dev.length?' · reserva devolvida ao estoque livre: '+dev.map(x=>x.nome+' '+manN(x.qtd,1)+' '+x.un+(x.orig?' (recebimento '+x.orig+')':'')).join(', '):' · nada estava reservado')
      +(o.sc&&!o.sc.rec?' · a '+o.sc.id+' segue em Compras; o que chegar entra no estoque livre':'')+(volta.length?' · '+volta.join(', ')+' voltou a Sem ordem':'')+'.'}; }); }
function manIniciar(c,id,pf){ const o=c.oms[id]; if(!o||o.etapa!=='Liberadas') throw new Error(id+' não está em Liberadas.'); if(pf!==undefined) manExige(c,pf,'executar',{o});
  o.etapa='Em execução'; o.ini=c.hoje; o.iniPor=manPor(pf); manToca(o);
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
/* motivos da condição (revisão 09/10, A1): cada motivo tem achado e OM; o principal é a.condInfo e os demais ficam em a.condInfo.mais.
   O ativo só volta a Apto quando não sobra motivo: "Declarar apto" encerra só o motivo da ordem (dano evitado: máquina a campo com outro defeito bloqueante aberto). */
function manMots(a){ const i=a&&a.condInfo; return i?[i].concat(i.mais||[]):[]; }
function manMotOm(c,m){ const o=m&&m.om&&c.oms[m.om]; return o&&manAberta(o)?o:null; }
function manMotTxt(c,m){ const o=manMotOm(c,m); return (m.achado||m.motivo||'motivo')+' · '+(o?o.id:'sem ordem'); }
function manMotSet(a,ms){ ms=ms.slice(); if(!ms.length){ a.condInfo=null; return; } ms.forEach(m=>{ delete m.mais; }); if(ms.length>1) ms[0].mais=ms.slice(1); a.condInfo=ms[0]; }
function manMotCond(a){ const ms=manMots(a); if(!ms.length) return 'Apto'; return ms.some(m=>(m.cond||a.cond)==='Bloqueado')?'Bloqueado':'Restrito'; }
/* novo motivo: o bloqueio passa à frente de uma restrição; num ativo já bloqueado, acrescenta (o principal segue o primeiro) */
function manMotAdd(a,m){ const ms=manMots(a); if(!ms.length||a.cond==='Apto'){ manMotSet(a,[m]); return; } if(a.cond==='Restrito'&&m.cond==='Bloqueado') manMotSet(a,[m].concat(ms)); else manMotSet(a,ms.concat([m])); }
/* O.S. com o recurso do ativo alocado de hoje em diante (alocação do PCP, O.S. › Recursos): aviso, nunca promessa de impedimento (A9) */
function manOsAloc(c,aid){ const r=MAN_AL.rec[aid]; if(!r) return []; return [...new Set(manAloc().filter(x=>x.r===r&&x.sit!=='manutenção'&&x.dia>=c.hoje).map(x=>x.os))]; }
/* a OM que trata a condição (D-34): trata um motivo (o do achado; senão um sem achado e sem ordem); Teste do reparo entra sozinho se ainda não há Teste (no Restrito, Medição também vale) */
function manTratar(c,o,ach,mot){ const a=c.ativos[o.aid]; if(!a||a.cond==='Apto') return false; const ms=manMots(a);
  const m=mot||ms.find(x=>ach&&x.achado===ach&&!manMotOm(c,x))||ms.find(x=>!x.achado&&!manMotOm(c,x)); if(!m) return false;
  o.trata=true; m.om=o.id; const mc=m.cond||a.cond;
  const temT=o.chk.some(t=>t.tipo==='Teste'); const temM=o.chk.some(t=>t.tipo==='Medição');
  if(!temT&&!(mc==='Restrito'&&temM)){ const s=(ach&&c.achados[ach])?c.achados[ach].sint:(m.motivo||'condição do ativo'); o.chk.push({t:'Teste do reparo · '+s,tipo:'Teste',r:'',mot:'',fixo:true,tent:[]}); }
  return true; }
function manTesteValido(c,o){ const a=c.ativos[o.aid]; const tt=o.chk.filter(t=>t.tipo==='Teste'); if(tt.length&&tt.every(t=>(t.tent||[]).length&&t.tent[t.tent.length-1].r==='Aprovado')) return true;
  const mm=manMots(a).find(m=>m.om===o.id);
  const cond=mm?(mm.cond||a.cond):(a?(a.cond!=='Apto'?a.cond:((a.condHist||[]).slice(-2)[0]||{}).cond):''); if(!tt.length&&(cond==='Restrito'||(a&&a.cond==='Restrito'))&&o.chk.some(t=>t.tipo==='Medição'&&t.r==='Conforme')) return true; return false; }
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
/* outros motivos da condição que seguem abertos além dos que esta OM trata (A1): o rótulo do comando diz se o ativo fica apto ou segue na condição */
function manAptoFica(c,o){ const a=c.ativos[o.aid]; return manMots(a).filter(m=>m.om!==o.id); }
function manAptoRot(c,o){ const a=c.ativos[o.aid]; const fica=manAptoFica(c,o); if(!fica.length) return 'Declarar '+(a?a.nome:'ativo')+' apto';
  return 'Encerrar o motivo da '+o.id+' · '+(a?a.nome:'ativo')+' segue '+(fica.some(m=>(m.cond||a.cond)==='Bloqueado')?'bloqueado':'restrito'); }
function manDeclararApto(c,id,pf){ const o=c.oms[id]; const m=manAptoMotivo(c,o); if(m) throw new Error(m); const a=c.ativos[o.aid]; if(pf!==undefined) manExige(c,pf,'condicao',{aid:o.aid});
  const ant=a.cond, por=manPor(pf); const fica=manAptoFica(c,o);
  if(fica.length){ const falta=fica.map(x=>manMotTxt(c,x)); manMotSet(a,fica); a.cond=manMotCond(a);
    a.condHist=(a.condHist||[]).concat([{cond:a.cond,de:ant,motivo:'Motivo da '+id+' encerrado (teste válido) · segue '+a.cond.toLowerCase()+' por '+falta.join('; '),por,em:c.hoje,om:id}]);
    o.aptidao={dec:'motivo',por,em:c.hoje,falta}; manToca(o);
    return {msg:'Motivo da '+id+' encerrado (CMD-19 por '+por+') · '+manNome(a)+' segue '+a.cond.toLowerCase()+' · Falta: '+falta.join(' · ')+'.'}; }
  a.cond='Apto'; a.condInfo=null; a.condHist=(a.condHist||[]).concat([{cond:'Apto',de:ant,motivo:'Declarado apto pela '+id+' (teste válido)',por,em:c.hoje,om:id}]);
  o.aptidao={dec:'apto',por,em:c.hoje}; manToca(o);
  return {msg:manNome(a)+' apto · CMD-19 por '+por+' na '+id+' · a agenda antiga não é reassumida; volta pela reprogramação do PCP.'}; }
function manManter(c,id,motivo,pf){ const o=c.oms[id]; if(!o||!o.trata) throw new Error('Esta ordem não trata a condição do ativo.'); if(o.aptidao) throw new Error('Aptidão já decidida.');
  if(o.etapa!=='Em conferência') throw new Error('Decida a aptidão em Em conferência.'); if(pf!==undefined) manExige(c,pf,'condicao',{aid:o.aid}); if(manVazio(motivo)) throw new Error('Informe o motivo para manter.');
  const a=c.ativos[o.aid]; const por=manPor(pf); o.aptidao={dec:'manter',motivo:String(motivo).trim(),por,em:c.hoje};
  manMots(a).forEach(x=>{ if(x.om===id) x.om=''; }); a.condHist=(a.condHist||[]).concat([{cond:a.cond,motivo:'Mantido '+a.cond.toLowerCase()+' na '+id+': '+String(motivo).trim(),por,em:c.hoje,om:id}]); manToca(o);
  return {msg:manNome(a)+' segue '+a.cond.toLowerCase()+' ('+String(motivo).trim()+') · o vínculo com a '+id+' foi desfeito; crie uma ordem corretiva no ativo.'}; }
/* peças retiradas (D-13): destino Recondicionar · Garantia · Sucata, com responsável; nunca volta ao livre */
function manRetirada(c,id,i,dest,resp,pf){ const o=c.oms[id]; if(!o) throw new Error('Ordem não encontrada.'); const r=(o.retiradas||[])[i]; if(!r) throw new Error('Peça retirada não encontrada.');
  if(pf!==undefined){ const m1=manPode(c,pf,'executar',{o}), m2=manPode(c,pf,'ponte'); if(m1&&m2) throw new Error(m1+'. Nada foi alterado.'); }
  if(['Recondicionar','Garantia','Sucata'].indexOf(dest)<0) throw new Error('Escolha o destino: Recondicionar, Garantia ou Sucata.'); if(manVazio(resp)) throw new Error('Informe o responsável pelo destino.');
  r.dest=dest; r.resp=String(resp).trim(); r.por=manPor(pf); r.em=c.hoje; manToca(o);
  return {msg:r.nome+' → '+dest.toLowerCase()+' com '+r.resp+' · não volta ao estoque livre.'}; }
function manSobras(c,id,pf){ const o=c.oms[id]; if(!o) throw new Error('Ordem não encontrada.'); if(pf!==undefined) manExige(c,pf,'ponte'); const sb=(o.pecas||[]).filter(p=>p.sob>0); if(!sb.length) return {nada:true,msg:'Sem sobras nesta ordem.'};
  const rc='AL-'+(412+Object.values(c.oms).filter(x=>x.recibo).length); sb.forEach(p=>{ if(p.item) c.itens[p.item].saldo+=p.sob; p.dev=(p.dev||0)+p.sob; p.sob=0; }); o.recibo=rc; o.devPor={por:manPor(pf),em:c.hoje}; manToca(o);
  return {msg:'Sobras da '+id+' devolvidas (simulado · papel do Almoxarifado) com recibo '+rc+' · '+sb.map(p=>manN(p.dev)+' '+p.un+' '+p.nome).join(', ')+'.'}; }
/* encerrar: uma regra (F79 + F92; D-34): sobras, peças retiradas com destino, decisão de aptidão na OM que trata a condição */
function manFaltaEncerrar(c,o){ const f=[]; const a=c.ativos[o.aid];
  if((o.pecas||[]).some(p=>p.sob>0)) f.push('resolver sobras · Otávio (simulado · papel do Almoxarifado)');
  (o.retiradas||[]).forEach(r=>{ if(!r.dest||r.dest==='A definir'||!r.resp) f.push('destino e responsável de '+r.nome+' · '+(o.executante||'Otávio')); });
  if(o.trata&&!o.aptidao) f.push('Declarar '+(a?a.nome:'o ativo')+' apto ou Manter '+(a&&a.cond!=='Apto'?a.cond.toLowerCase():'a condição')+' · Otávio ou '+manRtTxt(a));
  const ca=manAppConfAbertos(c,o.id).length; if(ca) f.push('resolver '+ca+(ca>1?' registros do app':' registro do app')+' (aplicar ou descartar) · Otávio');   /* S4: o fato do campo não fica para trás do encerramento */
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
    if(ab&&!d.rep){ const sobe=manAchSobe(ab,d); return {nada:true,rep:ab.id,mais:sobe.length>0,msg:'Possível repetição de '+ab.id+' ('+ab.sint+') · Somar ou Registrar novo'+(sobe.length?' · a nova é mais grave: somar eleva '+sobe.join(' e '):'')+'.'}; }
    if(ab&&d.rep==='somar'){ const sobe=manAchSobe(ab,d);
      if(!ab.ocd) ab.ocd=[{em:ab.em,crit:ab.crit,sug:ab.sug,por:ab.por,sint:ab.sint}];
      ab.ocd.push({em:c.hoje,crit:d.crit,sug:d.sug,por,sint:String(d.sint).trim(),evid:String(d.evid||'').trim()});
      ab.oc=(ab.oc||[]).concat([c.hoje]); if(!manVazio(d.evid)) ab.evid=(ab.evid?ab.evid+' + ':'')+String(d.evid).trim(); ab.rv=(ab.rv||0)+1;
      if(MAN_CRITN[d.crit]>MAN_CRITN[ab.crit]) ab.crit=d.crit; if(MAN_SUGN[d.sug]>MAN_SUGN[ab.sug]) ab.sug=d.sug; if(sobe.length) ab.nova=true;
      if(!manVazio(d.leit)) manLeitura(c,d.aid,manNum(d.leit),'Achado '+ab.id,pf,c.hoje);
      let bm=''; if(d.bloquear&&ab.sug==='Bloqueado'){ const rb=manCondicao(c,d.aid,'bloquear',{motivo:ab.sint,evid:d.evid,achado:ab.id},pf); bm=' · '+(rb.nada?a.nome+' já estava bloqueado por '+ab.id:manBloqTxt(a,rb)); }
      return {id:ab.id,msg:'Somado ao '+ab.id+' · '+ab.oc.length+' ocorrências'+(sobe.length?' · '+sobe.join(' e '):'')+bm+'.'}; }
    const id=manAchProx(c,MAN_PREF[d.origem]);
    c.achados[id]={id,origem:d.origem,comp:d.comp,aid:d.aid,sint:String(d.sint).trim(),crit:d.crit,sug:d.sug,evid:String(d.evid||'').trim(),leit:manVazio(d.leit)?'':manNum(d.leit),por,em:c.hoje,oc:[c.hoje],estado:'Sem ordem',om:'',nova:true,voltou:'',mot:'',rv:0,os:d.os||''};
    let lm=''; if(!manVazio(d.leit)&&a.un){ const r=manLeitura(c,d.aid,manNum(d.leit),'Achado '+id,pf,c.hoje); lm=r.msg?' · '+r.msg:''; }
    let bm=''; if(d.bloquear&&d.sug==='Bloqueado'){ const rb=manCondicao(c,d.aid,'bloquear',{motivo:String(d.sint).trim(),evid:d.evid,achado:id},pf); bm=' · '+manBloqTxt(a,rb); }
    return {id,msg:'Achado '+id+' registrado · '+manNome(a)+' · '+d.comp+bm+lm+(d.os?' · ligado à '+d.os:'')}; }); }
/* repetição mais grave (revisão 09/10, A2): somar nunca perde a criticidade nem a sugestão de condição da ocorrência nova */
const MAN_CRITN={'Baixa':1,'Média':2,'Alta':3}, MAN_SUGN={'Apto':1,'Restrito':2,'Bloqueado':3};
function manAchSobe(ab,d){ const s=[]; if(MAN_CRITN[d.crit]>MAN_CRITN[ab.crit]) s.push('criticidade '+ab.crit+' → '+d.crit); if(MAN_SUGN[d.sug]>MAN_SUGN[ab.sug]) s.push('sugestão '+ab.sug+' → '+d.sug); return s; }
function manBloqTxt(a,rb){ return rb&&rb.ant==='Bloqueado'?(a.nome+' segue bloqueado · motivo acrescentado ('+rb.n+' motivos)'):(a.nome+' bloqueado'); }
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
    const ms=manMots(a); const mot=ms.find(m=>m.achado===id&&!manMotOm(c,m))||ms.find(m=>!m.achado&&!manMotOm(c,m));   /* A1: o motivo do achado (ou um sem achado), nunca o de outra OM aberta */
    const trata=(a.cond!=='Apto'&&mot)?manTratar(c,o,id,mot):false;
    if(!trata) manVerifAch(o,q);
    q.estado='Na OM'; q.om=oid; q.nova=false; q.voltou=''; q.dec={k:'corretiva',por:manPor(pf),em:c.hoje}; q.rv=(q.rv||0)+1;
    return {id:oid,msg:oid+' criada em A liberar · '+manNome(a)+' · '+q.comp+' · '+q.crit+' · janela '+manBr(pj)+(trata?' · trata a condição ('+a.cond+'): Teste do reparo incluído':'')+' · informe o tempo previsto para liberar.'}; }); }
function manAchFechar(c,id,mot,pf){ const q=c.achados[id]; if(!q) throw new Error('Achado não encontrado.'); if(pf!==undefined) manExige(c,pf,'decidir');
  if(q.estado!=='Sem ordem') throw new Error(id+' está '+q.estado.toLowerCase()+'.'); if(manVazio(mot)) throw new Error('Informe o motivo para fechar sem serviço.');
  q.estado='Fechado sem serviço'; q.mot=String(mot).trim(); q.nova=false; q.dec={k:'fechar',por:manPor(pf),em:c.hoje}; q.rv=(q.rv||0)+1;
  return {msg:id+' fechado sem serviço · '+q.mot+'.'}; }
function manAchCrit(c,id,crit,pf){ const q=c.achados[id]; if(!q) throw new Error('Achado não encontrado.'); if(pf!==undefined) manExige(c,pf,'decidir'); if(['Alta','Média','Baixa'].indexOf(crit)<0) throw new Error('Criticidade inválida.');
  if(q.crit===crit) return {nada:true}; q.critHist=(q.critHist||[]).concat([{de:q.crit,para:crit,por:manPor(pf),em:c.hoje}]); q.crit=crit; q.nova=false; q.rv=(q.rv||0)+1; return {msg:id+' · criticidade '+crit+'.'}; }
/* corretiva pela condição (detalhe do ativo Bloqueado sem OM que trate, ex.: depois de "Manter"): herda o motivo e ganha o Teste do reparo */
function manCorretivaAtivo(c,aid,pf,chave){ return manCmd(c,chave,'corretivaAtivo',()=>{ const a=c.ativos[aid]; if(!a) throw new Error('Ativo não encontrado.'); if(pf!==undefined) manExige(c,pf,'decidir');
    const ms=manMots(a); if(!ms.length) throw new Error(a.nome+' está apto: nenhuma condição a tratar.');
    const i=ms.find(m=>!manMotOm(c,m)); if(!i){ const t=manMotOm(c,ms[0]); return {nada:true,id:t?t.id:'',msg:'A condição do '+a.nome+' já é tratada: '+ms.map(m=>manMotTxt(c,m)).join(' · ')+'.'}; }
    if(i.achado&&c.achados[i.achado]&&c.achados[i.achado].estado==='Sem ordem') return manAchCorretiva(c,i.achado);
    const oid='OM-'+String(c.seq).padStart(4,'0'); c.seq++; const esp=a.classe==='Irrigação'?'Eletricista':'Mecânico';
    const o={id:oid,tipo:'Corretiva',aid,serv:'Corretiva · '+(i.motivo||a.cond),crit:'Alta',etapa:'A liberar',origem:'Condição '+a.cond+' · '+(i.motivo||''),jan:'',janIso:'',ret:'',esp,tempo:null,executante:'',chk:[],pecas:[],exec:null,selos:[],achados:[],rv:0};
    c.oms[oid]=o; const pj=manProxLivre(c,o)||manAdd(c.hoje,1); o.janIso=pj; o.jan=manBr(pj); o.ret=manBr(pj)+' 17:00'; manTratar(c,o,'',i);
    return {id:oid,msg:oid+' criada em A liberar · trata a condição do '+a.nome+' (Teste do reparo incluído) · informe o tempo previsto para liberar.'}; }); }
/* marco sugerido do vínculo (D-41): última OM encerrada do mesmo serviço, ou de um que o "cumpre também"; corretiva nunca serve */
function manMarcoSug(c,p,aid){ const nomes=manWork(p).concat(manPub(p)).map(s=>String(s.nome).toLowerCase()); let best=null;
  Object.values(c.oms).forEach(o=>{ if(o.aid!==aid||o.tipo!=='Preventiva'||o.etapa!=='Encerradas'||!o.exec) return; const pl=o.pid?c.planos[o.pid]:null;
    const cob=[String(o.serv).toLowerCase()].concat(pl?manPub(pl).filter(s=>(o.cobre||[]).indexOf(s.id)>=0).map(s=>String(s.nome).toLowerCase()):[]);
    if(!nomes.some(n=>cob.indexOf(n)>=0)) return; if(!best||o.exec.data>best.data) best={data:o.exec.data,leit:o.exec.leit,om:o.id}; });
  return best; }
/* ---------- vínculo ativo × plano (MA-VINCULO, 16/10/2026; revisão Codex 6226249749) ----------
   Um só modelo: p.aplica diz a quem o plano se aplica; c.vinc['PM|ativo'] = {marco, ult, desde, fim?, hist?} é o vínculo, com a base de contagem
   (marco = a última execução antes do vínculo; ult = a última por serviço, que vale primeiro: manRef).
   - Vincular, revincular ou repetir nunca zera nem sobrescreve marco, ult ou ciclo e nunca registra manutenção como feita: a leitura atual como
     base esconderia atraso (250 h, referência 1.000 h, leitura 1.450 h = Vencida; com 1.450 h de referência ficaria Em dia).
   - Sem execução registrada, quem vincula escolhe: informar a última execução ou contar de agora (marco estimado, à vista).
   - Grupo de máquina diferente é recusado (o plano geraria ordem, tarefas e peças erradas); modelo diferente no mesmo grupo é aviso.
   - Gatilho por h ou km que o ativo não conta é dito; serviço sem nenhum gatilho aplicável é recusado (nunca "Sem gatilho" calado).
   - Lote: tudo ou nada. Desvincular guarda o vínculo com fim e motivo; a OM aberta continua; vincular de novo retoma a mesma contagem. */
const MAN_NIV={escopo:0,modelo:1,classe:2,grupo:3};
function manModelosPl(c,p){ const ap=p.aplica; if(ap.t==='modelo') return ap.v.slice(); const m=[];
  ap.v.concat(Object.keys(c.vinc).filter(k=>k.split('|')[0]===p.id&&manVincVale(c.vinc[k])).map(k=>k.split('|')[1])).forEach(id=>{ const a=c.ativos[id]; if(a&&m.indexOf(a.modelo)<0) m.push(a.modelo); }); return m; }
function manClassesPl(c,p){ const s=[]; c.ordem.forEach(id=>{ const a=c.ativos[id]; if(a&&(manCabe(c,p,a)||manVincVale(c.vinc[p.id+'|'+id]))&&s.indexOf(a.classe)<0) s.push(a.classe); }); return s; }
function manContTxt(a){ return a.un==='h'?'conta horas (horímetro)':(a.un==='km'?'conta km (odômetro)':'não tem contador'); }
function manVincCompat(c,p,a){ const r={erro:'',avisos:[],nivel:''}; if(!p||!a){ r.erro='Plano ou ativo não encontrado.'; return r; }
  if(!manAtvAtivo(a)){ r.erro=a.nome+' está '+String(a.sit||'inativo').toLowerCase()+': não recebe plano.'; return r; }
  if(p.estado==='Inativo'){ r.erro=p.id+' está inativo: reative o plano para vincular.'; return r; }
  if(p.grupo&&a.grupo!==p.grupo){ r.erro=p.id+' é de '+p.grupo+' e '+a.nome+' é de '+a.grupo+': o plano geraria ordem, tarefas e peças erradas.'; return r; }
  const ss=manWork(p); const dup=manDupServ(c,p.id,a.id,ss.concat(manPub(p)).map(s=>s.nome));
  if(dup){ r.erro=manNome(a)+' já faz '+dup.s+' pelo '+dup.pid+': um serviço por ativo evita ordem em dobro.'; return r; }
  ss.forEach(s=>{ const g=s.gat||{}; const fora=['h','km'].filter(u=>g[u]&&a.un!==u); if(!fora.length) return;
    const vale=['h','km'].filter(u=>g[u]&&a.un===u).concat(g.d?['d']:[]); const ft=fora.map(u=>manN(g[u])+' '+u).join(' e ');
    if(!vale.length){ if(!r.erro) r.erro=s.nome+' conta só por '+ft+' e '+a.nome+' '+manContTxt(a)+': nenhum gatilho se aplica.'; return; }
    r.avisos.push(s.nome+': o gatilho de '+ft+' não vale ('+a.nome+' '+manContTxt(a)+'); vence só a cada '+vale.map(u=>manN(g[u])+' '+manUn(u)).join(' ou ')+'.'); });
  if(r.erro) return r;
  const ms=manModelosPl(c,p); r.nivel=manCabe(c,p,a)?'escopo':(ms.indexOf(a.modelo)>=0?'modelo':(manClassesPl(c,p).indexOf(a.classe)>=0?'classe':'grupo'));
  if(ms.length&&ms.indexOf(a.modelo)<0) r.avisos.unshift('Modelo diferente: '+a.modelo+'. Confira tarefas e peças do '+p.id+'.');
  return r; }
/* planos que servem ao ativo (opções explícitas, nunca vínculo automático): do âmbito, do mesmo modelo, da mesma classe e do mesmo grupo, nessa ordem */
function manVincSug(c,a){ if(!manAtvAtivo(a)) return [];
  return c.ordemPlanos.map(id=>c.planos[id]).filter(p=>p&&p.estado!=='Inativo'&&!manVincVale(c.vinc[p.id+'|'+a.id])).map(p=>({p,cp:manVincCompat(c,p,a)})).filter(x=>!x.cp.erro)
    .sort((x,y)=>(MAN_NIV[x.cp.nivel]-MAN_NIV[y.cp.nivel])||((y.p.versao?1:0)-(x.p.versao?1:0))||x.p.id.localeCompare(y.p.id)); }
/* base de contagem proposta: o vínculo encerrado volta como estava ('hist'); senão a última OM encerrada do mesmo serviço ('om'); senão a pessoa escolhe */
function manVincBase(c,p,a){ const v=c.vinc[p.id+'|'+a.id]; if(v&&v.fim) return {modo:'hist',v};
  const m=manMarcoSug(c,p,a.id); return m?{modo:'om',data:m.data,leit:m.leit,om:m.om}:{modo:''}; }
/* b = {modo:'agora'|'ult', corr, data, leit, mot}: devolve o marco ou os erros por campo (a mesma conferência da prévia e do comando) */
function manVincRef(c,p,a,b){ b=b||{}; const b0=manVincBase(c,p,a); const errs={}; let ref=null;
  if(b0.modo==='hist') return {ref:null,errs,modo:'hist'};
  const modo=b0.modo==='om'?(b.corr?'ult':'om'):(b.modo||'');
  if(modo==='om') ref={data:b0.data,leit:a.un&&b0.leit!==undefined?b0.leit:null,om:null,est:false,de:b0.om};
  else if(modo==='agora'){ if(a.un&&!a.leit) errs.leit=a.nome+' não tem leitura registrada: registre a leitura ou informe a última execução.'; else ref={data:c.hoje,leit:a.un?a.leit.val:null,om:null,est:true}; }
  else if(modo==='ult'){ let n=null;
    if(manVazio(b.data)) errs.data='Informe a data da última execução.'; else if(String(b.data)>c.hoje) errs.data='A data não pode ser futura.';
    if(a.un){ n=manNum(b.leit); if(manVazio(b.leit)||isNaN(n)) errs.leit='Informe a leitura na última execução ('+a.un+').'; else if(n<0) errs.leit='Zero ou mais.'; else if(a.leit&&n>a.leit.val) errs.leit='Maior que a leitura atual ('+manLeitTxt(a)+').'; }
    if(b0.modo==='om'&&manVazio(b.mot)) errs.mot='Informe o motivo da correção ('+b0.om+').';
    if(!Object.keys(errs).length) ref={data:String(b.data),leit:a.un?n:null,om:null,est:false,de:'',mot:b0.modo==='om'?String(b.mot).trim():''}; }
  else errs.modo='Escolha como contar: informe a última execução ou conte de agora.';
  return {ref,errs,modo}; }
function manVincDeTxt(a,ref){ return manBr(ref.data)+(ref.leit!==null&&ref.leit!==undefined&&a.un?' · '+manQ(ref.leit,a.un):''); }
/* prévia = os vencimentos que o vínculo vai gerar, pela mesma conta das linhas (manRef + manVenc + manProxTxt) */
function manVincPrev(c,p,a,v){ if(p.estado==='Inativo') return [{nome:'',txt:'Plano inativo: não gera vencimentos.',sit:'Plano inativo',prox:'—'}];
  const ss=manPub(p); if(!ss.length) return [{nome:'',txt:'Rascunho: os vencimentos começam quando o '+p.id+' for publicado.',sit:'Aguarda publicar',prox:'—'}];
  return ss.map(s=>{ const ref=manRef(v,s.id); const x=manVenc(c,s,a,ref); const prox=x.gats.length?manProxTxt(c,x):'—';
    return {sid:s.id,nome:s.nome,x,sit:x.sit,prox,txt:'próxima em '+prox+' · '+manSitTxt(c,x),de:manVincDeTxt(a,ref)}; }); }
function manAplicaInclui(p,a){ const ap=p.aplica; if(ap.t==='ativos'){ if(ap.v.indexOf(a.id)<0) ap.v.push(a.id); } else if(ap.v.indexOf(a.modelo)<0){ ap.x=ap.x||[]; if(ap.x.indexOf(a.id)<0) ap.x.push(a.id); } }
/* vincular 1 ou vários ativos a um plano: itens = [{aid, base:{modo, corr, data, leit, mot}}]; tudo ou nada; repetir não muda nada (chave e vínculo existente) */
function manVincular(c,pid,itens,pf,chave){ return manCmd(c,chave,'vincular',()=>{ if(pf!==undefined) manExige(c,pf,'plano'); const p=c.planos[pid]; if(!p) throw new Error('Plano não encontrado.');
  const visto={}; const its=(itens||[]).filter(x=>x&&x.aid&&!visto[x.aid]&&(visto[x.aid]=1)); if(!its.length) throw new Error('Marque ao menos um ativo.');
  const er=[]; const ok=its.map(it=>{ const a=c.ativos[it.aid]; const k=pid+'|'+it.aid; const v=c.vinc[k]; if(!a){ er.push('ativo '+it.aid+' não encontrado'); return null; }
    if(manVincVale(v)) return {a,k,ja:true};
    const cp=manVincCompat(c,p,a); if(cp.erro){ er.push(cp.erro.replace(/\.$/,'')); return null; }
    if(v&&v.fim) return {a,k,volta:true};
    const r=manVincRef(c,p,a,it.base); const e=Object.values(r.errs); if(e.length){ er.push(a.nome+': '+e[0].replace(/\.$/,'')); return null; }
    return {a,k,ref:r.ref}; });
  if(er.length) throw new Error('Nada foi vinculado: '+er.join(' · ')+'.');
  const por=manPor(pf); const novos=[], jas=[], voltas=[];
  ok.forEach(x=>{ if(x.ja){ jas.push(x.a); return; }
    if(x.volta){ const v=c.vinc[x.k]; v.hist=(v.hist||[]).concat([Object.assign({},v.fim,{desde:v.desde||null})]); delete v.fim; v.desde={em:c.hoje,por}; voltas.push(x.a); }
    else { c.vinc[x.k]={marco:x.ref,ult:{},desde:{em:c.hoje,por}}; novos.push(x.a); }
    manAplicaInclui(p,x.a); });
  const fe=novos.concat(voltas); if(!fe.length) return {nada:true,msg:(jas.length>1?'Já vinculados':'Já vinculado')+' ao '+pid+': '+jas.map(a=>a.nome).join(', ')+' · nada mudou.'};
  const prox=(a)=>{ const ls=manLinhas(c,pid).filter(l=>l.aid===a.id&&l.s); return ls.length?ls.map(l=>l.s.nome+' '+manProxTxt(c,l.x)).join(', '):'vence quando o plano for publicado'; };
  return {msg:(fe.length>1?fe.length+' ativos vinculados ao '+pid:manNome(fe[0])+' vinculado ao '+pid)+' · '+fe.map(a=>(fe.length>1?a.nome+': ':'')+prox(a)).join(' · ')
      +(voltas.length?' · retoma a contagem de antes ('+voltas.map(a=>a.nome).join(', ')+')':'')+(jas.length?' · já estava: '+jas.map(a=>a.nome).join(', '):'')+'.',ids:fe.map(a=>a.id)}; }); }
function manDesvincular(c,pid,aid,motivo,pf,chave){ return manCmd(c,chave,'desvincular',()=>{ if(pf!==undefined) manExige(c,pf,'plano'); const p=c.planos[pid], a=c.ativos[aid], v=c.vinc[pid+'|'+aid];
  if(!p||!a) throw new Error('Plano ou ativo não encontrado.'); if(!manVincVale(v)) return {nada:true,msg:a.nome+' não está vinculado ao '+pid+' · nada mudou.'};
  if(manVazio(motivo)) throw new Error('Informe o motivo para desvincular.');
  v.fim={em:c.hoje,por:manPor(pf),mot:String(motivo).trim()};
  const ap=p.aplica; const lst=ap.t==='ativos'?ap.v:(ap.x||[]); const i=lst.indexOf(aid); if(i>=0) lst.splice(i,1);
  const ab=Object.values(c.oms).filter(o=>o.pid===pid&&o.aid===aid&&manAberta(o));
  return {msg:manNome(a)+' desvinculado do '+pid+' · histórico guardado'+(ab.length?' · '+ab.map(o=>o.id).join(', ')+(ab.length>1?' continuam abertas':' continua aberta'):'')+'.'}; }); }
/* trocar "Aplica a" sem perder vínculo: devolve o âmbito novo, o grupo e o efeito (mostrado antes de salvar) */
function manAplicaNova(c,p,d){ const L=Object.keys(c.vinc).filter(k=>k.split('|')[0]===p.id&&manVincVale(c.vinc[k])).map(k=>c.ativos[k.split('|')[1]]).filter(Boolean);
  const ef=[]; let ap, as; const nm=(xs)=>xs.map(a=>a.nome).join(', ');
  if(d.tipo==='modelo'){ if(!d.modelo) return {erro:'Escolha o modelo.',efeito:[]}; as=c.ordem.map(x=>c.ativos[x]).filter(a=>a&&a.modelo===d.modelo&&manAtvAtivo(a));
    const x=L.filter(a=>a.modelo!==d.modelo); ap={t:'modelo',v:[d.modelo]}; if(x.length) ap.x=x.map(a=>a.id);
    ef.push('Vale para todos do modelo '+d.modelo+' ('+as.length+(as.length===1?' ativo).':' ativos).'));
    const nc=as.filter(a=>L.indexOf(a)<0); if(nc.length) ef.push(nm(nc)+(nc.length>1?' entram como candidatos':' entra como candidato')+': o vínculo pede a base de contagem.');
    if(x.length) ef.push(nm(x)+(x.length>1?' seguem vinculados':' segue vinculado')+' (outro modelo).'); }
  else { const esc=(d.ativos||[]).slice(); if(!esc.length&&!L.length) return {erro:'Marque ao menos um ativo.',efeito:[]};
    const v=esc.concat(L.map(a=>a.id).filter(id=>esc.indexOf(id)<0)); ap={t:'ativos',v}; as=v.map(id=>c.ativos[id]).filter(Boolean);
    ef.push('Vale para os ativos escolhidos ('+v.length+').');
    const ks=L.filter(a=>esc.indexOf(a.id)<0); if(ks.length) ef.push(nm(ks)+(ks.length>1?' seguem vinculados':' segue vinculado')+': vínculo feito não se perde (para tirar, desvincule).');
    const sai=c.ordem.map(x=>c.ativos[x]).filter(a=>a&&manCabe(c,p,a)&&v.indexOf(a.id)<0); if(sai.length) ef.push(nm(sai)+(sai.length>1?' deixam':' deixa')+' de ser candidato.'); }
  const gs=[...new Set(as.concat(L).map(a=>a.grupo))]; if(gs.length>1) return {erro:'O plano ficaria com '+gs.join(' e ')+': um plano serve a um grupo de máquina.',efeito:ef};
  return {aplica:ap,grupo:gs[0]||p.grupo,efeito:ef}; }
/* situação do plano no ativo (coluna Plano da visão Ativos e detalhe do plano): Atrasado · Vence em N h ou dias · Em dia · Rascunho · Plano inativo */
function manPlSit(c,p,a){ if(p.estado==='Inativo') return {t:'Plano inativo',c:'gray',r:5}; if(!p.versao) return {t:'Rascunho',c:'gray',r:4};
  const ls=manLinhas(c,p.id).filter(l=>l.aid===a.id&&l.s&&l.x.gats.length); if(!ls.length) return {t:'Sem gatilho',c:'gray',r:4};
  const v=ls.find(l=>l.x.sit==='Vencida'); if(v) return {t:'Atrasado',c:'red',r:0,dica:v.s.nome+' · '+manSitTxt(c,v.x)};
  const b=ls.filter(l=>l.x.sit==='Vence em breve').sort((x,y)=>x.x.gats[x.x.prim].dd-y.x.gats[y.x.prim].dd)[0];
  if(b){ const g=b.x.gats[b.x.prim]; let t; if(g.u==='d'){ const n=Math.max(0,Math.ceil(g.dd)); t=n?('Vence em '+n+(n>1?' dias':' dia')):'Vence hoje'; } else t=g.falta>0?('Vence em '+manQ(g.falta,g.u)):'Na tolerância';
    return {t,c:'yellow',r:1,dica:b.s.nome+' · '+manProxTxt(c,b.x)}; }
  return {t:'Em dia',c:'green',r:2}; }
/* ---------- condição única (CMD-18, PRD 47.3 l.7720; D-10, D-34): painel Condição ---------- */
function manCondicao(c,aid,acao,d,pf){ const a=c.ativos[aid]; if(!a) throw new Error('Ativo não encontrado.'); if(pf!==undefined) manExige(c,pf,'condicao',{aid}); d=d||{}; const por=manPor(pf);
  const hist=(x)=>{ a.condHist=(a.condHist||[]).concat([Object.assign({por,em:c.hoje},x)]); };
  if(acao==='rt'){ if(manVazio(d.rt)) throw new Error('Escolha o responsável técnico.'); if(manVazio(d.motivo)) throw new Error('Informe o motivo da troca.'); const de=a.rt; a.rt=String(d.rt).trim();
    hist({cond:a.cond,motivo:'Responsável técnico: '+de+' → '+a.rt+' ('+String(d.motivo).trim()+')'}); return {msg:'Responsável técnico do '+a.nome+': '+a.rt+'.'}; }
  if(acao==='bloquear'){ if(a.cond==='Bloqueado'&&(!d.achado||manMots(a).some(m=>m.achado===d.achado))) return {nada:true,msg:a.nome+' já está bloqueado'+(d.achado?' por '+d.achado:'')+'.'};
    if(manVazio(d.motivo)) throw new Error('Informe o motivo do bloqueio.');
    const ant=a.cond; const m={cond:'Bloqueado',motivo:String(d.motivo).trim(),desde:c.hoje,por,evid:String(d.evid||'').trim(),achado:d.achado||'',om:'',ate:'',lim:''};
    manMotAdd(a,m); a.cond='Bloqueado';   /* A1: num ativo já bloqueado (ou restrito) o motivo novo se soma; nenhum se perde */
    let t=''; if(d.om){ const o=c.oms[d.om]; if(!o||o.aid!==aid||MAN_ABERTAS.indexOf(o.etapa)<0) throw new Error('Escolha uma ordem aberta do mesmo ativo.'); manTratar(c,o,d.achado,m); manToca(o); t=' · tratado na '+o.id; }
    hist({cond:'Bloqueado',motivo:m.motivo+(ant!=='Apto'?' (motivo acrescentado)':''),achado:m.achado,om:m.om||''});
    const os=manOsAloc(c,aid); const n=manMots(a).length;   /* A9: as O.S. alocadas são aviso ao PCP; o impedimento derivado na O.S. é o Bloco 2 (PCMS-A05) */
    return {ant,n,msg:a.nome+(ant==='Bloqueado'?' segue bloqueado · motivo acrescentado ('+n+' motivos)':' bloqueado (CMD-18)')+' · '+m.motivo+t+(os.length?' · alocado em '+os.join(', ')+': avise o PCP (O.S. › Recursos)':'')+'.'}; }
  if(acao==='restringir'){ if(manVazio(d.motivo)) throw new Error('Informe o motivo da restrição.'); if(manVazio(d.lim)) throw new Error('Informe os limites de operação.');
    if(manVazio(d.ate)) throw new Error('Informe o prazo da restrição.'); if(d.ate<c.hoje) throw new Error('O prazo não pode ser anterior a hoje.');
    if(a.cond==='Bloqueado') throw new Error(a.nome+' está bloqueado: a saída é Declarar apto na ordem que trata a condição.');
    a.cond='Restrito'; a.condInfo={cond:'Restrito',motivo:String(d.motivo).trim(),desde:c.hoje,por,evid:String(d.evid||'').trim(),achado:d.achado||'',om:'',ate:d.ate,lim:String(d.lim).trim()};
    if(d.om){ const o=c.oms[d.om]; if(o&&o.aid===aid&&MAN_ABERTAS.indexOf(o.etapa)>=0){ manTratar(c,o,d.achado,a.condInfo); manToca(o); } }
    hist({cond:'Restrito',motivo:a.condInfo.motivo,ate:d.ate,om:a.condInfo.om||''}); return {msg:a.nome+' restrito até '+manBr(d.ate)+' · '+a.condInfo.lim+'.'}; }
  if(acao==='encerrar'){ if(a.cond!=='Restrito') throw new Error('Encerrar restrição só com o ativo Restrito.');
    const om=manMots(a).map(m=>manMotOm(c,m)).find(Boolean); if(om) throw new Error('A '+om.id+' trata a restrição: a saída é Declarar apto nela.');
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
/* consumo pelo método tanque cheio (PRD CAL-07): volume de todos os lançamentos não estornados com leitura em (cheio anterior, este cheio] ÷ a distância do contador
   (revisão 09/10, A4: o parcial no meio conta). Unidade pelo contador do ativo (A10): horímetro → L/h; odômetro → km/L. lh = o valor na unidade un. */
function manLh(c,b){ if(!b||b.tipo||b.qual==='Estornado'||!b.cheio||b.leit===null||b.leit===undefined) return null;
  const ok=(x)=>x.aid===b.aid&&!x.tipo&&x.qual!=='Estornado'&&x.leit!==null&&x.leit!==undefined;
  const ant=(c.abast||[]).filter(x=>ok(x)&&x.cheio&&x.leit<b.leit&&(x.data+(x.hora||''))<=(b.data+(b.hora||''))&&x.id!==b.id)
    .sort((x,y)=>y.leit-x.leit)[0]; if(!ant) return null; const dh=b.leit-ant.leit; if(dh<=0) return null;
  const its=(c.abast||[]).filter(x=>ok(x)&&x.leit>ant.leit&&x.leit<=b.leit&&(x.data+(x.hora||''))<=(b.data+(b.hora||''))); const vol=its.reduce((s2,x)=>s2+(Number(x.vol)||0),0);
  const km=b.un==='km'; return {lh:km?(vol>0?dh/vol:null):vol/dh,un:km?'km/L':'L/h',de:ant.id,h:dh,vol,n:its.length}; }
function manConsTxt(x){ return x&&x.lh!==null&&x.lh!==undefined?(manN(x.lh,1)+' '+x.un):'—'; }
function manAbastecer(c,d,pf,chave){ return manCmd(c,chave,'abast',()=>{ if(pf!==undefined) manExige(c,pf,'registrar'); d=d||{}; const a=c.ativos[d.aid]; const er=[];
    if(!a) er.push('ativo'); if(manVazio(d.tq)) er.push('tanque/lote'); const vol=manNum(d.vol); if(isNaN(vol)||vol<=0) er.push('volume em L');
    if(a&&a.un&&manVazio(d.leit)) er.push('leitura ('+a.un+')'); if(manVazio(d.op)) er.push('operador');
    if(er.length) throw new Error('Informe: '+er.join(', ')+'.'); if(vol>2000) throw new Error('Volume acima de 2.000 L num lançamento: confira.');
    const data=d.data||c.hoje; if(data>c.hoje) throw new Error('A data não pode ser futura.');
    const id=manAbProx(c,'AB'); const L=a.un?manNum(d.leit):null; if(a.un&&(isNaN(L)||L<0)) throw new Error('Leitura inválida.');
    const b={id,aid:a.id,tq:d.tq,vol,data,hora:d.hora||manHrNo(c,data),leit:L,un:a.un,op:d.op,evid:String(d.evid||'').trim(),cheio:!!d.cheio,qual:'Confirmada',por:manPor(pf),os:d.os||''};
    c.abast=(c.abast||[]).concat([b]); let m={msg:''}; if(a.un){ m=manLeitura(c,a.id,L,'Abastecimento '+id,pf,data,id); b.qual=m.qual||'Confirmada'; b.lt=m.lt; }
    const lh=manLh(c,b);
    return {id,msg:'Lançamento '+id+' registrado · '+manNome(a)+' · '+manN(vol)+' L'+(lh?' · '+manConsTxt(lh)+' (tanque cheio'+(lh.n>1?', '+lh.n+' lançamentos':'')+')':'')+(m.msg?' · '+m.msg:'')}; }); }
function manEstornar(c,id,motivo,pf,chave){ return manCmd(c,chave,'estorno',()=>{ if(pf!==undefined) manExige(c,pf,'estorno'); const b=(c.abast||[]).find(x=>x.id===id); if(!b||b.tipo) throw new Error('Lançamento não encontrado.');
    if(b.qual==='Estornado') return {nada:true,msg:id+' já foi estornado ('+b.estorno+').'}; if(manVazio(motivo)) throw new Error('Informe o motivo do estorno.');
    const es=manAbProx(c,'ES'); c.abast.push({id:es,tipo:'Estorno',ref:id,aid:b.aid,tq:b.tq,vol:-b.vol,data:c.hoje,hora:manHrNo(c,c.hoje),leit:null,un:b.un,op:b.op,evid:'',cheio:false,qual:'Estorno',motivo:String(motivo).trim(),por:manPor(pf)});
    b.qual='Estornado'; b.estorno=es; const lt=(c.leituras||[]).find(x=>x.id===b.lt); const a=c.ativos[b.aid]; let lm='';
    if(lt&&lt.qual==='A confirmar'){ if(a&&a.suspeita&&a.suspeita.lt===lt.id) delete a.suspeita; lt.qual='Descartada'; }
    else if(lt&&lt.qual==='Confirmada'){ lt.qual='Estornada';   /* A3: a leitura do lançamento estornado sai; se era a atual, volta a última confirmada antes dela e os vencimentos recalculam */
      if(a&&a.leit&&a.leit.val===lt.val&&a.leit.data===lt.data&&a.leit.origem===lt.origem){
        const ls=(c.leituras||[]).map((x,i)=>[x,i]).filter(([x])=>x.aid===a.id&&x.id!==lt.id&&['Confirmada','Troca de contador'].indexOf(x.qual)>=0)
          .sort((p1,p2)=>String(p1[0].data).localeCompare(String(p2[0].data))||(p1[1]-p2[1])); const pv=(ls.slice(-1)[0]||[])[0];
        if(pv){ a.leit={val:pv.val,data:pv.data,origem:pv.origem}; lm=' · leitura de '+manQ(lt.val,a.un)+' estornada: '+manNome(a)+' volta a '+manLeitTxt(a); } } }
    return {id:es,msg:'Estorno '+es+' lançado para '+id+' ('+String(motivo).trim()+')'+lm+' · o original fica no histórico; registre o lançamento correto.'}; }); }
/* ---------- indicadores (PRD 55.2: até 4 cartões; "não calculável" sem dado) ---------- */
function manPeriodo(c,k){ const h=c.hoje; if(k==='30d') return {de:manAdd(h,-30),ate:h,t:'30 d'}; if(k==='12m') return {de:manAdd(h,-365),ate:h,t:'12 m'};
  const M=['jan','fev','mar','abr','mai','jun','jul','ago','set','out','nov','dez']; return {de:h.slice(0,8)+'01',ate:h,t:M[Number(h.slice(5,7))-1]+'/'+h.slice(0,4)}; }
function manCustoPeriodo(c,k,aid){ const P=manPeriodo(c,k); let enc=0, and=0;
  Object.values(c.oms).forEach(o=>{ if(aid&&o.aid!==aid) return; if(o.etapa==='Encerradas'&&o.exec&&o.exec.data>=P.de&&o.exec.data<=P.ate) enc+=manCustoFinal(c,o);
    else if(manAberta(o)&&o.etapa!=='A liberar') and+=manCusto(c,o,'est'); }); return {enc,and,P}; }
function manCumprimento(c,k){ const P=manPeriodo(c,k); const os=Object.values(c.oms).filter(o=>o.tipo==='Preventiva'&&o.etapa==='Encerradas'&&o.vencOrig&&o.exec&&o.exec.data>=P.de&&o.exec.data<=P.ate);
  if(!os.length) return null; const ok=os.filter(o=>o.exec.data<=o.vencOrig).length; return {ok,n:os.length,pct:Math.round(ok*100/os.length)}; }
/* ---------- "Propor substituto" (ponte até o 1b, ESPECIFICACAO §0.1: sai com a PCMS-M09b): o ativo parado afeta O.S. na alocação;
   Otávio registra a proposta de um substituto apto da mesma classe e o PCP decide em O.S. › Recursos (simulado) ---------- */
function manPropAfeta(c,o){ const a=c.ativos[o.aid]; const r=MAN_AL.rec[o.aid]; if(!a||!r) return []; const de=(a.condInfo&&a.condInfo.desde)||c.hoje;
  return [...new Set(manAloc().filter(x=>x.r===r&&x.sit!=='manutenção'&&x.dia>=de).map(x=>x.os))]; }
function manPropSub(c,o){ const a=c.ativos[o.aid]; if(!a) return null; return Object.values(c.ativos).filter(x=>x.id!==a.id&&x.classe===a.classe&&x.cond==='Apto').sort((x,y)=>x.id.localeCompare(y.id))[0]||null; }
function manPropor(c,id,pf){ const o=c.oms[id]; if(!o) throw new Error('Ordem não encontrada.'); if(pf!==undefined) manExige(c,pf,'ponte');
  const a=c.ativos[o.aid]; if(!a||a.cond!=='Bloqueado'||!manAberta(o)) throw new Error('Só para ativo bloqueado com ordem aberta.');
  c.prop=c.prop||{}; if(c.prop[id]) return {nada:true,msg:'Proposta já registrada · aguarda PCP em O.S. › Recursos (simulado).'};
  const os=manPropAfeta(c,o), s=manPropSub(c,o); if(!os.length) throw new Error('Nenhuma O.S. alocada a '+a.nome+' a partir de '+manBr((a.condInfo||{}).desde||c.hoje)+'.'); if(!s) throw new Error('Nenhum '+a.classe.toLowerCase()+' apto para substituir.');
  c.prop[id]={sub:s.id,os,por:manPor(pf),em:c.hoje};
  return {msg:'Proposta registrada: '+manNome(s)+' para '+os.join(' e ')+' · aguarda PCP em O.S. › Recursos (simulado).'}; }
/* ---------- app de campo (PCM S4, §3.7): o MB-09, o MB-09det e o MB-04 usam as mesmas funções, com a chave gerada no aparelho.
   Com sinal: aplica já. Sem sinal: valida na cópia do aparelho (mesma regra; erro volta ao campo) e vai para a fila (c.app.manFila).
   Na volta do sinal a fila vai uma vez só: o cenário revalida fase e o.rv da OM; se mudou, vira "Conflito a resolver · Otávio" e nunca é aplicado em silêncio. ---------- */
const MAN_APP_CMD={
  iniciar:(c,a,pf)=>manIniciar(c,a.om,pf),
  resp:(c,a,pf)=>manResp(c,a.om,a.i,a.r,a.mot,pf,a.val),
  tentativa:(c,a,pf)=>manTentativa(c,a.om,a.i,a.r,a.evid,pf),
  incluir:(c,a,pf)=>manIncluir(c,a.om,a.tipo,a.txt,pf),
  retirada:(c,a,pf)=>manRetirada(c,a.om,a.i,a.dest,a.resp,pf),
  concluir:(c,a,pf)=>manConcluir(c,a.om,a.leit,a.horas,a.forcar,a.apl,pf),
  apto:(c,a,pf)=>manDeclararApto(c,a.om,pf),
  manter:(c,a,pf)=>manManter(c,a.om,a.motivo,pf),
  abastecer:(c,a,pf,k)=>manAbastecer(c,a.d,pf,k),
  leitura:(c,a,pf,k)=>manLeituraAvulsa(c,a.aid,a.val,a.data,pf,k),
  achado:(c,a,pf,k)=>manAchRegistrar(c,a.d,pf,k)};
const MAN_APP_NOME={iniciar:'Iniciar serviço',resp:'Resposta de tarefa',tentativa:'Teste',incluir:'Tarefa incluída',retirada:'Destino de peça retirada',concluir:'Concluir serviço',
  apto:'Declarar apto',manter:'Manter condição',abastecer:'Abastecimento',leitura:'Leitura',achado:'Achado'};
function manAppAplicar(c,q){ const f=MAN_APP_CMD[q.cmd]; if(!f) throw new Error('Comando desconhecido: '+q.cmd+'.'); return manCmd(c,q.chave,'app:'+q.cmd,()=>f(c,q.args||{},q.por,q.chave)); }
function manAppFila(cc){ return (cc&&cc.app&&cc.app.manFila)||[]; }
/* cópia do aparelho: o estado do servidor com a fila aplicada por cima (o que o operador vê sem sinal) */
function manAppProj(cc){ const F=manAppFila(cc); if(!F.length) return cc.man; const m=manClone(cc.man); F.forEach(q=>{ try{ manAppAplicar(m,q); }catch(e){} }); return m; }
function manAppAid(m,q){ const a=q.args||{}; return a.aid||(a.d&&a.d.aid)||(a.om&&m.oms[a.om]?m.oms[a.om].aid:''); }
function manAppDesc(m,q){ const a=q.args||{}; const at=m.ativos[manAppAid(m,q)]; const t=a.om&&m.oms[a.om]&&a.i!==undefined?(m.oms[a.om].chk[a.i]||{}).t:'';
  return (MAN_APP_NOME[q.cmd]||q.cmd)+(a.om?' · '+a.om:'')+(at?' · '+at.nome:'')+(t?' · '+t:'')+(a.r?' · '+a.r:'')+(q.cmd==='abastecer'&&a.d?' · '+manN(manNum(a.d.vol))+' L':'')+(q.cmd==='leitura'?' · '+a.val+' '+(at?at.un:''):''); }
function manAppCmd(cc,q){ if(!q||!q.chave) throw new Error('Comando sem chave do aparelho.'); const a=q.args||{};
  if(cc.app.online!==false) return manAppAplicar(cc.man,q);
  cc.app.manFila=cc.app.manFila||[]; if(cc.app.manFila.some(x=>x.chave===q.chave)) return {nada:true,repetido:true,msg:'Já está no aparelho · aguardando sinal.'};
  const m=manClone(manAppProj(cc)); const o=a.om?m.oms[a.om]:null;   /* cópia: validar no aparelho nunca grava no servidor */ const rv=o?(o.rv||0):null, fase=o?o.etapa:null; const desc=manAppDesc(m,q);
  /* A7: a versão de referência é a do servidor quando a OM entrou na fila (o 1º registro dela); a projeção do aparelho pode coincidir com uma mudança do escritório */
  const ant=a.om?cc.app.manFila.find(x=>x.om===a.om):null; const srv=a.om?cc.man.oms[a.om]:null; const rvBase=ant?(ant.rvBase!==undefined?ant.rvBase:ant.rv):(srv?(srv.rv||0):null);
  const r=manAppAplicar(m,q); if(r.nada) return r;
  cc.app.manFila.push({chave:q.chave,cmd:q.cmd,args:a,por:q.por,om:a.om||'',rv,rvBase,fase,at:cenAgora(),desc}); cc.app.fila=(cc.app.fila||[]).concat(['MAN|'+q.chave]);
  return {fila:true,id:r.id||'',msg:desc+' · no aparelho, aguardando sinal (vai uma vez só ao voltar).'}; }
function manAppConflito(m,q,mot){ m.appConf=m.appConf||[]; const id='CA-'+String(m.appConf.length+1).padStart(3,'0');
  m.appConf.push({id,chave:q.chave,cmd:q.cmd,args:q.args,por:q.por,om:q.om||'',aid:manAppAid(m,q),at:q.at,desc:q.desc,mot,estado:'A resolver'});
  const o=q.om&&m.oms[q.om]; if(o) o.conflitoApp=(o.conflitoApp||0)+1; return id; }
/* volta do sinal: cada registro entra uma vez (recibo pela chave); OM mudada desde o registro vira conflito */
function manAppSinal(cc){ const F=manAppFila(cc).slice(); const m=cc.man; let n=0; const conf=[]; const esp={}, ruim={};
  F.forEach(q=>{ m.recibos=m.recibos||{}; if(m.recibos[q.chave]){ return; }
    const o=q.om?m.oms[q.om]:null; let mot='';
    /* A7: versão esperada = a do servidor no 1º registro da OM, depois a que os registros desta fila deixaram; o seguinte de uma OM em conflito também vira conflito */
    const e=o?((q.om in esp)?esp[q.om]:(q.rvBase!==undefined&&q.rvBase!==null?q.rvBase:q.rv)):null;
    if(q.om&&!o) mot=q.om+' não existe mais';
    else if(o&&ruim[q.om]) mot=q.om+' tem registro anterior desta fila em conflito';
    else if(o&&((o.rv||0)!==e||o.etapa!==q.fase)) mot=q.om+' mudou no escritório depois do registro'+(o.etapa!==q.fase?' (era '+q.fase+', agora '+o.etapa+')':' (outra alteração na mesma fase)');
    if(!mot){ try{ const r=manAppAplicar(m,q); if(r.nada&&!r.repetido) mot=r.msg||'não aplicado'; else { n++; if(o) esp[q.om]=(m.oms[q.om].rv||0); return; } }catch(x){ mot=String(x.message||x); } }
    if(q.om) ruim[q.om]=1; conf.push(manAppConflito(m,q,mot)); });
  cc.app.manFila=[]; cc.app.fila=(cc.app.fila||[]).filter(k=>String(k).indexOf('MAN|')!==0);
  return {n,conf}; }
function manAppConfAbertos(c,om,aid){ return (c.appConf||[]).filter(x=>x.estado==='A resolver'&&(om===undefined||x.om===om)&&(aid===undefined||(!x.om&&x.aid===aid))); }
function manAppConfBaixa(c,x){ const o=x.om&&c.oms[x.om]; if(o){ o.conflitoApp=Math.max(0,(o.conflitoApp||0)-1); manToca(o); } }
/* Otávio decide: aplicar o registro sobre o estado de agora (mesma função, autor original, mesma chave) ou descartar com motivo */
function manAppConfAplicar(c,id,pf){ manExige(c,pf,'decidir'); const x=(c.appConf||[]).find(y=>y.id===id); if(!x||x.estado!=='A resolver') throw new Error('Conflito não encontrado.');
  let q={chave:x.chave,cmd:x.cmd,args:x.args,por:x.por}; let r=manAppAplicar(c,q);
  if(r.nada&&r.rep&&x.cmd==='achado'){ q=Object.assign({},q,{args:Object.assign({},x.args,{d:Object.assign({},x.args.d,{rep:'somar'})})}); r=manAppAplicar(c,q); }
  if(r.nada&&!r.repetido) throw new Error((r.msg||'Não aplicado')+' · descarte com motivo ou peça novo registro.');
  x.estado='Aplicado'; x.dec={por:manPor(pf),em:c.hoje}; manAppConfBaixa(c,x); return {msg:'Registro do app aplicado: '+x.desc+(r.msg?' · '+String(r.msg).replace(/\.+$/,''):'')+'.'}; }
function manAppConfDescartar(c,id,motivo,pf){ manExige(c,pf,'decidir'); const x=(c.appConf||[]).find(y=>y.id===id); if(!x||x.estado!=='A resolver') throw new Error('Conflito não encontrado.');
  if(manVazio(motivo)) throw new Error('Informe o motivo para descartar.'); x.estado='Descartado'; x.dec={por:manPor(pf),em:c.hoje,motivo:String(motivo).trim()}; manAppConfBaixa(c,x);
  return {msg:'Registro do app descartado: '+x.desc+' ('+String(motivo).trim()+') · fica no histórico da ordem.'}; }
/* acesso para os testes de navegador (mesmo padrão do window.__cen da O.S.) */
try { window.__man = { manPropor, manAppCmd, manAppSinal, manAppProj, manAppConfAplicar, manAppConfDescartar, manMudar, manRetirada, manIncluir, manGet, manClone, manLinhas, manSemOrdem, manVenc, manGerar, manGerarTodas, manLiberar, manConcluir, manReset, manLeitura, manLeituraOk, manLeituraDescartar, manSolicitar, manReceber, manCancelar, manFalta, manPlaus, manNum,
  manConflito, manProxLivre, manMover, manPode, manAchOpcoes, manCusto, manCustoFinal, manTesteValido, manFaltaEncerrar, manFaltaConcluir, manMarcoSug,
  manTentativa, manDeclararApto, manAchRegistrar, manAchCorretiva, manAbastecer, manCondicao, manMots, manAptoRot,
  manVincular, manDesvincular, manVincCompat, manVincSug, manVincBase, manVincRef, manVincPrev, manAplicaNova, manPlSit, manSemPlano, manPlanosDe }; } catch (e) {}
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
