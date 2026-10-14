# -*- coding: utf-8 -*-
"""VISOES-2 §3.3–3.4 e §8 ponto 3 · toda forma lê o mesmo recorte, no navegador: Kanban com raias por grupo (o nome desce), trilha e filtros
em chips removíveis acima do conteúdo em Kanban, Calendário e Carga; filtro de Talhão limita os grupos com a O.S. de dois talhões (OS-0421,
T1 e T2; Codex 6168779649 achado 2); o recorte do Painel suspende a trilha sem apagá-la. Dados sintéticos; render em RENDER_DIR ou _render."""
import sys, os, time, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, servir

R = os.environ.get('RENDER_DIR') or os.path.join(HERE, '_render')
ok_n = 0; falhas = []
def chk(nome, cond, det=''):
    global ok_n
    if cond: ok_n += 1; print('OK  ' + nome, flush=True)
    else: falhas.append(nome); print('FALHA ' + nome + ' · ' + str(det)[:500], flush=True)

p, srv = servir(R); c = Chrome(); J = c.js
B = f'http://127.0.0.1:{p}/OS.dc.html'
def abre(q, w=1.6):
    c.goto(B + q, w); J("window.__e=window.__e||[];addEventListener('error',e=>window.__e.push(String(e.message)))")
def raias(): return J("[...document.querySelectorAll('.os-raia')].filter(r=>r.offsetParent).map(r=>[r.querySelector('.os-raia-cab b').innerText.trim(),[...r.querySelectorAll('[role=button][aria-label^=Abrir]')].map(x=>x.getAttribute('aria-label').split(' · ')[0].replace('Abrir ',''))])") or []
def quadro(): return sorted(J("[...document.querySelectorAll('[role=list][aria-label=\"Kanban das ordens\"] [role=button][aria-label^=Abrir]')].filter(x=>x.offsetParent).map(x=>x.getAttribute('aria-label').split(' · ')[0].replace('Abrir ',''))") or [])
def faixa(): return J("(()=>{const d=[...document.querySelectorAll('[data-os-recorte]')].find(x=>x.offsetParent); return d?d.innerText.replace(/\\s+/g,' ').trim():''})()") or ''
def tira(rx): J("(()=>{const b=[...document.querySelectorAll('[data-os-recorte] button')].filter(x=>x.offsetParent).find(x=>new RegExp(%s).test(x.getAttribute('aria-label')||'')); b.click();})()" % json.dumps(rx)); time.sleep(.6)
def visao(k): J("[...document.querySelectorAll('[data-visao]')].find(b=>b.getAttribute('data-visao')===%s).click()" % json.dumps(k)); time.sleep(.8)
def ids_tab(): return sorted(set(x.split('@')[0] for x in (J("[...document.querySelectorAll('[data-g2g=g_os] [data-rid]')].filter(e=>e.offsetParent).map(e=>e.getAttribute('data-rid'))") or []) if not x.startswith('grp@')))
try:
    c.aparelho(1440, 1000, 1, False); c.goto(B, .8); J("localStorage.clear();sessionStorage.clear()")
    abre('?view=lista'); todas = ids_tab()
    abre('?view=kanban&ag=onde'); rs = raias(); dist = sorted(set(i for _, xs in rs for i in xs))
    chk('F1 Kanban com Agrupar por Talhão: uma raia por talhão; OS-0421 nas raias T1 e T2; as O.S. distintas das raias = as da Tabela',
        len(rs) >= 3 and 'OS-0421' in dict(rs).get('T1', []) and 'OS-0421' in dict(rs).get('T2', []) and dist == todas, [rs, todas])
    J("[...document.querySelectorAll('.os-raia-cab')].find(b=>b.querySelector('b').innerText.trim()==='T2').click()"); time.sleep(.7)
    f = faixa()
    chk('F2 o nome da raia desce: trilha no endereço, um quadro só com as O.S. de T2 e a faixa "Talhão: … › T2 ×" acima do quadro',
        'trilha=' in J("location.search") and not raias() and quadro() == sorted(dict(rs)['T2']) and 'Talhão:' in f and '› T2' in f and 'Limpar filtros' in f, [J("location.search"), quadro(), f])
    visao('calendario'); cal = sorted(set(J("[...document.querySelectorAll('[role=button][aria-label^=Abrir],button[aria-label^=Abrir]')].filter(x=>x.offsetParent).map(x=>x.getAttribute('aria-label').split(' · ')[0].replace('Abrir ',''))") or []))
    chk('F3 Calendário lê o mesmo recorte da trilha (só O.S. de T2) e mostra a mesma faixa', set(cal) <= set(dict(rs)['T2']) and '› T2' in faixa(), [cal, faixa()])
    visao('carga')
    chk('F4 Carga mostra a mesma faixa do recorte', '› T2' in faixa() and 'Limpar filtros' in faixa(), faixa())
    visao('kanban'); tira('Tirar a trilha')
    chk('F5 o × do chip tira a trilha: as raias voltam e o endereço fica sem trilha', len(raias()) == len(rs) and 'trilha=' not in J("location.search"), [J("location.search"), len(raias())])
    # filtro de Talhão = T1 na coluna (Tabela) e Agrupar por Talhão: só o grupo T1, OS-0421 não reaparece em T2 (achado 2, com dado real)
    visao('lista')
    J("(()=>{const h=[...document.querySelectorAll('[data-g2g=g_os] [role=columnheader]')].find(x=>/^talhão/i.test(x.innerText.trim())); h.querySelector('.g2fb').click();})()"); time.sleep(.45)
    J("(()=>{const d=[...document.querySelectorAll('[role=dialog]')].find(x=>/Filtrar por valores/i.test(x.innerText)); [...d.querySelectorAll('button')].find(b=>b.innerText.trim()==='Limpar').click();})()"); time.sleep(.3)
    J("(()=>{const d=[...document.querySelectorAll('[role=dialog]')].find(x=>/Filtrar por valores/i.test(x.innerText)); const l=[...d.querySelectorAll('label')].find(x=>/^T1\\b/.test(x.innerText.trim())&&!/^T1-/.test(x.innerText.trim())); l.querySelector('input').click(); [...d.querySelectorAll('button')].find(b=>b.innerText.trim()==='OK').click();})()"); time.sleep(.6)
    grp = J("[...document.querySelectorAll('[data-g2g=g_os] [data-rid^=\"grp@\"]')].map(e=>e.getAttribute('data-rid'))") or []
    chk('F6 Tabela por Talhão com filtro Talhão = T1: só o grupo T1 (OS-0421 não leva o grupo T2 junto)', grp == ['grp@T1'], grp)
    visao('kanban'); rk = raias()
    chk('F7 Kanban com o mesmo filtro: só a raia T1, e a faixa traz o chip "Talhão: T1 ×"', [x for x, _ in rk] == ['T1'] and 'Talhão: T1' in faixa(), [rk, faixa()])
    tira('Remover filtro Talhão')
    chk('F8 o × do chip do filtro remove só esse filtro: as raias voltam e a faixa some', len(raias()) == len(rs) and faixa() == '', [len(raias()), faixa()])
    # recorte do Painel com trilha guardada: a trilha fica suspensa (não esconde O.S. do recorte) e volta ao sair
    J("[...document.querySelectorAll('.os-raia-cab')].find(b=>b.querySelector('b').innerText.trim()==='C1').click()"); time.sleep(.6)
    q_tr = J("location.search")
    c.goto(B + q_tr.replace('view=kanban', 'view=lista') + '#painel=OS-0418,OS-0420', 1.6)
    chk('F9 #painel=OS-0418,OS-0420 com a trilha C1 guardada: o recorte mostra as duas O.S., sem raia nem faixa de trilha', ids_tab() == ['OS-0418', 'OS-0420'] and '› C1' not in faixa(), [ids_tab(), faixa()])
    J("(()=>{const b=[...document.querySelectorAll('button')].find(x=>/Ver todas as O\\.S\\./.test(x.innerText)); if(b) b.click();})()"); time.sleep(.7)
    visao('kanban')
    chk('F10 "Ver todas as O.S." devolve a trilha guardada (C1)', '› C1' in faixa() and not raias(), [faixa(), raias()])
    c.aparelho(390, 844, 2, True); abre('?view=kanban&ag=onde')
    chk('F11 celular: raias sem rolagem lateral da página', len(raias()) >= 3 and J("document.documentElement.scrollWidth<=innerWidth"), J("[document.documentElement.scrollWidth,innerWidth]"))
    # Codex 6170116165: F11 mede só a página; V2-RAIAS-MOBILE-01 mede a coluna da raia e o que há dentro, V2-RAIAS-TOQUE-01 os alvos de toque
    med = J("[...document.querySelectorAll('.os-raia .os-kbcol')].filter(x=>x.offsetParent).map(c=>[c.clientWidth,c.scrollWidth])") or []
    chk('F11b celular: coluna da raia com 148 px e nada encoberto (o quadro rola dentro, a página não)', med and min(w for w, _ in med) >= 140 and all(sw <= w + 1 for w, sw in med) and J("document.documentElement.scrollWidth<=innerWidth"), med[:6])
    cab = J("[...document.querySelectorAll('.os-raia-cab')].filter(x=>x.offsetParent).map(b=>Math.round(b.getBoundingClientRect().height))") or []
    J("[...document.querySelectorAll('.os-raia-cab')].find(x=>x.offsetParent).click()"); time.sleep(.8)
    alv = J("[...document.querySelectorAll('[data-os-recorte] button')].filter(x=>x.offsetParent).map(b=>{const r=b.getBoundingClientRect(); return [b.getAttribute('aria-label')||b.innerText.trim(), Math.round(r.width), Math.round(r.height)];})") or []
    chk('F11c toque: nome da raia, × da trilha e "Limpar filtros" com 44 px', cab and min(cab) >= 44 and any(a[0].startswith('Tirar a trilha') for a in alv) and all(a[1] >= 44 and a[2] >= 44 for a in alv), [cab, alv])
    chk('F12 sem erro de JS', not J("(window.__e||[]).length"), J("window.__e"))
finally:
    c.close(); srv.terminate()
print(f'RESULTADO: {ok_n}/{ok_n + len(falhas)}' + (' · FALHAS: ' + '; '.join(falhas) if falhas else ''))
sys.exit(1 if falhas else 0)
