# -*- coding: utf-8 -*-
"""Teste CDP (15 verificações) do fluxo de Pragas e doenças (MIP/MID) numa base só: Mapa (camada Pragas e doenças) ↔ AG-01 (lista + painel)
↔ AG-01det ↔ AG-03/AG-04 ↔ O.S. ↔ app (MB-06), com o estado 'talhao-os-mip-v1' e o cenário das O.S. ('talhao-os-cenario-v1').
Fluxo: vistoria acima do NC → só produtos registrados para cultura × alvo, com trava de carência e alerta de rotação → receituário RA →
OS-0440 em A liberar na tela O.S. → mapa com "Abrir OS-0440"; abaixo do NC → próxima vistoria; meleira → O.S. de erradicação sem produto;
"Seguir monitorando" no mapa registra e programa a próxima, que persiste e aparece no AG-01; ponto coletado no app chega ao AG-01.
As correções do parecer de 03/10 estão em mip_correcoes_test.py. Uso: python3 mip_fluxo_test.py (≈ 80 s)."""
import sys, os, time, subprocess, json
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
from cdp import Chrome
from journeys import free
R=os.path.join(HERE,'_render'); p=free()
srv=subprocess.Popen(['python3','-m','http.server',str(p),'--bind','127.0.0.1','--directory',R],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(0.8)
c=None; OK=[]; FAIL=[]
def chk(nome,cond,info=''):
    (OK if cond else FAIL).append(nome); print(('OK   ' if cond else 'FALHA'),nome,('' if cond else str(info)[:600]))
try:
    for _i in range(4):
        try: c=Chrome(port=free()); break
        except Exception: time.sleep(2)
    J=c.js; c.size(1440,900); U=f'http://127.0.0.1:{p}/'
    CLK="""((t,root)=>{const r=root?document.querySelector(root):document; if(!r) return 'SEM RAIZ'; const n=s=>(s||'').replace(/\\s+/g,' ').trim(); const els=[...r.querySelectorAll('button,a')].filter(e=>e.offsetParent!==null); const e=els.find(x=>n(x.innerText)===t)||els.find(x=>n(x.innerText).startsWith(t)); if(!e) return 'NÃO ACHEI: '+t; e.click(); return 'ok';})"""
    SETV="""((sel,val)=>{const i=document.querySelector(sel); if(!i) return 'sem campo'; const P=i.tagName==='SELECT'?HTMLSelectElement.prototype:HTMLInputElement.prototype; Object.getOwnPropertyDescriptor(P,'value').set.call(i,val); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true})); return 'ok';})"""
    def clk(t,root=None): r=J(f"({CLK})({json.dumps(t)},{json.dumps(root)})"); time.sleep(.45); return r
    def setv(sel,val): r=J(f"({SETV})({json.dumps(sel)},{json.dumps(val)})"); time.sleep(.35); return r
    def ir(pg,w=1.2): c.goto(U+pg,wait=w)
    def ir_hash(pg): ir(pg,1.5); time.sleep(.4)   # outra página: carga nova; mesma página: o hashchange abre o registro
    T=lambda: J("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).filter(Boolean).join(' | ')") or ''
    aside=lambda: J("(document.querySelector('aside[role=dialog]')||{innerText:''}).innerText") or ''
    linhas=lambda: J("[...document.querySelectorAll('[role=row].g2r')].map(r=>r.innerText.replace(/\\s+/g,' ').trim())") or []
    def mapa(tal,lay='MIP/MID'):
        J(f"sessionStorage.setItem('mapa-ctx',{json.dumps(json.dumps(dict(mf_faz='Santa Rita',lay=lay,tsel=[tal])))})"); ir('IN-04.dc.html',1.5)
    pan=lambda t: J(f"(document.querySelector('aside[aria-label^=\"{t}\"]')||{{}}).innerText||''") or ''
    prim=lambda t: J(f"(()=>{{const a=[...document.querySelectorAll('aside[aria-label^=\"{t}\"] a, aside[aria-label^=\"{t}\"] button')].find(a=>(a.getAttribute('style')||'').indexOf('30, 122, 76')>=0||(a.getAttribute('style')||'').indexOf('#1E7A4C')>=0); return a?[a.innerText.trim(),a.getAttribute('href')]:null;}})()")
    ir('Main.dc.html',0.8); J("localStorage.removeItem('talhao-os-mip-v1'); localStorage.removeItem('talhao-os-cenario-v1'); sessionStorage.clear()")
    # 1 · AG-01 vindo do Mapa na Santa Rita (contexto mapa-ctx): título do menu, selo, pior primeiro, primário único
    J("sessionStorage.setItem('mapa-ctx',JSON.stringify({mf_faz:'Santa Rita'}))")
    ir('AG-01.dc.html'); ls=linhas(); hd=J("document.querySelector('header').innerText.replace(/\\n/g,' | ')")
    chk('1 AG-01 "Pragas e doenças" (Santa Rita): selo "1 acima do NC sem decisão", VIS-013 primeiro com "Decidir controle", primário único "Programar vistoria"',
        'Pragas e doenças' in hd and '1 acima do NC sem decisão' in hd and ls and ls[0].startswith('VIS-013') and 'Acima do NC' in ls[0] and 'Decidir controle' in ls[0]
        and J("[...document.querySelectorAll('header button, header a')].filter(b=>b.innerText.trim()==='Programar vistoria').length")==1, [hd,ls[:2]])
    # 2 · Lagoa Grande no AG-01 (filtro Fazenda do topo)
    setv('select[aria-label="Filtrar por fazenda"]','Lagoa Grande'); ls=linhas()
    chk('2 Fazenda Lagoa Grande: VIS-051…060 no AG-01 (10), VIS-051 em controle pela OS-0504',
        len(ls)==10 and all(x.split(' ')[0]>='VIS-051' for x in ls) and any(x.startswith('VIS-051') and 'Em controle' in x and 'OS-0504' in x for x in ls), ls)
    # 3 · link com hash abre o painel e troca a fazenda
    setv('select[aria-label="Filtrar por fazenda"]','Santa Rita'); ir_hash('AG-01.dc.html#VIS-053'); a=aside()
    chk('3 AG-01.dc.html#VIS-053 abre o painel da meleira (Pivô 9) e troca a fazenda para Lagoa Grande · próximo passo "Confirmar foco"',
        a.startswith('VIS-053 · Meleira (virose) · Pivô 9') and 'Confirmar foco' in a and J("document.querySelector('select[aria-label=\"Filtrar por fazenda\"]').value")=='Lagoa Grande', a[:300])
    # 4 · mesma situação no Mapa e no AG-01
    mapa('P1'); lab=J("[...document.querySelectorAll('svg [role=button]')].map(e=>e.getAttribute('aria-label')).find(x=>x.startsWith('P1:'))"); pr=prim('P1')
    chk('4 Mapa P1: "Mosca-branca · acima do NC" (+2: VIS-014 em coleta e VIS-006 atrasada, iguais ao AG-01) · primário "Decidir controle" abre a decisão da VIS-013',
        lab=='P1: Mosca-branca · acima do NC · +2' and pr==['Decidir controle','AG-01.dc.html#VIS-013:decidir'], [lab,pr])
    # 5 · no mapa o verbo faz o que diz: "Seguir monitorando" (VIS-008 perto do NC) registra e programa a revisita, que persiste e chega ao AG-01
    mapa('T7'); pr=prim('T7'); r=clk('Seguir monitorando','aside[aria-label^="T7"]'); t1=T(); mapa('T7'); p7=pan('T7')
    ir('AG-01.dc.html'); ls=linhas(); l18=next((x for x in ls if x.startswith('VIS-018')),'')
    chk('5 Mapa T7 "Seguir monitorando" (botão, não link) registra na VIS-008 e programa VIS-018 (ácaro-rajado), que persiste e aparece no AG-01 como Programada · "Coletar no app"',
        pr==['Seguir monitorando',None] and 'Seguir monitorando registrado em VIS-008 · VIS-018 programada para 24/09' in t1 and 'Ácaro-rajado · programada' in p7 and 'Programada' in l18 and 'Coletar no app' in l18, [pr,r,t1,p7[:200],l18])
    # 6 · decisão: só os registrados para feijão × mosca-branca, com a conferência ao vivo
    ir_hash('AG-01.dc.html#VIS-013:decidir')
    nomes=J("[...document.querySelectorAll('aside [role=radiogroup][aria-label=\"Produto registrado\"] b')].map(b=>b.innerText.trim())")
    chips=J("[...document.querySelectorAll('aside [role=radiogroup][aria-label=\"Produto registrado\"] > div')].map(d=>d.innerText.replace(/\\s+/g,' '))") or []
    chk('6 Decidir controle (VIS-013): só os 4 registrados para feijão × mosca-branca · Inseticida B com alerta de rotação (IRAC 1B)',
        nomes==['Ciantraniliprole 100 OD','Acaricida D','Inseticida B','Piriproxifem 100 EC'] and any('Inseticida B' in x and 'Rotação' in x for x in chips), [nomes,chips])
    # 7 · trava de carência × colheita (10/10) com a data de aplicação
    J("[...document.querySelectorAll('aside input[name=dc_prod]')][1].click()"); time.sleep(.3)
    setv('aside input[aria-label="Data da aplicação"]','2026-09-28'); a=aside(); dis=J("[...document.querySelectorAll('aside button')].find(b=>b.innerText.trim()==='Emitir receituário e gerar O.S.').disabled")
    chk('7 Acaricida D aplicado em 28/09: trava "carência de 14 dias passa da colheita prevista (10/10): aplicar até 26/09" e o botão fica bloqueado',
        'Carência de 14 dias passa da colheita prevista (10/10): aplicar até 26/09.' in a and dis is True, [a[a.find('Carência'):a.find('Carência')+160],dis])
    # 8 · emitir: receituário RA + O.S. em A liberar
    setv('aside input[aria-label="Data da aplicação"]','2026-09-24'); J("[...document.querySelectorAll('aside input[name=dc_prod]')][0].click()"); time.sleep(.3)
    clk('Emitir receituário e gerar O.S.','aside'); t1=T(); a=aside()
    chk('8 Emitir: receituário RA-0142 (DIA-009 · REC-015) e OS-0440 em A liberar · painel "Em controle" com "Abrir OS-0440"',
        'Receituário RA-0142 emitido (DIA-009 · REC-015) · OS-0440 em A liberar' in t1 and 'Em controle' in a and 'OS-0440 · A liberar' in a
        and J("!!document.querySelector('aside a[href=\"OS.dc.html#OS-0440\"]')"), [t1,a[:300]])
    # 9 · a O.S. chega à tela O.S. (cenário compartilhado), com o produto e a origem
    ir_hash('OS.dc.html#OS-0440'); a=aside(); org=J("(JSON.parse(localStorage.getItem('talhao-os-cenario-v1')).ordens['OS-0440'].osc.novo.orig||[]).join(' · ')") or ''
    chk('9 OS.dc.html#OS-0440: A liberar com Ciantraniliprole 100 OD (sem lote: a trava de estoque é a da liberação) e origem VIS-013 · RA-0142',
        a.startswith('OS-0440') and 'A liberar' in a and 'Ciantraniliprole 100 OD' in a and 'VIS-013' in org and 'RA-0142' in org, [a[:300],org])
    # 10 · o mapa mostra o controle emitido
    mapa('P1'); pr=prim('P1'); lab=J("[...document.querySelectorAll('svg [role=button]')].map(e=>e.getAttribute('aria-label')).find(x=>x.startsWith('P1:'))")
    chk('10 Mapa P1 depois de emitir: "Mosca-branca · em controle" · primário "Abrir OS-0440"', pr==['Abrir OS-0440','OS.dc.html#OS-0440'] and 'em controle' in (lab or ''), [pr,lab])
    # 11 · abaixo do NC: seguir monitorando programa a próxima no ritmo semanal
    ir_hash('AG-01.dc.html#VIS-015'); clk('Seguir monitorando','aside'); t1=T()
    chk('11 VIS-015 abaixo do NC → "Seguir monitorando" registra e programa VIS-019 para 29/09', 'Seguir monitorando registrado em VIS-015 · VIS-019 programada para 29/09' in t1, t1)
    # 12 · meleira: foco → erradicação sem produto
    ir_hash('AG-01.dc.html#VIS-053'); clk('Confirmar foco','aside'); r=clk('Gerar O.S. de erradicação','aside'); t1=T()
    o41=J("(JSON.parse(localStorage.getItem('talhao-os-cenario-v1')).ordens['OS-0441'])||null")
    chk('12 Meleira (PV09): Confirmar foco → "Gerar O.S. de erradicação" → OS-0441 em A liberar sem produto',
        'OS-0441 de erradicação emitida em A liberar' in t1 and o41 and o41['etapa']=='A liberar' and o41['ins']==[] and o41['talhao']=='Pivô 9', [r,t1,o41 and {k:o41[k] for k in ('etapa','ins','talhao')}])
    # 13 · sub-detalhe: rota e evidências por hash
    ir_hash('AG-01det.dc.html#VIS-051'); b=J("document.querySelector('main').innerText")
    nd=J("document.querySelectorAll('[aria-label=\"Rota em W da vistoria\"] span[title]').length")
    chk('13 AG-01det#VIS-051: rota do Pivô 6 com 20 pontos e média válida 18 % (NC 15) · voltar leva a AG-01.dc.html#VIS-051',
        'VIS-051 · Ácaro-rajado · Pivô 6' in b and nd==20 and '18\n% folhas com ácaro · NC 15' in b and J("!!document.querySelector('a[aria-label=\"Voltar\"][href=\"AG-01.dc.html#VIS-051\"]')"), [b[:300],nd])
    # 14 · app: o ponto coletado chega ao AG-01
    c.size(390,940); ir_hash('MB-06.dc.html#VIS-014'); setv('#mb_cont','12'); r=clk('Registrar e ir ao ponto 11'); t1=T(); c.size(1440,900)
    ir_hash('AG-01.dc.html#VIS-014'); a=aside()
    chk('14 App MB-06#VIS-014: "Registrar e ir ao ponto 11" grava o ponto 10 · AG-01 mostra 10 de 14 coletados', 'Ponto 10 registrado' in t1 and '10 de 14 pontos coletados' in a, [r,t1,a[:300]])
    # 15 · AG-03 e AG-04 leem a mesma decisão (sem bloqueio por laudo)
    ir('AG-03.dc.html'); d9=next((x for x in linhas() if x.startswith('DIA-009')),''); ir('AG-04.dc.html'); r15=next((x for x in linhas() if x.startswith('REC-015')),'')
    chk('15 AG-03: DIA-009 Registrada (sem "Bloqueado" por laudo) · AG-04: REC-015 com RA-0142 e OS-0440',
        'Registrada' in d9 and 'Bloqueado' not in d9 and 'RA-0142' in r15 and 'Receituário emitido' in r15 and 'OS-0440' in r15, [d9,r15])
    J("localStorage.removeItem('talhao-os-mip-v1'); localStorage.removeItem('talhao-os-cenario-v1')")
finally:
    try:
        if c: c.close()
    finally: srv.terminate()
print('RESULTADO', f'{len(OK)}/{len(OK)+len(FAIL)}')
sys.exit(1 if FAIL else 0)
