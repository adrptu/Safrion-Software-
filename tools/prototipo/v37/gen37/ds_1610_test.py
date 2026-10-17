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
  C · navegador: Cartões (VIS-07, 17/10, revê a VIS-06) em O.S. (também agrupada por talhão), Planejar safra, Parceiros e Produtos (árvore):
      grade de cartões compactos, sem cabeçalho de colunas, título com o selo de estado, até 4 campos rotulados; Atividades em Tabela ordenam
      por Custo/ha e filtram por Insumos.
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
    # VIS-07 (17/10/2026, proprietário: "os cartoes em ordem de serviço estao fora do padrao design system"; revê a VIS-06 de 16/10): o oráculo
    # antigo pedia um cartão por linha, colunas alinhadas e rótulos uma vez no alto. Agora: grade de cartões compactos (vários por fileira a
    # 1440 px), inclusive agrupada; sem cabeçalho de colunas; título com o selo de estado; até 4 campos, cada um com o rótulo.
    # Contraprova: o render anterior (cartão em linha com cabeçalho de colunas) reprova C1.
    for pg, gid, selo in [('OS.dc.html?view=cartoes', 'g_os', True), ('OS.dc.html?view=cartoes&ag=onde', 'g_os', True), ('SAF.dc.html?view=cartoes', 'g_saf', False),
                          ('CD-05.dc.html?view=cartoes', 'g_forn', False), ('CD-06.dc.html?view=cartoes', 'g_itm', False)]:
        c.goto(BASE + pg, 1.6)
        m = J(f"""(()=>{{ const box=document.querySelector('[data-g2cd="{gid}"]'); if(!box) return null; const vis=e=>!!e&&e.getClientRects().length>0;
            const ks=[...box.querySelectorAll('.g2cd')].filter(vis), hd=[...box.querySelectorAll('.g2cd-hd')].filter(vis).length;
            const fil={{}}; ks.forEach(k=>{{ const t=Math.round(k.getBoundingClientRect().top); fil[t]=(fil[t]||0)+1; }});
            const fs=k=>[...k.querySelectorAll(':scope > .g2cd-lin .g2cd-f')].filter(vis), nf=ks.map(k=>fs(k).length);
            const rot=ks.every(k=>fs(k).every(f=>{{ const l=f.querySelector('.g2cd-fl'); return vis(l)&&l.innerText.trim().length>0; }}));
            const grupos=[...box.querySelectorAll('.g2cd-gcab')].filter(vis).length, arvore=ks.some(k=>vis(k.querySelector('.g2cd-nk')));   /* árvore: categorias com itens dentro (as vazias ficam sem seta) */
            return {{n:ks.length, hd, porFileira:Math.max(0,...Object.values(fil)), cmax:Math.max(0,...nf), rot, grupos, arvore,
                     selo:ks.filter(k=>vis(k.querySelector(':scope > .g2cd-lin .g2cd-selo'))).length}}; }})()""")
        if m and m.get('arvore') and m['cmax'] == 0:   # árvore (Produtos): o cartão é a categoria; os campos rotulados estão nos itens, ao abrir
            J(f"[...document.querySelectorAll('[data-g2cd=\"{gid}\"] .g2cd .g2cd-nk')].find(e=>e.getClientRects().length).click()"); time.sleep(.6)
            k = J(f"""(()=>{{ const vis=e=>!!e&&e.getClientRects().length>0; const ks=[...document.querySelectorAll('[data-g2cd="{gid}"] .g2cd-k')].filter(vis);
                const fs=k=>[...k.querySelectorAll('.g2cd-f')].filter(vis); return {{n:ks.length, cmax:Math.max(0,...ks.map(k=>fs(k).length)),
                rot:ks.every(k=>fs(k).every(f=>{{ const l=f.querySelector('.g2cd-fl'); return vis(l)&&l.innerText.trim().length>0; }}))}}; }})()""") or {}
            m['cmax'] = k.get('cmax', 0) if k.get('n') else 0; m['rot'] = m['rot'] and k.get('rot', False); m['itens'] = k
        chk(f'C1 VIS-07 {pg}: grade de cartões compactos ({m and m["n"]}), sem cabeçalho de colunas, até 4 campos rotulados' + (' e o selo de fase no título' if selo else ''),
            m and m['n'] > 0 and m['hd'] == 0 and (m['porFileira'] >= 2 or m['n'] == 1) and 1 <= m['cmax'] <= 4 and m['rot'] and (not selo or m['selo'] == m['n'])
            and ('ag=' not in pg or m['grupos'] >= 2), m)
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
