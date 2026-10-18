# -*- coding: utf-8 -*-
"""Contraprovas do revisor (Claude), rodada 2, no navegador, para o robô v5.1 @7c2045d6, com páginas sintéticas (dados fictícios).
A: isolamento por marcas reprova quando dois trabalhadores dividem a mesma origem (servidor único forçado).
B: empilhado (A7) pelo fluxo real run5()/doScreen()/passage(): pilha com e sem gravar hash, "Abrir na tela de" imediato,
   com 1,5 s, com outro registro na dona e ausente.
C: A6, 2ª passada real (fase_leva): clique desviado por JS para outro registro; o href aponta o alvo certo.
D: A5/A3, LEVA_JS + chegada_estrita() reais em páginas com diálogo sem título, com outro título, com o título certo e só h1.
E: resumo.py e aceite.passa() sobre as saídas de B/C.
Uso: python3 -I contraprovas_navegador2.py --robo51 <pasta robo-v51> --sint <pasta das páginas ZZ-*> --trabalho <pasta nova>"""
import argparse, importlib.util, json, os, shutil, subprocess, sys
ap = argparse.ArgumentParser(); ap.add_argument('--robo51', required=True); ap.add_argument('--sint', required=True); ap.add_argument('--trabalho', required=True)
a = ap.parse_args()
def mod(nome, arq):
    spec = importlib.util.spec_from_file_location(nome, arq); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
R = mod('rodar51', os.path.join(a.robo51, 'rodar.py')); G = mod('aceite51', os.path.join(a.robo51, 'aceite.py'))
trab = os.path.abspath(a.trabalho); assert not os.path.exists(trab), 'use pasta nova'
os.makedirs(os.path.join(trab, 'robot3')); shutil.copytree(a.sint, os.path.join(trab, 'v3'))
ORIG = ['ZZ-P-RAPIDA', 'ZZ-P-LENTA', 'ZZ-PH-RAPIDA', 'ZZ-PH-LENTA', 'ZZ-PH-LENTAERR', 'ZZ-P-SEMIR', 'ZZ-PH-SEMIR', 'ZZ-DESVIO']
json.dump([{'n': n} for n in ORIG], open(os.path.join(trab, 'robot3', 'screens.json'), 'w'))
os.makedirs(os.path.join(trab, 'entradas')); json.dump([], open(os.path.join(trab, 'entradas', 'ocultas.json'), 'w'))
json.dump({'rows': []}, open(os.path.join(trab, 'entradas', 'navegacao.json'), 'w'))
for n in R.princ_do_resumo():   # o resumo lê estas telas para o filtro estático; vazias aqui
    p = os.path.join(trab, 'v3', n + '.dc.html')
    if not os.path.exists(p): open(p, 'w').write('<html></html>')
res = {}
R.esperar_vaga()
# ---- A: origem compartilhada forçada ----
srvs = R.Servidores(); c = None; real = srvs.subir; bases = []
def subir_um(*x):
    if not bases: bases.append(real(*x))
    return bases[0]
srvs.subir = subir_um
try:
    c = R.Chrome(R.CHROME)
    try:
        R.fase_robo(c, srvs, trab, 'isolado', ORIG[:2], 3, 2); res['A'] = 'FALHA: não reprovou'
    except RuntimeError as e:
        res['A'] = ('PASS: reprovou' if 'armazenamento não isolado' in str(e) else 'FALHA: outro erro') + ' · ' + str(e)[:300]
finally:
    if c: c.close(); R.log(f'Chrome PID {c.p.pid} encerrado')
    srvs.parar()
# ---- B + C + D ----
srvs = R.Servidores(); c = None
try:
    c = R.Chrome(R.CHROME)
    R.fase_robo(c, srvs, trab, 'isolado', ORIG, 5, 2)
    res['B_isolamento'] = json.load(open(os.path.join(trab, 'isolamento-v51.json')))
    saida = os.path.join(trab, 'saida-isolado')
    res['B'] = {}
    for n in ORIG:
        f = os.path.join(saida, n + '.v5.json')
        d = json.load(open(f)) if os.path.exists(f) else {'passagens': [{'r': 'sem bruto'}]}
        res['B'][n] = [{k: p.get(k) for k in ('r', 'para', 'alvo', 'empilhado', 'abriu', 'destacou', 'titulo', 'voltar')} for p in d['passagens']]
    base = srvs.subir(trab, R.ROBO, os.path.join(trab, 'robot3', 'screens.json'), saida)
    R.fase_leva(c, base, trab, 'isolado')
    res['C_leva'] = json.load(open(os.path.join(saida, 'leva-check.json')))
    aba = c.abas[0]; res['D'] = {}
    for pag, esperado in (('ZZ-LEVASEM', False), ('ZZ-LEVACOM', False), ('ZZ-LEVAOK', True), ('ZZ-LEVAH1', True)):
        R.limpar_origem(aba, base); aba.goto(f'{base}/v3/{pag}.dc.html', espera_corpo=False); aba.pump(1.0)
        r = aba.js(R.LEVA_JS); r.pop('corpo', None)
        obtido = R.chegada_estrita(r, 'OS-0502', pag)
        res['D'][pag] = {'leva': r, 'chegadaEstrita': obtido, 'esperado': esperado, 'ok': obtido is esperado}
finally:
    if c: c.close(); R.log(f'Chrome PID {c.p.pid} encerrado')
    srvs.parar()
# ---- E ----
out = subprocess.run([sys.executable, '-I', os.path.join(a.robo51, 'resumo.py'), os.path.join(trab, 'saida-isolado'), os.path.join(trab, 'entradas', 'ocultas.json'), os.path.join(trab, 'v3'), os.path.join(trab, 'resumo.json')], capture_output=True, text=True)
res['E_resumo'] = out.stdout.strip() or out.stderr.strip()[-400:]
# o passa() do portão é interno a avaliar(): cada resultado real de B entra como único caso de todo o inventário mínimo;
# "passaria" = o portão não acusa caso crítico inconclusivo/falho (os bloqueios de RA e o de taxa não dependem do caso)
import tempfile
REQ = [('OS→EST','entregar','OS-0424'),('OS→EST','entregar','OS-0425'),('OS→EST','devolver','OS-0417'),('OS→EST','saldo','OS-0418'),
       ('OS→receituário','','OS-0504'),('OS→receituário','','OS-0508'),('receituário→OS','','VIS-051'),('receituário→OS','','VIS-052'),
       ('Aprovações→OS','',''),('OM→OS','','OM-0233'),('OS→OM','','OS-0420'),('OS→OM','','OS-0431'),('OS→OM','','OS-0507')]
res['E_portao'] = {}
for n, v in res['B'].items():
    out_n = []
    for p in v:
        with tempfile.TemporaryDirectory() as d:
            json.dump({'casos': [{'percurso': g, 'sub': s, 'detalhe': i, 'visao': '', 'res': p} for g, s, i in REQ], 'origens': []}, open(os.path.join(d, 'casos-criticos.json'), 'w'))
            json.dump({'casos': [], 'origens': []}, open(os.path.join(d, 'casos-criticos-endereco.json'), 'w'))
            g = G.avaliar(d, 1.0, [])
        out_n.append({'passaria': not any('inconclusivo ou falho' in b or 'ausente ou falhou' in b for b in g['bloqueios']), 'bloqueios': g['bloqueios']})
    res['E_portao'][n] = out_n
json.dump(res, open(os.path.join(trab, 'contraprovas2.json'), 'w'), ensure_ascii=False, indent=1)
print(json.dumps(res, ensure_ascii=False, indent=1))
