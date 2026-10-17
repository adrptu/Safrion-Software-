"""R2 · S4f: depois de agrupar pela tela, a seção Origem do detalhe da O.S. (aberta como a pessoa abriria) informa o grupo e a versão.
Uso: GEN37=<gen37> RENDER_DIR=<render> python3 -B origem_grupo_test.py"""
import json, os, sys, time
G = os.environ['GEN37']; sys.path.insert(0, G)
from comp_lib import Chrome, servir
R = os.environ['RENDER_DIR']; porta, srv = servir(R); c = None; res = []
D = 'document.querySelector(\'aside[aria-label="Agrupamento de operações"]\')'
def ok(n, v, info=''): res.append(bool(v)); print(('OK    ' if v else 'FALHA ') + n + ('' if v else ' · ' + str(info)[:400]), flush=True)
try:
    c = Chrome(); c.aparelho(1440, 900); url = f'http://127.0.0.1:{porta}/OS.dc.html'
    c.goto(url); c.js("localStorage.setItem('safrion.perfilDemo','Caio')"); c.goto(url)
    c.js("(()=>{const e=document.querySelector('select[aria-label=\"Filtrar por fazenda\"]');Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype,'value').set.call(e,'Lagoa Grande');e.dispatchEvent(new Event('change',{bubbles:true}))})()"); time.sleep(.8)
    c.js("[...document.querySelectorAll('button')].find(b=>b.innerText.trim()==='Agrupar operações compatíveis').click()"); time.sleep(.6)
    for oid in ('OS-0590', 'OS-0591'): c.js(D + ".querySelector('input[aria-label^=\"%s ·\"]').click()" % oid); time.sleep(.3)
    for t in ('Conferir agrupamento', 'Confirmar agrupamento'):
        c.js("[...%s.querySelectorAll('button')].find(b=>b.innerText.trim()===%s).click()" % (D, json.dumps(t))); time.sleep(.6)
    ok('grupo criado pela tela', c.js("Object.keys(window.__cen.cenGet().gruposExec||{}).join()") == 'GRP-1')
    c.js(D + ".querySelector('header button').click()"); time.sleep(.3)
    c.goto(url + '#OS-0590'); time.sleep(.9)
    c.js("[...document.querySelectorAll('aside[role=dialog] section[aria-label] > button[aria-expanded=\"false\"]')].forEach(b=>b.click())"); time.sleep(.5)
    pan = c.js("(()=>{const a=document.querySelector('aside[role=dialog]');return a?a.innerText.replace(/\\s+/g,' '):''})()") or ''
    i = pan.find('GRP-1'); ok('Origem do detalhe informa "Grupo de execução GRP-1 · v1"', 'Grupo de execução GRP-1 · v1' in pan, pan[max(0, i - 80):i + 200] if i >= 0 else pan[-400:])
    ok('sem exceções JavaScript', not c.js('(window.__errs||[]).length'), c.js('window.__errs'))
finally:
    if c: c.close()
    srv.terminate()
print(f'RESULTADO {sum(res)}/{len(res)}')
