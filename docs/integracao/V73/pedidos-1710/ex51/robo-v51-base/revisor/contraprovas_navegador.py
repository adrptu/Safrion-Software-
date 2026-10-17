# -*- coding: utf-8 -*-
"""Contraprovas do revisor (Claude) no navegador para o robô v5.1, com páginas sintéticas (dados fictícios).
A: isolamento por marcas reprova quando dois trabalhadores dividem a mesma origem (servidor único forçado).
B: empilhado (data-g2pilha) positivo e negativo, pelo fluxo real run5()/doScreen()/passage() e pelo resumo.py.
C: 2ª passada (LEVA_JS + expressão chegouEstrito de fase_leva) com diálogo sem título cujo corpo cita o alvo.
Uso: python3 -I contraprovas_navegador.py --robo51 <pasta robo-v51> --sint <pasta das páginas ZZ-*> --trabalho <pasta nova>"""
import argparse, importlib.util, json, os, re, shutil, subprocess, sys
ap = argparse.ArgumentParser(); ap.add_argument('--robo51', required=True); ap.add_argument('--sint', required=True); ap.add_argument('--trabalho', required=True)
a = ap.parse_args()
spec = importlib.util.spec_from_file_location('rodar51', os.path.join(a.robo51, 'rodar.py')); R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
trab = os.path.abspath(a.trabalho); assert not os.path.exists(trab), 'use pasta nova'
os.makedirs(os.path.join(trab, 'robot3')); shutil.copytree(a.sint, os.path.join(trab, 'v3'))
telas = [{'n': 'ZZ-PILHAOK'}, {'n': 'ZZ-PILHAERR'}]
json.dump(telas, open(os.path.join(trab, 'robot3', 'screens.json'), 'w'))
os.makedirs(os.path.join(trab, 'entradas')); json.dump([], open(os.path.join(trab, 'entradas', 'ocultas.json'), 'w'))
json.dump({'rows': []}, open(os.path.join(trab, 'entradas', 'navegacao.json'), 'w'))
for n in R.princ_do_resumo():   # o resumo lê estas telas para o filtro estático; vazias aqui
    open(os.path.join(trab, 'v3', n + '.dc.html'), 'w').write('<html></html>')
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
        R.fase_robo(c, srvs, trab, 'isolado', ['ZZ-PILHAOK', 'ZZ-PILHAERR'], 3, 2); res['A'] = 'FALHA: não reprovou'
    except RuntimeError as e:
        res['A'] = ('PASS: reprovou' if 'armazenamento não isolado' in str(e) else 'FALHA: outro erro') + ' · ' + str(e)[:300]
finally:
    if c: c.close(); R.log(f'Chrome PID {c.p.pid} encerrado')
    srvs.parar()
# ---- B: empilhado pelo fluxo real, origens próprias ----
srvs = R.Servidores(); c = None
try:
    c = R.Chrome(R.CHROME)
    R.fase_robo(c, srvs, trab, 'isolado', ['ZZ-PILHAOK', 'ZZ-PILHAERR'], 5, 2)
    res['B_isolamento'] = json.load(open(os.path.join(trab, 'isolamento-v51.json')))
    brutos = {t['n']: json.load(open(os.path.join(trab, 'saida-isolado', t['n'] + '.v5.json'))) for t in telas}
    res['B_passagens'] = {n: [{k: p.get(k) for k in ('r', 'alvo', 'esperado', 'empilhado', 'abriu', 'destacou', 'titulo', 'voltar')} for p in d['passagens']] for n, d in brutos.items()}
    # ---- C: 2ª passada, mesma expressão de fase_leva ----
    base = srvs.subir(trab, R.ROBO, os.path.join(trab, 'robot3', 'screens.json'), os.path.join(trab, 'saida-c'))
    aba = c.abas[0]
    for pag in ('ZZ-LEVASEM', 'ZZ-LEVACOM'):
        R.limpar_origem(aba, base); aba.goto(f'{base}/v3/{pag}.dc.html', espera_corpo=False); aba.pump(1.0)
        r = aba.js(R.LEVA_JS); alvo = 'OS-0502'
        estrito = bool(alvo and re.search(r'(?<![A-Za-z0-9_-])' + re.escape(alvo) + r'(?![A-Za-z0-9_-])', ' '.join([r['dlg']] + r.get('selected', []))))
        res['C_' + pag] = {'dlg': r['dlg'], 'chegouEstrito': estrito}
finally:
    if c: c.close(); R.log(f'Chrome PID {c.p.pid} encerrado')
    srvs.parar()
out = subprocess.run([sys.executable, '-I', os.path.join(a.robo51, 'resumo.py'), os.path.join(trab, 'saida-isolado'), os.path.join(trab, 'entradas', 'ocultas.json'), os.path.join(trab, 'v3'), os.path.join(trab, 'resumo.json')], capture_output=True, text=True)
res['B_resumo'] = out.stdout.strip() or out.stderr.strip()[-400:]
json.dump(res, open(os.path.join(trab, 'contraprovas.json'), 'w'), ensure_ascii=False, indent=1)
print(json.dumps(res, ensure_ascii=False, indent=1))
