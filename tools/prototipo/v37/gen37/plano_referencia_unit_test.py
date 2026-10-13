"""CONTROLE-02 fatia2: núcleo puro e projeção dos seletores SAF reais, dados sintéticos.
Não testa publicação/recibo/UI: dependem de CONF-D50/CF04 e do gancho posterior.
Uso: python3 plano_referencia_unit_test.py (node no PATH).
"""
import json
import os
from pathlib import Path
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
os.environ['SAFRION_DADOS'] = 'sintetico'
os.chdir(HERE)
import engine as E
from areas import processo_safra as SAF

# Captura a montagem antes de shell37 gravar e limpar os registradores do gerador.
# Somente o destino HTML é substituído; dados, grades e seletores são os mesmos da tela.
SAF.shell37 = lambda *args, **kwargs: None
SAF.build()
shim = """const assert = require('node:assert/strict');
const __ls = {};
const localStorage = {getItem:k=>__ls[k]||null, setItem:(k,v)=>{__ls[k]=String(v);}};
const window = {addEventListener(){}};
const location = {hash:'',pathname:'',search:''};
const history = {replaceState(){}};
"""
source = (shim + '\nconst GRIDS = ' + json.dumps(E.GRIDS, ensure_ascii=False) + ';\n'
          + (HERE / 'g2lib.js').read_text() + '\n' + E.EXTRAJS[0] + '\n'
          + (HERE / 'plano_referencia.js').read_text() + '\n'
          + (HERE / 'plano_referencia_unit.js').read_text())
with tempfile.TemporaryDirectory(prefix='safrion-f2-') as td:
    target = Path(td) / 'test.js'
    target.write_text(source)
    result = subprocess.run(['node', str(target)], capture_output=True, text=True, timeout=90)
print(result.stdout, end='')
if result.stderr:
    print(result.stderr, end='')
raise SystemExit(result.returncode)
