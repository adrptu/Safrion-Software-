# EX-55 D2 A2: aplica os 60 contextos no IN-04 de um _render e grava o pacote do coletor do Codex (mapa_camadas_test.py --coletor).
# Página isolada do ensaio: IN-04x.dc.html = IN-04 com window.__ex55e (eval no escopo da tela), criada igual na base e na candidata.
# Uso: python3 -B coleta_ex55.py <gen37 do render> <saída.json>. O contexto entra por sessionStorage 'mapa-ctx' (o mesmo que o IN-04 grava);
# o coletor (SNAPSHOT_JS) vem sempre da candidata e23f9fc8; o alvo "com alvo" é o primeiro de alvosFaz() da fazenda, igual na base e na candidata. Nada muda dados ou filtros além do contexto.
import json, os, subprocess, sys, time
G = os.path.abspath(sys.argv[1]); OUT = sys.argv[2]; sys.path.insert(0, G)
os.environ.setdefault('CDP_GL', '1')
from comp_lib import Chrome, servir
SNAP = subprocess.run([sys.executable, '-B', '/tmp/claude-0/ex55c/tools/prototipo/v37/gen37/mapa_camadas_test.py', '--coletor'], capture_output=True, text=True, check=True).stdout.strip()
FASES = ['Todas', 'A liberar', 'Liberadas', 'Em execução', 'Em conferência', 'Encerradas']
p, srv = servir(os.path.join(G, '_render')); c = Chrome(); J = c.js
U = lambda pg: f'http://127.0.0.1:{p}/{pg}'
def pronto():
    # mapa inicializado na página do ensaio; até 30 s
    for _ in range(300):
        try:
            if J("!!window.__ex55e&&window.__ex55e('!!MUX.self&&TIDS().length>0')"): return True
        except Exception: pass
        time.sleep(.1)
    return False
def abre(ctx):
    # a página anterior regrava 'mapa-ctx' ao sair: passa por uma página vazia da mesma origem (sem código do Mapa),
    # grava o contexto ali e só então abre o Mapa do ensaio
    c.goto(U('vazio-ensaio.html'), .1)
    for _ in range(50):
        if (J("location.pathname") or '').endswith('/vazio-ensaio.html') and J("document.readyState") == 'complete': break
        time.sleep(.1)
    J("localStorage.clear(); sessionStorage.clear(); sessionStorage.setItem('mapa-ctx'," + json.dumps(json.dumps(ctx)) + "); 1")
    c.call('Page.navigate', {'url': U('IN-04x.dc.html')})
    t0 = time.time()
    if not pronto(): raise SystemExit('mapa não inicializou: ' + json.dumps(ctx, ensure_ascii=False))
    print('  pronto em', round(time.time() - t0, 1), 's', flush=True)
pac, alvo = {}, {}
try:
    c.aparelho(1440, 900, 1, False)
    for faz in ['Santa Rita', 'Lagoa Grande']:
        print(faz, 'alvos', flush=True); abre({'mf_faz': faz, 'lay': 'MIP/MID'}); av = json.loads(J("window.__ex55e('JSON.stringify(alvosFaz())')") or '[]')
        if not av: raise SystemExit('sem alvos em ' + faz)
        av = sorted(av); alvo[faz] = av[0]
        casos = [('OS|%s|%s' % (v, f), {'lay': 'O.S./prazos', 'flt': {'O.S./prazos': {'ver': v, 'fase': f}}})
                 for v in ['Fases', 'Avanço', 'Atrasos', 'Impedimentos'] for f in FASES]
        casos += [('MIP|%s|%s' % (d, a), {'lay': 'MIP/MID', 'flt': {'MIP/MID': {'per': 'Últimos %s dias' % d}}, 'mipAlvos': [av[0]] if a == 'com alvo' else []})
                  for d in ['7', '30'] for a in ['sem alvo', 'com alvo']]
        casos += [('IRR|' + v, {'lay': 'Irrigação', 'flt': {'Irrigação': {'ver': v}}}) for v in ['Hoje', 'Balanço hídrico']]
        for nome, ctx in casos:
            print(faz, nome, flush=True); abre(dict(ctx, mf_faz=faz)); pac[faz + '|' + nome] = json.loads(J('window.__ex55e(' + json.dumps(SNAP) + ')'))
finally:
    c.close(); srv.terminate()
json.dump(pac, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, sort_keys=True, indent=0)
print('contextos', len(pac), '· alvos', alvo, '· saída', OUT)
