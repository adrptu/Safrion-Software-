# -*- coding: utf-8 -*-
"""Teste CDP das correções do passo 4 nos Planos de manutenção (PM.dc.html):
base "vencimento programado" no fechamento do ciclo · atalho Criar plano deixa o ativo "Sem vínculo" (sem plano duplicado) ·
marco negativo recusado · ativo em dois planos com o mesmo serviço recusado no vínculo · inativar com vencida pede confirmação ·
F5 reabre o plano · Vincular ativo some sem candidatos · Esc e Tab no painel · editar nome e Aplica-se a.
Uso: python3 ma_correcoes_pm_test.py   (lê _render; zera o cenário da manutenção em cada bloco)"""
import sys, os, time, json
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from cadc_lib import T, SETV

t=T(); J=t.J; FALHAS=[]
def ok(cond,msg):
    print(('  ok  ' if cond else '  FALHA ')+msg)
    if not cond: FALHAS.append(msg)
def toast(): return J("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).filter(Boolean).join(' | ')") or ''
def clk(txt,root=''):
    r=J(f"""(()=>{{const n=s=>(s||'').replace(/\\s+/g,' ').trim(); const els=[...document.querySelectorAll('{root} button, {root} a')].filter(e=>e.getClientRects().length); const e=els.find(x=>n(x.innerText)==={json.dumps(txt)})||els.find(x=>n(x.innerText).startsWith({json.dumps(txt)}))||els.find(x=>n(x.getAttribute('aria-label'))==={json.dumps(txt)}); if(!e) return 'NAO ACHEI'; e.click(); return 'ok';}})()""")
    time.sleep(.4); return r
def setv(sel,val): r=J(f"({SETV})({json.dumps(sel)},{json.dumps(val)})"); time.sleep(.2); return r
def pan(): return J("(document.querySelector('aside[role=dialog]')||{}).innerText||''") or ''
def key(k,code,vk,shift=False):
    m=8 if shift else 0
    t.c.call('Input.dispatchKeyEvent',{'type':'keyDown','key':k,'code':code,'windowsVirtualKeyCode':vk,'modifiers':m}); t.c.call('Input.dispatchKeyEvent',{'type':'keyUp','key':k,'code':code,'windowsVirtualKeyCode':vk,'modifiers':m}); time.sleep(.05)
def novo(): J("localStorage.clear()")
def ir(f):
    """navegação rápida: espera o documento novo (marca some) e o corpo renderizado; hash na mesma página volta em até 3 s"""
    J("window.__velho=1"); t.c.call('Page.navigate',{'url':f'http://127.0.0.1:{t.p}/{f}'})
    for _ in range(30):
        time.sleep(.1)
        try:
            if J("!window.__velho && document.readyState==='complete' && document.body && document.body.innerText.length>50"): break
        except Exception: pass
    time.sleep(.45)
t.goto=ir
def sem_erro(tela): e=t.errs(); ok(not e, f'{tela}: sem erro de JS {e[:160]}')
try:
    t.goto('PM.dc.html'); novo()
    # 1 · base "vencimento programado": próxima revisão conta do vencimento (20/09/2026 + 365 d), não da execução (23/09)
    t.goto('PM.dc.html#PM-05'); time.sleep(.3); sem_erro('PM#PM-05')
    clk('Revisão pré-plantio','main'); setv('#sv_base','prog'); clk('Salvar','aside'); clk('Revisar e publicar','main'); clk('Publicar v2','main'); clk('Gerar ordem','main'); g=toast()
    t.goto('MA-04.dc.html#OM-0235'); time.sleep(.4); clk('Liberar serviço','aside'); clk('Iniciar serviço','aside'); clk('Marcar pendentes como feitas','aside')
    setv('#om-leitura','890'); clk('Concluir serviço','aside'); c=toast()
    ok('OM-0235 gerada' in g and 'em 20/09/2027' in c and 'conta do vencimento programado' in c, f'base programada: próxima em 20/09/2027 · {c[:140]}')
    # 2 · atalho Criar plano: o ativo sai de "Sem plano" e o 2º clique não duplica; o endereço passa a #PM-11
    novo(); t.goto('MA-01.dc.html'); time.sleep(.2)
    J("(()=>{const r=[...document.querySelectorAll('[role=table]')[0].querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.indexOf('Distribuidor')>=0); [...r.querySelectorAll('a')].find(a=>a.innerText.trim()==='Criar plano').click();})()"); time.sleep(1.4)
    p0=pan(); clk('Salvar','aside'); h=J("location.hash"); s1=toast()
    t.goto('MA-01.dc.html'); l=t.anyrow(0,'Distribuidor') or ''
    t.goto('PM.dc.html'); sp=J("[...document.querySelectorAll('main button[aria-label^=\"Criar plano para\"]')].map(b=>b.innerText)")
    ok('Novo plano' in p0 and 'PM-11 criado' in s1 and h=='#PM-11' and 'Sem vínculo' in l and 'Vincular · PM-11' in l and 'Sem plano' not in l and len(sp)==3 and not any('Distribuidor' in x for x in sp),
       f'atalho Criar plano: Distribuidor fica Sem vínculo · Vincular · PM-11, hash {h}, sem plano {len(sp)} · {l[:90]}')
    # 3 · marco negativo é recusado no vínculo
    t.goto('PM.dc.html#PM-11'); time.sleep(.3)
    clk('Incluir serviço','main'); setv('#sv_nome','Revisão 100 h'); setv('#sv_h','100'); setv('#sv_tempo','2'); setv('#sv_esp','Mecânico'); clk('Salvar','aside')
    setv('#pm-tk-s1','Lubrificar pontos de graxa'); clk('Incluir tarefa','main')
    clk('Vincular ativo','main'); setv('#vk_data','2026-09-01'); setv('#vk_leit','-50'); clk('Salvar','aside'); e=pan()
    ok('Zero ou mais.' in e and J("!!document.querySelector('aside[role=dialog]')"), 'vincular: leitura negativa recusada no campo')
    setv('#vk_leit','600'); clk('Salvar','aside'); v1=toast()
    ok('Distribuidor 3 t vinculado ao PM-11' in v1 and not J("!!document.querySelector('aside[role=dialog]')"), f'vincular: leitura 600 aceita · {v1[:80]}')
    # 4 · ativo em dois planos com o mesmo serviço: aviso no novo plano e vínculo recusado
    novo(); t.goto('PM.dc.html'); clk('Novo plano')
    setv('#np_nome','MF 7719 cópia'); setv('#np_tipo','modelo'); setv('#np_modelo','MF 7719'); av=pan(); setv('#np_base','PM-01'); clk('Salvar','aside')
    clk('Vincular ativo','main'); setv('#vk_data','2026-09-02'); setv('#vk_leit','2793'); clk('Salvar','aside'); e=pan()
    ok('Trator 02 já está no PM-01' in av and 'já faz Revisão 250 h pelo PM-01' in e, f'dois planos, mesmo serviço: aviso ao criar e vínculo recusado · {e[-140:]}')
    J("document.querySelector('aside[role=dialog] button[aria-label=Fechar]').click()"); time.sleep(.3); clk('Descartar alterações','aside')
    # 5 · inativar plano com vencida pede confirmação; Manter ativo não muda nada
    novo(); t.goto('PM.dc.html#PM-02'); time.sleep(.3); clk('Inativar plano','main'); a=J("[...document.querySelectorAll('main [role=alert]')].map(x=>x.innerText).join(' ')") or ''
    est=J("__man.manGet().planos['PM-02'].estado"); clk('Manter ativo','main')
    ok('Inativar mesmo assim' in a and 'Trator 03' in a and est=='Ativo' and J("__man.manGet().planos['PM-02'].estado")=='Ativo', f'inativar com vencida pede confirmação · {a[:100]}')
    # 6 · F5 reabre o plano aberto pelo cartão
    t.goto('PM.dc.html'); J("document.querySelector('main button[aria-label^=\"Abrir plano PM-04\"]').click()"); time.sleep(.4); h=J("location.hash")
    J("window.__velho=1; location.reload()"); time.sleep(1.2); h2=J("(document.querySelector('main h2')||{}).innerText||''")
    ok(h=='#PM-04' and h2.startswith('PM-04'), f'F5 reabre o plano: hash {h} · {h2}')
    # 7 · Vincular ativo some quando todos já estão vinculados
    ok(not J("[...document.querySelectorAll('main button')].some(b=>b.innerText.trim()==='Vincular ativo')"), 'PM-04: sem candidatos, sem botão Vincular ativo')
    # 8 · painel do serviço: Tab gira dentro; Esc com o foco fora fecha
    clk('Revisão 250 h','main'); time.sleep(.3)
    for _ in range(30): key('Tab','Tab',9)
    dentro=J("!!document.activeElement.closest('#sv-painel')")
    J("document.querySelector('main h2').setAttribute('tabindex','-1'); document.querySelector('main h2').focus()"); key('Escape','Escape',27); time.sleep(.3)
    ok(dentro and not J("!!document.querySelector('#sv-painel')"), f'painel do serviço: Tab preso no painel ({dentro}) e Esc fora fecha')
    # 9 · editar nome e Aplica-se a
    clk('Editar plano','main'); setv('#np_nome','Pulverizador Uniport 3030 · revisões 250/500 h'); clk('Salvar','aside'); s9=toast()
    ok('PM-04 salvo' in s9 and J("__man.manGet().planos['PM-04'].nome")=='Pulverizador Uniport 3030 · revisões 250/500 h', f'editar plano: nome salvo · {s9[:80]}')
    sem_erro('PM fim')
finally:
    t.c.close(); t.srv.terminate()
print('FALHAS:',len(FALHAS)); [print(' -',f) for f in FALHAS]
if FALHAS: raise AssertionError('; '.join(FALHAS))
