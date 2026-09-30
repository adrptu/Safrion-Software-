# -*- coding: utf-8 -*-
"""Teste real (Chrome) — O.S. etapa 1 (26/09): irrigação só com água sem agrônomo (OS-0419/0422/0423; OS-0418 segue com o agrônomo)
e filtros do topo (Fazenda e Safra) na lista, no Kanban, nos chips de fase e no selo do cabeçalho, com estado vazio de uma frase + uma ação.
Uso: python3 os_irrig_filtro_test.py [pasta _render]   (15 verificações; < 60 s)"""
import sys, os, time, subprocess, json, re
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from cdp import Chrome
from journeys import free
HERE=os.path.dirname(os.path.abspath(__file__)); R=sys.argv[1] if len(sys.argv)>1 else os.path.join(HERE,'_render')
p=free(); srv=subprocess.Popen(['python3','-m','http.server',str(p),'--bind','127.0.0.1','--directory',R],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(.8)
c=Chrome(port=free()); J=c.js; OK=[]; FAIL=[]
def chk(n,cond,info=''): (OK if cond else FAIL).append(n); print(('  ok  ' if cond else '  FALHOU ')+n+(' · '+str(info)[:260] if info!='' else ''))
def pan(): return J("(()=>{const a=document.querySelector('aside[role=dialog]'); return a?a.innerText.replace(/\\s+/g,' '):'';})()") or ''
def temb(t): return bool(J(f"[...document.querySelectorAll('aside[role=dialog] button')].some(b=>b.innerText.trim()==={json.dumps(t)})"))
def link(t): return J(f"(()=>{{const a=[...document.querySelectorAll('aside[role=dialog] a')].find(a=>a.innerText.trim().startsWith({json.dumps(t)})); return a?a.getAttribute('href'):'';}})()") or ''
def ids(): return J("[...document.querySelectorAll('[role=row].g2ed')].map(r=>r.innerText.split('\\n')[0].trim())") or []
def linha(id_): return J(f"(()=>{{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.trim().startsWith({json.dumps(id_)})); return r?r.innerText.replace(/\\s+/g,' '):'';}})()") or ''
def cor(id_,t): return J(f"(()=>{{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.trim().startsWith({json.dumps(id_)})); const s=r&&[...r.querySelectorAll('span')].filter(x=>x.innerText.trim().startsWith({json.dumps(t)})).pop(); return s?getComputedStyle(s).color:'';}})()") or ''
def abrir(id_): J(f"(()=>{{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.trim().startsWith({json.dumps(id_)})); r.click();}})()"); time.sleep(.4)
def fechar(): J("(()=>{const b=document.querySelector('aside[role=dialog] button[aria-label=Fechar]'); b&&b.click();})()"); time.sleep(.3)
def passo_bg(): return J("(()=>{const r=document.querySelector('aside[role=dialog] [aria-label=\"Próximo passo\"]'); return r?getComputedStyle(r).backgroundColor:'';})()") or ''
def filtro(lab,val):
    J(f"""(()=>{{const i=document.querySelector('select[aria-label={json.dumps(lab)}]'); Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype,'value').set.call(i,{json.dumps(val)});
      i.dispatchEvent(new Event('input',{{bubbles:true}})); i.dispatchEvent(new Event('change',{{bubbles:true}}));}})()"""); time.sleep(.4)
def sel(lab): return J(f"document.querySelector('select[aria-label={json.dumps(lab)}]').value") or ''
def chips(): return J("[...document.querySelectorAll('[aria-label=\"Filtrar por fase\"] button')].map(b=>b.innerText.replace(/\\s+/g,' ').trim())") or []
def hdr(): return J("(()=>{const h=document.querySelector('header h1'); const s=h&&h.nextElementSibling; return s?s.innerText.trim():'';})()") or ''
def vazio(): return J("(()=>{const d=document.querySelector('[aria-label=\"Sem ordens no filtro\"]'); return d?d.innerText.replace(/\\s+/g,' ').trim():'';})()") or ''
def clica(t): J(f"(()=>{{const b=[...document.querySelectorAll('button')].find(b=>b.innerText.trim()==={json.dumps(t)}); b&&b.click();}})()"); time.sleep(.4)
PROIB=re.compile(r'política de água|PA-07|exceção|revisão individual',re.I)
AMAR,VERM='rgb(138, 90, 0)','rgb(180, 35, 24)'
try:
    c.size(1440,1000); c.goto(f'http://127.0.0.1:{p}/OS.dc.html',wait=1.3)
    chk('1 sem erro JS · padrão Santa Rita/Todas mostra as 13 ordens', (J("window.__err||''") or '')=='' and sel('Filtrar por fazenda')=='Santa Rita' and sel('Filtrar por safra')=='Todas' and len(ids())==13, ids())
    # ---------- irrigação só com água ----------
    l=linha('OS-0422')
    chk('2 OS-0422 na lista: água, 2 passadas de 6,75 mm, selo amarelo Janela a definir, dono João', 'Irrigação · água' in l and '13,5 mm em 2 passadas de 6,75 mm' in l and 'Janela a definir' in l and 'João (irrigante)' in l and cor('OS-0422','Janela a definir')==AMAR, (l,cor('OS-0422','Janela a definir')))
    l=linha('OS-0423')
    chk('3 OS-0423 na lista: selo vermelho Conflito · parada da B3, estimativa por ET, dono Caio (PCP)', 'Conflito · parada da B3' in l and 'estimativa por ET · sonda sem dado' in l and 'Caio (PCP)' in l and cor('OS-0423','Conflito')==VERM, (l,cor('OS-0423','Conflito')))
    txt=''
    abrir('OS-0422'); t=pan(); txt+=t
    chk('4 OS-0422: próximo passo Definir janela (João) → IR-02, sem agrônomo e sem liberar/revisar, caixa amarela', 'Definir janela' in t and 'Quem resolve: João (irrigante)' in t and link('Definir janela')=='IR-02.dc.html' and 'agrônom' not in t
        and not temb('Revisar versão') and not temb('Liberar para execução') and passo_bg()=='rgb(255, 243, 214)', (t[:420],passo_bg()))
    fechar(); abrir('OS-0423'); t=pan(); txt+=t
    chk('5 OS-0423: Resolver conflito (Caio, PCP) → IR-02; estimativa por ET não bloqueia; caixa vermelha', 'Resolver conflito' in t and 'Quem resolve: Caio (PCP)' in t and link('Resolver conflito')=='IR-02.dc.html'
        and 'Estimativa por ET · sonda sem dado (não bloqueia).' in t and 'agrônom' not in t and passo_bg()=='rgb(253, 232, 230)', (t[:420],passo_bg()))
    fechar(); abrir('OS-0419'); t=pan(); txt+=t
    # v39: cada fato uma vez no painel — a lâmina fica só em Insumos e a origem é o balanço hídrico
    chk('6 OS-0419 liberada: origem no balanço hídrico, lâmina 10,81 mm uma vez (Insumos), sem citar política', 'Balanço hídrico de 23/09 · Pivô 2 · Milho V10' in t and t.count('10,81 mm em 1 passada')==1 and 'olítica' not in t and temb('Iniciar execução'), t[-300:])
    fechar(); abrir('OS-0418'); t=pan()
    chk('7 OS-0418 (fertirrigação) segue com o agrônomo', 'Aguardando agrônomo' in t and temb('Revisar versão') and 'Ana (agrônoma)' in t, t[:300])
    fechar(); txt+=J("document.body.innerText")+J("[...document.scripts].map(s=>s.textContent).join(' ')")
    m=PROIB.findall(txt); chk('8 tela e dados da O.S. sem política de água, PA-07, exceção ou revisão individual', not m, m[:5])
    # ---------- filtros do topo ----------
    filtro('Filtrar por safra','2025/26')
    chk('9 Safra 2025/26: lista, chips e cabeçalho só com OS-0415 e OB-0104', sorted(ids())==['OB-0104','OS-0415'] and chips()[0]=='Todas 2' and 'Encerradas 2' in chips() and 'A liberar 0' in chips() and hdr()=='0 em execução · nenhuma impedida', (ids(),chips(),hdr()))
    clica('Kanban'); kb=J("[...document.querySelectorAll('[aria-label=\"Kanban das ordens\"] > div')].map(d=>d.querySelectorAll('[role=button]').length)")
    chk('10 Kanban 2025/26: 2 cartões, ambos em Encerradas', kb==[0,0,0,0,2], kb)
    clica('Lista'); filtro('Filtrar por safra','Safrinha 2027')
    chk('11 Safrinha 2027 sem ordens: uma frase e uma ação, sem lista nem abas', vazio()=='Nenhuma ordem na safra Safrinha 2027 Ver todas as safras' and J("document.querySelectorAll('[role=table]').length")==0 and not J("!!document.querySelector('[aria-label=\"Visão das ordens\"]')"), vazio())
    clica('Ver todas as safras')
    chk('12 Ver todas as safras volta às 13 ordens e o seletor mostra Todas', len(ids())==13 and sel('Filtrar por safra')=='Todas' and vazio()=='', (len(ids()),sel('Filtrar por safra')))
    filtro('Filtrar por fazenda','Boa Vista')
    chk('13 Boa Vista: Nenhuma ordem na Boa Vista · Ver Santa Rita; cabeçalho zerado', vazio()=='Nenhuma ordem na Boa Vista Ver Santa Rita' and hdr()=='0 em execução · nenhuma impedida', (vazio(),hdr()))
    clica('Ver Santa Rita'); n_sr=len(ids()); s_sr=sel('Filtrar por fazenda'); h_sr=hdr()
    filtro('Filtrar por fazenda','Todas')
    chk('14 Ver Santa Rita volta às 13 (2 em execução · 2 impedidas); Fazenda Todas mostra tudo', n_sr==13 and s_sr=='Santa Rita' and h_sr=='2 em execução · 2 impedidas' and len(ids())==13, (n_sr,s_sr,h_sr,len(ids())))
    c.shot(os.path.join(HERE,'_probe','os_irrig_filtro.png'))
    # ---------- CA-01 (Ordens de campo) ----------
    c.goto(f'http://127.0.0.1:{p}/CA-01.dc.html',wait=1.0)
    hr=J("""(()=>{const f=(id,t)=>{ const r=[...document.querySelectorAll('[role=row]')].find(r=>r.innerText.trim().startsWith(id)); const a=r&&[...r.querySelectorAll('a')].find(a=>a.innerText.trim().startsWith(t)); return a?a.getAttribute('href'):''; };
      return [f('OS-0422','Definir janela'),f('OS-0423','Resolver conflito')];})()""")
    b=J("document.body.innerText")
    chk('15 CA-01: Definir janela e Resolver conflito levam à IR-02; sem política nem fora da política', hr==['IR-02.dc.html','IR-02.dc.html'] and 'olítica' not in b and not PROIB.search(b) and (J("window.__err||''") or '')=='', (hr,PROIB.findall(b)[:3]))
finally:
    c.close(); srv.terminate()
print(f'\nRESULTADO: {len(OK)} ok · {len(FAIL)} falhas'); [print('  -',f) for f in FAIL]
