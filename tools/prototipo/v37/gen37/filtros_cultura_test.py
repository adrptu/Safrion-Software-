# -*- coding: utf-8 -*-
"""Cultura e Talhão no filtro principal (proprietário, 13/10/2026: "em ordem de serviço coloque no filtro principal da tela... também cultura e
talhão. nas demais telas que isso for bastante essencial e ajudar o usuário, pode por também"). Confere no navegador:
  F1 Produção (Colheita, Recebimento e Estoque de produto): a faixa "Filtros desta tela" tem Cultura; escolher uma cultura deixa só linhas
     dela (e menos que antes quando há outras); "Todas" volta tudo
  F2 Colheita: Talhão segue a Cultura (só talhões dela) e filtra as linhas pelo talhão
  F3 O.S.: os avisos que eram do seletor de talhão da barra voltaram (revisão do agente de testes, 13/10): o total de O.S. distintas na Tabela
     agrupada por Talhão (VISOES-2, 14/10: Tabela + "Agrupar por" Talhão; a nota diz "N O.S. · X ha · a O.S. de vários talhões aparece em cada
     um e conta uma vez no total") e o aviso de talhão que sai do filtro ao trocar a fazenda, com o nome do talhão (não o ID)
  F4 390 px: as listas da faixa com alvo de toque ≥ 44 px (aceite de campo, NAV-2CB-TOQUE-01 do Codex); sem rolagem lateral; sem erro de JS
  F5 Pragas e doenças (AG-01): Cultura e Talhão na faixa, com oráculo pelos dados do MIP (dados_mip.VIS × TAL): opções = o que tem vistoria
     na fazenda; Cultura deixa só as vistorias dela (lista e chip "Todas"); o Talhão segue a Cultura; trocar a fazenda tira o talhão de
     outra fazenda com aviso pelo nome; abrir pelo link uma vistoria escondida pela Cultura tira só esse filtro e mostra a linha
  F6 PROD-C961-CONTEXTO-01 (revisão Codex de 13/10): Cultura e Talhão escolhidos na faixa voltam ao recarregar a tela e ao sair e
     voltar (Colheita, Recebimento e Estoque de produto; Colheita também a 390 px)
Uso: python3 filtros_cultura_test.py (lê _render ou RENDER_DIR)."""
import os, sys, json, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, servir, troca_visao
from tabelas_lib import Grade
import dados_mip as DM

OK, FAIL = [], []
def chk(n, c, info=''):
    (OK if c else FAIL).append(n); print(('OK    ' if c else 'FALHA ') + n + ('' if c else ' · ' + str(info)[:700]), flush=True)

R = os.environ.get('RENDER_DIR') or os.path.join(HERE, '_render')
p, srv = servir(R); c = Chrome(); J = c.js
U = lambda pg: f'http://127.0.0.1:{p}/{pg}'
CULTURAS = ['Café', 'Feijão', 'Mamão Formosa', 'Milho', 'Soja']
ROWS = """JSON.stringify([...document.querySelectorAll('[role=table]')].filter(t=>t.offsetParent).flatMap(t=>[...t.querySelectorAll('[role=row]')].slice(1)
  .filter(r=>r.offsetParent&&!r.classList.contains('g2tot')).map(r=>r.innerText.replace(/\\s+/g,' '))))"""
def opts(al): return json.loads(J(f"JSON.stringify([...document.querySelectorAll('select[aria-label=\"{al}\"] option')].map(o=>o.textContent))") or '[]')
def sel(al, val):
    J(f"""(()=>{{const s=document.querySelector('select[aria-label="{al}"]'); if(!s) return; s.value={json.dumps(val)}; s.dispatchEvent(new Event('change',{{bubbles:true}}));}})()"""); time.sleep(.7)
def limpa(): c.goto(U('Main.dc.html'), .3); J("localStorage.clear(); sessionStorage.clear(); 1")
def so_da(rows, cu):   # linha de outra cultura = contém o nome de outra cultura e não o desta
    outras = [x for x in CULTURAS if x != cu and not (cu == 'Mamão Formosa' and x == 'Mamão')]
    return [r for r in rows if any(o in r for o in outras) and cu not in r]

def folhas_colheita(mobile):
    if not mobile:
        return Grade(J).dicts(so_folhas=True)
    # Controle público confirmado no DOM pelo revisor (6254915626).
    abriu = J("""(()=>{const bs=[...document.querySelectorAll('button.g2xtog')]
      .filter(b=>/Expandir tudo/.test(b.innerText)&&b.getClientRects().length);
      if(bs.length>1) throw Error('Expandir tudo ambíguo');
      if(!bs.length) return false; bs[0].click(); return true;})()""")
    if abriu:
        limite = time.monotonic() + 5
        while not J("[...document.querySelectorAll('.pr-cards button[role=listitem]')].some(r=>r.getClientRects().length)"):
            if time.monotonic() >= limite: raise AssertionError('Colheita não mostrou folhas após Expandir tudo')
            time.sleep(.05)
    # Produção tem cartões próprios (.pr-card), não cartões da grade G2.
    # Ler somente folhas visíveis; ausência de cartões mantém F2 vermelho.
    return J("""(()=>{
      const listas=[...document.querySelectorAll('[role=list][aria-label="Lista em cartões"]')]
        .filter(g=>g.getClientRects().length);
      if(listas.length!==1) throw Error('Lista de cartões da Colheita ausente ou ambígua');
      return [...listas[0].querySelectorAll('button[role=listitem]')]
        .filter(r=>r.getClientRects().length)
        .map(r=>({'Talhão · variedade':r.querySelector('b').innerText.replace(/\\s+/g,' ').trim(),
          texto:r.innerText.replace(/\\s+/g,' ').trim()}));})()""") or []

try:
    c.aparelho(1440, 900, 1, False); c.call('Page.addScriptToEvaluateOnNewDocument', {'source': "window.__err='';addEventListener('error',e=>{window.__err+=(e.message||'erro')+' | ';});"})
    res = {}
    for pg, cu in (('COLH.dc.html', 'Soja'), ('CARGA.dc.html', 'Soja'), ('PROD.dc.html', 'Soja')):
        limpa(); c.goto(U(pg), 1.4)
        o = opts('Filtrar por cultura'); r0 = json.loads(J(ROWS) or '[]'); sel('Filtrar por cultura', cu); r1 = json.loads(J(ROWS) or '[]')
        ruins = so_da(r1, cu); sel('Filtrar por cultura', 'Todas'); r2 = json.loads(J(ROWS) or '[]')
        res[pg] = (o, len(r0), len(r1), ruins[:2], len(r2))
    chk('F1 Colheita, Recebimento e Estoque de produto: Cultura na faixa; "Soja" deixa só linhas de soja (menos que antes); "Todas" volta tudo',
        all(v[0] and v[0][0] == 'Todas' and 'Soja' in v[0] and v[2] < v[1] and not v[3] and v[4] == v[1] for v in res.values()), res)
    # base-verde3: T2 não está em produção; P1 existe no catálogo atual. TAB-12 nasce recolhido.
    for largura, mobile in ((1440, False), (390, True)):
        c.aparelho(largura, 844 if mobile else 900, 2 if mobile else 1, mobile)
        limpa(); c.goto(U('COLH.dc.html'), 1.4)
        t0 = opts('Filtrar por talhão'); sel('Filtrar por cultura', 'Café'); t1 = opts('Filtrar por talhão')
        sel('Filtrar por cultura', 'Todas')
        antes = folhas_colheita(mobile)
        esperadas = [x for x in antes if x.get('Talhão · variedade', '').split(' ')[0] == 'P1']
        sel('Filtrar por talhão', 'P1'); depois = folhas_colheita(mobile)
        chk(f'F2 {largura} Colheita: Café → só C1; P1 mantém exatamente suas folhas e exclui as demais',
            t0[:1] == ['Todos'] and 'P1' in t0 and len(t0) > 3 and t1 == ['Todos', 'C1']
            and esperadas and len(esperadas) < len(antes) and depois == esperadas,
            [t0, t1, esperadas, depois])
    c.aparelho(1440, 900, 1, False)
    # F3 · O.S.: total do agrupado e aviso do talhão que sai do filtro
    limpa(); c.goto(U('OS.dc.html'), 1.4); ag = troca_visao(J, 'agrupada'); time.sleep(.8)   # VISOES-2: Tabela + "Agrupar por" Talhão
    gt = J("(()=>{const n=[...document.querySelectorAll('[role=note]')].find(x=>/O\\.S\\. · .* ha · a O\\.S\\. de vários talhões aparece em cada um e conta uma vez no total/.test(x.innerText)&&x.getClientRects().length); return n?n.innerText.trim():'';})()") or ''
    # a conta de O.S. distintas contra as linhas dos grupos é do tabelas_os_test (TF06); aqui, como antes, a nota à vista
    chk('F3 O.S. › Tabela agrupada por Talhão: o total de O.S. distintas à vista ("N O.S. · X ha · a O.S. de vários talhões aparece em cada um e conta uma vez no total")',
        ag == 'ok' and bool(gt) and int(gt.split(' ')[0]) > 0, [ag, gt])
    limpa(); c.goto(U('OS.dc.html'), 1.4); sel('Filtrar por fazenda', 'Lagoa Grande'); sel('Filtrar por talhão', 'Lagoa Grande|PV04'); sel('Filtrar por fazenda', 'Santa Rita')
    msg = J("(()=>{const n=[...document.querySelectorAll('[role=status]')].find(x=>/saiu do filtro/.test(x.innerText)&&x.getClientRects().length); return n?n.innerText:'';})()") or ''
    chk('F3 O.S.: trocar a fazenda tira o talhão do filtro com aviso, pelo nome ("Pivô 4"), não pelo ID', 'Pivô 4' in msg and 'PV04' not in msg, msg)
    # F5 · Pragas e doenças: oráculo pelos dados do MIP
    VR = "JSON.stringify([...document.querySelectorAll('[role=row][data-rid]')].filter(r=>r.offsetParent&&/^VIS-/.test(r.getAttribute('data-rid'))).map(r=>r.getAttribute('data-rid')).sort())"
    tot = lambda: J("(()=>{const b=[...document.querySelectorAll('[aria-label=\"Filtrar por situação\"] button')][0]; return b?b.innerText.replace(/\\s+/g,' '):'';})()") or ''
    val = lambda al: J(f"(document.querySelector('select[aria-label=\"{al}\"]')||{{}}).value") 
    cul = lambda v: DM.TAL[v['tal']]['cultura']
    sr = [v for v in DM.VIS if v['faz'] == 'Santa Rita']
    esp_c = ['Todas'] + sorted({cul(v) for v in sr if cul(v)})
    fei = sorted(v['id'] for v in sr if cul(v) == 'Feijão'); fei_t = ['Todos'] + sorted({DM.TAL[v['tal']]['rot'] for v in sr if cul(v) == 'Feijão'})
    limpa(); c.goto(U('AG-01.dc.html'), 1.4); sel('Filtrar por fazenda', 'Santa Rita')
    o5 = opts('Filtrar por cultura'); r0 = json.loads(J(VR) or '[]'); sel('Filtrar por cultura', 'Feijão'); r1 = json.loads(J(VR) or '[]'); t5 = opts('Filtrar por talhão'); tt = tot()
    chk('F5 Pragas e doenças: Cultura com as culturas que têm vistoria na fazenda; "Feijão" deixa só as vistorias de feijão (lista e chip "Todas"); o Talhão segue a Cultura',
        o5 == esp_c and len(r0) == len(sr) and r1 == fei and tt == f'Todas {len(fei)}' and t5 == fei_t, [o5, esp_c, len(r0), r1, fei, tt, t5, fei_t])
    lg4 = sorted(v['id'] for v in DM.VIS if v['tal'] == 'PV04')
    limpa(); c.goto(U('AG-01.dc.html'), 1.4); sel('Filtrar por fazenda', 'Lagoa Grande'); sel('Filtrar por talhão', 'PV04'); r4 = json.loads(J(VR) or '[]')
    sel('Filtrar por fazenda', 'Santa Rita'); tv = val('Filtrar por talhão'); toast = J("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).join(' | ')") or ''; r5 = json.loads(J(VR) or '[]')
    chk('F5 Pragas e doenças: Talhão "Pivô 4" deixa só as vistorias dele; trocar para Santa Rita tira o talhão do filtro com aviso pelo nome',
        r4 == lg4 and tv == '' and 'Pivô 4' in toast and 'saiu do filtro' in toast and len(r5) == len(sr), [r4, lg4, tv, toast[:160], len(r5)])
    soja = next(v['id'] for v in sr if cul(v) == 'Soja')
    limpa(); c.goto(U('AG-01.dc.html'), 1.4); sel('Filtrar por fazenda', 'Santa Rita'); sel('Filtrar por cultura', 'Feijão')
    J(f"location.hash='#{soja}'; 1"); time.sleep(1.0); cv = val('Filtrar por cultura'); r6 = json.loads(J(VR) or '[]')
    chk(f'F5 Pragas e doenças: abrir {soja} (soja) pelo link com "Feijão" no filtro tira só a Cultura e mostra a linha', cv == 'Todas' and soja in r6 and val('Filtrar por fazenda') == 'Santa Rita', [cv, r6])
    # F6 · contexto guardado (sair e voltar, recarregar; 1440 e 390 px na Colheita)
    val = lambda al: J(f"(document.querySelector('select[aria-label=\"{al}\"]')||{{}}).value")
    f6 = {}
    for pg, w, m in (('COLH.dc.html', 1440, False), ('COLH.dc.html', 390, True), ('CARGA.dc.html', 1440, False), ('PROD.dc.html', 1440, False)):
        c.aparelho(w, 900 if w > 400 else 844, 2 if m else 1, m); limpa(); c.goto(U(pg), 1.4); sel('Filtrar por cultura', 'Soja')
        tal = ''
        if pg == 'COLH.dc.html':
            ts = [o for o in json.loads(J("JSON.stringify([...document.querySelectorAll('select[aria-label=\"Filtrar por talhão\"] option')].map(o=>o.value))") or '[]') if o]
            tal = ts[0] if ts else ''; sel('Filtrar por talhão', tal)
        c.goto(U(pg), 1.4); r1 = [val('Filtrar por cultura'), val('Filtrar por talhão') if tal else '']
        c.goto(U('MOD-AGR.dc.html'), .8); c.goto(U(pg), 1.4); r2 = [val('Filtrar por cultura'), val('Filtrar por talhão') if tal else '']
        f6[f'{pg}@{w}'] = (tal, r1, r2)
    chk('F6 Cultura e Talhão voltam ao recarregar e ao sair e voltar (Colheita 1440 e 390 px, Recebimento, Estoque de produto)',
        all(t[1] == ['Soja', t[0]] and t[2] == ['Soja', t[0]] for t in f6.values()) and f6['COLH.dc.html@1440'][0] != '', f6)
    c.aparelho(1440, 900, 1, False)
    # F4 · celular
    c.aparelho(390, 844, 2, True); alt = {}
    for pg in ('OS.dc.html', 'COLH.dc.html', 'PROD.dc.html', 'AG-01.dc.html'):
        limpa(); c.goto(U(pg), 1.4)
        alt[pg] = [json.loads(J("JSON.stringify([...document.querySelectorAll('.mf-tela select')].map(s=>Math.round(s.getBoundingClientRect().height)))") or '[]'),
                   J("document.documentElement.scrollWidth-document.documentElement.clientWidth")]
    chk('F4 390 px: listas da faixa com alvo ≥ 44 px e sem rolagem lateral', all(v[0] and min(v[0]) >= 44 and (v[1] or 0) <= 0 for v in alt.values()), alt)
    chk('F4 sem erro de JS', not (J("window.__err||''") or ''), J("window.__err||''"))
finally:
    try: c.close()
    except Exception: pass
    srv.terminate()
print(f'RESULTADO: {len(OK)} ok · {len(FAIL)} falhas')
sys.exit(1 if FAIL else 0)

