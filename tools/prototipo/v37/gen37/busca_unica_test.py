# -*- coding: utf-8 -*-
"""Um campo de busca por tela (proprietário, 13/10/2026: "quero somente 1 campo de busca por tela. 2 fica confuso"). Confere no navegador:
  B1 nenhuma tela tem mais de um campo de busca à vista ao abrir (busca, combobox ou campo "buscar/digite"), 1440 × 900
  B2 nas telas com várias tabelas, também depois de cada aba ou visão (role=tab e as visões da Manutenção #vis=): no máximo um campo
  B3 tela com várias tabelas à vista (Inteligência de compras): o campo único diz "Buscar nesta tela" e o termo filtra TODAS as tabelas à
     vista; oráculo: cada tabela fica com as linhas que já tinham o termo no texto (sem diferença de caixa)
  B4 limpar o termo devolve todas as linhas de todas as tabelas; tela com uma tabela só segue "Buscar nesta tabela"
  B5 Consulta Agrofit: Cultura e Praga-alvo são listas de escolha (sem digitar); o único campo de texto é a busca da lista
  B6 sem erro de JS
Uso: python3 busca_unica_test.py (lê _render ou RENDER_DIR)."""
import os, sys, json, time, glob, re
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, servir

OK, FAIL = [], []
def chk(n, c, info=''):
    (OK if c else FAIL).append(n); print(('OK    ' if c else 'FALHA ') + n + ('' if c else ' · ' + str(info)[:900]), flush=True)

R = os.environ.get('RENDER_DIR') or os.path.join(HERE, '_render')
p, srv = servir(R); c = Chrome(); J = c.js
U = lambda pg: f'http://127.0.0.1:{p}/{pg}'
BUSCAS = r"""JSON.stringify([...document.querySelectorAll('input,textarea')].filter(i=>{ if(!i.getClientRects().length) return false; const r=i.getBoundingClientRect(); if(r.width<20||r.height<10) return false;
  const t=(i.getAttribute('type')||'text').toLowerCase(); if(['hidden','checkbox','radio','button','submit','number','date','range','color','file'].includes(t)) return false;
  if(i.closest('[role=dialog]')) return false;   /* filtro do cabeçalho aberto (popover) não é campo da tela */
  const ph=((i.getAttribute('placeholder')||'')+' '+(i.getAttribute('aria-label')||'')).toLowerCase();
  return t==='search'||i.getAttribute('role')==='combobox'||!!i.getAttribute('aria-autocomplete')||/busc|pesquis|digite|procur|filtrar/.test(ph); })
  .map(i=>(i.getAttribute('aria-label')||i.getAttribute('placeholder')||'?').slice(0,50)))"""
TABS = "JSON.stringify([...document.querySelectorAll('main [role=tab]')].filter(b=>b.getClientRects().length).map(b=>b.innerText.replace(/\\s+/g,' ').trim()).slice(0,8))"
TABELAS = """JSON.stringify([...document.querySelectorAll('main [role=table]')].filter(t=>t.getClientRects().length).map(t=>[...t.querySelectorAll('[role=row][data-rid]')]
  .filter(r=>r.getClientRects().length).map(r=>[r.getAttribute('data-rid'), r.innerText.replace(/\\s+/g,' ')])))"""
def busca(term):
    J(f"""(()=>{{const i=[...document.querySelectorAll('input[type=search]')].find(x=>x.getClientRects().length); const P=HTMLInputElement.prototype;
      Object.getOwnPropertyDescriptor(P,'value').set.call(i,{json.dumps(term)}); i.dispatchEvent(new Event('input',{{bubbles:true}})); i.dispatchEvent(new Event('change',{{bubbles:true}}));}})()"""); time.sleep(.8)
def limpa(): c.goto(U('Main.dc.html'), .3); J("localStorage.clear(); sessionStorage.clear(); 1")
try:
    c.call('Page.addScriptToEvaluateOnNewDocument', {'source': "window.__err='';addEventListener('error',e=>{window.__err+=(e.message||'erro')+' | ';});"})
    c.aparelho(1440, 900, 1, False); limpa()
    pags = sorted(os.path.basename(f) for f in glob.glob(os.path.join(R, '*.dc.html')))
    mais, errs = {}, {}
    for n in pags:
        c.goto(U(n), 3.0 if n.startswith('AG-07') else 1.2)
        b = json.loads(J(BUSCAS) or '[]')
        if len(b) > 1: mais[n] = b
        e = J("window.__err||''") or ''
        if e: errs[n] = e[:120]
    chk(f'B1 {len(pags)} telas: nenhuma com mais de um campo de busca à vista ao abrir', not mais, mais)
    # B2 · abas e visões das telas com várias tabelas
    multi = [n for n in pags if open(os.path.join(R, n), encoding='utf-8', errors='ignore').read().count('data-g2q=') > 1]
    ruins, vistos = {}, 0
    for n in multi:
        c.goto(U(n), 1.4); tabs = json.loads(J(TABS) or '[]')
        for t in tabs:
            J(f"(()=>{{const b=[...document.querySelectorAll('main [role=tab]')].find(x=>x.getClientRects().length&&x.innerText.replace(/\\s+/g,' ').trim()==={json.dumps(t)}); if(b) b.click();}})()"); time.sleep(.6); vistos += 1
            b = json.loads(J(BUSCAS) or '[]')
            if len(b) > 1: ruins[f'{n} › {t}'] = b
    for v in ('semordem', 'ordens', 'ativos', 'planos'):
        c.goto(U(f'MA.dc.html#vis={v}'), 1.6); vistos += 1; b = json.loads(J(BUSCAS) or '[]')
        if len(b) > 1: ruins[f'MA › {v}'] = b
    chk(f'B2 {len(multi)} telas com várias tabelas, {vistos} abas ou visões abertas: no máximo um campo de busca à vista em cada', vistos > 0 and not ruins, ruins)
    # B3/B4 · Inteligência de compras: várias tabelas à vista, um campo para todas (oráculo pelas linhas antes do termo)
    limpa(); c.goto(U('IC.dc.html'), 1.6)
    t0 = json.loads(J(TABELAS) or '[]'); lab = J("(()=>{const i=[...document.querySelectorAll('input[type=search]')].find(x=>x.getClientRects().length); return i?i.getAttribute('aria-label'):'';})()")
    # termo: uma palavra da 2ª tabela que também aparece na 1ª (as duas filtram) ou, sem isso, a 1ª palavra longa da 2ª tabela
    pal = lambda t: {w for _, x in t for w in re.findall(r'[A-Za-zÀ-ú]{5,}', x)}
    termo = ''
    if len(t0) >= 2:
        com = sorted(pal(t0[0]) & pal(t0[1])); termo = (com or sorted(pal(t0[1])) or [''])[0]
    esp = [sorted(r for r, x in t if termo.lower() in x.lower()) for t in t0]
    busca(termo); t1 = json.loads(J(TABELAS) or '[]'); got = [sorted(r for r, _ in t) for t in t1]
    chk(f'B3 IC: {len(t0)} tabelas à vista e um campo só, "Buscar nesta tela"; o termo "{termo}" filtra todas (oráculo pelas linhas que já tinham o termo)',
        len(t0) >= 2 and lab == 'Buscar nesta tela' and bool(termo) and got == esp and any(len(e) < len(t) for e, t in zip(esp, t0)), [len(t0), lab, termo, [len(x) for x in t0], [len(x) for x in esp], [len(x) for x in got]])
    busca(''); t2 = json.loads(J(TABELAS) or '[]')
    c.goto(U('OS.dc.html'), 1.4); lab1 = J("(()=>{const i=[...document.querySelectorAll('input[type=search]')].find(x=>x.getClientRects().length); return i?i.getAttribute('aria-label'):'';})()")
    chk('B4 limpar o termo devolve todas as linhas de todas as tabelas; tela com uma tabela só (O.S.) segue "Buscar nesta tabela"',
        [sorted(r for r, _ in t) for t in t2] == [sorted(r for r, _ in t) for t in t0] and lab1 == 'Buscar nesta tabela', [[len(x) for x in t2], lab1])
    # B5 · Consulta Agrofit
    c.goto(U('AG-07.dc.html'), 1.0); t5 = time.time()
    while time.time() - t5 < 30 and not J("(()=>{const s=document.querySelector('select[aria-label=Cultura]'); return !!s&&s.options.length>5;})()"): time.sleep(.3)
    J("(()=>{const s=document.querySelector('select[aria-label=Cultura]'); const o=[...s.options].find(o=>o.text==='Soja'); s.value=o.value; s.dispatchEvent(new Event('change',{bubbles:true}));})()"); time.sleep(2.0)
    sel5 = json.loads(J("JSON.stringify(['Cultura','Praga-alvo'].map(l=>{const s=document.querySelector('select[aria-label=\"'+l+'\"]'); return s?[s.tagName,s.options.length>1]:null;}))") or '[]')
    b5 = json.loads(J(BUSCAS) or '[]')
    chk('B5 Consulta Agrofit (Soja): Cultura e Praga-alvo como listas de escolha; o único campo de texto é a busca da lista', sel5 == [['SELECT', True], ['SELECT', True]] and len(b5) == 1, [sel5, b5])
    chk('B6 sem erro de JS (abertura das telas)', not errs, errs)
finally:
    try: c.close()
    except Exception: pass
    srv.terminate()
print(f'RESULTADO: {len(OK)} ok · {len(FAIL)} falhas')
sys.exit(1 if FAIL else 0)
