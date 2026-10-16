"""IRR-ONDA0: domínio Node com dados sintéticos. Sem navegador.
Uso: NODE=/caminho/node python3 -B irr_onda0_test.py
IRR_SOURCE opcional permite contraprova na base.
"""
import ast, json, os, subprocess, tempfile
from pathlib import Path
os.environ['SAFRION_DADOS'] = 'sintetico'
import dados_irrigacao as DI
import dados as D
HERE = Path(__file__).resolve().parent
tree = ast.parse((HERE / 'areas/irrigacao.py').read_text())
detail = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'ir03det')
js = next(n.value for n in ast.walk(detail) if isinstance(n, ast.Constant) and isinstance(n.value, str) and 'function EXTRAVALS' in n.value)
common = next(n.value for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, str) and 'function IRG(id)' in n.value)
num = next(x for x in (HERE / 'g2lib.js').read_text().splitlines() if x.startswith('function g2num('))
with tempfile.TemporaryDirectory(prefix='irr-onda0-') as td:
    fixture = Path(td) / 'seed.json'
    fixture.write_text(json.dumps({'irr': DI.seed(), 'fichas': D.FICHA_PIVO, 'detail': js, 'common': common, 'num': num}), encoding='utf-8')
    result = subprocess.run([os.environ.get('NODE', 'node'), str(HERE / 'irr_onda0_unit.js'), str(fixture)], cwd=HERE)
    raise SystemExit(result.returncode)
