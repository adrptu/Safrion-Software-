# -*- coding: utf-8 -*-
"""Beneficiamento BEN-1 · teste de navegador do fluxo principal (docs/beneficiamento/ESPECIFICACAO.md §11.3 E01-E12, §11.7; DECISOES §12).
Modos (um por vez, cada um abre o Chrome headless do cadc_lib.T; o cenário começa limpo):
  fluxo    tarefa do proprietário (§11.7) no desktop, com cliques e campos digitados medidos (linha de base, AC-36): menu Produção ›
           Recebimento e beneficiamento e a faixa de telas até Beneficiamento (BEN-D14); OB-0112 recusa com as duas causas e quem resolve; OB-0110 concluir, conferir (Paula), fechar recusado pela
           custódia; devolução no Estoque (Rui); fechar: L39-120 e L39-121 em inspeção; no Estoque de produto a Qualidade (Marta) registra
           o resultado e libera; o Comercial reserva a sugestão para o PV-031 e a falta aparece; retirar o L39-119 e liberar a OB-0112
           (REQ-041 no Estoque); e a integração com a Colheita: o L39-131 (recebido em processo) abre uma ordem nova pelo atalho.
  erros    recusas e repetição pela tela: perfil sem papel recusado sem gravar; massa pesada acima da entrada; caixas acima da custódia;
           estorno com motivo e relançamento herdado; justificativa acima da alçada decide a gestão; toque duplo no Registrar grava uma vez;
           formulário aberto em versão antiga recebe conflito; navegar (atalhos) nunca grava.
  celular  390 × 844: cartões, sem rolagem lateral, ação primária visível e painel inteiro (BEN e Estoque de produto); fluxo a 390 px:
           Concluir e Conferir com o aviso da mudança de fase visível, Fechar recusado com a causa no painel, toque duplo no Retirar
           grava uma vez e Autorizar e liberar recusado sem gravar.
  revisao  achados da revisão adversarial de 09/10 pela tela: (B1) lote de entrada numa ordem liberada sem "Registrar decisão" no
           Estoque de produto (BEN-REV-01); (B2) carga cujo lote está numa ordem liberada sem "Estornar" em Cargas, com o porquê, e a
           ordem da Lagoa Grande no Packing da Santa Rita (BEN-REV-02, BEN-REV-08); (B3) carga com avaria no Packing: "Liberar lote" da
           Marta no Estoque de produto e o lote passa a abrir ordem (BEN-REV-03); a ordem nova leva o lote inteiro, sem campo de kg (BEN-REV-09).
  roteiro  integração BEN, rodada 1 (a 1440; roteiro390 = o mesmo a 390 com toque real): Igor cria a ordem do L39-132 com as caixas da
           necessidade (1.169 un), vê o impedimento de caixas com quem resolve; o Rui confere a NF 7731 das caixas no Estoque; o Igor
           libera, o Rui entrega no balcão; saídas, conferência (Paula) e Fechar fecham os 12.300 kg sem diferença fictícia; a CG-2107
           sem "Estornar" com o porquê; a Marta sem "Registrar decisão" no L39-132.
  complemento rodada 1 (S3): falta de caixa durante a execução: a recusa diz a saída, "Pedir mais caixas" faz o complemento da
           mesma REQ (toque duplo grava uma vez), o Rui entrega no balcão e o balanço fecha com diferença 0.
  duplo    rodada 1 (S3): toque duplo real (mouse a 1440, toque a 390) em "Autorizar rota e liberar" e "Iniciar processo": a repetição é
           absorvida (o aviso repete o recibo) e não dispara a operação seguinte.
  criada   rodada 1 (S3): depois de "Criar ordem" (toque duplo) a ordem criada fica selecionada e aberta com o próximo passo dela; o 2º
           toque não a libera e o cabeçalho não aponta outra ordem.
  cancelar integração BEN (09/10): ordem em A liberar que não libera (caixas acima do livre; entrada que mudou com o estorno da carga)
           tem saída: "Cancelar a ordem" com motivo (nada reservado) e o lote abre outra ordem.
  faixa390 integração BEN (09/10): a 390 px, Cargas › faixa de telas › Beneficiamento por toque real (a lista aberta fica acima da
           primária presa ao rodapé); a ordem nasce com a necessidade de caixas e a falta aparece com a saída.
Uso: env CHROME_BIN=… flock /tmp/cdpB.lock env CDP_GL=1 timeout 900 python3 ben_fluxo_test.py [fluxo|erros|celular|revisao|roteiro|roteiro390|cancelar|faixa390]
Capturas em _probe/ben_*.png. Dados sintéticos (SAFRION_DADOS=sintetico)."""
import sys, os, time, json
os.environ.setdefault('SAFRION_DADOS', 'sintetico')
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from cadc_lib import T
TODOS = ('fluxo', 'erros', 'celular', 'revisao', 'roteiro', 'roteiro390', 'complemento', 'duplo', 'criada', 'cancelar', 'faixa390')
MODOS = [a for a in sys.argv[1:] if a in TODOS] or list(TODOS)
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
window.ACHA=(t,root)=>{ const r=root?document.querySelector(root):document; if(!r) return null; const els=[...r.querySelectorAll('button,a,[role=tab],[role=button],[role=row],.pr-card,label')].filter(VIS);
  return els.find(x=>N(x.innerText)===t)||els.find(x=>N(x.innerText).startsWith(t))||els.find(x=>(x.getAttribute('aria-label')||'')===t)||null; };
window.PTO=(t,root)=>{ const e=ACHA(t,root); if(!e) return null; e.scrollIntoView({block:'center',inline:'nearest'}); const r=e.getBoundingClientRect(); const x=Math.round(r.left+Math.min(r.width/2,40)), y=Math.round(r.top+r.height/2);
  const top=document.elementFromPoint(x,y); return {x,y,cob:!(top&&(top===e||e.contains(top))),aviso:!!(top&&top.closest&&top.closest('[role=status]')),top:top?top.tagName+' '+N(top.innerText).slice(0,40):''}; };
window.PERFIL=(k)=>{ localStorage.setItem('safrion.perfilDemo',k); return k; };
'ok'"""
def lib(): J(LIB)
CONC = 'Enviar para conferência'   # NAV-CLAREZA 3 (rodada 1): o verbo do efeito, como a O.S.
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
def cen(expr): return J(f"(()=>{{ const c=CEN()||(window.__cen?window.__cen.cenGet():{{}}); return ({expr}); }})()")   # nada gravado ainda: lê o cenário inicial pelo cenGet
def perfil(k): J(f"PERFIL({json.dumps(k)})"); time.sleep(.1)
def rev(): return cen("c.rev||0")
CHIP = "(()=>{ const a=[...document.querySelectorAll('aside[role=dialog]')].find(VIS); const h=a&&a.querySelector('h2'); const b=h&&h.parentElement.querySelector('span[style*=\"border-radius\"]'); return b?N(b.innerText):''; })()"
FAIXA = "[...document.querySelectorAll('nav[aria-label=\"Telas de recebimento e beneficiamento\"] a')].map(a=>[N(a.innerText),a.getAttribute('href'),a.getAttribute('aria-current')])"
BTNS = "[...document.querySelectorAll('aside[role=dialog] button')].filter(VIS).map(b=>N(b.innerText))"
def nav_clk(x, root):   # toque que navega (link): conta o toque e recarrega o apoio na página nova
    cl, tx = J("[window.__cl||0, window.__tx||0]") or [0, 0]; r = J(f"CLK({json.dumps(x)},{json.dumps(root)})"); time.sleep(1.4); lib(); J(f"window.__cl={cl + 1}; window.__tx={tx};"); return r
MOBILE = [False]
def tamanho(w, h):   # a 390 px o Chrome emula toque (Input.dispatchTouchEvent); no desktop, mouse
    MOBILE[0] = w < 500; t.c.size(w, h); t.c.call('Emulation.setTouchEmulationEnabled', {'enabled': MOBILE[0], 'maxTouchPoints': 5 if MOBILE[0] else 1})
def tocar(x, root=None, w=.6, nav=False):
    """toque (390) ou clique (desktop) real no ponto do elemento, como a pessoa: recusa se outro elemento cobre o ponto; conta o toque"""
    p = J(f"PTO({json.dumps(x)},{json.dumps(root)})")
    if not p: return 'NÃO ACHEI: ' + x
    n = 0
    while p and p['cob'] and p.get('aviso') and n < 10:   # o aviso (role=status) por cima do alvo: a pessoa espera ele sair
        time.sleep(1); n += 1; p = J(f"PTO({json.dumps(x)},{json.dumps(root)})")
    if n: print(f'   (esperou {n} s o aviso sair de cima de "{x}")')
    if not p: return 'NÃO ACHEI: ' + x
    if p['cob']: return 'COBERTO: ' + x + ' por ' + p['top']
    cl, tx = J("[window.__cl||0, window.__tx||0]") or [0, 0]
    if MOBILE[0]:
        t.c.call('Input.dispatchTouchEvent', {'type': 'touchStart', 'touchPoints': [{'x': p['x'], 'y': p['y']}]}); t.c.call('Input.dispatchTouchEvent', {'type': 'touchEnd', 'touchPoints': []})
    else:
        for tp in ('mouseMoved', 'mousePressed', 'mouseReleased'): t.c.call('Input.dispatchMouseEvent', {'type': tp, 'x': p['x'], 'y': p['y'], 'button': 'left', 'clickCount': 1})
    time.sleep(1.4 if nav else w); lib(); J(f"window.__cl={cl + 1}; window.__tx={tx};"); return 'ok'
def duplo(x, root='aside', gap=.12):
    """toque/clique duplo real no mesmo ponto (gap entre os dois): o 2º cai no que o 1º fez aparecer, como na mão da pessoa"""
    p = J(f"PTO({json.dumps(x)},{json.dumps(root)})"); n = 0
    while p and p['cob'] and p.get('aviso') and n < 10: time.sleep(1); n += 1; p = J(f"PTO({json.dumps(x)},{json.dumps(root)})")   # espera o aviso sair de cima
    if not p or p['cob']: return 'NÃO ACHEI/COBERTO: ' + x + ('' if not p else ' por ' + p['top'])
    for i in range(2):
        if MOBILE[0]:
            t.c.call('Input.dispatchTouchEvent', {'type': 'touchStart', 'touchPoints': [{'x': p['x'], 'y': p['y']}]}); t.c.call('Input.dispatchTouchEvent', {'type': 'touchEnd', 'touchPoints': []})
        else:
            for tp in ('mousePressed', 'mouseReleased'): t.c.call('Input.dispatchMouseEvent', {'type': tp, 'x': p['x'], 'y': p['y'], 'button': 'left', 'clickCount': i + 1})
        if i == 0: time.sleep(gap)
    time.sleep(1); lib(); return 'ok'
def est_secao(i): J(f"document.querySelectorAll('nav[aria-label=\"Seções do estoque\"] button')[{i - 1}].click()"); time.sleep(.5)

try:
    if 'fluxo' in MODOS:
        print('== fluxo · tarefa do proprietário (§11.7) de ponta a ponta, com cliques e campos medidos')
        # (1) BEN-D14 (09/10): Produção com 3 itens (colheita D-01); o Beneficiamento é tela irmã de Cargas em "Recebimento e beneficiamento"
        ir('CARGA.dc.html', limpa=True); J("window.__cl=0")
        m = J("N(document.querySelector('nav[aria-label=Menu]').innerText)") or ''
        itens = J("[...document.querySelectorAll('nav[aria-label=Menu] a')].map(a=>[N(a.innerText),a.getAttribute('href')]).filter(x=>['COLH.dc.html','CARGA.dc.html','BEN.dc.html','PROD.dc.html'].indexOf(x[1])>=0)") or []
        t.chk('(1) menu: Produção com 3 itens (Previsão e colheita, Recebimento e beneficiamento, Estoque de produto), antes de Manutenção',
              [x[0] for x in itens] == ['Previsão e colheita', 'Recebimento e beneficiamento', 'Estoque de produto'] and m.find('Produção') < m.find('Manutenção'), itens)
        fx = J(FAIXA) or []
        t.chk('(1) Cargas mostra a faixa de telas: Cargas e recebimento (atual) | Beneficiamento, com a pendência escrita (1 a liberar)',
              len(fx) == 2 and fx[0][1] == 'CARGA.dc.html' and fx[0][2] == 'page' and fx[1][1] == 'BEN.dc.html' and fx[1][0].startswith('Beneficiamento') and '1 a liberar' in fx[1][0], fx)
        cg = J("ROWTXT('L39-131')") or ''
        t.chk('(1) Cargas: a carga recebida em processo (L39-131) diz o próximo passo "Abrir ordem de beneficiamento · Igor"', 'Abrir ordem de beneficiamento · Igor' in cg, cg)
        nav_clk('Beneficiamento', 'nav[aria-label="Telas de recebimento e beneficiamento"]')
        t.chk('BEN abre sem erro de JS', not t.errs(), t.errs())
        fx = J(FAIXA) or []; sub = J("[...document.querySelectorAll('nav[aria-label=Menu] a')].filter(a=>getComputedStyle(a).backgroundColor==='rgb(30, 122, 76)').map(a=>N(a.innerText))") or []
        t.chk('(1) no Beneficiamento: faixa com Beneficiamento atual (aria-current) e o item do menu "Recebimento e beneficiamento" em destaque; título Beneficiamento',
              len(fx) == 2 and fx[1][2] == 'page' and fx[0][2] is None and sub == ['Recebimento e beneficiamento'] and J("N(document.querySelector('h1').innerText)") == 'Beneficiamento', [fx, sub])
        clk('Kanban', '[aria-label="Visão das ordens"]', w=.7)
        kb = J("[...document.querySelectorAll('[aria-label=\"Kanban das ordens\"] > *')].filter(VIS).map(x=>N(x.innerText).slice(0,40))")
        t.chk('Kanban com exatamente 5 fases e a contagem da semente (A liberar 1, Em execução 1)', len(kb or []) == 5 and kb[0].lower().startswith('a liberar 1') and kb[2].lower().startswith('em execução 1') and kb[4].lower().startswith('encerradas 0'), kb)
        J("window.__cl=1"); clk('Lista')   # a medida conta o toque da faixa e deixa de fora o Kanban (só conferência do teste)
        t.chk('sem seleção, a ação primária do cabeçalho é a da 1ª ordem com passo: "Autorizar rota e liberar · OB-0112"', J("PRIM()") == ['Autorizar rota e liberar · OB-0112'], J("PRIM()"))
        shot('lista')
        # (2) OB-0112: autorizar e liberar recusa com as duas causas e quem resolve (Igor age)
        perfil('Igor'); r0 = rev(); clk('Autorizar rota e liberar · OB-0112'); p = pan()
        # rodada 1 (BEN-D23): a falta de 341 caixas tem saída real: a NF 7731 a conferir no Estoque (a sobra de 60 da OB-0110 não cobre)
        t.chk('(2) painel da OB-0112 lista as duas causas antes do toque, cada uma com dono e atalho (caixas: conferir a NF 7731; a sobra da OB-0110 citada)', 'L39-119 em inspeção (INSP-94) · Marta (qualidade)' in p and 'Caixa de mamão Formosa 10 kg: 540 un disponíveis para 881 un · Estoque' in p
              and 'Conferir a NF 7731 das caixas no Estoque' in p and 'A OB-0110 tem 60 un em custódia' in p and 'Retirar L39-119 da ordem' in p, p[:900])
        t.chk('(2) OB-0112 A liberar: balanço sem diferença nem recuperação antes de começar ("Entrada a processar"; nada "acima da faixa" nem 100,00 %)',
              'Entrada a processar' in p and 'acima da faixa' not in p and '100,00 %' not in p and 'Em processo 0 kg' not in p, p[p.find('BALANÇO'):][:300] if 'BALANÇO' in p else p[:600])
        clk('Autorizar rota e liberar', 'aside'); p = pan()
        t.chk('(2) "Autorizar rota e liberar" recusa com as 2 causas; nada gravado (fase e revisão iguais)', 'Liberação recusada · 2 causas' in p and cen("c.ordens['OB-0112'].etapa") == 'A liberar' and rev() == r0, [p[-400:], rev(), r0])
        clk('Fechar', 'aside')
        # (3) OB-0110: concluir, conferir (Paula), fechar recusado pela custódia
        row('OB-0110'); p = pan()
        t.chk('(3) OB-0110 Em execução: balanço com as razões de K01 (A 80,00 %, B 15,00 %, descarte 5,00 %, recuperação 95,00 %) e primária "Enviar para conferência"', all(x in p for x in ('80,00 %', '15,00 %', '5,00 %', '95,00 %')) and J("PPRIM()") == [CONC] and 'Fechar processo' not in p, [J("PPRIM()"), p[:600]])
        clk(CONC, 'aside'); et = cen("c.ordens['OB-0110'].etapa"); tc = toast(); ch = J(CHIP)
        t.chk('(3) retorno da mudança de fase: o aviso diz "OB-0110 em conferência" com a diferença e quem confere; o selo do painel passa a "Em conferência"',
              'OB-0110 em conferência' in tc and 'Paula (conferência) confere o balanço' in tc and ch == 'Em conferência', [tc, ch])
        perfil('Paula'); clk('Conferir balanço', 'aside'); cf = cen("(c.ordens['OB-0110'].ben.conf||{}).quem")
        t.chk('(3) Enviar para conferência (Igor) → Em conferência; Conferir balanço gravado em nome da Paula (conferência), diferença 0', et == 'Em conferência' and cf == 'Paula (conferência)', [et, cf, toast()])
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
        t.chk('(medida) tarefa do proprietário, desde Recebimento e beneficiamento, em até 30 toques e sem campo digitado (só toques: a quantidade e as caixas vêm sugeridas)', cl <= 30 and tx == 0, [cl, tx])
        # integração com a Colheita: o L39-131 (recebido em processo, pós-colheita do CAR0) abre uma ordem pelo atalho do Estoque de produto
        ir('PROD.dc.html#L39-131'); time.sleep(.4); p = pan()
        t.chk('Colheita → Beneficiamento: L39-131 em processo no Estoque de produto com o atalho "Abrir ordem de beneficiamento" (só navega)', 'Abrir ordem de beneficiamento' in p and rev() == cen("c.rev||0"), p[:400])
        r0 = rev(); clk('Abrir ordem de beneficiamento', 'aside', w=1.0); lib(); time.sleep(.4); p = pan()
        # rodada 1 (BEN-D23 supera a BEN-D21): as caixas vêm com a necessidade da rota (2.292); a OB-0112 reservou 584 das 600 un e ficam 16
        # livres: o campo avisa antes do toque que a liberação fica impedida até o Estoque receber as caixas, com a nota e quem confere
        t.chk('o atalho abre a ordem nova com o L39-131 marcado, a rota única (PACK-FRU v3) e as caixas da necessidade (2.292, com a falta e a saída à vista); navegar não gravou',
              'Nova ordem' in p and 'PACK-FRU v3' in p and J("(document.querySelector('aside [id^=pf_cx_]')||{}).value||''") == '2292' and '= 2292 un' in p
              and 'Acima das 16 un livres no Estoque: a liberação fica impedida até o Estoque receber as caixas (NF 7731 do PC-096, 1.200 un a conferir' in p and rev() == r0,
              [p[:700], J("(document.querySelector('aside [id^=pf_cx_]')||{}).value")])
        perfil('Igor'); J("(()=>{ const b=[...document.querySelectorAll('aside button')].find(x=>N(x.innerText)==='Criar ordem'); window.__cl++; b.click(); b.click(); })()"); time.sleep(.6)
        st = cen("c.ordens['OB-0113']&&[c.ordens['OB-0113'].etapa,c.ordens['OB-0113'].ben.ent[0].lote,c.ordens['OB-0113'].ins[0].tot,!!c.ordens['OB-0114']]"); tc = toast()
        t.chk('Criar ordem (toque duplo): uma OB-0113 só, A liberar, com o L39-131 e 2.292 caixas (a necessidade); nada reservado antes de liberar; o aviso "OB-0113 criada" fica',
              st == ['A liberar', 'L39-131', 2292, False] and not cen("c.producao.lotes['L39-131'].ordem") and 'OB-0113 criada' in tc, [st, tc])
        ir('CARGA.dc.html'); cg = J("ROWTXT('L39-131')") or ''
        t.chk('Cargas depois de criar: a carga do L39-131 aponta a ordem "na OB-0113 (A liberar)"', 'na OB-0113 (A liberar)' in cg, cg)
        shot('fluxo_fim')
        t.chk('fluxo sem erro de JS', not t.errs(), t.errs())
    if 'erros' in MODOS:
        print('== erros · recusas, estorno e repetição pela tela')
        ir('BEN.dc.html#OB-0110', limpa=True); time.sleep(.3)
        r0 = rev(); perfil('Ana'); clk(CONC, 'aside'); p = pan()
        t.chk('perfil sem o papel (Ana) recusado: "decisão de Igor (responsável de produção)", nada gravado', 'decisão de Igor (responsável de produção)' in p and rev() == r0 and cen("c.ordens['OB-0110'].etapa") == 'Em execução', p[-200:])
        perfil('Igor'); clk('+ Registrar saída', 'aside'); clk('Produto', 'aside'); clk('A', 'aside'); setv('#pf_cx', '10'); setv('#pf_br', '106'); clk('Registrar', 'aside'); p = pan()
        t.chk('massa pesada não se cria: +100 kg de A recusado com as parcelas, nada gravado', 'Saídas pesadas 12.100 kg > entrada 12.000 kg + tolerância 12 kg' in p and rev() == r0, p[-300:])
        setv('#pf_cx', '61'); setv('#pf_br', '600'); clk('Registrar', 'aside'); p = pan()
        t.chk('caixas acima da custódia: "Caixas acima da custódia: 60 un, e a REQ-030 já foi toda entregue. Peça mais caixas na ordem"', 'Caixas acima da custódia: 60 un, e a REQ-030 já foi toda entregue. Peça mais caixas na ordem ("Pedir mais caixas")' in p and rev() == r0, p[-300:])
        clk('Cancelar', 'aside'); row('OB-0110'); clk('Estornar S-02', 'aside'); clk('Confirmar estorno de S-02', 'aside'); p = pan()
        t.chk('estorno sem motivo recusado', 'motivo do estorno' in p and rev() == r0, p[-300:])
        clk('Pesagem refeita', 'aside'); clk('Confirmar estorno de S-02', 'aside'); p = pan(); st = cen("[c.ordens['OB-0110'].ben.sai[1].estorno&&c.ordens['OB-0110'].ben.sai[1].estorno.motivo, c.reqs['REQ-030'].itens[0].custodia, c.movs.slice(-1)[0].tipo]")
        t.chk('estorno com motivo: S-02 riscada, 180 cx voltam à custódia (240), MV estorno-consumo; o relançamento abre herdando fluxo e classe', st == ['Pesagem refeita', 240, 'estorno-consumo'] and 'relançar s-02' in p.lower()
              and J("[...document.querySelectorAll('aside button[aria-pressed=true]')].map(b=>N(b.innerText)).join('|')") == 'Produto|B', [st, J("[...document.querySelectorAll('aside button[aria-pressed=true]')].map(b=>N(b.innerText)).join('|')"), p[p.lower().find('relançar'):][:120]])
        bl = J("(()=>{ const a=[...document.querySelectorAll('aside[role=dialog]')].find(VIS); const s=a&&[...a.querySelectorAll('section')].find(x=>/balanço de massa/i.test(x.getAttribute('aria-label')||'')); return s?N(s.innerText):''; })()") or ''
        t.chk('em execução com 1.800 kg ainda não registrados: o balanço mostra "Em processo" e a diferença "apurada no envio para conferência" (não "acima da faixa")',
              'Em processo 1.800 kg' in bl and 'apurada no envio para conferência' in bl and 'acima da faixa' not in bl, bl)
        setv('#pf_cx', '180'); setv('#pf_br', '1808'); J("(()=>{ const b=[...document.querySelectorAll('aside button')].find(x=>N(x.innerText)==='Registrar'); b.click(); b.click(); })()"); time.sleep(.6)
        n = cen("c.ordens['OB-0110'].ben.sai.filter(s=>!s.estorno).length"); nm = cen("c.movs.filter(m=>m.tipo==='consumo').length")
        tc = toast(); p = pan()
        t.chk('toque duplo no Registrar (mesma chave): 1 registro novo e 1 MV de consumo; o aviso do registro fica (sem "Não gravado")', n == 3 and nm == 1 and 'S-04 registrada' in tc and 'não gravado' not in p.lower(), [n, nm, tc, p[:200]])
        row('OB-0110'); r0 = rev(); J("(()=>{ const b=[...document.querySelectorAll('aside button')].find(x=>N(x.innerText)==='Enviar para conferência'); b.click(); b.click(); })()"); time.sleep(.6); p = pan(); tc = toast()
        t.chk('toque duplo em "Enviar para conferência": grava uma vez e o retorno não vira erro (sem "Não gravado"; o aviso diz em conferência ou "Já feito")',
              cen("c.ordens['OB-0110'].etapa") == 'Em conferência' and rev() == r0 + 1 and 'não gravado' not in p.lower() and ('em conferência' in tc or 'Já feito' in tc), [tc, p[:300]])
        clk('Justificar diferença', 'aside'); clk('Perda não identificada', 'aside'); setv('#pf_tj', 'fruta caída na esteira'); clk('Justificar diferença', 'aside'); p = pan()
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
        d = J("(()=>{ const a=[...document.querySelectorAll('aside[role=dialog]')].find(VIS); if(!a) return null; const r=a.getBoundingClientRect(); const b=[...a.querySelectorAll('button')].filter(VIS).find(x=>N(x.innerText)==='Enviar para conferência'); "
              "a.scrollTop=a.scrollHeight; const br=b&&b.getBoundingClientRect(); return {w:Math.round(r.width), fora:r.left<-1||r.right>innerWidth+1, prim:!!b&&br.bottom<=innerHeight+1&&br.top>=0}; })()")
        t.chk('painel da OB-0110 a 390 px: largura toda, sem corte, primária "Enviar para conferência" alcançável', d and d['w'] >= 380 and not d['fora'] and d['prim'], d)
        shot('celular_painel')
        # fluxo a 390 px: avançar (Concluir, Conferir), recusa (Fechar com caixas em custódia) e repetição (toque duplo no Retirar)
        TV = "(()=>{ const e=[...document.querySelectorAll('[role=status]')].find(x=>N(x.innerText)); if(!e) return null; const r=e.getBoundingClientRect(); return r.top>=0&&r.bottom<=innerHeight&&r.left>=0&&r.right<=innerWidth; })()"
        perfil('Igor'); r0 = rev(); clk(CONC, 'aside'); tc = toast(); ch = J(CHIP); tv = J(TV)
        t.chk('390 px · Enviar para conferência: o aviso "OB-0110 em conferência" aparece inteiro na tela e o selo do painel muda para "Em conferência"', 'OB-0110 em conferência' in tc and ch == 'Em conferência' and tv and rev() == r0 + 1, [tc, ch, tv])
        perfil('Paula'); clk('Conferir balanço', 'aside'); tc = toast()
        t.chk('390 px · Conferir balanço gravado pela Paula; o aviso diz o próximo passo', 'conferido por Paula (conferência)' in tc and 'Próximo passo: Fechar processo' in tc, tc)
        perfil('Igor'); r1 = rev(); clk('Fechar processo', 'aside'); p = pan()
        vis = J("(()=>{ const a=[...document.querySelectorAll('aside[role=dialog]')].find(VIS); const e=a&&[...a.querySelectorAll('[role=alert]')].find(VIS); if(!e) return null; e.scrollIntoView({block:'nearest'}); const r=e.getBoundingClientRect(); return r.left>=0&&r.right<=innerWidth+1; })()")
        t.chk('390 px · Fechar recusado: "Não gravado" com a causa (caixas em custódia) no painel, sem corte; nada gravado', 'não gravado' in p.lower() and 'Sobra em custódia: Caixa de mamão Formosa 10 kg 60 un' in p and vis and rev() == r1 and cen("c.ordens['OB-0110'].etapa") == 'Em conferência', [vis, rev(), r1, p[:900]])
        clk('Fechar', 'aside')
        J("(()=>{ const k=[...document.querySelectorAll('.pr-card')].find(x=>N(x.innerText).indexOf('OB-0112')>=0); k&&k.click(); })()"); time.sleep(.6)
        r2 = rev(); J("(()=>{ const a=[...document.querySelectorAll('aside[role=dialog]')].find(VIS); const b=a&&[...a.querySelectorAll('button')].find(x=>N(x.innerText)==='Retirar L39-119 da ordem'); if(b){ b.click(); b.click(); } })()"); time.sleep(.6)
        st = cen("[c.ordens['OB-0112'].versao, c.ordens['OB-0112'].ben.ent.map(e=>e.lote).join(','), c.ordens['OB-0112'].ben.hist.filter(h=>/Entrada retirada/.test(h.ev)).length]")
        p = pan(); tc = toast()
        t.chk('390 px · toque duplo em "Retirar L39-119 da ordem": uma retirada só (v2, uma linha no histórico, revisão +1) e o retorno não vira conflito nem erro',
              st == ['v2', 'L39-117,L39-118', 1] and rev() == r2 + 1 and 'não gravado' not in p.lower() and 'mudou depois' not in p and 'L39-119 sai da ordem' in tc, [st, rev(), r2, tc, p[:300]])
        r3 = rev(); clk('Autorizar rota e liberar', 'aside'); p = pan()
        t.chk('390 px · Autorizar e liberar recusado por 1 causa (540 un livres para 584 un) com atalho de devolução; nada gravado', 'Liberação recusada · 1 causa' in p and '540 un disponíveis para 584 un' in p and rev() == r3, p[-400:])
        shot('celular_fluxo')
        ir('PROD.dc.html', w=390, h=844); m = J("({lado:document.documentElement.scrollWidth>innerWidth+1, cards:[...document.querySelectorAll('.pr-card')].filter(VIS).length})")
        t.chk('Estoque de produto a 390 px com os lotes do packing: sem rolagem lateral, cartões', m and not m['lado'] and m['cards'] > 0, m)
        t.chk('celular sem erro de JS', not t.errs(), t.errs())
    if 'revisao' in MODOS:
        print('== revisao · achados BEN-REV-01, 02, 03, 08 e 09 pela tela')
        # B1 (BEN-REV-01): L39-119 sai da OB-0112, a Marta libera, o Igor abre e libera a OB-0113 só com ele
        ir('BEN.dc.html#OB-0112', limpa=True); perfil('Igor'); ir('BEN.dc.html#OB-0112'); clk('Retirar L39-119 da ordem', 'aside')
        perfil('Marta'); ir('PROD.dc.html#L39-119'); clk('Conforme', 'aside'); clk('Registrar resultado', 'aside'); clk('Liberar', 'aside'); clk('Registrar decisão', 'aside')
        t.chk('B1 · Marta registra Conforme e libera o L39-119 no Estoque de produto', cen("c.producao.lotes['L39-119'].q0") == 'Liberado', toast())
        perfil('Igor'); ir('BEN.dc.html'); clk('+ Nova ordem'); clk('L39-119', 'aside'); p = pan()
        t.chk('B1 · BEN-REV-09: a ordem nova leva o lote inteiro (sem campo "Quantidade do"; o saldo vem na opção do lote)', 'Quantidade do' not in p and 'A ordem leva o lote inteiro' in p and J("!!document.querySelector('aside [id^=pf_kg_]')") is False, p[:400])
        clk('Criar ordem', 'aside'); ir('BEN.dc.html#OB-0113'); clk('Autorizar rota e liberar', 'aside')
        t.chk('B1 · OB-0113 liberada com o L39-119 (em processo nela)', cen("[c.ordens['OB-0113']&&c.ordens['OB-0113'].etapa, c.producao.lotes['L39-119'].ordem]") == ['Liberadas', 'OB-0113'], toast())
        perfil('Marta'); ir('PROD.dc.html#L39-119'); r0 = rev(); p = pan(); bt = J(BTNS) or []
        t.chk('B1 · BEN-REV-01: no Estoque de produto o L39-119 não oferece "Registrar decisão"; o próximo passo aponta a OB-0113; nada gravado',
              'Registrar decisão' not in bt and 'em processo na OB-0113' in p and rev() == r0 and cen("c.producao.movs.filter(m=>m.lote==='L39-119'&&m.fis!==false).reduce((a,m)=>a+m.kg,0)") == 3130, [bt, p[:400]])
        shot('rev_b1')
        # B2 (BEN-REV-02, BEN-REV-08): OB-0113 com o L39-132 (Lagoa Grande), liberada; a CG-2107 não estorna
        ir('BEN.dc.html', limpa=True); perfil('Igor'); ir('BEN.dc.html'); clk('+ Nova ordem'); clk('L39-132', 'aside')
        cx = J("(document.querySelector('aside [id^=pf_cx_]')||{}).id"); setv('#' + cx, '200'); clk('Criar ordem', 'aside'); ir('BEN.dc.html#OB-0113'); p = pan()
        t.chk('B2 · BEN-REV-08: a OB-0113 roda no Packing (Santa Rita) com a fruta da Lagoa Grande (linha, balança e caixas do mesmo lugar)', 'Packing (Santa Rita) · fruta da Lagoa Grande' in p and cen("c.ordens['OB-0113'].ben.local") == 'l8', p[:300])
        clk('Autorizar rota e liberar', 'aside')
        ir('CARGA.dc.html'); row('CG-2107'); p = pan(); bt = J(BTNS) or []; r0 = rev()
        t.chk('B2 · BEN-REV-02: a CG-2107 (L39-132 em processo na OB-0113) não oferece "Estornar"; o próximo passo diz por quê e o caminho (balanço, alçada), sem repetir o lote',
              cen("c.ordens['OB-0113'].etapa") == 'Liberadas' and 'Estornar' not in bt and 'Sem estorno enquanto a OB-0113 não fecha' in p and 'se justifica na conferência (alçada)' in p and 'Lote L39-132: Em processo' not in p and cen("c.producao.cargas['CG-2107'].st") == 'Recebida', [bt, p[:500]])
        shot('rev_b2')
        # B3 (BEN-REV-03): carga com avaria do T7 no Packing (fixture: O.S. de colheita do T7, que a semente não tem, e a pesagem pela regra)
        # o cenário da fixture sai do mesmo motor das telas (node): a pesagem passa pela regra prReceber, não por JSON escrito à mão
        from ben_unit_test import motor, node
        fx = node(motor() + """ const c = cenClone(CEN0); c.ordens['OS-0932'] = { id: 'OS-0932', tipo: 'Colheita · semana 39', talhao: 'T7', area: 0, etapa: 'Em execução', versao: 'v1', realizado: 6, saldo: 0, resp: 'Sérgio', ins: [], req: null, selos: [],
          ap: [{ d: '25/09', dia: 1, ha: 6, st: 'Conferido', sinc: true, origem: 'web' }], reservado: false, osc: {} };
          prReceber(c, { os: 'OS-0932', ticket: 'TK-T7A', bruto: 9400, tara: 3200, cond: 'Com avaria', dcol: '2026-09-25' }); c.rev = (c.rev || 0) + 1; print(JSON.stringify(c));""", 'ben_rev_b3.js')
        ir('PROD.dc.html', limpa=True); J(f"localStorage.setItem('talhao-os-cenario-v1', {json.dumps(fx.stdout.strip().splitlines()[-1])})")
        perfil('Marta'); ir('PROD.dc.html#L39-133'); p = pan(); pp = J("PPRIM()") or []
        t.chk('B3 · BEN-REV-03: L39-133 (avaria, Packing) em processo com "Liberar lote · Marta (qualidade)" e a primária "Liberar L39-133"', 'Liberar lote · Marta (qualidade)' in p and 'Liberar L39-133' in pp, [pp, p[:300]])
        clk('Liberar L39-133', 'aside'); tc = toast()
        t.chk('B3 · Marta libera: "seguem para o beneficiamento; Igor (responsável de produção) abre a ordem"; o lote continua em processo', 'seguem para o beneficiamento' in tc and cen("c.producao.lotes['L39-133'].q0") == 'Liberado', tc)
        ir('PROD.dc.html#L39-133'); p = pan()
        t.chk('B3 · o próximo passo do L39-133 passa a "Abrir ordem de beneficiamento · Igor"', 'Abrir ordem de beneficiamento' in p, p[:300])
        shot('rev_b3')
        t.chk('revisao sem erro de JS', not t.errs(), t.errs())
    def roteiro(W):
        # integração BEN, rodada 1 (Codex 6089909749): a tarefa do proprietário como está escrita, por toque real (390) ou clique real (1440).
        # Igor cria a ordem do L39-132 com as caixas da necessidade (1.169 un), vê o impedimento de caixas com quem resolve, o Rui confere a
        # NF 7731 das caixas no Estoque (fluxo existente), o Igor libera, o Rui entrega no balcão, e a execução e o balanço fecham os 12.300 kg
        # sem diferença fictícia; a CG-2107 sem Estornar com o porquê; a Marta sem "Registrar decisão" no L39-132
        T_ = str(W); H = 844 if W < 500 else 1000; tamanho(W, H)
        print(f'== roteiro {T_} · tarefa do proprietário com as caixas da necessidade, recebimento no Estoque e balanço fechado')
        ir('CARGA.dc.html', limpa=True, w=W, h=H); perfil('Igor'); ir('CARGA.dc.html', w=W, h=H); J("window.__cl=0; window.__tx=0;"); time.sleep(.6)
        if W < 500: tocar('Cargas e recebimento', 'nav[aria-label="Telas de recebimento e beneficiamento"]')   # a 390 a faixa é uma lista que abre no toque
        r = tocar('Beneficiamento', 'nav[aria-label="Telas de recebimento e beneficiamento"]', nav=True)
        t.chk(T_ + ' R1 · Cargas › faixa › Beneficiamento pelo toque', r == 'ok' and J("location.pathname.split('/').pop()") == 'BEN.dc.html', [r, J("location.pathname")])
        tocar('+ Nova ordem'); tocar('L39-132', 'aside'); p = pan(); cxv = J("(document.querySelector('aside [id^=pf_cx_]')||{}).value")
        t.chk(T_ + ' R1 · Nova ordem com o L39-132: Caixas vem com a necessidade da rota (1169) e o campo avisa a falta no Estoque e como se resolve (NF 7731 a conferir, quem confere)',
              cxv == '1169' and '= 1169 un' in p and 'Acima das 540 un livres no Estoque: a liberação fica impedida até o Estoque receber as caixas (NF 7731 do PC-096, 1.200 un a conferir · Rui (almoxarife) ou Paula (almoxarife)).' in p, [cxv, p[:900]])
        r0 = rev(); r = tocar('Criar ordem', 'aside'); tc = toast()
        t.chk(T_ + ' R1 · Criar ordem: OB-0113 em A liberar com 1.169 un (sugestão confirmada) e o aviso de que a liberação fica impedida até o Estoque receber as caixas',
              r == 'ok' and 'OB-0113 criada (A liberar)' in tc and '1.169 un de caixa (sugestão confirmada)' in tc and 'Atenção: 540 un livres no Estoque para 1.169 un' in tc and rev() == r0 + 1 and cen("c.ordens['OB-0113'].ins[0].tot") == 1169, [r, tc])
        ir('BEN.dc.html#OB-0113', w=W, h=H); p = pan()
        t.chk(T_ + ' R2 · impedimento das caixas à vista antes do toque, com quem resolve e a recuperação (conferir a NF 7731 no Estoque)',
              'Caixa de mamão Formosa 10 kg: 540 un disponíveis para 1.169 un · Estoque' in p and 'resolve: Rui (almoxarife) ou Paula (almoxarife)' in p and 'Conferir a NF 7731 das caixas no Estoque' in p and 'Faltam 629 un' in p, p[:1100])
        r0 = rev(); r = tocar('Autorizar rota e liberar', 'aside'); p = pan()
        t.chk(T_ + ' R2 · Autorizar rota e liberar recusado (540 para 1.169), nada gravado', r == 'ok' and 'Liberação recusada · 1 causa' in p and rev() == r0 and cen("c.ordens['OB-0113'].etapa") == 'A liberar', [r, p[-400:]])
        perfil('Rui'); r = tocar('Conferir a NF 7731 das caixas no Estoque', 'aside', nav=True); time.sleep(.4); lib()
        t.chk(T_ + ' R3 · o atalho leva ao Estoque (Confira recebimentos) sem gravar', r == 'ok' and J("location.pathname.split('/').pop()") == 'EST.dc.html' and rev() == r0 and 'NF 7731' in (J("ROWTXT('NF 7731')") or ''), [r, J("ROWTXT('NF 7731')")])
        r = tocar('NF 7731'); time.sleep(.3)
        un = J("[...document.querySelectorAll('aside[role=dialog] label')].filter(l=>/Quantidade conferida|Apta para uso/.test(l.innerText)).map(l=>N(l.parentElement.innerText))") or []
        setv('#fx_g_rec_conf', '1200'); setv('#fx_g_rec_apto', '1200'); setv('#fx_g_rec_quar', '0')
        fx = J("[ (document.querySelector('#fx_g_rec_local')||{}).value, (document.querySelector('#fx_g_rec_val')||{}).value, (document.querySelector('#fx_g_rec_lote')||{}).value ]")
        r2 = tocar('Salvar', 'aside[role=dialog]'); tc = toast(); st = cen("[ (c.lotes['Caixa de mamão Formosa 10 kg|CX26-02']||{}).fisico, (c.lotes['Caixa de mamão Formosa 10 kg|CX26-02']||{}).local ]")
        t.chk(T_ + ' R3 · Rui confere a NF 7731 (unidade un, lote CX26-02 no Packing, sem validade): 1.200 un entram no disponível',
              r == 'ok' and r2 == 'ok' and all(' un' in x for x in un) and fx == ['Packing', 'Sem validade', 'CX26-02'] and 'Recebimento NF 7731 conferido: 1.200 un de Caixa de mamão Formosa 10 kg no lote CX26-02' in tc and st == [1200, 'Packing'], [r, r2, un, fx, tc, st])
        perfil('Igor'); ir('BEN.dc.html#OB-0113', w=W, h=H); p = pan()
        t.chk(T_ + ' R4 · recebida a nota, o painel da OB-0113 fica sem impedimento', 'Nenhum: a ordem pode ser autorizada e liberada.' in p, p[:800])
        r = tocar('Autorizar rota e liberar', 'aside'); tc = toast()
        st = cen("[c.ordens['OB-0113'].etapa, c.ordens['OB-0113'].req, c.producao.lotes['L39-132'].ordem, c.reqs['REQ-041']&&c.reqs['REQ-041'].itens[0].solicitado, c.reqs['REQ-041']&&c.reqs['REQ-041'].itens[0].lote]")
        t.chk(T_ + ' R4 · Igor libera: Liberadas, REQ-041 com a necessidade inteira (1.169 un do CX26-02) e o L39-132 preso à ordem', r == 'ok' and st == ['Liberadas', 'REQ-041', 'OB-0113', 1169, 'CX26-02'] and 'autorizada (CMD-42) e liberada (CMD-06)' in tc, [r, st, tc])
        ir('CARGA.dc.html', w=W, h=H); tocar('CG-2107'); p = pan(); bt = J(BTNS) or []
        t.chk(T_ + ' R5 · a CG-2107 não oferece "Estornar" e o próximo passo diz por quê', 'Estornar' not in bt and 'Sem estorno enquanto a OB-0113 não fecha' in p, [bt, p[:500]])
        perfil('Marta'); ir('PROD.dc.html#L39-132', w=W, h=H); p = pan(); bt = J(BTNS) or []
        t.chk(T_ + ' R5 · Marta: o L39-132 no Estoque de produto sem "Registrar decisão"; o próximo passo aponta a OB-0113', 'Registrar decisão' not in bt and 'OB-0113' in p, [bt, p[:400]])
        perfil('Rui'); ir('EST.dc.html', w=W, h=H)
        if W < 500: tocar('Confira recebimentos', 'nav[aria-label="Seções do estoque"]')
        tocar('Entregue por O.S.', 'nav[aria-label="Seções do estoque"]'); r = tocar('REQ-041'); q = J("[(document.querySelector('#fx_g_ent_qtd')||{}).value,(document.querySelector('#fx_g_ent_quem')||{}).value]")
        r2 = tocar('Salvar', 'aside[role=dialog]'); tc = toast(); st = cen("[c.reqs['REQ-041'].itens[0].entregue, c.reqs['REQ-041'].itens[0].custodia, c.reqs['REQ-041'].itens[0].quem]")
        t.chk(T_ + ' R6 · Rui entrega no balcão a REQ-041 inteira (1.169 un) ao Igor', r == 'ok' and r2 == 'ok' and q == ['1169', 'Igor'] and st == [1169, 1169, 'Igor'], [r, r2, q, st, tc])
        perfil('Igor'); ir('BEN.dc.html#OB-0113', w=W, h=H); r = tocar('Iniciar processo', 'aside')
        t.chk(T_ + ' R7 · Igor inicia: Em execução', r == 'ok' and cen("c.ordens['OB-0113'].etapa") == 'Em execução', [r, toast()])
        def saida(fl, op, kg=None, cx=None, br=None):
            ir('BEN.dc.html#OB-0113', w=W, h=H); a = tocar('+ Registrar saída', 'aside')
            if a != 'ok': a = tocar('Registrar saída', 'aside')
            tocar(fl, 'aside'); tocar(op, 'aside')
            if cx: setv('#pf_cx', cx); setv('#pf_br', br)
            else: setv('#pf_kg', kg)
            b = tocar('Registrar', 'aside'); return [a, b, toast()]
        s1 = saida('Produto', 'A', cx='1000', br='10600'); s2 = saida('Produto', 'B', cx='169', br='1791,4'); s3 = saida('Descarte', 'Compostagem', kg='610')
        st = cen("[c.ordens['OB-0113'].ben.sai.filter(s=>!s.estorno).map(s=>s.kg), c.reqs['REQ-041'].itens[0].custodia]")
        t.chk(T_ + ' R7 · saídas pesadas: A 1.000 cx (10.000 kg), B 169 cx (1.690 kg) e descarte 610 kg; as 1.169 caixas usadas, custódia 0', st == [[10000, 1690, 610], 0], [st, s1, s2, s3])
        ir('BEN.dc.html#OB-0113', w=W, h=H); r = tocar(CONC, 'aside'); tc = toast()
        t.chk(T_ + ' R8 · ' + CONC + ': Em conferência com diferença 0 kg (0,00 %), sem justificativa', r == 'ok' and cen("c.ordens['OB-0113'].etapa") == 'Em conferência' and 'diferença 0 kg (0,00 %)' in tc, [r, tc])
        perfil('Paula'); r = tocar('Conferir balanço', 'aside'); perfil('Igor'); r2 = tocar('Fechar processo', 'aside'); tc = toast()
        st = cen("(()=>{ const o=c.ordens['OB-0113']; const P=c.producao; const nv=Object.values(P.lotes).filter(L=>L.benef==='OB-0113').map(L=>L.id+':'+P.movs.filter(m=>m.lote===L.id&&m.fis!==false).reduce((a,m)=>a+m.kg,0)).join(',');"
                 " return [o.etapa, (o.ben.just||[]).length, o.ben.sai.filter(s=>s.fluxo==='Perda identificada').length, P.movs.filter(m=>m.lote==='L39-132'&&m.fis!==false).reduce((a,m)=>a+m.kg,0), nv, c.reqs['REQ-041'].itens[0].custodia]; })()")
        t.chk(T_ + ' R8 · Paula confere e Igor fecha: Encerradas; L39-133 (A) 10.000 kg e L39-134 (B) 1.690 kg Em inspeção; descarte 610 kg; L39-132 esgotado; diferença 0 sem justificativa nem perda',
              r == 'ok' and r2 == 'ok' and st == ['Encerradas', 0, 0, 0, 'L39-133:10000,L39-134:1690', 0] and 'diferença 0 kg' in tc and 'descarte 610 kg' in tc, [r, r2, st, tc])
        cl, tx = J("[window.__cl, window.__tx]"); print(f'MEDIDA roteiro {T_}: {cl} toques/cliques e {tx} campos digitados (Igor, Rui, Paula; inclui as saídas pesadas)')
        shot('roteiro_' + T_)
        t.chk(T_ + ' roteiro sem erro de JS', not t.errs(), t.errs())
        tamanho(1440, 1000)
    if 'roteiro' in MODOS: roteiro(1440)
    if 'roteiro390' in MODOS: roteiro(390)
    if 'complemento' in MODOS:
        # rodada 1 (S3): falta de caixa durante a execução tinha só a recusa ("peça no Estoque") e o Estoque recusava (REQ toda entregue).
        # Agora a ordem pede o complemento da mesma REQ (recibo, reserva, entrega no balcão, custódia) e o balanço fecha sem perda fictícia
        print('== complemento · falta de caixa na execução: Pedir mais caixas, entrega no balcão e balanço fechado')
        from ben_unit_test import motor, node
        fx = node(motor() + """ const c = cenClone(CEN0); const IG = 'Igor', RU = 'Rui', CX = BENC.cx.item;
          function M(fn) { const x = cenClone(c); const r = fn(x) || {}; Object.keys(c).forEach(k => delete c[k]); Object.assign(c, x); return r; }
          M(x => benNova(x, { lotes: [{ lote: 'L39-132', kg: 12300 }] }, IG));
          M(x => { const n0 = x.movs.length; cenReceber(x, CX, 'CX26-02', 1200, 'un', 'Packing', '—', 'NF 7731', true, RU); x.movs[n0].estRec = { id: 'r7731', nf: 'NF 7731', ped: 'PC-096', conf: 1200, apto: 1200, quar: 0, lote: 'CX26-02' }; });
          M(x => benAutorizarLiberar(x, 'OB-0113', IG)); M(x => cenEntregar(x, 'REQ-041', CX, 1169, null, RU)); M(x => benIniciar(x, 'OB-0113', IG));
          M(x => benSaida(x, 'OB-0113', { fluxo: 'Produto', classe: 'A', cx: 1100, bruto: 11660 }, IG)); M(x => benSaida(x, 'OB-0113', { fluxo: 'Produto', classe: 'B', cx: 69, bruto: 731.4 }, IG));
          c.rev = (c.rev || 0) + 1; print(JSON.stringify(c));""", 'ben_complemento.js')
        ir('BEN.dc.html', limpa=True); J(f"localStorage.setItem('talhao-os-cenario-v1', {json.dumps(fx.stdout.strip().splitlines()[-1])})"); perfil('Igor'); ir('BEN.dc.html#OB-0113')
        st = cen("[c.ordens['OB-0113'].etapa, c.reqs['REQ-041'].itens[0].custodia, c.reqs['REQ-041'].itens[0].solicitado]")
        t.chk('X0 · fixture pelo motor das telas: OB-0113 em execução, 1.169 caixas usadas (custódia 0) e 610 kg a registrar', st == ['Em execução', 0, 1169], st)
        r0 = rev(); clk('+ Registrar saída', 'aside'); clk('Produto', 'aside'); clk('B', 'aside'); setv('#pf_cx', '20'); setv('#pf_br', '212'); clk('Registrar', 'aside'); p = pan()
        t.chk('X1 · a fruta rendeu mais: 20 cx de B recusadas com a saída escrita (Pedir mais caixas na ordem; quem entrega), nada gravado',
              'Caixas acima da custódia: 0 un, e a REQ-041 já foi toda entregue. Peça mais caixas na ordem ("Pedir mais caixas"); Rui (almoxarife) ou Paula (almoxarife) entrega no balcão.' in p and rev() == r0, p[-400:])
        clk('Cancelar', 'aside'); row('OB-0113'); bt = J(BTNS) or []; clk('Pedir mais caixas', 'aside'); p = pan(); qv = J("(document.querySelector('#pf_qx')||{}).value")
        t.chk('X2 · "Pedir mais caixas" no painel em execução abre o complemento da REQ-041 com a sugestão pelo que falta processar (58 un para 610 kg) e o que acontece depois',
              'Pedir mais caixas' in bt and qv == '58' and 'Complemento da REQ-041: o Estoque reserva no CX26-02 e entrega no balcão' in p, [bt, qv, p[:600]])
        setv('#pf_qx', '20'); r0 = rev(); J("(()=>{ const b=[...document.querySelectorAll('aside button')].find(x=>N(x.innerText)==='Pedir caixas'); if(!b) return; window.__cl++; b.click(); b.click(); })()"); time.sleep(.7); tc = toast()
        st = cen("[c.reqs['REQ-041'].itens[0].solicitado, c.movs.filter(m=>m.tipo==='reserva'&&m.req==='REQ-041').length, c.lotes['Caixa de mamão Formosa 10 kg|CX26-02'].reservado, c.ordens['OB-0113'].ben.hist.filter(h=>/Caixas pedidas/.test(h.ev)).length]")
        t.chk('X2 · Pedir caixas (toque duplo): um complemento só (REQ-041 1.169 → 1.189, uma reserva nova de 20 no CX26-02, uma linha no histórico); o aviso diz quem entrega',
              st == [1189, 2, 20, 1] and rev() == r0 + 1 and '20 un de Caixa de mamão Formosa 10 kg pedidas para a OB-0113: REQ-041 com 1.189 un' in tc, [st, rev(), r0, tc])
        perfil('Rui'); ir('EST.dc.html'); est_secao(2); rw = J("ROWTXT('REQ-041')") or ''
        r = J("(()=>{ const rw=[...document.querySelectorAll('[role=row]')].find(x=>N(x.innerText).indexOf('REQ-041')>=0); if(!rw) return 'sem linha'; (rw.querySelector('[role=cell] span')||rw).click(); return 'ok'; })()"); time.sleep(.5)
        q = J("[(document.querySelector('#fx_g_ent_qtd')||{}).value,(document.querySelector('#fx_g_ent_quem')||{}).value]"); clk('Salvar', 'aside[role=dialog]'); tc = toast()
        st = cen("[c.reqs['REQ-041'].itens[0].entregue, c.reqs['REQ-041'].itens[0].custodia]")
        t.chk('X3 · no Estoque a REQ-041 mostra 20 un a entregar; o Rui entrega ao Igor no balcão (custódia 20)', r == 'ok' and '20 un' in rw and q == ['20', 'Igor'] and st == [1189, 20], [rw, q, st, tc])
        perfil('Igor'); ir('BEN.dc.html#OB-0113'); clk('+ Registrar saída', 'aside'); clk('Produto', 'aside'); clk('B', 'aside'); setv('#pf_cx', '20'); setv('#pf_br', '212'); clk('Registrar', 'aside'); a = toast()
        ir('BEN.dc.html#OB-0113'); clk('+ Registrar saída', 'aside'); clk('Descarte', 'aside'); clk('Compostagem', 'aside'); setv('#pf_kg', '410'); clk('Registrar', 'aside'); b = toast()
        ir('BEN.dc.html#OB-0113'); clk(CONC, 'aside'); tc = toast(); st = cen("[c.ordens['OB-0113'].etapa, c.reqs['REQ-041'].itens[0].custodia, (c.ordens['OB-0113'].ben.just||[]).length]")
        t.chk('X4 · com as 20 caixas o Igor embala o resto e envia para conferência: diferença 0 kg (0,00 %), custódia 0, sem justificativa',
              'S-03 registrada' in a and 'S-04 registrada' in b and st == ['Em conferência', 0, 0] and 'diferença 0 kg (0,00 %)' in tc, [a, b, st, tc])
        shot('complemento')
        t.chk('complemento sem erro de JS', not t.errs(), t.errs())
    if 'duplo' in MODOS:
        # rodada 1 (S3): o 2º clique de um clique duplo em "Autorizar rota e liberar" caía na primária seguinte ("Iniciar processo") e iniciava
        # o processo. A repetição tem de ser absorvida (o aviso repete o recibo) sem disparar a operação seguinte, a 1440 (mouse) e a 390 (toque)
        from ben_unit_test import motor, node
        fx = node(motor() + """ const c = cenClone(CEN0); const IG = 'Igor', RU = 'Rui', CX = BENC.cx.item;
          function M(fn) { const x = cenClone(c); const r = fn(x) || {}; Object.keys(c).forEach(k => delete c[k]); Object.assign(c, x); return r; }
          M(x => benNova(x, { lotes: [{ lote: 'L39-132', kg: 12300 }] }, IG));
          M(x => { const n0 = x.movs.length; cenReceber(x, CX, 'CX26-02', 1200, 'un', 'Packing', '—', 'NF 7731', true, RU); x.movs[n0].estRec = { id: 'r7731', nf: 'NF 7731', ped: 'PC-096', conf: 1200, apto: 1200, quar: 0, lote: 'CX26-02' }; });
          c.rev = (c.rev || 0) + 1; print(JSON.stringify(c));""", 'ben_duplo.js')
        FX = fx.stdout.strip().splitlines()[-1]
        for W in (1440, 390):
            T_ = str(W); H = 844 if W < 500 else 1000; tamanho(W, H); print(f'== duplo {T_} · toque duplo nas primárias que mudam de fase')
            ir('BEN.dc.html', limpa=True, w=W, h=H); J(f"localStorage.setItem('talhao-os-cenario-v1', {json.dumps(FX)})"); perfil('Igor'); ir('BEN.dc.html#OB-0113', w=W, h=H)
            r0 = rev(); r = duplo('Autorizar rota e liberar'); tc = toast(); p = pan()
            st = cen("[c.ordens['OB-0113'].etapa, c.ordens['OB-0113'].ben.hist.filter(h=>/Iniciada/.test(h.ev)).length, c.ordens['OB-0113'].ben.hist.filter(h=>/Liberada/.test(h.ev)).length]")
            t.chk(T_ + ' D1 · toque duplo em "Autorizar rota e liberar": só libera (Liberadas, uma liberação, nada iniciado; revisão +1); o 2º toque repete o recibo',
                  r == 'ok' and st == ['Liberadas', 0, 1] and rev() == r0 + 1 and 'autorizada (CMD-42) e liberada (CMD-06)' in tc and 'não gravado' not in p.lower(), [r, st, rev(), r0, tc])
            r0 = rev(); r = duplo('Iniciar processo'); p = pan(); st = cen("c.ordens['OB-0113'].etapa"); fm = J("!!document.querySelector('aside [role=group][aria-label^=\"Registrar saída\"]')")
            t.chk(T_ + ' D2 · toque duplo em "Iniciar processo": só inicia (Em execução; o formulário de saída não abre sozinho)',
                  r == 'ok' and st == 'Em execução' and rev() == r0 + 1 and fm is False, [r, st, fm, rev(), r0, p[:300]])
            t.chk(T_ + ' duplo sem erro de JS', not t.errs(), t.errs())
        tamanho(1440, 1000)
    if 'criada' in MODOS:
        # rodada 1 (S3): depois de "Criar ordem" a ordem criada sumia da vista (o painel fechava) e a primária do cabeçalho apontava outra
        # ordem com o mesmo verbo. A ordem criada fica selecionada e aberta, com o próximo passo dela; o toque duplo no Criar não a libera
        from ben_unit_test import motor, node
        fx = node(motor() + """ const c = cenClone(CEN0); const RU = 'Rui', CX = BENC.cx.item;
          const n0 = c.movs.length; cenReceber(c, CX, 'CX26-02', 1200, 'un', 'Packing', '—', 'NF 7731', true, RU); c.movs[n0].estRec = { id: 'r7731', nf: 'NF 7731', ped: 'PC-096', conf: 1200, apto: 1200, quar: 0, lote: 'CX26-02' };
          c.rev = (c.rev || 0) + 1; print(JSON.stringify(c));""", 'ben_criada.js')
        FX = fx.stdout.strip().splitlines()[-1]
        for W in (1440, 390):
            T_ = str(W); H = 844 if W < 500 else 1000; tamanho(W, H); print(f'== criada {T_} · a ordem criada fica aberta com o próximo passo dela')
            ir('BEN.dc.html', limpa=True, w=W, h=H); J(f"localStorage.setItem('talhao-os-cenario-v1', {json.dumps(FX)})"); perfil('Igor'); ir('BEN.dc.html', w=W, h=H)
            tocar('+ Nova ordem'); tocar('L39-132', 'aside'); r = duplo('Criar ordem'); p = pan(); tc = toast(); h2 = J("(()=>{ const a=[...document.querySelectorAll('aside[role=dialog]')].find(VIS); const h=a&&a.querySelector('h2'); return h?N(h.innerText):''; })()")
            st = cen("[c.ordens['OB-0113']&&c.ordens['OB-0113'].etapa, !!c.ordens['OB-0114']]"); hp = J("PRIM()") or []
            t.chk(T_ + ' C1 · Criar ordem (toque duplo): uma OB-0113 só, em A liberar (o 2º toque não a libera); o aviso diz a criação',
                  r == 'ok' and st == ['A liberar', False] and 'OB-0113 criada (A liberar)' in tc, [r, st, tc])
            t.chk(T_ + ' C2 · a OB-0113 fica aberta no painel com o próximo passo dela (Autorizar rota e liberar · Igor), e nada no cabeçalho aponta outra ordem',
                  h2.startswith('OB-0113') and 'PRÓXIMO PASSO Autorizar rota e liberar · Igor' in p and not any('OB-0112' in x for x in hp), [h2, p[:300], hp])
            t.chk(T_ + ' criada sem erro de JS', not t.errs(), t.errs())
        tamanho(1440, 1000)
    if 'cancelar' in MODOS:
        # integração BEN (09/10), achado 2: ordem em A liberar que não libera (caixas acima do livre; entrada que mudou com o estorno da carga)
        # prendia o lote sem saída (sem Cancelar, sem editar, sem incluir entrada). Agora "Cancelar a ordem" (rascunho: nada reservado)
        print('== cancelar · ordem em A liberar sem como liberar tem saída: Cancelar a ordem (motivo) e o lote abre outra ordem')
        ir('BEN.dc.html', limpa=True); perfil('Igor'); ir('BEN.dc.html'); clk('+ Nova ordem'); clk('L39-132', 'aside')
        cx = J("(document.querySelector('aside [id^=pf_cx_]')||{}).id"); setv('#' + cx, '1169'); p = pan()
        t.chk('C1 · 1.169 caixas (acima das 540 livres): o aviso aparece no campo antes do toque', 'Acima das 540 un livres no Estoque: a liberação fica impedida até o Estoque receber as caixas (NF 7731' in p, p[:900])
        clk('Criar ordem', 'aside'); tc = toast()
        t.chk('C1 · a ordem nasce com o aviso de que a liberação fica impedida e quem resolve', 'OB-0113 criada (A liberar)' in tc and 'Atenção: 540 un livres no Estoque para 1.169 un' in tc, tc)
        ir('BEN.dc.html#OB-0113'); r0 = rev(); clk('Autorizar rota e liberar', 'aside'); p = pan(); bt = J(BTNS) or []
        t.chk('C1 · liberação recusada (540 de 1.169), nada gravado; o próximo passo e o painel oferecem "Cancelar a ordem"', 'Liberação recusada · 1 causa' in p and rev() == r0 and 'Cancelar a ordem' in bt and 'Cancelar a ordem (nada foi reservado)' in p, [bt, p[:600]])
        clk('Cancelar a ordem', 'aside'); r1 = rev(); clk('Confirmar cancelamento da OB-0113', 'aside'); p = pan()
        t.chk('C1 · sem motivo o cancelamento é recusado e nada é gravado', 'Informe o motivo do cancelamento.' in p and rev() == r1 and cen("c.ordens['OB-0113'].etapa") == 'A liberar', p[-300:])
        setv('#pf_mc', 'caixas insuficientes no Estoque'); clk('Confirmar cancelamento da OB-0113', 'aside'); tc = toast()
        st = cen("[c.ordens['OB-0113'].etapa, (c.ordens['OB-0113'].ben.canc||{}).quem, c.producao.lotes['L39-132'].ordem||'', c.ordens['OB-0113'].req||'']")
        t.chk('C1 · OB-0113 Canceladas por Igor, com o motivo; nada reservado e o L39-132 livre', st == ['Canceladas', 'Igor (responsável de produção)', '', ''] and 'OB-0113 cancelada por Igor' in tc, [st, tc])
        p = pan(); kb = J("ROWTXT('OB-0113')") or ''
        t.chk('C1 · painel e lista: Canceladas, sem ação primária nem "Atrasada", motivo à vista', 'Canceladas' in kb and 'Atrasada' not in kb and J("PPRIM()") == [] and 'caixas insuficientes no Estoque' in p, [kb, J("PPRIM()"), p[:500]])
        clk('Fechar', 'aside'); clk('+ Nova ordem'); clk('L39-132', 'aside'); cxv = J("(document.querySelector('aside [id^=pf_cx_]')||{}).value"); clk('Criar ordem', 'aside')
        st = cen("[c.ordens['OB-0114']&&c.ordens['OB-0114'].etapa, c.ordens['OB-0114']&&c.ordens['OB-0114'].ins[0].tot, c.producao.lotes['L39-132'].ordem||'']")
        t.chk('C1 · o L39-132 abre a OB-0114 com a necessidade (1.169), em A liberar (as caixas chegam pela NF 7731: modo roteiro)', cxv == '1169' and st == ['A liberar', 1169, ''], [cxv, st, toast()])
        # (C2) carga estornada com a ordem em A liberar (a BEN-D19 permite: rascunho): a entrada não confere mais e a ordem tinha só uma entrada
        ir('BEN.dc.html', limpa=True); perfil('Igor'); ir('BEN.dc.html'); clk('+ Nova ordem'); clk('L39-131', 'aside')
        cx = J("(document.querySelector('aside [id^=pf_cx_]')||{}).id"); setv('#' + cx, '500'); clk('Criar ordem', 'aside')
        ir('CARGA.dc.html'); row('CG-2106'); clk('Estornar', 'aside'); setv('#pf_mot', 'ticket trocado na balança'); clk('Confirmar estorno', 'aside')
        t.chk('C2 · a CG-2106 é estornada com a ordem ainda em A liberar (BEN-D19): o L39-131 fica com 12.180 kg', cen("c.producao.cargas['CG-2106'].st") == 'Estornada' and cen("c.producao.movs.filter(m=>m.lote==='L39-131'&&m.fis!==false).reduce((a,m)=>a+m.kg,0)") == 12180, toast())
        ir('BEN.dc.html#OB-0113'); clk('Autorizar rota e liberar', 'aside'); p = pan(); bt = J(BTNS) or []
        t.chk('C2 · liberação recusada ("24.120 kg na ordem, 12.180 kg no lote") e a ordem de uma entrada só oferece "Cancelar a ordem"', 'L39-131: 24.120 kg na ordem, 12.180 kg no lote.' in p and 'Cancelar a ordem' in bt and cen("c.ordens['OB-0113'].etapa") == 'A liberar', [bt, p[:600]])
        clk('Cancelar a ordem', 'aside'); setv('#pf_mc', 'carga CG-2106 estornada'); clk('Confirmar cancelamento da OB-0113', 'aside')
        clk('Fechar', 'aside'); clk('+ Nova ordem'); p = pan()
        t.chk('C2 · cancelada a OB-0113, o L39-131 volta à ordem nova com o saldo de agora (12.180 kg)', cen("c.ordens['OB-0113'].etapa") == 'Canceladas' and 'L39-131 · 12.180 kg' in p, p[:600])
        shot('cancelar')
        t.chk('cancelar sem erro de JS', not t.errs(), t.errs())
    if 'faixa390' in MODOS:
        # integração BEN (09/10), achado 3: a 390 px a lista aberta da faixa de telas (z-index 31) ficava sob a primária presa ao rodapé
        # (z-index 40) e o toque em "Beneficiamento" abria a pesagem; é o único caminho do menu até o Beneficiamento. Toque real (CDP), não .click()
        print('== faixa390 · 390 × 844: Cargas › faixa › Beneficiamento por toque real e o roteiro do proprietário com o valor inicial')
        ir('CARGA.dc.html', limpa=True, w=390, h=844); perfil('Igor'); ir('CARGA.dc.html', w=390, h=844); time.sleep(1.5)
        J("(()=>{ const l=document.querySelector('nav[aria-label=\"Telas de recebimento e beneficiamento\"] label.etp-atual'); l&&l.click(); })()"); time.sleep(.6)
        m = J("(()=>{ const a=[...document.querySelectorAll('nav[aria-label=\"Telas de recebimento e beneficiamento\"] a')].find(x=>x.getAttribute('href')==='BEN.dc.html'); if(!a||!VIS(a)) return null; const r=a.getBoundingClientRect();"
              " const pts=[[.15,.5],[.5,.5],[.85,.5],[.5,.2],[.5,.8]].map(([fx,fy])=>{ const e=document.elementFromPoint(r.left+r.width*fx,r.top+r.height*fy); return e&&(e===a||a.contains(e))?'livre':'coberto por '+N(e&&e.innerText).slice(0,30); });"
              " return {x:Math.round(r.left+r.width/2), y:Math.round(r.top+r.height/2), pts}; })()")
        t.chk('F1 · 390 px: lista da faixa aberta e o item "Beneficiamento" livre nos 5 pontos (nada por cima, nem a primária presa ao rodapé)', m and all(x == 'livre' for x in m['pts']), m)
        if m:
            for tp in ('mousePressed', 'mouseReleased'): t.c.call('Input.dispatchMouseEvent', {'type': tp, 'x': m['x'], 'y': m['y'], 'button': 'left', 'clickCount': 1})
        time.sleep(1.6); lib(); loc = J("location.pathname.split('/').pop()"); p = pan()
        t.chk('F1 · o toque no item leva ao Beneficiamento (não abre a pesagem)', loc == 'BEN.dc.html' and 'Registrar pesagem' not in p, [loc, p[:200]])
        clk('+ Nova ordem'); clk('L39-132', 'aside'); cxv = J("(document.querySelector('aside [id^=pf_cx_]')||{}).value"); clk('Criar ordem', 'aside')
        ir('BEN.dc.html#OB-0113', w=390, h=844); clk('Autorizar rota e liberar', 'aside'); p = pan(); st = cen("[c.ordens['OB-0113']&&c.ordens['OB-0113'].etapa, c.producao.lotes['L39-132'].ordem||'']")
        t.chk('F2 · 390 px: a OB-0113 nasce com a necessidade (1.169 caixas) e a liberação mostra a falta com a saída (o roteiro inteiro a 390: modo roteiro390)', cxv == '1169' and st == ['A liberar', ''] and 'Conferir a NF 7731 das caixas no Estoque' in p, [cxv, st, p[-300:]])
        clk('Fechar', 'aside'); J("(()=>{ const l=document.querySelector('nav[aria-label=\"Telas de recebimento e beneficiamento\"] label.etp-atual'); l&&l.click(); })()"); time.sleep(.6)
        pv = J("(()=>{ const b=document.querySelector('.pr-prim'); return b?getComputedStyle(b).visibility:'sem'; })()")
        J("(()=>{ const l=document.querySelector('nav[aria-label=\"Telas de recebimento e beneficiamento\"] label.etp-atual'); l&&l.click(); })()"); time.sleep(.6)
        pv2 = J("(()=>{ const b=document.querySelector('.pr-prim'); return b&&VIS(b)?getComputedStyle(b).visibility:'sem'; })()")
        t.chk('F3 · no Beneficiamento a 390 px a primária presa ao rodapé some só com a lista aberta e volta ao fechar', pv == 'hidden' and pv2 == 'visible', [pv, pv2])
        shot('faixa390')
        t.chk('faixa390 sem erro de JS', not t.errs(), t.errs())
finally:
    t.fim()
sys.exit(0 if all(t.ok) else 1)   # juízo pela linha RESULTADO e pelo código de saída
