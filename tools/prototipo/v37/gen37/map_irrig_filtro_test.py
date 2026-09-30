# -*- coding: utf-8 -*-
"""Teste CDP (≤ 15 verificações) do Mapa IN-04 e da caixa do Início após a regra "irrigação só com água sem agrônomo":
camada Irrigação (OS-0419/0422/0423), filtro Fazenda do topo (Santa Rita / Boa Vista / Todas), fase e realizado vindos do
cenário compartilhado (localStorage talhao-os-cenario-v1), Aprovações sem exceção de água, próxima pendência e Agenda."""
import sys, os, time, subprocess, json
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
from cdp import Chrome
from journeys import free
import cenario
R=os.path.join(HERE,'_render'); p=free()
srv=subprocess.Popen(['python3','-m','http.server',str(p),'--bind','127.0.0.1','--directory',R],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(0.8)
c=None; OK=[]; FAIL=[]
def chk(nome,cond,info=''):
    (OK if cond else FAIL).append(nome); print(('OK   ' if cond else 'FALHA'),nome,('' if cond else info))
try:
    c=Chrome(port=free()); J=c.js
    CLK="""((t,root)=>{const r=root?document.querySelector(root):document; if(!r) return 'SEM RAIZ'; const n=s=>(s||'').replace(/\\s+/g,' ').trim(); const els=[...r.querySelectorAll('button,a')]; const e=els.find(x=>n(x.innerText)===t)||els.find(x=>n(x.innerText).startsWith(t)); if(!e) return 'NÃO ACHEI: '+t; e.click(); return 'ok';})"""
    SETV="""((sel,val)=>{const i=document.querySelector(sel); Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype,'value').set.call(i,val); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true}));})"""
    def clk(t,root=None): r=J(f"({CLK})({json.dumps(t)},{json.dumps(root)})"); time.sleep(.35); return r
    def faz(v): J(f"({SETV})('select[aria-label=\"Filtrar por fazenda\"]',{json.dumps(v)})"); time.sleep(.4)
    SV="[...document.querySelectorAll('svg [role=button]')]"
    lab=lambda t: J(f"(()=>{{const e={SV}.find(x=>(x.getAttribute('aria-label')||'').startsWith('{t}:')); return e?[e.getAttribute('aria-label'),e.getAttribute('fill')]:[null,null];}})()")
    tap=lambda t: (J(f"{SV}.find(x=>(x.getAttribute('aria-label')||'').startsWith('{t}:')).dispatchEvent(new MouseEvent('click',{{bubbles:true}}))"),time.sleep(.35))
    pan=lambda t: J(f"(document.querySelector('aside[aria-label^=\"{t}\"]')||{{}}).innerText||''") or ''
    href=lambda t,txt: J(f"(()=>{{const a=[...document.querySelectorAll('aside[aria-label^=\"{t}\"] a')].filter(a=>a.innerText.trim()==={json.dumps(txt)}); return a.map(x=>x.getAttribute('href'));}})()")
    body=lambda: J("document.body.innerText") or ''
    head=lambda: J("document.querySelector('header').innerText.replace(/\\n/g,' | ')") or ''
    sh=lambda: J("document.documentElement.scrollHeight")
    c.size(1440,900); c.goto(f'http://127.0.0.1:{p}/IN-04.dc.html'); time.sleep(.4)
    J("localStorage.removeItem('talhao-os-cenario-v1')")
    # 1-2 · abre na Santa Rita sem rolagem; cabeçalho só com impedidas e decisões do agrônomo
    chk('1 IN-04 abre sem erro, Santa Rita, sem rolagem', J("window.__err||''")=='' and J("document.querySelector('select[aria-label=\"Filtrar por fazenda\"]').value")=='Santa Rita' and sh()<=900, sh())
    chk('2 cabeçalho: OS-0420 e OS-0431 impedidas · 3 decisões pendentes (OS-0418, OS-0420 e OS-0430)', 'OS-0420 e OS-0431 impedidas · 3 decisões pendentes' in head(), head())
    # 3-6 · camada Irrigação, programação de hoje
    clk('Irrigação'); clk('Programação de hoje')
    leg=J("(([...document.querySelectorAll('div')].filter(d=>d.innerText.trim().endsWith('Geometria e valores demonstrativos.')).pop())||{innerText:''}).innerText.replace(/\\n/g,' / ')") or ''
    chk('3 legenda: liberada hoje / aguardando decisão (só fertirrigação) / pendência operacional / sem programação',
        all(x in leg for x in ['liberada hoje','aguardando decisão (só fertirrigação)','pendência operacional (janela ou conflito)','sem programação']) and 'política' not in leg, leg)
    l7,f7=lab('T7'); l2,f2=lab('P2')
    chk('4 T7 vermelho "Conflito · parada da B3"; P2 azul (OS-0419 liberada hoje)', 'Conflito · parada da B3' in (l7 or '') and f7=='#C8553D' and f2=='#6E9FC6', [l7,f7,l2,f2])
    tap('T7'); t7=pan('T7')
    chk('5 painel T7: conflito, dono Caio · PCP e atalho Resolver conflito → IR-02', 'Conflito · parada da B3' in t7 and 'dono: Caio · PCP' in t7 and href('T7','Resolver conflito')==['IR-02.dc.html'], t7[:400].replace('\n',' / '))
    tap('T7'); tap('P2'); t2=pan('P2')
    chk('6 painel P2: OS-0419 pela necessidade do balanço · OS-0422 Janela a definir, dono João, Definir janela → IR-02',
        'liberada pela necessidade do balanço · 10,81 mm · hoje 20:00–amanhã 10:31 (14,5 h)' in t2 and 'Janela a definir' in t2 and 'dono: João' in t2 and href('P2','Definir janela')==['IR-02.dc.html'], t2[:500].replace('\n',' / '))
    tap('P2')
    chk('7 mapa sem exceção de água: nenhum link para IN-02x-os0422 nem "política"', J("document.querySelectorAll('a[href*=\"os0422\"]').length")==0 and 'política' not in body() and 'exceção' not in body().lower())
    # 8-10 · filtro Fazenda do topo
    faz('Boa Vista')
    chk('8 Boa Vista: estado vazio com Cadastrar talhões → CD-01, sem talhões nem indicadores',
        'Nenhum talhão desenhado na Boa Vista' in body() and J("(()=>{const a=[...document.querySelectorAll('a')].find(a=>a.innerText.trim()==='Cadastrar talhões'); return a?a.getAttribute('href'):null;})()")=='CD-01.dc.html'
        and J(f"{SV}.length")==0 and J("(document.querySelector('[role=group][aria-label^=\"Indicadores de\"]')||{innerText:''}).innerText.trim()")=='', body()[:300])
    chk('9 Boa Vista: cabeçalho "Boa Vista sem talhões desenhados" e sem rolagem', 'Boa Vista sem talhões desenhados' in head() and sh()<=900, [head(),sh()])
    c.shot(os.path.join(HERE,'_shots','IN-04_boavista.png'))
    faz('Todas')
    chk('10 Todas: Santa Rita desenhada (8 talhões) + aviso "Boa Vista sem geometria"', J(f"{SV}.length")==8 and 'Boa Vista sem geometria' in body() and 'impedidas' in head(), head())
    c.shot(os.path.join(HERE,'_shots','IN-04_todas_irrig.png'))
    faz('Santa Rita')
    # 11-12 · cenário compartilhado: outra tela muda a OS-0424 (turno fechado) e devolve a sobra da OS-0417
    s=cenario.seed(); s['rev']=7
    s['ordens']['OS-0424'].update(etapa='Em execução',realizado=20,saldo=60)
    it=s['reqs']['REQ-031']['itens'][0]; it['devolvido']+=it['custodia']; it['custodia']=0
    J(f"localStorage.setItem('talhao-os-cenario-v1',{json.dumps(json.dumps(s,ensure_ascii=False))}); window.dispatchEvent(new StorageEvent('storage',{{key:'talhao-os-cenario-v1'}}))"); time.sleep(.4)
    clk('Ordens de serviço'); tap('P2'); t2=pan('P2')
    chk('11 cenário: OS-0424 aparece Em execução com 20/80 ha · saldo 60 ha (sem recarregar)', 'OS-0424 · Pulverização · Fungicida A' in t2 and 'Janela 24/09 · 20/80 ha · saldo 60 ha' in t2 and 'Em execução' in t2, t2[:500].replace('\n',' / '))
    tap('P2'); tap('P1'); t1=pan('P1')
    chk('12 cenário: sobra da OS-0417 recebida → sem custódia, sem selo "Sobras a receber" e sem "Receber sobras"', '95/95 ha' in t1 and 'custódia' not in t1 and 'Receber sobras' not in t1 and 'Sobras a receber' not in t1, t1[:500].replace('\n',' / '))
    J("localStorage.removeItem('talhao-os-cenario-v1')")
    # 13-15 · caixa de Aprovações, próxima pendência e Agenda
    c.goto(f'http://127.0.0.1:{p}/IN-02.dc.html'); time.sleep(.3); b=body()
    rows=J("[...document.querySelectorAll('[role=row].g2ed')].map(r=>r.innerText.split('\\n')[0])") or []
    chk('13 Aprovações sem exceção de água nem PA-08: 7 decisões (com a OS-0430) · 2 vencem hoje', len(rows)==7 and 'OS-0430 · dessecação T1-A · v1' in rows and 'Exceção de água' not in b and 'PA-08' not in b and 'OS-0423' not in b and '7 pendentes · 2 vencem hoje' in b, [rows,head()])
    c.goto(f'http://127.0.0.1:{p}/IN-02x-os0420.dc.html'); time.sleep(.3); clk('Aprovar versão v3')
    nx=J("(()=>{const a=[...document.querySelectorAll('a')].find(a=>/Fila vazia|Próxima pendência/.test(a.innerText)); return a?[a.innerText.trim(),a.getAttribute('href')]:null;})()")
    chk('14 após decidir a OS-0420: próxima pendência OS-0430 (a OS-0418 também segue pendente) → O.S.', nx and nx[0].startswith('Próxima pendência: OS-0430') and nx[1]=='OS.dc.html', nx)
    c.goto(f'http://127.0.0.1:{p}/IN-03.dc.html'); time.sleep(.3); b=body()
    chk('15 Agenda: sem "Renovar política"; conflito da OS-0423 com Caio e janela da OS-0422 com João',
        'Renovar política' not in b and 'Resolver conflito da OS-0423 com a parada da B3' in b and 'Definir janela da OS-0422' in b, b[:600])
finally:
    try:
        if c: c.close()
    finally: srv.terminate()
print(f'\n{len(OK)} ok · {len(FAIL)} falhas', FAIL)
