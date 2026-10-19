# -*- coding: utf-8 -*-
"""Revisão do PR #132 (Claude): o evento entre abas na CD-04, no navegador real (Chrome, dados sintéticos), pela tela.
Duas janelas da mesma origem (quadros A e B, cada uma com a CD-04 inteira, aba Equipes). Tudo pela tela, como o gestor faria:
  E1 B muda o calendário da Oficina para seg–sex · 08–18h e salva; A, ociosa, mostra 08–18h na linha da Oficina sem nenhuma interação
  E2 A abre a Oficina e escolhe escala 6×2 (rascunho); B salva seg–sáb · 06–15h; o rascunho de A continua no formulário aberto
  E3 A salva o rascunho antigo: recusa por revisão (nada gravado), rascunho mantido; a fonte segue com o valor de B
  E4 nenhum erro de JavaScript em A nem em B
Uso: env CHROME_BIN=… CDP_GL=1 python3 -B sonda_abas.py <gen37> <render>"""
import os, sys, json, time
G, RD = sys.argv[1], sys.argv[2]; sys.path.insert(0, G)
from comp_lib import Chrome, servir
p, srv = servir(RD); c = Chrome(); J = c.js
U = lambda pg: f'http://127.0.0.1:{p}/{pg}'
OK = FAIL = 0
def chk(n, cond, info=''):
    global OK, FAIL
    if cond: OK += 1; print('OK   ', n)
    else: FAIL += 1; print('FALHA', n, '·', str(info)[:700])
W = {'A': "document.getElementById('qa').contentWindow", 'B': "document.getElementById('qb').contentWindow"}
def linha(q): return J(f"(w=>{{ const r=[...w.document.querySelectorAll('[data-g2g=g_eq] [role=row][data-rid]')].find(r=>/Oficina/.test(r.innerText)); return r?r.innerText.replace(/\\s+/g,' ').trim():''; }})({W[q]})") or ''
def aba(q): J(f"(w=>{{ const t=[...w.document.querySelectorAll('[role=tab]')].find(t=>/^Equipes/.test(t.innerText.trim())); if(t) t.click(); }})({W[q]})"); time.sleep(.6)
def abre(q): J(f"(w=>{{ const r=[...w.document.querySelectorAll('[data-g2g=g_eq] [role=row][data-rid]')].find(r=>/Oficina/.test(r.innerText)); if(r) (r.querySelector('.g2pw')||r.querySelector('[role=cell]')||r).click(); }})({W[q]})"); time.sleep(.6)
def cal(q, v): return J(f"(w=>{{ const s=w.document.getElementById('fx_g_eq_cal'); if(!s) return 'sem campo'; Object.getOwnPropertyDescriptor(w.HTMLSelectElement.prototype,'value').set.call(s,{json.dumps(v)}); s.dispatchEvent(new w.Event('change',{{bubbles:true}})); return 'ok'; }})({W[q]})")
def calv(q): return J(f"(w=>{{ const s=w.document.getElementById('fx_g_eq_cal'); return s?s.value:''; }})({W[q]})") or ''
def salva(q): J(f"(w=>{{ const a=[...w.document.querySelectorAll('aside[role=dialog]')].find(a=>a.getClientRects().length); const b=a&&[...a.querySelectorAll('button')].find(b=>b.innerText.trim()==='Salvar'); if(b) b.click(); }})({W[q]})"); time.sleep(.8)
def dialogo(q): return J(f"(w=>{{ const a=[...w.document.querySelectorAll('aside[role=dialog]')].find(a=>a.getClientRects().length); return a?a.innerText.replace(/\\s+/g,' '):''; }})({W[q]})") or ''
def espera(e, s=8):
    f = time.time() + s
    while time.time() < f:
        if J(e): return True
        time.sleep(.25)
    return False
try:
    c.aparelho(1440, 900); c.goto(U('Main.dc.html'), .4); J("localStorage.clear(); sessionStorage.clear(); 1")
    c.goto(U('agrofit_meta.json'), .4)   # contêiner estático da mesma origem (o Main.dc.html redireciona e apagaria os quadros)
    J("document.body.innerHTML='<iframe id=qa style=\"width:1400px;height:800px\"></iframe><iframe id=qb style=\"width:1400px;height:800px\"></iframe>';"
      f"document.getElementById('qa').src={json.dumps(U('CD-04.dc.html'))}; document.getElementById('qb').src={json.dumps(U('CD-04.dc.html'))}; 1")
    espera(f"!!({W['A']}.document&&{W['A']}.document.querySelector('[role=tab]')&&{W['B']}.document&&{W['B']}.document.querySelector('[role=tab]'))", 25); time.sleep(1.5)
    for q in 'AB': J(f"(w=>{{ w.__e=[]; w.addEventListener('error',e=>w.__e.push(String(e.message))); }})({W[q]})"); aba(q)
    l0 = linha('A'); print('      A antes:', l0)
    abre('B'); r1 = cal('B', 'seg–sex · 08–18h'); salva('B'); fb = dialogo('B')
    e1 = espera(f"(w=>{{ const r=[...w.document.querySelectorAll('[data-g2g=g_eq] [role=row][data-rid]')].find(r=>/Oficina/.test(r.innerText)); return !!r&&r.innerText.indexOf('08–18h')>=0; }})({W['A']})")
    chk('E1 B salva a Oficina em 08–18h pela tela; A, ociosa, mostra 08–18h sem interação', '07–17h' in l0 and r1 == 'ok' and not fb and e1, [l0, r1, fb[:200], linha('A')])
    abre('A'); ra = cal('A', 'escala 6×2 · 8h')
    abre('B'); rb = cal('B', 'seg–sáb · 06–15h'); salva('B'); time.sleep(1.2)
    da = dialogo('A'); va = calv('A')
    chk('E2 com o formulário aberto em A (rascunho 6×2), a gravação em B não apaga o rascunho', ra == 'ok' and rb == 'ok' and bool(da) and va == 'escala 6×2 · 8h', [ra, rb, va, da[:200]])
    salva('A'); da2 = dialogo('A'); va2 = calv('A'); lb = linha('B')
    chk('E3 A salva o rascunho antigo: recusa por revisão, rascunho mantido, fonte com o valor de B', 'mudaram' in da2 and va2 == 'escala 6×2 · 8h' and '06–15h' in lb, [da2[:300], va2, lb])
    er = (J(f"{W['A']}.__e") or []) + (J(f"{W['B']}.__e") or [])
    chk('E4 nenhum erro de JavaScript em A nem em B', not er, er[:5])
finally:
    c.close(); srv.terminate()
print(f'RESULTADO: {OK}/{OK+FAIL} ok'); sys.exit(1 if FAIL else 0)
