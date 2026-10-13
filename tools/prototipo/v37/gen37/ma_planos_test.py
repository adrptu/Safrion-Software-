# -*- coding: utf-8 -*-
"""Teste CDP dos Planos de manutenção girando as preventivas (pedido de 02/10/2026):
menu · biblioteca de planos · vencimentos calculados (paridade JS × Python) · gerar sem duplicar · falta de peça trava a liberação ·
jornada da OM-0234 (conflito vira aviso → iniciar → checklist + leitura → concluir fecha o ciclo) · publicar v+1 sem mudar a ordem aberta ·
leitura do abastecimento muda a situação · leitura menor vira troca de contador a confirmar.
Uso: python3 ma_planos_test.py   (lê _render; o cenário da manutenção é zerado no início)"""
import sys, os, time, json
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from cadc_lib import T, SETV
import dados_manutencao as DM

t=T(); J=t.J; FALHAS=[]
def ok(cond,msg):
    print(('  ok  ' if cond else '  FALHA ')+msg)
    if not cond: FALHAS.append(msg)
def toast(): return J("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).filter(Boolean).join(' | ')") or ''
def clk(txt,root=''):
    r=J(f"""(()=>{{const n=s=>(s||'').replace(/\\s+/g,' ').trim(); const els=[...document.querySelectorAll('{root} button, {root} a')]; const e=els.find(x=>n(x.innerText)==={json.dumps(txt)})||els.find(x=>n(x.innerText).startsWith({json.dumps(txt)})); if(!e) return 'NAO ACHEI'; e.click(); return 'ok';}})()""")
    time.sleep(.4); return r
def setv(sel,val): r=J(f"({SETV})({json.dumps(sel)},{json.dumps(val)})"); time.sleep(.2); return r
def pan(): return J("(document.querySelector('aside[role=dialog]')||{}).innerText||''") or ''
def feitas():   # CTL-3 (R-D4): sem ação em massa; cada tarefa sem resposta recebe "Feito", uma a uma (PRD 54.2), com quem e hora
    n=0
    for _ in range(30):
        r=J("(()=>{const g=[...document.querySelectorAll('aside [role=group]')].find(g=>{const bs=[...g.querySelectorAll('button')]; return bs.some(b=>b.innerText.trim()==='Feito')&&!bs.some(b=>b.getAttribute('aria-pressed')==='true');}); if(!g) return false; [...g.querySelectorAll('button')].find(b=>b.innerText.trim()==='Feito').click(); return true;})()"); time.sleep(.3)
        if not r: break
        n+=1
    return n
def sem_erro(tela): e=t.errs(); ok(not e, f'{tela}: sem erro de JS {e[:160]}')
try:
    t.goto('PM.dc.html'); J("localStorage.clear()"); t.goto('PM.dc.html'); sem_erro('PM')
    # 1 · menu: Planos de manutenção é o 1º item; MA-03 virou Vencimentos e paradas (sem nome duplicado)
    m=J("[...document.querySelectorAll('nav[aria-label=Menu] a')].map(a=>a.innerText.trim()+'|'+a.getAttribute('href'))")
    i=m.index('Planos de manutenção|PM.dc.html') if 'Planos de manutenção|PM.dc.html' in m else -1
    ok(i>=0 and m[i+1]=='Ativos e disponibilidade|MA-01.dc.html' and 'Vencimentos e paradas|MA-03.dc.html' in m and not any(x.startswith('Plano de manutenção|') for x in m),
       'menu: Planos de manutenção primeiro na Manutenção; MA-03 = Vencimentos e paradas')
    # 2 · biblioteca: 10 planos, 4 ativos sem plano, PM-02 vencido
    cards=J("[...document.querySelectorAll('main button[aria-label^=\"Abrir plano\"]')].map(b=>b.innerText.replace(/\\s+/g,' '))")
    sem=J("[...document.querySelectorAll('main button[aria-label^=\"Criar plano para\"]')].map(b=>b.innerText)")
    ok(len(cards)==10 and len(sem)==4 and any('MF 4292' in c and '1 vencida' in c for c in cards), f'biblioteca: 10 planos, 4 sem plano, PM-02 com 1 vencida ({len(cards)}, {len(sem)})')
    # 3 · paridade do vencimento JS × Python
    js=J("__man.manLinhas(__man.manGet()).filter(l=>l.s).map(l=>[l.pid,l.aid,l.sid,l.x.sit,l.x.prev])")
    py=sorted([x['pid'],x['aid'],x['sid'],x['sit'],x['prev']] for x in DM.linhas())
    ok(sorted(js)==py, f'vencimento: manVenc (JS) = vencimento() (Python) nos {len(py)} ativo × serviço')
    # 4 · Vencimentos e paradas: 2 vencidas, 3 sem ordem, primária pelo estado
    t.goto('MA-03.dc.html'); sem_erro('MA-03')
    k=J("[...document.querySelectorAll('main div')].filter(d=>/^(VENCIDAS|SEM ORDEM)$/.test(d.innerText.trim())).map(d=>d.parentElement.innerText.replace(/\\s+/g,' '))")
    prim=J("[...document.querySelectorAll('header button')].map(b=>b.innerText.trim()).filter(x=>x.startsWith('Gerar'))")
    ok(any(x.startswith('VENCIDAS 2') for x in k) and any(x.startswith('SEM ORDEM 3') for x in k) and prim==['Gerar 3 ordens preventivas'], f'MA-03: 2 vencidas · 3 sem ordem · primária Gerar 3 ordens preventivas {k} {prim}')
    # 5 · gerar sem duplicar
    clk('Gerar 3 ordens preventivas'); tt=toast()
    n1=J("Object.keys(__man.manGet().oms).length"); r=J("(()=>{ const M=__man; const c=M.manClone(M.manGet()); return M.manGerarTodas(c).msg; })()"); n2=J("Object.keys(__man.manGet().oms).length")
    ok('OM-0235, OM-0236, OM-0237' in tt and 'OM-0235 com Falta peça' in tt and n1==n2==8 and 'Nenhuma ordem a gerar' in r, f'gerar: 3 ordens, sem duplicar no 2º clique · {tt[:90]}')
    ok('Ver ordens de manutenção' in J("document.querySelector('header').innerText"), 'MA-03: sem nada a gerar, a primária vira Ver ordens de manutenção')
    # 6 · OM-0235: checklist do plano e falta de peça trava a liberação
    t.goto('MA-04.dc.html#OM-0235'); time.sleep(.4); sem_erro('MA-04')
    p=pan(); r=J("(()=>{ try{ const M=__man; M.manLiberar(M.manClone(M.manGet()),'OM-0235'); return 'liberou'; }catch(e){ return e.message; } })()")
    ok(p.startswith('OM-0235 · Trator 03') and p.count('Sem resposta')==5 and 'Falta peça' in p and 'Solicitar compra' in p and 'Filtro de óleo MF 4292' in r, 'OM-0235: 5 tarefas do plano, Falta peça e liberar bloqueado')
    J("document.querySelector('aside[role=dialog] button[aria-label=Fechar]').click()"); time.sleep(.3)
    # 7 · OM-0234: conflito com a produção é aviso confirmado
    clk('Liberar serviço'); a=toast(); avs='Liberar mesmo assim' in pan()
    clk('Liberar mesmo assim','aside'); b=toast()
    ok('conflito com a OS-0420' in a and avs and 'liberada para a oficina' in b and 'reservado' in b, 'OM-0234: conflito vira aviso; liberar mesmo assim reserva as peças')
    clk('Iniciar serviço','aside'); clk('Concluir serviço','aside'); e1=toast()
    feitas(); setv('#om-leitura','2900'); clk('Concluir serviço','aside'); e2=toast()
    ok('5 tarefas sem resposta' in e1 and 'menor que a última' in e2, 'concluir exige checklist respondido e leitura não menor que a última')
    setv('#om-leitura','2995'); clk('Concluir serviço','aside'); c=toast(); p=pan()
    ok('em conferência' in c and 'ciclo fechado' in c and '3.245 h' in c and p.startswith('OM-0234') and 'Em conferência' in p, f'concluir fecha o ciclo: próxima em 3.245 h · {c[:110]}')
    # 8 · plano: Trator 02 volta a Em dia a partir da execução (horímetro não zera)
    t.goto('PM.dc.html#PM-01'); time.sleep(.4); sem_erro('PM etapa 2')
    l=t.anyrow(0,'Revisão 250 h') or ''
    ok('Em dia' in l and '3.245 h' in l and 'OM-0234' in l and '2.995 h' in l, f'PM-01: Trator 02 Em dia, próxima 3.245 h, última 2.995 h pela OM-0234 · {l[:140]}')
    # 9 · publicar v4 não muda a ordem aberta (OM-0237 da v3 do PM-07)
    t.goto('PM.dc.html#PM-07'); time.sleep(.4); clk('Preventiva mensal','main'); setv('#sv_td','2'); clk('Salvar','aside'); r1=toast()
    clk('Revisar e publicar','main'); clk('Publicar v4','main'); r2=toast()
    o=J("(()=>{ const c=__man.manGet(); const o=c.oms['OM-0237']; return [o.ver,o.chk.length,c.planos['PM-07'].versao]; })()")
    ok('Rascunho v4 criado' in r1 and 'PM-07 v4 publicada' in r2 and 'OM-0237 segue na v3' in r2 and o==[3,5,4], f'publicar v4: OM-0237 segue na v3 · {r2[:100]}')
    # 10 · leitura do abastecimento muda a situação; leitura menor vira troca de contador a confirmar
    t.goto('MA-05.dc.html'); sem_erro('MA-05')
    def abast(ativo,cont):
        clk('Registrar abastecimento'); setv('aside[role=dialog] select[id$=_ativo]',ativo); setv('aside[role=dialog] select[id$=_tq]','Sede · D-118')
        setv('aside[role=dialog] input[id$=_vol]','150'); setv('aside[role=dialog] input[id$=_cont]',cont); setv('aside[role=dialog] select[id$=_op]','Beto'); setv('aside[role=dialog] input[id$=_evid]','foto')
        clk('Salvar','aside'); return toast()
    a1=abast('Trator 04 · JD 5078E','3530'); a2=abast('Comboio CB-01','48100')
    ok('AB-1043' in a1 and 'Revisão 250 h: vence em breve' in a1 and 'troca de contador' in a2, f'MA-05: 3.530 h deixa o Trator 04 vencendo em breve; 48.100 km < 48.200 km pede confirmação · {a1[:80]}')
    t.goto('MA-03.dc.html'); l4=t.anyrow(0,'Trator 04') or ''; lc=t.anyrow(0,'Comboio') or ''
    ok('Vence em breve' in l4 and '3.530 h' in l4 and 'Leitura a confirmar' in lc and '48.200 km' in lc, 'MA-03: Trator 04 recalculado; comboio mantém 48.200 km com leitura a confirmar')
    t.c.shot(os.path.join(os.path.dirname(os.path.abspath(__file__)),'_probe','manut','ma_planos_test_fim.png'))
finally:
    t.c.close(); t.srv.terminate()
print('FALHAS:',len(FALHAS)); [print(' -',f) for f in FALHAS]
if FALHAS: raise AssertionError('; '.join(FALHAS))
