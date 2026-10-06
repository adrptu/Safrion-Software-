# -*- coding: utf-8 -*-
"""Produção · colheita de ponta a ponta (docs/colheita/ESPECIFICACAO.md v1.1; decisões D-01..D-25 em docs/colheita/DECISOES.md).
catalogo(): o que as regras de producao.js leem e não mudam (PRDC): unidade de mercado por cultura (dados_cad.CULTURA_UN, fonte única).
Os números da demonstração valem na camada sintética (dados_lagoa_fonte.REAL = False); os testes rodam com SAFRION_DADOS=sintetico."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
import dados_cad as DC


def catalogo():
    return dict(un=DC.CULTURA_UN)


def js_regras():
    """PRDC + producao.js (regras e comandos pr*)."""
    return ('const PRDC = ' + json.dumps(catalogo(), ensure_ascii=False).replace('</', '<\\/') + ';\n'
            + open(os.path.join(HERE, 'producao.js'), encoding='utf-8').read() + '\n')
