# -*- coding: utf-8 -*-
"""CADUX · regressão de navegador dos achados da revisão adversarial do Codex (base 5d533a8) que dependem do navegador de verdade:
  1 · voltar do navegador com alteração não salva (R06, AC-21): o painel aberto pelo endereço (#reg=, X-REG da MA), a ficha da fazenda,
      a ficha da equipe e a criação da fazenda, a 1440 (mouse) e a 390 (toque); antes, o voltar saía para o Main e perdia o digitado;
  9 · toque duplo a 390: o 2º toque não abre outro registro dentro do painel que acabou de abrir; um toque depois, normal, abre;
 11 · 390 px: no mestre só a lista de cartões (o detalhe não aparece embaixo com a lista espremida); a 1ª linha da Lagoa Grande e da
      natureza do CD-07 cabe na tela; as abas ficam inteiras; um verde por tela (o Próximo passo do detalhe é secundário); "‹ {grupo}"
      no painel; 13 · #faz=BV&talhao=T2 avisa na tela.
O que é regra sem layout fica no cadux_rev_test.py (node).
Uso (navegador um por vez): env CHROME_BIN=/tmp/cloudchrome/chrome flock /tmp/cdpH.lock env CDP_GL=1 timeout 900 python3 cadux_rev_nav_test.py"""
import os, sys, time, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); os.chdir(HERE)
from comp_lib import Chrome, servir
from cadux_nav import Nav, mestre_item, alvo_linha, botao, botao_ini, PAINEL
OK, FAIL = [], []
def chk(n, cond, info=''):
    (OK if cond else FAIL).append(n); print(('OK    ' if cond else 'FALHA ') + n + ('' if cond else ' · ' + str(info)[:600]), flush=True)
port, srv = servir(os.path.join(HERE, '_render')); c = Chrome(); J = c.js
def limpa():
    c.goto(f'http://127.0.0.1:{port}/Main.dc.html', .3); J('localStorage.clear();sessionStorage.clear()')
def pagina():
    return J('location.pathname.split("/").pop()')
def aviso_nao_salvo():
    return J("[...document.querySelectorAll('aside [role=alert]')].some(e=>e.getClientRects().length&&/alterações não salvas/.test(e.innerText))")
def titulo():
    return J(f"({PAINEL}||{{getAttribute:()=>''}}).getAttribute('aria-label')") or ''
def ponto(expr):
    return J("(()=>{ const e=(%s); if(!e) return null; e.scrollIntoView({block:'center'}); const r=e.getBoundingClientRect(); return {x:r.left+r.width/2,y:r.top+r.height/2}; })()" % expr)
def toque_duplo(p, intervalo=.12):
    for i in range(2):
        c.call('Input.dispatchTouchEvent', {'type': 'touchStart', 'touchPoints': [{'x': p['x'], 'y': p['y']}]}); time.sleep(.03)
        c.call('Input.dispatchTouchEvent', {'type': 'touchEnd', 'touchPoints': []})
        if i == 0: time.sleep(intervalo)
    time.sleep(.9)
VERDES_TELA = r"""[...document.querySelectorAll('button,a')].filter(e=>{ const r=e.getBoundingClientRect(); return r.width>1&&r.height>1&&getComputedStyle(e).visibility!=='hidden'&&getComputedStyle(e).backgroundColor==='rgb(30, 122, 76)'&&!e.closest('aside'); }).map(e=>e.innerText.replace(/\s+/g,' ').trim())"""
try:
    # ---------------- 1 · voltar do navegador com alteração não salva ----------------
    for L, (w, h, toque) in (('1440', (1440, 900, False)), ('390', (390, 844, True))):
        c.aparelho(w, h, toque=toque); n = Nav(c, port, toque)
        # painel aberto pelo endereço de outra frente (#reg=a02 é o link da MA): era a 1ª entrada da tela no histórico
        limpa(); n.abre('CD-03', '#reg=a02'); time.sleep(.4)
        n.clica(botao('Editar ativo', PAINEL), 'Editar ativo'); n.digita('#fx_g_atv_custo_h', '222', 'Custo por hora')
        n.volta()
        chk(f'{L} R06/AC-21 CD-03#reg=a02 › Editar ativo › R$/h 222 › voltar: fica no CD-03, painel com "Há alterações não salvas" e o 222',
            pagina() == 'CD-03.dc.html' and aviso_nao_salvo() and J("(document.querySelector('#fx_g_atv_custo_h')||{}).value") == '222',
            [pagina(), aviso_nao_salvo(), J("(document.querySelector('#fx_g_atv_custo_h')||{}).value")])
        n.clica(botao('Continuar editando', PAINEL), 'Continuar editando')
        n.clica(botao('Cancelar', PAINEL), 'Cancelar'); n.clica(botao('Descartar alterações', PAINEL), 'Descartar')
        n.volta()
        chk(f'{L} R06 depois de descartar, o voltar seguinte sai da tela (nenhum voltar sem efeito)', pagina() == 'Main.dc.html', pagina())
        # ficha da fazenda (CD-01) e da equipe (CD-04): o grupo não é item no endereço, e a ficha não empilhava nada
        limpa(); n.abre('CD-01'); n.clica(mestre_item('Santa Rita'), 'Santa Rita'); n.clica(botao('Ver ficha da fazenda'), 'Ver ficha')
        n.clica(botao('Editar fazenda', PAINEL), 'Editar fazenda'); n.digita('#fx_g_faz_nome', 'Santa Rita X', 'Nome')
        n.volta()
        chk(f'{L} R06/AC-21 CD-01 › Santa Rita › Ver ficha › Editar fazenda › digitar › voltar: fica, com o aviso e o nome digitado',
            pagina() == 'CD-01.dc.html' and aviso_nao_salvo() and J("(document.querySelector('#fx_g_faz_nome')||{}).value") == 'Santa Rita X', [pagina(), aviso_nao_salvo()])
        limpa(); n.abre('CD-01')
        if w >= 1024: n.clica(mestre_item('Todas'), 'Todas')
        n.clica(botao('+ Criar fazenda'), '+ Criar fazenda'); n.digita('#fx_g_faz_nome', 'Fazenda Nova X', 'Nome')
        n.volta()
        chk(f'{L} R06/AC-21 CD-01 › + Criar fazenda › nome › voltar: fica, com o aviso e o nome', pagina() == 'CD-01.dc.html' and aviso_nao_salvo()
            and J("(document.querySelector('#fx_g_faz_nome')||{}).value") == 'Fazenda Nova X', [pagina(), aviso_nao_salvo()])
        limpa(); n.abre('CD-04'); n.clica(mestre_item('Campo 1'), 'Campo 1'); n.clica(botao_ini('Ver ficha'), 'Ver ficha')
        n.clica(botao_ini('Editar', PAINEL), 'Editar'); fid = J("(()=>{ const e=[...document.querySelectorAll('aside input[type=text],aside input:not([type])')].find(x=>!x.readOnly&&!x.disabled&&x.getClientRects().length); return e?e.id:''; })()")
        n.digita('#' + fid, 'Campo 1 X', 'campo da equipe'); n.volta()
        chk(f'{L} R06/AC-21 CD-04 › Campo 1 › Ver ficha › Editar › digitar › voltar: fica, com o aviso e o digitado', pagina() == 'CD-04.dc.html' and aviso_nao_salvo()
            and J(f"(document.querySelector('#{fid}')||{{}}).value") == 'Campo 1 X', [fid, pagina(), aviso_nao_salvo()])
        chk(f'{L} sem erro de script', not J('window.__errs||[]'), J('window.__errs'))

    # ---------------- 9 · toque duplo a 390 ----------------
    c.aparelho(390, 844, toque=True); n = Nav(c, port, True)
    casos = [('CD-07', '#dim=natureza', "document.querySelector('.cmd-d [role=row][data-rid] .g2alvo')"),
             ('CD-01', '#faz=SR', alvo_linha('T2')), ('CD-03', '#classe=trator', "document.querySelector('.cmd-d [role=row][data-rid] .g2alvo')"),
             ('CD-06', '#grp=GR6', "document.querySelector('.cmd-d [role=row][data-rid] .g2alvo')")]
    for pag, hh, expr in casos:
        limpa(); n.abre(pag, hh); time.sleep(.4); p = ponto(expr); c.toque(p['x'], p['y']); time.sleep(.5); t1 = titulo()
        limpa(); n.abre(pag, hh); time.sleep(.4); p = ponto(expr); toque_duplo(p); t2 = titulo()
        chk(f'390 achado 9 {pag}{hh}: toque duplo na linha abre o mesmo registro do toque simples ({t1})', t1 and t1 == t2, [t1, t2])
    # o bloqueio só vale para o 2º toque: depois dele, um toque normal num filho do painel abre o filho
    limpa(); n.abre('CD-07', '#dim=natureza'); time.sleep(.4); toque_duplo(ponto("document.querySelector('.cmd-d [role=row][data-rid] .g2alvo')")); t1 = titulo()
    fil = "[...document.querySelectorAll('aside[role=dialog] button')].find(b=>b.getClientRects().length&&/^3\\.1\\.0\\d/.test(b.innerText.trim()))"
    tem = J(f"!!({fil})")
    if tem: time.sleep(.6); n.clica(fil, '1º filho'); t2 = titulo()
    chk('390 achado 9 CD-07: depois do toque duplo, um toque normal no filho do painel abre o filho (o bloqueio é só do 2º toque)', tem and t2 != t1 and '3.1.0' in t2, [t1, tem and t2])

    # ---------------- 11 · 390 px: mestre, 1ª linha, abas, um verde, "‹ {grupo}" ----------------
    for pag in ('CD-01', 'CD-07', 'CD-06'):
        limpa(); n.abre(pag); time.sleep(.3)
        o = J("(()=>{ const d=document.querySelector('.cmd-d'); const it=[...document.querySelectorAll('.cmd-lista .cmd-it')].filter(e=>e.getClientRects().length); const r=it[0]&&it[0].getBoundingClientRect();"
              " return {niv:document.querySelector('.cmd').getAttribute('data-nivel'),det:!!d&&d.getClientRects().length>0,n:it.length,c1:r?[Math.round(r.top),Math.round(r.bottom)]:null,ih:innerHeight}; })()")
        chk(f'390 achado 11 {pag} no mestre: só a lista de cartões (o detalhe não aparece embaixo) e o 1º cartão inteiro na tela',
            o['niv'] == 'm' and not o['det'] and o['n'] >= 3 and o['c1'] and o['c1'][1] <= o['ih'], o)
    for pag, hh in (('CD-01', '#faz=LG'), ('CD-07', '#dim=natureza'), ('CD-01', '#faz=SR')):
        limpa(); n.abre(pag, hh); time.sleep(.3)
        o = J("(()=>{ const rs=[...document.querySelectorAll('.cmd-d [role=row][data-rid]')].filter(r=>r.getClientRects().length); const r=rs[0]&&rs[0].getBoundingClientRect();"
              " const ab=[...document.querySelectorAll('.cadx-abas [role=tab]')].filter(t=>t.getClientRects().length).map(t=>{ const b=t.getBoundingClientRect(); return [t.innerText.replace(/\\s+/g,' ').trim(),Math.round(b.left),Math.round(b.right)]; });"
              " return {r0:r?[Math.round(r.top),Math.round(r.bottom)]:null,ih:innerHeight,iw:innerWidth,abas:ab,sw:document.documentElement.scrollWidth}; })()")
        chk(f'390 achado 11 (I32/I33) {pag}{hh}: a 1ª linha da grade cabe na tela sem rolar; abas inteiras; sem rolagem lateral',
            o['r0'] and o['r0'][1] <= o['ih'] and all(a[1] >= 0 and a[2] <= o['iw'] for a in o['abas']) and o['sw'] <= o['iw'], o)
    limpa(); n.abre('CD-01', '#faz=BV'); time.sleep(.3); vd = J(VERDES_TELA)
    chk('390 achado 11 CD-01 Boa Vista: um verde na tela ("+ Criar talhão"); "Informar CAR" do Próximo passo é secundário, no mesmo lugar',
        vd == ['+ Criar talhão'] and J(f"!!({botao_ini('Informar CAR')})"), [vd, J(f"!!({botao_ini('Informar CAR')})")])
    limpa(); n.abre('CD-07'); n.clica(mestre_item('Todas as dimensões'), 'Todas as dimensões'); vd = J(VERDES_TELA)
    chk('390 achado 11 CD-07 Todas as dimensões: um verde na tela ("+ Criar código"); "Publicar estrutura" é secundário',
        vd == ['+ Criar código'] and J(f"!!({botao_ini('Publicar estrutura')})"), [vd, J(f"!!({botao_ini('Publicar estrutura')})")])
    limpa(); n.abre('CD-01', '#faz=SR'); n.clica(alvo_linha('T2'), 'T2')
    chk('390 achado 11 painel do T2 com "‹ Santa Rita" no topo, que volta à Santa Rita', J(f"!!({botao('‹ Santa Rita', PAINEL)})"), titulo())
    if J(f"!!({botao('‹ Santa Rita', PAINEL)})"):
        n.clica(botao('‹ Santa Rita', PAINEL), '‹ Santa Rita')
        chk('390 "‹ Santa Rita" fecha o painel e mostra a Santa Rita', not J(f"!!{PAINEL}") and J("document.querySelector('#dx-t').innerText") == 'Santa Rita', [titulo(), J("document.querySelector('#dx-t').innerText")])
    # SEL-02 a 390: com o detalhe oculto de fato no mestre, o aviso do registro indisponível vai para cima da lista (uma cópia só no DOM)
    for pag, hh, ent in (('CD-01', '#talhao=ZZ9', 'Talhão'), ('CD-02', '#cv=zz', 'Cultivar'), ('CD-03', '#atv=zz', 'Ativo'), ('CD-04', '#pes=zz', 'Pessoa'),
                         ('CD-05', '#par=zz', 'Parceiro'), ('CD-06', '#item=zz', 'Item'), ('CD-07', '#cod=zz', 'Código')):
        limpa(); n.abre(pag, hh); time.sleep(.3)
        o = J("(()=>{ const as=[...document.querySelectorAll('.cmd-aviso')]; const a=as[0]; const r=a&&a.getBoundingClientRect(); const b=a&&a.querySelector('button');"
              " return {n:as.length,role:a&&a.getAttribute('role'),vis:!!r&&r.height>0&&r.bottom<=innerHeight,t:a?a.innerText.replace(/\\s+/g,' ').trim():'',saida:!!b&&b.getClientRects().length>0,"
              " niv:document.querySelector('.cmd').getAttribute('data-nivel'),cartoes:[...document.querySelectorAll('.cmd-lista .cmd-it')].filter(e=>e.getClientRects().length).length,painel:!!document.querySelector('aside[role=dialog]')}; })()")
        chk(f'390 SEL-02 {pag}{hh}: aviso "{ent} … indisponível" visível em cima da lista, com saída, uma cópia só, nada aberto',
            o['n'] == 1 and o['role'] == 'alert' and o['vis'] and o['t'].startswith(ent) and 'indisponível' in o['t'] and (o['saida'] or pag == 'CD-07') and not o['painel'] and (o['niv'] != 'm' or o['cartoes'] >= 2), o)
    # ---------------- 13 · endereço com a fazenda errada para o talhão: aviso na tela ----------------
    c.aparelho(1440, 900); limpa(); n = Nav(c, port, False); n.abre('CD-01', '#faz=BV&talhao=T2'); time.sleep(.3)
    av = J("(()=>{ const a=document.querySelector('.cmd-aviso'); return a&&a.getClientRects().length?[a.getAttribute('role'),a.innerText.replace(/\\s+/g,' ').trim()]:null; })()")
    chk('1440 achado 13 #faz=BV&talhao=T2: abre o T2 da Santa Rita e diz na tela, com role=alert, que o talhão é da Santa Rita',
        av and av[0] == 'alert' and 'é da Santa Rita, não da Boa Vista' in av[1] and titulo() == 'Talhão · T2' and J('location.hash') == '#faz=SR&talhao=T2', [av, titulo(), J('location.hash')])
finally:
    try: c.close()
    except Exception: pass
    srv.terminate()
print(f'RESULTADO: {len(OK)}/{len(OK) + len(FAIL)} ok' + (' · FALHAS: ' + '; '.join(FAIL) if FAIL else ''))
sys.exit(1 if FAIL else 0)
