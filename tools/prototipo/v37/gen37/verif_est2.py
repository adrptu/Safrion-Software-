# -*- coding: utf-8 -*-
"""Verificador · Estoque (item 07): lote recebido vencido pode ter a quarentena liberada? Entra no disponível e vira o 1º do FEFO?"""
import time
from verif_cmpest_lib import V
v=V('EST.dc.html'); J=v.J
def sv(k,val): return v.setv('#fx_g_'+k,val)
try:
    v.open()
    v.clk('2 Entregue por O.S.'); v.row('REQ-036'); print('  REQ-036 lote (FEFO) antes:', J("document.querySelector('#fx_g_ent_lote').value")); v.clk('Fechar','aside[role=dialog]')
    v.clk('1 Confira recebimentos'); v.row('NF 4533'); sv('rec_conf','20000'); sv('rec_apto','0'); sv('rec_quar','20000'); sv('rec_val','08/2026'); sv('rec_obs','Lote vencido na chegada')
    v.clk('Salvar','aside[role=dialog]'); t=v.rowtxt('NF 4533'); print('  linha:', t)
    v.chk('lote vencido não oferece "Liberar quarentena" (vencido fica fora do utilizável)', 'Liberar quarentena' not in t, t)
    if 'Liberar quarentena' in t:
        print('  liberar:', J("(()=>{const r=[...document.querySelectorAll('[role=row]')].find(r=>/NF 4533/.test(r.innerText)); const b=[...r.querySelectorAll('button')].find(b=>/Liberar quarentena/.test(b.innerText)); b.click(); return 'ok';})()")); time.sleep(.4)
        print('  confirmar:', J("(()=>{const r=[...document.querySelectorAll('[role=row]')].find(r=>/NF 4533/.test(r.innerText)); const b=[...r.querySelectorAll('button')].find(b=>/Confirmar liberação/.test(b.innerText)); b.click(); return 'ok';})()")); time.sleep(.4)
        print('  toast:', v.T())
        v.clk('4 Confira saldos'); v.clk('Expandir tudo'); t=v.rowtxt('S58-0926'); print('  S58-0926:', t)
        v.chk('lote vencido não entra no disponível', not ('20.000 kg — 20.000 kg' in t or t.count('20.000 kg')>=3), t)
        v.clk('2 Entregue por O.S.'); v.row('REQ-036'); lf=J("document.querySelector('#fx_g_ent_lote').value"); print('  REQ-036 lote (FEFO) depois:', lf, '|', J("(document.querySelector('#fx_g_ent_lote').closest('label,div')||{innerText:''}).innerText").replace('\n',' / ')[:200])
        v.chk('FEFO não sugere o lote vencido', 'S58-0926' not in lf, lf)
        v.shot('v_est_vencido_liberado.png')
    v.chk('sem erro JS no fim', J("window.__err||'nenhum'")=='nenhum', J("window.__err||''"))
finally:
    v.close()
