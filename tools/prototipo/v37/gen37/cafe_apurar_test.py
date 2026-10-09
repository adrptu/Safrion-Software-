# -*- coding: utf-8 -*-
"""COLH-C01 · café em litros "sc a apurar" com ou sem área apontada (revisão Codex 6070584991; docs/colheita R-09).
unit: monta o JS real (perfis + cenario.js + producao.js + núcleo da O.S. + funções das telas COLH, PROD e CARGA) e roda cafe_apurar_unit.js no node.
nav:  Chrome real: Produção › Previsão e colheita (1440 e 390 px) e Estoque de produto com a carga de café de 12.000 L, depois o rendimento medido.
Uso (de gen37/, depois do build e do montar_render): python3 cafe_apurar_test.py [unit|nav]   (sem argumento: as duas; sai 1 se alguma falhar)"""
import os, sys, json, re, subprocess, tempfile
os.environ.setdefault('SAFRION_DADOS', 'sintetico')
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); os.chdir(HERE)
MODOS = sys.argv[1:] or ['unit', 'nav']
FALHAS = 0


def fatia(js, nome):
    """uma função de nível superior do JS da tela (até a próxima definição de nível superior)"""
    i = js.index('function ' + nome + '(')
    m = re.compile(r'\n(?=function |const |let |var |try )').search(js, i + 1)
    return js[i:m.start() if m else len(js)] + '\n'


def unit():
    import cenario
    from areas.processo_os import JS_NUCLEO
    from areas import producao as AP
    pre = ("globalThis.window=globalThis; var localStorage=undefined; var location={hash:''};\nfunction g2rows(){ return []; }\n"
           + cenario.perfis_js() + cenario.js_prefixo())
    telas = AP.PR_UI_JS + AP.PR_PED_JS + AP.COLH_JS + fatia(AP.PROD_JS, 'prLoteRow') + fatia(AP.PROD_JS, 'prPanLote') + fatia(AP.CARGA_JS, 'prCgSit') + fatia(AP.CARGA_JS, 'prCgOrig') + fatia(AP.CARGA_JS, 'prPanCarga')
    src = pre + JS_NUCLEO + telas + open(os.path.join(HERE, 'cafe_apurar_unit.js'), encoding='utf-8').read()
    fd, p = tempfile.mkstemp(prefix='cafe_apurar_', suffix='.js')
    with os.fdopen(fd, 'w', encoding='utf-8') as f: f.write(src)
    try: r = subprocess.run(['node', p], capture_output=True, text=True, timeout=120)
    finally: os.unlink(p)
    for l in r.stdout.splitlines():
        if l.startswith('REPRO'): print(l[:900])
    L = [l for l in r.stdout.splitlines() if l.startswith('[{')]
    if r.returncode or not L: print('FALHA motor JS:', r.stderr[-1500:]); return 1
    res = json.loads(L[-1]); f = 0
    for x in res:
        print(('OK    ' if x['ok'] else 'FALHA ') + x['n'] + ('' if x['ok'] else ' · ' + x['info'][:600])); f += not x['ok']
    print(f'RESULTADO unit: {len(res) - f}/{len(res)}'); return 1 if f else 0


if __name__ == '__main__':
    if 'unit' in MODOS: FALHAS += unit()
    if 'nav' in MODOS:
        import cafe_apurar_nav
        FALHAS += cafe_apurar_nav.rodar()
    sys.exit(1 if FALHAS else 0)
