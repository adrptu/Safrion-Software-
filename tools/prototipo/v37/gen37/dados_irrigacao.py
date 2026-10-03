# -*- coding: utf-8 -*-
"""Irrigação · fonte única dos dados (02/10/2026): semente IRR0 do estado compartilhado entre IR-01..IR-04, IR-03det e a camada
Irrigação do Mapa (IN-04). O estado vive no navegador (localStorage 'talhao-os-irrigacao-v1'), com a API de irrigacao_estado.js.
Uso: EXTRAJS[0] = cenario.js_prefixo() + dados_irrigacao.js_prefixo() + <js da tela>; a tela chama irrOuvir(self) e lê irrGet().

Tempo: minutos desde 23/09/2026 00:00 (HOJE do protótipo). Agora = 06:12 (balanço do dia calculado).
Balanço (PRD cap. 63 e CAL-09): déficit = déficit inicial + ETc − chuva efetiva − irrigação LÍQUIDA; líquida = bruta medida × eficiência
(a eficiência entra uma vez). Bruta = líquida ÷ eficiência; passadas = ⌈bruta ÷ limite⌉; volume = bruta × área × 10; duração = volume ÷ (vazão × 3,6).
Santa Rita: P2 11,2 mm (medido) · P1 ≈8,4 mm (sonda suspeita) · T7 ≈10,0 mm (sonda sem dado desde 20/09) — os mesmos números das outras telas;
a ETc dos 7 dias fecha a memória com a irrigação líquida dos eventos medidos.
Lagoa Grande: balanço DEMONSTRATIVO sobre os pivôs reais do KML (ETo 5,5 mm/dia × Kc do mamão pela fase). Vazão demonstrativa de 1,25 L/s
por ha, eficiência 85 %, até 8 mm por passada, intervalo de 18 h; todos os pivôs na captação do Rio A (demonstração) (outorga SINT-001/0000, 573 L/s
× 21 h/dia, vencida em 22/11/2023 e em renovação — aviso). Ribeirão B (demonstração) (19 L/s, vencida em 13/02/2024) aparece em IR-04 sem setor ligado.
As tarefas do dia da Lagoa Grande (tarefa única por setor) são geradas pelo irrGerar() de irrigacao_estado.js na primeira leitura (OS-0601…)."""
import json, os, math, datetime as dt
import dados_lagoa_safra as DLS

HERE = os.path.dirname(os.path.abspath(__file__))
HOJE = dt.date(2026, 9, 23)
AGORA = 6 * 60 + 12


def m(dia, hhmm):
    """minuto desde 23/09 00:00 · dia = deslocamento em dias (0 = hoje)."""
    h, mi = map(int, hhmm.split(':'))
    return dia * 1440 + h * 60 + mi


def dur(lam, ha, ls):
    """duração em minutos de uma lâmina bruta (mm) na área (ha) com a vazão (L/s)."""
    return round(lam * ha * 10 / (ls * 3.6) * 60)


FAZ = {'SR': dict(nome='Santa Rita', irrig='João', pcp='Caio · PCP', gestor='Ana · gestora', pcm='Rui · PCM',
                  fonte='Estação Santa Rita · sondas P1, P2 e T7 · hoje 06:00'),
       'LG': dict(nome='Lagoa Grande', irrig='Joaquim', pcp='PCP da Lagoa Grande', gestor='Gestor da Lagoa Grande', pcm='Manutenção',
                  fonte='balanço demonstrativo · ETo 5,5 mm/dia × Kc do mamão pela fase', demo=True)}

CAPT = {
    'SR-RIO': dict(faz='SR', nome='Rio · captação da sede', outorga='demonstrativa', ls=400, h=21, venc='2028-06-30', st='Vigente'),
    'SR-RES': dict(faz='SR', nome='Reservatório da sede', outorga='demonstrativa', ls=250, h=21, venc='2028-06-30', st='Vigente'),
    'LG-PAR': dict(faz='LG', nome='Rio A (demonstração)', outorga='SINT-002/0000', ls=573, h=21, venc='2023-11-22', st='Em renovação',
                   obs='renovação no processo técnico 56898/2023 · irrigação de 619,29 ha por pivô central'),
    'LG-STC': dict(faz='LG', nome='Ribeirão B (demonstração)', outorga='SINT-003/0000', ls=19, h=21, venc='2024-02-13', st='Vencida',
                   obs='irrigação de 136 ha por pivô central · nenhum setor ligado'),
    'LG-BAR': dict(faz='LG', nome='Barramento · afluente do Ribeirão B (demonstração)', outorga='SINT-004/0000', ls=65, h=24, venc='2027-11-25', st='Vigente',
                   obs='65 L/s de março a novembro · 0 L/s em dezembro a fevereiro · nenhum setor ligado'),
}

FONTES = {
    'EST-SR': dict(faz='SR', nome='Estação meteorológica Santa Rita', gr='ET₀ / chuva / vento', un='mm/dia · mm', at=m(0, '06:00'), cal='2027-02-28', cob='Raio 8 km', st='Ativa'),
    'HID-P2': dict(faz='SR', nome='Hidrômetro · Pivô 2', gr='Volume', un='m³', at=m(0, '06:00'), cal='2026-09-30', cob='Pivô 2', st='Ativa'),
    'SO-P2': dict(faz='SR', nome='Sonda de umidade · P2 (20 cm)', gr='Umidade do solo', un='% vol.', at=m(0, '05:40'), cal='2027-01-31', cob='Pivô 2', st='Ativa', setor='P2'),
    'SO-P1': dict(faz='SR', nome='Sonda de umidade · P1 (20 cm)', gr='Umidade do solo', un='% vol.', at=m(0, '05:40'), cal='2027-01-31', cob='Pivô 1', st='Suspeita',
                  motivo='salto de 18 p.p.', desde=m(0, '05:40'), setor='P1'),
    'SO-T7': dict(faz='SR', nome='Sonda de umidade · T7', gr='Umidade do solo', un='% vol.', at=m(-3, '06:00'), cal='2027-01-31', cob='Gotejo T7', st='Sem dado',
                  desde=m(-3, '06:00'), setor='T7'),
    'PREV-SR': dict(faz='SR', nome='Previsão meteorológica (modelo externo)', gr='Chuva prevista 48 h', un='mm', at=m(0, '06:00'), cal='', cob='Regional', st='Previsão', ro=True),
    'ETO-LG': dict(faz='LG', nome='ETo de referência · Lagoa Grande (demonstrativa)', gr='ET₀', un='mm/dia', at=m(0, '06:00'), cal='', cob='Fazenda', st='Ativa', ro=True),
    'SO-PV10': dict(faz='LG', nome='Sonda de umidade · Pivô 10', gr='Umidade do solo', un='% vol.', at=m(-2, '06:00'), cal='2027-03-31', cob='Pivô 10', st='Sem dado',
                    desde=m(-2, '06:00'), setor='PV10'),
}


def _ap(q, os_, vol, ha, ef, cob, txt, prov=False):
    return dict(q=q, os=os_, n=1, vol=vol, ha=ha, ef=ef, cob=cob, txt=txt, prov=prov)


def _gov(aps, ha):
    """mesma conta de irrCreditos() (irrigacao_estado.js): volta completa credita o pivô; passagem parcial fica na faixa coberta
    (lâmina = volume ÷ área coberta) e só entra no pivô quando as parciais da MESMA ordem completam a área (vale a menor líquida)."""
    gov = 0.0; grp = {}
    for a in aps:
        cob = a['cob'] if a.get('cob') is not None else a['ha']
        if cob <= 0 or a['vol'] <= 0: continue
        net = a['vol'] / (10 * cob) * a['ef'] / 100
        if cob >= ha - 1e-9: gov += net; continue
        g = grp.setdefault(a['os'], [0.0, 1e9]); g[0] += cob; g[1] = min(g[1], net)
    return gov + sum(g[1] for g in grp.values() if g[0] >= ha - 1e-6)


def _sr():
    """Santa Rita: P2, P1 e T7 com o balanço de 7 dias (16/09..22/09) que fecha nos déficits das outras telas."""
    S = {}
    base = [
        ('P2', 'Pivô 2', 'Milho V10', 80, 'pivô', 166, 'B2', 'Bomba B2', 'SR-RIO', 12.0, 18, 90, 8.0, 'SO-P2', 5.0, 12.0, 11.2,
         [_ap(m(-6, '20:00'), 'OS-0388', 8640, 80, 90, 80, 'volta completa'), _ap(m(-4, '20:00'), 'OS-0391', 6400, 80, 90, 80, 'volta completa'),
          _ap(m(-1, '22:06'), 'OS-0394', 1206, 80, 90, 11.6, 'passagem parcial', prov=True)]),
        ('P1', 'Pivô 1', 'Feijão R5', 95, 'pivô', 150, 'B1', 'Bomba B1', 'SR-RIO', 12.0, 18, 90, 8.0, 'SO-P1', 5.0, 12.0, 8.4,
         [_ap(m(-6, '21:00'), 'OS-0387', 9595, 95, 90, 95, 'volta completa'), _ap(m(-2, '21:00'), 'OS-0393', 7695, 95, 90, 95, 'volta completa')]),
        ('T7', 'Gotejo T7', 'Mamão', 42, 'gotejo', 233, 'B3', 'Bomba B3', 'SR-RES', 6.0, 12, 95, 5.0, 'SO-T7', 3.1, 10.5, 10.0,
         [_ap(m(-7, '16:00'), 'OS-0389', 1680, 42, 95, 42, 'turno completo'), _ap(m(-5, '16:00'), 'OS-0390', 1680, 42, 95, 42, 'turno completo'),
          _ap(m(-4, '16:00'), 'OS-0392', 1680, 42, 95, 42, 'turno completo')]),
    ]
    for (sid, nome, cult, ha, tipo, ls, bomba, bnome, capt, lmax, imin, efic, lim, sonda, d0, pef, alvo, aps) in base:
        net = _gov(aps, ha)
        etc = round(alvo - d0 + pef + net, 2)   # ETc dos 7 dias que fecha a memória no déficit de hoje (passagem parcial não entra)
        S[sid] = dict(faz='SR', nome=nome, cult=cult, ha=ha, tipo=tipo, vazao=ls, bomba=bomba, bnome=bnome, capt=capt, lmax=lmax, imin=imin, efic=efic,
                      limiar=lim, sonda=sonda, bal=dict(d0=d0, etc=etc, pef=pef, chuva='20/09 · 20 mm × 60 %', ini=m(-8, '00:00'), dias=7, ap=aps))
    return S


FASE = [('formação inicial', 0.60, 6.0, 90), ('pré-florada', 0.85, 8.0, 240), ('produção', 1.05, 9.0, 99999)]
ETO = 5.5
# déficit demonstrativo de hoje por pivô (mesmos números da camada Irrigação até 01/10); pivô fora da lista = preparo, sem rega
DEF_LG = {'PV01': 6.1, 'PV02': 9.8, 'PV03': 7.4, 'PV04': 4.8, 'PV05': 13.2, 'PV06': 3.2, 'PV07': 5.6, 'PV08': 6.4, 'PV09': 10.6, 'PV10': 7.9, 'PV14': 2.9, 'PV15': 4.1,
          'PV17': 8.2, 'PV18': 11.4, 'PV19': 2.4, 'PV20': 7.7, 'PV21': 8.8, 'PV22': 5.3, 'PV23': 6.9, 'PV24': 9.4}


def _lg():
    cad = json.load(open(os.path.join(__import__('dados_lagoa_fonte').DIR, 'lagoa_cadastro.json'), encoding='utf-8'))
    plantio = {DLS.PID_DE[c['local']]: c['plantio'] for c in DLS.CULTIVOS}
    S = {}
    for p in cad['pivos']:
        pid = p['id']; ha = p['area_ha']; n = p['nome'].split()[-1]
        pl = plantio.get(pid); dias = (HOJE - dt.date(*map(int, pl.split('-')))).days if pl else -1
        x = dict(faz='LG', nome=f'Pivô {n}', cult='Mamão', ha=ha, tipo='pivô', vazao=round(1.25 * ha), bomba='B-' + pid, bnome=f'Bomba do Pivô {n}',
                 capt='LG-PAR', lmax=8.0, imin=18, efic=85, sonda=('SO-PV10' if pid == 'PV10' else None), bal=None, limiar=None, fase='preparo de área')
        if pid in DEF_LG and dias >= 0:
            fase, kc, lim, _ = next(f for f in FASE if dias < f[3])
            d = DEF_LG[pid]; etcd = ETO * kc; ndias = max(1, round(d / etcd))
            x.update(cult=f'Mamão · {fase}', fase=fase, limiar=lim, kc=kc,
                     bal=dict(d0=0.0, etc=d, pef=0.0, chuva='sem chuva no período', ini=m(-ndias, '00:00'), dias=ndias, ap=[], repos=m(-ndias, '06:00')))
        elif dias < 0:
            x.update(cult='Mamão · plantio previsto', fase='preparo de área')
        S[pid] = x
    return S


# ordens de irrigação só com água da Santa Rita (as mesmas de dados.ORDENS); as da Lagoa Grande nascem do irrGerar()
def _ordens():
    T = lambda q, rec, ev, quem: dict(q=q, rec=rec, ev=ev, quem=quem)
    O = {}
    O['OS-0419'] = dict(id='OS-0419', faz='SR', setor='P2', tipo='água', versao='v1', etapa='Liberadas', lam=10.81, au='AU-3098', lib='LIB-2287', ex='EX-5120', tele=8480,
                        orig=dict(d=11.2, q=m(0, '06:12'), t='balanço de 23/09 · 1 volta a 62 % (percentímetro)'),
                        passadas=[dict(n=1, ini=m(0, '20:00'), dur=871, lam=10.81, st='Programada', cob=None, vol=None)],
                        exec=dict(pausas=[]), conf=None, fert=None,
                        trilha=[T(m(0, '06:12'), 'AU-3098', 'Necessidade calculada pelo balanço · déficit 11,2 mm → 10,81 mm brutos em 1 passada', 'sistema'),
                                T(m(0, '06:12'), 'LIB-2287', 'Liberada pela prontidão · janela, bomba B2, energia e outorga conferidas', 'sistema')])
    O['OS-0422'] = dict(id='OS-0422', faz='SR', setor='P2', tipo='água', versao='v1', etapa='A liberar', lam=13.5, au='AU-3099', libRes='LIB-2291', ex=None,
                        orig=dict(d=11.2, q=m(0, '06:12'), t='próximo ciclo · déficit 11,2 mm + ETc prevista'),
                        passadas=[dict(n=i, ini=None, dur=dur(6.75, 80, 166), lam=6.75, st='Programada', cob=None, vol=None) for i in (1, 2)],
                        exec=dict(pausas=[]), conf=None, fert=None,
                        trilha=[T(m(0, '06:12'), 'AU-3099', 'Necessidade do próximo ciclo · 13,5 mm brutos em 2 passadas de 6,75 mm (limite 12,0 mm)', 'sistema')])
    O['OS-0423'] = dict(id='OS-0423', faz='SR', setor='T7', tipo='água', versao='v1', etapa='A liberar', lam=4.0, au='AU-3100', libRes='LIB-2292', ex=None,
                        orig=dict(d=10.0, q=m(0, '06:12'), t='balanço de 23/09 · estimativa por ET (sonda sem dado)'),
                        passadas=[dict(n=1, ini=m(0, '14:00'), dur=dur(4.0, 42, 233), lam=4.0, st='Programada', cob=None, vol=None)],
                        exec=dict(pausas=[]), conf=None, fert=None,
                        trilha=[T(m(0, '06:12'), 'AU-3100', 'Necessidade estimada por ET · turno de 4,0 mm no gotejo', 'sistema')])
    O['OS-0394'] = dict(id='OS-0394', faz='SR', setor='P2', tipo='água', versao='v1', etapa='Em conferência', lam=10.81, au='AU-3094', lib='LIB-2283', ex='EX-5116',
                        orig=dict(d=10.9, q=m(-1, '06:12'), t='balanço de 22/09'),
                        passadas=[dict(n=1, ini=m(-1, '20:00'), dur=871, lam=10.81, st='Parcial', cob=11.6, vol=1206, fimReal=m(-1, '22:06'))],
                        exec=dict(pausas=[], ini=m(-1, '20:00'), fim=m(-1, '22:06')),
                        conf=dict(med=1206, est=round(10.81 * 11.6 * 10), st='Divergência'), fert=None,
                        trilha=[T(m(-1, '20:00'), 'EX-5116', 'Início · telemetria da B2', 'João'),
                                T(m(-1, '22:06'), 'EX-5116', 'Parou às 22:06 (2,1 h) · 11,6 de 80 ha cobertos · hidrômetro 1.206 m³', 'telemetria'),
                                T(m(-1, '22:07'), 'EX-5116', 'Conferência: 10,4 mm medidos × 10,81 mm estimados na área coberta (−3,8 %) · acima da tolerância de 3 %', 'sistema')])
    O['OS-0392'] = dict(id='OS-0392', faz='SR', setor='T7', tipo='água', versao='v1', etapa='Encerradas', lam=4.0, au='AU-3090', lib='LIB-2279', ex='EX-5108',
                        orig=dict(d=8.2, q=m(-4, '06:12'), t='balanço de 19/09'),
                        passadas=[dict(n=1, ini=m(-4, '14:00'), dur=dur(4.0, 42, 233), lam=4.0, st='Feita', cob=42, vol=1680, fimReal=m(-4, '16:00'))],
                        exec=dict(pausas=[], ini=m(-4, '14:00'), fim=m(-4, '16:00')),
                        conf=dict(med=1680, est=1680, st='Automática', q=m(-4, '16:04')), fert=None,
                        trilha=[T(m(-4, '16:04'), 'EX-5108', 'Conferência automática · 1.680 m³ medidos × 1.680 m³ estimados · encerrada', 'sistema')])
    return O


# fertirrigações (O.S. agrícola): a etapa vem do cenário da O.S.; aqui só a janela na bomba (para conflito) e o texto do mapa
# lam = lâmina bruta por ha que a O.S. aplica com o produto; base = área já apontada na semente (fora do balanço demonstrativo):
# o que a O.S. apontar além da base entra no balanço do setor (irrApsOS)
FERT = {'OS-0418': dict(setor='P1', ini=m(1, '21:00'), fim=m(2, '11:15'), lam=8.1, base=0, nome='fertirrigação · Ureia'),
        'OS-0506': dict(setor='PV04', ini=m(1, '06:00'), fim=m(1, '17:00'), lam=6.0, base=34, nome='fertirrigação NK · turno 2 em 24/09'),
        'OS-0507': dict(setor='PV05', ini=None, fim=None, lam=6.0, base=20, nome='fertirrigação de arranque · bomba parada')}
# paradas do PCM na bomba (bloqueiam a janela)
PARADAS = [dict(bomba='B3', ini=m(0, '14:00'), fim=m(0, '15:00'), txt='parada da B3', ref='manutenção preventiva', dono='Caio · PCP'),
           dict(bomba='B-PV05', ini=m(-2, '08:00'), fim=m(2, '12:00'), txt='bomba do Pivô 5 em manutenção', ref='OM-0251', dono='Manutenção')]


def seed():
    st = dict(v=1, rev=0, hoje='2026-09-23', agora=AGORA, ponta=[18 * 60, 21 * 60], tol=3, faz=FAZ, capt=CAPT, fontes=FONTES,
              setores=dict(_sr(), **_lg()), ordens=_ordens(), fert=FERT, paradas=PARADAS, ger=False,
              seq=dict(os=600, lib=2300, ex=5121, au=3101))
    return st


def deficit(st, sid):
    """mesma conta de irrDef() (irrigacao_estado.js) — para os testes e textos estáticos."""
    x = st['setores'][sid]; b = x['bal']
    if not b: return None
    return max(0.0, b['d0'] + b['etc'] - b['pef'] - _gov(b['ap'], x['ha']))


def js_prefixo():
    return ('const IRR0 = ' + json.dumps(seed(), ensure_ascii=False).replace('</', '<\\/') + ';\n'
            + open(os.path.join(HERE, 'irrigacao_estado.js'), encoding='utf-8').read() + '\n')


if __name__ == '__main__':
    s = seed()
    for k in ('P2', 'P1', 'T7', 'PV02', 'PV08', 'PV09', 'PV10', 'PV18', 'PV21', 'PV24'):
        x = s['setores'][k]; print(k, x['cult'], x['limiar'], round(deficit(s, k), 2), x['bal']['etc'] if x['bal'] else None)
