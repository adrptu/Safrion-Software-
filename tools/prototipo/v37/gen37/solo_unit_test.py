# -*- coding: utf-8 -*-
"""Análise de solo · testes de unidade das regras e comandos (solo.js) no node, sem navegador; e as fontes únicas no Python.
Uso: SAFRION_DADOS=sintetico python3 solo_unit_test.py   → uma linha por verificação e 'RESULTADO: OK n/n' no fim.
Números: docs/analise-solo/verificacao/conta_semente.py (§6 da especificação)."""
import os, sys, json, subprocess, re
os.environ.setdefault('SAFRION_DADOS', 'sintetico')
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
PRELUDIO = 'globalThis.print=(...a)=>console.log(...a);\n'
OK = []
def ok(nome, cond, info=''):
    OK.append(bool(cond)); print(('OK    ' if cond else 'FALHA ') + nome + ('' if cond else ' · ' + str(info)[:600]), flush=True)


def fonte():
    import cenario, dados_solo
    return (PRELUDIO + cenario.perfis_js() + cenario.js_prefixo() + dados_solo.js_prefixo()
            + open(os.path.join(HERE, 'solo_unit.js'), encoding='utf-8').read() + '\nprint(JSON.stringify(R));\n')


def main():
    os.makedirs(os.path.join(HERE, '_probe'), exist_ok=True)
    p = os.path.join(HERE, '_probe', 'solo_unit_all.js'); open(p, 'w', encoding='utf-8').write(fonte())
    r = subprocess.run(['node', p], capture_output=True, text=True, timeout=120)
    out = r.stdout.strip().splitlines()
    ok('motor JS (node) executou sem erro', r.returncode == 0 and out, r.stderr[-800:])
    for x in (json.loads(out[-1]) if out else []): ok(x['n'], x['ok'], x['info'])
    # fontes únicas no Python: garantia (CD-06 e regra), preço de referência (CD-06 e regra), corretivo fora da trava de agrotóxico
    import dados_cad as DC, dados_carencia as DCR
    ok('D-11 garantia estruturada: KCl 60% → 60 % K₂O; Calcário dolomítico → PRNT 85 % (o mesmo texto do CD-06)',
       DC.GARANTIA['KCl 60%']['k2o'] == '60' and DC.GARANTIA['Calcário dolomítico'] == dict(txt='PRNT 85%', prnt='85'))
    ok('D-10 preço de referência do Calcário dolomítico: R$ 180,00/t (fonte única do CD-06 e da regra)', DC.preco_ref('Calcário dolomítico') == 180.0 and DC.preco_ref('KCl 60%') == 2.4
       and DC.preco_ref('Semente de soja 58 W') == 9.5, (DC.preco_ref('Calcário dolomítico'), DC.preco_ref('Semente de soja 58 W')))
    pr = DCR._produtos()
    ok('A4 o Calcário dolomítico entra no registro legal como corretivo (fora da trava de agrotóxico)', pr.get('Calcário dolomítico', {}).get('defn') is False
       and pr['Calcário dolomítico']['classe'] == 'Corretivos', pr.get('Calcário dolomítico'))
    # nenhum nome global de solo.js é redefinido pelas telas que carregam o prefixo (SAF: safra.js, cal01.js, ocupacao.js)
    defs = lambda t: set(re.findall(r'^(?:function|const|let|var)\s+([A-Za-z_$][\w$]*)', t, re.M))
    so = defs(open(os.path.join(HERE, 'solo.js'), encoding='utf-8').read())
    for f in ('safra.js', 'cal01.js', 'ocupacao.js', 'cenario.js', 'producao.js', 'ben.js', 'g2lib.js', 'irrigacao_estado.js', 'mip.js'):
        dup = sorted(so & defs(open(os.path.join(HERE, f), encoding='utf-8').read())); ok(f'nomes de solo.js não colidem com {f}', not dup, dup)
    # regressão (rodada 3): solo.js entra no prefixo do cenário de todas as telas, inclusive a O.S.; o os_irrig_filtro_test (verificação 6)
    # proíbe "política de água"/"PA-07"/"exceção"/"revisão individual" no texto e nos scripts da OS.dc.html. Esse texto fica nas telas do solo e da Irrigação
    import cenario
    proib = sorted(set(re.findall(r'política de água|PA-07|exceção|revisão individual', cenario.js_prefixo(), re.I)))
    ok('prefixo do cenário (com solo.js) sem "política de água", "PA-07", "exceção" e "revisão individual" (a O.S. carrega o prefixo)', not proib, proib)
    # regressão (rodada 3): a etapa 4 do Planejar safra passou a dizer a origem da dose (R21); a Compra lê a memória do dados2.demanda.
    # Sem o mesmo rótulo no Python, a memória do Fungicida A diferia entre as duas telas (saf_cmp_continuidade_test, verificação 21).
    # Integração V56 × CTL-4: a conta das duas telas é a demanda única (demFazenda no cal01.js; dem_fazenda no Python); o rótulo vai nela,
    # e o T1-B entra só pela parte sem O.S. (OS-0421 cobre 350 de 610 ha: 152 × 260/610 = 64,79 ha), com a dose ajustada da sessão.
    import dados2 as D2
    fa = [e['calc'] for e in D2.demanda('S2627')['Fungicida A']['evs'] if e.get('own')]
    cj = open(os.path.join(HERE, 'cal01.js'), encoding='utf-8').read()
    ok('memória da demanda no Python com a origem do ajuste do talhão, como o Planejar safra (T1-B 0,60 L/ha "(ajustado pelo usuário)" na parte sem O.S.; os demais sem rótulo)',
       '0,60 L/ha (ajustado pelo usuário) × 64,79 ha' in fa and sum('ajustado' in x for x in fa) == 1 and "' (ajustado pelo usuário)'" in cj and "' (pela análise · '" in cj, fa)
    # o mesmo rótulo na conta JS (demFazenda): dose da análise, dose da sessão e padrão sem rótulo; a cópia das partes fixas da SOL (safra.js _ent) leva a origem
    occ = [dict(saf='S', k='c1|a1', a='a1', local='T1-A', tal='T1', area=160, dt='2026-12-01', nome='Cobertura',
                prods=[dict(nome='KCl 60%', grupo='F', un='kg', preco=2.4, dose=150, q=24000, orig='análise', laudo='LAU-2061')]),
           dict(saf='S', k='c2|a1', a='a1', local='T1-B', tal='T1', area=152, dt='2026-12-01', nome='Cobertura',
                prods=[dict(nome='KCl 60%', grupo='F', un='kg', preco=2.4, dose=140, q=21280, orig='sessão', laudo='')]),
           dict(saf='S', k='c3|a1', a='a1', local='T2', tal='T2', area=298, dt='2026-12-01', nome='Cobertura',
                prods=[dict(nome='KCl 60%', grupo='F', un='kg', preco=2.4, dose=120, q=35760)])]
    x = dict(saf='S', faz='F', hoje='2026-10-01', viavel='2026-10-08', ordem={'S': 0}, nomes={'S': 'S'}, occ=occ, osd=[], reservas=[], recebDt=[], fisico={})
    pj = os.path.join(HERE, '_solo_dem_orig.js')
    open(pj, 'w', encoding='utf-8').write(PRELUDIO + cj + '\nconst m=demFazenda(' + json.dumps(x, ensure_ascii=False)
                                          + ");\nprint(JSON.stringify(m['KCl 60%'].evs.filter(e=>e.own).map(e=>e.calc)));\n")
    try: r = subprocess.run(['node', pj], capture_output=True, text=True, timeout=120)
    finally: os.unlink(pj)
    cs = json.loads(r.stdout.strip().splitlines()[-1]) if r.returncode == 0 and r.stdout.strip() else []
    sj = open(os.path.join(HERE, 'safra.js'), encoding='utf-8').read()
    ok('demFazenda (Planejar safra, Compra e Mapa) escreve a origem da dose: "pela análise · LAU-2061", "ajustado pelo usuário" e o padrão sem rótulo; a SOL guarda orig e laudo',
       cs == ['150,00 kg/ha (pela análise · LAU-2061) × 160 ha', '140,00 kg/ha (ajustado pelo usuário) × 152 ha', '120,00 kg/ha × 298 ha']
       and "orig:p.orig||'',laudo:p.laudo||''" in sj, [cs, r.stderr[-400:]])
    fb = [e['calc'] for e in D2.dem_fazenda(dict(x, occ=occ))['KCl 60%']['evs'] if e.get('own')]
    ok('dem_fazenda (Python) escreve a mesma memória que o demFazenda', fb == cs, [fb, cs])
    print('RESULTADO:', 'OK' if all(OK) else 'FALHOU', f'{sum(OK)}/{len(OK)}')
    return all(OK)


if __name__ == '__main__':
    sys.exit(0 if main() else 1)
