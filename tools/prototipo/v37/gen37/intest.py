# -*- coding: utf-8 -*-
"""Teste CDP do Mapa (IN-04): camada, filtro recolore talhão, clique abre painel, sem rolagem (≤ 900).
Uso: python3 intest.py [a|b|c|all]."""
import sys, os, time, subprocess, json
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from cdp import Chrome
from journeys import free
R=os.path.join(os.path.dirname(os.path.abspath(__file__)),'_render'); p=free()
PARTE=(sys.argv[1] if len(sys.argv)>1 else 'all')  # a = mapa e camadas · b = modos, geometria e selos · c = lote das Aprovações (cada parte < 90 s)
srv=subprocess.Popen(['python3','-m','http.server',str(p),'--bind','127.0.0.1','--directory',R],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(0.8)
c=None; OK=[]; FAIL=[]
def chk(nome,cond,info=''):
    (OK if cond else FAIL).append(nome); print(('OK   ' if cond else 'FALHA'),nome,info)
try:
    c=Chrome(port=free()); J=c.js
    CLK="""((t,root)=>{const r=root?document.querySelector(root):document; const n=s=>(s||'').replace(/\\s+/g,' ').trim(); const els=[...r.querySelectorAll('button,a')]; const e=els.find(x=>n(x.innerText)===t)||els.find(x=>n(x.innerText).startsWith(t)); if(!e) return 'NÃO ACHEI: '+t; e.click(); return 'ok';})"""
    def clk(t,root=None): r=J(f"({CLK})({json.dumps(t)},{json.dumps(root)})"); time.sleep(.4); return r
    fill=lambda t: J(f"(()=>{{const e=[...document.querySelectorAll('svg [role=button]')].find(x=>(x.getAttribute('aria-label')||'').startsWith('{t}:')); return e?e.getAttribute('fill'):null;}})()")
    lab=lambda t: J(f"(()=>{{const e=[...document.querySelectorAll('svg [role=button]')].find(x=>(x.getAttribute('aria-label')||'').startsWith('{t}:')); return e?e.getAttribute('aria-label'):null;}})()")
    tap=lambda t: J(f"(()=>{{const e=[...document.querySelectorAll('svg [role=button]')].find(x=>(x.getAttribute('aria-label')||'').startsWith('{t}:')); e.dispatchEvent(new MouseEvent('click',{{bubbles:true}})); return 'ok';}})()")
    T=lambda: J("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).filter(Boolean).join(' | ')")
    if PARTE in ('a','all'):
        c.size(1440,900); c.goto(f'http://127.0.0.1:{p}/IN-04.dc.html'); time.sleep(.6)
        chk('sem erro de render', 'renderVals' not in J("document.body.innerText"))
        sh=J("document.documentElement.scrollHeight"); chk('scrollHeight <= 900',sh<=900,sh)
        chk('barra vertical com as 9 funcionalidades',J("document.querySelectorAll('nav[aria-label=\"Funcionalidades do mapa\"] [role=tab]').length")==9 and all(x in J("document.querySelector('nav[aria-label=\"Funcionalidades do mapa\"]').innerText") for x in ['Integrado','Satélite','Solo','Irrigação','Custos']))
        chk('barra horizontal com filtros e indicadores da funcionalidade',J("!!document.querySelector('[role=group][aria-label^=\"Indicadores de\"]')") and 'Todas as condições' in J("document.body.innerText"))
        chk('ferramentas sobre o mapa com nomes',all(x in J("document.querySelector('[role=toolbar][aria-label=\"Ferramentas do mapa\"]').innerText") for x in ['Selecionar área','Medir','Tela cheia']))
        fo=J("[...document.querySelectorAll('svg foreignObject')].map(t=>t.textContent).join(' ')") or ''
        chk('rótulo no talhão (foreignObject): T1 em amarelo com a OS-0430 a liberar pelo agrônomo', 'OS-0430 a liberar' in fo and 'aguarda agrônomo' not in fo, J("[...document.querySelectorAll('svg text')].map(t=>t.textContent).slice(0,4).join(' / ')"))
        print('Integrado T4:', fill('T4'), lab('T4'))
        # trocar camada → Solo
        clk('Solo'); f1=fill('T4'); l1=lab('T4'); print('Solo V% T4:',f1,l1)
        chk('camada Solo ativa', 'V 41' in (l1 or ''), l1)
        clk('K'); f2=fill('T4'); l2=lab('T4'); print('Solo K T4:',f2,l2)
        clk('P'); f3=fill('T1'); print('Solo P T1', f3, lab('T1'))
        clk('MO'); f4=fill('T1'); print('Solo MO T1', f4, lab('T1'))
        chk('filtro muda cor do talhão (P→MO no T1)', f3!=f4, f'{f3} → {f4}')
        clk('20–40 cm'); print('20–40 T2', fill('T2'), lab('T2'))
        # satélite
        clk('Satélite'); a=fill('P2'); clk('06/09'); b=fill('P2'); print('P2 21/09',a,'06/09',b)
        chk('Satélite: cena 06/09 deixa P2 hachurado (nuvem)', a!=b and 'hatch' in (b or ''), f'{a} → {b}')
        clk('21/09'); clk('NDWI'); print('NDWI P1', fill('P1'), lab('P1')); clk('NDVI')
        # clicar talhão → painel
        tap('T7'); time.sleep(.4)
        pan=J("(document.querySelector('aside[aria-label^=\"T7\"]')||{}).innerText||''")
        chk('clique no T7 abre painel com vigor', 'NDVI' in pan and 'Programar vistoria' in pan, pan[:160].replace('\n',' / '))
        clk('Programar vistoria','aside[aria-label^="T7"]'); t1=T(); chk('Programar vistoria (inspeção da mancha) gera VIS-018', 'VIS-018 programada para T7 × inspeção de mancha' in t1, t1[:100])
        clk('Programar vistoria','aside[aria-label^="T7"]')
        chk('sem duplicar vistoria', 'Abrir VIS-018' in J("(document.querySelector('aside[aria-label^=\"T7\"]')||{}).innerText||''"))
        sh=J("document.documentElement.scrollHeight"); chk('scrollHeight <= 900 com painel',sh<=900,sh)
        c.shot(os.path.join(os.path.dirname(R),'_shots','IN-04_satelite_T7.png'))
        # O.S./prazos
        clk('Ordens de serviço'); tap('T4'); time.sleep(.3)
        pan=J("(document.querySelector('aside[aria-label^=\"T4\"]')||{}).innerText||''")
        chk('O.S.: painel do T4 com ordem, fase e Abrir ordem', 'OS-0420' in pan and 'Em execução' in pan and 'Abrir ordem' in pan, pan[:200].replace('\n',' / '))
        chk('OS-0420 com o selo do registro (impedida, sem selo de revisão)', 'Impedida · ativo bloqueado' in pan and 'Revisão de saldo' not in pan, pan[:300].replace('\n',' / '))
        href=J("(()=>{const a=[...document.querySelectorAll('aside[aria-label^=\"T4\"] a')].find(a=>a.innerText.trim()==='Abrir ordem'); return a?a.getAttribute('href'):null;})()")
        chk('Abrir ordem → detalhe da OS-0420', href=='CA-01x-os0420.dc.html', href)
        b0=fill('P1'); clk('Encerradas'); b1=fill('P1'); print('fase Encerradas P1', b0,'→',b1)
        chk('filtro de fase recolore P1', b0!=b1)
        clk('A liberar'); tap('P2'); time.sleep(.3)
        pan=J("(document.querySelector('aside[aria-label^=\"P2\"]')||{}).innerText||''"); chk('OS-0422 no mapa (A liberar)', 'OS-0422' in pan, pan[:160].replace('\n',' / '))
        c.shot(os.path.join(os.path.dirname(R),'_shots','IN-04_os_P2.png'))
        clk('Todas'); tap('P2'); time.sleep(.2)
        # seleção múltipla
        clk('Selecionar área'); tap('T1'); tap('T2'); time.sleep(.3)
        pan=J("(document.querySelector('aside[aria-label^=\"Área selecionada\"]')||{}).innerText||''"); chk('Selecionar área soma talhões', '610 ha' in pan, pan[:120].replace('\n',' / '))
        clk('Selecionar área')
        clk('Tela cheia'); chk('tela cheia abre', J("!!document.querySelector('[role=dialog][aria-label=\"Mapa em tela cheia\"]')"))
        DLG='[role=dialog][aria-label="Mapa em tela cheia"]'
        s_nav=json.dumps(DLG+' nav[aria-label="Funcionalidades do mapa"] [role=tab]'); s_tb=json.dumps(DLG+' [role=toolbar]')
        s_ind=json.dumps(DLG+' [role=group][aria-label^="Indicadores de"]'); s_tbb=json.dumps(DLG+' [role=toolbar] button')
        chk('tela cheia mantém a barra vertical (9 funcionalidades)', J("document.querySelectorAll("+s_nav+").length")==9)
        tb=J("(document.querySelector("+s_tb+")||{innerText:''}).innerText") or ''
        chk('tela cheia mantém ferramentas, filtros e indicadores', all(x in tb for x in ['Selecionar área','Medir','Sair da tela cheia']) and J("!!document.querySelector("+s_ind+")"), tb)
        chk('item de tela cheia aparece ligado', J("(()=>{const b=[...document.querySelectorAll("+s_tbb+")].find(b=>b.innerText.trim()==='Sair da tela cheia'); return b?b.getAttribute('aria-pressed'):null;})()")=='true')
        c.shot(os.path.join(os.path.dirname(R),'_shots','IN-04_full.png'))
        clk('Sair da tela cheia')
        for lay in ['Integrado','Pragas e doenças','Irrigação','Estádio','Colheita e produtividade','Custos']:
            clk(lay); tap('P1'); time.sleep(.25); pn=J("(document.querySelector('aside[aria-label^=\"P1\"]')||{}).innerText||''")
            chk('painel '+lay, len(pn)>40, pn[:90].replace('\n',' / ')); tap('P1')
    # parte b abre o mapa de novo e recria a VIS-018 no T7 (a numeração das vistorias segue a da parte a)
    if PARTE=='b':
        c.size(1440,900); c.goto(f'http://127.0.0.1:{p}/Main.dc.html')   # o mapa abre na Lagoa Grande (01/10): os talhões desenhados são da Santa Rita
        J("localStorage.removeItem('talhao-os-mip-v1'); sessionStorage.setItem('mapa-ctx',JSON.stringify({mf_faz:'Santa Rita'}))")
        c.goto(f'http://127.0.0.1:{p}/IN-04.dc.html'); time.sleep(.6)
        clk('Satélite'); tap('T7'); time.sleep(.3); clk('Programar vistoria','aside[aria-label^="T7"]'); tap('T7')
    if PARTE in ('b','all'):
        # "Programar vistoria" da barra do MIP/MID = modo que programa a vistoria no talhão clicado (mesma função do painel e do AG-01)
        VB="(()=>{const b=[...document.querySelectorAll('button')].find(b=>b.innerText.trim()==='Programar vistoria' && b.title==='Clique no talhão para programar a vistoria'); return b;})()"
        vbar=lambda: J(f"(()=>{{const b={VB}; return b?b.getAttribute('aria-pressed'):null;}})()")
        vclk=lambda: (J(f"{VB}.click()"), time.sleep(.4))
        panof=lambda t: J(f"(document.querySelector('aside[aria-label^=\"{t}\"]')||{{}}).innerText||''") or ''
        clk('Pragas e doenças')
        chk('MIP/MID: Programar vistoria na barra é botão de modo, não link para AG-01', vbar()=='false' and not J("[...document.querySelectorAll('a')].some(a=>a.innerText.trim().startsWith('Programar vistoria'))"))
        vclk(); chk('modo ligado: selo "Programar vistoria · clique num talhão"', vbar()=='true' and 'Programar vistoria · clique num talhão' in (T() or ''), T())
        tap('T4'); time.sleep(.4); t1=T()
        chk('clique no T4 programa VIS-019 (protocolo da soja em pré-plantio, mesma função do painel)', 'VIS-019 programada para T4 × nematoide-de-cisto' in t1, t1)
        chk('painel do T4 mostra a vistoria programada', 'Abrir VIS-019' in panof('T4'), panof('T4')[:200].replace('\n',' / '))
        tap('T4'); time.sleep(.4); chk('clicar de novo não duplica', 'VIS-019 já está aberta para T4 · nenhuma vistoria duplicada.' in T(), T())
        vclk(); chk('botão desliga o modo', vbar()=='false' and 'Programar vistoria · clique num talhão' not in (T() or ''))
        tap('P1'); time.sleep(.3); vclk(); t1=T()
        chk('com talhão selecionado, age direto sem ligar o modo (P1 já tem a VIS-014 aberta: não duplica)', 'VIS-014 já está aberta para P1' in t1 and vbar()=='false', t1)
        tap('P1'); vclk(); clk('Medir')
        chk('Medir desliga o modo Programar vistoria', vbar()=='false' and 'Medir · clique num talhão' in (T() or ''))
        clk('Medir')
        clk('Selecionar área'); tap('T1'); tap('T2'); time.sleep(.3)
        clk('Programar vistoria nas áreas'); t1=T()
        chk('seleção múltipla programa uma vistoria por talhão (T2 já tem a VIS-017)', 'VIS-020 programada para T1 × nematoide-de-cisto · VIS-017 já está aberta para T2' in t1, t1)
        clk('Programar vistoria nas áreas'); chk('seleção múltipla não duplica', 'VIS-020 já está aberta para T1 · VIS-017 já está aberta para T2 · nenhuma vistoria duplicada.' in T(), T())
        clk('Selecionar área'); clk('Limpar seleção')
        # geometria: T1 com polígono v3 validado e a parcela T1-B sem polígono (sem desenhar a T1-B)
        clk('Integrado'); tap('T1'); time.sleep(.3); pn=panof('T1')
        chk('Integrado · T1: linha Geometria com a T1-B sem polígono', 'Geometria' in pn and 'polígono v3 validado 12/09 · T1-B sem polígono' in pn, pn[:400].replace('\n',' / '))
        tap('T1'); tap('T2'); time.sleep(.3); chk('talhão sem pendência de geometria não ganha a linha', 'Geometria' not in panof('T2')); tap('T2')
        clk('Estádio'); tap('T1'); time.sleep(.3); pn=panof('T1')
        chk('Próxima ocupação marca a T1-B sem polígono (e só ela)', 'T1-B · Soja 62 X · 152 ha · plantio 25/10/2026 · meta 62 sc/ha · sem polígono' in pn and 'T1-A · Soja 58 W · 160 ha · plantio 15/10/2026 · meta 64 sc/ha\n' in pn+'\n', pn[:500].replace('\n',' / '))
        chk('a T1-B não é desenhada no mapa', J("document.querySelectorAll('svg [role=button]').length")==8)
        tap('T1')
        # selos da O.S. no mapa iguais aos da tela de O.S.
        clk('Ordens de serviço'); tap('T2'); time.sleep(.3); pn=panof('T2')
        chk('OS-0431 no mapa: Falta máquina (sem selo de aprovação)', 'Falta máquina · Trator T1 bloqueado' in pn and 'Aprovada pelo agrônomo' not in pn, pn[:300].replace('\n',' / '))
        tap('T2'); clk('Integrado')
        nums=J("(document.querySelector('[role=group][aria-label^=\"Indicadores de\"]')||{}).innerText||''") or ''
        chk('indicador Impedidas = 2 (OS-0420 e OS-0431)', 'Impedidas 2' in nums.replace('\n',' '), nums.replace('\n',' '))
        sh=J("document.documentElement.scrollHeight"); chk('scrollHeight final <= 900',sh<=900,sh)
    if PARTE in ('c','all'):
        # lote das Aprovações (O.S. não entra na caixa: o agrônomo libera na tela O.S.; desistir segue "Cancelar sem execução")
        c.goto(f'http://127.0.0.1:{p}/IN-02.dc.html'); time.sleep(.4)
        sel=lambda rx: (J(f"""(()=>{{[...document.querySelectorAll('[role=row].g2ed')].forEach(r=>{{ if(/{rx}/.test(r.innerText)) r.querySelector('input[type=checkbox]').click(); }});}})()"""), time.sleep(.3))
        sel('Diesel|Orçamento revisado')
        clk('Aprovar selecionados'); t=T(); chk('lote: resultado por item (Diesel aprovada · Orçamento exige revisão individual)', 'Diesel' in t and 'revisão individual (não aprovadas): Orçamento revisado · safra 26/27' in t, t[:400])
        sel('Diesel')
        clk('Aprovar selecionados'); t=T(); chk('lote: Diesel já decidida, nada duplicado', 'já decididas, nada duplicado: Política de estoque · Diesel S10' in t, t[:400])
finally:
    try:
        if c: c.close()
    finally: srv.terminate()
print(f'\n{len(OK)} ok · {len(FAIL)} falhas', FAIL)
