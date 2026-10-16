"""EST-1: conflito de validade no mesmo lote, recusa atômica e recuperação no recebimento."""
from est_lib import Est
E=Est(copiar=False)
try:
 for w in [1440,390]:
  E.c.size(w,1000 if w==1440 else 844);E.abrir();E.J('localStorage.clear();sessionStorage.clear()');E.abrir()
  E.mudar("c.lotes['Semente de soja 58 W|S58-0926']={prod:'Semente de soja 58 W',lote:'S58-0926',un:'kg',local:'Câmara fria',validade:'12/2099',fisico:100,reservado:0,quarentena:0};return {msg:'fixture sintética'};")
  E.abrir();E.clk('Conferir NF 4533')
  for campo,valor in [('conf','20000'),('apto','0'),('quar','20000'),('val','01/2000'),('obs','Validade conferida na embalagem sintética')]:E.setv('fx_g_rec_'+campo,valor)
  campos="JSON.stringify([...document.querySelectorAll('aside[role=dialog] input,aside[role=dialog] select,aside[role=dialog] textarea')].map(x=>[x.id,x.value]))"
  antes=E.J('JSON.stringify({...localStorage})');draft=E.J(campos);E.salvar()
  E.ok('validade informada difere' in E.err() and '12/2099' in E.err(),str(w)+': conflito informa validade registrada junto ao campo',E.err())
  E.ok(E.aberto() and E.J(campos)==draft,str(w)+': rascunho preservado')
  E.ok(E.J('JSON.stringify({...localStorage})')==antes,str(w)+': recusa sem movimento/saldo/recibo')
  E.setv('fx_g_rec_lote','EST1-NOVO');E.salvar()
  E.ok(not E.aberto(),str(w)+': código de lote corrigido permite receber em quarentena',E.err())
  E.ok(E.cen("c.lotes['Semente de soja 58 W|EST1-NOVO'].validade==='01/2000'&&c.lotes['Semente de soja 58 W|EST1-NOVO'].quarentena===20000&&c.lotes['Semente de soja 58 W|S58-0926'].fisico===100"),str(w)+': novo lote conserva vencimento/quarentena e anterior intacto')
  E.ok(E.J('document.documentElement.scrollWidth<=innerWidth+1') and not E.erros(),str(w)+': sem overflow/erro JS',E.erros())
finally:ok=E.fim()
raise SystemExit(0 if ok else 1)
