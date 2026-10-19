# -*- coding: utf-8 -*-
"""EX-53 M7a · KPI-PCM-08 backlog por especialidade sem navegador (padrão compras_materiais_unit_test.py).
Monta no node: perfis de demonstração do g2lib + cenário + regras da manutenção (com dados_compras_mat) + man_backlog_unit.js.
Uso (de gen37/): python3 -B man_backlog_unit_test.py    (sai 1 se algum caso falhar)"""
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
    src = PRELUDIO + cenario.perfis_js() + DM.js_prefixo() + open(os.path.join(HERE, 'man_backlog_unit.js'), encoding='utf-8').read()
    os.makedirs(os.path.join(HERE, '_probe'), exist_ok=True)
    p = os.path.join(HERE, '_probe', 'man_backlog_unit_all.js'); open(p, 'w', encoding='utf-8').write(src)
    r = subprocess.run(MOTOR + [p], capture_output=True, text=True, timeout=120)
    out = r.stdout.strip().splitlines()
    ok(r.returncode == 0 and out, 'motor JS (jsc/node) executou sem erro', (r.stderr or r.stdout)[:600])
    if r.returncode != 0 or not out: return   # só lê o JSON quando o motor terminou e escreveu (Codex 6258137889)
    try: casos = json.loads(out[-1])
    except ValueError as e: return ok(False, 'saída do motor é a lista de casos em JSON', [str(e), out[-1][:300]])
    for x in casos: ok(x['ok'], x['n'], x['info'])
if __name__ == '__main__':
    os.chdir(HERE); unit()
    print(f'RESULTADO: {N[0] - len(FAIL)}/{N[0]} ok' + (' · FALHAS: ' + '; '.join(FAIL) if FAIL else ''))
    sys.exit(1 if FAIL else 0)
