# -*- coding: utf-8 -*-
"""Mapa (IN-04) · barra com as nove funções (DEC-0910-36 · PLA-01, decisão do proprietário de 16/10/2026: volta aos nomes da DEC-2609-12).
Oráculos: a lista da decisão (abaixo), os laudos de dados_solo.py (a mesma base do AG-02) e a cor cinza do mapa (LCOR_OP['gray']).
  N1 1440 px: a barra tem os nove nomes, nesta ordem, com ícone e nome à vista (dica "Mostrar … no mapa", DS-48)
  N2 Ordens de serviço: filtros Fases · Avanço · Atrasos · Impedimentos · Insumos; cada visão pinta o mapa (legenda própria); Insumos
     mostra a necessidade × estoque (faixa Produtos/Faltam, painel com a seção Insumos) e troca Fase por Período
  N3 Colheita e produtividade: filtros Situação · Carência e destino; Carência traz "Consultar em" e o rótulo da carência no talhão
  N4 Solo (Santa Rita): talhão sem laudo 0–20 = "Sem laudo", em cinza; nenhum aparece como zero
  N5 nenhuma função antiga sumiu: as 11 camadas de antes são alcançáveis (barra ou filtro); o contexto salvo "Insumos" e o link #car:PV23
     abrem a função nova; no Integrado, "Neste talhão" traz Insumos e Carência e destino com o seu "Ver …"
  N7 Solo (proprietário, 16/10/2026: "coloque icone para importar novo laudo"): ícone só nessa função, por último nas ferramentas do topo do
     mapa, à direita (junto de Selecionar área, Medir, Desenhar e Importar), 32 px no mouse e 44 px no toque, dica e aria-label; abre o mesmo
     Registrar laudo do AG-02 com a fazenda e o talhão do mapa
  N8 barra horizontal (proprietário, 16/10/2026: "a barra de ícones do mapa por estar do lado da barra lateral de ícones dos módulos não fica
     legal"): no alto do bloco, acima da faixa da camada e do mapa, em uma linha a 1440 px; nenhuma coluna entre a lateral dos módulos e o
     mapa; 390 px: rola dentro da barra, alvos de 44 px com o nome, a função ativa à vista e a página sem rolagem lateral
  N6 sem erro de JS
Uso: python3 mapa9_test.py (lê _render ou RENDER_DIR; CDP_GL=1 para o mapa real da Lagoa Grande)."""
import os, sys, json, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
os.environ.setdefault('CDP_GL', '1')
from comp_lib import Chrome, servir
import dados_solo as DS, dados as D

OK, FAIL = [], []
def chk(n, c, info=''):
    (OK if c else FAIL).append(n); print(('OK    ' if c else 'FALHA ') + n + ('' if c else ' · ' + str(info)[:900]), flush=True)

NOVE = ['Integrado', 'Satélite', 'Solo', 'Pragas e doenças', 'Ordens de serviço', 'Irrigação', 'Estádio', 'Colheita e produtividade', 'Custos']
OS_F = ['Fases', 'Avanço', 'Atrasos', 'Impedimentos', 'Insumos']
CINZA = '#C9CFCB'   # LCOR_OP['gray'] do mapa
SR_TAL = [t[0] for t in D.TALHOES]
SR_LAUDO = {l['tal'] for l in DS.LAUDOS if l['faz'] == DS.SR and l['tipo'] == 'solo' and l['prof'] == '0–20'}
SEM = [t for t in SR_TAL if t not in SR_LAUDO]

R = os.environ.get('RENDER_DIR') or os.path.join(HERE, '_render')
p, srv = servir(R); c = Chrome(); J = c.js
U = lambda pg: f'http://127.0.0.1:{p}/{pg}'
TRI = "[...document.querySelectorAll('nav[aria-label=\"Funcionalidades do mapa\"] button')]"
def espera(e, s=30):
    f = time.time() + s
    while time.time() < f:
        if J(e): return True
        time.sleep(.3)
    return False
def abre(ctx, hash_='', lg=False):
    c.goto(U('Main.dc.html'), .3); J("localStorage.clear(); sessionStorage.clear(); 1")
    J(f"sessionStorage.setItem('mapa-ctx',{json.dumps(json.dumps(ctx))}); 1"); c.goto(U('IN-04.dc.html' + hash_), 1.6)
    if lg: espera("!!(window.__LGI&&window.__LGI.pronto)"); time.sleep(1.0)
def camada(nome):
    r = J(f"(()=>{{const b={TRI}.find(b=>b.innerText.trim()==={json.dumps(nome)}); if(!b) return false; b.click(); return true;}})()"); time.sleep(.8); return r
def grupo(rot):   # botões do filtro (grupo segmentado) com o estado
    return json.loads(J(f"JSON.stringify([...document.querySelectorAll('main [role=group][aria-label={json.dumps(rot)}] button')].map(b=>[b.innerText.trim(),b.getAttribute('aria-pressed')]))") or '[]')
def aperta(rot, op):
    r = J(f"(()=>{{const b=[...document.querySelectorAll('main [role=group][aria-label={json.dumps(rot)}] button')].find(b=>b.innerText.trim()==={json.dumps(op)}); if(!b) return false; b.click(); return true;}})()"); time.sleep(.8); return r
selects = lambda: json.loads(J("JSON.stringify([...document.querySelectorAll('main select')].filter(s=>s.getClientRects().length).map(s=>s.getAttribute('aria-label')))") or '[]')
nums = lambda: (J("(document.querySelector('[role=group][aria-label^=\"Indicadores de\"]')||{innerText:''}).innerText") or '').replace('\n', ' ')
ativa = lambda: J(f"{TRI}.filter(b=>b.getAttribute('aria-selected')==='true').map(b=>b.innerText.trim())") or []
BLOCO = "(()=>{const n=document.querySelector('nav[aria-label=\"Funcionalidades do mapa\"]'); let s=n; while(s&&s.parentElement&&!(s.innerText||'').match(/Selecionar área/)) s=s.parentElement; return s;})()"
legenda = lambda: J(f"(()=>{{const s={BLOCO}; const d=s&&[...s.querySelectorAll('div')].filter(x=>x.getClientRects().length&&/position: absolute; left: 12px; bottom: 12px/.test(x.getAttribute('style')||''))[0]; return d?d.innerText.replace(/\\s+/g,' '):'';}})()") or ''
def tal(t):   # rótulo (aria-label sem o "T1: ") e cor do talhão desenhado (Santa Rita)
    # MUX-F1 (17/10/2026): o nome acessível do talhão passou a ser o completo do pedido ("T4, 120 ha, …"); o talhão se acha por data-talhao e o
    # rótulo da camada vem de data-rotulo, o mesmo texto que vinha depois de "T4: " (oráculo obsoleto na forma de achar; a asserção não muda)
    return json.loads(J(f"JSON.stringify((()=>{{const e=[...document.querySelectorAll('svg [role=button]')].find(x=>x.getAttribute('data-talhao')==='{t}'); return e?[e.getAttribute('data-rotulo'),e.getAttribute('fill')]:['',''];}})())") or '["",""]')
def toca(t): J(f"(()=>{{const e=[...document.querySelectorAll('svg [role=button]')].find(x=>x.getAttribute('data-talhao')==='{t}'); e&&e.dispatchEvent(new MouseEvent('click',{{bubbles:true}}));}})()"); time.sleep(.6)
painel = lambda: (J("(()=>{const a=[...document.querySelectorAll('main aside[aria-label]')].find(x=>x.getClientRects().length); return a?a.innerText.replace(/\\s+/g,' '):'';})()") or '')
try:
    c.call('Page.addScriptToEvaluateOnNewDocument', {'source': "window.__err='';addEventListener('error',e=>{window.__err+=(e.message||'erro')+' | ';});"})
    c.aparelho(1440, 900, 1, False)
    # ---------- N1 · barra ----------
    abre({'mf_faz': 'Santa Rita'})
    b = json.loads(J(f"""JSON.stringify({TRI}.map(x=>{{ const w=document.createTreeWalker(x,NodeFilter.SHOW_TEXT); let vis='';
      while(w.nextNode()){{ const n=w.currentNode, r=n.parentElement.getBoundingClientRect(); if(n.textContent.trim()&&r.width>2&&r.height>2) vis+=n.textContent.trim(); }}
      return {{nome:x.textContent.trim(), tit:x.getAttribute('title'), vis, svg:!!x.querySelector('svg')}}; }}))""") or '[]')
    chk('N1 barra: os nove nomes da DEC-2609-12, na ordem da decisão, com ícone e nome à vista e a dica "Mostrar … no mapa"',
        [x['nome'] for x in b] == NOVE and all(x['vis'] == x['nome'] and x['svg'] and x['tit'] == f"Mostrar {x['nome']} no mapa" for x in b), b)
    BARRA = """JSON.stringify((()=>{const n=document.querySelector('nav[aria-label="Funcionalidades do mapa"]'); const w=n.parentElement; const c=document.querySelector('.mapa-corpo').getBoundingClientRect();
      const a=document.querySelector('.mapa-area').getBoundingClientRect(); const t=document.querySelector('main b'); const fx=document.querySelector('main [role=group][aria-label^="Indicadores de"]').getBoundingClientRect();
      const bs=[...n.querySelectorAll('[role=tab]')].map(b=>b.getBoundingClientRect()); const at=n.querySelector('[data-ativo="true"]'); const ar=at?at.getBoundingClientRect():null; const wr=w.getBoundingClientRect();
      return {linhas:new Set(bs.map(r=>Math.round(r.top))).size, h:[...new Set(bs.map(r=>Math.round(r.height)))], nb:Math.round(n.getBoundingClientRect().bottom), ft:Math.round(fx.top), at:Math.round(a.top),
        esq:Math.round(a.left-c.left), rola:w.scrollWidth>w.clientWidth, ativoVis:!!ar&&ar.left>=wr.left-1&&ar.right<=wr.right+1, pag:document.documentElement.scrollWidth-document.documentElement.clientWidth};})())"""
    b8 = json.loads(J(BARRA) or '{}')
    chk('N8a 1440 px: a barra fica no alto do bloco, em uma linha, acima da faixa da camada e do mapa; o mapa começa na borda do bloco (nenhuma coluna de ícones ao lado da lateral dos módulos)',
        b8.get('linhas') == 1 and b8.get('h') == [32] and b8['nb'] <= b8['ft'] and b8['nb'] <= b8['at'] and b8['esq'] <= 2 and b8['pag'] <= 0, b8)
    # ---------- N2 · Ordens de serviço ----------
    camada('Ordens de serviço'); g = grupo('Mostrar'); vis = {}
    for op in OS_F[:4]:
        aperta('Mostrar', op); vis[op] = [legenda(), tal('T4'), tal('T7')[0], selects()]
    chk('N2a Ordens de serviço: Mostrar = Fases · Avanço · Atrasos · Impedimentos · Insumos (Fases ao abrir); Fase como lista suspensa nas quatro visões das ordens',
        [x[0] for x in g] == OS_F and g[0][1] == 'true' and all('Fase' in v[3] for v in vis.values()), [g, {k: v[3] for k, v in vis.items()}])
    chk('N2b cada visão pinta o mapa: Fases (fase da ordem), Avanço (ha feitos ÷ ha da ordem), Atrasos (prazo), Impedimentos (OS-0420 impedida em vermelho); T7 sem ordem',
        'em execução' in vis['Fases'][0] and 'OS-0420 · em execução' == vis['Fases'][1][0]
        and '30/100 ha · 30 %' in vis['Avanço'][1][0] and 'em andamento' in vis['Avanço'][0]
        and vis['Atrasos'][1][0].startswith('OS-0420 · atrasada') and 'vence hoje' in vis['Atrasos'][0]
        and vis['Impedimentos'][1][0].startswith('OS-0420 · impedida') and vis['Impedimentos'][1][1] == '#C8553D'
        and all(v[2] == 'sem ordem' for v in vis.values()), vis)
    aperta('Mostrar', 'Insumos'); n_ins = nums(); s_ins = selects(); per = grupo('Período'); leg = legenda()
    toca('T4'); p4 = painel(); toca('T4')
    chk('N2c Insumos (filtro das Ordens de serviço): faixa Produtos e Faltam, Período no lugar de Fase, legenda do estoque e painel do T4 com a seção Insumos',
        'Produtos' in n_ins and 'Faltam' in n_ins and 'Fase' not in s_ins and [x[0] for x in per] == ['Próximos 30 dias', 'Safra toda']
        and 'estoque cobre' in leg and 'INSUMOS' in p4.upper() and 'Abrir Compra de insumos' in p4, [n_ins, s_ins, per, leg, p4[:300]])
    # ---------- N3 · Colheita e produtividade › Carência e destino (Lagoa Grande, mapa real) ----------
    abre({'mf_faz': 'Lagoa Grande'}, lg=True); camada('Colheita e produtividade'); gc = grupo('Mostrar'); q0 = grupo('Consultar em')
    aperta('Mostrar', 'Carência e destino'); q1 = grupo('Consultar em'); n_car = nums()
    r23 = J("(()=>{const m=window.__LGI&&window.__LGI.markers['PV23']; return m?m.getElement().getAttribute('aria-label'):'';})()") or ''
    chk('N3 Colheita e produtividade: Mostrar = Situação · Carência e destino; "Consultar em" só na carência; Pivô 23 "carência até 26/09" e faixa "Em carência"',
        [x[0] for x in gc] == ['Situação', 'Carência e destino'] and gc[0][1] == 'true' and q0 == [] and [x[0] for x in q1] == ['Hoje', 'Em 7 dias', 'Em 14 dias']
        and 'carência até 26/09' in r23 and 'Em carência' in n_car, [gc, q0, q1, r23, n_car])
    # ---------- N4 · Solo: "Sem laudo" em cinza ----------
    abre({'mf_faz': 'Santa Rita', 'lay': 'Análises de solo'}); nome = J(f"(()=>{{const s={BLOCO}; const b=s&&[...s.querySelectorAll('b')].find(x=>x.getClientRects().length); return b?b.innerText.trim():'';}})()")
    rs = {t: tal(t) for t in SR_TAL}; ruins = {t: rs[t] for t in SEM if rs[t] != ['Sem laudo', CINZA]}
    zero = {t: rs[t][0] for t in SR_TAL if any(z in rs[t][0] for z in (' 0 %', ' 0,0', ': 0'))}
    toca(SEM[0]); ps = painel(); toca(SEM[0])
    chk(f'N4 Solo (Santa Rita): {len(SEM)} talhões sem laudo 0–20 {SEM} = "Sem laudo" em cinza {CINZA}; nenhum como zero; painel e legenda dizem "Sem laudo"',
        nome == 'Solo' and SEM and not ruins and not zero and 'Sem laudo' in ps and 'Registrar laudo' in ps and 'sem laudo' in legenda(), [nome, ruins, zero, ps[:200], legenda()])
    # ---------- N5 · nenhuma função sumiu ----------
    ANTIGAS = {'Integrado': ('barra', 'Integrado'), 'Satélite': ('barra', 'Satélite'), 'Lavoura': ('barra', 'Estádio'), 'Análises de solo': ('barra', 'Solo'),
               'Pragas e doenças': ('barra', 'Pragas e doenças'), 'Carência e destino': ('filtro', 'Colheita e produtividade'), 'Colheita': ('barra', 'Colheita e produtividade'),
               'Irrigação': ('barra', 'Irrigação'), 'Ordens de serviço': ('barra', 'Ordens de serviço'), 'Insumos': ('filtro', 'Ordens de serviço'), 'Custos': ('barra', 'Custos')}
    abre({'mf_faz': 'Santa Rita'}); falta = []
    for antiga, (onde, nova) in ANTIGAS.items():
        ok_b = camada(nova) and ativa() == [nova]
        if onde == 'filtro': ok_b = ok_b and aperta('Mostrar', antiga) and dict(grupo('Mostrar')).get(antiga) == 'true'
        if not ok_b: falta.append(antiga)
    abre({'mf_faz': 'Santa Rita', 'lay': 'Insumos', 'flt': {'Insumos': {'per': 'Safra toda'}}}); ctx_ins = [ativa(), dict(grupo('Mostrar')).get('Insumos'), dict(grupo('Período')).get('Safra toda')]
    abre({'mf_faz': 'Santa Rita', 'lay': 'Integrado'}, '#car:PV23', lg=True); time.sleep(.6)
    lk_car = [ativa(), dict(grupo('Mostrar')).get('Carência e destino'), painel()[:80]]
    J(f"{TRI}.find(b=>b.innerText.trim()==='Integrado').click()"); time.sleep(.8)
    hub = json.loads(J("JSON.stringify((()=>{const s=document.querySelector('main aside[aria-label] section[aria-label=\"Neste talhão\"]'); return s?[...s.children].filter(d=>d.querySelector('button')).map(d=>[d.firstElementChild.innerText.trim(),[...d.querySelectorAll('button')].map(b=>b.innerText.trim())]):[];})())") or '[]')
    ESP_HUB = ['Satélite', 'Solo', 'Pragas e doenças', 'Ordens de serviço', 'Insumos', 'Irrigação', 'Estádio', 'Colheita e produtividade', 'Carência e destino', 'Custos']
    J("(()=>{const b=[...document.querySelectorAll('main aside[aria-label] button')].find(b=>b.innerText.trim()==='Ver insumos'); b&&b.click();})()"); time.sleep(.8)
    ver_ins = [ativa(), dict(grupo('Mostrar')).get('Insumos')]
    chk('N5 nenhuma função sumiu: as 11 camadas de antes são alcançáveis (9 na barra, Insumos e Carência como filtro); contexto "Insumos" e link #car:PV23 abrem a função nova; Integrado do Pivô 23 com Insumos e Carência e destino e o "Ver …" de cada um',
        not falta and ctx_ins == [['Ordens de serviço'], 'true', 'true'] and lk_car[0] == ['Colheita e produtividade'] and lk_car[1] == 'true' and 'Pivô 23' in lk_car[2]
        and [h[0] for h in hub] == ESP_HUB and all(len(h[1]) == 1 and h[1][0].startswith('Ver ') for h in hub) and ver_ins == [['Ordens de serviço'], 'true'],
        [falta, ctx_ins, lk_car, hub, ver_ins])
    # ---------- N7 · ícone "Importar laudo de análise de solo" (proprietário, 16/10/2026) ----------
    IMP = "document.querySelector('main a.mapa-solo-imp')"
    # lugar: dentro das ferramentas do topo do mapa ("Ferramentas do mapa": Selecionar área, Medir, Desenhar e Importar), o último (à direita)
    GEOM = f"""JSON.stringify((()=>{{const a={IMP}; if(!a||!a.getClientRects().length) return null; const r=a.getBoundingClientRect(); const tb=a.closest('[role=toolbar][aria-label="Ferramentas do mapa"]');
      const m=document.querySelector('.mapa-area').getBoundingClientRect(); const vis=tb?[...tb.querySelectorAll('button,a')].filter(x=>x.getClientRects().length):[];
      return {{w:Math.round(r.width),h:Math.round(r.height),al:a.getAttribute('aria-label'),dica:a.getAttribute('data-dica'),txt:a.innerText.trim(),svg:!!a.querySelector('svg'),
        ferramentas:!!tb,ultimo:vis[vis.length-1]===a,vizinhos:vis.map(x=>x.innerText.trim()).filter(Boolean),topo:r.top>=m.top&&r.top<=m.top+60,direita:r.right>=m.right-24,fundo:getComputedStyle(a).backgroundColor,href:a.getAttribute('href')}};}})())"""
    errs0 = J("window.__err") or ''
    abre({'mf_faz': 'Santa Rita', 'lay': 'Análises de solo'}); g1 = json.loads(J(GEOM) or 'null'); fora = {}
    for nm in [x for x in NOVE if x != 'Solo']: camada(nm); fora[nm] = J(f"!!{IMP}")
    abre({'mf_faz': 'Santa Rita', 'lay': 'Análises de solo', 'tsel': ['T3']}); h3 = (json.loads(J(GEOM) or 'null') or {}).get('href', '')
    DLG = "(()=>{const d=[...document.querySelectorAll('[role=dialog]')].find(x=>x.getClientRects().length&&/Registrar laudo/.test(x.innerText)); return d?[location.pathname.split('/').pop(),[...d.querySelectorAll('select')].map(s=>s.options[s.selectedIndex]?s.options[s.selectedIndex].text:'')]:null;})()"
    J(f"{IMP}.click()"); espera(f"(()=>{{try{{ const x={DLG}; return !!(x&&x[1].some(t=>t.split(' · ')[0]==='T3')); }}catch(e){{ return false; }}}})()", 30)   # espera a navegação e o formulário com o talhão
    dlg = json.loads(J(f"JSON.stringify({DLG})") or 'null')
    chk('N7a Solo: ícone só com o desenho, dica e aria-label "Importar laudo de análise de solo", 32 × 32 px no mouse, o último das ferramentas no topo do mapa, à direita (junto de Selecionar área e Medir); ausente nas outras 8 funções',
        bool(g1) and g1['al'] == g1['dica'] == 'Importar laudo de análise de solo' and g1['txt'] == '' and g1['svg'] and g1['w'] == 32 and g1['h'] == 32
        and g1['ferramentas'] and g1['ultimo'] and g1['topo'] and g1['direita'] and g1['fundo'] == 'rgb(255, 255, 255)' and {'Selecionar área', 'Medir'} <= set(g1['vizinhos'])
        and not any(fora.values()), [g1, fora])
    chk('N7b ativar abre o mesmo "Registrar laudo" do AG-02 (importação do PDF), com Santa Rita e o talhão escolhido no mapa (T3)',
        h3 == 'AG-02.dc.html#registrar=' + 'Santa%20Rita%2FT3' and bool(dlg) and dlg[0] == 'AG-02.dc.html' and 'Santa Rita' in dlg[1] and any(x.split(' · ')[0] == 'T3' for x in dlg[1]), [h3, dlg])
    c.aparelho(390, 844, 2, True); abre({'mf_faz': 'Santa Rita', 'lay': 'Análises de solo'}); g2 = json.loads(J(GEOM) or 'null')
    lat = J("document.documentElement.scrollWidth-document.documentElement.clientWidth")
    chk('N7c 390 px com toque: o ícone tem 44 × 44 px, segue nas ferramentas do topo do mapa e a página não rola de lado', bool(g2) and g2['w'] >= 44 and g2['h'] >= 44 and g2['ferramentas'] and g2['ultimo'] and (lat or 0) <= 0, [g2, lat])
    camada('Custos'); time.sleep(.4); b8m = json.loads(J(BARRA) or '{}')
    nomes390 = json.loads(J(f"JSON.stringify({TRI}.map(b=>[b.innerText.trim(),Math.round(b.getBoundingClientRect().height)]))") or '[]')
    chk('N8b 390 px com toque: barra no alto, em uma linha, rolável dentro dela, 9 alvos de 44 px com o nome à vista; trocar para Custos a deixa à vista; página sem rolagem lateral',
        b8m.get('linhas') == 1 and b8m.get('h') == [44] and b8m.get('rola') and b8m.get('ativoVis') and ativa() == ['Custos'] and b8m['nb'] <= b8m['at']
        and [x[0] for x in nomes390] == NOVE and b8m['pag'] <= 0, [b8m, nomes390, ativa()])
    chk('N6 sem erro de JS', not (errs0 or J("window.__err") or ''), [errs0, J("window.__err")])
finally:
    try: c.close()
    except Exception: pass
    srv.terminate()
print(f'RESULTADO: {len(OK)} ok · {len(FAIL)} falhas')
sys.exit(1 if FAIL else 0)
