# -*- coding: utf-8 -*-
"""EX-54 · Frentes de trabalho na Ordem de Serviço (proprietário, 18/10/2026: "o agrupamento de OS e talhoes semelhantes ... esta muito ruim";
prompt-safrion-frentes-trabalho.md, aceite). Navegador real, dados sintéticos, 1440 e 390 px.
  F1 a visão "Frentes" existe no seletor da O.S. (ícone, nome acessível "Ver em frentes de trabalho") e abre pelo endereço ?view=frentes
  F2 Lagoa Grande: acaricida (abamectina, 5 pivôs, 2 caldas), fungicida (tebuconazol, 4 pivôs) e calagem (3 pivôs) viram frentes
  F3 a frente mostra porquê, rota numerada no mapa (números 1..N visíveis) e ganho em km e cargas contra cada O.S. sozinha
  F4 Santa Rita: OS-0421 e OS-0424 (Fungicida A) na mesma frente, com a diferença de adjuvante como troca de calda
  F5 Santa Rita: OS-0420 e OS-0431 (plantio de soja) na mesma frente
  F6 plantio e calcário não pedem pulverizador; fertirrigação fica fora (vai pelo pivô)
  F7 a O.S. sem vazão aparece com "Definir vazão" e a frente diz quem decide a aprovação; nada é aprovado, liberado ou reservado
  F8 "Agrupar N O.S. desta calda" abre a conferência do OS-LOTE com as O.S. na ordem da rota
  F9 sem erro de JavaScript e sem rolagem horizontal (1440 e 390)
Contraprova: o render da v134 não tem a visão Frentes (F1 a F8 reprovam).
Uso (de gen37/): env CHROME_BIN=… SAFRION_DADOS=sintetico [RENDER_DIR=…] python3 -B os_frentes_test.py"""
import json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, servir

R = os.environ.get('RENDER_DIR') or os.path.join(HERE, '_render')
OK = FAIL = 0
def chk(nome, cond, info=''):
    global OK, FAIL
    if cond: OK += 1; print('OK   ', nome)
    else: FAIL += 1; print('FALHA', nome, '·', str(info)[:500])

SEC = "document.querySelector('[data-os-frentes]')"
def txt(c): return c.js(f"({SEC}||{{}}).innerText||''") or ''
def faz(c, nome):
    c.js("(()=>{const e=document.querySelector('select[aria-label=\"Filtrar por fazenda\"]');if(!e)return;Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype,'value').set.call(e,%s);e.dispatchEvent(new Event('change',{bubbles:true}))})()" % json.dumps(nome)); time.sleep(1)
def card(c, titulo):
    return c.js("(()=>{const b=[...document.querySelectorAll('[data-os-frentes] .fr-card')].find(x=>x.innerText.includes(%s));if(!b)return false;b.click();return true})()" % json.dumps(titulo))

port, srv = servir(R)
try:
    for w, h in ((1440, 900), (390, 844)):
        P = f'{w}px · '
        c = Chrome(); c.aparelho(w, h, 1, w == 390)
        c.call('Page.addScriptToEvaluateOnNewDocument', {'source': "window.__e=[];addEventListener('error',e=>window.__e.push(String(e.message)))"})
        url = f'http://127.0.0.1:{port}/OS.dc.html'
        c.goto(url); c.js("localStorage.clear();localStorage.setItem('safrion.perfilDemo','Caio')"); c.goto(url, 1.5)
        tem_btn = c.js("!!document.querySelector('[data-visao=\"frentes\"][aria-label=\"Ver em frentes de trabalho\"]')") or c.js("!!document.querySelector('[data-visao-menu=\"frentes\"]')")
        c.goto(url + '?view=frentes', 1.6); faz(c, 'Lagoa Grande')
        chk(P + 'F1 visão Frentes no seletor e pelo endereço ?view=frentes', tem_btn and c.js(f"!!{SEC}&&{SEC}.offsetParent!==null"))
        t = txt(c)
        chk(P + 'F2 Lagoa Grande: frentes de abamectina (5 pivôs, 2 caldas), tebuconazol (4 pivôs) e calcário (3 pivôs)',
            'Abamectina 18 EC' in t and '5 pivôs' in t and '2 caldas' in t and 'Tebuconazol 200 EC' in t and '4 pivôs' in t and 'Calcário dolomítico filler' in t and '3 pivôs' in t, t[:700])
        nums = c.js("[...document.querySelectorAll('[data-os-frentes] .fr-n')].filter(x=>x.offsetParent!==null&&x.getBoundingClientRect().width>10).map(x=>x.textContent).sort().join(',')")
        chk(P + 'F3 porquê, rota numerada no mapa (1 a 5) e ganho em km e cargas contra cada O.S. sozinha',
            'Por que juntou' in t and nums == '1,2,3,4,5' and 'com cada O.S. sozinha' in t and 'cargas fechadas por O.S.' in t, [nums, t[t.find('Por que'):t.find('Por que') + 200]])
        faz(c, 'Santa Rita'); card(c, 'Fungicida A'); time.sleep(.5); t = txt(c)
        chk(P + 'F4 OS-0421 e OS-0424 (Fungicida A) na mesma frente, com o adjuvante como troca de calda',
            'OS-0421' in t and 'OS-0424' in t and 'Troca de calda' in t and 'Adjuvante espalhante' in t, t[:600])
        card(c, 'Soja'); time.sleep(.5); t = txt(c)
        chk(P + 'F5 OS-0420 e OS-0431 (plantio de soja) na mesma frente', 'PLANTIO' in t.upper() and 'OS-0420' in t and 'OS-0431' in t, t[:500])
        c.js(f"(()=>{{const d={SEC}&&{SEC}.querySelector('details');if(d)d.open=true}})()"); time.sleep(.2); t = txt(c)
        chk(P + 'F6 plantio e calcário sem "alocar pulverizador"; fertirrigação fora (vai pelo pivô)',
            'alocar pulverizador' not in t and 'OS-0418' in t and 'vai pelo pivô' in t, t[-600:])
        card(c, 'Glifosato'); time.sleep(.5); t = txt(c)
        nada = c.js("(()=>{const k=window.__cen&&window.__cen.cenGet&&window.__cen.cenGet();if(!k)return null;return ['OS-0595','OS-0596','OS-0597'].every(id=>k.ordens[id].etapa==='A liberar'&&!k.ordens[id].reservado&&!((k.ordens[id].osc||{}).ev||[]).length)})()")
        chk(P + 'F7 P1 sem vazão com "Definir vazão", quem decide a aprovação, nada aprovado, liberado ou reservado',
            'Definir vazão' in t and 'RT decide' in t and nada in (True, None), [nada, t[:600]])
        okb = c.js("(()=>{const b=[...document.querySelectorAll('[data-os-frentes] .fr-acoes button')].find(x=>x.innerText.startsWith('Agrupar 2 O.S. desta calda'));if(!b)return false;b.click();return true})()"); time.sleep(.8)
        dlg = "document.querySelector('aside[aria-label=\"Agrupamento de operações\"]')"
        dt = c.js(f"({dlg}||{{}}).innerText||''") or ''
        ordem = [x for x in ('OS-0595', 'OS-0596') if x in dt]
        chk(P + 'F8 "Agrupar 2 O.S. desta calda" abre a conferência do OS-LOTE com as O.S. da rota', okb and 'Conferir agrupamento' in dt and len(ordem) == 2, dt[:400])
        c.tecla('Escape', vk=27); time.sleep(.3)
        e = c.js('window.__e') or []; ov = c.js('document.documentElement.scrollWidth-innerWidth')
        chk(P + 'F9 sem erro de JavaScript e sem rolagem horizontal', not e and ov <= 1, [e, ov])
        c.shot(os.path.join(HERE, '_shots', f'os_frentes_{w}.png')) if os.path.isdir(os.path.join(HERE, '_shots')) else None
        c.close()
finally:
    srv.terminate()
print(f'RESULTADO: {OK}/{OK + FAIL} ok')
sys.exit(1 if FAIL else 0)
