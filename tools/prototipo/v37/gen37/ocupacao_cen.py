# -*- coding: utf-8 -*-
"""Cadastros que o serviço de ocupação (ocupacao.js / ocupacao.py) lê, montados uma vez para a tela (processo_safra.py → D2) e para
ocupacao_unit.py: classe das culturas e unidade de mercado (CD-02, DEC-0510-03), ciclo das cultivares (CD-02), talhões Ativos do CD-01 por
fazenda (com o B1 da Boa Vista e os pivôs da Lagoa Grande, dado sintético), safras e cultivos no formato do serviço. Só lê."""
import dados as D, dados2 as D2, dados_cad as DC, dados_lagoa_safra as DL

FOLGA = 1   # folga de liberação em dias (R-06): parâmetro do dono, padrão "dia seguinte" (DECISOES §3)
CULTURAS = {c[0]: c[2] for c in DC.CULTURAS}
# unidade de mercado da meta por cultura (DEC-0510-03): a mesma escrita curta que a meta do cultivo já usa ("62 sc/ha", "45 t/ha/ano")
UN_META = {c[0]: ('sc/ha' if c[3].startswith('sc') else c[3]) for c in DC.CULTURAS}


def cultivares():
    from areas.cadastros import CULTIVARES
    return [(c, v, d) for _i, c, v, _tp, d, _rg in CULTIVARES]


def talhoes():
    """{fazenda: [(nome, área)]} na ordem do CD-01, só talhões Ativos. Pivô da Lagoa: id do mapa (PVnn) → nome do talhão (Pivô n)."""
    from areas.cad_fazendas import _tal_rows
    nome_de = {v: k for k, v in DL.PID_DE.items()}
    out = {}
    for r in _tal_rows():
        v = r['v']
        if v.get('sit') != 'Ativo': continue
        out.setdefault(v['faz'], []).append((nome_de.get(r['id'], r['id']), float(v['decl'])))
    return out


def fazendas():
    """Fazendas ativas do CD-01 (opções do formulário de safra)."""
    return [f['nome'] for f in DC.FAZENDAS if f.get('sit', 'Ativa') == 'Ativa'] + (['Lagoa Grande'] if not any(f['nome'] == 'Lagoa Grande' for f in DC.FAZENDAS) else [])


def safras(extra=()):
    s = {x['id']: dict(id=x['id'], nome=x['nome'], ini=x['ini'], fim=x['fim'], faz=x['fazenda'], ro=bool(x.get('ro'))) for x in D2.SAFRAS}
    for x in extra: s[x['id']] = dict(x)
    return s


def tal_de(local, tipo): return local if tipo != 'Parcela' else str(local).rsplit('-', 1)[0]


def cultivo(c, saf):
    return dict(id=c['id'], saf=saf, faz=c['fazenda'], faixa=c['local'], tipo=c['tipo'], talhao=tal_de(c['local'], c['tipo']), area=c['area'],
                cult=c['cultura'], var=c['variedade'], plantio=c['plantio'], plano=c.get('plano') or None, colheita=c.get('colheita') or None,
                colheita_real=c.get('colheita_real') or None, ciclo=c.get('ciclo') or None, origem=c.get('origem') or '')


def cultivos(fonte=None):
    fonte = D2.CULTIVOS if fonte is None else fonte
    return [cultivo(c, sid) for sid, lst in fonte.items() for c in lst]
