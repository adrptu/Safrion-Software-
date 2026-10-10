# -*- coding: utf-8 -*-
"""Análise de solo (SOLO-01; docs/analise-solo/ESPECIFICACAO.md §6): fonte única dos laudos sintéticos, da regra de demonstração,
do produto padrão de correção por fazenda e das medições de água no solo (capacidade de campo, ponto de murcha).
Uso: EXTRAJS[0] = cenario.js_prefixo() + dados_solo.js_prefixo() + <js da tela>. As regras ficam em solo.js (já no prefixo do cenário).
Dados sintéticos (inclusive os da Lagoa Grande). Nenhum laudo aqui é aprovação do proprietário; a tabela regional é decisão da fazenda (D-02)."""
import json
import dados2 as D2
import dados_cad as DC
import dados_lagoa_safra as DLS

HOJE = D2.HOJE_ISO            # 2026-09-23 (data do cenário)
VIAVEL = D2.VIAVEL            # chegada viável de uma compra nova (hoje + PRAZO_REPOSICAO), R18
ROTULO = 'Demonstração — tabela regional a decidir pelo proprietário'


def _an(a, v, un, met='', ld='', q=''):
    """analito do laudo: valor em texto decimal (sem float), unidade explícita, método/extrator, limite de detecção e qualificador ('<')."""
    return dict(a=a, v=v, un=un, met=met, ld=ld, q=q)


def _solo(ca, mg, k, hal, al, ext='Mehlich-1', argila=None):
    out = [_an('Ca', ca, 'cmolc/dm³', 'KCl 1 mol/L', '0,1'), _an('Mg', mg, 'cmolc/dm³', 'KCl 1 mol/L', '0,1'),
           _an('K', k, 'mg/dm³', ext, '1')]
    if hal is not None: out.append(_an('H+Al', hal, 'cmolc/dm³', 'SMP', '0,1'))
    out.append(_an('Al', al, 'cmolc/dm³', 'KCl 1 mol/L', '0,1'))
    if argila is not None: out.append(_an('Argila', argila, '%', 'densímetro', '1'))
    return out


def L(id, faz, tal, prof, coleta, lab, ext, an, sit, area, zona='', tipo='solo', lab_idx=None, arq='', por='Ana (agrônoma)', em='2026-09-20'):
    v = sit == 'Validado'
    return dict(id=id, tipo=tipo, faz=faz, tal=tal, prof=prof, coleta=coleta, lab=lab, ext=ext, an=an, sit=sit, area=area, zona=zona,
                lab_idx=lab_idx or {}, arq=arq or f'laudo_{lab.split()[0].lower()}_{tal.replace(" ", "")}_{prof.replace("–", "-") or "folha"}.pdf',
                por=(por if v else ''), em=(em if v else ''))


SR, LG = 'Santa Rita', 'Lagoa Grande'
# §6 da especificação: cátions em cmolc/dm³; K em mg/dm³ (Mehlich-1 ou Resina); valores do laboratório preservados (lab_idx)
LAUDOS = [
    L('LAU-2043', SR, 'T4', '0–20', '2026-09-12', 'Lab Solo Vale', 'Mehlich-1', _solo('3.90', '1.40', '31.28', '3.82', '0.10'), 'Validado', 204,
      zona='composta por zona (Z2 de 3 zonas)'),
    L('LAU-2044', SR, 'T4', '20–40', '2026-09-12', 'Lab Solo Vale', 'Mehlich-1', _solo('1.10', '0.50', '23.46', '3.00', '0.10', argila='32'), 'Validado', 204,
      zona='composta por zona (3 zonas)'),
    L('LAU-2048', SR, 'P1', '', '2026-09-18', 'Agrolab', 'digestão nítrico-perclórica',
      [_an('N', '48.2', 'g/kg', 'Kjeldahl', '0,1'), _an('P', '3.1', 'g/kg', 'nítrico-perclórica', '0,1'), _an('K', '17.4', '', 'nítrico-perclórica', '—'),
       _an('B', '42', 'mg/kg', 'azometina-H', '1')], 'Inconsistente', 95, tipo='folha', arq='laudo_agrolab_P1_folha.pdf'),
    L('LAU-2050', SR, 'C1', '0–20', '2026-09-19', 'Agrolab', 'Resina', _solo('3.40', '1.10', '97.75', None, '0', ext='Resina'), 'Aguardando validação', 38),
    L('LAU-2061', SR, 'T1', '0–20', '2026-09-18', 'Lab Solo Vale', 'Mehlich-1', _solo('3.10', '1.25', '58.65', '3.00', '0'), 'Validado', 312),
    L('LAU-2063', SR, 'T2', '0–20', '2026-09-18', 'Lab Solo Vale', 'Mehlich-1', _solo('1.25', '0.44', '136.85', '3.06', '0.30'), 'Validado', 298),
    L('LAU-2071', LG, 'Pivô 12', '0–20', '2026-09-15', 'Agrolab', 'Mehlich-1', _solo('2.90', '0.95', '78.20', '4.05', '0.20'), 'Validado', 48.47,
      lab_idx={'V': '49'}),
    L('LAU-2072', LG, 'Pivô 12', '20–40', '2026-09-15', 'Agrolab', 'Mehlich-1', _solo('0.30', '0.20', '31.28', '4.00', '0.60', argila='20'), 'Validado', 48.47),
]
# laudo de exemplo do formulário "Registrar laudo" (D-23): nasce Aguardando validação; só depois de validado sugere a calagem do T7
EXEMPLO = dict(faz=SR, tal='T7', prof='0–20', coleta='2026-09-22', lab='Lab Solo Vale', ext='Mehlich-1', area=42,
               an=_solo('3.90', '1.30', '160.31', '2.89', '0'), arq='laudo_labsolovale_T7_0-20.pdf')
LABS = ['Lab Solo Vale', 'Agrolab', 'Embrapa Solos (convênio)']

# Regra de demonstração (D-02, D-03, D-18; R06–R08 e R10). estado: 'demonstração' ou 'desligada' (zero sugestões, laudo visível)
REGRA = dict(estado='demonstração', rotulo=ROTULO,
             v2={'Soja': '60', 'Milho': '60', 'Feijão': '60', 'Café': '60', 'Mamão Formosa': '70'},
             k=dict(culturas=['Soja'], ext='Mehlich-1', cortes=['40', '80', '120'], classes=['baixo', 'médio', 'adequado', 'alto'],
                    faixa=['2400', '4800'], tabela=[['3600', {'baixo': '90', 'médio': '72', 'adequado': '48', 'alto': '0'}],
                                                    ['4800', {'baixo': '108', 'médio': '90', 'adequado': '60', 'alto': '0'}]]),
             gesso=dict(estado='demonstração', ca='0.5', m='20', k={'Anual': '50', 'Perene': '75'}),
             validade=dict(meses=24, irrigado=12),
             tol=dict(pp='0.5', cmolc='0.05'))   # D-17: diferença do laboratório acima disto mostra "difere do laboratório"
# produto padrão de correção por fazenda (D-12); trocar o produto é ação explícita no painel (R19)
CORR = {SR: dict(cal='Calcário dolomítico'), LG: dict(cal='Calcário dolomítico filler', ges='Gesso agrícola')}
# talhões irrigados (validade de 12 meses, D-18): setores do módulo Irrigação (dados_irrigacao: P1, P2, T7) e os pivôs da Lagoa Grande
IRRIGADOS = ['P1', 'P2', 'T7'] + sorted(DLS.TALHOES)

# ---------- água no solo (pedido do proprietário 05–09/10: teste de capacidade de campo por talhão) ----------
# Propriedade do solo, medida por talhão ou zona. Não é capacidade do equipamento (pivô) nem recomendação técnica: a lâmina continua
# vindo da política de água (PA-07) e do responsável técnico. CAD = (CC − PMP) × profundidade efetiva (solo.js, soloCAD).
AGUA = [
    dict(id='AGS-001', faz=SR, tal='T7', zona='', data='2026-08-20', prof='0–40', z='40', met='Curva de retenção (laboratório)', un='% volume',
         cc='32', pmp='18', fonte='Lab Solo Vale', resp='Ana (agrônoma)'),
    dict(id='AGS-002', faz=SR, tal='P1', zona='', data='2026-08-28', prof='0–30', z='30', met='Anel volumétrico (campo + estufa)', un='% volume',
         cc='28', pmp='15', fonte='Agrolab', resp='Ana (agrônoma)'),
    dict(id='AGS-003', faz=SR, tal='P2', zona='Z1 (baixada)', data='2026-09-02', prof='0–30', z='30', met='Curva de retenção (laboratório)', un='mm/cm',
         cc='3.1', pmp='1.6', fonte='Lab Solo Vale', resp='Ana (agrônoma)'),
    dict(id='AGS-004', faz=LG, tal='Pivô 12', zona='', data='2026-09-16', prof='0–40', z='40', met='Capacidade de campo no campo (inundação e drenagem)', un='% volume',
         cc='30', pmp='', fonte='Agrolab', resp='Ana (agrônoma)'),
]
METODOS_AGUA = ['Curva de retenção (laboratório)', 'Anel volumétrico (campo + estufa)', 'Capacidade de campo no campo (inundação e drenagem)']
UN_AGUA = ['% volume', 'mm/cm']
# quem mede (revisão A9, S4): pessoas do cadastro (CD-04, dados_cad.PESSOAS) das equipes de Agronomia e Irrigação; a agrônoma no texto da semente
RESP_AGUA = ['Ana (agrônoma)'] + [f"{p['nome']} ({p['funcao'].lower()})" for p in DC.PESSOAS if p['equipe'] in ('Agronomia', 'Irrigação') and p['nome'] != 'Ana']


def _talhao(c):
    return c['local'] if c['tipo'] != 'Parcela' else c['local'].rsplit('-', 1)[0]


def cultivos():
    """cultivos das safras abertas (AG-02, "Uso no plano"): mesma fonte do Planejar safra (dados2), com o talhão de cada parcela (R02)."""
    out = []
    for s in D2.SAFRAS:
        if s['ro']: continue
        for c in D2.CULTIVOS.get(s['id'], []):
            out.append(dict(id=c['id'], saf=s['id'], safNome=s['nome'], faz=s.get('fazenda', SR), local=c['local'], tal=_talhao(c), cultura=c['cultura'],
                            area=c['area'], meta=c['meta'], unm=c['un_meta'], plano=c['plano'] or '', plantio=c['plantio'], colheita=c.get('colheita') or ''))
    return out


def os_chave():
    """cultivo|atividade → O.S. do registro (R11: a O.S. existente decide se ainda dá para mudar a dose)."""
    import dados as D
    out = {}
    for o in D.ORDENS + D.ORDENS_LG:
        k = o.get('chave')
        for x in (k if isinstance(k, (list, tuple)) else ([k] if k else [])): out[x] = o['id']
    return out


def dados():
    itens = {}
    for p in D2.PLANOS:
        for a in p['atividades']:
            for x in a['prods']: itens.setdefault(x['prod'], dict(un=x['un'], grupo=x['grupo']))
    for n, x in DC.ITENS_NOVOS.items(): itens.setdefault(n, dict(un=x['un'], grupo=x['grupo']))
    corr_prods = sorted({p for f in CORR.values() for p in f.values()})
    return dict(hoje=HOJE, viavel=VIAVEL, laudos=LAUDOS, exemplo=EXEMPLO, labs=LABS, regra=REGRA, corr=CORR, irrigados=IRRIGADOS,
                gar={n: {k: v for k, v in g.items() if k != 'txt'} for n, g in DC.GARANTIA.items()},
                preco={n: DC.preco_ref(n) for n in list(itens) if DC.preco_ref(n) != ''},
                itens={n: itens[n] for n in corr_prods + ['KCl 60%'] if n in itens},
                classe={c[0]: c[2] for c in DC.CULTURAS}, agua=AGUA, metodosAgua=METODOS_AGUA, unAgua=UN_AGUA,
                cult=cultivos(), osChave=os_chave(),
                planos={p['id']: dict(id=p['id'], nome=p['nome'], versao=p['versao'], cultura=p['cultura'], atividades=p['atividades']) for p in D2.PLANOS},
                safras={s['id']: dict(nome=s['nome'], faz=s.get('fazenda', SR), ro=s['ro']) for s in D2.SAFRAS})


def js_prefixo():
    return 'const SOLO0 = ' + json.dumps(dados(), ensure_ascii=False).replace('</', '<\\/') + ';\n'


if __name__ == '__main__':
    d = dados(); print(len(d['laudos']), 'laudos ·', len(d['cult']), 'cultivos ·', d['preco'].get('Calcário dolomítico'), '· os', d['osChave'])
