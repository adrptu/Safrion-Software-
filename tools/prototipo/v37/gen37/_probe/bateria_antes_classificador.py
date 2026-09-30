# -*- coding: utf-8 -*-
"""Bateria de regressão do protótipo: roda cada teste isolado, com limite de tempo, e grava resumo com a última linha de cada um.
Uso: python3 _probe/bateria.py [saida.md]"""
import subprocess, sys, os, time, datetime, re
G = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(G)
TESTES = [
 ['matest.py'], ['ostest.py'], ['os_cenario_test.py'], ['os_irrig_filtro_test.py'], ['os_v39_bloq_test.py'], ['os_v39_liberar_test.py'], ['os_v39_selo_agua_test.py'],
 ['esttest.py'], ['est_cenario_test.py'], ['est_fix1_test.py'], ['est_fix2_test.py'], ['cmptest.py'],
 ['mbtest.py', 'a'], ['mbtest.py', 'b'], ['mbtest.py', 'c'], ['mbtest.py', 'd'],
 ['app_cenario_test.py'], ['app_mb02det_test.py'], ['app_mb03_turno_test.py'], ['app_mb03x_test.py'], ['app_mb04_test.py'], ['app_os0424_test.py'], ['app_restaurar_test.py'], ['app_saldo_zero_test.py'],
 ['intest.py'], ['map_aprov_test.py'], ['map_decisoes_test.py'], ['map_irrig_filtro_test.py'], ['irtest.py'], ['pltest.py'], ['cftest.py'],
 ['cadf_test.py'], ['cadf_det_test.py'], ['cadf_fix_det_test.py'], ['cadf_fix_lista_test.py'], ['cadc_test.py'], ['cadc_cd02_test.py'], ['cadc_cd06_test.py'], ['cadc_cd07_test.py'],
 ['cada_cd03_test.py'], ['cada_cd04_test.py'], ['cada_fix03_test.py'], ['cada_fix04_test.py'], ['cadp_test.py'], ['cadp_vtest.py'], ['cadp_fix_test.py'], ['cd0102test.py'],
 ['saf38test.py'], ['partest.py'], ['patest.py'],
]
saida = sys.argv[1] if len(sys.argv) > 1 else '_probe/bateria_resultado.md'
linhas = [f'# Bateria de regressão · {datetime.datetime.now():%d/%m/%Y %H:%M} · gerador {G}', '', '| Teste | Saída | Tempo (s) | Última linha relevante |', '|---|---|---|---|']
tot_ok = tot_falha = 0
for t in TESTES:
    ini = time.time()
    try:
        p = subprocess.run(['python3'] + t, capture_output=True, text=True, timeout=420)
        out = (p.stdout or '') + (p.stderr or ''); code = p.returncode
    except subprocess.TimeoutExpired:
        out, code = 'TIMEOUT (420 s)', 124
    rel = [l for l in out.strip().splitlines() if re.search(r'OK|FALH|falha|RESULT|Traceback|Error|TIMEOUT|verifica', l)]
    ult = (rel[-1] if rel else (out.strip().splitlines() or [''])[-1])[:160].replace('|', '/')
    ruim = code != 0 or re.search(r'FALHA|Traceback|TIMEOUT|FALHAS: [1-9]', out) is not None
    tot_falha += bool(ruim); tot_ok += (not ruim)
    linhas.append(f"| {' '.join(t)} | {'FALHA' if ruim else 'ok'} (exit {code}) | {time.time() - ini:.0f} | {ult} |")
    open(os.path.join(G, '_probe', 'bat_' + '_'.join(t).replace('.py', '') + '.out'), 'w', encoding='utf-8').write(out)
    print(linhas[-1], flush=True)
linhas += ['', f'**{tot_ok} testes sem falha · {tot_falha} com falha.** Saídas completas: `_probe/bat_*.out`.']
open(os.path.join(G, saida), 'w', encoding='utf-8').write('\n'.join(linhas) + '\n')
print(f'\n{tot_ok} ok · {tot_falha} com falha')
