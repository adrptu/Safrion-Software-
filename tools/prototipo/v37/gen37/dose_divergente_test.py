# -*- coding: utf-8 -*-
"""B-R8 · divergência de consumo/dose no fecho do turno (revisão Codex 6064114787 §2; harness "Prova focal recuperável B-R8" virou teste).
unit: monta o JS real (perfis + cenario.js + OSD do gerador + núcleo da O.S. com carência) e roda dose_divergente_unit.js no node.
nav:  Chrome real sobre o mesmo cenário (localStorage): app MB-03 a 390 px fecha o turno com dose divergente e mostra o recibo;
      O.S. (1440 px e 390 px) mostra o selo na lista, no Kanban e no painel, a linha do apontamento com planejado × informado,
      recusa de quem não é agrônomo, motivo obrigatório, aceite de Ana, repetição sem efeito e o encerramento só depois da revisão.
Uso (de gen37/, depois do build e do montar_render): python3 dose_divergente_test.py [unit|nav]   (sem argumento: unit; sai 1 se alguma falhar)"""
import os, sys, json, subprocess, tempfile, time
os.environ.setdefault('SAFRION_DADOS', 'sintetico')
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); os.chdir(HERE)
MODOS = sys.argv[1:] or ['unit']
FALHAS = 0


def unit():
    import cenario
    import areas.processo_os as P
    g2 = [l for l in open(os.path.join(HERE, 'g2lib.js'), encoding='utf-8') if l.startswith('function g2num')][0]
    pre = "var window={addEventListener(){}}; var localStorage=undefined; var location={hash:''};\n" + g2 + cenario.perfis_js()
    osd = dict(ords=P._ordens(), nova=P._nova_ordem_dados(), aloc={}, agf={})
    src = (pre + cenario.js_prefixo() + 'const OSD = ' + json.dumps(osd, ensure_ascii=False) + ';\nconst RC_OS=[];\n' + P.JS_NUCLEO + '\n'
           + open(os.path.join(HERE, 'dose_divergente_unit.js'), encoding='utf-8').read())
    fd, p = tempfile.mkstemp(prefix='dose_div_', suffix='.js')
    with os.fdopen(fd, 'w', encoding='utf-8') as f: f.write(src)
    try: r = subprocess.run(['node', p], capture_output=True, text=True, timeout=120)
    finally: os.unlink(p)
    for l in r.stdout.splitlines():
        if l.startswith('REPRO'): print(l[:900])
    L = [l for l in r.stdout.splitlines() if l.startswith('[{')]
    if r.returncode or not L: print('FALHA motor JS:', r.stderr[-1500:]); return 1
    res = json.loads(L[-1]); f = 0
    for x in res:
        print(('OK    ' if x['ok'] else 'FALHA ') + x['n'] + ('' if x['ok'] else ' · ' + x['info'][:500])); f += not x['ok']
    print(f'RESULTADO unit: {len(res) - f}/{len(res)}'); return 1 if f else 0


if 'unit' in MODOS: FALHAS += unit()
if 'nav' in MODOS:
    import dose_divergente_nav
    FALHAS += dose_divergente_nav.rodar()
sys.exit(1 if FALHAS else 0)
