# -*- coding: utf-8 -*-
"""SUP · Compras em 2 seções + detalhe (docs/suprimentos-simplificado §9.2, AC-SUP-01..03, 09, 10, 12, 13) · navegador, desktop 1440 e celular 390.
Lista → detalhe na fase (Cote → Decida); alçada numa linha; Ana (gerência, até R$ 300.000) não aprova acima; a Direção (Helena) abre no que
aguarda ela e decide com motivo; mudar a escolha invalida o envio (sig); pedido emitido é acompanhado e reprogramado com versões.
Uso (de gen37/, depois do build e do montar_render): python3 cmp_fila_test.py      (sai 1 se algum caso falhar)"""
import sys, os, time, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from est_lib import Est

a = Est(copiar=False); ok = a.ok; J = a.J
CMDS = r'/^(Enviar|Aprovar|Devolver|Recusar|Reenviar|Justificar|Reprogramar|Confirmar|Salvar)/'


def ir(h='', wait=1.4):
    a.c.goto('about:blank', wait=.1)   # recarrega sempre: o mesmo endereço duas vezes não dispara hashchange
    a.c.goto(f'http://127.0.0.1:{a.p}/CMP.dc.html{h}', wait=wait)
    J("window.__errs=window.__errs||[]; if(!window.__ouve){ window.__ouve=1; window.addEventListener('error',e=>window.__errs.push(e.message)); }")
    time.sleep(.4)


def reg():
    return J("(()=>{ try{ return JSON.parse(localStorage.getItem('talhao-os-compras-v1')||'null')||{}; }catch(e){ return {}; } })()") or {}


def aprov():
    return ((reg().get('proc') or {}).get('S2627') or {}).get('aprov') or {}


def prim():
    return J("(()=>{const b=[...document.querySelectorAll('.acoes-prim')].find(b=>b.offsetParent); return b?b.innerText.trim():'';})()")


def secs():
    return J("[...document.querySelectorAll('.acoes-sec,.acoes-lnk')].filter(b=>b.offsetParent).map(b=>b.innerText.trim())")


def clk_prim():
    r = J("(()=>{const b=[...document.querySelectorAll('.acoes-prim')].find(b=>b.offsetParent); if(!b) return 'sem primária'; b.click(); return 'ok';})()"); time.sleep(.6); return r


def faixa():
    return J("(document.querySelector('[aria-label=\"Situação da solicitação\"]')||{innerText:''}).innerText.replace(/\\s+/g,' ')")


def cnt():
    return J("[...document.querySelectorAll('nav[aria-label=\"Seções de compras\"] button')].map(b=>{const s=b.querySelector('.sec-cnt'); return s?s.innerText.trim():'';})")


def esperar_respostas(t=12):
    for _ in range(int(t / .5)):
        if 'Em cotação' not in faixa(): break
        time.sleep(.5)
    time.sleep(.4)


def mudar_escolha(insumo, qtd):
    J("(()=>{const b=[...document.querySelectorAll('button')].find(b=>b.offsetParent&&/^Expandir tudo/.test(b.innerText.trim())); if(b) b.click();})()"); time.sleep(.3)
    a.row(insumo); a.setv('#fx_g_cmp_ped', str(qtd)); return a.clk('Salvar escolha', 'aside[role=dialog]')


try:
    ir('', 1.8)
    # ---------- 1 · seções, lista e abertura (AC-SUP-01, 02) ----------
    nomes = J("[...document.querySelectorAll('nav[aria-label=\"Seções de compras\"] button')].map(b=>(b.querySelector('span')||b).innerText.trim())")
    ok(nomes == ['Atenda solicitações', 'Acompanhe pedidos'], '1 duas seções sem número', nomes)
    ok(a.cel('SOL-2026-07', 'Situação') == 'A cotar', '1 a lista abre com a SOL-2026-07 "A cotar"', a.cel('SOL-2026-07', 'Situação'))
    ok(cnt()[0].endswith('a mover'), '1 contador neutro da seção (Ana: o que ela move)', cnt())
    bl = J(f"[...document.querySelectorAll('main [role=row] button')].filter(b=>b.offsetParent&&{CMDS}.test(b.innerText.trim())).map(b=>b.innerText.trim())")
    ok(bl == [], '1 nenhum botão de comando em linha', bl)
    r0 = reg(); a.row('SOL-2026-07'); time.sleep(.4)
    ok('SOL-2026-07' in faixa() and 'A cotar' in faixa() and prim() == 'Enviar 15 convites (simulado)', '1 o detalhe abre na fase Cote: "Enviar 15 convites (simulado)"', [faixa()[:160], prim()])
    ok(not aprov(), '1 abrir não aprova nem emite (cmptest:128)', aprov())
    # ---------- 2 · Cote → Decida sem clique de troca ----------
    clk_prim(); esperar_respostas()
    fx = faixa(); alc = J("document.body.innerText.match(/Total R\\$ [^\\n]+/)||['']")[0]
    ok('Em cotação' not in fx and 'A cotar' not in fx and not prim().startswith('Enviar 15'), '2 as respostas chegam e a fase troca para Decida sem clique', [fx[:200], prim()])
    ok('aprova: Direção (acima de R$ 300.000,00)' in alc, '2 alçada numa linha: total, pedidos e quem aprova', alc)
    ok('PEDIDOS QUE SERÃO EMITIDOS' in a.main().upper(), '2 prévia dos pedidos visível antes do toque')
    # ---------- 3 · Ana não aprova acima da alçada; envia à Direção ----------
    p3 = prim(); body = a.main()
    ok(p3.startswith('Enviar à Direção · R$') and 'Aprovar e emitir' not in body, '3 Ana (até R$ 300.000) não vê "Aprovar e emitir"; a primária é "Enviar à Direção"', p3)
    clk_prim(); ap = aprov()
    ok(ap.get('estado') == 'pendente' and 'Aguardando Direção' in faixa() and not (reg().get('ped') or {}), '3 enviada: "Aguardando Direção", nenhum pedido emitido', [ap.get('estado'), faixa()[:120]])
    # ---------- 4 · Direção: abre no que aguarda ela; devolver exige motivo ----------
    a.perfil('Helena'); ir('', 1.6)
    ok(cnt()[0] == '1 aguardando você', '4 Helena (Direção): contador "1 aguardando você"', cnt())
    vis = J("[...document.querySelectorAll('main [role=row]')].filter(r=>r.offsetParent&&/SOL-/.test(r.innerText)).map(r=>r.innerText.replace(/\\s+/g,' '))")
    ok(vis and all('Aguardando Direção' in x for x in vis), '4 a lista abre filtrada em "Aguardando Direção"', vis)
    a.row('SOL-2026-07'); time.sleep(.4)
    ok(prim().startswith('Aprovar e emitir') and 'Devolver' in secs() and 'Recusar' in secs(), '4 detalhe da Direção: Aprovar e emitir · Devolver · Recusar', [prim(), secs()])
    a.clk('Devolver'); clk_prim()
    ok(aprov().get('estado') == 'pendente' and 'motivo' in a.main().lower(), '4 devolver sem motivo não registra', aprov().get('estado'))
    a.setv('[aria-label="Motivo da decisão"]', 'Rever prazo do MAP'); clk_prim()
    ap = aprov(); ok(ap.get('estado') == 'devolvida' and ap.get('motivo') == 'Rever prazo do MAP' and str(ap.get('decPor', '')).startswith('Helena'), '4 devolvida com motivo e quem decidiu', ap)
    # ---------- 5 · Ana ajusta (sig muda) e reenvia; Direção recusa com motivo: nada emitido ----------
    a.perfil('Ana'); ir('#sol=SOL-2026-07&saf=S2627', 1.6)
    ok(prim() == 'Ajustar escolhas' and 'Devolvida' in faixa(), '5 Ana vê "Devolvida" e "Ajustar escolhas"', [prim(), faixa()[:120]])
    r = mudar_escolha('MAP 11-52', '62000'); time.sleep(.4)
    ok(prim().startswith('Reenviar à Direção · R$'), '5 mudar a escolha troca a primária para "Reenviar à Direção"', [r, prim()])
    clk_prim(); ok(aprov().get('estado') == 'pendente', '5 reenviada', aprov().get('estado'))
    mudar_escolha('MAP 11-52', '62500'); time.sleep(.4)
    ok('reenviar à Direção (a compra mudou)' in faixa(), '5 sig: mudar depois do envio invalida o envio', faixa()[:200])
    a.perfil('Helena'); ir('#sol=SOL-2026-07&saf=S2627', 1.6)
    ok(not prim().startswith('Aprovar e emitir'), '5 a Direção não aprova um envio invalidado', prim())
    a.perfil('Ana'); ir('#sol=SOL-2026-07&saf=S2627', 1.6); clk_prim()
    a.perfil('Helena'); ir('#sol=SOL-2026-07&saf=S2627', 1.6)
    J("(()=>{const b=[...document.querySelectorAll('.acoes-lnk')].find(b=>b.offsetParent&&b.innerText.trim()==='Recusar'); if(b) b.click();})()"); time.sleep(.4)
    a.setv('[aria-label="Motivo da decisão"]', '   '); clk_prim()
    ok(aprov().get('estado') == 'pendente', '5 recusa com motivo só de espaços não registra', aprov().get('estado'))
    a.setv('[aria-label="Motivo da decisão"]', 'Preço acima do orçamento da safra'); clk_prim()
    ok(aprov().get('estado') == 'recusada' and not (reg().get('ped') or {}) and 'Recusada' in faixa(), '5 recusada com motivo: nenhum pedido emitido', [aprov().get('estado'), faixa()[:120]])
    # ---------- 6 · aprovação pela Direção emite; Acompanhe pedidos reprograma com versão ----------
    J("localStorage.removeItem('talhao-os-compras-v1')"); a.perfil('Ana'); ir('#sol=SOL-2026-07&saf=S2627', 1.8)
    clk_prim(); esperar_respostas(); clk_prim()
    a.perfil('Helena'); ir('#sol=SOL-2026-07&saf=S2627', 1.6); pa = prim(); clk_prim()
    ap = aprov(); pcs = (ap.get('emi') or {}).get('pcs') or []
    ok(pa.startswith('Aprovar e emitir') and ap.get('estado') == 'aprovada' and len(pcs) > 0 and str((ap.get('dec') or {}).get('por', '')).startswith('Helena'), '6 a Direção aprova e emite; a decisão grava Helena', [pa, ap.get('estado'), pcs])
    a.perfil('Ana'); ir('', 1.4); a.clk('Acompanhe pedidos'); time.sleep(.4)
    pc = pcs[0] if pcs else 'PC-?'
    ok(a.rowtxt(pc) != 'sem linha', f'6 {pc} aparece em Acompanhe pedidos', a.rowtxt(pc)[:120])
    a.row(pc); asd = a.aside()
    ok(f'Pedido · {pc}' in asd and f'Reprogramar {pc}' in asd, '6 painel do pedido: confirmar ou reprogramar', asd[:200])
    a.clk(f'Reprogramar {pc} ›', 'aside[role=dialog]'); a.setv('#fx_g_ped_prev', '2026-11-20'); a.setv('#fx_g_ped_obs', 'fornecedor sem caminhão')
    a.clk(f'Reprogramar {pc}', 'aside[role=dialog]'); time.sleep(.4)
    pv = ((reg().get('ped') or {}).get(pc) or {})
    ok(pv.get('prev') == '2026-11-20' and len(pv.get('prevs') or []) == 1 and (pv['prevs'][0].get('motivo') == 'fornecedor sem caminhão'), '6 reprogramar guarda a promessa anterior com o motivo', pv)
    erros = a.erros(); ok(erros == [], '— sem erro de JavaScript no desktop', erros)
    # ---------- 7 · celular 390 ----------
    a.c.size(390, 844); ir('', 1.6)
    sw = J("[document.scrollingElement.scrollWidth,window.innerWidth]")
    hd = J("[...document.querySelectorAll('main [role=columnheader]')].filter(h=>{const r=h.getBoundingClientRect(); return r.width>0&&r.left>=0&&r.right<=window.innerWidth+1;}).map(h=>h.innerText.replace(/[⇅▾▴▼▲]/g,'').trim().toUpperCase())")
    ok(sw[0] <= sw[1] + 1, '7 390 px: a página não rola de lado', sw)
    ok(any(h.startswith('SOLICITAÇÃO') for h in hd) and any(h.startswith('SITUAÇÃO') for h in hd), '7 390 px: Solicitação e Situação à vista', hd)
    a.shot('q_cmp_fila_390.png')
    erros = a.erros(); ok(erros == [], '— sem erro de JavaScript no celular', erros)
finally:
    passou = a.fim()
sys.exit(0 if passou else 1)
