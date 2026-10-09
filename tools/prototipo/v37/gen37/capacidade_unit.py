# -*- coding: utf-8 -*-
"""Teste de unidade · SAF etapa única "Dimensione operações e recursos" (ESPECIFICACAO etapa-unica-3-4-5 §9.1, C1 a C24), sem navegador.
Roda o MESMO bloco CAPACIDADE da tela (safra.js, entre // >>> CAPACIDADE e // <<< CAPACIDADE) no node e o espelho dados2.capacidade em
Python sobre as mesmas ocorrências (dados2.ocorr_op, repartir com os grupos de recursos da fazenda) e confere os números da especificação:
capacidade, ocupação, necessárias, falta, soma das safras abertas da mesma fazenda, "<1 %", invariância da demanda, sobrescrita de
configuração (cfg_override), custo por cultura (resumo_cultura), partição do calendário e o texto do veredito. JS = Python (C11).
Uso: python3 capacidade_unit.py"""
import sys, os, json, copy, random, subprocess, re, datetime
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import dados2 as D2
OK, FAIL = [], []
def chk(nome, cond, det=''):
    (OK if cond else FAIL).append(nome); print(('OK    · ' if cond else 'FALHA · ') + nome + ('' if cond else ' · ' + str(det)[:900]), flush=True)
def near(a, b, tol=0.006): return a is not None and b is not None and abs(a - b) <= tol
def nf(x, d=2): return ('{:,.%df}' % d).format(x).replace(',', 'X').replace('.', ',').replace('X', '.')
SRC = open(os.path.join(HERE, 'safra.js'), encoding='utf-8').read()
BLOCO = SRC[SRC.index('// >>> CAPACIDADE'):SRC.index('// <<< CAPACIDADE')]
JS_RUN = r"""
const fs=require('fs'); eval(fs.readFileSync(process.argv[1],'utf8')+'\n;globalThis.CX={capSaf,capVeredito,fmtOcup,cargaRec,classeOc,capJanelas};');
const X=globalThis.CX; const jobs=JSON.parse(fs.readFileSync(0,'utf8')); const out=[];
for(const j of jobs){ if(j.op==='fmt'){ out.push(j.v.map(x=>X.fmtOcup(x))); continue; } if(j.op==='cls'){ out.push(j.v.map(x=>X.classeOc(...x))); continue; }
  const G=X.capSaf(j.oc,j.outras,j.recursos,j.meses,j.dias); const g={};
  Object.keys(G).forEach(k=>{ const x=G[k]; g[k]={un:x.un,cells:x.cells.map(c=>({d:c.d,dThis:c.dThis,dOth:c.dOth,cap:c.cap,ocup:c.ocup,nec:c.nec,red:c.red,soma:c.soma,own:c.own})),
    max:x.max?{mes:x.max.mes,ocup:x.max.ocup}:null,reds:x.reds.map(c=>c.mes),horas:x.horasSafra,txt:x.max?X.fmtOcup(x.max.ocup):'—',fo:(x.fora||[]).map(f=>[f.sid,f.cls,f.mi,f.h,f.n])}; });
  const r={G:g,carga:j.oc.map(i=>Object.fromEntries(Object.keys(G).map(k=>[k,X.cargaRec(i,k)])))}; if(j.ver) r.ver=X.capVeredito(G,j.oc,j.ver); out.push(r); }
process.stdout.write(JSON.stringify(out));
"""
TMP = os.path.join(HERE, '_probe'); os.makedirs(TMP, exist_ok=True); BF = os.path.join(TMP, 'capacidade_bloco.js'); open(BF, 'w', encoding='utf-8').write(BLOCO)
def js(jobs):
    p = subprocess.run(['node', '-e', JS_RUN, BF], input=json.dumps(jobs), capture_output=True, text=True, timeout=600)
    if p.returncode: raise SystemExit('node falhou: ' + p.stderr[-2000:])
    return json.loads(p.stdout)
def oc_json(o, safra=None):
    # cls = etiqueta do calendário da própria safra (classeOc no capCalc da tela): só as ocorrências desta safra a levam (revisão SAF, S3.1)
    s = SAF.get(safra) if safra else None
    return dict(mi=o['mi'], a=dict(op=o['a']['op'], nome=o['a']['nome']), dt=o['dt'].isoformat(), **({'cls': D2.classe_oc(o['dt'], o['mi'], s['ini'], s['fim'])} if s else {}),
                rp=dict(itens=[dict(nh=x.get('nh') or 0, h=x.get('h') or 0, nq=x.get('nq') or 0, semRec=bool(x.get('semRec')), Hin=(None if x.get('Hin') in (None, float('inf')) else x.get('Hin')), nome=x.get('nome')) for x in o['rp']['itens']],
                        falta=dict(semHoras=o['rp']['falta']['semHoras'])), cfs=o['cfs'])
def recs(**mod):
    rs = copy.deepcopy(D2.RECURSOS)
    for r in rs:
        if r['id'] in mod: r.update(mod[r['id']])
    return rs
def rec_js(rs): return [dict(r, pes=(r['id'] == 'oper')) for r in rs]
SAF = {s['id']: s for s in D2.SAFRAS}
def br(iso): return iso[8:10] + '/' + iso[5:7] + '/' + iso[0:4]
def ver_in(safra, oc, recursos):
    s = SAF[safra]; cs = [c for c in D2.CULTIVOS[safra]]
    com = [c for c in cs if c['plano'] and D2.PLANO.get(c['plano'], {}).get('cultura') == c['cultura']]; sem = [c for c in cs if c not in com]
    cls = dict(antes=0, fora=0, depois=0, cal=0)
    for o in oc:
        cls[D2.classe_oc(o['dt'], o['mi'], s['ini'], s['fim'])] += 1
    return dict(semPlano=[dict(local=c['local'], area=c['area']) for c in sem], aPlano=sum(c['area'] for c in com), cls=cls, ini=br(s['ini']),
                outras={x['id']: x['nome'] for x in D2.SAFRAS}, pend=sum(1 for o in oc if o['pend']), semHoras=sum(o['rp']['falta']['semHoras'] for o in oc),
                incompleto='', periodoCal=D2.MESES[0][1] + ' – ' + D2.MESES[-1][1])
def job(safra, recursos=None, planos=None, cfg=None, ver=False, outras_off=False):
    rs = recursos or D2.RECURSOS
    oc = D2.ocorr_op(safra, planos, cfg, rs)
    # outras com o período de cada uma (SAF-C02): a classe de cada ocorrência delas sai da safra de origem, dentro do capSaf
    outras = [] if outras_off else [dict(id=sid, nome=SAF[sid]['nome'], ini=SAF[sid]['ini'], fim=SAF[sid]['fim'], oc=[oc_json(o) for o in D2.ocorr_op(sid, None, None, rs)]) for sid in D2.outras_safras(safra)]
    j = dict(op='cap', oc=[oc_json(o, safra) for o in oc], outras=outras, recursos=rec_js(rs), meses=D2.MESES, dias=D2.DIAS_UTEIS)
    if ver: j['ver'] = ver_in(safra, oc, rs)
    return j, oc
def py_cap(safra, recursos=None, planos=None, cfg=None): return D2.capacidade(safra, recursos, planos, cfg)
MI = {lab: i for i, (_, lab) in enumerate(D2.MESES)}
def cel(G, k, mes): return G[k]['cells'][MI[mes]]

if __name__ == '__main__':
    J = []; P = []
    def add(nome, safra, **kw):
        j, oc = job(safra, kw.get('recursos'), kw.get('planos'), kw.get('cfg'), kw.get('ver', False), kw.get('outras_off', False)); J.append(j)
        P.append((nome, safra, kw, oc))
    add('base S2627', 'S2627', ver=True); add('base S27SF', 'S27SF', ver=True); add('base LG2627', 'LG2627', ver=True); add('base S2526', 'S2526', ver=True)
    add('Colhedoras 0', 'S2627', recursos=recs(colh=dict(un=0)), ver=True)
    add('SOJA-AT nos sem plano', 'S2627', planos={c: 'SOJA-AT' for c in ('c4', 'c5', 'c6', 'c7')}, ver=True)
    add('Tratores 5', 'S2627', recursos=recs(trator=dict(un=5)))
    add('Operadores 5', 'S2627', recursos=recs(oper=dict(un=5)), ver=True)
    add('LG Operadores 10', 'LG2627', recursos=recs(oper=dict(un=10)))
    add('LG Operadores 5', 'LG2627', recursos=recs(oper=dict(un=5)))
    add('Operadores 0', 'S2627', recursos=recs(oper=dict(un=0)))
    add('Tratores 1', 'S2627', recursos=recs(trator=dict(un=1)), ver=True)
    add('larg 12', 'S2627', cfg={('Adubação a lanço', 'Adubação de cobertura', 'r3'): dict(larg=12)})
    add('pess 3', 'S2627', cfg={('Plantio', 'Plantio e adubação de base', 'r2'): dict(pess=3)})
    add('S27SF encerrada', 'S2627', outras_off=True)
    R = js(J); RES = {}
    for (nome, safra, kw, oc), r in zip(P, R):
        RES[nome] = (r, oc)
        g = py_cap(safra, kw.get('recursos'), kw.get('planos'), kw.get('cfg'))
        if kw.get('outras_off'): continue
        dif = []
        for k, x in r['G'].items():
            for i, (a, b) in enumerate(zip(x['cells'], g[k]['cells'])):
                for f in ('d', 'dThis', 'dOth', 'cap', 'nec'):
                    if abs((a[f] or 0) - (b[f] or 0)) > 1e-6: dif.append((k, i, f, a[f], b[f]))
                if (a['ocup'] is None) != (b['ocup'] is None) or (a['ocup'] is not None and abs(a['ocup'] - b['ocup']) > 1e-6) or a['red'] != b['red']: dif.append((k, i, 'ocup/red', a['ocup'], b['ocup']))
            if x['reds'] != [c['mes'] for c in g[k]['reds']] or (x['max'] or {}).get('mes') != ((g[k]['max'] or {}).get('mes')): dif.append((k, 'max/reds'))
        chk('C11 paridade JS = Python · %s' % nome, not dif, dif[:4])
    G = RES['base S2627'][0]['G']
    c = cel(G, 'colh', 'fev/27'); chk('C1 S2627 Colhedoras fev/27 81,07 %, precisa de 1', near(c['d'], 122.0) and near(c['cap'], 150.48) and near(c['ocup'], 81.07, .005) and c['nec'] == 1, c)
    c = cel(G, 'trator', 'fev/27'); chk('C2 S2627 Tratores fev/27 (122,00 + 67,31 da Safrinha) ÷ 699,20 = 27,08 %, precisa de 2; maior uso em fev/27',
        near(c['dThis'], 122.0) and near(c['dOth'], 67.31) and near(c['cap'], 699.2) and near(c['ocup'], 27.08, .005) and c['nec'] == 2 and G['trator']['max']['mes'] == 'fev/27', (c, G['trator']['max']))
    exp3 = [('pulv', 'dez/26', 49.07, 189.0, 25.97, None), ('plant', 'out/26', 62.70, 198.0, 31.67, None), ('dist', 'nov/26', 33.89, 218.5, 15.51, None), ('oper', 'mai/27', 655.83, 1555.2, 42.17, 6)]
    for k, m, d, cap, o, nec in exp3:
        c = cel(G, k, m); chk('C3 S2627 %s maior uso %s %s %%' % (k, m, nf(o)), G[k]['max']['mes'] == m and near(c['d'], d, .01) and near(c['cap'], cap) and near(c['ocup'], o, .005) and (nec is None or c['nec'] == nec), c)
    chk('C3 Operadores out/26 precisa de 2', cel(G, 'oper', 'out/26')['nec'] == 2)
    for safra, h in (('S2627', 1241.95), ('S27SF', 460.40), ('LG2627', 86839.80), ('S2526', 0.0)):
        chk('C4 horas de Operadores no calendário · %s %s' % (safra, nf(h)), near(RES['base ' + safra][0]['G']['oper']['horas'], h, .01), RES['base ' + safra][0]['G']['oper']['horas'])
    L = RES['base LG2627'][0]['G']
    c = cel(L, 'oper', 'nov/26'); chk('C5 LG2627 Operadores nov/26 1.584,40 %, precisa de 127', near(c['d'], 23613.86, .01) and near(c['cap'], 1490.4) and near(c['ocup'], 1584.40, .005) and c['nec'] == 127, c)
    c = cel(L, 'oper', 'out/26'); chk('C5 LG2627 Operadores out/26 1.305,79 %, precisa de 105', near(c['ocup'], 1305.79, .005) and c['nec'] == 105, c)
    chk('C5 LG2627 Operadores mai/27 173,95 % (14) e ago/27 66,49 % (10)', near(cel(L, 'oper', 'mai/27')['ocup'], 173.95, .005) and cel(L, 'oper', 'mai/27')['nec'] == 14 and near(cel(L, 'oper', 'ago/27')['ocup'], 66.49, .005) and cel(L, 'oper', 'ago/27')['nec'] == 10)
    chk('C5 LG2627 Operadores em falta em 9 meses', L['oper']['reds'] == ['out/26', 'nov/26', 'dez/26', 'jan/27', 'fev/27', 'abr/27', 'mai/27', 'jul/27', 'ago/27'], L['oper']['reds'])
    c = cel(L, 'trator', 'out/26'); chk('C5 LG2627 Tratores out/26 233,51 %, precisa de 10; falta de out/26 a jan/27', near(c['d'], 1890.49, .01) and near(c['ocup'], 233.51, .005) and c['nec'] == 10 and L['trator']['reds'] == ['out/26', 'nov/26', 'dez/26', 'jan/27'], (c, L['trator']['reds']))
    G0 = RES['Colhedoras 0'][0]['G']; c = cel(G0, 'colh', 'fev/27'); oc0 = RES['Colhedoras 0'][1]
    chk('C6 Colhedoras = 0: fev/27 122,00 h, não calculável, precisa de 1 (falta); 3 pendentes', near(c['d'], 122.0) and c['ocup'] is None and c['nec'] == 1 and c['red'] and sum(1 for o in oc0 if o['pend']) == 3 and G0['colh']['txt'] == 'não calculável', (c, sum(1 for o in oc0 if o['pend'])))
    chk('C6 Tratores e Operadores de fev/27 iguais à base', near(cel(G0, 'trator', 'fev/27')['d'], cel(G, 'trator', 'fev/27')['d']) and near(cel(G0, 'oper', 'fev/27')['d'], cel(G, 'oper', 'fev/27')['d']))
    S7 = RES['base S27SF'][0]['G']
    chk('C7 S27SF maior uso Colhedoras jul/27 55,86 %; fev/27 só da S2627 não conta', S7['colh']['max']['mes'] == 'jul/27' and near(S7['colh']['max']['ocup'], 55.86, .005) and not cel(S7, 'colh', 'fev/27')['own'] and cel(S7, 'colh', 'fev/27')['d'] > 0, S7['colh']['max'])
    S6 = RES['base S2526'][0]['G']; oc6 = RES['base S2526'][1]
    chk('C8 S2526: 21 ocorrências fora do calendário, nenhuma demanda, não soma outras', len(oc6) == 21 and all(o['mi'] < 0 for o in oc6) and all(c['d'] == 0 for g in S6.values() for c in g['cells']) and D2.outras_safras('S2526') == [])
    c = cel(RES['SOJA-AT nos sem plano'][0]['G'], 'colh', 'fev/27'); chk('C9 com SOJA-AT nos sem plano: Colhedoras fev/27 182,00 ÷ 150,48 = 120,95 %, precisa de 2', near(c['d'], 182.0) and near(c['ocup'], 120.95, .005) and c['nec'] == 2, c)
    c = cel(RES['Tratores 5'][0]['G'], 'trator', 'fev/27'); chk('C10 Tratores 4 → 5: fev/27 21,66 % (189,31 ÷ 874,00)', near(c['d'], 189.31, .01) and near(c['cap'], 874.0) and near(c['ocup'], 21.66, .005), c)
    hb = {k: G[k]['horas'] for k in G}
    for nome in ('Colhedoras 0', 'Operadores 5'):
        h2 = RES[nome][0]['G']; chk('C12 invariância da demanda · %s (366,92 / 116,67 / 62,70 / 40,22 / 122,00 / 1.241,95)' % nome, all(near(h2[k]['horas'], hb[k], .01) for k in hb), {k: round(h2[k]['horas'], 2) for k in h2})
    chk('C12 base: horas por recurso', [round(hb[k], 2) for k in ('trator', 'pulv', 'plant', 'dist', 'colh', 'oper')] == [366.92, 116.67, 62.70, 40.22, 122.0, 1241.95], hb)
    chk('C12 Operadores 0: o Plantio passa ao prestador e Operadores cai para 1.116,55', near(RES['Operadores 0'][0]['G']['oper']['horas'], 1116.55, .01), RES['Operadores 0'][0]['G']['oper']['horas'])
    c = cel(RES['Operadores 5'][0]['G'], 'oper', 'mai/27'); oc5 = RES['Operadores 5'][1]
    pend5 = [o for o in oc5 if o['pend']]
    chk('C13 Operadores 8 → 5: mai/27 67,47 %, precisa de 6 (falta); 1 pendente C1 · Colheita · sem recurso na fazenda', near(c['ocup'], 67.47, .005) and c['nec'] == 6 and c['red'] and len(pend5) == 1 and pend5[0]['c']['local'] == 'C1' and pend5[0]['rp']['causa'] == 'sem recurso na fazenda', (c, [(o['c']['local'], o['a']['nome'], o['rp']['causa']) for o in pend5]))
    L10 = RES['LG Operadores 10'][0]['G']; c = cel(L10, 'oper', 'nov/26')
    chk('C14 LG Operadores 8 → 10: nov/26 1.267,52 %, pendentes 56 → 0, falta em 7 meses', near(c['ocup'], 1267.52, .005) and sum(1 for o in RES['LG Operadores 10'][1] if o['pend']) == 0 and sum(1 for o in RES['base LG2627'][1] if o['pend']) == 56 and len(L10['oper']['reds']) == 7, (c['ocup'], len(L10['oper']['reds'])))
    chk('C14 LG Operadores 8 → 5: pendentes 56 → 91', sum(1 for o in RES['LG Operadores 5'][1] if o['pend']) == 91, sum(1 for o in RES['LG Operadores 5'][1] if o['pend']))
    cf = lambda i, r: dict(id=i, nome='Colhedora ' + i, rend=r, part='', jan=40, custo_h=100, diesel='', pess=0, seq=False, troca='', ativos=[], rec=dict(colh=1))
    rp = D2.repartir(300, [cf('a', 5), cf('b', 4)], dict(colh=dict(un=1, nome='Colhedoras'))); rp2 = D2.repartir(300, [cf('a', 5), cf('b', 4)], dict(colh=dict(un=2, nome='Colhedoras')))
    chk('C15 serialização 300 ha: 1 colhedora 40,00 h e 120,00 ha sem conjunto; 2 colhedoras 66,67 h e saldo 0', near(rp['hconj'], 40.0) and near(rp['saldo'], 120.0) and near(rp2['hconj'], 66.67, .01) and near(rp2['saldo'], 0.0), (rp['hconj'], rp['saldo'], rp2['hconj'], rp2['saldo']))
    G16 = RES['Operadores 0'][0]['G']; oc16 = RES['Operadores 0'][1]
    own16 = [c for c in G16['oper']['cells'] if c['own']]
    chk('C16 Operadores 0: 30 pendentes; toda célula de Operadores desta safra não calculável e em falta', sum(1 for o in oc16 if o['pend']) == 30 and own16 and all(c['ocup'] is None and c['red'] for c in own16), (sum(1 for o in oc16 if o['pend']), len(own16)))
    c = cel(RES['Tratores 1'][0]['G'], 'trator', 'fev/27')
    chk('C17 Tratores 1: fev/27 108,30 %, precisa de 2, tem 1; sozinha 69,79 %', near(c['ocup'], 108.30, .005) and c['nec'] == 2 and c['soma'] and near(100 * c['dThis'] / c['cap'], 69.79, .005), c)
    v = RES['Tratores 1'][0]['ver']['txt']; chk('C17 veredito R2 "somando a Safrinha 2027 (67,3 h)"', 'Tratores precisam de 2 em fev/27 e você tem 1, somando a Safrinha 2027 (67,3 h)' in v, v)
    GS = RES['S27SF encerrada'][0]['G']
    chk('C18 S27SF encerrada: S2627 Tratores fev/27 17,45 %; Operadores fev/27 19,82 %', near(cel(GS, 'trator', 'fev/27')['ocup'], 17.45, .005) and near(cel(GS, 'oper', 'fev/27')['ocup'], 19.82, .005), (cel(GS, 'trator', 'fev/27')['ocup'], cel(GS, 'oper', 'fev/27')['ocup']))
    chk('C19 S2627 Operadores nov/26 4,95 %: LG2627 e S2526 não entram', near(cel(G, 'oper', 'nov/26')['ocup'], 4.95, .005) and 'LG2627' not in D2.outras_safras('S2627') and 'S2526' not in D2.outras_safras('S2627'), cel(G, 'oper', 'nov/26'))
    f = js([dict(op='fmt', v=[cel(G, 'pulv', 'jan/27')['ocup'], cel(G, 'dist', 'out/26')['ocup'], cel(G, 'trator', 'jan/27')['ocup'], 0, None, 1584.4])])[0]
    chk('C20 fmtOcup: <1 % · 1 % · <1 % · — · não calculável · 1.584 %', f == ['<1 %', '1 %', '<1 %', '—', 'não calculável', '1.584 %'] and [D2.fmt_ocup(x) for x in (cel(G, 'pulv', 'jan/27')['ocup'], cel(G, 'dist', 'out/26')['ocup'], 0, None, 1584.4)] == ['<1 %', '1 %', '—', 'não calculável', '1.584 %'], f)
    for nome in ('base S2627', 'base S27SF', 'base LG2627', 'base S2526'):
        r, oc = RES[nome]; tot = {}
        s = SAF[nome.split()[-1]]
        for o, cg in zip(oc, r['carga']):
            if o['mi'] < 0 or D2.classe_oc(o['dt'], o['mi'], s['ini'], s['fim']) != 'cal': continue
            for k, h in cg.items(): tot[(k, o['mi'])] = tot.get((k, o['mi']), 0) + h
        bad = [(k, mi) for k in r['G'] for mi in range(12) if abs(tot.get((k, mi), 0) - r['G'][k]['cells'][mi]['dThis']) > 1e-9]
        chk('C21 Σ cargaRec das ocorrências = demanda desta safra em cada recurso e mês · ' + nome, not bad, bad[:4])
    hc = sum(o['rp']['hconj'] or 0 for o in RES['base S2627'][1] if o['a']['op'] == 'Plantio' and o['mi'] == MI['out/26'])
    chk('C21 negativo: Plantadeiras out/26 Σ horas-conjunto = 125,40, não 62,70', near(hc, 125.40, .01) and near(cel(G, 'plant', 'out/26')['d'], 62.70, .01), hc)
    t = D2.plano_op('S2627', cfg_override={('Adubação a lanço', 'Adubação de cobertura', 'r3'): dict(larg=12)})
    lan = sum(o['rp']['hconj'] or 0 for o in RES['larg 12'][1] if o['a']['op'] == 'Adubação a lanço')
    chk('C22 largura 12 m na Adubação de cobertura: 595,73 h · R$ 272.513,18 · 1.275,84 h-homem · Adubação a lanço 74,11 h · Distribuidores nov/26 31,02 %',
        near(t['hconj'], 595.73, .01) and near(t['cop'], 272513.18, .01) and near(t['hh'], 1275.84, .01) and near(lan, 74.11, .01) and near(cel(RES['larg 12'][0]['G'], 'dist', 'nov/26')['ocup'], 31.02, .005), (t['hconj'], t['cop'], t['hh'], lan))
    t = D2.plano_op('S2627', cfg_override={('Plantio', 'Plantio e adubação de base', 'r2'): dict(pess=3)})
    G3 = RES['pess 3'][0]['G']
    chk('C22 3 pessoas no Plantio: Operadores 1.304,65 h · out/26 16,41 % · R$ 266.999,64', near(G3['oper']['horas'], 1304.65, .01) and near(cel(G3, 'oper', 'out/26')['ocup'], 16.41, .005) and near(t['cop'], 266999.64, .01), (G3['oper']['horas'], cel(G3, 'oper', 'out/26')['ocup'], t['cop']))
    rc = D2.resumo_cultura('S2627'); po = D2.plano_op('S2627')
    tab = {k: (round(b['area'], 2), round(b['cop'], 2), round(b['cins'], 2), round(b['rha'], 2)) for k, b in rc.items()}
    chk('C23 resumo por cultura S2627 (§4.3)', tab == {'Soja': (610, 230032.11, 1283143.0, 2480.61), 'Café': (38, 33497.55, 94848.0, 3377.51), 'Mamão Formosa': (42, 1087.41, 20559.0, 515.39)}, tab)
    chk('C23 Σ custo de operação por cultura = plano_op · Σ insumos = R$ 1.398.550,00', near(sum(b['cop'] for b in rc.values()), po['cop'], .01) and near(sum(b['cins'] for b in rc.values()), 1398550.0, .01))
    rl = D2.resumo_cultura('LG2627'); m = rl['Mamão Formosa']
    chk('C23 LG2627 Mamão parcial (56 ocorrências pendentes), nunca R$ 4.072,16', m['rha'] is None and m['npend'] == 56, (m['rha'], m['npend']))
    for safra, esp in (('S2627', (0, 0, 0, 33)), ('S27SF', (0, 0, 0, 14)), ('LG2627', (75, 0, 0, 201)), ('S2526', (0, 21, 0, 0))):
        cl = ver_in(safra, RES['base ' + safra][1], D2.RECURSOS)['cls']
        chk('C24 partição do calendário %s = antes + fora + depois + calendário' % safra, (cl['antes'], cl['fora'], cl['depois'], cl['cal']) == esp, cl)
    V = {k: RES[k][0]['ver']['txt'] for k in ('base S2627', 'base S27SF', 'base LG2627', 'base S2526', 'Colhedoras 0')}
    chk('V1 veredito S2627 (R4)', V['base S2627'] == 'Na estimativa mensal, cabe nos 690 ha com plano. Fora da conta: T4, T3, P1 e P2 (475 ha), sem plano. Prazo por talhão não verificado: 17 de 17 atividades sem janela.', V['base S2627'])
    chk('V12 veredito S27SF (R5)', V['base S27SF'] == 'Na estimativa mensal, cabe com o que você tem. Prazo por talhão não verificado: 7 de 7 atividades sem janela.', V['base S27SF'])
    chk('V8 veredito LG2627 (R2)', V['base LG2627'] == 'Falta recurso: Operadores e equipe precisam de 127 em nov/26 e você tem 8 (9 meses); Tratores, 10 em out/26 e você tem 4 (4 meses). Inclui 56 ocorrências ainda sem alocação. Fora da conta: 75 ocorrências antes do início da safra (01/09/2026).', V['base LG2627'])
    chk('V11 veredito S2526 (R1)', V['base S2526'] == 'Capacidade não calculada: as 21 ocorrências desta safra ficam fora do calendário do protótipo (set/26 – ago/27).', V['base S2526'])
    chk('V13 veredito Colhedoras = 0', V['Colhedoras 0'].startswith('Falta recurso: Colhedoras precisam de 1 em fev/27 e você tem 0. Inclui 3 ocorrências ainda sem alocação. Fora da conta: '), V['Colhedoras 0'])
    chk('V10/C9 veredito com SOJA-AT nos sem plano começa por Colhedoras', RES['SOJA-AT nos sem plano'][0]['ver']['txt'].startswith('Falta recurso: Colhedoras precisam de 2 em fev/27 e você tem 1.'), RES['SOJA-AT nos sem plano'][0]['ver']['txt'])
    chk('P2 veredito Operadores 8 → 5', 'Operadores e equipe precisam de 6 em mai/27 e você tem 5' in RES['Operadores 5'][0]['ver']['txt'], RES['Operadores 5'][0]['ver']['txt'])
    # S3.1 (revisão SAF, 06/10/2026) · ocorrência desta safra depois do fim (ou antes do início) conta no custo e não na capacidade.
    # d3 da S27SF com plantio em 20/05/2027: a colheita cai em ago/27, depois do fim (31/07/2027). Antes da correção, Colhedoras e
    # Operadores somavam ago/27 (19 h e 42,4 h) com o veredito dizendo "Fora da conta: 2 ocorrências depois do fim".
    _orig = copy.deepcopy(D2.CULTIVOS['S27SF'])
    try:
        for c_ in D2.CULTIVOS['S27SF']:
            if c_['id'] == 'd3': c_['plantio'] = '2027-05-20'
        j31, oc31 = job('S27SF', ver=True); r31 = js([j31])[0]; g31 = D2.capacidade('S27SF')
        cl31 = ver_in('S27SF', oc31, D2.RECURSOS)['cls']; ago = MI['ago/27']
        chk('S3.1 d3 em 20/05/2027: 2 ocorrências depois do fim, e nenhuma hora delas na capacidade de ago/27 (JS e Python)',
            cl31['depois'] == 2 and all(r31['G'][k]['cells'][ago]['dThis'] == 0 and g31[k]['cells'][ago]['dThis'] == 0 for k in r31['G']),
            (cl31, {k: (r31['G'][k]['cells'][ago]['dThis'], g31[k]['cells'][ago]['dThis']) for k in r31['G']}))
        chk('S3.1 veredito diz "Fora da conta: 2 ocorrências depois do fim da safra" e não cita ago/27', 'Fora da conta: 2 ocorrências depois do fim da safra' in r31['ver']['txt'] and 'ago/27' not in r31['ver']['txt'], r31['ver']['txt'])
        dif = [(k, i) for k in r31['G'] for i in range(12) if abs(r31['G'][k]['cells'][i]['d'] - g31[k]['cells'][i]['d']) > 1e-6 or r31['G'][k]['cells'][i]['red'] != g31[k]['cells'][i]['red']]
        chk('S3.1 paridade JS = Python com ocorrências depois do fim', not dif, dif[:4])
        casos = [('2027-01-31', 4, '2027-02-01', '2027-07-31'), ('2027-08-01', 11, '2027-02-01', '2027-07-31'), ('2025-10-01', -1, '2025-09-01', '2026-08-31'), ('2027-03-01', 6, '2027-02-01', '2027-07-31')]
        cj = js([dict(op='cls', v=[list(x) for x in casos])])[0]
        chk('S3.1 classe_oc (Python) = classeOc (tela): antes · depois · fora · cal', [D2.classe_oc(*x) for x in casos] == cj == ['antes', 'depois', 'fora', 'cal'], cj)
    finally:
        D2.CULTIVOS['S27SF'][:] = _orig
    # ================= SAF-C02 (Codex, 09/10/2026) · capacidade simétrica entre safras abertas =================
    # Regra: a elegibilidade de cada ocorrência na capacidade sai do período da safra de ORIGEM (classeOc), qualquer que seja a safra
    # aberta; a carga de outra safra que fica fora da conta aparece no veredito com número, motivo e horas (sem verde enganoso). Antes,
    # a ocorrência de outra safra entrava como estava: com o mesmo período, abrir A dava 340 h (R2) e abrir B, 140 h (R4).
    MF = [['2027-02', 'fev/27']]; DF = {'2027-02': 20}; RF = [dict(id='trator', nome='Tratores', un=1, jornada=8, turnos=1, disp=100, pes=False)]
    def ocf(i, h, dt, rec=None, mi=0):   # ocorrência da fixture do harness do Codex (nh = h = nq; janela 2000 h)
        return dict(id=i, mi=mi, dt=dt, a=dict(op='Teste', nome=i), rp=dict(itens=[dict(nh=h, h=h, nq=h, Hin=2000)], falta=dict(semHoras=0)), cfs=[dict(rec=rec or dict(trator=1))])
    def vista(sid, ocs, per, recs=RF, meses=MF, dias=DF, ver=True):
        """job com a safra sid aberta: as ocorrências dela com cls pelo período dela (o capCalc da tela); as outras com o período de cada uma"""
        oc = [dict(o, cls=D2.classe_oc(o['dt'], o['mi'], *per[sid])) for o in ocs[sid]]
        cl = dict(antes=0, fora=0, depois=0, cal=0)
        for o in oc: cl[o['cls']] += 1
        j = dict(op='cap', oc=oc, outras=[dict(id=x, nome=x, ini=per[x][0], fim=per[x][1], oc=ocs[x]) for x in ocs if x != sid], recursos=recs, meses=meses, dias=dias)
        if ver: j['ver'] = dict(semPlano=[], aPlano=100, cls=cl, ini=br(per[sid][0]), outras={x: x for x in ocs}, pend=0, semHoras=0, incompleto='', periodoCal=meses[0][1])
        return j
    def py_vista(j):
        f = getattr(D2, 'cap_saf', None)
        return f(j['oc'], j['outras'], j['recursos'], j['meses'], j['dias']) if f else None
    def par(rj, pg):
        if pg is None: return ['sem dados2.cap_saf']
        dif = []
        for k, x in rj['G'].items():
            for i_, (a, b) in enumerate(zip(x['cells'], pg[k]['cells'])):
                for f in ('d', 'dThis', 'dOth', 'nec'):
                    if abs((a[f] or 0) - (b[f] or 0)) > 1e-9: dif.append((k, i_, f, a[f], b[f]))
                if a['red'] != b['red']: dif.append((k, i_, 'red'))
            if x['fo'] != [[f['sid'], f['cls'], f['mi'], f['h'], f['n']] for f in pg[k].get('fora', [])]: dif.append((k, 'fora', x['fo'], pg[k].get('fora')))
        return dif
    OCS = dict(A=[ocf('A1', 100, '2027-02-10')], B=[ocf('B1', 40, '2027-02-10'), ocf('B2', 200, '2027-02-28')])
    PER = dict(A=('2027-02-01', '2027-02-15'), B=('2027-02-01', '2027-02-15'))
    PER_CTL = dict(A=('2027-02-01', '2027-02-28'), B=('2027-02-01', '2027-02-28'))   # controle: B2 dentro do período das duas
    OCS3 = dict(A=[ocf('A1', 100, '2027-02-10'), ocf('A2', 50, '2027-02-20')], B=[ocf('B1', 40, '2027-02-10'), ocf('B2', 200, '2027-02-28')])
    PER3 = dict(A=('2027-02-11', '2027-02-28'), B=('2027-02-11', '2027-02-28'))       # antes do início: A1 e B1 fora nas duas vistas
    JF = [vista('A', OCS, PER), vista('B', OCS, PER), vista('A', OCS, PER_CTL), vista('B', OCS, PER_CTL), vista('A', OCS3, PER3), vista('B', OCS3, PER3)]
    RFX = js(JF); PFX = [py_vista(j) for j in JF]
    ca, cb = RFX[0]['G']['trator']['cells'][0], RFX[1]['G']['trator']['cells'][0]
    chk('SAF-C02 A↔B com o mesmo período (01 a 15/02/2027): 140 h nas duas vistas (A1 100 + B1 40), cabe com 1; era 340 h com a A aberta',
        near(ca['d'], 140) and near(cb['d'], 140) and (ca['dThis'], ca['dOth'], cb['dThis'], cb['dOth']) == (100, 40, 40, 100) and ca['nec'] == cb['nec'] == 1 and not ca['red'] and not cb['red'], (ca, cb))
    va, vb = RFX[0]['ver'], RFX[1]['ver']
    chk('SAF-C02 vista A: a B2 (200 h) fica fora da conta com número, motivo e horas; amarelo (R4), nunca verde',
        va['R'] == 'R4' and va['txt'] == 'Na estimativa mensal, cabe nos 100 ha com plano. Fora da conta: 1 ocorrência da B depois do fim dela (Tratores 200,0 h).', va)
    chk('SAF-C02 vista B: a B2 fora da conta como "depois do fim da safra" (R4), sem citar a A',
        vb['R'] == 'R4' and vb['txt'] == 'Na estimativa mensal, cabe nos 100 ha com plano. Fora da conta: 1 ocorrência depois do fim da safra.', vb)
    chk('SAF-C02 capSaf guarda a carga excluída da outra safra (B2: depois do fim, fev/27, 200 h)', [f[:4] for f in RFX[0]['G']['trator']['fo']] == [['B', 'depois', 0, 200]], RFX[0]['G']['trator']['fo'])
    c1, c2 = RFX[2]['G']['trator']['cells'][0], RFX[3]['G']['trator']['cells'][0]
    chk('SAF-C02 controle (B2 dentro do período, 01 a 28/02/2027): 340 h nas duas vistas, precisa de 3, tem 1',
        near(c1['d'], 340) and near(c2['d'], 340) and c1['nec'] == c2['nec'] == 3 and c1['red'] and c2['red'] and not RFX[2]['G']['trator']['fo'] and not RFX[3]['G']['trator']['fo'], (c1, c2))
    chk('SAF-C02 controle: R2 nas duas; a A soma a B (240,0 h), a B falta sozinha',
        RFX[2]['ver']['txt'] == 'Falta recurso: Tratores precisam de 3 em fev/27 e você tem 1, somando a B (240,0 h).' and RFX[3]['ver']['txt'] == 'Falta recurso: Tratores precisam de 3 em fev/27 e você tem 1.', (RFX[2]['ver'], RFX[3]['ver']))
    c1, c2 = RFX[4]['G']['trator']['cells'][0], RFX[5]['G']['trator']['cells'][0]
    chk('SAF-C02 antes do início (11 a 28/02/2027 nas duas): 250 h nas duas vistas (A2 50 + B2 200); A1 e B1 fora',
        near(c1['d'], 250) and near(c2['d'], 250) and (c1['dThis'], c2['dThis']) == (50, 200), (c1, c2))
    chk('SAF-C02 antes do início: cada vista cita a própria e a da outra com o motivo "antes do início dela"',
        RFX[4]['ver']['txt'] == 'Falta recurso: Tratores precisam de 2 em fev/27 e você tem 1, somando a B (200,0 h). Fora da conta: 1 ocorrência antes do início da safra (11/02/2027); 1 ocorrência da B antes do início dela (Tratores 40,0 h).'
        and RFX[5]['ver']['txt'] == 'Falta recurso: Tratores precisam de 2 em fev/27 e você tem 1. Fora da conta: 1 ocorrência antes do início da safra (11/02/2027); 1 ocorrência da A antes do início dela (Tratores 100,0 h).',
        (RFX[4]['ver']['txt'], RFX[5]['ver']['txt']))
    dif = [(n, par(r, g)) for n, r, g in zip(('A', 'B', 'A ctl', 'B ctl', 'A antes', 'B antes'), RFX, PFX) if par(r, g)]
    chk('SAF-C02 paridade JS = Python (dados2.cap_saf) nas 6 vistas da fixture, com a carga excluída', not dif, dif[:3])
    _saf0 = list(D2.SAFRAS)
    try:
        D2.SAFRAS.extend([dict(id='XA', nome='Teste A', ini='2027-02-01', fim='2027-02-15', fazenda='Santa Rita', ro=False),
                          dict(id='XF', nome='Teste F', ini='2027-02-01', fim='2027-02-15', fazenda='Boa Vista', ro=False),
                          dict(id='XE', nome='Teste E', ini='2027-02-01', fim='2027-02-15', fazenda='Santa Rita', ro=True)])
        o1, o2, o3 = D2.outras_safras('S2627'), D2.outras_safras('XE'), D2.outras_safras('XF')
        chk('SAF-C02 outras safras: só abertas e da mesma fazenda (S27SF, XA); outra fazenda (XF, LG2627) e encerrada (XE, S2526) fora; com a encerrada aberta na tela, nada soma',
            o1 == ['S27SF', 'XA'] and o2 == [] and o3 == [], (o1, o2, o3))
    finally:
        D2.SAFRAS[:] = _saf0
    # cenário real, o mesmo do teste de navegador (saf_capacidade_simetrica_test.py): S2627 e S27SF com o MESMO período, 01/09/2026 a
    # 12/07/2027. A colheita da Safrinha em 14 e 15/07 (P1 e T2) cai depois do fim; em jul/27 a S2627 tem a poda do C1 (04/07)
    _per = {s: (SAF[s]['ini'], SAF[s]['fim']) for s in ('S2627', 'S27SF')}; cop0 = D2.plano_op('S27SF')['cop']
    try:
        for s in ('S2627', 'S27SF'): SAF[s]['ini'], SAF[s]['fim'] = '2026-09-01', '2027-07-12'
        jA, ocA = job('S2627', ver=True); jB, ocB = job('S27SF', ver=True); rA, rB = js([jA, jB]); gA, gB = D2.capacidade('S2627'), D2.capacidade('S27SF')
        jul = MI['jul/27']
        dj = {k: (rA['G'][k]['cells'][jul]['d'], rB['G'][k]['cells'][jul]['d'], gA[k]['cells'][jul]['d'], gB[k]['cells'][jul]['d']) for k in ('trator', 'oper', 'colh')}
        chk('SAF-C02 real: jul/27 Tratores 61,7 h nas duas vistas e no espelho (poda 25,3 + dessecação 4,4 + colheita T1-A 32,0); era 140,3 h com a S2627 aberta',
            all(near(x, 61.7, .06) for x in dj['trator']), dj)
        tudo = [(k, i) for k in rA['G'] for i in range(12) if len({round(x, 9) for x in (rA['G'][k]['cells'][i]['d'], rB['G'][k]['cells'][i]['d'], gA[k]['cells'][i]['d'], gB[k]['cells'][i]['d'])}) > 1]
        chk('SAF-C02 real: demanda de todo recurso × mês igual nas duas vistas (JS e Python)', not tudo, tudo[:6])
        chk('SAF-C02 real: veredito da S2627 identifica a colheita da Safrinha fora da conta (número, motivo e horas dos recursos que a S2627 usa em jul/27)',
            '2 ocorrências da Safrinha 2027 depois do fim dela (Tratores 78,6 h e Operadores e equipe 157,2 h)' in rA['ver']['txt'] and rA['ver']['R'] != 'R5', rA['ver'])
        chk('SAF-C02 real: veredito da S27SF diz "2 ocorrências depois do fim da safra" e não cita a S2627 (nada dela fora em jul/27)',
            'Fora da conta: 2 ocorrências depois do fim da safra' in rB['ver']['txt'] and 'Safra 2026/27' not in rB['ver']['txt'], rB['ver'])
        dep = [o for o in ocB if D2.classe_oc(o['dt'], o['mi'], '2026-09-01', '2027-07-12') == 'depois']
        cop1 = D2.plano_op('S27SF')['cop']
        chk('SAF-C02 real: custo preservado — o custo de operação da S27SF não muda com o período e inclui as 2 colheitas fora da conta',
            near(cop1, cop0, .001) and len(dep) == 2 and all((o['cop'] or 0) > 0 for o in dep) and near(sum(o['cop'] or 0 for o in ocB), cop1, .01), (cop0, cop1, [(o['c']['local'], str(o['dt']), o['cop']) for o in dep]))
        dif = [(n, k) for n, r, g in (('S2627', rA, gA), ('S27SF', rB, gB)) for k in r['G'] if r['G'][k]['fo'] != [[f['sid'], f['cls'], f['mi'], f['h'], f['n']] for f in g[k].get('fora', [])]]
        chk('SAF-C02 real: paridade JS = Python da carga fora da conta (g.fora, desta safra e das outras)', not dif, dif[:4])
    finally:
        for s in ('S2627', 'S27SF'): SAF[s]['ini'], SAF[s]['fim'] = _per[s]
    # S3.1 com a S2627 aberta: a colheita da Safrinha depois do fim dela (d3 em 20/05/2027 → ago/27) não entra mais em ago/27 da S2627
    # (antes entrava: 19 h de Colhedoras e 42,4 h de Operadores); a S2627 não tem demanda em ago/27, então o veredito não muda (V1)
    _orig = copy.deepcopy(D2.CULTIVOS['S27SF'])
    try:
        for c_ in D2.CULTIVOS['S27SF']:
            if c_['id'] == 'd3': c_['plantio'] = '2027-05-20'
        jx, _ = job('S2627', ver=True); rx = js([jx])[0]; gx = D2.capacidade('S2627'); ago = MI['ago/27']
        chk('SAF-C02 S3.1 com a S2627 aberta: nenhuma hora da Safrinha depois do fim dela em ago/27 (JS e Python); veredito igual ao V1',
            all(rx['G'][k]['cells'][ago]['dOth'] == 0 and gx[k]['cells'][ago]['dOth'] == 0 for k in rx['G']) and rx['ver']['txt'] == V['base S2627'],
            ({k: (rx['G'][k]['cells'][ago]['dOth'], gx[k]['cells'][ago]['dOth']) for k in rx['G']}, rx['ver']['txt']))
    finally:
        D2.CULTIVOS['S27SF'][:] = _orig
    # propriedade: 150 sorteios de 2 ou 3 safras abertas da mesma fazenda (períodos e ocorrências ao acaso, inclusive fora do calendário):
    # a demanda de cada recurso × mês é a mesma com qualquer safra aberta, igual à soma das ocorrências elegíveis pela safra de origem
    # (oráculo independente), e JS = Python
    random.seed(20261009)
    MP = [['2027-01', 'jan/27'], ['2027-02', 'fev/27'], ['2027-03', 'mar/27']]; DP = {'2027-01': 21, '2027-02': 19, '2027-03': 22}
    RP = [dict(id='trator', nome='Tratores', un=2, jornada=8, turnos=1, disp=90, pes=False), dict(id='oper', nome='Operadores', un=3, jornada=8, abs=10, pes=True)]
    D0 = datetime.date(2026, 12, 15)
    def mi_de(dt): return next((i for i, (m, _) in enumerate(MP) if m == dt[:7]), -1)
    JP, CASOS = [], []
    for _k in range(150):
        ids = ['A', 'B', 'C'][:random.choice([2, 3])]; per = {}; ocs = {}
        for x in ids:
            a, b = sorted(random.sample(range(120), 2)); per[x] = ((D0 + datetime.timedelta(a)).isoformat(), (D0 + datetime.timedelta(b)).isoformat())
            ocs[x] = []
            for n in range(random.randint(1, 4)):
                dt = (D0 + datetime.timedelta(random.randrange(0, 120))).isoformat()
                ocs[x].append(ocf(x + str(n), random.choice([5, 12.5, 40, 80, 200]), dt, random.choice([dict(trator=1), dict(oper=2), dict(trator=1, oper=1)]), mi_de(dt)))
        CASOS.append((ids, per, ocs))
        for x in ids: JP.append(vista(x, ocs, per, RP, MP, DP, ver=False))
    RPX = js(JP); bad = []; i_ = 0; nviews = 0
    for ids, per, ocs in CASOS:
        orac = {}
        for x in ids:
            for o in ocs[x]:
                if o['mi'] < 0 or D2.classe_oc(o['dt'], o['mi'], *per[x]) != 'cal': continue
                for c_ in D2.carga_itens(o): orac[(c_['k'], o['mi'])] = orac.get((c_['k'], o['mi']), 0) + c_['h']
        for x in ids:
            r = RPX[i_]; pg = py_vista(JP[i_]); i_ += 1; nviews += 1
            for kk in ('trator', 'oper'):
                for mi in range(3):
                    dj = r['G'][kk]['cells'][mi]['d']; dp = pg[kk]['cells'][mi]['d'] if pg else None
                    if abs(dj - orac.get((kk, mi), 0)) > 1e-9 or dp is None or abs(dp - dj) > 1e-9: bad.append((x, kk, mi, dj, dp, orac.get((kk, mi), 0)))
    chk('SAF-C02 propriedade: 150 sorteios (%d vistas) — demanda igual com qualquer safra aberta, = Σ elegíveis pela origem, JS = Python' % nviews, not bad, (len(bad), bad[:4]))
    # C11 · 200 combinações sorteadas de unidades, jornada, turnos, disponibilidade e absenteísmo (e sobrescrita de configuração), JS = Python
    random.seed(20261005); J2 = []; P2 = []
    for k in range(200):
        mod = {}
        for r in D2.RECURSOS:
            if random.random() < 0.5:
                base = dict(un=random.choice([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]) if r['id'] == 'oper' else random.choice([0, 1, 2, 3, 4, 5]), jornada=random.choice([8, 9, 10, 12]))
                if r['id'] == 'oper': base['abs'] = random.choice([0, 5, 10, 30])
                else: base.update(turnos=random.choice([1, 2]), disp=random.choice([80, 90, 95, 100]))
                mod[r['id']] = base
        cfg = None
        if random.random() < 0.3:
            op, atv, cid = random.choice([('Adubação a lanço', 'Adubação de cobertura', 'r3'), ('Plantio', 'Plantio e adubação de base', 'r2'), ('Pulverização', '*', 'r1')])
            cfg = {(op, atv, cid): random.choice([dict(larg=random.choice([12, 18, 30])), dict(vel=random.choice([5, 9, 12])), dict(efic=random.choice([60, 90])), dict(pess=random.choice([1, 2, 3])), dict(maq=random.choice([100, 250]))])}
        safra = random.choice(['S2627', 'S27SF', 'LG2627'])
        j, oc = job(safra, recs(**mod), None, cfg); J2.append(j); P2.append((safra, recs(**mod), cfg))
    R2 = js(J2); dif = []
    for (safra, rs, cfg), r in zip(P2, R2):
        g = D2.capacidade(safra, rs, None, cfg)
        for k, x in r['G'].items():
            for i, a in enumerate(x['cells']):
                b = g[k]['cells'][i]
                if abs(a['d'] - b['d']) > 1e-6 or a['nec'] != b['nec'] or a['red'] != b['red'] or (a['ocup'] is None) != (b['ocup'] is None) or (a['ocup'] is not None and abs(a['ocup'] - b['ocup']) > 1e-6): dif.append((safra, k, i)); break
            if x['txt'] != D2.fmt_ocup(g[k]['max']['ocup'] if g[k]['max'] else 0) and x['max'] is not None: dif.append((safra, k, 'txt', x['txt']))
    chk('C11 paridade JS = Python em 200 combinações (unidades, jornada, turnos, disponibilidade, absenteísmo e cfg_override)', not dif, dif[:5])
    print('\nRESULTADO: %d OK · %d FALHA' % (len(OK), len(FAIL)))
    sys.exit(1 if FAIL else 0)
