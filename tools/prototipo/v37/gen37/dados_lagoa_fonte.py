# -*- coding: utf-8 -*-
"""Fonte dos dados da Fazenda Lagoa Grande (CONTINUIDADE-MAC-20261003 / CORTE-REMOTO-01 · CAMADA-SINTETICA-01).
Reais só no Mac do proprietário (dados_lagoa_kml.py + dados_lagoa/); fora dele (GitHub, nuvem) a demonstração sintética de
dados_lagoa_sintetico/ com os mesmos nomes e formatos. SAFRION_DADOS=sintetico força a sintética mesmo com a real presente.
Nunca mistura: sem as constantes E a pasta reais, tudo vem da sintética (ROTULO = 'Demonstração sintética', mostrado nas telas).
Na sintética, a saída é gerada sozinha quando falta ou está velha (dados_lagoa_sintetico.gerar.garantir; mesma semente, mesmos bytes)."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
_REAL_DIR = os.path.join(HERE, 'dados_lagoa'); _SINT_DIR = os.path.join(HERE, 'dados_lagoa_sintetico', 'saida')
_FORCA = os.environ.get('SAFRION_DADOS') == 'sintetico'
try:
    if _FORCA or not os.path.exists(os.path.join(_REAL_DIR, 'lagoa_s2_resumo.json')): raise ImportError('sem dado real')
    from dados_lagoa_kml import LG_FONTE, LG_GEO, LG_PIVOS, LG_PERIMETROS, LG_AMBIENTAL, LG_AGUA
    REAL = True
except ImportError:
    try:
        from dados_lagoa_sintetico.kml import LG_FONTE, LG_GEO, LG_PIVOS, LG_PERIMETROS, LG_AMBIENTAL, LG_AGUA
        from dados_lagoa_sintetico import gerar as _gerar
    except ImportError as e:
        raise ImportError('Sem dados da Lagoa Grande: no Mac, dados_lagoa_kml.py (real); fora dele, gere dados_lagoa_sintetico/ '
                          '(contrato em RETOMADA-NUVEM.md)') from e
    REAL = False
DIR = _REAL_DIR if REAL else _SINT_DIR
ROTULO = '' if REAL else 'Demonstração sintética'
if not REAL: _gerar.garantir(DIR)
# número do pivô → hectares, com a MESMA precisão do mapa (2 casas): mapa, safra, O.S., doses e custos usam o mesmo valor;
# arredondar só na exibição (SINT-C01, SINT-REV-20261003-2300)
PIVOS_HA = {int(p[0][2:]): round(p[2], 2) for p in LG_PIVOS}
