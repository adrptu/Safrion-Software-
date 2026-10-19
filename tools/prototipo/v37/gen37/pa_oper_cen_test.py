"""PA-OPER F1 · cargas (P4), retrato (P19) e propriedade no serviço único da EX-38 (cenPreparoOrdem, cenario.js), em Node.
Dados sintéticos. Uso: python3 -B pa_oper_cen_test.py   (sai 0 com tudo OK)"""
import os, shutil, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import cenario

def main():
    node = os.environ.get('NODE') or shutil.which('node')
    if not node: raise SystemExit('Node indisponível')
    payload = cenario.perfis_js() + cenario.js_prefixo() + '\n' + (ROOT / 'pa_oper_cen.js').read_text(encoding='utf-8')
    run = subprocess.run([node], input=payload, text=True, capture_output=True)
    print(run.stdout, end=''); print(run.stderr, end='', file=sys.stderr)
    raise SystemExit(run.returncode)

if __name__ == '__main__': main()
