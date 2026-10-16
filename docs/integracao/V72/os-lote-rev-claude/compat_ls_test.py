"""Revisão Claude do PR #88 · cenário salvo pela base continua legível na candidata (mesma origem, mesmo perfil Chrome descartável).
1) serve o _render da BASE numa porta fixa, grava uma mudança real (liberar OS-0430 como Ana, pela própria página) e guarda o JSON salvo;
2) troca o servidor para o _render da CANDIDATA na MESMA porta e abre a O.S.: confere que o salvo não foi descartado nem reescrito ao abrir,
   que a mudança da base aparece, que a tela abre sem exceção e que um novo comando grava preservando o que já existia.
Uso: GEN37=<gen37 da candidata> BASE_RENDER=<dir> CAND_RENDER=<dir> SAIDA=<dir> python3 -B compat_ls_test.py"""
import json, os, sys, time, subprocess, hashlib
G = os.environ['GEN37']; sys.path.insert(0, G)
from comp_lib import Chrome
from journeys import free
SAIDA = os.environ.get('SAIDA', '.'); res = []
CEN_LS = 'talhao-os-cenario-v1'
def ok(n, v, info=''):
    res.append(dict(n=n, ok=bool(v), info=str(info)[:500])); print(('OK    ' if v else 'FALHA ') + n + ('' if v else ' · ' + str(info)[:500]), flush=True)
porta = free(); srv = None; c = None
def serve(d):
    global srv
    if srv: srv.terminate(); srv.wait(5)
    srv = subprocess.Popen(['python3', '-m', 'http.server', str(porta), '--bind', '127.0.0.1', '--directory', d], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(.7)
try:
    url = f'http://127.0.0.1:{porta}/OS.dc.html'
    serve(os.environ['BASE_RENDER']); c = Chrome(); c.aparelho(1440, 900)
    c.goto(url); c.js("localStorage.setItem('safrion.perfilDemo','Ana')"); c.goto(url)
    r = c.js("(()=>{const X=window.__cen;const r=X.cenMudar(null,k=>X.osc_liberar(k,'OS-0430',false,'','Ana'));return r.erro||r.msg})()")
    salvo = c.js("localStorage.getItem(%s)" % json.dumps(CEN_LS)) or ''
    h0 = hashlib.sha256(salvo.encode()).hexdigest()[:16]
    ok('base: comando real gravou o cenário (OS-0430 liberada)', '"OS-0430"' in salvo and json.loads(salvo)['ordens']['OS-0430']['etapa'] == 'Liberadas', r)
    ok('base: cenário salvo não tem as origens de demonstração', 'OS-0590' not in salvo)
    serve(os.environ['CAND_RENDER']); c.goto(url); time.sleep(.8)
    depois = c.js("localStorage.getItem(%s)" % json.dumps(CEN_LS)) or ''
    ok('candidata: abrir a tela não reescreve nem descarta o salvo da base', hashlib.sha256(depois.encode()).hexdigest()[:16] == h0, [h0, len(salvo), len(depois)])
    ok('candidata: lê a mudança da base (OS-0430 Liberadas pela cenGet)', c.js("window.__cen.cenGet().ordens['OS-0430'].etapa") == 'Liberadas')
    ok('candidata: sem exceção ao abrir com o salvo antigo', not c.js('(window.__errs||[]).length'), c.js('window.__errs'))
    filtro = c.js("(()=>{const e=document.querySelector('select[aria-label=\"Filtrar por fazenda\"]');Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype,'value').set.call(e,'Lagoa Grande');e.dispatchEvent(new Event('change',{bubbles:true}));return true})()"); time.sleep(.6)
    c.js("[...document.querySelectorAll('button')].find(b=>b.innerText.trim()==='Agrupar operações compatíveis')?.click()"); time.sleep(.6)
    t = c.js("(()=>{const d=document.querySelector('aside[aria-label=\"Agrupamento de operações\"]');return d?d.innerText.replace(/\\s+/g,' '):'(sem painel: perfil sem papel)'})()")
    ok('candidata: painel de agrupamento abre com salvo antigo (sem origens de demonstração) e sem exceção', 'OS-0590' not in (t or '') and not c.js('(window.__errs||[]).length'), (t or '')[:300])
    r2 = c.js("(()=>{const X=window.__cen;const r=X.cenMudar(null,k=>X.osc_liberar(k,'OS-0431',false,'','Ana'));return r.erro||r.msg})()")
    final = json.loads(c.js("localStorage.getItem(%s)" % json.dumps(CEN_LS)) or '{}')
    ok('candidata: novo comando grava preservando a mudança da base', final.get('ordens', {}).get('OS-0430', {}).get('etapa') == 'Liberadas' and final.get('rev', 0) > json.loads(salvo).get('rev', 0), [r2, final.get('rev')])
finally:
    if c: c.close()
    if srv: srv.terminate()
    open(os.path.join(SAIDA, 'compat_ls.json'), 'w').write(json.dumps(res, ensure_ascii=False, indent=1))
print(f'RESULTADO {sum(r["ok"] for r in res)}/{len(res)}')
