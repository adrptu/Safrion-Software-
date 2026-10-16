# Apoio comum dos scripts do PR #76: acha o gen37 pelo caminho do repositório (ou GEN37) e serve um _render no Chrome do comp_lib.
import os, sys
AQUI = os.path.dirname(os.path.abspath(__file__))
GEN = os.environ.get('GEN37') or os.path.normpath(os.path.join(AQUI, '..', '..', '..', '..', '..', 'tools', 'prototipo', 'v37', 'gen37'))
sys.path.insert(0, GEN)
from comp_lib import Chrome, servir   # noqa: E402
TAMANHOS = [(1440, 900), (390, 844)]
