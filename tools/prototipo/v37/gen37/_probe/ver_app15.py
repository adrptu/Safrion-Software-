# -*- coding: utf-8 -*-
"""Verificador App 15: vários quadros abertos ao mesmo tempo (iframes na mesma origem, como no Canvas) — um muda, os outros atualizam; Restaurar."""
import sys, os, time, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ver_app_lib import V, CLK, SETV
v = V()
F = ['MB-01', 'MB-03', 'MB-04', 'MB-05', 'MB-02det']
def fj(i, expr):
    return v.J(f"(()=>{{const w=window.document.querySelectorAll('iframe')[{i}].contentWindow; const document=w.document; return ({expr});}})()")
def fclk(i, t):
    r = v.J(f"(()=>{{const document=window.document.querySelectorAll('iframe')[{i}].contentWindow.document; return ({CLK})({json.dumps(t)});}})()")
    time.sleep(.5); return r
def fset(i, sel, val):
    r = v.J(f"(()=>{{const w=window.document.querySelectorAll('iframe')[{i}].contentWindow; const document=w.document; const HTMLInputElement=w.HTMLInputElement, HTMLTextAreaElement=w.HTMLTextAreaElement, Event=w.Event; return ({SETV})({json.dumps(sel)},{json.dumps(val)});}})()")
    time.sleep(.2); return r
def foot(i):
    return fj(i, "(()=>{const m=document.querySelector('main'); const f=m&&m.nextElementSibling; return f?[...f.querySelectorAll('a,button')].filter(e=>e.offsetParent!==null).map(e=>e.innerText.trim()).join(' | '):'';})()")
def hdr(i): return fj(i, "document.querySelector('header').innerText.replace(/\\s+/g,' ')")
def main(i): return fj(i, "document.querySelector('main').innerText.replace(/\\n/g,' / ')")
try:
    v.c.goto(f'http://127.0.0.1:{v.p}/', wait=0.6)
    v.J("document.body.innerHTML=" + json.dumps(''.join(f'<iframe src="{t}.dc.html" style="width:390px;height:1800px;border:0"></iframe>' for t in F)))
    time.sleep(3.5)
    print('  inicial:', [foot(i) for i in range(len(F))])
    print('  B iniciar:', fclk(1, 'Iniciar turno · OS-0421'))
    time.sleep(.6)
    print('  depois iniciar:', [foot(i) for i in range(len(F))])
    v.ok(foot(0) == 'Fechar turno · OS-0421' and foot(4) == 'Fechar turno', 'MB-01 e MB-02det atualizam quando MB-03 inicia o turno')
    print('  A sem sinal:', fclk(0, 'Sem sinal')); time.sleep(.4)
    print('  B sinal:', fj(1, "[...document.querySelectorAll('[role=group] button')].map(b=>b.innerText+'='+b.getAttribute('aria-pressed')).join(', ')"))
    fset(1, '#ft_ha', '60'); fset(1, '#ft_h', '5'); print('  B fechar:', fclk(1, 'Fechar turno')); time.sleep(.5)
    print('  hdrs:', hdr(0), '||', hdr(3), '||', hdr(4))
    v.ok('1 aguardando sinal' in hdr(0), 'MB-01 mostra 1 aguardando sinal após fechar no MB-03')
    fset(2, '#oc_txt', 'Teste de ocorrência'); print('  C registrar:', fclk(2, 'Registrar ocorrência')); time.sleep(.4)
    print('  C main:', main(2)[:300])
    print('  B main (resumo):', main(1)[:300])
    # Restaurar no MB-01
    print('  A restaurar:', fclk(0, 'Restaurar demonstração')); time.sleep(.8)
    print('  pós-restaurar foots:', [foot(i) for i in range(len(F))])
    print('  pós B main:', main(1)[:400])
    print('  pós C main:', main(2)[:400], '| hdr', hdr(2))
    b1 = main(1); c1 = main(2)
    v.ok('Turno fechado' not in b1, 'MB-03 aberto em outro quadro não mostra turno fechado que o Restaurar apagou')
    v.ok('Voltar à fila' not in foot(2) or 'OC-501' not in c1, 'MB-04 aberto em outro quadro não mostra ocorrência que o Restaurar apagou')
    print('  erros:', [fj(i, "window.__errs||null") for i in range(len(F))])
finally:
    v.fim()
