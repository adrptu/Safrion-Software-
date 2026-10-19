# -*- coding: utf-8 -*-
"""UNID-PROD P5 · prova pedida pelo Codex no PR #133 (revisão 5569013634): o rótulo composto do pivô pela cadeia real, a 1440 e a 390 px.
Cadeia real: carga recebida → prProdOS (modo da participação) → prResultado → colhNum → MUX.info → marcador do MapLibre (rótulo e nome acessível).
O estado sintético é montado no armazenamento local: a CD-04 grava a fonte (o calendário do Comercial, sem relação com o Mapa) e a participação
das origens do Pivô 19 nas cargas recebidas passa a "estimada" (COLH R-06), como o formulário de carga grava. O Mamão fica em kg/ha (Ana).
  E1 1440 × 900: o rótulo do Pivô 19 é "em colheita · <n> kg/ha · estimativa", inteiro (sem corte de largura nem de altura)
  E2 390 × 844 com toque: o mesmo
  E3 o nome acessível do pivô traz o mesmo indicador, com "estimativa" (1440 e 390)
  E4 o rótulo do Pivô 19, dentro da tela, não se sobrepõe a outro rótulo visível, antes e depois de selecionar o pivô (1440 e 390). A 390 px o
     Pivô 19 abre fora da área do mapa: o teste centraliza o mapa nele, como a pessoa arrastaria (selecionar pelo teclado não move o mapa)
  E5 sonda de texto (não é a cadeia real: o cenário sintético não tem café em talhão do Mapa; o café C1 da Santa Rita não tem geometria):
     os textos compostos do café a apurar com a medida do campo e da estimativa, pela mesma quebra (MUX.quebra), cabem no rótulo a 1440 e a 390
  E6 nenhum erro de JavaScript
Fotos: docs/integracao/V73/p5-mapa/fotos/p19_estimativa_{1440,390}.png
Uso (de gen37/): env CHROME_BIN=… CDP_GL=1 SAFRION_DADOS=sintetico [RENDER_DIR=…] python3 -B mapa_rotulo_real_test.py"""
import os, sys, json, time, re, base64
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
os.environ.setdefault('CDP_GL', '1')
from comp_lib import Chrome, servir

R = os.environ.get('RENDER_DIR') or os.path.join(HERE, '_render')
FOTOS = os.path.normpath(os.path.join(HERE, '..', '..', '..', '..', 'docs', 'integracao', 'V73', 'p5-mapa', 'fotos'))
OK = FAIL = 0
def chk(nome, cond, info=''):
    global OK, FAIL
    if cond: OK += 1; print('OK   ', nome)
    else: FAIL += 1; print('FALHA', nome, '·', str(info)[:900])
SETV = "((k,val)=>{ const i=document.getElementById(k); if(!i) return 'sem '+k; const P=i.tagName==='TEXTAREA'?HTMLTextAreaElement.prototype:(i.tagName==='SELECT'?HTMLSelectElement.prototype:HTMLInputElement.prototype); Object.getOwnPropertyDescriptor(P,'value').set.call(i,val); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true})); return 'ok'; })"
BTN = "((t)=>{ const a=[...document.querySelectorAll('aside[role=dialog]')].find(a=>a.getClientRects().length); const b=a&&[...a.querySelectorAll('button')].find(b=>(b.innerText||'').trim()===t); if(!b) return false; b.click(); return true; })"
# o estado gravado é achado pelo conteúdo (as cargas da produção), sem depender do nome da chave
ESTADO = "Object.keys(localStorage).find(k=>{ try{ const x=JSON.parse(localStorage.getItem(k)); return !!(x&&x.producao&&x.producao.cargas&&x.cadPessoas); }catch(e){ return false; } })"
ROT = r"""JSON.stringify((()=>{ const m=window.__LGI&&window.__LGI.markers['PV19']; if(!m) return null; const e=m.getElement(), s=e.children[1], r=e.getBoundingClientRect();
  const t=document.querySelector('[data-mux-grupo] [data-talhao=PV19]');
  const outros=Object.entries(window.__LGI.markers).filter(([k])=>k!=='PV19').map(([k,v])=>[k,v.getElement()]).filter(([k,x])=>x.getClientRects().length&&getComputedStyle(x).visibility!=='hidden')
    .map(([k,x])=>[k,x.getBoundingClientRect()]).filter(([k,q])=>q.left<r.right-1&&q.right>r.left+1&&q.top<r.bottom-1&&q.bottom>r.top+1).map(([k])=>k);
  return {txt:s.textContent.replace(/\s+/g,' ').trim(), corte:s.scrollWidth>s.clientWidth+1||s.scrollHeight>s.clientHeight+1, nome:(t&&t.getAttribute('aria-label'))||'',
    sobre:outros, dentro:r.left>=0&&r.top>=0&&r.right<=innerWidth&&r.bottom<=innerHeight, r:[Math.round(r.left),Math.round(r.top),Math.round(r.width),Math.round(r.height)]}; })())"""
SONDA = """(()=>{ const s=window.__LGI.markers['PV19'].getElement().children[1], o=s.textContent, out=[], q=(window.__MUX&&window.__MUX.quebra)||(t=>t);
  ['em colheita · kg/ha a apurar · 1.200,00 kg/ha de Café da roça · +1','em colheita · 1.484,89 kg/ha · estimativa · +1'].forEach(t=>{
    s.textContent=q(t); out.push([t, s.scrollHeight>s.clientHeight+1||s.scrollWidth>s.clientWidth+1, Math.round(s.clientHeight)]); });
  s.textContent=o; return JSON.stringify(out); })()"""
def espera(e, s=30):
    f = time.time() + s
    while time.time() < f:
        if J(e): return True
        time.sleep(.3)
    return False
p, srv = servir(R); c = Chrome(); J = c.js
c.call('Page.addScriptToEvaluateOnNewDocument', {'source': "window.__e=[];addEventListener('error',e=>window.__e.push(String(e.message)))"})
U = lambda pg: f'http://127.0.0.1:{p}/{pg}'
erros = []
def prepara():
    c.aparelho(1440, 900); c.goto(U('Main.dc.html'), .3)
    J("localStorage.clear(); sessionStorage.clear(); localStorage.setItem('safrion.perfilDemo','Ana'); localStorage.setItem('safrion.pref.unidprod:Ana:Mamão Formosa','kg'); 1")
    c.goto(U('CD-04.dc.html'), 1.8)   # grava a fonte pela tela, sem tocar no Mapa (calendário do Comercial)
    J("(()=>{ const t=[...document.querySelectorAll('[role=tab]')].find(t=>/^Equipes/.test(t.innerText.trim())); if(t) t.click(); })()"); time.sleep(.6)
    J("(()=>{ const r=[...document.querySelectorAll('[data-g2g=g_eq] [role=row][data-rid]')].find(r=>/Comercial/.test(r.innerText)); if(r) (r.querySelector('.g2pw')||r.querySelector('[role=cell]')||r).click(); })()"); time.sleep(.6)
    g = [J(SETV + "('fx_g_eq_cal','seg–sáb · 06–15h')")]; time.sleep(.3); g.append(J(BTN + "('Salvar')")); time.sleep(.9)
    n = J("(()=>{ const k=" + ESTADO + "; if(!k) return 'sem estado'; const x=JSON.parse(localStorage.getItem(k)); let n=0;"
          " Object.values(x.producao.cargas).filter(g=>g.st==='Recebida').forEach(g=>(g.origem||[]).forEach(o=>{ if(o.tal==='Pivô 19'){ o.modo='estimada'; n++; } }));"
          " localStorage.setItem(k,JSON.stringify(x)); return n; })()")
    return g, n
def abre(w, h, toque):
    c.aparelho(w, h, 1 if w > 400 else 2, toque); c.goto('about:blank', .1)
    c.goto(U('Main.dc.html'), .3); J("sessionStorage.setItem('mapa-ctx','{\"mf_faz\":\"Lagoa Grande\"}'); 1")
    c.goto(U('IN-04.dc.html'), 1.0); espera("!!(window.__LGI&&window.__LGI.pronto)")
    J("(()=>{ const L=window.__LGI; L.map.jumpTo({center:L.markers['PV19'].getLngLat()}); })()"); time.sleep(1.0)
    J("(()=>{const b=[...document.querySelectorAll('nav[aria-label=\"Funcionalidades do mapa\"] [role=tab]')].find(b=>b.innerText.trim()==='Colheita e produtividade'); if(b) b.click();})()"); time.sleep(1.6)
def foto(nome, r):
    os.makedirs(FOTOS, exist_ok=True); x, y, w, h = r; pad = 70
    clip = {'x': max(0, x - pad), 'y': max(0, y - pad), 'width': w + 2 * pad, 'height': h + 2 * pad, 'scale': 1}
    d = c.call('Page.captureScreenshot', {'format': 'png', 'clip': clip}); open(os.path.join(FOTOS, nome + '.png'), 'wb').write(base64.b64decode(d['data']))
try:
    g, n = prepara(); print('      estado:', g, 'origens do Pivô 19 marcadas como estimada:', n)
    med = {}
    for w, h, toque in ((1440, 900, False), (390, 844, True)):
        abre(w, h, toque); a = json.loads(J(ROT) or 'null') or {}
        J("(()=>{ const t=document.querySelector('[data-mux-grupo] [data-talhao=PV19]'); if(t) t.focus(); })()"); time.sleep(.15); c.tecla('Enter', 'Enter', 13, '\r'); time.sleep(1.0)
        d = json.loads(J(ROT) or 'null') or {}
        if d.get('r') and d.get('dentro') and not os.environ.get('RENDER_DIR'): foto(f'p19_estimativa_{w}', d['r'])   # a contraprova (RENDER_DIR) não grava foto
        med[w] = (a, d, json.loads(J(SONDA) or '[]')); erros.extend(J("window.__e") or [])
        print(f'      {w}:', med[w])
    ok_txt = lambda x: bool(re.fullmatch(r'em colheita · [\d.]+,\d+ kg/ha · estimativa', x.get('txt', ''))) and not x.get('corte')
    chk('E1 1440 px: o Pivô 19 mostra "em colheita · <n> kg/ha · estimativa" inteiro, pela cadeia real', isinstance(n, int) and n > 0 and ok_txt(med[1440][0]) and ok_txt(med[1440][1]), [n, med[1440][:2]])
    chk('E2 390 px com toque: o mesmo', ok_txt(med[390][0]) and ok_txt(med[390][1]), med[390][:2])
    chk('E3 o nome acessível do pivô traz o mesmo indicador, com "estimativa" (1440 e 390)',
        all(m[0].get('txt') and m[0]['txt'] in m[0].get('nome', '').replace(' ', ' ') and 'estimativa' in m[0].get('nome', '') for m in med.values()), {k: v[0].get('nome') for k, v in med.items()})
    chk('E4 o rótulo do Pivô 19, dentro da tela, não se sobrepõe a outro rótulo visível, antes e depois de selecionar (1440 e 390)',
        all(m[0].get('dentro') and m[1].get('dentro') and not m[0].get('sobre') and not m[1].get('sobre') for m in med.values()),
        {k: (v[0].get('dentro'), v[0].get('sobre'), v[1].get('dentro'), v[1].get('sobre')) for k, v in med.items()})
    chk('E5 sonda de texto (identificada; não é a cadeia real): os compostos do café a apurar e da estimativa cabem no rótulo a 1440 e a 390',
        all(len(m[2]) == 2 and not any(x[1] for x in m[2]) for m in med.values()), {k: v[2] for k, v in med.items()})
    chk('E6 nenhum erro de JavaScript', not erros, erros[:5])
finally:
    c.close(); srv.terminate()
print(f'RESULTADO: {OK}/{OK+FAIL} ok')
sys.exit(1 if FAIL else 0)
