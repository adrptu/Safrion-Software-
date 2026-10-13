# -*- coding: utf-8 -*-
"""SUP · Estoque em 4 seções (docs/suprimentos-simplificado §9.2, AC-SUP-01..05, 08, 12, 16) · navegador, desktop 1440 e celular 390/360.
Cada papel abre no que tem de fazer; o painel do registro resolve (entregar inteira, devolução, consumo, laudo, contagem cega); navegar não grava.
Uso (de gen37/, depois do build): python3 est_fila_test.py      (sai 1 se algum caso falhar)"""
import sys, os, time, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from est_lib import Est

SECOES = ['Atenda requisições', 'Receba e inspecione', 'Faça contagens', 'Confira saldos']
CMDS = r'/^(Entregar|Receber|Registrar|Conciliar|Aceitar|Aprovar|Liberar|Contar|Recusar|Salvar|Enviar|Manter)/'
a = Est(); ok = a.ok
J = a.J


def estado():
    return a.cen("[c.rev,(c.movs||[]).length]")


def ir(h, wait=1.2):
    a.c.goto('about:blank', wait=.1)   # recarrega sempre: o mesmo endereço duas vezes não dispara hashchange
    a.c.goto(f'http://127.0.0.1:{a.p}/EST.dc.html{h}', wait=wait)
    a.J("window.__errs=window.__errs||[]; if(!window.__ouve){ window.__ouve=1; window.addEventListener('error',e=>window.__errs.push(e.message)); }")
    time.sleep(.5)


def cnt():
    return J("[...document.querySelectorAll('nav[aria-label=\"Seções do estoque\"] button')].map(b=>{const s=b.querySelector('.sec-cnt'); return s?s.innerText.trim():'';})")


def titulo():
    return J("(document.querySelector('aside[role=dialog] h2,aside[role=dialog] [role=heading]')||document.querySelector('aside[role=dialog]')||{innerText:''}).innerText.split('\\n')[0].trim()")


def prim_painel():
    """Primária do painel (última ação do rodapé do aside: Cancelar · <primária>)."""
    return J("(()=>{const a=document.querySelector('aside[role=dialog]'); if(!a) return ''; const b=[...a.querySelectorAll('button')].filter(b=>b.offsetParent&&!/^(Cancelar|Fechar|×)$/.test(b.innerText.trim())&&getComputedStyle(b).backgroundColor==='rgb(30, 122, 76)'); return b.length?b[b.length-1].innerText.trim():'';})()")


def clk_prim():
    return J("(()=>{const a=document.querySelector('aside[role=dialog]'); const b=[...a.querySelectorAll('button')].filter(b=>b.offsetParent&&getComputedStyle(b).backgroundColor==='rgb(30, 122, 76)'); if(!b.length) return 'sem primária'; b[b.length-1].click(); return 'ok';})()")


def prim_dentro():
    """A primária do painel cabe no painel e recebe o toque: inteira dentro do aside (rótulo longo quebra linha, não vaza para fora) e o ponto
    de toque (centro e começo do botão) cai nela, não no fundo da gaveta. Defeito do roteiro do BEN (R6, 09/10): "COBERTO … por BUTTON"."""
    return J("(()=>{const a=document.querySelector('aside[role=dialog]'); if(!a) return 'sem painel'; const b=[...a.querySelectorAll('button')].filter(b=>b.offsetParent&&getComputedStyle(b).backgroundColor==='rgb(30, 122, 76)').pop(); if(!b) return 'sem primária';"
             " b.scrollIntoView({block:'center'}); const ra=a.getBoundingClientRect(), rb=b.getBoundingClientRect(); const hit=(x,y)=>{ const e=document.elementFromPoint(x,y); return !!e&&(e===b||b.contains(e)); };"
             " const y=rb.top+rb.height/2; return {dentro:rb.left>=ra.left-1&&rb.right<=ra.right+1&&rb.left>=0&&rb.right<=innerWidth+1, centro:hit(rb.left+rb.width/2,y), inicio:hit(rb.left+12,y), w:Math.round(rb.width), aw:Math.round(ra.width)};})()")


def botoes_em_linha():
    return J(f"[...document.querySelectorAll('main [role=row] button')].filter(b=>b.offsetParent&&{CMDS}.test(b.innerText.trim())).map(b=>b.innerText.trim())")


try:
    ir('', 1.6)
    # ---------- 1 · seções e contadores (AC-SUP-01, 02, 16) ----------
    nomes = J("[...document.querySelectorAll('nav[aria-label=\"Seções do estoque\"] button')].map(b=>(b.querySelector('span')||b).innerText.trim())")
    ok(nomes == SECOES, '1 quatro seções sem número: ' + ' · '.join(SECOES), nomes)
    ok(J("!document.querySelector('[aria-label*=\"Etapas\"]')") and not any(n[:1].isdigit() for n in nomes), '1 nenhuma faixa de etapas numeradas')
    c0 = cnt()
    # "2 notas" desde o merge do BEN rodada 1 (BEN-D23): a NF 7731 das caixas do Packing (Santa Rita) espera a conferência
    ok(c0[:3] == ['3 a entregar · 1 sobra', '2 notas · 1 laudo', '1 a contar · 1 ajuste'], '1 contadores neutros da Santa Rita', c0)
    ok(J("[...document.querySelectorAll('nav[aria-label=\"Seções do estoque\"] .sec-cnt')].every(s=>getComputedStyle(s).color!=='rgb(185, 28, 28)')"), '1 contador neutro (não vermelho)')
    a.fazenda('Lagoa Grande'); a.ir_secao('Atenda requisições')
    ok(cnt()[0] == '1 a entregar' and a.rowtxt('REQ-021') != 'sem linha' and a.rowtxt('REQ-039') == 'sem linha', '1 Lagoa Grande: "1 a entregar", REQ-021 na fila e REQ-039 fora', [cnt(), a.rowtxt('REQ-021')[:60]])
    a.fazenda('Todas'); ok(cnt()[0] == '4 a entregar · 1 sobra', '1 Todas soma as fazendas: "4 a entregar · 1 sobra"', cnt())
    a.fazenda('Boa Vista'); ok('Nenhum estoque na Boa Vista' in a.main(), '1 Boa Vista: estado vazio com "Ver Santa Rita"')
    a.clk('Ver Santa Rita'); ok(J("document.querySelector('[aria-label=\"Filtrar por fazenda\"]').value") == 'Santa Rita', '1 "Ver Santa Rita" volta ao filtro')
    # ---------- 2 · abertura pelo perfil (Ver como) sem gravar (AC-SUP-02) ----------
    e0 = estado(); ir('', 1.4)
    ab = {}
    ab['Ana'] = a.secao()
    a.perfil('Rui'); ab['Rui'] = a.secao()
    a.perfil('Paula'); ab['Paula'] = a.secao()
    ok(ab == {'Ana': 'Receba e inspecione', 'Rui': 'Atenda requisições', 'Paula': 'Faça contagens'}, '2 abre pelo papel: Ana → Receba e inspecione (laudo), Rui → Atenda requisições, Paula → Faça contagens (INV-2611)', ab)
    ok(estado() == e0, '2 Ver como não muda c.rev nem os movimentos', [e0, estado()])
    # ---------- 3 · endereços (AC-SUP-03): abrem o lugar certo e não executam ----------
    a.perfil('Rui'); e0 = estado()
    ir('#req=REQ-031'); r31 = (a.secao(), a.aberto(), a.aside())
    ok(r31[0] == 'Atenda requisições' and r31[1] and 'REQ-031' in r31[2] and 'Devolução' in r31[2], '3 #req=REQ-031 abre o painel da sobra (Devolução)', r31[2][:120])
    ir('#sec=xyz'); ok(a.erros() == [] and a.secao() in SECOES, '3 #sec=xyz abre sem erro', a.erros())
    ir('#sec=recebimentos'); ok(a.secao() == 'Receba e inspecione', '3 apelido #sec=recebimentos → Receba e inspecione', a.secao())
    ir('#sec=movimentos'); ok(a.secao() == 'Confira saldos' and 'Cada movimento do estoque' in a.main(), '3 apelido #sec=movimentos → Confira saldos › Movimentos')
    ir('#lote=K26-11'); ok(a.secao() == 'Confira saldos' and 'K26-11' in a.aside(), '3 #lote=K26-11 abre o lote em Confira saldos', a.aside()[:80])
    ir('#nf=NF 4501'); ok(a.secao() == 'Receba e inspecione' and 'Parcela NF 4501' in a.aside(), '3 #nf=NF 4501 abre a parcela em quarentena', a.aside()[:80])
    ir('#os=OS-0420'); ok('REQ-036' in a.aside() and 'impedida' in a.aside().lower(), '3 #os=OS-0420 abre a REQ-036 (O.S. impedida, só consulta)', a.aside()[:160])
    ok(estado() == e0, '3 navegar não executa: c.rev e c.movs iguais', [e0, estado()])
    # ---------- 4 · nenhum comando dentro de linha (AC-SUP-13) ----------
    ir('', 1.2); a.fazenda('Todas'); bl = []
    for s in SECOES:
        a.ir_secao(s); bl += botoes_em_linha()
    a.clk('Movimentos'); bl += botoes_em_linha()
    ok(bl == [], '4 nenhum botão de comando em [role=row] (requisições, notas, contagens, lotes, movimentos)', bl)
    # ---------- 5 · Entregar REQ-021 a Renato em 2 toques, "Separe:" antes do toque (AC-SUP-04) ----------
    ir('', 1.2); a.fazenda('Lagoa Grande'); a.ir_secao('Atenda requisições')
    a.row('REQ-021'); asd = a.aside(); pr = prim_painel()
    ok('Separe:' in asd and 'LG26-05' in asd and '1.850 bandejas de 50 mudas' in asd and 'Almox. Lagoa Grande' in asd, '5 toque 1: o painel mostra "Separe:" com lote, validade, local e embalagem', asd[:300])
    ok(pr.startswith('Entregar REQ-021 · 92.500 un Muda de mamão Formosa (lote LG26-05) + 20.000 kg Superfosfato simples (lote LG26-09) a Renato'), '5 primária nomeia a requisição inteira e o recebedor', pr)
    pd = prim_dentro(); ok(isinstance(pd, dict) and pd['dentro'] and pd['centro'] and pd['inicio'], '5 1440 px: a primária de rótulo longo cabe no painel e recebe o toque (centro e começo)', pd)
    clk_prim(); time.sleep(.6)
    r21 = a.cen("[c.reqs['REQ-021'].itens.map(i=>i.entregue),c.movs.filter(m=>m.req==='REQ-021'&&m.tipo==='entrega').map(m=>m.quem)]")
    ok(r21[0] == [92500, 20000] and r21[1] == ['Rui (almoxarife) → Renato'] * 2, '5 toque 2: entregue inteira; a trilha grava Rui → Renato', r21)
    ok('entregues a Renato' in (a.aside() + a.toast()), '5 comprovante no painel', a.aside()[:200])
    # ---------- 6 · toque duplo no "Entregar REQ-039": uma entrega; REQ-040 intacta ----------
    ir('#req=REQ-039'); n40 = a.cen("[c.reqs['REQ-040'].itens[0].entregue,c.lotes['NPK 20-05-20|N26-03'].reservado]")
    J("(()=>{const a=document.querySelector('aside[role=dialog]'); const b=[...a.querySelectorAll('button')].filter(b=>b.offsetParent&&getComputedStyle(b).backgroundColor==='rgb(30, 122, 76)').pop(); b.click(); setTimeout(()=>b.click(),60);})()")
    time.sleep(1.0)
    d39 = a.cen("[c.reqs['REQ-039'].itens[0].entregue,c.movs.filter(m=>m.req==='REQ-039'&&m.tipo==='entrega').length,c.reqs['REQ-040'].itens[0].entregue,c.lotes['NPK 20-05-20|N26-03'].reservado]")
    ok(d39[:2] == [65, 1] and d39[2:] == n40, '6 dois cliques em 60 ms: REQ-039 entregue uma vez (65 L); REQ-040 e a reserva do N26-03 intactas', [d39, n40])
    # ---------- 7 · REQ-040: reserva parcial entrega o reservado ----------
    ir('', 1.0); a.ir_secao('Atenda requisições')
    ok(a.cel('REQ-040', 'Situação') == 'Reserva parcial · faltam 3.400 kg', '7 REQ-040 "Reserva parcial · faltam 3.400 kg"', a.cel('REQ-040', 'Situação'))
    a.row('REQ-040'); asd = a.aside(); pr = prim_painel()
    ok('falta fica com Compras' in asd and pr.startswith('Entregar REQ-040 · 8.000 kg NPK 20-05-20 (lote N26-03)'), '7 painel explica a falta e entrega os 8.000 kg reservados', [pr, asd[:200]])
    clk_prim(); time.sleep(.6)
    ok(a.cen("c.reqs['REQ-040'].itens[0].entregue") == 8000, '7 REQ-040 entregou 8.000 kg', a.cen("c.reqs['REQ-040'].itens[0].entregue"))
    # ---------- 8 · consumo fora da requisição (CC) e recusa com motivo (AC-SUP-05) ----------
    a.mudar("cenIniciarTurno(c,'OS-0421'); return cenFecharTurno(c,10,2,{'Fungicida A':10,'Adjuvante espalhante':0.5},'');")
    kid = a.cen("(c.confs.find(k=>k.prod==='Adjuvante espalhante')||{}).id")
    ir('', 1.0); a.perfil('Rui'); a.ir_secao('Atenda requisições')
    J("[...document.querySelectorAll('main [role=row] [aria-expanded=false]')].forEach(b=>b.click())"); time.sleep(.3)
    lf = a.rowtxt('Adjuvante espalhante', 'fora da requisição')
    ok(lf != 'sem linha' and kid in lf, f'8 linha "Adjuvante espalhante · fora da requisição" ({kid}) na REQ-035', lf)
    a.row('Adjuvante espalhante', 'fora da requisição'); asd = a.aside()
    ok('Consumo em conferência' in asd and 'Recusar relato' in asd, '8 o painel concilia (aceitar ou recusar o relato)', asd[:200])
    a.clk('Recusar relato ' + kid + ' ›', 'aside[role=dialog]'); e0 = estado(); clk_prim(); time.sleep(.4)
    ok(a.cen(f"c.confs.find(k=>k.id==='{kid}').estado") == 'Em conferência' and estado() == e0 and a.err() != '', '8 recusa sem motivo não grava', a.err())
    a.setv('#fx_g_req_mot', 'operador não usou adjuvante'); clk_prim(); time.sleep(.5)
    kr = a.cen(f"[c.confs.find(k=>k.id==='{kid}').estado,c.confs.find(k=>k.id==='{kid}').decisao]")
    ok(kr == ['Recusado', 'operador não usou adjuvante'], '8 recusa grava o motivo digitado', kr)
    # ---------- 9 · devolução em branco recusa; digitada grava quem recebeu (Ver como Paula) ----------
    ir('', 1.0); a.perfil('Paula'); ir('#req=REQ-031'); e0 = estado(); clk_prim(); time.sleep(.4)
    ok(estado() == e0 and a.err() != '', '9 devolução em branco: recusa salvar e nada é gravado', a.err())
    a.setv('#fx_g_req_dqtd', '500'); clk_prim(); time.sleep(.5)
    d31 = a.cen("[c.reqs['REQ-031'].itens[0].custodia,(c.movs.filter(m=>m.req==='REQ-031'&&m.tipo==='devolucao').pop()||{}).quem]")
    ok(d31[0] == 0 and str(d31[1]).startswith('Paula (almoxarife)'), '9 500 kg recebidos; a trilha grava Paula (Ver como)', d31)
    # ---------- 10 · laudo por parcela: aprovado e reprovado (AC-SUP-06) ----------
    a.perfil('Rui'); ir('#nf=NF 4501')
    ok(prim_painel() == '', '10 Rui vê a parcela sem a primária do laudo (decisão da gestora)', prim_painel())
    a.perfil('Ana'); ir('#nf=NF 4501'); a.setv('#fx_g_rec_laudo', 'LAB-0917'); a.setv('#fx_g_rec_res', 'Aprovado'); time.sleep(.3)
    ok(prim_painel() == 'Liberar parcela · 10.000 kg', '10 primária "Liberar parcela · 10.000 kg"', prim_painel())
    clk_prim(); time.sleep(.5)
    ok(a.cen("[c.lotes['KCl 60%|K26-11'].quarentena,(c.movs.slice(-1)[0]||{}).quem]") == [0, 'Ana (gestora)'], '10 laudo aprovado libera a parcela; trilha com Ana', a.cen("c.lotes['KCl 60%|K26-11'].quarentena"))
    a.mudar("return cenDevolver(c,'REQ-039','Fungicida A',5,false,'Rui','embalagem aberta');")
    ir('#nf=REQ-039'); a.setv('#fx_g_rec_laudo', 'INSP-0042'); a.setv('#fx_g_rec_res', 'Reprovado'); a.setv('#fx_g_rec_dest', 'descartar com laudo'); time.sleep(.3)
    ok(prim_painel() == 'Manter bloqueada · laudo reprovado', '10 reprovado: primária "Manter bloqueada · laudo reprovado"', prim_painel())
    clk_prim(); time.sleep(.5)
    lr = a.cen("[c.lotes['Fungicida A|F26-02'].quarentena,(cenQuar(c.lotes['Fungicida A|F26-02']).find(p=>p.doc==='REQ-039')||{}).laudo]")
    ok(lr[0] == 5 and (lr[1] or {}).get('res') == 'Reprovado', '10 laudo reprovado mantém os 5 L bloqueados, com o laudo na parcela', lr)
    # ---------- 11 · contagem cega (AC-SUP-08): nem linha, nem formulário, nem filtro, nem Saldos ----------
    a.perfil('Paula'); ir('#sec=saldos'); ls = a.rowtxt('G26-14')
    ok('contagem aberta' in ls and '1.200' not in ls, '11 Saldos: para quem conta, físico e disponível do G26-14 ficam ocultos', ls)
    ir('#sec=contagens'); lc = a.rowtxt('INV-2611')
    ok(lc != 'sem linha' and '1.200' not in lc, '11 linha da INV-2611 sem o saldo do sistema', lc)
    fl = J("""(()=>{ const out=[]; [...document.querySelectorAll('main button[aria-label^="Filtrar "]')].filter(b=>b.offsetParent).forEach(b=>{ b.click(); out.push(document.body.innerText.split('Contagens').slice(1).join(' ')); b.click(); }); return out.join(' | '); })()""")
    ok('1.200' not in fl, '11 filtros das colunas sem o saldo', fl[:200])
    a.row('INV-2611'); asd = a.aside()
    ok('Contagem cega' in asd and '1.200' not in asd, '11 formulário sem o saldo', asd[:200])
    a.setv('#fx_g_cnt_cont', '1180'); e0 = estado(); clk_prim(); time.sleep(.5)
    asd = a.aside(); ok('Informe a causa' in asd and prim_painel() == 'Enviar ajuste à gestora', '11 com diferença, o mesmo painel pede a causa', [prim_painel(), asd[:200]])
    a.setv('#fx_g_cnt_causa', 'vazamento de uma bombona'); clk_prim(); time.sleep(.5)
    aj = a.cen("(c.ajustes||[]).filter(x=>x.lote==='G26-14').map(x=>[x.estado,x.contador,x.dif])")
    ok(aj == [['Aguardando gestor', 'Paula (almoxarife)', -20]], '11 ajuste vai à gestora com o contador Paula', aj)
    erros = a.erros(); ok(erros == [], '— sem erro de JavaScript no desktop', erros)
    # ---------- 12 · celular 390 e 360 (AC-SUP-12) ----------
    for w in (390, 360):
        a.c.size(w, 844); ir('', 1.4); a.perfil('Rui'); ir('', 1.0); a.ir_secao('Atenda requisições')
        sw = J("[document.scrollingElement.scrollWidth,window.innerWidth]")
        hd = J("[...document.querySelectorAll('main [role=columnheader]')].filter(h=>{const r=h.getBoundingClientRect(); return r.width>0&&r.left>=0&&r.right<=window.innerWidth+1;}).map(h=>h.innerText.replace(/[⇅▾▴▼▲]/g,'').trim().toUpperCase())")
        ok(sw[0] <= sw[1] + 1, f'12 {w} px: a página não rola de lado', sw)
        ok(any(h.startswith('REQUISIÇÃO') for h in hd) and any(h.startswith('SITUAÇÃO') for h in hd), f'12 {w} px: Requisição e Situação à vista', hd)
        J("window.__cen.cenReset()"); ir('#req=REQ-039', 1.4)
        vis = J("(()=>{const a=document.querySelector('aside[role=dialog]'); if(!a) return 'sem painel'; const sep=[...a.querySelectorAll('*')].find(e=>e.childElementCount===0&&/Separe:/.test(e.innerText||'')); const b=[...a.querySelectorAll('button')].filter(b=>b.offsetParent&&getComputedStyle(b).backgroundColor==='rgb(30, 122, 76)').pop(); const H=window.innerHeight; const v=e=>{ if(!e) return false; const r=e.getBoundingClientRect(); return r.top>=0&&r.bottom<=H+1; }; return [v(sep),v(b),b?b.innerText.trim():''];})()")
        ok(isinstance(vis, list) and vis[0] and vis[1], f'12 {w} px: no painel, "Separe:" e a primária sem rolar', vis)
        pd = prim_dentro(); ok(isinstance(pd, dict) and pd['dentro'] and pd['centro'] and pd['inicio'], f'12 {w} px: a primária cabe no painel e recebe o toque', pd)
        a.shot(f'q_est_fila_{w}.png')
    erros = a.erros(); ok(erros == [], '— sem erro de JavaScript no celular', erros)
finally:
    passou = a.fim()
sys.exit(0 if passou else 1)
