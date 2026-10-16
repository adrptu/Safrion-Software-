"""Gera somente GE08 e extrai seu script real para o teste Node, sem navegador."""
import pathlib
import re
import sys
from areas import gestao
import engine

gestao._ge08()
page = pathlib.Path(engine.P) / 'GE-08.dc.html'
html = page.read_text()
scripts = re.findall(r'<script[^>]*data-dc-script[^>]*>([\s\S]*?)</script>', html)
# proteção de regressão (revisão Claude do PR #90): o rótulo do botão de gravar está no painel da ficha, e o bloco Documentos mantém
# "Incluir documento" à vista com "Bens e avaliações" no ⋯
painel = html[html.index('aria-label="{{g_ficha_F.title}}"'):]
painel = painel[:painel.index('</aside>')]
assert '>{{cre_ficha_salvar_rotulo}}</button>' in painel and '>Salvar</button>' not in painel
docs = html[html.index('Documentos para crédito</h3>'):]
docs = docs[:docs.index('role="table"')]
assert docs.index('Incluir documento') < docs.index('role="menu"') < docs.index('Bens e avaliações')
assert 'CRE-0102 · condição documental pendente' in html
assert '{{cre_ficha_vazia_motivo}}' in html
assert len(scripts) == 1 and "g_ficha" in scripts[0]
out = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(engine.ROOT) / 'credito_ficha_generated.js'
out.write_text(scripts[0])
print('GE08 gerada; script real extraído:', out)
