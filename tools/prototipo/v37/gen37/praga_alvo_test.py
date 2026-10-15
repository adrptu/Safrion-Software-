# -*- coding: utf-8 -*-
"""Teste CDP · AG-07 Praga-alvo (pedido do proprietário, 09/10/2026: "na consulta agrofit tem que aparecer colunas das pragas alvo").
Com a cultura escolhida, a lista tem uma linha por USO na cultura (produto × praga-alvo) com Praga-alvo e Nome científico em colunas próprias,
filtro e ordenação no cabeçalho, busca por praga-alvo e a ficha aberta já com a cultura e o alvo do uso; a tabela "Usos registrados" da
ficha tem uma variável por coluna e ordena pelo cabeçalho. Esperados recalculados dos arquivos servidos (agrofit_*.json).
Fluxos: normal (1440 e 390 px), recusa (busca sem resultado; usos que não carregam → lista por produto + "Tentar de novo"), repetição
(trocar e voltar a cultura, recarregar). Capturas em _probe/praga_alvo_*.png. Uso: python3 praga_alvo_test.py"""
import sys, os, re, time, subprocess, json, unicodedata
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from cdp import Chrome
from journeys import free
R = os.path.join(HERE, '_render'); PROBE = os.path.join(HERE, '_probe'); os.makedirs(PROBE, exist_ok=True); p = free()
ld = lambda f: json.load(open(os.path.join(R, f), encoding='utf-8'))
META = ld('agrofit_meta.json'); IDX = ld('agrofit_indice.json')
U = {}
for i in range(META['contagens']['fatias_cultura']): U.update(ld(f'agrofit_usos_cultura_{i}.json')['culturas'])
CU = IDX['culturas']; TD = IDX['todasCulturas']; AL = IDX['alvos']; NP = META['contagens']['registros']
def nz(t): return ''.join(ch for ch in unicodedata.normalize('NFD', str(t)) if not unicodedata.combining(ch)).lower()
def nf(n): return f'{int(n):,}'.replace(',', '.')
cid = lambda n: next(i for i, c in enumerate(CU) if c[0] == n)
aid = lambda s: next(i for i, a in enumerate(AL) if a[0] == s)
SJ, MA = cid('Soja'), cid('Mamão'); PH = aid('Phakopsora pachyrhizi'); FN = AL[PH][1][0]
F = {c: i for i, c in enumerate(IDX['campos'])}; REG = [str(r[F['registro']]) for r in IDX['produtos']]
USJ = [(i, c, a) for c in (SJ, TD) for a, ps in U[str(c)] for i in ps]
N_SJ = len(USJ); N_FN = sum(1 for i, c, a in USJ if FN in (AL[a][1] or []))
def uh(c, a): al = AL[a]; return nz(CU[c][0] + ' ' + al[0] + ' ' + ' '.join(al[1] or []))
N_BUSCA = sum(1 for i, c, a in USJ if all(w in uh(c, a) for w in ('ferrugem', 'asiatica')))   # nenhum produto tem essas palavras no nome
srv = subprocess.Popen(['python3', '-m', 'http.server', str(p), '--bind', '127.0.0.1', '--directory', R], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)
c = None; OK = []; FAIL = []; ERRS = []
def chk(nome, cond, info=''):
    (OK if cond else FAIL).append(nome); print(('OK   ' if cond else 'FALHA'), nome, ('' if cond else str(info)[:900]), flush=True)
t0 = time.time()
try:
    c = Chrome(port=free()); J = c.js; c.size(1440, 900)
    c.call('Page.addScriptToEvaluateOnNewDocument', {'source': "window.__errs=[];window.addEventListener('error',e=>window.__errs.push(String(e.message)));const __ce=console.error;console.error=function(){window.__errs.push([...arguments].map(String).join(' ').slice(0,300));__ce.apply(console,arguments);};"
        # falha simulada dos usos por cultura (só com ?falhaUsos=1): a lista fica por produto e o aviso oferece "Tentar de novo"
        "if(location.search.indexOf('falhaUsos=1')>=0){ window.__agFailU=true; const f0=window.fetch; window.fetch=function(u,o){ if(window.__agFailU&&String(u).indexOf('agrofit_usos_cultura')>=0) return Promise.reject(new Error('rede indisponível (simulada)')); return f0.apply(this,arguments); }; }"})
    def junta(pag): ERRS.extend(f'{pag}: {e}' for e in (J("(window.__errs||[]).filter(e=>e.indexOf(\"reading 'g2toast'\")<0)") or []))
    U_ = lambda f: f'http://127.0.0.1:{p}/{f}'
    J0 = "window.__setv=(sel,val)=>{const el=document.querySelector(sel); if(!el) return 'SEM '+sel; const pr=el.tagName==='SELECT'?HTMLSelectElement.prototype:HTMLInputElement.prototype; Object.getOwnPropertyDescriptor(pr,'value').set.call(el,val); el.dispatchEvent(new Event(el.tagName==='SELECT'?'change':'input',{bubbles:true})); return 'ok';}; 1"
    setv = lambda sel, val: (J(f"__setv({json.dumps(sel)},{json.dumps(val)})"), time.sleep(.45))[0]
    cnt = lambda: J("(()=>{const s=[...document.querySelectorAll('main span')].find(x=>/ de [\\d.]+ (produtos|usos em .+)$/.test(x.innerText.trim())); return s?s.innerText.trim():'';})()") or ''
    cab = lambda: [nz(x).replace('⇅', '').replace('▾', '').replace('▲', '').replace('▼', '').strip() for x in (J("[...document.querySelectorAll('main [role=columnheader]')].map(h=>h.innerText.replace(/\\s+/g,' '))") or [])]
    linhas = lambda: J("[...document.querySelectorAll('main [role=table] [role=row].g2ed')].map(r=>[...r.querySelectorAll('[role=cell]')].map(x=>x.innerText.trim()))") or []
    FX = 'aside[aria-label^="Ficha"]'
    ficha = lambda: J(f"(document.querySelector('{FX}')||{{}}).innerText||''") or ''
    def pronto(t=40, usos=True):
        for _ in range(int(t / .25)):
            if J("!!(window.__agx&&__agx.AGX.st==='ok')") and (not usos or J("__agx.AGX.uSt==='ok'")): J(J0); return True
            time.sleep(.25)
        J(J0); return False
    def combo(rot, txt):   # Cultura e Praga-alvo são listas de escolha (13/10: um campo de busca por tela): a 1ª opção que começa com o texto (ou o contém)
        r = J(f"""(()=>{{const s=document.querySelector('select[aria-label={json.dumps(rot)}]'); if(!s) return 'sem lista';
          const n=x=>String(x||'').normalize('NFD').replace(/[\\u0300-\\u036f]/g,'').toLowerCase().trim(); const q=n({json.dumps(txt)}); const os=[...s.options];
          const o=q===''?os.find(o=>o.value===''):(os.find(o=>o.value!==''&&n(o.text).startsWith(q))||os.find(o=>o.value!==''&&n(o.text).indexOf(q)>=0));
          if(!o) return 'sem opção'; s.value=o.value; s.dispatchEvent(new Event('change',{{bubbles:true}})); return 'ok';}})()"""); time.sleep(.6)
        return r
    clica = lambda raiz, txt: J(f"(()=>{{const b=[...document.querySelectorAll({json.dumps(raiz + ' button')})].find(x=>x.innerText.replace(/\\s+/g,' ').trim().startsWith({json.dumps(txt)})); if(!b) return 'NÃO ACHEI'; b.click(); return 'ok';}})()")
    # trilhas reais da grade (o desenho em colunas não quebra: cada linha com N células numa mesma faixa)
    trilhas = lambda: J("(()=>{const t=document.querySelector('main .g2rola [role=table]'); return t?getComputedStyle(t).gridTemplateColumns.split(' ').length:0;})()")
    alinhado = lambda: J("(()=>{const rs=[...document.querySelectorAll('main [role=table] [role=row].g2ed')].slice(0,12); return rs.length>0&&rs.every(r=>{const cs=[...r.querySelectorAll('[role=cell]')]; const l=cs.map(x=>Math.round(x.getBoundingClientRect().left)); return cs.length&&l.every((x,i)=>i===0||x>l[i-1]);});})()")   # célula que quebra de faixa volta à esquerda
    shot = lambda n: c.shot(os.path.join(PROBE, f'praga_alvo_{n}.png'))
    # cdp.Chrome mostra todas as colunas (como quem escolheu "todas" no painel "Colunas"); o padrão sem Tox · amb (15/10/2026) está em agrofit_faixa_test.py
    COLS_U = ['produto · registro', 'praga-alvo', 'nome cientifico', 'cultura do uso', 'ingrediente ativo · grupo quimico', 'classe · modo de acao', 'tox · amb', 'na fazenda']
    COLS_P = ['produto · registro', 'ingrediente ativo · grupo quimico', 'classe · modo de acao', 'culturas', 'alvos', 'tox · amb', 'na fazenda']   # Alvos: 13/10 (proprietário)

    # ---------- 1 · normal (1440): sem cultura, por produto; com Soja, uma linha por uso com Praga-alvo e Nome científico ----------
    c.goto(U_('AG-07.dc.html'), wait=1.0); pr = pronto()
    a0 = cab(); n0 = cnt(); L0 = linhas()
    combo('Cultura', 'soja'); a1 = cab(); n1 = cnt(); L = linhas(); tr = trilhas(); al1 = alinhado()
    pp = [r[1] for r in L]; cc = [r[2] for r in L]; uc = {r[3] for r in L}
    chk(f'1 sem cultura: 7 colunas por produto ("{nf(NP)} de {nf(NP)} produtos"); Cultura = Soja: 8 colunas por uso, "{nf(N_SJ)} de {nf(N_SJ)} usos em Soja", Praga-alvo e Nome científico preenchidos, grade em 8 trilhas',
        pr and a0 == COLS_P and n0 == f'{nf(NP)} de {nf(NP)} produtos' and a1 == COLS_U and n1 == f'{nf(N_SJ)} de {nf(N_SJ)} usos em Soja'
        and len(L) == 50 and all(len(r) == 8 for r in L) and any(x and x != '—' for x in pp) and all(x for x in cc) and uc <= {'Soja', 'Todas as culturas'} and tr == 8 and al1,
        [tr, al1, pr, a0, n0, a1, n1, len(L), L[:1]])
    shot('soja_1440')
    # Alvos (proprietário, 13/10/2026: "coloque coluna dos alvos na planilha"): oráculo pelos usos publicados (agrofit_usos_cultura_*.json):
    # o produto tem os alvos de todos os seus usos, em qualquer cultura; a célula diz quantos e mostra até 3 nomes comuns (+ o resto)
    REG = {str(r[0]): k for k, r in enumerate(IDX['produtos'])}
    def alvos_de(pi): return {a for cu_ in U for a, ps in U[cu_] if pi in ps}
    def nome_alvo(a): al = AL[a] if a < len(AL) else ['', []]; return (al[1][0] if al[1] else al[0]) or '(alvo não informado)'
    ruins = []
    for r in L0[:12]:
        reg = re.search(r'Reg\. (\d+)', r[0] if r else ''); pi = REG.get(reg.group(1)) if reg else None
        if pi is None: ruins.append(('sem registro', r[:1])); continue
        az = alvos_de(pi); t = (r[4] if len(r) > 4 else '').split('\n'); nm = [x.strip() for x in (t[-1] if len(t) > 1 else '').split(',') if x.strip()]
        mais = re.match(r'(.*) \+(\d+)$', nm[-1]) if nm else None
        if mais: nm[-1] = mais.group(1)
        if t[0] != f'{nf(len(az))} {"alvo" if len(az) == 1 else "alvos"}' or not set(nm) <= {nome_alvo(a) for a in az} or len(nm) != min(3, len(az)) or (len(az) > 3) != bool(mais) or (mais and int(mais.group(2)) != len(az) - 3):
            ruins.append((reg.group(1), t, len(az)))
    chk('1b sem cultura, coluna Alvos: cada produto com o número de alvos dos seus usos (todas as culturas) e até 3 nomes comuns + o resto (oráculo pelos usos publicados)',
        L0 and not ruins, ruins[:3])

    # ---------- 2 · ordenação pelo cabeçalho (Praga-alvo A → Z) ----------
    J("document.querySelector('main [role=columnheader] button[aria-label=\"Ordenar por Praga-alvo\"]').click()"); time.sleep(.8)
    srt = [r[1] for r in linhas()][:30]
    ok2 = J(f"(()=>{{const a={json.dumps(srt)}.filter(x=>x&&x!=='—'); return a.length>20&&a.every((x,i)=>i===0||x.localeCompare(a[i-1],'pt-BR',{{numeric:true,sensitivity:'base'}})>=0);}})()")
    chk('2 ordenar por Praga-alvo (cabeçalho): as primeiras linhas em ordem alfabética', ok2 is True, srt[:8])
    J("document.querySelector('main [role=columnheader] button[aria-label=\"Ordenar por Praga-alvo\"]').click()"); time.sleep(.3)
    J("document.querySelector('main [role=columnheader] button[aria-label=\"Ordenar por Praga-alvo\"]').click()"); time.sleep(.5)   # volta à ordem da lista
    # ---------- 3 · filtro da coluna Praga-alvo pelo nome comum ----------
    J("document.querySelector('main [role=columnheader] button[aria-label=\"Filtrar Praga-alvo\"]').click()"); time.sleep(.5)
    clica('[role=dialog][aria-label="Filtrar Praga-alvo"]', 'Limpar'); time.sleep(.3); setv('#g2fq_g_agf', FN)   # desmarca tudo, procura o nome e marca só ele
    J(f"(()=>{{const l=[...document.querySelectorAll('[role=dialog][aria-label=\"Filtrar Praga-alvo\"] label')].find(x=>x.innerText.trim().startsWith({json.dumps(FN)})); if(l) l.querySelector('input').click();}})()"); time.sleep(.3)
    clica('[role=dialog][aria-label="Filtrar Praga-alvo"]', 'OK'); time.sleep(.8)
    n3 = cnt(); L3 = linhas()
    chk(f'3 filtro da coluna Praga-alvo = "{FN}": "{nf(N_FN)} de {nf(N_SJ)} usos em Soja", só linhas com esse nome comum',
        n3 == f'{nf(N_FN)} de {nf(N_SJ)} usos em Soja' and L3 and all(FN in r[1] for r in L3), [n3, L3[:2]])
    shot('filtro_praga')
    # 3b · A5 (revisão de 10/10): com o filtro da coluna, Classe e Orgânicos (listas da faixa "Filtros", 15/10/2026) contam as linhas filtradas e o
    # número da opção é o que a lista mostra ao escolher
    FXS = 'main [role=group][aria-label="Filtros"] select'
    chips = lambda: dict((m[0], int(m[1].replace('.', ''))) for m in (J(f"[...document.querySelectorAll({json.dumps(FXS)})].flatMap(s=>[...s.options].map(o=>o.text.trim())).filter(t=>/^(Todas|Fungicida|Só aprovados) \\([\\d.]+\\)$/.test(t)).map(t=>[t.replace(/ \\([\\d.]+\\)$/,''),t.match(/([\\d.]+)\\)$/)[1]])") or []))
    n_ = lambda: int((cnt().split(' de ')[0] or '0').replace('.', ''))
    k0 = chips(); setv(FXS + '[aria-label="Classe"]', 'Fungicida'); time.sleep(.5); nF = n_(); k1 = chips(); setv(FXS + '[aria-label="Orgânicos"]', 'S'); time.sleep(.5); nO = n_()
    setv(FXS + '[aria-label="Orgânicos"]', ''); setv(FXS + '[aria-label="Classe"]', '')
    chk(f'3b A5 · com o filtro "{FN}", Classe e Orgânicos contam as linhas filtradas: Todas = {nf(N_FN)}, Fungicida = a lista com a classe, Só aprovados (com Fungicida) = a lista com os dois',
        k0.get('Todas') == N_FN and k0.get('Fungicida') == nF > 0 and k1.get('Só aprovados') == nO, [k0, nF, k1, nO])
    clica('main', 'Limpar filtros'); time.sleep(.6)
    # ---------- 4 · busca por praga-alvo (sem acento, no mesmo uso) ----------
    combo('Cultura', 'soja'); setv('main input[type=search]', 'ferrugem ASIATICA'); n4 = cnt(); L4 = linhas()
    chk(f'4 busca "ferrugem ASIATICA" em Soja: {nf(N_BUSCA)} usos, todos de {AL[PH][0]}', n4 == f'{nf(N_BUSCA)} de {nf(N_SJ)} usos em Soja' and L4 and all(r[2] == AL[PH][0] for r in L4), [n4, L4[:2]])
    # ---------- 5 · a linha do uso abre a ficha com a cultura e o alvo escolhidos; Esc devolve o foco à mesma linha ----------
    rid = J("(()=>{const r=document.querySelector('main [role=table] [role=row].g2ed'); r.focus(); r.click(); return r.getAttribute('data-rid');})()"); time.sleep(1.0)
    sel = J(f"[...document.querySelectorAll('{FX} select')].slice(0,2).map(s=>s.value)") or []
    f5 = ficha()
    chk(f'5 linha do uso ({rid}) abre a ficha com Cultura = Soja e Alvo = {AL[PH][0]} já escolhidos (um toque a menos para "Usar na O.S.")',
        bool(rid) and sel == [str(SJ), str(PH)] and 'rotacao · soja ×' in nz(f5), [rid, sel, f5[:200]])
    # tabela "Usos registrados" da ficha: Praga-alvo | Nome científico | Tipo, ordenada pelo cabeçalho
    ucab = J(f"[...document.querySelectorAll('{FX} [role=table][aria-label^=\"Alvos em\"] [role=columnheader]')].map(h=>h.innerText.replace(/\\s+/g,' ').trim())") or []
    J(f"document.querySelector('{FX} [role=table][aria-label^=\"Alvos em\"] [role=columnheader] button').click()"); time.sleep(.4)
    us1 = J(f"[...document.querySelectorAll('{FX} [role=table][aria-label^=\"Alvos em\"] [role=row]')].slice(1).map(r=>r.querySelector('[role=cell]').innerText.trim())") or []
    so1 = J(f"document.querySelector('{FX} [role=table][aria-label^=\"Alvos em\"] [role=columnheader]').getAttribute('aria-sort')")
    J(f"document.querySelector('{FX} [role=table][aria-label^=\"Alvos em\"] [role=columnheader] button').click()"); time.sleep(.4)
    us2 = J(f"[...document.querySelectorAll('{FX} [role=table][aria-label^=\"Alvos em\"] [role=row]')].slice(1).map(r=>r.querySelector('[role=cell]').innerText.trim())") or []
    so2 = J(f"document.querySelector('{FX} [role=table][aria-label^=\"Alvos em\"] [role=columnheader]').getAttribute('aria-sort')")
    cheios = lambda a: [x for x in a if x not in ('—', 'não informado')]
    chk('5b ficha › Usos registrados: colunas Praga-alvo | Nome científico | Tipo; o cabeçalho ordena A → Z e Z → A (aria-sort)',
        [nz(x.replace('⇅', '').replace('▲', '').replace('▼', '')).strip() for x in ucab[:3]] == ['praga-alvo', 'nome cientifico', 'tipo'] and so1 == 'ascending' and so2 == 'descending'
        and len(cheios(us1)) > 1 and cheios(us2)[0] == cheios(us1)[-1] and sorted(cheios(us2)) == sorted(cheios(us1)), [ucab, so1, so2, us1[:4], us2[:4]])
    shot('ficha_usos')
    J("document.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true}))"); time.sleep(.6)
    foco = J("document.activeElement&&document.activeElement.getAttribute('data-rid')")
    chk('5c Esc fecha a ficha e o foco volta à linha do uso', foco == rid and not J(f"!!document.querySelector('{FX}')"), [foco, rid])
    junta('AG-07 1440')
    # ---------- 6 · RECUSA: busca sem resultado → aviso e "Limpar filtros" volta à lista inteira por produto ----------
    setv('main input[type=search]', 'zzzz praga inexistente'); vazio = J("(document.querySelector('main')||{}).innerText.indexOf('Nenhuma linha corresponde aos filtros')>=0")
    n6 = cnt(); clica('main', 'Limpar filtros'); time.sleep(.6); n6b = cnt(); a6 = cab()
    chk(f'6 RECUSA busca sem resultado em Soja: "0 de {nf(N_SJ)} usos em Soja" + "Nenhuma linha corresponde aos filtros"; "Limpar filtros" volta a {nf(NP)} produtos e 6 colunas',
        vazio is True and n6 == f'0 de {nf(N_SJ)} usos em Soja' and n6b == f'{nf(NP)} de {nf(NP)} produtos' and a6 == COLS_P and trilhas() == 7, [vazio, n6, n6b, a6])
    # ---------- 7 · REPETIÇÃO: Soja de novo e recarregar dão a mesma lista ----------
    combo('Cultura', 'soja'); n7 = cnt(); c.goto(U_('AG-07.dc.html'), wait=1.0); pronto(); combo('Cultura', 'soja'); n7b = cnt()
    combo('Cultura', 'mamão'); n7c = cnt(); NM = sum(len(ps) for c_ in (MA, TD) for a, ps in U[str(c_)])
    chk(f'7 REPETIÇÃO: Soja de novo e depois de recarregar = "{nf(N_SJ)} de {nf(N_SJ)} usos em Soja"; Mamão = {nf(NM)} usos', n7 == n7b == f'{nf(N_SJ)} de {nf(N_SJ)} usos em Soja' and n7c == f'{nf(NM)} de {nf(NM)} usos em Mamão', [n7, n7b, n7c])
    junta('AG-07 repetição')
    # ---------- 8 · RECUSA: usos que não carregam → a lista fica por produto, com aviso e "Tentar de novo" ----------
    c.goto(U_('AG-07.dc.html?falhaUsos=1'), wait=1.5); pronto(usos=False); time.sleep(1.0); combo('Cultura', 'soja')
    err = J("(()=>{const a=[...document.querySelectorAll('main [role=alert]')].map(x=>x.innerText).join(' '); return a;})()") or ''; a8 = cab(); n8 = cnt()
    J("window.__agFailU=false"); clica('main', 'Tentar de novo'); ok8 = pronto(); time.sleep(.8); a8b = cab(); n8b = cnt()
    chk('8 RECUSA usos indisponíveis: Soja fica por produto (6 colunas, "… de 4.409 produtos") com "Os usos registrados … não carregaram" + "Tentar de novo"; depois, por uso (8 colunas)',
        'não carregaram' in err and a8 == COLS_P and n8.endswith(f'de {nf(NP)} produtos') and ok8 and a8b == COLS_U and n8b == f'{nf(N_SJ)} de {nf(N_SJ)} usos em Soja', [err[:120], a8, n8, ok8, a8b, n8b])
    ERRS[:] = [e for e in ERRS if 'simulada' not in e]; junta('AG-07 falha usos')
    ERRS[:] = [e for e in ERRS if 'simulada' not in e]
    # ---------- 9 · 390 px: por uso, 8 colunas com a 1ª presa e rolagem só dentro da caixa; volta a 6 sem quebrar ----------
    c.size(390, 844); c.goto(U_('AG-07.dc.html'), wait=1.0); pronto(); combo('Cultura', 'soja'); time.sleep(.8)
    g9 = J("(()=>{const r=document.querySelector('main .g2rola'); const t=r.querySelector('[role=table]'); const h=t.querySelector('[role=columnheader]');"
           " return [document.scrollingElement.scrollWidth, innerWidth, r.scrollWidth>r.clientWidth, getComputedStyle(t).gridTemplateColumns.split(' ').length, getComputedStyle(h).position];})()") or []
    al9 = alinhado(); a9 = cab(); shot('soja_390')
    combo('Cultura', ''); time.sleep(.2)
    a9b = cab(); tr9b = trilhas(); al9b = alinhado()
    chk('9 390 px · Soja: 8 colunas (Praga-alvo e Nome científico), 1ª coluna presa, rolagem lateral só dentro da tabela, linhas sem quebrar; sem cultura volta a 7 trilhas (com Alvos)',
        len(g9) == 5 and g9[0] <= g9[1] and g9[2] is True and g9[3] == 8 and g9[4] == 'sticky' and al9 and a9 == COLS_U and a9b == COLS_P and tr9b == 7 and al9b, [g9, al9, a9, a9b, tr9b, al9b])
    combo('Cultura', 'soja'); setv('main input[type=search]', 'ferrugem asiatica')
    J("(()=>{const r=document.querySelector('main [role=table] [role=row].g2ed'); r.click();})()"); time.sleep(1.0)
    g9c = J(f"(()=>{{const a=document.querySelector('{FX}'); const t=a.querySelector('[role=table][aria-label^=\"Alvos em\"]'); return a&&t?[a.scrollWidth,a.clientWidth,Math.round(t.getBoundingClientRect().right),Math.round(a.getBoundingClientRect().right)]:null;}})()")
    shot('ficha_390')
    chk('9b 390 px · ficha com a tabela de usos sem rolagem lateral', bool(g9c) and g9c[0] <= g9c[1] and g9c[2] <= g9c[3], g9c)
    junta('AG-07 390')
    chk('10 nenhum erro de execução nas páginas', not ERRS, ERRS[:5])
finally:
    try:
        if c: c.close()
    finally: srv.terminate()
print(f'\nRESULTADO: {len(OK)}/{len(OK) + len(FAIL)} ok · {time.time() - t0:.0f} s', FAIL)
