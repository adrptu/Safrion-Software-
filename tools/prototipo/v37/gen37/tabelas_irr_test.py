# -*- coding: utf-8 -*-
"""Teste real (Chrome) — TABELAS-FOCO-20261004 v2 (5983172395), Irrigação (IR-01..IR-04 e IR-03det): uma variável por coluna.
TF03 por grade: colunas próprias (sem rótulo composto), unidade junto do valor nas colunas com data-un ("11,2 mm", "166 L/s"), filtro e
ordenação em todas as colunas (inclusive as passadas do detalhe), filtro pelo texto da célula e por item de lista (avisos, setores),
Início/Fim/Quando ordenados pelo instante (ontem < hoje < amanhã, que pelo texto sairia ao contrário), Situação/Etapa em chip; Fazenda
só com "Todas" no topo (Pivô 2 existe nas duas fazendas) com cada célula sob o seu cabeçalho; 390 px rolando dentro da caixa.
Fluxo no mesmo estado (irrigacao_estado.js): definir a janela da OS-0422 no detalhe → IR-03 mostra Início/Fim e ordena por eles (normal);
passada sem hora é recusada e nada muda (recusa); salvar de novo não duplica a ordem (repetição).
Uso: python3 tabelas_irr_test.py [pasta de capturas]   (< 3 min)"""
import sys, os, re, time, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, servir
from tabelas_lib import Grade, limpa, num, un_ok, instante, crescente
OUT = sys.argv[1] if len(sys.argv) > 1 else None
if OUT: os.makedirs(OUT, exist_ok=True)
OK, FAIL = [], []
def chk(n, cond, info=''):
    (OK if cond else FAIL).append(n); print(('  ok  ' if cond else '  FALHOU ') + n + (' · ' + str(info)[:300] if info != '' else ''), flush=True)

p, srv = servir(os.path.join(HERE, '_render')); c = Chrome(); J = c.js
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
    rows = J(f"[...([...document.querySelectorAll('[role=table]')].filter(t=>t.offsetParent))[{g.i}].querySelectorAll('[role=row]')].filter(r=>r.offsetParent&&r.querySelector('[role=cell]')).map(r=>[!!r.querySelector('button[aria-label^=\"Expandir\"],button[aria-label^=\"Recolher\"]'),[...r.querySelectorAll('[role=cell]')].map(x=>x.innerText.replace(/\\s+/g,' ').replace(/^[▸▾]\\s*/,'').trim())])") or []
    k = g.labels().index(col); out = []; cur = None
    for grp, cells in rows:
        if grp: cur = []; out.append(cur)
        elif cur is not None: cur.append(cells[k])
    return out

try:
    c.aparelho(1440, 900, 1, False)
    abre('Main.dc.html', .3); J("localStorage.clear(); sessionStorage.clear()")
    # ================= IR-01 =================
    abre('IR-01.dc.html'); g = Grade(J, 0)
    SET = ['Setor', 'Cultura', 'Estádio', 'Área', 'Déficit hoje', 'Fonte do déficit', 'Necessidade bruta', 'Passadas', 'Ordem', 'Cobertura', 'Resta', 'Situação', 'Pendência', 'Próxima passada', 'Próximo passo', 'Responsável']
    d = tf03('IR-01 Setores', g, SET, extra=('próximo ciclo',))
    p2 = next((r for r in d if r.get('Setor') == 'Pivô 2'), {}); t7 = next((r for r in d if r.get('Setor') == 'Gotejo T7'), {})
    chk('IR-01: Pivô 2 = Milho | V10 | 80 ha | 11,2 mm | Medido | 12,44 mm | 2 | OS-0419 | 87 % | 1,5 mm | A conferir | Divergência · −3,8 % | — | Conferir medição | João',
        [p2.get(k) for k in SET[1:]] == ['Milho', 'V10', '80 ha', '11,2 mm', 'Medido', '12,44 mm', '2', 'OS-0419', '87 %', '1,5 mm', 'A conferir', 'Divergência · −3,8 %', '—', 'Conferir medição', 'João'], p2)
    p1 = next((r for r in d if r.get('Setor') == 'Pivô 1'), {})
    chk('IR-01: a pendência explica a situação e a próxima passada tem coluna própria (Pivô 1 Impedida · Falta insumo · Ureia 45% · amanhã 21:00; Gotejo T7 Conflito · parada da B3 · hoje 14:00)',
        [p1.get(k) for k in ('Situação', 'Pendência', 'Próxima passada', 'Próximo passo')] == ['Impedida', 'Falta insumo · Ureia 45%', 'amanhã 21:00', 'Programar só água']
        and [t7.get(k) for k in ('Pendência', 'Próxima passada')] == ['Conflito · parada da B3', 'hoje 14:00'], (p1, t7))
    chk('IR-01: déficit estimado com ≈ e a fonte em coluna própria (Gotejo T7 ≈10,0 mm · Estimativa por ET)', t7.get('Déficit hoje') == '≈10,0 mm' and t7.get('Fonte do déficit') == 'Estimativa por ET', t7)
    qf = J("[...document.querySelectorAll('[role=group][aria-label^=\"Filtro rápido\"] button')].map(b=>b.innerText.replace(/\\s+\\d+$/,'').trim())") or []
    chk('IR-01: o filtro rápido de Situação tem os mesmos textos dos chips da coluna', set(x for x in qf if x != 'Todos') == {r.get('Situação') for r in d}, (qf, [r.get('Situação') for r in d]))
    g.filtra('Fonte do déficit', ['Estimativa por ET']); fl = [r.get('Setor') for r in g.dicts()]
    chk('IR-01: filtro Fonte do déficit = Estimativa por ET → Gotejo T7 e Pivô 1', sorted(fl) == ['Gotejo T7', 'Pivô 1'], fl)
    limpa(J); g.ordena('Déficit hoje', desc=True); df = [num(x) for x in g.col('Déficit hoje')]
    chk('IR-01: ordenar Déficit hoje (decrescente) pelo número (o ≈ não atrapalha)', crescente(df, True), g.col('Déficit hoje'))
    limpa(J); g.ordena('Próxima passada'); pp = [r.get('Setor') for r in g.dicts() if r.get('Próxima passada') not in ('', '—')]
    chk('IR-01: ordenar Próxima passada pelo instante (hoje 14:00 antes de amanhã 21:00)', pp[:2] == ['Gotejo T7', 'Pivô 1'], g.col('Próxima passada'))
    fazenda('Todas'); g = Grade(J, 0); hs = g.labels(); d = g.dicts()
    pv2 = sorted(r.get('Fazenda') for r in d if r.get('Setor') == 'Pivô 2')
    chk('IR-01 Todas: a coluna Fazenda entra (Pivô 2 da Santa Rita e da Lagoa Grande se distinguem) e cada célula fica sob o seu cabeçalho',
        hs[:2] == ['Setor', 'Fazenda'] and pv2 == ['Lagoa Grande', 'Santa Rita'] and alinhada(g) == 0, (hs[:3], pv2, alinhada(g)))
    lg = next((r for r in d if r.get('Fazenda') == 'Lagoa Grande' and r.get('Estádio') not in ('', '—')), {})
    chk('IR-01 Todas: Lagoa Grande com Cultura Mamão e a fase do mamão em Estádio (antes "Mamão · produção" numa célula)', lg.get('Cultura') == 'Mamão' and lg.get('Estádio') in ('formação inicial', 'pré-florada', 'produção', 'preparo de área'), lg)
    fazenda('Santa Rita'); g = Grade(J, 0)
    chk('IR-01 Santa Rita: a coluna Fazenda sai e a grade continua alinhada', g.labels() == SET and alinhada(g) == 0, g.labels()[:3])
    shot('ir01-1440')
    # ================= IR-02 =================
    abre('IR-02.dc.html'); g = Grade(J, 0)
    AG = ['Captação › ordem', 'Tipo', 'Setor', 'Bomba', 'Vazão', 'Início', 'Fim', 'Lâmina', 'Passadas', 'Etapa', 'Pendência', 'Próximo passo', 'Responsável', 'Avisos']
    d = tf03('IR-02 Agenda', g, AG, extra=())
    rio = next((r for r in d if r.get('Captação › ordem', '').startswith('Rio')), {}); o19 = next((r for r in d if r.get('Captação › ordem') == 'OS-0419'), {})
    chk('IR-02: captação com o pico de hoje na Vazão (166 L/s); OS-0419 Água | Pivô 2 | Bomba B2 | 166 L/s | hoje 20:00 | amanhã 10:31 | 10,81 mm | 1 | Liberadas',
        rio.get('Vazão') == '166 L/s' and [o19.get(k) for k in AG[1:10]] == ['Água', 'Pivô 2', 'Bomba B2', '166 L/s', 'hoje 20:00', 'amanhã 10:31', '10,81 mm', '1', 'Liberadas'], (rio, o19))
    g.ordena('Início'); bl = por_grupo(g, 'Início')
    ok_ = all(crescente([instante(x) for x in b]) or len([x for x in b if instante(x)]) < 2 for b in bl) and any(len([x for x in b if instante(x)]) > 1 for b in bl)
    chk('IR-02: ordenar Início pelo instante dentro da captação; "a definir" no fim', ok_ and all(b.index('a definir') == len(b) - 1 for b in bl if 'a definir' in b), bl)
    # ================= IR-03 =================
    abre('IR-03.dc.html'); g = Grade(J, 0)
    OSC = ['Ordem', 'Tipo', 'Setor', 'Cultura', 'Início', 'Fim', 'Lâmina', 'Passadas', 'Etapa', 'Pendência', 'Avisos', 'Próximo passo', 'Responsável']
    d = tf03('IR-03 Ordens', g, OSC)
    o94 = next((r for r in d if r.get('Ordem') == 'OS-0394'), {})
    chk('IR-03: OS-0394 Água | Pivô 2 | Milho | ontem 20:00 | ontem 22:06 | 10,81 mm | 1 | Em conferência | Divergência · −3,8 %',
        [o94.get(k) for k in OSC[1:10]] == ['Água', 'Pivô 2', 'Milho', 'ontem 20:00', 'ontem 22:06', '10,81 mm', '1', 'Em conferência', 'Divergência · −3,8 %'], o94)
    etapas = {r.get('Etapa') for r in d}
    chk('IR-03: Etapa só com as fases da O.S. (A liberar, Liberadas, Em execução, Em conferência, Encerradas)', etapas <= {'A liberar', 'Liberadas', 'Em execução', 'Em conferência', 'Encerradas'}, etapas)
    g.ordena('Início'); ini = g.col('Início'); ks = [instante(x) for x in ini if instante(x)]
    chk('IR-03: ordenar Início pelo instante (19/09 < ontem < hoje < amanhã; pelo texto "amanhã" viria antes de "hoje"); "a definir" no fim',
        crescente(ks) and ini[-1] == 'a definir' and ini.index('ontem 20:00') < ini.index('hoje 14:00') < ini.index('amanhã 21:00'), ini)
    g.ordena('Início', desc=True); ini2 = [instante(x) for x in g.col('Início') if instante(x)]
    chk('IR-03: ordenar Início decrescente pelo instante', crescente(ini2, True), g.col('Início'))
    rr = g.rotulos('Avisos'); g.filtra('Avisos', ['Ponta parcial (20–21 h)']); fl = [r.get('Ordem') for r in g.dicts()]
    chk('IR-03: filtro Avisos por item (Ponta parcial) → OS-0419', 'Ponta parcial (20–21 h)' in (rr or []) and fl == ['OS-0419'], (rr, fl))
    limpa(J)
    fazenda('Todas'); g = Grade(J, 0); d = g.dicts()
    chk('IR-03 Todas: coluna Fazenda (3ª) com Santa Rita e Lagoa Grande; células alinhadas', g.labels()[2] == 'Fazenda' and {r.get('Fazenda') for r in d} == {'Santa Rita', 'Lagoa Grande'} and alinhada(g) == 0, (g.labels()[:4], alinhada(g)))
    fazenda('Santa Rita'); shot('ir03-1440')
    # ================= IR-03det =================
    abre('IR-03det.dc.html#OS-0419'); gp, gt = Grade(J, 0), Grade(J, 1)
    dp = tf03('IR-03det Passadas', gp, ['Passada', 'Início', 'Fim', 'Lâmina', 'Duração', 'Estado', 'Área coberta', 'Volume medido'])
    chk('IR-03det: 1ª | hoje 20:00 | amanhã 10:31 | 10,81 mm | 14,5 h | Programada | — | —',
        dp and [dp[0].get(k) for k in ('Passada', 'Início', 'Fim', 'Lâmina', 'Duração', 'Estado', 'Área coberta', 'Volume medido')] == ['1ª', 'hoje 20:00', 'amanhã 10:31', '10,81 mm', '14,5 h', 'Programada', '—', '—'], dp)
    dt = tf03('IR-03det Trilha', gt, ['Quando', 'Recibo', 'Evento', 'Quem'])
    gt.ordena('Quando', desc=True); qd = [instante(x) for x in gt.col('Quando')]
    chk('IR-03det: ordenar Quando pelo instante', all(qd) and qd == sorted(qd, reverse=True), gt.col('Quando'))
    # ================= IR-04 =================
    abre('IR-04.dc.html'); gs, gc, gd = Grade(J, 0), Grade(J, 1), Grade(J, 2)
    ds = tf03('IR-04 Fontes', gs, ['Fonte', 'Grandeza', 'Unidade', 'Atualização', 'Calibração', 'Validade da calibração', 'Cobertura', 'Estado', 'Efeito no balanço'], chips=('Estado',))
    hp = next((r for r in ds if r.get('Fonte') == 'Hidrômetro · Pivô 2'), {}); s1 = next((r for r in ds if r.get('Fonte', '').startswith('Sonda de umidade · P1')), {})
    chk('IR-04: hidrômetro Volume | m³ | hoje 06:00 | Vence em 7 dias | 30/09/2026; sonda P1 Suspeita (o motivo vai para o painel)',
        [hp.get(k) for k in ('Grandeza', 'Unidade', 'Atualização', 'Calibração', 'Validade da calibração')] == ['Volume', 'm³', 'hoje 06:00', 'Vence em 7 dias', '30/09/2026'] and s1.get('Estado') == 'Suspeita', (hp, s1))
    gs.ordena('Atualização'); at = gs.col('Atualização')
    chk('IR-04: ordenar Atualização pelo instante (20/09 antes de hoje)', at and at[0] == '20/09 06:00' and crescente([instante(x) for x in at]), at)
    J("(()=>{const r=[...document.querySelectorAll('[role=row].g2ed')].find(x=>x.innerText.indexOf('Sonda de umidade · P1')===0); r&&r.querySelector('[role=cell] span').click();})()"); time.sleep(.5)
    sub = J("(document.querySelector('aside[role=dialog]')||{innerText:''}).innerText.replace(/\\s+/g,' ')") or ''
    chk('IR-04: o painel da sonda P1 diz o motivo da suspeita (salto de 18 p.p.)', 'Suspeita · salto de 18 p.p.' in sub, sub[:200])
    J("(()=>{const b=[...document.querySelectorAll('aside[role=dialog] button')].find(b=>b.innerText.trim()==='Cancelar'); b&&b.click();})()"); time.sleep(.3)
    dc = tf03('IR-04 Captações', gc, ['Captação', 'Outorga', 'Vazão outorgada', 'Regime', 'Vencimento', 'Situação', 'Volume hoje', 'Uso do dia', 'Setores ligados'])
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
    abre('IR-03det.dc.html#OS-0422:janela', 1.8)
    dlg = lambda: J("(document.querySelector('aside[role=dialog]')||{innerText:''}).innerText.replace(/\\s+/g,' ')") or ''
    clk = lambda t: J(f"(()=>{{const b=[...document.querySelectorAll('aside[role=dialog] button')].find(b=>b.innerText.trim()==={json.dumps(t)}); if(!b) return false; b.click(); return true;}})()")
    toast = lambda: J("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).filter(Boolean).join(' | ')") or ''
    d0 = dlg(); clk('Usar janela sugerida'); time.sleep(.4); clk('Salvar janela'); time.sleep(.8); t = toast()
    abre('IR-03.dc.html'); g = Grade(J, 0); o22 = next((r for r in g.dicts() if r.get('Ordem') == 'OS-0422'), {})
    g.ordena('Início'); ini = g.col('Início'); ords = g.col('Ordem'); k22 = ords.index('OS-0422') if 'OS-0422' in ords else -1
    chk('fluxo (normal): janela sugerida salva no detalhe (libera pela prontidão) → IR-03 mostra Início e Fim da OS-0422 e ordena por eles',
        'Definir janela' in d0 and 'OS-0422' in t and ('Janela salva' in t or 'Liberadas' in t) and instante(o22.get('Início')) and instante(o22.get('Fim')) and crescente([instante(x) for x in ini if instante(x)]) and k22 >= 0 and instante(ini[k22]), (d0[:80], t, o22))
    ini22 = o22.get('Início')
    abre('IR-03det.dc.html#OS-0422:janela', 1.8); pan = 'Definir janela' in dlg() or 'janela' in dlg().lower()
    J("""(()=>{const i=document.querySelector('#jn_h1'); if(!i) return; Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(i,''); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true}));})()"""); time.sleep(.3)
    clk('Salvar janela'); time.sleep(.6); t2 = toast()
    clk('Cancelar'); time.sleep(.3)
    abre('IR-03.dc.html'); o22b = next((r for r in Grade(J, 0).dicts() if r.get('Ordem') == 'OS-0422'), {})
    chk('fluxo (recusa): passada sem hora → "Informe data e hora da passada 1." e a janela gravada não muda', pan and 'Informe data e hora da passada 1' in t2 and o22b.get('Início') == ini22, (pan, t2, o22b.get('Início'), ini22))
    abre('IR-03det.dc.html#OS-0422:janela', 1.8); clk('Salvar janela'); time.sleep(.8)
    abre('IR-03.dc.html'); g = Grade(J, 0); n22 = g.col('Ordem').count('OS-0422'); o22c = next((r for r in g.dicts() if r.get('Ordem') == 'OS-0422'), {})
    chk('fluxo (repetição): salvar a mesma janela de novo não cria outra ordem nem muda o Início', n22 == 1 and o22c.get('Início') == ini22, (n22, o22c.get('Início')))
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
    ERRS.extend(J("window.__errs") or []); chk('sem erro de script (390)', not ERRS, ERRS[:3])
finally:
    c.close(); srv.terminate()
print(f'RESULTADO: {len(OK)}/{len(OK) + len(FAIL)} ok' + (' · FALHAS: ' + '; '.join(FAIL) if FAIL else ''))
sys.exit(1 if FAIL else 0)
