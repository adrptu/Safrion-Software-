# -*- coding: utf-8 -*-
"""Sonda manual (Claude, revisão PR #89): teclado e toque na raia do Kanban da O.S., via CDP, com eventos de tecla com texto
(Enter = '\r', Espaço = ' ') e toque real (Input.dispatchTouchEvent), perfil e porta próprios (comp_lib.Chrome). Dados sintéticos.
Uso: GEN=<gen37> RENDER_DIR=<_render> SHOTS=<dir> [LAB_FECHADA=Abrir] python3 -B sonda_raia.py"""
import os, sys, time, json
G = os.environ['GEN']; sys.path.insert(0, G)
from comp_lib import Chrome, servir
R = os.environ['RENDER_DIR']; SH = os.environ.get('SHOTS', ''); LABF = os.environ.get('LAB_FECHADA', 'Expandir')
p, srv = servir(R); c = Chrome(); J = c.js
B = f'http://127.0.0.1:{p}/OS.dc.html'
res = []
def chk(n, cond, det=''):
    res.append(bool(cond)); print(('OK    ' if cond else 'FALHA ') + n + ' · ' + json.dumps(det, ensure_ascii=False)[:600], flush=True)
def tecla(key, code, vk, text):
    c.call('Input.dispatchKeyEvent', {'type': 'keyDown', 'key': key, 'code': code, 'windowsVirtualKeyCode': vk, 'text': text, 'unmodifiedText': text})
    c.call('Input.dispatchKeyEvent', {'type': 'keyUp', 'key': key, 'code': code, 'windowsVirtualKeyCode': vk}); time.sleep(.7)
CAB = "[...document.querySelectorAll('.os-raia-cab')].find(b=>b.querySelector('b').innerText.trim()===%s)"
EST = """(()=>{const b=%s; if(!b) return null; const sec=b.closest('.os-raia');
  return {exp:b.getAttribute('aria-expanded'), lab:b.getAttribute('aria-label'), txt:b.innerText.replace(/\\s+/g,' ').trim(),
    cards:[...sec.querySelectorAll('[role=list] [role=button][aria-label^=Abrir]')].filter(x=>x.offsetParent).length,
    foco:document.activeElement===b, mesmo:window.__b===b, fv:b.matches(':focus-visible'), q:location.search,
    abertas:[...document.querySelectorAll('.os-raia-cab')].map(x=>x.querySelector('b').innerText.trim()+'='+x.getAttribute('aria-expanded'))};})()"""
def est(nome): return J(EST % (CAB % json.dumps(nome)))
ATIVO = "(()=>{const a=document.activeElement; return a.closest('.os-raia-cab')?'cab '+a.querySelector('b').innerText.trim():(a.getAttribute('aria-label')||a.tagName).slice(0,40)})()"
try:
    c.aparelho(1440, 1000, 1, False); c.goto(B, .8); J("localStorage.clear();sessionStorage.clear()")
    c.goto(B + '?view=kanban&ag=onde', 1.6)
    e0 = est('T2'); q0 = J("location.search")
    chk('K0 raias abertas no início, aria-expanded=true, rótulo "Recolher raia …"', e0 and e0['exp'] == 'true' and (e0['lab'] or '').startswith('Recolher raia T2') and e0['cards'] > 0, e0)
    # foco pelo teclado: foco em T2, Shift+Tab (último cartão de T1) e Tab de volta a T2 (o :focus-visible é o do teclado)
    J("window.__b=%s; window.__b.focus()" % (CAB % json.dumps('T2'))); c.tab(1, shift=True); time.sleep(.2); c.tab(1); time.sleep(.2)
    e1 = est('T2'); chk('K1 Shift+Tab e Tab voltam a T2 com foco visível', e1 and e1['foco'] and e1['fv'], e1)
    tecla('Enter', 'Enter', 13, '\r'); e2 = est('T2')
    chk('K2 Enter recolhe T2: aria-expanded=false, sem cartões, foco no MESMO botão, endereço igual, outras raias abertas',
        e2 and e2['exp'] == 'false' and e2['cards'] == 0 and e2['foco'] and e2['mesmo'] and e2['q'] == q0
        and all(x.endswith('=true') for x in e2['abertas'] if not x.startswith('T2=')) and (e2['lab'] or '').startswith(LABF + ' raia T2'), e2)
    if SH: c.shot(os.path.join(SH, 'raia_t2_recolhida_1440.png'))
    c.tab(1); time.sleep(.2); t3 = J(ATIVO)
    chk('K3 com T2 recolhida, o Tab seguinte vai ao cabeçalho de T3, sem passar por cartão oculto', t3 == 'cab T3', t3)
    J("window.__b.focus()"); time.sleep(.1)
    tecla(' ', 'Space', 32, ' '); e3 = est('T2')
    chk('K4 Espaço expande T2: aria-expanded=true, os mesmos cartões, foco no mesmo botão', e3 and e3['exp'] == 'true' and e3['cards'] == e0['cards'] and e3['foco'] and e3['mesmo'], e3)
    # diagnóstico do F2 original do PR: c.tecla('Enter', vk=13) sem o texto '\r'
    c.tecla('Enter', vk=13); time.sleep(.7); e4 = est('T2')
    print('INFO  diagnóstico: Enter sem texto (F2 original do PR) deixa aria-expanded=' + str(e4 and e4['exp']) + ' (true = não acionou)', flush=True)
    if e4 and e4['exp'] == 'false': tecla(' ', 'Space', 32, ' ')
    # visão: Calendário e volta; recarregar (memória só da tela)
    tecla('Enter', 'Enter', 13, '\r')
    J("[...document.querySelectorAll('[data-visao]')].find(b=>b.getAttribute('data-visao')==='calendario').click()"); time.sleep(.8)
    J("[...document.querySelectorAll('[data-visao]')].find(b=>b.getAttribute('data-visao')==='kanban').click()"); time.sleep(.8)
    e5 = est('T2'); chk('K5 Calendário e volta ao Kanban: T2 continua recolhida', e5 and e5['exp'] == 'false', e5)
    c.goto(B + '?view=kanban&ag=onde', 1.6); e6 = est('T2')
    chk('K6 (registro) recarregar a página reabre T2 (estado só da tela, sem preferência gravada)', e6 and e6['exp'] == 'true', e6)
    chk('K7 sem erro de JS na página (cadc_lib.ERRS)', not J("(window.__errs||[]).length"), J("window.__errs"))
    # 390 px com toque real
    c.aparelho(390, 844, 2, True); c.goto(B + '?view=kanban&ag=onde', 1.6)
    m = J("""(()=>{const b=[...document.querySelectorAll('.os-raia-cab')].find(x=>x.offsetParent); b.scrollIntoView({block:'center'}); const r=b.getBoundingClientRect();
      return {nome:b.querySelector('b').innerText.trim(), w:Math.round(r.width), h:Math.round(r.height), x:r.left+r.width/2, y:r.top+r.height/2, exp:b.getAttribute('aria-expanded'), q:location.search,
        topo:document.elementFromPoint(r.left+r.width/2,r.top+r.height/2)?.closest('.os-raia-cab')===b};})()""")
    chk('T1 390 px: cabeçalho da raia com alvo ≥ 44 × 44 px, sem nada por cima', m['h'] >= 44 and m['w'] >= 44 and m['topo'], m)
    c.toque(m['x'], m['y']); time.sleep(.4); a = est(m['nome'])
    chk('T2 390 px: toque recolhe a raia (aria-expanded=false, sem cartões), sem navegar nem rolar a página de lado',
        a and a['exp'] == 'false' and a['cards'] == 0 and a['q'] == m['q'] and J("document.documentElement.scrollWidth<=innerWidth"), a)
    if SH: c.shot(os.path.join(SH, 'raia_recolhida_390.png'))
    m2 = J("""(()=>{const b=[...document.querySelectorAll('.os-raia-cab')].find(x=>x.offsetParent); const r=b.getBoundingClientRect(); return {x:r.left+r.width/2, y:r.top+r.height/2};})()""")
    c.toque(m2['x'], m2['y']); time.sleep(.4); a2 = est(m['nome'])
    chk('T3 390 px: segundo toque expande de novo', a2 and a2['exp'] == 'true' and a2['cards'] > 0, a2)
    chk('T4 sem erro de JS a 390 px', not J("(window.__errs||[]).length"), J("window.__errs"))
finally:
    c.close(); srv.terminate()
print(f'RESULTADO: {sum(res)}/{len(res)}')
sys.exit(0 if all(res) else 1)
