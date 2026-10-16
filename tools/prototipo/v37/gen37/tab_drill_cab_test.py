# -*- coding: utf-8 -*-
"""TAB-09 e TAB-10 (proprietário, 16/10/2026; docs/design-system/padroes-1610.md), com a skill padrao-safrion: varredura de todas as telas.
  TAB-09 "colone os icones de drill down sempre na esquerda, fica mais intuitivo em todas telas": a seta de abrir/expandir (▸ ▾ ›) fica na
         1ª coluna, à esquerda de qualquer outra coluna da linha (seleção, número, texto, ícone). Em árvore e grupos o recuo do nível continua.
         Seta de seção (botão com aria-expanded, sem lista suspensa) vem antes do nome.
  TAB-10 "padronize a altura das colunas cabeçalho das tabelas, em diferentes telas temos diferentes alturas": toda linha de cabeçalho de tabela
         (role=columnheader ou th) tem 40 px (±1), a altura de duas linhas de rótulo do cabeçalho do motor.
Varre todas as páginas do _render (fora Main e as páginas de redirecionamento) a 1440 × 900 e 390 × 844 (toque), em cada estado:
  inicial · "Expandir tudo" (árvore e grupos) · o outro modo do seletor Tabela | Cartões · e estados extras que só abrem por endereço
  (Atividades do plano, ficha do Agrofit).
Contraprova: RENDER_DIR=<render da 519ed7b> reprova (Atividades com o DAP antes da seta, seleção antes da seta, seta de seção no fim;
cabeçalhos de 26,6 a 64,4 px).
Uso (de gen37/): CHROME_BIN=… CDP_GL=1 SAFRION_DADOS=sintetico python3 -B tab_drill_cab_test.py   · TDC_LARG=1440 ou 390 (padrão: as duas)
Saída: uma linha por desvio (até 40 por regra) e o RESULTADO; sai 1 se falhar."""
import os, sys, json, glob, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, servir
from areas.maquinas import REDIRECIONA

R = os.environ.get('RENDER_DIR') or os.path.join(HERE, '_render')
CAB_PX = 40   # TAB-10: altura do cabeçalho (engine.TABELA_CSS, .g2th)
LARGS = [int(x) for x in (os.environ.get('TDC_LARG') or '1440,390').split(',')]
FORA = set(REDIRECIONA) | {'Main.dc.html'}
PAGS = sorted(os.path.basename(f) for f in glob.glob(os.path.join(R, '*.dc.html')) if os.path.basename(f) not in FORA)
EXTRAS = ['PA.dc.html#plano=SOJA-AT', 'PA.dc.html?view=tabela#plano=SOJA-AT', 'AG-07.dc.html#pasteuria-nishizawae-fs', 'SAF.dc.html#saf=S2627&passo=operacoes']
OK, FAIL = [], []
def chk(n, c, info=''):
    (OK if c else FAIL).append(n); print(('OK    ' if c else 'FALHA ') + n + ('' if c else ' · ' + str(info)[:1500]), flush=True)

# ---------- TAB-09: seta de abrir na 1ª coluna ----------
SETA = r"""(()=>{
 const vis=e=>{ if(!e) return false; const r=e.getBoundingClientRect(); if(r.width<=1||r.height<=1) return false; const cs=getComputedStyle(e); return cs.visibility!=='hidden'&&cs.display!=='none'&&parseFloat(cs.opacity)>0.05; };
 const nome=e=>e.tagName.toLowerCase()+(e.className&&typeof e.className==='string'&&e.className.trim()?'.'+e.className.trim().split(/\s+/).slice(0,2).join('.'):'');
 const txt=e=>(e.innerText||e.getAttribute('aria-label')||'').replace(/\s+/g,' ').trim().slice(0,48);
 const ROW='[role=row],tr,[role=listitem],li,[role=treeitem]';
 const out={n:0, ruins:[]};
 // 1) seta só ícone (motor, cartões, peças próprias): nada da mesma linha à esquerda dela
 for(const A of [...document.querySelectorAll('.g2car,.g2drill,.g2cd-nk')].filter(vis)){
   out.n++; const a=A.getBoundingClientRect(), cy=a.top+a.height/2;
   let row=A.closest(ROW); if(!row){ row=A.parentElement; while(row&&row.parentElement&&row.getBoundingClientRect().width<200) row=row.parentElement; }
   const esq=[]; const dentro=el=>el.closest(ROW)===row||!A.closest(ROW);
   const tw=document.createTreeWalker(row,NodeFilter.SHOW_TEXT); let t;
   while(t=tw.nextNode()){ if(!/\S/.test(t.textContent)) continue; const el=t.parentElement; if(!el||A.contains(el)||!vis(el)||!dentro(el)) continue;
     const rg=document.createRange(); rg.selectNodeContents(t); for(const r of rg.getClientRects()){ if(r.width>0&&r.top<cy&&r.bottom>cy&&r.right<=a.left+1){ esq.push(t.textContent.trim().slice(0,16)); break; } } }
   row.querySelectorAll('input,select,textarea,img,svg,button').forEach(el=>{ if(A.contains(el)||el.contains(A)||(el.tagName==='svg'&&el.closest('button')&&!el.closest('button').contains(A)&&el.closest('button')!==el)||!vis(el)||!dentro(el)) return;
     const r=el.getBoundingClientRect(); if(r.top<cy&&r.bottom>cy&&r.right<=a.left+1) esq.push('<'+(el.type==='checkbox'?'checkbox':el.tagName.toLowerCase())+'>'); });
   if(esq.length) out.ruins.push({k:'linha', seta:nome(A), linha:txt(row), esq:[...new Set(esq)].slice(0,3)}); }
 // 2) seta de seção ou de item que abre ali (botão com aria-expanded, sem lista suspensa): a seta vem antes do nome
 const GL=/[▸▾▴▶▼›]/;
 for(const B of [...document.querySelectorAll('button[aria-expanded]:not([aria-haspopup]):not(.g2car):not(.g2mais):not(.g2xtog),summary:not(.acoes-mais summary)')].filter(vis)){
   const its=[]; const tw=document.createTreeWalker(B,NodeFilter.SHOW_TEXT); let t, gl=null, antes=false;
   while(t=tw.nextNode()){ const s=t.textContent; if(!/\S/.test(s)||!vis(t.parentElement)) continue; const i=s.search(GL);
     if(i>=0&&gl===null){ if(s.slice(0,i).trim()) antes=true; const rg=document.createRange(); rg.setStart(t,i); rg.setEnd(t,i+1); gl=rg.getBoundingClientRect().left; }
     const rg=document.createRange(); rg.selectNodeContents(t); const r=[...rg.getClientRects()].find(r=>r.width>0); if(r&&!(i>=0&&!s.replace(GL,'').trim())) its.push(r.left); }
   if(gl===null) continue; out.n++;
   if(antes||its.some(x=>x<gl-1)) out.ruins.push({k:'seção', seta:nome(B), linha:txt(B), esq:['texto antes da seta']}); }
 return out; })()"""

# ---------- TAB-10: altura do cabeçalho ----------
CAB = r"""(()=>{
 const vis=e=>{ if(!e) return false; const r=e.getBoundingClientRect(); if(r.width<=1||r.height<=1) return false; const cs=getComputedStyle(e); return cs.visibility!=='hidden'&&cs.display!=='none'; };
 const rows=new Set(); document.querySelectorAll('[role=columnheader],th').forEach(h=>{ if(!vis(h)) return; const r=h.closest('[role=row],tr'); if(r&&vis(r)) rows.add(r); });
 return [...rows].map(r=>{ const t=r.closest('[role=table],table,[role=grid],[role=treegrid]');
   const cortado=[...r.querySelectorAll('.g2hl')].filter(x=>vis(x)&&x.scrollHeight>x.clientHeight+1).map(x=>x.innerText.trim());
   return {h:Math.round(r.getBoundingClientRect().height*10)/10, cortado, g:t?(t.getAttribute('data-g2g')||t.getAttribute('aria-label')||t.className||t.tagName):'',
     lab:[...r.querySelectorAll('[role=columnheader],th')].filter(vis).map(h=>h.innerText.replace(/\s+/g,' ').replace(/ ?[⇅▲▼]/g,'').trim()).filter(Boolean).join(' | ').slice(0,70)}; }); })()"""

ESTADOS = r"""((k)=>{ const vis=e=>!!e&&e.getClientRects().length>0;
 if(k==='expandir'){ const bs=[...document.querySelectorAll('.g2xtog')].filter(b=>vis(b)&&/Expandir/.test(b.innerText)); bs.forEach(b=>b.click()); return bs.length; }
 if(k==='modo'){ const bs=[...document.querySelectorAll('[data-g2md]')].filter(vis).map(g=>g.querySelector('[data-modo][aria-pressed=false]')).filter(Boolean); bs.forEach(b=>b.click()); return bs.length; }
 return 0; })"""

def varre(c, J, BASE, w):
    setas, cabs, n_setas, n_cab, telas_seta, telas_cab, cortes = [], [], 0, 0, set(), set(), set()
    alturas = {}
    for pg in PAGS + EXTRAS:
        c.goto(BASE + pg, 1.0)
        for est in ('inicial', 'expandir', 'modo'):
            if est != 'inicial':
                if not J(f"{ESTADOS}('{est}')"): continue
                time.sleep(.7)
            s = J(SETA) or {'n': 0, 'ruins': []}; n_setas += s['n']
            for x in s['ruins']:
                setas.append((w, pg, est, x['k'], x['seta'], x['linha'], tuple(x['esq']))); telas_seta.add(pg)
            for x in (J(CAB) or []):
                n_cab += 1; alturas.setdefault(x['h'], set()).add(pg)
                for t in x.get('cortado') or []: cortes.add((pg, t))
                if abs(x['h'] - CAB_PX) > 1: cabs.append((w, pg, est, x['g'], x['h'], x['lab'])); telas_cab.add(pg)
        J("localStorage.clear(); localStorage.setItem('safrion.perfilDemo','Ana')")
    return setas, cabs, n_setas, n_cab, telas_seta, telas_cab, alturas, cortes

p, srv = servir(R); c = Chrome(); J = c.js; BASE = f'http://127.0.0.1:{p}/'
try:
    for w in LARGS:
        h, e, t = (900, 1, False) if w > 500 else (844, 2, True)
        c.aparelho(w, h, e, t); c.goto(BASE + 'Main.dc.html', .3); J("localStorage.clear(); localStorage.setItem('safrion.perfilDemo','Ana')")
        setas, cabs, n_setas, n_cab, ts, tc, alt, cortes = varre(c, J, BASE, w)
        dedup = lambda L: list(dict.fromkeys(L))
        print(f'# {w} px · {len(PAGS)} telas + {len(EXTRAS)} estados por endereço · {n_setas} setas e {n_cab} cabeçalhos medidos', flush=True)
        print(f'# {w} px · alturas de cabeçalho: ' + ', '.join(f'{k} px em {len(v)} telas' for k, v in sorted(alt.items())), flush=True)
        print(f'# {w} px · rótulos de cabeçalho com reticências (3ª linha; nome inteiro no aria-label): {len(cortes)} · ' + '; '.join(sorted(f'{p}: {t}' for p, t in cortes))[:900], flush=True)
        for x in dedup(setas)[:40]: print('  seta', x, flush=True)
        for x in dedup(cabs)[:40]: print('  cab ', x, flush=True)
        chk(f'A{w} TAB-09 seta de abrir na 1ª coluna, antes de qualquer outra coluna ({n_setas} setas; telas com desvio: {len(ts)})', n_setas > 500 and not setas, sorted(ts))
        chk(f'B{w} TAB-10 cabeçalho de tabela com {CAB_PX} px ±1 ({n_cab} cabeçalhos; alturas distintas: {len(alt)}; telas com desvio: {len(tc)})', n_cab > 100 and not cabs, sorted(tc))
    errs = J("window.__errs||[]") or []
    chk('C sem erro de JavaScript na última tela', not errs, errs[:4])
finally:
    c.close(); srv.terminate()
print(f'RESULTADO: {len(OK)} ok · {len(FAIL)} falhas' + (' · ' + '; '.join(FAIL) if FAIL else ''))
sys.exit(1 if FAIL else 0)
