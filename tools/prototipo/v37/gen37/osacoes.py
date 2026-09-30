# -*- coding: utf-8 -*-
"""Teste real (Chrome) — O.S. 26/09: cancelar sem execução e dispensar saldo (os-04), Nova ordem sem duplicar (os-05),
OS-0431 aprovada com falta de máquina (os-06), selos e percentual (os-07)."""
import sys, os, time, subprocess, json
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from cdp import Chrome
from journeys import free
HERE=os.path.dirname(os.path.abspath(__file__)); R=sys.argv[1] if len(sys.argv)>1 else os.path.join(HERE,'_render')
p=free(); srv=subprocess.Popen(['python3','-m','http.server',str(p),'--bind','127.0.0.1','--directory',R],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(.8)
c=Chrome(port=free()); J=c.js; OK=[]; FAIL=[]
def chk(n,cond,info=''): (OK if cond else FAIL).append(n); print(('  ok  ' if cond else '  FALHOU ')+n+(' · '+str(info)[:240] if info!='' else ''))
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
try:
    c.size(1440,1000); c.goto(f'http://127.0.0.1:{p}/OS.dc.html',wait=1.3)
    chk('sem erro JS', (J("window.__err||''") or '')=='')
    # ---------- os-07: selos e percentual ----------
    l=linha('OS-0421'); chk('lista mostra percentual: 190 / 350 ha · 54 % · saldo 160 ha', '190 / 350 ha · 54 %' in l and 'saldo 160 ha' in l, l)
    chk('OS-0430 com selo Aguardando agrônomo', 'Aguardando agrônomo' in linha('OS-0430'), linha('OS-0430'))
    l=linha('OS-0420'); chk('OS-0420 com os dois selos (impedida + revisão de saldo)', 'Impedida · ativo bloqueado' in l and 'Revisão de saldo pendente · v3' in l, l)
    kanban(); k=cartao('OS-0421'); chk('cartão do Kanban: 190/350 ha · 54 % · saldo 160 ha', '190/350 ha · 54 % · saldo 160 ha' in k, k)
    chk('cartão da OS-0420 com Revisão de saldo pendente · v3', 'Revisão de saldo pendente · v3' in cartao('OS-0420'), cartao('OS-0420'))
    lista()
    # ---------- os-06: OS-0431 aprovada, falta máquina ----------
    l=linha('OS-0431'); chk('OS-0431 com selos Aprovada pelo agrônomo e Falta máquina · Trator T1 bloqueado', 'Aprovada pelo agrônomo' in l and 'Falta máquina · Trator T1 bloqueado' in l, l)
    cor=J("""(()=>{const c=(id,t)=>{ const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.trim().startsWith(id)); const s=[...r.querySelectorAll('span')].filter(x=>x.innerText.trim().startsWith(t)).pop(); return getComputedStyle(s).color; };
      return [c('OS-0431','Falta máquina'), c('OS-0420','Impedida'), c('OS-0430','Aguardando')];})()""")
    chk('falta de máquina da OS-0431 continua vermelha (mesma cor de Impedida)', cor and cor[0]==cor[1] and cor[0]!=cor[2], cor)
    ov=J("(()=>{const t=document.querySelector('[role=table]').parentElement; return [t.scrollWidth,t.clientWidth];})()"); chk('lista cabe sem rolagem horizontal', ov[0]<=ov[1]+1, ov)
    chk('cabeçalho conta 2 impedidas (OS-0420 e OS-0431)', '2 em execução · 2 impedidas' in J("document.body.innerText"))
    abrir('OS-0431'); t=pan()
    chk('OS-0431: versão v1 aprovada, sem pedir nova revisão', 'REC-014 v2 · v1 aprovada' in t and not temb('Revisar versão'), t[:300])
    chk('OS-0431: liberar bloqueado por falta de máquina, dono PCP', 'Liberar bloqueado: Trator T1' in t and 'Quem resolve: PCP' in t and not temb('Liberar para execução'))
    chk('OS-0431: situação cita a retirada de Liberadas e a aprovação preservada, sem citar o Trator 02', 'Retirada de Liberadas em 23/09' in t and 'Aprovação da v1 preservada' in t and 'Confirmar substituto' in t and 'Trator 02' not in t.split('SITUAÇÃO ATUAL')[-1].split('ORIGEM')[0], t[-500:])
    chk('OS-0431: origem mostra liberada e retirada pela INSP-105', 'Liberada e retirada em 23/09 pela INSP-105' in t)
    chk('OS-0431: pode ser cancelada (sem realizado)', temb('Cancelar sem execução') and not temb('Dispensar saldo'))
    fechar()
    # ---------- os-04: cancelar sem execução ----------
    abrir('OS-0424'); chk('OS-0424 (Liberadas, sem realizado): Cancelar sem execução, sem Dispensar', temb('Cancelar sem execução') and not temb('Dispensar saldo'))
    btn('Cancelar sem execução'); t=pan()
    chk('confirmação diz o que acontece com a reserva', 'Cancelar OS-0424 sem execução' in t and 'Libera a reserva de 65 L do lote F26-02' in t, t[:400])
    btn('Confirmar cancelamento'); chk('motivo é obrigatório', 'Informe o motivo do cancelamento.' in pan())
    setv('aside[role=dialog] textarea[aria-label="Motivo do cancelamento"]','Chuva prevista para a janela; nova ordem após a reprogramação')
    btn('Confirmar cancelamento'); tt=toast()
    chk('toast: cancelada e reserva de 65 L do F26-02 liberada', 'OS-0424 cancelada sem execução' in tt and 'Reserva de 65 L do lote F26-02 liberada' in tt, tt)
    t=pan(); chk('painel: Canceladas, somente consulta, sem ações', 'Canceladas' in t and 'somente consulta' in t and not temb('Cancelar sem execução') and not temb('Iniciar execução'), t[:300])
    fechar()
    chk('sai da lista (Todas)', 'OS-0424' not in ids() and len(ids())==12, ids())
    cs=chips(); chk('chip Canceladas depois de Encerradas, com 1', cs[-1]=='Canceladas 1' and cs[-2].startswith('Encerradas') and cs[0]=='Todas 12', cs)
    chip_fase('Canceladas'); chk('chip Canceladas mostra a OS-0424', ids()==['OS-0424'] and 'Canceladas' in linha('OS-0424'), (ids(),linha('OS-0424')))
    chip_fase('Todas'); kanban(); chk('sai do quadro (Kanban)', cartao('OS-0424')=='' and J("document.querySelectorAll('[aria-label=\"Kanban das ordens\"] [role=button]').length")==12)
    lista()
    # ---------- os-04: dispensar saldo ----------
    abrir('OS-0420'); chk('OS-0420 (com realizado): Dispensar saldo, nunca Cancelar', temb('Dispensar saldo') and not temb('Cancelar sem execução'))
    btn('Dispensar saldo'); t=pan(); chk('formulário de dispensa com limite de 20 %', 'Até 20 % da área (20 ha)' in t and 'realizado de 30 ha fica preservado' in t, t[:500])
    setv('aside[role=dialog] textarea[aria-label="Motivo da dispensa"]','Área alagada na baixada'); marca('Validação agronômica')
    btn('Confirmar dispensa'); t=pan()
    chk('OS-0420: 70 ha recusados (70 % acima de 20 % · exige Direção)', '70 ha = 70 % acima de 20 % · exige Direção.' in t, t[:600])
    btn('Voltar'); chk('recusa não muda o saldo (70 ha)', 'saldo 70 ha' in linha('OS-0420') and 'dispensado' not in linha('OS-0420'), linha('OS-0420'))
    fechar(); abrir('OS-0421'); chk('OS-0421 em execução: Dispensar saldo, sem Cancelar', temb('Dispensar saldo') and not temb('Cancelar sem execução'))
    btn('Dispensar saldo'); setv('aside[role=dialog] input[aria-label="Área a dispensar em hectares"]','40')
    btn('Confirmar dispensa'); chk('motivo obrigatório', 'Informe o motivo da dispensa.' in pan())
    setv('aside[role=dialog] textarea[aria-label="Motivo da dispensa"]','Faixa de 40 ha já tratada na aplicação anterior')
    btn('Confirmar dispensa'); chk('validação agronômica obrigatória', 'Marque a validação agronômica.' in pan())
    marca('Validação agronômica'); btn('Confirmar dispensa'); tt=toast(); t=pan()
    chk('dispensa dentro do limite registrada', 'Dispensados 40 ha da OS-0421' in tt and 'realizado 190 ha preservado' in tt and 'saldo 120 ha' in tt, tt)
    chk('painel: Realizado 190 · Dispensado 40 · Saldo 120', 'Realizado 190 ha · Dispensado 40 ha · Saldo 120 ha (de 350 ha)' in t, t[t.find('APONTAMENTOS'):][:700])
    ap=J("[...document.querySelectorAll('aside[role=dialog] [style*=\"grid-template-columns: 64px\"]')].slice(1).map(r=>r.innerText.replace(/\\s+/g,' '))") or []
    pv=[x for x in ap if 'Previsto' in x]
    chk('turnos previstos acompanham o saldo (50 + 50 + 20)', len(pv)==3 and 'prev. 50 ha' in pv[0] and 'prev. 50 ha' in pv[1] and 'prev. 20 ha' in pv[2], ap)
    chk('lista: saldo 120 ha e dispensado 40 ha', '190 / 350 ha · 54 % saldo 120 ha dispensado 40 ha' in linha('OS-0421'), linha('OS-0421'))
    btn('Dispensar saldo'); setv('aside[role=dialog] input[aria-label="Área a dispensar em hectares"]','31'); setv('aside[role=dialog] textarea[aria-label="Motivo da dispensa"]','x'); marca('Validação agronômica'); btn('Confirmar dispensa')
    chk('limite é acumulado (40 + 31 = 71 ha > 70 ha)', '71 ha = 20,3 % acima de 20 % · exige Direção.' in pan(), pan()[:500])
    btn('Voltar'); fechar()
    # ---------- os-05: Nova ordem não duplica ordem gerada pelo plano ----------
    n0=len(ids())
    J("(()=>{const b=[...document.querySelectorAll('button')].find(b=>b.innerText.trim()==='Nova ordem'); b.click();})()"); time.sleep(.4)
    setv('#nv_saf','S2627'); setv('#nv_cult','c1'); setv('#nv_atv','a1'); setv('#nv_jan','2026-09-25')
    btn('Emitir ordem'); e=J("[...document.querySelectorAll('aside [role=alert]')].map(x=>x.innerText).join(' | ')") or ''
    chk('T1-A · Dessecação pré-plantio: erro no campo aponta a OS-0430', 'Já existe OS-0430 para esta atividade neste cultivo.' in e, e)
    chk('botão Abrir OS-0430 no lugar da instrução', temb('Abrir OS-0430'))
    btn('Abrir OS-0430'); t=pan()
    chk('Abrir OS-0430 fecha o formulário e abre a ordem existente, sem emitir', t.startswith('OS-0430') and 'Nova ordem' not in t[:40] and len(ids())==n0 and 'OS-0440' not in ids(), (t[:80],len(ids())))
    fechar()
    J("(()=>{const b=[...document.querySelectorAll('button')].find(b=>b.innerText.trim()==='Nova ordem'); b.click();})()"); time.sleep(.4)
    setv('#nv_saf','S2627'); setv('#nv_cult','c9'); setv('#nv_atv','k1'); setv('#nv_jan','2026-10-15'); btn('Emitir ordem')
    e=J("[...document.querySelectorAll('aside [role=alert]')].map(x=>x.innerText).join(' | ')") or ''
    chk('C1 · Adubação 1ª parcela: aponta a OS-0425', 'Já existe OS-0425' in e and temb('Abrir OS-0425'), e)
    setv('#nv_atv','k2'); chk('trocar a atividade tira o botão da duplicata', not temb('Abrir OS-0425'))
    btn('Emitir ordem'); tt=toast(); chk('atividade sem ordem emite normalmente (OS-0440)', 'OS-0440 emitida em A liberar' in tt, tt)
    c.shot(os.path.join(HERE,'_probe','os_acoes.png'))
    chk('sem erro JS no fim', (J("window.__err||''") or '')=='')
finally:
    c.close(); srv.terminate()
print(f'\nRESULTADO: {len(OK)} ok · {len(FAIL)} falhas'); [print('  -',f) for f in FAIL]
