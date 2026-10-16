# -*- coding: utf-8 -*-
"""Apoio dos scripts de validação EX-41/EX-42 (só leitura). Usa o comp_lib do gerador (G) para o Chrome headless.
Perfil do Chrome em /tmp/claude-0/ex42_prof_<pid> (apagado no fim); mata só o processo que abriu."""
import os, sys, json, time, shutil, tempfile, atexit, subprocess
B = os.path.dirname(os.path.abspath(__file__))
G = os.environ.get('G') or '/tmp/claude-0/ex42/tools/prototipo/v37/gen37'
OUT, PNG = os.path.join(B, 'out'), os.path.join(B, 'png')
os.makedirs(OUT, exist_ok=True); os.makedirs(PNG, exist_ok=True)
os.environ.setdefault('CHROME_BIN', '/tmp/cloudchrome/chrome'); os.environ.setdefault('CDP_GL', '1'); os.environ.setdefault('SAFRION_DADOS', 'sintetico')
PROF = f'/tmp/claude-0/ex42_prof_{os.getpid()}'; os.makedirs(PROF, exist_ok=True)
os.environ['TMPDIR'] = PROF; tempfile.tempdir = PROF
sys.path.insert(0, G)
from comp_lib import Chrome, servir   # noqa: E402
_srv = []
def server(d, utf8=False):
    if not utf8:
        p, s = servir(d); _srv.append(s); return p
    # o insumo não declara charset (o Artifact põe o esqueleto na publicação): servir com text/html; charset=utf-8
    from journeys import free
    p = free(); cod = ("import http.server,functools,sys;H=http.server.SimpleHTTPRequestHandler;"
                       "H.extensions_map={**H.extensions_map,'.html':'text/html; charset=utf-8'};"
                       "http.server.ThreadingHTTPServer(('127.0.0.1',int(sys.argv[1])),functools.partial(H,directory=sys.argv[2])).serve_forever()")
    s = subprocess.Popen([sys.executable, '-c', cod, str(p), d], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(.6); _srv.append(s); return p
def chrome():
    c = Chrome(); atexit.register(lambda: (c.close(), [x.terminate() for x in _srv], shutil.rmtree(PROF, ignore_errors=True)))
    return c
def dump(nome, obj):
    with open(os.path.join(OUT, nome), 'w', encoding='utf-8') as f: json.dump(obj, f, ensure_ascii=False, indent=1)
def log(f, *a):
    s = ' '.join(str(x) for x in a); print(s, flush=True); f.write(s + '\n'); f.flush()
