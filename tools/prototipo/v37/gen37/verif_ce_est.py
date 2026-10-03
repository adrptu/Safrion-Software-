# -*- coding: utf-8 -*-
"""Verificador independente · Estoque (itens 03, 04, 07, 08): casos de borda não cobertos pelo esttest."""
import time, json
from verif_ce_lib import V
v=V('EST.dc.html'); J=v.J
def S(i,val): return v.setv('#'+i,val)
def A(): return J("(document.querySelector('aside[role=dialog]')||{innerText:''}).innerText.replace(/\\s+/g,' ')")
def rowbtn(t,b):
    r=J(f"(()=>{{const r=[...document.querySelectorAll('[role=row]')].find(r=>r.innerText.indexOf({json.dumps(t)})>=0); if(!r) return 'sem linha'; const x=[...r.querySelectorAll('button')].find(x=>x.innerText.trim()==={json.dumps(b)}); if(!x) return 'sem botão'; x.click(); return 'ok';}})()"); time.sleep(.45); return r
def editaveis(): return J("document.querySelectorAll('aside[role=dialog] input:not([readonly]):not([disabled]), aside[role=dialog] select:not([disabled]), aside[role=dialog] textarea:not([readonly]):not([disabled])').length")
try:
    v.open(); v.chk('sem erro JS', J("window.__err||'nenhum'")=='nenhum', J("window.__err||''"))
    # ---------- item 07: validade ----------
    v.clk('Registrar recebimento')
    v.chk('novo: PC-088 (fertilizante) → Sem validade travado', J("document.querySelector('#fx_g_rec_val').value")=='Sem validade' and J("document.querySelector('#fx_g_rec_val').readOnly||document.querySelector('#fx_g_rec_val').disabled"))
    peds=J("[...document.querySelectorAll('#fx_g_rec_ped option')].map(o=>o.value)"); print('  pedidos:', peds)
    p90=[x for x in peds if x.startswith('PC-090')][0]; p91=[x for x in peds if x.startswith('PC-091')][0]
    S('fx_g_rec_ped',p91); v.chk('troca para PC-091 (semente): validade editável e vazia', J("document.querySelector('#fx_g_rec_val').value")=='' and not J("document.querySelector('#fx_g_rec_val').readOnly||document.querySelector('#fx_g_rec_val').disabled"))
    S('fx_g_rec_nf','NF 7001'); S('fx_g_rec_qtd_nf','1000'); S('fx_g_rec_conf','1000'); S('fx_g_rec_apto','1000'); S('fx_g_rec_quar','0'); S('fx_g_rec_lote','S62-0930'); S('fx_g_rec_local','Câmara fria')
    for bad in ['6/2027','06/27','00/2027','2027-06','06-2027']:
        S('fx_g_rec_val',bad); v.clk('Salvar','aside[role=dialog]'); e=v.errs(); v.chk(f'validade "{bad}" recusada', 'mês/ano' in e.lower() or 'Use mês/ano' in e, e)
    S('fx_g_rec_val','09/2026'); v.clk('Salvar','aside[role=dialog]'); e=v.errs(); print('  validade no mês corrente (09/2026):', e or 'salvou', '|', v.T())
    v.chk('validade do mês corrente aceita com apta > 0', not J("!!document.querySelector('aside[role=dialog]')"), e)
    # lote vencido: tudo em quarentena com motivo
    v.clk('Registrar recebimento'); S('fx_g_rec_ped',p91); S('fx_g_rec_nf','NF 7002'); S('fx_g_rec_qtd_nf','500'); S('fx_g_rec_conf','500'); S('fx_g_rec_apto','0'); S('fx_g_rec_quar','500')
    S('fx_g_rec_lote','S62-0801'); S('fx_g_rec_local','Câmara fria'); S('fx_g_rec_val','08/2026'); v.clk('Salvar','aside[role=dialog]'); e=v.errs()
    v.chk('vencido com apta 0 e sem motivo: pede motivo', 'motivo' in e.lower(), e)
    S('fx_g_rec_obs','Lote vencido: devolver ao fornecedor'); v.clk('Salvar','aside[role=dialog]'); print('  vencido salvo:', v.T())
    v.chk('vencido com apta 0 e motivo: salva', not J("!!document.querySelector('aside[role=dialog]')"), v.errs())
    # FEFO: NF 4533 com validade anterior à do lote antigo → lote novo vem primeiro
    v.row('NF 4533'); S('fx_g_rec_conf','20000'); S('fx_g_rec_apto','20000'); S('fx_g_rec_quar','0'); S('fx_g_rec_val','01/2027'); v.clk('Salvar','aside[role=dialog]'); print('  NF 4533:', v.T(), v.errs())
    # receber em lote já existente com validade diferente
    v.clk('Registrar recebimento'); S('fx_g_rec_ped',p90); S('fx_g_rec_nf','NF 7003'); S('fx_g_rec_qtd_nf','1000'); S('fx_g_rec_conf','1000'); S('fx_g_rec_apto','1000'); S('fx_g_rec_quar','0')
    S('fx_g_rec_lote','S58-0801'); S('fx_g_rec_local','Câmara fria'); S('fx_g_rec_val','03/2027'); S('fx_g_rec_div','Sobra'); S('fx_g_rec_obs','sobra de 1 t na carga'); v.clk('Salvar','aside[role=dialog]'); e=v.errs(); print('  lote existente com outra validade:', e or 'salvou sem aviso', '|', v.T())
    v.chk('lote existente (06/2027) recebido com validade 03/2027: aviso ou erro', bool(e), 'salvou sem aviso: '+v.T())
    if J("!!document.querySelector('aside[role=dialog]')"): v.clk('Cancelar','aside[role=dialog]'); v.clk('Descartar','aside[role=dialog]')
    v.clk('4 Confira saldos'); v.clk('Expandir tudo')
    t=v.rowtxt('S62-0930'); v.chk('lote S62-0930 validade 09/2026', '09/2026' in t, t)
    t=v.rowtxt('S62-0801'); v.chk('lote vencido S62-0801: tudo em quarentena, disponível 0', '500 kg' in t and '08/2026' in t and t.count('0 kg')>=1, t)
    t=v.rowtxt('S58-0801'); print('  S58-0801 após receber 03/2027:', t)
    v.row('S58-0801'); og=A(); print('  origem S58-0801:', og[-260:]); v.clk('Fechar','aside[role=dialog]')
    v.clk('2 Entregue por O.S.')
    v.row('REQ-036'); a=A(); lv=J("(document.querySelector('#fx_g_ent_lote')||{value:''}).value"); print('  REQ-036 lote padrão (FEFO):', lv)
    v.chk('FEFO: REQ-036 sugere o lote S58-0926 (01/2027) antes do S58-0801 (06/2027)', lv.startswith('S58-0926'), lv)
    # ---------- item 04 ----------
    print('  REQ-036 subtítulo:', a[:330])
    v.chk('REQ-036: subtítulo sem ponto duplo', '..' not in a.split('Salvar')[0], a[:330])
    v.chk('REQ-036: só consulta', editaveis()==0, editaveis())
    v.clk('Fechar','aside[role=dialog]')
    t=v.rowtxt('REQ-036'); v.chk('REQ-036 linha: Bloqueada + selo + motivo', 'Bloqueada' in t and 'O.S. impedida · OM-0233' in t and 'Trator T1' in t, t)
    k2=J("document.querySelector('main').innerText.split('\\n').find(l=>/requisiç/.test(l))||''"); print('  k2:', k2)
    v.chk('k2 conta 2 bloqueadas (REQ-036 e REQ-038)', '2 bloqueadas' in k2, k2)
    # ---------- item 03 ----------
    t=v.rowtxt('REQ-031'); v.chk('REQ-031: selo conferência e sem negrito de ação', 'O.S. em conferência · sem nova entrega' in t, t)
    v.row('REQ-031'); a=A(); v.chk('REQ-031: subtítulo explica sem nova entrega', 'sem nova entrega' in a and editaveis()==0, a[:200]); v.clk('Fechar','aside[role=dialog]')
    v.row('REQ-035'); a=A(); v.chk('REQ-035: ajuda com a conta 15 L', 'A entregar: 15 L = 175 L solicitado − 95 L consumido − 65 L em custódia.' in a, a[:400])
    S('fx_g_ent_qtd','15,5'); v.clk('Salvar','aside[role=dialog]'); e=v.errs(); v.chk('15,5 L: erro com a conta', 'Acima do saldo a entregar: 15 L (175 L solicitado − 95 L consumido − 65 L em custódia).' in e, e)
    S('fx_g_ent_qtd','15'); v.clk('Salvar','aside[role=dialog]'); print('  entrega 15:', v.T())
    t=v.rowtxt('REQ-035'); v.chk('REQ-035 completa após 15 L', 'Entrega completa' in t, t)
    p=v.prim(); print('  primária etapa 2:', p)
    # devolução em quarentena também reabre o saldo, mas o lote não tem o disponível
    v.clk('3 Receba devoluções'); v.row('REQ-035'); S('fx_g_dev_qtd','20'); S('fx_g_dev_cond','Embalagem aberta · quarentena'); S('fx_g_dev_obs','tampa rompida'); v.clk('Salvar','aside[role=dialog]'); print('  dev quarentena:', v.T())
    v.clk('2 Entregue por O.S.'); t=v.rowtxt('REQ-035'); print('  REQ-035 após devolver 20 L em quarentena:', t)
    v.chk('saldo reaberto: 20 L a entregar', '20 L' in t, t)
    # ---------- item 08 ----------
    v.clk('5 Faça contagens')
    v.clk('Filtrar Sistema na data de corte') if False else None
    fm=J("(()=>{const b=[...document.querySelectorAll('button')].find(b=>(b.getAttribute('aria-label')||'')==='Filtrar Sistema na data de corte'); if(!b) return 'sem'; b.click(); return 'ok';})()"); time.sleep(.4)
    menu=J("document.body.innerText"); v.chk('filtro da coluna Sistema não revela o saldo da contagem a fazer', '1.200' not in menu.split('Contagens',1)[-1] or 'oculto até contar' in menu, fm)
    J("(()=>{const b=[...document.querySelectorAll('button')].find(b=>(b.getAttribute('aria-label')||'')==='Filtrar Sistema na data de corte'); if(b) b.click();})()"); time.sleep(.3)
    v.row('INV-2609'); a=A(); v.chk('INV-2609 (diferença salva): quantidade e contador travados, causa editável',
        J("document.querySelector('#fx_g_cnt_cont').readOnly||document.querySelector('#fx_g_cnt_cont').disabled") and J("document.querySelector('#fx_g_cnt_contador').disabled") and not J("document.querySelector('#fx_g_cnt_causa').readOnly||document.querySelector('#fx_g_cnt_causa').disabled"), a[:200])
    v.clk('Fechar','aside[role=dialog]')
    print('  recontar INV-2609:', rowbtn('INV-2609','Recontar'), v.T())
    ct=J("document.querySelector('#fx_g_cnt_contador').value"); v.chk('recontagem pré-preenche o outro contador (Rui fez a anterior)', ct.startswith('Paula'), ct)
    a=A(); v.chk('recontagem cega: sem 90.000 e sem 89.400 no formulário', '90.000' not in a and '89.400' not in a, a[:300])
    t=v.rowtxt('INV-2609'); v.chk('linha volta a oculto até contar', 'oculto até contar' in t and '90.000' not in t, t)
    v.clk('Cancelar','aside[role=dialog]'); v.clk('Descartar','aside[role=dialog]')
    t=v.rowtxt('INV-2609'); print('  depois de cancelar a recontagem:', t)
    p=v.prim(); print('  primária:', p)
    v.row('INV-2609'); S('fx_g_cnt_cont','89400'); v.clk('Salvar','aside[role=dialog]'); print('  recontagem 89.400:', v.T(), v.errs())
    t=v.rowtxt('INV-2609'); v.chk('recontagem salva com a mesma diferença', '−600' in t and 'Recontar' in t, t)
    v.row('INV-2609'); a=A(); v.chk('origem mostra a contagem anterior com a causa', 'Contagem anterior: 89.400 kg por Rui (conferente)' in a and 'Sacaria rasgada' in a, a[-300:])
    v.chk('causa limpa na recontagem: pede de novo', J("document.querySelector('#fx_g_cnt_causa').value")=='', J("document.querySelector('#fx_g_cnt_causa').value"))
    v.clk('Fechar','aside[role=dialog]')
    # nova contagem: saldo não aparece antes de salvar
    v.clk('+ Nova contagem') if 'Nova contagem' in v.body() else None
    if not J("!!document.querySelector('aside[role=dialog]')"): print('  (sem botão Nova contagem visível)', v.prim())
    else:
        a=A(); v.chk('nova contagem: formulário sem saldo do sistema', 'Sistema' not in a and '1.200' not in a, a[:300]); v.clk('Cancelar','aside[role=dialog]')
    v.shot('ce_est_e5.png')
    v.chk('sem erro JS no fim', J("window.__err||'nenhum'")=='nenhum', J("window.__err||''"))
finally:
    v.close()
