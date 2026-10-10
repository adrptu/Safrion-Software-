# -*- coding: utf-8 -*-
"""v55 · varredura de DOM: nenhuma tela visível leva ao Beneficiamento (BEN.dc.html).
Uso: env CHROME_BIN=… flock /tmp/cdpW.lock env CDP_GL=1 SAFRION_DADOS=sintetico python3 varre_ben.py <gen37> [saida.json]
Telas visíveis = boards da página 'menu' do canvas gerado (project/canvas.json). Em cada uma, no estado inicial (1440 px e 390 px):
  (a) todo elemento com algum atributo que cite BEN.dc.html (<a href>, onclick, data-*, action, formaction…), fora de <script>/<style>;
  (b) todo <a>/botão cujo texto ofereça a ação da tela oculta ("Abrir ordem de beneficiamento", "Abrir a OB-…", "Abrir a ordem").
Estados com o vínculo histórico (ordem de beneficiamento) à vista: Cargas (cada carga aberta), Estoque de produto (cada lote por âncora),
Previsão e colheita (cada talhão), Estoque (cada tela da faixa), O.S. (cada ordem por âncora), Manutenção (cada ativo e ordem por âncora).
Sai 1 se achar qualquer elemento; imprime 'RESULTADO: n estados · m elementos que levam a BEN.dc.html'."""
import sys, os, json, time
G = os.path.abspath(sys.argv[1]); OUT = sys.argv[2] if len(sys.argv) > 2 else None
sys.path.insert(0, G); os.chdir(G)
from cadc_lib import T
import cenario
SEED = cenario.seed()   # o mesmo cenário inicial das telas (CEN0): lotes, ordens e manutenção para abrir cada registro por âncora
cv = json.load(open(os.path.join(G, 'project', 'canvas.json')))
VIS = sorted(k for k, v in cv['boards'].items() if v.get('page') == 'menu')
OC = sorted(k for k, v in cv['boards'].items() if v.get('page') == 'ocultos')
ACHA = r"""(()=>{ const out=[]; const n=s=>(s||'').replace(/\s+/g,' ').trim();
  for(const e of document.querySelectorAll('body *')){ if(e.closest('script,style')) continue;
    for(const a of e.attributes){ if(String(a.value).indexOf('BEN.dc.html')>=0) out.push({tag:e.tagName,attr:a.name,v:String(a.value).slice(0,120),txt:n(e.innerText).slice(0,80)}); } }
  for(const e of document.querySelectorAll('a,button,[role=button]')){ const t=n(e.innerText);
    if(/^Abrir ordem de beneficiamento|^Abrir a OB-|^Abrir a ordem$/.test(t)&&e.getClientRects().length) out.push({tag:e.tagName,attr:'texto',v:t.slice(0,120),txt:t.slice(0,80)}); }
  return out; })()"""
t = T(); J = t.J; res = {}; n_est = 0
def scan(nome):
    global n_est
    n_est += 1; r = J(ACHA) or []
    if r: res[nome] = r; print('ACHOU', nome, json.dumps(r, ensure_ascii=False)[:400], flush=True)
    return r
def ir(f, w=1440, h=1000):
    t.c.size(w, h); t.goto(f); t0 = time.time()
    while len((J("(document.body&&document.body.innerText)||''") or '').strip()) < 20 and time.time() - t0 < 8: time.sleep(.25)
def linhas():   # registros da 1ª grade com seleção (g2ed), pelo texto
    return J("[...document.querySelectorAll('main [role=row].g2ed')].map(r=>r.innerText.replace(/\\s+/g,' ').trim().slice(0,60))") or []
def clica_linha(i):
    J(f"(()=>{{const r=[...document.querySelectorAll('main [role=row].g2ed')][{i}]; if(r) (r.querySelector('.g2pw')||r).click();}})()"); time.sleep(.35)
try:
    t.goto('Main.dc.html'); J("localStorage.clear()")
    # 1) toda tela visível, estado inicial, 1440 e 390 px
    for f in VIS:
        ir(f); scan(f + ' · 1440')
        ir(f, 390, 844); scan(f + ' · 390')
    # 2) estados com o vínculo histórico à vista
    ir('CARGA.dc.html'); ls = linhas()
    for i, l in enumerate(ls): ir('CARGA.dc.html'); clica_linha(i); scan(f'CARGA · carga aberta {l[:24]}')
    lotes = sorted(SEED['producao']['lotes']); txt_emp = {}
    for L in lotes:
        ir('PROD.dc.html#' + L); time.sleep(.3); scan(f'PROD · lote {L}')
        a = J("(()=>{ const a=document.querySelector('aside'); return a?a.innerText.replace(/\\s+/g,' ').slice(0,300):''; })()") or ''
        if 'OB-' in a or 'beneficiamento' in a: txt_emp[L] = a
    ir('COLH.dc.html'); ls = linhas()
    for i, l in enumerate(ls[:40]): ir('COLH.dc.html'); clica_linha(i); scan(f'COLH · linha {l[:24]}')
    ir('EST.dc.html'); nb = J("[...document.querySelectorAll('nav.etp .etp-itens>*')].length") or 0
    for i in range(nb):
        ir('EST.dc.html'); J(f"(()=>{{const b=[...document.querySelectorAll('nav.etp .etp-itens>*')][{i}]; b&&b.click();}})()"); time.sleep(.4); scan(f'EST · tela {i + 1}')
    ords = sorted(SEED['ordens'])
    for o in ords: ir('OS.dc.html#' + o); time.sleep(.3); scan(f'OS · {o}')
    man = {'at': sorted((SEED.get('man') or {}).get('ativos') or {}), 'om': sorted((SEED.get('man') or {}).get('oms') or {})}
    for a in man.get('at', []): ir('MA.dc.html#ativo=' + a); time.sleep(.3); scan(f'MA · ativo {a}')
    for o in man.get('om', []): ir('MA.dc.html#om=' + o); time.sleep(.3); scan(f'MA · {o}')
    tot = sum(len(v) for v in res.values())
    print('telas visíveis:', len(VIS), '·', ' '.join(f[:-8] for f in VIS))
    print('BEN.dc.html no canvas:', cv['boards'].get('BEN.dc.html', {}).get('page'), '· ocultos:', len(OC))
    print('lotes com vínculo de beneficiamento no painel (PROD):', json.dumps(txt_emp, ensure_ascii=False)[:1500])
    print(f'RESULTADO: {n_est} estados · {tot} elementos que levam a BEN.dc.html · erros JS: {t.errs()[:200] or "nenhum"}')
    if OUT: json.dump({'vis': VIS, 'achados': res, 'estados': n_est, 'em_processo': txt_emp}, open(OUT, 'w'), ensure_ascii=False, indent=1)
finally:
    try: t.c.close()
    except Exception: pass
    t.srv.terminate()
sys.exit(1 if res else 0)
