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
    # regressão (rodada 3): a etapa 4 do Planejar safra (safra.js demanda) passou a dizer a origem da dose (R21); a Compra lê a memória do
    # dados2.demanda. Sem o mesmo rótulo no Python, a memória do Fungicida A diferia entre as duas telas (saf_cmp_continuidade_test, verificação 21)
    import dados2 as D2
    fa = [e['calc'] for e in D2.demanda('S2627')['Fungicida A']['evs'] if e.get('own')]
    sj = open(os.path.join(HERE, 'safra.js'), encoding='utf-8').read()
    ok('memória da demanda no Python com a origem do ajuste do talhão, como a etapa 4 (T1-B 0,60 L/ha "(ajustado pelo usuário)"; os demais sem rótulo)',
       '0,60 L/ha (ajustado pelo usuário) × 152 ha' in fa and sum('ajustado' in x for x in fa) == 1 and "' (ajustado pelo usuário)'" in sj, fa)
    print('RESULTADO:', 'OK' if all(OK) else 'FALHOU', f'{sum(OK)}/{len(OK)}')
    return all(OK)


if __name__ == '__main__':
    sys.exit(0 if main() else 1)
