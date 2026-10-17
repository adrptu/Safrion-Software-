# -*- coding: utf-8 -*-
"""Teste CDP · CTL-4, revisão do 853a6a8 (lente estado): o que acontece no Estoque, na O.S. e no app muda a demanda única como o fato físico pede.
Cada caso repete pela tela a reprodução da revisão (ACHADOS-v1) e falha no 853a6a8.
  K1 · custódia é suprimento: entregar 8.000 kg de NPK à OS-0425 (Estoque), cancelar a OS-0425 (O.S.) e receber a devolução (Estoque) não mudam
       o NPK do Planejar safra (14.800 kg), o total nem a primária; o Mapa segue "Falta 14.800 kg" (no 853a6a8: 22.800 kg, +R$ 27.200)
  K2 · devolver a sobra (500 kg de MAP da OS-0417, em conferência) não muda a compra nem cria "Acima da demanda" na Compra
  K3 · cancelar com material entregue não diz "nada tinha sido entregue": o aviso, a confirmação e o painel da O.S. cancelada mostram a custódia com
       quem recebeu e o próximo passo "Receber devolução" (Estoque); depois da devolução o aviso some
  Q1 · NF 4533 (PC-090) conferida inteira em quarentena: a Semente de soja 58 W fica "Qualidade pendente · 15.456 kg" no Planejar safra e na Compra,
       com a decisão à vista, sem entrar no total a comprar nem trocar a primária (no 853a6a8: 15.456 kg Complemento, +R$ 146.832, "Enviar para cotação")
  Q2 · laudo reprovado no Estoque ("Reprovar com o laudo", com o motivo): aí sim vira falta firme, com o motivo na memória
  Q3 · laudo liberado: coberto, sem qualidade pendente
  A7 · turno fechado no app sem sinal (50 ha, 25 L na OS-0421) não muda a compra até o envio: a demanda usa a custódia que a O.S. mostra (65 L)
  R1 · entregar 64 L à OS-0424 (a REQ-039 reservou 65 L) não muda a Safrinha: a reserva que sobra não é demanda de ninguém
  F1 · liberar a OS-0501 (Lagoa Grande) com lotes da Santa Rita conta a reserva uma vez em cada fazenda e a entrega não muda nenhuma das duas
  D3 · SU-03det e MB-05 leem a mesma demanda viva do Planejar safra: devolução bloqueada (qualidade pendente) e laudo reprovado (pendência de compra,
       conflito e "Registrar divergência") aparecem nas três telas com o mesmo número; nunca "sem pendência de compra" com a demanda pedindo complemento
Uso: python3 demanda_estado_nav_test.py   (depois do build e do montar_render; capturas q_ctl4e_*.png em _probe/)"""
import sys, os, time, subprocess, json
HERE=os.environ.get('GEN') or os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
from cdp import Chrome
from journeys import free
from est_lib import FIND
R=os.path.join(HERE,'_render'); OUT=os.path.join(HERE,'_probe'); os.makedirs(OUT,exist_ok=True)
p=free(); srv=subprocess.Popen(['python3','-m','http.server',str(p),'--bind','127.0.0.1','--directory',R],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(0.8)
OK=[]; FAIL=[]
def chk(nome,cond,det=''):
    (OK if cond else FAIL).append(nome); print(('OK    · ' if cond else 'FALHA · ')+nome+('' if cond else f' · {str(det)[:2500]}'),flush=True)
c=Chrome(port=free()); J=c.js; B=f'http://127.0.0.1:{p}/'
c.call('Page.addScriptToEvaluateOnNewDocument',{'source':'window.__g2cvTodasSempre=true'})   # V2-3: teste de domínio lê colunas fora do "Abre com"
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
    def cmp_ler(nome,memo_=False):
        ir('CMP.dc.html#sol=SOL-2026-07&saf=S2627',w=1.7); clk('Expandir tudo',w=.6)
        r=J(f"(()=>{{const r=[...document.querySelectorAll('[role=row]')].find(r=>r.innerText.indexOf({json.dumps(nome)})>=0); return r?r.innerText.replace(/\\s+/g,' '):'';}})()") or ''
        k2=J("(document.body.innerText.match(/SOL-2026-07 · [^\\n]*enviada em[^\\n]*/)||[''])[0]") or ''
        # Integração V56 × CTL-4: as colunas da linha (a mesma conta viva do Planejar safra) e, se pedida, a memória
        cl=J(f"""(()=>{{const n=s=>(s||'').replace(/\\s+/g,' ').trim(); const t=[...document.querySelectorAll('[role=table]')].find(t=>t.offsetParent); if(!t) return {{}};
              const hs=[...t.querySelectorAll('[role=columnheader]')].map(h=>n(h.innerText.replace(/[⇅▾▴▼▲]/g,'')).replace(/ · \\d+$/,'').toUpperCase()); const r=[...t.querySelectorAll('[role=row]')].find(x=>{{const c=x.querySelector('[role=cell]'); return c&&n(c.innerText)==={json.dumps(nome)};}});
          if(!r) return {{}}; const cs=[...r.querySelectorAll('[role=cell]')]; const o={{}}; ['ESTOQUE APTO','A RECEBER','NECESSIDADE','NA COMPRA'].forEach(k=>{{const i=hs.indexOf(k); o[k]=i>=0&&cs[i]?n(cs[i].innerText):'';}}); return o;}})()""") or {}
        return dict(row=r,k2=k2,cl=cl,memo=(memo(nome) if memo_ else []))
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
    def os_cancelada(oid):   # O.S. cancelada fica fora do quadro: o chip "Canceladas" mostra a linha
        ir('OS.dc.html',w=1.6); clk('Canceladas',w=.6)
        J(f"(()=>{{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.trim().startsWith({json.dumps(oid)})); r&&r.click();}})()"); time.sleep(.6)
    def motivo(txt):
        J(f"(()=>{{const i=document.querySelector('textarea[aria-label=\"Motivo do cancelamento\"]'); if(!i) return; const P=HTMLTextAreaElement.prototype; Object.getOwnPropertyDescriptor(P,'value').set.call(i,{json.dumps(txt)}); i.dispatchEvent(new Event('input',{{bubbles:true}})); i.dispatchEvent(new Event('change',{{bubbles:true}}));}})()"); time.sleep(.3)
    painel=lambda: (J("(document.querySelector('aside[role=dialog]')||{innerText:''}).innerText") or '').replace('\n',' · ')
    sem_est=lambda x: {k:([v[0],v[2]] if isinstance(v,list) else v) for k,v in x.items()}   # a entrega muda o estoque apto do almoxarifado, não a compra
    c.size(1440,1000); ir('SAF.dc.html'); J("localStorage.clear(); sessionStorage.clear(); localStorage.setItem('safrion.perfilDemo','Ana')")
    # ================= K1 · custódia é suprimento: entrega, cancelamento e devolução da OS-0425 =================
    n0=safler(['NPK 20-05-20']); m0=mapa('C1')
    est_secao(2); e1=est_row('REQ-040','NPK 20-05-20'); clk('Salvar','aside[role=dialog]',w=.8); te=T()
    n1=safler(['NPK 20-05-20'])
    os_painel('OS-0425'); cc=clk('Cancelar sem execução','aside[role=dialog]'); cct=painel(); motivo('talhão replanejado (teste CTL-4)'); cf=clk('Confirmar cancelamento','aside[role=dialog]',w=.8); tc=T()
    n2=safler(['NPK 20-05-20']); foto('k1_saf_cancelada'); m2=mapa('C1')
    os_cancelada('OS-0425'); pc=painel(); lk=J("[...document.querySelectorAll('aside[role=dialog] a')].map(a=>a.innerText.trim()+'>'+a.getAttribute('href')).join(' | ')") or ''; foto('k3_os_cancelada_custodia')
    est_secao(3); e3=est_row('REQ-040','NPK 20-05-20'); setv('#fx_g_dev_qtd','8000'); setv('#fx_g_dev_cond','Apta · volta ao disponível'); clk('Salvar','aside[role=dialog]',w=.8); td=T()
    n3=safler(['NPK 20-05-20']); os_cancelada('OS-0425'); pc2=painel()
    chk('K1 custódia é suprimento: entregar 8.000 kg de NPK à OS-0425, cancelar a OS-0425 e receber a devolução — Planejar safra NPK "14.800 kg", o total e a primária iguais em todos os passos; Mapa C1 "Falta 14.800 kg" (no 853a6a8: 22.800 kg, +R$ 27.200)',
        e1=='ok' and 'entregues' in te and cc=='ok' and cf=='ok' and 'cancelada' in tc and e3=='ok' and 'devolvidos' in td
        and all(x['NPK 20-05-20'][0]=='14.800 kg' and x['total']==n0['total'] and x['prim']==n0['prim'] for x in (n1,n2,n3)) and 'Falta 14.800 kg' in m0 and 'Falta 14.800 kg' in m2,
        (te,tc,td,n0,n1,n2,n3,m2[:200]))
    chk('K3 cancelar com material entregue (achado 7): a confirmação diz que os 8.000 kg ficam em custódia, o aviso não diz "nada tinha sido entregue", e o painel da OS-0425 cancelada mostra "Custódia a devolver: 8.000 kg de NPK 20-05-20" com o link "Receber devolução" (Estoque); depois da devolução o aviso some',
        'em custódia' in cct and 'nada foi entregue' not in cct and 'nada tinha sido entregue' not in tc and 'em custódia com' in tc and 'Custódia a devolver: 8.000 kg de NPK 20-05-20' in pc
        and 'Receber devolução' in lk and '>EST.dc.html' in lk and 'Custódia a devolver' not in pc2,
        dict(cct='em custódia' in cct and 'nada foi entregue' not in cct,tc='nada tinha sido entregue' not in tc and 'em custódia com' in tc,pc='Custódia a devolver: 8.000 kg de NPK 20-05-20' in pc,lk=lk,pc2='Custódia a devolver' not in pc2,toast=tc[-300:]))
    # ================= K2 · devolver a sobra da OS-0417 (em conferência) =================
    J("localStorage.clear(); sessionStorage.clear(); localStorage.setItem('safrion.perfilDemo','Ana')")
    d0=safler(['MAP 11-52']); mm=memo('MAP 11-52')
    est_secao(3); e4=est_row('REQ-031','MAP 11-52'); setv('#fx_g_dev_qtd','500'); setv('#fx_g_dev_cond','Apta · volta ao disponível'); clk('Salvar','aside[role=dialog]',w=.8); t4=T()
    d1=safler(['MAP 11-52']); cm=cmp_ler('MAP 11-52',True); foto('k2_cmp_devolucao')
    chk('K2 devolver a sobra não muda a compra: os 500 kg de MAP com a OS-0417 (em conferência) já contam ("+ 500 kg em custódia sem uso" na memória) — MAP "79.500 kg" antes e depois, total igual, sem "Acima da demanda" no Planejar safra nem na Compra (no 853a6a8: 80.000 → 79.500 e aviso de 500 kg)',
        e4=='ok' and 'devolvidos' in t4 and d0['MAP 11-52'][0]=='79.500 kg' and d1['MAP 11-52'][0]=='79.500 kg' and d1['total']==d0['total'] and d1['prim']==d0['prim']
        and d0['MAP 11-52'][1]=='90.000 kg' and d1['MAP 11-52'][1]=='90.500 kg' and any('500 kg em custódia sem uso' in x for x in mm)
        and 'Acima' not in d1['MAP 11-52'][2] and 'acima da demanda' not in cm['k2'] and 'Acima da demanda' not in cm['row'],(t4,d0,d1,mm[:8],cm))
    chk('K2b a Compra lê a mesma conta viva (integração V56 × CTL-4): depois da devolução, "Estoque apto" 90.500 e "Necessidade" 79.500 na SOL-2026-07, e a memória sem a custódia (antes: 90.000 e "+ 500 kg em custódia" da foto da versão)',
        cm['cl'].get('ESTOQUE APTO')=='90.500' and cm['cl'].get('NECESSIDADE')=='79.500' and any(x.startswith('Estoque apto hoje: 90.500 kg') for x in cm['memo'])
        and not any('custódia sem uso' in x for x in cm['memo']),(cm['cl'],cm['memo'][:6]))
    # ================= Q1–Q3 · NF 4533 em quarentena: falta condicionada à qualidade (PRD 65.4; CAL-01 "Qualidade pendente"; DEMO-02) =================
    SEM='Semente de soja 58 W'
    def nf4533():
        est_secao(1); a=clk('Conferir NF 4533',w=.6)
        for k,v in (('#fx_g_rec_conf','20000'),('#fx_g_rec_apto','0'),('#fx_g_rec_quar','20000'),('#fx_g_rec_val','06/2027'),('#fx_g_rec_obs','Aguarda laudo de germinação (teste CTL-4)')): setv(k,v)
        clk('Salvar','aside[role=dialog]',w=.9); return a,T()
    def laudo(acao,num,mot=''):
        est_secao(4); J(f"(()=>{{const r=({FIND})(['S58-0926']); if(!r) return; const b=[...r.querySelectorAll('button')].find(b=>/Liberar após inspeção/.test(b.innerText)); b&&b.click();}})()"); time.sleep(.5)
        setv('#est-laudo',num); setv('#est-laudo-mot',mot); r=clk(acao,'[role=group][aria-label="Liberar quarentena com laudo"]',w=.8); return r,T()
    J("localStorage.clear(); sessionStorage.clear(); localStorage.setItem('safrion.perfilDemo','Ana')")
    g0=safler([SEM]); qa,tq=nf4533(); g1=safler([SEM]); mq=memo(SEM); foto('q1_saf_qualidade_pendente'); cq=cmp_ler(SEM,True); foto('q1_cmp_qualidade_pendente'); mpq=mapa('T4')
    chk('Q1 NF 4533 inteira em quarentena (achado 2, S2): Planejar safra Semente de soja 58 W "0 kg" com "Qualidade pendente · 15.456 kg", total e primária iguais; a memória diz a falta condicionada e a decisão; a Compra mostra a mesma qualidade pendente sem compra (no 853a6a8: 15.456 kg · Complemento · +R$ 146.832 · "Enviar para cotação")',
        qa=='ok' and 'quarentena' in tq and g1[SEM][0]=='0 kg' and 'Qualidade pendente · 15.456 kg' in g1[SEM][2] and g1['total'].startswith(g0['total']) and g1['prim']==g0['prim']=='Abrir Compra de insumos ›'
        and '1 insumo com qualidade pendente' in g1['total'] and any(x.startswith('Falta condicionada à qualidade: 15.456 kg') for x in mq)
        and 'Qualidade pendente · 15.456 kg' in cq['row'] and 'qualidade pendente: Semente de soja 58 W 15.456 kg' in cq['k2'],(tq,g0,g1,[x for x in mq if 'condicionada' in x or 'quarentena' in x][:3],cq))
    MRP=('motivo: 20.000 kg em quarentena aguardam laudo (lote S58-0926 · NF 4533: Aguarda laudo de germinação (teste CTL-4))','responsável: o gestor libera ou reprova com o laudo no Estoque','prazo: decidir antes de 15/10/2026')
    fc=next((x for x in mq if x.startswith('Falta condicionada à qualidade: 15.456 kg')),'')
    chk('Q1b aceite CTL-4-FIX item 2 (integração V56): a NF em quarentena sai do "A receber" da Compra (0) e a linha não diz "Coberto"; a falta condicionada traz motivo (o da conferência), responsável, prazo e decisão no Planejar safra, na Compra e no Mapa',
        cq['cl'].get('A RECEBER')=='0' and cq['cl'].get('ESTOQUE APTO')=='12.000' and 'Coberto' not in cq['cl'].get('NA COMPRA','') and 'Qualidade pendente · 15.456 kg' in cq['cl'].get('NA COMPRA','')
        and all(t in fc for t in MRP) and all(t in cq['cl'].get('NA COMPRA','') for t in MRP) and all(t in mpq for t in MRP) and 'Qualidade pendente · 15.456 kg' in mpq
        and any(x.startswith('Sem falta nesta safra se o laudo liberar os 20.000 kg') for x in mq),(cq['cl'],fc,[t in mpq for t in MRP],[x for x in mq if x.startswith('Sem falta')]))
    rr,tr=laudo('Reprovar com o laudo','LAB-2','germinação 71%'); g2=safler([SEM]); mr=memo(SEM); foto('q2_saf_reprovado'); cr=cmp_ler(SEM)
    chk('Q2 laudo reprovado com o motivo: aí sim a Semente de soja 58 W vira falta firme de 15.456 kg ("Complemento") e a primária pede o envio; a memória diz "Reprovado: 20.000 kg do lote S58-0926 … laudo LAB-2: germinação 71%"',
        rr=='ok' and 'reprovados com o laudo LAB-2' in tr and g2[SEM][0]=='15.456 kg' and 'Complemento' in g2[SEM][2] and g2['prim']=='Enviar para cotação'
        and any(x.startswith('Reprovado: 20.000 kg do lote S58-0926') and 'germinação 71%' in x for x in mr),(tr,g2,[x for x in mr if 'Reprov' in x]))
    chk('Q2b com o laudo reprovado a Compra mostra a mesma necessidade (15.456) e "Complemento · 15.456 kg", com quem envia (o Planejar safra), em vez de "—" calado',
        cr['cl'].get('NECESSIDADE')=='15.456' and 'Complemento · 15.456 kg' in cr['cl'].get('NA COMPRA','') and 'o Planejar safra envia o complemento da SOL-2026-07' in cr['cl'].get('NA COMPRA',''),cr['cl'])
    J("localStorage.clear(); sessionStorage.clear(); localStorage.setItem('safrion.perfilDemo','Ana')")
    nf4533(); rl,tl=laudo('Liberar com o laudo','LAB-1'); g3=safler([SEM])
    chk('Q3 laudo liberado: coberto pelo estoque (32.000 kg aptos), sem qualidade pendente e com o total da semente',
        rl=='ok' and 'liberados com o laudo LAB-1' in tl and g3[SEM][0]=='0 kg' and g3[SEM][1]=='32.000 kg' and 'Coberto' in g3[SEM][2] and g3['total']==g0['total'],(tl,g3))
    # ================= A7 · turno do app sem sinal =================
    J("localStorage.clear(); sessionStorage.clear(); localStorage.setItem('safrion.perfilDemo','Ana')")
    f0=safler(['Fungicida A'],'S27SF'); h0=safler(['Fungicida A'])
    ir('OS.dc.html',w=1.6); ra=J("(()=>{ const X=window.__cen; const r=X.cenMudar(null,c=>{ X.cenSinal(c,false); X.cenIniciarTurno(c,'OS-0421'); return X.cenFecharTurno(c,50,4,{'Fungicida A':25,'Adjuvante espalhante':0},'',[]); }); return r.erro||r.msg; })()") or ''
    f1=safler(['Fungicida A'],'S27SF'); foto('a7_saf_semsinal'); h1=safler(['Fungicida A']); mfa=memo('Fungicida A')
    ir('OS.dc.html',w=1.6); rs=J("(()=>{ const X=window.__cen; const r=X.cenMudar(null,c=>X.cenSinal(c,true)); return r.erro||r.msg; })()") or ''; f2=safler(['Fungicida A'],'S27SF')
    chk('A7 turno fechado no app sem sinal (achado 4, S3): Safrinha 2027 e Safra 2026/27 com o mesmo Fungicida A, total e primária antes e depois; a memória da OS-0421 usa os 65 L em custódia que a O.S. mostra; com o sinal, a Safrinha segue igual (no 853a6a8: 23,0 → 47,5 L e a Safra 2026/27 pedia 0,5 L)',
        'aparelho' in ra and f1==f0 and h1==h0 and any('OS-0421' in x and '− 65 L em custódia' in x for x in mfa) and 'enviado' in rs and f2['Fungicida A'][0]==f0['Fungicida A'][0],(ra,f0,f1,h0,h1,[x for x in mfa if 'OS-0421' in x][:2],rs,f2))
    # ================= R1 · reserva que sobra (REQ-039 reservou 65 L; a OS-0424 precisa de 64) =================
    J("localStorage.clear(); sessionStorage.clear(); localStorage.setItem('safrion.perfilDemo','Ana')")
    r0=safler(['Fungicida A'],'S27SF'); est_secao(2); er=est_row('REQ-039','Fungicida A'); setv('#fx_g_ent_qtd','64'); clk('Salvar','aside[role=dialog]',w=.8); tr1=T(); r1=safler(['Fungicida A'],'S27SF')
    chk('R1 reserva que sobra (achado 5, S3): entregar 64 L à OS-0424 (REQ-039 reservou 65 L) não muda a Safrinha 2027 — Fungicida A, total e primária iguais (no 853a6a8: 22,98 → 23,98 L, +R$ 145)',
        er=='ok' and '64 L de Fungicida A entregues' in tr1 and sem_est(r1)==sem_est(r0),(tr1,r0,r1))
    # ================= F1 · reserva entre fazendas: OS-0501 (Lagoa Grande) liberada com lotes da Santa Rita =================
    J("localStorage.clear(); sessionStorage.clear(); localStorage.setItem('safrion.perfilDemo','Ana')")
    GL=['Glifosato 480','Óleo mineral']; num=lambda t: float(t.split(' ')[0].replace('.','').replace(',','.')) if t and t[0].isdigit() else 0.0
    a0=safler(GL); b0=safler(GL,'LG2627')
    ir('OS.dc.html',w=1.6); rl5=J("(()=>{ const X=window.__cen; const r=X.cenMudar(null,c=>X.osc_liberar(c,'OS-0501',false,null,{k:'Ana'})); return r.erro||r.msg; })()") or ''
    a1=safler(GL); b1=safler(GL,'LG2627'); foto('f1_saf_lg_liberada')
    est_secao(2); est_row('OS-0501','Glifosato 480'); clk('Salvar','aside[role=dialog]',w=.8); tg=T(); est_row('OS-0501','Óleo mineral'); clk('Salvar','aside[role=dialog]',w=.8); to=T()
    a2=safler(GL); b2=safler(GL,'LG2627')
    soma=lambda a,b,n: round(num(a[n][0])+num(b[n][0]),1)
    chk('F1 reserva entre fazendas (achado 3, S3): liberar a OS-0501 (Lagoa Grande) com lotes do Almox. defensivos da Santa Rita move a compra entre as fazendas sem contar duas vezes (Glifosato SR 20,0 → 167,9 L e LG 293,3 → 145,4 L; a soma não muda) e entregar não muda nenhuma das duas (no 853a6a8: LG não mudava na liberação e baixava na entrega)',
        'liberada' in rl5 and 'entregues' in tg and 'entregues' in to and a1['Glifosato 480'][0]=='167,9 L' and b1['Glifosato 480'][0]=='145,4 L'
        and all(abs(soma(a1,b1,n)-soma(a0,b0,n))<=0.15 for n in GL) and sem_est(a2)==sem_est(a1) and sem_est(b2)==sem_est(b1),(rl5,tg,to,a0,b0,a1,b1,a2,b2))   # a tela arredonda a 0,1 L cada fazenda
    # ================= D3 · SU-03det e MB-05 da mesma fonte =================
    J("localStorage.clear(); sessionStorage.clear(); localStorage.setItem('safrion.perfilDemo','Ana')")
    def su03det(): ir('SU-03det.dc.html',w=1.6); return (J("document.body.innerText") or '').replace('\n',' · ')
    def mb05(): ir('MB-05.dc.html',w=1.6); clk('Almoxarife',w=.6); return (J("document.body.innerText") or '').replace('\n',' · ')
    su0=su03det(); mb0=mb05()
    est_secao(3); ed=est_row('REQ-035','Fungicida A'); setv('#fx_g_dev_qtd','30'); setv('#fx_g_dev_cond','Bloqueada para inspeção · vai para quarentena'); setv('#fx_g_dev_obs','Galão sem lacre (teste CTL-4)'); clk('Salvar','aside[role=dialog]',w=.8); tdv=T()
    s1=safler(['Fungicida A']); su1=su03det(); foto('d3_su03det_qualidade'); mb1=mb05(); foto('d3_mb05_qualidade')
    import re as _re
    cq=(_re.search(r'Qualidade pendente · ([\d.,]+ L)',s1['Fungicida A'][2]) or [None,''])[1]
    est_secao(4); J(f"(()=>{{const r=({FIND})(['F26-02']); if(!r) return; const b=[...r.querySelectorAll('button')].find(b=>/Liberar após inspeção/.test(b.innerText)); b&&b.click();}})()"); time.sleep(.5)
    setv('#est-laudo','LAB-9'); setv('#est-laudo-mot','lacre violado'); rr3=clk('Reprovar com o laudo','[role=group][aria-label="Liberar quarentena com laudo"]',w=.8); trp=T()
    s2=safler(['Fungicida A']); su2=su03det(); foto('d3_su03det_pendencia'); mb2=mb05(); foto('d3_mb05_conflito')
    lq=s2['Fungicida A'][0]
    chk('D3 SU-03det e MB-05 da mesma fonte (achado 6, S3): na semente "Sem pendência de compra" nas duas; com a devolução bloqueada as duas mostram "Qualidade pendente · '+(cq or '?')+'" como o Planejar safra; com o laudo reprovado, "Pendência de compra · '+lq+'" no SU-03det e "Conflito de reserva" com "Registrar divergência" no MB-05, o mesmo número do Planejar safra (no 853a6a8: "sem pendência de compra" fixo da semente)',
        'Sem pendência de compra' in su0 and 'Sem pendência de compra' in mb0 and 'devolvidos e bloqueados' in tdv and cq and 'Qualidade pendente · '+cq in su1 and 'Qualidade pendente · '+cq in mb1
        and 'Sem pendência de compra' not in su1 and rr3=='ok' and 'reprovados' in trp and 'Complemento' in s2['Fungicida A'][2] and lq!='0,0 L' and 'Pendência de compra · '+lq in su2
        and 'Sem pendência de compra' not in su2 and 'Conflito de reserva' in mb2 and 'Registrar divergência' in mb2 and 'pendência de compra de '+lq in mb2,
        dict(ok=['Qualidade pendente · '+cq in su1,'Qualidade pendente · '+cq in mb1,'Sem pendência de compra' not in su1,'Pendência de compra · '+lq in su2,'Sem pendência de compra' not in su2,'Conflito de reserva' in mb2,'Registrar divergência' in mb2,'pendência de compra de '+lq in mb2,rr3],
             su0='Sem pendência de compra' in su0,mb0='Sem pendência de compra' in mb0,tdv=tdv,s1=s1,su1=[x for x in su1.split(' · ') if 'pend' in x.lower()][:4],mb1=[x for x in mb1.split(' · ') if 'pend' in x.lower()][:4],
             trp=trp,s2=s2,su2=[x for x in su2.split(' · ') if 'pend' in x.lower()][:4],mb2=[x for x in mb2.split(' · ') if 'onflito' in x or 'pend' in x.lower()][:5]))
    col(); chk('E1 sem erro JS nas telas abertas (Planejar safra, Estoque, O.S., Compra, Mapa)',ERR==[],ERR[:5])
finally:
    c.close(); srv.terminate()
print(f'\nRESULTADO: {len(OK)} ok · {len(FAIL)} falhas'); [print('  -',f) for f in FAIL]
sys.exit(1 if FAIL else 0)

