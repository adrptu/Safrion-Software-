import json,time
from o0lib import S,cen,clicaT,preenche
s=S()
def passo(perf,pag,acoes,nome,espera=1.6,depois=None):
    s.reset(perf); s.ir(pag,espera); print('\n=====',nome,'·',pag,'· perfil',perf)
    for a in acoes:
        if isinstance(a,tuple) and a[0]=='fill': print('  preenche',preenche(s,a[1])); continue
        if isinstance(a,tuple) and a[0]=='dlg': print('  diálogo:',(s.dialogo() or '')[:700]); print('  campos:',json.dumps(s.campos(),ensure_ascii=False)[:1400]); continue
        if isinstance(a,tuple) and a[0]=='in': print('  clica(dialog)',a[1],'→',clicaT(s,a[1],raiz='[role=dialog]')); print('  toast:',s.toast()); continue
        print('  clica',a,'→',clicaT(s,a)); print('  toast:',s.toast())
    s.shot(nome)
    if depois: depois()
try:
  passo('Caio','CO-06det.dc.html',['Liberar para destinação compatível'],'ex33_co06det_caio')
  passo('Caio','PT-04det.dc.html',['Recusar crédito'],'ex33_pt04det')
  def ge05():
      print('  linha f2096:',s.J("[...document.querySelectorAll('[role=row]')].filter(e=>/FAT-2096/.test(e.innerText)).map(e=>e.innerText.replace(/\\s+/g,' ').slice(0,220))"))
      s.ir('GE-05.dc.html',1.5); print('  após recarga, botão:',[b for b in s.botoes() if 'crédito' in b.lower()][:3], '| bloco:', 'Crédito emitido' in s.texto())
  passo('Caio','GE-05.dc.html',['Emitir crédito do RC-12'],'ex33_ge05_caio',depois=ge05)
  def lo04():
      s.ir('LO-04.dc.html',1.5); print('  após recarga:',[b for b in s.botoes() if 'Rota Sul' in b])
  passo('Caio','LO-04.dc.html',['Contratar Rota Sul'],'ex33_lo04_caio',depois=lo04)
  passo('Caio','AG-06.dc.html',['Registrar parecer'],'ex33_ag06_caio')
  passo('Caio','SU-04.dc.html',['Selecionar Fertisul'],'ex33_su04_sel')
  print('  nota alçada SU-04:',[l for l in s.texto().split('\n') if 'Alçada' in l][:3])
  def su05():
      print('  contratos:',s.J("[...document.querySelectorAll('[role=row]')].filter(e=>/CT-2026-14|CT-2026-03/.test(e.innerText)).map(e=>e.innerText.replace(/\\s+/g,' ').slice(0,240))"))
      print('  pedidos:',s.J("[...document.querySelectorAll('[role=row]')].filter(e=>/PC-094|PC-093/.test(e.innerText)).map(e=>e.innerText.replace(/\\s+/g,' ').slice(0,200))"))
  passo('Caio','SU-05.dc.html',['Formalizar contrato',('dlg',),('in','Formalizar contrato'),'Emitir pedido','Confirmar fornecedor'],'ex33_su05_caio',depois=su05)
  def su04():
      print('  linha COT-113:',s.J("[...document.querySelectorAll('[role=row]')].filter(e=>/COT-113/.test(e.innerText)).map(e=>e.innerText.replace(/\\s+/g,' ').slice(0,240))"))
  passo('Caio','SU-04.dc.html',['Enviar COT-113'],'ex33_su04_cot113',depois=su04)
  passo('Caio','GE-04.dc.html',['Enviar remessa ao banco'],'ex33_ge04_caio')
  def su08():
      print('  linhas PE:',s.J("[...document.querySelectorAll('[role=row]')].filter(e=>/PE-0/.test(e.innerText)).map(e=>e.innerText.replace(/\\s+/g,' ').slice(0,240))"))
      print('  aprovar perda →',clicaT(s,'Aprovar perda')); print('  toast:',s.toast())
      print('  linhas PE:',s.J("[...document.querySelectorAll('[role=row]')].filter(e=>/PE-0/.test(e.innerText)).map(e=>e.innerText.replace(/\\s+/g,' ').slice(0,240))"))
      s.shot('ex33_su08_aprovada_rui')
      s.ir('SU-08.dc.html',1.5); print('  após recarga, PE-013?', 'PE-013' in s.texto())
  passo('Rui','SU-08.dc.html',['Registrar perda',('dlg',),('fill',{'Quantidade':'5','Causa':'saco rasgado (teste sintético)','Evidência':'foto sintética','Aprovador':'Gerente da fazenda'}),('in','Submeter perda')],'ex33_su08_rui',depois=su08)
  passo('Caio','GE-08.dc.html#vis=dossie',['Autorizar bloco'],'ex33_ge08_caio')
  print('  perfis no seletor:',s.J("(typeof g2perfis==='function')?g2perfis().map(p=>p.t):null"))
  print('erros',s.erros())
finally: s.fim()
