# -*- coding: utf-8 -*-
"""Main.dc.html: página técnica mínima desde 13/10/2026 (o índice central saiu; ver build)."""
import os
import engine as E


def build():
    """13/10/2026 (proprietário: "elimine essa tela e já caia direto no sistema ao clicar no artefato"): o índice saiu. O protótipo abre no
    Mapa (ui37.INICIO37) e o logotipo leva a ele; perfis trocam no avatar da barra; app de campo, portal, onboarding e backoffice ficam em
    "Outros acessos" (areas/modulos.py). Main.dc.html fica só como página técnica mínima, sem link no sistema (os testes a usam como página
    neutra para limpar o armazenamento do navegador)."""
    from ui37 import INICIO37
    fname='Main.dc.html'; E._reset_screen(fname)
    open(os.path.join(E.P,fname),'w').write('<!doctype html>\n<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
        '<title>Safrion</title></head><body style="font-family: system-ui, sans-serif; color: #15201A; margin: 24px;">'
        f'<p>O protótipo começa no <a href="{INICIO37}">Mapa</a>.</p></body></html>')
