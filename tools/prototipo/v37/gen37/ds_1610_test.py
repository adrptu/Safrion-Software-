# -*- coding: utf-8 -*-
"""Padrões do proprietário de 16/10/2026 (docs/design-system/padroes-1610.md), com a skill padrao-safrion:
  S · sem navegador, em todas as páginas do _render:
      TAB-08 toda tabela do motor tem o cabeçalho com ⇅ e funil (cab_colunas_html) e a moldura da tabela (TABELA_CSS);
      AGR-02 nenhuma página tem a trilha do agrupamento (data-g2agtr);
      TAB-08 Planos agronômicos › Atividades em Tabela usa a mesma peça de cabeçalho e de filtro (pa_tb).
  B · navegador a 1440 × 900, todas as telas com tabela do motor à vista:
      B1 a tabela tem moldura (borda e raio de 12 px) e o cabeçalho tem ⇅ e funil em toda coluna;
      B2 toda linha que abre o detalhe (g2ed) mostra a seta na 1ª célula (› ou ▸/▾), sem texto (TAB-04);
      B3 sem linha vertical no cabeçalho e nas células da 1ª coluna.
  C · navegador: Cartões em linha (VIS-06) em O.S., Planejar safra, Parceiros e Produtos (árvore): um cartão por linha (mesma esquerda e
      largura), colunas alinhadas entre os cartões, rótulos uma vez no alto; Atividades em Tabela ordenam por Custo/ha e filtram por Insumos.
Contraprova: RENDER_DIR=<render da versão anterior> python3 ds_1610_test.py reprova.
Uso (de gen37/): CHROME_BIN=… SAFRION_DADOS=sintetico python3 -B ds_1610_test.py   · DS_PARTES=S,B,C"""
import os, re, sys, json, glob, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
OK, FAIL = [], []
def chk(n, c, info=''):
    (OK if c else FAIL).append(n); print(('OK    ' if c else 'FALHA ') + n + ('' if c else ' · ' + str(info)[:900]), flush=True)
R = os.environ.get('RENDER_DIR') or os.path.join(HERE, '_render')
PARTES = set((os.environ.get('DS_PARTES') or 'S,B,C').split(','))
PAGS = sorted(f for f in glob.glob(os.path.join(R, '*.dc.html')) if os.path.basename(f) != 'Main.dc.html')
def tela(s): return not (len(s) < 5000 and 'location.replace' in s)

def parte_s():
    sem_cab, trilha, n_tab = [], [], 0
    for f in PAGS:
        s = open(f, encoding='utf-8').read(); pg = os.path.basename(f)
        if not tela(s): continue
        for g in set(re.findall(r'data-g2g="([A-Za-z0-9_]+)"', s)):
            n_tab += 1
            if f'list="{{{{{g}_head}}}}"' not in s: sem_cab.append((pg, g))
        if re.search(r'<nav[^>]*data-g2agtr=', s): trilha.append(pg)
    css = 'g2rola:has(>[role=table][data-g2g]){border:1px solid #E4E9E5;border-radius:12px'
    sem_css = [os.path.basename(f) for f in PAGS if 'data-g2g=' in open(f, encoding='utf-8').read() and css not in open(f, encoding='utf-8').read()]
    chk(f'S1 TAB-08 toda tabela do motor ({n_tab}) tem o cabeçalho com ordenar e filtrar', n_tab > 80 and not sem_cab, sem_cab[:6])
    chk('S2 TAB-08 a moldura da tabela vale em toda página com tabela do motor', not sem_css, sem_css[:6])
    chk(f'S3 AGR-02 nenhuma página com a trilha do agrupamento ({len(PAGS)} páginas)', not trilha, trilha[:6])
    pa = open(os.path.join(R, 'PA.dc.html'), encoding='utf-8').read()
    chk('S4 TAB-08 Atividades do plano em Tabela usa a peça do motor (cabeçalho e filtro pa_tb)', 'list="{{pa_tb_head}}"' in pa and '{{pa_tb_fm.open}}' in pa)

def parte_b(c, J, BASE):
    ruins = {k: [] for k in ('moldura', 'cab', 'seta', 'vert')}; n = 0
    for f in PAGS:
        pg = os.path.basename(f); s = open(f, encoding='utf-8').read()
        if not tela(s) or 'data-g2g=' not in s: continue
        c.goto(BASE + pg, 1.1)
        r = J("""(()=>{ const out=[]; document.querySelectorAll('[role=table][data-g2g]').forEach(t=>{ if(!t.getClientRects().length) return;
            const box=t.parentElement, cs=getComputedStyle(box), hs=[...t.querySelectorAll('[role=columnheader]')].filter(h=>h.querySelector('.g2hb'));
            const ferr=hs.some(h=>h.querySelector('button.g2hb'))?hs.filter(h=>!h.querySelector('.g2so')||!h.querySelector('.g2fb')).length:0;
            const rows=[...t.querySelectorAll('[role=row].g2ed')].filter(r=>r.getClientRects().length).slice(0,12);
            // TAB-09 (16/10/2026): a seta fica na 1ª célula da linha (com seleção, antes da caixa), não necessariamente na do nome (.g2c0)
            const semSeta=rows.filter(r=>{ const c0=r.querySelector('[role=cell]'); return !c0||!c0.querySelector('.g2drill,.g2car'); }).map(r=>r.getAttribute('data-rid'));
            const c0=t.querySelector('[role=cell].g2c0'), h0=t.querySelector('[role=columnheader].g2c0');
            const vert=[c0,h0].filter(Boolean).some(e=>{ const sh=getComputedStyle(e).boxShadow; return sh&&sh!=='none'; });
            out.push({g:t.getAttribute('data-g2g'), moldura:cs.borderTopWidth==='1px'&&cs.borderTopLeftRadius==='12px', ferr, semSeta, vert}); }); return out; })()""") or []
        for t in r:
            n += 1
            if not t['moldura']: ruins['moldura'].append((pg, t['g']))
            if t['ferr']: ruins['cab'].append((pg, t['g'], t['ferr']))
            if t['semSeta']: ruins['seta'].append((pg, t['g'], t['semSeta'][:3]))
            if t['vert']: ruins['vert'].append((pg, t['g']))
    chk(f'B1 TAB-08 toda tabela à vista tem moldura de 12 px ({n} tabelas)', n > 40 and not ruins['moldura'], ruins['moldura'][:6])
    chk('B1b TAB-08 toda coluna com ordenar tem ⇅ e funil', not ruins['cab'], ruins['cab'][:6])
    chk('B2 TAB-04 toda linha que abre o detalhe mostra a seta na 1ª célula', not ruins['seta'], ruins['seta'][:6])
    chk('B3 TAB-08 sem linha vertical na 1ª coluna', not ruins['vert'], ruins['vert'][:6])

def parte_c(c, J, BASE):
    for pg, gid in [('OS.dc.html?view=cartoes', 'g_os'), ('SAF.dc.html?view=cartoes', 'g_saf'), ('CD-05.dc.html?view=cartoes', 'g_forn'), ('CD-06.dc.html?view=cartoes', 'g_itm')]:
        c.goto(BASE + pg, 1.6)
        m = J(f"""(()=>{{ const box=document.querySelector('[data-g2cd="{gid}"]'); if(!box) return null; const ks=[...box.querySelectorAll('.g2cd')].filter(k=>k.getClientRects().length);
            const L=new Set(ks.map(k=>Math.round(k.getBoundingClientRect().left))), W=new Set(ks.map(k=>Math.round(k.getBoundingClientRect().width)));
            const col=(k,i)=>{{ const f=k.querySelectorAll('.g2cd-lin .g2cd-f')[i]; return f?Math.round(f.getBoundingClientRect().left):null; }};
            const n=ks.length?ks[0].querySelectorAll('.g2cd-lin .g2cd-f').length:0, alinh=[...Array(n).keys()].every(i=>new Set(ks.map(k=>col(k,i))).size===1);
            const hd=box.querySelector('.g2cd-hd'); return {{n:ks.length, esquerda:L.size, largura:W.size, campos:n, alinh, rotulos:hd?hd.innerText.replace(/\\s+/g,' ').trim():''}}; }})()""")
        chk(f'C1 VIS-06 {pg}: um cartão por linha ({m and m["n"]}), colunas alinhadas e rótulos uma vez no alto',
            m and m['n'] > 0 and m['esquerda'] == 1 and m['largura'] == 1 and m['alinh'] and (m['campos'] == 0 or m['rotulos']), m)
    c.goto(BASE + 'PA.dc.html?view=tabela#plano=SOJA-AT', 1.6)
    ids = lambda: J("[...document.querySelectorAll('.pa-tb-l[data-atv]')].map(x=>x.getAttribute('data-atv'))") or []
    a0 = ids()
    J("[...document.querySelectorAll('.pa-tb .g2hb')].find(b=>/custo/i.test(b.innerText)).click()"); time.sleep(.5)
    custos = J("[...document.querySelectorAll('.pa-tb-l[data-atv]')].map(x=>x.innerText)") or []
    vals = [float(re.search(r'R\$\s*([\d.]+,\d+)', t).group(1).replace('.', '').replace(',', '.')) for t in custos if re.search(r'R\$\s*([\d.]+,\d+)', t)]
    J("[...document.querySelectorAll('.pa-tb .g2fb')].find(b=>/insumos/i.test(b.getAttribute('aria-label'))).click()"); time.sleep(.5)
    J("(()=>{const l=[...document.querySelectorAll('[role=dialog] label')].find(l=>/2 insumos/.test(l.innerText)); l.querySelector('input').click();})()"); time.sleep(.3)
    J("[...document.querySelectorAll('[role=dialog] button')].find(b=>b.innerText.trim()==='OK').click()"); time.sleep(.5)
    a2 = ids(); txt = J("[...document.querySelectorAll('.pa-tb-l[data-atv]')].map(x=>x.innerText).join('|')") or ''
    chk('C2 TAB-08 Atividades em Tabela: ⇅ do Custo/ha ordena do menor para o maior; o funil de Insumos tira "2 insumos"',
        len(a0) >= 6 and vals == sorted(vals) and len(vals) >= 5 and 0 < len(a2) < len(a0) and '2 insumos' not in txt, [a0, vals, a2])

if 'S' in PARTES: parte_s()
if PARTES & {'B', 'C'}:
    from comp_lib import Chrome, servir
    p, srv = servir(R); c = Chrome(); J = c.js; BASE = f'http://127.0.0.1:{p}/'
    c.aparelho(1440, 900, 1); c.goto(BASE + 'Main.dc.html', .3); J("localStorage.clear(); localStorage.setItem('safrion.perfilDemo','Ana')")
    if 'B' in PARTES: parte_b(c, J, BASE)
    if 'C' in PARTES: parte_c(c, J, BASE)
    errs = J("window.__errs||[]") or []
    chk('D sem erro de JavaScript', not errs, errs[:4]); c.close()
print(f'RESULTADO: {len(OK)} ok · {len(FAIL)} falhas' + (' · ' + '; '.join(FAIL) if FAIL else ''))
sys.exit(1 if FAIL else 0)
