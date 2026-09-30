# -*- coding: utf-8 -*-
"""Verificador independente (os-04..os-07): casos além do osacoes.py — só observa, não altera o protótipo."""
import sys, os, time, subprocess, json
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from cdp import Chrome
from journeys import free
HERE=os.path.dirname(os.path.abspath(__file__)); R=os.path.join(HERE,'_render')
p=free(); srv=subprocess.Popen(['python3','-m','http.server',str(p),'--bind','127.0.0.1','--directory',R],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(.8)
c=Chrome(port=free()); J=c.js; OK=[]; FAIL=[]
def chk(n,cond,info=''): (OK if cond else FAIL).append(n); print(('  ok  ' if cond else '  FALHOU ')+n+(' · '+str(info)[:400] if info!='' else ''))
def pan(): return J("(()=>{const a=document.querySelector('aside[role=dialog]'); return a?a.innerText.replace(/\\s+/g,' '):'';})()") or ''
def temb(t): return bool(J(f"[...document.querySelectorAll('aside[role=dialog] button')].some(b=>b.innerText.trim()==={json.dumps(t)})"))
def btn(t,root='aside[role=dialog]'):
    r=J(f"(()=>{{const b=[...document.querySelectorAll({json.dumps(root+' button')})].find(b=>b.innerText.trim()==={json.dumps(t)}); if(!b) return false; b.click(); return true;}})()"); time.sleep(.35); return r
def toast(): return J("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).filter(Boolean).join(' | ')") or ''
def linha(id_): return J(f"(()=>{{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.trim().startsWith({json.dumps(id_)})); return r?r.innerText.replace(/\\s+/g,' '):'';}})()") or ''
def ids(): return J("[...document.querySelectorAll('[role=row].g2ed')].map(r=>r.innerText.split('\\n')[0].trim())") or []
def abrir(id_): J(f"(()=>{{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.trim().startsWith({json.dumps(id_)})); r.click();}})()"); time.sleep(.4)
def fechar(): J("(()=>{const b=document.querySelector('aside[role=dialog] button[aria-label=Fechar]'); b&&b.click();})()"); time.sleep(.3)
def setv(sel,val):
    J(f"""(()=>{{const i=document.querySelector({json.dumps(sel)}); const P=i.tagName==='SELECT'?HTMLSelectElement.prototype:(i.tagName==='TEXTAREA'?HTMLTextAreaElement.prototype:HTMLInputElement.prototype);
      Object.getOwnPropertyDescriptor(P,'value').set.call(i,{json.dumps(val)}); i.dispatchEvent(new Event('input',{{bubbles:true}})); i.dispatchEvent(new Event('change',{{bubbles:true}}));}})()"""); time.sleep(.25)
def marca(lab): J(f"document.querySelector('aside[role=dialog] input[aria-label={json.dumps(lab)}]').click()"); time.sleep(.25)
def chip_fase(t): J(f"(()=>{{const b=[...document.querySelectorAll('[aria-label=\"Filtrar por fase\"] button')].find(b=>b.innerText.replace(/\\s+/g,' ').trim().startsWith({json.dumps(t)})); b.click();}})()"); time.sleep(.4)
def chips(): return J("[...document.querySelectorAll('[aria-label=\"Filtrar por fase\"] button')].map(b=>b.innerText.replace(/\\s+/g,' ').trim())") or []
def kanban(): J("(()=>{const b=[...document.querySelectorAll('button')].find(b=>b.innerText.trim()==='Kanban'); b&&b.click();})()"); time.sleep(.4)
def lista(): J("(()=>{const b=[...document.querySelectorAll('button')].find(b=>b.innerText.trim()==='Lista'); b&&b.click();})()"); time.sleep(.4)
def cartao(id_): return J(f"(()=>{{const k=[...document.querySelectorAll('[aria-label=\"Kanban das ordens\"] [role=button]')].find(x=>x.innerText.indexOf({json.dumps(id_)})===0); return k?k.innerText.replace(/\\s+/g,' '):'';}})()") or ''
def ins(): return J("(()=>{const a=document.querySelector('aside[role=dialog]'); if(!a) return ''; const t=a.innerText; const i=t.indexOf('INSUMOS'); return t.slice(i,i+600).replace(/\\s+/g,' ');})()") or ''
def nova(saf,cult,atv,jan):
    J("(()=>{const b=[...document.querySelectorAll('button')].find(b=>b.innerText.trim()==='Nova ordem'); b.click();})()"); time.sleep(.4)
    setv('#nv_saf',saf); setv('#nv_cult',cult); setv('#nv_atv',atv); setv('#nv_jan',jan); btn('Emitir ordem')
def alerts(): return J("[...document.querySelectorAll('aside [role=alert]')].map(x=>x.innerText).join(' | ')") or ''
def reload(): c.goto(f'http://127.0.0.1:{p}/OS.dc.html',wait=1.2)
try:
    c.size(1440,1000); reload()
    chk('sem erro JS', (J("window.__err||''") or '')=='')
    # 1) OS-0424: cancelar -> a seção Insumos ainda diz "Reservado"?
    abrir('OS-0424'); print('   insumos antes:', ins()[:200])
    btn('Cancelar sem execução'); setv('aside[role=dialog] textarea[aria-label="Motivo do cancelamento"]','Chuva'); btn('Confirmar cancelamento')
    print('   toast:', toast()); t=ins(); print('   insumos depois:', t[:250])
    chk('OS-0424 cancelada: seção Insumos deixa de mostrar a reserva de 65 L', 'Reservado 65 L' not in t, t[:250])
    chk('OS-0424 cancelada: fase e situação', 'Canceladas' in pan()[:120] and 'Reserva de 65 L do lote F26-02 liberada' in pan(), pan()[-400:])
    fechar()
    # 2) OS-0425: cancelar (Liberadas com REQ-040)
    abrir('OS-0425'); chk('OS-0425 oferece Cancelar sem execução', temb('Cancelar sem execução'))
    btn('Cancelar sem execução'); t=pan(); chk('OS-0425 confirmação cita a REQ-040', 'Cancela a requisição REQ-040' in t, t[:400])
    setv('aside[role=dialog] textarea[aria-label="Motivo do cancelamento"]','Replanejar'); btn('Confirmar cancelamento'); tt=toast()
    chk('OS-0425 toast', 'OS-0425 cancelada sem execução. Requisição REQ-040 cancelada' in tt, tt)
    t=ins(); chk('OS-0425 cancelada: Insumos não mostra REQ-040 ativa', 'REQ-040 · lote N26-03' not in t, t[:250])
    fechar()
    # 3) OS-0430 A liberar sem reserva: cancelar, depois Nova ordem c1|a1 deve emitir (cancelada não conta)
    abrir('OS-0430'); btn('Cancelar sem execução'); t=pan()
    chk('OS-0430 confirmação: nenhum insumo reservado', 'Nenhum insumo foi reservado.' in t, t[:400])
    btn('Confirmar cancelamento'); chk('OS-0430 motivo obrigatório', 'Informe o motivo do cancelamento.' in pan())
    setv('aside[role=dialog] textarea[aria-label="Motivo do cancelamento"]','   '); btn('Confirmar cancelamento'); chk('motivo só com espaços é recusado', 'Informe o motivo do cancelamento.' in pan())
    setv('aside[role=dialog] textarea[aria-label="Motivo do cancelamento"]','Plantio adiado'); btn('Confirmar cancelamento'); print('   toast:', toast())
    fechar()
    nova('S2627','c1','a1','2026-09-28'); tt=toast(); e=alerts()
    chk('cancelada não conta como duplicata: T1-A · Dessecação emite nova ordem', 'OS-0440 emitida' in tt and 'Já existe' not in e, (tt,e))
    fechar()
    # 4) chips e contagem
    cs=chips(); print('   chips:', cs)
    chk('Todas não conta canceladas (13 - 3 + 1 nova = 11)', cs[0]=='Todas 11' and cs[-1]=='Canceladas 3', cs)
    chip_fase('Canceladas'); chk('chip Canceladas lista as 3', sorted(ids())==['OS-0424','OS-0425','OS-0430'], ids())
    abrir('OS-0430'); t=pan(); chk('canceladas: painel sem ações', not temb('Cancelar sem execução') and not temb('Revisar versão') and not temb('Dispensar saldo'), t[:200])
    fechar(); chip_fase('Todas')
    # 5) OS-0431 cancelável; após cancelar, cabeçalho de impedidas?
    hdr0=J("document.body.innerText.match(/\\d+ em execução · \\d+ impedidas/)?.[0]||''")
    abrir('OS-0431'); btn('Cancelar sem execução'); setv('aside[role=dialog] textarea[aria-label="Motivo do cancelamento"]','Sem máquina'); btn('Confirmar cancelamento'); fechar()
    hdr1=J("document.body.innerText.match(/\\d+ em execução · \\d+ impedidas/)?.[0]||''")
    print('   cabeçalho antes/depois de cancelar OS-0431:', hdr0, '|', hdr1)
    # 6) OS-0421: apontar 90 ha, dispensar 70 ha (=20 %) -> saldo 0 -> Enviar para conferência
    reload(); abrir('OS-0421'); btn('Registrar apontamento'); setv('aside[role=dialog] input[type=date]','2026-09-26')
    setv('aside[role=dialog] input[aria-label="Área feita em hectares"]','90'); btn('Salvar apontamento'); print('   toast apont:', toast())
    t=pan(); print('   acum:', t[t.find('Acumulado'):][:80])
    btn('Dispensar saldo'); t=pan(); print('   form disp:', t[t.find('Área a dispensar'):][:260])
    v0=J("document.querySelector('aside[role=dialog] input[aria-label=\"Área a dispensar em hectares\"]').value"); print('   valor inicial:', v0)
    for val,exp in [('0','Informe a área a dispensar (maior que 0 ha).'),('abc','Informe a área a dispensar (maior que 0 ha).'),('71','Máximo 70 ha: é o saldo da ordem.'),('-5','Informe a área a dispensar (maior que 0 ha).')]:
        setv('aside[role=dialog] input[aria-label="Área a dispensar em hectares"]',val); btn('Confirmar dispensa'); a=J("[...document.querySelectorAll('aside[role=dialog] [role=alert]')].map(x=>x.innerText).join(' | ')")
        chk(f'dispensa {val!r}: {exp}', exp in (a or ''), a)
    setv('aside[role=dialog] input[aria-label="Área a dispensar em hectares"]','70'); setv('aside[role=dialog] textarea[aria-label="Motivo da dispensa"]','Faixa já tratada'); marca('Validação agronômica'); btn('Confirmar dispensa')
    tt=toast(); t=pan(); print('   toast disp:', tt)
    chk('dispensa até zerar o saldo: toast pede conferência', 'saldo 0 ha' in tt and 'Envie a ordem para conferência' in tt, tt)
    chk('saldo 0: próximo passo vira Enviar para conferência', temb('Enviar para conferência') and not temb('Registrar apontamento') and not temb('Dispensar saldo'), t[:400])
    chk('saldo 0: painel mostra Realizado · Dispensado · Saldo', 'Realizado 280 ha · Dispensado 70 ha · Saldo 0 ha (de 350 ha)' in t, t[t.find('APONTAMENTOS'):][:600])
    chk('saldo 0: sem turnos previstos', 'Previsto' not in t[t.find('APONTAMENTOS'):t.find('SITUAÇÃO')], t[t.find('APONTAMENTOS'):t.find('SITUAÇÃO')])
    kv=t[t.find('Saldo'):][:60]; print('   kv saldo:', kv)
    btn('Enviar para conferência'); t=pan(); print('   conf:', t[t.find('Enviar OS-0421'):][:160]); btn('Confirmar envio'); print('   toast:', toast())
    fechar(); l=linha('OS-0421'); print('   linha:', l)
    kanban(); print('   cartao:', cartao('OS-0421')); lista()
    # 7) dispensa decimal
    reload(); abrir('OS-0421'); btn('Dispensar saldo'); setv('aside[role=dialog] input[aria-label="Área a dispensar em hectares"]','10,5'); setv('aside[role=dialog] textarea[aria-label="Motivo da dispensa"]','x'); marca('Validação agronômica'); btn('Confirmar dispensa')
    tt=toast(); chk('dispensa decimal 10,5 aceita', 'Dispensados 10,5 ha' in tt and 'saldo 149,5 ha' in tt, tt)
    t=pan(); print('   acum dec:', t[t.find('Realizado 190'):][:90])
    fechar(); print('   linha dec:', linha('OS-0421')); kanban(); print('   cartao dec:', cartao('OS-0421')); lista()
    # 8) Nova ordem: T2 · Plantio e adubação de base (OS-0431 vem do plano SOJA-AT no T2)
    reload(); n0=len(ids()); nova('S2627','c3','a3','2026-09-28'); tt=toast(); e=alerts()
    print('   T2 plantio:', tt, '|', e)
    chk('T2 · Plantio e adubação de base não duplica a OS-0431', 'emitida' not in tt, (tt,e))
    fechar()
    # 9) dup com filtro de fase que esconde a ordem existente
    reload(); chip_fase('Encerradas'); nova('S2627','c1','a1','2026-09-28'); e=alerts(); btn('Abrir OS-0430'); t=pan()
    chk('Abrir OS-0430 com filtro Encerradas: painel abre a ordem', t.startswith('OS-0430'), t[:120])
    fechar()
    # 10) liberar OS-0430 (sem aprovar? não) -> OS-0419 Liberadas (água): cancelar
    reload(); abrir('OS-0419'); chk('OS-0419 (irrigação por política, Liberadas): Cancelar sem execução', temb('Cancelar sem execução'))
    btn('Cancelar sem execução'); print('   OS-0419 conf:', pan()[pan().find('Cancelar OS-0419'):][:200]); btn('Voltar'); fechar()
    # 11) Kanban OS-0431 selos
    kanban(); k=cartao('OS-0431'); chk('Kanban OS-0431 com os dois selos', 'Aprovada pelo agrônomo' in k and 'Falta máquina · Trator T1 bloqueado' in k, k)
    c.shot(os.path.join(HERE,'_probe','verif_os_kanban.png')); lista()
    chk('sem erro JS no fim', (J("window.__err||''") or '')=='')
finally:
    c.close(); srv.terminate()
print(f'\nRESULTADO: {len(OK)} ok · {len(FAIL)} falhas'); [print('  -',f) for f in FAIL]
