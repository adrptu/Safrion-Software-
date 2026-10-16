# Cenários de comando (perfil isolado, localStorage do Chrome temporário): liberar OS-0501, entregar fração e acima, embalagem
from base import *
SETV = """((sel,val)=>{const i=document.querySelector(sel); if(!i) return 'NAO ACHEI'; const P=i.tagName==='SELECT'?HTMLSelectElement.prototype:HTMLInputElement.prototype; Object.getOwnPropertyDescriptor(P,'value').set.call(i,val); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true})); return 'ok';})"""
CLK = """((t)=>{const n=s=>(s||'').replace(/\\s+/g,' ').trim(); const b=[...document.querySelectorAll('aside[role=dialog] button')].find(x=>n(x.innerText)===t&&x.getAttribute('aria-disabled')!=='true'); if(!b) return 'NAO ACHEI '+t; b.click(); return 'ok';})"""
def cen(s, expr): return s.J(f"(()=>{{const X=window.__cen; const c=X.cenGet(); return ({expr});}})()")
def mudar(s, body): return s.J(f"(()=>{{const X=window.__cen; with(X){{ try{{ const r=cenMudar(null,c=>{{{body}}}); return r.erro||r.msg||JSON.stringify(r); }}catch(e){{return 'ERRO: '+e.message;}} }} }})()")
s = S()
try:
    s.reset('Ana'); s.go('OS.dc.html', 1.5)
    s.J(f"({SETV})('select[aria-label=\"Filtrar por fazenda\"]','Lagoa Grande')"); time.sleep(.6)
    s.J("(()=>{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>/OS-0501/.test(r.innerText)); r&&r.click();})()"); time.sleep(.6)
    print('1 liberar:', s.J(f"({CLK})('Liberar para execução')")); time.sleep(.5)
    for t in ['Confirmar liberação', 'Liberar', 'Confirmar']:
        r = s.J(f"({CLK})({json.dumps(t)})"); print('  conf', t, r); time.sleep(.5)
        if r == 'ok': break
    print('  toast:', s.J("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).filter(Boolean).join(' | ')"))
    rid = cen(s, "c.ordens['OS-0501'].req"); print('  etapa', cen(s, "c.ordens['OS-0501'].etapa"), 'req', rid)
    print('  itens', cen(s, f"JSON.stringify(c.reqs[{json.dumps(rid)}]&&c.reqs[{json.dumps(rid)}].itens.map(i=>[i.prod,i.solicitado,i.un,i.emb]))"))
    s.perfil('Rui'); s.go('OS.dc.html', 1.2)
    print('2 entregar 150 L (acima):', mudar(s, f"return cenEntregar(c,{json.dumps(rid)},'Glifosato 480',150,'Wesley','Rui','k-ex38-a');"))
    print('3 entregar 147,93 L (fração de galão 20 L):', mudar(s, f"return cenEntregar(c,{json.dumps(rid)},'Glifosato 480',147.93,'Wesley','Rui','k-ex38-b');"))
    print('4 adjuvante da OS-0421 pela REQ-035:', mudar(s, "return cenEntregar(c,'REQ-035','Adjuvante espalhante',10,'Marcos','Rui','k-ex38-c');"))
    print('5 lotes Adjuvante:', cen(s, "JSON.stringify(Object.values(c.lotes).filter(l=>/Adjuvante|Óleo/.test(l.prod)).map(l=>[l.prod,l.lote,l.fisico,l.reservado]))"))
    print('6 REQ-031:', cen(s, "JSON.stringify(c.reqs['REQ-031'].itens.map(i=>[i.prod,i.solicitado,i.entregue,i.consumido,i.custodia,i.devolvido]))"), 'tot OS-0417', cen(s, "JSON.stringify(c.ordens['OS-0417'].ins)"))
    print('7 REQ-022/025/023/024:', cen(s, "JSON.stringify(['REQ-022','REQ-025','REQ-023','REQ-024'].map(r=>c.reqs[r].itens.map(i=>[r,i.prod,i.entregue,i.un,i.emb])))"))
    print('8 movimentos de adjuvante:', cen(s, "JSON.stringify((c.movs||[]).filter(m=>/Adjuvante/.test(m.prod||'')))"))
    print('ERRS', s.J("window.__errs"))
finally:
    s.fim()
