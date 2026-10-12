# -*- coding: utf-8 -*-
"""Teste CDP · CTL-4, revisão do 853a6a8 (lente estado): o que acontece no Estoque, na O.S. e no app muda a demanda única como o fato físico pede.
Cada caso repete pela tela a reprodução da revisão (ACHADOS-v1) e falha no 853a6a8.
  K1 · custódia é suprimento: entregar 8.000 kg de NPK à OS-0425 (Estoque), cancelar a OS-0425 (O.S.) e receber a devolução (Estoque) não mudam
       o NPK do Planejar safra (14.800 kg), o total nem a primária; o Mapa segue "Falta 14.800 kg" (no 853a6a8: 22.800 kg, +R$ 27.200)
  K2 · devolver a sobra (500 kg de MAP da OS-0417, em conferência) não muda a compra nem cria "Acima da demanda" na Compra
Uso: python3 demanda_estado_nav_test.py   (depois do build e do montar_render; capturas q_ctl4e_*.png em _probe/)"""
import sys, os, time, subprocess, json
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
from cdp import Chrome
from journeys import free
from est_lib import FIND
R=os.path.join(HERE,'_render'); OUT=os.path.join(HERE,'_probe'); os.makedirs(OUT,exist_ok=True)
p=free(); srv=subprocess.Popen(['python3','-m','http.server',str(p),'--bind','127.0.0.1','--directory',R],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(0.8)
OK=[]; FAIL=[]
def chk(nome,cond,det=''):
    (OK if cond else FAIL).append(nome); print(('OK    · ' if cond else 'FALHA · ')+nome+('' if cond else f' · {str(det)[:600]}'),flush=True)
c=Chrome(port=free()); J=c.js; B=f'http://127.0.0.1:{p}/'
c.call('Page.addScriptToEvaluateOnNewDocument',{'source':"window.__err=[];addEventListener('error',e=>window.__err.push(String(e.message)));addEventListener('unhandledrejection',e=>window.__err.push(String(e.reason)));"})
ERR=[]
def col():
    try: ERR.extend(J("location.href==='about:blank'?[]:(window.__err||['sem ouvinte em '+location.pathname]).concat([...document.querySelectorAll('.sc-logic-error')].map(e=>e.innerText))") or [])
    except Exception as e: ERR.append('coleta: '+str(e))
CLK="""((t,root)=>{const r=root?document.querySelector(root):document; if(!r) return 'SEM RAIZ'; const n=s=>(s||'').replace(/\\s+/g,' ').trim(); const els=[...r.querySelectorAll('button,a')].filter(e=>e.offsetParent!==null); const e=els.find(x=>n(x.innerText)===t)||els.find(x=>n(x.innerText).startsWith(t)); if(!e) return 'NÃO ACHEI: '+t; e.click(); return 'ok';})"""
SETV="""((sel,val)=>{const i=document.querySelector(sel); if(!i) return 'sem campo '+sel; const P=i.tagName==='SELECT'?HTMLSelectElement.prototype:(i.tagName==='TEXTAREA'?HTMLTextAreaElement.prototype:HTMLInputElement.prototype); Object.getOwnPropertyDescriptor(P,'value').set.call(i,val); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true})); return 'ok';})"""
try:
    clk=lambda t,root=None,w=.45: (J(f"({CLK})({json.dumps(t)},{json.dumps(root)})"),time.sleep(w))[0]
    setv=lambda sel,v: (J(f"({SETV})({json.dumps(sel)},{json.dumps(v)})"),time.sleep(.25))[0]
    T=lambda: J("[...document.querySelectorAll('[role=status],[role=alert]')].map(x=>x.innerText).filter(Boolean).join(' | ')") or ''
    body=lambda: J("document.body.innerText") or ''
    def ir(f,w=1.4): col(); c.goto('about:blank',wait=.1); c.goto(B+f,wait=w)
    def cel(nome,coluna):   # valor de uma coluna (cabeçalho) na linha cujo Insumo é nome
        return J(f"""(()=>{{const t=[...document.querySelectorAll('[role=table]')].find(t=>t.offsetParent); if(!t) return ''; const hs=[...t.querySelectorAll('[role=columnheader]')].map(h=>h.innerText.replace(/[⇅▾▴]/g,'').replace(/\\s+/g,' ').trim().toUpperCase());
          const iI=hs.indexOf('INSUMO'), i=hs.indexOf({json.dumps(coluna.upper())}); const r=[...t.querySelectorAll('[role=row]')].find(x=>{{const cs=x.querySelectorAll('[role=cell]'); return cs[iI]&&cs[iI].innerText.replace(/\\s+/g,' ').trim()==={json.dumps(nome)};}});
          return r?[...r.querySelectorAll('[role=cell]')][i].innerText.replace(/\\s+/g,' ').trim():'(sem linha)';}})()""") or ''
    k6=lambda: J("(document.body.innerText.match(/Valor da necessidade[^\\n]+/)||[''])[0]") or ''
    prim=lambda: (J("(()=>{const b=[...document.querySelectorAll('.acoes-prim')].find(x=>x.offsetParent); return b?b.innerText.replace(/\\s+/g,' ').trim():'';})()") or '')
    foto=lambda n: c.shot(os.path.join(OUT,f'q_ctl4e_{n}.png'))
    def saf(s='S2627'): ir(f'SAF.dc.html#saf={s}&passo=demanda',w=1.7); clk('Expandir tudo',w=.6)
    def safler(nomes,s='S2627'):
        saf(s); return dict(total=k6(),prim=prim(),**{n:[cel(n,k) for k in ('Necessidade líquida','Estoque apto','Situação')] for n in nomes})
    def memo(nome):
        J(f"(()=>{{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.replace(/\\s+/g,' ').indexOf({json.dumps(nome)})>=0); if(!r) return; r.scrollIntoView({{block:'center'}}); (r.querySelector('[role=cell] b')||r.querySelector('[role=cell] span')||r).click();}})()"); time.sleep(.6)
        t=(J("(document.querySelector('aside[role=dialog]')||{innerText:''}).innerText") or '').split('\n'); fechar(); return [x.strip() for x in t if x.strip()]
    def fechar(): J("(()=>{const a=document.querySelector('aside[role=dialog]'); if(!a) return; const b=[...a.querySelectorAll('button')].find(b=>/^Fechar$|^×$/.test(b.innerText.trim())||b.getAttribute('aria-label')==='Fechar'); if(b) b.click();})()"); time.sleep(.35)
    def cmp_ler(nome):
        ir('CMP.dc.html#sol=SOL-2026-07&saf=S2627',w=1.7); clk('Expandir tudo',w=.6)
        r=J(f"(()=>{{const r=[...document.querySelectorAll('[role=row]')].find(r=>r.innerText.indexOf({json.dumps(nome)})>=0); return r?r.innerText.replace(/\\s+/g,' '):'';}})()") or ''
        k2=J("(document.body.innerText.match(/SOL-2026-07 · [^\\n]*enviada em[^\\n]*/)||[''])[0]") or ''
        return dict(row=r,k2=k2)
    SV="[...document.querySelectorAll('svg [role=button]')]"
    def tap(t): J(f"(()=>{{const e={SV}.find(x=>(x.getAttribute('aria-label')||'').startsWith('{t}:')); e&&e.dispatchEvent(new MouseEvent('click',{{bubbles:true}}));}})()"); time.sleep(.5)
    pan=lambda t: (J(f"(document.querySelector('aside[aria-label^=\"{t}\"]')||{{}}).innerText||''") or '').replace('\n',' · ')
    def mapa(tal,faz='Santa Rita'):
        J(f"sessionStorage.setItem('mapa-ctx',{json.dumps(json.dumps({'mf_faz':faz,'lay':'Insumos','tsel':[],'flt':{'Insumos':{'per':'Safra toda'}}}))})"); ir('IN-04.dc.html',w=2.0)
        tap(tal); x=pan(tal); tap(tal); return x
    def est_secao(i): ir('EST.dc.html',w=1.6); J(f"document.querySelectorAll('nav[aria-label=\"Seções do estoque\"] button')[{i-1}].click()"); time.sleep(.5)
    def est_row(*ts):
        r=J(f"(()=>{{const r=({FIND})({json.dumps(list(ts))}); if(!r) return 'sem linha'; (r.querySelector('[role=cell] span')||r).click(); return 'ok';}})()"); time.sleep(.5); return r
    def os_painel(oid):
        ir('OS.dc.html',w=1.6)
        J(f"(()=>{{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.trim().startsWith({json.dumps(oid)})); r&&r.click();}})()"); time.sleep(.6)
    def motivo(txt):
        J(f"(()=>{{const i=document.querySelector('textarea[aria-label=\"Motivo do cancelamento\"]'); if(!i) return; const P=HTMLTextAreaElement.prototype; Object.getOwnPropertyDescriptor(P,'value').set.call(i,{json.dumps(txt)}); i.dispatchEvent(new Event('input',{{bubbles:true}})); i.dispatchEvent(new Event('change',{{bubbles:true}}));}})()"); time.sleep(.3)
    painel=lambda: (J("(document.querySelector('aside[role=dialog]')||{innerText:''}).innerText") or '').replace('\n',' · ')
    c.size(1440,1000); ir('SAF.dc.html'); J("localStorage.clear(); sessionStorage.clear(); localStorage.setItem('safrion.perfilDemo','Ana')")
    # ================= K1 · custódia é suprimento: entrega, cancelamento e devolução da OS-0425 =================
    n0=safler(['NPK 20-05-20']); m0=mapa('C1')
    est_secao(2); e1=est_row('REQ-040','NPK 20-05-20'); clk('Salvar','aside[role=dialog]',w=.8); te=T()
    n1=safler(['NPK 20-05-20'])
    os_painel('OS-0425'); cc=clk('Cancelar sem execução','aside[role=dialog]'); motivo('talhão replanejado (teste CTL-4)'); cf=clk('Confirmar cancelamento','aside[role=dialog]',w=.8); tc=T()
    n2=safler(['NPK 20-05-20']); foto('k1_saf_cancelada'); m2=mapa('C1')
    est_secao(3); e3=est_row('REQ-040','NPK 20-05-20'); setv('#fx_g_dev_qtd','8000'); clk('Salvar','aside[role=dialog]',w=.8); td=T()
    n3=safler(['NPK 20-05-20'])
    chk('K1 custódia é suprimento: entregar 8.000 kg de NPK à OS-0425, cancelar a OS-0425 e receber a devolução — Planejar safra NPK "14.800 kg", o total e a primária iguais em todos os passos; Mapa C1 "Falta 14.800 kg" (no 853a6a8: 22.800 kg, +R$ 27.200)',
        e1=='ok' and 'entregues' in te and cc=='ok' and cf=='ok' and 'cancelada' in tc and e3=='ok' and 'devolvidos' in td
        and all(x['NPK 20-05-20'][0]=='14.800 kg' and x['total']==n0['total'] and x['prim']==n0['prim'] for x in (n1,n2,n3)) and 'Falta 14.800 kg' in m0 and 'Falta 14.800 kg' in m2,
        (te,tc,td,n0,n1,n2,n3,m2[:200]))
    # ================= K2 · devolver a sobra da OS-0417 (em conferência) =================
    J("localStorage.clear(); sessionStorage.clear(); localStorage.setItem('safrion.perfilDemo','Ana')")
    d0=safler(['MAP 11-52']); mm=memo('MAP 11-52')
    est_secao(3); e4=est_row('REQ-031','MAP 11-52'); setv('#fx_g_dev_qtd','500'); clk('Salvar','aside[role=dialog]',w=.8); t4=T()
    d1=safler(['MAP 11-52']); cm=cmp_ler('MAP 11-52'); foto('k2_cmp_devolucao')
    chk('K2 devolver a sobra não muda a compra: os 500 kg de MAP com a OS-0417 (em conferência) já contam ("+ 500 kg em custódia sem uso" na memória) — MAP "79.500 kg" antes e depois, total igual, sem "Acima da demanda" no Planejar safra nem na Compra (no 853a6a8: 80.000 → 79.500 e aviso de 500 kg)',
        e4=='ok' and 'devolvidos' in t4 and d0['MAP 11-52'][0]=='79.500 kg' and d1==d0 and any('500 kg em custódia sem uso' in x for x in mm)
        and 'Acima' not in d1['MAP 11-52'][2] and 'acima da demanda' not in cm['k2'] and 'Acima da demanda' not in cm['row'],(t4,d0,d1,mm[:8],cm))
    col(); chk('E1 sem erro JS nas telas abertas (Planejar safra, Estoque, O.S., Compra, Mapa)',ERR==[],ERR[:5])
finally:
    c.close(); srv.terminate()
print(f'\nRESULTADO: {len(OK)} ok · {len(FAIL)} falhas'); [print('  -',f) for f in FAIL]
sys.exit(1 if FAIL else 0)
