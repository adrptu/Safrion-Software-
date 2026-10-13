# -*- coding: utf-8 -*-
"""Teste real (Chrome) — O.S. sem ordens de água (decisão do proprietário de 01/10/2026) e filtros do topo (Fazenda e Safra).
A irrigação só com água (OS-0419/0422/0423) deixou de ser O.S. agrícola: não aparece na OS.dc.html em nenhuma combinação de Fazenda
e Safra (lista, Kanban, chips de fase, contadores e selo do cabeçalho) e vive no módulo Irrigação (IR-02 programação, IR-03 Ordens de
irrigação, IR-03det = OS-0419). A fertirrigação OS-0418 continua na O.S., liberada pela agrônoma (produto + requisição).
Os filtros do topo seguem cobertos com as ordens que restam (lista, Kanban, chips, selo e estado vazio de uma frase + uma ação).
Uso: python3 os_irrig_filtro_test.py [pasta _render]   (15 verificações; < 60 s)"""
import sys, os, time, subprocess, json, re
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from cdp import Chrome
from journeys import free
HERE=os.path.dirname(os.path.abspath(__file__)); R=sys.argv[1] if len(sys.argv)>1 else os.path.join(HERE,'_render')
p=free(); srv=subprocess.Popen(['python3','-m','http.server',str(p),'--bind','127.0.0.1','--directory',R],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(.8)
c=Chrome(port=free()); J=c.js; OK=[]; FAIL=[]
def chk(n,cond,info=''): (OK if cond else FAIL).append(n); print(('  ok  ' if cond else '  FALHOU ')+n+(' · '+str(info)[:260] if info!='' else ''))
# 01/10: o painel recolhe o que não faz a ordem andar na fase; o teste abre tudo antes de ler
def pan():
    if J('(()=>{const bs=[...document.querySelectorAll(\'aside[role=dialog] section[aria-label] > button[aria-expanded="false"]\')]; bs.forEach(b=>b.click()); return bs.length;})()'): time.sleep(.3)
    return J("(()=>{const a=document.querySelector('aside[role=dialog]'); return a?a.innerText.replace(/\\s+/g,' '):'';})()") or ''
def temb(t): return bool(J(f"[...document.querySelectorAll('aside[role=dialog] button')].some(b=>b.innerText.trim()==={json.dumps(t)})"))
def ids(): return J("[...document.querySelectorAll('[role=row].g2ed')].map(r=>r.innerText.split('\\n')[0].trim())") or []
def linha(id_): return J(f"(()=>{{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.trim().startsWith({json.dumps(id_)})); return r?r.innerText.replace(/\\s+/g,' '):'';}})()") or ''
def cor(id_,t): return J(f"(()=>{{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.trim().startsWith({json.dumps(id_)})); const s=r&&[...r.querySelectorAll('span')].filter(x=>x.innerText.trim().startsWith({json.dumps(t)})).pop(); return s?getComputedStyle(s).color:'';}})()") or ''
def rlink(id_,t): return J(f"(()=>{{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.trim().startsWith({json.dumps(id_)})); const a=r&&[...r.querySelectorAll('a')].find(a=>a.innerText.trim().startsWith({json.dumps(t)})); return a?a.getAttribute('href'):'';}})()") or ''
def fechar(): J("(()=>{const b=document.querySelector('aside[role=dialog] button[aria-label=Fechar]'); b&&b.click();})()"); time.sleep(.3)
def filtro(lab,val,w=.4):
    J(f"""(()=>{{const i=document.querySelector('select[aria-label={json.dumps(lab)}]'); Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype,'value').set.call(i,{json.dumps(val)});
      i.dispatchEvent(new Event('input',{{bubbles:true}})); i.dispatchEvent(new Event('change',{{bubbles:true}}));}})()"""); time.sleep(w)
def sel(lab): return J(f"document.querySelector('select[aria-label={json.dumps(lab)}]').value") or ''
def opcoes(lab): return J(f"[...document.querySelector('select[aria-label={json.dumps(lab)}]').options].map(o=>o.value)") or []
def chips(): return J("[...document.querySelectorAll('[aria-label=\"Filtrar por fase\"] button')].map(b=>b.innerText.replace(/\\s+/g,' ').trim())") or []
def hdr(): return J("(()=>{const h=document.querySelector('header h1'); const s=h&&h.nextElementSibling; return s?s.innerText.trim():'';})()") or ''
def vazio(): return J("(()=>{const d=document.querySelector('[aria-label=\"Sem ordens no filtro\"]'); return d?d.innerText.replace(/\\s+/g,' ').trim():'';})()") or ''
def clica(t): J(f"(()=>{{const b=[...document.querySelectorAll('button')].find(b=>b.innerText.trim()==={json.dumps(t)}); b&&b.click();}})()"); time.sleep(.4)
def esperar(pag):   # navegação por clique em link: espera a página nova carregar
    for _ in range(40):
        time.sleep(.25)
        if pag in (J("location.href") or '') and J("document.readyState")=='complete' and J("!!document.body && document.body.innerText.length>50"): break
    time.sleep(.8)
# estado da tela num filtro: linhas, cartões do Kanban, chips, cabeçalho e ids de água no texto visível
EST=r"""(()=>{const ids=[...document.querySelectorAll('[role=row].g2ed')].map(r=>r.innerText.split('\n')[0].trim());
  const kb=[...document.querySelectorAll('[aria-label="Kanban das ordens"] [role=button]')].map(b=>b.innerText.split('\n')[0].trim());
  const ch=[...document.querySelectorAll('[aria-label="Filtrar por fase"] button')].map(b=>b.innerText.replace(/\s+/g,' ').trim());
  const h=document.querySelector('header h1'); const s=h&&h.nextElementSibling;
  return {ids,kb,ch,hd:s?s.innerText.trim():'',agua:(document.body.innerText.match(/OS-04(19|22|23)/g)||[])};})()"""
AGUA=('OS-0419','OS-0422','OS-0423')
PROIB=re.compile(r'política de água|PA-07|exceção|revisão individual',re.I)
REV=re.compile(r'Revisar versão|Aguardando agrônomo|Aprovada pelo agrônomo|APV-')  # O.S. sem revisão (01/10): só na OS.dc.html (verificação 6)
AMAR,VERM='rgb(138, 90, 0)','rgb(180, 35, 24)'
def num(ch,rot):   # 'Em execução 2' -> 2 (None se o chip não existe)
    m=[x for x in ch if x.startswith(rot+' ')]; return int(m[0].split()[-1]) if m else None
try:
    c.size(1440,1000)
    # link antigo de ordem de água: abre a lista padrão, sem painel e sem a ordem
    c.goto(f'http://127.0.0.1:{p}/OS.dc.html#OS-0419',wait=1.3)
    ids0=ids(); n0=len(ids0); ch0=chips()
    chk('1 sem erro JS · OS.dc.html#OS-0419 abre a lista padrão Santa Rita/Todas sem painel: 10 ordens agrícolas, chip Todas igual às linhas, nenhuma de água',
        (J("window.__err||''") or '')=='' and not J("!!document.querySelector('aside[role=dialog]')") and sel('Filtrar por fazenda')=='Santa Rita' and sel('Filtrar por safra')=='Todas'
        and n0==10 and num(ch0,'Todas')==n0 and not set(AGUA)&set(ids0) and not J(EST)['agua'] and hdr()=='2 em execução · 3 impedidas', (ids0,ch0,hdr()))
    # ---------- água fora da O.S. em todas as combinações de Fazenda e Safra ----------
    FAZ=opcoes('Filtrar por fazenda'); SAF=opcoes('Filtrar por safra'); NS={}; ruim=[]
    for f in FAZ:
        for s in SAF:
            filtro('Filtrar por fazenda',f,.25); filtro('Filtrar por safra',s,.25); e=J(EST); NS[(f,s)]=len(e['ids'])
            if set(AGUA)&set(e['ids']) or e['agua']: ruim.append((f,s,'água',e['agua']))
            if e['ids'] and num(e['ch'],'Todas')!=len(e['ids']): ruim.append((f,s,'chip Todas',e['ch'][:1],len(e['ids'])))
            if e['ids'] and not e['hd'].startswith(f"{num(e['ch'],'Em execução')} em execução"): ruim.append((f,s,'cabeçalho',e['hd'],e['ch']))
    chk(f'2 lista, chips e cabeçalho sem OS-0419/0422/0423 nas {len(FAZ)}×{len(SAF)} combinações de Fazenda e Safra; chip Todas = linhas; em execução do selo = chip',
        len(FAZ)>=4 and len(SAF)>=4 and not ruim and NS[('Santa Rita','Todas')]==n0, (ruim[:4],FAZ,SAF))
    filtro('Filtrar por fazenda','Santa Rita'); filtro('Filtrar por safra','Todas'); clica('Kanban'); ruim=[]
    for f in FAZ:
        for s in SAF:
            filtro('Filtrar por fazenda',f,.25); filtro('Filtrar por safra',s,.25); e=J(EST)
            if set(AGUA)&set(e['kb']) or e['agua']: ruim.append((f,s,'água',e['kb']))
            if len(e['kb'])!=NS[(f,s)]: ruim.append((f,s,'cartões',len(e['kb']),NS[(f,s)]))
    filtro('Filtrar por fazenda','Santa Rita'); filtro('Filtrar por safra','Todas'); kb_sr=J(EST)['kb']; clica('Lista')
    chk('3 Kanban sem ordens de água em todas as combinações; cartões = linhas da lista em cada uma (Santa Rita/Todas: as mesmas 10)',
        not ruim and sorted(kb_sr)==sorted(ids0), (ruim[:4],kb_sr))
    # ---------- fertirrigação OS-0418 continua na O.S. ----------
    l=linha('OS-0418')
    chk('4 OS-0418 na lista da O.S.: Fertirrigação · reclassificada, A liberar, selo vermelho Falta insumo · Ureia 45%', 'Fertirrigação · reclassificada' in l and 'A liberar' in l
        and cor('OS-0418','Falta insumo')==VERM, (l,cor('OS-0418','Falta insumo')))
    c.goto(f'http://127.0.0.1:{p}/IR-03.dc.html',wait=1.0)
    # 02/10: a linha abre o registro (sem coluna de link); a fertirrigação abre na O.S.
    J("(()=>{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.trim().startsWith('OS-0418')); r&&r.click();})()"); esperar('OS.dc.html')
    t=pan(); txt=t
    chk('5 IR-03: a linha da OS-0418 (Liberar na O.S.) abre a OS-0418 na O.S.: Ana (agrônoma) libera, requisição ao liberar; sem lote de Ureia, liberar fica bloqueado',
        (J("location.href") or '').endswith('OS.dc.html#OS-0418') and t.startswith('OS-0418') and 'Ana (agrônoma)' in t and 'REQ-' in t and not temb('Revisar versão')
        and 'Aguardando agrônomo' not in t and 'Liberar bloqueado: sem lote de Ureia 45%' in t, (J("location.href"),t[:300]))
    fechar(); txt+=J("document.body.innerText")+J("[...document.scripts].map(s=>s.textContent).join(' ')")
    m=PROIB.findall(txt)+REV.findall(txt); chk('6 tela e dados da O.S. sem política de água, PA-07, exceção, revisão individual nem revisão/aprovação de versão', not m, m[:5])
    # ---------- filtros do topo ----------
    filtro('Filtrar por safra','2025/26')
    chk('7 Safra 2025/26: lista, chips e cabeçalho só com OS-0415 e OB-0104', sorted(ids())==['OB-0104','OS-0415'] and chips()[0]=='Todas 2' and 'Encerradas 2' in chips() and 'A liberar 0' in chips() and hdr()=='0 em execução · nenhuma impedida', (ids(),chips(),hdr()))
    clica('Kanban'); kb=J("[...document.querySelectorAll('[aria-label=\"Kanban das ordens\"] > div')].map(d=>d.querySelectorAll('[role=button]').length)")
    chk('8 Kanban 2025/26: 2 cartões, ambos em Encerradas', kb==[0,0,0,0,2], kb)
    clica('Lista'); filtro('Filtrar por safra','Safrinha 2027')
    chk('9 Safrinha 2027 sem ordens: uma frase e uma ação, sem lista nem abas', vazio()=='Nenhuma ordem na safra Safrinha 2027 Ver todas as safras' and J("document.querySelectorAll('[role=table]').length")==0 and not J("!!document.querySelector('[aria-label=\"Visão das ordens\"]')"), vazio())
    clica('Ver todas as safras')
    chk(f'10 Ver todas as safras volta às {n0} ordens e o seletor mostra Todas', len(ids())==n0 and sel('Filtrar por safra')=='Todas' and vazio()=='', (len(ids()),sel('Filtrar por safra')))
    filtro('Filtrar por fazenda','Boa Vista')
    chk('11 Boa Vista: Nenhuma ordem na Boa Vista · Ver Santa Rita; cabeçalho zerado', vazio()=='Nenhuma ordem na Boa Vista Ver Santa Rita' and hdr()=='0 em execução · nenhuma impedida', (vazio(),hdr()))
    clica('Ver Santa Rita'); n_sr=len(ids()); s_sr=sel('Filtrar por fazenda'); h_sr=hdr()
    filtro('Filtrar por fazenda','Lagoa Grande'); lg=ids()
    filtro('Filtrar por fazenda','Todas'); todas=ids()
    # 01/10: Todas = Santa Rita (sem água) + as 11 ordens da Fazenda Lagoa Grande (OS-0501 a OS-0511)
    chk(f'12 Ver Santa Rita volta às {n0} (2 em execução · 3 impedidas); Lagoa Grande tem 11 (OS-05xx); Fazenda Todas = Santa Rita + Lagoa Grande',
        n_sr==n0 and s_sr=='Santa Rita' and h_sr=='2 em execução · 3 impedidas' and len(lg)==11 and all(x.startswith('OS-05') for x in lg) and sorted(todas)==sorted(ids0+lg),
        (n_sr,s_sr,h_sr,len(lg),len(todas)))
    c.shot(os.path.join(HERE,'_probe','os_irrig_filtro.png'))
    # ---------- as ordens de água vivem na Irrigação ----------
    c.goto(f'http://127.0.0.1:{p}/IR-02.dc.html',wait=1.0)
    ir2=ids(); a2=[linha(x) for x in AGUA]; c2=(cor('OS-0422','Janela a definir'),cor('OS-0423','Conflito'))
    c.goto(f'http://127.0.0.1:{p}/IR-03.dc.html',wait=1.0)
    ir3=ids(); a3=[linha(x) for x in AGUA]; c3=(cor('OS-0422','Janela a definir'),cor('OS-0423','Conflito'))
    nx3=[x for x in (('OS-0419','Iniciar irrigação'),('OS-0422','Definir janela'),('OS-0423','Resolver conflito'),('OS-0418','Receber o insumo no Estoque')) if x[1] in linha(x[0])]
    chk('13 IR-02 e IR-03 listam OS-0419/0422/0423 como água; OS-0422 amarela (Janela a definir, 2 passadas de 6,75 mm), OS-0423 vermelha (Conflito · parada da B3, estimativa por ET); próximo passo na linha: Iniciar irrigação, Definir janela, Resolver conflito e, para a OS-0418, o mesmo passo da O.S. (Receber o insumo no Estoque)',
        set(AGUA)<=set(ir2) and set(AGUA)<=set(ir3) and all('gua' in x for x in a2+a3) and c2==(AMAR,VERM) and c3==(AMAR,VERM)
        and '2 passadas de 6,75 mm' in a3[1] and 'estimativa por et' in a3[2].lower() and len(nx3)==4 and (J("window.__err||''") or '')=='',
        (ir2,ir3,c2,c3,nx3))
    J("(()=>{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.trim().startsWith('OS-0419')); r&&r.click();})()"); esperar('IR-03det.dc.html')
    b=J("document.body.innerText") or ''
    chk('14 IR-03det (linha da OS-0419 → IR-03det#OS-0419): OS-0419 · Irrigação · Pivô 2, Liberadas, 10,81 mm do balanço de 23/09, Iniciar irrigação; sem agrônomo nem política',
        (J("location.href") or '').endswith('IR-03det.dc.html#OS-0419') and J("document.querySelector('h1').innerText.trim()")=='OS-0419 · Irrigação · Pivô 2' and 'Liberadas' in b and '10,81 mm brutos em 1 passada' in b
        and 'balanço de 23/09' in b and J("[...document.querySelectorAll('button')].some(x=>x.innerText.trim()==='Iniciar irrigação')") and 'agrônom' not in b and 'olítica' not in b and not PROIB.search(b)
        and (J("window.__err||''") or '')=='', (J("location.href"),b[b.find('OS-0419'):][:200]))
    # ---------- CA-01 (Ordens de campo, módulo oculto preservado) ----------
    c.goto(f'http://127.0.0.1:{p}/CA-01.dc.html',wait=1.0)
    hr=J("""(()=>{const f=(id,t)=>{ const r=[...document.querySelectorAll('[role=row]')].find(r=>r.innerText.trim().startsWith(id)); const a=r&&[...r.querySelectorAll('a')].find(a=>a.innerText.trim().startsWith(t)); return a?a.getAttribute('href'):''; };
      return [f('OS-0422','Definir janela'),f('OS-0423','Resolver conflito')];})()""")
    b=J("document.body.innerText"); l2=J("(()=>{const r=[...document.querySelectorAll('[role=row]')].find(r=>r.innerText.trim().startsWith('OS-0422')); return r?r.innerText.replace(/\\s+/g,' '):'';})()") or ''
    l3=J("(()=>{const r=[...document.querySelectorAll('[role=row]')].find(r=>r.innerText.trim().startsWith('OS-0423')); return r?r.innerText.replace(/\\s+/g,' '):'';})()") or ''
    chk('15 CA-01: Definir janela (João, irrigante) e Resolver conflito (Caio, PCP) levam à IR-02; sem política nem fora da política', hr==['IR-02.dc.html','IR-02.dc.html'] and 'João (irrigante)' in l2 and 'Caio (PCP)' in l3
        and 'olítica' not in b and not PROIB.search(b) and (J("window.__err||''") or '')=='', (hr,PROIB.findall(b)[:3]))
finally:
    c.close(); srv.terminate()
print(f'\nRESULTADO: {len(OK)} ok · {len(FAIL)} falhas'); [print('  -',f) for f in FAIL]
