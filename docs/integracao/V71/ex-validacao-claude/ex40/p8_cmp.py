# -*- coding: utf-8 -*-
"""EX-40.11 · contrato formal × "Aprovar e emitir pedido": o que o fluxo vigente (Compras, no menu) faz na aprovação; onde fica o
"Formalizar contrato" (SU-05, oculta) · executado. Perfil Ana (Gerente da fazenda na alçada de compra de demonstração)."""
import os, sys, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e40lib import S, G, clique, BTN, BTNC
sys.path.insert(0, G)
from comp_lib import IR_ETAPA
s = S(); s.reset('Ana')
s.go('CMP.dc.html', espera=2.2); time.sleep(.6)
s.p('# EX-40.11 · Compras › Insumos da safra · etapa 5 (render b87f79b, Ana)')
ab = clique(s, BTNC('Abrir compra'), 1.2)
r0 = s.J(f"({IR_ETAPA})(3)"); time.sleep(.6); cv = clique(s, BTNC('Enviar convites'), 1.2); tcv = s.toast()
r = s.J(f"({IR_ETAPA})(5)"); time.sleep(.8)
s.p(f"Abrir compra: {ab} · etapa 3: {r0} · Enviar convites: {cv} → {tcv[:200]!r}")
alc = s.J("(document.body.innerText.match(/(Valor da compra|Valor dentro|Acima da sua|Exigida|Alçada de aprovação)[^\\n]{0,220}/g)||[]).slice(0,6)")
prim = s.J("[...document.querySelectorAll('button')].filter(b=>b.getClientRects().length&&getComputedStyle(b).backgroundColor==='rgb(30, 122, 76)').map(b=>(b.innerText||'').replace(/\\s+/g,' ').trim())")
prev = s.J("(document.body.innerText.match(/PC-\\d+ \\(prévia\\)[^\\n]{0,80}/g)||[]).slice(0,4)")
s.p(f"ir à etapa 5: {r} · primária(s) {prim}"); s.p(f"  alçada: {alc}"); s.p(f"  prévia de pedidos: {prev}")
s.shot('p8_CMP_etapa5.png')
txt5 = s.J("(()=>{const n=x=>(x||'').replace(/\\s+/g,' ').trim(); return n(document.querySelector('main').innerText).slice(0,1600);})()")
s.p(f"  etapa 5 (texto): {txt5!r}")
# reduzir para caber na alçada da Ana não é necessário para provar o desenho: lemos o texto do botão e o que a confirmação diz no código
# materiais: SC-039 (reposição) em cotação
s.go('CMP.dc.html#tipo=materiais&sc=SC-039', espera=2.2); time.sleep(.8)
pan = s.J("(()=>{const d=[...document.querySelectorAll('aside[role=dialog],[role=dialog],aside')].find(e=>e.getClientRects().length&&/SC-039/.test(e.innerText)); return d?d.innerText.replace(/\\s+/g,' ').slice(0,900):(document.body.innerText.match(/SC-039[^\\n]{0,200}/)||[''])[0];})()")
s.p(f"\n# Compras › Materiais · SC-039 (reposição, Em cotação): {pan!r}")
emit = s.J("[...document.querySelectorAll('button')].filter(b=>b.getClientRects().length&&/^Emitir pedido/.test((b.innerText||'').trim())).map(b=>(b.innerText||'').replace(/\\s+/g,' ').trim()+(b.disabled?' (desabilitado)':''))")
s.p(f"  botão: {emit}"); s.cliques = 0
r1 = clique(s, BTNC('Emitir pedido'), 1.0); t = s.toast()
s.p(f"  clique ({r1}) → {t!r} · cliques {s.cliques}")
s.shot('p8_CMP_SC-039.png')
# perfil sem alçada (Rui)
s.reset('Rui'); s.go('CMP.dc.html#tipo=materiais&sc=SC-039', espera=2.2); time.sleep(.8)
emit = s.J("[...document.querySelectorAll('button')].filter(b=>b.getClientRects().length&&/^Emitir pedido/.test((b.innerText||'').trim())).map(b=>(b.innerText||'').replace(/\\s+/g,' ').trim()+(b.disabled?' (desabilitado)':'')+' · '+(b.title||b.getAttribute('data-dica')||''))")
s.p(f"  [Rui] botão: {emit}")
# SU-05 (oculta)
s.reset('Ana'); s.go('SU-05.dc.html', espera=1.6)
su = s.J("(document.body.innerText.match(/(Formalizar contrato|Emitir pedido|Alçada|alçada)[^\\n]{0,160}/g)||[]).slice(0,8)")
s.p(f"\n# SU-05 (oculta, 2 saltos): {su}")
s.p(f"erros JS: {s.errs()}")
s.fim('p8_cmp.log')
