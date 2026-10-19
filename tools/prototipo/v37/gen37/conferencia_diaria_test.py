"""CONTROLE-02: núcleo real e dados sintéticos, sem mocks de permissão ou comandos."""
import argparse
import json
from pathlib import Path
import subprocess
import tempfile
import cenario
import areas.processo_os as P

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--node', default='node')
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
if args.output.exists():
    parser.error('output já existe; preserve os brutos e escolha outro caminho')
here = Path(__file__).resolve().parent
source = ('var window={addEventListener(){}};var localStorage=undefined;var location={hash:""};\n'
          + cenario.perfis_js() + cenario.js_prefixo()
          + 'const OSD=' + json.dumps({'ords':P._ordens(), 'nova':P._nova_ordem_dados(), 'aloc':{}, 'agf':{}},ensure_ascii=False) + ';const RC_OS=[];\n'
          + P.JS_NUCLEO
          + (here / 'conferencia_diaria_unit.js').read_text())
with tempfile.TemporaryDirectory(prefix='safrion-cd-unit-') as folder:
    script = Path(folder) / 'unit.js'
    script.write_text(source)
    r = subprocess.run([args.node, str(script)], capture_output=True, text=True, timeout=60)
try:
    results = json.loads(r.stdout)
except json.JSONDecodeError:
    raise RuntimeError(r.stderr or 'Nenhum resultado executado')
args.output.write_text(json.dumps({'results':results,'exit':r.returncode,'stderr':r.stderr},ensure_ascii=False,indent=2)+'\n')
passed = sum(x['ok'] for x in results)
print(f'{passed}/{len(results)}')
raise SystemExit(0 if results and passed == len(results) and r.returncode == 0 else 1)
