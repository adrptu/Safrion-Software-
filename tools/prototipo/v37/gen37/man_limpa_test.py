# -*- coding: utf-8 -*-
"""MAN-LIMPA-01 (proprietário, 14/10/2026: "em manutenção os filtros não estavam seguindo o padrão que definimos · elimine também os cards de
manutenção, vamos focar os cards na área de gráficos e relatórios · telas principais mais clean"). Confere no navegador, com oráculo dos dados (manGet):
  L1 nenhuma visão da Manutenção (Sem ordem, Ordens, Ativos, Planos) tem cartão de indicador, em 1440 e 390 px
  L2 cada visão tem a faixa Filtros do padrão (grupo "Filtros" com o funil), só com os filtros que valem para ela:
     Sem ordem e Ordens: Tipo, Criticidade, Grupo · Ativos: Grupo, Pendência · Planos: Grupo
  L3 Sem ordem · Tipo: Preventiva mostra só vencimentos de plano; Inspeção só achados de inspeção sem ordem; Corretiva só relatos e alertas sem ordem
  L4 Ordens · Tipo Corretiva + Criticidade Alta: as linhas são exatamente as ordens desse recorte, e o chip "Todas" conta o mesmo número
  L5 Grupo filtra também em Ativos e Planos (antes o seletor não tinha efeito nessas visões)
  L6 Lista e Kanban das ordens são ícones com nome (como na O.S.); o Kanban abre pelo ícone
  L7 sem erro de JS
  L8 Ativos › Abastecimentos: o Grupo filtra os lançamentos pelo ativo de cada um; limpar restaura todos; o grupo continua ao voltar a Ativos
     (revisão Codex 6160153073, MAN-LIMPA-GRUPO-01: antes o seletor aparecia e as 8 linhas ficavam)
  L9 "Pendências sem ordem" tem uma conta só: o cartão do Painel de Manutenção = as linhas da visão Sem ordem = manSemOrdem (antes 3 × 6)
Uso: python3 man_limpa_test.py (lê _render ou RENDER_DIR)."""
import os, sys, json, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
os.environ.setdefault('CDP_GL', '1')
from comp_lib import Chrome, servir

OK, FAIL = [], []
def chk(n, c, info=''):
    (OK if c else FAIL).append(n); print(('OK    ' if c else 'FALHA ') + n + ('' if c else ' · ' + str(info)[:700]), flush=True)
R = os.environ.get('RENDER_DIR') or os.path.join(HERE, '_render')
p, srv = servir(R); c = Chrome(); J = c.js
U = lambda pg: f'http://127.0.0.1:{p}/{pg}'
FAIXA = "[...document.querySelectorAll('[role=group][aria-label=Filtros]')].filter(g=>g.getClientRects().length&&g.querySelector('.mf-rot svg')).map(g=>[...g.querySelectorAll('select')].filter(s=>s.getClientRects().length).map(s=>s.getAttribute('aria-label')))"
CARDS = "[...document.querySelectorAll('main .ma-card, main .ma-cards')].filter(e=>e.getClientRects().length).length"
RIDS = "[...document.querySelectorAll('[role=row][data-rid]')].filter(r=>r.getClientRects().length).map(r=>r.getAttribute('data-rid'))"
def setf(rot, val):
    r = J(f"(()=>{{const s=[...document.querySelectorAll('[role=group][aria-label=Filtros] select')].find(s=>s.getAttribute('aria-label')==={json.dumps('Filtrar por ' + rot)}&&s.getClientRects().length); if(!s) return false;"
          f" Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype,'value').set.call(s,{json.dumps(val)}); s.dispatchEvent(new Event('change',{{bubbles:true}})); return true;}})()")
    time.sleep(.5); return r
def vis(v): c.goto(U('MA.dc.html#vis=' + v), 1.6)
ESPERA = {'semordem': ['Filtrar por tipo', 'Filtrar por criticidade', 'Filtrar por grupo'], 'ordens': ['Filtrar por tipo', 'Filtrar por criticidade', 'Filtrar por grupo'],
          'ativos': ['Filtrar por grupo', 'Filtrar por pendência'], 'planos': ['Filtrar por grupo']}
try:
    c.call('Page.addScriptToEvaluateOnNewDocument', {'source': "window.__err='';addEventListener('error',e=>{window.__err+=(e.message||'erro')+' | ';});"})
    cartoes, faixas = {}, {}
    for w, h, m in ((1440, 900, False), (390, 844, True)):
        c.aparelho(w, h, 2 if m else 1, m); c.goto(U('Main.dc.html'), .3); J("localStorage.clear(); sessionStorage.clear(); 1")
        for v in ESPERA:
            vis(v); cartoes[f'{v}@{w}'] = J(CARDS); faixas[f'{v}@{w}'] = J(FAIXA)
    chk('L1 nenhuma visão da Manutenção tem cartão de indicador (1440 e 390 px)', all(n == 0 for n in cartoes.values()), cartoes)
    # 15/10/2026 (DS, FIL-02): Prazo (Sem ordem), Fase e Rotina (Ordens) entraram na faixa; a 1440 px são chips, a 390 px viram seletor
    E390 = dict(ESPERA, semordem=ESPERA['semordem'] + ['Filtrar por prazo'], ordens=ESPERA['ordens'] + ['Filtrar por fase', 'Filtrar por rotina'])
    chk('L2 faixa Filtros com o funil em cada visão, só com os filtros dela', all(faixas[f'{v}@1440'] == [ESPERA[v]] and faixas[f'{v}@390'] == [E390[v]] for v in ESPERA), faixas)
    c.aparelho(1440, 900, 1, False)
    # L3 · Sem ordem por tipo (oráculo: achados sem ordem por origem; vencimentos com o prefixo v:)
    vis('semordem')
    ach = J("(()=>{ const c=window.__man.manGet(); return Object.values(c.achados).filter(q=>q.estado==='Sem ordem'&&c.ativos[q.aid]).map(q=>[q.id,q.origem]); })()") or []
    insp = sorted('a:' + i for i, o in ach if o == 'Inspeção'); corr = sorted('a:' + i for i, o in ach if o != 'Inspeção')
    t0 = J(RIDS) or []
    setf('tipo', 'Preventiva'); pv = J(RIDS) or []
    setf('tipo', 'Inspeção'); ins = sorted(J(RIDS) or [])
    setf('tipo', 'Corretiva'); cor = sorted(J(RIDS) or [])
    setf('tipo', '')
    chk('L3 Sem ordem · Tipo: Preventiva só vencimentos; Inspeção só achados de inspeção; Corretiva só relatos e alertas',
        bool(pv) and all(r.startswith('v:') for r in pv) and ins == insp and cor == corr and len(t0) == len(pv) + len(ins) + len(cor) and bool(ins) and bool(cor),
        [t0, pv, ins, insp, cor, corr])
    # L4 · Ordens: Corretiva + Alta (oráculo: as ordens não canceladas desse recorte)
    vis('ordens'); setf('tipo', 'Corretiva'); setf('criticidade', 'Alta')
    esp = sorted(J("Object.values(window.__man.manGet().oms).filter(o=>o.etapa!=='Canceladas'&&o.tipo==='Corretiva'&&o.crit==='Alta').map(o=>o.id)") or [])
    got = sorted(J(RIDS) or []); todas = J("(()=>{const b=[...document.querySelectorAll('[aria-label=\"Filtrar por fase\"] button')].find(b=>/^Todas/.test(b.innerText.trim())); return b?b.innerText.replace(/\\s+/g,' ').trim():'';})()") or ''
    chk('L4 Ordens · Corretiva + Alta: linhas = ordens do recorte; o chip Todas conta o mesmo', got == esp and bool(esp) and todas == f'Todas {len(esp)}', [got, esp, todas])
    setf('tipo', ''); setf('criticidade', '')
    # L5 · Grupo em Ativos e Planos
    vis('ativos'); g = J("(()=>{const s=[...document.querySelectorAll('[role=group][aria-label=Filtros] select')].find(s=>s.getAttribute('aria-label')==='Filtrar por grupo'&&s.getClientRects().length); return s?[...s.options].map(o=>o.value).filter(Boolean):[];})()") or []
    a0 = J(RIDS) or []; grp = g[0] if g else ''
    setf('grupo', grp); a1 = J(RIDS) or []
    ga = J(f"(()=>{{const c=window.__man.manGet(); return c.ordem.filter(id=>c.ativos[id]&&c.ativos[id].grupo==={json.dumps(grp)});}})()") or []
    vis('planos'); setf('grupo', ''); p0 = J(RIDS) or []
    gp = J("(()=>{ const c=window.__man.manGet(); const ps=c.ordemPlanos.map(id=>c.planos[id]).filter(Boolean); const g={}; ps.forEach(p=>{ g[p.grupo]=(g[p.grupo]||0)+1; }); const k=Object.keys(g).find(k=>g[k]<ps.length); return k?[k,ps.filter(p=>p.grupo===k).map(p=>p.id)]:null; })()")
    p1 = []
    if gp: setf('grupo', gp[0]); p1 = J(RIDS) or []
    chk('L5 Grupo filtra também em Ativos e Planos', bool(grp) and sorted(a1) == sorted(ga) and len(a1) < len(a0) and bool(gp) and sorted(p1) == sorted(gp[1]) and len(p1) < len(p0),
        [grp, len(a0), a1, ga, gp, len(p0), p1])
    setf('grupo', '')
    # L6 · Lista | Kanban em ícones
    vis('ordens')
    tb = J("(()=>{const t=[...document.querySelectorAll('[role=toolbar][aria-label=\"Visão das ordens\"]')].find(t=>t.getClientRects().length); if(!t) return null; return [...t.querySelectorAll('button')].map(b=>[b.getAttribute('aria-label'),b.innerText.trim(),!!b.querySelector('svg'),b.getAttribute('aria-pressed')]);})()")
    J("(()=>{const b=[...document.querySelectorAll('[role=toolbar][aria-label=\"Visão das ordens\"] button')].find(b=>b.getAttribute('aria-label')==='Kanban'); if(b) b.click();})()"); time.sleep(.6)
    kb = J("!!document.querySelector('[aria-label=\"Kanban das ordens\"]')&&document.querySelector('[aria-label=\"Kanban das ordens\"]').getClientRects().length>0")
    # DS VIS-05 (padroes-1510, 15/10/2026: "toda lista tem Tabela e Cartões"): Cartões entra entre a Lista e o Kanban
    chk('L6 Lista, Cartões e Kanban em ícones com nome; o ícone Kanban abre o quadro', tb == [['Lista', '', True, 'true'], ['Cartões', '', True, 'false'], ['Kanban', '', True, 'false']] and kb, [tb, kb])
    # L8 · Abastecimentos (oráculo: c.abast cujo ativo é do grupo; o grupo com mais lançamentos, que não seja o total)
    vis('ativos&modo=abastecimentos'); setf('grupo', ''); b0 = J(RIDS) or []
    ga = J("(()=>{ const c=window.__man.manGet(); const g={}; (c.abast||[]).forEach(b=>{ const k=(c.ativos[b.aid]||{}).grupo; if(k) (g[k]=g[k]||[]).push(b.id); });"
           " const k=Object.keys(g).sort((x,y)=>g[y].length-g[x].length).find(k=>g[k].length<(c.abast||[]).length); return k?[k,g[k]]:null; })()")
    b1 = []; b2 = []; ga_vol = None
    if ga:
        setf('grupo', ga[0]); b1 = J(RIDS) or []
        J("(()=>{const b=[...document.querySelectorAll('main button')].find(b=>b.innerText.trim()==='Ativos'&&b.getClientRects().length); if(b) b.click();})()"); time.sleep(.5)
        ga_vol = J("(()=>{const s=[...document.querySelectorAll('[role=group][aria-label=Filtros] select')].find(s=>s.getAttribute('aria-label')==='Filtrar por grupo'&&s.getClientRects().length); return s?s.value:null;})()")
        J("(()=>{const b=[...document.querySelectorAll('main button')].find(b=>b.innerText.trim()==='Abastecimentos'&&b.getClientRects().length); if(b) b.click();})()"); time.sleep(.5)
        setf('grupo', ''); b2 = J(RIDS) or []
    chk('L8 Abastecimentos: o Grupo filtra pelo ativo do lançamento; limpar restaura; o grupo continua ao voltar a Ativos',
        bool(ga) and sorted(b1) == sorted(ga[1]) and len(b1) < len(b0) and sorted(b2) == sorted(b0) and ga_vol == ga[0], [ga, len(b0), b1, ga_vol, len(b2)])
    # L9 · a mesma conta no Painel e na visão (oráculo: manSemOrdem do domínio)
    c.goto(U('PMAN.dc.html'), 1.6)
    pm = J("(()=>{ const m=document.querySelector('main').innerText.match(/Pendências sem ordem\\s*(?:ⓘ\\s*)?(\\d+)/); return m?+m[1]:null; })()")
    vis('semordem'); setf('tipo', ''); setf('criticidade', ''); setf('grupo', '')
    so = len(J(RIDS) or []); n = J("window.__man.manSemOrdem?window.__man.manSemOrdem(window.__man.manGet()).n:null")
    chk('L9 "Pendências sem ordem": cartão do Painel = linhas da visão Sem ordem = manSemOrdem', pm is not None and pm == so == n and n > 0, [pm, so, n])
    chk('L7 sem erro de JS', not (J("window.__err") or ''), J("window.__err"))
finally:
    try: c.close()
    except Exception: pass
    srv.terminate()
print(f'RESULTADO: {len(OK)} ok · {len(FAIL)} falhas')
sys.exit(1 if FAIL else 0)
