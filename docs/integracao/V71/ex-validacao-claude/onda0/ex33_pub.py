import json,time
from o0lib import S,clicaT,VIS
s=S()
try:
  for pg,b in [('PL-06.dc.html','Publicar parcelamento e plano'),('PL-02.dc.html','Publicar plano v4'),('PL-02det.dc.html','Publicar ajuste do T1-A'),('GE-02.dc.html','Publicar previsão V2')]:
    s.reset('Caio'); s.ir(pg,1.6)
    st0=s.J("(document.querySelector('header')||{}).innerText.replace(/\\s+/g,' ').slice(0,200)")
    print('\n==',pg,'(Caio) cabeçalho antes:',st0)
    print('  clica:',clicaT(s,b)); print('  toast:',s.toast())
    print('  Desfazer visível?', s.J("[...document.querySelectorAll('button,a')].some(e=>e.getClientRects().length&&/Desfazer/i.test(e.innerText))"))
    print('  cabeçalho depois:',s.J("(document.querySelector('header')||{}).innerText.replace(/\\s+/g,' ').slice(0,200)"))
    s.shot('ex33_pub_'+pg.split('.')[0])
finally: s.fim()
