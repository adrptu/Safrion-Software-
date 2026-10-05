# -*- coding: utf-8 -*-
"""CTL-2 · Frente A (AP-ÚNICO): apontamento único web (O.S. e Mapa) × app. PRD 8.5 l.3017-3036 (OSDIA-03/04/06), DEMO-11 l.4751, CMD-09, ENG-021.
unit: monta o JS real (cenario.js + JS_NUCLEO da O.S. com carência + OSD do gerador + econsDet do Estoque) e roda ap_unico_unit.js no node.
nav:  Chrome real (O.S. 1440 px e app 390 px) sobre o mesmo cenário (localStorage): formulário com consumo real e operador herdado,
      duplo clique, turno do app retido, as três saídas de Paula, sem sinal, Em conferência e cliques.
Uso (de gen37/, depois do build): python3 ap_unico_test.py [unit|nav]   (sem argumento: as duas partes; sai 1 se alguma falhar)"""
import os, sys, json, re, subprocess, tempfile, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); os.chdir(HERE)
MODOS = sys.argv[1:] or ['unit', 'nav']
FALHAS = 0

def unit():
    import cenario
    import areas.processo_os as P
    est = open(os.path.join(HERE, 'areas', 'processo_estoque.py'), encoding='utf-8').read()
    econs = re.search(r'function econsDet\(c,m\)\{.*?\.filter\(Boolean\); \}', est, re.S).group(0)
    g2 = [l for l in open(os.path.join(HERE, 'g2lib.js'), encoding='utf-8') if l.startswith('function g2num')][0]
    pre = "var window={addEventListener(){}}; var localStorage=undefined; var location={hash:''};\n" + g2
    osd = dict(ords=P._ordens(), nova=P._nova_ordem_dados(), aloc={}, agf={})
    src = (pre + cenario.js_prefixo() + 'const OSD = ' + json.dumps(osd, ensure_ascii=False) + ';\nconst RC_OS=[];\n' + P.JS_NUCLEO + '\n' + econs + '\n'
           + open(os.path.join(HERE, 'ap_unico_unit.js'), encoding='utf-8').read())
    fd, p = tempfile.mkstemp(prefix='ap_unico_', suffix='.js')
    with os.fdopen(fd, 'w', encoding='utf-8') as f: f.write(src)
    try: r = subprocess.run(['node', p], capture_output=True, text=True, timeout=120)
    finally: os.unlink(p)
    L = [l for l in r.stdout.splitlines() if l.startswith('[{')]
    for l in r.stdout.splitlines():
        if l.startswith('REPRO'): print(l)
    if r.returncode or not L: print('FALHA motor JS:', r.stderr[-1500:]); return 1
    res = json.loads(L[-1]); f = 0
    for x in res:
        print(('OK    ' if x['ok'] else 'FALHA ') + x['n'] + ('' if x['ok'] else ' · ' + x['info'][:400])); f += not x['ok']
    print(f'RESULTADO unit: {len(res) - f}/{len(res)}'); return 1 if f else 0

if 'unit' in MODOS: FALHAS += unit()
if 'nav' in MODOS:
    import ap_unico_nav
    FALHAS += ap_unico_nav.rodar()
sys.exit(1 if FALHAS else 0)
