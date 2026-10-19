# -*- coding: utf-8 -*-
"""EX-41 · varredura das páginas do render (G/_render, 62f2c35, dados sintéticos) a 1440 × 900, no estado inicial de cada página.
Por página: primárias verdes (rótulo), destrutivas à vista fora do ⋯, botões indisponíveis (motivo visível, só dica, nenhum), tabelas
(colunas com ordenar e com funil), Agrupar por e Colunas, caixas de seleção, faixa de etapas, formas de filtrar da lista (busca, lista
suspensa na barra, filtro rápido, funil) e texto interno à vista (IDs de requisito e notas de projeto).
Heurística, não oráculo: cada número vem com exemplos em out/p4_ex41_varredura.json. Só leitura."""
import os, sys, json, time, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from base import chrome, server, dump, log, OUT, PNG, G
R_DIR = os.path.join(G, '_render')
PAGS = sorted(f for f in os.listdir(R_DIR) if f.endswith('.dc.html'))
L = open(os.path.join(OUT, 'p4_ex41_varredura.log'), 'a' if os.environ.get('RETOMA') else 'w', encoding='utf-8')
port = server(R_DIR); c = chrome(); J = c.js; c.aparelho(1440, 900)
U = lambda pg: f'http://127.0.0.1:{port}/{pg}'
MEDE = r"""JSON.stringify((()=>{const n=s=>(s||'').replace(/\s+/g,' ').trim(); const vis=e=>{const r=e.getBoundingClientRect(); const cs=getComputedStyle(e); return r.width>1&&r.height>1&&cs.visibility!=='hidden'&&cs.display!=='none';};
 const B=document.body; const lat=e=>!!e.closest('.menu-lat,nav[aria-label="Menu principal"],[role=navigation]');
 const verde=e=>getComputedStyle(e).backgroundColor==='rgb(30, 122, 76)'&&parseFloat(getComputedStyle(e).borderTopLeftRadius)<30&&!e.closest('.menu-lat,[role=tablist],[role=group],[role=listbox],[role=radiogroup]');
 const btns=[...B.querySelectorAll('button,a,[role=button]')].filter(vis).filter(b=>!lat(b));
 const prim=btns.filter(verde).map(b=>n(b.innerText)||('['+(b.getAttribute('aria-label')||'')+']'));
 const DESTR=/^(Excluir|Remover|Apagar|Descartar|Estornar|Rejeitar|Recusar|Desativar|Inativar|Arquivar|Reprovar|Cancelar\s+\S)/i;
 const destr=btns.filter(b=>!b.closest('[role=menu]')&&DESTR.test(n(b.innerText)||b.getAttribute('aria-label')||'')).map(b=>n(b.innerText)||b.getAttribute('aria-label'));
 const dis=btns.filter(b=>b.disabled||b.getAttribute('aria-disabled')==='true').map(b=>{ const p=b.parentElement; const mot=p&&p.querySelector('.g2motivo'); const mv=mot&&vis(mot)?n(mot.innerText):'';
   const dica=b.getAttribute('data-dica')||b.title||((b.getAttribute('aria-describedby')||'').split(' ').map(id=>{const x=document.getElementById(id); return x?n(x.textContent):'';}).join(' '));
   return {t:n(b.innerText)||b.getAttribute('aria-label')||'', mot:mv, dica:n(dica).slice(0,160)}; });
 const heads=[...B.querySelectorAll('[role=columnheader],th')].filter(vis);
 const hSort=heads.filter(h=>[...h.querySelectorAll('button')].some(x=>/^Ordenar/.test(x.getAttribute('aria-label')||''))).length;
 const hFun=heads.filter(h=>[...h.querySelectorAll('button')].some(x=>/^Filtrar/.test(x.getAttribute('aria-label')||''))).length;
 const tabs=[...B.querySelectorAll('[role=table],table')].filter(vis).length;
 const tabsSemCtl=[...B.querySelectorAll('[role=table],table')].filter(vis).filter(t=>![...t.querySelectorAll('button')].some(x=>/^(Ordenar|Filtrar)/.test(x.getAttribute('aria-label')||''))).map(t=>n((t.getAttribute('aria-label')||'')+' '+([...t.querySelectorAll('[role=columnheader],th')].slice(0,3).map(h=>n(h.innerText)).join('|'))).slice(0,90));
 const txtBtn=t=>btns.some(b=>new RegExp('^'+t).test(n(b.innerText)));
 const chk=[...B.querySelectorAll('input[type=checkbox],[role=checkbox]')].filter(vis).filter(x=>x.closest('[role=table],table,[role=row]')).length;
 const sel=/\d+ selecionad/.test(B.innerText);
 const etapas=!!([...B.querySelectorAll('.etp-ind,[aria-label*="Etapas"],[aria-label*="etapas"]')].filter(vis).length);
 const busca=[...B.querySelectorAll('input')].filter(vis).filter(i=>i.type==='search'||/Buscar/i.test((i.placeholder||'')+(i.getAttribute('aria-label')||''))).length;
 const topo=[...B.querySelectorAll('[role=group][aria-label=Filtros] select, [role=group][aria-label=Filtros] button')].filter(vis).length;
 const barSel=[...B.querySelectorAll('select')].filter(vis).filter(s=>!s.closest('[role=group][aria-label=Filtros]')&&!/perfil/i.test(s.getAttribute('aria-label')||'')&&s.closest('main')).map(s=>s.getAttribute('aria-label')||'');
 const rapido=[...B.querySelectorAll('[role=group][aria-label]')].filter(vis).filter(g=>/Filtro rápido|Filtrar por/i.test(g.getAttribute('aria-label'))&&!g.closest('[role=group][aria-label=Filtros]')).map(g=>g.getAttribute('aria-label'));
 const main=B.querySelector('main')||B; const txt=main.innerText;
 const NOTA=/(\b(PRD|AGENTS|TODO)\b|\bDEC-\d{4}|\bENG-\d{3}|\bCAL-\d{2}|\bCMD-\d{2}|\bPEND-\d{2}|\bEX-\d{2}\b|\bDS-\d{2}\b|\bRN-\d{3}|\bPROJ-\d{2}|No Safrion|no protótipo|nota interna)/g;
 const notas=[]; let m; while((m=NOTA.exec(txt))&&notas.length<6){ notas.push(n(txt.slice(Math.max(0,m.index-45),m.index+45))); }
 const nNotas=(txt.match(NOTA)||[]).length;
 return {h1:n((document.querySelector('h1')||{innerText:''}).innerText),nh1:document.querySelectorAll('h1').length,prim,destr,dis,heads:heads.length,hSort,hFun,tabs,tabsSemCtl,agrupar:txtBtn('Agrupar por'),colunas:txtBtn('Colunas'),chk,sel,etapas,busca,topo,barSel,rapido,nNotas,notas};})())"""
PARC = os.path.join(OUT, 'p4_ex41_varredura.json')
RES = json.load(open(PARC, encoding='utf-8')) if os.environ.get('RETOMA') and os.path.exists(PARC) else {}
c.goto(U('Main.dc.html'), .2)
for i, pg in enumerate(PAGS):
    if pg in RES and 'falha' not in RES[pg]: continue
    t0 = time.time()
    try:
        J("try{localStorage.clear(); sessionStorage.clear()}catch(e){}; 1"); c.goto(U(pg), .3)
        RES[pg] = json.loads(J(MEDE)); RES[pg]['erros'] = J("window.__errs||[]")
    except Exception as e:
        RES[pg] = {'falha': str(e)[:200]}
    x = RES[pg]; log(L, f"{i+1:3d} {pg:28s} {time.time()-t0:4.1f}s prim={x.get('prim')} destr={len(x.get('destr', []))} dis={len(x.get('dis', []))} cab={x.get('heads')}/{x.get('hSort')}/{x.get('hFun')} notas={x.get('nNotas')}")
    if i % 10 == 0: dump('p4_ex41_varredura.json', RES)
dump('p4_ex41_varredura.json', RES)
# ---------- resumo ----------
ok = {k: v for k, v in RES.items() if 'falha' not in v}
prims = [(k, p) for k, v in ok.items() for p in v['prim'] if p]
uma = [(k, p) for k, p in prims if len(p.split()) == 1]
dis = [(k, d) for k, v in ok.items() for d in v['dis']]
S = dict(paginas=len(RES), falhas=[k for k, v in RES.items() if 'falha' in v],
         prim_total=len(prims), prim_paginas_com_mais_de_1=[(k, v['prim']) for k, v in ok.items() if len([p for p in v['prim'] if p]) > 1],
         prim_uma_palavra=uma, prim_rotulos=sorted(set(p for _, p in prims)),
         destr_a_vista=[(k, v['destr']) for k, v in ok.items() if v['destr']],
         dis_total=len(dis), dis_com_motivo_visivel=sum(1 for _, d in dis if d['mot']), dis_so_dica=sum(1 for _, d in dis if not d['mot'] and d['dica']), dis_sem_nada=[(k, d['t']) for k, d in dis if not d['mot'] and not d['dica']],
         dis_exemplos=dis[:25],
         cab_total=sum(v['heads'] for v in ok.values()), cab_ordenar=sum(v['hSort'] for v in ok.values()), cab_funil=sum(v['hFun'] for v in ok.values()),
         tabelas=sum(v['tabs'] for v in ok.values()), tabelas_sem_ordenar_filtrar=[(k, v['tabsSemCtl']) for k, v in ok.items() if v['tabsSemCtl']],
         paginas_com_tabela=sum(1 for v in ok.values() if v['tabs']), com_agrupar=sum(1 for v in ok.values() if v['tabs'] and v['agrupar']), com_colunas=sum(1 for v in ok.values() if v['tabs'] and v['colunas']),
         caixas_em_tabela=[(k, v['chk'], v['sel']) for k, v in ok.items() if v['chk']],
         etapas=[k for k, v in ok.items() if v['etapas']],
         formas_filtrar={k: dict(busca=v['busca'], barra=v['barSel'], rapido=v['rapido'], funil=v['hFun'], n=(1 if v['busca'] else 0) + (1 if v['barSel'] else 0) + (1 if v['rapido'] else 0) + (1 if v['hFun'] else 0)) for k, v in ok.items() if v['tabs']},
         notas=[(k, v['nNotas'], v['notas'][:3]) for k, v in ok.items() if v['nNotas']], erros_js=[(k, v['erros']) for k, v in ok.items() if v.get('erros')])
S['formas_hist'] = {}
for k, v in S['formas_filtrar'].items(): S['formas_hist'][v['n']] = S['formas_hist'].get(v['n'], 0) + 1
dump('p4_ex41_resumo.json', S)
log(L, 'RESUMO', json.dumps({k: (v if not isinstance(v, list) or len(v) < 12 else f'{len(v)} itens') for k, v in S.items() if k not in ('formas_filtrar', 'dis_exemplos', 'prim_rotulos')}, ensure_ascii=False))
log(L, 'FIM')
