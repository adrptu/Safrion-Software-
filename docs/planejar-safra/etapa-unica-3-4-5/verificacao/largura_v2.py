# Mede, no grid G2 real (g_res da etapa 5 "Por mês", CSS de 884620c), a largura da g_cap em 3 variantes. Não edita o repositório.
import sys, os, json, time
os.environ['CHROME_BIN']='/tmp/claude-0/-home-user-Safrion-Software-/65558514-68d9-57f5-9da3-513cd6735cdc/scratchpad/rev345p10/chrome.sh'
HERE='/home/user/sp-tab5/tools/prototipo/v37/gen37'; sys.path.insert(0, HERE)
from comp_lib import Chrome, servir
p, srv = servir(os.path.join(HERE, '_render')); c = Chrome(); J = c.js
MES=['set/26','out/26','nov/26','dez/26','jan/27','fev/27','mar/27','abr/27','mai/27','jun/27','jul/27','ago/27']
NOM=['Tratores','Pulverizadores','Plantadeiras','Distribuidores','Colhedoras','Operadores e equipe']
UN=['4 unidades','1 unidade','1 unidade','1 unidade','1 unidade','8 pessoas']
# §2.1 da especificação (S2627)
OC=[['2 %','9 %','8 %','7 %','<1 %','27 %','(6 %)','(4 %)','(<1 %)','<1 %','15 %','—'],
    ['10 %','5 %','17 %','26 %','<1 %','—','(11 %)','(10 %)','(2 %)','—','(2 %)','—'],
    ['—','32 %','—','—','—','(39 %)','—','(7 %)','—','—','—','—'],
    ['—','1 %','16 %','1 %','—','—','(12 %)','—','—','<1 %','—','—'],
    ['—','—','—','—','—','81 %','—','—','—','—','(56 %)','—'],
    ['1 %','12 %','5 %','4 %','<1 %','31 %','(3 %)','(3 %)','42 %','<1 %','15 %','—']]
MU=['27 %','26 %','32 %','16 %','81 %','42 %']; MM=['fev/27','dez/26','out/26','nov/26','fev/27','mai/27']
HS=['367 h','117 h','63 h','40 h','122 h','1.242 h']
PICO=['17 % · fev/27','26 % · dez/26','32 % · out/26','16 % · nov/26','81 % · fev/27','42 % · mai/27']
def variante(v):
    if v=='v2': H=['Recurso (ocupação no mês)','Maior uso','Mês']+MES; R=[[NOM[i],MU[i],MM[i]]+OC[i] for i in range(6)]
    elif v=='spec': H=['Recurso (ocupação)','Unidades']+MES+['Horas na safra']; R=[[NOM[i],UN[i]]+OC[i]+[HS[i]] for i in range(6)]
    elif v=='p10': H=['Recurso (ocupação)','Pico','Unidades']+MES; R=[[NOM[i],PICO[i],UN[i]]+OC[i] for i in range(6)]
    else: H=['Recurso (ocupação)','Unidades']+MES; R=[[NOM[i],UN[i]]+OC[i] for i in range(6)]
    return H,R
INJ=r"""((H,R)=>{const m=document.querySelector('main'); const x=[...m.querySelectorAll('.g2caixa')].filter(e=>e.offsetParent)[0]; const rola=x.querySelector('.g2rola'); const t=rola.firstElementChild;
 const rows=[...t.querySelectorAll(':scope > [role=row]')]; const h0=rows[0]; const top=rows.filter(r=>/^R_[a-z]+$/.test(r.getAttribute('data-rid')||''));
 rows.forEach(r=>{ if(r!==h0 && !top.includes(r)) r.remove(); }); while(top.length<R.length){ const n=top[top.length-1].cloneNode(true); t.appendChild(n); top.push(n); }
 t.style.setProperty('--g2cols','repeat('+H.length+', auto)'); t.style.gridTemplateColumns='repeat('+H.length+', auto)';
 const hc=[...h0.children]; const hT0=hc[0], hT=hc[1]; h0.innerHTML='';
 H.forEach((s,j)=>{const d=(j===0?hT0:hT).cloneNode(true); d.querySelector('.sc-interp').textContent=s; h0.appendChild(d);});
 top.forEach((r,i)=>{const cs=[...r.children]; const c0=cs[0].cloneNode(true), cn=cs[1].cloneNode(true); const car=c0.querySelector('.g2car'); if(car) car.remove();
   const sub=c0.querySelector('.g2pw span[style]'); if(sub) sub.remove(); r.innerHTML='';
   R[i].forEach((s,j)=>{const d=(j===0?c0:cn).cloneNode(true); const sp=d.querySelector('.sc-interp'); sp.textContent=s; const st=sp.parentElement; if(j>0){st.style.color=(s==='—'?'#65736A':'#15201A'); st.style.fontWeight='400';} r.appendChild(d);}); });
 return true;})(%s,%s)"""
M=r"""(()=>{const m=document.querySelector('main'); const x=[...m.querySelectorAll('.g2caixa')].filter(e=>e.offsetParent)[0]; const rola=x.querySelector('.g2rola');
 const hs=[...x.querySelectorAll('[role=columnheader]')]; const W=hs.map(h=>Math.round(h.getBoundingClientRect().width)); const rb=rola.getBoundingClientRect();
 const c0=hs[0].getBoundingClientRect().right; const sw0=[...x.querySelectorAll('[role=row]')].map(r=>r.children[0]).map(e=>Math.round(e.scrollWidth)); const inteiras=hs.slice(1).filter(h=>{const q=h.getBoundingClientRect(); return q.left>=c0-1 && q.right<=rb.right+1;}).map(h=>h.innerText.trim());
 return {cw:rola.clientWidth, sw:rola.scrollWidth, rolaH:rola.scrollWidth>rola.clientWidth+1, larguras:W, colunasInteirasSemRolar:inteiras, nlinhas:x.querySelectorAll('[role=row]').length-1};})()"""
out={}
try:
    for (w,h,mob) in ((1440,1040,False),(1366,768,False),(1280,800,False),(390,844,True),(360,800,True)):
        for v in ('v2',):
            c.aparelho(w,h,2 if mob else 1,mob)
            c.goto(f'http://127.0.0.1:{p}/Main.dc.html', .3); J("localStorage.clear(); sessionStorage.clear()")
            c.goto(f'http://127.0.0.1:{p}/SAF.dc.html#saf=S2627&etapa=5', 1.8)
            J("(()=>{const b=[...document.querySelectorAll('main button')].find(x=>x.innerText.trim()==='Por mês'); if(b) b.click();})()"); time.sleep(.8)
            H,R=variante(v); J(INJ%(json.dumps(H,ensure_ascii=False),json.dumps(R,ensure_ascii=False))); time.sleep(.4)
            r=J(M); k=f'{w}x{h} {v}'; out[k]=r; print(k, json.dumps(r,ensure_ascii=False))
            c.shot(f'shots/gcap-{w}-{v}.png')
finally:
    c.close(); srv.terminate()

