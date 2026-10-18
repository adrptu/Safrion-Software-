# -*- coding: utf-8 -*-
"""Teste real (Chrome) — TABELAS-FOCO-20261004 v2 (5983172395), incremento 1: O.S. por talhão e uma variável por coluna.
TF01 vínculo por ID (P1, T1 ≠ T1-A/Trator T1, T1 ou T2 sem duplicar, Sem talhão, vazio continua vazio, troca de fazenda, mesmo nome em
fazendas distintas); TF02 recorte combinado conservado em Lista/Kanban/Recursos, detalhe→voltar e recarga, sem ação de negócio;
TF03 colunas tipadas (número, data com anos distintos, vazio); TF04 teclado e toque em 1440 e 390 px com capturas; TF06 agrupar por
talhão com contagem distinta e total sem somar grupos sobrepostos; TF07 Cultura na faixa.
13/10/2026 (proprietário): o botão "Talhão: Todos ▾" da barra da tabela (ost_btn, diálogo com busca e caixas) saiu. O Talhão é a lista
"Filtrar por talhão" da faixa "Filtros desta tela" (Todos, os talhões do recorte e, com mais de um marcado na coluna, "N talhões"), ligada ao
MESMO filtro da coluna Talhão da grade (f.tal), que segue no cabeçalho para escolher vários. Entrou "Filtrar por cultura" (a do cultivo de
cada talhão da ordem na safra dela). As verificações de talhão andam pela faixa e pelo filtro da coluna, e conferem um contra o outro.
14/10/2026 (VISOES-2, pedido do proprietário): Lista e Tabela agrupada viraram a Tabela; agrupar por talhão é o "Agrupar por" › Talhão da grade
(troca_visao(J, 'agrupada') faz Tabela + Talhão; desagrupar é "Sem agrupar"); o grupo leva o nome do talhão com "›" (o nome desce um nível) e a
nota do total diz "N O.S. · X ha · a O.S. de vários talhões aparece em cada um e conta uma vez no total". A célula O.S. pode trazer antes o texto
curto do estado vermelho ("Falta insumo"): a O.S. da linha é o código visível (OS-/OB-) da célula.
Uso: python3 tabelas_os_test.py [pasta de capturas]   (< 90 s)"""
import sys, os, re, time, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, servir, troca_visao, cv_todas_js, agrupar_por
OUT = sys.argv[1] if len(sys.argv) > 1 else None
if OUT: os.makedirs(OUT, exist_ok=True)
OK, FAIL = [], []
def chk(n, cond, info=''):
    (OK if cond else FAIL).append(n); print(('  ok  ' if cond else '  FALHOU ') + n + (' · ' + str(info)[:300] if info != '' else ''))

p, srv = servir(os.path.join(HERE, '_render')); c = Chrome(); J = c.js
URL = f'http://127.0.0.1:{p}/OS.dc.html'
# código visível da O.S. na 1ª célula (VISOES-2: o texto curto do estado vermelho, ex. "Falta insumo", pode vir antes do código)
def ids(): return J("[...document.querySelectorAll('[role=row].g2ed')].filter(r=>r.offsetParent).map(r=>{const t=r.querySelector('[role=cell]').innerText.trim(); const m=t.match(/\\bO[SB]-\\d+/); return m?m[0]:t;})") or []
TAL, CUL = 'Filtrar por talhão', 'Filtrar por cultura'
def _s(lab): return f"document.querySelector('select[aria-label={json.dumps(lab)}]')"
def esc_txt(lab=TAL):   # texto da opção escolhida na faixa (Todos, T1, "2 talhões"…); None sem a lista
    return J(f"(()=>{{const s={_s(lab)}; return s&&s.selectedIndex>=0?s.options[s.selectedIndex].text.trim():null;}})()")
def tal(): return esc_txt(TAL)
def opcoes(lab=TAL): return J(f"(()=>{{const s={_s(lab)}; return s?[...s.options].map(o=>o.text.trim()):[];}})()") or []
def escolhe(nome, lab=TAL):   # escolhe na faixa pelo texto da opção (o que a pessoa lê); False se a opção não existe
    r = J(f"""(()=>{{const s={_s(lab)}; const o=s&&[...s.options].find(o=>o.text.trim()==={json.dumps(nome)}); if(!o) return false;
      Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype,'value').set.call(s,o.value);
      s.dispatchEvent(new Event('input',{{bubbles:true}})); s.dispatchEvent(new Event('change',{{bubbles:true}})); return true;}})()"""); time.sleep(.6); return r
def todos(): escolhe('Todos')
# filtro da coluna Talhão no cabeçalho da grade (menu de valores com contagem: Limpar, marcar, OK/Cancelar); o "Sem talhão" da faixa é "(vazio)" aqui
DLG = '[role=dialog][aria-label="Filtrar Talhão"]'
def _dlg_bt(t): J(f"(()=>{{const b=[...document.querySelectorAll({json.dumps(DLG + ' button')})].find(b=>b.innerText.trim()==={json.dumps(t)}); b&&b.click();}})()"); time.sleep(.3)
def col_abre():
    J("(()=>{const b=[...document.querySelectorAll('button[aria-label=\"Filtrar Talhão\"]')].find(b=>b.offsetParent); b&&b.click();})()"); time.sleep(.4)
    return bool(J(f"!!document.querySelector({json.dumps(DLG)})"))
def col_valores():   # valores do filtro da coluna com a contagem ("T1 1"); fecha com Cancelar
    if not col_abre(): return []
    r = J(f"[...document.querySelectorAll({json.dumps(DLG + ' label')})].map(l=>l.innerText.replace(/\\s+/g,' ').trim())") or []; _dlg_bt('Cancelar'); return r
def col_marcados():   # valores marcados no filtro da coluna Talhão; None = todos marcados (sem filtro); fecha com Cancelar
    if not col_abre(): return 'sem o filtro da coluna'
    m = J(f"[...document.querySelectorAll({json.dumps(DLG + ' label')})].map(l=>[l.innerText.replace(/\\s+\\d+$/,'').trim(),l.querySelector('input').checked])") or []
    _dlg_bt('Cancelar'); v = [n for n, on in m if on]; return None if m and len(v) == len(m) else v
def col_tal(nomes):   # filtra pela coluna: Limpar, marca cada nome exato (o número ao lado é a contagem), OK
    if not col_abre(): return False
    _dlg_bt('Limpar'); achou = True
    for n in nomes:
        achou = J(f"(()=>{{const l=[...document.querySelectorAll({json.dumps(DLG + ' label')})].find(l=>l.innerText.replace(/\\s+\\d+$/,'').trim()==={json.dumps(n)}); if(!l) return false; l.querySelector('input').click(); return true;}})()") and achou; time.sleep(.15)
    _dlg_bt('OK'); time.sleep(.3); return achou
def aba(t): troca_visao(J, {'Lista': 'lista', 'Kanban': 'kanban', 'Recursos': 'carga', 'Agrupada': 'agrupada'}[t])   # VISOES-1: pelo seletor (data-visao)
def fase(t): J(f"(()=>{{const b=[...document.querySelectorAll('[aria-label=\"Filtrar por fase\"] button')].find(b=>b.innerText.trim().startsWith({json.dumps(t)})); b&&b.click();}})()"); time.sleep(.4)
def busca(q):
    J(f"""(()=>{{const i=document.querySelector('input[aria-label="Buscar nesta tabela"]'); Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(i,{json.dumps(q)});
      i.dispatchEvent(new Event('input',{{bubbles:true}})); i.dispatchEvent(new Event('change',{{bubbles:true}}));}})()"""); time.sleep(.5)
def sel(lab, val):
    J(f"""(()=>{{const i=document.querySelector('select[aria-label={json.dumps(lab)}]'); Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype,'value').set.call(i,{json.dumps(val)});
      i.dispatchEvent(new Event('input',{{bubbles:true}})); i.dispatchEvent(new Event('change',{{bubbles:true}}));}})()"""); time.sleep(.6)
def notas(): return J("[...document.querySelectorAll('[role=note],[role=status]')].filter(n=>n.offsetParent).map(n=>n.innerText.replace(/\\s+/g,' ').trim()).filter(Boolean)") or []
def recursos(): return sorted(set(J("[...document.querySelectorAll('[aria-label=\"Alocação de recursos na semana\"] button')].filter(b=>b.offsetParent).map(b=>b.innerText.split(' ')[0]).filter(x=>/^O[SB]-/.test(x))") or []))
def kanban(): return J("[...document.querySelectorAll('[role=button][aria-label^=\"Abrir O\"]')].filter(b=>b.offsetParent).map(b=>b.getAttribute('aria-label').split(' ')[1])") or []
def cel_col(col): return J(f"""(()=>{{const hs=[...document.querySelectorAll('[role=columnheader]')].filter(h=>h.offsetParent).map(h=>h.innerText.replace(/[⇅▾▴▲▼]/g,'').replace(/\\s+/g,' ').trim().toUpperCase());
   const i=hs.indexOf({json.dumps(col.upper())}); return [...document.querySelectorAll('[role=row].g2ed')].filter(r=>r.offsetParent).map(r=>[...r.querySelectorAll('[role=cell]')][i].innerText.trim());}})()""") or []
def ordena(col):
    J(f"""(()=>{{const h=[...document.querySelectorAll('[role=columnheader]')].filter(h=>h.offsetParent).find(h=>h.innerText.replace(/[⇅▾▴▲▼]/g,'').trim().toUpperCase()==={json.dumps(col.upper())});
      const b=[...h.querySelectorAll('button')].find(b=>/Ordenar|⇅/.test((b.getAttribute('aria-label')||'')+b.innerText))||h.querySelector('button'); b.click();}})()"""); time.sleep(.4)
def negocio(): return J("JSON.stringify(Object.keys(localStorage).filter(k=>k.indexOf('safrion.pref.')!==0).sort().map(k=>[k,localStorage.getItem(k)]))")   # a preferência de visão (safrion.pref.) não é negócio (VISOES-1)
def shot(n):
    if OUT: c.shot(os.path.join(OUT, n + '.png'))

try:
    c.aparelho(1440, 900, 1, False)
    c.goto(URL.replace('OS.dc.html', 'Main.dc.html'), .3); J("localStorage.clear(); sessionStorage.clear()")
    c.goto(URL, 1.2); J(cv_todas_js('g_os'))   # VISOES-2 §3.6: este teste confere todas as colunas da O.S. (a pessoa escolhe "todas")
    c.goto(URL, 1.2); J("window.__e=[];addEventListener('error',e=>window.__e.push(String(e.message)))")
    todas = ids(); neg0 = negocio(); shot('tf04-1440-antes')
    print('linhas', todas)
    # ---------------- TF01 ----------------
    op = opcoes(); cv = col_valores(); print('opções', op, cv)
    vis_t = J(f"(()=>{{const s={_s(TAL)}; return !!s&&!!s.offsetParent&&!!s.closest('[aria-label=\"Filtros\"]');}})()")
    chk('TF01 faixa "Filtros": Talhão visível em Todos, com Sem talhão e os mesmos talhões do filtro da coluna (que mostra a contagem por valor)',
        vis_t and tal() == 'Todos' and op[:1] == ['Todos'] and 'Sem talhão' in op and bool(cv) and all(x.split()[-1].isdigit() for x in cv)
        and sorted('(vazio)' if o == 'Sem talhão' else o for o in op[1:]) == sorted(x.rsplit(' ', 1)[0] for x in cv), (vis_t, tal(), op, cv))
    escolhe('P1'); chk('TF01 P1 devolve os vínculos P1 (OS-0417, OS-0418 e a OS-0597 da demonstração das Frentes)', sorted(ids()) == ['OS-0417', 'OS-0418', 'OS-0597'], ids()); todos()   # v135: semente EX-54 na Santa Rita
    escolhe('T1'); r = ids(); cm = col_marcados()
    chk('TF01 T1 na faixa filtra na hora e não seleciona T1-A (OS-0430) nem "Trator T1" (OS-0431): só OS-0421; o filtro da coluna Talhão fica com T1',
        r == ['OS-0421'] and tal() == 'T1' and cm == ['T1'], (r, tal(), cm))
    col_tal(['T1', 'T2']); r = ids()
    chk('TF01 T1 ou T2 pelo filtro da coluna: OS-0421 (T1+T2) aparece uma vez, com OS-0431 e a OS-0599 (KCl em T2, demonstração das Frentes); a faixa mostra "2 talhões"',
        sorted(r) == ['OS-0421', 'OS-0431', 'OS-0599'] and r.count('OS-0421') == 1 and tal() == '2 talhões', (r, tal()))
    escolhe('Sem talhão'); cm = col_marcados()
    chk('TF01 Sem talhão: OB-0104 com Local Armazém Sede; na coluna, "(vazio)"', ids() == ['OB-0104'] and cel_col('Local') == ['Armazém Sede'] and cm == ['(vazio)'], (ids(), cel_col('Local'), cm))
    todos(); cm = col_marcados()
    chk('TF01 Todos volta às linhas do contexto e limpa o filtro da coluna Talhão', ids() == todas and tal() == 'Todos' and cm is None, (len(ids()), tal(), cm))
    # vazio continua vazio (T1 + fase em que a OS-0421 não está)
    escolhe('T1'); fase('Encerradas'); r = ids()
    chk('TF01 T1 + Encerradas: vazio continua vazio (sem cair para todas as linhas)', r == [], r)
    fase('Todas'); todos()
    # ---------------- TF07 Cultura (13/10): a do cultivo de cada talhão da ordem na safra dela ----------------
    rec = (esc_txt('Filtrar por fazenda'), esc_txt('Filtrar por safra')); co = opcoes(CUL)
    escolhe('Café', CUL); r = ids(); ot = opcoes(); lt = cel_col('Talhão')
    chk('TF07 Cultura "Café" no recorte padrão (Santa Rita, Todas as safras): só OS-0425, na hora; o Talhão oferece só os talhões do recorte',
        rec == ('Santa Rita', 'Todas') and co[:1] == ['Todas'] and 'Café' in co and esc_txt(CUL) == 'Café' and r == ['OS-0425'] and ot == ['Todos'] + lt, (rec, co, r, ot, lt))
    escolhe('Todas', CUL)
    chk('TF07 Cultura "Todas" volta às linhas do contexto', ids() == todas and esc_txt(CUL) == 'Todas', len(ids()))
    # mesmo nome de talhão em fazendas diferentes: o vínculo é por ID com a fazenda (componente G2, linhas sintéticas)
    import subprocess
    u = json.loads(subprocess.run(['node', '-e', """const vm=require('vm'),fs=require('fs'); const ctx={}; vm.createContext(ctx);
      vm.runInContext(fs.readFileSync(process.argv[1],'utf8')+';this.g2match=g2match;',ctx); const sp={cols:[{k:'tal',multi:true}]};
      const rs=[{id:'A',m:{tal:[{id:'Santa Rita|T1',l:'T1'}]},v:{}},{id:'B',m:{tal:[{id:'Lagoa|T1',l:'T1'}]},v:{}},{id:'C',m:{tal:[]},v:{}}];
      console.log(JSON.stringify([rs.filter(r=>ctx.g2match(r,sp,{f:{tal:['Santa Rita|T1']}})).map(r=>r.id), rs.filter(r=>ctx.g2match(r,sp,{f:{tal:['(vazio)']}})).map(r=>r.id)]));""",
      os.path.join(HERE, 'g2lib.js')], capture_output=True, text=True).stdout or 'null')
    chk('TF01 mesmo nome "T1" em duas fazendas não se mistura; vazio por (vazio)', u == [['A'], ['C']], u)
    # troca de contexto: Fazenda = Todas mostra a fazenda no rótulo; escolher um pivô e voltar a Santa Rita remove o valor e avisa
    fz = J("[...document.querySelector('select[aria-label=\"Filtrar por fazenda\"]').options].map(o=>o.value)") or []
    sel('Filtrar por fazenda', 'Todas'); op = opcoes()
    pv = next((o for o in op if o.startswith('Pivô')), '')
    chk('TF01 Fazenda = Todas: rótulos com a fazenda', bool(pv) and ' · ' in pv and 'T1 · Santa Rita' in op, op[:6])
    escolhe(pv); n_pv = ids()
    sel('Filtrar por fazenda', 'Santa Rita'); m = notas(); cm = col_marcados()
    chk('TF01 troca para Santa Rita: talhão fora do escopo sai do filtro e a tela avisa (sem trocar a fazenda sozinha)',
        bool(n_pv) and tal() == 'Todos' and cm is None and any('saiu do filtro' in x for x in m) and J("document.querySelector('select[aria-label=\"Filtrar por fazenda\"]').value") == 'Santa Rita' and ids() == todas, (fz, pv, n_pv, tal(), cm, m))
    # ---------------- TF02 ----------------
    col_tal(['T1', 'T2']); busca('Plantio'); r = ids()
    chk('TF02 Talhão (T1 ou T2) E busca "Plantio": OS-0431 e a OS-0599 ("KCl a lanço antes do plantio", demonstração)', sorted(r) == ['OS-0431', 'OS-0599'], r)
    busca(''); fase('Em execução'); r1 = ids()
    aba('Kanban'); k = kanban(); kn = notas()
    chk('TF02 Kanban com o mesmo recorte (talhão + fase) e nota do recorte', sorted(k) == sorted(r1) and any('talhão' in x.lower() for x in kn), (r1, k, kn))
    aba('Recursos'); rc = recursos(); rn = notas()
    chk('TF02 Recursos só com blocos das O.S. do recorte de talhão', set(rc) <= {'OS-0421', 'OS-0431'} and len(rc) >= 1 and any('talh' in x.lower() for x in rn), (rc, rn))
    aba('Lista')
    J("[...document.querySelectorAll('[role=row].g2ed')].filter(r=>r.offsetParent)[0].click()"); time.sleep(.5)
    det = J("!!document.querySelector('aside[role=dialog]')")
    J("(()=>{const b=document.querySelector('aside[role=dialog] button[aria-label=Fechar]'); b&&b.click();})()"); time.sleep(.4)
    cm = col_marcados()
    chk('TF02 abrir e fechar o detalhe conserva o recorte', det and ids() == r1 and tal() == '2 talhões' and cm == ['T1', 'T2'], (det, ids(), tal(), cm))
    c.goto(URL, 1.2); cm = col_marcados()
    chk('TF02 recarregar a página (volta do detalhe completo) conserva talhão e fase', ids() == r1 and tal() == '2 talhões' and cm == ['T1', 'T2'], (ids(), tal(), cm))
    todos(); r2 = ids()
    chk('TF02 limpar Talhão mantém o filtro de fase', len(r2) > len(r1) and set(r1) <= set(r2) and J("[...document.querySelectorAll('[aria-label=\"Filtrar por fase\"] button')].some(b=>b.getAttribute('aria-pressed')==='true'&&b.innerText.startsWith('Em execução'))"), (r1, r2))
    fase('Todas')
    chk('TF02 filtrar não executou ação de negócio (cenário salvo inalterado)', negocio() == neg0)
    # ---------------- TF03 ----------------
    ordena('Área'); a = [x for x in cel_col('Área') if x not in ('—', '')]
    num = [float(x.split(' ')[0].replace('.', '').replace(',', '.')) for x in a if re.match(r'^[\d.]+,\d{2} ha$', x)]
    chk('TF03 Área ordena por número (38 antes de 100), com a unidade na célula ("160,00 ha", decisão de 05/10/2026)', len(num) == len(a) > 1 and (num == sorted(num) or num == sorted(num, reverse=True)), a)
    ordena('Início'); d = [x for x in cel_col('Início') if x not in ('—', '')]
    iso = [x[6:] + x[3:5] + x[:2] for x in d]
    chk('TF03 Início ordena por data, anos distintos (2025 antes de 2026)', (iso == sorted(iso) or iso == sorted(iso, reverse=True)) and any(x.endswith('2025') for x in d) and any(x.endswith('2026') for x in d), d)
    chk('TF03 Realizado, Saldo e Progresso em colunas próprias', all(cel_col(k) for k in ('Realizado', 'Saldo', 'Progresso', 'Quem resolve', 'Próxima ação', 'Prazo')))
    un = [(k, x) for k, u in (('Realizado', 'ha'), ('Saldo', 'ha'), ('Dispensado', 'ha'), ('Progresso', '%')) for x in cel_col(k) if x not in ('—', '') and not re.match(r'^[\d.]+(,\d+)? ' + u + '$', x)]
    hs_os = J("[...document.querySelectorAll('[role=columnheader]')].filter(h=>h.offsetParent).map(h=>h.innerText.replace(/[⇅▾▴▲▼]/g,'').replace(/\\s+/g,' ').trim())") or []
    chk('TF03 unidade fixa na célula ("60,00 ha", "37,5 %"), cabeçalho sem "(ha)"; sem a coluna Lâmina, que ficava sempre vazia', not un and hs_os and not any('(' in h for h in hs_os) and 'Lâmina' not in hs_os, (un[:3], hs_os))
    pr = dict(zip(ids(), cel_col('Prazo'))); ac = dict(zip(ids(), cel_col('Próxima ação')))
    chk('TF03 Próxima ação separada do prazo ("entrega" | "até 15/10")', ac.get('OS-0425') == 'entrega' and pr.get('OS-0425') == 'até 15/10', (ac.get('OS-0425'), pr.get('OS-0425')))
    # ---------------- TF06 ----------------
    aba('Agrupada'); time.sleep(.2)   # VISOES-2: agrupar por talhão é a Tabela + "Agrupar por" › Talhão
    # TAB-12 (17/10/2026): os grupos nascem recolhidos (antes, abertos); a pessoa usa "Expandir tudo" para ver as O.S. de cada talhão
    J("[...document.querySelectorAll('button.g2xtog')].filter(b=>b.offsetParent&&/Expandir tudo/.test(b.innerText)).forEach(b=>b.click())"); time.sleep(.4)
    # grupo = linha grp@ (nome sem a seta e sem o "›" de descer); O.S. = código visível da linha filha
    GRP = """(()=>{ const out={}; let cur=null; [...document.querySelectorAll('[role=row].g2r')].filter(r=>r.offsetParent).forEach(r=>{ const t=r.querySelector('[role=cell]').innerText.replace(/[▾▸]/g,'').replace(/\\s*›\\s*$/,'').trim();
      if(/^grp@/.test(r.getAttribute('data-rid')||'')){ cur=t; out[cur]=[]; } else { const m=t.match(/\\bO[SB]-\\d+/); (out[cur]=out[cur]||[]).push(m?m[0]:t); } }); return out; })()"""
    g = J(GRP) or {}
    TOT = re.compile(r'^\d+ O\.S\. · ')   # nota do total do agrupamento por Talhão
    tot = next((x for x in notas() if TOT.match(x)), '')
    soma = sum(len(v) for v in g.values()); dist = len({x for v in g.values() for x in v})
    chk('TF06 OS-0421 aparece nos grupos T1 e T2 com a mesma identidade', 'OS-0421' in g.get('T1', []) and 'OS-0421' in g.get('T2', []), g)
    chk('TF06 total geral conta O.S. distintas (10), não a soma dos grupos (11): "10 O.S. · … · a O.S. de vários talhões aparece em cada um e conta uma vez no total"',
        soma == dist + 1 and tot.startswith(f'{dist} O.S. · ') and tot.endswith('a O.S. de vários talhões aparece em cada um e conta uma vez no total'), (soma, dist, tot))
    cont = J("(()=>{const s=[...document.querySelectorAll('span')].find(s=>s.offsetParent&&/^\\d+ de \\d+$/.test(s.innerText.trim())); return s?s.innerText.trim():'';})()")
    chk('TF06 contador da grade no agrupado conta O.S. distintas (10 de 10), não grupos (9)', cont == f'{dist} de {len(todas)}', cont)
    shot('tf06-1440-agrupado')
    col_tal(['T1', 'T2']); g2 = J(GRP) or {}; tot = next((x for x in notas() if TOT.match(x)), '')
    chk('TF06 com T1 ou T2: só grupos T1 e T2; total 3 O.S. · 750 ha (350 + 102 + 298 da OS-0599, cada O.S. uma vez)', list(g2) == ['T1', 'T2'] and tot.startswith('3 O.S. · 750 ha · '), (g2, tot))
    J("[...document.querySelectorAll('[role=row].g2r')].filter(r=>r.offsetParent).find(r=>/^OS-0421/.test(r.innerText.trim())).querySelector('[role=cell]').click()"); time.sleep(.5)
    chk('TF06 clicar na O.S. dentro do grupo abre o detalhe da própria O.S.', (J("(document.querySelector('aside[role=dialog]')||{}).innerText||''") or '').startswith('OS-0421'))
    J("(()=>{const b=document.querySelector('aside[role=dialog] button[aria-label=Fechar]'); b&&b.click();})()"); time.sleep(.3)
    aba('Lista'); agrupar_por(J, 'Sem agrupar'); todos()   # VISOES-2: desagrupar = "Agrupar por" › Sem agrupar (a Tabela guarda o agrupamento)
    chk('TF06 desagrupar volta às linhas canônicas', sorted(ids()) == sorted(todas), len(ids()))
    chk('sem botão Expandir/Recolher na lista sem grupos', not J("[...document.querySelectorAll('.g2xtog')].some(b=>b.offsetParent)"))
    chk('sem erro de script (1440)', not J("window.__e"), J("window.__e"))
    # ---------------- TF04: 390 px, toque e teclado na lista "Filtrar por talhão" da faixa ----------------
    c.aparelho(390, 844, 2, True); c.goto(URL, 1.2); J("window.__e=[];addEventListener('error',e=>window.__e.push(String(e.message)))")
    shot('tf04-390-antes')
    foco = lambda: J("document.activeElement&&document.activeElement.getAttribute('aria-label')")
    b = J(f"(()=>{{const r={_s(TAL)}.getBoundingClientRect(); const m=document.querySelector('main'); return [r.left,r.right,r.top,r.height,innerWidth,innerHeight,document.documentElement.scrollWidth,m?m.getBoundingClientRect().left:0];}})()")
    chk('TF04 390 px: Talhão da faixa à vista sem rolar, entre o menu e a borda, alvo ≥ 32 px de altura e página sem rolagem horizontal',
        b[0] >= b[7] and b[1] <= b[4] and b[2] >= 0 and b[2] + b[3] <= b[5] and b[3] >= 32 and b[6] <= b[4] + 1, b)
    # toque abre a lista nativa com o foco nela; digitar "T1" e Enter escolhe (o teclado do celular faz o mesmo); a lista filtra na hora
    c.toque(b[0] + 20, b[2] + b[3] / 2); time.sleep(.3); f0 = foco()
    for ch in 'T1': c.tecla(ch, 'Key' + ch if ch.isalpha() else 'Digit' + ch, ord(ch), text=ch)
    c.tecla('Enter', 'Enter', 13, text='\r'); time.sleep(.6); r = ids(); f1 = foco()
    chk('TF04 toque: a lista do Talhão recebe o foco; escolher T1 filtra na hora (só OS-0421) e o foco fica na lista', f0 == TAL and r == ['OS-0421'] and tal() == 'T1' and f1 == TAL, (f0, r, tal(), f1))
    shot('tf04-390-depois')
    c.tecla('ArrowDown', 'ArrowDown', 40); time.sleep(.6); r1, t1 = ids(), tal()
    c.tecla('ArrowUp', 'ArrowUp', 38); time.sleep(.6); r2, t2 = ids(), tal()
    chk('TF04 teclado: com o foco na lista, ↓ escolhe T1-A (só OS-0430) e ↑ volta a T1 (só OS-0421), filtrando na hora', (t1, r1, t2, r2) == ('T1-A', ['OS-0430'], 'T1', ['OS-0421']) and foco() == TAL, (t1, r1, t2, r2, foco()))
    cm = col_marcados()
    chk('TF04 390 px: o filtro da coluna Talhão fica com o T1 escolhido na faixa', cm == ['T1'], cm)
    col_tal(['T1', 'T2']); r = ids()
    chk('TF04 390 px: dois talhões pelo filtro da coluna (T1 ou T2) mostram "2 talhões" na faixa', sorted(r) == ['OS-0421', 'OS-0431', 'OS-0599'] and tal() == '2 talhões', (r, tal()))
    J("[...document.querySelectorAll('[role=row].g2ed')].filter(r=>r.offsetParent)[0].focus()"); c.tecla('Enter', 'Enter', 13, text='\r'); time.sleep(.5)
    det = J("!!document.querySelector('aside[role=dialog]')"); shot('tf04-390-detalhe')
    J("(()=>{const b=document.querySelector('aside[role=dialog] button[aria-label=Fechar]'); b&&b.click();})()"); time.sleep(.4)
    chk('TF04 Enter na linha abre o detalhe; fechar volta com o recorte', det and sorted(ids()) == ['OS-0421', 'OS-0431', 'OS-0599'] and tal() == '2 talhões', (det, ids(), tal()))
    todos(); cm = col_marcados()
    chk('TF04 390 px: "Todos" na faixa limpa o Talhão (linhas do contexto, na ordem gravada no TF03, e filtro da coluna sem marca)', sorted(ids()) == sorted(todas) and tal() == 'Todos' and cm is None, (len(ids()), tal(), cm))
    chk('sem erro de script (390)', not J("window.__e"), J("window.__e"))
finally:
    c.close(); srv.terminate()
print(f'RESULTADO: {len(OK)}/{len(OK) + len(FAIL)} ok' + (' · FALHAS: ' + '; '.join(FAIL) if FAIL else ''))
sys.exit(1 if FAIL else 0)
