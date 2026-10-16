import json,time
from o0lib import S,cen,clicaT,preenche,VIS
s=S()
SEL="(()=>{const e=[...document.querySelectorAll('input[type=checkbox],[role=checkbox],button')].filter(x=>x.getClientRects().length).find(x=>/Selecionar as \\d+ linhas/.test(x.getAttribute('aria-label')||x.title||x.innerText||'')); if(!e) return 'sem'; e.click(); return (e.getAttribute('aria-label')||'');})()"
def ev430(c):
    o=(c or {}).get('ordens',{}).get('OS-0430') if c else None
    if not o: return None
    return {'etapa':o.get('etapa'),'ev':[e.get('t') for e in ((o.get('osc') or {}).get('ev') or [])]}
try:
  import subprocess; print('render:',subprocess.run(['git','-C','/tmp/claude-0/v69b','log','--oneline','-1'],capture_output=True,text=True).stdout.strip())
  # EX-32 PL-04
  for perf in ['Ana','Caio']:
    s.reset(perf); s.ir('PL-04.dc.html',1.6)
    print('\n== PL-04',perf); print('  conferir:',clicaT(s,'Conferir prontidão')); print('  toast:',s.toast())
    ls0=s.ls(); print('  liberar prontas:',clicaT(s,'Liberar prontas')); print('  toast:',s.toast()); print('  ls mudou:',[k for k,v in s.ls().items() if ls0.get(k)!=v]); s.shot('ex32_pl04_'+perf+'_ba0e994')
  # EX-32 CA-01
  for perf in ['Ana','Caio']:
    s.reset(perf); s.ir('CA-01.dc.html',1.8); print('\n== CA-01',perf); print('  sel:',s.J(SEL)); time.sleep(.4)
    ls0=s.ls(); print('  liberar sel:',clicaT(s,'Liberar selecionadas')); print('  toast:',s.toast()); print('  ls mudou:',[k for k,v in s.ls().items() if ls0.get(k)!=v]); s.shot('ex32_ca01_'+perf+'_ba0e994')
  # OS.dc · caminho correto, OS-0430
  for perf in ['Caio','Ana']:
    s.reset(perf); s.ir('OS.dc.html',2.0); print('\n== OS.dc OS-0430',perf)
    r=s.J("(()=>{const r=[...document.querySelectorAll('[role=row]')].find(e=>/OS-0430/.test(e.innerText)); if(!r) return 'sem'; (r.querySelector('[role=gridcell]')||r).click(); return 'ok';})()"); time.sleep(1.0); print('  abriu:',r)
    print('  botões:',[b for b in s.botoes() if 'iberar' in b or 'provar' in b][:6])
    c0=cen(s); print('  antes:',ev430(c0) or 'cenário semente (nada gravado)')
    print('  liberar:',clicaT(s,'Liberar para execução')); time.sleep(.6); print('  diálogo:',(s.dialogo() or '')[:400])
    for t in ['Aprovar e liberar','Confirmar','Liberar']:
        if s.dialogo():
            r=clicaT(s,t,raiz='[role=dialog]')
            if r.startswith('ok'): print('  confirma:',r); break
    time.sleep(.6); print('  toast:',s.toast()); print('  depois:',ev430(cen(s))); s.shot('ex32_os0430_'+perf)
  # IN-02 Caio
  s.reset('Caio'); s.ir('IN-02.dc.html',1.6); print('\n== IN-02 Caio'); print('  sel:',s.J(SEL)); time.sleep(.4); print('  aprovar:',clicaT(s,'Aprovar selecionados')); print('  toast:',s.toast()); s.shot('ex32_in02_Caio_ba0e994')
  # CA-03 só OC-114 e CA-03det
  s.reset('Ana'); s.ir('CA-03.dc.html',1.6); print('\n== CA-03')
  s.J("(()=>{const cb=[...document.querySelectorAll('input[type=checkbox]')].find(e=>/OC-114/.test(e.getAttribute('aria-label')||'')); cb&&cb.click();})()"); time.sleep(.4)
  print('  encerrar (só OC-114):',clicaT(s,'Encerrar tratamento')); print('  toast:',s.toast()); s.shot('ex32_ca03_so114_ba0e994')
  s.ir('CA-03det.dc.html',1.6); print('  CA-03det encerrar:',clicaT(s,'Encerrar tratamento')); print('  toast:',s.toast())
  # IR-01 com Rui
  s.reset('Rui'); s.ir('IR-01.dc.html',2.0); print('\n== IR-01 Rui'); print('  conferir:',clicaT(s,'Conferir medição')); time.sleep(.4); print('  validar:',clicaT(s,'Validar e encerrar')); print('  toast:',s.toast())
  # EST devolução (fluxo do cenário)
  s.reset('Rui'); s.ir('EST.dc.html',2.0); print('\n== EST devolução')
  print('  etapa:',clicaT(s,'Receba devoluções')); time.sleep(.6)
  print('  linhas:',s.J("[...document.querySelectorAll('[role=row]')].filter(e=>/REQ-0/.test(e.innerText)).map(e=>e.innerText.replace(/\\s+/g,' ').slice(0,200)).slice(0,4)"))
  r=s.J("(()=>{const r=[...document.querySelectorAll('[role=row]')].find(e=>/REQ-031/.test(e.innerText)&&/custódia|Paula|sc/.test(e.innerText)); if(!r) return 'sem'; (r.querySelector('[role=gridcell]')||r).click(); return 'ok';})()"); time.sleep(.7)
  print('  abriu REQ-031:',r); print('  campos:',json.dumps(s.campos(),ensure_ascii=False)[:900]); s.shot('ex34_est_devolucao_form')
  print('  erros',s.erros())
finally: s.fim()
