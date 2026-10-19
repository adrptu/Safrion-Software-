# -*- coding: utf-8 -*-
"""Padrões do proprietário de 15/10/2026 (docs/design-system/padroes-1510.md): "padronize no design system essas melhorias que definimos hoje".
  S · sem navegador, em todas as páginas do _render:
      TAB-01 Agrupar por à esquerda de Colunas em toda barra que tem os dois; TAB-02 a contagem "x de y" só sem filtro rápido;
      TAB-03 o filtro da coluna é o funil (ICONS['filtro']), cheio quando ativo; TAB-04 a seta de abrir e recolher não tem dica (title);
      AVI-01 toda página com aviso traz G2_TOAST_TOM; SEL-03 toda página traz a lista suspensa do DS (g2dsel);
      TAB-05 e TAB-06: opções da grade (menu_linha, sico_so_icone) e uso no Planejar safra.
  A · tom do aviso (node): feito → verde ✓, impedido → âmbar ⚠, informa → branco ⓘ.
  B · navegador a 1440 × 900: O.S. › Kanban com Agrupar por (as raias seguem o grupo), Carga sem cartões de resumo, Fase na área da visão
      (fora da faixa do topo), funil cheio com filtro ativo, lista suspensa do DS no Agrofit (abre, ↓ e Enter escolhem, Esc fecha).
  C · navegador, todas as telas: linha que abre detalhe abaixo mostra a seta ▸/▾ (TAB-04, 16/10), inclusive Planos › Atividades em Tabela.
Uso (de gen37/, depois de build.py e montar_render.py): python3 ds_1510_test.py · RENDER_DIR=<dir> serve outro _render · DS_PARTES=S,A,B"""
import os, re, sys, json, glob, time, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import engine as E

OK, FAIL = [], []
def chk(n, c, info=''):
    (OK if c else FAIL).append(n); print(('OK    ' if c else 'FALHA ') + n + ('' if c else ' · ' + str(info)[:900]), flush=True)
R = os.environ.get('RENDER_DIR') or os.path.join(HERE, '_render')
PARTES = set((os.environ.get('DS_PARTES') or 'S,A,B,C').split(','))
PAGS = sorted(f for f in glob.glob(os.path.join(R, '*.dc.html')) if os.path.basename(f) != 'Main.dc.html')   # Main: página técnica mínima, sem tela de uso

def parte_s():
    ruins = {k: [] for k in ('ord', 'cnt', 'fun', 'car', 'toast', 'dsel')}
    for f in PAGS:
        s = open(f, encoding='utf-8').read(); pg = os.path.basename(f)
        if len(s) < 5000 and 'location.replace' in s: continue   # só redirecionamento (MA-01..05 → MA): não desenha tela
        for g in set(re.findall(r'data-g2agb="([A-Za-z0-9_]+)"', s)):
            a, b = s.find(f'data-g2agb="{g}"'), s.find(f'data-g2cvb="{g}"')
            if b != -1 and a > b: ruins['ord'].append((pg, g))
        for m in re.finditer(r'<span data-g2cnt="([^"]+)"', s):
            if f'<sc-if value="{{{{{m.group(1)}_hasqf !== true}}}}"' not in s[max(0, m.start() - 120):m.start()]: ruins['cnt'].append((pg, m.group(1)))
        for m in re.finditer(r'<button type="button" class="g2fb"[^>]*>(.{0,400}?)</button>', s):
            if E.ICONS['filtro'] not in m.group(1) or 'fill="{{h.ffill}}"' not in m.group(1): ruins['fun'].append(pg)
        for m in re.finditer(r'<button[^>]*class="(?:g2car|pa-expandir)[^"]*"[^>]*>', s):
            if ' title=' in m.group(0): ruins['car'].append(pg)
        if 'class="g2toast"' in s and 'function G2_TOAST_TOM' not in s: ruins['toast'].append(pg)
        if 'window.g2dselAbre' not in s: ruins['dsel'].append(pg)
    chk(f'S1 TAB-01 Agrupar por à esquerda de Colunas em toda barra ({len(PAGS)} páginas)', len(PAGS) > 100 and not ruins['ord'], ruins['ord'][:6])
    chk('S2 TAB-02 contagem "x de y" só quando a grade não tem filtro rápido', not ruins['cnt'], ruins['cnt'][:6])
    chk('S3 TAB-03 filtro da coluna com o funil (vazado; cheio pelo estado)', not ruins['fun'] and 'ffill' in open(os.path.join(HERE, 'g2lib.js'), encoding='utf-8').read(), ruins['fun'][:6])
    chk('S4 TAB-04 seta de abrir e recolher sem dica (title)', not ruins['car'], ruins['car'][:6])
    chk('S5 AVI-01 toda página com aviso traz o tom (G2_TOAST_TOM)', not ruins['toast'], ruins['toast'][:6])
    chk('S6 SEL-03 toda página traz a lista suspensa do DS (g2dsel)', not ruins['dsel'], ruins['dsel'][:6])
    # TAB-01 (16/10): na barra da grade, "Expandir tudo" vem antes de Agrupar por e Colunas; o modo de visão fica na ponta
    ordem = []
    for f in PAGS:
        s = open(f, encoding='utf-8').read()
        for m in re.finditer(r'data-g2cvb="([A-Za-z0-9_]+)"', s):
            g = m.group(1); ini = s.rfind(f'data-g2q="{g}"', 0, m.start())
            if ini < 0: continue
            seg = s[ini:m.start()]
            if 'class="g2xtog"' not in seg and 'class="g2xtog"' in s[m.start():m.start() + 4000].split('data-g2q=')[0]: ordem.append((os.path.basename(f), g))
    chk('S8 TAB-01 Expandir tudo antes de Agrupar por e Colunas em toda grade em árvore', not ordem, ordem[:6])
    saf = open(os.path.join(HERE, 'areas', 'processo_safra.py'), encoding='utf-8').read()
    sig = E.grid.__code__.co_varnames[:E.grid.__code__.co_argcount + E.grid.__code__.co_kwonlyargcount]
    chk('S7 TAB-05/06 opções da grade (menu_linha, sico_so_icone) e uso no Planejar safra (Talhões e cultivos; Operações e recursos)',
        'menu_linha' in sig and 'sico_so_icone' in sig and 'menu_linha=True' in saf and 'sico_so_icone=True' in saf, sig)

def parte_a():
    js = E.G2_TOAST_JS + r"""
const C = t => { const r = G2_TOAST_TOM(t); return r.ic; };
console.log(JSON.stringify({salvo: C('Plano salvo · v7'), incl: C('Insumo incluído'), nao: C('Não foi possível liberar: falta a aprovação'),
  inf: C('Informe a dose'), neutro: C('Etapa 2 de 4: Operações')}));"""
    r = subprocess.run(['node', '-e', js], capture_output=True, text=True)
    try: t = json.loads(r.stdout.strip().splitlines()[-1])
    except Exception: t = {}
    chk('A1 AVI-01 tom pelo texto: salvo/incluído verde, "Não…"/"Informe…" âmbar, o resto neutro',
        t.get('salvo') == t.get('incl') == '#1E7A4C' and t.get('nao') == t.get('inf') == '#B7791F' and t.get('neutro') == '#4B5A51', [t, r.stderr[-300:]])

def parte_b():
    from comp_lib import Chrome, servir
    p, srv = servir(R); c = Chrome(); J = c.js
    U = lambda pg: f'http://127.0.0.1:{p}/{pg}'
    def espera(expr, lim=8.0):
        t0 = time.time()
        while time.time() - t0 < lim:
            if J(expr): return True
            time.sleep(.15)
        return False
    try:
        c.call('Page.addScriptToEvaluateOnNewDocument', {'source': "window.__err='';addEventListener('error',e=>{window.__err+=(e.message||'erro')+' | ';});"})
        c.aparelho(1440, 900, 1, False)
        c.goto(U('OS.dc.html'), 1.6); espera("!!document.querySelector('[data-visoes-gid=g_os]')")
        # TAB-01: Fase fora da faixa do topo (.mf-tela), na área da visão
        fase = json.loads(J("""JSON.stringify((()=>{const g=[...document.querySelectorAll('[role=group]')].find(g=>/fase/i.test(g.getAttribute('aria-label')||'')&&g.getClientRects().length);
          return g?{topo:!!g.closest('.mf-tela'),area:!!g.closest('.os-colbar')}:null;})())""") or 'null')
        chk('B1 TAB-01 O.S.: filtro rápido de Fase na área da visão, fora da faixa do topo', bool(fase) and not fase['topo'] and fase['area'], fase)
        # VIS-05: Agrupar por no Kanban; as raias seguem o grupo
        J("[...document.querySelectorAll('[data-visoes-gid=g_os] button')].find(b=>/kanban/i.test(b.getAttribute('aria-label')||''))?.click()")
        espera("!!document.querySelector('.os-agkb [data-g2agb=g_os]')")
        J("document.querySelector('.os-agkb [data-g2agb=g_os]')?.click()")
        espera("[...document.querySelectorAll('[role=menu] [role=menuitemradio],[role=menu] [role=menuitem],[role=menu] button')].some(b=>b.getClientRects().length)", 4)
        esc = J("""(()=>{const its=[...document.querySelectorAll('[role=menu] [role=menuitemradio],[role=menu] [role=menuitem],[role=menu] button')].filter(b=>b.getClientRects().length&&/fazenda|talh|cultura|tipo|respons/i.test(b.textContent));
          const b=its[0]; if(!b) return ''; b.click(); return b.textContent.trim();})()""")
        raias = espera("document.querySelectorAll('.os-raia').length>0", 5)
        n = J("document.querySelectorAll('.os-raia').length")
        chk('B2 VIS-05 O.S. › Kanban: "Agrupar por" à vista e, escolhido um grupo, o quadro vira raias por grupo', bool(esc) and raias, [esc, n])
        # TAB-07: Carga sem cartões de resumo
        J("[...document.querySelectorAll('[data-visoes-gid=g_os] button')].find(b=>/carga/i.test(b.getAttribute('aria-label')||''))?.click()")
        espera("!!document.querySelector('[aria-label=\"Alocação de recursos na semana\"]')")
        cards = J("""(()=>{const t=document.querySelector('[aria-label="Alocação de recursos na semana"]'); if(!t) return -1;
          const box=t.parentElement; let n=0; for(const ch of box.children){ if(ch===t) break; if(ch.getClientRects().length) n++; } return n;})()""")
        chk('B3 TAB-07 O.S. › Carga: nada entre o topo da visão e a tabela de alocação (sem cartões de resumo)', cards == 0, cards)
        # TAB-03: funil cheio com filtro ativo
        # a visão escolhida fica guardada (VISOES-1): volta para a Tabela antes de olhar o cabeçalho
        J("[...document.querySelectorAll('[data-visoes-gid=g_os] button')].find(b=>/tabela|lista/i.test(b.getAttribute('aria-label')||''))?.click()")
        espera("[...document.querySelectorAll('.g2fb')].some(b=>b.getClientRects().length)")
        f0 = J("[...document.querySelectorAll('.g2fb')].find(b=>b.getClientRects().length)?.querySelector('svg')?.getAttribute('fill')")
        chk('B4 TAB-03 funil vazado sem filtro e nome acessível "Filtrar <coluna>"', f0 == 'none' and (J("[...document.querySelectorAll('.g2fb')].find(b=>b.getClientRects().length)?.getAttribute('aria-label')") or '').startswith('Filtrar '), f0)
        # SEL-03: lista suspensa do DS no Agrofit
        c.goto(U('AG-07.dc.html'), 1.6); espera("[...document.querySelectorAll('main select')].some(s=>s.getClientRects().length)")
        info = json.loads(J("""JSON.stringify((()=>{const s=[...document.querySelectorAll('main select')].find(x=>x.getClientRects().length&&!x.disabled&&x.options.length>1);
          if(!s) return null; s.setAttribute('data-t1510','1'); const r=s.getBoundingClientRect(); return {x:r.left+r.width/2,y:r.top+r.height/2,v:s.value,n:s.options.length};})())""") or 'null')
        if info:
            c.mouse(info['x'], info['y'], 'mousePressed', 'left'); c.mouse(info['x'], info['y'], 'mouseReleased', 'left')
            aberta = espera("!!document.querySelector('.g2dsel')&&document.querySelector('.g2dsel').getClientRects().length>0", 3)
            c.tecla('ArrowDown', 'ArrowDown', 40); c.tecla('Enter', 'Enter', 13); time.sleep(.3)
            v1 = J("document.querySelector('[data-t1510]').value"); fechou = J("!document.querySelector('.g2dsel')||!document.querySelector('.g2dsel').getClientRects().length")
            chk('B5 SEL-03 Agrofit: a lista de escolha abre no desenho do DS; ↓ e Enter escolhem e fecham', aberta and v1 != info['v'] and fechou, [info, v1, aberta, fechou])
        else:
            chk('B5 SEL-03 Agrofit: há lista de escolha à vista', False, 'nenhum select visível em AG-07')
        e = J("window.__err||''"); chk('B6 sem erro de JS nas telas abertas', not e, e)
    finally:
        try: c.close()
        except Exception: pass
        srv.terminate()

# C · TAB-04 (16/10/2026, proprietário: "na tabela tá sem símbolo drill down de planos agronômicos, verifique nas demais"): toda linha de
# tabela ou lista que abre um detalhe abaixo (controle com aria-expanded + aria-controls, fora de menu) mostra a seta ▸/▾ na própria linha
SETA = r"""JSON.stringify((()=>{const vis=e=>e.getClientRects().length>0;
  const tem=r=>[...r.querySelectorAll('.g2car,svg,[aria-hidden=true]')].some(e=>vis(e)&&(e.classList.contains('g2car')||/[▸▾›⌄]/.test(e.textContent||'')||e.tagName.toLowerCase()==='svg'))||/[▸▾›]/.test(r.innerText||'');
  const ruins=[]; for(const c of document.querySelectorAll('[aria-expanded][aria-controls]:not([aria-haspopup])')){ if(!vis(c)) continue;
    const r=c.closest('[role=row],[role=listitem]'); if(!r||!vis(r)) continue; if(!tem(r)) ruins.push((r.innerText||'').replace(/\s+/g,' ').slice(0,50)); }
  return ruins.slice(0,4);})())"""
def parte_c():
    from comp_lib import Chrome, servir
    p, srv = servir(R); c = Chrome(); J = c.js
    try:
        c.aparelho(1440, 900, 1, False); ruins = {}
        pags = [os.path.basename(f) for f in PAGS] + ['PA.dc.html?view=tabela#plano=SOJA-AT']
        for pg in pags:
            try:
                c.goto(f'http://127.0.0.1:{p}/{pg}', 1.0); r = json.loads(J(SETA) or '[]')
            except Exception as e: r = ['erro: ' + str(e)[:60]]
            if r: ruins[pg] = r
        chk(f'C1 TAB-04 toda linha que abre detalhe abaixo mostra a seta ▸/▾ ({len(pags)} telas, inclusive Planos › Atividades em Tabela)', not ruins, ruins)
        c.goto(f'http://127.0.0.1:{p}/PA.dc.html?view=tabela#plano=SOJA-AT', 1.6)
        n = J("(()=>{const b=[...document.querySelectorAll('.pa-tb-l')].filter(r=>r.getClientRects().length); return [b.length, b.filter(r=>r.querySelector('.g2car')).length];})()")
        chk('C2 Planos › Atividades em Tabela: cada atividade tem a seta de abrir os insumos', n and n[0] > 0 and n[0] == n[1], n)
    finally:
        try: c.close()
        except Exception: pass
        srv.terminate()

if 'S' in PARTES: parte_s()
if 'A' in PARTES: parte_a()
if 'B' in PARTES: parte_b()
if 'C' in PARTES: parte_c()
print(f'RESULTADO: {len(OK)} ok · {len(FAIL)} falhas')
sys.exit(1 if FAIL else 0)
