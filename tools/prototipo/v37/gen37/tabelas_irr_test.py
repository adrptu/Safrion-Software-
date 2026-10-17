# -*- coding: utf-8 -*-
"""Teste real (Chrome) — TABELAS-FOCO-20261004 v2 (5983172395), Irrigação (IR-01..IR-04 e IR-03det): uma variável por coluna.
TF03 por grade: colunas próprias (sem rótulo composto), unidade junto do valor nas colunas com data-un ("11,2 mm", "166 L/s"), filtro e
ordenação em todas as colunas (inclusive as passadas do detalhe), filtro pelo texto da célula e por item de lista (avisos, setores),
Início/Fim/Quando ordenados pelo instante (ontem < hoje < amanhã, que pelo texto sairia ao contrário), Situação/Etapa em chip; Fazenda
só com "Todas" no topo (Pivô 2 existe nas duas fazendas) com cada célula sob o seu cabeçalho; 390 px rolando dentro da caixa.
Fluxo no mesmo estado (irrigacao_estado.js), a 1440 e a 390 px: definir a janela da OS-0422 no detalhe → IR-03 mostra Início/Fim e ordena
por eles (normal); passada sem hora é recusada e nada muda (recusa); salvar de novo não duplica a ordem (repetição). A 390 px, com toque:
filtro e ordem pelo menu da coluna, filtro + busca sem resultado (aviso) e o mesmo filtro duas vezes.
Revisão TABR (09/10/2026): estado, pendência e próximo passo logo depois da identificação, à vista sem rolar a 1440 e a 1280 px, e as
grades IR-01..IR-03 cabem na caixa a 1440 px (A1); a linha do setor não mistura duas ordens: a próxima passada é da ordem da coluna Ordem e a
pendência de outra ordem diz qual é (A2); a Vazão do IR-02 não junta o pico da captação com a vazão do setor (A4); ordem encerrada sem selo
na Pendência (A6); passadas necessárias no painel (A7); estado salvo de versão antiga descartado (A9); o tipo da pendência no chip e o
detalhe na dica, responsável sem a função (A11); o Fim da ordem é o fim da última passada (mutante M-m); no IR-03det a Duração é a
da janela da linha (OS-0394: 2,1 h, não as 14,5 h previstas; pré-existente).
TABR-CTX-02 (revisão do TABR-CTX-01, 10/10/2026): a coluna Fazenda sai com a fazenda do topo e leva o filtro, a ordem e o menu de filtro
dela (antes ficava o chip "faz: Santa Rita", o filtro era ignorado e voltava com "Todas"); busca e outros filtros ficam. A 1440 e a 390 px,
por clique (toque) e pelo teclado (setas no seletor de fazenda; o foco fica nele).
Uso: python3 tabelas_irr_test.py [pasta de capturas]   (< 3 min)"""
import sys, os, re, time, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, servir, cv_todas_sempre
from tabelas_lib import Grade, limpa, num, un_ok, instante, crescente
OUT = sys.argv[1] if len(sys.argv) > 1 else None
if OUT: os.makedirs(OUT, exist_ok=True)
OK, FAIL = [], []
def chk(n, cond, info=''):
    (OK if cond else FAIL).append(n); print(('  ok  ' if cond else '  FALHOU ') + n + (' · ' + str(info)[:300] if info != '' else ''), flush=True)

p, srv = servir(os.path.join(HERE, '_render')); c = Chrome(); J = c.js; cv_todas_sempre(c)   # V2-3: a tabela completa como foi desenhada (TABELAS-FOCO); o padrão é conferido na VISOES-2
ERRS = []
def shot(n):
    if OUT: c.shot(os.path.join(OUT, n + '.png'))
def abre(pg, w=1.6):
    try: e = J("window.__errs") or []
    except Exception: e = []
    ERRS.extend(e); c.goto(f'http://127.0.0.1:{p}/{pg}', w)
def fazenda(f):
    J(f"""(()=>{{const i=[...document.querySelectorAll('select')].find(s=>[...s.options].some(o=>o.value==='Todas')); Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype,'value').set.call(i,{json.dumps(f)});
      i.dispatchEvent(new Event('change',{{bubbles:true}}));}})()"""); time.sleep(1)
def alinhada(g):
    """cada célula sob o seu cabeçalho (a trilha da grade acompanha a coluna Fazenda que entra e sai)."""
    return J(f"""(()=>{{const t=([...document.querySelectorAll('[role=table]')].filter(t=>t.offsetParent))[{g.i}]; const hs=[...t.querySelectorAll('[role=columnheader]')]; const hl=hs.map(h=>Math.round(h.getBoundingClientRect().left));
      return [...t.querySelectorAll('[role=row]')].filter(r=>r.querySelector('[role=cell]')).filter(r=>{{const cs=[...r.querySelectorAll('[role=cell]')]; return cs.length!==hs.length||cs.some((c,i)=>Math.abs(Math.round(c.getBoundingClientRect().left)-hl[i])>1);}}).length;}})()""")
def tf03(nome, g, esperado, chips=('Situação', 'Etapa', 'Estado'), extra=()):
    hs = g.heads(); ls = [h for h, _ in hs]
    chk(f'{nome}: colunas {" | ".join(esperado)}', ls == esperado, ls)
    chk(f'{nome}: nenhum rótulo composto (" · ", " / ")', not any(' · ' in h or ' / ' in h for h in ls), ls)
    m = g.com_menu(); chk(f'{nome}: filtro (▾) e ordenação no título em todas as {len(m)} colunas', m and all(m), m)
    d = g.dicts(); ruins = [(h, r.get(h)) for h, u in hs if u for r in d if not un_ok(r.get(h, ''), u, extra)]
    chk(f'{nome}: unidade junto do valor ({", ".join(h + " " + u for h, u in hs if u) or "nenhuma"})', not ruins, ruins[:4])
    for col in chips:
        if col in ls:
            ch = [x for x in g.chips(col) if x is not None]; chk(f'{nome}: {col} em chip ({len(ch)})', ch and all(ch), g.chips(col)[:6])
    return d
def por_grupo(g, col):
    g.abre_tudo()   # TAB-12 (17/10/2026): a árvore nasce recolhida; a pessoa abre tudo antes de comparar os grupos
    rows = J(f"[...([...document.querySelectorAll('[role=table]')].filter(t=>t.offsetParent))[{g.i}].querySelectorAll('[role=row]')].filter(r=>r.offsetParent&&r.querySelector('[role=cell]')).map(r=>[!!r.querySelector('button.g2car[aria-expanded]'),[...r.querySelectorAll('[role=cell]')].map(x=>x.innerText.replace(/\\s+/g,' ').replace(/^[▸▾]\\s*/,'').trim())])") or []
    k = g.labels().index(col); out = []; cur = None
    for grp, cells in rows:
        if grp: cur = []; out.append(cur)
        elif cur is not None: cur.append(cells[k])
    return out

def fchips():
    return J("[...document.querySelectorAll('button[aria-label=\"Remover filtro\"]')].filter(b=>b.offsetParent).map(b=>b.parentElement.innerText.replace(/\\s*×\\s*$/,'').trim())") or []
def conta():
    return J("([...document.querySelectorAll('main span')].filter(s=>s.offsetParent&&/^\\d+ de \\d+$/.test(s.innerText.trim())).map(s=>s.innerText.trim()))[0]||''") or ''
def ctx02(tam, tec):
    """TABR-CTX-02 no IR-01: "Todas" no topo, coluna Fazenda = Santa Rita (↓), Situação Impedida ou Programada e busca "Pivô" → Lagoa Grande no topo
    (a coluna sai) → "Todas".
    tec: a fazenda do topo muda pelo teclado (seta no seletor focado); senão, pelo valor do seletor."""
    m = f'TABR-CTX-02 {tam} ' + ('teclado' if tec else 'clique')
    SEL = "[...document.querySelectorAll('select')].find(s=>[...s.options].some(o=>o.value==='Todas'))"
    def topo(f, seta):
        if not tec: fazenda(f); return True
        J(f"{SEL}.focus()"); time.sleep(.1); c.tecla(seta, seta, 40 if seta == 'ArrowDown' else 38); time.sleep(1)
        return J(f"[{SEL}.value, document.activeElement==={SEL}]") == [f, True]
    def busca(t):
        J(f"""(()=>{{const i=[...document.querySelectorAll('input[aria-label="Buscar nesta tabela"]')].find(x=>x.offsetParent); Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(i,{json.dumps(t)});
          i.dispatchEvent(new Event('input',{{bubbles:true}})); i.dispatchEvent(new Event('change',{{bubbles:true}}));}})()"""); time.sleep(.4)
    bval = lambda: J("(([...document.querySelectorAll('input[aria-label=\"Buscar nesta tabela\"]')].find(x=>x.offsetParent))||{}).value") or ''
    abre('IR-01.dc.html'); fazenda('Todas'); limpa(J); g = Grade(J, 0)
    SIT = ('Impedida', 'Programada'); busca('Pivô'); prep = [g.filtra('Situação', list(SIT)), g.filtra('Fazenda', ['Santa Rita']), g.ordena('Fazenda', desc=True)]
    d0, c0 = g.dicts(), fchips(); cs = [x for x in c0 if x.startswith('Situação: ')]
    chk(f'{m} IR-01 Todas: busca "Pivô" + Situação Impedida ou Programada + Fazenda = Santa Rita (↓) → só setores da Santa Rita, com os dois chips',
        all(prep) and d0 and {r.get('Fazenda') for r in d0} == {'Santa Rita'} and len(cs) == 1 and sorted(c0) == ['Fazenda: Santa Rita'] + cs, (prep, [(r.get('Setor'), r.get('Fazenda')) for r in d0], c0))
    ok1 = topo('Lagoa Grande', 'ArrowDown'); d1, c1, l1, n1 = g.dicts(), fchips(), g.labels(), conta()
    chk(f'{m} IR-01 topo = Lagoa Grande: a coluna Fazenda sai com o filtro dela (sem chip "faz: Santa Rita"); a Situação e a busca ficam e a lista é da Lagoa Grande'
        + ('; o foco fica no seletor' if tec else ''),
        ok1 and c1 == cs and 'Fazenda' not in l1 and d1 and all(r.get('Situação') in SIT and 'Pivô' in r.get('Setor', '') for r in d1)
        and n1 == f'{len(d1)} de 23' and bval() == 'Pivô' and alinhada(g) == 0, (ok1, c1, l1[:3], n1, [r.get('Setor') for r in d1], bval()))
    ok2 = topo('Todas', 'ArrowUp'); d2, c2, l2, n2 = g.dicts(), fchips(), g.labels(), conta()
    chk(f'{m} IR-01 topo = Todas: a coluna Fazenda volta sem o filtro antigo (antes voltava "Fazenda: Santa Rita" e escondia a Lagoa Grande); Situação e busca ficam',
        ok2 and c2 == cs and l2[:3] == ['Setor', 'Fazenda', 'Situação'] and {r.get('Fazenda') for r in d2} == {'Santa Rita', 'Lagoa Grande'} and all(r.get('Situação') in SIT for r in d2)
        and n2 == f'{len(d2)} de 26' and bval() == 'Pivô' and alinhada(g) == 0, (ok2, c2, l2[:3], n2, sorted({r.get('Fazenda') for r in d2})))
    shot(f'ctx02-ir01-{tam.split()[0]}-{"teclado" if tec else "clique"}')
    busca(''); limpa(J); fazenda('Santa Rita')

def fluxo_janela(tam):
    """janela da OS-0422 no mesmo estado da irrigação: normal (salvar a sugerida), recusa (passada sem hora) e repetição (salvar de novo)."""
    abre('IR-03det.dc.html#OS-0422:janela', 1.8)
    dlg = lambda: J("(document.querySelector('aside[role=dialog]')||{innerText:''}).innerText.replace(/\\s+/g,' ')") or ''
    clk = lambda t: J(f"(()=>{{const b=[...document.querySelectorAll('aside[role=dialog] button')].find(b=>b.innerText.trim()==={json.dumps(t)}); if(!b) return false; b.click(); return true;}})()")
    toast = lambda: J("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).filter(Boolean).join(' | ')") or ''
    d0 = dlg(); clk('Usar janela sugerida'); time.sleep(.4); clk('Salvar janela'); time.sleep(.8); t = toast()
    abre('IR-03.dc.html'); g = Grade(J, 0); o22 = next((r for r in g.dicts() if r.get('Ordem') == 'OS-0422'), {})
    g.ordena('Início'); ini = g.col('Início'); ords = g.col('Ordem'); k22 = ords.index('OS-0422') if 'OS-0422' in ords else -1
    chk(f'fluxo {tam} (normal): janela sugerida salva no detalhe (libera pela prontidão) → IR-03 mostra Início e Fim da OS-0422 e ordena por eles',
        'Definir janela' in d0 and 'OS-0422' in t and ('Janela salva' in t or 'Liberadas' in t) and instante(o22.get('Início')) and instante(o22.get('Fim')) and crescente([instante(x) for x in ini if instante(x)]) and k22 >= 0 and instante(ini[k22]), (d0[:80], t, o22))
    ini22 = o22.get('Início')
    abre('IR-03det.dc.html#OS-0422', 1.6); fp = [instante(x) for x in Grade(J, 0).col('Fim') if instante(x)]
    chk(f'fluxo {tam} (M-m): o Fim da OS-0422 no IR-03 é o fim da última passada (2 passadas), não o da primeira', len(fp) == 2 and instante(o22.get('Fim')) == max(fp) and min(fp) < max(fp), (o22.get('Fim'), fp))
    abre('IR-03det.dc.html#OS-0422:janela', 1.8); pan = 'Definir janela' in dlg() or 'janela' in dlg().lower()
    J("""(()=>{const i=document.querySelector('#jn_h1'); if(!i) return; Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(i,''); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true}));})()"""); time.sleep(.3)
    clk('Salvar janela'); time.sleep(.6); t2 = toast()
    clk('Cancelar'); time.sleep(.3)
    abre('IR-03.dc.html'); o22b = next((r for r in Grade(J, 0).dicts() if r.get('Ordem') == 'OS-0422'), {})
    chk(f'fluxo {tam} (recusa): passada sem hora → "Informe data e hora da passada 1." e a janela gravada não muda', pan and 'Informe data e hora da passada 1' in t2 and o22b.get('Início') == ini22, (pan, t2, o22b.get('Início'), ini22))
    abre('IR-03det.dc.html#OS-0422:janela', 1.8); clk('Salvar janela'); time.sleep(.8)
    abre('IR-03.dc.html'); g = Grade(J, 0); n22 = g.col('Ordem').count('OS-0422'); o22c = next((r for r in g.dicts() if r.get('Ordem') == 'OS-0422'), {})
    chk(f'fluxo {tam} (repetição): salvar a mesma janela de novo não cria outra ordem nem muda o Início', n22 == 1 and o22c.get('Início') == ini22, (n22, o22c.get('Início')))

try:
    c.aparelho(1440, 900, 1, False)
    abre('Main.dc.html', .3); J("localStorage.clear(); sessionStorage.clear()")
    # ================= IR-01 =================
    abre('IR-01.dc.html'); g = Grade(J, 0)
    SET = ['Setor', 'Situação', 'Pendência', 'Próximo passo', 'Déficit hoje', 'Necessidade bruta', 'Ordem', 'Cobertura', 'Próxima passada']
    d = tf03('IR-01 Setores', g, SET, extra=('próximo ciclo',))
    p2 = next((r for r in d if r.get('Setor') == 'Pivô 2'), {}); t7 = next((r for r in d if r.get('Setor') == 'Gotejo T7'), {})
    # A2: a OS-0419 (Liberada, hoje 20:00) cobre o déficit; a divergência e o "Conferir medição" são da OS-0394, que a pendência nomeia; antes a
    # Próxima passada saía "—" (era da OS-0394) ao lado da OS-0419
    chk('IR-01 (A2): Pivô 2 = A conferir | Divergência na OS-0394 (−3,8 % na dica) | Conferir medição | 11,2 mm | 12,44 mm | OS-0419 | 87 % | hoje 20:00 (a próxima passada é da OS-0419, a ordem da linha)',
        [p2.get(k) for k in SET[1:]] == ['A conferir', 'Divergência na OS-0394 : −3,8 %', 'Conferir medição', '11,2 mm', '12,44 mm', 'OS-0419', '87 %', 'hoje 20:00'], p2)
    p1 = next((r for r in d if r.get('Setor') == 'Pivô 1'), {})
    chk('IR-01 (A11): a pendência tem o tipo no chip e o detalhe na dica (Pivô 1 Falta insumo · Ureia 45% · amanhã 21:00; Gotejo T7 Conflito · parada da B3 · hoje 14:00)',
        [p1.get(k) for k in ('Situação', 'Pendência', 'Próxima passada', 'Próximo passo')] == ['Impedida', 'Falta insumo : Ureia 45%', 'amanhã 21:00', 'Programar só água']
        and [t7.get(k) for k in ('Pendência', 'Próxima passada')] == ['Conflito : parada da B3 · 14:00–15:00', 'hoje 14:00'] and t7.get('Déficit hoje') == '≈10,0 mm', (p1, t7))
    vis = J("""(()=>{const t=([...document.querySelectorAll('[role=table]')].filter(t=>t.offsetParent))[0]; const c=[...t.querySelectorAll('[role=row]')].find(r=>r.innerText.indexOf('Pivô 1')===0).querySelectorAll('[role=cell]')[2];
      const ch=c.querySelector('span[data-dica]'); return [ch.getAttribute('data-dica'), ch.getBoundingClientRect().width<200, [...ch.querySelectorAll('.g2sr')].length, ch.hasAttribute('title')];})()""") or []
    # integração V56 (DS-DICA): a dica do chip é a do design system (data-dica, g2dica: ponteiro, foco e toque), sem a dica nativa (title) por cima
    chk('IR-01 (A11): o chip mostra só "Falta insumo"; "Ureia 45%" fica na dica (data-dica do design system, sem title) e no texto do leitor de tela', vis[:1] == ['Ureia 45%'] and vis[2] == 1 and vis[3] is False, vis)
    qf = J("[...document.querySelectorAll('[role=group][aria-label^=\"Filtro rápido\"] button')].map(b=>b.innerText.replace(/\\s+\\d+$/,'').trim())") or []
    chk('IR-01: o filtro rápido de Situação tem os mesmos textos dos chips da coluna', set(x for x in qf if x != 'Todos') == {r.get('Situação') for r in d}, (qf, [r.get('Situação') for r in d]))
    rp = g.rotulos('Pendência'); g.filtra('Pendência', ['Falta insumo']); fl = [r.get('Setor') for r in g.dicts()]
    chk('IR-01: o filtro da Pendência oferece o tipo (Falta insumo, Conflito…) e filtra por ele → Pivô 1', 'Falta insumo' in (rp or []) and 'Conflito' in (rp or []) and fl == ['Pivô 1'], (rp, fl))
    limpa(J); g.ordena('Déficit hoje', desc=True); df = [num(x) for x in g.col('Déficit hoje')]
    chk('IR-01: ordenar Déficit hoje (decrescente) pelo número (o ≈ não atrapalha)', crescente(df, True), g.col('Déficit hoje'))
    limpa(J); g.ordena('Próxima passada'); pp = [r.get('Setor') for r in g.dicts() if r.get('Próxima passada') not in ('', '—')]
    chk('IR-01: ordenar Próxima passada pelo instante (hoje 14:00 < hoje 20:00 < amanhã 21:00)', pp[:3] == ['Gotejo T7', 'Pivô 2', 'Pivô 1'], g.col('Próxima passada'))
    limpa(J)
    # painel do setor: o que saiu da grade (fonte do déficit, cultura e estádio, passadas necessárias, o que resta e o responsável)
    J("(()=>{const r=[...document.querySelectorAll('[role=row].g2ed')].find(x=>x.innerText.indexOf('Pivô 2')===0); r&&r.querySelector('[role=cell] span').click();})()"); time.sleep(.5)
    pn = J("(document.querySelector('aside[role=dialog]')||{innerText:''}).innerText.replace(/\\s+/g,' ')") or ''
    fv = lambda k: J(f"(document.querySelector('#fx_g_set_{k}')||{{}}).value") or ''
    chk('IR-01 painel (A1, A7): Pivô 2 com fonte do déficit, 2 passadas necessárias, OS-0419 cobre 87 % · resta 1,5 mm, responsável João e Milho · V10',
        'estação Santa Rita' in fv('defT') and '2 passadas necessárias' in fv('necT') and 'programação 13,4 mm' in fv('necT') and 'bruta 12,44 mm' in fv('necT') and fv('ordT') == 'OS-0419 · cobre 87 % · resta 1,5 mm' and fv('donoT') == 'João' and fv('cultT') == 'Milho · V10', [fv(k) for k in ('defT', 'necT', 'ordT', 'donoT', 'cultT')])
    J("(()=>{const b=[...document.querySelectorAll('aside[role=dialog] button')].find(b=>b.innerText.trim()==='Cancelar'); b&&b.click();})()"); time.sleep(.3)
    fazenda('Todas'); g = Grade(J, 0); hs = g.labels(); d = g.dicts()
    pv2 = sorted(r.get('Fazenda') for r in d if r.get('Setor') == 'Pivô 2')
    chk('IR-01 Todas: a coluna Fazenda entra (Pivô 2 da Santa Rita e da Lagoa Grande se distinguem) e cada célula fica sob o seu cabeçalho',
        hs[:3] == ['Setor', 'Fazenda', 'Situação'] and pv2 == ['Lagoa Grande', 'Santa Rita'] and alinhada(g) == 0, (hs[:3], pv2, alinhada(g)))
    p5 = next((r for r in d if r.get('Setor') == 'Pivô 5' and r.get('Fazenda') == 'Lagoa Grande'), {})
    rep = [(r.get('Setor'), r.get('Situação'), r.get('Pendência')) for r in d if r.get('Situação') and r.get('Pendência', '').startswith(r.get('Situação'))]
    chk('IR-01 Todas: a Pendência diz o que segura sem repetir a Situação (Pivô 5 Impedida | Bomba parada; antes "Impedida · bomba parada")',
        p5.get('Situação') == 'Impedida' and p5.get('Pendência') == 'Bomba parada' and not rep, (p5.get('Situação'), p5.get('Pendência'), rep[:3]))
    J("(()=>{const r=[...document.querySelectorAll('[role=row].g2ed')].find(x=>x.innerText.indexOf('Pivô 9')===0); r&&r.querySelector('[role=cell] span').click();})()"); time.sleep(.5)
    cl = J("(document.querySelector('#fx_g_set_cultT')||{}).value") or ''
    chk('IR-01 Todas: Lagoa Grande com a cultura e a fase do mamão no painel do setor (Mamão · produção)', cl == 'Mamão · produção', cl)
    J("(()=>{const b=[...document.querySelectorAll('aside[role=dialog] button')].find(b=>b.innerText.trim()==='Cancelar'); b&&b.click();})()"); time.sleep(.3)
    fazenda('Santa Rita'); g = Grade(J, 0)
    chk('IR-01 Santa Rita: a coluna Fazenda sai e a grade continua alinhada', g.labels() == SET and alinhada(g) == 0, g.labels()[:3])
    shot('ir01-1440')
    ctx02('1440', False); ctx02('1440', True)
    # ================= IR-02 =================
    abre('IR-02.dc.html'); g = Grade(J, 0)
    AG = ['Captação › ordem', 'Etapa', 'Pendência', 'Próximo passo', 'Setor', 'Início', 'Fim', 'Lâmina', 'Avisos']
    d = tf03('IR-02 Agenda', g, AG, extra=())
    rio = next((r for r in d if r.get('Captação › ordem', '').startswith('Rio')), {}); o19 = next((r for r in d if r.get('Captação › ordem') == 'OS-0419'), {})
    chk('IR-02 (A4): sem coluna de Vazão que juntava o pico da captação (166) e a vazão do setor; o pico de hoje é aviso da captação (166 de 400 L/s)',
        'Vazão' not in g.labels() and rio.get('Avisos') == 'Pico hoje 166 de 400 L/s', rio)
    chk('IR-02: OS-0419 Liberadas | — | Iniciar irrigação | Pivô 2 | hoje 20:00 | amanhã 10:31 | 10,81 mm | Ponta parcial (20–21 h)',
        [o19.get(k) for k in AG[1:]] == ['Liberadas', '—', 'Iniciar irrigação', 'Pivô 2', 'hoje 20:00', 'amanhã 10:31', '10,81 mm', 'Ponta parcial (20–21 h)'], o19)
    rr = g.rotulos('Avisos'); g.filtra('Avisos', ['Ponta parcial (20–21 h)']); fl = [r.get('Captação › ordem') for r in g.dicts(True)]
    chk('IR-02: filtro Avisos por item (Ponta parcial) → OS-0419', 'Ponta parcial (20–21 h)' in (rr or []) and fl == ['OS-0419'], (rr, fl))
    limpa(J); g.ordena('Início'); bl = por_grupo(g, 'Início')
    ok_ = all(crescente([instante(x) for x in b]) or len([x for x in b if instante(x)]) < 2 for b in bl) and any(len([x for x in b if instante(x)]) > 1 for b in bl)
    chk('IR-02: ordenar Início pelo instante dentro da captação; "a definir" no fim', ok_ and all(b.index('a definir') == len(b) - 1 for b in bl if 'a definir' in b), bl)
    limpa(J); fazenda('Lagoa Grande'); g = Grade(J, 0); d = g.dicts()
    # integração V56 (CTL-5): a outorga do Rio A vem do cadastro (aba Água do CD-01) e está "Vence em 90 dias" (antes, cópia "Em renovação");
    # o aviso da outorga continua uma vez só, na linha da captação, com qual outorga vence e quanto sai
    ra = next((r for r in d if r.get('Captação › ordem', '').startswith('Rio A')), {}); ren = [r.get('Captação › ordem') for r in d if 'Outorga vence em 90 dias' in r.get('Avisos', '')]
    chk('IR-02 Lagoa Grande: o aviso da outorga ("Outorga vence em 90 dias · SINT-002/0000 vence em 20/11/2026 (42 de 186 L/s)") uma vez, na linha da captação (antes repetido em cada ordem do Rio A)',
        ren == [ra.get('Captação › ordem')] and ra and 'SINT-002/0000 vence em 20/11/2026 (42 de 186 L/s)' in ra.get('Avisos', ''), (ren, ra))
    fazenda('Santa Rita')
    # ================= IR-03 =================
    abre('IR-03.dc.html'); g = Grade(J, 0)
    OSC = ['Ordem', 'Etapa', 'Pendência', 'Próximo passo', 'Responsável', 'Tipo', 'Setor', 'Início', 'Fim', 'Lâmina']
    d = tf03('IR-03 Ordens', g, OSC)
    o94 = next((r for r in d if r.get('Ordem') == 'OS-0394'), {}); o92 = next((r for r in d if r.get('Ordem') == 'OS-0392'), {}); o23 = next((r for r in d if r.get('Ordem') == 'OS-0423'), {})
    chk('IR-03: OS-0394 Em conferência | Divergência (−3,8 % na dica) | Conferir medição | João | Água | Pivô 2 | ontem 20:00 | ontem 22:06 | 10,81 mm',
        [o94.get(k) for k in OSC[1:]] == ['Em conferência', 'Divergência : −3,8 %', 'Conferir medição', 'João', 'Água', 'Pivô 2', 'ontem 20:00', 'ontem 22:06', '10,81 mm'], o94)
    chk('IR-03 (A6): a OS-0392 encerrada não tem pendência (o "Encerrada automaticamente" fica no detalhe)', o92.get('Etapa') == 'Encerradas' and o92.get('Pendência') == '—', o92)
    chk('IR-03 (A11): Responsável só com a pessoa (OS-0423 Caio; antes "Caio · PCP")', o23.get('Responsável') == 'Caio', o23)
    etapas = {r.get('Etapa') for r in d}
    chk('IR-03: Etapa só com as fases da O.S. (A liberar, Liberadas, Em execução, Em conferência, Encerradas)', etapas <= {'A liberar', 'Liberadas', 'Em execução', 'Em conferência', 'Encerradas'}, etapas)
    g.ordena('Início'); ini = g.col('Início'); ks = [instante(x) for x in ini if instante(x)]
    chk('IR-03: ordenar Início pelo instante (19/09 < ontem < hoje < amanhã; pelo texto "amanhã" viria antes de "hoje"); "a definir" no fim',
        crescente(ks) and ini[-1] == 'a definir' and ini.index('ontem 20:00') < ini.index('hoje 14:00') < ini.index('amanhã 21:00'), ini)
    g.ordena('Início', desc=True); ini2 = [instante(x) for x in g.col('Início') if instante(x)]
    chk('IR-03: ordenar Início decrescente pelo instante', crescente(ini2, True), g.col('Início'))
    g.filtra('Tipo', ['Fertirrigação']); fl = [r.get('Ordem') for r in g.dicts()]
    chk('IR-03: filtro Tipo = Fertirrigação (Água ou Fertirrigação, uma variável) → OS-0418', fl == ['OS-0418'], fl)
    limpa(J)
    fazenda('Todas'); g = Grade(J, 0); d = g.dicts()
    o507 = next((r for r in d if r.get('Ordem') == 'OS-0507'), {}); rep = [(r.get('Ordem'), r.get('Pendência')) for r in d if r.get('Pendência', '').startswith('Impedida')]
    chk('IR-03 Todas: OS-0507 Fertirrigação com Pendência "Bomba parada" (sem "Impedida ·"); Tipo só Água ou Fertirrigação',
        o507.get('Tipo') == 'Fertirrigação' and o507.get('Pendência') == 'Bomba parada' and not rep and {r.get('Tipo') for r in d} == {'Água', 'Fertirrigação'}, (o507, rep))
    chk('IR-03 Todas: coluna Fazenda (2ª) com Santa Rita e Lagoa Grande; células alinhadas', g.labels()[:3] == ['Ordem', 'Fazenda', 'Etapa'] and {r.get('Fazenda') for r in d} == {'Santa Rita', 'Lagoa Grande'} and alinhada(g) == 0, (g.labels()[:4], alinhada(g)))
    fazenda('Santa Rita'); shot('ir03-1440')
    # ================= IR-03det =================
    abre('IR-03det.dc.html#OS-0419'); gp, gt = Grade(J, 0), Grade(J, 1)
    dp = tf03('IR-03det Passadas', gp, ['Passada', 'Início', 'Fim', 'Lâmina', 'Duração', 'Estado', 'Área coberta', 'Volume medido'])
    chk('IR-03det: 1ª | hoje 20:00 | amanhã 10:31 | 10,81 mm | 14,5 h | Programada | — | —',
        dp and [dp[0].get(k) for k in ('Passada', 'Início', 'Fim', 'Lâmina', 'Duração', 'Estado', 'Área coberta', 'Volume medido')] == ['1ª', 'hoje 20:00', 'amanhã 10:31', '10,81 mm', '14,5 h', 'Programada', '—', '—'], dp)
    dt = tf03('IR-03det Trilha', gt, ['Quando', 'Recibo', 'Evento', 'Quem'])
    gt.ordena('Quando', desc=True); qd = [instante(x) for x in gt.col('Quando')]
    chk('IR-03det: ordenar Quando pelo instante', all(qd) and qd == sorted(qd, reverse=True), gt.col('Quando'))
    # pré-existente (revisão TABR): a Duração é a da janela da linha; a OS-0394 rodou ontem 20:00–22:06 → 2,1 h (antes 14,5 h previstas ao lado do horário real)
    abre('IR-03det.dc.html#OS-0394'); d94 = Grade(J, 0).dicts()
    chk('IR-03det OS-0394: Início ontem 20:00 | Fim ontem 22:06 | Duração 2,1 h (a duração da mesma janela, não a prevista)',
        d94 and [d94[0].get(k) for k in ('Início', 'Fim', 'Duração')] == ['ontem 20:00', 'ontem 22:06', '2,1 h'], d94[:1])
    # ================= IR-04 =================
    abre('IR-04.dc.html'); gs, gc, gd = Grade(J, 0), Grade(J, 1), Grade(J, 2)
    ds = tf03('IR-04 Fontes', gs, ['Fonte', 'Estado', 'Grandeza', 'Unidade', 'Atualização', 'Calibração', 'Validade da calibração', 'Cobertura', 'Efeito no balanço'], chips=('Estado',))
    hp = next((r for r in ds if r.get('Fonte') == 'Hidrômetro · Pivô 2'), {}); s1 = next((r for r in ds if r.get('Fonte', '').startswith('Sonda de umidade · P1')), {})
    chk('IR-04: hidrômetro Volume | m³ | hoje 06:00 | Vence em 7 dias | 30/09/2026; sonda P1 Suspeita (o motivo vai para o painel)',
        [hp.get(k) for k in ('Grandeza', 'Unidade', 'Atualização', 'Calibração', 'Validade da calibração')] == ['Volume', 'm³', 'hoje 06:00', 'Vence em 7 dias', '30/09/2026'] and s1.get('Estado') == 'Suspeita', (hp, s1))
    gs.ordena('Atualização'); at = gs.col('Atualização')
    chk('IR-04: ordenar Atualização pelo instante (20/09 antes de hoje)', at and at[0] == '20/09 06:00' and crescente([instante(x) for x in at]), at)
    J("(()=>{const r=[...document.querySelectorAll('[role=row].g2ed')].find(x=>x.innerText.indexOf('Sonda de umidade · P1')===0); r&&r.querySelector('[role=cell] span').click();})()"); time.sleep(.5)
    sub = J("(document.querySelector('aside[role=dialog]')||{innerText:''}).innerText.replace(/\\s+/g,' ')") or ''
    chk('IR-04: o painel da sonda P1 diz o motivo da suspeita (salto de 18 p.p.)', 'Suspeita · salto de 18 p.p.' in sub, sub[:200])
    J("(()=>{const b=[...document.querySelectorAll('aside[role=dialog] button')].find(b=>b.innerText.trim()==='Cancelar'); b&&b.click();})()"); time.sleep(.3)
    es = next((r for r in ds if r.get('Fonte', '').startswith('Estação meteorológica')), {})
    chk('IR-04: a estação lista grandezas e unidades na mesma ordem (ET₀, Chuva, Vento | mm/dia, mm, km/h; antes "ET₀ / chuva / vento" e "mm/dia · mm" sem a do vento); o hidrômetro credita as irrigações (a Cobertura diz onde)',
        [es.get('Grandeza'), es.get('Unidade')] == ['ET₀, Chuva, Vento', 'mm/dia, mm, km/h'] and hp.get('Efeito no balanço') == 'crédito das irrigações', (es.get('Grandeza'), es.get('Unidade'), hp.get('Efeito no balanço')))
    rg = gs.rotulos('Grandeza'); gs.filtra('Grandeza', ['Chuva']); fl = [r.get('Fonte') for r in gs.dicts()]
    chk('IR-04: filtro Grandeza por item (Chuva) → só a estação', 'Chuva' in (rg or []) and fl == ['Estação meteorológica Santa Rita'], (rg, fl))
    limpa(J)
    # cadastrar sensor: a unidade vem da grandeza (o formulário não pede; não diverge dela)
    J("(()=>{const b=[...document.querySelectorAll('button')].find(b=>b.offsetParent&&b.innerText.trim().replace(/^\\+\\s*/,'')==='Cadastrar sensor'); b&&b.click();})()"); time.sleep(.5)
    labs = J("[...document.querySelectorAll('aside[role=dialog] label[for]')].map(l=>l.innerText.trim())") or []
    for sel, val in (('#fx_g_src_nome', 'Hidrômetro · Pivô 1'), ('#fx_g_src_gr', 'Volume'), ('#fx_g_src_cob', 'Pivô 1')):
        J(f"""(()=>{{const i=document.querySelector({json.dumps(sel)}); if(!i) return; const P=i.tagName==='SELECT'?HTMLSelectElement.prototype:HTMLInputElement.prototype;
          Object.getOwnPropertyDescriptor(P,'value').set.call(i,{json.dumps(val)}); i.dispatchEvent(new Event('input',{{bubbles:true}})); i.dispatchEvent(new Event('change',{{bubbles:true}}));}})()"""); time.sleep(.2)
    J("(()=>{const b=[...document.querySelectorAll('aside[role=dialog] button')].find(b=>b.innerText.trim()==='Salvar'); b&&b.click();})()"); time.sleep(.8)
    hn = next((r for r in Grade(J, 0).dicts() if r.get('Fonte') == 'Hidrômetro · Pivô 1'), {})
    chk('IR-04 cadastrar sensor: o formulário não pede a unidade (vem da grandeza); hidrômetro novo = Volume | m³ | Aguardando 1ª leitura',
        'Grandeza' in labs and 'Unidade' not in labs and [hn.get(k) for k in ('Grandeza', 'Unidade', 'Estado')] == ['Volume', 'm³', 'Aguardando 1ª leitura'], (labs, hn))
    dc = tf03('IR-04 Captações', gc, ['Captação', 'Situação', 'Outorga', 'Vazão outorgada', 'Regime', 'Vencimento', 'Volume hoje', 'Uso do dia', 'Setores ligados'])
    rio = next((r for r in dc if r.get('Captação', '').startswith('Rio')), {})
    chk('IR-04: Rio demonstrativa | 400 L/s | 21 h/dia | 30/06/2028 | Vigente | 2.390 m³ | 8 % | Pivô 2, Pivô 1',
        [rio.get(k) for k in ('Outorga', 'Vazão outorgada', 'Regime', 'Vencimento', 'Situação', 'Volume hoje', 'Uso do dia', 'Setores ligados')] == ['demonstrativa', '400 L/s', '21 h/dia', '30/06/2028', 'Vigente', '2.390 m³', '8 %', 'Pivô 2, Pivô 1'], rio)
    gc.filtra('Setores ligados', ['Gotejo T7']); fl = [r.get('Captação') for r in gc.dicts()]
    chk('IR-04: filtro Setores ligados por item (Gotejo T7) → Reservatório da sede', fl == ['Reservatório da sede'], fl)
    limpa(J)
    dd = tf03('IR-04 Desempenho', gd, ['Setor', 'Cultura', 'Volume', 'Energia', 'Lâmina aplicada', 'Eficiência', 'Variação da eficiência'])
    p2 = next((r for r in dd if r.get('Setor') == 'Pivô 2'), {})
    chk('IR-04: Pivô 2 Milho | 32.480 m³ | 23.370 kWh | 40,6 mm | 1,39 m³/kWh | +4 %', [p2.get(k) for k in ('Cultura', 'Volume', 'Energia', 'Lâmina aplicada', 'Eficiência', 'Variação da eficiência')] == ['Milho', '32.480 m³', '23.370 kWh', '40,6 mm', '1,39 m³/kWh', '+4 %'], p2)
    fazenda('Todas'); gs, gc = Grade(J, 0), Grade(J, 1)
    chk('IR-04 Todas: Fazenda nas fontes e nas captações, com as células alinhadas', gs.labels()[1] == 'Fazenda' and gc.labels()[1] == 'Fazenda' and alinhada(gs) == 0 and alinhada(gc) == 0, (gs.labels()[:3], gc.labels()[:3]))
    fazenda('Santa Rita'); shot('ir04-1440')
    # ================= fluxo no mesmo estado: janela da OS-0422 =================
    fluxo_janela('1440')
    # A9: estado salvo com a semente anterior (v=2: a estação com "mm/dia · mm", sem o vento) é descartado; a mesma versão seria aceita
    J("""(()=>{const k='talhao-os-irrigacao-v1'; const o=JSON.parse(localStorage.getItem(k)); const f=Object.values(o.fontes).find(x=>x.nome.indexOf('Estação')===0); f.un='mm/dia · mm'; o.v=2; localStorage.setItem(k,JSON.stringify(o));})()""")
    abre('IR-04.dc.html'); es = next((r for r in Grade(J, 0).dicts() if r.get('Fonte', '').startswith('Estação meteorológica')), {})
    chk('IR-04 (A9): estado salvo de versão anterior (v=2, estação "mm/dia · mm") é descartado: a estação volta a mm/dia, mm, km/h', es.get('Unidade') == 'mm/dia, mm, km/h', es)
    # A1: estado, pendência e próximo passo à vista sem rolar a grade (1440 e 1280 px, fazenda única e "Todas"); a 1440 px IR-01..IR-03 cabem na caixa
    MED = """(()=>[...document.querySelectorAll('.g2rola')].filter(r=>r.offsetParent).map(r=>{const R=r.getBoundingClientRect(); const hs=[...r.querySelectorAll('[role=table]>[role=row] [role=columnheader]')];
      const lab=h=>h.textContent.replace(/[⇅▾▴▼▲]/g,'').replace(/\\s+/g,' ').trim(); return {sobra:r.scrollWidth-r.clientWidth, fora:hs.filter(h=>h.getBoundingClientRect().right>R.right+1).map(lab)};}))()"""
    CHAVE = {'Situação', 'Etapa', 'Estado', 'Pendência', 'Próximo passo'}; larg = []
    for w in (1440, 1280):
        c.aparelho(w, 900, 1, False)
        for fz in ('Santa Rita', 'Todas'):
            for pg in ('IR-01.dc.html', 'IR-02.dc.html', 'IR-03.dc.html', 'IR-04.dc.html'):
                abre(pg, 1.3); fazenda(fz)
                for i, m in enumerate(J(MED) or []):
                    ruim = sorted(CHAVE & set(m['fora'])) + (['rola %d px' % m['sobra']] if (w == 1440 and fz == 'Santa Rita' and pg[:5] in ('IR-01', 'IR-02', 'IR-03') and m['sobra'] > 1) else [])
                    if ruim: larg.append((w, fz, pg.split('.')[0], i, ruim))
        fazenda('Santa Rita')
    chk('IR (A1): Situação/Etapa/Estado, Pendência e Próximo passo à vista sem rolar a 1440 e 1280 px (Santa Rita e Todas); IR-01, IR-02 e IR-03 cabem na caixa a 1440 px', not larg, larg)
    c.aparelho(1440, 900, 1, False)
    ERRS.extend(J("window.__errs") or []); chk('sem erro de script (1440)', not ERRS, ERRS[:3])
    # ================= 390 px =================
    c.aparelho(390, 844, 2, True); J("localStorage.removeItem('talhao-os-irrigacao-v1')"); r390 = []
    for pg in ('IR-01.dc.html', 'IR-02.dc.html', 'IR-03.dc.html', 'IR-03det.dc.html#OS-0419', 'IR-04.dc.html'):
        abre(pg)
        n = J("[...document.querySelectorAll('[role=table]')].filter(t=>t.offsetParent).length") or 0
        for i in range(n):
            q = Grade(J, i).rola_dentro(); r390.append((pg.split('.')[0] + f' #{i}', q.get('pagina'), q.get('cabe') or q.get('rola'), q.get('c0'), q.get('rola')))
        if pg.startswith('IR-03.'): shot('ir03-390')
    ruim = [x for x in r390 if not (x[1] and x[2] and x[3])]
    chk(f'390 px: {len(r390)} grades sem rolagem lateral da página; cada grade cabe ou rola dentro da caixa, com a 1ª coluna à vista', r390 and not ruim, ruim or r390[:3])
    chk('390 px: as grades largas rolam dentro da caixa', sum(1 for x in r390 if x[4]) >= len(r390) - 2, [x[0] for x in r390 if not x[4]])
    fluxo_janela('390 px')
    ctx02('390 px', False); ctx02('390 px', True)
    abre('IR-03.dc.html'); g = Grade(J, 0); n0 = len(g.dicts())
    g.filtra('Etapa', ['A liberar']); a1 = [r.get('Ordem') for r in g.dicts()]; g.ordena('Início'); ini = [instante(x) for x in g.col('Início') if instante(x)]
    chk('390 px (normal): filtro Etapa = A liberar pelo menu da coluna e ordem por Início (instante), com toque', a1 and all(r.get('Etapa') == 'A liberar' for r in g.dicts()) and crescente(ini), (a1, g.col('Início')))
    J("""(()=>{const i=[...document.querySelectorAll('input[aria-label="Buscar nesta tabela"]')].find(x=>x.offsetParent); if(!i) return; Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(i,'Pivô 9');
      i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true}));})()"""); time.sleep(.5)
    vaz = J("[...document.querySelectorAll('main div')].some(x=>x.offsetParent&&/^Nenhuma linha corresponde aos filtros/.test(x.innerText.trim()))")
    chk('390 px (recusa): Etapa = A liberar + busca "Pivô 9" (setor da Lagoa Grande) → nenhuma linha e o aviso "Nenhuma linha corresponde aos filtros"', g.dicts() == [] and vaz, len(g.dicts()))
    limpa(J); g.filtra('Etapa', ['A liberar']); b1 = [r.get('Ordem') for r in g.dicts()]; g.filtra('Etapa', ['A liberar']); b2 = [r.get('Ordem') for r in g.dicts()]; limpa(J)
    chk('390 px (repetição): o mesmo filtro duas vezes dá o mesmo recorte; Limpar filtros volta a todas', b1 == b2 and sorted(b1) == sorted(a1) and len(g.dicts()) == n0, (b1, b2, n0))
    ERRS.extend(J("window.__errs") or []); chk('sem erro de script (390)', not ERRS, ERRS[:3])
finally:
    c.close(); srv.terminate()
print(f'RESULTADO: {len(OK)}/{len(OK) + len(FAIL)} ok' + (' · FALHAS: ' + '; '.join(FAIL) if FAIL else ''))
sys.exit(1 if FAIL else 0)

