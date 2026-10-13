#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Lista os testes do protótipo que a mudança <base> → <cabeça> pode afetar (seleção pelo impacto, ACELERA 13/10/2026).

Uso: python3 testes_afetados.py <base> <cabeça> [--lista] [--motivos]
  (sem opção)  um teste por linha (caminho relativo a gen37/)
  --motivos    acrescenta o porquê de cada teste
  --lista      formato do nav.sh/roda.sh (nome|VAR=v|comando), um modo por linha, navegador primeiro

Como decide (o texto dos testes é lido na <cabeça>):
 1. Monta as duas pontas pelo cache (render_cache.sh) e compara project/ e _render/ arquivo a arquivo. Página *.dc.html que
    mudou, entrou ou saiu é "página mudada"; qualquer outro arquivo do site que mudou (support.js, JSON) conta como todas.
 2. Teste de navegador (usa cdp.py) é afetado se ele ou um apoio que ele importa (journeys, est_lib, os_lib, comp_lib, …)
    cita o nome de uma página mudada (CD-03, "CD-03.dc.html") ou varre todas as páginas (glob/listdir de *.dc.html).
 3. Qualquer teste (navegador ou unidade) é afetado se ele mesmo mudou ou se usa, direta ou indiretamente, um arquivo mudado
    de gen37/: import de módulo .py, menção a um .js/.py/.json pelo nome, ou glob que casa com ele (ex.: areas/*.py).
 4. Sempre: varredura.py, ../ferramentas/acoes_duplicadas.py e links_ocultos_test.py.
É uma seleção para rodar primeiro; a bateria completa continua valendo a cada marco."""
import sys, os, re, json, subprocess, fnmatch, filecmp

AQUI = os.path.dirname(os.path.abspath(__file__))
V37 = os.path.dirname(AQUI)
GEN = 'tools/prototipo/v37/gen37'
FIXOS = ['varredura.py', '../ferramentas/acoes_duplicadas.py', 'links_ocultos_test.py']
# Entradas de gen37 que não são teste (montagem, empacotamento, capturas, cópias antigas)
NAO_TESTE = {'build.py', 'montar_render.py', 'merge_canvas.py', 'pack37.py', 'zip37.py', 'shot.py', 'shots_all.py',
             'os_v39_shots.py', 'fluxos37_md.py', 'nav37_md.py', 'qa37.py', 'widthcheck.py', 'tabelas_inventario.py',
             'catalogo_operacoes.py', 'cada_probe.py', 'ben_massa.py'}
# Modos usados na bateria da V56 (docs/integracao/V56/brutos/lista_cand.txt) para os testes que têm modo
MODOS = {'acao_unica_test.py': [('acao_familias', '', 'familias'), ('acao_v3', '', 'v3'), ('acao_responsivo', '', 'responsivo'), ('acao_saf', '', 'saf')],
         'etapas_celular_test.py': [('etapas_celular', '', 'celular'), ('etapas_complemento', '', 'complemento'), ('etapas_desktop', '', 'desktop'), ('etapas_faixa', '', 'faixa')],
         'componentes_test.py': [('componentes_' + m, '', m) for m in ('matriz', 'rotacao', 'interacao', 'ajustes', 'ajustes2')],
         'dose_divergente_test.py': [('dose_divergente_unit', '', 'unit'), ('dose_divergente_nav', '', 'nav')],
         'cafe_apurar_test.py': [('cafe_apurar_unit', '', 'unit'), ('cafe_apurar_nav', '', 'nav')],
         'ds_test.py': [('ds_test', 'DS_PARTES=A,B,C,D,E,G', '')]}


TOPO = subprocess.run(['git', '-C', V37, 'rev-parse', '--show-toplevel'], capture_output=True, text=True, check=True).stdout.strip()


def git(*a, **k):
    return subprocess.run(['git', '-C', TOPO] + list(a), capture_output=True, check=True, **k).stdout


def montado(commit):
    """pasta do cache com project/ e _render/ do commit (monta se faltar)"""
    r = subprocess.run([os.path.join(AQUI, 'render_cache.sh'), commit], capture_output=True, text=True)
    if r.returncode: sys.exit(f'render_cache.sh {commit} falhou:\n{r.stderr}')
    return os.path.dirname(r.stdout.strip().splitlines()[-1])


def _igual(fa, fb):
    if filecmp.cmp(fa, fb, shallow=False): return True
    if os.path.basename(fa) == 'canvas.json':   # o build carimba a hora em createdOnFiles.at: não é mudança do site
        tira = lambda d: {k: v for k, v in d.items() if k != 'createdOnFiles'}
        return tira(json.load(open(fa, encoding='utf-8'))) == tira(json.load(open(fb, encoding='utf-8')))
    return False


def site_mudado(db, dh):
    """(páginas mudadas, arquivos servidos mudados, saídas do build mudadas): páginas *.dc.html de project/ e _render/;
    os demais arquivos de _render/ (support.js, JSON do AGROFIT, Lagoa) são servidos a todas as páginas; os de project/ que não
    são servidos (canvas.json) só valem para o teste que os cita pelo nome"""
    pags, servidos, saidas = set(), set(), set()
    for sub in ('project', '_render'):
        a, b = os.path.join(db, sub), os.path.join(dh, sub)
        na, nb = set(os.listdir(a)), set(os.listdir(b))
        for f in sorted(na | nb):
            if f in na and f in nb and _igual(os.path.join(a, f), os.path.join(b, f)): continue
            if f.endswith('.dc.html'): pags.add(f[:-8])
            else: (servidos if sub == '_render' else saidas).add(f)
    return pags, servidos, saidas - servidos


def arvore(commit):
    """{caminho relativo a gen37: texto} dos .py e .js de gen37/ (com areas/) e de ferramentas/ na ponta"""
    nomes = [n for n in git('ls-tree', '-r', '--name-only', commit, '--', GEN, 'tools/prototipo/v37/ferramentas').decode().splitlines()
             if n.endswith(('.py', '.js'))]
    entrada = ''.join(f'{commit}:{n}\n' for n in nomes).encode()
    out = git('cat-file', '--batch', input=entrada); txt = {}; i = 0
    for n in nomes:
        cab_fim = out.index(b'\n', i); tam = int(out[i:cab_fim].split()[2]); ini = cab_fim + 1
        txt[os.path.relpath(n, GEN)] = out[ini:ini + tam].decode('utf-8', 'replace'); i = ini + tam + 1
    return txt


IMP = re.compile(r'^\s*(?:from\s+([\w.]+)\s+import\s+\(?([\w ,*]+)|import\s+([\w., ]+?)(?:\s+as\s+\w+)?)\s*\)?\s*(?:#.*)?$', re.M)
CITA = re.compile(r'[\w\-]+\.(?:js|py|json)\b')
RODA_PY = re.compile(r'subprocess|Popen|python|runpy|exec')
GLOB = re.compile(r'glob\.glob\((.*?)\)\s*(?:\+|if|\]|\)|$)', re.M)
LIT = re.compile(r"""['"]([^'"\n]*)['"]""")
TODAS = re.compile(r'^.*\b(?:listdir|glob)\b.*\.dc\.html.*$', re.M)


def dependencias(arq, texto, por_nome, todos):
    """(importa, cita, globs): módulos .py importados; .js/.json citados pelo nome (e .py citado numa linha que o executa);
    padrões de glob relativos a gen37/"""
    base = os.path.dirname(arq); imp, cit, padroes = set(), set(), set()
    if arq.endswith('.py'):
        for m in IMP.finditer(texto):
            mods = [m.group(1)] if m.group(1) else [x.strip().split(' ')[0] for x in m.group(3).split(',')]
            if m.group(1):   # from areas import inicio, processo_os → areas/inicio.py, areas/processo_os.py
                mods += [m.group(1) + '.' + x.strip().split(' ')[0] for x in m.group(2).split(',') if x.strip() and x.strip() != '*']
            for mod in mods:
                caminho = mod.replace('.', '/')
                for cand in (caminho + '.py', caminho + '/__init__.py', os.path.join(base, caminho + '.py')):
                    cand = os.path.normpath(cand)
                    if cand in todos and cand != arq: imp.add(cand)
        for g in GLOB.finditer(texto):
            lits = [x for x in LIT.findall(g.group(1)) if x]
            if any('*' in x for x in lits): padroes.add('/'.join(lits))
    for linha in texto.splitlines():
        for c in CITA.findall(linha):
            if c.endswith('.py') and not RODA_PY.search(linha): continue
            for n in por_nome.get(c, []):
                if n != arq: cit.add(n)
    return imp, cit, padroes


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if len(args) != 2: sys.exit('uso: python3 testes_afetados.py <base> <cabeça> [--lista] [--motivos]')
    base, cab = (git('rev-parse', '--verify', a + '^{commit}').decode().strip() for a in args)
    pags, outros, saidas = site_mudado(montado(base), montado(cab))
    mudados = {os.path.normpath(os.path.relpath(n, GEN)) for n in git('diff', '--name-only', base, cab, '--', 'tools/prototipo/v37').decode().splitlines()}
    txt = arvore(cab); todos = set(txt)
    por_nome = {}
    for n in todos: por_nome.setdefault(os.path.basename(n), []).append(n)
    imp, cit, pad = {}, {}, {}
    for a, t in txt.items(): imp[a], cit[a], pad[a] = dependencias(a, t, por_nome, todos)
    for a in todos:   # glob também é uso: o arquivo que casa com o padrão entra como dependência
        for p in pad[a]:
            cit[a] |= {n for n in todos if not p.endswith('.dc.html') and fnmatch.fnmatch(n, p) and n != a}

    def fecho(a, com_citas, so_js=False):
        """o que `a` usa: imports (sempre) e, com_citas, arquivos citados — .py citado só pelo próprio `a` (script que ele roda),
        e nada citado de dentro da montagem (o gerador cita testes e ferramentas nos comentários)"""
        vistos, pilha = set(), [a]
        while pilha:
            x = pilha.pop()
            if x in vistos: continue
            vistos.add(x); pilha.extend(imp.get(x, ()))
            if com_citas and x not in gerador:
                pilha.extend(c for c in cit.get(x, ()) if not c.endswith('.py') or (x == a and not so_js))
        return vistos

    # gerador: o que a montagem usa (build.py, montar_render.py); não conta como "texto do teste" para achar páginas
    gerador = fecho('build.py', False) | fecho('montar_render.py', False)   # módulos .py que a montagem importa
    gerador |= {c for g in list(gerador) for c in cit.get(g, ()) if not c.endswith('.py') and not c.endswith(('_unit.js', '_test.js'))}
    importados = set().union(*imp.values())
    citados_js = set().union(*cit.values())
    entradas = sorted(a for a in todos if a.endswith('.py') and '/' not in a and a not in importados and a not in NAO_TESTE
                      and not a.endswith('_backup.py') and not a.startswith('dados'))
    entradas += sorted(a for a in todos if a.endswith(('_test.js', '_unit.js')) and '/' not in a and a not in citados_js)
    entradas += [f for f in FIXOS if os.path.normpath(f) in todos and f not in entradas]
    motivos = {}

    def marca(t, m): motivos.setdefault(t, []).append(m)
    for f in FIXOS: marca(f, 'conjunto fixo')
    re_pag = {p: re.compile(r'(?<![\w-])' + re.escape(p) + r'(?:\.dc\.html)?(?![\w])') for p in pags}
    navega = {}
    for t in entradas:
        nt = os.path.normpath(t)
        fi, ft = fecho(nt, False), fecho(nt, True)
        fp = fecho(nt, True, so_js=True)   # texto onde procurar as páginas: o teste, os apoios que ele importa e os .js que eles citam
        navega[t] = 'cdp.py' in fi
        if nt in mudados: marca(t, 'o teste mudou')
        usa = sorted(x for x in ft if x != nt and x in mudados)
        if usa: marca(t, 'usa arquivo mudado: ' + ', '.join(usa[:6]) + (' …' if len(usa) > 6 else ''))
        if pags or outros:
            texto = '\n'.join(txt[x] for x in fp if x == nt or x not in gerador)
            if outros and navega[t]: marca(t, 'arquivo do site mudou (vale para todas as páginas): ' + ', '.join(sorted(outros)[:4]))
            elif pags and TODAS.search(texto): marca(t, f'varre todas as páginas ({len(pags)} mudaram)')
            elif pags:
                abre = sorted(p for p, rx in re_pag.items() if rx.search(texto))
                if abre: marca(t, 'abre página mudada: ' + ', '.join(abre[:8]) + (' …' if len(abre) > 8 else ''))
        if saidas:
            texto = '\n'.join(txt[x] for x in fp if x == nt or x not in gerador)
            cita = sorted(f for f in saidas if f in texto)
            if cita: marca(t, 'lê saída do build que mudou: ' + ', '.join(cita))
    sel = sorted((t for t in entradas if t in motivos), key=lambda t: (not navega.get(t, True), t))
    print(f'# {base[:7]} → {cab[:7]}: {len(pags)} página(s) mudada(s), {len(outros)} outro(s) arquivo(s) servido(s), '
          f'{len(mudados)} arquivo(s) de tools/prototipo/v37; {len(sel)} de {len(entradas)} testes'
          + (f' (saídas do build que não são servidas e mudaram: {", ".join(sorted(saidas))})' if saidas else ''), file=sys.stderr)
    if '--gerador' in sys.argv: print('# gerador: ' + ' '.join(sorted(gerador)), file=sys.stderr)
    if '--todos' in sys.argv: sel = sorted(entradas, key=lambda t: (not navega.get(t, True), t)); motivos.update({t: motivos.get(t, ['universo']) for t in sel})
    if '--lista' in sys.argv:
        unid = False
        for t in sel:
            if not navega.get(t, True) and not unid: print('# unidade (sem navegador)'); unid = True
            nome = os.path.basename(t).rsplit('.', 1)[0]
            if t.endswith('.js'): print(f'{nome}||/usr/bin/env node {t}'); continue
            if t == '../ferramentas/acoes_duplicadas.py': print(f'acoes_duplicadas||{t} . /tmp/acoes_duplicadas_{cab[:7]}.json'); continue
            for n, e, m in MODOS.get(t, [(nome, '', '')]): print(f'{n}|{e}|{t}' + (f' {m}' if m else ''))
    else:
        for t in sel: print(t + ('  :: ' + ' · '.join(motivos[t]) if '--motivos' in sys.argv else ''))


if __name__ == '__main__':
    main()
