# -*- coding: utf-8 -*-
"""Teste CDP de OS.dc.html: Lista/Kanban, chips de fase, painel lateral, Nova ordem e fase igual ao app (MB-02).
01/10/2026 (decisão do proprietário): ordens só de água (OS-0419, OS-0422, OS-0423) saem da página O.S. e vivem na Irrigação;
a lista, o Kanban, os chips e os contadores contam só as ordens agrícolas (10 em Santa Rita · 2026/27, lidas na própria página);
a fertirrigação OS-0418 continua na O.S. O app de campo (MB-02) ainda mostra a água ao irrigante: a fase app × O.S. é comparada
só nas ordens que estão na página O.S."""
import sys, os, time, subprocess, json, re, shutil
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from cdp import Chrome
from journeys import free
from comp_lib import troca_visao   # VISOES-1: troca de visão pelo seletor (data-visao), não pelo texto
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
def pan():   # 01/10: abre as seções recolhidas do painel antes de ler
    if J('(()=>{const bs=[...document.querySelectorAll(\'aside[role=dialog] section[aria-label] > button[aria-expanded="false"]\')]; bs.forEach(b=>b.click()); return bs.length;})()'): time.sleep(.3)
    return J("(document.querySelector('aside[role=dialog]')||{innerText:''}).innerText")
FASES=['A liberar','Liberadas','Em execução','Em conferência','Encerradas']
AGUA=['OS-0419','OS-0422','OS-0423']   # 01/10: ordens só de água, fora da página O.S.
chips=lambda: J("[...document.querySelectorAll('[aria-label=\"Filtrar por fase\"] button')].map(b=>b.innerText.replace(/\\s+/g,' ').trim())") or []
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
    r0=rows(); N=len(r0); cs0=chips()
    check('10 ordens agrícolas na lista (registro canônico, igual ao chip Todas)', N==10 and cs0[:1]==[f'Todas {N}'] and len(set(r0))==N, (r0,cs0[:1]))
    corpo=J("document.body.innerText")
    check('ordens só de água fora da página O.S. (lista e texto)', not any(x in r0 or x in corpo for x in AGUA), [x for x in AGUA if x in corpo])
    # TABELAS-FOCO (5983172395 item 6): uma variável por coluna; a rolagem horizontal fica dentro da caixa da tabela e não esconde o filtro Talhão
    ov=J("(()=>{const b=document.getElementById('ost_btn').getBoundingClientRect(); return [document.documentElement.scrollWidth,innerWidth,b.left>=0&&b.right<=innerWidth&&b.width>0];})()"); check('página sem rolagem horizontal e filtro Talhão visível (a tabela rola dentro da caixa)', ov[0]<=ov[1]+1 and ov[2], ov)
    # chips de fase
    clk('Em execução'); r=rows(); check('chip Em execução filtra', r==['OS-0421','OS-0420'] or sorted(r)==['OS-0420','OS-0421'], r)
    check('chip marcado', J("[...document.querySelectorAll('[aria-label=\"Filtrar por fase\"] button')].filter(b=>b.getAttribute('aria-pressed')==='true').map(b=>b.innerText.replace(/\\s+/g,' '))")==['Em execução 2'])
    clk('A liberar'); r=rows(); check('chip A liberar = 3 (fertirrigação OS-0418 fica; água OS-0422/OS-0423 não)', sorted(r)==['OS-0418','OS-0430','OS-0431'] and 'A liberar 3' in chips(), r)
    check('filtro aparece na grade', 'Fase: A liberar' in J("document.body.innerText"))
    clk('Todas'); check(f'Todas volta a {N}', rows()==r0)
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
    troca_visao(J,'kanban'); time.sleep(.3)
    cols=J("[...document.querySelectorAll('[aria-label=\"Kanban das ordens\"] > div')].map(d=>d.innerText.split('\\n').slice(0,2).join(' '))")
    check('Kanban 5 colunas fixas', len(cols)==5 and all(cols[i].upper().startswith(FASES[i].upper()) for i in range(5)), cols)
    kb={}
    for i,f in enumerate(FASES):
        ids=J(f"[...document.querySelectorAll('[aria-label=\"Kanban das ordens\"] > div')[{i}].querySelectorAll('[role=button]')].map(b=>b.innerText.split('\\n')[0].trim())")
        for x in ids: kb[x]=f
    check(f'Kanban {N} cartões, sem ordens de água', len(kb)==N and sorted(kb)==sorted(r0) and not any(x in kb for x in AGUA), kb)
    c.shot(os.path.join(HERE,'_probe','os_kanban.png'))
    J("[...document.querySelectorAll('[role=button]')].find(b=>b.innerText.indexOf('OS-0420')===0).click()"); time.sleep(.4)
    t=pan(); check('cartão abre painel OS-0420 com link da ordem completa', 'OS-0420' in t and J("(document.querySelector('aside[role=dialog] a')||{}).getAttribute('href')")=='CA-01x-os0420.dc.html' and 'v3 no saldo de 70 ha' in t and 'em revisão' not in t, t[:60])
    clk('Fechar','aside[role=dialog]')
    # lista × Kanban
    troca_visao(J,'lista'); lista={}
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
    t=pan(); check('painel da nova ordem A liberar: Liberar para execução e Ajustar antes de liberar, sem selo de agrônomo', 'OS-0440' in t and 'Liberar para execução' in t and 'Ajustar antes de liberar' in t and 'Aguardando agrônomo' not in t and 'Revisar versão' not in t, t[:120])
    J("document.querySelector('aside[role=dialog] button[aria-label=Fechar]').click()"); time.sleep(.3); check(f'{N+1} ordens', len(rows())==N+1)
    cs=chips(); check('contador A liberar 4 e Todas sobe junto', cs[1]=='A liberar 4' and cs[0]==f'Todas {N+1}', cs)
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
    comuns_app=[k for k in app if k in lista]   # 01/10: o app ainda mostra a água ao irrigante; compara só o que está na página O.S.
    check('fase igual ao app MB-02 (ordens da página O.S.)', len(comuns_app)>=3 and all(app[k]==lista[k] for k in comuns_app), {k:(app[k],lista.get(k)) for k in app})
    check('app MB-02 ainda mostra a água OS-0419 ao irrigante, fora da página O.S.', 'OS-0419' in app and 'OS-0419' not in lista and 'resp. João' in txt[txt.find('OS-0419'):][:200], txt[txt.find('OS-0419'):][:200])
finally:
    c.close(); srv.terminate()
print(f'\n{len(ok)} ok · {len(falhas)} falhas', falhas)
