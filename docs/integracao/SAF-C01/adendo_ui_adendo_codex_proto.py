# -*- coding: utf-8 -*-
"""Roteiro do ADENDO do Codex (comentário 6079770308, 11:22 UTC), só com botões e campos, contra o _render da worktree (somente leitura).
S2627: café C1 (2019, 38 ha) reduzido a 20 ha (C1-A); safra nova 2028 Santa Rita; Planejar C1; soja C1-B.
Aceite do Codex: Salvar 30 ha recusado com limite 18 ha e rascunho preservado; 18 ha grava. Observação do integrador: a área livre
do toast tem de sair da mesma fonte da trava (inclui o perene sem fim). Mede também 19 ha (limite + 1) e a edição para 19 ha.
Uso: python3 ui_adendo_codex.py [w h toque]"""
from pathlib import Path
import sys, os, json, time
GEN = Path('<sp-proto>/tools/prototipo/v37/gen37')
os.environ['SAFRION_DADOS'] = 'sintetico'; os.environ.pop('CDP_PORT', None); sys.path.insert(0, str(GEN))
from comp_lib import Chrome
import saf_nav_lib as L
W, H, TQ = (int(sys.argv[1]), int(sys.argv[2]), sys.argv[3] == '1') if len(sys.argv) > 3 else (1440, 900, False)
c = L.c = Chrome(); res = {}
try:
    L.abre('#saf=S2627&passo=cultivos', W, H, TQ)
    L.clica_linha('c9'); res['c9_campos'] = L.campos('g_cult_S2627')
    L.fset('g_cult_S2627', 'area', '20'); L.salvar(); res['toast_cafe'] = L.toast()
    L.botao('Trocar safra'); L.botao('Nova safra')
    for k, v in [('nome', 'Contraprova perene 2028'), ('ini', '2028-01-01'), ('fim', '2028-12-31'), ('faz', 'Santa Rita')]: L.fset('g_saf', k, v)
    L.salvar()
    res['continuar'] = L.botao('Continuar: planejar talhões')
    res['linha_C1_antes'] = L.linha('C1')
    res['planejar'] = L.na_linha('C1', 'Planejar ›'); res['painel_antes'] = L.painel()[:400]
    for k, v in [('cult', 'Soja'), ('var', '58 W'), ('plano', 'SOJA-AT'), ('plantio', '2028-06-01'), ('area', '30'), ('local', 'C1-B'), ('meta', '60')]: L.fset('g_cult_NOVA', k, v)
    L.salvar(); time.sleep(.4)
    def soja(): return [x for x in L.folhas('g_cult_NOVA') if x['v'].get('cult') == 'Soja' and x['v'].get('local', '').startswith('C1')]
    res['30ha'] = dict(alerta=L.alerta(), painel_aberto=L.painel() != '', gravadas=soja(), campos=L.campos('g_cult_NOVA'))
    L.fset('g_cult_NOVA', 'area', '19'); L.salvar(); time.sleep(.4)
    res['19ha'] = dict(alerta=L.alerta(), painel_aberto=L.painel() != '', gravadas=soja())
    L.fset('g_cult_NOVA', 'area', '18'); L.salvar(); time.sleep(.6)
    res['18ha'] = dict(toast=L.toast(), alerta=L.alerta(), gravadas=[(x['id'], x['v'].get('area'), x['v'].get('local')) for x in soja()])
    time.sleep(.5)
    res['linha_C1_depois'] = L.linha('C1'); res['faixa_depois'] = L.faixa(); res['rows_C1'] = [r for r in L.rows() if 'C1' in json.dumps(r, ensure_ascii=False)]
    s = soja()
    if s:
        L.clica_linha(s[0]['id']); L.fset('g_cult_NOVA', 'area', '19'); L.salvar(); time.sleep(.4)
        res['edita_19'] = dict(alerta=L.alerta(), areas=[x['v'].get('area') for x in soja()])
    res['erros_js'] = L.erros()
finally:
    print(json.dumps(res, ensure_ascii=False, indent=1))
    c.close(); L.srv.terminate()
