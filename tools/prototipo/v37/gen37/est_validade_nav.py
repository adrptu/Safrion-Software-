"""EST-1: proteção parcial da tela, antes da correção central; dados sintéticos."""
from est_lib import Est
E=Est(copiar=False)
try:
 for w in [1440,390]:
  E.c.size(w,1000 if w==1440 else 844);E.abrir();E.J("localStorage.clear();sessionStorage.clear()");E.abrir()
  E.mudar("return cenLiberar(c,'OS-0430');")
  rid=E.cen("c.ordens['OS-0430'].req");prod=E.cen("c.reqs[c.ordens['OS-0430'].req].itens[0].prod")
  E.mudar("const r=c.reqs[c.ordens['OS-0430'].req],i=r.itens[0];c.lotes[i.prod+'|'+i.lote].validade='01/2000';return {msg:'precondição sintética'};")
  E.J("localStorage.setItem('safrion.perfilDemo','Rui')");E.abrir();E.etapa(2)
  linha=E.rowtxt(rid,prod);E.ok('Bloqueada' in linha and 'vencido' in linha,str(w)+': linha mostra bloqueio por validade',linha)
  antes=E.J("JSON.stringify({...localStorage})");E.row(rid,prod)
  E.ok('Revise a reserva' in E.aside(),str(w)+': detalhe nomeia recuperação',E.aside())
  E.ok(E.J("[...document.querySelectorAll('aside[role=dialog] input,aside[role=dialog] select')].filter(x=>!x.readOnly&&!x.disabled).length")==0,str(w)+': consulta não oferece quantidade para entregar')
  E.ok(antes==E.J("JSON.stringify({...localStorage})"),str(w)+': abrir consulta preserva estado')
  E.ok(E.J("document.documentElement.scrollWidth<=innerWidth+1") and not E.J('window.__errs.length'),str(w)+': sem overflow ou erroJS')
finally: ok=E.fim()
raise SystemExit(0 if ok else 1)
