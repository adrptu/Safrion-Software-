# -*- coding: utf-8 -*-
"""Teste real (Chrome) — O.S. 26/09, correções do verificador: insumos acompanham o cancelamento (os-04),
cabeçalho recalculado (os-04), Nova ordem não duplica OS-0431 nem OS-0421 (os-05)."""
import sys, os, time, subprocess, json
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from cdp import Chrome
from journeys import free
HERE=os.path.dirname(os.path.abspath(__file__)); R=sys.argv[1] if len(sys.argv)>1 else os.path.join(HERE,'_render')
p=free(); srv=subprocess.Popen(['python3','-m','http.server',str(p),'--bind','127.0.0.1','--directory',R],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(.8)
c=Chrome(port=free()); J=c.js; OK=[]; FAIL=[]
def chk(n,cond,info=''): (OK if cond else FAIL).append(n); print(('  ok  ' if cond else '  FALHOU ')+n+(' · '+str(info)[:260] if info!='' else ''))
def pan(): return J("(()=>{const a=document.querySelector('aside[role=dialog]'); return a?a.innerText.replace(/\\s+/g,' '):'';})()") or ''
def temb(t): return bool(J(f"[...document.querySelectorAll('aside[role=dialog] button')].some(b=>b.innerText.trim()==={json.dumps(t)})"))
def btn(t,root='aside[role=dialog]'):
    r=J(f"(()=>{{const b=[...document.querySelectorAll({json.dumps(root+' button')})].find(b=>b.innerText.trim()==={json.dumps(t)}); if(!b) return false; b.click(); return true;}})()"); time.sleep(.35); return r
def toast(): return J("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).filter(Boolean).join(' | ')") or ''
def ids(): return J("[...document.querySelectorAll('[role=row].g2ed')].map(r=>r.innerText.split('\\n')[0].trim())") or []
def abrir(id_): J(f"(()=>{{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.trim().startsWith({json.dumps(id_)})); r.click();}})()"); time.sleep(.4)
def fechar(): J("(()=>{const b=document.querySelector('aside[role=dialog] button[aria-label=Fechar]'); b&&b.click();})()"); time.sleep(.3)
def setv(sel,val):
    J(f"""(()=>{{const i=document.querySelector({json.dumps(sel)}); const P=i.tagName==='SELECT'?HTMLSelectElement.prototype:(i.tagName==='TEXTAREA'?HTMLTextAreaElement.prototype:HTMLInputElement.prototype);
      Object.getOwnPropertyDescriptor(P,'value').set.call(i,{json.dumps(val)}); i.dispatchEvent(new Event('input',{{bubbles:true}})); i.dispatchEvent(new Event('change',{{bubbles:true}}));}})()"""); time.sleep(.25)
def ins(): return J("(()=>{const a=document.querySelector('aside[role=dialog]'); if(!a) return ''; const t=a.innerText; const i=t.indexOf('INSUMOS'); const j=t.indexOf('APONTAMENTOS'); return t.slice(i,j).replace(/\\s+/g,' ');})()") or ''
def hdr(): return J("(()=>{const h=document.querySelector('header h1'); const s=h&&h.nextElementSibling; return s?s.innerText.trim():'';})()") or ''
def alerts(): return J("[...document.querySelectorAll('aside [role=alert]')].map(x=>x.innerText).join(' | ')") or ''
def cancelar(id_,mot):
    abrir(id_); btn('Cancelar sem execução'); setv('aside[role=dialog] textarea[aria-label="Motivo do cancelamento"]',mot); btn('Confirmar cancelamento')
def nova(cult,atv,jan='2026-09-28'):
    J("(()=>{const b=[...document.querySelectorAll('button')].find(b=>b.innerText.trim()==='Nova ordem'); b.click();})()"); time.sleep(.4)
    setv('#nv_saf','S2627'); setv('#nv_cult',cult); setv('#nv_atv',atv); setv('#nv_jan',jan); btn('Emitir ordem')
def reload():  # recomeça do início da demonstração: o cenário compartilhado (localStorage) guarda as mudanças entre recargas
    J("try{localStorage.removeItem('talhao-os-cenario-v1')}catch(e){}"); c.goto(f'http://127.0.0.1:{p}/OS.dc.html',wait=1.2)
try:
    c.size(1440,1000); reload()
    chk('sem erro JS', (J("window.__err||''") or '')=='')
    chk('cabeçalho inicial: 2 em execução · 2 impedidas', hdr()=='2 em execução · 2 impedidas', hdr())
    # ---------- os-04: insumos acompanham o cancelamento ----------
    cancelar('OS-0424','Chuva'); t=ins()
    chk('OS-0424 cancelada: insumo mostra a reserva liberada', 'Reserva de 65 L liberada · lote F26-02 · REQ-039' in t and 'Reservado 65 L' not in t, t)
    chk('OS-0424 cancelada: aviso, situação e insumo dizem o mesmo', 'Reserva de 65 L do lote F26-02 liberada.' in toast() and 'Reserva de 65 L do lote F26-02 liberada.' in pan(), toast())
    fechar()
    cancelar('OS-0425','Replanejar'); t=ins()
    chk('OS-0425 cancelada: insumo mostra a REQ-040 cancelada', 'REQ-040 cancelada · nada entregue' in t and 'faltam 3.400 kg' not in t, t)
    fechar()
    cancelar('OS-0431','Sem máquina'); t=ins()
    chk('OS-0431 cancelada (A liberar, sem reserva): nada reservado', t.count('Nada reservado · ordem cancelada')==2 and 'Reserva ao liberar' not in t, t)
    fechar()
    chk('cabeçalho recalculado: 2 em execução · 1 impedida', hdr()=='2 em execução · 1 impedida', hdr())
    # liberada e depois cancelada: a reserva feita na liberação volta
    abrir('OS-0430'); btn('Revisar versão'); btn('Aprovar versão'); btn('Liberar para execução'); btn('Confirmar liberação')
    chk('OS-0430 liberada: insumos reservados', 'Reservado no Estoque' in ins(), ins())
    btn('Cancelar sem execução'); setv('aside[role=dialog] textarea[aria-label="Motivo do cancelamento"]','Plantio adiado'); btn('Confirmar cancelamento'); t=ins()
    chk('OS-0430 cancelada depois de liberada: reserva liberada nos três insumos', t.count('Reserva liberada no Estoque')==3 and 'Reservado no Estoque' not in t, t)
    fechar()
    # iniciar a OS-0419 muda a contagem de execução
    abrir('OS-0419'); btn('Iniciar execução'); btn('Confirmar início'); fechar()
    chk('cabeçalho acompanha o início: 3 em execução', hdr()=='3 em execução · 1 impedida', hdr())
    # ---------- os-05: Nova ordem não duplica ordens do plano ----------
    reload(); n0=len(ids())
    nova('c3','a3'); e=alerts()
    chk('T2 · Plantio e adubação de base aponta a OS-0431, sem emitir', 'Já existe OS-0431 para esta atividade neste cultivo.' in e and temb('Abrir OS-0431') and 'emitida' not in toast(), (e,toast()))
    btn('Abrir OS-0431'); t=pan()
    chk('Abrir OS-0431 abre a ordem existente', t.startswith('OS-0431') and len(ids())==n0, t[:80])
    chk('Padrão · versão da OS-0431 sem repetir a REC-014 v2', 'Soja alta tecnologia v6 · REC-014 v2 · v1 aprovada' in t and t.count('REC-014 v2 · REC-014 v2')==0, t[t.find('PADRÃO'):][:90])
    fechar()
    for cult,loc in (('c1','T1-A'),('c2','T1-B'),('c3','T2')):
        nova(cult,'a6'); e=alerts()
        chk(f'{loc} · Fungicida 1ª aplicação aponta a OS-0421 (T1+T2)', 'Já existe OS-0421' in e and temb('Abrir OS-0421'), e)
        btn('Cancelar'); btn('Descartar alterações')
    nova('c3','a7'); tt=toast()
    chk('T2 · Fungicida 2ª aplicação (sem ordem) emite normalmente', 'OS-0440 emitida em A liberar' in tt, tt)
    fechar()
    # cancelada não conta: depois de cancelar a OS-0431, T2 · Plantio emite
    cancelar('OS-0431','Sem máquina'); fechar(); nova('c3','a3'); tt=toast()
    chk('OS-0431 cancelada: T2 · Plantio emite nova ordem (OS-0441)', 'OS-0441 emitida' in tt, (tt,alerts()))
    fechar()
    chk('sem erro JS no fim', (J("window.__err||''") or '')=='')
    c.shot(os.path.join(HERE,'_probe','osfix.png'))
finally:
    c.close(); srv.terminate()
print(f'\nRESULTADO: {len(OK)} ok · {len(FAIL)} falhas'); [print('  -',f) for f in FAIL]
