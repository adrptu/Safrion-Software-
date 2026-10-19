# -*- coding: utf-8 -*-
"""EX-40.3 (AG-05 Validar + Publicar; e o passo único do fluxo vigente, Planos agronômicos) e EX-40.4 (AG-06 Propor melhoria × Propor revisão) · executado."""
import os, sys, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e40lib import S, clique, BTN, BTNC, LAB
s = S(); s.reset('Ana')
s.p('# EX-40.3 · AG-05 (oculta) · Validar e Publicar')
for perfil in ('Ana', 'Caio'):
    s.perfil(perfil); s.go('AG-05.dc.html', espera=1.2); s.cliques = 0
    vis = s.J("[...document.querySelectorAll('button,a,[role=menuitem]')].filter(b=>b.getClientRects().length).map(b=>(b.innerText||b.getAttribute('aria-label')||'').replace(/\\s+/g,' ').trim()).filter(t=>/Validar|Publicar/.test(t))")
    r1 = clique(s, BTN('Validar')); t1 = s.toast()
    r2 = clique(s, BTN('Publicar')); t2 = s.toast()
    sit = s.J("(()=>{const r=[...document.querySelectorAll('tr')].find(t=>t.innerText.includes('Feijão pivô v3'));return r?r.innerText.replace(/\\s+/g,' ').slice(0,200):'';})()")
    s.p(f"[{perfil}] botões visíveis {vis} · Validar {r1}: {t1!r}")
    s.p(f"   Publicar {r2}: {t2!r}")
    s.p(f"   linha depois dos dois cliques: {sit!r} · cliques {s.cliques}")
    if perfil == 'Ana': s.shot('p3_AG-05.png')
s.p('\n# Fluxo vigente: Planos agronômicos (PA, no menu) · mudar a dose de Fungicida A e "Salvar alterações"')
def mudar_dose(val):
    if s.J(f"!!{LAB('Mostrar insumos de Fungicida 1ª aplicação')}"): clique(s, LAB('Mostrar insumos de Fungicida 1ª aplicação'), .5)
    clique(s, LAB('Alterar a dose de Fungicida A'), .4)
    s.J("document.activeElement&&document.activeElement.select&&document.activeElement.select()")
    s.c.call('Input.insertText', {'text': val}); time.sleep(.2); s.c.tecla('Enter', 'Enter', 13, text='\r'); time.sleep(.6)
for perfil, val in (('Caio', '0,6'), ('Rui', '0,7')):
    s.reset(perfil); s.go('PA.dc.html#plano=SOJA-AT', espera=1.5); s.cliques = 0
    mudar_dose(val); ta = s.toast()
    prim = s.J("[...document.querySelectorAll('button')].filter(b=>b.getClientRects().length&&getComputedStyle(b).backgroundColor==='rgb(30, 122, 76)').map(b=>(b.innerText||'').replace(/\\s+/g,' ').trim())")
    r = clique(s, BTNC('Salvar alterações'), .8); tb = s.toast()
    ver = s.J("(document.body.innerText.match(/v\\d+ (publicada|em vigor)[^\\n]{0,60}/)||[''])[0]")
    s.p(f"[{perfil}] dose {val}: aviso {ta!r} · primárias {prim} · Salvar {r}: {tb!r} · cliques {s.cliques}")
    s.shot(f'p3_PA_{perfil}.png')
s.p('\n# EX-40.4 · AG-06 (oculta) · Propor melhoria × Propor revisão')
s.reset('Ana')
for rot in ('Propor melhoria', 'Propor revisão'):
    s.go('AG-06.dc.html', espera=1.2)
    href = s.J(f"(()=>{{const e={BTN(rot)}; return e?(e.getAttribute('href')||'(botão)'):null;}})()")
    ctx = s.J(f"(()=>{{const e={BTN(rot)}; if(!e) return ''; const tr=e.closest('tr'); return tr?tr.innerText.replace(/\\s+/g,' ').slice(0,160):'bloco: '+(e.closest('section,div')||{{}}).innerText.replace(/\\s+/g,' ').slice(0,100);}})()")
    r = clique(s, BTN(rot), 1.2)
    dest = s.J("location.pathname.split('/').pop()+' · '+((document.querySelector('h1')||{}).innerText||'')")
    s.p(f"{rot}: href {href} · contexto {ctx!r} → abre {dest}")
s.p(f"erros JS: {s.errs()}")
s.fim('p3_agro.log')
