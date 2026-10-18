# -*- coding: utf-8 -*-
"""VISOES-2 (F2a) · Calendário da O.S. (proprietário, 13/10/2026: "já implantou os modos de visão em todas telas?"). Só leitura: a semana de
segunda a domingo com o mesmo recorte da Lista e do Kanban (filtros, busca, Talhão; Canceladas fora); a ordem aparece em cada dia da sua janela;
sem início, na faixa "Sem data"; o clique abre o mesmo painel; programar fica no detalhe (sem arrastar). Confere no navegador:
  K1 o seletor tem a visão Calendário (ícone, "Ver em calendário") e ela abre na semana de hoje do cenário (21/09 a 27/09/2026), 7 dias
  K2 oráculo: as ordens da semana = as da Lista (mesmo recorte) cuja janela Início–Fim cruza a semana; cada uma em cada dia da janela
  K3 ‹ › trocam de semana e "Hoje" volta; K4 o filtro da faixa vale (Cultura: Café → só OS-0425 na semana dela)
  K5 semana sem ordem do recorte: o estado diz isso e leva à próxima semana com ordem
  K6 o clique no cartão abre o painel da ordem; nada é arrastável
  K7 390 px: agenda por dia (só os dias com ordem), sem rolagem lateral; K8 sem erro de JS
  K9 teclado (CAL-C961-FOCO-01, revisão Codex de 13/10): Enter no cartão abre o painel com o foco dentro dele; Esc fecha e o foco volta ao
     cartão (1440 e 390 px)
Uso: python3 visoes_calendario_test.py (lê _render ou RENDER_DIR)."""
import os, re, sys, json, time, datetime as dt
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, servir, troca_visao

OK, FAIL = [], []
def chk(n, c, info=''):
    (OK if c else FAIL).append(n); print(('OK    ' if c else 'FALHA ') + n + ('' if c else ' · ' + str(info)[:700]), flush=True)

R = os.environ.get('RENDER_DIR') or os.path.join(HERE, '_render')
p, srv = servir(R); c = Chrome(); J = c.js
U = lambda pg: f'http://127.0.0.1:{p}/{pg}'
SEG, DOM = dt.date(2026, 9, 21), dt.date(2026, 9, 27)
# VISOES-2 V2-1 (14/10): a ordem de vários dias fica uma vez na faixa (.oscal.oscal-faixa, grid-column a / span n) e conta em cada dia que
# ela cobre; a grade dos dias é o outro .oscal (só as ordens visíveis contam: a célula guarda uma cópia compacta para o celular).
# O teste lia o primeiro .oscal (a faixa) e achava 0 dias (oráculo obsoleto desde 14/10)
CAL = """JSON.stringify((()=>{ const gs=[...document.querySelectorAll('.oscal')].filter(x=>x.getClientRects().length); const g=gs.find(x=>x.querySelector('.oscal-dia')); if(!g) return null;
  const idDe=b=>(b.getAttribute('aria-label')||'').replace(/^Abrir /,'').split(' · ')[0], fx=gs.find(x=>x.classList.contains('oscal-faixa'));
  const multi=fx?[...fx.querySelectorAll('.oscal-o')].map(b=>{ const m=/grid-column:\s*(\d+)\s*\/\s*span\s*(\d+)/.exec(b.getAttribute('style')||''); return {id:idDe(b),a:m?+m[1]:0,n:m?+m[2]:0}; }):[];
  const dias=[...g.querySelectorAll('.oscal-dia')].map((d,i)=>({t:d.getAttribute('aria-label'), vis:d.getClientRects().length>0, ids:[...d.querySelectorAll('.oscal-o')].filter(b=>b.getClientRects().length).map(idDe).concat(multi.filter(o=>i+1>=o.a&&i+1<o.a+o.n).map(o=>o.id))}));
  const tit=[...document.querySelectorAll('b[aria-live]')].map(b=>b.innerText).find(Boolean)||''; return {dias,tit,drag:document.querySelectorAll('.oscal [draggable=true]').length}; })())"""
# Colunas essenciais: Início e Fim saíram da vista padrão e ficam no seletor "Colunas". O oráculo liga as duas pelo mesmo seletor que o
# usuário usa e lê as linhas VISÍVEIS da Tabela (mesmo recorte)
LISTA = """JSON.stringify((()=>{ const t=[...document.querySelectorAll('[role=table]')].find(t=>t.offsetParent); if(!t) return null;
  const hs=[...t.querySelectorAll('[role=columnheader]')].map(h=>h.innerText.replace(/[⇅▾▴▲▼]/g,'').trim().toUpperCase());
  const iI=hs.findIndex(h=>h.startsWith('INÍCIO')), iF=hs.findIndex(h=>h.startsWith('FIM')), iS=hs.findIndex(h=>h.startsWith('FASE'));
  return [...t.querySelectorAll('[role=row][data-rid]')].map(r=>{ const cs=[...r.querySelectorAll('[role=cell]')].map(c=>c.innerText.trim()); return [r.getAttribute('data-rid'),cs[iI],cs[iF],cs[iS]]; }); })())"""
def colunas(*rots):
    J("(()=>{const b=document.querySelector('[data-g2cvb=g_os]'); if(b&&b.getAttribute('aria-expanded')!=='true') b.click();})()"); time.sleep(.45)
    for rot in rots:
        J("(()=>{const l=[...document.querySelectorAll('[data-g2cv=g_os] label')].find(x=>x.innerText.trim()===%s); const i=l&&l.querySelector('input'); if(i&&!i.checked) i.click();})()" % json.dumps(rot)); time.sleep(.45)
    J("(()=>{const b=document.querySelector('[data-g2cvb=g_os]'); if(b&&b.getAttribute('aria-expanded')==='true') b.click();})()"); time.sleep(.3)
def iso(br):   # aceita 2026-09-21, 20260921 e 21/09/2026
    br = str(br or '').strip()
    try:
        if re.match(r'^\d{4}-\d{2}-\d{2}', br): return dt.date(int(br[:4]), int(br[5:7]), int(br[8:10]))
        if re.match(r'^\d{8}$', br): return dt.date(int(br[:4]), int(br[4:6]), int(br[6:8]))
        d, m, a = br.split('/'); return dt.date(int(a), int(m), int(d))
    except Exception: return None
def oraculo():
    # DRILL-RECOLHIDO (v129, 17/10): a Tabela abre recolhida; o oráculo expande tudo antes de ler as linhas das O.S.
    J("(()=>{const b=[...document.querySelectorAll('.g2xtog')].find(x=>x.offsetParent&&/Expandir tudo/.test(x.innerText||'')); if(b) b.click();})()"); time.sleep(.6)
    colunas('Início', 'Fim')
    ls = json.loads(J(LISTA) or 'null') or []; esp = {}
    for rid, ini, fim, fase in ls:
        a = iso(ini)
        if not a or fase == 'Canceladas': continue
        b = iso(fim) or a
        if b < a: b = a
        if a <= DOM and b >= SEG:
            esp[rid] = sorted(str(SEG + dt.timedelta(k)) for k in range(7) if a <= SEG + dt.timedelta(k) <= b)
    return esp, ls
def limpa(): c.goto(U('Main.dc.html'), .3); J("localStorage.clear(); sessionStorage.clear(); 1")
def sel(al, val):
    J(f"""(()=>{{const s=document.querySelector('select[aria-label="{al}"]'); s.value={json.dumps(val)}; s.dispatchEvent(new Event('change',{{bubbles:true}}));}})()"""); time.sleep(.7)
try:
    c.call('Page.addScriptToEvaluateOnNewDocument', {'source': "window.__err='';addEventListener('error',e=>{window.__err+=(e.message||'erro')+' | ';});"})
    c.aparelho(1440, 900, 1, False); limpa(); c.goto(U('OS.dc.html'), 1.5)
    bt = json.loads(J("JSON.stringify((()=>{const b=document.querySelector('[data-visao=\"calendario\"]'); return b?[b.getAttribute('aria-label'),!!b.querySelector('svg path')]:null;})())") or 'null')
    esp, ls = oraculo()
    troca_visao(J, 'calendario'); k = json.loads(J(CAL) or 'null')
    chk('K1 visão Calendário no seletor ("Ver em calendário", ícone) abre na semana de hoje do cenário, 21/09 a 27/09/2026, com 7 dias',
        bt == ['Ver em calendário', True] and k and k['tit'] == '21/09 a 27/09/2026' and len(k['dias']) == 7, [bt, k and k['tit'], k and len(k['dias'])])
    dias = [str(SEG + dt.timedelta(i)) for i in range(7)]
    vis = {}
    for i, d in enumerate((k or {}).get('dias', [])):
        for oid in d['ids']: vis.setdefault(oid, []).append(dias[i])
    chk('K2 as ordens da semana = as da Lista (mesmo recorte) com janela que cruza a semana, cada uma em cada dia da janela (oráculo pela Lista)',
        bool(esp) and {o: sorted(v) for o, v in vis.items()} == esp, [sorted(esp.items())[:4], sorted(vis.items())[:4]])
    J("document.querySelector('button[aria-label=\"Próxima semana\"]').click()"); time.sleep(.6); t1 = (json.loads(J(CAL) or '{}') or {}).get('tit')
    J("document.querySelector('button[aria-label=\"Semana anterior\"]').click()"); time.sleep(.3); J("document.querySelector('button[aria-label=\"Semana anterior\"]').click()"); time.sleep(.6)
    t2 = (json.loads(J(CAL) or '{}') or {}).get('tit')
    J("[...document.querySelectorAll('button')].find(b=>b.innerText.trim()==='Hoje'&&b.offsetParent).click()"); time.sleep(.6); t3 = (json.loads(J(CAL) or '{}') or {}).get('tit')
    chk('K3 › vai à semana seguinte, ‹ volta, e "Hoje" retorna à semana do cenário', t1 == '28/09 a 04/10/2026' and t2 == '14/09 a 20/09/2026' and t3 == '21/09 a 27/09/2026', [t1, t2, t3])
    # K6 · clique abre o painel; nada arrastável
    alvo = next(iter(sorted(vis)), None)
    if alvo: J(f"[...document.querySelectorAll('.oscal-o')].find(b=>(b.getAttribute('aria-label')||'').indexOf('Abrir {alvo} ')===0).click()"); time.sleep(.8)
    pan = J("(()=>{const a=[...document.querySelectorAll('aside[aria-label], [role=dialog]')].find(x=>x.getClientRects().length); return a?a.innerText.slice(0,200):'';})()") or ''
    chk('K6 o clique no cartão abre o painel da ordem; nenhum cartão arrastável', bool(alvo) and alvo in pan and k and k['drag'] == 0, [alvo, pan[:80]])
    # K4 · filtro da faixa vale no calendário (Café: OS-0425 em 15/10)
    limpa(); c.goto(U('OS.dc.html'), 1.4); sel('Filtrar por cultura', 'Café'); troca_visao(J, 'calendario')
    k4 = json.loads(J(CAL) or 'null') or {}; ids4 = sorted({i for d in k4.get('dias', []) for i in d['ids']})
    est = J("(()=>{const e=[...document.querySelectorAll('[role=status],[role=note]')].map(x=>x.innerText).find(t=>/Nenhuma ordem do recorte nesta semana/.test(t)); return e||'';})()") or ''
    bt5 = J("(()=>{const b=[...document.querySelectorAll('button')].find(b=>/^Ir para a semana de /.test(b.innerText.trim())&&b.offsetParent); return b?b.innerText.trim():'';})()") or ''
    if bt5: J("[...document.querySelectorAll('button')].find(b=>/^Ir para a semana de /.test(b.innerText.trim())&&b.offsetParent).click()"); time.sleep(.7)
    k5 = json.loads(J(CAL) or 'null') or {}; ids5 = sorted({i for d in k5.get('dias', []) for i in d['ids']})
    chk('K4/K5 Cultura Café: a semana de hoje fica sem ordem e o estado diz isso, com o atalho para a próxima semana com ordem (15/10: só a OS-0425)',
        ids4 == [] and 'Nenhuma ordem do recorte nesta semana' in est and bt5 == 'Ir para a semana de 15/10' and ids5 == ['OS-0425'] and k5.get('tit') == '12/10 a 18/10/2026', [ids4, est[:80], bt5, ids5, k5.get('tit')])
    # K7 · celular
    # na semana do cenário todos os dias têm ordem; o recorte Café na semana de 15/10 tem um dia só: a agenda mostra só ele, em coluna única
    c.aparelho(390, 844, 2, True); limpa(); c.goto(U('OS.dc.html'), 1.4); sel('Filtrar por cultura', 'Café'); troca_visao(J, 'calendario')
    J("(()=>{const b=[...document.querySelectorAll('button')].find(b=>/^Ir para a semana de /.test(b.innerText.trim())&&b.offsetParent); if(b) b.click();})()"); time.sleep(.7)
    k7 = json.loads(J(CAL) or 'null') or {}; lg = J("document.documentElement.scrollWidth-document.documentElement.clientWidth")
    vis7 = [d for d in k7.get('dias', []) if d['vis']]
    larg = json.loads(J("JSON.stringify([Math.round(document.querySelector('.oscal').getBoundingClientRect().width)].concat([...document.querySelectorAll('.oscal-dia')].filter(d=>d.getClientRects().length).map(d=>Math.round(d.getBoundingClientRect().width))))") or '[]')
    chk('K7 390 px: agenda só com os dias que têm ordem (semana de 15/10, Café: só quinta 15/10), coluna única, sem rolagem lateral',
        len(vis7) == 1 and vis7[0]['ids'] == ['OS-0425'] and (vis7[0]['t'] or '').startswith('qui 15/10') and len(larg) == 2 and larg[1] >= larg[0] - 2 and (lg or 0) <= 0, [[(d['t'], d['ids']) for d in vis7], larg, lg])
    # K9 · teclado: Enter abre o painel com o foco dentro; Esc fecha e devolve o foco ao cartão
    k9 = []
    for w, h, m in ((1440, 900, False), (390, 844, True)):
        c.aparelho(w, h, 2 if m else 1, m); limpa(); c.goto(U('OS.dc.html'), 1.4); troca_visao(J, 'calendario')
        J("(()=>{const b=[...document.querySelectorAll('.oscal-o')].find(x=>x.getClientRects().length); if(b) b.focus();})()"); a0 = J("(document.activeElement&&document.activeElement.getAttribute('aria-label'))||''") or ''
        c.tecla('Enter', 'Enter', 13, text='\r'); time.sleep(.8)
        dentro = J("!!(document.activeElement&&document.activeElement.closest&&document.activeElement.closest('aside[role=dialog]'))")
        c.tecla('Escape', 'Escape', 27); time.sleep(.8)
        fechou = not J("[...document.querySelectorAll('aside[role=dialog]')].some(a=>a.getClientRects().length)")
        a1 = J("(document.activeElement&&document.activeElement.getAttribute('aria-label'))||''") or ''
        k9.append([w, a0[:30], dentro, fechou, a1 == a0 and bool(a0)])
    chk('K9 teclado: Enter no cartão abre o painel com o foco dentro; Esc fecha e o foco volta ao mesmo cartão (1440 e 390 px)', all(x[2] and x[3] and x[4] for x in k9), k9)
    chk('K8 sem erro de JS', not (J("window.__err||''") or ''), J("window.__err||''"))
finally:
    try: c.close()
    except Exception: pass
    srv.terminate()
print(f'RESULTADO: {len(OK)} ok · {len(FAIL)} falhas')
sys.exit(1 if FAIL else 0)
