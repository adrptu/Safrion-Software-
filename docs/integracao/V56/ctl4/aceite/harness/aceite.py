# -*- coding: utf-8 -*-
"""Aceite CTL-4-FIX na candidata V56 (acordo com o Codex, comentários 6133716339 e 6133809632 do PR #47), pela tela.
Cada cenário começa com o armazenamento limpo e o perfil de demonstração Ana; os comandos são os das próprias telas (Estoque, O.S.),
salvo a pré-condição do A11 (apontamento da OS-0421 pelo comando da página da O.S., como no demanda_estado_nav_test A7).
Saída: valores antes/depois em JSON (OUTJ), capturas em OUTD, log em LOGF. Uso:
  env GEN=<gen37> OUTD=<capturas> LOGF=<log> OUTJ=<json> python3 aceite.py"""
import os, sys, json, time, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from navlib import Nav, log
from est_lib import FIND
n = Nav(); J = n.J; V = {}
ROWD = """((nome)=>{const n=s=>(s||'').replace(/\\s+/g,' ').trim(); const out=[];
  [...document.querySelectorAll('[role=table]')].filter(t=>t.offsetParent).forEach(t=>{
    const hs=[...t.querySelectorAll('[role=columnheader]')].map(h=>n(h.innerText.replace(/[⇅▾▴▼▲]/g,'')).replace(/ · \\d+$/,''));
    [...t.querySelectorAll('[role=row]')].forEach(r=>{ const cs=[...r.querySelectorAll('[role=cell]')]; if(!cs.length) return;
      if(!cs.some(cx=>n(cx.innerText).startsWith(nome))) return; const o={}; cs.forEach((cx,i)=>{ o[hs[i]||('col'+i)]=n(cx.innerText); }); out.push(o); }); });
  return out;})"""
rowd = lambda nome: (J(f"({ROWD})({json.dumps(nome)})") or [])
def reset():
    n.ir('SAF.dc.html', w=1.0); J("localStorage.clear(); sessionStorage.clear(); localStorage.setItem('safrion.perfilDemo','Ana')")
def memo(nome, shot=None):
    J(f"(()=>{{const r=({FIND})([{json.dumps(nome)}]); if(!r) return; r.scrollIntoView({{block:'center'}}); (r.querySelector('[role=cell] b')||r.querySelector('[role=cell] span')||r).click();}})()"); time.sleep(.7)
    if shot: n.foto(shot)
    t = (J("(document.querySelector('aside[role=dialog]')||{innerText:''}).innerText") or '').split('\n'); t = [x.strip() for x in t if x.strip()]
    n.clk('Fechar', 'aside[role=dialog]', w=.4); J("document.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true}))"); time.sleep(.3)
    i = next((k for k, x in enumerate(t) if x == 'ORIGEM'), -1)
    return t[i + 1:] if i >= 0 else t[:40]
def saf(nomes, s='S2627', shot=None, memos=True, mshot=None):
    n.saf(s); o = dict(total=n.k6(), prim=n.prim(), linhas={x: (rowd(x) or [{}])[0] for x in nomes})
    if shot: n.foto(shot)
    if memos: o['memo'] = {x: memo(x, (mshot if (mshot and x == nomes[0]) else None)) for x in nomes}
    return o
def cmp(nomes, shot=None, memos=True, mshot=None):
    n.ir('CMP.dc.html#sol=SOL-2026-07&saf=S2627', w=1.8)
    if not J("[...document.querySelectorAll('button')].some(b=>b.offsetParent&&b.innerText.trim()==='Recolher tudo')"): n.clk('Expandir tudo', w=.7)
    k2 = J("(document.body.innerText.match(/SOL-2026-07 · Safra[^\\n]*/)||[''])[0]") or ''
    o = dict(k2=k2, tot=J("[...document.querySelectorAll('.g2tot')].filter(x=>x.offsetParent).map(x=>x.innerText.replace(/\\s+/g,' ').trim())"), prim=n.prim(),
             linhas={x: (rowd(x) or [{}])[0] for x in nomes})
    if shot: n.foto(shot)
    if memos: o['memo'] = {x: memo(x, (mshot if (mshot and x == nomes[0]) else None)) for x in nomes}
    return o
def mapa(tal, prods, shot=None):
    J(f"sessionStorage.setItem('mapa-ctx',{json.dumps(json.dumps({'mf_faz':'Santa Rita','lay':'Insumos','tsel':[],'flt':{'Insumos':{'per':'Safra toda'}}}))})"); n.ir('IN-04.dc.html', w=2.2)
    n.tap(tal); x = n.pan(tal)
    if shot: n.foto(shot)
    n.tap(tal); out = {}
    for p in prods:
        k = x.find(p, max(0, x.find('compartilhado da fazenda')))
        out[p] = x[k:k + 420] if k >= 0 else '(produto não aparece no painel)'
    return out
def pt(nomes):
    n.ir('PT-02det.dc.html', w=1.6)
    return dict(total=(J("(document.body.innerText.match(/Total[^\\n]*/)||[''])[0]") or ''), linhas={x: (rowd(x) or [{}])[0] for x in nomes})
def est_saldo(prod):
    n.est_secao(4); J("(()=>{const b=[...document.querySelectorAll('button')].find(b=>b.offsetParent&&b.innerText.trim()==='Expandir tudo'); b&&b.click();})()"); time.sleep(.6)
    return rowd(prod)
def cen(expr): return n.cen(expr)
def nf4533(conf, apto, quar, val, div, obs):
    n.est_secao(1); a = n.clk('Conferir NF 4533', w=.6)
    for k, v in (('#fx_g_rec_conf', conf), ('#fx_g_rec_apto', apto), ('#fx_g_rec_quar', quar), ('#fx_g_rec_val', val), ('#fx_g_rec_div', div), ('#fx_g_rec_obs', obs)):
        if v is not None: n.setv(k, v)
    n.clk('Salvar', 'aside[role=dialog]', w=.9); return a, n.T()
def laudo(acao, num, mot=''):
    n.est_secao(4); J(f"(()=>{{const r=({FIND})(['S58-0926']); if(!r) return; const b=[...r.querySelectorAll('button')].find(b=>/Liberar após inspeção/.test(b.innerText)); b&&b.click();}})()"); time.sleep(.5)
    n.setv('#est-laudo', num); n.setv('#est-laudo-mot', mot); r = n.clk(acao, '[role=group][aria-label="Liberar quarentena com laudo"]', w=.8); return r, n.T()
SEM = 'Semente de soja 58 W'; MAP = 'MAP 11-52'; NPK = 'NPK 20-05-20'; FA = 'Fungicida A'
CEN_MAP = "{req031:c.reqs['REQ-031'].itens.map(i=>({prod:i.prod,entregue:i.entregue,consumido:i.consumido,devolvido:i.devolvido,custodia:i.custodia})),os0417:c.ordens['OS-0417'].etapa,lotes:Object.values(c.lotes).filter(l=>l.prod==='MAP 11-52').map(l=>({lote:l.lote,fisico:l.fisico,reservado:l.reservado,quarentena:l.quarentena}))}"
CEN_SEM = "{lotes:Object.values(c.lotes).filter(l=>l.prod==='Semente de soja 58 W').map(l=>({lote:l.lote,fisico:l.fisico,quarentena:l.quarentena,quarRep:l.quarRep||0,rep:l.rep||null})),movs:(c.movs||[]).filter(m=>m.prod==='Semente de soja 58 W').map(m=>({tipo:m.tipo,qtd:m.qtd,apto:m.apto,doc:m.doc,obs:m.obs||(m.estRec&&m.estRec.obs)||''}))}"
CEN_NPK = "{os0425:{etapa:c.ordens['OS-0425'].etapa,osc:c.ordens['OS-0425'].osc||null},req040:{estado:c.reqs['REQ-040'].estado,itens:c.reqs['REQ-040'].itens.map(i=>({prod:i.prod,entregue:i.entregue,custodia:i.custodia,devolvido:i.devolvido}))},lote:c.lotes['NPK 20-05-20|N26-03']}"
try:
    log('GEN=', os.environ['GEN']); n.c.size(1440, 1000)
    # ============ 1 · devolução REQ-031 (500 kg de MAP 11-52, OS-0417 em conferência) ============
    reset(); I1 = {}
    I1['antes'] = dict(cen=cen(CEN_MAP), saf=saf([MAP], shot='i1_saf_antes', mshot='i1_saf_memo_antes'), cmp=cmp([MAP]), mapa=mapa('T4', [MAP]), pt=pt([MAP]), est=est_saldo(MAP))
    n.est_secao(3); I1['linha'] = n.est_row('REQ-031', MAP); I1['set'] = n.setv('#fx_g_dev_qtd', '500'); n.clk('Salvar', 'aside[role=dialog]', w=.9); I1['recibo'] = n.T()
    I1['depois'] = dict(cen=cen(CEN_MAP), saf=saf([MAP], shot='i1_saf_depois', mshot='i1_saf_memo_depois'), cmp=cmp([MAP], shot='i1_cmp_depois', mshot='i1_cmp_memo_depois'), mapa=mapa('T4', [MAP]), pt=pt([MAP]), est=est_saldo(MAP))
    V['item1'] = I1; log('ITEM 1:', json.dumps(I1, ensure_ascii=False)[:3000])
    # ============ 2 · NF 4533 / PC-090 com 20.000 kg em quarentena; laudo liberado; laudo reprovado ============
    reset(); I2 = {}
    I2['antes'] = dict(cen=cen(CEN_SEM), saf=saf([SEM]), cmp=cmp([SEM]), mapa=mapa('T4', [SEM]))
    I2['nf'] = nf4533('20000', '0', '20000', '06/2027', None, 'Aguarda laudo de germinação (aceite CTL-4-FIX)')
    I2['quar'] = dict(cen=cen(CEN_SEM), saf=saf([SEM], shot='i2_saf_quarentena', mshot='i2_saf_memo_quarentena'), cmp=cmp([SEM], shot='i2_cmp_quarentena', mshot='i2_cmp_memo_quarentena'),
                      mapa=mapa('T4', [SEM], shot='i2_mapa_t4_quarentena'), pt=pt([MAP, SEM]))
    I2['lib'] = laudo('Liberar com o laudo', 'LAB-1')
    I2['liberado'] = dict(cen=cen(CEN_SEM), saf=saf([SEM], shot='i2_saf_laudo_liberado'), cmp=cmp([SEM]), mapa=mapa('T4', [SEM]))
    reset(); I2['nf2'] = nf4533('20000', '0', '20000', '06/2027', None, 'Aguarda laudo de germinação (aceite CTL-4-FIX)')
    I2['rep'] = laudo('Reprovar com o laudo', 'LAB-2', 'germinação 71%')
    I2['reprovado'] = dict(cen=cen(CEN_SEM), saf=saf([SEM], shot='i2_saf_laudo_reprovado', mshot='i2_saf_memo_reprovado'), cmp=cmp([SEM], shot='i2_cmp_laudo_reprovado'), mapa=mapa('T4', [SEM]))
    V['item2'] = I2; log('ITEM 2:', json.dumps(I2, ensure_ascii=False)[:3000])
    # ============ 3 · entregar 8.000 kg de NPK (REQ-040), cancelar a OS-0425 (Ana, motivo), devolver; A11 da OS-0421 ============
    reset(); I3 = {}
    I3['antes'] = dict(cen=cen(CEN_NPK), saf=saf([NPK], memos=False), cmp=cmp([NPK], memos=False), mapa=mapa('C1', [NPK]))
    n.est_secao(2); I3['ent_linha'] = n.est_row('REQ-040', NPK); I3['ent_qtd'] = J("(document.querySelector('#fx_g_ent_qtd')||{}).value"); n.clk('Salvar', 'aside[role=dialog]', w=.9); I3['ent_recibo'] = n.T()
    I3['entregue'] = dict(cen=cen(CEN_NPK), saf=saf([NPK], memos=False), cmp=cmp([NPK], memos=False), mapa=mapa('C1', [NPK]))
    n.os_painel('OS-0425'); I3['canc_btn'] = n.clk('Cancelar sem execução', 'aside[role=dialog]'); I3['canc_confirma_txt'] = (J("(document.querySelector('aside[role=dialog]')||{innerText:''}).innerText") or '').replace('\n', ' · ')
    n.motivo('Talhão replanejado (aceite CTL-4-FIX)'); I3['canc_ok'] = n.clk('Confirmar cancelamento', 'aside[role=dialog]', w=.9); I3['canc_recibo'] = n.T()
    n.ir('OS.dc.html', w=1.6); n.clk('Canceladas', w=.6)
    J("(()=>{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.trim().startsWith('OS-0425')); r&&r.click();})()"); time.sleep(.7)
    I3['os_cancelada_painel'] = (J("(document.querySelector('aside[role=dialog]')||{innerText:''}).innerText") or '').replace('\n', ' · '); n.foto('i3_os0425_cancelada_custodia')
    I3['os_cancelada_links'] = J("[...document.querySelectorAll('aside[role=dialog] a')].map(a=>a.innerText.trim()+'>'+a.getAttribute('href'))")
    I3['cancelada'] = dict(cen=cen(CEN_NPK), saf=saf([NPK], memos=False, shot='i3_saf_cancelada'), cmp=cmp([NPK], memos=False), mapa=mapa('C1', [NPK]))
    n.est_secao(3); I3['dev_linha'] = n.est_row('REQ-040', NPK); n.setv('#fx_g_dev_qtd', '8000'); n.clk('Salvar', 'aside[role=dialog]', w=.9); I3['dev_recibo'] = n.T()
    I3['devolvida'] = dict(cen=cen(CEN_NPK), saf=saf([NPK], memos=False), cmp=cmp([NPK], memos=False, shot='i3_cmp_devolvida'), mapa=mapa('C1', [NPK]))
    # A11: OS-0421 aponta 150 ha com 20 L (comando da página da O.S.), depois Estoque › devolução de 40 L da REQ-035 (apta)
    reset(); A = {}
    A['antes'] = dict(s2627=saf([FA], memos=False), s27sf=saf([FA], 'S27SF', memos=False))
    n.ir('OS.dc.html', w=1.6)
    A['apontar'] = J("(()=>{ const X=window.__cen; const r=X.cenMudar(null,c=>X.osc_apontar(c,'OS-0421','26/09',150,{'Fungicida A':20,'Adjuvante espalhante':0},[],'W-A11')); return r.erro||r.msg||'ok'; })()")
    A['cen_apontado'] = cen("{req035:c.reqs['REQ-035'].itens.map(i=>({prod:i.prod,entregue:i.entregue,consumido:i.consumido,custodia:i.custodia,devolvido:i.devolvido})),os:c.ordens['OS-0421'].etapa}")
    A['apontado'] = dict(s2627=saf([FA], memos=False), s27sf=saf([FA], 'S27SF', memos=False))
    n.est_secao(3); A['dev_linha'] = n.est_row('REQ-035', FA); A['dev_set'] = n.setv('#fx_g_dev_qtd', '40'); n.clk('Salvar', 'aside[role=dialog]', w=.9); A['dev_recibo'] = n.T()
    A['cen_devolvido'] = cen("{req035:c.reqs['REQ-035'].itens.map(i=>({prod:i.prod,entregue:i.entregue,consumido:i.consumido,custodia:i.custodia,devolvido:i.devolvido})),lotes:Object.values(c.lotes).filter(l=>l.prod==='Fungicida A').map(l=>({lote:l.lote,fisico:l.fisico}))}")
    A['devolvido'] = dict(s2627=saf([FA], memos=False), s27sf=saf([FA], 'S27SF', memos=False, shot='i3_a11_saf_s27sf_devolvido'))
    I3['A11'] = A
    V['item3'] = I3; log('ITEM 3:', json.dumps(I3, ensure_ascii=False)[:3000])
    # ============ 4 · projeção datada dos recebimentos ============
    reset(); I4 = {}
    P = ['KCl 60%', 'Semente de soja 62 X', SEM]
    I4['semente'] = dict(saf=saf(P, mshot='i4_saf_memo_kcl'), cmp=cmp(P))
    I4['nf_parcial'] = nf4533('12000', '12000', '0', '06/2027', 'Falta', 'Entrega parcial: 8.000 kg seguem no PC-090 (aceite CTL-4-FIX)')
    I4['parcial'] = dict(cen=cen(CEN_SEM), saf=saf(P, mshot='i4_saf_memo_kcl_parcial'), cmp=cmp(P))
    V['item4'] = I4; log('ITEM 4:', json.dumps(I4, ensure_ascii=False)[:3000])
    V['erros_js'] = n.erros()
finally:
    try: n.close()
    finally: json.dump(V, open(os.environ['OUTJ'], 'w'), ensure_ascii=False, indent=1)
