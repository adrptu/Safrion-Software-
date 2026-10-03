# -*- coding: utf-8 -*-
"""Teste CDP (≤ 15 verificações) das Aprovações IN-02 sem O.S. (a O.S. é liberada pelo agrônomo na tela O.S., com ajuste opcional),
da OS-0418 que abre A liberar impedida pelo Estoque, do Mapa sem decisões pendentes e dos atalhos de devolução do Meu dia e da Agenda,
que levam ao Estoque do menu. Uso: python3 map_aprov_test.py (≈ 20 s)."""
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
    ir('IN-02.dc.html'); J("localStorage.removeItem('talhao-os-cenario-v1')"); J("sessionStorage.setItem('mapa-ctx','{\"mf_faz\":\"Santa Rita\"}')"); ir('IN-02.dc.html',900)  # o Mapa deste teste é o da Santa Rita (01/10: abre na Lagoa Grande)
    rs=rows()
    chk('1 Aprovações sem O.S.: 4 decisões (inventário, Diesel, orçamento e acesso) · 4 pendentes · 1 vence hoje',
        len(rs)==4 and not any(r.startswith('OS-0') for r in rs) and '4 pendentes · 1 vence hoje' in head() and J("document.documentElement.scrollHeight")<=HOV.get('IN-02.dc.html',900), [rs,head(),J("document.documentElement.scrollHeight")])
    # 2 · a O.S. não passa por revisão: a OS-0418 abre A liberar, já impedida pelo Estoque (Ureia 45 % sem lote), sem selo nem recibo do agrônomo
    ir('OS.dc.html'); J("(()=>{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.trim().startsWith('OS-0418')); r&&r.click();})()"); time.sleep(.4)
    po=J("(()=>{const a=document.querySelector('aside[role=dialog]'); return a?a.innerText.replace(/\\s+/g,' '):'';})()") or ''
    chk('2 O.S.: OS-0418 A liberar com "Liberar bloqueado: sem lote de Ureia 45%", sem "Aguardando agrônomo", "Aprovada pelo agrônomo", AP-2201 nem "Revisar versão"',
        'Liberar bloqueado: sem lote de Ureia 45%' in po and not any(x in po for x in ('Aguardando agrônomo','Aprovada pelo agrônomo','AP-2201','Revisar versão')), po[:400])
    # 3 · Mapa na abertura: nenhuma decisão pendente; OS-0418 e OS-0430 a liberar pelo agrônomo; o T4 só com a máquina
    ir('IN-04.dc.html',900); lb=J("(()=>{const e=[...document.querySelectorAll('svg [role=button]')].find(x=>(x.getAttribute('aria-label')||'').startsWith('T4:')); return e?e.getAttribute('aria-label'):'';})()")
    nm=(J("(document.querySelector('[role=group][aria-label^=\"Indicadores de\"]')||{innerText:''}).innerText") or '').replace('\n',' ')
    chk('3 Mapa: sem "Decisões pendentes", "A liberar (agrônomo) 2", cabeçalho sem "decis" e T4 "OS-0420 impedida"', 'Decisões pendentes' not in nm and 'A liberar (agrônomo) 2' in nm and 'decis' not in head() and lb=='T4: OS-0420 impedida', [nm,head(),lb])
    # 4-5 · devolução de sobras vai ao Estoque do menu (nunca ao módulo oculto SU-07)
    ir('IN-01.dc.html'); a1=J("[...document.querySelectorAll('a')].filter(a=>a.innerText.trim()==='Receber devolução').map(a=>a.getAttribute('href'))")
    chk('4 Meu dia: "Receber devolução" → EST.dc.html', a1==['EST.dc.html'] and J("document.querySelectorAll('a[href=\"SU-07.dc.html\"]').length")==0, a1)
    ir('IN-03.dc.html'); a3=J("(()=>{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>/REQ-031/.test(r.innerText)); const a=r&&r.querySelector('a'); return a?[a.innerText.trim(),a.getAttribute('href')]:null;})()")
    chk('5 Agenda: REQ-031 "Receber devolução" → EST.dc.html', a3==['Receber devolução','EST.dc.html'] and J("document.querySelectorAll('a[href=\"SU-07.dc.html\"]').length")==0, a3)
finally:
    try:
        if c: c.close()
    finally: srv.terminate()
print(f'\n{len(OK)} ok · {len(FAIL)} falhas', FAIL)
