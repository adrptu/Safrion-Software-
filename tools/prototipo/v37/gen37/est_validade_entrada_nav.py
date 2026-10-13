"""EST-1: devolução vencida, recuperação em quarentena, desktop e celular sintéticos."""
from est_lib import Est
E=Est(copiar=False)
try:
 for w in [1440,390]:
  E.c.size(w,1000 if w==1440 else 844);E.abrir();E.J("localStorage.clear();sessionStorage.clear()");E.abrir()
  E.mudar("return cenLiberar(c,'OS-0430');")
  rid=E.cen("c.ordens['OS-0430'].req");prod=E.cen("c.reqs[c.ordens['OS-0430'].req].itens[0].prod")
  E.mudar("const r=c.reqs[c.ordens['OS-0430'].req],i=r.itens[0];return cenEntregar(c,r.id,i.prod,2,'Marcos','Rui','ENTRADA-NAV');")
  E.mudar("const r=c.reqs[c.ordens['OS-0430'].req],i=r.itens[0];c.lotes[i.prod+'|'+i.lote].validade='01/2000';return {msg:'precondição sintética'};")
  E.J("localStorage.setItem('safrion.perfilDemo','Rui')");E.abrir();E.etapa(3);E.row(rid,prod)
  E.setv('fx_g_dev_qtd','1');E.setv('fx_g_dev_cond','Apta · volta ao disponível');E.setv('fx_g_dev_obs','Lote vencido')
  campos="JSON.stringify([...document.querySelectorAll('aside[role=dialog] input,aside[role=dialog] select,aside[role=dialog] textarea')].map(x=>[x.id,x.value]))"
  antes=E.J("JSON.stringify({...localStorage})");draft=E.J(campos);E.salvar()
  E.ok('vencido' in E.err() and 'quarentena' in E.err(),str(w)+': erro mostra validade e recuperação',E.err())
  E.ok(E.aberto() and E.J(campos)==draft,str(w)+': rascunho preservado')
  E.ok(antes==E.J("JSON.stringify({...localStorage})"),str(w)+': recusa sem alterar estado')
  E.setv('fx_g_dev_cond','Bloqueada para inspeção · vai para quarentena');E.salvar()
  E.ok(not E.aberto(),str(w)+': correção em quarentena conclui devolução',E.err())
  E.ok(E.cen("c.reqs[c.ordens['OS-0430'].req].itens[0].custodia")==1,str(w)+': custódia baixada uma vez')
  E.ok(E.J("document.documentElement.scrollWidth<=innerWidth+1") and not E.J('window.__errs.length'),str(w)+': sem overflow/erro JS')
finally: ok=E.fim()
raise SystemExit(0 if ok else 1)
