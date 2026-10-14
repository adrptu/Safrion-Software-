# -*- coding: utf-8 -*-
"""VISOES-2 §3.6 · colunas só o essencial, no navegador (aceite h): a O.S. abre com O.S., Atividade, Talhão, Prazo, Fase e Progresso;
"Colunas +12" abre o painel agrupado pela pergunta (a identidade travada); marcar mostra, desmarcar oculta, "Ocultar coluna" no menu
da coluna; a escolha volta no próximo acesso e é por perfil; "Restaurar padrão"; o recorte ("X de Y") não muda; filtro de coluna oculta
segue como chip; celular abre com as 3 primeiras; a Situação vira ícone com o texto. Dados sintéticos; render em RENDER_DIR ou _render."""
import sys, os, time, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, servir

R = os.environ.get('RENDER_DIR') or os.path.join(HERE, '_render')
ok_n = 0; falhas = []
def chk(nome, cond, det=''):
    global ok_n
    if cond: ok_n += 1; print('OK  ' + nome, flush=True)
    else: falhas.append(nome); print('FALHA ' + nome + ' · ' + str(det)[:400], flush=True)

p, srv = servir(R); c = Chrome(); J = c.js
URL = f'http://127.0.0.1:{p}/OS.dc.html'
def abrir(perfil=None, limpa=False):
    c.goto(URL, espera=.8)
    J("(()=>{%s %s})()" % ("localStorage.clear();" if limpa else "", ("localStorage.setItem('safrion.perfilDemo',%s);" % json.dumps(perfil)) if perfil else ""))
    c.goto(URL, espera=1.6); J("window.__e=[];addEventListener('error',e=>window.__e.push(String(e.message)))")
def head(): return J("[...document.querySelectorAll('[data-g2g=g_os] [role=columnheader]')].map(h=>h.innerText.replace(/[⇅▾▴▲▼]/g,'').replace(/\\s+/g,' ').trim().toUpperCase())") or []
def conta(): return J("(()=>{const s=[...document.querySelectorAll('span')].find(x=>/^\\d+ de \\d+$/.test(x.innerText.trim())&&x.offsetParent); return s?s.innerText.trim():''})()")
def botao(): return J("(()=>{const b=document.querySelector('[data-g2cvb=g_os]'); return b?[b.innerText.replace(/\\s+/g,' ').trim(),b.getAttribute('aria-label'),b.getAttribute('aria-expanded')]:null})()")
def painel(): return J("(()=>{const d=document.querySelector('[data-g2cv=g_os]'); return d?d.innerText.replace(/\\n+/g,' | '):''})()") or ''
def marca(rot):
    J("(()=>{const l=[...document.querySelectorAll('[data-g2cv=g_os] label')].find(x=>x.innerText.trim()===%s); if(l) l.querySelector('input').click();})()" % json.dumps(rot)); time.sleep(.45)
def abre_painel():
    if not painel(): J("document.querySelector('[data-g2cvb=g_os]').click()"); time.sleep(.45)
PAD = ['O.S.', 'ATIVIDADE', 'TALHÃO', 'PRAZO', 'FASE', 'PROGRESSO']
try:
    c.aparelho(1440, 900, 1, False)
    abrir('Caio', limpa=True)
    h0, n0 = head(), conta()
    chk('C1 O.S. abre com exatamente as 6 colunas de "Abre com", na ordem', h0 == PAD, h0)
    chk('C2 botão "Colunas +12" com o número de ocultas no nome acessível', botao() == ['Colunas +12', 'Colunas · 12 ocultas', 'false'], botao())
    ico = J("[...document.querySelectorAll('[data-g2g=g_os] [role=row] [role=img]')].map(x=>x.getAttribute('aria-label'))") or []
    chk('C3 Situação vira ícone antes da O.S., com o texto no nome acessível', len(ico) >= 3 and all(x.startswith('Situação: ') for x in ico) and any('Falta insumo' in x for x in ico), ico)
    abre_painel(); pn = painel()
    grupos = [g for g in ['O QUÊ', 'QUEM', 'QUANDO', 'ONDE', 'MEDIDAS', 'SITUAÇÃO', 'OUTRAS'] if g in pn.upper()]
    dis = J("[...document.querySelectorAll('[data-g2cv=g_os] input')].filter(i=>i.disabled).map(i=>i.closest('label').innerText.trim())")
    chk('C4 painel agrupado pela pergunta, na ordem; a identidade (O.S.) fica travada', grupos == ['O QUÊ', 'QUEM', 'QUANDO', 'ONDE', 'MEDIDAS', 'SITUAÇÃO', 'OUTRAS'] and dis == ['O.S.'] and botao()[2] == 'true', [grupos, dis])
    marca('Situação'); marca('Quem resolve')
    h1 = head()
    chk('C5 marcar mostra: Quem resolve e Situação entram depois do padrão, na ordem da grade; o recorte não muda', h1 == PAD + ['SITUAÇÃO', 'QUEM RESOLVE'] and conta() == n0, [h1, conta(), n0])
    marca('Prazo')
    chk('C6 desmarcar oculta (Prazo sai) e o botão conta 11 ocultas', 'PRAZO' not in head() and botao()[0] == 'Colunas +11', [head(), botao()])
    J("(()=>{const d=document.querySelector('[data-g2cv=g_os]'); d.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true}));})()"); time.sleep(.4)
    chk('C7 Esc fecha o painel e o foco volta ao botão Colunas', not painel() and J("document.activeElement&&document.activeElement.getAttribute('data-g2cvb')") == 'g_os')
    abrir('Caio')
    chk('C8 a escolha volta no próximo acesso', head() == ['O.S.', 'ATIVIDADE', 'TALHÃO', 'FASE', 'PROGRESSO', 'SITUAÇÃO', 'QUEM RESOLVE'], head())
    abrir('Ana')
    chk('C9 a escolha é por perfil: Ana abre no padrão', head() == PAD, head())
    abrir('Caio'); abre_painel()
    J("(()=>{const b=[...document.querySelectorAll('[data-g2cv=g_os] button')].find(x=>x.innerText.trim()==='Restaurar padrão'); if(b) b.click();})()"); time.sleep(.45)
    chk('C10 "Restaurar padrão" volta às 6 colunas e some quando já está no padrão', head() == PAD and 'Restaurar padrão' not in painel(), [head(), painel()[-80:]])
    J("(()=>{const b=[...document.querySelectorAll('[data-g2cv=g_os] button')].find(x=>x.innerText.trim()==='Fechar'); if(b) b.click();})()"); time.sleep(.3)
    # filtro numa coluna e depois ocultar a coluna pelo menu dela: o recorte continua visível como chip
    J("(()=>{const h=[...document.querySelectorAll('[data-g2g=g_os] [role=columnheader]')].find(x=>/^fase/i.test(x.innerText.trim())); h.querySelector('.g2fb').click();})()"); time.sleep(.45)
    J("(()=>{const d=[...document.querySelectorAll('[role=dialog]')].find(x=>/Filtrar por valores/i.test(x.innerText)); const lim=[...d.querySelectorAll('button')].find(b=>b.innerText.trim()==='Limpar'); lim.click();})()"); time.sleep(.3)
    J("(()=>{const d=[...document.querySelectorAll('[role=dialog]')].find(x=>/Filtrar por valores/i.test(x.innerText)); const l=[...d.querySelectorAll('label')].find(x=>/^A liberar/.test(x.innerText.trim())); l.querySelector('input').click(); [...d.querySelectorAll('button')].find(b=>b.innerText.trim()==='OK').click();})()"); time.sleep(.5)
    n1 = conta()
    J("(()=>{const h=[...document.querySelectorAll('[data-g2g=g_os] [role=columnheader]')].find(x=>/^fase/i.test(x.innerText.trim())); h.querySelector('.g2fb').click();})()"); time.sleep(.45)
    tem_oc = J("!![...document.querySelectorAll('button.g2fi')].find(x=>x.innerText.trim()==='Ocultar coluna')")
    J("(()=>{const b=[...document.querySelectorAll('button.g2fi')].find(x=>x.innerText.trim()==='Ocultar coluna'); if(b) b.click();})()"); time.sleep(.45)
    chips = J("[...document.querySelectorAll('span')].filter(s=>/^Fase: /.test(s.innerText.trim())).map(s=>s.innerText.trim())") or []
    chk('C11 "Ocultar coluna" no menu da coluna; o filtro da coluna oculta segue como chip e o recorte não muda',
        tem_oc and 'FASE' not in head() and conta() == n1 and n1 != n0 and any('A liberar' in x for x in chips), [tem_oc, head(), conta(), n1, chips])
    J("(()=>{const o=document.querySelector('[data-g2g=g_os] [role=columnheader] .g2fb'); })()")
    menu_id = J("(()=>{const h=document.querySelector('[data-g2g=g_os] [role=columnheader]'); h.querySelector('.g2fb').click(); return 1;})()"); time.sleep(.4)
    chk('C12 a identidade (O.S.) não oferece "Ocultar coluna"', not J("!![...document.querySelectorAll('button.g2fi')].find(x=>x.innerText.trim()==='Ocultar coluna')"))
    c.aparelho(390, 844, 2, True); abrir('Otávio', limpa=True)
    chk('C13 celular abre com as 3 primeiras do padrão', head() == PAD[:3], head())
    errs = J("(window.__e||[]).length") or 0
    chk('C14 sem erro de JS', not errs, J("window.__e"))
finally:
    c.close(); srv.terminate()
print(f'RESULTADO: {ok_n}/{ok_n + len(falhas)}' + (' · FALHAS: ' + '; '.join(falhas) if falhas else ''))
sys.exit(1 if falhas else 0)
