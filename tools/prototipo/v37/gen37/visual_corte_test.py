# -*- coding: utf-8 -*-
"""Varredura visual de cortes e sobreposições (pedido do proprietário, 13/10/2026: "corrija em todo o sistema esses bugs visuais /
componentes visuais cortados"). Abre cada página do _render em 1440 × 900, 1024 × 640 e 390 × 844 (e as visões por endereço
listadas em EXTRA) e mede, no navegador:
  C1 conteúdo que sai da célula da grade (selo, texto ou botão além da borda da célula: invade a coluna vizinha);
  C2 texto cortado sem aviso (elemento com overflow escondido, conteúdo maior que a caixa e sem reticências);
  C3 barra de ações presa embaixo (.acoes / .acoes-form) flutuando no meio da tela, com conteúdo da mesma rolagem visível abaixo;
  C4 linha que começa com o separador "·" (resto de uma quebra de linha: "· Trator MF 7719").
  R (informativo, não conta) texto longo cortado de propósito com reticências dentro da célula (CADX, linha de uma altura).
Saída: uma linha por achado e o total por regra; sai 1 se houver achado. Uso: python3 visual_corte_test.py [prefixo das páginas]."""
import sys, os, json, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, servir
R = os.environ.get('RENDER_DIR') or os.path.join(HERE, '_render')
FILTRO = sys.argv[1] if len(sys.argv) > 1 else ''
PAGS = sorted(f for f in os.listdir(R) if f.endswith('.dc.html') and f.startswith(FILTRO))
EXTRA = ['MA.dc.html#vis=ordens', 'MA.dc.html#vis=ativos', 'MA.dc.html#vis=planos', 'PA.dc.html#plano=SOJA-AT', 'SAF.dc.html#saf=S2627&passo=cultivos',
         'SAF.dc.html#saf=S2627&passo=operacoes', 'SAF.dc.html#saf=S2627&passo=demanda']
TAMS = [(1440, 900), (1024, 640), (390, 844)]
MEDE = r"""(()=>{ const out=[]; const vis=e=>{ const r=e.getBoundingClientRect(); return r.width>0&&r.height>0; };
  const nome=e=>(e.innerText||e.textContent||'').replace(/\s+/g,' ').trim().slice(0,60);
  // C1 · conteúdo além da célula (só os filhos diretos visíveis e os selos)
  document.querySelectorAll('[role=cell]').forEach(c=>{ if(!vis(c)) return; const cr=c.getBoundingClientRect(); if(cr.width<8) return;
    const es=[...c.querySelectorAll('span,a,button,b,strong,em,div')].filter(vis);
    for(const e of es){ const r=e.getBoundingClientRect(); if(r.right>cr.right+2||r.left<cr.left-2){
      // R (informativo): texto longo cortado de propósito com reticências por um bloco dentro da célula (CADX: linha de uma altura)
      let a=e.parentElement, ret=false; while(a&&a!==c){ const s=getComputedStyle(a); if(s.textOverflow==='ellipsis'&&s.overflowX!=='visible'){ ret=true; break; } a=a.parentElement; }
      out.push([ret?'R':'C1',nome(e)||nome(c),Math.round(r.right-cr.right)]); break; } } });
  // C2 · texto cortado sem reticências
  document.querySelectorAll('body *').forEach(e=>{ if(!vis(e)||!e.children) return; const s=getComputedStyle(e); const rr=e.getBoundingClientRect();
    if(rr.width<=2||rr.height<=2||s.clip!=='auto'&&s.clip!==''||s.clipPath!=='none'||e.closest('.g2sr,.sr-only,.ma-sr,[class*=sr]')) return;   /* texto só para leitor de tela (invisível de propósito) */
    if((s.overflowX==='hidden'||s.overflowX==='clip')&&s.textOverflow!=='ellipsis'&&e.scrollWidth>e.clientWidth+2&&e.children.length===0&&(e.innerText||'').trim()) out.push(['C2',nome(e),e.scrollWidth-e.clientWidth]); });
  // C3 · barra presa embaixo flutuando: há conteúdo da página visível abaixo dela, dentro da janela
  document.querySelectorAll('.acoes,.acoes-form').forEach(b=>{ if(!vis(b)) return; const r=b.getBoundingClientRect(); if(r.bottom>=innerHeight-2) return;
    const y=Math.min(innerHeight-4,r.bottom+14); const xs=[r.left+20,(r.left+r.right)/2,r.right-20];
    const debaixo=xs.map(x=>document.elementFromPoint(x,y)).filter(el=>el&&!b.contains(el)&&el!==document.body&&el!==document.documentElement&&(el.innerText||'').trim()&&getComputedStyle(b).position==='sticky');
    if(debaixo.length&&r.bottom<innerHeight-30) out.push(['C3',nome(b).slice(0,40),Math.round(innerHeight-r.bottom)]); });
  // C4 · linha que começa com "·"
  // começa a linha = nada visível à esquerda na mesma linha, subindo pelos irmãos até o bloco que contém (item flexível ao lado do título não conta;
  // texto só para leitor de tela também não)
  const naLinha=(x,rr)=>{ while(x&&x!==document.body){ for(let s=x.previousSibling;s;s=s.previousSibling){ const g=document.createRange(); g.selectNodeContents(s);
        if([...g.getClientRects()].some(q=>q.width>0&&q.height>0&&q.bottom>rr.top+2&&q.top<rr.bottom-2&&q.right<=rr.left+2)) return false; }
      const pe=x.parentElement; if(!pe) break; if(['block','list-item','table-cell','grid','flow-root','flex','inline-flex'].includes(getComputedStyle(pe).display)) return true; x=pe; } return true; };
  const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT); let n; while((n=w.nextNode())){ const t=n.textContent; if(!/^\s*·\s/.test(t)) continue; const p=n.parentElement; if(!p||!vis(p)) continue;
    if(p.closest('.etp-sr,.g2sr,.sr-only,.ma-sr')||getComputedStyle(p).opacity==='0') continue;   // escondido no começo da linha (g2sepIni)
    const i0=t.indexOf('·'); const g=document.createRange(); g.setStart(n,i0); g.setEnd(n,i0+1); const rr=g.getBoundingClientRect(); if(!(rr.width>1&&rr.height>1)) continue;
    if(naLinha(n,rr)) out.push(['C4',t.trim().slice(0,50),0]); }
  return out; })()"""
ROLA = "(()=>{ const m=document.querySelector('main[data-scroll]')||document.scrollingElement; const H=m.scrollHeight; return H; })()"
def rola_para(c, f):
    c.js("(()=>{ const m=document.querySelector('main[data-scroll]')||document.scrollingElement; m.scrollTop=Math.round((m.scrollHeight-m.clientHeight)*%s); window.scrollTo(0,Math.round((document.documentElement.scrollHeight-innerHeight)*%s)); })()" % (f, f))
achados = {}; total = 0
p, srv = servir(R); c = Chrome()
try:
    for pg in PAGS + [x for x in EXTRA if x.startswith(FILTRO)]:
        for (w, h) in TAMS:
            c.aparelho(w, h, 1, w < 600); c.goto(f'http://127.0.0.1:{p}/{pg}', espera=.9)
            vistos = set()
            for f in (0, .5, 1):
                rola_para(c, f); time.sleep(.25)
                for regra, txt, d in (c.js(MEDE) or []):
                    k = (regra, txt)
                    if k in vistos: continue
                    vistos.add(k); achados.setdefault(regra, []).append((pg, w, txt, d)); total += regra != 'R'
                    print(f'{regra} | {pg} | {w}px | {txt} | {d}', flush=True)
finally:
    c.close(); srv.terminate()
for k in sorted(achados): print(f'TOTAL {k}: {len(achados[k])}' + (' (informativo: reticências de propósito, não conta)' if k == 'R' else ''))
print(f'RESULTADO: {total} achado(s) em {len(PAGS)} páginas + {len(EXTRA)} visões × {len(TAMS)} tamanhos')
sys.exit(1 if total else 0)
