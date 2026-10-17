# -*- coding: utf-8 -*-
"""EDL-01 · medição de cliques e digitação antes × depois (AGENTS §3.3), no navegador, com cliques reais do mouse (CDP) e teclas contadas.
Cenário (dados sintéticos): Safra 2027/28 nova da Santa Rita; planejar os talhões livres (T1, T2, T3, T4, P1 e P2; T7 e C1 seguem com o
perene de outra safra) com Soja · 58 W · Soja alta tecnologia · plantio 15/10/2027 e a meta de cada talhão (64, 62, 63, 60, 66, 65 sc/ha).
  A (antes)  painel por talhão: "Planejar ›" na linha, campos do formulário e Salvar, talhão a talhão
  B (depois) "Editar talhões…": marcar todas, "Aplicar aos marcados" com cultura, variedade, plantio e plano; metas digitadas na coluna com
             Enter descendo; Salvar
  C (depois) "Editar talhões…": colar o bloco da planilha (6 linhas × 5 colunas) na 1ª célula de cultura; Salvar
Conta: clique = um clique do mouse (abrir lista do DS e escolher a opção são 2); tecla = um caractere digitado, Enter ou Ctrl+V. Escolher
o campo para digitar é 1 clique. Criar a safra fica fora da conta (igual nos três). Confere que A, B e C gravam os mesmos cultivos.
Uso: python3 -B saf_lote_medida.py [--json saida.json]"""
import sys, os, time, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, servir
R = os.environ.get('RENDER_DIR') or os.path.join(HERE, '_render')
ALVO = dict(cult='Soja', var='58 W', plano='SOJA-AT', plantio='2027-10-15')
METAS = {'T1': '64', 'T2': '62', 'T3': '63', 'T4': '60', 'P1': '66', 'P2': '65'}
q = json.dumps
p, srv = servir(R); c = Chrome(); J = c.js
CONTA = {'cliques': 0, 'teclas': 0}
def esp(t=.45): time.sleep(t)
def centro(expr):
    return J(f"(()=>{{const e={expr}; if(!e) return null; e.scrollIntoView({{block:'center',inline:'nearest'}}); const r=e.getBoundingClientRect(); return [r.left+r.width/2, r.top+r.height/2];}})()")
def clique(expr, conta=True):
    xy = centro(expr)
    if not xy: raise RuntimeError('não achei: ' + expr[:160])
    for t in ('mousePressed', 'mouseReleased'):
        c.call('Input.dispatchMouseEvent', {'type': t, 'x': xy[0], 'y': xy[1], 'button': 'left', 'clickCount': 1})
    if conta: CONTA['cliques'] += 1
    esp()
def escolhe(expr_sel, valor):   # lista do DS no computador: abrir e escolher a opção (2 cliques)
    clique(expr_sel)
    txt = J(f"(()=>{{const s={expr_sel}; const o=[...s.options].find(o=>o.value==={q(valor)}); return o?o.textContent:null;}})()")
    clique(f"[...document.querySelectorAll('.g2dsel [role=option]')].find(o=>o.textContent.replace('✓','').trim()===({q(txt)}||'').trim())")
def digita(expr, txt, clicar=True):   # escolher o campo (1 clique) e digitar por cima (o foco seleciona o número; no texto, seleciona tudo antes)
    if clicar: clique(expr)
    J(f"(()=>{{const e={expr}; e.focus(); e.select&&e.select();}})()")
    c.call('Input.insertText', {'text': txt}); CONTA['teclas'] += len(txt); esp(.35)
def data(expr, iso):   # campo de data: 1 clique e 8 dígitos (ddmmaaaa); o valor entra pelo próprio campo
    clique(expr); CONTA['teclas'] += 8
    J(f"""(()=>{{const e={expr}; Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(e,{q(iso)}); e.dispatchEvent(new Event('input',{{bubbles:true}})); e.dispatchEvent(new Event('change',{{bubbles:true}}));}})()"""); esp(.35)
def tecla(k):
    vk = {'Enter': 13}[k]; c.call('Input.dispatchKeyEvent', {'type': 'keyDown', 'key': k, 'code': k, 'windowsVirtualKeyCode': vk, 'text': '\r'})
    c.call('Input.dispatchKeyEvent', {'type': 'keyUp', 'key': k, 'code': k, 'windowsVirtualKeyCode': vk}); CONTA['teclas'] += 1; esp(.4)
def nova_safra():
    c.aparelho(1440, 900, 1, False); c.call('Page.bringToFront')
    c.goto(f'http://127.0.0.1:{p}/Main.dc.html', .2); J("localStorage.clear();sessionStorage.clear()")
    c.goto(f'http://127.0.0.1:{p}/SAF.dc.html', 1.6); esp(.8)
    J("[...document.querySelectorAll('button')].find(b=>b.offsetParent&&b.innerText.trim()==='Criar safra').click()"); esp(.6)
    for k, v in (('nome', 'Safra 2027/28'), ('ini', '2027-09-01'), ('fim', '2028-08-31')):
        J(f"(()=>{{const i=document.getElementById('fx_g_saf_{k}'); Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(i,{q(v)}); i.dispatchEvent(new Event('input',{{bubbles:true}}));}})()")
    esp(.3); J("[...document.querySelectorAll('aside[role=dialog] button')].find(b=>b.innerText.trim()==='Salvar').click()"); esp(1.6)
    J("(()=>{const b=[...document.querySelectorAll('button')].find(b=>b.offsetParent&&/Planejar talhões livres/.test(b.innerText)); return !!b;})()")
    CONTA['cliques'] = 0; CONTA['teclas'] = 0
def cultivos(): return sorted([(x['local'], x['cult'], x['var'], x['plano'], x['plantio'], x['meta'], x['area']) for x in (J("window.__safRef.cultivos()") or [])])
res = {}
try:
    # ---------- A · antes: painel por talhão ----------
    nova_safra()
    livres = J("[...document.querySelectorAll('[role=table] [role=row]')].filter(r=>r.offsetParent&&[...r.querySelectorAll('button')].some(b=>b.innerText.trim()==='Planejar ›')).map(r=>r.querySelector('.g2c0 b').innerText.trim())")
    assert livres == list(METAS), livres
    for t in METAS:
        clique(f"[...[...document.querySelectorAll('[role=table] [role=row]')].find(r=>r.offsetParent&&r.querySelector('.g2c0 b')&&r.querySelector('.g2c0 b').innerText.trim()==={q(t)}).querySelectorAll('button')].find(b=>b.innerText.trim()==='Planejar ›')")
        F = lambda k: f"document.getElementById('fx_g_cult_NOVA_{k}')"
        if J(f"{F('cult')}.value") != ALVO['cult']: escolhe(F('cult'), ALVO['cult'])
        if J(f"{F('var')}.value") != ALVO['var']: digita(F('var'), ALVO['var'])
        if J(f"{F('plano')}.value") != ALVO['plano']: escolhe(F('plano'), ALVO['plano'])
        if J(f"{F('plantio')}.value") != ALVO['plantio']: data(F('plantio'), ALVO['plantio'])
        digita(F('meta'), METAS[t])
        clique("[...document.querySelectorAll('aside[role=dialog] button')].find(b=>b.innerText.trim()==='Salvar')"); esp(.6)
        if J("!!document.querySelector('aside[role=dialog]')"): raise RuntimeError('formulário não fechou em ' + t + ': ' + (J("document.querySelector('aside[role=dialog]').innerText") or '')[:300])
    res['A'] = dict(CONTA, cultivos=cultivos())
    # ---------- B · depois: Editar talhões, aplicar aos marcados e metas na coluna ----------
    nova_safra()
    clique("document.getElementById('sl-abrir')"); esp(.8)
    clique("document.querySelector('#sl-grade [aria-label=\"Marcar todas as linhas\"]')")
    escolhe("document.querySelector('#sl-grade [aria-label=\"Cultura para os marcados\"]')", ALVO['cult'])
    digita("document.querySelector('#sl-grade [aria-label=\"Variedade para os marcados\"]')", ALVO['var'])
    data("document.querySelector('#sl-grade [aria-label=\"Plantio para os marcados\"]')", ALVO['plantio'])
    escolhe("document.querySelector('#sl-grade [aria-label=\"Plano para os marcados\"]')", ALVO['plano'])
    clique("document.getElementById('sl-aplicar')")
    for i, t in enumerate(METAS):
        digita(f"document.querySelector('#sl-grade [data-l=\"novo:{t}\"][data-c=\"meta\"]')", METAS[t], clicar=(i == 0))
        tecla('Enter')
    clique("document.getElementById('sl-salvar')"); esp(.8)
    if J("!!document.getElementById('sl-painel')"): raise RuntimeError('B não salvou: ' + (J("document.getElementById('sl-painel').innerText") or '')[:400])
    res['B'] = dict(CONTA, cultivos=cultivos())
    # ---------- C · depois: colar o bloco da planilha ----------
    nova_safra()
    clique("document.getElementById('sl-abrir')"); esp(.8)
    bloco = ''.join(f"Soja\t58 W\t15/10/2027\t{METAS[t]}\tSoja alta tecnologia\r\n" for t in METAS)
    clique("document.querySelector('#sl-grade [data-l=\"novo:T1\"][data-c=\"cult\"]')")
    J("(()=>{const g=document.querySelector('.g2dsel'); if(g) g.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true}));})()"); CONTA['teclas'] += 1   # Esc fecha a lista que o clique abriu
    J(f"""(()=>{{const e=document.querySelector('#sl-grade [data-l="novo:T1"][data-c="cult"]'); e.focus(); const dt=new DataTransfer(); dt.setData('text/plain',{q(bloco)});
      e.dispatchEvent(new ClipboardEvent('paste',{{clipboardData:dt,bubbles:true,cancelable:true}}));}})()"""); CONTA['teclas'] += 1; esp(.8)   # Ctrl+V
    info = J("(document.getElementById('sl-info')||{}).innerText") or ''
    clique("document.getElementById('sl-salvar')"); esp(.8)
    if J("!!document.getElementById('sl-painel')"): raise RuntimeError('C não salvou: ' + info + ' · ' + (J("document.getElementById('sl-painel').innerText") or '')[:400])
    res['C'] = dict(CONTA, cultivos=cultivos(), info=info)
finally:
    c.close(); srv.terminate()
iguais = res['A']['cultivos'] == res['B']['cultivos'] == res['C']['cultivos'] and len(res['A']['cultivos']) == 6
for k, nome in (('A', 'antes · painel por talhão'), ('B', 'depois · Editar talhões (aplicar + coluna)'), ('C', 'depois · Editar talhões (colar planilha)')):
    print(f"{k} {nome}: {res[k]['cliques']} cliques · {res[k]['teclas']} teclas · {len(res[k]['cultivos'])} cultivos")
print('cultivos gravados:', res['A']['cultivos'])
print('C:', res['C'].get('info'))
print('RESULTADO:', 'OK' if iguais else 'FALHOU', '· os três caminhos gravam os mesmos 6 cultivos' if iguais else '· cultivos diferentes entre os caminhos')
if '--json' in sys.argv: json.dump(res, open(sys.argv[sys.argv.index('--json') + 1], 'w'), ensure_ascii=False, indent=1)
sys.exit(0 if iguais else 1)
