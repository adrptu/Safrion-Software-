# -*- coding: utf-8 -*-
"""Teste CDP do módulo Irrigação (IR-01..04 + IR-03det): faixa de etapas, água sem aprovação (passadas, janela, conflito),
ciclo da OS-0419 até Encerradas com recibos, reclassificação na própria ordem (fertirrigação vai ao agrônomo) e limites do equipamento."""
import sys, os, time, subprocess, json
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from cdp import Chrome
from journeys import free
R=os.path.join(os.path.dirname(os.path.abspath(__file__)),'_render'); p=free()
srv=subprocess.Popen(['python3','-m','http.server',str(p),'--bind','127.0.0.1','--directory',R],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(0.8)
c=Chrome(port=free()); J=c.js
CLK="""((t,root)=>{const r=root?document.querySelector(root):document; const n=s=>(s||'').replace(/\\s+/g,' ').trim(); const els=[...r.querySelectorAll('button,a')]; const e=els.find(x=>n(x.innerText)===t)||els.find(x=>n(x.innerText).startsWith(t)); if(!e) return 'NÃO ACHEI: '+t; e.click(); return 'ok';})"""
SETV="""((sel,val)=>{const i=document.querySelector(sel); const P=i.tagName==='SELECT'?HTMLSelectElement.prototype:(i.tagName==='TEXTAREA'?HTMLTextAreaElement.prototype:HTMLInputElement.prototype); Object.getOwnPropertyDescriptor(P,'value').set.call(i,val); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true}));})"""
T=lambda: J("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).filter(Boolean).join(' | ')")
ROW=lambda txt: J(f"""(()=>{{const r=[...document.querySelectorAll('[role=row]')].find(r=>r.innerText.replace(/\\s+/g,' ').indexOf({json.dumps(txt)})>=0); return r?r.innerText.replace(/\\s+/g,' '):'—';}})()""")
def clk(t,root=None): r=J(f"({CLK})({json.dumps(t)},{json.dumps(root)})"); time.sleep(.45); return r
def rowclk(txt,btn):
    r=J(f"""(()=>{{const r=[...document.querySelectorAll('[role=row]')].find(r=>r.innerText.replace(/\\s+/g,' ').indexOf({json.dumps(txt)})>=0); if(!r) return 'sem linha'; const b=[...r.querySelectorAll('button,a')].find(b=>b.innerText.trim().startsWith({json.dumps(btn)})); if(!b) return 'sem botão '+{json.dumps(btn)}; b.click(); return 'ok';}})()"""); time.sleep(.45); return r
def rowopen(txt):
    J(f"""(()=>{{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.replace(/\\s+/g,' ').indexOf({json.dumps(txt)})>=0); (r.querySelector('[role=cell] span')||r).click();}})()"""); time.sleep(.4)
ok=[];
def chk(nome,cond): ok.append((nome,bool(cond))); print(('✓ ' if cond else '✗ ')+nome)
try:
    c.size(1440,1000)
    # ---------- faixa de etapas em todas as telas ----------
    for t,cur in [('IR-01',1),('IR-02',2),('IR-03',3),('IR-03det',3),('IR-04',4)]:
        c.goto(f'http://127.0.0.1:{p}/{t}.dc.html'); time.sleep(.3)
        nav=J("[...document.querySelectorAll('nav[aria-label=\"Etapas do processo\"] a')].map(a=>a.getAttribute('href')+'|'+(a.getAttribute('aria-current')||''))")
        chk(f'{t}: faixa com 4 etapas e atual = {cur}', len(nav)==4 and nav[cur-1].endswith('|step') and [x.split('|')[0] for x in nav]==['IR-01.dc.html','IR-02.dc.html','IR-03.dc.html','IR-04.dc.html'])
        chk(f'{t}: sem botão Editar', J("![...document.querySelectorAll('button,a')].some(b=>/^Editar/.test(b.innerText.trim()))"))
    # ---------- IR-01: memória do déficit e limites do equipamento ----------
    c.goto(f'http://127.0.0.1:{p}/IR-01.dc.html'); time.sleep(.3)
    r=ROW('Milho V10 · 80 ha'); print('   ', r); chk('IR-01: Pivô 2 fecha 5,0 + 38,5 − 12,0 − 20,3 = 11,2 e mostra a necessidade', all(x in r for x in ['5,0 mm','38,5 mm','12,0 mm','20,3 mm','11,2 mm','Irrigar 10,81 mm hoje','2 passadas']))
    chk('IR-01: nenhuma menção a política, exceção ou revisão da água', J("!/Fora da|exceç|PA-07/.test(document.body.innerText)"))
    rowopen('Milho V10 · 80 ha'); orig=J("[...document.querySelectorAll('aside[role=dialog] div')].map(d=>d.innerText).join(' ')"); chk('IR-01: linha abre memória e origens (1,5 mm em 80 ha)', '1,5 mm equivalentes em 80 ha' in orig and 'Memória' in orig)
    clk('Fechar','aside[role=dialog]')
    rowopen('Sonda + estação'); ids=J("[...document.querySelectorAll('aside[role=dialog] input:not([readonly])')].map(i=>i.id)"); print('    campos limites:',ids)
    J(f"({SETV})('#fx_g_pol_lmax','4,5')"); time.sleep(.2); clk('Salvar','aside[role=dialog]'); time.sleep(.3); t=T(); print('   ',t)
    chk('IR-01: limite menor divide o próximo ciclo em mais passadas', '3 passadas' in t and '3 passadas' in ROW('Milho V10 · 80 ha estação'))
    # ---------- IR-02: sem aprovação; janela, conflito e passadas ----------
    c.goto(f'http://127.0.0.1:{p}/IR-02.dc.html'); time.sleep(.3)
    print('   estado:', J("document.querySelector('header').innerText.replace(/\\s+/g,' ')")[-80:])
    chk('IR-02: OS-0422 em 2 passadas, pendência é a janela (sem revisão)', '2 passadas de 6,75 mm' in ROW('OS-0422') and 'Janela a definir' in ROW('OS-0422') and 'Revisar' not in ROW('OS-0422'))
    chk('IR-02: sem painel de exceção nem botão Aprovar', J("![...document.querySelectorAll('button')].some(b=>/Aprovar exceção|Revisar exceção/.test(b.innerText))"))
    rowclk('OS-0422','Definir janela'); chk('IR-02: Definir janela abre a própria linha', 'OS-0422' in J("(document.querySelector('aside[role=dialog]')||{innerText:''}).innerText") or J("!!document.querySelector('#fx_g_ag_janela')"))
    J(f"({SETV})('#fx_g_ag_janela','25/09 20:00–22:36')"); time.sleep(.2); clk('Salvar','aside[role=dialog]'); time.sleep(.3); t=T(); print('   ',t)
    chk('IR-02: com janela, liberada na hora com LIB e passadas', 'LIB-2291' in t and '2 passadas' in t and 'Liberadas' in ROW('OS-0422'))
    rowclk('OS-0423','Resolver conflito'); t=T(); print('   ',t); chk('IR-02: conflito resolvido move a janela e libera (estimativa por ET não bloqueia)', '15:00–17:00' in ROW('OS-0423') and 'Conflito' not in ROW('OS-0423') and 'Liberadas' in ROW('OS-0423') and 'LIB-2292' in t)
    rowopen('OS-0419'); J(f"({SETV})('#fx_g_ag_lamina','13')"); time.sleep(.2); clk('Salvar','aside[role=dialog]'); time.sleep(.3); t=T(); print('   ',t)
    chk('IR-02: OS-0419 com 13 mm segue liberada em 2 passadas', 'Liberadas' in ROW('OS-0419') and '2 passadas de 6,5 mm' in ROW('OS-0419'))
    clk('Programar período'); J(f"({SETV})('#fx_g_ag_setor','Pivô 2 · Milho V10')"); J(f"({SETV})('#fx_g_ag_janela','26/09 20:00–22:06')"); J(f"({SETV})('#fx_g_ag_lamina','10,81')"); J(f"({SETV})('#fx_g_ag_dur','2,1')"); time.sleep(.2)
    clk('Salvar','aside[role=dialog]'); time.sleep(.4); t=T(); print('   ',t); chk('IR-02: nova programação gera OS-0440 liberada automaticamente', 'OS-0440' in t and 'Liberadas' in ROW('OS-0440'))
    clk('Programar período'); J(f"({SETV})('#fx_g_ag_setor','Pivô 2 · Milho V10')"); J(f"({SETV})('#fx_g_ag_janela','26/09 20:00–22:06')"); J(f"({SETV})('#fx_g_ag_lamina','10,81')"); J(f"({SETV})('#fx_g_ag_dur','2,1')"); time.sleep(.2)
    clk('Salvar','aside[role=dialog]'); time.sleep(.4); t=T(); print('   ',t); chk('IR-02: mesma janela recupera a tarefa única (sem duplicar)', 'recuperada' in t and J("[...document.querySelectorAll('[role=row]')].filter(r=>r.innerText.indexOf('OS-0440')>=0).length")==1)
    rowclk('OS-0418','Ver decisão') if False else None
    chk('IR-02: OS-0418 (fertirrigação) aponta para a própria decisão', J("[...document.querySelectorAll('[role=row]')].find(r=>r.innerText.indexOf('OS-0418')>=0).querySelector('a').getAttribute('href')")=='IN-02det.dc.html')
    # ---------- IR-03: divergência ----------
    c.goto(f'http://127.0.0.1:{p}/IR-03.dc.html'); time.sleep(.3)
    rowclk('OS-0394','Revisar divergência'); chk('IR-03: divergência revisada encerra OS-0394', 'Encerradas' in ROW('OS-0394'))
    chk('IR-03: OS-0422 não aponta mais para IN-02', J("[...document.querySelectorAll('[role=row]')].find(r=>r.innerText.indexOf('OS-0422')>=0).querySelector('a').getAttribute('href')")=='IR-02.dc.html')
    # ---------- IR-03det: ciclo completo ----------
    c.goto(f'http://127.0.0.1:{p}/IR-03det.dc.html'); time.sleep(.3)
    hdr=lambda: J("document.querySelector('header').innerText.replace(/\\s+/g,' ')")
    cur=lambda: J("[...document.querySelectorAll('main span')].filter(s=>['A liberar','Liberadas','Em execução','Em conferência','Encerradas'].includes(s.innerText.trim()) && getComputedStyle(s).color==='rgb(255, 255, 255)').map(s=>s.innerText.trim()).join('|')")
    chk('IR-03det: começa Liberadas', 'Liberadas' in hdr() and cur()=='Liberadas')
    clk('Confirmar término da irrigação') if False else None
    clk('Pausar'); chk('IR-03det: pausar antes de iniciar é bloqueado com motivo', 'Inicie a irrigação' in T())
    clk('Iniciar irrigação'); t=T(); print('   ',t); chk('IR-03det: iniciar → Em execução (selo e trilha)', '20:02' in t and 'Em execução' in hdr() and cur()=='Em execução')
    clk('Pausar'); chk('IR-03det: pausa vira selo, etapa preservada', 'Pausada' in hdr() and cur()=='Em execução')
    clk('Confirmar término da irrigação'); chk('IR-03det: término bloqueado enquanto pausada', 'Retome' in T())
    clk('Retomar'); clk('Confirmar término da irrigação'); t=T(); print('   ',t); chk('IR-03det: término → Em conferência', 'Em conferência' in hdr())
    time.sleep(2.0); t=T(); print('   ',t); chk('IR-03det: conferência automática → Encerradas com recibos', 'Encerradas' in hdr() and cur()=='Encerradas' and 'AU-3098' in t and 'LIB-2287' in t and 'EX-5120' in t)
    trl=J("[...document.querySelectorAll('[role=table]')[1].querySelectorAll('[role=row]')].slice(1).map(r=>r.innerText.replace(/\\s+/g,' '))"); print('    trilha:', trl)
    chk('IR-03det: trilha coerente (início 20:02, término 24/09 10:41: 1 volta de 14,5 h + 8 min de pausa)', any('20:02' in x for x in trl) and any('24/09 10:41' in x and 'Término' in x and '14,5 h' in x for x in trl))
    chk('IR-03det: primária vira Voltar às ordens', 'Voltar às ordens' in hdr())
    # reclassificação antes de iniciar
    c.goto(f'http://127.0.0.1:{p}/IR-03det.dc.html'); time.sleep(.3)
    clk('Adicionar produtos'); chk('IR-03det: painel de reclassificação da OS-0419', 'OS-0419' in J("document.querySelector('aside[role=dialog] h2').innerText"))
    J(f"({SETV})('#rc_dose','')"); time.sleep(.2); clk('Criar versão v2','aside[role=dialog]'); chk('IR-03det: valida dose e motivo junto ao campo', 'maior que zero' in J("document.querySelector('aside[role=dialog]').innerText") and 'motivo' in J("document.querySelector('aside[role=dialog]').innerText"))
    clk('Cancelar','aside[role=dialog]'); chk('IR-03det: aviso de alterações não salvas', 'Há alterações não salvas' in J("document.querySelector('aside[role=dialog]').innerText")); clk('Continuar editando','aside[role=dialog]')
    J(f"({SETV})('#rc_dose','12')"); J(f"({SETV})('#rc_mot','Deficiência de N no estádio V10')"); time.sleep(.2)
    href_before=J("location.pathname"); clk('Criar versão v2','aside[role=dialog]'); t=T(); print('   ',t)
    chk('IR-03det: v2 criada na própria OS-0419, sem navegar para outra ordem', J("location.pathname")==href_before and 'OS-0419 v2 criada' in t and 'A liberar' in hdr() and cur()=='A liberar')
    aut=J("[...document.querySelectorAll('[role=table]')[0].querySelectorAll('[role=row]')].slice(1).map(r=>r.innerText.replace(/\\s+/g,' '))"); print('    autorização:', aut)
    chk('IR-03det: requisição 960 kg após aprovação e sem encerramento automático', any('960 kg' in x for x in aut) and any('Sem encerramento automático' in x for x in aut))
    clk('Aguardando aprovação da v2'); chk('IR-03det: primária bloqueada explica o motivo', 'aprovação individual' in T())
    # reclassificação em execução
    c.goto(f'http://127.0.0.1:{p}/IR-03det.dc.html'); time.sleep(.3)
    clk('Iniciar irrigação'); clk('Adicionar produtos'); J(f"({SETV})('#rc_mot','Deficiência de N')"); time.sleep(.2); clk('Criar versão v2','aside[role=dialog]')
    chk('IR-03det: em execução, v2 vira selo Revisão de saldo', 'revisão de saldo' in hdr().lower() and cur()=='Em execução')
    # ---------- IR-04: novo sensor ----------
    c.goto(f'http://127.0.0.1:{p}/IR-04.dc.html'); time.sleep(.3)
    clk('+ Cadastrar sensor'); J(f"({SETV})('#fx_g_src_nome','Sonda de umidade · P2 (30 cm)')"); J(f"({SETV})('#fx_g_src_cal','2027-03-31')"); time.sleep(.2)
    clk('Salvar','aside[role=dialog]'); time.sleep(.3); chk('IR-04: sensor novo aguarda 1ª leitura', 'Aguardando 1ª leitura' in ROW('P2 (30 cm)') and 'primeira leitura' in T())
    print('erros JS:', J("window.__err||'nenhum'"))
finally:
    c.close(); srv.terminate()
print(f"\n{sum(1 for _,o in ok if o)} de {len(ok)} verificações OK")
