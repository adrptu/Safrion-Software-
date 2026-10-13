# -*- coding: utf-8 -*-
"""CADUX · teste de navegador do fluxo principal dos Cadastros (pedido do proprietário, 09/10/2026: "clicar na fazenda e abrir os talhões
cadastrados nela na tela"). Roda a 1440 × 900 (mouse e teclado) e a 390 × 844 (toque):
  normal     · fazenda → talhões no mapa e na grade → talhão no painel → voltar com o filtro, a posição e o foco;
  teclado    · ↑/↓/Enter no mestre (com anúncio), Esc fecha o painel e devolve o foco à linha;
  erro       · criar sem nome recusa com o campo destacado e mantém o digitado; alteração não salva segura o voltar do navegador (R06);
  repetição  · criar dois talhões seguidos na Boa Vista ("+ Criar outro talhão na Boa Vista"), sem repetir área (R11);
  indisponível · #talhao=ZZ9 abre a lista com aviso e saída, sem selecionar outro registro (SEL-02);
  e em cada tela: uma primária por contexto (BOT-01), linha com um só alvo e fora do Tab (BOT-07), window.__errs vazio.
Uso (navegador um por vez): env CHROME_BIN=/tmp/cloudchrome/chrome flock /tmp/cdpH.lock env CDP_GL=1 timeout 900 python3 cadux_cd01_test.py"""
import os, sys, time, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); os.chdir(HERE)
from comp_lib import Chrome, servir
from cadux_nav import Nav, mestre_item, alvo_linha, botao, botao_ini, PAINEL, VERDES, LINHAS
OK, FAIL = [], []
OUTDIR = os.environ.get('CADUX_FOTOS', '')
def chk(n, cond, info=''):
    (OK if cond else FAIL).append(n); print(('OK    ' if cond else 'FALHA ') + n + ('' if cond else ' · ' + str(info)[:600]), flush=True)
def foto(c, nome):
    if OUTDIR: os.makedirs(OUTDIR, exist_ok=True); c.shot(os.path.join(OUTDIR, nome + '.png'))

AVISO = "document.querySelector('.cmd-aviso')"
port, srv = servir(os.path.join(HERE, '_render')); c = Chrome(); J = c.js
def limpa():
    c.goto(f'http://127.0.0.1:{port}/Main.dc.html', .3); J('localStorage.clear();sessionStorage.clear()')
def contexto(L, rot, mestre=False):
    """regras de toda tela: verde por contexto, alvo único por linha, sem erro de script. mestre=True: abaixo de 1024 px, no nível do mestre
    a grade não está na tela (só os cartões); confere os cartões no lugar das linhas (achado 11 da revisão: antes o detalhe aparecia embaixo)"""
    vd = J(VERDES); ln = J(LINHAS)
    if mestre:
        ct = J("[...document.querySelectorAll('.cmd-lista .cmd-it')].filter(e=>e.getClientRects().length).length")
        chk(f'{L} {rot}: no mestre, só os cartões das fazendas (a grade do detalhe fica fora da tela)', ct >= 3 and not ln and J("document.querySelector('.cmd').getAttribute('data-nivel')") == 'm', [ct, ln[:2]])
        ln = None
    chk(f'{L} {rot}: no máximo um verde no cabeçalho, no Próximo passo e no painel (BOT-01); até 2 secundárias no painel (BOT-06)',
        len(vd['cab']) <= 1 and len(vd['prox']) <= 1 and len(vd['painel']) <= 1 and len(vd['secPainel']) <= 2, vd)
    if ln is not None:
        ruins = [r for r in ln if r['tab'] not in ('-1', None) or len([x for x in r['cmds'] if 'g2car' not in x]) != 1]
        chk(f'{L} {rot}: cada linha com um só alvo nomeado e fora do Tab (BOT-07)', ln and not ruins, ruins[:3] or 'sem linhas')
    chk(f'{L} {rot}: sem erro de script', not J('window.__errs||[]'), J('window.__errs'))
try:
    for L, (w, h, toque) in (('1440', (1440, 900, False)), ('390', (390, 844, True))):
        c.aparelho(w, h, toque=toque); limpa(); n = Nav(c, port, toque)
        # ---------------- normal: fazenda → talhões → painel → voltar ----------------
        n.abre('CD-01')
        larga = w >= 1024
        if larga:
            chk(f'{L} abre em "Todas as fazendas" com o mestre e o detalhe lado a lado', J("document.querySelector('#dx-t').innerText") == 'Todas as fazendas' and J("document.querySelector('.cmd').getAttribute('data-nivel')") == 'l', J("document.querySelector('#dx-t').innerText"))
        else:
            chk(f'{L} abre no mestre (lista das fazendas, um nível por vez)', J("document.querySelector('.cmd').getAttribute('data-nivel')") == 'm' and J(f"!!({mestre_item('Santa Rita')})"), J("document.querySelector('.cmd').getAttribute('data-nivel')"))
        cab = J("[...document.querySelectorAll('header button')].filter(b=>getComputedStyle(b).backgroundColor==='rgb(30, 122, 76)').map(b=>b.innerText.trim())")
        chk(f'{L} "+ Criar talhão" é a primária do cabeçalho (BOT-02/03)', cab == ['+ Criar talhão'], cab)
        n.clica(mestre_item('Santa Rita'), 'Santa Rita')
        chk(f'{L} Santa Rita: endereço #faz=SR e o detalhe da fazenda', J('location.hash') == '#faz=SR' and J("document.querySelector('#dx-t').innerText") == 'Santa Rita', [J('location.hash'), J("document.querySelector('#dx-t').innerText")])
        rows = J("[...document.querySelectorAll('.cmd-d [role=row][data-rid]')].filter(r=>r.getClientRects().length).map(r=>r.getAttribute('data-rid'))")
        chk(f'{L} os 8 talhões da Santa Rita na grade, "8 de 8"', len(rows) == 8 and J("document.querySelector('.cmd-d .cmd-conta').innerText").startswith('8 de 8'), [rows, J("(document.querySelector('.cmd-d .cmd-conta')||{}).innerText")])
        if larga:
            mp = J("[...document.querySelectorAll('.cd-mapa svg [data-tid]')].filter(e=>e.getClientRects().length).map(e=>e.getAttribute('data-tid'))")
            chk(f'{L} os talhões da Santa Rita também no mapa da fazenda, acima da grade', len(mp) >= 7 and set(mp) <= set(rows), mp)
            # regra do cadf_fix_lista 9 e 10 (sem rolagem de página): só a grade e o mapa rolam dentro do bloco; a legenda do mapa fica inteira
            pg = J("(()=>{ const se=document.scrollingElement; const lg=document.querySelector('.cd-mapa-leg'); const b=lg&&lg.getBoundingClientRect(); const cx=lg&&lg.closest('.cmd-d').getBoundingClientRect();"
                   " return {doc:se.scrollHeight<=innerHeight+1, leg:!!b&&b.bottom<=cx.bottom+1&&b.height>0}; })()")
            chk(f'{L} a página não rola; a grade e o mapa rolam dentro do bloco e a legenda do mapa fica inteira', pg['doc'] and pg['leg'], pg)
        foto(c, f'cd01_{L}_santa_rita')
        contexto(L, 'Santa Rita')
        # filtro rápido "Todos/A resolver" não muda; a busca da tela filtra os dois níveis
        # a busca fica no mestre: no computador ao lado do detalhe; abaixo de 1024 px o detalhe ocupa a tela (a busca a 390 é testada abaixo)
        q0 = 'T' if larga else ''
        if larga: n.digita('#mx-q', q0, 'busca')
        vis_q = J("[...document.querySelectorAll('.cmd-d [role=row][data-rid]')].filter(r=>r.getClientRects().length).length")
        n.clica(alvo_linha('T2'), 'T2')
        tit = J(f"({PAINEL}||{{}}).getAttribute&&{PAINEL}.getAttribute('aria-label')")
        chk(f'{L} T2 abre no painel em consulta, com o foco no título (DS-41)', tit == 'Talhão · T2' and J("document.activeElement.tagName==='H2'"), [tit, J("document.activeElement.outerHTML.slice(0,80)")])
        chk(f'{L} endereço do painel #faz=SR&talhao=T2 (pushState: o voltar fecha)', J('location.hash').endswith('talhao=T2') and J('history.state&&history.state.cadux') == 'i', [J('location.hash'), J('history.state')])
        pw = J(f"{PAINEL}.getBoundingClientRect().width")
        chk(f'{L} painel com 820 px no computador e tela cheia no celular', (pw == 820) if larga else (pw >= 389), pw)
        contexto(L, 'painel do T2')
        foto(c, f'cd01_{L}_painel_T2')
        if larga:
            n.clica(f"{PAINEL}.querySelector('.g2nav button:last-of-type')", '›')
            t2 = J(f"{PAINEL}.getAttribute('aria-label')")
            chk(f'{L} "›" vai ao próximo talhão da lista filtrada, no mesmo painel', t2 and t2 != 'Talhão · T2' and t2.startswith('Talhão · '), t2)
            n.clica(f"{PAINEL}.querySelector('.g2nav button:first-of-type')", '‹')
        n.volta()
        chk(f'{L} voltar do navegador fecha o painel e volta a #faz=SR', not J(f"!!{PAINEL}") and J('location.hash') == '#faz=SR', [J(f"!!{PAINEL}"), J('location.hash')])
        chk(f'{L} voltar preserva a busca e o recorte da grade', J("document.querySelector('#mx-q').value") == q0 and J("[...document.querySelectorAll('.cmd-d [role=row][data-rid]')].filter(r=>r.getClientRects().length).length") == vis_q, [J("document.querySelector('#mx-q').value"), vis_q])
        time.sleep(.3)
        foco = J("(document.activeElement.closest('[data-rid]')||{}).getAttribute&&document.activeElement.closest('[data-rid]').getAttribute('data-rid')")
        chk(f'{L} o foco volta ao alvo do T2 (DS-60)', foco == 'T2', J("document.activeElement.outerHTML.slice(0,120)"))
        # ---------------- teclado (1440): mestre com ↑/↓/Enter e anúncio; Esc fecha o painel ----------------
        if larga:
            n.digita('#mx-q', '', 'limpa busca') if False else J("(()=>{ const e=document.querySelector('#mx-q'); const s=Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set; s.call(e,''); e.dispatchEvent(new Event('input',{bubbles:true})); })()")
            time.sleep(.4)
            J(f"({mestre_item('Santa Rita')}).focus()"); n.tecla('ArrowDown')
            fo = J("document.activeElement.innerText.replace(/\\s+/g,' ').trim()")
            n.tecla('Enter')
            chk(f'{L} ↓ e Enter no mestre escolhem a Boa Vista, com o anúncio para o leitor de tela', fo.startswith('Boa Vista') and J('location.hash') == '#faz=BV' and 'Boa Vista' in J("document.querySelector('.cmd-m [role=status]').innerText"), [fo, J('location.hash'), J("document.querySelector('.cmd-m [role=status]').innerText")])
            n.clica(mestre_item('Santa Rita'), 'Santa Rita'); n.clica(alvo_linha('T3'), 'T3'); n.tecla('Escape')
            chk(f'{L} Esc fecha o painel e devolve o foco à linha do T3', not J(f"!!{PAINEL}") and J("(document.activeElement.closest('[data-rid]')||{getAttribute:()=>''}).getAttribute('data-rid')") == 'T3', J("document.activeElement.outerHTML.slice(0,100)"))
            # mapa: tocar no talhão abre o mesmo painel
            n.clica("document.querySelector('.cd-mapa svg [data-tid=T4]')", 'T4 no mapa')
            chk(f'{L} talhão tocado no mapa abre o painel dele', J(f"({PAINEL}||{{getAttribute:()=>''}}).getAttribute('aria-label')") == 'Talhão · T4', J(f"!!{PAINEL}"))
            n.tecla('Escape')
        else:
            # a 390: "‹ Fazendas" volta ao mestre, com a Santa Rita marcada
            n.volta() if J('history.state&&history.state.cadux') == 'g' else n.clica(botao_ini('‹ Fazendas'), '‹ Fazendas')
            chk(f'{L} voltar sobe do detalhe ao mestre (um nível por vez)', J("document.querySelector('.cmd').getAttribute('data-nivel')") == 'm', J("document.querySelector('.cmd').getAttribute('data-nivel')"))
            # busca no mestre a 390: o resultado abre o painel direto (tarefa 9)
            J("(()=>{ const e=document.querySelector('#mx-q'); const s=Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set; s.call(e,''); e.dispatchEvent(new Event('input',{bubbles:true})); })()"); time.sleep(.3)
            n.digita('#mx-q', 'PV07', 'busca PV07')
            n.clica("[...document.querySelectorAll('.cmd-res button')].find(b=>b.innerText.startsWith('PV07'))", 'PV07 · Lagoa Grande')
            chk(f'{L} busca "PV07" no mestre abre o painel do PV07 direto', J(f"({PAINEL}||{{getAttribute:()=>''}}).getAttribute('aria-label')") == 'Talhão · PV07', J(f"!!{PAINEL}"))
            n.volta()
        # ---------------- erro e repetição: criar na Boa Vista ----------------
        limpa(); n.abre('CD-01', '#faz=BV')
        n.clica(botao('+ Criar talhão', "document.querySelector('header')"), '+ Criar talhão')
        chk(f'{L} "+ Criar talhão" com a Boa Vista escolhida: Fazenda = Boa Vista (herdada, trocável)', J("document.querySelector('#fx_g_tal_faz').value") == 'Boa Vista' and not J("document.querySelector('#fx_g_tal_faz').disabled"), J("document.querySelector('#fx_g_tal_faz').value"))
        n.digita('#fx_g_tal_decl', '80', 'área')
        n.clica(botao('Criar talhão', PAINEL) or botao('Salvar', PAINEL), 'Salvar') if J(f"!!({botao('Criar talhão', PAINEL)})") else n.clica(botao('Salvar', PAINEL), 'Salvar')
        chk(f'{L} sem nome: recusa com o campo destacado e mantém a área digitada', J(f"!!{PAINEL}") and J("[...document.querySelectorAll('aside [role=alert]')].some(e=>/Informe|identifica/i.test(e.innerText))") and J("document.querySelector('#fx_g_tal_decl').value") == '80',
            J("[...document.querySelectorAll('aside [role=alert]')].map(e=>e.innerText)"))
        n.digita('#fx_g_tal_t', 'B2', 'nome')
        n.clica(botao('Criar talhão', PAINEL) if J(f"!!({botao('Criar talhão', PAINEL)})") else botao('Salvar', PAINEL), 'Salvar')
        chk(f'{L} B2 criado: o painel mostra o B2 em consulta, com o endereço do novo', J(f"({PAINEL}||{{getAttribute:()=>''}}).getAttribute('aria-label')") == 'Talhão · B2' and 'faz=BV' in J('location.hash'), [J(f"!!{PAINEL}") and J(f"{PAINEL}.getAttribute('aria-label')"), J('location.hash')])
        contexto(L, 'painel do B2 criado')
        n.zera()
        n.clica(botao_ini('+ Criar outro talhão', PAINEL), '+ Criar outro talhão')
        r11 = [J("document.querySelector('#fx_g_tal_faz').value"), J("document.querySelector('#fx_g_tal_decl').value"), J("document.querySelector('#fx_g_tal_t').value")]
        chk(f'{L} "+ Criar outro talhão na Boa Vista": fazenda herdada, nome e área vazios (R11)', r11 == ['Boa Vista', '', ''], r11)
        n.digita('#fx_g_tal_t', 'B3', 'nome'); n.digita('#fx_g_tal_decl', '40', 'área')
        n.clica(botao('Criar talhão', PAINEL) if J(f"!!({botao('Criar talhão', PAINEL)})") else botao('Salvar', PAINEL), 'Salvar')
        chk(f'{L} repetição: o 2º talhão sai com 2 cliques além de digitar nome e área (tarefa 8)', n.cliques == 2 and J(f"({PAINEL}||{{getAttribute:()=>''}}).getAttribute('aria-label')") == 'Talhão · B3', n.conta())
        rows = J("[...document.querySelectorAll('.cmd-d [role=row][data-rid]')].map(r=>r.innerText.split('\\n')[0])")
        chk(f'{L} Boa Vista com B1, B2 e B3 na grade', all(any(x.startswith(t) for x in rows) for t in ('B1', 'B2', 'B3')), rows)
        # alteração não salva segura o voltar do navegador (R06)
        n.clica(botao('Editar talhão', PAINEL), 'Editar talhão')
        n.digita('#fx_g_tal_decl', '41', 'área')
        n.volta()
        chk(f'{L} com alteração não salva, o voltar do navegador mantém o painel e avisa (R06)', J(f"!!{PAINEL}") and J("[...document.querySelectorAll('aside [role=alert]')].some(e=>/alterações não salvas/.test(e.innerText))") and J("document.querySelector('#fx_g_tal_decl').value") == '41',
            [J(f"!!{PAINEL}"), J("[...document.querySelectorAll('aside [role=alert]')].map(e=>e.innerText)")])
        n.clica(botao('Continuar editando', PAINEL) if J(f"!!({botao('Continuar editando', PAINEL)})") else botao_ini('Continuar', PAINEL), 'Continuar editando')
        n.clica(botao('Cancelar', PAINEL), 'Cancelar')
        # ---------------- indisponível ----------------
        limpa(); n.abre('CD-01', '#talhao=ZZ9')
        av = J("(document.querySelector('.cmd-aviso[role=alert]')||{}).innerText||''")
        chk(f'{L} #talhao=ZZ9: aviso visível e acessível, nada aberto, nada selecionado, com saída (SEL-02)', 'indisponível' in av and 'Nada foi aberto' in av and not J(f"!!{PAINEL}") and J('location.hash') == '' and J('!!(' + botao_ini('Ver todas', AVISO) + ')'), [av, J('location.hash')])
        chk(f'{L} o aviso não parece sucesso (sem verde)', J("getComputedStyle(document.querySelector('.cmd-aviso')).backgroundColor") not in ('rgb(30, 122, 76)', 'rgb(228, 243, 233)'), J("getComputedStyle(document.querySelector('.cmd-aviso')).backgroundColor"))
        foto(c, f'cd01_{L}_indisponivel')
        n.clica(botao_ini('Ver todas', AVISO), 'Ver todas as fazendas')
        chk(f'{L} "Ver todas as fazendas" tira o aviso', not J("!!document.querySelector('.cmd-aviso')"), J("(document.querySelector('.cmd-aviso')||{}).innerText"))
        contexto(L, 'depois do aviso', mestre=not larga)
        # as 7 telas de Cadastros: abrem sem erro, com no máximo um verde no cabeçalho; no computador a página não rola (só a lista e o painel
        # rolam por dentro do bloco: regra do cadp_fix_test 14 e do cadf_fix_lista_test 9, levada para cá no P9)
        for pag in ('CD-01', 'CD-02', 'CD-03', 'CD-04', 'CD-05', 'CD-06', 'CD-07'):
            limpa(); n.abre(pag)
            pg = J("(()=>{ const se=document.scrollingElement; const vd=[...document.querySelectorAll('header button,header a')].filter(b=>getComputedStyle(b).backgroundColor==='rgb(30, 122, 76)'); return {doc:se.scrollHeight<=innerHeight+1, verdes:vd.length, errs:(window.__errs||[]).length}; })()")
            chk(f'{L} {pag}: abre sem erro de script e com no máximo um verde no cabeçalho' + (' e a página não rola' if larga else ''), pg['errs'] == 0 and pg['verdes'] <= 1 and (pg['doc'] or not larga), pg)
finally:
    c.close(); srv.terminate()
print(f'RESULTADO: {len(OK)}/{len(OK) + len(FAIL)} ok' + (' · FALHAS: ' + '; '.join(FAIL) if FAIL else ''))
sys.exit(1 if FAIL else 0)
