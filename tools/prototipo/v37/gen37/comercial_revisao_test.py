# -*- coding: utf-8 -*-
"""Comercial e logística · teste de navegador das correções da revisão adversarial de 09/10 (subagente revisor do workflow; não é o parecer do Codex) (HEAD bdc5ca8; A1..A11 de tela).
As regras (A2..A12) estão em comercial_unit.js (casos RV-*); aqui, o que só a tela mostra.
Modos (um por vez, cada um abre o Chrome headless do cadc_lib.T):
  duplo      A1 (S2): duplo clique HUMANO (dois eventos de mouse, 120 ms, mesmo ponto; Input.dispatchMouseEvent com clickCount 1 e 2) nas
             primárias do painel: "Confirmar saída" não confirma a entrega; "Registrar venda" e "Registrar a saca" não reservam lote;
             "Confirmar entrega" pede data e "Recebido" escolhidos e grava uma entrega só; depois do intervalo, o clique deliberado age
  cabecalho  A6 (S3): com o painel aberto, o cabeçalho não repete o verde com o mesmo rótulo e outro efeito (apagava bruto e tara)
  qualidade  A3 (S2) e A11: lote devolvido só é liberado por Marta (qualidade) ou Ana (agrônoma); Dora e Rui não veem verde; "Reservar"
             no Estoque de produto só para quem tem o papel
  situacao   A4 e A5 (S3): venda com a carga em trânsito aparece "Em trânsito"; peso acima do previsto avisa antes de gravar e a outra
             carga da venda fica "impedida: reserva menor que o previsto", sem "Confirmar saída"
  unidade    A7 (S3) e A11: venda em saca de 50 kg reserva, mostra a carga e devolve em "sc 50 kg"; "Outras datas" aceita 2809 (teclado numérico)
Uso: env CHROME_BIN=… flock /tmp/cdpC.lock env CDP_GL=1 timeout 900 python3 comercial_revisao_test.py [modo …]
Dados sintéticos (SAFRION_DADOS=sintetico; a Lagoa Grande é sintética)."""
import sys, os, time, json
os.environ.setdefault('SAFRION_DADOS', 'sintetico')
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from cadc_lib import T
TODOS = ('duplo', 'cabecalho', 'qualidade', 'situacao', 'unidade')
MODOS = [a for a in sys.argv[1:] if a in TODOS] or list(TODOS)
PR = os.path.join(HERE, '_probe'); os.makedirs(PR, exist_ok=True)
t = T(); J = t.J
LIB = r"""
window.N=s=>(s||'').replace(/\s+/g,' ').trim();
window.VIS=e=>{ if(!e) return false; const r=e.getBoundingClientRect(); const cs=getComputedStyle(e); return r.width>1&&r.height>1&&cs.visibility!=='hidden'&&cs.display!=='none'; };
window.CLK=(t,root)=>{ const r=root?document.querySelector(root):document; if(!r) return 'SEM RAIZ '+root; const els=[...r.querySelectorAll('button,a,[role=tab]')].filter(VIS);
  const e=els.find(x=>N(x.innerText)===t)||els.find(x=>N(x.innerText).startsWith(t))||els.find(x=>(x.getAttribute('aria-label')||'')===t); if(!e) return 'NÃO ACHEI: '+t; e.click(); return 'ok'; };
window.SETV=(sel,val)=>{ const i=document.querySelector(sel); if(!i) return 'sem '+sel; const P=i.tagName==='SELECT'?HTMLSelectElement.prototype:(i.tagName==='TEXTAREA'?HTMLTextAreaElement.prototype:HTMLInputElement.prototype);
  Object.getOwnPropertyDescriptor(P,'value').set.call(i,val); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true})); return 'ok'; };
window.ROW=(t)=>{ const r=[...document.querySelectorAll('[role=row]')].filter(VIS).find(x=>N(x.innerText).indexOf(t)>=0); if(!r) return 'sem linha '+t; (r.querySelector('.g2pw')||r).click(); return 'ok'; };
window.ROWTXT=(t)=>{ const r=[...document.querySelectorAll('[role=row]')].find(x=>N(x.innerText).indexOf(t)>=0); return r?N(r.innerText):''; };
window.PAN=()=>{ const a=[...document.querySelectorAll('aside[role=dialog]')].find(VIS); return a?N(a.innerText):''; };
window.TOAST=()=>[...document.querySelectorAll('[role=status]')].map(x=>N(x.innerText)).filter(Boolean).join(' | ');
window.VERDE=e=>VIS(e)&&getComputedStyle(e).backgroundColor==='rgb(30, 122, 76)';
window.PRIM=()=>[...document.querySelectorAll('header .pr-prim, header button, header a')].filter(VERDE).map(e=>N(e.innerText));
window.PRIMP=()=>[...document.querySelectorAll('aside[role=dialog] button, aside[role=dialog] a')].filter(VERDE).map(e=>N(e.innerText));
window.VERDES=(t)=>[...document.querySelectorAll('button,a')].filter(e=>VERDE(e)&&N(e.innerText)===t).length;
window.PRESS=(g)=>[...document.querySelectorAll('aside [role=group][aria-label^="'+g+'"] [aria-pressed=true]')].map(b=>N(b.innerText));
window.CEN=()=>JSON.parse(localStorage.getItem('talhao-os-cenario-v1')||'null')||((window.__car&&window.__car.cenGet)?window.__car.cenGet():null);
'ok'"""
def lib(): J(LIB)
def ir(pg, limpa=False, perfil=None, w=1440, h=1000):
    t.c.size(w, h)
    if limpa:
        t.c.goto(f'http://127.0.0.1:{t.p}/Main.dc.html', wait=.4); J("localStorage.clear(); sessionStorage.clear()")
    if perfil is not None:
        t.c.goto(f'http://127.0.0.1:{t.p}/Main.dc.html', wait=.3); J(f"localStorage.setItem('safrion.perfilDemo',{json.dumps(perfil)})")
    t.goto(pg); time.sleep(.5); lib()
def clk(x, root=None, w=.45): r = J(f"CLK({json.dumps(x)},{json.dumps(root)})"); time.sleep(w); return r
def setv(sel, val): r = J(f"SETV({json.dumps(sel)},{json.dumps(val)})"); time.sleep(.25); return r
def row(x): r = J(f"ROW({json.dumps(x)})"); time.sleep(.45); return r
def pan(): return J("PAN()") or ''
def toast(): return J("TOAST()") or ''
def cen(expr): return J(f"(()=>{{ const c=CEN(); return ({expr}); }})()")
def shot(n): t.c.shot(os.path.join(PR, 'comercial_rev_' + n + '.png'))
def mut(js):
    """prepara o estado pelo motor da página (a mesma cenMudar das telas), sem passar pela tela testada"""
    return J("(()=>{ const {prReceber,prReservar,prCancelarReserva}=window.__pr; const W=window.__com||{}; const r=window.__car.cenMudar(null,c=>{ " + js + " }); return r.erro||'ok'; })()")
def xy(label, root='aside[role=dialog]'):
    return J(f"(()=>{{ const e=[...document.querySelector({json.dumps(root)}).querySelectorAll('button,a')].filter(VIS).find(x=>N(x.innerText)==={json.dumps(label)}); if(!e) return null; e.scrollIntoView({{block:'center'}}); const r=e.getBoundingClientRect(); return [r.x+r.width/2, r.y+r.height/2]; }})()")
def dbl(label, gap=.12):
    """duplo clique humano: dois pares pressionar/soltar no mesmo ponto, clickCount 1 e 2, 120 ms entre eles (o navegador entrega detail 1 e 2)"""
    p = xy(label)
    if not p: return 'NÃO ACHEI: ' + label
    for n in (1, 2):
        t.c.call('Input.dispatchMouseEvent', {'type': 'mousePressed', 'x': p[0], 'y': p[1], 'button': 'left', 'clickCount': n})
        t.c.call('Input.dispatchMouseEvent', {'type': 'mouseReleased', 'x': p[0], 'y': p[1], 'button': 'left', 'clickCount': n})
        if n == 1: time.sleep(gap)
    time.sleep(1.0); return 'ok'
SACA60 = "['PV-030','CT-203','CRE-0095','BT-090'].forEach(id=>W.comConverterSaca(c,{venda:id,fat:'60',fonte:'Contrato '+id+' (teste)',ator:'Ana',chave:'T-SACA-'+id})); return {msg:''};"
COLHEITA = ("prReceber(c,{carga:'CG-2108',ticket:'TK-4520',bruto:19250,tara:7200,cond:'Íntegra',chave:'T-REC'}); "
            "prReservar(c,{pedido:'PV-036',lote:'L39-133',kg:10000,ator:'Dora',chave:'T-RS36'}); return {msg:''};")
CARGA36 = ("W.comAprovarCredito(c,{venda:'PV-036',ator:'Ana',chave:'K-CR'}); W.comProgramar(c,{venda:'PV-036',lotes:[{lote:'L39-133',prev:10000}],veic:'Baú refrigerado 12 t',"
           "transp:'Rota Sul Transportes',placa:'ABC1D23',dprev:'2026-09-26',ator:'Dora',chave:'K-PG'}); return {msg:''};")

try:
    if 'duplo' in MODOS:
        print('== duplo · A1 duplo clique humano nas primárias do painel')
        ir('VEN.dc.html', limpa=True); m = [mut(COLHEITA), mut(CARGA36)]
        ir('EXPED.dc.html#RM-0002', perfil='Rui'); time.sleep(.3); setv('#pf_br', '22000'); setv('#pf_ta', '12000')
        d = dbl('Confirmar saída da RM-0002'); rm = cen("(()=>{ const r=c.producao.expedicoes['RM-0002']; return [r.st, !!r.saida, r.entrega, c.producao.movs.filter(m=>m.rm==='RM-0002'&&m.tipo==='expedição').length]; })()")
        t.chk('A1 duplo clique em "Confirmar saída da RM-0002" (agricultor entrega): a saída grava uma vez e a entrega NÃO é confirmada pelo 2º clique (RM em trânsito)',
              m == ['ok', 'ok'] and d == 'ok' and rm == ['Em trânsito', True, None, 1] and 'saída de 10.000 kg' in toast(), [m, d, rm, toast()])
        t.chk('A1 o formulário "Confirmar entrega" abre sem data nem "Recebido" escolhidos (nada pré-marcado)', 'Confirmar entrega da RM-0002' in pan() and J("PRESS('Data da entrega')") == [] and J("PRESS('Recebido')") == [], [J("PRESS('Data da entrega')"), J("PRESS('Recebido')"), pan()[:300]])
        time.sleep(.6); clk('Hoje 26/09', 'aside'); clk('Confirmar entrega da RM-0002', 'aside')
        t.chk('A1 confirmar a entrega sem escolher "Recebido" é recusado junto do formulário; nada gravado', 'Escolha "Recebido tudo" ou "Com devolução"' in pan() and cen("c.producao.expedicoes['RM-0002'].entrega") is None, pan()[-300:])
        clk('Recebido tudo', 'aside'); d = dbl('Confirmar entrega da RM-0002')
        e = cen("(()=>{ const r=c.producao.expedicoes['RM-0002']; return [r.st, r.entrega&&r.entrega.d, (r.devs||[]).length]; })()")
        t.chk('A1 duplo clique em "Confirmar entrega": uma entrega (26/09), nenhuma devolução, e o 2º clique não abre outra ação', d == 'ok' and e == ['Entregue', '2026-09-26', 0] and 'Registrar devolução ·' not in pan(), [d, e, pan()[:300]])
        shot('duplo_entrega')
        ir('VEN.dc.html', limpa=True); mut(SACA60); ir('VEN.dc.html', perfil='Dora')
        clk('Registrar venda')
        for b in ('Coop Grão Sul', 'Soja em grão', 'Pronta entrega', 'Próxima semana'): clk(b, 'aside', .35)
        setv('#pf_q', '100'); setv('#pf_pr', '130'); d = dbl('Registrar venda')
        v = cen("[!!c.producao.pedidos['PV-039'], Object.values(c.producao.reservas).filter(r=>r.pedido==='PV-039').length]")
        t.chk('A1 duplo clique em "Registrar venda": PV-039 gravada e nenhuma reserva feita pelo 2º clique (o painel mostra "Reservar" para quem decide)', d == 'ok' and v == [True, 0] and 'Reservar' in (J("PRIMP()") or []), [d, v, J("PRIMP()"), toast()])
        time.sleep(.6); clk('Reservar', 'aside'); n = cen("Object.values(c.producao.reservas).filter(r=>r.pedido==='PV-039'&&r.st==='Ativa').length")
        t.chk('A1 passado o intervalo, o clique deliberado em "Reservar" age: uma reserva para o PV-039', n == 1, [n, toast()])
        ir('VEN.dc.html', limpa=True, perfil='Dora'); row('PV-030'); clk('60 kg', 'aside'); d = dbl('Registrar a saca')
        s = cen("[!!c.producao.pedidos['PV-030'].fatConf, Object.values(c.producao.reservas).filter(r=>r.pedido==='PV-030').map(r=>r.id)]")
        t.chk('A1 duplo clique em "Registrar a saca": saca gravada e nenhuma reserva nova (só a RS-0001 da semente)', d == 'ok' and s == [True, ['RS-0001']], [d, s, toast()])
        t.chk('duplo: nenhuma página com erro de JS', not t.errs(), t.errs())
    if 'cabecalho' in MODOS:
        print('== cabecalho · A6 o cabeçalho não repete o verde do painel aberto')
        ir('VEN.dc.html', limpa=True); mut(COLHEITA); mut(CARGA36)
        ir('EXPED.dc.html#RM-0002', perfil='Rui'); time.sleep(.3); setv('#pf_br', '22000'); setv('#pf_ta', '12000')
        t.chk('A6 painel da RM-0002 aberto: um só verde "Confirmar saída da RM-0002" (o do painel); o cabeçalho fica sem verde', J("VERDES('Confirmar saída da RM-0002')") == 1 and J("PRIM()") == [] and J("PRIMP()") == ['Confirmar saída da RM-0002'], [J("PRIM()"), J("PRIMP()")])
        clk('Esta semana'); b = J("[(document.querySelector('#pf_br')||{}).value, (document.querySelector('#pf_ta')||{}).value]")
        t.chk('A6 bruto e tara digitados continuam no formulário depois de outro toque na tela', b == ['22000', '12000'], b)
        clk('Cancelar', 'aside')
        t.chk('A6 fechado o painel, a primária volta ao cabeçalho ("Confirmar saída da RM-0002") e abre o painel', J("PRIM()") == ['Confirmar saída da RM-0002'], J("PRIM()"))
        clk('Confirmar saída da RM-0002'); t.chk('A6 o verde do cabeçalho abre o formulário da saída (Peso bruto)', 'Peso bruto' in pan() and J("PRIM()") == [], [pan()[:200], J("PRIM()")])
        ir('VEN.dc.html', perfil='Dora'); clk('Registrar venda')
        t.chk('A6 "Registrar venda" aberto: o verde é o do painel; o cabeçalho não repete', J("PRIM()") == [] and J("PRIMP()") == ['Registrar venda'], [J("PRIM()"), J("PRIMP()")])
        t.chk('cabecalho: nenhuma página com erro de JS', not t.errs(), t.errs())
    if 'qualidade' in MODOS:
        print('== qualidade · A3 só a Qualidade (ou a agrônoma) libera o lote devolvido; A11 verde só para quem tem o papel')
        ir('VEN.dc.html', limpa=True); mut(COLHEITA); mut(CARGA36)
        m = mut("W.comSair(c,{rm:'RM-0002',bruto:'22000',tara:'12000',ator:'Rui',chave:'K-S'}); W.comEntregar(c,{rm:'RM-0002',d:'2026-09-26',dev:{kg:400,motivo:'Maturação avançada'},ator:'Rui',chave:'K-E'}); return {msg:''};")
        lote = cen("(c.producao.expedicoes['RM-0002'].devs[0]||{}).lote") or ''
        for pf in ('Dora', 'Rui'):
            ir('PROD.dc.html#' + lote, perfil=pf); time.sleep(.3); p = pan()
            t.chk(f'A3 {pf} no lote devolvido {lote}: nenhum verde "Liberar"; o painel diz quem decide (Ana (agrônoma) ou Marta (qualidade))',
                  m == 'ok' and bool(lote) and J("PRIM()") == [] and J("PRIMP()") == [] and 'Decisão de Ana (agrônoma) ou Marta (qualidade)' in p, [m, lote, J("PRIM()"), J("PRIMP()"), p[:300]])
        ir('PROD.dc.html#' + lote, perfil='Marta'); time.sleep(.3)
        op = J("[...document.querySelectorAll('select option')].map(o=>N(o.innerText)).filter(x=>x.indexOf('Marta')===0)") or []
        t.chk('A3 perfil "Marta · Qualidade" no seletor; o painel mostra "Liberar ' + lote + '"', 'Marta · Qualidade' in op and J("PRIMP()") == ['Liberar ' + lote], [op, J("PRIMP()")])
        clk('Liberar ' + lote, 'aside'); lb = cen(f"[c.producao.lotes['{lote}'].q0, (c.producao.lotes['{lote}'].lib||{{}}).quem]")
        t.chk('A3 Marta libera: grava "Marta (qualidade)" (quem agiu, não um nome fixo)', lb == ['Liberado', 'Marta (qualidade)'] and 'liberado por Marta (qualidade)' in toast(), [lb, toast()])
        ir('VEN.dc.html', limpa=True); mut(SACA60); ir('PROD.dc.html', perfil='Rui'); row('L10-031')
        t.chk('A11 Rui (expedição) no L10-031 com pedido a cobrir: nenhum verde "Reservar …"; o painel diz quem decide', J("PRIM()") == [] and J("PRIMP()") == [] and 'Decisão de Ana (gestora) ou Dora (comercial)' in pan(), [J("PRIM()"), J("PRIMP()"), pan()[:300]])
        ir('PROD.dc.html', perfil='Dora'); t.chk('A11 Dora (comercial) vê "Reservar L10-031 para pedido" no cabeçalho', J("PRIM()") == ['Reservar L10-031 para pedido'], J("PRIM()"))
        t.chk('qualidade: nenhuma página com erro de JS', not t.errs(), t.errs())
        shot('qualidade')
    if 'situacao' in MODOS:
        print('== situacao · A4 em trânsito e A5 carga sem reserva que a cubra')
        ir('VEN.dc.html', limpa=True); mut(COLHEITA)
        m = mut("W.comAprovarCredito(c,{venda:'PV-036',kg:12050,ator:'Ana',chave:'K-C0'}); ['AAA1A11','BBB2B22'].forEach((pl,i)=>W.comProgramar(c,{venda:'PV-036',lotes:[{lote:'L39-133',prev:i?4000:6000}],veic:'Baú refrigerado 12 t',transp:'Rota Sul Transportes',placa:pl,dprev:'2026-09-26',ator:'Dora',chave:'K-P'+i})); return {msg:''};")
        ir('EXPED.dc.html#RM-0002', perfil='Rui'); time.sleep(.3); setv('#pf_br', '22000'); setv('#pf_ta', '12000'); time.sleep(.2); p = pan()
        t.chk('A5 antes de gravar, o painel avisa: líquido 4.000 kg acima do previsto (6.000 kg), a diferença sai da reserva prevista para a RM-0003', m == 'ok' and 'Líquido 4.000 kg acima do previsto (6.000 kg): a diferença sai da reserva prevista para a RM-0003' in p, [m, p[:700]])
        clk('Confirmar saída da RM-0002', 'aside'); time.sleep(.3)
        t.chk('A5 a saída grava com o aviso de que a RM-0003 fica sem reserva', 'Aviso: líquido 4.000 kg acima do previsto (6.000 kg): RM-0003 fica sem reserva' in toast(), toast())
        r3 = J("ROWTXT('RM-0003')") or ''
        t.chk('A5 RM-0003 aparece "Programada · impedida: reserva menor que o previsto" (não "Confirmar saída")', 'impedida: reserva menor que o previsto' in r3 and 'Confirmar saída' not in r3, r3)
        row('RM-0003'); p = pan()
        t.chk('A5 painel da RM-0003: sem verde "Confirmar saída"; o passo diz a reserva que falta e quem resolve', J("PRIMP()") == [] and J("PRIM()") == [] and 'Saída impedida: reserva do PV-036 no L39-133 (0 kg) menor que o previsto da carga (4.000 kg)' in p, [J("PRIMP()"), p[:400]])
        ir('VEN.dc.html', perfil='Dora'); rv = J("ROWTXT('PV-036')") or ''
        t.chk('A4 venda com a RM-0002 em trânsito: "Em trânsito" (não "Entregue")', 'Em trânsito' in rv and 'Entregue' not in rv.split('·')[0], rv)
        ir('PCOM.dc.html'); kp = J("N(document.querySelector('[aria-label=Indicadores]').innerText)") or ''
        t.chk('A4 "Entregue nos últimos 30 dias" conta só o entregue (RM-0001: R$ 91.470,00), não a carga em trânsito', 'R$ 91.470,00' in (kp.upper().split('ENTREGUE NOS ÚLTIMOS 30 DIAS') + [''])[1][:40], kp)
        t.chk('situacao: nenhuma página com erro de JS', not t.errs(), t.errs())
        shot('situacao')
    if 'unidade' in MODOS:
        print('== unidade · A7 venda em saca de 50 kg e A11 datas sem barra')
        ir('VEN.dc.html', limpa=True)
        m = mut("W.comConverterSaca(c,{venda:'PV-030',fat:'50',fonte:'Contrato CT-201 cl. 2',ator:'Ana',chave:'S50'}); prCancelarReserva(c,'RS-0001','refazer com 50 kg','Ana'); return {msg:''};")
        ir('VEN.dc.html', perfil='Ana'); row('PV-030')
        q = J("(()=>{ const i=[...document.querySelectorAll('aside input')].find(x=>x.id.indexOf('pf_q_L10-031_PV-030')===0); return i?i.value:null; })()")
        t.chk('A7 reservar para o PV-030 (saca de 50 kg): sugestão 4.000 em "sc 50 kg" (200.000 kg)', m == 'ok' and q == '4000' and 'sc 50 kg' in pan(), [m, q, pan()[:500]])
        m2 = mut("prReservar(c,{pedido:'PV-030',lote:'L10-031',kg:30000,ator:'Ana',chave:'S1'}); W.comProgramar(c,{venda:'PV-030',lotes:[{lote:'L10-031',prev:30000}],veic:'Bitrem graneleiro 37 t',placa:'AAA1A11',dprev:'2026-09-26',ator:'Ana',chave:'S2'}); W.comSair(c,{rm:'RM-0002',bruto:'44000',tara:'14000',ator:'Ana',chave:'S3'}); return {msg:''};")
        ir('EXPED.dc.html#RM-0002', perfil='Rui'); time.sleep(.3); r2 = J("ROWTXT('RM-0002')") or ''
        t.chk('A7 a carga do PV-030 mostra "600 sc 50 kg" (a massa da venda), não "500 sc"', m2 == 'ok' and '600 sc 50 kg' in r2 and '500 sc' not in r2, [m2, r2])
        clk('Registrar devolução', 'aside'); u = 'sc 50 kg' in pan(); setv('#pf_dq', '100'); clk('Fora do padrão contratado', 'aside'); clk('Registrar devolução', 'aside')
        dv = cen("(c.producao.expedicoes['RM-0002'].devs[0]||{}).kg")
        t.chk('A7 devolução digitada "100" em sc 50 kg = 5.000 kg (não 6.000 kg)', u and dv == 5000 and '100 sc 50 kg devolvidos' in toast(), [u, dv, toast()])
        ir('VEN.dc.html', perfil='Dora'); clk('Registrar venda')
        for b in ('Coop Grão Sul', 'Soja em grão', 'Pronta entrega', 'Outras datas'): clk(b, 'aside', .35)
        setv('#pf_di', '2809'); setv('#pf_df', '3009'); setv('#pf_q', '100'); setv('#pf_pr', '130'); clk('Registrar venda', 'aside')
        v = cen("(()=>{ const v=c.producao.pedidos['PV-039']; return v?[v.ini,v.fim]:null; })()")
        t.chk('A11 "Outras datas" com o teclado numérico (sem barra): 2809 e 3009 = janela 28/09–30/09', v == ['2026-09-28', '2026-09-30'], [v, pan()[-300:], toast()])
        t.chk('unidade: nenhuma página com erro de JS', not t.errs(), t.errs())
finally:
    t.fim()   # imprime RESULTADO
sys.exit(0 if all(t.ok) else 1)
