import json,time
from o0lib import S,clicaT
s=S()
try:
  s.reset('Caio'); s.ir('GE-02.dc.html',1.8); print('== GE-02 (Caio)')
  print('  ⋯:',clicaT(s,'Mais ações de Publicação')); time.sleep(.4)
  print('  itens:',[b for b in s.botoes() if 'Publicar' in b or 'Submeter' in b or 'Autorizar' in b])
  print('  publicar:',clicaT(s,'Publicar previsão V2')); print('  toast:',s.toast())
  print('  Desfazer?', s.J("[...document.querySelectorAll('button,a')].some(e=>e.getClientRects().length&&/Desfazer/i.test(e.innerText))")); s.shot('ex33_pub_GE-02_v2')
  s.reset('Caio'); s.ir('PL-03.dc.html',1.8); print('== PL-03 (Caio)')
  print('  publicar cenário:',clicaT(s,'Publicar cenário 2º turno')); print('  toast:',s.toast())
  print('  Desfazer?', s.J("[...document.querySelectorAll('button,a')].some(e=>e.getClientRects().length&&/Desfazer/i.test(e.innerText))")); s.shot('ex33_pub_PL-03_cenario')
finally: s.fim()
