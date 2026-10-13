# -*- coding: utf-8 -*-
"""PCM simplificado · tela única da Manutenção (MA.dc.html) no Chrome: aceite AC-PCM-01..07, 10, 12-14, 17-22 (ESPECIFICACAO §9)
e o fluxo principal (gerar as preventivas → liberar) em 1440 px e 390 px: normal, recusa (papel sem o comando, com o motivo) e
repetição (duplo toque = um efeito). O app (AC-PCM-27) está em ma_app_fluxo_test.py; as regras, em ma_regras_test.py e ma_app_test.py.
Uso (de gen37/, depois de build.py e montar_render.py): python3 ma_unica_test.py"""
import sys, os, re, json, time, glob
from ma_lib import MA
from ui37 import MENU2, INICIO37
from areas.maquinas import REDIRECIONA

HERE = os.path.dirname(os.path.abspath(__file__)); PJ = os.path.join(HERE, 'project')
m = MA(1440, 1000); J = m.J
PRIMS_FORA = "[...document.querySelectorAll('header button,header a,main button,main a')].filter(e=>e.getClientRects().length&&!e.closest('#ma-painel')&&!e.closest('.menu-lat')&&getComputedStyle(e).backgroundColor==='rgb(30, 122, 76)').map(e=>e.innerText.replace(/\\s+/g,' ').trim())"
PRIMS_PAN = "[...document.querySelectorAll('#ma-painel button,#ma-painel a')].filter(e=>e.getClientRects().length&&getComputedStyle(e).backgroundColor==='rgb(30, 122, 76)').map(e=>e.innerText.replace(/\\s+/g,' ').trim())"
CEN = "localStorage.getItem('talhao-os-cenario-v1')"
try:
    # ---------- AC-PCM-01 · menu com 1 item (ícone), link direto para a tela única; o início leva à MA num toque ----------
    m.ir('vis=semordem', perfil='Otávio', limpa=True); m.sem_erro('MA')
    g = [x for x in MENU2 if x[0] == 'Manutenção'][0]
    mn = J("[...document.querySelectorAll('nav[aria-label=Menu] a')].filter(a=>a.getAttribute('aria-label')==='Manutenção').map(a=>[a.getAttribute('href'),a.getAttribute('title'),a.getAttribute('aria-current'),a.innerText.trim()])")
    tog = J("[...document.querySelectorAll('nav[aria-label=Menu] button,nav[aria-label=Menu] .ml-tog')].filter(e=>e.getClientRects().length).length")
    idx = open(os.path.join(PJ, 'Main.dc.html'), encoding='utf-8').read(); ini = open(os.path.join(PJ, INICIO37), encoding='utf-8').read()
    # 13/10 (proprietário): barra lateral só com ícones, sem submenus nem expandir; as 4 visões ficam no seletor da própria MA (v57: 4 subitens no menu).
    # O índice central saiu (Main.dc.html é página técnica sem menu): o caminho de entrada é o ícone Manutenção na página inicial (Mapa).
    VIS_OK = {'', 'vis=semordem', 'vis=ordens', 'vis=ativos', 'vis=planos'}
    lk = J("[...document.querySelectorAll('nav[aria-label=Menu] a')].map(a=>a.getAttribute('href')).filter(h=>/^MA/.test(h||''))")
    vs = J("[...document.querySelectorAll('main .ma-vis button')].map(b=>b.innerText.replace(/\\s*\\d+\\s*$/,'').trim())")
    li = re.findall(r'<a [^>]*href="(MA[^"]*)"', ini)
    m.ok(all(h.split('#')[0] == 'MA.dc.html' and (h.split('#', 1) + [''])[1] in VIS_OK for _, h in g[2]) and lk == ['MA.dc.html'] and mn == [['MA.dc.html', 'Manutenção', 'page', '']]
         and tog == 0 and vs == ['Sem ordem', 'Ordens', 'Ativos', 'Planos'] and li == ['MA.dc.html'] and not re.search(r'(MA-0[1-5]|PM|MA-04det)\.dc\.html', idx + ini),
         'AC-PCM-01 · menu: um só ícone Manutenção, link direto para a tela única MA (destacado, sem subitens nem expandir), as 4 visões no seletor da tela; nenhuma rota antiga; o início (Mapa) leva à MA num toque', [lk, mn, tog, vs, li])
    # ---------- AC-PCM-02 · rotas antigas (com e sem âncora) e fora do canvas ----------
    rotas = [('PM.dc.html', 'vis=planos'), ('MA-01.dc.html', 'vis=ativos'), ('MA-02.dc.html', 'vis=semordem&tipo=achados'), ('MA-03.dc.html', 'vis=semordem'),
             ('MA-04.dc.html', 'vis=ordens'), ('MA-05.dc.html', 'vis=ativos&modo=abastecimentos'), ('MA-04det.dc.html', 'om=OM-0233'),
             ('MA-04.dc.html#OM-0234', 'om=OM-0234'), ('PM.dc.html#PM-01', 'plano=PM-01'), ('MA-01.dc.html#novo:a14', 'vis=planos&novo=plano:a14')]
    ruim = []
    for de, para in rotas:
        # sob carga a tela MA demora a montar: passa por about:blank (nada da navegação anterior pendente) e espera o destino até 10 s, em vez de 1,3 s fixos
        m.c.call('Page.navigate', {'url': 'about:blank'}); time.sleep(.15)
        m.c.call('Page.navigate', {'url': f'http://127.0.0.1:{m.t.p}/{de}'}); t0 = time.time(); h = ''
        while True:
            time.sleep(.25)
            try: h = J("document.readyState==='complete'?location.pathname.split('/').pop()+location.hash:''") or ''
            except Exception: h = ''
            got = set(h.split('#', 1)[1].split('&')) if h.startswith('MA.dc.html#') else set()
            if set(para.split('&')) <= got or time.time() - t0 > 10: break
        if not set(para.split('&')) <= got: ruim.append((de, h))   # a visão de Ordens a ≥ 1024 px ainda acrescenta &om= do painel aberto sozinho
    pag = {k: v.get('page') for k, v in json.load(open(os.path.join(PJ, 'canvas.json')))['boards'].items()}
    m.ok(not ruim and not any(f in pag for f in REDIRECIONA), 'AC-PCM-02 · PM, MA-01..05 e MA-04det (com #OM-, #PM-, #novo:) levam ao endereço novo; fora do canvas', ruim)
    m.ir('om=OM-0234'); a1 = m.pan(); m.ir('plano=PM-01'); a2 = J("(document.querySelector('main h2')||{}).innerText||''"); m.ir('vis=planos&novo=plano:a14'); a3 = J("(document.querySelector('#np-painel')||{}).innerText||''")
    m.ok(a1.startswith('OM-0234') and a2.startswith('PM-01') and 'Silo 01' in a3, 'AC-PCM-02 · o destino abre o registro (painel da OM-0234, plano PM-01, Novo plano do Silo 01)', [a1[:30], a2[:30], a3[:80]])
    # ---------- AC-PCM-03 · nenhum link para tela removida ----------
    viv = []
    for f in glob.glob(os.path.join(PJ, '*.dc.html')):
        b = os.path.basename(f)
        if b in REDIRECIONA: continue
        s = open(f, encoding='utf-8').read()
        if re.search(r'(MA-0[1-5]|PM|MA-04det)\.dc\.html', s): viv.append(b)
    m.ok(not viv, 'AC-PCM-03 · nenhum project/*.dc.html (fora dos redirecionamentos) aponta para MA-01..05, MA-04det ou PM', viv)
    # ---------- AC-PCM-04 · Kanban com 5 colunas nesta ordem ----------
    m.ir('vis=ordens'); m.clk('Kanban')
    cols = J("(()=>{const k=document.querySelector('[aria-label=\"Kanban das ordens\"]'); if(!k) return null; return [...k.children].filter(e=>e.getClientRects().length).map(e=>((e.querySelector('h3,h4,[role=heading]')||e).innerText.split('\\n')[0]).trim());})()")
    kb = J("[...document.querySelectorAll('[aria-label=\"Kanban das ordens\"] [role=button]')].map(b=>b.getAttribute('aria-label')||b.innerText)") or []
    m.ok(cols is not None and [re.sub(r'\s*\d+$', '', x).upper() for x in cols][:5] == ['A LIBERAR', 'LIBERADAS', 'EM EXECUÇÃO', 'EM CONFERÊNCIA', 'ENCERRADAS'] and len(cols) == 5
         and all(re.search(r'OM-\d+', x) for x in kb), 'AC-PCM-04 · Kanban com exatamente 5 colunas (A liberar → Encerradas) e só OMs nos cartões', [cols, kb[:3]])
    # ---------- AC-PCM-05/06/07 · uma primária; nenhum comando em linha; sem faixa ----------
    ruins = {}
    for a in ['vis=semordem', 'vis=ordens', 'vis=ativos', 'vis=ativos&modo=abastecimentos', 'vis=planos', 'ativo=a01', 'plano=PM-01']:
        m.ir(a); pf = J(PRIMS_FORA) or []
        btn_linha = J("[...document.querySelectorAll('[role=row][data-rid] button')].filter(b=>b.getClientRects().length&&!b.classList.contains('g2car')).length")
        faixa = J("!!document.querySelector('.etp-ind,nav[aria-label=\"Telas da manutenção\"],[aria-label=\"Etapas do processo\"]')")
        if len(pf) > 1 or btn_linha or faixa: ruins[a] = (pf, btn_linha, faixa)
    for a in ['om=OM-0234', 'om=OM-0233', 'achado=INSP-104', 'venc=PM-02|a03|s1', 'ativo=a02']:
        m.ir(a)
        if a == 'ativo=a02': m.bloco('Situação'); m.clk('Mudar condição')
        pf = J(PRIMS_FORA) or []; pp = J(PRIMS_PAN) or []
        if pf or len(pp) > 1: ruins[a] = (pf, pp)
    m.ok(not ruins, 'AC-PCM-05/06/07 · ≤ 1 primária por visão, detalhe e painel; com painel aberto nenhuma primária fora dele; nenhum botão de comando nas linhas; sem faixa ou etapas', ruins)
    # ---------- AC-PCM-18 · nenhum selo fixo; AC-PCM-10 · sem "Marcar pendentes" e nada nasce respondido ----------
    ma = open(os.path.join(PJ, 'MA.dc.html'), encoding='utf-8').read()
    fixos = [x for x in ('1 bloqueio ativo', '3 de alta criticidade', '1 desvio a investigar', '1 bloqueado · 1 restrito', 'Marcar pendentes') if x in ma]
    m.ir('vis=semordem'); m.clk('Gerar 3 ordens preventivas')
    nova = m.man("['OM-0235','OM-0236','OM-0237'].every(id=>m.oms[id]&&m.oms[id].chk.every(t=>!t.r&&!(t.tent||[]).length))")
    m.ok(not fixos and nova, 'AC-PCM-18/10 · sem selos fixos nem "Marcar pendentes"; as preventivas geradas nascem sem resposta', fixos)
    # ---------- AC-PCM-17 · cartões ≤ 4, calculados, filtram ----------
    cartoes = {}
    for v in ('semordem', 'ordens', 'ativos'):
        m.ir('vis=' + v); cartoes[v] = J("[...document.querySelectorAll('main .ma-card,main button.ma-card')].filter(e=>e.getClientRects().length).length")
    m.ir('vis=ativos'); apt = J("(()=>{const b=[...document.querySelectorAll('main button')].find(b=>/APTOS AGORA/i.test(b.innerText)); return b?b.innerText.replace(/\\s+/g,' '):'';})()")
    n0 = len(m.linhas(0)); m.clk('APTOS AGORA'); n1 = len(m.linhas(0))
    m.ok(all(0 < x <= 4 for x in cartoes.values()) and 'APTOS AGORA' in apt.upper() and 0 < n1 < n0, 'AC-PCM-17 · até 4 cartões por visão; "Aptos agora" (não disponibilidade) e tocar filtra', [cartoes, apt, n0, n1])
    # ---------- AC-PCM-19 · Ver como: abertura, matriz, pontes do Otávio, estado não muda ----------
    ab = {}
    for k in ('Otávio', 'Zé', 'Ana'):
        m.ir('', perfil=k, limpa=True); ab[k] = J("location.hash")
    m.ir('vis=semordem', perfil='Zé'); zg = J("(()=>{const b=[...document.querySelectorAll('header button')].find(b=>/^Gerar/.test(b.innerText.trim())); return b?b.disabled:'sem';})()")
    m.ir('ativo=a11', perfil='Zé'); m.bloco('Situação'); zc = J("(()=>{const b=[...document.querySelectorAll('main button')].find(b=>/^Mudar condição/.test(b.innerText.trim())); return b?b.disabled:'sem';})()")
    m.ir('ativo=a01', perfil='Zé'); m.bloco('Situação'); zt = J("(()=>{const b=[...document.querySelectorAll('main button')].find(b=>/^Mudar condição/.test(b.innerText.trim())); return b?b.disabled:'sem';})()")
    s0 = J(CEN); m.ir('vis=ordens', perfil='Ana'); m.ir('vis=ordens', perfil='Otávio'); s1 = J(CEN)
    m.ok(ab['Otávio'].startswith('#vis=semordem') and ab['Zé'].startswith('#vis=ordens') and ab['Ana'].startswith('#vis=ativos') and zg is True and zc is True and zt is False and s0 == s1,
         'AC-PCM-19 · Otávio abre em Sem ordem, Zé em Ordens, Ana em Ativos; Gerar só do Otávio; condição: Zé só no ativo de que é responsável técnico (T1 sim, Bomba do Pivô 2 não); trocar o papel não muda o estado', [ab, zg, zc, zt, s0 == s1])
    m.ir('vis=semordem', perfil='Otávio'); m.clk('Gerar 3 ordens preventivas')
    m.ir('om=OM-0230'); m.clk('Resolver sobras (simulado · papel do Almoxarifado)', '#ma-painel'); m.clk('Encerrar ordem', '#ma-painel')
    m.ir('om=OM-0235'); m.clk('Solicitar compra (simulado · Compras recebe no 1c)', '#ma-painel'); m.clk('Registrar recebimento (simulado · papel do Almoxarifado)', '#ma-painel'); m.clk('Liberar serviço', '#ma-painel')
    m.ok(m.man("m.oms['OM-0230'].etapa") == 'Encerradas' and m.man("m.oms['OM-0235'].etapa") == 'Liberadas', 'AC-PCM-19 · pontes do Otávio rotuladas "(simulado · …)": a OM-0230 encerra e a OM-0235 sai de A liberar', [m.man("m.oms['OM-0230'].etapa"), m.man("m.oms['OM-0235'].etapa")])
    # ---------- AC-PCM-12/13 (tela) · teste com tentativas; motivo para quem não executa; MA-04det não é gerado ----------
    m.ir('om=OM-0233', perfil='Ana', limpa=True); p = m.pan()
    det = open(os.path.join(PJ, 'MA-04det.dc.html'), encoding='utf-8').read()
    m.ok('1ª tentativa · Reprovado' in p and 'Anexar foto' not in p and 'Ação de Zé, executante' in p and 'location.replace' in det and len(det) < 3000,
         'AC-PCM-12/13 · a OM-0233 traz a 1ª tentativa Reprovada; quem não executa vê o Teste sem comando e o motivo; MA-04det é só redirecionamento', p[-160:])
    # ---------- AC-PCM-14 · a mesma condição do T1 na MA, no CD-03 e na O.S. (bloqueado e depois apto) ----------
    def tres():
        m.ir('ativo=a01'); t1 = J("document.querySelector('main').innerText.split('\\n').slice(0,40).join(' ')") or ''
        x1 = 'Bloqueado' if 'Bloqueado' in t1 else ('Apto' if re.search(r'\bApto\b', t1) else '?')   # revisão 09/10 (S4): sem o texto da condição não vale "Apto"
        m.ir('', pagina='CD-03.dc.html'); J("(()=>{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.indexOf('Trator T1')>=0); if(r) (r.querySelector('.g2pw')||r).click();})()"); time.sleep(.5)
        ct = J("(()=>{const i=document.querySelector('aside[role=dialog] [id$=\"_cond_t\"]'); return i?i.value:'';})()") or ''
        x2 = 'Bloqueado' if ct.startswith('Bloqueado') else ('Apto' if ct.startswith('Apto') else '?' + ct)
        m.ir('', pagina='OS.dc.html'); o = J("document.body.innerText") or ''
        oc = J("(()=>{ try{ const c=window.__cen.cenGet(); const a=c.man.ativos.a01; return a?a.cond:''; }catch(e){ return ''; } })()") or ''
        x3 = 'Bloqueado' if ('Trator T1 bloqueado' in o and oc == 'Bloqueado') else ('Apto' if ('Trator T1 bloqueado' not in o and oc == 'Apto' and 'OS-0431' in o) else '?')
        return [x1, x2, x3]
    antes = tres()
    m.ir('om=OM-0233', perfil='Zé'); m.clk('Aprovado', '#ma-painel'); m.clk('Anexar foto e registrar Aprovado', '#ma-painel'); m.setv('#om-leitura', '4320'); m.clk('Previsto (6,5 h)', '#ma-painel')
    m.clk('Concluir serviço', '#ma-painel'); m.clk('Declarar Trator T1 apto', '#ma-painel'); depois = tres()
    m.ok(antes == ['Bloqueado'] * 3 and depois == ['Apto'] * 3, 'AC-PCM-14 · Trator T1 com a mesma condição na MA, no CD-03 e na O.S. (bloqueado; depois de Declarar apto, apto nos três)', [antes, depois])
    # ---------- AC-PCM-20 · F5 reabre os endereços; "‹ Ativos" volta com o filtro ----------
    m.ir('vis=ativos', perfil='Otávio', limpa=True); f5 = []
    for a, alvo in [('om=OM-0234', 'OM-0234'), ('achado=SM-0150', 'SM-0150'), ('venc=PM-02|a03|s1', 'PM-02'), ('ativo=a02', 'Trator 02'), ('plano=PM-04', 'PM-04'),
                    ('vis=semordem&tipo=achados', 'INSP-104'), ('vis=ativos&modo=abastecimentos', 'AB-1042')]:
        m.ir(a); m.recarregar(); t = (m.pan() or '') + J("document.querySelector('main').innerText")
        if alvo not in t: f5.append(a)
    m.ir('vis=ativos'); m.clk('Bloqueado 1'); nf = m.linhas(0); m.abre('a01'); m.clk('‹ Ativos'); nv = m.linhas(0)
    m.ok(not f5 and nf == ['a01'] and nv == nf, 'AC-PCM-20 · F5 reabre #om=, #achado=, #venc=, #ativo=, #plano=, #vis=…&tipo=, &modo=; "‹ Ativos" volta com o filtro', [f5, nf, nv])
    # ---------- AC-PCM-21 · 5 grades com busca, filtro e ordenação; rótulos de custo com unidade ----------
    gr = {}
    for a in ('vis=semordem', 'vis=ordens', 'vis=ativos', 'vis=ativos&modo=abastecimentos', 'vis=planos'):
        m.ir(a); gr[a] = J("(()=>{const cx=[...document.querySelectorAll('main .g2caixa')].filter(e=>e.getClientRects().length)[0]; if(!cx) return null; return [!!cx.querySelector('input[type=search],input[placeholder^=Buscar],input[aria-label^=Buscar]'), cx.querySelectorAll('.g2fb').length>0, cx.querySelectorAll('.g2hb').length>0];})()")
    m.ir('om=OM-0234'); m.bloco('Custo e tempos'); cu = m.pan()
    m.ok(all(v == [True, True, True] for v in gr.values()) and 'CUSTO R$/H DA OFICINA' in cu.upper(), 'AC-PCM-21 · as 5 grades com busca, filtro e ordenação; "Custo R$/h da oficina" no painel', gr)
    # ---------- fluxo principal a 1440 px: gerar e liberar (normal, recusa, repetição) ----------
    m.ir('vis=semordem', perfil='Ana', limpa=True); r = J("(()=>{const b=[...document.querySelectorAll('header button')].find(b=>/^Gerar/.test(b.innerText.trim())); return b?[b.disabled,b.getAttribute('title')||'']:null;})()")
    m.ok(r and r[0] is True and 'Otávio' in (r[1] or '') + (m.body()), 'fluxo · recusa: Ana vê "Gerar" desabilitado com o motivo (Ação do Otávio)', r)
    m.ir('vis=semordem', perfil='Otávio'); n0 = m.man("Object.keys(m.oms).length")
    J("(()=>{const b=[...document.querySelectorAll('header button')].find(b=>/^Gerar/.test(b.innerText.trim())); b.click(); b.click();})()"); time.sleep(.6)
    m.ok(m.man("Object.keys(m.oms).length") == n0 + 3, 'fluxo · repetição: duplo toque em "Gerar 3 ordens preventivas" gera 3, não 6', m.man("Object.keys(m.oms).length") - n0)
    m.ir('om=OM-0237'); m.clk('Liberar serviço', '#ma-painel'); m.clk('Liberar serviço', '#ma-painel'); t = m.toast()
    m.ok(m.man("m.oms['OM-0237'].etapa") == 'Liberadas', 'fluxo · normal: a OM-0237 (sem conflito) libera para João; tocar de novo não faz nada', t[:120])
    # ---------- AC-PCM-22 · 390 × 844 ----------
    m.c.size(390, 844); r390 = {}
    for a in ('vis=semordem', 'vis=ordens', 'vis=ativos', 'vis=planos', 'ativo=a01'):
        m.ir(a, perfil='Otávio'); r390[a] = [m.largura(), J("[...document.querySelectorAll('[role=row][data-rid]')].filter(r=>{const b=r.getBoundingClientRect(); return b.height&&b.bottom<=844;}).length"), len(m.linhas(0))]
    m.ir('om=OM-0234'); pw = J("(()=>{const p=document.querySelector('#ma-painel'); const r=p.getBoundingClientRect(); const pr=[...p.querySelectorAll('button')].find(b=>getComputedStyle(b).backgroundColor==='rgb(30, 122, 76)'&&b.getClientRects().length); const q=pr?pr.getBoundingClientRect():null; return [Math.round(r.width), q?Math.round(q.bottom):-1];})()")
    m.ok(all(v[0] <= 0 for v in r390.values()) and all(v[1] >= min(5, v[2]) for k, v in r390.items() if k != 'ativo=a01') and pw[0] >= 380 and 0 < pw[1] <= 844,
         'AC-PCM-22 · 390 px: sem rolagem lateral; ≥ 5 linhas acima da dobra; painel em tela cheia com a primária sem rolar', [r390, pw])
    # recusa a 390 px: Ana (agrônoma e gestora) não tem o papel do PCM; vê os comandos da OM desabilitados, com o motivo, e nada muda
    m.ir('om=OM-0234', perfil='Ana')
    r = J("(()=>{const bs=[...document.querySelectorAll('#ma-painel button')].filter(b=>b.getClientRects().length&&/^(Liberar|Mover janela)/.test(b.innerText.trim())); bs.forEach(b=>b.click()); return bs.map(b=>[b.innerText.trim(),b.disabled]);})()"); time.sleep(.4)
    m.ok(bool(r) and all(x[1] for x in r) and 'Ação do Otávio' in m.pan() and m.man("m.oms['OM-0234'].etapa") == 'A liberar' and m.largura() <= 0,
         'fluxo a 390 px · recusa: Ana vê "Mover janela"/"Liberar" desabilitados com o motivo (Ação do Otávio); tocar não muda a OM-0234', r)
    # normal e repetição a 390 px: Otávio libera com o conflito aceito; duplo toque reserva as peças uma vez só
    m.ir('om=OM-0234', perfil='Otávio')
    RES = "Object.values(m.itens).reduce((s,i)=>s+(+i.reservado||0),0)"
    res0 = m.man(RES); q = m.man("(m.oms['OM-0234'].pecas||[]).filter(p=>p.item).reduce((s,p)=>s+(+p.qtd||0),0)")
    m.clk('Liberar mesmo assim', '#ma-painel'); m.clk('Liberar mesmo assim', '#ma-painel'); res1 = m.man(RES)
    m.ok(m.man("m.oms['OM-0234'].etapa") == 'Liberadas' and m.largura() <= 0 and abs((res1 or 0) - (res0 or 0) - (q or 0)) < 1e-9,
         'fluxo a 390 px · com conflito, "Liberar mesmo assim" (ponte até o 1b) libera uma vez; duplo toque reserva as peças uma vez só', [res0, res1, q])
    m.c.size(1280, 900); m.ir('vis=ordens', perfil='Otávio', limpa=True); time.sleep(.4)
    role = J("(document.querySelector('#ma-painel')||{}).getAttribute&&document.querySelector('#ma-painel').getAttribute('role')")
    J("document.body.focus()")
    for _ in range(6): m.tecla('Tab', 'Tab', 9)
    fora = J("!(document.activeElement&&document.activeElement.closest('#ma-painel'))")
    m.ok(role == 'complementary' and fora, 'AC-PCM-22 · a ≥ 1024 px o painel abre sozinho, não modal (o Tab não fica preso)', [role, fora])
    m.sem_erro('fim')
finally:
    rc = m.fim()
sys.exit(rc)
