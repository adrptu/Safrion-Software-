# -*- coding: utf-8 -*-
"""Pragas e doenças (MIP/MID): base ÚNICA de vistorias para o Mapa (camada Pragas e doenças), AG-01 (lista + painel), AG-01det
(rota e evidências), AG-03/AG-04 (diagnósticos e receituários do MIP) e o app de campo (MB-06).

Uso nas telas: EXTRAJS[0] = cenario.js_prefixo() + dados_mip.js_prefixo() + <js da tela>. A tela chama mipOuvir(self) e lê mipGet().
Estado no navegador: localStorage 'talhao-os-mip-v1' (vistorias, decisões, DIA, REC/RA, aplicações e contadores). Sem localStorage,
vale só na tela aberta. A O.S. de controle vai para o cenário compartilhado das O.S. ('talhao-os-cenario-v1', formato osc.novo).

Regras (PRD AG-01/AG-03/AG-04, CAL-12, RN-016 e decisões do proprietário de 01–02/10/2026):
- Protocolo por cultura × fase × alvo: método, unidade, critério (NC numérico ou presença), NC por estádio, pontos = área ÷ área por
  ponto entre o mínimo e o máximo (mamão: 20 plantas por pivô), intervalo (semanal; nematoide 30 dias).
- Média = soma das observações válidas ÷ amostras válidas; ponto fora da tolerância de GPS ou em recoleta sai da média e fica à vista.
- Resultado: média ≥ NC → acima do NC; abaixo do NC com ≥ 2 pontos de reboleira (≥ 2 × NC) → foco (mais reboleiras nunca rebaixam o
  resultado; acima de 30 % dos pontos a reboleira é "larga" e a decisão sugere controlar o talhão); ≥ 80 % do NC → perto do NC (revisita
  em 3 dias); senão abaixo do NC (seguir monitorando). Presença (viroses) → foco, sem dividir por zero.
- Ritmo por talhão × alvo: a última vistoria encerrada sem a seguinte e com a prevista vencida fica "Vistoria atrasada" (Programar vistoria).
- Coleta: ponto da vez = o primeiro sem contagem, depois os de recoleta; percentual até 100; ponto corrigível até a decisão; vistoria
  concluída com falta ou recoleta e sem decisão reabre no app ("Completar coleta").
- O.S. cancelada sem execução não conta como aplicação (nº máximo e rotação); a nova decisão reaproveita o DIA e o receituário antigo
  fica "Cancelado", substituído pelo novo.
- Produto elegível = uso registrado para cultura × alvo em agrofit_dados (só leitura); travas só legais/segurança; o resto é alerta.
Dados DEMONSTRATIVOS (NC, pontos, doses). Santa Rita = fazenda desenhada; Lagoa Grande = pivôs reais do KML com vistorias demonstrativas.
Datas de coleta até o "hoje" da demonstração (23/09/2026); só vistoria programada tem data futura.
"""
import json, os, re, math, datetime as _dt
import agrofit_dados as A
import dados_lagoa_safra as DLS

HERE = os.path.dirname(os.path.abspath(__file__))
HOJE = '2026-09-23'
KEY = 'talhao-os-mip-v1'
SR, LG = 'Santa Rita', 'Lagoa Grande'

# ---------------------------------------------------------------- protocolos (cultura × fase × alvo)
# fases: prefixos aceitos ('*' = qualquer fase com cultura). ncf: NC por estádio (prefixo da fase → NC). ap: ha por ponto.
def P(id, cultura, fases, alvo, chave, tipo, met, un, crit, nc, ap, pmin, pmax, inter, ver, ncf=None, sem=''):
    return dict(id=id, cultura=cultura, fases=fases, alvo=alvo, chave=chave, tipo=tipo, met=met, un=un, crit=crit, nc=nc, ncf=ncf,
                ap=ap, pmin=pmin, pmax=pmax, inter=inter, ver=ver, sem=sem)
_MAMAO = ['formação', 'início da produção', 'produção']
PROT = {p['id']: p for p in [
    P('soja-nematoide', 'Soja', ['pré-plantio'], 'Nematoide-de-cisto', 'nematoide-de-cisto', 'Nematoide',
      'trincheira · solo 0–20 cm', 'cistos/200 cm³', 'nc', 15, 15, 10, 20, 30, 'MIP Soja v4'),
    P('soja-daninhas', 'Soja', ['pré-plantio'], 'Daninhas pré-plantio', 'daninhas · dessecação pré-plantio', 'Planta daninha',
      'caminhamento · quadro de 1 m²', 'plantas/m²', 'nc', 5, 18, 8, 16, 7, 'MIP Soja v4'),
    P('feijao-mosca', 'Feijão', ['V', 'R'], 'Mosca-branca', 'mosca-branca', 'Praga',
      'adultos no folíolo do terço superior', 'adultos/folíolo', 'nc', 4.0, 8, 10, 20, 7, 'MIP Feijão v2', ncf=[['V', 2.0], ['R', 4.0]]),
    P('feijao-acaro', 'Feijão', ['V', 'R'], 'Ácaro-branco', 'ácaro-branco', 'Praga',
      'folíolos do ponteiro', '% folíolos com ácaro', 'nc', 20, 7, 10, 20, 7, 'MIP Feijão v2',
      sem='Sem produto registrado para feijão × ácaro-branco nesta base · conferir no AGROFIT oficial'),
    P('feijao-percevejo', 'Feijão', ['V', 'R'], 'Percevejo', 'percevejo', 'Praga',
      'pano de batida · 1 m de fileira', 'percevejos/pano', 'nc', 2.0, 8, 10, 20, 7, 'MIP Feijão v2',
      sem='Sem produto registrado para feijão × percevejo nesta base · conferir no AGROFIT oficial'),
    P('milho-lagarta', 'Milho', ['V', 'R'], 'Lagarta-do-cartucho', 'lagarta-do-cartucho', 'Praga',
      'cartucho raspado · 10 plantas seguidas', '% plantas atacadas', 'nc', 20, 6, 10, 20, 7, 'MIP Milho v3'),
    P('cafe-phoma', 'Café', ['*'], 'Mancha-de-phoma', 'mancha-de-phoma', 'Doença',
      'ramos do terço superior', '% ramos com lesão', 'nc', 10, 3.2, 8, 20, 7, 'MIP Café v1'),
    P('mamao-acaro', 'Mamão', _MAMAO, 'Ácaro-rajado', 'ácaro-rajado', 'Praga',
      'folhas do terço médio · 1 planta por ponto', '% folhas com ácaro', 'nc', 15, 1, 20, 20, 7, 'MIP Mamão v2'),
    P('mamao-mosca', 'Mamão', _MAMAO, 'Mosca-branca', 'mosca-branca', 'Praga',
      'adultos na folha do terço superior', 'adultos/folha', 'nc', 10, 1, 20, 20, 7, 'MIP Mamão v2'),
    P('mamao-antracnose', 'Mamão', _MAMAO, 'Antracnose', 'antracnose', 'Doença',
      '5 frutos por planta', '% frutos com lesão', 'nc', 5, 1, 20, 20, 7, 'MIP Mamão v2'),
    P('mamao-cochonilha', 'Mamão', _MAMAO, 'Cochonilha', 'cochonilha', 'Praga',
      'tronco e frutos · 1 planta por ponto', '% plantas com colônia', 'nc', 10, 1, 20, 20, 7, 'MIP Mamão v2'),
    P('mamao-meleira', 'Mamão', _MAMAO, 'Meleira (virose)', 'meleira', 'Virose',
      'planta a planta nas linhas da amostra', 'plantas com sintoma', 'presenca', None, 1, 20, 20, 7, 'MIP Mamão v2',
      sem='Virose sem controle químico: arrancar e destruir as plantas com sintoma (roguing)'),
    P('mamao-anelar', 'Mamão', _MAMAO, 'Mancha-anelar (PRSV)', 'mancha-anelar', 'Virose',
      'planta a planta nas linhas da amostra', 'plantas com sintoma', 'presenca', None, 1, 20, 20, 7, 'MIP Mamão v2',
      sem='Virose sem controle químico: arrancar e destruir as plantas com sintoma (roguing)'),
    P('inspecao', '*', ['*'], 'Inspeção de mancha', '', 'Investigação',
      'caminhamento até o centroide · 5 pontos', 'pontos com sintoma', 'presenca', None, 1, 5, 5, 7, 'Inspeção dirigida'),
]}

# ---------------------------------------------------------------- talhões (cultura, fase, área, colheita)
# colheita: 'aaaa-mm-dd' (prevista), 'contínua' (mamão em produção, colheita semanal) ou '' (sem colheita no horizonte)
TAL = {
    'T1': dict(faz=SR, rot='T1', cultura='Soja', fase='pré-plantio', area=312, colheita=''),
    'T2': dict(faz=SR, rot='T2', cultura='Soja', fase='pré-plantio', area=298, colheita=''),
    'T3': dict(faz=SR, rot='T3', cultura='Soja', fase='pré-plantio', area=96, colheita=''),
    'T4': dict(faz=SR, rot='T4', cultura='Soja', fase='pré-plantio', area=204, colheita=''),
    'P1': dict(faz=SR, rot='P1', cultura='Feijão', fase='R5', area=95, colheita='2026-10-10'),
    'P2': dict(faz=SR, rot='P2', cultura='Milho', fase='V10', area=80, colheita='2026-11-15'),
    'T7': dict(faz=SR, rot='T7', cultura='Mamão', fase='produção', area=42, colheita='contínua'),
    'C1': dict(faz=SR, rot='C1', cultura='Café', fase='granação', area=38, colheita='2027-05-20'),
}
def _fase_mamao(plantio):
    d = (_dt.date.fromisoformat(HOJE) - _dt.date.fromisoformat(plantio)).days
    if d < 0: return '', ''
    if d < 90: return 'formação inicial', ''
    if d < 240: return 'formação · pré-florada', ''
    if d < 300: return 'início da produção', 'contínua'
    return 'produção', 'contínua'
for _n, _ha in DLS.PIVOS.items():
    _c = next((c for c in DLS.CULTIVOS if c['local'] == DLS.nome(_n)), None)
    _f, _col = _fase_mamao(_c['plantio']) if _c else ('', '')
    TAL[DLS.pid(_n)] = dict(faz=LG, rot=DLS.nome(_n), cultura=('Mamão' if _f else ''), fase=_f, area=_ha, colheita=_col)

# centro e raio para a rota em W do AG-01det (Santa Rita: desenho demonstrativo; Lagoa Grande: centro e raio reais do KML)
_SR_LL = {'T1': (-17.832, -50.622), 'T2': (-17.832, -50.606), 'T3': (-17.848, -50.596), 'T4': (-17.846, -50.608), 'P1': (-17.838, -50.588),
          'P2': (-17.838, -50.578), 'T7': (-17.848, -50.586), 'C1': (-17.848, -50.576)}
for _t, _ll in _SR_LL.items(): TAL[_t].update(ll=list(_ll), r=round(math.sqrt(TAL[_t]['area'] * 1e4 / math.pi)))
for _p in json.load(open(os.path.join(__import__('dados_lagoa_fonte').DIR, 'lagoa_s2_resumo.json'), encoding='utf-8'))['pivos']:
    if _p['id'] in TAL: TAL[_p['id']].update(ll=[_p['lat'], _p['lon']], r=round(_p['r_m']))

def prots_do(t):
    """Protocolos válidos para o talhão (cultura × fase); talhão sem cultura não tem protocolo (só a inspeção dirigida)."""
    x = TAL[t]
    if not x['cultura']: return []
    return [p['id'] for p in PROT.values() if p['cultura'] == x['cultura'] and
            (p['fases'] == ['*'] or any(x['fase'].startswith(f) for f in p['fases']))]

def pontos(prot, area):
    p = PROT[prot]
    return max(p['pmin'], min(p['pmax'], math.ceil(area / p['ap'])))

# ---------------------------------------------------------------- Agrofit (só leitura): usos elegíveis por cultura × alvo
def _num(s): return float(s.replace('.', '').replace(',', '.')) if ',' in s else float(s)
def _dose(txt, cultura):
    """'0,50–0,75 L/ha' → (0.5, 0.75, 'L'); mL→L e g→kg; '/100 L de água' → por ha com calda de 1.000 L/ha (mamão)."""
    m = re.match(r'\s*([\d.,]+)(?:\s*–\s*([\d.,]+))?\s*(mL|L|g|kg)\s*/\s*(ha|100 L de água)', txt)
    if not m: return None
    a = _num(m.group(1)); b = _num(m.group(2)) if m.group(2) else a; un = m.group(3); base = m.group(4)
    if un == 'mL': a, b, un = a / 1000, b / 1000, 'L'
    if un == 'g': a, b, un = a / 1000, b / 1000, 'kg'
    if base != 'ha': a, b = a * 10, b * 10          # calda de 1.000 L/ha = 10 × 100 L
    return round(a, 3), round(b, 3), un
def _dias(txt):
    m = re.match(r'\s*(\d+)\s*dias?', txt or '')
    if m: return int(m.group(1))
    return 0 if 'sem restri' in (txt or '') else None
def _max(x):
    if isinstance(x, int): return x
    m = re.match(r'\s*(\d+)', str(x or '')); return int(m.group(1)) if m else None
def uso(q, u):
    """Um uso da bula de referência (agrofit_dados) → dose por ha, carência e máximo de aplicações. Derivação única (Frente E · ENG-011):
    alimenta o AGF do AG-01 e o CARD da O.S. (dados_carencia._usos). Dose só por semente (TS) → None."""
    d = _dose(u['dose'], u['cultura'])
    if not d: return None
    return dict(id=q['id'], nome=q['nomes_fazenda'][0], cls=q['classe'], gr=q['grupos'], g=q['grupo'], sit=q['situacao'],
                conf=bool(u['conferido']), dose=u['dose'], dmin=d[0], dmax=d[1], un=d[2], car=_dias(u['carencia']),
                cart=u['carencia'], mx=_max(u['max_aplic']), inter=u.get('intervalo', ''), calda=('/100 L de água' in u['dose']))
def _agf():
    out = {}
    for p in PROT.values():
        if not p['chave'] or p['cultura'] == '*': continue
        k = p['cultura'] + '|' + p['chave']
        if k in out: continue
        lst = []
        for q in A.PRODUTOS:
            if not q['grupos']: continue          # adjuvante não é controle
            for u in q['usos']:
                if u['cultura'] != p['cultura'] or u['chave'] != p['chave']: continue
                x = uso(q, u)
                if not x: continue                # tratamento de sementes (TS) não entra no receituário foliar do MIP
                lst.append(x)
                break
        out[k] = sorted(lst, key=lambda x: (x['sit'] == 'Cancelado', x['car'] if x['car'] is not None else 0, x['nome']))
    return out
AGF = _agf()
GRUPO = {q['id']: dict(nome=q['nomes_fazenda'][0], gr=q['grupos'], g=q['grupo']) for q in A.PRODUTOS}

# ---------------------------------------------------------------- vistorias (semente)
def _pts(vals, rec=(), npts=None):
    n = npts or len(vals)
    out = []
    for i in range(n):
        v = vals[i] if i < len(vals) else None
        out.append(dict(n=i + 1, v=v, ok=(i + 1) not in rec, rec=(i + 1) in rec))
    return out
def V(id, tal, prot, data, resp, vals, est='concluida', rec=(), npts=None, pend=None, dec=None, dia='', nota=''):
    n = npts or pontos(prot, TAL[tal]['area'])
    assert len(vals) <= n, (id, len(vals), n)
    return dict(id=id, faz=TAL[tal]['faz'], tal=tal, prot=prot, data=data, resp=resp, est=est, npts=n, pts=_pts(vals, rec, n),
                pend=pend or [], dec=dec, dia=dia, nota=nota, orig='seed', parcial=False, pos_de='')
def D(t, por, em, **kw): return dict(t=t, por=por, em=em, **kw)
_OSA = {o['id']: o['area'] for o in DLS.ORDENS}   # área decidida = área da O.S. ligada (mesma fonte das ordens)
VIS = [
    # ---- Santa Rita
    V('VIS-006', 'P1', 'feijao-percevejo', '2026-09-04', 'Marcos', [1, 0, 1, 1, 0, 1, 1, 0, 1, 2, 0, 2],
      dec=D('monitorar', 'Ana', '2026-09-04', prox='2026-09-11')),
    V('VIS-008', 'T7', 'mamao-acaro', '2026-09-08', 'Marcos', [10, 20, 10, 10, 20, 10, 10, 20, 10, 0, 10, 20, 10, 10, 20, 10, 10, 10, 10, 10]),
    V('VIS-011', 'T4', 'soja-nematoide', '2026-09-15', 'Marcos', [4, 6, 12, 34, 5, 7, 41, 3, 13, 29, 9, 5, 4, 6], rec=(11,),
      dec=D('controlar', 'Ana', '2026-09-17', dia='DIA-007', rec='REC-014', os='OS-0420', area=204,
            nota='Reboleiras nos pontos 04, 07 e 10: cultivar resistente 58 W, TS e K na base (REC-014)'), dia='DIA-007'),
    V('VIS-012', 'P2', 'milho-lagarta', '2026-09-08', 'Marcos', [10, 0, 10, 10, 0, 10, 10, 0, 10, 10, 0, 10, 10, 10],
      dec=D('monitorar', 'Marcos', '2026-09-08', dia='DIA-008', prox='2026-09-15'), dia='DIA-008'),
    V('VIS-013', 'P1', 'feijao-mosca', '2026-09-18', 'Marcos', [4.2, 5.6, 6.1, 4.8, 5.0, 5.9, 4.4, 5.3, 4.9, 5.5, 4.6, 4.9], dia='DIA-009'),
    V('VIS-014', 'P1', 'feijao-acaro', '2026-09-22', 'Marcos', [5, 10, 0, 10, 15, 5, 10, 20, 10], est='coleta'),
    V('VIS-015', 'P2', 'milho-lagarta', '2026-09-22', 'Marcos', [10, 20, 10, 10, 0, 20, 10, 10, 20, 10, 10, 10, 20, 10]),
    V('VIS-016', 'C1', 'cafe-phoma', '2026-09-22', 'João', [], pend=[14, 18, 9, 22, 16, 12], dia='DIA-010',
      nota='João concluiu a rota com 6 de 12 pontos (chuva) · pacote no aparelho, sem sinal'),
    V('VIS-017', 'T2', 'soja-daninhas', '2026-09-26', 'Marcos', [], est='programada'),
    # ---- Lagoa Grande (pivôs reais do KML; vistorias demonstrativas · monitora Lúcia)
    V('VIS-051', 'PV06', 'mamao-acaro', '2026-09-19', 'Lúcia', [20, 10, 30, 20, 10, 20, 30, 10, 20, 20, 10, 20, 10, 30, 20, 10, 20, 20, 10, 20],
      dec=D('controlar', 'Ana', '2026-09-20', os='OS-0504', ra='RA-0141', prod='abamectina-18-ec', area=_OSA['OS-0504'],
            nota='Antecipa a atividade do plano (controle de ácaro e cochonilha)')),
    V('VIS-052', 'PV23', 'mamao-antracnose', '2026-09-17', 'Lúcia', [20, 0, 20, 0, 20, 0, 0, 20, 0, 20, 20, 0, 0, 20, 0, 20, 0, 0, 20, 0],
      dec=D('controlar', 'Ana', '2026-09-18', os='OS-0508', ra='RA-0140', prod='tebuconazol-200-ec', area=_OSA['OS-0508'])),
    V('VIS-053', 'PV09', 'mamao-meleira', '2026-09-21', 'Lúcia', [0] * 11 + [1, 1, 1] + [0] * 6,
      nota='Plantas com sintoma nas linhas 12 a 14'),
    V('VIS-054', 'PV02', 'mamao-mosca', '2026-09-22', 'Lúcia', [8, 9, 7, 10, 8, 9, 8, 11, 7, 8, 9, 8, 10, 7, 9, 8, 9, 8, 7, 8]),
    V('VIS-055', 'PV22', 'mamao-anelar', '2026-09-21', 'Lúcia', [0] * 6 + [1] + [0] * 13, nota='1 planta com anéis no fruto, linha 7'),
    V('VIS-056', 'PV18', 'mamao-cochonilha', '2026-09-20', 'Lúcia', [0] * 9 + [100] + [0] * 10,
      dec=D('monitorar', 'Ana', '2026-09-20', prox='2026-09-27')),
    V('VIS-057', 'PV04', 'mamao-acaro', '2026-09-22', 'Lúcia', [0, 10, 0, 10, 0, 0, 10, 0, 10, 0, 0, 10, 0, 10, 0, 0, 10, 0, 10, 0]),
    V('VIS-058', 'PV01', 'mamao-mosca', '2026-09-18', 'Lúcia', [2, 3, 1, 2, 2, 3, 2, 1, 2, 3, 2, 2, 1, 3, 2, 2, 3, 2, 2, 2],
      dec=D('monitorar', 'Ana', '2026-09-18', prox='2026-09-25')),
    V('VIS-059', 'PV19', 'mamao-antracnose', '2026-09-20', 'Lúcia', [0] * 12 + [20] + [0] * 7,
      dec=D('monitorar', 'Ana', '2026-09-20', prox='2026-09-27')),
    V('VIS-060', 'PV17', 'mamao-acaro', '2026-09-10', 'Lúcia', [0, 10, 0, 0, 10, 0, 0, 10, 0, 0, 10, 0, 0, 10, 0, 0, 10, 0, 0, 0],
      dec=D('monitorar', 'Ana', '2026-09-10', prox='2026-09-17')),
]
# diagnósticos do MIP (DIA-007…010 = AG-03) e recomendações (REC-015 = rascunho do DIA-009); novos: DIA-011, REC-019, RA-0142 em diante
DIA = {
    'DIA-007': dict(id='DIA-007', vis='VIS-011', tal='T4', sit='Registrada', dec='Controlar no plantio', em='2026-09-17', por='Ana', rec='REC-014',
                    hip='Reboleiras de nematoide-de-cisto e K baixo no perfil (0–20 cm)', risco='alto'),
    'DIA-008': dict(id='DIA-008', vis='VIS-012', tal='P2', sit='Registrada', dec='Seguir monitorando', em='2026-09-08', por='Marcos', rec='',
                    hip='Lagarta-do-cartucho abaixo do NC', risco='baixo'),
    'DIA-009': dict(id='DIA-009', vis='VIS-013', tal='P1', sit='A decidir', dec='', em='2026-09-18', por='Ana', rec='REC-015',
                    hip='Mosca-branca acima do NC no R5', risco='alto', laudo='LAU-2048'),
    'DIA-010': dict(id='DIA-010', vis='VIS-016', tal='C1', sit='A decidir', dec='', em='2026-09-22', por='Ana', rec='',
                    hip='Mancha-de-phoma em expansão na granação', risco='alto'),
}
REC = {'REC-015': dict(id='REC-015', dia='DIA-009', vis='VIS-013', tal='P1', sit='Rascunho', ra='', prod='', os='')}
# aplicações do ciclo (rotação de modo de ação e nº máximo de aplicações); as O.S. de controle do MIP entram aqui ao emitir
APL = [
    dict(tal='P1', data='2026-08-25', prod='acaricida-d', chave='mosca-branca', os=''),
    dict(tal='P1', data='2026-09-08', prod='inseticida-b', chave='mosca-branca', os=''),
    dict(tal='T7', data='2026-08-20', prod='acaricida-d', chave='ácaro-rajado', os=''),
    dict(tal='PV06', data='2026-08-28', prod='abamectina-18-ec', chave='ácaro-rajado', os=''),
    dict(tal='PV06', data='2026-09-24', prod='abamectina-18-ec', chave='ácaro-rajado', os='OS-0504'),
    dict(tal='PV23', data='2026-09-03', prod='mancozebe-750-wg', chave='antracnose', os=''),
    dict(tal='PV23', data='2026-09-19', prod='tebuconazol-200-ec', chave='antracnose', os='OS-0508'),
]
# conjunto da O.S. de controle (mesmo rendimento da tela O.S.)
CONJ = {'Pulverização': dict(conj='Trator 02 MF 7719 + Pulverizador PJ-3030 36 m', rend=21.6),
        'Pulverização · mamão': dict(conj='Turbopulverizador 2.000 L + Trator 05', rend=6.0),
        'Tratos culturais': dict(conj='Equipe de tratos culturais (6 pessoas)', rend=0.6)}
RESP = {SR: ['Marcos', 'João'], LG: ['Lúcia', 'Wesley']}

_GPS11 = ['−17,840 · −50,615', '−17,841 · −50,614', '−17,842 · −50,613', '−17,843 · −50,611', '−17,843 · −50,610', '−17,844 · −50,610', '−17,845 · −50,609',
          '−17,846 · −50,608', '−17,847 · −50,607', '−17,848 · −50,606', '−17,849 · −50,604', '−17,850 · −50,603', '−17,850 · −50,602', '−17,851 · −50,601']
_HORA11 = ['07:28', '07:35', '07:42', '07:55', '08:02', '08:08', '08:15', '08:26', '08:37', '08:48', '09:02', '09:10', '09:20', '09:30']
for _v in VIS:
    if _v['id'] == 'VIS-011':
        for _x, _g, _h in zip(_v['pts'], _GPS11, _HORA11): _x.update(gps=_g, h=_h, gm=(42 if _x['n'] == 11 else 4))

def seed():
    # v=2 (04/10, PRE-REV-20261004): área das decisões ligadas = área da O.S.; descarta o estado salvo com a área antiga
    return dict(v=2, rev=0, origemSemente='sintetica', vis={v['id']: v for v in VIS}, dia=DIA, rec=REC, apl=APL, seq=dict(vis=18, dia=11, rec=19, ra=142))

def estatico():
    return dict(hoje=HOJE, key=KEY, prot=PROT, tal=TAL, agf=AGF, grupo=GRUPO, conj=CONJ, resp=RESP, rt='Ana',
                prots={t: prots_do(t) for t in TAL})

def verificar():
    """Coerência da semente (falha no build): datas, pontos × protocolo, médias e resultados citados nas telas."""
    s = seed()
    for v in s['vis'].values():
        p = PROT[v['prot']]; t = TAL[v['tal']]
        assert v['prot'] in prots_do(v['tal']), (v['id'], 'protocolo fora da cultura/fase', v['prot'], v['tal'])
        assert v['npts'] == pontos(v['prot'], t['area']), (v['id'], v['npts'], pontos(v['prot'], t['area']))
        if v['est'] != 'programada': assert v['data'] <= HOJE, (v['id'], 'coleta no futuro', v['data'])
    def media(i):
        v = s['vis'][i]; val = [x['v'] for x in v['pts'] if x['v'] is not None and x['ok'] and not x['rec']]
        return sum(val) / len(val)
    assert abs(media('VIS-011') - 13.0) < 1e-9          # 169 / 13 válidos (ponto 11 em recoleta) → foco, não acima do NC 15
    assert round(media('VIS-013'), 1) == 5.1             # acima do NC 4,0 (R5)
    assert abs(media('VIS-051') - 18) < 1e-9 and abs(media('VIS-052') - 9) < 1e-9 and abs(media('VIS-054') - 8.4) < 1e-9
    assert [x['id'] for x in AGF['Feijão|mosca-branca']] == ['ciantraniliprole-100-od', 'acaricida-d', 'inseticida-b', 'piriproxifem-100-ec'], AGF['Feijão|mosca-branca']
    assert AGF['Feijão|ácaro-branco'] == [] and AGF['Mamão|meleira'] == []
    return True

def js_prefixo():
    j = lambda o: json.dumps(o, ensure_ascii=False).replace('</', '<\\/')
    return ('const MIPD = ' + j(estatico()) + ';\nconst MIP0 = ' + j(seed()) + ';\n'
            + open(os.path.join(HERE, 'mip.js'), encoding='utf-8').read() + '\n')

if __name__ == '__main__':
    verificar()
    for k, v in AGF.items(): print(k, [(x['nome'], x['g'], x['dmin'], x['dmax'], x['un'], x['car'], x['mx']) for x in v])
    print({t: (x['cultura'], x['fase'], prots_do(t)) for t, x in TAL.items() if x['faz'] == LG})

