# -*- coding: utf-8 -*-
"""Teste real (Chrome) — TABELAS-FOCO-20261004 v2 (5983172395), incremento 1: O.S. por talhão e uma variável por coluna.
TF01 vínculo por ID (P1, T1 ≠ T1-A/Trator T1, T1 ou T2 sem duplicar, Sem talhão, vazio continua vazio, troca de fazenda, mesmo nome em
fazendas distintas); TF02 recorte combinado conservado em Lista/Kanban/Recursos, detalhe→voltar e recarga, sem ação de negócio;
TF03 colunas tipadas (número, data com anos distintos, vazio); TF04 teclado e toque em 1440 e 390 px com capturas; TF06 agrupar por
talhão com contagem distinta e total sem somar grupos sobrepostos.
Uso: python3 tabelas_os_test.py [pasta de capturas]   (< 90 s)"""
import sys, os, time, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, servir
OUT = sys.argv[1] if len(sys.argv) > 1 else None
if OUT: os.makedirs(OUT, exist_ok=True)
OK, FAIL = [], []
def chk(n, cond, info=''):
    (OK if cond else FAIL).append(n); print(('  ok  ' if cond else '  FALHOU ') + n + (' · ' + str(info)[:300] if info != '' else ''))

p, srv = servir(os.path.join(HERE, '_render')); c = Chrome(); J = c.js
URL = f'http://127.0.0.1:{p}/OS.dc.html'
def ids(): return J("[...document.querySelectorAll('[role=row].g2ed')].filter(r=>r.offsetParent).map(r=>r.querySelector('[role=cell]').innerText.trim())") or []
def btn_tal(): return J("document.getElementById('ost_btn').innerText.replace(/\\s+/g,' ').trim()") or ''
def abre_tal():
    if not J("!!document.querySelector('[aria-label=\"Filtrar por talhão\"]')"): J("document.getElementById('ost_btn').click()"); time.sleep(.35)
def opcoes(): abre_tal(); return J("[...document.querySelectorAll('[aria-label=\"Filtrar por talhão\"] label')].map(l=>l.innerText.replace(/\\s+/g,' ').trim())") or []
def marca(nome):   # marca/desmarca uma opção pelo nome exato (o número ao lado é a contagem)
    abre_tal(); r = J(f"(()=>{{const l=[...document.querySelectorAll('[aria-label=\"Filtrar por talhão\"] label')].find(l=>l.innerText.replace(/\\s+\\d+$/,'').trim()==={json.dumps(nome)}); if(!l) return false; l.querySelector('input').click(); return true;}})()"); time.sleep(.4); return r
def fecha_tal(): J("(()=>{const d=document.querySelector('[aria-label=\"Filtrar por talhão\"]'); if(d) [...d.querySelectorAll('button')].find(b=>b.innerText.trim()==='Fechar').click();})()"); time.sleep(.3)
def todos(): J("[...document.querySelectorAll('button')].find(b=>b.innerText.trim()==='Todos os talhões').click()"); time.sleep(.4)
def aba(t): J(f"[...document.querySelectorAll('button,[role=tab]')].find(b=>b.innerText.trim()==={json.dumps(t)}).click()"); time.sleep(.4)
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
def negocio(): return J("JSON.stringify(Object.keys(localStorage).sort().map(k=>[k,localStorage.getItem(k)]))")
def shot(n):
    if OUT: c.shot(os.path.join(OUT, n + '.png'))

try:
    c.aparelho(1440, 900, 1, False)
    c.goto(URL.replace('OS.dc.html', 'Main.dc.html'), .3); J("localStorage.clear(); sessionStorage.clear()")
    c.goto(URL, 1.2); J("window.__e=[];addEventListener('error',e=>window.__e.push(String(e.message)))")
    todas = ids(); neg0 = negocio(); shot('tf04-1440-antes')
    print('linhas', todas)
    # ---------------- TF01 ----------------
    op = opcoes(); print('opções', op)
    chk('TF01 seletor Talhão visível com Todos, contagem por opção e Sem talhão', btn_tal().startswith('Talhão: Todos') and any(o.startswith('Sem talhão') for o in op) and all(o.split()[-1].isdigit() for o in op), (btn_tal(), op))
    marca('P1'); chk('TF01 P1 devolve os vínculos P1 (OS-0417, OS-0418)', sorted(ids()) == ['OS-0417', 'OS-0418'], ids()); marca('P1')
    marca('T1'); r = ids()
    chk('TF01 T1 não seleciona T1-A (OS-0430) nem "Trator T1" (OS-0431): só OS-0421', r == ['OS-0421'] and btn_tal() == 'Talhão: T1 ▾', (r, btn_tal()))
    marca('T2'); r = ids()
    chk('TF01 T1 ou T2: OS-0421 (T1+T2) aparece uma vez, com OS-0431', sorted(r) == ['OS-0421', 'OS-0431'] and r.count('OS-0421') == 1, r)
    todos(); marca('Sem talhão')
    chk('TF01 Sem talhão: OB-0104 com Local Armazém Sede', ids() == ['OB-0104'] and cel_col('Local') == ['Armazém Sede'], (ids(), cel_col('Local')))
    todos(); fecha_tal()
    chk('TF01 Todos os talhões volta às linhas do contexto', ids() == todas, len(ids()))
    # vazio continua vazio (T1 + fase em que a OS-0421 não está)
    marca('T1'); fecha_tal(); fase('Encerradas'); r = ids()
    chk('TF01 T1 + Encerradas: vazio continua vazio (sem cair para todas as linhas)', r == [], r)
    fase('Todas'); todos()
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
    pv = next((o.rsplit(' ', 1)[0] for o in op if o.startswith('Pivô')), '')
    chk('TF01 Fazenda = Todas: rótulos com a fazenda', bool(pv) and ' · ' in pv and any(o.startswith('T1 · Santa Rita') for o in op), op[:6])
    marca(pv); fecha_tal(); n_pv = ids()
    sel('Filtrar por fazenda', 'Santa Rita'); m = notas()
    chk('TF01 troca para Santa Rita: talhão fora do escopo sai do filtro e a tela avisa (sem trocar a fazenda sozinha)',
        btn_tal() == 'Talhão: Todos ▾' and any('saiu do filtro' in x for x in m) and J("document.querySelector('select[aria-label=\"Filtrar por fazenda\"]').value") == 'Santa Rita' and ids() == todas, (fz, pv, n_pv, btn_tal(), m))
    # ---------------- TF02 ----------------
    marca('T1'); marca('T2'); fecha_tal(); busca('Plantio'); r = ids()
    chk('TF02 Talhão (T1 ou T2) E busca "Plantio": só OS-0431', r == ['OS-0431'], r)
    busca(''); fase('Em execução'); r1 = ids()
    aba('Kanban'); k = kanban(); kn = notas()
    chk('TF02 Kanban com o mesmo recorte (talhão + fase) e nota do recorte', sorted(k) == sorted(r1) and any('talhão' in x.lower() for x in kn), (r1, k, kn))
    aba('Recursos'); rc = recursos(); rn = notas()
    chk('TF02 Recursos só com blocos das O.S. do recorte de talhão', set(rc) <= {'OS-0421', 'OS-0431'} and len(rc) >= 1 and any('talh' in x.lower() for x in rn), (rc, rn))
    aba('Lista')
    J("[...document.querySelectorAll('[role=row].g2ed')].filter(r=>r.offsetParent)[0].click()"); time.sleep(.5)
    det = J("!!document.querySelector('aside[role=dialog]')")
    J("(()=>{const b=document.querySelector('aside[role=dialog] button[aria-label=Fechar]'); b&&b.click();})()"); time.sleep(.4)
    chk('TF02 abrir e fechar o detalhe conserva o recorte', det and ids() == r1 and btn_tal() == 'Talhão: T1, T2 ▾', (det, ids(), btn_tal()))
    c.goto(URL, 1.2)
    chk('TF02 recarregar a página (volta do detalhe completo) conserva talhão e fase', ids() == r1 and btn_tal() == 'Talhão: T1, T2 ▾', (ids(), btn_tal()))
    todos(); r2 = ids()
    chk('TF02 limpar Talhão mantém o filtro de fase', len(r2) > len(r1) and set(r1) <= set(r2) and J("[...document.querySelectorAll('[aria-label=\"Filtrar por fase\"] button')].some(b=>b.getAttribute('aria-pressed')==='true'&&b.innerText.startsWith('Em execução'))"), (r1, r2))
    fase('Todas')
    chk('TF02 filtrar não executou ação de negócio (cenário salvo inalterado)', negocio() == neg0)
    # ---------------- TF03 ----------------
    ordena('Área (ha)'); a = [x for x in cel_col('Área (ha)') if x not in ('—', '')]
    num = [float(x.replace('.', '').replace(',', '.')) for x in a]
    chk('TF03 Área (ha) ordena por número (38 antes de 100)', num == sorted(num) or num == sorted(num, reverse=True), a)
    ordena('Início'); d = [x for x in cel_col('Início') if x not in ('—', '')]
    iso = [x[6:] + x[3:5] + x[:2] for x in d]
    chk('TF03 Início ordena por data, anos distintos (2025 antes de 2026)', (iso == sorted(iso) or iso == sorted(iso, reverse=True)) and any(x.endswith('2025') for x in d) and any(x.endswith('2026') for x in d), d)
    chk('TF03 Realizado, Saldo e Progresso em colunas próprias, com unidade no cabeçalho', all(cel_col(k) for k in ('Realizado (ha)', 'Saldo (ha)', 'Progresso (%)', 'Quem resolve', 'Próxima ação', 'Prazo')))
    pr = dict(zip(ids(), cel_col('Prazo'))); ac = dict(zip(ids(), cel_col('Próxima ação')))
    chk('TF03 Próxima ação separada do prazo ("entrega" | "até 15/10")', ac.get('OS-0425') == 'entrega' and pr.get('OS-0425') == 'até 15/10', (ac.get('OS-0425'), pr.get('OS-0425')))
    # ---------------- TF06 ----------------
    J("[...document.querySelectorAll('button')].find(b=>b.innerText.trim()==='Agrupar por talhão').click()"); time.sleep(.6)
    g = J("""(()=>{ const out={}; let cur=null; [...document.querySelectorAll('[role=row].g2r')].filter(r=>r.offsetParent).forEach(r=>{ const t=r.querySelector('[role=cell]').innerText.replace('▾','').replace('▸','').trim();
      if(/^O[SB]-/.test(t)) out[cur].push(t); else { cur=t; out[cur]=[]; } }); return out; })()""") or {}
    tot = next((x for x in notas() if x.startswith('Total')), '')
    soma = sum(len(v) for v in g.values()); dist = len({x for v in g.values() for x in v})
    chk('TF06 OS-0421 aparece nos grupos T1 e T2 com a mesma identidade', 'OS-0421' in g.get('T1', []) and 'OS-0421' in g.get('T2', []), g)
    chk('TF06 total geral conta O.S. distintas (10), não a soma dos grupos (11)', soma == dist + 1 and tot.startswith(f'Total: {dist} O.S. distintas'), (soma, dist, tot))
    cont = J("(()=>{const s=[...document.querySelectorAll('span')].find(s=>s.offsetParent&&/^\\d+ de \\d+$/.test(s.innerText.trim())); return s?s.innerText.trim():'';})()")
    chk('TF06 contador da grade no agrupado conta O.S. distintas (10 de 10), não grupos (9)', cont == f'{dist} de {len(todas)}', cont)
    shot('tf06-1440-agrupado')
    marca('T1'); marca('T2'); fecha_tal(); g2 = J("[...document.querySelectorAll('[role=row].g2r')].filter(r=>r.offsetParent).map(r=>r.querySelector('[role=cell]').innerText.replace('▾','').trim())"); tot = next((x for x in notas() if x.startswith('Total')), '')
    chk('TF06 com T1 ou T2: só grupos T1 e T2; total 2 O.S. · 452 ha (350 + 102, cada O.S. uma vez)', [x for x in g2 if not x.startswith('O')] == ['T1', 'T2'] and tot.startswith('Total: 2 O.S. distintas · 452 ha'), (g2, tot))
    J("[...document.querySelectorAll('[role=row].g2r')].filter(r=>r.offsetParent).find(r=>/^OS-0421/.test(r.innerText.trim())).querySelector('[role=cell]').click()"); time.sleep(.5)
    chk('TF06 clicar na O.S. dentro do grupo abre o detalhe da própria O.S.', (J("(document.querySelector('aside[role=dialog]')||{}).innerText||''") or '').startswith('OS-0421'))
    J("(()=>{const b=document.querySelector('aside[role=dialog] button[aria-label=Fechar]'); b&&b.click();})()"); time.sleep(.3)
    J("[...document.querySelectorAll('button')].find(b=>b.innerText.trim()==='Desagrupar').click()"); time.sleep(.4); todos()
    chk('TF06 desagrupar volta às linhas canônicas', sorted(ids()) == sorted(todas), len(ids()))
    chk('sem botão Expandir/Recolher na lista sem grupos', not J("[...document.querySelectorAll('.g2xtog')].some(b=>b.offsetParent)"))
    chk('sem erro de script (1440)', not J("window.__e"), J("window.__e"))
    # ---------------- TF04: 390 px, toque e teclado ----------------
    c.aparelho(390, 844, 2, True); c.goto(URL, 1.2); J("window.__e=[];addEventListener('error',e=>window.__e.push(String(e.message)))")
    shot('tf04-390-antes')
    b = J("(()=>{const r=document.getElementById('ost_btn').getBoundingClientRect(); return [r.left,r.right,r.top,r.height,innerWidth,document.documentElement.scrollWidth];})()")
    chk('TF04 390 px: Talhão visível sem rolar a tabela, alvo ≥ 28 px e página sem rolagem horizontal', b[0] >= 0 and b[1] <= b[4] and b[3] >= 28 and b[5] <= b[4] + 1, b)
    c.toque(b[0] + 20, b[2] + b[3] / 2); time.sleep(.3)
    lab = J("(()=>{const l=[...document.querySelectorAll('[aria-label=\"Filtrar por talhão\"] label')].find(l=>/^T1\\s/.test(l.innerText.trim())); const r=l.getBoundingClientRect(); return [r.left+20,r.top+r.height/2,r.height];})()")
    pop = J("(()=>{const r=document.querySelector('[aria-label=\"Filtrar por talhão\"]').getBoundingClientRect(); const m=document.querySelector('main'); return [r.left,r.right,innerWidth,document.documentElement.scrollWidth,document.activeElement&&document.activeElement.id,m?m.getBoundingClientRect().left:0];})()")
    chk('TF04 390 px: seletor aberto cabe entre o menu e a borda, sem deslocar a página, foco na pesquisa', pop[0] >= pop[5] and pop[1] <= pop[2] and pop[3] <= pop[2] + 1 and pop[4] == 'ost_q', pop)
    c.toque(lab[0], lab[1]); time.sleep(.3)
    chk('TF04 toque: abre o seletor e marca T1 (alvo ≥ 32 px); a lista filtra na hora', lab[2] >= 32 and ids() == ['OS-0421'] and btn_tal() == 'Talhão: T1 ▾', (lab, ids()))
    shot('tf04-390-depois')
    c.tecla('Escape', 'Escape', 27); time.sleep(.3)
    chk('TF04 Esc fecha o seletor e o foco volta ao botão Talhão', not J("!!document.querySelector('[aria-label=\"Filtrar por talhão\"]')") and J("document.activeElement&&document.activeElement.id") == 'ost_btn')
    c.tecla('Enter', 'Enter', 13, text='\r'); time.sleep(.4)
    foco_q = J("document.activeElement&&document.activeElement.id")
    for ch in 'T2': c.tecla(ch, 'Key' + ch if ch.isalpha() else 'Digit' + ch, ord(ch), text=ch)
    time.sleep(.4); filtradas = J("[...document.querySelectorAll('[aria-label=\"Filtrar por talhão\"] label')].map(l=>l.innerText.replace(/\\s+\\d+$/,'').trim())") or []
    chk('TF04 teclado: Enter abre com o foco na pesquisa; digitar "T2" deixa só T2', foco_q == 'ost_q' and filtradas == ['T2'], (foco_q, filtradas))
    c.tab(2); c.tecla(' ', 'Space', 32, text=' '); time.sleep(.4)
    chk('TF04 teclado: Tab até T2 e Espaço marca (T1 ou T2)', sorted(ids()) == ['OS-0421', 'OS-0431'], (ids(), J("document.activeElement&&document.activeElement.outerHTML.slice(0,80)")))
    c.tecla('Escape', 'Escape', 27); time.sleep(.3)
    J("[...document.querySelectorAll('[role=row].g2ed')].filter(r=>r.offsetParent)[0].focus()"); c.tecla('Enter', 'Enter', 13, text='\r'); time.sleep(.5)
    det = J("!!document.querySelector('aside[role=dialog]')"); shot('tf04-390-detalhe')
    J("(()=>{const b=document.querySelector('aside[role=dialog] button[aria-label=Fechar]'); b&&b.click();})()"); time.sleep(.4)
    chk('TF04 Enter na linha abre o detalhe; fechar volta com o recorte', det and sorted(ids()) == ['OS-0421', 'OS-0431'] and btn_tal() == 'Talhão: T1, T2 ▾', (det, ids()))
    chk('sem erro de script (390)', not J("window.__e"), J("window.__e"))
finally:
    c.close(); srv.terminate()
print(f'RESULTADO: {len(OK)}/{len(OK) + len(FAIL)} ok' + (' · FALHAS: ' + '; '.join(FAIL) if FAIL else ''))
sys.exit(1 if FAIL else 0)
