# -*- coding: utf-8 -*-
"""EX-40.7 (PCOM: "Colunas" e "Tabela | Cartões" duas vezes) e EX-40.8 (CD-04: formas de filtrar) · executado."""
import os, sys, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e40lib import S, clique, BTN, BTNC
s = S(); s.reset('Ana')
s.go('PCOM.dc.html', espera=1.8)
d = s.J("""(()=>{const n=x=>(x||'').replace(/\\s+/g,' ').trim(); const vis=e=>e.getClientRects().length>0;
  const ctl=[...document.querySelectorAll('button,[role=tab],select,summary')].filter(vis).map(b=>n(b.innerText||b.getAttribute('aria-label'))).filter(t=>/^Colunas|Tabela|Cartões|Agrupar por/.test(t));
  const grupos=[...document.querySelectorAll('[data-visoes-gid]')].filter(vis).map(e=>e.getAttribute('data-visoes-gid'));
  const linhas=['g_of','g_pr'].map(g=>[g,[...document.querySelectorAll('[data-gid=\"'+g+'\"] tbody tr, #'+g+' tbody tr')].length]);
  return {ctl,grupos,linhas,blocos:[...document.querySelectorAll('h2')].filter(vis).map(e=>n(e.innerText))};})()""")
s.p('# EX-40.7 · PCOM (render b87f79b, Ana, 1440)'); s.p(json.dumps(d, ensure_ascii=False))
nc = s.J("[...document.querySelectorAll('[data-visao]')].filter(e=>e.getClientRects().length).map(e=>e.getAttribute('data-visao'))")
s.p(f"   'Colunas' visíveis: {s.conta('Colunas')} · botões de visão visíveis: {nc}")
s.shot('p5_PCOM.png')
# outras telas com duas listas no mesmo corpo (mesmo padrão): contar barras de visão por tela do menu
cont = {}
for f in ('PCOM.dc.html', 'VEN.dc.html', 'EXPED.dc.html', 'PROD.dc.html', 'EST.dc.html', 'CMP.dc.html', 'COLH.dc.html', 'CARGA.dc.html', 'IR-01.dc.html', 'AG-02.dc.html', 'GE-03.dc.html', 'IC.dc.html', 'IV.dc.html', 'OS.dc.html', 'AG-01.dc.html', 'GE-02.dc.html', 'PSUP.dc.html', 'PAGR.dc.html', 'PMAN.dc.html'):
    s.go(f, espera=1.2)
    cont[f] = s.J("[...document.querySelectorAll('button')].filter(b=>b.getClientRects().length&&/^Colunas/.test((b.innerText||b.getAttribute('aria-label')||'').trim())).length")
s.p(f"   barras com 'Colunas' visíveis por tela (estado inicial): {cont}")
s.p('\n# EX-40.8 · CD-04 Pessoas e equipes (aba Pessoas)')
s.go('CD-04.dc.html', espera=1.8)
d = s.J("""(()=>{const n=x=>(x||'').replace(/\\s+/g,' ').trim(); const vis=e=>e.getClientRects().length>0;
  const chips=[...document.querySelectorAll('.cadx-qf button[aria-pressed]')].filter(vis).map(b=>n(b.innerText));
  const sel=[...document.querySelectorAll('select[aria-label=\"Função\"]')].filter(vis).map(x=>[...x.options].map(o=>n(o.text)));
  const ag=[...document.querySelectorAll('[data-g2agb]')].filter(vis).map(b=>b.getAttribute('data-g2agb')+': '+n(b.innerText));
  const fun=[...document.querySelectorAll('button')].filter(b=>vis(b)&&/^Filtrar /.test(b.getAttribute('aria-label')||'')).map(b=>b.getAttribute('aria-label'));
  const busca=[...document.querySelectorAll('input[type=search],input[placeholder*=Buscar],input[aria-label*=Buscar]')].filter(vis).length;
  return {chips,funcao:sel,agrupar:ag,funis:fun,busca};})()""")
s.p(json.dumps(d, ensure_ascii=False))
# itens do "Agrupar por" da grade de pessoas
r = s.J("(()=>{const b=[...document.querySelectorAll('[data-g2agb=\"g_pes\"]')].find(e=>e.getClientRects().length); if(!b) return 'sem Agrupar por'; b.click(); return 'aberto';})()"); time.sleep(.4)
it = s.J("[...document.querySelectorAll('[data-g2agm=\"g_pes\"] [role=menuitemradio]')].map(x=>(x.innerText||'').replace(/\\s+/g,' ').trim())")
s.p(f"   Agrupar por (g_pes): {r} · itens {it}")
s.c.tecla('Escape', 'Escape', 27); time.sleep(.3)
s.shot('p5_CD-04.png')
# medida: achar os caldeiros pelos três caminhos (cliques)
s.go('CD-04.dc.html', espera=1.5); s.cliques = 0
clique(s, "[...document.querySelectorAll('.cadx-qf button[aria-pressed]')].find(b=>b.getClientRects().length&&/Caldeiro/.test(b.innerText))")
n1 = s.J("[...document.querySelectorAll('tbody tr')].filter(t=>t.getClientRects().length).length"); c1 = s.cliques
s.p(f"   chip 'Caldeiros': {c1} clique(s) · linhas visíveis {n1}")
s.go('CD-04.dc.html', espera=1.5)
val = s.J("(()=>{const x=[...document.querySelectorAll('select[aria-label=\"Função\"]')].find(e=>e.getClientRects().length); if(!x) return null; const o=[...x.options].find(o=>/aldeir/.test(o.text)); return o?o.value:null;})()")
s.p(f"   lista 'Função' tem caldeiro? valor {val!r}")
s.p(f"erros JS: {s.errs()}")
s.fim('p5_pcom_cd04.log')
