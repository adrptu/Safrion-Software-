# -*- coding: utf-8 -*-
"""CMP-MAT (V69) · regras de Compras de materiais, peças e serviços sem navegador (padrão ma_regras_test.py).
Monta no node: perfis de demonstração do g2lib + cenário + regras da manutenção (com dados_compras_mat) + compras_materiais_unit.js.
Uso (de gen37/): python3 -B compras_materiais_unit_test.py    (sai 1 se algum caso falhar)"""
import os, sys, json, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'
MOTOR, PRELUDIO = ([JSC], '') if os.path.exists(JSC) else (['node'], 'globalThis.print=(...a)=>console.log(...a);\n')
FAIL = []; N = [0]
def ok(cond, msg, extra=''):
    N[0] += 1; print(('OK    ' if cond else 'FALHA ') + msg + ('' if cond else ' · ' + str(extra)[:600]), flush=True)
    if not cond: FAIL.append(msg)
def unit():
    import cenario, dados_manutencao as DM
    src = PRELUDIO + cenario.perfis_js() + DM.js_prefixo() + open(os.path.join(HERE, 'compras_materiais_unit.js'), encoding='utf-8').read()
    os.makedirs(os.path.join(HERE, '_probe'), exist_ok=True)
    p = os.path.join(HERE, '_probe', 'compras_materiais_unit_all.js'); open(p, 'w', encoding='utf-8').write(src)
    r = subprocess.run(MOTOR + [p], capture_output=True, text=True, timeout=120)
    out = r.stdout.strip().splitlines()
    ok(r.returncode == 0 and out, 'motor JS (jsc/node) executou sem erro', r.stderr[:600])
    for x in (json.loads(out[-1]) if out else []): ok(x['ok'], x['n'], x['info'])
if __name__ == '__main__':
    os.chdir(HERE); unit()
    print(f'RESULTADO: {N[0] - len(FAIL)}/{N[0]} ok' + (' · FALHAS: ' + '; '.join(FAIL) if FAIL else ''))
    sys.exit(1 if FAIL else 0)
