# -*- coding: utf-8 -*-
"""PCM simplificado S4 · app de campo × manutenção sem navegador (padrão ma_regras_test.py).
Monta no node: perfis do g2lib + cenário único (cenario.js) + regras da manutenção (dados_manutencao) + JS do app (areas/mobile.py) + ma_app_unit.js.
Confere AC-PCM-27 e §3.7: Minha fila do Zé, Máquina herdada do turno, abastecimento e achado pelo app, sem sinal (fila uma vez só,
conflito quando a OM mudou no escritório) e a decisão do Otávio sobre o conflito.
Uso (de gen37/): python3 ma_app_test.py    (sai 1 se algum caso falhar)"""
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
    from areas import mobile as MB
    src = (PRELUDIO + cenario.perfis_js() + DM.js_prefixo() + MB.JS_BASE + MB.MBAPP_JS
           + open(os.path.join(HERE, 'ma_app_unit.js'), encoding='utf-8').read())
    os.makedirs(os.path.join(HERE, '_probe'), exist_ok=True)
    p = os.path.join(HERE, '_probe', 'ma_app_unit_all.js'); open(p, 'w', encoding='utf-8').write(src)
    r = subprocess.run(MOTOR + [p], capture_output=True, text=True, timeout=120)
    out = r.stdout.strip().splitlines()
    ok(r.returncode == 0 and out, 'motor JS (jsc/node) executou sem erro', r.stderr[:600])
    for x in (json.loads(out[-1]) if out else []): ok(x['ok'], x['n'], x['info'])
if __name__ == '__main__':
    unit()
    print(f'RESULTADO: {N[0] - len(FAIL)}/{N[0]} ok' + (' · FALHAS: ' + '; '.join(FAIL) if FAIL else ''))
    sys.exit(1 if FAIL else 0)
