# -*- coding: utf-8 -*-
"""Produção · teste de navegador do fluxo principal (docs/colheita/ESPECIFICACAO.md §8; AC-01, AC-04, AC-15..AC-19, AC-22).
Modos (um por vez, cada um abre o Chrome headless do cadc_lib.T):
  os       A-05/AC-22: ordem nova de colheita pela tela da O.S. nasce na fazenda e na safra do cultivo (não some do filtro
           Lagoa Grande · 2026/27); a mesma semana não duplica; "Aprovar e liberar" da S40 do Pivô 6 recusado por carência
           sem dados (dono Wesley). Roda também na base (a parte A-05 falha lá: é o defeito reproduzido).
  fluxo    AC-17: tarefa do proprietário (§8.1) de ponta a ponta no desktop, com cliques e campos digitados medidos
           (limite 30 cliques e 5 campos); AC-01 menu; AC-04; AC-15 (encerrar com carga a pesar recusado no OS.dc.html).
  erros    recusas e repetição: pesagem sem condição, ticket repetido com outro conteúdo, reserva acima da falta, mesma
           pesagem repetida não duplica, carga sem sinal do app só entra ao voltar o sinal (AC-16).
  celular  AC-19: 390 × 844, cartões, sem rolagem horizontal, ação primária visível e presa ao rodapé nas três telas.
  revisao  regressões da revisão adversarial (Codex, 06/10): A-01 dia da colheita obrigatório e lote em inspeção sem apontamento,
           A-02 ponto de milhar, A-03 cancelar e reservar de novo, A-04 O.S. com carga não cancela, A-05 avaria depois da liberação,
           A-06 descartar carga a pesar (CARGA e MB-10), A-09 toque duplo no MB-07, A-11 carga sem sinal na O.S., A-13 sem "Liberar"
           quando a pendência é de outro, A-14 MB-10 na carência, A-15 ponderada com a área da conta, A-16 perda inválida,
           A-17 PV-030 como saldo do CT-201, A-18 coluna Em processo.
Uso: env CHROME_BIN=… flock /tmp/cdpB.lock env CDP_GL=1 timeout 900 python3 producao_fluxo_test.py [os|fluxo|erros|celular]
Capturas em _probe/producao_*.png. Dados sintéticos (SAFRION_DADOS=sintetico)."""
import sys, os, time, json
os.environ.setdefault('SAFRION_DADOS', 'sintetico')
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from cadc_lib import T
MODOS = [a for a in sys.argv[1:] if a in ('os', 'fluxo', 'erros', 'celular', 'revisao')] or ['os', 'fluxo', 'erros', 'celular', 'revisao']
PR = os.path.join(HERE, '_probe'); os.makedirs(PR, exist_ok=True)
t = T(); J = t.J
LIB = r"""
window.N=s=>(s||'').replace(/\s+/g,' ').trim();
window.VIS=e=>{ if(!e) return false; const r=e.getBoundingClientRect(); const cs=getComputedStyle(e); return r.width>1&&r.height>1&&cs.visibility!=='hidden'&&cs.display!=='none'; };
window.__cl=window.__cl||0; window.__tx=window.__tx||0;
window.CLK=(t,root)=>{ const r=root?document.querySelector(root):document; if(!r) return 'SEM RAIZ '+root; const els=[...r.querySelectorAll('button,a,[role=tab]')].filter(VIS);
  const e=els.find(x=>N(x.innerText)===t)||els.find(x=>N(x.innerText).startsWith(t))||els.find(x=>(x.getAttribute('aria-label')||'')===t); if(!e) return 'NÃO ACHEI: '+t; window.__cl++; e.click(); return 'ok'; };
window.SETV=(sel,val,conta)=>{ const i=document.querySelector(sel); if(!i) return 'sem '+sel; const P=i.tagName==='SELECT'?HTMLSelectElement.prototype:(i.tagName==='TEXTAREA'?HTMLTextAreaElement.prototype:HTMLInputElement.prototype);
  Object.getOwnPropertyDescriptor(P,'value').set.call(i,val); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true})); if(conta) window.__tx++; return 'ok'; };
window.ROW=(t)=>{ const r=[...document.querySelectorAll('[role=row]')].filter(VIS).find(x=>N(x.innerText).indexOf(t)>=0); if(!r) return 'sem linha '+t; window.__cl++; (r.querySelector('.g2pw')||r).click(); return 'ok'; };
window.ROWTXT=(t)=>{ const r=[...document.querySelectorAll('[role=row]')].find(x=>N(x.innerText).indexOf(t)>=0); return r?N(r.innerText):''; };
window.PAN=()=>{ const a=[...document.querySelectorAll('aside[role=dialog]')].find(VIS); return a?N(a.innerText):''; };
window.TOAST=()=>[...document.querySelectorAll('[role=status]')].map(x=>N(x.innerText)).filter(Boolean).join(' | ');
window.PRIM=()=>{ const b=[...document.querySelectorAll('header .pr-prim, header button, header a')].filter(e=>VIS(e)&&getComputedStyle(e).backgroundColor==='rgb(30, 122, 76)'); return b.map(e=>N(e.innerText)); };
window.CEN=()=>JSON.parse(localStorage.getItem('talhao-os-cenario-v1')||'null')||((window.__car&&window.__car.cenGet)?window.__car.cenGet():null);
'ok'"""
def lib(): J(LIB)
def ir(pg, limpa=False, w=1440, h=1000):
    t.c.size(w, h)
    if limpa:
        t.c.goto(f'http://127.0.0.1:{t.p}/Main.dc.html', wait=.4); J("localStorage.clear(); sessionStorage.clear()")
    cl, tx = (J("[window.__cl||0, window.__tx||0]") or [0, 0]) if not limpa else (0, 0)
    t.goto(pg); time.sleep(.5); lib(); J(f"window.__cl={cl}; window.__tx={tx};")
def clk(x, root=None, w=.45): r = J(f"CLK({json.dumps(x)},{json.dumps(root)})"); time.sleep(w); return r
def setv(sel, val, conta=True): r = J(f"SETV({json.dumps(sel)},{json.dumps(val)},{'true' if conta else 'false'})"); time.sleep(.25); return r
def row(x): r = J(f"ROW({json.dumps(x)})"); time.sleep(.45); return r
def pan(): return J("PAN()") or ''
def toast(): return J("TOAST()") or ''
def shot(n): t.c.shot(os.path.join(PR, 'producao_' + n + '.png'))
def cen(expr): return J(f"(()=>{{ const c=CEN(); return ({expr}); }})()")
def nova_ordem(saf, cult_txt, atv_txt, jan):
    """formulário de ordem nova da O.S. (o mesmo da base): escolhe safra, cultivo e atividade pelo texto da opção"""
    pick = lambda sel, txt: J(f"(()=>{{ const s=document.querySelector({json.dumps(sel)}); if(!s) return 'sem select'; const o=[...s.options].find(o=>o.text.indexOf({json.dumps(txt)})>=0); if(!o) return 'sem opção '+{json.dumps(txt)}; return SETV({json.dumps(sel)},o.value); }})()")
    a = pick('#nv_saf', saf); time.sleep(.3); b = pick('#nv_cult', cult_txt); time.sleep(.3); c = pick('#nv_atv', atv_txt); time.sleep(.3)
    d = setv('#nv_jan', jan); return [a, b, c, d]

try:
    if 'os' in MODOS:
        print('== os · A-05 / AC-22: ordem nova de colheita na fazenda e safra do cultivo; uma por semana; carência no liberar')
        ir('OS.dc.html', limpa=True)
        clk('Nova ordem'); r = nova_ordem('Safra Mamão 2026/27', 'Pivô 19', 'Colheita', '2026-09-28'); clk('Emitir ordem', 'aside')
        c = cen("(()=>{ const k=Object.keys(c.ordens).filter(k=>c.ordens[k].osc&&c.ordens[k].osc.novo); const o=c.ordens[k[k.length-1]]; return o?[o.id,o.tipo,o.osc.novo.faz,o.osc.novo.saf,o.etapa]:null; })()")
        t.chk('A-05 ordem nova do Pivô 19 (Safra Mamão 2026/27) nasce na Lagoa Grande e na safra 2026/27, A liberar', c and c[2] == 'Lagoa Grande' and c[3] == '2026/27' and c[4] == 'A liberar', [r, c])
        nid = c[0] if c else ''
        J("SETV('select[aria-label=\"Filtrar por fazenda\"]','Lagoa Grande')"); time.sleep(.4); J("SETV('select[aria-label=\"Filtrar por safra\"]','2026/27')"); time.sleep(.5)
        t.chk('A-05 com o filtro Lagoa Grande · 2026/27 a ordem nova aparece na lista', bool(nid) and nid in (J("ROWTXT(" + json.dumps(nid) + ")") or ''), nid)
        t.chk('AC-22 perene: a ordem se chama "Colheita · semana 40"', c and c[1] == 'Colheita · semana 40', c)
        clk('Nova ordem'); nova_ordem('Safra Mamão 2026/27', 'Pivô 19', 'Colheita', '2026-09-29'); clk('Emitir ordem', 'aside')
        e = pan()
        t.chk('AC-22 segunda ordem de colheita da mesma semana (S40) no Pivô 19 é recusada e aponta a existente', ('Já existe ' + nid) in e and 'semana 40' in e, e[:400])
        clk('Cancelar', 'aside'); clk('Descartar alterações', 'aside')
        clk('Nova ordem'); nova_ordem('Safra Mamão 2026/27', 'Pivô 19', 'Colheita', '2026-09-22'); clk('Emitir ordem', 'aside')
        e = pan()
        t.chk('AC-22 colheita na semana 39 do Pivô 19 é recusada: a OS-0505 (Colheita · semana 39) já existe', 'Já existe OS-0505' in e, e[:400])
        clk('Cancelar', 'aside'); clk('Descartar alterações', 'aside')
        ir('OS.dc.html#nova:lg06:q3:2026-09-28')
        v = J("[document.querySelector('#nv_saf')&&document.querySelector('#nv_saf').value, document.querySelector('#nv_cult')&&document.querySelector('#nv_cult').value, document.querySelector('#nv_atv')&&document.querySelector('#nv_atv').value, document.querySelector('#nv_jan')&&document.querySelector('#nv_jan').value]")
        t.chk('#nova:lg06:q3:2026-09-28 abre a ordem nova já preenchida (safra, cultivo, atividade, janela)', v == ['LG2627', 'lg06', 'q3', '2026-09-28'], v)
        clk('Emitir ordem', 'aside'); time.sleep(.3)
        c6 = cen("(()=>{ const o=Object.values(c.ordens).find(o=>o.talhao==='Pivô 6'&&/semana 40/.test(o.tipo)); return o?o.id:''; })()")
        t.chk('a ordem da S40 do Pivô 6 é emitida (A liberar)', bool(c6), c6)
        if c6:
            ir('OS.dc.html#' + c6); a = clk('Liberar para execução', 'aside'); p = pan() + ' ' + toast()
            et = cen(f"c.ordens[{json.dumps(c6)}].etapa")
            t.chk('AC-22 liberar (Aprovar e liberar) a S40 do Pivô 6 fica impedido no comando por carência sem dados, com dono Wesley; a ordem continua A liberar',
                  et == 'A liberar' and a.startswith('NÃO ACHEI') and 'Liberar bloqueado: carência sem dados' in p and 'Wesley' in p, [a, et, p[:500]])
        shot('os')
    if 'fluxo' in MODOS:
        print('== fluxo · AC-01 menu e AC-17 tarefa do proprietário (§8.1), cliques e campos medidos')
        ir('PROD.dc.html', limpa=True)
        m = J("(()=>{ const nav=document.querySelector('nav[aria-label=Menu]'); const t=N(nav.innerText); return t; })()") or ''
        i_ag, i_pr, i_ma = m.find('Agrícola'), m.find('Produção'), m.find('Manutenção')
        t.chk('AC-01 grupo Produção logo depois de Agrícola (antes de Manutenção)', 0 <= i_ag < i_pr < i_ma, m[:300])
        itens = J("[...document.querySelectorAll('nav[aria-label=Menu] a')].map(a=>[N(a.innerText),a.getAttribute('href')]).filter(x=>['COLH.dc.html','CARGA.dc.html','PROD.dc.html'].indexOf(x[1])>=0)") or []
        t.chk('AC-01 Produção com 3 itens: Previsão e colheita, Cargas e recebimento, Estoque de produto', [x[0] for x in itens] == ['Previsão e colheita', 'Cargas e recebimento', 'Estoque de produto'], itens)
        for pg in ('COLH', 'CARGA', 'PROD'):
            ir(pg + '.dc.html'); t.chk(f'AC-01 {pg} abre sem erro de JS', not t.errs(), t.errs())
        ir('COLH.dc.html', limpa=True)
        t.chk('§8.1 sem seleção, a ação primária é "Publicar previsão" do Pivô 19', J("PRIM()") == ['Publicar previsão do Pivô 19'], J("PRIM()"))
        r = row('Pivô 19'); p = pan()
        t.chk('painel do Pivô 19: passe S39 parcial 0,73 t/ha, ciclo 0,48 t/ha, 1 carga a receber, rascunho S40 e S41', '0,73 t/ha' in p and '0,48 t/ha' in p and 'CG-2108' in p and 'S40' in p and 'S41' in p, p[:900])
        clk('Publicar previsão', 'aside'); p = toast()
        t.chk('(1) Publicar previsão: v2 do Pivô 19 com S40 72,78 t e S41 87,34 t', 'v2 publicada' in p and 'S40 72,78 t' in p and 'S41 87,34 t' in p, p)
        t.chk('(1) a ação primária passa a "Programar colheita S40"', J("PRIM()") == ['Programar colheita S40'], J("PRIM()"))
        clk('Programar colheita S40'); time.sleep(.8); lib()
        v = J("[document.querySelector('#nv_cult')&&document.querySelector('#nv_cult').value, document.querySelector('#nv_jan')&&document.querySelector('#nv_jan').value]")
        t.chk('(1) "Programar colheita S40" abre a ordem nova pré-preenchida (Pivô 19, janela 28/09)', v == ['lg19', '2026-09-28'], v)
        clk('Emitir ordem', 'aside'); nid = cen("(()=>{ const o=Object.values(c.ordens).find(o=>o.talhao==='Pivô 19'&&/semana 40/.test(o.tipo)); return o?o.id+'|'+o.etapa:''; })()") or '|'
        nid, et = nid.split('|')
        t.chk('(1) Emitir: ordem "Colheita · semana 40" do Pivô 19 em A liberar', bool(nid) and et == 'A liberar', nid)
        ir('OS.dc.html#' + nid); clk('Liberar para execução', 'aside'); clk('Confirmar liberação', 'aside'); et = cen(f"c.ordens[{json.dumps(nid)}].etapa")
        t.chk('(2) Aprovar e liberar a ordem nova (carência do Pivô 19 em dia): Liberadas', et == 'Liberadas', [et, pan()[:300], toast()])
        ir('MB-10.dc.html'); lib()
        clk('Apontar área · OS-0505'); setv('#mb_ha', '25'); setv('#mb_h', '8'); clk('Gravar área'); p = toast()
        t.chk('(3) MB-10 › Colheita › OS-0505: Apontar área 25 ha em 8 h (regra única do apontamento, origem app)', '25 ha' in p, p)
        ap = cen("c.ordens['OS-0505'].ap.filter(a=>a.origem==='app').map(a=>[a.ha,a.st,a.d])")
        t.chk('(3) o apontamento do app entrou uma vez na OS-0505 (26/09, Provisório)', ap == [[25, 'Provisório', '26/09']], ap)
        ir('COLH.dc.html'); row('Pivô 19'); p = pan()
        t.chk('AC-04 apontar 25 ha sem carga não muda a produção (36,42 t) e o passe S39 cai para 0,49 t/ha', '36,42 t' in p and '0,49 t/ha' in p, p[:900])
        clk('Fechar', 'aside')
        ir('CARGA.dc.html'); t.chk('(4) sem seleção, a primária é "Registrar pesagem"', J("PRIM()") == ['Registrar pesagem'], J("PRIM()"))
        row('CG-2108'); t.chk('(4) com a CG-2108 selecionada, a primária vira "Pesar a CG-2108"', J("PRIM()") == ['Pesar a CG-2108'], J("PRIM()"))
        setv('#pf_tk', 'TK-4520'); setv('#pf_bruto', '19250'); setv('#pf_tara', '7200'); clk('Íntegra', 'aside'); clk('Pesar a CG-2108', 'aside'); p = toast()
        t.chk('(4) Pesar a CG-2108 (19.250 − 7.200): nasce o L39-133 com 12.050 kg, Liberado; passe 0,65 t/ha', 'L39-133' in p and '12.050 kg' in p and 'Liberado' in p and '0,65 t/ha' in p, p)
        ir('PROD.dc.html'); row('L39-133'); p = pan()
        t.chk('(5) L39-133 no estoque: 12.050 kg apto, vence 29/09; ação "Reservar para pedido" com PV-036 e sugestão 10.000 kg',
              '12.050 kg' in p and 'vence 29/09' in p and 'PV-036' in p and J("document.querySelector('[id^=pf_q_L39-133_PV-036]').value") == '10000', p[:600])
        clk('Reservar', 'aside'); p = toast()
        t.chk('(5) reserva RS-0002: 10.000 kg para o PV-036; L39-133 disponível 2.050 kg; PV-036 coberto', 'RS-0002' in p and '10.000 kg' in p and '2.050 kg' in p and 'coberto' in p, p)
        cl, tx = J("[window.__cl, window.__tx]")
        print(f'     medida AC-17: {cl} cliques · {tx} campos digitados (25 ha, horas, ticket, bruto, tara)')
        t.chk(f'AC-17 tarefa de ponta a ponta dentro de 30 cliques e 5 campos digitados ({cl} cliques · {tx} campos)', cl <= 30 and tx <= 5, [cl, tx])
        shot('fluxo')
    if 'erros' in MODOS:
        print('== erros · recusa e repetição')
        ir('CARGA.dc.html', limpa=True); row('CG-2108'); setv('#pf_tk', 'TK-4520'); setv('#pf_bruto', '19250'); setv('#pf_tara', '7200')
        clk('Pesar a CG-2108', 'aside'); p = pan()
        t.chk('pesagem sem condição é recusada no painel, nada gravado', 'Informe a condição' in p and cen("c.producao.cargas['CG-2108'].st") == 'A pesar', p[-300:])
        clk('Com avaria', 'aside'); clk('Pesar a CG-2108', 'aside')
        q = cen("(()=>{ const L=c.producao.lotes['L39-133']; return L?L.q0:''; })()")
        t.chk('Com avaria: L39-133 nasce Em inspeção (entrada não é liberação)', q == 'Em inspeção', q)
        n = cen("c.producao.movs.length")
        clk('Registrar pesagem'); clk('OS-0505 · Pivô 19', 'aside'); setv('#pf_dcol', '22/09'); setv('#pf_tk', 'TK-4520'); setv('#pf_bruto', '20000'); setv('#pf_tara', '7200'); clk('Íntegra', 'aside')
        clk('Registrar pesagem', 'aside'); p = pan()
        t.chk('ticket TK-4520 repetido com outro conteúdo = conflito, nada gravado', 'conflito' in p and cen("c.producao.movs.length") == n, p[-300:])
        setv('#pf_bruto', '19250'); clk('Com avaria', 'aside'); clk('Registrar pesagem', 'aside'); p = toast()
        t.chk('a mesma pesagem por outro formulário (mesmo ticket e conteúdo) = a mesma carga, nada somado', 'mesma carga' in p and cen("c.producao.movs.length") == n, [p, cen("c.producao.movs.length"), n])
        ir('PROD.dc.html'); row('L39-133'); clk('Liberar L39-133', 'aside'); p = toast()
        t.chk('Liberar lote (Qualidade) passa a Liberado', 'liberado por Qualidade' in p, p)
        row('L39-133'); setv('[id^=pf_q_L39-133_PV-036]', '10001'); clk('Reservar', 'aside'); p = pan()
        t.chk('reserva acima da falta do pedido é recusada junto ao formulário', 'Acima da falta' in p, p[-300:])
        ir('MB-10.dc.html'); lib(); clk('Sem sinal'); clk('Registrar carga · OS-0505'); setv('#mb_cx', '300'); clk('Carreta 02'); clk('Gravar carga'); p = toast()
        cid = cen("(()=>{ const g=Object.values(c.producao.cargas).find(g=>g.sinc===false); return g?g.id:''; })()")
        t.chk('AC-16 sem sinal: a carga fica no aparelho', bool(cid) and 'aparelho' in p, [cid, p])
        ir('CARGA.dc.html'); t.chk('AC-16 a carga do aparelho não aparece na web', not (J(f"ROWTXT({json.dumps(cid)})") or ''), cid)
        ir('MB-10.dc.html'); lib(); clk('Com sinal'); clk('Com sinal')
        ir('CARGA.dc.html'); n2 = J(f"[...document.querySelectorAll('[role=row]')].filter(r=>N(r.innerText).indexOf({json.dumps(cid)})>=0).length")
        t.chk('AC-16 ao voltar o sinal a carga entra uma vez (repetir o envio não duplica)', n2 == 1, n2)
        # AC-12 no app: contar no MB-07 grava a CNT- e não publica; a Previsão e colheita oferece "Publicar previsão" ao Pivô 6
        ir('MB-07.dc.html#lg06'); clk('Mais um fruto Pintado'); clk('Mais um fruto Pintado'); clk('Mais um fruto De vez'); clk('Registrar e ir à planta 2')
        setv('#mb_peso', '1,10'); clk('Concluir talhão (1 planta)'); p = toast()
        vs = cen("(c.producao.previsoes.lg06||[]).length")
        t.chk('AC-12 MB-07: Concluir talhão grava a CNT-0002 do Pivô 6 sem publicar (versão vigente continua a v1)', 'CNT-0002' in p and 'só muda quando' in p and vs == 1, [p, vs])
        ir('COLH.dc.html'); row('Pivô 6'); t.chk('AC-12 depois da contagem, a ação do Pivô 6 é "Publicar previsão"', J("PRIM()") == ['Publicar previsão'], J("PRIM()"))
        clk('Fechar', 'aside')
        # AC-15 no OS.dc.html: a OS-0505 posta Em conferência (término físico) com a CG-2108 a pesar não encerra; dono Lúcia
        ir('OS.dc.html', limpa=True)
        J("window.__car.cenMudar(null,c=>{ const o=c.ordens['OS-0505']; o.etapa='Em conferência'; o.saldo=0; o.ap=o.ap.filter(a=>a.st!=='Previsto'); return {msg:''}; })")
        ir('OS.dc.html#OS-0505'); a = clk('Conferir e encerrar', 'aside'); p = pan() + ' ' + toast()
        et = cen("c.ordens['OS-0505'].etapa"); lk = J("(()=>{ const a=[...document.querySelectorAll('aside[role=dialog] a')].find(x=>N(x.innerText).startsWith('Pesar a carga')); return a?a.getAttribute('href'):''; })()")
        t.chk('AC-15 no OS.dc.html, encerrar a OS-0505 com a CG-2108 a pesar fica impedido no comando, com dono Lúcia e o caminho para pesar', et == 'Em conferência' and a.startswith('NÃO ACHEI') and 'Encerrar bloqueado: Carga a pesar: CG-2108' in p and 'Lúcia pesa e recebe' in p and lk == 'CARGA.dc.html#CG-2108', [a, et, lk, p[:700]])
        shot('erros')
    if 'celular' in MODOS:
        print('== celular · AC-19 em 390 × 844')
        for pg in ('COLH', 'CARGA', 'PROD'):
            ir(pg + '.dc.html', limpa=True, w=390, h=844)
            m = J("(()=>{ const m=document.querySelector('main'); return [document.documentElement.scrollWidth, m.scrollWidth-m.clientWidth, [...document.querySelectorAll('.pr-card')].filter(VIS).length, [...document.querySelectorAll('.g2rola')].filter(VIS).length]; })()")
            b = J("(()=>{ const b=[...document.querySelectorAll('.pr-prim')].find(VIS); if(!b) return null; const r=b.getBoundingClientRect(); return [N(b.innerText), Math.round(r.top), Math.round(r.bottom), innerHeight, getComputedStyle(b).position]; })()")
            t.chk(f'AC-19 {pg}: cartões no lugar da tabela, sem rolagem horizontal', m and m[0] <= 390 and m[1] <= 0 and m[2] > 0 and m[3] == 0, m)
            t.chk(f'AC-19 {pg}: ação primária visível e presa ao rodapé', b and b[4] == 'fixed' and b[2] <= b[3] and b[1] > b[3] - 120, b)
            shot('390_' + pg)
        ir('PROD.dc.html', w=390, h=844); clk('L10-031 · Soja em grão'); p = pan()
        t.chk('AC-19 tocar no cartão abre o painel do lote (master-detail no celular)', 'L10-031' in p and '34.545 sc' in p, p[:200])
    if 'revisao' in MODOS:
        print('== revisao · regressões da revisão adversarial (A-01..A-18)')
        alerta = lambda: J("[...document.querySelectorAll('aside [role=alert]')].map(x=>N(x.innerText)).join(' | ')") or ''
        # A-02 · ponto de milhar como no ticket da balança
        ir('CARGA.dc.html', limpa=True); row('CG-2108'); setv('#pf_tk', 'TK-4520'); setv('#pf_bruto', '19.250'); setv('#pf_tara', '7.200'); clk('Íntegra', 'aside'); clk('Pesar a CG-2108', 'aside'); p = toast()
        g = cen("(()=>{ const g=c.producao.cargas['CG-2108']; return [g.st,g.liq,g.lote]; })()")
        t.chk('A-02 bruto "19.250" e tara "7.200": 12.050 kg líquidos (não 12,05)', g == ['Recebida', 12050, 'L39-133'] and '12.050 kg líquidos' in p, [g, p])
        # A-03 · reservar, cancelar e reservar de novo
        ir('PROD.dc.html'); row('L39-133'); clk('Reservar', 'aside'); p1 = toast()
        # Comercial P6 (D-C14): a venda e o "Cancelar reserva" estão em Comercial › Contratos e pedidos; a situação do PV-036 coberto pela reserva é
        # "Aguardando crédito" (R-C08, KC09: a receber da Frutas Real + esta reserva passa o limite), não "Coberto": a falta é o que prova a cobertura
        ir('VEN.dc.html'); row('PV-036'); clk('Cancelar reserva', 'aside'); setv('#pf_mot', 'cliente adiou'); clk('Cancelar RS-0002', 'aside'); p2 = toast()
        ir('PROD.dc.html'); row('L39-133'); clk('Reservar', 'aside'); p3 = toast() + ' ' + pan()[-200:]
        a = cen("Object.values(c.producao.reservas).filter(r=>r.pedido==='PV-036'&&r.st==='Ativa').map(r=>r.id)")
        ir('VEN.dc.html'); pv = J("ROWTXT('PV-036')") or ''
        t.chk('A-03 reservar → cancelar → reservar de novo: uma reserva ativa nova (RS-0003) e PV-036 sem falta (Aguardando crédito)', a == ['RS-0003'] and 'RS-0002' in p1 and 'cancelada' in p2 and 'RS-0003' in p3 and 'Aguardando crédito' in pv and '10.000 kg 0 kg' in pv, [a, p1, p2, p3, pv])
        # A-17 · PV-030 diz que é o saldo do CT-201; A-18 · coluna Em processo
        ir('VEN.dc.html', limpa=True)   # Comercial P6: a linha da venda está em Contratos e pedidos
        t.chk('A-17 a linha do PV-030 diz que a quantidade é o saldo do CT-201', 'saldo 4.000 sc do CT-201' in (J("ROWTXT('PV-030')") or ''), J("ROWTXT('PV-030')"))
        ir('PROD.dc.html')
        hd = J("[...document.querySelectorAll('[role=columnheader]')].map(x=>N(x.innerText))") or []
        mam = J("ROWTXT('Mamão Formosa · fruta de campo')") or ''
        t.chk('A-18 Estoque de produto com a coluna Em processo (mamão: 66.250 kg em processo)', any(h.lower().startswith('em processo') for h in hd) and '66.250 kg 0 kg 66.250 kg 0 kg' in mam, [hd, mam[:200]])
        # A-15 · a linha da cultura diz a área da ponderada
        ir('COLH.dc.html', limpa=True); mt = J("ROWTXT('Mamão Formosa')") or ''
        t.chk('A-15 linha do Mamão Formosa: 0,70 t/ha ponderada sobre 137,9 ha colhidos (96,74 t ÷ 137,9 ha)', '0,70 t/ha ponderada' in mt and 'sobre 137,9 ha colhidos' in mt, mt[:300])
        # A-16 · perda inválida ao publicar: o painel diz o que corrigir
        row('Pivô 19'); setv('#pf_pe', 'abc'); clk('Publicar previsão', 'aside'); al = alerta(); n = cen("c.producao.previsoes.lg19.length")
        t.chk('A-16 perda "abc": erro junto do campo e nada publicado (sem erro de JS)', 'Número de 0 a 99' in al and n == 1 and not t.errs(), [al, n, t.errs()])
        # A-09 · toque duplo em Concluir talhão (MB-07) grava uma contagem
        ir('MB-07.dc.html#lg06'); clk('Mais um fruto Pintado'); clk('Registrar e ir à planta 2'); setv('#mb_peso', '1,10')
        J("(()=>{ const b=[...document.querySelectorAll('button')].filter(VIS).find(b=>N(b.innerText).startsWith('Concluir talhão')); b.click(); b.click(); })()"); time.sleep(.6)
        n = cen("c.producao.contagens.filter(x=>x.cult==='lg06').length")
        t.chk('A-09 toque duplo em Concluir talhão (MB-07): uma contagem nova (o Pivô 6 não tinha contagem)', n == 1, cen("c.producao.contagens.filter(x=>x.cult==='lg06').map(x=>[x.id,x.chave])"))
        # A-01 · dia da colheita obrigatório, sem padrão; dia sem apontamento → lote em inspeção (A-13: Sérgio resolve, sem "Liberar")
        ir('CARGA.dc.html', limpa=True); clk('Registrar pesagem'); clk('OS-0505 · Pivô 19', 'aside')
        d0 = J("document.querySelector('#pf_dcol')&&document.querySelector('#pf_dcol').value"); pills = J("[...document.querySelectorAll('aside [role=group][aria-label=\"Dia da colheita\"] button')].map(b=>N(b.innerText))") or []
        setv('#pf_tk', 'TK-9100'); setv('#pf_bruto', '19200'); setv('#pf_tara', '7200'); clk('Íntegra', 'aside'); clk('Registrar pesagem', 'aside'); e = pan()
        t.chk('A-01 dia da colheita sem valor padrão, com atalhos (Hoje, Ontem, dias apontados); sem o dia, nada gravado', d0 == '' and pills[:2] == ['Hoje 26/09', 'Ontem 25/09'] and '22/09 · apontado' in pills and 'Informe o dia da colheita' in e
              and not cen("Object.values(c.producao.cargas).some(g=>g.ticket==='TK-9100')"), [d0, pills, e[-200:]])
        clk('Hoje 26/09', 'aside'); clk('Registrar pesagem', 'aside'); p = toast()
        lt = cen("(()=>{ const g=Object.values(c.producao.cargas).find(g=>g.ticket==='TK-9100'); return g?[g.dcol,g.lote]:null; })()") or ['', '']
        t.chk('A-01 colhida "hoje" (26/09) sem apontamento da OS-0505 nesse dia: lote Em inspeção, não Liberado', lt[0] == '2026-09-26' and 'Em inspeção' in p, [lt, p])
        ir('PROD.dc.html'); row(lt[1]); pp = pan(); bt = J("[...document.querySelectorAll('aside[role=dialog] button')].filter(VIS).map(b=>N(b.innerText))") or []
        t.chk('A-13 lote pendente do Sérgio: "Sérgio resolve", sem "Liberar" nem "Reservar" no painel', 'Sérgio resolve' in pp and not any(x.startswith('Liberar') or x.startswith('Reservar') for x in bt), [pp[:300], bt])
        # A-05 · avaria depois da liberação não entra apta
        ir('CARGA.dc.html', limpa=True)
        for tk, br in (('TK-A1', '12000'), ('TK-A2', '15000')):
            clk('Registrar pesagem'); clk('OS-0505 · Pivô 19', 'aside'); setv('#pf_dcol', '22/09'); setv('#pf_tk', tk); setv('#pf_bruto', br); setv('#pf_tara', '7200'); clk('Com avaria', 'aside'); clk('Registrar pesagem', 'aside')
            if tk == 'TK-A1':
                ir('PROD.dc.html'); row('L39-133'); clk('Liberar L39-133', 'aside'); ir('CARGA.dc.html')
        p = toast(); L = cen("(()=>{ const g=Object.values(c.producao.cargas).filter(g=>/^TK-A/.test(g.ticket)).map(g=>g.lote); return g; })()")
        t.chk('A-05 2ª carga com avaria depois da liberação vai a lote novo Em inspeção', L and len(L) == 2 and L[0] != L[1] and 'Em inspeção' in p, [L, p])
        # A-06 · carga do app em dobro: a pesagem nova sugere pesar a do app; descartar no CARGA e no MB-10 destrava
        ir('MB-10.dc.html', limpa=True); lib()
        for i in (1, 2): clk('Registrar carga · OS-0505'); setv('#mb_cx', '300'); clk('Carreta 02'); clk('Gravar carga')
        ids = cen("Object.values(c.producao.cargas).filter(g=>g.st==='A pesar'&&g.via==='app'&&g.id!=='CG-2108').map(g=>g.id)") or []
        ir('CARGA.dc.html'); clk('Registrar pesagem'); clk('OS-0505 · Pivô 19', 'aside'); pp = pan()
        bt = J("[...document.querySelectorAll('aside[role=dialog] button')].filter(VIS).map(b=>N(b.innerText))") or []
        t.chk('A-06 pesagem nova da OS-0505 avisa das cargas do app a pesar e oferece "Pesar a CG-…"', len(ids) == 2 and all(i in pp for i in ids) and ('Pesar a ' + ids[0]) in bt, [ids, pp[:300], bt])
        clk('Cancelar', 'aside'); row(ids[1]); clk('Descartar', 'aside'); setv('#pf_mot', 'registrada duas vezes no app'); clk('Confirmar descarte', 'aside'); p = toast()
        st1 = cen(f"c.producao.cargas[{json.dumps(ids[1])}].st")
        t.chk('A-06 CARGA: Descartar com motivo tira a carga da fila (Descartada, motivo no histórico)', st1 == 'Descartada' and 'descartada' in p, [st1, p])
        ir('MB-10.dc.html'); lib(); clk('Descartar carga a pesar'); clk(ids[0]); setv('#mb_mot', 'não saiu do campo'); clk('Descartar carga'); p = toast()
        st0 = cen(f"c.producao.cargas[{json.dumps(ids[0])}].st")
        t.chk('A-06 MB-10: Descartar carga a pesar (toque na carga + motivo) também descarta', st0 == 'Descartada' and 'descartada' in p, [st0, p])
        # A-11 · carga sem sinal: a O.S. manda reconectar o app, não pesar
        ir('CARGA.dc.html', limpa=True); row('CG-2108'); setv('#pf_tk', 'TK-4520'); setv('#pf_bruto', '19250'); setv('#pf_tara', '7200'); clk('Íntegra', 'aside'); clk('Pesar a CG-2108', 'aside')
        ir('MB-10.dc.html'); lib(); clk('Sem sinal'); clk('Registrar carga · OS-0505'); setv('#mb_cx', '200'); clk('Carreta 02'); clk('Gravar carga')
        ir('OS.dc.html'); J("window.__car.cenMudar(null,c=>{ const o=c.ordens['OS-0505']; o.etapa='Em conferência'; o.saldo=0; o.ap=o.ap.filter(a=>a.st!=='Previsto'); return {msg:''}; })")
        ir('OS.dc.html#OS-0505'); pp = pan(); lk = J("[...document.querySelectorAll('aside[role=dialog] a')].filter(VIS).map(a=>N(a.innerText))") or []; rw = J("ROWTXT('OS-0505')") or ''
        t.chk('A-11 encerrar com carga no aparelho: "Sérgio reconecta o app", sem "Lúcia pesa" nem link de pesar; a linha da O.S. não manda a Lúcia', 'Sérgio reconecta o app' in pp and 'Lúcia pesa' not in pp and not any(x.startswith('Pesar a carga') for x in lk) and 'Lúcia' not in rw, [pp[pp.find('Encerrar bloqueado'):][:300], lk, rw[:200]])
        # A-14 · MB-10 na carência: aviso sem "turnos" e confirmação explícita para registrar colheita já feita
        ir('OS.dc.html', limpa=True)
        J("window.__car.cenMudar(null,c=>{ c.ordens['OS-0999']={id:'OS-0999',tipo:'Pulverização · antracnose',talhao:'Pivô 19',area:75.11,etapa:'Encerradas',versao:'v1',realizado:75.11,saldo:0,resp:'Wesley',ins:[{p:'Tebuconazol 200 EC',dose:1,un:'L',tot:75.11}],req:null,selos:[],ap:[{d:'22/09',dia:1,ha:75.11,st:'Conferido',sinc:true,origem:'web'}],reservado:false,osc:{}}; return {msg:''}; })")
        ir('MB-10.dc.html'); lib(); cd = J("N(document.querySelector('main').innerText)") or ''
        clk('Apontar área · OS-0505'); setv('#mb_ha', '5'); setv('#mb_h', '2'); clk('Gravar área'); e = J("[...document.querySelectorAll('[role=alert]')].filter(VIS).map(x=>N(x.innerText)).join(' | ')") or ''
        n0 = cen("c.ordens['OS-0505'].ap.filter(a=>a.origem==='app').length"); clk('Colheita já feita'); clk('Gravar área'); n1 = cen("c.ordens['OS-0505'].ap.filter(a=>a.origem==='app').length")
        t.chk('A-14 MB-10 na carência: "não colha agora" (sem "turnos suspensos"); gravar pede "Colheita já feita" e só então registra', 'não colha agora' in cd and 'turnos suspensos' not in cd and 'Colheita já feita' in e and n0 == 0 and n1 == 1, [cd[cd.find('Carência'):][:200], e, n0, n1])
        # A-04 · O.S. de colheita liberada com carga recebida não oferece "Cancelar sem execução"
        ir('COLH.dc.html', limpa=True); row('Pivô 19'); clk('Publicar previsão', 'aside'); ir('COLH.dc.html'); clk('Programar colheita S40'); time.sleep(.8); lib(); clk('Emitir ordem', 'aside')
        nid = cen("(()=>{ const o=Object.values(c.ordens).find(o=>o.talhao==='Pivô 19'&&/semana 40/.test(o.tipo)); return o?o.id:''; })()") or ''
        ir('OS.dc.html#' + nid); clk('Liberar para execução', 'aside'); clk('Confirmar liberação', 'aside')
        ir('OS.dc.html#' + nid); a0 = J("[...document.querySelectorAll('aside[role=dialog] button, aside[role=dialog] a')].filter(VIS).map(b=>N(b.innerText))") or []
        ir('CARGA.dc.html'); clk('Registrar pesagem'); clk(nid + ' · Pivô 19', 'aside'); clk('Hoje 26/09', 'aside'); setv('#pf_tk', 'TK-9001'); setv('#pf_bruto', '19200'); setv('#pf_tara', '7200'); clk('Íntegra', 'aside'); clk('Registrar pesagem', 'aside')
        ir('OS.dc.html#' + nid); a1 = J("[...document.querySelectorAll('aside[role=dialog] button, aside[role=dialog] a')].filter(VIS).map(b=>N(b.innerText))") or []
        t.chk('A-04 ' + nid + ' Liberadas: "Cancelar sem execução" some depois da carga recebida (colheita com carga é execução)', 'Cancelar sem execução' in a0 and 'Cancelar sem execução' not in a1 and cen(f"c.ordens[{json.dumps(nid)}].etapa") == 'Liberadas', [nid, a0, a1])
        t.chk('revisão: nenhuma página com erro de JS', not t.errs(), t.errs())
        shot('revisao')
finally:
    t.fim()
