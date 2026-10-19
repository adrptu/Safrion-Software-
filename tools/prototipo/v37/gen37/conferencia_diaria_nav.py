"""CONTROLE-02: jornada real na O.S.; dados/perfil isolados pelo os_lib existente."""
import argparse
import json
import time
from pathlib import Path
from os_lib import Os
from app_lib import SETV

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args()
if args.output.exists(): parser.error('preserve os brutos: escolha outro output')
t=Os();j=t.J;resultados=[]
def check(nome,cond,valor=None):
 resultados.append({'nome':nome,'ok':bool(cond),'valor':valor})
 print(('OK ' if cond else 'FALHA ')+nome,flush=True)
def setv(sel,val):
 r=j(f'({SETV})({json.dumps(sel)},{json.dumps(val)})');time.sleep(.15);return r
def open_day():
 t.pan();j("document.getElementById('cd_OS-0421_4_open').click()");time.sleep(.2)
def facts():return t.cen("JSON.stringify({fase:c.ordens['OS-0421'].etapa,real:c.ordens['OS-0421'].realizado,saldo:c.ordens['OS-0421'].saldo,reqs:c.reqs,movs:c.movs})")
try:
 t.abrir();setv('[aria-label="Trocar perfil de demonstração"]','Paula');t.ordem('OS-0421');open_day();before=facts()
 check('Contexto, comparação honesta e foco inicial',j("document.activeElement.id")== 'cd_OS-0421_4_dec' and 'Não há meta diária registrada' in t.pan())
 t.c.call('Input.dispatchKeyEvent',{'type':'keyDown','key':'Tab','code':'Tab','windowsVirtualKeyCode':9});t.c.call('Input.dispatchKeyEvent',{'type':'keyUp','key':'Tab','code':'Tab','windowsVirtualKeyCode':9})
 check('Teclado alcança motivo após resultado',j('document.activeElement.id')=='cd_OS-0421_4_mot')
 setv('#cd_OS-0421_4_dec','divergencia');t.btn('Registrar conferência')
 check('Motivo obrigatório, foco no erro, sem efeitos', 'Informe o motivo' in t.pan() and j('document.activeElement.id')=='cd_OS-0421_4_erro' and facts()==before)
 setv('#cd_OS-0421_4_mot','Horas precisam de evidência');t.fechar();t.ordem('OS-0421');t.pan()
 check('Fechar e reabrir preserva motivo e ordem',j("document.getElementById('cd_OS-0421_4_mot').value")=='Horas precisam de evidência')
 t.btn('Registrar conferência')
 check('Divergência grava Não conforme sem repetir efeitos',t.cen("c.ordens['OS-0421'].ap.find(a=>a.dia===4).conferenciaDia.estado")=='Não conforme' and facts()==before)
 open_day()
 check('Caso identificado, resolução explícita e foco no motivo', 'Caso CD-OS-0421-4-' in t.pan() and not j("!!document.getElementById('cd_OS-0421_4_dec')") and j('document.activeElement.id')=='cd_OS-0421_4_mot')
 t.btn('Vincular evidência e conferir dia')
 check('Resolução exige evidência sem fechar caso', 'Informe o motivo e a evidência' in t.pan() and t.cen("c.ordens['OS-0421'].ap.find(a=>a.dia===4).conferenciaDia.caso.estado")=='Em conferência')
 setv('#cd_OS-0421_4_mot','Evidência conferida');t.c.size(390,844)
 j("document.getElementById('cd_OS-0421_4_mot').scrollIntoView({block:'center'})");time.sleep(.2)
 caseBounds=j("(()=>{const s=document.querySelector('section[aria-label=\"Conferência diária\"]'),r=s.getBoundingClientRect();return {left:r.left,right:r.right,scroll:s.scrollWidth,client:s.clientWidth,primary:[...s.querySelectorAll('button')].filter(b=>b.innerText==='Vincular evidência e conferir dia').map(b=>({h:b.getBoundingClientRect().height,top:b.getBoundingClientRect().top,bottom:b.getBoundingClientRect().bottom}))}})()")
 check('390px: resolver caso cabe e ação primária fica alcançável',caseBounds['left']>=0 and caseBounds['right']<=390 and caseBounds['scroll']<=caseBounds['client'] and len(caseBounds['primary'])==1 and caseBounds['primary'][0]['h']>=44 and caseBounds['primary'][0]['bottom']<=844,caseBounds)
 t.c.shot(str(args.output.with_name(args.output.stem+'-caso.png')))
 t.btn('Vincular evidência e conferir dia')
 check('Resolução preserva histórico e devolve foco',t.cen("c.ordens['OS-0421'].ap.find(a=>a.dia===4).conferenciasAnteriores.length")==1 and j('document.activeElement.id')=='cd_OS-0421_4_open' and facts()==before)
 open_day();setv('#cd_OS-0421_4_mot','Rascunho da conferente')
 t.mudar("c.ordens['OS-0421'].versao='v99';return {msg:'Mudança concorrente sintética'}")
 t.btn('Registrar conferência')
 check('Versão concorrente recusa e conserva rascunho', 'versão mudou' in t.pan() and j("document.getElementById('cd_OS-0421_4_mot').value")=='Rascunho da conferente')
 t.btn('Rever dados atuais');t.btn('Registrar conferência')
 check('Rever dados permite decisão atual com recibo',t.cen("c.ordens['OS-0421'].ap.find(a=>a.dia===4).conferenciaDia.motivo")=='Rascunho da conferente')
 open_day();setv('[aria-label="Trocar perfil de demonstração"]','Marcos');t.pan()
 check('Trocar perfil fecha decisão, preserva dados',not t.temb('Registrar conferência'))
 open_day();check('Sem papel a tela informa quem decide e não oferece gravação',not t.temb('Registrar conferência') and 'Paula (conferência)' in t.pan())
 setv('[aria-label="Trocar perfil de demonstração"]','Paula');t.c.size(390,844);open_day()
 j("document.getElementById('cd_OS-0421_4_mot').scrollIntoView({block:'center'})");time.sleep(.2)
 bounds=j("(()=>{const s=document.querySelector('section[aria-label=\"Conferência diária\"]'),r=s.getBoundingClientRect();return {left:r.left,right:r.right,scroll:s.scrollWidth,client:s.clientWidth,buttons:[...s.querySelectorAll('button')].map(b=>({text:b.innerText,h:b.getBoundingClientRect().height}))}})()")
 check('390px: formulário e ações cabem, alvos de 44px',bounds['left']>=0 and bounds['right']<=390 and bounds['scroll']<=bounds['client'] and all(b['h']>=44 for b in bounds['buttons']),bounds)
 t.c.shot(str(args.output.with_suffix('.png')))
 t.mudar("c.ordens['OS-0421'].ap.find(a=>a.dia===4).st='Duplicidade · não somado';return {msg:'Projeção sintética do resultado de descarte'}")
 check('Apontamento descartado mantém recibo visível e não oferece reconferência', 'Fora do acumulado · histórico preservado' in t.pan() and not t.temb('Registrar conferência') and bool(t.cen("c.ordens['OS-0421'].ap.find(a=>a.dia===4).conferenciaDia")))
 check('Sem erro JavaScript',not t.erros(),t.erros())
except Exception as e:
 check('Jornada executada sem interrupção',False,repr(e));raise
finally:
 t.fim();args.output.write_text(json.dumps(resultados,ensure_ascii=False,indent=2)+'\n')
raise SystemExit(0 if resultados and all(r['ok'] for r in resultados) else 1)
