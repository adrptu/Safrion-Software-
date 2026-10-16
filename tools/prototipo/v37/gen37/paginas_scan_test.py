# -*- coding: utf-8 -*-
"""Varredura rápida das páginas (regime do protótipo, AGENTS §3.5: geração e varredura das páginas a cada mudança): cada página do _render
abre sem erro de JS, com a barra lateral recolhida (ícones, sem submenu) quando é tela da equipe, e sem rolagem lateral da página em 1440 e
390 px, e com o conteúdo de cada cartão de bloco dentro da borda (S4). Páginas técnicas e de redirecionamento ficam fora (Main, MA-0x e PM).
Uso: python3 paginas_scan_test.py (lê _render ou RENDER_DIR)."""
import os, sys, json, time, glob
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, servir
from areas.maquinas import REDIRECIONA
R = os.environ.get('RENDER_DIR') or os.path.join(HERE, '_render')
import ui37
# o BEN ficava fora enquanto oculto (v55); publicado (BEN_PUBLICADO=True, BEN-D39, 13/10/2026) é tela da equipe e entra na varredura
FORA = set(REDIRECIONA) | {'Main.dc.html'} | (set() if ui37.BEN_PUBLICADO else {'BEN.dc.html'})
pags = sorted(os.path.basename(f) for f in glob.glob(os.path.join(R, '*.dc.html')) if os.path.basename(f) not in FORA)
p, srv = servir(R); c = Chrome(); J = c.js
ERR, LARG, SUB, CART = [], [], [], []; NCART = 0
# captura de erro instalada antes dos scripts de cada página (window.__err não é preenchido pela página: sem isto a verificação não prova nada)
CAP = ("window.__err='';addEventListener('error',e=>{window.__err+=(e.message||'erro')+' | ';});"
       "addEventListener('unhandledrejection',e=>{window.__err+='promessa: '+String(e.reason&&e.reason.message||e.reason)+' | ';});"
       "(function(){const ce=console.error;console.error=function(){window.__err+='console: '+[...arguments].map(String).join(' ').slice(0,200)+' | ';return ce.apply(this,arguments);};})();")
c.call('Page.addScriptToEvaluateOnNewDocument', {'source': CAP})
try:
    c.aparelho(1440, 900, 1, False); c.goto(f'http://127.0.0.1:{p}/{pags[0]}', .6); J("setTimeout(()=>{ throw new Error('contraprova S0'); },0)"); time.sleep(.3)
    S0 = 'contraprova S0' in (J("window.__err") or '')
    for w, h, e, t in ((1440, 900, 1, False), (390, 844, 2, True)):
        c.aparelho(w, h, e, t)
        for pg in pags:
            c.goto(f'http://127.0.0.1:{p}/{pg}', .9)
            r = json.loads(J("""JSON.stringify({e:String(window.__err||''), lg:document.documentElement.scrollWidth-document.documentElement.clientWidth,
              sub:document.querySelectorAll('nav[aria-label=Menu] .ml-sub, nav[aria-label=Menu] [aria-expanded]').length,
              cs:(()=>{ const v=[...document.querySelectorAll('main div[style*="border-radius: 16px"]')].filter(d=>d.offsetParent&&getComputedStyle(d).overflowY==='visible');
                return {n:v.length, fora:v.filter(d=>d.scrollHeight>d.clientHeight+2).map(d=>d.clientHeight+'/'+d.scrollHeight+' px '+d.textContent.replace(/\\s+/g,' ').trim().slice(0,32))}; })()})""") or '{}')
            if r.get('e'): ERR.append((w, pg, r['e'][:160]))
            if (r.get('lg') or 0) > 0: LARG.append((w, pg, r['lg']))
            if r.get('sub'): SUB.append((w, pg, r['sub']))
            cs = r.get('cs') or {}; NCART += cs.get('n') or 0
            CART += [(w, pg, x) for x in cs.get('fora') or []]
finally:
    c.close(); srv.terminate()
ok = lambda n, x: print(('OK    ' if not x else 'FALHA ') + n + ('' if not x else ' · ' + str(x[:8])), flush=True) or (not x)
r = [ok('S0 a captura de erro funciona (erro provocado é visto)', [] if S0 else ['não capturou']), ok(f'S1 {len(pags)} páginas × 2 tamanhos sem erro de JS (erro, promessa rejeitada e console.error)', ERR), ok('S2 sem rolagem lateral da página', LARG), ok('S3 barra lateral sem submenu nem expandir', SUB),
     # S4 (16/10): o último cartão do section() numa tela longa ficava com 2 px em 1440 × 900 e o texto fora da borda (CO-07, PL-01, VE-01, VE-02).
     # altura/conteúdo em px; sem nenhum cartão medido a verificação não prova nada
     ok(f'S4 cartões de bloco ({NCART} medidos) com o conteúdo dentro da borda', CART if NCART else ['nenhum cartão medido'])]
print(f'RESULTADO: {sum(r)} ok · {len(r)-sum(r)} falhas ({len(pags)} páginas)')
sys.exit(0 if all(r) else 1)
