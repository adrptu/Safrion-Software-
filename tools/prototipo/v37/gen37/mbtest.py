# -*- coding: utf-8 -*-
"""Teste CDP do módulo App móvel (MB-01..MB-10 + detalhes): altura sem corte, sem buracos, ações com title,
estados DEMO-11 (fila do aparelho sem sinal / reenviar sem duplicar), DEMO-14 (reconhecer), DEMO-20 (papéis), confirmações que mudam a tela.
v3.9: MB-01..MB-05 leem o cenário compartilhado (fila de Marcos, sinal, recibos); a jornada completa está em app_cenario_test.py.
Uso: python3 mbtest.py [--shots] [a|b|c|d]   (a = genéricos MB-01..MB-05det · b = genéricos MB-06..MB-10det · c = jornadas · d = erros JS;
     sem letra roda tudo — passa de 90 s: rode por partes)"""
import sys, os, time, subprocess, json, re
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from cdp import Chrome
from journeys import free
HERE=os.path.dirname(os.path.abspath(__file__)); R=os.path.join(HERE,'_render'); OUT=os.path.join(HERE,'_shots'); p=free()
TELAS=['MB-01','MB-02','MB-02det','MB-03','MB-03x-recibo','MB-04','MB-05','MB-05det','MB-06','MB-07','MB-08','MB-08x-recibo','MB-09','MB-09det','MB-10','MB-10det']
for t in TELAS:
    open(os.path.join(R,t+'.dc.html'),'w').write(open(os.path.join(HERE,'project',t+'.dc.html')).read())
srv=subprocess.Popen(['python3','-m','http.server',str(p),'--bind','127.0.0.1','--directory',R],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(0.8)
c=Chrome(port=free()); J=c.js; FAIL=[]
PARTES=[x for x in sys.argv[1:] if x in ('a','b','c','d')] or ['a','b','c','d']
def parte(x): return x in PARTES
SETV="""((sel,val)=>{const i=document.querySelector(sel); const P=i.tagName==='TEXTAREA'?HTMLTextAreaElement.prototype:HTMLInputElement.prototype; Object.getOwnPropertyDescriptor(P,'value').set.call(i,val); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true}));})"""
CLK="""((t)=>{const n=s=>(s||'').replace(/\\s+/g,' ').trim(); const els=[...document.querySelectorAll('button,a')].filter(e=>e.offsetParent!==null); const e=els.find(x=>n(x.innerText)===t)||els.find(x=>n(x.innerText).startsWith(t)); if(!e) return 'NÃO ACHEI: '+t; e.click(); return 'ok';})"""
T=lambda: J("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).filter(Boolean).join(' | ')")
BODY=lambda: J("document.body.innerText")
HDR=lambda: J("document.querySelector('header').innerText.replace(/\\s+/g,' ')")
FOOT=lambda: J("(()=>{const f=[...document.querySelectorAll('a,button')].filter(e=>e.offsetParent!==null&&/font-size: 17px/.test(e.getAttribute('style')||'')); return f.map(e=>e.innerText.trim()).join(' | ');})()")
def clk(t): r=J(f"({CLK})({json.dumps(t)})"); time.sleep(.4); return r
def ok(cond,msg):
    print(('  OK  ' if cond else '  FALHA ')+msg)
    if not cond: FAIL.append(msg)
def open_(t):
    c.goto(f'http://127.0.0.1:{p}/{t}.dc.html',wait=1.2)
    J("window.__errs=[]; window.addEventListener('error',e=>window.__errs.push(e.message));")
def over(): return J("(()=>{const m=document.querySelector('main'); const kids=[...m.children].filter(e=>e.offsetParent!==null||e.tagName==='SC-IF'); let b=0; m.querySelectorAll(':scope > *, :scope > sc-if > *').forEach(e=>{const r=e.getBoundingClientRect(); if(r.height) b=Math.max(b,r.bottom);}); const mr=m.getBoundingClientRect(); return Math.round(b+16-mr.bottom);})()")
def wide(): return J("(()=>{const m=document.querySelector('main'); return [...m.querySelectorAll('*')].filter(e=>e.getBoundingClientRect().right>392).map(e=>e.tagName+':'+(e.innerText||'').slice(0,30)).slice(0,3);})()")
try:
    c.size(390,2400)   # viewport ≥ altura da prancha (MB-02 = 2320): com o teto 100dvh do celular real, abaixo disso o main rola e a medida deixa de ser da prancha
    for t in [x for i,x in enumerate(TELAS) if parte('a' if i<8 else 'b')]:
        open_(t); print(t)
        ok(J("document.body.innerText.indexOf('{{')<0"),'sem buracos {{}} visíveis')
        o=over(); ok(o<=0,f'{t}: conteúdo cabe na altura (excesso {o}px)'); print('    folga',-o)
        w=wide(); ok(not w,'sem estouro horizontal '+str(w))
        nt=J("[...document.querySelectorAll('main button, main a')].filter(e=>e.offsetParent!==null&&!e.getAttribute('title')&&e.getAttribute('role')!=='tab').map(e=>e.innerText.trim()).slice(0,4)")
        ok(not nt,'ações secundárias com title '+str(nt))
        ok(not re.search(r'\bEditar\b',BODY()),'sem botão Editar')
        if '--shots' in sys.argv: c.shot(os.path.join(OUT,t+'_cdp.png'))
    if parte('c'):
      print('v3.9 · MB-01 minha fila do cenário')
      open_('MB-01'); b=BODY()
      ok('OS-0421 · Pulverização' in b and 'OS-0424 · Pulverização' in b and 'OS-0420' not in b and 'OS-0419' not in b,'MB-01: fila só com ordens de Marcos liberadas/em execução')
      ok('Realizado 190 de 350 ha · saldo 160 ha' in b and 'com você 65 L' in b and 'retirar 65 L' in b,'MB-01: realizado, saldo e insumos a retirar/com você')
      ok('Com sinal' in b and 'Sem sinal' in b and 'Nada aguardando sinal' in b and 'Restaurar demonstração' in b,'MB-01: alternador de sinal, contador e restaurar')
      ok(FOOT()=='Iniciar turno · OS-0421','primário = passo mais urgente: '+FOOT())
      print('DEMO-11 · MB-02 pacote')
      open_('MB-02'); b=BODY()
      ok('Realizado 190 de 350 ha · saldo 160 ha' in b and 'Aguarda liberação no escritório' in b,'MB-02: OS-0421 do cenário e OS-0430 aguardando liberação')
      ok('Revogada no servidor' in b and 'Relato fora da autorização atual · aguarda decisão' in b,'ordem revogada e relato fora da autorização')
      clk('Iniciar · bloqueado (revogada'); ok('revogada no servidor' in T(),'iniciar ordem revogada bloqueia com motivo')
      print('DEMO-14 · MB-02 reconhecer')
      ok('Fichas do saldo revogadas' in b and 'Revisão de saldo' not in b and 'aprovar a v3' not in b,'aviso de revogação das fichas do saldo (sem selo de revisão da v3)')
      clk('Reconhecer'); ok('CI-0931' in T() and 'Ciência registrada · CI-0931' in BODY(),'reconhecer registra ciência')
      ok(clk('Reconhecer').startswith('NÃO ACHEI'),'botão Reconhecer some após ciência')
      print('DEMO-11 · sem sinal → fila do aparelho → reenviar sem duplicar')
      open_('MB-03'); ok(FOOT()=='Iniciar turno · OS-0421' and 'Nenhum turno aberto' in BODY(),'MB-03 sem turno: primário Iniciar turno')
      open_('MB-04'); clk('Sem sinal'); J(f"({SETV})('#oc_txt','Bico da seção 3 entupido; troquei e segui.')"); time.sleep(.2); clk('Registrar ocorrência')
      ok('No aparelho · aguardando sinal' in BODY() and '1 registro aguardando sinal' in BODY(),'ocorrência sem sinal fica no aparelho')
      open_('MB-03x-recibo'); ok(FOOT()=='Reenviar pendentes' and 'REC-7741' in BODY(),'recibos: 1 pendente e histórico REC-7741')
      clk('Reenviar pendentes'); ok('sem cópia' in T() and '1 registro aguardando sinal' in BODY(),'reenviar sem sinal não duplica')
      clk('Com sinal'); b=BODY(); ok('REC-7742' in b and 'Nada aguardando sinal' in b and FOOT()=='Voltar à fila','sinal volta: enviado uma vez com recibo REC-7742')
      print('DEMO-05/15 · MB-08')
      open_('MB-08'); b=BODY()
      ok('hoje 20:00–amanhã 10:31 · 1 volta de 14,5 h' in b and 'iniciada 20:02' in b and '2,1 de 14,5 h executadas' in b and '21:04' not in b and '21:32' not in b,'janela da volta inteira (14,5 h), início e andamento')
      ok('13,5 mm (OS-0422)' in b and '14 mm' not in b,'13,5 mm da OS-0422')
      open_('MB-08x-recibo'); b=BODY()
      ok('LIB-2287' in b and 'LB-2205' not in b,'liberação LIB-2287')
      ok('10,81 mm nos 80 ha (volta completa' in b and '20:02–24/09 10:33' in b,'execução da volta completa')
      ok('nada nesta ordem' not in b and 'próximo ciclo: OS-0422' in b,'falta mostra o próximo ciclo')
      print('DEMO-06 · MB-07')
      open_('MB-07'); b=BODY()
      ok('Previsão T7 · S39 (v S39-02)' in b and 'Previsão PV-031' not in b and 'previsão S39, que abastece o PV-031' in b,'previsão x pedido')
      clk('Registrar e ir à planta 19'); ok('planta 19 de 40' in BODY(),'avança planta')
      print('DEMO-20 · MB-10 papéis')
      open_('MB-10'); b=BODY()
      ok('CG-1207' in b and 'T2' not in b and 'Carga 05' not in b,'balança sem T2/Carga 05')
      ok('Sandra (fiscal) · prazo hoje 10:00' in b,'Carga 07 · Sandra 10:00')
      J("document.querySelectorAll('[role=tab]')[1].click()"); time.sleep(.4); b=BODY()
      ok('Minha viagem' in b and 'Abrir pesagem' not in b and 'Carga 07' not in b and 'Confirmar chegada' not in b,'motorista vê só a viagem')
      ok('Informar nova previsão' in FOOT(),'primário do motorista')
      clk('Informar nova previsão'); ok('10:20' in BODY(),'nova previsão exibida')
      J("document.querySelectorAll('[role=tab]')[2].click()"); time.sleep(.4)
      ok('Minha viagem' not in BODY() and 'Chegada a confirmar' in BODY(),'recebedor vê a chegada')
      clk('Confirmar chegada'); ok('Chegada confirmada' in BODY() and 'chegada confirmada' in HDR(),'confirmar chegada muda selo e cabeçalho')
      print('Confirmações de detalhe')
      for tela,bt,exp in [('MB-05det','Confirmar recebimento','DV-0912'),('MB-09det','Concluir serviço','Em conferência'),('MB-10det','Confirmar pesagem','ROM-0791 emitido'),('MB-04','Registrar ocorrência','registrada')]:
          open_(tela)
          if tela=='MB-04': J(f"({SETV})('#oc_txt','Vento acima de 10 km/h; parei a barra.')"); time.sleep(.2)
          clk(bt); ok(exp in BODY() or exp in HDR(),f'{tela}: {bt} → {exp}')
          ok(clk(bt).startswith('NÃO ACHEI'),f'{tela}: primário não repete a ação')
    for t in (TELAS if parte('d') else []):
        open_(t); e=J("window.__errs"); ok(not e,f'{t} sem erros JS {e}')
finally:
    c.close(); srv.terminate()
print('FALHAS:',len(FAIL)); [print(' -',f) for f in FAIL]
