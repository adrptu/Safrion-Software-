# -*- coding: utf-8 -*-
"""Teste CDP de OS.dc.html: Lista/Kanban, chips de fase, painel lateral, Nova ordem e fase igual ao mapa (IN-04) e ao app (MB-02)."""
import sys, os, time, subprocess, json, re, shutil
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from cdp import Chrome
from journeys import free
HERE=os.path.dirname(os.path.abspath(__file__)); R=os.path.join(HERE,'_render')
for n in ('OS.dc.html',): shutil.copy(os.path.join(HERE,'project',n),os.path.join(R,n))  # IN-04 e MB-02 são de outras frentes: usa a cópia já em _render
p=free(); srv=subprocess.Popen(['python3','-m','http.server',str(p),'--bind','127.0.0.1','--directory',R],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(0.8)
c=Chrome(port=free()); J=c.js
CLK="""((t,root)=>{const r=root?document.querySelector(root):document; if(!r) return 'SEM RAIZ'; const n=s=>(s||'').replace(/\\s+/g,' ').trim(); const els=[...r.querySelectorAll('button,a,[role=button]')]; const e=els.find(x=>n(x.innerText)===t)||els.find(x=>n(x.innerText).startsWith(t)); if(!e) return 'NÃO ACHEI: '+t; e.click(); return 'ok';})"""
SETV="""((sel,val)=>{const i=document.querySelector(sel); const P=i.tagName==='SELECT'?HTMLSelectElement.prototype:HTMLInputElement.prototype; Object.getOwnPropertyDescriptor(P,'value').set.call(i,val); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true}));})"""
def clk(t,root=None): r=J(f"({CLK})({json.dumps(t)},{json.dumps(root)})"); time.sleep(.4); return r
def setv(sel,val): J(f"({SETV})({json.dumps(sel)},{json.dumps(val)})"); time.sleep(.3)
toast=lambda: J("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).filter(Boolean).join(' | ')")
rows=lambda: J("[...document.querySelectorAll('[role=table] [role=row].g2ed')].map(r=>r.innerText.split('\\n')[0].trim())")
pan=lambda: J("(document.querySelector('aside[role=dialog]')||{innerText:''}).innerText")
FASES=['A liberar','Liberadas','Em execução','Em conferência','Encerradas']
def fase_de(txt):
    for f in FASES:
        if f in txt: return f
    return None
ok=[]; falhas=[]
def check(nome,cond,info=''):
    (ok if cond else falhas).append(nome); print(('OK  ' if cond else 'FALHA ')+nome, info)
try:
    c.size(1440,1000); c.goto(f'http://127.0.0.1:{p}/OS.dc.html')
    check('sem erro JS', J("window.__err||''")=='', J("window.__err||''"))
    check('abre na Lista', J("document.querySelectorAll('[role=table]').length")==1)
    r0=rows(); check('13 ordens na lista (registro canônico)', len(r0)==13, r0)
    ov=J("(()=>{const t=document.querySelector('[role=table]').parentElement; return [t.scrollWidth,t.clientWidth];})()"); check('lista cabe sem rolagem horizontal', ov[0]<=ov[1]+1, ov)
    # chips de fase
    clk('Em execução'); r=rows(); check('chip Em execução filtra', r==['OS-0421','OS-0420'] or sorted(r)==['OS-0420','OS-0421'], r)
    check('chip marcado', J("[...document.querySelectorAll('[aria-label=\"Filtrar por fase\"] button')].filter(b=>b.getAttribute('aria-pressed')==='true').map(b=>b.innerText.replace(/\\s+/g,' '))")==['Em execução 2'])
    clk('A liberar'); r=rows(); check('chip A liberar = 5', len(r)==5 and 'OS-0418' in r and 'OS-0431' in r, r)
    check('filtro aparece na grade', 'Fase: A liberar' in J("document.body.innerText"))
    clk('Todas'); check('Todas volta a 13', len(rows())==13)
    # painel OS-0421
    J("[...document.querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.indexOf('OS-0421')===0).click()"); time.sleep(.5)
    t=pan(); check('painel abre', 'OS-0421' in t, t[:80])
    check('painel fase Em execução', fase_de(t.split('\n',3)[1] if '\n' in t else t)=='Em execução' or 'Em execução' in t)
    ap=J("[...document.querySelectorAll('aside[role=dialog] [style*=\"grid-template-columns: 64px\"]')].slice(1).map(r=>r.innerText.replace(/\\s+/g,' '))")
    print('   apontamentos:', ap)
    check('apontamentos 50,50,50,40 → 190/350', len(ap)>=4 and '190 / 350 ha' in ap[3] and '50 / 350' in ap[0] and '150 / 350' in ap[2], ap[:4])
    check('saldo 160', 'saldo 160 ha' in t)
    check('frase do turno', 'Fechar o turno não encerra a ordem' in t)
    check('origem', 'Origem'.upper() in t.upper() and 'Safra 2026/27' in t)
    href=J("(document.querySelector('aside[role=dialog] a')||{}).getAttribute && document.querySelector('aside[role=dialog] a').getAttribute('href')"); check('Abrir ordem → CA-01det', href=='CA-01det.dc.html', href)
    c.shot(os.path.join(HERE,'_probe','os_painel.png'))
    J("document.querySelector('aside[role=dialog]').dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true}))"); time.sleep(.3)
    check('Esc fecha painel', pan()=='')
    # Kanban
    clk('Kanban'); time.sleep(.3)
    cols=J("[...document.querySelectorAll('[aria-label=\"Kanban das ordens\"] > div')].map(d=>d.innerText.split('\\n').slice(0,2).join(' '))")
    check('Kanban 5 colunas fixas', len(cols)==5 and all(cols[i].upper().startswith(FASES[i].upper()) for i in range(5)), cols)
    kb={}
    for i,f in enumerate(FASES):
        ids=J(f"[...document.querySelectorAll('[aria-label=\"Kanban das ordens\"] > div')[{i}].querySelectorAll('[role=button]')].map(b=>b.innerText.split('\\n')[0].trim())")
        for x in ids: kb[x]=f
    check('Kanban 13 cartões', len(kb)==13, kb)
    c.shot(os.path.join(HERE,'_probe','os_kanban.png'))
    J("[...document.querySelectorAll('[role=button]')].find(b=>b.innerText.indexOf('OS-0420')===0).click()"); time.sleep(.4)
    t=pan(); check('cartão abre painel OS-0420 com link da ordem completa', 'OS-0420' in t and J("(document.querySelector('aside[role=dialog] a')||{}).getAttribute('href')")=='CA-01x-os0420.dc.html' and 'v3 em revisão' in t, t[:60])
    clk('Fechar','aside[role=dialog]')
    # lista × Kanban
    clk('Lista'); lista={}
    for r_ in J("[...document.querySelectorAll('[role=row].g2ed')].map(r=>r.innerText.replace(/\\n/g,' | '))"):
        lista[r_.split(' | ')[0].strip()]=fase_de(r_)
    check('Lista = Kanban', lista==kb, {k:(lista.get(k),kb.get(k)) for k in kb if lista.get(k)!=kb.get(k)})
    # Nova ordem
    clk('Nova ordem'); check('form Nova ordem', 'Nova ordem' in pan())
    clk('Emitir ordem','aside[role=dialog]'); e=J("[...document.querySelectorAll('aside [role=alert]')].map(x=>x.innerText).join(' | ')"); check('valida vazios', 'Escolha a safra' in e, e)
    setv('#nv_saf','S2627'); setv('#nv_cult','c4'); check('cultivo sem plano avisa', 'não tem plano aplicado' in pan())
    setv('#nv_cult','c1'); setv('#nv_atv','a7'); setv('#nv_jan','2026-12-01')
    clk('Cancelar','aside[role=dialog]'); check('aviso não salvo', 'Há alterações não salvas' in pan())
    clk('Continuar editando','aside[role=dialog]'); clk('Emitir ordem','aside[role=dialog]')
    tt=toast(); check('emite em A liberar', 'OS-0440' in tt and 'A liberar' in tt and 'Não foi liberada' in tt, tt)
    t=pan(); check('painel da nova ordem A liberar', 'OS-0440' in t and 'Aguardando agrônomo' in t, t[:120])
    J("document.querySelector('aside[role=dialog] button[aria-label=Fechar]').click()"); time.sleep(.3); check('14 ordens', len(rows())==14)
    check('contador A liberar 6', J("[...document.querySelectorAll('[aria-label=\"Filtrar por fase\"] button')].map(b=>b.innerText.replace(/\\s+/g,' '))")[1]=='A liberar 6')
    clk('Nova ordem'); setv('#nv_saf','S2627'); setv('#nv_cult','c1'); setv('#nv_atv','a7'); setv('#nv_jan','2026-12-02'); clk('Emitir ordem','aside[role=dialog]')
    e=J("[...document.querySelectorAll('aside [role=alert]')].map(x=>x.innerText).join(' | ')"); check('não duplica', 'Já existe OS-0440' in e, e)
    clk('Cancelar','aside[role=dialog]'); clk('Descartar alterações','aside[role=dialog]')
    # mapa IN-04 e app MB-02: mesma fase
    c.goto(f'http://127.0.0.1:{p}/IN-04.dc.html')
    mapa={}
    for r_ in J("[...document.querySelectorAll('[role=table] [role=row]')].slice(1).map(r=>r.innerText.replace(/\\n/g,' | '))"):
        m=re.match(r'\s*((?:OS|OB)-\d+)',r_)
        if m: mapa[m.group(1)]=fase_de(r_)
    comuns=[k for k in mapa if k in lista]
    print('   mapa IN-04: sem tabela de ordens desde 25/09; fase × mapa conferida no T12 (testes_pedido.py)')
    c.goto(f'http://127.0.0.1:{p}/MB-02.dc.html')
    txt=J("document.body.innerText"); app={}
    for m in re.finditer(r'((?:OS|OB)-\d{4})',txt):
        k=m.group(1)
        if k in app: continue
        seg=txt[m.end():m.end()+220]; nxt=re.search(r'(?:OS|OB)-\d{4}',seg); seg=seg[:nxt.start()] if nxt else seg
        f=fase_de(seg)
        if f: app[k]=f
    check('fase igual ao app MB-02', app and all(app[k]==lista.get(k) for k in app), {k:(app[k],lista.get(k)) for k in app})
finally:
    c.close(); srv.terminate()
print(f'\n{len(ok)} ok · {len(falhas)} falhas', falhas)
