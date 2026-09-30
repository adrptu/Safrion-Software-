# -*- coding: utf-8 -*-
"""Verificador · Compra (item 02): devolvida pela Direção e ajustada para dentro da alçada da Ana — textos de reenvio × ação da etapa 5."""
import time, json
from verif_cmpest_lib import V
v=V('CMP.dc.html'); J=v.J
TA='textarea[aria-label="Motivo da decisão"]'
try:
    v.open(); v.clk('Abrir compra'); v.clk('3 Solicite cotações'); v.clk('Enviar convites (simulado)'); time.sleep(7)
    v.clk('Comparar propostas'); v.clk('Revisar aprovação'); v.clk('Enviar à Direção')
    v.clk('Registrar devolução'); v.typ(TA,'Reduzir MAP para 40 t'); v.clk('Confirmar devolução')
    v.clk('Ajustar escolhas'); v.row('MAP 11-52'); v.setv('#'+v.fid('ped'),'40000'); v.clk('Salvar','aside[role=dialog]')
    t=v.T(); ban=J("(document.body.innerText.match(/Devolvida pela[^\\n]+/)||[''])[0]"); print('  toast:', t); print('  banner e4:', ban)
    v.clk('5 Aprove a compra'); a5=J("(document.body.innerText.match(/Valor dentro[^\\n]+|Compra ajustada[^\\n]+|Acima da sua[^\\n]+/)||[''])[0]"); pr=v.prim(); print('  a5:', a5); print('  primário:', pr)
    v.chk('textos da devolução batem com a ação da etapa 5 (dentro da alçada)', not (('Reenvie à Direção' in t or 'reenvie na etapa 5' in ban) and 'Aprovar compra' in pr), f'toast/banner pedem reenvio à Direção; primário: {pr}')
    v.chk('sem erro JS no fim', J("window.__err||'nenhum'")=='nenhum', J("window.__err||''"))
finally:
    v.close()
