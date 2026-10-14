# -*- coding: utf-8 -*-
"""Teste CDP (≤ 15 verificações) do Mapa IN-04 e da caixa do Início após a regra "irrigação só com água sem agrônomo":
camada Irrigação (OS-0419/0422/0423), filtro Fazenda do topo (Santa Rita / Boa Vista / Todas), fase e realizado vindos do
cenário compartilhado (localStorage talhao-os-cenario-v1), Aprovações sem O.S. nem exceção de água e Agenda.
Decisões do proprietário de 01/10/2026: a barra do mapa tem Integrado, Satélite, Lavoura, Pragas e doenças, Irrigação, Ordens de serviço,
Insumos e Custos, e o painel do talhão mostra só a camada escolhida. As ordens só de água (OS-0419, OS-0422, OS-0423) não são O.S.
agrícolas: ficam fora da camada Ordens de serviço, das suas contagens e de "Ordens abertas" do Integrado, e vivem na camada Irrigação
("Abrir ordem" → IR-03det#OS-xxxx; o primário leva direto à ação: conflito → IR-03det#OS-0423:conflito). A fertirrigação OS-0418
continua na O.S. 02/10: a camada Irrigação e a cor do Integrado vêm do estado compartilhado da irrigação (talhao-os-irrigacao-v1),
o mesmo das telas IR-01..IR-04."""
import sys, os, time, subprocess, json, re
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
from cdp import Chrome
from journeys import free
import cenario
R=os.path.join(HERE,'_render'); p=free(); SH=os.path.join(HERE,'_probe'); os.makedirs(SH,exist_ok=True)
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
    labs=lambda: J(f"{SV}.map(x=>x.getAttribute('aria-label')||'')") or []
    tap=lambda t: (J(f"{SV}.find(x=>(x.getAttribute('aria-label')||'').startsWith('{t}:')).dispatchEvent(new MouseEvent('click',{{bubbles:true}}))"),time.sleep(.35))
    pan=lambda t: J(f"(document.querySelector('aside[aria-label^=\"{t}\"]')||{{}}).innerText||''") or ''
    href=lambda t,txt: J(f"(()=>{{const a=[...document.querySelectorAll('aside[aria-label^=\"{t}\"] a')].filter(a=>a.innerText.trim()==={json.dumps(txt)}); return a.map(x=>x.getAttribute('href'));}})()")
    # "Abrir ordem" de cada ordem do painel: [id da ordem do cartão, destino]
    ORD="""(t=>[...document.querySelectorAll('aside[aria-label^="'+t+'"] a')].filter(a=>a.innerText.trim()==='Abrir ordem').map(a=>{let e=a.parentElement; while(e && !/O[SB]-0\\d\\d\\d/.test(e.innerText)) e=e.parentElement; const m=(e?e.innerText:'').match(/O[SB]-0\\d\\d\\d/g)||[]; return [[...new Set(m)].join(','), a.getAttribute('href')];}))"""
    abrir=lambda t: J(f"({ORD})({json.dumps(t)})") or []
    RAIL="[...document.querySelectorAll('nav[aria-label=\"Funcionalidades do mapa\"] button')]"
    def camada(nome): r=J(f"(()=>{{const b={RAIL}.find(b=>(b.getAttribute('title')||'').startsWith('Mostrar {nome} no mapa')); if(!b) return 'sem botão'; b.click(); return 'ok';}})()"); time.sleep(.4); return r
    body=lambda: J("document.body.innerText") or ''
    head=lambda: J("document.querySelector('header').innerText.replace(/\\n/g,' | ')") or ''
    nums=lambda: (J("(document.querySelector('[role=group][aria-label^=\"Indicadores de\"]')||{innerText:''}).innerText") or '').replace('\n',' ')
    num=lambda rot,txt: (lambda m: int(m.group(1)) if m else None)(re.search(re.escape(rot)+r' (\d+)',txt))
    sh=lambda: J("document.documentElement.scrollHeight")
    AGUA=('OS-0419','OS-0422','OS-0423')
    c.size(1440,900); c.goto(f'http://127.0.0.1:{p}/Main.dc.html'); time.sleep(.4)
    J("localStorage.removeItem('talhao-os-cenario-v1'); localStorage.removeItem('talhao-os-irrigacao-v1')")
    J("sessionStorage.setItem('mapa-ctx','{\"mf_faz\":\"Santa Rita\"}')"); c.goto(f'http://127.0.0.1:{p}/IN-04.dc.html',wait=1.2)  # mapa na Santa Rita (01/10: abre na Lagoa Grande), camada Integrado
    # 1-2 · abre na Santa Rita sem rolagem; cabeçalho com as impedidas e as ordens a liberar pelo agrônomo (nenhuma decisão de O.S.)
    chk('1 IN-04 abre sem erro, Santa Rita, sem rolagem', J("window.__err||''")=='' and J("document.querySelector('select[aria-label=\"Filtrar por fazenda\"]').value")=='Santa Rita' and sh()<=900, sh())
    chk('2 cabeçalho: OS-0420 e OS-0431 impedidas · 2 a liberar (OS-0418 e OS-0430), sem "decisões"', 'OS-0420 e OS-0431 impedidas · 2 a liberar' in head() and 'decis' not in head(), head())
    # 3-6 · barra de 01/10 (Irrigação de volta, Pragas e doenças); as ordens de água vivem na camada Irrigação
    rail=J(f"{RAIL}.map(b=>b.innerText.trim())") or []
    # + Análises de solo (afb2f46) e Colheita (0346e66, pedido do proprietário de 14/10 = DEC-0910-36)
    chk('3 barra: Integrado, Satélite, Lavoura, Análises de solo, Pragas e doenças, Carência e destino (MAPA-CARENCIA-LMR-20261003), Colheita, Irrigação, Ordens de serviço, Insumos, Custos',
        rail==['Integrado','Satélite','Lavoura','Análises de solo','Pragas e doenças','Carência e destino','Colheita','Irrigação','Ordens de serviço','Insumos','Custos'], rail)
    l7,f7=lab('T7'); l2,f2=lab('P2')
    # 01/10: o Integrado fala da irrigação sem citar a ordem de água como O.S. (ela é do módulo Irrigação); 02/10: a cor vem do estado da irrigação
    chk('4 Integrado: T7 vermelho (irrigação em conflito); P2 amarelo (irrigação · conferir medição da passagem parcial), sem número de ordem de água', 'irrigação em conflito' in (l7 or '') and 'OS-0423' not in (l7 or '') and f7=='#C8553D' and 'conferir medição' in (l2 or '') and 'OS-0394' not in (l2 or '') and f2=='#D4B25A', [l7,f7,l2,f2])
    n_int=nums()  # "Ordens abertas" do Integrado (conferido com a tela O.S. no fim)
    r=camada('Irrigação'); tap('T7'); t7=pan('T7')
    chk('5 camada Irrigação, painel T7: OS-0423 em conflito com a parada da B3, dono Caio (PCP), Resolver conflito → IR-03det#OS-0423:conflito e Abrir ordem → IR-03det#OS-0423',
        r=='ok' and 'Conflito · parada da B3' in t7 and 'Caio' in t7 and 'PCP' in t7 and href('T7','Resolver conflito')==['IR-03det.dc.html#OS-0423:conflito'] and abrir('T7')==[['OS-0423','IR-03det.dc.html#OS-0423']], [r,abrir('T7'),t7[:400].replace('\n',' / ')])
    tap('T7'); tap('P2'); t2=pan('P2'); a2=abrir('P2'); h2=href('P2','Conferir medição'); tap('P2'); tap('P1'); a1=abrir('P1'); h1=href('P1','Programar só água'); tap('P1')
    # sem destino repetido: o cartão cuja ordem já é o primário do rodapé não tem link próprio
    chk('6 camada Irrigação, painel P2: primário Conferir medição → IR-03det#OS-0394:conferir; OS-0419 Liberadas e OS-0422 Janela a definir com link ao registro · P1: OS-0418 parada por falta de insumo (link à O.S.) e primário Programar só água → IR-02#programar=P1',
        'OS-0419 · Irrigação · água' in t2 and 'Liberadas' in t2 and 'Janela a definir' in t2 and h2==['IR-03det.dc.html#OS-0394:conferir']
        and ['OS-0419','IR-03det.dc.html#OS-0419'] in a2 and ['OS-0422','IR-03det.dc.html#OS-0422'] in a2 and a1==[['OS-0418','OS.dc.html#OS-0418']] and h1==['IR-02.dc.html#programar=P1'], [a2,h2,a1,h1,t2[:500].replace('\n',' / ')])
    # camada Ordens de serviço: contagens e rótulos sem as ordens de água (conferidos com a tela O.S. no fim)
    camada('Ordens de serviço'); n_os=nums(); l_os=labs(); camada('Integrado')
    chk('7 mapa sem exceção de água: nenhum link para IN-02x-os0422 nem "política"', J("document.querySelectorAll('a[href*=\"os0422\"]').length")==0 and 'política' not in body() and 'exceção' not in body().lower())
    # 8-10 · filtro Fazenda do topo
    faz('Boa Vista')
    chk('8 Boa Vista: estado vazio com Cadastrar talhões → CD-01, sem talhões nem indicadores',
        'Nenhum talhão desenhado na Boa Vista' in body() and J("(()=>{const a=[...document.querySelectorAll('a')].find(a=>a.innerText.trim()==='Cadastrar talhões'); return a?a.getAttribute('href'):null;})()")=='CD-01.dc.html'
        and J(f"{SV}.length")==0 and J("(document.querySelector('[role=group][aria-label^=\"Indicadores de\"]')||{innerText:''}).innerText.trim()")=='', body()[:300])
    chk('9 Boa Vista: cabeçalho "Boa Vista sem talhões desenhados" e sem rolagem', 'Boa Vista sem talhões desenhados' in head() and sh()<=900, [head(),sh()])
    c.shot(os.path.join(SH,'IN-04_boavista.png'))
    faz('Todas')
    chk('10 Todas: Santa Rita desenhada (8 talhões) + aviso "Boa Vista sem geometria"', J(f"{SV}.length")==8 and 'Boa Vista sem geometria' in body() and 'impedidas' in head(), head())
    c.shot(os.path.join(SH,'IN-04_todas_irrig.png'))
    faz('Santa Rita')
    # 11-12 · cenário compartilhado: outra tela muda a OS-0424 (turno fechado) e devolve a sobra da OS-0417
    s=cenario.seed(); s['rev']=7
    s['ordens']['OS-0424'].update(etapa='Em execução',realizado=20,saldo=108)   # G1 do CTL-1: OS-0424 na soja do T1-B (128 ha), não mais no milho do P2
    it=s['reqs']['REQ-031']['itens'][0]; it['devolvido']+=it['custodia']; it['custodia']=0
    J(f"localStorage.setItem('talhao-os-cenario-v1',{json.dumps(json.dumps(s,ensure_ascii=False))}); window.dispatchEvent(new StorageEvent('storage',{{key:'talhao-os-cenario-v1'}}))"); time.sleep(.4)
    camada('Ordens de serviço'); tap('P2'); t2=pan('P2'); tap('P2'); tap('T1'); tt1=pan('T1')
    chk('11 cenário (camada Ordens de serviço): OS-0424 (T1-B) aparece Em execução com 20/128 ha · saldo 108 ha no T1 (sem recarregar) · P2 sem a OS-0424 e sem as ordens de água OS-0419/OS-0422',
        'OS-0424 · Pulverização · Fungicida A' in tt1 and '20/128 ha · saldo 108 ha' in tt1 and 'Em execução' in tt1 and 'OS-0424' not in t2 and not any(x in t2 for x in AGUA), (t2[:200].replace('\n',' / '), tt1[:700].replace('\n',' / ')))
    tap('T1'); tap('P1'); t1=pan('P1')
    chk('12 cenário: sobra da OS-0417 recebida → sem custódia, sem selo "Sobras a receber" e sem "Receber sobras"', '95/95 ha' in t1 and 'custódia' not in t1 and 'Receber sobras' not in t1 and 'Sobras a receber' not in t1, t1[:500].replace('\n',' / '))
    J("localStorage.removeItem('talhao-os-cenario-v1')")
    # 13-14 · caixa de Aprovações (sem O.S.) e Agenda
    c.goto(f'http://127.0.0.1:{p}/IN-02.dc.html'); time.sleep(.3); b=body()
    rows=J("[...document.querySelectorAll('[role=row].g2ed')].map(r=>r.innerText.split('\\n')[0])") or []
    chk('13 Aprovações sem O.S., sem exceção de água nem PA-08: 4 decisões · 1 vence hoje', len(rows)==4 and not any(r.startswith('OS-0') for r in rows) and 'Exceção de água' not in b and 'PA-08' not in b and 'OS-0423' not in b and '4 pendentes · 1 vence hoje' in b, [rows,head()])
    c.goto(f'http://127.0.0.1:{p}/IN-03.dc.html'); time.sleep(1.2); b=body()
    rg=lambda s: J(f"(()=>{{const r=[...document.querySelectorAll('[role=row]')].find(r=>r.innerText.indexOf({json.dumps(s)})>=0); return r?r.innerText.replace(/\\s+/g,' '):'';}})()") or ''
    chk('14 Agenda (lida do estado da irrigação): sem "Renovar política"; conflito da OS-0423 com a parada da B3 com Caio e janela da OS-0422 com João',
        'Renovar política' not in b and 'Resolver conflito · OS-0423' in rg('OS-0423') and 'parada da B3' in rg('OS-0423') and 'Caio' in rg('OS-0423') and 'Definir janela · OS-0422' in rg('OS-0422') and 'João' in rg('OS-0422'), [rg('OS-0423'), rg('OS-0422')])
    # 15 · contagens do mapa = tela O.S. (Santa Rita, cenário limpo): ordens de água fora da camada Ordens de serviço e de "Ordens abertas"
    c.size(1440,1000); c.goto(f'http://127.0.0.1:{p}/OS.dc.html',wait=1.2)
    os_rows=J("[...document.querySelectorAll('[role=row].g2ed')].map(r=>r.innerText.replace(/\\s+/g,' ').trim())") or []
    ids=[r.split(' ')[0] for r in os_rows if r.startswith('OS-')]; abertas=[r.split(' ')[0] for r in os_rows if r.startswith('OS-') and 'Encerradas' not in r]
    fz=J("(document.querySelector('select[aria-label=\"Filtrar por fazenda\"]')||{}).value")
    chk('15 contagens sem água: camada Ordens de serviço "Ordens" = ordens OS da tela O.S. e "Ordens abertas" do Integrado = abertas da tela O.S.; nenhum rótulo nem a tela O.S. com OS-0419/0422/0423',
        fz=='Santa Rita' and len(ids)>0 and num('Ordens',n_os)==len(ids) and num('Ordens abertas',n_int)==len(abertas)
        and not any(x in ids for x in AGUA) and not any(x in l for l in l_os for x in AGUA), [fz,ids,abertas,n_os,n_int,l_os])
finally:
    try:
        if c: c.close()
    finally: srv.terminate()
print(f'\n{len(OK)} ok · {len(FAIL)} falhas', FAIL)
