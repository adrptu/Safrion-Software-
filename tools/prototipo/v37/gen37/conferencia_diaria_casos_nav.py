"""Contraprovas N3 e 4254646830: duas abas reais e arquivamento após substituição."""
import argparse,json,time,urllib.request
from pathlib import Path
from os_lib import Os
from cdp import Chrome,WS
from app_lib import SETV
P=argparse.ArgumentParser();P.add_argument('--output',type=Path,required=True);args=P.parse_args()
if args.output.exists():P.error('preserve os brutos: escolha outro output')
t=Os();J=t.J;results=[];target=None;other=None

def check(n,c,info=None):
 results.append({'nome':n,'ok':bool(c),'info':info});print(('OK ' if c else 'FALHA ')+n,flush=True)
def setv(j,sel,val):j(f'({SETV})({json.dumps(sel)},{json.dumps(val)})');time.sleep(.2)
def open_day(j,dia):
 j("[...document.querySelectorAll('aside[role=dialog] section[aria-label] > button[aria-expanded=\"false\"]')].forEach(b=>b.click())");time.sleep(.2)
 j(f"document.getElementById('cd_OS-0421_{dia}_open').click()");time.sleep(.2)
def click(j,txt):
 j(f"[...document.querySelectorAll('section[aria-label=\"Conferência diária\"] button')].find(b=>b.innerText==={json.dumps(txt)}).click()");time.sleep(.25)
def ap(d):return t.cen(f"c.ordens['OS-0421'].ap.find(a=>a.dia==={d})")
def facts():return t.cen("JSON.stringify({os:c.ordens['OS-0421'].etapa,area:c.ordens['OS-0421'].realizado,saldo:c.ordens['OS-0421'].saldo,reqs:c.reqs,movs:c.movs})")
try:
 t.abrir();setv(J,'[aria-label="Trocar perfil de demonstração"]','Paula');t.ordem('OS-0421');open_day(J,4);setv(J,'#cd_OS-0421_4_mot','Rascunho da primeira aba')
 target=t.c.call('Target.createTarget',{'url':f'http://127.0.0.1:{t.p}/OS.dc.html'})['targetId']
 tabs=json.load(urllib.request.urlopen(f'http://127.0.0.1:{t.c.port}/json'))
 tab=next(x for x in tabs if x['id']==target);other=object.__new__(Chrome);other.ws=WS(tab['webSocketDebuggerUrl']);other.i=0
 other.call('Runtime.enable');other.call('Page.enable');other.goto(f'http://127.0.0.1:{t.p}/OS.dc.html',wait=.5);J2=other.js
 setv(J2,'[aria-label="Trocar perfil de demonstração"]','Paula')
 J2("[...document.querySelectorAll('[role=row].g2ed')].find(x=>x.innerText.startsWith('OS-0421')).click()");time.sleep(.3);open_day(J2,4)
 setv(J2,'#cd_OS-0421_4_dec','divergencia');setv(J2,'#cd_OS-0421_4_mot','Evidência ausente na segunda aba');click(J2,'Registrar conferência');time.sleep(.3)
 check('Caso aberto fica visível na listagem em execução','Divergência diária pendente' in t.linha('OS-0421'))
 before=ap(4);click(J,'Vincular evidência e conferir dia')
 check('Duas abas: prévia antiga não resolve caso novo',ap(4)==before and before['conferenciaDia']['caso']['estado']=='Em conferência' and 'versão mudou' in t.pan(),t.pan()[-650:])
 check('Duas abas: recusa preserva motivo da primeira aba',J("document.getElementById('cd_OS-0421_4_mot').value")=='Rascunho da primeira aba')
 t.btn('Rever dados atuais');setv(J,'#cd_OS-0421_4_mot','Evidência do dia revista no caso atual');click(J,'Vincular evidência e conferir dia')
 check('Duas abas: revisão explícita da referência atual resolve uma vez',ap(4)['conferenciaDia']['caso']['estado']=='Vinculado' and len(ap(4)['conferenciasAnteriores'])==1)
 t.c.call('Target.closeTarget',{'targetId':target});target=None;other.ws.s.close();other=None
 # Real duplicate commands; do not invent a discarded state or archive receipt.
 t.mudar("return osc_apontar(c,'OS-0421','26/09',50)");open_day(J,5);setv(J,'#cd_OS-0421_5_dec','divergencia');setv(J,'#cd_OS-0421_5_mot','Relato a conferir antes da substituição');click(J,'Registrar conferência')
 t.mudar("cenIniciarTurno(c,'OS-0421');cenFecharTurno(c,50,8,undefined,'',[]);return osc_apDecidir(c,'OS-0421',6,'este',undefined,'Paula')")
 check('Substituição preserva caso aberto e identifica dia vencedor',ap(5)['st']=='Duplicidade · não somado' and ap(5)['conferenciaDia']['caso']['estado']=='Em conferência' and ap(5)['dec']['vale']==6,ap(5))
 open_day(J,5);check('Descartado oferece arquivar caso, sem conferir execução',t.temb('Arquivar caso substituído') and not t.temb('Vincular evidência e conferir dia') and not t.temb('Registrar conferência'))
 check('Arquivamento nomeia o motivo correto','Motivo do arquivamento — obrigatório' in t.pan())
 before=facts();click(J,'Arquivar caso substituído');check('Arquivamento exige motivo e preserva efeitos',ap(5)['conferenciaDia']['caso']['estado']=='Em conferência' and facts()==before)
 setv(J,'#cd_OS-0421_5_mot','Mesmo turno: vale o dia 6, conforme decisão de Paula');t.c.size(390,844)
 J("document.getElementById('cd_OS-0421_5_mot').scrollIntoView({block:'center'})");time.sleep(.2);t.c.shot(str(args.output.with_suffix('.png')))
 click(J,'Arquivar caso substituído')
 check('Arquivamento fecha caso com trilha sem novo estorno',ap(5)['conferenciaDia']['caso']['estado']=='Arquivado' and ap(5)['conferenciaDia']['caso']['descarte']['vale']==6 and ap(5)['st']=='Duplicidade · não somado' and facts()==before and len(ap(5)['conferenciasAnteriores'])==1)
 check('Caso arquivado não oferece nova gravação',not J("!!document.getElementById('cd_OS-0421_5_open')"))
 # Same event turn: both clicks use the same rendered handler.
 open_day(J,4);setv(J,'#cd_OS-0421_4_mot','Conferência atual, um recibo')
 n=len(ap(4).get('conferenciasAnteriores',[]))
 J("(()=>{const b=[...document.querySelectorAll('section[aria-label=\"Conferência diária\"] button')].find(b=>b.innerText==='Registrar conferência');b.click();b.click()})()");time.sleep(.3)
 check('Duplo clique não deixa rascunho de erro nem duplica recibo',len(ap(4)['conferenciasAnteriores'])==n+1 and not t.temb('Registrar conferência') and not J("!!document.getElementById('cd_OS-0421_4_erro')"))
 t.mudar("c.ordens['OS-0421'].ap.find(a=>a.dia===4).quem='Paula (conferência)';return {msg:'Fixture do mesmo autor'}");open_day(J,4)
 check('Mesmo autor recebe aviso antes de gravar','Ao registrar, ficará revisão posterior pendente' in t.pan())
 t.mudar("c.ordens['OS-0421'].etapa='Encerradas';return {msg:'Fixture de ordem encerrada'}");t.fechar();t.ordem('OS-0421');t.pan()
 check('Ordem encerrada oferece somente consulta da conferência',not J("!!document.getElementById('cd_OS-0421_4_open')") and not t.temb('Registrar conferência'))
 check('Sem erro JavaScript',not t.erros(),t.erros())
except Exception as e:
 check('Jornada sem interrupção',False,repr(e))
finally:
 if target:t.c.call('Target.closeTarget',{'targetId':target})
 if other:other.ws.s.close()
 t.fim();args.output.write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
raise SystemExit(0 if results and all(x['ok'] for x in results) else 1)
