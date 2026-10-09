# -*- coding: utf-8 -*-
"""Roda o espelho Python (ocupacao.py, base ou novo) sobre as fixtures. Uso: python3 roda_servico.py <dir com ocupacao.py> <fixtures.json> [semmsg]"""
import sys, json, time, importlib.util
spec = importlib.util.spec_from_file_location('ocx', sys.argv[1] + '/ocupacao.py'); OC = importlib.util.module_from_spec(spec); spec.loader.exec_module(OC)
dados = json.load(open(sys.argv[2]))
semmsg = len(sys.argv) > 3 and sys.argv[3] == 'semmsg'
def lst(x): return json.loads(json.dumps(x))
out = {}; t_tot = 0.0
for f in dados['fixtures']:
    c = f.get('ctx') or dados['ctx']
    ctx = OC.ctx_de(c['culturas'], [tuple(x) for x in c['cultivares']], c['planos'], f['folga'])
    t0 = time.perf_counter()
    r = OC.checa(ctx, f['safras'], f['antes'], f['depois'], f['sid'], f['alvo'], f['T'])
    t1 = time.perf_counter()
    o = dict(trav=lst(r['trav']), pend=lst(r['pend']), aviso=[y['id'] for y in r['aviso']], ms_chk=(t1 - t0) * 1000)
    if r['o'] is not None and not semmsg:
        o['mt'] = OC.msg_trava(ctx, r, f['sid'], f['T'], None) if r['trav'] else ''
        o['mp'] = OC.msg_pend(ctx, r, f['sid'], None) if hasattr(OC, 'msg_pend') else None
    occ = OC.ocupacoes(ctx, f['safras'], f['depois'])
    L, band = OC.tabela(ctx, f['safras'][f['sid']], occ, [('T1', f['T']), ('T2', f['T2'])], f['safras'])
    L1 = next(v for v in L if v['t'] == 'T1')
    o['tab'] = dict(trav=lst(L1['trav']), pend=lst(L1['pend']), sit=L1['sit'], exc=L1.get('exc'), band=band, own=[x['id'] for x in L1['own']], fora=[x['id'] for x in L1['fora']],
                    faixa=OC.faixa_txt(band, L, f['T'] + f['T2']))
    t_tot += (time.perf_counter() - t0) * 1000
    out[f['id']] = o
json.dump(dict(src=sys.argv[1], ms_total=t_tot, res=out), sys.stdout, ensure_ascii=False)
