# -*- coding: utf-8 -*-
"""EX-42 · 390 × 844 com toque: arrastar a barra de tempo com o dedo, tocar no ícone de manejo e "Hoje" (pub.html = insumo no esqueleto do Artifact)."""
import os, sys, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from base import chrome, server, dump, log, OUT, PNG
SERVE = '/tmp/claude-0/-home-user-Safrion-Software-/65558514-68d9-57f5-9da3-513cd6735cdc/scratchpad/ex42_proto'
L = open(os.path.join(OUT, 'p1b_toque.log'), 'w', encoding='utf-8'); R = {}
port = server(SERVE, utf8=True); c = chrome(); J = c.js
c.aparelho(390, 844, 2, True); c.goto(f'http://127.0.0.1:{port}/pub.html', .8); J("try{localStorage.clear()}catch(e){};1"); c.goto(f'http://127.0.0.1:{port}/pub.html', 1.2)
dia = lambda: J("+document.getElementById('tl').getAttribute('aria-valuenow')")
J("document.getElementById('tl').scrollIntoView({block:'center'});1"); time.sleep(.3)
r = json.loads(J("JSON.stringify(document.getElementById('tl').getBoundingClientRect())")); R['tl_rect'] = r
svg = json.loads(J("JSON.stringify(document.querySelector('#tl svg').getBoundingClientRect())")); R['svg_rect'] = svg
y = r['y'] + 40; x0 = r['x'] + r['width'] * .8
R['alvo_no_ponto'] = J(f"(e=>e?(e.id||e.tagName)+'|'+(e.closest('#tl')?'dentro do #tl':'fora'):null)(document.elementFromPoint({x0},{y}))")
d0 = dia(); traj = []
c.call('Input.dispatchTouchEvent', {'type': 'touchStart', 'touchPoints': [{'x': x0, 'y': y}]}); time.sleep(.15); traj.append(dia())
for k in range(1, 8):
    c.call('Input.dispatchTouchEvent', {'type': 'touchMove', 'touchPoints': [{'x': x0 - 20 * k, 'y': y}]}); time.sleep(.1); traj.append(dia())
c.call('Input.dispatchTouchEvent', {'type': 'touchEnd', 'touchPoints': []}); time.sleep(.3)
R['arrasto_dedo'] = dict(antes=d0, trajetoria=traj, depois=dia(), scrollY=J('scrollY')); log(L, 'arrasto dedo', R['arrasto_dedo'], R['alvo_no_ponto'])
c.shot(os.path.join(PNG, 'proto_390_linha_do_tempo.png'))
# toque simples numa data (alternativa a arrastar com um ponteiro)
c.toque(r['x'] + r['width'] * .3, y); R['toque_simples'] = dia(); log(L, 'toque simples ->', R['toque_simples'])
# Hoje
J("[...document.querySelectorAll('button')].find(b=>b.innerText.trim()==='Hoje').click();1"); time.sleep(.3); R['hoje'] = dia()
# toque num ícone de manejo (22 px)
e = json.loads(J("JSON.stringify((b=>{const r=b.getBoundingClientRect(); return {x:r.x+r.width/2,y:r.y+r.height/2,w:r.width,h:r.height,l:b.getAttribute('aria-label')};})(document.querySelector('#tlbox > .evt.def')))"))
c.toque(e['x'], e['y']); time.sleep(.4)
R['icone'] = dict(caixa=[round(e['w']), round(e['h'])], label=e['l'], pop=(J("(p=>p?p.innerText.replace(/\\s+/g,' ').slice(0,400):'')(document.querySelector('.pop'))") or ''),
                  pop_rect=J("(p=>p?(r=>[Math.round(r.left),Math.round(r.right),Math.round(r.top),Math.round(r.bottom)])(p.getBoundingClientRect()):null)(document.querySelector('.pop'))"))
c.shot(os.path.join(PNG, 'proto_390_pop_icone.png')); log(L, 'ícone', R['icone'])
R['erros_js'] = J("window.__errs||[]"); dump('p1b_toque.json', R); log(L, 'FIM')
