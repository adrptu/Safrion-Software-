# -*- coding: utf-8 -*-
"""Configurações (CONF-01; docs/configuracoes/ESPECIFICACAO.md) · seed sintético e prefixo de TODA tela (CONF0 + configuracoes.js).

Fonte única por fato (§1): pessoa = CD-04 (cad_ativos_pessoas.pessoas(), a mesma função da tela); papel padrão = G2_PERFIS e alçada
padrão = G2_ALCADAS (bloco <perfis> do g2lib.js); o que o CF-01 muda vive em c.conf do cenário salvo (talhao-os-cenario-v1), ausente → padrão.
Aqui o Python só monta CONF0: pessoas com acesso inicial, eventos da implantação (CONF-D22), conexões de demonstração (CONF-D20) e os
níveis da alçada de compras lidos de dados2.ALCADA (AL-16, só leitura, CONF-D23). Nenhuma credencial existe no protótipo (ENG-017)."""
import json, os, re, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
VERSAO = 1
DIA_OP = '2026-09-26'      # data operacional da demonstração (a mesma de CEN_DIA_OP)
FEM = {'Ana', 'Paula', 'Marta'}     # rótulo do papel no feminino ("gestora", "agrônoma"); sintético (Marta: BEN-1)
# implantação (CONF-D22): Ana recebe o acesso da plataforma no aceite do contrato v1 (28/06) e concede aos outros no início do contrato (01/07);
# quem foi admitido depois recebe na admissão (Lucas, 01/08). Beto (admitido em 22/09) segue sem acesso.
ACESSO_INI = {'p1': ('2026-06-28', 'Plataforma (implantação)')}
ORDEM_IMPL = ['p11', 'p2', 'p3', 'p6', 'p10', 'p5', 'p7', 'p8', 'p4']   # Caio, Marcos, Carlos, Paula, Nilton, João, Rui, Zé; depois Lucas
CONEXOES = [
    dict(id='erp', t='ERP · Sankhya', traz='pedidos de compra e notas fiscais de entrada', leva='movimentos que mudam o físico do Estoque (recebimento de NF, entrega, devolução, ajuste e consumo baixado)',
         escritor='Estoque e O.S. escrevem o movimento; o ERP escreve o financeiro e o fiscal', ult='2026-09-26 06:40', onde='Suprimentos › Estoque'),
    dict(id='est', t='Estação meteorológica · Santa Rita', traz='chuva, temperatura, umidade e vento a cada hora', leva='nada',
         escritor='a estação escreve o clima; Irrigação e janela de aplicação só leem', ult='2026-09-26 06:00', onde='Agrícola › Irrigação'),
    dict(id='tel', t='Telemetria de máquinas', traz='horímetro e posição dos tratores e da colhedora', leva='nada',
         escritor='a telemetria escreve o horímetro; a Manutenção decide o vencimento', ult='2026-09-25 18:10', onde='Manutenção › Ativos e disponibilidade'),
    dict(id='lab', t='Laboratório de análises', traz='laudos de solo, foliar e de qualidade do insumo', leva='amostras enviadas (nº e talhão)',
         escritor='o laboratório escreve o laudo; o agrônomo decide a recomendação', ult='2026-09-18 14:00', onde='Agrícola › Planos agronômicos'),
    dict(id='app', t='App de campo', traz='apontamentos, recebimentos e ocorrências do aparelho', leva='ordens liberadas e fichas de execução',
         escritor='o servidor decide o que soma; duplicidade vai para a conferência na O.S. (CMD-09)', ult='', onde='Agrícola › Ordem de Serviço'),
]


def _perfis_bloco():
    s = open(os.path.join(HERE, 'g2lib.js'), encoding='utf-8').read()
    return s[s.index('// <perfis>'):s.index('// </perfis>')]


def _papeis_padrao():
    """papéis padrão de G2_PERFIS (lidos do bloco <perfis>, a mesma fonte do navegador), só para o texto dos eventos da implantação."""
    b = _perfis_bloco(); i = b.index('const G2_PERFIS='); j = b.index('];', i)
    out = {}
    for m in re.finditer(r"\{k:'([^']+)',t:'[^']*',papeis:\{([^}]*)\}\}", b[i:j]):
        out[m.group(1)] = re.findall(r"(\w+):'([^']*)'", m.group(2))
    return out


def pessoas():
    """pessoas do CD-04 (mesma função da tela) com o que o CF-01 lê: equipe, função, habilidades, CREA, login inicial e gênero do rótulo."""
    import dados_cad as DC
    import areas.cad_ativos_pessoas as CAP
    by = {p['id']: dict(p, **CAP._OVR.get(p['id'], {})) for p in DC.PESSOAS}
    out = []
    for pid, v in CAP.pessoas():
        p = by[pid]
        out.append(dict(id=pid, k=v['nome'], equipe=v['equipe'], funcao=p.get('funcao', ''), hab=[h for h in str(v['hab']).split('; ') if h],
                        crea=v.get('vcrea', '') or '', login=v['acesso'] == 'Com login', adm=v.get('adm', ''), fem=v['nome'] in FEM))
    return out


def seed():
    """CONF0: pessoas, acesso inicial, eventos da implantação, conexões e alçada de compras. A versão inclui o resumo do bloco <perfis>:
    outra frente que mude G2_PERFIS ou G2_ALCADAS invalida o c.conf salvo (volta ao padrão), como o cenGet faz com o cenário."""
    import dados2 as D2
    ps = pessoas(); pad = _papeis_padrao(); by = {p['id']: p for p in ps}
    ini = {}
    for p in ps:
        if not p['login']: continue
        if p['id'] in ACESSO_INI: ini[p['id']] = ACESSO_INI[p['id']]
        elif p['adm'] > '2026-07-01': ini[p['id']] = (p['adm'], 'Ana (gestora)')
        else: ini[p['id']] = ('2026-07-01', 'Ana (gestora)')
    ordem = ['p1'] + [x for x in ORDEM_IMPL if x in ini] + [x for x in ini if x not in ORDEM_IMPL and x != 'p1']
    ev = []
    for pid in ordem:
        p = by[pid]; d, quem = ini[pid]; pp = [rot for _k, rot in pad.get(p['k'], [])]
        ev.append(dict(id='CFG-%04d' % (len(ev) + 1), d=d, at='', tipo='acesso', quem=quem, alvo=p['k'],
                       t='Acesso concedido a ' + p['k'] + ' · ' + (' e '.join(pp) if pp else 'só app de campo'),
                       ef='Ativo desde ' + '/'.join(reversed(d.split('-'))), origem='plataforma' if quem.startswith('Plataforma') else 'web'))
    compras = []
    for a in D2.ALCADA:
        compras.append(dict(ate=a['ate'], quem=a['quem']))
    s = dict(v=None, hoje=DIA_OP, pessoas=[dict(p, acesso=('ativo' if p['id'] in ini else 'sem'), desde=ini.get(p['id'], ('', ''))[0]) for p in ps],
             ev=ev, alc_desde='2026-07-01', compras=compras, conexoes=CONEXOES)
    resumo = json.dumps(s, sort_keys=True, ensure_ascii=False) + _perfis_bloco()
    s['v'] = f"CONF-{VERSAO}-{hashlib.sha1(resumo.encode('utf-8')).hexdigest()[:8]}"
    return s


_CACHE = {}


def js_prefixo():
    """prefixo de TODA tela (engine), uma vez, depois do da assinatura: CONF0 + configuracoes.js (só nomes conf*/CONF*, RV-13)."""
    if 'js' not in _CACHE:
        _CACHE['js'] = ('const CONF0 = ' + json.dumps(seed(), ensure_ascii=False).replace('</', '<\\/') + ';\n'
                        + open(os.path.join(HERE, 'configuracoes.js'), encoding='utf-8').read() + '\n')
    return _CACHE['js']


if __name__ == '__main__':
    import sys; sys.path.insert(0, HERE)
    s = seed()
    print(s['v'], len(s['pessoas']), 'pessoas ·', sum(1 for p in s['pessoas'] if p['acesso'] == 'ativo'), 'com acesso ·', len(s['ev']), 'eventos')
    for e in s['ev']: print(' ', e['id'], e['d'], e['quem'], '·', e['t'])
