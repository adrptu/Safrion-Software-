"""EX55 D2: contrato puro e contraprova; A2/A5 no navegador são separados."""
import ast
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
NODE = os.environ.get('NODE', 'node')


def main():
    subprocess.run([NODE, str(HERE / 'mapa_camadas_unit.js')], check=True)
    source = (HERE / 'mapa_camadas.js').read_text(encoding='utf-8')
    palette = json.loads(next(x for x in source.splitlines() if x.startswith('const MC_COR='))[13:-1])
    assert set(palette) == {'ok', 'good', 'lime', 'yellow', 'orange', 'red', 'gray', 'blue', 'navy', 'none', 'cloud', 'purple', 'sat'}
    with tempfile.TemporaryDirectory(prefix='ex55-mutation-') as td:
        td = Path(td)
        shutil.copyfile(HERE / 'mapa_camadas_unit.js', td / 'mapa_camadas_unit.js')
        if (HERE / 'inicio.base.py').exists():
            shutil.copyfile(HERE / 'inicio.base.py', td / 'inicio.base.py')
        assert "x.d<5?'ok'" in source
        (td / 'mapa_camadas.js').write_text(source.replace("x.d<5?'ok'", "x.d<6?'ok'", 1), encoding='utf-8')
        result = subprocess.run([NODE, str(td / 'mapa_camadas_unit.js')], capture_output=True, text=True)
        assert result.returncode != 0 and 'yellow' in result.stderr and 'ok' in result.stderr, result.stderr
        print('PASS: mutação do limiar 5→6 rejeitada por divergência de classe')
    print('PASS: contrato puro; não certifica paridade visual nem regressões de navegador')


if __name__ == '__main__':
    main()
