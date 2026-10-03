# -*- coding: utf-8 -*-
"""Teste CDP (≤ 15 verificações) do Mapa IN-04 · próximo passo das O.S. (liberar), sobras e ações sem destino repetido.
Decisão do proprietário de 01/10/2026: ao clicar no talhão, o painel mostra só a funcionalidade da camada escolhida. No Integrado, a seção
"NESTE TALHÃO" traz uma linha por funcionalidade com um "Ver …" que troca a camada mantendo o talhão; cartões das O.S., "Próximo passo" e
"Nova O.S. neste talhão" só aparecem na camada Ordens de serviço; as seções ficam sempre abertas. As ordens só de água (OS-0419/0422/0423)
não são O.S.: o conflito do T7 sai da camada Ordens de serviço e se resolve na camada Irrigação (02/10: direto na ação, IR-03det#OS-0423:conflito).
OS-0418 e OS-0430, a liberar pelo agrônomo, entram na contagem (2 a liberar) e deixam P1 e T1 amarelos; a OS-0420 só tem o impedimento
da máquina; os painéis não repetem destino; "Receber sobras" leva ao Estoque do menu; a devolução recebida pela tela EST e a liberação
feita pela tela O.S. (cenário compartilhado) chegam ao mapa. Uso: python3 map_decisoes_test.py (≈ 30 s)."""
import sys, os, time, subprocess, json
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
from cdp import Chrome
from journeys import free
R=os.path.join(HERE,'_render'); p=free()
srv=subprocess.Popen(['python3','-m','http.server',str(p),'--bind','127.0.0.1','--directory',R],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(0.8)
c=None; OK=[]; FAIL=[]
def chk(nome,cond,info=''):
    (OK if cond else FAIL).append(nome); print(('OK   ' if cond else 'FALHA'),nome,('' if cond else info))
try:
    c=Chrome(port=free()); J=c.js; c.size(1440,900)
    CLK="""((t,root)=>{const r=root?document.querySelector(root):document; if(!r) return 'SEM RAIZ'; const n=s=>(s||'').replace(/\\s+/g,' ').trim(); const els=[...r.querySelectorAll('button,a')].filter(e=>e.offsetParent!==null); const e=els.find(x=>n(x.innerText)===t)||els.find(x=>n(x.innerText).startsWith(t)); if(!e) return 'NÃO ACHEI: '+t; e.click(); return 'ok';})"""
    def clk(t,root=None): r=J(f"({CLK})({json.dumps(t)},{json.dumps(root)})"); time.sleep(.35); return r
    SV="[...document.querySelectorAll('svg [role=button]')]"
    lab=lambda t: J(f"(()=>{{const e={SV}.find(x=>(x.getAttribute('aria-label')||'').startsWith('{t}:')); return e?[e.getAttribute('aria-label'),e.getAttribute('fill')]:[null,null];}})()")
    tap=lambda t: (J(f"{SV}.find(x=>(x.getAttribute('aria-label')||'').startsWith('{t}:')).dispatchEvent(new MouseEvent('click',{{bubbles:true}}))"),time.sleep(.35))
    pan=lambda t: J(f"(document.querySelector('aside[aria-label^=\"{t}\"]')||{{}}).innerText||''") or ''
    links=lambda t: J(f"[...document.querySelectorAll('aside[aria-label^=\"{t}\"] a')].map(a=>[a.innerText.trim(),a.getAttribute('href')])") or []
    prim=lambda t: J(f"(()=>{{const a=[...document.querySelectorAll('aside[aria-label^=\"{t}\"] a')].find(a=>a.style.background.indexOf('30, 122, 76')>=0||a.style.backgroundColor.indexOf('30, 122, 76')>=0); return a?[a.innerText.trim(),a.getAttribute('href')]:null;}})()")
    unico=lambda ls: len({h for _,h in ls})==len(ls)
    head=lambda: J("document.querySelector('header').innerText.replace(/\\n/g,' | ')") or ''
    nums=lambda: (J("(document.querySelector('[role=group][aria-label^=\"Indicadores de\"]')||{innerText:''}).innerText") or '').replace('\n',' ')
    T=lambda: J("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).filter(Boolean).join(' | ')") or ''
    AMAR,VERDE='#D4B25A','#7FAE68'
    RAIL="[...document.querySelectorAll('nav[aria-label=\"Funcionalidades do mapa\"] button')]"
    def camada(nome): r=J(f"(()=>{{const b={RAIL}.find(b=>(b.getAttribute('title')||'').startsWith('Mostrar {nome} no mapa')); if(!b) return 'sem botão'; b.click(); return 'ok';}})()"); time.sleep(.4); return r
    ativa=lambda: J(f"{RAIL}.filter(b=>b.getAttribute('aria-selected')==='true').map(b=>b.innerText.trim())") or []
    ver=lambda t,txt: (J(f"(()=>{{const b=[...document.querySelectorAll('aside[aria-label^=\"{t}\"] button')].find(b=>b.innerText.trim()==={json.dumps(txt)}); if(!b) return 'sem botão'; b.click(); return 'ok';}})()"),time.sleep(.4))[0]
    def mapa(lay=None):  # mapa da Santa Rita (01/10: abre na Lagoa Grande), sem talhão escolhido; camada pedida ou Integrado
        ctx={'mf_faz':'Santa Rita'}
        if lay: ctx['lay']=lay
        J(f"sessionStorage.setItem('mapa-ctx',{json.dumps(json.dumps(ctx))})"); c.size(1440,900); c.goto(f'http://127.0.0.1:{p}/IN-04.dc.html',wait=1.2)
    c.goto(f'http://127.0.0.1:{p}/Main.dc.html'); J("localStorage.removeItem('talhao-os-cenario-v1'); localStorage.removeItem('talhao-os-irrigacao-v1')"); mapa()
    # 1-2 · nenhuma O.S. conta como decisão; OS-0418 e OS-0430 a liberar pelo agrônomo (cabeçalho = indicador) deixam o T1 amarelo
    chk('1 cabeçalho e indicador: 2 a liberar (OS-0418 e OS-0430), sem "decisões"', '2 a liberar' in head() and 'decis' not in head() and 'A liberar (agrônomo) 2' in nums() and 'Decisões' not in nums(), [head(),nums()])
    l1,f1=lab('T1'); chk('2 Integrado: T1 amarelo "OS-0430 a liberar" (mesma contagem do cabeçalho)', l1=='T1: OS-0430 a liberar' and f1==AMAR, [l1,f1])
    # 3 · Integrado (01/10): "NESTE TALHÃO" com uma linha por funcionalidade e um "Ver …"; sem cartões de O.S., próximo passo nem "Nova O.S."; nada recolhível
    tap('T1'); t1=pan('T1')
    lin=J("(()=>{const s=document.querySelector('aside[aria-label^=\"T1\"] section[aria-label=\"Neste talhão\"]'); return s?[...s.children].filter(d=>d.querySelector('button')).map(d=>[d.firstElementChild.innerText.trim(),[...d.querySelectorAll('button')].map(b=>b.innerText.trim())]):[];})()") or []
    sem_os=(J("document.querySelectorAll('aside[aria-label^=\"T1\"] [role=radio], aside[aria-label^=\"T1\"] [aria-label=\"Próximo passo\"], aside [aria-expanded], aside details').length")==0
            and 'Nova O.S. neste talhão' not in t1 and 'Liberar para execução' not in t1)
    r=ver('T1','Ver ordens'); a=ativa(); tsel=json.loads(J("sessionStorage.getItem('mapa-ctx')") or '{}').get('tsel'); t1=pan('T1')
    chk('3 Integrado T1: "NESTE TALHÃO" com Satélite, Lavoura, Pragas e doenças, Carência e destino, Irrigação, Ordens de serviço, Insumos e Custos (um "Ver …" cada), sem O.S. nem recolher · "Ver ordens" troca para Ordens de serviço com o T1 aberto',
        [n for n,_ in lin]==['Satélite','Lavoura','Pragas e doenças','Carência e destino','Irrigação','Ordens de serviço','Insumos','Custos'] and all(len(b)==1 and b[0].startswith('Ver ') for _,b in lin)
        and sem_os and r=='ok' and a==['Ordens de serviço'] and tsel==['T1'] and 'ORDENS DE SERVIÇO' in t1 and 'NESTE TALHÃO' not in t1, [lin,sem_os,r,a,tsel,t1[:200]])
    # 4-7 · camada Ordens de serviço: primário = próximo passo da ordem mais urgente, sem outro botão para o mesmo destino
    lk=links('T1')
    bt=J("[...document.querySelectorAll('aside[aria-label^=\"T1\"] [aria-label=\"Próximo passo\"] button')].map(b=>b.innerText.trim())") or []
    # Fase 1 (01/10): o painel mostra as ordens do talhão e o próximo passo da escolhida; o primário é Liberar no próprio mapa e o ajuste abre a O.S.
    chk('4 T1 (Ordens de serviço): OS-0430 A liberar · primário "Liberar para execução" · "Ajustar antes de liberar" → O.S. da OS-0430 · rodapé "Nova O.S. neste talhão" · sem revisão · nenhum destino repetido',
        'Liberar para execução' in bt and ['Ajustar antes de liberar','OS.dc.html#OS-0430:ajustar'] in lk and lk[-1:]==[['Nova O.S. neste talhão','OS.dc.html']]
        and 'Aguardando agrônomo' not in t1 and 'Revisar' not in t1 and unico(lk), [bt,lk])
    tap('T1'); tap('P1'); p1=pan('P1'); lk=links('P1'); pr=prim('P1')
    # a OS-0418 (mais urgente) vem escolhida, impedida pelo Estoque (Ureia 45 % sem lote); a OS-0417 (sobras) mostra o atalho ao Estoque quando é escolhida
    J("[...document.querySelectorAll('aside[aria-label^=\"P1\"] [role=radio]')].find(b=>b.innerText.indexOf('OS-0417')>=0).click()"); time.sleep(.35)
    lk2=links('P1'); pr2=prim('P1')
    chk('5 P1: OS-0418 com Liberar bloqueado pelo Estoque · primário "Ajustar antes de liberar" → O.S. da OS-0418 · OS-0417: "Receber devolução no Estoque" (EST) · sem IN-02det · nenhum destino repetido',
        'Liberar bloqueado' in p1 and pr==['Ajustar antes de liberar','OS.dc.html#OS-0418:ajustar'] and pr2==['Receber devolução no Estoque','EST.dc.html'] and unico(lk) and unico(lk2)
        and not any(h in ('SU-07.dc.html','IN-02det.dc.html') for _,h in lk+lk2), [pr,lk,pr2,lk2])
    tap('P1'); tap('T4'); lk=links('T4'); pr=prim('T4')
    chk('6 T4: OS-0420 parada só pela máquina · primário "Reprogramar saldo" → PL-05 · ordem completa → CA-01x-os0420 · sem IN-02x-os0420 · nenhum destino repetido',
        pr==['Reprogramar saldo','PL-05.dc.html'] and any(h=='CA-01x-os0420.dc.html' for _,h in lk) and not any('IN-02x' in (h or '') for _,h in lk) and unico(lk), [pr,lk])
    tap('T4')
    # 7 · o conflito de água do T7 (OS-0423) não é O.S. (01/10): em Ordens de serviço o T7 fica sem ordem; na camada Irrigação, um só botão que abre a ação no registro
    l7,_=lab('T7'); tap('T7'); t7=pan('T7'); tap('T7')
    r=camada('Irrigação'); tap('T7'); lk=links('T7'); pr=prim('T7'); H7='IR-03det.dc.html#OS-0423:conflito'
    chk('7 T7: sem ordem na camada Ordens de serviço · na camada Irrigação, um só botão "Resolver conflito" (primário) → IR-03det#OS-0423:conflito',
        l7=='T7: sem ordem' and 'OS-0423' not in t7 and r=='ok' and pr==['Resolver conflito',H7] and [h for _,h in lk].count(H7)==1, [l7,t7[:160],r,pr,lk])
    tap('T7')
    # 8-9 · a devolução recebida pela tela Estoque tira custódia, selo e atalho da OS-0417 no mapa
    c.size(1440,1000); c.goto(f'http://127.0.0.1:{p}/EST.dc.html',wait=1.2); clk('Receba devoluções'); clk('Receber devolução da REQ-031'); clk('Salvar','aside[role=dialog]'); t=T()
    chk('8 Estoque: devolução da REQ-031 recebida (500 kg → 0 kg)', '500 kg → 0 kg' in t, t)
    mapa('O.S./prazos'); tap('P1'); t1=pan('P1'); i=t1.find('OS-0417'); o17=t1[i:i+260]
    chk('9 mapa (Ordens de serviço) após a devolução: OS-0417 sem "Sobras a receber", sem custódia e sem "Receber sobras"',
        i>=0 and 'Sobras a receber' not in o17 and 'custódia' not in o17 and 'Receber sobras' not in t1 and '95/95 ha' in o17, o17.replace('\n',' / '))
    tap('P1')
    # 10-12 · liberar a OS-0430 pela tela O.S. (sem revisar nem aprovar antes) chega ao mapa: sai da contagem e o T1 volta ao verde
    c.size(1440,1000); c.goto(f'http://127.0.0.1:{p}/OS.dc.html',wait=1.2)
    J("(()=>{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.trim().startsWith('OS-0430')); r&&r.click();})()"); time.sleep(.4)
    clk('Liberar para execução','aside[role=dialog]'); clk('Confirmar liberação','aside[role=dialog]'); t=T()
    chk('10 O.S.: OS-0430 liberada direto pela tela O.S.', 'OS-0430 liberada' in t, t)
    mapa()
    chk('11 mapa após a liberação: 1 a liberar no cabeçalho e no indicador', '1 a liberar' in head() and 'A liberar (agrônomo) 1' in nums(), [head(),nums()])
    l1,f1=lab('T1'); tap('T1'); r=ver('T1','Ver ordens'); t1=pan('T1'); lk=links('T1')
    chk('12 T1 volta ao verde no Integrado; em Ordens de serviço ("Ver ordens") a OS-0430 está Liberadas, sem "Ajustar antes de liberar", sem repetir destino',
        l1=='T1: OS-0421 · 190/350 ha' and f1==VERDE and r=='ok' and 'Liberadas' in t1 and 'Ajustar antes de liberar' not in t1 and unico(lk), [l1,f1,r,lk])
    tap('T1')
    sh=J("document.documentElement.scrollHeight"); chk('13 sem rolagem (≤ 900)', sh<=900, sh)
finally:
    try:
        if c: c.close()
    finally: srv.terminate()
print(f'\n{len(OK)} ok · {len(FAIL)} falhas', FAIL)
