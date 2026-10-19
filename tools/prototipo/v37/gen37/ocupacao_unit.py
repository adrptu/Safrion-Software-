# -*- coding: utf-8 -*-
"""Teste de unidade do serviço de ocupação (Planejar safra, etapa 2 · ESPECIFICACAO.md §7.1, OC-U1 a OC-U9), sem navegador.
Roda a MESMA função da tela (ocupacao.js no node) e o espelho ocupacao.py sobre os mesmos dados e confere: JS = Python em tudo (OC-U6) e os
números da especificação (períodos §6.1, faixas §3.4, chips, trava/pendência/mensagens §7.3), com folga 1 e folga 0. As lavouras em campo
e4/e5 vêm de dados2 (S2526, origem 'lavoura em campo'); se a base ainda não as tiver, entram como fixture sintética.
Uso: python3 ocupacao_unit.py [n_sequencias]   (propriedades OC-U5: padrão 400 sequências de 3 salvamentos, semente 20261005)"""
import sys, os, json, copy, random, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import dados2 as D2
import ocupacao as OC, ocupacao_cen as CEN

OK, FAIL = [], []
def chk(nome, cond, det=''):
    (OK if cond else FAIL).append(nome); print(('OK    · ' if cond else 'FALHA · ') + nome + ('' if cond else ' · ' + str(det)[:900]), flush=True)

E45 = [dict(id='e4', fazenda='Santa Rita', local='P1', tipo='Talhão inteiro', cultura='Feijão', variedade='BRS Estilo', area=95, plantio='2026-07-05',
            meta=48, un_meta='sc/ha', plano=None, colheita='2026-10-10', ro=True, origem='lavoura em campo'),
       dict(id='e5', fazenda='Santa Rita', local='P2', tipo='Talhão inteiro', cultura='Milho', variedade='Híbrido AG 8700', area=80, plantio='2026-08-10',
            meta=180, un_meta='sc/ha', plano=None, colheita='2026-11-15', ro=True, origem='lavoura em campo')]
def fonte(com_e45=True):
    f = copy.deepcopy(D2.CULTIVOS)
    tem = [c['id'] for c in f.get('S2526', [])]
    if com_e45 and 'e4' not in tem: f['S2526'] = f['S2526'] + copy.deepcopy(E45)
    if not com_e45: f['S2526'] = [c for c in f['S2526'] if c['id'] not in ('e4', 'e5')]
    return f
CULT = CEN.CULTURAS; CVS = CEN.cultivares(); TAL = CEN.talhoes()
def ctxa(folga=1): return dict(culturas=CULT, cultivares=[list(x) for x in CVS], planos=D2.PLANOS, folga=folga)
def NV(id_, nome, ini, fim, faz='Santa Rita'): return dict(id=id_, nome=nome, ini=ini, fim=fim, faz=faz, ro=False)
NOVAS = {'caso5': NV('N5', 'Nova (caso 5)', '2027-01-10', '2027-08-30'), '2027/28': NV('N28', 'Nova 2027/28', '2027-09-01', '2028-08-31'),
         'BoaVista': NV('NBV', 'Nova Boa Vista', '2026-09-01', '2027-08-31', 'Boa Vista'),
         'LG2728': NV('NLG28', 'Nova Lagoa 2027/28', '2027-09-01', '2028-08-31', 'Lagoa Grande'),
         'LG2627b': NV('NLG27', 'Nova Lagoa 2026/27', '2026-09-01', '2027-08-31', 'Lagoa Grande')}

# ---------- JS (node) ----------
JS_RUN = r"""
const fs=require('fs'); eval(fs.readFileSync(require('path').join(require('path').dirname(process.argv[1]),'datas_atividade.js'),'utf8')+'\n'+fs.readFileSync(process.argv[1],'utf8')+'\n;globalThis.OCX={ocCtx,ocOcupacoes,ocTabela,ocChips,ocFaixaTxt,ocChecar,ocPlantioMin,ocMsgTrava,ocMsgPend,ocMsgAviso,ocMsgSemJanela,ocPendCurta,ocP,ocLib,ocDia,ocBr,ocIso};');
const X=globalThis.OCX; const jobs=JSON.parse(fs.readFileSync(0,'utf8')); const out=[];
const ser=(o,ctx)=>({id:o.id,ciclo:o.ciclo,saf:o.saf,safs:o.safs,t:o.t,faixa:o.faixa,ini:o.ini,plantio:o.plantio,fim:o.fim,classe:o.classe,nuc:o.nuc,P:X.ocP(ctx,o),avisos:o.avisos});
for(const j of jobs){ const ctx=X.ocCtx(j.ctx.culturas,j.ctx.cultivares,j.ctx.planos,j.ctx.folga);
  if(j.op==='occ'){ out.push(X.ocOcupacoes(ctx,j.safras,j.cults).map(o=>ser(o,ctx))); continue; }
  if(j.op==='tab'){ const occ=X.ocOcupacoes(ctx,j.safras,j.cults); const [L,b]=X.ocTabela(ctx,j.safra,occ,j.talhoes,j.safras);
    out.push({band:b,faixa:X.ocFaixaTxt(b,L,j.tot),chips:X.ocChips(L),linhas:L.map(v=>({t:v.t,sit:v.sit,A:v.A,livre:v.livre,conf:v.conf,area_livre:v.area_livre,desde:v.desde,est:v.est,
      own:v.own.map(o=>o.id),vis:v.vis.map(o=>o.id),seq:v.seq,linhas:v.linhas,vinc:v.vinc,planejar:v.planejar,trav:v.trav,pend:v.pend,exc:v.exc||0}))}); continue; }
  if(j.op==='chk'){ const r=X.ocChecar(ctx,j.safras,j.antes,j.depois,j.sid,j.alvo,j.T);
    const o={trav:r.trav,pend:r.pend,aviso:r.aviso.map(y=>y.id),ini:r.o?r.o.ini:null,fim:r.o?r.o.fim:null,classe:r.o?r.o.classe:null};
    if(r.o){ o.mt=r.trav.length?X.ocMsgTrava(ctx,r,j.sid,j.T,j.pmin===undefined?null:j.pmin):''; o.mp=X.ocMsgPend(ctx,r,j.sid,j.pmin===undefined?null:j.pmin); o.ma=X.ocMsgAviso(ctx,r); }
    out.push(o); continue; }
  if(j.op==='pmin'){ out.push(X.ocPlantioMin(ctx,j.safras,j.cults,j.sid,j.novo,j.desde,j.T,j.ate===undefined?null:j.ate)); continue; }
  if(j.op==='p3'){ const occ=X.ocOcupacoes(ctx,j.safras,j.cults); const o=occ.find(x=>x.id===j.alvo), sg=occ.find(x=>x.id===j.seg); out.push(X.ocMsgSemJanela(ctx,o,sg,j.base,j.sid,j.livre)); continue; }
  out.push(null); }
process.stdout.write(JSON.stringify(out));
"""
def js(jobs):
    p = subprocess.run(['node', '-e', JS_RUN, os.path.join(HERE, 'ocupacao.js')], input=json.dumps(jobs), capture_output=True, text=True, timeout=600)
    if p.returncode: raise SystemExit('node falhou: ' + p.stderr[-2000:])
    return json.loads(p.stdout)

# ---------- Python (mesmo formato) ----------
def lst(x): return json.loads(json.dumps(x))   # tuplas → listas (mesma forma do JS)
def py(jobs):
    out = []
    for j in jobs:
        c = j['ctx']; ctx = OC.ctx_de(c['culturas'], c['cultivares'], c['planos'], c['folga'])
        if j['op'] == 'occ':
            out.append([dict(id=o['id'], ciclo=o['ciclo'], saf=o['saf'], safs=o['safs'], t=o['t'], faixa=o['faixa'], ini=o['ini'], plantio=o['plantio'], fim=o['fim'],
                             classe=o['classe'], nuc=o['nuc'], P=OC.P(ctx, o), avisos=lst(o['avisos'])) for o in OC.ocupacoes(ctx, j['safras'], j['cults'])]); continue
        if j['op'] == 'tab':
            occ = OC.ocupacoes(ctx, j['safras'], j['cults']); L, b = OC.tabela(ctx, j['safra'], occ, j['talhoes'], j['safras'])
            out.append(dict(band=b, faixa=OC.faixa_txt(b, L, j['tot']), chips=OC.chips(L), linhas=[dict(t=v['t'], sit=v['sit'], A=v['A'], livre=v['livre'], conf=v['conf'],
                area_livre=v['area_livre'], desde=v['desde'], est=v['est'], own=[o['id'] for o in v['own']], vis=[o['id'] for o in v['vis']], seq=lst(v['seq']), linhas=v['linhas'],
                vinc=v['vinc'], planejar=v['planejar'], trav=lst(v['trav']), pend=lst(v['pend']), exc=v.get('exc', 0)) for v in L])); continue
        if j['op'] == 'chk':
            r = OC.checa(ctx, j['safras'], j['antes'], j['depois'], j['sid'], j['alvo'], j['T'])
            o = dict(trav=lst(r['trav']), pend=lst(r['pend']), aviso=[y['id'] for y in r['aviso']], ini=r['o']['ini'] if r['o'] else None,
                     fim=r['o']['fim'] if r['o'] else None, classe=r['o']['classe'] if r['o'] else None)
            if r['o']:
                pm = j.get('pmin')
                o['mt'] = OC.msg_trava(ctx, r, j['sid'], j['T'], None, pm) if r['trav'] else ''
                o['mp'] = OC.msg_pend(ctx, r, j['sid'], pm); o['ma'] = OC.msg_aviso(ctx, r)
            out.append(o); continue
        if j['op'] == 'pmin':
            out.append(OC.plantio_min(ctx, j['safras'], j['cults'], j['sid'], j['novo'], j['desde'], j['T'], j.get('ate'))); continue
        if j['op'] == 'p3':
            occ = OC.ocupacoes(ctx, j['safras'], j['cults']); o = next(x for x in occ if x['id'] == j['alvo']); sg = next(x for x in occ if x['id'] == j['seg'])
            try: out.append(OC.msg_sem_janela(ctx, o, sg, j['base'], j['sid'], *([j['livre']] if j.get('livre') else [])))
            except TypeError: out.append(OC.msg_sem_janela(ctx, o, sg, j['base'], j['sid']))   # serviço anterior, sem o nome sugerido
            continue
        out.append(None)
    return out

def canon(x):
    if isinstance(x, float) and x == int(x): return int(x)
    if isinstance(x, list): return [canon(y) for y in x]
    if isinstance(x, dict): return {k: canon(v) for k, v in x.items()}
    return x
def roda(jobs, nome):
    a, b = canon(js(jobs)), canon(py(jobs))
    dif = [i for i, (x, y) in enumerate(zip(a, b)) if json.dumps(x, sort_keys=True) != json.dumps(y, sort_keys=True)]
    chk('OC-U6 paridade JS = Python · %s (%d casos)' % (nome, len(jobs)), not dif and len(a) == len(b),
        [(i, json.dumps(a[i], sort_keys=True)[:400], json.dumps(b[i], sort_keys=True)[:400]) for i in dif[:2]])
    return a

D = OC.dia; BR = OC.br
def safras_com(*novas): return CEN.safras(novas)
def tab_job(safra, cults, safs, folga=1):
    tal = TAL[safra['faz']]
    return dict(op='tab', ctx=ctxa(folga), safra=safra, safras=safs, cults=cults, talhoes=[list(x) for x in tal], tot=sum(a for _, a in tal))
def N(**k):
    base = dict(id='nv', saf='S27SF', faz='Santa Rita', tipo='Parcela', cult='Milho', var='Híbrido AG 8700', plano='MILHO-SF', colheita=None, colheita_real=None, ciclo=None, origem='')
    base.update(k)
    if 'talhao' not in base: base['talhao'] = CEN.tal_de(base['faixa'], base['tipo'])
    return base
def T_(t, faz='Santa Rita'): return dict(TAL[faz])[t]
def muda(cults, cid, **k):
    out = copy.deepcopy(cults)
    for c in out:
        if c['id'] == cid: c.update(k)
    return out
def chk_job(cults, sid, alvo_novo=None, mud=None, folga=1, safs=None, pmin=None):
    safs = safs or safras_com()
    if alvo_novo: depois = cults + [alvo_novo]; alvo = alvo_novo['id']; t = alvo_novo['talhao']
    else: depois = muda(cults, mud[0], **mud[1]); alvo = mud[0]; t = next(c['talhao'] for c in cults if c['id'] == alvo)
    faz = (alvo_novo or next(c for c in cults if c['id'] == alvo))['faz']
    j = dict(op='chk', ctx=ctxa(folga), safras=safs, antes=cults, depois=depois, sid=sid, alvo=alvo, T=T_(t, faz))
    if pmin is not None: j['pmin'] = pmin
    return j

if __name__ == '__main__':
    NSEQ = int(sys.argv[1]) if len(sys.argv) > 1 else 400
    CU = CEN.cultivos(fonte(True)); CU0 = CEN.cultivos(fonte(False))
    S = safras_com()
    # ---------- OC-U1 · períodos (§6.1) ----------
    occ = roda([dict(op='occ', ctx=ctxa(1), safras=S, cults=CU)], 'períodos')[0]
    by = {o['id']: o for o in occ}
    ESP = {'c1': ('25/09/2026', '10/02/2027', 'plano', '03/02/2027', '10/02/2027'), 'c2': ('05/10/2026', '20/02/2027', 'plano', '13/02/2027', '20/02/2027'),
           'c3': ('28/09/2026', '13/02/2027', 'plano', '06/02/2027', '13/02/2027'), 'c4': ('20/10/2026', '15/02/2027', 'estimado', '08/02/2027', '31/08/2027'),
           'c5': ('22/10/2026', '17/02/2027', 'estimado', '10/02/2027', '31/08/2027'), 'c6': ('10/11/2026', '08/03/2027', 'estimado', '01/03/2027', '31/08/2027'),
           'c7': ('25/11/2026', '23/03/2027', 'estimado', '16/03/2027', '31/08/2027'), 'c8': ('10/03/2025', 'sem fim', 'perene', 'sem fim', 'sem fim'),
           'c9': ('15/01/2019', 'sem fim', 'perene', 'sem fim', 'sem fim'), 'd1': ('20/02/2027', '10/07/2027', 'plano', '09/07/2027', '10/07/2027'),
           'd2': ('25/02/2027', '15/07/2027', 'plano', '14/07/2027', '15/07/2027'), 'd3': ('15/04/2027', '14/07/2027', 'plano', '13/07/2027', '14/07/2027'),
           'e4': ('05/07/2026', '10/10/2026', 'informada', '02/10/2026', '10/10/2026'), 'e5': ('10/08/2026', '15/11/2026', 'informada', '15/11/2026', '15/11/2026')}
    got = {k: (BR(by[k]['ini']), BR(by[k]['fim']), by[k]['classe'], BR(by[k]['nuc']), BR(by[k]['P'])) for k in ESP}
    chk('OC-U1 períodos dos cultivos da Santa Rita (§6.1)', got == ESP, {k: got[k] for k in ESP if got[k] != ESP[k]})
    chk('OC-U1 R-05: T7 e C1 "sem fim" (colheitaDe não serve como fim)', by['c8']['fim'] >= OC.INF and by['c9']['fim'] >= OC.INF)
    # ---------- OC-U2/U3/U9 · faixas e chips (§3.4, §6.1) ----------
    TABS = [('S2627', S['S2627'], S), ('S27SF', S['S27SF'], S), ('caso 5', NOVAS['caso5'], safras_com(NOVAS['caso5'])), ('2027/28', NOVAS['2027/28'], safras_com(NOVAS['2027/28'])),
            ('LG2627', S['LG2627'], S), ('Boa Vista nova', NOVAS['BoaVista'], safras_com(NOVAS['BoaVista'])), ('Lagoa nova 2027/28', NOVAS['LG2728'], safras_com(NOVAS['LG2728'])),
            ('Lagoa nova 2026/27', NOVAS['LG2627b'], safras_com(NOVAS['LG2627b']))]
    FX = {'S2627': 'Nesta safra 1.165 · de 1.165 ha · 1 sucessão a conferir', 'S27SF': 'Nesta safra 553 · Livre 152 · A conferir 380 · Perene 80 · de 1.165 ha · 1 sucessão a conferir',
          'caso 5': 'Nesta safra 0 · Livre 450 · A conferir 475 · Perene 80 · Ocupado 160 · de 1.165 ha', '2027/28': 'Nesta safra 0 · Livre 1.085 · Perene 80 · de 1.165 ha',
          'LG2627': 'Nesta safra 1.285,23 · de 1.285,23 ha', 'Boa Vista nova': 'Nesta safra 0 · Livre 120 · de 120 ha',
          'Lagoa nova 2027/28': 'Nesta safra 0 · Perene 1.285,23 · de 1.285,23 ha', 'Lagoa nova 2026/27': 'Nesta safra 0 · Perene 1.285,23 · de 1.285,23 ha'}
    CH = {'S2627': {'Planejado': 7, 'A conferir': 1}, 'S27SF': {'A conferir': 4, 'Perene': 2, 'Livre': 1, 'Planejado': 1}, 'caso 5': {'A conferir': 4, 'Livre': 2, 'Perene': 2},
          '2027/28': {'Livre': 6, 'Perene': 2}, 'Boa Vista nova': {'Livre': 1}, 'LG2627': {'Planejado': 23}, 'Lagoa nova 2027/28': {'Perene': 23}, 'Lagoa nova 2026/27': {'Perene': 23}}
    LIN = {'S2627': 18, 'S27SF': 15, 'caso 5': 15, '2027/28': 8}
    for f in (1, 0):
        res = roda([tab_job(s, CU, ss, f) for _, s, ss in TABS], 'tabelas folga %d' % f)
        for (nome, s, ss), r in zip(TABS, res):
            if f == 1:
                chk('OC-U2 faixa %s (§3.4)' % nome, r['faixa'] == FX[nome], r['faixa'])
                chk('OC-U3 chips %s pelo nível 0 (soma = Todas)' % nome, r['chips'] == CH[nome] and sum(r['chips'].values()) == len(r['linhas']), r['chips'])
                if nome in LIN: chk('§3.2 linhas com grupos abertos %s = %d' % (nome, LIN[nome]), sum(v['linhas'] for v in r['linhas']) == LIN[nome], sum(v['linhas'] for v in r['linhas']))
            tot = sum(a for _, a in TAL[s['faz']])
            chk('OC-U2 faixa soma T (%s, folga %d)' % (nome, f), abs(sum(r['band'].values()) - tot) < 0.011, r['band'])
        if f == 1:
            L = {v['t']: v for v in res[1]['linhas']}
            sd = {t: (L[t]['sit'], OC.ha(L[t]['area_livre']), BR(L[t]['desde']) if L[t]['area_livre'] > 0.005 else '—') for t in L}
            chk('§6.1 S27SF Situação e Livre a partir de', sd == {'T1': ('Livre', '152', '21/02/2027'), 'T2': ('Planejado', '0', '—'), 'T3': ('A conferir', '96', '18/02/2027'),
                'T4': ('A conferir', '204', '16/02/2027'), 'P1': ('A conferir', '0', '—'), 'P2': ('A conferir', '80', '24/03/2027'), 'T7': ('Perene', '0', '—'), 'C1': ('Perene', '0', '—')}, sd)
            chk('§6.1 S27SF "est." em T3, T4 e P2', [t for t in L if L[t]['est']] == ['T3', 'T4', 'P2'], [t for t in L if L[t]['est']])
            chk('R-12 S27SF filhas de fora visíveis', {t: L[t]['vis'] for t in L} == {'T1': ['c1', 'c2'], 'T2': ['c3'], 'T3': ['c5'], 'T4': ['c4'], 'P1': ['c6'], 'P2': ['c7'], 'T7': ['c8'], 'C1': ['c9']},
                {t: L[t]['vis'] for t in L})
            L0 = {v['t']: v for v in res[0]['linhas']}
            chk('R-12 S2627 filhas de fora visíveis (d1, d2, d3+e4, e5)', {t: L0[t]['vis'] for t in ('T1', 'T2', 'P1', 'P2')} == {'T1': ['d1'], 'T2': ['d2'], 'P1': ['e4', 'd3'], 'P2': ['e5']},
                {t: L0[t]['vis'] for t in L0})
            L3 = {v['t']: v for v in res[3]['linhas']}
            chk('R-24 2027/28: Vincular ciclo em T7 e C1, sem Planejar', L3['T7']['vinc'] == ['c8'] and L3['C1']['vinc'] == ['c9'] and not L3['T7']['planejar'], (L3['T7'], L3['C1']))
            L2 = {v['t']: v for v in res[2]['linhas']}
            chk('R-24 caso 5 (a S2627 cruza): T7 e C1 sem Vincular nem Planejar', not L2['T7']['vinc'] and not L2['C1']['vinc'] and not L2['T7']['planejar'])
            chk('R-25 Lagoa nova 2026/27: 23 pivôs Perene sem ação', all(v['sit'] == 'Perene' and not v['vinc'] and not v['planejar'] for v in res[7]['linhas']))
            chk('R-24 Lagoa nova 2027/28: 23 Vincular, 0 Planejar', sum(1 for v in res[6]['linhas'] if v['vinc']) == 23 and not any(v['planejar'] for v in res[6]['linhas']))
            chk('R-01 Boa Vista nova: só o B1, Livre 120 ha desde 01/09/2026', [(v['t'], v['sit'], v['area_livre'], BR(v['desde'])) for v in res[5]['linhas']] == [('B1', 'Livre', 120.0, '01/09/2026')])
            chk('R-01 LG2627 nunca oferece o T1', all(v['t'].startswith('Pivô') for v in res[4]['linhas']) and len(res[4]['linhas']) == 23)
            L4 = {v['t']: v for v in res[3]['linhas']}
            chk('§6.1 caso 5 e 2027/28', (L2['T1']['sit'], L2['T1']['area_livre'], BR(L2['T1']['desde']), L2['T2']['area_livre'], BR(L2['T2']['desde']), L2['P1']['sit'], BR(L2['P1']['desde']),
                L4['T1']['area_livre'], BR(L4['T1']['desde'])) == ('Livre', 152.0, '21/02/2027', 298.0, '16/07/2027', 'A conferir', '15/07/2027', 312.0, '01/09/2027'))
        else:
            L = {v['t']: v for v in res[1]['linhas']}
            chk('A10 folga 0: S27SF T1 a partir de 20/02/2027, P2 23/03/2027', (BR(L['T1']['desde']), BR(L['P2']['desde'])) == ('20/02/2027', '23/03/2027'))
    r0 = roda([tab_job(S['S27SF'], CU0, S, 1), tab_job(S['S2627'], CU0, S, 1)], 'sem e4/e5')
    chk('OC-U9 faixas da S27SF e da S2627 iguais com e sem e4/e5', (r0[0]['faixa'], r0[1]['faixa']) == (FX['S27SF'], FX['S2627']), (r0[0]['faixa'], r0[1]['faixa']))
    # ---------- OC-U7 · e5 em S2526 × e5 numa lista sintética ----------
    e5 = next(c for c in CU if c['id'] == 'e5'); sint = dict(id='OCUP', nome='Ocupações', ini='2026-01-01', fim='2026-12-31', faz='Santa Rita', ro=True)
    CU7 = [c for c in CU if c['id'] != 'e5'] + [dict(e5, saf='OCUP')]
    a = roda([dict(op='occ', ctx=ctxa(1), safras=S, cults=CU), dict(op='occ', ctx=ctxa(1), safras=safras_com(sint), cults=CU7),
              chk_job(CU, 'S2627', mud=('c7', dict(plano='SOJA-AT'))), chk_job(CU7, 'S2627', mud=('c7', dict(plano='SOJA-AT')), safs=safras_com(sint))], 'OC-U7')
    l1 = [o for o in a[0] if o['id'] == 'e5'][0]; l2 = [o for o in a[1] if o['id'] == 'e5'][0]
    chk('OC-U7 mesma liberação do e5 (16/11/2026) e mesma pendência do c7', BR(l1['fim'] + 1) == BR(l2['fim'] + 1) == '16/11/2026' and a[2]['pend'] == a[3]['pend'], (a[2]['pend'], a[3]['pend']))
    # ---------- OC-U8 · bordas da §7.3 (folga 1 e 0) ----------
    J = []; R = []
    def caso(rot, job, esp):
        J.append(job); R.append((rot, esp))
    f1 = 1
    caso('T1-B 152 ha 21/02/2027 salva', chk_job(CU, 'S27SF', N(faixa='T1-B', area=152, plantio='2027-02-21')), dict(trav=0, pend={}))
    caso('T1-B 152 ha 20/02/2027 pendência 1 dia com c2', chk_job(CU, 'S27SF', N(faixa='T1-B', area=152, plantio='2027-02-20')), dict(trav=0, pend={'nv': [('prevista', 'c2', '20/02/2027', '20/02/2027', 1)]}))
    caso('folga 0: T1-B 20/02/2027 sem pendência', chk_job(CU, 'S27SF', N(faixa='T1-B', area=152, plantio='2027-02-20'), folga=0), dict(trav=0, pend={}))
    caso('T1-B 15/02/2027 pendência 6 dias com c2', chk_job(CU, 'S27SF', N(faixa='T1-B', area=152, plantio='2027-02-15')), dict(trav=0, pend={'nv': [('prevista', 'c2', '15/02/2027', '20/02/2027', 6)]}))
    caso('T1-C 15/02/2027 pendência de soma no d1', chk_job(CU, 'S27SF', N(faixa='T1-C', area=152, plantio='2027-02-15')), dict(trav=0, pend={'d1': [('soma', 'c2+nv', '20/02/2027', '20/02/2027', 1)]}))
    caso('T1 312 ha 21/02/2027 recusado (M1)', chk_job(CU, 'S27SF', N(faixa='T1', tipo='Talhão inteiro', area=312, plantio='2027-02-21')),
         dict(trav=['safra', 'faixa'], mt='De 21/02/2027 a 10/07/2027, 160 ha de T1 estão com Milho (T1-A, Safrinha 2027). Máximo 152 ha nesse período.'))
    caso('T1 312 ha 11/07/2027 recusado pela área desta safra (regra de hoje)', chk_job(CU, 'S27SF', N(faixa='T1', tipo='Talhão inteiro', area=312, plantio='2027-07-11')), dict(trav=['safra']))
    for d in ('2026-10-23', '2027-01-10', '2027-02-10'):
        caso('T3 milho %s recusado (M2)' % BR(D(d)), chk_job(CU, 'S27SF', N(id='m3', faixa='T3', tipo='Talhão inteiro', area=96, plantio=d)),
             dict(trav=['faixa'], mt='T3 está com Soja 62 X da Safra 2026/27, plantada em 22/10/2026: ocupa a área até pelo menos 10/02/2027 (ciclo mínimo da soja, 112 dias, CD-02). '
                  'O plano geraria insumo e O.S. sobre lavoura em campo. Informe a colheita da soja ou plante a partir de 11/02/2027.'))
    caso('T3 milho 11/02/2027 salva com provável sobreposição (7 dias)', chk_job(CU, 'S27SF', N(id='m3', faixa='T3', tipo='Talhão inteiro', area=96, plantio='2027-02-11')),
         dict(trav=0, pend={'m3': [('provavel', 'c5', '11/02/2027', '17/02/2027', 7)]}, ma='provável sobreposição (7 dias) com a soja da Safra 2026/27'))
    caso('T3 milho 18/02/2027 salva com aviso de saída estimada', chk_job(CU, 'S27SF', N(id='m3', faixa='T3', tipo='Talhão inteiro', area=96, plantio='2027-02-18')),
         dict(trav=0, pend={}, ma='saída da soja estimada em 17/02/2027; confirme a colheita'))
    caso('T3 milho sem plano 23/10/2026 salva com aviso', chk_job(CU, 'S27SF', N(id='m3', faixa='T3', tipo='Talhão inteiro', area=96, plantio='2026-10-23', plano=None)), dict(trav=0))
    CI = muda(CU, 'c5', colheita='2027-01-20')
    caso('c5 colheita 20/01/2027 → milho 21/01/2027 salva', chk_job(CI, 'S27SF', N(id='m3', faixa='T3', tipo='Talhão inteiro', area=96, plantio='2027-01-21')), dict(trav=0, pend={}))
    caso('c5 colheita 20/01/2027 → milho 20/01/2027 recusado', chk_job(CI, 'S27SF', N(id='m3', faixa='T3', tipo='Talhão inteiro', area=96, plantio='2027-01-20')), dict(trav=['faixa']))
    for p in ('SOJA-AT', 'SOJA-PD'):
        for cid in ('c4', 'c5', 'c6'): caso('%s %s salva' % (cid, p), chk_job(CU, 'S2627', mud=(cid, dict(plano=p))), dict(trav=0, pend={}))
    caso('c7 SOJA-AT pendência 11 dias com e5 (P1)', chk_job(CU, 'S2627', mud=('c7', dict(plano='SOJA-AT')), pmin=D('2026-12-06')),
         dict(trav=0, pend={'c7': [('prevista', 'e5', '05/11/2026', '15/11/2026', 11)]},
              mp='P2: sobreposição prevista de 11 dias. A dessecação da Soja alta tecnologia cai em 05/11/2026 e o Milho AG 8700 (Safra 2025/26) está previsto até 15/11/2026. '
                 'Mude o plantio para 06/12/2026 ou depois, ou confirme a colheita do milho.'))
    caso('c7 SOJA-PD pendência 6 dias', chk_job(CU, 'S2627', mud=('c7', dict(plano='SOJA-PD'))), dict(trav=0, pend={'c7': [('prevista', 'e5', '10/11/2026', '15/11/2026', 6)]}))
    CR = muda(CU, 'e5', colheita_real='2026-11-20')
    caso('e5 colhido 20/11/2026 → c7 SOJA-AT recusado (M4)', chk_job(CR, 'S2627', mud=('c7', dict(plano='SOJA-AT')), pmin=D('2026-12-11')),
         dict(trav=['observado'], mt='O Milho AG 8700 de P2 foi colhido em 20/11/2026; a dessecação da Soja alta tecnologia cai em 05/11/2026, com o milho em campo. Plantio a partir de 11/12/2026 resolve.'))
    CA = muda(CU, 'e5', colheita=None)
    caso('e5 sem colheita informada → c7 SOJA-AT recusado (M2)', chk_job(CA, 'S2627', mud=('c7', dict(plano='SOJA-AT'))), dict(trav=['faixa']))
    caso('plantio do c1 em 30/10/2026: pendência 6 dias no d1 (P2)', chk_job(CU, 'S2627', mud=('c1', dict(plantio='2026-10-30'))),
         dict(trav=0, pend={'d1': [('prevista', 'c1', '20/02/2027', '25/02/2027', 6)]},
              mp='T1-A: a colheita prevista da Soja passa para 25/02/2027, depois do plantio do Milho da Safrinha 2027 (20/02/2027). Sobreposição prevista de 6 dias.'))
    CT = CU + [N(id='m3', faixa='T3', tipo='Talhão inteiro', area=96, plantio='2027-02-11')]
    caso('OC-11 depois SOJA-AT no c5: pendência passa ao milho (7 dias)', chk_job(CT, 'S2627', mud=('c5', dict(plano='SOJA-AT'))), dict(trav=0, pend={'m3': [('prevista', 'c5', '11/02/2027', '17/02/2027', 7)]}))
    caso('OC-11 depois SOJA-PD no c5: 4 dias', chk_job(CT, 'S2627', mud=('c5', dict(plano='SOJA-PD'))), dict(trav=0, pend={'m3': [('prevista', 'c5', '11/02/2027', '14/02/2027', 4)]}))
    CT2 = CU + [N(id='m3', faixa='T3', tipo='Talhão inteiro', area=96, plantio='2027-02-18')]
    for p in ('SOJA-AT', 'SOJA-PD'): caso('OC-23(a) T3 no padrão, depois %s no c5: sem pendência' % p, chk_job(CT2, 'S2627', mud=('c5', dict(plano=p))), dict(trav=0, pend={}))
    CP = CU + [N(id='m2', faixa='P2', tipo='Talhão inteiro', area=80, plantio='2027-03-24')]
    caso('OC-23(b) P2 milho 24/03, c7 SOJA-AT 25/11: só a pendência com e5', chk_job(CP, 'S2627', mud=('c7', dict(plano='SOJA-AT'))), dict(trav=0, pend={'c7': [('prevista', 'e5', '05/11/2026', '15/11/2026', 11)]}))
    caso('OC-23(b) c7 SOJA-AT 06/12/2026 recusado (M2 com as duas ocupações)', chk_job(CP, 'S2627', mud=('c7', dict(plano='SOJA-AT', plantio='2026-12-06'))),
         dict(trav=['faixa'], mt='P2: a Soja 62 X desta safra, plantada em 06/12/2026, ocupa a área até pelo menos 27/03/2027 (ciclo mínimo da soja, 112 dias, CD-02), e o Milho da Safrinha 2027 começa em 24/03/2027. '
              'O plano geraria insumo e O.S. sobre lavoura em campo.'))
    caso('OC-23(b) c7 SOJA-PD 01/12/2026: pendência 3 dias no milho', chk_job(CP, 'S2627', mud=('c7', dict(plano='SOJA-PD', plantio='2026-12-01'))),
         dict(trav=0, pend={'m2': [('prevista', 'c7', '24/03/2027', '26/03/2027', 3)]}))
    caso('SOJA-AT T1-B 12/03/2027 pendência 1 dia', chk_job(CU, 'S27SF', N(faixa='T1-B', area=152, cult='Soja', var='62 X', plano='SOJA-AT', plantio='2027-03-12')), dict(trav=0, pend={'nv': [('prevista', 'c2', '20/02/2027', '20/02/2027', 1)]}))
    caso('SOJA-AT T1-B 13/03/2027 salva', chk_job(CU, 'S27SF', N(faixa='T1-B', area=152, cult='Soja', var='62 X', plano='SOJA-AT', plantio='2027-03-13')), dict(trav=0, pend={}))
    s28 = safras_com(NOVAS['2027/28'])
    caso('2027/28 Milho T7 01/10/2027 recusado (M3)', chk_job(CU, 'N28', N(id='mt7', saf='N28', faixa='T7', tipo='Talhão inteiro', area=42, plantio='2027-10-01'), safs=s28),
         dict(trav=['faixa'], mt='T7 tem Mamão Formosa perene, sem fim registrado. O plano geraria insumo e O.S. sobre o pomar. O encerramento do ciclo ainda não existe no sistema.'))
    caso('2027/28 Café CAFE-AR T3 01/11/2027 salva com início 01/11/2027', chk_job(CU, 'N28', N(id='cf', saf='N28', faixa='T3', tipo='Talhão inteiro', area=96, plantio='2027-11-01', cult='Café', var='Catuaí 144', plano='CAFE-AR'), safs=s28),
         dict(trav=0, ini='01/11/2027'))
    caso('2027/28 Vincular c9: uma ocupação, sem trava', chk_job(CU, 'N28', dict(next(c for c in CU if c['id'] == 'c9'), id='v_c9', saf='N28', ciclo='c9', plano=None, colheita=None), safs=s28), dict(trav=0))
    res = roda(J, 'bordas §7.3 + mensagens')
    for (rot, esp), r in zip(R, res):
        ok = True; det = {}
        if 'trav' in esp:
            tt = [x[0] for x in r['trav']]
            ok &= (tt == [] if esp['trav'] == 0 else tt == esp['trav']); det['trav'] = tt
        if 'pend' in esp:
            pp = {k: [(p[0], p[1], BR(p[2]), BR(p[3]), p[4]) for p in v] for k, v in r['pend'].items()}
            ok &= pp == esp['pend']; det['pend'] = pp
        for k in ('mt', 'mp', 'ma'):
            if k in esp: ok &= r.get(k) == esp[k]; det[k] = r.get(k)
        if 'ini' in esp: ok &= BR(r['ini']) == esp['ini']; det['ini'] = BR(r['ini'])
        chk('OC-U8 ' + rot, ok, det)
    # ---------- R-17 PlantioMin ----------
    c7 = next(c for c in CU if c['id'] == 'c7')
    PM = [dict(op='pmin', ctx=ctxa(1), safras=S, cults=CU, sid='S2627', novo=dict(c7, plano=p), desde=D('2026-11-16'), T=80.0, ate=D('2027-01-31')) for p in ('SOJA-AT', 'SOJA-PD')]
    PM += [dict(op='pmin', ctx=ctxa(1), safras=S, cults=CU, sid='S27SF', novo=N(faixa='T1-B', area=152, cult=cu, var=vr, plano=p), desde=D('2027-02-21'), T=312.0)
           for cu, vr, p in (('Soja', '62 X', 'SOJA-AT'), ('Soja', '62 X', 'SOJA-PD'), ('Milho', 'Híbrido AG 8700', 'MILHO-SF'), ('Feijão', 'Pérola', 'FEIJ-PV'))]
    PM += [dict(op='pmin', ctx=ctxa(1), safras=S, cults=CR, sid='S2627', novo=dict(c7, plano='SOJA-AT'), desde=D('2026-11-21'), T=80.0, ate=D('2027-01-31')),
           dict(op='pmin', ctx=ctxa(1), safras=S, cults=CP, sid='S2627', novo=dict(c7, plano='SOJA-AT'), desde=D('2026-11-16'), T=80.0, ate=D('2027-01-31'))]
    pm = roda(PM, 'PlantioMin')
    chk('OC-21 PlantioMin c7 SOJA-AT 06/12/2026 · SOJA-PD 01/12/2026', [BR(x) for x in pm[:2]] == ['06/12/2026', '01/12/2026'], [BR(x) for x in pm[:2]])
    chk('OC-21 PlantioMin T1-B: SOJA-AT 13/03, SOJA-PD 08/03, MILHO-SF e FEIJ-PV 21/02/2027', [BR(x) for x in pm[2:6]] == ['13/03/2027', '08/03/2027', '21/02/2027', '21/02/2027'], [BR(x) for x in pm[2:6]])
    chk('R-17 depois da colheita real do e5: PlantioMin 11/12/2026', BR(pm[6]) == '11/12/2026', BR(pm[6]))
    chk('R-17 sem janela com o milho do P2 em 24/03/2027 (P3)', pm[7] is None, pm[7])
    ctx1 = OC.ctx_de(CULT, CVS, D2.PLANOS, 1)
    occP = OC.ocupacoes(ctx1, S, CP + [])
    o7 = OC.mk(ctx1, dict(c7, plano='SOJA-AT'), dict(S['S2627'])); seg = next(o for o in occP if o['id'] == 'm2')
    p3 = OC.msg_sem_janela(ctx1, o7, seg, D('2026-11-16'), 'S2627')
    chk('OC-U4 P3 (sem janela)', p3 == 'P2 tem Milho da Safrinha 2027 a partir de 24/03/2027. Para a soja com Soja alta tecnologia começar depois do cultivo anterior (16/11/2026), replaneje esse milho para 04/04/2027 ou depois.', p3)
    # ---------- SAF-C01 · soma com perene ou ocupação antiga no talhão (Codex + Gemini, PR #47, comentário 6079770308) ----------
    # Os 3 casos do harness do Codex (mesmo contexto e números) e 4 do autor (anual antiga; perene + perene, antiga e recente; mesma faixa), pelo serviço da tela (JS) e pelo espelho (Python).
    CTXC = dict(culturas={'Café': 'Perene', 'Soja': 'Anual'}, cultivares=[['Soja', 'Teste', 112]], folga=1,
                planos=[dict(id='PTEST', cultura='Soja', estado='Publicado', atividades=[dict(op='Colheita', nome='Colheita', g=dict(tipo='DAP', dias=120))])])
    SC01 = dict(nova=dict(id='nova', nome='Safra teste 2027', ini='2027-01-01', fim='2027-12-31', faz='Fictícia'),
                sf=dict(id='sf', nome='Safrinha teste 2027', ini='2027-03-01', fim='2027-08-31', faz='Fictícia'))
    def c01(velha, area_nova, extra=(), nova=None):
        ano = velha['plantio'][:4]
        safs = dict(SC01, velha=dict(id='velha', nome='Perene original', ini=ano + '-01-01', fim=ano + '-12-31', faz='Fictícia'))
        base = dict(saf='velha', faz='Fictícia', talhao='T1', tipo='Parcela', var='Teste')
        soja = dict(base, id='soja', ciclo='soja', saf='nova', faixa='T1-B', area=area_nova, cult='Soja', plantio='2027-06-01', plano='PTEST'); soja.update(nova or {})
        antes = [dict(base, ciclo=x['id'], **x) for x in [velha] + list(extra)]; depois = antes + [soja]
        return [dict(op='chk', ctx=CTXC, safras=safs, antes=antes, depois=depois, sid='nova', alvo='soja', T=100),
                dict(op='tab', ctx=CTXC, safra=safs['nova'], safras=safs, cults=depois, talhoes=[['T1', 100]], tot=100)]
    CAFE = lambda d: dict(id='cafe', faixa='T1-A', area=40, cult='Café', plantio=d)
    EXC_A, LIM_A, EXC_R = ('PERENE-ANTIGO-EXCESSO (café 2020 40 ha + soja 2027 70 ha)', 'PERENE-ANTIGO-LIMITE (café 2020 40 ha + soja 2027 60 ha)',
                           'PERENE-RECENTE-EXCESSO (café 2026 40 ha + soja 2027 70 ha)')
    ANUAL = 'ANUAL-ANTIGA-EXCESSO (soja 2020 em T1-C + soja 40 ha da safrinha + soja 70 ha)'
    MF = 'PERENE-ANTIGO-MESMA-FAIXA (café 2020 40 ha em T1-A + soja 2027 30 ha em T1-A)'
    PP = ['PERENE-PERENE %s (café %s 40 ha + café 2027 70 ha)' % (r, d[:4]) for r, d in (('ANTIGO', '2020-01-01'), ('RECENTE', '2026-01-01'))]
    C01 = [(EXC_A, c01(CAFE('2020-01-01'), 70)), (LIM_A, c01(CAFE('2020-01-01'), 60)), (EXC_R, c01(CAFE('2026-01-01'), 70)),
           (ANUAL, c01(dict(id='velha20', faixa='T1-C', area=30, cult='Soja', plantio='2020-06-01', plano='PTEST'), 70,
                       [dict(id='sojaA', saf='sf', faixa='T1-A', area=40, cult='Soja', plantio='2027-05-15', plano='PTEST')])),
           (PP[0], c01(CAFE('2020-01-01'), 70, nova=dict(cult='Café', plano=None))), (PP[1], c01(CAFE('2026-01-01'), 70, nova=dict(cult='Café', plano=None))),
           (MF, c01(CAFE('2020-01-01'), 30, nova=dict(faixa='T1-A')))]
    r01 = roda([j for _, js_ in C01 for j in js_], 'SAF-C01 (3 casos do Codex + 4 do autor)')
    R01 = {rot: (r01[2 * i], r01[2 * i + 1]) for i, (rot, _) in enumerate(C01)}
    def resumo(ch, tb):
        L1 = tb['linhas'][0]
        return dict(trav=ch['trav'], pend=ch['pend'], sit=L1['sit'], exc=L1['exc'], band=tb['band'], faixa=tb['faixa'])
    EXC = dict(trav=[['soma', 'cafe', 'soja', D('2027-06-01'), 110]], pend={'soja': [['soma', 'cafe', D('2027-09-21'), D('2027-09-29'), 9]]}, sit='Sobreposição', exc=10,
               band={'nesta': 70, 'livre': 0, 'conf': 0, 'perene': 30, 'ocup': 0}, faixa='Nesta safra 70 · Perene 30 · de 100 ha · 10 ha em sobreposição')
    MT = 'De 01/06/2027 a 29/09/2027, 40 ha de T1 estão com Café (T1-A, Perene original). Máximo 60 ha nesse período.'
    for rot, esp, mt in ((EXC_A, EXC, MT), (EXC_R, EXC, MT),
                         (LIM_A, dict(trav=[], pend={}, sit='Planejado', exc=0, band={'nesta': 60, 'livre': 0, 'conf': 0, 'perene': 40, 'ocup': 0}, faixa='Nesta safra 60 · Perene 40 · de 100 ha'), '')):
        got = canon(resumo(*R01[rot]))
        chk('SAF-C01 %s: trava, pendência R-15, Situação, faixa e excesso' % rot, got == canon(esp), got)
        chk('SAF-C01 %s: mensagem da trava' % rot, R01[rot][0]['mt'] == mt, R01[rot][0]['mt'])
    for rot in PP:
        ch, tb = R01[rot]
        chk('SAF-C01 %s: trava de soma, Situação Sobreposição e mensagem "A partir de" (o período não tem fim; o laço antigo da mensagem ia até 10^8 dias)' % rot,
            (ch['trav'], tb['linhas'][0]['sit'], ch['mt']) == ([['soma', 'cafe', 'soja', D('2027-06-01'), 110]], 'Sobreposição',
                                                             'A partir de 01/06/2027, 40 ha de T1 estão com Café (T1-A, Perene original). Máximo 60 ha nesse período.'), (ch['trav'], tb['linhas'][0]['sit'], ch['mt']))
    ch, tb = R01[MF]
    chk('SAF-C01 controle %s: trava de faixa (M3), sem soma (70 ha cabem), como antes' % MF,
        (ch['trav'], ch['mt'], tb['linhas'][0]['sit'], tb['linhas'][0]['exc']) == ([['faixa', 'cafe', 'soja', D('2027-06-01')]],
        'T1-A tem Café perene, sem fim registrado. O plano geraria insumo e O.S. sobre o cafezal. O encerramento do ciclo ainda não existe no sistema.', 'Sobreposição', 0),
        (ch['trav'], ch['mt'], tb['linhas'][0]['sit'], tb['linhas'][0]['exc']))
    ch, tb = R01[ANUAL]
    chk('SAF-C01 %s: a soja de 2020 não esconde a soma de 110 ha em 2027 (ocChecar e tabela)' % ANUAL,
        ch['trav'] == [['soma', 'sojaA', 'soja', D('2027-06-01'), 110]] and tb['linhas'][0]['sit'] == 'Sobreposição', (ch['trav'], tb['linhas'][0]['sit']))
    # ---------- SAF-C01 · varredura por eventos = laço dia a dia sem teto (referência) ----------
    def nuc_dia(o, x):   # núcleo no dia x, escrito à parte: [plantio, núcleo + folga), e sempre o dia do plantio (cultura sem ciclo com folga 0)
        return o['plantio'] <= x < OC.mais(o['nuc'], o['folga']) or x == o['plantio']
    def fis_ref(l):   # área física: por faixa a maior; talhão inteiro cobre o talhão
        inteiro = [o['area'] for o in l if o['tipo'] != 'Parcela']; fx = {}
        for o in l:
            if o['tipo'] == 'Parcela': fx.setdefault(o['faixa'], []).append(o['area'])
        p = sum(max(v) for v in fx.values())
        return p if not inteiro else (max(inteiro + [p]) if fx else max(inteiro))
    def soma_dia_a_dia(ctx, occs, T, alvo=None):
        """Referência: laço dia a dia da soma (R-14/R-15) sem teto, até o último ponto finito (depois dele nada muda). Área física por dia; o dia sai da
        soma do alvo só com par do próprio alvo na mesma área (no núcleo, par com plano ou perene)."""
        trav, pend = [], {}
        if not occs: return trav, pend
        d0 = min(o['ini'] for o in occs)
        d1 = max([d0] + [x for o in occs for x in (o['plantio'] + 1, OC.nuc_lib(o), OC.liberacao(ctx, o, 'est')) if x < OC.INF])
        vis_t, vis_p, ordp = set(), {}, []
        def par_alvo(l, plano):
            a = [o for o in l if alvo and o['id'] == alvo]
            return bool(a) and any(b['id'] != alvo and b['ciclo'] != a[0]['ciclo'] and (b['faixa'] == a[0]['faixa'] or a[0]['tipo'] != 'Parcela' or b['tipo'] != 'Parcela')
                                   and (not plano or OC.com_plano(a[0]) or OC.com_plano(b)) for b in l)
        for x in range(d0, d1 + 1):
            nu = [o for o in occs if nuc_dia(o, x)]
            if fis_ref(nu) > T + 0.005 and any(OC.com_plano(o) for o in nu) and not par_alvo(nu, True):
                last = max(nu, key=lambda o: (o['plantio'], o['id']))
                if not alvo or alvo in [o['id'] for o in nu]:
                    k = ('+'.join(sorted(o['id'] for o in nu if o is not last)), last['id'])
                    if k not in vis_t: vis_t.add(k); trav.append(('soma', k[0], last['id'], x, OC.r2(fis_ref(nu))))
            else:
                pv = [o for o in occs if o['ini'] <= x < OC.liberacao(ctx, o, 'est')]
                if fis_ref(pv) > T + 0.005 and not par_alvo(pv, False):
                    last = max(pv, key=lambda o: (o['plantio'], o['id']))
                    key = (last['id'], '+'.join(sorted(o['id'] for o in pv if o is not last)))
                    if key not in vis_p: vis_p[key] = []; ordp.append(key)
                    vis_p[key].append(x)
        for lid, causa in ordp:
            if alvo and alvo != lid and alvo not in causa.split('+'): continue
            d = vis_p[(lid, causa)]; pend.setdefault(lid, []).append(('soma', causa, d[0], d[-1], len(d)))
        return trav, pend
    def mt_dia_a_dia(ctx, chk, T):
        """Referência da M1 (soma/safra), dia a dia: nos dias de núcleo do alvo (até o último ponto finito), a maior área física dos outros em núcleo;
        quem = os outros no primeiro desses dias; período do maior início ao menor fim entre o alvo e eles. None: nenhum outro em núcleo."""
        o = chk['o']; outros = [x for x in chk['mesmo'] if x is not o]
        d1 = max([o['plantio']] + [x for y in chk['mesmo'] for x in (y['plantio'] + 1, OC.nuc_lib(y)) if x < OC.INF])
        best = None
        for x in range(o['plantio'], d1 + 1):
            if not nuc_dia(o, x): continue
            at = [y for y in outros if nuc_dia(y, x)]
            if at and (best is None or fis_ref(at) > best[0]): best = (fis_ref(at), at)
        if best is None: return None
        pior, quem = best
        ini = max([o['ini']] + [x['ini'] for x in quem]); fim = max(ini, min([o['fim'] if o['fim'] is not None else o['plantio']] + [x['fim'] for x in quem if x['fim'] is not None]))
        import math
        mx = T - pior; sf = [x for x in chk['trav'] if x[0] == 'safra']
        if sf: mx = min(mx, T - sum(x['area'] for x in chk['mesmo'] if x is not o and sf[0][1] in x['safs']))
        mx = math.floor(mx * 100 + 1e-6) / 100
        quando = ('A partir de %s' % BR(ini)) if fim >= OC.INF else ('De %s a %s' % (BR(ini), BR(fim)))
        return '%s, %s ha de %s estão com %s. Máximo %s ha nesse período.' % (quando, OC.ha(pior), o['t'], ' e '.join('%s (%s, %s)' % (x['cult'], x['faixa'], x['safnome']) for x in quem),
                                                                         OC.ha(max(0.0, mx)))
    def so_soma(tr, pe): return lst([t for t in tr if t[0] == 'soma']), lst({k: [p for p in v if p[0] == 'soma'] for k, v in pe.items() if any(p[0] == 'soma' for p in v)})
    rnd = random.Random(20261009); ctxr = OC.ctx_de(CULT, CVS, D2.PLANOS, 1); dif = []; nconj = ntrav = npend = nmsg = 0; jobs_r = []; grupos = {}
    for o in OC.ocupacoes(ctxr, S, CU): grupos.setdefault((o['faz'], o['t']), []).append(o)
    for (fz, t), g in grupos.items():
        T = dict(TAL[fz])[t]
        if so_soma(*OC.avalia(ctxr, g, T)) != so_soma(*soma_dia_a_dia(ctxr, g, T)): dif.append(('base', fz, t))
    CR = [('Soja', '58 W', 'SOJA-AT'), ('Soja', '62 X', None), ('Milho', 'Híbrido AG 8700', 'MILHO-SF'), ('Feijão', 'Pérola', None), ('Sorgo', 'Sem ciclo', None),
          ('Café', 'Catuaí 144', None), ('Mamão Formosa', 'Formosa', None)]
    for k in range(300):
        T = rnd.choice([100.0, 150.0]); n = rnd.randint(2, 7); cults = []; safs = {}
        for i in range(n):
            cu, vr, pid = rnd.choice(CR); pl = D('2026-06-01') + rnd.randrange(-400, 600) if rnd.random() < 0.75 else D('2012-01-01') + rnd.randrange(0, 3650)
            inteiro = rnd.random() < 0.15; fx = 'T1' if inteiro else rnd.choice(['T1-A', 'T1-B', 'T1-C'])
            sid = 'R%d' % i; safs[sid] = dict(id=sid, nome='Safra %d' % i, ini=OC.iso(pl - 30), fim=OC.iso(pl + 330), faz='F', ro=False)
            c = dict(id='o%d' % i, saf=sid, faz='F', talhao='T1', faixa=fx, tipo='Talhão inteiro' if inteiro else 'Parcela', area=(T if inteiro else OC.r2(rnd.uniform(10, T * 0.8))),
                     cult=cu, var=vr, plantio=OC.iso(pl), plano=pid, colheita=None, colheita_real=None, ciclo=None, origem='')
            u = rnd.random()
            if not pid and u < 0.25: c['colheita'] = OC.iso(pl + rnd.randrange(60, 200))
            elif u > 0.85: c['colheita_real'] = OC.iso(pl + rnd.randrange(40, 200))
            cults.append(c)
        occs = OC.ocupacoes(ctxr, safs, cults); alvo = rnd.choice([None, cults[-1]['id']]); nconj += 1
        a_, b_ = so_soma(*OC.avalia(ctxr, occs, T, alvo)), so_soma(*soma_dia_a_dia(ctxr, occs, T, alvo))
        ntrav += bool(a_[0]); npend += bool(a_[1])
        if a_ != b_: dif.append((k, a_, b_))
        rc = OC.checa(ctxr, safs, cults[:-1], cults, cults[-1]['saf'], cults[-1]['id'], T)
        if any(x[0] in ('soma', 'safra') for x in rc['trav']):
            ref = mt_dia_a_dia(ctxr, rc, T)
            if ref is not None:
                nmsg += 1
                if OC.msg_trava(ctxr, rc, cults[-1]['saf'], T, None) != ref: dif.append((k, 'msg', OC.msg_trava(ctxr, rc, cults[-1]['saf'], T, None), ref))
        if k < 120: jobs_r.append(dict(op='chk', ctx=ctxa(1), safras=safs, antes=cults[:-1], depois=cults, sid=cults[-1]['saf'], alvo=cults[-1]['id'], T=T))
    print('     (SAF-C01) conjuntos aleatórios %d · com trava de soma %d · com pendência de soma %d · mensagens M1 com período finito %d · grupos fazenda × talhão da base %d'
          % (nconj, ntrav, npend, nmsg, len(grupos)))
    chk('SAF-C01 varredura por eventos = laço dia a dia sem teto, e mensagem M1 = laço dia a dia (base + %d conjuntos aleatórios, plantios de 2012 a 2027, com e sem alvo)' % nconj, not dif, dif[:2])
    roda(jobs_r, 'SAF-C01 conjuntos aleatórios (ocChecar e mensagens)')
    # ---------- SAF-C01 · achados da verificação independente (3 verificadores, 09/10/2026) ----------
    PL = lambda i, c, dias: dict(id=i, cultura=c, estado='Publicado', atividades=dias)
    COL = lambda d: dict(op='Colheita', nome='Colheita', g=dict(tipo='DAP', dias=d))
    CTXV = dict(culturas={'Café': 'Perene', 'Soja': 'Anual', 'Milho': 'Anual'}, cultivares=[['Soja', '58 W', 112], ['Milho', 'AG', 140]], folga=1,
                planos=[PL('P', 'Soja', [COL(120)]), PL('PS', 'Soja', [dict(op='Dessecação', nome='Dessecação pré', g=dict(tipo='DAP', dias=-20)), COL(120)]), PL('PM', 'Milho', [COL(150)])])
    SV = lambda i, nome, ini, fim: dict(id=i, nome=nome, ini=ini, fim=fim, faz='F')
    CV = lambda i, saf, fx, area, cult, pl, **k: dict(dict(id=i, saf=saf, faz='F', talhao='T1', faixa=fx, tipo='Parcela', area=area, cult=cult,
                                                            var={'Café': 'C', 'Soja': '58 W', 'Milho': 'AG'}.get(cult, ''), plantio=pl), **k)
    # (1) par antigo na mesma faixa (dado antigo: café 1998 e café 2015 em T1-A) + soja nova 70 ha em T1-B: área física 40 + 70 = 110 > 100
    S1 = dict(a=SV('a', 'Café 1998', '1998-01-01', '1998-12-31'), b=SV('b', 'Café 2015', '2015-01-01', '2015-12-31'), n=SV('n', 'Safra 2027', '2027-01-01', '2027-12-31'))
    c98, c15 = CV('cafe98', 'a', 'T1-A', 40, 'Café', '1998-03-01'), CV('cafe15', 'b', 'T1-A', 40, 'Café', '2015-03-01')
    sj = lambda area, **k: CV('soja', 'n', 'T1-B', area, 'Soja', '2027-06-01', plano='P', **k)
    J1 = [dict(op='chk', ctx=CTXV, safras=S1, antes=a_, depois=a_ + [sj(ar)], sid='n', alvo='soja', T=100) for a_, ar in (([c98, c15], 70), ([c98], 70), ([c98, c15], 60))]
    J1 += [dict(op='tab', ctx=CTXV, safra=S1['n'], safras=S1, cults=[c98, c15, sj(70)], talhoes=[['T1', 100]], tot=100)]
    # (1b) par do alvo SEM plano na mesma faixa (soja sem plano 70 ha e soja antiga sem plano 30 ha em T1-A) + café 2020 40 ha em T1-B: não há T-faixa
    # para esse par, então o dia continua na soma física (máx(70, 30) + 40 = 110 > 100)
    S1b = dict(v=SV('v', 'Café 2020', '2020-01-01', '2020-12-31'), m=SV('m', 'Safra maio', '2027-01-01', '2027-12-31'), n=S1['n'])
    a1b = [CV('cafe', 'v', 'T1-B', 40, 'Café', '2020-01-01'), CV('sojav', 'm', 'T1-A', 30, 'Soja', '2027-05-20')]
    J1 += [dict(op='chk', ctx=CTXV, safras=S1b, antes=a1b, depois=a1b + [CV('soja', 'n', 'T1-A', ar, 'Soja', '2027-06-01')], sid='n', alvo='soja', T=100) for ar in (70, 60)]
    # (2) M1 com três ocupações (folga 0): o período não pode sair invertido e regravar com o "Máximo" não pode travar pela área
    S2 = dict(s1=SV('s1', 'Safra 1', '2030-01-01', '2030-12-31'), s2=SV('s2', 'Safra 2', '2030-09-01', '2031-08-31'), n=SV('n', 'Nova', '2030-01-01', '2030-12-31'))
    a2 = [CV('soja40', 's1', 'T1-A', 40, 'Soja', '2030-03-28', plano='PS'), CV('soja25', 's2', 'T1-B', 25, 'Soja', '2030-10-21', plano='PS')]
    mi = lambda ar: CV('milho', 'n', 'T1-D', ar, 'Milho', '2030-06-10', plano='PM')
    J2 = [dict(op='chk', ctx=dict(CTXV, folga=0), safras=S2, antes=a2, depois=a2 + [mi(61)], sid='n', alvo='milho', T=100)]
    # (3) cultura sem ciclo no CD-02 (sorgo com plano), talhão inteiro sobre café perene de talhão inteiro: trava de faixa também com folga 0
    CTX3 = lambda f: dict(culturas={'Café': 'Perene', 'Sorgo': 'Anual'}, cultivares=[], folga=f, planos=[PL('PSG', 'Sorgo', [COL(100)])])
    S3 = dict(a=SV('a', 'Café', '2026-01-01', '2026-12-31'), n=SV('n', 'Nova', '2027-01-01', '2027-12-31'))
    ca3 = dict(CV('cafe', 'a', 'T1', 100, 'Café', '2026-03-01'), tipo='Talhão inteiro'); so3 = dict(CV('sorgo', 'n', 'T1', 100, 'Sorgo', '2027-06-01', plano='PSG'), tipo='Talhão inteiro')
    J3 = [dict(op='chk', ctx=CTX3(f), safras=S3, antes=[ca3], depois=[ca3, so3], sid='n', alvo='sorgo', T=100) for f in (0, 1)]
    # (4) P3 com perene nova numa safra antiga e anual futura na mesma parcela: replanejar a anual não resolve; a saída é outra parcela
    S4 = dict(v=SV('v', 'Café 2020', '2020-01-01', '2020-12-31'), n=SV('n', 'BV 2027', '2027-01-01', '2027-12-31'))
    c4 = [CV('cafe', 'v', 'B1-A', 30, 'Café', '2020-01-01'), CV('soja', 'n', 'B1-A', 90, 'Soja', '2027-06-01', plano='P')]
    J4 = [dict(op='p3', ctx=CTXV, safras=S4, cults=c4, alvo='cafe', seg='soja', base=D('2020-01-01'), sid='v', livre='B1-B'),
          dict(op='p3', ctx=CTXV, safras=S4, cults=c4, alvo='cafe', seg='soja', base=D('2020-01-01'), sid='v')]
    rv = roda(J1 + J2 + J3 + J4, 'SAF-C01 achados da verificação (cruz antigo, M1 com 3, folga 0, P3 perene)')
    r1, r1c, r1l, t1, r1b, r1bl = rv[:6]; r2 = rv[6]; r3 = rv[7:9]; r4 = rv[9:11]
    chk('SAF-C01 par antigo na mesma faixa (café 1998 + café 2015 em T1-A) não tira o dia da soma: soja 70 ha trava (área física 110 ha)',
        r1['trav'] == [['soma', 'cafe15+cafe98', 'soja', D('2027-06-01'), 110]] and r1c['trav'] == [['soma', 'cafe98', 'soja', D('2027-06-01'), 110]] and r1l['trav'] == [],
        (r1['trav'], r1c['trav'], r1l['trav']))
    chk('SAF-C01 tabela com o par antigo: Sobreposição, faixa e soma (110 ha), excesso 10 ha', (t1['linhas'][0]['sit'], [x[0] for x in t1['linhas'][0]['trav']], t1['linhas'][0]['exc']) ==
        ('Sobreposição', ['faixa', 'soma'], 10), t1['linhas'][0])
    chk('SAF-C01 mensagem com o par antigo: a área física (40 ha) e o máximo que destrava (60 ha)',
        r1['mt'] == 'De 01/06/2027 a 29/09/2027, 40 ha de T1 estão com Café (T1-A, Café 1998) e Café (T1-A, Café 2015). Máximo 60 ha nesse período.', r1['mt'])
    chk('SAF-C01 par do alvo sem plano na mesma faixa: a soma física trava 70 ha e libera 60 ha', r1b['trav'][:1] == [['soma', 'cafe+sojav', 'soja', D('2027-06-01'), 110]]
        and all(x[0] == 'soma' for x in r1b['trav']) and r1bl['trav'] == [],
        (r1b['trav'], r1bl['trav']))
    import re as _re
    m2 = _re.match(r'De (\d\d/\d\d/\d{4}) a (\d\d/\d\d/\d{4}), .* Máximo ([\d.,]+) ha nesse período\.$', r2.get('mt', ''))
    dd = lambda b: D('%s-%s-%s' % (b[6:], b[3:5], b[:2]))
    ok2 = bool(m2) and dd(m2.group(1)) <= dd(m2.group(2))
    mx2 = float(m2.group(3).replace('.', '').replace(',', '.')) if m2 else None
    r2b = roda([dict(J2[0], depois=a2 + [mi(mx2 if mx2 is not None else 0)])], 'SAF-C01 M1 regravada com o Máximo')[0]
    chk('SAF-C01 M1 com três ocupações: período em ordem e com quem está no pior dia (antes: "De 01/10/2030 a 26/07/2030")',
        ok2 and r2['mt'].startswith('De 10/06/2030 a ') and 'Soja (T1-A, Safra 1)' in r2['mt'] and 'T1-B' not in r2['mt'], r2.get('mt'))
    chk('SAF-C01 M1 com três ocupações: regravar com o Máximo (%s ha) não trava pela área' % mx2, mx2 is not None and not any(x[0] in ('soma', 'safra') for x in r2b['trav']), (mx2, r2b['trav']))
    chk('SAF-C01 cultura sem ciclo com folga 0: o dia do plantio entra na T-faixa (folga 0 e 1)', [x['trav'] for x in r3] == [[['faixa', 'cafe', 'sorgo', D('2027-06-01')]]] * 2, [x['trav'] for x in r3])
    chk('SAF-C01 P3 com perene nova: "use outra parcela", sem mandar replanejar a anual', r4 == ['O café é perene e não libera B1-A: use outra parcela (ex.: B1-B).',
                                                                                              'O café é perene e não libera B1-A: use outra parcela.'], r4)
    # (5) propriedade da M1: em todo conjunto aleatório com trava de área, regravar o alvo com o "Máximo" não deixa trava de soma nem de safra
    rnd5 = random.Random(77); viol = []; nmax = 0
    maximo_ = getattr(OC, 'maximo', None)   # (o serviço anterior não tem; o teste roda contra ele para provar que pega o defeito)
    for k in range(300 if maximo_ else 0):
        T = rnd5.choice([100.0, 150.0]); n = rnd5.randint(3, 7); cults = []; safs = {}
        for i in range(n):
            cu, vr, pid = rnd5.choice(CR); pl = D('2026-06-01') + rnd5.randrange(-400, 600) if rnd5.random() < 0.75 else D('2012-01-01') + rnd5.randrange(0, 3650)
            inteiro = rnd5.random() < 0.1; fx = 'T1' if inteiro else rnd5.choice(['T1-A', 'T1-B', 'T1-C', 'T1-D'])
            sid = 'R%d' % i; safs[sid] = dict(id=sid, nome='Safra %d' % i, ini=OC.iso(pl - 30), fim=OC.iso(pl + 330), faz='F', ro=False)
            cults.append(dict(id='o%d' % i, saf=sid, faz='F', talhao='T1', faixa=fx, tipo='Talhão inteiro' if inteiro else 'Parcela', area=(T if inteiro else OC.r2(rnd5.uniform(10, T * 0.8))),
                              cult=cu, var=vr, plantio=OC.iso(pl), plano=pid, colheita=None, colheita_real=None, ciclo=None, origem=''))
        alvo = cults[-1]
        for f in (0, 1):
            ctxf = OC.ctx_de(CULT, CVS, D2.PLANOS, f); rc = OC.checa(ctxf, safs, cults[:-1], cults, alvo['saf'], alvo['id'], T)
            M = maximo_(ctxf, rc, T) if rc['o'] else None
            sf_ = [x for x in rc['trav'] if x[0] == 'safra']
            # fora do alcance: os outros sozinhos já passam da área (dado antigo); aí o "Máximo" é 0 e nenhuma área destrava
            if not M or (M['p'] and M['p']['pior'] > T + 0.005) or (sf_ and sf_[0][4] - alvo['area'] > T + 0.005): continue
            nmax += 1; a2_ = OC.r2(M['max'] - 0.004) if M['max'] > 0.004 else 0.0
            novo = dict(alvo, area=a2_, tipo='Parcela', faixa=alvo['faixa'] if alvo['tipo'] == 'Parcela' else 'T1-Z')
            rr = OC.checa(ctxf, safs, cults[:-1], cults[:-1] + [novo], alvo['saf'], alvo['id'], T)
            if any(x[0] in ('soma', 'safra') for x in rr['trav']): viol.append((k, f, M['max'], rr['trav']))
    print('     (SAF-C01) M1: %d travas de área em conjuntos aleatórios, folga 0 e 1' % nmax)
    chk('SAF-C01 propriedade da M1: regravar com o "Máximo" não deixa trava de soma nem de safra (%d casos)' % nmax, nmax > 50 and not viol, viol[:3])
    # (6) PlantioMin: o pré-filtro (desempenho) dá o mesmo dia que a busca sem filtro, inclusive sem janela, com histórico longo e perene antiga
    def plantio_min_ref(ctx, safras, cults, sid, novo, desde, T, ate=None):
        t = novo.get('talhao') or OC.talhao_de(novo['faixa'], novo['tipo'])
        base = [c for c in cults if c['faz'] == novo['faz'] and (c.get('talhao') or OC.talhao_de(c['faixa'], c['tipo'])) == t and c['id'] != novo['id']]
        antes = base + [c for c in cults if c['id'] == novo['id']]
        d = desde + (OC.antecedencia(ctx, novo['plano']) if novo.get('plano') else 0); fim = ate if ate is not None else OC.dia(safras[sid]['fim'])
        while d <= fim:
            r = OC.checa(ctx, safras, antes, base + [dict(novo, plantio=OC.iso(d))], sid, novo['id'], T)
            if not r['trav'] and not r['pend']: return d
            d += 1
        return None
    rnd6 = random.Random(2026); dif6 = []; jobs6 = []; n6 = nn6 = 0
    for k in range(40):
        T = 500.0; cults = []; safs = {}; anos = rnd6.randint(3, 12)
        if rnd6.random() < 0.7:
            safs['P0'] = SV('P0', 'Café antigo', '1996-01-01', '1996-12-31'); cults.append(CV('per', 'P0', 'T1-P', rnd6.choice([60.0, 100.0]), 'Café', '1996-03-01'))
        for a in range(anos):
            y = 2026 - anos + a; sid = 'H%d' % a; safs[sid] = SV(sid, 'Safra %d' % y, '%d-09-01' % y, '%d-08-31' % (y + 1))
            for j_, (cu, vr, pid) in enumerate(rnd6.sample(CR[:5], 3)):
                pl = D('%d-09-01' % y) + rnd6.randrange(0, 200)
                cults.append(dict(CV('h%d_%d' % (a, j_), sid, 'T1-%s' % 'ABCD'[j_], OC.r2(rnd6.uniform(50, 150)), cu, pl=OC.iso(pl)), var=vr, plano=pid, colheita=None, colheita_real=None, ciclo=None, origem=''))
        safs['N'] = SV('N', 'Nova 2027/28', '2027-09-01', '2028-08-31')
        cu, vr, pid = rnd6.choice(CR[:3]); area = rnd6.choice([100.0, 300.0, 410.0, 450.0])
        novo = dict(id='nv', saf='N', faz='F', talhao='T1', faixa='T1-N', tipo='Parcela', area=area, cult=cu, var=vr, plano=pid, colheita=None, colheita_real=None, ciclo=None, origem='', plantio='')
        if rnd6.random() < 0.3:   # edição: a versão gravada do alvo começa antes do "desde"
            cults.append(dict(novo, plantio='2027-08-20'))
        desde = D('2027-09-01') + rnd6.randrange(0, 60); ate = desde + rnd6.choice([30, 90])
        ctx6 = OC.ctx_de(CULT, CVS, D2.PLANOS, rnd6.choice([0, 1]))
        a_, b_ = OC.plantio_min(ctx6, safs, cults, 'N', novo, desde, T, ate), plantio_min_ref(ctx6, safs, cults, 'N', novo, desde, T, ate)
        n6 += 1; nn6 += a_ is None
        if a_ != b_: dif6.append((k, a_, b_))
        if k < 12: jobs6.append(dict(op='pmin', ctx=dict(ctxa(ctx6['folga'])), safras=safs, cults=cults, sid='N', novo=novo, desde=desde, T=T, ate=ate))
    print('     (SAF-C01) PlantioMin com pré-filtro × sem filtro: %d casos (%d sem janela)' % (n6, nn6))
    chk('SAF-C01 PlantioMin com pré-filtro = sem filtro (%d casos, histórico de 3 a 12 safras, perene de 1996, edição)' % n6, not dif6 and 0 < nn6 < n6, dif6[:3])
    roda(jobs6, 'SAF-C01 PlantioMin com histórico longo')
    # ---------- OC-U5 · propriedades ----------
    random.seed(20261005)
    VAR = {'Soja': '58 W', 'Milho': 'Híbrido AG 8700', 'Feijão': 'Pérola'}
    PLN = {'Soja': ['SOJA-AT', 'SOJA-PD', None], 'Milho': ['MILHO-SF', None], 'Feijão': ['FEIJ-PV', None]}
    SAFS_T = [('S27SF', None), ('N5', NOVAS['caso5']), ('N28', NOVAS['2027/28']), ('S2627', None)]
    falhas = {}; n = salvos = travados = 0; amostra = []
    def falha(k): falhas[k] = falhas.get(k, 0) + 1
    for k in range(NSEQ):
        folga = random.choice([0, 1, 3]); ctx = OC.ctx_de(CULT, CVS, D2.PLANOS, folga)
        sid, nova = random.choice(SAFS_T); safs = safras_com(nova) if nova else S; s = safs[sid]
        cults = copy.deepcopy(CU if random.random() < 0.8 else CU0)
        for passo in range(3):
            t = random.choice(['T1', 'T2', 'T3', 'T4', 'P1', 'P2', 'T7']); T = T_(t)
            cult = random.choice(list(VAR)); pid = random.choice(PLN[cult])
            d = D(s['ini']) + random.randrange(0, max(1, D(s['fim']) - D(s['ini']) - 150))
            area = OC.r2(random.uniform(10, T)); inteiro = random.random() < 0.4
            nv = N(id='n%d' % passo, saf=sid, faixa=(t if inteiro else '%s-Z%d' % (t, passo)), tipo=('Talhão inteiro' if inteiro else 'Parcela'), talhao=t,
                   area=(T if inteiro else area), plantio=OC.iso(d), cult=cult, var=VAR[cult], plano=pid)
            r = OC.checa(ctx, safs, cults, cults + [nv], sid, nv['id'], T); n += 1
            if len(amostra) < 150: amostra.append(dict(op='chk', ctx=ctxa(folga), safras=safs, antes=cults, depois=cults + [nv], sid=sid, alvo=nv['id'], T=T))
            occ2 = [x for x in OC.ocupacoes(ctx, safs, cults + [nv]) if x['t'] == t]
            r1 = sorted(x[0] for x in OC.avalia(ctx, occ2, T)[0]); r2_ = sorted(x[0] for x in OC.avalia(ctx, list(reversed(occ2)), T)[0])
            if r1 != r2_: falha('trava depende da ordem')
            if r['trav']: travados += 1; continue
            cults = cults + [nv]; salvos += 1
            m = [x for x in OC.ocupacoes(ctx, safs, cults) if x['t'] == t]
            for i, A in enumerate(m):
                for B in m[i + 1:]:
                    if A['ciclo'] != B['ciclo'] and OC.mesma_area(A, B) and (OC.com_plano(A) or OC.com_plano(B)) and OC.intersec(A['plantio'], getattr(OC, 'nuc_fim', OC.nuc_lib)(A), B['plantio'], getattr(OC, 'nuc_fim', OC.nuc_lib)(B)):
                        falha('núcleos cruzados aceitos')
            for x in sorted({o2['plantio'] for o2 in m}):   # SAF-C01: a soma dos núcleos só cresce num plantio; todos, sem horizonte (antes: 400 dias a cada 3)
                nu = [o2 for o2 in m if OC.nuc_ativo(o2, x)]
                if fis_ref(nu) > T + 0.005 and any(OC.com_plano(o2) for o2 in nu): falha('soma certa (área física) > área aceita'); break
            for o2 in m:
                if o2['classe'] == 'estimado' and OC.P(ctx, o2) < o2['fim']: falha('P < fim estimado')
                if o2['classe'] == 'perene' and OC.P(ctx, o2) != OC.INF: falha('perene com fim')
        occ = OC.ocupacoes(ctx, safs, cults); L, b = OC.tabela(ctx, s, occ, TAL['Santa Rita'], safs)
        if abs(sum(b.values()) - 1165) > 0.011: falha('faixa ≠ total')
        if sum(OC.chips(L).values()) != len(L): falha('chips ≠ Todas')
        if any(v['conf'] < -0.005 or v['livre'] < -0.005 for v in L): falha('Livre/A conferir < 0')
        if k % 8 == 0:
            t = random.choice(['T1', 'T3', 'P2']); pid = random.choice(['SOJA-AT', 'MILHO-SF']); cult = 'Soja' if pid.startswith('SOJA') else 'Milho'
            v = {x['t']: x for x in L}[t]; T = T_(t)
            nv = N(id='pm', saf=sid, faixa=t, tipo='Talhão inteiro', talhao=t, area=T, cult=cult, var=VAR[cult], plano=pid)
            if v['area_livre'] > T - 0.005 and v['desde'] is not None:
                pmv = OC.plantio_min(ctx, safs, cults, sid, nv, v['desde'], T)
                if pmv is not None:
                    rr = OC.checa(ctx, safs, cults, cults + [dict(nv, plantio=OC.iso(pmv))], sid, 'pm', T)
                    if rr['trav'] or rr['pend']: falha('PlantioMin com trava/pendência')
                    if pmv > v['desde'] + OC.antecedencia(ctx, pid):
                        rr = OC.checa(ctx, safs, cults, cults + [dict(nv, plantio=OC.iso(pmv - 1))], sid, 'pm', T)
                        if not rr['trav'] and not rr['pend']: falha('PlantioMin − 1 também passa')
    for d in ('2027-09-15', '2027-11-01', '2028-02-01'):
        for pid, cult, var in (('CAFE-AR', 'Café', 'Catuaí 144'), ('MAMAO-F', 'Mamão Formosa', 'Formosa')):
            o = OC.mk(ctx1, N(id='x', saf='N28', faixa='T3', tipo='Talhão inteiro', area=96, plantio=d, cult=cult, var=var, plano=pid), NOVAS['2027/28'])
            if o['ini'] != D(d): falha('DATA fora mudou o início')
    CV = CU + [dict(next(c for c in CU if c['id'] == x), id='v_' + x, saf='N28', ciclo=x, plano=None, colheita=None) for x in ('c9', 'c8')]
    if any(OC.avalia(ctx1, [x for x in OC.ocupacoes(ctx1, s28, CV) if x['t'] == t], T_(t))[0] for t in ('T7', 'C1')): falha('ciclo vinculado conflita')
    print('     (OC-U5) salvamentos tentados %d · aceitos %d · recusados %d' % (n, salvos, travados))
    chk('OC-U5 propriedades (%d sequências × 3 salvamentos, folga 0/1/3): 0 falhas' % NSEQ, not falhas, falhas)
    roda(amostra, 'amostra das propriedades')
    print('\nRESULTADO: %d OK · %d FALHA' % (len(OK), len(FAIL)))
    sys.exit(1 if FAIL else 0)
