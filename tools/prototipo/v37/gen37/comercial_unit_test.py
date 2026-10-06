# -*- coding: utf-8 -*-
"""Comercial e logística · testes de unidade das regras (comercial.js e o que producao.js ganhou no P1) no node, sem navegador.
Uso: SAFRION_DADOS=sintetico python3 comercial_unit_test.py   → uma linha por verificação e 'RESULTADO: OK n/n' no fim.
Números: docs/comercial/verificacao/contas.py (KC01..KC18). Casos C01..C12 = docs/comercial/ESPECIFICACAO.md §8; R01..R05 = defeitos
da base f4121bd reproduzidos antes da correção (falham lá, passam depois do P1). Dados sintéticos (a Lagoa Grande é sintética)."""
import os, sys, json, subprocess
sys.dont_write_bytecode = True
os.environ.setdefault('SAFRION_DADOS', 'sintetico')
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
PRELUDIO = 'globalThis.print=(...a)=>console.log(...a);\n'
OK = []
def ok(nome, cond, info=''):
    OK.append(bool(cond)); print(('OK    ' if cond else 'FALHA ') + nome + ('' if cond else ' · ' + str(info)[:700]), flush=True)


def fonte(nucleo=True):
    import cenario
    from areas.processo_os import JS_NUCLEO
    from areas import producao as AP
    com = ''
    if os.path.exists(os.path.join(HERE, 'comercial.js')):   # na base f4121bd o arquivo não existe: só as regressões R01..R05 rodam
        import dados_comercial
        com = dados_comercial.js_regras()
    return (PRELUDIO + cenario.perfis_js() + cenario.js_prefixo() + (JS_NUCLEO if nucleo else '') + AP.PR_UI_JS + AP.PR_PED_JS + com
            + 'const NUCLEO = ' + ('true' if nucleo else 'false') + ';\n'
            + open(os.path.join(HERE, 'comercial_unit.js'), encoding='utf-8').read() + '\nprint(JSON.stringify(R));\n')


def rodar(nucleo):
    os.makedirs(os.path.join(HERE, '_probe'), exist_ok=True)
    p = os.path.join(HERE, '_probe', 'comercial_unit_%s.js' % ('com' if nucleo else 'sem'))
    open(p, 'w', encoding='utf-8').write(fonte(nucleo))
    r = subprocess.run(['node', p], capture_output=True, text=True, timeout=180)
    out = r.stdout.strip().splitlines()
    ok('motor JS (node) executou sem erro' + ('' if nucleo else ' · montado SEM o núcleo da carência'), r.returncode == 0 and out, r.stderr[-900:])
    for x in (json.loads(out[-1]) if out else []): ok(x['n'], x['ok'], x['info'])


def main():
    rodar(True)
    rodar(False)   # CE-01: página montada sem o núcleo da carência (CARD, carAvaliar)
    # nenhum nome global de producao.js, cenario.js ou do núcleo da carência é redefinido por comercial.js (a mesma guarda da Colheita)
    import re
    defs = lambda t: set(re.findall(r'^(?:function|const|let|var)\s+([A-Za-z_$][\w$]*)', t, re.M)) | set(re.findall(r'(?<![\w.])function\s+([A-Za-z_$][\w$]*)\s*\(', t))
    com = defs(open(os.path.join(HERE, 'comercial.js'), encoding='utf-8').read())
    from areas import producao as AP
    outros = {n: open(os.path.join(HERE, n), encoding='utf-8').read() for n in ('producao.js', 'cenario.js', 'g2lib.js')}
    outros.update({'dados_carencia.JS': __import__('dados_carencia').JS, 'PR_UI_JS': AP.PR_UI_JS, 'PR_PED_JS': AP.PR_PED_JS})
    for nome, t in outros.items():
        dup = sorted(com & defs(t)); ok(f'nomes de comercial.js não redefinem os de {nome}', not dup, dup)
    print('RESULTADO:', 'OK' if all(OK) else 'FALHOU', f'{sum(OK)}/{len(OK)}')
    return all(OK)


if __name__ == '__main__':
    sys.exit(0 if main() else 1)
