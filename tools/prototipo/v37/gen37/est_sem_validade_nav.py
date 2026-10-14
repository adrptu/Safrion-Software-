import json
from est_lib import Est
from areas import processo_estoque as PE
p=next(p for p in PE._pedidos() if p['grupo'] in PE.SEM_VALIDADE)
E=Est(copiar=False)
try:
 for w in [1440,390]:
  E.c.size(w,900 if w==1440 else 844);E.abrir();E.J('localStorage.clear();sessionStorage.clear()');E.abrir()
  l={'prod':p['item'],'lote':'EST1-FERT','un':p['un'],'local':'Galpão 2','validade':'—','fisico':100,'reservado':0,'quarentena':0};key=p['item']+'|EST1-FERT'
  E.mudar('c.lotes['+json.dumps(key)+']='+json.dumps(l)+';return {msg:"fixture"};');E.abrir();E.clk('Conferir NF 4533')
  E.setv('fx_g_rec_val','12/2099');E.setv('fx_g_rec_ped',PE._ped_label(p))
  for k,v in [('nf','NF 99996'),('qtd_nf','5'),('conf','5'),('apto','5'),('quar','0'),('lote','EST1-FERT')]:E.setv('fx_g_rec_'+k,v)
  E.ok(E.val('fx_g_rec_val')=='Sem validade',str(w)+': data anterior fica oculta pelo campo sem validade')
  E.salvar();E.ok(not E.aberto(),str(w)+': troca de pedido permite recebimento válido',E.err())
  E.ok(E.cen('c.lotes['+json.dumps(key)+'].fisico===105&&c.lotes['+json.dumps(key)+'].validade==="—"'),str(w)+': soma5 preservando ausência de validade')
  E.ok(not E.erros(),str(w)+': sem erro JS',E.erros())
finally:ok=E.fim()
raise SystemExit(0 if ok else 1)
