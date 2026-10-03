# -*- coding: utf-8 -*-
"""Verificador independente (mapa-cadastros-06/07/08 + os-06/07 no mapa e no CA-01, os-08 Voltar) — só observa."""
import sys, os, time, subprocess, json
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from cdp import Chrome
from journeys import free
HERE=os.path.dirname(os.path.abspath(__file__)); R=os.path.join(HERE,'_render'); p=free()
srv=subprocess.Popen(['python3','-m','http.server',str(p),'--bind','127.0.0.1','--directory',R],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(0.8)
c=None; OK=[]; FAIL=[]
def chk(nome,cond,info=''):
    (OK if cond else FAIL).append(nome); print(('OK   ' if cond else 'FALHA'),nome,str(info)[:400])
try:
    c=Chrome(port=free()); J=c.js
    CLK="""((t,root)=>{const r=root?document.querySelector(root):document; const n=s=>(s||'').replace(/\\s+/g,' ').trim(); const els=[...r.querySelectorAll('button,a,[role=tab]')]; const e=els.find(x=>n(x.innerText)===t)||els.find(x=>n(x.innerText).startsWith(t)); if(!e) return 'NÃO ACHEI: '+t; e.click(); return 'ok';})"""
    def clk(t,root=None): r=J(f"({CLK})({json.dumps(t)},{json.dumps(root)})"); time.sleep(.4); return r
    tap=lambda t,root='': J(f"(()=>{{const e=[...document.querySelectorAll('{root} svg [role=button]')].find(x=>(x.getAttribute('aria-label')||'').startsWith('{t}:')); if(!e) return 'sem'; e.dispatchEvent(new MouseEvent('click',{{bubbles:true}})); return 'ok';}})()")
    T=lambda: J("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).filter(Boolean).join(' | ')") or ''
    panof=lambda t: J(f"(document.querySelector('aside[aria-label^=\"{t}\"]')||{{}}).innerText||''") or ''
    VB="(()=>{return [...document.querySelectorAll('button')].filter(b=>b.innerText.trim()==='Programar vistoria' && b.title==='Clique no talhão para programar a vistoria');})()"
    vbar=lambda: J(f"(()=>{{const b={VB}; return b.map(x=>x.getAttribute('aria-pressed'));}})()")
    vclk=lambda: (J(f"{VB}[{VB}.length-1].click()"), time.sleep(.4))
    c.size(1440,900); c.goto(f'http://127.0.0.1:{p}/Main.dc.html')
    # vistorias do mapa ficam no estado do MIP (persistem): começa da semente; o mapa abre na Lagoa Grande (01/10): talhões desenhados = Santa Rita
    J("localStorage.removeItem('talhao-os-mip-v1'); sessionStorage.setItem('mapa-ctx',JSON.stringify({mf_faz:'Santa Rita'}))")
    c.goto(f'http://127.0.0.1:{p}/IN-04.dc.html'); time.sleep(.6)
    chk('sem erro JS', (J("window.__err||''") or '')=='' and 'renderVals' not in J("document.body.innerText"))
    rail=J("[...document.querySelectorAll('nav[aria-label=\"Funcionalidades do mapa\"] [role=tab]')].map(x=>x.innerText.trim())")
    chk('barra vertical = só as 9 funcionalidades', len(rail)==9, rail)
    # ---- modo Programar vistoria (mesma base do AG-01): troca de funcionalidade desliga; clique depois não cria ----
    clk('Pragas e doenças'); vclk(); print('   modo:', vbar(), T())
    clk('Satélite'); print('   após trocar p/ Satélite:', vbar(), T())
    tap('T4'); time.sleep(.4); t=T(); chk('troca de funcionalidade desliga o modo (clique no T4 no Satélite não cria vistoria)', 'VIS-0' not in t, t)
    tap('T4'); time.sleep(.2)
    # modo + T7 (tem mancha) -> centroide
    clk('Pragas e doenças'); vclk(); tap('T7'); time.sleep(.4); t=T(); chk('modo no T7: programa VIS-018 do alvo da última vistoria (ácaro-rajado)', 'VIS-018 programada para T7 × ácaro-rajado' in t, t)
    chk('modo cria e seleciona o talhão (painel do T7 aberto)', 'Abrir VIS-018' in panof('T7'), panof('T7')[:160])
    tap('P2'); time.sleep(.4); t=T(); chk('modo continua ligado: 2º talhão (P2) programa VIS-019', 'VIS-019 programada para P2' in t, t)
    vclk(); tap('P2'); time.sleep(.2)
    # modo ligado e depois Tela cheia
    vclk(); clk('Tela cheia'); time.sleep(.4)
    DLG='[role=dialog][aria-label="Mapa em tela cheia"]'
    chk('tela cheia abre', J(f"!!document.querySelector('{DLG}')"))
    print('   modo na tela cheia:', vbar(), '| modo selo:', T())
    rail_f=J(f"[...document.querySelectorAll('{DLG} nav[aria-label=\"Funcionalidades do mapa\"] [role=tab]')].map(x=>x.innerText.trim())")
    chk('tela cheia: barra vertical com 9', len(rail_f)==9, rail_f)
    hb=J(f"(document.querySelector('{DLG} [role=group][aria-label^=\"Indicadores de\"]')||{{}}).innerText||''")
    chk('tela cheia: indicadores da funcionalidade', len(hb)>5, hb.replace('\n',' '))
    r=tap('P1',DLG); time.sleep(.4); t=T(); print('   tap P1 em tela cheia:', r, t)
    chk('tela cheia: modo Programar vistoria funciona no mapa da tela cheia (P1 já tem a VIS-014 aberta)', 'VIS-014 já está aberta para P1' in t, t)
    # trocar funcionalidade dentro da tela cheia pela barra vertical
    J(f"(()=>{{const e=[...document.querySelectorAll('{DLG} nav[aria-label=\"Funcionalidades do mapa\"] [role=tab]')].find(x=>x.innerText.trim()==='Solo'); e&&e.click();}})()"); time.sleep(.4)
    hb2=J(f"(document.querySelector('{DLG} [role=group][aria-label^=\"Indicadores de\"]')||{{}}).getAttribute?.('aria-label')||''")
    chk('tela cheia: barra vertical troca a funcionalidade (indicadores de Solo)', 'Solo' in (hb2 or ''), hb2)
    sel=J(f"[...document.querySelectorAll('{DLG} nav[aria-label=\"Funcionalidades do mapa\"] [role=tab]')].filter(x=>x.getAttribute('aria-selected')==='true').map(x=>x.innerText.trim())")
    chk('tela cheia: item Solo marcado', sel==['Solo'], sel)
    ov=J(f"(()=>{{const d=document.querySelector('{DLG}'); return [d.scrollWidth,d.clientWidth,d.scrollHeight,d.clientHeight, document.documentElement.scrollWidth, window.innerWidth];}})()")
    chk('tela cheia sem rolagem horizontal', ov[0]<=ov[1]+1 and ov[4]<=ov[5], ov)
    c.shot(os.path.join(HERE,'_probe','verif_full.png'))
    clk('Sair da tela cheia'); time.sleep(.3)
    chk('saiu da tela cheia', not J(f"!!document.querySelector('{DLG}')"))
    # ---- geometria só na camada Integrado ----
    clk('Integrado'); tap('T1'); time.sleep(.3); pn=panof('T1'); chk('Integrado T1: Geometria', 'Geometria\npolígono v3 validado 12/09 · T1-B sem polígono' in pn, pn[:500].replace('\n',' / '))
    tap('T1'); clk('Satélite'); tap('T1'); time.sleep(.3); chk('Satélite T1: sem linha Geometria', 'Geometria' not in panof('T1'), panof('T1')[:200].replace('\n',' / ')); tap('T1')
    # ---- mapa O.S./prazos: OS-0430 e OS-0431 ----
    clk('O.S./prazos'); tap('T1'); time.sleep(.3); pn=panof('T1'); print('   T1 O.S.:', pn[:600].replace('\n',' / '))
    chk('mapa: OS-0430 A liberar com Liberar para execução (sem selo do agrônomo)', 'A liberar' in pn and 'Liberar para execução' in pn and 'Aguardando agrônomo' not in pn, pn[:600].replace('\n',' / '))
    tap('T1'); tap('T2'); time.sleep(.3); pn=panof('T2'); print('   T2 O.S.:', pn[:700].replace('\n',' / '))
    cores=J("(()=>{const a=document.querySelector('aside[aria-label^=\"T2\"]'); return [...a.querySelectorAll('span')].filter(s=>/^Falta máquina/.test(s.innerText.trim())).map(s=>s.innerText.trim()+'='+getComputedStyle(s).color);})()")
    print('   cores:', cores)
    tap('T2')
    c.shot(os.path.join(HERE,'_probe','verif_mapa_T2.png'))
    # ---- CA-01 (painel de campo) ----
    c.goto(f'http://127.0.0.1:{p}/CA-01.dc.html'); time.sleep(.5)
    body=J("document.body.innerText")
    chk('CA-01 sem erro', 'renderVals' not in body and (J("window.__err||''") or '')=='')
    r431=J("(()=>{const r=[...document.querySelectorAll('[role=row]')].find(r=>r.innerText.indexOf('OS-0431')>=0); return r?r.innerText.replace(/\\s+/g,' '):'';})()")
    r430=J("(()=>{const r=[...document.querySelectorAll('[role=row]')].find(r=>r.innerText.indexOf('OS-0430')>=0); return r?r.innerText.replace(/\\s+/g,' '):'';})()")
    print('   CA-01 OS-0431:', r431); print('   CA-01 OS-0430:', r430)
    chk('CA-01 OS-0431 com falta máquina (sem selo nem versão "aprovada")', 'Falta máquina' in r431 and 'Aprovada pelo agrônomo' not in r431 and 'v1 aprovada' not in r431, r431)
    chk('CA-01 OS-0430 A liberar, sem Aguardando agrônomo', 'Aguardando agrônomo' not in r430 and 'A liberar' in r430, r430)
    import re
    m=re.findall(r'[^\n]*impedid[^\n]*', body); print('   CA-01 impedidas:', m[:4])
    # ---- os-08: Voltar ----
    for f in ['CA-01det','CA-01x-os0420']:
        c.goto(f'http://127.0.0.1:{p}/{f}.dc.html'); time.sleep(.4)
        J("document.querySelector('a[aria-label=Voltar]').click()"); time.sleep(1.5)
        u=J("location.pathname"); chk(f'{f}: Voltar abre OS.dc.html', u.endswith('/OS.dc.html'), u)
    # ---- MB-02: selos da OS-0420 ----
    c.goto(f'http://127.0.0.1:{p}/MB-02.dc.html'); time.sleep(.5)
    b=J("document.body.innerText"); i=b.find('OS-0420'); print('   MB-02 OS-0420:', b[i:i+300].replace('\n',' / '))
finally:
    try:
        if c: c.close()
    finally: srv.terminate()
print(f'\n{len(OK)} ok · {len(FAIL)} falhas', FAIL)
