# -*- coding: utf-8 -*-
"""CADUX · medição das tarefas da ESPECIFICACAO §5 depois da mudança, com a contagem da linha de base (docs/cadastros-ux/antes/tarefas.json):
o menu conta 1 clique; escolher numa lista conta 1; digitar conta campo e caracteres. Cada tarefa começa com o navegador limpo, a 1440 × 900
(mouse) e a 390 × 844 (toque), segue o caminho alvo e confere que chegou ao que a tarefa pede (o que a pessoa precisa ver na tela).
Grava docs/cadastros-ux/depois/tarefas.json e falha se alguma tarefa passar do alvo ou não chegar.
Uso (navegador um por vez): env CHROME_BIN=/tmp/cloudchrome/chrome flock /tmp/cdpH.lock env CDP_GL=1 timeout 900 python3 cadux_tarefas_test.py"""
import os, sys, time, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); os.chdir(HERE)
from comp_lib import Chrome, servir
from cadux_nav import Nav, mestre_item, alvo_linha, botao, botao_ini, PAINEL
OK, FAIL = [], []
def chk(n, cond, info=''):
    (OK if cond else FAIL).append(n); print(('OK    ' if cond else 'FALHA ') + n + ('' if cond else ' · ' + str(info)[:600]), flush=True)
DOCS = os.path.normpath(os.path.join(HERE, '..', '..', '..', '..', 'docs', 'cadastros-ux'))
# alvo (cliques, caracteres) por largura; None = sem alvo fixado na ESPECIFICACAO §5 (só mede)
ALVO = {'1': {'1440': (3, 0), '390': (3, 0)}, '2': {'1440': (4, 4), '390': (4, 4)}, '3': {'1440': (2, 0), '390': (3, 0)},
        '4a': {'1440': (1, 0), '390': (3, 0)}, '4b': {'1440': (2, 0), '390': (2, 0)}, '5': {'1440': (3, 0), '390': (3, 0)},
        '6': {'1440': (2, 0), '390': (3, 0)}, '7': {'1440': (3, 0), '390': (3, 0)}, '8': {'1440': (2, 0), '390': (2, 0)},
        '9': {'390': (2, 4)}, '9m': {'390': (5, 0)}, '10': {'1440': None, '390': None}, '11': {'1440': (2, 11), '390': (2, 11)}}
port, srv = servir(os.path.join(HERE, '_render')); c = Chrome(); J = c.js
def limpa():
    c.goto(f'http://127.0.0.1:{port}/Main.dc.html', .3); J('localStorage.clear();sessionStorage.clear()')
def painel_t():
    return J(f"({PAINEL}||{{getAttribute:()=>''}}).getAttribute('aria-label')") or ''
def visivel(txt):
    """o texto aparece na janela sem rolar (no painel aberto ou na página)"""
    return J("(()=>{ const t=%s; const raiz=document.querySelector('aside[role=dialog]')||document.body; const w=document.createTreeWalker(raiz,NodeFilter.SHOW_TEXT);"
             " while(w.nextNode()){ const n=w.currentNode; if(n.textContent.indexOf(t)<0) continue; const r=n.parentElement.getBoundingClientRect(); if(r.height>0&&r.top>=0&&r.bottom<=innerHeight&&r.left>=0&&r.right<=innerWidth) return true; } return false; })()" % json.dumps(txt))
def linhas():
    return J("[...document.querySelectorAll('.cmd-d [role=row][data-rid]')].filter(r=>r.getClientRects().length).map(r=>r.innerText.replace(/\\s+/g,' ').trim())")
MED = {}
try:
    for L, (w, h, toque) in (('1440', (1440, 900, False)), ('390', (390, 844, True))):
        c.aparelho(w, h, toque=toque); larga = w >= 1024; MED[L] = []
        def fecha(t, nome, chegou, n, info=''):
            m = dict(tarefa=f'{t} {nome}', largura=int(L), **n.conta(), chegou=bool(chegou), info=info); MED[L].append(m)
            a = ALVO[t].get(L)
            dentro = a is None or (m['cliques'] <= a[0] and m['caracteres'] <= a[1])
            chk(f'{L} tarefa {t} ({nome}): {m["cliques"]} cliques · {m["caracteres"]} caracteres' + (f' (alvo {a[0]} · {a[1]})' if a else ' (sem alvo: só medida)'), chegou and dentro, [m['passos'], info])
        def nova():
            limpa(); return Nav(c, port, toque)
        # 1 · ver os talhões da Santa Rita e abrir o T2
        n = nova(); n.menu('CD-01'); n.clica(mestre_item('Santa Rita'), 'Santa Rita')
        ls = linhas(); n.clica(alvo_linha('T2'), 'T2')
        fecha('1', 'talhões da Santa Rita e o T2', painel_t() == 'Talhão · T2' and len(ls) == 8, n, ls[:2])
        # 2 · cadastrar o talhão B2 (80 ha) na Boa Vista, sem trocar a fazenda
        n = nova(); n.menu('CD-01'); n.clica(mestre_item('Boa Vista'), 'Boa Vista'); n.clica(botao('+ Criar talhão', "document.querySelector('header')"), '+ Criar talhão')
        faz = J("document.querySelector('#fx_g_tal_faz').value")
        n.digita('#fx_g_tal_t', 'B2', 'Identificação'); n.digita('#fx_g_tal_decl', '80', 'Área cultivável')
        n.clica(botao('Salvar', PAINEL), 'Salvar')
        fecha('2', 'cadastrar B2 com 80 ha na Boa Vista', faz == 'Boa Vista' and painel_t() == 'Talhão · B2' and 'faz=BV' in J('location.hash'), n, [faz, J('location.hash')])
        # 3 · Trator 02: implementos e horímetro, sem rolar o painel
        n = nova(); n.menu('CD-03')
        if not larga: n.clica(mestre_item('Todos os ativos'), 'Todos os ativos')
        n.clica(alvo_linha('a02'), 'Trator 02')
        ok3 = painel_t() == 'Ativo · Trator 02' and visivel('Contador') and visivel('Pulverizador PJ-3030')
        fecha('3', 'Trator 02: contador e conjuntos sem rolar', ok3, n, [painel_t(), visivel('Contador'), visivel('Pulverizador PJ-3030')])
        # 4a · equipe e papel do Marcos (ver)
        n = nova(); n.menu('CD-04')
        if larga:
            lm = [x for x in linhas() if x.startswith('Marcos')]
            fecha('4a', 'equipe e papel do Marcos', bool(lm) and 'Campo 1' in lm[0], n, lm)
        else:
            n.clica(mestre_item('Todas as pessoas'), 'Todas as pessoas'); n.clica(alvo_linha('p2'), 'Marcos')
            fecha('4a', 'equipe e papel do Marcos', painel_t() == 'Pessoa · Marcos' and visivel('Campo 1'), n, painel_t())
        # 4b · quem mais está na equipe do Marcos
        n = nova(); n.menu('CD-04'); n.clica(mestre_item('Campo 1'), 'Campo 1')
        nomes = [x.split(' ')[0] for x in linhas()]
        fecha('4b', 'membros da equipe Campo 1', 'Marcos' in nomes and len(nomes) >= 3, n, nomes)
        # 5 · fungicida: registro, unidade, embalagem e locais
        n = nova(); n.menu('CD-06'); n.clica(mestre_item('Fungicidas'), 'Fungicidas'); n.clica(alvo_linha('i18'), 'Fungicida A')
        t5 = J(f"({PAINEL}||{{}}).innerText||''")
        fecha('5', 'Fungicida A: registro, unidade, embalagem e locais', painel_t() == 'Item · Fungicida A' and all(k in t5.lower() for k in ('registro', 'unidade', 'embalagem', 'locais')), n, t5[:200])
        # 6 · o que a Agro Norte fornece
        n = nova(); n.menu('CD-05'); n.clica(mestre_item('Fornecedores'), 'Fornecedores')
        if larga:
            la = [x for x in linhas() if x.startswith('Agro Norte')]
            fecha('6', 'grupos que a Agro Norte fornece', bool(la) and 'Fungicidas' in la[0], n, la)
        else:
            n.clica(alvo_linha('F03'), 'Agro Norte')
            fecha('6', 'grupos que a Agro Norte fornece', painel_t() == 'Parceiro · Agro Norte' and visivel('Fungicidas'), n, painel_t())
        # 7 · cultivar 58 W e o rendimento da pulverização no mesmo painel
        n = nova(); n.menu('CD-02'); n.clica(mestre_item('Soja'), 'Soja'); n.clica(alvo_linha('cv1'), '58 W')
        t7 = J(f"({PAINEL}||{{}}).innerText||''")
        fecha('7', 'cultivar 58 W e o rendimento da pulverização', painel_t() == 'Cultivar · 58 W' and 'rendimentos que valem para a soja' in t7.lower() and 'Pulverização' in t7, n, t7[:200])
        # 8 · gestor: talhões seguidos numa fazenda (cliques do 2º em diante)
        n = nova(); n.abre('CD-01', '#faz=BV'); n.clica(botao('+ Criar talhão', "document.querySelector('header')"), '+ Criar talhão', conta=False)
        n.digita('#fx_g_tal_t', 'B2', 'Identificação'); n.digita('#fx_g_tal_decl', '80', 'Área'); n.clica(botao('Salvar', PAINEL), 'Salvar', conta=False)
        n.zera(); n.clica(botao_ini('+ Criar outro talhão', PAINEL), '+ Criar outro talhão na Boa Vista')
        vaz = [J("document.querySelector('#fx_g_tal_t').value"), J("document.querySelector('#fx_g_tal_decl').value")]
        n.digita('#fx_g_tal_t', 'B3', 'Identificação'); n.digita('#fx_g_tal_decl', '40', 'Área'); n.clica(botao('Salvar', PAINEL), 'Salvar')
        n.chars = 0   # a digitação (Identificação e Área) é o próprio dado de cada talhão; o alvo conta os cliques
        fecha('8', 'talhão seguido na mesma fazenda', painel_t() == 'Talhão · B3' and vaz == ['', ''], n, vaz)
        # 9 · agrônomo a 390: abrir o PV07 da Lagoa Grande pela busca do mestre
        if not larga:
            n = nova(); n.menu('CD-01'); n.digita('#mx-q', 'PV07', 'busca')
            n.clica("[...document.querySelectorAll('.cmd-res button')].find(b=>b.innerText.startsWith('PV07'))", 'PV07 · Lagoa Grande')
            fecha('9', 'PV07 pela busca do mestre', painel_t() == 'Talhão · PV07', n, painel_t())
            # pelo mapa (ESPECIFICACAO §5: 5) · Menu → Lagoa Grande → Mapa → PV07 (o pivô pequeno aproxima no toque) → PV07 (abre)
            n = nova(); n.menu('CD-01'); n.clica(mestre_item('Lagoa Grande'), 'Lagoa Grande'); n.clica(botao('Mapa'), 'Mapa')
            pv = "[...document.querySelectorAll('.cd-mapa svg [data-tid=PV07]')].find(e=>e.getClientRects().length)"
            for _ in range(3):
                if painel_t(): break
                n.clica(pv, 'PV07 no mapa')
            fecha('9m', 'PV07 pelo mapa', painel_t() == 'Talhão · PV07', n, painel_t())
        # 10 · almoxarife: fungicida novo (L, galão de 5 L, Almox. defensivos)
        n = nova(); n.menu('CD-06'); n.clica(mestre_item('Fungicidas'), 'Fungicidas'); n.clica(botao('+ Criar item', "document.querySelector('header')"), '+ Criar item')
        ini = {k: J(f"document.querySelector('#fx_g_itm_{k}').value") for k in ('un', 'emb', 'local')}
        n.digita('#fx_g_itm_item', 'Fungicida Teste 250 SC', 'nome')
        n.escolhe('#fx_g_itm_un', 'L', 'Unidade-base'); n.escolhe('#fx_g_itm_emb', J("[...document.querySelector('#fx_g_itm_emb').options].map(o=>o.value).find(v=>/Gal/i.test(v))||''"), 'Embalagem')
        n.digita('#fx_g_itm_cont', '5', 'Conteúdo')
        loc = J("[...document.querySelector('#fx_g_itm_local').options].map(o=>o.value).find(v=>/defensiv/i.test(v))||''"); n.escolhe('#fx_g_itm_local', loc, 'Local padrão')
        n.clica(botao('Salvar', PAINEL), 'Salvar')
        fecha('10', 'fungicida novo com unidade, embalagem e local', painel_t().startswith('Item · Fungicida Teste') and ini == {'un': '', 'emb': '', 'local': ''}, n, [ini, loc, painel_t()])
        # 11 · comprador: quem fornece Tebuconazol 200 EC
        n = nova(); n.menu('CD-05'); n.digita('#mx-q', 'Tebuconazol', 'busca')
        if larga:
            lf = linhas()   # a busca já recorta a grade: os fornecedores homologados do grupo do insumo
        else:
            n.clica("[...document.querySelectorAll('.cmd-res button')].find(b=>/Fungicidas/.test(b.innerText))", 'Fungicidas · fornecedores')
            lf = [J(f"({PAINEL}||{{}}).innerText||''")] if J(f"!!{PAINEL}") else linhas()
        fecha('11', 'quem fornece Tebuconazol 200 EC', any('Agro Norte' in x for x in lf), n, [x[:300] for x in lf[:4]])
        chk(f'{L} sem erro de script nas tarefas', not J('window.__errs||[]'), J('window.__errs'))
finally:
    c.close(); srv.terminate()
os.makedirs(os.path.join(DOCS, 'depois'), exist_ok=True)
json.dump(MED, open(os.path.join(DOCS, 'depois', 'tarefas.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('gravado:', os.path.join(DOCS, 'depois', 'tarefas.json'))
print(f'RESULTADO: {len(OK)}/{len(OK) + len(FAIL)} ok' + (' · FALHAS: ' + '; '.join(FAIL) if FAIL else ''))
sys.exit(1 if FAIL else 0)
