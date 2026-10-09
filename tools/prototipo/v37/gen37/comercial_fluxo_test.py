# -*- coding: utf-8 -*-
"""Comercial e logística · teste de navegador do fluxo principal (docs/comercial/ESPECIFICACAO.md §8; AC-01, AC-11, AC-12, AC-14..AC-17).
Modos (um por vez, cada um abre o Chrome headless do cadc_lib.T):
  menu     AC-01: grupo Comercial logo depois de Produção, 3 itens, cada um abre sem erro de JS; nenhum elo para tela oculta
  tarefa   AC-14: tarefa do proprietário (§8.1, perfil Ana) de ponta a ponta no desktop, com cliques e campos medidos (≤ 16 e ≤ 3);
           "Confirmar saída" recebe dois cliques seguidos sem espera e grava um só MP de expedição; Painel com R$ 128,00/sc e R$ 170.318
  erros    recusa e repetição: venda sem campos, tara ≥ bruto, crédito da Frutas Real (KC09) recusado para Rui e aprovado por Ana,
           registrar venda com duplo clique grava uma venda, venda futura na semana em curso não é oferecida
  perfis   AC-12: sem o papel, a primária mostra o dono em vez do botão (Rui na venda, Dora na saída, Caio em tudo); o registro grava quem agiu
  painel   AC-11: Painel da semente pelas funções do estado; "Vender … · Safra 2026/27" abre a venda futura com produto, tipo e safra herdados
  celular  AC-16: 390 × 844, cartões, sem rolagem horizontal, primária visível e presa ao rodapé nas três telas
  producao AC-17: Estoque de produto sem a grade Pedidos (reservar a partir do lote continua) e Previsão e colheita sem as colunas comerciais
Uso: env CHROME_BIN=… flock /tmp/cdpC.lock env CDP_GL=1 timeout 900 python3 comercial_fluxo_test.py [modo …]
Capturas em _probe/comercial_*.png. Dados sintéticos (SAFRION_DADOS=sintetico; a Lagoa Grande é sintética)."""
import sys, os, time, json
os.environ.setdefault('SAFRION_DADOS', 'sintetico')
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from cadc_lib import T
TODOS = ('menu', 'tarefa', 'erros', 'perfis', 'painel', 'celular', 'producao')
MODOS = [a for a in sys.argv[1:] if a in TODOS] or list(TODOS)
PR = os.path.join(HERE, '_probe'); os.makedirs(PR, exist_ok=True)
t = T(); J = t.J
LIB = r"""
window.N=s=>(s||'').replace(/\s+/g,' ').trim();
window.VIS=e=>{ if(!e) return false; const r=e.getBoundingClientRect(); const cs=getComputedStyle(e); return r.width>1&&r.height>1&&cs.visibility!=='hidden'&&cs.display!=='none'; };
/* cliques e campos contados na sessão (sobrevivem à troca de página pelo elo; ir(limpa) zera) */
window.CNT=(k,n)=>{ try{ sessionStorage.setItem(k,String((+sessionStorage.getItem(k)||0)+(n||1))); }catch(e){} };
window.CLK=(t,root)=>{ const r=root?document.querySelector(root):document; if(!r) return 'SEM RAIZ '+root; const els=[...r.querySelectorAll('button,a,[role=tab]')].filter(VIS);
  const e=els.find(x=>N(x.innerText)===t)||els.find(x=>N(x.innerText).startsWith(t))||els.find(x=>(x.getAttribute('aria-label')||'')===t); if(!e) return 'NÃO ACHEI: '+t; CNT('__cl'); e.click(); return 'ok'; };
window.CLK2=(t,root)=>{ const r=root?document.querySelector(root):document; const e=[...r.querySelectorAll('button,a')].filter(VIS).find(x=>N(x.innerText)===t); if(!e) return 'NÃO ACHEI: '+t; CNT('__cl',2); e.click(); e.click(); return 'ok'; };
window.SETV=(sel,val,conta)=>{ const i=document.querySelector(sel); if(!i) return 'sem '+sel; const P=i.tagName==='SELECT'?HTMLSelectElement.prototype:(i.tagName==='TEXTAREA'?HTMLTextAreaElement.prototype:HTMLInputElement.prototype);
  Object.getOwnPropertyDescriptor(P,'value').set.call(i,val); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true})); if(conta) CNT('__tx'); return 'ok'; };
window.ROW=(t)=>{ const r=[...document.querySelectorAll('[role=row]')].filter(VIS).find(x=>N(x.innerText).indexOf(t)>=0); if(!r) return 'sem linha '+t; CNT('__cl'); (r.querySelector('.g2pw')||r).click(); return 'ok'; };
window.ROWTXT=(t)=>{ const r=[...document.querySelectorAll('[role=row]')].find(x=>N(x.innerText).indexOf(t)>=0); return r?N(r.innerText):''; };
window.PAN=()=>{ const a=[...document.querySelectorAll('aside[role=dialog]')].find(VIS); return a?N(a.innerText):''; };
window.TOAST=()=>[...document.querySelectorAll('[role=status]')].map(x=>N(x.innerText)).filter(Boolean).join(' | ');
window.PRIM=()=>{ const b=[...document.querySelectorAll('header .pr-prim, header button, header a')].filter(e=>VIS(e)&&getComputedStyle(e).backgroundColor==='rgb(30, 122, 76)'); return b.map(e=>N(e.innerText)); };
window.DONO=()=>{ const e=[...document.querySelectorAll('header .com-dono')].find(VIS); return e?N(e.innerText):''; };
window.CEN=()=>JSON.parse(localStorage.getItem('talhao-os-cenario-v1')||'null')||((window.__car&&window.__car.cenGet)?window.__car.cenGet():null);
'ok'"""
def lib(): J(LIB)
def ir(pg, limpa=False, w=1440, h=1000, perfil=None):
    t.c.size(w, h)
    if limpa:
        t.c.goto(f'http://127.0.0.1:{t.p}/Main.dc.html', wait=.4); J("localStorage.clear(); sessionStorage.clear()")
    if perfil is not None:
        t.c.goto(f'http://127.0.0.1:{t.p}/Main.dc.html', wait=.3); J(f"localStorage.setItem('safrion.perfilDemo',{json.dumps(perfil)})")
    t.goto(pg); time.sleep(.5); lib()
def clk(x, root=None, w=.45): r = J(f"CLK({json.dumps(x)},{json.dumps(root)})"); time.sleep(w); return r
def setv(sel, val, conta=True): r = J(f"SETV({json.dumps(sel)},{json.dumps(val)},{'true' if conta else 'false'})"); time.sleep(.25); return r
def row(x): r = J(f"ROW({json.dumps(x)})"); time.sleep(.45); return r
def pan(): return J("PAN()") or ''
def toast(): return J("TOAST()") or ''
def shot(n): t.c.shot(os.path.join(PR, 'comercial_' + n + '.png'))
def cen(expr): return J(f"(()=>{{ const c=CEN(); return ({expr}); }})()")
def btns(): return J("[...document.querySelectorAll('aside[role=dialog] button, aside[role=dialog] a')].filter(VIS).map(b=>N(b.innerText))") or []
def mut(js):
    """prepara o estado da demonstração pelo motor da página (a mesma cenMudar das telas), sem passar pela tela testada"""
    return J("(()=>{ const {prReceber,prReservar}=window.__pr; const {comConverterSaca}=window.__com||{}; const r=window.__car.cenMudar(null,c=>{ " + js + " }); return r.erro||'ok'; })()")
SACA60 = ("['PV-030','CT-203','CRE-0095','BT-090'].forEach(id=>comConverterSaca(c,{venda:id,fat:'60',fonte:'Contrato '+id+' (teste)',ator:'Ana',chave:'T-SACA-'+id})); return {msg:''};")
COLHEITA = ("prReceber(c,{carga:'CG-2108',ticket:'TK-4520',bruto:19250,tara:7200,cond:'Íntegra',chave:'T-REC'}); "
            "prReservar(c,{pedido:'PV-036',lote:'L39-133',kg:10000,ator:'Dora',chave:'T-RS36'}); return {msg:''};")

try:
    if 'menu' in MODOS:
        print('== menu · AC-01')
        ir('VEN.dc.html', limpa=True)
        m = J("N(document.querySelector('nav[aria-label=Menu]').innerText)") or ''
        i_pr, i_co, i_ma = m.find('Produção'), m.find('Comercial'), m.find('Manutenção')
        t.chk('AC-01 grupo Comercial logo depois de Produção (antes de Manutenção)', 0 <= i_pr < i_co < i_ma, m[:400])
        itens = J("[...document.querySelectorAll('nav[aria-label=Menu] a')].map(a=>[N(a.innerText),a.getAttribute('href')]).filter(x=>['VEN.dc.html','EXPED.dc.html','PCOM.dc.html'].indexOf(x[1])>=0)") or []
        t.chk('AC-01 Comercial com 3 itens: Contratos e pedidos, Expedição e entregas, Painel comercial', [x[0] for x in itens] == ['Contratos e pedidos', 'Expedição e entregas', 'Painel comercial'], itens)
        for pg in ('VEN', 'EXPED', 'PCOM'):
            ir(pg + '.dc.html'); t.chk(f'AC-01 {pg} abre sem erro de JS e com dados do estado', not t.errs() and len(J("N(document.querySelector('main').innerText)") or '') > 200, t.errs())
            oc = J("[...document.querySelectorAll('a[href]')].map(a=>a.getAttribute('href')).filter(h=>/^(VE|LO|CO)-\\d/.test(h))") or []
            t.chk(f'AC-01 {pg} sem elo para tela oculta (VE-*, LO-*, CO-*)', not oc, oc)
        shot('menu')
    if 'tarefa' in MODOS:
        print('== tarefa · AC-14 tarefa do proprietário (§8.1), perfil Ana, cliques e campos medidos')
        ir('VEN.dc.html', limpa=True)
        t.chk('§8.1 sem seleção, a primária é "Registrar venda"', J("PRIM()") == ['Registrar venda'], J("PRIM()"))
        r = row('PV-030'); p = pan()
        t.chk('(0) A-17 PV-030 "Saca a conferir" (VE-05 oculto sc 50 kg × Colheita 60 kg): o painel pede a massa da saca com a fonte; primária "Registrar a saca do PV-030"',
              'Saca a conferir' in p and '4.000 sc (saca de 50 ou 60 kg a conferir)' in p and '50 kg' in btns() and '60 kg' in btns() and J("PRIM()") == ['Registrar a saca do PV-030'], [r, J("PRIM()"), p[:500]])
        clk('60 kg', 'aside'); t.chk('(0) escolhida a massa, o painel mostra a conta antes de gravar: 4.000 sc × 60 kg = 240.000 kg', '4.000 sc × 60 kg = 240.000 kg' in pan(), pan()[:500])
        clk('Registrar a saca', 'aside'); p = toast()
        t.chk('(0) saca de 60 kg registrada por Ana (gestora) com a fonte "Contrato CT-201": 4.000 sc = 240.000 kg; falta 125 sc', 'saca de 60 kg registrada por Ana (gestora) (Contrato CT-201)' in p and 'falta 125 sc' in p, p)
        p = pan()
        sug = J("(()=>{ const i=[...document.querySelectorAll('aside input')].find(x=>x.id.indexOf('pf_q_L10-031_PV-030')===0); return i?i.value:null; })()")
        t.chk('(1) PV-030 Parcial: o painel abre a reserva com a sugestão L10-031 · 125 sc; a primária é "Reservar lote para o PV-030"', 'Parcial' in p and 'L10-031' in p and sug == '125' and J("PRIM()") == ['Reservar lote para o PV-030'], [r, sug, J("PRIM()"), p[:400]])
        clk('Reservar', 'aside'); p = toast()
        t.chk('(1) Reservar: RS-0002 de 125 sc do L10-031 para o PV-030 (Coberto)', 'RS-0002' in p and '125 sc' in p and 'coberto' in p and 'Coberto' in (J("ROWTXT('PV-030')") or ''), [p, J("ROWTXT('PV-030')")])
        t.chk('(2) a primária passa a "Programar carga do PV-030"', J("PRIM()") == ['Programar carga do PV-030'], J("PRIM()"))
        clk('Programar carga do PV-030'); time.sleep(.9); lib(); p = pan()
        t.chk('(2) "Programar carga do PV-030" abre a Expedição com a venda herdada (cliente retira)', 'Programar carga' in p and 'PV-030' in p and 'Cliente retira' in p, p[:400])
        clk('Bitrem graneleiro 37 t', 'aside'); setv('#pf_pl', 'QZA1B23')
        pv = J("(()=>{ const i=[...document.querySelectorAll('aside input')].find(x=>x.id.indexOf('pf_pv_L10-031_Bitrem')===0); return i?i.value:null; })()")
        t.chk('(2) previsto pré-preenchido: 37.000 kg (mín da reserva sem carga e da capacidade do bitrem, KC11) e data Hoje', pv == '37000' and 'Hoje 26/09' in pan(), [pv, pan()[:300]])
        clk('Programar carga', 'aside'); p = toast()
        t.chk('(2) RM-0002 programada: 37.000 kg, bitrem QZA1B23, cliente retira', 'RM-0002 programada' in p and 'QZA1B23' in p, p)
        t.chk('(3) a carga fica selecionada e a primária é "Confirmar saída da RM-0002"', J("PRIM()") == ['Confirmar saída da RM-0002'] and 'Peso bruto' in pan(), [J("PRIM()"), pan()[:300]])
        setv('#pf_br', '51200'); setv('#pf_ta', '14240'); time.sleep(.2)
        t.chk('(3) o painel mostra o líquido antes de gravar: 36.960 kg = 616 sc', '36.960 kg = 616 sc' in pan(), pan()[:600])
        r2 = J("CLK2('Confirmar saída da RM-0002','aside[role=dialog]')"); time.sleep(.8); p = toast()
        n = cen("c.producao.movs.filter(m=>m.tipo==='expedição'&&m.rm==='RM-0002').length")
        S = cen("(()=>{ const L=c.producao.lotes['L10-031']; const f=c.producao.movs.filter(m=>m.lote==='L10-031'&&m.fis!==false).reduce((a,m)=>a+m.kg,0); const r=Object.values(c.producao.reservas).filter(r=>r.lote==='L10-031'&&r.st==='Ativa').reduce((a,r)=>a+r.kg,0); return [f,r,f-r]; })()")
        liq = cen("c.producao.expedicoes['RM-0002'].saida.liq")
        t.chk('(3) dois cliques seguidos em "Confirmar saída": um só MP de expedição; 36.960 kg (616 sc) saem; disponível do L10-031 continua 34.420 sc (2.065.200 kg)',
              r2 == 'ok' and n == 1 and liq == 36960 and S and S[2] == 2065200 and ('616 sc' in p or 'já confirmada' in p), [r2, n, liq, S, p])
        rw = J("ROWTXT('RM-0002')") or ''
        t.chk('(3) cliente retira: a RM-0002 fica Entregue, R$ 78.848,00 a receber até 26/09', 'Entregue' in rw and 'R$ 78.848,00 a receber até 26/09' in rw, [rw, p])
        clk('Painel comercial'); time.sleep(.9); lib()
        pz = J("ROWTXT('Soja em grão R$')") or J("ROWTXT('Soja em grão')") or ''; kp = J("N(document.querySelector('[aria-label=Indicadores]').innerText)") or ''
        t.chk('(4) Painel comercial: soja realizado R$ 128,00/sc e a receber R$ 170.318,00', 'R$ 128,00/sc' in (J("N(document.querySelector('main').innerText)") or '') and 'R$ 170.318,00' in kp, [pz, kp])
        cl, tx = J("[+sessionStorage.getItem('__cl')||0, +sessionStorage.getItem('__tx')||0]")
        print(f'     medida AC-14: {cl} cliques · {tx} campos digitados (placa, bruto, tara)')
        t.chk(f'AC-14 tarefa de ponta a ponta dentro de 16 cliques e 3 campos digitados ({cl} cliques · {tx} campos)', cl <= 16 and tx <= 3, [cl, tx])
        t.chk('tarefa: nenhuma página com erro de JS', not t.errs(), t.errs())
        shot('tarefa')
    if 'erros' in MODOS:
        print('== erros · recusa e repetição')
        ir('VEN.dc.html', limpa=True); nv0 = cen("Object.keys(c.producao.pedidos).length"); clk('Registrar venda'); clk('Registrar venda', 'aside'); p = pan(); n0 = cen("Object.keys(c.producao.pedidos).length")
        t.chk('Registrar venda sem cliente é recusado junto do formulário; nada gravado', 'Escolha o cliente' in p and n0 == nv0 == 7, [p[-300:], nv0, n0])
        clk('Frutas Real', 'aside'); clk('Venda futura', 'aside'); sem = J("[...document.querySelectorAll('aside [role=group][aria-label^=\"Semana\"] button')].map(b=>N(b.innerText))") or []
        t.chk('CE-02 venda futura de mamão só oferece semanas que não começaram (S40..S43, sem a S39)', sem and all(not x.startswith('S39') for x in sem) and sem[0].startswith('S40'), sem)
        clk('S42', 'aside'); setv('#pf_q', '20000'); setv('#pf_pr', '3,10'); time.sleep(.2)
        t.chk('aviso ao vivo: a S42 fica em déficit (não trava)', 'déficit' in pan(), pan()[:400])
        J("CLK2('Registrar venda','aside[role=dialog]')"); time.sleep(.8); p = toast()
        ids = cen("Object.keys(c.producao.pedidos).filter(k=>/^CT-2/.test(k)&&k!=='CT-203')") or []
        t.chk('duplo clique em "Registrar venda" grava uma venda só (CT-205, chave do formulário): o 2º clique repete a chave e o conteúdo e volta "já registrada", sem erro',
              ids == ['CT-205'] and ('CT-205 registrada' in p or 'CT-205 já registrada' in p) and 'conflito' not in pan(), [ids, p])
        # A-17: registrar a saca sem escolher a massa é recusado; 50 kg explícitos ficam na venda e a oferta continua suspensa pelos outros dois contratos
        ir('VEN.dc.html'); row('CT-203'); clk('Registrar a saca', 'aside'); p = pan()
        t.chk('A-17 "Registrar a saca" sem escolher a massa: recusa junto do formulário ("50 kg ou 60 kg"), nada gravado', 'Escolha a massa da saca escrita no contrato: 50 kg ou 60 kg' in p and not cen("c.producao.pedidos['CT-203'].fatConf"), p[-300:])
        clk('50 kg', 'aside'); clk('Registrar a saca', 'aside'); p = toast(); rw = J("ROWTXT('CT-203')") or ''
        t.chk('A-17 CT-203 com 50 kg: "12.000 sc 50 kg" a "R$ 132,00/sc 50 kg" (não reinterpretado pela saca de 60 kg da cultura); a oferta 26/27 segue suspensa por CRE-0095 e BT-090',
              '12.000 sc 50 kg' in rw and 'R$ 132,00/sc 50 kg' in rw and 'continua suspensa até registrar CRE-0095, BT-090' in p, [rw, p])
        # crédito da Frutas Real (KC09) e saída impedida
        ir('VEN.dc.html'); mut(COLHEITA); ir('VEN.dc.html')
        t.chk('KC09 depois da tarefa da Colheita: PV-036 "Aguardando crédito"', 'Aguardando crédito' in (J("ROWTXT('PV-036')") or ''), J("ROWTXT('PV-036')"))
        ir('VEN.dc.html', perfil='Rui'); row('PV-036'); d = J("DONO()"); pr = J("PRIM()")
        t.chk('AC-12 Rui (expedição) vê o dono no lugar do botão: "Ana (gestora): aprovar crédito do PV-036"', d.startswith('Ana (gestora)') and 'aprovar crédito do PV-036' in d and not pr, [d, pr])
        ir('EXPED.dc.html#nova:PV-036', perfil='Dora'); clk('Rota Sul Transportes', 'aside'); clk('Baú refrigerado 12 t', 'aside'); setv('#pf_pl', 'RSU2E45'); clk('Programar carga', 'aside')
        t.chk('Dora (comercial) programa a carga do PV-036: RM-0002, Rota Sul, baú refrigerado', cen("c.producao.expedicoes['RM-0002']&&c.producao.expedicoes['RM-0002'].quem") == 'Dora (comercial)', toast())
        t.chk('a carga aparece "Programada · impedida: crédito · Ana (gestora) aprova no PV-036"', 'impedida: crédito' in (J("ROWTXT('RM-0002')") or ''), J("ROWTXT('RM-0002')"))
        ir('EXPED.dc.html#RM-0002', perfil='Rui'); time.sleep(.3)
        t.chk('a saída impedida no crédito não vira primária (o próximo passo diz quem resolve)', not J("PRIM()") and 'Saída impedida no crédito' in pan(), [J("PRIM()"), pan()[:300]])
        ir('VEN.dc.html#PV-036', perfil='Ana'); time.sleep(.3); clk('Aprovar crédito do PV-036', 'aside'); p = toast()
        t.chk('Ana aprova o crédito até R$ 121.970,00', 'aprovado por Ana (gestora) até R$ 121.970,00' in p, p)
        ir('EXPED.dc.html#RM-0002', perfil='Rui'); time.sleep(.3); setv('#pf_br', '7200'); setv('#pf_ta', '7200'); clk('Confirmar saída da RM-0002', 'aside'); p = pan()
        t.chk('tara ≥ bruto é recusada junto do formulário; nada baixado', 'maior que zero' in p and cen("c.producao.movs.filter(m=>m.rm==='RM-0002').length") == 0, p[-300:])
        setv('#pf_br', '17240'); setv('#pf_ta', '7200'); time.sleep(.2); p = pan()
        t.chk('KC18 o painel avisa o excesso de 40 kg e o crédito antes de gravar (decisão de Ana)', 'Excesso de 40 kg' in p and 'Crédito' in p, p[:700])
        clk('Confirmar saída da RM-0002', 'aside'); p = pan()
        t.chk('KC18 Rui não confirma o excesso: "decisão de Ana (gestora)", nada baixado', 'decisão de Ana (gestora)' in p and cen("c.producao.movs.filter(m=>m.rm==='RM-0002').length") == 0, p[-300:])
        setv('#pf_br', '17200'); clk('Confirmar saída da RM-0002', 'aside'); p = toast()
        t.chk('Rui confirma a saída de 10.000 kg: em trânsito, grava Rui (expedição)', 'Em trânsito' in p and cen("c.producao.expedicoes['RM-0002'].saida.quem") == 'Rui (expedição)', p)
        clk('Hoje 26/09', 'aside'); clk('Com devolução', 'aside'); setv('#pf_dq', '400'); clk('Maturação avançada', 'aside'); clk('Confirmar entrega da RM-0002', 'aside'); p = toast()
        lote = cen("(c.producao.expedicoes['RM-0002'].devs[0]||{}).lote") or ''
        t.chk('KC10 entrega com devolução de 400 kg: lote novo Em inspeção, R$ 29.280,00 a receber até 24/10', bool(lote) and 'Em inspeção' in p and 'R$ 29.280,00 a receber até 24/10' in p, [lote, p])
        ir('PROD.dc.html#' + lote, perfil='Ana'); time.sleep(.3); p = pan()
        t.chk('o lote devolvido aparece Em inspeção no Estoque de produto com "Liberar lote · Qualidade"', 'Em inspeção' in p and 'Liberar ' + lote in btns(), [p[:300], btns()])
        t.chk('erros: nenhuma página com erro de JS', not t.errs(), t.errs())
        shot('erros')
    if 'perfis' in MODOS:
        print('== perfis · AC-12')
        ir('VEN.dc.html', limpa=True, perfil='Caio'); d = J("DONO()")
        t.chk('Caio (PCP): sem "Registrar venda"; a primária diz o dono', not J("PRIM()") and d.startswith('Ana (gestora) ou Dora (comercial)'), [J("PRIM()"), d])
        ir('VEN.dc.html', perfil='Dora'); t.chk('Dora (comercial) registra venda', J("PRIM()") == ['Registrar venda'], J("PRIM()"))
        row('PV-030'); clk('60 kg', 'aside'); clk('Registrar a saca', 'aside'); clk('Reservar', 'aside'); clk('Programar carga do PV-030'); time.sleep(.9); lib()
        clk('Bitrem graneleiro 37 t', 'aside'); setv('#pf_pl', 'ABC1D23'); clk('Programar carga', 'aside'); d = J("DONO()")
        t.chk('Dora programa a carga mas não confirma a saída: a primária mostra "Ana (gestora) ou Rui (expedição)"', not J("PRIM()") and d.startswith('Ana (gestora) ou Rui (expedição)') and 'Peso bruto' not in pan(), [J("PRIM()"), d])
        rs = cen("[c.producao.reservas['RS-0002'].quem, c.producao.pedidos['PV-030'].fatConf.quem]")
        t.chk('a saca e a reserva gravam Dora (comercial), não um nome fixo', rs == ['Dora (comercial)', 'Dora (comercial)'], rs)
        shot('perfis')
    if 'painel' in MODOS:
        print('== painel · AC-11')
        ir('PCOM.dc.html', limpa=True)
        es0, sf0 = (J("ROWTXT('Estoque (2025/26)')") or ''), (J("ROWTXT('Safra 2026/27')") or '')
        t.chk('A-17 semente: soja Estoque (2025/26) e Safra 2026/27 "suspenso · saca a conferir" (PV-030; CT-203, CRE-0095, BT-090), sem número inventado',
              'suspenso' in es0 and 'saca a conferir: PV-030' in es0 and 'Suspenso' in es0 and 'saca a conferir: CT-203, CRE-0095, BT-090' in sf0 and '48.280' not in sf0, [es0, sf0])
        t.chk('A-17 semente: sem linha com livre, a primária é o passo que destrava: "Registrar a saca do PV-030" (abre a venda)', J("PRIM()") == ['Registrar a saca do PV-030'] and J("[...document.querySelectorAll('header a')].some(a=>(a.getAttribute('href')||'').endsWith('VEN.dc.html#PV-030'))"), J("PRIM()"))
        ir('VEN.dc.html'); mut(SACA60); ir('PCOM.dc.html'); mt = J("N(document.querySelector('main').innerText)") or ''
        es, sf, me, m41 = (J("ROWTXT('Estoque (2025/26)')") or ''), (J("ROWTXT('Safra 2026/27')") or ''), (J("ROWTXT('Estoque 0 kg')") or ''), (J("ROWTXT('S41')") or '')
        t.chk('AC-11 soja (saca de 60 kg registrada): Estoque (2025/26) 38.420 sc apto · 4.000 sc · 3.875 sc · 34.420 sc · Livre', '38.420 sc apto' in es and '4.000 sc' in es and '3.875 sc' in es and '34.420 sc' in es and 'Livre' in es, es)
        t.chk('AC-11 soja: Safra 2026/27 68.180 sc publicada · 19.900 sc · 48.280 sc', '68.180 sc publicada' in sf and '19.900 sc' in sf and '48.280 sc' in sf, sf)
        t.chk('AC-11 mamão: Estoque 0 kg apto, déficit 10.000 kg; S41 sem versão publicada, déficit 30.000 kg', 'déficit 10.000 kg' in me and 'sem versão publicada' in m41 and 'déficit 30.000 kg' in m41, [me, m41])
        t.chk('AC-11 preço: soja R$ 131,00/sc contratado; mamão R$ 3,05/kg contratado e R$ 3,00/kg realizado; a receber R$ 91.470,00; referência sintética',
              'R$ 131,00/sc' in mt and 'R$ 3,05/kg' in mt and 'R$ 3,00/kg' in mt and 'R$ 91.470,00' in mt and 'R$ 129,40/sc' in mt, mt[:900])
        t.chk('AC-11 sem seleção, a primária é vender a primeira linha com livre: "Vender Soja em grão · Estoque (2025/26)"', J("PRIM()") == ['Vender Soja em grão · Estoque (2025/26)'], J("PRIM()"))
        row('Safra 2026/27'); t.chk('selecionada a safra 26/27, a primária é "Vender Soja em grão · Safra 2026/27"', J("PRIM()") == ['Vender Soja em grão · Safra 2026/27'], J("PRIM()"))
        clk('Fechar', 'aside'); clk('Vender Soja em grão · Safra 2026/27'); time.sleep(.9); lib()
        on = J("[...document.querySelectorAll('aside [aria-pressed=true]')].map(b=>N(b.innerText))") or []
        t.chk('#nova:<produto>:<período> abre "Registrar venda" com Soja em grão, Venda futura e Safra 2026/27 herdados', 'Venda futura' in on and any(x.startswith('Soja em grão') for x in on) and any(x.startswith('Safra 2026/27') for x in on), on)
        t.chk('painel: nenhuma página com erro de JS', not t.errs(), t.errs())
        shot('painel')
    if 'celular' in MODOS:
        print('== celular · AC-16 em 390 × 844')
        for pg in ('VEN', 'EXPED', 'PCOM'):
            ir(pg + '.dc.html', limpa=True, w=390, h=844)
            if pg == 'EXPED':   # na semente nada dá para programar (PV-030 com a saca a conferir): registrada a saca, "Programar carga" volta a ser a primária
                t.chk('EXPED na semente sem "Programar carga" (nenhuma venda com reserva sem carga); o estado diz o que falta', not J("PRIM()") and 'reserve lote em Contratos e pedidos' in (J("N(document.querySelector('header').innerText)") or ''), J("PRIM()"))
                ir('VEN.dc.html', w=390, h=844); mut(SACA60); ir('EXPED.dc.html', w=390, h=844)
            m = J("(()=>{ const m=document.querySelector('main'); return [document.documentElement.scrollWidth, m.scrollWidth-m.clientWidth, [...document.querySelectorAll('.pr-card')].filter(VIS).length, [...document.querySelectorAll('.g2rola')].filter(VIS).length]; })()")
            b = J("(()=>{ const b=[...document.querySelectorAll('.pr-prim')].find(VIS); if(!b) return null; const r=b.getBoundingClientRect(); return [N(b.innerText), Math.round(r.top), Math.round(r.bottom), innerHeight, getComputedStyle(b).position]; })()")
            t.chk(f'AC-16 {pg}: cartões no lugar da tabela, sem rolagem horizontal', m and m[0] <= 390 and m[1] <= 0 and m[2] > 0 and m[3] == 0, m)
            t.chk(f'AC-16 {pg}: ação primária visível e presa ao rodapé', b and b[4] == 'fixed' and b[2] <= b[3] and b[1] > b[3] - 140, b)
            shot('390_' + pg)
        ir('VEN.dc.html', w=390, h=844); clk('PV-030 · Coop Grão Sul'); p = pan()
        t.chk('AC-16 tocar no cartão abre o painel da venda (master-detail no celular): PV-030 pede registrar a saca (A-17)', 'PV-030' in p and 'Coop Grão Sul' in p and 'Registrar a saca' in p, p[:200])
    if 'producao' in MODOS:
        print('== producao · AC-17 Estoque de produto sem Pedidos; Previsão e colheita sem as colunas comerciais')
        ir('VEN.dc.html', limpa=True); mut(SACA60); ir('PROD.dc.html'); mt = J("N(document.querySelector('main').innerText)") or ''
        t.chk('AC-17 Estoque de produto só com lotes (sem a grade Pedidos: ela está em Contratos e pedidos)', 'Lotes de produto' in mt and 'Pedido · cliente' not in mt and not (J("ROWTXT('PV-036')") or ''), mt[:300])
        row('L10-031'); p = pan()
        t.chk('AC-17 reservar a partir do lote continua (L10-031 → PV-030, 125 sc)', 'PV-030' in p and 'Reservar' in btns(), [p[:300], btns()])
        ir('COLH.dc.html'); clk('Por semana'); hd = J("[...document.querySelectorAll('[role=columnheader]')].filter(VIS).map(x=>N(x.innerText))") or []
        t.chk('AC-17 Previsão e colheita › Por semana sem "Vendas futuras" e "Oferta livre" (vão ao Painel comercial)', hd and not any(h.startswith('Vendas futuras') or h.startswith('Oferta livre') for h in hd) and 'Painel comercial' in (J("N(document.querySelector('main').innerText)") or ''), hd)
        t.chk('producao: nenhuma página com erro de JS', not t.errs(), t.errs())
finally:
    t.fim()   # imprime RESULTADO
sys.exit(0 if all(t.ok) else 1)
