# -*- coding: utf-8 -*-
"""Teste CDP das correções do parecer de 03/10 em Pragas e doenças (MIP/MID), no navegador e nas telas reais:
fazenda do AG-01 ↔ Mapa nos dois sentidos · atraso de ritmo visível na lista · grades cabem em 1280 × 800 · Mapa = AG-01 no T7 ·
"Completar coleta" reabre a coleta no app · contagem impossível recusada e ponto corrigível · O.S. cancelada não conta (nº máximo,
rotação) e a nova decisão reaproveita o DIA · clique duplo sem erro · erradicação com área validada · AG-01det com primário que executa ·
foco devolvido e Tab preso no painel · REC-014 sem contradição · sem textos de bastidor.
Uso (cada parte < 90 s): python3 mip_correcoes_test.py a  (1–7: fazenda, atraso, largura, mapa, app)  ·  python3 mip_correcoes_test.py b  (8–12)."""
import sys, os, time, subprocess, json
PARTE=(sys.argv[1] if len(sys.argv)>1 else 'ab').lower()
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
from cdp import Chrome
from journeys import free
R=os.path.join(HERE,'_render'); p=free()
srv=subprocess.Popen(['python3','-m','http.server',str(p),'--bind','127.0.0.1','--directory',R],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(0.8)
c=None; OK=[]; FAIL=[]
def chk(nome,cond,info=''):
    (OK if cond else FAIL).append(nome); print(('OK   ' if cond else 'FALHA'),nome,('' if cond else str(info)[:700]))
try:
    for _i in range(4):
        try: c=Chrome(port=free()); break
        except Exception: time.sleep(2)
    J=c.js; c.size(1440,900); U=f'http://127.0.0.1:{p}/'
    c.call('Page.addScriptToEvaluateOnNewDocument',{'source':'window.__g2cvTodasSempre=true'})   # V2-3: teste de domínio lê colunas fora do "Abre com"
    CLK="""((t,root)=>{const r=root?document.querySelector(root):document; if(!r) return 'SEM RAIZ'; const n=s=>(s||'').replace(/\\s+/g,' ').trim(); const els=[...r.querySelectorAll('button,a')].filter(e=>e.offsetParent!==null); const e=els.find(x=>n(x.innerText)===t)||els.find(x=>n(x.innerText).startsWith(t)); if(!e) return 'NÃO ACHEI: '+t; e.click(); return 'ok';})"""
    SETV="""((sel,val)=>{const i=document.querySelector(sel); if(!i) return 'sem campo'; const P=i.tagName==='SELECT'?HTMLSelectElement.prototype:(i.tagName==='TEXTAREA'?HTMLTextAreaElement.prototype:HTMLInputElement.prototype); Object.getOwnPropertyDescriptor(P,'value').set.call(i,val); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true})); return 'ok';})"""
    def clk(t,root=None): r=J(f"({CLK})({json.dumps(t)},{json.dumps(root)})"); time.sleep(.45); return r
    def setv(sel,val): r=J(f"({SETV})({json.dumps(sel)},{json.dumps(val)})"); time.sleep(.35); return r
    def ir(pg,w=1.2): c.goto(U+pg,wait=w); time.sleep(.3)
    def tecla(k,code,shift=False):
        for tp in ('keyDown','keyUp'): c.call('Input.dispatchKeyEvent',dict(type=tp,key=k,code=k,windowsVirtualKeyCode=code,nativeVirtualKeyCode=code,modifiers=8 if shift else 0))
        time.sleep(.35)
    T=lambda: J("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).filter(Boolean).join(' | ')") or ''
    aside=lambda: J("(document.querySelector('aside[role=dialog]')||{innerText:''}).innerText") or ''
    linhas=lambda: J("[...document.querySelectorAll('[role=row].g2r')].map(r=>r.innerText.replace(/\\s+/g,' ').trim())") or []
    faz=lambda: J("(document.querySelector('select[aria-label=\"Filtrar por fazenda\"]')||{}).value||''")
    ir('Main.dc.html',0.8); J("localStorage.removeItem('talhao-os-mip-v1'); localStorage.removeItem('talhao-os-cenario-v1'); sessionStorage.clear()")
    if 'a' in PARTE:
        # 1 · fazenda: sem contexto, o AG-01 abre como o Mapa (Lagoa Grande); trocar no AG-01 persiste e chega ao Mapa; #VIS também
        ir('AG-01.dc.html'); f0=faz(); setv('select[aria-label="Filtrar por fazenda"]','Santa Rita'); ir('AG-01.dc.html'); f1=faz(); ir('IN-04.dc.html',1.6); f2=faz()
        ir('AG-01.dc.html#VIS-051'); f3=faz(); ir('IN-04.dc.html',1.6); f4=faz()
        chk('1 Fazenda: AG-01 sem contexto = Lagoa Grande (igual ao Mapa) · Santa Rita escolhida no AG-01 persiste ao recarregar e abre o Mapa na Santa Rita · #VIS-051 leva AG-01 e Mapa para a Lagoa Grande',
            [f0,f1,f2,f3,f4]==['Lagoa Grande','Santa Rita','Santa Rita','Lagoa Grande','Lagoa Grande'], [f0,f1,f2,f3,f4])
        # 2 · atraso de ritmo visível na lista e com o próximo passo nomeado
        ir('AG-01.dc.html'); l60=next((x for x in linhas() if x.startswith('VIS-060')),'')
        J("(()=>{const r=[...document.querySelectorAll('[role=row].g2r')].find(r=>r.innerText.trim().startsWith('VIS-060')); const b=[...r.querySelectorAll('button,a')].find(b=>b.innerText.trim()==='Programar vistoria'); b.click();})()"); time.sleep(.5)
        pv=J("(()=>{const a=document.querySelector('aside[aria-label=\"Programar vistoria\"]'); return a?[a.querySelector('#pv_tal').value,a.querySelector('select[aria-label=\"Alvo\"]').value]:null;})()")
        chk('2 AG-01 (Lagoa Grande): VIS-060 "Vistoria atrasada · prevista para 17/09 · 6 dias" com "Programar vistoria", que abre o formulário no Pivô 17 × ácaro-rajado',
            'Vistoria atrasada' in l60 and '17/09 · 6 dias' in l60 and 'Programar vistoria' in l60 and pv==['PV17','mamao-acaro'], [l60,pv])
        J("sessionStorage.setItem('mapa-ctx',JSON.stringify({mf_faz:'Santa Rita'}))"); ir('AG-01.dc.html'); l06=next((x for x in linhas() if x.startswith('VIS-006')),'')
        chk('3 AG-01 (Santa Rita): VIS-006 (P1 percevejo, prevista 11/09) atrasada mesmo com a VIS-014 aberta em outro alvo do P1', 'Vistoria atrasada' in l06 and '11/09 · 12 dias' in l06, l06)
        # 4 · grades cabem em 1280 × 800 (sem coluna cortada)
        c.size(1280,800); larg={}
        for pg in ('AG-01.dc.html','AG-03.dc.html','AG-04.dc.html'):
            ir(pg); larg[pg]=J("[...document.querySelectorAll('.g2rola')].map(g=>g.scrollWidth-g.clientWidth)")
        c.size(1440,900)
        chk('4 1280 × 800: AG-01, AG-03 e AG-04 sem rolagem lateral (Próximo passo à vista)', all(v and max(v)<=0 for v in larg.values()), larg)
        # 5 · Mapa (7 dias) e AG-01 iguais no T7: VIS-008 perto do NC, "Seguir monitorando" como botão
        J(f"sessionStorage.setItem('mapa-ctx',{json.dumps(json.dumps(dict(mf_faz='Santa Rita',lay='MIP/MID',tsel=['T7'])))})"); ir('IN-04.dc.html',1.6)
        lab=J("[...document.querySelectorAll('svg [role=button]')].map(e=>e.getAttribute('aria-label')).find(x=>x.startsWith('T7:'))")
        pr=J("(()=>{const a=[...document.querySelectorAll('aside[aria-label^=\"T7\"] a, aside[aria-label^=\"T7\"] button')].find(a=>(a.getAttribute('style')||'').indexOf('30, 122, 76')>=0||(a.getAttribute('style')||'').indexOf('#1E7A4C')>=0); return a?[a.tagName,a.innerText.trim()]:null;})()")
        fonte=J("document.body.innerText.indexOf('a mesma base do AG-01')")
        ir('AG-01.dc.html'); l08=next((x for x in linhas() if x.startswith('VIS-008')),'')
        chk('5 Mapa T7 (7 dias) = AG-01: "Ácaro-rajado · perto do NC" com o botão "Seguir monitorando" · sem texto de bastidor na fonte',
            (lab or '').startswith('T7: Ácaro-rajado · perto do NC') and pr==['BUTTON','Seguir monitorando'] and 'Perto do NC' in l08 and 'Seguir monitorando' in l08 and fonte==-1, [lab,pr,l08,fonte])
        # 6 · coleta incompleta: "Completar coleta" reabre a coleta no app (antes: beco sem saída)
        c.size(390,940); ir('MB-06.dc.html#VIS-017'); setv('#mb_cont','3,5'); clk('Registrar e ir ao ponto 2')
        J("document.querySelector('input[type=checkbox]').click()"); time.sleep(.3); setv('#mb_cont','8'); clk('Registrar e ir ao ponto 3'); r=clk('Concluir com 2 de 16 pontos')
        c.size(1440,900); ir('AG-01.dc.html#VIS-017'); a=aside(); lk=J("(document.querySelector('aside a#pan_prim_a')||{}).getAttribute&&document.querySelector('aside a#pan_prim_a').getAttribute('href')")
        c.size(390,940); ir('MB-06.dc.html#VIS-017'); lb=J("(document.querySelector('label[for=mb_cont]')||{innerText:''}).innerText")
        setv('#mb_cont','4'); r2=clk('Registrar e ir ao ponto 4'); t1=T(); c.size(1440,900)
        chk('6 VIS-017 concluída com 2 de 16 → AG-01 "Coleta incompleta" com "Completar coleta" (MB-06#VIS-017) → o app abre o ponto 3 e reabre a coleta',
            'Coleta incompleta' in a and lk=='MB-06.dc.html#VIS-017' and lb.startswith('Contagem no ponto 3') and 'VIS-017 reaberta · Ponto 3 registrado' in t1, [r,a[:160],lk,lb,r2,t1])
        # 7 · contagem impossível recusada; ponto corrigível no app
        c.size(390,940); ir('MB-06.dc.html#VIS-014'); setv('#mb_cont','500'); clk('Registrar e ir ao ponto 11')
        er=J("(document.querySelector('[role=alert]')||{innerText:''}).innerText")
        J("(()=>{const b=[...document.querySelectorAll('button')].find(b=>b.innerText.trim().startsWith('01 ·')); b.click();})()"); time.sleep(.35)
        lb=J("(document.querySelector('label[for=mb_cont]')||{innerText:''}).innerText"); setv('#mb_cont','6'); r=clk('Corrigir ponto 1'); t1=T(); c.size(1440,900)
        chk('7 App: 500 em "% folíolos com ácaro" recusado (passa de 100) · tocar no ponto 01 abre "Corrigir o ponto 1" e grava 5 → 6',
            'passa de 100' in er and lb.startswith('Corrigir o ponto 1') and 'Ponto 1 corrigido: 5 → 6' in t1, [er,lb,r,t1])
    if 'b' in PARTE and 'a' not in PARTE: ir('Main.dc.html',0.8); J("localStorage.removeItem('talhao-os-mip-v1'); localStorage.removeItem('talhao-os-cenario-v1'); sessionStorage.clear()")
    if 'b' in PARTE:
        # 8 · O.S. cancelada sem execução: não conta no nº máximo nem na rotação; nova decisão reaproveita o DIA-009; clique duplo sem erro
        ir('AG-01.dc.html#VIS-013:decidir'); J("[...document.querySelectorAll('aside input[name=dc_prod]')][2].click()"); time.sleep(.3)
        clk('Emitir receituário e gerar O.S.','aside'); t0=T()
        # cancelamento sem execução feito na tela O.S. (o núcleo da O.S. é de outra trilha): grava a etapa no cenário e volta ao AG-01 vindo da O.S.
        J("(()=>{const c=JSON.parse(localStorage.getItem('talhao-os-cenario-v1')); c.ordens['OS-0440'].etapa='Canceladas'; localStorage.setItem('talhao-os-cenario-v1',JSON.stringify(c));})()")
        ir('OS.dc.html#OS-0440'); ir('AG-01.dc.html#VIS-013'); a=aside(); clk('Decidir controle','aside'); J("[...document.querySelectorAll('aside input[name=dc_prod]')][2].click()"); time.sleep(.3)
        a2=aside(); dis=J("[...document.querySelectorAll('aside button')].find(b=>b.innerText.trim()==='Emitir receituário e gerar O.S.').disabled")
        J("window.__errs=[]; window.addEventListener('error',e=>window.__errs.push(String(e.message)));")
        J("(()=>{const b=[...document.querySelectorAll('aside button')].find(b=>b.innerText.trim()==='Emitir receituário e gerar O.S.'); b.click(); b.click();})()"); time.sleep(.6)
        t1=T(); errs=J("window.__errs")
        chk('8a Cancelar a OS-0440 (Inseticida B): VIS-013 "O.S. cancelada" → "Decidir controle"; Inseticida B sem trava de nº máximo, rotação citando 08/09 e não a cancelada',
            'OS-0440 em A liberar' in t0 and 'O.S. cancelada' in a and 'Nº máximo' not in a2 and '08/09 · Inseticida B' in a2 and '24/09 · Inseticida B' not in a2 and dis is False, [t0,a[:200],a2[a2.find('Rotação'):a2.find('Rotação')+140],dis])
        chk('8b Nova decisão: RA-0143 (DIA-009 · REC-019) e OS-0441; clique duplo não lança erro', 'Receituário RA-0143 emitido (DIA-009 · REC-019) · OS-0441 em A liberar' in t1 and errs==[], [t1,errs])
        ir('AG-04.dc.html'); r15=next((x for x in linhas() if x.startswith('REC-015')),''); r19=next((x for x in linhas() if x.startswith('REC-019')),'')
        ir('AG-03.dc.html'); ls=linhas(); d9=next((x for x in ls if x.startswith('DIA-009')),'')
        chk('8c Rastreabilidade: REC-015 "Cancelado · substituído pelo REC-019"; REC-019 com OS-0441; DIA-009 abre a OS-0441; sem DIA-011 duplicado',
            'Cancelado' in r15 and 'substituído pelo REC-019' in r15 and 'OS-0441' in r19 and 'Abrir OS-0441' in d9 and not any(x.startswith('DIA-011') for x in ls), [r15,r19,d9])
        # 9 · erradicação: área do foco não passa do talhão
        ir('AG-01.dc.html#VIS-055:decidir'); setv('aside input[aria-label="Área em hectares"]','999'); a=aside()
        dis=J("[...document.querySelectorAll('aside button')].find(b=>b.innerText.trim()==='Gerar O.S. de erradicação').disabled")
        # SINT-T01: área do Pivô 22 da fonte única (dados_lagoa_fonte), no formato do mipN (até 1 casa, vírgula)
        import dados_lagoa_fonte as _F; a22=_F.PIVOS_HA[22]; t22=f'{a22:.2f}'.rstrip('0').rstrip('.').replace('.',',')   # mesma forma do mipN(área, 2) da mensagem
        chk(f'9 Erradicação com 999 ha no Pivô 22 ({t22} ha): trava "Área maior que o talhão ({t22} ha)" e botão bloqueado', a22 < 999 and f'Área maior que o talhão ({t22} ha).' in a and dis is True, [a[-300:],dis])
        # 10 · AG-01det: o primário executa (não repete o destino do Voltar)
        ir('AG-01det.dc.html#VIS-016'); b=J("(()=>{const x=[...document.querySelectorAll('header a, header button')].find(e=>e.innerText.trim()==='Sincronizar agora'); return x?[x.tagName,x.getAttribute('href')]:null;})()")
        clk('Sincronizar agora','header'); t1=T(); kp=J("document.querySelector('main').innerText.indexOf('6 de 12')>=0")
        chk('10 AG-01det#VIS-016: "Sincronizar agora" é botão que sincroniza ali mesmo (6 de 12 pontos)', b==['BUTTON',None] and 'pontos de João entraram na VIS-016' in t1 and kp, [b,t1,kp])
        # 11 · teclado: Esc devolve o foco à linha; Tab fica preso no painel (aria-modal)
        J("sessionStorage.setItem('mapa-ctx',JSON.stringify({mf_faz:'Santa Rita'}))")   # o passo 9 (Pivô 22) deixou a Lagoa Grande no contexto
        ir('AG-01.dc.html'); J("(()=>{const r=[...document.querySelectorAll('[role=row].g2r')].find(r=>r.innerText.trim().startsWith('VIS-013')); r.focus();})()"); tecla('Enter',13)
        ab=J("!!document.querySelector('aside[role=dialog]')"); tecla('Escape',27)
        fo=J("(()=>{const a=document.activeElement; const r=a&&a.closest?a.closest('[role=row]'):null; return r?r.innerText.trim().slice(0,7):(a?a.tagName:'');})()")
        J("(()=>{const r=[...document.querySelectorAll('[role=row].g2r')].find(r=>r.innerText.trim().startsWith('VIS-013')); r.focus();})()"); tecla('Enter',13)
        J("(()=>{const a=document.querySelector('aside[role=dialog]'); const f=[...a.querySelectorAll('a[href],button:not([disabled]),input,select,textarea')].filter(x=>x.offsetParent!==null&&x.getAttribute('tabindex')!=='-1'); f[f.length-1].focus();})()")
        tecla('Tab',9); dentro=J("!!(document.activeElement&&document.activeElement.closest('aside[role=dialog]'))"); tecla('Tab',9,shift=True); dentro2=J("!!(document.activeElement&&document.activeElement.closest('aside[role=dialog]'))")
        chk('11 Teclado: Enter abre, Esc fecha e devolve o foco à linha VIS-013; Tab e Shift+Tab ficam dentro do painel', ab and fo=='VIS-013' and dentro and dentro2, [ab,fo,dentro,dentro2])
        # 12 · REC-014 sem contradição e sem destino repetido; textos de bastidor fora
        ir('AG-04det.dc.html'); b=J("document.body.innerText"); np=J("document.querySelectorAll('a[href=\"AG-07.dc.html#pasteuria-nishizawae-fs\"]').length")
        hd=J("document.querySelector('header').innerText")
        ir('AG-03det.dc.html'); b3=J("document.body.innerText"); n14=J("document.querySelectorAll('a[href=\"AG-04det.dc.html\"]').length"); h14=J("document.querySelectorAll('header a[href=\"AG-04det.dc.html\"]').length")   # AÇÃO v3.1 (G2): o elo da cadeia que repete o próximo passo fica informativo
        chk('12 AG-04det: "Saldo de 70 ha travado · TS sem registro", v3 "TS travado · sem registro", primário "Criar v4 com TS registrado", 1 link para a Pasteuria · AG-03det sem "Cada elo" e com 1 link para o REC-014 (o primário do cabeçalho; AÇÃO v3.1)',
            'Saldo de 70 ha travado · TS sem registro' in hd and 'Criar v4 com TS registrado' in hd and 'TS travado · sem registro' in b and 'Aprovada por Ana · saldo' not in b and np==1
            and 'Cada elo abre o registro' not in b3 and n14==1 and h14==1, [hd[:300],np,n14,h14])
    J("localStorage.removeItem('talhao-os-mip-v1'); localStorage.removeItem('talhao-os-cenario-v1'); sessionStorage.clear()")
finally:
    try:
        if c: c.close()
    finally: srv.terminate()
print('RESULTADO', f'{len(OK)}/{len(OK)+len(FAIL)}')
sys.exit(1 if FAIL else 0)
