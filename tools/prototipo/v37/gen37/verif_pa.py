# -*- coding: utf-8 -*-
"""Verificação independente (Chrome) · planos-safra-07: casos-limite do gatilho 'Dias antes do plantio'."""
import sys, os, time, subprocess, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cdp import Chrome
from journeys import free
HERE = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(HERE, '_render'); p = free()
SHOT = sys.argv[1] if len(sys.argv) > 1 else HERE
srv = subprocess.Popen(['python3', '-m', 'http.server', str(p), '--bind', '127.0.0.1', '--directory', R], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)
c = Chrome(port=free()); J = c.js
CLK = """((t,root)=>{const r=root?document.querySelector(root):document; if(!r) return 'SEM RAIZ '+root; const n=s=>(s||'').replace(/\\s+/g,' ').trim(); const els=[...r.querySelectorAll('button,a')]; const e=els.find(x=>n(x.innerText)===t)||els.find(x=>n(x.innerText).startsWith(t))||els.find(x=>n(x.getAttribute('aria-label'))===t); if(!e) return 'NÃO ACHEI: '+t; e.click(); return 'ok';})"""
SETV = """((sel,val)=>{const i=document.querySelector(sel); if(!i) return 'sem '+sel; const P=i.tagName==='SELECT'?HTMLSelectElement.prototype:HTMLInputElement.prototype; Object.getOwnPropertyDescriptor(P,'value').set.call(i,val); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true})); return 'ok';})"""
T = lambda: J("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).filter(Boolean).join(' | ')")
DLG = lambda: J("!!document.querySelector('aside[role=dialog]')")
PT = lambda: (J("(document.querySelector('aside[role=dialog]')||{innerText:''}).innerText.replace(/\\s+/g,' ')") or '')
def clk(t, root=None): r = J(f"({CLK})({json.dumps(t)},{json.dumps(root)})"); time.sleep(.4); return r
def setv(sel, val): r = J(f"({SETV})({json.dumps(sel)},{json.dumps(val)})"); time.sleep(.25); return r
def atv(nome): J(f"[...document.querySelectorAll('main button')].find(b=>b.innerText==={json.dumps(nome)}).click()"); time.sleep(.4)
def gats(): return J("[...document.querySelectorAll('main b')].map(b=>b.innerText).filter(t=>/^DAP /.test(t))")
def err(): t = PT(); import re; m = re.search(r'(Use [^.]*\.|Informe os dias[^.]*\.)', t); return m.group(1) if m else ''
def say(*a): print(*a, flush=True)
def trysave(tipo, dias, nome='Herbicida pós-emergente'):
    atv(nome); setv('#fm_tipo', tipo); setv('#fm_dias', dias); clk('Salvar', 'aside[role=dialog]')
    if DLG():
        e = err(); say(f'  {tipo} {dias!r}: RECUSADO · {e}'); clk('Cancelar', 'aside[role=dialog]'); clk('Descartar alterações', 'aside[role=dialog]')
        if DLG(): J("document.querySelector('aside[role=dialog] button[aria-label=Fechar]')&&document.querySelector('aside[role=dialog] button[aria-label=Fechar]').click()")
        return None
    say(f'  {tipo} {dias!r}: SALVO · gatilhos DAP {gats()} · toast {T()[:80]}')
    return True
try:
    c.size(1440, 1100); c.goto(f'http://127.0.0.1:{p}/PA.dc.html')
    J("window.__errs=[]; window.addEventListener('error',e=>window.__errs.push(String(e.message)));")
    J("document.querySelector('button[aria-label=\"Abrir plano Soja alta tecnologia\"]').click()"); time.sleep(.5)
    say('gatilhos iniciais:', gats())
    say('grupos:', J("[...document.querySelectorAll('main h3')].map(h=>h.innerText+' :: '+(h.nextElementSibling?h.nextElementSibling.innerText:''))"))
    # novo: tipo padrão
    clk('Incluir atividade'); say('novo · tipo selecionado:', J("document.querySelector('#fm_tipo').value"), '· rótulo:', J("document.querySelector('#fm_tipo').selectedOptions[0].innerText")); clk('Cancelar', 'aside[role=dialog]')
    say('Casos (atividade Herbicida pós-emergente, DAP 25):')
    trysave('DAP', '-20')
    trysave('DAP', '−20')   # sinal de menos tipográfico (U+2212), o mesmo que a tela exibe em "DAP −20"
    trysave('DAP', '–15')   # meia-risca (U+2013)
    trysave('DAP', '2,5')
    trysave('DAP', '401')
    trysave('DAP', '400')
    trysave('DAPA', '181')
    trysave('DAPA', '180')
    trysave('DAPA', '0')
    atv('Herbicida pós-emergente'); say('reabrir após DAPA 0 → tipo', J("document.querySelector('#fm_tipo').value"), 'dias', J("document.querySelector('#fm_dias').value"), '· rótulo', J("document.querySelector('#fm_tipo').selectedOptions[0].innerText")); clk('Cancelar', 'aside[role=dialog]')
    trysave('DANC', '181')
    trysave('DAPC', '401')
    trysave('DAPC', '400')
    say('grupos no fim:', J("[...document.querySelectorAll('main h3')].map(h=>h.innerText)"))
    say('texto do grupo DAP:', J("(()=>{const h=[...document.querySelectorAll('main h3')].find(h=>/plantio/i.test(h.innerText)); return h? h.parentElement.innerText.split('\\n').slice(0,3).join(' | '):'';})()"))
    c.shot(os.path.join(SHOT, 'verif_pa.png'))
    say('erros JS:', J("window.__errs"))
finally:
    c.close(); srv.terminate()
