# Simulação de layout da v2 (não é a tela implementada): sobre o _render de 884620c, etapa 4 atual (g_op real), troca o topo do bloco pelo
# topo da v2 — veredito (role=status) + linha de capacidade (Maior uso / faltas, "Capacidade por mês ▾", custo de operação, "Resumo da safra")
# — sem faixa de indicadores; g_cap recolhida (padrão) ou aberta (clone da g_res real com 6 linhas). Conta as linhas da g_op acima da área de ações.
import sys, os, json, time
HERE='/home/user/sp-tab5/tools/prototipo/v37/gen37'; sys.path.insert(0, HERE)
os.environ['CHROME_BIN']='/tmp/claude-0/-home-user-Safrion-Software-/65558514-68d9-57f5-9da3-513cd6735cdc/scratchpad/rev345p10/chrome.sh'
from comp_lib import Chrome, servir
p, srv = servir(os.path.join(HERE, '_render')); c = Chrome(); J = c.js
OUT=os.path.dirname(os.path.abspath(__file__))+'/shots'
PEGA=r"""(()=>{const cx=[...document.querySelectorAll('main .g2caixa')].filter(e=>e.offsetParent).pop(); return cx.outerHTML;})()"""
VER={'S2627':('#5B4300','● Na estimativa mensal, cabe nos 690 ha com plano. Prazo por talhão não verificado: 17 de 17 atividades sem janela. Fora da conta: T4, T3, P1 e P2 (475 ha), sem plano.',
   '<button type="button" class="acoes-lnk">Maior uso: Colhedoras 81 % · fev/27</button>','Custo de operação R$ 264.617,07 · máquinas e pessoas, sem insumos',True),
 'LG2627':('#B42318','● Falta recurso: Operadores e equipe precisam de 127 em nov/26 e você tem 8 (9 meses); Tratores, 10 em out/26 e você tem 4 (4 meses). Inclui 56 ocorrências ainda sem alocação. Fora da conta: 75 ocorrências antes do início da safra (01/09/2026).',
   '<button type="button" class="acoes-lnk">Operadores e equipe 1.584 % · nov/26</button> <button type="button" class="acoes-lnk">Tratores 234 % · out/26</button>','Custo de operação R$ 1.533.499,13 · inclui R$ 919.906,51 de antes de 01/09/2026',False)}
MONTA=r"""((html,V,aberta)=>{const m=document.querySelector('main'); const sec=m.querySelector('section'); const corpo=sec.querySelector('.g2caixa').parentElement; const gop=corpo.querySelector('.g2caixa');
 const h3=sec.querySelector('h3'); h3.textContent='Operações e recursos'; const sub=h3.nextElementSibling;
 sub.innerHTML='<span role="status" style="color:'+V[0]+';font-weight:700">'+V[1]+'</span> '+V[2]+' <button type="button" class="g2xtog" aria-expanded="'+(aberta?'true':'false')+'">Capacidade por mês '+(aberta?'▴':'▾')+'</button>';
 const tog=h3.parentElement.nextElementSibling; if(tog){ tog.innerHTML='<span style="font-size:13px;color:#65736A">'+V[3]+'</span> <button type="button" class="acoes-lnk">Resumo da safra</button>'; }
 if(aberta){ const t=document.createElement('div'); t.innerHTML=html; const cap=t.firstElementChild; const barra=cap.firstElementChild; if(!barra.classList.contains('g2rola')) barra.remove();
   const rows=[...cap.querySelectorAll('[role=row]')]; const ult=rows[rows.length-1]; ult.parentElement.appendChild(ult.cloneNode(true)); cap.style.marginBottom='10px'; corpo.insertBefore(cap,gop); }
 const ac=m.querySelector('.acoes'); if(V[4]){ const n=document.createElement('p'); n.className='acoes-nota'; n.innerHTML='<button class="acoes-lnk">Aplicar plano em 4 cultivos</button>'; ac.insertBefore(n,ac.firstChild); }
 return true;})"""
M=r"""(()=>{const m=document.querySelector('main'); const cx=[...m.querySelectorAll('.g2caixa')].pop(); const rola=cx.querySelector('.g2rola'); const rb=rola.getBoundingClientRect();
 const ac=m.querySelector('.acoes').getBoundingClientRect(); const lim=Math.min(rb.bottom,ac.top)+1;
 const rows=[...rola.querySelectorAll('[role=row]')].filter(e=>e.offsetParent); const vis=rows.slice(1).filter(r=>r.getBoundingClientRect().bottom<=lim);
 const tot=rows[rows.length-1]; const st=m.querySelector('[role=status]').getBoundingClientRect();
 return {linhas:vis.length, de:rows.length-1, total:vis.includes(tot), rolaH:Math.round(rb.height), veredito:[Math.round(st.height)], main:[m.scrollHeight,m.clientHeight]};})()"""
VP=[(1440,1040),(1366,768),(1280,800),(1440,789),(1366,657),(1280,689)]
try:
    c.aparelho(1440,1040,1,False); c.goto(f'http://127.0.0.1:{p}/Main.dc.html', .3); J("localStorage.clear(); sessionStorage.clear()")
    c.goto(f'http://127.0.0.1:{p}/SAF.dc.html#saf=S2627&etapa=5', 1.8); html=J(PEGA)
    for (w,h) in VP:
        c.aparelho(w,h,1,False)
        for saf in ('S2627','LG2627'):
            for aberta in (False,True):
                c.goto(f'http://127.0.0.1:{p}/Main.dc.html', .2); c.goto(f'http://127.0.0.1:{p}/SAF.dc.html#saf={saf}&etapa=4', 1.6)
                J(MONTA+'('+json.dumps(html)+','+json.dumps(VER[saf],ensure_ascii=False)+','+('true' if aberta else 'false')+')'); time.sleep(.4)
                r=J(M); print(f"{w}x{h} {saf} g_cap {'aberta ' if aberta else 'recolhida'} | g_op {r['linhas']}/{r['de']} Total {'sim' if r['total'] else 'não'} | dados {r['rolaH']} px | veredito {r['veredito'][0]} px | main {r['main']}")
                if (w,h) in ((1280,800),(1440,1040)): c.shot(f"{OUT}/v2c-{w}x{h}-{saf}-{'aberta' if aberta else 'recolhida'}.png")
finally:
    c.close(); srv.terminate()
