"""EST-2: erro, preservação de rascunho e recuperação no recebimento; dados sintéticos."""
from est_lib import Est
E=Est(copiar=False)
try:
 for largura in [1440,390]:
  E.c.size(largura,1000 if largura==1440 else 844);E.abrir();E.J("localStorage.clear();sessionStorage.clear()");E.abrir()
  E.clk('Conferir NF 4533')
  for campo,valor in [('conf','20000'),('apto','20000'),('quar','0'),('val','05/2027'),('div','Item diferente do pedido'),('obs','Produto diferente do comprado')]: E.setv('fx_g_rec_'+campo,valor)
  antes=E.J("JSON.stringify({...localStorage})")
  campos="JSON.stringify([...document.querySelectorAll('aside[role=dialog] input,aside[role=dialog] select,aside[role=dialog] textarea')].map(x=>[x.id,x.value]))"
  draft=E.J(campos);E.salvar()
  E.ok('não confirme como o produto comprado' in E.err(),str(largura)+': motivo e recuperação junto ao formulário',E.err())
  E.ok(E.aberto() and E.J(campos)==draft,str(largura)+': preenchimento preservado')
  E.ok(E.J("JSON.stringify({...localStorage})")==antes,str(largura)+': nenhum saldo/movimento/recibo gravado')
  E.ok(E.J("document.documentElement.scrollWidth<=innerWidth+1"),str(largura)+': página sem excesso horizontal')
  E.setv('fx_g_rec_div','Sem divergência');E.salvar()
  E.ok(not E.aberto() and 'Conferido' in E.rowtxt('NF 4533'),str(largura)+': item conferido corretamente recupera fluxo',E.toast())
  E.ok(not E.J('window.__errs.length'),str(largura)+': sem erro JS')
finally: ok=E.fim()
raise SystemExit(0 if ok else 1)
