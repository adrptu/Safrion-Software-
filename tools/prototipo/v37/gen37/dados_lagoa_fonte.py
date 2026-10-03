# -*- coding: utf-8 -*-
"""Fonte dos dados da Fazenda Lagoa Grande (CONTINUIDADE-MAC-20261003 / CORTE-REMOTO-01).
Reais só no Mac do proprietário (dados_lagoa_kml.py + dados_lagoa/); fora dele (GitHub, nuvem) a demonstração sintética de
dados_lagoa_sintetico/ com os mesmos nomes e formatos. SAFRION_DADOS=sintetico força a sintética mesmo com a real presente."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
_REAL_DIR = os.path.join(HERE, 'dados_lagoa'); _SINT_DIR = os.path.join(HERE, 'dados_lagoa_sintetico', 'saida')
_FORCA = os.environ.get('SAFRION_DADOS') == 'sintetico'
try:
    if _FORCA: raise ImportError('forçado')
    from dados_lagoa_kml import LG_FONTE, LG_GEO, LG_PIVOS, LG_PERIMETROS, LG_AMBIENTAL, LG_AGUA
    REAL = True
except ImportError:
    try: from dados_lagoa_sintetico.kml import LG_FONTE, LG_GEO, LG_PIVOS, LG_PERIMETROS, LG_AMBIENTAL, LG_AGUA
    except ImportError as e:
        raise ImportError('Sem dados da Lagoa Grande: no Mac, dados_lagoa_kml.py (real); fora dele, gere dados_lagoa_sintetico/ '
                          '(contrato em RETOMADA-NUVEM.md)') from e
    REAL = False
DIR = _REAL_DIR if (REAL and os.path.exists(os.path.join(_REAL_DIR, 'lagoa_s2_resumo.json'))) else _SINT_DIR
PIVOS_HA = {int(p[0][2:]): int(round(p[2])) for p in LG_PIVOS}     # número do pivô → hectares (como dados_lagoa_safra.PIVOS)
