# -*- coding: utf-8 -*-
"""Fonte dos dados da Fazenda Lagoa Grande (CONTINUIDADE-MAC-20261003 / CORTE-REMOTO-01 · CAMADA-SINTETICA-01).
Reais só no Mac do proprietário (dados_lagoa_kml.py + dados_lagoa/); fora dele (GitHub, nuvem) a demonstração sintética de
dados_lagoa_sintetico/ com os mesmos nomes e formatos. SAFRION_DADOS=sintetico força a sintética mesmo com a real presente.
Nunca mistura: sem as constantes E a pasta reais, tudo vem da sintética (ROTULO = 'Demonstração sintética', mostrado nas telas).
Na sintética, a saída é gerada sozinha quando falta ou está velha (dados_lagoa_sintetico.gerar.garantir; mesma semente, mesmos bytes)."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
_REAL_DIR = os.path.join(HERE, 'dados_lagoa'); _SINT_DIR = os.path.join(HERE, 'dados_lagoa_sintetico', 'saida')
_FORCA = os.environ.get('SAFRION_DADOS') == 'sintetico'
try:
    if _FORCA or not os.path.exists(os.path.join(_REAL_DIR, 'lagoa_s2_resumo.json')): raise ImportError('sem dado real')
    from dados_lagoa_kml import LG_FONTE, LG_GEO, LG_PIVOS, LG_PERIMETROS, LG_AMBIENTAL, LG_AGUA
    REAL = True
except ImportError:
    try:
        from dados_lagoa_sintetico.kml import LG_FONTE, LG_GEO, LG_PIVOS, LG_PERIMETROS, LG_AMBIENTAL, LG_AGUA
        from dados_lagoa_sintetico import gerar as _gerar
    except ImportError as e:
        raise ImportError('Sem dados da Lagoa Grande: no Mac, dados_lagoa_kml.py (real); fora dele, gere dados_lagoa_sintetico/ '
                          '(contrato em RETOMADA-NUVEM.md)') from e
    REAL = False
DIR = _REAL_DIR if REAL else _SINT_DIR
ROTULO = '' if REAL else 'Demonstração sintética'
if not REAL: _gerar.garantir(DIR)
# número do pivô → hectares, com a MESMA precisão do mapa (2 casas): mapa, safra, O.S., doses e custos usam o mesmo valor;
# arredondar só na exibição (SINT-C01, SINT-REV-20261003-2300)
PIVOS_HA = {int(p[0][2:]): round(p[2], 2) for p in LG_PIVOS}


# ---------- outorga da água: fonte única = o cadastro (LG_AGUA, aba Água do CD-01) · CTL-5 (E3, RL-E4) ----------
# A irrigação não guarda valor de outorga: vazão, horas por dia, vencimento e situação da captação dos pivôs saem daqui.
# Formato pt-BR do cadastro (ponto é milhar, vírgula é decimal), também no dado real do Mac. Sem arredondar no dado (ENG-013).
import re as _re, datetime as _dt


def agua_ls(v):
    """vazão do cadastro em L/s: '150 m³/h' → 41,666… · '1,0 L/s' → 1,0 · '—' → None"""
    m = _re.match(r'\s*([\d.,]+)\s*(m³/h|m3/h|L/s)', str(v or ''), _re.I)
    if not m: return None
    x = float(m.group(1).replace('.', '').replace(',', '.'))
    return x / 3.6 if m.group(2).lower() in ('m³/h', 'm3/h') else x


def agua_h(reg):
    """horas por dia do regime: '20 h/dia · 12 meses' → 20 · 'contínuo' → 24 · sem regime → None"""
    m = _re.match(r'\s*(\d+(?:[.,]\d+)?)\s*h/dia', str(reg or ''))
    if m: return float(m.group(1).replace(',', '.'))
    return 24.0 if str(reg or '').strip().lower().startswith('contínuo') else None


def agua_sit(a, hoje):
    """situação do ponto de água: a MESMA regra de aguaSit do CD-01 (areas/cad_fazendas.py), conferida em outorga_unit_test.py"""
    if not a.get('tipo'): return 'Sem descrição no KML'
    if a.get('renov'): return 'Em renovação'
    if a.get('venc') and a['venc'] < hoje: return 'Vencida'
    if a.get('venc') and (_dt.date.fromisoformat(a['venc']) - _dt.date.fromisoformat(hoje)).days <= 90: return 'Vence em 90 dias'
    return 'Vigente'


def _irrig_sup(a, fin):
    return (str(a.get('tipo') or '').startswith('Outorga') and 'captação superficial' in str(a.get('modo') or '').lower()
            and str(a.get('fin') or '').lower() == fin.lower())


def captacao(agua, hoje, curso=None, fin='Irrigação'):
    """captação dos pivôs = soma das outorgas de captação superficial para a finalidade, do mesmo curso d'água, no cadastro.
    Premissa declarada (o cadastro não liga pivô a ponto de captação): sem curso, vale o de maior vazão vigente somada (rede comum
    aos pontos do curso). Outorga vencida sai da soma e fica na observação; nenhuma vigente → situação 'Vencida' (trava com o gestor)."""
    br = lambda d: '/'.join(reversed(str(d).split('-'))) if d else '—'
    sup = [a for a in agua if _irrig_sup(a, fin)]
    vale = lambda a: agua_sit(a, hoje) != 'Vencida' and agua_ls(a['vazao']) and agua_h(a['regime'])
    if not curso:
        soma = {}
        for a in sup:
            if vale(a): soma[a['curso']] = soma.get(a['curso'], 0) + agua_ls(a['vazao'])
        cursos = [a['curso'] for a in sup]
        curso = max(soma, key=soma.get) if soma else (max(cursos, key=cursos.count) if cursos else '')
    todas = [a for a in sup if a['curso'] == curso]
    ok = [a for a in todas if vale(a)]
    fora = [a['num'] + ' vencida em ' + br(a['venc']) for a in todas if a not in ok and agua_sit(a, hoje) == 'Vencida']
    if not ok:
        return dict(nome=curso or 'sem captação no cadastro', outorga=' + '.join(a['num'] for a in todas) or 'sem outorga no cadastro',
                    ls=0.0, h=0.0, venc=max([a['venc'] for a in todas if a['venc']] or ['']), st='Vencida', aviso='',
                    obs='nenhuma outorga vigente de ' + fin.lower() + ' no cadastro' + (' · ' + ', '.join(fora) if fora else ''))
    ls = sum(agua_ls(a['vazao']) for a in ok); vol = sum(agua_ls(a['vazao']) * agua_h(a['regime']) for a in ok)   # m³/dia = L/s × h × 3,6
    sits = [agua_sit(a, hoje) for a in ok]
    st = 'Em renovação' if 'Em renovação' in sits else ('Vence em 90 dias' if 'Vence em 90 dias' in sits else 'Vigente')
    pri = min(ok, key=lambda a: a['venc'] or '9999')
    al = next((a for a in ok if agua_sit(a, hoje) == st), pri)   # a outorga que motiva o aviso
    aviso = '' if st == 'Vigente' else ('Outorga ' + al['num'] + (' em renovação' if st == 'Em renovação' else ' vence em ' + br(al['venc'])))
    return dict(nome=curso, outorga=' + '.join(a['num'] for a in ok), ls=ls, h=vol / ls, venc=pri['venc'], st=st, aviso=aviso,
                obs=str(len(ok)) + ' outorgas de ' + fin.lower() + ' do ' + curso + ' no cadastro (aba Água)'
                + (' · fora da soma: ' + ', '.join(fora) if fora else ''))
