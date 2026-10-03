# -*- coding: utf-8 -*-
"""Verificador · Estoque (itens 03, 04, 07, 08): validade ao trocar o pedido, formatos, mês corrente, lote já existente com outra validade,
lote vencido todo em quarentena; saldo a entregar; contagem cega (DOM, filtro), recontar e cancelar, nova contagem, INV-2609."""
import time, json
from verif_cmpest_lib import V
v=V('EST.dc.html'); J=v.J
def sv(k,val): return v.setv('#fx_g_'+k,val)
try:
    v.open(); v.chk('sem erro JS', J("window.__err||'nenhum'")=='nenhum', J("window.__err||''"))
    # ---- recebimento novo: trocar o pedido muda a regra da validade ----
    v.clk('Registrar recebimento'); ro=J("document.querySelector('#fx_g_rec_val').readOnly||document.querySelector('#fx_g_rec_val').disabled"); val=J("document.querySelector('#fx_g_rec_val').value")
    print('  PC-088:', ro, val); v.chk('PC-088 (fertilizante): Sem validade travado', ro and val=='Sem validade')
    opts=J("[...document.querySelectorAll('#fx_g_rec_ped option')].map(o=>o.value)"); print('  pedidos:', opts)
    sv('rec_ped',[o for o in opts if o.startswith('PC-091')][0]); time.sleep(.3)
    ro=J("document.querySelector('#fx_g_rec_val').readOnly||document.querySelector('#fx_g_rec_val').disabled"); val=J("document.querySelector('#fx_g_rec_val').value"); print('  PC-091:', ro, repr(val))
    v.chk('trocar para semente destrava a validade vazia', (not ro) and val=='', f'{ro} {val!r}')
    sv('rec_nf','NF 9001'); sv('rec_qtd_nf','8000'); sv('rec_conf','8000'); sv('rec_apto','8000'); sv('rec_quar','0'); sv('rec_lote','S62-0926'); sv('rec_local','Câmara fria')
    for bad in ['6/2027','06/27','00/2027','2027-06']:
        sv('rec_val',bad); v.clk('Salvar','aside[role=dialog]'); e=v.errs(); v.chk(f'validade {bad!r} recusada', 'mês/ano' in e, e)
    sv('rec_val','09/2026'); v.clk('Salvar','aside[role=dialog]'); e=v.errs(); print('  09/2026 (mês corrente):', e or 'salvou', '|', v.T())
    v.chk('validade no mês corrente é aceita', not J("!!document.querySelector('aside[role=dialog]')"), e)
    # ---- lote já existente com outra validade ----
    v.clk('Registrar recebimento'); sv('rec_ped',[o for o in opts if o.startswith('PC-090')][0]); time.sleep(.3)
    sv('rec_nf','NF 9002'); sv('rec_qtd_nf','1000'); sv('rec_conf','1000'); sv('rec_apto','1000'); sv('rec_quar','0'); sv('rec_lote','S58-0801'); sv('rec_local','Câmara fria'); sv('rec_val','01/2027')
    v.clk('Salvar','aside[role=dialog]'); e=v.errs(); print('  lote existente S58-0801 (06/2027) com 01/2027:', e or 'salvou', '|', v.T())
    salvo=not J("!!document.querySelector('aside[role=dialog]')")
    if salvo:
        v.clk('4 Confira saldos'); v.clk('Expandir tudo'); t=v.rowtxt('S58-0801'); print('  S58-0801:', t)
        v.row('S58-0801'); og=v.aside().replace('\n',' / '); print('  origem:', og[:400]); v.clk('Fechar','aside[role=dialog]')
        v.chk('validade diferente num lote já existente não é aceita sem aviso', False, 'salvou; lote ficou com '+('06/2027' if '06/2027' in t else '?')+' e a origem registra 01/2027' if 'validade 01/2027' in og else t)
        v.clk('1 Confira recebimentos')
    else: v.clk('Cancelar','aside[role=dialog]'); v.clk('Descartar alterações','aside[role=dialog]')
    # ---- lote vencido: todo em quarentena com motivo; etapa 4 e disponível (página nova) ----
    v.open(); v.row('NF 4533'); sv('rec_conf','20000'); sv('rec_apto','0'); sv('rec_quar','20000'); sv('rec_val','08/2026'); v.clk('Salvar','aside[role=dialog]'); e=v.errs(); print('  vencido sem motivo:', e)
    v.chk('vencido com apta 0 ainda exige motivo', 'motivo' in e.lower(), e)
    sv('rec_obs','Lote vencido na chegada · devolver ao fornecedor'); v.clk('Salvar','aside[role=dialog]'); print('  toast:', v.T())
    v.chk('vencido todo em quarentena salva', not J("!!document.querySelector('aside[role=dialog]')"), v.errs())
    t=v.rowtxt('NF 4533'); print('  linha:', t); v.chk('linha do recebimento mostra a validade vencida e aguarda laudo', 'validade 08/2026' in t and 'Aguarda laudo' in t, t)
    v.clk('4 Confira saldos'); v.clk('Expandir tudo'); t=v.rowtxt('S58-0926'); print('  S58-0926:', t); v.chk('lote vencido: 20 t físico, 20 t quarentena, 0 disponível, validade 08/2026', '08/2026' in t and t.count('20.000 kg')>=2, t)
    v.shot('v_est_e4.png')
    # ---- etapa 2 (página nova) ----
    v.open(); v.clk('2 Entregue por O.S.'); print('  k2:', J("document.querySelector('main').innerText.split('\\n').find(l=>/requisiç/.test(l))"))
    for rq in ['REQ-031','REQ-035','REQ-036','REQ-038','REQ-040']: print('   ',v.rowtxt(rq)[:200])
    print('  primário e2:', v.prim())
    v.row('REQ-035'); print('  sub REQ-035:', v.sub()); sv('ent_qtd','16'); v.clk('Salvar','aside[role=dialog]'); e=v.errs(); print('  16 L:', e)
    v.chk('REQ-035 16 L: mensagem com a conta', e.startswith('Acima do saldo a entregar: 15 L (175 L solicitado − 95 L consumido − 65 L em custódia)'), e)
    sv('ent_qtd','15'); v.clk('Salvar','aside[role=dialog]'); t=v.rowtxt('REQ-035'); print('  REQ-035 após 15:', t); v.chk('REQ-035 entrega completa', 'Entrega completa' in t, t)
    v.row('REQ-035'); print('  sub completa:', v.sub()); v.chk('entrega completa abre só consulta', J("document.querySelectorAll('aside[role=dialog] input:not([readonly]), aside[role=dialog] select:not([disabled])').length")==0); v.clk('Fechar','aside[role=dialog]')
    # ---- etapa 5: contagem cega (página nova) ----
    v.open(); v.clk('5 Faça contagens')
    html=J("(()=>{const r=[...document.querySelectorAll('[role=row]')].find(r=>/INV-2611/.test(r.innerText)); return r?r.outerHTML:'';})()")
    v.chk('linha A contar não carrega 1.200 nem 1200 no HTML', '1.200' not in html and '1200' not in html, [x for x in ['1.200','1200'] if x in html])
    # filtro da coluna Sistema
    fo=J("""(async()=>{const hs=[...document.querySelectorAll('[role=columnheader]')]; const h=hs.find(x=>/SISTEMA/i.test(x.innerText)); if(!h) return 'sem cabeçalho'; const b=[...h.querySelectorAll('button')].pop(); if(!b) return 'sem botão'; b.click(); await new Promise(r=>setTimeout(r,400)); const m=document.querySelector('[role=dialog]:not(aside),[role=menu],[role=listbox]'); return m?m.innerText:document.body.innerText.slice(0,0);})()""")
    print('  filtro Sistema:', str(fo)[:200]); v.chk('filtro da coluna Sistema não revela o saldo da linha a contar', '1.200' not in str(fo), fo)
    J("document.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true}))"); time.sleep(.3)
    v.shot('v_est_e5.png')
    # recontar e cancelar
    v.clk('Contar INV-2611'); sv('cnt_cont','1190'); v.clk('Salvar','aside[role=dialog]')
    print('  após contar 1190:', v.rowtxt('INV-2611'), '|', v.T(), '|', v.errs())
    print('  recontar:', J("(()=>{const r=[...document.querySelectorAll('[role=row]')].find(r=>/INV-2611/.test(r.innerText)); if(!r) return 'sem linha'; const b=[...r.querySelectorAll('button')].find(b=>b.innerText.trim()==='Recontar'); if(!b) return 'sem botão'; b.click(); return 'ok';})()")); time.sleep(.5)
    v.clk('Cancelar','aside[role=dialog]'); time.sleep(.3); print('  depois de cancelar:', v.aside()[:120].replace('\n',' / '))
    if J("!!document.querySelector('aside[role=dialog]')"): v.clk('Descartar alterações','aside[role=dialog]')
    t=v.rowtxt('INV-2611'); print('  linha após cancelar recontagem:', t, '| primário:', v.prim())
    # INV-2609 recontar: contador anterior Rui
    print('  recontar INV-2609:', J("(()=>{const r=[...document.querySelectorAll('[role=row]')].find(r=>/INV-2609/.test(r.innerText)); const b=[...r.querySelectorAll('button')].find(b=>b.innerText.trim()==='Recontar'); if(!b) return 'sem'; b.click(); return 'ok';})()")); time.sleep(.5)
    print('  contador sugerido:', J("document.querySelector('#fx_g_cnt_contador').value"), '| aside:', v.aside()[:300].replace('\n',' / '))
    v.chk('INV-2609: recontagem sugere Paula e não mostra 90.000', J("document.querySelector('#fx_g_cnt_contador').value")=='Paula (almoxarife)' and '90.000' not in v.aside())
    sv('cnt_cont','89400'); v.clk('Salvar','aside[role=dialog]'); t=v.rowtxt('INV-2609'); print('  INV-2609 recontada:', t)
    v.row('INV-2609'); og=v.aside().replace('\n',' / '); print('  origem INV-2609:', og[:400]); v.clk('Cancelar','aside[role=dialog]')
    if J("!!document.querySelector('aside[role=dialog]')"): v.clk('Descartar alterações','aside[role=dialog]')
    # nova contagem
    v.clk('+ Nova contagem') if 'Nova contagem' in v.body() else None
    print('  nova contagem aberta?', J("!!document.querySelector('aside[role=dialog]')"), v.aside()[:200].replace('\n',' / '))
    v.chk('sem erro JS no fim', J("window.__err||'nenhum'")=='nenhum', J("window.__err||''"))
finally:
    v.close()
