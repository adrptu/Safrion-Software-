# -*- coding: utf-8 -*-
"""Compara o oráculo v2 (força bruta dia a dia, independente do serviço) com o serviço novo (JS e Python) e com o da rodada anterior (ef0d7b2).
Uso: python3 compara2.py fixtures.json oraculo2.json js_novo.json py_novo.json js_ef0.json py_ef0.json [divergencias.json]"""
import sys, json, re, collections, datetime
fx, orc, jn, pn, je, pe_ = [json.load(open(p)) for p in sys.argv[1:7]]
F = {f['id']: f for f in fx['fixtures']}
O, JN, PN, JE, PE = orc['res'], jn['res'], pn['res'], je['res'], pe_['res']
def soma_t(tr): return [list(t) for t in tr if t[0] == 'soma']
def nsoma_t(tr): return [list(t) for t in tr if t[0] != 'soma']
def soma_p(pe): return {k: [list(p) for p in v if p[0] == 'soma'] for k, v in pe.items() if any(p[0] == 'soma' for p in v)}
def nsoma_p(pe): return {k: [list(p) for p in v if p[0] != 'soma'] for k, v in pe.items() if any(p[0] != 'soma' for p in v)}
def num(s): return float(s.replace('.', '').replace(',', '.'))
def dia(b): return (datetime.date(int(b[6:]), int(b[3:5]), int(b[:2])) - datetime.date(1970, 1, 1)).days
M1 = re.compile(r'^(?:De (\d\d/\d\d/\d{4}) a (\d\d/\d\d/\d{4})|A partir de (\d\d/\d\d/\d{4})), ([\d\.,]+) ha de \S+ estão com .+\. Máximo ([\d\.,]+) ha nesse período\.$')
div = collections.defaultdict(list); cont = collections.Counter()
for fid, o in O.items():
    if o.get('sem_alvo'): cont['sem_alvo'] += 1; continue
    jn_, pn_, je_, pe2 = JN[fid], PN[fid], JE[fid], PE[fid]
    cont['fixtures'] += 1; exp = o['soma_trav']; cont['oraculo:trava_soma'] += bool(exp); cont['oraculo:pend_soma'] += bool(o['soma_pend'])
    for nome, r in (('js_novo', jn_), ('py_novo', pn_)):
        if soma_t(r['trav']) != exp: div[nome + ':trav_soma'].append((fid, soma_t(r['trav']), exp))
        if soma_p(r['pend']) != o['soma_pend']: div[nome + ':pend_soma'].append((fid, soma_p(r['pend']), o['soma_pend']))
        t = r['tab']
        if soma_t(t['trav']) != o['tab_soma_trav']: div[nome + ':tab_trav_soma'].append((fid, soma_t(t['trav']), o['tab_soma_trav']))
        if soma_p(t['pend']) != o['tab_soma_pend']: div[nome + ':tab_pend_soma'].append((fid, soma_p(t['pend']), o['tab_soma_pend']))
        if (t['exc'] or 0) != o['tab_exc']: div[nome + ':tab_exc'].append((fid, t['exc'], o['tab_exc']))
        if (t['own'], t['fora']) != (o['tab_own'], o['tab_fora']): div[nome + ':tab_own_fora'].append((fid, t['own'], t['fora']))
        if o['tab_soma_trav'] and t['sit'] != 'Sobreposição': div[nome + ':tab_sit'].append((fid, t['sit']))
        if (t['exc'] or 0) > 0.005 and ('%s ha em sobreposição' % ('%g' % t['exc']).replace('.', ',')) not in t['faixa'] and 'em sobreposição' not in t['faixa']: div[nome + ':faixa_sem_exc'].append((fid, t['faixa']))
        if r.get('mt') and any(x[0] in ('soma', 'safra') for x in r['trav']):
            m = M1.match(r['mt'])
            if not o['m1']:
                if m: div[nome + ':m1_sem_outros_no_oraculo'].append((fid, r['mt']))
                continue
            if not m: div[nome + ':m1_formato'].append((fid, r['mt'], o['m1'])); continue
            ini = dia(m.group(1) or m.group(3)); fim_inf = m.group(3) is not None; fim = None if fim_inf else dia(m.group(2))
            got = dict(ini=ini, fim_inf=fim_inf, fim=fim, pior=num(m.group(4)), max=num(m.group(5)))
            expm = dict(ini=o['m1']['ini'], fim_inf=o['m1']['fim_inf'], fim=None if o['m1']['fim_inf'] else o['m1']['fim'], pior=o['m1']['pior'], max=o['m1']['max'])
            if got != expm: div[nome + ':m1'].append((fid, r['mt'], expm))
            if not fim_inf and fim < ini: div[nome + ':m1_periodo_invertido'].append((fid, r['mt']))
            cont[nome + ':m1_conferidas'] += 1
    for k in ('trav', 'pend', 'aviso', 'mt', 'mp'):
        if json.dumps(jn_.get(k), sort_keys=True) != json.dumps(pn_.get(k), sort_keys=True).replace('.0,', ',').replace('.0]', ']') and jn_.get(k) != pn_.get(k):
            div['paridade_novo:' + k].append((fid, jn_.get(k), pn_.get(k)))
    for k in ('trav', 'pend', 'sit', 'exc', 'band', 'faixa'):
        if jn_['tab'][k] != pn_['tab'][k]: div['paridade_novo:tab_' + k].append((fid, jn_['tab'][k], pn_['tab'][k]))
    # rodada anterior (ef0d7b2): o oráculo v2 pega o que mudou?
    for nome, r in (('js_ef0', je_), ('py_ef0', pe2)):
        if soma_t(r['trav']) != exp:
            cont[nome + ':trav_soma_difere'] += 1
            if exp and not soma_t(r['trav']): cont[nome + ':nao_trava_e_devia'] += 1
            if soma_t(r['trav']) and not exp: cont[nome + ':trava_e_nao_devia'] += 1
        if soma_p(r['pend']) != o['soma_pend']: cont[nome + ':pend_soma_difere'] += 1
    # fora da soma: o que mudou entre a rodada anterior e a correção (esperado: só a T-faixa de cultura sem ciclo com folga 0)
    if nsoma_t(je_['trav']) != nsoma_t(jn_['trav']): div['ef0×novo:trav_nao_soma'].append((fid, F[fid]['folga'], nsoma_t(je_['trav']), nsoma_t(jn_['trav'])))
    if nsoma_p(je_['pend']) != nsoma_p(jn_['pend']): div['ef0×novo:pend_nao_soma'].append((fid, F[fid]['folga'], nsoma_p(je_['pend']), nsoma_p(jn_['pend'])))
    if je_['aviso'] != jn_['aviso']: div['ef0×novo:aviso'].append((fid, je_['aviso'], jn_['aviso']))
    if o['fis'] and not jn_['trav']:
        motivo = 'sem plano/perene no dia' if not o['fis']['comPlano'] else ('par do alvo com plano na mesma área (T-faixa)' if o['fis']['cruz'] else 'SEM EXPLICACAO')
        cont['fisico_sem_trava:' + motivo] += 1
        if motivo != 'sem plano/perene no dia': div['fisico_sem_trava'].append((fid, motivo, o['fis']))
    if exp: cont['novo_trava_soma_ok'] += soma_t(jn_['trav']) == exp
print('CONTAGENS'); [print('  %-55s %d' % (k, v)) for k, v in sorted(cont.items())]
print('DIVERGÊNCIAS (classe: n)')
for k in sorted(div): print('  %-55s %d' % (k, len(div[k])))
for k in sorted(div):
    print('\n== %s (até 3) ==' % k)
    for x in div[k][:3]: print('  ', json.dumps(x, ensure_ascii=False)[:700])
print('\ntempo: oraculo %.0f ms · js_novo %.1f ms · py_novo %.1f ms · js_ef0 %.1f ms · py_ef0 %.1f ms' % (orc['ms'], jn['ms_total'], pn['ms_total'], je['ms_total'], pe_['ms_total']))
json.dump({k: v for k, v in div.items()}, open(sys.argv[7] if len(sys.argv) > 7 else 'divergencias2.json', 'w'), ensure_ascii=False)
