# -*- coding: utf-8 -*-
"""Alocação de recursos às O.S. na semana 22–27/09/2026 (fonte única para a tela da ordem e a visão Recursos do PCP).
Coerente com dados.ORDENS: OS-0421 dias 3–7 (manhãs), OS-0420 com Trator T1 quebrado em 22/09 (OM-0233) e substituto Trator 02
a partir de 24/09 condicionado à v3, OS-0431 dependente do T1, OS-0424 em 24/09 06:00–11:00, OS-0430 em 25/09 à tarde, irrigação com João.
"""
DIAS = [('2026-09-22', 'seg 22/09'), ('2026-09-23', 'ter 23/09'), ('2026-09-24', 'qua 24/09'), ('2026-09-25', 'qui 25/09'), ('2026-09-26', 'sex 26/09'), ('2026-09-27', 'sáb 27/09')]
JORNADA = 10.0  # h por dia disponível para máquina, implemento e pessoa (1 turno)
JOR_RECURSO = {'PV1': 24.0, 'PV2': 24.0}  # pivô gira fora do turno: a volta a 62 % leva ≈14,5 h

RECURSOS = [  # id, tipo, nome
    ('T1', 'Máquina', 'Trator T1 JD 6M 155'), ('T02', 'Máquina', 'Trator 02 MF 7719'), ('T03', 'Máquina', 'Trator 03'), ('T04', 'Máquina', 'Trator 04'),
    ('COL', 'Máquina', 'Colhedora Axial-Flow 7250'), ('PV1', 'Máquina', 'Pivô 1'), ('PV2', 'Máquina', 'Pivô 2'),
    ('PJ', 'Implemento', 'Pulverizador PJ-3030 36 m'), ('PL', 'Implemento', 'Plantadeira 24 linhas'), ('DI', 'Implemento', 'Distribuidor 3 t'), ('ES', 'Implemento', 'Esqueletadeira'),
    ('MAR', 'Pessoa', 'Marcos · operador'), ('CAR', 'Pessoa', 'Carlos · operador'), ('PAU', 'Pessoa', 'Paula · caldeiro'), ('JOA', 'Pessoa', 'João · irrigante'),
]
# (recurso, O.S. ou evento, dia, início, fim, situação) — situação: firme | condicional (depende de aprovação/liberação) | manutenção
ALOC = []
def _a(recs, os_, dia, ini, fim, sit='firme'):
    for r in recs: ALOC.append(dict(r=r, os=os_, dia=dia, ini=ini, fim=fim, sit=sit))
for dia, fim in [('2026-09-22', 11.0), ('2026-09-23', 11.0), ('2026-09-24', 11.0), ('2026-09-25', 11.0), ('2026-09-26', 12.0)]:
    _a(['T03', 'PJ', 'MAR', 'PAU'], 'OS-0421', dia, 6.0, fim)
_a(['T1', 'PL', 'CAR'], 'OS-0420', '2026-09-22', 6.0, 9.5)                      # 12 ha até a quebra do T1
_a(['T1'], 'OM-0233', '2026-09-22', 9.5, 18.0, 'manutenção')
for dia in ['2026-09-23', '2026-09-24']: _a(['T1'], 'OM-0233', dia, 6.0, 18.0, 'manutenção')
for dia in ['2026-09-24', '2026-09-25', '2026-09-26', '2026-09-27']:
    _a(['T02', 'PL', 'CAR'], 'OS-0420', dia, 6.0, 16.0, 'condicional')              # saldo de 70 ha após a v3
_a(['T1', 'PL', 'CAR'], 'OS-0431', '2026-09-24', 6.0, 16.0, 'condicional')           # plantio T2 pede o T1 bloqueado
_a(['T04', 'PJ', 'MAR', 'PAU'], 'OS-0424', '2026-09-24', 6.0, 11.0)
_a(['T03', 'PJ', 'MAR', 'PAU'], 'OS-0430', '2026-09-25', 13.0, 20.4, 'condicional')  # 160 ha ÷ 21,6 ha/h ≈ 7,4 h
_a(['PV2'], 'OS-0419', '2026-09-23', 20.0, 24.0); _a(['PV2'], 'OS-0419', '2026-09-24', 0.0, 10.52)   # 1 volta a 62 % ≈ 14,5 h
_a(['JOA'], 'OS-0419', '2026-09-23', 20.0, 22.0); _a(['JOA'], 'OS-0419', '2026-09-24', 6.0, 10.52)  # partida à noite; ronda e término de manhã
_a(['JOA'], 'OS-0423', '2026-09-23', 14.0, 16.0)
_a(['PV1'], 'OS-0418', '2026-09-24', 21.0, 24.0, 'condicional'); _a(['PV1'], 'OS-0418', '2026-09-25', 0.0, 11.25, 'condicional')  # 8,1 mm × 95 ha ÷ 150 L/s ≈ 14,3 h
_a(['JOA'], 'OS-0418', '2026-09-24', 21.0, 23.0, 'condicional'); _a(['JOA'], 'OS-0418', '2026-09-25', 6.0, 11.25, 'condicional')

NOME = {r: n for r, t, n in RECURSOS}; TIPO = {r: t for r, t, n in RECURSOS}


def hh(x):
    h = int(x); m = int(round((x - h) * 60))
    return f'{h:02d}:{m:02d}'


def conflitos():
    """Sobreposição de horário do mesmo recurso em ordens diferentes (manutenção conta como indisponível)."""
    out = []
    for i, a in enumerate(ALOC):
        for b in ALOC[i + 1:]:
            if a['r'] == b['r'] and a['dia'] == b['dia'] and a['os'] != b['os'] and a['ini'] < b['fim'] and b['ini'] < a['fim']:
                out.append(dict(r=a['r'], dia=a['dia'], a=a['os'], b=b['os'], ini=max(a['ini'], b['ini']), fim=min(a['fim'], b['fim']),
                                manut=('manutenção' in (a['sit'], b['sit']))))
    return out


def semana():
    """Por recurso: horas por dia, uso da semana, conflitos, excesso de jornada e ociosidade."""
    conf = conflitos(); res = []
    for r, t, n in RECURSOS:
        dias = []; tot = 0.0
        for d, lab in DIAS:
            its = [a for a in ALOC if a['r'] == r and a['dia'] == d]
            h = sum(a['fim'] - a['ini'] for a in its if a['sit'] != 'manutenção'); tot += h
            dias.append(dict(d=d, itens=its, h=h, manut=any(a['sit'] == 'manutenção' for a in its),
                             conf=[c for c in conf if c['r'] == r and c['dia'] == d], acima=h > JOR_RECURSO.get(r, JORNADA) + 1e-9))
        disp = JOR_RECURSO.get(r, JORNADA) * len(DIAS) - sum(a['fim'] - a['ini'] for a in ALOC if a['r'] == r and a['sit'] == 'manutenção')
        res.append(dict(r=r, tipo=t, nome=n, dias=dias, h=tot, disp=disp, uso=(tot / disp if disp else 0)))
    return res, conf


def da_ordem(os_):
    """Recursos alocados a uma O.S., com janelas e alertas (conflito, manutenção, condicional)."""
    conf = conflitos(); its = [a for a in ALOC if a['os'] == os_]
    out = []
    for r in dict.fromkeys(a['r'] for a in its):
        ja = [a for a in its if a['r'] == r]
        cs = [c for c in conf if c['r'] == r and os_ in (c['a'], c['b'])]
        out.append(dict(r=r, tipo=TIPO[r], nome=NOME[r],
                        janelas=' · '.join(f"{a['dia'][8:10]}/{a['dia'][5:7]} {hh(a['ini'])}–{hh(a['fim'])}" for a in ja),
                        cond=any(a['sit'] == 'condicional' for a in ja),
                        alertas=[(f"{'Em manutenção' if c['manut'] else 'Conflito com ' + (c['b'] if c['a'] == os_ else c['a'])} em {c['dia'][8:10]}/{c['dia'][5:7]} {hh(c['ini'])}–{hh(c['fim'])}") for c in cs]))
    return out


if __name__ == '__main__':
    res, conf = semana()
    for x in res: print(f"{x['nome']:32s} {x['h']:5.1f} h / {x['disp']:4.1f} h = {x['uso']*100:5.1f} %", '·', sum(len(d['conf']) for d in x['dias']), 'conflitos')
    for c in conf: print(c)
    print(da_ordem('OS-0424'))
