# -*- coding: utf-8 -*-
"""Teste CDP (≤ 15 verificações) do Mapa IN-04 · decisões do agrônomo, sobras e ações sem destino repetido.
OS-0430 "Aguardando agrônomo" entra na contagem (3 decisões) e deixa o T1 amarelo; os painéis não repetem destino; "Receber sobras"
leva ao Estoque do menu; a devolução recebida pela tela EST e a revisão aprovada pela tela O.S. (cenário compartilhado) chegam ao mapa.
Uso: python3 map_decisoes_test.py (≈ 30 s)."""
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
    c.goto(f'http://127.0.0.1:{p}/IN-04.dc.html'); J("localStorage.removeItem('talhao-os-cenario-v1')"); c.goto(f'http://127.0.0.1:{p}/IN-04.dc.html',wait=1.2)
    # 1-2 · OS-0430 conta como decisão do agrônomo (cabeçalho = indicador) e deixa o T1 amarelo
    chk('1 cabeçalho e indicador: 3 decisões pendentes (OS-0418, OS-0420 e OS-0430)', '3 decisões pendentes' in head() and 'Decisões pendentes 3' in nums(), [head(),nums()])
    l1,f1=lab('T1'); chk('2 Integrado: T1 amarelo "OS-0430 aguarda agrônomo" (mesmo selo, mesma contagem)', l1=='T1: OS-0430 aguarda agrônomo' and f1==AMAR, [l1,f1])
    # 3-6 · painéis: primário = próximo passo da ordem mais urgente, sem outro botão para o mesmo destino
    tap('T1'); t1=pan('T1'); lk=links('T1'); pr=prim('T1')
    chk('3 T1: OS-0430 Aguardando agrônomo · primário "Revisar v1" → O.S. · nenhum destino repetido', 'Aguardando agrônomo' in t1 and pr==['Revisar v1','OS.dc.html'] and unico(lk), [pr,lk])
    tap('T1'); tap('P1'); lk=links('P1'); pr=prim('P1')
    chk('4 P1: primário "Revisar v2" → IN-02det · "Receber sobras" → Estoque (EST) · nenhum destino repetido',
        pr==['Revisar v2','IN-02det.dc.html'] and ['Receber sobras','EST.dc.html'] in lk and unico(lk) and not any(h=='SU-07.dc.html' for _,h in lk), [pr,lk])
    tap('P1'); tap('T7'); lk=links('T7'); pr=prim('T7')
    chk('5 T7: um só botão para IR-02 ("Resolver conflito", primário)', pr==['Resolver conflito','IR-02.dc.html'] and [h for _,h in lk].count('IR-02.dc.html')==1, [pr,lk])
    tap('T7'); tap('T4'); lk=links('T4'); pr=prim('T4')
    chk('6 T4: primário "Revisar v3" → IN-02x-os0420 · "Abrir ordem" → CA-01x-os0420 · nenhum destino repetido',
        pr==['Revisar v3','IN-02x-os0420.dc.html'] and ['Abrir ordem','CA-01x-os0420.dc.html'] in lk and unico(lk), [pr,lk])
    tap('T4')
    # 7-8 · a devolução recebida pela tela Estoque tira custódia, selo e atalho da OS-0417 no mapa
    c.size(1440,1000); c.goto(f'http://127.0.0.1:{p}/EST.dc.html',wait=1.2); clk('3 Receba devoluções'); clk('Receber devolução da REQ-031'); clk('Salvar','aside[role=dialog]'); t=T()
    chk('7 Estoque: devolução da REQ-031 recebida (500 kg → 0 kg)', '500 kg → 0 kg' in t, t)
    c.size(1440,900); c.goto(f'http://127.0.0.1:{p}/IN-04.dc.html',wait=1.2); tap('P1'); t1=pan('P1'); i=t1.find('OS-0417'); o17=t1[i:i+260]
    chk('8 mapa após a devolução: OS-0417 sem "Sobras a receber", sem custódia e sem "Receber sobras"',
        i>=0 and 'Sobras a receber' not in o17 and 'custódia' not in o17 and 'Receber sobras' not in t1 and '95/95 ha' in o17, o17.replace('\n',' / '))
    tap('P1')
    # 9-11 · a revisão aprovada pela tela O.S. sai da contagem e o T1 volta ao verde
    c.size(1440,1000); c.goto(f'http://127.0.0.1:{p}/OS.dc.html',wait=1.2)
    J("(()=>{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.trim().startsWith('OS-0430')); r&&r.click();})()"); time.sleep(.4)
    clk('Revisar versão','aside[role=dialog]'); clk('Aprovar versão','aside[role=dialog]'); t=T()
    chk('9 O.S.: versão v1 da OS-0430 aprovada (APV-0430-v1)', 'APV-0430-v1' in t, t)
    c.size(1440,900); c.goto(f'http://127.0.0.1:{p}/IN-04.dc.html',wait=1.2)
    chk('10 mapa após a aprovação: 2 decisões pendentes no cabeçalho e no indicador', '2 decisões pendentes' in head() and 'Decisões pendentes 2' in nums(), [head(),nums()])
    l1,f1=lab('T1'); tap('T1'); t1=pan('T1'); lk=links('T1'); pr=prim('T1')
    chk('11 T1 volta ao verde; OS-0430 "Aprovada pelo agrônomo", primário "Abrir OS-0430" sem repetir destino',
        l1=='T1: OS-0421 · 190/350 ha' and f1==VERDE and 'Aprovada pelo agrônomo' in t1 and 'Aguardando agrônomo' not in t1 and pr==['Abrir OS-0430','OS.dc.html'] and unico(lk), [l1,f1,pr,lk])
    tap('T1')
    sh=J("document.documentElement.scrollHeight"); chk('12 sem rolagem (≤ 900)', sh<=900, sh)
finally:
    try:
        if c: c.close()
    finally: srv.terminate()
print(f'\n{len(OK)} ok · {len(FAIL)} falhas', FAIL)
