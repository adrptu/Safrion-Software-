# -*- coding: utf-8 -*-
"""Beneficiamento BEN-1 · teste de navegador do fluxo principal (docs/beneficiamento/ESPECIFICACAO.md §11.3 E01-E12, §11.7; DECISOES §12).
Modos (um por vez, cada um abre o Chrome headless do cadc_lib.T; o cenário começa limpo):
  fluxo    tarefa do proprietário (§11.7) no desktop, com cliques e campos digitados medidos (linha de base, AC-36): menu Produção ›
           Beneficiamento; OB-0112 recusa com as duas causas e quem resolve; OB-0110 concluir, conferir (Paula), fechar recusado pela
           custódia; devolução no Estoque (Rui); fechar: L39-120 e L39-121 em inspeção; no Estoque de produto a Qualidade (Marta) registra
           o resultado e libera; o Comercial reserva a sugestão para o PV-031 e a falta aparece; retirar o L39-119 e liberar a OB-0112
           (REQ-041 no Estoque); e a integração com a Colheita: o L39-131 (recebido em processo) abre uma ordem nova pelo atalho.
  erros    recusas e repetição pela tela: perfil sem papel recusado sem gravar; massa pesada acima da entrada; caixas acima da custódia;
           estorno com motivo e relançamento herdado; justificativa acima da alçada decide a gestão; toque duplo no Registrar grava uma vez;
           formulário aberto em versão antiga recebe conflito; navegar (atalhos) nunca grava.
  celular  390 × 844: cartões, sem rolagem lateral, ação primária visível e painel inteiro (BEN e Estoque de produto).
Uso: env CHROME_BIN=… flock /tmp/cdpB.lock env CDP_GL=1 timeout 900 python3 ben_fluxo_test.py [fluxo|erros|celular]
Capturas em _probe/ben_*.png. Dados sintéticos (SAFRION_DADOS=sintetico)."""
import sys, os, time, json
os.environ.setdefault('SAFRION_DADOS', 'sintetico')
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from cadc_lib import T
MODOS = [a for a in sys.argv[1:] if a in ('fluxo', 'erros', 'celular')] or ['fluxo', 'erros', 'celular']
PR = os.path.join(HERE, '_probe'); os.makedirs(PR, exist_ok=True)
t = T(); J = t.J
LIB = r"""
window.N=s=>(s||'').replace(/\s+/g,' ').trim();
window.VIS=e=>{ if(!e) return false; const r=e.getBoundingClientRect(); const cs=getComputedStyle(e); return r.width>1&&r.height>1&&cs.visibility!=='hidden'&&cs.display!=='none'; };
window.__cl=window.__cl||0; window.__tx=window.__tx||0;
window.CLK=(t,root)=>{ const r=root?document.querySelector(root):document; if(!r) return 'SEM RAIZ '+root; const els=[...r.querySelectorAll('button,a,[role=tab],[role=button]')].filter(VIS);
  const e=els.find(x=>N(x.innerText)===t)||els.find(x=>N(x.innerText).startsWith(t))||els.find(x=>(x.getAttribute('aria-label')||'')===t); if(!e) return 'NÃO ACHEI: '+t; window.__cl++; e.click(); return 'ok'; };
window.SETV=(sel,val,conta)=>{ const i=document.querySelector(sel); if(!i) return 'sem '+sel; const P=i.tagName==='SELECT'?HTMLSelectElement.prototype:(i.tagName==='TEXTAREA'?HTMLTextAreaElement.prototype:HTMLInputElement.prototype);
  Object.getOwnPropertyDescriptor(P,'value').set.call(i,val); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true})); if(conta) window.__tx++; return 'ok'; };
window.ROW=(t)=>{ const r=[...document.querySelectorAll('[role=row]')].filter(VIS).find(x=>N(x.innerText).indexOf(t)>=0); if(!r) return 'sem linha '+t; window.__cl++; (r.querySelector('.g2pw')||r.querySelector('[role=cell] span')||r).click(); return 'ok'; };
window.ROWTXT=(t)=>{ const r=[...document.querySelectorAll('[role=row]')].find(x=>N(x.innerText).indexOf(t)>=0); return r?N(r.innerText):''; };
window.PAN=()=>{ const a=[...document.querySelectorAll('aside[role=dialog]')].find(VIS); return a?N(a.innerText):''; };
window.TOAST=()=>[...document.querySelectorAll('[role=status]')].map(x=>N(x.innerText)).filter(Boolean).join(' | ');
window.PRIM=()=>{ const b=[...document.querySelectorAll('header .pr-prim, header button, header a')].filter(e=>VIS(e)&&getComputedStyle(e).backgroundColor==='rgb(30, 122, 76)'); return b.map(e=>N(e.innerText)); };
window.PPRIM=()=>{ const a=[...document.querySelectorAll('aside[role=dialog]')].find(VIS); if(!a) return []; return [...a.querySelectorAll('button,a')].filter(e=>VIS(e)&&getComputedStyle(e).backgroundColor==='rgb(30, 122, 76)').map(e=>N(e.innerText)); };
window.CEN=()=>JSON.parse(localStorage.getItem('talhao-os-cenario-v1')||'null');
window.PERFIL=(k)=>{ localStorage.setItem('safrion.perfilDemo',k); return k; };
'ok'"""
def lib(): J(LIB)
def ir(pg, limpa=False, w=1440, h=1000):
    t.c.size(w, h)
    if limpa:
        t.c.goto(f'http://127.0.0.1:{t.p}/Main.dc.html', wait=.4); J("localStorage.clear(); sessionStorage.clear()")
    cl, tx = (J("[window.__cl||0, window.__tx||0]") or [0, 0]) if not limpa else (0, 0)
    t.goto(pg); time.sleep(.6); lib(); J(f"window.__cl={cl}; window.__tx={tx};")
def clk(x, root=None, w=.45): r = J(f"CLK({json.dumps(x)},{json.dumps(root)})"); time.sleep(w); return r
def setv(sel, val, conta=True): r = J(f"SETV({json.dumps(sel)},{json.dumps(val)},{'true' if conta else 'false'})"); time.sleep(.25); return r
def row(x): r = J(f"ROW({json.dumps(x)})"); time.sleep(.5); return r
def pan(): return J("PAN()") or ''
def toast(): return J("TOAST()") or ''
def shot(n): t.c.shot(os.path.join(PR, 'ben_' + n + '.png'))
def cen(expr): return J(f"(()=>{{ const c=CEN()||{{}}; return ({expr}); }})()")
def perfil(k): J(f"PERFIL({json.dumps(k)})"); time.sleep(.1)
def rev(): return cen("c.rev||0")
def est_secao(i): J(f"document.querySelectorAll('nav[aria-label=\"Seções do estoque\"] button')[{i - 1}].click()"); time.sleep(.5)

try:
    if 'fluxo' in MODOS:
        print('== fluxo · tarefa do proprietário (§11.7) de ponta a ponta, com cliques e campos medidos')
        ir('BEN.dc.html', limpa=True)
        t.chk('BEN abre sem erro de JS', not t.errs(), t.errs())
        m = J("N(document.querySelector('nav[aria-label=Menu]').innerText)") or ''
        itens = J("[...document.querySelectorAll('nav[aria-label=Menu] a')].map(a=>[N(a.innerText),a.getAttribute('href')]).filter(x=>['COLH.dc.html','CARGA.dc.html','BEN.dc.html','PROD.dc.html'].indexOf(x[1])>=0)") or []
        t.chk('(1) menu: Produção › Beneficiamento entre Cargas e recebimento e Estoque de produto (4 itens, no fluxo do recebido ao estoque)',
              [x[0] for x in itens] == ['Previsão e colheita', 'Cargas e recebimento', 'Beneficiamento', 'Estoque de produto'] and m.find('Produção') < m.find('Manutenção'), itens)
        clk('Kanban', '[aria-label="Visão das ordens"]', w=.7)
        kb = J("[...document.querySelectorAll('[aria-label=\"Kanban das ordens\"] > *')].filter(VIS).map(x=>N(x.innerText).slice(0,40))")
        t.chk('Kanban com exatamente 5 fases e a contagem da semente (A liberar 1, Em execução 1)', len(kb or []) == 5 and kb[0].lower().startswith('a liberar 1') and kb[2].lower().startswith('em execução 1') and kb[4].lower().startswith('encerradas 0'), kb)
        J("window.__cl=0"); clk('Lista')
        t.chk('sem seleção, a ação primária do cabeçalho é a da 1ª ordem com passo: "Autorizar rota e liberar · OB-0112"', J("PRIM()") == ['Autorizar rota e liberar · OB-0112'], J("PRIM()"))
        shot('lista')
        # (2) OB-0112: autorizar e liberar recusa com as duas causas e quem resolve (Igor age)
        perfil('Igor'); r0 = rev(); clk('Autorizar rota e liberar · OB-0112'); p = pan()
        t.chk('(2) painel da OB-0112 lista as duas causas antes do toque, cada uma com dono e atalho', 'L39-119 em inspeção (INSP-94) · Marta (qualidade)' in p and 'Caixa de mamão Formosa 10 kg: 540 un disponíveis para 881 un · Estoque' in p
              and 'Receber a devolução da OB-0110 no Estoque' in p and 'Retirar L39-119 da ordem' in p, p[:900])
        clk('Autorizar rota e liberar', 'aside'); p = pan()
        t.chk('(2) "Autorizar rota e liberar" recusa com as 2 causas; nada gravado (fase e revisão iguais)', 'Liberação recusada · 2 causas' in p and cen("c.ordens['OB-0112'].etapa") == 'A liberar' and rev() == r0, [p[-400:], rev(), r0])
        clk('Fechar', 'aside')
        # (3) OB-0110: concluir, conferir (Paula), fechar recusado pela custódia
        row('OB-0110'); p = pan()
        t.chk('(3) OB-0110 Em execução: balanço com as razões de K01 (A 80,00 %, B 15,00 %, descarte 5,00 %, recuperação 95,00 %) e primária "Concluir execução"', all(x in p for x in ('80,00 %', '15,00 %', '5,00 %', '95,00 %')) and J("PPRIM()") == ['Concluir execução'] and 'Fechar processo' not in p, [J("PPRIM()"), p[:600]])
        clk('Concluir execução', 'aside'); et = cen("c.ordens['OB-0110'].etapa")
        perfil('Paula'); clk('Conferir balanço', 'aside'); cf = cen("(c.ordens['OB-0110'].ben.conf||{}).quem")
        t.chk('(3) Concluir (Igor) → Em conferência; Conferir balanço gravado em nome da Paula (conferência), diferença 0', et == 'Em conferência' and cf == 'Paula (conferência)', [et, cf, toast()])
        perfil('Igor'); clk('Fechar processo', 'aside'); p = pan()
        t.chk('(3) Fechar recusado: "Sobra em custódia: Caixa de mamão Formosa 10 kg 60 un. Receba a devolução no Estoque."', 'Sobra em custódia: Caixa de mamão Formosa 10 kg 60 un. Receba a devolução no Estoque.' in p and cen("c.ordens['OB-0110'].etapa") == 'Em conferência', p[-300:])
        # devolução no Estoque (Rui, almoxarife)
        ir('EST.dc.html'); perfil('Rui'); est_secao(3)
        r = J("(()=>{ const rw=[...document.querySelectorAll('[role=row]')].find(x=>N(x.innerText).indexOf('REQ-030')>=0); if(!rw) return 'sem linha'; window.__cl++; (rw.querySelector('[role=cell] span')||rw).click(); return 'ok'; })()"); time.sleep(.5)
        q = J("(document.querySelector('#fx_g_dev_qtd')||{}).value"); clk('Salvar', 'aside[role=dialog]'); time.sleep(.3)
        st = cen("[c.reqs['REQ-030'].itens[0].custodia, c.lotes['Caixa de mamão Formosa 10 kg|CX26-01'].fisico]")
        t.chk('(3) Estoque › Receba devoluções: REQ-030 sugere 60 un; devolução apta: custódia 0 e CX26-01 540 → 600 un', r == 'ok' and q == '60' and st == [0, 600], [r, q, st, toast()])
        ir('BEN.dc.html#OB-0110'); perfil('Igor'); time.sleep(.3); clk('Fechar processo', 'aside'); p = toast()
        st = cen("[c.ordens['OB-0110'].etapa, c.producao.lotes['L39-120']&&c.producao.lotes['L39-120'].q0, c.producao.lotes['L39-121']&&c.producao.lotes['L39-121'].q0, c.producao.ben.insp['INSP-92'].prazo]")
        t.chk('(3) Fechar: OB-0110 Encerradas; L39-120 e L39-121 Em inspeção (INSP-92, Marta, prazo 28/09); "Fechar não libera"', st == ['Encerradas', 'Em inspeção', 'Em inspeção', '2026-09-28'] and 'Fechar não libera' in p, [st, p])
        p = pan(); t.chk('painel da ordem encerrada: lotes gerados com link ao Estoque de produto; nenhuma primária', 'lotes gerados' in p.lower() and 'abrir no estoque de produto' in p.lower() and J("PPRIM()") == [], [J("PPRIM()"), p[:300]])
        shot('ob0110_fechada')
        # (4) Estoque de produto: Qualidade (Marta) registra resultado e libera; Comercial reserva
        ir('PROD.dc.html#L39-120'); time.sleep(.4); p = pan()
        t.chk('(4) L39-120 no Estoque de produto: Em inspeção, INSP-92, primária "Registrar resultado"; reservar não é oferecido', 'INSP-92' in p and J("PPRIM()") == ['Registrar resultado'] and 'Reservar' not in ' '.join(J("PPRIM()") or []), [J("PPRIM()"), p[:500]])
        perfil('Marta'); clk('Conforme', 'aside'); clk('Registrar resultado', 'aside'); p1 = toast()
        clk('Liberar', 'aside'); clk('Registrar decisão', 'aside'); p2 = toast()
        t.chk('(4) Marta: resultado Conforme e decisão Liberar → L39-120 Liberado; a OB-0110 continua Encerradas', 'Conforme por Marta (qualidade)' in p1 and 'liberado (CMD-24) por Marta (qualidade)' in p2
              and cen("c.producao.lotes['L39-120'].q0") == 'Liberado' and cen("c.ordens['OB-0110'].etapa") == 'Encerradas', [p1, p2])
        ir('PROD.dc.html#L39-120'); time.sleep(.4); perfil('Ana')
        clk('Reservar L39-120 para pedido', 'aside'); sug = J("(document.querySelector('aside [id^=pf_q_L39-120_PV-031]')||{}).value"); clk('Reservar', 'aside'); p = toast()
        st = cen("[Object.values(c.producao.reservas).filter(r=>r.lote==='L39-120'&&r.st==='Ativa').map(r=>r.id+':'+r.kg).join(','), c.producao.pedidos['PV-031'].qtd]")
        t.chk('(4) Reservar para pedido: PV-031 sugerido, quantidade 9600 (o lote não cobre o pedido inteiro); RS-0002 de 9.600 kg', sug == '9600' and st[0] == 'RS-0002:9600', [sug, st, p])
        row('PV-031'); p = pan()
        t.chk('(4) PV-031 mostra a falta de 400 kg (parcial)', 'falta 400 kg' in p.lower() and 'Parcial' in p, p[:500])
        # (5) OB-0112: retirar o L39-119 e liberar → REQ-041 no Estoque
        ir('BEN.dc.html#OB-0112'); perfil('Igor'); time.sleep(.3); clk('Retirar L39-119 da ordem', 'aside'); p = toast()
        clk('Autorizar rota e liberar', 'aside'); p2 = toast()
        st = cen("[c.ordens['OB-0112'].etapa, c.ordens['OB-0112'].req, c.ordens['OB-0112'].versao, c.reqs['REQ-041']&&c.reqs['REQ-041'].itens[0].solicitado]")
        t.chk('(5) Retirar o L39-119 (v2, 6.140 kg, 584 un) e liberar: Liberadas, REQ-041 com 584 un (CMD-42 e CMD-06)', st == ['Liberadas', 'REQ-041', 'v2', 584] and 'CMD-42' in p2 and 'CMD-06' in p2, [st, p, p2])
        ir('EST.dc.html'); est_secao(2); t.chk('(5) a REQ-041 da OB-0112 aparece em Entregue por O.S.', 'OB-0112' in (J("ROWTXT('REQ-041')") or ''), J("ROWTXT('REQ-041')"))
        cl, tx = J("[window.__cl, window.__tx]")
        print(f'MEDIDA tarefa do proprietário (§11.7): {cl} cliques/toques e {tx} campos digitados (linha de base, AC-36)')
        t.chk('(medida) tarefa do proprietário em até 30 toques e sem campo digitado (só toques: a quantidade e as caixas vêm sugeridas)', cl <= 30 and tx == 0, [cl, tx])
        # integração com a Colheita: o L39-131 (recebido em processo, pós-colheita do CAR0) abre uma ordem pelo atalho do Estoque de produto
        ir('PROD.dc.html#L39-131'); time.sleep(.4); p = pan()
        t.chk('Colheita → Beneficiamento: L39-131 em processo no Estoque de produto com o atalho "Abrir ordem de beneficiamento" (só navega)', 'Abrir ordem de beneficiamento' in p and rev() == cen("c.rev||0"), p[:400])
        r0 = rev(); clk('Abrir ordem de beneficiamento', 'aside', w=1.0); lib(); time.sleep(.4); p = pan()
        t.chk('o atalho abre a ordem nova com o L39-131 marcado, a rota única (PACK-FRU v3) e as caixas sugeridas (2.292); navegar não gravou', 'Nova ordem' in p and 'PACK-FRU v3' in p and '2292' in J("(document.querySelector('aside [id^=pf_cx_]')||{}).value||''") and rev() == r0,
              [p[:500], J("(document.querySelector('aside [id^=pf_cx_]')||{}).value")])
        perfil('Igor'); clk('Criar ordem', 'aside'); st = cen("c.ordens['OB-0113']&&[c.ordens['OB-0113'].etapa,c.ordens['OB-0113'].ben.ent[0].lote,c.ordens['OB-0113'].ins[0].tot]")
        t.chk('Criar ordem: OB-0113 A liberar com o L39-131 e 2.292 caixas; nada reservado antes de liberar', st == ['A liberar', 'L39-131', 2292] and not cen("c.producao.lotes['L39-131'].ordem"), [st, toast()])
        shot('fluxo_fim')
        t.chk('fluxo sem erro de JS', not t.errs(), t.errs())
    if 'erros' in MODOS:
        print('== erros · recusas, estorno e repetição pela tela')
        ir('BEN.dc.html#OB-0110', limpa=True); time.sleep(.3)
        r0 = rev(); perfil('Ana'); clk('Concluir execução', 'aside'); p = pan()
        t.chk('perfil sem o papel (Ana) recusado: "decisão de Igor (responsável de produção)", nada gravado', 'decisão de Igor (responsável de produção)' in p and rev() == r0 and cen("c.ordens['OB-0110'].etapa") == 'Em execução', p[-200:])
        perfil('Igor'); clk('+ Registrar saída', 'aside'); clk('Produto', 'aside'); clk('A', 'aside'); setv('#pf_cx', '10'); setv('#pf_br', '106'); clk('Registrar', 'aside'); p = pan()
        t.chk('massa pesada não se cria: +100 kg de A recusado com as parcelas, nada gravado', 'Saídas pesadas 12.100 kg > entrada 12.000 kg + tolerância 12 kg' in p and rev() == r0, p[-300:])
        setv('#pf_cx', '61'); setv('#pf_br', '600'); clk('Registrar', 'aside'); p = pan()
        t.chk('caixas acima da custódia: "Caixas acima da custódia: 60 un. Peça a entrega no Estoque."', 'Caixas acima da custódia: 60 un. Peça a entrega no Estoque.' in p and rev() == r0, p[-300:])
        clk('Cancelar', 'aside'); row('OB-0110'); clk('Estornar S-02', 'aside'); clk('Confirmar estorno de S-02', 'aside'); p = pan()
        t.chk('estorno sem motivo recusado', 'motivo do estorno' in p and rev() == r0, p[-300:])
        clk('Pesagem refeita', 'aside'); clk('Confirmar estorno de S-02', 'aside'); p = pan(); st = cen("[c.ordens['OB-0110'].ben.sai[1].estorno&&c.ordens['OB-0110'].ben.sai[1].estorno.motivo, c.reqs['REQ-030'].itens[0].custodia, c.movs.slice(-1)[0].tipo]")
        t.chk('estorno com motivo: S-02 riscada, 180 cx voltam à custódia (240), MV estorno-consumo; o relançamento abre herdando fluxo e classe', st == ['Pesagem refeita', 240, 'estorno-consumo'] and 'relançar s-02' in p.lower()
              and J("[...document.querySelectorAll('aside button[aria-pressed=true]')].map(b=>N(b.innerText)).join('|')") == 'Produto|B', [st, J("[...document.querySelectorAll('aside button[aria-pressed=true]')].map(b=>N(b.innerText)).join('|')"), p[p.lower().find('relançar'):][:120]])
        setv('#pf_cx', '180'); setv('#pf_br', '1808'); J("(()=>{ const b=[...document.querySelectorAll('aside button')].find(x=>N(x.innerText)==='Registrar'); b.click(); b.click(); })()"); time.sleep(.6)
        n = cen("c.ordens['OB-0110'].ben.sai.filter(s=>!s.estorno).length"); nm = cen("c.movs.filter(m=>m.tipo==='consumo').length")
        t.chk('toque duplo no Registrar (mesma chave): 1 registro novo e 1 MV de consumo', n == 3 and nm == 1, [n, nm, toast()])
        row('OB-0110'); clk('Concluir execução', 'aside'); clk('Justificar diferença', 'aside'); clk('Perda não identificada', 'aside'); setv('#pf_tj', 'fruta caída na esteira'); clk('Justificar diferença', 'aside'); p = pan()
        t.chk('diferença de 100 kg (0,83 %): Igor recusado "0,83 % > alçada de 0,5 %: decide Ana (gestora)"', '0,83 % > alçada de 0,5 %: decide Ana (gestora)' in p, p[-300:])
        perfil('Ana'); clk('Justificar diferença', 'aside'); p = toast()
        t.chk('Ana (gestora) justifica; a Paula confere depois', 'justificada por Ana (gestora)' in p, p)
        # formulário aberto com a versão antiga: conflito (outro quadro gravou antes)
        ir('BEN.dc.html#OB-0110'); perfil('Igor'); time.sleep(.3); clk('+ Registrar perda', 'aside'); clk('Avaria no manuseio', 'aside')
        J("(()=>{ const c=JSON.parse(localStorage.getItem('talhao-os-cenario-v1')); c.ordens['OB-0110'].ver+=1; c.rev+=1; localStorage.setItem('talhao-os-cenario-v1',JSON.stringify(c)); })()")
        setv('#pf_kg', '5'); setv('#pf_tk', 'TK-5561'); setv('#pf_mo', 'perda pesada'); clk('Registrar', 'aside'); p = pan()
        t.chk('dois quadros: o formulário aberto antes de outra gravação recebe "A OB-0110 mudou depois que você abriu", nada gravado', 'A OB-0110 mudou depois que você abriu' in p and cen("c.ordens['OB-0110'].ben.sai.length") == 4, p[-300:])
        # navegar nunca grava: atalhos do painel e do Estoque de produto
        ir('BEN.dc.html#OB-0112'); r0 = rev(); hs = J("[...document.querySelectorAll('aside a')].map(a=>a.getAttribute('href'))")
        t.chk('atalhos da OB-0112 (devolução no Estoque, lote no Estoque de produto) só navegam; revisão igual', 'EST.dc.html' in (hs or []) and rev() == r0, hs)
        shot('erros')
        t.chk('erros sem erro de JS', not t.errs(), t.errs())
    if 'celular' in MODOS:
        print('== celular · 390 × 844')
        ir('BEN.dc.html', limpa=True, w=390, h=844); time.sleep(.4)
        m = J("(()=>{ const vw=innerWidth; return {lado:document.documentElement.scrollWidth>vw+1||document.body.scrollWidth>vw+1, cards:[...document.querySelectorAll('.pr-card')].filter(VIS).length,"
              "prim:(()=>{ const b=document.querySelector('.pr-prim'); if(!b||!VIS(b)) return null; const r=b.getBoundingClientRect(); return r.bottom<=innerHeight&&r.right<=vw&&r.left>=0; })()}; })()")
        t.chk('BEN a 390 px: sem rolagem lateral; lista em cartões (2 ordens); ação primária visível presa ao rodapé', m and not m['lado'] and m['cards'] == 2 and m['prim'], m)
        shot('celular_lista')
        J("(()=>{ const k=[...document.querySelectorAll('.pr-card')].find(x=>N(x.innerText).indexOf('OB-0110')>=0); k&&k.click(); })()"); time.sleep(.6)
        d = J("(()=>{ const a=[...document.querySelectorAll('aside[role=dialog]')].find(VIS); if(!a) return null; const r=a.getBoundingClientRect(); const b=[...a.querySelectorAll('button')].filter(VIS).find(x=>N(x.innerText)==='Concluir execução'); "
              "a.scrollTop=a.scrollHeight; const br=b&&b.getBoundingClientRect(); return {w:Math.round(r.width), fora:r.left<-1||r.right>innerWidth+1, prim:!!b&&br.bottom<=innerHeight+1&&br.top>=0}; })()")
        t.chk('painel da OB-0110 a 390 px: largura toda, sem corte, primária "Concluir execução" alcançável', d and d['w'] >= 380 and not d['fora'] and d['prim'], d)
        shot('celular_painel')
        ir('PROD.dc.html', w=390, h=844); m = J("({lado:document.documentElement.scrollWidth>innerWidth+1, cards:[...document.querySelectorAll('.pr-card')].filter(VIS).length})")
        t.chk('Estoque de produto a 390 px com os lotes do packing: sem rolagem lateral, cartões', m and not m['lado'] and m['cards'] > 0, m)
        t.chk('celular sem erro de JS', not t.errs(), t.errs())
finally:
    t.fim()
sys.exit(0 if all(t.ok) else 1)   # juízo pela linha RESULTADO e pelo código de saída
