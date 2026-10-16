# -*- coding: utf-8 -*-
"""Modo de ver Tabela | Cartões (proprietário, 15/10/2026: "Coloque modos de visão em todas telas... nessas 2 por exemplo tem que ter opção
tabela e 'Cartões'"), no Chrome headless, como a pessoa usa (clique e toque de verdade no seletor, no cartão e na linha):
  M1  o seletor está no fim da barra da tabela, depois de Colunas, com "Tabela" e "Cartões" (aria-label, aria-pressed) e a Tabela ativa
  M2  trocar para Cartões e voltar: os mesmos itens nos dois modos (contagem e ids, na ordem) sem filtro, com busca, com filtro rápido
      e com Agrupar por (título por grupo; descer pelo nome do grupo); o total da tabela vira a linha de resumo acima dos cartões
  M3  abrir um item pelo cartão faz o mesmo que a linha da Tabela (mesmo painel, etapa ou endereço); Enter no cartão também
  M4  a escolha fica: recarregar abre em Cartões (preferência por perfil × tela × listagem); a listagem principal leva ?view=cartoes no
      endereço; outro perfil abre na Tabela; voltar à Tabela tira o view= do endereço
  M5  390 px (toque): cartões numa coluna, sem rolagem lateral; botões do seletor com 44 px
  M6  Planos agronômicos › Atividades do plano: abre em Cartões (a lista própria); a Tabela tem DAP, Atividade, Insumos, Custo/ha e ⋯,
      as mesmas atividades com o filtro por operação; clicar na linha abre os insumos como o cartão; a escolha fica e vai ao endereço
  M7  DS VIS-05 ("toda lista tem Tabela e Cartões"): O.S. (seletor de visões da VISOES-1), MA › Ordens e BEN (Lista | Kanban próprios) ganham
      Cartões no próprio seletor, sem um 2º seletor na barra da grade; os mesmos itens da Tabela (e com Agrupar por, na O.S.)
  M8  sem erro de JavaScript
Telas: Planejar safra › etapa 1 (g_saf), Atividades do plano (PA), Cadastros › Parceiros (CD-05 g_forn), Manutenção › Ativos (MA g_at),
Estoque › Recebimento (EST g_rec), Configurações › Usuários (CF-01 g_pes, lista sem colunas essenciais: visoes.MODO_LISTAS) e Cadastros ›
Produtos (CD-06 g_itm, árvore). Dados sintéticos; render em RENDER_DIR ou _render.
Uso (de gen37/): CHROME_BIN=… SAFRION_DADOS=sintetico python3 -B cartoes_test.py   (sai 1 se falhar). Emulação; não é aparelho físico."""
import sys, os, time, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, servir, agrupar_por, troca_visao

R = os.environ.get('RENDER_DIR') or os.path.join(HERE, '_render')
ok_n = 0; falhas = []
def chk(nome, cond, det=''):
    global ok_n
    if cond: ok_n += 1; print('OK  ' + nome, flush=True)
    else: falhas.append(nome); print('FALHA ' + nome + ' · ' + str(det)[:600], flush=True)

p, srv = servir(R); c = Chrome(); J = c.js
BASE = f'http://127.0.0.1:{p}/'
ERROS = []
def guarda_erros():
    try: ERROS.extend(J("window.__errs||[]") or [])
    except Exception: pass
def abrir(url, perfil=None, limpa=False, espera=1.3):
    guarda_erros()
    if limpa or perfil:
        c.goto(BASE + 'Main.dc.html', .3)
        J("(()=>{%s %s})()" % ("localStorage.clear(); sessionStorage.clear();" if limpa else "",
                               ("localStorage.setItem('safrion.perfilDemo',%s);" % json.dumps(perfil)) if perfil else ""))
    c.goto(BASE + url, espera)
def espera(cond, limite=5.0):
    fim = time.time() + limite
    while time.time() < fim:
        try:
            if J(cond): return True
        except Exception: pass
        time.sleep(.12)
    return False
def clique_xy(x, y):
    c.mouse(x, y); c.mouse(x, y, 'mousePressed', 'left'); c.mouse(x, y, 'mouseReleased', 'left'); time.sleep(.45)
def clique_el(expr, toque=False):
    """clique (ou toque) de verdade no centro do elemento (expressão JS), depois de trazê-lo à vista"""
    r = J(f"(()=>{{const e={expr}; if(!e) return null; e.scrollIntoView({{block:'center'}}); const r=e.getBoundingClientRect(); return [r.left+r.width/2, r.top+r.height/2];}})()")
    if not r: return False
    if toque: c.toque(*r)
    else: clique_xy(*r)
    return True
def modo_btn(gid, k): return f"document.querySelector('[data-g2md=\"{gid}\"] [data-modo=\"{k}\"]')"
def modo(gid, k, toque=False):
    clique_el(modo_btn(gid, k), toque); time.sleep(.35)
def pressed(gid): return J(f"[...document.querySelectorAll('[data-g2md=\"{gid}\"] [data-modo]')].map(b=>[b.getAttribute('data-modo'),b.getAttribute('aria-label'),b.getAttribute('aria-pressed')])")
def ids_tab(gid): return J(f"[...document.querySelectorAll('[data-g2g=\"{gid}\"] [role=row][data-rid]')].filter(r=>r.getClientRects().length).map(r=>r.getAttribute('data-rid'))") or []
def ids_car(gid): return J(f"[...document.querySelectorAll('[data-g2cd=\"{gid}\"] [data-rid]')].filter(r=>r.getClientRects().length).map(r=>r.getAttribute('data-rid'))") or []
def na_tela(gid): return J(f"({{tab:!!document.querySelector('[data-g2g=\"{gid}\"]'), car:!!document.querySelector('[data-g2cd=\"{gid}\"]')}})")
def conta(gid): return J(f"(()=>{{const s=document.querySelector('[data-g2cnt=\"{gid}\"]'); return s?s.innerText.trim():''}})()")
BARRA = "(document.querySelector('[data-g2md=\"%s\"]')||{}).parentElement"
def busca(gid, termo):
    J("(()=>{const b=%s; const i=b&&b.querySelector('input[type=search]'); if(!i) return; const set=Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set; set.call(i,%s); i.dispatchEvent(new Event('input',{bubbles:true}));})()" % (BARRA % gid, json.dumps(termo)))
    time.sleep(.45)
def chips(gid): return J("(()=>{const b=%s; return b?[...b.querySelectorAll('button[aria-pressed]')].filter(x=>!x.closest('[data-g2md]')&&x.getClientRects().length).map(x=>x.innerText.replace(/\\s+/g,' ').trim()):[]})()" % (BARRA % gid)) or []
def chip(gid, i):
    J("(()=>{const b=%s; const xs=[...b.querySelectorAll('button[aria-pressed]')].filter(x=>!x.closest('[data-g2md]')&&x.getClientRects().length); if(xs[%d]) xs[%d].click();})()" % (BARRA % gid, i, i)); time.sleep(.45)
def ag_rotulos(gid):
    J(f"(()=>{{const b=document.querySelector('[data-g2agb=\"{gid}\"]'); if(b&&b.getAttribute('aria-expanded')!=='true') b.click();}})()"); time.sleep(.35)
    r = J(f"(()=>{{const m=document.querySelector('[data-g2agm=\"{gid}\"]'); return m?[...m.querySelectorAll('[role=menuitemradio]')].map(x=>(x.innerText||'').trim().split('\\n')[0].trim()):[]}})()") or []
    c.tecla('Escape', 'Escape', 27); time.sleep(.3); return r
def efeito():
    """o que abrir um item fez: endereço, etapa atual, painel ou diálogo à vista (título) e formulário lateral"""
    return J(r"""(()=>{const n=s=>(s||'').replace(/\s+/g,' ').trim(); const vis=e=>!!e&&e.getClientRects().length>0;
      const d=[...document.querySelectorAll('aside[role=dialog],[role=dialog],aside')].filter(vis).map(x=>n((x.querySelector('h2,h3,b')||x).innerText).slice(0,60));
      const et=document.querySelector('.etp-ind [aria-current=step]');
      return {url:location.pathname.split('/').pop()+location.hash, etapa:et?n(et.innerText).slice(0,40):'', paineis:d};})()""")

CASOS = [
    # (nome, página, grade, toque 390 confere uma coluna)
    ('SAF etapa 1', 'SAF.dc.html', 'g_saf'),
    ('CD-05 Parceiros', 'CD-05.dc.html', 'g_forn'),
    ('MA Ativos', 'MA.dc.html#vis=ativos', 'g_at'),
    ('EST Recebimento', 'EST.dc.html', 'g_rec'),
    ('CF-01 Pessoas', 'CF-01.dc.html', 'g_pes'),
]
try:
    c.aparelho(1440, 900, 1, False)
    for nome, pg, gid in CASOS:
        abrir(pg, perfil='Ana', limpa=True)
        espera(f"!!document.querySelector('[data-g2md=\"{gid}\"]')")
        # M1 · lugar e estado do seletor
        lugar = J("(()=>{const m=document.querySelector('[data-g2md=\"%s\"]'); if(!m) return null; const cv=document.querySelector('[data-g2cvb=\"%s\"]'); const ag=document.querySelector('[data-g2agb=\"%s\"]');"
                  " const pos=(a,b)=>!!a&&!!b&&!!(a.compareDocumentPosition(b)&Node.DOCUMENT_POSITION_FOLLOWING); return {aposCol:cv?pos(cv,m):null, aposAg:ag?pos(ag,m):null, rot:m.getAttribute('aria-label'), mesmaBarra:!!cv&&cv.parentElement===m.parentElement};})()" % (gid, gid, gid))
        chk(f'M1 {nome}: seletor Tabela | Cartões depois de Colunas e do Agrupar por, na barra da tabela; Tabela ativa ao abrir',
            lugar and lugar['aposCol'] is not False and lugar['aposAg'] is not False and lugar['rot'].startswith('Visão')
            and pressed(gid) == [['tabela', 'Tabela', 'true'], ['cartoes', 'Cartões', 'false']] and na_tela(gid) == {'tab': True, 'car': False}, [lugar, pressed(gid)])
        t0, n0 = ids_tab(gid), conta(gid)
        modo(gid, 'cartoes'); c0, nc = ids_car(gid), conta(gid)
        url = J("location.search")
        chk(f'M2a {nome}: Cartões mostra os mesmos itens da Tabela, na mesma ordem ({len(t0)}), e o "X de Y" não muda; o endereço leva ?view=cartoes',
            t0 and c0 == t0 and nc == n0 and na_tela(gid) == {'tab': False, 'car': True} and pressed(gid)[1][2] == 'true' and 'view=cartoes' in url, [t0, c0, n0, nc, url])
        lst = J(f"(()=>{{const l=[...document.querySelectorAll('[data-g2cd=\"{gid}\"] [role=list]')]; return l.map(x=>[x.getAttribute('aria-label'), x.querySelectorAll(':scope > [role=listitem]').length]);}})()")
        chk(f'M2b {nome}: cartões em lista com rótulo (role=list/listitem)', lst and all(x[0] and x[1] > 0 for x in lst), lst)
        # busca (pelo título do 1º item) nos dois modos
        # o termo é a palavra mais longa do título do 1º cartão, sem o texto de links e botões da célula (o "Editar" da safra)
        termo = J(f"(()=>{{const t=document.querySelector('[data-g2cd=\"{gid}\"] .g2cd-tit'); if(!t) return ''; let x=t.innerText; t.querySelectorAll('a,button,[role=img]').forEach(e=>{{ x=x.replace(e.innerText,' '); }}); return x.replace(/[^A-Za-zÀ-ÿ0-9 ]/g,' ').trim().split(/\\s+/).sort((a,b)=>b.length-a.length)[0]||''}})()")
        busca(gid, termo); c1 = ids_car(gid); modo(gid, 'tabela'); t1 = ids_tab(gid)
        chk(f'M2c {nome}: com a busca "{termo}" os dois modos mostram os mesmos itens', termo and t1 and c1 == t1 and len(t1) <= len(t0), [termo, t1, c1])
        busca(gid, '')
        # filtro rápido: o 2º chip
        cs = chips(gid)
        if len(cs) >= 2:
            chip(gid, 1); t2 = ids_tab(gid); modo(gid, 'cartoes'); c2 = ids_car(gid)
            chk(f'M2d {nome}: com o filtro rápido "{cs[1]}" os dois modos mostram os mesmos itens', t2 and c2 == t2 and len(t2) < len(t0), [cs[1], t2, c2])
            chip(gid, 0); modo(gid, 'tabela')
        # Agrupar por: a 1ª pergunta do menu; cartões com um título por grupo; descer pelo nome do grupo
        ags = [x for x in ag_rotulos(gid) if x != 'Sem agrupar']
        if ags:
            modo(gid, 'cartoes'); r = agrupar_por(J, ags[0], gid); c3 = ids_car(gid); modo(gid, 'tabela'); t3 = ids_tab(gid)
            ng = len([x for x in t3 if x.startswith('grp@')])
            chk(f'M2e {nome}: Agrupar por "{ags[0]}": os mesmos grupos e itens nos dois modos ({ng} grupos)', r == 'ok' and t3 and c3 == t3 and ng >= 1, [r, t3, c3])
            modo(gid, 'cartoes')
            ngc = J(f"document.querySelectorAll('[data-g2cd=\"{gid}\"] .g2cd-gcab').length")
            desce = J(f"(()=>{{const b=document.querySelector('[data-g2cd=\"{gid}\"] .g2cd-gcab button[aria-label^=\"Descer\"]'); if(!b) return ''; const t=b.innerText.trim(); b.click(); return t;}})()"); time.sleep(.5)
            trilha = J(f"(()=>{{const n=document.querySelector('[data-g2agtr=\"{gid}\"]'); return n?n.innerText.replace(/\\s+/g,' ').trim():''}})()")
            c4 = ids_car(gid); modo(gid, 'tabela'); t4 = ids_tab(gid)
            chk(f'M2f {nome}: no Cartões, um título por grupo ({ngc}); o nome do grupo desce (trilha "{trilha}") e os dois modos seguem iguais',
                ngc == ng and desce and desce.rstrip(' ›') in trilha and t4 and c4 == t4, [ngc, ng, desce, trilha, t4, c4])
            agrupar_por(J, 'Sem agrupar', gid)
        # total da tabela → linha de resumo acima dos cartões
        tot_t = J(f"(()=>{{const r=document.querySelector('[data-g2g=\"{gid}\"] .g2tot'); return r?r.innerText.replace(/\\s+/g,' ').trim():''}})()")
        modo(gid, 'cartoes')
        tot_c = J(f"(()=>{{const r=document.querySelector('[data-g2cd=\"{gid}\"] .g2cd-tot'); return r?r.innerText.replace(/\\s+/g,' ').trim():''}})()")
        if any(ch.isdigit() for ch in tot_t):   # a linha Total da Tabela só com números de colunas à vista (MA › Ativos: o custo fica em Colunas)
            num = [x for x in tot_t.split(' ') if any(ch.isdigit() for ch in x)]
            chk(f'M2g {nome}: o total da tabela vira a linha de resumo acima dos cartões', tot_c.startswith('Total') and all(x in tot_c for x in num), [tot_t, tot_c])
        # M3 · abrir pelo cartão = abrir pela linha
        abrir(pg)   # recarrega em Cartões (preferência)
        espera(f"!!document.querySelector('[data-g2cd=\"{gid}\"] [role=listitem]')")
        alvo = J(f"(()=>{{const k=[...document.querySelectorAll('[data-g2cd=\"{gid}\"] .g2cd.g2ed')].find(x=>x.getClientRects().length); return k?k.getAttribute('data-rid'):''}})()")
        e_c = None
        if alvo:
            pos = J(f"(()=>{{const k=document.querySelector('[data-g2cd=\"{gid}\"] [data-rid=\"{alvo}\"]'); k.scrollIntoView({{block:'center'}}); const r=k.getBoundingClientRect(); return [r.left+6, r.bottom-5];}})()")
            clique_xy(*pos); time.sleep(.4); e_c = efeito()
        abrir(pg); modo(gid, 'tabela'); e_t = None
        if alvo:
            pos = J(f"(()=>{{const k=document.querySelector('[data-g2g=\"{gid}\"] [role=row][data-rid=\"{alvo}\"]'); k.scrollIntoView({{block:'center'}}); const r=k.getBoundingClientRect(); return [r.left+3, r.top+r.height/2];}})()")
            clique_xy(*pos); time.sleep(.4); e_t = efeito()
        chk(f'M3a {nome}: clicar no cartão {alvo} faz o mesmo que a linha da Tabela', alvo and e_c and e_c == e_t and (e_c['paineis'] or e_c['url'] != pg or e_c['etapa']), [alvo, e_c, e_t])
        # M4 · preferência e endereço
        abrir(pg); modo(gid, 'cartoes'); abrir(pg)
        chk(f'M4a {nome}: recarregar abre em Cartões (preferência da Ana); a listagem principal leva ?view=cartoes',
            na_tela(gid) == {'tab': False, 'car': True} and pressed(gid)[1][2] == 'true', [na_tela(gid), pressed(gid)])
        abrir(pg, perfil='Caio')
        chk(f'M4b {nome}: outro perfil (Caio) abre na Tabela', na_tela(gid) == {'tab': True, 'car': False}, na_tela(gid))
        abrir(pg, perfil='Ana'); modo(gid, 'tabela')
        chk(f'M4c {nome}: voltar à Tabela grava a escolha e tira o view= do endereço', 'view=' not in J("location.search") and na_tela(gid) == {'tab': True, 'car': False}, [J("location.href"), na_tela(gid)])

    # M4d · chegada pelo endereço: ?view=cartoes abre a listagem principal (a 1ª à vista) em Cartões, sem preferência gravada; a outra
    # listagem da mesma tela (AG-02: Laudos e Água) fica na Tabela, e trocar o modo dela não mexe no endereço
    abrir('AG-02.dc.html?view=cartoes', perfil='Ana', limpa=True); espera("!!document.querySelector('[data-g2cd=\"g_lau\"]')")
    a1, a2 = na_tela('g_lau'), na_tela('g_agua')
    modo('g_agua', 'cartoes'); u1 = J("location.search"); a3 = na_tela('g_agua')
    chk('M4d endereço ?view=cartoes: a listagem principal (AG-02 Laudos) abre em Cartões; a segunda (Água) fica na Tabela e trocar o modo dela não mexe no endereço',
        a1 == {'tab': False, 'car': True} and a2 == {'tab': True, 'car': False} and a3 == {'tab': False, 'car': True} and u1 == '?view=cartoes', [a1, a2, a3, u1])

    # M3b · teclado: Enter no cartão abre o mesmo que o clique (CD-05: o formulário do parceiro)
    abrir('CD-05.dc.html', perfil='Ana', limpa=True); modo('g_forn', 'cartoes')
    J("(()=>{const k=document.querySelector('[data-g2cd=\"g_forn\"] [data-rid=\"F02\"]'); k.focus();})()"); time.sleep(.2)
    foco = J("document.activeElement&&document.activeElement.getAttribute('data-rid')")
    c.tecla('Enter', 'Enter', 13, text='\r'); time.sleep(.6); ek = efeito()
    chk('M3b CD-05: o cartão recebe o foco (Tab) e Enter abre o parceiro', foco == 'F02' and any('Casa do Adubo' in x for x in ek['paineis']), [foco, ek])

    # árvore (CD-06): o cartão do grupo diz quantos itens e abre os filhos dentro; os mesmos itens da Tabela
    abrir('CD-06.dc.html', perfil='Ana', limpa=True); t5 = ids_tab('g_itm'); modo('g_itm', 'cartoes'); c5 = ids_car('g_itm')
    kn = J("(()=>{const b=document.querySelector('[data-g2cd=\"g_itm\"] .g2cd-nk'); return b?[b.innerText.trim(), b.getAttribute('aria-expanded')]:null})()")
    J("document.querySelector('[data-g2cd=\"g_itm\"] .g2cd-nk').click()"); time.sleep(.4)
    c6 = ids_car('g_itm'); modo('g_itm', 'tabela'); t6 = ids_tab('g_itm')
    chk('M2h CD-06 (árvore): os mesmos itens nos dois modos; o cartão do grupo recolhe e abre os filhos dentro dele, como a seta da Tabela',
        t5 and c5 == t5 and kn and kn[1] == 'true' and len(c6) < len(c5) and c6 == t6, [t5[:6], c5[:6], kn, len(c5), len(c6), t6 == c6])

    # M6 · Atividades do plano (PA)
    abrir('PA.dc.html#plano=SOJA-AT', perfil='Ana', limpa=True)
    espera("!!document.querySelector('.pa-atividade')")
    pa_card = J("[...document.querySelectorAll('.pa-atividade[data-atv]')].map(x=>x.getAttribute('data-atv'))") or []
    chk('M6a PA: Atividades do plano abre em Cartões (a lista própria), com o seletor depois do "Expandir tudo"',
        pa_card and pressed('pa_atv') == [['tabela', 'Tabela', 'false'], ['cartoes', 'Cartões', 'true']]
        and J("(()=>{const x=[...document.querySelectorAll('button.g2xtog')].find(b=>b.getClientRects().length); const m=document.querySelector('[data-g2md=pa_atv]'); return !!x&&!!(x.compareDocumentPosition(m)&Node.DOCUMENT_POSITION_FOLLOWING);})()"), [pa_card, pressed('pa_atv')])
    modo('pa_atv', 'tabela')
    cab = J("[...document.querySelectorAll('.pa-tb [role=columnheader]')].map(h=>h.innerText.trim())")
    pa_tab = J("[...document.querySelectorAll('.pa-tb-l[data-atv]')].map(x=>x.getAttribute('data-atv'))") or []
    lin = J("(()=>{const l=document.querySelector('.pa-tb-l'); return l?{ico:!!l.querySelector('.pa-op-ico svg'), mais:!!l.querySelector('.g2mais'), cells:[...l.querySelectorAll('[role=cell]')].map(x=>x.innerText.replace(/\\s+/g,' ').trim())}:null})()")
    chk('M6b PA Tabela: colunas DAP, Atividade (com o ícone), Insumos, Custo/ha e ⋯; as mesmas atividades, na mesma ordem; ?view=tabela no endereço',
        [x.upper() for x in cab[:4]] == ['DAP', 'ATIVIDADE', 'INSUMOS', 'CUSTO/HA'] and pa_tab == pa_card and lin and lin['ico'] and lin['mais'] and 'view=tabela' in J("location.search"), [cab, pa_tab, lin])
    # filtro por operação: o 2º chip
    J("(()=>{const xs=[...document.querySelectorAll('.pa-opf')]; if(xs[1]) xs[1].click();})()"); time.sleep(.45)
    f_tab = J("[...document.querySelectorAll('.pa-tb-l[data-atv]')].map(x=>x.getAttribute('data-atv'))") or []
    modo('pa_atv', 'cartoes'); f_card = J("[...document.querySelectorAll('.pa-atividade[data-atv]')].map(x=>x.getAttribute('data-atv'))") or []
    chk('M6c PA: com o filtro por operação os dois modos mostram as mesmas atividades', f_tab and f_tab == f_card and len(f_tab) < len(pa_card), [f_tab, f_card])
    J("(()=>{const xs=[...document.querySelectorAll('.pa-opf')]; if(xs[0]) xs[0].click();})()"); time.sleep(.4)
    # clicar na linha (cartão) abre os insumos; o mesmo na Tabela
    alvo = pa_card[0]
    pos = J(f"(()=>{{const l=document.querySelector('.pa-atividade[data-atv=\"{alvo}\"] .pa-atividade-linha'); const r=l.getBoundingClientRect(); return [r.right-170, r.top+r.height/2];}})()")
    clique_xy(*pos); ins_c = J(f"(()=>{{const a=document.querySelector('.pa-atividade[data-atv=\"{alvo}\"]'); return a?[...a.querySelectorAll('.pa-insumos [role=group],.pa-insumos button')].map(b=>(b.getAttribute('aria-label')||b.innerText).trim()).filter(Boolean).slice(-1)[0]||'':''}})()")
    clique_xy(*pos)   # fecha de novo
    modo('pa_atv', 'tabela')
    pos = J(f"(()=>{{const l=document.querySelector('.pa-tb-l[data-atv=\"{alvo}\"] .pa-tb-ins')||document.querySelector('.pa-tb-l[data-atv=\"{alvo}\"]'); const r=l.getBoundingClientRect(); return [r.left+r.width/2, r.top+r.height/2];}})()")
    clique_xy(*pos)
    ins_t = J(f"(()=>{{const d=document.querySelector('.pa-tb-l[data-atv=\"{alvo}\"]+.pa-tb-det'); return d?[...d.querySelectorAll('.pa-insumos [role=group],.pa-insumos button')].map(b=>(b.getAttribute('aria-label')||b.innerText).trim()).filter(Boolean).slice(-1)[0]||'':''}})()")
    exp = J(f"(()=>{{const b=document.querySelector('.pa-tb-l[data-atv=\"{alvo}\"] .pa-titulo'); return b?b.getAttribute('aria-expanded'):null}})()")
    chk('M6d PA: clicar na linha da Tabela abre os insumos logo abaixo, como o cartão (mesmo "Incluir insumo")', ins_c and ins_c == ins_t and exp == 'true', [ins_c, ins_t, exp])
    abrir('PA.dc.html#plano=SOJA-AT')
    chk('M6e PA: recarregar mantém a Tabela (preferência)', J("!!document.querySelector('.pa-tb')") and not J("!!document.querySelector('.pa-atividade')"), pressed('pa_atv'))
    modo('pa_atv', 'cartoes')
    chk('M6f PA: voltar a Cartões tira o view= e mostra a lista própria', 'view=' not in J("location.search") and J("!!document.querySelector('.pa-atividade')"), J("location.href"))

    # M7 · O.S., MA › Ordens e BEN: Cartões no seletor da própria tela (DS VIS-05)
    abrir('OS.dc.html', perfil='Ana', limpa=True); espera("!!document.querySelector('[data-g2g=\"g_os\"]')")
    t7 = ids_tab('g_os'); r7 = troca_visao(J, 'cartoes', '[aria-label="Visão das ordens"]'); c7 = ids_car('g_os'); u7 = J("location.search")
    agrupar_por(J, 'Talhão', 'g_os'); c8 = ids_car('g_os'); troca_visao(J, 'lista', '[aria-label="Visão das ordens"]'); t8 = ids_tab('g_os'); agrupar_por(J, 'Sem agrupar', 'g_os')
    chk('M7a O.S.: "Ver em cartões" no seletor de visões (?view=cartoes) mostra as mesmas ordens da Tabela, também agrupadas por Talhão; sem 2º seletor na barra da grade',
        r7 == 'ok' and t7 and c7 == t7 and 'view=cartoes' in u7 and t8 and c8 == t8 and any(x.startswith('grp@') for x in t8) and not J("!!document.querySelector('[data-g2md=\"g_os\"]')"), [r7, t7, c7, u7, t8, c8])
    for nome, pg2, g2, alvo in [('MA › Ordens', 'MA.dc.html#vis=ordens', 'g_om', "[...document.querySelectorAll('[aria-label=\"Visão das ordens\"] button')].find(b=>b.getAttribute('aria-label')==='Cartões')"),
                                ('BEN', 'BEN.dc.html', 'g_ob', "[...document.querySelectorAll('[aria-label=\"Visão das ordens\"] button')].find(b=>b.innerText.trim()==='Cartões')")]:
        abrir(pg2, perfil='Ana', limpa=True); espera(f"!!document.querySelector('[data-g2g=\"{g2}\"]')")
        ta = ids_tab(g2); clique_el(alvo); time.sleep(.4); ca = ids_car(g2); pr = J(f"(()=>{{const b={alvo}; return b?b.getAttribute('aria-pressed'):null}})()")
        chk(f'M7b {nome}: "Cartões" no seletor da tela (Lista | Cartões | Kanban) mostra as mesmas ordens da Lista; sem 2º seletor na barra da grade',
            ta and ca == ta and pr == 'true' and not J(f"!!document.querySelector('[data-g2md=\"{g2}\"]')"), [ta, ca, pr, J("location.hash")])

    # M5 · 390 px (toque): uma coluna, sem rolagem lateral, alvos de 44 px
    c.aparelho(390, 844, 2, True)
    for pg, gid in [('CD-05.dc.html', 'g_forn'), ('SAF.dc.html', 'g_saf'), ('MA.dc.html', 'g_at')]:
        abrir(pg, perfil='Ana', limpa=True); espera(f"!!document.querySelector('[data-g2md=\"{gid}\"]')")
        alt = J(f"[...document.querySelectorAll('[data-g2md=\"{gid}\"] button')].map(b=>Math.round(b.getBoundingClientRect().height))")
        modo(gid, 'cartoes', toque=True)
        m = J(f"""(()=>{{const ks=[...document.querySelectorAll('[data-g2cd="{gid}"] .g2cd')].filter(k=>k.getClientRects().length); const xs=[...new Set(ks.map(k=>Math.round(k.getBoundingClientRect().left)))];
              const cx=document.querySelector('[data-g2cd="{gid}"]'); return {{n:ks.length, colunas:xs.length, lado:document.documentElement.scrollWidth>innerWidth+1, dentro:cx?cx.scrollWidth<=cx.clientWidth+1:false,
              cabe:ks.every(k=>k.getBoundingClientRect().right<=innerWidth)}};}})()""")
        chk(f'M5 {pg} 390 px: cartões numa coluna ({m["n"] if m else 0}), sem rolagem lateral; seletor com 44 px no toque',
            m and m['n'] > 0 and m['colunas'] == 1 and not m['lado'] and m['dentro'] and m['cabe'] and alt and min(alt) >= 44, [m, alt])
    abrir('PA.dc.html?view=tabela#plano=SOJA-AT', perfil='Ana', limpa=True)
    m = J("({lado:document.documentElement.scrollWidth>innerWidth+1, tb:!!document.querySelector('.pa-tb'), dentro:(()=>{const t=document.querySelector('.pa-tb'); return !!t&&t.scrollWidth<=t.clientWidth+1;})()})")
    chk('M5 PA 390 px: a Tabela das atividades cabe na largura (sem rolagem lateral)', m['tb'] and not m['lado'] and m['dentro'], m)

    guarda_erros()
    errs = [e for e in ERROS if e]
    chk('M8 sem erro de JavaScript', not errs, errs[:5])
finally:
    c.close(); srv.terminate()
print(f'RESULTADO: {ok_n}/{ok_n + len(falhas)}' + (' · FALHAS: ' + '; '.join(falhas) if falhas else ''))
sys.exit(1 if falhas else 0)
