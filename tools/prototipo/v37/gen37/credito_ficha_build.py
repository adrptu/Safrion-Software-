"""Gera somente GE08 e extrai seu script real para o teste Node, sem navegador."""
import pathlib
import re
import sys
from areas import gestao
import engine

gestao._ge08()
page = pathlib.Path(engine.P) / 'GE-08.dc.html'
scripts = re.findall(r'<script[^>]*data-dc-script[^>]*>([\s\S]*?)</script>', page.read_text())
assert len(scripts) == 1 and "g_ficha" in scripts[0]
out = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(engine.ROOT) / 'credito_ficha_generated.js'
out.write_text(scripts[0])
print('GE08 gerada; script real extraído:', out)
