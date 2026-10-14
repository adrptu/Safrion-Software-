# -*- coding: utf-8 -*-
"""Camada Colheita no Mapa e faixa "Filtros" (proprietário, 14/10/2026: "Em vez de filtros desta tela… coloque Filtros: · teste o símbolo de
filtro junto ou sozinho" e "veja se tem algum submenu/funcionalidade em agrícola importante que ainda não tem ícone e funcionalidade no mapa
e adicione. O mapa é um modo de visão geográfico dos dados de tudo que acontece na fazenda").
Oráculo: a própria tela Previsão e colheita (COLH), lida no navegador — cada linha de cultivo traz Previsão, Colhido e Situação. No Mapa, o
talhão mostra o cultivo de situação mais urgente (Em colheita › Programada › Prevista › Colhida › Sem previsão) e "+N" para os outros.
  C1 barra do mapa: "Colheita" logo depois de "Carência e destino", com o desenho de engine.ICONS['Colheita']
  C2 Lagoa Grande e Santa Rita: o rótulo de cada talhão = situação da COLH (e "+N" com mais cultivos); talhão sem cultivo em produção, "sem colheita"
  C3 faixa de números = contagem por situação dos talhões (oráculo acima); "A receber" = cargas a receber da COLH
  C4 Pivô 19: painel com a Previsão e o Colhido iguais aos da COLH e "1 carga na balança"; o primário leva à Previsão e colheita do cultivo
  C5 o caminho do painel para a Previsão e colheita abre a COLH com o painel do mesmo cultivo
  F1 faixa de filtros (O.S., Mapa, Colheita): grupo "Filtros", só o funil (engine.ICONS['filtro']) com a dica "Filtros"; sem "Filtros desta tela"
  F2 390 px: faixa sem rolagem lateral; sem erro de JS
Uso: python3 colheita_mapa_test.py (lê _render ou RENDER_DIR)."""
import os, sys, json, time, re
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
os.environ.setdefault('CDP_GL', '1')
from comp_lib import Chrome, servir, cv_todas_sempre
import engine as E
import dados_producao as DP

OK, FAIL = [], []
def chk(n, c, info=''):
    (OK if c else FAIL).append(n); print(('OK    ' if c else 'FALHA ') + n + ('' if c else ' · ' + str(info)[:900]), flush=True)
R = os.environ.get('RENDER_DIR') or os.path.join(HERE, '_render')
p, srv = servir(R); c = Chrome(); J = c.js; cv_todas_sempre(c)   # teste de domínio: lê colunas fora do "Abre com"
U = lambda pg: f'http://127.0.0.1:{p}/{pg}'
ORD = ['Em colheita', 'Programada', 'Prevista', 'Colhida', 'Sem previsão']
def espera(e, s=45):
    f = time.time() + s
    while time.time() < f:
        if J(e): return True
        time.sleep(.4)
    return False
def limpa(): c.goto(U('Main.dc.html'), .3); J("localStorage.clear(); sessionStorage.clear(); 1")
def camada(nome):
    J(f"(()=>{{const b=[...document.querySelectorAll('[role=tab][data-dica]')].find(b=>b.getAttribute('data-dica')==={json.dumps(nome)}); if(b) b.click();}})()"); time.sleep(1.6)
BLOCO = "(()=>{const n=document.querySelector('nav[aria-label=\"Funcionalidades do mapa\"]'); let s=n; while(s&&s.parentElement&&!(s.innerText||'').match(/Selecionar área/)) s=s.parentElement; return s;})()"
FAIXA = f"""JSON.stringify((()=>{{const s={BLOCO}; if(!s) return {{}}; const o={{}}; const t=s.innerText.replace(/\\s+/g,' ');
  ['Em colheita','Programada','Prevista','Sem previsão','Colhida','A receber'].forEach(k=>{{ const m=t.match(new RegExp(k+' (\\\\d+)')); if(m) o[k]=+m[1]; }}); return o;}})())"""
FILTROS = """JSON.stringify((()=>{const g=document.querySelector('.mf-tela'); if(!g) return null; const r=g.querySelector('.mf-rot'); const pth=r&&r.querySelector('svg path');
  return {grupo:g.getAttribute('aria-label'),texto:(r?r.innerText:'').trim(),d:pth?pth.getAttribute('d'):'',dica:r?r.getAttribute('data-dica'):'',velho:/filtros desta tela/i.test(document.body.innerText)};})())"""
def talhao_do_local(faz, local, pivos):
    if faz == 'Lagoa Grande':
        m = re.match(r'Pivô (\d+)$', local); return pivos.get(int(m.group(1))) if m else None
    return local.split('-')[0]
try:
    c.call('Page.addScriptToEvaluateOnNewDocument', {'source': "window.__err='';addEventListener('error',e=>{window.__err+=(e.message||'erro')+' | ';});"})
    c.aparelho(1440, 900, 1, False); limpa()
    # oráculo: a tela Previsão e colheita (filtros em Todas)
    c.goto(U('COLH.dc.html'), 1.6); f_colh = json.loads(J(FILTROS) or 'null')
    J("(()=>{const b=[...document.querySelectorAll('button')].find(b=>/Expandir tudo/.test(b.innerText)); if(b) b.click();})()"); time.sleep(.8)
    linhas = json.loads(J("JSON.stringify([...document.querySelectorAll('[role=table]')[0].querySelectorAll('[role=row][data-rid]')].filter(r=>!/^grp:/.test(r.getAttribute('data-rid'))).map(r=>[r.getAttribute('data-rid'),[...r.querySelectorAll('[role=cell],[role=gridcell]')].map(x=>x.innerText.replace(/\\s+/g,' ').trim())]))") or '[]')
    cat = {k: [v['faz'], v['local']] for k, v in DP.catalogo()['cult'].items()}   # fazenda e local do cultivo (dado do catálogo, não a regra testada)
    # V2-3: a ordem das colunas segue o "Abre com"; a leitura é pelo nome do cabeçalho, com todas as colunas (cv_todas_sempre)
    cab = [h.split('\n')[0].strip().upper() for h in (J("[...document.querySelectorAll('[role=table]')[0].querySelectorAll('[role=columnheader]')].map(h=>h.innerText.trim())") or [])]
    iS, iP, iC = cab.index('SITUAÇÃO · PRÓXIMO PASSO'), cab.index('PREVISÃO'), cab.index('COLHIDO')
    col = {}
    for cid, cel in linhas:
        st_ = cel[iS]; sit = next((s for s in ORD if st_.startswith(s)), None); rec = re.search(r'(\d+) cargas? a receber', st_)
        col[cid] = dict(sit=sit, prev=cel[iP], colh=cel[iC], rec=int(rec.group(1)) if rec else 0, faz=cat.get(cid, ['', ''])[0], local=cat.get(cid, ['', ''])[1])
    # Mapa · Lagoa Grande
    limpa(); J("sessionStorage.setItem('mapa-ctx','{\"mf_faz\":\"Lagoa Grande\"}'); 1"); c.goto(U('IN-04.dc.html'), 1.0); pronto = espera("!!(window.__LGI&&window.__LGI.pronto)")
    f_mapa = json.loads(J(FILTROS) or 'null')
    rail = json.loads(J("JSON.stringify([...document.querySelectorAll('[role=tab][data-dica]')].map(b=>[b.getAttribute('data-dica'),(b.querySelector('svg path')||{getAttribute:()=>''}).getAttribute('d')]))") or '[]')
    nomes = [x[0] for x in rail]; i = nomes.index('Colheita') if 'Colheita' in nomes else -1
    chk('C1 barra do mapa: "Colheita" logo depois de "Carência e destino", com o desenho de Colheita', pronto and i > 0 and nomes[i - 1] == 'Carência e destino' and rail[i][1] == E.ICONS['Colheita'], nomes)
    camada('Colheita')
    pivos = {int(re.sub(r'\D', '', pid)): pid for pid in json.loads(J("JSON.stringify(Object.keys(window.__LGI.markers))") or '[]')}
    rot_lg = {pid: J(f"window.__LGI.markers['{pid}'].getElement().innerText.replace(/\\s+/g,' ').trim()") for pid in pivos.values()}
    def esperado(faz, tids):
        por = {}
        for cid, x in col.items():
            if x['faz'] != faz: continue
            t = talhao_do_local(faz, x['local'], pivos)
            if t: por.setdefault(t, []).append(x)
        out = {}
        for t in tids:
            xs = sorted(por.get(t, []), key=lambda x: (ORD.index(x['sit']), x['local']))
            out[t] = (xs[0]['sit'].lower() + (f' · +{len(xs) - 1}' if len(xs) > 1 else '')) if xs else 'sem colheita'
        return out, por
    esp_lg, por_lg = esperado('Lagoa Grande', list(pivos.values()))
    ruins = {t: [rot_lg[t], e] for t, e in esp_lg.items() if not (rot_lg[t] or '').split(' ', 1)[-1].startswith(e.split(' · +')[0]) or (('+' in e) != ('· +' in (rot_lg[t] or '')))}
    fx = json.loads(J(FAIXA) or '{}')
    cont = {s: sum(1 for t in esp_lg if esp_lg[t].startswith(s.lower())) for s in ORD}
    rec = sum(x['rec'] for xs in por_lg.values() for x in xs)
    # Santa Rita
    limpa(); J("sessionStorage.setItem('mapa-ctx',JSON.stringify({mf_faz:'Santa Rita',lay:'Colheita'})); 1"); c.goto(U('IN-04.dc.html'), 1.8)
    tids_sr = ['T1', 'T2', 'P1', 'P2', 'T4', 'T3', 'T7', 'C1']   # geometria da Santa Rita (inicio.GEO)
    rot_sr = {t: J(f"(()=>{{const e=[...document.querySelectorAll('svg [aria-label]')].find(x=>(x.getAttribute('aria-label')||'').startsWith('{t}:')); return e?e.getAttribute('aria-label'):'';}})()") or '' for t in tids_sr}
    esp_sr, _ = esperado('Santa Rita', tids_sr)
    ruins_sr = {t: [rot_sr[t], e] for t, e in esp_sr.items() if e.split(' · +')[0] not in rot_sr[t] or (('+' in e) and e.split(' · ')[-1] not in rot_sr[t])}
    chk(f'C2 rótulo de cada talhão = situação da Previsão e colheita (Lagoa Grande {len(esp_lg)} pivôs, Santa Rita {len(esp_sr)} talhões; "+N" com mais cultivos)',
        not ruins and not ruins_sr and len(esp_lg) == 23, [ruins, ruins_sr])
    chk(f'C3 faixa da Lagoa Grande = contagem por situação {cont} e A receber {rec}', all(fx.get(s, 0) == cont[s] for s in ORD) and fx.get('A receber', 0) == rec, [fx, cont, rec])
    # C4 · Pivô 19
    limpa(); J("sessionStorage.setItem('mapa-ctx',JSON.stringify({mf_faz:'Lagoa Grande',lay:'Colheita',tsel:['PV19']})); 1"); c.goto(U('IN-04.dc.html'), 1.0); espera("!!(window.__LGI&&window.__LGI.pronto)"); time.sleep(1.2)
    pan = J("(()=>{const a=[...document.querySelectorAll('main aside')].find(x=>x.getClientRects().length); return a?a.innerText.replace(/\\s+/g,' '):'';})()") or ''
    prim = json.loads(J("JSON.stringify((()=>{const a=[...document.querySelectorAll('main aside a')].filter(x=>x.getClientRects().length).pop(); return a?[a.innerText.trim(),a.getAttribute('href')]:null;})())") or 'null')
    x19 = col.get('lg19', {})
    chk(f'C4 Pivô 19: Previsão "{x19.get("prev")}" e Colhido "{x19.get("colh")}" iguais aos da COLH, "1 carga na balança"; primário para a COLH do cultivo',
        bool(x19) and f'Previsão {x19["prev"]}' in pan and f'Colhido {x19["colh"]}' in pan and '1 carga na balança' in pan and bool(prim) and (prim[1] or '').startswith('COLH.dc.html#lg19'), [pan[:500], prim])
    # C5 · link da seção abre o painel do cultivo na COLH
    # o link da seção some quando o primário já leva ao mesmo endereço (sem caminho repetido no painel): vale o do primário
    lk = J("(()=>{const a=[...document.querySelectorAll('main aside a')].find(x=>x.innerText.trim()==='Abrir na Previsão e colheita'); return a?a.getAttribute('href'):'';})()") or (prim or ['', ''])[1] or ''
    p5 = ''
    if lk:
        c.goto(U(lk), 2.0); p5 = J("(()=>{const a=[...document.querySelectorAll('aside')].find(x=>x.getClientRects().length&&/Pivô 19/.test(x.innerText)); return a?a.innerText.replace(/\\s+/g,' ').slice(0,200):'';})()") or ''
    chk('C5 o caminho do painel (seção ou primário) abre a COLH com o painel do Pivô 19', lk == 'COLH.dc.html#lg19' and 'Pivô 19' in p5, [lk, p5])
    # F1 · faixa de filtros
    c.goto(U('OS.dc.html'), 1.4); f_os = json.loads(J(FILTROS) or 'null')
    ok_f = lambda f: bool(f) and f['grupo'] == 'Filtros' and f['texto'] == '' and f['d'] == E.ICONS['filtro'] and f['dica'] == 'Filtros' and not f['velho']
    chk('F1 faixa de filtros na O.S., no Mapa e na Colheita: grupo "Filtros", só o funil com a dica "Filtros", sem "Filtros desta tela"', all(ok_f(f) for f in (f_os, f_mapa, f_colh)), [f_os, f_mapa, f_colh])
    e1 = J("window.__err") or ''
    c.aparelho(390, 844, 2, True); c.goto(U('OS.dc.html'), 1.4); sw = J("document.documentElement.scrollWidth<=window.innerWidth+1")
    chk('F2 390 px: O.S. sem rolagem lateral; sem erro de JS', sw and not e1 and not (J("window.__err") or ''), [sw, e1, J("window.__err")])
finally:
    try: c.close()
    except Exception: pass
    srv.terminate()
print(f'RESULTADO: {len(OK)} ok · {len(FAIL)} falhas')
sys.exit(1 if FAIL else 0)
