# -*- coding: utf-8 -*-
"""Teste CDP (≤ 15 verificações) da fila do agrônomo: Aprovações IN-02 e decisões IN-02x-os0420 / IN-02det.
OS-0430 na caixa (OS.dc.html); o recibo cabe no artboard (820 e 710 px, heights_override.json); a próxima pendência percorre a fila
em círculo e só diz "Fila vazia" sem nenhuma pendente; as decisões gravam no cenário e aparecem nas Aprovações, no Mapa e na O.S.;
atalhos de devolução do Meu dia e da Agenda levam ao Estoque do menu. Uso: python3 map_aprov_test.py (≈ 35 s)."""
import sys, os, time, subprocess, json
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
from cdp import Chrome
from journeys import free
R=os.path.join(HERE,'_render'); p=free()
HOV=json.load(open(os.path.join(HERE,'heights_override.json'),encoding='utf-8'))
srv=subprocess.Popen(['python3','-m','http.server',str(p),'--bind','127.0.0.1','--directory',R],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(0.8)
c=None; OK=[]; FAIL=[]
def chk(nome,cond,info=''):
    (OK if cond else FAIL).append(nome); print(('OK   ' if cond else 'FALHA'),nome,('' if cond else info))
try:
    c=Chrome(port=free()); J=c.js
    CLK="""((t,root)=>{const r=root?document.querySelector(root):document; if(!r) return 'SEM RAIZ'; const n=s=>(s||'').replace(/\\s+/g,' ').trim(); const els=[...r.querySelectorAll('button,a')].filter(e=>e.offsetParent!==null); const e=els.find(x=>n(x.innerText)===t)||els.find(x=>n(x.innerText).startsWith(t)); if(!e) return 'NÃO ACHEI: '+t; e.click(); return 'ok';})"""
    def clk(t,root=None): r=J(f"({CLK})({json.dumps(t)},{json.dumps(root)})"); time.sleep(.35); return r
    def ir(f,h=1000): c.size(1440,h); c.goto(f'http://127.0.0.1:{p}/{f}',wait=1.2)
    body=lambda: J("document.body.innerText") or ''
    head=lambda: J("document.querySelector('header').innerText.replace(/\\n/g,' | ')") or ''
    rows=lambda: J("[...document.querySelectorAll('[role=row].g2ed')].map(r=>r.innerText.replace(/\\s+/g,' '))") or []
    # recibo: texto, link da próxima pendência e posição (base do link, do recibo e do bloco Decisão) no artboard
    REC="""(()=>{const s=[...document.querySelectorAll('div[role=status]')].find(d=>/Recibo/.test(d.innerText)); if(!s) return null; const a=s.querySelector('a'); const sec=s.closest('section');
      return {t:s.innerText.replace(/\\s+/g,' '),lk:a.innerText.replace(/\\s+/g,' ').trim(),h:a.getAttribute('href'),a:Math.round(a.getBoundingClientRect().bottom),s:Math.round(s.getBoundingClientRect().bottom),sec:Math.round(sec.getBoundingClientRect().bottom),sh:document.documentElement.scrollHeight};})()"""
    ir('IN-02.dc.html'); J("localStorage.removeItem('talhao-os-cenario-v1')"); ir('IN-02.dc.html',900)
    rs=rows(); r30=next((r for r in rs if r.startswith('OS-0430')),'')
    chk('1 Aprovações: 7 decisões com a OS-0430 (alçada Agrônomo · Decidir → O.S.) · 7 pendentes · 2 vencem hoje',
        len(rs)==7 and 'alçada: Agrônomo' in r30 and J("(()=>{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.startsWith('OS-0430')); const a=r&&[...r.querySelectorAll('a')].find(a=>a.innerText.trim()==='Decidir'); return a?a.getAttribute('href'):null;})()")=='OS.dc.html'
        and '7 pendentes · 2 vencem hoje' in head() and J("document.documentElement.scrollHeight")<=HOV.get('IN-02.dc.html',900), [rs,head(),J("document.documentElement.scrollHeight")])
    # 2-3 · OS-0420 v3 no artboard de 820 px: recibo inteiro e próxima pendência = OS-0430 (a OS-0418 também segue pendente)
    H20=HOV.get('IN-02x-os0420.dc.html',900); ir('IN-02x-os0420.dc.html',H20); clk('Aprovar versão v3'); r=J(REC) or {}
    c.shot(os.path.join(HERE,'_probe','map_IN-02x-os0420_aprovada.png'))
    chk(f'2 IN-02x-os0420 em 1440×{H20}: recibo, link e bloco Decisão inteiros no artboard', r and r['a']<=H20 and r['s']<=H20 and r['sec']<=H20 and r['sh']<=H20, r)
    chk('3 próxima pendência depois da OS-0420: OS-0430 → O.S. (não "Fila vazia")', r.get('lk','').startswith('Próxima pendência: OS-0430') and r.get('h')=='OS.dc.html', r)
    # 4 · OS-0418 v2 no artboard de 710 px: a OS-0420 já decidida sai da fila; a OS-0430 continua
    H18=HOV.get('IN-02det.dc.html',900); ir('IN-02det.dc.html',H18); clk('Aprovar versão v2'); r=J(REC) or {}
    chk(f'4 IN-02det em 1440×{H18}: recibo inteiro · próxima pendência OS-0430 (OS-0420 já decidida)', r and r['sec']<=H18 and r['sh']<=H18 and r['lk'].startswith('Próxima pendência: OS-0430'), r)
    # 5 · decisão gravada no cenário: reabrir mostra o recibo, sem botão de aprovar (nada duplica)
    ir('IN-02det.dc.html',H18); r=J(REC) or {}
    chk('5 reabrir a IN-02det: recibo AP-2201 e sem "Aprovar versão v2" visível', 'AP-2201' in r.get('t','') and J("[...document.querySelectorAll('button')].some(b=>b.offsetParent&&b.innerText.trim()==='Aprovar versão v2')")==False, r)
    # 6 · Aprovações leem as decisões: OS-0418 e OS-0420 aprovadas com recibo; OS-0430 segue Decidir
    ir('IN-02.dc.html'); rs=rows(); g=lambda k: next((x for x in rs if x.startswith(k)),'')
    chk('6 Aprovações: OS-0418 "Aprovada · AP-2201", OS-0420 "Aprovada · AP-2202", OS-0430 Decidir · 5 pendentes · 1 vence hoje',
        'Aprovada · AP-2201' in g('OS-0418') and 'Aprovada · AP-2202' in g('OS-0420') and 'Decidir' in g('OS-0430') and '5 pendentes · 1 vence hoje' in head(), [rs,head()])
    # 7 · a O.S. mostra a mesma decisão (selo e recibo da OS-0418)
    ir('OS.dc.html'); J("(()=>{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.trim().startsWith('OS-0418')); r&&r.click();})()"); time.sleep(.4)
    po=J("(()=>{const a=document.querySelector('aside[role=dialog]'); return a?a.innerText.replace(/\\s+/g,' '):'';})()") or ''
    chk('7 O.S.: OS-0418 "Aprovada pelo agrônomo" com recibo AP-2201 e próximo passo Liberar', 'Aprovada pelo agrônomo' in po and 'AP-2201' in po and 'Libere para execução' in po and 'Aguardando agrônomo' not in po, [po.find('AP-2201'),po[:300]])
    # 8 · aprovar a OS-0430 na O.S. esvazia a fila: só então "Fila vazia"
    J("(()=>{const b=document.querySelector('aside[role=dialog] button[aria-label=Fechar]'); b&&b.click();})()"); time.sleep(.3)
    J("(()=>{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.trim().startsWith('OS-0430')); r&&r.click();})()"); time.sleep(.4)
    clk('Revisar versão','aside[role=dialog]'); clk('Aprovar versão','aside[role=dialog]')
    ir('IN-02x-os0420.dc.html',H20); r=J(REC) or {}
    chk('8 fila do agrônomo vazia (OS-0418, OS-0420 e OS-0430 decididas): "Fila vazia · voltar às Aprovações"', r.get('lk','').startswith('Fila vazia') and r.get('h')=='IN-02.dc.html', r)
    # 9 · Mapa: nenhuma decisão pendente e o T4 sem o "v3"
    ir('IN-04.dc.html',900); lb=J("(()=>{const e=[...document.querySelectorAll('svg [role=button]')].find(x=>(x.getAttribute('aria-label')||'').startsWith('T4:')); return e?e.getAttribute('aria-label'):'';})()")
    nm=(J("(document.querySelector('[role=group][aria-label^=\"Indicadores de\"]')||{innerText:''}).innerText") or '').replace('\n',' ')
    chk('9 Mapa: "Decisões pendentes 0", cabeçalho só com as impedidas e T4 "OS-0420 impedida"', 'Decisões pendentes 0' in nm and 'decis' not in head() and lb=='T4: OS-0420 impedida', [nm,head(),lb])
    # 10-11 · devolução de sobras vai ao Estoque do menu (nunca ao módulo oculto SU-07)
    ir('IN-01.dc.html'); a1=J("[...document.querySelectorAll('a')].filter(a=>a.innerText.trim()==='Receber devolução').map(a=>a.getAttribute('href'))")
    chk('10 Meu dia: "Receber devolução" → EST.dc.html', a1==['EST.dc.html'] and J("document.querySelectorAll('a[href=\"SU-07.dc.html\"]').length")==0, a1)
    ir('IN-03.dc.html'); a3=J("(()=>{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>/REQ-031/.test(r.innerText)); const a=r&&r.querySelector('a'); return a?[a.innerText.trim(),a.getAttribute('href')]:null;})()")
    chk('11 Agenda: REQ-031 "Receber devolução" → EST.dc.html', a3==['Receber devolução','EST.dc.html'] and J("document.querySelectorAll('a[href=\"SU-07.dc.html\"]').length")==0, a3)
finally:
    try:
        if c: c.close()
    finally: srv.terminate()
print(f'\n{len(OK)} ok · {len(FAIL)} falhas', FAIL)
